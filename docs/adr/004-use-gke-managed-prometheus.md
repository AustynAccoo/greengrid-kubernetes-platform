# ADR 004: Use GKE Managed Service for Prometheus

- Status: Accepted
- Date: 2026-09-11

## Context

The telemetry API exposes typed Prometheus metrics, but the development cluster configuration disabled managed collection and the Helm chart had no scrape resource. Operating a separate Prometheus stack would add storage, upgrades, identity, and scaling work that does not advance the project's core demonstration. Default-deny ingress also means a collector cannot scrape the API unless its path is deliberately modeled.

## Decision

Enable GKE Managed Service for Prometheus in the Terraform GKE module. Grant the custom node service account `roles/monitoring.metricWriter` so the managed collector can push metrics without a key.

Create a namespace-scoped `PodMonitoring` resource in the Helm chart. Select telemetry API pods by stable labels, scrape the named `http` port at `/metrics` every 30 seconds, and set a 10-second timeout plus sample and label limits.

Add a NetworkPolicy that permits TCP 8000 only from pods labeled `app.kubernetes.io/name=collector` in the Standard GKE `gmp-system` namespace. Keep all other default-deny behavior.

## Consequences

- GKE owns collector lifecycle, sharding, and upgrades.
- Application metrics are available through Cloud Monitoring and PromQL without operating a standalone metrics database.
- The collection path spans Terraform, node IAM, a Kubernetes custom resource, workload labels/ports, and NetworkPolicy, so all of those contracts require validation.
- Custom-metric ingestion can create cost; scrape and cardinality limits plus Metrics Management review are required.
- The chart assumes the managed Prometheus CRDs exist before installation. Infrastructure must be updated before the Helm release.
- This decision does not create dashboards, SLOs, notification channels, or alert policies; those require separate design and validation.
