# Observability

## Implemented signals

GKE sends system metrics and system/workload logs to Google Cloud. Managed Service for Prometheus is enabled in Terraform, and Helm creates one namespaced `PodMonitoring` resource for the telemetry API.

The API exposes:

| Metric | Type | Meaning |
| --- | --- | --- |
| `greengrid_telemetry_records` | Gauge | Records currently retained by one API pod |
| `greengrid_telemetry_submissions_total` | Counter | Records accepted by one API pod since process start |

Scrapes target the named `http` container port and `/metrics` path every 30 seconds with a 10-second timeout. Sample and label limits protect against accidental cardinality or ingestion growth. The default metadata labels preserve pod, container, and controller identity.

Managed collectors run as a DaemonSet and scrape targets on the same node. The chart's default-deny posture therefore includes an explicit ingress rule from `app.kubernetes.io/name=collector` pods in `gmp-system` to API TCP 8000. The custom node service account has `roles/monitoring.metricWriter` so collectors can push samples without a static key.

Google documents the managed-collection and `PodMonitoring` model in [Get started with managed collection](https://cloud.google.com/stackdriver/docs/managed-prometheus/setup-managed).

## Useful PromQL

```promql
up{job=~".*telemetry-api.*"}
```

```promql
sum(greengrid_telemetry_records)
```

```promql
sum(rate(greengrid_telemetry_submissions_total[5m]))
```

The counter must be queried with `rate` or `increase` for operational trends. A reset after a Pod restart is normal. The retained-record gauge is per pod because storage is intentionally local memory; summing it is useful for the demo but is not a durable system-of-record count.

## HPA demonstration

The API HPA scales on GKE resource CPU metrics, not the custom application metrics above. Requests provide the HPA utilization denominator. The bounded `/simulate-load` route can create observable CPU pressure without an unbounded stress endpoint. It is disabled by default and in staging/production values; only development explicitly registers it.

```sh
kubectl -n greengrid-dev get hpa --watch
kubectl -n greengrid-dev top pods
kubectl -n greengrid-dev get pods --watch
```

Generate multiple bounded requests from an authorized in-cluster test client, then correlate requested load, Pod CPU, desired replicas, new Pod readiness, and scale-down stabilization. Do not expect immediate scale-down: the chart intentionally uses a five-minute development stabilization window.

## Verification and troubleshooting

```sh
kubectl -n greengrid-dev get podmonitoring
kubectl -n greengrid-dev describe podmonitoring
kubectl -n gmp-system get pods -l app.kubernetes.io/name=collector -o wide
kubectl -n gmp-system logs -l app.kubernetes.io/name=collector -c prometheus --tail=100
```

If the `up` query has no series, separate discovery/scrape failure from query failure:

1. Confirm the API Pod labels match the `PodMonitoring` selector.
2. Confirm `/metrics` responds inside the API Pod and emits `# TYPE` lines.
3. Confirm the named `http` port maps to container port 8000.
4. Confirm collector and API Pods share nodes as expected and the monitoring NetworkPolicy matches actual collector labels/namespace.
5. Inspect `PodMonitoring` status and collector logs.
6. Query `up` in Cloud Monitoring Metrics Explorer; if it is present there, investigate the external query client rather than ingestion.

Target-status reporting is intended for acute diagnosis and should not be left enabled without considering operator resource use. See [Google's Managed Service for Prometheus troubleshooting guide](https://cloud.google.com/stackdriver/docs/managed-prometheus/troubleshooting).

## Deliberate boundary

Dashboards, notification channels, and production alert policies are not yet claimed as implemented. The next reliability increment should add an availability/error signal, a documented SLO, one actionable alert with a runbook, and a controlled alert test.
