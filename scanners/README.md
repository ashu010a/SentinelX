# Scanners

This directory contains integrations and wrappers for various security tools used by SentinelX.

## Overview

- Scanner tools (like subfinder, httpx, etc.) are installed inside the `worker` Docker container.
- Each scanner is called via the `subprocess` module from the Celery worker executing the scan task.
- Results are parsed from standard output (often JSON) and saved to the database.

## Adding a New Scanner

To integrate a new scanner tool into the pipeline:

1. **Install in Dockerfile.worker**: Add the installation commands (e.g., `go install ...`) to the worker's Dockerfile.
2. **Add Runner Method**: Create or update a module in `scanner_service.py` to wrap the CLI execution of the tool, passing necessary arguments and capturing output.
3. **Add Step in Pipeline Task**: Update the core scan celery task to invoke the new scanner service method at the appropriate stage of the pipeline and handle its results.
