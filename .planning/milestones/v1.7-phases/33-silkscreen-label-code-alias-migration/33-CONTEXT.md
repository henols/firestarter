# Phase 33: Silkscreen Label → Code Alias Migration - Context

**Gathered:** 2026-05-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Inventory every silkscreen label that appears on any known RURP shield revision (Rev 0 / Rev 1 / rev2-lowercase / Rev 2.0-working / Rev 2.1 / Rev 2.2 / Rev 2.3 + Modified Rev 0) into a single canonical table in `.planning/v1.7-SHIELD-REVS.md` §7, mapping each silkscreen label to a `PIN_<SUBSYSTEM>_<FUNCTION>` (or `CTRL_*` for register-bit) code alias. Land the aliases as `#define` declarations in a new `firestarter/include/rurp_pinout.h` header and as constants in `firestarter_app/firestarter/constants.py`. Hard-rename all existing call-sites (~86 references across `firestarter/include/` + `firestarter/src/` for the current alias set `VPE_ENABLE` / `VPE_TO_VPP` / `P1_VPP_ENABLE` / `A9_VPP_ENABLE` / `READ_WRITE` / `REGULATOR` / `ADDRESS_LINE_*` / `VOLTAGE_MEASURE_PIN` / `HARDWARE_REVISION_PIN`) from the old shield-specific net names to the new canonical names. The migration is name-only — no wire-format change, no behavior change, no .hex size drift beyond ≤ ~50 B per board (`uno` / `leonardo` / `uno328pb`). Pytest + Unity test suites stay green. GATE-1.7 non-regression is the load-bearing constraint (ALIAS-03). Per-rev pin-mapping differences from Phase 32 §4 (e.g. A2-ADC in Rev 1 → A3-ADC in Rev 2.x; A18 split across two control-reg bits in Rev 1 vs Rev 2) resolve via the existing `HARDWARE_REVISION` ifdef + `REV_1_*` / `REV_2_*` per-rev macro pattern already in `rurp_shield.h:70-89`.

Desk-side only — no operator-on-bench required for Phase 33. No sub-repo `beta`/`main` promotion; sub-repo `v1.7-shield-investigation` branches in `firestarter/` and `firestarter_app/` receive the rename commits. Meta-repo `v1.7-shield-investigation` branch receives the §7 fill commit on `.planning/v1.7-SHIELD-REVS.md`.

</domain>

<decisions>
## Implementation Decisions

### Silkscreen Source of Truth (D-01..D-03)

