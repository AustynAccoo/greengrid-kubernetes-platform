"""FastAPI routes and application assembly."""

import logging
import os

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse

from telemetry_api import __version__
from telemetry_api.logging_config import configure_logging
from telemetry_api.models import (
    LoadRequest,
    LoadResponse,
    SubmissionResponse,
    TelemetryListResponse,
    TelemetryRecord,
)
from telemetry_api.service import TelemetryService
from telemetry_api.store import TelemetryStore

configure_logging()
LOGGER = logging.getLogger(__name__)
DEFAULT_RETENTION_LIMIT = 1_000


def _retention_limit_from_environment() -> int:
    raw_value = os.getenv("TELEMETRY_RETENTION_LIMIT", str(DEFAULT_RETENTION_LIMIT))
    try:
        value = int(raw_value)
    except ValueError:
        LOGGER.warning("invalid retention limit; using default", extra={"error": raw_value})
        return DEFAULT_RETENTION_LIMIT
    if value < 1:
        LOGGER.warning("retention limit below one; using default", extra={"error": raw_value})
        return DEFAULT_RETENTION_LIMIT
    return value


def create_app(store: TelemetryStore | None = None) -> FastAPI:
    """Create an application with an injectable store for deterministic tests."""

    telemetry_store = (
        store if store is not None else TelemetryStore(_retention_limit_from_environment())
    )
    service = TelemetryService(telemetry_store)
    application = FastAPI(title="GreenGrid Telemetry API", version=__version__)

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        LOGGER.warning(
            "request validation failed",
            extra={"error": str(exc), "path": request.url.path},
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Request validation failed",
                    "details": [
                        {key: value for key, value in error.items() if key != "ctx"}
                        for error in exc.errors()
                    ],
                }
            },
        )

    @application.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
        LOGGER.exception(
            "unexpected request failure",
            extra={"error": str(exc), "path": request.url.path},
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "An unexpected error occurred",
                }
            },
        )

    @application.get("/health/live")
    def liveness() -> dict[str, str]:
        return {"status": "alive", "service": "telemetry-api", "version": __version__}

    @application.get("/health/ready")
    def readiness() -> dict[str, str | int]:
        return {
            "status": "ready",
            "service": "telemetry-api",
            "version": __version__,
            "retention_limit": telemetry_store.retention_limit,
        }

    @application.get("/telemetry", response_model=TelemetryListResponse)
    def get_telemetry() -> TelemetryListResponse:
        records = service.retrieve()
        return TelemetryListResponse(count=len(records), records=records)

    @application.post(
        "/telemetry", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED
    )
    def post_telemetry(record: TelemetryRecord) -> SubmissionResponse:
        retained = service.submit(record)
        LOGGER.info(
            "telemetry accepted",
            extra={"asset_id": record.asset_id, "record_count": retained},
        )
        return SubmissionResponse(
            message="telemetry accepted", retained_records=retained, record=record
        )

    @application.get("/metrics", response_class=PlainTextResponse)
    def metrics() -> str:
        return (
            "# HELP greengrid_telemetry_records Current retained telemetry records.\n"
            "# TYPE greengrid_telemetry_records gauge\n"
            f"greengrid_telemetry_records {len(telemetry_store)}\n"
            "# HELP greengrid_telemetry_submissions_total Accepted telemetry records.\n"
            "# TYPE greengrid_telemetry_submissions_total counter\n"
            f"greengrid_telemetry_submissions_total {service.submission_count()}\n"
        )

    @application.post("/simulate-load", response_model=LoadResponse)
    def simulate_load(request: LoadRequest) -> LoadResponse:
        LOGGER.info("starting bounded load simulation")
        return service.simulate_load(request.duration_ms)

    return application


app = create_app()
