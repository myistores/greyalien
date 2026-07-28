## V23.5B migration audit

The four production podcast collections were reconciled across legacy media fields and migrated into approved `officialMedia` collections. The migration covers 257 episodes and four series entities, preserves Need to Know Episode 13/14 corrections and all 40 Somewhere in the Skies 2017 records, and reports zero non-media changes. Detailed reports are in `data/migration/v23.5b/`.

# GreyAlien Podcast Audit — Version 15.0

| Podcast | Hosts | Launch | Connections | Website | YouTube | Spotify | Apple |
|---|---|---:|---:|---:|---:|---:|---:|
| WEAPONIZED | Jeremy Corbell, George Knapp | 2023 | 4 | Yes | Yes | Yes | Yes |
| Need to Know | Bryce Zabel, Ross Coulthart | 2021 | 2 | Yes | Yes | Yes | Yes |
| Merged | Ryan Graves | 2022 | 3 | Yes | Yes | Yes | Yes |
| The Black Vault Radio | John Greenewald Jr. | 2018 | 2 | Yes | Yes | Yes | Yes |
| Theories of Everything | Curt Jaimungal | 2020 | 1 | Yes | Yes | Yes | Yes |
| Engaging the Phenomenon | James Iandoli | 2018 | 1 | Yes | Yes | Yes | No |
| That UFO Podcast | Andy McGrillen | 2020 | 1 | Yes | Yes | Yes | Yes |
| Somewhere in the Skies | Ryan Sprague | 2017 | 1 | Yes | Yes | Yes | Yes |


## V23.2 Somewhere in the Skies 2017 audit

- Source releases reconciled: 40
- Final unique records: 40
- Numbered episodes: 36
- Non-numbered releases: 4
- Duplicates suppressed: 0
- Excluded non-episode items: 0
- Episode #37 excluded because its publication date is January 1, 2018.
- Official/hosted episode references and authoritative directory metadata were verified before import.


## V23.3 Somewhere in the Skies gateway restoration
- Primary public route: `categories/somewhere-in-the-skies.html`
- Canonical secondary route: `entities/entity.html?id=somewhere-in-the-skies-podcast`
- 2017 archive records: 40 unique releases
- Verified combined filters: Historical UFO Cases (10), Witness Accounts (11), High Strangeness (7), Media and Popular Culture (12)
- Episode entities, approved classifications, canonical records, and relationships unchanged.

## V23.4 Somewhere in the Skies media audit
All 40 2017 records were audited. Retired Acast links were removed. Six independently matched exact episode destinations are retained; the remaining 34 records use a clearly labeled official Apple Podcasts archive fallback. Episode data and graph relationships were not changed.

## V23.5A universal official-media audit layer
Podcast audits may now validate either explicit `officialMedia` collections or derived legacy collections. Live checks must be explicitly invoked and cannot report success without a network response.

## V23.5C.1 readiness

All 257 migrated podcast episodes and four canonical podcast-series entities are represented in the offline audit inventory. Need to Know Episodes 13 and 14 retain dedicated regression checks, and all 40 Somewhere in the Skies 2017 records remain included. No podcast content or media records were changed.
