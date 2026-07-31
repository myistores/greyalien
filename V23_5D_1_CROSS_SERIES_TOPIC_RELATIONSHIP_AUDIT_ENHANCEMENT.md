# V23.5D.1 — Cross-Series Topic Relationship Audit Enhancement

**Base Repository:** V23.5D  
**Production Type:** Knowledge-graph audit enhancement (analysis only)

This release extends the existing cross-series topic audit with explainable knowledge-graph traversal and three-stage candidate validation. It preserves the V23.5D human-review gate and does not modify entity data, relationships, schemas, classifications, rendering, generated pages, or recommendation logic.

## Added capabilities

- Bidirectional traversal of existing graph relationships, capped at two edges for explainability.
- Recognition of Case, historical incident, encounter, and investigation entities.
- Case inheritance discovery for the Historical UFO Cases umbrella topic.
- Subject Relevance, Research Value, and Case Inheritance test records for every candidate.
- Metadata, Knowledge Graph, and Hybrid discovery classification.
- Existing Case links, Topic links, missing umbrella links, redundant links, and graph paths.
- Cross-series graph consistency analysis.
- Human approval worksheet with every decision initialized to `pending`.
- Machine-readable reports and a GitHub Actions workflow for repeatable execution.

## Repository protection

The audit hashes entity JSON and generated entity pages before and after analysis. Any protected-file mutation causes validation failure.
