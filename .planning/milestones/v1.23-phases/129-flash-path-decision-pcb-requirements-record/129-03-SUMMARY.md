---
phase: 129-flash-path-decision-pcb-requirements-record
plan: 03
subsystem: docs
tags: [decision-record, py32f071, flash-path, vtor-correction, honesty-ledger]

requires:
  - phase: 129-02
    provides: "firestarter/tests/test_flash_path_record_sync.py — TestFlashPathRecordSync's 31 RED legs, including test_meta_extract_is_non_vacuous[S1] and test_three_tiers_and_non_retirement[meta/fw]"
provides:
  - ".planning/v1.23-FLASH-PATH-DECISION.md — the authoritative record's header block, §1 Context (six sourced subsections + Revision Note), and §2 the three-tier flash-path decision [SHARED:S1]"
affects: [129-04, 129-05, 129-06, 129-07, 129-08, 129-09]

tech-stack:
  added: []
  patterns:
    - "Milestone-prefixed SCREAMING-KEBAB decision doc at .planning/ root (D-02), no adr/ directory, no ADR numbering scheme"
    - "Per-claim confidence tags in headings and mid-sentence ([VERIFIED]/[CITED]/[ASSUMED]/[UNVERIFIED-UNTIL-SILICON]), closed by a blanket ## Claim ceiling later plan will add"
    - "Revision Note shape borrowed from v1.9-COBS-DECISION.md §2.0: what-was-believed / what-is-true / how-established / what-it-supersedes, per correction"

key-files:
  created:
    - .planning/v1.23-FLASH-PATH-DECISION.md
  modified: []

key-decisions:
  - "Anchored-to SHA uses the HEAD recorded in 129-01's SUMMARY (3393137...) per the plan's explicit instruction, not the current firmware HEAD (42395cf, post-129-02) — a deliberate planner choice, not a staleness bug"
  - "§1.1 states that §4 owns the address table and deliberately does not repeat any ORIGIN/LENGTH value, per the plan's explicit anti-duplication instruction (two copies of one table is the drift the D-03 gate exists to catch)"
  - "§1.6 records all three corrections (VTOR present, 0x36B7 allocated to Puya, 14.6 KiB bootloader floor) but hands the REQUIREMENTS.md/ROADMAP.md/linker-comment prose correction to Phase 130's CLOSE-01 by name — no such file was touched this plan"

patterns-established:
  - "No no-VTOR workaround (SYSCFG MEM_MODE remap, RAM vector copy, trampoline) is enumerated anywhere in this record — verified by a zero-hit case-insensitive grep, per RESEARCH C-1's explicit warning that these are irrelevant once VTOR is confirmed present"

requirements-completed: []

coverage:
  - id: D1
    description: "Header block carries all five [SHARED:Sn] keys in one line, the D-02 milestone-prefixed filename with no adr/ directory, and the five-tag confidence-tag legend"
    requirement: "PCB-01"
    verification:
      - kind: unit
        ref: "grep -qF checks for '[SHARED:S1]'..'[SHARED:S5]', '0ed2f4b4d3391eccfd4491006a30295fd78e32c2', 'test_flash_path_record_sync.py' against .planning/v1.23-FLASH-PATH-DECISION.md"
        status: pass
    human_judgment: false
  - id: D2
    description: "Section 1's six subsections (1.1-1.6) carry every sourced fact with heading-level confidence tags; the Revision Note records all three corrections and enumerates zero no-VTOR workarounds"
    verification:
      - kind: unit
        ref: "grep -cE '^### 1\\.[1-6] ' == 6; grep -ciE 'MEM_MODE|trampoline|RAM vector copy' == 0; full needle scan (PF8, nBOOT1, PA13, PA14, nRST, PA11, PA12, USBD_SOF, LQFP64, QFN56, QFN32, PB2, PB3, __VTOR_PRESENT, SCB->VTOR, CLOSE-01, FUT-N04, Puya Semiconductor, usbd_cdc_if.c, pycdc.inf, 14.6 KiB, re-flash) all present"
        status: pass
    human_judgment: false
  - id: D3
    description: "Section 2 [SHARED:S1] carries the verbatim non-retirement sentence and every _S1_NEEDLES entry; the two named gate legs turn GREEN; the RED ledger drops from 31 to exactly 29"
    requirement: "PCB-01"
    verification:
      - kind: unit
        ref: "pytest \"tests/test_flash_path_record_sync.py::TestFlashPathRecordSync::test_meta_extract_is_non_vacuous[S1]\" \"tests/test_flash_path_record_sync.py::TestFlashPathRecordSync::test_three_tiers_and_non_retirement[meta]\" -q -- 2 passed; pytest tests/ -q -- 29 failed, 192 passed"
        status: pass
    human_judgment: false

