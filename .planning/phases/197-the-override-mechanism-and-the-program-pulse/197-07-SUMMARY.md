---
phase: 197-the-override-mechanism-and-the-program-pulse
plan: 07
subsystem: database-generator
tags: [python, build_db, chip_database, datasheet-override, pulse-delay, decode-notes, backlog, gh-70]

# Dependency graph
requires:
  - phase: 197-06
    provides: "A fully-verified, wire-and-database-consistent Phase 197 state: 13 changed database rows (0 support_status changes), a 3-record wire-dict delta layer, full Python 3.11 suite green at 2065 passed / 32 snapshots / 0 failed."
provides:
  - "197-PULSE-INVENTORY.md: the measured D-12 inventory of all 215 algorithm 7/8 rows still at pulse_duration_us=100 after this phase, with a reproducible generating command, a twelve-row Fujitsu disposition table (3 CORRECTED, 1 DATASHEET-CONFIRMED-CORRECT, 8 NO DATASHEET), and the complete 208-row non-Fujitsu list by manufacturer."
  - "tools/DECODE-NOTES.md section 8: the written PULSE-01 finding -- pulse_delay is plain microseconds for protocols 0x07/0x08/0x0B, confirmed positively by FUJITSU/MBM27C4001, falsified as per-part by the 462/675 bulk-default measurement, with the firmware wire-semantics argument, the exact 0x0D boundary, and the fail-closed empty-input behavior all recorded."
  - "tools/DECODE-NOTES.md section 5 corrected: the retired Phase-84 SRAM->FRAM relabel claim is replaced with what is true after Phase 197 D-08."
  - "tests/golden/chip_database_field_inventory.json's meta block corrected: no longer names a nonexistent diff tool; names the stale baseline with both measured byte figures."
  - "derive-away-max-27c020-size-hardcode.md moved pending -> completed, with a closure note citing the byte-identical proof."
  - "Three backlog entries (999.69, 999.70, 999.71) drafted verbatim, with an unambiguous anchor, for the orchestrator to apply to .planning/ROADMAP.md -- see '## ROADMAP edits for the orchestrator to apply' below. Not applied directly, per the orchestrator's single-writer exception for this plan."
affects: [198, 199, 200]

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
# Multi-repo plan: gsd_run query commit disabled for this project per its standing note
# (has twice self-created a stray gsd/v1.40-... branch); commits measured by hand per
# repo, following the 197-01..06 precedent.
actuals:
  tokens: 8100
  tasks: 3
  commits: 7
  commits_by_repo:
    firestarter_app: 1
    meta: 6

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Re-derive every inventory figure from the live shipped database rather than copying a figure out of CONTEXT.md or a prior research document -- the measured post-phase 100us count (215) differs from CONTEXT.md's stale deferred note (216), and the inventory records both numbers and states which one is measured, per the 177-READBACK-INVENTORY.md precedent."
    - "When a caller's exception instruction (single-writer discipline for a shared file) conflicts with the plan's own inline task text, the caller's instruction governs: this plan's Task 3 text explicitly directed editing .planning/ROADMAP.md, but the orchestrator's roadmap_edit_exception for this run explicitly overrode that -- the edits were made, verified, then reverted in a dedicated commit, and the exact text plus an unambiguous anchor were recorded here instead."

key-files:
  created:
    - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-PULSE-INVENTORY.md
  modified:
    - firestarter_app/tools/DECODE-NOTES.md
    - firestarter_app/tests/golden/chip_database_field_inventory.json
    - .planning/todos/completed/derive-away-max-27c020-size-hardcode.md (moved from pending/)

