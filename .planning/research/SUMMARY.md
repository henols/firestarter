# Project Research Summary

**Project:** Firestarter — milestone v1.42 "Jumper Display Correctness & Rev 2.2 3-Pin Header"
**Domain:** EPROM programmer (Arduino firmware + Python host CLI + RURP shield hardware)
**Researched:** 2026-09-25
**Confidence:** HIGH for datasheet facts and code paths. MEDIUM for the consequences on silicon: nothing here was measured on a bench, and each bench-dependent claim is labelled.

Scope: Q1 (TI 2516/2532 programming), Q2 (what firmware `0x0B` does), Q3 (Rev 0/1 JP1-JP3 and the per-pin-map jumper table), and planner pitfalls. This document cites the Phase 182 ground truth as "GT note" (`.planning/notes/jumper-display-ground-truth.md`) and does not re-derive it.

*Persisted by the orchestrator from the researcher's inline return (the researcher's own write was refused by the harness). Two claims were spot-checked by the orchestrator on 2026-09-25 before persisting: `firestarter info AM27C010` prints `JP4 ... = Closed` in the `Rev 2.0 & 2.1` block, and `memory_set_data` (`firestarter_fw/src/proms/memory.cpp:361-371`) pulses via `rurp_chip_enable()`, which is `rurp_set_chip_enable(0)` — CE active low (`firestarter_fw/include/rurp_shield.h:114-120`).*

## Executive Summary

**The TI 2516 does not strobe on pin 20.** The TMS2516 data sheet (TI, Dec 1979, rev. May 1982, p.138 operation table) puts PD/PGM on **pin 18**, CS on pin 20 and VPP on pin 21. That is the Intel 2716 arrangement, and TI's own sheet says "Interchangeable with Intel 2716". Only the **TMS2532** strobes on pin 20 (PD/PGM, active LOW), with A11 on pin 18.

- The seed's premise is false for the 2516 and true only for the 2532.
- The todo's claim (DIP24_2716, VPP on pin 21, as the JEDEC 2716) is correct.
- JP4's third pole (periphery-facing, to socket 25 = a 24-pin part's pin 21, GT note) carries **VPP**, not the strobe.
- The "TI distinguisher" the milestone plans for the 2516 therefore has no electrical basis. The 2516 needs what every `DIP24_2716` row needs.

**The real blocker is the firmware `0x0B` write path, and it affects the whole 2716 family.**

- `memory_set_data` pulses the shield's CE line (socket 22 = 24-pin pin 18) **LOW** for `pulse_delay`. Between pulses it leaves CE HIGH (`firestarter_fw/src/proms/memory.cpp:363-371`).
- The 2716, TMS2516 and NMC27C16 program on an **active-HIGH** PGM pulse and inhibit with PGM low.
- So with VPP on and OE high, the firmware holds the part in "program" mode *between* strobes, while `set_address` pushes latch bytes over the shared data bus. The intended 500 µs pulse becomes "inhibit".
- The Intel sheet says: "The 2716 must not be programmed with a DC signal applied to the CE/PGM input".
- This comes from the code and datasheets, not from a measurement. On the operator's irreplaceable, not-blank TMS2516 it would mean uncontrolled bit-clearing.
- **No write to the TMS2516 may happen before this is fixed and trace-tested.**

Two more defects affect the same rows:

1. **Read mode holds pin 21 (VPP) at about 0 V, not VCC.** `memory.cpp:413-416` skips driving the VPP line for "VPP-on-P1" parts. The datasheets require VPP = VCC in read. This is a likely cause (inference) of the v1.15 "2516 read unstable" finding (FUT-03). v1.15 blamed a "shared OE/VPP pin", which the 2516 does not have.
2. **The `DIP24_2532` bus-config sends `256` (the ROM_CE sentinel) as A11.** It is stored in a `uint8_t` as 0, so A11 lands on A0. The 2532 cannot be read or written today.

