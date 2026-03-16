---
name: tidb-query-tuning
description: Diagnose and optimize slow TiDB queries using optimizer hints, session variables, join strategy selection, subquery optimization, and index tuning. Use when a query is slow, produces a bad plan, or needs performance guidance on TiDB.
---

# TiDB Query Tuning

Use this skill to diagnose and resolve TiDB query performance issues. It follows a rigorous workflow from symptom identification to verified solution.

---

## Workflow

1. **Capture the current plan & clues:**
   - Run `EXPLAIN ANALYZE <query>` to get actual execution stats.
   - Compare `estRows` vs `actRows` — large divergence means stale or missing statistics.
   - Note the most expensive operators (wall time, memory, rows processed).
   - **Use PLAN REPLAYER**: Run `PLAN REPLAYER DUMP EXPLAIN [ANALYZE] <query>;` to export comprehensive on-site information (version, config, stats, plan) to a ZIP file.
   - **Use Debug API**: Use TiDB HTTP API (port 10080) to pull runtime info: `/debug/pprof`, `/stats/dump/{db}/{table}`, or `/schema/{db}/{table}`.
   - **Check Bindings**: Run `SHOW GLOBAL BINDINGS;` to see if existing plan baselines are affecting the query.

2. **Check statistics health:**
   - `SHOW STATS_HEALTHY WHERE Db_name = '<db>' AND Table_name = '<table>';`
   - If health < 80 or `actRows` diverges significantly from `estRows`, run `ANALYZE TABLE <table>;` (or with `ALL COLUMNS` if `@@tidb_analyze_column_options` is not `ALL`) and re-check the plan.
   - For specific indexes: `ANALYZE TABLE <table> INDEX <index_name>;`

3. **Identify the bottleneck pattern:**
   - **Bad join order or strategy** → see `references/join-strategies.md`
   - **Subquery not handled well** → see `references/subquery-optimization.md`
   - **Wrong or missing index** → see `references/index-selection.md`
   - **Optimizer choosing a suboptimal plan despite good stats** → see `references/optimizer-hints.md` and `references/session-variables.md`
   - **Stats are stale or auto analyze cannot keep up** → see `references/stats-health-and-auto-analyze.md`
   - **Plans change after restart or sync stats loading times out** → see `references/stats-loading-and-startup.md`
   - **Need to tune analyze version, column coverage, or memory-heavy stats collection** → see `references/stats-version-and-analyze-configuration.md`
   - **Need a matching field incident, workaround, or fixed-version precedent** → search `references/optimizer-oncall-experiences-redacted/`
   - **Need recent customer issue precedents with linked PRs and merge timestamps** → search `references/tidb-customer-planner-issues/`

4. **Reproduce & Investigate locally:**
   - **Local Reproduction**: Use `tiup playground` and `PLAN REPLAYER LOAD` to reproduce the issue locally. See `references/plan-replayer-testing.md`.
   - **Test Versions**: Verify the fix in newer stable versions or `nightly`.
   - **Deep Code Analysis**: If the cause is still unclear, clone `pingcap/tidb` and analyze the source code. **Read AGENTS.md and .agents/skills in the TiDB repo first.**

5. **Apply the fix:**
   - Prefer the least invasive change: refresh stats → add index → SQL Binding → hint → session variable.
   - **SQL Binding**: Fix plans without code changes: `CREATE GLOBAL BINDING FOR <stmt> USING <hinted_stmt>;`.
   - **Hints & Variables**: Use hints when the fix is query-specific; use session variables when it applies to a workload pattern.
   - **Bug Report**: If it's a confirmed bug, follow the workflow in `references/bug-report.md`. **Anonymize all sensitive data** before reporting.

6. **Verify the improvement:**
   - Re-run `EXPLAIN ANALYZE` with the fix applied.
   - Confirm `actRows` and execution time improved.
   - If the fix is a hint, document it in a SQL comment so future readers understand why.

## High-signal rules

- **Always check stats first.** Most bad plans in TiDB come from stale or missing statistics, not optimizer bugs.
- **Treat stats maintenance as capacity planning.** If `AUTO ANALYZE` cannot keep up with stats decay, plan quality will drift even when SQL does not change.
- **`EXPLAIN ANALYZE` is the ground truth.** `EXPLAIN` alone shows estimates; `ANALYZE` shows what actually happened.
- **Search known field cases before inventing a new workaround.** The oncall corpus under `references/optimizer-oncall-experiences-redacted/` is useful for symptom matching, investigation signals, and fix-version lookup.
- **Search recent GitHub issue precedents when fix lineage matters.** The corpus under `references/tidb-customer-planner-issues/` is useful when you need linked PRs, merge times, and still-open customer gaps.
- **Correlated subqueries:** TiDB decorrelates by default. When the subquery is well-indexed and the outer query is selective, `NO_DECORRELATE()` often wins. See `references/subquery-optimization.md`.
- **Join strategies matter:** TiDB supports hash join, index join, merge join, and shuffle joins. The right choice depends on table sizes, index availability, and data distribution. See `references/join-strategies.md`.
- **Hints are per-query; variables are per-session/global.** Use hints for surgical fixes, variables for workload-wide tuning.
- **TiFlash acceleration:** For analytical queries on large tables, push computation to TiFlash replicas using `READ_FROM_STORAGE(TIFLASH[<table>])`. See `references/session-variables.md`.
- **Anonymize sensitive info.** Before reporting bugs, ensure table names, columns, and data are anonymized.
- **Reproduce before suggesting upgrades.** Use TiUP playground to verify if a newer version actually fixes the issue.

## References

- `references/clues.md` — Detailed SQLs and metrics for clue collection.
- `references/reproduction.md` — Baseline investigation and known version issues.
- `references/plan-replayer-testing.md` — Local reproduction using TiUP and PLAN REPLAYER.
- `references/bug-report.md` — Standard bug report template and anonymization workflow.
- `references/optimizer-hints.md` — Optimizer hints: syntax, catalog, and when to use each.
- `references/session-variables.md` — Session/global variables that affect plan choice.
- `references/join-strategies.md` — Join algorithms, when TiDB picks each, and how to override.
- `references/subquery-optimization.md` — Decorrelation, semi-join, EXISTS/IN patterns and NO_DECORRELATE.
- `references/index-selection.md` — Index hints, invisible indexes, index advisor, composite index guidance.
- `references/explain-patterns.md` — Reading EXPLAIN ANALYZE output to identify bottlenecks.
- `references/stats-health-and-auto-analyze.md` — Statistics health, auto analyze backlog diagnosis, and safe concurrency tuning.
- `references/stats-loading-and-startup.md` — Init stats, sync load, restart-time plan instability, and version-based mitigation.
- `references/stats-version-and-analyze-configuration.md` — Stats versioning, analyze coverage, and memory-safe stats collection settings.
- `references/optimizer-oncall-experiences-redacted/` — Redacted optimizer oncall case corpus with user symptoms, investigation signals, workarounds, and fixed versions.
- `references/tidb-customer-planner-issues/README.md` — Generated GitHub issue corpus with one file per customer-driven planner issue, including linked PRs and merge timestamps.

## Scripts

- `scripts/collect_diag_info.sql` — SQL script to collect baseline tuning metadata.
