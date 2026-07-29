from __future__ import annotations
import random, socket, ssl, time
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from threading import BoundedSemaphore
import requests
from requests import Response
from requests.exceptions import ConnectionError,ConnectTimeout,ReadTimeout,SSLError
from .common import now_iso,host

YT_GATE=BoundedSemaphore(2)
@dataclass
class FetchConfig:
 timeout_connect: float=15; timeout_read: float=30; max_retries: int=3; base_backoff: float=3; max_backoff: float=60; jitter: float=1.5; user_agent: str='GreyAlien-MediaAudit/23.5C.2A (+https://greyalien.com)'

def _retry_after(value):
 if not value:return None
 try:return max(0,float(value))
 except ValueError:
  try:return max(0,(parsedate_to_datetime(value)-parsedate_to_datetime(now_iso())).total_seconds())
  except Exception:return None

def classify_transport(exc):
 text=str(exc).lower()
 if isinstance(exc,SSLError) or 'ssl' in text or 'tls' in text:return 'tls_negotiation_failure'
 if isinstance(exc,(ConnectTimeout,ReadTimeout)) or 'timed out' in text:return 'connection_timeout'
 if 'name or service not known' in text or 'temporary failure in name resolution' in text or 'nodename nor servname' in text:return 'dns_resolution_failure'
 if 'connection refused' in text:return 'connection_refused'
 if 'no route to host' in text or 'network is unreachable' in text:return 'unreachable_host'
 return 'temporary_routing_failure'

def fetch(url,config=None,session=None):
 config=config or FetchConfig(); session=session or requests.Session(); attempts=[]; gate=YT_GATE if host(url) in {'youtube.com','www.youtube.com','youtu.be','m.youtube.com'} else None
 if gate: gate.acquire()
 try:
  for attempt in range(1,config.max_retries+1):
   started=now_iso()
   try:
    r=session.get(url,headers={'User-Agent':config.user_agent,'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'},timeout=(config.timeout_connect,config.timeout_read),allow_redirects=True)
    attempts.append({'attempt':attempt,'startedAt':started,'completedAt':now_iso(),'httpStatus':r.status_code,'url':r.url,'retryAfter':r.headers.get('Retry-After')})
    if r.status_code!=429: return r,attempts,None
    if attempt==config.max_retries:return r,attempts,'rate_limit_exhausted'
    delay=_retry_after(r.headers.get('Retry-After')) or min(config.max_backoff,config.base_backoff*(2**(attempt-1))+random.uniform(0,config.jitter))
    attempts[-1]['waitSeconds']=round(delay,3); time.sleep(delay)
   except (ConnectionError,ConnectTimeout,ReadTimeout,SSLError,socket.gaierror,ssl.SSLError) as exc:
    reason=classify_transport(exc); attempts.append({'attempt':attempt,'startedAt':started,'completedAt':now_iso(),'transportFailure':reason,'detail':str(exc)[:500]})
    return None,attempts,reason
  return None,attempts,'temporary_routing_failure'
 finally:
  if gate:gate.release()
