# Issue #67363: planner: better binding matching mechanism

## Metadata
- Issue: https://github.com/pingcap/tidb/issues/67363
- Status: open
- Type: type/enhancement
- Created At: 2026-03-27T08:27:00Z
- Labels: report/customer, sig/planner, type/enhancement

## Customer-Facing Phenomenon
- See the example below, the second query can't hit the binding because is wrapped by , so it has a different SQL digest. It's better to loose the matching mechanism and allow the second query to hit the binding as well:

## Linked PRs
- No linked PR was found from the issue timeline.

## Notes
- This issue is still open. Use this file as a reminder list for customer-driven gaps that still need a fix or a completed rollout.
