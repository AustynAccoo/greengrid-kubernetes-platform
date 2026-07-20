variable "project_id" {
  description = "GCP project ID."
  type        = string
}
variable "region" {
  description = "Region for the subnet."
  type        = string
}
variable "network_name" {
  description = "Custom VPC name."
  type        = string
}
variable "subnet_name" {
  description = "GKE subnet name."
  type        = string
}
variable "subnet_cidr" {
  description = "Primary node CIDR."
  type        = string
  validation {
    condition     = can(cidrhost(var.subnet_cidr, 0))
    error_message = "subnet_cidr must be valid CIDR notation."
  }
}
variable "pods_secondary_range_name" {
  description = "Name of the Pod secondary range."
  type        = string
}
variable "pods_secondary_cidr" {
  description = "Secondary CIDR for Pods."
  type        = string
  validation {
    condition     = can(cidrhost(var.pods_secondary_cidr, 0))
    error_message = "pods_secondary_cidr must be valid CIDR notation."
  }
}
variable "services_secondary_range_name" {
  description = "Name of the Service secondary range."
  type        = string
}
variable "services_secondary_cidr" {
  description = "Secondary CIDR for Services."
  type        = string
  validation {
    condition     = can(cidrhost(var.services_secondary_cidr, 0))
    error_message = "services_secondary_cidr must be valid CIDR notation."
  }
}
