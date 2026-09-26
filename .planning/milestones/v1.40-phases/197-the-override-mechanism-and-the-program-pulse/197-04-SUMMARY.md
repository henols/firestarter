---
phase: 197-the-override-mechanism-and-the-program-pulse
plan: 04
subsystem: database-generator
tags: [python, build_db, chip_database, at28c, fm1608, fram-sram, gh-70]

# Dependency graph
requires:
  - phase: 197-03
    provides: "The hardened datasheet-override loader (five OVR-04 fail-closed legs, 18 unit tests) and NMOS_TRUE_VPP_MV fully evacuated as six override entries; the single _chip_aliases derivation per row already reused by apply_datasheet_override"
provides:
  - "_AT28C_DIP24_NAMES and its consuming arm deleted from tools/build_db.py; the hardware-damage guard (build_db.py's pin_count==24/proto_id/flags&0x10 check) is now the sole writer of unsupported_reason on the nine affected rows, byte-unchanged against 70c92ce"
  - "_ETYPE_RELABEL deleted from tools/build_db.py; RAMTRON/FM1608 now reads electrical.type=SRAM and electrical.vcc_mv=5000 (up from 3300), consistent with its four Ramtron siblings"
  - ".planning/notes/197-at28c-guard-evidence-for-phase-199.md: the measured 19-row pinout/flags table, the operator ruling, and the three test legs Phase 199 must rewrite together if it narrows the guard"
affects: [199]

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
# Multi-repo plan: gsd_run query commit disabled for this project per its standing note
# (has twice self-created a stray gsd/v1.40-... branch); commits measured by hand per
# repo, following the 197-01/02/03 precedent.
actuals:
  tokens: 6181
  tasks: 3
  commits: 5
  commits_by_repo:
    firestarter_app: 2
    meta: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Deletion, not migration, for a hardcode whose selection work is already done by another mechanism: measuring that a name list and a guard select the identical row set (same flags bit, zero exceptions) is what makes deleting the list, rather than moving it, correct — D-05's 'only decoded values may be overridden' forced this distinction rather than a default third home in the override file."
    - "A relabel deletion pinned on BOTH fields it moves, not just the one named in the decision: FM1608's electrical.vcc_mv had no assertion anywhere in the suite before this plan, even though D-08 predicted only electrical.type would change. The new assertion exists precisely so a future regression restoring 3300 is caught."

key-files:
  created:
    - .planning/notes/197-at28c-guard-evidence-for-phase-199.md
  modified:
    - firestarter_app/tools/build_db.py
    - firestarter_app/tests/test_build_db_inclusion.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr
    - firestarter_app/firestarter/data/chip_database.json
    - .planning/REQUIREMENTS.md

key-decisions:
  - "OVR-05 marked Complete in REQUIREMENTS.md (shared-ID gate, #2388): 197-03 already finished and left it Pending because 197-04 (this plan) also declares it in frontmatter; both declaring plans have now finished, so the checkbox and traceability-table row are flipped by hand (per this project's standing note that the requirements/roadmap verbs reformat the whole file), touching only those two lines."
  - "ROADMAP.md is NOT edited by this executor, per the orchestrator's explicit roadmap-edit exception for this plan's Task 3. The note the task asked to file is written in full and owned by this plan; the exact pointer text and anchor line for the orchestrator to apply are recorded below under '## ROADMAP pointer for the orchestrator to apply'."
  - "Task 1's alias-set derivation ambiguity resolved in favor of keeping the single _chip_aliases comprehension: it is not, in fact, consumed only by the deleted AT28C arm — it is already reused by apply_datasheet_override (wired in by plan 197-02/03) two lines later in execution order. Removing it would have broken the override mechanism. Only the AT28C-specific consumer (the arm and its name list) was deleted."
  - "test_at28c16_named_arm_reason_mentions_adapter_doc keeps its original function name despite the 'named arm' it tested no longer existing, per the plan's own artifact tracking, which names this exact test as the one being rewritten in place rather than renamed."

requirements-completed: [OVR-05]

