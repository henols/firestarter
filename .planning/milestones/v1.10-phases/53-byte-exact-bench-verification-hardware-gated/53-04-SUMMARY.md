---
phase: 53-byte-exact-bench-verification-hardware-gated
plan: "04"
subsystem: .planning/v1.10/bench-verification/fault-injection
tags: [bench, operator-witnessed, xact-02, cobs, crc8, resync, fault-injection, fast-nak]
dependency_graph:
  requires:
    - phase: "53-02"
      provides: "dev fault-inject harness (outgoing hook + FaultInjectingSerialCommunicator)"
  provides:
    - "Operator-witnessed XACT-02 evidence: COBS/CRC8 resync detect+recover (both directions, both fault forms)"
    - "Per-frame firmware NAK latency proof: corrupt-crc8 ~1ms sub-second; drop-delimiter ~1s single bounded deadline"
    - "dev fault-inject --mode latency (established single-port per-frame measurement)"
    - "Firmware optimization: drop-delimiter error ~2s -> ~1s (no redundant drain silence-wait)"
  affects:
    - ".planning/v1.10/bench-verification/fault-injection/"
    - "firestarter_app/firestarter/eprom_operations.py, serial_comm.py, cli_handlers.py"
    - "firestarter/src/boards/rurp_serial_utils.cpp"
tech_stack:
  added: []
  patterns:
    - "Established-connection per-frame timing (avoids find_and_connect multi-port retry inflation)"
    - "_drain_to_delimiter(wait_on_silence): skip the redundant 2nd silence-wait after the inter-byte deadline"
key_files:
  created:
    - ".planning/v1.10/bench-verification/fault-injection/fault-inject-outgoing-log.txt"
    - ".planning/v1.10/bench-verification/fault-injection/fault-inject-incoming-log.txt"
    - ".planning/v1.10/bench-verification/fault-injection/FINDINGS-2026-06-05.md"
    - ".planning/v1.10/bench-verification/fault-injection/{outgoing,incoming}-{corrupt-crc8,drop-delimiter}/"
    - ".planning/v1.10/bench-verification/fault-injection/latency-{corrupt-crc8,drop-delimiter}/"
    - ".planning/v1.10/bench-verification/fault-injection/latency-opt-{corrupt-crc8,drop-delimiter}-leonardo/"
  modified: []
key-decisions:
  - "Harness false-negative (53-02): the outgoing hook was set AFTER a read's only send_json_command (the setup), and a READ's MAIN phase sends only plaintext acks -> it never fired. Fixed by threading the hook into find_and_connect/_probe_port so the setup command frame is corrupted at connection time (firestarter_app 630fafd)."
  - "Firmware fast-NAK RCA: reading rurp_communication_read_data + firestarter.cpp CMD_IDLE shows the fast-NAK ALREADY EXISTS (corrupt-crc8 -> immediate -4 -> MSG_ERR_EMPTY_INPUT). The earlier 6-23s 'timeout' was a HARNESS artifact (corrupting the connection-setup frame triggers find_and_connect multi-port retry), NOT firmware slowness."
  - "Harness refinement (firestarter_app 8480ff3): dev fault-inject --mode latency measures the per-frame NAK on a single pinned, established connection -> corrupt-crc8 = 3ms (Uno) / 1ms (Leonardo) sub-second."
  - "Firmware optimization (firestarter 0266ee2): a dropped-delimiter frame waited TWICE (inter-byte deadline + drain host-silence) = ~2s. _drain_to_delimiter(wait_on_silence=false) at the deadline removes the redundant 2nd wait -> ~1s (single inter-byte deadline, the irreducible floor)."
requirements-completed: [XACT-02]
duration: ~2 hours (operator-witnessed, cross-repo)
completed: "2026-06-05"
tasks_completed: 2
files_modified: 0
---

# Phase 53 Plan 04: XACT-02 Fault-Injection Resync — Operator-Witnessed (+ harness fix + firmware optimization)

**COBS/CRC8 resync proven on real hardware (both directions, both fault forms): detect + recover with NO silent corruption. Per-frame firmware NAK is sub-second for complete corrupt frames (~1ms) and a single bounded ~1s inter-byte deadline for truncated frames (optimized down from ~2s). No path exceeds ~1s; the Phase-50 2s cascade stays gone.**

## Performance

- **Duration:** ~2 h (operator-witnessed; spanned a harness fix, RCA, harness refinement, and a firmware optimization)
- **Completed:** 2026-06-05
- **Boards:** Uno (ACM1, W27C512 0xda08) for the 4-combo + latency runs; Leonardo (ACM2) for the optimized-firmware re-bench

