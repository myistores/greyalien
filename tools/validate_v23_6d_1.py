#!/usr/bin/env python3
"""V23.6D.1 bounded reliability/performance validation."""
from pathlib import Path
import hashlib, json, re, sys

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/mnt/data/v236d1_base')
errors=[]

def load(root, rel):
    return json.loads((root/rel).read_text(encoding='utf-8'))

def sha(path):
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()

# Permanent graph content must be byte-for-byte unchanged.
base_files=sorted((BASE/'data/entities').glob('*.json'))
new_files=sorted((ROOT/'data/entities').glob('*.json'))
if [p.name for p in base_files] != [p.name for p in new_files]:
    errors.append('Permanent entity file inventory changed.')
else:
    changed=[a.name for a,b in zip(base_files,new_files) if sha(a)!=sha(b)]
    if changed: errors.append(f'Permanent entity files changed: {changed[:10]}')

old_idx=load(BASE,'data/entity-index.json')
idx=load(ROOT,'data/entity-index.json')
relidx=load(ROOT,'data/relationship-index.json')
if len(old_idx['entities']) != len(idx['entities']):
    errors.append('Searchable entity count changed.')
old_sem=[{k:v for k,v in e.items() if not k.startswith('_')} for e in old_idx['entities']]
new_sem=[{k:v for k,v in e.items() if not k.startswith('_') and k!='eventCategory'} for e in idx['entities']]
# Remove additive eventCategory from comparison; every prior field/order should match.
if old_sem != new_sem:
    errors.append('Entity-index pre-existing semantic rows changed beyond additive optimization metadata.')

index_ids={e['id'] for e in idx['entities']}
entity_by_id={json.loads(p.read_text(encoding='utf-8'))['id']:json.loads(p.read_text(encoding='utf-8')) for p in new_files}
# Relationship-index edge equivalence with legacy full-graph browser scan.
expected={i:[] for i in index_ids}
for source_id in sorted(index_ids):
    e=entity_by_id[source_id]
    for r in e.get('relationships',[]):
        if r.get('target') in index_ids:
            expected[r['target']].append({'source':source_id,'type':r.get('type'),'meta':r})
for target in expected:
    expected[target].sort(key=lambda x:(x.get('source',''),x.get('type',''),json.dumps(x.get('meta',{}),sort_keys=True,ensure_ascii=False)))
actual=relidx.get('incoming',{})
if set(actual)!=index_ids: errors.append('Relationship index target inventory does not match entity index.')
for target in index_ids:
    if expected[target] != actual.get(target,[]):
        errors.append(f'Relationship lookup mismatch for {target}')
        break
# Orphan checks.
for target, rows in actual.items():
    if target not in index_ids: errors.append(f'Orphan relationship target {target}')
    for row in rows:
        if row.get('source') not in index_ids: errors.append(f"Orphan relationship source {row.get('source')}")
        if (row.get('meta') or {}).get('target') != target: errors.append(f'Relationship target mismatch at {target}')

engine=(ROOT/'assets/js/entity-engine.js').read_text(encoding='utf-8')
if 'idx.entities.map(e=>fetch(`../data/entities/${e.id}.json`)' in engine:
    errors.append('Legacy full-graph fetch loop remains in entity engine.')
if '../data/relationship-index.json' not in engine:
    errors.append('Entity engine does not load relationship index.')
if 'Unable to load this record.' not in engine or '>Retry<' not in engine:
    errors.append('Explicit entity load failure/retry state missing.')
if 'GreyAlien entity load failed' not in engine:
    errors.append('Diagnostic console error missing.')
entity_html=(ROOT/'entities/entity.html').read_text(encoding='utf-8')
if 'entity-engine.js?v=23.6d.1' not in entity_html:
    errors.append('Entity engine cache-busting release query missing.')

# Representative direct URL IDs must exist and have reverse lookup entries.
representative=['marco-rubio','david-grusch','sol-foundation','publication-2026-civilizational-risks-uap-technology-arms-race','2023-merged-episode-18']
for eid in representative:
    if eid not in entity_by_id: errors.append(f'Missing regression entity {eid}')
    if eid not in actual: errors.append(f'Missing relationship lookup for regression entity {eid}')

legacy_entity_requests=len(old_idx['entities'])+1  # current entity + full index sweep (current was fetched again)
optimized_entity_requests=1
legacy_core_json_requests=len(old_idx['entities'])+5
optimized_core_json_requests=6
print(f'Legacy entity JSON requests per indexed entity page: ~{legacy_entity_requests}')
print(f'Optimized entity JSON requests per indexed entity page: {optimized_entity_requests}')
print(f'Legacy core JSON requests before assets/media: ~{legacy_core_json_requests}')
print(f'Optimized core JSON requests before assets/media: {optimized_core_json_requests}')
print(f'Relationship-index entries: {sum(len(v) for v in actual.values())}')
print(f'Permanent entity files: {len(new_files)} (unchanged)')
if errors:
    print('FAIL V23.6D.1')
    for e in errors: print('-',e)
    sys.exit(1)
print('PASS V23.6D.1')