coverage:
  - id: D1
    description: "_AT28C_DIP24_NAMES and its consuming arm deleted from tools/build_db.py; the hardware-damage guard, left byte-unchanged, is now the sole writer of unsupported_reason on the nine adapter-required DIP24 rows (guard's own 'socket pin 21 = WE' wording, no wiki-page reference); zero rows flip to supported"
    requirement: OVR-05
    verification:
      - kind: unit
        ref: "tests/test_build_db_inclusion.py::TestUnsupportedReasonStrings::test_at28c16_named_arm_reason_mentions_adapter_doc (rewritten to pin guard wording)"
        status: pass
      - kind: other
        ref: "python -c '...' asserting exactly 9 adapter-required rows, all reasons start with 'adapter required:' and contain 'socket pin 21 = WE', none mentions 'wiki' -> GUARD_TEXT_OK"
        status: pass
      - kind: other
        ref: "git diff 70c92ce -- tools/build_db.py | grep -E '^[-+].*(pin_count == 24|flags & 0x10|hardware-damage path)' -> empty (guard byte-unchanged)"
        status: pass
      - kind: other
        ref: "git diff 70c92ce --name-only -- tests/test_sdp_capability.py tests/test_chip_resolver.py tests/test_sdp_honesty.py -> empty (all three stay green, unmodified)"
        status: pass
      - kind: unit
        ref: "pytest tests/test_build_db_inclusion.py tests/test_sdp_capability.py tests/test_chip_resolver.py tests/test_sdp_honesty.py tests/test_chip_database_field_inventory.py -> 67 passed"
        status: pass
    human_judgment: false
  - id: D2
    description: "_ETYPE_RELABEL deleted from tools/build_db.py; RAMTRON/FM1608 changes two fields (electrical.type FRAM->SRAM, electrical.vcc_mv 3300->5000), both pinned by new/updated assertions; test_characterization.ambr re-recorded with exactly one line changed"
    requirement: OVR-05
    verification:
      - kind: unit
        ref: "tests/test_build_db_inclusion.py::TestVariantDecodeClassification::test_fm1608_resolves_sram_std (rewritten: SRAM + new vcc_mv==5000 assertion)"
        status: pass
      - kind: other
        ref: "python -c '...' asserting FM1608 row: type=SRAM, vcc_mv=5000, algorithm=40, pinout=DIP28_JEDEC_SRAM_8K -> FM1608_OK"
        status: pass
      - kind: other
        ref: "git diff 70c92ce --numstat -- tests/__snapshots__/test_characterization.ambr -> 1 insertion, 1 deletion (exactly one line)"
        status: pass
      - kind: other
        ref: "git diff 70c92ce --name-only -- tests/test_database_conversion.py tests/test_ic_layout.py tests/test_diagnostic_report.py -> empty (all three stay green)"
        status: pass
      - kind: unit
        ref: "pytest tests/ -o addopts='' -q -rf -> 2 failed, 2053 passed; both FAILED lines name tests/test_wire_dict_equivalence.py and no other module"
        status: pass
    human_judgment: false
  - id: D3
    description: ".planning/notes/197-at28c-guard-evidence-for-phase-199.md written: reproducible method, full 19-row table, per-fact disposition, operator ruling verbatim, named honesty limit, and the three test legs Phase 199 must decide about"
    requirement: OVR-05
    verification:
      - kind: other
        ref: "grep -c '^|' .planning/notes/197-at28c-guard-evidence-for-phase-199.md -> 21 (>= 21 required)"
        status: pass
      - kind: other
        ref: "grep -qF for DIP24_2816, DIP24_2716, rw-pin, 'flags & 0x10', a8efaedc, 'Phase 199' -> all found"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-09-18
status: complete
---

# Phase 197 Plan 04: The override mechanism and the program pulse Summary

**Deleted the two remaining part-specific hardcodes from `build_db.py` (`_AT28C_DIP24_NAMES`, `_ETYPE_RELABEL`) as defects rather than migrating them, leaving the hardware-damage guard byte-unchanged and filing the guard-narrowing evidence Phase 199 inherits.**

