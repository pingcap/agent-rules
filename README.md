<p align="center">
  <img src="public/logo.svg" alt="AgenticStore logo" width="120" height="120" />
</p>

# AgenticStore

AgenticStore is a repo for designing and curating SKILLS for code agents. It focuses on database provisioning workflows for agentic apps, with TiDB Cloud as the current supported provider. Components are added incrementally and documented as the skill set grows.

## Goals

- Provide reusable SKILLS for database provisioning and lifecycle tasks
- Offer opinionated, composable database workflows for AI app builders
- Keep guidance practical, concise, and easy to apply in real projects

## Scope (Current + Planned)

- TiDB Cloud provisioning and lifecycle workflows
- TiDB Cloud serverless driver usage and edge runtime guidance
- TiDB Cloud Kysely usage (TCP + serverless/edge)
- More managed database providers (planned)

## Structure

The repo is centered around the `skills/` directory:

- `skills/` - skill definitions and instructions

## How to Use

- Browse the `skills/` directory for capability-specific instructions.
- Use skills to provision, connect to, or manage database resources.
- Open the relevant `SKILL.md` for step-by-step guidance and prerequisites.

## Skill Authoring

- Skill folders use lowercase letters, digits, and hyphens (e.g., `object-storage-s3`).
- Each skill must include `SKILL.md` with YAML frontmatter containing `name`, `description`, and optional `allowed-tools`.
- Keep the body concise with a clear "when to use" section and a short workflow.
- Move long docs into `references/` and prefer runnable scripts or templates in `scripts/` or `assets/`.
- Avoid extra docs inside skill folders (no README or changelog).

## Current Skills

- `tidbx` - TiDB Cloud provisioning and lifecycle workflows.
- `tidbx-serverless-driver` - Serverless HTTP driver usage and edge runtime guidance.
- `tidbx-kysely` - Kysely integration patterns (TCP + serverless/edge).
- `tidbx-prisma` - Prisma ORM setup (schema, migrations, typed client) for TiDB.
- `tidbx-nextjs` - Next.js App Router patterns for TiDB (route handlers, runtimes, Vercel/serverless).
- `tidbx-javascript-mysql2` - Node.js mysql2 driver connection patterns (TLS/CA, pool, transactions).
- `tidbx-javascript-mysqljs` - Node.js mysqljs/mysql driver connection patterns (TLS/CA, pool, transactions).

## Contributing

Contributions are welcome. If you add a new component, include:

- A short rationale
- Clear prerequisites
- Step-by-step usage
- Known trade-offs

## Roadmap
