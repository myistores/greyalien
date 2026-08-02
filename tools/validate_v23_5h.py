#!/usr/bin/env python3
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
errors=[]
index=(ROOT/'index.html').read_text(encoding='utf-8')
dev=(ROOT/'development-updates.html').read_text(encoding='utf-8')
entities=json.loads((ROOT/'data/entity-index.json').read_text(encoding='utf-8'))['entities']
podcasts=json.loads((ROOT/'data/podcasts/podcast-index.json').read_text(encoding='utf-8'))['podcasts']
episodes=json.loads((ROOT/'data/podcasts/episode-index.json').read_text(encoding='utf-8'))['episodes']
counts={}
for e in entities: counts[e['type']]=counts.get(e['type'],0)+1
for required in ['V23.5G','V23.5F','Connected research','development-updates.html','V23.5H — Homepage Refresh']:
    if required not in index: errors.append(f'missing homepage content: {required}')
for forbidden in ['Coming Soon...','V23.5C.1:</strong> Built the universal podcast media-audit engine']:
    if forbidden in index: errors.append(f'obsolete homepage content remains: {forbidden}')
for value in [len(entities),len(counts),counts.get('person',0),counts.get('hearing',0),len(episodes),len(podcasts)]:
    if f'>{value:,}<' not in index: errors.append(f'missing generated metric: {value:,}')
if index.count('class="latest-item update-card"') != 3: errors.append('homepage does not contain exactly three update cards')
if 'Complete release history' not in dev or 'V23.5H' not in dev or 'V23.5F' not in dev: errors.append('development history page is incomplete')
if 'development-updates.html' not in (ROOT/'sitemap.xml').read_text(encoding='utf-8'): errors.append('development page missing from sitemap')
release=json.loads((ROOT/'data/release-summary.json').read_text(encoding='utf-8'))
if release.get('version')!='V23.5H': errors.append('release-summary.json is not V23.5H')
if errors:
    print('V23.5H validation: FAILED')
    for error in errors: print('-',error)
    raise SystemExit(1)
print('V23.5H validation: PASSED')
print(f'- {len(entities):,} entities / {len(counts)} entity types')
print(f'- {counts.get("person",0):,} people / {counts.get("hearing",0):,} hearings')
print(f'- {len(episodes):,} podcast episodes / {len(podcasts)} podcast series')
print('- Exactly three visitor-facing update cards')
print('- Dedicated complete development-history page')
print('- No repeated Coming Soon entries or obsolete V23.5C.1 notice')
