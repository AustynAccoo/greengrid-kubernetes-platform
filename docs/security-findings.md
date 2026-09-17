# Security findings and preventive controls

This register records the six previously identified gaps and the fixes present in the repository. Evidence links point to implementation or the documented incident history, not fresh cloud observations. No GCP or Kubernetes verification was performed for this change. “Resolved in code” does not mean an approved infrastructure or Helm update has been deployed.

Project risk ratings (Low, Medium, High, or Critical) express remediation priority for the documented GreenGrid project scope before the fix. They are qualitative project judgments, not CVSS scores, advisory severity labels, or claims of demonstrated exploitation. Where repository history shows a configuration gap but does not record the original discovery procedure, the detection method explicitly states that limitation.

## DNS under default-deny

- **Finding ID:** GG-SEC-001
- **Project risk rating:** Medium
- **Detection method:** Historical runtime troubleshooting notes record the investigation: generator restarts and missing telemetry led to checks of Pod events, logs, Service endpoints, and DNS resolution.
- **Risk rating rationale:** The documented failure interrupted the project’s telemetry path, but the evidence describes a development availability problem, not data compromise or a production incident.
- **Risk:** Blocking DNS prevents the generator from finding the API, interrupting telemetry and causing restarts.
- **Evidence:** Historical incident notes record a ready API Service endpoint while the generator could not resolve the Service name. After the scoped DNS allowance, name resolution and successful `201` telemetry deliveries were reported. The [network policies](../helm/greengrid-platform/templates/networkpolicies.yaml) contain that allowance. These are historical observations, not fresh runtime verification.
- **Resolution:** Allow TCP/UDP 53 to `k8s-app=kube-dns` pods in `kube-system`, retaining default-deny ingress and egress.
- **Preventive CI control:** `make helm-verify` invokes [the Helm verifier](../scripts/verify_helm_security.py) to check DNS peers and ports in every environment.
- **Status:** Resolved in code; historical runtime recovery is documented. No new live validation claimed.

## Helm-test egress

- **Finding ID:** GG-SEC-002
- **Project risk rating:** Medium
- **Detection method:** Pre-deployment chart-policy inspection identifies API ingress without matching Helm-test egress under default deny; the correction is recorded in commit `8f6f364`. The repository does not preserve a separate original detection log or a live failed Helm-test result.
- **Risk rating rationale:** The gap undermined release verification through the Service path; the evidence does not establish an application outage or unauthorized access.
- **Risk:** The readiness test cannot reach the API despite permitted API ingress, producing a misleading failed release check.
- **Evidence:** [The chart policy](../helm/greengrid-platform/templates/networkpolicies.yaml) now includes `helm-test-to-api`; ingress alone does not grant test-pod egress.
- **Resolution:** Permit Helm-test pods to reach only same-namespace, same-release telemetry API pods on TCP 8000. DNS uses the separate scoped policy.
- **Preventive CI control:** [The Helm verifier](../scripts/verify_helm_security.py) requires the exact test egress specification and 19 rendered resources per environment.
- **Status:** Resolved in code; live Helm-test success requires an approved deployment and verification.

## Dependency vulnerabilities

- **Finding ID:** GG-SEC-003
- **Project risk rating:** High
- **Detection method:** Historical dependency remediation notes record an OSV-backed dependency audit identifying the old Starlette resolution and Pytest pin despite passing application tests.
- **Risk rating rationale:** Known advisories affected both runtime and development dependencies, warranting prompt project remediation. The repository evidence does not establish specific exploitability, compromise, or a CVSS score.
- **Risk:** Vulnerable runtime or development dependencies can expose application and build environments even when unit tests pass.
- **Evidence:** Historical remediation notes identify the old Starlette/Pytest stack and report a clean audit after upgrades and repeated application checks. The [development requirements](../requirements-dev.txt) and [API requirements](../applications/telemetry-api/requirements.txt) contain the replacement pins. Historical audit results are not a current clean bill of health.
- **Resolution:** Upgrade the affected dependency stack and digest-pinned Python base, retaining application contract tests.
- **Preventive CI control:** `make dependency-audit` runs pip-audit; application tests check behavior; [Dependabot](../.github/dependabot.yml) proposes updates. The container job now configures Trivy scans of both local images for fixable CRITICAL OS/library vulnerabilities.
- **Status:** Earlier findings remediated in repository pins; fresh audit and image-scan results remain required. Lower-severity and unfixed image vulnerabilities do not fail this Trivy gate.

## Missing metrics collection

