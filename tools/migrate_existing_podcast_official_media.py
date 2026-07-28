#!/usr/bin/env python3
from __future__ import annotations
import json,glob,hashlib,copy,re,sys
from pathlib import Path
from collections import Counter,defaultdict
sys.path.insert(0,str(Path(__file__).parent))
from podcast_official_media import canonical_url,validate_record,resolve_preferred
ROOT=Path(__file__).resolve().parents[1]
TARGETS={
 'weaponized-podcast':'WEAPONIZED',
 'need-to-know-podcast':'Need to Know',
 'merged-podcast':'MERGED',
 'somewhere-in-the-skies-podcast':'Somewhere in the Skies'
}
MEDIA_FIELDS=('mediaLinks','officialLinks','referenceSources')

def platform(item):
 u=item.get('url','').lower(); p=(item.get('platform') or item.get('linkType') or item.get('sourceType') or '').lower()
 if 'youtube' in u or 'youtu.be' in u or 'youtube' in p:return 'YouTube'
 if 'podcasts.apple.com' in u or 'apple' in p:return 'Apple Podcasts'
 if 'spotify.com' in u or 'spotify' in p:return 'Spotify'
 if any(x in u for x in ('weaponizedpodcast.com','mergedpodcast.com','somewhereintheskies.com')):return 'Official website'
 if u.endswith(('.rss','.xml')) or '/feed' in u or 'feed' in p:return 'RSS'
 if 'chtbl.com' in u:return 'Official audio feed'
 return item.get('platform') or 'Official media'

def classify(entity,item,field):
 u=item['url']; ul=u.lower(); txt=' '.join(str(item.get(k,'')) for k in ('label','platform','linkType','sourceType','linkScope')).lower()
 is_series=entity.get('type')=='podcast_series'
 if u.lower().endswith(('.rss','.xml')) or '/feed' in ul or 'audio_feed' in txt:
  return 'feed','feed',7,'Open Official RSS Feed'
 if 'youtube.com/playlist' in ul:
  return 'playlist','video',6,'Browse Official YouTube Playlist'
 if 'youtube.com/channel/' in ul or re.search(r'youtube\.com/@[^/?#]+/?$',ul):
  return 'channel','video',6,'Open Official YouTube Channel'
 if 'podcasts.apple.com' in ul:
  dest='series' if is_series or '/podcast/' in ul and '?i=' not in ul else 'episode'
  return dest,'audio',6 if dest=='series' else 3,'Browse Apple Podcasts Series Archive' if dest=='series' else 'Listen on Apple Podcasts'
 if 'open.spotify.com/show/' in ul:
  return 'series','audio',6,'Browse Spotify Series Archive'
 if 'open.spotify.com/episode/' in ul:
  return 'episode','audio',4,'Listen on Spotify'
 if 'chtbl.com' in ul:
  return ('series' if is_series else 'series'),'audio',6,'Browse Official Podcast Archive'
 if is_series:
  return 'series','web_page',6,'Open Official Podcast Website'
 # explicit legacy distinctions first
 if item.get('linkScope')=='series_archive' or 'series archive' in txt or 'archive fallback' in txt:
  return 'series','audio' if platform(item) in ('Apple Podcasts','Spotify') else 'web_page',6,'Browse Official Series Archive'
 if 'watch?v=' in ul or 'youtu.be/' in ul:
  return 'episode','video',2,'Watch on YouTube'
 if 'official_episode_page' in txt or re.search(r'/episode(?:s(?:-\d+)?)?/[^/?#]+',ul) or re.search(r'/episodes?-\d+/episode-\d+',ul):
  return 'episode','web_page',1,'Open Official Episode Page'
 # preserve current public behavior but do not mislabel ambiguous links
 return 'series','web_page',6,'Browse Official Series Archive'

def status(item):
 s=item.get('verificationStatus') or item.get('validationStatus') or 'verified'
 return {'live_verified':'verified','live_verified_fallback':'verified'}.get(s,s if s in {'verified','pending_review','unavailable','retired','rejected'} else 'pending_review')

