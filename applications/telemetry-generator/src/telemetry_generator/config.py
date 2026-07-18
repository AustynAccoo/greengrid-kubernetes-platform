"""Environment-backed generator configuration."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratorConfig:
    """Validated runtime settings with local-development defaults."""

    api_url: str = "http://localhost:8000"
    interval_seconds: float = 5.0
    request_timeout_seconds: float = 5.0
    max_retries: int = 3
    initial_backoff_seconds: float = 0.5

    @classmethod
    def from_environment(cls) -> "GeneratorConfig":
        """Load supported settings without accepting secrets."""

        defaults = cls()
        return cls(
            api_url=os.getenv("TELEMETRY_API_URL", defaults.api_url).rstrip("/"),
            interval_seconds=_positive_float(
                "TELEMETRY_INTERVAL_SECONDS", defaults.interval_seconds
            ),
            request_timeout_seconds=_positive_float(
                "TELEMETRY_REQUEST_TIMEOUT_SECONDS", defaults.request_timeout_seconds
            ),
            max_retries=_non_negative_int("TELEMETRY_MAX_RETRIES", defaults.max_retries),
            initial_backoff_seconds=_positive_float(
                "TELEMETRY_INITIAL_BACKOFF_SECONDS", defaults.initial_backoff_seconds
            ),
        )


def _positive_float(name: str, default: float) -> float:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return value


def _non_negative_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if value < 0:
        raise ValueError(f"{name} must be zero or greater")
    return value
