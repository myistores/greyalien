from __future__ import annotations
import json,re
from urllib.parse import parse_qs,urlsplit,urlunsplit,urlencode
from .common import norm_text

APPLE_BRAND_NAMES={
 'apple','apple podcast','apple podcasts','apple podcasts preview','apple podcasts preview app',
 'listen on apple podcasts','podcasts on apple podcasts','apple podcasts app','itunes','itunes store'
}
SOURCE_CONFIDENCE={
 'apple_structured_metadata':100,'embedded_json':98,'json_ld':96,'apple_storefront_metadata':94,
 'canonical_metadata':86,'open_graph':76,'twitter_card':70,'document_title':52
}

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
 v=str(v).strip()
 v=re.sub(r'^Listen to\s+','',v,flags=re.I)
 v=re.sub(r'\s*[-|–—:]\s*(?:Apple Podcasts(?: Preview)?|Listen on Apple Podcasts)\s*$','',v,flags=re.I).strip()
 return v or None

def is_apple_branding(value):
 raw=re.sub(r'[^a-z0-9]+',' ',str(value or '').lower()).strip()
 cleaned=re.sub(r'[^a-z0-9]+',' ',str(_clean_title(value) or '').lower()).strip()
 return not cleaned or raw in APPLE_BRAND_NAMES or cleaned in APPLE_BRAND_NAMES or bool(re.fullmatch(r'(?:listen on )?apple podcasts?(?: preview)?',raw))

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
  try:yield json.loads(raw),('json_ld' if 'ld+json' in typ else 'embedded_json')
  except Exception:continue

def _candidate(candidates,field,value,source,confidence=None,context=None):
 if value in (None,'',[]):return
 if isinstance(value,dict):value=value.get('name') or value.get('title') or value.get('value')
 if value in (None,'',[]):return
 if field in {'showTitle','episodeTitle'}:value=_clean_title(value)
 if not value:return
 rejected=False; reason=None
 if field=='showTitle' and is_apple_branding(value):rejected=True;reason='platform_branding'
 candidates.append({'field':field,'value':str(value) if field in {'showId','episodeId'} else value,'source':source,'confidence':confidence if confidence is not None else SOURCE_CONFIDENCE.get(source,50),'rejected':rejected,'rejectionReason':reason,'context':context})

def _meta(soup,*keys):
 for key in keys:
  n=soup.find('meta',attrs={'property':key}) or soup.find('meta',attrs={'name':key})
  if n and n.get('content'):return n['content'].strip()
 return None

def _canonical_slug_title(url):
 path=urlsplit(url or '').path
 m=re.search(r'/podcast/([^/]+)/id\d+',path)
 if not m:return None
 slug=m.group(1).replace('-',' ').strip()
 return ' '.join(w.capitalize() if w.lower() not in {'in','the','of','and','to'} else w.lower() for w in slug.split())

