#!/usr/bin/env python3
"""Validate structured visual identity records and local assets."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]; warnings=[]
for p in (ROOT/'data/entities').glob('*.json'):
    try: d=json.loads(p.read_text())
    except Exception: continue
    v=d.get('visualIdentity')
    if not v: continue
    for key in ('asset','alt'):
        if not v.get(key): errors.append(f'{d.get("id")}: visualIdentity.{key} missing')
    asset=v.get('asset','').replace('../','',1)
    if asset and not (ROOT/asset).exists(): errors.append(f'{d.get("id")}: visual asset not found: {asset}')
    if d.get('type')=='podcast_series' and not (v.get('hosts') or d.get('podcastHosts')): warnings.append(f'{d.get("id")}: no hosts supplied for visual identity')
print(f'Visual identity validation: {len(errors)} error(s), {len(warnings)} warning(s).')
for x in errors: print('ERROR:',x)
for x in warnings: print('WARNING:',x)
sys.exit(1 if errors else 0)
