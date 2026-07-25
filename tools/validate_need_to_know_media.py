#!/usr/bin/env python3
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
ENT=ROOT/'data/entities'
PLAYLISTS={
 'https://www.youtube.com/playlist?list=PLXdU8QbJkboeMcvUNyGpb9h6FUS9cVBti',
 'https://www.youtube.com/playlist?list=PLXdU8QbJkboePTgyvfpJ6X8MXWPkfxOgv'
}
EXPECTED={
22:'AMZdrtKI_mo',23:'e6XE7wef6k0',24:'3o04UkYg_ks',25:'D62Jj7Ju03A',26:'Bi8ENmUagxw',27:'ZGiQrsyF1U8',28:'Ys47XIOD8h8',29:'g2TI1D1h3AQ',30:'1fmJ9lR28ks',31:'5VwDo_m5Yok',32:'_KAV-nKB-L4',33:'0ZOSixfpq1Y',34:'pFHHxzoIuy8',35:'rQjbFZT9_EM',36:'-PwZsQidbqE',37:'5-As3SXPeJg',38:'AVjzYwQDzeg',39:'YEOB3ASfFuQ',40:'F_0bi1bLHKo',41:'Zrd44LASEKI',42:'0oVa3xU34Dk',43:'RsF-dGi-cFc',44:'QZWhxUAwiN4',45:'n6CjzI5aaww',46:'cwR8pOz9Gvg',47:'vSpHaNbd5A8',48:'DWShhjGr-uc',49:'NFvXyOiUiZ0',50:'XiMrk9vX3og',51:'zC60JOR8nPw',52:'M8Xb3q0NILY',53:'9dmoqsa5WvU',54:'br8sAWRl8EA',55:'5ZxQJg15FNM',56:'l1OQuK5bHt4',57:'kAhQmbCy1VE',58:'DtpBExdn2rc',59:'KLXqSz4xAzE',60:'PLVpruAjP1c',61:'1viZCDLJfqg',62:'83EQaXJvYRI',63:'up3_XVMvetg',64:'r8o4RN_xj2I',65:'cmxyApOGPCA',66:'lwsSMUgC7JM',67:'ZlRkF8Q-yMc',68:'g28EbphgcG0',69:'aQgOPR_z1Iw',70:'EHDcnPDUlXU',71:'pzAOCST4mB4',72:'JiiXNgQ4qL8',73:'8C1pgdKUuoQ',74:'P6oX5E5zXa4',75:'A7t5jd2FDJ4'}
records=[]; errors=[]; video_ids=[]
for p in ENT.glob('*need-to-know-episode-*.json'):
 d=json.loads(p.read_text(encoding='utf-8'))
 if d.get('type')=='podcast_episode' and d.get('seriesId')=='need-to-know-podcast': records.append(d)
for d in sorted(records,key=lambda x:x.get('episodeNumber',999)):
 n=d.get('episodeNumber'); ml=d.get('mediaLinks',[]); rs=d.get('referenceSources',[])
 primary=[x for x in ml if x.get('url') not in PLAYLISTS]
 secondary=[x for x in ml if x.get('url') in PLAYLISTS]
 refs=[x for x in rs if x.get('url') not in PLAYLISTS]
 collections=[x for x in rs if x.get('url') in PLAYLISTS]
 if len(primary)!=1: errors.append(f'#{n}: expected one primary media link, found {len(primary)}')
 if len(refs)!=1: errors.append(f'#{n}: expected one primary reference source, found {len(refs)}')
 if len(secondary)!=1 or len(collections)!=1: errors.append(f'#{n}: official collection link missing or duplicated')
 if primary and refs and primary[0].get('url')!=refs[0].get('url'): errors.append(f'#{n}: primary media/reference URLs disagree')
 if primary:
  u=primary[0].get('url','')
  if 'needtoknow.today/podcasts-on-youtube' in u: errors.append(f'#{n}: archive page used as primary media')
  m=re.search(r'[?&]v=([A-Za-z0-9_-]{11})',u)
  if not m: errors.append(f'#{n}: primary media is not a direct YouTube watch URL')
  else:
   vid=m.group(1); video_ids.append((n,vid))
   if n in EXPECTED and EXPECTED[n]!=vid: errors.append(f'#{n}: expected {EXPECTED[n]}, found {vid}')
ids=[x[1] for x in video_ids]
if len(ids)!=len(set(ids)): errors.append('duplicate primary YouTube video IDs detected')
nums=sorted(d.get('episodeNumber') for d in records)
if nums!=list(range(1,76)): errors.append(f'expected episode numbers 1-75, found {nums}')
print(f'Audited {len(records)} Need to Know records and {len(ids)} direct primary video IDs.')
print(f'Unique primary video IDs: {len(set(ids))}.')
if errors:
 print('NEED TO KNOW MEDIA VALIDATION FAILED'); print('\n'.join('- '+x for x in errors)); sys.exit(1)
print('NEED TO KNOW MEDIA VALIDATION PASSED')
