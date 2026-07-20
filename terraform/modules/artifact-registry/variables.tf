variable "project_id" {
  description = "GCP project ID."
  type        = string
}
variable "region" {
  description = "Artifact Registry region."
  type        = string
}
variable "repository_id" {
  description = "Docker repository identifier."
  type        = string
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,62}$", var.repository_id))
    error_message = "repository_id must be a lowercase, label-safe identifier."
  }
}
variable "labels" {
  description = "Labels for ownership and cost attribution."
  type        = map(string)
  default     = {}
}