duration: 30min
completed: 2026-08-02
status: complete
---

# Phase 129 Plan 03: Flash-Path Record — Header, Context, and the Three-Tier Decision Summary

**Created `.planning/v1.23-FLASH-PATH-DECISION.md` — the authoritative v1.23 flash-path and PCB requirements record's header block, six-subsection Context section (with a Revision Note correcting three factual premises this milestone's own planning documents got wrong), and the `[SHARED:S1]` three-tier flash-path decision — discharging PCB-01's two gate legs and dropping the RED ledger from 31 to 29.**

## Performance

- **Duration:** ~30 min
- **Started:** 2026-08-02 (continuation of the 129-01/129-02 session)
- **Completed:** 2026-08-02
- **Tasks:** 3 (2 content, 1 content + commit)
- **Files modified:** 1 created

## Accomplishments

- **Task 1 — header block.** Milestone-prefixed SCREAMING-KEBAB filename at `.planning/` root (D-02), no `adr/` directory, no ADR numbering. Metadata block names all five `[SHARED:Sn]` keys in one line, cites the subset's future location (`firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md`) and the D-03 sync gate that enforces parity, and anchors to both the firmware HEAD recorded in 129-01's SUMMARY and the pinned SDK `GIT_TAG`. Reader-routing `## Summary` and a five-tag confidence-tag legend close out the header.
- **Task 2 — §1 Context, six subsections.** Sourced substrate for a schematic author: the flash map pointer to §4 (no duplicated address table), the BOOT0/nBOOT1 boot-mode table with the unresolved-default hazard, SWD pin facts, USB pins/crystal-less-USB/HSE-hedge reasoning, the seven-package PB0–PB7 contiguity table (QFN56/QFN32 ruled out), and §1.6's Revision Note recording all three corrections RESEARCH surfaced: the part **has** a VTOR (`__VTOR_PRESENT 1`, `SCB->VTOR` written in `SystemInit`), `0x36B7` is allocated to Puya Semiconductor and copied verbatim from the pinned SDK's own CDC example, and the seed's bootloader-size estimate is off by roughly a factor of five (14.6 KiB measured vs. "a few KB"). Each correction states what was believed, what is true, how it was established, and what it supersedes — and explicitly hands the `REQUIREMENTS.md`/`ROADMAP.md`/linker-comment prose correction to Phase 130's `CLOSE-01` by name rather than performing it here.
- **Task 3 — §2 `[SHARED:S1]` the three-tier decision, and the commit.** Fixed the three routes in priority order (self-flash bootloader intended primary, factory USB DFU maintainer/manufacturing recovery, SWD last resort), each tier's reliability/cost/hazard facts, and the verbatim non-retirement sentence the gate pins character-for-character. Committed exactly one file on the meta branch.

## Task Commits

