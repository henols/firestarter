---
phase: 97-pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program
plan: 02
subsystem: testing
tags: [rca, bench, pre-01, rca-01, am27c020, 0x08, eprom-quick, held-rail, safe-01, operator-witnessed]

# Dependency graph
requires:
  - phase: 97 (plan 01)
    provides: EVIDENCE.{md,json} Cell A schema + 97-RCA-FINDINGS PRE-01/RCA-01 sections + pinned held-rail proxy values + Wave-0 gate scripts (check_pre01/check_signature)
provides:
  - PRE-01 pre-flight captured (N=3 byte-identical read oracle, blank-state SHA256, 0x08 decode confirmed)
  - RCA-01 reproduced on real silicon (0x08 writes 0 bits @ 0x000000, bad bytes 1/1, retries 20) at the CORRECTED rig (VPP 13.0V + JP4 closed); chip pristine
  - Code-level exoneration of RC-2-routing (H2 disproven: -f 0x188 -> physical 0x89 asserts P1) + RC-1 premise confirmed (pin 31 = A18 per info decode)
  - hold_rail.py non-invasive held-rail bench tool (works around the DTR-reset tooling bug)
affects: [97-03 (W27C512 0x07 differential control + RC-1/RC-2 final verdicts + RCA-03 named cause), 98-fix]

# Tech tracking
tech-stack:
  added:
    - ".planning/v1.18/bench/hold_rail.py — held-rail static proxy that keeps the serial port open (no DTR-reset), reusing installed firestarter framing"
  patterns:
    - "Corrected-rig RCA: remove trivial confounds (VPP pot 12.0->13.0V, JP4 open->closed) BEFORE spending the single irreversible attempt, so a 0-bits result is unambiguous"
    - "Code-decode substitution: when a bench measurement is tooling-blocked, answer the same question by decoding the control register through rurp_map_ctrl_reg_for_hardware_revision rather than fabricating (D-02)"

key-files:
  created:
    - .planning/v1.18/bench/hold_rail.py
    - .planning/debug/resolved/held-rail-dev-reg-timeout.md
  modified:
    - .planning/v1.18/bench/EVIDENCE.json
    - .planning/v1.18/bench/EVIDENCE.md
    - .planning/phases/97-.../evidence/97-RCA-FINDINGS.md

key-decisions:
  - "Used `write -b` for the single attempt (skip blank-check ONLY, Phase-92 decouple) — REQUIRED because the chip is non-blank (0x02@0x0000) so plain write aborts at blank-check before programming. Justified deviation from the literal 'no -b' must-have; SAFE-01 intact (flags=0x08, no FLAG_FORCE, over-voltage guard untouched). Operator-approved."
  - "Adjusted VPP pot 12.0->13.0V and moved JP4 open->closed (fw info 32-pin=Closed) BEFORE the attempt — both confounds corrected so the 0-bits result is unambiguous."
  - "Held-rail pin-1/pin-31 DMM recorded as 'not measured' (D-02, never fabricated) — blocked by a real tooling bug (DTR-reset-on-close); the routing question it was for is answered by code RCA instead (H2 disproven)."
  - "RC-1/RC-2 FINAL verdicts deferred to Plan 03 (the 0x07 differential), per the RCA-FINDINGS structure; Plan 02 delivers the reproduced signature + the code-level routing exoneration that feeds them."

requirements-completed: [PRE-01, RCA-01]

# Metrics
duration: ~1 session (operator-witnessed bench)
completed: 2026-06-30
---

# Phase 97 Plan 02: PRE-01 Pre-Flight + RCA-01 Reproduction Summary

**Operator-witnessed bench session (Leonardo + RURP Rev 2.0, fw 3.0.0b10 / bccd995) that captured the PRE-01 writability pre-flight and reproduced the RCA-01 0-bits-programmed failure on the seated AM27C020 — at a CORRECTED rig (VPP 13.0V, JP4 closed) so the 0-bits outcome is unambiguous — with exactly ONE irreversible program attempt, the chip left pristine, and SAFE-01 held throughout. A held-rail DMM tooling bug surfaced mid-session was root-caused (debug session), worked around (hold_rail.py), and the routing question it blocked was answered by code instead.**

## Accomplishments

