# GreenGrid: Secure Kubernetes Platform for Energy Telemetry

## Project overview

GreenGrid is an employer-facing portfolio project demonstrating production-style Kubernetes platform engineering for energy telemetry on Google Kubernetes Engine (GKE). This initial repository contains only the project foundation; application and infrastructure implementation will follow in reviewed increments.

## Business context

The platform will model ingestion and delivery of operational energy telemetry while emphasizing reliability, traceability, security, and controlled change.

## Architecture

The planned solution uses Python services packaged as Docker images, GKE infrastructure managed by Terraform, Helm packaging, Argo CD reconciliation, and GitHub Actions validation and delivery. See [docs/architecture.md](docs/architecture.md).

## Environment strategy

Changes progress from development to staging to production using separate configuration, immutable artifacts, validation, review, and approvals. See [docs/environment-strategy.md](docs/environment-strategy.md).

## Demonstrated capabilities

Planned capabilities include infrastructure as code, secure containers, Kubernetes operations, GitOps, automated testing, observability, incident-oriented troubleshooting, and auditable promotion.

## Security controls

The project will apply least privilege, non-root containers, Workload Identity, dedicated Kubernetes ServiceAccounts, default-deny networking, secret hygiene, image immutability, and supply-chain validation. See [docs/security.md](docs/security.md).

## Testing strategy

Testing will be layered across code, containers, Terraform, Helm, policy, integration, and post-deployment verification. See [docs/testing-strategy.md](docs/testing-strategy.md).

## CI/CD and promotion workflow

Pull requests will run validation gates. A commit-SHA-tagged artifact will be built once and promoted unchanged through environments by reviewed GitOps configuration updates. See [docs/deployment-process.md](docs/deployment-process.md).

## Deployment

Deployment instructions will be added with the implementation. No deployable resources exist in this foundation.

## Troubleshooting demonstrations

Future scenarios will demonstrate diagnosis of failed probes, resource pressure, network-policy failures, rollout problems, and telemetry delivery issues.

## Repository structure

- `applications/`: planned telemetry API and generator services
- `terraform/`: reusable modules and environment roots
- `helm/`: platform chart
- `gitops/`: Argo CD applications and environment configuration
- `scripts/`: safe automation helpers
- `docs/`: architecture, security, process, plans, and ADRs
- `tests/`: cross-component tests
- `.github/`: workflows and collaboration templates

## Cost controls

The implementation will use explicit budgets, modest non-production sizing, autoscaling boundaries, short-lived test resources, and documented cleanup procedures. No cloud resources are created by this foundation.

## Cleanup

Cleanup instructions will be documented before any infrastructure is deployed. Destructive operations will require explicit approval.

## Production improvements

Future production-oriented extensions may include multi-region design, stronger policy enforcement, managed secrets, disaster recovery exercises, SLOs, advanced observability, and independent GCP projects and organizational controls.

