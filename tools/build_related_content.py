#!/usr/bin/env python3
"""Generate Referenced In and related-podcast-episode recommendations."""
from pathlib import Path
from datetime import datetime, timezone
import json
ROOT=Path(__file__).resolve().parents[1]
ENT=ROOT/'data/entities'; OUT=ROOT/'data/related-content.json'
entities=[json.loads(p.read_text(encoding='utf-8')) for p in sorted(ENT.glob('*.json'))]
by_id={e['id']:e for e in entities}
refs={eid:[] for eid in by_id}
for source in entities:
    for rel in source.get('relationships',[]):
        target=rel.get('target')
        if target in refs:
            refs[target].append({'id':source['id'],'type':source['type'],'name':source['name'],'relationshipType':rel.get('type',''),'role':rel.get('role',''),'context':rel.get('context','')})
for rows in refs.values():
    rows.sort(key=lambda x:(x['type'],x['name'].lower(),x['id']))

episodes=[e for e in entities if e.get('type')=='podcast_episode']
targets={e['id']:{r.get('target') for r in e.get('relationships',[]) if r.get('target') and r.get('type')!='episode_of'} for e in episodes}
related={}
for ep in episodes:
    candidates=[]
    for other in episodes:
        if other['id']==ep['id']: continue
        shared=sorted(targets[ep['id']] & targets[other['id']])
        if not shared: continue
        same_series=(ep.get('seriesId') and ep.get('seriesId')==other.get('seriesId'))
        score=len(shared)*10+(5 if same_series else 0)
        candidates.append({'id':other['id'],'name':other['name'],'seriesId':other.get('seriesId',''),'date':other.get('date',''),'sharedEntityIds':shared,'sharedEntityCount':len(shared),'score':score})
    candidates.sort(key=lambda x:(x['score'],x.get('date',''),x['name']),reverse=True)
    related[ep['id']]=candidates[:6]

payload={'schemaVersion':1,'generatedBy':'tools/build_related_content.py','generatedAt':datetime.now(timezone.utc).isoformat(),'referencedIn':refs,'relatedEpisodes':related}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(f'Built related-content data for {len(entities)} entities and {len(episodes)} podcast episodes.')
