#!/usr/bin/env python3
"""Validate one import record or a directory of JSON records without changing the site."""
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import argparse, json, re, sys
ROOT=Path(__file__).resolve().parents[1]
KNOWN_TYPES={'person','hearing','organization','document','topic','case','interview','podcast_episode','podcast_series','legislation','timeline_event','publication','claim','media_series'}
ID_RE=re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
DATE_RE=re.compile(r'^\d{4}-\d{2}-\d{2}$')

def files_for(path):
    return sorted(path.glob('*.json')) if path.is_dir() else [path]

def validate(e, existing_ids, batch_ids):
    errors=[]; warnings=[]; eid=e.get('id','<missing-id>')
    for k in ('id','type','name','summary','relationships','sources'):
        if k not in e or e[k] in ('',None): errors.append(f'{eid}: missing required field {k}')
    if e.get('id') and not ID_RE.match(e['id']): errors.append(f'{eid}: id must use lowercase kebab-case')
    if e.get('type') not in KNOWN_TYPES: errors.append(f'{eid}: unsupported entity type {e.get("type")}')
    if not isinstance(e.get('relationships',[]),list): errors.append(f'{eid}: relationships must be an array')
    if not isinstance(e.get('sources',[]),list): errors.append(f'{eid}: sources must be an array')
    if e.get('date'):
        try: datetime.strptime(e['date'],'%Y-%m-%d')
        except Exception: errors.append(f'{eid}: date must use YYYY-MM-DD')
    seen=set()
    for i,r in enumerate(e.get('relationships',[]) if isinstance(e.get('relationships',[]),list) else []):
        if not isinstance(r,dict) or not r.get('type') or not r.get('target'):
            errors.append(f'{eid}: relationship {i+1} requires type and target'); continue
        key=(r['type'],r['target'],r.get('role',''))
        if key in seen: warnings.append(f'{eid}: duplicate relationship {key}')
        seen.add(key)
        if r['target'] not in existing_ids and r['target'] not in batch_ids:
            warnings.append(f'{eid}: unresolved relationship target {r["target"]}')
    primary=0
    for i,s in enumerate(e.get('sources',[]) if isinstance(e.get('sources',[]),list) else []):
        if not isinstance(s,dict) or not s.get('label') or not s.get('url'):
            errors.append(f'{eid}: source {i+1} requires label and url'); continue
        u=urlparse(s['url'])
        if u.scheme not in ('http','https') or not u.netloc: errors.append(f'{eid}: invalid source URL {s["url"]}')
        if s.get('primary'): primary+=1
    if e.get('sources') and primary==0: warnings.append(f'{eid}: no source marked primary')
    if e.get('type')=='podcast_episode':
        for k in ('date','seriesId','episodeNumber','episodeTitle'):
            if e.get(k) in ('',None): errors.append(f'{eid}: podcast episode missing {k}')
        ep=[r for r in e.get('relationships',[]) if r.get('type')=='episode_of']
        if len(ep)!=1: errors.append(f'{eid}: podcast episode requires exactly one episode_of relationship')
        elif ep[0].get('target')!=e.get('seriesId'): errors.append(f'{eid}: episode_of target must match seriesId')
        if not any(r.get('role') in ('host','co_host') for r in e.get('relationships',[])): errors.append(f'{eid}: podcast episode requires host/co_host relationship')
    return errors,warnings

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('path'); ap.add_argument('--json-report'); args=ap.parse_args()
    path=Path(args.path).resolve(); fs=files_for(path)
    if not fs: raise SystemExit('No JSON records found.')
    records=[]; parse_errors=[]
    for f in fs:
        try: records.append((f,json.loads(f.read_text(encoding='utf-8'))))
        except Exception as ex: parse_errors.append(f'{f.name}: invalid JSON: {ex}')
    existing={p.stem for p in (ROOT/'data/entities').glob('*.json')}; batch={e.get('id') for _,e in records if e.get('id')}
    errors=list(parse_errors); warnings=[]
    if len(batch)!=len(records): errors.append('Batch contains duplicate or missing entity ids.')
    for _,e in records:
        er,wa=validate(e,existing,batch); errors+=er; warnings+=wa
    report={'path':str(path),'recordCount':len(records),'errors':errors,'warnings':warnings,'valid':not errors}
    if args.json_report: Path(args.json_report).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'Validated {len(records)} import record(s): {len(errors)} error(s), {len(warnings)} warning(s).')
    for x in errors: print('ERROR:',x)
    for x in warnings: print('WARNING:',x)
    sys.exit(1 if errors else 0)
if __name__=='__main__': main()
