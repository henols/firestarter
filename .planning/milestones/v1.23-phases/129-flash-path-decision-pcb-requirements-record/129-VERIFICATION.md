---
phase: 129-flash-path-decision-pcb-requirements-record
verified: 2026-08-02T00:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 129: Flash-Path Decision & PCB Requirements Record Verification Report

**Phase Goal:** Every PCB decision that is free today and unrecoverable after layout is written
down, citing the flash map Phase 126 actually reserved rather than one merely intended.
**Verified:** 2026-08-02
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

This is a documentation-and-gate phase. Verification therefore weighs (1) whether the gate that
judges the two record copies genuinely predates the content it judges, (2) whether the gate's 41
legs are substantive rather than hollow, (3) whether the one authorized mid-phase deviation
(the linker-locator fix) actually holds to its RED-preserving proof, (4) whether the durable
artifacts stay inside the milestone's honesty ceiling, and (5) whether the five requirement ticks
are earned. All five were independently re-executed rather than taken from SUMMARY.md or
129-NONREGRESSION.md's own say-so.

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A committed ADR-style record names the three-tier flash path and states DFU-landing does not retire the self-flash seed | VERIFIED | `.planning/v1.23-FLASH-PATH-DECISION.md` §2 `[SHARED:S1]`; `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md` §"three-tier flash path" byte-identical; `_L1_NON_RETIREMENT` sentence present verbatim in both; `test_three_tiers_and_non_retirement[meta]`/`[fw]` re-run PASS |
| 2 | PCB requirements recorded as distinct, checkable line items (BOOT0/nBOOT1, SWD pads, contiguous 8-bit port, depopulated HSE) | VERIFIED | Seven R1–R7 checkbox rows in §3, each with a `*Why:*`/`*Breaks if omitted:*` pair; `test_pcb_checklist_rows_are_wellformed[meta]`/`[fw]` re-run PASS; `_checklist_rows` parser enforces the shape structurally, not by eyeball |
| 3 | Flash-budget section cites the actual reserved addresses/sizes from Phase 126's linker symbols, incl. bootloader region and vector-relocation implication | VERIFIED (AMENDED wording, honestly disclosed) | §4 table transcribes `BOOTLOADER`/`FLASH`/`CONFIG`/`RAM` and `__config_*` symbols read directly from `platform/py32f071/linker/PY32F071xB_FLASH.ld` — independently confirmed by reading the linker script myself. The "no VTOR" premise in the *requirement's own wording* is independently confirmed FALSE (`__VTOR_PRESENT 1` in the CMSIS header genuinely absent from the pre-edit linker comment is a separate, correctly-corrected point). The record states the corrected migration-cost implication instead of a false one, and explicitly names Phase 130 CLOSE-01 as owner of amending the stale requirement/roadmap prose. This is an honest amendment, not a quiet redefinition — the substantive ask (a stated migration cost attached to the bootloader region) is discharged; only a factually wrong premise is corrected |
| 4 | A specific USB VID/PID decision replaces the undocumented placeholder, stating squatting becomes a liability at ship | VERIFIED (partial amendment, honestly disclosed) | §5 records pid.codes VID `0x1209`, interim `1209:0001`, and the exact `_L2_SHIP_GATE` sentence — present verbatim in both copies. The placeholder's provenance (Puya Semiconductor / `usbd_cdc_if.c` / `pycdc.inf`) is now recorded rather than left "undocumented," which is a strengthening of the requirement's claim, not a weakening; `usb_cdc.c` is deliberately unedited (D-06) with the obligation tracked in §8. Disposition is recorded, not hidden |
| 5 | Socket-empty-before-install instruction documented, with explicit reasoning why it is stronger here than the provisional-pin-map comparable | VERIFIED | §6 `[SHARED:S5]` verbatim in both copies plus `platform/py32f071/README.md` §"Hardware validation still required" pointer; `test_socket_empty_instruction_present[meta]`/`[fw]`/`[readme]` re-run PASS |

