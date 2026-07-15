#!/usr/bin/env python3
"""Validate GreyAlien entity IDs and relationship targets.
Legacy unresolved targets are reported as warnings so they can be cleaned up gradually.
"""
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
idx=json.loads((ROOT/'data/entity-index.json').read_text())
ids=[e['id'] for e in idx['entities']]
errors=[]; warnings=[]
if len(ids)!=len(set(ids)):
    errors.append('Duplicate IDs in entity-index.json')
files={p.stem:p for p in (ROOT/'data/entities').glob('*.json')}
for eid in ids:
    if eid not in files:
        errors.append(f'Missing entity file: {eid}.json')
for eid,p in files.items():
    d=json.loads(p.read_text())
    if d.get('id')!=eid:
        errors.append(f'ID/file mismatch: {p.name}')
    for rel in d.get('relationships',[]):
        if rel.get('target') not in files:
            warnings.append(f"{eid}: unresolved legacy target {rel.get('target')}")
if warnings:
    print(f'Warnings: {len(warnings)} unresolved relationship targets remain for future cleanup.')
if errors:
    print('VALIDATION FAILED')
    print('\n'.join('- '+e for e in errors))
    sys.exit(1)
print(f'Graph structure valid: {len(files)} entity files, {len(ids)} indexed entities.')
