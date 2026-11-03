# How To: Tune the Cost Model and Index Selection

These variables control the foundational cost model that the optimizer uses to compare plans, and how it evaluates index access paths. Adjusting them changes how the optimizer weighs sequential vs random I/O, which cost model version is active, and how it handles edge cases in index selection.

## Variables at a glance

| Variable | Default | What it controls |
|----------|---------|-----------------|
| `tidb_cost_model_version` | 2 | Which cost model the optimizer uses |
| `tidb_opt_seek_factor` | 20 | Cost multiplier for random I/O seeks |
| `tidb_opt_ordering_index_selectivity_threshold` | 0 | Threshold for preferring an ordering index |
| `tidb_opt_range_max_size` | 67108864 (64 MB) | Max memory for range construction |

## When to use each variable

### Plans are suboptimal after upgrading from an old TiDB version

**Symptom:** After upgrading, some queries get worse plans. The cluster may still be using cost model v1.

**What to do:**

```sql
-- Check current version
SELECT @@tidb_cost_model_version;

-- Switch to v2 (default since TiDB 6.2)
SET GLOBAL tidb_cost_model_version = 2;
```

**Benefit:** Cost model v2 is more accurate for modern TiDB. It better estimates the cost of TiKV vs TiFlash access, handles wide tables more accurately, and produces better plans for most workloads.

**Caution:** Switching cost model versions can change many query plans at once. Test on a non-production environment first, or roll out gradually with session-level testing on critical queries.

### The optimizer keeps choosing index lookups over full scans on large analytical queries

**Symptom:** For queries that scan most of a table, the optimizer still picks an index lookup path. The random I/O from index lookups is slower than a sequential full scan would be.

**What to do:**

```sql
-- Increase seek factor to make random I/O more expensive
SET tidb_opt_seek_factor = 40;  -- default is 20
```

**Benefit:** A higher seek factor tells the optimizer that random I/O is relatively more expensive compared to sequential I/O. This pushes it toward sequential scans and away from index lookups when a large portion of the table is being read.

**When to lower it:** On fast SSD/NVMe storage where random I/O is nearly as fast as sequential, you might lower the seek factor (e.g., 5-10) to encourage more index-based access paths.

### ORDER BY ... LIMIT queries pick a bad ordering index

**Symptom:** A query like `SELECT ... FROM t WHERE <filter> ORDER BY col LIMIT 10` uses an index on `col` to avoid sorting, but the filter is poorly selective on that index, causing it to scan many rows before finding matches.

**What to do:**

```sql
-- Set a selectivity threshold; the optimizer will only use the ordering index
-- if it estimates the filter selectivity is better than this threshold
SET tidb_opt_ordering_index_selectivity_threshold = 0.1;  -- 10% selectivity
```

**Benefit:** Prevents the optimizer from choosing an ordering index when the filter would require scanning too many rows through that index. Instead, it will use a more selective index and add an explicit sort, which is faster overall.

**Typical values:** Start with 0 (disabled, the default) and increase gradually. Values between 0.01 and 0.2 are common. The right value depends on your data distribution and query patterns.

### Queries with huge IN lists fall back to full index scans

**Symptom:** A query like `SELECT * FROM t WHERE id IN (1, 2, 3, ..., 100000)` unexpectedly uses an IndexFullScan instead of point lookups. The optimizer ran out of memory constructing the range.

**What to do:**

```sql
-- Increase the memory budget for range construction
SET tidb_opt_range_max_size = 134217728;  -- 128 MB (default is 64 MB)
```

**Benefit:** Allows the optimizer to construct larger range sets, so queries with many IN-list values or complex range conditions can still use efficient point lookups instead of falling back to a full scan.

**Caution:** Increasing this too much can cause high memory usage during query optimization. Only raise it if you have specific queries that need it, and monitor TiDB memory usage.

### Queries with large IN lists on non-critical paths

If raising `tidb_opt_range_max_size` globally is too risky, use per-query scope:

```sql
SELECT /*+ SET_VAR(tidb_opt_range_max_size=134217728) */ *
FROM orders WHERE id IN (/* large list */);
```

## Diagnostic workflow

1. **Check cost model version first** — this is the single highest-impact variable. If you're on v1, switch to v2 before tuning anything else.

2. **Look at EXPLAIN output for unexpected access paths:**
   - IndexLookUp on analytical queries → raise `tidb_opt_seek_factor`
   - Ordering index with poor filter → set `tidb_opt_ordering_index_selectivity_threshold`
   - IndexFullScan with large IN list → check `tidb_opt_range_max_size`

3. **Validate with EXPLAIN ANALYZE** — compare actual rows scanned, execution time, and memory usage before and after the change.

## General guidance

- `tidb_cost_model_version` should be set globally and consistently across the cluster. Mixed versions make diagnosis harder.
- `tidb_opt_seek_factor` reflects your storage characteristics. Set it once based on your hardware and leave it.
- `tidb_opt_ordering_index_selectivity_threshold` and `tidb_opt_range_max_size` are best applied per-query or per-session for specific problem queries rather than globally.
