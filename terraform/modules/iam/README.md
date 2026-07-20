# IAM

Creates a keyless, dedicated node service account. `roles/container.defaultNodeServiceAccount` is Google's minimum aggregate role for GKE node system operations, including required logging and monitoring behavior. `roles/artifactregistry.reader` is scoped to the GreenGrid repository so nodes can pull private images. Owner, Editor, key resources, and workload API permissions are intentionally absent.

