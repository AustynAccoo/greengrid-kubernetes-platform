# GreenGrid Engineering Rules

These rules apply to the entire repository and to human and automated contributors.

- Never commit credentials, tokens, secrets, or service-account keys.
- Terraform manages persistent GCP infrastructure.
- Never run `terraform apply` or `terraform destroy` without explicit approval.
- Containers must run as non-root.
- Containers must use least-privilege security settings.
- Kubernetes workloads require CPU and memory requests and limits.
- Kubernetes workloads require startup, readiness, and liveness probes.
- Do not use the default Kubernetes ServiceAccount.
- Use Workload Identity instead of static GCP keys.
- Use default-deny NetworkPolicies.
- Use immutable image tags based on Git commit SHA.
- Build an artifact once and promote the same artifact across environments.
- Development, staging, and production configuration must remain separate.
- Staging and production changes require documented approval.
- Run tests and validation after every meaningful change.
- Keep the implementation achievable within the weekend scope.
- Document significant architecture and security decisions.

## Working agreement

Make small, reviewable changes. Do not deploy or mutate external systems unless the task explicitly authorizes it. Prefer deterministic automation, pin dependencies where practical, and update relevant documentation alongside behavior changes.

