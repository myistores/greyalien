# V23.4 — Somewhere in the Skies Official Media Link Restoration

Base: V23.3 Gateway Restoration Patch

V23.4 removes the forty retired Acast URLs from the 2017 Somewhere in the Skies archive without changing episode content, classifications, canonical entities, topics, or relationships.

## Media reconciliation

- 40 episode/release records audited.
- 40 retired Acast URLs removed from entity media links, reference sources, and gateway archive data.
- 6 stable episode-specific Apple Podcasts or Spotify destinations independently matched by title/date.
- 34 records use the active official Apple Podcasts series archive as an explicitly labeled fallback because a stable episode-specific destination could not be independently confirmed.
- No series-archive fallback is labeled as a direct episode page.

## Validation

`tools/validate_somewhere_in_the_skies_media.py` validates record count, Acast removal, link scope, archive/entity consistency, and fallback labeling. With `--live`, it follows redirects, rejects HTTP errors and rendered not-found pages, confirms the show title, and performs episode-title matching for direct episode links.
