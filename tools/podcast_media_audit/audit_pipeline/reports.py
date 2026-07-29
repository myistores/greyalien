from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
from .common import now_iso,read_json,write_json

def generate(results_path,proposals_path,out_dir):
 results=read_json(results_path)['results']; proposals=read_json(proposals_path)['proposals']; out=Path(out_dir); (out/'series').mkdir(parents=True,exist_ok=True)
 pby=defaultdict(list)
 for p in proposals:pby[p.get('jobId')].append(p)
 groups=defaultdict(list)
 for r in results:groups[r.get('associatedSeries') or 'Unknown'].append(r)
 human=[]
 for series,rows in groups.items():
  stats=Counter(r['finalValidationStatus'] for r in rows); rp=[p for r in rows for p in pby[r['jobId']]]
  report={'series':series,'generatedAt':now_iso(),'totalJobs':len(rows),'httpResults':dict(Counter(str(r.get('httpStatus')) for r in rows)),'redirects':sum(bool(r.get('redirectHistory')) for r in rows),'confirmedDestinations':stats['verified'],'identityMismatches':stats['identity_mismatch'],'trackingWrapperFailures':stats['retired_tracking_wrapper'],'temporaryRateLimits':stats['temporarily_unverifiable'],'repairProposals':len(rp),'automaticallyApprovedProposals':sum(p['approvalCategory']=='automatic' for p in rp),'humanReviewItems':sum(p['approvalCategory']!='automatic' for p in rp),'preferredDestinationChanges':0,'remainingFallbacks':sum(r.get('destinationType') in {'series archive','podcast series or show','RSS feed'} for r in rows)}
  slug=series.lower().replace(' ','-').replace('/','-'); write_json(out/'series'/f'{slug}_live_audit_report.json',report)
  human.extend((series,p) for p in rp if p['approvalCategory']!='automatic')
 cross={'generatedAt':now_iso(),'uniqueUrls':len({r.get('requestedUrl') for r in results}),'mediaOccurrences':len(results),'platformDistribution':dict(Counter(r.get('platform') for r in results)),'contentTypeDistribution':dict(Counter(r.get('destinationType') for r in results)),'confirmedEpisodeLinks':sum(r['finalValidationStatus']=='verified' and r.get('destinationType') in {'direct episode','hosted episode page'} for r in results),'seriesArchiveLinks':sum(r.get('destinationType') in {'series archive','podcast series or show'} for r in results),'duplicateDestinations':len(results)-len({r.get('requestedUrl') for r in results}),'failedDestinations':sum(r['finalValidationStatus'] in {'validation_failed','soft_404','identity_mismatch','retired_tracking_wrapper'} for r in results),'temporarilyUnverifiableDestinations':sum(r['finalValidationStatus']=='temporarily_unverifiable' for r in results),'repairs':len(proposals),'reviewQueue':sum(p['approvalCategory']!='automatic' for p in proposals),'remainingRssFallbacks':sum(r.get('destinationType')=='RSS feed' for r in results),'remainingArchiveFallbacks':sum(r.get('destinationType') in {'series archive','podcast series or show'} for r in results)}; write_json(out/'cross_series_live_audit_report.json',cross)
 md=['# Human Review Queue','',f'Generated: {now_iso()}','']
 for series,p in sorted(human,key=lambda x:(x[0],x[1].get('proposedAction',''))):
  md += [f"## {series} — {p['proposalId']}",f"- **What failed:** {p.get('reason') or p['supportingEvidence'].get('failureReason')}",f"- **Original URL:** {p.get('originalUrl')}",f"- **What the system found:** {p['supportingEvidence'].get('evidenceSummary')}",f"- **Proposed correction:** {p.get('proposedAction')}",f"- **Available alternative:** {p.get('replacementUrl') or 'Official replacement research required'}",'- **Reviewer decision:** Approve, reject, or provide an authoritative replacement.','']
 (out/'human_review_report.md').write_text('\n'.join(md),encoding='utf-8')
