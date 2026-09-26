---
phase: 101-fw-apply-names-in-firmware
plan: 02
subsystem: firmware
tags: [firmware, dispatch, protocol-naming, arduino, platformio, docs-sync, integration-gate]

# Dependency graph
requires:
  - phase: 100-name-canonical-protocol-name-set-operator-approval
    provides: operator-approved 14-token canonical PROTO_<NAME> map + handler-family layer (PROTOCOLS.md @ 6e7bd38)
  - phase: 101-fw-apply-names-in-firmware
    plan: 00
    provides: dispatch-mirror guard parser fixed for the Phase-100 two-table PROTOCOLS.md layout (GATE-01 prerequisite)
  - phase: 101-fw-apply-names-in-firmware
    plan: 01
    provides: firestarter/include/proto_constants.h (14 PROTO_<NAME> tokens) + memory.cpp dispatch chain relabeled
provides:
  - FW-03 conformance assertion — all 7 handler families (eprom/sram/flash4/flash3/eeprom28c/flash_intel/not-implemented) confirmed already matching Phase 100's approved family-name layer, zero renames
  - firestarter/CLAUDE.md dispatch-order list + Algorithm Handlers table synced to PROTO_ tokens (no dangling old prose names)
  - Full GATE-01/02/03 integration assertion — phase-closing proof of zero regression across the Wave-0/1/2 relabel
affects: [102-host-apply-names-in-cli, 103-docs-reconcile-protocols-md]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Conformance-confirm over rename: FW-03 satisfied by verifying approved names == existing configure_*/.cpp names, not by editing any handler file"
    - "Doc-sync-in-same-commit: firestarter/CLAUDE.md's dispatch/handler tables kept line-for-line consistent with the relabeled memory.cpp"

key-files:
  modified:
    - firestarter/CLAUDE.md

key-decisions:
  - "FW-03 satisfied via conformance confirmation (D-01) — grep-verified all 7 configure_*/.h symbols present, zero file/function renames, zero signature/extern-C/include-guard changes"
  - "No optional // serves PROTO_... cross-reference comments added to handler headers — the CLAUDE.md doc-sync already carries the PROTO_↔handler↔file mapping, so the header comments were judged redundant; explicitly permitted as optional by the plan, not required"
  - "platformio.ini working-tree whitespace diff (pre-existing, unrelated trailing-space removal on one comment line) left untouched — outside this plan's files_modified scope and not part of any prior task's commit"

patterns-established: []

requirements-completed: [FW-03, GATE-01, GATE-02, GATE-03]

coverage:
  - id: D1
    description: "All 7 handler families (eprom, sram, flash4, flash3, eeprom28c, flash_intel, not-implemented) confirmed conformant to Phase 100's approved family-name layer — zero renames"
    requirement: FW-03
    verification:
      - kind: unit
        ref: "grep -q configure_eprom/configure_sram/configure_flash4/configure_flash3/configure_eeprom28c/configure_flash_intel/configure_not_implemented across the 7 respective include/*.h headers — all 7 present"
        status: pass
      - kind: unit
        ref: "pio run -e uno (SUCCESS, 23516 B / 72.9%, byte-identical to Plan 01 baseline)"
        status: pass
    human_judgment: false
  - id: D2
    description: "firestarter/CLAUDE.md dispatch-order list + Algorithm Handlers table synced to PROTO_ tokens; no old prose names (EPROM_STD/FLASH_AMD_STD/FLASH_AMD_ALT/FLASH_EEPROM) remain"
    requirement: FW-03
    verification:
      - kind: unit
        ref: "grep -n 'EPROM_STD|FLASH_AMD_STD|FLASH_AMD_ALT|FLASH_EEPROM\\b' firestarter/CLAUDE.md — 0 matches (exit 1)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Full GATE-01/02/03 integration assertion green with zero source edits — native 82/82, uno+leonardo build SUCCESS, check_dispatch PASS, diff_db identity, constants-parity 6, dispatch-mirror 2, ruff check/format clean, mypy watermark held, no CLI file touched anywhere in the phase"
    requirement: "GATE-01, GATE-02, GATE-03"
    verification:
      - kind: integration
        ref: "pio test -e native — 82 test cases: 82 succeeded"
        status: pass
      - kind: integration
        ref: "pio run -e uno && pio run -e leonardo — both [SUCCESS] (Uno 23516 B/72.9%; Leonardo 25654 B/89.5%, byte-identical to v1.16 baseline)"
        status: pass
      - kind: integration
        ref: "python tools/check_dispatch.py — PASS: 746 chips scanned, 736 supported, 0 dispatch regressions, 0 consistency violations"
        status: pass
      - kind: integration
        ref: "python tools/diff_db.py — PASS: 2 pre-existing (Phase-94) changed chips explained, 0 new, 0 removed"
        status: pass
      - kind: unit
        ref: "pytest tests/test_revision_constants_parity.py -q — 6 passed (count unchanged, D-02 holds, no PROTO_ mirror added)"
        status: pass
      - kind: unit
        ref: "pytest tests/test_dispatch_mirror.py -q — 2 passed (Wave-0 fix holds green)"
        status: pass
      - kind: unit
        ref: "ruff check firestarter/ tests/ — All checks passed! ; ruff format --check firestarter/ tests/ — 77 files already formatted"
        status: pass
      - kind: unit
        ref: "python tools/check_mypy_watermark.py — 1 errors, 34 below watermark (35) — gate holds"
        status: pass
      - kind: other
        ref: "git log --name-only across the full v1.19 phase diff (Wave 0/1/2) — only tests/test_dispatch_mirror.py (host) + firestarter.h-adjacent firmware files touched; no CLI grammar file anywhere in the diff (GATE-03 by diff scope)"
        status: pass
    human_judgment: false

