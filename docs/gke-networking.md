# GKE Networking

Development uses a custom-mode VPC and a `us-east4` subnet. The non-overlapping ranges are:

- Nodes: `10.80.0.0/20`
- Pods: `10.84.0.0/14`
- Services: `10.88.0.0/20`

VPC-native alias IPs bind the named Pod and Service secondary ranges to GKE. Private Google Access is enabled. GKE Dataplane V2 provides built-in Kubernetes NetworkPolicy enforcement for the default-deny Helm policies; the legacy cluster `network_policy` setting is deliberately omitted because GKE rejects using both.

Development nodes have public addresses so the cluster can retrieve required internet content without paying for Cloud NAT. No custom load balancers, VPNs, NAT gateways, or unrelated firewall rules are created. The API remains a ClusterIP in the Helm chart.

At workload scope, default-deny covers ingress and egress. All chart pods may reach only `kube-dns` in `kube-system` over TCP/UDP 53. Generator pods may reach API pods over TCP 8000, while API ingress admits only generator, Helm-test, and GKE managed Prometheus collector traffic. Collector access requires both the `gmp-system` namespace label and `app.kubernetes.io/name=collector` pod label; it does not create general namespace ingress.

Production should use private nodes, restricted control-plane access, Cloud NAT or an approved egress proxy, firewall policy, flow logs, DNS review, and address planning coordinated across the organization. Workload Identity with Dataplane V2 also requires Helm network policy to permit the GKE metadata server path when a workload eventually uses Google APIs.
