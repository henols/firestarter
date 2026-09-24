---
title: 205-SESSION-COST — the measured added wall-clock of erase -b's second port open, and the labelled derivation over Phase 203's cited medians
date: 2026-09-22
context: >
  Phase 205 D-01 requires `erase -b`'s added wall-clock be handed to Phase 206's SESS-01 ("collapse
  the three (now four, counting erase -b) port opens into one leased serial session"). Unlike Phase
  203's own SESSION-COST document (scoped bench-no, a pure derivation), this phase's bench plan (07)
  had a real board in the loop for three other legs, so the added cost is MEASURED here, with the
  derivation over Phase 203's cited per-open medians recorded alongside it, labelled as a
  derivation, per Fork C's decision in 205-07-PLAN.md.
---

# 205-SESSION-COST — SESS-01's before-figure: measured, with a derivation beside it

## 1. What is being counted

Before this phase, `firestarter erase -b` on the UV-EPROM family (protocol `0x07`, the class the
bench rig's W27C512 rides) ran the post-erase blank check **inside the erase's own port session**, as
the firmware's `firestarter_operation_end = mem_util_blank_check` assignment (`eprom.cpp:52-54`,
FWBLANK-02). **One port open, whole operation.**

D-01 re-implements that check host-side, through Phase 202's `check_eprom_blank` — the same engine
`firestarter blank` uses. `erase -b` now opens the port **twice**: once for the erase itself, and a
second time (after the first port closes, per `EpromOperator._operation_context`'s `finally`
disconnect) for the host-side blank check. **This document counts the wall-clock erase -b adds over
plain `erase`, on the same part, the same board, and the same rig, measured in the same bench session
`205-BENCH-MATRIX.md` records.**

Plain `erase` (no `-b`) is unaffected — still one port open, still exits `0`/`1` unchanged.

## 2. The measured added wall-clock (this document's own bench figure)

Measured 2026-09-22, `205-BENCH-MATRIX.md`'s bench rig: Arduino Leonardo (ATmega32U4, `2341:8036`,
`/dev/ttyACM0`), post-205 firmware (`6e11d057b59977dd870c1ddcc588dd2f6f3ea1db`), post-205 host
(`firestarter_app` editable install, `c7c1d9a1c8207e77cf539ca0c68b6a01d317e888`). The seated part is a
W27C512 riding the UV handler — **PROXY**, the same coverage limit `205-BENCH-MATRIX.md` states
throughout; the electrical-erase timing measured here would differ for a true UV part, but the
**port-open cost** this document isolates is a structural property of `_operation_context`, not of
the part's own erase electrical behaviour, so it applies unchanged regardless of which family occupies
the second port open.

Three runs each, wall-clock timed with `time` around the whole `firestarter erase ...` subprocess,
alternating nothing — all plain-`erase` runs first, then all `erase -b` runs, immediately after,
same part, same board, no reflash or reseat between them:

| Run | Plain `erase` (no `-b`) | `erase -b` |
|---|---|---|
| 1 | 4.138s | 14.753s |
| 2 | 3.946s | 14.543s |
| 3 | 3.929s | 14.578s |
| **Median** | **3.946s** | **14.578s** |
| Min | 3.929s | 14.543s |
| Max | 4.138s | 14.753s |

**MEASURED added wall-clock, Leonardo-class board, N=3 runs each: 14.578s − 3.946s = 10.632s.**

All three `erase -b` runs exited 0 with the same verdict: erased, then a whole-device host-side check
reporting `blank/contact, 0 bad of 65536 compared of 65536 (0x000000-0x00FFFF)` — `erase -b` running
end to end, exit 0, on real silicon, three times.

## 3. Why the measured figure is larger than a bare connect-cost derivation — the read term is real, not omitted

