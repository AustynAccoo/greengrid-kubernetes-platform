"""Unit tests for telemetry API behavior and bounded retention."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from telemetry_api.main import create_app
from telemetry_api.store import TelemetryStore


def telemetry_payload(asset_id: str = "battery-001") -> dict[str, object]:
    return {
        "asset_id": asset_id,
        "asset_type": "battery",
        "temperature_c": 24.5,
        "power_output_kw": 500.0,
        "state_of_charge": 82.0,
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
    }


def test_liveness_endpoint() -> None:
    response = TestClient(create_app()).get("/health/live")

    assert response.status_code == 200
    assert response.json()["status"] == "alive"
    assert response.json()["version"] == "0.1.0"


def test_readiness_endpoint() -> None:
    response = TestClient(create_app()).get("/health/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["retention_limit"] == 1_000


def test_valid_telemetry_submission() -> None:
    response = TestClient(create_app()).post("/telemetry", json=telemetry_payload())

    assert response.status_code == 201
    assert response.json()["message"] == "telemetry accepted"
    assert response.json()["retained_records"] == 1


def test_invalid_asset_type_rejected() -> None:
    payload = telemetry_payload()
    payload["asset_type"] = "solar"

    response = TestClient(create_app()).post("/telemetry", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_invalid_state_of_charge_rejected() -> None:
    payload = telemetry_payload()
    payload["state_of_charge"] = 101

    response = TestClient(create_app()).post("/telemetry", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_telemetry_retrieval() -> None:
    client = TestClient(create_app())
    client.post("/telemetry", json=telemetry_payload("battery-002"))

    response = client.get("/telemetry")

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["records"][0]["asset_id"] == "battery-002"


def test_record_retention_limit_discards_oldest() -> None:
    client = TestClient(create_app(TelemetryStore(retention_limit=2)))
    for asset_id in ("battery-001", "battery-002", "battery-003"):
        assert client.post("/telemetry", json=telemetry_payload(asset_id)).status_code == 201

    response = client.get("/telemetry")

    assert response.json()["count"] == 2
    assert [item["asset_id"] for item in response.json()["records"]] == [
        "battery-002",
        "battery-003",
    ]


def test_metrics_endpoint_exposes_typed_api_metrics() -> None:
    client = TestClient(create_app())
    assert client.post("/telemetry", json=telemetry_payload()).status_code == 201

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "# TYPE greengrid_telemetry_records gauge" in response.text
    assert "greengrid_telemetry_records 1" in response.text
    assert "# TYPE greengrid_telemetry_submissions_total counter" in response.text
    assert "greengrid_telemetry_submissions_total 1" in response.text


def test_load_simulation_is_bounded_by_request_validation() -> None:
    client = TestClient(create_app(load_simulation_enabled=True))

    accepted = client.post("/simulate-load", json={"duration_ms": 1})
    rejected = client.post("/simulate-load", json={"duration_ms": 5_001})

    assert accepted.status_code == 200
    assert accepted.json()["duration_ms"] == 1
    assert accepted.json()["iterations"] > 0
    assert rejected.status_code == 422


def test_load_simulation_is_disabled_by_default() -> None:
    response = TestClient(create_app()).post("/simulate-load", json={"duration_ms": 1})

    assert response.status_code == 404
