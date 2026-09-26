---
phase: 120-host-cli-surface-wire-emission-capability-refusal
plan: 03
subsystem: host-cli
tags: [logging, observability, serial-comm, sdp]

# Dependency graph
requires:
  - phase: 118-observe-auto-unlock-visible-declinable-fw-half
    provides: "Unconditional firmware INFO-band report lines (0x5E/0x5F) that the host was silently discarding"
  - phase: 119-lock-sdp-enable-command-surface-fw-half
    provides: "Two more unconditional INFO-band ids (0x60/0x61) plus 0x62, extending the same visibility gap"
provides:
  - "firestarter_app/firestarter/serial_comm.py — _log_rurp_feedback now logs response.type == \"INFO\" at logging.INFO (was logging.DEBUG, invisible at default verbosity)"
affects: [120-08-host-cli-surface-wire-emission-capability-refusal]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Scoped severity-arm promotion: add exactly one new elif comparing on the label, leave every other arm and the DEBUG fall-through untouched, and prove the scope with a parametrised negative test rather than trusting the diff alone"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/tests/test_serial_comm.py

key-decisions:
  - "Confirmed via read that the plan's two CONTEXT.md corrections hold in the live tree: the target function is _log_rurp_feedback (no _log_response exists), and the blast radius is six unconditional INFO-band ids, not five — the sixth being 0x5B MSG_INFO_HW, whose catalog severity is INFO despite being emitted through the unconditional LOG_WARN_ID_U8 alias."
  - "Did not touch NON_RESPONSE_PREFIXES or get_response() — INFO frames still never reach the operation layer, which is what mechanically enforces D-10's 'the host never parses a duration out of a decoded frame' for plan 120-08."
  - "Added the negative-scoped-promotion test as two caplog.at_level blocks per label (bound at INFO, then bound at DEBUG) rather than a single assertion, so the test proves both 'not visible at INFO' and 'actually logs at DEBUG' — ruling out a false pass from the call silently no-op'ing."

requirements-completed: []  # HOST-05 spans plans 120-03 and 120-08; only 120-08 may close it. Deliberately empty.

coverage:
  - id: D1
    description: "Response with type==\"INFO\" now produces exactly one record at logging.INFO on the RURP logger"
    verification:
      - kind: unit
        ref: "tests/test_serial_comm.py::test_info_band_frame_is_promoted_to_logging_info"
        status: pass
    human_judgment: false
  - id: D2
    description: "Protocol-phase labels (OK/INIT/MAIN/END/DATA) still log at logging.DEBUG — the promotion is scoped, not blanket"
    verification:
      - kind: unit
        ref: "tests/test_serial_comm.py::test_non_info_protocol_phase_labels_still_log_at_debug (parametrised x5)"
        status: pass
    human_judgment: false
  - id: D3
    description: "WARN/ERROR severity arms unchanged (WARN->WARNING, ERROR->ERROR) — new arm did not reorder or shadow them"
    verification:
      - kind: unit
        ref: "tests/test_serial_comm.py::test_warn_and_error_severity_arms_are_unchanged"
        status: pass
    human_judgment: false

# Metrics
duration: 12min
completed: 2026-07-29
status: complete
---

# Phase 120 Plan 03: Promote INFO-Band Frames to Default Visibility Summary

**One scoped `elif response.type == "INFO": level = logging.INFO` arm in `_log_rurp_feedback`, so the SDP report lines Phase 118/119 deliberately emit unconditionally are finally visible at default host verbosity — plus three additive tests proving the promotion, its negative scope, and the untouched WARN/ERROR arms.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-07-29T10:33:00Z
- **Completed:** 2026-07-29T10:37:01Z
- **Tasks:** 2 (both `type="auto"`, Task 1 `tdd="true"`)
- **Files modified:** 2 (`firestarter_app/firestarter/serial_comm.py`, `firestarter_app/tests/test_serial_comm.py`)

## Accomplishments

