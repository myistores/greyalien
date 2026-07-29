# V23.5C.2A.1 — Podcast Official Media Link Rendering Restoration

## Scope
Rendering and compatibility repair only. No podcast URLs, metadata, classifications, entities, relationships, claims, timelines, IDs, or routes are changed.

## Rendering pipeline

```text
Podcast entity JSON
  ↓
officialMedia / official_media / preserved legacy fields
  ↓
assets/js/podcast-official-media.js compatibility adapter
  ↓
destination-aware eligibility, deduplication, and preferred resolution
  ↓
entity-engine.js / podcast-directory.js / somewhere-in-the-skies-gateway.js
  ↓
visible, accessible HTML anchors
```

## Root cause
`assets/js/podcast-official-media.js` existed, but `entities/entity.html` did not load it. `entity-engine.js` recognized migrated `officialMedia`, suppressed the legacy panels, and then rendered no replacement because the compatibility helper was undefined.

## Repair
- Loads the universal helper before the entity renderer.
- Combines `officialMedia`, optional `official_media`, and legacy fields for mixed migration and rollback states.
- Deduplicates by canonical URL.
- Selects preferred destinations using the V23.5A hierarchy.
- Renders a visible preferred action and eligible alternates.
- Restores series-directory and Somewhere in the Skies gateway actions.
- Prevents direct-episode labeling for playlist, channel, series, archive, and feed destinations.

## Preferred hierarchy
1. Official hosted episode page
2. Official YouTube episode
3. Apple Podcasts episode
4. Spotify episode
5. Other verified episode
6. Official series destination
7. RSS

## Permanent regression validation
Run:

```bash
python tools/validate_v23_5c2a1.py
```

The validator fails when eligible official media exists but no public action can be rendered, when more than one preferred action is produced, when a non-episode destination outranks an available direct episode, or when the helper is not integrated into the public renderers.

## Diagnostics and reports
Generated under `reports/v23.5c.2a.1/`:
- `rendering_diagnostics.json`
- `rendering_restoration_summary.md`
- Per-series rendering reports for WEAPONIZED, Need to Know, MERGED, and Somewhere in the Skies

## Data integrity
The release does not rewrite podcast entity JSON. Existing corrected destinations for Need to Know Episodes 13 and 14 remain unchanged.