**Supplies are only partly compatible.**

- The TMS2516 needs single +5 V, plus VPP 25 V ± 1 V while programming (p.140 note 3).
- The shield's VPE design ceiling is **22.53 V** (Rev 2.3 schematic annotation). The Rev 2.1/2.2 BOMs use the same divider values.
- Phase 199 measured **22140 mV at socket pin 1** through composite 0x088 on a Rev 2.0 board. That is the same Q8 P1 route the DIP24_2716 rows use; JP4 only extends it to socket 25.
- The TMS2516 will therefore be programmed **below its 24 V minimum**. That matches the recorded "25 V NMOS best-effort, no hardware change, ever" stance (MILESTONES.md, v1.14 Phase 79).
- The ADC reads about +7.95 % high, so `MSG_WARN_VPP_LOW` (23.75 V threshold) will not fire.

**A separate hazard:** the TI **TMS2716** is a three-supply part (VBB −5 V on pin 21, VDD +12 V on pin 19). It is in the DB as `TI/TMS2716` on DIP24_2716, `supported`, 18000 mV.

## Key Findings

### Q1 — TMS2516 / TMS2532 vs Intel/JEDEC 2716 / 2732

These sources were rendered and read directly:
- TMS2516 pp.137-143, from git object `firestarter_fw@83313fc:datasheets/0x0B-EPROM-LEGACY/2516_EPROM.pdf`. That commit is on branch `v1.16-protocol-first-architecture-rebuild` only, not on any current branch.
- TMS2532 pp.145-146 (jrok.com).
- The TMS2708/2716 + TMS2516 "9900 Family" sheet (xtronics.com).
- Intel 2716 (archive.org).
- National NMC27C16 (deramp.com).

Intel 2732/2732A is MEDIUM: taken from a web-search summary of the ST M2732A sheet, not rendered.

| | Intel 2716 / NMC27C16 | **TI TMS2516** | Intel 2732 / 2732A | **TI TMS2532** | TI TMS2716 (not a 2516) |
|---|---|---|---|---|---|
| Pin 18 | CE/PGM | **PD/PGM** | CE | **A11** | CS (Program) |
| Pin 19 | A10 | A10 | A10 | A10 | **VDD +12 V** |
| Pin 20 | OE | **CS** | OE/VPP | **PD/PGM** | A10 |
| Pin 21 | VPP | VPP | A11 | VPP | **VBB −5 V** |
| VPP pin / level | 21 / 25 V (NMC27C16 25 ± 1, max 26) | 21 / 25 ± 1 V (abs max 28) | 20 (=OE) / 25 V; 2732A 21 V | 21 / 25 V | n/a |
| Program strobe | pin 18 **active HIGH** 50 ms, max 55 | pin 18 **active HIGH** ("Pulsed VIL to VIH"), tw(PR) 45/50/55 ms | pin 18 **active LOW** 50 ms (MEDIUM) | pin 20 **active LOW** ("Pulsed VIH to VIL") 50 ms, max 55 | — |
| Inhibit | CE/PGM low, OE high, VPP 25 | PD/PGM low, CS high, VPP 25 | — | PD/PGM high | — |
| Verify | CE low, OE low, VPP 25 | PD/PGM low, CS low, VPP 25 "(or +5 V)" | — | a read after VPP "returns to +5 V" | — |
| Read-mode VPP | = VCC ("must be at 5V") | +5 V (may tie to VCC except in program mode) | — | +5 V | — |
| Supplies | single +5 V | single +5 V | single +5 V | single +5 V | −5 / +5 / +12 V |

Other TMS2516 facts: p.138, "a 50-millisecond TTL high-level pulse should be applied to the PGM pin … Maximum pulse width is 55 milliseconds". p.141, the setup and hold times are 2 µs min. p.140, IPP2 30 mA max, ICC2 100 mA max.

