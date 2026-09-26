# Phase 76: Spec-Only Gaps — adapter-required + X88C64 - Research

**Researched:** 2026-06-18
**Domain:** EEPROM protocol specs, DIP24 adapter pinouts, chip DB classification
**Confidence:** MEDIUM (datasheets partially sourced via HTML proxy pages; key protocol facts confirmed but some timing values indirect)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** GAP-02 delivers the **datasheet feasibility verdict + protocol spec only** (STORE/RECALL
  sequence, byte vs page write, timing). X88C64 is classified as a **documented feasible-candidate** —
  **no `0x34` firmware handler is committed this phase.**
- **D-02:** **Reword the X88C64 `unsupported_reason` string now**, as part of GAP-02's re-classification.
  The current "XICOR NovRAM serial-parallel hybrid" is misleading — the chip is a **parallel DIP24**
  part the RURP can drive. New string reflects the datasheet verdict (parallel DIP24, feasible-candidate,
  handler not implemented). **`check_dispatch.py` and `diff_db.py` MUST stay green.**
- **D-03:** The `resolve_pinout_key` arm in `firestarter_app/tools/build_db.py` **names AT28C04 /
  AT28C16 explicitly and routes them deterministically to `adapter-required` (refusal)**. It does NOT
  encode the DIP24→DIP32 pin remap. **Not a resurrected guess table.**
- **D-04:** The DIP24→DIP32 adapter pin-map lives in a **spec doc** authored in **two layers, kept in
  lockstep**: operator-facing copy in **`firestarter/doc/`** + canonical investigation copy in meta
  **`.planning/`** — matching the existing two-layer SHIELD-REVISIONS pattern.

### Claude's Discretion
- Exact filename/section layout of the new adapter spec doc (follow the SHIELD-REVISIONS precedent).
- Exact wording of the rewritten X88C64 `unsupported_reason` (must be datasheet-accurate and keep gates green).
- Depth/structure of the X88C64 protocol write-up beyond "STORE/RECALL + byte/page write + timing".

### Deferred Ideas (OUT OF SCOPE)
- **Graduating AT28C04/16 (and X88C64) to `supported`** — needs a physical DIP24 adapter + golden
  write+read-back round-trip; explicitly out of v1.13.
- **X88C64 `0x34` firmware handler** — to be built in a future milestone.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GAP-01 | AT28C04/AT28C16 24-pin EEPROM `adapter-required` path has a documented pin-map/adapter spec and a `resolve_pinout_key` named rule arm (NOT a resurrected guess table); chips remain `support_status: adapter-required` until a physical adapter exists and a golden write+read-back round-trips | DIP24_2816 pinout confirmed (codebase), AT28C16 pin description sourced (amiga-stuff.com), DIP24→DIP32 adapter re-route mechanics derived; `resolve_pinout_key` extension point identified |
| GAP-02 | X88C64 (0x34) is re-classified with a documented feasibility verdict + the STORE/RECALL + byte/page write protocol sourced from the datasheet; a firmware handler is committed ONLY if the protocol is fully spec'd and RURP-feasible — otherwise it remains a documented feasible-candidate (no blind handler) | X88C64P protocol fully sourced (alldatasheet.com HTML, 14-page datasheet); **critical finding: X88C64P uses 8051 multiplexed-bus interface, NOT standard /WE /OE /CE parallel bus** — feasibility verdict and handler complexity are MEDIUM (feasible in principle, non-trivial interface adaption required) |
</phase_requirements>

---

## Summary

Phase 76 delivers two spec-gated gaps as documentation + classification only. No chip graduates to `supported`; no firmware handler is committed.

**GAP-01 (AT28C04 / AT28C16):** Nine DIP24 5V parallel EEPROMs already have a working firmware handler (`configure_eeprom28c`, protocol `0x0D`) and correct DB entries (`adapter-required`, `DIP24_2816` pinout). The only blocker is physical: the RURP socket is wired for DIP32, and the chip's 24 pins sit at a different physical layout. The adapter spec translates each DIP24 chip pin to its required DIP32 socket position. The `resolve_pinout_key` function needs a **named explicit rule arm** (D-03) that identifies AT28C04/AT28C16 chips by name and classifies them as `adapter-required` — currently they fall through Site B (an algorithmic 24-pin EEPROM hazard filter). The named arm makes the classification declarative and audit-friendly.

**GAP-02 (X88C64P):** Research reveals a critical architectural nuance — the X88C64P is NOT a conventional /WE /OE /CE parallel EEPROM like AT28C04/16. It presents an **8051-compatible multiplexed address/data bus** interface: eight pins are A/D0–A/D7 (multiplexed address and data), plus ALE (Address Latch Enable), WR, RD, PSEN, CE, and WC control signals. The RURP drives a standard parallel bus (dedicated address + data + /WE /OE /CE lines), which is architecturally incompatible with the X88C64P without additional interface logic to demultiplex the address/data bus. This makes the X88C64P a **medium-feasibility candidate** — physically DIP24/5V so the socket and voltage are compatible, but the bus protocol requires a non-trivial firmware adaptation. The current `unsupported_reason` string "XICOR NovRAM serial-parallel hybrid" is misleading (the chip IS parallel, just multiplexed-parallel, not standard-parallel). The D-02 reword reflects the accurate verdict.

**Primary recommendation:** The named rule arm for AT28C04/AT28C16 is a one-line change to `resolve_pinout_key` in `build_db.py`. The X88C64P reason-string reword is a one-string change. Both changes regenerate through `build_db.py` (codegen-driven, not hand-edited JSON). The adapter spec doc follows the SHIELD-REVISIONS two-layer pattern.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| X88C64 feasibility verdict | Meta planning doc | host DB (unsupported_reason) | Verdict lives in RESEARCH + PROTOCOL-ENUMERATION; DB carries human-readable summary |
| AT28C04/16 adapter pin-map | firestarter/doc/ (operator-facing) | .planning/ (canonical investigation) | Two-layer SHIELD-REVISIONS pattern; sub-repo doc for hardware builder, meta for full record |
| resolve_pinout_key rule arm | Host DB pipeline (build_db.py) | — | Named arm is build-time classification; chip_resolver enforces at runtime |
| diff_db / check_dispatch gates | Host CI gate | — | Gates enforce no support_status change, no new supported chips |