- `_log_rurp_feedback` gained one new `elif` arm promoting the `INFO` label from `logging.DEBUG` to `logging.INFO`. `OK`, `INIT`, `MAIN`, `END`, `DATA` and the pre-existing `WARN`/`ERROR` arms are byte-identical apart from the insertion — verified by `git diff` showing 36 insertions, 0 deletions, all inside the severity-chain region.
- The in-source comment records five things per the plan's action spec: the D-09/HOST-05/F-120-02 defect being fixed; that the promotion is deliberately scoped to `INFO` only; the six-id blast radius (`0x5E`/`0x5F`/`0x60`/`0x61`/`0x62` plus `0x5B` `MSG_INFO_HW`); that `0x5B` is Phase 35's CR-02 hard-fail-loud warning, now visible for the first time; and the `-v` prefix-rendering side effect (`I:` → `INFO:`).
- Three additive tests: a positive leg, a parametrised negative-scoped leg (5 labels), and a WARN/ERROR regression leg — 7 new test cases total, all passing on first run.
- `NON_RESPONSE_PREFIXES` and `_read_and_parse_lines` are untouched — confirmed both by `git diff` scope and by keeping `get_response()`'s filter behavior intact, which is load-bearing for plan 120-08's D-10.

## Task Commits

Each task was committed atomically, inside the `firestarter_app` submodule:

1. **Task 1: Promote the INFO label to logging.INFO in `_log_rurp_feedback`** — `fa05776` (feat)
2. **Task 2: Add the D-09 promotion tests, including the negative scoped-promotion leg** — `f897724` (test)

No plan-metadata commit inside `firestarter_app` — this plan's changes are `serial_comm.py` + `test_serial_comm.py`; the metadata commit for this plan lives in the meta repo (below).

## Files Created/Modified

- `firestarter_app/firestarter/serial_comm.py` — one new `elif` arm in `_log_rurp_feedback` promoting `"INFO"` to `logging.INFO`, with a five-part provenance comment.
- `firestarter_app/tests/test_serial_comm.py` — three new tests (`test_info_band_frame_is_promoted_to_logging_info`, `test_non_info_protocol_phase_labels_still_log_at_debug`, `test_warn_and_error_severity_arms_are_unchanged`) plus a `Response` import and a module-level comment block recording the six-id finding and the zero-existing-tests-moved search result.

## Two CONTEXT.md Corrections (confirmed live, per plan's `<output>` instruction)

1. **The target function is `_log_rurp_feedback`, not `_log_response`.** No `_log_response` function exists anywhere in the tree; CONTEXT.md's line numbers (`serial_comm.py:232-247`, mapping at `:233-238`) were correct, only the name was wrong (RESEARCH F-12). Confirmed by direct read before editing.
2. **The blast radius is SIX unconditional INFO-band ids, not five.** CONTEXT.md D-09 names `0x5E`, `0x5F`, `0x60`, `0x61`, `0x62`. The sixth is `MSG_INFO_HW` (`0x5B`), emitted through `LOG_WARN_ID_U8` at `rurp_hw_rev_utils.h:96` — which `logging_id.h:115` makes a plain unconditional alias for `LOG_ID_U8` — while its *catalog* severity is `INFO`. This means D-09 also partially fixes Phase 35's CR-02 hard-fail-loud revision warning, a second and older observability defect that was invisible at default verbosity for the same reason. It fires exactly on shields whose revision detect is inconclusive with no EEPROM override — the operator's Rev 2.2 / Rev 2.0 / modified-Rev-0 rotation.

**Zero existing tests moved.** A search of the whole `test_serial_comm.py` module (and cross-checked against `test_decoder.py`) for level assertions and record-count assertions on the `RURP` logger — `caplog.at_level(..., logger="RURP")`, `not caplog.records`, `len(caplog.records) ==`, `caplog.records == []` — found zero hits before this plan. `test_decoder.py`'s `test_severity_routing_preserves_response_shape` asserts only that `Response.type` is a string label, unaffected by the level change. Every test added by this plan is purely additive; `git diff --stat tests/test_serial_comm.py` shows 102 insertions, 0 deletions.