## Performance

- **Duration:** ~50 min
- **Started:** 2026-09-18
- **Completed:** 2026-09-18
- **Tasks:** 3 (two `type="auto" tdd="true"`, one `type="auto"`)
- **Files modified:** 5 (2 generator/test files in Task 1, 3 generator/test/snapshot files in Task 2, 1 new note + REQUIREMENTS.md in Task 3), plus 1 gitlink

## Accomplishments

- **Task 1 — AT28C DIP24 name list deleted, guard is sole writer:**
  - Removed the 14-name `_AT28C_DIP24_NAMES` set literal, the two-branch arm that intersected it with the row's aliases, and the 12-line comment block entirely about that arm. Kept the single `_chip_aliases` derivation — measured to be already reused by `apply_datasheet_override` (wired in by plan 197-02/03) two statements later, not, as the plan flagged as a possibility, consumed only by the deleted arm.
  - Left the hardware-damage guard (`pin_count == 24 and proto_id in (0x07, 0x08, 0x0B) and (flags & 0x10)`) completely untouched — verified byte-identical against `70c92ce` by a diff check on its condition and reason-string text.
  - Regeneration measured: exactly 9 rows carry `support_status: adapter-required` (unchanged count), all with reasons starting `adapter required:` and containing `socket pin 21 = WE`, none mentioning a wiki page. **Zero rows flipped to `supported`** — matching D-15's correction of D-07's originally-claimed effect.
  - `tests/test_sdp_capability.py`, `tests/test_chip_resolver.py`, `tests/test_sdp_honesty.py` show zero diff against `70c92ce` — all three predicted-green by D-18 stayed green.
  - Rewrote `test_at28c16_named_arm_reason_mentions_adapter_doc` to pin the guard's own wording (`socket pin 21 = WE`, no wiki reference) instead of the retired named-arm text; its docstring's third property, which asserted the guard wording was ABSENT, is rewritten to state the new truth (it is now the ONLY wording present).
