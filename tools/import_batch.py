#!/usr/bin/env python3
"""Transactional bulk importer for GreyAlien entities and podcast episodes."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, shutil, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]; ENT=ROOT/'data/entities'; REPORTS=ROOT/'data/imports/reports'
BUILD=('build_graph.py','build_podcasts.py','build_related_content.py','build_entity_pages.py','build_homepage.py','build_sitemap.py','validate_graph.py','validate_podcasts.py','build_deployment_report.py')

def run(script,*args,cwd=ROOT):
    return subprocess.run([sys.executable,str(ROOT/'tools'/script),*map(str,args)],cwd=cwd,text=True,capture_output=True)

def main():
    ap=argparse.ArgumentParser(description='Validate and transactionally import JSON records.')
    ap.add_argument('path',help='JSON file or directory containing JSON files')
    ap.add_argument('--dry-run',action='store_true'); ap.add_argument('--replace',action='store_true'); args=ap.parse_args()
    src=Path(args.path).resolve(); files=sorted(src.glob('*.json')) if src.is_dir() else [src]
    if not files or not all(f.exists() for f in files): raise SystemExit('No import JSON files found.')
    REPORTS.mkdir(parents=True,exist_ok=True); stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    report={'startedAt':datetime.now(timezone.utc).isoformat(),'source':str(src),'dryRun':args.dry_run,'replace':args.replace,'files':[f.name for f in files],'status':'started','steps':[]}
    with tempfile.TemporaryDirectory(prefix='greyalien-import-') as td:
        stage=Path(td)/'site'; shutil.copytree(ROOT,stage,ignore=shutil.ignore_patterns('.git','*.zip','data/imports/reports'))
        stage_import=Path(td)/'records'; stage_import.mkdir()
        for f in files: shutil.copy2(f,stage_import/f.name)
        val=subprocess.run([sys.executable,str(stage/'tools/validate_import_record.py'),str(stage_import)],cwd=stage,text=True,capture_output=True)
        report['steps'].append({'name':'validate_records','returnCode':val.returncode,'output':val.stdout+val.stderr})
        if val.returncode: report['status']='validation_failed'; return finish(report,stamp,1)
        imported=[]
        for f in sorted(stage_import.glob('*.json')):
            e=json.loads(f.read_text(encoding='utf-8')); dst=stage/'data/entities'/f'{e["id"]}.json'
            if dst.exists() and not args.replace:
                report['status']='conflict'; report['steps'].append({'name':'conflict','output':f'{e["id"]} already exists; rerun with --replace.'}); return finish(report,stamp,1)
            shutil.copy2(f,dst); imported.append(e['id'])
        for script in BUILD:
            p=subprocess.run([sys.executable,str(stage/'tools'/script)],cwd=stage,text=True,capture_output=True)
            report['steps'].append({'name':script,'returnCode':p.returncode,'output':p.stdout+p.stderr})
            if p.returncode: report['status']='build_failed'; return finish(report,stamp,1)
        report['importedIds']=imported
        if args.dry_run:
            report['status']='dry_run_passed'; return finish(report,stamp,0)
        # Commit only mutable generated/data outputs after all staged checks pass.
        backup=Path(td)/'backup'; backup.mkdir()
        for eid in imported:
            live=ENT/f'{eid}.json'
            if live.exists(): shutil.copy2(live,backup/live.name)
            shutil.copy2(stage/'data/entities'/f'{eid}.json',live)
        for rel in ('data/entity-index.json','data/graph-manifest.json','data/podcasts','data/related-content.json','data/automation','entities/generated','index.html','sitemap.xml'):
            source=stage/rel; target=ROOT/rel
            if target.exists():
                if target.is_dir(): shutil.rmtree(target)
                else: target.unlink()
            if source.is_dir(): shutil.copytree(source,target)
            else: target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,target)
        report['status']='committed'; return finish(report,stamp,0)

def finish(report,stamp,code):
    report['finishedAt']=datetime.now(timezone.utc).isoformat(); out=REPORTS/f'import-{stamp}.json'
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'Import status: {report["status"]}. Report: {out.relative_to(ROOT)}')
    for step in report.get('steps',[]):
        text=step.get('output','').strip()
        if text: print(f'[{step["name"]}]\n{text}')
    raise SystemExit(code)
if __name__=='__main__': main()