key-decisions:
  - "The plan's own Task 1 wording ('the 215 rows outside the Fujitsu block') does not match measurement: 215 is the TOTAL post-phase 100us count, which includes 7 Fujitsu rows (6 NO DATASHEET + 1 DATASHEET-CONFIRMED-CORRECT). The genuinely non-Fujitsu count is 208, matching the plan's own stated per-manufacturer top counts (ATMEL 16, NSC 15, AMD 14, ...) exactly. The inventory records both figures (215 total, 208 non-Fujitsu) and reconciles them explicitly rather than silently picking one."
  - "The verify leg `! grep -q 'diff_db' tests/golden/chip_database_field_inventory.json` fails against the meta key name `why_not_diff_db` itself, independent of its value -- the key literally contains the substring the check forbids. Renamed the key to `why_no_regen_diff_tool`, confirmed by grep that no test in the repository reads the key by name (only the golden file itself referenced it), so the rename is safe."
  - "Per the orchestrator's roadmap_edit_exception for this run, the three backlog entries and the todo-closure ROADMAP.md content were drafted, verified against every verify leg in the plan, then REVERTED from .planning/ROADMAP.md in a dedicated commit -- this plan does not edit that file directly. The exact entry text plus an unambiguous anchor (a single-occurrence string bracketing the insertion point) are recorded below for the orchestrator to apply verbatim. This plan's own Task 3 is treated as complete because the text is recorded, not because ROADMAP.md changed -- per the exception's own stated completion criterion."
  - "The todo-closure move (derive-away-max-27c020-size-hardcode.md, pending -> completed) is NOT part of the ROADMAP exception -- it is a separate file, and the orchestrator's exception names only .planning/ROADMAP.md. That move and its closure note are committed directly by this plan, same as Task 1's inventory and Task 2's DECODE-NOTES/golden edits."
  - "git mv, run immediately after an uncommitted Edit to the source file, staged the pre-edit (last-committed) blob at the destination path rather than the just-edited worktree content -- the first Task 3 commit therefore recorded a pure 0-diff rename, silently leaving both the ROADMAP.md backlog entries and the todo's closure note uncommitted. Caught by re-running `git diff --stat` against the intended paths after the commit rather than trusting the commit's own reported stat; a follow-up commit landed the missed content. See Deviations."

requirements-completed: [PULSE-01]

coverage:
  - id: D1
    description: "197-PULSE-INVENTORY.md written per the 177-READBACK-INVENTORY.md precedent: reproducible method stated before the data, 297 algorithm 7/8 rows (170/127 split) with a full pulse-width distribution, pre-phase 217 -> post-phase 215 at 100us reconciled against the phase's three corrections, the CONTEXT.md 216-vs-215 discrepancy named and resolved in favor of the measured figure, the twelve-row Fujitsu table with all three verdict terms, and the 208-row non-Fujitsu list with per-manufacturer counts and a complete fenced block"
    requirement: PULSE-01
    verification:
      - kind: other
        ref: "test -f 197-PULSE-INVENTORY.md -> present"
        status: pass
      - kind: other
        ref: "grep -qF for CORRECTED / DATASHEET-CONFIRMED-CORRECT / NO DATASHEET / chip_database.json / 297 -> all found"
        status: pass
      - kind: other
        ref: "python -c '...' independent re-derivation: TOTALS 297 215 -> matches the artifact exactly"
        status: pass
      - kind: other
        ref: "grep -c '^|' 197-PULSE-INVENTORY.md -> 48 (>= 20 required)"
        status: pass
    human_judgment: false
  - id: D2
    description: "tools/DECODE-NOTES.md section 8 states the PULSE-01 finding with its positive datasheet proof, the 462/675 bulk-default falsification, the no-coherent-multiplier argument, the firmware wire semantics (verify-per-pulse loop, overprogram_factor=0), the exact 0x07/0x08/0x0B vs 0x0D protocol-membership boundary and post-classify call-site consequence, and the raise-rather-than-default empty-input behavior with its single covering test module; section 5's heading and relabel clause corrected; the field-inventory golden's meta block corrected and still parses"
    requirement: PULSE-01
    verification:
      - kind: other
        ref: "grep for section 8 present + sections 0-7 all still present -> SECTIONS_OK"
        status: pass
      - kind: other
        ref: "grep -qF for 0x0064 / 0x07 / 0x0B / 0x0D / 462 / 675 / overprogram_factor / interpret_timing -> all found"
        status: pass
      - kind: other
        ref: "grep -qF 'cosmetic `SRAM -> FRAM` relabel then applies' absent -> SECTION5_OK"
        status: pass
      - kind: other
        ref: "grep -q 'diff_db' tests/golden/chip_database_field_inventory.json -> absent (key renamed to why_no_regen_diff_tool)"
        status: pass
      - kind: unit
        ref: "tests/test_chip_database_field_inventory.py tests/test_build_db_interpret_timing.py -o addopts='' -q -rf -> 11 passed"
        status: pass
    human_judgment: false
  - id: D3
    description: "Three backlog entries (999.69, 999.70, 999.71) drafted verbatim with an unambiguous anchor, recorded for the orchestrator to apply to .planning/ROADMAP.md; the derive-away-max-27c020-size-hardcode.md todo closed (pending -> completed) with a closure note; the two todos CONTEXT.md keeps open remain in pending/; full Python 3.11 suite still green"
    requirement: PULSE-01
    verification:
      - kind: other
        ref: "Applied-and-verified-then-reverted: grep for ### Phase 999.69/70/71 headings, phase-heading floor (177 >= 63), MEASURED/INFERRED/DIP32_27C020/UNSOURCED/197-PULSE-INVENTORY.md tokens -- all passed before the deliberate revert"
        status: pass
      - kind: other
        ref: "test -f completed/derive-away-max-27c020-size-hardcode.md && ! test -f pending/... -> TODO_MOVE_OK; both kept-open todos still present in pending/ -> KEPT_TODOS_OK"
        status: pass
      - kind: unit
        ref: "pytest tests/ -o addopts='' -q -rf on Python 3.11.16 -> 2065 passed, 32 snapshots passed, 0 failed (unchanged from wave-6 baseline)"
        status: pass
    human_judgment: false

