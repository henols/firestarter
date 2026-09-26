# Phase 86: infoic.xml Variant-Field Decode + Correct DB Regen - Research

**Researched:** 2026-06-25
**Domain:** minipro `infoic.xml` field semantics; `build_db.py` classification pipeline; host-only DB regen + gate re-pin
**Confidence:** HIGH (all classification-affecting claims grounded in minipro source `database.c`/`database.h`/`minipro.h` @ master and an exhaustive local survey of the live `infoic.xml`)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Act on the variant field now — generate a correct DB rather than documenting an incorrect one. The "edge cases" being removed are exactly `build_db.py` Rule 1/2/3.
- **D-02:** Deliberate scope amendment to v1.16, not creep. The "pure behavior-preserving / DB-frozen / two-decode-corrections-only" lock is lifted **for this phase only**. Recompose phases (88–89) remain DB-frozen against the **new re-pinned baseline**.
- **D-03:** Inserted as its own phase BEFORE the naming pass. You document the corrected world; you cannot freeze the DB and rewrite it in the same window.
- **D-04:** Decode **both** bytes. Low byte (`variant & 0xFF`) is the existing pinout-family discriminator; the high byte is the new work. Ground every classification-affecting value in minipro source (`database.c`) and/or a committed datasheet.
- **D-05:** Acquire more datasheets if needed (operator-authorized). Any value no source resolves → documented honest gap, never guessed.
- **D-06:** **Full replacement — delete Rule 1, Rule 2 (WARNING-5), Rule 3.** Variant decode becomes the sole classifier. (Claude recommended keeping the rules as asserted-equivalent guards; operator overruled in favor of full deletion — safe because of D-08.)
- **D-07:** Every changed record must be explained by a cited variant-decode rule — reuse the v1.11 GATE-02 classified-diff pattern in `diff_db.py`. Re-pin `chip_database.baseline.json` + `dispatch_baseline.json` to the new correct DB.
- **D-08:** `check_dispatch.py` 0-violations is the structural safety backstop that makes deleting WARNING-5 safe. It asserts (type-string-independent) that no chip routes to `configure_eprom` (12V VPP) on a pinout with no VPP pin.
- **D-09:** On-hand bench-proven chips' wire values must not silently move. The 11 v1.15 EVIDENCE chips keep `algorithm`/`vpp_mv`/`pinout`, OR any moved value is flagged for Leonardo + RURP Rev 2.0 re-bench before Phase 90.

### Claude's Discretion
- Exact decode-table structure in `build_db.py`, high-byte field-naming, and whether the decode is a lookup table vs. bitfield parse — planner/executor's call, as long as Rule 1/2/3 are gone and the gates (D-07/D-08/D-09) hold.
- How datasheet provenance for high-byte resolution is recorded (extend `datasheets/README.md` provenance columns or a decode-notes doc).

### Deferred Ideas (OUT OF SCOPE)
- Naming / documentation vocabulary → Phase 87.
- Implementing the 0x34 X88C64 programming handler → still PCB-blocked (FUT-01); this phase only corrects its decode.
- Open write-path defects (W29C040/CR-01, AM27C020/FUT-06, 2516/FUT-03) → preserved as-is.
- Firmware-side consequences of changed wire values → surfaced via D-09, resolved at Phase 90 bench.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| VAR-01 | Decode `variant` in full (low + high byte), grounded in `database.c`/datasheet; honest gaps documented | §"Variant Field Semantics — The Decisive Finding" gives the authoritative `database.c#L1918` meaning of the high byte and the full high-byte census; §"Honest Gaps" lists what no source resolves |
| VAR-02 | `build_db.py` derives `electrical.type`/`algorithm`/`pinout` from principled decode; Rule 1/2/3 removed | §"Decode → Classification Mapping" maps each deleted rule to its replacement signal (the answer is NOT the variant high byte — see finding) |
| VAR-03 | FM1608→0x28 and X88C64→EEPROM via general decode; every changed row cited; baselines re-pinned | §"Blast Radius", §"Reproducibility + Gates", §"diff_db.py re-pin mechanics" |
| VAR-04 | `check_dispatch.py` 0 violations; 11 EVIDENCE chips keep wire values or flag for re-bench | §"D-08 Structural Backstop", §"D-09 EVIDENCE-11 Risk Table" |
| SAFE-04 | Over-voltage stays blocked at firmware VPP check; host guard never bypassed; no irreplaceable UV part written on unstable path | §"Safety Domain"; the decode rewrite touches no write path and no host guard |
</phase_requirements>

## Summary

The crux question of this phase has a surprising, well-grounded answer: **the `variant` high byte is NOT an electrical-type, algorithm, or pinout discriminator in minipro's own logic.** `minipro/src/database.c#L1918` is the *only* place the high byte is consumed: `uint8_t algo_number = (uint8_t)(device->variant >> 8);`. It is appended as a hex suffix to the protocol's algorithm *name* (e.g. `ROM28P` → `ROM28P41`) to select a specific FPGA bitstream/algorithm file for the **T56/T76** programmers. It carries fine-grained per-chip timing/sequence-file selection within a protocol family, not a memory-class taxonomy that maps onto firestarter's `electrical.type`/`algorithm`/`pinout`. `[VERIFIED: minipro database.c#L1918-L1985 @ master]`

This reframes VAR-02. The honest, principled classifier is built from the fields minipro *itself* uses to classify a memory device: **`type`** (`MP_MEMORY=0x01` vs `MP_SRAM=0x04`), **`protocol_id`** (the algorithm-family / dispatch axis), **`pin_map & 0xFF`** (the physical-layout cluster `pm_idx`, already consumed by `resolve_pinout_key`), **`flags`** (the `0x10` electrically-erasable bit), and **`variant & 0xFF`** (the low-byte sub-discriminator within a layout cluster, already consumed). The survey proves this: FM1608 (FRAM) and AT28C64 (real EEPROM) **share the exact same variant `0x4126`** — the *only* field separating them is `type` (4 vs 1) and `pm_idx` (0 vs 19). The X88C64P EEPROM is identified by `protocol_id=0x34`, not by its variant `0x3100`. `[VERIFIED: infoic.xml INFOIC2PLUS survey, 659 unique DIP-parallel chips]`

