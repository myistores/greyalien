from __future__ import annotations
import json,re
from bs4 import BeautifulSoup
import feedparser
from .common import now_iso
from .detection import detect_platform,detect_destination_type,media_identifier
SOFT404=('page not found','404 not found','content unavailable','episode not found','this page doesn’t exist','this page does not exist')
def _meta(soup,*keys):
 for key in keys:
  node=soup.find('meta',attrs={'property':key}) or soup.find('meta',attrs={'name':key})
  if node and node.get('content'):return node['content'].strip()
 return None
def extract(response):
 ct=response.headers.get('Content-Type',''); raw=response.content[:1500000]; final=response.url
 if 'xml' in ct.lower() or raw.lstrip().startswith(b'<?xml') or raw.lstrip().startswith(b'<rss'):
  feed=feedparser.parse(raw); title=feed.feed.get('title'); return {'pageTitle':title,'htmlTitle':title,'canonicalUrl':final,'ogTitle':None,'ogUrl':None,'ogType':'rss','description':feed.feed.get('subtitle'),'platform':'RSS','mediaIdentifier':None,'publisherName':feed.feed.get('author'),'podcastName':title,'episodeTitle':None,'episodeNumber':None,'publicationDate':None,'duration':None,'availability':'available' if not feed.bozo else 'parse_warning','contentType':ct,'retrievedAt':now_iso(),'rssEntryCount':len(feed.entries),'rssBozo':bool(feed.bozo),'soft404':False}
 text=raw.decode(response.encoding or 'utf-8',errors='replace'); soup=BeautifulSoup(text,'html.parser'); title=soup.title.get_text(' ',strip=True) if soup.title else None
 canonical=(soup.find('link',rel=lambda x:x and 'canonical' in x) or {}).get('href') if soup else None
 ld=[]
 for node in soup.find_all('script',type='application/ld+json'):
  try: ld.append(json.loads(node.string or 'null'))
  except Exception: pass
 flat=json.dumps(ld,ensure_ascii=False); epno=None
 m=re.search(r'"episodeNumber"\s*:\s*"?(\d+)',flat); epno=int(m.group(1)) if m else None
 desc=_meta(soup,'description','og:description'); ogt=_meta(soup,'og:title'); platform=detect_platform(final,ct)
 evidence={'pageTitle':title,'htmlTitle':title,'canonicalUrl':canonical,'ogTitle':ogt,'ogUrl':_meta(soup,'og:url'),'ogType':_meta(soup,'og:type'),'description':desc,'platform':platform,'mediaIdentifier':media_identifier(final,platform),'publisherName':_meta(soup,'author','article:author'),'podcastName':_meta(soup,'music:musician') or _meta(soup,'og:site_name'),'episodeTitle':ogt or title,'episodeNumber':epno,'publicationDate':_meta(soup,'article:published_time','date','datePublished'),'duration':_meta(soup,'video:duration','music:duration'),'availability':'available','contentType':ct,'retrievedAt':now_iso(),'soft404':response.status_code==200 and any(x in ((title or '')+' '+(desc or '')).lower() for x in SOFT404)}
 evidence['destinationType']=detect_destination_type(final,platform,evidence); return evidence
