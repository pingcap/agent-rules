# Issue #65818: Analyze cannot be cancelled promptly

## Metadata
- Issue: https://github.com/pingcap/tidb/issues/65818
- Status: open
- Type: type/bug
- Created At: 2026-01-26T11:27:23Z
- Labels: affects-8.5, report/customer, severity/moderate, sig/planner, type/bug

## Customer-Facing Phenomenon
- The analyze worker blocks on RPC/NextRaw; the job does not exit promptly after kill, and the analyze execution can hang.

## Linked PRs
- Fix PR #65249: executor: fix analyze cannot be killed
  URL: https://github.com/pingcap/tidb/pull/65249
  State: open
  Merged At: not merged
  Changed Files Count: 12
  Main Modules: pkg/executor, pkg/distsql, pkg/statistics
  Sample Changed Files:
  - pkg/distsql/distsql.go
  - pkg/executor/analyze.go
  - pkg/executor/analyze_col.go
  - pkg/executor/analyze_col_v2.go
  - pkg/executor/analyze_idx.go
  - pkg/executor/analyze_test.go
  - pkg/executor/analyze_utils.go
  - pkg/executor/table_reader.go
  - pkg/executor/test/analyzetest/BUILD.bazel
  - pkg/executor/test/analyzetest/analyze_test.go
  - pkg/executor/test/analyzetest/memorycontrol/memory_control_test.go
  - pkg/statistics/handle/autoanalyze/autoanalyze.go
  PR Summary: What problem does this PR solve? Problem Summary: After #63067 removed the coprocessor-side periodic kill polling fallback in , cancellation for  and RPC paths effectively relies on the caller-provided context being canceled promptly. Analyze still had several V1 paths that entered  or RPC with  or otherwise inconsistent contexts. As a result, a kill signal could be observed before entering the RPC, but once a worker was blocked in  or RPC, some paths could not exit proactively. What changed and how does it work?

## Notes
- This issue is still open. Use this file as a reminder list for customer-driven gaps that still need a fix or a completed rollout.
