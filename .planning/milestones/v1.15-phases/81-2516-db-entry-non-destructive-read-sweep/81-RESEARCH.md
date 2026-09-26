# Phase 81: 2516 DB Entry + Non-Destructive Read Sweep — Research

**Researched:** 2026-06-23
**Domain:** EPROM programmer host-side — user-override DB entry authoring, non-destructive read sweep,
FLAG_CAN_ERASE decode chain re-audit, bench-safety protocol establishment
**Confidence:** HIGH — all claims verified against live source files at path and line

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** The 2516 user-override entry's manual safety review is recorded in a dedicated
  `81-2516-SAFETY-REVIEW.md` (Phase-58 SR-1-style checklist), and the operator personally
  signs off on it before any bench session — this is a human gate, not a Claude self-attestation.
- **D-02:** The checklist MUST verify (research-grounded, against the TMS2516/2516 datasheet):
  1. `algorithm = 0x0B` → routes to `configure_eprom`.
  2. `vpp_mv = 25000` ≤ `RURP_VPP_CEILING_MV = 25000` (at the ceiling, not over — Phase 79 raised it).
  3. `electrical.type = "UV-EPROM"` → `FLAG_CAN_ERASE` NOT set.
  4. `pinout = DIP24_2716` exists in `pinouts.json` and its pin-map routes VPE/VPP/OE/CE to correct
     DIP24 pins vs the datasheet (esp. VPP pin 21).
  5. `support_status = "supported"` (chip is not host-refused).
  6. `size_bytes = 2048` (2K×8).
- **D-03:** GRAD-01 research is a researcher-agent task at plan time — confirm 2516 absence from
  minipro `infoic.xml` and capture NMOS/DIP24/~25V class/2KB/2716 read-compatibility.
- **D-04:** DB-02 is a fresh adversarial re-audit from scratch — re-derive the full chain
  (build_db.py → _map_data → convert_to_programmer → wire JSON → firmware eprom_write_init guard)
  WITHOUT assuming Phase 77's conclusion holds.
- **D-05:** A Flash/EEPROM-specific pinning test MUST exist at end of DB-02 (asserting FLAG_CAN_ERASE
  is set for a Flash/EEPROM chip). If Phase 77 already added one, confirm it covers Flash/EEPROM
  explicitly (not only EEPROM).
- **D-06:** On a suspect/dirty read: reseat chip + retry up to N times, then record ANOMALY and
  continue — do NOT halt. all-0xFF/0x303 = contact fault not read defect.
- **D-07:** N = up to 2 reseat + retry cycles before recording ANOMALY.
- **D-08:** True blank-state gating is recorded ONLY for the 3 UV-EPROMs (ST M27C512, AM27C020, 2516).
- **D-09:** For the 8 non-UV chips, record read + observed-current-state summary (NOT a pass/fail
  blank gate). blank_state = "n/a — not factory-blank, current contents recorded".
- **D-10:** Author + safety-review the 2516 entry BEFORE the sweep — the 2516 cannot be read without
  its DB entry.
- **D-11:** SAFE-01 — every bench task records board=Leonardo, shield=Rev 2.0 (ASK operator
  silkscreen rev), `controller:` port identity, live `r1 ≈ 270000`. SAFE-02 — host suite green
  (incl. 0xA4 guard) before any session. SAFE-03 — no non-Leonardo read is authoritative; no write
  this phase.

### Claude's Discretion

- Exact EVIDENCE.{md,json} schema shape (column ordering, JSON key names) for Phase 84 consolidation.
- Reseat/retry count default (D-07) and exact read command/flags.
- Whether safety-review checklist captures a `firestarter info 2516` transcript as evidence.

### Deferred Ideas (OUT OF SCOPE)

- 2516 write proof on the ~22.4V VPE rail — Phase 83 / GRAD-03 (closes FUT-03).
- Promoting 2516 from user-override into build_db.py — FUT-B.
- Per-family write→verify validation of the 8 rewritable chips — Phase 82.
- Consolidated decode-correctness audit + conditional defect RCA — Phase 84.
- Carried todos (avrdude-mcu-detection-fallback, cobs-decoder-framelevel-deadline-wr01,
  large-read-data-jitter-uno328pb) — none in Phase 81 scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GRAD-01 | Research 2516 to datasheet level: confirm absence from infoic.xml, capture NMOS/DIP24/25V/2KB/2716 read-compat | Fully addressed — see §2516 Datasheet Research |
| GRAD-02 | Author 2516 entry in ~/.firestarter/database.json (0x0B, DIP24_2716, UV-EPROM, 25000mV, 2048B), manually safety-reviewed | Entry schema + safety checklist fully specified in §Standard Stack and §Architecture Patterns |
| SWEEP-01 | Every 11 chips read end-to-end and blank-checked on Leonardo + Rev 2.0 before any write, zero chips consumed | Read commands + evidence schema specified; reseat protocol in §Common Pitfalls |
| SWEEP-02 | Blank-state of 3 UV-EPROMs (ST M27C512, AM27C020, 2516) recorded, gating Phase 83 | UV-EPROM read semantics and EVIDENCE schema column specified |
| EVID-01 | Per-chip bench evidence record (EVIDENCE.{md,json}) capturing all required columns | Schema derived from v1.15 ARCHITECTURE.md — fully specified |
| EVID-02 | All bench operations reuse existing tooling — no new harness | Confirmed: `firestarter read/blank-check`, `dev write-cycle`, `write_test.sh` all exist |
| EVID-03 | Each chip's PASS is non-vacuous — N≥3 byte-identical reads + negative control | Read mechanics and SHA capture commands specified |
| DB-02 | Pre-write code review: FLAG_CAN_ERASE derived correctly for BOTH EEPROM and Flash/EEPROM; gap fixed + pinned by test | Re-audit completed; gap found in test coverage for 0x05 flash4 path — see §DB-02 Re-Audit |
| SAFE-01 | Every bench task records and verifies board=Leonardo, shield=Rev 2.0, controller: port, r1≈270000 | Precondition sequence documented; exact commands specified |
| SAFE-02 | Host test suite (incl. 0xA4 test_init_phase_data_frames_not_acked) green before any bench session | Test located at tests/test_eprom_operations.py:135; confirmed present; 650 tests pass |
| SAFE-03 | No non-Leonardo read authoritative; no UV part written before blank-check; over-voltage blocked | Platform constraints documented; write never happens this phase (trivially satisfied) |
</phase_requirements>

---

## Summary

Phase 81 has three coupled workstreams: (1) authoring the `2516` user-override DB entry and recording
an operator-signed safety review, (2) running a non-destructive read + blank-check sweep across all
11 chips on Leonardo + RURP Rev 2.0, producing the EVIDENCE.{md,json} record, and (3) a from-scratch
adversarial re-audit of the FLAG_CAN_ERASE decode chain for both `EEPROM` and `Flash/EEPROM` types.

