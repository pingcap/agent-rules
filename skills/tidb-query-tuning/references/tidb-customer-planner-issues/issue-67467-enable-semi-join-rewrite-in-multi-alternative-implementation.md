# Issue #67467: enable semi_join_rewrite in multi alternative implementation

## Metadata
- Issue: https://github.com/pingcap/tidb/issues/67467
- Status: open
- Type: type/enhancement
- Created At: 2026-03-31T12:41:16Z
- Labels: report/customer, sig/planner, type/enhancement

## Customer-Facing Phenomenon
- bad plan In real customer env, the final result is zero(IndexJoin_181 output 0 rows), most of time is spent to compute the outer side of , because will keep all rows from , and is a very large table(almost 3,000,000 rows after the filter of .

## Linked PRs
- No linked PR was found from the issue timeline.

## Notes
- This issue is still open. Use this file as a reminder list for customer-driven gaps that still need a fix or a completed rollout.
