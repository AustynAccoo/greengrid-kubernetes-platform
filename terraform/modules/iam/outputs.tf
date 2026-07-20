output "node_service_account_email" {
  description = "Email of the dedicated GKE node service account."
  value       = google_service_account.gke_nodes.email
}
output "node_service_account_name" {
  description = "Resource name of the node service account."
  value       = google_service_account.gke_nodes.name
}
output "node_project_roles" {
  description = "Project roles granted to the node service account."
  value       = sort(tolist(local.node_project_roles))
}

