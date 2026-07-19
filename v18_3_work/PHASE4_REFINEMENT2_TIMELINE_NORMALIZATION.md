# V17.5 — Timeline Normalization Engine

## Purpose
Prevent one historical event from appearing more than once in an entity timeline when both a dated media record and a dedicated timeline-event record describe the same occurrence.

## Canonical-event rule
A dedicated `timeline_event` record is the canonical timeline representation. Dated media, podcast episode, hearing, document, or publication records may remain separate knowledge entities, but when they point to the same canonical event they are rendered as one timeline card.

## Build assets
- `tools/build_timeline_normalization.py` creates `data/timeline-normalization.json`.
- `tools/validate_timeline_normalization.py` validates aliases, canonical targets, dates, conflicts, and renderer integration.
- `assets/js/entity-engine.js` resolves timeline aliases before rendering and deduplicates by canonical event ID.

## Connection-count rule
The top-level page statistic is labeled **Unique connections**. It counts unique directly connected entity IDs. It is not intended to equal the sum of cards across Related, Referenced In, Timeline, and Continue Research sections because those sections can present the same connected entity from different research perspectives.

## V17.4 regression examples
- `2018-bob-lazar-area-51-flying-saucers` normalizes to `timeline-2018-12-04-bob-lazar-documentary-release`.
- `2026-weaponized-episode-115` normalizes to `timeline-2026-04-14-weaponized-episode-115`.

Jeremy Corbell therefore retains 12 unique graph connections while his Related Timeline displays four canonical historical events rather than six cards.
