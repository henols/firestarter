# Phase 53: Byte-Exact Bench Verification (hardware-gated) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-02
**Phase:** 53-byte-exact-bench-verification-hardware-gated
**Areas discussed:** Fault-injection harness (XACT-02), Byte-identity + write leg (XACT-01), uno328pb re-test recording (XACT-03)
**Not selected:** Milestone evidence artifact (SC4) — captured by default in CONTEXT.md D-11

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Fault-injection harness (XACT-02) | Direction, fault forms, pass bar | ✓ |
| Byte-identity pass bar + write leg (XACT-01) | N, baseline meaning, write proof, shield rev | ✓ |
| uno328pb re-test recording (XACT-03) | Runs, before/after, verdict wording | ✓ |
| Milestone evidence artifact (SC4) | Location, structure, contents | (deferred to defaults) |

---

## Fault-injection harness (XACT-02)

### Direction

| Option | Description | Selected |
|--------|-------------|----------|
| Host→fw command frame | Firmware decoder resync on the wire | |
| fw→host read frame | Host decoder resync (read-bug direction) | |
| Both directions | Both decoders demonstrated on bench path | ✓ |

**User's choice:** Both directions (D-01)

### Fault forms

| Option | Description | Selected |
|--------|-------------|----------|
| Corrupted CRC8 byte | CRC fails → reject + drain | ✓ (recommended) |
| Dropped 0x00 delimiter | Frames merge → re-anchor | ✓ (recommended) |
| Spurious/extra 0x00 | Stray delimiter mid-frame | (optional, planner discretion) |

**User's choice:** "recommend" — locked to corrupted-CRC8 + dropped-delimiter (mirrors Phase 50 D-02); spurious-0x00 left optional (D-02).

### Pass criterion

| Option | Description | Selected |
|--------|-------------|----------|
| Clean error + next transfer succeeds | (a) immediate error, (b) next frame byte-exact | ✓ |
| Next transfer succeeds only | Re-anchor only, no timing assertion | |
| Timed: assert error latency bound | Record measured time-to-error | (optional, D-03 discretion) |

**User's choice:** Clean immediate error + next transfer succeeds byte-exact (D-03)

---

## Byte-identity + write leg (XACT-01)

### N runs / consistency bar

| Option | Description | Selected |
|--------|-------------|----------|
| N=5, match GATE-1.8d | 5 consecutive, all SHA-256-identical | ✓ |
| N=10 for extra margin | Double depth | |
| Operator picks at bench | N>=5 floor | |

**User's choice:** N=5 (D-04)

### Baseline meaning

| Option | Description | Selected |
|--------|-------------|----------|
| Self-consistency + hash-match if chip available | Mandatory self-consistency; strong-form hash-match if original chip present | ✓ |
| Byte-match stored baseline hashes (strict) | Requires original chip; blocks otherwise | |
| N-run self-consistency only | No tie-back to stored binaries | |

**User's choice:** Self-consistency mandatory + baseline-hash-match if original chip on bench (D-05)

### Write leg proof

| Option | Description | Selected |
|--------|-------------|----------|
| Write→read-back→compare, N cycles | Independent host-side compare to source image | ✓ |
| Firmware built-in verify only | Couples to firmware verify internals | |
| Write once + read-back once | Single cycle, weaker confidence | |

**User's choice:** Write→read-back→compare, N=5 cycles (D-06)

### Shield rev

| Option | Description | Selected |
|--------|-------------|----------|
| Rev 2.0, confirm at bench | Reads clean (Phase 44); matches baseline lineage | ✓ |
| Rev 2.2 (newest) | Diverges from baseline lineage | |
| Operator decides per board | No rev pinned | |

**User's choice:** Rev 2.0, operator confirms silkscreen at bench (D-07)

---

## uno328pb re-test recording (XACT-03)

### Run count

| Option | Description | Selected |
|--------|-------------|----------|
| N=5 with timeout-retry logging | Match depth; log timeouts/retries honestly | ✓ |
| N=10 to characterize drift | Richer failure-shape sample | |
| Operator judgment, N>=5 floor | As many as needed | |

**User's choice:** N=5 with explicit timeout-retry logging (D-08)

### Before/after capture

| Option | Description | Selected |
|--------|-------------|----------|
| Cite documented 'before' + capture hardened 'after' | No old-fw re-flash | ✓ |
| Fresh A/B: flash old fw, then hardened | Two extra sideload cycles | |
| After-only, qualitative | Weakest contrast | |

**User's choice:** Cite documented before-shape + capture hardened after (D-09)

### Verdict wording

| Option | Description | Selected |
|--------|-------------|----------|
| Structured exoneration verdict block | Shape + change + explicit not-a-fix line | ✓ |
| Free-form operator note | No mandated structure | |
| You draft the exact wording | Claude templates it | |

**User's choice:** Structured exoneration verdict block per v1.9-COBS-DECISION §2.0 (D-10)

---

## Claude's Discretion

- Fault-injection harness implementation form (test wedge / debug flag / dev subcommand) + fw→host receive-path hook mechanism — must not touch production transport paths.
- Optional spurious-0x00 fault form (D-02) and measured error-latency number (D-03).
- Exact artifact filenames/structure under `.planning/v1.10/bench-verification/` (D-11).
- Write-leg source image + data-block content patterns (D-06).

## Deferred Ideas

- v1.9 read-bug RCA + per-shield fix (Bug A / Bug B) — deferred to v1.9 Phase 45+.
- A/B re-flash of pre-hardening firmware on uno328pb — rejected for Phase 53 (D-09).
- WR-01 frame-level decoder deadline — out of v1.10 scope; pending todo.
