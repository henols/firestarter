---
title: 203-SESSION-COST — the added wall-clock of the guard read and the read-back
date: 2026-09-21
context: >
  Phase 203 (D-17) requires the added wall-clock this phase's guard-read and
  --verify read-back cost be recorded so Phase 206's SESS-02 ("measure the
  saving on a real run; if it does not pay for the structural change, revert
  and record that") inherits a real before-figure instead of inventing its
  own baseline. This phase is scoped bench-no -- no hardware measurement was
  taken here. Every figure below is a derivation over prior recorded
  measurements, cited to the artifact and section that measured it.
---

# 203-SESSION-COST — the added wall-clock, derived and cited

## 1. What is being counted

`EpromOperator._operation_context` disconnects in its `finally`, and every operation opens and
closes its own port (D-17, `.planning/phases/203-the-write-guard-moves-up-a-layer/203-CONTEXT.md`).
Before this phase, `firestarter write` on a UV-EPROM part was **one** port open: the write itself.
After this phase:

- A **guarded, plain `write`** (no `--verify`) on a UV-EPROM part (protocol `0x07`/`0x08`/`0x0B`/
  `0x06`/`0x10`, not erase-exempt) is **two** port opens: the guard's blank-check read, then the
  write. **One extra open.**
- A **guarded `write --verify`** is **three** port opens: the guard read, the write, and the
  `--verify` read-back. **Two extra opens.**

Each open resets an Uno-class board (`serial_comm.py:205`, `CONNECTION_STABILIZE_DELAY = 2.0`
seconds after opening the port, part of the structural floor cited in §2). An erase-exempt part
(protocol `0x05`/`0x0D`, or SRAM/FRAM) pays none of this: the guard is skipped entirely for those
families (`write_blank_guard.requires_blank_check`, proven in 203-01's
`test_write_on_erase_exempt_part_pays_no_guard_read` and siblings), so nothing below applies to
them.

## 2. The connect term, cited

The per-open medians below are `.planning/milestones/v1.36-phases/176-transport-instrumentation-connect-cost-measurement-partially/176-MEASUREMENT.md`
§4a/§4b, measured 2026-09-04 against `firestarter_app` HEAD `df2978e` (branch
`gsd/v1.36-dev-test-fidelity`), ten samples per board class, port pinned explicitly
(`restrict_to_port=True`) so port discovery cannot inflate the figure. The two board classes are
**never blended** — 176-MEASUREMENT.md is explicit that no single combined number exists or
should be quoted, and this document follows that rule.

| Board class | `firmware_max_chunk` | Samples | Min | Median | Max | Structural floor | Remainder |
|---|---|---|---|---|---|---|---|
| Uno-class (`/dev/ttyACM1`) | 512 B | 10 | 2.517s | **2.518s** | 2.519s | 2.500s | 0.018s |
| Leonardo-class (`/dev/ttyACM0`) | 1024 B | 10 | 2.606s | **2.607s** | 2.676s | 2.500s | 0.107s |

Quoted verbatim, not rounded. The structural floor (2.500s = `CONNECTION_STABILIZE_DELAY` 2.0s +
`_CONSUME_REMAINING_INPUT_WINDOW_S` 0.5s, `firestarter_app/firestarter/eprom_operations.py:100-102`
and `serial_comm.py:85`) is board-independent; the small per-class remainder (0.018s Uno, 0.107s
Leonardo) is the only part of the connect cost that varies by board, and 176-MEASUREMENT.md §6
records that neither hypothesis for *why* the two remainders differ was confirmed — only the
aggregate wall-clock was observed.

## 3. The derived totals

**This section is this document's own arithmetic, not a measurement.** Applying §1's port-open
counts to §2's medians, per board class:

| Guarded operation | Extra opens | Uno-class added cost | Leonardo-class added cost |
|---|---|---|---|
| Plain `write` (guarded, no `--verify`) | +1 | **2.518s** | **2.607s** |
| `write --verify` (guarded) | +2 | **5.036s** | **5.214s** |

These are sums of §2's cited medians (`2.518s x 2 = 5.036s`; `2.607s x 2 = 5.214s`), not a second
measured quantity. Two caveats on the arithmetic itself:

- It assumes each extra open costs exactly one more connect-cost median — i.e. no warm-port
  discount and no additional cost from the guard's or the read-back's own read traffic beyond the
  connect. The guard's read and the `--verify` read-back both move real bytes over the wire in
  addition to the connect; §4 and §5 below account for that traffic, and it is **additive** to
  the connect totals in this table, not included in them.
- It is a structural estimate over a real, cited connect-cost figure, not a bench run of the
  actual guarded `write --verify` path end to end. §6 states this in full.

## 4. The abort term, cited

On a **guard refusal** (a non-blank byte found), the guard's read stops in flight rather than
draining the whole region — the same mid-stream-stop mechanism `.planning/phases/202-one-comparison-engine-on-the-host/202-READ-ABORT-ANSWER.md`
("The mechanism", "The cost") documents and proves for `verify_eprom`'s default path. That
document's own words: "Up to one second of firmware timeout per abort — the ack-wait's own
deadline, unavoidable because the deliberate stop and this cost are the same mechanism." The
bound is the firmware's `op_wait_for_ack` deadline (1000 ms, polled every 10 ms,
`firestarter_fw/src/operation_utils.cpp:94-108`), not an average or a typical case — every
deliberate stop costs at most this much, once, and the read itself may have consumed far less
than the full region's transfer time before the abort fired. This term applies **only** to a
refused write (the guard finds non-blank content and stops); it does not apply to the §2/§3
connect terms, which are paid on every guarded operation regardless of outcome.

## 5. The read term, cited and hedged

