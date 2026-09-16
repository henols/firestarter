# v1.10 Byte-Exact Bench Verification — Milestone Evidence Artifact (Phase 53, SC4)

> **Hand-off to the resumed v1.9 Phase 45+ read-bug RCA.** This artifact aggregates the
> operator-witnessed bench evidence proving the hardened COBS serial transport is a **settled,
> byte-exact variable** — so the v1.9 RCA can rule serial framing OUT as a confounder.
>
> Assembled by Plan 53-06 (SC4). Composes 53-03 (clean-board read+write), 53-04 (fault-injection
> resync + latency), 53-05 (uno328pb exoneration), and 53-07 (post-54/55 corpus extension). No new
> transport behavior or harness code — pure aggregation.

## Operator attestation

- **Date:** 2026-06-05 (single operator-witnessed bench session).
- **Boards & confirmed silkscreen shield revs (D-07):**
  - **Leonardo** — Rev 2.0 (operator-confirmed). Post-55 hardened firmware (`OK: FW: 3.0.0b6:leonardo`, pure 2-field) + the 53-04 drop-delimiter optimization.
  - **Uno** — Rev 2.0 (operator-confirmed). Post-55 hardened firmware (`OK: FW: 3.0.0b6:uno`).
  - **uno328pb** — Rev 2.2 (typical per bench history; operator "go"). Post-55 firmware sideloaded this session (`OK: FW: 3.0.0b6:uno328pb`, pure 2-field — D-09 hardened-only).
- **Chip:** W27C512 throughout. Chips were re-seated/moved across boards during the session (the read SHAs differ per board because different physical chips/contents were in each socket); every leg records its own source SHA. **Net non-destructive** — write legs used each chip's own read-back content as the source.
- **Bench caveats (honest record):** the Leonardo's VPP read 13.1 V (> 12.0 V fatal guard) — reads/writes were force-bypassed (`-f`) per operator authorization (reads route no VPP; forced writes still came out byte-exact). The uno328pb's VPP read 12.7 V (non-fatal warning). The Leonardo intermittently destabilized under forced-VPP writes (needed a reset + retries). Ports re-enumerated repeatedly (ACM↔USB); identity was re-verified per leg.

## Form achieved: SELF-CONSISTENCY (D-05), not strong-form baseline hash-match

No chip on the bench this session was the original GATE-1.8d Rev 2.0 baseline (`19710f6e…`). Per D-05,
**self-consistency** (all N=5 reads byte-identical to each other) is the achieved and recorded form for
XACT-01. The strong-form baseline hash-match was **not** attempted (baseline chip not present).

## XACT-01 — clean-board byte-identity (53-03 + 53-07)

| board | buffer | leg | N | verdict | SHA-256 |
|-------|--------|-----|---|---------|---------|
| Uno (53-03) | 512 | read | 5 | **0** (self-consistent) | `8144ae57…` (5/5 identical) |
| Uno (53-03) | 512 | write→read-back | 5 | **0** | 5/5 readback == source `8144ae57…` |
| Leonardo (53-03) | 1024 | read | 5 | **0** (self-consistent) | `25bae52d…` (5/5 identical) |
| Leonardo (53-03) | 1024 | write→read-back | 5 | **0** | 5/5 readback == source `25bae52d…` |
| Leonardo (53-07) | 1024 | read | 5 | **0** (self-consistent) | `de2f2560…` (5/5 identical) |
| Leonardo (53-07) | 1024 | write→read-back | 5 | **0** | 5/5 readback == source `de2f2560…` |

**53-07 post-54/55 contract extension:** raw identity `OK: FW: 3.0.0b6:leonardo` (pure 2-field, no
`:buf:maxchunk` suffix — CAP-01 SC1); **ack-sourced** chunking 1024×64 both directions (host default is
512 → 1024 proves the MSG_OK_READY ack drives sizing); even-block, no odd remainder (65536 % 1024 == 0);
safe-512 default recorded software-covered (Phase 55 `TestCapSafeDefault` 3/3). Evidence:
`even-block-ack/` (fw-identity-raw.txt, chunk-evidence.txt, read-leg/, write-leg/, safe-512-note.txt).
Uno 512×128 second witness deferred (no chip at the time).

