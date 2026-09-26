---
phase: 129-flash-path-decision-pcb-requirements-record
plan: 04
subsystem: docs
tags: [decision-record, py32f071, pcb-checklist, flash-budget, vtor-correction]

requires:
  - phase: 129-03
    provides: ".planning/v1.23-FLASH-PATH-DECISION.md — header block, §1 Context (six sourced subsections + Revision Note), §2 [SHARED:S1] the three-tier flash-path decision"
provides:
  - ".planning/v1.23-FLASH-PATH-DECISION.md — §3 the pre-schematic PCB checklist [SHARED:S2] (seven R1-R7 rows plus a Deliberately undecided subsection) and §4 the flash budget as actually reserved [SHARED:S3] (reserved map, today's footprint, bootloader budget, D-12's corrected migration cost)"
affects: [129-05, 129-06, 129-07, 129-08, 129-09]

tech-stack:
  added: []
  patterns:
    - "Checklist row shape: '- [ ] **R<n> — <title>**' followed by two-space-indented '- *Why:*' / '- *Breaks if omitted:*' lines, each carrying 20+ chars — parsed mechanically by test_flash_path_record_sync.py's _checklist_rows"
    - "Bootloader figure never appears without a migration/re-flash/ORIGIN cost token within the same line or a two-line window (D-10's proximity rule)"

key-files:
  created: []
  modified:
    - .planning/v1.23-FLASH-PATH-DECISION.md

key-decisions:
  - "§3's R3 row states the PB0-PB7 contiguity constraint as a package-selection decision (viable: LQFP64/CSP64/QFN64/LQFP48/QFN48; ruled out: QFN56/QFN32), per F-10, rather than a plain pin-assignment row"
  - "§4's three-sector (24 KiB) verdict row carries ORIGIN, migration and re-flash all in the same table-row line as the figure, satisfying D-10's proximity rule trivially (zero lines apart) rather than relying on the two-line window"
  - "§4's correction paragraph restates C-1 (VTOR present, SCB->VTOR written at boot) without literally naming any no-VTOR workaround scheme (no 'MEM_MODE', 'trampoline' or 'RAM vector copy' token), since RESEARCH C-1 establishes those are the wrong mitigation class once VTOR is confirmed present"

patterns-established:
  - "Deliberately undecided subsection names socket/ZIF, connector and power budget with one sentence each on what would have to be known before deciding — established as the shape for stating a record's own edges rather than leaving silence to be misread as 'no constraint'"

requirements-completed: []

coverage:
  - id: D1
    description: "§3 [SHARED:S2] — seven well-formed checklist rows (R1-R7) covering PCB-02's four named items (BOOT0/nBOOT1 strap, SWD pads, contiguous data bus, HSE hedge) plus the three D-14 additions (VPP sense, test points, USB connector/D+ pull-up) plus F-10's package-selection constraint, with a 'Deliberately undecided' subsection naming socket/ZIF, connector and power budget"
    requirement: "PCB-02"
    verification:
      - kind: unit
        ref: "pytest tests/test_flash_path_record_sync.py::TestFlashPathRecordSync::test_meta_extract_is_non_vacuous[S2] and ::test_pcb_checklist_rows_are_wellformed[meta] -- 2 passed"
        status: pass
    human_judgment: false
  - id: D2
    description: "§4 [SHARED:S3] — the reserved flash map transcribed verbatim from the linker script, today's delta-only application footprint, the two bootloader anchors, the three-sector (24 KiB) verdict with its migration cost in the same row, and D-12's corrected cost framing (C-1: VTOR present, fleet re-flash is the real cost) with zero no-VTOR workarounds enumerated"
    requirement: "PCB-03"
    verification:
      - kind: unit
        ref: "pytest tests/test_flash_path_record_sync.py::TestFlashPathRecordSync::test_meta_extract_is_non_vacuous[S3], ::test_flash_budget_cites_reserved_map[meta], ::test_bootloader_figure_carries_its_cost[meta] -- 3 passed"
        status: pass
    human_judgment: false
  - id: D3
    description: "Meta commit contains only the record file; REQUIREMENTS.md, ROADMAP.md and both submodule gitlinks untouched; RED ledger drops from 29 failed/192 passed to exactly 24 failed/197 passed"
    verification:
      - kind: unit
        ref: "git show --stat --format= HEAD (1 file); git diff --name-only HEAD~1 HEAD -- .planning/REQUIREMENTS.md .planning/ROADMAP.md firestarter firestarter_app (empty); pytest tests/ -q -- 24 failed, 197 passed"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-08-02
status: complete
---

# Phase 129 Plan 04: PCB Checklist and Reserved Flash Budget Summary

**Appended §3 (seven-row pre-schematic PCB checklist, [SHARED:S2]) and §4 (flash budget as Phase 126 actually reserved it, [SHARED:S3]) to `.planning/v1.23-FLASH-PATH-DECISION.md`, discharging five gate legs and dropping the firmware RED ledger from 29 to exactly 24.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-08-02 (continuation of the 129-01..129-03 session)
- **Completed:** 2026-08-02
- **Tasks:** 3 (2 content, 1 content + commit)
- **Files modified:** 1

## Accomplishments

