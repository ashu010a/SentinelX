# API Documentation

Base URL: `/api/v1`

## Projects

### `GET /projects`
List all projects.
**Response**:
```json
[
  {
    "id": "uuid",
    "name": "Acme Corp",
    "target_domain": "acme.com",
    "created_at": "2023-10-27T10:00:00Z"
  }
]
```

### `POST /projects`
Create a new project.
**Request**:
```json
{
  "name": "Acme Corp",
  "target_domain": "acme.com"
}
```
**Response**: `201 Created` with project details.

### `GET /projects/{id}`
Get project details.

## Scans

### `POST /projects/{id}/scans`
Start a new scan for the given project.
**Response**: `202 Accepted`
```json
{
  "scan_id": "uuid",
  "status": "pending",
  "message": "Scan initiated"
}
```

### `GET /projects/{id}/scans`
List all scans for a project.

### `GET /scans/{id}`
Get the status and details of a specific scan.
**Response**:
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "status": "running",
  "start_time": "2023-10-27T10:05:00Z",
  "end_time": null
}
```

## Assets

### `GET /assets?project_id={id}`
List discovered assets, optionally filtered by project.
**Response**:
```json
[
  {
    "id": "uuid",
    "hostname": "api.acme.com",
    "ip_address": "1.2.3.4",
    "is_active": true
  }
]
```

## Vulnerabilities

### `GET /vulnerabilities?project_id={id}&severity=high`
List discovered vulnerabilities, optionally filtered by project and severity.
**Response**:
```json
[
  {
    "id": "uuid",
    "asset_id": "uuid",
    "title": "Exposed .git directory",
    "severity": "high",
    "discovered_at": "2023-10-27T10:15:00Z"
  }
]
```

## Error Handling

Standard HTTP status codes are used. Errors return a JSON payload:
```json
{
  "detail": "Error message explaining what went wrong."
}
```

## Authentication

*Authentication is planned for version 0.2.* Currently, endpoints are unauthenticated for local development. Future versions will use OAuth2 with Bearer tokens (JWT).