**Score:** 5/5 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.planning/v1.23-FLASH-PATH-DECISION.md` | Authoritative ADR-style record, 11 `## ` headings, 5 `[SHARED:Sn]` markers | VERIFIED | Read in full (288 lines); 11 top-level headings, 5 shared markers, `### Deliberately undecided` subsection, closing `## Claim ceiling` all present |
| `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md` | Firmware-repo subset, byte-identical shared bodies | VERIFIED | Read in full (143 lines); no numbered `## ` headings (subset convention), `## Claim ceiling` present, all 5 shared bodies textually identical to the meta record on direct comparison |
| `firestarter/tests/test_flash_path_record_sync.py` | 41-leg fail-closed + parity/content sync gate | VERIFIED | Re-run independently: `41 passed in 0.56s`. Read the full 1239-line source: needle-based content checks, non-vacuity guards (F-14/A-7 shape), planted-mutation test against the *real* artifact, subprocess-isolated absent-meta-root skip test, exact-clause forbidden-regex on the linker script — substantive, not hollow |
| `firestarter/tests/meta_presence.py` | Fail-closed meta-repo presence probe | VERIFIED | Read in full (134 lines); `.exists()`-based marker check, `MissingScanTargetError` raised (not returned/skipped) when the meta repo is present but a target is missing, one overridable seam (`FIRESTARTER_META_ROOT`) that never touches the marker name |
| `firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld` | Comment-only D-11 cross-reference, no region/symbol change | VERIFIED | `git show 5a89ee7 -- .../PY32F071xB_FLASH.ld` shows only comment-block text changed; grep for `ORIGIN|LENGTH|PROVIDE|ASSERT|_estack|_Min_` diff lines returns zero |
| `.planning/seeds/py32f071-no-external-tool-fw-install.md` | Status updated, points at new record, D-17 four-field schema intact | VERIFIED | Read in full; frontmatter is exactly `title`/`trigger_condition`/`planted_date`/`status`; status reads "partially realised..."; body links `../v1.23-FLASH-PATH-DECISION.md` and names `FUT-N05` |
| `.planning/phases/.../129-NONREGRESSION.md` | Closing re-execution record, criterion 3 AMENDED | VERIFIED | Read in full (498 lines); every locally-provable row independently re-executed by this verifier and matched |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `.planning/v1.23-FLASH-PATH-DECISION.md` §4 | `platform/py32f071/linker/PY32F071xB_FLASH.ld` | address/symbol citation | WIRED | All table values (`0x08000000`, `120K`, `0x0801E000`, `8K`, `__config_page_size`, `__config_slot_a_start`, `__config_slot_b_start`, `__config_region_end`, `0x08020000`) independently confirmed present, verbatim, in the linker script I read directly |
| Meta record §2–§6 | Firmware subset (same headings) | `test_shared_sections_match[S1..S5]` | WIRED | Re-run PASS for all five keys; independently spot-compared several sections by eye during the Read above — identical |
| `firestarter/CLAUDE.md` | Both record copies | five `[SHARED:Sn]` key names | WIRED | Confirmed both `[SHARED:S1]`…`[SHARED:S5]` lines present in `firestarter/CLAUDE.md`'s "PY32F071 Flash-Path and PCB Documentation" section |
| `platform/py32f071/README.md` | `FLASH-PATH-AND-PCB.md` | pointer + verbatim socket sentence | WIRED | Confirmed both the pointer text and `_L3_SOCKET_EMPTY` sentence present in README's "Hardware validation still required" section |
| Gate commits (`3393137`, `42395cf`) | Record content commits (`8515a59`, `8102d0f`) | git commit-timestamp order | WIRED (order proven, not just claimed) | Independently confirmed via `git log`: gate commits at 11:08/11:19 on 2026-08-02, meta record content commit `8515a59` at 11:29, firmware subset `8102d0f` at 11:53 — gate genuinely precedes both records |

### Data-Flow Trace (Level 4)

Not applicable — this phase produces static documentation and a gate, not a rendering/data-flow
pipeline. The equivalent check performed instead was tracing the linker-symbol citation chain
(§4 of the record → the real linker script), reported above under Key Link Verification.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full firmware suite passes at the claimed count | `python -m pytest tests/ -q -rs` (run once, in `/workspaces/firestarter`) | `221 passed in 6.88s` | PASS — matches 129-NONREGRESSION.md's claim exactly |
| Sync gate module passes at the claimed count | `python -m pytest tests/test_flash_path_record_sync.py -v` | `41 passed in 0.56s`, all 10 fail-closed legs + 31 parity/content legs individually green | PASS |
| Milestone claim gate passes on all 3 durable artifacts | `python3 .../check_permitted_claims.py <meta record> <fw subset> <129-NONREGRESSION.md>` | `PASS: ... 3 file(s) carry the required silicon caveat` exit 0 | PASS |
| Forbidden-overclaim phrases absent from durable artifacts | manual grep for the 6 forbidden phrases in REQUIREMENTS.md's Validation Ceiling | zero matches across all 3 files | PASS |
| Deviation re-check: locator-fix scope | `git show 2ef7b57 -- tests/test_flash_path_record_sync.py` | diff touches only the brace-detection loop (`memory_idx` added, condition changed); needle set, forbidden regex, non-vacuity assert untouched | PASS |
| Deviation re-check: pre-edit linker had the false clause and lacked all 4 needles | `git show 5a89ee7^:platform/py32f071/linker/PY32F071xB_FLASH.ld` grepped | 1 match for "no VTOR" (case-insensitive); 0 matches for each of the 4 needles | PASS — RED-preserving proof holds |
| Deviation re-check: `5a89ee7` is comment-only | `git show 5a89ee7 -- .../PY32F071xB_FLASH.ld \| grep -E '^[+-]' \| grep -E 'ORIGIN\|LENGTH\|PROVIDE\|ASSERT'` | zero lines | PASS |
| Meta gitlink and submodule HEAD match the claimed firmware HEAD | `git submodule status firestarter`, `git rev-parse HEAD` in firmware repo | both report `5a89ee76dc4681abe18db259e57bb92f519520f4` | PASS |
| No premature requirement tick before 129-09 | `git log --oneline -- .planning/REQUIREMENTS.md` | only `b62d5e1` ("close phase") touches the file within Phase 129 | PASS |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|--------------|----------------|--------------|--------|----------|
| PCB-01 | 129-01,02,03,06,08,09 | Three-tier flash path, non-retirement statement | SATISFIED | §2 `[SHARED:S1]`; `test_three_tiers_and_non_retirement` PASS both copies |
| PCB-02 | 129-01,02,04,06,09 | Distinct, checkable PCB requirement rows | SATISFIED | §3 R1–R7; `test_pcb_checklist_rows_are_wellformed` PASS both copies |
| PCB-03 | 129-01,02,03,04,06,07,09 | Flash budget cites actually-reserved addresses; vector-relocation implication | SATISFIED (honest AMENDED wording — see Truth 3) | §4; `test_flash_budget_cites_reserved_map` / `test_bootloader_figure_carries_its_cost` PASS both copies; independently confirmed against the linker script |
| PCB-04 | 129-01,02,05,06,09 | Real VID/PID decision replacing the undocumented placeholder | SATISFIED (honest partial-amendment wording — see Truth 4) | §5; `test_vid_pid_decision_and_ship_gate` PASS both copies |
| PCB-05 | 129-01,02,05,06,09 | Socket-empty install instruction, stronger-here reasoning | SATISFIED | §6; `test_socket_empty_instruction_present` PASS meta/fw/readme |

