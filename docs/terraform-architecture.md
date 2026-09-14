# Terraform Architecture

The deployable development root composes five reusable modules:

```text
project-services
  ├── network
  ├── artifact-registry ── iam
  └──────────────────────── gke
network ─────────────────── gke
iam ─────────────────────── gke
```

`project-services` enables only required APIs. `network` creates VPC-native address space. `artifact-registry` stores the two service images. `iam` creates the node identity, repository pull grant, and metrics-writer permission. `gke` consumes those outputs to create a zonal cluster and separate node pool with managed Prometheus collection enabled. Explicit dependencies ensure APIs exist before dependent resources are planned for creation.

The development root owns persistent infrastructure. Helm remains responsible for Kubernetes workloads; Terraform does not create Kubernetes resources. Staging and production reuse module contracts but require independent roots, state, identities, projects, review, and approval.

Rollback normally means reverting reviewed Terraform configuration and inspecting a new plan. Infrastructure changes are not assumed reversible: network ranges, cluster topology, deletion protection, and destructive replacements require migration plans. Cleanup requires a reviewed destroy plan and explicit approval; no destroy target is included in the Makefile.

## Expected pre-deployment plan

The anticipated live development plan is **1 addition, 2 in-place updates, zero replacements, and zero deletions**: add `roles/monitoring.metricWriter` to the node identity, enable GKE managed Prometheus in place, and enable Artifact Registry `docker_config.immutable_tags = true` in place. This is an expectation, not a live plan result; confirm it with a separately authorized plan before requesting apply approval.