**Verdicts:**
- **Seed claim "TI strobes on pin 20, Intel on 18":** FALSE for the TMS2516 and TRUE only for the TMS2532. HIGH confidence.
- **Todo claim "2516 = DIP24_2716, VPP on pin 21 as the JEDEC 2716":** CORRECT. HIGH confidence. Its inference that "the 2532 is the part that actually needs it" is half right: every VPP-on-21 part needs the 24-pin pole.
- **v1.15 SR-1** (`81-2516-SAFETY-REVIEW.md` Item 4): the pin assignment is right, but strobe polarity was never checked. Its Item 1 ("CE/OE strobing, 500µs pulses") does not match the datasheet's single active-high 50 ms pulse.
- **`firestarter_app/firestarter/ic_layout.py:270`** says "Shares pins between OE/VPP" for every 0x0B chip. That is true only for DIP24_2732.

### Q2 — What firmware protocol 0x0B does today

**How the host pin map reaches the firmware.**
- `pinouts.json` gives function → DIP pin. `database.py` `pin_conversions` gives DIP pin → RURP bus line (`firestarter_app/firestarter/database.py:45-117`).
- `get_bus_config` (`database.py:240-296`) sends only `bus`, `rw-pin`, `vpp-pin` and `static-high`. **`ce-pin` and `oe-pin` are never sent.**
- The CE and OE lines are hardwired on the shield. They appear as the sentinels `ROM_CE=0x100` and `ROM_OE=0x101` (`database.py:36-37,56-58`).
- A `vpp-pin` that resolves to CE or OE is dropped (`database.py:276-277`), so the firmware uses `vpp_line=0xFF`.
- The firmware parses `bus` into `uint8_t address_lines[20]` (`include/firestarter.h:189-196`, `src/json_parser.c:462`).

**Pin mapping for 24-pin pins 18, 20 and 21:**

| 24-pin | Socket | RURP line | Shield driver | 0x0B role today |
|---|---|---|---|---|
| 18 | 22 | ROM_CE | Arduino D13 (`CHIP_ENABLE` 0x20: `include/rurp_shield.h:55`, `leonardo_rurp_shield.cpp:59-60`), direct to socket 22 | **The program strobe.** Pulsed LOW, idles HIGH (`memory.cpp:363-371`) |
| 20 | 24 | ROM_OE | Arduino D10 (`OUTPUT_ENABLE` 0x04) via D12 + pull-down; VPE via Q3/Q6 on `CTRL_VPE_ENABLE` | Held HIGH in the pulse pass (`memory.cpp:363`). The VPP pin for DIP24_2732 |
| 21 | 25 | bus 11 (A11 latch) | Latch, direct on Rev 0-2.1 and through **D34** on Rev 2.2+, with a 10k pull-down. On Rev 2.2+ also Q8 → JP5 → socket 1 → JP4 periphery pole | `vpp_line=11`. `using_p1_as_vpp()` is true (`include/memory_utils.h:73-76`; `VPP_P21_24_DIP 0x0B` at `rurp_shield.h:40`), so VPE_ENABLE becomes `CTRL_VPP_P1_ENABLE` 0x08 (`eprom.cpp:600-606`) |

D34 first appears at Rev 2.2. It is in `Rev2.2/W27C512Programmer.csv:11` and `-top-pos.csv:47`, and absent from `Rev2.1/W27C512ProgrammerBOM.csv:6` (under `.planning/milestones/v1.7-artifacts/upstream-rurp/hardware/`). It is the blocking diode that makes the third pole safe for the A11 latch.

**The 0x0B block sequence** (`eprom.cpp:262-491`):
1. The regulator is switched on (`eprom_hv_route_mask` → DIRECT_VPE → `CTRL_VPP_REGULATOR_ENABLE`; `eprom.cpp:237-252`, `eprom_params.cpp:33`).
2. Scan pass: bytes are read with CE low, OE low and the route off.
3. Pulse pass: the route is asserted (`eprom.cpp:470`), then 1000 µs setup (`include/eprom.h:93`). Each pending byte gets `set_data`: CE low for 500 µs (`eprom.cpp:66`; the DB value is 500). Then a 100 µs hold, and the route drops (`eprom.cpp:479`).
4. Budgets: 255 pulses and a 50000 µs energy cap. A pulse wider than the cap is refused (`eprom.cpp:94-99`).

