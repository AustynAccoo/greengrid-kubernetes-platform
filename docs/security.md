# Security

## Baseline controls

- Prevent secrets, tokens, credentials, and service-account keys from entering Git.
- Use Workload Identity for GCP access and dedicated Kubernetes ServiceAccounts.
- Run containers as non-root with read-only filesystems and dropped capabilities where compatible.
- Define CPU and memory requests and limits plus startup, readiness, and liveness probes.
- Begin with default-deny NetworkPolicies and allow only required flows.
- Grant minimal IAM, CI, GitOps, and runtime permissions.
- Tag images with Git commit SHAs, enforce immutable Docker tags in Artifact Registry, build once, and promote the same digest. Registry enforcement takes effect after the approved Terraform change.
- Require validation, review, and documented approval for sensitive changes.

## Automated verification

CI currently enforces Python vulnerability auditing, immutable dependency pins, application tests, container runtime contracts, Terraform prohibited-pattern checks, and rendered Helm assertions. The Helm verifier checks pod security, identities, resources, probes, internal-only Services, exact network peers/ports, and the managed Prometheus scrape contract for all three environment overlays. The Helm-test egress contract requires only same-namespace, same-release telemetry API pods on TCP 8000; DNS remains a separate scoped allowance. Terraform security checks require `docker_config { immutable_tags = true }` to prevent reliance on tag naming alone. GitHub Actions use read-only permissions and complete commit-SHA pins.

Secret scanning, image CVE scanning/signing, admission policy, and attestation verification remain production improvements. Findings and exceptions should identify severity, owner, justification, and expiry. Security decisions with lasting consequences belong in ADRs.

## Incident posture

Response documentation will cover containment, credential rotation, evidence preservation, rollback, communication, and follow-up actions before production readiness is claimed.