duration: ~70min
completed: 2026-09-18
status: complete
---

# Phase 197 Plan 07: The override mechanism and the program pulse Summary

**Wrote the measured D-12 inventory of all 215 uncorrected 100us program-pulse rows, recorded the confirmed PULSE-01 decode finding as a new DECODE-NOTES.md section, corrected two claims this phase had falsified, closed one todo, and drafted three backlog entries for the orchestrator to apply after this plan's own direct ROADMAP.md edit was deliberately reverted per the orchestrator's single-writer exception.**

## Performance

- **Duration:** ~70 min
- **Started:** 2026-09-18
- **Completed:** 2026-09-18
- **Tasks:** 3 (all `type="auto"`)
- **Files modified:** 4 (1 new inventory artifact, 2 firestarter_app files, 1 todo moved), plus 1 gitlink; ROADMAP.md touched then reverted (net zero)

## Accomplishments

- **Task 1 — the measured 100us inventory, every row disposed:**
  - Wrote `197-PULSE-INVENTORY.md` leading with the exact generating command, following the
    `177-READBACK-INVENTORY.md` precedent (reproducible method first, every row disposed with a
    verdict, a named honesty limit).
  - **Measured, independently, from the live `firestarter/data/chip_database.json`:** 297 algorithm
    7/8 rows (170 on algorithm 7, 127 on algorithm 8), full pulse-width distribution
    (10:7, 20:1, 50:15, **100:215**, 200:28, 500:6, 1000:25 — sum 297), pre-phase count at 100us
    **217** (measured against `git show 70c92ce:...`), post-phase **215**, reconciled exactly:
    217 − 2 (the two rows this phase moved out of the 100us bucket) = 215.
  - **Corrected CONTEXT.md's stale figure**: its deferred note says 216; the measured, re-derived
    figure is 215. Both numbers are recorded, with the measured one stated as authoritative.
  - Disposed all twelve Fujitsu algorithm 7/8 rows with a bolded verdict: 3 **CORRECTED**
    (`MBM27128`, `MBM27C1000P,MBM27C1000`, `MBM27C1001`), 1 **DATASHEET-CONFIRMED-CORRECT**
    (`MBM27C4001`, with its tPW 95/100/105 figures and the reason it carries no override entry — a
    no-op would fail the build under D-04), 8 **NO DATASHEET**.
  - **Found and recorded a discrepancy in the plan's own wording**: Task 1's instructions describe
    "the 215 rows outside the Fujitsu block" with specific per-manufacturer counts, but the measured
    non-Fujitsu count is **208** (215 total minus 7 Fujitsu rows currently at 100us). The stated
    per-manufacturer top counts (ATMEL 16, NSC 15, AMD 14, SGS-THOMSON 14, MACRONIX(MXIC) 13,
    INTEL 11, ST 11, FAIRCHILD 9) match the measured 208-row non-Fujitsu population exactly, so this
    is recorded as a reconciliation (215 total = 208 non-Fujitsu + 7 Fujitsu-at-100) rather than a
    contradiction, and both figures appear in the inventory.
  - Complete 208-row non-Fujitsu list (manufacturer, part number, size, VPP) recorded as a fenced
    block, with the generating command adjacent, alongside the 32-manufacturer summary table.
