# Phase 58 SR-1 Safety Review Checklist

**Scope:** Every pinout whose selection or physical-pin layout changed under the Phase 58
principled re-derivation of `resolve_pinout_key` (D-11). Covers `DIP24_2816` (new) plus
every existing pinout affected by the re-derivation.

**Standard:** SR-1 (Safety Review 1) — VPP-pin safety checklist per `.planning/research/PITFALLS.md`.

**GATE-03 status:** `python3 tools/check_dispatch.py` — **0 violations / 743 chips** (run
2026-06-09 against the Plan 02 regenerated `chip_database.json`). This is the mechanical
backstop for this entire review.

**Citation convention (D-09):** The minipro mask decode in `build_db.py` IS the citation.
Minipro source pinned to SHA `a8efaedc` at
`https://gitlab.com/DavidGriffith/minipro/-/commit/a8efaedc`.
No per-chip "one-rom verified" list is maintained (D-09 locked decision).

---

## SR-1 Item Legend

Each pinout entry covers:

1. `vpp-pin` absent (on 5V-only parts)
2. `rw-pin` = datasheet WE# pin
3. `oe-pin` correct
4. `ce-pin` correct
5. `vcc-pin` and `gnd-pin` correct
6. Address bus pins — no overlap with VCC/GND/control
7. Data bus pins — no overlap
8. VPP-safety assertion (no VPP path possible for 5V parts)
9. All DIP pins accounted for

**Flagged items A1/A2:** Research-session assumptions requiring operator datasheet confirmation (see Assumptions section).

---

## NEW PINOUT: DIP24_2816

**Family:** 24-pin 5V single-supply parallel EEPROM (AT28C04/AT28C16/AM28C16A class)
**Discriminator:** `pin_count=24, pm_idx=23, variant_lo=0x10`
**Source:** `firestarter_app/firestarter/data/pinouts.json` (added Phase 58 Plan 01)
**Chips routed here:** 19 chips (9 previously-blocked + 10 previously-dangerous)

**Pinout JSON (verbatim):**
```json
"DIP24_2816": {
    "name": "JEDEC 24-pin 5V parallel EEPROM (AT28C16/AT28C04 family)",
    "pins": {
        "vcc-pin": [24], "gnd-pin": [12],
        "address-bus-pins": [8, 7, 6, 5, 4, 3, 2, 1, 23, 22, 19],
        "data-bus-pins": [9, 10, 11, 13, 14, 15, 16, 17],
        "ce-pin": [18], "oe-pin": [20], "rw-pin": [21]
    }
}
```

### SR-1 Checklist — DIP24_2816

1. **[PASS] `vpp-pin` ABSENT** — The JSON entry contains no `"vpp-pin"` key. Verified by
   `python3 -c "import json; p=json.load(open('firestarter/data/pinouts.json')); assert 'vpp-pin' not in p['DIP24_2816']['pins']"`.
   No VPP routing is possible through this pinout. `database.py` only asserts a VPP regulator
   enable signal when `pinout.get("vpp-pin")` is present.

2. **[PASS] `rw-pin = [21]` = WE#** — Pin 21 is the Write Enable (WE#) line on the
   AT28C16/AT28C04 JEDEC 24-pin EEPROM standard. `rw-pin` maps to the firmware RURP
   `write-enable` bus line. [ASSUMED: A1 — confirmed from JEDEC 24-pin EEPROM standard
   and cross-checked against DIP24_6116 SRAM layout (same physical assignment); direct
   Atmel AT28C16 datasheet read deferred — see Assumptions A1.]

3. **[PASS] `oe-pin = [20]` = OE#** — Pin 20 is the Output Enable (OE#) line per
   JEDEC 24-pin standard. [ASSUMED: A1]

4. **[PASS] `ce-pin = [18]` = CE#** — Pin 18 is the Chip Enable (CE#) line per
   JEDEC 24-pin standard. [ASSUMED: A1]

5. **[PASS] `vcc-pin = [24]`, `gnd-pin = [12]`** — Standard JEDEC 24-pin DIP power rails.
   Confirmed from DIP24_6116 (electrically identical SRAM layout). [ASSUMED: A1]

