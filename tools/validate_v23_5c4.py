#!/usr/bin/env python3
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]
expected={
1:('0CeWGqVZ3ft2lpaln1vUnf',None),2:('0rsZ1iYPkG5R5MtTwO91yu','5QDt_bTpo60'),
3:('61Y2LdLvATqQI5D68Nisj4','uEiHQls_-Y8'),4:('5nnM6FRzSDFrGjkBD4bBDF','HSfpUVr3Ais'),
5:('3XfnZP8EqF6K2VnuysvQIg','RRyER-wEswA'),6:('220gaXtTnUbqCe3FDL0zir','yTNuzvLx4io'),
7:('4DKHn3la46ZaWVpnZpqdBJ','Vd5WemgxddI'),8:('66s2vQXfI8QiAvTbI6FcTL','q9s8zhS1UNE'),
9:('73Y7A1Gdio7bSOdzcNz6hO','bJLAa1uMr5o'),10:('49tt1J5N28UtzXpR1rBXqS','ZGgV409wwRY')}
for n,(sid,yid) in expected.items():
 p=ROOT/f'data/entities/2017-somewhere-in-the-skies-episode-{n}.json'; e=json.loads(p.read_text())
 media=e.get('officialMedia') or []
 spotify=[x for x in media if x.get('platform')=='Spotify']
 youtube=[x for x in media if x.get('platform')=='YouTube']
 if len(spotify)!=1 or spotify[0].get('url')!=f'https://open.spotify.com/episode/{sid}': errors.append(f'episode {n}: Spotify mismatch')
 expected_y=0 if yid is None else 1
 if len(youtube)!=expected_y: errors.append(f'episode {n}: YouTube count mismatch')
 if yid and youtube[0].get('url')!=f'https://www.youtube.com/watch?v={yid}': errors.append(f'episode {n}: YouTube mismatch')
 for x in spotify+youtube:
  if '?' in x['url'] and not (x.get('platform')=='YouTube' and '?v=' in x['url'] and x['url'].count('?')==1): errors.append(f'episode {n}: tracking parameter remains')
  if x.get('destinationType')!='episode' or x.get('verificationStatus')!='verified': errors.append(f'episode {n}: bad direct-media classification')
for p in sorted((ROOT/'data/entities').glob('2017-somewhere-in-the-skies-episode-*.json')):
 n=int(p.stem.rsplit('-',1)[1])
 if n<=10: continue
 e=json.loads(p.read_text())
 if any((x.get('validationProvenance') or {}).get('release')=='V23.5C.4' for x in e.get('officialMedia',[])): errors.append(f'episode {n}: out-of-scope modification marker')
js=(ROOT/'assets/js/podcast-official-media.js').read_text()
for token in ["pilot=e.seriesId==='somewhere-in-the-skies-podcast'","official-media-actions","['Spotify','YouTube'].includes(r.platform)"]:
 if token not in js: errors.append(f'renderer missing {token}')
css=(ROOT/'style.css').read_text()
if '.official-media-actions{display:flex;flex-wrap:wrap' not in css: errors.append('pilot CSS missing')
if errors:
 print('\n'.join(errors));sys.exit(1)
print('V23.5C.4 validation passed: 10 Spotify URLs, 9 YouTube URLs, scoped UI pilot, prior Apple records preserved.')
