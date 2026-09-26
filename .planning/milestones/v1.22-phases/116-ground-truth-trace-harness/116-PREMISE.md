---
title: TRACE-06 premise — does `firestarter write at28c256` abort at INIT on 3.0.0b11?
date: 2026-07-27
context: >
  Written by Phase 116 Plan 07 (D-14) to settle the milestone's highest-value
  PREDICTED claim one phase early, and to correct the "all 84" framing error
  before six downstream researchers (Phases 117-122) inherit it. Modelled on
  `.planning/notes/dev-test-unknown-chip-fail-fast.md`.
---

# TRACE-06 premise: the AT28C write-abort finding

## 1. The question

Does `firestarter write at28c256` abort at INIT on `3.0.0b11`? `REQUIREMENTS.md` §Framing
names this the milestone's "highest-value PREDICTED claim," assigned to Phase 116 to settle
before any fix is designed — the harness-before-fix ordering invariant exists precisely so
this question is answered from evidence, not assumed from research.

## 2. The finding, at the software layer

**Yes.** `eeprom28c_write_init` returns `RESPONSE_CODE_ERROR` before any data byte is
transferred, for all four `0x0D` pinouts.

Mechanism, traced end to end: `eeprom28c_write_init` calls
`flash_execute_command(EEPROM_SDP_DISABLE)`, the 6-write `AA-55-80-AA-55-20` SDP-disable
sequence (`eeprom_28c.cpp:100-108`), then calls `eeprom28c_wait_for_write(handle, 0x5555,
0x20)` to confirm completion (`eeprom_28c.cpp:131`). That completion check polls
`firestarter_get_data(0x5555)` up to 2000 times, expecting to read back the sequence's own
terminal command byte (`0x20`). Against the harness's address-keyed mock — which reproduces
the virgin `0xFF`-style non-response a part that never recognised the sequence would give —
the poll never observes `0x20`, exhausts its 2000 iterations, emits
`MSG_ERR_EEPROM_TIMEOUT`, and sets `handle->response_code = RESPONSE_CODE_ERROR`
(`eeprom_28c.cpp:151-153`). `eeprom28c_write_init` then returns early: the blank check that
would normally follow never runs, and not one data byte is ever sent to the bus.

## 3. The evidence, and how to re-run it

This is evidence produced by **this phase's harness**, not a transcript copied from
research. Two artifacts carry it, both re-runnable without checking out an old tree:

- **`firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md`** (committed by plan
  116-06) — the parked, RED-by-design suite's verbatim captured output. Section "Response
  code observed after `eeprom28c_write_init`, per pinout" tabulates `RESPONSE_CODE_ERROR (0)`
  for all five traced chip/pinout combinations (`DIP28_28C256`/AT28C256,
  `DIP28_28C64`/AT28C64, `DIP24_2816`/AT28C16, `DIP32_28C512_EEPROM`/AT28C010,
  `DIP32_28C512_EEPROM`/AT28C040).
- **Re-run command:** from `firestarter/`, temporarily add the single line
  `native/avr/test_eeprom28c_sdp` to `platformio.ini`'s `test_filter` allowlist, then run
  `pio test -e native -f "*test_eeprom28c_sdp*"` (or execute
  `.pio/build/native/firestarter_native` directly — `pio test` reports a summary-reporting
  `[ERRORED]`/`SIGBUS` quirk for a binary that exits non-zero on *expected* test failures;
  the binary itself exits cleanly with a plain Unity summary, per RED-BASELINE.md
  "Verbatim captured output"). Remove the allowlist line afterward to restore the 95/95
  default baseline this plan's Task 1 gate re-confirmed.