**Q2-A (HIGH on code and datasheet; consequence NOT measured). The polarity is inverted for all 15 DIP24_2716 rows.**
- In the pulse pass CE idles HIGH with OE HIGH and VPP up. The datasheets call this "Start Programming", held as a forbidden DC level.
- The address and data change under it in `mem_util_set_address` (`memory.cpp:288-304`), and the data bus is shared with the latch inputs (`include/rurp_register_utils.h:65-75`).
- The intended CE-low pulse is "Inhibit".
- The same code is correct for DIP24_2732. **The pin is right, the polarity is wrong.**

**Q2-B (HIGH on code; the effect is inference). Pin 21 is at about 0 V in read.**
- VPP is driven high only when `vpp_line != 0xFF && !using_p1_as_vpp` (`memory.cpp:413-416`).
- The v1.15 instability record is "3 SHAs, 1.9 % jitter" (`84-05-SUMMARY.md:71`). v1.15 attributed it to a "shared OE/VPP" pin (`81-03-SUMMARY.md:76`), which the 2516 does not have.

**Q2-C (HIGH). DIP24_2532 cannot be driven.**
- Its address bus includes pin 18 (`pinouts.json:131`), which is `ROM_CE`. The wire bus is `[0..10,256]` (run this session).
- `uint8_t` storage turns 256 into 0 (`json_parser.c:462`), so A11 is remapped onto A0 (`memory.cpp:399-407`).
- Physical A11 is the CE line, and PD/PGM is on the OE line.

**Can the pin-map data express the TI strobe?**
- **TMS2516:** no new key is needed, because the pin is already right. What is missing is the **polarity**, and no pin-map key carries it. `rw-pin` is a static level (`memory.cpp:409-411`), and pin 18 cannot be a `rw-pin`.
- **TMS2532:** the pin map cannot express it. It needs a new firmware mode ("CE line = A11, OE line = active-low PGM") plus a wire signal.

**Change list:**

| Repo | Change | For |
|---|---|---|
| fw | When `pins==24 && vpp_line==VPP_P21_24_DIP`: hold CE LOW while the VPP route is up. Change the address and data only while CE is low. Pulse CE HIGH for `pulse_delay`, with OE high. Leave DIP24_2732 (`vpp_line 0xFF`) and the 28/32-pin paths as they are. | TMS2516 and all DIP24_2716 rows |
| fw | Read and verify with VPP = VCC for this class: drive bus 11 high (`memory.cpp:413-416`). D34 blocks VPE on Rev 2.2+. | Stable reads (FUT-03) |
| fw | Native Unity trace tests: the CE level for each register write while the route is up. DIP24_2716 changes, DIP24_2732 stays the same. | Proof before bench |
| host/DB | `get_bus_config` refuses `ROM_CE`/`ROM_OE` in `address-bus-pins` (fail-closed). The 2532 row in `tools/extra_chips.json` stops being `supported` until a 2532 mode exists. | Q2-C |
| generator | `TI/TMS2716` leaves `supported` through `build_db.py` / `datasheet_overrides.json`, with the citation. | Pitfall 3 |
| generator (optional) | The 2716-class pulse width: datasheet single pulse 45-55 ms, against today's 500 µs × up to 100 under the 50 ms cap. | Datasheet fidelity |
| host | No new key for the 2516. The bench needs `firestarter config --rev 4`, because ADC cannot tell 2.2 from 2.0 and CAP-02 refuses `vpp-pin 11` otherwise (`serial_comm.py:749-803`). | Bench |
| docs | Replace the text at `ic_layout.py:270-271`. Settle `firestarter_fw/CLAUDE.md` "Project documents disagree about that jumper" and `firestarter_fw/PROTOCOLS.md:180,183` "via JP4 jumper routing". | Honesty |

