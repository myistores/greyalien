#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
required=[ROOT/'tools/research_accelerator.py',ROOT/'data/research-accelerator/templates/batch-manifest.json']
errors=[]
for p in required:
    if not p.exists(): errors.append(f'Missing {p.relative_to(ROOT)}')
if not errors:
    with tempfile.TemporaryDirectory() as td:
        p=subprocess.run([sys.executable,str(ROOT/'tools/research_accelerator.py'),str(ROOT/'data/research-accelerator/fixtures/test-manifest.json'),'--offline-dir',str(ROOT/'data/research-accelerator/fixtures'),'--no-network','--out',td],cwd=ROOT,text=True,capture_output=True)
        if p.returncode: errors.append('Fixture run failed: '+p.stdout+p.stderr)
        else:
            drafts=list((Path(td)/'drafts').glob('*.json')); reviews=list((Path(td)/'reviews').glob('*.json'))
            if len(drafts)!=1 or len(reviews)!=1: errors.append('Fixture did not create exactly one draft and review')
            else:
                d=json.loads(drafts[0].read_text()); r=json.loads(reviews[0].read_text())
                if d.get('episodeNumber')!=57: errors.append('Episode number extraction failed')
                if not any(x.get('target')=='thiago-ticchetti' for x in d.get('relationships',[])): errors.append('Existing entity matching failed')
                if r.get('confidenceScore',0)<70: errors.append('Fixture confidence unexpectedly low')
print(f'Research Accelerator validation: {len(errors)} error(s).')
for e in errors: print('ERROR:',e)
raise SystemExit(1 if errors else 0)
