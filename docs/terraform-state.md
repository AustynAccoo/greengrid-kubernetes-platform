# Terraform State

`backend.tf` contains an empty GCS backend block. Local validation uses `terraform init -backend=false`; team initialization supplies bucket and prefix through approved backend configuration rather than Git.

A real team bootstraps a dedicated encrypted, versioned GCS bucket in a separate process and state. Access is restricted to environment-specific automation and break-glass administrators, with audit logging and retention. Development, staging, and production use distinct state prefixes or preferably distinct buckets and projects.

The state bucket cannot be safely created by the same backend configuration that depends on it. Terraform state can contain sensitive provider and resource attributes even when configuration contains no secret, so state and plans remain ignored and must never be attached to public issues. State rollback uses bucket object versions only with incident approval and careful consistency review.

