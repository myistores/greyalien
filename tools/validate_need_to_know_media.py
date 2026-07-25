#!/usr/bin/env python3
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
ENT=ROOT/'data/entities'
PLAYLIST='https://www.youtube.com/playlist?list=PLXdU8QbJkboeMcvUNyGpb9h6FUS9cVBti'
records=[]; errors=[]; video_ids=[]
for p in ENT.glob('*need-to-know-episode-*.json'):
    d=json.loads(p.read_text(encoding='utf-8'))
    if d.get('type')!='podcast_episode' or d.get('seriesId')!='need-to-know-podcast':
        continue
    records.append(d)
for d in sorted(records,key=lambda x:x.get('episodeNumber',999)):
    n=d.get('episodeNumber'); ml=d.get('mediaLinks',[]); rs=d.get('referenceSources',[])
    primary=[x for x in ml if x.get('url')!=PLAYLIST]
    secondary=[x for x in ml if x.get('url')==PLAYLIST]
    refs=[x for x in rs if x.get('url')!=PLAYLIST]
    collections=[x for x in rs if x.get('url')==PLAYLIST]
    if len(primary)!=1: errors.append(f'#{n}: expected one primary media link, found {len(primary)}')
    if len(refs)!=1: errors.append(f'#{n}: expected one primary reference source, found {len(refs)}')
    if len(secondary)!=1 or len(collections)!=1: errors.append(f'#{n}: official collection link missing or duplicated')
    if primary and refs and primary[0].get('url')!=refs[0].get('url'): errors.append(f'#{n}: primary media/reference URLs disagree')
    if primary:
        u=primary[0].get('url','')
        if 'needtoknow.today/podcasts-on-youtube' in u: errors.append(f'#{n}: archive page used as primary media')
        m=re.search(r'[?&]v=([A-Za-z0-9_-]{11})',u)
        if not m: errors.append(f'#{n}: primary media is not a direct YouTube watch URL')
        else: video_ids.append((n,m.group(1)))
ids=[x[1] for x in video_ids]
if len(ids)!=len(set(ids)): errors.append('duplicate primary YouTube video IDs detected')
if len(records)!=21: errors.append(f'expected 21 Need to Know records, found {len(records)}')
print(f'Audited {len(records)} Need to Know records and {len(ids)} direct primary video IDs.')
print(f'Unique primary video IDs: {len(set(ids))}.')
if errors:
    print('NEED TO KNOW MEDIA VALIDATION FAILED')
    print('\n'.join('- '+x for x in errors)); sys.exit(1)
print('NEED TO KNOW MEDIA VALIDATION PASSED')
