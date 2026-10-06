# Snapshot Model
- Enforces an immutable historical record via the `ProjectSnapshot` table.
- Stores aggregated risk thresholds (`asset_count`, `risk_score`) aligned exactly with a deterministic `scan_id`.
