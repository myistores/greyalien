## V23.5C.2A.1 — Podcast Official Media Link Rendering Restoration

Restores public podcast media actions by reconnecting the V23.5A compatibility helper to entity, series-directory, and gateway renderers. Adds mixed-state legacy compatibility and permanent rendering regression detection without changing podcast or knowledge-graph data. See `V23_5C_2A_1_PODCAST_OFFICIAL_MEDIA_LINK_RENDERING_RESTORATION.md`.

## Current release — V23.5B

All existing WEAPONIZED, Need to Know, MERGED, and Somewhere in the Skies podcast records now use the V23.5A universal Official Media collection while retaining legacy media fields for compatibility and rollback. See `V23_5B_EXISTING_PODCAST_OFFICIAL_MEDIA_MIGRATION.md`.

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
See `V23_5A_UNIVERSAL_PODCAST_OFFICIAL_MEDIA_ARCHITECTURE.md`. V23.5B has now migrated the four production podcast collections while retaining legacy fields for compatibility and rollback.

## V23.5C.1 podcast media audit preparation

The repository includes an offline-first universal podcast media-audit engine at `tools/audit_podcast_media.py`. Generated artifacts are stored under `data/media-audit/v23.5c.1/`. The package inventories and normalizes current media data, creates deterministic live-validation jobs, prepares episode-identity evidence, and accepts externally produced results transactionally. V23.5C.1 performs no production network checks and makes no podcast media-data changes.


## V23.5C.2A — Enhanced Live Podcast Audit Runner and Repair Pipeline

V23.5C.2A upgrades the prepared V23.5C.1 inventory into a production-capable GitHub Actions validation and repair-preparation pipeline. It captures destination evidence, distinguishes HTTP failures from transport failures, validates platform/content type/episode identity, generates approval-gated repairs, creates transactional previews and rollback snapshots, and regenerates reports without changing public media records during evidence generation. See `docs/releases/V23_5C_2A_ENHANCED_LIVE_PODCAST_AUDIT_RUNNER_AND_REPAIR_PIPELINE.md`.

## V23.5C.2B GitHub Actions live-validation runner

The repository now includes `.github/workflows/v23-5c-2b-live-podcast-media-validation.yml`. Run it manually from GitHub Actions with `job_limit` blank to validate all 491 prepared media jobs. The workflow uploads complete validation evidence and approval-gated repair proposals without silently changing production media. See `docs/releases/V23_5C_2B_LIVE_PODCAST_MEDIA_VALIDATION_AND_REPAIR.md`.
