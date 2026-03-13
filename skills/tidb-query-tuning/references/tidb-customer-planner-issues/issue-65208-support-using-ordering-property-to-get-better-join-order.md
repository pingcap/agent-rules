# Issue #65208: support using ordering property to get better join order

## Metadata
- Issue: https://github.com/pingcap/tidb/issues/65208
- Status: open
- Type: type/enhancement
- Created At: 2025-12-24T02:53:56Z
- Labels: report/customer, sig/planner, type/enhancement

## Customer-Facing Phenomenon
- The better plan: choose join order of  and use , so we can leverage the ordering property and only need to get 1000 rows from Join output.

## Linked PRs
- Fix PR #63522: planner: Allow leading ordered table to survive (WIP)
  URL: https://github.com/pingcap/tidb/pull/63522
  State: open
  Merged At: not merged
  Changed Files Count: 11
  Main Modules: pkg/planner/core, pkg/session
  Sample Changed Files:
  - pkg/planner/core/exhaust_physical_plans.go
  - pkg/planner/core/find_best_task.go
  - pkg/planner/core/operator/logicalop/logical_join.go
  - pkg/planner/core/operator/physicalop/physical_index_join.go
  - pkg/planner/core/operator/physicalop/physical_topn.go
  - pkg/planner/core/plan_cost_ver2.go
  - pkg/planner/core/rule_join_reorder.go
  - pkg/planner/core/rule_join_reorder_greedy.go
  - pkg/sessionctx/vardef/tidb_vars.go
  - pkg/sessionctx/variable/session.go
  - pkg/sessionctx/variable/sysvar.go
  PR Summary: What problem does this PR solve? Problem Summary: What changed and how does it work?

## Notes
- This issue is still open. Use this file as a reminder list for customer-driven gaps that still need a fix or a completed rollout.
