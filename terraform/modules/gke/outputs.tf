output "cluster_id" {
  description = "GKE cluster resource ID."
  value       = google_container_cluster.this.id
}
output "cluster_name" {
  description = "GKE cluster name."
  value       = google_container_cluster.this.name
}
output "cluster_location" {
  description = "GKE cluster location."
  value       = google_container_cluster.this.location
}
output "workload_identity_pool" {
  description = "GKE Workload Identity pool."
  value       = google_container_cluster.this.workload_identity_config[0].workload_pool
}
output "node_pool_name" {
  description = "Separately managed node pool name."
  value       = google_container_node_pool.primary.name
}
