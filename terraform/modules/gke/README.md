# GKE

Creates a zonal Standard development cluster and a separately managed autoscaling node pool. It uses the Regular release channel, VPC-native alias IPs, Dataplane V2 NetworkPolicy enforcement, Workload Identity Federation, Shielded Nodes, secure metadata, automatic repair/upgrades, and explicit logging/monitoring. The GKE HPA add-on supplies resource metrics for the chart HPA. Managed Prometheus and HTTP load balancing are disabled for scope and cost control.
