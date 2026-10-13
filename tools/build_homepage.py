#!/usr/bin/env python3
"""Build the V23.6D.15 homepage updates and graph-generated metrics."""
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
              <span class="update-version">V23.6D.14</span>
              <strong>Government Reporting Procedures + VASCO Machine Learning</strong>
              <span>Added a carefully attributed government-reporting procedure record and the peer-reviewed machine-learning contribution to the VASCO research debate.</span>
              <a href="categories/latest-uap-news.html#secret-directive-uap-reporting-2026-10-12">Explore the latest ingestion →</a>
            </article>
            <article class="latest-item update-card">
              <span class="update-version">V23.6D.13</span>
              <strong>RFK Jr. UAP Briefing Statements</strong>
              <span>Preserved the interview statements as attributed claims while connecting them to permanent briefing, transition and government-transparency context.</span>
              <a href="categories/latest-uap-news.html#rfk-jr-uap-briefings-2026-10-09">Explore the article →</a>
            </article>
            <article class="latest-item update-card">
              <span class="update-version">V23.6D.12</span>
              <strong>PURSUE Six-Object Infrared Bird Analysis</strong>
              <span>Connected a new scientific paper, its probabilistic bird interpretation and its methodological limits to PURSUE and Image &amp; Video Analysis.</span>
              <a href="categories/latest-uap-news.html#pursue-pr135-bird-analysis-2026-10-06">Explore the research →</a>
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
          <p class="kicker">Recently added</p>
          <h2>Recently Added to GreyAlien</h2>
          {cards}
          <div class="development-link"><a class="button secondary" href="development-updates.html">View complete development history</a></div>
        </aside>'''

html = index_path.read_text(encoding='utf-8')
html, n = re.subn(r'\s*<aside class="panel(?: homepage-updates)?">\s*<p class="kicker">(?:Latest additions|Recently added)</p>.*?</aside>', '\n' + replacement, html, count=1, flags=re.S)
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
if n == 0:
    html, n = re.subn(r'\s*<section class="section research-growth".*?</section>', '\n' + growth, html, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Research growth section was not found exactly once.')

# Current release information and development link in the homepage footer.
footer = '''  <footer>
    <div class="wrap footer-grid">
      <span>© <span id="year"></span> GreyAlien.com</span>
      <span>V23.6D.15 — Homepage &amp; UAP News Experience · <a href="development-updates.html">Development Updates</a></span>
    </div>
  </footer>'''
html, n = re.subn(r'  <footer>.*?</footer>', footer, html, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Homepage footer was not found exactly once.')

index_path.write_text(html, encoding='utf-8')
print(f'Built V23.6D.15 homepage with {len(entities)} entities across {len(counts)} entity types.')
