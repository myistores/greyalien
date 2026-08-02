#!/usr/bin/env python3
"""Build the V23.5H homepage updates and graph-generated metrics."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
index_path = ROOT / 'index.html'
entity_index = json.loads((ROOT / 'data/entity-index.json').read_text(encoding='utf-8'))
podcast_index = json.loads((ROOT / 'data/podcasts/podcast-index.json').read_text(encoding='utf-8'))
episode_index = json.loads((ROOT / 'data/podcasts/episode-index.json').read_text(encoding='utf-8'))
entities = entity_index['entities']
counts = {}
for entity in entities:
    counts[entity['type']] = counts.get(entity['type'], 0) + 1

cards = f'''<div class="latest update-card-grid">
            <article class="latest-item update-card">
              <span class="update-version">V23.5G</span>
              <strong>Organization Taxonomy Rationalization</strong>
              <span>Improved the Organization collection by reclassifying programs, research projects, advisory panels, facilities, military assets and media outlets into more accurate entity types while preserving established knowledge connections.</span>
              <a href="development-updates.html">Read the development details →</a>
            </article>
            <article class="latest-item update-card">
              <span class="update-version">V23.5F</span>
              <strong>Topic Taxonomy Rationalization</strong>
              <span>Refined visible Topics into clearer research destinations, consolidated duplicate terminology and moved supporting classifications out of the visitor-facing Topic inventory without losing relationships.</span>
              <a href="development-updates.html">Read the development details →</a>
            </article>
            <article class="latest-item update-card">
              <span class="update-version">Connected research</span>
              <strong>Podcast Knowledge Base</strong>
              <span>Explore {len(episode_index['episodes']):,} researched episodes across {len(podcast_index['podcasts']):,} podcast series, connected to people, cases, organizations, documents, claims and research topics throughout GreyAlien.</span>
              <a href="categories/podcasts.html">Explore podcasts →</a>
            </article>
          </div>'''

metrics = f'''<div class="homepage-metrics" aria-label="Current GreyAlien knowledge-base totals">
            <div><strong>{len(entities):,}</strong><span>Entities</span></div>
            <div><strong>{len(counts):,}</strong><span>Entity types</span></div>
            <div><strong>{counts.get('person', 0):,}</strong><span>People</span></div>
            <div><strong>{counts.get('hearing', 0):,}</strong><span>Hearings</span></div>
            <div><strong>{len(episode_index['episodes']):,}</strong><span>Podcast episodes</span></div>
            <div><strong>{len(podcast_index['podcasts']):,}</strong><span>Podcast series</span></div>
          </div>'''

replacement = f'''        <aside class="panel homepage-updates">
          <p class="kicker">Latest additions</p>
          <h2>Recent knowledge-base improvements</h2>
          {cards}
          <div class="development-link"><a class="button secondary" href="development-updates.html">View complete development history</a></div>
        </aside>'''

html = index_path.read_text(encoding='utf-8')
html, n = re.subn(r'\s*<aside class="panel">\s*<p class="kicker">Latest additions</p>.*?</aside>', '\n' + replacement, html, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Latest Additions panel was not found exactly once.')

# Insert or replace the generated metrics directly after the graph section.
metrics_section = f'''    <section class="section metrics-section" aria-labelledby="current-scale">
      <div class="wrap">
        <div class="section-head">
          <div><p class="kicker">Current knowledge base</p><h2 id="current-scale">GreyAlien by the numbers</h2></div>
          <p>These totals are generated automatically from the current knowledge graph and podcast indexes each time the site is built.</p>
        </div>
        {metrics}
      </div>
    </section>'''
html = re.sub(r'\s*<section class="section metrics-section".*?</section>', '', html, count=1, flags=re.S)
anchor = '    <section class="section" id="featured">'
if anchor not in html:
    raise SystemExit('Featured section anchor not found.')
html = html.replace(anchor, metrics_section + '\n\n' + anchor, 1)

# Replace the obsolete standalone release notice with one research-growth statement.
growth = '''    <section class="section research-growth" aria-labelledby="research-growth-heading">
      <div class="wrap panel cta">
        <p class="kicker">Research growth</p>
        <h2 id="research-growth-heading">GreyAlien’s connected collections continue to expand.</h2>
        <p>New research will strengthen UAP news, space exploration, science and technology, movies and documentaries, and the Research Library as source-supported material is added to the knowledge graph.</p>
        <a class="button secondary" href="development-updates.html">Follow development updates</a>
      </div>
    </section>'''
html, n = re.subn(r'\s*<section class="section" aria-labelledby="v235c1-update">.*?</section>', '\n' + growth, html, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Obsolete V23.5C.1 development notice was not found exactly once.')

# Current release information and development link in the homepage footer.
footer = '''  <footer>
    <div class="wrap footer-grid">
      <span>© <span id="year"></span> GreyAlien.com</span>
      <span>V23.5H — Homepage Refresh · <a href="development-updates.html">Development Updates</a></span>
    </div>
  </footer>'''
html, n = re.subn(r'  <footer>.*?</footer>', footer, html, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Homepage footer was not found exactly once.')

index_path.write_text(html, encoding='utf-8')
print(f'Built V23.5H homepage with {len(entities)} entities across {len(counts)} entity types.')