No new wire flag is needed if the firmware keys on `(24, VPP_P21_24_DIP)` and the host keeps DIP24_2532 out. If a flag is used instead, it is a `constants.py` / `firestarter.h` lockstep pair, and 0x08 stays reserved.

### Q3 — Rev 0/1 JP1-JP3 from `firestarter_fw/document/rurp_schematics_rev1.pdf`

The title block reads "Rev: 0", although the file is named rev1. The operator says Rev 0 and Rev 1 are identical (GT note).

| Jumper (silkscreen) | Common pin 2 → | Pin 1 | Pin 3 |
|---|---|---|---|
| JP1 "24pin ROM VCC" | socket 28 | A13 net (U3 latch) | +5 V (U3 VCC rail) |
| JP2 ">=SST39SF020 & 28C512 need A17" | socket 30 | +5 V | A17 net |
| JP3 "W27C010/AT27C010 needs p1 VPE/VPP (32 pin)" | J6 pin 3 = Q8 collector (P1_VPP_ENABLE VPE) | socket 3 (A15 node after D11) | socket 1 (A18 node after D33, R12 pull-down) |

What this means:
- No Rev 0/1 path reaches socket 25, and A11 goes to socket 25 with no diode. 24-pin VPP-on-21 parts cannot be programmed on Rev 0/1.
- Q6 (OE, socket 24) and Q7 (A9, socket 26) need no jumper.
- Rev 2.x replaces JP1 and JP2 with the Q11/Q12 (A13 → P28) and Q9/Q10 (A17 → P30) switches (Rev 2.3 sch). The firmware drives them through `static-high [13]` and `CTRL_ADDRESS_LINE_17` (`memory.cpp:203`).

**Today's code** (`ic_layout.py:140-167`; derivation at `:598-638`):
- JP1 and JP2 are correct.
- JP3 is wrong for two maps, because it keys on `"vpp-pin" in pin_map`:
  - DIP28_27512 gets "28pin". It should be off, because VPP is on OE via Q6.
  - DIP32_27C801 gets "32pin". It should be off, because pin 1 is A19.
- There is no "unreachable" note for the 24-pin VPP-21 maps.

**New defect, not in the GT note:** Rev 2.0/2.1 JP4 prints **"Closed" for DIP32_STD (70) and DIP32_27C020 (88)**. `firestarter info AM27C010` shows it (run this session). The Rev 2 silkscreen says Open for 32-pin ROMs (`.planning/milestones/v1.37-phases/182-jp5-destructive-operation-gate/evidence/shield-rev2-jp4-jp5.jpg`). The GT note's population table marks these maps "Correct", which is wrong. If the Closed pole reaches socket 3 (inferred, PROBE-PENDING), "Closed" puts VPE on pin 3 (A15).

### Draft per-pin-map jumper table (16 pin maps, 746 rows)

Legend:
- **n/m** — the jumper does not matter.
- **off** — leave the jumper off. The chip does not use it, but a wrong position joins socket 1 to a live pin.
- Rev 2.2/2.3 poles: **28-pin pole** = socket-facing, **24-pin pole** = periphery-facing. Both were measured (GT note).
- `[PP]` = the cell depends on the Rev 2.0/2.1 Closed-pole destination, which is PROBE-PENDING (inferred to be socket 3).
- `[INF]` = inference.

