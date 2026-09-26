# 59-SRAM-AUDIT.md — GATE-04 SRAM/NVRAM Behavioral Audit

**Date:** 2026-06-09
**Phase:** 59 — Correctness Gate + Per-chip Diff + SRAM Audit
**Milestone:** v1.11 — Complete infoic.xml Decode & Database Correctness
**Status:** COMPLETE — Safety Verdict: NO ESCALATION

---

## Scope

This audit covers two layers of the SRAM/NVRAM path in Firestarter:

1. **Firmware Layer** — `configure_sram()` in `firestarter/src/proms/sram.cpp`: confirms the
   function is a near-no-op (no VPP assertion, no regulator enable, no pin configuration).

2. **Host-Side Dispatch** — `check_dispatch.py` BLOCKER-2 guard: confirms that all chips with
   SRAM protocols `{0x0E, 0x27, 0x28, 0x29}` route to `configure_sram` and that zero chips with
   these protocols route to `configure_eprom` (which would enable the 12V VPP boost regulator on
   a 5V part).

The audit additionally documents the three required NVRAM behavioral truths (D-04) and records
an explicit Safety Verdict.

**Out of scope:** New firmware handler design; firmware sub-repo code changes (none needed);
0x2A/0x2C/0x2E protocol feasibility (protocol removed from KNOWN_PROTOCOLS in Phase 57,
confirmed infeasible per scope-correction 2026-06-08).

---

## Firmware Layer Audit

**Subject:** `firestarter/src/proms/sram.cpp` + `firestarter/include/sram.h`

**Finding:** `configure_sram` is a **near-no-op**.

The entire body of `configure_sram` is:

```
void configure_sram(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CONFIGURING_SRAM);
}
```

This function does exactly one thing: emit a debug log message
(`LOG_DEBUG_ID_SUB(DBG_CONFIGURING_SRAM)`). It performs:

- NO pin configuration
- NO VPP assertion (no `CTRL_VPP_REGULATOR_ENABLE`, no `CTRL_VPP_P1_ENABLE`,
  no `CTRL_VPP_A9_ENABLE`, no `CTRL_VPE_ENABLE`)
- NO regulator enable
- NO chip-enable sequence
- NO blank-check customization

The actual read/write bus operations are dispatched through the standard
`firestarter_handle_t` operation function pointers (`.firestarter_operation_main`,
`.firestarter_operation_write`, etc.), which handle generic JEDEC SRAM byte-read/byte-write
I/O. `configure_sram` only seeds the debug path; the bus I/O is entirely generic.

**`sram.h` finding:** `firestarter/include/sram.h` declares only:
`void configure_sram(firestarter_handle_t* handle);`

No additional state, no WP#-control bits, no voltage-routing fields. The header adds zero
SRAM-specific state to the `firestarter_handle_t` structure.

**Verdict:** The firmware SRAM handler is functionally correct for the JEDEC SRAM byte-write
use case. It adds no hardware-damage surface. The VPP regulator path is completely absent.

---

## Host-Side Dispatch Audit

**Subject:** `firestarter_app/tools/check_dispatch.py` BLOCKER-2 guard

The BLOCKER-2 guard in `check_dispatch.py` defines:

```
_SRAM_PROTOCOLS = {0x0E, 0x27, 0x28, 0x29}
```

These four protocol IDs correspond to:
- `0x0E` — `SRAM_32PIN` (32-pin SRAM, e.g., 6264/62256 family)
- `0x27` — `SRAM_24PIN` (24-pin SRAM)
- `0x28` — `SRAM_STD` (standard SRAM)
- `0x29` — `SRAM_512K_1M` (larger SRAM/NVRAM, DS1225/M48T08 class)

The BLOCKER-2 guard simulates the firmware dispatch chain (`configure_memory` in
`firestarter/src/proms/memory.cpp`) for every chip in `chip_database.json`. It asserts:

> No chip whose `algorithm` (protocol_id) is in `_SRAM_PROTOCOLS` resolves to
> `configure_eprom` in the simulated dispatch.

