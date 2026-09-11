# Cost Controls

Development uses one zonal Standard cluster and an autoscaling pool of one to three `e2-standard-2` nodes with 50 GiB balanced disks. Zonal control-plane placement and public nodes avoid regional node multiplication and Cloud NAT cost. The machine provides enough capacity for GKE system components, Dataplane V2, telemetry workloads, and HPA metrics; smaller shared-core types are inappropriate for NetworkPolicy overhead.

The foundation creates no database, load balancer, NAT gateway, VPN, backup service, or multiple live clusters. Labels support billing analysis. A billing budget is assumed to be configured outside this Terraform state.

Likely cost drivers are node VM uptime, boot disks, network egress, log volume, Artifact Registry storage, managed Prometheus samples, and any later load balancer. The `PodMonitoring` interval plus sample/label limits bound the current custom-metric path, but Cloud Monitoring Metrics Management should still be reviewed after deployment. Autoscaling maximums bound node growth but do not replace budgets and alerts. Stop application load when unused and use an explicitly reviewed Terraform destroy for full teardown. Review the destroy plan for retained APIs, registry data, and deletion protection first.
