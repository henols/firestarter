---
phase: 33-silkscreen-label-code-alias-migration
plan: 04
subsystem: host-cli-and-meta-docs
tags: [python, host, documentation, alias, silkscreen-table, migration, ctrl, pin, res, jmp, alias-01, alias-02, gate-1.7, milestone-close]

# Dependency graph
requires:
  - phase: 33-silkscreen-label-code-alias-migration
    plan: 00
    provides: "baseline .hex artifacts (uno / uno328pb / leonardo) + check-migration.sh wave-merge gate"
  - phase: 33-silkscreen-label-code-alias-migration
    plan: 01
    provides: "firestarter/include/rurp_pinout.h — canonical CTRL_*/PIN_* alias substrate"
  - phase: 33-silkscreen-label-code-alias-migration
    plan: 02
    provides: "src/proms/*.cpp + src/hardware_operations.cpp migrated to CTRL_*"
  - phase: 33-silkscreen-label-code-alias-migration
    plan: 03
    provides: "firmware-side rename complete — dispatcher + settle-check + board adapters + native test + atomic D-06 rurp_shield.h:25-89 delete; check-migration.sh PASS"
provides:
  - "firestarter_app/firestarter/constants.py — RURP_CONTROL_REGISTER_BITS block mirroring rurp_pinout.h (9 CTRL_* constants, wide-layout hex values, with `# was OLD_NAME` annotations)"
  - "firestarter_app/firestarter/main.py — `--firestarter` argparse docstring refreshed to CTRL_* names with cross-reference line to constants.RURP_CONTROL_REGISTER_BITS"
  - "firestarter_app/CLAUDE.md — constants sync rule extended to cover rurp_pinout.h"
  - ".planning/v1.7-SHIELD-REVS.md §7 — populated 12-column silkscreen → code alias table with 17 data rows (9 CTRL_* canonical + 3 per-rev variants + 1 reserved + 2 PIN_* + 1 RES_* + 1 JMP_*); D-09 sentinels honored; mine-notes.md + rurp_pinout.h cross-citations"
  - "Phase 33 closed end-to-end: ALIAS-01 + ALIAS-02 + ALIAS-03 all MET"
affects:
  - "Phase 34 (Shield-Version-Detect Design + Firmware Plumbing) — RES_HW_REVISION_DIVIDER + PIN_HW_REVISION_DETECT_ADC aliases ready for ADC band-table substrate"
  - "Phase 35 (Documentation + Milestone Close) — §7 footnotes refresh once operator photos land (D-02 follow-up)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Python-mirror-of-C++-#defines block — same idiom as existing FLAG_* block (constants.py:60-69); section comment header + NAME = 0xNNN per line + `# was OLD_NAME` annotation tracing the rename"
    - "Meta-repo §7 fill pattern: 12-column shape (silkscreen + type + alias + hex + 7 per-rev + citation) reusing §1 + §6 sentinel vocabulary (`not-present` / `(inherits Rev 0)` / `as-modified — pending Phase 35` / `pending Phase 35` / `✓`) and source-citation format (`mine-notes.md:NNN` with blob SHA + line; `rurp_pinout.h` for code anchors)"
    - "Atomic commit-then-bump pattern for firestarter_app submodule: commit Task 1 inside the submodule on v1.7-shield-investigation; then bump submodule pointer in meta-repo as a separate commit (per sequential_execution contract)"
    - "Existing typos preserved verbatim (Phase 33 is name-only — `argumet` / `sheild` in main.py docstring carry through unchanged)"

key-files:
  created:
    - ".planning/phases/33-silkscreen-label-code-alias-migration/33-04-SUMMARY.md (this file)"
  modified:
    - "firestarter_app/firestarter/constants.py (+15 lines — new # RURP Control Register Bits block, 9 CTRL_* constants)"
    - "firestarter_app/firestarter/main.py (9 docstring line refresh + 1 new cross-reference line; typos preserved)"
    - "firestarter_app/CLAUDE.md (sync rule extended to also cover rurp_pinout.h)"
    - ".planning/v1.7-SHIELD-REVS.md (§7 placeholder replaced by 3-para preamble + 12-col × 17-row table)"

