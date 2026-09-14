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

for service in telemetry-api telemetry-generator; do
  uid="$(docker compose exec --no-TTY "$service" id -u)"
  gid="$(docker compose exec --no-TTY "$service" id -g)"
  [ "$uid" = "10001" ] || { echo "$service runs as unexpected UID $uid" >&2; exit 1; }
  [ "$gid" = "10001" ] || { echo "$service runs as unexpected GID $gid" >&2; exit 1; }

  if docker compose exec --no-TTY "$service" sh -c 'touch /rootfs-write-test' >/dev/null 2>&1; then
    echo "$service root filesystem is writable" >&2
    exit 1
  fi
  docker compose exec --no-TTY "$service" sh -c 'touch /tmp/runtime-write-test && rm /tmp/runtime-write-test'

  container_id="$(docker compose ps --quiet "$service")"
  [ "$(docker inspect --format '{{.HostConfig.ReadonlyRootfs}}' "$container_id")" = "true" ] || {
    echo "$service read-only root filesystem setting is missing" >&2
    exit 1
  }
  cap_drop="$(docker inspect --format '{{range .HostConfig.CapDrop}}{{.}} {{end}}' "$container_id")"
  case " $cap_drop " in
    *" ALL "*) ;;
    *) echo "$service does not drop all Linux capabilities" >&2; exit 1 ;;
  esac
  security_options="$(docker inspect --format '{{range .HostConfig.SecurityOpt}}{{.}} {{end}}' "$container_id")"
  case " $security_options " in
    *" no-new-privileges:true "*) ;;
    *) echo "$service does not enforce no-new-privileges" >&2; exit 1 ;;
  esac

  echo "$service runtime contract passed (uid=$uid gid=$gid, read-only root, drop ALL)."
done
