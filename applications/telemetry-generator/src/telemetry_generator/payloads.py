"""Creation of fictional, schema-compatible telemetry payloads."""

import random
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

ASSETS: tuple[tuple[str, str], ...] = (
    ("battery-001", "battery"),
    ("wind-001", "wind"),
    ("marine-001", "marine"),
)


class GeneratedTelemetry(BaseModel):
    """Generator-side contract matching the telemetry API schema."""

    model_config = ConfigDict(extra="forbid")

    asset_id: str
    asset_type: str
    temperature_c: float
    power_output_kw: float = Field(ge=0)
    state_of_charge: float | None = Field(default=None, ge=0, le=100)
    status: str
    timestamp: datetime


def create_payload(rng: random.Random | None = None) -> dict[str, Any]:
    """Generate one plausible fictional reading."""

    random_source = rng or random.Random()
    asset_id, asset_type = random_source.choice(ASSETS)
    temperature = round(random_source.uniform(5.0, 75.0), 2)
    status = "healthy" if temperature < 55 else "warning" if temperature < 68 else "critical"
    state_of_charge = (
        round(random_source.uniform(10.0, 100.0), 2) if asset_type == "battery" else None
    )
    record = GeneratedTelemetry(
        asset_id=asset_id,
        asset_type=asset_type,
        temperature_c=temperature,
        power_output_kw=round(random_source.uniform(0.0, 2_500.0), 2),
        state_of_charge=state_of_charge,
        status=status,
        timestamp=datetime.now(UTC),
    )
    return record.model_dump(mode="json")
