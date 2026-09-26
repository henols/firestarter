---
phase: 151-protection-readability-lock-status
plan: 03
subsystem: firmware-protocol
tags: [firmware, avr, platformio, wire-protocol, mypy, pytest, ruff]

# Dependency graph
requires:
  - phase: 151-01
    provides: 151-DESIGN.md's §1 wire shape and §7 debug-output-consequence decisions
provides:
  - "CMD_LOCK_STATUS 16 defined in firestarter/include/firestarter.h"
  - "is_memory_cmd()'s ninth admitted case (CMD_LOCK_STATUS), still zero preprocessor conditionals"
  - "firestarter.cpp's parse gate widened to admit any is_memory_cmd() command regardless of ordinal"
  - "Both native mirror sites (test_cmd_admission.cpp, test_pinmap_provisional.cpp) proving the nine-command set"
  - "COMMAND_LOCK_STATUS = 16 + COMMAND_NAMES entry in firestarter_app/firestarter/constants.py"
  - "_EXPECTED_CMD_NAMES in check_is_memory_cmd_no_ifdef.py grown to nine names"
  - "tests/test_parse_gate_admission.py — non-vacuous source-scan proof of the widened gate"
affects: [151-05, 151-08, 151-10, 151-13]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Predicate-first disjunction ordering (is_memory_cmd(handle->cmd) || handle->cmd < CMD_READ_VPP) keeps the cheap ordinal test as fallback, not primary."
    - "Count assertions paired with membership truth tables so a two-edit compensating change cannot slip past a set-equality proof."

key-files:
  created:
    - firestarter_app/tests/test_parse_gate_admission.py
  modified:
    - firestarter/include/firestarter.h
    - firestarter/src/firestarter.cpp
    - firestarter/test/native/avr/test_cmd_admission/test_cmd_admission.cpp
    - firestarter/test/native/avr/test_pinmap_provisional/test_pinmap_provisional.cpp
    - firestarter_app/firestarter/constants.py
    - firestarter_app/tools/check_is_memory_cmd_no_ifdef.py
    - firestarter_app/tests/test_check_is_memory_cmd_no_ifdef.py
    - firestarter_app/tests/fixtures/planted_ifdef_in_predicate.h

key-decisions:
  - "Widened the parse gate rather than re-ordering the CMD_* enum or making the read a non-memory command (OD-3), per 151-DESIGN.md."
  - "Left the second diagnostic-range ordinal guard unchanged; command 16 emits no DBG_* lines by construction, documented as a chosen consequence (DESIGN.md §7)."
  - "No loop() dispatch arm added for CMD_LOCK_STATUS — command 16 falls through to MSG_ERR_UNKNOWN_CMD until Plan 151-08."
  - "check_is_memory_cmd_no_ifdef.py's PASS message now reports the expected-set count dynamically instead of a hardcoded 'eight', so a future growth does not require editing a display string separately from the set."
  - "check_mypy_watermark.py verified under a uv-managed Python 3.11 venv rather than this devcontainer's default 3.12, which fails the gate closed on an unrelated numpy stub syntax issue (documented project environment trap)."

patterns-established:
  - "A ninth memory command was added by touching exactly the four sites 151-DESIGN.md's OD-3 named: the enum, the predicate, the parse gate, and the two host/firmware mirror pairs — no fifth site discovered."

requirements-completed: []

