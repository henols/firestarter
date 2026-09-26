---
phase: 08-convert-state-machine-prefix-call-sites-ok-init-main-end
plan: 03
subsystem: protocol
tags: [serial, id-frame, host-parser, sentinel-byte, pytest, python]

# Dependency graph
requires:
  - phase: 08-convert-state-machine-prefix-call-sites-ok-init-main-end
    plan: 01
    provides: catalog entries for MSG_INIT_DONE/MSG_MAIN_DONE/MSG_END_DONE/MSG_OK_REV/MSG_OK_CFG/MSG_OK_FW_HANDSHAKE as id_frame
  - phase: 08-convert-state-machine-prefix-call-sites-ok-init-main-end
    plan: 02
    provides: u16 len field (W-04) + conftest.build_frame updated to u16

provides:
  - "EXPECTED_PREFIXES no longer contains INIT/MAIN/END (W-01 host parser surgical removal)"
  - "STATE_MACHINE_PREFIXES = [] (empty; catalog format strings own rendering)"
  - "_log_rurp_feedback dead branch removed (no more 'Done' rewrite for state-machine prefixes)"
  - "_format_message sentinel-aware renderer for MSG_OK_REV/MSG_OK_CFG/MSG_OK_FW_HANDSHAKE"
  - "9 Wave-0 gap tests in test_decoder.py: INIT/MAIN/END ID-frame + P-02/P-03/P-04 sentinel rendering"
  - "Host parser ID-frame ready: can decode every catalog-declared state-machine ack as soon as Plan 04 firmware emits them"

affects:
  - phase-08-plan-04
  - phase-08-plan-05

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "_format_message sentinel-byte pattern: check msg_id, inspect 0xFF sentinel, return custom render or None to fall through to generic"
    - "Wave-0 gap tests: add failing tests first, then implement — proves the rendering is actually tested not just assumed"

key-files:
  created: []
  modified:
    - "firestarter_app/firestarter/serial_comm.py"
    - "firestarter_app/tests/test_decoder.py"

key-decisions:
  - "Phase 08-03: _format_message added as a new method on SerialCommunicator; called by _decode_id_frame before generic catalog rendering; returns None to signal fall-through — minimal invasiveness"
  - "Phase 08-03: INIT/MAIN/END removed from EXPECTED_PREFIXES; PREFIX_REGEX no longer matches those line prefixes; existing text path for OK + DATA unchanged until Plan 04/05"
  - "Phase 08-03: STATE_MACHINE_PREFIXES kept as symbol (empty list) rather than deleted — other modules may import it; comment explains W-01 migration"
  - "Phase 08-03: INIT/MAIN/END tests pass immediately (catalog was already wired in Plan 01); P-02/P-03/P-04 tests required the new sentinel renderer (RED→GREEN confirmed)"

patterns-established:
  - "Sentinel 0xFF rendering pattern: _format_message checks msg_id + sentinel byte position, returns formatted string or None for generic fall-through"

requirements-completed:
  - LMIG-03

# Metrics
duration: 20min
completed: 2026-05-18
---

# Phase 08 Plan 03: Host Parser Surgical Removal + P-02/P-03/P-04 Sentinel Rendering Summary

**Host parser surgically updated: INIT/MAIN/END removed from line-prefix matching; sentinel-aware _format_message renders MSG_OK_REV/MSG_OK_CFG/MSG_OK_FW_HANDSHAKE; 9 Wave-0 decoder tests added — all 23 decoder tests green.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-05-18T19:30:00Z
- **Completed:** 2026-05-18T19:50:00Z
- **Tasks:** 2 (TDD: RED tests + GREEN implementation, committed together as specified)
- **Files modified:** 2

## Accomplishments

- Removed "INIT", "MAIN", "END" from `EXPECTED_PREFIXES` — PREFIX_REGEX no longer matches state-machine text acks
- Emptied `STATE_MACHINE_PREFIXES = []` with W-01 migration comment
- Removed dead `if response.type in STATE_MACHINE_PREFIXES: message = "Done"` branch from `_log_rurp_feedback`
- Added `_format_message` sentinel-aware renderer to `SerialCommunicator` for P-02/P-03/P-04 IDs
- Added 9 Wave-0 gap tests for INIT/MAIN/END ID-frame decode and P-02/P-03/P-04 sentinel rendering
- All 27 tests (23 decoder + 4 fwguard) pass; no regressions

## Surgical Edit Sites in serial_comm.py

| Site | Location | Pre-edit | Post-edit |
|------|----------|----------|-----------|
| Site 1: EXPECTED_PREFIXES | ~line 129-139 | list included "MAIN", "INIT", "END" | removed; comment explains W-01 |
| Site 2: STATE_MACHINE_PREFIXES | ~line 152 | `["INIT", "MAIN", "END"]` | `[]  # W-01 migration comment` |
| Site 3: _log_rurp_feedback | ~line 288-289 | `if type in STATE_MACHINE_PREFIXES: message = "Done"` | deleted (replaced with comment) |
| Site 4: _format_message (new) | before _decode_id_frame | absent | new method; wired into _decode_id_frame before generic rendering |

## New Tests Added