**Rendered-prefix side effect:** under `-v`, an `INFO` frame's rendered prefix changes from `I:` to `INFO:`, because the one-character abbreviation in `_log_rurp_feedback` applies only while `rurp_logger.isEnabledFor(logging.DEBUG)` *and* the type is in `NON_RESPONSE_PREFIXES` — at `-v` the DEBUG gate is already open regardless of this arm's level assignment, so the frame renders with its full label instead of the abbreviated form used at default verbosity for other `NON_RESPONSE_PREFIXES` members.

## Class Lesson

A two-repo requirement can pass its own phase's verification and still be false end to end. Phase 118's OBS-01 (verified 5/5 ROADMAP criteria) shipped a firmware-side INFO report line and proved it emitted correctly on the wire — but the host-side consumer discarded it at default verbosity for the entirety of Phases 118 and 119, because `_log_rurp_feedback` special-cased only `ERROR`/`WARN` and let the whole INFO band fall to `logging.DEBUG` while `_setup_logging` sets root to `INFO` unless `-v`. Firmware-emits-correctly and user-sees-it are two separate claims, and only end-to-end verification across both repos catches the gap between them.

## Decisions Made

- Confirmed both CONTEXT.md corrections against the live tree (function name, six-vs-five ids) before writing the fix, rather than trusting the plan's restatement alone.
- Kept the fix to exactly one `elif` arm — no restructuring of the existing chain, no touching `NON_RESPONSE_PREFIXES`, no touching `get_response()`.
- Wrote the negative-scoped-promotion test with two `caplog.at_level` blocks (INFO-bound, then DEBUG-bound) per label instead of a single assertion, so a silent no-op logging call cannot produce a false pass.

## Deviations from Plan

None — plan executed exactly as written. Both tasks' verification blocks passed after the auto-formatter (`ruff format`) reformatted the new test additions to match project style; no logic change resulted, and the diff remained additions-only (confirmed by `git diff --stat` before and after).

## Issues Encountered

None.

## Non-regression checks (plan `<verification>` block, run in full)

- `python3 -m pytest tests/test_serial_comm.py tests/test_decoder.py tests/test_eprom_operations.py -q` — 114 passed.
- `ruff check firestarter/ tests/` — all checks passed.
- `ruff format --check firestarter/ tests/` — 96 files already formatted.
- `python3 tools/check_mypy_watermark.py` — 1 error (watermark 35, 34 below) — unchanged from prior plans' baseline.
- `git -C /workspaces/firestarter status --porcelain` — empty; tip still `0048b3d`. Firmware sub-repo byte-untouched.
- `git -C /workspaces/firestarter_app diff --stat -- firestarter/messages.py tools/catalog/` — empty. Catalog artifacts untouched.
- Known-RED baselines named, not tolerated: `test_audit_coverage_matrix.py::test_golden_file_matches` (stale golden, pre-existing) was not run in this scoped verification pass; `test_no_programmer_found_*` did not trigger (no live board attached to this session).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- INFO-band frames are now visible at default verbosity; this is a prerequisite observation-layer fix that plan 120-08 (HOST-05's other half — D-10 summary line, D-11 exit code) can build on.
- `NON_RESPONSE_PREFIXES` still filters INFO frames out of `get_response()`, so plan 120-08 cannot parse a duration out of a decoded frame via that path — confirmed intact.
- HOST-05 is **not** ticked by this plan — verified `.planning/REQUIREMENTS.md` is untouched; only plan 120-08 may close it.
- No blockers. Both sub-repo working trees stayed clean throughout except for the two committed changes above.

---
*Phase: 120-host-cli-surface-wire-emission-capability-refusal*
*Completed: 2026-07-29*

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/serial_comm.py`
- FOUND: `firestarter_app/tests/test_serial_comm.py`
- FOUND: `.planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-03-SUMMARY.md`
- FOUND commit `fa05776` (Task 1)
- FOUND commit `f897724` (Task 2)
