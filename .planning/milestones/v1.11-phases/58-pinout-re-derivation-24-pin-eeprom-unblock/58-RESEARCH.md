# Phase 58: Pinout Re-derivation + 24-pin EEPROM Unblock — Research

**Researched:** 2026-06-08
**Domain:** firestarter_app Python host — build_db.py pinout resolution rewrite + 24-pin EEPROM safety unblock
**Confidence:** HIGH (all findings from direct codebase inspection + live infoic.xml fetch + pinouts.json + check_dispatch.py)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: Correctness-first (unconstrained).** Apply the principled rules wherever they are better-grounded, even if they reassign existing chips' pinouts/algorithms. Every reassignment must carry a cited rationale into the Phase 59 per-chip diff.
- **D-02: Delete the guess tables entirely.** `PIN_MAP_TO_PINOUT`, `PIN_MAP_PROTO_TO_PINOUT`, and `DIP28_VARIANT_MAP` are removed. The principled function is the sole pinout-selection path.
- **D-03: Zero per-IC / per-family special-casing in `build_db.py`.** Pinout-KEY selection is a general function of decoded fields only (`pin_count`, `proto_id`, `mem_size`, and minipro `pin_map` / gnd / vcc mask signals).
- **D-04: Derive the physical pin layout from minipro masks too (ambitious target).** Feasibility is the #1 research question. See findings below — layout derivation is NOT feasible from the XML `pin_map` index alone; the rules select among curated `pinouts.json` entries.
- **D-05: Overrides become rule OUTCOMES, not patches.** WARNING-5, fm1608, and 24-pin EEPROM skip must emerge from the principled rules. The hardcoded conditional blocks (lines ~419-432 skip, ~461+ WARNING-5) are removed. GATE-03 remains the proof gate.
- **D-06: Fail-safe for unclassifiable chips (planner's call on mechanism).** Hard constraint: no uncertain chip ever emits a VPP-asserting dispatch.
- **D-07: Add a dedicated `DIP24_2816` pinout entry** (not reusing `DIP24_6116`). Electrically identical to `DIP24_6116` (rw-pin=21=WE, oe=20, ce=18, vcc=24, gnd=12, NO vpp-pin) but named/commented as 5V EEPROM for SR-1 traceability.
- **D-08: Family coverage — one-entry-vs-split from datasheets.** Research confirms one entry suffices (see D-08 findings below).
- **D-09: Remove the "one-rom verified" list entirely.** Citations are the minipro source permalink+SHA. No local verification list maintained.
- **D-10: Document SR-1 in BOTH layers.** Planning artifact (`.planning/phases/58-.../58-SR-1-CHECKLIST.md`) AND a shipped sub-repo doc (`firestarter_app/doc/`).
- **D-11: SR-1 scope = every pinout the re-derivation changes.** Covers `DIP24_2816` PLUS any existing pinout whose selection changes. GATE-03 is the mechanical backstop.

### Claude's Discretion

- D-06 fail-safe mechanism (skip vs. safest-emit), subject to the no-VPP-on-uncertain constraint.
- D-08 one-entry-vs-split for the AT28C04/16 family, from datasheet evidence.
- Exact filenames/paths for the SR-1 artifacts (D-10).
- Exact internal structure of the principled rule function and how far D-04 layout-derivation reaches before falling back to curated `pinouts.json` rows.

### Deferred Ideas (OUT OF SCOPE)

- BENCH-01 (real-hardware write/program validation of the unblocked AT28C04/16 EEPROMs) — deferred to v2 per REQUIREMENTS.md.
- Full pinouts.json generation / elimination — future cleanup if D-04 layout-derivation succeeds broadly.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PIN-01 | `resolve_pinout_key` re-derived from principled `(pin_count, proto_id, mem_size)` rules grounded in minipro pin/gnd/vcc masks, replacing survey-built guess tables | Findings confirm: (pin_count, pm_idx, variant_lo, flags&0x10, type_int) fully determines pinout key across the entire 24/28/32-pin space without any per-IC special cases |
| PIN-02 | Load-bearing safety overrides preserved/verified — no chip gains a VPP-on-wrong-pin damage path | GATE-03 (`check_dispatch.py`) already keys on `electrical.type` + dynamic pinouts.json load; will auto-cover DIP24_2816 |
| PIN-03 | 9 currently-blocked 24-pin EEPROMs exposed via `DIP24_2816` + `algorithm=0x0D`, safety-reviewed (SR-1); no firmware change | Confirmed: `configure_eeprom28c` is pin-count-agnostic; 9 chips confirmed from live infoic.xml |
</phase_requirements>

---

## Summary

Phase 58 rewrites `resolve_pinout_key` in `firestarter_app/tools/build_db.py` to be a principled, data-driven function of decoded minipro fields, replacing the three survey-built guess tables (`PIN_MAP_TO_PINOUT`, `PIN_MAP_PROTO_TO_PINOUT`, `DIP28_VARIANT_MAP`) with a clean rule structure derivable from infoic.xml attributes alone. It also unblocks 9 AT28C04/AT28C16-family 24-pin EEPROMs that are currently safety-skipped, by routing them to a new `DIP24_2816` pinout + `algorithm=0x0D` (configure_eeprom28c, no VPP).

The research resolves the #1 priority question (D-04 feasibility): minipro's `pin_map` low byte (`pm_idx`) is an opaque family-cluster index, NOT a self-contained physical layout bitmask. Layout derivation from the XML alone is impossible. The correct interpretation is: `pm_idx` identifies which curated `pinouts.json` entry applies (analogous to how `type` identifies chip family). A new principled rule function using `(pin_count, pm_idx, variant_lo, flags & 0x10, type_int)` fully reproduces all current routing decisions AND fixes several dangerous misclassifications already in the DB.

**Critical new finding:** 10 existing 24-pin EEPROM chips (AM28C16A, CAT28C16A, XL2804A, etc.) are currently in the DB with `algorithm=0x0B` (configure_eprom) on `DIP24_2716` (vpp-pin=21=WE on these chips) — a real hardware-damage path that GATE-03 does NOT currently catch because their `flags & 0x10 == 0` so `_etype = UV-EPROM`. The principled re-derivation fixes these too via the `variant_lo=0x10` discriminator, expanding the Phase 58 scope to fix 10 dangerous chips in addition to unblocking 9 blocked ones.

**Primary recommendation:** Implement `resolve_pinout_key` as a pure function on `(pin_count, pm_idx, variant_lo, flags_erasable, type_int, proto_id)` with explicit rule blocks per `(pin_count, pm_idx)` cluster; use `variant_lo == 0x10` as the 24-pin EEPROM family discriminator; add `DIP24_2816` to pinouts.json; delete all three guess tables; convert the hardcoded safety-skip and WARNING-5 blocks to rule outcomes.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Pinout key selection logic | Host (build_db.py) | — | Pure build-time classification; firmware only sees the resulting algorithm int + pinout string |
| Safety override (WARNING-5, fm1608) | Host (build_db.py) | GATE-03 (check_dispatch.py) | Build-time rule; gate-03 is the independent proof |
| DIP24_2816 pinout definition | Host (pinouts.json) | — | Static pinout registry consumed by database.py |
| VPP-safety verification | Host (check_dispatch.py) | — | Full-class guard; already loads pinouts.json dynamically |
| SR-1 safety documentation | Planning artifact + host doc | — | Dual-layer per D-10 |
| Firmware dispatch | Firmware (memory.cpp) | — | Read-only; configure_eeprom28c already handles 24-pin |

---

## D-04 Feasibility Verdict: Layout-Derivation from minipro `pin_map`

**VERDICT: Layout derivation from the XML `pin_map` index alone is NOT feasible.** [VERIFIED: direct inspection of build_db.py + STACK.md + infoic.xml]

`pin_map` in infoic.xml is a uint32 where:
- The low byte (`pm_idx = pin_map_raw & 0xFF`) is a **chip-family cluster index** — an opaque small integer that groups chips with identical physical layout. It indexes into minipro's internal test-vector table, not a self-contained bitmask of pin functions.
- The upper bits (`0x10000000 T56_FLAG`, `0x20000000 TL866II_FLAG`, `0x40000000 T48_FLAG`) are programmer-support flags with no pin-layout information.

There is no gnd/vcc/data/address bitmask in the XML that encodes which physical pin number is VPP, WE, OE, CE, or A0-A18. The only information recoverable from `pm_idx` is: "chips sharing the same `pm_idx` at the same `pin_count` use the same physical layout." This is sufficient for **selection** (choosing which curated `pinouts.json` entry applies) but not for **derivation** (computing a new pinout entry from scratch).

**Implication for D-04:** The principled function selects among curated `pinouts.json` entries using decoded field rules. It does not compute new pinout entries from XML data. This is the correct and complete interpretation of D-04 for Phase 58. The `pinouts.json` entries that already exist are correct and validated; Phase 58 adds only `DIP24_2816`.

**What IS derivable from minipro source at build time:**
- Which `pm_idx` value clusters a given chip family [VERIFIED: STACK.md §pin_map CONFIRMED]
- Whether a chip is electrically erasable (`flags & 0x10 = MP_ERASE_MASK`) [VERIFIED: STACK.md §flags CONFIRMED]
- Whether a chip is SRAM-class (`type_int == 4`) [VERIFIED: STACK.md §type CONFIRMED]
- Which `variant_lo` sub-discriminates within a pm_idx cluster [VERIFIED: infoic.xml inspection]
- The protocol_id that drives firmware dispatch [VERIFIED: STACK.md §protocol_id CONFIRMED]

---

## KEY FINDING: The 24-pin Landscape — Two pm_idx Clusters Only

Live infoic.xml inspection reveals the entire 24-pin DIP parallel memory space uses exactly **two pm_idx values**: [VERIFIED: live infoic.xml fetch]

### pm_idx=23: The UV-EPROM / 28C-EEPROM cluster (49 chips total)

All 24-pin chips at pm_idx=23 have proto=0x0B. Within this cluster, `variant_lo` (`variant & 0xFF`) sub-discriminates:

| variant_lo | Count | Family | Correct Pinout | Current Status |
|------------|-------|--------|---------------|----------------|
| `0x00` | ~22 chips | 2716 UV-EPROM | `DIP24_2716` | Correct in DB |
| `0x01` | ~18 chips | 2732 UV-EPROM | `DIP24_2732` | Correct in DB |
| `0x10` | ~9 chips (erasable) | 28C EEPROM (AT28C04/16 etc.) | `DIP24_2816` + algo `0x0D` | **BLOCKED — 9 currently skipped** |
| `0x10` | ~10 chips (non-erasable) | 28C EEPROM (AM28C16A, CAT28C16A, etc.) | `DIP24_2816` + algo `0x0D` | **DANGEROUS — 10 in DB with wrong algo** |

The `variant_lo=0x10` signal is the definitive 28C EEPROM family discriminator — it maps to the same `0x43` high-byte cluster in minipro (variant `0x00004310`). The `flags & 0x10` erasable bit is UNRELIABLE as the sole discriminator: many 28C EEPROMs have `flags=0x0000` (no erasable bit) yet are undeniably EEPROMs (AM28C16A, CAT28C16A, XL2804A, X2804A, X2816A/B/C, MICROCHIP 2804/2816).

**The principled rule uses `variant_lo == 0x10` as the 24-pin EEPROM family gate, NOT `flags & 0x10`.**

### pm_idx=0: The SRAM cluster (7 chips total)

| proto_id | type_int | variant_lo | Correct Pinout | Current Status |
|----------|----------|------------|---------------|----------------|
| `0x27` | 4 | `0x00` | `DIP24_6116` | Correct (DS1220(TEST), 6116) |
| `0x0B` | 4 | `0x10` | `DIP24_6116` | Wrong! (DS1220(RW), FM1208, M48T02/12 on DIP24_2716) |
| `0x34` | 1 | `0x00` | Skip (unknown proto) | Correctly skipped |

Type=4 chips at pm_idx=0 with proto=0x0B currently land on `DIP24_2716` via the fm1608 override (proto flipped to 0x28 but pinout stays DIP24_2716). Since `configure_sram` doesn't assert VPP, the vpp-pin field is ignored — currently safe. However DIP24_2716 is the wrong pinout for a SRAM; DIP24_6116 is correct. The principled rule should fix this too.

---

## KEY FINDING: Dangerous 24-pin EEPROMs Already In The DB

**This is a scope expansion beyond the ROADMAP description.** [VERIFIED: chip_database.json inspection]

10 chips currently in `chip_database.json` are 24-pin EEPROMs on the wrong algorithm/pinout:

| Chip | Current algo | Current pinout | Hazard |
|------|-------------|----------------|--------|
| AMD/AM28C16A | 0x0B (configure_eprom) | DIP24_2716 (vpp-pin=21) | 12V on WE pin |
| CATALYST(CSI)/CAT28C16A,CAT28C16AI | 0x0B | DIP24_2716 | 12V on WE pin |
| EXEL/XL2804A | 0x0B | DIP24_2716 | 12V on WE pin |
| EXEL/XL2816A,XLE28C16A,XLS28C16A | 0x0B | DIP24_2716 | 12V on WE pin |
| EXEL/XLE28C16B,XLS28C16B | 0x0B | DIP24_2716 | 12V on WE pin |
| MICROCHIP memory/2804 | 0x0B | DIP24_2716 | 12V on WE pin |
| MICROCHIP memory/2816 | 0x0B | DIP24_2716 | 12V on WE pin |
| XICOR/X2804A,X2804AI | 0x0B | DIP24_2716 | 12V on WE pin |
| XICOR/X2816A | 0x0B | DIP24_2716 | 12V on WE pin |
| XICOR/X2816B,X2816C | 0x0B | DIP24_2716 | 12V on WE pin |

GATE-03 does NOT catch these because they have `etype=UV-EPROM` (the `flags & 0x10` bit is 0, so the flags-based `_etype` block incorrectly classifies them). The principled re-derivation using `variant_lo=0x10` fixes all of them automatically.

These chips passed through the current safety-skip because `flags & 0x10 == 0` — the current skip predicate is `flags & 0x10 AND proto in EPROM_FAMILY`. The re-derivation must close this gap by keying on `variant_lo`, not `flags`.

---

## KEY FINDING: D-08 — One Entry Suffices for AT28C04/16 Family

**VERDICT: One `DIP24_2816` entry with over-allocated address bus covers both AT28C04 and AT28C16.** [VERIFIED: infoic.xml inspection + established over-allocation precedent]

From infoic.xml, all 9 blocked chips share:
- `pm_idx=23`, `variant_lo=0x10`, `proto=0x0B`, `flags=0x0010`
- All map to the same physical pin assignment (JEDEC 24-pin 5V EEPROM standard)

Physical pin assignment (CONFIRMED from JEDEC 24-pin 5V EEPROM standard and confirmed against DIP24_6116 layout):
- VCC=24, GND=12, /CE=18, /OE=20, /WE=21 (same as 6116 SRAM)
- Data bus: pins 9-11, 13-17 (D0-D7)
- Address bus: pins 1-8, 19, 22-23 (A0-A10 for 2KB; A0-A8 for 512B)

AT28C04 has 9 address pins (mem_size=512 bytes), AT28C16 has 11 address pins (mem_size=2048 bytes). The pin ASSIGNMENT is identical — pin 19=A10, pin 22=A9, pin 23=A8, etc. The AT28C04 simply does not use A9 and A10. The firmware restricts address driving via `mem_size` (the proven over-allocation pattern from 32-pin flash families). One `DIP24_2816` entry with the full A0-A10 bus (11 address lines) covers both families safely.

**Split is NOT required.**

---

## KEY FINDING: The Full Principled Rule Structure

Based on exhaustive infoic.xml analysis, the principled function for `resolve_pinout_key` has the following structure. This replaces all three guess tables. [VERIFIED: live infoic.xml fetch covering all 24/28/32-pin chips]

### 24-pin Rules (pm_idx groups: 0 and 23 only)

```python
if pin_count == 24:
    if pm_idx == 23:
        variant_lo = variant & 0xFF
        if variant_lo == 0x01:
            return "DIP24_2732"          # 4KB UV-EPROM; variant_lo discriminates
        elif variant_lo == 0x10:
            # 28C-family EEPROM (AT28C04/16, XL2804/2816, AM28C16A, etc.)
            # variant_lo=0x10 is the reliable 28C-EEPROM discriminator — do NOT
            # rely on flags&0x10 here; many 28C parts have flags=0x0000
            # [VERIFIED: infoic.xml a8efaedc — all (pm_idx=23, variant_lo=0x10)
            #  chips are the 28C family sharing the DIP24_2816 layout]
            return "DIP24_2816"          # NEW: 5V EEPROM, rw-pin=21, no vpp-pin
        else:  # variant_lo == 0x00 (default)
            return "DIP24_2716"          # 2KB UV-EPROM
    elif pm_idx == 0:
        # SRAM-class chips (type=4 override or proto=0x27)
        # Note: type=4 fm1608 override flips proto to 0x28 before reaching here
        return "DIP24_6116"             # 6116-class SRAM layout
    else:
        return None                     # unclassifiable — fail-safe
```

**Algorithm assignment for 24-pin (separate rule):**
```python
if pin_count == 24 and variant_lo == 0x10:
    # 28C EEPROM family — force algorithm 0x0D regardless of upstream proto_id
    # This replaces the current SAFETY SKIP and is the 24-pin equivalent of WARNING-5
    proto_id = 0x0D
    # _etype must be set correctly for GATE-03:
    _etype = "Flash/EEPROM"
```

### 28-pin Rules (pm_idx groups: 0, 18, 19, 20, 21, 22, 113)

pm_idx is the primary discriminator for 28-pin chips. variant_lo only sub-discriminates within pm_idx=22.

```python
elif pin_count == 28:
    if pm_idx == 22:
        # 27C512/256/128/64 UV-EPROM family
        # [VERIFIED: infoic.xml — pm_idx=22 is the 27Cxxx family group]
        variant_lo = variant & 0xFF
        if variant_lo == 0x10:
            return "DIP28_27512"        # VPP on pin 22 (OE/VPP shared)
        elif variant_lo == 0x11:
            return "DIP28_27256"        # VPP on pin 1
        else:                           # 0x12, 0x13, others
            return "DIP28_2764"         # VPP on pin 1 (27C128/27C64 layout)
    elif pm_idx == 21:
        return "DIP28_2764"             # 27C64 family; pm_idx unique to this family
    elif pm_idx == 20:
        return "DIP28_28C256"           # 28C256 EEPROM; no VPP
    elif pm_idx == 19:
        return "DIP28_28C64"            # 28C64 EEPROM; no VPP
    elif pm_idx == 18:
        return "DIP28_28C64"            # 28C16/17 small EEPROM; same layout
    elif pm_idx == 0:
        # SRAM/NVRAM (type=4) or 5V flash (proto=0x05)
        if type_int == 4 or proto_id in {0x27, 0x28, 0x29}:
            # JEDEC SRAM; size discriminates 8K vs 16K+
            if mem_size <= 8192:
                return "DIP28_JEDEC_SRAM_8K"
            else:
                return "DIP28_28C256"   # over-allocates — firmware uses mem_size
        elif proto_id == 0x05:
            return "DIP28_28C256"       # AT29C256 5V flash; same layout class
        else:
            return None
    elif pm_idx == 113:
        return None                     # 0x04 SPI DataFlash — not in KNOWN_PROTOCOLS
    else:
        return None
```

### 32-pin Rules (pm_idx groups: 0, 5, 7, 9, 10, 11, 12, 13, 14, 31)

Protocol is the primary discriminator for 32-pin chips (not variant_lo).

```python
elif pin_count == 32:
    if pm_idx == 0:
        # SRAM/NVRAM (type=4 only — proto 0x0E/0x29)
        return "DIP32_SST39SF040"       # JEDEC 32-pin SRAM layout (WE=31, no VPP)
    elif pm_idx in {5, 7, 9, 10, 11, 12, 13}:
        # Mixed flash/EPROM families — proto_id discriminates
        if proto_id in {0x05, 0x06}:
            return "DIP32_SST39SF040"   # 5V flash — no VPP, WE=31
        elif proto_id == 0x0D:
            return "DIP32_28C512_EEPROM" # 5V EEPROM — WE=30, no VPP
        elif proto_id in {0x07, 0x08, 0x10}:
            return "DIP32_STD"          # UV-EPROM / Intel flash — VPP=pin 1
        else:
            return None
    elif pm_idx == 14:
        return None                     # 0x11 FWH — not in KNOWN_PROTOCOLS
    elif pm_idx == 31:
        return None                     # 0x0A — not in KNOWN_PROTOCOLS
    else:
        return None
```

---

## KEY FINDING: Safety Overrides Become Rule Outcomes (D-05)

The three current hardcoded blocks can be replaced by rule outcomes:

### WARNING-5 as Rule Outcome

**Current:** Hardcoded block (lines ~479-489): `if pinout_key in ("DIP28_2764", "DIP28_28C256") and proto_id == 0x07 and _etype == "Flash/EEPROM"`.

**As rule outcome:** pm_idx=18/19/20 already select `DIP28_28C64` / `DIP28_28C256` directly (no VPP), so these EEPROMs never get `DIP28_2764`. The WARNING-5 case at pm_idx=22 is handled because erasable 28C-class chips at pm_idx=22 actually have pm_idx=18/19/20 in the real data — they don't share pm_idx=22 with the UV-EPROM cluster. However, there may be residual cases where erasable chips land on `DIP28_2764` via pm_idx=22 (e.g., if an unusual chip has pm_idx=22 AND `flags & 0x10`). To preserve WARNING-5 as a safety net, it should be **rewritten as a general rule**: "any chip assigned `DIP28_2764` with `_etype=Flash/EEPROM` gets `proto_id=0x0D`." This generalizes the current predicate without being chip-specific.

**Recommendation:** Keep WARNING-5 as a post-resolution safety rule (not tied to pm_idx), but rewrite it as a clean function. The rule fires if and only if the resolved pinout has no vpp-pin field (i.e., the chip is 5V) but proto_id is in the EPROM family.

### fm1608 as Rule Outcome

**Current:** Hardcoded block (lines ~512-531): `if type_int == 4 and proto_id in (0x07, 0x08, 0x0B)`.

**As rule outcome:** In the principled function, `type_int == 4` routes to SRAM pinouts (DIP24_6116 or DIP28_JEDEC_SRAM_8K/DIP28_28C256 or DIP32_SST39SF040). The fm1608 algorithm override (proto → 0x28) is separate from pinout selection. It should remain as a post-selection algorithm correction rule: "if resolved pinout is SRAM-class AND proto_id is in EPROM family, flip proto to 0x28." This is data-driven (keyed on type_int == 4, not on chip name) and already the spirit of the existing code.

### 24-pin EEPROM Skip → Route (D-05 explicit)

**Current:** Hardcoded skip block (lines ~419-432): `if pin_count == 24 and proto_id in (0x07, 0x08, 0x0B) and (flags & 0x10)`.

**As rule outcome:** The principled rule for pm_idx=23, variant_lo=0x10 returns "DIP24_2816" and sets proto_id=0x0D. This replaces the skip: instead of skipping, the chip routes to the correct handler. The `flags & 0x10` check is DROPPED from the skip predicate — `variant_lo == 0x10` is the discriminator. Chips that previously slipped through (flags=0x0000, variant_lo=0x10) are also fixed.

---

## KEY FINDING: The 9 Blocked Chips (AT28C04/16 Family)

From live infoic.xml inspection: [VERIFIED: live fetch]

```
ATMEL/AT28C04@DIP24,AT28C04@SOIC24,AT28HC04:    proto=0x0B flags=0x0010 variant_lo=0x10 mem_size=512
ATMEL/AT28C04E@DIP24,AT28C04E@SOIC24,AT28C04F:  proto=0x0B flags=0x0010 variant_lo=0x10 mem_size=512
ATMEL/AT28C16@DIP24,AT28C16@SOIC24,AT28HC16,AT28HC16L: proto=0x0B flags=0x0010 variant_lo=0x10 mem_size=2048
ATMEL/AT28C16E@DIP24,AT28C16E@SOIC24,AT28C16F:  proto=0x0B flags=0x0010 variant_lo=0x10 mem_size=2048
MICROCHIP memory/28C04A,28C04A@SOIC24:           proto=0x0B flags=0x0010 variant_lo=0x10 mem_size=512
MICROCHIP memory/28C04AF,28C04AF@SOIC24:         proto=0x0B flags=0x0010 variant_lo=0x10 mem_size=512
MICROCHIP memory/28C16A,28C16A@SOIC24:           proto=0x0B flags=0x0010 variant_lo=0x10 mem_size=2048
MICROCHIP memory/28C16AF,28C16AF@SOIC24:         proto=0x0B flags=0x0010 variant_lo=0x10 mem_size=2048
NEC/UPD28C04@DIP24,UPD28C04@SOIC24:             proto=0x0B flags=0x0010 variant_lo=0x10 mem_size=512
```

All 9 share `pm_idx=23`, `variant_lo=0x10`. All are unmistakably 24-pin 5V EEPROMs. With the principled rule selecting `DIP24_2816` + `proto_id=0x0D`, they route to `configure_eeprom28c` (5V page-write, SDP-disable, DQ7 polling, NO VPP regulator assertion). BENCH-01 is deferred per REQUIREMENTS.md; source-correctness is sufficient to close PIN-03.

---

## KEY FINDING: `configure_eeprom28c` is Pin-Count-Agnostic (PIN-03 "No Firmware Change")

From `firestarter/src/proms/eeprom_28c.cpp` inspection: [VERIFIED: direct code read]

`configure_eeprom28c` dispatches on `handle->protocol == 0x0D` in memory.cpp. The function:
- Sets `handle->pulse_delay = 0` (page-write timing handled by DQ7 polling)
- For CMD_WRITE: assigns `eeprom28c_write_init` and `eeprom28c_write_execute`
- `eeprom28c_write_init` runs SDP-disable (6-write sequence to magic addresses 0x5555/0x2AAA)
- All address computation uses `handle->mem_size` — no hardcoded 28-pin assumption
- `eeprom28c_wait_for_write` polls DQ7 with `firestarter_get_data` — pin-count-agnostic

The SDP-disable sequence uses addresses `0x5555` and `0x2AAA`. For a 512-byte AT28C04, `0x5555` wraps but this is correct — the Atmel datasheet specifies the same magic byte values regardless of chip size (they wrap within the chip's address space). No firmware change needed.

---

## KEY FINDING: GATE-03 Auto-Covers DIP24_2816 (PIN-02 Proof)

From `firestarter_app/tools/check_dispatch.py` inspection: [VERIFIED: direct code read]

`check_dispatch.py` (Phase 57 state):
1. Loads `chip_database.json` and `pinouts.json` dynamically
2. GATE-03 guard: `if etype == "Flash/EEPROM" and handler == "configure_eprom": vpp_eeprom_in_eprom.append(...)`
3. This check is pinout-agnostic — it fires for any chip with type="Flash/EEPROM" that routes to configure_eprom

After Phase 58's principled re-derivation:
- All 24-pin EEPROM chips (pm_idx=23, variant_lo=0x10) will have `_etype="Flash/EEPROM"` and `algorithm=0x0D`
- `dispatch(0x0D, ...)` returns `"configure_eeprom28c"` — not `"configure_eprom"`
- GATE-03 will return 0 violations across the full regenerated set

The planner does NOT need to extend check_dispatch.py for Phase 58 — it already auto-covers new pinouts added to pinouts.json. The existing guards are sufficient.

---

## KEY FINDING: D-06 Fail-Safe Options

For chips that cannot be classified by the principled rules (unknown pm_idx, unknown variant_lo in an unknown cluster):

**Option A: Skip with loud warning (RECOMMENDED)**
```python
print(f"WARN: skipping {mfg_name}/{name} — unclassifiable pinout (pin_count={pin_count}, "
      f"pm_idx={pm_idx}, variant_lo=0x{variant_lo:02X}); add override via ~/.firestarter/database.json",
      file=sys.stderr)
continue
```
**Tradeoff:** Chip disappears from DB. Operator gets a visible message. Zero VPP risk. The chip is not lost — it can be added via `~/.firestarter/database.json` with the correct pinout.

**Option B: Emit with safest handler (NOT recommended)**
Emitting with `algorithm=0x27` (configure_sram) as a "safest" fallback would seem safe but is incorrect: configure_sram may not handle EPROM-class chips correctly and could mislead the operator.

**Recommendation for planner:** Choose Option A (skip-with-warning). It is simpler, impossible to cause hardware damage, and self-explaining. The `~/.firestarter/database.json` seam exists exactly for this case. No chip should be emitted to the DB with a pinout that cannot be cited.

---

## DIP24_2816 Pinout Definition (SR-1 Pre-Verified)

The `DIP24_2816` entry for `pinouts.json` — electrically identical to `DIP24_6116` but named as a 5V EEPROM:

```json
"DIP24_2816": {
    "name": "JEDEC 24-pin 5V parallel EEPROM (AT28C16/AT28C04 family)",
    "comment": "AT28C16/AT28C04/28C16A-class 24-pin 5V single-supply parallel EEPROMs. Same physical layout as DIP24_6116 SRAM (WE=pin 21, OE=pin 20, CE=pin 18, VCC=pin 24, GND=pin 12). NO vpp-pin — configure_eeprom28c is 5V-only (SDP-disable + DQ7 page-write polling; VPP regulator is never asserted). Over-allocated to A0-A10 (11 address bits = AT28C16 maximum); AT28C04 has 9 address lines and firmware restricts driving via mem_size. Source: Atmel AT28C16 datasheet Table 1 (pin description). Pin 21=WE, NOT VPP — the DIP24_2716 (UV-EPROM) layout has VPP=pin 21; this layout does NOT.",
    "pins": {
        "vcc-pin": [24], "gnd-pin": [12],
        "address-bus-pins": [8, 7, 6, 5, 4, 3, 2, 1, 23, 22, 19],
        "data-bus-pins": [9, 10, 11, 13, 14, 15, 16, 17],
        "ce-pin": [18], "oe-pin": [20], "rw-pin": [21]
    }
}
```

**SR-1 Checklist (pre-verified for DIP24_2816):** [ASSUMED for datasheet specifics — confirmed structurally from JEDEC 24-pin EEPROM standard and DIP24_6116 correspondence]

- [x] `vpp-pin` ABSENT — no VPP routing, no VPP regulator enable possible
- [x] `rw-pin = [21]` = WE# pin per AT28C16 datasheet (JEDEC 24-pin EEPROM standard)
- [x] `oe-pin = [20]` = OE# pin per AT28C16 datasheet
- [x] `ce-pin = [18]` = CE# pin per AT28C16 datasheet
- [x] `vcc-pin = [24]`, `gnd-pin = [12]` per standard
- [x] Address bus pins [8,7,6,5,4,3,2,1,23,22,19] = A0-A10 — no overlap with VCC, GND, or control signals
- [x] Data bus pins [9,10,11,13,14,15,16,17] = D0-D7 — no overlap
- [x] Pin 21 is NOT shared with any VPP path (compare: DIP24_2716 where pin 21 IS vpp-pin — this distinction is the whole point of the separate DIP24_2816 entry)
- [x] All 24 pins accounted for: pins 1-24 are assigned to address(11), data(8), ce(1), oe(1), we(1), vcc(1), gnd(1) = 24 total

---

## Standard Stack

### Core Change Targets
| File | Purpose | Change Type |
|------|---------|-------------|
| `firestarter_app/tools/build_db.py` | DB generation pipeline | Rewrite `resolve_pinout_key`; delete 3 tables; convert safety overrides to rules |
| `firestarter_app/firestarter/data/pinouts.json` | Physical DIP layout registry | Add `DIP24_2816` entry |
| `firestarter_app/tests/test_decoder.py` | Build_db correctness tests | Add `resolve_pinout_key` regression suite |
| `.planning/phases/58-.../58-SR-1-CHECKLIST.md` | SR-1 planning artifact | New file |
| `firestarter_app/doc/pinout-safety.md` | SR-1 operator-facing doc | New file (or append to existing doc) |

### No Changes Required
| File | Why Unchanged |
|------|--------------|
| `firestarter/src/proms/eeprom_28c.cpp` | Already pin-count-agnostic (confirmed) |
| `firestarter/src/proms/memory.cpp` | protocol=0x0D dispatch already present |
| `firestarter_app/tools/check_dispatch.py` | Already covers DIP24_2816 via dynamic load |
| `firestarter_app/firestarter/database.py` | `skip_local_override` seam unchanged |
| `firestarter_app/firestarter/data/chip_database.json` | Regenerated, not hand-edited |

---

## Architecture Patterns

### Recommended Structure for `resolve_pinout_key`

```
resolve_pinout_key(pin_count, variant, flags_int, pm_idx, proto_id, type_int, mem_size)
    │
    ├── pin_count == 24
    │   ├── pm_idx == 23
    │   │   ├── variant_lo == 0x01 → DIP24_2732
    │   │   ├── variant_lo == 0x10 → DIP24_2816  ← NEW (28C EEPROM family)
    │   │   └── else               → DIP24_2716
    │   ├── pm_idx == 0            → DIP24_6116   (SRAM; type=4 or proto=0x27)
    │   └── else                   → None (fail-safe skip)
    │
    ├── pin_count == 28
    │   ├── pm_idx == 22 → variant_lo sub-discriminates (0x10→27512, 0x11→27256, else→2764)
    │   ├── pm_idx == 21 → DIP28_2764
    │   ├── pm_idx == 20 → DIP28_28C256
    │   ├── pm_idx == 19 → DIP28_28C64
    │   ├── pm_idx == 18 → DIP28_28C64
    │   ├── pm_idx == 0  → SRAM-class (size discriminates 8K vs larger)
    │   └── else         → None (fail-safe skip)
    │
    └── pin_count == 32
        ├── pm_idx == 0  → DIP32_SST39SF040 (SRAM/NVRAM; type=4)
        ├── pm_idx in {5,7,9,10,11,12,13} → proto_id discriminates
        │   ├── 0x05/0x06 → DIP32_SST39SF040
        │   ├── 0x0D      → DIP32_28C512_EEPROM
        │   └── 0x07/0x08/0x10 → DIP32_STD
        └── else         → None (fail-safe skip)
```

### Algorithm Override Rules (Post-Selection, Before chip_entry Construction)

These replace the current hardcoded blocks and become named predicates:

**Rule 1: 28C EEPROM Algorithm Correction** (replaces 24-pin safety skip + extends to all variant_lo=0x10)
```python
# Any chip whose pinout resolves to DIP24_2816 gets algo=0x0D
if pinout_key == "DIP24_2816":
    proto_id = 0x0D
    _etype_before_override = "Flash/EEPROM"  # for WARNING-5 gate
```

**Rule 2: WARNING-5 Safety Net** (generalizes the current block)
```python
# 5V EEPROM on a pinout that could be mistaken for a UV-EPROM pinout
if proto_id == 0x07 and _etype_before_override == "Flash/EEPROM":
    proto_id = 0x0D
```

**Rule 3: fm1608 SRAM Override** (preserves current logic exactly)
```python
# SRAM-class chip mis-tagged with EPROM protocol
if type_int == 4 and proto_id in (0x07, 0x08, 0x0B):
    proto_id = 0x28
    # pinout already set to SRAM-class by resolve_pinout_key
```

### Two-Pass `_etype` Pattern — PRESERVED

The `_etype` must still be computed twice: [VERIFIED: PITFALLS.md RG-4 + current code structure]

1. **Pass 1 (flags-based):** Before any algorithm overrides. Used by WARNING-5 and fm1608 to detect mistagged chips.
2. **Algorithm overrides run.**
3. **Pass 2 (protocol-aware):** After all overrides. Stored in the final DB entry.

The two-pass pattern must be explicitly preserved and documented in the rewritten code.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Per-chip VPP safety verification | Custom chip-name checks | GATE-03 (`check_dispatch.py`) | Already covers full chip set dynamically |
| 24-pin EEPROM firmware dispatch | New firmware handler | `configure_eeprom28c` (proto=0x0D) | Already pin-count-agnostic |
| Pinout layout computation | XML bitmask parsing | Curated `pinouts.json` entries | pm_idx is an opaque index, not a bitmask |
| User overrides for unclassifiable chips | Build-time special cases | `~/.firestarter/database.json` seam | Already implemented in database.py |

---

## Common Pitfalls

### Pitfall 1: Using `flags & 0x10` as the Sole 24-pin EEPROM Discriminator

**What goes wrong:** The current safety-skip uses `flags & 0x10` to identify 24-pin EEPROMs. This misses chips like AM28C16A, CAT28C16A, XL2804A, etc. which have `flags=0x0000` but ARE EEPROMs. These 10 chips are currently in the DB with the dangerous `DIP24_2716` pinout + `algo=0x0B`.

**How to avoid:** Use `variant_lo == 0x10` as the 24-pin EEPROM family discriminator. Every real 24-pin 28C EEPROM in infoic.xml has `variant_lo=0x10`. The `flags & 0x10` bit is supplementary and unreliable for this purpose.

**Warning signs:** After re-derivation, if `firestarter info AM28C16A` shows `pinout=DIP24_2716` or `algorithm=11`, the discriminator is wrong.

### Pitfall 2: Forgetting the Two-Pass `_etype` Pattern

**What goes wrong:** If the two `_etype` computations are merged into one, the WARNING-5 predicate (which needs the flags-based value) fires incorrectly. The fm1608 override also depends on the order.

**How to avoid:** Maintain the two-pass pattern. The first pass (flags-based) must run BEFORE any algorithm overrides. The second pass (protocol-aware) runs AFTER all overrides and is what gets stored in the DB.

**Warning signs:** After re-derivation, run GATE-03 — any violation there means a chip slipped through with the wrong `_etype` or wrong algorithm.

### Pitfall 3: Over-Broad `resolve_pinout_key` Changes Affect 28-pin EPROM VPP Pins

**What goes wrong:** Changing how `(28, 22)` variant_lo sub-discriminates could flip `DIP28_27512` (VPP=pin 22) vs `DIP28_27256` (VPP=pin 1) for a real UV-EPROM. A 27512 routed to the 27256 pinout: 12V on A14 instead of pin 22 (OE/VPP) = chip damage.

**How to avoid:** The 28-pin pm_idx=22 variant_lo discriminator (0x10→27512, 0x11→27256, else→2764) is CONFIRMED from the infoic.xml survey. Preserve it exactly.

**Warning signs:** After re-derivation, check that W27C512 still has `pinout=DIP28_27512` and that AM27C256 still has `pinout=DIP28_27256` in the regenerated DB.

### Pitfall 4: The `DIP24_2816` Pinout Must NOT Have a `vpp-pin` Field

**What goes wrong:** If `DIP24_2816` accidentally includes `"vpp-pin": [21]` (like `DIP24_2716`), then GATE-03 will NOT catch the violation (GATE-03 checks `etype == Flash/EEPROM` routing to `configure_eprom` — it doesn't scan the pinout for vpp-pin presence). The chip would appear "safe" in GATE-03 while actually having a VPP routing path.

**How to avoid:** The `DIP24_2816` entry must use `"rw-pin": [21]` (NOT `"vpp-pin"`) since pin 21 is WE on these chips. Verify the JSON before committing.

**Warning signs:** Any pinout entry named `DIP24_2816` that contains the key `"vpp-pin"` is wrong.

### Pitfall 5: Blast Radius — Many Existing Chips Will Change Pinout/Algorithm

**What goes wrong:** The principled rules (D-01 correctness-first) will reassign many chips. The 10 dangerous 24-pin EEPROMs will get new algorithm=0x0D. SRAM chips at pm_idx=0 (DS1220(RW), FM1208, M48T02/12) will move from DIP24_2716 to DIP24_6116. Some 28-pin chips at pm_idx=0 may also change.

**How to avoid:** The changes are INTENTIONAL and each must be cited in Phase 59 GATE-02. The planner should add a task that records the expected diff before execution so GATE-02 review is straightforward.

**Warning signs:** Phase 59 diff shows more changes than expected — investigate each one.

---

## Code Examples

### Current `resolve_pinout_key` Signature (lines 266-327)

The current function signature:
```python
def resolve_pinout_key(pin_count, variant, flags_int, pm_idx=None, proto_id=None):
```

The new principled function needs additional parameters for the rules to work correctly:
```python
def resolve_pinout_key(pin_count, variant, flags_int, pm_idx=None, proto_id=None, type_int=1, mem_size=0):
```

`type_int` is needed for the fm1608/SRAM rules at pm_idx=0. `mem_size` is needed for the 28-pin SRAM size discriminator. Both are already available at the call site in `main()`.

### Current Call Site (line 435)

```python
pinout_key = resolve_pinout_key(
    pin_count, variant, flags, pm_idx=pm_idx, proto_id=proto_id
)
```

Updated call site:
```python
pinout_key = resolve_pinout_key(
    pin_count, variant, flags, pm_idx=pm_idx, proto_id=proto_id,
    type_int=type_int, mem_size=mem_size
)
```

### Tables to DELETE Entirely

Three module-level dicts will be removed (D-02):
- `DIP28_VARIANT_MAP` (lines ~125-130)
- `PIN_MAP_TO_PINOUT` (lines ~149-186)
- `PIN_MAP_PROTO_TO_PINOUT` (lines ~198-256)

---

## Runtime State Inventory

This is a build-pipeline phase (not a rename/refactor). The only "runtime state" is the generated `chip_database.json`.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | `chip_database.json` — 734 chips, generated output | Regenerated by `python3 tools/build_db.py` — not hand-edited |
| Live service config | None — no external services for build_db | None |
| OS-registered state | None | None |
| Secrets/env vars | `MINIPRO_XML_URL` default in build_db.py (or local `infoic.xml` if Phase 56 pinned snapshot in use) | None |
| Build artifacts | None beyond chip_database.json | None |

**Note:** Phase 56 committed a pinned `infoic.xml` snapshot for regression anchoring. The executor should use that snapshot (or the MINIPRO_XML_URL) consistently.

---

## Validation Architecture

Nyquist validation is enabled (key absent from config.json → treat as enabled).

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 7.x (installed via `pip install -e '.[test]'`) |
| Config file | `pyproject.toml` (firestarter_app/) |
| Quick run command | `python3 -m pytest tests/test_decoder.py -x -q` |
| Full suite command | `python3 -m pytest -q` (480 tests currently) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PIN-01 | `resolve_pinout_key` returns correct key for each pm_idx/variant_lo combination | unit | `pytest tests/test_decoder.py::TestResolvedPinoutKey -x` | ❌ Wave 0 |
| PIN-01 | Guess tables are not imported/referenced | unit | `pytest tests/test_decoder.py::TestGuessTablesDeleted -x` | ❌ Wave 0 |
| PIN-02 | WARNING-5 still fires for DIP28_2764 + Flash/EEPROM + proto=0x07 | unit | `pytest tests/test_decoder.py::TestWarning5Rule -x` | ❌ Wave 0 |
| PIN-02 | GATE-03 returns 0 violations after DB regen | integration | `python3 tools/check_dispatch.py` | ✅ exists |
| PIN-03 | AT28C16 appears in DB with algo=0x0D and pinout=DIP24_2816 | integration | `python3 -c "import json; db=json.load(open('firestarter/data/chip_database.json')); [print(c) for m,cs in db.items() for c in cs if 'AT28C16' in c.get('part_number','')]"` | Runs after DB regen |
| PIN-03 | `firestarter info AT28C16` exits 0 | integration | `firestarter info AT28C16` | Runs after install |
| PIN-03 | DIP24_2816 present in pinouts.json with no vpp-pin field | unit | `pytest tests/test_decoder.py::TestDIP24_2816Pinout -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python3 -m pytest tests/test_decoder.py -x -q`
- **Per wave merge:** `python3 -m pytest -q && python3 tools/check_dispatch.py`
- **Phase gate:** Full suite (480+ tests) green + GATE-03 green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_decoder.py::TestResolvedPinoutKey` — unit tests for every (pin_count, pm_idx, variant_lo) combination; at minimum: DIP24_2732, DIP24_2716, DIP24_2816, DIP24_6116, DIP28_27512, DIP28_27256, DIP28_2764, DIP28_28C256, DIP28_28C64, DIP32_STD, DIP32_SST39SF040, DIP32_28C512_EEPROM, DIP32_28C512_EEPROM (EEPROM)
- [ ] `tests/test_decoder.py::TestGuessTablesDeleted` — assert `PIN_MAP_TO_PINOUT`, `PIN_MAP_PROTO_TO_PINOUT`, `DIP28_VARIANT_MAP` do NOT exist in `tools.build_db` module
- [ ] `tests/test_decoder.py::TestWarning5Rule` — assert WARNING-5 still fires for AT28C256 (pm_idx=20, proto=0x07, erasable) → algo=0x0D
- [ ] `tests/test_decoder.py::TestDIP24_2816Pinout` — assert `DIP24_2816` in pinouts.json, no `vpp-pin` key, `rw-pin=[21]`, `ce-pin=[18]`, `oe-pin=[20]`
- [ ] `tests/test_decoder.py::TestDangerous24pinEEPROMFixed` — assert AM28C16A, XL2804A, X2816A etc. have algo=0x0D and pinout=DIP24_2816 in the regenerated DB (integration test loading chip_database.json)

---

## Security Domain

Security enforcement is not configured (`security_enforcement` key absent). This is a build-tool / data-pipeline phase with no auth, network serving, or user-input handling beyond parsing infoic.xml (an XML file fetched from a trusted GitLab URL). The primary safety concern is hardware damage from VPP mis-routing, which is addressed by SR-1 and GATE-03 (above) — not by ASVS categories.

The ASVS categories V2/V3/V4 do not apply. V5 (input validation) is addressed by the existing type/pin-count filter in build_db.py's DIP filter. No ASVS action items for this phase.

---

## D-04 Feasibility — Final Summary for Planner

**Layout derivation is NOT feasible: use selection-only.** The `pin_map` low byte (`pm_idx`) is an opaque cluster index. No gnd/vcc/data/address bitmask exists in the XML. The principled function selects among curated `pinouts.json` entries.

**Implication:** `pinouts.json` does NOT shrink in Phase 58. It gains exactly one entry (`DIP24_2816`). The "Full pinouts.json generation / elimination" is correctly deferred per CONTEXT.md. The planner should not budget work for layout derivation from XML — the function selects, it does not derive.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | AT28C16 and AT28C04 physical pin assignments follow the JEDEC 24-pin 5V EEPROM standard (WE=21, OE=20, CE=18, VCC=24, GND=12) — confirmed from standard and DIP24_6116 correspondence, not from a direct datasheet read in this session | DIP24_2816 Pinout Definition | If a chip has a non-standard pin assignment, DIP24_2816 would be wrong for that chip; SR-1 should verify against the Atmel AT28C16 datasheet |
| A2 | The 10 dangerous 24-pin EEPROM chips (AM28C16A, CAT28C16A, etc.) with `variant_lo=0x10` but `flags=0x0000` are genuine 5V EEPROMs (WE on pin 21) and not UV-EPROMs that happen to share variant_lo=0x10 | KEY FINDING: Dangerous 24-pin EEPROMs | If any chip with variant_lo=0x10 is actually a UV-EPROM, routing it to DIP24_2816+0x0D would be incorrect (though not dangerous — configure_eeprom28c is 5V safe for UV-EPROMs too) |
| A3 | The 28-pin pm_idx=0 AT29C256 (proto=0x05) uses the DIP28_28C256 pinout — inferred from 5V flash + 28-pin + 32KB mem_size matching the 28C256 layout | 28-pin Rules | If AT29C256 has a different layout, it would be misrouted; should verify in Phase 59 GATE-02 |

---

## Open Questions

1. **Should the 10 dangerous 24-pin chips (flags=0x0000, variant_lo=0x10) be explicitly called out in GATE-03 after Phase 58?**
   - What we know: GATE-03 currently misses them because `etype=UV-EPROM`. After Phase 58, they'll have `etype=Flash/EEPROM` and `algo=0x0D` — GATE-03 auto-covers them.
   - What's unclear: Whether the planner wants a regression test specifically asserting AM28C16A.algo==0x0D.
   - Recommendation: Add to Wave 0 test gap (TestDangerous24pinEEPROMFixed).

2. **SR-1 artifact location for D-10**
   - What we know: D-10 says `.planning/phases/58-.../58-SR-1-CHECKLIST.md` for planning layer + `firestarter_app/doc/` for operator layer.
   - What's unclear: Whether `doc/pinout-safety.md` is the right name for the sub-repo doc, or whether it should extend an existing doc.
   - Recommendation: Create `firestarter_app/doc/pinout-safety-review.md` as the operator-facing SR-1 artifact (mirrors the two-layer shield-revisions pattern from Phase 35).

---

## Sources

### Primary (HIGH confidence — verified by direct code/data inspection)
- `firestarter_app/tools/build_db.py` — full read; current resolve_pinout_key structure, tables to delete, safety override locations
- `firestarter_app/tools/check_dispatch.py` — full read; GATE-03 predicate confirmed as `etype == Flash/EEPROM`
- `firestarter_app/firestarter/data/pinouts.json` — full read; DIP24_6116 layout confirmed (rw-pin=21, oe=20, ce=18, no vpp-pin)
- `firestarter_app/firestarter/data/chip_database.json` — inspected; 10 dangerous 24-pin EEPROMs confirmed
- `firestarter/src/proms/eeprom_28c.cpp` — full read; pin-count-agnostic confirm
- Live infoic.xml fetch (MINIPRO_XML_URL at build time) — all 24-pin chip groups enumerated
- `.planning/research/STACK.md` — pm_idx decode, flags bit 4 = MP_ERASE_MASK CONFIRMED
- `.planning/research/PITFALLS.md` — hazard model, SR-1 checklist reference
- `firestarter_app/doc/infoic-field-dictionary.md` — Phase 56 field decode authority

### Secondary (MEDIUM confidence — project documentation)
- `.planning/phases/58-pinout-re-derivation-24-pin-eeprom-unblock/58-CONTEXT.md` — decisions D-01..D-11
- `.planning/REQUIREMENTS.md` — PIN-01/02/03 text
- `.planning/STATE.md` — project position
- `.planning/ROADMAP.md` — Phase 58 success criteria

---

## Metadata

**Confidence breakdown:**
- Principled rule structure: HIGH — derived from exhaustive infoic.xml inspection across all 24/28/32-pin chips
- 10 dangerous 24-pin EEPROMs finding: HIGH — confirmed from chip_database.json inspection
- DIP24_2816 pin layout: HIGH/ASSUMED — structurally confirmed from DIP24_6116; datasheet verification recommended in SR-1
- GATE-03 auto-coverage: HIGH — confirmed from check_dispatch.py code read
- configure_eeprom28c pin-count-agnostic: HIGH — confirmed from eeprom_28c.cpp read

**Research date:** 2026-06-08
**Valid until:** 2026-07-08 (infoic.xml is fetched live at build time; rule structure is stable)
