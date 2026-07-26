#!/usr/bin/env python3
"""Finalize a reviewed V23 podcast draft for the normal import pipeline.

This command does not decide classifications. A reviewer must edit the draft first,
then explicitly approve it. The approved JSON is written to a separate directory.
"""
from pathlib import Path
import argparse, json

def main():
    ap=argparse.ArgumentParser(description='Approve a human-reviewed V23 podcast draft.')
    ap.add_argument('draft'); ap.add_argument('--out-dir',required=True); ap.add_argument('--reviewer',required=True)
    args=ap.parse_args(); src=Path(args.draft).resolve(); e=json.loads(src.read_text(encoding='utf-8'))
    c=e.get('classification')
    if e.get('type')!='podcast_episode' or not isinstance(c,dict): raise SystemExit('Draft is not a classified podcast_episode.')
    required=('contentClass','episodeType','primaryTopics','secondaryTopics','researchAccelerator','entityExtraction','confidence')
    missing=[k for k in required if k not in c]
    if missing: raise SystemExit('Classification missing: '+', '.join(missing))
    if c['contentClass']=='research' and c['researchAccelerator']!='full': raise SystemExit('Research episodes must use full Research Accelerator depth.')
    if c['contentClass']=='catalog' and e.get('principalClaims'): raise SystemExit('Catalog records must not contain principal claims.')
    c['reviewRequired']=False; c['reviewedBy']=args.reviewer; c['reviewStatus']='approved'
    out=Path(args.out_dir).resolve(); out.mkdir(parents=True,exist_ok=True); dst=out/src.name
    dst.write_text(json.dumps(e,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'Approved classified record written to {dst}')
    print('Run validate_import_record.py and import_batch.py before publication.')
if __name__=='__main__': main()
