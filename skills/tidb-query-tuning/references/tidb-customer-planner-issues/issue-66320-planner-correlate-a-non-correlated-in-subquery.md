# Issue #66320: Planner: correlate a non-correlated IN subquery

## Metadata
- Issue: https://github.com/pingcap/tidb/issues/66320
- Status: open
- Type: type/bug
- Created At: 2026-02-21T00:19:21Z
- Labels: report/customer, severity/moderate, sig/planner, type/bug

## Customer-Facing Phenomenon
- TiDB can "decorrelate" a correlated subquery today, but cannot correlate a subquery that was originally non-correlated.

## Linked PRs
- Fix PR #66206: planner: correlate subquery rule
  URL: https://github.com/pingcap/tidb/pull/66206
  State: open
  Merged At: not merged
  Changed Files Count: 22
  Main Modules: pkg/planner/core, pkg/session, pkg/bindinfo, pkg/planner
  Sample Changed Files:
  - pkg/bindinfo/binding_auto_test.go
  - pkg/planner/core/BUILD.bazel
  - pkg/planner/core/casetest/rule/BUILD.bazel
  - pkg/planner/core/casetest/rule/main_test.go
  - pkg/planner/core/casetest/rule/rule_correlate_test.go
  - pkg/planner/core/casetest/rule/testdata/correlate_suite_in.json
  - pkg/planner/core/casetest/rule/testdata/correlate_suite_out.json
  - pkg/planner/core/casetest/rule/testdata/correlate_suite_xut.json
  - pkg/planner/core/core_init.go
  - pkg/planner/core/exhaust_physical_plans.go
  - pkg/planner/core/expression_rewriter.go
  - pkg/planner/core/find_best_task.go
  - pkg/planner/core/operator/logicalop/logical_join.go
  - pkg/planner/core/operator/physicalop/base_physical_plan.go
  - pkg/planner/core/optimizer.go
  - pkg/planner/core/optimizer_test.go
  - pkg/planner/core/rule/logical_rules.go
  - pkg/planner/core/rule_correlate.go
  - pkg/planner/util/utilfuncp/func_pointer_misc.go
  - pkg/sessionctx/vardef/tidb_vars.go
  PR Summary: What problem does this PR solve? Problem Summary: What changed and how does it work? Claude code review: Detailed PR Review: Cost-Based Selection Between Join and Apply for Non-Correlated IN Subqueries

## Notes
- This issue is still open. Use this file as a reminder list for customer-driven gaps that still need a fix or a completed rollout.
