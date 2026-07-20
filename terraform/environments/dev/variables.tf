variable "project_id" {
  description = "GCP project ID. Must be supplied explicitly and must not be a credential."
  type        = string
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "project_id must be a valid GCP project ID."
  }
}
variable "region" {
  description = "GCP region for regional resources."
  type        = string
  default     = "us-east4"
  validation {
    condition     = var.region == "us-east4"
    error_message = "This development foundation is intentionally constrained to us-east4."
  }
}
variable "environment" {
  description = "Environment identifier. Only dev is deployable in this root."
  type        = string
  default     = "dev"
  validation {
    condition     = var.environment == "dev"
    error_message = "terraform/environments/dev only accepts environment=dev."
  }
}
variable "cluster_name" {
  description = "Development GKE cluster name."
  type        = string
  default     = "greengrid-dev"
}
variable "network_name" {
  description = "Development custom VPC name."
  type        = string
  default     = "greengrid-dev-vpc"
}
variable "subnet_name" {
  description = "Development GKE subnet name."
  type        = string
  default     = "greengrid-dev-gke"
}
variable "subnet_cidr" {
  description = "Primary node CIDR."
  type        = string
  default     = "10.80.0.0/20"
  validation {
    condition     = can(cidrhost(var.subnet_cidr, 0))
    error_message = "subnet_cidr must be valid CIDR notation."
  }
}
variable "pods_secondary_range_name" {
  description = "Pod secondary range name."
  type        = string
  default     = "greengrid-dev-pods"
}
variable "pods_secondary_cidr" {
  description = "Pod secondary CIDR."
  type        = string
  default     = "10.84.0.0/14"
  validation {
    condition     = can(cidrhost(var.pods_secondary_cidr, 0))
    error_message = "pods_secondary_cidr must be valid CIDR notation."
  }
}
variable "services_secondary_range_name" {
  description = "Service secondary range name."
  type        = string
  default     = "greengrid-dev-services"
}
variable "services_secondary_cidr" {
  description = "Service secondary CIDR."
  type        = string
  default     = "10.88.0.0/20"
  validation {
    condition     = can(cidrhost(var.services_secondary_cidr, 0))
    error_message = "services_secondary_cidr must be valid CIDR notation."
  }
}
variable "artifact_registry_repository" {
  description = "Docker Artifact Registry repository ID."
  type        = string
  default     = "greengrid"
}
variable "node_machine_type" {
  description = "Cost-conscious but usable node machine type."
  type        = string
  default     = "e2-standard-2"
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]+$", var.node_machine_type))
    error_message = "node_machine_type must be a valid machine type name."
  }
}
variable "node_min_count" {
  description = "Minimum development nodes."
  type        = number
  default     = 1
  validation {
    condition     = var.node_min_count >= 1 && var.node_min_count <= 3
    error_message = "node_min_count must be between 1 and 3."
  }
}
variable "node_max_count" {
  description = "Maximum development nodes."
  type        = number
  default     = 3
  validation {
    condition     = var.node_max_count >= var.node_min_count && var.node_max_count <= 5
    error_message = "node_max_count must be at least node_min_count and no more than 5."
  }
}
variable "deletion_protection" {
  description = "Whether Terraform protects the development cluster from deletion."
  type        = bool
  default     = false
}
variable "labels" {
  description = "Additional label-safe resource labels."
  type        = map(string)
  default     = {}
  validation {
    condition     = alltrue([for key, value in var.labels : can(regex("^[a-z][a-z0-9_-]{0,62}$", key)) && can(regex("^[a-z0-9_-]{0,63}$", value))])
    error_message = "Label keys and values must use lowercase GCP label-safe characters."
  }
}
