#!/usr/bin/env python3
import csv,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(root/'tools/audit_cross_series_topics.py'),'--root',str(root)],check=True)
out=root/'reports/v23-5d-1'; r=json.loads((out/'audit-results.json').read_text(encoding='utf-8'))
assert r['release']=='V23.5D.1'
assert r['baseRepository']=='V23.5D'
assert r['humanReviewRequired'] is True
assert r['repositoryMutationDetected'] is False
assert r['inventory']['podcastEpisodes']>0
assert r['inventory']['recognizedCaseEntities']>0
assert r['inventory']['episodesWithCasePaths']>0
for tid in ('ufo-history','historical-ufo-cases','witness-accounts'):
    rows=r['topics'][tid]['candidates']; assert rows
    for x in rows:
        assert x['discoveryMethod'] in ('Metadata Discovery','Knowledge Graph Discovery','Hybrid Discovery')
        assert x['subjectRelevanceTest']['result'] in ('pass','fail','needs_review')
        assert x['researchValueTest']['result'] in ('pass','fail','needs_review')
        assert x['caseInheritanceTest']['result'] in ('pass','fail','not_applicable')
        assert x['humanDecision']=='pending'
        assert x['relationshipExplanation']
case_rows=r['topics']['historical-ufo-cases']['candidates']
assert any(x['caseInheritanceTest']['result']=='pass' for x in case_rows)
assert any(x['discoveryMethod'] in ('Knowledge Graph Discovery','Hybrid Discovery') for x in case_rows)
required=['audit-results.json','candidate-relationship-report.json','graph-consistency-report.json','case-inheritance-analysis.json','human-approval-worksheet.csv','V23_5D_1_CROSS_SERIES_TOPIC_RELATIONSHIP_AUDIT.md']
assert all((out/x).exists() for x in required)
with (out/'human-approval-worksheet.csv').open(encoding='utf-8') as f:
    rows=list(csv.DictReader(f)); assert rows and all(x['humanDecision']=='pending' for x in rows)
print('V23.5D.1 validation passed: graph traversal, three-stage tests, reports, human gate, and repository protection verified.')
