from sqlalchemy.orm import Session
from app.models import schema as models

def trigger_alert(db: Session, project_id: str, message: str, severity: str):
    # Abstracted Webhook/In-app dispatcher
    alert = models.Alert(project_id=project_id, message=message, severity=severity)
    db.add(alert)
    db.commit()
    print(f"[ALERT] {severity.upper()}: {message}")
