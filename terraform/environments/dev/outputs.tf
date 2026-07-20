output "cluster_name" {
  description = "Development GKE cluster name."
  value       = module.gke.cluster_name
}
output "cluster_location" {
  description = "Development GKE cluster zone."
  value       = module.gke.cluster_location
}
output "network_name" {
  description = "Custom VPC name."
  value       = module.network.network_name
}
output "subnet_name" {
  description = "GKE subnet name."
  value       = module.network.subnet_name
}
output "artifact_registry_repository_url" {
  description = "Docker repository URL prefix."
  value       = module.artifact_registry.repository_url
}
output "node_service_account_email" {
  description = "Dedicated node service account email."
  value       = module.iam.node_service_account_email
}
output "workload_identity_pool" {
  description = "Workload Identity pool used by Kubernetes identities."
  value       = module.gke.workload_identity_pool
}
