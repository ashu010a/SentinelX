# Monitoring Architecture
## Diff Engine Strategy
To avoid costly $O(N^2)$ cross-table snapshot comparisons, the Diff Engine utilizes a `last_seen_scan_id` tracing mechanism. 
1. The scanner updates `last_seen` on all observed entities.
2. The Engine executes a fast query: `SELECT WHERE status='OPEN' AND last_seen != current_scan`.
3. Discrepancies are natively emitted to the `TimelineEvents` table.
