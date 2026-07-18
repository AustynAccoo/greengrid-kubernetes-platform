# Contributing

## Workflow

1. Open or reference an issue with clear scope and acceptance criteria.
2. Create a short-lived branch and make a focused change.
3. Run the relevant local formatting, tests, and validation.
4. Open a pull request using the repository template.
5. Address automated checks and code-owner review.
6. Obtain documented approval for staging or production changes.

Do not commit secrets or generated credentials. Keep environment configuration separate, and update documentation or ADRs when a decision changes architecture, security, or operations.

## Commit and review expectations

Use clear, imperative commit messages. Pull requests should explain risk, testing evidence, rollback, and operational impact. Artifacts must use immutable Git commit SHA tags and be promoted without rebuilding.

