#!/usr/bin/env python3
from pathlib import Path
import json, hashlib, sys
from PIL import Image
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
errors=[]

def err(msg): errors.append(msg)

def load(rel):
    return json.loads((ROOT/rel).read_text(encoding='utf-8'))

paper_id='publication-2026-civilizational-risks-uap-technology-arms-race'
news_id='2026-08-20-sol-foundation-uap-technology-arms-race'
expected_existing=[
'2026-08-21-ufo-chronicles-marco-rubio-uap',
'2026-08-20-debrief-pursue-video-analysis',
'2026-08-19-liberation-times-ufo-disclosure-trump',
'2026-08-19-scitechdaily-have-we-found-alien-life']

# Permanent entity and count discipline
ent_dir=ROOT/'data/entities'
entity_files=list(ent_dir.glob('*.json'))
if len(entity_files)!=1611: err(f'Expected 1611 permanent entity files, found {len(entity_files)}')
if not (ent_dir/f'{paper_id}.json').exists(): err('Permanent policy-paper entity missing')
paper=load(f'data/entities/{paper_id}.json')
if paper.get('type')!='publication': err('Policy paper must use existing publication entity type')
if paper.get('entitySubtype')!='policy_paper': err('Policy paper entity subtype missing')
rels={(r.get('type'),r.get('target')) for r in paper.get('relationships',[])}
for expected in [
('references_person','marik-von-rennenkampff'),('published_by','sol-foundation'),
('references_topic','national-security-secrecy'),('references_topic','non-human-intelligence'),
('references_topic','reverse-engineering'),('references_topic','uap-disclosure')]:
    if expected not in rels: err(f'Missing publication relationship {expected}')

idx=load('data/entity-index.json')
idx_ids={x['id'] for x in idx.get('entities',[])}
if paper_id not in idx_ids: err('Permanent policy paper missing from entity index')
if news_id in idx_ids: err('News Record incorrectly appears in public entity index')

# Existing Organization/Person reused rather than duplicated.
for eid in ('sol-foundation','marik-von-rennenkampff'):
    if eid not in idx_ids: err(f'Existing entity not reused: {eid}')

# News record + ordering
news=load(f'data/news/{news_id}.json')
if news.get('recordType')!='news_record': err('New current record is not a news_record')
if news.get('contentType')!='research_policy_paper': err('Research/policy content type not preserved')
if news.get('primarySourceUrl','').endswith('.pdf') is False: err('Primary PDF source missing from news record')
if paper_id not in news.get('relatedEntityIds',[]): err('News Record does not connect to permanent publication')
ni=load('data/news/index.json').get('records',[])
expected_order=[expected_existing[0],news_id,expected_existing[1],expected_existing[2],expected_existing[3]]
if ni!=expected_order: err(f'Unexpected news ordering: {ni}')

# Protected prior news records/assets unchanged.
hashes=load('data/v23-6d-protected-hashes.json')
for rel, expected_hash in hashes.items():
    p=ROOT/rel
    if not p.exists(): err(f'Protected file missing: {rel}'); continue
    got=hashlib.sha256(p.read_bytes()).hexdigest()
    if got!=expected_hash: err(f'Protected prior V23.6C content changed: {rel}')

# Gateway rendering structure.
news_html=(ROOT/'categories/latest-uap-news.html').read_text(encoding='utf-8')
news_soup=BeautifulSoup(news_html,'html.parser')
entries=news_soup.select('article.news-entry')
if len(entries)!=5: err(f'Latest UAP News should contain 5 records, found {len(entries)}')
if paper_id not in news_html: err('Latest UAP News does not expose permanent research-record connection')
if 'Read Original Paper →' not in news_html: err('News gateway missing Read Original Paper action')

research_html=(ROOT/'categories/research-library.html').read_text(encoding='utf-8')
research_soup=BeautifulSoup(research_html,'html.parser')
if len(research_soup.select('article.research-entry'))!=1: err('Research Library should contain exactly one research record')
for obsolete in ('Foundation structure','First content coming next','GreyAlien Version 2 establishes the structure'):
    if obsolete in research_html: err(f'Obsolete Research Library placeholder remains: {obsolete}')
if paper_id not in research_html: err('Research Library does not link to permanent publication record')
if 'Policy-Paper-UAP-Arms-Race-Volume2-8.20.26-1.pdf' not in research_html: err('Research Library does not link to original Sol Foundation PDF')

ridx=load('data/research-library/index.json')
if ridx.get('records')!=[paper_id]: err('Research Library data index must contain only the first permanent paper')

# Local image and dimensions.
image_path=ROOT/'assets/news/sol-uap-arms-race-2026-08.jpg'
if not image_path.exists(): err('Locally hosted news image missing')
else:
    with Image.open(image_path) as im:
        if im.size!=(1400,788): err(f'Unexpected new news image dimensions {im.size}')

# Connected Research targets resolve for both gateway pages.
for page in (news_soup,research_soup):
    for a in page.select('a.topic-chip[href*="../entities/entity.html?id="]'):
        eid=a['href'].split('id=',1)[1]
        if not (ent_dir/f'{eid}.json').exists(): err(f'Broken Connected Research target: {eid}')

# Inherited V23.6C source-validation repair is narrow and present.
rubio=load('data/entities/marco-rubio.json')
rubio_links=[x for x in rubio.get('officialLinks',[]) if x.get('url')=='https://history.state.gov/departmenthistory/people/rubio-marco']
if not rubio_links or rubio_links[0].get('linkType')!='official_biography': err('Inherited Marco Rubio official-link validation defect not repaired')

# Release documentation.
for rel in ('V23_6D_LATEST_UAP_NEWS_RESEARCH_LIBRARY_CROSS_GATEWAY_INGESTION.md','V23_6D_NEW_ENTITY_REVIEW.md'):
    if not (ROOT/rel).exists(): err(f'Missing release document: {rel}')

if errors:
    print('V23.6D VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('V23.6D VALIDATION PASSED')
print(f'- Permanent entity files: {len(entity_files)}')
print('- New permanent entities: 1 (Publication)')
print('- Latest UAP News records: 5')
print('- Research Library records: 1')
print('- Prior four news records/assets: byte-for-byte preserved')
