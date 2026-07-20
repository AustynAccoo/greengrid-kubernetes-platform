# GCP IAM

Terraform creates `greengrid-gke-nodes`, a dedicated keyless IAM service account for nodes. It is distinct from Kubernetes ServiceAccounts and from application identities.

- `roles/container.defaultNodeServiceAccount` at project scope is Google's current minimum aggregate node role for normal GKE system operations, including required logging and monitoring behavior.
- `roles/artifactregistry.reader` is granted only on the GreenGrid repository so kubelet can pull `telemetry-api` and `telemetry-generator` images.

Owner, Editor, Compute Admin, service-account keys, public members, and workload API roles are absent. The node pool uses the `cloud-platform` OAuth scope as Google recommends for custom node accounts; IAM roles remain the authorization boundary.

The Terraform deployment principal itself is external to this code. A real team should use short-lived federation, separation of duties, a reviewed custom role or carefully selected predefined roles, and environment-specific identities. The principal attaching the node account must have Service Account User on that account, granted outside this module according to organizational ownership.

