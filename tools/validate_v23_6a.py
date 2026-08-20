#!/usr/bin/env python3
from pathlib import Path
import json, sys
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
errors=[]
def check(cond,msg):
    if not cond: errors.append(msg)
idx=json.loads((ROOT/'data/news/index.json').read_text(encoding='utf-8'))
check(idx.get('records')==['2026-08-19-liberation-times-ufo-disclosure-trump','2026-08-19-scitechdaily-have-we-found-alien-life'],'news index order/records mismatch')
for rid in idx.get('records',[]):
    p=ROOT/'data/news'/f'{rid}.json'
    check(p.exists(),f'missing news record {rid}')
    if not p.exists(): continue
    d=json.loads(p.read_text(encoding='utf-8'))
    check(d.get('recordType')=='news_record',f'{rid}: wrong recordType')
    check(d.get('visibility',{}).get('entityDirectory') is False,f'{rid}: visible in entity directory')
    img=d.get('image',{}).get('sitePath')
    check(bool(img) and (ROOT/img).exists(),f'{rid}: image missing')
    for eid in d.get('relatedEntityIds',[]):
        check((ROOT/'data/entities'/f'{eid}.json').exists(),f'{rid}: missing connected entity {eid}')
page=ROOT/'categories/latest-uap-news.html'
soup=BeautifulSoup(page.read_text(encoding='utf-8'),'html.parser')
arts=soup.select('article.news-entry')
check(len(arts)==2,'gateway should render exactly two news entries')
for n,art in enumerate(arts,1):
    check(art.select_one('.news-image img') is not None,f'article {n}: image absent')
    src=art.select_one('.news-source-link'); related=art.select_one('.news-related')
    check(src is not None and related is not None,f'article {n}: source/related block missing')
    if src and related: check(src.sourceline < related.sourceline,f'article {n}: original source link not before Connected Research')
    for a in art.select('a.topic-chip'):
        eid=a.get('href','').split('id=')[-1]
        check((ROOT/'data/entities'/f'{eid}.json').exists(),f'article {n}: broken entity link {eid}')
if errors:
    print('V23.6A VALIDATION FAILED')
    for e in errors: print('-',e)
    sys.exit(1)
print('V23.6A VALIDATION PASSED')
print('News records: 2')
print('New permanent entities: 0')
