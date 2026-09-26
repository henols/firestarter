---
phase: 188-the-tools-directory
reviewed: 2026-09-13T00:00:00Z
depth: standard
files_reviewed: 33
files_reviewed_list:
  - .claude/skills/devtest-rootcause/SKILL.md
  - .claude/skills/devtest-rootcause/scripts/diff_db.py
  - .claude/skills/devtest-rootcause/scripts/seed_debug_session.py
  - firestarter/.github/workflows/beta-build.yml
  - firestarter/.github/workflows/build.yml
  - firestarter/platformio.ini
  - firestarter/scripts/baseline/size_baseline.json
  - firestarter/test/native/avr/_shared/host_stubs_common.inc
  - firestarter/tests/fixtures/captured_test_native_nodevtools_summary.log
  - firestarter/tests/fixtures/captured_test_native_summary.log
  - firestarter/tests/fixtures/planted_size_baseline_suites_errored.log
  - firestarter/tests/test_check_size_baseline.py
  - firestarter/tools/catalog/codegen.py
  - firestarter_app/.github/workflows/ci.yml
  - firestarter_app/CLAUDE.md
  - firestarter_app/pyproject.toml
  - firestarter_app/tests/fixtures/synthetic_nonzero_chip_id.py
  - firestarter_app/tests/test_blast_radius_invariance.py
  - firestarter_app/tests/test_build_db_inclusion.py
  - firestarter_app/tests/test_chip_test.py
  - firestarter_app/tests/test_decoder.py
  - firestarter_app/tests/test_lock_status_class_partition.py
  - firestarter_app/tests/test_numeric_schema_source_scan.py
  - firestarter_app/tests/test_parse_devtest_issue.py
  - firestarter_app/tests/test_sdp_db_invariant.py
  - firestarter_app/tests/test_skip_census.py
  - firestarter_app/tests/test_voltage_field_census.py
  - firestarter_app/tools/build_db.py
  - firestarter_app/tools/catalog/codegen.py
  - firestarter_app/tools/gen_sdp_bus_config.py
  - firestarter_app/tools/gen_test_image.py
  - firestarter_app/tools/parse_devtest_issue.py
  - tools/catalog/codegen.py
findings:
  critical: 0
  warning: 6
  info: 1
  total: 7
status: issues_found
---

# Phase 188: Code Review Report

**Reviewed:** 2026-09-13
**Depth:** standard
**Files Reviewed:** 31 (30 listed + `firestarter/tools/catalog/codegen.py`, read for the three-way byte-identity check)
**Status:** issues_found

## Summary

Phase 188 was a retirement phase: ten `check_*.py` gate scripts, six GSD-process tools, two CI
mirrors, one orphan, and the frame-vector apparatus on both the firmware and host sides were
deleted, and the phase's own SUMMARY.md files show unusually careful bookkeeping — cross-references
were swept in the same commits as the deletions that orphaned them, non-vacuity controls were run
before trusting a sweep's zero count, and several residual gaps were disclosed by name in
`Next Phase Readiness` sections for a later plan to pick up.

That bookkeeping was not, however, complete. This review found six places where a surviving
comment or docstring still asserts something that stopped being true the moment this phase's own
deletions landed — three of them citing a specific test or tool by name as still-active enforcement
when that test or tool no longer exists anywhere in the tree — plus one dangling CI comment and one
fully orphaned data file. None of these break a build or a test (the phase's own acceptance batteries
are green, and I did not find a reason to doubt that), so nothing here is classified Critical. All
are classified Warning because each one misrepresents the current state of the codebase to a future
reader in a way that could waste their time or, in the SDP/claim-safety cases, cause them to
under-estimate how little is currently guarded.

Two of the six (the `firestarter_app/CLAUDE.md` mypy-in-CI claim, and the orphaned
`dispatch_baseline.json`) were already flagged by the phase's own plans as disclosed, deferred gaps
— they are confirmed still present in the reviewed tree and are reported here because a disclosed
gap is still a gap until it is closed, not because the disclosure was inadequate. The other four
(the `check_diagnostic_report_claims.py` comment, the `check_sdp_capability_invariants.py`
docstring, the `test_numeric_schema_source_scan.py` internal inconsistency, and the
`beta-build.yml` "vector gates above" comment) were not called out in any SUMMARY.md I read and
appear to be genuinely new findings.

The `codegen.py` three-way byte-identity requirement holds (`tools/catalog/codegen.py`,
`firestarter/tools/catalog/codegen.py`, `firestarter_app/tools/catalog/codegen.py` all hash
`70583765b788401178...` — byte-identical, 735 lines each). The native/AVR figure quadruple
(`size_baseline.json`, both `captured_test_native*.log` fixtures,
`planted_size_baseline_suites_errored.log`, and `test_check_size_baseline.py`'s hardcoded
assertions) all agree at 179 cases / 179 succeeded / 16 suites, and the AVR flash/RAM figures in
`test_check_size_baseline.py` match `size_baseline.json`'s `avr_targets` exactly — I found no
disagreement anywhere in that family.

