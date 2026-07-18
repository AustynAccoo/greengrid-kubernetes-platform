# Deployment Process

## Planned workflow

1. A pull request runs formatting, tests, security checks, Terraform validation, and Helm/GitOps rendering.
2. Required reviewers approve the change before merge.
3. CI builds each affected container once, tags it with the Git commit SHA, records its digest, and publishes provenance.
4. A reviewed GitOps change references that immutable digest for development.
5. Successful development evidence permits a reviewed promotion of the same digest to staging.
6. Staging validation and documented approval permit production promotion of that same digest.
7. Argo CD reconciles approved desired state; health and smoke checks verify the rollout.

## Rollback

Rollback is a reviewed or authorized emergency Git revert to the last known-good configuration and artifact digest. The team verifies Argo CD health, workload probes, service behavior, and telemetry flow afterward. Emergency changes receive retrospective review.

No deployment automation or live resources exist in the repository foundation.

