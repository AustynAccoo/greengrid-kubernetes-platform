# ADR 002: Use GitOps with Argo CD

- Status: Accepted
- Date: 2026-07-17

## Context

Environment changes require review, auditability, reproducibility, controlled promotion, and reliable rollback.

## Decision

Use Argo CD to reconcile declared environment state stored under `gitops/`. Promote immutable artifact digests through reviewed configuration changes from development to staging to production.

## Consequences

Git history becomes the desired-state audit trail and rollback uses known-good revisions. Repository access and Argo CD permissions become security-critical, drift is reconciled, and emergency procedures must remain documented and reviewed after use.

