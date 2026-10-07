
import json
from abc import ABC, abstractmethod
from app.models import schema as models

class ScannerResultImporter(ABC):
    scanner_name = ""
    supported_formats = []
    
    def process(self, filepath, project_id, db, job):
        try:
            job.status = "processing"
            db.commit()
            self.parse_and_import(filepath, project_id, db, job)
            job.status = "completed"
            db.commit()
        except Exception as e:
            db.rollback()
            job.status = "failed"
            job.parse_errors += 1
            db.commit()
            print(f"Import critical failure: {e}")

    @abstractmethod
    def parse_and_import(self, filepath, project_id, db, job): pass

class SubfinderImporter(ScannerResultImporter):
    scanner_name = "subfinder"
    supported_formats = ["jsonl"]
    
    def parse_and_import(self, filepath, project_id, db, job):
        with open(filepath) as f:
            for line in f:
                if not line.strip(): continue
                try:
                    data = json.loads(line)
                    host = data.get("host")
                    if not host: continue
                    
                    asset = db.query(models.Asset).filter_by(project_id=project_id, value=host).first()
                    if asset:
                        job.assets_updated += 1
                    else:
                        asset = models.Asset(project_id=project_id, asset_type="domain", value=host)
                        db.add(asset)
                        db.flush()
                        db.add(models.AssetChange(asset_id=asset.id, change_type="NEW ASSET"))
                        job.assets_created += 1
                except:
                    job.parse_errors += 1

class HttpxImporter(ScannerResultImporter):
    scanner_name = "httpx"
    supported_formats = ["jsonl"]
    
    def parse_and_import(self, filepath, project_id, db, job):
        with open(filepath) as f:
            for line in f:
                if not line.strip(): continue
                try:
                    data = json.loads(line)
                    host = data.get("host", data.get("url", "").replace("https://", "").replace("http://", ""))
                    if not host: continue
                    
                    asset = db.query(models.Asset).filter_by(project_id=project_id, value=host).first()
                    if asset:
                        job.assets_updated += 1
                    else:
                        asset = models.Asset(project_id=project_id, asset_type="domain", value=host)
                        db.add(asset)
                        db.flush()
                        job.assets_created += 1
                except:
                    job.parse_errors += 1

class NucleiImporter(ScannerResultImporter):
    scanner_name = "nuclei"
    supported_formats = ["json", "jsonl"]
    
    def parse_and_import(self, filepath, project_id, db, job):
        with open(filepath) as f:
            for line in f:
                if not line.strip(): continue
                try:
                    data = json.loads(line)
                    host = data.get("host", "")
                    info = data.get("info", {})
                    title = info.get("name", "Unknown Finding")
                    severity = info.get("severity", "info")
                    
                    asset = db.query(models.Asset).filter_by(project_id=project_id, value=host).first()
                    if not asset:
                        asset = models.Asset(project_id=project_id, asset_type="domain", value=host)
                        db.add(asset)
                        db.flush()
                        job.assets_created += 1
                        
                    finding = db.query(models.Finding).filter_by(asset_id=asset.id, title=title).first()
                    if finding:
                        job.findings_updated += 1
                    else:
                        finding = models.Finding(project_id=project_id, asset_id=asset.id, title=title, severity=severity)
                        db.add(finding)
                        db.flush()
                        # Add raw evidence JSON
                        db.add(models.Evidence(finding_id=finding.id, data=data))
                        
                        # Calculate Basic Risk Score Component
                        score = 10.0 if severity == "critical" else 7.5 if severity == "high" else 5.0
                        db.add(models.RiskScore(asset_id=asset.id, score=score, reasons={"scanner": "nuclei", "severity": severity}))
                        job.findings_created += 1
                except:
                    job.parse_errors += 1

def get_importer(name: str):
    registry = {"subfinder": SubfinderImporter(), "httpx": HttpxImporter(), "nuclei": NucleiImporter(), "semgrep": SemgrepImporter(), "gitleaks": GitleaksImporter(), "trivy": TrivyImporter(), "checkov": CheckovImporter(), "prowler": ProwlerImporter()}
    return registry.get(name.lower())


class SemgrepImporter(ScannerResultImporter):
    scanner_name = "semgrep"
    supported_formats = ["json"]
    def parse_and_import(self, filepath, project_id, db, job):
        with open(filepath) as f:
            data = json.load(f)
            results = data.get("results", [])
            for res in results:
                try:
                    path = res.get("path")
                    rule = res.get("check_id")
                    extra = res.get("extra", {})
                    sev = extra.get("severity", "WARNING").lower()
                    if sev == "warning": sev = "medium"
                    if sev == "error": sev = "high"
                    
                    asset = db.query(models.Asset).filter_by(project_id=project_id, asset_type="repository", value="local-repo").first()
                    if not asset:
                        asset = models.Asset(project_id=project_id, asset_type="repository", value="local-repo")
                        db.add(asset)
                        db.flush()
                        
                    fp = f"{project_id}:{asset.id}:{rule}:{path}"
                    finding = db.query(models.Finding).filter_by(project_id=project_id, asset_id=asset.id, fingerprint=fp).first()
                    if not finding:
                        finding = models.Finding(
                            project_id=project_id, asset_id=asset.id, title=rule, severity=sev, 
                            domain="APPSEC", finding_type="SAST", location=path, fingerprint=fp, status="OPEN"
                        )
                        db.add(finding)
                        db.add(models.RiskScore(asset_id=asset.id, score=7.0, reasons={"r":"sast"}))
                        job.findings_created += 1
                except: job.parse_errors += 1