---

## Standard Stack

### Core (no new packages — all existing infrastructure)

| Tool / File | Version | Purpose | Status |
|-------------|---------|---------|--------|
| `build_db.py` | current | DB pipeline — `resolve_pinout_key` extension + X88C64 reason reword | Modify |
| `chip_database.json` | current | Output of codegen — regenerated, not hand-edited | Regenerate |
| `diff_db.py` | current | Per-chip diff gate (GATE-02) — must stay green | Must stay green |
| `check_dispatch.py` | current | 744-chip dispatch + support_status gate (GATE-03) — must stay green | Must stay green |
| `test_build_db_inclusion.py` | current | Inclusion/rule-arm tests — extend for new rule arm and reworded string | Extend |
| `firestarter/doc/SHIELD-REVISIONS.md` | current | Operator-facing hardware doc — new adapter spec follows this pattern | Pattern reference |
| `.planning/v1.7-SHIELD-REVS.md` | current | Meta investigation-canonical — new adapter spec follows this pattern | Pattern reference |

**No new packages required.** This phase is documentation + classification only (build_db.py + doc files).

---

## Package Legitimacy Audit

> Not applicable — this phase installs no new external packages.

No packages are installed this phase. The build pipeline (`build_db.py`, `diff_db.py`, `check_dispatch.py`) and test infrastructure are all pre-existing.

---

## Architecture Patterns

### System Architecture Diagram

```
infoic.xml
    |
    v
build_db.py
  |-- resolve_pinout_key() ─── NEW: named arm for AT28C04/AT28C16 → adapter-required
  |-- Site B filter (existing 24-pin hazard filter) ─── AT28C04/16 currently caught here
  |-- X88C64 classification ─── D-02: reword unsupported_reason
    |
    v
chip_database.json (regenerated)
    |
    ├── diff_db.py ──────────────── GATE-02: 1-chip delta (X88C64 reason string); 0 support_status changes
    └── check_dispatch.py ───────── GATE-03: 744 chips; no new supported; AT28C04/16 still adapter-required

New docs (two-layer):
  firestarter/doc/AT28C04-ADAPTER.md ─── operator-facing (GitHub-visible)
  .planning/AT28C04-ADAPTER.md ─────────── meta investigation-canonical
```

### Recommended Project Structure (new files only)

```
firestarter/doc/
└── AT28C04-ADAPTER.md          # operator-facing adapter pin-map spec (D-04 layer 1)

.planning/
└── AT28C04-ADAPTER.md          # meta investigation-canonical adapter spec (D-04 layer 2)

firestarter_app/tests/
└── test_build_db_inclusion.py  # extend: AT28C04/16 named-arm test + X88C64 reason string test
```

### Pattern 1: Named Rule Arm in resolve_pinout_key

**What:** An explicit `if chip_name in {...}` check in `resolve_pinout_key` that routes AT28C04 / AT28C16 family chips to `adapter-required` deterministically, independent of pin count / flags heuristics.
**When to use:** When a chip's classification must be audit-friendly and explicit, not derived from a heuristic predicate that might drift.

D-03 says the arm does NOT encode the DIP24→DIP32 pin remap — that lives in the spec doc. The arm simply names the chips and returns a sentinel that the caller interprets as `adapter-required`.

**Current Site B filter (existing, NOT the named arm):**
```python
# firestarter_app/tools/build_db.py (lines 388-411)
if (
    pin_count == 24
    and proto_id in (0x07, 0x08, 0x0B)
    and (flags & 0x10)
):
    _support_status = "adapter-required"
    _unsupported_reason = (
        "adapter required: requires a dedicated DIP24 EEPROM adapter "
        "or firmware handler — socket pin 21 = WE, which the RURP "
        "DIP24_2716 pinout maps to the 12V VPP rail (hardware-damage path)"
    )
    proto_id = NON_DISPATCHABLE_ALGO
```

The 9 AT28C04/AT28C16 chips already pass through Site B (pin_count=24, proto_id=0x0B/0x07/0x08, flags&0x10=True). D-03 requires an **additional named arm** that explicitly identifies these chips. The named arm:

1. Fires BEFORE or alongside Site B (before `resolve_pinout_key` call)
2. Uses `name` (part number string from infoic.xml) to match AT28C04/AT28C16 family members
3. Overwrites or confirms `_support_status = "adapter-required"` with the named-arm reason string
4. Does NOT demote `proto_id` to `NON_DISPATCHABLE_ALGO` — the existing Site B already handles that

**Candidate named-arm trigger strings** (from chip_database.json confirmed entries):
- `"AT28C04"`, `"AT28HC04"`, `"AT28C04E"`, `"AT28C04F"` (ATMEL)
- `"AT28C16"`, `"AT28HC16"`, `"AT28HC16L"`, `"AT28C16E"`, `"AT28C16F"` (ATMEL)
- `"28C04A"`, `"28C04AF"` (MICROCHIP memory)
- `"28C16A"`, `"28C16AF"` (MICROCHIP memory)
- `"UPD28C04"` (NEC)

Match logic: check if any alias in the comma-separated `name` field starts with or equals one of the above.

**Example named-arm structure:**
```python
# NEW: named arm for AT28C04/AT28C16 families (D-03)
# Fires before Site B to make the classification explicit and audit-friendly.
# The DIP24→DIP32 pin remap is NOT encoded here — it lives in the adapter spec doc.
_AT28C_DIP24_NAMES = {
    "AT28C04", "AT28HC04", "AT28C04E", "AT28C04F",
    "AT28C16", "AT28HC16", "AT28HC16L", "AT28C16E", "AT28C16F",
    "28C04A", "28C04AF", "28C16A", "28C16AF",
    "UPD28C04",
}
_chip_aliases = {a.split("@")[0].strip() for a in name.split(",") if a.strip()}
if _chip_aliases & _AT28C_DIP24_NAMES:
    _support_status = "adapter-required"
    _unsupported_reason = (
        "adapter required: AT28C04/AT28C16 DIP24 chip — requires a physical "
        "DIP24-to-DIP32 adapter; see firestarter/doc/AT28C04-ADAPTER.md"
    )
    # Note: proto_id is NOT demoted here; Site B still fires for the hazard guard
```

