from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from database import Base, engine, get_db
import models
from worker import execute_scan_sync

Base.metadata.create_all(bind=engine)
app = FastAPI(title="SentinelX MVP API")

@app.get("/api/health")
def health(): return {"status": "ok"}

@app.post("/api/projects")
def create_project(data: dict, db: Session = Depends(get_db)):
    p = models.Project(name=data.get('name'))
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

@app.post("/api/projects/{project_id}/targets")
def add_target(project_id: str, data: dict, db: Session = Depends(get_db)):
    t = models.Target(project_id=project_id, target_value=data.get('target_value'))
    db.add(t)
    db.commit()
    db.refresh(t)
    return t

@app.post("/api/scans")
def start_scan(data: dict, db: Session = Depends(get_db)):
    job = models.ScanJob(project_id=data.get('project_id'), target_id=data.get('target_id'))
    db.add(job)
    db.commit()
    db.refresh(job)
    # Trigger synchronous worker execution for native verification (no redis locally)
    execute_scan_sync(job.id)
    # Clear session cache to see updates from the worker's separate DB session
    db.expire_all()
    return db.query(models.ScanJob).filter_by(id=job.id).first()

@app.get("/api/projects/{project_id}/assets")
def get_assets(project_id: str, db: Session = Depends(get_db)):
    return db.query(models.Asset).filter_by(project_id=project_id).all()

@app.get("/api/projects/{project_id}/findings")
def get_findings(project_id: str, db: Session = Depends(get_db)):
    return db.query(models.Finding).filter_by(project_id=project_id).all()

@app.get("/api/dashboard/{project_id}")
def get_dashboard(project_id: str, db: Session = Depends(get_db)):
    assets = db.query(models.Asset).filter_by(project_id=project_id).count()
    findings = db.query(models.Finding).filter_by(project_id=project_id).count()
    # Pull average risk score from DB
    from sqlalchemy.sql import func
    risk = db.query(func.avg(models.RiskScore.score)).join(models.Asset).filter(models.Asset.project_id==project_id).scalar()
    return {"total_assets": assets, "critical_findings": findings, "risk_score": risk or 0.0}

@app.get("/api/projects/{project_id}/timeline")
def get_timeline(project_id: str, db: Session = Depends(get_db)):
    assets = db.query(models.Asset).filter_by(project_id=project_id).all()
    asset_ids = [a.id for a in assets]
    changes = db.query(models.AssetChange).filter(models.AssetChange.asset_id.in_(asset_ids)).all()
    return changes

@app.get("/api/projects/{project_id}/reports")
def generate_report(project_id: str, format: str = "json", db: Session = Depends(get_db)):
    if format == "html":
        return {"data": "<h1>SentinelX Security Report</h1><p>Risk Score and Assets listed below...</p>"}
    return {"data": {"summary": "JSON Report Content"}}

import os
import shutil
from importers import get_importer

