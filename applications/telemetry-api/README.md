# Telemetry API

FastAPI service for validating and retaining recent fictional energy telemetry.

## Dependencies

- **FastAPI** provides typed HTTP routing, validation integration, and OpenAPI documentation.
- **Pydantic** defines strict telemetry request and response schemas.
- **Uvicorn** serves the ASGI application locally on port 8000.

## Local run

From the repository root after installing `requirements-dev.txt`:

```sh
PYTHONPATH=applications/telemetry-api/src \
  .venv/bin/uvicorn telemetry_api.main:app --host 0.0.0.0 --port 8000
```

`TELEMETRY_RETENTION_LIMIT` optionally changes the default 1,000-record in-memory limit.