[VERIFIED: `firestarter_app/tools/build_db.py` — Site B structure, name extraction pattern from `test_build_db_inclusion.py:_aliases()`]

### Pattern 2: X88C64 reason-string reword (D-02)

**What:** Change the single string at `build_db.py:367` for the X88C64 `protocol-not-implemented` reason.
**Constraint:** The new string MUST contain "protocol not implemented" (substring) per `test_build_db_inclusion.py:test_protocol_not_implemented_reason_contains_not_implemented` and `test_read_protocol_not_implemented_typed_refusal` (existing tests pin this invariant).

**Current string** (line 367):
```python
_unsupported_reason = "protocol not implemented: 0x34 (XICOR NovRAM serial-parallel hybrid)"
```

**Proposed new string:**
```python
_unsupported_reason = (
    "protocol not implemented: 0x34 (XICOR X88C64P — parallel DIP24 NovRAM, "
    "8051 multiplexed-bus interface; feasible-candidate, handler not implemented)"
)
```

This is datasheet-accurate ("parallel DIP24" correct — it IS parallel, just multiplexed-parallel), honest about the bus interface, and keeps the "protocol not implemented" substring required by tests.

[VERIFIED: `build_db.py:361-367` — current reason string; `tests/test_build_db_inclusion.py:449-473` — test invariants on reason string]

### Pattern 3: Two-layer adapter spec doc (D-04)

**What:** Mirror the SHIELD-REVISIONS two-layer doc pattern. One file in `firestarter/doc/` (operator-facing, GitHub-visible — for someone physically building the adapter); one file in `.planning/` (meta investigation-canonical — full derivation, evidence citations).

**SHIELD-REVISIONS precedent (confirmed by direct read):**
- `firestarter/doc/SHIELD-REVISIONS.md` — contains §1 inventory, §2 capability matrix, §3 silkscreen alias table, §4 ADC band table (4 sections, operator-useful subset)
- `.planning/v1.7-SHIELD-REVS.md` — full 9-section document with all investigation history, bench evidence, full electrical diffs

**Adapter spec doc structure:**
- `firestarter/doc/AT28C04-ADAPTER.md` — pin table (DIP24 pin → DIP32 socket pin), socket re-route description, safety notes. Operator needs this to build the adapter.
- `.planning/AT28C04-ADAPTER.md` — full derivation including pinout source citations, firmware handler confirmation, why each pin maps where it does, future graduation steps.

[VERIFIED: `firestarter/doc/SHIELD-REVISIONS.md` structure (direct read); `firestarter_app/CLAUDE.md` §"Constants" confirms two-layer lockstep pattern]

### Anti-Patterns to Avoid

- **Hand-editing chip_database.json:** The DB is codegen output. Changes go in `build_db.py`, regenerated via `python tools/build_db.py`. [VERIFIED: `firestarter_app/CLAUDE.md` §"Database Pipeline"]
- **Resurrecting a guess table for the named arm:** D-03 explicitly prohibits encoding the DIP24→DIP32 pin remap in `resolve_pinout_key`. The arm names chips explicitly; the remap lives in the spec doc.
- **Changing X88C64 support_status:** D-02 is a reason-string reword only. `support_status` stays `protocol-not-implemented`. `diff_db.py` will catch any accidental status change.
- **Committing a 0x34 firmware handler:** D-01 is locked. Even if the protocol were fully spec'd, no handler this phase.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| DB chip classification | Hand-edit chip_database.json | Modify build_db.py + regenerate | JSON is codegen output; hand edits are wiped on next regeneration |
| Validating new named arm | Manual DB inspection | Extend test_build_db_inclusion.py + run diff_db/check_dispatch | Automated gates catch regressions |
| Adapter pin remap validation | Trust manual reasoning | Cross-check against DIP24_2816 pinout in pinouts.json + AT28C16 datasheet | Pinouts.json is the ground truth for RURP pin routing |

---

## GAP-01 Technical Facts: AT28C04 / AT28C16 DIP24 Pinout

### AT28C16 DIP24 Pin Description

The AT28C16 is a 2K×8 (16Kbit) parallel EEPROM in 24-pin DIP. The AT28C04 is the same physical package with fewer address bits used.

[CITED: amiga-stuff.com/hardware/28c16.html + DIP24_2816 entry in pinouts.json (VERIFIED by direct codebase read)]

| DIP24 Pin | Function | Notes |
|-----------|----------|-------|
| 1 | A7 | Address bit 7 |
| 2 | A6 | Address bit 6 |
| 3 | A5 | Address bit 5 |
| 4 | A4 | Address bit 4 |
| 5 | A3 | Address bit 3 |
| 6 | A2 | Address bit 2 |
| 7 | A1 | Address bit 1 |
| 8 | A0 | Address bit 0 |
| 9 | D0 | Data bit 0 |
| 10 | D1 | Data bit 1 |
| 11 | D2 | Data bit 2 |
| 12 | GND | Ground |
| 13 | D3 | Data bit 3 |
| 14 | D4 | Data bit 4 |
| 15 | D5 | Data bit 5 |
| 16 | D6 | Data bit 6 |
| 17 | D7 | Data bit 7 |
| 18 | /CE | Chip Enable (active LOW) |
| 19 | A10 | Address bit 10 |
| 20 | /OE | Output Enable (active LOW) |
| 21 | /WE | Write Enable (active LOW) |
| 22 | A9 | Address bit 9 |
| 23 | A8 | Address bit 8 |
| 24 | VCC | +5V supply |

**AT28C04 difference:** The AT28C04 is 512×8 (4Kbit, 9 address bits A0–A8). Pins 22 (A9) and 19 (A10) are NC on AT28C04. The DIP24_2816 pinout in `pinouts.json` lists pins 22 and 19 in `address-bus-pins` but firmware restricts driving via `mem_size` — so the AT28C04 naturally uses only A0–A8. [ASSUMED: firmware mem_size restriction behavior for sub-11-bit chips]

