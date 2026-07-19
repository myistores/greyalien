#!/usr/bin/env python3
"""Validate timeline normalization configuration and known duplicate-event prevention."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
entities={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'data/entities').glob('*.json')}
path=ROOT/'data/timeline-normalization.json'
errors=[]
if not path.exists(): errors.append('Missing data/timeline-normalization.json')
else:
 d=json.loads(path.read_text(encoding='utf-8')); aliases=d.get('aliases',{})
 if d.get('conflicts'): errors.append(f"Normalization conflicts present: {len(d['conflicts'])}")
 for alias,canonical in aliases.items():
  a=entities.get(alias); c=entities.get(canonical)
  if not a: errors.append(f'Missing alias entity: {alias}'); continue
  if not c or c.get('type')!='timeline_event': errors.append(f'Canonical target is not a timeline_event: {canonical}'); continue
  if a.get('date') and c.get('date') and a['date']!=c['date']: errors.append(f'Date mismatch: {alias} -> {canonical}')
 # Required regression pairs discovered during V17.4 testing.
 expected={
  '2018-bob-lazar-area-51-flying-saucers':'timeline-2018-12-04-bob-lazar-documentary-release',
  '2026-weaponized-episode-115':'timeline-2026-04-14-weaponized-episode-115'
 }
 for alias,canonical in expected.items():
  if alias in entities and canonical in entities and aliases.get(alias)!=canonical:
   errors.append(f'Regression mapping missing: {alias} -> {canonical}')
engine=(ROOT/'assets/js/entity-engine.js').read_text(encoding='utf-8')
for token in ['timeline-normalization.json','Unique connections','canonicalTimelineId']:
 if token not in engine: errors.append(f'Entity renderer missing integration token: {token}')
if errors:
 print('Timeline normalization validation: FAILED')
 for e in errors: print(' -',e)
 raise SystemExit(1)
print(f"Timeline normalization validation: PASSED ({len(json.loads(path.read_text())['aliases'])} aliases).")
