variable "project_id" {
  description = "GCP project ID."
  type        = string
}
variable "service_account_id" {
  description = "Account ID for the dedicated GKE node service account."
  type        = string
  default     = "greengrid-gke-nodes"
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.service_account_id))
    error_message = "service_account_id must be 6-30 lowercase characters."
  }
}
variable "artifact_registry_location" {
  description = "Location of the Artifact Registry repository."
  type        = string
}
variable "artifact_registry_repository" {
  description = "Repository ID from which nodes pull images."
  type        = string
}

