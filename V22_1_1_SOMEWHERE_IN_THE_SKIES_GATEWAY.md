# V22.1.1 — Somewhere in the Skies Archive Gateway

**Base repository:** V22.1

## Scope

Adds a scalable series gateway for Somewhere in the Skies without ingesting episodes or changing the knowledge-graph schema. The gateway combines year and topic browsing, keyword search, compact episode rows, sorting, and 25-record pagination.

## Added

- `categories/somewhere-in-the-skies.html`
- `assets/js/somewhere-in-the-skies-gateway.js`
- `data/podcasts/somewhere-in-the-skies-archive.json`

## Updated

- Podcast directory links the canonical series card to the new gateway.
- Podcast index includes the gateway route and official website.
- Native responsive styles support desktop and mobile browsing.
- Homepage Latest Additions, changelog, and sitemap were updated.

## Ingestion behavior

The archive JSON currently contains no episode records because V22.1 has not ingested Somewhere in the Skies episodes. Future ingestion can append individual canonical episode records to `episodes[]`; the gateway will automatically calculate year/topic counts, filter combinations, tier counts, search results, and pagination.

## Production boundary

No existing entities, relationships, templates, routing behavior, or episode content were altered.


## V23.2 population status

The gateway is now populated with the complete 2017 archive: 40 unique records. The 2017 filter, topic filters, combined year-and-topic filters, title/summary search, guest metadata, and direct record links are active.


## V23.3 restoration status
The V22.1.1 gateway is again the primary public destination. Podcast-directory and related-series links route here, while the canonical podcast-series entity remains a secondary knowledge-graph view with a return link to the gateway. All 40 V23.2 archive records are exposed as compact paginated rows and retain their reviewed V23 topic assignments.