- **D-01: Combination source, desk-side, no operator photos needed.** Phase 33 pulls verbatim silkscreen labels from two upstream sources per rev:
  - **Primary — physically-printed labels** (chip-socket pin labels VPP/VCC/GND/A0..A18/D0..D7/CE/OE/WE, plus shield-level R41, JP4, etc.): upstream `F_Silkscreen.gbr` per rev (already mined Phase 31 — see `mine-notes.md:427-510` per-rev R41/JP4/A3 grep). For each rev, `git show <commit>:hardware/<path>/F_Silkscreen.gbr` is grep-able for `%TO.C,<designator>*%` entries (e.g. mine-notes confirms `R41` and `JP4` designators are present in Rev 2.2 gerbers).
  - **Secondary — in-schematic-only net names** (control-register bits like `VPE_ENABLE`, `REGULATOR`, `P1_VPP_ENABLE`, `A9_VPP_ENABLE`, `READ_WRITE`, `VPE_TO_VPP` — these are net labels INSIDE Anders's `.kicad_sch`, not physically printed on PCB silkscreen): upstream per-rev `.kicad_sch` text grep (per-rev blobs already located in `mine-notes.md` §Per-rev R41 — Rev2.0 blob `d2a7f691`, Rev2.1 `f3b7a521`, Rev2.3 `fe35bd78`).
  - Both layers feed the §7 alias table. Each row records whether the label is silkscreen-printed (S) or schematic-net-only (N) for downstream clarity.
- **D-02: Operator photos are NOT a Phase 33 blocker.** All three operator-on-hand boards (Rev 2.2 / Rev 2.0 / Modified Rev 0) remain `state: upstream-only` in `v1.7-SHIELD-REVS.md` §1 — photos were blocked the Phase 31 session and are Phase 35 follow-ups #1/#2/#3. Phase 33's silkscreen inventory pulls from upstream-only sources (gerbers + schematics). When Phase 35 photos land, any verbatim ops-board silkscreen text that differs from upstream gerber labels (per memory [[user_shield_revisions]] — operator owns physical Rev 2.2 / Rev 2.0 / Modified Rev 0, and silkscreen text rarely diverges from gerber across minor revs) gets a footnote in §7, not a table rewrite. Rationale: blocking Phase 33 on Phase 35 photos would back up the whole v1.7 critical path; gerber source is unambiguous and dated.
- **D-03: Alias scoping — RURP-shield-interface layer only.** Aliases are generated for: (a) control-register bit names (currently 8 bits in `rurp_shield.h:25-33` plus per-rev REV_1_* / REV_2_* equivalents at `:70-94`); (b) Arduino-pin assignments that map to RURP signals (currently 2: `VOLTAGE_MEASURE_PIN A2` and `HARDWARE_REVISION_PIN A3`); (c) shield-level designators that appear in firmware logic (R41 detect-divider, JP4 VPP-jumper — Phase 34 will consume the R41/JP4 aliases). **NOT in scope:** JEDEC chip-pin layer (`pinouts.json` already names VPP/VCC/GND/CE/OE/WE per DIP layout — that's chip-side, not shield-side); AVR-PORT layer (`PORTD`/`PORTB`/`DDRD` masks in `uno_rurp_shield.cpp`/`leonardo_rurp_shield.cpp` — MCU-internal register access, not RURP signal labels); per-DIP address-line / data-line socket pin labels (the chip-socket A0/D0 labels ARE silkscreened but the firmware speaks to them via the bus_config DIP-pin remapping in pinouts.json, not via direct shield-pin constants).

### Per-Rev Divergence Mechanism (D-04..D-05)

- **D-04: Reuse existing `HARDWARE_REVISION` ifdef + `REV_1_*` / `REV_2_*` per-rev macro pattern.** The current code at `rurp_shield.h:70-89` already declares `REV_1_VPE_TO_VPP` / `REV_2_VPE_TO_VPP` / `REV_1_ADDRESS_LINE_16` / `REV_2_ADDRESS_LINE_16` / etc. as alternate bit-mask variants gated by the `#ifdef HARDWARE_REVISION` compile-flag (set via `-D HARDWARE_REVISION` in `platformio.ini:23`). The dispatch logic in `rurp_hw_rev_utils.h:13-35` maps the canonical control register to per-rev bit positions via `rurp_map_ctrl_reg_for_hardware_revision()` at write time. Phase 33 extends this same pattern: new canonical aliases (`CTRL_VPP_VPE_DROP_ENABLE`, `CTRL_VPP_REGULATOR_ENABLE`, etc.) replace the current bare aliases (`VPE_TO_VPP`, `REGULATOR`); per-rev `CTRL_*_REV_N` variants replace `REV_1_*` / `REV_2_*`. No new platformio envs. No new compile-time switch. Phase 34 layers runtime ADC-detect (per Phase 31 §3 + Phase 34 plumbing) ON TOP OF this same substrate — `rurp_detect_hardware_revision()` (`rurp_hw_rev_utils.h:41`) becomes the canonical detector that populates `rurp_configuration_t.hardware_revision`.
- **D-05: New rev rows handled by mechanical extension.** Any rev surfaced in Phase 31 inventory (`v1.7-SHIELD-REVS.md` §1) that needs a distinct compile-time alias variant adds a new `CTRL_*_REV_<N>` macro block in `rurp_pinout.h` and a new case in `rurp_map_ctrl_reg_for_hardware_revision()`. Current rev coverage: Rev 0, Rev 1, Rev 2.0, Rev 2.1, Rev 2.2 are all already gated by the existing ifdef pattern; Rev 2.3 inherits Rev 2.2's bit layout (per Phase 32 §4 row 7 — no electrical delta beyond R41 value + JP4 footprint; control-register bit positions unchanged). Modified Rev 0: see D-08.

### Old-Name Migration Policy (D-06..D-07)

- **D-06: Hard-rename via `#define` aliases — call-sites move from old to new names.** Honors ALIAS-02 literal reading: "Existing call-sites that use bare pin numbers or shield-specific net names are migrated to the aliases." New canonical names land in `firestarter/include/rurp_pinout.h`. All current call-sites (audit: 86 references via `grep -rn "VPE_ENABLE\|VPE_TO_VPP\|P1_VPP_ENABLE\|A9_VPP_ENABLE\|READ_WRITE\|REGULATOR\|HARDWARE_REVISION_PIN\|VOLTAGE_MEASURE_PIN" firestarter/include/ firestarter/src/`) are rewritten to use the new names. Old `#define`s in `rurp_shield.h:25-33` are REMOVED — no shim, no backward-compat alias chain (per memory [[feedback_branching]] / project posture: small atomic diffs, no orphan symbols).
- **D-07: Aliases use `#define`, not `constexpr` or `enum class`.** Preprocessor-only substitution emits literally byte-identical token stream after expansion → byte-identical compiled `.hex` (the AVR ELF/HEX output is program-memory bytes; symbol-name strings live in the ELF, not in the .hex Intel-format output that `name_firmware.py` writes). `constexpr uint8_t REGULATOR = 0x80;` would add a debug symbol (DWARF or AVR-objcopy symbol table) that COULD push .hex size up if the toolchain includes any symbol metadata; `#define` is uncompromised. The ALIAS-03 ≤ ~50 B per-board allowance is held in reserve for edge cases (e.g. if Unity native-test build path picks up symbol changes through ArduinoFake stubs); for the three AVR targets, byte-identical .hex is the expected outcome and the planner records the actual `wc -c` of each .hex pre/post migration in the fix-commit message.

### Python-Side Scope (D-08)

- **D-08: Minimal `constants.py` addition — control-register bit constants block.** Add a new `# RURP Control Register Bits` block to `firestarter_app/firestarter/constants.py` mirroring the C++ `CTRL_*` names (with the same hex values as the C++ `#define`s). Per the CLAUDE.md sync rule ("`firestarter/constants.py` must stay in sync with `firestarter/include/firestarter.h` in the firmware sub-repo"), this is the canonical place for Python-side parity. Refresh the docstring at `firestarter_app/firestarter/main.py:408-415` (current text references `VPE_TO_VPP` / `REGULATOR` / `P1_VPP_ENABLE` / `VPE_ENABLE` / `A9_VPP_ENABLE` literally) to use the new `CTRL_*` names AND link to the new `constants.RURP_CONTROL_REGISTER_BITS` block. **Not in scope:** new `firestarter/rurp_pinout.py` module (Python doesn't write the control register or interpret Arduino pin numbers — the constants are documentary only); no `eprom_operations.py` changes (the wire protocol's `bus_config` is JEDEC chip-pin-level, not shield-pin-level); no `database.py` changes. Pytest stays green by construction (no behavior touched).

### Modified Rev 0 Handling (D-09)

- **D-09: Modified Rev 0 row in §7 — explicit `pending Phase 35` sentinels for rework-touched cells.** Operator's third board (per memory [[user_shield_revisions]]) carries hardware-bug-A/B rework consisting of cuts + jumpers; rework trace deferred to Phase 35 follow-up #4 (write full `.planning/v1.7/MODIFICATIONS.md`). Phase 33's §7 alias table includes a Modified Rev 0 column; cells the rework touches (TBD until Phase 35 trace lands) carry the sentinel `as-modified — pending Phase 35`; cells unaffected by rework (e.g. control-register bit layout — the rework is hand-wire-level, not chip-replacement-level) inherit from parent Rev 0 with a `(inherits Rev 0)` note. **Firmware does NOT branch on Modified Rev 0** — at compile time it's indistinguishable from Rev 0 (no new `REVISION_MODIFIED_0` macro, no new ifdef branch). Operator-attested-only programming stays the workflow per existing memory.

### Claude's Discretion

- **Plan-wave decomposition:** single big-bang wave vs subsystem-split (e.g. Wave 1 = create `rurp_pinout.h` + alias-only header churn → Wave 2 = rename call-sites in `firestarter/src/proms/*.cpp` → Wave 3 = rename call-sites in `firestarter/src/boards/*.cpp` + `include/*.h` → Wave 4 = Python-side + §7 fill). Planner decides; the subsystem-split is the natural shape because GATE-1.7 .hex byte-identical can be verified after each wave (early defect detection).
- **Exact naming of each alias** — the spec gives examples (`PIN_VPP_REGULATOR_ENABLE`, `PIN_DATA_BUS_BYTE_0`, `PIN_ADDRESS_BUS_A14`) but doesn't enumerate. Planner derives the full alias list from §7 source rows + the existing `rurp_shield.h:25-33` set. The `CTRL_*` vs `PIN_*` namespace split (`CTRL_*` for control-register bits, `PIN_*` for Arduino-pin assignments) is a planner refinement of the spec's single `PIN_*` namespace — flagged here for planner to lock at plan time.
- **Order of §7 columns** — silkscreen label, alias name, type (S = silkscreen-printed / N = schematic-net-only), per-rev applicability (`✓` / `not-present` / `pending Phase 35`), source citation (gerber file or schematic blob + line ref). Planner decides exact column order; the data shape is mandatory.
- **Whether to bump `CONFIG_VERSION`** (currently `"VER06"` in `rurp_shield.h:93`). The EEPROM persists `rurp_configuration_t`; if `rurp_configuration_t` struct layout doesn't change (which it doesn't — only macro names change), `CONFIG_VERSION` stays at `"VER06"`. Planner verifies.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project planning
- `.planning/ROADMAP.md` §v1.7 — milestone goal, structural notes, Phase 33 success criteria, ALIAS-03 GATE-1.7 constraint
- `.planning/REQUIREMENTS.md` — ALIAS-01 (silkscreen inventory) / ALIAS-02 (header + Python module + call-site migration) / ALIAS-03 (GATE-1.7 .hex byte-identical)
- `.planning/STATE.md` — current milestone state (Phase 33 next; v1.6 paused at Phase 27 RCA re-open boundary)
- `.planning/PROJECT.md` — project overview
- `.planning/codebase/STRUCTURE.md` — repo layout (meta-repo + 2 sub-repos)
- `.planning/codebase/CONVENTIONS.md` — coding conventions
- `.planning/codebase/CONCERNS.md` — known concerns / patterns

### v1.7 canonical document
- `.planning/v1.7-SHIELD-REVS.md` §1 — per-rev inventory (8 rows; all operator boards `state: upstream-only`)
- `.planning/v1.7-SHIELD-REVS.md` §3 — Anders R41-on-A3 detect-HW scheme (Phase 33 alias for R41 + A3-ADC consumed here)
- `.planning/v1.7-SHIELD-REVS.md` §4 — inter-rev electrical deltas (Phase 33 reads to know which pin-mappings differ per rev; Rev 1 → rev2 A2→A3 migration is the foundational delta)
- `.planning/v1.7-SHIELD-REVS.md` §5 — inter-rev mechanical deltas (JP4 footprint 1x2 → 2x2 Rev 2.2 → Rev 2.3)
- `.planning/v1.7-SHIELD-REVS.md` §6 — per-rev capability matrix (Phase 33 aligns silkscreen aliases with per-rev supported protocols)
- `.planning/v1.7-SHIELD-REVS.md` §7 — `<!-- OWNED BY PHASE 33 — TBD -->` — Phase 33 fills this section

### Phase 31 + Phase 32 cross-phase intel (load-bearing for §7 fill)
- `.planning/phases/31-upstream-shield-archaeology/31-CONTEXT.md` — D-10 9-column inventory schema; D-11 gitignore policy; D-12 CHAT-INTEL deliverable
- `.planning/phases/31-upstream-shield-archaeology/mine-notes.md` §Per-rev R41 / JP4 / A3 grep (lines 434-510) — verbatim silkscreen/schematic-net evidence per rev with blob SHAs + line refs
- `.planning/phases/31-upstream-shield-archaeology/mine-notes.md` §Findings Summary — A through G (R41 introduction, JP4 footprint change, schematic file rename, 4k7→10k value, etc.)
- `.planning/v1.7/notes/CHAT-INTEL.md` (gitignored — meta-repo local) §1 R41 history, §2 JP3-mod → JP4 rename, §5 Rev 2.3 silkscreen-only-diff claim (and the schematic-evidence rebuttal)
- `.planning/v1.7/upstream-rurp/` (gitignored upstream clone) — `hardware/<rev>/F_Silkscreen.gbr` per rev is the canonical source for silkscreen-printed labels; `hardware/W27C512Programmer.kicad_sch` (blobs d2a7f691 / f3b7a521 / fe35bd78 — per Phase 31 mine) is the canonical source for in-schematic-only net names

### Firmware source-of-truth files (Phase 33 modifies these)
- `firestarter/include/rurp_shield.h` — current control-register bit defines (`:25-33`), per-rev REV_1_* / REV_2_* variants (`:70-94`), `VOLTAGE_MEASURE_PIN` / `HARDWARE_REVISION_PIN` (`:21, :36`), `CONFIG_VERSION` (`:98`)
- `firestarter/include/firestarter.h` — `firestarter_handle_t` struct (no struct changes expected)
- `firestarter/include/rurp_hw_rev_utils.h` — `rurp_map_ctrl_reg_for_hardware_revision()` dispatcher (Phase 33 may rename internal macros referenced here, but signature stays)
- `firestarter/include/rurp_register_utils.h` — `rurp_write_to_register()` (uses `P1_VPP_ENABLE` and `CONTROL_REGISTER` — rename targets)
- `firestarter/src/proms/eprom.cpp`, `flash_type_4.cpp`, `eeprom_28c.cpp`, `flash_intel.cpp`, `sram.cpp`, `memory.cpp` — call-sites that consume the alias set (audit via `grep -rn "VPE_ENABLE\|VPE_TO_VPP\|P1_VPP_ENABLE\|A9_VPP_ENABLE\|READ_WRITE\|REGULATOR" firestarter/src/proms/`)
- `firestarter/src/boards/uno_rurp_shield.cpp`, `leonardo_rurp_shield.cpp`, `rurp_common.cpp` — call-sites that consume `VOLTAGE_MEASURE_PIN` + PORTx mask bits (PORTx masks are NOT migrated per D-03 alias-scoping)
- `firestarter/src/hardware_operations.cpp` — consumes `REGULATOR | VPE_TO_VPP` (rename targets at `:27, :30`)
- `firestarter/platformio.ini` — `-D HARDWARE_REVISION` (env-level), `RURP_BOARD_NAME` per env (already shipped); no new build flags expected

### Host CLI source-of-truth files (Phase 33 modifies these)
- `firestarter_app/firestarter/constants.py` — current state: command codes + flag bits only, no pin/register constants. Phase 33 adds `RURP_CONTROL_REGISTER_BITS` block per D-08.
- `firestarter_app/firestarter/main.py:408-415` — current docstring references old C++ names; refresh to new names per D-08.
- `firestarter_app/CLAUDE.md` — has the sync-with-firmware-`firestarter.h` rule; verify the rule covers the new `constants.py` block too.

### Memory (auto-recalled, persistent)
- `[[user_shield_revisions]]` — operator owns Rev 2.2 / Rev 2.0 / Modified Rev 0; ALWAYS ASK which rev when "swap the shield" comes up. Phase 33 desk-side: not a concern, no bench programming.
- `[[project_v17_shield_investigation]]` — v1.7 milestone state (Phases 31-35; documentation-first + detect-resistor design + ADC plumbing)
- `[[feedback_branching]]` — milestone branches in all 3 repos; Phase 33 touches meta-repo + both sub-repos
- `[[user_firestarter_repo_layout]]` — meta + 2 sub-repos; sub-repos branched off `beta`, meta off `main`

### Sub-repo CLAUDE.md (must respect)
- `firestarter/CLAUDE.md` — protocol dispatch invariants (Phase 33 alias rename must not perturb dispatch order in `memory.cpp:configure_memory`); KNOWN_PROTOCOLS list (unchanged)
- `firestarter_app/CLAUDE.md` — Python sync-with-firmware rule for `constants.py`; database pipeline architecture (Phase 33 does not touch `tools/build_db.py` or `chip_database.json`)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`HARDWARE_REVISION` ifdef pattern** (`rurp_shield.h:24-53` + `:70-94`) — already does per-rev macro variant gating. Phase 33's per-rev divergence reuses this verbatim; no new mechanism needed.
- **`rurp_map_ctrl_reg_for_hardware_revision()`** (`rurp_hw_rev_utils.h:13-35`) — already maps the canonical control-register layout to per-rev bit positions at write time. Phase 33 renames the macros this function references but keeps the function signature + dispatch shape unchanged.
- **`rurp_detect_hardware_revision()`** (`rurp_hw_rev_utils.h:41-58`) — already reads `HARDWARE_REVISION_PIN` (A3) + `VOLTAGE_MEASURE_PIN` (A2) at boot to populate the per-rev `revision` static. Phase 33 does NOT change this; Phase 34 will extend it with the ADC voltage-band lookup table.
- **`rurp_configuration_t.hardware_revision`** EEPROM byte (referenced in `rurp_hw_rev_utils.h:62`) — already the operator-configured override path. Phase 33 leaves this alone; Phase 34 will use it as the fall-through when ADC reads `rev_unknown`.
- **Phase 9 macro-rename precedent** (`.planning/phases/09-delete-old-log-macros-measure-flash-savings/`) — already proved that AVR-flash-byte-identical macro renames are possible. Same pattern reused: catalog old name → new name → mechanical replacement via grep + plan-wave subsystem split.

### Established Patterns
- **`#define`-based aliases, not `constexpr`/`enum class`** — the entire firmware uses `#define` for compile-time constants (control register bits, flag bits, response codes, etc.). Phase 33 follows the same convention. `constexpr` is used only for type-anchored constants (`VCC_CALC_CONSTANT` in `rurp_common.cpp:27`, `INPUT_RESOLUTION` in `uno_rurp_shield.cpp:17`) where AVR-objcopy strips the symbol post-link.
- **`#ifdef HARDWARE_REVISION` compile-flag gating** — set via `-D HARDWARE_REVISION` in `platformio.ini:23` for all three AVR envs (uno / uno328pb / leonardo). The native test env does NOT set it, so test code paths see the legacy single-rev layout. Phase 33 preserves this asymmetry.
- **Per-board ifdef in boards/*.cpp** — `#ifdef ARDUINO_AVR_UNO || defined(ARDUINO_AVR_ATmega328PB)` / `#ifdef ARDUINO_AVR_LEONARDO`. Phase 33 does NOT introduce per-board alias variants (RURP signal layer is board-invariant — only the PORTx mapping to Arduino pins differs, and PORTx mapping is NOT a Phase 33 alias).
- **Header organization**: one `.h` per major subsystem (`rurp_shield.h`, `rurp_register_utils.h`, `rurp_hw_rev_utils.h`, `firestarter.h`, etc.). Phase 33's new `rurp_pinout.h` fits cleanly into this layout.
- **Python-to-C++ sync via `firestarter/CLAUDE.md`** — explicit sync-burden rule. Phase 33 D-08 minimal-Python approach honors this without inflating diff.

### Integration Points
- **Phase 33 → Phase 34**: §7 alias table includes a `R41` row + an `A3` row (Arduino-pin ADC) — Phase 34 ADC-band lookup reads these aliases to populate `rurp_detect_hardware_revision()`'s voltage-band table. The compile-time `HARDWARE_REVISION_PIN` alias becomes the canonical name Phase 34 consumes.
- **Phase 33 → Phase 35 (close)**: §7 + alias migration commits land in PROJECT.md "Validated" updates; README cross-links from `firestarter/README.md` + `firestarter_app/README.md` to `.planning/v1.7-SHIELD-REVS.md` §7 ("which silkscreen label means what in code").
- **Phase 33 → v1.6 resume**: When v1.6 Phase 27 RCA re-opens (per memory [[project_v17_shield_investigation]]), the instrumented A/B build paths cite `rurp_pinout.h` aliases — the new names are self-documenting for the RCA log. No code path divergence; just clarity.

</code_context>

<specifics>
## Specific Ideas

- **Silkscreen labels live in 2 layers** — physically-printed on PCB (`F_Silkscreen.gbr` from upstream gerbers) AND in-schematic-only net labels (`.kicad_sch` net property values). The canonical §7 alias table records BOTH with a type column (`S` / `N`) so future readers know whether a label is visible on the board or only in the schematic source.
- **Existing aliases ARE already shield-net names** — `VPE_ENABLE`, `REGULATOR`, `P1_VPP_ENABLE`, etc. in `rurp_shield.h` ARE the schematic net names Anders uses. Phase 33's rename is a RENAME (`VPE_ENABLE` → `CTRL_VPP_VPE_DROP_ENABLE`), not a migration-from-bare-pin-numbers. The spec's example "`VPP_EN` → `PIN_VPP_REGULATOR_ENABLE`" reads as a hypothetical — actual current code uses the verbose `VPE_ENABLE` not the silkscreen-style `VPP_EN`.
- **`#define VPE_TO_VPP 0x01` vs `0x100` is rev-dependent** — `rurp_shield.h:25, :51` shows the same name `VPE_TO_VPP` takes value `0x01` in the pre-HARDWARE_REVISION path and `0x100` in the HARDWARE_REVISION path. The new canonical alias must preserve this rev-dependent value mapping. Planner verifies the ifdef shape carries through unchanged.
- **`ADDRESS_LINE_16 == VPE_TO_VPP` aliasing** — `rurp_shield.h:26` says `#define ADDRESS_LINE_16 VPE_TO_VPP`. This is a load-bearing alias (A16 signal multiplexes with the VPE-to-VPP dropping-resistor enable on Rev 0/1). The new canonical names must preserve the aliasing: `CTRL_ADDRESS_LINE_16` and `CTRL_VPP_VPE_DROP_ENABLE` are textually identical `#define`s in the legacy path AND distinct values in the Rev 2 path. Planner double-checks the bit-position math after rename.
- **Modified Rev 0 is operator-attested, not firmware-detected** — per memory [[user_shield_revisions]] + Phase 32 §6 row 8. Phase 33 inventories aliases for stock Rev 0; rework-specific aliases (if any are needed for firmware to consume) are post-v1.7. The §7 Modified Rev 0 column carries `pending Phase 35` sentinels for cells the rework touches per D-09.
- **`CONFIG_VERSION "VER06"` does NOT bump** — the rename touches macro names only, not `rurp_configuration_t` struct layout. EEPROM-persisted config stays compatible. Planner verifies in fix-commit message.

</specifics>

<deferred>
## Deferred Ideas

### For Phase 34 discuss (when that phase opens)
- **ADC voltage-band lookup table** consumes the `R41` + `HARDWARE_REVISION_PIN` aliases from Phase 33 §7. Specifically: per-rev R41 value (4k7 for Rev 2.0/2.1/2.2; 10k for Rev 2.3) + supply voltage → expected ADC reading range. Phase 34 owns the band-table data; Phase 33 owns the alias names.
- **Rev 2.2 R41 4k7-vs-10k discrepancy** (CHAT-INTEL §1 says 10k; schematic blob f3b7a521 shows 4k7) is unresolved — physical measurement is Phase 35 follow-up #5. Phase 34's band table must accommodate both values (or rely on Phase 35 operator measurement); flag in Phase 34 discuss.
- **Runtime detect plumbing** extends `rurp_detect_hardware_revision()` from its current digital-read + threshold-compare (`rurp_hw_rev_utils.h:41-58`) to a multi-band lookup. Phase 33 leaves the function alone; Phase 34 modifies its body but keeps signature.

### For Phase 35 (close)
- **§7 footnotes for ops-board silkscreen** — when Phase 35 photos land (follow-ups #1/#2/#3), any ops-board verbatim silkscreen that differs from upstream gerber labels gets a footnote in §7. Not a table rewrite per D-02.
- **README cross-links** — `firestarter/README.md` + `firestarter_app/README.md` link to `.planning/v1.7-SHIELD-REVS.md` §7 for "which silkscreen label = which code symbol." Phase 35 owns the README write.
- **PROJECT.md "Validated" entry** for the alias migration. Phase 35 owns.
- **Modified Rev 0 §7 cell upgrade** — Phase 35 follow-up #4 (full MODIFICATIONS.md) may reveal rework-specific signal aliases needed; if so, post-v1.7 milestone takes the upgrade.

### Out of v1.7 entirely
- **AVR-PORT-layer aliases** (PORTD/PORTB/DDRD masks in board cpp files) — MCU-internal register access, not RURP shield signal layer. Could be future cleanup but is out of Phase 33 alias-scoping per D-03.
- **JEDEC chip-pin layer renaming** (`pinouts.json` VPP/CE/OE/WE per DIP layout) — already named correctly; chip-side, not shield-side.
- **`firestarter/rurp_pinout.py` host module** (full mirror of C++ aliases as a Python module) — D-08 chose minimal `constants.py` addition; full Python mirror module is a v1.8+ cleanup if Python ever needs to build bus_config payloads at the control-register-bit level.
- **Migrating PORTx masks in board cpp files** (e.g. `PORTB_CONTROL_MASK` in `leonardo_rurp_shield.cpp:20`) — MCU-internal layer per D-03; future cleanup if ever needed.
- **`constexpr`/`enum class` for control-register bits** — `#define` is the project convention per D-07; a more modern C++ style is out of scope.

### Reviewed Todos (not folded)
- `avrdude-mcu-detection-fallback.md` — v1.5 carryover, not Phase 33 scope (firmware/host install concern).
- `large-read-data-jitter-uno328pb.md` — v1.6 milestone scope; v1.6 resumes after v1.7 ships.
- `w27c512-eeprom-misclassification.md` — separate HIGH-priority backlog; chip-database routing bug.

(None folded — Phase 33's domain is the rename-only alias migration; the open todos are orthogonal concerns.)

</deferred>

---

*Phase: 33-Silkscreen-Label-Code-Alias-Migration*
*Context gathered: 2026-05-25*