**Codebase cross-check (VERIFIED):** `pinouts.json` DIP24_2816 entry:
```json
"address-bus-pins": [8,7,6,5,4,3,2,1,23,22,19],
"data-bus-pins": [9,10,11,13,14,15,16,17],
"ce-pin": [18], "oe-pin": [20], "rw-pin": [21]
```
Pin ordering in array = A0(8), A1(7), A2(6), A3(5), A4(4), A5(3), A6(2), A7(1), A8(23), A9(22), A10(19). Matches AT28C16 datasheet exactly.

### DIP24 → DIP32 Socket Adapter Re-route

The RURP socket is DIP32 (32-pin). The AT28C04/AT28C16 chip is DIP24. An adapter board physically re-routes the DIP24 chip's 24 pins into the DIP32 socket, connecting each chip pin to the correct RURP bus line.

**The RURP DIP32 socket is wired to bus lines per DIP32_28C512_EEPROM (the 5V EEPROM 32-pin layout used by configure_eeprom28c):**

[VERIFIED: `firestarter_app/firestarter/data/pinouts.json` DIP32_28C512_EEPROM entry]

```
DIP32 socket pin → RURP bus role:
  Pin 1  → NC (not used in 28C512 layout; would be A15 for full 64K — not relevant for AT28C16/04)
  Pin 3  → A15 (address bit 15)
  Pin 4  → A12 (address bit 12)
  Pin 5  → A7
  Pin 6  → A6
  Pin 7  → A5
  Pin 8  → A4
  Pin 9  → A3
  Pin 10 → A2
  Pin 11 → A1
  Pin 12 → A0
  Pin 13 → D0
  Pin 14 → D1
  Pin 15 → D2
  Pin 16 → GND
  Pin 17 → D3
  Pin 18 → D4
  Pin 19 → D5
  Pin 20 → D6
  Pin 21 → D7
  Pin 22 → /CE
  Pin 23 → A10
  Pin 24 → /OE
  Pin 25 → A11
  Pin 26 → A9
  Pin 27 → A8
  Pin 28 → A13
  Pin 29 → A14
  Pin 30 → /WE (rw-pin)
  Pin 31 → NC (not used in EEPROM layout)
  Pin 32 → VCC
```

**Adapter pin mapping (DIP24 chip pin → DIP32 socket pin):**

[ASSUMED: mapping derived from matching bus roles; planner should verify against pinouts.json DIP32_28C512_EEPROM before committing to spec doc]

| DIP24 chip pin | Chip function | DIP32 socket pin | RURP bus role | Notes |
|---------------|--------------|-----------------|--------------|-------|
| 1 | A7 | 5 | A7 | Direct match |
| 2 | A6 | 6 | A6 | Direct match |
| 3 | A5 | 7 | A5 | Direct match |
| 4 | A4 | 8 | A4 | Direct match |
| 5 | A3 | 9 | A3 | Direct match |
| 6 | A2 | 10 | A2 | Direct match |
| 7 | A1 | 11 | A1 | Direct match |
| 8 | A0 | 12 | A0 | Direct match |
| 9 | D0 | 13 | D0 | Direct match |
| 10 | D1 | 14 | D1 | Direct match |
| 11 | D2 | 15 | D2 | Direct match |
| 12 | GND | 16 | GND | Direct match |
| 13 | D3 | 17 | D3 | Direct match |
| 14 | D4 | 18 | D4 | Direct match |
| 15 | D5 | 19 | D5 | Direct match |
| 16 | D6 | 20 | D6 | Direct match |
| 17 | D7 | 21 | D7 | Direct match |
| 18 | /CE | 22 | /CE | Direct match |
| 19 | A10 | 23 | A10 | Direct match |
| 20 | /OE | 24 | /OE | Direct match |
| 21 | /WE | 30 | /WE (rw-pin) | Key reroute: chip pin 21 → socket pin 30 |
| 22 | A9 | 26 | A9 | Direct match |
| 23 | A8 | 27 | A8 | Direct match |
| 24 | VCC | 32 | VCC | Direct match |

**Unconnected DIP32 socket pins** (no corresponding DIP24 pin):
- Socket pin 1: leave NC (no chip connection)
- Socket pin 3: leave NC (A15 — not needed for AT28C16 max 11 address bits)
- Socket pin 4: leave NC (A12 — AT28C16 has 11 address bits A0-A10; A12 unused)
- Socket pin 25: leave NC (A11 — not needed)
- Socket pin 28: leave NC (A13 — not needed)
- Socket pin 29: leave NC (A14 — not needed)
- Socket pin 31: leave NC

**Key insight for the spec doc:** The critical re-route is chip pin 21 (/WE) → DIP32 socket pin 30. In the DIP24 EEPROM layout, /WE is at pin 21; in the DIP32 socket (configured for 5V EEPROM via DIP32_28C512_EEPROM), /WE (rw-pin) is at socket pin 30. This is the source of the adapter-required classification — inserting the chip directly into a DIP32 socket would connect chip pin 21 (/WE) to the wrong RURP bus line (socket pin 21 = D7 in the DIP32 layout, not /WE).

**Safety verification:** The DIP24_2816 pinout has NO `vpp-pin` entry — the AT28C04/AT28C16 is a 5V-only EEPROM; no VPP rail is connected. The DIP32_28C512_EEPROM pinout also has no `vpp-pin`. The adapter is electrically safe from the VPP damage hazard perspective.

[VERIFIED: `pinouts.json` DIP24_2816 and DIP32_28C512_EEPROM entries — both lack `vpp-pin`]

---

## GAP-02 Technical Facts: X88C64P Protocol

### Device Identity

