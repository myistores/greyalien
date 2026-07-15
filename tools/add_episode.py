#!/usr/bin/env python3
"""Add a completed podcast-episode JSON file to the entity index and sitemap.
Usage: python tools/add_episode.py path/to/episode.json
"""
from pathlib import Path
import json, shutil, sys
ROOT=Path(__file__).resolve().parents[1]
if len(sys.argv)!=2:
    raise SystemExit('Usage: python tools/add_episode.py episode.json')
src=Path(sys.argv[1]); data=json.loads(src.read_text())
required=['id','type','name','summary']
missing=[k for k in required if not data.get(k)]
if missing: raise SystemExit('Missing required fields: '+', '.join(missing))
dst=ROOT/'data/entities'/f"{data['id']}.json"
shutil.copyfile(src,dst)
idxp=ROOT/'data/entity-index.json'; idx=json.loads(idxp.read_text())
if not any(e['id']==data['id'] for e in idx['entities']):
    idx['entities'].append({k:data.get(k,'') for k in ['id','type','name','summary','date']})
    order={t:i for i,t in enumerate(idx.get('entityTypes',[]))}
    idx['entities'].sort(key=lambda e:(order.get(e['type'],999),e['name'].lower(),e['id']))
    idxp.write_text(json.dumps(idx,indent=2,ensure_ascii=False)+'\n')
smp=ROOT/'sitemap.xml'; text=smp.read_text(); url=f"https://greyalien.com/entities/entity.html?id={data['id']}"
if url not in text:
    text=text.replace('</urlset>',f'  <url>\n    <loc>{url}</loc>\n  </url>\n</urlset>')
    smp.write_text(text)
print(f"Added {data['id']}")
