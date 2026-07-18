# Local Containers

## Security model

Both images use Python `3.12.11-slim-bookworm` pinned to an immutable multi-platform digest. They install only their service-specific pinned runtime requirements, copy only source code, run as UID/GID `10001`, use exec-form process commands, and contain no credentials. OCI labels identify the application, version, license, and source repository.

Compose adds read-only root filesystems, bounded temporary filesystems, all-capability drops, `no-new-privileges`, PID limits, CPU and memory limits, and a Docker-internal service network. The generator is attached only to that internal network. The API also joins a dedicated edge network so Docker Desktop can publish API port 8000; no generator port is exposed. These controls improve local parity but do not replace orchestration policy or production hardening.

The API health check calls `/health/ready`. The generator becomes healthy only after successfully delivering telemetry and refreshing its health marker. Compose starts the generator after the API is healthy. Both services receive `SIGTERM`: Uvicorn handles graceful ASGI shutdown, and the generator has explicit `SIGINT` and `SIGTERM` handlers.

## Configuration

Copy `.env.example` to `.env` only when overriding the safe Compose defaults. The file contains no credentials and `.env` remains ignored by Git.

## Commands

```sh
make install  # Create a Python 3.12 virtual environment and install pinned dev dependencies
make format   # Check formatting
make lint     # Run Ruff linting
make test     # Run the complete unit suite
make build    # Build both local images
make run      # Start both services and wait for health
make logs     # Follow service logs
make stop     # Stop and remove the local Compose containers
make verify   # Run local code gates and container verification
make clean    # Stop Compose and remove local images/caches
```

After `make run`, inspect `http://localhost:8000/health/live`, `http://localhost:8000/health/ready`, and `http://localhost:8000/telemetry`.

## Immutable production references

The `:local` image tags are intentionally limited to local development. A production promotion must reference the same CI-built image by Git commit SHA and preferably its registry digest, for example:

```text
us-docker.pkg.dev/example-project/greengrid/telemetry-api:git-a1b2c3d@sha256:<digest>
```

Never use `latest` for an environment deployment.

## Troubleshooting

- If Docker is unavailable, start the local Docker engine and rerun `docker info`.
- If port 8000 is occupied, set `TELEMETRY_API_HOST_PORT` in an untracked `.env`.
- If the generator is unhealthy, inspect `docker compose logs telemetry-generator` and confirm the API is healthy.
- Use `docker compose ps` for health state and `docker compose exec <service> id` to verify runtime identity.
