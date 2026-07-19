#!/usr/bin/env python3
"""Generate stable, crawlable HTML entry points for every knowledge-graph entity."""
from pathlib import Path
import json, html, shutil
ROOT=Path(__file__).resolve().parents[1]
ENT=ROOT/'data/entities'; OUT=ROOT/'entities/generated'
OUT.mkdir(parents=True, exist_ok=True)
valid=set()
for p in sorted(ENT.glob('*.json')):
    e=json.loads(p.read_text(encoding='utf-8')); eid=e['id']; valid.add(eid)
    title=html.escape(e.get('name',eid)); summary=html.escape(e.get('summary','GreyAlien connected knowledge-base record.'))
    type_label=html.escape(e.get('type','entity').replace('_',' ').title())
    canonical=f'https://greyalien.com/entities/generated/{eid}.html'
    doc=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | GreyAlien</title><meta name="description" content="{summary[:300]}">
<link rel="canonical" href="{canonical}"><link rel="stylesheet" href="../../style.css">
<meta property="og:title" content="{title} | GreyAlien"><meta property="og:description" content="{summary[:300]}">
<script>location.replace('../entity.html?id='+encodeURIComponent({json.dumps(eid)}));</script></head>
<body><main><section class="page-hero"><div class="wrap"><p class="kicker">{type_label}</p><h1>{title}</h1><p>{summary}</p><p><a class="button" href="../entity.html?id={html.escape(eid)}">Open connected record</a></p></div></section></main></body></html>'''
    (OUT/f'{eid}.html').write_text(doc,encoding='utf-8')
for old in OUT.glob('*.html'):
    if old.stem not in valid: old.unlink()
print(f'Generated {len(valid)} stable entity pages.')
