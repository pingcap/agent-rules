# How To: Control TiFlash and MPP Execution

These variables control whether and how TiDB uses TiFlash (the columnar storage engine) and MPP (Massively Parallel Processing) for query execution. Use them to route analytical queries to TiFlash, force MPP execution, or prevent TiFlash from being used when it's not appropriate.

## Variables at a glance

| Variable | Default | What it controls |
|----------|---------|-----------------|
| `tidb_allow_mpp` | ON | Master switch for MPP execution |
| `tidb_enforce_mpp` | OFF | Force all eligible queries to use MPP |
| `tidb_isolation_read_engines` | tikv,tiflash,tidb | Which storage engines the optimizer can use |
| `tidb_enable_tiflash_cop` | ON | Allow TiFlash coprocessor (non-MPP) requests |

## How TiFlash execution works

TiDB can read from TiFlash in two modes:

1. **MPP mode**: TiFlash nodes collaborate to execute the query in parallel (shuffles, joins, aggregations happen on TiFlash). Best for analytical queries.
2. **Cop mode**: TiDB sends coprocessor requests to TiFlash, similar to how it reads from TiKV. Simpler but less powerful — no cross-node shuffles.

The optimizer chooses between TiKV and TiFlash based on cost estimation. These variables let you override that choice.

## When to use each variable

### Route an analytical session entirely to TiFlash

**Symptom:** You're running analytical queries (aggregations, joins on large tables, GROUP BY) and want to ensure they use TiFlash's columnar storage and MPP execution.

**What to do:**

```sql
-- Force all reads to TiFlash and enable MPP
SET tidb_isolation_read_engines = 'tiflash';
SET tidb_enforce_mpp = ON;
```

**Benefit:** All table reads go to TiFlash, and the optimizer uses MPP execution for joins, aggregations, and shuffles. This can be orders of magnitude faster for analytical queries on large datasets.

**Caution:** This will fail for tables that don't have TiFlash replicas. Only use this in sessions where you know all queried tables are replicated to TiFlash.

### Let the optimizer choose, but allow TiFlash

**Symptom:** You want the optimizer to consider both TiKV and TiFlash and pick the cheaper option. This is the default behavior.

**What to do:**

```sql
-- These are the defaults — set them explicitly if a previous session changed them
SET tidb_isolation_read_engines = 'tikv,tiflash,tidb';
SET tidb_allow_mpp = ON;
SET tidb_enforce_mpp = OFF;
```

**Benefit:** The optimizer uses cost-based selection. Small point queries go to TiKV; large analytical queries go to TiFlash when the cost is lower.

### Prevent TiFlash from being used

**Symptom:** TiFlash is deployed in the cluster but you want certain sessions (e.g., OLTP application connections) to never use it, to avoid unexpected latency from TiFlash access.

**What to do:**

```sql
-- Remove TiFlash from the engine list
SET tidb_isolation_read_engines = 'tikv,tidb';
```

**Benefit:** Guarantees all reads go to TiKV. Useful for OLTP sessions where you want predictable latency and TiFlash access would be suboptimal.

### TiFlash cop requests are overloading TiFlash

**Symptom:** High-frequency small queries are sent to TiFlash as cop (coprocessor) requests instead of MPP. TiFlash CPU spikes from handling many individual cop requests. Dashboard shows high TiFlash cop request volume.

**What to do:**

```sql
-- Disable TiFlash cop mode — queries will either use MPP or fall back to TiKV
SET GLOBAL tidb_enable_tiflash_cop = OFF;
```

**Benefit:** Prevents TiDB from sending lightweight coprocessor requests to TiFlash. Queries that would have used TiFlash in cop mode will either:
- Use MPP if eligible (better for analytical queries)
- Fall back to TiKV (better for small OLTP queries)

**When to keep it ON:** If you have queries that benefit from TiFlash's columnar reads but don't qualify for MPP (e.g., simple single-table scans without joins or aggregations).

### Force MPP for a specific analytical query

**What to do:**

```sql
-- Per-query approach
SELECT /*+ SET_VAR(tidb_enforce_mpp=ON) */
  region, SUM(amount), COUNT(*)
FROM orders
GROUP BY region;
```

**Benefit:** Forces MPP execution for this single query without affecting other queries in the session.

## Common tuning recipes

### Dedicated analytical session

```sql
SET tidb_isolation_read_engines = 'tiflash';
SET tidb_enforce_mpp = ON;
SET tidb_mem_quota_query = 4294967296;  -- 4 GB for large analytical queries
```

### Mixed HTAP workload — optimizer chooses

```sql
SET tidb_isolation_read_engines = 'tikv,tiflash,tidb';
SET tidb_allow_mpp = ON;
SET tidb_enforce_mpp = OFF;
```

### Pure OLTP session — no TiFlash

```sql
SET tidb_isolation_read_engines = 'tikv,tidb';
```

## Diagnostic workflow

### 1. Check if TiFlash is being used

```sql
EXPLAIN ANALYZE SELECT ...;
-- Look for "tiflash" in the store column or "ExchangeSender/ExchangeReceiver" operators (MPP)
```

### 2. Check if TiFlash replicas exist

```sql
SELECT * FROM information_schema.tiflash_replica WHERE TABLE_SCHEMA = 'mydb';
```

### 3. If TiFlash is available but not chosen

```sql
-- Check current engine settings
SELECT @@tidb_isolation_read_engines;
SELECT @@tidb_allow_mpp;

-- Try forcing it to compare performance
SET tidb_enforce_mpp = ON;
EXPLAIN ANALYZE SELECT ...;
```

## General guidance

- `tidb_allow_mpp = ON` is required for any MPP execution. If it's OFF, `tidb_enforce_mpp` has no effect.
- `tidb_enforce_mpp` forces MPP but won't make unsupported operations work on TiFlash. If a query uses functions or operators not supported by TiFlash, it falls back.
- `tidb_isolation_read_engines` is the most powerful control — it completely removes engines from consideration. Use it for session-level workload isolation.
- TiFlash is almost always better for large scans, aggregations, and joins. TiKV is almost always better for point lookups and small range scans. Let the optimizer choose unless you have a clear reason to override.
