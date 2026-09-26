---
phase: 174-blast-radius-invariance-harness
reviewed: 2026-09-03T00:00:00Z
depth: standard
files_reviewed: 15
files_reviewed_list:
  - firestarter_app/tests/fixtures/report_shapes.py
  - firestarter_app/tests/fixtures/rekey_ledger.py
  - firestarter_app/tests/fixtures/planted_rekey_mutation.py
  - firestarter_app/tests/fixtures/shape_ids.json
  - firestarter_app/tests/fixtures/devtest_issue_corpus.json
  - firestarter_app/tests/fixtures/part_number_delta.json
  - firestarter_app/tests/test_blast_radius_invariance.py
  - firestarter_app/tests/test_rekey_ledger.py
  - firestarter_app/tests/test_devtest_issue_corpus.py
  - firestarter_app/tests/test_part_number_delta_drift.py
  - firestarter_app/tools/snapshot_report_shapes.py
  - firestarter_app/tools/build_devtest_issue_corpus.py
  - firestarter_app/tools/measure_part_number_delta.py
  - tools/rekey/check_rekey_ledger.py
  - .github/workflows/rekey-ledger-check.yml
findings:
  critical: 1
  warning: 4
  info: 2
  total: 7
status: issues_found
---

# Phase 174: Code Review Report

**Reviewed:** 2026-09-03T00:00:00Z
**Depth:** standard
**Files Reviewed:** 15
**Status:** issues_found

## Summary

Reviewed the blast-radius invariance harness at standard depth: the frozen report-shape corpus and its builders, the append-only re-key ledger and its meta-side checker, the 26-row filed-issue corpus gate, and the part-number-delta drift gate. All 122 pytest tests across the four test modules pass on the current tree (`pytest tests/test_blast_radius_invariance.py tests/test_rekey_ledger.py tests/test_devtest_issue_corpus.py tests/test_part_number_delta_drift.py -o addopts="" -q` → `122 passed`), and `tools/snapshot_report_shapes.py --check` currently reports no drift across all 16 committed snapshots. The engineering in this phase is unusually rigorous — every absolute-value gate documents its own anti-vacuity leg and most of them were independently verified here by reproducing the RED/GREEN transitions.

Despite that rigor, one genuine aliasing bug was found and reproduced live: two of the module's own helper functions mutate a `functools.cache`-memoized `DiagnosticReport` object's `db_diff` field in place, silently violating the module's own documented invariant that `db_diff` is `None` on a bare `build_shape()` result — for 6 of the 16 shape ids. This is exactly the class of bug CR-01 fixed once already (for `.results`/`.plan` sharing) but the fix did not cover this second aliasing path. Additional gaps were found in the completeness of GATE-05's drift protection, a duplicate-detection asymmetry in the meta-side ledger checker, and an unvalidated ambiguity risk in the corpus generator's coverage-tag "solve by trial" logic.

## Critical Issues

### CR-01: `render_shape()` and `_to_dict_with_db_diff()` mutate a cached `DiagnosticReport`'s `db_diff` in place, leaking state across all future `build_shape()` calls for 6 of 16 shape ids

**File:** `firestarter_app/tools/snapshot_report_shapes.py:92`, `firestarter_app/tests/test_blast_radius_invariance.py:404`

**Issue:** Six of the sixteen `report_shapes.py` builders are decorated with `@functools.cache` (`m27c512-full-all-ok`, `m27c512-full-blank-check-bad`, `m27c512-full-runs-1`, `at28c256-full-all-ok-sdp`, `sst27sf512-full-all-ok`, `w27e257-full-all-ok`), so every call to `build_shape(shape_id)` for one of these ids returns the *same* `DiagnosticReport` instance. `render_shape()` (the snapshot tool) and `_to_dict_with_db_diff()` (the test-module helper) both do:

```python
report = build_shape(shape_id)
report.db_diff = build_db_diff(report.auto_capture.chip, db, report.results)
```

