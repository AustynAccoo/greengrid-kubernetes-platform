# ADR 001: Use Google Kubernetes Engine

- Status: Accepted
- Date: 2026-07-17

## Context

GreenGrid must demonstrate production-style Kubernetes platform engineering on Google Cloud while keeping the implementation achievable within a weekend.

## Decision

Use GKE as the managed Kubernetes control plane. Terraform will manage persistent GCP infrastructure, and Kubernetes configuration will be delivered through Helm and GitOps.

## Consequences

GKE provides relevant managed-platform experience and integrates with Google IAM and Workload Identity. The project must control cost, pin and document platform choices, and clearly distinguish portfolio shortcuts from a real organization's project and network isolation.

