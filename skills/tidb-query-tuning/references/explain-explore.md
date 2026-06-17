# TiDB EXPLAIN EXPLORE Slow Query Workflow

## Purpose

Help a user investigate a TiDB slow query with real evidence:

1. Collect the slow SQL, schema, plan, stats, and workload context.
2. Use `EXPLAIN EXPLORE` to discover historical and generated plan candidates.
3. Use LLM reasoning to compare candidate plans and explain tradeoffs.
4. Ask whether shortlisted candidates may be verified with `EXPLAIN ANALYZE`.
5. Recommend either the verified best plan or, if verification is not allowed, the most likely best plan from static evidence.

## Guardrails

- Do not run expensive or mutating commands without explicit user approval.
- Use only non-ANALYZE `EXPLAIN EXPLORE` for candidate discovery.
- Do not use `EXPLAIN EXPLORE ANALYZE` for ranking; it is intentionally out of scope because it can be too heavy.
- `EXPLAIN ANALYZE <candidate SQL>` is allowed only after asking the user and receiving explicit approval.
- Do not execute `CREATE GLOBAL BINDING`, `DROP GLOBAL BINDING`, `ANALYZE TABLE`, DDL, or SQL rewrites unless the user explicitly asks.
- Never claim the slow query is fixed without before/after evidence.
- Do not recommend a binding, index, or stats refresh from estimated cost alone; explain the evidence and uncertainty.
- Always include rollback SQL for any binding recommendation.
- For production, ask for explicit approval before any mutating SQL or heavyweight validation.

## Evidence Checklist

Ask for or collect the smallest useful evidence set:

- TiDB version and whether this is production, staging, or a replay environment.
- Slow SQL text, normalized SQL, or 64-character SQL digest.
- Slow-log fields if available: `Digest`, `Plan_digest`, `Query_time`, `Process_time`, `Wait_time`, `Process_keys`, `Total_keys`, `Result_rows`.
- Current plan: `EXPLAIN FORMAT = 'brief' <SQL>`.
- Schema for involved tables: `SHOW CREATE TABLE`.
- Existing relevant bindings: `SHOW GLOBAL BINDINGS` and any matching `original_sql`, `bind_sql`, `plan_digest`, and status.
- Stats health and freshness: `SHOW STATS_HEALTHY`, `SHOW STATS_META`, relevant `SHOW STATS_HISTOGRAMS`, and plan markers such as `stats:pseudo`, `stats:partial[...]`, or `allEvicted`.
- Plan replayer zip if live reproduction is unsafe or unavailable.

## Expected Workflow

1. Run non-ANALYZE `EXPLAIN EXPLORE <SQL>` to get more plan candidates.
2. Choose a small shortlist of likely good candidates from plan shape and the ranking rules below.
3. Ask the user whether it is acceptable to run `EXPLAIN ANALYZE <candidate SQL>` for the shortlisted candidates.
4. If the user approves:
   - run `EXPLAIN ANALYZE` only for the shortlisted candidates;
   - compare actual runtime, actual rows, scan rows, and plan shape;
   - recommend the best verified candidate.
5. If the user does not approve:
   - do not run runtime validation;
   - recommend the most likely best candidate from static evidence;
   - clearly label it as an unverified/static recommendation.

## EXPLAIN EXPLORE Commands

Use one of these forms depending on the input:

```sql
EXPLAIN EXPLORE '<sql text or sql digest>';
EXPLAIN EXPLORE SELECT ...;
EXPLAIN EXPLORE REPLAYER '<path/to/replayer.zip>';
```

Current codebase notes:

- Parser support is in `pkg/parser/parser.y`.
- AST fields are `ExplainStmt.Explore`, `ExplainStmt.SQLDigest`, and `ExplainStmt.ReplayerFile`.
- Runtime rendering is in `pkg/planner/core/common_plans.go`.
- Candidate exploration is in `pkg/bindinfo/binding_auto.go` and `pkg/bindinfo/binding_plan_generation.go`.
- Replayer loading for explore is in `pkg/executor/plan_replayer.go`.
- A string payload that is 64 characters and contains no space is treated as a SQL digest; otherwise it is parsed as SQL text.
- `EXPLAIN EXPLORE SELECT ...` currently targets `SelectStmt`.
- `EXPLAIN EXPLORE REPLAYER ...` loads the replayer file and explores the target SQL extracted from it.
- Do not claim feature availability across TiDB versions without checking the target branch.

## Repo Evidence Map

