#!/usr/bin/env python3
import csv,json,subprocess,sys,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(root/'tools/audit_entity_worthiness.py'),'--root',str(root),'--output-dir','reports/v23-5e-1'],check=True)
out=root/'reports/v23-5e-1'; r=json.loads((out/'entity-worthiness-philosophy-results.json').read_text()); v=json.loads((out/'validation-summary.json').read_text())
assert r['release']=='V23.5E.1' and r['baseRepository']=='V23.5E'
assert r['humanReviewRequired'] and not r['repositoryMutationDetected']
assert all(r['philosophy'].values())
assert v['repositoryUnchanged'] and v['auditReadOnly'] and v['allHumanDecisionsPending']
rows=r['results']; assert rows and len(rows)==r['inventory']['entitiesEvaluated']
required={'curatorApprovedEntityType','destinationEligibility','destinationTier','navigationProminence','entityTypeBaseline','entityWorthinessScore','entityTypePercentile','researchValueNarrative','supportingEvidence','justification','humanRecommendation','humanDecision'}
for x in rows:
 assert required <= set(x)
 assert 0<=x['entityWorthinessScore']<=100 and 0<=x['entityTypePercentile']<=100
 assert x['destinationTier'].startswith(('Tier 1','Tier 2','Tier 3','Tier 4'))
 assert x['navigationProminence'] in ('Core Navigation','Featured Research Gateway','Frequently Recommended','Search-Driven Discovery','Contextual Discovery')
 assert x['humanDecision']=='pending'
 if x['curatorApprovedEntityType']: assert x['destinationEligibility']=='Qualifies as a destination'
assert any(x['curatorApprovedEntityType'] for x in rows)
assert any(not x['curatorApprovedEntityType'] for x in rows)
required_files=['entity-worthiness-philosophy-results.json','destination-hierarchy-report.json','entity-type-governance-report.json','navigation-prominence-report.json','entity-type-baseline-analysis.json','enhanced-human-review-workbook.csv','enhanced-human-review-workbook.xlsx','validation-summary.json','DESTINATION_HIERARCHY_REPORT.md','NAVIGATION_PROMINENCE_REPORT.md']
assert all((out/x).exists() for x in required_files)
with (out/'enhanced-human-review-workbook.csv').open(encoding='utf-8-sig') as f:
 data=list(csv.DictReader(f)); assert len(data)==len(rows); assert all(x['Human Decision']=='pending' for x in data)
with zipfile.ZipFile(out/'enhanced-human-review-workbook.xlsx') as z:
 assert all(f'xl/worksheets/sheet{i}.xml' in z.namelist() for i in (1,2,3))
print(f"V23.5E.1 validation passed: {len(rows)} entities evaluated with four-tier hierarchy, entity-type governance, within-type percentiles, navigation prominence, workbook outputs, and read-only protection.")
