#!/usr/bin/env python3
from pathlib import Path
import json, copy, datetime
ROOT=Path(__file__).resolve().parents[1]; ENT=ROOT/'data/entities'; REPORT=ROOT/'reports/v23-5g'; REPORT.mkdir(parents=True,exist_ok=True)
entities={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in ENT.glob('*.json')}; before=copy.deepcopy(entities)
metadata=['60-minutes','animal-wellness-action','buddha-jones','fox-news','lord-huron','wall-street-journal']
reclass={
'aatip':('program','Government Program'),'aawsap':('program','Government Program'),'advanced-theoretical-physics-program':('program','Government Program'),'project-blue-book':('program','Government Program'),'project-sign':('program','Government Program'),'uap-task-force':('program','Government Program'),
'galileo-project':('research_project','Research Project / Initiative'),'disclosure-project':('research_project','Research Project / Initiative'),
'nasa-uap-independent-study-team':('advisory_panel','Scientific Advisory Panel'),
'eglin-air-force-base':('facility','Military Installation / Facility'),'malmstrom-air-force-base':('facility','Military Installation / Facility'),'minot-air-force-base':('facility','Military Installation / Facility'),'raf-bentwaters':('facility','Military Installation / Facility'),'vandenberg-space-force-base':('facility','Military Installation / Facility'),'icecube-neutrino-observatory':('facility','Observatory / Research Facility'),
'uss-jackson':('military_vessel','Military Vessel'),'uss-princeton':('military_vessel','Military Vessel'),
'ask-a-pol':('publication','Publication / Media Outlet'),'australian-broadcasting-corporation':('publication','Publication / Media Outlet'),'klas-tv':('publication','Publication / Media Outlet'),'liberation-times':('publication','Publication / Media Outlet'),'the-new-york-times':('publication','Publication / Media Outlet'),'uap-register':('publication','Publication / Media Outlet'),
'united-states-air-force-thunderbirds':('military_unit','Military Unit')}
duplicates={'aaro':['all-domain-anomaly-resolution-office'],'department-of-defense':['united-states-department-of-defense']}
summary={'release':'V23.5G','baseRepository':'V23.5F','generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'metadataConversions':[],'reclassifications':[],'consolidations':[],'relationshipMigrations':[],'aliases':[]}
def unique(dst,key,items):
    cur=dst.setdefault(key,[]); seen={json.dumps(x,sort_keys=True) for x in cur}
    for x in items:
        s=json.dumps(x,sort_keys=True)
        if s not in seen: cur.append(copy.deepcopy(x)); seen.add(s)
def merge(srcid,dstid):
    src,dst=entities[srcid],entities[dstid]
    for k in ('relationships','officialLinks','referenceSources'): unique(dst,k,src.get(k,[]))
    aliases=dst.setdefault('aliases',[])
    for a in [src.get('name'),srcid,*src.get('aliases',[])]:
        if a and a not in aliases: aliases.append(a)
    migrated=0
    for eid,e in entities.items():
        if eid==srcid: continue
        for r in e.get('relationships',[]):
            if r.get('target')==srcid:
                r['target']=dstid; migrated+=1; summary['relationshipMigrations'].append({'sourceEntity':eid,'oldTarget':srcid,'newTarget':dstid,'relationshipType':r.get('type')})
        ded=[]; seen=set()
        for r in e.get('relationships',[]):
            s=json.dumps(r,sort_keys=True)
            if s not in seen: ded.append(r); seen.add(s)
        e['relationships']=ded
    entities[srcid]={'id':srcid,'type':src.get('type','organization'),'name':src.get('name',srcid),'summary':src.get('summary','Legacy alias.'),'relationships':[],'taxonomyStatus':'alias','destinationPage':False,'visibleInDirectory':False,'searchable':True,'redirectTo':dstid,'canonicalEntityId':dstid}
    summary['aliases'].append({'aliasId':srcid,'canonicalId':dstid,'incomingRelationshipsMigrated':migrated})
for eid in metadata:
    e=entities[eid]; e['taxonomyStatus']='supporting_metadata'; e['destinationPage']=False; e['visibleInDirectory']=False; e['searchable']=True
    summary['metadataConversions'].append({'id':eid,'name':e['name'],'relationshipsPreserved':len(e.get('relationships',[]))})
for eid,(typ,sub) in reclass.items():
    e=entities[eid]; old=e['type']; e['type']=typ; e['entitySubtype']=sub; e['taxonomyStatus']='canonical'; e['destinationPage']=True; e['visibleInDirectory']=True; e['searchable']=True
    summary['reclassifications'].append({'id':eid,'name':e['name'],'oldType':old,'newType':typ,'subtype':sub,'identifierPreserved':True,'relationshipsPreserved':len(e.get('relationships',[]))})
for canonical,aliases in duplicates.items():
    entities[canonical]['taxonomyStatus']='canonical'; entities[canonical]['isCanonical']=True
    for alias in aliases: merge(alias,canonical)
    summary['consolidations'].append({'canonicalId':canonical,'canonicalName':entities[canonical]['name'],'aliases':aliases})
for eid,e in entities.items(): (ENT/f'{eid}.json').write_text(json.dumps(e,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
summary['beforeEntityCount']=len(before); summary['afterEntityCount']=len(entities); summary['beforeRelationshipCount']=sum(len(e.get('relationships',[])) for e in before.values()); summary['afterRelationshipCount']=sum(len(e.get('relationships',[])) for e in entities.values())
(REPORT/'relationship-migration-summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'metadata':len(metadata),'reclassified':len(reclass),'aliases':sum(map(len,duplicates.values()))},indent=2))
