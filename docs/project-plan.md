# Project Plan

## Goal

Deliver a credible, weekend-sized portfolio demonstration of senior platform-engineering practices without presenting a toy workflow as production-ready.

## Incremental plan

1. [x] Establish repository governance, architecture boundaries, and decision records.
2. [x] Build and test minimal telemetry services.
3. [x] Package hardened, non-root containers.
4. [x] Define reusable Terraform and the isolated development root.
5. [x] Create a secure multi-environment Helm chart and policy validation.
6. [x] Add non-deploying CI gates, dependency maintenance, and immutable-tag enforcement.
7. [x] Define managed Prometheus collection and the restricted scrape path.
8. [ ] Apply and verify the observability change in development; record an HPA and metrics drill.
9. [ ] Add one SLO-backed alert and rehearse failed rollout/rollback.
10. [ ] Add keyless immutable image publishing and controlled promotion.
11. [ ] Add Argo CD desired state only after the promotion contract is working.

## Scope controls

Prefer a small end-to-end path with strong evidence over broad unfinished features. Defer multi-region, complex streaming, and enterprise organizational automation to documented production improvements unless time remains.