def migrate_entity(entity):
 gathered=[]
 for field in MEDIA_FIELDS:
  for pos,item in enumerate(entity.get(field,[]) or []):
   if isinstance(item,dict) and item.get('url'):
    d,m,r,l=classify(entity,item,field); st=status(item)
    gathered.append({
      '_field':field,'_index':pos,'platform':platform(item),'url':item['url'],'destinationType':d,'mediaType':m,
      'official': field!='referenceSources' or str(item.get('sourceType','')).startswith(('official_','authoritative_')),
      'verified':st=='verified','verificationStatus':st,'preferredRank':r,'label':l,
      'approved':st=='verified','published':st=='verified',
      'migrationProvenance':{'release':'V23.5B','legacyField':field,'legacyIndex':pos,'legacyLabel':item.get('label','')}
    })
 # dedupe while retaining all provenance
 chosen={}; dup=0
 for rec in gathered:
  key=canonical_url(rec['url']); old=chosen.get(key)
  if old:
   dup+=1
   old.setdefault('migrationProvenanceMerged',[]).append(rec['migrationProvenance'])
   score=lambda x:(x['official'],x['destinationType']=='episode',x['verified'],-x['preferredRank'])
   if score(rec)>score(old):
    rec['migrationProvenanceMerged']=old.get('migrationProvenanceMerged',[])+[old['migrationProvenance']]
    chosen[key]=rec
  else: chosen[key]=rec
 records=list(chosen.values())
 records.sort(key=lambda x:(x['destinationType']!='episode',x['preferredRank'],x['platform'],x['url']))
 out=copy.deepcopy(entity); out['officialMedia']=records
 pref=resolve_preferred(out,preserve_legacy=False)
 out['mediaMigration']={
   'release':'V23.5B','status':'approved' if pref else 'compatibility_only',
   'legacyFieldsPreserved':True,'legacyUrlCount':len(gathered),'mediaRecordCount':len(records),
   'duplicateCanonicalUrlsSuppressed':dup,
   'preferredCanonicalUrl':canonical_url(pref['url']) if pref else None,
   'preferredLabel':pref['label'] if pref else None
 }
 return out,gathered,dup

def nonmedia(d):
 d=copy.deepcopy(d); d.pop('officialMedia',None); d.pop('mediaMigration',None); return d

def main():
 before={}; reports={k:Counter() for k in TARGETS}; inventory=[]
 snapshot_dir=ROOT/'data'/'migration'/'v23.5b'; snapshot_dir.mkdir(parents=True,exist_ok=True)
 for f in glob.glob(str(ROOT/'data/entities/*.json')):
  entity=json.load(open(f,encoding='utf-8')); sid=entity.get('id') if entity.get('id') in TARGETS else entity.get('seriesId')
  if sid not in TARGETS: continue
  before[entity['id']]=copy.deepcopy(entity)
  migrated,gathered,dup=migrate_entity(entity)
  for r in migrated['officialMedia']:
   errs=validate_record(r)
   if errs: raise SystemExit(f"{entity['id']} {r['url']}: {errs}")
  Path(f).write_text(json.dumps(migrated,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
  c=reports[sid]; c['series_entities']+=entity.get('type')=='podcast_series'; c['episode_entities']+=entity.get('type')=='podcast_episode'; c['legacy_urls']+=len(gathered); c['media_records']+=len(migrated['officialMedia']); c['duplicates']+=dup
  pref=resolve_preferred(migrated,preserve_legacy=False)
  if pref:c['preferred_'+pref['platform']]+=1
  else:c['no_approved_destination']+=1
  for r in migrated['officialMedia']:
   c[r['destinationType']]+=1
   if r['verificationStatus']=='retired':c['retired']+=1
   if r['verificationStatus']=='pending_review':c['pending_review']+=1
  if pref and pref['destinationType']!='episode' and entity.get('type')=='podcast_episode':c['series_fallbacks']+=1
  for g in gathered:
   d,m,r,l=classify(entity,g,g.get('_field',''))
   inventory.append({'series':TARGETS[sid],'seriesId':sid,'entityId':entity['id'],'entityType':entity['type'],'episodeNumber':entity.get('episodeNumber'),'episodeTitle':entity.get('episodeTitle') or entity.get('name'),'publicationDate':entity.get('date'),'legacyField':g.get('_field'),'legacyLabel':g.get('label'),'url':g['url'],'platform':platform(g),'destinationType':d,'mediaType':m,'official':g.get('official',True),'validationStatus':status(g),'canonicalUrl':canonical_url(g['url']),'proposedPreferredRank':r,'migrationDecision':'accepted','reviewRequirement':'none' if status(g)=='verified' else 'human_review'})
 # integrity
 changed=[]
 for eid,old in before.items():
  new=json.load(open(ROOT/'data/entities'/f'{eid}.json',encoding='utf-8'))
  if nonmedia(old)!=nonmedia(new):changed.append(eid)
 if changed: raise SystemExit('Unauthorized non-media changes: '+','.join(changed))
 combined=Counter()
 for c in reports.values():combined.update(c)
 payload={'release':'V23.5B','seriesReports':{TARGETS[k]:dict(v) for k,v in reports.items()},'combined':dict(combined),'nonMediaFieldChangeCount':0,'entityCount':len(before)}
 (snapshot_dir/'media-inventory.json').write_text(json.dumps(inventory,indent=2,ensure_ascii=False)+'\n')
 (snapshot_dir/'reconciliation.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n')
 (snapshot_dir/'rollback-manifest.json').write_text(json.dumps({'release':'V23.5B','method':'Remove officialMedia and mediaMigration fields to restore V23.5A entity representation; legacy fields are unchanged.','entities':sorted(before)},indent=2)+'\n')
 print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