So Rule 1/2/3 can be **deleted and replaced by a single principled classifier keyed on (`type`, `protocol_id`, `pm_idx`, `flags`)** — which is what the three rules were *approximating* with name-keyed and pinout-keyed special-cases. The variant *low* byte stays exactly as `resolve_pinout_key` already uses it. The variant *high byte* gets **documented** (VAR-01: its true `algo_number` meaning + a full census) but is **not wired into classification** — and that documented-non-use is itself the honest answer VAR-01 demands, not a gap. The blast radius is fully containable: the new classifier reproduces today's Rule 1/2/3 *output* for the safe-critical chips while removing ~60 lines of fragile special-case code.

**Primary recommendation:** Replace Rule 1/2/3 with one principled `classify(type, proto_id, pm_idx, flags, variant_lo, mem_size)` function that derives `electrical.type` + the dispatch `algorithm`, keeping `resolve_pinout_key` as-is. Document the variant high byte as minipro's T56/T76 `algo_number` (cite `database.c#L1918`) and record the value census; do **not** branch classification on it. Re-pin both baselines, extend `diff_db.py` with variant-decode rule labels, and prove `check_dispatch.py` 0-violations + the 11-EVIDENCE-chip wire-value stability table.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| infoic.xml field decode | Build tooling (`tools/build_db.py`) | — | Offline pipeline; no runtime/serial involvement |
| Chip classification (type/algo/pinout) | Build tooling | — | Pure function of decoded XML fields, emitted into `chip_database.json` |
| Structural VPP-safety gate | Build tooling (`tools/check_dispatch.py`) | Host guard (`chip_resolver`) | Gate proves no 12V-on-no-VPP-pin; host guard is the runtime backstop |
| Diff classification + baseline pin | Build tooling (`tools/diff_db.py` + `tools/baseline/`) | CI (`test_diff_db_gate.py`) | Gate runs in pytest; baseline is the frozen reference |
| Runtime dispatch (unchanged) | Firmware | Host `database.py` | NOT touched this phase — host emits the same wire schema |

## Variant Field Semantics — The Decisive Finding (VAR-01)

### What the variant high byte means in minipro's own code

`minipro/src/database.c`, function `get_algorithm()`:

```c
// database.c#L1918
uint8_t algo_number = (uint8_t)(device->variant >> 8);
...
// database.c#L1953-L1981
snprintf(algo_str, sizeof(algo_str), "%02X", algo_number);
char *name = stpcpy(algorithm->name, entry);   // entry = algo_table[protocol_id-1]
...
strcat(name, algo_str);                          // e.g. "ROM28P" + "41" => "ROM28P41"
```

`[VERIFIED: minipro database.c#L1918-L1985 @ master — https://gitlab.com/DavidGriffith/minipro/-/raw/master/src/database.c]`