| Pin map (rows) | VPP lands | R0/1 JP1 | R0/1 JP2 | R0/1 JP3 | R2.0/2.1 JP4 | R2.2/2.3 JP4 | Wrong today |
|---|---|---|---|---|---|---|---|
| DIP24_2716 (15) | pin 21 → socket 25 (P1) | +5 V | n/m | n/m + note: VPP unreachable, needs Rev 2.2+ 24-pin pole (999.55) | n/m `[PP]` + note | **24-pin pole** (SETTLED) | "N/A", no note, no 2.2 block |
| DIP24_2532 (1) | socket 25 | +5 V | n/m | as DIP24_2716 | as DIP24_2716 | 24-pin pole, but the chip cannot be driven (Q2-C): print a refusal | implies the chip works |
| DIP24_2732 (16) | OE, socket 24 (Q6) | +5 V | n/m | off | n/m `[PP]` | **off** (24-pin pole ties socket 1 to A11) | no 2.2 block |
| DIP24_2816 (19) | none (WE on 21) | +5 V | n/m | off | n/m `[PP]` | **off** (24-pin pole ties socket 1 to WE) | no 2.2 block |
| DIP24_6116 (7) | none (WE on 21) | +5 V | n/m | off | n/m `[PP]` | **off** | no 2.2 block |
| DIP28_2764 (58) | pin 1 → socket 3 | A13 | +5 V | **28pin** | **Closed** `[PP]` | **28-pin pole** | no 2.2 block |
| DIP28_27256 (67) | pin 1 → socket 3 | A13 | +5 V | **28pin** | **Closed** `[PP]` | **28-pin pole** | no 2.2 block |
| DIP28_27512 (45) | OE socket 24; pin 1 = A15 | A13 | +5 V | off | **Open** | off | JP3 "28pin", JP4 "Closed" |
| DIP28_28C256 (30) | none; pin 1 = A14 | A13 | +5 V | off | Open | off | no 2.2 block |
| DIP28_28C64 (35) | none; pin 1 NC | A13 (n/m `[INF]`) | +5 V | off | Open | off | no 2.2 block |
| DIP28_JEDEC_SRAM_8K (14) | none | A13 (n/m `[INF]`) | +5 V | off | Open | off | no 2.2 block |
| DIP32_STD (70, incl. 39 × 0x10) | pin 1 → socket 1 | A13 | A17 | **32pin** | **Open** | **no jumper** | **JP4 "Closed" (new)** |
| DIP32_27C020 (88) | pin 1 → socket 1 | A13 | A17 | **32pin** | **Open** | no jumper | **JP4 "Closed" (new)** |
| DIP32_27C801 (8) | OE socket 24; pin 1 = A19 | A13 | A17 | **off** | Open; JP5 must be cut (Phase 182 gate) | off | JP3 "32pin", JP4 "Closed" |
| DIP32_SST39SF040 (255) | none; pin 1 = A18 | A13 | A17 | off | Open | off | no 2.2 block (999.59 is out of scope) |
| DIP32_28C512_EEPROM (18) | none; WE on 30 | A13 | **A17** | off | Open | off | no 2.2 block |

The Rev 0/1 cells come from the PDF (D-4). The operator's *modified* Rev 0 has unobserved electricals and may differ.

### Critical Pitfalls

