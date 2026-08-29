#!/usr/bin/env python3
from pathlib import Path
import json, sys, re
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'data/entities'; errors=[]
manifest=json.loads((ROOT/'data/graph-manifest.json').read_text())
idx=json.loads((ROOT/'data/entity-index.json').read_text())
rels=json.loads((ROOT/'data/relationship-index.json').read_text())

def check(cond,msg):
    if not cond: errors.append(msg)

# Reference research artifacts retained for future Science Research Agent regression testing.
check((ROOT/'docs/science-research/ST-001A_RESEARCH_PACKET.md').exists(),'S&T-001A reference research packet missing')
check((ROOT/'docs/science-research/ST-001A_INGESTION_MANIFEST.json').exists(),'S&T-001A ingestion manifest missing')

# Entity uniqueness/content
matches=[e for e in idx['entities'] if e['id']=='image-video-analysis' or e.get('name')=='Image & Video Analysis']
check(len(matches)==1,f'Image & Video Analysis entity count is {len(matches)}, expected 1')
iva=json.loads((E/'image-video-analysis.json').read_text())
check(iva.get('type')=='topic','Image & Video Analysis must be topic')
check(iva.get('taxonomyStatus')=='canonical','Image & Video Analysis must be canonical')
science=iva.get('scienceResearch',{})
check(science.get('collection')=='Scientific Methods','Science collection metadata missing')
check(science.get('researchPacket')=='S&T-001A','Research packet provenance missing')
check(science.get('scienceSeedScore')=='30/30','Science Seed Score missing')
check(len(science.get('foundation',[]))==9,'Expected 9 scientific foundation subsections')
check(len(science.get('authoritativeSources',[]))==13,'Expected 13 authoritative sources')
check({s.get('tier') for s in science.get('authoritativeSources',[])}=={'S','A'},'Only approved Tier S/A sources expected')
check(len(science.get('evidenceClasses',[]))==9,'Expected 9 evidence classifications')

# Exactly 18 approved incoming relationships
incoming=rels.get('incoming',{}).get('image-video-analysis',[])
check(len(incoming)==18,f'Expected 18 incoming S&T-001A relationships, found {len(incoming)}')
expected={
'2004-nimitz-encounter','2016-mosul-orb-incident','2017-iraq-jellyfish-uap','2025-large-disc-uap-video','2025-yemen-hellfire-uap-video','syria-uap-2021','2026-03-31-house-uap-video-request-letter','2026-weaponized-episode-108','2025-weaponized-episode-81','2024-weaponized-episode-47','2025-weaponized-episode-79','2025-weaponized-episode-89','2023-weaponized-episode-8','2025-weaponized-episode-72','claim-context-is-required-to-interpret-released-uap-videos','claim-the-released-footage-warrants-frame-by-frame-technical-review','claim-independent-experts-require-direct-and-transparent-access','claim-the-object-appears-to-accelerate-abruptly-after-sensor-lock'}
found={r['source'] for r in incoming}
check(found==expected,f'Approved relationship sources differ. Missing={sorted(expected-found)}, extra={sorted(found-expected)}')
check('chad-underwood' not in found,'Held Chad Underwood relationship was created')
check('2014-2015-east-coast-navy-encounters' not in found,'Held East Coast Navy relationship was created')
for r in incoming:
    meta=r.get('meta',{})
    check(meta.get('researchPacket')=='S&T-001A',f"{r.get('source')}: research provenance missing")
    check(meta.get('confidenceGrade') in {'A','B'},f"{r.get('source')}: unexpected confidence grade")
    check(isinstance(meta.get('confidenceScore'),int),f"{r.get('source')}: confidence score missing")

# No duplicate direct relationships to the target
for p in E.glob('*.json'):
    d=json.loads(p.read_text())
    rs=[(r.get('type'),r.get('target')) for r in d.get('relationships',[]) if r.get('target')=='image-video-analysis']
    check(len(rs)==len(set(rs)),f'{p.stem}: duplicate relationship to Image & Video Analysis')