coverage:
  - id: D1
    description: "CMD_LOCK_STATUS 16 defined and admitted by is_memory_cmd() (ninth case, no preprocessor conditional), reaching json_parse()/configure_memory() via the widened parse gate"
    verification:
      - kind: unit
        ref: "firestarter/test/native/avr/test_cmd_admission/test_cmd_admission.cpp#test_admission_truth_table_over_every_cmd_value (native + native_nodevtools)"
        status: pass
      - kind: unit
        ref: "firestarter/test/native/avr/test_cmd_admission/test_cmd_admission.cpp#test_admission_count_is_exactly_nine"
        status: pass
      - kind: other
        ref: "python3 -c source-scan asserting the widened is_memory_cmd body has exactly 9 case labels including CMD_LOCK_STATUS and no preprocessor conditional"
        status: pass
    human_judgment: false
  - id: D2
    description: "The diagnostic-range ordinal guard is left unchanged, with its comment recording the no-DBG_* consequence as a Phase 151 choice"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_parse_gate_admission.py#test_diagnostic_range_unchanged_with_phase_151_comment"
        status: pass
    human_judgment: false
  - id: D3
    description: "Provisional-pinmap refusal covers CMD_LOCK_STATUS, proven by the local run of the env no CI leg runs"
    verification:
      - kind: unit
        ref: "pio test -e native_pinmap_provisional (test_pinmap_provisional_refuses_cmd_lock_status, 11 cases total)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Firmware CMD_* and host COMMAND_* ladders both carry 16 with a COMMAND_NAMES entry; bidirectional parity gate observed running, not skipped"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_revision_constants_parity.py (pytest -o addopts=\"-rs\", 14 passed, 0 skipped)"
        status: pass
      - kind: unit
        ref: "python3 -c: constants.COMMAND_LOCK_STATUS == 16 and 16 in constants.COMMAND_NAMES"
        status: pass
    human_judgment: false
  - id: D5
    description: "Leonardo build stays inside the unguarded 28672 B Caterina cliff, margin recorded explicitly"
    verification:
      - kind: other
        ref: "pio run -e leonardo -> flash_used 27248 B; margin 28672-27248 = 1424 B (UNGUARDED)"
        status: pass
    human_judgment: false

duration: ~30min
completed: 2026-08-20
status: complete
---

# Phase 151 Plan 03: `CMD_LOCK_STATUS` Admission Gate Summary

**Firmware/host command-16 admission: `is_memory_cmd()` grows to nine cases, the parse gate widens to `is_memory_cmd(handle->cmd) || handle->cmd < CMD_READ_VPP`, both native mirror suites and the host constant ladder move in lockstep, leonardo stays 1424 B clear of the unguarded Caterina cliff.**

## Performance

- **Duration:** ~30 min
- **Started:** ~2026-08-20T13:00Z (approximate — not captured at session start)
- **Completed:** 2026-08-20T13:28Z
- **Tasks:** 3 completed
- **Files modified:** 9 (2 firmware source, 2 firmware native-test, 4 app host, 1 app fixture) + 1 new app test file

## Accomplishments

- `CMD_LOCK_STATUS 16` defined in `firestarter/include/firestarter.h` immediately above `is_memory_cmd()`, whose switch body grew from eight `case` labels to nine with zero preprocessor conditionals and without naming `CMD_DEV_ADDRESS`/`CMD_DEV_REGISTER`.
- `firestarter/src/firestarter.cpp`'s parse gate at the old `:77` widened to `is_memory_cmd(handle->cmd) || handle->cmd < CMD_READ_VPP`, predicate ordered first (cheap ordinal test as fallback), with an extended Phase 151 comment paragraph recording OD-3's rejected alternatives (enum re-ordering breaks wire compatibility; a non-memory command is structurally impossible because `firestarter_get_data` is set only by `configure_memory`).
- The second, independent diagnostic-range ordinal guard (`handle->cmd > CMD_IDLE && handle->cmd < CMD_READ_VPP`) is left **byte-for-byte unchanged**; its comment now records that command 16 falls outside it by construction, so `dev lock-status` will emit none of the three `DBG_*` lines — a stated choice (DESIGN.md §7), not a discovery.
- No `loop()` dispatch arm was added for command 16 — it currently falls through to `default: LOG_ERROR_ID_U8(MSG_ERR_UNKNOWN_CMD, ...)`, a coherent, buildable intermediate state until Plan 151-08 lands the operation.
- Both firmware-native mirror suites moved: `test_cmd_admission.cpp`'s exhaustive `[0,255]` truth table grew from `{1,2,3,4,5,6,9,10}` to include `16`, plus a new independent count-assertion leg (`is_memory_cmd` true for exactly 9 of 256 values) and boundary controls at 15/17; `test_pinmap_provisional.cpp` gained a ninth per-command case (`test_pinmap_provisional_refuses_cmd_lock_status`) and its truth-table negative control now covers all nine commands.
- Host mirror: `constants.py` gained `COMMAND_LOCK_STATUS = 16` and a `COMMAND_NAMES[16]` entry (no exemption needed in `test_revision_constants_parity.py`'s four-entry map — it maps by the default `CMD_X -> COMMAND_X` rule); `check_is_memory_cmd_no_ifdef.py`'s `_EXPECTED_CMD_NAMES` grew from eight to nine names, and its PASS message now reports the count dynamically.
- New `firestarter_app/tests/test_parse_gate_admission.py` (4 legs, no `monkeypatch.setenv`): the widened gate expression is present in the real firmware source; the diagnostic-range test is present unchanged with a "Phase 151" sentence in its preceding comment; `loop()`'s `default:` arm still emits `MSG_ERR_UNKNOWN_CMD`; and a non-vacuity control proves the shared extraction helper can report the widened expression **ABSENT** against a synthetic pre-Phase-151 source.
- All three AVR targets build clean: uno 25166 B flash / 1575 B RAM, uno328pb 25216 B flash / 1581 B RAM, leonardo 27248 B flash / 2016 B RAM. Leonardo's unguarded Caterina-cliff margin (`28672 − 27248`) is **1424 B**, comfortably inside the 1460 B budget this plan was given (delta from the 27212 B pre-plan baseline was +36 B).

## Task Commits

Each task was committed atomically, dual-repo:

1. **Task 1: `CMD_LOCK_STATUS 16`, the ninth `is_memory_cmd` arm, and the widened parse gate** — firestarter `32c32e7` (feat)
2. **Task 2: Move both firmware-native mirror sites and run the env no CI leg runs** — firestarter `4df96c1` (test)
3. **Task 3: Host constant parity, the `_EXPECTED_CMD_NAMES` deliberate act, and a non-vacuous parse-gate source scan** — firestarter_app `fe2634f` (feat)

**Plan metadata:** recorded in this SUMMARY commit (meta repo).

_Note: this plan's `commits_land_in: [firestarter, firestarter_app]` — no meta-repo code commit exists for Tasks 1-3; only STATE.md/ROADMAP.md/this SUMMARY are committed in the meta repo._

## Files Created/Modified

- `firestarter/include/firestarter.h` — `CMD_LOCK_STATUS 16` definition + ninth `is_memory_cmd()` case + preamble prose update (eight -> nine)
- `firestarter/src/firestarter.cpp` — widened parse gate + extended Phase 119/151 comment; diagnostic-range guard's comment extended, body unchanged
- `firestarter/test/native/avr/test_cmd_admission/test_cmd_admission.cpp` — truth table extended to nine, new count leg, new 15/17 boundary controls
- `firestarter/test/native/avr/test_pinmap_provisional/test_pinmap_provisional.cpp` — ninth per-command refusal case + extended truth-table negative control
- `firestarter_app/firestarter/constants.py` — `COMMAND_LOCK_STATUS = 16` + `COMMAND_NAMES` entry
- `firestarter_app/tools/check_is_memory_cmd_no_ifdef.py` — `_EXPECTED_CMD_NAMES` grown to nine; PASS message now dynamic
- `firestarter_app/tests/test_check_is_memory_cmd_no_ifdef.py` — two "eight" docstring sites updated to nine; new `len(_EXPECTED_CMD_NAMES) == 9` leg; two synthetic fixtures extended with `CMD_LOCK_STATUS` so they still pass against the grown expected set
- `firestarter_app/tests/fixtures/planted_ifdef_in_predicate.h` — added the unconditional `CMD_LOCK_STATUS` case so the fixture still isolates assertion (a) only, per its own documented rule
- `firestarter_app/tests/test_parse_gate_admission.py` (new) — 4-leg non-vacuous source-scan proof over `firestarter/src/firestarter.cpp`

## Decisions Made

- Widened the parse gate (`is_memory_cmd(handle->cmd) || handle->cmd < CMD_READ_VPP`) rather than re-ordering the enum (breaks wire compatibility) or making the read a non-memory command (structurally impossible — `firestarter_get_data` is set only by `configure_memory`). Per OD-3 / 151-DESIGN.md.
- Left the diagnostic-range ordinal guard at `firestarter.cpp:132-142` completely unchanged; recorded the no-`DBG_*`-output consequence in its comment as a chosen trade, not a defect to fix.
- Deliberately did **not** add a `loop()` dispatch arm for `CMD_LOCK_STATUS` — that belongs to Plan 151-08. Command 16 currently produces `MSG_ERR_UNKNOWN_CMD`, a coherent intermediate state.
- `check_is_memory_cmd_no_ifdef.py`'s PASS message computes the expected-set size from `len(_EXPECTED_CMD_NAMES)` rather than a hardcoded word, so a future growth needs only the one set-literal edit.
- Ran `check_mypy_watermark.py` under a `uv`-managed Python 3.11 venv rather than this devcontainer's default 3.12, which fails the gate closed on an unrelated numpy/py3.12 stub syntax issue — a previously documented environment trap, not caused by this plan's changes.

## Deviations from Plan

None — plan executed exactly as written. The two synthetic fixtures in `test_check_is_memory_cmd_no_ifdef.py` (out-of-body control, comment-not-a-violation control) and the committed `planted_ifdef_in_predicate.h` fixture needed a `CMD_LOCK_STATUS` case added so they continued to pass/isolate correctly against the grown nine-name expected set — this is the mechanical consequence of Task 3's own instruction to grow `_EXPECTED_CMD_NAMES`, not an unplanned discovery, so it is recorded here rather than under a numbered Rule.

## Issues Encountered

- `scripts/check_build_warnings.py` (firmware) requires `--log ENV=PATH` or `--rebuild`; the plan's verify block's bare invocation is documented shorthand. Ran `--rebuild`, which passed (AVR `== 0` on all three targets; native 1138/1166, native_nodevtools 1152/1166, both below watermark).
- `python3 tools/check_mypy_watermark.py` (app) fails closed under this devcontainer's default Python 3.12 on an unrelated `numpy/__init__.pyi` syntax error (`Type statement is only supported in Python 3.12 and greater` — an inverted-looking message from a stub file that predates 3.12 syntax support in the installed mypy). Resolved by building a throwaway `uv venv --python 3.11` and installing `.[test]` into it (per project memory's documented recipe), which produced a clean, complete run: 34 errors, 1 below the watermark of 35, no new errors introduced by this plan.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `CMD_LOCK_STATUS 16` is fully admitted at the wire-protocol layer (firmware admission gate + host constant mirror) and ready for Plan 151-05 (the `MSG_DATA_PROTECTION_STATUS` catalog id) and Plan 151-08 (the actual `loop()` dispatch + operation implementation).
- Leonardo's Caterina-cliff margin after this plan is 1424 B — Plan 151-10 (which does the cold-rebuild MERGE-05 measurement after all firmware-touching plans land) should re-measure from this point forward; this plan's own build figures are recorded as an early indication only, per the plan's own instruction, not the authoritative 151-10 measurement.
- No requirement was flipped (`requirements: []`); this plan **advances** `LOCK-02`, whose checkbox flip belongs to Plan 151-13.

---
*Phase: 151-protection-readability-lock-status*
*Completed: 2026-08-20*

## Self-Check: PASSED

All 10 files created/modified verified present on disk; all 3 commits (firestarter `32c32e7`, `4df96c1`; firestarter_app `fe2634f`) verified present in their respective repositories' `git log --oneline --all`.