No orphaned requirements: `grep -E "Phase 129" .planning/REQUIREMENTS.md` maps only PCB-01…PCB-05
to this phase, and all five appear in at least one plan's `requirements:` frontmatter.

### Anti-Patterns Found

None. Scanned every file in this phase's declared change surface
(`.planning/v1.23-FLASH-PATH-DECISION.md`, `.planning/seeds/py32f071-no-external-tool-fw-install.md`,
`firestarter/CLAUDE.md`, `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md`,
`firestarter/platform/py32f071/README.md`, `firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld`,
`firestarter/tests/meta_presence.py`, `firestarter/tests/test_flash_path_record_sync.py`,
`.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`) for `TBD|FIXME|XXX`: zero unreferenced markers
introduced by this phase (the many `TBD` hits in `ROADMAP.md` are all pre-existing future-phase
placeholders unrelated to Phase 129's own change surface). No `TODO|HACK|PLACEHOLDER` /
"not yet implemented" / "coming soon" hits either (the word "placeholder" appears only in its
legitimate sense — describing the USB VID/PID or pin-map placeholders the record is *about*).
No forbidden-overclaim phrases from the milestone's own claim-gate phrase table anywhere in the
three durable artifacts (mechanically confirmed via `check_permitted_claims.py`, independently
re-run).

### Human Verification Required

None. This phase's substance — whether the gate genuinely predates its content, whether the 41
legs are substantive, whether the one authorized deviation holds, whether the durable artifacts
respect the honesty ceiling, and whether the five requirement ticks are earned — is entirely
checkable from the git history, the source of the gate module, and the text of the two record
copies. No runtime behavior, visual UI, or external service is involved (no PY32F071 hardware
exists, and the phase's own claim ceiling correctly states this).

### Gaps Summary

No gaps found. Every must-have re-verified independently against the live tree rather than
accepted from 129-NONREGRESSION.md's or the SUMMARYs' own narration:

- Git-timestamp order genuinely shows the sync gate (`3393137`/`42395cf`) committed before either
  record's content (`8515a59`/`8102d0f`) existed.
- The gate's 41 legs are substantive: needle-based content assertions, a non-vacuity guard applied
  before every comparison, a planted-mutation test run against the real artifact (not only a
  synthetic fixture), and ten fail-closed legs that were independently re-run and produce
  `MissingScanTargetError` (not a silent skip) when a scan target is missing under a present meta
  repo.
- The one authorized deviation (`2ef7b57`'s locator-only fix, RED-preserved by `5a89ee7^`'s genuine
  needle-miss and false clause) checks out on independent re-verification of all three legs of the
  proof: the locator diff is scoped to brace-detection only; the pre-edit linker content genuinely
  lacked all four needles and genuinely carried the false "no VTOR" clause; and `5a89ee7` itself
  changes no `ORIGIN`/`LENGTH`/`PROVIDE`/`ASSERT`/`_estack`/`_Min_` line.
- The durable artifacts stay inside the honesty ceiling: the milestone claim gate passes on
  independent re-run against all three named artifacts, and a manual grep for the six forbidden
  overclaim phrases from REQUIREMENTS.md's Validation Ceiling returns zero hits.
- PCB-01…PCB-05 are all ticked in REQUIREMENTS.md, all five are earned by content that exists on
  disk and is mechanically gated, and the two amended criteria (PCB-03 for the "no VTOR" wording,
  PCB-04 for the "undocumented" wording) are honestly disclosed as amendments — with Phase 130
  CLOSE-01 explicitly named as the owner of correcting the stale requirement/roadmap prose — rather
  than silently redefined to fit what shipped. Git history confirms no plan prior to 129-09 touched
  `REQUIREMENTS.md`.

---

_Verified: 2026-08-02_
_Verifier: Claude (gsd-verifier)_
