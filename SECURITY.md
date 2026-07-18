# Security Policy

## Reporting a vulnerability

Do not disclose suspected vulnerabilities in a public issue. For this portfolio repository, contact the repository owner privately through the security-reporting channel configured on the hosting platform. Include impact, reproduction steps, affected versions, and any suggested mitigation.

## Supported versions

Until the first release, only the latest commit on the default branch is considered supported.

## Security baseline

Never commit secrets. Use least privilege, non-root containers, dedicated Kubernetes ServiceAccounts, Workload Identity, default-deny network policy, bounded resources, required health probes, immutable artifacts, reviewed changes, and separated environment configuration.