key-decisions:
  - "ALIAS-01 namespace lock — 4-way split (CTRL_* control-register bits / PIN_* Arduino-pin assignments / RES_* shield resistor designators / JMP_* shield jumper designators). All 17 §7 data rows match ^(CTRL|PIN|RES|JMP)_[A-Z0-9_]+$."
  - "D-09 Modified Rev 0 sentinel split honored: 14 of 17 rows carry `(inherits Rev 0)` (control-register bits + Arduino pins — rework is hand-wire-level, not control-register-layout-level); 2 rows (R41 + JP4 — physical shield designators) carry `as-modified — pending Phase 35`. No row claims unverified rework state."
  - "Per-rev variant rows count = 3 (CTRL_VPP_VPE_DROP_ENABLE_REV1, CTRL_VPP_VPE_DROP_ENABLE_REV2, CTRL_ADDRESS_LINE_18_REV2) — captures the legacy/REV2 hex-value duality (Pitfall 2) + REV2 A18/VPP_P1 multiplex (Pitfall 3) in table form, preserving the §3 schema substrate."
  - "Phase 33 is name-only — typos `argumet` / `sheild` in main.py:404-417 preserved verbatim. Hex values in main.py and constants.py docstring match the HARDWARE_REVISION wide layout (CTRL_VPP_VPE_DROP_ENABLE = 0x100) — Python is documentary, never writes the control register, so the wider layout is the relevant authoritative reference."
  - "Source citations use mine-notes.md as the schematic-net evidence layer (Phase 31 per-rev R41/JP4 grep at :434-510) and rurp_pinout.h as the code anchor — both are post-Wave-3 verified substrates."
  - "Pitfall 1 + Pitfall 3 aliasing semantics documented in row notes — CTRL_ADDRESS_LINE_16 shares bit with CTRL_VPP_VPE_DROP_ENABLE in legacy non-HARDWARE_REVISION branch; CTRL_ADDRESS_LINE_18_REV2 aliased to CTRL_VPP_P1_ENABLE in REV2 wide layout."

requirements-completed:
  - ALIAS-01
  - ALIAS-02

# Metrics
duration: ~10min
completed: 2026-05-25
---

# Phase 33 Plan 04: Wave 4 — Python Parity + §7 Silkscreen-Alias Table Fill Summary

**Closed Phase 33 end-to-end: Python host CLI now mirrors the firmware CTRL_* namespace (constants.py + main.py + sync rule); v1.7-SHIELD-REVS.md §7 canonical silkscreen → code alias table populated with 17 rows across 4 alias namespaces (CTRL_/PIN_/RES_/JMP_). ALIAS-01 + ALIAS-02 + ALIAS-03 all MET. check-migration.sh PASS preserved post-Wave-4 (firmware untouched — Δ = 0 B across all 3 AVR envs).**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-05-25T11:55:59Z (immediately after 33-03 close)
- **Completed:** 2026-05-25T12:02:42Z
- **Tasks:** 2
- **firestarter_app sub-repo commits:** 1 (Task 1)
- **Meta-repo commits:** 2 (1 submodule-pointer bump for Task 1 + 1 §7 fill for Task 2)
- **Files modified (host):** 3 (constants.py, main.py, CLAUDE.md)
- **Files modified (meta):** 1 (.planning/v1.7-SHIELD-REVS.md)

## Accomplishments

### Task 1 — firestarter_app Python-side CTRL_* parity (ALIAS-02)

