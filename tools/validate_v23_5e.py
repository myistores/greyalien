#!/usr/bin/env python3
import csv,json,subprocess,sys,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(root/'tools/audit_entity_worthiness.py'),'--root',str(root)],check=True)
out=root/'reports/v23-5e'; r=json.loads((out/'entity-worthiness-results.json').read_text()); v=json.loads((out/'validation-summary.json').read_text())
assert r['release']=='V23.5E' and r['baseRepository']=='V23.5D.2'
assert r['humanReviewRequired'] and not r['repositoryMutationDetected']
assert v['repositoryUnchanged'] and v['auditReadOnly'] and v['allHumanDecisionsPending']
assert r['inventory']['entitiesEvaluated']>0 and len(r['inventory']['entityTypes'])>=10
rows=r['results']; assert len(rows)==r['inventory']['entitiesEvaluated']
required_tests=['researchDestinationTest','independentKnowledgeTest','relationshipConvergenceTest','longTermSignificanceTest','betterParentTest']
for x in rows:
 assert 0<=x['entityWorthinessScore']<=100
 assert all(k in x for k in required_tests)
 assert x['recommendedKnowledgeRole'] in ('Destination Entity','Supporting Entity','Contextual Metadata')
 assert x['supportingEvidence'] and x['justification'] and x['finalRecommendation'] and x['humanDecision']=='pending'
 assert len(x['scoreFactors'])==10
assert any(x['borderline'] for x in rows); assert any(x['recommendedKnowledgeRole']=='Contextual Metadata' for x in rows); assert any(x['recommendedKnowledgeRole']=='Destination Entity' for x in rows)
required=['entity-worthiness-results.json','destination-entity-report.json','borderline-entity-report.json','contextual-metadata-candidates-report.json','category-quality-analysis.json','enhanced-human-review-workbook.csv','enhanced-human-review-workbook.xlsx','validation-summary.json','ENTITY_WORTHINESS_REPORT.md','DESTINATION_ENTITY_REPORT.md','BORDERLINE_ENTITY_REPORT.md','CONTEXTUAL_METADATA_CANDIDATES_REPORT.md']
assert all((out/x).exists() for x in required)
with (out/'enhanced-human-review-workbook.csv').open(encoding='utf-8-sig') as f:
 data=list(csv.DictReader(f)); assert len(data)==len(rows); assert all(x['Human Decision']=='pending' for x in data)
with zipfile.ZipFile(out/'enhanced-human-review-workbook.xlsx') as z:
 assert all(f'xl/worksheets/sheet{i}.xml' in z.namelist() for i in (1,2,3))
print(f"V23.5E validation passed: {len(rows)} entities evaluated across {len(r['inventory']['entityTypes'])} types; complete scoring, explanations, workbook, human gate, and repository protection verified.")
