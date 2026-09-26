# Phase 81 SR-1 Safety Review — 2516 User-Override Entry

**Scope:** The hand-authored `~/.firestarter/database.json` entry for the Intel/TI 2516
(24-pin NMOS UV-EPROM, DIP24_2716 pinout, algorithm 0x0B).

**Standard:** SR-1 (Safety Review 1) — VPP-pin safety checklist.

**GATE-03 status:** Not applicable — user-override entries are not scanned by
`tools/check_dispatch.py` (which operates on the generated `chip_database.json` only).
This manual review is the compensating control for the bypassed automated gates.

**Reviewer:** Claude (Phase 81 executor, 2026-06-23)

**Chip background (GRAD-01 research):**
The Intel/TI 2516 is a 24-pin NMOS UV-erasable PROM, 2K×8 = 2048 bytes, introduced
circa 1977. It is the 2KB member of the 2716 family. VPP programming voltage is 25V
(Intel datasheet: TMS2516). It is pin-compatible with the 2716 (uses the same DIP24
socket layout); read-mode is identical to the 2716 (VPP held at VCC=5V, OE/CE asserted).

**GRAD-01 infoic.xml finding:** The 2516 is ABSENT from minipro's `infoic.xml`. The 28
hits for "2516" in infoic.xml are all "25160" SPI serial EEPROM parts (e.g. AT25160,
25160S, etc.) — NOT the parallel UV-EPROM 2516. This confirms the 2516 must be a
hand-authored user-override entry that bypasses `build_db.py`/`check_dispatch.py`/
`diff_db.py`.

**Override mechanism:** The entry uses `name: "2516"` (alongside `part_number: "2516"`)
under the `"INTEL"` manufacturer key. `EpromDatabase._merge_databases` routes this via
the add-new-item path (lines 244–246 of `database.py`) since "2516" does not match any
existing INTEL chip's `part_number`. The `skip_local_override=True` seam used by the
automated test suite makes this entry INVISIBLE to CI/CD.

**D-01 gate context:** This is the SOLE compensating control before Phase 83 writes
the irreplaceable 2516. The chip has no UV eraser available, so any write is permanent.
The operator MUST personally review and sign below before any bench session.

---

## SR-1 Item Legend

