#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
SECRET='record-2026-secret-directive-uap-reporting-procedures'; SECRET_NEWS='2026-10-12-secret-directive-uap-reporting-procedures'; VASCO='publication-2026-machine-learning-historical-transients'; VASCO_NEWS='2026-08-10-vasco-machine-learning-transient-analysis'
SC=[f'claim-secret-directive-{x}' for x in ['classified-existence','government-wide-scope','multiple-contacts','odni-fbi-referrals','no-classified-submissions-to-sol','no-guaranteed-release']]
VC=[f'claim-vasco-ml-{x}' for x in ['classification-performance','nuclear-window-association','probability-gradient','earth-shadow-deficit','unrecognized-transient-population','no-origin-determination']]
errors=[]
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def need(v,m):
    if not v: errors.append(m)
for eid in [SECRET,VASCO,'peter-skafish','stephen-bruehl','brian-doherty','alina-streblyanska',*SC,*VC]: need((ROOT/f'data/entities/{eid}.json').exists(),f'missing {eid}')
for nid in [SECRET_NEWS,VASCO_NEWS]:
    n=load(ROOT/f'data/news/{nid}.json'); need(n.get('newsStatus')=='current' and n.get('visibility',{}).get('landmark') is False and n.get('knowledgePermanence')=='permanent',f'lifecycle invalid {nid}'); need(n.get('image',{}).get('src'),f'image metadata missing {nid}')
s=load(ROOT/f'data/entities/{SECRET}.json'); need(s.get('recordMetadata',{}).get('directivePubliclyAvailable') is False,'directive public boundary missing'); need(s.get('recordMetadata',{}).get('solAcceptsClassifiedDisclosures') is False,'classified submission boundary missing')
v=load(ROOT/f'data/entities/{VASCO}.json'); need(v.get('publicationMetadata',{}).get('publicationStatus')=='Peer-reviewed journal article','peer-review status missing'); need(v.get('publicationMetadata',{}).get('doi')=='10.1038/s41598-026-66148-2','DOI missing'); need('not probability of artificial' in v.get('editorialNotes',{}).get('probabilityBoundary',''),'probability boundary missing')
for img in ['secret-directive-uap-reporting-procedures-2026-10.png','vasco-machine-learning-transient-analysis-2026-08.png']: need((ROOT/'assets/news'/img).exists(),f'missing image {img}')
need(load(ROOT/'data/news/index.json').get('records',[])[:2]==[SECRET_NEWS,VASCO_NEWS],'news index order missing'); need(load(ROOT/'data/research-library/index.json').get('records',[])[:2]==[SECRET,VASCO],'research index order missing')
need('secret-directive-uap-reporting-2026-10-12' in (ROOT/'categories/latest-uap-news.html').read_text(encoding='utf-8'),'secret news card missing'); need('vasco-machine-learning-study-2026-08-10' in (ROOT/'categories/latest-uap-news.html').read_text(encoding='utf-8'),'VASCO news card missing'); need('v=23.6d14' in (ROOT/'entities/entity.html').read_text(encoding='utf-8'),'cache key missing')
need(hashlib.sha256((ROOT/'assets/js/entity-engine.js').read_bytes()).hexdigest()=='895c140cff5b2dab5e322068eea31be216529373b3b64cf002504c324bcd2be0','V23.6D.1 runtime changed')
bad=[]
for p in ROOT.rglob('*.json'):
    try: load(p)
    except Exception as e: bad.append(str(p.relative_to(ROOT))+': '+str(e))
need(not bad,'JSON failures: '+'; '.join(bad[:3]))
if errors:
    print('V23.6D.14 VALIDATION FAILED'); [print('- '+e) for e in errors]; raise SystemExit(1)
print('V23.6D.14 VALIDATION PASSED'); print('- Two current/non-landmark news records and two permanent records verified'); print('- Twelve structured claims and four new person entities verified'); print('- Classified-directive attribution and VASCO origin-probability boundaries verified'); print(f'- {sum(1 for _ in ROOT.rglob("*.json"))} JSON files parse successfully'); print('- Two companion images and standing image rule verified')
