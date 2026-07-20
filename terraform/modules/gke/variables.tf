variable "project_id" {
  description = "GCP project ID."
  type        = string
}
variable "location" {
  description = "Zonal location for the development control plane and nodes."
  type        = string
}
variable "cluster_name" {
  description = "GKE cluster name."
  type        = string
}
variable "network_id" {
  description = "Custom VPC resource ID."
  type        = string
}
variable "subnet_id" {
  description = "GKE subnet resource ID."
  type        = string
}
variable "pods_secondary_range_name" {
  description = "Pod secondary range name."
  type        = string
}
variable "services_secondary_range_name" {
  description = "Service secondary range name."
  type        = string
}
variable "node_service_account_email" {
  description = "Dedicated node service account email."
  type        = string
}
variable "node_machine_type" {
  description = "Machine type for development nodes."
  type        = string
}
variable "node_min_count" {
  description = "Minimum nodes in the zonal pool."
  type        = number
}
variable "node_max_count" {
  description = "Maximum nodes in the zonal pool."
  type        = number
}
variable "node_disk_type" {
  description = "Persistent disk type for nodes."
  type        = string
  default     = "pd-balanced"
}
variable "node_disk_size_gb" {
  description = "Boot disk size in GiB."
  type        = number
  default     = 50
}
variable "deletion_protection" {
  description = "Protect the cluster from Terraform deletion."
  type        = bool
}
variable "labels" {
  description = "Resource labels."
  type        = map(string)
  default     = {}
}