- `algo_table` (database.c#L334) is indexed by **`protocol_id`**, NOT by the variant high byte. The high byte (`algo_number`) is the **hex suffix** that picks one specific algorithm/bitstream file *within* that protocol family for the T56/T76 programmer firmware.
- For the TL866II/RURP-relevant path the high byte is **not consulted at all** for classification, electrical type, pinout, or VPP — it only affects which T56/T76 FPGA algorithm blob is loaded. `[VERIFIED: database.c — variant appears at exactly two sites: L585 (parse) and L1918 (the >>8 above); grep confirms no other use]`

**Conclusion for VAR-01:** the high byte is a *programmer-firmware algorithm-file selector*, not a memory taxonomy. This is the honest, source-grounded answer. The phase documents it as such and does NOT derive `electrical.type`/`algorithm`/`pinout` from it. The "structured" appearance the census noted is real but is a **correlation with protocol family**, not an independent semantic axis (see cross-tab below).

### Full high-byte census (659 unique DIP-parallel chips, INFOIC2PLUS filter)

`[VERIFIED: exhaustive local parse of infoic.xml @ master, build_db.py's exact filter (24–32 pin, no SMD, no serial, type∈{1,4})]`

| variant hi | count | (type, protocol_id) it co-occurs with | algo_table family (proto) |
|-----------|-------|----------------------------------------|---------------------------|
| 0x11 | 73 | (1,0x08) | ROM32P |
| 0x12 | 4 | (1,0x08) | ROM32P |
| 0x13 | 7 | (1,0x08) | ROM32P |
| 0x14 | 27 | (1,0x08) | ROM32P |
| 0x31 | 41 | (1,0x07) ×40, (1,0x34) ×1 (X88C64P) | ROM28P / GEN_ |
| 0x32 | 56 | (1,0x07) | ROM28P |
| 0x33 | 44 | (1,0x07) | ROM28P |
| 0x34 | 9 | (1,0x04) — DataFlash, skipped by KNOWN_PROTOCOLS gate | AT45D |
| 0x37 | 3 | (1,0x07) | ROM28P |
| 0x3A | 12 | (1,0x0B) | ROM24P |
| 0x3B | 10 | (1,0x0B) | ROM24P |
| 0x41 | 69 | (1,0x07) ×45, (4,0x07) ×14, (4,0x28) ×10 | ROM28P / ROM28P_2 |
| 0x43 | 24 | (1,0x0B) ×19, (4,0x0B) ×3, (4,0x27) ×2 | ROM24P |
| 0x44 | 17 | (1,0x0D) | EE28C32P |
| 0x50 | 24 | (4,0x0E) ×12, (4,0x29) ×12 | RAM32 |
| 0x51 | 12 | (4,0x0E) ×4, (4,0x29) ×8 | RAM32 |
| 0x70 | 39 | (1,0x06) | W29F32P |
| 0x71 | 119 | (1,0x06) | W29F32P |
| 0x75 | 25 | (1,0x05) | F29EE |
| 0x77 | 2 | (1,0x05) | F29EE |
| 0x79 | 2 | (1,0x10) | 28F32P |
| 0x7A | 23 | (1,0x10) | 28F32P |
| 0x7B | 4 | (1,0x10) | 28F32P |
| 0x7C | 2 | (1,0x10) | 28F32P |
| 0x80 | 3 | (1,0x10) | 28F32P |
| 0x93 | 2 | (1,0x11) — FWH, infeasible, skipped | FWH |
| 0xE2 | 6 | (1,0x08) ×5, (4,0x07) ×1 (M48T08) | ROM32P |

**Reading the table:** every high-byte value sits inside one protocol family (the algo_table column), confirming it is a *sub-variant within a protocol*, not a cross-cutting type code. The two interesting collision cells are exactly the FM1608 and X88C64 cases:
- `hi=0x41` mixes (1,0x07) real 28C EEPROMs **and** (4,0x07) FRAM/NVRAM — same variant `0x4126`, separated only by `type`.
- `hi=0x31` is the 27512 EPROM family (variant `0x3110`); X88C64P is the lone (1,0x34) entry with variant `0x3100`, separated by `protocol_id`.

### Ground-truth proof tuples (verified from the live XML)

`[VERIFIED: infoic.xml INFOIC2PLUS @ master]`

| Chip | type | protocol_id | variant | voltages | flags | pin_map (pm_idx) | size |
|------|------|-------------|---------|----------|-------|------------------|------|
| FM1608 | 4 | 0x07 | **0x4126** | 0x0100 | 0x00000000 | 0x00000000 (0) | 0x2000 |
| FM1208 | 4 | 0x0b | **0x4310** | 0x0200 | 0x00000000 | 0 | 0x800 |
| FM1808 / FM18L08 | 4 | 0x07 | 0x4126 | 0x010x | 0x00000000 | 0 | 0x8000 |
| FM16W08 | 4 | 0x07 | 0x4126 | 0x0101 | 0x00000000 | 0 | 0x2000 |
| X88C64P | 1 | **0x34** | 0x3100 | 0x0200 | **0x00414200** | 0x9000e600 (0) | 0x2000 |
| AT28C64 (collides w/ FM1608 variant) | 1 | 0x07 | **0x4126** | — | 0x000010 | 19 | 0x2000 |
| AT28C256 | 1 | 0x07 | 0x4126 | — | 0x00C010 | 20 | 0x8000 |
| 27C512 family | 1 | 0x07 | 0x3110 | — | 0x000068/78 | 22 | 0x10000 |

**The load-bearing facts:** (a) FM1608 and AT28C64 are indistinguishable by `variant` (both `0x4126`); `type` (4 vs 1) is the discriminator. (b) X88C64P's EEPROM identity is `protocol_id=0x34`; `flags & 0x10 == 0` so the existing flags-based EEPROM rule misses it; today it falls through to `UV-EPROM`. (c) `flags & 0x10` correctly marks W27C512/SST27SF512 etc. as electrically-erasable; this is unchanged.

### Type-field constants (the real memory-class axis)

`[VERIFIED: minipro/src/minipro.h#L67-L74 @ master]`

```
MP_MEMORY = 0x01   MP_MCU = 0x02   MP_PLD = 0x03   MP_SRAM = 0x04
MP_LOGIC  = 0x05   MP_NAND = 0x06  MP_EMMC = 0x07  MP_VGA = 0x08
```

build_db.py already filters to `type ∈ {1, 4}` = `{MP_MEMORY, MP_SRAM}`. `MP_SRAM` (type=4) is minipro's tag for the SRAM/FRAM/NVRAM class — this is the authoritative signal Rule 3 keys on.

## Decode → Classification Mapping (VAR-02)

The replacement is a single principled classifier. Each deleted rule maps to a field-based predicate that is **already present in the data** — no rule loses coverage:

| Deleted rule | What it did | Replacement signal (principled) | Coverage proof |
|--------------|-------------|----------------------------------|----------------|
| **Rule 1** (build_db.py ~L516) | `pinout==DIP24_2816` → force algo `0x0D` | Already structural: `resolve_pinout_key` maps 24-pin `pm_idx=23, variant_lo=0x10` → `DIP24_2816`; the principled classifier emits algo `0x0D` for that pinout class. Keep the pinout→algo mapping inside the classifier (not as a post-hoc override). | All `(pm_idx=23, variant_lo=0x10)` chips are the 28C family `[VERIFIED: survey]` |
| **Rule 2 / WARNING-5** (~L552) | 5V-EEPROM on EPROM pinout (`DIP28_28C256`/`DIP28_2764`+Flash/EEPROM/`DIP28_28C64`) → flip `0x07`→`0x0D` | Principled: a chip whose resolved pinout has **no VPP pin** (or is a known 5V-EEPROM layout: `pm_idx∈{18,19,20}`) must dispatch `0x0D`. The 0x07 chips that legitimately keep 12V VPP (W27C512 etc.) sit on `pm_idx=22` pinouts that DO have a VPP pin. So `pm_idx` cleanly separates them. | `pm_idx∈{18,19,20}` = 28C64/28C256 5V-EEPROM clusters; `pm_idx=22` = 27Cxxx VPP-pin EPROM cluster `[VERIFIED: survey + datasheet cross-check noted in build_db.py L546-L548]` |
| **Rule 3** (~L583) | `type==4 AND proto∈{0x07,0x08,0x0B}` → algo `0x28` + SRAM pinout | Principled and unchanged: `type==4` (MP_SRAM) is the authoritative class. Emit algo `0x28` (SRAM_STD) for type=4 chips that arrived with an EPROM-family protocol. This is the *exact same predicate* — it just moves into the unified classifier instead of being a trailing override. | 18 type=4 chips carry EPROM-family proto (FM*/DS12*/M48T*/BQ40*) `[VERIFIED: survey]` |

**Net effect:** Rule 1/2/3 were never using the variant high byte — they used `pinout`/`type`/`flags`. The "principled variant-driven decode" the requirement asks for is satisfied by (a) keeping the variant **low** byte's existing role in `resolve_pinout_key`, and (b) consolidating the type/proto/pm_idx/flags logic into one classifier, while (c) documenting that the variant **high** byte is the minipro `algo_number` and is deliberately not a classification input. This is the honest interpretation of VAR-02 given the source evidence.

### Recommended classifier shape (Claude's discretion area — D-06)

A single function returning `(etype, algorithm)` given the already-resolved `pinout_key`:

```python
# Pseudocode — derived from build_db.py current two-pass logic, consolidated.
# Source grounding: minipro.h MP_SRAM=0x04; flags&0x10 = electrically-erasable
#   (minipro database.c flags handling); pm_idx clusters from resolve_pinout_key.
def classify(type_int, proto_id, pm_idx, flags, pinout_key, mem_size):
    # 1. SRAM/FRAM/NVRAM class (was Rule 3) — type is authoritative
    if type_int == 4 or proto_id in {0x0E, 0x27, 0x28, 0x29}:
        return ("SRAM", 0x28 if proto_id in {0x07,0x08,0x0B} else proto_id)
    # 2. 5V-EEPROM pinout clusters (was Rule 1 + Rule 2) — pm_idx / pinout decides
    if pinout_key in {"DIP24_2816","DIP28_28C64","DIP28_28C256"} \
       or (pinout_key == "DIP28_2764" and (flags & 0x10)):
        return ("EEPROM", 0x0D)            # configure_eeprom28c, no VPP
    # 3. EPROM-family with electrically-erasable bit = CMOS EEPROM (keeps 12V VPP)
    if proto_id in {0x07,0x08,0x0B}:
        return ("EEPROM" if (flags & 0x10) else "UV-EPROM", proto_id)
    # 4. Flash families
    if proto_id in {0x05,0x06,0x0D,0x10}:
        return ("Flash/EEPROM", proto_id)
    return ("UV-EPROM", proto_id)
```

This is **structurally equivalent** to today's Pass-1/Rules/Pass-2 sequence but collapses the override stack. The FM1608 `type=4` arm yields `(SRAM, 0x28)` (then the existing Phase-84 FRAM cosmetic relabel applies). X88C64P (`proto=0x34`) is gated upstream as `protocol-not-implemented`; its `electrical.type` should come out **EEPROM** — see the X88C64 note below.

### X88C64 EEPROM-type fix (VAR-03)

X88C64P has `proto=0x34`, `flags=0x00414200` (`flags & 0x10 == 0`), so neither the flags rule nor any proto-family arm currently tags it EEPROM → it defaults to `UV-EPROM` (confirmed in the live DB). It is also `support_status=protocol-not-implemented` and NON-dispatchable, so this is a *display/classification* correction with no dispatch consequence. The principled fix: treat `proto_id == 0x34` (XICOR NovRAM/EEPROM) as `electrical.type = "EEPROM"`. Add a small explicit arm for 0x34 in the classifier. `[VERIFIED: infoic.xml X88C64P tuple + live chip_database.json shows type=UV-EPROM today]`

## Standard Stack

No new dependencies (SAFE-05). The existing tooling is the stack:

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| Python | 3.11 (CI target), 3.12 (devcontainer) | build/test runtime | CI pins 3.11; validate against it `[VERIFIED: ci.yml#L32]` |
| `requests` | (in `.[test]` deps) | fetch infoic.xml | `build_db.py` uses it; confirmed importable in devcontainer `[VERIFIED: import check]` |
| `ruff` | per `.[dev]`/`.[test]` | lint + format gate | CI gate `[CITED: firestarter_app/CLAUDE.md]` |
| `mypy` | per watermark | type gate (8 strict modules; build_db NOT in strict set) | `tools/check_mypy_watermark.py` `[CITED: CLAUDE.md]` |
| `pytest` | per `.[test]` | runs `test_diff_db_gate.py`, `test_build_db_inclusion.py`, `test_check_dispatch_invariants.py` | `--cov-fail-under=70` `[VERIFIED: ci.yml]` |

**Installation (toolchain restore in devcontainer):**
```bash
cd firestarter_app && pip install -e '.[test]'
```

## Package Legitimacy Audit

No external packages are installed by this phase. SAFE-05 forbids new third-party deps; the only artifacts are `datasheets/` additions (D-05). **Audit: N/A — zero new packages.**

## Architecture Patterns

### System Architecture Diagram

```
                 minipro upstream (GitLab @ master)
                              │  MINIPRO_XML_URL fetch (requests.get, build_db.py L11/L290)
                              ▼
                        infoic.xml  (17.8 MB)
                              │  ET.fromstring → INFOIC2PLUS database only
                              ▼
        ┌──────────────  build_db.py main() loop  ──────────────┐
        │  per <ic>:                                            │
        │   decode: type, protocol_id, variant(lo+hi), flags,   │
        │           voltages, pin_map→pm_idx, code_memory_size  │
        │      │                                                │
        │      ├─ inclusion gates (KNOWN_PROTOCOLS, 0x34 PNI,   │
        │      │   24-pin EEPROM adapter-required, NMOS VPP)    │  ← UNCHANGED
        │      │                                                │
        │      ├─ resolve_pinout_key(... variant_lo ...)        │  ← UNCHANGED (low byte)
        │      │                                                │
        │      └─ classify(type,proto,pm_idx,flags,pinout) ◄────┼── NEW: replaces
        │            → (electrical.type, algorithm)             │     Rule 1/2/3 + 2-pass
        │      │                                                │
        │      ▼                                                │
        │  chip_entry { electrical, programming, pinout, ... }  │
        └───────────────────────┬───────────────────────────────┘
                                ▼
                  firestarter/data/chip_database.json  (~744 records)
                       │                        │                      │
                       ▼                        ▼                      ▼
             diff_db.py (GATE-02)     check_dispatch.py (D-08)   EpromDatabase (runtime,
             vs baseline/*.json       0 violations               UNCHANGED wire schema)
                  │                         │
            re-pin baselines          dispatch_baseline.json re-pin
```

File-to-implementation mapping: see the Component Responsibilities below.

### Recommended Project Structure (files touched)
```
firestarter_app/
├── tools/
│   ├── build_db.py                 # rewrite: delete Rule 1/2/3 + 2-pass, add classify()
│   ├── diff_db.py                  # add variant-decode rule labels to _RATIONALES/_RULE_FIELD_PATHS
│   ├── check_dispatch.py           # UNCHANGED (it is the structural backstop; run it)
│   └── baseline/
│       ├── chip_database.baseline.json   # RE-PIN to new DB (diff_db reference)
│       └── dispatch_baseline.json        # RE-PIN (check_dispatch inline-capture format)
├── firestarter/data/chip_database.json   # REGENERATED output (744 chips)
└── tests/
    ├── test_diff_db_gate.py        # runs diff_db.py in subprocess — MUST stay green after re-pin
    ├── test_build_db_inclusion.py  # DB-01/02/03 invariants — must still hold
    └── test_check_dispatch_invariants.py  # synthetic VPP-invariant fixtures
firestarter/datasheets/             # (firmware sub-repo) optional D-05 datasheet additions + README provenance
```

### Pattern: v1.11/v1.12 decode-correctness milestone (the direct precedent)
**What:** source-grounded field dictionary → re-derived `build_db.py` → classified diff gate → re-pin baseline.
**When to use:** any `infoic.xml` decode change. This phase is "v1.11 part 2: the variant field."
**Example:** the `[VERIFIED: minipro database.c#Lxxx @ a8efaedc]` citation idiom already embedded throughout `build_db.py` and `diff_db.py`'s `_RATIONALES`. New rule labels must carry the same citation discipline (cite `database.c#L1918` for the variant-high-byte=algo_number fact).

### Anti-Patterns to Avoid
- **Branching classification on `variant >> 8`.** The census *looks* structured but the high byte is a per-protocol bitstream selector (database.c#L1918), not a memory-class axis. A classifier keyed on it would be a coincidence-fit that breaks on the next upstream chip add. Use `type`/`proto`/`pm_idx`/`flags`.
- **Keeping a residual override after the classifier.** D-06 says full deletion. Fold all logic into `classify()`; don't leave a "just in case" post-hoc flip — that recreates the edge-case stack the phase removes.
- **Re-pinning the baseline before the diff is fully explained.** Re-pin is the *last* step (VAR-03): first make `diff_db.py` classify every changed row, THEN copy current→baseline. Re-pinning early hides unexplained diffs.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Per-chip diff classification | A new diff script | `diff_db.py` `_classify_diff` + `_RULE_FIELD_PATHS` (extend) | Already does composite-key 1:1 indexing, compound-change surfacing, exit-code contract (0/1/2) |
| 12V-on-wrong-pin safety check | A bespoke type-string check | `check_dispatch.py` structural guard (`_build_no_vpp_pin_set`) | Type-string-independent; this is exactly D-08's backstop |
| Pinout selection | New layout tables | `resolve_pinout_key` (keep verbatim) | Phase 58 already derived the principled pm_idx/variant_lo logic; do NOT touch it |
| VPP nibble decode | Re-decoding voltages | existing `voltages & 0xF0` mask + `VPP_MV` table | BUG-B already fixed; minipro uses `voltages & 0xff` for vpp but RURP's 0xF0 mask is intentional (low nibble = option flags) `[VERIFIED: database.c#L697 vs build_db.py L61-L68]` |

**Key insight:** every gate this phase needs already exists and is CI-wired. The work is a *classifier rewrite + baseline re-pin*, not new infrastructure.

## Runtime State Inventory

This is a build-tool + generated-data refactor. There is runtime-adjacent state to account for:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | `firestarter/data/chip_database.json` (744 records) — the regenerated artifact | Regenerate via `build_db.py`; commit the new file |
| Stored data (baselines) | `tools/baseline/chip_database.baseline.json` (370 KB) + `tools/baseline/dispatch_baseline.json` (157 KB) | RE-PIN both to the new DB (VAR-03 / D-07) |
| Live service config | None — no live service; infoic.xml is fetched fresh from GitLab `master` on every `build_db.py` run. **Reproducibility caveat below.** | None |
| OS-registered state | None | None |
| Secrets/env vars | `FIRESTARTER_DB_FILE`, `FIRESTARTER_PINOUTS_FILE`, `FIRESTARTER_BASELINE_FILE` (test seams in diff_db/check_dispatch) — names unchanged | None |
| Build artifacts | `tools/__pycache__/` (stale `.pyc` after build_db edit) | Harmless; ignored |
| User-override layer | `~/.firestarter/database.json` merges over the generated DB at runtime (`skip_local_override` seam) | Out of scope; not touched |

**Reproducibility caveat (resolve at plan time — IMPORTANT):** `build_db.py` fetches `MINIPRO_XML_URL` (GitLab `master`) live; there is **no vendored `tools/infoic.xml`** (confirmed: file absent). The `firestarter_app/CLAUDE.md` data-flow text says "`build_db.py` parses `tools/infoic.xml`" but that is stale/aspirational — the code path is remote-fetch only (`build_db.py` L11, L288-L295). This means: (1) the regenerated DB is only reproducible against the upstream `master` snapshot at regen time, and (2) prior `[VERIFIED: ... @ a8efaedc]` citations pin a *specific commit* the current `master` may have drifted from. **The planner should decide whether to pin the fetch to a commit SHA** (vendor `infoic.xml` or change the URL to a fixed ref) so the diff is deterministic and the baseline re-pin is reproducible. Recommended: capture the upstream commit SHA used for this regen and record it in the decode-notes doc (matches the existing `@ a8efaedc` citation convention).

## Common Pitfalls

### Pitfall 1: Treating the variant high byte as a type/pinout enum
**What goes wrong:** building `classify()` to switch on `variant >> 8`.
**Why it happens:** the census looks structured (0x41→FRAM, 0x31→27512…).
**How to avoid:** the structure is *protocol-family correlation* (database.c#L1918 proves it's the algo-file suffix). FM1608 and AT28C64 share `0x4126`; `type` is the discriminator. Key on `type`/`proto`/`pm_idx`/`flags`.
**Warning signs:** classifier needs more than ~28 high-byte cases, or two chips with the same high byte want different `electrical.type`.

### Pitfall 2: Two-pass ordering loss (RESEARCH precedent Pitfall 2)
**What goes wrong:** collapsing Pass-1/Pass-2 changes which `_etype` the EEPROM/Flash arms see.
**Why it happens:** today's Pass-1 computes a flags-based `_etype` that Rules 1/2 read, then Pass-2 re-derives from the (overridden) proto.
**How to avoid:** the consolidated `classify()` must compute `electrical.type` from the **final** algorithm (post-SRAM/EEPROM decision), exactly as Pass-2 does. The pseudocode above already orders SRAM → EEPROM-pinout → proto-family.
**Warning signs:** W27C512 flips from `EEPROM` to `UV-EPROM` (flags&0x10 must still win on `pm_idx=22`).

### Pitfall 3: 27512 vs 27256 VPP-pin swap (RESEARCH precedent Pitfall 3)
**What goes wrong:** `variant_lo 0x10→DIP28_27512` (VPP pin 22) and `0x11→DIP28_27256` (VPP pin 1) get swapped → 12V to the wrong pin.
**How to avoid:** do NOT touch `resolve_pinout_key`. The variant *low* byte logic is correct and out of scope for the rewrite.
**Warning signs:** `check_dispatch.py` novpp/eeprom28c lists change; 27512-family pinout deltas in `diff_db.py`.

### Pitfall 4: Baseline re-pin breaks `test_diff_db_gate.py` (CI-wired)
**What goes wrong:** `test_diff_db_gate.py` runs `diff_db.py` in a subprocess and asserts exit 0 + "PASS: all". After regen, the *new* DB vs the *old* baseline produces a big diff → test fails until both the rule labels are added AND the baseline is re-pinned.
**How to avoid:** sequence is (1) regen DB, (2) extend `diff_db.py` `_RATIONALES`/`_RULE_FIELD_PATHS`/`_classify_diff` with variant-decode rule labels so every changed row is explained, (3) verify `diff_db.py` exits 0 against the *new* baseline only after re-pin. Note `test_diff_db_gate.py` compares current vs baseline — once both are the new DB the identity diff is empty and the test passes trivially; the *explained-diff* proof (D-07) is a separate pre-re-pin run captured in the decode-notes doc.
**Warning signs:** pytest red on `TestDiffDbGate::test_diff_db_identity_pass`.

### Pitfall 5: Phase-84 FRAM relabel + Phase-66 inclusion logic collateral
**What goes wrong:** deleting Rule 3 also removes the `pinout_key`/`size_label` SRAM re-route that FM1608 depends on; or the `_PHASE84_RELABEL` cosmetic SRAM→FRAM step runs on a now-differently-typed chip.
**How to avoid:** the new `classify()` must still emit `algo=0x28` + the SRAM pinout for type=4 chips (Rule 3's *behavior* is preserved, only its *form* changes). Keep the Phase-84 relabel and the Phase-66 inclusion gates (0x34 PNI, 24-pin adapter-required, NMOS VPP) intact — they are not Rule 1/2/3 and are not in scope for deletion.
**Warning signs:** FM1608 `electrical.type` ≠ `FRAM`, or pinout ≠ `DIP28_JEDEC_SRAM_8K`, in the new DB.

## Code Examples

### diff_db.py rule-label extension (the D-07 pattern)
```python
# tools/diff_db.py — add to _RATIONALES (cite the source for the variant fact)
"VARIANT_DECODE": (
    "Variant-decode consolidation (Phase 86 VAR-02) — Rule 1/2/3 replaced by a\n"
    "  single principled classify(type,proto,pm_idx,flags,pinout).\n"
    "  The variant HIGH byte is minipro's T56/T76 algo-file selector, NOT a\n"
    "  classification axis.\n"
    "  [VERIFIED: minipro database.c#L1918 @ <PINNED_SHA> —\n"
    "   uint8_t algo_number = (uint8_t)(device->variant >> 8)]\n"
    "  type=4 (MP_SRAM) is the FRAM/NVRAM class signal (FM1608/DS12*/M48T*).\n"
    "  [VERIFIED: minipro.h#L70 MP_SRAM=0x04]"
),
# _RULE_FIELD_PATHS["VARIANT_DECODE"] = {("programming","algorithm"),("pinout",),("electrical","type")}
```

### Regenerate + gate sequence
```bash
cd firestarter_app
python tools/build_db.py                              # regen chip_database.json
python tools/diff_db.py | tee /tmp/diff-explained.txt  # MUST exit 0 vs OLD baseline (every row labeled) BEFORE re-pin
python tools/check_dispatch.py                         # MUST print 0 violations (D-08 / VAR-04)
# re-pin (VAR-03) — last:
cp firestarter/data/chip_database.json tools/baseline/chip_database.baseline.json
# dispatch_baseline.json: regenerate via check_dispatch's inline-capture (see meta.generated_by)
pytest tests/test_diff_db_gate.py tests/test_build_db_inclusion.py tests/test_check_dispatch_invariants.py
ruff check tools/ firestarter/ tests/ && ruff format --check tools/ firestarter/ tests/
```
*(Note: `dispatch_baseline.json` carries `meta.generated_by="check_dispatch.py inline capture"` — confirm/locate the capture path; it is NOT consumed by any test directly (grep finds no test reading it), so its re-pin is a documentation/provenance artifact, not a gate. Verify this at plan time.)*

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Name-keyed & pinout-keyed override stack (Rule 1/2/3) | Principled field-based `classify()` | Phase 86 (this) | ~60 lines of special-case removed; decode is a pure function of minipro fields |
| Variant byte = "pinout family only (low byte)" | Both bytes documented; high byte = `algo_number` (T56/T76 file selector), explicitly NOT a classifier | Phase 86 | Closes the VAR-01 knowledge gap with source grounding |
| `electrical.type` derived in two passes around overrides | Derived once from final algorithm inside `classify()` | Phase 86 | Same output, simpler order |

**Deprecated/outdated:**
- `firestarter_app/CLAUDE.md` data-flow line "parses `tools/infoic.xml`": stale — code fetches remote. Flag for Phase 87 doc pass (or fix opportunistically).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The current upstream `master` infoic.xml is field-compatible with the `@ a8efaedc` snapshot the existing citations pin (no new high-byte semantics introduced upstream) | Variant Semantics | LOW — survey was run on live `master`; if upstream changed, the diff would surface new chips/values which `diff_db.py` would flag as unexplained (fails safe) |
| A2 | `dispatch_baseline.json` is not consumed by any CI test (grep found no reader) — its re-pin is provenance-only | Reproducibility + Gates | MEDIUM — if a hidden consumer exists, a stale dispatch_baseline could pass silently; planner should re-verify with a fresh grep before treating re-pin as optional |
| A3 | The principled `classify()` reproduces today's Rule 1/2/3 *output* for all safety-critical chips (no NEW chip moves onto a 12V path) | Decode→Classification | LOW — `check_dispatch.py` 0-violations is the hard gate (D-08); any regression is caught structurally |
| A4 | 2516 (v1.15 ANOMALY chip) is either absent from the generated DB or unaffected by the classifier change | D-09 EVIDENCE | MEDIUM — it did not appear under the `2516` part_number search; planner must confirm its DB presence/identity and that its row is unchanged (D-09 + SAFE-04: do not move an unstable UV part's wire values) |
| A5 | Treating `proto_id==0x34` as `electrical.type="EEPROM"` is the correct X88C64 fix (vs. a broader NovRAM rule) | X88C64 fix | LOW — X88C64P is the only 0x34 DIP-parallel chip in scope; it is non-dispatchable so the change is display-only |

**No `[ASSUMED]` claims affect safety dispatch** — all dispatch-affecting facts are `[VERIFIED]` against source.

## Open Questions (RESOLVED during planning)

> All three resolved by plan design: Q1 (fetch SHA) → captured in DECODE-NOTES.md by 86-01 T1; Q2 (dispatch_baseline.json gate-vs-provenance) → 86-03 T1 treats it as provenance-only, `chip_database.baseline.json` is the live gate; Q3 (2516 DB presence) → CONTEXT.md D-10/D-11 + plan 86-04 ship it via the non-upstream supplement (UNVERIFIED).

1. **Pin the infoic.xml fetch to a commit SHA?**
   - What we know: fetch is live against `master`; no vendored copy; existing citations pin `@ a8efaedc`.
   - What's unclear: whether the operator wants deterministic reproducibility (vendor or pin) vs. always-latest.
   - Recommendation: pin to a SHA (or vendor `tools/infoic.xml`) for this regen and record it; matches existing citation convention and makes the baseline re-pin reproducible. (Claude's discretion per D-05 on how provenance is recorded.)

2. **Is `dispatch_baseline.json` re-pin a gate or provenance?**
   - What we know: no test reads it; `chip_database.baseline.json` is the live gate (via `test_diff_db_gate.py`).
   - Recommendation: re-pin both for consistency (D-07 names both), but treat `chip_database.baseline.json` as the load-bearing one. Confirm with a final grep.

3. **2516 DB presence (D-09 / SAFE-04).**
   - What we know: not found under bare `2516`; v1.15 marked it ANOMALY (unstable read path, must not be spent).
   - Recommendation: planner verifies its DB record (likely under a manufacturer prefix or `TMS2516`) and asserts zero delta on its row.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | build_db/diff_db/check_dispatch | ✓ | 3.12 (devcontainer); CI is 3.11 | validate against 3.11 semantics |
| `requests` | build_db.py remote fetch | ✓ | in `.[test]` | none (network required to regen) |
| Network → gitlab.com | build_db.py `MINIPRO_XML_URL` | ✓ (verified: 17.8 MB fetched this session) | — | vendor `infoic.xml` locally (also resolves Open Q1) |
| `ruff` / `mypy` / `pytest` | CI gate | ✓ (via `.[test]`) | per lockfile | `pip install -e '.[test]'` to restore |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** network for regen — vendoring `infoic.xml` removes the dependency and improves reproducibility.

## Validation Architecture

`workflow.nyquist_validation` is absent in `.planning/config.json` → treated as enabled. This phase's "behavior" is data correctness, so the test map targets the existing gate scripts rather than new runtime tests.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (+ subprocess-driven gate scripts) |
| Config file | `firestarter_app/pyproject.toml` (`.[test]`); CI `firestarter_app/.github/workflows/ci.yml` |
| Quick run command | `pytest tests/test_diff_db_gate.py tests/test_build_db_inclusion.py -x` |
| Full suite command | `pytest tests/ --cov=firestarter --cov-fail-under=70` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| VAR-02 | Rule 1/2/3 removed; classifier emits correct algo/type | unit/integration | `pytest tests/test_build_db_inclusion.py -x` | ✅ (extend assertions if needed) |
| VAR-03 | Every changed row explained; baseline re-pinned | integration | `python tools/diff_db.py` (exit 0) → `pytest tests/test_diff_db_gate.py -x` | ✅ |
| VAR-03 | FM1608→0x28, X88C64→EEPROM via general decode | unit | new assertion: load `chip_database.json`, assert FM1608 algo==0x28 & type==FRAM, X88C64 type==EEPROM | ❌ Wave 0 (add to `test_build_db_inclusion.py`) |
| VAR-04 | 0 dispatch violations | integration | `python tools/check_dispatch.py` (prints "0 ... violations") + `pytest tests/test_check_dispatch_invariants.py` | ✅ |
| VAR-04 / D-09 | 11 EVIDENCE chips wire-stable | unit | new assertion: each EVIDENCE chip's algo/vpp_mv/pinout unchanged vs old baseline | ❌ Wave 0 (data-driven test from EVIDENCE.json) |

### Sampling Rate
- **Per task commit:** `pytest tests/test_diff_db_gate.py tests/test_build_db_inclusion.py -x`
- **Per wave merge:** `python tools/build_db.py && python tools/diff_db.py && python tools/check_dispatch.py && pytest tests/`
- **Phase gate:** full suite green + `diff_db.py` 0 + `check_dispatch.py` 0 violations + ruff/format/mypy(watermark) green on py3.11 semantics before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/test_build_db_inclusion.py` — add FM1608 (algo=0x28, type=FRAM) and X88C64 (type=EEPROM) assertions for VAR-03.
- [ ] `tests/` — add a D-09 EVIDENCE-11 wire-stability test (load `.planning/v1.15/bench/EVIDENCE.json` chip list; assert algo/vpp_mv/pinout match old baseline OR are explicitly flagged).
- [ ] Decode-notes doc (D-05 provenance + pinned infoic.xml SHA) — new artifact.

## D-09 EVIDENCE-11 Risk Table (VAR-04)

Current DB values for the 11 bench-proven chips (from live `chip_database.json`). The classifier rewrite must NOT move algo/vpp_mv/pinout for any of these, or the moved value must be flagged for Leonardo + RURP Rev 2.0 re-bench before Phase 90.

| Chip | algo | pinout | vpp_mv | type | Risk under new classifier |
|------|------|--------|--------|------|---------------------------|
| W27C512 | 0x07 | DIP28_27512 | 12000 | EEPROM | NONE — `pm_idx=22`, flags&0x10 → EEPROM/0x07 unchanged |
| W27E512 | 0x07 | DIP28_27512 | 12000 | EEPROM | NONE — same cluster |
| SST27SF512 | 0x07 | DIP28_27512 | 12000 | EEPROM | NONE — flags `0x78` (erasable) preserved |
| W27E040 (W27C040) | 0x08 | DIP32_STD | 12000 | EEPROM | NONE — proto 0x08, flags&0x10 → EEPROM unchanged |
| SST39SF040 | 0x06 | DIP32_SST39SF040 | 12000 | Flash/EEPROM | NONE — Flash family arm unchanged; Phase-84 STOP preserved |
| W29C020 | 0x05 | DIP32_SST39SF040 | 12000 | Flash/EEPROM | NONE — Flash family unchanged |
| W29C040 | 0x05 | DIP32_SST39SF040 | 12000 | Flash/EEPROM | NONE — unchanged (CR-01 write defect untouched) |
| FM1608 | 0x28 | DIP28_JEDEC_SRAM_8K | 12000 | FRAM | LOW — type=4 SRAM arm + Phase-84 relabel must reproduce exactly; verify in new DB |
| ST M27C512 | 0x07 | DIP28_27512 | 13000 | UV-EPROM | NONE — flags&0x10==0 → UV-EPROM/0x07 unchanged |
| AM27C020 | 0x08 | DIP32_STD | 13000 | UV-EPROM | NONE — unchanged (FUT-06 write defect untouched) |
| 2516 | (verify) | (verify) | (verify) | UV-EPROM (NMOS) | VERIFY — not found under bare `2516`; planner must locate its record and assert zero delta (SAFE-04: unstable read path, do not move) |

**Mitigation:** the planner should add the data-driven EVIDENCE-stability test (Wave 0) that diffs these chips' three wire fields against the OLD baseline; any non-empty delta becomes an explicit `checkpoint:human-verify` for Phase 90 re-bench (D-09).

## Safety Domain

`security_enforcement` is absent in config → treated as enabled, but this is **hardware-safety**, not web/app-security. Standard ASVS web categories (auth, session, access control, crypto) are **N/A** — there is no user input surface, network endpoint, or credential in a build-time data pipeline.

The relevant safety model is the **12V-VPP-on-a-5V-pin hardware-damage path** (STRIDE: Tampering / physical), mitigated structurally:

| Hazard | Mitigation (this phase) | Gate |
|--------|--------------------------|------|
| 12V VPP asserted on a no-VPP-pin socket (deleting WARNING-5) | `check_dispatch.py` structural guard: no chip routes to `configure_eprom` on a pinout with no `vpp-pin` (type-string-independent) | `python tools/check_dispatch.py` → 0 violations (D-08 / VAR-04) |
| SRAM/FRAM mis-dispatched to `configure_eprom` (12V on 5V FRAM) | type=4 → `algo=0x28` (configure_sram, no VPP) preserved in `classify()` | `check_dispatch.py` `_SRAM_PROTOCOLS` guard + `sram_in_eprom` list |
| Over-voltage NMOS part | NMOS VPP correction + `vpp-exceeds-max` demotion to NON_DISPATCHABLE_ALGO — UNCHANGED by this phase | firmware VPP check + host `chip_resolver` guard (SAFE-04) |
| Writing an irreplaceable/unstable UV part | No write path touched; 2516 stays UNVERIFIED; decode-only change | SAFE-04 — verify 2516 row unchanged |

**The host guard (`chip_resolver.resolve_chip`) and firmware VPP check are not modified** — SAFE-04 is satisfied by non-action plus the structural gate.

## Sources

### Primary (HIGH confidence)
- minipro `src/database.c` @ master — `variant>>8 = algo_number` (L1918), `algo_table` (L334), pin_map low-byte (L611), voltages decode (L696-697), chip_type parse (L583). https://gitlab.com/DavidGriffith/minipro/-/raw/master/src/database.c
- minipro `src/minipro.h` @ master — type constants `MP_MEMORY=0x01 … MP_SRAM=0x04` (L67-74). https://gitlab.com/DavidGriffith/minipro/-/raw/master/src/minipro.h
- minipro `src/database.h` @ master — `IC2_ALG_*` protocol constants (L31-73).
- `infoic.xml` @ master (17.8 MB, fetched + parsed this session) — full INFOIC2PLUS survey of 659 unique DIP-parallel chips; FM/X88C64 ground-truth tuples.
- Local code: `firestarter_app/tools/build_db.py` (current Rule 1/2/3 at L508-605, classifier two-pass L487-643), `tools/diff_db.py`, `tools/check_dispatch.py`, `firestarter/data/chip_database.json`, `tests/test_diff_db_gate.py`, `.planning/v1.15/bench/EVIDENCE.json`.

### Secondary (MEDIUM confidence)
- `firestarter_app/CLAUDE.md` (WARNING-5 writeup, CI gate; note the stale "parses tools/infoic.xml" line).
- `.planning/REQUIREMENTS.md` §Scope AMENDMENT + VAR-01..04/SAFE-04; `86-CONTEXT.md` D-01..D-09.

### Tertiary (LOW confidence)
- None — all classification-affecting claims cross-checked against minipro source + live XML.

## Metadata

**Confidence breakdown:**
- Variant semantics: HIGH — single source-of-truth line (database.c#L1918) + exhaustive XML census.
- Decode→classification mapping: HIGH — each deleted rule's replacement signal proven present in the survey.
- Blast radius / EVIDENCE stability: MEDIUM-HIGH — current DB values captured directly; 2516 record location is the one open item.
- Reproducibility (fetch pinning): MEDIUM — code path confirmed remote-only; SHA-pinning is a planner decision.

**Research date:** 2026-06-25
**Valid until:** ~2026-07-25 (stable; only risk is upstream infoic.xml drift on `master`, which the diff gate catches as unexplained rows).
