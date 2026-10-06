from fastapi.testclient import TestClient
import time
from main import app

# TestClient runs background tasks synchronously in the same thread, 
# making it perfect for testing our background scanner pipeline!
client = TestClient(app)

print("--- 1. Creating Project ---")
response = client.post("/api/v1/projects", json={
    "name": "Test Run",
    "target": "example.com",
    "description": "Automated tool test"
})
project_data = response.json()
print("Project created:", project_data)
project_id = project_data.get("id")

print("\n--- 2. Triggering Scan ---")
response = client.post("/api/v1/scans", json={
    "project_id": project_id,
    "scan_type": "full"
})
scan_data = response.json()
print("Scan job created:", scan_data)

print("\n--- 3. Fetching Discovered Assets ---")
response = client.get(f"/api/v1/assets?project_id={project_id}")
print("Assets found:", response.json())

print("\n--- 4. Fetching Discovered Vulnerabilities ---")
response = client.get(f"/api/v1/vulnerabilities?project_id={project_id}")
print("Vulnerabilities found:", response.json())
