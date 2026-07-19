#!/usr/bin/env python3
from pathlib import Path
import json
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parents[1]
idx=json.loads((ROOT/'data/entity-index.json').read_text(encoding='utf-8'))
static=['','about.html','categories/congressional-hearings.html','categories/whistleblower-database.html','categories/podcasts.html','categories/latest-uap-news.html','categories/space-exploration.html','categories/science-technology.html','categories/movies-documentaries.html','categories/research-library.html','entities/index.html']
urls=['https://greyalien.com/'+p for p in static]+[f'https://greyalien.com/entities/entity.html?id={e["id"]}' for e in idx['entities']]
body='\n'.join(f'  <url><loc>{escape(u)}</loc></url>' for u in urls)
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+body+'\n</urlset>\n',encoding='utf-8')
print(f'Built sitemap with {len(urls)} URLs.')