## Warnings

### WR-01: Stale "only enforcement" claim for a deleted claim-safety test

**File:** `firestarter_app/tools/parse_devtest_issue.py:212-215`
**Issue:** The comment above `_NOT_ATTRIBUTABLE` reads:

```python
# survive). Pre-checked against `check_diagnostic_report_claims.py`'s
# 14-entry `FORBIDDEN_PATTERNS` table and clean -- proven, not assumed, by
# `test_parser_marker_strings_trip_no_forbidden_claim_pattern`. No claim
# gate scans this file today (P-5); that test is the only enforcement.
```

`check_diagnostic_report_claims.py` and the test it names,
`test_parser_marker_strings_trip_no_forbidden_claim_pattern`, were both deleted by this phase
(confirmed: `grep -n "forbidden\|FORBIDDEN_PATTERNS" tests/test_parse_devtest_issue.py` returns
nothing). The comment's claim "that test is the only enforcement" is no longer true — there is now
*zero* enforcement of the forbidden-claim-pattern property on this string, not "one test's worth."
A maintainer editing `_NOT_ATTRIBUTABLE` (or adding a sibling claim string) who trusts this comment
will believe a safety net still exists where none does.

This file was one of 188-07's measured "20 survivor files" carrying an inert, deliberately
untouched mention of a deleted tool — correctly out of scope for that plan's GSD-*citation* sweep
(this isn't a Phase/D-NN identifier), but it is still a materially false claim about current
enforcement, which is a different defect class than the citation sweep was hunting.
**Fix:** Replace the last sentence with an honest statement, e.g.: "No claim gate scans this file
today (P-5); nothing currently re-verifies this string against a forbidden-pattern table." If the
property still matters, either restore a minimal check or file a tracked follow-up rather than
leaving the comment to assert protection that isn't there.

### WR-02: Stale "already gates elsewhere" claim for a deleted SDP invariant checker

**File:** `firestarter_app/tests/test_sdp_db_invariant.py:161-166`
**Issue:** `_assert_partition_matches_committed`'s docstring says a chip entering the measured ALLOW
set without also being in the committed set is "the widening signal
`tools/check_sdp_capability_invariants.py` already gates elsewhere." That file was deleted in this
same phase (plan 188-04's deletion list explicitly names
`check_sdp_capability_invariants.py`/`test_check_sdp_capability.py`). There is no other gate on this
widening signal anymore — this test's own committed-snapshot comparison is now the *only* one. The
docstring understates the current exposure by implying redundant coverage that no longer exists.
**Fix:** Drop the `tools/check_sdp_capability_invariants.py` clause, or replace it with a statement
that this test is now the sole gate on ALLOW-set widening.

### WR-03: Self-contradictory docstring after a partial repair

**File:** `firestarter_app/tests/test_numeric_schema_source_scan.py:215,235` (vs. the module-level
docstring at line 43)
**Issue:** Plan 188-05 deleted the module's old "test 2" (an `audit_coverage_matrix.py` scan) and,
per its own SUMMARY, "trimmed the surviving non-vacuity leg's docstring reference from 'tests 1 and
2' to 'test 1'." That edit landed at line 43 (module docstring: "...the exact same
`_find_forbidden_tokens` helper **test 1** calls..."), but the *function*-level docstring and
assertion message for `test_scan_helper_detects_planted_forbidden_tokens` were not updated and still
read "tests 1 and 2":

```python
def test_scan_helper_detects_planted_forbidden_tokens() -> None:
    """Drives the SAME `_find_forbidden_tokens` helper tests 1 and 2 call, ...
    ...
        f"which means tests 1 and 2 above prove nothing."
```

Current "test 2" (`test_page_size_by_part_has_exactly_two_entries`) does not call
`_find_forbidden_tokens` at all — it only imports `build_db._PAGE_SIZE_BY_PART` and checks its
length. The module now contains two docstrings that disagree with each other about which tests
share this helper.
**Fix:** Change both occurrences of "tests 1 and 2" (function docstring and the assertion failure
message) to "test 1", matching the already-corrected module-level docstring.

### WR-04: Docstring still claims an invariant enforced by a now-deleted test

**File:** `firestarter_app/tests/test_build_db_inclusion.py:9-11`
**Issue:** The module docstring states: "These tests assert the Phase 66 DB-01/02/03/05 behaviors
implemented by build_db.py ... and the SC#3 dispatch-safety invariant enforced by Plan 04." The test
that enforced that invariant, `test_non_supported_chips_are_non_dispatchable` (the in-function
consumer of the now-deleted `check_dispatch.py`'s `dispatch`/`KNOWN_PROTOCOLS` symbols, per the
88-02 census), was deleted by this phase per the operator's "delete the consumers" ruling. Nothing
in the file's actual test bodies asserts that invariant any longer, but the docstring — which a
reader consults first to learn what the module covers — still claims it does. (This is not a
complaint about the deletion decision itself, which was made on the record with full disclosure of
its cost; it is that the file's own description of its coverage was not updated to match.)
**Fix:** Remove the "and the SC#3 dispatch-safety invariant enforced by Plan 04" clause from the
module docstring, or note explicitly that this invariant's coverage was retired with the rest of
the `check_dispatch.py` consumers in Phase 188.

### WR-05: Dangling "vector gates above" comment in beta-build.yml

**File:** `firestarter/.github/workflows/beta-build.yml:107-109`
**Issue:**

```yaml
      # Same rationale as the vector gates above: -D DEV_TOOLS lives in the
      # shared [env] block, so without this leg the no-DEV_TOOLS build is never
      # compiled on the branch that ships.
      - name: Run native unit tests (no DEV_TOOLS)
        run: pio test -e native_nodevtools
```

The "Vector catalog validity check" and "Codegen drift gate (frame_vectors.h)" steps this comment
refers back to were deleted whole by this phase's plan 188-06, along with their own explanatory
comment block (confirmed: 188-06's SUMMARY explicitly records deleting "their explanatory comment
block above its pair" for those two steps). This *different* comment, attached to the following,
surviving `native_nodevtools` step, references "the vector gates above" that no longer exist in the
file — it survived the sweep that removed its subject. The sibling workflow, `build.yml`, has a
fully self-contained comment at the equivalent step (citing Phase 119 D-04 directly, with no
backward reference to anything else), confirming this is a leftover, not an intentional style.
**Fix:** Rewrite the comment to stand on its own, e.g. "`-D DEV_TOOLS` lives in the shared `[env]`
block, so without this leg the no-DEV_TOOLS build is never compiled on the branch that ships" (drop
the "Same rationale as ... above" clause).

### WR-06: `firestarter_app/CLAUDE.md` overstates mypy's CI enforcement

**File:** `firestarter_app/CLAUDE.md:127`
**Issue:** "**Tooling gate (v1.8):** `ruff check` + `ruff format --check` + `mypy` (strict on 8
modules ...) + `pytest --cov-fail-under=70` — all enforced by `.github/workflows/ci.yml` on every
PR; `pre-commit` config wires the same hook order locally." Plan 188-04 deleted the mypy step from
`ci.yml` entirely (confirmed: zero `mypy` references anywhere in `firestarter_app/.github/workflows/
ci.yml`, and `git log -p` shows the exact removed step, `mypy type check (watermark gate)`, in
188-04's commit `0f251f0`). mypy still runs locally via `.pre-commit-config.yaml` (confirmed present
and configured), but it is no longer part of the PR gate this line claims it is. 188-04's own
SUMMARY.md disclosed this exact gap twice ("this line now overstates mypy's CI enforcement ...
flagged here for 188-09's verdict note") and 188-09's verdict note documents the mypy CI removal as
one of the retired items, but neither plan corrected this specific line in `CLAUDE.md` itself — it
still reads as it did before the deletion.
**Fix:** Update the sentence to say mypy is enforced locally via `pre-commit` only (no longer via
CI), or restore a mypy CI step if that coverage is still wanted.

## Info

### IN-01: Fully orphaned data artifact retained on disk

**File:** `firestarter_app/tools/baseline/dispatch_baseline.json`
**Issue:** This 158 KB JSON file's `generated_by` field reads "check_dispatch.py inline capture."
`check_dispatch.py`, its sole generator and (per the 188-02 census) its sole consumer, was deleted
by this phase. A repo-wide `grep -rn "dispatch_baseline"` across `tests/`, `tools/`, and
`firestarter/` in `firestarter_app` returns zero hits — nothing reads this file anymore. This is a
disclosed, deliberate retention (188-05's Next Phase Readiness note flags "`tools/baseline/
dispatch_baseline.json`'s orphaned-data status" for 188-09, and 188-09's verdict note records it),
not an oversight, so this is Info rather than Warning: the file is dead weight, not a
misrepresentation.
**Fix:** If no future plan intends to revive a dispatch-invariant check that reads this file,
delete it; otherwise leave a short, honest note in the phase's closing record (not in the file
itself, per the no-comments-in-product-source rule) that names why it is being kept.

---

_Reviewed: 2026-09-13T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
