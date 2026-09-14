locals {
  node_project_roles = toset([
    "roles/container.defaultNodeServiceAccount",
    "roles/monitoring.metricWriter",
  ])
}

resource "google_service_account" "gke_nodes" {
  project      = var.project_id
  account_id   = var.service_account_id
  display_name = "GreenGrid GKE node service account"
  description  = "Least-privilege identity for GreenGrid GKE node system operations; no keys are created."
}

resource "google_project_iam_member" "gke_nodes" {
  for_each = local.node_project_roles

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.gke_nodes.email}"
}

resource "google_artifact_registry_repository_iam_member" "reader" {
  project    = var.project_id
  location   = var.artifact_registry_location
  repository = var.artifact_registry_repository
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.gke_nodes.email}"
}
