# Diff Engine Logic
Deterministic transition engine:
- `NEW`: first_seen_scan_id == current_scan
- `RESOLVED`: last_seen_scan_id != current_scan AND status == OPEN
- `REOPENED`: status == RESOLVED AND last_seen_scan_id == current_scan
