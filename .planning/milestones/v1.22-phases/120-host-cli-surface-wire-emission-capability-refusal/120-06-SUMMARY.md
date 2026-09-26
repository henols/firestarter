---
phase: 120-host-cli-surface-wire-emission-capability-refusal
plan: 06
subsystem: host-cli
tags: [python, click, sdp, wire-protocol, firestarter_app]

# Dependency graph
requires:
  - phase: 120-02
    provides: "COMMAND_SDP_UNLOCK=9, COMMAND_SDP_LOCK=10, FLAG_SKIP_SDP_UNLOCK=0x100, COMMAND_NAMES entries in firestarter/constants.py"
  - phase: 119 (all plans)
    provides: "firmware-side CMD_SDP_UNLOCK/CMD_SDP_LOCK payload-free handlers with NULL init/end"
provides:
  - "EpromOperator.sdp_unlock(name, eprom_data_dict, operation_flags=0) -> bool — payload-free cmd 9 operation"
  - "EpromOperator.sdp_lock(name, eprom_data_dict, operation_flags=0) -> bool — payload-free cmd 10 operation"
  - "build_flags(..., *, skip_sdp_unlock: bool = False) mapping FLAG_SKIP_SDP_UNLOCK onto the wire, keyword-only"
affects: [120-08, 120-09]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Payload-free operation-layer method: _operation_context + no main_phase_handler -> _run_state_machine falls through to _main_phase_simple (erase_eprom's exact shape, now shared by sdp_unlock/sdp_lock)."
    - "Wire-boundary test oracle: patch SerialCommunicator.find_and_connect with a side_effect that captures the composed command_dict, rather than asserting on the Python return value alone."

key-files:
  created: []
  modified:
    - "firestarter_app/firestarter/eprom_operations.py"
    - "firestarter_app/tests/test_eprom_operations.py"

key-decisions:
  - "sdp_unlock/sdp_lock pass no main_phase_handler to _run_state_machine, matching erase_eprom's shape exactly, per Phase 119 D-13 (firmware leaves init/end NULL for both commands)."
  - "skip_sdp_unlock is keyword-only (bare * after skip_erase) because both production callers (cli_handlers.build_arg_flags / _build_op_flags) pass the first four build_flags parameters positionally — a positional insertion would have silently shifted verbose/skip_erase (D-19)."
  - "FLAG_SKIP_SDP_UNLOCK is mapped inside build_flags rather than OR-ed in by a caller afterwards, unlike FLAG_OUTPUT_ENABLE/FLAG_CHIP_ENABLE in cli_handlers._build_op_flags — every wire-flag bit stays mapped in exactly one function."
  - "No D-10 host summary line is emitted from sdp_unlock/sdp_lock — that line belongs in the Click handler (plan 120-08 owns it) per RESEARCH F-11."
  - "The emitted command_dict['flags'] == 2 residue (FLAG_CAN_ERASE from database.py's DB rule) is pinned deliberately as firmware-inert, not suppressed — the wider 0x0D flag-surface honesty problem stays out of scope for this phase."

requirements-completed: []  # HOST-01 closes in 120-08; HOST-02 closes in 120-09. This plan closes neither (per plan frontmatter/prohibitions).

coverage:
  - id: D1
    description: "EpromOperator.sdp_unlock and sdp_lock exist as payload-free operations (cmd 9 / cmd 10), no main_phase_handler, no # data frame, no host DONE round-trip"
    verification:
      - kind: unit
        ref: "tests/test_eprom_operations.py::TestSdpOperationsWireShape::test_sdp_unlock_emits_cmd_9_payload_free"
        status: pass
      - kind: unit
        ref: "tests/test_eprom_operations.py::TestSdpOperationsWireShape::test_sdp_lock_emits_cmd_10_payload_free"
        status: pass
      - kind: unit
        ref: "tests/test_eprom_operations.py::TestSdpOperationsWireShape::test_sdp_unlock_setup_failure_returns_false"
        status: pass
      - kind: unit
        ref: "tests/test_eprom_operations.py::TestSdpOperationsWireShape::test_sdp_lock_setup_failure_returns_false"
        status: pass
    human_judgment: false
  - id: D2
    description: "build_flags maps FLAG_SKIP_SDP_UNLOCK via a keyword-only skip_sdp_unlock parameter (default False); BUG-1 characterization contract re-verified unmodified"
    requirement: "HOST-02"
    verification:
      - kind: unit
        ref: "tests/test_eprom_operations.py::TestSdpOperationsWireShape::test_skip_sdp_unlock_bit_reaches_the_wire"
        status: pass
      - kind: unit
        ref: "tests/test_bug_characterization.py::test_build_arg_flags_force_truthiness_not_existence"
        status: pass
    human_judgment: false
  - id: D3
    description: "Emitted command_dict['flags'] == 2 residue (DB FLAG_CAN_ERASE) pinned at the wire boundary as firmware-inert, not a defect"
    verification:
      - kind: unit
        ref: "tests/test_eprom_operations.py::TestSdpOperationsWireShape::test_sdp_command_flags_carry_the_db_can_erase_bit"
        status: pass
    human_judgment: false

# Metrics
duration: ~20min
completed: 2026-07-29
status: complete
---

# Phase 120 Plan 06: SDP Operator Methods + Wire Flag Mapping Summary

**`EpromOperator.sdp_unlock`/`sdp_lock` land as payload-free cmd 9/10 operations copy-shaped from `erase_eprom`, and `build_flags` grows a keyword-only `skip_sdp_unlock` mapping `FLAG_SKIP_SDP_UNLOCK` (0x100) onto the wire.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-07-29T10:53Z (approx, per STATE.md prior session marker)
- **Completed:** 2026-07-29T11:01Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments
- `EpromOperator.sdp_unlock` and `EpromOperator.sdp_lock` — payload-free operation-layer entry points for `COMMAND_SDP_UNLOCK` (9) / `COMMAND_SDP_LOCK` (10), copy-shaped from `erase_eprom`: no `main_phase_handler`, no `#` data frame, no host `DONE` round-trip. Docstrings state that a `True` return means only "the sequence was emitted", never a silicon-state claim, and that capability refusal lives in `firestarter/sdp_capability.py` (enforced by callers, not here).
- `build_flags(..., *, skip_sdp_unlock: bool = False)` — the ninth wire flag (`FLAG_SKIP_SDP_UNLOCK`, 0x100) is mapped inside the one function that maps wire flags, keyword-only so neither production caller's positional argument order can shift.
- Four new wire-boundary tests pin: the payload-free shape (cmd 9 / cmd 10, no `#` frame, no `DONE`) plus each method's setup-failure `False` path; the DB's firmware-inert `FLAG_CAN_ERASE` residue (`flags == 2` for `at28c256`); and the new `0x100` bit reaching the composed `command_dict["flags"]`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add EpromOperator.sdp_unlock and EpromOperator.sdp_lock as payload-free operations** - `8510c59` (feat)
2. **Task 2: Add the keyword-only skip_sdp_unlock parameter to build_flags and re-verify the BUG-1 contract** - `93d0d62` (feat)
3. **Task 3: Pin the payload-free operation shape and the emitted flags value** - `48edd92` (test)

_Note: no separate plan-metadata commit inside the submodule — the meta-repo final commit (below) covers SUMMARY.md/STATE.md/ROADMAP.md._

## Files Created/Modified
- `firestarter_app/firestarter/eprom_operations.py` — added `sdp_unlock`/`sdp_lock` methods (adjacent to `erase_eprom`); imported `COMMAND_SDP_UNLOCK`, `COMMAND_SDP_LOCK`, `FLAG_SKIP_SDP_UNLOCK`; widened `build_flags` signature with the keyword-only `skip_sdp_unlock` parameter.
- `firestarter_app/tests/test_eprom_operations.py` — added `TestSdpOperationsWireShape` (4 tests: two payload-free-shape tests each also covering the setup-failure path, one `flags == 2` residue test, one `skip_sdp_unlock` wire-bit test) plus two module-level helpers (`_at28c256_programmer_dict`, `_capture_written_frames`).

## Decisions Made
- Mirrored `erase_eprom`'s exact shape for both SDP methods rather than inventing a new pattern — the plan's own precedent, and it keeps the payload-free contract (no data frame, no `DONE`) trivially true by construction (no code path to emit either).
- Chose to test at the wire boundary (the composed `command_dict` captured via a patched `find_and_connect` side_effect) rather than only asserting the Python return value, per the plan's HOST-01/HOST-02 oracle requirement.
- Split "shape + setup-failure" into two separate test methods per SDP command (4 tests total) rather than one combined test per command — improves failure localization without violating the plan's four-named-test acceptance criteria (all four named tests exist and pass; the two setup-failure legs are additional coverage the acceptance criteria explicitly required be present).
- Did not emit the D-10 host summary line from either method — that is plan 120-08's Click-handler responsibility per RESEARCH F-11.

## Deviations from Plan

### Auto-fixed Issues

**1. [Self-caught during editing, no rule needed] Restored an accidentally-deleted pre-existing assertion**
- **Found during:** Task 3 (test file edit)
- **Issue:** My initial `Edit` anchor for appending new test content did not include the original file's final line (`assert setup_called[0][0] == "W27C512"`, part of the pre-existing `test_eeprom_blank_check_still_reaches_setup`), so that line was momentarily dropped from the diff.
- **Fix:** Restored the line to its original test before running any verification or committing; confirmed via `git diff --stat` that the final committed diff for `tests/test_eprom_operations.py` is additions-only (190 insertions, 0 deletions).
- **Files modified:** `firestarter_app/tests/test_eprom_operations.py`
- **Verification:** `git diff tests/test_eprom_operations.py | grep -c '^-[^-]'` returns `0` before commit.
- **Committed in:** `48edd92` (Task 3 commit — the restoration happened before this commit, so the committed history never contains the deletion)

---

**Total deviations:** 1 self-caught editing slip, corrected before commit. No scope creep; no plan-required behavior changed.
**Impact on plan:** None — corrected in-flight, verified additions-only before the task commit.

## Issues Encountered
None beyond the self-caught editing slip above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `EpromOperator.sdp_unlock`/`sdp_lock` are ready for plan 120-08's `dev sdp` CLI command (which will add the capability-refusal check via `sdp_capability.py`, the D-10 summary line, and close HOST-01).
- `build_flags(skip_sdp_unlock=...)` is ready for plan 120-09's `write --skip-sdp-unlock` CLI flag (which will close HOST-02) and for its auto-set-on-refused-parts behavior (D-01/D-04 in STATE.md's Phase 120 corrections).
- No blockers. `firestarter/cli_handlers.py`, `firestarter/serial_comm.py`, `firestarter/messages.py`, and `firestarter/data/` are all byte-untouched by this plan (confirmed via scoped `git diff --stat`). The firmware sub-repo (`/workspaces/firestarter`) is untouched (`git status --porcelain` empty).
- HOST-01 and HOST-02 remain **Pending** in `.planning/REQUIREMENTS.md` — not marked Complete by this plan, per its explicit prohibition.

---
*Phase: 120-host-cli-surface-wire-emission-capability-refusal*
*Completed: 2026-07-29*

## Self-Check: PASSED

- FOUND: `.planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-06-SUMMARY.md`
- FOUND commit `8510c59` (Task 1) in `firestarter_app`
- FOUND commit `93d0d62` (Task 2) in `firestarter_app`
- FOUND commit `48edd92` (Task 3) in `firestarter_app`
