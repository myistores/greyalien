#!/usr/bin/env python3
"""One-command GreyAlien build, automation, validation, and deployment reporting."""
from pathlib import Path
from datetime import datetime, timezone
import argparse,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
STEPS=['build_graph.py','build_podcasts.py','build_related_content.py','build_entity_pages.py','build_homepage.py','build_sitemap.py','validate_graph.py','validate_podcasts.py','build_deployment_report.py']
def main():
 ap=argparse.ArgumentParser(description='Run the complete GreyAlien automation pipeline.')
 ap.add_argument('--report',default='',help='Optional JSON path for the orchestration report')
 args=ap.parse_args(); started=datetime.now(timezone.utc); results=[]
 for script in STEPS:
  p=subprocess.run([sys.executable,str(ROOT/'tools'/script)],cwd=ROOT,text=True,capture_output=True)
  results.append({'step':script,'returnCode':p.returncode,'output':(p.stdout+p.stderr).strip()})
  print(f'[{script}]')
  if p.stdout.strip(): print(p.stdout.strip())
  if p.stderr.strip(): print(p.stderr.strip(),file=sys.stderr)
  if p.returncode:
   write_report(args.report,started,results,'failed'); raise SystemExit(p.returncode)
 write_report(args.report,started,results,'passed')
 print('Automation status: PASSED. Site assets are ready for deployment.')
def write_report(path,started,results,status):
 out=Path(path).resolve() if path else ROOT/'data/automation/last-run.json'; out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps({'startedAt':started.isoformat(),'finishedAt':datetime.now(timezone.utc).isoformat(),'status':status,'steps':results},indent=2)+'\n')
if __name__=='__main__': main()
