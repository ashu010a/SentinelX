# Railway Multipart Form Fix

## Root Cause
The FastAPI application successfully built inside Docker but crashed immediately on startup during Railway's initialization sequence. The stack trace `RuntimeError: Form data requires "python-multipart" to be installed` occurs when `uvicorn` boots and FastAPI initializes the routing tree. 

Because we previously built endpoints that ingest Scanner Result files (using FastAPI's `UploadFile = File(...)` mechanism), FastAPI lazily expects the `python-multipart` module to be available in the execution environment to parse `multipart/form-data` requests. Without it, the router panics and crashes the container prior to Liveness/Readiness probe execution.

## Changed Files
- `backend/requirements.txt`

## Dependency Version
```text
python-multipart>=0.0.9
```
I appended this explicitly to the production requirements so that Docker automatically pulls it during the `pip install --no-cache-dir -r requirements.txt` stage of the Railway build process.

## Local Verification Commands
*(Executed within the local Python sandbox context simulating the Railway Docker container state)*
```bash
# Force reinstall and validation of dependency DAG
pip install --no-cache-dir -r backend/requirements.txt

# Run the complete integration test suite ensuring FastAPI Uvicorn boot doesn't trigger the RuntimeError
python run_rc1_checks.py
```

## Verification Results
- **FastAPI Startup:** The routing tree initialized successfully without the `RuntimeError`.
- **Probes:** `/health` and `/ready` endpoints returned `200 OK`.
- **Upload Functionality:** The backend test suite gracefully executed file-based Scanner Result imports.
- **Image Integrity:** The fix relies exclusively on standard Python packaging inside the `requirements.txt` manifest, guaranteeing the immutable Docker image correctly contains the `python-multipart` binaries at runtime.
