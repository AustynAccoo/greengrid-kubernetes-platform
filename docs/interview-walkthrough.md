# Interview Walkthrough

## 90-second architecture answer

> GreenGrid is a GKE platform project I built to demonstrate the platform work around a small energy-telemetry service. Terraform owns the GCP foundation: required APIs, a custom VPC with secondary Pod and Service ranges, Artifact Registry, a keyless node identity, and a zonal Standard GKE cluster in `us-east4-b`. I chose Standard GKE so I could work directly with node pools, upgrades, networking, and identity.
>
> Helm owns the Kubernetes layer. It deploys a telemetry generator and FastAPI service using dedicated ServiceAccounts, non-root read-only containers, requests and limits, three probe types, an HPA, environment-aware PDBs, quotas, and default-deny NetworkPolicies. The generator reaches the API only through an internal ClusterIP Service; there is no public application ingress.
>
> For operations, workloads emit structured logs and the API exposes Prometheus metrics. GKE managed collection scrapes those metrics through a `PodMonitoring` resource, with a narrow NetworkPolicy for the collector. GitHub Actions independently validates the application and dependencies, rendered Helm policy, Terraform, and the running container contract. I keep the scope honest: development has been exercised, while staging/production values and Argo CD are designs, not live production claims.

## Five-minute walkthrough order

1. **Start with the boundary:** the Python workload is deliberately small; the point is secure, repeatable platform delivery.
2. **Follow a change:** pull request → four CI gates → immutable Git-SHA image → registry → reviewed infrastructure/release step.
3. **Explain infrastructure ownership:** Terraform owns cloud lifecycle; Helm owns namespace-scoped workload lifecycle.
4. **Follow runtime traffic:** generator → Kubernetes DNS → ClusterIP → API pod → bounded in-memory store.
5. **Show defense in depth:** keyless identity, dedicated ServiceAccounts, restricted containers, quota/resources, probes, and default deny.
6. **Show operations:** JSON logs, HPA/resource metrics, `PodMonitoring`, PromQL, rollout and Helm-test evidence.
7. **Close with tradeoffs:** zonal/public-node development saves portfolio cost; production needs regional private nodes, controlled egress, durable storage, authenticated ingress, SLOs, and recovery testing.

## Problem story 1: default deny blocked DNS

**Situation:** After applying default-deny egress, the generator restarted and telemetry stopped arriving.

**How to say it:**

> I began with the symptom but did not assume the API was down. I checked Pod events, generator logs, the Service and endpoints, and then name resolution. The Service had a ready API endpoint, while the generator could not resolve its Kubernetes DNS name. That isolated the failure to the network path. Default deny was working exactly as configured, but I had omitted DNS egress. I added a narrow rule for TCP and UDP 53 to `kube-dns` in `kube-system`, kept general egress denied, and then verified name resolution plus successful `201` telemetry deliveries. I also strengthened the rendered-manifest test so DNS and application egress are separate, exact contracts.

**What it proves:** layered troubleshooting, understanding of Kubernetes discovery, and security that remains least privilege after the fix.

## Problem story 2: dependency security drift

**Situation:** The service tests passed, but its 2025 pins had accumulated 2026 advisories.

**How to say it:**

> I treated passing unit tests and dependency safety as different controls. I ran an OSV-backed dependency audit and found the old Starlette resolution and Pytest pin were no longer acceptable. I upgraded FastAPI, Starlette, Pydantic, Uvicorn, Pytest, Ruff, and the digest-pinned Python base. Then I reran the API, retry, retention, metrics, and bounded-load contracts. The audit returned no known vulnerabilities. Finally, I added that audit to CI and Dependabot so this becomes continuous evidence instead of a one-time cleanup.

**What it proves:** supply-chain awareness, safe upgrades, validation discipline, and prevention after remediation.

## Problem story 3: metrics endpoint without an ingestion path

**Situation:** The API had `/metrics`, but Terraform explicitly disabled managed Prometheus and Helm had no scrape resource.

**How to say it:**

> I traced observability end to end rather than checking a box for a metrics endpoint. I enabled GKE managed collection in Terraform, added the metrics-writer role to the custom node identity, created a namespaced `PodMonitoring` object, and added sample and label limits. Because the workloads use default-deny ingress, I also added a rule that admits TCP 8000 only from collector pods in the Standard GKE `gmp-system` namespace. The Helm policy test now asserts the selector, port, path, interval, limits, and exact network peer. That turns metrics from dead code into a verifiable collection path.

**What it proves:** systems thinking across application, Kubernetes CRDs, IAM, networking, and cost controls.

## Problem story 4: documentation got ahead of implementation

**Situation:** The README described CI and GitOps as planned architecture, but no workflow or Argo CD desired state existed.

**How to say it:**

> I audited claims against repository evidence. I implemented the missing CI gates, then rewrote the status and architecture documentation to distinguish what had been deployed, what was code-complete but still needed an approved update, and what remained future work. I kept Argo CD in the roadmap instead of presenting GitOps as live. That matters because senior engineers should communicate operational truth, not just ideal architecture.

**What it proves:** ownership, honest risk communication, and the ability to close control gaps.

## Likely follow-ups

### Why Terraform and Helm instead of one tool?

Terraform is responsible for long-lived cloud resources with stateful lifecycle and plan review. Helm packages Kubernetes objects that change with the application and vary by environment. Keeping the boundary explicit reduces state coupling and lets each layer use the right validation and rollback model.

### Why Workload Identity if the application has no GCP role?

The cluster is ready for keyless workload identity, but neither service currently calls a Google API, so granting an application role would violate least privilege. Dedicated Kubernetes ServiceAccounts exist now; I would add a dedicated Google identity and the narrowest role only when a concrete API requirement appears.

### What does the HPA depend on?

The HPA target is CPU utilization as a percentage of the API container's CPU request. That is why requests are mandatory. GKE provides the resource metrics path; custom Prometheus metrics are for service insight, not the current scaling decision.

### Can the PDB guarantee availability?

No. It constrains voluntary disruptions only. It cannot prevent a node crash, zone failure, or application defect. In development, `minAvailable: 0` lets a single replica drain; staging and production values pair higher replica floors with `minAvailable: 1` and `2`.

### What would you do next?

Add request/error/latency metrics and one SLO-backed alert, run and record an HPA drill plus a failed-rollout/rollback drill, then implement keyless GitHub-to-GCP delivery and Argo CD only if the interview timeline justifies it.

## Claims to avoid

- Do not call staging or production live.
- Do not say Argo CD currently reconciles this repository.
- Do not describe the in-memory API as durable or horizontally consistent.
- Do not call a zonal public-node cluster production-ready.
- Do not present the project as prior employer production work; describe it as hands-on portfolio implementation.
