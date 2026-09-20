---
created: 2026-09-20T00:00:00Z
title: The 3.0 s read-abort acceptance window is untested at its true failure boundary
area: host
resolves_phase: null
source: .planning/phases/202-one-comparison-engine-on-the-host/202-REVIEW.md § WR-01
files:
  - firestarter_app/firestarter/eprom_operations.py (READ_ABORT_ACCEPTANCE_WINDOW_S, and _drive_region_compare's four-condition D-08 discrimination)
  - firestarter_app/tests/test_eprom_operations.py (TestVerifyEpromReadAbort — where the boundary leg would go)
---

## Problem

Phase 202 tells a deliberate host-initiated read-stop apart from a genuine hardware timeout by
asking whether the firmware's `MSG_ERR_TIMEOUT` frame arrived within
`READ_ABORT_ACCEPTANCE_WINDOW_S` (3.0 s) of the host deciding to stop acking. The constant's
documented reasoning — the firmware's own 1 s `op_wait_for_ack` plus a few ms of transmission — is
sound for the firmware's half. It does not bound the host's half.

That 3.0 s is real wall-clock. It spans a `time.monotonic()` call, GIL contention, OS scheduling
and USB-serial driver latency, none of which the firmware's 1 s figure constrains. If a genuinely
deliberate abort's frame lands past 3.0 s under host load — a busy CI runner, a slow USB bridge, or
`dev test`-style back-to-back operations queuing for scheduler time — `_drive_region_compare`
reports exit 2 (hardware or transport failure) for what is actually exit 1 (mismatch).

That is the precise error the discrimination exists to prevent, approached from the direction the
tests do not cover. `test_timeout_outside_the_acceptance_window_returns_two` only proves the window
fires correctly on a frame that genuinely arrived late. Nothing exercises it from just *inside* the
boundary, so nothing proves an abort at, say, 2.9 s under injected jitter still resolves to
"aborted".

The failure is quiet and misdirecting: an operator sees `verify` claim a hardware fault on a chip
that is merely mismatching, and starts debugging the shield.

## Fix

Either route is acceptable; they are not exclusive.

1. Add the missing boundary leg — inject a delay just inside the window and assert the
   discrimination still resolves to "aborted", so the edge is pinned rather than assumed.
2. If the window stays fixed, say so at the constant: record that a false hardware error under
   heavy host load is a known, accepted outcome, so the next person reading a "verify says hardware
   error but the chip just mismatches" report does not chase it as a hardware bug.

Making the window configurable is a third option, worth it only if a constrained environment
actually trips it.

## Why it was not fixed in phase 202

Phase 202's own invariants asked whether the abort-vs-fault discrimination can misfire in either
direction. It surfaced this as a design tradeoff rather than a defect, and no phase must-have
depends on it. The phase verified 38/38 without it.
