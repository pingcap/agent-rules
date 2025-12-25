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

- TiDB Cloud serverless provisioning (clusters, branches, users, import/export)
- More managed database providers (planned)

## Structure

The repo is centered around the `skills/` directory:

- `skills/` - skill definitions and instructions

## How to Use

- Browse the `skills/` directory for capability-specific instructions.
- Use skills to provision or manage database resources.

## Contributing

Contributions are welcome. If you add a new component, include:

- A short rationale
- Clear prerequisites
- Step-by-step usage
- Known trade-offs

## Roadmap

- Add more database provisioning skills (managed SQL providers)
- Add database lifecycle skills (backup/restore, export/import)
