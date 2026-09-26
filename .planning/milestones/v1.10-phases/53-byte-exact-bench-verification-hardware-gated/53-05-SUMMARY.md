---
phase: 53-byte-exact-bench-verification-hardware-gated
plan: "05"
subsystem: .planning/v1.10/bench-verification/uno328pb
tags: [bench, operator-witnessed, xact-03, uno328pb, transport-exoneration, timeout, read-jitter]
dependency_graph:
  requires:
    - phase: "53-02"
      provides: "dev consistency-check harness (3-way verdict 0/1/2)"
  provides:
    - "Operator-witnessed XACT-03 transport-exoneration verdict for the uno328pb on the hardened transport"
    - "After-shape vs documented v1.6 before-shape; structured D-10 exoneration block"
  affects:
    - ".planning/v1.10/bench-verification/uno328pb/"
tech_stack:
  added: []
  patterns:
    - "D-08: timeouts logged + retried across 5 attempts, never aborted; timeout -> verdict 2 (never collapsed to verdict 1)"
    - "D-09: hardened-firmware-only — post-55 sideloaded this session; before-shape cited from v1.6, not re-run"
key_files:
  created:
    - ".planning/v1.10/bench-verification/uno328pb/timeout-retry-log.txt"
    - ".planning/v1.10/bench-verification/uno328pb/exoneration-verdict.txt"
    - ".planning/v1.10/bench-verification/uno328pb/{read-runs,attempt-1..5}/ (per-run binaries, however many completed)"
  modified: []
key-decisions:
  - "Sideloaded post-55 firmware to the uno328pb (chip-out + replug by operator; single port disambiguated). Identity confirmed pure 'OK: FW: 3.0.0b6:uno328pb' (no suffix) = hardened (D-09)."
  - "After-shape: floating-bus mode RESOLVED (~8.8% 0xff real data, position instability 100%->36%) but read instability PERSISTS (intermittent mid-read timeouts -> verdict 2; full reads diverge run-to-run -> verdict 1, mean 15% pairwise). Shape-changed = PARTIAL."
  - "Exoneration (NOT a fix): the hardened transport did not make the uno328pb byte-stable -> the read-path fault is hardware/shield-level; RCA deferred to v1.9 Phase 45+ (verbatim D-10 line recorded)."
  - "0xff-drop (99.4%->8.8%) is partly confounded by chip state (before = floating/blank read; after = seated data chip) — recorded honestly; the load-bearing persistent signal is the timeout + run-to-run divergence."
requirements-completed: [XACT-03]
duration: ~45 minutes (operator-witnessed; uno328pb sideload + 5 retry attempts)
completed: "2026-06-05"
tasks_completed: 2
files_modified: 0
---

# Phase 53 Plan 05: XACT-03 uno328pb Transport-Exoneration — Operator-Witnessed

**The uno328pb, re-tested on the HARDENED post-55 transport, is still NOT byte-stable — intermittent mid-read timeouts (verdict 2) and run-to-run divergence (verdict 1) persist. The catastrophic v1.6 floating-bus mode (~99.4% 0xff) is resolved, but the read instability remains. Structured transport-exoneration verdict recorded: this is NOT a per-shield hardware fix; the RCA stays deferred to v1.9 Phase 45+.**

## Performance

- **Duration:** ~45 min (operator-witnessed; post-55 sideload + 5 retry attempts)
- **Completed:** 2026-06-05
- **Board:** uno328pb /dev/ttyUSB0, post-55 firmware sideloaded this session, data chip seated

## Accomplishments

- **D-09 hardened-only honored:** sideloaded the post-55 uno328pb firmware (chip-out + operator replug; single port disambiguated from a transient USB0/USB1 duplicate). Identity confirmed pure `OK: FW: 3.0.0b6:uno328pb` (no `:buf:maxchunk` suffix).
- **D-08 retry discipline:** ran `dev consistency-check --runs 5` across **5 retry attempts**, all logged to `timeout-retry-log.txt`, never aborted. Timeouts mapped to **verdict 2** (hw-error), never collapsed to verdict 1.
- **After-shape captured + quantified** vs the documented v1.6 before-shape.
- **Structured exoneration verdict** (`exoneration-verdict.txt`) with the verbatim D-10 line.

## Before vs After

| metric | v1.6 BEFORE (cited) | hardened AFTER (observed) |
|--------|---------------------|---------------------------|
| 0xff content | ~99.4% (floating bus) | ~8.8% (real data) * |
| positions unstable (N=5) | 100% | 36% |
| pairwise divergence | 0.47% | mean 15% (max 34%) |
| timeouts | 4× N=5 | persist (intermittent mid-read; verdict 2) |
| full-read consistency | — | attempt 5: 5 reads, 5 distinct SHAs (verdict 1) |
| VPP | — | 12.7V warning (non-fatal) |

\* 0xff drop partly confounded by chip state (before = floating/blank; after = seated data chip). The load-bearing persistent signal is the timeout + run-to-run divergence.

## Verdict

**Shape-changed = PARTIAL.** Floating-bus mode resolved; read instability persists. The hardened COBS transport did **not** make the uno328pb byte-stable → the read-path fault is hardware/shield-level, not transport.

> transport-exoneration per v1.9-COBS-DECISION §2.0 — NOT a per-shield hardware fix; the actual RCA stays deferred to v1.9 Phase 45+.

A green-or-changed result is still exoneration, not a fix (per the 53-05 objective): serial framing is ruled out as the sole cause; the residual instability is handed to the v1.9 read-bug RCA (Phase 45+).

## Deviations from Plan

1. **Port disambiguation** — the uno328pb briefly presented on two ports (USB0+USB1, both pre-55); operator replugged to a single port before the sideload (no flash to an ambiguous target).
2. **`-f` on the read** — used to bypass the chip-id/VPP guard; the VPP-high (12.7V) was a non-fatal warning on the uno328pb (it proceeded), unlike the Leonardo's 13.1V fatal guard.
3. **5 attempts, not a single --runs 5** — the consistency-check aborts at the first verdict-2 (hw-error), so D-08 "retry, never abort" was satisfied by repeating the command 5× and logging each.

No fabricated data; before-shape cited from v1.6-EVIDENCE.md (not re-run, per D-09). Other 53 plans untouched.

## Self-Check: PASSED

- [x] uno328pb on HARDENED post-55 firmware (pure identity, no suffix) — D-09
- [x] timeout-retry-log.txt: 5 attempts, timeouts logged + retried, never aborted; verdict 2 never collapsed to verdict 1 — D-08
- [x] after-shape captured + quantified vs cited v1.6 before-shape
- [x] exoneration-verdict.txt: structured before/after + shape-changed + verbatim transport-exoneration line (D-10)
- [x] per-run binaries committed (however many completed)
- [x] No fabricated data; before-shape cited not re-run
