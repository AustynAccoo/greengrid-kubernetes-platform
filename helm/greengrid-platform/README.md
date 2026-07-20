# GreenGrid Platform Helm Chart

This chart renders namespace-scoped GreenGrid workloads. It deliberately does not create a Namespace: namespace ownership, Pod Security Admission labels, lifecycle, and shared policy normally belong to the platform team. Use an explicit namespace such as `greengrid-dev`, `greengrid-staging`, or `greengrid-prod`, labeled to enforce the Kubernetes `restricted` Pod Security Standard before a real installation.

## Resources and controls

- Two Deployments run the API and generator with dedicated ServiceAccounts and token automount disabled. Pods and containers use non-root UID/GID 10001, RuntimeDefault seccomp, read-only root filesystems, no privilege escalation, no privileged mode, and all capabilities dropped. Host networking, host PID/IPC, and hostPath are absent.
- Two ConfigMaps hold only non-sensitive settings. Credentials never belong in values or ConfigMaps.
- A ClusterIP Service exposes the API only within the cluster.
- The API HPA scales on CPU utilization relative to the CPU request. Its bounds and stabilization differ by environment. The cluster must provide the metrics API; this chart does not install one.
- The API PodDisruptionBudget constrains voluntary evictions: development allows its single pod to move, staging keeps one available, and production keeps two. It does not prevent involuntary failures and can delay maintenance when spare capacity is unavailable.
- ResourceQuota limits aggregate namespace consumption. LimitRange supplies guardrails, while every workload container still declares explicit requests and limits.
- A Helm test calls API readiness through the ClusterIP Service.

## Probe design

API startup probes allow initialization before liveness begins. Readiness calls `/health/ready` to control Service endpoints, while liveness calls `/health/live` only to detect a stuck process. This separation avoids restarts for temporary readiness failures.

The generator has no HTTP listener. Its probes inspect a marker refreshed only after successful API delivery. Startup allows initial DNS/API convergence, readiness represents recent delivery, and liveness restarts a persistently stalled generator.

## Resources and autoscaling

Requests drive scheduling and form the denominator for CPU HPA utilization. Limits cap consumption; CPU may throttle and memory overage may terminate the container. Production values must ultimately come from observed load rather than estimates. The HPA owns the live API replica count within its bounds; `replicaCount` supplies the initial baseline.

## Network paths

Default-deny selects all pods for ingress and egress. DNS egress permits TCP/UDP 53 only to `k8s-app: kube-dns` pods in `kube-system`. Generator egress permits TCP 8000 only to API pods, with matching API ingress from generator and Helm-test pods. There is no general internet egress or external API ingress.

DNS labels and CNI behavior vary and must be verified. An ingress controller, service mesh, external data store, cloud API, or telemetry exporter would need additional narrowly scoped policy.

## Environment differences

| Setting | Development | Staging | Production |
| --- | ---: | ---: | ---: |
| API baseline replicas | 1 | 2 | 3 |
| API HPA range | 1–3 | 2–4 | 3–8 |
| API PDB minimum available | 0 | 1 | 2 |
| Generator replicas | 1 | 1 | 2 |
| Logging | debug | info | warning |
| Resources | small | production-like | strictest |

Render with base values plus one overlay. Replace both `git-000…000` placeholders with approved commit-SHA tags; never use `latest`.

```sh
helm lint helm/greengrid-platform -f helm/greengrid-platform/values-dev.yaml
helm template greengrid helm/greengrid-platform --namespace greengrid-dev -f helm/greengrid-platform/values-dev.yaml
```

`make helm-verify` lints, renders, attempts kubectl client-side dry-run, performs Helm's fully offline client dry-run, and checks the rendered security invariants for every environment. Kubectl may still require API discovery even in client mode; without a cluster, the Helm dry-run and rendered-manifest verifier provide the offline gates.

## Real production adjustments

Confirm cluster compatibility, registry access, Workload Identity annotations, topology spread, zone capacity, priority classes, metrics availability, HPA/PDB interaction, shared quotas, DNS labels, CNI semantics, admission controls, signed images, vulnerability policy, ingress and TLS, SLOs, alerting, rollout/rollback, and measured sizing. Staging and production changes require documented approval.
