---
name: pytidb-dev
description: Use when contributing to the PyTiDB repository: set up the dev environment, run lint/format/test, work with optional extras (models, pandas, mcp), and build or publish.
---

# PyTiDB Development

Use this skill for repository maintenance and contribution workflows.

## Workflow

1. Install dependencies with uv, then sync dev extras.
2. Run lint and format with ruff before tests.
3. Run pytest with the repo test settings and required env vars.
4. Use make targets when available.
5. Avoid committing secrets or local .env files.

## References

- Dev commands and env notes: `references/dev.md`
