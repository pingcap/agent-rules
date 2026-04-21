# TiDB Query Tuning Agent Notes

Use this skill directory for two different knowledge sources:

- curated topic references under `references/`
- GitHub issue-derived field experience generated into markdown files

## When to mine issue experience

Use GitHub issue mining when:

- the local references do not cover a customer-facing symptom well enough
- you need a recent field precedent instead of a general tuning rule
- you want fix PRs, merge timestamps, and open issue reminders
- you want to build or refresh a local corpus of planner or stats bugs, with `report/customer` issues preferred when they exist

Do not start from issue mining if a stable reference under `references/` already answers the question. Use the issue corpus to complement the topic docs, not replace them.

## Default workflow

1. Start with the local references in `references/`.
2. Search `references/optimizer-oncall-experiences-redacted/` for a symptom match.
3. Search `references/tidb-customer-planner-issues/` if you need linked PRs, merge times, or still-open customer gaps.
4. If the most relevant recent planner issue does not carry `report/customer`, do not exclude it for that reason alone. Broaden the GitHub query and inspect it directly.
5. If the local corpora are still missing the pattern, mine GitHub issues with the script in `scripts/`.
6. Review the generated files, then fold reusable learnings back into the relevant reference docs when appropriate.

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

Preferred query for customer-driven planner issues:

```text
repo:pingcap/tidb is:issue label:"report/customer" label:"sig/planner" created:>=2024-01-01
```

Fallback query for recent planner issues when `report/customer` is missing but the issue is still highly relevant:

```text
repo:pingcap/tidb is:issue label:"sig/planner" created:>=2024-01-01
```

Preferred query for stats-heavy issue mining:

```text
repo:pingcap/tidb is:issue label:"report/customer" (label:"sig/planner" OR label:"sig/execution") stats created:>=2024-01-01
```

Adjust the query rather than hardcoding different behaviors into the script. `report/customer` is a prioritization signal, not a hard requirement.

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

## TiDB high CPU investigation workflow

When the customer reports high TiDB CPU usage, use the following workflow before jumping to optimizer conclusions:

0. Treat `clinic-api` as the default entry point. If `clinic-api` is unavailable, require the user to provide the equivalent raw evidence first, including CPU profiles, query history, plans, TopSQL, statement summary, and slow query samples.
1. Define both the problematic time window and a comparable non-problematic baseline window. The baseline should preferably be from the same time-of-day pattern. Pull many TiDB CPU profiles for both sides, ideally around 50 profiles in total if the incident duration allows it.
2. Compare the problem-window and baseline CPU profiles to identify which stacks or functions consume materially more time during the incident.
3. Work backward from the hot stacks and infer what query or plan patterns could produce them. Consider optimizer, executor, compiler, GC, memory tracking, range building, and internal SQL paths instead of assuming all CPU comes from user SQL.
4. Check TopSQL, statement summary, and slow query records in the same time window. Collect the candidate SQLs and their plans, and include internal SQL in the candidate set.
5. Build a minimal candidate query set that best explains the observed CPU symptom. Use correlation analysis, principal-component style reduction, or combinational optimization to find the smallest query combination that remains highly correlated with the incident signal.
6. Compare candidate queries against the observed symptom shape. For example, CPU spikes may correlate better with GC pressure, compiler duration, plan building, or execution hot loops than with raw query count alone. Check correlation, periodicity, and dispersion instead of relying only on top-N totals.
7. If the candidate set does not explain the symptom with high confidence, go back to step 1, expand the profiling sample set, and repeat the comparison with a better baseline or a narrower incident slice.

Use this workflow to decide whether the next step should be query tuning, plan inspection, stats diagnosis, internal SQL investigation, or a product bug report.

## Tooling assumptions

- `gh` CLI must be installed and authenticated
- network access to GitHub must be available
- the output directory should be treated as generated content

## Editing guidance

- Keep curated docs in `references/` concise and topic-oriented.
- Keep generated issue corpora outside the hand-written topic docs unless they are intentionally promoted.
- If you regenerate a corpus, prefer writing into a fresh output directory or knowingly replacing the previous generated set.
