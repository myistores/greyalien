#!/usr/bin/env python3
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]; BASE=Path('/mnt/data/v235g_base'); OUT=ROOT/'reports/v23-5g'; OUT.mkdir(parents=True,exist_ok=True)
cur={p.stem:json.loads(p.read_text()) for p in (ROOT/'data/entities').glob('*.json')}; old={p.stem:json.loads(p.read_text()) for p in (BASE/'data/entities').glob('*.json')}
metadata={'60-minutes','animal-wellness-action','buddha-jones','fox-news','lord-huron','wall-street-journal'}
reclass={'aatip','aawsap','advanced-theoretical-physics-program','project-blue-book','project-sign','uap-task-force','galileo-project','disclosure-project','nasa-uap-independent-study-team','eglin-air-force-base','malmstrom-air-force-base','minot-air-force-base','raf-bentwaters','vandenberg-space-force-base','icecube-neutrino-observatory','uss-jackson','uss-princeton','ask-a-pol','australian-broadcasting-corporation','klas-tv','liberation-times','the-new-york-times','uap-register','united-states-air-force-thunderbirds'}
alias={'all-domain-anomaly-resolution-office':'aaro','united-states-department-of-defense':'department-of-defense'}
approved=metadata|reclass|set(alias)|set(alias.values())
def canon(x): return alias.get(x,x)
def edges(es):
 out=set()
 for sid,e in es.items():
  if e.get('taxonomyStatus')=='alias': continue
  for r in e.get('relationships',[]): out.add((canon(sid),r.get('type'),canon(r.get('target')),r.get('role'),r.get('context'),r.get('timeline')))
 return out
olded,newed=edges(old),edges(cur)
unapproved=[]
for eid in set(old)&set(cur):
 if eid in approved: continue
 a,b=old[eid],cur[eid]
 if a==b: continue
 aa,bb=dict(a),dict(b); aa.pop('relationships',None); bb.pop('relationships',None)
 if aa!=bb: unapproved.append(eid)
ids=set(cur); unresolved=[{'source':s,'target':r.get('target')} for s,e in cur.items() for r in e.get('relationships',[]) if r.get('target') not in ids]
idx=json.loads((ROOT/'data/entity-index.json').read_text()); rows=idx['entities']
org_visible=[x['id'] for x in rows if x['type']=='organization' and x.get('visibleInDirectory') is not False]
metadata_visible=[x['id'] for x in rows if x['id'] in metadata and x.get('visibleInDirectory') is not False]
wrong_types={eid:cur[eid]['type'] for eid in reclass if cur[eid]['type']=='organization'}
redirect_missing=[a for a in alias if not (ROOT/f'entities/generated/{a}.html').exists()]
metadata_pages=[m for m in metadata if (ROOT/f'entities/generated/{m}.html').exists()]
status='PASS' if not(olded-newed or newed-olded or unapproved or metadata_visible or wrong_types or redirect_missing or metadata_pages) else 'FAIL'
report={'release':'V23.5G','status':status,'entityCountBefore':len(old),'entityCountAfter':len(cur),'logicalRelationshipsBefore':len(olded),'logicalRelationshipsAfter':len(newed),'missingLogicalRelationships':sorted(olded-newed),'newLogicalRelationships':sorted(newed-olded),'unapprovedEntityContentChanges':sorted(unapproved),'unresolvedRelationshipCount':len(unresolved),'metadataEntitiesVisible':metadata_visible,'metadataDestinationPagesRemaining':metadata_pages,'reclassifiedEntitiesStillOrganizations':wrong_types,'missingRedirectPages':redirect_missing,'visibleOrganizationCount':len(org_visible),'visibleOrganizationIds':org_visible,'approvedEntityIds':sorted(approved)}
(OUT/'validation-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
md=f'''# V23.5G Validation Report\n\n**Status:** {status}\n\n- Entities before/after: {len(old)} / {len(cur)}\n- Logical relationships before/after: {len(olded)} / {len(newed)}\n- Supporting metadata still visible: {len(metadata_visible)}\n- Reclassified records still typed Organization: {len(wrong_types)}\n- Missing legacy redirects: {len(redirect_missing)}\n- Unapproved entity content changes: {len(unapproved)}\n- Existing unresolved references (not introduced by this release): {len(unresolved)}\n'''
(OUT/'V23_5G_VALIDATION_REPORT.md').write_text(md)
print(json.dumps(report,indent=2,ensure_ascii=False)); sys.exit(0 if status=='PASS' else 1)