Use these code paths when refreshing or debugging this skill:

- `pkg/planner/core/common_plans.go`: output columns and `renderResultForExplore`.
- `pkg/bindinfo/binding_auto.go`: historical plans, generated plans, and `IsSimplePointPlan`.
- `pkg/bindinfo/binding_plan_generation.go`: candidate generation by optimizer vars, fix-controls, leading hints, index hints, and `NO_DECORRELATE`.
- `pkg/bindinfo/binding_plan_evolution.go`: current rule-based recommender; LLM predictor is a TODO.
- `pkg/bindinfo/binding_auto_test.go`: expected generated candidates, empty/zero execution columns without ANALYZE, simple point-plan rule.
- `pkg/bindinfo/testdata/binding_auto_suite_out.json`: sample generated plan shapes.
- `pkg/planner/core/plan_cost_ver2.go`: cost intuition for scans, lookup, sort, TopN, aggregation, and joins.
- `pkg/planner/core/find_best_task.go`: skyline pruning heuristics for access paths: property match, access predicates, equal/IN prefix, index-back scan, pseudo stats, and risk.

## How To Read The Result

Compare these output columns first:

- `statement`: original SQL being explored.
- `binding_hint`: hint set for the candidate.
- `plan`: plan text for the candidate.
- `plan_digest`: unique digest of the candidate plan.
- `recommend`, `reason`: built-in recommendation signal; treat it as a hint, not proof.
- `explain_analyze`: generated by TiDB; run it only for shortlisted candidates after user approval.
- `binding`: generated global binding SQL for the candidate.

Ignore all execution-info columns output by non-ANALYZE `EXPLAIN EXPLORE`; do not use them for ranking:

- `avg_latency`
- `exec_times`
- `avg_scan_rows`
- `avg_returned_rows`
- `latency_per_returned_row`
- `scan_rows_per_returned_row`

## Static Candidate Ranking Rules

Use these rules to rank candidates from non-ANALYZE `EXPLAIN EXPLORE`. Treat the result as a best plan-shape hypothesis, not runtime proof.

1. Start with hard static wins.
   - A simple `Point_Get` or `Batch_Point_Get` with only `Selection` or `Projection` above it is the strongest plan-shape signal.
   - `TableDual` or impossible-range plans are best only when they are semantically expected.
   - Avoid plans containing `CARTESIAN` unless the SQL truly has no join predicate.
2. Compare estimated cardinality, but discount weak stats.
   - Prefer lower `estRows` at the access operators and after major joins/aggregations.
   - If the better estimate depends on `stats:pseudo`, `stats:partial[...]`, or `allEvicted`, lower confidence and ask for stats evidence.
   - If all candidates have similar `estRows`, do not rank by the root estimate alone; inspect access path and operator work.
3. Rank access paths.
   - Prefer bounded `IndexRangeScan`, `TableRangeScan`, `Point_Get`, or `Batch_Point_Get` over `TableFullScan` for selective predicates.
   - Prefer covering `IndexReader` or index-only plans over `IndexLookUp` when the required columns are in the index.
   - Prefer `IndexLookUp` only when the index range is tight and the table-side `TableRowIDScan` estimate is small.
   - Do not blindly prefer an index lookup over a table scan: for broad ranges, many selected columns, or estimates near the full table, table scan can be cheaper than double-read.
   - Treat `IndexFullScan` as weaker than `IndexRangeScan` unless it provides ordering or covering access that avoids a worse scan/sort.
   - Treat `IndexMerge` as promising only when multiple selective branches greatly reduce rows; otherwise keep confidence medium because row estimates can be fragile.
4. Prefer earlier filtering and pushdown.
   - A predicate represented as an index `range` is better than a cop `Selection`; cop `Selection` is usually better than root `Selection`.
   - Prefer pushed-down `TopN`, aggregation, and filters when they reduce rows before returning to root.
   - Penalize plans that scan many rows then filter late at root.
5. Compare join shape.
   - For `HashJoin`, prefer a smaller `Build` side because it builds the hash table; a large build side increases memory risk.
   - For `IndexJoin` / `IndexHashJoin` / `IndexMergeJoin`, prefer when the driver side is small and the inner/probe side uses a bounded index range such as `range: decided by [eq(...)]`.
   - Penalize index joins with a large outer side, large per-key inner estimates, many ranges, or double-read table probes.
   - Prefer `HashJoin` for large symmetric inputs when there is no selective index driver.
   - Prefer `MergeJoin` when both sides already provide order with `keep order:true`; penalize it if it requires extra `Sort`.
   - Avoid join orders that multiply large intermediate row counts early.
