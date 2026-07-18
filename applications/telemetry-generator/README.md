# Telemetry Generator

Local process that emits fictional battery, wind, and marine telemetry to the API.

## Dependencies

- **HTTPX** supplies timeout-aware HTTP transport and testable client primitives.
- **Pydantic** validates generated payloads before transmission.

## Configuration

- `TELEMETRY_API_URL` defaults to `http://localhost:8000`.
- `TELEMETRY_INTERVAL_SECONDS` defaults to `5`.
- `TELEMETRY_REQUEST_TIMEOUT_SECONDS` defaults to `5`.
- `TELEMETRY_MAX_RETRIES` defaults to `3`.
- `TELEMETRY_INITIAL_BACKOFF_SECONDS` defaults to `0.5`.
- `TELEMETRY_GENERATOR_HEALTH_FILE` optionally selects a successful-delivery health marker.

Run from the repository root after installing `requirements-dev.txt`:

```sh
PYTHONPATH=applications/telemetry-generator/src \
  .venv/bin/python -m telemetry_generator.main
```
