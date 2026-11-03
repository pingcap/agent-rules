# How To: Manage Statistics Loading and Freshness

These variables control how TiDB handles missing or outdated statistics during query optimization. They determine whether the optimizer waits for complete stats before planning, and what happens when stats are stale.

## Variables at a glance

| Variable | Default | What it controls |
|----------|---------|-----------------|
| `tidb_stats_load_sync_wait` | 100 (ms) | Max wait time for on-demand stats loading during optimization |
| `tidb_enable_pseudo_for_outdated_stats` | OFF | Whether to fall back to pseudo stats when real stats are outdated |

## When to use each variable

### Query plans are unstable after TiDB restart

**Symptom:** The first wave of queries after a TiDB restart gets different (often worse) plans than steady-state traffic. Plans stabilize after a few minutes as stats are loaded into memory.

**What to do:**

```sql
-- Increase the sync-load wait budget so the optimizer waits longer for stats
SET GLOBAL tidb_stats_load_sync_wait = 200;  -- 200ms (default is 100ms)
```

**Benefit:** The optimizer waits longer for complete column statistics to load before compiling a plan. This produces more stable plans during warm-up at the cost of slightly higher compilation latency.

**When to increase further:** If `Statistics -> Sync Load QPS` on the dashboard shows frequent timeouts, the wait budget is too short. Increase gradually (200 → 500 → 1000ms) until timeouts are rare.

**When to decrease:** If compilation latency is a concern and you're running a recent TiDB version (v8.2+) with adaptive stats-load concurrency, the loading path may already be fast enough to use a lower budget.

### Sync load timeouts are frequent and sustained

**Symptom:** The dashboard shows a high sustained rate of sync-load timeouts, not just occasional spikes. Plans are frequently compiled against incomplete stats.

**What to do:**

```sql
-- First, increase the wait budget
SET GLOBAL tidb_stats_load_sync_wait = 500;
```

If that's not enough:
- On versions before v8.2: increase `stats-load-concurrency` in the TiDB configuration file
- On v8.2+: set `stats-load-concurrency = 0` to enable adaptive concurrency based on CPU cores

**Benefit:** More worker capacity means stats are loaded faster, so the optimizer is less likely to time out waiting.

### Plans silently degrade when stats become stale

**Symptom:** After bulk data changes (large INSERTs, DELETEs, or partition operations), query plans degrade but there are no warnings or errors. The optimizer silently uses pseudo statistics.

**What to do:**

```sql
-- Ensure pseudo stats are disabled (this is the default since newer versions)
SET GLOBAL tidb_enable_pseudo_for_outdated_stats = OFF;
```

**Benefit:** When OFF, TiDB uses the real (albeit outdated) statistics rather than falling back to pseudo stats. This is almost always better because:
- Real outdated stats are still closer to reality than pseudo stats
- The optimizer produces warnings about stale stats, making the problem visible
- You can then address the root cause (run `ANALYZE TABLE` or tune auto analyze)

**When you might set it ON:** Almost never. The only case is if outdated stats are so wrong that they produce worse plans than pseudo stats — this is extremely rare.

## Diagnostic workflow

### 1. Check if stats freshness is causing plan issues

```sql
-- Check stats health for the relevant tables
SHOW STATS_HEALTHY WHERE Db_name = 'mydb' AND Table_name = 'mytable';

-- If health is low, refresh stats
ANALYZE TABLE mydb.mytable;

-- Check if the plan improves
EXPLAIN ANALYZE SELECT ...;
```

### 2. Check if sync load is a bottleneck

Look at the TiDB dashboard:
- `Statistics -> Sync Load QPS` — if timeouts are frequent, increase `tidb_stats_load_sync_wait`
- `Statistics -> Sync Load Duration` — if durations are near the timeout, the budget is too tight

### 3. After restart, verify warm-up behavior

```sql
-- Immediately after restart, check a critical query's plan
EXPLAIN SELECT ...;

-- Wait 30 seconds, check again
EXPLAIN SELECT ...;

-- If plans differ, the warm-up period is too long — increase sync wait or upgrade
```

## Interaction with other settings

- **`tidb_auto_analyze_ratio`**: Controls when auto analyze triggers. If stats decay faster than auto analyze runs, you'll see more stale-stats issues regardless of these loading variables. See the [Statistics Collection guide](statistics-collection-and-auto-analyze.md).
- **force-init-stats**: A TiDB configuration option (not a session variable) that makes TiDB wait for full stats initialization before serving traffic. Use it when the first queries after restart must be stable.
- **Stats version**: These loading variables work with both stats v1 and v2, but v2 loads more efficiently.

## General guidance

- Keep `tidb_enable_pseudo_for_outdated_stats = OFF` — this is the safe default.
- Start with `tidb_stats_load_sync_wait = 100` and only increase if you see sync-load timeouts.
- If you're on an older TiDB version and seeing restart-time plan drift, upgrading is usually a better fix than tuning these variables.
- After changing stats loading behavior, validate first-query latency and plan stability for your critical queries.
