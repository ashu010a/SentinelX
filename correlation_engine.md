# Correlation Engine
## Architecture
- Evaluates rule definitions against normalized tables.
- **Deduplication:** Finding fingerprints mathematically prevent duplicate entries across overlapping scanners (Nuclei + HTTPX).
- **Isolation:** Multi-tenant separation maintained at the DB query level.