The measured added cost (10.632s) is markedly larger than the derived connect-term-only figure in §4
(2.607s). This is not a discrepancy to explain away — it is exactly the caveat 203-SESSION-COST.md §3
already stated in words ("the guard's ... read traffic ... is additive to the connect totals ... not
included in them") and this document's own bench run is the first place that additive term has been
measured rather than hedged as unknown.

`erase -b`'s second port open does not merely open and close — it drives a **whole-device** blank
check (D-01's stated scope: "whole-device, not region-scoped ... erase on this family is
device-global"). For this 65536 B (64 KiB) part, that scan itself measures **7.40s** of the second
port open's total (the CLI's own reported time, matching `205-BENCH-MATRIX.md`'s whole-device `read`
legs, which report the identical `7.40s` figure for the same 65536 B transfer over the same rig — the
blank check and a plain read move the same volume of data over the wire in this direction). The
remainder of the second open's cost (roughly 14.578 − 3.946 − 7.40 ≈ 3.2s) is the connect/stabilise
overhead of that second open, in the same range as — though not identical to, because this is a real
measurement with its own jitter, not the same instrument — 203-SESSION-COST.md's cited 2.607s
Leonardo-class connect median.

**The read term scales with device size.** A larger part (this project's registry goes up to 512 KiB)
would cost proportionally more blank-check wall-clock on the second open; the connect-term component
alone (§4) does not.

## 4. The derivation over Phase 203's cited medians (labelled as a derivation, not re-measured)

Per Fork C and 203's own discipline: quoted verbatim from
`.planning/phases/203-the-write-guard-moves-up-a-layer/203-SESSION-COST.md` §2, measured
2026-09-04 against `firestarter_app` HEAD `df2978e`, ten samples per board class, port pinned:

| Board class | Connect median | Structural floor | Remainder |
|---|---|---|---|
| Uno-class | **2.518s** | 2.500s | 0.018s |
| Leonardo-class | **2.607s** | 2.500s | 0.107s |

**D-01 adds exactly one open** to `erase -b` (the same "+1 open" shape 203-SESSION-COST.md §3 applies
to a guarded plain `write`). Applying that one-open count to the cited medians, per board class:

| Board class | Derived added cost (connect term only) |
|---|---|
| Uno-class | **2.518s** |
| Leonardo-class | **2.607s** |

**This row is a derivation, not a second measurement.** It is Phase 203's own arithmetic
(`extra opens x connect median`), re-stated here for `erase -b` specifically, over a connect-cost
figure measured on 2026-09-04, not re-measured in this document or in `205-BENCH-MATRIX.md`. The two
board classes are never blended, following 203's and 176-MEASUREMENT.md's explicit rule.

## 5. What Phase 206 should do with both numbers

**Both figures are handed to SESS-01, not one in place of the other:**

- The **derivation** (2.607s Leonardo-class / 2.518s Uno-class) isolates the connect-term-only cost
  of the second port open — comparable across any operation that opens one extra port, regardless of
  how much data that second open moves.
- The **measurement** (10.632s, this document, Leonardo-class, N=3, this specific 65536 B part) is
  the real added cost `erase -b` pays *today*, on *this* device size, including the whole-device
  read traffic the connect-term derivation deliberately excludes (§3).
- **Do not blend them, and do not treat the measurement as replacing the derivation.** The
  derivation's value is that it generalises (any extra open costs at least this much, on this board
  class, regardless of device size); the measurement's value is that it is a genuine bench figure for
  the specific, common case (a 64 KiB UV-family part). SESS-01 should scale the read-traffic
  component by device size when reasoning about a larger part, and should treat the connect-term
  component as fixed per open regardless of size.
- **Collapsing the second port open (SESS-01's own job) removes the connect-term component
  entirely** and leaves the read-traffic component largely unavoidable — the blank check still has to
  move the same bytes over the wire even inside a single leased session. The saving SESS-01 should
  expect to measure is closer to the derivation's ~2.6s than to this document's ~10.6s, because most
  of this document's measured figure is read traffic that a leased session does not eliminate.

## 6. Explicit non-measurement statement — what this document does NOT claim

**No true UV part was in the loop for this measurement** — the W27C512 riding the UV handler is a
PROXY (per `205-BENCH-MATRIX.md`'s stated coverage limit throughout). The **port-open structural
cost** measured here is chip-identity-independent (it is a property of `_operation_context` and the
serial transport, not of which family occupies the socket); the **read-traffic** component (§3) is
sized by the part's total byte count, which this measurement's 64 KiB W27C512 shares with several
validated UV-family parts in the registry but not with the largest ones.

This document supersedes nothing in `203-SESSION-COST.md` — that document's own connect-term medians
are cited here, not re-measured, and its explicit non-measurement statement about the write-guard's
three-open figure stands unchanged.

## Provenance table

| Term | Value | Measured or derived | Source |
|---|---|---|---|
| Plain `erase`, Leonardo-class, this rig | 3.946s median (min 3.929s, max 4.138s, N=3) | measured | this document §2, `205-BENCH-MATRIX.md` B7 |
| `erase -b`, Leonardo-class, this rig | 14.578s median (min 14.543s, max 14.753s, N=3) | measured | this document §2, `205-BENCH-MATRIX.md` B7 |
| **Added wall-clock, `erase -b`, Leonardo-class, this rig, this part size (64 KiB)** | **10.632s** | **measured** | this document §2 |
| Whole-device blank-check read traffic component (64 KiB) | 7.40s | measured (CLI-reported, corroborated against `205-BENCH-MATRIX.md`'s equal-size `read` legs) | this document §3 |
| Leonardo-class connect median (cited) | 2.607s (min 2.606s, max 2.676s, N=10) | measured, cited from Phase 203 | `203-SESSION-COST.md` §2, `176-MEASUREMENT.md` §4b |
| Uno-class connect median (cited) | 2.518s (min 2.517s, max 2.519s, N=10) | measured, cited from Phase 203 | `203-SESSION-COST.md` §2, `176-MEASUREMENT.md` §4a |
| Derived added cost, `erase -b`, connect-term only, Leonardo-class | 2.607s | derived | this document §4 |
| Derived added cost, `erase -b`, connect-term only, Uno-class | 2.518s | derived | this document §4 |
| PROXY note | W27C512 rides the UV handler; no true UV part measured | n/a | this document §6, `205-BENCH-MATRIX.md` |

---
*Phase: 205-the-pre-flights-leave-the-firmware*
*Written: 2026-09-22*
