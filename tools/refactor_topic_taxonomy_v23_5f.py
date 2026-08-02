#!/usr/bin/env python3
from pathlib import Path
import json, copy, datetime
ROOT=Path(__file__).resolve().parents[1]; ENT=ROOT/'data/entities'; CFG=ROOT/'data/topic-taxonomy-v23-5f.json'; REPORT=ROOT/'reports/v23-5f'
REPORT.mkdir(parents=True,exist_ok=True)
config=json.loads(CFG.read_text(encoding='utf-8'))
entities={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in ENT.glob('*.json')}
before=copy.deepcopy(entities)
summary={'release':'V23.5F','baseRepository':'V23.5E.1','generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'supportingClassifications':[],'reclassifications':[],'consolidations':[],'relationshipMigrations':[],'aliases':[]}

def unique_merge(dst,key,items):
    existing=dst.setdefault(key,[])
    seen={json.dumps(x,sort_keys=True,ensure_ascii=False) for x in existing}
    for item in items:
        sig=json.dumps(item,sort_keys=True,ensure_ascii=False)
        if sig not in seen: existing.append(copy.deepcopy(item)); seen.add(sig)

def merge_entity(source_id,target_id,reason):
    src=entities[source_id]; dst=entities[target_id]
    unique_merge(dst,'relationships',src.get('relationships',[])); unique_merge(dst,'officialLinks',src.get('officialLinks',[])); unique_merge(dst,'referenceSources',src.get('referenceSources',[]))
    aliases=dst.setdefault('aliases',[])
    for alias in [src.get('name'),source_id,*src.get('aliases',[])]:
        if alias and alias not in aliases: aliases.append(alias)
    migrated=0
    for eid,e in entities.items():
        if eid==source_id: continue
        for rel in e.get('relationships',[]):
            if rel.get('target')==source_id:
                rel['target']=target_id; migrated+=1; summary['relationshipMigrations'].append({'sourceEntity':eid,'oldTarget':source_id,'newTarget':target_id,'relationshipType':rel.get('type')})
        # de-duplicate relationships after target migration
        dedup=[]; seen=set()
        for rel in e.get('relationships',[]):
            sig=json.dumps(rel,sort_keys=True,ensure_ascii=False)
            if sig not in seen: dedup.append(rel); seen.add(sig)
        e['relationships']=dedup
    entities[source_id]={
      'id':source_id,'type':'topic','name':src.get('name',source_id),'summary':src.get('summary','Legacy taxonomy alias.'),
      'relationships':[],'officialLinks':[],'referenceSources':[],
      'taxonomyStatus':'alias','destinationPage':False,'visibleInDirectory':False,'redirectTo':target_id,'canonicalEntityId':target_id
    }
    summary['aliases'].append({'aliasId':source_id,'canonicalId':target_id,'reason':reason,'incomingRelationshipsMigrated':migrated})

for eid in config['supportingClassifications']:
    e=entities[eid]; e['taxonomyStatus']='supporting_classification'; e['destinationPage']=False; e['visibleInDirectory']=False; e['searchable']=True
    summary['supportingClassifications'].append({'id':eid,'name':e['name'],'relationshipsPreserved':len(e.get('relationships',[]))})

for eid,spec in config['reclassifications'].items():
    if spec.get('target'):
        merge_entity(eid,spec['target'],'approved reclassification into existing destination')
        target=entities[spec['target']]; target['entitySubtype']=spec['subtype']; target['taxonomyStatus']='canonical'
        summary['reclassifications'].append({'sourceId':eid,'targetId':spec['target'],'newType':target['type'],'subtype':spec['subtype'],'reusedExistingDestination':True})
    else:
        e=entities[eid]; old=e['type']; e['type']=spec['targetType']; e['entitySubtype']=spec['subtype']; e['taxonomyStatus']='canonical'; e['destinationPage']=True; e['visibleInDirectory']=True
        if spec['subtype'] in ('program','alleged_program'):
            e.setdefault('organizationPurpose',e.get('summary',''))
        if spec['subtype']=='event': e.setdefault('eventCategory','Public research event')
        if spec['subtype'] in ('historical_case','location'): e.setdefault('caseStatus','Research destination')
        summary['reclassifications'].append({'sourceId':eid,'targetId':eid,'oldType':old,'newType':e['type'],'subtype':spec['subtype'],'identifierPreserved':True})

for canonical,aliases in config['duplicateClusters'].items():
    entities[canonical]['taxonomyStatus']='canonical'; entities[canonical]['isCanonical']=True
    for alias in aliases: merge_entity(alias,canonical,'approved duplicate-topic consolidation')
    summary['consolidations'].append({'canonicalId':canonical,'canonicalName':entities[canonical]['name'],'aliases':aliases})

for eid,e in entities.items():
    (ENT/f'{eid}.json').write_text(json.dumps(e,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

# Integrity accounting before/after, treating migrated targets as preserved edges.
def edge_count(es): return sum(len(e.get('relationships',[])) for e in es.values())
summary['beforeEntityCount']=len(before); summary['afterEntityCount']=len(entities); summary['beforeRelationshipCount']=edge_count(before); summary['afterRelationshipCount']=edge_count(entities)
(REPORT/'relationship-migration-summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'supporting':len(summary['supportingClassifications']),'reclassified':len(summary['reclassifications']),'consolidatedAliases':len(summary['aliases']),'relationshipsBefore':summary['beforeRelationshipCount'],'relationshipsAfter':summary['afterRelationshipCount']},indent=2))