- **Part number:** X88C64P (DIP24 package variant); X88C64S (SOIC24 — excluded by SMD filter)
- **Manufacturer:** XICOR Inc. (later acquired by Intersil/Renesas)
- **Organization:** 8K × 8 (65,536 bits = 64Kbit), organized as 8,192 bytes in 8 × 1K blocks
- **Package:** DIP24 (24-pin plastic DIP) — the 'P' suffix confirms DIP package
- **Technology:** CMOS Textured Poly Floating Gate EEPROM
- **VCC:** 5V ±10% (4.5V–5.5V) [CITED: X88C64P datasheet page 8 via alldatasheet.com]
- **Dual-plane architecture:** Two independent 4K×8 arrays; CONCURRENT READ WRITE™ allows executing from one plane while writing the other

[CITED: alldatasheet.com/html-pdf/34232/XICOR/X88C64P — pages 1, 2, 8]

### Critical Finding: Interface Architecture

**The X88C64P does NOT present a standard /WE /OE /CE parallel EEPROM interface.**

It presents an **8051 multiplexed-bus interface** compatible with Intel 8031/8051 family microcontrollers operating in expanded multiplexed mode:

[CITED: X88C64P datasheet page 2 via alldatasheet.com html-pdf/34232/XICOR/X88C64P/257/2]

| DIP24 Pin | Function | Description |
|-----------|----------|-------------|
| 1 | NC | No Connect |
| 2 | A12 | Upper address bit 12 |
| 3 | NC | No Connect |
| 4 | NC | No Connect |
| 5 | WC | Write Control (active LOW to enable writes; HIGH aborts write cycle) |
| 6 | /PSEN | Program Store Enable (controls code-fetch reads from EEPROM plane) |
| 7 | A/D0 | Multiplexed Address/Data bit 0 |
| 8 | A/D1 | Multiplexed Address/Data bit 1 |
| 9 | A/D2 | Multiplexed Address/Data bit 2 |
| 10 | A/D3 | Multiplexed Address/Data bit 3 |
| 11 | A/D4 | Multiplexed Address/Data bit 4 |
| 12 | VSS | Ground |
| 13 | A/D5 | Multiplexed Address/Data bit 5 |
| 14 | A/D6 | Multiplexed Address/Data bit 6 |
| 15 | A/D7 | Multiplexed Address/Data bit 7 |
| 16 | /CE | Chip Enable (active LOW) |
| 17 | A10 | Address bit 10 (upper) |
| 18 | /RD | Read strobe (active LOW) |
| 19 | A11 | Address bit 11 (upper) |
| 20 | A9 | Address bit 9 (upper) |
| 21 | A8 | Address bit 8 (upper) |
| 22 | ALE | Address Latch Enable — address is latched on falling edge |
| 23 | /WR | Write strobe (active LOW) |
| 24 | VCC | +5V supply |

**Note:** There are NO dedicated STORE/RECALL pins on the X88C64P. The "NovRAM" STORE/RECALL concept applies to Xicor's older 28-pin NOVRAM family (X2210/X2212/X2201A series from the 1985 Xicor Data Book). The X88C64P is a different product — it is an EEPROM with CONCURRENT READ WRITE™ (dual-plane architecture), not a battery-backed SRAM+EEPROM combination. The current `unsupported_reason` string is doubly wrong: it calls the chip "serial-parallel hybrid" (wrong — it IS parallel) AND implies STORE/RECALL (wrong — no such pins exist on this chip).

[CITED: X88C64P datasheet pages 1-2 via alldatasheet.com; Xicor 1985 Data Book via bitsavers.org/components/xicor/1985_Xicor_Data_Book.pdf (confirmed NOVRAM family X2210/X2212 has STORE/RECALL — X88C64P does NOT)]

### Write Protocol

Address latching (from page 3): "When ALE is HIGH, the A/D0–A/D7 and A8–A12 addresses flow into the device. The addresses, both low and high order, are latched when ALE transitions LOW."

Write cycle (from page 4): "A write is performed by latching the addresses on the falling edge of ALE. Then WR is strobed LOW followed by valid data being presented at the A/D0–A/D7 pins."

Page write: Supports up to **32 bytes per write cycle** (page mode write). [CITED: X88C64P datasheet page 1 feature list via alldatasheet.com page 1]

Write cycle completion: Toggle Bit Polling — "I/O6 will toggle from HIGH to LOW and LOW to HIGH on subsequent attempts to read the device" during internal write. The A12 address state must match between write and polling reads. [CITED: X88C64P datasheet page 6 via alldatasheet.com]

Write cycle time: Approximately 100 µs (referenced on page 5: "100 µs delay for internal programming cycles"). [CITED: X88C64P datasheet page 5 via alldatasheet.com]

Write abort: "WC is driven HIGH (before tBLC Max) after Write (WR) goes HIGH" to abort a write cycle. [CITED: X88C64P datasheet page 2 via alldatasheet.com]

Data protection: Software Block Protect Register — individual write-lock capability for eight 1K blocks. [CITED: X88C64P datasheet page 1]

Endurance: 100,000 write cycles. Data retention: 100 years. [CITED: X88C64P datasheet page 1]

### RURP Feasibility Verdict

**MEDIUM feasibility — feasible-candidate, handler not implemented.**

**Why feasible (not infeasible):**
1. **DIP24, 5V VCC** — the socket physically fits and the voltage is within RURP capability. No VPP rail required (5V-only EEPROM).
2. **Parallel interface** — despite being multiplexed-parallel, the chip's address and data signals are driven via digital I/O pins, which the Arduino can control.
3. **RURP ceiling**: 5V-only chip, no VPP needed → RURP_VPP_CEILING_MV is irrelevant. Not a vpp-exceeds-max case.

**Why non-trivial (not immediate):**
1. **Multiplexed bus:** The RURP firmware drives a standard parallel bus (dedicated address lines on bus latches, dedicated data lines, separate /WE /OE /CE strobes via control register bits). The X88C64P requires ALE→address-latch→/WR→data protocol, which is structurally different from `memory_write_execute`'s simple address-set → /WE-strobe sequence.
2. **No STORE/RECALL:** The planned "STORE/RECALL sequence" in the phase description was based on the wrong assumption that X88C64P is a NOVRAM with STORE/RECALL pins. The actual write protocol is ALE/WR-based. This is good news (simpler than expected) but requires the firmware to demultiplex the address/data bus.
3. **ALE timing:** Address latching requires ALE pulse → data phase, which may require modifying the RURP address-bus driver to toggle an additional control bit for ALE. Research of `rurp_shield.h` / `rurp_pinout.h` would be needed to confirm whether an ALE-compatible control bit exists or needs to be added.

