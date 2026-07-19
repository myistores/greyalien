#!/usr/bin/env python3
"""Validate GreyAlien entity files, schema rules, vocabulary, and graph integrity."""
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
ENT=ROOT/'data/entities'
idx=json.loads((ROOT/'data/entity-index.json').read_text(encoding='utf-8'))
schema=json.loads((ROOT/'data/schema/entity-schema-v2.json').read_text(encoding='utf-8'))
vocab=json.loads((ROOT/'data/schema/relationship-vocabulary.json').read_text(encoding='utf-8'))
allowed_types=set(schema['properties']['type']['enum']); required=schema['required']; id_re=re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
errors=[]; warnings=[]; files={p.stem:p for p in ENT.glob('*.json')}; records={}
for stem,p in files.items():
    try: d=json.loads(p.read_text(encoding='utf-8')); records[stem]=d
    except Exception as exc: errors.append(f'{p.name}: invalid JSON ({exc})')
ids=[e.get('id') for e in idx.get('entities',[])]
if len(ids)!=len(set(ids)): errors.append('Duplicate IDs in entity-index.json')
for stem,d in records.items():
    for key in required:
        if key not in d or d[key] in ('',None): errors.append(f'{stem}: missing required field {key}')
    if d.get('id')!=stem: errors.append(f'{stem}: ID/file mismatch ({d.get("id")})')
    if not id_re.match(stem): errors.append(f'{stem}: invalid stable ID format')
    if d.get('type') not in allowed_types: errors.append(f'{stem}: unsupported entity type {d.get("type")}')
    if not isinstance(d.get('relationships',[]),list): errors.append(f'{stem}: relationships must be an array'); continue
    for n,rel in enumerate(d.get('relationships',[]),1):
        if not isinstance(rel,dict): errors.append(f'{stem}: relationship {n} is not an object'); continue
        if rel.get('type') not in vocab: errors.append(f'{stem}: unknown relationship type {rel.get("type")}')
        target=rel.get('target')
        if not target: errors.append(f'{stem}: relationship {n} missing target')
        elif target not in records: warnings.append(f'{stem}: unresolved legacy target {target}')
for eid in ids:
    if eid not in files: errors.append(f'Missing entity file: {eid}.json')
for stem in files:
    if stem not in ids: errors.append(f'Entity omitted from index: {stem}')
print(f'Checked {len(records)} entities and {sum(len(d.get("relationships",[])) for d in records.values())} declared relationships.')
if warnings: print(f'Warnings: {len(warnings)} unresolved legacy relationship targets remain.')
if errors:
    print('VALIDATION FAILED'); print('\n'.join('- '+e for e in errors[:100])); sys.exit(1)
print('VALIDATION PASSED')