- **Observed response code per pinout** (from plan 116-06's RED-BASELINE.md, itself matching
  116-RESEARCH.md §F1's independent capture in this same session):

  | Pinout | Chip | `response_code` after `eeprom28c_write_init` |
  |---|---|---|
  | `DIP28_28C256` | AT28C256 (32 KB) | `RESPONSE_CODE_ERROR` (0) |
  | `DIP28_28C64` | AT28C64 (8 KB) | `RESPONSE_CODE_ERROR` (0) |
  | `DIP24_2816` | AT28C16 (2 KB) | `RESPONSE_CODE_ERROR` (0) |
  | `DIP32_28C512_EEPROM` | AT28C010 (128 KB) | `RESPONSE_CODE_ERROR` (0) |
  | `DIP32_28C512_EEPROM` | AT28C040 (512 KB) | `RESPONSE_CODE_ERROR` (0) |

## 4. The validation ceiling — stated, not implied

**Permitted wording** (116-RESEARCH.md §F1, used verbatim):

> On `3.0.0b11`, `eeprom28c_write_init` aborts with `MSG_ERR_EEPROM_TIMEOUT` →
> `RESPONSE_CODE_ERROR` before any data byte is transferred, for all four `0x0D` pinouts.
> Verified by native trace (`pio test -e native`) driving the real `configure_memory` →
> `firestarter_operation_init` path with host-derived `bus_config_t` values. The abort is
> unconditional for any `get_data(0x5555) != 0x20`; per DS20006432B §6.6.2 a part that
> recognised the sequence cannot return `0x20` there. No AT28C part was on the bench; this
> is not a silicon-state claim.

Every claim in this section is **software-layer**. The bridge from "the code aborts against
a mock" to "the code would abort against real silicon" is a **citation, not an
observation**: Microchip DS20006432B §6.6.2 p.10 and DS20006386B p.10 both state that the
SDP command-sequence data "is not written to the device," which is what makes `0x20`
unreachable at `0x5555` on a part that recognised the sequence. This suite never read either
datasheet directly to confirm that wording — it cites `116-RESEARCH.md`'s prior citation of
`.planning/research/SUMMARY.md`.

**Task 1's datasheet-presence audit (RESEARCH Open Question 5), settled here as a concrete
present/absent list, not a general statement:** `firestarter_app/datasheets/` contains
exactly three PDFs — `AT28C256.pdf`, `SST39SF0x0A.pdf`, `W27C020.pdf`. Of the three citations
of record:
- **DS20006432B (AT28C64B)** — absent from the tree by filename search (`find . -iname
  "*DS20006432*"` returns nothing).
- **DS20006386B (AT28C256)** — also absent by that exact document-ID filename; `AT28C256.pdf`
  is in the tree and is presumably a copy of this datasheet, but 116-RESEARCH.md itself flags
  it as carrying "a known notes-2/3 copy-paste error" and does not confirm it is in fact
  DS20006386B. This artifact does not resolve that ambiguity — it only reports it honestly.
- **Atmel doc0270** — absent from the tree by filename search (`find . -iname
  "*doc0270*"` returns nothing).

No AT28C part was on the operator's bench for Phase 116 (confirmed at milestone kickoff).
This is not a silicon-state claim, and it never will be one until a part is on hand.

**Forbidden claims** — a later reader must not mistake this artifact's scope for any of the
following:
- That an AT28C256, AT28C64, AT28C16, AT28C010, or AT28C040 was observed to abort a write.
- That gh#11 or gh#12 are "fixed," "verified," or even necessarily reproduced — Phase 116 did
  not attempt to reproduce either report; it traced the code path both reports would hit.
- That the datasheet citations were read and confirmed by this phase — they were not; Task 1
  found two of the three named PDFs absent by filename and the third unconfirmed.
- That any `support_status` changed, or that the 84-chip `0x0D` count changed. It did not.

**Review test (RESEARCH Pitfall 7):** no sentence above has the chip as its subject rather
than the code. Every claim's subject is `eeprom28c_write_init`, the completion check, the
mock, or the suite — never "the AT28C256" doing something.

## 5. CORRECTION 4 — the framing error this phase corrects

`REQUIREMENTS.md` §Framing and `.planning/research/SUMMARY.md`'s finding 1 both state the
write-inhibit affects "all 84" `0x0D` chips: *"At least one command write is emitted with
`/WE` HIGH — a documented Write Inhibit — on all 84 `0x0D` chips."*

**The measured figure is 66 of 84**, not all 84. Per-pinout breakdown
(116-RESEARCH.md CORRECTION 4, `[VERIFIED: executed in this session]`):

| Pinout | Chips | `rw` bus line | Register domain | Writes inhibited (of 6) |
|---|---|---|---|---|
| `DIP28_28C64` | 35 | 14 | MSB bit 6 | **4** (the four `0x5555` loads) |
| `DIP24_2816` | 19 | 11 | MSB bit 3 | **2** (the two `0x2AAA` loads) |
| `DIP28_28C256` | 12 | 14 | MSB bit 6 | **4** (the four `0x5555` loads) |
| `DIP32_28C512_EEPROM` | 18 | 20 | CONTROL bit `0x10` | **0** at INIT-time register state |
| **total** | **84** | | | **66 chips affected** |

**`DIP24_2816` is inhibited on the *opposite* writes from the DIP28 pinouts** — the `0x2AAA`
loads, not the `0x5555` loads — because `0x2A` has bit 3 set while `0x55` does not. Any prose
that says "the `0x5555` writes are inhibited" is wrong for these 19 chips.

## 6. Why the distinction is load-bearing

Two consequences a later editor must not undo by "simplifying" this correction back to "all
84 chips have a write inhibited":

- **The DIP32 band (18 chips, `DIP32_28C512_EEPROM`) is inhibit-free at plain INIT-time
  register state** — `CTRL_ADDRESS_LINE_17`/`18` start clean on a fresh boot, so a plain trace
  against this pinout would show zero inhibited writes and would look, incorrectly, like this
  band is unaffected. This is exactly why plan 116-06's DIP32 cases (4-5) are *deliberately
  stale-upper-address* cases — seeding `CTRL_ADDRESS_LINE_17|18` HIGH before driving the
  sequence — rather than plain traces. Deleting the 66-of-84 framing and reverting to "all 84"
  makes those two cases look decorative or redundant; they are not. They are the only way
  this pinout's real hazard (a stale upper-address bit left by a *prior* operation staying
  stuck for the entire SDP sequence, because `fu_flash_fast_address` never writes
  `CONTROL_REGISTER` at all) becomes observable, since it is invisible from a fresh boot.
- **The INIT abort (§2 above) is unconditional for every `0x0D` pinout.** Because
  `eeprom28c_write_init` always fails at the completion-check timeout regardless of whether
  any individual command write was inhibited, there is no working `write` behaviour on this
  family to preserve today. This voids the backward-compatibility objection to changing the
  auto-unlock default (option (d), locked 2026-07-27): if AT28C writes already abort
  unconditionally, the cost of changing that default is ~zero, because there is nothing users
  currently rely on that a policy change could break.