1. `vpp-pin` present and correct (positive check — DIP24_2716 IS a VPP-routing pinout)
2. `rw-pin` = correct (no WE# on 2516 — it uses PGM-style programming via CE/OE timing)
3. `oe-pin` correct (Output Enable)
4. `ce-pin` correct (Chip Enable)
5. `vcc-pin` and `gnd-pin` correct
6. Address bus pins — no overlap with VCC/GND/control
7. Data bus pins — no overlap
8. VPP-safety assertion (25V at the correct physical pin; genuinely 25V chip)
9. All DIP24 pins accounted for

---

## D-02 Checklist — Six Required Values

### Item 1: algorithm = 0x0B → routes to `configure_eprom`

**Datasheet basis:** Intel 2516 / TMS2516 uses the EPROM_LEGACY programming protocol
(25V VPP, CE/OE strobing, 500µs pulses). In the Firestarter firmware, algorithm 0x0B
routes to `configure_eprom` in `eprom.cpp` (the EPROM_LEGACY path). This is the same
path used by the M2716, M2732 family — correct for NMOS UV-EPROMs requiring 25V VPP.

**Entry value:** `"algorithm": 11` (decimal 11 = 0x0B hexadecimal)

**Wire decode from `firestarter info 2516`:**
```
Protocol: Legacy EPROM/EEPROM (ID: 0x0B)
  - Programming protocol for older 24-pin devices
  - Shares pins between OE/VPP so high voltage is common
  - Targets small capacity 2716/2732/28C04/16 era parts
```

**Result: PASS** — algorithm = 0x0B, routes to `configure_eprom`.

---

### Item 2: vpp_mv = 25000 ≤ RURP_VPP_CEILING_MV = 25000

**Datasheet basis:** Intel 2516 programming voltage VPP = 25V (TMS2516 datasheet table
"DC Programming Conditions": VPP = 25V ±1V). TI TMS2516 datasheet confirms the same.

**Entry value:** `"vpp_mv": 25000`

**Ceiling check:** `RURP_VPP_CEILING_MV = 25000` (in `firestarter_app/tools/build_db.py`
line 117, raised from 22000 in Phase 79). The 2516's 25000 is AT the ceiling — not over.
Over-ceiling entries are rejected by `build_db.py`; this entry bypasses build_db, so the
manual check is mandatory.

**Wire decode from `firestarter info 2516`:**
```
VPP: 25.0v
```

**Result: PASS** — vpp_mv = 25000, at the ceiling (not over). Phase 79 explicitly raised
the ceiling to 25000 to permit NMOS 25V graduation.

---

### Item 3: electrical.type = "UV-EPROM" → FLAG_CAN_ERASE NOT set

**Datasheet basis:** The 2516 is a UV-erasable PROM. It requires ultraviolet light for
erasure; there is no electrical erase path. No operator UV eraser is available.

**Entry value:** `"type": "UV-EPROM"`

**FLAG_CAN_ERASE check (0x02 bit):** From `database.py` `convert_to_programmer`, the
`FLAG_CAN_ERASE` flag (0x02) is set ONLY for `electrical.type in ("EEPROM", "Flash/EEPROM")`.
UV-EPROM does NOT qualify → flag is NOT set.

**Python verification:**
```python
from firestarter.database import EpromDatabase
db = EpromDatabase(skip_local_override=False)
e = db.get_eprom('2516')
o = db.convert_to_programmer(e)
print(o['flags'] & 0x02)  # → 0  (FLAG_CAN_ERASE NOT set)
```
Output: `0`

**Wire decode from `firestarter info 2516`:**
```
Type:               UV-EPROM
Can be erased:      no (UV erase only)
Flags: 0x00000000
```

**Result: PASS** — UV-EPROM type, FLAG_CAN_ERASE = 0. The auto-erase path will NOT fire.

---

### Item 4: pinout = DIP24_2716 → VPP=pin 21, CE=pin 18, OE=pin 20, VCC=pin 24, GND=pin 12

**Datasheet basis (Intel 2516 / TMS2516):**
- Pin 21: VPP (25V programming voltage) — confirmed from 2516 datasheet pinout diagram.
  The 2516 uses the identical DIP24 pin assignment as the 2716/2732 family.
- Pin 18: CE# (Chip Enable, active low)
- Pin 20: OE# (Output Enable, active low)
- Pin 24: VCC (5V)
- Pin 12: GND

**pinouts.json DIP24_2716 entry (verbatim):**
```json
"DIP24_2716": {
    "name": "JEDEC 2716 (2KB)",
    "pins": {
        "vcc-pin": [24], "gnd-pin": [12], "vpp-pin": [21],
        "VCC_READ": 5.0, "VCC_PROG": 25.0,
        "address-bus-pins": [8, 7, 6, 5, 4, 3, 2, 1, 23, 22, 19],
        "data-bus-pins": [9, 10, 11, 13, 14, 15, 16, 17],
        "ce-pin": [18], "oe-pin": [20],
        "static-high-pins": [24]
    }
}
```

**vpp-pin verification:** `vpp-pin = [21]` — VPP routes to DIP24 pin 21. Per the 2516
datasheet, pin 21 is VPP (25V programming). This is the critical pin: if the chip is
ever seated in the ZIF socket during a WRITE, 25V will appear on pin 21. The datasheet
confirms this is correct.

**VCC_PROG = 25.0:** The `DIP24_2716` pinout's `VCC_PROG = 25.0` confirms the expected
programming voltage is 25V, consistent with `vpp_mv = 25000`.

**Wire decode from `firestarter info 2516`:**
```
       24-DIP package
        -----v-----
  A7  -|  1     24 |- VCC   
  A6  -|  2     23 |- A8    
  A5  -|  3     22 |- A9    
  A4  -|  4     21 |- VPP   
  A3  -|  5     20 |- OE    
  A2  -|  6     19 |- A10   
  A1  -|  7     18 |- CE    
  A0  -|  8     17 |- D7    
  D0  -|  9     16 |- D6    
  D1  -| 10     15 |- D5    
  D2  -| 11     14 |- D4    
  GND -| 12     13 |- D3    
        -----------
```

**Pin verification (against DIP24_2716 pinouts.json):**

| Pin | pinouts.json | `firestarter info` | Datasheet | Match? |
|-----|--------------|--------------------|-----------|--------|
| 21  | vpp-pin      | VPP                | VPP (25V) | PASS   |
| 18  | ce-pin       | CE                 | CE#       | PASS   |
| 20  | oe-pin       | OE                 | OE#       | PASS   |
| 24  | vcc-pin      | VCC                | VCC (5V)  | PASS   |
| 12  | gnd-pin      | GND                | GND       | PASS   |

**Result: PASS** — DIP24_2716 exists in pinouts.json, vpp-pin = [21] per datasheet.

---

### Item 5: support_status = "supported" → chip passes host guard

**Basis:** `chip_resolver.resolve_chip` (Phase 39 DATA-01) checks `support_status ==
"supported"` before returning any chip config. If `support_status` is anything else
(e.g., "adapter-required", "protocol-not-implemented"), the chip is refused at the
host level before any wire JSON is sent to the firmware.

**Entry value:** `"support_status": "supported"`

**Wire decode from `firestarter info 2516`:** (no "not supported" error — command exits 0)

**Result: PASS** — support_status = "supported". The 2516 will pass the host guard.

---

### Item 6: size_bytes = 2048 → 2KB chip, address space A0-A10

**Datasheet basis:** The Intel 2516 is a 2K×8-bit ROM (2048 bytes = 0x800). 11 address
lines A0-A10. The part name "2516" explicitly encodes "25" (EPROM family) and "16" = 16K
bits = 2K bytes.

**Entry value:** `"size_bytes": 2048`

**Wire decode from `firestarter info 2516`:**
```
Memory size:        0x800
```
(0x800 hex = 2048 decimal)

**Address bus check:** DIP24_2716 uses 11 address pins (A0-A10 at pins 8,7,6,5,4,3,2,1,23,22,19).
11 address bits → 2^11 = 2048 addresses. Consistent with size_bytes = 2048.

**Result: PASS** — size_bytes = 2048, consistent with datasheet and address bus.

---

## `firestarter info 2516` Full Transcript (Decode Evidence)

Captured with `~/.firestarter/database.json` installed (2026-06-23):

```
Eprom Info          
Name:               2516
Manufacturer:       INTEL
Number of pins:     24
Memory size         0x800
Type:               UV-EPROM
Can be erased:      no (UV erase only)
VCC:                5.0v
VPP:                25.0v
Chip ID:            -
Pulse delay:        500µS

       24-DIP package
        -----v-----
  A7  -|  1     24 |- VCC   
  A6  -|  2     23 |- A8    
  A5  -|  3     22 |- A9    
  A4  -|  4     21 |- VPP   
  A3  -|  5     20 |- OE    
  A2  -|  6     19 |- A10   
  A1  -|  7     18 |- CE    
  A0  -|  8     17 |- D7    
  D0  -|  9     16 |- D6    
  D1  -| 10     15 |- D5    
  D2  -| 11     14 |- D4    
  GND -| 12     13 |- D3    
        -----------

Jumper config (Rev 0.1 & 1.0):
  JP1: (● ●)●  (5V, A13 = VCC)
  JP2:  ● ● ●  (5V, A17 = NA)
  JP3:  ● ● ●  (28pin, 32pin = NA)

Jumper config (Rev 2.0 & 2.1):
  JP4:  N/A    (28pin, 32pin = NA)

Protocol: Legacy EPROM/EEPROM (ID: 0x0B)
  - Programming protocol for older 24-pin devices
  - Shares pins between OE/VPP so high voltage is common
  - Targets small capacity 2716/2732/28C04/16 era parts

Flags: 0x00000000
```

---

## SR-1 Pin Count Verification (Item 9)

Full DIP24_2716 pin accounting for the 2516:

| Pin Group      | Pins                                      | Count |
|----------------|-------------------------------------------|-------|
| Address bus    | 1,2,3,4,5,6,7,8,19,22,23 (A0-A10)        | 11    |
| Data bus       | 9,10,11,13,14,15,16,17 (D0-D7)            | 8     |
| CE#            | 18                                        | 1     |
| OE#            | 20                                        | 1     |
| VPP            | 21                                        | 1     |
| VCC            | 24                                        | 1     |
| GND            | 12                                        | 1     |
| **Total**      |                                           | **24**|

All 24 pins assigned. No pin double-counted. No pin unassigned.

**Result: PASS** — all 24 DIP pins accounted for.

---

## Safety Analysis: Highest-Risk Field (Pitfall 8)

Per `.planning/research/PITFALLS.md` Pitfall 8, the highest-risk field in a user-override
entry is `vpp_mv`. If it were set to 12000 instead of 25000:

- The firmware would program at 12V (below the 2516's 25V threshold).
- The chip would not program (12V is insufficient for NMOS VPP).
- No hardware damage — but a false "programmed" result (chip contents unchanged).
- Critically: because 12V < 23.75V (95% of 12000 = 11400, no warning threshold exceeded
  at 12V in the context of vpp_mv=12000).

**Verification:** `vpp_mv = 25000` is confirmed in this review (Item 2). The `firestarter
info` transcript shows `VPP: 25.0v`. No ambiguity.

---

## Summary Table

| Item | D-02 Value | Actual Value | Result |
|------|------------|--------------|--------|
| 1: algorithm | 0x0B → `configure_eprom` | `algorithm=11` (0x0B), Protocol ID 0x0B | **PASS** |
| 2: vpp_mv | 25000 ≤ ceiling 25000 | `vpp_mv=25000`, VPP: 25.0v | **PASS** |
| 3: electrical.type | UV-EPROM → no FLAG_CAN_ERASE | `type="UV-EPROM"`, flags=0x0, not erasable | **PASS** |
| 4: pinout DIP24_2716 | vpp-pin=[21], ce=[18], oe=[20], vcc=[24], gnd=[12] | All confirmed in pinouts.json + info transcript | **PASS** |
| 5: support_status | "supported" | `support_status="supported"` | **PASS** |
| 6: size_bytes | 2048 | `size_bytes=2048`, 0x800 | **PASS** |
| SR-1 pin count | 24 pins | 24 pins accounted for | **PASS** |

**Overall SR-1 result: PASS**

All 6 D-02 values verified against TMS2516/Intel 2516 datasheet and confirmed in
`firestarter info 2516` decode transcript. The entry is safe to use for Phase 81 reads
(non-destructive) and, subject to Phase 83 VPE rail measurement, for NMOS best-effort
write.

---

## Notes on Phase 81 Read Safety

Reading the 2516 with `firestarter read` does NOT apply VPP. The `configure_eprom` path
(0x0B) applies VPP only during the write sequence. A read uses CE# + OE# at 5V VCC with
VPP held at VCC (5V), which is correct read-mode per the 2516 datasheet. The 11th chip
in the Phase 81 sweep is therefore non-destructive.

---

## Operator Sign-Off (D-01 Human Gate)

The operator must personally verify the 6 D-02 items in this review before any bench
session that uses the 2516. This gate is blocking-human and non-auto-approvable because
the chip is irreplaceable (no UV eraser available).

**Steps for operator sign-off:**
1. Read each of the 6 D-02 items above end to end.
2. Confirm `vpp_mv = 25000` (NOT 12000) — this is Pitfall 8, the highest-risk field.
3. Confirm `electrical.type = UV-EPROM` → FLAG_CAN_ERASE is NOT set.
4. Run `firestarter info 2516` yourself and verify the output matches the transcript.
5. Confirm VPP = pin 21 in the 24-DIP diagram (fourth pin from top-right).
6. Fill in the sign-off line below.

**Operator sign-off:** [x] Approved — Henrik / 2026-06-23

*Phase 81 executor: Claude (Sonnet 4.6), 2026-06-23*
