"""Validated request and response models for telemetry."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AssetType(StrEnum):
    """Supported fictional energy asset categories."""

    BATTERY = "battery"
    WIND = "wind"
    MARINE = "marine"


class AssetStatus(StrEnum):
    """Supported operational health states."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"


class TelemetryRecord(BaseModel):
    """One validated energy telemetry reading."""

    model_config = ConfigDict(extra="forbid")

    asset_id: str = Field(min_length=1, max_length=128)
    asset_type: AssetType
    temperature_c: float = Field(ge=-100, le=250)
    power_output_kw: float = Field(ge=0)
    state_of_charge: float | None = Field(default=None, ge=0, le=100)
    status: AssetStatus
    timestamp: datetime

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_timezone_aware(cls, value: datetime) -> datetime:
        """Reject ambiguous timestamps without a UTC offset."""

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        return value


class TelemetryListResponse(BaseModel):
    """Structured collection response."""

    count: int
    records: list[TelemetryRecord]


class SubmissionResponse(BaseModel):
    """Structured ingestion acknowledgement."""

    message: str
    retained_records: int
    record: TelemetryRecord


class LoadRequest(BaseModel):
    """Bounded local CPU-load simulation parameters."""

    duration_ms: int = Field(default=100, ge=1, le=5_000)


class LoadResponse(BaseModel):
    """Load simulation result."""

    message: str
    duration_ms: int
    iterations: int
