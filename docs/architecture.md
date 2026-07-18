# Architecture

## Purpose

GreenGrid will demonstrate a secure Kubernetes platform that produces and serves representative energy telemetry. The foundation intentionally defines boundaries before implementation.

## Planned components

- A Python telemetry generator will emit synthetic readings.
- A Python telemetry API will ingest and expose telemetry.
- Docker will package each service as a non-root, least-privilege image.
- Terraform will manage persistent GCP and GKE infrastructure.
- Helm will package Kubernetes workloads with required resources and probes.
- Argo CD will reconcile environment-specific desired state.
- GitHub Actions will validate changes, build immutable artifacts, and initiate controlled promotion.

## Repository boundaries

Application source, infrastructure, chart packaging, and GitOps desired state remain separate so changes can be validated and reviewed at the correct boundary. Detailed runtime topology, data stores, observability, and availability targets will be decided in later ADRs before implementation.

