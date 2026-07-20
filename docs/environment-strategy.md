# Environment Strategy

## Promotion path

`development -> staging -> production`

Each environment has separate Terraform roots and GitOps configuration. Values such as sizing, endpoints, policy parameters, and scaling bounds must not leak between environments.

CI validates every pull request before merge. Reviewers assess test evidence, security impact, operational risk, and rollback. A container artifact is built once from an accepted Git commit, tagged with its commit SHA, resolved by digest, and promoted unchanged rather than rebuilt.

Development receives the earliest integration deployment. Promotion to staging occurs through a reviewed configuration change after development validation. Promotion to production requires successful staging evidence, a documented approval gate, and another reviewed change. Staging and production approval records must identify the approver and artifact digest.

Production rollback restores a previously verified GitOps revision and immutable artifact digest. Argo CD reconciles that declared state, and post-rollback health checks confirm recovery. Database or incompatible schema changes, when introduced, must have an independently tested rollback or forward-recovery plan.

For portfolio cost control, environments may initially share carefully isolated infrastructure. In a real organization, development, staging, and production would be conceptually separated into different GCP projects, with distinct IAM, quotas, billing visibility, Workload Identity bindings, networks or controlled connectivity, and blast radii.

## Terraform environment model

```text
GCP organization
├── greengrid-dev project
├── greengrid-staging project
└── greengrid-prod project
```

Only the development Terraform root is deployable in the current scope. Development uses a small node pool, debug application configuration, faster iteration, controlled deletion, and lower availability. Staging would use production-like sizing and security with separate state and identity, integration and operational testing, and approval before promotion. Production would use regional availability, stricter IAM, deletion protection, controlled maintenance, stronger observability, backup/recovery, separate state and identity, and explicit approval before deployment.