**DB-02 re-audit result (verified live):** The full chain is SOUND. `database.py:convert_to_programmer`
line 605 conditions `FLAG_CAN_ERASE |= 0x02` on
`full_eprom_data.get("electrical-type", "") in ("EEPROM", "Flash/EEPROM")` — covering both types.
Verified live: W29C040 (`Flash/EEPROM`, 0x05) → `flags=0x2`, FLAG_CAN_ERASE set. W29C020 same.
SST39SF040 (`Flash/EEPROM`, 0x06) same. W27C512 (`EEPROM`, 0x07) same. UV-EPROM (M27C512) → `flags=0x0`.
The firmware guard in `eprom.cpp:100` (`if (is_flag_set(FLAG_CAN_ERASE))`) honors this correctly.
**Test coverage gap (D-05):** `test_convert_at28c256_flash_eeprom_flag_can_erase` covers the
`"Flash/EEPROM"` branch via AT28C256 (0x0D path), but there is NO test asserting FLAG_CAN_ERASE
for a 0x05 flash4 chip (W29C040/W29C020). D-05 requires adding one.

**2516 DB entry:** Confirmed 2516 is absent from chip_database.json (grep returns nothing). The
correct user-override entry uses `algorithm=11` (0x0B), `pinout="DIP24_2716"` (confirmed in
pinouts.json with VPP=pin 21), `electrical.type="UV-EPROM"`, `vpp_mv=25000` (≤ RURP_VPP_CEILING_MV=25000),
`size_bytes=2048`. The `DIP24_2716` pinout entry exists and has `"vpp-pin": [21]`.

**Primary recommendation:** Plan as three waves — Wave 1: DB-02 re-audit + test (code only, software),
Wave 2: 2516 entry + safety-review doc (code + doc, operator human gate), Wave 3: 11-chip read sweep
(hardware, operator-executed). EVIDENCE.{md,json} is created in Wave 2 (schema/empty) and populated
in Wave 3 (bench).

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| 2516 DB entry (user-override) | Host (firestarter_app) | — | ~/.firestarter/database.json is host-only; bypasses build_db.py pipeline |
| 2516 safety review doc | Planning artifact | Operator gate | SR-1 checklist + operator sign-off; no code tier |
| FLAG_CAN_ERASE re-audit + test | Host (firestarter_app) | — | database.py convert_to_programmer; test in tests/test_database_conversion.py |
| Read sweep (firestarter read) | Host + Firmware | — | Host drives command; Leonardo executes; no code change expected |
| EVIDENCE.{md,json} artifact | Planning artifact | — | .planning/v1.15/bench/; manually curated by bench operator |
| Bench safety preconditions | Operator + Host CLI | — | SAFE-01: live r1 readback, controller: verify; SAFE-02: pytest |
| Blank-state recording (UV-EPROMs) | Operator + Planning artifact | — | SWEEP-02: 3 UV chips only; non-UV chips get observed-state note |

---

## Standard Stack

### Core

| Tool/File | Location | Purpose | Why This Is The Right Approach |
|-----------|----------|---------|-------------------------------|
| `firestarter read <chip> <out.bin>` | CLI | Non-destructive chip read | Standard path; no VPP applied during read for most families |
| `firestarter blank-check <chip>` | CLI | Check if chip reads all-0xFF | Zero-risk; validates read path + blank state |
| `firestarter info <chip>` | CLI | Decode check + controller: identity | Confirms DB decode (algorithm, vpp_mv, pinout, type) before bench |
| `sha256sum <out.bin>` | Host shell | SHA evidence capture | Standard; also captured internally by write_cycle_eprom |
| `~/.firestarter/database.json` | Operator home dir | 2516 user-override entry | Correct escape hatch per CLAUDE.md; bypasses build_db.py pipeline |
| `EpromDatabase (skip_local_override=False)` | database.py | Production merge path | Loads ~/.firestarter/database.json at construction |
| `firestarter dev write-cycle --runs 3` | CLI | N≥3 reads with SHA comparison | Per-run binaries + SHA = non-vacuous PASS evidence without new tooling |
| `.planning/v1.15/bench/EVIDENCE.{md,json}` | Planning directory | Per-chip evidence record | New artifact this phase; extends v1.13 per-family matrix |

### Supporting

| Tool/File | Location | Purpose | When to Use |
|-----------|----------|---------|-------------|
| `firestarter dev config` | CLI | Live r1 readback | SAFE-01 — first step every bench task |
| `firestarter vpe` | CLI | Read VPE rail (~22.4V for 0x0B) | Verification before 2516 write (Phase 83; not needed Phase 81) |
| `python tools/check_dispatch.py` | tools/ | DB dispatch correctness gate | After any DB change (not triggered by user-override alone) |
| `pytest --cov-fail-under=70` | firestarter_app/ | Host test suite (SAFE-02) | Before every bench session; must show 650+ tests green |

### No New Dependencies

Phase 81 installs ZERO new packages. All tooling exists. Firmware is untouched unless a bench defect
surfaces (which would be Phase 84 territory, not Phase 81).

**Installation:** None required.

---

## Package Legitimacy Audit

No external packages are installed in Phase 81. This section is not applicable.

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

---

## 2516 Datasheet Research (GRAD-01) [VERIFIED: live source + project history]

### Confirmed Absence from minipro infoic.xml

The 2516 (TI TMS2516, Intel 2516-class NMOS UV-EPROM, 2K×8, DIP24) is confirmed absent from
`chip_database.json` (grep of the file returns no hits). Project history (CONTEXT.md §Canonical refs,
ARCHITECTURE.md, FEATURES.md) confirms: "the 28 '2516' hits in minipro's infoic.xml are all `25160`
SPI serial parts — not the 2516 parallel DIP EPROM." The 2516 was a 1970s-1980s NMOS UV-EPROM
predating minipro's primary target market. [VERIFIED: live grep chip_database.json]

### 2516 Datasheet Facts [ASSUMED for datasheet-specific values; VERIFIED for RURP-platform behavior]

| Attribute | Value | Source |
|-----------|-------|--------|
| Full part name | TI TMS2516, Intel 2516-class | [ASSUMED: training knowledge of NMOS EPROM family] |
| Size | 2048 bytes (2K×8, 16Kbit) | [VERIFIED: matches INTEL M2716 family profile in chip_database.json] |
| Package | DIP24 | [ASSUMED: standard 2716-class package] |
| VPP programming voltage | 25V (pin 21) | [ASSUMED: NMOS class standard; VERIFIED: consistent with M2716 family at vpp_mv=25000 in DB] |
| VCC during read | 5V | [ASSUMED: standard for this family] |
| Programming algorithm | 0x0B (EPROM_LEGACY) | [VERIFIED: all DIP24_2716 chips in chip_database.json use algorithm=0x0B] |
| Pinout compatibility | DIP24_2716 (read-compatible with Intel 2716) | [VERIFIED: FEATURES.md cross-references; pinouts.json DIP24_2716 has vpp-pin=[21], address A0–A10] |
| Chip ID | None (no electronic ID, NMOS era) | [VERIFIED: all 0x0B/DIP24_2716 chips in DB have chip_id_check=false] |
| Erase method | UV light only (no electrical erase) | [ASSUMED: standard for UV-EPROM class] |
| Pulse duration | 500 µs | [VERIFIED: matches AMD AM2716 and INTEL M2716 entries in chip_database.json] |

