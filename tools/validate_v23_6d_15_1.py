#!/usr/bin/env python3
"""Validate V23.6D.15.1 layout patch and content integrity."""
from pathlib import Path
from lxml import html

ROOT = Path(__file__).resolve().parents[1]
errors = []
page = ROOT / "categories/latest-uap-news.html"
doc = html.parse(str(page))
cards = doc.xpath('//article[contains(concat(" ",normalize-space(@class)," ")," news-card ")]')
if len(cards) != 18: errors.append(f"expected 18 cards, found {len(cards)}")
if len({c.get('id') for c in cards}) != 18: errors.append("card IDs are not unique")
if sum(bool(c.xpath('.//figure[contains(@class,"news-image")]//img')) for c in cards) != 18: errors.append("image coverage is not 18/18")
if doc.xpath('string(//section[contains(@class,"news-featured")]/h2)').strip() != "Latest Reporting": errors.append("featured heading not updated")
if len(doc.xpath('//button[contains(@class,"news-filter") and @data-filter]')) != 7: errors.append("seven content filters not present")
if len(doc.xpath('//button[contains(@class,"news-filter-clear")]')) != 1: errors.append("clear-filter control missing")
if len(doc.xpath('//section[contains(@class,"news-month")]/h2/span')) != 3: errors.append("monthly article counts missing")
for card in cards:
    if card.get('data-news-status') and card.get('data-news-status') != 'current': errors.append(f"unexpected news status: {card.get('id')}")
    if card.get('data-knowledge-permanence') and card.get('data-knowledge-permanence') != 'permanent': errors.append(f"unexpected permanence: {card.get('id')}")
css = (ROOT / 'style.css').read_text(encoding='utf-8')
for required in ('grid-template-columns:repeat(6,minmax(0,1fr))', '.news-card.news-lead{grid-column:1/-1', '@media print', 'break-inside:avoid'):
    if required not in css: errors.append(f"CSS safeguard missing: {required}")
if 'grid-row:span 2' in css: errors.append("obsolete featured row span remains")
if errors:
    print('V23.6D.15.1 VALIDATION FAILED')
    for error in errors: print('-', error)
    raise SystemExit(1)
print('V23.6D.15.1 validation passed: stable featured grid, 18 cards/images, filters, month counts and lifecycle integrity.')
