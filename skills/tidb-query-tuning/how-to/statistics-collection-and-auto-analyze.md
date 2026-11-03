# How To: Tune Statistics Collection and Auto Analyze

These variables control how TiDB collects, refreshes, and maintains table statistics. Good statistics are the foundation of good query plans — if the optimizer doesn't know your data distribution, it can't pick the right join order, access path, or execution engine.

## Variables at a glance

| Variable | Default | What it controls |
|----------|---------|-----------------|
| `tidb_analyze_version` | 2 | Stats collection algorithm (v1 or v2) |
| `tidb_analyze_column_options` | PREDICATE | Which columns to collect stats for |
| `tidb_analyze_skip_column_types` | blob,mediumblob,longblob,json | Column types to exclude from stats |
| `tidb_auto_analyze_ratio` | 0.5 | Row-change threshold to trigger auto analyze |
| `tidb_auto_analyze_concurrency` | 1 (v8.5+) | Parallel auto analyze jobs |
| `tidb_auto_build_stats_concurrency` | 1 | Parallel stats building tasks |
| `tidb_build_sampling_stats_concurrency` | 2 | Parallel column sampling workers |
| `tidb_auto_analyze_partition_batch_size` | 128 | Partitions per analyze batch |
| `tidb_merge_partition_stats_concurrency` | 1 | Parallel global stats merge workers |
| `tidb_analyze_distsql_scan_concurrency` | 2 | Scan concurrency for analyze |
| `tidb_sysproc_scan_concurrency` | 1 | System process scan concurrency |
| `tidb_enable_async_merge_global_stats` | OFF | Async merge for partitioned table stats |
| `tidb_enable_historical_stats` | OFF | Store historical stats snapshots |
| `tidb_enable_stats_owner` | ON | Whether this TiDB node runs analyze jobs |
| `tidb_max_auto_analyze_time` | 43200 (12h) | Max time for a single auto analyze job |

## Common scenarios

### Stats are going stale faster than auto analyze can refresh them

**Symptom:** `SHOW STATS_HEALTHY` shows tables in the unhealthy range ([0, 60]) and the count is growing over time. Dashboard shows Auto Analyze Query Per Minute frequently drops to zero while stale tables exist.

**What to do:**

```sql
-- Step 1: Lower the trigger threshold so analyze starts sooner
SET GLOBAL tidb_auto_analyze_ratio = 0.3;  -- trigger at 30% row change (default 0.5)
```

**Benefit:** Tables become eligible for auto analyze earlier, preventing stats from decaying to the point where plans degrade.

**Caution:** Lowering this too aggressively (e.g., 0.1) means more frequent analyze runs. Only lower it when TiDB and TiKV still have headroom.

### Auto analyze is triggered but finishes too slowly

**Symptom:** `SHOW ANALYZE STATUS` shows long-running analyze jobs. The backlog keeps growing despite analyze tasks running.

**What to do:**

```sql
-- Increase parallel analyze jobs (v8.5+)
SET GLOBAL tidb_auto_analyze_concurrency = 3;

-- Increase parallel stats building
SET GLOBAL tidb_auto_build_stats_concurrency = 4;

-- Increase scan concurrency for analyze
SET GLOBAL tidb_analyze_distsql_scan_concurrency = 4;
```

**Benefit:** More parallel work means higher analyze throughput. Multiple tables or partitions can be analyzed simultaneously.

**Important:** These parameters are multiplicative. `auto_analyze_concurrency * auto_build_stats_concurrency * build_sampling_stats_concurrency` is the effective parallelism. Keep this within what TiDB CPU can sustain — overdoing it creates contention and makes analyze slower.

### Wide tables are slow to analyze

**Symptom:** Tables with many columns take a long time to analyze, even though most columns aren't used in WHERE clauses.

**What to do:**

```sql
-- Only collect stats for columns that appear in predicates
SET GLOBAL tidb_analyze_column_options = 'PREDICATE';

-- Skip large, low-value column types
SET GLOBAL tidb_analyze_skip_column_types = 'json,blob,mediumblob,longblob,text,mediumtext,longtext';

-- Increase column sampling parallelism for the remaining columns
SET GLOBAL tidb_build_sampling_stats_concurrency = 4;
```

