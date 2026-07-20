output "network_id" {
  description = "VPC resource ID."
  value       = google_compute_network.this.id
}
output "network_name" {
  description = "VPC name."
  value       = google_compute_network.this.name
}
output "subnet_id" {
  description = "Subnet resource ID."
  value       = google_compute_subnetwork.this.id
}
output "subnet_name" {
  description = "Subnet name."
  value       = google_compute_subnetwork.this.name
}
output "pods_secondary_range_name" {
  description = "Pod range name."
  value       = var.pods_secondary_range_name
}
output "services_secondary_range_name" {
  description = "Service range name."
  value       = var.services_secondary_range_name
}