@app.post("/api/imports")
def create_import(project_id: str = Form(...), scanner_name: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    importer = get_importer(scanner_name)
    if not importer:
        raise HTTPException(status_code=400, detail="Scanner adapter not found")
        
    job = models.ImportJob(project_id=project_id, scanner_name=scanner_name, status="queued")
    db.add(job)
    db.commit()
    db.refresh(job)
    
    os.makedirs("uploads", exist_ok=True)
    filepath = f"uploads/{job.id}_{os.path.basename(file.filename)}"
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Trigger import synchronously for local testing (simulating celery delay)
    # Re-open session internally for processing isolation
    from database import SessionLocal
    proc_db = SessionLocal()
    job_proc = proc_db.query(models.ImportJob).filter_by(id=job.id).first()
    importer.process(filepath, project_id, proc_db, job_proc)
    proc_db.close()
    
    db.expire_all()
    return db.query(models.ImportJob).filter_by(id=job.id).first()

@app.get("/api/imports")
def get_imports(project_id: str, db: Session = Depends(get_db)):
    return db.query(models.ImportJob).filter_by(project_id=project_id).all()

from app.risk import risk_service

@app.get("/api/projects/{project_id}/risk")
def get_project_risk(project_id: str, db: Session = Depends(get_db)):
    res = risk_service.calculate_project_risk(db, project_id)
    if not res: return {"message": "No risk data"}
    
    history = db.query(models.RiskHistory).filter_by(entity_type="project", entity_id=project_id).order_by(models.RiskHistory.calculated_at.desc()).first()
    return history

@app.get("/api/projects/{project_id}/risk/top-findings")
def get_top_findings(project_id: str, db: Session = Depends(get_db)):
    # Prioritized finding response
    histories = db.query(models.RiskHistory).filter_by(entity_type="finding", project_id=project_id).order_by(models.RiskHistory.score.desc()).limit(10).all()
    return histories

@app.get("/api/findings/{finding_id}/risk")
def get_finding_risk(finding_id: str, db: Session = Depends(get_db)):
    return risk_service.process_finding_risk(db, finding_id)

from app.risk import risk_service

@app.get("/api/projects/{project_id}/risk")
def get_project_risk(project_id: str, db: Session = Depends(get_db)):
    res = risk_service.calculate_project_risk(db, project_id)
    if not res: return {"message": "No risk data"}
    
    history = db.query(models.RiskHistory).filter_by(entity_type="project", entity_id=project_id).order_by(models.RiskHistory.calculated_at.desc()).first()
    return history

@app.get("/api/projects/{project_id}/risk/top-findings")
def get_top_findings(project_id: str, db: Session = Depends(get_db)):
    # Prioritized finding response
    histories = db.query(models.RiskHistory).filter_by(entity_type="finding", project_id=project_id).order_by(models.RiskHistory.score.desc()).limit(10).all()
    return histories

@app.get("/api/findings/{finding_id}/risk")
def get_finding_risk(finding_id: str, db: Session = Depends(get_db)):
    return risk_service.process_finding_risk(db, finding_id)

from app.correlation import graph_service, relationship_service

@app.get("/api/projects/{project_id}/graph")
def get_graph(project_id: str, db: Session = Depends(get_db)):
    return graph_service.get_project_graph(project_id, db)

@app.get("/api/projects/{project_id}/risk-paths")
def get_risk_paths(project_id: str, db: Session = Depends(get_db)):
    return graph_service.calculate_risk_paths(project_id, db)

@app.post("/api/projects/{project_id}/correlate")
def trigger_correlation(project_id: str, db: Session = Depends(get_db)):
    relationship_service.run_correlation_engine(project_id, db)
    return {"status": "success"}

from app.monitoring import diff_engine

@app.post("/api/projects/{project_id}/snapshots/generate")
def generate_diff_snapshot(project_id: str, scan_id: str, db: Session = Depends(get_db)):
    return diff_engine.generate_snapshot_and_diff(db, project_id, scan_id)

@app.get("/api/projects/{project_id}/snapshots")
def get_snapshots(project_id: str, db: Session = Depends(get_db)):
    return db.query(models.ProjectSnapshot).filter_by(project_id=project_id).all()

@app.get("/api/projects/{project_id}/timeline-events")
def get_timeline_events(project_id: str, db: Session = Depends(get_db)):
    return db.query(models.TimelineEvent).filter_by(project_id=project_id).order_by(models.TimelineEvent.created_at.desc()).all()

@app.get("/api/projects/{project_id}/alerts")
def get_alerts(project_id: str, db: Session = Depends(get_db)):
    return db.query(models.Alert).filter_by(project_id=project_id).order_by(models.Alert.created_at.desc()).all()

from app.ai import ai_service
from pydantic import BaseModel

class ChatRequest(BaseModel):
    conversation_id: str
    question: str

@app.post("/api/projects/{project_id}/assistant/chat")
def chat_with_assistant(project_id: str, req: ChatRequest, db: Session = Depends(get_db)):
    # Create conversation if not exists
    conv = db.query(models.AIConversation).filter_by(id=req.conversation_id, project_id=project_id).first()
    if not conv:
        conv = models.AIConversation(id=req.conversation_id, project_id=project_id)
        db.add(conv)
        db.commit()
        
    try:
        return ai_service.ask_assistant(db, project_id, req.conversation_id, req.question)
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))

from app.reporting import remediation_service, report_export
from pydantic import BaseModel

class RemediationUpdate(BaseModel):
    remediation_status: str = None
    owner: str = None
    remediation_notes: str = None

@app.patch("/api/findings/{finding_id}/remediation")
def update_remediation(finding_id: str, payload: RemediationUpdate, db: Session = Depends(get_db)):
    return remediation_service.update_finding_remediation(db, finding_id, payload.dict(exclude_unset=True))

@app.get("/api/projects/{project_id}/operations")
def get_operations_dashboard(project_id: str, db: Session = Depends(get_db)):
    findings = db.query(models.Finding).filter_by(project_id=project_id).all()
    open_f = [f for f in findings if f.remediation_status in ['OPEN', 'IN_PROGRESS']]
    # Calculate mock completion rates
    return {
        "overall_risk": 7.5,
        "open_findings": len(open_f),
        "overdue_findings": 0,
        "remediation_completion": {"critical": 100, "high": 50, "medium": 0, "low": 0}
    }

class ReportRequest(BaseModel):
    report_type: str
    format: str
    filters: dict = {}

@app.post("/api/projects/{project_id}/reports")
def create_report(project_id: str, payload: ReportRequest, db: Session = Depends(get_db)):
    return report_export.generate_report(db, project_id, payload.report_type, payload.format, payload.filters)

@app.get("/api/projects/{project_id}/compliance")
def get_compliance(project_id: str, db: Session = Depends(get_db)):
    # Static generic mapping view
    return {
        "frameworks": {
            "NIST": {"coverage": "75%", "potential_gaps": 4},
            "CIS": {"coverage": "82%", "potential_gaps": 2}
        }
    }
