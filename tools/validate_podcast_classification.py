#!/usr/bin/env python3
"""Validate the V23 engine, configuration, schema, and classified live records."""
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]; warnings=[]
try: cfg=json.loads((ROOT/'data/podcast-classification-config.json').read_text(encoding='utf-8'))
except Exception as ex: errors.append(f'Invalid classification config: {ex}'); cfg={}
try: json.loads((ROOT/'data/podcast-classification-schema.json').read_text(encoding='utf-8'))
except Exception as ex: errors.append(f'Invalid classification schema: {ex}')
for k in ('engineVersion','contentClasses','episodeTypes','topics','researchSignals','catalogSignals','typeSignals'):
    if k not in cfg: errors.append(f'Config missing {k}')
valid_classes={'research','standard','catalog'}
classified=0
for p in (ROOT/'data/entities').glob('*.json'):
    try: e=json.loads(p.read_text(encoding='utf-8'))
    except Exception: continue
    if e.get('type')!='podcast_episode' or 'classification' not in e: continue
    classified+=1; c=e['classification']; eid=e.get('id',p.stem)
    if c.get('contentClass') not in valid_classes: errors.append(f'{eid}: invalid contentClass')
    if c.get('reviewRequired') is not False: warnings.append(f'{eid}: live record still requires classification review')
    if not isinstance(c.get('primaryTopics'),list): errors.append(f'{eid}: primaryTopics must be array')
print(f'Podcast classification validation: {len(errors)} error(s), {len(warnings)} warning(s), {classified} classified live record(s).')
for x in errors: print('ERROR:',x)
for x in warnings: print('WARNING:',x)
sys.exit(1 if errors else 0)
