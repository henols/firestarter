---
phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half
plan: 01
subsystem: testing
tags: [gate, source-scan, pytest, sdp, host-cli, regex, brace-matching]

# Dependency graph
requires:
  - phase: 117-fix-remap-aware-0x0d-emitter-honest-completion-signal
    provides: "eeprom28c_emit_command_sequence and eeprom28c_wait_for_sdp_completion as two separate, brace-matchable static functions inside eeprom_28c.cpp"
provides:
  - "check_no_log_in_sdp_window.py's scanned window redefined to the union of the emitter body (eeprom_28c.cpp:206-222) and the completion-poll body (eeprom_28c.cpp:244-257), replacing the old between-the-call-sites span"
  - "The committed anti-hollow fixture (planted_log_in_window.cpp) re-planted inside the emitter body (line 35), still failing the gate"
  - "All 4 broken pytest cases (2, 3, 4, 6) repaired by name plus a new completion-poll-body negative (case 7) -- 7 total cases, all green"
  - "D-11 preserved: the gate still asserts exactly one thing (no logging call in the timing window); no AT28C_TBLC_MAX_US citation-presence check added"
affects: ["118-04 (adds the report lines into the now-legal between-the-call-sites span)", "118-05", "118-06"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Parameterised brace-matcher (_find_function_body(cleaned_text, func_name)) replacing a module-constant-bound one, so the same machinery resolves multiple target functions"
    - "Two-body union window resolution (_resolve_windows) plus a demoted anchor-pattern check retained purely as a rename tripwire on a third function (eeprom28c_write_init), decoupled from window computation"
    - "Test-time-derived expected-line-number assertion (grep the marker comment in the fixture/temp source rather than hardcoding a second literal) to prevent silent re-plant/assertion desync"

key-files:
  created: []
  modified:
    - firestarter_app/tools/check_no_log_in_sdp_window.py
    - firestarter_app/tests/fixtures/planted_log_in_window.cpp
    - firestarter_app/tests/test_check_no_log_in_sdp_window.py

key-decisions:
  - "scan()'s return contract widened to (violations, emitter_range, poll_range) -- a 3-tuple whose 2nd/3rd elements are each an inclusive (start_line, end_line) pair for one of the two windows, in file order (emitter first, poll second)"
  - "_EMIT_ANCHOR_PATTERNS / _WAIT_ANCHOR_PATTERNS kept append-only and repurposed as a secondary rename-tripwire inside _resolve_windows: they no longer compute the scanned span, but eeprom28c_write_init must still contain one emit anchor followed by one wait anchor, or resolution fails closed"
  - "Case 2's hardcoded 'line 29' literal replaced with a value derived from the fixture at test time (grep the PLANTED VIOLATION marker), so a future re-plant cannot silently desync the assertion from the fixture"
  - "Planted violation now lives at planted_log_in_window.cpp:35, inside the re-planted static eeprom28c_emit_command_sequence body"

requirements-completed: []  # OBS-01 and OBS-03 intentionally NOT marked complete -- both are multi-plan requirements; this plan lands only the gate-window half (see 118-01-PLAN.md "Requirement ownership" section). OBS-01 closes with 118-02/118-04; OBS-03 closes with 118-02/118-03/118-04.

coverage:
  - id: D1
    description: "check_no_log_in_sdp_window.py rewritten to scan the emitter body + completion-poll body union instead of the old between-the-call-sites span"
    requirement: "OBS-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tools/check_no_log_in_sdp_window.py (manual run: python tools/check_no_log_in_sdp_window.py, PASS naming emitter lines 206-222 and completion-poll lines 256-269)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Committed anti-hollow fixture re-planted inside the new emitter body (line 35); still fails the gate; anti-hollow spot check (delete plant, confirm RED, restore) passed"
    requirement: "OBS-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_check_no_log_in_sdp_window.py#test_checker_exits_nonzero_on_committed_planted_violation"
        status: pass
    human_judgment: false
  - id: D3
    description: "All 7 pytest cases green (4 repaired by name: 2/3/4/6; 1 new poll-body negative: case 7; 2 unchanged: 1/5); sibling firmware-source-scanning gates confirmed unaffected"
    requirement: "OBS-01"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_check_no_log_in_sdp_window.py (7 passed)"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_sdp_table_parity.py, test_sdp_bus_config_drift.py, test_revision_constants_parity.py (14 passed)"
        status: pass
    human_judgment: false

# Metrics
duration: 55min
completed: 2026-07-28
status: complete
---

# Phase 118 Plan 01: D-06 SDP No-Log Gate Window Rewrite Summary

**Redefined `check_no_log_in_sdp_window.py`'s scanned window from the between-call-sites span to the emitter body + completion-poll body union, re-planted the anti-hollow fixture inside the emitter, and repaired all 4 broken pytest cases plus added a poll-body negative — 7/7 green.**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-07-28
- **Completed:** 2026-07-28
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- `check_no_log_in_sdp_window.py` now brace-matches TWO function bodies — `eeprom28c_emit_command_sequence` (`eeprom_28c.cpp:206-222`) and `eeprom28c_wait_for_sdp_completion` (`eeprom_28c.cpp:244-257`) — and scans their union, instead of the old span between the two call sites inside `eeprom28c_write_init`. Verified against the real, unmodified `eeprom_28c.cpp`: `PASS: no logging call in SDP timing window (..., emitter lines 206-222, completion-poll lines 256-269)`, exit 0.
- `_find_function_body` generalised from a module-constant-bound lookup to `_find_function_body(cleaned_text, func_name)`, driven by a new `_func_def_pattern(func_name)` helper built from the same `\bvoid\s+<name>\s*\([^)]*\)\s*\{` template as before (still excludes the `;`-terminated forward declarations, still tolerates `static` and multi-arg signatures).
- `_EMIT_ANCHOR_PATTERNS` / `_WAIT_ANCHOR_PATTERNS` kept **append-only**, unchanged in content, and repurposed inside a new `_resolve_windows` helper as a secondary rename-tripwire: after resolving both bodies, `eeprom28c_write_init`'s body is still brace-matched and still required to contain one emit anchor followed by one wait anchor. If a future refactor moves the emitter or poll call out of `write_init` entirely, this still fails closed.
- The committed anti-hollow fixture (`tests/fixtures/planted_log_in_window.cpp`) re-planted: gained a `static void eeprom28c_emit_command_sequence(...)` body (with the planted `LOG_INFO_ID(MSG_DEBUG);` inside it, at line 35) and a clean `static void eeprom28c_wait_for_sdp_completion(...)` body; `eeprom28c_write_init` now calls both by their post-117 names. Verified: `FIRESTARTER_SDP_SRC=tests/fixtures/planted_log_in_window.cpp python tools/check_no_log_in_sdp_window.py` → `FAIL: 1 logging call(s) ... line 35: LOG_INFO_ID(...)`, exit 1, no `ERROR:` on stderr.
- All 4 broken pytest cases repaired by name (case 2's hardcoded `"line 29"` replaced with a value derived from the fixture at test time via a new `_line_number_of_marker` helper; cases 3 and 4 rewritten with both bodies present so they no longer hit the fail-closed `ValueError`; case 6 renamed to `test_checker_fails_closed_when_emitter_body_is_absent` and rewritten to omit only the emitter definition), plus a new case 7 (`test_checker_exits_nonzero_on_log_planted_in_completion_poll_body`) proving the poll half of the union is actually scanned (T-118-01-HALFWINDOW). 7/7 pass.
- Anti-hollow spot check performed manually (not committed): deleted the planted line from the fixture, re-ran the suite, confirmed `test_checker_exits_nonzero_on_committed_planted_violation` FAILED (its own `_line_number_of_marker` helper raised `AssertionError: marker 'PLANTED VIOLATION' not found`), then restored the fixture and re-verified the gate PASSes against the real source and the suite is green again.
- No `AT28C_TBLC_MAX_US` citation-presence assertion added anywhere (D-11 preserved) — the module docstring states explicitly why (comment-blanking makes a citation scan a second uncleaned-text pass; D-09's runtime check in a later plan is strictly stronger evidence).

## Task Commits

All three tasks landed in **one** commit, per the plan's explicit repo-mechanics instruction ("This plan produces one commit, in one repo" / "all in one commit" / verification item 5's exact required subject) — this overrides the generic per-task-commit default.

1. **Task 1: Redefine the gate's window as the emitter body plus the completion-poll body** — folded into the single commit below.
2. **Task 2: Re-plant the committed fixture inside the new window** — folded into the single commit below.
3. **Task 3: Repair all four broken pytest cases and add a completion-poll-body negative** — folded into the single commit below.

**Single plan commit (in `firestarter_app`):** `d9bbff2` — `test(118-01): redefine SDP no-log gate window to the emitter and poll bodies (OBS-01, OBS-03)`

**Plan metadata (in the meta-repo):** committed separately below (this SUMMARY.md + STATE.md + ROADMAP.md).

## Files Created/Modified

- `firestarter_app/tools/check_no_log_in_sdp_window.py` — window resolution rewritten (D-06); docstring rewritten to state the new window, the rationale, and the D-11 single-job constraint.
- `firestarter_app/tests/fixtures/planted_log_in_window.cpp` — re-planted inside the emitter body; header comment extended with the D-06 rationale and the new planted line number (35).
- `firestarter_app/tests/test_check_no_log_in_sdp_window.py` — cases 2/3/4/6 repaired, case 6 renamed, new case 7 added, module docstring's Coverage list updated to 7 entries.

## Decisions Made

- **`scan()`'s widened return contract:** `(violations, emitter_range, poll_range)` — a 3-tuple whose 2nd and 3rd elements are each an inclusive `(start_line, end_line)` pair, in file order (emitter body first, poll body second, matching their physical order in `eeprom_28c.cpp`). `main()`'s PASS/FAIL lines name both ranges explicitly (e.g. `emitter lines 206-222, completion-poll lines 256-269`). **This is the contract Plan 118-04's own verification depends on knowing.**
- **Anchor tuples' disposition:** `_EMIT_ANCHOR_PATTERNS` and `_WAIT_ANCHOR_PATTERNS` are unchanged in content (both entries in each, pre-Phase-117 and post-Phase-117, still present) and still append-only. They are no longer used to *compute* the scanned window; they are now a secondary assertion inside `_resolve_windows` that `eeprom28c_write_init`'s body still wires the emit call to the wait call in order. This satisfies the plan's "cleanest disposition" guidance verbatim.
- **Case 2's line-number derivation:** chosen over a second hardcoded literal, per the plan's stated preference ("prefer deriving the expected line number from the fixture at test time... if you can do so without weakening the assertion"). A new `_line_number_of_marker(text, marker)` helper greps the `PLANTED VIOLATION` comment marker in the fixture text at test-run time and asserts on that derived value plus `"FAIL:"` and the macro name — preserving the paired output-content anti-hollow shape the case's own docstring requires. The same helper is reused by the new case 7 for the poll-body-planted line.
- **Fail-closed message wording:** each of the three `ValueError` messages in `_resolve_windows` (emitter-body-absent, poll-body-absent, write-init-body-absent) plus the two pre-existing anchor-absent messages names its own target and tells the maintainer to add the new anchor/name rather than delete the gate. The literal substring `"add the new anchor"` is preserved in the emitter-body-absent message specifically, since pytest case 6 asserts on that exact substring.

## Deviations from Plan

None — plan executed exactly as written, including its explicit override of the generic per-task-commit convention (one commit for all three tasks, as the plan required in three separate places).

## Issues Encountered

- **Fixture header line-number transcription slip (self-caught, not committed as a bug):** when first drafting the re-planted fixture I wrote "line 33" in the header comment before running the checker to confirm the actual line; the checker's own FAIL output immediately showed line 35 (my header-comment estimate had miscounted the blank line after the closing `*/`). Corrected before running any acceptance checks or committing — no incorrect state was ever committed.
- **Full host pytest baseline capture required `--tb=no` without `-q`:** running `python -m pytest -q` truncated the final `"N passed, M failed in Xs"` summary line in this environment (root cause not investigated — likely an interaction with the `snapshot report summary` custom terminal-reporter section from the `syrupy` plugin). Switching to `python -m pytest --tb=no` (no `-q`) surfaced the summary reliably. Not a defect in this plan's scope; noted here so a future baseline capture in this repo doesn't waste time on the same trap.

## Pre-plan host pytest baseline (captured before any edit)

Command: `cd /workspaces/firestarter_app && python -m pytest --tb=no`

**Result: `1 failed, 973 passed in 36.74s`**

- The 1 failure is the pre-existing, out-of-scope golden-fixture drift named in the executor dispatch prompt: `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` (stale golden; needs a dedicated regen, not this plan's regression).
- The two `test_no_programmer_found_*` characterization tests (also named as a known pre-existing artifact in the dispatch prompt) were **not** failing at baseline capture time — verified separately with `-k test_no_programmer_found` → both passed (no live board's `comports=[]` monkeypatch defeat was active in this run).

## Post-plan host pytest full-suite result

Command: `cd /workspaces/firestarter_app && python -m pytest --tb=no`

**Result: `1 failed, 974 passed in 37.20s`** — exactly baseline's 973 passed + 1 new case (`test_checker_exits_nonzero_on_log_planted_in_completion_poll_body`), same single pre-existing failure (`test_audit_coverage_matrix`), zero new failures. No regression introduced.

## Resolved window line ranges (for Plan 118-04's verification)

- **Emitter body:** `eeprom_28c.cpp` lines **206-222** (`eeprom28c_emit_command_sequence`).
- **Completion-poll body:** `eeprom_28c.cpp` lines **256-269** (`eeprom28c_wait_for_sdp_completion`).
- **The legal report-line span** (unscanned by this gate) is everything in `eeprom28c_write_init` outside both bodies above — i.e. before line 206's call site and after line 269's call site, which in the current `write_init` body means immediately before the `eeprom28c_emit_command_sequence(...)` call (line 291) and immediately after the `eeprom28c_wait_for_sdp_completion(handle);` call (line 297).

## Planted-violation line number (re-plant)

`tests/fixtures/planted_log_in_window.cpp:35` — inside the re-planted `eeprom28c_emit_command_sequence` body. Both the fixture's own header comment and the paired pytest's derived-at-test-time assertion cite this value; neither is a duplicated hardcoded literal that could silently desync.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The gate now scans exactly the two windows where SDP timing actually lives. Plan 118-04 can add its `LOG_ID`/`LOG_ID_U32` report lines immediately before the emit call and immediately after the wait call inside `eeprom28c_write_init` (the old between-the-call-sites span) with the confidence that this gate will PASS on that placement and FAIL if a future edit moves either line inside either body.
- `_EMIT_ANCHOR_PATTERNS` / `_WAIT_ANCHOR_PATTERNS` remain append-only; Plan 118-04 and later plans must not delete entries from them even if they touch `eeprom28c_write_init` again.
- OBS-01 and OBS-03 remain **Pending** in `.planning/REQUIREMENTS.md` — confirmed not marked Complete by this plan (see `requirements-completed: []` above and the rationale in the plan's own "Requirement ownership" section).
- No blockers for Plan 118-02 (the three-repo catalog ritual) or Plan 118-03/118-04 (firmware changes) — this plan touched only `firestarter_app`, and the firmware submodule (`firestarter/`) is byte-unchanged.

## Self-Check: PASSED

- FOUND: `firestarter_app/tools/check_no_log_in_sdp_window.py`
- FOUND: `firestarter_app/tests/fixtures/planted_log_in_window.cpp`
- FOUND: `firestarter_app/tests/test_check_no_log_in_sdp_window.py`
- FOUND: `.planning/phases/118-observe-auto-unlock-visible-opt-out-able-fw-half/118-01-SUMMARY.md`
- FOUND: commit `d9bbff2` in `firestarter_app` (`git log --oneline --all`)

---
*Phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half*
*Completed: 2026-07-28*
