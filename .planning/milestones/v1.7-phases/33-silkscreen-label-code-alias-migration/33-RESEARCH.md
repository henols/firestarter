# Phase 33: Silkscreen Label → Code Alias Migration — Research

**Researched:** 2026-05-25
**Domain:** Firmware macro rename (`#define` substitution) with .hex byte-identical gate; cross-repo Python-mirror constants block; v1.7-SHIELD-REVS.md §7 schema fill
**Confidence:** HIGH

## Summary

Phase 33 is a hard rename — no behavior change, no struct change, no wire-format change. The work is mechanical: replace the existing shield-net-named macros in `firestarter/include/rurp_shield.h:25-89` with a canonical `CTRL_*` / `PIN_*` namespace in a new `firestarter/include/rurp_pinout.h`, rewrite **106 call-site references across 13 files** (95 lines in firmware src/include + 7 lines in native tests + 4 lines in the Python host docstring at `firestarter_app/firestarter/main.py:408-416`), and mirror a small `RURP_CONTROL_REGISTER_BITS` block in `firestarter_app/firestarter/constants.py`. Fill `.planning/v1.7-SHIELD-REVS.md` §7 with a per-rev silkscreen → alias table sourced from upstream `F_Silkscreen.gbr` (physically-printed labels) + per-rev `.kicad_sch` blobs (in-schematic-only net names) via the per-rev R41/JP4/A3 grep already captured in `mine-notes.md:427-510`.

The load-bearing constraint is **ALIAS-03 / GATE-1.7 .hex byte-identical for `uno` / `leonardo` / `uno328pb` modulo ≤ ~50 B**. Because `#define` is preprocessor-only substitution, the post-CPP token stream is literally identical (just renamed identifiers carry no AVR symbol-table footprint). `#define` is the project convention (`firestarter/include/rurp_shield.h` is built on `#define`; `constexpr` reserved for type-anchored host-test constants). Two subtle preservation requirements: (1) the `ADDRESS_LINE_16 == VPE_TO_VPP` aliasing in the legacy non-`HARDWARE_REVISION` path must carry through to identical aliasing in the new namespace; (2) the rev-dependent value mapping (`VPE_TO_VPP = 0x01` legacy vs `0x100` rev-2) must remain ifdef-gated.

**Primary recommendation:** Single-header substrate (`rurp_pinout.h`) included from `rurp_shield.h`, name-only rename via 4-wave subsystem split (header creation → control-register call-sites → board-ADC-pin call-sites → §7 fill + Python mirror), pre/post `cmp` of all 3 `.hex` artifacts captured in the wrap-up commit message.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**D-01: Combination source, desk-side, no operator photos needed.** Phase 33 pulls verbatim silkscreen labels from two upstream sources per rev:
- **Primary — physically-printed labels** (chip-socket pin labels VPP/VCC/GND/A0..A18/D0..D7/CE/OE/WE, plus shield-level R41, JP4, etc.): upstream `F_Silkscreen.gbr` per rev (already mined Phase 31 — see `mine-notes.md:427-510`). For each rev, `git show <commit>:hardware/<path>/F_Silkscreen.gbr` is grep-able for `%TO.C,<designator>*%` entries.
- **Secondary — in-schematic-only net names** (control-register bits like `VPE_ENABLE`, `REGULATOR`, `P1_VPP_ENABLE`, `A9_VPP_ENABLE`, `READ_WRITE`, `VPE_TO_VPP` — net labels INSIDE `.kicad_sch`, not physically printed): upstream per-rev `.kicad_sch` text grep (per-rev blobs already located in `mine-notes.md` — Rev2.0 blob `d2a7f691`, Rev2.1 `f3b7a521`, Rev2.3 `fe35bd78`).
- Both layers feed the §7 alias table. Each row records whether the label is silkscreen-printed (S) or schematic-net-only (N).

**D-02: Operator photos are NOT a Phase 33 blocker.** All three operator-on-hand boards (Rev 2.2 / Rev 2.0 / Modified Rev 0) remain `state: upstream-only`; photos blocked the Phase 31 session and are Phase 35 follow-ups #1/#2/#3.

**D-03: Alias scoping — RURP-shield-interface layer only.** Aliases for: (a) control-register bit names (8 bits in `rurp_shield.h:25-33` plus per-rev `REV_1_*` / `REV_2_*` equivalents at `:70-94`); (b) Arduino-pin assignments that map to RURP signals (`VOLTAGE_MEASURE_PIN A2`, `HARDWARE_REVISION_PIN A3`); (c) shield-level designators that appear in firmware logic (R41 detect-divider, JP4 VPP-jumper — Phase 34 will consume these). **NOT in scope:** JEDEC chip-pin layer (`pinouts.json`); AVR-PORT layer (`PORTD`/`PORTB`/`DDRD` masks); per-DIP socket-pin labels.

**D-04: Reuse existing `HARDWARE_REVISION` ifdef + `REV_1_*` / `REV_2_*` per-rev macro pattern.** Phase 33 extends — no new platformio envs, no new compile-time switch. Phase 34 layers runtime ADC-detect ON TOP OF the same substrate.

**D-05: New rev rows handled by mechanical extension.** Rev 2.3 inherits Rev 2.2's bit layout. Modified Rev 0: see D-09.

**D-06: Hard-rename via `#define` aliases — no shim, no backward-compat alias chain.** New canonical names land in `firestarter/include/rurp_pinout.h`. All 86+ current call-sites are rewritten. Old `#define`s in `rurp_shield.h:25-33` are REMOVED.

**D-07: Aliases use `#define`, not `constexpr` or `enum class`.** Preprocessor-only substitution → byte-identical compiled `.hex`. The ALIAS-03 ≤ ~50 B per-board allowance is held in reserve for edge cases; byte-identical .hex is the expected outcome.

**D-08: Minimal `constants.py` addition — control-register bit constants block.** Add a `# RURP Control Register Bits` block to `firestarter_app/firestarter/constants.py` mirroring the C++ `CTRL_*` names. Refresh the docstring at `firestarter_app/firestarter/main.py:408-415`. **Not in scope:** new `firestarter/rurp_pinout.py` module; no `eprom_operations.py` changes; no `database.py` changes.

**D-09: Modified Rev 0 row in §7 — explicit `pending Phase 35` sentinels for rework-touched cells.** Cells the rework touches carry `as-modified — pending Phase 35`; cells unaffected by rework inherit from parent Rev 0 with a `(inherits Rev 0)` note. **Firmware does NOT branch on Modified Rev 0** — no new `REVISION_MODIFIED_0` macro.

### Claude's Discretion

- **Plan-wave decomposition:** single big-bang wave vs subsystem-split. The subsystem-split is the natural shape because GATE-1.7 .hex byte-identical can be verified after each wave.
- **Exact naming of each alias** — derive from §7 source rows + the existing `rurp_shield.h:25-33` set. The `CTRL_*` vs `PIN_*` namespace split (`CTRL_*` for control-register bits, `PIN_*` for Arduino-pin assignments) is a planner refinement of the spec's single `PIN_*` namespace.
- **Order of §7 columns** — silkscreen label, alias name, type (S/N), per-rev applicability (`✓` / `not-present` / `pending Phase 35`), source citation.
- **Whether to bump `CONFIG_VERSION`** (currently `"VER06"`). EEPROM struct layout unchanged → stays at `"VER06"`. Planner verifies.

### Deferred Ideas (OUT OF SCOPE)