### PRE-01 — Tier-0 writability pre-flight (captured, never fabricated)
- **Decode confirmed:** `firestarter info AM27C020` → UV-EPROM, DIP32, 0x40000, VPP 13.0V, protocol **0x08**, chip-id **0x197**. Pinout decode also surfaced **pin 31 = A18** (RC-1 premise) and the fw jumper guidance **32-pin = JP4 Closed**.
- **Read oracle N=3 byte-identical:** `dev consistency-check --runs 3` → PASS, distinct SHAs = 1. **Blank-state SHA256 = `90cd45f5343cd938006f20635de39479159c51b9d56c1b6f1fb23075ed567297`**.
- **Blank check:** NOT-BLANK @ `0x000000` = `0x02` (matches v1.15).
- **Baseline rails:** as-found VPP **12.0V** (below 12.5–13.0V band) → operator set **13.0V**; VPE 13.8V → 15.1V (shares regulator).

### RCA-01 — reproduced on real silicon (corrected rig)
- **Single attempt:** `firestarter -v write -b AM27C020 probe.img` (1-byte `0x00` over `0x02` @ 0x0000 = one legal 1→0). Flags = **0x08 (SkipBlankCheck only)** — no FLAG_FORCE.
- **Signature:** `ERROR: Failed to write memory, 0x000000, retries: 20, bad bytes: 1` → **0 bits programmed**. `retries 20` matches the v1.15 seed.
- **Chip pristine:** post-attempt N=3 oracle == pre-attempt SHA (`90cd45f5…`). Exactly one irreversible attempt spent.
- **Writability = INDETERMINATE pre-fix** (D-01/D-02) — 0-flip is consistent with both "broken path" and "OTP"; NOT read as OTP, does NOT trigger deferral.
- **Both confounds corrected first** (VPP 13.0V, JP4 closed) → the 0-bits failure is **not** a voltage or jumper problem.

### Root-cause direction (feeds Plan 03)
- **H2 (VPP-not-reaching-pin-1) DISPROVEN by code:** `-f 0x188` → `rurp_map_ctrl_reg_for_hardware_revision` (REVISION_2_0) → physical **`CTRL 0x89` = REGULATOR + P1 + VPE_DROP_REV2**; the P1_ENABLE/A18 alias is gated on the unset A18 input bit. VPP **does** reach pin 1.
- Cause sharpened to **RC-1: pin 31 modeled as address line A18, not a held PGM pin** — a firmware/pinout issue. Final RC-1/RC-2 verdicts + RCA-03 named cause are Plan 03's deliverable.

## Deviations from Plan
1. **`-b` used for the single attempt (vs literal "no -b" must-have).** Necessary: chip is non-blank, so plain write aborts at the blank-check before programming. Safe: Phase-92 decoupled `-b` to skip ONLY the blank-check (not erase), and it does not relax the over-voltage SAFE-01 guard (that needs `--force`). Operator-approved via checkpoint.
2. **Held-rail pin-1/pin-31 DMM not physically measured.** A real tooling bug (DTR-reset-on-close drops the latched rail) blocked the static proxy. Root-caused + archived (`debug/resolved/held-rail-dev-reg-timeout.md`), non-invasive `hold_rail.py` workaround created, proper fix deferred to Phase 98. The routing question it was for was answered by code (H2 disproven) — recorded "not measured", never fabricated (D-02).
3. **Plan-ordered held-rail-before-attempt** became moot: VPP/JP4 confounds were corrected first and the proxy was tooling-blocked; the attempt proceeded on the corrected rig and the routing was code-confirmed.

## Issues Encountered
- **Held-rail `dev reg -f` timeout** (operator-reported blocker): set rail → host `expect_ack` times out (firmware button-wait, UART down) → `finally: _disconnect_programmer()` closes port → DTR-reset → rail drops. Root cause H1 confirmed; H2 disproven. Fix is a Phase-98 source change (host `--hold-seconds`/`dtr=False`, or fw non-blocking hold-mode). Bench unblocked via `hold_rail.py` (keeps port open).
- pyserial does not lock the port exclusively → a manual `firestarter` command run alongside `hold_rail.py` collides and resets the board. Operator guidance: while a hold is running, measure only (type no `firestarter` command).

## Verification
- `python3 .planning/v1.18/bench/check_pre01.py` → PASS (blank-state SHA + controller captured).
- `python3 .planning/v1.18/bench/check_signature.py` → PASS (`bits_flipped=0`, pre==post SHA → pristine).
- 97-RCA-FINDINGS.md PRE-01 + RCA-01 sections filled with real captures; Bench Discipline Log row 02 complete.
- Exactly one irreversible program attempt spent; SAFE-01 held (flags=0x08, no `--force`).

## Self-Check: PASSED
- All captured values recorded verbatim; no fabricated bench data (D-02).
- check_pre01.py + check_signature.py both PASS.
- No source modified under `firestarter/` or `firestarter_app/` (diagnostic phase; the Phase-98 fix is named, not applied).

---
*Phase: 97-pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program*
*Completed: 2026-06-30*
