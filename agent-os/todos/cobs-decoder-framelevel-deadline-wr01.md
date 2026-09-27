---
id: cobs-decoder-framelevel-deadline-wr01
title: Add a frame-level deadline to the firmware COBS decoder byte-wait (WR-01)
captured: 2026-06-01
status: pending
type: enhancement
target_milestone: v1.10
priority: medium
related_phase: 50
requirement: FRAME-02
source: .planning/phases/50-data-path-framing-layer-automatic-resync-dual-repo-lockstep/50-REVIEW.md (WR-01) + 50-VERIFICATION.md
---

# Frame-level deadline for the COBS decoder byte-wait (WR-01)

## The issue

Phase 50 deliberately removed the per-byte `timeout_ms = 2000` loop from
`firestarter/src/boards/rurp_serial_utils.cpp` (it was the SC1 cascade source — len_u16
corruption → wrong-length read → 2 s timeout per chunk). The replacement decoder waits for
bytes with an **unbounded** spin: `while (rurp_communication_available() <= 0) {}` (decoder
byte-wait ~line 125 and `_drain_to_delimiter` ~lines 92-98).

Consequence: if the host disconnects mid-frame, the firmware spins **forever** instead of the
old 2 s. The Phase 50 plan (D-01/D-03) assumed incomplete frames would be "governed by existing
op-level timeout machinery," but the decoder blocks inside `rurp_communication_read_data` and
never returns `OP_MSG_INCOMPLETE`, so that machinery is never reached.

Verifier classification (50-VERIFICATION.md): real residual risk but **does not defeat any
Phase-50 must_have** — it is a clean hang, not a corrupt transfer, and the 2 s *cascade* source
is gone. Classified advisory/deferred.

## The fix (proposed)

Reintroduce a timeout at the **frame level** (a single `millis()`-based deadline across the whole
frame read + drain), NOT a per-byte 2 s loop — so a stalled/disconnected host returns an error and
lets the op layer recover, without re-creating the per-chunk cascade that Phase 50 eliminated.
Pick a deadline generous enough not to trip on normal inter-byte gaps at 250000 baud.

## Where

- `firestarter/src/boards/rurp_serial_utils.cpp` — decoder byte-wait + `_drain_to_delimiter`.
- Add a firmware Unity case (truncated frame → bounded error return, no hang) under
  `firestarter/test/native/avr/test_cobs_data_frame/`.

Candidate landing: Phase 51 (command-channel framing migration) or a Phase 50 follow-up, operator's call.
