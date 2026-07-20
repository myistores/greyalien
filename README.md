## Current release: V17.5 — Timeline Normalization Engine

See `PHASE4\_REFINEMENT2\_TIMELINE\_NORMALIZATION.md` for normalization and connection-count rules.

# GreyAlien V17.2 — Import System

Deploy the complete package to the repository root. Phase 3 documentation is in `PHASE3\_IMPORT\_SYSTEM.md` and `data/imports/README.md`.

# GreyAlien Version 5 — Analytics, Search and Sharing Foundation

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

