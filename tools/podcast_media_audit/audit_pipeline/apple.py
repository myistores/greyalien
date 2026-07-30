from __future__ import annotations
import json,re
from dataclasses import dataclass
from urllib.parse import parse_qs,urlsplit,urlunsplit,urlencode
from .common import norm_text

APPLE_BRAND_NAMES={'apple','apple podcasts','podcasts on apple podcasts'}

def extract_apple_ids(url):
 s=urlsplit(url or ''); q=parse_qs(s.query); episode=(q.get('i') or [None])[0]
 m=re.search(r'/id(\d+)(?:$|[/?])',s.path); show=m.group(1) if m else None
 return {'showId':str(show) if show else None,'episodeId':str(episode) if episode else None}

def normalize_apple_url(url,preserve_episode_id=True,episode_id=None):
 s=urlsplit(url or ''); q=parse_qs(s.query,keep_blank_values=True)
 keep={k:v for k,v in q.items() if k.lower() not in {'utm_source','utm_medium','utm_campaign','utm_term','utm_content','fbclid','gclid','itsct','itscg'}}
 if preserve_episode_id and episode_id and not keep.get('i'): keep['i']=[str(episode_id)]
 query=urlencode(sorted((k,x) for k,vals in keep.items() for x in vals))
 path=re.sub(r'/+','/',s.path or '/').rstrip('/') or '/'
 return urlunsplit(((s.scheme or 'https').lower(),(s.hostname or '').lower(),path,query,''))

def _clean_title(v):
 if not v:return None
 v=re.sub(r'\s*[-|–—]\s*Apple Podcasts\s*$','',str(v),flags=re.I).strip()
 return v or None

def _walk(obj):
 if isinstance(obj,dict):
  yield obj
  for v in obj.values():yield from _walk(v)
 elif isinstance(obj,list):
  for v in obj:yield from _walk(v)

def _json_scripts(soup):
 for node in soup.find_all('script'):
  typ=(node.get('type') or '').lower(); ident=node.get('id') or ''
  if 'json' not in typ and ident not in {'shoebox-ember-data-store','__NEXT_DATA__'}:continue
  raw=node.string or node.get_text() or ''
  try:yield json.loads(raw)
  except Exception:continue

def _set(out,field,value,source,confidence):
 if value in (None,'',[]):return
 if field in {'showTitle','episodeTitle'}: value=_clean_title(value)
 if not value:return
 cur=out.get(field)
 if not cur or confidence>cur['confidence']:out[field]={'value':str(value) if field in {'showId','episodeId'} else value,'source':source,'confidence':confidence}

def extract_apple_metadata(soup,original_url,final_url,canonical_url=None):
 out={}; diagnostics=[]
 urls=[original_url,final_url,canonical_url]
 ids=[extract_apple_ids(u) for u in urls if u]
 for item,src in zip(ids,['original_url','final_url','canonical_url']):
  _set(out,'showId',item.get('showId'),src,98); _set(out,'episodeId',item.get('episodeId'),src,100)
 for document in _json_scripts(soup):
  for node in _walk(document):
   typ=str(node.get('@type') or node.get('type') or '').lower()
   name=node.get('name') or node.get('title')
   collection=node.get('partOfSeries') or node.get('partOfPodcastSeries') or node.get('collectionName') or node.get('podcastName')
   if isinstance(collection,dict):collection=collection.get('name') or collection.get('title')
   if collection:_set(out,'showTitle',collection,'embedded_json',100)
   if any(x in typ for x in ('podcastepisode','episode')):
    _set(out,'episodeTitle',name,'embedded_json',100)
   elif any(x in typ for x in ('podcastseries','show')):
    _set(out,'showTitle',name,'embedded_json',96)
   for key in ('episodeId','episodeID','adamId'):
    val=node.get(key)
    if val and str(val).startswith('100'):_set(out,'episodeId',val,'embedded_json',98)
   for key in ('showId','showID','collectionId'):_set(out,'showId',node.get(key),'embedded_json',95)
   _set(out,'publicationDate',node.get('datePublished') or node.get('releaseDate'),'embedded_json',90)
   _set(out,'duration',node.get('duration'),'embedded_json',85)
   author=node.get('author') or node.get('creator')
   if isinstance(author,dict):author=author.get('name')
   _set(out,'author',author,'embedded_json',80)
   _set(out,'description',node.get('description'),'embedded_json',80)
   image=node.get('image') or node.get('artworkUrl')
   if isinstance(image,dict):image=image.get('url')
   _set(out,'artworkUrl',image,'embedded_json',80)
 def meta(*keys):
  for key in keys:
   n=soup.find('meta',attrs={'property':key}) or soup.find('meta',attrs={'name':key})
   if n and n.get('content'):return n['content'].strip()
  return None
 site=meta('og:site_name')
 og_title=meta('og:title')
 if site and norm_text(site) not in APPLE_BRAND_NAMES:_set(out,'showTitle',site,'open_graph',75)
 _set(out,'episodeTitle',og_title,'open_graph',72)
 _set(out,'description',meta('og:description','description'),'open_graph',70)
 _set(out,'artworkUrl',meta('og:image'),'open_graph',70)
 _set(out,'publicationDate',meta('article:published_time','datePublished'),'meta_tag',65)
 title=soup.title.get_text(' ',strip=True) if soup.title else None
 _set(out,'episodeTitle',title,'document_title',50)
 episode_id=(out.get('episodeId') or {}).get('value')
 can=canonical_url or final_url or original_url
 if episode_id and can and not extract_apple_ids(can).get('episodeId'):
  diagnostics.append('canonical_url_dropped_episode_identifier')
  can=normalize_apple_url(can,True,episode_id)
 else: can=normalize_apple_url(can,True,episode_id) if can else None
 flat={k:v['value'] for k,v in out.items()}
 flat['canonicalUrl']=can
 flat['countryOrStorefront']=(urlsplit(final_url or original_url or '').path.strip('/').split('/') or [None])[0] or None
 flat['metadataSources']={k:{'source':v['source'],'confidence':v['confidence']} for k,v in out.items()}
 flat['reviewReasons']=diagnostics
 return flat

def classify_apple_destination(original_url,final_url,canonical_url,metadata):
 episode=metadata.get('episodeId') or next((extract_apple_ids(u).get('episodeId') for u in (original_url,final_url,canonical_url) if u),None)
 show=metadata.get('showId') or next((extract_apple_ids(u).get('showId') for u in (original_url,final_url,canonical_url) if u),None)
 if episode:return 'direct episode'
 if show:return 'podcast series or show'
 return 'unknown'
