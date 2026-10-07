from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import schema as models

def calculate_sla_due_date(db: Session, project_id: str, severity: str, created_at: datetime):
    settings = db.query(models.ProjectSettings).filter_by(project_id=project_id).first()
    if not settings:
        settings = models.ProjectSettings(project_id=project_id)
        db.add(settings)
        db.flush()
        
    days_map = {
        "critical": settings.sla_critical_days,
        "high": settings.sla_high_days,
        "medium": settings.sla_medium_days,
        "low": settings.sla_low_days
    }
    days = days_map.get(severity.lower(), 90)
    return created_at + timedelta(days=days)

def log_audit(db: Session, project_id: str, action: str, obj_type: str, obj_id: str, meta: dict):
    log = models.AuditLog(
        project_id=project_id, user_id="system", action=action,
        object_type=obj_type, object_id=obj_id, metadata_json=meta
    )
    db.add(log)

def update_finding_remediation(db: Session, finding_id: str, updates: dict):
    finding = db.query(models.Finding).filter_by(id=finding_id).first()
    if not finding: return None
    
    old_state = {"status": finding.remediation_status, "owner": finding.owner}
    
    if "remediation_status" in updates:
        finding.remediation_status = updates["remediation_status"]
    if "owner" in updates:
        finding.owner = updates["owner"]
    if "remediation_notes" in updates:
        finding.remediation_notes = updates["remediation_notes"]
        
    log_audit(db, finding.project_id, "REMEDIATION_UPDATE", "FINDING", finding.id, {"old": old_state, "new": updates})
    db.commit()
    db.refresh(finding)
    return finding
