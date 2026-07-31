# V23.5C.4 Live URL and UI Pilot Report

## Inventory

- Spotify direct episode URLs: 10
- YouTube direct watch URLs: 9
- Episode 1 YouTube URL: intentionally absent
- All stored URLs were normalized to canonical episode/watch form.

## Pre-deployment validation

- Repository record validation passed for all 19 supplied direct URLs.
- Nine Spotify pages returned the expected Somewhere in the Skies episode title during online inspection.
- Spotify Episode 5 returned HTTP 429 during the inspection attempt, so it remains scheduled for confirmation in the deployed UI pilot rather than being treated as a content mismatch.
- The online fetch service throttled the YouTube page requests. Their canonical watch-video structure and supplied video identifiers were preserved, but final click-through confirmation is required after deployment.

## Rendering behavior

- Episodes 2–10 render `Watch on YouTube` and `Listen on Spotify` as direct action buttons.
- Episode 1 renders only `Listen on Spotify`.
- Retained Apple destinations render below the direct actions as secondary resource rows.
- Direct actions wrap on narrow screens; the rest of the episode page and media architecture are unchanged.

## Required live inspection after deployment

Open Episodes 1–10 and confirm each button reaches the intended episode. Pay particular attention to Spotify Episode 5 and all nine YouTube destinations because automated pre-deployment access was throttled.
