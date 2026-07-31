#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(root/'tools/audit_cross_series_topics.py'),'--root',str(root)],check=True)
r=json.loads((root/'reports/v23-5d/audit-results.json').read_text(encoding='utf-8'))
assert r['release']=='V23.5D'
assert r['humanReviewRequired'] is True
assert r['repositoryMutationDetected'] is False
assert r['inventory']['podcastEpisodes']>0
for tid in ('ufo-history','historical-ufo-cases','witness-accounts'):
    assert tid in r['topics']
    assert r['topics'][tid]['current']['outgoingRelationships']==0
    assert r['topics'][tid]['proposed']
print('V23.5D validation passed: analysis artifacts generated; entity data unchanged.')
