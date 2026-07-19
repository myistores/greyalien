#!/usr/bin/env python3
"""Validate universal structured sources and official-site coverage."""
from pathlib import Path
from urllib.parse import urlparse
import json,sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]; warnings=[]; checked=0; official=0
for p in sorted((ROOT/'data/entities').glob('*.json')):
 e=json.loads(p.read_text(encoding='utf-8')); sources=e.get('sources',[])
 if not isinstance(sources,list): errors.append(f"{e.get('id')}: sources must be an array"); continue
 primaries=0
 for i,s in enumerate(sources):
  checked+=1
  if not isinstance(s,dict) or not s.get('label') or not s.get('url') or not s.get('sourceType'):
   errors.append(f"{e.get('id')}: source {i+1} requires label, url, and sourceType"); continue
  u=urlparse(s['url'])
  if u.scheme not in ('http','https') or not u.netloc: errors.append(f"{e.get('id')}: invalid source URL {s['url']}")
  if s.get('primary'): primaries+=1
  if s.get('sourceType')=='official_website': official+=1
 if sources and primaries==0: warnings.append(f"{e.get('id')}: sources present but none marked primary")
 if primaries>1: warnings.append(f"{e.get('id')}: multiple primary sources")
 if e.get('type') in ('organization','podcast_series') and sources and not any(s.get('sourceType')=='official_website' for s in sources if isinstance(s,dict)):
  warnings.append(f"{e.get('id')}: no official_website source recorded")
print(f"Source validation: {checked} links checked, {official} official websites, {len(errors)} errors, {len(warnings)} warnings.")
for x in errors: print('ERROR:',x)
for x in warnings: print('WARNING:',x)
sys.exit(1 if errors else 0)
