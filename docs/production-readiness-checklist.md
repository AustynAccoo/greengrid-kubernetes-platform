# Production Readiness Checklist

## Ownership and reliability

- [ ] Service owner, on-call path, SLOs, and alert priorities are documented.
- [ ] Capacity, autoscaling bounds, quotas, disruption behavior, and failure modes are tested.
- [ ] Backup, restore, disaster recovery, and rollback exercises meet defined objectives.

## Security

- [ ] Threat model and security review are complete.
- [ ] Workload Identity, dedicated ServiceAccounts, minimal IAM, and secret management are verified.
- [ ] Non-root runtime controls, resources, probes, and default-deny NetworkPolicies are enforced.
- [ ] Images are immutable, scanned, signed or attested, and traceable to reviewed source.

## Delivery and operations

- [ ] CI gates, code-owner review, staging evidence, and production approval are enforced.
- [ ] The same artifact is promoted across environments.
- [ ] Dashboards, logs, metrics, traces, runbooks, and alerts are validated.
- [ ] Rollback, incident response, change records, and audit evidence are available.

## Cost and lifecycle

- [ ] Budgets, alerts, labels, sizing, retention, and scaling limits are reviewed.
- [ ] Cleanup and decommission procedures are tested and explicitly approved.