- **constants.py — RURP_CONTROL_REGISTER_BITS block added.** Appended after the existing `# Control Flags` block (line 69). New section header `# RURP Control Register Bits — mirror of firestarter/include/rurp_pinout.h` + 3-line documentary comment (Python doesn't write the control register; used by `firestarter dev registers --firestarter` host-side helpers; keep in sync per CLAUDE.md sync rule). 9 constants in MSB-to-LSB order matching the HARDWARE_REVISION wide layout:
  - `CTRL_VPP_VPE_DROP_ENABLE = 0x100` (was VPE_TO_VPP — wide layout)
  - `CTRL_VPP_REGULATOR_ENABLE = 0x080` (was REGULATOR)
  - `CTRL_READ_WRITE = 0x040` (was READ_WRITE)
  - `CTRL_ADDRESS_LINE_18 = 0x020`
  - `CTRL_ADDRESS_LINE_17 = 0x010`
  - `CTRL_VPP_P1_ENABLE = 0x008` (was P1_VPP_ENABLE)
  - `CTRL_VPE_ENABLE = 0x004` (was VPE_ENABLE)
  - `CTRL_VPP_A9_ENABLE = 0x002` (was A9_VPP_ENABLE)
  - `CTRL_ADDRESS_LINE_16 = 0x001`
  - Pattern matches FLAG_* idiom verbatim (no type annotations; section header + per-line constants + inline `# was OLD_NAME` annotations on the 5 renamed bits + 2 layered renames).

- **main.py:400-417 docstring refreshed.** The `reg_parser.add_argument("-f", "--firestarter", …)` help docstring now lists `0x100 - CTRL_VPP_VPE_DROP_ENABLE` through `0x001 - CTRL_ADDRESS_LINE_16` (all 9 bits) with a new cross-reference line `See constants.RURP_CONTROL_REGISTER_BITS (mirror of rurp_pinout.h).` inserted before the 0x100 line. Existing typos `argumet` (sic — line 405) and `sheild` (sic — line 407) preserved verbatim — Phase 33 is name-only.

- **firestarter_app/CLAUDE.md sync rule extended.** The pre-existing sync rule about `firestarter/constants.py` ↔ `firestarter/include/firestarter.h` is unchanged. Appended a sentence: *"Additionally, the `RURP_CONTROL_REGISTER_BITS` block in `constants.py` (CTRL_* names) mirrors the control-register-bit declarations in `firestarter/include/rurp_pinout.h` (Phase 33 / v1.7 — silkscreen-label code-alias migration). Keep CTRL_* names + hex values in sync with the firmware header."*

- **Submodule commit:** `firestarter_app@907c7b2` (`feat(33-04): add RURP_CONTROL_REGISTER_BITS to constants.py + refresh main.py docstring`).
- **Meta-repo submodule-pointer bump:** `7821ef2a` → `782ef2a` (`feat(33-04): bump firestarter_app to 907c7b2 — Python CTRL_* parity (ALIAS-02)`).

### Task 2 — .planning/v1.7-SHIELD-REVS.md §7 fill (ALIAS-01)

- **Placeholder replaced.** `<!-- OWNED BY PHASE 33 — TBD -->` (line 107 pre-edit) removed.
- **3-paragraph preamble inserted** covering: (1) purpose of the canonical reference and downstream Phase 34/35 consumers; (2) 4-way namespace lock per Open Question Q1 (CTRL_* / PIN_* / RES_* / JMP_*); (3) label-type legend (S = silkscreen-printed via gerber `%TO.C,*%`; N = schematic-net-only) + sentinel vocabulary + source-citation format.
- **12-column table** with shape `silkscreen_label | label_type | canonical_alias | hex_value (legacy / rev2) | rev_0 | rev_1 | rev_2_0 | rev_2_1 | rev_2_2 | rev_2_3 | mod_rev_0 | source_citation`.
- **17 data rows** (≥16 required):
  - **9 control-register canonical bits** (all label_type N): CTRL_VPP_REGULATOR_ENABLE (0x80), CTRL_VPP_VPE_DROP_ENABLE (0x01 legacy / 0x100 rev2 — Pitfall 1 footnote), CTRL_READ_WRITE (0x40), CTRL_ADDRESS_LINE_18 (0x20 — Pitfall 3 footnote), CTRL_ADDRESS_LINE_17 (0x10), CTRL_VPP_P1_ENABLE (0x08), CTRL_VPE_ENABLE (0x04), CTRL_VPP_A9_ENABLE (0x02), CTRL_ADDRESS_LINE_16 (0x01 — Pitfall 1 footnote).
  - **3 per-rev variant rows** (all label_type N): CTRL_VPP_VPE_DROP_ENABLE_REV1 (Rev 0/1 only), CTRL_VPP_VPE_DROP_ENABLE_REV2 (Rev 2.x only), CTRL_ADDRESS_LINE_18_REV2 (Rev 2.x, aliased to CTRL_VPP_P1_ENABLE per Pitfall 3).
  - **1 reserved row** (label_type N): CTRL_ADDRESS_LINE_13 (0x20 — reserved per Open Question Q2, no current call-site).
  - **2 Arduino-pin rows** (label_type N): PIN_VPP_VOLTAGE_ADC (A2 — all revs), PIN_HW_REVISION_DETECT_ADC (A3 — Rev 2.x only, `not-present` for Rev 0/1).
  - **2 shield-level designator rows** (label_type S — physically silkscreen-printed): R41 → RES_HW_REVISION_DIVIDER (`not-present` Rev 0/1; `✓ (4k7)` Rev 2.0/2.1; `✓ (4k7 sch / 10k chat — pending Phase 35 §5 follow-up #5 measurement)` Rev 2.2; `✓ (10k)` Rev 2.3; `as-modified — pending Phase 35` Mod Rev 0); JP4 → JMP_VPP_P1_BYPASS (similar shape; 1x2 header for Rev 2.0/2.1/2.2; 2x2 footprint change in Rev 2.3 per §5 mechanical delta).
- **Alias-namespace breakdown:** 13 CTRL_* / 2 PIN_* / 1 RES_* / 1 JMP_* = 17 rows total. Every canonical_alias matches `^(CTRL|PIN|RES|JMP)_[A-Z0-9_]+$`.
- **D-09 mod_rev_0 sentinel coverage:** 15 rows carry `(inherits Rev 0)` (control-register bits + Arduino pins — rework is hand-wire-level, not control-register-layout-level). 2 rows (R41 + JP4) carry `as-modified — pending Phase 35` (physical shield designators may have been altered by the hardware-bug-A/B rework — full trace pending Phase 35 follow-up #4).
- **Source citations:** schematic-net rows cite `rurp_pinout.h` (post-Wave-3 canonical) + `mine-notes.md:434` (per-rev `.kicad_sch` net-label evidence from the Phase 31 grep session). Silkscreen-printed rows cite `mine-notes.md:429-430` (`%TO.C,R41*%` and `%TO.C,JP4*%` in Rev 2.2 gerber) + per-rev .kicad_sch line refs at `:444 / :461 / :499` (Rev 2.0 / 2.1 / 2.3 blob SHA + line NNNN).
- **Meta-repo commit:** `7e7e3f0` (`docs(33-04): fill v1.7-SHIELD-REVS.md §7 silkscreen → code alias table (ALIAS-01)`).

## Verification

### Task 1 (host CLI) verification

| Check | Command | Result |
|-------|---------|--------|
| RURP_CONTROL_REGISTER_BITS block header present | `grep -q '# RURP Control Register Bits' constants.py` | PASS |
| CTRL_VPP_REGULATOR_ENABLE = 0x080 | grep | PASS |
| CTRL_VPP_VPE_DROP_ENABLE = 0x100 | grep | PASS |
| CTRL_ADDRESS_LINE_16 = 0x001 | grep | PASS |
| 9 CTRL_* constants present | grep -c | 9 (PASS) |
| main.py docstring contains `0x100 - CTRL_VPP_VPE_DROP_ENABLE` | grep | PASS |
| main.py docstring contains `0x001 - CTRL_ADDRESS_LINE_16` | grep | PASS |
| main.py cross-reference line `RURP_CONTROL_REGISTER_BITS` | grep | PASS |
| firestarter_app/CLAUDE.md references rurp_pinout.h | grep | PASS |
| main.py typos `argumet` + `sheild` preserved | grep | PASS |
| `from firestarter import constants; assert constants.CTRL_VPP_REGULATOR_ENABLE == 0x080 and constants.CTRL_VPP_VPE_DROP_ENABLE == 0x100` | python -c | PY-IMPORT OK |
| pytest in firestarter_app | `pytest -x` | 82/82 PASS (0.81 s) |
| `firestarter --help` loads cleanly | smoke test | PASS |
| `firestarter dev reg --help` shows refreshed docstring | smoke test | PASS (all 9 CTRL_* lines shown + cross-reference line) |

### Task 2 (§7 fill) verification

| Check | Command | Result |
|-------|---------|--------|
| Placeholder `<!-- OWNED BY PHASE 33 — TBD -->` removed | `! grep -q '<!-- OWNED' v1.7-SHIELD-REVS.md` | PASS |
| §7 heading `## 7. Silkscreen → Code Alias Table` present | grep | PASS |
| Pipe-prefixed lines in §7 (header + sep + data rows) | `awk … grep -c '^|\\ '` | 18 (≥17 required — PASS) |
| Data rows with canonical alias matching `(CTRL|PIN|RES|JMP)_` | awk + grep | 17 (≥16 required — PASS) |
| Every canonical_alias matches `^(CTRL|PIN|RES|JMP)_[A-Z0-9_]+$` | awk + regex | 17/17 PASS |
| Contains CTRL_VPP_REGULATOR_ENABLE | grep | PASS |
| Contains RES_HW_REVISION_DIVIDER | grep | PASS |
| Contains JMP_VPP_P1_BYPASS | grep | PASS |
| Contains PIN_HW_REVISION_DETECT_ADC | grep | PASS |
| Contains `as-modified — pending Phase 35` | grep | PASS |
| Contains `(inherits Rev 0)` | grep | PASS |
| Contains `mine-notes.md` citation | grep | PASS |
| Contains `rurp_pinout.h` code anchor | grep | PASS |

### Post-Wave-4 gate verification (firmware unchanged — GATE-1.7)

- **check-migration.sh:** `PASS: alias migration verified clean` (all 3 assertions: 0 old-name hits + 0 REV_[12]_ hits + cmp byte-identical for uno + uno328pb + leonardo).
- **.hex byte-identical post-Wave-4:** all 3 AVR envs identical to Wave-0 baseline.

| Board | Pre-Wave-4 size | Post-Wave-4 size | Δ | sha256 (post) |
|-------|-----------------|------------------|---|----------------|
| uno | 62,617 B | 62,617 B | 0 B | `5e7f393a48543b4d2c95f48c37a3751814a3221afebda6866eb4a7d73be28927` |
| uno328pb | 62,854 B | 62,854 B | 0 B | `d9e51b7e54fe26af6a3286ae8a6e483b56892936c4efd15c13dad9ed22e91ee7` |
| leonardo | 68,876 B | 68,876 B | 0 B | `9bc0ed128fb0729c6952c2a8e922516fc42a47f49426f3d6e641a6536ed6095e` |

GATE-1.7 ALIAS-03 holds: Δ = 0 B across all 3 envs (vs. ≤ ~50 B per-board budget). Phase 33 introduces zero AVR-side regression — Python parity is documentary-only, §7 fill is meta-repo doc.

## Deviations from Plan

None — plan executed exactly as written. Task 1 + Task 2 ran clean, no Rules 1-4 triggers, no checkpoints needed.

## Cross-cutting context preserved

- **firestarter_app/firestarter/config.py drift** — the pre-existing uncommitted refactor of `get_local_database`, `get_local_pin_maps`, `ConfigManager._load_config`, and `update_config` was NOT touched. Verified post-commit: `git status --porcelain firestarter/config.py` → ` M firestarter/config.py` (still unstaged). This drift predates Phase 33 and carries forward on the v1.7-shield-investigation branch unchanged.
- **Branch model invariant:** firestarter_app sub-repo + meta-repo both on `v1.7-shield-investigation` per `feedback_branching` memory; sub-repo work commits inside the submodule first, then a pointer-bump commit lands in the meta-repo (per sequential_execution contract).

## Phase 33 close-out

**Requirements met across all 4 plans (33-00 → 33-04):**

| Requirement | Met in | Evidence |
|-------------|--------|----------|
| ALIAS-01 (silkscreen → code alias inventory in §7) | 33-04 Task 2 | 17-row populated table in `.planning/v1.7-SHIELD-REVS.md` §7; 4-way namespace split (13 CTRL_* / 2 PIN_* / 1 RES_* / 1 JMP_*); mine-notes.md + rurp_pinout.h cross-citations; D-09 sentinels |
| ALIAS-02 (firmware aliases land + call-sites migrated + Python mirror) | 33-01 (header create) + 33-02 (src/proms call-sites) + 33-03 (remaining headers + native test + atomic D-06 delete) + 33-04 Task 1 (Python parity) | Firmware: rurp_pinout.h created, all 13 files migrated, rurp_shield.h:25-89 deleted atomically. Python: RURP_CONTROL_REGISTER_BITS block added; main.py docstring refreshed; firestarter_app/CLAUDE.md sync rule extended. |
| ALIAS-03 (GATE-1.7 non-regression — .hex byte-identical) | 33-00 (baseline) + 33-01/02/03 (per-wave cmp) + 33-04 (post-Wave-4 cmp) | All 3 AVR envs: Δ = 0 B from Wave 0 baseline to post-Wave-4. check-migration.sh PASS at every wave boundary including post-Wave-4. pio test -e native 20/20 PASS. pytest 82/82 PASS. |

**Pending (Phase 33 closes the firmware + host migration; Phase 34/35 consume the substrate):**

- **Phase 34 (Shield-Version-Detect Design + Firmware Plumbing):** will consume the new RES_HW_REVISION_DIVIDER + PIN_HW_REVISION_DETECT_ADC aliases from §7 for the ADC band-table substrate; the §7 row schema is the canonical reference for per-rev detect-resistor values.
- **Phase 35 (Documentation + Milestone Close):** will refresh §7 footnotes once operator photos land (D-02 follow-up) — currently the 4k7-vs-10k Rev 2.2 R41 discrepancy and the Modified Rev 0 R41/JP4 rework cells carry `pending Phase 35` / `as-modified — pending Phase 35` sentinels that will be resolved by physical measurement + photographic verification.

## Self-Check: PASSED

- [x] firestarter_app/firestarter/constants.py present + contains RURP_CONTROL_REGISTER_BITS block (`grep -q '# RURP Control Register Bits' constants.py` → PASS)
- [x] firestarter_app/firestarter/main.py present + docstring refreshed (`grep -q 'CTRL_VPP_VPE_DROP_ENABLE' main.py` → PASS)
- [x] firestarter_app/CLAUDE.md present + sync rule extended (`grep -q 'rurp_pinout.h' CLAUDE.md` → PASS)
- [x] .planning/v1.7-SHIELD-REVS.md present + §7 filled (`! grep -q '<!-- OWNED BY PHASE 33 — TBD -->'` → PASS; 17 data rows matching `^(CTRL|PIN|RES|JMP)_` namespace)
- [x] firestarter_app sub-repo commit `907c7b2` present (`git -C firestarter_app log --oneline | grep 907c7b2` → FOUND)
- [x] Meta-repo submodule-pointer-bump commit `782ef2a` present (`git -C /workspaces log --oneline | grep 782ef2a` → FOUND)
- [x] Meta-repo §7-fill commit `7e7e3f0` present (`git -C /workspaces log --oneline | grep 7e7e3f0` → FOUND)
- [x] check-migration.sh post-Wave-4 PASS (`bash check-migration.sh` → `PASS: alias migration verified clean`)
- [x] config.py drift preserved untouched (`git -C firestarter_app status --porcelain firestarter/config.py` → ` M firestarter/config.py`)
