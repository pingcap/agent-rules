# Repository Guidelines

## Project Structure & Module Organization
This repository is a curated collection of Codex skills. The main directories are:

- `README.md` for the high-level project overview and roadmap.
- `skills/` for all skill definitions.

Each skill lives in its own folder and must include a `SKILL.md` with YAML frontmatter. Optional subfolders include `scripts/`, `references/`, and `assets/` for helpers and deeper docs.

## Build, Test, and Development Commands
There is no global build or test system in this repo. Most work is documentation and skill authoring. When a skill provides scripts, run them directly and refer to its `SKILL.md` for usage.

## Coding Style & Naming Conventions
- Skill folder names use lowercase letters, digits, and hyphens (e.g., `object-storage-s3`).
- Keep `SKILL.md` concise and action-oriented; move long references into `references/`.
- Avoid extra docs inside skill folders (no README or changelog).
- Prefer ASCII text unless a skill’s domain requires otherwise.

## Testing Guidelines
No repository-wide tests are defined today. If you add scripts that need validation, document how to run checks inside the relevant `SKILL.md` and keep them lightweight.

## Commit & Pull Request Guidelines
Recent history uses short, imperative-style messages, occasionally with a PR number suffix (e.g., `init chatgpt (#2)`). Keep commit summaries concise and scoped. For pull requests, include:

- A clear description of the skill or change.
- Rationale and prerequisites (when adding a new component).
- Steps to use or verify the change.
- When referencing TiDB issues or pull requests, use the full GitHub URL (for example, `https://github.com/pingcap/tidb/issues/67498`) instead of bare `#12345` references to avoid cross-repo ambiguity.

## Security & Configuration Tips
Do not commit secrets in skills or references. If a skill requires credentials, document environment variable names in `SKILL.md` and provide placeholders only.
