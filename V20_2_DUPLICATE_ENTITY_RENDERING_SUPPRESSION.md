# V20.2 — Duplicate Entity Rendering Suppression

## Scope

Rendering-only optimization applied to relationship-based entity cards.

## Behavior

- Resolves each connected entity to a stable real-world identity key before relationship sections render.
- Honors explicit canonical identity fields when present.
- Uses podcast series plus episode number as the stable identity for podcast episodes.
- Uses official episode URLs or normalized type-and-name identities as fallbacks.
- Displays one card per real-world entity.
- Prefers an explicitly canonical entity when available; otherwise prefers the stronger canonical-style record and relationship context.
- Applies the selected card consistently to all relationship sections and Continue Research.

## Verified Example

The duplicate pairs for WEAPONIZED Episodes #74, #75, and #76 resolve to:

- `2025-weaponized-episode-74`
- `2025-weaponized-episode-75`
- `2025-weaponized-episode-76`

The alternate Matthew Brown episode records remain in the repository and all knowledge-graph relationships remain unchanged.

## Exclusions

No changes were made to architecture, schema, templates, navigation, styling, routing, entities, or knowledge-graph relationships.
