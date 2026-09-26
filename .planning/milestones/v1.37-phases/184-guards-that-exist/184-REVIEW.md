---
phase: 184-guards-that-exist
reviewed: 2026-09-11T00:00:00Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - CLAUDE.md
  - firestarter/PROTOCOLS.md
  - firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp
  - firestarter_app/tests/fixtures/planted_no_exists_proxy.py
  - firestarter_app/tests/scan_paths.py
  - firestarter_app/tests/test_scan_paths_resolve.py
  - firestarter_app/tools/check_no_exists_proxy.py
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
---

# Phase 184: Code Review Report

**Reviewed:** 2026-09-11
**Depth:** standard
**Files Reviewed:** 7
**Status:** clean

## Summary

Phase 184 is claim-hygiene work: one new fail-closed pytest guard
(`test_every_scan_path_resolver_is_an_existing_tests_module` in
`firestarter_app/tests/test_scan_paths_resolve.py`), a corresponding removal of
a rotted `ScanPathEntry` from `firestarter_app/tests/scan_paths.py`, a
docstring/prose re-anchor of `_FLOOR`'s justification and two stale count
figures, and four prose-only repairs (two docstring re-dates in the
`check_no_exists_proxy.py` fixture pair, one retirement sentence in
`firestarter/PROTOCOLS.md`, one `tools/` state sentence in `CLAUDE.md`, and
one false clause deleted from a C++ comment). No production logic changed
outside the one new test function.

I traced the new test against every item on the review's focus list and
against the actual file tree, not just the source text:

- **Not vacuous.** An empty `resolved_by` tuple is explicitly caught
  (`test_scan_paths_resolve.py:175-180`) before the per-value loop runs, so it
  cannot pass by having nothing to iterate. An empty `CROSS_REPO_TEST_PATHS`
  tuple itself is guarded by the separate, pre-existing
  `test_inventory_is_non_vacuous` (`_FLOOR = 6`) — the phase deliberately did
  not duplicate that guard into the new test, matching the project's
  no-duplicate-census-assertion convention documented in this same file's
  module docstring.
- **Structural, not existence-derived.** The `is_bare` predicate
  (`test_scan_paths_resolve.py:182-187`) rejects `""`, `"."`, `".."`, any
  value containing `/` or `\`, and any value where `Path(value).name != value`
  — before any filesystem check runs. I confirmed this is what actually
  caught the real rotted entry: `ae92dd1`'s commit message documents an
  observed RED against `"tools/wiki/dispatch_mirror.py (meta repo; relocated
  by 168-10)"` (rejected on the `/` check, not on absence).
  `test_dispatch/test_configure_memory.cpp`'s own now-orphaned entry is gone
  from `scan_paths.py` as of that same commit.
- **`is_file()`, not `exists()`.** Line 196 uses `.is_file()`, so a same-named
  directory under `tests/` would still fail.
- **Collects all offenders, asserts once.** `offenders` accumulates across
  the full double loop; a single `assert not offenders` at the end reports
  every violation together (lines 173-207).
- **Scoped to `firestarter_app/tests/` only.** `_TESTS_DIR = _APP_REPO_ROOT /
  "tests"` (line 55); never resolves into the sibling firmware repo.
- **No pytest marker, no skip path.** The function carries no `@requires_fw`
  or other marker — it needs no firmware checkout, so none is warranted, and
  none is present to let it silently downgrade to SKIP.
- **Count figures verified against the live tuples, not just read.** I ran
  the actual code: `CROSS_REPO_TEST_PATHS` has 6 entries and
  `CROSS_REPO_TOOL_RESOLVERS` has 11, matching `_FLOOR = 6`,
  `scan_paths.py`'s corrected "6 paths" prose (was "8 paths", both instances
  fixed, confirmed no stale "8 paths" text remains), and the existing
  `assert len(CROSS_REPO_TOOL_RESOLVERS) == 11`. I also verified every one of
  the 8 `resolved_by` bare filenames named across the 6 `CROSS_REPO_TEST_PATHS`
  entries actually exists under `firestarter_app/tests/`, and every one of the
  11 tool filenames in `CROSS_REPO_TOOL_RESOLVERS` exists under
  `firestarter_app/tools/`. I ran `pytest tests/test_scan_paths_resolve.py`
  and `python tools/check_no_exists_proxy.py` directly; both pass (5/5, and a
  clean 78-file `PASS:` respectively).
- **No escape hatches.** No allowlist, marker, `# noqa`, or `startswith()`
  bypass anywhere in the new check — fail-closed as intended.

I also checked the two files outside the explicit new-logic path:

- `check_no_exists_proxy.py` and `planted_no_exists_proxy.py` diffs are
  docstring/comment text only (re-dating a citation to the now-deleted
  `test_dispatch_mirror.py`); the AST-scanning behavior and the three planted
  fixture subjects are byte-for-byte unchanged where it matters (only prose
  lines differ). Confirmed by re-running the tool against the real tree.
- `firestarter/PROTOCOLS.md`'s corrected sentence ("no tool machine-reads
  this document ... retired ... no automated dispatch guard exists now") is
  accurate against the actual repo history (`5426d7ef` retired the
  `tools/wiki/` checkers).
- `CLAUDE.md`'s corrected sentence about `tools/` (meta repo) was checked
  against the live tree: `tools/` here does in fact contain only `catalog/`,
  and `.planning/v1.35/MIGRATION-TABLE.md` does exist at the path the new
  sentence names.
- `test_configure_memory.cpp`'s one-clause comment deletion ("one row per
  `KNOWN_PROTOCOLS` entry") removes a claim without touching any assertion,
  `RUN_TEST` registration, or table data — a no-op for test behavior.

No count/census assertion was added to the new check, no project-forbidden
comment was introduced into `firestarter/` or `firestarter_app/` source, and
nothing in this phase's diff touches build, CI, or dispatch logic.

All reviewed files meet quality standards. No issues found.