def extract_apple_metadata(soup,original_url,final_url,canonical_url=None):
 candidates=[]; diagnostics=[]
 urls=[('original_url',original_url),('final_url',final_url),('canonical_url',canonical_url)]
 for source,url in urls:
  item=extract_apple_ids(url)
  _candidate(candidates,'showId',item.get('showId'),source,98)
  _candidate(candidates,'episodeId',item.get('episodeId'),source,100)
 for document,script_source in _json_scripts(soup):
  for node in _walk(document):
   typ=str(node.get('@type') or node.get('type') or node.get('kind') or '').lower()
   name=node.get('name') or node.get('title')
   collection=node.get('partOfSeries') or node.get('partOfPodcastSeries') or node.get('collectionName') or node.get('podcastName') or node.get('showName')
   source='apple_structured_metadata' if any(k in node for k in ('podcastName','collectionName','showName','adamId')) else script_source
   if collection:_candidate(candidates,'showTitle',collection,source,SOURCE_CONFIDENCE.get(source),typ)
   if any(x in typ for x in ('podcastepisode','podcast-episode','episode')):
    _candidate(candidates,'episodeTitle',name,source,SOURCE_CONFIDENCE.get(source),typ)
   elif any(x in typ for x in ('podcastseries','podcast-series','show')):
    _candidate(candidates,'showTitle',name,source,SOURCE_CONFIDENCE.get(source)-2,typ)
   for key in ('episodeId','episodeID','episodeAdamId'):_candidate(candidates,'episodeId',node.get(key),source,98,key)
   adam=node.get('adamId')
   if adam and str(adam).startswith('100'):_candidate(candidates,'episodeId',adam,source,98,'adamId')
   for key in ('showId','showID','collectionId'):_candidate(candidates,'showId',node.get(key),source,95,key)
   _candidate(candidates,'publicationDate',node.get('datePublished') or node.get('releaseDate') or node.get('releaseDateTime'),source,90)
   _candidate(candidates,'duration',node.get('duration'),source,85)
   _candidate(candidates,'episodeNumber',node.get('episodeNumber') or node.get('trackNumber'),source,88)
   author=node.get('author') or node.get('creator') or node.get('artistName')
   _candidate(candidates,'author',author,source,80)
   _candidate(candidates,'description',node.get('description') or node.get('shortDescription'),source,80)
   image=node.get('image') or node.get('artworkUrl') or node.get('artwork')
   _candidate(candidates,'artworkUrl',image,source,80)
 site=_meta(soup,'og:site_name'); og_title=_meta(soup,'og:title')
 _candidate(candidates,'showTitle',site,'open_graph',76,'og:site_name')
 _candidate(candidates,'episodeTitle',og_title,'open_graph',74,'og:title')
 _candidate(candidates,'description',_meta(soup,'og:description','description'),'open_graph',70)
 _candidate(candidates,'artworkUrl',_meta(soup,'og:image'),'open_graph',70)
 _candidate(candidates,'showTitle',_meta(soup,'twitter:site','twitter:creator'),'twitter_card',68)
 _candidate(candidates,'episodeTitle',_meta(soup,'twitter:title'),'twitter_card',70)
 _candidate(candidates,'publicationDate',_meta(soup,'article:published_time','datePublished','music:release_date'),'open_graph',66)
 canonical=canonical_url or final_url or original_url
 _candidate(candidates,'showTitle',_canonical_slug_title(canonical),'canonical_metadata',64,'canonical_url_slug')
 title=soup.title.get_text(' ',strip=True) if soup.title else None
 destination_has_episode=any(extract_apple_ids(u).get('episodeId') for _,u in urls if u)
 _candidate(candidates,'episodeTitle' if destination_has_episode else 'showTitle',title,'document_title',52,'html_title')
 selected={}
 for c in candidates:
  if c['rejected']:continue
  cur=selected.get(c['field'])
  if cur is None or c['confidence']>cur['confidence']:selected[c['field']]=c
 episode_id=(selected.get('episodeId') or {}).get('value')
 can=canonical
 if episode_id and can and not extract_apple_ids(can).get('episodeId'):
  diagnostics.append('canonical_url_dropped_episode_identifier');can=normalize_apple_url(can,True,episode_id)
 else:can=normalize_apple_url(can,True,episode_id) if can else None
 flat={k:v['value'] for k,v in selected.items()}
 flat['canonicalUrl']=can
 flat['countryOrStorefront']=(urlsplit(final_url or original_url or '').path.strip('/').split('/') or [None])[0] or None
 flat['metadataSources']={k:{'source':v['source'],'confidence':v['confidence']} for k,v in selected.items()}
 flat['metadataSourceSelected']=flat.get('metadataSources',{}).get('showTitle')
 flat['rejectedMetadataCandidates']=[c for c in candidates if c['rejected']]
 flat['metadataCandidates']=candidates
 flat['confidenceScore']=(selected.get('showTitle') or {}).get('confidence')
 flat['finalSelectedSeries']=flat.get('showTitle')
 flat['finalSelectedEpisode']=flat.get('episodeTitle')
 flat['parserDecisionPath']=[f"reject:{c['source']}:{c['value']}:{c['rejectionReason']}" for c in candidates if c['rejected']]+[f"select:{k}:{v['source']}:{v['confidence']}" for k,v in selected.items()]
 flat['reviewReasons']=diagnostics
 return flat

def classify_apple_destination(original_url,final_url,canonical_url,metadata):
 episode=metadata.get('episodeId') or next((extract_apple_ids(u).get('episodeId') for u in (original_url,final_url,canonical_url) if u),None)
 show=metadata.get('showId') or next((extract_apple_ids(u).get('showId') for u in (original_url,final_url,canonical_url) if u),None)
 if episode:return 'direct episode'
 if show:return 'podcast series or show'
 return 'unknown'