→ **XACT-01: byte-exact on clean boards (both buffer classes), self-consistency form. PROVEN.**

## XACT-02 — fault-injection resync (53-04)

Detect + recover proven both directions, both fault forms (corrupt-crc8, drop-delimiter):
- **fw→host (incoming):** the host decoder catches the mutated frame (`CRC mismatch for ID 0x10`) — no silent corruption — and the next transfer recovers byte-exact.
- **host→fw (outgoing):** the firmware fast-NAKs a corrupt command frame; recovery byte-exact on the same connection.
- **Per-frame NAK latency** (established single-port connection, `dev fault-inject --mode latency`, post-optimization firmware):
  - corrupt-crc8 (complete frame): **0.001 s** — SUB-SECOND fast-fail.
  - drop-delimiter (truncated frame): **1.001 s** — single bounded inter-byte deadline (firmware optimized from ~2 s; `_drain_to_delimiter` redundant silence-wait removed, `firestarter 0266ee2`).
- No path exceeds ~1 s; the Phase-50 2 s timeout cascade stays eliminated. Timeout → verdict 2 (never collapsed to verdict 1).

Evidence: `fault-injection/` (fault-inject-{outgoing,incoming}-log.txt, latency-*/, FINDINGS-2026-06-05.md).

→ **XACT-02: bounded resync + sub-second/bounded clean error. PROVEN.**

## XACT-03 — uno328pb transport-exoneration (53-05)

uno328pb re-tested on the hardened firmware (5 retry attempts; D-08 timeouts logged + retried, never
aborted; timeout → verdict 2, never collapsed to verdict 1):

| metric | v1.6 BEFORE (cited) | hardened AFTER |
|--------|---------------------|----------------|
| 0xff | ~99.4% (floating bus) | ~8.8% (real data) * |
| positions unstable (N=5) | 100% | 36% |
| pairwise divergence | 0.47% | mean 15% (max 34%) |
| timeouts | 4× N=5 | persist (intermittent mid-read; verdict 2) |
| full-read consistency | — | 5 reads → 5 distinct SHAs (verdict 1) |

\* 0xff drop partly confounded by chip state (before = floating/blank; after = seated data chip).

**Shape-changed = PARTIAL:** floating-bus mode resolved; read instability persists.

> **transport-exoneration per v1.9-COBS-DECISION §2.0 — NOT a per-shield hardware fix; the actual RCA stays deferred to v1.9 Phase 45+.**

Evidence: `uno328pb/` (timeout-retry-log.txt, exoneration-verdict.txt, read-runs/, attempt-1..5/).

## Milestone claim (the settled variable)

On the hardened COBS transport, the serial path is **byte-exact and bounded** on clean boards
(XACT-01: N=5 read self-consistency + write→read-back==source, both buffer classes) and **fails safe
with bounded resync** under fault injection (XACT-02: detect + recover, sub-second/≤1 s clean error, no
2 s cascade, no silent corruption). The uno328pb residual read instability is **not** transport — it
persists on the hardened transport (XACT-03 exoneration), so it is a hardware/shield-level read-path
fault.

**→ The v1.9 read-bug RCA (Phase 45+) may treat the serial transport as a SETTLED, byte-exact variable
and rule serial framing OUT as a confounder.** The uno328pb instability is handed to that RCA as a
hardware-level concern, not a transport one.

## Artifact index

```
.planning/milestones/v1.10-artifacts/bench-verification/
├── SUMMARY.md                      ← this milestone evidence artifact (SC4)
├── clean-board-uno/                ← XACT-01 Uno 512 (53-03): read-leg/ + write-leg/
├── clean-board-leonardo/           ← XACT-01 Leonardo 1024 (53-03): read-leg/ + write-leg/
├── even-block-ack/                 ← XACT-01 post-54/55 corpus (53-07): identity + ack-sourced chunks + read/write
├── fault-injection/                ← XACT-02 (53-04): outgoing/incoming logs + latency + FINDINGS
└── uno328pb/                       ← XACT-03 (53-05): timeout-retry-log + exoneration-verdict + per-run binaries
```
