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

The container CI job now configures the [official Trivy Action](https://github.com/aquasecurity/trivy-action/tree/ed142fd0673e97e23eac54620cfb913e5ce36c25) for both locally built images with a full commit-SHA pin. It scans OS/library vulnerabilities, fails on CRITICAL findings with fixes, and ignores unfixed findings. It uses Docker-local images and table output, with no registry publication or security-event write permission. Both scans are attempted after a successful runtime check, even if the first scan fails. Successful execution must be confirmed by CI; this is not an image-signing or admission control.

Secret scanning, image signing, admission policy, and attestation verification remain production improvements. Findings and exceptions should identify severity, owner, justification, and expiry. Security decisions with lasting consequences belong in ADRs.

## Incident posture

Response documentation will cover containment, credential rotation, evidence preservation, rollback, communication, and follow-up actions before production readiness is claimed.

## Production security roadmap

These controls are planned, not implemented by this change:

1. **TruffleHog OSS:** the immediate next control, contingent on validated explicit PR and push commit ranges, full SHA pinning, read-only permissions, and synthetic detection tests. See [the findings register](security-findings.md#immediate-next-control-trufflehog-oss).
2. **GitHub-to-GCP Workload Identity Federation:** use short-lived federation for a separate approved delivery workflow, constrained to trusted repository/ref/environment identities with minimal roles. This is distinct from existing GKE workload identity. Any future `id-token: write` belongs only in that delivery job, not current validation jobs.
3. **Artifact Analysis:** establish registry-side vulnerability evidence and a documented severity/exception policy for promoted image digests, complementing local CI scanning.
4. **Binary Authorization:** introduce tested admission policy and trusted attestations tied to approved image digests; rehearse rollback and emergency exceptions before enforcement.
5. **SCC/GKE security posture review:** review Security Command Center and GKE posture findings, assign owners and remediation deadlines, and retain evidence. Do not assume configuration checks prove the running cluster is compliant.

Track specific remediations and current evidence in [security findings](security-findings.md). No cloud resources or permissions are changed by this workflow update.
