from __future__ import annotations
import argparse,logging,sys
from pathlib import Path
from .common import read_json,write_json
from .runner import run_inventory
from .reports import generate
from .transaction import preview,apply_media_json
from .validate import validate_schema,validate_jobs_results,validate_proposals,validate_outputs

def main(argv=None):
 p=argparse.ArgumentParser(prog='greyalien-media-audit'); sub=p.add_subparsers(dest='cmd',required=True)
 r=sub.add_parser('run'); r.add_argument('--jobs',required=True); r.add_argument('--out',required=True); r.add_argument('--limit',type=int)
 g=sub.add_parser('reports'); g.add_argument('--results',required=True); g.add_argument('--proposals',required=True); g.add_argument('--out',required=True)
 t=sub.add_parser('transaction-preview'); t.add_argument('--repo-root',required=True); t.add_argument('--proposals',required=True); t.add_argument('--approvals',required=True); t.add_argument('--out',required=True)
 a=sub.add_parser('apply'); a.add_argument('--media-file',required=True); a.add_argument('--manifest',required=True); a.add_argument('--output',required=True)
 v=sub.add_parser('validate'); v.add_argument('--jobs',required=True); v.add_argument('--results',required=True); v.add_argument('--proposals',required=True); v.add_argument('--out',required=True); v.add_argument('--result-schema'); v.add_argument('--proposal-schema')
 args=p.parse_args(argv); logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s',handlers=[logging.StreamHandler(),logging.FileHandler(Path(getattr(args,'out','.') if hasattr(args,'out') else '.').parent/'live_validation_run.log',encoding='utf-8')])
 if args.cmd=='run': run_inventory(args.jobs,args.out,args.limit)
 elif args.cmd=='reports': generate(args.results,args.proposals,args.out)
 elif args.cmd=='transaction-preview': preview(args.repo_root,args.proposals,args.approvals,args.out)
 elif args.cmd=='apply': apply_media_json(args.media_file,args.manifest,args.output)
 elif args.cmd=='validate':
  if args.result_schema: validate_schema(args.results,args.result_schema)
  if args.proposal_schema: validate_schema(args.proposals,args.proposal_schema)
  validate_jobs_results(args.jobs,args.results);validate_proposals(args.proposals);validate_outputs(args.out)
 return 0
if __name__=='__main__':raise SystemExit(main())
