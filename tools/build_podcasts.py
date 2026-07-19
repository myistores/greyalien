#!/usr/bin/env python3
"""Build podcast-series and episode indexes from universal entity JSON files."""
from pathlib import Path
from datetime import datetime, timezone
import json
ROOT=Path(__file__).resolve().parents[1]
ENT=ROOT/'data/entities'; OUT=ROOT/'data/podcasts'
entities=[json.loads(p.read_text(encoding='utf-8')) for p in sorted(ENT.glob('*.json'))]
by_id={e['id']:e for e in entities}
series=sorted((e for e in entities if e.get('type')=='podcast_series'),key=lambda e:(e.get('launchYear','9999'),e['name'].lower()))
episodes=[]
for e in entities:
    rels=e.get('relationships',[])
    ep_rel=next((r for r in rels if r.get('type')=='episode_of'),None)
    if e.get('type')=='podcast_episode' or ep_rel:
        sid=e.get('seriesId') or (ep_rel or {}).get('target')
        row={k:e.get(k) for k in ('id','name','summary','date','dateDisplay','episodeNumber','episodeTitle','runtime','status') if e.get(k) not in (None,'')}
        row['seriesId']=sid
        row['externalUrl']=e.get('externalUrl','')
        row['guestIds']=[r['target'] for r in rels if r.get('role')=='guest']
        row['subjectIds']=[r['target'] for r in rels if r.get('role') in ('primary_subject','co_subject')]
        row['claimIds']=[r['target'] for r in rels if r.get('type') in ('presented_claim','contains_claim','references_claim')]
        row['relationshipCount']=len(rels)
        episodes.append(row)
episodes.sort(key=lambda e:(e.get('date',''),str(e.get('episodeNumber','')),e['id']),reverse=True)
rows=[]
for p in series:
    pe=[e for e in episodes if e.get('seriesId')==p['id']]
    connected=set()
    for e in pe:
        src=by_id[e['id']]
        connected.update(r.get('target') for r in src.get('relationships',[]) if r.get('target') and r.get('target')!=p['id'])
    rows.append({'id':p['id'],'name':p['name'],'hosts':p.get('podcastHosts',[]),'launchYear':p.get('launchYear',''),'status':p.get('status',''),'summary':p['summary'],'officialWebsite':p.get('externalUrl',''),'episodeCount':len(pe),'connectedEntityCount':len(connected),'latestEpisodeDate':max((e.get('date','') for e in pe),default='')})
(OUT/'podcast-index.json').write_text(json.dumps({'schemaVersion':2,'generatedBy':'tools/build_podcasts.py','podcasts':rows},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(OUT/'episode-index.json').write_text(json.dumps({'schemaVersion':1,'generatedBy':'tools/build_podcasts.py','episodes':episodes},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
manifest={'schemaVersion':1,'seriesCount':len(rows),'episodeCount':len(episodes),'episodesBySeries':{p['id']:sum(1 for e in episodes if e.get('seriesId')==p['id']) for p in rows},'generatedAt':datetime.now(timezone.utc).isoformat()}
(OUT/'podcast-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(f"Built {len(rows)} podcast series and {len(episodes)} episode records.")
