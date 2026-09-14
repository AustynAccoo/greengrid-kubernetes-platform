# GKE Troubleshooting Runbook

## Purpose

Use this runbook to diagnose GreenGrid failures aloud and to capture evidence during controlled interview drills. Start broad, isolate the failed layer, test one hypothesis at a time, and verify both recovery and the retained security posture.

## First five minutes

Set the intended context explicitly before issuing commands:

```sh
kubectl config current-context
kubectl cluster-info
kubectl get namespace greengrid-dev --show-labels
kubectl -n greengrid-dev get deploy,pods,svc,endpoints,hpa,pdb,networkpolicy,podmonitoring
kubectl -n greengrid-dev get events --sort-by=.metadata.creationTimestamp
```

Answer these questions in order:

1. Am I operating against the intended project, cluster, and namespace?
2. Is desired state present, and did a rollout or configuration change just occur?
3. Are Pods scheduled, running, ready, and stable?
4. Does the Service have ready endpoints?
5. Is the failure application, resource, identity, DNS, network, or observability specific?

Do not begin by deleting Pods. A restart can erase the most useful evidence and does not fix a bad desired state.

## Scenario 1: generator is restarting and telemetry is missing

```sh
kubectl -n greengrid-dev get pods -l app.kubernetes.io/component=telemetry-generator -o wide
kubectl -n greengrid-dev describe pod -l app.kubernetes.io/component=telemetry-generator
kubectl -n greengrid-dev logs -l app.kubernetes.io/component=telemetry-generator --previous --tail=100
kubectl -n greengrid-dev get service,endpoints -l app.kubernetes.io/component=telemetry-api
kubectl -n greengrid-dev get networkpolicy -o yaml
```

Interpretation:

| Evidence | Likely layer | Next check |
| --- | --- | --- |
| `Name or service not known`, DNS timeout | DNS / egress policy | DNS policy selects generator and targets actual kube-dns labels on TCP/UDP 53 |
| Connection refused with a resolved IP | API listener/readiness | API logs, ports, probes, and endpoint readiness |
| HTTP 5xx followed by retries | API/server path | API exception logs and resource health |
| HTTP 4xx with no retries | Payload/contract | Validation response and generator payload |
| Health marker older than 30 seconds | Delivery path | Work backward from generator logs to DNS, Service, endpoint, API |

Recovery is complete only when the generator stays Ready, restart count stops increasing, and logs show repeated successful `201` deliveries. Recheck that no broad internet egress was added.

## Scenario 2: API rollout is stuck

```sh
kubectl -n greengrid-dev rollout status deployment --all --timeout=3m
kubectl -n greengrid-dev get replicaset,pods -l app.kubernetes.io/component=telemetry-api
kubectl -n greengrid-dev describe pod -l app.kubernetes.io/component=telemetry-api
kubectl -n greengrid-dev logs -l app.kubernetes.io/component=telemetry-api --all-containers --tail=100
helm history greengrid --namespace greengrid-dev
```

Separate common causes:

- `ImagePullBackOff`: image path/tag, registry existence, node identity, or repository IAM.
- `CreateContainerConfigError`: missing ConfigMap or invalid reference.
- Startup/liveness failures: process/listener failure, wrong path/port, or resource starvation.
- Running but unready: readiness semantics or dependency state; do not weaken liveness to mask it.
- Pending: quota, requests, taints, affinity, or node capacity.

If the release is harmful and the prior revision is known good, use a reviewed `helm rollback`, then repeat Service, endpoints, test, logs, and telemetry checks. Preserve the failed manifest and events for follow-up.

## Scenario 3: HPA does not scale

```sh
kubectl -n greengrid-dev get hpa --watch
kubectl -n greengrid-dev describe hpa
kubectl -n greengrid-dev top pods -l app.kubernetes.io/component=telemetry-api
kubectl -n greengrid-dev get deployment -l app.kubernetes.io/component=telemetry-api -o yaml
```

Check in this order:

1. HPA has a current CPU value rather than `<unknown>`.
2. API containers have CPU requests; utilization is calculated against them.
3. Load reaches the API and lasts long enough to cross collection/reconciliation windows.
4. Desired replicas are below `maxReplicas` and namespace quota permits new Pods.
5. Nodes have capacity or cluster autoscaler can add a node within the configured maximum.
6. New Pods pass startup/readiness; an HPA can request replicas that never become usable.

Scale-down is intentionally slower because of its stabilization window. Do not interpret that delay as a broken HPA.

## Scenario 4: Prometheus metrics are absent

```sh
kubectl -n greengrid-dev get podmonitoring -o yaml
kubectl -n greengrid-dev describe podmonitoring
kubectl -n greengrid-dev get pods -l app.kubernetes.io/component=telemetry-api --show-labels
kubectl -n gmp-system get pods -l app.kubernetes.io/name=collector -o wide
kubectl -n gmp-system logs -l app.kubernetes.io/name=collector -c prometheus --tail=100
kubectl -n greengrid-dev get networkpolicy -o yaml
```

Test the endpoint from inside an API Pod without introducing a new network path:

```sh
kubectl -n greengrid-dev exec deployment/greengrid-greengrid-platform-telemetry-api -- \
  python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/metrics').read().decode())"
```

If the endpoint works, validate selector labels, named port, collector namespace/labels, policy, and `PodMonitoring` status. Query `up` in Cloud Monitoring Metrics Explorer. If `up` exists there, ingestion works and the remaining problem is query-side access or configuration.

## Scenario 5: Pod is Pending

```sh
kubectl -n greengrid-dev describe pod <pod-name>
kubectl -n greengrid-dev describe resourcequota
kubectl -n greengrid-dev get limitrange -o yaml
kubectl get nodes
kubectl describe node <node-name>
```

Use scheduler events as evidence. Compare requested CPU/memory with allocatable capacity, namespace quota, node-pool maximums, and system workload overhead. Lowering requests just to make scheduling pass can invalidate the HPA denominator and hide capacity risk; change sizing only with measured justification.

## Evidence to capture after every drill

- Trigger and timestamp.
- User-visible and platform symptoms.
- Last known-good version and recent change.
- Commands and decisive evidence, excluding secrets.
- Root cause and rejected hypotheses.
- Recovery action and rollback decision.
- Verification of service behavior and security controls.
- Preventive test, alert, documentation, or policy change.
