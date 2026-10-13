#!/usr/bin/env python3
"""Release-specific validation for V23.6D.12."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]; PUB='publication-2026-six-infrared-objects-bird-wingbeat-analysis'; CASE='case-dow-uap-pr135-six-infrared-objects'; NEWS='2026-10-06-pursue-pr135-six-objects-bird-analysis'
errors=[]
def need(v,m):
    if not v: errors.append(m)
def load(p): return json.loads(p.read_text(encoding='utf-8'))
pub=load(ROOT/f'data/entities/{PUB}.json'); case=load(ROOT/f'data/entities/{CASE}.json'); news=load(ROOT/f'data/news/{NEWS}.json')
need(pub.get('publicationMetadata',{}).get('version')=='v2','arXiv version missing')
need('peer review and acceptance not established' in pub.get('publicationMetadata',{}).get('publicationStatus',''),'preprint status missing')
need(case.get('caseMetadata',{}).get('reportedObjectCount')==6,'six-object count missing')
need(news.get('newsStatus')=='current' and news.get('knowledgePermanence')=='permanent','lifecycle invalid')
need(news.get('visibility',{}).get('landmark') is False,'news must be non-landmark')
need((ROOT/'assets/news/pursue-pr135-six-object-bird-analysis.png').exists(),'companion image missing')
need(load(ROOT/'data/news/index.json').get('records',[None])[0]==NEWS,'news index ordering missing')
need(load(ROOT/'data/research-library/index.json').get('records',[None])[0]==PUB,'research index ordering missing')
need('id="pursue-pr135-bird-analysis-2026-10-06"' in (ROOT/'categories/latest-uap-news.html').read_text(encoding='utf-8'),'news card missing')
need('id="pursue-pr135-six-object-bird-analysis"' in (ROOT/'categories/research-library.html').read_text(encoding='utf-8'),'research card missing')
need('v=23.6d12' in (ROOT/'entities/entity.html').read_text(encoding='utf-8'),'cache key missing')
authors=['jacob-haqq-misra','ravi-kopparapu','richard-cloete','omer-eldadi','michael-shermer','avi-loeb']
claims=['claim-pr135-mission-report-480-mph','claim-pr135-independent-brightness-flicker','claim-pr135-flicker-not-tested-artifact','claim-pr135-galileo-animal-frequency-overlap','claim-pr135-parallax-can-reproduce-projected-speed','claim-pr135-bird-hypothesis','claim-pr135-telemetry-needed-to-test-hypothesis']
for eid in authors+claims: need((ROOT/f'data/entities/{eid}.json').exists(),f'missing record: {eid}')
targets={r.get('target') for r in pub.get('relationships',[])}
for eid in authors+claims+[CASE,'collection-2026-pursue-release-06','publication-2026-limits-velocity-recovery-pursue','galileo-project','image-video-analysis']: need(eid in targets,f'publication relationship missing: {eid}')
need('not a definitive identification' in pub.get('researchLibraryMetadata',{}).get('researchImplication',''),'interpretation boundary missing')
need(hashlib.sha256((ROOT/'assets/js/entity-engine.js').read_bytes()).hexdigest()=='895c140cff5b2dab5e322068eea31be216529373b3b64cf002504c324bcd2be0','V23.6D.1 runtime changed')
bad=[]
for p in ROOT.rglob('*.json'):
    try: load(p)
    except Exception as exc: bad.append(f'{p.relative_to(ROOT)}: {exc}')
need(not bad,'JSON parse failures: '+'; '.join(bad[:5]))
if errors:
    print('V23.6D.12 VALIDATION FAILED'); [print('- '+e) for e in errors]; raise SystemExit(1)
print('V23.6D.12 VALIDATION PASSED')
print('- Current / non-landmark news and permanent preprint verified')
print('- Six authors, PR135 case and seven structured claims verified')
print('- Original report, quantitative findings and provisional bird hypothesis remain separate')
print(f'- {sum(1 for _ in ROOT.rglob("*.json"))} JSON files parse successfully')
print('- Companion image and V23.6D.1 runtime verified')