class GitleaksImporter(ScannerResultImporter):
    scanner_name = "gitleaks"
    supported_formats = ["json"]
    def parse_and_import(self, filepath, project_id, db, job):
        with open(filepath) as f:
            data = json.load(f)
            for res in data:
                try:
                    secret_type = res.get("RuleID", "Unknown Secret")
                    file_path = res.get("File", "unknown")
                    raw_secret = res.get("Secret", "")
                    
                    # NEVER store the raw secret
                    masked = raw_secret[:4] + "*" * 8 + raw_secret[-4:] if len(raw_secret) > 8 else "***REDACTED***"
                    
                    asset = db.query(models.Asset).filter_by(project_id=project_id, asset_type="repository", value="local-repo").first()
                    if not asset:
                        asset = models.Asset(project_id=project_id, asset_type="repository", value="local-repo")
                        db.add(asset)
                        db.flush()
                    
                    title = f"Exposed {secret_type}"
                    fp = f"{project_id}:{asset.id}:{title}:{file_path}"
                    finding = db.query(models.Finding).filter_by(project_id=project_id, asset_id=asset.id, fingerprint=fp).first()
                    if not finding:
                        finding = models.Finding(
                            project_id=project_id, asset_id=asset.id, title=title, severity="critical",
                            domain="SECRETS", finding_type="SECRET", location=file_path, fingerprint=fp, status="OPEN"
                        )
                        db.add(finding)
                        db.flush()
                        # Add masked evidence
                        db.add(models.Evidence(finding_id=finding.id, data={"masked_secret": masked, "file": file_path}))
                        db.add(models.RiskScore(asset_id=asset.id, score=9.5, reasons={"r":"secret"}))
                        job.findings_created += 1
                except: job.parse_errors += 1

class TrivyImporter(ScannerResultImporter):
    scanner_name = "trivy"
    supported_formats = ["json"]
    def parse_and_import(self, filepath, project_id, db, job):
        with open(filepath) as f:
            data = json.load(f)
            target = data.get("ArtifactName", "unknown-image")
            
            asset = db.query(models.Asset).filter_by(project_id=project_id, asset_type="container_image", value=target).first()
            if not asset:
                asset = models.Asset(project_id=project_id, asset_type="container_image", value=target)
                db.add(asset)
                db.flush()
                
            for res in data.get("Results", []):
                for vuln in res.get("Vulnerabilities", []):
                    title = vuln.get("VulnerabilityID")
                    sev = vuln.get("Severity", "MEDIUM").lower()
                    
                    fp = f"{project_id}:{asset.id}:{title}"
                    finding = db.query(models.Finding).filter_by(project_id=project_id, asset_id=asset.id, fingerprint=fp).first()
                    if not finding:
                        finding = models.Finding(
                            project_id=project_id, asset_id=asset.id, title=title, severity=sev,
                            domain="CONTAINER", finding_type="SCA", fingerprint=fp, status="OPEN"
                        )
                        db.add(finding)
                        db.add(models.RiskScore(asset_id=asset.id, score=8.0, reasons={"r":"container"}))
                        job.findings_created += 1

class CheckovImporter(ScannerResultImporter):
    scanner_name = "checkov"
    supported_formats = ["json"]
    def parse_and_import(self, filepath, project_id, db, job):
        with open(filepath) as f:
            data = json.load(f)
            for res in data.get("results", {}).get("failed_checks", []):
                resource = res.get("resource")
                file_path = res.get("file_path")
                title = res.get("check_id")
                
                asset = db.query(models.Asset).filter_by(project_id=project_id, asset_type="iac_resource", value=resource).first()
                if not asset:
                    asset = models.Asset(project_id=project_id, asset_type="iac_resource", value=resource)
                    db.add(asset)
                    db.flush()
                
                fp = f"{project_id}:{asset.id}:{title}"
                finding = db.query(models.Finding).filter_by(project_id=project_id, asset_id=asset.id, fingerprint=fp).first()
                if not finding:
                    finding = models.Finding(
                        project_id=project_id, asset_id=asset.id, title=title, severity="medium",
                        domain="IAC", finding_type="MISCONFIGURATION", location=file_path, fingerprint=fp, status="OPEN"
                    )
                    db.add(finding)
                    job.findings_created += 1

class ProwlerImporter(ScannerResultImporter):
    scanner_name = "prowler"
    supported_formats = ["json"]
    def parse_and_import(self, filepath, project_id, db, job):
        with open(filepath) as f:
            data = json.load(f)
            for res in data:
                if res.get("Status") != "FAIL": continue
                
                resource = res.get("ResourceArn", "unknown-cloud-resource")
                title = res.get("CheckID")
                sev = res.get("Severity", "medium").lower()
                
                asset = db.query(models.Asset).filter_by(project_id=project_id, asset_type="cloud_resource", value=resource).first()
                if not asset:
                    asset = models.Asset(project_id=project_id, asset_type="cloud_resource", value=resource)
                    db.add(asset)
                    db.flush()
                
                fp = f"{project_id}:{asset.id}:{title}"
                finding = db.query(models.Finding).filter_by(project_id=project_id, asset_id=asset.id, fingerprint=fp).first()
                if not finding:
                    finding = models.Finding(
                        project_id=project_id, asset_id=asset.id, title=title, severity=sev,
                        domain="CLOUD", finding_type="CSPM", fingerprint=fp, status="OPEN"
                    )
                    db.add(finding)
                    job.findings_created += 1
