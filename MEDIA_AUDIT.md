## V23.5B podcast media reconciliation

The controlled migration inventoried 958 legacy URL occurrences and created 491 canonical official-media records across 261 entities. Broad live-link research was intentionally deferred to V23.5C.

# GreyAlien Media Audit — Version 14.2

| Interview | Platform | Host | Direct link | Alternatives |
|---|---|---|---:|---:|
| David Grusch NewsNation Interview | NewsNation | Ross Coulthart | Yes | 2 |
| David Fravor on the Lex Fridman Podcast | Lex Fridman Podcast | Lex Fridman | Yes | 3 |
| Alexandro Wiggins on WEAPONIZED | WEAPONIZED | Jeremy Corbell and George Knapp | Yes | 3 |
| Bob Lazar's 1989 KLAS Interviews | KLAS-TV / 8 News Now | George Knapp | Yes | 3 |
| Jonathan Weygandt Peru Encounter Interview | Archived video | Disclosure-era interviewer | Yes | 1 |
| Michael Herrera Public Interview | YouTube | Not listed | Yes | 1 |
| Eric Hecker South Pole Interview | PBD Podcast | Patrick Bet-David | Yes | 1 |
| David Adair: My Story — Child Prodigy to Rocket Scientist | Gaia | Not listed | Yes | 2 |

## V23.5A official-media validation
Canonical URL comparison now covers tracking parameters, trailing slashes, HTTP/HTTPS normalization, YouTube mobile/short URLs, and preserves episode-identifying parameters.

## V23.5C.1 offline audit-engine preparation

The universal podcast media audit is prepared under `data/media-audit/v23.5c.1/`. It covers WEAPONIZED, Need to Know, MERGED, and Somewhere in the Skies. The generated dataset contains 1,449 media occurrences and 491 unique validation jobs. Live HTTP status, redirects, soft-404 detection, and episode-identity confirmation remain explicitly `not_run` pending V23.5C.2.
