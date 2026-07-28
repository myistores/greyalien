#!/usr/bin/env python3
import argparse,glob,json,sys,urllib.request,urllib.error,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SERIES='https://podcasts.apple.com/us/podcast/somewhere-in-the-skies/id1227858637'
BAD=('shows.acast.com/somewhere-in-the-skies',)

def load_records():
    return [json.load(open(p,encoding='utf-8')) for p in sorted(glob.glob(str(ROOT/'data/entities/2017-somewhere-in-the-skies*.json')))]
def check_static(records):
    errors=[]
    if len(records)!=40: errors.append(f'Expected 40 records, found {len(records)}')
    for d in records:
        links=d.get('mediaLinks',[])
        if len(links)!=1: errors.append(f"{d['id']}: expected exactly one media link") ; continue
        l=links[0]; u=l.get('url',''); scope=l.get('linkScope')
        if any(b in u for b in BAD): errors.append(f"{d['id']}: retired Acast URL remains")
        if scope not in ('episode','series_archive'): errors.append(f"{d['id']}: invalid linkScope {scope}")
        if scope=='series_archive' and u!=SERIES: errors.append(f"{d['id']}: unapproved archive fallback")
        if scope=='episode' and u==SERIES: errors.append(f"{d['id']}: series page mislabeled as episode")
        if not d.get('referenceSources') or d['referenceSources'][0].get('url')!=u: errors.append(f"{d['id']}: source/media mismatch")
    archive=json.load(open(ROOT/'data/podcasts/somewhere-in-the-skies-archive.json',encoding='utf-8'))
    items=archive.get('episodes',archive.get('releases',[]))
    if len(items)!=40: errors.append(f'Archive expected 40 records, found {len(items)}')
    by={d['id']:d['mediaLinks'][0] for d in records}
    for x in items:
        if x.get('officialUrl')!=by[x['entityId']]['url']: errors.append(f"{x['entityId']}: archive/entity URL mismatch")
    return errors

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 GreyAlien link validator'})
    with urllib.request.urlopen(req,timeout=25) as r:
        body=r.read(500000).decode('utf-8','ignore'); return r.status,r.geturl(),body

def check_live(records):
    errors=[]; seen={}
    for d in records:
        l=d['mediaLinks'][0]; u=l['url']
        if u not in seen:
            try: seen[u]=fetch(u)
            except Exception as e: errors.append(f'{u}: HTTP failure: {e}'); continue
        status,final,body=seen[u]
        if status>=400: errors.append(f'{u}: HTTP {status}')
        low=body.lower()
        if re.search(r'page not found|404 not found|doesn.t exist',low): errors.append(f'{u}: rendered not-found page')
        if 'somewhere in the skies' not in low: errors.append(f'{u}: show title not found')
        if l['linkScope']=='episode':
            title=d.get('episodeTitle','').lower(); tokens=[t for t in re.findall(r'[a-z0-9]+',title) if len(t)>4][:4]
            if tokens and sum(t in low for t in tokens)<max(1,len(tokens)//2): errors.append(f"{d['id']}: episode title does not sufficiently match destination")
    return errors

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--live',action='store_true'); args=ap.parse_args()
    rec=load_records(); errors=check_static(rec)
    if args.live: errors+=check_live(rec)
    if errors:
        print('\n'.join('ERROR: '+e for e in errors)); return 1
    exact=sum(d['mediaLinks'][0]['linkScope']=='episode' for d in rec)
    print(f'PASS: 40 records; {exact} exact episode links; {40-exact} verified series-archive fallbacks; no retired Acast URLs.')
    return 0
if __name__=='__main__': sys.exit(main())
