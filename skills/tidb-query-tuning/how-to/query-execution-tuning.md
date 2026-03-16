# How To: Tune Query Execution (Joins, Scans & Rewrites)

These variables control how TiDB executes joins, scans, and internal query rewrites. Use them when the optimizer picks the wrong join strategy, join order, or fails to apply beneficial rewrites.

## Variables at a glance

| Variable | Default | What it controls |
|----------|---------|-----------------|
| `tidb_opt_prefer_range_scan` | OFF | Prefer range scans over full table scans |
| `tidb_opt_enable_hash_join` | ON | Master switch for hash join |
| `tidb_index_join_batch_size` | 25000 | Batch size for index join outer side |
| `tidb_hash_join_concurrency` | 5 | Parallel hash join workers |
| `tidb_opt_insubq_to_join_and_agg` | ON | Rewrite IN subqueries to joins |
| `tidb_opt_derive_topn` | ON | Push TopN through joins/projections |
| `tidb_opt_enable_late_materialization` | ON | Delay column reads until after filtering |
| `tidb_opt_advanced_join_hint` | OFF (older clusters) | Enable advanced join hint syntax |
| `tidb_opt_join_reorder_threshold` | 0 | Join count threshold for greedy vs DP reorder |
| `tidb_enable_outer_join_reorder` | ON | Allow outer join reordering |

## When to use each variable

### The optimizer picks hash join but index join would be faster

**Symptom:** A join query builds a large hash table in memory when the inner table has a selective index on the join key. `EXPLAIN ANALYZE` shows HashJoin with high build time.

**What to do:**

```sql
-- Option 1: Increase index join batch size to improve throughput
SET tidb_index_join_batch_size = 50000;

-- Option 2: Disable hash join entirely (use sparingly)
SET tidb_opt_enable_hash_join = OFF;
```

**Benefit:** Index join probes the inner table via its index for each batch of outer rows. When the inner index is selective, this avoids building a large hash table and uses less memory.

**Caution:** Disabling hash join globally is rarely the right answer. Prefer per-query hints (`INL_JOIN`) or cost factors instead. Only use `tidb_opt_enable_hash_join = OFF` when you're certain no query in the session benefits from hash join.

### Hash joins are slow because of low parallelism

**Symptom:** Hash join is the right strategy, but execution is slower than expected. The TiDB node has idle CPU during the join phase.

**What to do:**

```sql
SET tidb_hash_join_concurrency = 8;  -- or higher, up to available cores
```

**Benefit:** More workers build and probe the hash table in parallel, improving throughput on multi-core machines with large joins.

### The optimizer underestimates filter selectivity and chooses full scans

**Symptom:** A query with a WHERE clause that filters most rows still uses a TableFullScan instead of a range scan. The stats may not reflect recent data changes.

**What to do:**

```sql
SET tidb_opt_prefer_range_scan = ON;
```

**Benefit:** Forces the optimizer to prefer range scans even when the cost estimate says a full scan is cheaper. This is a useful safety net when statistics are known to be imprecise.

**When to turn it off:** Once statistics are refreshed (`ANALYZE TABLE`), re-evaluate whether this is still needed. It can hurt queries where a full scan genuinely is cheaper.

### IN subquery rewrite produces a worse plan

**Symptom:** A query with `WHERE col IN (SELECT ...)` gets rewritten to a join with aggregation, but the rewritten plan is slower — for example, the join explodes the row count before aggregation reduces it.

**What to do:**

```sql
SET tidb_opt_insubq_to_join_and_agg = OFF;
```

**Benefit:** Keeps the subquery as a semi-join or correlated subquery, which can be more efficient when the subquery result set is small.

### Late materialization hurts a scan-heavy query

**Symptom:** Rarely, delaying column reads until after filtering can be counterproductive — for example, when the filter eliminates very few rows and the extra read step adds overhead.

**What to do:**

```sql
SET tidb_opt_enable_late_materialization = OFF;
```

**Benefit:** Fetches all columns in a single pass. Only disable this if you've confirmed via `EXPLAIN ANALYZE` that late materialization adds overhead for your specific query pattern.

### Join order is wrong for multi-table queries

**Symptom:** The optimizer picks a join order that processes the largest table first, or pairs tables in an order that produces large intermediate results.

**What to do:**

```sql
-- Lower the threshold to use dynamic-programming (DP) reorder for more joins
-- DP is more thorough but slower to plan; greedy is faster but less optimal
SET tidb_opt_join_reorder_threshold = 0;  -- 0 = always use DP (default)

-- If an upgrade caused a regression with outer join reordering:
SET tidb_enable_outer_join_reorder = OFF;
```

**Benefit:** DP-based reorder evaluates more join orderings and finds better plans for complex multi-join queries. Disabling outer join reorder can fix regressions where the optimizer incorrectly reorders outer joins after a version upgrade.

### Advanced join hints don't work on an upgraded cluster

**Symptom:** You're using advanced join hint syntax (e.g., `LEADING`, `HASH_JOIN_BUILD`) but they're ignored. The cluster was upgraded from an older version where `tidb_opt_advanced_join_hint` defaults to OFF.

**What to do:**

```sql
-- Enable globally after upgrade
SET GLOBAL tidb_opt_advanced_join_hint = ON;

-- Or per-query
SELECT /*+ SET_VAR(tidb_opt_advanced_join_hint=1) LEADING(t1, t2) */ ...
```

**Benefit:** Unlocks the full set of join hints including `LEADING()`, `HASH_JOIN_BUILD()`, and `HASH_JOIN_PROBE()`.

## Common tuning recipes

### High-throughput batch join session

```sql
SET tidb_hash_join_concurrency = 8;
SET tidb_index_join_batch_size = 50000;
SET tidb_distsql_scan_concurrency = 30;
```

### OLTP session where range scans should always win

```sql
SET tidb_opt_prefer_range_scan = ON;
SET tidb_opt_enable_late_materialization = ON;
```

## General guidance

- Always validate changes with `EXPLAIN ANALYZE` before and after.
- Prefer per-query hints or `SET_VAR` over session variables when the fix is query-specific.
- Session variables affect all queries in the connection — be careful in connection-pooled environments.
- These variables interact with cost factors: if you've also adjusted `tidb_opt_*_cost_factor` variables, test the combined effect.
