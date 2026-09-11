# Deployment Process

## Pull-request gates

The `CI` workflow runs four independent, read-only jobs on every pull request and on pushes to `main`:

1. Application formatting, linting, 14 tests, and Python vulnerability audit.
2. Helm lint, rendering, client dry-run, and manifest-policy checks for dev, staging, and production.
3. Terraform formatting, backend-free initialization, validation, and prohibited-pattern checks.
4. Container build, health, telemetry flow, non-root identity, read-only filesystem, writable `/tmp`, dropped capabilities, and no-new-privileges checks.

Actions are pinned to complete commit SHAs. Workflow permissions are read-only, overlapping runs are cancelled, and every job has a timeout. CI has no GCP credential and cannot apply Terraform or install Helm releases.

## Development infrastructure change

From `terraform/environments/dev`, use a remote GCS backend for shared work. The backend bucket is bootstrapped separately and must not be created by the state that consumes it.

```sh
terraform init -backend-config=<approved-backend-config>
terraform plan -input=false -out=<reviewed-plan-file> -var='project_id=<project-id>'
terraform show <reviewed-plan-file>
```

Review resource replacements, IAM changes, networking, node count, cost, deletion protection, and provider versions. `terraform apply` requires explicit approval and must apply the reviewed plan rather than silently creating a new one.

The observability hardening change is expected to update the existing cluster to enable managed Prometheus and add `roles/monitoring.metricWriter` to the node identity. Confirm that the plan does not replace the cluster or node pool before approval.

## Build-once image flow

Each service image is built from one accepted Git commit. Use a tag in the form `git-<40-character-lowercase-commit-sha>`, push it once, resolve its registry digest, and record both values. Do not rebuild between environments.

```text
<registry>/telemetry-api:git-<sha>@sha256:<digest>
<registry>/telemetry-generator:git-<sha>@sha256:<digest>
```

The current Helm helper enforces the Git-SHA tag format. A future delivery workflow should update values to full digests after build and promote the same digest.

## Development Helm release

Namespace ownership sits outside the application chart. Create and label it once through an approved platform process:

```sh
kubectl create namespace greengrid-dev
kubectl label namespace greengrid-dev pod-security.kubernetes.io/enforce=restricted
```

Preview the exact release before installation:

```sh
helm upgrade --install greengrid helm/greengrid-platform \
  --namespace greengrid-dev \
  --values helm/greengrid-platform/values-dev.yaml \
  --set telemetryApi.image.repository=<api-repository> \
  --set telemetryApi.image.tag=git-<sha> \
  --set telemetryGenerator.image.repository=<generator-repository> \
  --set telemetryGenerator.image.tag=git-<sha> \
  --dry-run=server
```

Remove `--dry-run=server` only after review and explicit deployment approval. Use `--atomic --wait --timeout 5m` for the approved upgrade so a failed rollout returns to the preceding Helm release.

## Post-deployment evidence

```sh
kubectl -n greengrid-dev get deploy,pods,svc,endpoints,hpa,pdb,networkpolicy,podmonitoring
kubectl -n greengrid-dev rollout status deployment --all --timeout=3m
helm test greengrid --namespace greengrid-dev --logs
kubectl -n greengrid-dev logs -l app.kubernetes.io/component=telemetry-generator --tail=50
kubectl -n greengrid-dev describe podmonitoring
```

Confirm the following:

- Both rollouts complete and Pods are Ready without repeated restarts.
- The API Service has ready endpoints.
- Generator logs show successful `201` deliveries.
- HPA has current CPU metrics and the configured replica bounds.
- `PodMonitoring` configuration is accepted and PromQL returns `up`, `greengrid_telemetry_records`, and `rate(greengrid_telemetry_submissions_total[5m])`.
- No unexpected external Service or additional network path exists.

## Promotion

Development evidence permits a reviewed change for staging. Staging evidence and an explicit approver permit production promotion. The artifact digest must remain identical through both promotions. The repository currently provides environment values but does not claim live staging/production clusters or automated GitOps reconciliation.

## Rollback

Application rollback and infrastructure rollback are separate decisions.

- **Application:** use `helm history`, review the previous revision/digests, run `helm rollback <release> <revision> --wait`, then repeat post-deployment checks.
- **Configuration:** revert the responsible Git commit and allow the normal reviewed delivery path to restore desired state.
- **Infrastructure:** revert Terraform configuration, produce a new plan, and inspect it. Never assume cluster, subnet, or identity changes are safely reversible.
- **Emergency change:** record the reason, operator, commands, evidence, and follow-up. Reconcile the repository immediately afterward.