9 new tests + 0 updated (WR-03 test was already correct from Plan 01):

| Test | Type | Expected Result |
|------|------|-----------------|
| test_init_done_arrives_as_id_frame | W-01/W-02 | response.type=="INIT", message=="(init done)" |
| test_main_done_arrives_as_id_frame | W-01/W-02 | response.type=="MAIN", message=="(main done)" |
| test_end_done_arrives_as_id_frame | W-01/W-02 | response.type=="END", message=="(end done)" |
| test_fw_handshake_p04_with_hw_revision_decodes | P-04 | "FW: 2.0.11-dev, HW: Rev1, Cmd: 0x0f" |
| test_fw_handshake_p04_no_hw_revision_decodes | P-04 | "FW: 2.0.11-dev, Cmd: 0x0f" |
| test_ok_rev_p02_with_override_decodes | P-02 | "Rev2, Override HW: Rev1" |
| test_ok_rev_p02_no_override_decodes | P-02 | "Rev1" |
| test_ok_cfg_p03_with_override_decodes | P-03 | "R1: 10000, R2: 4700, Override HW: Rev2" |
| test_ok_cfg_p03_no_override_decodes | P-03 | "R1: 10000, R2: 4700" |

**RED gate:** 6 of 9 new tests failed before serial_comm.py was updated (INIT/MAIN/END already passed via catalog; P-02/P-03/P-04 sentinel rendering was absent).

**GREEN gate:** All 23 tests pass after _format_message added and EXPECTED_PREFIXES edited.

**pytest summary:** `23 passed in 0.24s` (test_decoder.py); `27 passed in 0.26s` (full suite)

## Task Commits

1. **Tasks 1+2: RED tests + GREEN implementation (committed together per plan)** - `ac23b85` (feat)

## Files Created/Modified

- `/workspaces/firestarter_prom/firestarter_app/firestarter/serial_comm.py` — 4 surgical edit sites; new _format_message method; new MSG_OK_REV/CFG/FW_HANDSHAKE imports
- `/workspaces/firestarter_prom/firestarter_app/tests/test_decoder.py` — struct import added; MSG_OK_REV/CFG/MSG_INIT_DONE/MSG_MAIN_DONE/MSG_END_DONE imports added; 9 new tests appended to TestIdFrameDecoder

## Decisions Made

- `_format_message` added as an instance method on `SerialCommunicator` (not a module-level function) — consistent with other private methods; receives `msg_id`, `params` (already decoded), and `entry` for possible future use; returns `str | None`
- The sentinel 0xFF check happens on the decoded int value (after `_decode_param` runs), not on raw bytes — cleaner and avoids duplicating param-decode logic
- INIT/MAIN/END tests pass immediately in RED state because the catalog was already wired in Plan 01 (severity-band routing correct); only P-02/P-03/P-04 needed the sentinel renderer to be RED

## Deviations from Plan

### Notes

The plan mentioned updating `test_wire_format_text_catalog_id_rejected_as_id_frame` to "drop 0x06 from the rejection set." Inspecting the test showed it was **already updated in Plan 01** (the test already asserts `CATALOG[MSG_OK_FW_HANDSHAKE].wire_format == "id_frame"` and no longer rejects 0x06 as a binary frame). No changes to that test were needed in Plan 03. This is not a deviation — Plan 01 did its job.

**Total deviations:** None - plan executed as written (one acceptance criterion was pre-satisfied by Plan 01).

## Issues Encountered

None.

## Host Parser State After Plan 03

| Ack type | Before Plan 03 | After Plan 03 |
|----------|---------------|---------------|
| INIT/MAIN/END | Matched by PREFIX_REGEX as text (EXPECTED_PREFIXES included them) | Removed from EXPECTED_PREFIXES; only arrive as ID frames |
| MSG_INIT_DONE/MSG_MAIN_DONE/MSG_END_DONE | Could decode as ID frames but text path also existed | ID-frame path only; tested |
| MSG_OK_REV | Rendered "Rev%u (eff: %u)" via catalog | Sentinel-aware: "Rev{eff}" or "Rev{eff}, Override HW: Rev{phys}" |
| MSG_OK_CFG | Rendered "R1: %lu, R2: %lu, Cfg: %u" | Sentinel-aware: "R1: {r1}, R2: {r2}" or with "Override HW: Rev{n}" |
| MSG_OK_FW_HANDSHAKE | Rendered "HW: %u, Cmd: 0x%02x, FW: %s" | Sentinel-aware: "FW: {fw}, HW: Rev{hw}, Cmd: 0x{cmd}" or no HW clause |
| OK/DATA text prefix | Matched by PREFIX_REGEX | Unchanged — stays until Plan 04/05 land firmware conversions |

## Next Phase Readiness

- Host parser is fully ID-frame ready for state-machine acks
- Plan 04 can convert firmware `send_ack_const`/`send_ack_format`/`send_main_done`/`send_init_done`/`send_end_done` call-sites — host will decode them correctly on first emit
- Plan 05 (DATA streaming + MSG_DATA_CHUNK) can proceed independently

---
*Phase: 08-convert-state-machine-prefix-call-sites-ok-init-main-end*
*Completed: 2026-05-18*
