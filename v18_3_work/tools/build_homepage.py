#!/usr/bin/env python3
"""Update homepage Latest Additions from generated release and knowledge-base data."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
index_path=ROOT/'index.html'
release=json.loads((ROOT/'data/release-summary.json').read_text(encoding='utf-8'))
entity_index=json.loads((ROOT/'data/entity-index.json').read_text(encoding='utf-8'))
podcast_index=json.loads((ROOT/'data/podcasts/podcast-index.json').read_text(encoding='utf-8'))
episode_index=json.loads((ROOT/'data/podcasts/episode-index.json').read_text(encoding='utf-8'))
entities=entity_index['entities']
counts={}
for e in entities: counts[e['type']]=counts.get(e['type'],0)+1
weaponized=sum(1 for e in episode_index['episodes'] if e.get('seriesId')=='weaponized-podcast')
dev=f'<strong>GreyAlien Version {release["version"]} — {release["title"]}</strong><br>{release["summary"]}'
kb=(f'<strong>Knowledge Graph:</strong> {len(entities)} connected entities across {len(counts)} entity types.<br>'
    f'<strong>Congressional Hearings:</strong> {counts.get("hearing",0)} hearing records in the connected entity system.<br>'
    f'<strong>Witness &amp; Whistleblower Database:</strong> {counts.get("person",0)} people profiles connected to hearings, interviews, organizations, documents, claims and related entities.<br>'
    f'<strong>Podcast Knowledge Base:</strong> {len(podcast_index["podcasts"])} foundational podcast series with {len(episode_index["episodes"])} researched episodes, including {weaponized} WEAPONIZED additions. Podcast totals and related-episode recommendations are generated automatically.<br>'
    '<strong>Latest UAP News:</strong> Coming Soon...<br><strong>Space Exploration:</strong> Coming Soon...<br><strong>Science &amp; Technology:</strong> Coming Soon...<br><strong>Movies &amp; Documentaries:</strong> Coming Soon...<br><strong>Research Library:</strong> Coming Soon...')
html=index_path.read_text(encoding='utf-8')
html,n1=re.subn(r'(<div class="latest-item"><strong>Development Updates</strong><span>).*?(</span></div>)',lambda m:m.group(1)+dev+m.group(2),html,count=1,flags=re.S)
html,n2=re.subn(r'(<div class="latest-item"><strong>Knowledge Base Growth</strong><span>).*?(</span></div>)',lambda m:m.group(1)+kb+m.group(2),html,count=1,flags=re.S)
if n1!=1 or n2!=1: raise SystemExit('Homepage Latest Additions structure was not found exactly once.')
index_path.write_text(html,encoding='utf-8')
print(f'Updated homepage Latest Additions for GreyAlien Version {release["version"]}.')