**Benefit:** Reduces the volume of data that analyze must process. Skipping JSON/blob columns avoids reading large values that don't contribute to plan quality.

**When to use ALL instead of PREDICATE:** If your workload is analytical (OLAP) with varied query shapes, use `tidb_analyze_column_options = 'ALL'` to ensure the optimizer has full coverage. `PREDICATE` works best for stable OLTP workloads.

### Partitioned tables dominate the analyze backlog

**Symptom:** Tables with hundreds or thousands of partitions take a long time because each partition is analyzed individually, then global stats are merged.

**What to do:**

```sql
-- Increase partition batch size
SET GLOBAL tidb_auto_analyze_partition_batch_size = 256;

-- Enable async global stats merge (reduces memory spikes)
SET GLOBAL tidb_enable_async_merge_global_stats = ON;

-- Increase merge concurrency
SET GLOBAL tidb_merge_partition_stats_concurrency = 4;

-- Increase partition-level build concurrency
SET GLOBAL tidb_auto_build_stats_concurrency = 4;
```

**Benefit:** Larger batches reduce the number of merge rounds. Async merge prevents memory spikes. Higher concurrency processes more partitions in parallel.

### Analyze jobs interfere with business traffic

**Symptom:** TiKV latency or CPU increases when analyze is running. Business queries slow down during analyze windows.

**What to do:**

```sql
-- Option 1: Dedicate specific TiDB nodes to stats work
-- On business-serving TiDB nodes:
SET GLOBAL tidb_enable_stats_owner = OFF;

-- On dedicated stats TiDB nodes:
SET GLOBAL tidb_enable_stats_owner = ON;
```

```sql
-- Option 2: Reduce scan concurrency to limit TiKV pressure
SET GLOBAL tidb_analyze_distsql_scan_concurrency = 1;
SET GLOBAL tidb_sysproc_scan_concurrency = 1;
```

**Benefit:** Stats-owner isolation ensures analyze work doesn't compete with latency-sensitive SQL. Reducing scan concurrency limits the read bandwidth analyze consumes from TiKV.

**Important:** Do not disable `tidb_enable_stats_owner` on ALL TiDB nodes — this effectively disables cluster-wide auto analyze.

### Cluster is on stats v1 or mixed versions

**Symptom:** `SELECT @@tidb_analyze_version` returns 1, or different tables have stats collected with different versions.

**What to do:**

```sql
-- Switch to v2
SET GLOBAL tidb_analyze_version = 2;

-- Re-analyze critical tables
ANALYZE TABLE db.table1;
ANALYZE TABLE db.table2;
```

**Benefit:** Stats v2 has better estimation for skewed data, better out-of-range handling, and more efficient sampling. It's been the default since TiDB 6.5.

### You want to cap how long a single analyze job can run

**What to do:**

```sql
-- Default is 43200 seconds (12 hours)
SET GLOBAL tidb_max_auto_analyze_time = 7200;  -- 2 hours
```

**Benefit:** Prevents a single runaway analyze job from blocking the analyze queue for hours. Jobs that exceed the limit are cancelled and retried later.

### Historical stats are consuming too much memory

**What to do:**

```sql
SET GLOBAL tidb_enable_historical_stats = OFF;
```

**Benefit:** Stops TiDB from storing historical stats snapshots, reducing memory pressure. Only enable this if you have a specific operational need to compare stats across time periods.

## Recommended tuning order

1. **Confirm stats v2** — highest-impact single change
2. **Set column coverage policy** — `PREDICATE` for OLTP, `ALL` for OLAP
3. **Exclude memory-heavy column types** — `tidb_analyze_skip_column_types`
4. **Tune the trigger threshold** — `tidb_auto_analyze_ratio`
5. **Tune concurrency** — only after policy choices are correct
6. **Handle partitioned tables** — async merge, partition batch size
7. **Isolate stats work** — dedicated TiDB nodes if needed

## General guidance

- Change one variable at a time and observe the effect over hours, not minutes.
- Use dashboard trends (`Stats Healthy Distribution`, `Auto Analyze Duration`) to judge improvement.
- Always add TiKV background read rate limiting before aggressively increasing analyze scan concurrency.
- Re-check query plans after major stats tuning changes — plan choices can legitimately change.