This assigns directly onto whatever object `build_shape()` returned. For the 6 cached shape ids, that mutates the shared singleton, so every subsequent `build_shape(shape_id)` call in the same process returns an object whose `db_diff` is no longer `None` — contradicting the explicit invariant documented in both files: *"`db_diff` is `None` on a bare `build_shape()` result"* (`report_shapes.py`'s `_build_at28c256_full_all_ok_sdp` docstring area; `test_blast_radius_invariance.py:394`).

Reproduced live:
```python
from tests.fixtures.report_shapes import build_shape
r1 = build_shape('m27c512-full-all-ok')
print(r1.db_diff)               # None
from tools.snapshot_report_shapes import render_shape
render_shape('m27c512-full-all-ok')
r2 = build_shape('m27c512-full-all-ok')
print(r2.db_diff, r1 is r2)     # DbDiff(...), True
```

No test in the current suite happens to assert `db_diff is None` for one of these 6 cached ids after a `render_shape`/`_to_dict_with_db_diff` call has already run in-process, so the bug is currently masked by test ordering rather than fixed. This is precisely the shared-mutable-state hazard CR-01 (`_clone_with_chip_override`'s `copy.deepcopy` fix, `report_shapes.py:484-504`) was written to eliminate for `.results`/`.plan` — the fix did not extend to this second, independently-discovered aliasing path through `.db_diff`. Any later phase (177+) that calls `render_shape()` for a cached shape before running an assertion that depends on a fresh `build_shape()` result (e.g. a future `db_diff is None` regression test, or two snapshot generations back-to-back for the same shape with different `EpromDatabase` instances) will get silently stale data.

**Fix:** Never assign onto the object `build_shape()` returns for a cached shape id. Either (a) have both call sites build off a copy, mirroring the `_clone_with_chip_override` pattern already used elsewhere in this file:

```python
import dataclasses

def render_shape(shape_id: str) -> str:
    report = dataclasses.replace(build_shape(shape_id), results=copy.deepcopy(build_shape(shape_id).results))
    report.db_diff = build_db_diff(report.auto_capture.chip, _DB, report.results)
    ...
```

or, cleaner, (b) stop mutating the report at all — thread `db_diff` through `to_dict()` as a parameter/composition step instead of an attribute assignment, so `build_shape()`'s output is never touched by a caller. Whichever fix is chosen, add a regression test asserting `build_shape(<a cached shape id>).db_diff is None` both before and after a `render_shape()` call for that same id in the same process.

## Warnings

### WR-01: GATE-05's snapshot-drift protection covers only 1 of 16 committed report shapes in the automated test suite

**File:** `firestarter_app/tests/test_blast_radius_invariance.py:561-569`

**Issue:** `174-CONTEXT.md` scopes GATE-05 to "a frozen ... table plus its committed report corpus" (plural, the whole corpus). `tools/snapshot_report_shapes.py --check` can drift-check all 16 committed snapshots under `tests/fixtures/reports/`, but nothing in the reviewed test suite or CI configuration invokes it. The only pytest coverage is `test_committed_snapshot_matches_a_fresh_regeneration`, which calls `render_shape()` for exactly one shape id — the uncached tracer `sst27sf512-six-step`. The other 15 committed JSON files are checked only for *existence* (via `test_shape_ids_frozen_hashes_ladder_pins_and_snapshots_agree`'s filename-stem comparison), never for byte-identical content against a fresh regeneration. A change to a builder or to `to_dict()`/`build_db_diff()` that alters a non-`dedup_fingerprint` field (banner counts, transport counters, a `write_target` field, `db_diff.current_support_status`, etc.) for any of the other 15 shapes would go completely undetected by `pytest`.

**Fix:** Parametrize the snapshot-drift assertion over all of `SHAPE_IDS`, not just the tracer:

```python
@pytest.mark.parametrize("shape_id", sorted(SHAPE_IDS))
def test_committed_snapshot_matches_a_fresh_regeneration(shape_id: str) -> None:
    from tools.snapshot_report_shapes import render_shape
    target = Path(__file__).parent / "fixtures" / "reports" / f"{shape_id}.json"
    committed = json.loads(target.read_text(encoding="utf-8"))
    fresh = json.loads(render_shape(shape_id))
    assert committed == fresh
```
(Given CR-01 above, fix the aliasing bug first, since parametrizing this over the 6 cached shape ids would otherwise make the fresh-vs-committed comparison order-dependent.)

### WR-02: `check_rekey_ledger.py` silently collapses a duplicate `ledger_id` in the app-side ledger, asymmetric with its own MILESTONES.md-side duplicate guard

**File:** `tools/rekey/check_rekey_ledger.py:129`

**Issue:** `parse_milestones_rows()` explicitly raises `LedgerParseError` (exit 2) when two `MILESTONES.md` rows share a `ledger_id` (`check_rekey_ledger.py:115-118`), and this is covered by a dedicated test (`test_duplicate_milestones_row_for_one_ledger_id_fails_closed`). But the app-side ledger has no equivalent guard: `check()` builds `ledger_by_id = {row[3]: row for row in ledger_rows}` (line 129), a plain dict comprehension that silently keeps only the *last* row for a duplicated `ledger_id` and drops the earlier one from every subsequent lookup. The app-side pytest suite (`tests/test_rekey_ledger.py:test_ledger_id_values_are_unique`) does catch this today, but the meta-side checker — which is documented as the authoritative cross-tree binding check (D-13) and is designed to run even when the app-side test suite hasn't — would pass a ledger with a duplicated `ledger_id` without complaint, silently checking only one of the two colliding rows against `MILESTONES.md`.

**Fix:** Add the same fail-closed duplicate check to `check()` (or `parse_ledger()`) that `parse_milestones_rows()` already has:
```python
seen: dict[str, LedgerRow] = {}
for row in ledger_rows:
    if row[3] in seen:
        raise LedgerParseError(f"duplicate ledger_id in app-side ledger: {row[3]!r}")
    seen[row[3]] = row
```

### WR-03: `_solve_row`'s coverage-tag "solve by trial" picks the first matching candidate without checking for ambiguity

**File:** `firestarter_app/tools/build_devtest_issue_corpus.py:169-187`

**Issue:** `_solve_row()` tries `(None, "")` then `(REGION_POLICY_FULL_DEVICE, COVERAGE_TAG_FULL_DEVICE)` and returns on the *first* candidate whose recomputed hash matches `filed_hash`. If a row's step vector happened to produce the same `dedup_fingerprint` under both candidates (e.g. no `write` step present, so the coverage discriminator never gets appended either way), the function would silently record `coverage_tag=""` even when `"cov=full-device"` also reproduces — an ambiguous case resolved arbitrarily by iteration order rather than detected and reported. `validate_rows()` only checks that the recorded `recomputed_hash` equals `filed_hash`; it never checks that exactly one of the two candidates matched.

**Fix:** Collect all matching candidates before returning, and raise `CorpusValidationError` naming the issue if more than one candidate reproduces the filed hash, so ambiguity surfaces as a build failure rather than a silently-arbitrary choice:
```python
matches = []
for coverage_policy, coverage_tag_value in (...):
    ...
    if recomputed == filed_hash:
        matches.append((real_repeat_policy_tag(report.results), coverage_tag_value, recomputed))
if len(matches) > 1:
    raise CorpusValidationError(f"issue #{issue_number}: coverage_tag is ambiguous — both candidates reproduce {filed_hash!r}")
if not matches:
    raise CorpusValidationError(...)
return matches[0]
```

### WR-04: Module-level `assert` in `report_shapes.py` guards a real invariant but is stripped under `python -O`

**File:** `firestarter_app/tests/fixtures/report_shapes.py:647-650`

**Issue:**
```python
assert not (set(SHAPE_IDS) & RESERVED_SHAPE_IDS), (
    "a shape_id was frozen under a name D-04 reserved for a later phase; "
    f"collision: {set(SHAPE_IDS) & RESERVED_SHAPE_IDS}"
)
```
runs at *import* time, not inside a pytest test — it's the mechanism D-04 relies on to keep a future `shape_id` from silently colliding with one of `RESERVED_SHAPE_IDS`. A bare `assert` at module scope is removed entirely when Python runs with `-O`/`-OO` (`PYTHONOPTIMIZE`), so this specific safety net — unlike the pytest-based gates elsewhere in this phase — degrades silently under an optimized interpreter, contrary to this phase's own "fail closed, never silently pass" design principle applied everywhere else in the harness.

**Fix:** Replace the bare `assert` with an explicit check that cannot be optimized away:
```python
_collision = set(SHAPE_IDS) & RESERVED_SHAPE_IDS
if _collision:
    raise RuntimeError(
        f"a shape_id was frozen under a name D-04 reserved for a later phase; "
        f"collision: {_collision}"
    )
```

## Info

### IN-01: `_fetch_issues` hardcodes `gh issue list --limit 300` with no check that the result count stayed under the limit

**File:** `firestarter_app/tools/build_devtest_issue_corpus.py:78-102`

**Issue:** If `henols/firestarter_prom` accumulates more than 300 total issues (open + closed) in the future, `gh issue list --limit 300` would silently truncate the result set, and `derive_rows()` has no way to detect that truncation — it would simply see fewer `[dev test]`-titled issues than actually exist, and `validate_rows()`'s `len(rows) != 26` check would only catch this once the corpus size legitimately needs to grow past 26 anyway (a coincidental catch, not a deliberate one).

**Fix:** After fetching, assert `len(issues) < 300` (or whatever limit is passed) and raise `CorpusError` naming the truncation risk if the fetch returned exactly the limit, prompting a deliberate `--limit` bump rather than a silent drop.

### IN-02: `_extract_report` picks the *last* fenced JSON block carrying a `dedup_fingerprint` key, with no documented rationale

**File:** `firestarter_app/tools/build_devtest_issue_corpus.py:116-130`

**Issue:** `_extract_report()` iterates every fenced-JSON block in an issue body and keeps overwriting `found = obj` for each one that parses as a dict with a `dedup_fingerprint` key, so the function returns whichever qualifying block appears *last* in the body. For the 26 filed issues this currently works (all rows reproduce), but the choice of "last wins" rather than "first wins" or "reject on more than one" is undocumented, and an issue body that legitimately contains two reports (e.g., an initial run followed by a corrected re-run pasted below it) would silently take the second one with no signal that a choice was made.

**Fix:** Either document why "last" is the intended selection (e.g., "later comments/edits supersede"), or raise `CorpusError` when more than one qualifying block is found, forcing a human to pick explicitly.

---

_Reviewed: 2026-09-03T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
