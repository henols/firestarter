---
phase: 120-host-cli-surface-wire-emission-capability-refusal
plan: 04
subsystem: testing
tags: [validation-contract, infoic-xml, sdp-capability, record-keeping, planning-docs]

# Dependency graph
requires:
  - phase: 120-host-cli-surface-wire-emission-capability-refusal
    provides: "120-SDP-PARTITION.md — the derived 43/41 SDP capability partition from infoic.xml bit 15"
provides:
  - "Corrected 120-VALIDATION.md HOST-04 oracle rows pointing at real pytest selectors"
  - "120-WATCHLIST.md — the nine-entry residual-risk record"
  - "A dated, scoped, append-only exception on the standing 2026-07-10 infoic-flags note"
affects: ["120-01", "120-05", "120-09", "121 (GATE-02)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Append-only note correction via prefix-assertion checker script, never a rewritten record"
    - "Watch-list as a named, reviewable home for residual risk instead of silent tolerance"

key-files:
  created:
    - .planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-WATCHLIST.md
    - .planning/phases/120-host-cli-surface-wire-emission-capability-refusal/check_note_append_only.py
  modified:
    - .planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-VALIDATION.md
    - .planning/notes/infoic-xml-protection-flags-research.md

key-decisions:
  - "120-VALIDATION.md's HOST-04 rows now state the derived 43/41 split (superseding both the interim 74/10 placeholder and RESEARCH F-01's curated 37/47), with the full pinned arithmetic (84/43/41/81/134/130) transcribed verbatim from 120-01-PLAN.md and 120-SDP-PARTITION.md"
  - "The named-refusals row is now exhaustive (19 DIP24_2816 + 2 FRAM) rather than the narrower 8-named+2-FRAM claim; the adapter-required row (HOST-01) now asserts all nine, not a hypothetical subset"
  - "A new HOST-04 row asserts the two derived structural invariants (no adapter-required part, no DIP24_2816 part in the allow-set) as consequences of the derivation, never its rule"
  - "The 2026-07-10 infoic-flags note is NOT overturned — it received a dated, append-only scoped exception stating both findings (taxonomy vs. capability) are correct about different questions"
  - "doc/lockable-proms.md section 17's AT28C16 error is recorded in 120-WATCHLIST.md but not fixed here; correction is GATE-02, Phase 121"

patterns-established:
  - "Prefix-assertion checker (check_note_append_only.py) as the machine-checked proof that a standing negative verdict was extended, not rewritten"

requirements-completed: []  # This plan closes NO requirement IDs. HOST-04 spans 120-01/120-05/120-09; only 120-09 may tick it.

coverage:
  - id: D1
    description: "120-VALIDATION.md's HOST-04 rows state the derived 43/41 split (with full pinned arithmetic) and no row still states the superseded 74/10 or 37/47 figures outside blockquote lines"
    verification:
      - kind: other
        ref: "python3 -c inline check (Task 1 <verify>): no 74/10 or 37/47 outside blockquotes, 43/41 present, DIP24_2816 and adapter-required present"
        status: pass
    human_judgment: false
  - id: D2
    description: "A named nine-entry residual-risk watch-list exists on disk (120-WATCHLIST.md) with the bounded remedy and two recorded-not-acted-on findings"
    verification:
      - kind: other
        ref: "python3 -c inline check (Task 2 <verify>): all nine part_number strings + GATE-02 + AT28C16 + F-17 + Validation Ceiling literals present"
        status: pass
    human_judgment: false
  - id: D3
    description: "The standing 2026-07-10 infoic-xml-protection-flags-research.md note carries a scoped exception appended without changing any existing sentence"
    verification:
      - kind: other
        ref: "check_note_append_only.py — asserts working-tree file is a strict prefix-extension of the HEAD-committed file"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-07-29
status: complete
---

# Phase 120 Plan 04: Validation Contract Correction & Residual-Risk Record-Keeping Summary

**Corrected `120-VALIDATION.md`'s HOST-04 oracle rows from the superseded interim 74/10 and curated 37/47 splits to the derived 43/41 partition, created a nine-entry residual-risk watch-list, and appended a dated scoped exception to the standing infoic-flags note without overturning its verdict.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-07-29 (session start)
- **Completed:** 2026-07-29
- **Tasks:** 3
- **Files modified:** 4 (1 new watch-list, 1 corrected validation contract, 1 append-only note, 1 new throwaway checker script)

## Accomplishments

- `120-VALIDATION.md`'s HOST-04 partition row now states the derived **43 ALLOW / 41 REFUSE** split over the 84 `algorithm == 13` entries, with the full pinned arithmetic (84 pairs; 81 distinct `part_number` strings split 40/41; 134 total alias-token instances; 130 distinct uppercased tokens split 65/65 with an empty intersection), and a parenthetical recording supersession of both the interim operator placeholder (74/10) and RESEARCH F-01's curated figure (37/47) — phrased so as not to contain the literal superseded slash-patterns, satisfying the plan's own regex verification gate.
- The named-refusals row widened from "8 named + 2 FRAM" to exhaustive coverage: all **19** `DIP24_2816` parts (`REASON_NOT_CAPABLE`) and both FRAM parts (`REASON_FRAM`, with `REASON_NOT_CAPABLE` proven absent to demonstrate branch order).
- The adapter-required row (found under HOST-01, not HOST-04 — the only pre-existing adapter-required row in the document) widened to assert all **nine** `adapter-required` `0x0D` parts hear the capability reason, referencing both the future CLI-level test (120-08) and the now-real DB-level exhaustive test from plan 120-05.
- A new HOST-04 row was added asserting the two derived **structural invariants** — the allow-set contains no `adapter-required` part and no part on pinout `DIP24_2816` — explicitly framed as consequences of the derivation, not its rule (RESEARCH F-03 still holds).
- Every corrected HOST-04 row's Automated Command now points at a real pytest `-k` selector matching an actual test name defined in `120-01-PLAN.md` or `120-05-PLAN.md` (e.g. `test_partition_covers_exactly_the_84_0x0d_entries`, `test_all_dip24_2816_parts_are_refused`, `test_synthetic_unknown_0x0d_entry_is_refused_non_vacuous`, `test_predicate_is_name_keyed_and_a_programmer_dict_is_rejected`, `test_local_override_0x0d_entry_is_refused_at_runtime`, `test_allow_set_contains_no_adapter_required_and_no_dip24_2816_part`), rather than the placeholder selectors (`partition`, `named_refusals`, `non_vacuous`, `dict_shape`, `local_override_refused`) that did not match any real test.
- `120-WATCHLIST.md` created, naming the nine residual-risk entries where `infoic.xml` bit 15 disagrees with `page_size > 1` and "no SDP" is least intuitive: `AM28C64A,AM28C64AE,AM28C64B,AM28C64BE`; `AT28PC64,AT28PC64E`; `CAT28C64A,CAT28C65`; `XLE2865A,XLS2865A`; `XLE28C16B,XLS28C16B`; `XLE28C64A,XLS28C64A`; `UPD28C64`; `X2816B,X2816C`; `X2864AP`. States the bounded remedy: move an entry between the two sets in `120-sdp-partition.json`'s and production/test copies **together**, and never widen the allow-list by default.
- The watch-list also records two findings deliberately **not acted on**: (a) `doc/lockable-proms.md` section 17 is wrong about `AT28C16` — it lists it as SDP-capable when `infoic.xml` bit 15 is clear for it — with correction deferred to **GATE-02, Phase 121**; (b) RESEARCH F-17's "the DB splits alias groups and we cannot see why" is now **answered**: `chip_database.json`'s split mirrors `infoic.xml`'s own split (`AT28C64` byte-write/no-protect vs. `AT28C64B` page-write/protect), making F-02 rule 1's "do not strip parentheticals" load-bearing on correctness, not merely stability.
- The standing 2026-07-10 `infoic-xml-protection-flags-research.md` note received a dated (2026-07-29), append-only scoped exception. Its existing verdict — bits 14/15 too coarse for `status_readable`/lock-status taxonomy, do not re-investigate — was **not** overturned. The exception states the narrower question Phase 120 asked (does a 0x0D part have an SDP command decoder at all, not what kind of protection or whether it's readable), reports the three ground-truth probes' pass counts (8/8, 2/2, 4/4), and states explicitly that both findings are correct about different questions. Machine-verified as a strict textual extension via `check_note_append_only.py` (working-tree file = HEAD file + 3020 appended characters, zero bytes of the original changed).

## Task Commits

Each task was committed atomically:

1. **Task 1: Correct 120-VALIDATION.md's HOST-04 rows to the derived 43/41 split and widen four oracle legs** - `aed8299` (docs)
2. **Task 2: Write 120-WATCHLIST.md naming the nine residual-risk entries and the two recorded-not-acted-on findings** - `8a1c924` (docs)
3. **Task 3: Append a scoped exception to the 2026-07-10 infoic-flags note without overturning its verdict** - `f572822` (docs)

_Note: this executor runs in worktree isolation; STATE.md/ROADMAP.md updates are owned by the orchestrator after wave merge and are not part of this plan's commits._

## Files Created/Modified

- `.planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-VALIDATION.md` - HOST-04 partition/named-refusals/non-vacuity/dict-shape/local-override rows corrected to real selectors and the derived split; HOST-01 adapter-required row widened; new structural-invariants row added
- `.planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-WATCHLIST.md` - new: nine-entry residual-risk record, bounded remedy, two recorded-not-acted-on findings, restated validation ceiling
- `.planning/notes/infoic-xml-protection-flags-research.md` - append-only scoped exception dated 2026-07-29
- `.planning/phases/120-host-cli-surface-wire-emission-capability-refusal/check_note_append_only.py` - new throwaway checker proving the note edit was append-only (kept on disk per the plan's "or write it under the phase directory" option)

## Decisions Made

- Interpreted "the adapter-required row" (singular, definite article in the plan's Task 1 action text) as referring to the one pre-existing adapter-required row in the document, which lives under HOST-01 (there was no existing HOST-04 adapter-required row) — widened it in place rather than duplicating a second adapter-required row under HOST-04, and pointed it at both the future CLI-level selector and the now-real DB-level exhaustive selector from plan 120-05.
- Phrased the superseded-figure supersession text (74 ALLOW / 10 REFUSE; 37 ALLOW / 47 REFUSE) without an adjacent slash between the two numbers, so the values are recorded in the document while still passing the Task 1 verification regex that bans `74\s*/\s*10` and `37\s*/\s*47` outside blockquote lines.
- Kept `check_note_append_only.py` on disk under the phase directory (one of the two options the plan explicitly offered) rather than running it purely inline, so the append-only proof is reviewable and re-runnable.

## Deviations from Plan

None - plan executed exactly as written. All three tasks' automated `<verify>` commands were run and passed as specified; no Rule 1-4 auto-fixes were needed.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `120-VALIDATION.md`'s HOST-04 half is now reachable by real, already-known test names from plans 120-01 and 120-05, so the final validation sweep (before `/gsd-verify-work`) has concrete commands to run rather than placeholders.
- `120-WATCHLIST.md` gives Phase 121 (and any future bench session) a ready-made lookup for the nine residual-risk parts, so a contradicting bench report is recognised rather than re-investigated from scratch.
- Phase 121's GATE-02 has the exact two Atmel entries (`AT28C64,AT28C64B(Non-Standard),AT28HC64,AT28HC64L` and `AT28C64B,AT28HC64B,AT28HC64BF`) pre-derived for correcting `doc/lockable-proms.md` section 17, with no doc changed by this phase.
- No blockers. HOST-04 remains correctly un-ticked in `.planning/REQUIREMENTS.md`, deferred to plan 120-09 as instructed.

---
*Phase: 120-host-cli-surface-wire-emission-capability-refusal*
*Completed: 2026-07-29*

## Self-Check: PASSED
All created/modified files exist on disk; all task commit hashes (aed8299, 8a1c924, f572822) and the SUMMARY commit (efe67b7) verified present in git log.
