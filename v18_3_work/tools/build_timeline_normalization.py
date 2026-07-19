#!/usr/bin/env python3
"""Build canonical timeline-event aliases without altering source entities."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
ENTITIES=ROOT/'data/entities'
OUT=ROOT/'data/timeline-normalization.json'

def load():
    return {p.stem:json.loads(p.read_text(encoding='utf-8')) for p in sorted(ENTITIES.glob('*.json'))}

def main():
    entities=load(); aliases={}; canonical={}; conflicts=[]
    for eid,e in entities.items():
        if e.get('type')!='timeline_event': continue
        canonical[eid]={
            'id':eid,'date':e.get('date',''),'eventCategory':e.get('eventCategory',''),
            'name':e.get('name',''),'aliases':[]
        }
        explicit=e.get('canonicalEventId')
        if explicit and explicit!=eid:
            aliases[eid]=explicit
        for rel in e.get('relationships',[]):
            target=entities.get(rel.get('target'))
            if not target or target.get('type') not in {'interview','podcast_episode','hearing','document','publication'}:
                continue
            same_date=bool(e.get('date') and target.get('date') and e.get('date')==target.get('date'))
            explicit_match=target.get('canonicalEventId')==eid
            role_match=rel.get('role') in {'related_media','documented_by','publisher'}
            if same_date and (role_match or explicit_match):
                prior=aliases.get(target['id'])
                if prior and prior!=eid:
                    conflicts.append({'alias':target['id'],'canonicalCandidates':[prior,eid]})
                    continue
                aliases[target['id']]=eid
                canonical[eid]['aliases'].append(target['id'])
    payload={
        'schemaVersion':'1.0','description':'Maps dated media/document records to canonical timeline-event records for display normalization.',
        'aliases':dict(sorted(aliases.items())),
        'canonicalEvents':dict(sorted(canonical.items())),
        'conflicts':conflicts,
        'statistics':{'canonicalEventCount':len(canonical),'aliasCount':len(aliases),'conflictCount':len(conflicts)}
    }
    OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f"Timeline normalization built: {len(canonical)} canonical events, {len(aliases)} aliases, {len(conflicts)} conflicts.")
    if conflicts: raise SystemExit(1)
if __name__=='__main__': main()