1. **Tasks 1+2+3 (single commit per the plan's own Task 3 instruction):** `8515a59` (docs) — `docs(129-03): v1.23 flash-path record — context, corrections and the three-tier decision`

**Recorded verbatim (per plan's `<output>` instruction):**
- Pytest before this plan's content: `31 failed, 190 passed`
- Pytest after this plan's content: `29 failed, 192 passed` (matches the plan's own prediction exactly)
- Discharged node ids: `TestFlashPathRecordSync::test_meta_extract_is_non_vacuous[S1]`, `TestFlashPathRecordSync::test_three_tiers_and_non_retirement[meta]`
- Meta commit SHA: `8515a59` on branch `gsd/v1.23-py32f071-integration`
- Firmware branch: `v1.23-py32f071-integration` @ `42395cf3ada60e6a93d6991e5e8b3118664e10e6` (unchanged this plan — no firmware file touched, no gitlink bump)

## Files Created/Modified

- `.planning/v1.23-FLASH-PATH-DECISION.md` — created: header block, `## Summary`, confidence-tag legend, `## 1. Context` (§1.1–§1.6), `## 2. Decision — the three-tier flash path [SHARED:S1]`

## Decisions Made

- **Anchored-to SHA follows the plan's literal instruction** ("the HEAD recorded in 129-01's SUMMARY") rather than the firmware's actual current HEAD (129-02 advanced it further to `42395cf`). This is the plan's own wording, not a staleness error — flagged here for the closing plan's awareness in case a later reader expects the anchor to track the moving branch tip.
- **§1.1 states no address values** — only points at §4 — following the plan's explicit anti-duplication instruction (the D-03 sync gate exists specifically to catch two divergent copies of one table).
- **§1.6 hands the prose correction to Phase 130's CLOSE-01 by name** rather than editing `REQUIREMENTS.md`, `ROADMAP.md`, or the linker script's `BOOTLOADER` comment — none of those files were touched this plan, consistent with the orchestrator's hard constraints and D-11/129-07's ownership of the linker-comment fix.
- **Zero no-VTOR workarounds enumerated** — `SYSCFG MEM_MODE` remap, RAM vector copy, and trampoline relocation are all absent from the document (confirmed via a zero-hit case-insensitive grep), since RESEARCH C-1 establishes these are the wrong mitigation class once VTOR is confirmed present.

## Deviations from Plan

None — plan executed exactly as written. Every acceptance-criteria grep and every `<verify><automated>` block in the plan's three tasks was run and passed before proceeding to the next task, and again before this Summary was written.

## Issues Encountered

None. The only two `--` (double-hyphen) matches in the file are markdown table separator rows (`|---|---|...`), not prose em-dash substitutes — confirmed by manual inspection, no wording change needed.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- §1's six subsections and §2's `[SHARED:S1]` section are ready for later plans to build on: 129-04 adds §3 (PCB checklist, `[SHARED:S2]`) and §4 (flash budget, `[SHARED:S3]`); 129-05 adds §5 (VID/PID, `[SHARED:S4]`) and §6 (socket-empty instruction, `[SHARED:S5]`); 129-06 mirrors all five `[SHARED:Sn]` bodies into the firmware subset and discharges the `fw`-side and parity legs; 129-07 fixes the linker comment's false "on a part with no VTOR" clause (using this plan's §1.6 Correction 1 as its citable source); 129-08 updates the seed's frontmatter status and links it to this record.
- `test_meta_extract_is_non_vacuous[S2]`…`[S5]` remain RED until their respective sections are written by later plans — expected per the discharging-plan ledger in `test_flash_path_record_sync.py`'s own docstring.
- No blockers. Meta repo clean apart from the intentional pre-existing dirty gitlinks (`firestarter`, `firestarter_app` — both left unbumped for `129-09`, both confirmed unchanged by this plan's commit via `git diff HEAD~1 HEAD -- firestarter firestarter_app` returning zero bytes). Firmware tree untouched and clean at `42395cf3ada60e6a93d6991e5e8b3118664e10e6`.

---
*Phase: 129-flash-path-decision-pcb-requirements-record*
*Completed: 2026-08-02*
