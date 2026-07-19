# V17.4 — Phase 4 Refinement 1: Rendering Rules

V17.4 formalizes the first rendering rule uncovered during live testing of the automation engine.

## Rendering Rule 1

> Group relationship cards by the target entity category. Display the relationship itself as the badge on each card.

A page must not create two sections with the same user-facing category solely because the relationships differ.

## Example

Before V17.4, a podcast-series page could render:

- Related Media — `Published`
- Related Media — `Includes Episode`

V17.4 renders one section:

- Related Media
  - Alexandro Wiggins on WEAPONIZED — badge: `Published`
  - WEAPONIZED Episode #21 — badge: `Includes Episode`
  - Additional episodes — badge: `Includes Episode`

## Central configuration

Section categories are defined in:

```text
data/schema/rendering-groups.json
```

The browser renderer reads this configuration directly. Current media grouping includes:

```text
interview + podcast_episode → Media
```

## Validation

The automation pipeline now runs:

```bash
python tools/validate_rendering_rules.py
```

The validator checks that:

- each section key is unique;
- an entity type belongs to only one rendered category;
- interviews and podcast episodes share the Media category;
- the entity renderer uses the centralized configuration.

## Unchanged concepts

The refinement does not merge sections that serve different research purposes. These remain distinct:

- Related Media
- Referenced In
- Continue Research
- Related Timeline
