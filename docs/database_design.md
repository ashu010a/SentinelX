# Database Design

## Core Entities
- **User:** Authentication and authorization details.
- **Project:** Organizational container for targets and scans.
- **Target:** The root domain or IP range authorized for scanning.
- **Asset / Domain / IP:** Discovered infrastructure components.
- **Service:** Discovered open ports/protocols on IPs.
- **Endpoint:** Discovered web URLs/APIs.
- **ScanJob:** Metadata about a Celery task (status, tool, progress).
- **Finding:** A normalized security vulnerability or misconfiguration.
- **Evidence:** Raw scanner output or proof linking to a Finding.

## Relationships
- Project (1) -> (N) Target
- Target (1) -> (N) Domain
- Domain (N) -> (M) IP
- IP (1) -> (N) Service
- Asset (1) -> (N) Finding
- ScanJob (1) -> (N) Finding
