#!/usr/bin/env python3
"""Rebuild the GreyAlien entity index and computed graph manifest from entity JSON files."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
ENT=ROOT/'data/entities'; DATA=ROOT/'data'
files=sorted(ENT.glob('*.json'))
entities=[json.loads(p.read_text(encoding='utf-8')) for p in files]
types=[]
for e in entities:
    if e['type'] not in types: types.append(e['type'])
index={'schemaVersion':2,'generatedBy':'tools/build_graph.py','entityTypes':types,'entities':[]}
for e in sorted(entities,key=lambda x:(x['type'],x['name'].lower(),x['id'])):
    row={k:e[k] for k in ('id','type','name','summary')}
    for k in ('date','dateDisplay','status'):
        if e.get(k): row[k]=e[k]
    index['entities'].append(row)
ids={e['id'] for e in entities}; incoming={i:0 for i in ids}; outgoing={i:0 for i in ids}; unresolved=[]
for e in entities:
    for r in e.get('relationships',[]):
        if r.get('target') in ids:
            outgoing[e['id']]+=1; incoming[r['target']]+=1
        else: unresolved.append({'source':e['id'],'target':r.get('target'),'type':r.get('type')})
manifest={'schemaVersion':1,'entityCount':len(entities),'relationshipCount':sum(outgoing.values()),'unresolvedRelationshipCount':len(unresolved),'connectionCounts':{i:{'incoming':incoming[i],'outgoing':outgoing[i],'total':incoming[i]+outgoing[i]} for i in sorted(ids)},'unresolvedRelationships':unresolved}
(DATA/'entity-index.json').write_text(json.dumps(index,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(DATA/'graph-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(f"Built index for {len(entities)} entities and {sum(outgoing.values())} resolved relationships.")
