# Development Environment

This is the only deployable Terraform root in the portfolio scope. It composes the project-services, network, Artifact Registry, IAM, and GKE modules for one cost-conscious zonal cluster in `us-east4-b`.

## Safe workflow

```sh
terraform init -backend=false
terraform validate
terraform plan -var='project_id=example-greengrid-dev'
```

For team use, initialize the empty GCS backend with a separately bootstrapped bucket and explicit backend configuration. Never commit the real project ID, `.tfvars`, state, plans, credentials, or service-account keys. Planning can read cloud APIs but cannot create resources. Applying and destroying always require separate explicit approval.

## Development defaults

- Zonal Standard GKE control plane in `us-east4-b`
- One to three `e2-standard-2` nodes with 50 GiB balanced disks
- Node CIDR `10.80.0.0/20`
- Pod CIDR `10.84.0.0/14`
- Service CIDR `10.88.0.0/20`
- Public node addresses to avoid Cloud NAT cost; Private Google Access remains enabled
- Deletion protection off by default for controlled portfolio cleanup

The selected node size has enough capacity for GKE system workloads, Dataplane V2, telemetry services, and HPA metrics while remaining modest. Actual scheduling must be checked against rendered Helm requests before deployment.

