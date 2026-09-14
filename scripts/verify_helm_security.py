#!/usr/bin/env python3
"""Verify security and observability invariants in a rendered Helm manifest."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

Manifest = dict[str, Any]
IMMUTABLE_IMAGE = re.compile(r":git-[0-9a-f]{40}$")


def require(condition: bool, message: str) -> None:
    """Abort with a useful contract failure instead of a Python traceback."""

    if not condition:
        raise SystemExit(message)


def resource_name(document: Manifest) -> str:
    return str(document.get("metadata", {}).get("name", "<unnamed>"))


def find_policy(policies: list[Manifest], suffix: str) -> Manifest:
    matches = [policy for policy in policies if resource_name(policy).endswith(suffix)]
    require(len(matches) == 1, f"expected one NetworkPolicy ending in {suffix!r}")
    return matches[0]


def ports(rule: Manifest) -> set[tuple[str, int]]:
    return {(str(port.get("protocol")), int(port.get("port"))) for port in rule.get("ports", [])}


def verify_container(name: str, container: Manifest, *, require_probes: bool) -> None:
    image = str(container.get("image", ""))
    require(bool(IMMUTABLE_IMAGE.search(image)), f"{name}: mutable image {image!r}")

    context = container.get("securityContext", {})
    require(context.get("privileged") is False, f"{name}: privileged must be false")
    require(
        context.get("allowPrivilegeEscalation") is False,
        f"{name}: privilege escalation must be false",
    )
    require(
        context.get("readOnlyRootFilesystem") is True,
        f"{name}: root filesystem must be read-only",
    )
    require("ALL" in context.get("capabilities", {}).get("drop", []), f"{name}: drop ALL")

    resources = container.get("resources", {})
    for resource_type in ("requests", "limits"):
        values = resources.get(resource_type, {})
        require(
            "cpu" in values and "memory" in values,
            f"{name}: CPU and memory {resource_type} are required",
        )

    if require_probes:
        for probe in ("startupProbe", "readinessProbe", "livenessProbe"):
            require(probe in container, f"{name}: {probe} is required")


def verify_pod_spec(owner: str, pod: Manifest, *, require_probes: bool) -> None:
    account = pod.get("serviceAccountName")
    require(account not in (None, "default"), f"{owner}: dedicated ServiceAccount required")
    require(
        pod.get("automountServiceAccountToken") is False,
        f"{owner}: ServiceAccount token automount must be false",
    )
    for field in ("hostNetwork", "hostPID", "hostIPC"):
        require(pod.get(field) is False, f"{owner}: {field} must be false")
    require(
        not any("hostPath" in volume for volume in pod.get("volumes", [])),
        f"{owner}: hostPath volumes are prohibited",
    )

    security = pod.get("securityContext", {})
    require(security.get("runAsNonRoot") is True, f"{owner}: runAsNonRoot is required")
    require(
        security.get("seccompProfile", {}).get("type") == "RuntimeDefault",
        f"{owner}: RuntimeDefault seccomp is required",
    )

    containers = pod.get("containers", [])
    require(bool(containers), f"{owner}: at least one container is required")
    for container in containers:
        verify_container(
            f"{owner}/{container.get('name', '<unnamed>')}",
            container,
            require_probes=require_probes,
        )


def verify_network_policies(policies: list[Manifest]) -> None:
    default_deny = find_policy(policies, "-default-deny")
    require(default_deny.get("spec", {}).get("podSelector") == {}, "default deny selects pods")
    require(
        sorted(default_deny.get("spec", {}).get("policyTypes", [])) == ["Egress", "Ingress"],
        "default deny must cover ingress and egress",
    )

    dns = find_policy(policies, "-allow-dns")
    dns_rules = dns.get("spec", {}).get("egress", [])
    require(len(dns_rules) == 1, "DNS policy must have exactly one egress rule")
    dns_targets = dns_rules[0].get("to", [])
    require(len(dns_targets) == 1, "DNS must have one namespace-and-pod target")
    require(
        dns_targets[0]
        .get("namespaceSelector", {})
        .get("matchLabels", {})
        .get("kubernetes.io/metadata.name")
        == "kube-system",
        "DNS egress must target kube-system",
    )
    require(
        dns_targets[0].get("podSelector", {}).get("matchLabels", {}).get("k8s-app") == "kube-dns",
        "DNS egress must target kube-dns pods",
    )
    require(ports(dns_rules[0]) == {("TCP", 53), ("UDP", 53)}, "DNS ports are too broad")

    generator = find_policy(policies, "-generator-to-api")
    generator_rules = generator.get("spec", {}).get("egress", [])
    require(len(generator_rules) == 1, "generator must have one application egress rule")
    generator_targets = generator_rules[0].get("to", [])
    require(len(generator_targets) == 1, "generator must target only API pods")
    require(
        generator_targets[0]
        .get("podSelector", {})
        .get("matchLabels", {})
        .get("app.kubernetes.io/component")
        == "telemetry-api",
        "generator egress must target telemetry-api",
    )
    require(ports(generator_rules[0]) == {("TCP", 8000)}, "generator egress is too broad")

    helm_test = find_policy(policies, "-helm-test-to-api")
    release_labels = generator.get("spec", {}).get("podSelector", {}).get("matchLabels", {})
    release_labels = {
        key: value for key, value in release_labels.items() if key != "app.kubernetes.io/component"
    }
    require(
        set(release_labels) == {"app.kubernetes.io/name", "app.kubernetes.io/instance"},
        "application selectors must include chart and release labels",
    )
    require(
        helm_test.get("spec")
        == {
            "podSelector": {
                "matchLabels": {**release_labels, "app.kubernetes.io/component": "helm-test"}
            },
            "policyTypes": ["Egress"],
            "egress": [
                {
                    "to": [
                        {
                            "podSelector": {
                                "matchLabels": {
                                    **release_labels,
                                    "app.kubernetes.io/component": "telemetry-api",
                                }
                            }
                        }
                    ],
                    "ports": [{"protocol": "TCP", "port": 8000}],
                }
            ],
        },
        "Helm test egress must allow only same-namespace, same-release API pods on TCP 8000",
    )

    api = find_policy(policies, "-api-ingress")
    api_rules = api.get("spec", {}).get("ingress", [])
    require(len(api_rules) == 1, "API application ingress must have exactly one rule")
    source_components = {
        source.get("podSelector", {}).get("matchLabels", {}).get("app.kubernetes.io/component")
        for source in api_rules[0].get("from", [])
    }
    require(
        source_components == {"telemetry-generator", "helm-test"},
        "API ingress must allow only the generator and Helm test",
    )
    require(ports(api_rules[0]) == {("TCP", 8000)}, "API ingress is too broad")

    monitoring = find_policy(policies, "-managed-prometheus-to-api")
    monitoring_rules = monitoring.get("spec", {}).get("ingress", [])
    require(len(monitoring_rules) == 1, "monitoring ingress must have exactly one rule")
    monitoring_sources = monitoring_rules[0].get("from", [])
    require(len(monitoring_sources) == 1, "monitoring ingress must have exactly one source")
    source = monitoring_sources[0]
    require(
        source.get("namespaceSelector", {})
        .get("matchLabels", {})
        .get("kubernetes.io/metadata.name")
        == "gmp-system",
        "monitoring ingress must originate in gmp-system",
    )
    require(
        source.get("podSelector", {}).get("matchLabels", {}).get("app.kubernetes.io/name")
        == "collector",
        "monitoring ingress must originate from managed collectors",
    )
    require(ports(monitoring_rules[0]) == {("TCP", 8000)}, "monitoring ingress is too broad")

    for policy in policies:
        spec = policy.get("spec", {})
        for direction in ("ingress", "egress"):
            peer_key = "from" if direction == "ingress" else "to"
            for rule in spec.get(direction, []):
                require(
                    not any("ipBlock" in peer for peer in rule.get(peer_key, [])),
                    f"{resource_name(policy)}: unrestricted IP blocks are prohibited",
                )


def verify_pod_monitoring(resources: list[Manifest]) -> None:
    require(len(resources) == 1, "exactly one PodMonitoring resource is required")
    spec = resources[0].get("spec", {})
    require(
        spec.get("selector", {}).get("matchLabels", {}).get("app.kubernetes.io/component")
        == "telemetry-api",
        "PodMonitoring must select telemetry-api pods",
    )
    endpoints = spec.get("endpoints", [])
    require(len(endpoints) == 1, "PodMonitoring must define one scrape endpoint")
    endpoint = endpoints[0]
    require(endpoint.get("port") == "http", "PodMonitoring must use the named HTTP port")
    require(endpoint.get("path") == "/metrics", "PodMonitoring must scrape /metrics")
    require(endpoint.get("interval") == "30s", "PodMonitoring interval must be 30s")
    require(endpoint.get("timeout") == "10s", "PodMonitoring timeout must be 10s")
    require(spec.get("filterRunning") is True, "PodMonitoring must ignore completed pods")
    limits = spec.get("limits", {})
    for field in ("samples", "labels", "labelNameLength", "labelValueLength"):
        require(int(limits.get(field, 0)) > 0, f"PodMonitoring {field} limit is required")


def verify_environment_config(config_maps: list[Manifest], environment: str) -> None:
    api_configs = [
        config_map
        for config_map in config_maps
        if config_map.get("metadata", {}).get("labels", {}).get("app.kubernetes.io/component")
        == "telemetry-api"
    ]
    require(len(api_configs) == 1, "exactly one telemetry API ConfigMap is required")
    actual = str(api_configs[0].get("data", {}).get("LOAD_SIMULATION_ENABLED", "")).lower()
    expected = "true" if environment == "dev" else "false"
    require(
        actual == expected,
        f"{environment}: LOAD_SIMULATION_ENABLED must be {expected}, found {actual!r}",
    )


def main() -> None:
    require(len(sys.argv) == 2, "usage: verify_helm_security.py <manifest>")
    manifest_path = Path(sys.argv[1])
    require(manifest_path.is_file(), f"manifest not found: {manifest_path}")

    documents = [document for document in yaml.safe_load_all(manifest_path.read_text()) if document]
    require(bool(documents), f"no Kubernetes resources found in {manifest_path}")
    by_kind: dict[str, list[Manifest]] = {}
    for document in documents:
        by_kind.setdefault(str(document.get("kind")), []).append(document)

    required = {
        "Deployment": 2,
        "ServiceAccount": 2,
        "ConfigMap": 2,
        "Service": 1,
        "HorizontalPodAutoscaler": 1,
        "PodDisruptionBudget": 1,
        "ResourceQuota": 1,
        "LimitRange": 1,
        "NetworkPolicy": 6,
        "PodMonitoring": 1,
        "Pod": 1,
    }
    require(len(documents) == 19, f"expected 19 resources, found {len(documents)}")
    for kind, expected in required.items():
        actual = len(by_kind.get(kind, []))
        require(actual == expected, f"expected {expected} {kind}, found {actual}")

    for account in by_kind["ServiceAccount"]:
        require(
            account.get("automountServiceAccountToken") is False,
            f"{resource_name(account)}: token automount must be false",
        )

    for deployment in by_kind["Deployment"]:
        verify_pod_spec(
            resource_name(deployment),
            deployment.get("spec", {}).get("template", {}).get("spec", {}),
            require_probes=True,
        )

    for pod in by_kind["Pod"]:
        verify_pod_spec(resource_name(pod), pod.get("spec", {}), require_probes=False)
        require(pod.get("spec", {}).get("restartPolicy") == "Never", "Helm test must not restart")

    services = by_kind["Service"]
    require(
        all(service.get("spec", {}).get("type") == "ClusterIP" for service in services),
        "all Services must remain internal ClusterIP Services",
    )

    verify_network_policies(by_kind["NetworkPolicy"])
    verify_pod_monitoring(by_kind["PodMonitoring"])
    verify_environment_config(by_kind["ConfigMap"], manifest_path.stem)
    print(f"Security verification passed for {manifest_path} ({len(documents)} resources).")


if __name__ == "__main__":
    main()
