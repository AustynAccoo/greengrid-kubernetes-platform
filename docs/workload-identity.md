# Workload Identity

The cluster configures the workload pool as `<PROJECT_ID>.svc.id.goog`, and the node pool uses `GKE_METADATA`. Static Google service-account keys are prohibited.

```text
Kubernetes ServiceAccount
        ↓
GKE Workload Identity
        ↓
Google Service Account
        ↓
Least-privilege GCP API access
```

The Helm chart already creates dedicated Kubernetes ServiceAccounts for each workload. Neither telemetry service currently needs a Google API, so Terraform creates no application Google service account and grants no workload permissions. When a concrete requirement appears, add a dedicated Google identity, narrow role, IAM principal binding, and Helm annotation or direct principal grant. Test the mapping in development and staging before production.

GKE managed Prometheus collection is a node-level platform function, not an application permission. Its collector uses the custom node identity, which has `roles/monitoring.metricWriter`; the telemetry Kubernetes ServiceAccounts still have no Google Cloud IAM role.

Separate environment projects produce separate workload pools, reducing identity-sameness risk. Never map the default Kubernetes ServiceAccount or mount a JSON key.