- **Task 1 — §3 the pre-schematic PCB checklist.** Seven checkbox rows (R1-R7), each a title plus exactly one `*Why:*` rationale line and one `*Breaks if omitted:*` consequence line: BOOT0/nBOOT1 strap reachability, SWD pads including `nRST`, the PB0-PB7 contiguous data bus stated as a package-selection constraint (viable packages LQFP64/CSP64/QFN64/LQFP48/QFN48; QFN56/QFN32 ruled out per F-10), the depopulated HSE crystal-less-USB hedge, VPP sense on PA4/ADC channel 4, data-bus test points, and the USB connector/D+ pull-up open question. A `### Deliberately undecided` subsection follows, naming socket/ZIF, connector family and power budget as genuinely open rather than silently omitted.
- **Task 2 — §4 the flash budget as actually reserved.** Five parts: (a) the reserved map transcribed verbatim from `platform/py32f071/linker/PY32F071xB_FLASH.ld` (BOOTLOADER/FLASH/CONFIG/RAM regions, all four `__config_*` symbols) with its geometry citation chain; (b) today's application footprint (`27,372` B, `192` B vector table) tagged local-build-only; (c) the two bootloader anchors (Puya's `12,032` B factory bootloader; this tree's measured `~14.6 KiB`) and the sector-quantised verdict table, with the three-sector/`24 KiB` row carrying `ORIGIN`, `migration` and `re-flash` in the same line as the figure; (d) D-12's corrected cost paragraph — the part **has** a VTOR (`__VTOR_PRESENT`, `SCB->VTOR`), so the vector-table move is cheap and the fleet re-flash is the real cost — with zero no-VTOR workaround schemes enumerated; (e) supersessions and hand-offs to FUT-N05/FUT-N06.
- **Task 3 — commit.** Staged exactly `.planning/v1.23-FLASH-PATH-DECISION.md`; verified the meta branch stayed on `gsd/v1.23-py32f071-integration`; confirmed `REQUIREMENTS.md`, `ROADMAP.md` and both submodule gitlinks are untouched by the commit; confirmed the firmware suite moved to `24 failed, 197 passed`, matching the plan's own prediction exactly.

## Task Commits

1. **Tasks 1+2+3 (single commit per the plan's own Task 3 instruction):** `e2d60b1` (docs) — `docs(129-04): PCB checklist and the reserved flash budget in the v1.23 flash-path record`

**Recorded verbatim (per plan's `<output>` instruction):**
- Row-shape counts: 7 row headers (`R1`-`R7`), 7 `*Why:*` lines, 7 `*Breaks if omitted:*` lines, 1 `### Deliberately undecided` heading.
- Pytest before this plan's content: `29 failed, 192 passed`
- Pytest after this plan's content: `24 failed, 197 passed` (matches the plan's own prediction exactly)
- Discharged node ids: `TestFlashPathRecordSync::test_meta_extract_is_non_vacuous[S2]`, `TestFlashPathRecordSync::test_pcb_checklist_rows_are_wellformed[meta]`, `TestFlashPathRecordSync::test_meta_extract_is_non_vacuous[S3]`, `TestFlashPathRecordSync::test_flash_budget_cites_reserved_map[meta]`, `TestFlashPathRecordSync::test_bootloader_figure_carries_its_cost[meta]`
- Meta commit SHA: `e2d60b1` on branch `gsd/v1.23-py32f071-integration`
- Firmware branch: `v1.23-py32f071-integration` @ `42395cf` (unchanged this plan — no firmware file touched, no gitlink bump)

## Files Created/Modified

- `.planning/v1.23-FLASH-PATH-DECISION.md` — appended `## 3. PCB requirements before the first schematic [SHARED:S2]` (seven rows + Deliberately undecided subsection) and `## 4. Flash budget, as actually reserved [SHARED:S3]` (five-part structure)

## Decisions Made

- **R3's rationale states the package-selection constraint explicitly** (viable: LQFP64/CSP64/QFN64/LQFP48/QFN48; ruled out: QFN56/QFN32), per RESEARCH F-10, rather than writing it as an ordinary pin-assignment row — this is the row D-14 calls out as absent from CONTEXT.md.
- **The three-sector/24 KiB verdict table row places `ORIGIN`, `migration` and `re-flash` on the identical source line as the figure itself**, satisfying D-10's two-line proximity rule with zero lines of separation rather than relying on the window's outer edge.
- **No no-VTOR workaround scheme is named anywhere in §4's correction paragraph** — verified by a zero-hit case-insensitive grep for `MEM_MODE|trampoline|RAM vector copy` — because RESEARCH C-1 establishes these are the wrong mitigation class once `__VTOR_PRESENT` is confirmed, and naming them would document a problem this part does not have.
- **§4(b)'s honesty sentence and the `27,372` B figure sit in the same paragraph as the word `local`**, so no reader can lift the figure as CI-comparable.

## Deviations from Plan

None — plan executed exactly as written. Every acceptance-criteria grep and every `<verify><automated>` block in the plan's three tasks was run and passed before committing.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- §3 and §4 are ready for later plans: 129-05 adds §5 (VID/PID, `[SHARED:S4]`) and §6 (socket-empty instruction, `[SHARED:S5]`); 129-06 mirrors all five `[SHARED:Sn]` bodies (including this plan's §3/§4) into the firmware subset and discharges the `fw`-side and parity legs; 129-07 fixes the linker comment's false "on a part with no VTOR" clause; 129-08 updates the seed's frontmatter status; 129-09 is the only plan permitted to tick PCB-01..PCB-05.
- `test_meta_extract_is_non_vacuous[S4]`/`[S5]` and all `fw`/`readme`/`test_shared_sections_match` legs remain RED until later plans write those sections — expected per the discharging-plan ledger in `test_flash_path_record_sync.py`'s own docstring.
- No blockers. Meta repo clean apart from the intentional pre-existing dirty gitlinks (`firestarter`, `firestarter_app` — both left unbumped for `129-09`, confirmed unchanged by this plan's commit via `git diff HEAD~1 HEAD -- firestarter firestarter_app` returning zero bytes). Firmware tree untouched and clean at `42395cf`.

---
*Phase: 129-flash-path-decision-pcb-requirements-record*
*Completed: 2026-08-02*
