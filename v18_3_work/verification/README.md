# Search engine verification

Version 5 is prepared for Google Search Console and Bing Webmaster Tools.

## Google Search Console
Recommended: use the **Domain property** and verify with the TXT record Google provides in GoDaddy DNS.
Alternative: download Google's HTML verification file and place it in the repository root.

## Bing Webmaster Tools
Fastest option: import the verified site from Google Search Console.
Alternative: paste Bing's `msvalidate.01` value into `assets/js/site-config.js`.

## Microsoft Clarity
Create a project for `https://greyalien.com`, then paste the project ID into
`microsoftClarityProjectId` in `assets/js/site-config.js`.
