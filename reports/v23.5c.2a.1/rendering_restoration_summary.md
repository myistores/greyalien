# V23.5C.2A.1 Rendering Restoration Summary

## Root cause
The V23.5A universal helper was present but `entities/entity.html` did not load it. The entity renderer detected `officialMedia`, suppressed legacy panels, then received an empty helper result because `window.GreyAlienOfficialMedia` was undefined.

## Repaired components
- Loaded the compatibility helper before the entity renderer.
- Restored preferred-media actions and deduplicated alternates for episode and series entities.
- Added mixed-state support for `officialMedia`, `official_media`, and legacy media fields.
- Restored preferred actions in the Somewhere in the Skies gateway and podcast directory.
- Added permanent build-failure validation when eligible media exists without a public action.

## Verification
- Podcast records checked: 261
- Episode records checked: 257
- Validation errors: 0
- Need to Know Episodes 13 and 14 preserve their existing approved direct YouTube identities.
- No official-media data or knowledge-graph JSON was rewritten.

## Remaining issues
None detected.
