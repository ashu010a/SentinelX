from sqlalchemy.orm import Session
import models
from .alert_service import trigger_alert
from datetime import datetime

def generate_snapshot_and_diff(db: Session, project_id: str, current_scan_id: str):
    # 1. Create Snapshot
    assets = db.query(models.Asset).filter_by(project_id=project_id).all()
    findings = db.query(models.Finding).filter_by(project_id=project_id, status='OPEN').all()
    
    # Mock project risk calculation via simple average for demonstration
    risk_score = 5.0
    
    snap = models.ProjectSnapshot(
        project_id=project_id,
        scan_id=current_scan_id,
        asset_count=len(assets),
        finding_count=len(findings),
        project_risk_score=risk_score
    )
    db.add(snap)
    
    # 2. Run Diff Engine (Detect missing items => RESOLVED/REMOVED)
    # If a finding is OPEN but wasn't seen in the current scan, mark it RESOLVED
    stale_findings = db.query(models.Finding).filter(
        models.Finding.project_id == project_id,
        models.Finding.status == 'OPEN',
        models.Finding.last_seen_scan_id != current_scan_id
    ).all()
    
    for f in stale_findings:
        f.status = 'RESOLVED'
        f.resolved_at = datetime.utcnow()
        evt = models.TimelineEvent(
            project_id=project_id, scan_id=current_scan_id,
            event_type="RESOLVED_FINDING", severity="info",
            asset_id=f.asset_id, finding_id=f.id,
            explanation=f"Finding '{f.title}' was not observed in the latest scan and has been marked as resolved."
        )
        db.add(evt)
        
    db.commit()
    return snap
