#!/usr/bin/env python3
"""Validate V23.6D.15 homepage and UAP news presentation."""
from pathlib import Path
import json
from lxml import html

ROOT = Path(__file__).resolve().parents[1]
errors = []
home = (ROOT / "index.html").read_text(encoding="utf-8")
for expected in ("1,749", "19", "179", "15", "257", "8", "Recently Added to GreyAlien", "V23.6D.15"):
    if expected not in home: errors.append(f"homepage missing {expected!r}")

doc = html.parse(str(ROOT / "categories/latest-uap-news.html"))
cards = doc.xpath('//article[contains(concat(" ",normalize-space(@class)," ")," news-card ")]')
if len(cards) != 18: errors.append(f"expected 18 news cards, found {len(cards)}")
ids = [a.get("id") for a in cards]
if len(ids) != len(set(ids)): errors.append("duplicate news card IDs")
if sum(bool(a.xpath('.//figure[contains(@class,"news-image")]//img')) for a in cards) != 18:
    errors.append("not every news card has an image")
featured = doc.xpath('//div[contains(@class,"news-feature-grid")]/article')
dates = [a.get("data-published") for a in featured]
if dates != ["2026-10-12", "2026-10-09", "2026-10-06", "2026-10-05"]:
    errors.append(f"incorrect featured chronology: {dates}")
if len(doc.xpath('//button[contains(@class,"news-filter") and @data-filter]')) != 7:
    errors.append("expected seven news filters")
for a in cards:
    image = a.xpath('.//figure[contains(@class,"news-image")]//img/@src')
    if image:
        target = (ROOT / "categories" / image[0]).resolve()
        if not target.exists(): errors.append(f"missing image for {a.get('id')}: {image[0]}")
    if not a.xpath('.//div[contains(@class,"news-actions")]'):
        errors.append(f"missing actions for {a.get('id')}")

for path in ROOT.rglob("*.json"):
    try: json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: errors.append(f"invalid JSON {path.relative_to(ROOT)}: {exc}")

if errors:
    print("V23.6D.15 validation FAILED")
    for e in errors: print("-", e)
    raise SystemExit(1)
print("V23.6D.15 validation passed: 18 cards, 18 images, correct featured chronology, metrics and JSON.")
