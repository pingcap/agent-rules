# How To: Manage Plan Stability with SQL Plan Baselines

These variables control TiDB's SQL Plan Management (SPM) feature, which lets you lock query plans to prevent regressions. Use them when you need to guarantee that a critical query always uses a known-good plan, regardless of stats changes, upgrades, or optimizer behavior changes.

## Variables at a glance

| Variable | Default | What it controls |
|----------|---------|-----------------|
| `tidb_enable_plan_baselines` | ON | Capture plan baselines automatically |
| `tidb_use_plan_baseline` | ON | Use captured baselines when available |
| `tidb_mem_quota_binding_cache` | 67108864 (64 MB) | Memory limit for the binding cache |

## How SQL Plan Baselines work

1. **Capture**: When `tidb_enable_plan_baselines = ON`, TiDB records the execution plan for each query the first time it's seen.
2. **Bind**: The captured plan becomes a baseline. You can also create bindings manually.
3. **Enforce**: When `tidb_use_plan_baseline = ON`, the optimizer checks for a matching baseline before planning. If one exists, it uses the bound plan instead of re-optimizing.

This means:
- New plans are captured as they appear
- Existing baselines prevent plan drift
- You can manually bind a specific plan to override the optimizer

## When to use each variable

### Prevent plan regressions after stats refresh or upgrade

**Symptom:** A critical query's plan changes after `ANALYZE TABLE` runs or after a TiDB version upgrade. The new plan is slower.

**What to do:**

```sql
-- 1. Ensure baselines are active (these are the defaults)
SET GLOBAL tidb_enable_plan_baselines = ON;
SET GLOBAL tidb_use_plan_baseline = ON;

-- 2. Manually create a binding for the critical query using the known-good plan
CREATE GLOBAL BINDING FOR
  SELECT * FROM orders WHERE status = 'pending' ORDER BY created_at
USING
  SELECT /*+ USE_INDEX(orders, idx_status_created) */ * FROM orders WHERE status = 'pending' ORDER BY created_at;
```

**Benefit:** The optimizer will always use the bound plan for this query, regardless of cost estimation changes. This is the strongest guarantee of plan stability.

### Temporarily disable baselines to debug a plan issue

**Symptom:** You suspect a baseline is forcing a suboptimal plan. You want to see what the optimizer would choose without baselines.

**What to do:**

```sql
-- Disable baseline usage for this session
SET tidb_use_plan_baseline = OFF;

-- Check the plan the optimizer would choose naturally
EXPLAIN ANALYZE SELECT ...;

-- Compare with the baseline plan
SET tidb_use_plan_baseline = ON;
EXPLAIN ANALYZE SELECT ...;
```

**Benefit:** Lets you compare the baseline plan with the optimizer's current best plan to determine if the baseline is still optimal.

### Global bindings are overriding per-query hints

**Symptom:** You've added hints to a specific query, but they're being ignored. A global binding for the same query pattern takes precedence.

**What to do:**

```sql
-- Check existing bindings
SHOW GLOBAL BINDINGS WHERE Original_sql LIKE '%orders%';

-- Option 1: Drop the conflicting binding
DROP GLOBAL BINDING FOR SELECT * FROM orders WHERE ...;

-- Option 2: Disable baselines for this session to let hints work
SET tidb_enable_plan_baselines = OFF;
```

**Benefit:** Removes the conflict between manual hints and automatic bindings. Per-query hints are more precise and should take precedence for targeted tuning.

### The binding cache is too small for a large number of bindings

**Symptom:** Some bindings are being evicted from cache. The log shows binding cache quota warnings. Queries intermittently don't use their expected plans.

**What to do:**

```sql
-- Increase the binding cache quota
SET GLOBAL tidb_mem_quota_binding_cache = 134217728;  -- 128 MB (default is 64 MB)
```

**Benefit:** More bindings can be cached in memory, ensuring they're available when queries are compiled.

**When to increase:** When you have many distinct query patterns with bindings (hundreds or thousands). Check the binding count:

```sql
SELECT COUNT(*) FROM mysql.bind_info WHERE status = 'enabled';
```

### Stop capturing new baselines but keep using existing ones

**Symptom:** You have a stable set of bindings and don't want new ones to be created automatically, which could lock in a bad plan.

**What to do:**

```sql
-- Stop automatic capture but keep enforcing existing baselines
SET GLOBAL tidb_enable_plan_baselines = OFF;
SET GLOBAL tidb_use_plan_baseline = ON;
```

**Benefit:** Existing bindings continue to stabilize plans, but no new plans are automatically captured. New query patterns get the optimizer's natural cost-based selection.

## Diagnostic workflow

### 1. Check if a binding exists for your query

```sql
SHOW GLOBAL BINDINGS WHERE Original_sql LIKE '%your_table%';
```

### 2. Check if the binding is being used

```sql
EXPLAIN SELECT ...;
-- Look for "Using binding: true" in the output
```

### 3. Check binding cache health

```sql
-- Check memory usage
SHOW GLOBAL BINDINGS;

-- Check for eviction warnings in TiDB logs
```

### 4. Evolve a binding to a better plan

```sql
-- If the optimizer finds a better plan, you can evolve the binding:
-- First, drop the old binding
DROP GLOBAL BINDING FOR SELECT ...;

-- Then either let auto-capture create a new one, or manually bind the better plan
CREATE GLOBAL BINDING FOR
  SELECT ...
USING
  SELECT /*+ desired hints */ ...;
```

## Common tuning recipes

### Lock down critical queries before an upgrade

```sql
-- Before upgrading, create explicit bindings for your top critical queries
CREATE GLOBAL BINDING FOR <query1> USING <query1 with hints>;
CREATE GLOBAL BINDING FOR <query2> USING <query2 with hints>;

-- Verify they're active
SHOW GLOBAL BINDINGS;
```

### Clean up stale bindings

```sql
-- Find bindings that haven't been used recently
SELECT original_sql, update_time FROM mysql.bind_info
WHERE status = 'enabled' ORDER BY update_time ASC;

-- Drop ones that are no longer needed
DROP GLOBAL BINDING FOR <old_query>;
```

## General guidance

- Baselines are most valuable for critical, high-frequency queries where plan stability matters more than plan optimality.
- For exploratory or ad-hoc queries, baselines can prevent the optimizer from finding better plans as data changes. Consider disabling capture for analytical workloads.
- Manually created bindings override auto-captured ones. Use manual bindings for your most critical queries.
- After a major TiDB upgrade, review your bindings — the optimizer may now produce better plans that your bindings are preventing.
- The binding cache is shared across all connections. Size it based on your total number of active bindings, not per-connection.
