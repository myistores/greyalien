#!/usr/bin/env python3
"""Validate and ingest one podcast episode, then rebuild all generated indexes."""
from pathlib import Path
import json, shutil, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
if len(sys.argv)!=2: raise SystemExit('Usage: python tools/ingest_podcast_episode.py path/to/episode.json')
src=Path(sys.argv[1]).resolve(); data=json.loads(src.read_text(encoding='utf-8'))
required=('id','type','name','summary','date','seriesId','episodeNumber','relationships','referenceSources')
missing=[k for k in required if data.get(k) in (None,'',[])]
if missing: raise SystemExit('Missing required podcast fields: '+', '.join(missing))
if data['type']!='podcast_episode': raise SystemExit('type must be podcast_episode')
if not any(r.get('type')=='episode_of' and r.get('target')==data['seriesId'] for r in data['relationships']): raise SystemExit('episode_of relationship must match seriesId')
if not any(r.get('role') in ('host','co_host') for r in data['relationships']): raise SystemExit('At least one host/co_host relationship is required')
dst=ROOT/'data/entities'/f"{data['id']}.json"
if dst.exists(): shutil.copy2(dst,dst.with_suffix('.json.bak'))
shutil.copy2(src,dst)
for script in ('build_graph.py','build_podcasts.py','build_sitemap.py','validate_graph.py','validate_podcasts.py'):
    subprocess.run([sys.executable,str(ROOT/'tools'/script)],check=True)
print(f'Ingested {data["id"]} and rebuilt generated assets.')
