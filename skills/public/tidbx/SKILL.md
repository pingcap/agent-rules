---
name: tidbx
description: Provision TiDB Cloud Serverless clusters and related resources. Use when creating, deleting, or listing clusters/branches, managing SQL users, or importing/exporting data.
---

# TiDB Cloud Provisioning (TiDB X)

Provision TiDB Cloud Serverless (now branded as TiDB X) clusters and related resources using the workflows below. Use the command patterns in the references file as implementation details, but keep the focus on the provisioning outcome and required inputs.

Note: TiDB Cloud Serverless has been renamed to TiDB X. Keep both terms in user-facing guidance for clarity.

Reminder: This skill provides TiDB Cloud cluster CRUD operations (Create, Read/list, Update, Delete). Before any CRUD action, ensure the user completes ticloud setup and authentication (see Provisioning Setup below).

## Provisioning Setup

Complete setup before any provisioning or lifecycle operations.

Setup Status (TiDB Cloud component)  
- ○ ticloud installed  
- ○ authenticated  

### Install CLI

For macOS/Linux:

```bash
curl https://raw.githubusercontent.com/tidbcloud/tidbcloud-cli/main/install.sh | sh
```

After install, verify:

```bash
command -v ticloud
```

Update checklist:

- ● ticloud installed

### Authenticate

Always check auth first:

```bash
ticloud auth whoami
```

If not logged in, run:

```bash
ticloud auth login --insecure-storage
```

Wait for the user to complete the browser flow, then re-check:

```bash
ticloud auth whoami
```

Update checklist:

- ● authenticated

### Network/DNS Issues

If `ticloud auth whoami` fails due to network/DNS (e.g., cannot reach `iam.tidbapi.com`):

- Explain that the environment needs network access for the CLI.
- Ask the user to enable network access for the agent environment, or run the command locally and share the output.

If setup errors persist, point the user to the official docs:

- https://docs.pingcap.com/tidbcloud/get-started-with-cli/

## Table Formatting (ASCII)

Use terminal-friendly ASCII tables for any list output (regions, projects, clusters, SQL users).

- Use ASCII borders with `+`, `-`, and `|`.
- Use fixed-width columns; left-align all text.
- Refine the table formatting so columns align cleanly and remain readable.
- Keep headers short and descriptive.
- Do not use Unicode box-drawing characters.

Example format:

```
+----------------+-----------------------+---------------------------+--------+
| Display Name   | Cluster ID            | Region                    | State  |
+----------------+-----------------------+---------------------------+--------+
| test-skill     | 10913591479486949552  | alicloud-ap-southeast-1   | ACTIVE |
+----------------+-----------------------+---------------------------+--------+
```

## Auth Gate + Network Issues

- Always run `ticloud auth whoami` before any action.
- If not logged in, complete the setup steps in this document before proceeding.
- If auth fails due to network/DNS errors (e.g., cannot reach `iam.tidbapi.com`), tell the user:
  - The environment needs network access for the CLI to reach TiDB Cloud.
  - They must enable network access in their agent environment or run the command locally and share the output.

## Core Workflows

### Create a Cluster

- Do not present a setup checklist for cluster creation steps (region/project/cluster name). If a status is needed, label it as "Create Flow" rather than "Setup Status."
- Run `ticloud serverless region` and present the full list in a terminal-friendly ASCII bordered table (fixed-width columns in a code block) with selectable option numbers before asking for a region.
- If the user doesn’t know the project ID, run `ticloud project list` and present the results in the same ASCII bordered table format before asking. Keep the project ID as a third column.
- Ask in this order: region (after listing options), project ID (after listing projects if needed), then cluster display name as the final confirmation step.
- Confirm the required parameters (region, project, cluster name).
- Use the serverless create command pattern from `references/ticloud.md`.
- When creating a cluster, wait 60 seconds for completion before returning control.
- Verify creation by listing clusters and present results in an ASCII bordered table rather than raw JSON. If the environment is non-interactive, use `ticloud serverless list -p <project-id> -o json` and render a table from the JSON.

### Delete a Cluster

- Require explicit user confirmation before delete operations.
- Use the serverless delete command pattern from `references/ticloud.md`.
- List clusters to confirm removal and present results in an ASCII bordered table rather than raw JSON. If the environment is non-interactive, use `ticloud serverless list -p <project-id> -o json` and render a table from the JSON.

### List Clusters

- If the user doesn’t know the available projects, list projects first, then ask which project to use.
- Ask which project the user wants to list before running `ticloud serverless list`.
- If the user doesn’t know the project ID, run `ticloud project list` and present results in the ASCII bordered table format.
- For non-interactive environments, use `ticloud serverless list -p <project-id> -o json` and render a table from the JSON.

### Describe a Cluster

- Confirm the target cluster (name or cluster ID).
- Use `ticloud serverless list -p <project-id> -o json` and filter by cluster ID or display name.
- Present details in a two-column ASCII table (Field, Value) with refined alignment.

### Create or Delete a Branch

- Confirm the target cluster and branch name.
- Use the branch commands from `references/ticloud.md`.
- List branches to verify changes.

### List Branches

- Follow the hierarchy: project → cluster → branch.
- If the user doesn’t know the available projects, list projects first.
- If the user doesn’t know the project ID, run `ticloud project list` and present results in the ASCII bordered table format.
- If the user doesn’t know the cluster ID, list clusters for the selected project and present results in the ASCII bordered table format.
- Ask which cluster the user wants to list before running `ticloud serverless branch list`.
- For non-interactive environments, use `ticloud serverless branch list --cluster-id <cluster-id> -o json` and render a table from the JSON.

### Manage SQL Users

- Use serverless SQL user commands from `references/ticloud.md`.
- Prefer generating the command for the user rather than executing it, unless the user explicitly asks you to run it.
- For password handling and execution, use `scripts/sql_user_manage.py` to generate a strong password, fetch host/port, create/update the SQL user, and update connection vars in `.env`.
- Never read or display stored passwords (do not cat `.env`).
- When listing SQL users, present results in an ASCII bordered table rather than raw JSON.
- Default to `role_readwrite` unless the user requests a different role.
- For SQL usernames, accept the exact value the user provides (including prefixed names like `2Q3h2gvr6xKRBhn.killer`).
- For password refresh, `--database` is optional; do not require it when updating a user.
- When creating or updating SQL users, wait 60 seconds for completion before returning control.

### Import or Export Data

- Confirm source/target, file format, and target database/schema.
- Use the serverless import/export commands from `references/ticloud.md`.
- Verify completion in CLI output or by listing relevant resources.

## Safety Checks

- Always run `ticloud auth whoami` before any action.
- Require explicit user confirmation before delete operations.
- For `ticloud` operations that take time, wait 60 seconds before returning control.

## References

- Command patterns and placeholders: `references/ticloud.md`
