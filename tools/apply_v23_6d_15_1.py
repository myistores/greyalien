#!/usr/bin/env python3
"""Apply V23.6D.15.1 permanent-record headline routing."""
from pathlib import Path
from lxml import html, etree

ROOT = Path(__file__).resolve().parents[1]
page = ROOT / "categories/latest-uap-news.html"
doc = html.parse(str(page))
changed = 0
for card in doc.xpath('//article[contains(concat(" ",normalize-space(@class)," ")," news-card ")]'):
    heading = card.xpath('./h2/a')[0]
    primary = card.xpath('.//div[contains(@class,"news-actions")]/a[1]')
    if primary and primary[0].get('href', '').startswith('../entities/'):
        heading.set('href', primary[0].get('href'))
        heading.attrib.pop('target', None)
        heading.attrib.pop('rel', None)
        changed += 1
page.write_text('<!doctype html>\n' + etree.tostring(doc.getroot(), encoding='unicode', method='html'), encoding='utf-8')
print(f'Routed {changed} news headlines to permanent GreyAlien records.')