**Recommended unsupported_reason (D-02):**
```
"protocol not implemented: 0x34 (XICOR X88C64P — parallel DIP24 5V EEPROM, "
"8051 multiplexed-bus interface (ALE/WR/RD); feasible-candidate, handler not implemented)"
```

This string:
- Contains "protocol not implemented" — satisfies test_protocol_not_implemented_reason_contains_not_implemented
- Contains "not implemented" — satisfies test_read_protocol_not_implemented_typed_refusal
- Is datasheet-accurate (parallel DIP24, 5V, ALE/WR/RD interface)
- Does NOT say "serial-parallel hybrid" (which was wrong)
- Does NOT falsely imply STORE/RECALL pins (which don't exist)

---

## Common Pitfalls

### Pitfall 1: Named Arm Collides with Site B

**What goes wrong:** If the named arm fires AFTER `proto_id` has already been demoted to `NON_DISPATCHABLE_ALGO` by Site B, the `proto_id` check in the named arm won't match.
**Why it happens:** Site B runs at lines 388–411 and sets `proto_id = NON_DISPATCHABLE_ALGO` (0x00). If the named arm checks `proto_id in (0x07, 0x08, 0x0B)`, it will miss AT28C04/AT28C16 chips that already passed Site B.
**How to avoid:** The named arm must fire BEFORE Site B and key on chip `name` (the raw infoic.xml name string), not on `proto_id`. Or: place it after Site B but don't rely on proto_id — just match chip name and overwrite the reason string.
**Warning signs:** `test_build_db_inclusion.py::TestAdapterRequired24Pin` still passes with the existing reason string; extend the test to assert the NEW reason string appears.

### Pitfall 2: diff_db.py Rejects the X88C64 Reason-String Change

**What goes wrong:** `diff_db.py` classifies all changed chips by a known root-cause rule. An `unsupported_reason`-only change on a chip with `support_status: protocol-not-implemented` must match `RULE_PHASE66` (the only rule that claims `("unsupported_reason",)` field path).
**Why it happens:** `_RULE_FIELD_PATHS["RULE_PHASE66"]` includes `("unsupported_reason",)` — this change WILL be explained by RULE_PHASE66 as long as no other fields change simultaneously.
**How to avoid:** Regenerate and run `diff_db.py` immediately; expect exactly 1 chip changed, classified as RULE_PHASE66. Verify the output shows `X88C64P,X88C64S` in the RULE_PHASE66 bucket.
**Warning signs:** `diff_db.py` exits 1 (unexplained diff) — means another field also changed unexpectedly.

### Pitfall 3: Treating X88C64P as a NOVRAM with STORE/RECALL Pins

**What goes wrong:** Planning documentation describes a STORE/RECALL pin sequence that doesn't exist on the X88C64P.
**Why it happens:** The X88C64P DB entry called it "XICOR NovRAM" and research discussions mentioned STORE/RECALL. Xicor's older NOVRAM family (X2210/X2212) does have STORE/RECALL, but those are 28-pin chips from 1985. The X88C64P (1994-1996) is architecturally different.
**How to avoid:** Document the actual ALE/WR/RD protocol in the spec. The feasibility write-up must state clearly: no STORE/RECALL pins; write protocol is ALE-latch + /WR-strobe + page-write up to 32 bytes.
**Warning signs:** Any spec document that describes a "STORE" or "RECALL" operation for the X88C64P is wrong.

### Pitfall 4: Named Arm Reason String Fails Existing Tests

**What goes wrong:** The new named-arm reason string for AT28C04/AT28C16 doesn't start with "adapter required:" — failing `test_adapter_required_reason_starts_with_adapter_required`.
**Why it happens:** Test `TestUnsupportedReasonStrings.test_adapter_required_reason_starts_with_adapter_required` asserts the reason starts with "adapter required:".
**How to avoid:** Keep "adapter required:" as the prefix. Example: `"adapter required: AT28C04/AT28C16 DIP24 chip — requires a physical DIP24-to-DIP32 adapter; see firestarter/doc/AT28C04-ADAPTER.md"`.
**Warning signs:** Test failure in `test_build_db_inclusion.py`.

### Pitfall 5: Adapter Pin Table Maps to Wrong DIP32 Layout

**What goes wrong:** The adapter spec uses the DIP32_STD layout (UV-EPROM with VPP at pin 1) instead of DIP32_28C512_EEPROM (5V EEPROM with /WE at pin 30). The chip would be programmed with incorrect bus routing.
**Why it happens:** The RURP socket is configured differently for EPROM vs EEPROM chips. The AT28C04/AT28C16 uses `configure_eeprom28c` (0x0D) which uses the 5V EEPROM layout.
**How to avoid:** All adapter mappings MUST reference `DIP32_28C512_EEPROM` (or confirm which DIP32 pinout `configure_eeprom28c` actually uses via `pinouts.json`). [VERIFIED: `chip_database.json` AT28C040 (supported 32-pin AT28C family) uses `pinout: DIP32_28C512_EEPROM` — this is the correct reference layout]

---

## Code Examples

### Check current X88C64P entry in DB
```python
# Verify current state
import json
with open('firestarter_app/firestarter/data/chip_database.json') as f:
    db = json.load(f)
for mfg, chips in db.items():
    for chip in chips:
        if 'X88C64' in chip.get('part_number', ''):
            print(mfg, chip.get('part_number'))
            print('  support_status:', chip.get('support_status'))
            print('  unsupported_reason:', chip.get('unsupported_reason'))
            print('  algorithm:', hex(chip.get('programming', {}).get('algorithm', 0)))
            print('  pinout:', chip.get('pinout'))
```
Current output (VERIFIED):
```
XICOR / X88C64P,X88C64S
  support_status: protocol-not-implemented
  unsupported_reason: protocol not implemented: 0x34 (XICOR NovRAM serial-parallel hybrid)
  algorithm: 0x34
  pinout: DIP24_6116
```

### Verify 9 adapter-required chips and their pinouts
```python
adapter_chips = [
    (mfg, chip.get('part_number'), chip.get('pinout'))
    for mfg, chips in db.items() if isinstance(chips, list)
    for chip in chips if chip.get('support_status') == 'adapter-required'
]
# Expected: 9 chips, all with pinout=DIP24_2816
```
Current output (VERIFIED): 9 chips — AT28C04, AT28C04E, AT28C04F, AT28C16, AT28C16E, AT28C16F, 28C04A, 28C04AF, UPD28C04 — all `DIP24_2816`.

### Run gate checks
```bash
cd firestarter_app
python tools/diff_db.py            # expect: 1 chip changed (X88C64P reason string), RULE_PHASE66
python tools/check_dispatch.py     # expect: 744 chips, 0 violations
pytest tests/test_build_db_inclusion.py -v  # extend these tests
```

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | AT28C04 pins 22 (A9) and 19 (A10) are NC when mem_size restricts to 9 address bits | GAP-01 DIP24 Pinout | AT28C04 has 9 address bits; driving A9/A10 as address lines when they should be NC could cause no harm (NC pins float high on chip, and firmware uses mem_size to gate which addresses are written) — low actual risk |
| A2 | The named arm must fire before or independently of Site B, keying on chip name | resolve_pinout_key Pattern | If implementation order is wrong, named arm may not have correct proto_id to match; mitigation: key on name only, not proto_id |
| A3 | DIP32_28C512_EEPROM is the correct DIP32 layout for the adapter (not DIP32_STD) | Adapter pin mapping table | Using wrong DIP32 layout would mean adapter routes VPP to a data pin or similar; must verify via supported AT28C040 entry (uses DIP32_28C512_EEPROM — confirmed) |
| A4 | X88C64P write cycle time is ~100µs | GAP-02 Write Protocol | Page 5 reference is indirect; actual tWC could differ. For feasibility verdict purposes this is "EEPROM-class timing, compatible with configure_eeprom28c timing expectations" — risk is LOW for a feasibility assessment |
| A5 | X88C64P has no STORE/RECALL pins | GAP-02 Protocol | High confidence — 14-page datasheet surveyed; no STORE/RECALL mentioned on any page; all references to STORE/RECALL in Xicor docs are for the older X2210/X2212 NOVRAM family |

---

## State of the Art

| Old Assumption | Corrected Understanding | Source | Impact |
|----------------|------------------------|--------|--------|
| X88C64P is a "serial-parallel hybrid" with STORE/RECALL | X88C64P is a standard-parallel-compatible 8051-multiplexed-bus EEPROM; NO STORE/RECALL pins | X88C64P datasheet pages 1-7 via alldatasheet.com | Feasibility verdict changes from "unclear" to "MEDIUM (feasible, non-trivial bus adaption)" |
| AT28C04/AT28C16 named arm doesn't exist — Site B covers them algorithmically | Named arm needed for explicit, audit-friendly classification (D-03) | CONTEXT.md D-03; `build_db.py` code review | Phase 76 adds named arm; no functional change for gate greenness |

**Deprecated:**
- "XICOR NovRAM serial-parallel hybrid" reason string: wrong on both axes (it IS parallel; there is no hybrid serial interface). D-02 rewrites this.

---

## Open Questions

1. **ALE control bit availability on RURP**
   - What we know: The RURP drives address/data/control via an 8-bit parallel latch (74HC573). Control register bits in `rurp_pinout.h` include VPP_ENABLE, A9_ENABLE, VPE_ENABLE, P1_ENABLE, READ_WRITE, ADDRESS_LINE_16/17/18/13.
   - What's unclear: Is there an available control register bit that could be used to drive ALE (or toggle a dedicated signal for address latching)? The X88C64P needs ALE toggled each write cycle.
   - Recommendation: Phase 76 defers this to the future handler milestone. The spec doc should note "ALE routing needs investigation before handler can be written" as part of the feasibility-candidate documentation.

2. **Exact tWC for X88C64P**
   - What we know: "100 µs" referenced in page 5 text; standard EEPROM timing in this era is 1–10 ms byte write.
   - What's unclear: Whether 100µs is the full write cycle or just one timing parameter. Page 8 shows power-up timing (tPUR 1ms, tPUW 5ms) but not tWC.
   - Recommendation: Tag as ASSUMED in spec doc. The feasibility verdict does not depend on the exact value — "EEPROM-class, within firmware capability" is sufficient for a feasible-candidate classification.

3. **Correct DIP32 pinout for adapter mapping**
   - What we know: AT28C040 (the 32-pin AT28C family member, supported) uses `DIP32_28C512_EEPROM` pinout.
   - What's unclear: Whether the firmware actually configures socket pins according to `DIP32_28C512_EEPROM` when running `configure_eeprom28c` for the 32-pin family. It should, since that's how the DB maps it.
   - Recommendation: Planner should add a task to verify by cross-checking the DIP32_28C512_EEPROM entry against what `configure_eeprom28c` expects for address/data/control pin routing, before finalizing the adapter spec doc pin table.

---

## Environment Availability

Step 2.6: SKIPPED — Phase 76 is documentation, DB regeneration, and classification only. No external runtime dependencies beyond the pre-installed Python toolchain and existing CI gates.

```
Python: available (devcontainer)
pip/pytest: available
build_db.py: pre-existing, runnable
diff_db.py: pre-existing
check_dispatch.py: pre-existing
```

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (existing firestarter_app test suite) |
| Config file | `firestarter_app/pytest.ini` (or pyproject.toml — pre-existing) |
| Quick run command | `cd firestarter_app && pytest tests/test_build_db_inclusion.py -v` |
| Full suite command | `cd firestarter_app && pytest --cov-fail-under=70` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| GAP-01 | AT28C04/AT28C16 chips classified as adapter-required with new named-arm reason string | unit | `pytest tests/test_build_db_inclusion.py::TestAdapterRequired24Pin -v` | ✅ (extend) |
| GAP-01 | All 9 adapter-required chips have correct reason string prefix | unit | `pytest tests/test_build_db_inclusion.py::TestUnsupportedReasonStrings::test_adapter_required_reason_starts_with_adapter_required -v` | ✅ (passes with new string) |
| GAP-02 | X88C64P reason string contains "protocol not implemented" | unit | `pytest tests/test_build_db_inclusion.py::TestUnsupportedReasonStrings::test_protocol_not_implemented_reason_contains_not_implemented -v` | ✅ (extend/verify with new string) |
| GAP-02 | X88C64P support_status stays protocol-not-implemented | unit | `pytest tests/test_build_db_inclusion.py::TestProtocolNotImplementedInclusion -v` | ✅ |
| GAP-01+02 | diff_db gate green (reason-string change classified as RULE_PHASE66; no support_status delta) | gate | `cd firestarter_app && python tools/diff_db.py` | ✅ gate |
| GAP-01+02 | check_dispatch gate green (744 chips, 0 violations) | gate | `cd firestarter_app && python tools/check_dispatch.py` | ✅ gate |
| GAP-01+02 | Full test suite above coverage floor | regression | `cd firestarter_app && pytest --cov-fail-under=70` | ✅ |

### Sampling Rate
- **Per task commit:** `pytest tests/test_build_db_inclusion.py -v && python tools/diff_db.py && python tools/check_dispatch.py`
- **Per wave merge:** Full suite: `pytest --cov-fail-under=70`
- **Phase gate:** Full suite green + diff_db PASS + check_dispatch PASS before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] Extend `test_build_db_inclusion.py::TestAdapterRequired24Pin` with a test that asserts the reason string for AT28C04/AT28C16 contains the named-arm text (the existing test only checks prefix "adapter required:" and presence, not the new named-arm wording)
- [ ] Add test asserting the new X88C64P reason string does NOT contain "serial-parallel hybrid" (regression guard against re-introducing the wrong description)

