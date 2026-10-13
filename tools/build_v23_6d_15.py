#!/usr/bin/env python3
"""Build V23.6D.15 homepage accuracy and Latest UAP News presentation."""
from copy import deepcopy
from pathlib import Path
import json
import re
from lxml import html, etree

ROOT = Path(__file__).resolve().parents[1]
NEWS = ROOT / "categories/latest-uap-news.html"

ARTICLE = {
    "secret-directive-uap-reporting-2026-10-12": ("2026-10-12", "government", None),
    "vasco-machine-learning-study-2026-08-10": ("2026-08-10", "science", None),
    "rfk-jr-uap-briefings-2026-10-09": ("2026-10-09", "statements", None),
    "pursue-pr135-bird-analysis-2026-10-06": ("2026-10-06", "sensors", None),
    "aaro-classified-responsive-records-2026-10-05": ("2026-10-05", "government", ("../assets/news/aaro-classified-responsive-records-2026-10.png", "Editorial illustration of classified UAP and USO records in a secure archive. Not documentary imagery.")),
    "podesta-delonge-call-2026-10-01": ("2026-10-01", "statements", ("../assets/news/podesta-delonge-call-confirmation-2026-10.png", "Editorial illustration of the confirmed 2016 discussion. Not documentary imagery of the participants.")),
    "pursue-release-06-2026-09-18": ("2026-09-18", "government", ("../assets/news/pursue-release-06-2026-09.png", "Editorial illustration of a sixth government UAP file release. Not an original government record.")),
    "pursue-disclosure-waiver-2026-09-14": ("2026-09-14", "government", ("../assets/news/pursue-disclosure-waiver-2026-09.png", "Editorial illustration of a protected disclosure channel. Not documentary imagery.")),
    "slysh-haloes-2026-09-09": ("2026-09-09", "space", None),
    "lunar-micron-technosignatures-2026-09-08": ("2026-09-08", "space", ("../assets/news/lunar-micron-technosignatures-2026-09.png", "Concept illustration of proposed lunar-regolith analysis—not a detected technosignature.")),
    "european-uap-barometer-2026-09-02": ("2026-09-02", "science", ("../assets/news/european-uap-barometer-2026-09.png", "Data illustration of European reporting channels and uneven coverage; report counts do not measure underlying phenomenon frequency.")),
    "aaro-nufohrc-access-2026-09-02": ("2026-09-02", "history", ("../assets/news/aaro-nufohrc-private-archives-2026-09.png", "Editorial illustration of private historical records being digitized for authorized research access.")),
    "vasco-scientific-challenge-2026-08-28": ("2026-08-28", "science", ("../assets/news/vasco-scientific-challenge-2026-08.png", "Scientific editorial illustration of archival-plate review—not an original plate or a verdict on the dispute.")),
    "legacy-sol-uap-arms-race-2026-08": ("2026-08-31", "government", None),
    "legacy-rubio-classified-2026-08-21": ("2026-08-21", "statements", None),
    "pursue-kinematic-inference-2026-08-20": ("2026-08-20", "sensors", None),
    "legacy-disclosure-pressure-2026-08-19": ("2026-08-19", "government", None),
    "legacy-alien-life-survey-2026-08-19": ("2026-08-19", "science", None),
}
LEGACY_IDS = [k for k in ARTICLE if k.startswith("legacy-")]

def text(el): return " ".join(el.itertext()).strip()

doc = html.parse(str(NEWS))
prose = doc.xpath('//section[contains(@class,"page-hero")]//div[contains(@class,"prose")]')[0]
articles = prose.xpath('./article[contains(concat(" ",normalize-space(@class)," ")," news-entry ")]')
legacy = iter(LEGACY_IDS)
for a in articles:
    if not a.get("id"):
        a.set("id", next(legacy))

by_id = {a.get("id"): a for a in articles}
missing = set(ARTICLE) - set(by_id)
if missing:
    raise SystemExit(f"Missing expected news articles: {sorted(missing)}")

for article_id, a in by_id.items():
    date, category, image = ARTICLE[article_id]
    a.set("data-published", date)
    a.set("data-category", category)
    a.set("class", "news-entry news-card")
    if image and not a.xpath('.//figure[contains(@class,"news-image")]'):
        fig = html.fragment_fromstring(f'<figure class="news-image"><img src="{image[0]}" alt="{image[1]}" loading="lazy"><figcaption>{image[1]} AI-generated for GreyAlien.</figcaption></figure>')
        h2 = a.xpath('./h2')[0]
        meta = h2.getnext()
        meta.addnext(fig)
    source = a.xpath('.//p[contains(@class,"news-source-link")]/a')
    connected = a.xpath('.//div[contains(@class,"news-related")]//a[starts-with(@href,"../entities/")]')
    if source:
        actions = etree.Element("div", {"class": "news-actions"})
        if connected:
            primary = etree.SubElement(actions, "a", {"class":"button", "href":connected[0].get("href")})
            primary.text = "Explore GreyAlien Record"
        secondary = etree.SubElement(actions, "a", {"class":"button secondary", "href":source[0].get("href"), "target":"_blank", "rel":"noopener noreferrer"})
        secondary.text = "Read Original Source"
        source[0].getparent().addnext(actions)
        source[0].getparent().getparent().remove(source[0].getparent())

