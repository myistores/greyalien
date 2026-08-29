#!/usr/bin/env python3
"""V23.6D.2 release validator: VASCO scientific challenge + news lifecycle + permanent research."""
from pathlib import Path
import hashlib, json, sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]

def load(rel):
    try: return json.loads((ROOT/rel).read_text(encoding='utf-8'))
    except Exception as exc: errors.append(f"{rel}: {exc}"); return {}

def require(cond,msg):
    if not cond: errors.append(msg)

protected={
  "data/entities/image-video-analysis.json": "83b0d594ee3d4e1c2a7a5441041e3e99a7b2e2e86d273415b15fe561e287dc3b",
  "categories/science-technology.html": "9f55d99a2cbb42ad68f3d8803ea11f5c9343c957e5eed3fc6211806738d0e962",
  "science/scientific-methods/index.html": "e751c00f9188a8146773ee90831e1c638631b78ee1cd23df49787a4fd3242270",
  "assets/js/entity-engine.js": "895c140cff5b2dab5e322068eea31be216529373b3b64cf002504c324bcd2be0",
  "assets/js/graph-core.js": "436034c2777af9fe907e451231e8a6103e83d319f9f21b8759cb76c5b5eba930",
  "assets/js/automation-enhancements.js": "51d8af788e0c3e83387bddcf50c6e9ae56bca988ffd16d26a591807c532efadf",
  "data/news/2026-08-21-ufo-chronicles-marco-rubio-uap.json": "60cf72a41f98c99141780b057a70e112ed676b290d73885c2b6dbab9a16982ee",
  "data/news/2026-08-20-sol-foundation-uap-technology-arms-race.json": "3d2aec4faf152aff3e859a744fb78a72793c1df6ba695d4c1e48cc53b440d033",
  "data/news/2026-08-20-debrief-pursue-video-analysis.json": "490405900bf47cf91aef7c16c1c5c263cf9a1b45182c0cb2e61261a45af09c7f",
  "data/news/2026-08-19-liberation-times-ufo-disclosure-trump.json": "4a2518def233b7e3b633a8a24403f9c4eb038d77abb70582c16477ab7994b734",
  "data/news/2026-08-19-scitechdaily-have-we-found-alien-life.json": "9e4e98d1b24b4d9392d3567c87e8789a8ec9f7ca22efad164480fc7d1c3043c9"
}
for rel,expected in protected.items():
    p=ROOT/rel
    require(p.exists(),f"Protected inherited file missing: {rel}")
    if p.exists(): require(hashlib.sha256(p.read_bytes()).hexdigest()==expected,f"Protected inherited file changed unexpectedly: {rel}")

news=load('data/news/2026-08-28-ibtimes-vasco-nuclear-test-challenge.json')
require(news.get('recordType')=='news_record','VASCO news record type mismatch')
require(news.get('newsStatus')=='current','VASCO news must begin current')
require(news.get('knowledgePermanence')=='permanent','VASCO extracted knowledge must be permanent')
require(news.get('visibility',{}).get('landmark') is False,'VASCO news must be non-landmark')
require(news.get('lifecycle',{}).get('automaticAgingEnabled') is False,'Automatic news aging must remain disabled')
require(any(r.get('type')=='surfaces_publication' and r.get('target')=='publication-2026-critical-evaluation-poss1e-technosignatures' for r in news.get('relationships',[])),'News must surface permanent PASA publication')

schema=load('data/news/news-record-schema.json')
require(schema.get('properties',{}).get('newsStatus',{}).get('enum')==['current','archived','landmark'],'newsStatus lifecycle enum missing or changed')
require('permanent' in schema.get('properties',{}).get('knowledgePermanence',{}).get('enum',[]),'knowledgePermanence schema missing permanent')

