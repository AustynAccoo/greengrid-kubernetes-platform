# Security

## Baseline controls

- Prevent secrets, tokens, credentials, and service-account keys from entering Git.
- Use Workload Identity for GCP access and dedicated Kubernetes ServiceAccounts.
- Run containers as non-root with read-only filesystems and dropped capabilities where compatible.
- Define CPU and memory requests and limits plus startup, readiness, and liveness probes.
- Begin with default-deny NetworkPolicies and allow only required flows.
- Grant minimal IAM, CI, GitOps, and runtime permissions.
- Tag images with Git commit SHAs, build once, and promote the same digest.
- Require validation, review, and documented approval for sensitive changes.

## Planned verification

CI will eventually include dependency, secret, container, IaC, chart, and policy scanning. Findings will be severity-gated with documented exceptions, owners, and expiry dates. Security decisions with lasting consequences belong in ADRs.

## Incident posture

Response documentation will cover containment, credential rotation, evidence preservation, rollback, communication, and follow-up actions before production readiness is claimed.

