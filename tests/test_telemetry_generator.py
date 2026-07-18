"""Unit tests for generator configuration, payloads, and retries."""

import random

import httpx
import pytest

from telemetry_generator.client import TelemetryClient
from telemetry_generator.config import GeneratorConfig
from telemetry_generator.payloads import create_payload


def test_generator_payload_creation() -> None:
    payload = create_payload(random.Random(7))

    assert payload["asset_type"] in {"battery", "wind", "marine"}
    assert payload["status"] in {"healthy", "warning", "critical"}
    assert payload["timestamp"].endswith("Z")
    if payload["asset_type"] == "battery":
        assert 0 <= payload["state_of_charge"] <= 100
    else:
        assert payload["state_of_charge"] is None


def test_generator_environment_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEMETRY_API_URL", "http://api.internal:9000/")
    monkeypatch.setenv("TELEMETRY_INTERVAL_SECONDS", "2.5")

    config = GeneratorConfig.from_environment()

    assert config.api_url == "http://api.internal:9000"
    assert config.interval_seconds == 2.5


def test_generator_retries_with_exponential_backoff() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        status_code = 503 if attempts < 3 else 201
        return httpx.Response(status_code, request=request)

    delays: list[float] = []
    config = GeneratorConfig(max_retries=3, initial_backoff_seconds=0.25)
    http_client = httpx.Client(transport=httpx.MockTransport(handler))

    with http_client:
        client = TelemetryClient(config, client=http_client, sleep=delays.append)
        delivered = client.send(create_payload(random.Random(1)))

    assert delivered is True
    assert attempts == 3
    assert delays == [0.25, 0.5]
