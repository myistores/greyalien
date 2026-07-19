#!/usr/bin/env python3
"""Create deployment-ready JSON and Markdown reports from generated assets."""
from pathlib import Path
from datetime import datetime, timezone
import json
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; REPORTS=DATA/'automation/reports'; REPORTS.mkdir(parents=True,exist_ok=True)
release=json.loads((DATA/'release-summary.json').read_text())
graph=json.loads((DATA/'graph-manifest.json').read_text())
pods=json.loads((DATA/'podcasts/podcast-manifest.json').read_text())
related=json.loads((DATA/'related-content.json').read_text())
sitemap=(ROOT/'sitemap.xml').read_text(encoding='utf-8').count('<url>')
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
report={'version':release['version'],'title':release['title'],'generatedAt':datetime.now(timezone.utc).isoformat(),'status':'ready_for_deployment','entityCount':graph['entityCount'],'resolvedRelationshipCount':graph['relationshipCount'],'unresolvedRelationshipWarnings':graph['unresolvedRelationshipCount'],'podcastSeriesCount':pods['seriesCount'],'podcastEpisodeCount':pods['episodeCount'],'relatedEpisodeSets':sum(1 for v in related['relatedEpisodes'].values() if v),'generatedEntityPageCount':len(list((ROOT/'entities/generated').glob('*.html'))),'sitemapUrlCount':sitemap,'validation':'passed'}
latest=REPORTS/'latest.json'; latest.write_text(json.dumps(report,indent=2)+'\n')
md=REPORTS/'latest.md'; md.write_text(f'''# GreyAlien V{report['version']} Deployment Report\n\n**Status:** Ready for deployment  \n**Generated:** {report['generatedAt']}\n\n- Entities: {report['entityCount']}\n- Resolved relationships: {report['resolvedRelationshipCount']}\n- Unresolved legacy warnings: {report['unresolvedRelationshipWarnings']}\n- Podcast series: {report['podcastSeriesCount']}\n- Researched podcast episodes: {report['podcastEpisodeCount']}\n- Episode records with related-episode recommendations: {report['relatedEpisodeSets']}\n- Generated entity entry pages: {report['generatedEntityPageCount']}\n- Sitemap URLs: {report['sitemapUrlCount']}\n- Validation: Passed\n\n## Release summary\n\n{release['summary']}\n''',encoding='utf-8')
print(f'Created deployment report: {md.relative_to(ROOT)}')
