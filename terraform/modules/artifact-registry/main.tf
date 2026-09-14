resource "google_artifact_registry_repository" "this" {
  project       = var.project_id
  location      = var.region
  repository_id = var.repository_id
  description   = "Immutable GreenGrid telemetry service container images"
  format        = "DOCKER"
  labels        = var.labels

  docker_config {
    immutable_tags = true
  }
}

