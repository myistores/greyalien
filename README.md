## Current release: V23.2 — Somewhere in the Skies 2017 Podcast Integration

See `PHASE4\_REFINEMENT2\_TIMELINE\_NORMALIZATION.md` for normalization and connection-count rules.

# GreyAlien

## Current release: V23.3
The Somewhere in the Skies gateway is restored as the primary public series destination. Its archive exposes all 40 unique 2017 releases through compact year, topic, search, sort, and combined-filter views. The canonical podcast-series entity remains available as the secondary knowledge-graph record.
 V17.2 — Import System

Deploy the complete package to the repository root. Phase 3 documentation is in `PHASE3\_IMPORT\_SYSTEM.md` and `data/imports/README.md`.

# GreyAlien

## Current release: V23.3
The Somewhere in the Skies gateway is restored as the primary public series destination. Its archive exposes all 40 unique 2017 releases through compact year, topic, search, sort, and combined-filter views. The canonical podcast-series entity remains available as the secondary knowledge-graph record.
 Version 5 — Analytics, Search and Sharing Foundation

## Included

* Google Analytics 4 on every page
* GA4 Measurement ID: `G-CPWQX72QKP`
* Custom `knowledge\_navigation` and outbound-link events
* Central site configuration
* Microsoft Clarity-ready configuration
* Google Search Console-ready verification
* Bing Webmaster Tools-ready verification
* `sitemap.xml`
* `robots.txt`
* canonical URLs
* Open Graph metadata
* Twitter/X card metadata
* JSON-LD structured data
* dynamic Event schema for hearing records
* custom `404.html`
* favicon and theme metadata

## Deploy

Upload the complete extracted package to the root of the existing GitHub repository.
Keep all folders intact and replace existing files when prompted.

Suggested commit:
`Add analytics search and social foundation`

## After deployment

1. Visit the site in a private browser window.
2. Open Google Analytics > Reports > Realtime.
3. Browse several GreyAlien pages.
4. Confirm that one active user and page views appear.

## Still to configure

* Search Console verification token or DNS TXT record
* Bing verification or Search Console import
* Microsoft Clarity project ID

Those values can be added centrally in:
`assets/js/site-config.js`

## V17.3 automation

Run the complete deployable build and validation process with:

```bash
python tools/automate\_site.py
```

See `PHASE4\_AUTOMATION.md` for the generated assets and testing workflow.

## V17.4 rendering refinement

V17.4 groups relationship cards by target entity category and retains the specific relationship as the card badge. This prevents duplicate user-facing sections such as two separate Related Media blocks. Rendering categories are centralized in `data/schema/rendering-groups.json` and checked by `tools/validate\_rendering\_rules.py`. See `PHASE4\_REFINEMENT1\_RENDERING\_RULES.md`.

## V18.4 Research Accelerator

Create reviewable podcast ingestion drafts with:

```bash
python tools/research\_accelerator.py data/research-accelerator/templates/batch-manifest.json
```

The accelerator never publishes directly. See `V18\_4\_RESEARCH\_ACCELERATOR.md`. 


### V21.5
Need to Know Episodes 22–75 were added as a content-only production batch with direct official media links, canonical entity reuse, and cross-series validation.

### V22.0
MERGED Episode #1 was added as the third integrated podcast-series pilot using the validated content-only production workflow, direct official media, canonical entity reuse, and evidence-based cross-series discovery.


### V22.1
MERGED Episodes 2–19 completed the 19-episode series as a content-only production ingestion with canonical entity reuse, source-grounded claims, direct episode media, and validated cross-series discovery.

## V23 internal podcast classification

New podcast releases are classified during Research Accelerator draft generation. See [`V23_PODCAST_CLASSIFICATION_ENGINE.md`](V23_PODCAST_CLASSIFICATION_ENGINE.md). Classification is internal-only and requires human approval before import.

The engine uses [`data/podcast-classification-config.json`](data/podcast-classification-config.json) and validates output against [`data/podcast-classification-schema.json`](data/podcast-classification-schema.json). The V23.0 release metadata remains recorded in [`data/release-summary.json`](data/release-summary.json).

### V23.1
The release-visibility patch updates homepage Latest Additions and Development Updates and verifies the V23 documentation references. It makes no code or knowledge-graph data changes.


### V23.2
The complete 2017 Somewhere in the Skies release archive was ingested as 40 unique records: 36 numbered episodes and four non-numbered releases. All records were classified through V23, approved before import, and added to the existing year-and-topic gateway. See `V23_2_SOMEWHERE_IN_THE_SKIES_2017_INTEGRATION.md`.

### V23.4 media restoration
The Somewhere in the Skies 2017 archive no longer uses retired Acast hosted-page URLs. Media destinations are now explicitly identified as exact episode links or official series-archive fallbacks. See `V23_4_SOMEWHERE_IN_THE_SKIES_OFFICIAL_MEDIA_LINK_RESTORATION.md`.

## V23.5A official-media architecture
See `V23_5A_UNIVERSAL_PODCAST_OFFICIAL_MEDIA_ARCHITECTURE.md`. Current podcast records remain on the legacy-compatible path until V23.5B migration.