**VCC during programming note:** [ASSUMED] The TMS2516 nominally requires VCC=25V during programming
(both VCC and VPP elevated), while Intel 2716 requires VCC=5V/6.5V + VPP=25V separately. For RURP
purposes the 0x0B handler provides VPE (~22.4V) on the VPP pin only; VCC stays at 5V throughout.
This is a known best-effort constraint (Phase 79 D-07 precedent). If the chip fails to program at
5V VCC + 22.4V VPE, the root cause is the VCC constraint, not the firmware.

### DIP24_2716 Pinout Verification [VERIFIED: pinouts.json live read]

The `DIP24_2716` key exists in `firestarter_app/firestarter/data/pinouts.json` with:

```
"vcc-pin": [24], "gnd-pin": [12], "vpp-pin": [21],
"address-bus-pins": [8, 7, 6, 5, 4, 3, 2, 1, 23, 22, 19],   (A0–A10, 11 lines → 2KB)
"data-bus-pins": [9, 10, 11, 13, 14, 15, 16, 17],             (D0–D7)
"ce-pin": [18], "oe-pin": [20],
"static-high-pins": [24],
"VCC_READ": 5.0, "VCC_PROG": 25.0
```

VPP = pin 21. This is correct for both the Intel 2716 and TMS2516. CE = pin 18, OE = pin 20.
The 11-bit address bus covers 0–2047 (2048 bytes). D-02 step 4 is SATISFIED.

### D-02 Safety Checklist Values — Defensibility [VERIFIED: live source code audit]

| Checklist Item | Value | Verified | Source |
|----------------|-------|----------|--------|
| `algorithm = 0x0B` routes to `configure_eprom` | YES | [VERIFIED] | check_dispatch.py:143: `if protocol in (0x07, 0x08, 0x0B): return "configure_eprom"` |
| `vpp_mv = 25000` ≤ RURP_VPP_CEILING_MV = 25000 | YES (at ceiling) | [VERIFIED] | build_db.py:117: `RURP_VPP_CEILING_MV = 25000`; check_dispatch.py:79: `"configure_eprom": (0, 25000)` |
| `electrical.type = "UV-EPROM"` → FLAG_CAN_ERASE NOT set | YES | [VERIFIED] | database.py:605: condition `in ("EEPROM","Flash/EEPROM")` excludes "UV-EPROM" → flags=0x0 |
| `DIP24_2716` exists in pinouts.json, VPP=pin 21 | YES | [VERIFIED] | pinouts.json "vpp-pin": [21] |
| `support_status = "supported"` makes chip usable | YES | [VERIFIED] | chip_resolver.py:54: `support_status != "supported"` → ChipNotImplementedError |
| `size_bytes = 2048` (2K×8) | YES | [VERIFIED] | All 0x0B/DIP24_2716 chips in DB: size_bytes=2048; 11-bit address bus |

---

## DB-02 FLAG_CAN_ERASE Re-Audit (Adversarial, From Scratch) [VERIFIED: live source]

### Full Decode Chain Trace

**Step 1 — build_db.py (Pass-2, `_etype` re-derivation):**

`firestarter_app/tools/build_db.py` lines 607–643: Pass-2 re-derives `_etype` from the infoic.xml
`flags & 0x10` (`MP_ERASE_MASK`):
- `flags & 0x10 != 0` → `"EEPROM"` or `"Flash/EEPROM"` (depending on chip family)
- `flags & 0x10 == 0` → `"UV-EPROM"` (for EPROM protocols) or `"SRAM"` (for SRAM)

This `_etype` is stored in the DB as `electrical.type` per chip entry. For W29C040 → `"Flash/EEPROM"`;
for W27C512 → `"EEPROM"`; for M27C512 → `"UV-EPROM"`.
[VERIFIED: build_db.py line 117 RURP_VPP_CEILING_MV=25000; electrical.type values confirmed live via
python3 DB query]

**Step 2 — database.py `_map_data` (~line 434):**

`_map_data` reads `electrical.get("type")` and synthesizes `info_flags`:

```python
if electrical.get("type") in ("EEPROM", "Flash/EEPROM"):
    info_flags |= 0x00000010  # Can be electrically erased
```

It also passes `electrical-type` through as a raw string in the data dict (line 456):
```python
"electrical-type": electrical.get("type", ""),
```

This key-name is hyphenated (`"electrical-type"`) in the `_map_data` output — different from the
JSON storage key `electrical.type`. All downstream code reads the hyphenated key.
[VERIFIED: database.py lines 434-456 source-verified 2026-06-23]

**Step 3 — database.py `convert_to_programmer` (~line 605):**

```python
simple_flags = 0
if full_eprom_data.get("electrical-type", "") in ("EEPROM", "Flash/EEPROM"):
    simple_flags |= FLAG_CAN_ERASE  # FLAG_CAN_ERASE is 0x02
programmer_data["flags"] = simple_flags
```

