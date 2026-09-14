# Testing Strategy

## Principles

Tests should be fast at the inner loop, deterministic, risk-based, and layered. Every meaningful change requires relevant validation, and promotion consumes recorded evidence rather than assumptions.

## Implemented layers

- Application: Ruff format/lint plus 14 tests for API health, validation, retention, metrics, development-only bounded load, generator configuration/payloads, exponential backoff, and non-retryable failure behavior.
- Dependency: `pip-audit` resolves the pinned Python manifests and fails on known vulnerabilities.
- Container: both images build and run; the verifier checks health, telemetry flow, UID/GID, read-only root, writable temporary storage, capability drops, and no-new-privileges.
- Terraform: recursive formatting, backend-free initialization, provider-backed validation, and static checks for prohibited IAM, credentials, state, default VPC, Workload Identity, Shielded Nodes, Dataplane V2, and managed Prometheus.
- Helm and Kubernetes: lint, render, client dry-run, and policy assertions across dev/staging/prod. Assertions cover resource counts, security contexts, requests/limits, probes, immutable tags, internal Services, exact network paths, and `PodMonitoring`.
- Local integration: Compose verifies generator-to-API delivery through the service network.
- Post-deployment: documented rollout, Helm test, endpoint, HPA, log, and metrics checks.

## Remaining layers

- Container OS/package vulnerability scanning and signed-image/attestation verification.
- Terraform module tests and recorded cloud plans.
- Automated ephemeral-cluster integration, negative NetworkPolicy tests, and rollback drills.
- GitOps reconciliation and promotion evidence after Argo CD is implemented.

Production promotion would require passing CI, successful staging verification, documented approval, and an explicit rollback plan. No live production promotion is currently claimed.
