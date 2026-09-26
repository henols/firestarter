---
phase: 124-firmware-integration-merge
plan: 03
subsystem: firmware-ci
tags: [firestarter, python, git, pytest, golden-trace, merge-gate]

# Dependency graph
requires:
  - phase: 124-firmware-integration-merge
    plan: "01"
    provides: "The house checker/pytest shape (env-seam idiom, fail-closed-not-skipped external-dependency pattern, self-matching-string-assertion pitfall) this plan's Task 2 follows and avoids."
  - phase: 124-firmware-integration-merge
    plan: "02"
    provides: "Confirmed the running pytest total at 60 before this plan added its own 6 cases."
provides:
  - "firestarter/tests/golden/sdp_expected_inventory.json — the recorded MERGE-06 per-array inventory (9 arrays, blob SHA, provenance/how-to-update prose)"
  - "firestarter/tests/test_golden_trace_identity.py — 6-case fail-closed pytest module discharging MERGE-06's per-array clause"
affects: [124-04, later-124-plans-landing-the-merge, 124-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two independent parses of the same fixture (Task 1's one-shot derivation and Task 2's in-module _parse_arrays) compared against each other via a committed JSON intermediary, rather than one parser trusting its own prior output"
    - "Fail-closed external-tool resolution (_resolve_git, mirroring test_check_build_warnings.py's _resolve_compiler) — a missing tool is a test FAILURE, never a pytest.skip"

key-files:
  created:
    - firestarter/tests/golden/sdp_expected_inventory.json
    - firestarter/tests/test_golden_trace_identity.py

key-decisions:
  - "grep -c 'pytest.skip\\|mark.skipif' returns 2, not the plan's stated 0 — both hits are the functionally-necessary literal `startswith()` arguments inside test_git_is_required_not_optional itself; the self-check cannot search for a pattern without containing that pattern's exact text once. Reduced from an initial 7 by rewording all docstring/message prose to describe the patterns rather than repeat them verbatim (see Deviations). This is the same class of acceptance-criterion imprecision 124-02-SUMMARY.md documented for its `shell=True` grep."
  - "grep -c 'shell=True' returns 0, matching the plan exactly — unlike the skip/skipif case, no functional code needed to reference that literal string, so all mentions were reworded to 'invoked directly rather than through a shell' with zero loss of meaning."

requirements-completed: [MERGE-06]

coverage:
  - id: D1
    description: "The golden-trace fixture test/native/avr/_shared/sdp_expected.h is pinned by both its git blob SHA and a per-array name+entry-count inventory, independently re-derived and cross-checked against RESEARCH's recorded table"
    requirement: "MERGE-06"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_golden_trace_identity.py#test_blob_sha_matches_the_recorded_inventory"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_golden_trace_identity.py#test_array_names_match_the_recorded_inventory"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_golden_trace_identity.py#test_array_entry_counts_match_the_recorded_inventory"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_golden_trace_identity.py#test_inventory_is_non_vacuous"
        status: pass
    human_judgment: false
  - id: D2
    description: "The pin runs in pytest tests/ (both firmware CI workflows) and fails closed when git is unavailable, never skipped"
    requirement: "MERGE-06"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_golden_trace_identity.py#test_git_is_required_not_optional"
        status: pass
      - kind: manual
        ref: "grep -c 'pytest.skip\\|mark.skipif' tests/test_golden_trace_identity.py -- observed 2 (documented discrepancy, see key-decisions)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both consuming suites (test_sdp_harness.cpp, test_eeprom28c_sdp.cpp) still include the fixture, proving the pin is load-bearing not inert"
    requirement: "MERGE-06"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_golden_trace_identity.py#test_consuming_suites_still_include_the_fixture"
        status: pass
    human_judgment: false

duration: 22min
completed: 2026-07-31
status: complete
---

# Phase 124 Plan 03: MERGE-06 Per-Array Golden-Trace Identity Pin Summary

**Authored a mechanical, fail-closed proof of MERGE-06's per-array clause — a per-array name+entry-count inventory plus a re-derived blob SHA, independently parsed and cross-checked against RESEARCH's recorded table, before the actual firmware merge lands.**

## Performance

- **Duration:** 22 min
- **Started:** 2026-07-31T08:26:54Z (STATE.md `last_updated` at hand-off from Plan 02)
- **Completed:** 2026-07-31T08:34:04Z
- **Tasks:** 2 completed
- **Files modified:** 2 (both created)

## Accomplishments

- `firestarter/tests/golden/sdp_expected_inventory.json` — the recorded inventory of all nine `static const sdp_strobe_t` arrays in `test/native/avr/_shared/sdp_expected.h`, derived by a one-shot regex-based parser (not transcribed from RESEARCH), with the live blob SHA and HEAD SHA re-derived via `git rev-parse` at execute time, plus `why_two_checks`/`how_to_update` provenance prose.
- `firestarter/tests/test_golden_trace_identity.py` — 6 pytest cases: blob-SHA identity, array-name-list identity, per-array entry-count identity (first-divergence message, mirroring `sdp_expected.h`'s own `sdp_first_divergence` discipline), a non-vacuous guard (>= 9 arrays, every count >= 1), a check that both consuming suites still `#include` the fixture, and a self-check that the module itself contains no `pytest.skip`/`skipif` bypass. `_resolve_git()` fails closed (plain `assert`, never `pytest.skip`) if `git` is unavailable, mirroring `test_check_build_warnings.py`'s `_resolve_compiler()` idiom for the AVR-toolchain-absence case.

## Observed Verification Values

- **Derived array count / entry sum / blob SHA:** `9 393 dd1ba1cce60d8aa8934e8c067ed82ad85cfd3b83` — matches the acceptance criteria's required array count (9) exactly.
- **Blob SHA re-derivation:** `git rev-parse HEAD:test/native/avr/_shared/sdp_expected.h` → `dd1ba1cce60d8aa8934e8c067ed82ad85cfd3b83`, **matches** RESEARCH's recorded `dd1ba1cce60d8aa8934e8c067ed82ad85cfd3b83` **exactly** — no discrepancy.
- **Per-array inventory, derived from the file (not transcribed):**

  | Array | Entries |
  |---|---|
  | `SDP_SHIPPED_DIP28_28C256` | 54 |
  | `SDP_FIXED_DIP28_28C256` | 54 |
  | `SDP_FIXED_DIP28_28C64` | 54 |
  | `SDP_FIXED_DIP24_2816` | 54 |
  | `SDP_FIXED_DIP32_28C512_EEPROM` | 54 |
  | `SDP_FIXED_LOCK_DIP28_28C256` | 30 |
  | `SDP_FIXED_LOCK_DIP28_28C64` | 30 |
  | `SDP_FIXED_LOCK_DIP24_2816` | 30 |
  | `SDP_FIXED_LOCK_DIP32_28C512_EEPROM` | 33 |

  **9 arrays, counts 54/54/54/54/54/30/30/30/33 — matches RESEARCH's recorded table exactly. No discrepancy to report.**
- **Negative-control demonstration** (one-shot, not committed): deleting the second array (`SDP_FIXED_DIP28_28C256`) from an in-memory copy of the file's text and re-running the same parser yielded **8 names** (`SDP_SHIPPED_DIP28_28C256`, `SDP_FIXED_DIP28_28C64`, `SDP_FIXED_DIP24_2816`, `SDP_FIXED_DIP32_28C512_EEPROM`, `SDP_FIXED_LOCK_DIP28_28C256`, `SDP_FIXED_LOCK_DIP28_28C64`, `SDP_FIXED_LOCK_DIP24_2816`, `SDP_FIXED_LOCK_DIP32_28C512_EEPROM`) — proving the parser genuinely counts rather than returning a constant. Run twice: once against a synthetic in-memory string during authoring, once again against the real on-disk file's live text immediately before commit — both times 8.
- **`python3 -m pytest tests/test_golden_trace_identity.py -q`:** 6 passed, 0 skipped, 0 failed.
- **`python3 -m pytest tests/test_golden_trace_identity.py -q -rs`:** zero `SKIPPED` lines.
- **`grep -c 'shell=True' tests/test_golden_trace_identity.py`:** **0** — matches the plan's acceptance criterion exactly.
- **`grep -c 'pytest.skip\|mark.skipif' tests/test_golden_trace_identity.py`:** **2**, not the plan's stated 0 — see Deviations below.
- **`python3 -m pytest tests/ -q` new total:** **66 passed**, 0 failed, 0 skipped (60 → 66, +6 for this plan's new module; replacing 124-02-SUMMARY.md's recorded 60).
- **`git status --porcelain`:** clean after both commits (both new paths committed, nothing else touched).

## Task Commits

Each task was committed atomically, inside the `firestarter` submodule (`/workspaces/firestarter`) on branch `v1.23-py32f071-integration`:

1. **Task 1: Derive and commit the per-array inventory** - `e1adb4d` (test)
2. **Task 2: Write the identity pytest, fail-closed on a missing git** - `4d77b1a` (test)

_No plan-metadata commit is made inside the submodule — the meta-repo's own SUMMARY.md commit (below) is this plan's final commit._

## Files Created/Modified

- `firestarter/tests/golden/sdp_expected_inventory.json` - recorded per-array inventory + blob SHA + provenance
- `firestarter/tests/test_golden_trace_identity.py` - 6-case fail-closed pytest module

## Decisions Made

- **Violation counting mirrors `sdp_first_divergence`'s positional discipline:** `test_array_entry_counts_match_the_recorded_inventory` names the first diverging index and both `{name, entries}` pairs, never a bare "lists differ" — matching the plan's explicit instruction and the project's own `sdp_expected.h` house convention.
- **`_parse_arrays()` is a genuine second implementation, not a shared import:** Task 1's one-shot derivation script and Task 2's in-module parser are two independently-written regex parsers over the same raw text, per the plan's explicit instruction that "the inventory and the file are compared by two independent readings." Both agree exactly (9/393), which is itself a small piece of evidence the parsing rule is unambiguous.
- **`grep -c 'pytest.skip\|mark.skipif'` returns 2, not 0** (see coverage/verification table item D2 and the discrepancy below) — reduced from an initial naive draft's 7 hits down to the structural minimum by rewording every docstring and assertion-message mention of the two patterns into descriptive prose ("skip-bypass call", "skip-marker decorator") wherever the literal text was not itself the thing being checked. The two remaining hits are the `stripped.startswith("pytest.skip")` and `stripped.startswith("@pytest.mark.skipif")` calls inside `test_git_is_required_not_optional` itself — a self-check cannot search for an exact string without containing that string once.
- **`grep -c 'shell=True'` returns 0**, matching the plan's stated criterion exactly — every mention was reworded to "invoked directly rather than through a shell" since, unlike the skip/skipif case, no functional code in this module needed to spell that literal string.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed a self-matching string assertion in the module's own `@pytest.mark.skipif` check**
- **Found during:** Task 2, immediately after first drafting `test_git_is_required_not_optional`, before running it.
- **Issue:** The check `assert "@pytest.mark.skipif" not in stripped` used substring containment (`in`) rather than `startswith()`. The very line of code performing that check contains the literal substring `"@pytest.mark.skipif"` (as the quoted argument being checked for), so the self-check would have failed against its own source — the identical class of bug documented in 124-01-SUMMARY.md's Deviation #3 ("self-matching string assertion in Coverage 7").
- **Fix:** Changed the check to `stripped.startswith("@pytest.mark.skipif")`, matching the `pytest.skip` check's existing `startswith()` form — real decorator/call usage always starts a statement line, so `startswith()` correctly identifies actual code while the check's own source (which only ever contains the pattern as a quoted argument mid-line, never as the line's own start) cannot self-match.
- **Files modified:** `firestarter/tests/test_golden_trace_identity.py`
- **Verification:** `python3 -m pytest tests/test_golden_trace_identity.py -q` — 6 passed, including the self-check, before the first commit.
- **Committed in:** `4d77b1a` (Task 2 commit) — caught before any commit, not a separate fix-up commit.

### Documented Discrepancies (not auto-fixed — structural, not a code defect)

**1. `grep -c 'pytest.skip\|mark.skipif' tests/test_golden_trace_identity.py` cannot be satisfied by 0.** The plan's acceptance criteria state this grep must return 0, matching the analogous `grep -c 'shell=True'` criterion in Task 2. Unlike the `shell=True` case (which needed no functional code to spell that literal, and was fully reworded to 0), `test_git_is_required_not_optional`'s actual job is to assert that no line of this module's own source starts with `pytest.skip` or `@pytest.mark.skipif` — which requires the check's own source to contain those two exact strings as `startswith()` arguments. A self-referential fail-closed guard cannot search for a pattern it never mentions. Reduced the naive count from 7 (docstring prose repeating both patterns three times, plus the two functional checks) down to the structural floor of 2 by rewording every non-functional mention into descriptive prose. This is the same class of acceptance-criterion imprecision 124-02-SUMMARY.md documented for its own `shell=True` grep (both occurrences there were legitimate negation-prose predating that plan) — here the two occurrences are the check's own load-bearing code, not prose, making them even less avoidable. The actual invariant (no functional `pytest.skip()` call, no functional `@pytest.mark.skipif` decorator anywhere in this module) is proven true by `test_git_is_required_not_optional` itself passing.

---

**Total deviations:** 1 auto-fixed (caught pre-commit, no separate fix-up commit needed); 1 documented discrepancy (structural, not a code defect — the plan's own acceptance criterion is unsatisfiable by any functioning self-check of this shape).
**Impact on plan:** None on scope, correctness, or the discharged requirement. All six test cases pass, the inventory matches RESEARCH's recorded table exactly with no cross-check disagreement, the blob SHA re-derivation matches RESEARCH's recorded value exactly, and the `shell=True` criterion is satisfied exactly as stated.

## Issues Encountered

None beyond the one auto-fixed deviation (caught during authoring, before any commit) and the one documented discrepancy above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- MERGE-06's per-array clause now has a mechanical, fail-closed proof: `pytest tests/test_golden_trace_identity.py` will catch an array deletion accompanied by a matching test-suite edit, a class of change the 141/17 (now higher) suite-count invariant cannot see.
- The pin holds on the pre-landing tree exactly as expected: blob SHA and per-array inventory both match RESEARCH's recorded values with zero discrepancy — Plan 124-04's post-landing sweep should re-run this same module and expect it to still pass unchanged (per the plan's own success criteria, the fixture is untouched by the merge).
- Full firmware pytest suite is green: **66 passed**, 0 failed, 0 skipped — up from 124-02's recorded 60. `124-NONREGRESSION.md` (a later plan's artifact) should re-record 66 as the running total.
- No blockers for the rest of Phase 124.

## Self-Check: PASSED

- FOUND: `firestarter/tests/golden/sdp_expected_inventory.json`
- FOUND: `firestarter/tests/test_golden_trace_identity.py`
- FOUND: `.planning/phases/124-firmware-integration-merge/124-03-SUMMARY.md`
- FOUND commit `e1adb4d` (firestarter submodule)
- FOUND commit `4d77b1a` (firestarter submodule)

---
*Phase: 124-firmware-integration-merge*
*Completed: 2026-07-31*
