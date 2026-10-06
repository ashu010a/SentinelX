import sys
sys.path.append('backend')
from database import Base, engine, SessionLocal
from models import ScanJob, Target, Project
import worker

Base.metadata.create_all(bind=engine)
db = SessionLocal()
p = Project(name='Test')
t = Target(project_id=p.id, target_value='example.com')
s = ScanJob(project_id=p.id, target_id=t.id)
db.add_all([p,t,s])
db.commit()

try:
    print("Executing scan...")
    worker.execute_scan_sync(s.id)
    db.refresh(s)
    print("Status:", s.status)
except Exception as e:
    import traceback
    traceback.print_exc()
