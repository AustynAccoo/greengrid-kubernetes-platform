#!/bin/sh
set -eu

terraform_root="terraform"

reject_pattern() {
  pattern="$1"
  message="$2"
  if rg -n --glob '*.tf' "$pattern" "$terraform_root"; then
    echo "Security check failed: $message" >&2
    exit 1
  fi
}

reject_pattern 'google_service_account_key' 'service-account key resource found'
reject_pattern 'roles/(owner|editor)' 'Owner or Editor role found'
reject_pattern '(allUsers|allAuthenticatedUsers)' 'public IAM member found'
reject_pattern 'network[[:space:]]*=[[:space:]]*"default"' 'default VPC usage found'
reject_pattern '(private_key|client_secret|BEGIN (RSA |EC )?PRIVATE KEY)' 'credential-like material found'
reject_pattern 'google_project_iam_(policy|binding)' 'authoritative or broad project IAM resource found'

rg -q 'workload_identity_config' terraform/modules/gke/main.tf || { echo "Workload Identity missing" >&2; exit 1; }
rg -q 'workload_metadata_config' terraform/modules/gke/main.tf || { echo "secure workload metadata missing" >&2; exit 1; }
rg -q 'enable_shielded_nodes[[:space:]]*=[[:space:]]*true' terraform/modules/gke/main.tf || { echo "Shielded Nodes missing" >&2; exit 1; }
rg -q 'service_account[[:space:]]*=[[:space:]]*var.node_service_account_email' terraform/modules/gke/main.tf || { echo "dedicated node service account missing" >&2; exit 1; }
rg -q 'datapath_provider[[:space:]]*=[[:space:]]*"ADVANCED_DATAPATH"' terraform/modules/gke/main.tf || { echo "Dataplane V2 missing" >&2; exit 1; }
rg -U -q 'managed_prometheus[[:space:]]*\{[^}]*enabled[[:space:]]*=[[:space:]]*true' terraform/modules/gke/main.tf || { echo "Managed Prometheus collection missing" >&2; exit 1; }
rg -q '"roles/monitoring.metricWriter"' terraform/modules/iam/main.tf || { echo "Managed Prometheus metric-writer role missing" >&2; exit 1; }

if git ls-files | rg '(\.tfstate($|\.)|\.tfplan$)'; then
  echo "Security check failed: Terraform state or plan is tracked" >&2
  exit 1
fi

echo "Terraform security checks passed."
