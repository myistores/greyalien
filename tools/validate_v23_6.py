#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

def check(ok, msg):
    if not ok:
        errors.append(msg)

page = (ROOT / 'categories/latest-uap-news.html').read_text(encoding='utf-8')
check('Current reporting on UAP, extraterrestrial life, space science, government activity and related research.' in page, 'Updated gateway introduction missing')
check('Foundation structure' not in page, 'Foundation structure placeholder still present')
check('First content coming next' not in page, 'First content placeholder still present')
check('Have We Found Alien Life? Here’s What Scientists Really Think' in page, 'Article headline missing')
check('SciTechDaily · August 19, 2026' in page, 'Source/date missing')
source_url = 'https://scitechdaily.com/have-we-found-alien-life-heres-what-scientists-really-think/'
check(source_url in page, 'Original source URL missing')
check('Connected Research' in page, 'Connected Research section missing')

record_path = ROOT / 'data/news/2026-08-19-scitechdaily-have-we-found-alien-life.json'
check(record_path.exists(), 'News Record missing')
if record_path.exists():
    record = json.loads(record_path.read_text(encoding='utf-8'))
    required = ['title','source','publicationDate','originalUrl','summary','dateAdded','relatedEntityIds']
    for field in required:
        check(field in record and record[field], f'News Record required field missing: {field}')
    check(record.get('recordType') == 'news_record', 'recordType must be news_record')
    check(record.get('visibility',{}).get('entityDirectory') is False, 'News Record must not appear in entity directory')
    check(record.get('visibility',{}).get('publicEntityType') is False, 'News must not be a public entity type')
    check(record.get('lifecycle',{}).get('automaticAgingEnabled') is False, 'Automatic aging must remain disabled')
    entity_ids = {p.stem for p in (ROOT / 'data/entities').glob('*.json')}
    for entity_id in record.get('relatedEntityIds',[]):
        check(entity_id in entity_ids, f'Related entity does not resolve: {entity_id}')
        check(f'../entities/entity.html?id={entity_id}' in page, f'Displayed Connected Research link missing: {entity_id}')

# Verify News did not become a public entity type.
entity_index = json.loads((ROOT / 'data/entity-index.json').read_text(encoding='utf-8'))
public_types = [str(x).lower() for x in entity_index.get('entityTypes', [])]
check('news' not in public_types and 'news_record' not in public_types, 'News was added to public entity types')

# Verify no News Record slipped into data/entities.
for p in (ROOT / 'data/entities').glob('*.json'):
    try:
        d=json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        continue
    check(d.get('type') not in ('news','news_record') and d.get('recordType') != 'news_record', f'News record incorrectly present in entity collection: {p.name}')

check((ROOT / 'V23_6_NEW_ENTITY_REVIEW.md').exists(), 'New Entity Review missing')

if errors:
    print('V23.6 validation FAILED')
    for e in errors:
        print(' -', e)
    sys.exit(1)
print('V23.6 validation PASSED')
print(' - Latest UAP News first article present')
print(' - 3 Connected Research links resolve to existing entity records')
print(' - no News public entity type introduced')
print(' - no new permanent entities required by this ingestion')
print(' - New Entity Review included')