**Proof:** `cd firestarter_app && python tools/check_dispatch.py` (Phase 58-03 result, confirmed
against the 743-chip regenerated DB, commit `f822498`):

```
PASS: all 743 chips have a valid dispatch path;
0 SRAM chips route to configure_eprom;
0 DIP28_2764 Flash/EEPROM chips route to configure_eprom;
0 Flash/EEPROM chips route to configure_eprom;
0 wire-key regressions
```

**Why this is the primary host-side safety proof:** `configure_eprom` is the only handler that
calls `eprom_check_vpp()` which enables `CTRL_VPP_REGULATOR_ENABLE` (the 12V boost regulator).
If a SRAM-protocol chip were routed to `configure_eprom`, the 12V regulator would be asserted
on a 5V SRAM part. The BLOCKER-2 guard confirms this path is entirely blocked: 0 of 743 chips
with SRAM protocols reach `configure_eprom`.

**Note on Pitfall 5 (59-RESEARCH.md):** Auditing only the firmware `sram.cpp` file (2 lines)
would miss this host-side proof — the firmware near-no-op finding alone does not demonstrate
that the dispatch chain never calls a VPP-asserting handler. The BLOCKER-2 guard is the
necessary second layer of evidence.

---

## NVRAM Behavioral Truths

[CITED: .planning/research/PITFALLS.md §E-3]

The following behavioral truths apply to NVRAM and FRAM devices supported via the SRAM
protocol set (`{0x0E, 0x27, 0x28, 0x29}`).

### (a) Blank-Check Limitation

**Affected families:** DS1225, DS1230, DS1245, M48T02, M48T08, M48T35, FM1608, FM16W08,
FM1808, BQ4010, BQ4011 (battery-backed NVRAM and ferroelectric FRAM)

NVRAM and FRAM devices **retain data indefinitely** via battery backup or ferroelectric
polarization. They are **NEVER factory-blank** (all 0xFF). Unlike UV-EPROMs, these parts
cannot be bulk-erased — they can only be overwritten byte-by-byte.

Consequence for Firestarter write operations:

- If `FLAG_SKIP_BLANK_CHECK` (0x08) is **absent** (the default), the write path performs a
  blank-check before writing. For a non-blank NVRAM chip this blank-check will **always fail**,
  and the write will be aborted. This is not a defect — it is correct behavior given the chip's
  non-blank state.
- Operators must either:
  - Set `FLAG_SKIP_BLANK_CHECK` (pass `-b` or equivalent flag) to skip the blank-check and
    overwrite directly, or
  - Accept that blank-check failure is expected for these parts and use a write-with-skip-blank
    invocation.

This is an operator consideration, not a hardware-damage path.

### (b) WP# Pin Behavior (DS1225 / M48T08 class)

Two distinct write-protect mechanisms exist in the SRAM/NVRAM families supported by Firestarter.

**DS1225 class** (DS1225, DS1230 — 8K/32K battery-backed SRAM, DIP28):
- Write-protect is controlled by the **hardware WP# pin** (pin 26 on the DS1225 DIP28 package).
- WP# is typically **internally pulled low** by default, meaning writes are enabled without any
  external intervention.
- An operator who has wired WP# high (external pull-up or board routing) will observe that
  writes fail silently. This is a non-destructive failure mode — no hardware damage occurs.
- The RURP generic SRAM write path does NOT drive WP# (it is not modeled in the pinout). The
  DS1225 write-protect behavior is therefore entirely passive from the firmware's perspective.
- [ASSUMED: standard DS1225 datasheet behavioral claim — internally pulled low; worst case is
  a non-destructive write failure. Risk: LOW per 59-RESEARCH.md Assumption A2.]

**M48T08 class** (M48T02, M48T08, M48T35 — timekeeper SRAM, DIP28/DIP32):
- Write-protect is controlled by **bit 7 of the control register byte** (for M48T08, the control
  byte is at address 0x1FF8 within the SRAM array).
- This is a **software-accessible bit**, NOT a hardware pin — it lives in the chip's data space
  and must be cleared by writing a 0 to bit 7 of that address before performing other writes.
