---
phase: 153-write-path-erase-policy
plan: 13
subsystem: docs
tags: [protocols-md, protocol-id, at28c, eeprom28c, flash4, erase-policy, dispatch-mirror]

# Dependency graph
requires:
  - phase: 153-07
    provides: "restored FLAG_CAN_ERASE for algorithm 13, CMD_ERASE dispatch arm landed in 153-03/04, corrected database.py comment"
provides:
  - "firestarter/doc/PROTOCOLS.md section 1.6 (0x0D) erase-model paragraph corrected: standalone CMD_ERASE arm, AN 0544B software six-byte erase, deliberately-unimplemented 12V hardware path, SDP-disable prefix, device-global scope, blank-check-skip flag now unread, software-proven-and-unvalidated honesty statement"
  - "firestarter/doc/PROTOCOLS.md section 1.1 (0x05) erase-model paragraph gained one sentence: write path performs no blank check either, bulk erase stays unadvertised for a hardware-hazard reason distinct from 0x0D's retired reason"
  - "firestarter_app/doc/protocol-id.md 0x0D row corrected: standalone software chip erase, FLAG_CAN_ERASE set for all 84 chips, honesty statement, extended cross-reference to PROTOCOLS.md section 1.6"
  - "ERASE-01, ERASE-02, ERASE-03 flipped to Complete in REQUIREMENTS.md — this plan was the last claimant of all three"
