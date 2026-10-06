# Scanner Ingestion Architecture
## Interface
The system relies on a generic `ScannerResultImporter` interface ensuring complete decoupling from offensive testing execution.
The pipeline operates strictly on passive JSON/JSONL output files parsing them directly into the Postgres schema.

## Deduplication Logic
- Assets are identified by `project_id` and `value` (e.g. FQDN/IP).
- Findings are deduplicated against the `asset_id` and vulnerability `title`.
- Duplicates safely update state parameters (`assets_updated`, `findings_updated`) rather than polluting the database.