- The firmware's generic SRAM write path (`configure_sram` + standard bus I/O) does **NOT**
  clear the M48T08 write-protect bit automatically.
- Operators programming an M48T08-class timekeeper with write-protect set must pre-clear the
  control register byte before the write operation, or use a memory image that includes a cleared
  control byte.
- [ASSUMED: standard M48T08 datasheet behavioral claim — control register at address 0x1FF8 with
  WP bit 7; worst case is a non-destructive write failure. Risk: LOW per 59-RESEARCH.md
  Assumption A2.]

**Safety verdict for WP# behavior:** Neither DS1225 nor M48T08 write-protect mechanism
represents a hardware-damage path on the RURP shield. The worst case is a silent write failure.
No firmware escalation is needed for this class of behavior.

### (c) RTC Oscillator Side Effect

**Affected families:** DS1225 (note: RTC is in timekeeper variants), M48T08, M48T35, and other
timekeeper NVRAM parts containing a 32.768 kHz oscillator and RTC counter.

Timekeeper NVRAM devices contain a **32.768 kHz crystal oscillator** and an **RTC (Real-Time
Clock) counter** integrated on-chip. The oscillator starts running as soon as VCC is applied to
the device — including during a RURP read or write operation.

Consequences:

- A seated timekeeper chip has its RTC **running** during any programming operation.
- This is **NOT a hardware-damage path** — the oscillator and counter circuits are designed to
  operate continuously with VCC present.
- It is a **state-change side effect**: if the RTC was previously set to a specific time, the
  clock advances by the duration of the programming operation. For an operation lasting ~1 minute,
  the RTC will have advanced by ~1 minute.
- **Operator action:** After programming a timekeeper NVRAM, the RTC time should be re-set if
  accurate timekeeping is required. This applies to both read and write operations (even a read
  advances the clock).

This is an operator awareness item, not a safety concern.

---

## Safety Verdict

**Verdict: NO GENUINE SAFETY ISSUE FOUND. NO FIRMWARE ESCALATION NEEDED.**

The audit finds:

1. `configure_sram` in `firestarter/src/proms/sram.cpp` is a near-no-op: it emits a debug log
   message and delegates all bus I/O to the generic `firestarter_handle_t` callbacks. No VPP
   regulator path exists in this function.

2. The BLOCKER-2 guard in `check_dispatch.py` confirms that 0 of 743 chips with SRAM protocols
   `{0x0E, 0x27, 0x28, 0x29}` route to `configure_eprom` — the only handler that asserts the
   12V VPP boost regulator. This is the primary host-side safety proof.

3. The three NVRAM behavioral truths — blank-check limitation, WP# behavior (DS1225/M48T08
   class), and RTC-oscillator side effect — are operator considerations and awareness items.
   None of them represent hardware-damage paths on the RURP shield.

**Escalation criterion (D-04):** A firmware backlog item would be raised ONLY if a real safety
issue had surfaced — specifically, if the audit had found a path by which `configure_sram`
dispatch could assert the VPP boost regulator on a 5V SRAM part, or if a SRAM-protocol chip
were found routing to `configure_eprom`. No such path was found.

This is an **audited verdict**, not a silent dismissal. The escalation criterion is stated
explicitly so future reviewers understand why no firmware item was created.

**DS1225/M48T08 assumption caveat:** The WP# behavioral claims carry an [ASSUMED] marker per
59-RESEARCH.md Assumption A2. The worst-case consequence of an incorrect assumption is a
non-destructive write failure — not hardware damage. The risk is LOW.

**Firmware sub-repo:** UNTOUCHED. This is a host-only, documentation-only deliverable (D-04 /
D-05 host-only milestone boundary). No `firestarter/` changes are made or needed.

---

## Shipped Doc Pointer

The operator-facing subset of this audit lives at:

`firestarter_app/doc/sram-nvram-behavior.md` (sub-repo, GitHub-visible, committed in lockstep
with this planning artifact as part of Phase 59 Plan 02).

That document is the D-04 layer 2 deliverable — it covers the three behavioral truths and the
safety note for an operator audience, omitting the firmware-source quotation and the host-side
dispatch-proof internals documented here.
