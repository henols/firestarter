---
phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half
plan: 07
subsystem: firmware
tags: [bench-measurement, sdp, eeprom28c, micros, leonardo, provenance]

# Dependency graph
requires:
  - phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half (plan 04)
    provides: "the two unconditional LOG_ID/LOG_ID_U32 report lines bracketing eeprom28c_emit_command_sequence with micros(), and the sdp_seq_len * AT28C_TBLC_MAX_US runtime budget check that this plan's real-board run exercises"
  - phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half (plan 06)
    provides: "118-NONREGRESSION.md's recorded Leonardo flash/RAM figures (25680/28672, 1998/2560), used here as the drift check before upload"
provides:
  - "118-MEASUREMENT.md — the milestone's only empirical (real-hardware) result: a measured 572 us SDP-disable emit duration on a real Arduino Leonardo, with full command/identity/build provenance and a line-by-line validation-ceiling review"
  - "OBS-04 marked Complete in REQUIREMENTS.md, closing all five OBS requirements (OBS-01..05)"
affects: ["119 (LOCK-06 flash/timing headroom judgement needs this raw 572us/600us figure)", "122 (close — the honesty-ledger close cites this as the one real measurement in the milestone)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Bench-measurement artifact pattern: a standalone {phase}-MEASUREMENT.md (mirroring RED-BASELINE.md / 116-PREMISE.md) carrying command + identity + build + raw-log provenance, explicitly excluded from PROTOCOL-LEDGER to prevent a ceiling-crossing misread"

key-files:
  created:
    - .planning/phases/118-observe-auto-unlock-visible-opt-out-able-fw-half/118-MEASUREMENT.md
  modified:
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Per D-12, ran autonomously with zero operator checkpoints; verified controller: port identity by command (firestarter fw against all three present devices: /dev/ttyACM0=leonardo, /dev/ttyACM1=uno, /dev/ttyUSB0=uno328pb) rather than assuming a device number."
  - "Used a 64-byte incrementing-byte payload rather than padding to the full 32768-byte at28c256 size — the host's write path performs no file-size-vs-memory-size validation before the INIT phase, and the SDP unlock happens entirely within eeprom28c_write_init before any payload byte is ever transferred, so no padding was needed to reach the measurement."
  - "The plan anticipated a --force-demoted chip-id-mismatch warning ahead of the unlock lines; it did not appear because at28c256's DB entry carries chip-id: 0 (skip ID check), so eeprom28c_check_chip_id's early-return path is never reached for this chip regardless of socket contents. Recorded in 118-MEASUREMENT.md §3 as a stronger, not weaker, confirmation of D-01 (the report lines are unconditional with no identity-check gate at all in front of them for this chip)."

requirements-completed: [OBS-04]

coverage:
  - id: D1
    description: "One real Leonardo run: firestarter write at28c256 --force against an empty socket, capturing the unconditional SDP-unlock report pair and a measured emit duration (572 us) against the 6x100us=600us t_BLC budget, with MSG_WARN_SDP_TBLC_EXCEEDED confirmed absent"
    requirement: "OBS-04"
    verification:
      - kind: manual_procedural
        ref: "118-MEASUREMENT.md §2-4 (verbatim command, controller: identity before/after upload, verbatim raw log, the number)"
        status: pass
    human_judgment: false
  - id: D2
    description: "118-MEASUREMENT.md's wording reviewed line-by-line against the validation ceiling: no sentence readable as bench-validating 0x0D on AT28C silicon; 0x0D stays UNVERIFIED; no support_status change; no PROTOCOL-LEDGER entry; 84-chip count unchanged"
    requirement: "OBS-04"
    verification:
      - kind: manual_procedural
        ref: "118-MEASUREMENT.md §1 and §6 (emitter-not-chip statement before any number; verbatim permitted/forbidden claims quoted; explicit PROTOCOL-LEDGER exclusion stated with reason)"
        status: pass
    human_judgment: false

# Metrics
duration: 25min
completed: 2026-07-28
status: complete
---

# Phase 118 Plan 07: OBS-04 Leonardo SDP Emit Duration Measurement Summary

**Measured the AT28C SDP-disable emitter's wall-clock duration on a real Arduino Leonardo — 572 microseconds against a 600-microsecond t_BLC budget — with full command/identity/build provenance in a dedicated `118-MEASUREMENT.md`, closing OBS-04 and all five OBS requirements.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-07-28
- **Completed:** 2026-07-28
- **Tasks:** 2
- **Files modified:** 2 (1 created, 1 modified)

## Accomplishments

- Identified the Leonardo by command, not assumption: `firestarter fw` run against all three present devices (`/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0`) — `/dev/ttyACM0` was the only one whose `controller:` line named `leonardo`.
- Built `pio run -e leonardo` at firmware HEAD `1880054` and confirmed Flash 25680/28672 (89.6%) / RAM 1998/2560 (78.0%) matched `118-NONREGRESSION.md`'s Wave 6 figures exactly before uploading — no drift.
- Uploaded via `pio run -t upload -e leonardo --upload-port /dev/ttyACM0`; re-ran `firestarter fw` afterward and confirmed the board now reports `3.0.0b11:leonardo` (it had reported `3.0.0b13` immediately before upload, proving the image actually changed).
- Issued exactly one `firestarter write at28c256 --force <64-byte payload>` against the empty socket. Captured verbatim: the unconditional `I: SDP unlock: disabling write protection` / `I: SDP unlock emitted in 572 us` report pair, then the expected downstream `ERROR: Not blank, at 0x000000, v: 0x40` failure from the empty socket.
- Wrote `118-MEASUREMENT.md`: the emitter-not-the-chip statement first, full provenance block, complete raw log, the number (572 µs vs. a 600 µs = `6 × AT28C_TBLC_MAX_US` budget, `MSG_WARN_SDP_TBLC_EXCEEDED` confirmed absent), socket-state explanation, verbatim validation-ceiling quote with explicit PROTOCOL-LEDGER exclusion, and named downstream consumers (Phase 119 LOCK-06).
- Marked **OBS-04** Complete in `REQUIREMENTS.md` (checkbox + traceability table), closing all five OBS requirements (OBS-01..05).

## Task Commits

Both tasks' output landed in one commit (Task 1 produced no file by itself — only the captured command output Task 2 wrote up):

1. **Task 1 (bench run) + Task 2 (write-up)** — `6b07a0e` — `docs(118-07): record the measured Leonardo SDP emit duration with provenance (OBS-04)`

**Plan metadata** (this SUMMARY + STATE.md + ROADMAP.md): committed separately below.

No commits were made in either sub-repo — `firestarter` was only built and uploaded, never edited (`git -C firestarter status --short` clean); `firestarter_app` was not touched at all (its pre-existing unrelated dirty files — `.gitignore`, `.coverage`, `.planning/config.json`, `SECURITY.md`, `doc/lockable-proms.md`, `write_test_port.sh` — are unchanged from prior plans' baselines).

## Files Created/Modified

- `.planning/phases/118-observe-auto-unlock-visible-opt-out-able-fw-half/118-MEASUREMENT.md` — created; the standalone measurement artifact with full D-13 provenance.
- `.planning/REQUIREMENTS.md` — OBS-04 checkbox flipped to `[x]` with a parenthetical citing the measured value; traceability table row `OBS-04` → `Complete`.

## Decisions Made

- No operator checkpoint of any kind was inserted, per D-12 — the operator's 2026-07-28 statement that the Leonardo is connected with an empty socket was treated as already on the record, and the plan's own `autonomous: true` forbade re-asking about socket state.
- Port identity was verified by running `firestarter fw` against every present candidate (`/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0`) rather than assuming device numbering — this is a Claude-side check, not an operator confirmation, and it also positively confirmed the two Uno-class boards present were correctly excluded from this Leonardo-only measurement.
- Chose a 64-byte incrementing-byte payload over padding to the full 32768-byte `at28c256` size. Verified in source (`eprom_operations.py` / `cli_handlers.py`) that no file-size-vs-`memory-size` validation gates the write before the INIT phase, and that the SDP unlock (`eeprom28c_write_init`) completes entirely before any payload byte transfer — so the short file was sufficient and no padding was needed.
- Documented, rather than treated as a failure, that the anticipated `--force`-demoted chip-id-mismatch warning did not appear: `at28c256`'s database entry carries `chip-id: 0` (skip ID check), so the identity-check path is bypassed entirely for this chip regardless of socket contents. This is recorded in `118-MEASUREMENT.md` §3 as strengthening, not weakening, the D-01 "unconditional" claim.

## Deviations from Plan

**None requiring a deviation rule.** The run succeeded on the first attempt (D-14's failure path was not needed). The one divergence from the plan's literal expectation — the absent chip-id-mismatch warning — is not a bug, missing functionality, or blocker; it is a correct consequence of `at28c256`'s DB-configured `chip-id: 0`, documented in place (§3 of `118-MEASUREMENT.md`) rather than "fixed," since there is nothing to fix.

## Issues Encountered

None. Port identification, build, upload, and the single write command all succeeded on the first attempt. The build figures matched `118-NONREGRESSION.md` exactly, so no drift investigation was needed.

## Validation-Ceiling Review (line-by-line, recorded per the plan's acceptance criterion)

Read `118-MEASUREMENT.md` in full, sentence by sentence, checking for any wording readable as claiming AT28C silicon accepted the SDP sequence, entered/left a protected state, or that t_BLC was met as accepted by a die. **Result: none found.** Every claim in the document has code, a captured log line, a git blob/commit, or a `pio run` size-report figure as its subject. §1 states the emitter-not-chip framing before any number appears; §5 explicitly explains why the empty socket does not compromise the number; §6 quotes REQUIREMENTS.md's permitted/forbidden claims verbatim and states which side of the line this measurement sits on, plus an explicit statement that the number must not be recorded in the PROTOCOL-LEDGER, with the reason. `0x0D` remains `UNVERIFIED`; the 84-chip count and `support_status` fields were not touched anywhere in this plan.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- All five OBS requirements (OBS-01..05) are now Complete. Phase 118 is requirement-complete.
- Phase 119's LOCK-06 headroom judgement has a citable, provenance-carrying figure (572 µs measured / 600 µs budget) to reference rather than re-measure, unless the emitter's code path changes.
- No blockers for Phase 119. This plan touched no firmware or host source file — only the meta-repo `.planning/` artifacts listed above — so the firmware submodule's working tree remains exactly at `1880054`, unmodified.

## Self-Check: PASSED

- FOUND: `/workspaces/.planning/phases/118-observe-auto-unlock-visible-opt-out-able-fw-half/118-MEASUREMENT.md`
- FOUND: commit `6b07a0e` in `/workspaces` (meta repo)
- FOUND: `.planning/REQUIREMENTS.md` shows `OBS-04` as `[x]` and `Complete` in the traceability table

## Self-Check: PASSED (post-write verification)

- FOUND: `/workspaces/.planning/phases/118-observe-auto-unlock-visible-opt-out-able-fw-half/118-MEASUREMENT.md`
- FOUND: `/workspaces/.planning/phases/118-observe-auto-unlock-visible-opt-out-able-fw-half/118-07-SUMMARY.md`
- FOUND: commit `6b07a0e` in git log
- FOUND: commit `70b320d` in git log

---
*Phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half*
*Completed: 2026-07-28*
