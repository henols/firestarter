# Phase 50: Data-Path Framing Layer + Automatic Resync (dual-repo lockstep) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-01
**Phase:** 50-data-path-framing-layer-automatic-resync-dual-repo-lockstep
**Areas discussed:** Recovery behavior after resync, Resync test (level & fault form), Interim version/interop guard, `#` marker & MAIN-state demux

> Note: Phase 49 (`v1.10-FRAMING-DECISION.md`) froze the COBS frame contract, so the mechanism,
> delimiter, frame layout, CRC8, RAM strategy, and per-file change map were NOT re-litigated. The
> four areas below are the only genuinely-open implementation/behavior gray areas for Phase 50.

---

## Recovery behavior after resync (FRAME-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Resync + fail-fast | Transport resyncs to next delimiter, surfaces a clean error immediately (no 2 s hang); existing op-level ERROR fires; user re-runs. Smallest diff, delivers the goal. | ✓ |
| Resync + block retransmit | Host re-sends the failed block, operation continues transparently. More robust but adds a retransmit/ACK protocol — a new capability, larger diff. | |

**User's choice:** Resync + fail-fast (Recommended)
**Notes:** Block-level retransmit explicitly deferred as a separate future capability — not Phase 50.

---

## Resync test — level & fault form (Phase 50 SC2)

| Option | Description | Selected |
|--------|-------------|----------|
| Both repos, minimal | Host pytest (corrupted-CRC + flipped/missing delimiter) AND a firmware Unity decoder case; honors dual-repo lockstep, proves cascade gone both directions. Full byte-compat matrix deferred to Phase 52. | ✓ |
| Host pytest only | Prove resync at host decoder level only. Fastest, but firmware decoder (where 2 s timeout lives) unproven. | |
| Firmware Unity only | Prove resync in firmware COBS decoder. Closest to metal, but host side unproven and Phase 52 already owns that suite. | |

**User's choice:** Both repos, minimal (Recommended)
**Notes:** Phase 50 proves *recovery*; Phase 52 proves *byte-exactness* (round-trip matrix, pathological cases).

---

## Interim version/interop guard

| Option | Description | Selected |
|--------|-------------|----------|
| No interim guard | Accept the breaking change; document it; rely on lockstep upgrade; proper handshake guard lands in Phase 51 (SC3). Interim guard = throwaway since Phase 51 reworks command ingest. Beta-only. | ✓ |
| Add interim guard now | Lightweight version/magic check so a mismatched pair fails clearly instead of silent corruption. Safer in dev window/bench but redundant with Phase 51. | |

**User's choice:** No interim guard (Recommended)
**Notes:** Consistent with the v1.2 lockstep-upgrade precedent and "nothing stable until operator says so."

---

## `#` marker & MAIN-state demux

| Option | Description | Selected |
|--------|-------------|----------|
| Keep `#` marker, frame follows | `read_command_in_main` still dispatches on `#`; only post-`#` bytes change to `[COBS(payload+CRC8)][0x00]`. Smallest/safest diff. Corrupted-`#` re-anchor flagged for research. | ✓ |
| Absorb `#` into framing | Pure `0x00`-delimited data path, reworking marker dispatch. Cleaner resync boundary but larger/riskier state-machine change. | |
| You decide | Defer to planner/research as an implementation-approach call. | |

**User's choice:** Keep `#` marker, frame follows (Recommended)
**Notes:** Residual edge flagged in CONTEXT.md (D-04) — research must confirm a corrupted `#` byte itself re-anchors cleanly on the next `0x00`.

---

## Claude's Discretion

- Placement of the COBS decode helper (`serial_comm.py` vs `frame_parser.py`).
- Encoder/decoder function naming and the precise streaming-decoder buffer strategy (in-place vs incremental), within the no-second-buffer / Uno-RAM constraint.
- Fault-injection fixtures and assertion style for the SC2 tests.

## Deferred Ideas

- Block-level retransmit / ACK on the data path — its own phase if ever wanted.
- Command-channel framing + CRC8-before-parse + version/handshake guard → Phase 51.
- Full byte-compat round-trip / lockstep contract tests → Phase 52.
- Bench verification (Uno/Leonardo/uno328pb, operator-gated) → Phase 53.
