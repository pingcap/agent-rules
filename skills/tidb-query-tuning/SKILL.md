# TiDB Query Tuning

**name:** tidb-query-tuning

**description:** Diagnose and optimize slow TiDB queries using optimizer hints, session variables, join strategy selection, subquery optimization, and index tuning. Use when a query is slow, produces a bad plan, or needs performance guidance on TiDB.

---

## Workflow

1. **Capture the current plan:**
   - Run `EXPLAIN ANALYZE <query>` to get actual execution stats.
   - Compare `estRows` vs `actRows` — large divergence means stale or missing statistics.
   - Note the most expensive operators (wall time, memory, rows processed).

2. **Check statistics health:**
   - `SHOW STATS_HEALTHY WHERE Db_name = '<db>' AND Table_name = '<table>';`
   - If health < 80 or `actRows` diverges significantly from `estRows`, run `ANALYZE TABLE <table>;` and re-check the plan.
   - For specific indexes: `ANALYZE TABLE <table> INDEX <index_name>;`

3. **Identify the bottleneck pattern:**
   - **Bad join order or strategy** → see `references/join-strategies.md`
   - **Subquery not handled well** → see `references/subquery-optimization.md`
   - **Wrong or missing index** → see `references/index-selection.md`
   - **Optimizer choosing a suboptimal plan despite good stats** → see `references/optimizer-hints.md` and `references/session-variables.md`

4. **Apply the fix:**
   - Prefer the least invasive change: refresh stats → add index → hint → session variable.
   - Use hints when the fix is query-specific.
   - Use session variables when the fix applies to a workload pattern.

5. **Verify the improvement:**
   - Re-run `EXPLAIN ANALYZE` with the fix applied.
   - Confirm `actRows` and execution time improved.
   - If the fix is a hint, document it in a SQL comment so future readers understand why.

## High-signal rules

- **Always check stats first.** Most bad plans in TiDB come from stale or missing statistics, not optimizer bugs.
- **`EXPLAIN ANALYZE` is the ground truth.** `EXPLAIN` alone shows estimates; `ANALYZE` shows what actually happened.
- **Correlated subqueries:** TiDB decorrelates by default. When the subquery is well-indexed and the outer query is selective, `NO_DECORRELATE()` often wins. See `references/subquery-optimization.md`.
- **Join strategies matter:** TiDB supports hash join, index join, merge join, and shuffle joins. The right choice depends on table sizes, index availability, and data distribution. See `references/join-strategies.md`.
- **Hints are per-query; variables are per-session/global.** Use hints for surgical fixes, variables for workload-wide tuning.
- **TiFlash acceleration:** For analytical queries on large tables, push computation to TiFlash replicas using `READ_FROM_STORAGE(TIFLASH[<table>])`. See `references/session-variables.md`.

## References

- `references/optimizer-hints.md` — Optimizer hints: syntax, catalog, and when to use each.
- `references/session-variables.md` — Session/global variables that affect plan choice.
- `references/join-strategies.md` — Join algorithms, when TiDB picks each, and how to override.
- `references/subquery-optimization.md` — Decorrelation, semi-join, EXISTS/IN patterns and NO_DECORRELATE.
- `references/index-selection.md` — Index hints, invisible indexes, index advisor, composite index guidance.
- `references/explain-patterns.md` — Reading EXPLAIN ANALYZE output to identify bottlenecks.