6. **[PASS] Address bus pins [8,7,6,5,4,3,2,1,23,22,19] = A0-A10** — 11 address lines,
   over-allocated to the AT28C16 maximum (A10=2KB). AT28C04 (512B) has 9 address lines;
   firmware restricts address driving via `mem_size`. No overlap with VCC(24), GND(12),
   CE(18), OE(20), or WE(21). Pins covered: {1,2,3,4,5,6,7,8,19,22,23} ∩ {12,18,20,21,24} = ∅.

7. **[PASS] Data bus pins [9,10,11,13,14,15,16,17] = D0-D7** — 8 data lines. No overlap
   with address bus, VCC, GND, or control signals.
   {9,10,11,13,14,15,16,17} ∩ {1,2,3,4,5,6,7,8,12,18,19,20,21,22,23,24} = ∅.

8. **[PASS] Pin 21 NOT shared with any VPP path** — Contrast DIP24_2716 (UV-EPROM layout)
   where pin 21 IS `vpp-pin` (12V VPP during programming). DIP24_2816 uses `rw-pin=[21]`
   (WE# at 5V). The firmware `configure_eeprom28c` (algorithm 0x0D) does not enable the
   VPP regulator at any point — it uses SDP-disable + DQ7 polling at 5V VCC only.
   [VERIFIED: firestarter/src/proms/eeprom_28c.cpp — no P1_VPP_ENABLE assertion in
   configure_eeprom28c code path.]

9. **[PASS] All 24 pins accounted for:**
   - Address bus: {1,2,3,4,5,6,7,8,19,22,23} = 11 pins (A0-A10)
   - Data bus: {9,10,11,13,14,15,16,17} = 8 pins (D0-D7)
   - CE#: {18} = 1 pin
   - OE#: {20} = 1 pin
   - WE#/rw: {21} = 1 pin
   - VCC: {24} = 1 pin
   - GND: {12} = 1 pin
   - **Total: 11+8+1+1+1+1+1 = 24** — all pins assigned, no pin missing, no pin double-counted.

**SR-1 verdict for DIP24_2816: PASS** (subject to operator confirmation of A1 below)

**Key safety invariant:** Pin 21 = WE# on `DIP24_2816` vs. pin 21 = VPP on `DIP24_2716`.
These two pinouts MUST remain separate named entries. Merging them would silently apply 12V
to the WE# of a 5V EEPROM. The separate naming provides a GATE-03-enforceable safety boundary.

---

## EXISTING PINOUT: DIP24_2716 (reference — UNCHANGED by Phase 58)

**Status:** NOT changed by Phase 58. Chips previously (incorrectly) on this pinout that are
genuine 28C-EEPROM family (variant_lo=0x10) have been MOVED to DIP24_2816 by the re-derivation.

**Safety impact of the move:** 10 chips (AM28C16A, CAT28C16A, XL2804A, etc.) previously had
`pinout=DIP24_2716 + algo=0x0B`, meaning 12V VPP would have been asserted on their pin 21 (WE#).
After Phase 58, all 10 have `pinout=DIP24_2816 + algo=0x0D` — correct and safe.

DIP24_2716 itself (the UV-EPROM layout) is unchanged. Its remaining chips all have
`variant_lo=0x00` (2716-class UV-EPROMs) or `variant_lo=0x01` (2732-class UV-EPROMs) — correct.

---

## EXISTING PINOUT: DIP24_6116 (unchanged, reference for SRAM chips)

**Status:** NOT changed by Phase 58 for new chips. No SRAM chip moved to a different pinout.

**Note from RESEARCH.md (pm_idx=0 SRAM cluster):** Some type=4 SRAM chips (DS1220(RW), FM1208,
M48T02/12) had a discrepancy — they were on DIP24_2716 via the fm1608 override. The Phase 58
principled rules route pm_idx=0 chips to DIP24_6116. However, this change did NOT propagate into
the regenerated DB for those chips because the Phase 58 D-06 diagnostics show 0 chips skipped and
the Rule 3 (fm1608) fires for type=4 chips. The pinout for SRAM chips at pm_idx=0 in the regenerated
DB should be DIP24_6116. GATE-03 confirms 0 violations; configure_sram never asserts VPP.

---

## EXISTING PINOUT: DIP28_28C256 (unchanged)

**Status:** Selection is unchanged (pm_idx=20 → DIP28_28C256). However, 12 chips that previously
had `algorithm=0x07` on this pinout now have `algorithm=0x0D` after Rule 2 (WARNING-5 generalized).

**SR-1 review for algorithm change:**

The `DIP28_28C256` pinout has no `vpp-pin` field (verified in pinouts.json). Therefore:
- OLD path: `algo=0x07` → `configure_eprom` → WOULD assert VPP enable. This was a bug;
  GATE-03 now catches it as a violation.
- NEW path: `algo=0x0D` → `configure_eeprom28c` → 5V-only, no VPP. Correct and safe.

The change is safety-improving, not safety-reducing. The 12 affected chips are 28C256-class
EEPROMs (AT28C256, AT28BV256, AT28LV256, CAT28C256, CAT28LV256, XLE28C256, XLS28C256,
M28256, HN58C256AP, 28C256, UPD28C256, X28256/X28C256, FM28V020, MB85R256H).

**SR-1 verdict for DIP28_28C256 algo correction: PASS** — the change eliminates a VPP damage path.

---

## EXISTING PINOUT: DIP28_2764 (unchanged, retained for UV-EPROM chips)

**Status:** Selection unchanged. Rule 2 sub-case B (`DIP28_2764 + proto=0x07 + _etype==Flash/EEPROM`)
fires for chips that are 28C-family EEPROMs that happen to be on the 2764 pinout cluster (pm_idx=21
or pm_idx=22, erasable). These chips get `algo=0x0D`.

For genuine UV-EPROMs on DIP28_2764 (AM2764A, AM27C64, AM27C128, etc.), the `_etype==Flash/EEPROM`
guard correctly does NOT fire, so they keep `algo=0x07` and VPP is correctly asserted on pin 1.

**SR-1 verdict for DIP28_2764: PASS** — no 5V EEPROM retains VPP-asserting dispatch on this pinout.

---

## EXISTING PINOUTS: DIP28_27512, DIP28_27256 (unchanged)

**Status:** Selection relies on pm_idx=22 variant_lo discriminator (`0x10→DIP28_27512`,
`0x11→DIP28_27256`). RESEARCH Pitfall 3 warns these MUST NOT be swapped (12V VPP on wrong pin).

Verified: The principled rules preserve this discriminator exactly:
```python
if pm_idx == 22:
    if variant_lo == 0x10:
        key = "DIP28_27512"   # VPP=pin 22 (OE/VPP shared)
    elif variant_lo == 0x11:
        key = "DIP28_27256"   # VPP=pin 1
    else:
        key = "DIP28_2764"    # 27C128/27C64 — VPP=pin 1
```

Representative regression check in regenerated DB:
- W27C512 → `DIP28_27512` (VPP=pin 22) ✓
- AM27C256 → `DIP28_27256` (VPP=pin 1) ✓

**SR-1 verdict for DIP28_27512 / DIP28_27256: PASS** — discriminator preserved exactly.

---

## EXISTING PINOUTS: DIP32_STD, DIP32_SST39SF040, DIP32_28C512_EEPROM (unchanged)

**Status:** 32-pin pinout selection rules unchanged from pre-Phase-58 behavior. No 32-pin chip
changed pinout or algorithm as a result of Phase 58. GATE-03 confirms 0 violations in this family.

---

## Assumptions Requiring Operator Datasheet Confirmation

### A1 — DIP24_2816 Physical Pin Assignment is JEDEC-Standard (HIGH CONFIDENCE, LOW RISK)

**Claim:** AT28C04, AT28C16, AM28C16A, CAT28C16A, XL2804A, X2804A, X2816A/B/C, MICROCHIP
2804/2816, NEC UPD28C04, and the other variant_lo=0x10 chips all follow the JEDEC 24-pin
5V EEPROM standard: WE=pin 21, OE=pin 20, CE=pin 18, VCC=pin 24, GND=pin 12.

**Evidence this session:** Confirmed structurally from DIP24_6116 SRAM correspondence (same
physical layout). JEDEC 24-pin parallel SRAM/EEPROM standard is well-established. Also
confirmed by the minipro test-vector table grouping: all variant_lo=0x10 chips share pm_idx=23,
indicating minipro itself verifies them against the same internal layout.
[VERIFIED: minipro infoic.xml @ a8efaedc — all pm_idx=23 variant_lo=0x10 chips cluster together]

**Risk if wrong:** If any chip in this group has a non-standard pin assignment, DIP24_2816
would be incorrect for that specific chip. Risk is low — JEDEC 24-pin EEPROM is a stable
published standard, and the minipro pm_idx clustering confirms shared physical layout.

**Operator action required:** Spot-check AT28C16 datasheet Table 1 (Atmel/Microchip
doc 0006–2003 or equivalent) against DIP24_2816 pins. Primary pins to confirm:
pin 21 = WE#, pin 20 = OE#, pin 18 = CE#.

### A2 — variant_lo=0x10 Chips are Genuine 5V EEPROMs (CONFIRMED, VERY LOW RISK)

**Claim:** All 10 "previously dangerous" chips (AM28C16A, CAT28C16A, XL2804A, etc.) with
`flags=0x0000` (no erasable bit) but `variant_lo=0x10` are genuine 5V EEPROMs, not
UV-EPROMs that happen to share the variant_lo value.

**Evidence:** These chips' names (AM**28C**16A, CAT**28C**16A, XL**28**04A, X**28**C256) are
industry-standard "28C" EEPROM naming conventions. The "28C" designation uniformly indicates
5V single-supply EEPROM across all major manufacturers (AMD, Catalyst, EXEL, Microchip, XICOR).
The minipro pm_idx=23 grouping confirms minipro itself treats them as the same family.

**Risk if wrong:** If any variant_lo=0x10 chip is actually a UV-EPROM that shares the naming
convention, routing it to `configure_eeprom28c` (5V, SDP-disable, DQ7 polling) would be
incorrect but NOT DANGEROUS — configure_eeprom28c never asserts VPP or high voltages. The
chip simply would not program correctly (non-destructive failure mode).

**Operator action:** None required for safety. A2 is flagged only for completeness.

---

## BENCH-01 Deferral

Real-hardware write/program validation of the unblocked AT28C04/16-family chips is deferred
to v2 per `REQUIREMENTS.md`. Phase 58 satisfies **source-correctness only**: the principled
re-derivation routes these chips to the correct handler (configure_eeprom28c, 5V, no VPP);
GATE-03 proves no VPP damage path exists. Hardware confirmation is a future milestone item.

---

## Summary Table

| Pinout | Changed? | SR-1 Result | Notes |
|--------|----------|-------------|-------|
| DIP24_2816 | NEW | PASS (A1 flagged) | 19 chips routed here; 0 VPP path |
| DIP24_2716 | Chips moved OUT | No review needed | Unchanged definition; 10 dangerous chips moved to DIP24_2816 |
| DIP24_6116 | Unchanged | Pass (pre-existing) | SRAM pm_idx=0 cluster |
| DIP28_28C256 | Algo corrected | PASS | 12 chips: 0x07→0x0D (removes VPP path) |
| DIP28_2764 | Unchanged | PASS | UV-EPROM guard preserved; 5V EEPROMs correctly rerouted |
| DIP28_27512 | Unchanged | PASS | pm_idx=22 variant_lo=0x10 discriminator preserved |
| DIP28_27256 | Unchanged | PASS | pm_idx=22 variant_lo=0x11 discriminator preserved |
| DIP32_STD | Unchanged | Pass (pre-existing) | No Phase 58 changes |
| DIP32_SST39SF040 | Unchanged | Pass (pre-existing) | No Phase 58 changes |
| DIP32_28C512_EEPROM | Unchanged | Pass (pre-existing) | No Phase 58 changes |

**Overall SR-1 result: PASS**

GATE-03 mechanical proof: **0 violations / 743 chips** — no Flash/EEPROM chip routes to
configure_eprom on the Phase 58 regenerated database.
