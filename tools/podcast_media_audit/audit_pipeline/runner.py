from __future__ import annotations
import logging
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import urlsplit
from .common import now_iso,read_json,write_json
from .detection import detect_platform,detect_destination_type
from .http_client import FetchConfig,fetch
from .metadata import extract
from .identity import compare_identity
from .proposals import proposal_for,build_queues
LOG=logging.getLogger('greyalien.audit')

def classify(job,response,transport,evidence,identity,retry_exhausted):
 h=(urlsplit(job.get('initialUrl','')).hostname or '').lower()
 if transport:
  return ('retired_tracking_wrapper' if h=='link.chtbl.com' else 'network_unavailable',transport)
 if response.status_code==429 and retry_exhausted=='rate_limit_exhausted': return ('temporarily_unverifiable','youtube_rate_limit_exhausted')
 if response.status_code==404:return ('validation_failed','http_404')
 if response.status_code>=400:return ('validation_failed',f'http_{response.status_code}')
 if evidence.get('soft404'):return ('soft_404','soft_404_detected')
 if identity.get('status')=='mismatch':return ('identity_mismatch','episode_identity_mismatch')
 if identity.get('status')=='confirmed':return ('verified','confirmed_identity')
 return ('reachable_unconfirmed','identity_not_confirmed')

def run_one(job,cfg):
 url=job.get('normalizedUrl') or job.get('initialUrl'); response,attempts,transport=fetch(url,cfg)
 redirects=[]; evidence={}; identity={'status':'insufficient_evidence','expected':{},'captured':{}}
 if response is not None:
  redirects=[{'status':r.status_code,'url':r.url,'location':r.headers.get('Location')} for r in response.history]
  evidence=extract(response); identity=compare_identity(job,evidence)
 status,reason=classify(job,response,transport,evidence,identity,'rate_limit_exhausted' if response is not None and response.status_code==429 else None)
 return {'schemaVersion':'2.0.0','jobId':job['jobId'],'validationTimestamp':now_iso(),'validatorVersion':'23.5C.2A','networkEnvironment':'github-actions-compatible','requestedUrl':url,'initialUrl':job.get('initialUrl'),'httpStatus':response.status_code if response is not None else None,'redirectHistory':redirects,'finalUrl':response.url if response is not None else None,'responseTimestamp':now_iso(),'attempts':attempts,'finalValidationStatus':status,'failureReason':reason,'platform':evidence.get('platform') or detect_platform(url),'contentType':evidence.get('contentType'),'destinationType':evidence.get('destinationType') or detect_destination_type(url,detect_platform(url)),'evidence':evidence,'identityComparison':identity,'associatedSeries':job.get('podcastSeries'),'associatedEpisodes':[job.get('entityId')],'repairEligibility':status in {'validation_failed','retired_tracking_wrapper','identity_mismatch','soft_404','reachable_unconfirmed'},'evidenceSummary':f"{status}: HTTP {response.status_code if response is not None else 'transport failure'}; identity={identity.get('status')}"}

def summary(results,proposals):
 c=Counter(r['finalValidationStatus'] for r in results); pc=Counter(r.get('platform') for r in results); dc=Counter(r.get('destinationType') for r in results)
 return {'schemaVersion':'2.0.0','generatedAt':now_iso(),'totalJobs':len(results),'statuses':dict(c),'platformDistribution':dict(pc),'contentTypeDistribution':dict(dc),'repairProposals':len(proposals),'automaticApprovals':sum(p['approvalCategory']=='automatic' for p in proposals),'humanReviewItems':sum(p['approvalCategory']!='automatic' for p in proposals)}

def run_inventory(jobs_path,out_dir,limit=None):
 doc=read_json(jobs_path); jobs=doc.get('jobs',doc if isinstance(doc,list) else []); out=Path(out_dir); out.mkdir(parents=True,exist_ok=True); results=[]; cfg=FetchConfig()
 for i,job in enumerate(jobs[:limit] if limit else jobs,1):
  LOG.info('job %s/%s %s',i,len(jobs),job['jobId']); results.append(run_one(job,cfg))
 verified={r.get('finalUrl') for r in results if r['finalValidationStatus']=='verified'}; proposals=[]
 byid={j['jobId']:j for j in jobs}
 for r in results: proposals.extend(proposal_for(byid[r['jobId']],r,verified))
 queues=build_queues(proposals); write_json(out/'live_validation_results.json',{'schemaVersion':'2.0.0','inventoryVersion':doc.get('version'),'inventoryGeneratedAt':doc.get('generatedAt'),'results':results}); write_json(out/'live_validation_summary.json',summary(results,proposals)); write_json(out/'repair_proposals.json',{'schemaVersion':'1.0.0','proposals':proposals}); write_json(out/'automatic_approval_queue.json',{'schemaVersion':'1.0.0','proposals':queues['automatic']}); write_json(out/'human_review_queue.json',{'schemaVersion':'1.0.0','proposals':queues['human']}); return results,proposals
