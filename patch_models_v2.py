import re

with open('backend/models.py', 'r') as f:
    code = f.read()

# Delete old AuditLog
code = re.sub(r'class AuditLog\(Base\):.*?(?=\nclass|\Z)', '', code, flags=re.DOTALL)

# Delete old Report
code = re.sub(r'class Report\(Base\):.*?(?=\nclass|\Z)', '', code, flags=re.DOTALL)

# Append new versions
code += """
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
"""

with open('backend/models.py', 'w') as f:
    f.write(code)
