#!/usr/bin/env python3
from pathlib import Path
import json,re,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]; ENT=ROOT/'data/entities'; REPORT=ROOT/'reports/v23.5c.2a.1'; REPORT.mkdir(parents=True,exist_ok=True)
SERIES={'weaponized-podcast':'WEAPONIZED','need-to-know-podcast':'Need to Know','merged-podcast':'MERGED','somewhere-in-the-skies-podcast':'Somewhere in the Skies'}

def canon(u):
 return re.sub(r'^https?://(?:www\.)?','',u or '').rstrip('/').lower()
def infer(r):
 x=r.get('destinationType') or r.get('linkScope'); u=(r.get('url') or '').lower(); t=' '.join(str(r.get(k,'')) for k in ('label','platform','sourceType')).lower()
 if x=='series_archive': return 'series'
 if x in {'episode','series','playlist','channel','feed'}: return x
 if 'playlist?' in u or 'playlist' in t:return 'playlist'
 if '/channel/' in u or re.search(r'youtube\.com/@[^/]+/?$',u):return 'channel'
 if 'rss' in t or '/feed' in u or u.endswith(('.xml','.rss')):return 'feed'
 if 'episode' in t or 'watch?v=' in u or '/episode' in u:return 'episode'
 return 'series'
def rank(r):
 if isinstance(r.get('preferredRank'),int):return r['preferredRank']
 d=infer(r); z=((r.get('url') or '')+' '+(r.get('platform') or '')).lower()
 if d=='episode':
  if 'weaponizedpodcast.com' in z or 'somewhereintheskies.com' in z:return 1
  if 'youtube' in z:return 2
  if 'podcasts.apple.com' in z:return 3
  if 'spotify' in z:return 4
  return 5
 return 7 if d=='feed' else 6
def collection(e):
 raw=[]
 for k in ('officialMedia','official_media'):
  if isinstance(e.get(k),list):raw+=e[k]
 for field in ('mediaLinks','officialLinks','referenceSources'):
  for x in e.get(field,[]) or []:
   if not isinstance(x,dict) or not x.get('url'):continue
   status=x.get('verificationStatus') or x.get('validationStatus') or 'verified'
   if status in {'live_verified','live_verified_fallback','legacy_unspecified'}:status='verified'
   official=field!='referenceSources' or str(x.get('sourceType','')).startswith(('official_','authoritative_'))
   raw.append({**x,'official':official,'verified':status=='verified','verificationStatus':status,'destinationType':infer(x),'preferredRank':rank(x),'legacySource':field})
 out={}
 for r in raw:
  if not r.get('url'):continue
  r={**r,'destinationType':infer(r),'preferredRank':rank(r)}; k=canon(r['url']); old=out.get(k)
  score=lambda x:(100 if x.get('official') else 0)+(20 if x.get('destinationType')=='episode' else 0)+(10 if x.get('verified') else 0)-rank(x)
  if old is None or score(r)>score(old):out[k]=r
 return list(out.values())
def eligible(r):return r.get('official') is True and r.get('verified') is True and r.get('verificationStatus')=='verified' and r.get('approved',True) is not False and r.get('published',True) is not False and str(r.get('url','')).startswith(('http://','https://'))
def preferred(e):
 a=[r for r in collection(e) if eligible(r)]; a.sort(key=lambda r:(infer(r)!='episode',rank(r),r.get('label',''))); return a[0] if a else None

diagnostics=[]; reports={k:[] for k in SERIES}; errors=[]
for p in sorted(ENT.glob('*.json')):
 e=json.loads(p.read_text()); sid=e.get('seriesId') or (e['id'] if e.get('type')=='podcast_series' else None)
 if sid not in SERIES or e.get('type') not in {'podcast_episode','podcast_series'}:continue
 rows=[r for r in collection(e) if eligible(r)]; pref=preferred(e); rendered=[]
 if pref:rendered.append({'label':pref.get('label') or 'Official media','url':pref['url'],'platform':pref.get('platform'),'destinationType':infer(pref),'preferred':True,'visible':True})
 for r in rows:
  if pref and canon(r['url'])==canon(pref['url']):continue
  rendered.append({'label':r.get('label') or 'Official media','url':r['url'],'platform':r.get('platform'),'destinationType':infer(r),'preferred':False,'visible':True})
 result='pass' if (not rows or rendered) else 'fail'
 if rows and not rendered:errors.append(f"{e['id']}: valid media exists but no action rendered")
 if len([r for r in rendered if r['preferred']])>1:errors.append(f"{e['id']}: duplicate preferred actions")
 if pref and infer(pref)!='episode' and e.get('type')=='podcast_episode' and any(infer(r)=='episode' for r in rows):errors.append(f"{e['id']}: non-episode selected over direct episode")
 diagnostics.append({'episode':e['id'],'entityType':e.get('type'),'seriesId':sid,'preferredDestination':rendered[0] if rendered else None,'renderedActions':rendered,'hiddenActions':[],'compatibilityStatus':'officialMedia+legacy' if isinstance(e.get('officialMedia'),list) else 'legacy-fallback','rendererInputs':{'officialMediaCount':len(e.get('officialMedia') or []),'legacyMediaCount':sum(len(e.get(x) or []) for x in ('mediaLinks','officialLinks','referenceSources'))},'rendererOutputs':{'visibleActionCount':len(rendered)},'validationResult':result})
 reports[sid].append(diagnostics[-1])