6. Compare ordering, limit, and aggregation work.
   - Prefer plans satisfying `ORDER BY` / `GROUP BY` through index order (`keep order:true`) when that avoids `Sort`.
   - `TopN` with small `count` is usually cheaper than full `Sort`; pushed `TopN` is better when it lowers returned rows.
   - Prefer `StreamAgg` when input is already ordered by the group keys. Prefer `HashAgg` when no natural order exists and `StreamAgg` would require sorting.
7. Consider store and task placement.
   - For small selective OLTP queries, TiKV point/range/index access is usually a stronger static signal.
   - For large scan/aggregation/join analytic shapes, TiFlash MPP can be plausible, especially when filters and joins stay in `mpp[tiflash]`.
   - Do not recommend a TiFlash plan from shape alone if table replicas, workload type, or data size are unknown.
8. Use `binding_hint` as an explanation, not the ranking source.
   - Hints show how TiDB can reproduce the candidate, but the plan tree decides whether it looks good.
   - Prefer hints that minimally force the desired access path/join order over broad cost-factor or fix-control side effects.
9. Assign confidence.
   - Strong: point-get plan, or one candidate clearly avoids full scan/cartesian/sort/double-read and has much lower reliable access estimates.
   - Medium: candidate has better access path or join order but estimates are close or stats are partial.
   - Weak: candidates rely on pseudo stats, have identical estimates, trade off different costs, or require unknown workload assumptions.

## Runtime Verification After Approval

Only use runtime evidence from separate `EXPLAIN ANALYZE <candidate SQL>` commands after the user explicitly approves them. Do not use execution-info columns from `EXPLAIN EXPLORE`.

1. Run `EXPLAIN ANALYZE` only for the shortlisted candidate SQL statements.
2. Compare actual execution evidence from those results:
   - wall-clock execution time in `execution info`;
   - `actRows` versus `estRows`;
   - processed/scan keys in cop task details;
   - memory and disk usage;
   - whether the actual plan still matches the intended candidate shape.
3. Recommend the best verified candidate only from these approved `EXPLAIN ANALYZE` results.
4. If approval is not given, skip runtime verification and keep the recommendation static/tentative.

## Decision Flow

1. Identify the baseline plan and current `Plan_digest`.
2. Compare candidate plans.
   - Ignore `EXPLAIN EXPLORE` execution-info columns because non-ANALYZE explore does not run the SQL.
   - Generated plans are hypotheses until separately verified.
   - Candidate plans with better static shape and much lower reliable access estimates are promising, but still need semantic checks.
3. Choose the likely fix category.
   - Binding: use when a better plan exists and only hints are needed.
   - Stats refresh: use when estimates look wrong or the plan contains `stats:pseudo`, `stats:partial[...]`, or `allEvicted`.
   - Index: use when all candidate plans scan too much and predicates/order/join shape need a new access path.
   - SQL rewrite: use when the SQL shape is non-sargable, returns too many rows, or blocks good plan generation.
   - No SQL fix: use when slowness appears caused by lock wait, TiKV/IO pressure, network, cache effects, or a one-off condition.
4. Validate before finalizing.
   - Ask whether `EXPLAIN ANALYZE` is allowed for the shortlisted candidates.
   - If yes, use the actual runtime evidence to choose the final recommendation.
   - If no, produce only a potential-best recommendation from static `EXPLAIN EXPLORE` evidence.

## LLM Reasoning Rules

- Explain why the recommended plan is better in database terms: access path, join order, row estimates, scan rows, selectivity, and operator cost.
- Do not invent missing schema, indexes, stats, or workload history.
- If evidence is incomplete, say exactly what is missing and mark the recommendation as tentative.
- Prefer the smallest reversible action before proposing DDL or SQL rewrites.
- Distinguish "best runtime-backed plan" from "best plan-shape hypothesis".
- Never say a generated-only candidate is definitely best. Say "most likely best from static plan shape" and explain the uncertainty.
- When asking for `EXPLAIN ANALYZE` approval, show the exact candidate SQL statements first.
- Output the top 1-3 candidates, not every candidate, unless the user asks for the full list.

## Report Format

Use this final shape:

```text
Problem:
Evidence:
Candidate plans:
Recommendation:
SQL to apply:
Rollback:
Validation:
Risks:
What is not verified:
```
