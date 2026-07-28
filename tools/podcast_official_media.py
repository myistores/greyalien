#!/usr/bin/env python3
"""Universal podcast official-media adapters, canonicalization, resolution, and validation."""
from __future__ import annotations
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode
import re
DESTINATION_TYPES={"episode","series","playlist","channel","feed"}
MEDIA_TYPES={"audio","video","web_page","feed"}
VERIFICATION_STATUSES={"verified","pending_review","unavailable","retired","rejected"}
TRACKING={"fbclid","gclid","mc_cid","mc_eid"}

def canonical_url(value:str)->str:
    try:
        s=urlsplit(value.strip()); host=s.hostname.lower() if s.hostname else ''
        if host.startswith('www.'): host=host[4:]
        if host in {'m.youtube.com','music.youtube.com'}: host='youtube.com'
        if host=='youtu.be':
            video=s.path.strip('/'); s=urlsplit('https://youtube.com/watch?'+urlencode({'v':video}))
            host='youtube.com'
        scheme='https'; port=s.port
        netloc=host if not port or port in (80,443) else f'{host}:{port}'
        path=re.sub(r'/+','/',s.path or '/'); path=path.rstrip('/') or '/'
        query=[]
        for k,v in parse_qsl(s.query,keep_blank_values=True):
            lk=k.lower()
            if lk.startswith('utm_') or lk in TRACKING: continue
            if host.endswith('youtube.com') and path=='/watch' and lk!='v': continue
            query.append((k,v))
        query.sort()
        return urlunsplit((scheme,netloc,path,urlencode(query),'')).rstrip('/')
    except Exception: return str(value).strip()

def infer_destination(link:dict)->str:
    explicit=link.get('destinationType') or link.get('linkScope')
    if explicit in DESTINATION_TYPES: return explicit
    if explicit=='series_archive': return 'series'
    url=(link.get('url') or '').lower(); text=' '.join(str(link.get(k,'')) for k in ('label','platform','sourceType')).lower()
    if 'rss' in text or url.endswith(('.rss','.xml')) or '/feed' in url: return 'feed'
    if 'playlist?' in url or 'collection' in text or 'playlist' in text: return 'playlist'
    if '/channel/' in url or '/@' in url and '/search' not in url: return 'channel'
    if any(x in text for x in ('episode page','episode video','episode #','episode ')) or 'watch?v=' in url or '/episode' in url: return 'episode'
    return 'series'

def infer_media_type(link:dict)->str:
    v=(link.get('mediaType') or '').lower().replace(' ','_')
    if v in MEDIA_TYPES:return v
    u=(link.get('url') or '').lower(); p=(link.get('platform') or '').lower()
    if infer_destination(link)=='feed': return 'feed'
    if 'youtube' in u or 'youtube' in p: return 'video'
    if any(x in u+p for x in ('spotify','apple','ivoox','audio','podcast')): return 'audio'
    return 'web_page'

def rank_for(link:dict)->int:
    if isinstance(link.get('preferredRank'),int): return link['preferredRank']
    d=infer_destination(link); u=(link.get('url') or '').lower(); p=(link.get('platform') or '').lower()
    if d=='episode':
        if 'youtube' in u+p:return 2
        if 'podcasts.apple.com' in u+p:return 3
        if 'spotify' in u+p:return 4
        if any(x in u for x in ('weaponizedpodcast.com','somewhereintheskies.com')):return 1
        return 5
    if d in {'series','playlist','channel'}:return 6
    return 7

def adapt_legacy(entity:dict)->list[dict]:
    out=[]
    for field in ('mediaLinks','officialLinks','referenceSources'):
        for item in entity.get(field,[]) or []:
            if not isinstance(item,dict) or not item.get('url'):continue
            status=item.get('verificationStatus') or item.get('validationStatus') or 'verified'
            status={'live_verified':'verified','live_verified_fallback':'verified'}.get(status,status)
            official=field!='referenceSources' or str(item.get('sourceType','')).startswith(('official_','authoritative_'))
            out.append({'platform':item.get('platform') or item.get('linkType') or item.get('sourceType') or 'Official media','url':item['url'],'destinationType':infer_destination(item),'mediaType':infer_media_type(item),'official':bool(official),'verified':status=='verified','verificationStatus':status if status in VERIFICATION_STATUSES else 'pending_review','preferredRank':rank_for(item),'label':item.get('label') or 'Open official media','legacySource':field,'legacy':True})
    return dedupe(out)

def dedupe(records:list[dict])->list[dict]:
    chosen={}
    for r in records:
        key=canonical_url(r.get('url',''))
        old=chosen.get(key)
        score=lambda x:(bool(x.get('official')),x.get('destinationType')=='episode',x.get('verified'),-int(x.get('preferredRank',999)))
        if not old or score(r)>score(old): chosen[key]=r
    return list(chosen.values())

def collection_for(entity:dict)->list[dict]:
    explicit=entity.get('officialMedia')
    return dedupe(explicit) if isinstance(explicit,list) else adapt_legacy(entity)

def public_eligible(r:dict)->bool:
    return bool(r.get('official')) and bool(r.get('verified')) and r.get('verificationStatus')=='verified' and r.get('approved',True) is not False and r.get('published',True) is not False

def resolve_preferred(entity:dict,preserve_legacy=True):
    records=[r for r in collection_for(entity) if public_eligible(r)]
    if not records:return None
    if preserve_legacy and not isinstance(entity.get('officialMedia'),list):
        legacy=[r for r in records if r.get('legacySource')=='mediaLinks']
        if legacy:return legacy[0]
    records.sort(key=lambda r:(r.get('destinationType')!='episode',int(r.get('preferredRank',999)),r.get('label','')))
    return records[0]

def validate_record(r:dict)->list[str]:
    e=[]
    for k in ('platform','url','destinationType','mediaType','official','verified','verificationStatus','preferredRank','label'):
        if k not in r:e.append(f'missing {k}')
    if r.get('destinationType') not in DESTINATION_TYPES:e.append('invalid destinationType')
    if r.get('mediaType') not in MEDIA_TYPES:e.append('invalid mediaType')
    if r.get('verificationStatus') not in VERIFICATION_STATUSES:e.append('invalid verificationStatus')
    if not isinstance(r.get('official'),bool):e.append('official must be boolean')
    if not isinstance(r.get('verified'),bool):e.append('verified must be boolean')
    if not isinstance(r.get('preferredRank'),int) or r.get('preferredRank',0)<1:e.append('invalid preferredRank')
    if not re.match(r'^https?://',str(r.get('url',''))):e.append('invalid URL')
    u=str(r.get('url','')).lower(); d=r.get('destinationType')
    if 'playlist?' in u and d=='episode':e.append('playlist classified as episode')
    if ('/channel/' in u or re.search(r'youtube\.com/@[^/]+/?$',u)) and d=='episode':e.append('channel classified as episode')
    if (u.endswith(('.rss','.xml')) or '/feed' in u) and d=='episode':e.append('feed classified as episode')
    return e
