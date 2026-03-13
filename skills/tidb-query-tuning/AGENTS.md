# TiDB Query Tuning Agent Notes

Use this skill directory for two different knowledge sources:

- curated topic references under `references/`
- GitHub issue-derived field experience generated into markdown files

## When to mine issue experience

Use GitHub issue mining when:

- the local references do not cover a customer-facing symptom well enough
- you need a recent field precedent instead of a general tuning rule
- you want fix PRs, merge timestamps, and open issue reminders
- you want to build or refresh a local corpus of customer-driven planner or stats bugs

Do not start from issue mining if a stable reference under `references/` already answers the question. Use the issue corpus to complement the topic docs, not replace them.

## Default workflow

1. Start with the local references in `references/`.
2. Search `references/optimizer-oncall-experiences-redacted/` for a symptom match.
3. Search `references/tidb-customer-planner-issues/` if you need linked PRs, merge times, or still-open customer gaps.
4. If the local corpora are still missing the pattern, mine GitHub issues with the script in `scripts/`.
5. Review the generated files, then fold reusable learnings back into the relevant reference docs when appropriate.

## Issue mining script

Use:

`scripts/generate_tidb_issue_experiences.py`

The script:

- searches GitHub issues with a provided query
- follows issue timeline cross-references and explicit fix comments
- collects linked PR metadata and changed files
- writes one markdown file per issue
- writes an index `README.md` into the output directory

The current checked-in issue corpus lives under:

- `references/tidb-customer-planner-issues/`

## Recommended query patterns

For customer-driven planner issues:

```text
repo:pingcap/tidb is:issue label:"report/customer" label:"sig/planner" created:>=2024-01-01
```

For stats-heavy issue mining:

```text
repo:pingcap/tidb is:issue label:"report/customer" (label:"sig/planner" OR label:"sig/execution") stats created:>=2024-01-01
```

Adjust the query rather than hardcoding different behaviors into the script.

## Usage example

```bash
python3 skills/tidb-query-tuning/scripts/generate_tidb_issue_experiences.py \
  --query 'repo:pingcap/tidb is:issue label:"report/customer" label:"sig/planner" created:>=2024-01-01' \
  --out-dir outputs/tidb-customer-planner-issues
```

## What to keep from generated issue files

Keep and reuse:

- customer-facing symptom descriptions
- investigation clues
- linked fix PRs
- merge timestamps
- affected modules
- open issues that should remain on the reminder list

Do not treat every generated issue as a mature tuning rule. Generated files are raw field precedents. Promote them into `references/` only after the pattern is stable and reusable.

## Tooling assumptions

- `gh` CLI must be installed and authenticated
- network access to GitHub must be available
- the output directory should be treated as generated content

## Editing guidance

- Keep curated docs in `references/` concise and topic-oriented.
- Keep generated issue corpora outside the hand-written topic docs unless they are intentionally promoted.
- If you regenerate a corpus, prefer writing into a fresh output directory or knowingly replacing the previous generated set.