# Metrics
duration: 20min
completed: 2026-07-01
status: complete
---

# Phase 101 Plan 02: FW-03 Conformance + Doc Sync + Full GATE Integration Assertion Summary

**Confirmed all 7 firmware handler families already conform to Phase 100's approved name set (zero renames), synced firestarter/CLAUDE.md's dispatch/handler tables to the new PROTO_ tokens, and closed the phase with a green full GATE-01/02/03 integration assertion (native 82/82, both boards build SUCCESS byte-identical, all host guards PASS, no CLI touched).**

## Performance

- **Duration:** ~20 min
- **Tasks:** 2 completed
- **Files modified:** 1 (`firestarter/CLAUDE.md`)

## Accomplishments
- FW-03 conformance confirmed: all 7 handler families (`configure_eprom`/`eprom.cpp`, `configure_sram`/`sram.cpp`, `configure_flash4`/`flash_type_4.cpp`, `configure_flash3`/`flash_type_3.cpp`, `configure_eeprom28c`/`eeprom_28c.cpp`, `configure_flash_intel`/`flash_intel.cpp`, `configure_not_implemented`/`not_implemented.cpp`) already exactly match PROTOCOLS.md's approved family-name layer — the FW-03 requirement is satisfied with **zero function/file renames** (D-01 no-op confirmed empirically, not just by prior research)
- `firestarter/CLAUDE.md` dispatch-order list (items 1–6) and Algorithm Handlers table relabeled from old prose names (`EPROM_STD`, `EPROM_QUICK`, `EPROM_LEGACY`, `EEPROM_POLL`, `SRAM_*`, `FLASH_AMD_ALT`, `FLASH_AMD_STD`, `FLASH_EEPROM`, `FLASH_EEPROM2`, `FLASH_INTEL`) to the operator-approved `PROTO_<NAME>` tokens, keeping the "must match memory.cpp line-for-line" invariant true; added the previously-undocumented `0x34` / `PROTO_EEPROM_8051BUS` row
- Full phase-closing GATE-01/02/03 integration assertion run with **zero source edits** — proving the Wave-0 (dispatch-mirror fix) + Wave-1 (constants + dispatch relabel) + Wave-2 (this plan's doc sync) output introduced no regression:
  - GATE-01 (numbers stay dispatch key): `pio test -e native` 82/82 succeeded; `test_dispatch_mirror.py` 2/2 passed (Wave-0 fix holds)
  - GATE-02 (no DB/wire/value change): `check_dispatch.py` PASS (746 chips, 0 dispatch regressions, 0 consistency violations); `diff_db.py` identity (0 new, 0 removed — the 2 changed chips are the pre-existing Phase-94 `page_size` delta, unrelated to naming); `test_revision_constants_parity.py` 6/6 passed (count unchanged — no PROTO_ mirror added to `constants.py`, D-02 holds)
  - GATE-03 (CLI unchanged): confirmed by diff scope — the only `firestarter_app` file touched across the entire phase (Wave 0 + this plan) is `tests/test_dispatch_mirror.py` (a test, not CLI grammar); no protocol name/alias accepted as CLI input
  - Both boards build SUCCESS with byte-identical flash usage to the pre-relabel baseline: Uno 23516 B / 72.9%, Leonardo 25654 B / 89.5% (matches the v1.16 tip exactly)
  - Host CI gate (py3.11 target, run under local 3.12.13 per established precedent): `ruff check firestarter/ tests/` clean, `ruff format --check` clean (77 files formatted), mypy watermark held (1 error, 34 below the 35 ceiling)

## Task Commits

Each task was committed atomically:

1. **Task 1: Assert FW-03 handler-family conformance and sync firestarter/CLAUDE.md to PROTO_ tokens** - `89e9e56` (docs)
2. **Task 2: Full GATE-01/02/03 integration assertion — prove no-regression across the relabel** - no commit (assertion-only task; zero source edits produced, as expected for an integration-gate task — all results recorded above and in this SUMMARY)

**Plan metadata:** captured in this SUMMARY commit (meta repo)

## Files Created/Modified
- `firestarter/CLAUDE.md` — dispatch-order list (6 numbered items) + Algorithm Handlers table protocol column relabeled from old prose names to `PROTO_<NAME>` tokens; added the 0x34 row

## Decisions Made
- **FW-03 via conformance-confirm, not rename (D-01 upheld empirically):** ran the grep-assertion chain against all 7 handler headers this session (not just relied on prior research) — all 7 `configure_*` symbols present, confirming zero delta between the approved family-name layer and the existing code. No handler file or function was touched.
- **No optional `// serves PROTO_...` cross-reference comments added to handler headers:** the plan permitted these as optional (RESEARCH rec #2 / PATTERNS "if the planner elects"); judged unnecessary since the CLAUDE.md doc-sync already documents the PROTO_↔handler↔file mapping in one authoritative table, and adding per-header comments would be a second place to keep in sync with no functional benefit. This does not violate any acceptance criterion — the criteria only require the comments be *comment-only* if added, not that they be mandatory.
- **`platformio.ini` pre-existing whitespace diff left untouched:** a one-line trailing-whitespace removal on a comment line was present in the working tree at plan start (unrelated to any Plan 101-00/01/02 commit); it is outside this plan's `files_modified: [firestarter/CLAUDE.md]` scope, so it was not staged or committed by this plan.

## Deviations from Plan

None — plan executed exactly as written. Task 1's optional cross-reference-comment sub-step was consciously skipped as genuinely optional (see Decisions Made above), which is within the plan's stated discretion, not a deviation from a mandated action.

## Issues Encountered

None. Both tasks completed on the first pass with all verification commands green.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **Phase 101 (fw-apply-names-in-firmware) is now fully closed.** FW-01/FW-02 (Plan 01), FW-03 (this plan), and GATE-01/02/03 (this plan, phase-closing) are all satisfied with a fully green guard suite and zero behavioral regression.
- **Phase 102 (host-apply-names-in-cli)** can proceed: it consumes the same PROTOCOLS.md name set to consolidate the two divergent host display-name vocabularies (`ic_layout.proto_display` + `protocol_info_data`). No firmware blocker remains.
- **Phase 103 (docs — reconcile PROTOCOLS.md prose + INV matrix)** has no open dependency on this plan.
- Gitlinks remain PINNED per standing policy — this plan did not bump the meta-repo submodule pointer (per `<submodule_commit_protocol>`); the orchestrator owns that after the wave completes.

## Self-Check: PASSED

- FOUND: `.planning/phases/101-fw-apply-names-in-firmware/101-02-SUMMARY.md`
- FOUND: firestarter commit `89e9e56` (docs(101-02): sync CLAUDE.md dispatch/handler tables to PROTO_ tokens)
- FOUND: meta commit `15b3e33` (docs(101-02): add plan 02 SUMMARY)

---
*Phase: 101-fw-apply-names-in-firmware*
*Completed: 2026-07-01*