- **Finding ID:** GG-SEC-004
- **Project risk rating:** Medium
- **Detection method:** Historical implementation notes describe tracing the metrics path from the API endpoint through Terraform and Helm, finding managed Prometheus disabled and no scrape resource.
- **Risk rating rationale:** The missing ingestion path reduced operational visibility and fault detection; it did not itself establish an outage or compromise, and no production monitoring claim is made.
- **Risk:** A working `/metrics` endpoint without ingestion leaves operational failures unobserved.
- **Evidence:** Historical implementation notes record that `/metrics` existed while managed collection was disabled and no scrape resource was configured. The [GKE module](../terraform/modules/gke/main.tf), [node IAM](../terraform/modules/iam/main.tf), and [PodMonitoring](../helm/greengrid-platform/templates/podmonitoring-api.yaml) contain the collection configuration added to address that gap.
- **Resolution:** Enable managed Prometheus, grant the node identity `roles/monitoring.metricWriter`, configure scraping with limits, and admit only scoped managed-collector ingress.
- **Preventive CI control:** [Terraform security checks](../scripts/verify_terraform_security.py) require collection and IAM configuration; Helm assertions require the scrape contract and collector ingress.
- **Status:** Resolved in code; actual ingestion requires separately approved deployment and metric-query evidence. Static checks do not prove live ingestion.

## Mutable registry tags

- **Finding ID:** GG-SEC-005
- **Project risk rating:** High
- **Detection method:** Terraform source inspection identifies the absence of registry immutability enforcement despite Git-SHA naming; commit `8f6f364` adds `immutable_tags = true`. The repository does not record an original registry overwrite test or cloud observation.
- **Risk rating rationale:** Artifact identity underpins the documented build-once promotion and rollback process, so missing enforcement is a high-priority integrity gap. This does not imply that any tag was overwritten or that an unauthorized actor had write access.
- **Risk:** A Git-SHA-shaped tag could be reassigned to different content, undermining build-once promotion and rollback traceability.
- **Evidence:** [Artifact Registry configuration](../terraform/modules/artifact-registry/main.tf) now declares `docker_config { immutable_tags = true }`; naming conventions alone did not enforce immutability.
- **Resolution:** Configure registry-enforced immutable Docker tags and promote the same built digest across environments.
- **Preventive CI control:** [Terraform security checks](../scripts/verify_terraform_security.py) require immutable tags; Helm checks require Git-SHA application image tags. CI does not yet enforce cross-environment digest promotion.
- **Status:** Resolved in code; registry enforcement takes effect after an approved Terraform update. No live enforcement claim.

## Dev-only load generation

- **Finding ID:** GG-SEC-006
- **Project risk rating:** Medium
- **Detection method:** API source and environment-control review identifies unconditional `/simulate-load` registration in the parent of commit `8f6f364`; that commit adds explicit enablement and disabled-by-default tests. The repository does not record the original reviewer’s procedure or a load-abuse incident.
- **Risk rating rationale:** Deliberate CPU work can compete with telemetry processing, but the documented request bound and internal-only API limit the supported project impact. No public exposure, exploitation, or production disruption is asserted.
- **Risk:** An exposed CPU-load endpoint can waste capacity or disrupt normal telemetry processing.
- **Evidence:** [API route registration](../applications/telemetry-api/src/telemetry_api/main.py), [API tests](../tests/test_telemetry_api.py), and environment values restrict `/simulate-load`. This finding concerns the load-simulation endpoint, not the normal synthetic telemetry generator.
- **Resolution:** Disable the endpoint by default, enable it only in the dev overlay, and bound request duration to five seconds.
- **Preventive CI control:** Application tests check disabled-route behavior and duration bounds; Helm verification requires load simulation enabled in dev and disabled in staging/production.
- **Status:** Resolved in code; rendered configuration is checked, but unauthorized live configuration drift is not detected by this CI.

## Immediate next control: TruffleHog OSS

Secret scanning is not implemented in this workflow. Add it only after validating explicit PR base/head and push before/after ranges, with a full commit-SHA action pin, `contents: read`, and checkout credentials disabled. Fetch enough history to resolve both endpoints. Test normal and fork PRs, multi-commit pushes, force pushes, and all-zero or missing push endpoints; define a safe explicit fallback or fail rather than silently skipping a range. Validate with synthetic secret fixtures and do not print real secrets. This change does not claim that range handling has been tested or that the repository is secret-free.

The current environment lacks a TruffleHog executable, so reliable range and detection validation has not been established. See [the security roadmap](security.md#production-security-roadmap) for the remaining controls.
