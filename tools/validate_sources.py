#!/usr/bin/env python3
"""Validate the separation of entity-owned official links and research reference sources."""
from pathlib import Path
from urllib.parse import urlparse
import json,sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]; warnings=[]; official_count=0; reference_count=0
for p in sorted((ROOT/'data/entities').glob('*.json')):
    e=json.loads(p.read_text(encoding='utf-8')); eid=e.get('id',p.stem)
    official=e.get('officialLinks',[]); refs=e.get('referenceSources',[])
    if not isinstance(official,list): errors.append(f'{eid}: officialLinks must be an array'); official=[]
    if not isinstance(refs,list): errors.append(f'{eid}: referenceSources must be an array'); refs=[]
    seen=set()
    for kind,items,required_type in [('official link',official,'linkType'),('reference source',refs,'sourceType')]:
        for i,s in enumerate(items):
            if not isinstance(s,dict) or not s.get('label') or not s.get('url') or not s.get(required_type):
                errors.append(f'{eid}: {kind} {i+1} requires label, url, and {required_type}'); continue
            u=urlparse(s['url'])
            if u.scheme not in ('http','https') or not u.netloc: errors.append(f'{eid}: invalid URL {s["url"]}')
            key=s['url'].rstrip('/').lower()
            if key in seen: warnings.append(f'{eid}: duplicate URL across source fields: {s["url"]}')
            seen.add(key)
            if kind=='official link': official_count+=1
            else: reference_count+=1
    if e.get('type')=='podcast_series' and not official:
        errors.append(f'{eid}: podcast series requires at least one official link')
    if e.get('type')=='organization' and not official:
        warnings.append(f'{eid}: no verified official links recorded')
    if 'sources' in e: errors.append(f'{eid}: legacy sources field must be migrated')
print(f'Link architecture validation: {official_count} official links, {reference_count} reference sources, {len(errors)} errors, {len(warnings)} warnings.')
for x in errors: print('ERROR:',x)
for x in warnings: print('WARNING:',x)
sys.exit(1 if errors else 0)
