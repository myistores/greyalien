#!/usr/bin/env python3
from pathlib import Path
import argparse,json,sys,urllib.request,urllib.error,re
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'tools'))
from podcast_official_media import *
def live_check(record,timeout=12):
    result={'status':'network_validation_unavailable','url':record['url']}
    try:
        req=urllib.request.Request(record['url'],headers={'User-Agent':'GreyAlienMediaValidator/1.0'})
        with urllib.request.urlopen(req,timeout=timeout) as r:
            body=r.read(500000).decode('utf-8','ignore'); final=r.geturl(); code=r.status
        low=body.lower(); notfound=any(x in low for x in ('page not found','404 not found','this video is unavailable'))
        result.update({'httpStatus':code,'finalUrl':final,'status':'validation_failed' if notfound or code>=400 else 'validation_passed','renderedNotFound':notfound})
    except urllib.error.HTTPError as e: result.update({'status':'validation_failed','httpStatus':e.code,'error':str(e)})
    except Exception as e: result.update({'status':'network_validation_unavailable','error':str(e)})
    return result
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--fixtures',action='store_true'); ap.add_argument('--live',action='store_true'); ap.add_argument('--entity'); args=ap.parse_args()
    errors=[]; checked=0
    paths=[ROOT/'data/entities'/f'{args.entity}.json'] if args.entity else list((ROOT/'data/entities').glob('*.json'))
    for p in paths:
        if not p.exists(): errors.append(f'missing entity {p.stem}'); continue
        e=json.loads(p.read_text()); explicit=e.get('officialMedia')
        if isinstance(explicit,list):
            seen=set()
            for i,r in enumerate(explicit):
                checked+=1
                for err in validate_record(r): errors.append(f'{e["id"]}[{i}]: {err}')
                cu=canonical_url(r.get('url',''))
                if cu in seen:errors.append(f'{e["id"]}: duplicate canonical URL {cu}')
                seen.add(cu)
            pref=resolve_preferred(e,preserve_legacy=False)
            if pref and not public_eligible(pref):errors.append(f'{e["id"]}: preferred is not public eligible')
        if args.live:
            for r in collection_for(e):
                if public_eligible(r): print(json.dumps({'entity':e['id'],**live_check(r)}))
    if args.fixtures:
        fx=json.loads((ROOT/'data/test-fixtures/podcast-official-media-fixtures.json').read_text())['fixtures']
        for e in fx:
            records=collection_for(e); checked+=len(records)
            if e['id']=='equivalent-youtube' and len(records)!=1:errors.append('equivalent YouTube URLs were not deduplicated')
            if e['id']=='legacy' and resolve_preferred(e).get('label')!='Existing button':errors.append('legacy primary behavior changed')
            if e['id']=='pending' and resolve_preferred(e).get('destinationType')!='series':errors.append('pending record became preferred')
            if e['id']=='retired' and resolve_preferred(e).get('destinationType')!='series':errors.append('retired record became preferred')
            if e['id'] in ('bad-playlist',):
                if not any(validate_record(r) for r in e['officialMedia']):errors.append('bad playlist fixture was not detected')
    print(f'Universal official-media validation: checked {checked} explicit/fixture records')
    if errors:
        print('UNIVERSAL OFFICIAL-MEDIA VALIDATION FAILED'); print('\n'.join('- '+x for x in errors)); return 1
    print('UNIVERSAL OFFICIAL-MEDIA VALIDATION PASSED'); return 0
if __name__=='__main__':raise SystemExit(main())
