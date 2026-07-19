# GreyAlien V18.2 — Production Batch #2 + Universal Source System

## Podcast ingestion
Added WEAPONIZED Episodes #48–#52. Episode #51 is preserved as an unreleased catalog placeholder because the official series page contains no published subject matter.

## Universal Source System
The generic entity renderer now reads `sources[]` for every entity type. A primary `official_website` source renders as **Visit official website**, other primary source types receive contextual buttons, and remaining structured sources render in an Additional Sources panel.

## Validation
`tools/validate_sources.py` checks link structure, URL validity, primary-source designation, and official-website coverage warnings for organizations and podcast series. It runs automatically through `tools/automate_site.py`.
