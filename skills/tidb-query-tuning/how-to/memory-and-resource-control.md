# How To: Control Memory and Resource Usage

These variables control how much memory and parallelism TiDB uses when executing queries. Use them to prevent OOM kills, manage resource contention between queries, and tune throughput for batch workloads.

## Variables at a glance

| Variable | Default | What it controls |
|----------|---------|-----------------|
| `tidb_mem_quota_query` | 1073741824 (1 GB) | Memory limit per query |
| `tidb_max_chunk_size` | 1024 | Max rows per execution chunk |
| `tidb_distsql_scan_concurrency` | 15 | Parallel TiKV coprocessor scan requests |

## When to use each variable

### Queries are being killed with "Out Of Memory" errors

**Symptom:** Queries fail with `Out Of Memory Quota!` errors. The TiDB log shows memory quota exceeded.

**What to do:**

```sql
-- Option 1: Increase the per-query memory limit
SET tidb_mem_quota_query = 2147483648;  -- 2 GB

-- Option 2: Increase globally for all connections
SET GLOBAL tidb_mem_quota_query = 2147483648;
```

**Benefit:** Allows memory-intensive queries (large joins, aggregations, sorts) to complete without hitting the memory limit.

**Caution:** Raising this too high risks TiDB node OOM if multiple large queries run concurrently. Calculate the safe limit as:

```
safe_limit = (TiDB_available_memory * 0.7) / max_concurrent_heavy_queries
```

**Better alternatives to consider first:**
- Optimize the query to use less memory (better indexes, push-down filters)
- Use TiFlash for analytical queries that process large datasets
- Add `ORDER BY ... LIMIT` to reduce result set size

### Queries need more memory temporarily for a batch job

**Symptom:** A scheduled batch job needs more memory than the default allows, but you don't want to raise the limit cluster-wide.

**What to do:**

```sql
-- Set for this session only
SET tidb_mem_quota_query = 4294967296;  -- 4 GB

-- Run the batch job
INSERT INTO summary_table SELECT ... FROM large_table GROUP BY ...;

-- Reset (or just close the connection)
SET tidb_mem_quota_query = 1073741824;
```

**Benefit:** Gives the batch job the memory it needs without affecting other connections.

### Scan-heavy queries are too slow

**Symptom:** Analytical queries or batch jobs that scan large tables are slow. TiDB is not fully utilizing TiKV read bandwidth. `EXPLAIN ANALYZE` shows long scan times.

**What to do:**

```sql
-- Increase scan parallelism
SET tidb_distsql_scan_concurrency = 30;  -- default is 15
```

**Benefit:** More concurrent coprocessor requests to TiKV means faster data retrieval. Each request scans a different range of data in parallel.

**When to increase:** When TiKV has spare read bandwidth and the query is scan-bound (most time is spent in TableReader/IndexReader).

**When to decrease:** When TiKV is under pressure from too many concurrent scan requests, or when you want to limit the impact of one query on others. For OLTP workloads with many concurrent small queries, the default of 15 is usually sufficient.

### Queries use too much memory on wide tables

**Symptom:** Queries on tables with many columns or large column values use more memory than expected, even with reasonable result set sizes.

**What to do:**

```sql
-- Reduce chunk size to lower per-batch memory usage
SET tidb_max_chunk_size = 256;  -- default is 1024
```

**Benefit:** Smaller chunks mean less data is held in memory at once during execution. Each processing step works on fewer rows, reducing peak memory usage.

**Trade-off:** Smaller chunks mean more processing iterations, which can reduce throughput. Only lower this when memory is the constraint, not speed.

### High-throughput batch processing needs larger chunks

**Symptom:** A batch ETL job or analytical query has plenty of memory headroom but throughput is lower than expected. CPU utilization is moderate.

**What to do:**

```sql
SET tidb_max_chunk_size = 4096;  -- or higher
SET tidb_distsql_scan_concurrency = 30;
```

**Benefit:** Larger chunks amortize per-batch overhead and improve CPU efficiency. Combined with higher scan concurrency, this maximizes throughput for data-intensive operations.

## Common tuning recipes

### Conservative OLTP session (protect the cluster)

```sql
SET tidb_mem_quota_query = 536870912;    -- 512 MB
SET tidb_max_chunk_size = 512;
SET tidb_distsql_scan_concurrency = 10;
```

### Aggressive batch/ETL session (maximize throughput)

```sql
SET tidb_mem_quota_query = 4294967296;   -- 4 GB
SET tidb_max_chunk_size = 4096;
SET tidb_distsql_scan_concurrency = 30;
```

### Mixed workload — limit impact of one heavy query

```sql
-- Per-query via SET_VAR
SELECT /*+ SET_VAR(tidb_mem_quota_query=2147483648) SET_VAR(tidb_distsql_scan_concurrency=20) */ *
FROM large_table WHERE ...;
```

## General guidance

- `tidb_mem_quota_query` is your primary defense against runaway queries. Don't raise it globally without understanding your concurrency profile.
- `tidb_distsql_scan_concurrency` directly affects TiKV read pressure. Monitor TiKV CPU and I/O when increasing it.
- `tidb_max_chunk_size` is a throughput-vs-memory trade-off. The default of 1024 is a good balance for most workloads.
- In connection-pooled environments, session-level changes persist for the life of the connection. Reset variables after batch jobs or use per-query `SET_VAR`.
