# Testing Strategy

## Principles

Tests should be fast at the inner loop, deterministic, risk-based, and layered. Every meaningful change requires relevant validation, and promotion consumes recorded evidence rather than assumptions.

## Planned layers

- Application: formatting, linting, type checks, unit tests, and API contract tests.
- Container: build validation, non-root execution, vulnerability scanning, and minimal-content checks.
- Terraform: formatting, validation, static analysis, module tests, and reviewed plans; no automatic apply from pull requests.
- Helm and Kubernetes: linting, template rendering, schema checks, policy tests, and assertions for resources, probes, ServiceAccounts, and network policy.
- Integration: telemetry generation, ingestion, querying, failure behavior, and authentication boundaries.
- Delivery: workflow tests, GitOps render checks, immutable-tag enforcement, deployment health checks, rollback exercises, and smoke tests.

Production promotion will require passing CI, successful staging verification, documented approval, and an explicit rollback plan.

