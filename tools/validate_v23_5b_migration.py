#!/usr/bin/env python3
import json,glob,sys,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from podcast_official_media import canonical_url,validate_record,resolve_preferred
ROOT=Path(__file__).resolve().parents[1]
TARGETS={'weaponized-podcast':123,'need-to-know-podcast':75,'merged-podcast':19,'somewhere-in-the-skies-podcast':40}
errors=[]; counts={k:0 for k in TARGETS}; migrated=0
for f in glob.glob(str(ROOT/'data/entities/*.json')):
 e=json.load(open(f)); sid=e.get('id') if e.get('id') in TARGETS else e.get('seriesId')
 if sid not in TARGETS: continue
 migrated+=1
 if e.get('type')=='podcast_episode':counts[sid]+=1
 if not isinstance(e.get('officialMedia'),list):errors.append(f"{e['id']}: missing officialMedia");continue
 seen=set()
 for r in e['officialMedia']:
  for x in validate_record(r):errors.append(f"{e['id']}: {x}")
  c=canonical_url(r['url'])
  if c in seen:errors.append(f"{e['id']}: duplicate canonical URL {c}")
  seen.add(c)
  if 'acast.com' in r['url'].lower() and r['verificationStatus']=='verified':errors.append(f"{e['id']}: active retired Acast URL")
 p=resolve_preferred(e,preserve_legacy=False)
 if p and p['destinationType'] in {'series','playlist','channel','feed'} and re.search(r'watch|listen to episode|official episode page',p['label'],re.I):errors.append(f"{e['id']}: fallback mislabeled {p['label']}")
 if e.get('mediaMigration',{}).get('legacyFieldsPreserved') is not True:errors.append(f"{e['id']}: compatibility flag missing")
for sid,n in TARGETS.items():
 if counts[sid]!=n:errors.append(f'{sid}: expected {n} episodes, found {counts[sid]}')
# Specific NTK corrections
expected={13:'HRCT_ddq39U',14:'YOjSBPfmoIM'}
for n,vid in expected.items():
 matches=[]
 for f in glob.glob(str(ROOT/'data/entities/*.json')):
  e=json.load(open(f))
  if e.get('seriesId')=='need-to-know-podcast' and e.get('episodeNumber')==n:matches.append(e)
 if len(matches)!=1 or not any(vid in r['url'] for r in matches[0].get('officialMedia',[])):errors.append(f'Need to Know Episode {n}: corrected video not preserved')
arc=json.load(open(ROOT/'data/podcasts/somewhere-in-the-skies-archive.json'))
if len(arc.get('episodes',[]))!=40:errors.append('Somewhere archive count changed')
rec=json.load(open(ROOT/'data/migration/v23.5b/reconciliation.json'))
if rec.get('nonMediaFieldChangeCount')!=0:errors.append('non-media changes reported')
if migrated!=261:errors.append(f'expected 261 migrated entities, found {migrated}')
if errors:
 print('\n'.join('ERROR '+e for e in errors));raise SystemExit(1)
print(f'V23.5B migration validation passed: {migrated} entities; episode counts {counts}; zero unauthorized non-media changes.')