# Syria enrichment + claim preservation
syria=json.loads((E/'syria-uap-2021.json').read_text())
check('digitally altered' in syria.get('summary',''),'Syria enrichment missing digital-alteration context')
check(any('aaro.mil' in x.get('url','') and '1007707' in x.get('url','') for x in syria.get('referenceSources',[])),'Syria AARO PR051 source missing')
claim=json.loads((E/'claim-the-object-appears-to-accelerate-abruptly-after-sensor-lock.json').read_text())
check(claim.get('type')=='claim','Acceleration record must remain a claim')
check('appears' in claim.get('name','').lower(),'Acceleration claim wording was improperly converted to fact')

# Collection/live rendering
methods=(ROOT/'science/scientific-methods/index.html').read_text()
check('Live research' in methods and 'Image &amp; Video Analysis' in methods,'Scientific Methods live topic card missing')
check('Planned starting areas' in methods,'Planned starting areas were removed')
check('../../entities/generated/image-video-analysis.html' in methods,'Live topic card destination incorrect')
engine=(ROOT/'assets/js/entity-engine.js').read_text()
for token in ['scienceResearch','Scientific foundation','Authoritative Research Sources','Claims & Analytical Questions','Related Scientific Topics']:
    check(token in engine,f'Reusable Science renderer missing token: {token}')
check('entity-engine.js?v=23.6e' in (ROOT/'entities/entity.html').read_text(),'Entity runtime cache bust not updated')
check('image-video-analysis.html' in (ROOT/'sitemap.xml').read_text(),'Generated entity missing from sitemap')

# V23.6D.1 reliability architecture must remain intact.
check('idx.entities.map(e=>fetch(`../data/entities/${e.id}.json`)' not in engine,'Legacy full-graph entity fetch loop returned')
check('../data/relationship-index.json' in engine,'Precomputed relationship-index loading was removed')
check('Unable to load this record.' in engine and '>Retry<' in engine,'Explicit entity load failure/retry state missing')
check('GreyAlien entity load failed' in engine,'Entity-load diagnostic logging missing')
index_ids={e['id'] for e in idx['entities']}
entity_by_id={p.stem:json.loads(p.read_text()) for p in E.glob('*.json') if json.loads(p.read_text()).get('taxonomyStatus')!='alias'}
expected_incoming={i:[] for i in index_ids}
for source_id in sorted(index_ids):
    d=entity_by_id[source_id]
    for r in d.get('relationships',[]):
        if r.get('target') in index_ids:
            expected_incoming[r['target']].append({'source':source_id,'type':r.get('type'),'meta':r})
for target in expected_incoming:
    expected_incoming[target].sort(key=lambda x:(x.get('source',''),x.get('type',''),json.dumps(x.get('meta',{}),sort_keys=True,ensure_ascii=False)))
actual_incoming=rels.get('incoming',{})
check(set(actual_incoming)==index_ids,'Relationship index target inventory no longer matches entity index')
for target in index_ids:
    if expected_incoming[target] != actual_incoming.get(target,[]):
        errors.append(f'Relationship-index equivalence failed for {target}')
        break

# Protected V23.6C news assets/records inherited through V23.6D remain byte-for-byte valid.
protected_path=ROOT/'data/v23-6d-protected-hashes.json'
if protected_path.exists():
    import hashlib
    for rel, expected_hash in json.loads(protected_path.read_text()).items():
        fp=ROOT/rel
        check(fp.exists(),f'Protected inherited file missing: {rel}')
        if fp.exists():
            check(hashlib.sha256(fp.read_bytes()).hexdigest()==expected_hash,f'Protected inherited file changed: {rel}')

# Graph counts: V23.6D.1 1611 entities / 3534 resolved relationships => +1 / +18.
check(manifest.get('entityCount')==1612,f"Expected 1612 entities, got {manifest.get('entityCount')}")
check(manifest.get('relationshipCount')==3552,f"Expected 3552 resolved relationships, got {manifest.get('relationshipCount')}")
check(manifest.get('unresolvedRelationshipCount')==56,f"Inherited unresolved count changed: {manifest.get('unresolvedRelationshipCount')}")

if errors:
    print('V23.6E VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('V23.6E VALIDATION PASSED')
print('Entity: Image & Video Analysis (1 canonical topic)')
print('Approved relationships: 18')
print('Science sources: 13 (Tier S/A)')
print('Held relationships preserved: Chad Underwood; East Coast Navy encounters')