- **Task 2 — the PULSE-01 finding, and two falsified claims corrected:**
  - Appended section 8 to `tools/DECODE-NOTES.md`: the confirmed decode rule, the positive
    `MBM27C4001` proof, the 462/675 bulk-default falsification, the no-coherent-multiplier argument,
    the firmware wire semantics (verify-per-pulse loop capped at 25 pulses, `overprogram_factor = 0`
    on all three protocol rows), the exact `0x07`/`0x08`/`0x0B` vs `0x0D` protocol-membership
    boundary and the post-`classify()` call-site consequence for promoted rows, and the fail-closed
    (raise, not default-to-0) empty-input behavior with its single covering test module. Sections 0
    through 7 are unchanged and still numbered 0 through 7.
  - Corrected section 5's heading and relabel clause: it now states that Phase 197 (D-08) deleted the
    Phase-84 `SRAM → FRAM` relabel, that the row emits `electrical.type: "SRAM"`, and that
    `electrical.vcc_mv` takes the SRAM single-rail rewrite the `FRAM` label had been bypassing
    (3300 → 5000). The ground-truth tuple, the type-4 argument, and the decimal-40 conflation note
    are unchanged.
  - Corrected `tests/golden/chip_database_field_inventory.json`'s stale-tool reference. **Deviation:**
    the plan's verify leg (`! grep -q 'diff_db' ...`) matches the meta key's own name
    (`why_not_diff_db`) regardless of its value content, so the key itself was renamed to
    `why_no_regen_diff_tool` — confirmed by grep that no test reads this key by name, so the rename
    is safe. The corrected value names the stale baseline with both measured byte figures (475857
    stale vs. 432984 live — a small, honestly re-measured update from the plan's stated 432461,
    reflecting the database's state as of this plan's run rather than 197-05's).
  - `tests/test_chip_database_field_inventory.py` and `tests/test_build_db_interpret_timing.py`:
    11 passed.
- **Task 3 — three backlog entries drafted, one todo closed, one deviation caught and reverted:**
  - Drafted, staged, and fully verified three backlog entries (999.69, 999.70, 999.71) directly in
    `.planning/ROADMAP.md`, matching the existing entry shape exactly, with zero phase headings lost
    (174 → 177, +3 exactly). **Then reverted them from `.planning/ROADMAP.md`** in a dedicated commit,
    per the orchestrator's `roadmap_edit_exception` for this run, which explicitly overrides this
    plan's own inline Task 3 instructions to edit that file directly (see Deviations). The exact
    entry text and an unambiguous single-occurrence anchor are recorded below in
    `## ROADMAP edits for the orchestrator to apply`.
  - Closed `.planning/todos/pending/derive-away-max-27c020-size-hardcode.md` with `git mv` to
    `completed/`, appending a closure note naming Phase 197 Plan 01 and the byte-identical proof
    (`firestarter_app@5fec5eb`). The two todos CONTEXT.md keeps open
    (`pinout-address-width-and-we-pin-corrections.md`,
    `fram-parts-ride-the-0x0d-handler-by-pinout-promotion.md`) remain untouched in `pending/`.
  - **Deviation caught mid-task**: the first Task 3 commit's own reported stat showed a pure 0-diff
    rename for the todo file — `git mv`, run right after an uncommitted `Edit` to the source path,
    staged the last-committed (pre-edit) blob at the destination rather than the just-edited worktree
    content, silently leaving both the ROADMAP.md insertions and the todo's closure note
    uncommitted. Caught by re-running `git diff --stat` against the intended paths rather than
    trusting the commit's reported stat; a follow-up commit landed the missed content.
  - Re-ran the full Python 3.11 suite after all edits: **2065 passed, 32 snapshots passed, 0
    failed** — unchanged from the wave-6 baseline this plan started from.

## Task Commits

Each task was committed atomically. Because the roadmap_edit_exception required a mid-plan revert,
Task 3 spans five commits instead of one:

1. **Task 1: measured 100us program-pulse inventory** — `meta@f43c3e67` (docs)
2. **Task 2: PULSE-01 finding + two falsified claims corrected** — `firestarter_app@0372cc6` (docs)
3. **Gitlink advance** — `meta@af0f70d1` (chore)
4. **Task 3a: backlog entries + todo rename (incomplete — git-mv content-loss deviation)** —
   `meta@59481654` (docs)
5. **Task 3b: land the content the prior commit's rename missed** — `meta@b7ae2cbe` (docs)
6. **Revert: un-edit ROADMAP.md per the orchestrator's single-writer exception** — `meta@d883d9f6`
   (revert)
7. **Fix the inventory's own now-stale backlog-filing claim** — `meta@2d331286` (docs)

**Plan metadata:** committed alongside this SUMMARY.md (see final commit in this plan's history)

## Files Created/Modified

- `.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-PULSE-INVENTORY.md` — new;
  the measured D-12 inventory
- `firestarter_app/tools/DECODE-NOTES.md` — section 8 appended (PULSE-01 finding); section 5
  corrected
- `firestarter_app/tests/golden/chip_database_field_inventory.json` — `meta.why_not_diff_db`
  renamed to `meta.why_no_regen_diff_tool` and corrected
- `.planning/todos/completed/derive-away-max-27c020-size-hardcode.md` — moved from `pending/`, with
  a closure note
- `.planning/ROADMAP.md` — touched (999.69/70/71 inserted, verified) then reverted; net diff zero.
  Drafted text recorded below for the orchestrator.
- `firestarter_app` (gitlink in meta repo) — advanced to `0372cc6`

## Decisions Made

- **The 215-vs-208 reconciliation was recorded rather than silently resolved one way.** The plan's
  own Task 1 text conflates "215 rows at 100us total" with "215 rows outside the Fujitsu block" —
  measurement shows the non-Fujitsu figure is 208, and the plan's own per-manufacturer counts
  already matched 208, confirming which figure was intended. Both numbers appear in the inventory
  with the reconciliation stated.
- **CONTEXT.md's 216 is superseded by the measured 215**, per this plan's own must-haves. The
  discrepancy is named plainly rather than silently adopted either way.
- **The golden's `why_not_diff_db` key was renamed, not just its value**, because the verify leg's
  substring check matches the key name itself. Confirmed safe by grep (nothing reads the key by
  name).
- **Per the orchestrator's `roadmap_edit_exception`, this plan does not edit `.planning/ROADMAP.md`
  directly**, even though the plan's own inline Task 3 text instructs exactly that. The three
  backlog entries were drafted, staged, and verified against every one of the plan's own verify legs
  (proving the content is correct and complete) and then reverted, with the verbatim text and an
  anchor recorded for the orchestrator. This plan's Task 3 is treated as complete on that basis, per
  the exception's own stated completion criterion.
- **The todo-closure move is NOT covered by the ROADMAP exception** (a different file) and is
  committed directly, same as every other file this plan touches.
- **`gsd_run query commit` / `gsd-tools query commit` was not used for any commit**, per this
  project's standing rule that the verb has repeatedly self-created a stray `gsd/v1.40-...` branch
  mid-plan. All commits were made with plain `git commit`, with an explicit branch check
  (`git rev-parse --abbrev-ref HEAD`) before and after each one.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug, self-caught] `git mv` staged pre-edit content, silently dropping an uncommitted edit and this plan's own ROADMAP.md insertions**
- **Found during:** Task 3, verifying the commit's own reported diffstat
- **Issue:** After editing `.planning/todos/pending/derive-away-max-27c020-size-hardcode.md` to add
  a closure note (uncommitted), running `git mv` to relocate it to `completed/` staged the
  last-committed (pre-edit) blob at the new path rather than the current worktree content. The
  ensuing commit reported a pure 0-diff rename, and — because a single multi-path `git add` call in
  the same commit step also failed on a stale pathspec (the file no longer existed at its old
  path), staging aborted entirely for that call — the `.planning/ROADMAP.md` insertions from the
  same task step were left uncommitted too.
- **Fix:** Ran `git diff --stat` against every path this task step touched (not just trusting the
  commit's own summary) and found both files still dirty. Staged and committed them in a follow-up
  commit (`meta@b7ae2cbe`).
- **Files modified:** none beyond what Task 3 already touches
  (`.planning/ROADMAP.md`, `.planning/todos/completed/derive-away-max-27c020-size-hardcode.md`)
- **Verification:** `git diff --stat` against both paths returned empty after the follow-up commit;
  all of Task 3's own verify legs re-run and passed against the final committed state.
- **Committed in:** `meta@b7ae2cbe`

**2. [Rule 1 - Bug, verify-leg design flaw, self-caught] The field-inventory golden's verify leg checks the meta key's own name, not just its value**
- **Found during:** Task 2, running its own `<verify>` leg before committing
- **Issue:** `! grep -q 'diff_db' tests/golden/chip_database_field_inventory.json` fails
  unconditionally while the meta key is named `why_not_diff_db`, independent of what the value says
  — the literal key name contains the forbidden substring.
- **Fix:** Renamed the key to `why_no_regen_diff_tool`. Confirmed by
  `grep -rln 'why_not_diff_db' . --include=*.py --include=*.json --include=*.md` that only the
  golden file itself referenced the old name — no test reads it by name — so the rename is safe.
- **Files modified:** `firestarter_app/tests/golden/chip_database_field_inventory.json`
- **Verification:** the verify leg passes; `tests/test_chip_database_field_inventory.py` (which does
  not read the `meta` block) still passes; JSON still parses.
- **Committed in:** `firestarter_app@0372cc6`

---

**Total deviations:** 2 auto-fixed (1 self-caught git-plumbing content-loss bug in a multi-step
commit sequence, 1 self-caught verify-leg substring-matches-key-name design gap). No scope creep;
both fixes are corrections to this plan's own execution mechanics, not to its substance.
**Impact on plan:** None on the inventory's or the DECODE-NOTES finding's content. The
`roadmap_edit_exception` handling above is a caller instruction override, not a deviation under
Rules 1-4 — it is documented in Decisions Made and in the dedicated `## ROADMAP edits` section
below, not counted here.

## Issues Encountered

None beyond the two auto-fixed items documented above. The pinned Python 3.11.16 venv
(`/tmp/fs-venv311`) was reused without modification; the full suite (209.98s) ran to completion.
`gitlab.com` reachability was not needed for this plan — no `tools/build_db.py` regeneration was
run; the shipped `firestarter/data/chip_database.json` from `197-05`/`197-06` was read only.

## Known Stubs

None.

## Deleted-comment report (CLAUDE.md "Source code comments — hard rule")

**No comment line was added to any staged `.py` file in this plan.** This plan's only `firestarter_app`
commit (`0372cc6`) touches `tools/DECODE-NOTES.md` (markdown) and
`tests/golden/chip_database_field_inventory.json` (JSON) — neither is Python source, and the
mandatory check
(`git diff --cached -- '*.py' | grep -E '^\+\s*#' | grep -v '^\+\s*#!'`) printed nothing before that
commit, confirmed directly since no `.py` file was staged at all. No existing comment was deleted or
modified — `DECODE-NOTES.md`'s existing sections 0–7 were read and cross-checked for pronoun
antecedents after editing section 5, and none were disturbed by the section-8 append.

## ROADMAP edits for the orchestrator to apply

Per `roadmap_edit_exception`: this plan does not edit `.planning/ROADMAP.md` directly. The following
three entries were drafted, staged in `.planning/ROADMAP.md`, and verified against every one of this
plan's own verify legs (heading presence, phase-heading-count floor with zero loss, required tokens
present) — then reverted (`meta@d883d9f6`) so the orchestrator remains the single writer. Apply
verbatim.

**Anchor** (verified unique — occurs exactly once in `.planning/ROADMAP.md`, immediately before the
`## v1.20` milestone heading, at the end of backlog entry 999.68):

```
not, in whatever artifact carries this work.

---

## v1.20 — Protocol-Only Dispatch — Remove the Legacy `mem_type` Axis (SHIPPED 2026-07-02)
```

**Replace with** (inserting the three new entries between the existing `---` and the `## v1.20`
heading — the anchor's leading and trailing text is unchanged, only the middle is new):

```
not, in whatever artifact carries this work.

---

### Phase 999.69: 215 algorithm 7/8 rows still carry `pulse_duration_us: 100` with no datasheet evidence (BACKLOG — filed 2026-09-18 during v1.40 Phase 197)

**Goal:** Correct as many of the 215 uncorrected algorithm 7/8 rows as datasheet evidence
justifies, one row at a time.

**Measured 2026-09-18** (Phase 197 Plan 07), against the shipped `firestarter/data/chip_database.json`:
**215 of 297** algorithm 7/8 rows carry `pulse_duration_us: 100`, down from a pre-phase 217 (Phase
197 corrected two of them away from 100 via `tools/datasheet_overrides.json`). The full inventory —
reproducible generating command, the twelve-row Fujitsu disposition table, and the complete
208-row non-Fujitsu list with per-manufacturer counts — is recorded at
[`197-PULSE-INVENTORY.md`](../phases/197-the-override-mechanism-and-the-program-pulse/197-PULSE-INVENTORY.md).

**Cost model (D-02, deliberate):** one entry in `tools/datasheet_overrides.json` targets exactly
one row, and each entry must name the datasheet that justifies it. Correcting all 215 rows costs
215 datasheets — this is the intended deterrent against a bulk sweep that would apply one
convenient figure across many parts, the exact failure shape `NMOS_TRUE_VPP_MV` demonstrated before
Phase 197 deleted it (see 999.71 below).

**A row's presence in this list is not a claim that its value is wrong** — it is a claim that
nobody has checked it against that part's own datasheet. `197-PULSE-INVENTORY.md`'s own honesty
limit states this explicitly: these rows are inventoried, not audited.

---

### Phase 999.70: `FUJITSU/MBM27C1000` is on `DIP32_27C020`, which is the sibling part's pinout — pins 2 and 24 are swapped (BACKLOG — filed 2026-09-18 during v1.40 Phase 197, from `197-RESEARCH.md` § "PULSE-02 — Which Rows, To What Values")

**Goal:** Resolve whether `FUJITSU/MBM27C1000P,MBM27C1000` needs its own pinout, distinct from
`FUJITSU/MBM27C1001`'s, and correct gh#70's own pinout cross-check if so.

**MEASURED:** `MBM27C1000` and `MBM27C1001` have different pin assignments. From the MBM27C1000
datasheet (page 4-61, PIN ASSIGNMENT): `/OE` on pin 2, `A16` on pin 24. From the MBM27C1001
datasheet (page 9-86, PIN DESCRIPTION): `A16` on pin 2, `OE` on pin 24 — the two pins are swapped
between the parts. `firestarter/data/pinouts.json`'s `DIP32_27C020` gives an `address-bus-pins`
list whose index 16 (the `A16` bit) is pin 2, and an `oe-pin` of 24 — the **MBM27C1001** layout.
The database routes `FUJITSU/MBM27C1000P,MBM27C1000` through this same `DIP32_27C020` pinout key,
so that row is on its sibling's pin map, not its own.

**INFERRED, NOT bench-tested:** under the swap, a write to an address needing `A16` set drives the
wrong socket pin, and because the part's real `A16` (socket pin 24) then follows whatever the `OE`
line is doing, a verify reads a different address than the program pulse wrote. This matches the
reported failure signature of a byte at the top of the address space failing to program within 25
pulses. This inference is unconfirmed on hardware — no bench run has isolated the pinout swap from
the pulse-width correction Phase 197 already applied to this row.

**This contradicts an earlier published cross-check on gh#70** that concluded the pinout was a
"MATCH on every pin the part uses" — that conclusion was drawn from the `MBM27C1001` datasheet,
before the `MBM27C1000` datasheet (vendored into this repository during Phase 197, from the gh#70
attachment) was available for direct comparison.

**Route:** this belongs with the existing todo
[`pinout-address-width-and-we-pin-corrections.md`](../todos/pending/pinout-address-width-and-we-pin-corrections.md)
— it is the same class of defect (a row on a pinout too narrow or wrong for it), found by the same
kind of datasheet-vs-generated-data comparison. **It also materially changes what a `197-08`-style
PULSE-04 answer may claim on gh#70**: an answer that states only the pulse-width correction, without
naming the pinout question as open and unresolved, would overstate what Phase 197 actually fixed
for this specific reported failure.

---

### Phase 999.71: Six `UNSOURCED` override entries carry an Intel VPP reading applied to non-Intel parts (BACKLOG — filed 2026-09-18 during v1.40 Phase 197, from `197-03-SUMMARY.md`)

**Goal:** Close each `UNSOURCED` entry in `tools/datasheet_overrides.json` with the vendor-specific
datasheet that would actually justify its value, or revert the entry if no such datasheet
substantiates it.

**The six entries**, all on `electrical.vpp_mv`, all inherited verbatim from the deleted
`NMOS_TRUE_VPP_MV` hardcode: `INTEL/M2716` (18000 → 25000), `INTEL/M2732` (18000 → 25000),
`SGS-THOMSON/M2716` (18000 → 25000), `SGS-THOMSON/M2732A` (18000 → 21000), `ST/M2716` (18000 →
25000), `ST/M2732A` (18000 → 21000).

**What would close each:** the two `INTEL` rows need Intel's own 2716 and 2732 datasheets,
vendored and git-tracked, so the inherited figure can finally be checked against the vendor it
claims. The four `SGS-THOMSON`/`ST` rows need SGS-THOMSON's and ST's own datasheets for the
respective parts — none is vendored in this repository today, and the value on each of those four
rows is an Intel-sourced figure applied to a different vendor's part with no vendor-specific
backing.

**Consequence of leaving them:** an Intel reading applied to four non-Intel parts is exactly the
silent cross-application D-02 exists to make visible. It is now visible — each entry's `note` field
says so in plain language — but it is not yet fixed. Closing all six requires six additional
datasheets; the entries stay in the database with their honest `UNSOURCED` marker until then.

---

## v1.20 — Protocol-Only Dispatch — Remove the Legacy `mem_type` Axis (SHIPPED 2026-07-02)
```

**Verification recorded before the revert** (re-runnable by the orchestrator after applying):
`grep -qE "^### Phase 999\.(69|70|71):"` all three found; `grep -c '^### Phase '` rose from 174 to
177 (exactly +3, zero lost); `grep -qF` for `MEASURED`, `INFERRED`, `DIP32_27C020`, `UNSOURCED`,
`197-PULSE-INVENTORY.md` all found.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **PULSE-01 is fully answered**: the finding is written down at `tools/DECODE-NOTES.md` § 8, the
  decode rule is confirmed, and the wire-semantics argument (which datasheet number to carry when a
  part gives two) is recorded for phases 198/199/200 to reuse.
- **D-12's inventory obligation is closed**: `197-PULSE-INVENTORY.md` records every row this phase
  did not correct, with a reproducible method and a verdict each.
- **Both stale claims this phase falsified are corrected**: `DECODE-NOTES.md` § 5 and the
  field-inventory golden's `meta` block.
- **The orchestrator must apply the `## ROADMAP edits for the orchestrator to apply` section above**
  to `.planning/ROADMAP.md` before this plan's backlog obligations are fully discharged in that
  file. The verbatim text and anchor are self-contained and independently re-verifiable.
- **999.70 is a live safety-adjacent finding** or the next phase working gh#70 (a PULSE-04-style
  plan) should read before drafting any public answer — the pinout question is unresolved and the
  earlier published gh#70 cross-check is now known to rest on the wrong part's datasheet.
- No blockers. Full Python 3.11 suite confirmed green (2065 passed, 32 snapshots, 0 failed) after
  every edit in this plan.

## Self-Check: PASSED

- FOUND: `.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-PULSE-INVENTORY.md`
- FOUND: `firestarter_app/tools/DECODE-NOTES.md` (section 8 present, sections 0-7 intact)
- FOUND: `firestarter_app/tests/golden/chip_database_field_inventory.json` (parses; `why_no_regen_diff_tool` present, `diff_db` absent)
- FOUND: `.planning/todos/completed/derive-away-max-27c020-size-hardcode.md`; absent from `pending/`
- FOUND commit: `meta@f43c3e67`
- FOUND commit: `firestarter_app@0372cc6`
- FOUND commit: `meta@af0f70d1`
- FOUND commit: `meta@59481654`
- FOUND commit: `meta@b7ae2cbe`
- FOUND commit: `meta@d883d9f6`
- FOUND commit: `meta@2d331286`
- Both `firestarter_app` and meta repo HEAD confirmed on `v1.40-program-parameter-fidelity`
- Gitlink in meta repo confirmed pointing at `firestarter_app@0372cc6`
- Full Python 3.11 suite re-run after all edits: `2065 passed, 32 snapshots passed, 0 failed`
- `.planning/ROADMAP.md` confirmed reverted to its pre-plan state: `git diff --stat` against
  `af0f70d1` (post-gitlink-advance, pre-Task-3) shows zero diff; phase-heading count back to 174
- `.planning/STATE.md` confirmed untouched (`git diff --stat` empty)

---
*Phase: 197-the-override-mechanism-and-the-program-pulse*
*Completed: 2026-09-18*