1. **Do not key JP4 on `vpp_mv` or on `"vpp-pin" in map`.** All 746 rows have a non-zero `vpp_mv`, including SRAM and flash rows (census, this session). `vpp-pin` also appears where VPP is on OE (2732, 27512, 27C801). Key on the socket where the resolved VPP lands: 1, 3, 25 or OE.
2. **Do not add a "pgm-on-pin-20" field for the 2516.** It would send the pulse to CS.
3. **Do not build a manufacturer-keyed "TI" distinguisher.** It sweeps in the three-supply `TI/TMS2716`, and TI rows sit under two keys, `TI` and `TEXAS INSTRUMENTS`.
4. **Do not write the TMS2516 before the firmware fix is trace-proven.** The part is irreplaceable, there is no UV eraser, and it is NOT blank (0x68@0x0000). The proof write must be bit-masked (260821-wna precedent) and must follow a stable N≥3 read.
5. **Do not claim in-spec programming.** The ceiling is about 22.5 V against a 24 V minimum. Record the meter reading next to the 24 V figure.
6. **Do not claim TMS2532 silicon proof** (D-5), and do not present the 2532 as working (Q2-C).
7. **Do not hand-edit `chip_database.json`.** The TI rows are in `tools/extra_chips.json`. Changes go through `build_db.py` / `datasheet_overrides.json` with a citation.
8. **Do not reproduce the two-state silkscreen clause**, even in the Rev 2.0/2.1 block. Print the per-chip result, and write to "Only for ROMs with VPP on P1".
9. **Do not print "does not matter" for Rev 2.2 JP4 on 28/32-pin parts.** The 24-pin pole on those parts is the 999.56 hazard. Say "no jumper".
10. **No source-scanning tests** (`.planning/notes/test-suite-source-introspection-removal.md`). A coverage test driven by `pinouts.json` is fine. Prove the firmware polarity with native trace tests.
11. **`firestarter_app/tests/test_ic_layout.py:281-308` goes red by design.** It needs a "2.0 & 2.1" key and forbids any "2.2" key. Rewrite it deliberately, and keep the JP5-absent test at `:271-278`.
12. **New firmware messages go through `tools/catalog/messages.toml` plus meta codegen only.** The new `info` strings are STE-strict: run `ste-lint.py`.
13. **Do not copy Phase 199's "22140 is a pin-1 figure on a path those rows do not use"** (`199-BENCH-RECORD.md:133-136`). It is the DIP24_2716/2532 path, and DIP24_2732 VPP is on pin 20.
14. **Do not loosen CAP-02.** Use `config --rev 4`.
15. **Take the chip out before firmware sideloads on Uno-class boards**, and verify the `controller:` identity of each port per task.

## Implications for Roadmap

Phase numbers continue at 208.

1. **Phase 208 — Bench evidence: unpowered, socket empty.**
   - Delivers: the Rev 2.0 JP4 continuity probe to sockets 1, 3 and 25. On Rev 2.2: a diode test for D34 (socket 25 to the A11 latch) and a sighting of the 24-pin-pole corner.
   - Why first: it settles the `[PP]` cells. No code.
2. **Phase 209 — Per-pin-map derivation and three revision blocks** (host).
   - Delivers: the 16-row table above, a fail-closed `pinouts.json` coverage test, the 999.55 note, the DIP32 JP4 fix, and the rewrite of `test_ic_layout.py:281-308`.
3. **Phase 210 — 999.65 VPP label and "Can be erased" line.** Small and host-only; it can fold into 209.
4. **Phase 211 — DB and generator safety.**
   - Delivers: TMS2716 out of `supported`; the 2532 fail-closed (host guard and `extra_chips` status); TMS2516, TMS2532 and Intel 2716 datasheets vendored into `firestarter_app/datasheets/` (the `extra_chips` datasheet path is dangling today); optionally the 2716-class pulse width.
   - Must come before 212: the firmware's `(24, 0x0B)` key is safe only after the 2532 is excluded.
5. **Phase 212 — Firmware 0x0B fix for the 2716 class.**
   - Delivers: the polarity fix, read-VPP = VCC, and native trace tests.
   - **Research flag:** the pass-batched loop, the `SERIAL_ON_IO` window with 50 ms pulses, `write_budget_s`, and the leonardo flash budget.
6. **Phase 213 — TMS2516 bench on Rev 2.2** (operator-gated). Steps in order:
   1. Empty-socket CE and VPP checks (`dev reg` / `dev addr` with `FLAG_CHIP_ENABLE` / `FLAG_OUTPUT_ENABLE`; meter on socket 25 at pot maximum).
   2. N≥3 stable read.
   3. Masked write.
   4. Verify, and record VPP against 24 V.
7. **Phase 214 — Wiki jumper tables and re-exported photographs (999.58).** Last, so it matches what shipped.

