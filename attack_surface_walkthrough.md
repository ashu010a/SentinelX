# Attack Surface Walkthrough
The Graph API now securely translates disconnected data points into a cohesive attack path.
- The `api.example.com` asset was safely nested under `example.com`.
- The cross-scanner deduplicated `Swagger UI` finding was securely linked via `vulnerable_to`.
- `GET /api/projects/{id}/graph` renders this structure seamlessly for the frontend UI.
