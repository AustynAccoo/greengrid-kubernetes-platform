# ADR 003: Use Workload Identity

- Status: Accepted
- Date: 2026-07-17

## Context

Kubernetes workloads may need GCP API access. Static service-account keys create long-lived secret material and increase rotation and leakage risk.

## Decision

Use GKE Workload Identity with dedicated Kubernetes ServiceAccounts and least-privilege Google service accounts. Do not use static GCP keys or the default Kubernetes ServiceAccount.

## Consequences

Identity bindings must be managed as code and tested per environment. Permissions become short-lived and workload-bound, reducing credential exposure while adding configuration that requires careful naming, IAM review, and troubleshooting guidance.