- **Task 2 — FM1608 relabel deleted, both moved fields pinned:**
  - Removed the single-entry `_ETYPE_RELABEL = {"FM1608": "FRAM"}` map, its alias-set comprehension (`part_aliases_set`, a duplicate of a pattern used three other places in the file), its loop, and the 6-line orphaned comment block whose `SST39SF040` clause warned against widening a map that no longer exists.
  - Regeneration measured: `RAMTRON/FM1608` now reads `electrical.type: SRAM`, `electrical.vcc_mv: 5000` (up from 3300 — the FRAM label had been bypassing the SRAM single-rail rewrite at the `if _etype == "SRAM":` block), `programming.algorithm: 40` and `pinout: DIP28_JEDEC_SRAM_8K` unchanged — matching D-17's corrected two-field effect exactly.
  - `test_fm1608_resolves_sram_std` rewritten: asserts `SRAM` instead of `FRAM`, plus a **new** `electrical.vcc_mv == 5000` assertion — `vcc_mv` had no pin anywhere in the suite before this commit. Class docstring updated to state both facts.
  - Re-recorded `tests/__snapshots__/test_characterization.ambr` with `pytest --snapshot-update` on Python 3.11: exactly one line changed (line 1001, FM1608's `FRAM` → `SRAM` column) — confirmed via `git diff --numstat` summing to 2 (1 insertion + 1 deletion).
  - `tests/test_database_conversion.py`, `tests/test_ic_layout.py`, `tests/test_diagnostic_report.py` show zero diff against `70c92ce` — all three predicted-green by D-18 stayed green.
  - Full Python 3.11 suite: **2 failed, 2053 passed** — both failures are the known-red `tests/test_wire_dict_equivalence.py` tests this plan's known-red window explicitly leaves for `197-06` to close; the changed-record count in `test_exactly_84_records_change_flags_and_no_other_field_moves` moved from 85 (197-03's baseline) to 85 (this run — the AT28C reason-string swaps and FM1608's `electrical.type`/`vcc_mv` are not surfaced fields in that test's wire-dict comparison at the count assertion's granularity); no other module regressed.
- **Task 3 — Phase 199 evidence filed:**
  - Wrote `.planning/notes/197-at28c-guard-evidence-for-phase-199.md` in full: the reproducible query method against the pinned `infoic.xml` (commit `a8efaedc`), the complete 19-row table (upstream `protocol_id`, `flags`, `flags & 0x10`, and deleted-list membership — the split is exactly the erasable bit, zero exceptions), three per-fact dispositions (name-list/guard identical selection, the `DIP24_2816` vs `DIP24_2716` pinout mismatch in the guard's own comment, and `classify()`'s re-promotion making the guard's dispatch-side effect moot for these rows), the operator ruling verbatim, a named honesty limit (pinout/flags analysis, not a bench measurement — no AT28C part written on any shield revision), and the three test legs (`test_sdp_capability.py`, `test_chip_resolver.py:87`, and this plan's rewritten `test_at28c16_named_arm_reason_mentions_adapter_doc`) that redden together the moment Phase 199 narrows the guard.
  - Per the orchestrator's roadmap-edit exception for this plan, **ROADMAP.md was NOT edited by this executor.** The exact pointer text and anchor line are recorded below for the orchestrator to apply as the single writer of that file this phase.
  - `REQUIREMENTS.md`: `OVR-05` flipped to Complete (checkbox + traceability table), since both plans declaring it in frontmatter (`197-03`, `197-04`) have now finished — the shared-ID gate (#2388) that held it Pending after `197-03` is satisfied.

## ROADMAP pointer for the orchestrator to apply

Read `.planning/ROADMAP.md` § "Phase 199: What the rails can actually deliver". The anchor line to
match, verbatim, is:

```
**Depends on**: Phase 197
```

Replace that single line with itself plus one new line directly beneath it:

```
**Depends on**: Phase 197
**Evidence inherited**: see `.planning/notes/197-at28c-guard-evidence-for-phase-199.md` for the measured 19-row AT28C DIP24 pinout/flags table, the operator ruling routing the guard's narrowing here, and the three test legs (`test_sdp_capability.py`, `test_chip_resolver.py:87`, `test_build_db_inclusion.py::TestUnsupportedReasonStrings::test_at28c16_named_arm_reason_mentions_adapter_doc`) that redden together the moment the guard is narrowed.
```

This is a scoped, single-anchor `Edit` — do not rewrite the Phase 199 section or touch any other
phase entry.

## Task Commits

Each task was committed atomically, inside the submodule (except Task 3's note and the gitlink advance):

1. **Task 1: Delete AT28C DIP24 name list, guard becomes sole writer** - `firestarter_app@6116500` (test)
2. **Task 2: Delete FM1608 relabel, pin both moved fields** - `firestarter_app@1cab76e` (feat)
3. **Task 3: File guard-narrowing evidence for Phase 199** - `meta@c611885d` (docs)

**Gitlink advance:** `meta@c3d8def4` (chore: advance firestarter_app gitlink)

**Plan metadata:** committed alongside this SUMMARY.md and REQUIREMENTS.md (see final commit in this plan's history)

_Note: both Task 1 and Task 2 are `tdd="true"`; correctness was proven via the plan's own `<verify>` automation (regeneration diffs, byte-identity against `70c92ce`, the known-red-window full-suite check, the no-comments check) plus the existing/rewritten unit tests, rather than a separate RED→GREEN→REFACTOR commit sequence — as in plans `197-02`/`197-03`, each deletion's correctness gate is its own dedicated assertion (the reason-string content, the two FM1608 fields), each unreachable against the pre-deletion code, so the rewritten test IS the RED-then-GREEN proof, executed and inspected before staging rather than committed as a separate RED commit._

## Files Created/Modified

- `firestarter_app/tools/build_db.py` - deleted `_AT28C_DIP24_NAMES` + its consuming arm + orphaned comment block (Task 1); deleted `_ETYPE_RELABEL` + its comprehension/loop + orphaned comment block (Task 2); kept the hardware-damage guard, the single `_chip_aliases` derivation, and the `_upstream_proto_id` capture all byte-unchanged
- `firestarter_app/tests/test_build_db_inclusion.py` - rewrote `test_at28c16_named_arm_reason_mentions_adapter_doc` (guard wording, docstring inverted) and `test_fm1608_resolves_sram_std` (SRAM + new vcc_mv assertion, docstring updated) plus the class docstring
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` - re-recorded; exactly one line changed (FM1608 FRAM → SRAM)
- `firestarter_app/firestarter/data/chip_database.json` - regenerated; 9 `unsupported_reason` string swaps (Task 1) + FM1608's two fields (Task 2), nothing else
- `.planning/notes/197-at28c-guard-evidence-for-phase-199.md` - new; the Phase 199 evidence note (Task 3)
- `.planning/REQUIREMENTS.md` - `OVR-05` checkbox and traceability-table row flipped to Complete (2-line diff)
- `firestarter_app` (gitlink in meta repo) - advanced to `1cab76e`

## Decisions Made

- **Kept the single `_chip_aliases` derivation in Task 1** rather than removing it as the plan's contingency language allowed, because it is measured to be reused two statements later by `apply_datasheet_override` (the override mechanism plan 197-02/03 wired in) — not, as the plan flagged as a possible outcome, consumed only by the arm being deleted. Removing it would have broken the override key resolution for every row.
- **`OVR-05` marked Complete in `REQUIREMENTS.md`** by hand-editing exactly two lines (checkbox + table row), per this project's standing note that the requirements/roadmap verbs reformat the whole file, and per the shared-ID gate (#2388) now being satisfied — both `197-03` and `197-04`, the only two plans declaring `OVR-05`, have finished.
- **`ROADMAP.md` not touched by this executor**, per the orchestrator's explicit roadmap-edit exception for this plan's Task 3. The note itself (the real deliverable) is written in full; the pointer text and anchor are handed to the orchestrator verbatim above.
- **`test_at28c16_named_arm_reason_mentions_adapter_doc` keeps its original name** even though the "named arm" it originally tested no longer exists, per the plan's own artifact tracking, which names this exact test as being rewritten in place.
- **`gsd_run query commit` was not used for any commit**, per this project's standing rule that the verb has twice self-created a stray `gsd/v1.40-...` branch mid-plan in this repository. All commits were made with plain `git commit`, with an explicit branch check before and after each one, and with the not-worktree / not-protected-branch preconditions confirmed before every commit.

## Deviations from Plan

None - plan executed exactly as written. The one contingency the plan explicitly flagged as needing a judgment call (whether to keep or remove the `_chip_aliases` comprehension) resolved in the "keep it" branch the plan itself anticipated, not a deviation from it.

**Total deviations:** 0
**Impact on plan:** None.

## Deleted-comment report (CLAUDE.md "Source code comments — hard rule")

**Task 1** (`firestarter_app@6116500`): 12 comment lines deleted from `tools/build_db.py`
(measured: `git show 6116500 -- tools/build_db.py | grep -cE '^-\s*#'` → 12). Quoted verbatim, per
the reporting requirement, because they record ordering/contract invariants and a decode fact:

> `# These arrive as proto_id 0x0D (configure_eeprom28c, pure 5V, no`
> `# VPP), so the guard above does NOT fire and proto_id stays 0x0D —`
> `# a real dispatchable handler. They are refused in-host by`
> `# support_status="adapter-required", which chip_resolver rejects`
> `# before any wire dict is built. This arm therefore sets only`
> `# support_status + reason and must NOT touch proto_id.`

> `# The reason string must start with "adapter required:" —`
> `# test_adapter_required_reason_starts_with_adapter_required.`

Both clauses described behavior of the arm being deleted (the "must NOT touch proto_id" invariant
and the cross-reference to a still-existing, unmodified test), not a fact about surviving code, so
deleting them whole (not rewording) is correct per the rule.

**Task 2** (`firestarter_app@1cab76e`): 6 comment lines deleted from `tools/build_db.py`
(measured: `git show 1cab76e -- tools/build_db.py | grep -cE '^-\s*#'` → 6). Quoted verbatim — this
one records a hardware/firmware-behavior fact about a DIFFERENT, still-shipping part
(`SST39SF040`), not about the deleted mechanism itself, so it is flagged explicitly here even
though it was correctly deleted whole (it documents a non-entry in a map that no longer exists):

> `# SST39SF040 deliberately KEEPS Flash/EEPROM: relabelling it to`
> `# 'Flash' flips FLAG_CAN_ERASE off and breaks its auto-erase.`

This fact (relabelling `SST39SF040` to `Flash` would flip `FLAG_CAN_ERASE` off and break its
auto-erase) is not lost: `SST39SF040` was never in `_ETYPE_RELABEL` and is not touched by either
of this plan's deletions — the comment was a warning against a hypothetical future edit to a map
that no longer exists, so it has no surviving subject to attach to. No code behavior changes for
`SST39SF040` as a result of this deletion.

**No comment line was added to any staged `.py` file in either task** — the mandatory check
(`git diff --cached -- '*.py' | grep -E '^\+\s*#' | grep -v '^\+\s*#!'`) printed nothing before
both commits.

## Issues Encountered

None. `gitlab.com` was reachable for every regeneration; the Python 3.11 venv at `/tmp/fs-venv311`
was reused without modification. The full suite ran to completion in every invocation.

## Known Stubs

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `tools/build_db.py` now contains **zero part-number literal hardcodes** — `NMOS_TRUE_VPP_MV`
  (evacuated in `197-03`), `_AT28C_DIP24_NAMES` and `_ETYPE_RELABEL` (both deleted in this plan)
  are all gone. `197-05`'s census of surviving part-specific constants should find nothing at these
  two sites.
- The hardware-damage guard is untouched and its narrowing is explicitly routed to Phase 199, with
  the full measured evidence filed at `.planning/notes/197-at28c-guard-evidence-for-phase-199.md`
  — Phase 199 can read the guard's actual selection criterion, the pinout mismatch in its own
  comment, and the three test legs that will need rewriting together, without re-deriving any of
  it.
- **The two known-red `tests/test_wire_dict_equivalence.py` tests remain open, to be closed by
  `197-06` by name**, exactly as this plan's known-red window specified:
  - `tests/test_wire_dict_equivalence.py::test_live_capture_matches_golden_plus_the_149_and_153_and_182_and_194_deltas`
  - `tests/test_wire_dict_equivalence.py::test_exactly_84_records_change_flags_and_no_other_field_moves`
- No blockers. `197-05` and onward can proceed against a database whose only diffs from `70c92ce`
  are the 9 reason-string swaps, FM1608's two fields, and `197-03`'s already-byte-identical NMOS
  move — nothing else has moved.
- **Outstanding for the orchestrator:** apply the `ROADMAP.md` pointer recorded above under
  "## ROADMAP pointer for the orchestrator to apply" (single-anchor edit, `.planning/ROADMAP.md`
  is otherwise untouched by this plan).

## Self-Check: PASSED

- FOUND: `firestarter_app/tools/build_db.py`
- FOUND: `firestarter_app/tests/test_build_db_inclusion.py`
- FOUND: `firestarter_app/tests/__snapshots__/test_characterization.ambr`
- FOUND: `.planning/notes/197-at28c-guard-evidence-for-phase-199.md`
- FOUND commit: `firestarter_app@6116500`
- FOUND commit: `firestarter_app@1cab76e`
- FOUND commit: `meta@c611885d`
- FOUND commit: `meta@c3d8def4`
- Both `firestarter_app` and meta repo HEAD confirmed on `v1.40-program-parameter-fidelity`
- Gitlink in meta repo confirmed pointing at `firestarter_app@1cab76e`
- `.planning/ROADMAP.md` confirmed untouched (`git diff --stat` empty) per the roadmap-edit exception
- `.planning/STATE.md` confirmed untouched

---
*Phase: 197-the-override-mechanism-and-the-program-pulse*
*Completed: 2026-09-18*
