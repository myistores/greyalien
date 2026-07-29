from __future__ import annotations
import hashlib, json, re, unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_KEYS={"utm_source","utm_medium","utm_campaign","utm_term","utm_content","fbclid","gclid","mc_cid","mc_eid","si","feature"}

def now_iso(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def read_json(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def write_json(path,obj):
 p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding='utf-8')
def sha256_file(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
 return h.hexdigest()
def stable_id(prefix,*parts): return prefix+'-'+hashlib.sha256('|'.join(str(x or '') for x in parts).encode()).hexdigest()[:16]
def normalize_url(url):
 s=urlsplit((url or '').strip()); scheme=(s.scheme or 'https').lower(); host=(s.hostname or '').lower()
 port=f':{s.port}' if s.port and not ((scheme=='http' and s.port==80) or (scheme=='https' and s.port==443)) else ''
 path=re.sub(r'/+','/',s.path or '/'); path=path.rstrip('/') or '/'
 q=[(k,v) for k,v in parse_qsl(s.query,keep_blank_values=True) if k.lower() not in TRACKING_KEYS]
 return urlunsplit((scheme,host+port,path,urlencode(sorted(q)),''))
def canonical_key(url):
 n=normalize_url(url); s=urlsplit(n); return urlunsplit(('https',s.netloc.removeprefix('www.'),s.path,s.query,''))
def host(url): return (urlsplit(url or '').hostname or '').lower()
def norm_text(value):
 s=unicodedata.normalize('NFKD',str(value or '')).encode('ascii','ignore').decode().lower()
 s=re.sub(r'\b(official|podcast|episode|ep\.?|watch|listen|youtube|apple podcasts|spotify)\b',' ',s)
 return re.sub(r'[^a-z0-9]+',' ',s).strip()
def tokens(value): return {x for x in norm_text(value).split() if len(x)>1}
def extract_episode_number(value):
 m=re.search(r'(?:episode|ep\.?|#)\s*0*(\d{1,4})\b',str(value or ''),re.I)
 return int(m.group(1)) if m else None
