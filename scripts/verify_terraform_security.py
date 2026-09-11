#!/usr/bin/env python3
"""Scan Terraform source and tracked files for GreenGrid security invariants."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

TERRAFORM_ROOT = Path("terraform")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"Terraform security check failed: {message}")


def reject_pattern(pattern: str, message: str, files: dict[Path, str]) -> None:
    expression = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    for path, content in files.items():
        match = expression.search(content)
        if match is not None:
            line = content.count("\n", 0, match.start()) + 1
            raise SystemExit(f"{path}:{line}: prohibited Terraform pattern: {message}")


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [path for path in result.stdout.split("\0") if path]


def main() -> None:
    files = {path: path.read_text() for path in TERRAFORM_ROOT.rglob("*.tf")}
    require(bool(files), "no Terraform files found")

    prohibited = (
        (r"\bgoogle_service_account_key\b", "service-account key resource found"),
        (r"roles/(owner|editor)\b", "Owner or Editor role found"),
        (r"\b(allUsers|allAuthenticatedUsers)\b", "public IAM member found"),
        (r'network\s*=\s*"default"', "default VPC usage found"),
        (
            r"private_key|client_secret|BEGIN (RSA |EC )?PRIVATE KEY",
            "credential-like material found",
        ),
        (
            r"\bgoogle_project_iam_(policy|binding)\b",
            "authoritative or broad project IAM resource found",
        ),
    )
    for pattern, message in prohibited:
        reject_pattern(pattern, message, files)

    gke = Path("terraform/modules/gke/main.tf").read_text()
    iam = Path("terraform/modules/iam/main.tf").read_text()
    require("workload_identity_config" in gke, "Workload Identity missing")
    require("workload_metadata_config" in gke, "secure workload metadata missing")
    require(
        bool(re.search(r"enable_shielded_nodes\s*=\s*true", gke)),
        "Shielded Nodes missing",
    )
    require(
        bool(re.search(r"service_account\s*=\s*var\.node_service_account_email", gke)),
        "dedicated node service account missing",
    )
    require(
        bool(re.search(r'datapath_provider\s*=\s*"ADVANCED_DATAPATH"', gke)),
        "Dataplane V2 missing",
    )
    require(
        bool(re.search(r"managed_prometheus\s*\{.*?enabled\s*=\s*true", gke, re.DOTALL)),
        "Managed Prometheus collection missing",
    )
    require(
        '"roles/monitoring.metricWriter"' in iam,
        "Managed Prometheus metric-writer role missing",
    )

    prohibited_tracked = [
        path
        for path in tracked_files()
        if re.search(r"(^|/)[^/]+\.tfstate(?:\.|$)|\.tfplan$", path)
    ]
    require(
        not prohibited_tracked,
        f"Terraform state or plan is tracked: {', '.join(prohibited_tracked)}",
    )
    print("Terraform security checks passed.")


if __name__ == "__main__":
    main()