Order in short: probe → display (no firmware dependency) → DB (makes the firmware key safe) → firmware → bench → wiki. Phases 212 and 213 need deeper research or a bench plan. The others use established patterns.

## Confidence Assessment

| Area | Confidence | Notes |
|---|---|---|
| Q1 datasheets (2516, 2532, 2716, TMS2716, NMC27C16) | HIGH | primary sheets rendered and read |
| Intel 2732/2732A polarity | MEDIUM | from a search summary |
| Q2 code paths and wire bytes | HIGH | code read; `get_bus_config` / `convert_to_programmer` run |
| Silicon consequences (spurious programming, VPP-0 V read) | MEDIUM / inference | not measured |
| Q3 Rev 0/1 routing | HIGH (PDF) | modified Rev 0 may differ; Rev 2.0/2.1 Closed pole PROBE-PENDING |
| Rail vs 24 V | MEDIUM | design annotation + one Rev 2.0 measurement; Rev 2.2 unmeasured |

### Gaps to Address
- **2716-class pulse strategy at about 22 V:** a single 50 ms pulse, or iterative 500 µs pulses under the 50 ms cap. Only the bench can decide.
- **Rev 2.2 VPE at socket 25:** never measured.
- **Rev 2.0/2.1 JP4 Closed destination:** still PROBE-PENDING.
- **The 13 non-TI DIP24_2716 rows:** only Intel 2716 and NMC27C16 are datasheet-confirmed active-high. The DB `vpp_mv` values of 12-18 V disagree with the NMC27C16 sheet's 25 V.
- **Research seams:** `research-plan` / `research-store` were not used, because of the no-write rule. Confidence tiers were assigned by source type.

## Sources

Primary datasheets (HIGH):
- TMS2516 data sheet: `firestarter_fw` commit `83313fc`, path `datasheets/0x0B-EPROM-LEGACY/2516_EPROM.pdf`
- [TI TMS2532 data sheet](https://www.jrok.com/datasheet/TMS2532.pdf)
- [TI TMS2708/2716 + TMS2516 sheet](https://xtronics.com/memory/TMS2716.pdf)
- [Intel 2716 data sheet](https://archive.org/download/2716-32/2716-32_text.pdf)
- [National NMC27C16 data sheet](https://deramp.com/downloads/mfe_archive/050-Component%20Specifications/National%20Semiconductor/Memory%20Components/National%2027c16.PDF)
- [ST M2732A data sheet](https://ee.hawaii.edu/~sasaki/EE260/Labs/Datasheets/m2732a.pdf) (MEDIUM, via search summary)

Schematics and board artefacts (HIGH):
- `firestarter_fw/document/rurp_schematics_rev1.pdf`
- `.planning/milestones/v1.7-artifacts/upstream-rurp/hardware/RelativelyUniversalROMProgrammerRev2.3.pdf`
- `RelativelyUniversalROMProgrammer.kicad_sch:12390` (VPE-Max 22.53 V)
- `Rev2.1/*.csv`, `Rev2.2/*.csv`
- The Rev 2 silkscreen photograph (path above)

Code (HIGH):
- Firmware: `src/proms/{eprom.cpp, eprom_params.cpp, memory.cpp}`; `include/{eprom.h, eprom_params.h, memory_utils.h, rurp_shield.h, rurp_pinout.h, rurp_register_utils.h, firestarter.h}`; `src/json_parser.c`
- Host: `firestarter/{database.py, ic_layout.py, eprom_info.py, serial_comm.py}`, `data/pinouts.json`, `tools/extra_chips.json`, `tests/test_ic_layout.py`

Project records:
- The GT note; the design audit; the seed; the two pending todos
- ROADMAP 999.55, 999.56, 999.58, 999.59, 999.65
- v1.15 Phase 81 (SAFETY-REVIEW, 81-03) and Phase 84 (84-05)
- v1.40 Phase 199 BENCH-RECORD
- MILESTONES.md, v1.14 Phase 79 entry