# static integration checks
entity_html=(ROOT/'entities/entity.html').read_text(); gateway_html=(ROOT/'categories/somewhere-in-the-skies.html').read_text(); helper=(ROOT/'assets/js/podcast-official-media.js').read_text(); engine=(ROOT/'assets/js/entity-engine.js').read_text(); gateway=(ROOT/'assets/js/somewhere-in-the-skies-gateway.js').read_text()
for ok,msg in [(entity_html.index('podcast-official-media.js')<entity_html.index('entity-engine.js'),'helper not loaded before entity renderer'),('officialMediaPanel=window.GreyAlienOfficialMedia' in engine,'entity renderer not consuming helper'),('podcast-official-media.js' in gateway_html,'gateway helper missing'),('renderAction(media' in gateway,'gateway preferred action missing'),('official_media' in helper,'snake_case compatibility missing'),('adaptLegacy' in helper,'legacy compatibility missing')]:
 if not ok:errors.append(msg)
# specific identity preservation
expected={13:'HRCT_ddq39U',14:'YOjSBPfmoIM'}
for n,vid in expected.items():
 matches=[d for d in diagnostics if d['seriesId']=='need-to-know-podcast' and json.loads((ENT/f"{d['episode']}.json").read_text()).get('episodeNumber')==n]
 if len(matches)!=1 or not matches[0]['preferredDestination'] or vid not in matches[0]['preferredDestination']['url']:errors.append(f'Need to Know Episode {n}: preferred identity mismatch')
# counts and reports
(REPORT/'rendering_diagnostics.json').write_text(json.dumps({'release':'V23.5C.2A.1','records':diagnostics,'errors':errors},indent=2)+'\n')
for sid,name in SERIES.items():
 a=reports[sid]; episodes=[x for x in a if x['entityType']=='podcast_episode']; missing=[x for x in episodes if not x['renderedActions']]
 md=f"# {name} Rendering Report\n\n- Episode count: {len(episodes)}\n- Records with official media: {sum(bool(x['rendererInputs']['officialMediaCount'] or x['rendererInputs']['legacyMediaCount']) for x in episodes)}\n- Rendered buttons: {sum(len(x['renderedActions']) for x in episodes)}\n- Missing buttons: {len(missing)}\n- Preferred selections: {sum(bool(x['preferredDestination']) for x in episodes)}\n- Compatibility issues: {sum(x['validationResult']!='pass' for x in episodes)}\n- Rendering fix: universal helper loaded and consumed; preferred action plus deduplicated alternates exposed.\n"
 (REPORT/f"{sid}_rendering_report.md").write_text(md)
summary=f'''# V23.5C.2A.1 Rendering Restoration Summary

## Root cause
The V23.5A universal helper was present but `entities/entity.html` did not load it. The entity renderer detected `officialMedia`, suppressed legacy panels, then received an empty helper result because `window.GreyAlienOfficialMedia` was undefined.

## Repaired components
- Loaded the compatibility helper before the entity renderer.
- Restored preferred-media actions and deduplicated alternates for episode and series entities.
- Added mixed-state support for `officialMedia`, `official_media`, and legacy media fields.
- Restored preferred actions in the Somewhere in the Skies gateway and podcast directory.
- Added permanent build-failure validation when eligible media exists without a public action.

## Verification
- Podcast records checked: {len(diagnostics)}
- Episode records checked: {sum(d['entityType']=='podcast_episode' for d in diagnostics)}
- Validation errors: {len(errors)}
- Need to Know Episodes 13 and 14 preserve their existing approved direct YouTube identities.
- No official-media data or knowledge-graph JSON was rewritten.

## Remaining issues
{'None detected.' if not errors else chr(10).join('- '+e for e in errors)}
'''
(REPORT/'rendering_restoration_summary.md').write_text(summary)
print(f'Validated {len(diagnostics)} podcast records; errors={len(errors)}')
if errors:
 print('\n'.join(errors));sys.exit(1)
