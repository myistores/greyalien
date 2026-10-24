# V23.6D.20.1 — Science presentation refinement

Baseline: V23.6D.20. Full deployment package.

## Changes
- Scoped typography for the Parallax and Infrared topic pages: smaller titles, tighter line height, compact explanatory sections.
- Science collection sidebars align at the top and end after their content.
- Live Infrared and Parallax topics removed from planned lists; remaining camera-artifact work and additional peer-reviewed research labeled accordingly.
- Scoped print rules: dark text, white backgrounds, headings kept with following text, paper cards and short explanation sections kept together when possible.
- Version-specific presentation stylesheet added to seven collection pages and the two topic pages.

## Validation
- Chromium screenshots inspected for desktop (1440px) and mobile (390px).
- Four page types checked at both widths: Infrared, Parallax, Research Papers & Reports, Technologies & Sensors. No horizontal overflow.
- Computed research-sidebar height: 433px, versus main content 2476px at desktop width.
- Topic title: 49.6px desktop, 32px mobile; line height 1.12.
- Chromium print rendering reviewed for Infrared and Papers; Parallax print rendering generated. Paper cards remain intact; text prints dark.
- New stylesheet parsed; stylesheet targets resolve.
- All research data, graph indexes, relationships, publication records and topic explanatory text match V23.6D.20.
- Baseline file population preserved. ZIP CRC integrity checked.

## Deployment
Extract the complete package into the website root with the usual deployment process. The version-specific stylesheet avoids reusing the previous presentation stylesheet URL. Not deployed by delivery.

Rollback: restore V23.6D.20.

## Changed files
- assets/css/science-presentation-v23-6d-20-1.css
- science/research-papers-reports/index.html
- science/disciplines/index.html
- science/technologies-sensors/index.html
- science/natural-explanations/index.html
- science/research-programs/index.html
- science/future-technologies/index.html
- science/scientific-methods/index.html
- entities/generated/infrared-imaging-interpretation.html
- entities/generated/parallax-apparent-motion.html