## Accomplishments

- **Resync detect + recover proven** — 4 combos (outgoing/incoming × corrupt-crc8/drop-delimiter): every clean follow-on transfer byte-exact; incoming legs log explicit `CRC mismatch for ID 0x10` detection (no silent acceptance).
- **Harness false-negative fixed** (`firestarter_app 630fafd`) — the outgoing fault now genuinely fires (was set after the read's only command frame → never fired).
- **Firmware fast-NAK RCA** — the fast-NAK already exists and is correct; the apparent 6–23 s "timeout" was a multi-port connect-retry measurement artifact (corrupting the connection-setup frame), not firmware slowness.
- **Harness refinement** (`firestarter_app 8480ff3`) — `dev fault-inject --mode latency` measures the true per-frame NAK on an established single-port connection.
- **Firmware optimization** (`firestarter 0266ee2`) — `_drain_to_delimiter(wait_on_silence)` removes the redundant second silence-wait; drop-delimiter error **2.005 s → 1.001 s**. Built both boards, native 43/43 pass, flashed + re-benched on the Leonardo.

## Final per-frame latency (validated on optimized firmware)

| fault form | NAK latency | verdict | recovery |
|------------|-------------|---------|----------|
| corrupt-crc8 (complete frame, bad CRC) | **0.001 s** | sub-second fast-fail | byte-exact, same connection |
| drop-delimiter (truncated frame) | **1.001 s** | single bounded inter-byte deadline (floor) | byte-exact, same connection |

## XACT-02 truths

- "corrupted host→fw frame surfaces a clean error immediately (sub-second, NOT a 2 s cascade)" — **MET**: complete corrupt frame ~1 ms; truncated frame ~1 s (one bounded inter-byte deadline — the minimum to detect a missing terminator). No 2 s cascade.
- "next transfer on the SAME open connection byte-exact" — **MET** (latency mode: recovery clean on the same connection, both forms).
- "mutated fw→host frame triggers host resync, next frame clean" — **MET** (incoming legs: CRC mismatch detected + recovered).
- "both fault forms exercised" — **MET** (corrupt-crc8 + drop-delimiter).

## Cross-repo commits

- `firestarter_app` `630fafd` — outgoing fault-injection false-negative fix + error-latency logging.
- `firestarter_app` `8480ff3` — `dev fault-inject --mode latency` (established single-port per-frame measurement) + tests.
- `firestarter` `0266ee2` — `_drain_to_delimiter(wait_on_silence)` drop-delimiter optimization (~2 s → ~1 s).
- Meta evidence: `3272f64` (4-combo), `db24ffe` (RCA), `feb2e82` (clean latency), `7a4b3d9` (optimized re-bench); debug session `fault-inject-harness-outgoing` resolved (`d752384`).

## Deviations from Plan

The plan scripted only the `dev fault-inject` cycle run. Three justified extensions were required to make the XACT-02 latency truth honestly demonstrable rather than a false negative:
1. **Harness false-negative fix** — the 53-02 outgoing hook never fired; without the fix the "corrupted transfer" was a false negative, not evidence.
2. **`--mode latency` refinement** — cycle-mode's outgoing latency was inflated by `find_and_connect`'s multi-port retry; a single-port established-connection measurement was needed for the true per-frame NAK.
3. **Firmware optimization** — operator-elected (after the RCA) to bring the bounded drop-delimiter error from ~2 s to ~1 s by removing the redundant drain silence-wait.

All extensions are committed with tests (host: +7 tests; firmware: native 43/43); no fabricated bench data. Production paths byte-identical when fault hooks are absent (T-53-03).

## Quality gates

Host: `ruff check` + `ruff format --check` clean; full suite 469 passed (1 hardware-only test deselected); coverage 71.89 % (≥70). Firmware: both boards build; native 43/43 pass. mypy: neutral (pre-existing project watermark drift unrelated to this work — flagged separately).

## Self-Check: PASSED

- [x] `fault-inject-outgoing-log.txt` + `fault-inject-incoming-log.txt` present (both fault forms)
- [x] Resync detect + recover proven both directions, both fault forms (recovery byte-exact)
- [x] Per-frame NAK: corrupt-crc8 sub-second; drop-delimiter single bounded ~1 s deadline (no 2 s cascade)
- [x] Firmware optimization built (both boards), native 43/43, flashed + re-benched on Leonardo
- [x] No fabricated data; production paths byte-identical without fault hooks
- [x] FINDINGS-2026-06-05.md documents the full arc (4-combo → RCA → latency → optimization)