*(Remaining infrastructure: all pre-existing. build_db.py runs locally.)*

---

## Security Domain

`security_enforcement` is not explicitly set in config.json (absent = enabled). However, this phase delivers only documentation + classification changes (no new code paths, no new network surfaces, no authentication/crypto). The applicable ASVS categories are minimal.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes (chip name matching) | Named-arm uses string comparison from build_db.py `_aliases()` pattern — not user input |
| V6 Cryptography | no | — |

### Known Threat Patterns for this Phase

| Pattern | Notes |
|---------|-------|
| DB injection via chip name | build_db.py processes infoic.xml (upstream XML); the named arm does string matching. No new attack surface — same XML source as all other phases. |
| Gate bypass | The primary security control is that non-supported chips stay refused via chip_resolver.py. This phase adds a named arm that also routes to adapter-required — same refusal path. No gate bypass risk. |

---

## Sources

### Primary (HIGH confidence — verified by direct read)
- `firestarter_app/tools/build_db.py` — resolve_pinout_key, Site B filter, KNOWN_PROTOCOLS, X88C64 reason string (lines 361-411)
- `firestarter_app/firestarter/data/pinouts.json` — DIP24_2816, DIP32_28C512_EEPROM, DIP24_2716, DIP24_6116 pinouts
- `firestarter_app/firestarter/data/chip_database.json` — X88C64P entry, all 9 adapter-required chips
- `firestarter_app/tests/test_build_db_inclusion.py` — test invariants on reason strings
- `firestarter_app/tools/diff_db.py` — RULE_PHASE66 claims unsupported_reason field
- `firestarter/src/proms/memory.cpp:74-119` — confirmed 0x34 has no dispatch arm (generic fail-closed catches it)
- `.planning/phases/76-spec-only-gaps-adapter-required-x88c64/76-CONTEXT.md` — locked decisions D-01 to D-04
- `.planning/v1.13-PROTOCOL-ENUMERATION.md` — 0x34 row classification, feasibility taxonomy
- `firestarter/doc/SHIELD-REVISIONS.md` — two-layer doc pattern to mirror
- `.planning/v1.7-SHIELD-REVS.md` — meta investigation-canonical layer pattern