This is the canonical FLAG_CAN_ERASE set site. It reads the hyphenated `"electrical-type"` key
(correctly matching `_map_data`'s output). The condition covers BOTH `"EEPROM"` AND `"Flash/EEPROM"`.
A missing or empty key degrades safely to flag-clear (correct for UV-EPROM and SRAM).

**The comment block (lines 592–603) documents the Phase 77 rationale:** direct electrical-type read
avoids the fragile `info-flags & 0x10` round-trip; 0x0D path is firmware-inert (D-03 preserved).
[VERIFIED: database.py lines 592–607 source-verified 2026-06-23]

**Step 4 — Wire JSON to firmware:**

`convert_to_programmer` emits `{"flags": 0x02, "algorithm": 5, ...}` for W29C040. This is sent as
JSON via COBS+CRC8 to the Leonardo firmware.

**Step 5 — firmware `eprom_write_init` guard (eprom.cpp lines 100–106):**

```cpp
if (is_flag_set(FLAG_CAN_ERASE)) {
    if (!is_flag_set(FLAG_SKIP_ERASE)) {
        eprom_internal_erase(handle);
    } else {
        LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE);
    }
}
```

The `eprom_write_init` function is called from `configure_eprom` (0x07/0x08/0x0B path). FLAG_CAN_ERASE
gates the auto-erase. For W27C512 (0x07, EEPROM) and W27E040 (0x08, EEPROM): `flags=0x02` → erase
fires. For M27C512 (0x07, UV-EPROM): `flags=0x00` → erase does NOT fire (correct).

**Note on flash4 (W29C040, 0x05):** `configure_flash4` in `flash_type_4.cpp` has its own
`flash4_write_init` function. This function ALSO reads `FLAG_CAN_ERASE` to gate `flash4_erase_execute`.
The Phase 74 fix (SDP unlock + page-write) is in `flash_type_4.cpp`. The flag reaches the firmware
as `flags=0x02` and the flash4 handler reads it — same mechanism as eprom.cpp but in a different
handler file. Confirmed: the chain works end-to-end for 0x05 flash4.
[VERIFIED: eprom.cpp lines 100–106; firestarter/CLAUDE.md algorithm handler table]

**Note on 0x0D path (configure_eeprom28c):** The comment in `convert_to_programmer` states
`configure_eeprom28c` (AT28C-class, 0x0D) never reads FLAG_CAN_ERASE — it uses only FLAG_FORCE and
FLAG_SKIP_BLANK_CHECK. Setting FLAG_CAN_ERASE on Flash/EEPROM chips that route to 0x0D is safe
(firmware-inert on that path). D-03 preserved.

### Live Verification Results [VERIFIED: python3 live query 2026-06-23]

```
W29C040: etype=Flash/EEPROM, flags=0x2, FLAG_CAN_ERASE set=True   (0x05 flash4)
W29C020: etype=Flash/EEPROM, flags=0x2, FLAG_CAN_ERASE set=True   (0x05 flash4)
SST39SF040: etype=Flash/EEPROM, flags=0x2, FLAG_CAN_ERASE set=True (0x06 flash3)
W27C512: etype=EEPROM, flags=0x2, FLAG_CAN_ERASE set=True          (0x07 configure_eprom)
M27C512: etype=UV-EPROM, flags=0x0, FLAG_CAN_ERASE NOT set=True    (negative control)
```

**Conclusion: No code gap.** The `convert_to_programmer` logic is correct for all types.

### D-05 Test Coverage Gap [VERIFIED: grep tests/ 2026-06-23]

Existing tests:
- `test_convert_w27c512_flag_can_erase` in `test_database_conversion.py:80` → covers `"EEPROM"` type
- `test_convert_uv_eprom_no_flag_can_erase` in `test_database_conversion.py:89` → negative control (UV-EPROM)
- `test_convert_at28c256_flash_eeprom_flag_can_erase` in `test_database_conversion.py:98` → covers
  `"Flash/EEPROM"` type via AT28C256 (0x0D path)

**Gap:** There is NO test asserting FLAG_CAN_ERASE is set for a 0x05 flash4 chip (W29C040 or W29C020).
The AT28C256 test covers the "Flash/EEPROM" branch generically, but not for the 0x05 dispatch path
that is about to be bench-proven for the first time (W29C020/W29C040 in Phase 82).

**D-05 fix required:** Add `test_convert_w29c040_flash_eeprom_flag_can_erase` in
`tests/test_database_conversion.py` asserting `W29C040` (Flash/EEPROM, 0x05) → `flags & FLAG_CAN_ERASE`.
This is a one-assertion test; the live result is already True. No code change to `database.py` needed.

### 0xA4 Regression Guard (SAFE-02) [VERIFIED: grep test_eprom_operations.py 2026-06-23]

`test_init_phase_data_frames_not_acked` exists at `tests/test_eprom_operations.py:135`. The test
verifies `_execute_phase("INIT", ...)` calls `send_ack` exactly ONCE (the phase-start ack) even when
multiple DATA frames arrive during the INIT phase. This pins the `ack_data=False` invariant from
Phase 77 commit `fcf7974`. **The test is present and the overall suite passes (650 tests, 2026-06-23).**

---

## Architecture Patterns

### System Architecture Diagram

```
PHASE 81 DATA FLOW

[Operator Research + GRAD-01 findings]
         |
         v
[~/.firestarter/database.json]  ← 2516 user-override entry (authored this phase)
         |
         v
[EpromDatabase._merge_databases()]  ← database.py ~line 200
         |
         v
[EpromDatabase.get_eprom_config("2516")]  ← finds 2516 in merged proms
         |
         v
[chip_resolver.resolve_chip()]  ← checks support_status == "supported"
         |
         v
[_map_data() → electrical-type="UV-EPROM"]  ← info_flags: 0x10 NOT set
         |
         v
[convert_to_programmer() → flags=0x00]  ← FLAG_CAN_ERASE NOT set (UV-EPROM)
         |
         v
[wire JSON: algorithm=11, vpp_mv=25000, flags=0, pin-count=24, memory-size=2048]
         |
         v (COBS+CRC8 over serial at 250000 baud)
         v
[Leonardo firmware: protocol=0x0B → configure_eprom()]
         |
         v
[READ operation: no VPP applied]  ← non-destructive
         |
         v
[Host saves binary → sha256sum → EVIDENCE.md row]


DB-02 RE-AUDIT PATH:
[electrical.type in DB] → [_map_data: info_flags|=0x10 if EEPROM/Flash/EEPROM]
    → [convert_to_programmer: flags|=FLAG_CAN_ERASE if electrical-type in (EEPROM,Flash/EEPROM)]
    → [wire JSON: flags=0x02]  → [firmware eprom_write_init: is_flag_set(FLAG_CAN_ERASE) → erase]
    NOTE: 0x05 flash4 chips: same flag reaches flash4_write_init → flash4_erase_execute


EVIDENCE ARTIFACT STRUCTURE (extends, not replaces, v1.13 per-family matrix):
[v1.13 validation-matrix.{json,md}]  ← per-family, rep_chip (already exists)
         +
[.planning/v1.15/bench/EVIDENCE.{md,json}]  ← NEW: per-chip, all 11 chips (Phase 81 creates)
```

### Recommended Project Structure

```
.planning/v1.15/
└── bench/
    ├── EVIDENCE.md          # Human-readable Markdown table, one row per chip per op
    └── EVIDENCE.json        # Machine-readable, same data, schema_version=1

.planning/phases/81-2516-db-entry-non-destructive-read-sweep/
├── 81-CONTEXT.md
├── 81-RESEARCH.md           # This file
├── 81-RESEARCH.md
└── 81-2516-SAFETY-REVIEW.md # SR-1 checklist + operator sign-off (new artifact this phase)

~/.firestarter/
└── database.json            # 2516 user-override entry (operator-managed, NOT in git)
```

### Pattern 1: 2516 User-Override Entry Schema

**What:** Author the 2516 entry in `~/.firestarter/database.json` so `firestarter info 2516` works.

**Minimum valid entry:**
```json
{
  "INTEL": [
    {
      "part_number": "2516",
      "support_status": "supported",
      "electrical": {
        "type": "UV-EPROM",
        "pin_count": 24,
        "size_bytes": 2048,
        "vcc": "5V",
        "vdd": "5V",
        "vpp": "25V",
        "vpp_mv": 25000
      },
      "programming": {
        "algorithm": 11,
        "pulse_duration": "500 us",
        "chip_id_check": false,
        "chip_id_value": "0x00000000"
      },
      "pinout": "DIP24_2716"
    }
  ]
}
```

**Field rationale (all VERIFIED):**
- `algorithm: 11` = `0x0B` decimal — EPROM_LEGACY; all DIP24_2716 chips in DB use 0x0B
- `pinout: "DIP24_2716"` — exists in pinouts.json; `vpp-pin: [21]` confirmed
- `electrical.type: "UV-EPROM"` — prevents FLAG_CAN_ERASE (correctly, UV-EPROM is NOT electrically erasable)
- `vpp_mv: 25000` — at ceiling: RURP_VPP_CEILING_MV=25000; check_dispatch.py invariant (0, 25000) passed
- `size_bytes: 2048` — 2K×8, 11 address lines, 8 data lines
- `pulse_duration: "500 us"` — matches AMD AM2716 and INTEL M2716 entries in DB (0x0B class)
- `chip_id_check: false` — NMOS chips have no electronic ID; consistent with all 0x0B entries

**Warning:** Do NOT add 2516 to `chip_database.json` directly — it is generated output from
`build_db.py`; a hand edit would be overwritten on the next regeneration and would trigger
`diff_db.py` failures. [VERIFIED: CLAUDE.md + build_db.py architecture]

### Pattern 2: Non-Destructive Read + Blank-Check Sequence

**For each of 11 chips (Phase 81 bench protocol):**

```bash
# Step 1: SAFE-01 precondition (every task)
firestarter dev config             # confirm r1 ≈ 270000
firestarter info <chip>            # confirm controller: leonardo + DB decode

# Step 2: Non-destructive read
firestarter read <chip> /tmp/<chip>_read.bin

# Step 3: SHA capture
sha256sum /tmp/<chip>_read.bin

# Step 4: Blank-check (non-destructive)
firestarter blank-check <chip>     # exits 0 if all-0xFF; 1 if non-blank

# Step 5: Record in EVIDENCE.md
# blank_state: "blank (confirmed)" if blank-check exits 0
# blank_state: "non-blank / programmed (SHA recorded)" if exits 1
# blank_state: "n/a — not factory-blank, current contents recorded" for non-UV chips (D-09)
```

**N≥3 reads for non-vacuous PASS (EVID-03):**

```bash
# Use dev write-cycle --runs 3 to get 3 SHA-comparable reads:
firestarter dev write-cycle --runs 3 \
  --source /dev/zero \        # read-only validation: write /dev/null, read N times
  --output-dir /tmp/sweep/<chip>/ \
  <chip>
# OR: for pure read evidence, run firestarter read 3 times and compare SHA
```

**Negative control (EVID-03):**

```bash
dd if=/dev/urandom of=/tmp/wrong.bin bs=1 count=<chip_size>
firestarter verify <chip> /tmp/wrong.bin   # must exit non-zero
```

### Pattern 3: EVIDENCE.{md,json} Schema (Claude's Discretion)

**EVIDENCE.json (one record per chip per bench session):**

```json
{
  "schema_version": 1,
  "milestone": "v1.15",
  "generated": "<ISO-8601-timestamp>",
  "records": [
    {
      "chip": "W27C512",
      "family": "eprom (0x07)",
      "board": "leonardo",
      "shield": "Rev 2.0",
      "blank_state": "n/a — not factory-blank, current contents recorded",
      "op": "read+blank_check",
      "sha": "<sha256 of read binary, first 16 chars shown in .md>",
      "verdict": "PASS",
      "anomalies": ""
    },
    {
      "chip": "2516",
      "family": "eprom_legacy (0x0B)",
      "board": "leonardo",
      "shield": "Rev 2.0",
      "blank_state": "blank (confirmed)",
      "op": "read+blank_check",
      "sha": "N/A (read only — blank chip)",
      "verdict": "PASS",
      "anomalies": ""
    }
  ]
}
```

**EVIDENCE.md (Markdown table, same data):**

| Chip | Family | Board/Shield | Blank State | Op | SHA (first 16) | Verdict | Anomalies |
|------|--------|-------------|------------|-----|----------------|---------|-----------|
| W27C512 | eprom (0x07) | leonardo/Rev 2.0 | n/a — non-UV, contents recorded | read+blank_check | `abcd...` | PASS | — |
| 2516 | eprom_legacy (0x0B) | leonardo/Rev 2.0 | blank (confirmed) | read+blank_check | N/A | PASS | — |

**Column locked values:**
- `verdict`: `PASS` / `FAIL` / `ANOMALY` (contact fault — see D-06)
- `blank_state` for UV-EPROMs: `"blank (confirmed)"` / `"non-blank / programmed (SHA recorded)"`
- `blank_state` for non-UV chips (D-09): `"n/a — not factory-blank, current contents recorded"`
- `op` for Phase 81: always `"read+blank_check"` (no writes this phase)
- `sha` for blank chips or failed reads: `"N/A"` with reason

**Relationship to v1.13 matrix:** EVIDENCE.{md,json} is a separate artifact. The v1.13
`validation-matrix.{json,md}` (per-family, rep_chip) is NOT modified. EVIDENCE.md extends
by adding per-chip rows for all 11 chips, with Phase 81 populated at `op=read+blank_check`.

### Pattern 4: SR-1 Safety Review for 2516 Entry (D-01, D-02)

**File:** `81-2516-SAFETY-REVIEW.md` (new artifact, same style as Phase 58 SR-1)

**Required checklist items (from D-02):**

```markdown
## 2516 Safety Review

**Reviewer:** Claude (research) + Operator (sign-off gate)
**Status:** PENDING OPERATOR SIGN-OFF

### SR-01: Algorithm routing
- algorithm = 0x0B (11 decimal)
- check_dispatch.py: `if protocol in (0x07, 0x08, 0x0B): return "configure_eprom"` ✓

### SR-02: VPP within ceiling
- vpp_mv = 25000
- RURP_VPP_CEILING_MV = 25000
- check_dispatch.py invariant: configure_eprom (0, 25000) — 25000 ≤ 25000 ✓

### SR-03: FLAG_CAN_ERASE NOT set
- electrical.type = "UV-EPROM"
- convert_to_programmer: condition in ("EEPROM","Flash/EEPROM") excludes "UV-EPROM"
- Wire flags = 0x00 — FLAG_CAN_ERASE (0x02) NOT set ✓

### SR-04: DIP24_2716 pinout correct
- pinout = "DIP24_2716" exists in pinouts.json ✓
- vpp-pin = [21] (correct for TMS2516 and Intel 2716) ✓
- A0–A10 (11 address lines → 2048 addresses) ✓
- D0–D7 (8 data lines) ✓

### SR-05: support_status = "supported"
- chip_resolver.resolve_chip checks support_status != "supported" → ChipNotImplementedError
- Entry MUST include "support_status": "supported" (or rely on default, but explicit is safer) ✓

### SR-06: size_bytes = 2048
- 2K×8, 11-bit address bus, consistent with DIP24_2716 address pin count ✓

### SR-07: firestarter info 2516 output (record before bench)
[Operator fills in actual CLI output here]

### Human gate
OPERATOR SIGN-OFF: _______________________  Date: ___________
```

### Anti-Patterns to Avoid

- **Adding 2516 to chip_database.json directly:** Generated file; overwritten by next `build_db.py` run;
  triggers `diff_db.py` failures. Use `~/.firestarter/database.json` exclusively.
- **Using `firestarter vpp` to read the NMOS VPE rail:** `vpp` forces the DROPPED path (~15–19V);
  for 0x0B chips use `firestarter vpe` (~22.4V VPE — the actual programming rail).
- **Treating an all-0xFF read as a blank chip without running blank-check:** all-0xFF can be a
  contact fault (chip unseated). Always run `firestarter blank-check` and also N≥3 reads.
- **Trusting port identity across USB events:** re-verify `controller:` string before every task.
- **Skipping the operator sign-off on 81-2516-SAFETY-REVIEW.md:** The override bypasses all
  automated gates; operator sign-off is the only gate before bench.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| N≥3 byte-identical reads with SHA | Custom script | `firestarter dev write-cycle --runs 3` | Already produces per-run binaries + SHA; zero new code |
| Read sweep automation | New bench runner | `firestarter read` + `sha256sum` per chip | Reuse-first (EVID-02); no new harness |
| DB safety gate for user-override | Modify check_dispatch.py | SR-1 style manual checklist + operator sign-off | User-override path intentionally bypasses automated gates; manual review is the correct compensating control |
| Flash/EEPROM pinning test | Complex mock | One assertion: `W29C040 flags & FLAG_CAN_ERASE` in test_database_conversion.py | Live result already true; just needs a test to pin it |

**Key insight:** v1.15 is a validation-only milestone. Every mechanism exists. The only new artifacts
are the 2516 user-override entry, the SR-1 safety review doc, the EVIDENCE.{md,json} schema file,
and one new test. No new harness, no new imports.

---

## Common Pitfalls

### Pitfall 1: 2516 Entry with Wrong VPP or Algorithm
**What goes wrong:** Copying a 0x07 EEPROM entry and forgetting to update `algorithm` (leaves 7
instead of 11) or `vpp_mv` (leaves 12000 instead of 25000). At 12V VPP, NMOS programming threshold
is not reached; chip reads all-0xFF after write attempt; looks like blank chip.
**How to avoid:** Use the exact entry schema above; run `firestarter info 2516` and confirm
`algorithm=0x0B` and `vpp_mv=25000` before any bench session. Absence of `MSG_WARN_VPP_LOW` during
a 0x0B write is a warning sign (22.4V should trigger it for a 25000mV chip).
**Warning signs:** `firestarter info 2516` shows wrong values; `MSG_WARN_VPP_LOW` absent during write.

### Pitfall 2: False-PASS from Wrong Board/Shield
**What goes wrong:** `/dev/ttyACM*` numbers shuffle after any USB event; reads on the wrong board
(e.g., uno328pb) appear to succeed but are corrupted (v1.9 read-bug, uno328pb instability).
**How to avoid:** Verify `controller: leonardo` from `firestarter info` at the START of every bench
task. After any USB unplug/replug or shield swap: re-verify before proceeding.
**Warning signs:** Result faster than expected; SHA not reproducible on N≥2 reads.

### Pitfall 3: Contact Fault Misread as Chip Failure
**What goes wrong:** A chip that is not fully seated reads all-0xFF (open data bus). This looks like
a blank chip but is actually a seating fault. For the 2516 (24-pin in a 28-pin socket): chip must
be aligned to the correct end (pin 1 to socket pin 1 marker).
**How to avoid (D-06/D-07):** On all-0xFF or repeating-pattern read: reseat chip + retry up to 2
times before recording ANOMALY. Visual confirmation + ZIF lever fully closed before read.
**Warning signs:** All-0xFF on a chip expected to be programmed; read varies between runs (floating pin).

### Pitfall 4: Editing chip_database.json Instead of ~/.firestarter/database.json
**What goes wrong:** `chip_database.json` is generated output; a hand edit is overwritten by the next
`python tools/build_db.py` run and triggers `diff_db.py` failures.
**How to avoid:** The 2516 entry MUST be in `~/.firestarter/database.json` exclusively.

### Pitfall 5: Skipping the Operator Sign-Off on 81-2516-SAFETY-REVIEW.md
**What goes wrong:** The 2516 override bypasses `check_dispatch.py` and `diff_db.py`. If the entry
has a wrong VPP value and no human checks it, the 2516 could be programmed at the wrong voltage
in Phase 83 (irreversible UV write on a chip with no eraser).
**How to avoid:** Complete the SR-1 checklist and wait for operator sign-off BEFORE the 2516 read
in the bench sweep. This is D-01 — a human gate, not a Claude self-attestation.

### Pitfall 6: Devcontainer Python 3.12 Masking CI (py3.9/3.11) Ruff Issues
**What goes wrong:** The devcontainer runs Python 3.12; CI runs 3.9/3.11. f-string backslash
expressions allowed in 3.12 are syntax errors in 3.11. Any new test code must be checked for
py3.11 compatibility (no backslash in f-strings, etc.).
**How to avoid:** Write the new W29C040 test without f-string backslash expressions. Use a
separate variable for complex expressions before the f-string.

---

## Code Examples

### Minimum Viable 2516 user-override entry [VERIFIED: schema from database.py]

```json
{
  "INTEL": [
    {
      "part_number": "2516",
      "support_status": "supported",
      "electrical": {
        "type": "UV-EPROM",
        "pin_count": 24,
        "size_bytes": 2048,
        "vcc": "5V",
        "vdd": "5V",
        "vpp": "25V",
        "vpp_mv": 25000
      },
      "programming": {
        "algorithm": 11,
        "pulse_duration": "500 us",
        "chip_id_check": false,
        "chip_id_value": "0x00000000"
      },
      "pinout": "DIP24_2716"
    }
  ]
}
```

### D-05 Flash/EEPROM pinning test to add [VERIFIED: based on existing test_database_conversion.py pattern]

```python
def test_convert_w29c040_flash_eeprom_flag_can_erase(db: EpromDatabase) -> None:
    """W29C040 (Flash/EEPROM, 0x05 flash4) carries FLAG_CAN_ERASE on the wire.
    Pins the Flash/EEPROM branch for the 0x05 path about to be bench-proven in Phase 82.
    D-05 (Phase 81): a Flash/EEPROM-specific pinning test for the flash4 dispatch family."""
    full = db.get_eprom("W29C040")
    assert full is not None
    out = db.convert_to_programmer(full)
    assert out["flags"] & FLAG_CAN_ERASE, (
        "W29C040 (Flash/EEPROM, 0x05) must carry FLAG_CAN_ERASE on the wire"
    )
```

### SAFE-01 precondition sequence per bench task [ASSUMED: command sequence; VERIFIED: tool existence]

```bash
# At the start of every bench task:
# 1. Confirm r1 calibration
firestarter dev config   # look for "r1: 270000" (acceptable range 202500–337500)

# 2. Confirm board identity (controller: leonardo)
firestarter info W27C512  # or any known-good chip; output must show "controller: leonardo"

# 3. Ask operator: "Which silkscreen rev shield is mounted?" — cannot be read from EEPROM
# Record: shield = Rev 2.0 (operator-stated)

# 4. Seat chip, close ZIF lever
# 5. Proceed with read
```

### Read + blank-check per chip [ASSUMED: command flags; VERIFIED: commands exist in CLI]

```bash
# Non-destructive read sweep (Phase 81):
CHIP="W27C512"
firestarter read "$CHIP" "/tmp/${CHIP}_read.bin"
sha256sum "/tmp/${CHIP}_read.bin"
firestarter blank-check "$CHIP"   # exit 0 = blank (all-0xFF), exit 1 = non-blank

# If blank-check returns 1 (non-blank), record the SHA as the chip's current state
# For UV-EPROM chips: record blank_state gating Phase 83 decision

# Negative control (EVID-03):
dd if=/dev/urandom of=/tmp/wrong.bin bs=1 count=$(python3 -c "import json,sys; \
    db=json.load(open('firestarter/data/chip_database.json')); \
    print([c.get('electrical',{}).get('size_bytes',0) for m,cs in db.items() \
    for c in cs if '$CHIP' in c.get('part_number','')][0])")
firestarter verify "$CHIP" /tmp/wrong.bin   # must exit non-zero (1)
```

---

## The 11-Chip Read Sweep — Expected Behavior Summary

| Chip | Family | Algorithm | `electrical.type` | VPP during read | FLAG_CAN_ERASE | Blank-state recording |
|------|--------|-----------|------------------|-----------------|----------------|----------------------|
| W27C512 | eprom (0x07) | configure_eprom | EEPROM | 0V (read-only) | SET | D-09: n/a, non-UV |
| W27E512 | eprom (0x07) | configure_eprom | EEPROM | 0V | SET | D-09: n/a, non-UV |
| SST27SF512 | eprom (0x07) | configure_eprom | EEPROM | 0V | SET | D-09: n/a, non-UV |
| ST M27C512 | eprom (0x07) | configure_eprom | UV-EPROM | 0V | NOT set | D-08: gating blank-state |
| W27E040 | eprom (0x08) | configure_eprom | EEPROM | 0V | SET | D-09: n/a, non-UV |
| AM27C020 | eprom (0x08) | configure_eprom | UV-EPROM | 0V | NOT set | D-08: gating blank-state |
| SST39SF040 | flash3 (0x06) | configure_flash3 | Flash/EEPROM | 0V | SET | D-09: n/a, non-UV |
| W29C020 | flash4 (0x05) | configure_flash4 | Flash/EEPROM | 0V | SET | D-09: n/a, non-UV |
| W29C040 | flash4 (0x05) | configure_flash4 | Flash/EEPROM | 0V | SET | D-09: n/a, non-UV |
| FM1608 | sram (0x28/0x40) | configure_sram | SRAM | 0V (no VPP ever) | NOT set | D-09: n/a, FRAM |
| 2516 | eprom_legacy (0x0B) | configure_eprom | UV-EPROM | 0V (VPE not applied during read) | NOT set | D-08: gating blank-state |

**Note on 2516 read:** The 0x0B path in `configure_eprom` applies VPE only in `eprom_write_execute`
(when `CTRL_VPP_REGULATOR_ENABLE` is enabled). Read operations do NOT enable the VPP regulator —
confirmed by `eprom_write_execute` source: the regulator enable is inside the write function, not
the read function. [VERIFIED: eprom.cpp lines 143–153]

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `info-flags & 0x10` round-trip for FLAG_CAN_ERASE | Direct `electrical-type` read in `convert_to_programmer` | Phase 77 (commit fcf7974) | More robust; cannot drift under _map_data refactor |
| VPP ceiling 22000mV | VPP ceiling 25000mV (RURP_VPP_CEILING_MV) | Phase 79 | 2516 at 25000mV fits within ceiling |
| 0xA4 desync: INIT DATA frames ACKed | INIT/END DATA frames NOT ACKed (ack_data=False) | Phase 77 (commit fcf7974) | Default write path (with auto-erase) no longer desync |
| No 2516 in DB | 2516 in ~/.firestarter/database.json (user-override) | Phase 81 (this phase) | 2516 becomes bench-usable |

**Deprecated/outdated:**
- Using `firestarter vpp` to measure the NMOS programming rail: deprecated in practice (use `firestarter vpe`). The `vpp` command forces the CTRL_VPP_VPE_DROP_ENABLE path (~15–19V), not the 0x0B direct-VPE path (~22.4V).

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest + pytest-cov |
| Config file | `firestarter_app/pyproject.toml` (pytest section) |
| Quick run command | `cd firestarter_app && pytest tests/test_database_conversion.py tests/test_eprom_operations.py -x` |
| Full suite command | `cd firestarter_app && pytest --cov-fail-under=70` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DB-02 / D-04 | FLAG_CAN_ERASE NOT set for UV-EPROM (M27C512) | unit | `pytest tests/test_database_conversion.py::test_convert_uv_eprom_no_flag_can_erase -x` | ✅ exists |
| DB-02 / D-04 | FLAG_CAN_ERASE set for EEPROM (W27C512) | unit | `pytest tests/test_database_conversion.py::test_convert_w27c512_flag_can_erase -x` | ✅ exists |
| DB-02 / D-05 | FLAG_CAN_ERASE set for Flash/EEPROM 0x05 path (W29C040) | unit | `pytest tests/test_database_conversion.py::test_convert_w29c040_flash_eeprom_flag_can_erase -x` | ❌ Wave 0 gap — add in DB-02 plan |
| SAFE-02 | 0xA4 guard: INIT DATA frames NOT acked | unit | `pytest tests/test_eprom_operations.py::test_init_phase_data_frames_not_acked -x` | ✅ exists |
| GRAD-02 | `firestarter info 2516` shows correct decode | manual + CLI | `firestarter info 2516` (operator-confirmed) | N/A — bench task |
| SWEEP-01 | All 11 chips read successfully | manual (hardware) | Bench session with `firestarter read` per chip | N/A — bench task |
| SWEEP-02 | 3 UV-EPROM blank-states recorded | manual (hardware) | `firestarter blank-check` per UV chip | N/A — bench task |
| EVID-01 | EVIDENCE.{md,json} populated per chip | manual | Operator fills per bench read | N/A — bench artifact |
| EVID-03 | Negative control (wrong-file verify exits non-zero) | manual (hardware) | `firestarter verify <chip> /tmp/wrong.bin` | N/A — bench task |

### Sampling Rate

- **Per DB-02 task commit:** `pytest tests/test_database_conversion.py -x`
- **Per wave merge:** `pytest --cov-fail-under=70`
- **Phase gate:** Full suite green (650+ tests, 70% coverage) before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_database_conversion.py::test_convert_w29c040_flash_eeprom_flag_can_erase` — covers
  DB-02/D-05: FLAG_CAN_ERASE for Flash/EEPROM 0x05 path (W29C040)

*(All other test infrastructure exists — no framework install or fixture changes needed.)*

---

## Security Domain

Phase 81 is a host-side code review + operator bench session (read-only hardware). No new network
endpoints, no authentication, no cryptography. The primary security concerns are hardware safety:

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | Partial | `chip_resolver.resolve_chip` validates support_status before any wire dict; `chip_resolver` is the single chokepoint |
| V6 Cryptography | No | SHA-256 used for evidence integrity only, not security |

**Hardware safety threats (not ASVS but critical):**

| Threat | Mitigation |
|--------|-----------|
| Over-voltage on 2516 (VPP > 25V) | check_dispatch.py invariant (0, 25000) blocks; firmware over-voltage guard blocks (CTRL_VPP_REGULATOR_ENABLE gated by vpp_mv < current measured) |
| FLAG_CAN_ERASE set on UV-EPROM (triggers unintended erase attempt) | `electrical.type = "UV-EPROM"` → condition excludes it; confirmed by `test_convert_uv_eprom_no_flag_can_erase` |
| User-override entry bypassing VPP safety gate | SR-1 checklist + operator sign-off (D-01); manual review is the compensating control |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | TMS2516 nominally requires VCC=25V during programming (not just VPP=25V) | §2516 Datasheet Research | If this is wrong and VCC=5V is sufficient, Phase 83 programming at 5V VCC + 22.4V VPE is more likely to succeed |
| A2 | TMS2516 programming pulse is nominally 50ms per datasheet (500µs in DB is empirical for 2716-class) | §2516 Datasheet Research | If chip needs longer pulses, the 20× retry ceiling in firmware may be insufficient at marginal voltage |
| A3 | TMS2516 is pin-compatible with Intel 2716 for the DIP24_2716 pinout (read-compatible) | §2516 Datasheet Research | If pin assignment differs from Intel 2716, the read would produce garbage or not connect |
| A4 | flash4_write_init reads FLAG_CAN_ERASE the same way as eprom_write_init | §DB-02 Re-Audit | If flash4 ignores the flag, W29C020/W29C040 would write to non-blank chips without erase, producing verify failures |
| A5 | `firestarter blank-check` exits 0 if blank (all-0xFF), exits 1 if non-blank | §Pattern 2 | If the exit code semantics differ, the bench protocol scripts above need adjustment |

**A4 mitigation note:** The FEATURES.md v1.15 research states: "`FLAG_CAN_ERASE` controls whether
`flash4_write_init` calls `flash4_erase_execute`." This is a design claim from the milestone
research, not directly verified in this session. The live test (`W29C040 flags=0x2`) confirms the
HOST correctly sets the flag; the FIRMWARE behavior is assumed consistent with the flag semantics.
The Phase 82 bench validation of W29C040 will provide the definitive silicon-level confirmation.

**If this table is empty:** It is not empty — see A1–A5 above.

---

## Open Questions

1. **FM1608 algorithm discrepancy**
   - What we know: DB shows `algorithm=40` (decimal; 0x28). `configure_sram` dispatches on
     `protocol ∈ {0x0E, 0x27, 0x28, 0x29}`. 0x28 = 40 decimal — consistent.
   - What's unclear: Some sources referenced `protocol=0x40` (64 decimal). FEATURES.md says
     `algorithm: 40 (0x28)`. These are the same number (0x28 = 40). No discrepancy — but verify
     `firestarter info FM1608` shows `algorithm: 40 (0x28)` before bench.
   - Recommendation: Run `firestarter info FM1608` as step 1 of the FM1608 bench task; confirm
     algorithm=40 and dispatch=configure_sram before attempting any read.

2. **Reseat/retry commands for anomaly handling (D-06)**
   - What we know: D-07 says up to 2 reseat+retry cycles. The bench operator physically reseats
     the chip.
   - What's unclear: Is there a `--retry` flag in the CLI, or is the retry protocol purely manual
     (re-run `firestarter read` after reseating)?
   - Recommendation: Plan as manual retry (operator reseats + re-runs `firestarter read`). No CLI
     retry flag is needed. The planner should document this as an explicit operator action in bench
     task steps.

3. **`firestarter blank-check` exact exit code semantics**
   - What we know: The CLI has a `blank-check` command. FEATURES.md documents it.
   - What's unclear: Does it exit 0 for blank and 1 for non-blank, or vice versa?
   - Recommendation: The planner should verify via `firestarter blank-check --help` as the first
     bench task action, or document both exit codes in the bench plan so the operator knows how to
     interpret the result.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 (devcontainer) | host suite (SAFE-02) | ✓ | 3.12 | — |
| pytest + pytest-cov | SAFE-02 | ✓ | current (650 tests green) | — |
| firestarter CLI | bench sweep | ✓ (installed via pip -e .) | 3.0.0b10 area | — |
| Leonardo + USB | bench sweep | ✓ (devcontainer USB passthrough) | — | — |
| RURP Rev 2.0 shield | bench sweep | ✓ (operator-confirmed) | Rev 2.0 | No fallback — this shield only |
| `sha256sum` | evidence capture | ✓ (standard Linux) | — | `python3 -c "import hashlib; ..."` |

**Missing dependencies with no fallback:**
- None — all software dependencies are in place; hardware availability is operator-confirmed.

**RURP Rev 2.0 note:** Operator must confirm Rev 2.0 is mounted (not Rev 2.2 or Rev 0) via
silkscreen — the EEPROM hw_revision byte cannot distinguish revs. [VERIFIED: user_shield_revisions memory]

---

## Sources

### Primary (HIGH confidence) [VERIFIED: live source code]

- `firestarter_app/firestarter/database.py` lines 420–467 (`_map_data`) + lines 562–609
  (`convert_to_programmer`) — FLAG_CAN_ERASE derivation, electrical-type passthrough
- `firestarter_app/firestarter/database.py` lines 200–251 — `_merge_databases`, user-override merge
- `firestarter/src/proms/eprom.cpp` lines 95–111 — `eprom_write_init` FLAG_CAN_ERASE gate
- `firestarter/src/proms/eprom.cpp` lines 143–153 — `eprom_write_execute` VPE enable (write-only)
- `firestarter_app/firestarter/data/pinouts.json` — DIP24_2716 entry (vpp-pin=[21] confirmed)
- `firestarter_app/firestarter/constants.py` line 80 — FLAG_CAN_ERASE = 0x02
- `firestarter/include/firestarter.h` line 60 — FLAG_CAN_ERASE 0x02 (parity confirmed)
- `firestarter_app/tools/build_db.py` line 117 — RURP_VPP_CEILING_MV = 25000
- `firestarter_app/tools/check_dispatch.py` line 79 — `configure_eprom: (0, 25000)` invariant
- `firestarter_app/tests/test_eprom_operations.py` line 135 — `test_init_phase_data_frames_not_acked`
- `firestarter_app/tests/test_database_conversion.py` lines 80–104 — FLAG_CAN_ERASE tests
- `firestarter_app/firestarter/data/chip_database.json` — live grep confirming 2516 absent
- Python3 live query (2026-06-23) — W29C040/W29C020/SST39SF040 flags=0x2 confirmed
- Host test suite run (2026-06-23) — 650 passed in 31.67s

### Secondary (MEDIUM confidence) [CITED: project planning artifacts]

- `.planning/phases/81-2516-db-entry-non-destructive-read-sweep/81-CONTEXT.md` — locked decisions D-01..D-11
- `.planning/research/ARCHITECTURE.md` — 2516 user-override flow diagram, component table
- `.planning/research/FEATURES.md` — per-chip expected behavior, flag semantics
- `.planning/research/PITFALLS.md` — 12 pitfalls with recovery strategies
- `.planning/research/STACK.md` — reusable stack, exact CLI commands
- `.planning/research/SUMMARY.md` — milestone research flags

### Tertiary (LOW confidence) [ASSUMED: training knowledge]

- TMS2516 datasheet specifics (VCC=25V programming requirement, nominal pulse timing)
- 2516 pinout compatibility with Intel 2716 (confirmed consistent with FEATURES.md but not
  verified against a datasheet in this session)

---

## Metadata

**Confidence breakdown:**
- DB-02 FLAG_CAN_ERASE re-audit: HIGH — verified live against production code + runtime result
- 2516 DB entry schema: HIGH — all fields verified against live DB, pinouts.json, check_dispatch.py
- 2516 datasheet facts: MEDIUM — training knowledge consistent with project research; silicon-level
  proof deferred to Phase 83
- Read sweep mechanics: HIGH — commands exist and are exercised in prior phases
- Test gap (D-05): HIGH — grep-confirmed absence of W29C040 FLAG_CAN_ERASE test

**Research date:** 2026-06-23
**Valid until:** 2026-07-23 (stable — no fast-moving dependencies)
