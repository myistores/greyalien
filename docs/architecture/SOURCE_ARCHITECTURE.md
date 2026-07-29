# Source Architecture — Audit Additions

`tools/podcast_media_audit/audit_pipeline` contains transport, metadata, platform detection, identity comparison, proposal, reporting, validation, and transaction modules. Schemas are under `tools/podcast_media_audit/schema`. The GitHub Actions workflow is read-only and writes only its artifact workspace.
