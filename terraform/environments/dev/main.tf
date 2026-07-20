module "project_services" {
  source = "../../modules/project-services"

  project_id = var.project_id
}

module "network" {
  source = "../../modules/network"

  project_id                    = var.project_id
  region                        = var.region
  network_name                  = var.network_name
  subnet_name                   = var.subnet_name
  subnet_cidr                   = var.subnet_cidr
  pods_secondary_range_name     = var.pods_secondary_range_name
  pods_secondary_cidr           = var.pods_secondary_cidr
  services_secondary_range_name = var.services_secondary_range_name
  services_secondary_cidr       = var.services_secondary_cidr

  depends_on = [module.project_services]
}

module "artifact_registry" {
  source = "../../modules/artifact-registry"

  project_id    = var.project_id
  region        = var.region
  repository_id = var.artifact_registry_repository
  labels        = local.labels

  depends_on = [module.project_services]
}

module "iam" {
  source = "../../modules/iam"

  project_id                   = var.project_id
  artifact_registry_location   = var.region
  artifact_registry_repository = module.artifact_registry.repository_id

  depends_on = [module.project_services]
}

module "gke" {
  source = "../../modules/gke"

  project_id                    = var.project_id
  location                      = local.zone
  cluster_name                  = var.cluster_name
  network_id                    = module.network.network_id
  subnet_id                     = module.network.subnet_id
  pods_secondary_range_name     = module.network.pods_secondary_range_name
  services_secondary_range_name = module.network.services_secondary_range_name
  node_service_account_email    = module.iam.node_service_account_email
  node_machine_type             = var.node_machine_type
  node_min_count                = var.node_min_count
  node_max_count                = var.node_max_count
  deletion_protection           = var.deletion_protection
  labels                        = local.labels

  depends_on = [module.project_services]
}