for a in articles:
    prose.remove(a)

intro = html.fragment_fromstring('''<div class="news-editorial-intro">
  <p>Current, source-grounded reporting connected to GreyAlien's permanent Research Library and knowledge graph. News can age; knowledge does not.</p>
  <div class="news-filter-bar" role="group" aria-label="Filter UAP news by subject">
    <button class="news-filter active" type="button" data-filter="all">All</button>
    <button class="news-filter" type="button" data-filter="government">Government &amp; disclosure</button>
    <button class="news-filter" type="button" data-filter="science">Scientific research</button>
    <button class="news-filter" type="button" data-filter="sensors">Sensor &amp; video analysis</button>
    <button class="news-filter" type="button" data-filter="space">Space &amp; technosignatures</button>
    <button class="news-filter" type="button" data-filter="history">Historical records</button>
    <button class="news-filter" type="button" data-filter="statements">Statements &amp; testimony</button>
  </div>
  <p class="news-result-count" aria-live="polite"></p>
</div>''')
prose.append(intro)

ordered = sorted(articles, key=lambda a: a.get("data-published"), reverse=True)
featured = etree.SubElement(prose, "section", {"class":"news-featured", "aria-labelledby":"featured-news-heading"})
etree.SubElement(featured, "p", {"class":"kicker"}).text = "Newest reporting"
etree.SubElement(featured, "h2", {"id":"featured-news-heading"}).text = "Latest four"
grid = etree.SubElement(featured, "div", {"class":"news-feature-grid"})
for i, a in enumerate(ordered[:4]):
    clone = deepcopy(a)
    clone.set("class", "news-entry news-card" + (" news-lead" if i == 0 else ""))
    grid.append(clone)

archive = etree.SubElement(prose, "div", {"class":"news-archive"})
months = [("2026-10", "More from October 2026"), ("2026-09", "September 2026"), ("2026-08", "August 2026")]
for prefix, label in months:
    month_articles = [a for a in ordered[4:] if a.get("data-published").startswith(prefix)]
    if not month_articles: continue
    sec = etree.SubElement(archive, "section", {"class":"news-month", "data-news-month":prefix})
    etree.SubElement(sec, "h2").text = label
    month_grid = etree.SubElement(sec, "div", {"class":"news-card-grid"})
    for a in month_articles: month_grid.append(deepcopy(a))

script = html.fragment_fromstring('''<script>
  (() => {
    const buttons = [...document.querySelectorAll('.news-filter')];
    const cards = [...document.querySelectorAll('.news-card')];
    const months = [...document.querySelectorAll('.news-month')];
    const count = document.querySelector('.news-result-count');
    function apply(filter) {
      let visible = 0;
      cards.forEach(card => { const show = filter === 'all' || card.dataset.category === filter; card.hidden = !show; if (show) visible++; });
      months.forEach(month => month.hidden = !month.querySelector('.news-card:not([hidden])'));
      buttons.forEach(button => { const active = button.dataset.filter === filter; button.classList.toggle('active', active); button.setAttribute('aria-pressed', active); });
      count.textContent = `${visible} article${visible === 1 ? '' : 's'} shown`;
    }
    buttons.forEach(button => button.addEventListener('click', () => apply(button.dataset.filter)));
    apply('all');
  })();
</script>''')
body = doc.xpath('//body')[0]
body.insert(len(body)-1, script)
NEWS.write_text('<!doctype html>\n' + etree.tostring(doc.getroot(), encoding='unicode', method='html'), encoding='utf-8')

# Keep structured news data chronological when consumed elsewhere.
news_index = ROOT / "data/news/index.json"
if news_index.exists():
    data = json.loads(news_index.read_text(encoding="utf-8"))
    key = "items" if isinstance(data, dict) and "items" in data else "news"
    if isinstance(data, dict) and isinstance(data.get(key), list):
        data[key].sort(key=lambda item: item.get("publicationDate") or item.get("date") or "", reverse=True)
        news_index.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print(f"Built Latest UAP News with {len(ordered)} chronological cards and {sum(1 for a in ordered if a.xpath('.//figure[contains(@class,\"news-image\")]'))} images.")