affects: [152-outward-facing-claims, phase-153-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "documentation-only correction of prose sites not covered by any parser or test, verified by explicit negative/positive grep criteria rather than a test suite"

key-files:
  created: []
  modified:
    - firestarter/doc/PROTOCOLS.md
    - firestarter_app/doc/protocol-id.md
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md

key-decisions:
  - "Added a new dedicated Citation line under the 0x0D erase-model paragraph naming both the AT28C256 datasheet's SDP section and the Atmel Application Note 0544B-10/98. The plan's read_first instruction assumed an existing citation line directly under that paragraph; there was none in the file (only the write-algorithm and VPP paragraphs had their own Citation lines) — a new one was added rather than extending a nonexistent one, satisfying the same intent (naming the application note)."
  - "Left the whole-file pipe-field-count check as a two-value result ({5, 7}) in protocol-id.md: the file legitimately contains two differently-shaped tables (5-column in-scope table, 3-column excluded-IDs table), pre-existing before this edit. Verified the corrected row's own table (lines 17-27) is internally uniform at 7 fields, matching every sibling row."

patterns-established: []

requirements-completed: [ERASE-01, ERASE-02, ERASE-03]

coverage:
  - id: D1
    description: "firestarter/doc/PROTOCOLS.md §1.6 (0x0D) no longer states the firmware implements no erase operation, no longer recommends the blank-check-skip flag as required to write a non-blank part, and states the erase is software-proven and unvalidated on silicon"
    requirement: "ERASE-01"
    verification:
      - kind: other
        ref: "grep -c 'no erase operation at all' doc/PROTOCOLS.md == 0"
        status: pass
      - kind: other
        ref: "grep -c 'is \\*\\*required\\*\\* to write a non-blank' doc/PROTOCOLS.md == 0"
        status: pass
      - kind: other
        ref: "grep -c 'software-proven and unvalidated on silicon' doc/PROTOCOLS.md >= 1"
        status: pass
    human_judgment: false
  - id: D2
    description: "firestarter/doc/PROTOCOLS.md §1.1 (0x05) gained the write-path-no-blank-check sentence, consistent with the algorithm-13 correction but keeping algorithm 5's distinct hardware-hazard exclusion"
    requirement: "ERASE-02"
    verification:
      - kind: other
        ref: "git diff --numstat -- doc/PROTOCOLS.md (confined to the two subsections)"
        status: pass
    human_judgment: false
  - id: D3
    description: "firestarter_app/doc/protocol-id.md 0x0D row no longer claims the family has no erase capability, cites Phase 153/ERASE-03, and carries the honesty statement"
    requirement: "ERASE-03"
    verification:
      - kind: other
        ref: "grep -c 'no erase operation' doc/protocol-id.md == 0; grep -cE 'ERASE-03|Phase 153' doc/protocol-id.md >= 1"
        status: pass
    human_judgment: false
  - id: D4
    description: "Section-0 dispatch table and dispatch-mirror three-way bind unaffected by the prose edits"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_dispatch_mirror.py — 2 passed"
        status: pass
      - kind: other
        ref: "firestarter_app/tools/check_dispatch.py — exit 0"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-08-21
status: complete
---

# Phase 153 Plan 13: Correct the two erase-capability prose claim sites Summary

**Rewrote `PROTOCOLS.md` §1.6's (0x0D) erase-model paragraph to describe the shipped `CMD_ERASE` standalone software chip erase and remove the "`-b` is required" recommendation, added a parallel sentence to §1.1 (0x05), and corrected `protocol-id.md`'s 0x0D row — the two documents that were the last false claim sites for ERASE-01/02/03.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-08-21T10:15Z (approx)
- **Completed:** 2026-08-21T10:29Z
- **Tasks:** 2/2
- **Files modified:** 4 (2 sub-repo docs + REQUIREMENTS.md + ROADMAP.md)

## Accomplishments

- `firestarter/doc/PROTOCOLS.md` §1.6 (0x0D): replaced the "no erase operation at all" / "flag is required" paragraph with a corrected one naming the standalone `CMD_ERASE` arm, the Atmel AN 0544B software six-byte chip erase (20 ms `t_EC`, SDP left enabled afterward), the deliberately-unimplemented 12 V hardware Chip Erase mode (D-153-03), the SDP-disable prefix rationale (D-153-02), the device-global scope and `erase --blank-check`/`--sector-address` no-ops (D-153-04), the now-set `FLAG_CAN_ERASE` for all 84 chips, and the verbatim honesty statement — "software-proven and unvalidated on silicon." Added a dedicated citation line naming both the datasheet and the application note.
- `firestarter/doc/PROTOCOLS.md` §1.1 (0x05): added one sentence to the erase-model paragraph stating the write path performs no blank check either (same per-page auto-erase reason), while keeping algorithm 5's capability-gated bulk erase unadvertised for its own distinct hardware-hazard reason (12 V routed onto a 5V-only part) — explicitly not conflated with algorithm 13's retired reason.
- `firestarter_app/doc/protocol-id.md`: corrected the 0x0D row's description cell to state the family has a standalone software chip erase as of Phase 153 (ERASE-03/ERASE-04), that the host sets `FLAG_CAN_ERASE` for all 84 chips, the honesty statement, and extended the PROTOCOLS.md cross-reference to cover the erase model as well as the SDP model. Whole file searched; no other "no erase" variant found outside this one row.
- Section-0 dispatch table (PROTOCOLS.md) and the host in-scope table's own field-count uniformity confirmed unchanged/uniform; `test_dispatch_mirror.py` and `check_dispatch.py` both still pass.
- Flipped ERASE-01, ERASE-02, and ERASE-03 to Complete in `.planning/REQUIREMENTS.md` (this plan was the declared last claimant of all three) and checked off `153-13-PLAN.md` in `.planning/ROADMAP.md`'s phase-153 plan list.
- Confirmed host suite fully green (1825 passed, matching the inherited state — no regression from doc-only edits), and CI-scoped `ruff check firestarter/ tests/`, `ruff format --check firestarter/ tests/`, and `tools/check_mypy_watermark.py` (35==35, zero headroom) all pass.
- `git diff --quiet -- tools/check_dispatch.py` holds; `firestarter/scripts/check_erase_no_vpp.py` still passes.

## Task Commits

1. **Task 1: Rewrite the 0x0D erase-model paragraph in PROTOCOLS.md, add the 0x05 write-path sentence** - `21a02c3` (docs, firestarter repo)
2. **Task 2: Correct the 0x0D row in protocol-id.md** - `5e9ca60` (docs, firestarter_app repo)

**Plan metadata:** (this commit) — meta-repo docs commit with SUMMARY.md, REQUIREMENTS.md, ROADMAP.md, STATE.md

## Files Created/Modified

- `firestarter/doc/PROTOCOLS.md` - corrected §1.6 (0x0D) erase-model paragraph + new citation line; added one sentence to §1.1 (0x05) erase-model paragraph
- `firestarter_app/doc/protocol-id.md` - corrected 0x0D row's description cell
- `.planning/REQUIREMENTS.md` - flipped ERASE-01/02/03 to Complete, with per-requirement evidence notes; updated traceability table status column
- `.planning/ROADMAP.md` - checked off `153-13-PLAN.md` in the phase-153 plan checklist

## Per-Site Table

| Site | Already fixed by an earlier plan? | What this plan changed |
|---|---|---|
| `firestarter/doc/PROTOCOLS.md:305` §1.6 (0x0D erase-model, incl. "`-b` is required") | No — flagged explicitly as the highest-value site, untouched by any prior plan | Rewrote the entire paragraph; removed the required-flag recommendation; added the honesty statement and a dedicated citation line |
| `firestarter/doc/PROTOCOLS.md` §1.1 (0x05 erase-model) | No — not previously touched | Appended one sentence: no blank check on the write path either; bulk erase stays unadvertised for a distinct hardware-hazard reason |
| `firestarter_app/doc/protocol-id.md:22` (0x0D row) | No — untouched by prior plans | Rewrote the erase clause in the description cell; added honesty statement; extended cross-reference |
| `firestarter_app/firestarter/cli_handlers.py:797-804` | Yes — corrected in `153-11` (the `--skip-erase` warning no longer claims "no erase operation at all"; verified by grep in this plan's `--read_first` pass, no residual claim found) | None needed — verified current, not re-touched |
| `firestarter_app/firestarter/chip_test.py:307,745-750` | Yes — corrected in `153-10` (reason texts rewritten; `_PROTOCOL_EEPROM_28C` kept as a defensive fallthrough with a reachability leg) | None needed — verified current, not re-touched |
| `firestarter/CLAUDE.md` (protocol table + "Protocol 0x0D notes") | Yes — corrected in `153-03` per plan frontmatter's flag; confirmed no lingering "has no erase operation at all" text during this plan's read pass | None needed — verified current, not re-touched |

No sixth site was found during this plan's execution.

## Decisions Made

- **Citation-line handling for the 0x0D erase-model paragraph:** the plan's `read_first` instruction described an "existing citation line under the paragraph" to extend. On inspection, no such line existed (only the write-algorithm and VPP paragraphs in this subsection carry their own `Citation:` lines) — the erase-model paragraph previously had none. Added a new dedicated citation line naming both the AT28C256 datasheet's SDP section and the Atmel Application Note *Software Chip Erase*, Rev. 0544B-10/98, satisfying the plan's underlying intent (naming the application note alongside the datasheet reference) without fabricating a prior citation that didn't exist.
- **protocol-id.md field-count check:** the plan's acceptance criterion ("a single value") assumes one table per file. The file has two tables of different shapes (5-column in-scope table, 3-column excluded-IDs table) — pre-existing, not introduced here. Verified the corrected row's uniformity within its own table (7 pipe-delimited fields, matching every other row in the in-scope table) rather than across the whole file.
- **ERASE-01/02/03 flip:** confirmed via frontmatter cross-check across all 13 prior plans that this plan (153-13) is the sole remaining claimant for all three requirements, and that both the code and documentation halves are now satisfied (code: `153-02`, `153-03/04`, `153-06`, `153-07`; docs: this plan). Flipped all three to Complete with per-requirement evidence quoted inline in REQUIREMENTS.md.
- **ROADMAP.md's requirements-traceability table (ERASE-01…09, currently all "Pending")** was deliberately left untouched — `153-16-PLAN.md`'s own scope statement names "the D-15 PROJECT.md/ROADMAP corrections + the full phase gate" as the closing plan's job, and this table is not synchronized per-plan elsewhere in the phase (ERASE-04/05/06/07 are already Complete in REQUIREMENTS.md but still show Pending in this ROADMAP table) — correcting it here would be inconsistent with the established pattern and out of this plan's stated scope.

## Deviations from Plan

None — plan executed exactly as written. The two items above (citation-line handling, field-count check) are documentation judgment calls within the plan's stated intent, not deviations from required behavior; no code was touched and no Rule 1-4 deviation applied.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- ERASE-01, ERASE-02, and ERASE-03 are now Complete — the two prose sites that had been holding them `In Progress`/`Pending` are corrected and gated by explicit grep criteria.
- `0x0D` stays `UNVERIFIED`; no `support_status` field was touched; gh#21/#32/#11/#12 remain open. Neither document claims the write path or the erase is validated on silicon — both carry the verbatim "software-proven and unvalidated on silicon" phrase.
- Remaining phase-153 plans (14, 15, 16) are unaffected by this plan's doc-only scope: 14 (ERASE-08 size measurement), 15 (tripwire fixture severance), 16 (ERASE-09 phase record + PROJECT.md/ROADMAP D-15 corrections + full phase gate) can proceed as planned.
- Host suite remains fully green (1825/1825); both native environments were not rebuilt (no firmware source file was touched by this plan — only `doc/PROTOCOLS.md`), consistent with the inherited green state.

## Self-Check: PASSED

---
*Phase: 153-write-path-erase-policy*
*Completed: 2026-08-21*
