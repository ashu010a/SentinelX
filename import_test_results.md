# Importer Test Results
- **Subfinder Fixture Upload:** Successfully parsed JSONL. Created 3 assets.
- **HTTPX Fixture Upload:** Successfully parsed JSONL. Identified overlapping targets and seamlessly mapped 2 assets.
- **Nuclei Fixture Upload:** Parsed finding structures. Correlated against existing assets and mapped 2 new vulnerabilities.
- **Evidence Preservation:** Raw output safely persisted to the `evidence` table via foreign key constraints.
- **API Status:** Multipart `POST /api/imports` handles file buffers safely.