- **For Phase 34 discuss:** ADC voltage-band lookup table; Rev 2.2 R41 4k7-vs-10k discrepancy; runtime-detect plumbing extension.
- **For Phase 35:** §7 footnotes for ops-board silkscreen; README cross-links; PROJECT.md "Validated" entry; Modified Rev 0 §7 cell upgrade.
- **Out of v1.7 entirely:** AVR-PORT-layer aliases (PORTD/PORTB/DDRD masks); JEDEC chip-pin renaming; `firestarter/rurp_pinout.py` host module; PORTx mask migration; `constexpr`/`enum class` for control-register bits.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ALIAS-01 | Every silkscreen label across all known revs inventoried in `.planning/v1.7-SHIELD-REVS.md`; maps silkscreen → code-side alias (`PIN_<SUBSYSTEM>_<FUNCTION>` convention) | §7 column schema (Finding #5) + per-rev `mine-notes.md:427-510` blob grep evidence; CHAT-INTEL.md §1-§5 already accessible at `.planning/v1.7/notes/CHAT-INTEL.md` |
| ALIAS-02 | Aliases land as `#define` in `firestarter/include/rurp_pinout.h` + constants in `firestarter_app/firestarter/constants.py`; existing call-sites migrated | Exact 106-line call-site inventory (Finding #1); `ADDRESS_LINE_16 == VPE_TO_VPP` aliasing preservation pattern (Finding #3); `rurp_map_ctrl_reg_for_hardware_revision()` dispatcher textual-update-only mapping (Finding #4) |
| ALIAS-03 | GATE-1.7 non-regression — compiled `.hex` byte-identical for `uno`/`leonardo`/`uno328pb` modulo ≤ ~50 B; pytest + Unity green | Pre/post `cmp` protocol (Finding #2); `#define` preprocessor-only substitution preserves AVR token stream; `name_firmware.py` PROGNAME derivation is RURP_BOARD_NAME-driven (independent of alias names) |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

**Meta-repo `/workspaces/CLAUDE.md`:**
- Constants/flag bits duplicated between `firestarter_app/firestarter/constants.py` (Python) and `firestarter/include/firestarter.h` (C++). Change both together. Phase 33 D-08 extends this rule to also cover the new `CTRL_*` block.
- Serial protocol changes must be kept in sync between `firestarter_app/firestarter/serial_comm.py` and `firestarter/src/firestarter.cpp`. *(Phase 33 does NOT touch the wire protocol — no change here.)*
- Hardware calibration (R1/R2, board revision) persisted in Arduino EEPROM via `rurp_configuration_t`. *(Phase 33 does NOT touch this struct — `CONFIG_VERSION "VER06"` stays put.)*

**`/workspaces/firestarter/CLAUDE.md`:**
- Protocol dispatch invariants — order in `memory.cpp:configure_memory` is source-of-truth; **dispatch order must not change**. Phase 33 only renames identifiers; dispatch logic untouched.
- `KNOWN_PROTOCOLS` list unchanged: `0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39`.
- Control register bit constants in CLAUDE.md §Constants reference `REGULATOR (0x80)`, `VPE_TO_VPP (0x01)`, `P1_VPP_ENABLE (0x08)`, `A9_VPP_ENABLE (0x02)`, `VPE_ENABLE (0x04)` — **these CLAUDE.md docstrings must be refreshed to the new `CTRL_*` names** alongside the rename.
- Native test pattern: `host_stubs.cpp` per suite stubs `rurp_*` symbols; tests assert on `handle->firestarter_operation_main` and `handle->response_code` only — never on register side effects. The native dispatch tests are name-only sensitive (any TU referencing `REGULATOR` etc. needs the same rename).

**`/workspaces/firestarter_app/CLAUDE.md`:**
- `firestarter/constants.py` must stay in sync with `firestarter/include/firestarter.h`. **Phase 33 expands this sync to also cover `rurp_pinout.h` for the new `RURP_CONTROL_REGISTER_BITS` block.** Update the sync-rule prose if planner wants it explicit (recommended).
- The protocol dispatch override (DIP28_2764 + 0x07 → 0x0D) is a `build_db.py` concern; Phase 33 does not touch this.
- Regression guard `tools/check_dispatch.py` is unaffected.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Control-register bit naming | Firmware (C++ header) | Python host (mirror constants) | Bits are written by firmware to the 74HC573 latch; Python only references them in documentation/debug commands |
| Arduino-pin assignment naming (A2/A3) | Firmware (C++ header) | — | Pin numbers are AVR-only; Python never references them |
| Silkscreen → alias canonical table | Meta-repo (`.planning/v1.7-SHIELD-REVS.md` §7) | — | Documentation artifact; both sub-repos cross-link in Phase 35 |
| Per-rev ifdef gating | Firmware build (`platformio.ini -D HARDWARE_REVISION`) | — | Compile-time only; Phase 34 extends with runtime ADC detect on top |
| EEPROM struct layout (`rurp_configuration_t`) | Firmware | — | Phase 33 does NOT modify struct; `CONFIG_VERSION "VER06"` stays |
| .hex artifact filename derivation | Firmware build (`name_firmware.py` + `RURP_BOARD_NAME` build_flag) | — | Already locked; alias rename has zero impact on PROGNAME |

## Standard Stack

This is an existing-codebase rename, not a new-library install. There is no new dependency.

### Core (existing — no version change)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| PlatformIO `atmelavr` | (pinned in `platformio.ini`) | AVR build environment for `uno` / `uno328pb` / `leonardo` | Existing project substrate |
| MiniCore | (pinned) | ATmega328PB Arduino framework | v1.5 lock; unchanged by Phase 33 |
| Unity (PIO `test_framework = unity`) | (pinned) | Native test suite for `configure_memory` dispatch + flash_intel VPP + eeprom28c chip_id | Phase 33 must keep Unity green |
| pytest | (pinned via firestarter_app pyproject) | Host CLI test suite | Phase 33 must keep pytest green |

**No new packages.** [VERIFIED: project codebase inspection — `firestarter/platformio.ini`, `firestarter_app/pyproject.toml`]

## Package Legitimacy Audit

Not applicable — Phase 33 installs no new packages. The rename is name-only across existing source files. No `pip install`, no `npm install`, no PlatformIO `lib_deps` additions.

## Architecture Patterns

### System Architecture Diagram

```
                  ┌─────────────────────────────────────────────┐
                  │  v1.7-SHIELD-REVS.md §7 (canonical table)   │
                  │   silkscreen → alias  (per-rev S/N rows)    │
                  └────────────────┬────────────────────────────┘
                                   │ (drives naming)
                                   ▼
                  ┌─────────────────────────────────────────────┐
                  │  firestarter/include/rurp_pinout.h  (NEW)   │
                  │   #define CTRL_VPP_REGULATOR_ENABLE 0x80    │
                  │   #define CTRL_VPP_VPE_DROP_ENABLE  0x01    │
                  │   #define CTRL_ADDRESS_LINE_16      ...     │
                  │   #define PIN_VPP_VOLTAGE_ADC       A2      │
                  │   #define PIN_HW_REVISION_DETECT_ADC A3     │
                  │   (legacy ifdef + REV_2_* per-rev variants) │
                  └────────────────┬────────────────────────────┘
                                   │
              ┌────────────────────┼────────────────────────┐
              ▼                    ▼                        ▼
   ┌──────────────────┐  ┌────────────────────┐  ┌──────────────────────────┐
   │ rurp_shield.h    │  │ rurp_hw_rev_utils  │  │ src/proms/*.cpp (5)      │
   │ #include         │  │ + rurp_register_   │  │  + src/hardware_         │
   │  rurp_pinout.h   │  │ utils.h            │  │ operations.cpp           │
   │ (old #defines    │  │ (dispatcher uses   │  │  + src/boards/*.cpp      │
   │  REMOVED)        │  │ new names; logic   │  │ (call-sites: 95 lines    │
   │                  │  │ unchanged)         │  │  rewritten verbatim)     │
   └──────────────────┘  └────────────────────┘  └──────────────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────────────────┐
                  │  AVR ELF → name_firmware.py → .hex          │
                  │  cmp pre.hex post.hex  →  byte-identical    │
                  │  (uno + uno328pb + leonardo)                │
                  └─────────────────────────────────────────────┘

                  ┌─────────────────────────────────────────────┐
                  │  firestarter_app/firestarter/constants.py   │
                  │   # RURP Control Register Bits  (new block) │
                  │   CTRL_VPP_REGULATOR_ENABLE = 0x80          │
                  │   ... (mirrors C++ #defines, no logic)      │
                  └─────────────────────────────────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────────────────┐
                  │  firestarter_app/firestarter/main.py:408-15 │
                  │   docstring updated to new CTRL_* names     │
                  └─────────────────────────────────────────────┘
```

### Recommended Project Structure

The new pinout header lives in `firestarter/include/` alongside the other rurp_*.h files:

```
firestarter/
├── include/
│   ├── rurp_pinout.h               # NEW — Phase 33 canonical macros
│   ├── rurp_shield.h               # existing — #include rurp_pinout.h; old #defines REMOVED
│   ├── rurp_hw_rev_utils.h         # existing — body unchanged, references new names
│   ├── rurp_register_utils.h       # existing — body unchanged, references new names
│   ├── firestarter.h               # existing — unchanged (struct + flag bits, not pin/register layer)
│   └── ...
├── src/
│   ├── proms/{eprom,flash_type_4,flash_intel,eeprom_28c,flash_utils,memory}.cpp   # rewritten call-sites
│   ├── boards/{uno_rurp_shield,leonardo_rurp_shield,rurp_common}.cpp              # rewritten call-sites (1-2 each)
│   └── hardware_operations.cpp     # rewritten (2 lines)
└── test/
    └── native/avr/
        └── test_flash_intel_vpp/test_flash_intel_vpp.cpp   # 7 lines rewritten

firestarter_app/firestarter/
├── constants.py                    # + RURP_CONTROL_REGISTER_BITS block (mirror C++)
└── main.py:408-416                 # docstring refreshed to new CTRL_* names

.planning/
└── v1.7-SHIELD-REVS.md             # §7 filled in-place
```

### Pattern 1: `#define`-based aliases via dedicated header

**What:** New macros land in a dedicated `rurp_pinout.h` header; `rurp_shield.h` includes it via `#include "rurp_pinout.h"` (or hosts it inline within the existing `#ifndef HARDWARE_REVISION` / `#ifdef HARDWARE_REVISION` gating).

**When to use:** All Phase 33 macro definitions.

**Example (Pattern 1A — separate header, recommended for cleanest call-site grep):**
```c
// firestarter/include/rurp_pinout.h
#ifndef __RURP_PINOUT_H__
#define __RURP_PINOUT_H__

// === Arduino-pin assignments (RURP signal layer) ===
#define PIN_VPP_VOLTAGE_ADC           A2   // formerly VOLTAGE_MEASURE_PIN
#ifdef HARDWARE_REVISION
#define PIN_HW_REVISION_DETECT_ADC    A3   // formerly HARDWARE_REVISION_PIN
#endif

// === Control register bit positions ===
#ifndef HARDWARE_REVISION
// Legacy single-rev layout (matches rurp_shield.h:25-33 pre-Phase-33)
#define CTRL_VPP_VPE_DROP_ENABLE      0x01   // formerly VPE_TO_VPP
#define CTRL_ADDRESS_LINE_16          CTRL_VPP_VPE_DROP_ENABLE  // aliased — bits share
#define CTRL_VPP_A9_ENABLE            0x02   // formerly A9_VPP_ENABLE
#define CTRL_VPE_ENABLE               0x04   // formerly VPE_ENABLE
#define CTRL_VPP_P1_ENABLE            0x08   // formerly P1_VPP_ENABLE
#define CTRL_ADDRESS_LINE_17          0x10
#define CTRL_ADDRESS_LINE_18          0x20
#define CTRL_READ_WRITE               0x40   // formerly READ_WRITE
#define CTRL_VPP_REGULATOR_ENABLE     0x80   // formerly REGULATOR
#else
// Per-rev wide layout (matches rurp_shield.h:43-51 + :70-94)
#define CTRL_ADDRESS_LINE_16          0x01
#define CTRL_VPP_A9_ENABLE            0x02
#define CTRL_VPE_ENABLE               0x04
#define CTRL_VPP_P1_ENABLE            0x08
#define CTRL_ADDRESS_LINE_17          0x10
#define CTRL_ADDRESS_LINE_18          0x20
#define CTRL_READ_WRITE               0x40
#define CTRL_VPP_REGULATOR_ENABLE     0x80
#define CTRL_VPP_VPE_DROP_ENABLE      0x100

// Per-rev bit variants for rurp_map_ctrl_reg_for_hardware_revision()
#define CTRL_VPP_VPE_DROP_ENABLE_REV1   0x01
#define CTRL_VPP_A9_ENABLE_REV1         0x02
// ... etc, mirroring REV_1_* / REV_2_* block at :70-94
#define CTRL_ADDRESS_LINE_18_REV2       CTRL_VPP_P1_ENABLE  // aliased — bits share
#endif

#endif // __RURP_PINOUT_H__
```

The `#include "rurp_pinout.h"` lands right under the existing `#include "rurp_types.h"` in `rurp_shield.h:19`. The 8-bit `#define VPE_TO_VPP 0x01` lines at `:25-33` and the per-rev REV_* block at `:70-94` are DELETED. Per `firestarter/CLAUDE.md` §Constants the docstring there is refreshed to the new names.

### Pattern 2: Hard-rename via grep + sed (no shim)

**What:** No `#define VPE_ENABLE CTRL_VPE_ENABLE` backward-compat alias. Old names disappear from the codebase entirely. Call-sites are rewritten verbatim, one file at a time, in commit-sized batches per wave.

**When to use:** All 106 call-sites + 4 docstring lines + 7 test-file references.

**Example operation per file (mechanical):**
```bash
# After verifying pre.hex captured for all 3 envs:
sed -i 's/\bVPE_TO_VPP\b/CTRL_VPP_VPE_DROP_ENABLE/g' src/proms/*.cpp src/proms/*.h
sed -i 's/\bREGULATOR\b/CTRL_VPP_REGULATOR_ENABLE/g' src/proms/*.cpp
# etc.
# Then build + cmp .hex
```

The planner SHOULD prefer per-task explicit `Edit`s over a single `sed` to keep the diffs reviewable and to catch incidental hits (e.g. the word `REGULATOR` could appear in a comment that's better preserved verbatim — the comment block in `rurp_shield.h:23` "CONTROL REGISTER" is NOT a `#define REGULATOR` consumer).

### Pattern 3: `rurp_map_ctrl_reg_for_hardware_revision()` is textual-update-only

**What:** The dispatcher in `rurp_hw_rev_utils.h:13-35` maps canonical bit positions to per-rev bit positions. Its body references `A9_VPP_ENABLE | VPE_ENABLE | P1_VPP_ENABLE | ...` (canonical input mask) on the left, and `REV_2_VPE_TO_VPP | REV_2_ADDRESS_LINE_16 | REV_2_ADDRESS_LINE_18 | REV_1_VPE_TO_VPP` (per-rev output bits) on the right. After rename: input mask becomes `CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE | CTRL_VPP_P1_ENABLE | ...`; output bits become `CTRL_VPP_VPE_DROP_ENABLE_REV2 | CTRL_ADDRESS_LINE_16_REV2 | CTRL_ADDRESS_LINE_18_REV2 | CTRL_VPP_VPE_DROP_ENABLE_REV1`. The switch-case structure is **unchanged** (same `case REVISION_2_0:` / `case REVISION_2_1:` / `case REVISION_2_2:` block; same `case REVISION_0:` / `case REVISION_1:` block). The `REVISION_0` / `REVISION_1` / `REVISION_2_*` constants in `rurp_shield.h:37-41` are NOT renamed (they are revision enum values, not RURP signal aliases — out of D-03 scope).

### Pattern 4: Python-side parity (D-08)

**What:** Add a single new constants block to `firestarter_app/firestarter/constants.py` mirroring the C++ `CTRL_*` names with the same hex values. No new Python module file (no `rurp_pinout.py`). Refresh `main.py:408-416` docstring.

**Example:**
```python
# constants.py — append after the existing FLAG_* block

# RURP Control Register Bits — mirror of firestarter/include/rurp_pinout.h
# Documentary only — Python does not write the control register directly
# (firmware owns that). Used by `firestarter dev registers --firestarter`
# and similar host-side helpers. Keep in sync per CLAUDE.md sync rule.
CTRL_VPP_VPE_DROP_ENABLE     = 0x100   # was VPE_TO_VPP (wide layout)
CTRL_VPP_REGULATOR_ENABLE    = 0x080   # was REGULATOR
CTRL_READ_WRITE              = 0x040   # was READ_WRITE
CTRL_ADDRESS_LINE_18         = 0x020
CTRL_ADDRESS_LINE_17         = 0x010
CTRL_VPP_P1_ENABLE           = 0x008   # was P1_VPP_ENABLE
CTRL_VPE_ENABLE              = 0x004   # was VPE_ENABLE
CTRL_VPP_A9_ENABLE           = 0x002   # was A9_VPP_ENABLE
CTRL_ADDRESS_LINE_16         = 0x001
```

The corresponding docstring rewrite in `main.py:408-416`:

```python
#  0x100 - CTRL_VPP_VPE_DROP_ENABLE
#  0x080 - CTRL_VPP_REGULATOR_ENABLE
#  0x040 - CTRL_READ_WRITE
#  0x020 - CTRL_ADDRESS_LINE_18
#  0x010 - CTRL_ADDRESS_LINE_17
#  0x008 - CTRL_VPP_P1_ENABLE
#  0x004 - CTRL_VPE_ENABLE
#  0x002 - CTRL_VPP_A9_ENABLE
#  0x001 - CTRL_ADDRESS_LINE_16
```

### Anti-Patterns to Avoid

- **Backward-compat alias chain.** `#define VPE_ENABLE CTRL_VPE_ENABLE` shims pollute the call-site grep + give future maintainers two names for one bit. Per D-06, hard-rename.
- **`constexpr uint8_t REGULATOR = 0x80;` translation.** AVR-objcopy MAY emit symbol metadata that pushes .hex size up; the project convention is `#define`. Per D-07.
- **Renaming `REVISION_0` / `REVISION_1` / `REVISION_2_*`** in `rurp_shield.h:37-41`. These are revision-enum values (not RURP-signal layer per D-03). Leave them alone.
- **Touching PORTD/PORTB/DDRD masks** in `uno_rurp_shield.cpp`/`leonardo_rurp_shield.cpp`. MCU-internal layer, out of D-03.
- **Bumping `CONFIG_VERSION`** (`rurp_shield.h:93`). EEPROM struct layout is unchanged; bumping the version would invalidate every operator's calibration data.
- **Renaming `CONTROL_REGISTER` / `LEAST_SIGNIFICANT_BYTE` / `MOST_SIGNIFICANT_BYTE` / `OUTPUT_ENABLE` / `CHIP_ENABLE`** (`rurp_shield.h:100-104`). These are 74HC573 latch selectors, NOT control-register bit names — different semantic layer. Out of scope.
- **Auto-applying `sed -i` across the entire tree in one shot.** Easy to hit a comment that meant the OLD name in a historic sense (e.g. `rurp_shield.h:62-63` comments document the old `VPE_ENABLE → P1_VPP_ENABLE` redirect; those comments need refreshing or rewording, but mechanical `sed` may rewrite them awkwardly).
- **Modifying `chip_database.json`** or any data file. Phase 33 is code-only.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Pre/post-rename .hex equivalence check | Custom hash-diff script | `cmp` (or `sha256sum` x2) | UNIX-standard, atomic, exits non-zero on diff. Intel HEX is a text format, so byte-identical is meaningful. |
| .hex artifact path resolution | Hardcoded paths | `.pio/build/<env>/firestarter_<RURP_BOARD_NAME>.hex` | Already locked by `name_firmware.py`; PROGNAME derives from `RURP_BOARD_NAME` build_flag (NOT alias names). |
| Per-rev macro variant gating | New compile-time switch (e.g. `-D RURP_REV_2_2`) | Existing `-D HARDWARE_REVISION` (set in `platformio.ini:23` for all 3 AVR envs) + `REVISION_*` enum at runtime via `rurp_get_hardware_revision()` | D-04 reuse; matches the substrate Phase 34 will extend with ADC detect. |
| Backward-compat shim for old names | `#define VPE_ENABLE CTRL_VPE_ENABLE` | Hard rename — `git grep` confirms zero remaining references to old names | D-06; project posture is small atomic diffs, no orphan symbols. |
| Python-side `rurp_pinout.py` mirror | Full Python module | Single `RURP_CONTROL_REGISTER_BITS` block in existing `constants.py` | D-08; Python is documentary-only at this layer (doesn't build bus_config payloads). |
| New §7 column count from scratch | Reinvent inventory schema | Reuse Phase 31 D-10 schema shape (silkscreen-first column, per-rev applicability columns) with column-set adapted for alias content (Finding #5) | Phase 31 already locked column ordering for §1; §7 inherits the column-style conventions. |

**Key insight:** Phase 33 is structurally a textual edit. The complexity is in the **silkscreen → alias mapping** (Finding #6, naming discipline) and the **rev-dependent aliasing semantics** (Finding #3, `ADDRESS_LINE_16 == VPE_TO_VPP` in legacy path, distinct values in Rev 2 path). The build / verification machinery (`pio run`, `cmp`, `pytest`, `pio test -e native`) is already in place — no new tooling.

## Runtime State Inventory

> Required because Phase 33 is a rename across firmware + Python host.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| **Stored data** | **None.** No database stores `VPE_ENABLE` / `REGULATOR` / etc. as a key or value. `chip_database.json` references chip-level data (algorithm, vpp_mv, pin_count, pinout); no shield-net names. `pinouts.json` references JEDEC chip-pin names (VPP, CE, OE), not control-register bits. Verified by: `grep -r "VPE_ENABLE\|VPE_TO_VPP\|REGULATOR" firestarter_app/firestarter/data/ → 0 hits`. | None |
| **Live service config** | **None.** No external service (n8n, Datadog, Tailscale, etc.) embeds these names. Project is local firmware + CLI. | None |
| **OS-registered state** | **None.** No Windows Task Scheduler / launchd / systemd / pm2 entries reference RURP signal names. | None |
| **Secrets / env vars** | **None.** Project has no `.env` containing RURP signal names; no SOPS keys named after them; no CI secret named after them. Verified by inspection of `.github/workflows/` in both sub-repos. | None |
| **Build artifacts / installed packages** | `.pio/build/<env>/firestarter_<env>.hex` and `.pio/build/<env>/firestarter.elf` already present on disk. These are stale relative to post-rename source. **Action:** the pre-migration `.hex` capture step (Finding #2) MUST run BEFORE the rename touches any source file, because re-building post-rename would overwrite them. Recommended: copy each pre-rename `.hex` to `.planning/v1.7/phase-33-baseline-hex/<env>.hex` (gitignored under D-11 v1.7/) before the first rename commit lands. | Capture .hex baseline before first source edit |

**Canonical assertion:** After every file in the repo is updated, the only runtime systems with the old strings cached are (a) the on-disk .pio build cache (cleared by `pio run` rebuild), (b) the pre-rename .hex baseline copies (intentionally retained for diff). Nothing else.

## Common Pitfalls

### Pitfall 1: `ADDRESS_LINE_16` and `VPE_TO_VPP` share a bit in the legacy path
**What goes wrong:** A naive rename that introduces `CTRL_ADDRESS_LINE_16 = 0x01` AND `CTRL_VPP_VPE_DROP_ENABLE = 0x01` as two independent `#define`s in the legacy `#ifndef HARDWARE_REVISION` path — losing the explicit `#define ADDRESS_LINE_16 VPE_TO_VPP` aliasing at `rurp_shield.h:26`.
**Why it happens:** The aliasing is load-bearing — A16 signal multiplexes with the VPE-to-VPP dropping-resistor enable on Rev 0/1 boards. Code at `src/proms/memory.cpp:142-144` explicitly comments: *"VPE_TO_VPP and ADDRESS_LINE_16 share the same CONTROL bit — preserving VPE_TO_VPP would corrupt A16 for 32-pin (512KB) chips."* Losing this aliasing would make A16 and VPP-drop independently writable in code where the firmware currently relies on them being the same bit.
**How to avoid:** In `rurp_pinout.h`'s `#ifndef HARDWARE_REVISION` block, define `CTRL_VPP_VPE_DROP_ENABLE 0x01` AS THE LITERAL VALUE, then `#define CTRL_ADDRESS_LINE_16 CTRL_VPP_VPE_DROP_ENABLE` AS A MACRO ALIAS. In the `#ifdef HARDWARE_REVISION` block, define them with distinct hex values (`CTRL_ADDRESS_LINE_16 0x01`, `CTRL_VPP_VPE_DROP_ENABLE 0x100`) — same as the current `rurp_shield.h:43, :51` shape.
**Warning signs:** After rename, `cmp pre.hex post.hex` on `uno` (legacy path — `uno` does set `-D HARDWARE_REVISION` per `platformio.ini:23`, so this pitfall surfaces on the native test path, not on `uno`. But the native test path **doesn't** set `HARDWARE_REVISION`, so this pitfall hits the Unity build. Check `test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp` references.).

> **Subtle correction:** All 3 AVR envs (`uno`, `uno328pb`, `leonardo`) set `-D HARDWARE_REVISION` (`platformio.ini:23` is at `[env]` scope and inherits). The legacy non-HARDWARE_REVISION code path is the **native test build** only. So the aliasing trap is most likely to surface during `pio test -e native`, not during `pio run -e uno`. Plan accordingly: run the native test suite in every wave's verification step.

### Pitfall 2: Per-rev `VPE_TO_VPP` value is `0x01` legacy vs `0x100` in HARDWARE_REVISION path
**What goes wrong:** Single new `#define CTRL_VPP_VPE_DROP_ENABLE 0x01` outside the ifdef → silently changes the value on AVR builds where the current path has `0x100`.
**Why it happens:** The current `rurp_shield.h` declares `VPE_TO_VPP 0x01` at `:25` (legacy) and re-declares `VPE_TO_VPP 0x100` at `:51` (HARDWARE_REVISION) — the ifdef sets which one wins. The rename must preserve the ifdef gate.
**How to avoid:** Mirror the existing ifdef structure verbatim. The new `rurp_pinout.h` has the same `#ifndef HARDWARE_REVISION` / `#else` / `#endif` shape.
**Warning signs:** Bit-mask math in `memory.cpp:139-144` will diverge silently; `top_address` computation will use the wrong bit.

### Pitfall 3: `rurp_map_ctrl_reg_for_hardware_revision()` references BOTH canonical and REV-prefixed names
**What goes wrong:** Rename the canonical input mask (`A9_VPP_ENABLE | VPE_ENABLE | ...`) but forget to rename the per-rev output bits (`REV_2_VPE_TO_VPP | REV_2_ADDRESS_LINE_16 | REV_2_ADDRESS_LINE_18 | REV_1_VPE_TO_VPP`) at `rurp_hw_rev_utils.h:21-28`.
**Why it happens:** Two namespaces in the same function body. Easy to miss the right-hand-side names during call-site sweep.
**How to avoid:** When auditing `rurp_hw_rev_utils.h:13-35`, enumerate both LHS and RHS macro references. The new `CTRL_*_REV1` and `CTRL_*_REV2` names should be defined alongside the canonical `CTRL_*` names in `rurp_pinout.h`. After rename, `git grep "REV_[12]_" firestarter/` should return 0 hits (other than in the renaming commit's diff itself).
**Warning signs:** Build fails to compile (unresolved symbol) — easy to catch. The risk is if the planner forgets to add the REV-prefixed new names, the dispatcher becomes a no-op.

### Pitfall 4: PROGNAME / .hex filename derives from `RURP_BOARD_NAME`, NOT alias names
**What goes wrong:** Concern that "renaming aliases changes the .hex output filename or path" — it does not.
**Why it happens:** `name_firmware.py:60-61` derives PROGNAME from the `RURP_BOARD_NAME` build_flag (`uno` / `uno328pb` / `leonardo` per env). Alias renames inside source files do not touch PROGNAME.
**How to avoid:** No action — just understand the boundary. `.hex` filenames stay: `firestarter_uno.hex`, `firestarter_uno328pb.hex`, `firestarter_leonardo.hex`. The `cmp` is on filenames that are stable across the rename.
**Warning signs:** If `.hex` filenames change after the rename, something else is broken (likely an accidental edit to `platformio.ini` build_flags).

### Pitfall 5: `CONFIG_VERSION "VER06"` accidentally bumped
**What goes wrong:** Reflexive instinct to bump `CONFIG_VERSION` because a firmware change happened.
**Why it happens:** Project convention bumps `CONFIG_VERSION` when `rurp_configuration_t` struct layout changes (so EEPROM-stored calibration data with the old layout is recognized as stale). Phase 33 does NOT change the struct layout — only macro names.
**How to avoid:** Verify the struct definition in `include/rurp_types.h` is byte-identical pre/post; explicitly NOT touch `rurp_shield.h:93` `#define CONFIG_VERSION "VER06"`.
**Warning signs:** Operator's calibrated R1/R2 values reset to defaults after firmware reflash — would indicate accidental struct or version drift.

### Pitfall 6: Native test suite (`test_flash_intel_vpp.cpp`) references old names
**What goes wrong:** Migration sweeps `firestarter/src/` and `firestarter/include/` but misses `firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp` (7 lines reference `REGULATOR | P1_VPP_ENABLE`).
**Why it happens:** Easy to forget the test/ subtree in a `grep -rn include/ src/` sweep.
**How to avoid:** Explicit grep also against `test/`. The post-rename verification command must include the test path: `grep -rn "VPE_ENABLE\|VPE_TO_VPP\|P1_VPP_ENABLE\|A9_VPP_ENABLE\|READ_WRITE\|REGULATOR\|HARDWARE_REVISION_PIN\|VOLTAGE_MEASURE_PIN" include/ src/ test/`.
**Warning signs:** `pio test -e native` build fails post-rename — unresolved symbol on `REGULATOR`.

### Pitfall 7: Modified Rev 0 mistakenly gets a new ifdef branch
**What goes wrong:** Planner adds a `REVISION_MODIFIED_0 5` enum value + new `#ifdef MODIFIED_REV_0` block.
**Why it happens:** Misreading D-09 — Modified Rev 0 needs `pending Phase 35` sentinels in the §7 TABLE, not new firmware compile-time branches.
**How to avoid:** Per D-09, "Firmware does NOT branch on Modified Rev 0 — at compile time it's indistinguishable from Rev 0." No new `REVISION_*` enum value.
**Warning signs:** The `REVISION_0..REVISION_2_2` block at `rurp_shield.h:37-41` grows beyond 5 entries.

## Code Examples

Verified patterns from project source files:

### Existing `#define`-based macro layer (target shape for the new header)
```c
// Source: firestarter/include/rurp_shield.h:21-53 (pre-Phase-33)
#define VOLTAGE_MEASURE_PIN A2

#ifndef HARDWARE_REVISION
#define VPE_TO_VPP      0x01
#define ADDRESS_LINE_16             VPE_TO_VPP
#define A9_VPP_ENABLE   0x02
#define VPE_ENABLE      0x04
#define P1_VPP_ENABLE   0x08
#define ADDRESS_LINE_17             0x10
#define ADDRESS_LINE_18             0x20
#define READ_WRITE      0x40
#define REGULATOR       0x80

#else
#define HARDWARE_REVISION_PIN A3
#define REVISION_0 0
#define REVISION_1 1
#define REVISION_2_0 2
#define REVISION_2_1 3
#define REVISION_2_2 4

#define ADDRESS_LINE_16             0x01
#define A9_VPP_ENABLE   0x02
#define VPE_ENABLE      0x04
#define P1_VPP_ENABLE   0x08
#define ADDRESS_LINE_17             0x10
#define ADDRESS_LINE_18             0x20
#define READ_WRITE      0x40
#define REGULATOR       0x80
#define VPE_TO_VPP      0x100
#endif
```

### Existing call-site usage (representative)
```c
// Source: firestarter/src/proms/eprom.cpp:143-149 (pre-Phase-33)
if (handle->firestarter_get_control_register(handle, REGULATOR) == 0) {
    if (handle->protocol == FLASH_LEGACY) {
        // EPROM_LEGACY: direct VPE path — no VPE_TO_VPP dropping resistor
        handle->firestarter_set_control_register(handle, REGULATOR, 1);
    } else {
        // EPROM_STD / EPROM_QUICK: VPE_TO_VPP dropping path for precise VPP
        handle->firestarter_set_control_register(handle, REGULATOR | VPE_TO_VPP, 1);
    }
}
```

After Phase 33 rename:
```c
if (handle->firestarter_get_control_register(handle, CTRL_VPP_REGULATOR_ENABLE) == 0) {
    if (handle->protocol == FLASH_LEGACY) {
        // EPROM_LEGACY: direct VPE path — no CTRL_VPP_VPE_DROP_ENABLE dropping resistor
        handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);
    } else {
        // EPROM_STD / EPROM_QUICK: CTRL_VPP_VPE_DROP_ENABLE dropping path for precise VPP
        handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE, 1);
    }
}
```

### Existing dispatcher (preservation target — Pattern 3)
```c
// Source: firestarter/include/rurp_hw_rev_utils.h:13-35 (pre-Phase-33)
uint8_t rurp_map_ctrl_reg_for_hardware_revision(rurp_register_t data) {
    uint8_t ctrl_reg = 0;
    uint8_t hw = rurp_get_hardware_revision();
    switch (hw) {
    case REVISION_2_0:
    case REVISION_2_1:
    case REVISION_2_2:
        ctrl_reg = data & (A9_VPP_ENABLE | VPE_ENABLE | P1_VPP_ENABLE | ADDRESS_LINE_17 | READ_WRITE | REGULATOR);
        ctrl_reg |= data & VPE_TO_VPP ? REV_2_VPE_TO_VPP : 0;
        ctrl_reg |= data & ADDRESS_LINE_16 ? REV_2_ADDRESS_LINE_16 : 0;
        ctrl_reg |= data & ADDRESS_LINE_18 ? REV_2_ADDRESS_LINE_18 : 0;
        break;
    case REVISION_0:
    case REVISION_1:
        ctrl_reg = data;
        ctrl_reg |= data & VPE_TO_VPP ? REV_1_VPE_TO_VPP : 0;
        break;
    default:
        break;
    }
    return ctrl_reg;
}
```

The function signature, the `switch` shape, the case-fallthrough on Rev 2.0/2.1/2.2, and the `REVISION_*` constants stay verbatim. Only the macro names inside the function body change. This is Finding #4.

## Exact Call-Site Inventory

Verified by `grep -rn "VPE_ENABLE\|VPE_TO_VPP\|P1_VPP_ENABLE\|A9_VPP_ENABLE\|READ_WRITE\|REGULATOR\|HARDWARE_REVISION_PIN\|VOLTAGE_MEASURE_PIN\|ADDRESS_LINE_1[678]\|ADDRESS_LINE_13" include/ src/ test/` against the current `v1.7-shield-investigation` working tree on 2026-05-25:

| File | Matching lines | Notes |
|------|---------------|-------|
| `firestarter/include/rurp_shield.h` | **39** | The old `#define`s themselves + comments referencing names. After Phase 33, only the per-rev `REVISION_*` enum block + the latch selectors (`LEAST_SIGNIFICANT_BYTE` etc.) remain in this file. |
| `firestarter/src/proms/eprom.cpp` | **22** | Largest call-site cluster — UV-EPROM handler (alg 0x07/0x08/0x0B), all `REGULATOR | VPE_TO_VPP` / `A9_VPP_ENABLE | VPE_ENABLE` patterns. |
| `firestarter/include/rurp_hw_rev_utils.h` | **10** | Dispatcher (Pattern 3) + `rurp_detect_hardware_revision()` body. |
| `firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp` | **7** | Test references `REGULATOR | P1_VPP_ENABLE`. Pitfall 6. |
| `firestarter/src/proms/flash_intel.cpp` | **7** | Intel 28F flash handler (alg 0x10) — all `REGULATOR | P1_VPP_ENABLE` patterns. |
| `firestarter/src/proms/memory.cpp` | **6** | Top-level dispatch + bus_config bit-mask math at `:139-144` (includes the load-bearing `ADDRESS_LINE_16 == VPE_TO_VPP` comment — Pitfall 1). |
| `firestarter/src/proms/flash_utils.cpp` | **3** | `READ_WRITE` toggle (flash write enable). |
| `firestarter/src/proms/flash_type_4.cpp` | **3** | Page-write flash (alg 0x05/0x35/0x39). |
| `firestarter/src/proms/eeprom_28c.cpp` | **3** | AT28C-series EEPROM (alg 0x0D). |
| `firestarter/src/hardware_operations.cpp` | **2** | `hw_read_voltage()` — VPP vs VPE selection at `:27, :30`. |
| `firestarter/include/rurp_register_utils.h` | **2** | `rurp_write_to_register()` settle-delay check on `P1_VPP_ENABLE` clear (`:17, :42`). |
| `firestarter/src/boards/uno_rurp_shield.cpp` | **1** | Comment-only reference to `READ_WRITE`. |
| `firestarter/src/boards/rurp_common.cpp` | **1** | `analogRead(VOLTAGE_MEASURE_PIN)` (`:58`). |
| **Total firmware** | **106** | (95 in include/src + 7 in test/ + 4 docstring lines in main.py — see Python below) |

**Python-side (per D-08):**
| File | Matching lines | Notes |
|------|---------------|-------|
| `firestarter_app/firestarter/main.py:408-416` | **9 lines** (one per bit) | Docstring inside `reg_parser.add_argument("-f", ...)` help text. Refresh to new `CTRL_*` names. |
| `firestarter_app/firestarter/constants.py` | **0 currently → +9 new** | Add new `# RURP Control Register Bits` block (Pattern 4). |

**Verification command for post-rename:** the planner SHOULD include a task that runs `grep -rn "\\bVPE_ENABLE\\b\\|\\bVPE_TO_VPP\\b\\|\\bP1_VPP_ENABLE\\b\\|\\bA9_VPP_ENABLE\\b\\|\\bREAD_WRITE\\b\\|\\bREGULATOR\\b\\|\\bHARDWARE_REVISION_PIN\\b\\|\\bVOLTAGE_MEASURE_PIN\\b" firestarter/include/ firestarter/src/ firestarter/test/` and assert 0 hits. Use word boundaries (`\\b`) to avoid false positives on `REGULATOR` appearing in comments (e.g. "CONTROL REGISTER" header at `rurp_shield.h:23` is a comment — not a `#define REGULATOR` consumer).

## §7 Column Schema (Phase 33 deliverable)

Per Finding #5 — Phase 31 D-10 established a 9-column inventory schema for §1. Phase 33 §7 needs its own column shape because the row content is different (silkscreen-keyed, not rev-keyed).

**Recommended column shape:**

| silkscreen_label | label_type | canonical_alias | hex_value (legacy / rev2) | rev_0 | rev_1 | rev_2_0 | rev_2_1 | rev_2_2 | rev_2_3 | mod_rev_0 | source_citation |
|------------------|-----------|------------------|----------------------------|-------|-------|---------|---------|---------|---------|-----------|------------------|

**Column semantics:**

- **silkscreen_label** (str) — verbatim label as it appears on the PCB silkscreen or as a net name in the .kicad_sch (e.g. `VPP_EN`, `R41`, `JP4`, `A3`).
- **label_type** (enum: `S` / `N`) — `S` if physically printed on PCB silkscreen (visible to operator with the chip socketed); `N` if schematic-net-only (visible only when reading the .kicad_sch source).
- **canonical_alias** (str) — the new code-side name, e.g. `CTRL_VPE_ENABLE`, `PIN_HW_REVISION_DETECT_ADC`, `RES_HW_REVISION_DIVIDER`.
- **hex_value** (str) — the bit's mask in the format `0x01 / 0x100` for bits whose value differs between legacy and HARDWARE_REVISION paths (per Pitfall 2). For Arduino-pin assignments, e.g. `A3`.
- **rev_0 / rev_1 / rev_2_0 / rev_2_1 / rev_2_2 / rev_2_3** (enum: `✓` / `not-present` / `pending Phase 35`) — per-rev applicability.
- **mod_rev_0** (enum: `(inherits Rev 0)` / `as-modified — pending Phase 35`) — D-09 sentinel; cells the rework touches carry the pending sentinel.
- **source_citation** (str) — gerber blob SHA + line refs OR schematic blob SHA + line refs (per the Phase 31 mine-notes evidence). E.g. `mine-notes.md:467 (Rev 2.1 blob f3b7a521 line 18240)`.

**Row count estimate (for Validation Architecture):** ~16 rows — 8 control-register bits + 2 Arduino-pin assignments (A2 ADC, A3 ADC) + 2 shield designators (R41, JP4) + 4 per-rev variant rows (REV_1_VPE_TO_VPP etc.). Planner SHOULD enumerate exactly during plan-time.

**Critical handoff rows for Phase 34 (per Finding #6):**
- `R41` row → `canonical_alias: RES_HW_REVISION_DIVIDER` (or `RES_DETECT_DIVIDER` — planner picks). Type: `S` (R41 IS silkscreened per `mine-notes.md:429` "%TO.C,R41*%" in Rev 2.2 gerber).
- `A3` row → `canonical_alias: PIN_HW_REVISION_DETECT_ADC`. Type: `N` (A3 is the Arduino-pin label; not silkscreened on the shield silkscreen — silkscreened on the Arduino itself).
- `JP4` row → `canonical_alias: JMP_VPP_P1_BYPASS` (or similar). Type: `S` (JP4 IS silkscreened — `mine-notes.md:430`).

These three rows are the §7 → Phase 34 ADC band-table substrate (Finding #6).

## State of the Art

This is not a new-library research domain. The "state of the art" is the project's own existing convention.

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Bare hex literals (`0x80`) in handler code | Named `#define`s (`REGULATOR`) | v1.0 (pre-history) | Already in place; Phase 33 is the second-pass naming refinement. |
| Shield-specific net names (`VPE_TO_VPP`, `REGULATOR`) | Canonical `CTRL_*` / `PIN_*` namespace | Phase 33 (this milestone) | Self-documenting code without reading schematic; per-rev mapping centralized in `rurp_pinout.h`. |
| Per-rev variants as `REV_1_*` / `REV_2_*` prefix | Canonical name + `_REVn` suffix (`CTRL_*_REV2`) | Phase 33 | Suffix groups all variants of one signal together at the top level. |

**Deprecated post-Phase-33:**
- `VPE_ENABLE` / `VPE_TO_VPP` / `P1_VPP_ENABLE` / `A9_VPP_ENABLE` / `READ_WRITE` / `REGULATOR` / `VOLTAGE_MEASURE_PIN` / `HARDWARE_REVISION_PIN` / `ADDRESS_LINE_13` / `ADDRESS_LINE_16` / `ADDRESS_LINE_17` / `ADDRESS_LINE_18` — replaced by `CTRL_*` / `PIN_*` canonical names.
- `REV_1_*` / `REV_2_*` prefix family — replaced by `CTRL_*_REV1` / `CTRL_*_REV2` suffix family.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Firmware native test framework | PlatformIO + Unity (v2.x, pinned in `platformio.ini`) |
| Firmware native config file | `firestarter/platformio.ini` [env:native] |
| Firmware AVR build envs | `uno`, `uno328pb`, `leonardo` — 3 envs at `[env:uno]`, `[env:uno328pb]`, `[env:leonardo]` |
| Firmware native quick run | `cd firestarter && pio test -e native -f "*test_dispatch*"` (~10 s) |
| Firmware native full suite | `cd firestarter && pio test -e native` (~30 s; 3 suites: dispatch, messages, data_input) |
| Firmware AVR build (all 3) | `cd firestarter && pio run -e uno && pio run -e uno328pb && pio run -e leonardo` |
| Python framework | pytest (already in use) |
| Python config | `firestarter_app/pyproject.toml` |
| Python quick run | `cd firestarter_app && pytest -x` (~5 s; 7 test files) |
| Python full suite | `cd firestarter_app && pytest` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| ALIAS-01 | Every silkscreen label inventoried in §7 | doc-check / row-count assertion | `awk '/^## 7\\./{f=1;next} /^## 8\\./{f=0} f' .planning/v1.7-SHIELD-REVS.md \| grep -c '^\| '` — assert ≥ 16 rows | ❌ (test script Wave 0 — see Gaps) |
| ALIAS-01 | Each §7 row maps a silkscreen label to a `CTRL_*` / `PIN_*` alias following the convention | doc-check / regex | `awk '/^## 7\\./,/^## 8\\./' .planning/v1.7-SHIELD-REVS.md \| grep -E '\\|\\s*(CTRL_\|PIN_\|RES_\|JMP_)'` — assert each row's alias column matches | ❌ (Wave 0) |
| ALIAS-02 | New `rurp_pinout.h` exists with the alias `#define`s | file-existence + grep | `test -f firestarter/include/rurp_pinout.h && grep -c '^#define CTRL_' firestarter/include/rurp_pinout.h` | ❌ (created in Phase 33 Wave 1) |
| ALIAS-02 | `firestarter_app/firestarter/constants.py` has the `RURP_CONTROL_REGISTER_BITS` block | grep | `grep -c '^CTRL_' firestarter_app/firestarter/constants.py` — assert ≥ 9 | ✅ existing file |
| ALIAS-02 | Zero remaining references to old names in firmware | grep-zero | `grep -rn '\\b\\(VPE_ENABLE\\|VPE_TO_VPP\\|P1_VPP_ENABLE\\|A9_VPP_ENABLE\\|READ_WRITE\\|REGULATOR\\|HARDWARE_REVISION_PIN\\|VOLTAGE_MEASURE_PIN\\)\\b' firestarter/include/ firestarter/src/ firestarter/test/ 2>/dev/null \| wc -l` — assert 0 | ✅ tool available |
| ALIAS-02 | Zero remaining references to old names in Python host docstring | grep-zero | `grep -n 'VPE_TO_VPP\\|VPE_ENABLE\\|P1_VPP_ENABLE\\|A9_VPP_ENABLE\\|REGULATOR\\|READ_WRITE' firestarter_app/firestarter/main.py firestarter_app/firestarter/constants.py` — assert 0 hits OR all in comments referring to old names | ✅ tool available |
| ALIAS-03 | `firestarter_uno.hex` byte-identical pre/post rename modulo ≤ ~50 B | cmp + wc -c | `cmp .planning/v1.7/phase-33-baseline-hex/uno.hex .pio/build/uno/firestarter_uno.hex; echo $?` — assert 0 (or document drift in commit msg) | ✅ |
| ALIAS-03 | `firestarter_uno328pb.hex` byte-identical pre/post | cmp | `cmp .planning/v1.7/phase-33-baseline-hex/uno328pb.hex .pio/build/uno328pb/firestarter_uno328pb.hex` | ✅ |
| ALIAS-03 | `firestarter_leonardo.hex` byte-identical pre/post | cmp | `cmp .planning/v1.7/phase-33-baseline-hex/leonardo.hex .pio/build/leonardo/firestarter_leonardo.hex` | ✅ |
| ALIAS-03 | Unity native test suite green | pio test | `cd firestarter && pio test -e native` | ✅ |
| ALIAS-03 | pytest green | pytest | `cd firestarter_app && pytest` | ✅ |
| ALIAS-03 | All 3 AVR envs compile clean | pio run | `cd firestarter && pio run -e uno && pio run -e uno328pb && pio run -e leonardo` — assert exit 0 | ✅ |

### Sampling Rate

- **Per task commit:** `pio run -e uno && pio test -e native -f "*test_dispatch*"` (~20 s)
- **Per wave merge:**
  1. Build all 3 AVR envs: `pio run -e uno -e uno328pb -e leonardo`
  2. Run full Unity native suite: `pio test -e native`
  3. Compare each .hex to baseline: `cmp .planning/v1.7/phase-33-baseline-hex/{uno,uno328pb,leonardo}.hex .pio/build/{uno,uno328pb,leonardo}/firestarter_*.hex`
  4. (Wave 4 only) `cd firestarter_app && pytest -x`
- **Phase gate (post-Wave-4, before `/gsd-verify-work`):**
  1. Full grep-zero on old names: `grep -rn '\\b\\(VPE_ENABLE\\|VPE_TO_VPP\\|...\\)\\b' firestarter/include/ firestarter/src/ firestarter/test/` → 0 hits
  2. Full `.hex` cmp 3 boards → exit 0 (or drift ≤ ~50 B documented in commit msg)
  3. Full Unity + pytest green
  4. §7 row count ≥ 16 (Wave 4 deliverable)
  5. §7 row-alias regex match (every alias matches `^(CTRL|PIN|RES|JMP)_`)
  6. `firestarter/CLAUDE.md` §Constants docstring refreshed to new names

### Wave 0 Gaps

- [ ] Pre-rename `.hex` baseline capture script — should write to `.planning/v1.7/phase-33-baseline-hex/` (gitignored under D-11). Single-shot Bash task at start of Wave 1.
- [ ] `tools/check_alias_migration.sh` (or equivalent) — grep-zero + `.hex` cmp wrapper for repeatable wave-merge verification. Lives in firestarter sub-repo's `tools/` (already exists per `firestarter_app/tools/check_dispatch.py` precedent).
- [ ] §7 row-count assertion script — counts table rows under `## 7.` heading; lives in meta-repo (e.g. `.planning/tools/check_section_7.sh` or inline pytest under `firestarter_app/tests/test_v17_silkscreen_table.py`). Planner picks location.

*(No new test framework install needed — Unity + pytest already in place.)*

## Security Domain

Phase 33 has minimal security surface (no auth, no input validation, no cryptography, no session). The constraint we explicitly verify:

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes (file-path scope) | `name_firmware.py:48-51` already validates `RURP_BOARD_NAME` matches `[a-zA-Z0-9_-]+` before flowing into PROGNAME → filename. Phase 33 does NOT touch this. |
| V6 Cryptography | no | — |
| V14 Configuration | yes (build flags) | `-D HARDWARE_REVISION` set at `[env]` scope; Phase 33 must not accidentally narrow or widen this. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Macro-collision (new alias name shadows an existing identifier elsewhere) | Tampering | The new `CTRL_*` / `PIN_*` namespace is project-unique. Verify with `git grep "^#define CTRL_" firestarter/` → all hits in `rurp_pinout.h`. |
| Build artifact path traversal (PROGNAME injection) | Tampering | Already mitigated by `name_firmware.py:48-51` validation. Phase 33 changes no build_flags. |
| EEPROM data corruption (silent struct layout drift) | Tampering | Pitfall 5 — `CONFIG_VERSION "VER06"` stays put; verifier checks the line is byte-identical. |
| Wire-format drift (host sends old bit-name; firmware expects new) | Tampering | Wire format is JSON commands — `algorithm`, `vpp_mv`, `pin-count`, etc. — NOT control-register bit names. The bits are firmware-internal. Phase 33 does not perturb the wire. Verify by grepping `firestarter_app/firestarter/eprom_operations.py` for any reference to renamed names → expected 0. |

## Sources

### Primary (HIGH confidence — all VERIFIED via direct codebase inspection)

- `/workspaces/firestarter/include/rurp_shield.h:21-94` — full pre-Phase-33 macro layout, ifdef structure, value bindings [VERIFIED: file read]
- `/workspaces/firestarter/include/rurp_hw_rev_utils.h:13-58` — dispatcher + detect functions [VERIFIED: file read]
- `/workspaces/firestarter/include/rurp_register_utils.h:23-59` — write-to-register settle delay [VERIFIED: file read]
- `/workspaces/firestarter/src/proms/eprom.cpp`, `flash_intel.cpp`, `flash_type_4.cpp`, `flash_utils.cpp`, `eeprom_28c.cpp`, `memory.cpp` — call-site clusters [VERIFIED: grep with line refs]
- `/workspaces/firestarter/src/hardware_operations.cpp:27, :30` — `hw_read_voltage()` REGULATOR | VPE_TO_VPP path [VERIFIED: file read]
- `/workspaces/firestarter/src/boards/rurp_common.cpp:58` — `analogRead(VOLTAGE_MEASURE_PIN)` [VERIFIED: grep]
- `/workspaces/firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp` — 7 lines [VERIFIED: grep]
- `/workspaces/firestarter/platformio.ini:21-65` — `-D HARDWARE_REVISION` env-level inheritance + per-env `RURP_BOARD_NAME` [VERIFIED: file read]
- `/workspaces/firestarter/name_firmware.py:18-61` — PROGNAME derivation logic [VERIFIED: file read]
- `/workspaces/firestarter_app/firestarter/constants.py` — current 70-line constants module; no shield-pin block yet [VERIFIED: file read]
- `/workspaces/firestarter_app/firestarter/main.py:395-417` — `reg_parser` docstring with old names [VERIFIED: file read]
- `/workspaces/.planning/v1.7-SHIELD-REVS.md` §1-§6 — fills + §7-§9 TBD markers [VERIFIED: file read]
- `/workspaces/.planning/phases/31-upstream-shield-archaeology/mine-notes.md:427-535` — per-rev R41/JP4/A3 grep, blob SHAs, schematic line refs [VERIFIED: file read]
- `/workspaces/.planning/v1.7/notes/CHAT-INTEL.md` — Anders/henols quotes, dated, 5 sections [VERIFIED: file read — accessible at this path despite gitignore]
- `/workspaces/CLAUDE.md` — project layout + Python/C++ sync rule [VERIFIED: file read]
- `/workspaces/firestarter/CLAUDE.md` — protocol dispatch invariants, KNOWN_PROTOCOLS, native test layout [VERIFIED: file read via system reminder]
- `/workspaces/firestarter_app/CLAUDE.md` — constants.py sync rule, DB pipeline [VERIFIED: file read via system reminder]

### Secondary (MEDIUM confidence — derived patterns)

- Phase 9 archive `/workspaces/.planning/phases/09-delete-old-log-macros-measure-flash-savings/` — precedent for atomic macro rename + flash-savings measurement (5 plans) [VERIFIED: directory listing] — supports CONTEXT.md "Phase 9 macro-rename precedent" claim.
- v1.5 + v1.6 fix-commit patterns for capturing per-board `.hex` SHA-256s in commit messages — Phase 33 inherits this norm. [VERIFIED: ROADMAP entries reference these patterns]

### Tertiary (LOW confidence)

- *(none — all claims in this research are verified against the working tree as of 2026-05-25)*

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The `cmp` comparator and `wc -c` size check on Intel-HEX-format `.hex` files together suffice for ALIAS-03 verification (i.e. no need to also AVR-objdump / nm the .elf) | Validation Architecture / Pitfall 4 | LOW — `.hex` is text Intel HEX; identical bytes → identical AVR flash image. If a tooling quirk (date stamp embedded by `avr-objcopy`) makes the text differ, the wrap-up commit can fall back to `avr-objcopy --srec-len 0x10 -O ihex` normalization or to comparing `.elf` section sizes via `avr-size`. Documented in commit msg per D-07. |
| A2 | The `#define`-based rename will NOT trigger any compiler warning beyond what the pre-rename build already emits (no `-Wunused-macros` etc.) | Pattern 1 | LOW — `pio run` warning output is captured by the verifier; if a new warning surfaces, it's a clear flag for the planner. |
| A3 | The §7 column shape (12 columns: 1 silkscreen + 1 type + 1 alias + 1 hex + 7 per-rev + 1 citation) is mechanically sound — every cell is fillable from upstream evidence per Finding #5 | §7 Column Schema | MEDIUM — if a per-rev column ends up >50% `(inherits Rev X)` sentinels, planner may want to collapse to a single "varies-per-rev" column. Cosmetic, not load-bearing. Confirm with user at discuss-time or planner's discretion. |
| A4 | Modified Rev 0 row in §7 needs no firmware ifdef branch — D-09 is mechanically sound | Pitfall 7 | LOW — D-09 is explicit. The §7 table column carries `(inherits Rev 0)` / `pending Phase 35` sentinels; firmware semantics unchanged. |
| A5 | The Rev 2.2 R41 4k7-vs-10k discrepancy (CHAT-INTEL §1 vs schematic blob) does NOT affect Phase 33 alias choice — only Phase 34's band-table values | Open Questions Q3 | LOW — R41 is a designator (one name in §7) whose ohmic value is irrelevant to the alias rename. Phase 34 owns the value. |
| A6 | The `firestarter/CLAUDE.md` §Constants docstring at lines referencing `REGULATOR (0x80)` etc. should be refreshed to the new names in Wave 4 (or Wave 1 as part of the header creation commit) — this is a load-bearing project doc, not optional | Project Constraints | LOW — Inline doc refresh is standard. Planner picks wave; recommendation: same commit as `rurp_pinout.h` creation for atomicity. |

**Note:** Six assumptions only — Phase 33 is structurally simple and most claims are direct file-read verifications.

## Open Questions

1. **`CTRL_*` vs `PIN_*` namespace split — should `R41` go to a third `RES_*` namespace, or stay under `PIN_*`?**
   - What we know: `R41` is a resistor designator (component), not a pin assignment. A third namespace `RES_*` (or `JMP_*` for jumpers like JP4) is more semantically pure.
   - What's unclear: Whether the planner wants 4 namespaces (`CTRL_*`, `PIN_*`, `RES_*`, `JMP_*`) or to fold designators into `PIN_*` (as in "the pin/component that R41 sits at").
   - Recommendation: Use 4 namespaces. `CTRL_*` for control-register bits, `PIN_*` for Arduino-pin assignments, `RES_*` for shield resistor designators, `JMP_*` for shield jumper designators. Cleanest semantic grouping; total alias count is small enough (~16) that namespace bloat is not a concern.

2. **Should `ADDRESS_LINE_13` (referenced only in `rurp_shield.h:55`, used by no `.cpp`) be migrated?**
   - What we know: `#define ADDRESS_LINE_13 0x20` exists at line 55 outside any ifdef; grep finds 0 call-sites in `src/`.
   - What's unclear: Whether it's legacy debt (delete) or future-reserve (rename + keep).
   - Recommendation: Migrate as `CTRL_ADDRESS_LINE_13` for consistency but flag with a comment `// reserved — no current call-site`. Lower risk than deleting; matches "name-only" Phase 33 charter.

3. **Rev 2.2 R41 value discrepancy (4k7 schematic vs 10k chat) — does it affect §7 row content?**
   - What we know: Per CHAT-INTEL §1 + §4 row 5 in v1.7-SHIELD-REVS.md, schematic blob shows 4k7; Anders chat states 10k. Phase 35 follow-up #5 covers operator measurement.
   - What's unclear: Whether §7's R41 row records the schematic value, the chat value, or both.
   - Recommendation: §7's R41 row records the **alias name** (`RES_HW_REVISION_DIVIDER`), NOT the resistance value. The value lives in §3 (existing detect-hw scheme) + §9 (Phase 34 ADC band table). Phase 33 §7 is value-agnostic for components. This decouples the rename from Phase 35's measurement follow-up.

4. **`uno_rurp_shield.cpp:29` references `READ_WRITE` in a comment only — does the comment refresh count toward the 106 line-count?**
   - What we know: The line is `// NOTE: The original code included `READ_WRITE` (0x40), which would attempt to control PB6.` — purely documentary, no executable reference.
   - What's unclear: Whether the planner wants comments refreshed to `CTRL_READ_WRITE` for consistency, or to leave them as historical record of the old name.
   - Recommendation: Refresh the comment to use the new name (`// NOTE: The original code included \`CTRL_READ_WRITE\` (0x40), ...`). Reduces future confusion for readers grep-ing for the old name and finding only this comment.

5. **Should `firestarter/include/firestarter.h:53` `FLAG_VPE_AS_VPP 0x10` also be migrated?**
   - What we know: This is a host-API flag (parsed from the JSON wire `flags` field), NOT a shield-net name. It controls a code-path choice in `eprom.cpp` ("treat VPE as VPP — direct path, no dropping resistor"). The name references `VPE` and `VPP` but is operational, not shield-layer.
   - What's unclear: Whether D-03's "RURP-shield-interface layer" excludes or includes this.
   - Recommendation: **Do NOT migrate** — D-03 explicitly scopes to control-register bits + Arduino-pin assignments + shield-level designators. `FLAG_VPE_AS_VPP` is a wire-protocol flag (in `firestarter.h:53`, not `rurp_shield.h`). Out of scope. Documented as such in plan.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO CLI (`pio`) | All firmware build/test commands | ✅ | (system-installed; checked via `find .pio` returning artifacts) | — |
| `pio` env `uno` | Build ATmega328P artifact | ✅ | (working artifact in `.pio/build/uno/firestarter_uno.hex` as of 2026-05-25) | — |
| `pio` env `uno328pb` | Build ATmega328PB artifact | ✅ | (working artifact in `.pio/build/uno328pb/`) | — |
| `pio` env `leonardo` | Build ATmega32U4 artifact | ✅ | (working artifact in `.pio/build/leonardo/`) | — |
| `pio` env `native` | Unity native test suite | ✅ | (test config in `platformio.ini:67-104`) | — |
| pytest | Python host CLI test suite | ✅ | (existing 7 test files in `firestarter_app/tests/`) | — |
| `cmp` / `wc` / `grep` / `awk` | Verification commands | ✅ | (POSIX-standard) | — |
| Git | Branch operations + commit | ✅ | (existing v1.7-shield-investigation branch) | — |
| `pip install -e .` | Editable install for firestarter_app (already done) | ✅ | (existing install — `firestarter --help` works) | — |

**Missing dependencies with no fallback:** None.
**Missing dependencies with fallback:** None.

## Metadata

**Confidence breakdown:**
- Call-site inventory (Finding #1): HIGH — verified via `grep -rn` with exact per-file counts.
- GATE-1.7 verification protocol (Finding #2): HIGH — `cmp` of Intel HEX is well-defined; `name_firmware.py` PROGNAME derivation locks artifact path; pre-rename baseline captured in gitignored `.planning/v1.7/phase-33-baseline-hex/`.
- `ADDRESS_LINE_16 == VPE_TO_VPP` aliasing (Finding #3): HIGH — explicit verbatim aliasing at `rurp_shield.h:26` + load-bearing comment at `memory.cpp:142-144`.
- `rurp_map_ctrl_reg_for_hardware_revision()` dispatcher (Finding #4): HIGH — function body is 23 lines, dispatcher structure unchanged, textual macro updates only.
- §7 column schema (Finding #5): MEDIUM — 12-column shape is recommended but planner discretion (A3).
- Phase 34 handoff names (Finding #6): MEDIUM — recommendation `PIN_HW_REVISION_DETECT_ADC` + `RES_HW_REVISION_DIVIDER` is sensible but planner discretion.
- Modified Rev 0 mechanical soundness (Finding #7): HIGH — D-09 explicit, firmware does not branch.
- `CONFIG_VERSION` non-bump (Finding #8): HIGH — struct layout unchanged, `#define CONFIG_VERSION "VER06"` at `rurp_shield.h:93` stays.
- Validation Architecture (Finding #9): HIGH — test substrate already exists, sampling rate matches Phase 9 precedent.
- CHAT-INTEL.md accessibility (Finding #10): HIGH — file confirmed present at `.planning/v1.7/notes/CHAT-INTEL.md` (4851 bytes); gitignored but locally accessible.

**Research date:** 2026-05-25
**Valid until:** 2026-06-25 (Phase 33 has no external-API dependencies; only loses validity if the firmware codebase changes substantively before planning).