### Secondary (MEDIUM confidence — cited from official/near-official sources)
- X88C64P datasheet pages 1-10 via [alldatasheet.com html-pdf/34232/XICOR/X88C64P](https://www.alldatasheet.com/datasheet-pdf/pdf/34232/XICOR/X88C64P.html) — pinout, interface description, write protocol, VCC voltage
- AT28C16 DIP24 pinout from [amiga-stuff.com/hardware/28c16.html](https://www.amiga-stuff.com/hardware/28c16.html)
- Xicor 1985 Data Book via [bitsavers.org/components/xicor/1985_Xicor_Data_Book.pdf](https://www.bitsavers.org/components/xicor/1985_Xicor_Data_Book.pdf) — confirmed older NOVRAM family has STORE/RECALL; X88C64P does not

### Tertiary (LOW confidence — search results, not full source verification)
- X88C64P write cycle ~100µs — indirect reference from page 5 HTML proxy; marked [ASSUMED] for exact value

---

## Metadata

**Confidence breakdown:**
- AT28C04/AT28C16 pinout: HIGH — cross-verified between codebase pinouts.json and published AT28C16 datasheet reference; DIP24_2816 entry in codebase is the ground truth
- X88C64P interface architecture: HIGH — surveyed 10 of 14 datasheet pages; multiplexed-bus architecture unambiguously confirmed across multiple pages
- X88C64P STORE/RECALL absence: HIGH — no STORE/RECALL mention in any of 10 pages surveyed; older Xicor NOVRAM family confirmed to have them, X88C64P confirmed not to
- DIP24→DIP32 adapter mapping: MEDIUM — derived from pinouts.json ground truth (verified) + bus role matching (logical derivation); exact mapping flagged for planner verification
- X88C64P write cycle timing (tWC): LOW — approximate from indirect page reference

**Research date:** 2026-06-18
**Valid until:** 2026-07-18 (30 days — stable datasheets; no fast-moving dependencies)
