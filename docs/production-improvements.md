# Production Improvements

Production would move from the portfolio's zonal, public-node development design to a regional cluster with nodes distributed across zones, private nodes, controlled egress, restricted control-plane endpoints, deletion protection, maintenance windows, backup and recovery objectives, capacity testing, stronger audit and observability retention, and tested disaster recovery.

Organizational improvements include separate projects and state, federated deployment identities, policy-as-code admission, signed image enforcement, repository cleanup policy, vulnerability gates, IAM conditions, organization policies, centralized logging, alerting and SLOs, quota planning, support escalation, and rehearsed cluster replacement.

Promotion remains build-once: immutable Git-SHA image digests advance from development to staging to production after validation and documented approval. Infrastructure rollback and application rollback are separate procedures.

