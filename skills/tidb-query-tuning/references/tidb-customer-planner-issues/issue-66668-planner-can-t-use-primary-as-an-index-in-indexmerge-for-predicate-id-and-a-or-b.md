# Issue #66668: planner: can't use primary as an index in IndexMerge for predicate `id=? and (a=? or b=?)`

## Metadata
- Issue: https://github.com/pingcap/tidb/issues/66668
- Status: open
- Type: type/enhancement
- Created At: 2026-03-04T02:53:02Z
- Labels: plan-rewrite, report/customer, sig/planner, type/enhancement

## Customer-Facing Phenomenon
- Enhancement See the example below, we can use IndexMerge for the second plan, but can't for the first plan:

## Linked PRs
- Fix PR #66670: pkg/planner: allow primary key as IndexMerge partial path for `id=? and (a=? or b=?)`
  URL: https://github.com/pingcap/tidb/pull/66670
  State: open
  Merged At: not merged
  Changed Files Count: 3
  Main Modules: tests/integrationtest, pkg/planner/core
  Sample Changed Files:
  - pkg/planner/core/indexmerge_unfinished_path.go
  - tests/integrationtest/r/planner/core/indexmerge_path.result
  - tests/integrationtest/t/planner/core/indexmerge_path.test
  PR Summary: What problem does this PR solve? Problem Summary: IndexMerge cannot use the primary key as a partial path for predicates like . For example,  falls back to TableRangeScan instead of IndexMerge, while  works correctly. What changed and how does it work? In , the table path (primary key for clustered tables) was skipped whenever  returned nil. For conditions such as , each DNF branch (, ) is first handled separately, and the top-level  is merged later. Because  alone cannot build a valid range on primary key ,  failed and the table path was always skipped, so it never got the merged filters. **Fix:** Only skip the table path when  (int-handle tables). For common-handle/clustered tables,  holds the primary key index, so we keep the gradual filter collection and allow filters like  to be merge

## Notes
- This issue is still open. Use this file as a reminder list for customer-driven gaps that still need a fix or a completed rollout.
