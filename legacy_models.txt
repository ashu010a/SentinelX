from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, JSON, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, index=True)

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, index=True)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class Target(Base):
    __tablename__ = "targets"
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id"), index=True)
    target_value = Column(String)

class Asset(Base):
    __tablename__ = "assets"
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id"), index=True)
    asset_type = Column(String)
    first_seen_scan_id = Column(String)
    last_seen_scan_id = Column(String) # domain, ip
    value = Column(String, index=True)
    criticality = Column(String, default='medium')
    exposed = Column(Boolean, default=False)

class Domain(Base):
    __tablename__ = "domains"
    id = Column(String, primary_key=True, default=generate_uuid)
    asset_id = Column(String, ForeignKey("assets.id"), index=True)
    fqdn = Column(String)

class IPAddress(Base):
    __tablename__ = "ip_addresses"
    id = Column(String, primary_key=True, default=generate_uuid)
    asset_id = Column(String, ForeignKey("assets.id"), index=True)
    ip = Column(String)

class Service(Base):
    __tablename__ = "services"
    id = Column(String, primary_key=True, default=generate_uuid)
    asset_id = Column(String, ForeignKey("assets.id"), index=True)
    port = Column(Integer)
    protocol = Column(String)

class Endpoint(Base):
    __tablename__ = "endpoints"
    id = Column(String, primary_key=True, default=generate_uuid)
    service_id = Column(String, ForeignKey("services.id"), index=True)
    url = Column(String)

class Technology(Base):
    __tablename__ = "technologies"
    id = Column(String, primary_key=True, default=generate_uuid)
    asset_id = Column(String, ForeignKey("assets.id"), index=True)
    name = Column(String)

class Certificate(Base):
    __tablename__ = "certificates"
    id = Column(String, primary_key=True, default=generate_uuid)
    asset_id = Column(String, ForeignKey("assets.id"), index=True)
    issuer = Column(String)

class ScanJob(Base):
    __tablename__ = "scan_jobs"
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id"), index=True)
    target_id = Column(String, ForeignKey("targets.id"), index=True)
    status = Column(String, default="queued") # queued, running, completed, failed
    progress = Column(Integer, default=0)

class Finding(Base):
    __tablename__ = "findings"
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id"), index=True)
    asset_id = Column(String, ForeignKey("assets.id"), index=True)
    title = Column(String)
    severity = Column(String)
    domain = Column(String, default='EXTERNAL')
    finding_type = Column(String, default='VULNERABILITY')
    location = Column(String, nullable=True)
    status = Column(String, default='OPEN')
    remediation_status = Column(String, default='OPEN')
    owner = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=True)
    remediation_notes = Column(Text, nullable=True)
    compliance_mappings = Column(JSON, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    reopening_count = Column(Integer, default=0)
    first_seen_scan_id = Column(String)
    last_seen_scan_id = Column(String)
    status = Column(String, default='OPEN')
    remediation_status = Column(String, default='OPEN')
    owner = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=True)
    remediation_notes = Column(Text, nullable=True)
    compliance_mappings = Column(JSON, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    reopening_count = Column(Integer, default=0)
    first_seen_scan_id = Column(String)
    last_seen_scan_id = Column(String)
    fingerprint = Column(String, index=True)
    occurrence_count = Column(Integer, default=1)
    scanner_sources = Column(String)
    cvss = Column(Float, nullable=True)
    kev = Column(Boolean, default=False)
    epss = Column(Float, default=0.0)
    confidence = Column(String, default='certain')

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(String, primary_key=True, default=generate_uuid)
    finding_id = Column(String, ForeignKey("findings.id"), index=True)
    data = Column(JSON)

class RiskScore(Base):
    __tablename__ = "risk_scores"
    id = Column(String, primary_key=True, default=generate_uuid)
    asset_id = Column(String, ForeignKey("assets.id"), index=True)
    score = Column(Float)
    reasons = Column(JSON)

class AssetChange(Base):
    __tablename__ = "asset_changes"
    id = Column(String, primary_key=True, default=generate_uuid)
    asset_id = Column(String, ForeignKey("assets.id"), index=True)
    change_type = Column(String)


class ImportJob(Base):
    __tablename__ = "import_jobs"
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    project_id = Column(String, ForeignKey("projects.id"), index=True)
    scanner_name = Column(String)
    status = Column(String, default="queued") # queued, processing, completed, failed
    assets_created = Column(Integer, default=0)
    assets_updated = Column(Integer, default=0)
    findings_created = Column(Integer, default=0)
    findings_updated = Column(Integer, default=0)
    findings_resolved = Column(Integer, default=0)
    parse_errors = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

class RiskHistory(Base):
    __tablename__ = "risk_history"
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    entity_type = Column(String, index=True) # finding, asset, project
    entity_id = Column(String, index=True)
    project_id = Column(String, index=True)
    score = Column(Float)
    previous_score = Column(Float, nullable=True)
    delta = Column(Float, default=0.0)
    trend = Column(String) # increased, decreased, unchanged
    category = Column(String)
    factors = Column(JSON)
    explanation = Column(Text)
    policy_version = Column(String)
    calculated_at = Column(DateTime, server_default=func.now())

class Relationship(Base):
    __tablename__ = "relationships"
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    project_id = Column(String, ForeignKey("projects.id"), index=True)
    source_id = Column(String, index=True)
    target_id = Column(String, index=True)
    relationship_type = Column(String, index=True)
    confidence = Column(Float)
    evidence = Column(String)
    explanation = Column(Text)
    first_seen = Column(DateTime, server_default=func.now())
    last_seen = Column(DateTime, server_default=func.now())

class ProjectSnapshot(Base):
    __tablename__ = "project_snapshots"
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    project_id = Column(String, ForeignKey("projects.id"), index=True)
    scan_id = Column(String, index=True)
    asset_count = Column(Integer, default=0)
    finding_count = Column(Integer, default=0)
    project_risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())

