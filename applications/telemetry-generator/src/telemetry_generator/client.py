"""HTTP transport with bounded retry and exponential backoff."""

import logging
import time
from collections.abc import Callable
from typing import Any

import httpx

from telemetry_generator.config import GeneratorConfig

LOGGER = logging.getLogger(__name__)


class TelemetryClient:
    """Submit generated records to the telemetry API."""

    def __init__(
        self,
        config: GeneratorConfig,
        client: httpx.Client | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.config = config
        self._client = client or httpx.Client(timeout=config.request_timeout_seconds)
        self._owns_client = client is None
        self._sleep = sleep

    def send(self, payload: dict[str, Any]) -> bool:
        """Send a payload, retrying transient transport and server failures."""

        for attempt in range(self.config.max_retries + 1):
            try:
                response = self._client.post(f"{self.config.api_url}/telemetry", json=payload)
                response.raise_for_status()
                LOGGER.info(
                    "telemetry sent",
                    extra={
                        "asset_id": payload["asset_id"],
                        "attempt": attempt + 1,
                        "status_code": response.status_code,
                    },
                )
                return True
            except (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError) as exc:
                retryable = (
                    not isinstance(exc, httpx.HTTPStatusError) or exc.response.status_code >= 500
                )
                if not retryable or attempt >= self.config.max_retries:
                    LOGGER.error(
                        "telemetry delivery failed",
                        extra={"attempt": attempt + 1, "error": str(exc)},
                    )
                    return False
                delay = self.config.initial_backoff_seconds * (2**attempt)
                LOGGER.warning(
                    "telemetry delivery retry scheduled",
                    extra={"attempt": attempt + 1, "error": str(exc)},
                )
                self._sleep(delay)
        return False

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "TelemetryClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
