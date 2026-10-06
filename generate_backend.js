const fs = require('fs');
const path = require('path');
const baseDir = path.join(__dirname, 'backend');

const files = {
  'requirements.txt': `fastapi
uvicorn
sqlalchemy
pydantic`,
  'database.py': `from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./sentinelx.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
`,
  'models.py': `from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    target = Column(String)
    description = Column(String, nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Asset(Base):
    __tablename__ = "assets"
    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"))
    hostname = Column(String, nullable=True)
    ip = Column(String, nullable=True)
    type = Column(String)
    status = Column(String, default="active")
    risk_score = Column(Float, nullable=True)
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())

class Vulnerability(Base):
    __tablename__ = "vulnerabilities"
    id = Column(String, primary_key=True, index=True)
    asset_id = Column(String, ForeignKey("assets.id"))
    name = Column(String)
    severity = Column(String)
    status = Column(String, default="open")
    first_seen = Column(DateTime(timezone=True), server_default=func.now())

class ScanJob(Base):
    __tablename__ = "scans"
    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"))
    status = Column(String, default="pending")
    scan_type = Column(String)
    progress = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
`,
  'main.py': `import uuid
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SentinelX API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/projects")
def get_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).all()

@app.post("/api/v1/projects")
def create_project(project: dict, db: Session = Depends(get_db)):
    db_proj = models.Project(
        id=str(uuid.uuid4()),
        name=project.get('name', 'Unnamed'),
        target=project.get('target', ''),
        description=project.get('description', '')
    )
    db.add(db_proj)
    db.commit()
    db.refresh(db_proj)
    return db_proj

@app.get("/api/v1/assets")
def get_assets(project_id: str = None, db: Session = Depends(get_db)):
    q = db.query(models.Asset)
    if project_id:
        q = q.filter(models.Asset.project_id == project_id)
    return q.all()

@app.get("/api/v1/vulnerabilities")
def get_vulnerabilities(project_id: str = None, severity: str = None, db: Session = Depends(get_db)):
    return db.query(models.Vulnerability).all()

@app.get("/api/v1/scans")
def get_scans(db: Session = Depends(get_db)):
    return db.query(models.ScanJob).all()

@app.post("/api/v1/scans")
def create_scan(scan: dict, db: Session = Depends(get_db)):
    db_scan = models.ScanJob(
        id=str(uuid.uuid4()),
        project_id=scan['project_id'],
        scan_type=scan.get('scan_type', 'full')
    )
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    return db_scan
`
};

for (const [relPath, content] of Object.entries(files)) {
  const fullPath = path.join(baseDir, relPath);
  fs.mkdirSync(path.dirname(fullPath), { recursive: true });
  fs.writeFileSync(fullPath, content.trim() + '\\n', 'utf8');
}
console.log('Backend built successfully!');
