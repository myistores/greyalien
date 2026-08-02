#!/usr/bin/env python3
"""Build the visitor-accessible GreyAlien development history page."""
from pathlib import Path
import html
import re

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / 'CHANGELOG.md'
OUTPUT = ROOT / 'development-updates.html'


def render_markdown_history(text: str) -> str:
    parts = []
    in_list = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            if in_list:
                parts.append('</ul>')
                in_list = False
            continue
        heading = re.match(r'^(#{1,3})\s+(.+)$', line)
        if heading:
            if in_list:
                parts.append('</ul>')
                in_list = False
            level = min(len(heading.group(1)) + 1, 4)
            parts.append(f'<h{level}>{html.escape(heading.group(2))}</h{level}>')
        elif line.startswith('- '):
            if not in_list:
                parts.append('<ul>')
                in_list = True
            parts.append(f'<li>{html.escape(line[2:])}</li>')
        else:
            if in_list:
                parts.append('</ul>')
                in_list = False
            parts.append(f'<p>{html.escape(line)}</p>')
    if in_list:
        parts.append('</ul>')
    return '\n'.join(parts)

history = render_markdown_history(CHANGELOG.read_text(encoding='utf-8'))
page = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Development Updates | GreyAlien</title>
  <meta name="description" content="GreyAlien development updates, release notes, implementation summaries and production history.">
  <link rel="stylesheet" href="style.css">
  <meta name="theme-color" content="#07110f">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <link rel="canonical" href="https://greyalien.com/development-updates.html">
  <link rel="icon" type="image/jpeg" href="assets/grey-alien-logo.jpg">
  <meta property="og:site_name" content="GreyAlien">
  <meta property="og:image" content="https://greyalien.com/assets/grey-alien-logo.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <script src="assets/js/site-config.js"></script>
  <script src="assets/js/seo.js"></script>
  <script src="assets/js/analytics.js" defer></script>
</head>
<body>
  <header class="topbar">
    <div class="wrap nav">
      <a class="brand" href="index.html">GreyAlien</a>
      <nav class="nav-links" aria-label="Primary navigation">
        <a href="index.html#explore">Explore</a>
        <a href="index.html#knowledge-graph">Knowledge Graph</a>
        <a href="entities/index.html">Entity Explorer</a>
        <a href="about.html">About</a>
        <a href="https://www.facebook.com/greyaliennews/" target="_blank" rel="noopener">Facebook</a>
      </nav>
    </div>
  </header>
  <main>
    <section class="page-hero development-hero">
      <div class="wrap">
        <p class="kicker">Development Updates</p>
        <h1>How GreyAlien is being built.</h1>
        <div class="prose"><p>This page preserves the technical release history separately from the visitor-facing homepage. It documents production changes, validation work and the continued development of the connected knowledge base.</p></div>
      </div>
    </section>
    <section class="section">
      <div class="wrap development-layout">
        <aside class="panel development-current">
          <p class="kicker">Current release</p>
          <h2>V23.5H — Homepage Refresh &amp; Development Updates</h2>
          <p>Refreshed the homepage with three visitor-facing update cards, graph-generated metrics, consolidated research-growth messaging and a dedicated development-history destination.</p>
          <div class="development-facts">
            <span>Production type<strong>Homepage Enhancement</strong></span>
            <span>Knowledge graph changes<strong>None</strong></span>
            <span>Routing changes<strong>One new static page</strong></span>
          </div>
          <a class="button" href="index.html">Return to homepage</a>
        </aside>
        <article class="panel development-history prose">
          <p class="kicker">Complete release history</p>
          {history}
        </article>
      </div>
    </section>
  </main>
  <footer>
    <div class="wrap footer-grid"><span>© <span id="year"></span> GreyAlien.com</span><a href="index.html">Return home</a></div>
  </footer>
  <script>document.getElementById('year').textContent = new Date().getFullYear();</script>
  <script>
    GreyAlienSEO.apply({{
      title: "Development Updates | GreyAlien",
      description: "GreyAlien development updates, release notes, implementation summaries and production history.",
      canonical: "https://greyalien.com/development-updates.html",
      image: "https://greyalien.com/assets/grey-alien-logo.jpg",
      jsonLd: {{"@context":"https://schema.org","@type":"CollectionPage","name":"GreyAlien Development Updates","url":"https://greyalien.com/development-updates.html","isPartOf":{{"@type":"WebSite","name":"GreyAlien","url":"https://greyalien.com/"}}}}
    }});
  </script>
</body>
</html>
'''
OUTPUT.write_text(page, encoding='utf-8')
print('Built development-updates.html from CHANGELOG.md.')
