# Production Readiness Checklist

## Ownership and reliability

- [ ] Service owner, on-call path, SLOs, and alert priorities are documented.
- [ ] Capacity, autoscaling bounds, quotas, disruption behavior, and failure modes are tested.
- [ ] Backup, restore, disaster recovery, and rollback exercises meet defined objectives.

## Security

- [ ] Threat model and security review are complete.
- [x] Workload Identity, dedicated ServiceAccounts, and minimal current IAM are defined and statically verified; application secret management remains future work because the services consume no secret.
- [x] Non-root runtime controls, resources, probes, and default-deny NetworkPolicies are rendered and automatically enforced by policy checks.
- [ ] Images are immutable, scanned, signed or attested, and traceable to reviewed source.

## Delivery and operations

- [ ] CI gates are implemented; code-owner review, staging evidence, and production approval still require repository/environment enforcement.
- [ ] The same artifact is promoted across environments.
- [ ] Structured logs, metrics collection configuration, and runbooks exist; live scrape evidence, dashboards, traces, and alerts remain incomplete.
- [ ] Rollback, incident response, change records, and audit evidence are available.

## Cost and lifecycle

- [ ] Budgets, alerts, labels, sizing, retention, and scaling limits are reviewed.
- [ ] Cleanup and decommission procedures are tested and explicitly approved.
