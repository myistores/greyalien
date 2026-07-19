GreyAlien V17.4 — Automation Engine Refinement

DEPLOYMENT
1. Extract this package.
2. Replace the deployed GreyAlien repository contents with the package contents.
3. Commit and push through GitHub Desktop.
4. Confirm the homepage shows "GreyAlien Version 17.4 — Automation Engine Refinement."

PRIMARY LIVE TEST
Open:
https://greyalien.com/entities/entity.html?id=weaponized-podcast

Expected result:
- One Related Media section.
- Seven connected media records in that section.
- Alexandro Wiggins on WEAPONIZED retains the "Published" badge.
- The six researched WEAPONIZED episodes retain their "Includes Episode" badges.
- Referenced In remains a separate section.
- Continue Research remains a separate section.

LOCAL VALIDATION
python tools/automate_site.py

Expected final line:
Automation status: PASSED. Site assets are ready for deployment.