pub=load('data/entities/publication-2026-critical-evaluation-poss1e-technosignatures.json')
require(pub.get('type')=='publication','Permanent PASA research object must be a publication entity')
require(pub.get('publicationMetadata',{}).get('publicationStatus')=='Peer-reviewed accepted manuscript','Publication status must preserve accepted-manuscript distinction')
require(pub.get('publicationMetadata',{}).get('doi')=='10.1017/pasa.2026.10230','PASA DOI mismatch')
require(pub.get('researchLibraryMetadata',{}).get('knowledgePermanence')=='permanent','Research Library publication must be permanent')
require(bool(pub.get('researchLibraryMetadata',{}).get('methodology')),'Research methodology missing')
require(bool(pub.get('researchLibraryMetadata',{}).get('principalFindings')),'Principal findings missing')
require(bool(pub.get('researchLibraryMetadata',{}).get('limitations')),'Research limitations missing')
require(any(r.get('target')=='claim-vasco-transients-nuclear-test-correlation' and r.get('role')=='challenges' for r in pub.get('relationships',[])),'Publication must challenge original correlation claim')

original=load('data/entities/claim-vasco-transients-nuclear-test-correlation.json')
challenge=load('data/entities/claim-watters-vasco-methodological-challenge.json')
require(original.get('claimStatus')=='disputed','Original VASCO correlation claim must remain disputed, not overwritten')
require(challenge.get('claimStatus')=='research_finding_under_dispute','Methodological challenge must preserve active-dispute status')
require(any('vasconsite.wordpress.com/2026/07/11' in s.get('url','') for s in challenge.get('referenceSources',[])),'Competing VASCO response/replication context missing from challenge claim')

new_entities=['publication-2026-critical-evaluation-poss1e-technosignatures','vasco-project','beatriz-villarroel','wesley-watters','kevin-knuth','technosignatures','palomar-observatory','claim-vasco-transients-nuclear-test-correlation','claim-watters-vasco-methodological-challenge']
idx=load('data/entity-index.json')
ids={e.get('id') for e in idx.get('entities',[])}
for eid in new_entities:
    require((ROOT/f'data/entities/{eid}.json').exists(),f'Missing entity {eid}')
    require(eid in ids,f'Entity omitted from entity index: {eid}')
    require((ROOT/f'entities/generated/{eid}.html').exists(),f'Missing crawlable generated page: {eid}')

nidx=load('data/news/index.json')
require(nidx.get('records',[None])[0]=='2026-08-28-ibtimes-vasco-nuclear-test-challenge','VASCO news must be newest indexed record')
ridx=load('data/research-library/index.json')
require(ridx.get('records',[None])[0]=='publication-2026-critical-evaluation-poss1e-technosignatures','PASA critique must be newest Research Library record')

news_html=(ROOT/'categories/latest-uap-news.html').read_text(encoding='utf-8')
research_html=(ROOT/'categories/research-library.html').read_text(encoding='utf-8')
require('id="vasco-scientific-challenge-2026-08-28"' in news_html,'Latest UAP News VASCO article missing')
require('data-news-status="current"' in news_html and 'data-knowledge-permanence="permanent"' in news_html,'Lifecycle/permanence HTML markers missing')
require('Permanent Research Record' in news_html,'News → Research Library entity path missing')
require('id="critical-evaluation-poss1e-technosignatures"' in research_html,'Research Library PASA record missing')
require('Related News Coverage' in research_html,'Research → News backlink missing')
require('active scientific dispute' in research_html,'Research Library must avoid categorical debunking framing')

entity_shell=(ROOT/'entities/entity.html').read_text(encoding='utf-8')
require('entity-engine.js?v=23.6d2' in entity_shell,'Entity runtime cache bust must identify V23.6D.2')

if errors:
    print('V23.6D.2 VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('V23.6D.2 VALIDATION PASSED')
print(' - current/non-landmark news surface + permanent research object')
print(' - independent newsStatus and knowledgePermanence lifecycle fields')
print(' - original VASCO correlation claim and methodological challenge remain separate')
print(' - VASCO competing response/replication context preserved')
print(' - cross-gateway News ↔ Research paths present')
print(' - V23.6E Science & Technology and V23.6D.1 runtime files protected byte-for-byte')
