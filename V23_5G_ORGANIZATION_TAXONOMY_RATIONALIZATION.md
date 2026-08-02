# V23.5G — Organization Taxonomy Rationalization

Base: V23.5F (deployed)

This bounded production release refines only the approved Organization records. It converts six incidental organizations to searchable supporting metadata, reclassifies twenty-four records into semantically accurate entity types, and consolidates two duplicate Organization records into canonical entities. Existing identifiers, logical relationships, URLs, and aliases are preserved.

## Production Results

- 6 supporting-metadata conversions
- 24 entity reclassifications
- 2 duplicate aliases consolidated
- 0 logical relationships added
- 0 logical relationships lost
- 0 unapproved entity-content changes
- 2 legacy redirect pages preserved

## Reused Existing Entity Type

Publication / Media Outlet records reuse the existing `publication` type.

## New Bounded Entity Types

The existing universal entity schema was extended only where no accurate type existed:

- `program`
- `research_project`
- `advisory_panel`
- `facility`
- `military_vessel`
- `military_unit`

See `reports/v23-5g/relationship-migration-summary.json` and `reports/v23-5g/V23_5G_VALIDATION_REPORT.md`.
