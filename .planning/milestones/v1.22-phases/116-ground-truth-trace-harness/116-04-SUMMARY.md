---
phase: 116-ground-truth-trace-harness
plan: 04
subsystem: testing
tags: [python, host-pytest, sdp, source-scan, anti-hollow, brace-matching]

# Dependency graph
requires:
  - phase: 116-01
    provides: "v1.22 branch in both sub-repos; 82/82 native baseline"
provides:
  - "tools/check_no_log_in_sdp_window.py — structural (brace-matched) scan proving no LOG_* macro call sits inside eeprom28c_write_init's SDP timing window (flash_execute_command(EEPROM_SDP_DISABLE) -> eeprom28c_wait_for_write(...)), fails closed on every degenerate input"
  - "tests/fixtures/planted_log_in_window.cpp — committed, never-compiled, deliberately-violating fixture (TRACE-03c's anti-hollow proof)"
  - "tests/test_check_no_log_in_sdp_window.py — 6-test paired pytest: clean-source control, planted-violation proof, out-of-window control, comment-not-a-call control, 2 fail-closed legs"
affects: [117, 118]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Comment-stripping that preserves length and newlines (blank out // and /* */ spans with spaces, keep \\n) so line numbers and brace/anchor positions in the cleaned text map 1:1 onto the original source — avoids both a false-positive-on-prose substring grep AND a line-number-drift bug from a naive strip"
    - "Anchor-tuple-of-regexes module constants (_EMIT_ANCHOR_PATTERNS / _WAIT_ANCHOR_PATTERNS) with an explicit 'add here, do not delete' comment — Phase 117's emitter replacement extends the tuple rather than editing the fail-closed logic"
    - "FIRESTARTER_SDP_SRC env-override seam mirrors check_dispatch.py's FIRESTARTER_DB_FILE / check_devtest_orchestrator.py's FIRESTARTER_DEVTEST_SRC — lets the paired pytest inject a real subprocess-level fixture without touching the real, clean eeprom_28c.cpp"

key-files:
  created:
    - firestarter_app/tools/check_no_log_in_sdp_window.py
    - firestarter_app/tests/fixtures/planted_log_in_window.cpp
    - firestarter_app/tests/test_check_no_log_in_sdp_window.py
  modified: []

key-decisions:
  - "Deny list implemented as one regex (\\bLOG_[A-Z][A-Z0-9_]*\\s*\\() rather than an enumerated literal list of macro names — every macro in firestarter/include/logging_id.h shares the LOG_ prefix followed by an uppercase/underscore identifier and an opening paren, so one pattern covers all ~50 without hand-maintaining a name list that would drift from logging_id.h"
  - "Window scoped strictly to eeprom28c_write_init's own body via brace-matching (never a whole-file scan) — this makes the out-of-window control (Task 2 test 3) trivially correct: a LOG_* call inside eeprom28c_wait_for_write's own body (a separate, later function in the file) is never seen by the scan, because the brace-matcher never leaves eeprom28c_write_init's braces"
  - "Comment-stripping implemented as a length/newline-preserving blank-out pass over the whole cleaned text (not a per-window strip) so both the brace-matcher and the anchor/deny-list regexes operate on the same comment-free text and every reported line number stays correct against the original file"

requirements-completed: []  # TRACE-03 partial: only the planted-LOG_ sub-negative (TRACE-03c)
                             # lands here. TRACE-03's other 3 sub-negatives (unlock-table
                             # mutated to 0x10, lock-table swapped for write prefix,
                             # protocol != 0x0D -> 0xBB) land in 116-05's always-green harness
                             # suite per D-04/116-PATTERNS.md -- REQUIREMENTS.md checkbox stays
                             # unchecked until all 4 land, mirroring the 116-01 precedent
                             # (commit 8d8c42f reverted an identical premature TRACE-01/03 mark)

coverage:
  - id: D1
    description: "check_no_log_in_sdp_window.py resolves the SDP timing window structurally (brace-matched function-body extraction, not a bare grep) and exits 0 on today's clean eeprom_28c.cpp, printing a PASS line naming the resolved line range (109-111)"
    requirement: "TRACE-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tools/check_no_log_in_sdp_window.py (manual run); firestarter_app/tests/test_check_no_log_in_sdp_window.py::test_checker_exits_zero_on_clean_source"
        status: pass
    human_judgment: false
  - id: D2
    description: "Committed planted-violation fixture (tests/fixtures/planted_log_in_window.cpp) makes the checker exit 1 and name the planted line — the anti-hollow proof that the gate is capable of failing (TRACE-03c, D-04 third bullet)"
    requirement: "TRACE-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_check_no_log_in_sdp_window.py::test_checker_exits_nonzero_on_committed_planted_violation"
        status: pass
    human_judgment: false
  - id: D3
    description: "The gate discriminates by position (out-of-window control) and by call-vs-comment (comment-not-a-call control), not by mere textual presence of a logging-macro name anywhere in the function"
    requirement: "TRACE-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_check_no_log_in_sdp_window.py::test_checker_exits_zero_when_log_call_is_outside_window, ::test_checker_exits_zero_when_log_macro_name_is_only_in_a_comment"
        status: pass
    human_judgment: false
  - id: D4
    description: "The checker fails closed (never a silent pass) when the source path is missing or when eeprom28c_write_init's emit anchor cannot be located, naming the required fix (add the new anchor) rather than deleting the gate"
    requirement: "TRACE-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_check_no_log_in_sdp_window.py::test_checker_fails_closed_on_missing_source_path, ::test_checker_fails_closed_when_emit_anchor_is_absent"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-07-27
status: complete
---

# Phase 116 Plan 04: Ground Truth + Trace Harness — Planted-`LOG_`-in-SDP-Window Scan (TRACE-03c) Summary

**Built TRACE-03's third negative: a brace-matched structural scanner proving no logging call sits inside `eeprom28c_write_init`'s SDP command-sequence timing window, paired with a committed planted-violation fixture that proves the gate can actually fail — Phase 118's OBS-01 now has a gate keeping its report lines *around* the sequence, not inside it.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-07-27
- **Tasks:** 2
- **Files created:** 3 (all in `firestarter_app`)

## Accomplishments

- `firestarter_app/tools/check_no_log_in_sdp_window.py`: brace-matches `eeprom28c_write_init`'s body, resolves the window between the `flash_execute_command(EEPROM_SDP_DISABLE)` emit anchor and the `eeprom28c_wait_for_write(...)` completion-wait anchor, strips `//`/`/* */` comment spans (length/newline-preserving) before applying a single `LOG_[A-Z][A-Z0-9_]*(` deny-list regex covering every macro in `logging_id.h`. On today's tree the window resolves to `eeprom_28c.cpp` lines **109-111** and is clean (`PASS:` exit 0).
- `firestarter_app/tests/fixtures/planted_log_in_window.cpp`: committed, never-compiled, deliberately-violating variant of `eeprom28c_write_init` with a `LOG_INFO_ID(MSG_DEBUG)` call planted between the two anchors (line 29), header comment stating in plain words this must never be "fixed".
- `firestarter_app/tests/test_check_no_log_in_sdp_window.py`: 6 tests — clean-source control, the load-bearing planted-violation proof (exit 1, names line 29 and the macro), an out-of-window control (log call placed after the wait anchor, exit 0), a comment-not-a-call control (macro names appearing only in `//`/`/* */` spans inside the window, exit 0), and two fail-closed legs (missing source path; source present but emit anchor absent) — the latter's stderr names "add the new anchor" per the anti-rename contract.

## Observed facts

**Resolved window on today's tree:**

| Fact | Value |
|---|---|
| Resolved line range | `eeprom_28c.cpp:104-106` |
| Emit anchor | `flash_execute_command(EEPROM_SDP_DISABLE)` (line 109) |
| Wait anchor | `eeprom28c_wait_for_write(` (line 111) |
| Deny-list macro names | Every macro in `firestarter/include/logging_id.h`: `LOG_ID*`, `LOG_INFO_ID*`, `LOG_ERROR_ID*`, `LOG_WARN_ID*`, `LOG_OK_ID*`, `LOG_INIT_ID*`, `LOG_MAIN_ID*`, `LOG_END_ID*`, `LOG_DATA_ID*`, `LOG_DEBUG_ID_SUB*` — matched via the single pattern `\bLOG_[A-Z][A-Z0-9_]*\s*\(`, never a hand-enumerated list |
| Anchor regexes Phase 117 will need to extend | `_EMIT_ANCHOR_PATTERNS = (re.compile(r"flash_execute_command\s*\(\s*EEPROM_SDP_DISABLE\s*\)"),)` and `_WAIT_ANCHOR_PATTERNS = (re.compile(r"eeprom28c_wait_for_write\s*\("),)` in `tools/check_no_log_in_sdp_window.py` — when Phase 117 replaces the emitter with a `0x0D`-local one on `handle->firestarter_set_data`, add the new call-site pattern to `_EMIT_ANCHOR_PATTERNS` (do not replace/delete the existing entry outright unless the old emitter is gone from the tree) |

## Task Commits

Each task was committed atomically inside `firestarter_app`:

1. **Task 1: check_no_log_in_sdp_window.py — structural scan of the SDP timing window** — `8e3652f` (feat, in `firestarter_app` sub-repo)
2. **Task 2: Planted-violation fixture + paired anti-hollow pytest (TRACE-03c)** — `cf85507` (test, in `firestarter_app` sub-repo)

**Plan metadata:** committed in the meta repo (this SUMMARY.md + STATE.md + ROADMAP.md), see final commit below. Meta gitlink pointers for `firestarter` / `firestarter_app` stay unstaged (PINNED policy).

## Files Created/Modified

- `firestarter_app/tools/check_no_log_in_sdp_window.py` — 280-line structural scanner, fails closed on every degenerate input
- `firestarter_app/tests/fixtures/planted_log_in_window.cpp` — committed, never-compiled, deliberately-violating fixture
- `firestarter_app/tests/test_check_no_log_in_sdp_window.py` — 6-test paired pytest

## Decisions Made

- Deny list implemented as one regex (`\bLOG_[A-Z][A-Z0-9_]*\s*\(`) instead of enumerating every macro name from `logging_id.h` by hand — every logging macro in that header shares the `LOG_` prefix followed immediately by an uppercase/underscore identifier and an opening paren, so one pattern covers all of them (`LOG_ID*` through `LOG_DEBUG_ID_SUB*`) without a name list that could silently drift from the header.
- Window scoped strictly to `eeprom28c_write_init`'s own brace-matched body (never a whole-file scan) — this makes the out-of-window control trivially correct by construction: a `LOG_*` call inside `eeprom28c_wait_for_write`'s own body (a separate function later in the file) is never visited by the scan, because the brace-matcher never leaves `eeprom28c_write_init`'s braces.
- Comment-stripping is a single length/newline-preserving blank-out pass over the whole cleaned text (not a per-window strip) so both the brace-matcher and the anchor/deny-list regexes see the same comment-free text, and every reported line number still maps 1:1 onto the real source file.

## Deviations from Plan

None in the code — plan executed exactly as written. Both tasks' acceptance criteria (clean-tree PASS naming the resolved range, fail-closed on missing-path/missing-anchor, 6-test paired pytest with the planted-violation proof, out-of-window and comment-not-a-call discrimination) are met verbatim.

**Requirements bookkeeping correction:** this plan's frontmatter lists `requirements: [TRACE-03]`, but TRACE-03 itself names **four** first-class negative traces (unlock table mutated to `0x10`, lock table swapped for the write prefix, a planted `LOG_` inside the timing window, and `protocol != 0x0D` reaching `0xBB`). This plan (116-04) delivers only the third of those four — the planted-`LOG_` scan (TRACE-03c). The other three are built in 116-05's always-green harness suite as test-local `byte_flip_t` copies + a `test_not_implemented`-pattern positive test (D-04, `116-PATTERNS.md`). Marking the `TRACE-03` checkbox in `REQUIREMENTS.md` complete here would repeat the exact premature-completion mistake `116-01`'s commit `8d8c42f` ("revert premature TRACE-01/03 completion marks (3 of 4 negatives pending)") already caught and reverted. `requirements mark-complete TRACE-03` was run and then manually reverted in `REQUIREMENTS.md` (both the checklist line and the traceability table row) before this plan's final commit — the checkbox stays unchecked until 116-05 lands the remaining three negatives.

## Issues Encountered

- Ran the full `firestarter_app` pytest suite (not just the two new modules) to satisfy the plan's "no new failures beyond known pre-existing ones" acceptance criterion: exactly one failure, `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches`, matching the pre-existing golden-fixture drift already documented in project memory (`reference_audit_coverage_matrix_golden_stale.md`) and re-confirmed as unrelated in 116-03's summary — not caused by this plan, out of scope, left untouched.
- No collection error from the new `tests/fixtures/` directory (the `.cpp` fixture is data, never collected as a test file).

## Known Stubs

None.

## Threat Flags

None — the checker only reads `firestarter/src/proms/eeprom_28c.cpp` as text; no network endpoint, auth path, or schema change. `T-116-04-ENVBYPASS` (the `FIRESTARTER_SDP_SRC` override as a bypass vector) is mitigated by the fail-closed-on-missing-path leg, verified in Task 2's test 5.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- TRACE-03's third negative is now committed and permanently re-runnable: the gate passes clean, fails on a committed planted violation, and discriminates by position and by call-vs-comment — closing D-04's third bullet.
- `eeprom_28c.cpp` stayed byte-untouched throughout (`git status --short src/ include/` in `firestarter` empty at every checkpoint) — no sentinel comments were added to make the window easier to find; the window is derived structurally.
- Phase 117's FIX-01 (remap-aware emitter replacing `flash_execute_command(EEPROM_SDP_DISABLE)`) has a documented, single extension point: append the new emitter's call-site pattern to `_EMIT_ANCHOR_PATTERNS` in `check_no_log_in_sdp_window.py`. If Phase 117 forgets, the gate fails closed with a message naming exactly that fix rather than silently passing.
- No blockers for Wave 3 (116-05, the always-green SDP harness suite) or the remaining Wave 2 sibling work — this plan's files are net-new and touch nothing 116-02/116-03 created.

---
*Phase: 116-ground-truth-trace-harness*
*Completed: 2026-07-27*

## Self-Check: PASSED

- FOUND: `firestarter_app/tools/check_no_log_in_sdp_window.py`
- FOUND: `firestarter_app/tests/fixtures/planted_log_in_window.cpp`
- FOUND: `firestarter_app/tests/test_check_no_log_in_sdp_window.py`
- FOUND: `.planning/phases/116-ground-truth-trace-harness/116-04-SUMMARY.md`
- FOUND commit `8e3652f` (firestarter_app): feat(116-04) check_no_log_in_sdp_window.py
- FOUND commit `cf85507` (firestarter_app): test(116-04) planted fixture + paired pytest
