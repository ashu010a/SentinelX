import sys
from fastapi.testclient import TestClient

sys.path.append('backend')
from app.main import app

client = TestClient(app)

def run_verification():
    print("1. Checking API Health...")
    assert client.get("/api/v1/health").status_code == 200
    
    print("2. Creating Project...")
    project_id = client.post("/api/v1/projects", json={"name": "MVP Test"}).json()['id']
    
    print("3. Adding Target...")
    target_id = client.post(f"/api/v1/projects/{project_id}/targets", json={"target_value": "example.com"}).json()['id']
    
    print("4. Triggering Scan & Executing Pipeline...")
    scan = client.post(f"/api/v1/scans", json={"project_id": project_id, "target_id": target_id}).json()
    assert scan['status'] == 'completed', "Scan failed or queued"
        
    print("5. Verifying Assets...")
    assets = client.get(f"/api/v1/projects/{project_id}/assets").json()
    print(f"Found {len(assets)} assets.")
    assert len(assets) > 0, "No assets found"

    print("6. Verifying Findings...")
    findings = client.get(f"/api/v1/projects/{project_id}/findings").json()
    print(f"Found {len(findings)} findings.")
    assert len(findings) > 0, "No findings found"
    
    print("VERIFICATION SUCCESSFUL: Full Data Pipeline Works.")

if __name__ == "__main__":
    run_verification()
