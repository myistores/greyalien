import unittest
from audit_pipeline.proposals import proposal_for,consolidate_proposals
class ProposalTests(unittest.TestCase):
 def test_related_findings_one_proposal(self):
  job={'jobId':'j1','initialUrl':'https://podcasts.apple.com/us/podcast/x/id123','platform':'Apple Podcasts','destinationType':'direct episode','podcastSeries':'X'}
  result={'finalValidationStatus':'reachable_unconfirmed','finalUrl':job['initialUrl'],'httpStatus':200,'redirectHistory':[],'evidenceSummary':'x','failureReason':'x','evidence':{'platform':'Apple Podcasts','destinationType':'podcast series or show'},'identityComparison':{'status':'insufficient_evidence','identityScore':20,'expected':{},'captured':{}}}
  ps=proposal_for(job,result);self.assertEqual(len(ps),1);self.assertGreaterEqual(ps[0]['mergedProposalCount'],2);self.assertIn('direct_episode_degraded_to_show_page',ps[0]['supportingReasons'])
 def test_duplicate_keys_collapse(self):
  p={'deduplicationKey':'x','mergedProposalCount':1,'supportingReasons':['a'],'replacementCandidates':[]}
  out=consolidate_proposals([dict(p),dict(p)]);self.assertEqual(len(out),1);self.assertEqual(out[0]['mergedProposalCount'],2)
if __name__=='__main__':unittest.main()