class TimelineEvent(Base):
    __tablename__ = "timeline_events"
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    project_id = Column(String, ForeignKey("projects.id"), index=True)
    scan_id = Column(String, index=True)
    event_type = Column(String) # NEW_FINDING, RESOLVED_FINDING, NEW_ASSET, RISK_INCREASED
    severity = Column(String)
    domain = Column(String, default='EXTERNAL')
    finding_type = Column(String, default='VULNERABILITY')
    location = Column(String, nullable=True)
    status = Column(String, default='OPEN')
    remediation_status = Column(String, default='OPEN')
    owner = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=True)
    remediation_notes = Column(Text, nullable=True)
    compliance_mappings = Column(JSON, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    reopening_count = Column(Integer, default=0)
    first_seen_scan_id = Column(String)
    last_seen_scan_id = Column(String)
    asset_id = Column(String, nullable=True)
    finding_id = Column(String, nullable=True)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    explanation = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class MonitoringProfile(Base):
    __tablename__ = "monitoring_profiles"
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    project_id = Column(String, ForeignKey("projects.id"), index=True)
    schedule = Column(String) # daily, weekly
    enabled = Column(Boolean, default=True)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    project_id = Column(String, ForeignKey("projects.id"), index=True)
    message = Column(String)
    severity = Column(String)
    domain = Column(String, default='EXTERNAL')
    finding_type = Column(String, default='VULNERABILITY')
    location = Column(String, nullable=True)
    status = Column(String, default='OPEN')
    remediation_status = Column(String, default='OPEN')
    owner = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=True)
    remediation_notes = Column(Text, nullable=True)
    compliance_mappings = Column(JSON, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    reopening_count = Column(Integer, default=0)
    first_seen_scan_id = Column(String)
    last_seen_scan_id = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

class AIConversation(Base):
    __tablename__ = "ai_conversations"
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    project_id = Column(String, ForeignKey("projects.id"), index=True)
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime, server_default=func.now())

class AIMessage(Base):
    __tablename__ = "ai_messages"
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    conversation_id = Column(String, ForeignKey("ai_conversations.id"), index=True)
    role = Column(String) # user, assistant, system
    content = Column(Text)
    model_used = Column(String, nullable=True)
    provider = Column(String, nullable=True)
    sources = Column(JSON, nullable=True) # Array of evidence IDs
    created_at = Column(DateTime, server_default=func.now())

class ProjectSettings(Base):
    __tablename__ = 'project_settings'
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    project_id = Column(String, ForeignKey('projects.id'), index=True)
    sla_critical_days = Column(Integer, default=1)
    sla_high_days = Column(Integer, default=7)
    sla_medium_days = Column(Integer, default=30)
    sla_low_days = Column(Integer, default=90)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    project_id = Column(String, ForeignKey("projects.id"), index=True)
    user_id = Column(String)
    action = Column(String)
    object_type = Column(String)
    object_id = Column(String)
    metadata_json = Column(JSON)
    timestamp = Column(DateTime, server_default=func.now())

class Report(Base):
    __tablename__ = "reports"
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    project_id = Column(String, ForeignKey("projects.id"), index=True)
    report_type = Column(String)
    status = Column(String, default="COMPLETED")
    filter_config = Column(JSON, nullable=True)
    format = Column(String)
    file_path = Column(String, nullable=True)
    generated_by = Column(String, default="system")
    generated_at = Column(DateTime, server_default=func.now())
