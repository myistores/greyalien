#!/usr/bin/env python3
"""Rebuild GreyAlien compact entity/relationship indexes and graph manifest.

V23.6D.1 adds a precomputed incoming-relationship index so entity pages no longer
need to fetch every full entity JSON record to discover reverse relationships.
"""
from pathlib import Path
import json
import re
import unicodedata

ROOT=Path(__file__).resolve().parents[1]
ENT=ROOT/'data/entities'; DATA=ROOT/'data'
files=sorted(ENT.glob('*.json'))
entities=[json.loads(p.read_text(encoding='utf-8')) for p in files]
index_entities=[e for e in entities if e.get('taxonomyStatus') != 'alias']
index_ids={e['id'] for e in index_entities}

def normalize_identity(value):
    value=unicodedata.normalize('NFKD', str(value or '')).encode('ascii','ignore').decode('ascii').lower()
    value=value.replace('&',' and ')
    return re.sub(r'[^a-z0-9]+',' ',value).strip()

def canonical_url_identity(url):
    value=str(url or '').lower()
    value=re.sub(r'^https?://(?:www\.)?','',value)
    value=re.split(r'[?#]',value,1)[0].rstrip('/')
    return value

def identity_key(entity):
    explicit=entity.get('canonicalId') or entity.get('canonicalEntityId') or entity.get('sameAsEntityId') or entity.get('realWorldEntityId')
    if explicit:
        return f'canonical:{explicit}'
    if entity.get('type')=='podcast_episode' and entity.get('seriesId') and entity.get('episodeNumber') is not None:
        try: num=int(entity.get('episodeNumber'))
        except (TypeError,ValueError): num=entity.get('episodeNumber')
        return f"podcast_episode:{entity.get('seriesId')}:{num}"
    links=(entity.get('mediaLinks') or [])+(entity.get('officialLinks') or [])+(entity.get('referenceSources') or [])
    for link in links:
        url=(link or {}).get('url')
        if url and re.search(r'/episode(?:s(?:-\d+)?)?/|[?&]episode=',url,re.I):
            return f"{entity.get('type')}:url:{canonical_url_identity(url)}"
    return f"{entity.get('type')}:name:{normalize_identity(entity.get('name'))}"

def canonical_score(entity):
    score=0
    if entity.get('isCanonical') is True or entity.get('canonical') is True or entity.get('status')=='canonical': score+=1000
    if entity.get('canonicalId')==entity.get('id') or entity.get('canonicalEntityId')==entity.get('id'): score+=900
    if re.match(r'^\d{4}-.*episode-\d+$', entity.get('id',''), re.I): score+=120
    if any((s or {}).get('sourceType')=='official_episode_page' for s in (entity.get('referenceSources') or [])): score+=80
    if any(re.search(r'official.*episode|episode.*official',f"{(l or {}).get('label','')} {(l or {}).get('platform','')}",re.I) for l in (entity.get('mediaLinks') or [])): score+=60
    score+=len(entity.get('referenceSources') or [])*3+len(entity.get('officialLinks') or [])*2+len(entity.get('mediaLinks') or [])
    return score

types=[]
for e in index_entities:
    if e['type'] not in types: types.append(e['type'])
index={'schemaVersion':3,'generatedBy':'tools/build_graph.py','entityTypes':types,'entities':[]}
for e in sorted(index_entities,key=lambda x:(x['type'],x['name'].lower(),x['id'])):
    row={k:e[k] for k in ('id','type','name','summary')}
    for k in ('destinationPage','visibleInDirectory','searchable','taxonomyStatus','entitySubtype'):
        if k in e: row[k]=e[k]
    for k in ('date','dateDisplay','status','eventCategory'):
        if e.get(k): row[k]=e[k]
    # Compact precomputed values preserve V23 duplicate/canonical rendering rules
    # without embedding full connected entity records into the index.
    row['_identityKey']=identity_key(e)
    row['_canonicalScore']=canonical_score(e)
    index['entities'].append(row)

ids={e['id'] for e in entities}; incoming={i:0 for i in ids}; outgoing={i:0 for i in ids}; unresolved=[]
# V23.6D.1 reverse lookup: one compact entry per resolved relationship, grouped
# by target. Outgoing relationships continue to come from the requested entity.
incoming_relationships={i:[] for i in sorted(index_ids)}
for e in entities:
    for r in e.get('relationships',[]):
        target=r.get('target')
        if target in ids:
            outgoing[e['id']]+=1; incoming[target]+=1
        else:
            unresolved.append({'source':e['id'],'target':target,'type':r.get('type')})
        # Match prior browser behavior: only searchable/non-alias source and
        # target entities participated in full-graph relationship discovery.
        if e['id'] in index_ids and target in index_ids:
            incoming_relationships[target].append({
                'source':e['id'],
                'type':r.get('type'),
                'meta':r
            })
for target, rows in incoming_relationships.items():
    rows.sort(key=lambda x:(x.get('source',''),x.get('type',''),json.dumps(x.get('meta',{}),sort_keys=True,ensure_ascii=False)))
relationship_index={
    'schemaVersion':1,
    'generatedBy':'tools/build_graph.py',
    'purpose':'Precomputed incoming relationships for reliable entity-page rendering without full-graph fetches.',
    'incoming':incoming_relationships
}
manifest={'schemaVersion':1,'entityCount':len(entities),'relationshipCount':sum(outgoing.values()),'unresolvedRelationshipCount':len(unresolved),'connectionCounts':{i:{'incoming':incoming[i],'outgoing':outgoing[i],'total':incoming[i]+outgoing[i]} for i in sorted(ids)},'unresolvedRelationships':unresolved}
(DATA/'entity-index.json').write_text(json.dumps(index,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(DATA/'relationship-index.json').write_text(json.dumps(relationship_index,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(DATA/'graph-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(f"Built compact index for {len(index_entities)} searchable entities, {sum(outgoing.values())} resolved relationships, and reverse relationship lookup.")
