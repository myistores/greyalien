#!/usr/bin/env python3
"""Validate podcast-series and episode records and their graph semantics."""
from pathlib import Path
import json, re, sys
ROOT=Path(__file__).resolve().parents[1]; ENT=ROOT/'data/entities'
records={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in ENT.glob('*.json')}
errors=[]; warnings=[]; episodes=[]
for eid,e in records.items():
    ep=[r for r in e.get('relationships',[]) if r.get('type')=='episode_of']
    if e.get('type')=='podcast_episode' or ep:
        episodes.append(e)
        if e.get('type')!='podcast_episode': warnings.append(f'{eid}: legacy type {e.get("type")} should be podcast_episode')
        if len(ep)!=1: errors.append(f'{eid}: expected exactly one episode_of relationship')
        sid=e.get('seriesId') or (ep[0].get('target') if ep else None)
        if sid not in records or records.get(sid,{}).get('type')!='podcast_series': errors.append(f'{eid}: invalid podcast series {sid}')
        if e.get('seriesId') and ep and e['seriesId']!=ep[0].get('target'): errors.append(f'{eid}: seriesId and episode_of target disagree')
        for k in ('date','episodeNumber'):
            if e.get(k) in (None,''): warnings.append(f'{eid}: missing recommended field {k}')
        if not e.get('referenceSources'): warnings.append(f'{eid}: no referenceSources array')
        hosts=[r for r in e.get('relationships',[]) if r.get('role') in ('host','co_host')]
        if not hosts: errors.append(f'{eid}: at least one host relationship is required')
        claims=[r for r in e.get('relationships',[]) if r.get('type') in ('presented_claim','contains_claim')]
        if len(claims)>7: warnings.append(f'{eid}: {len(claims)} principal claims exceeds the 3–7 editorial standard')
for p in (e for e in records.values() if e.get('type')=='podcast_series'):
    if not p.get('podcastHosts'): errors.append(f'{p["id"]}: podcastHosts is required')
print(f'Checked {sum(1 for e in records.values() if e.get("type")=="podcast_series")} series and {len(episodes)} episodes.')
if warnings:
    print(f'Warnings: {len(warnings)}'); print('\n'.join('- '+w for w in warnings[:100]))
if errors:
    print('PODCAST VALIDATION FAILED'); print('\n'.join('- '+e for e in errors[:100])); sys.exit(1)
print('PODCAST VALIDATION PASSED')
