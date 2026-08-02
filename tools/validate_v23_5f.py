#!/usr/bin/env python3
from pathlib import Path
import json, sys, hashlib
ROOT=Path(__file__).resolve().parents[1]; BASE=Path('/mnt/data/v235e1_baseline'); REPORT=ROOT/'reports/v23-5f'; REPORT.mkdir(parents=True,exist_ok=True)
cfg=json.loads((ROOT/'data/topic-taxonomy-v23-5f.json').read_text())
cur={p.stem:json.loads(p.read_text()) for p in (ROOT/'data/entities').glob('*.json')}
old={p.stem:json.loads(p.read_text()) for p in (BASE/'data/entities').glob('*.json')}
approved=set(cfg['supportingClassifications'])|set(cfg['reclassifications'])
alias_map={}
for canonical,aliases in cfg['duplicateClusters'].items():
 approved.add(canonical); approved.update(aliases); alias_map.update({a:canonical for a in aliases})
for src,spec in cfg['reclassifications'].items():
 if spec.get('target'): approved.add(spec['target']); alias_map[src]=spec['target']

def canon(x):
 while x in alias_map: x=alias_map[x]
 return x

def edges(es):
 out=[]
 for sid,e in es.items():
  if e.get('taxonomyStatus')=='alias': continue
  for r in e.get('relationships',[]): out.append((canon(sid),r.get('type'),canon(r.get('target')),r.get('role'),r.get('context'),r.get('timeline')))
 return out
old_edges=set(edges(old)); new_edges=set(edges(cur)); missing=sorted(old_edges-new_edges); added=sorted(new_edges-old_edges)
# Only entity records that are approved or that reference an approved migrated target may change.
unapproved_content=[]
for eid in sorted(set(old)&set(cur)):
 if eid in approved: continue
 a=old[eid]; b=cur[eid]
 if a==b: continue
 aa=dict(a); bb=dict(b); aa.pop('relationships',None); bb.pop('relationships',None)
 if aa!=bb: unapproved_content.append(eid)
# references: preserve legacy baseline; fail only on newly introduced unresolved targets
ids=set(cur); unresolved=[]
for sid,e in cur.items():
 for r in e.get('relationships',[]):
  if r.get('target') not in ids: unresolved.append({'source':sid,'target':r.get('target'),'type':r.get('type')})
old_ids=set(old); old_unresolved={(sid,r.get('target'),r.get('type')) for sid,e in old.items() for r in e.get('relationships',[]) if r.get('target') not in old_ids}
new_unresolved=[x for x in unresolved if (x['source'],x['target'],x['type']) not in old_unresolved]
idx=json.loads((ROOT/'data/entity-index.json').read_text()); index_ids=[e['id'] for e in idx['entities']]
duplicates=len(index_ids)-len(set(index_ids))
supporting_visible=[e['id'] for e in idx['entities'] if e['id'] in cfg['supportingClassifications'] and e.get('visibleInDirectory') is not False]
alias_index=[a for a in alias_map if a in index_ids]
redirect_missing=[a for a,t in alias_map.items() if not (ROOT/f'entities/generated/{a}.html').exists()]
validation={
 'release':'V23.5F','status':'PASS' if not(missing or added or new_unresolved or unapproved_content or duplicates or supporting_visible or alias_index or redirect_missing) else 'FAIL',
 'entityCountBefore':len(old),'entityCountAfter':len(cur),'logicalRelationshipsBefore':len(old_edges),'logicalRelationshipsAfter':len(new_edges),
 'missingLogicalRelationships':missing,'newLogicalRelationships':added,'baselineUnresolvedRelationshipCount':len(old_unresolved),'currentUnresolvedRelationshipCount':len(unresolved),'newUnresolvedRelationships':new_unresolved,
 'unapprovedEntityContentChanges':unapproved_content,'duplicateIndexIds':duplicates,'supportingClassificationsVisible':supporting_visible,
 'legacyAliasesInSearchIndex':alias_index,'missingRedirectPages':redirect_missing,
 'schemaFilesChanged': sorted(str(p.relative_to(ROOT)) for p in (ROOT/'data/schema').glob('*') if (BASE/p.relative_to(ROOT)).exists() and p.read_bytes()!=(BASE/p.relative_to(ROOT)).read_bytes()),
 'approvedTopicEntitiesChanged':sorted(approved),'aliasMap':alias_map
}
(REPORT/'validation-report.json').write_text(json.dumps(validation,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(validation,indent=2,ensure_ascii=False)); sys.exit(0 if validation['status']=='PASS' else 1)
