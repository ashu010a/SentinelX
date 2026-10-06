# Database Schema

## ER Diagram

```text
[Project] 1 ----- * [Scan]
[Project] 1 ----- * [Asset]
[Scan] 1 ----- * [Asset] (Discovered in)
[Asset] 1 ----- * [Port]
[Asset] 1 ----- * [Vulnerability]
[Scan] 1 ----- * [Vulnerability] (Found during)
```

## Tables

### `projects`
Stores target domains and configurations.
- `id` (UUID, Primary Key)
- `name` (String, Not Null)
- `target_domain` (String, Not Null, Unique)
- `created_at` (Timestamp)
- `updated_at` (Timestamp)

### `scans`
Records individual scan executions.
- `id` (UUID, Primary Key)
- `project_id` (UUID, Foreign Key -> projects.id)
- `status` (Enum: pending, running, completed, failed)
- `start_time` (Timestamp)
- `end_time` (Timestamp)
- `celery_task_id` (String)

### `assets`
Stores discovered subdomains, IPs, and web servers.
- `id` (UUID, Primary Key)
- `project_id` (UUID, Foreign Key -> projects.id)
- `hostname` (String, Not Null)
- `ip_address` (String)
- `asset_type` (Enum: domain, subdomain, ip)
- `is_active` (Boolean)
- `first_seen` (Timestamp)
- `last_seen` (Timestamp)

### `ports`
Stores open ports associated with assets.
- `id` (UUID, Primary Key)
- `asset_id` (UUID, Foreign Key -> assets.id)
- `port_number` (Integer, Not Null)
- `service_name` (String)
- `state` (String)

### `vulnerabilities`
Stores findings from vulnerability scanners.
- `id` (UUID, Primary Key)
- `asset_id` (UUID, Foreign Key -> assets.id)
- `scan_id` (UUID, Foreign Key -> scans.id)
- `title` (String, Not Null)
- `severity` (Enum: info, low, medium, high, critical)
- `description` (Text)
- `remediation` (Text)
- `template_id` (String) - Nuclei template ID
- `discovered_at` (Timestamp)

## Indexes

To ensure query performance, the following indexes should be created:
- `ix_assets_project_id` on `assets(project_id)`
- `ix_assets_hostname` on `assets(hostname)`
- `ix_vulnerabilities_asset_id` on `vulnerabilities(asset_id)`
- `ix_vulnerabilities_severity` on `vulnerabilities(severity)`
- `ix_scans_project_id` on `scans(project_id)`

## Migration Strategy

Alembic will be used for database migrations. All schema changes must be accompanied by an Alembic migration script generated via `alembic revision --autogenerate`.
