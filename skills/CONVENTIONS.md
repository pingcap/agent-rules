# Skill Conventions

This directory stores Codex skills for the AgenticStore repo.

## Layout

- `skills/` - publishable skills

Each skill lives in its own folder named after the skill.

## Naming

- Use lowercase letters, digits, and hyphens only.
- Keep names short and action-oriented (e.g., `db-postgres`, `object-storage-s3`).

## Required Files

Every skill must include:

- `SKILL.md` with YAML frontmatter containing:
  - `name` (short skill id)
  - `description` (primary trigger signal; written as a clear "use when" summary)
  - `allowed-tools` (optional, list only the tools the skill needs)

Optional directories:

- `scripts/` - executable helpers
- `references/` - detailed docs loaded on demand
- `assets/` - templates or files used in outputs

## Skill Structure (Progressive Disclosure)

Skills are loaded in stages to keep context small:

- Level 1: Metadata (YAML frontmatter) is always loaded at startup.
- Level 2: `SKILL.md` body is loaded only when the skill is triggered.
- Level 3: Supporting files are loaded only when referenced:
  - `references/` for deep dives and factual lookups
  - `assets/` for templates and example files
  - `scripts/` for deterministic operations run via shell

Design for this flow: keep the main instructions concise and defer long docs to `references/`.

## Creation Workflow

Prefer the `init_skill.py` helper to scaffold new skills:

```bash
scripts/init_skill.py <skill-name> --path skills --resources scripts,references,assets
```

Package when ready:

```bash
scripts/package_skill.py <path/to/skill-folder>
```

## Style

- Keep `SKILL.md` concise and action-oriented.
- Move deep reference material into `references/`.
- Avoid extra docs inside skill folders (no README or changelog).
- Use "when to use" bullets and short workflows (checklists and phases).
- Document required environment variables and never hardcode secrets.
- Prefer runnable examples and scripts over long inline code blocks.