The only in-repo throughput figures for a full-region read/verify/write on a UV-EPROM part come
from `.planning/notes/dev-test-sequence-cost-model.md`, and that note states its own limits in its
own words, quoted here rather than summarized: "Every rate here comes from **one** operator log: a
single `firestarter dev test sst27sf512 --fast` run on a **Leonardo** (1024 B buffer) against a
**65536 B** part, pasted into the explore session on 2026-08-30. This is a model built on one
sample, not a benchmark." Its measured primitives table, for the same 65536 B part:

| Primitive | Time | Effective rate | Wire direction |
|---|---|---|---|
| read | 7.51s | 8.7 KB/s | device→host, plus a host file write |
| verify | 5.71s | 11.5 KB/s | host→device, firmware compares |
| blank-check | 4.86s | 13.5 KB/s | no payload, device-side scan |

The guard's read and `write --verify`'s read-back both pull the *written region* back from the
device and compare on the host — closest in shape to the `read` row above (device→host, though
without necessarily writing a file), not the `verify` row (which is a firmware-side compare this
phase specifically moves off the firmware). Applying the note's own correction: read rate is
protocol-dependent, not just size-dependent — the note's own second data point (`AM27C020`,
protocol `0x08`) read 24% slower than the `0x07` figure this table is built on. **No absolute
second-count for the guard's read or `--verify`'s read-back is derived here from this table for
that reason** — the region sizes a real `write` touches vary per invocation and per protocol in a
way the connect term (§2, fixed per port-open) does not, and this note's own single-sample,
one-protocol scope does not support extrapolating a specific number. It is cited to establish
*shape* (a full-region UV read is the single most expensive non-write primitive this project has
measured) and its caveat, not to produce a per-invocation total.

## 6. The explicit non-measurement statement

**Phase 203 took no new hardware measurement.** The phase is scoped bench-no (`203-CONTEXT.md`:
"This phase is app-only and bench-no"), and the in-repo connect-cost harness
(`EpromOperator.measure_connect_cost`, `eprom_operations.py:1877-1907`) needs a real board to
produce a number — it resolves a port and **returns early without one** (its own docstring:
"Refuses rather than guesses: with no port resolved, this logs and returns False without opening
anything"). No board was attached to run it against during this phase's execution. Every figure in
§2, §4 and §5 above is quoted from a prior artifact that DID take a real measurement; §3's totals
are this document's own arithmetic over those cited figures, not a new measurement. Recording §3's
totals as "203 measured 5.036s" or "203 measured 5.214s" would hand Phase 206's SESS-02 a
fabricated baseline it has no way to detect as fabricated — this sentence is the whole reason D-17
asked for this document to exist.

## 7. What Phase 206 should do with it

Phase 206's SESS-01 owns collapsing the three port opens (guard read, write, `--verify` read-back)
into one leased serial session. Its SESS-02 must **measure the saving on a real run** — a genuine
bench figure, not a derivation — and, if the saving does not pay for the structural cost of the
lease, **revert the change and record that**, per D-17's own framing. This document is SESS-02's
before-figure. Its error bar is **not** the connect term in §2, which is a real ten-sample
measurement with a sub-0.1s spread on each board class; the error bar is the read term in §5,
which is a single sample on one protocol and is explicitly not extrapolated into a number here.
Any comparison SESS-02 makes against §3's derived totals should treat the connect component as
trustworthy and the guard-read/read-back traffic component as unknown until measured.

## 8. The alternative that remains open

A bench run — attaching a real board and running `EpromOperator.measure_connect_cost` alongside a
timed guarded `write --verify` — would replace this derivation with a genuine measurement. It was
not taken here because the phase is scoped bench-no, not because it is unavailable: the harness
already exists (`tests/test_connect_cost_harness.py`, `eprom_operations.py:1877-1907`) and needs
only a board. The operator can commission that run at any time. If one is taken, **this document
should be superseded by a new one, not amended in place** — a derivation and a measurement are
different kinds of evidence, and overwriting the derivation's numbers with measured ones in the
same file would erase the distinction §6 exists to preserve.

## Provenance table

| Term | Value | Measured or derived | Source (artifact, section) |
|---|---|---|---|
| Uno-class connect median | 2.518s (min 2.517s, max 2.519s, N=10) | measured | `176-MEASUREMENT.md` §4a |
| Leonardo-class connect median | 2.607s (min 2.606s, max 2.676s, N=10) | measured | `176-MEASUREMENT.md` §4b |
| Structural connect floor | 2.500s | measured (derived from constants, confirmed against both classes' logs) | `176-MEASUREMENT.md` §4a/§4b; `firestarter_app/firestarter/eprom_operations.py:100-102`, `serial_comm.py:85` |
| Extra opens, guarded plain `write` | +1 | derived (§1, §3, this document) | this document §1, §3 |
| Extra opens, guarded `write --verify` | +2 | derived (§1, §3, this document) | this document §1, §3 |
| Added cost, guarded plain `write` (Uno / Leonardo) | 2.518s / 2.607s | derived | this document §3 |
| Added cost, guarded `write --verify` (Uno / Leonardo) | 5.036s / 5.214s | derived | this document §3 |
| Per-abort bound (guard refusal, mid-read stop) | up to 1.000s | measured (firmware constant, proven mechanism) | `202-READ-ABORT-ANSWER.md` "The mechanism", "The cost" |
| Full-region read rate, 65536 B, protocol 0x07, Leonardo | 7.51s / 8.7 KB/s | measured, single-sample, one protocol -- hedged | `dev-test-sequence-cost-model.md` "Measured primitives (65536 B part)" |
| No new hardware measurement taken this phase | -- (explicit statement) | n/a | this document §6; `203-CONTEXT.md` (bench-no scope) |

---
*Phase: 203-the-write-guard-moves-up-a-layer*
*Written: 2026-09-21*
