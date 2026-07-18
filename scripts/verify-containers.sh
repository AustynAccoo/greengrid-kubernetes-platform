#!/bin/sh
set -eu

cleanup() {
  docker compose down --remove-orphans
}

trap cleanup EXIT INT TERM

docker compose build
docker compose up --detach --wait
docker compose ps

python3 - <<'PY'
import json
import time
import urllib.request


def get_json(path: str) -> dict[str, object]:
    with urllib.request.urlopen(f"http://127.0.0.1:8000{path}", timeout=5) as response:
        return json.load(response)


live = get_json("/health/live")
ready = get_json("/health/ready")
if live.get("status") != "alive" or ready.get("status") != "ready":
    raise SystemExit("API health verification failed")

deadline = time.monotonic() + 30
while time.monotonic() < deadline:
    telemetry = get_json("/telemetry")
    if int(telemetry.get("count", 0)) > 0:
        print(f"Generated telemetry records: {telemetry['count']}")
        break
    time.sleep(1)
else:
    raise SystemExit("generator did not deliver telemetry within 30 seconds")

print(f"Liveness: {live}")
print(f"Readiness: {ready}")
PY

docker compose exec --no-TTY telemetry-api id
docker compose exec --no-TTY telemetry-generator id

