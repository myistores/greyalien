#!/usr/bin/env python3
import csv,json,subprocess,sys,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(root/'tools/audit_cross_series_topics.py'),'--root',str(root)],check=True)
out=root/'reports/v23-5d-2'; r=json.loads((out/'audit-results.json').read_text(encoding='utf-8')); v=json.loads((out/'validation-summary.json').read_text(encoding='utf-8'))
assert r['release']=='V23.5D.2' and r['baseRepository']=='V23.5D.1'
assert r['humanReviewRequired'] is True and r['repositoryMutationDetected'] is False
assert v['repositoryUnchanged'] and v['auditReadOnly'] and v['allHumanDecisionsPending']
assert r['inventory']['podcastEpisodes']>0 and r['inventory']['recognizedCaseEntities']>0
all_rows=[]
for tid in ('ufo-history','historical-ufo-cases','witness-accounts'):
 rows=r['topics'][tid]['candidates']; assert rows; all_rows += rows
 ctx=r['topics'][tid]['destinationTopicContext']; assert ctx['coverageSummary']; assert isinstance(ctx['strengths'],list); assert isinstance(ctx['gaps'],list)
 for x in rows:
  assert x['destinationTopic']==r['topics'][tid]['topic']
  assert 0<=x['topicCoverageScore']<=100
  assert x['researcherBenefitAssessment'] in ('yes','uncertain','no')
  assert x['topicImprovementAssessment']
  assert x['researchValueExplanation'] and x['currentTopicCoverageSummary']
  assert isinstance(x['uniqueContributionAssessment'],list)
  assert isinstance(x['coverageGapFilled'],list)
  assert isinstance(x['improvementCategory'],list) and x['improvementCategory']
  assert x['humanDecision']=='pending'
assert any(x['broadensTopic'] for x in all_rows)
assert any(x['deepensTopic'] for x in all_rows)
assert any(x['caseInheritanceTest']['result']=='pass' for x in r['topics']['historical-ufo-cases']['candidates'])
required=['audit-results.json','candidate-relationship-report.json','destination-topic-research-value-report.json','topic-coverage-analysis.json','coverage-gap-analysis.json','complementary-coverage-report.json','redundancy-analysis-report.json','graph-consistency-report.json','enhanced-human-review-workbook.csv','enhanced-human-review-workbook.xlsx','validation-summary.json','V23_5D_2_DESTINATION_TOPIC_RESEARCH_VALUE_REPORT.md']
assert all((out/x).exists() for x in required)
with (out/'enhanced-human-review-workbook.csv').open(encoding='utf-8') as f:
 rows=list(csv.DictReader(f)); assert len(rows)==len(all_rows); assert all(x['Human Decision']=='pending' for x in rows)
with zipfile.ZipFile(out/'enhanced-human-review-workbook.xlsx') as z:
 assert 'xl/worksheets/sheet1.xml' in z.namelist() and 'xl/worksheets/sheet2.xml' in z.namelist()
print(f"V23.5D.2 validation passed: {len(all_rows)} destination-topic candidates, complete scoring and explanations, enhanced workbook, human gate, and repository protection verified.")
