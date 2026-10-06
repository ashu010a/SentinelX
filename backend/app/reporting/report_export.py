import json
import csv
import io
import html
from sqlalchemy.orm import Session
import models
import os

def generate_report(db: Session, project_id: str, report_type: str, req_format: str, filters: dict):
    findings = db.query(models.Finding).filter_by(project_id=project_id).all()
    
    # Track audit
    from .remediation_service import log_audit
    log_audit(db, project_id, "REPORT_GENERATED", "REPORT", report_type, {"format": req_format, "filters": filters})
    
    report_record = models.Report(
        project_id=project_id, report_type=report_type, format=req_format, filter_config=filters
    )
    db.add(report_record)
    db.commit()
    db.refresh(report_record)
    
    os.makedirs("exports", exist_ok=True)
    file_path = f"exports/{report_record.id}.{req_format}"
    
    if req_format == "json":
        data = [{"id": f.id, "title": f.title, "severity": f.severity, "status": f.remediation_status, "owner": f.owner} for f in findings]
        with open(file_path, "w") as f: json.dump(data, f)
            
    elif req_format == "csv":
        with open(file_path, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Title", "Severity", "Status", "Owner"])
            for f in findings: writer.writerow([f.id, f.title, f.severity, f.remediation_status, f.owner])
                
    elif req_format == "html":
        # Safe HTML Escaping
        html_content = f"<html><head><title>{html.escape(report_type)}</title></head><body><h1>SentinelX Security Report</h1><table border='1'>"
        html_content += "<tr><th>Title</th><th>Severity</th><th>Status</th></tr>"
        for f in findings:
            html_content += f"<tr><td>{html.escape(f.title)}</td><td>{html.escape(f.severity)}</td><td>{html.escape(f.remediation_status)}</td></tr>"
        html_content += "</table></body></html>"
        with open(file_path, "w") as f: f.write(html_content)
    
    elif req_format == "pdf":
        # Mock PDF via text for testing environment
        with open(file_path, "w") as f: f.write("MOCK PDF BINARY HEADER\n" + report_type)

    report_record.file_path = file_path
    db.commit()
    return report_record
