# Phase 33: Silkscreen Label → Code Alias Migration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-25
**Phase:** 33-silkscreen-label-code-alias-migration
**Areas discussed:** Silkscreen source of truth, Per-rev divergence mechanism, Old-name migration policy, Python-side scope
**Mode:** auto (work-without-stopping per session directive — Claude made the reasonable call on each area; user retained redirect)

---

## Silkscreen source of truth

| Option | Description | Selected |
|--------|-------------|----------|
| Upstream F_Silkscreen.gbr per rev (gerber layer) | Verbatim physically-printed labels; already mined Phase 31; desk-side available now | partial ✓ (primary) |
| Upstream .kicad_sch net-name layer | In-schematic-only net labels (e.g. VPE_ENABLE, REGULATOR); already partly aliased in rurp_shield.h | partial ✓ (secondary) |
| Operator board photos | Verbatim ops-board silkscreen; blocked Phase 31 session, Phase 35 follow-up #1/#2/#3 | deferred |
| Combination of all three | | ✓ (gerber + .kicad_sch; photos deferred to Phase 35 footnote) |

**Claude's call:** Combination — primary source is `F_Silkscreen.gbr` for physically-printed labels, secondary source is `.kicad_sch` net-name layer for in-schematic-only labels that need code aliases. Operator photos are NOT a Phase 33 blocker — Phase 35 follow-ups can footnote if ops-board verbatim differs.
**Notes:** Captured as D-01..D-03 in CONTEXT.md. Alias scoping (D-03) constrains to RURP-shield-interface layer — NOT JEDEC chip-pin layer (pinouts.json already names) and NOT AVR-PORT layer (MCU-internal).

---

## Per-rev divergence mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse existing HARDWARE_REVISION ifdef + REV_1_*/REV_2_* pattern | rurp_shield.h:70-89 + rurp_hw_rev_utils.h:13-35 already proven for Rev 0/1/2.0/2.1/2.2 | ✓ |
| New compile-time RURP_SHIELD_REV env switch | Would add platformio envs per rev | |
| Runtime-only via Phase 34 ADC detect | No compile-time divergence; all branching at runtime | |
| Hybrid (compile-time floor + runtime override) | | |

**Claude's call:** Reuse existing pattern. Already shipped and proven. Phase 34 layers runtime ADC detect on top of the same substrate via `rurp_detect_hardware_revision()` → `rurp_configuration_t.hardware_revision`.
**Notes:** Captured as D-04..D-05. No new platformio envs. Mechanical extension for new revs from Phase 31 inventory.

---

## Old-name migration policy

| Option | Description | Selected |
|--------|-------------|----------|
| Hard-rename — all 86 call-sites move to PIN_*/CTRL_* | Honors ALIAS-02 literal reading; larger diff; #define keeps .hex byte-identical | ✓ |
| Additive — add new names alongside, deprecate old at v1.8 | Smaller diff; two namespaces co-exist; "migration" weaker | |
| Preprocessor shim — #define old=new keeps call-sites unchanged | Zero .hex risk; "migration" is header-only; arguably violates ALIAS-02 strict reading | |

**Claude's call:** Hard-rename via `#define` aliases. ALIAS-02 explicitly says "call-sites are migrated to the aliases." Using `#define` (not constexpr/enum class) means preprocessor-only substitution → byte-identical `.hex` → ALIAS-03 GATE-1.7 satisfied with zero margin needed.
**Notes:** Captured as D-06..D-07. Symbol-name overhead allowance (≤ ~50 B per board) held in reserve for edge cases (e.g. native test build with ArduinoFake). Three AVR targets are expected to produce literally byte-identical `.hex`; planner records `wc -c` pre/post in fix-commit message.

---

## Python-side scope

| Option | Description | Selected |
|--------|-------------|----------|
| Full constants.py mirror | Add all control-register bit constants to constants.py for documentation parity | ✓ (minimal block) |
| New firestarter/rurp_pinout.py module | Clean separation from constants.py | |
| Docstring-only refresh main.py:408-415 | Minimal — no new code; honors "name-only" | partial |
| Skip Python entirely | Interpret REQUIREMENTS-02 as firmware-only | |

**Claude's call:** Minimal `constants.py` addition + docstring refresh. Adds a small `RURP_CONTROL_REGISTER_BITS` block to `constants.py` mirroring the C++ `CTRL_*` names (per CLAUDE.md sync rule with `firestarter.h`); refreshes `main.py:408-415` docstring to reference new names. No new module — Python doesn't write the control register or interpret pin numbers; firmware does.
**Notes:** Captured as D-08. Pytest stays green by construction. No `eprom_operations.py` / `database.py` / `serial_comm.py` changes.

---

## Folded gray area: Modified Rev 0 handling

This was identified during analysis but not surfaced as a separate AskUserQuestion option (max 4 options). Folded into Phase 33 scope via Claude's call:

**D-09:** §7 alias table includes a Modified Rev 0 column. Cells the rework touches carry the sentinel `as-modified — pending Phase 35`; unaffected cells inherit from parent Rev 0. Firmware does NOT branch on Modified Rev 0 at compile time. Rework-trace deferred to Phase 35 follow-up #4.

---

## Claude's Discretion

The following are left to the planner per CONTEXT.md `<decisions>` Claude's Discretion section:

- Plan-wave decomposition (single big-bang vs subsystem-split). Subsystem-split is the natural shape because GATE-1.7 `.hex` byte-identical can be verified after each wave (early defect detection).
- Exact alias names per silkscreen label / schematic net (spec gives examples, not enumeration).
- `CTRL_*` vs `PIN_*` namespace split refinement of the spec's single `PIN_*` namespace.
- Exact column order of §7 (data shape is mandatory; order is style).
- `CONFIG_VERSION` bump decision — Claude's strong prior is no bump (no struct layout change); planner verifies.

## Deferred Ideas

See CONTEXT.md `<deferred>` section for the full list. Highlights:

- Phase 34: ADC voltage-band lookup table consumes Phase 33 `R41` + `HARDWARE_REVISION_PIN` aliases; Rev 2.2 R41 4k7-vs-10k discrepancy unresolved.
- Phase 35 (close): §7 footnotes for ops-board silkscreen photos; README cross-links; PROJECT.md "Validated" entry; Modified Rev 0 §7 cell upgrade if rework reveals new signal aliases.
- Out of v1.7: AVR-PORT-layer aliases (MCU-internal); full `firestarter/rurp_pinout.py` host module; `constexpr`/`enum class` modernization.
- Reviewed-but-not-folded todos: `avrdude-mcu-detection-fallback.md`, `large-read-data-jitter-uno328pb.md` (v1.6 scope), `w27c512-eeprom-misclassification.md` — all orthogonal to Phase 33's rename-only domain.
