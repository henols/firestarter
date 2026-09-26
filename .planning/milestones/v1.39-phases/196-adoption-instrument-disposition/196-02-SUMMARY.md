---
phase: 196-adoption-instrument-disposition
plan: 02
subsystem: docs
tags: [retirement, gsd-planning, meta-repo-bookkeeping, requirements-sync]

# Dependency graph
requires:
  - phase: 196-01
    provides: ".planning/notes/adoption-instrument-retirement.md, the durable record every edit in this plan points at"
provides:
  - "CLAUDE.md § Repository Structure corrected to one tools/ occupant, plus a dated retirement paragraph"
  - "PROJECT.md's third-item paragraph no longer claims the instrument still runs"
  - "REQUIREMENTS.md INSTR heading and INSTR-01 text reworded to the settled disposition; both traceability rows left Pending"
  - "ROADMAP.md Phase 196 success criteria 1 and 3 reworded to the settled disposition"
  - "One appended annotation inside the seed's frozen FIRED banner, naming the retirement date and the note's path"
affects: [196-03-plan]

# Actuals (#2632)
actuals:
  tokens: 1383
  tasks: 3
  commits: 1

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Cite a self-falsifying act by date, never by sha, when the citing document cannot reference its own commit (mirrors the CLAUDE.md tools/wiki/ and source-comment-rule precedents already in the file)"
    - "Describe a retired artifact, never name its path or filename, in any live document a residual-reference gate scans"

key-files:
  created: []
  modified:
    - CLAUDE.md
    - .planning/PROJECT.md
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/seeds/SEED-claim-firestarter-slug.md

key-decisions:
  - "Task 3's SEED-AT-CANONICAL-PATH verify leg, as written in the plan, has a substring-match bug: `case \"$ST\" in R*|*D*)` tests the whole porcelain-status line against `*D*`, and the filename `SEED-claim-firestarter-slug.md` itself contains an uppercase `D` (from `SEED`), so the leg fails on every valid modified-not-renamed-not-deleted status regardless of the actual git status code. Verified the true status code is ` M` (modified, first two porcelain characters only) via `git status --porcelain -- \"$S\" | cat -A`, confirmed it is neither `R*` nor `D*` when read correctly, and treated the acceptance criterion (\"never as renamed or deleted\") as satisfied on that corrected reading rather than editing the plan's verify script. See Deviations."
  - "CLAUDE.md's surviving tools/ bullet was left as a one-item list rather than folded into the count sentence — the acceptance criteria required only that the count read 'holds one directory' and that tools/catalog/'s description survive, and a list-of-one reads more consistently with the file's existing bullet style than an inline fold would."
  - "The retirement paragraph and the seed annotation both cite `.planning/notes/adoption-instrument-retirement.md` by path and 2026-09-17 by date, with zero SHAs anywhere near either citation, per D-06/R4's date-not-sha rule and this plan's own CITED-BY-DATE-NOT-SHA check."

requirements-completed: []

coverage:
  - id: D1
    description: "CLAUDE.md's repository-structure inventory is corrected (one tools/ occupant, tools/catalog/ description intact) and carries a dated, path-citing, SHA-free retirement paragraph; the tools/wiki/ paragraph and heading count are byte-identical to before"
    requirement: "INSTR-02"
    verification:
      - kind: other
        ref: "196-02-PLAN.md Task 1 <verify> automated legs: CLAUDE-SWEPT, CITED-BY-DATE-NOT-SHA, CLAUDE-UNTOUCHED-ELSEWHERE"
        status: pass
    human_judgment: false
  - id: D2
    description: "PROJECT.md's third-item paragraph no longer claims the instrument still runs, points at the retirement note, and every hunk falls inside the paragraph's own line band"
    requirement: "INSTR-02"
    verification:
      - kind: other
        ref: "196-02-PLAN.md Task 1 <verify> automated legs: PROJECT-SWEPT, PROJECT-SCOPE-OK"
        status: pass
    human_judgment: false
  - id: D3
    description: "REQUIREMENTS.md's INSTR heading and INSTR-01 text state the settled disposition with no path citation; INSTR-02's text and both Pending traceability rows are untouched"
    requirement: "INSTR-02"
    verification:
      - kind: other
        ref: "196-02-PLAN.md Task 2 <verify> automated legs: REQUIREMENTS-SWEPT, TRACEABILITY-STILL-PENDING"
        status: pass
    human_judgment: false
  - id: D4
    description: "ROADMAP.md criterion 1 states the settled disposition and points at the note; criterion 3 records that its antecedent is false; the plans line is unedited; every hunk falls inside the Phase 196 block"
    requirement: "INSTR-02"
    verification:
      - kind: other
        ref: "196-02-PLAN.md Task 2 <verify> automated legs: ROADMAP-SWEPT, ROADMAP-SCOPE-OK"
        status: pass
    human_judgment: false
  - id: D5
    description: "The seed gained exactly one appended annotation inside its FIRED banner, removed nothing, stayed at its canonical path, and one attribution-free commit on the milestone branch carries exactly the five swept documents"
    requirement: "INSTR-02"
    verification:
      - kind: other
        ref: "196-02-PLAN.md Task 3 <verify> automated legs: SEED-APPEND-ONLY, SEED-AT-CANONICAL-PATH (corrected reading, see Deviations), SWEEP-COMMIT-SCOPE-OK"
        status: pass
    human_judgment: true
    rationale: "The plan's own <verification> section names two properties no automated leg can reach: (1) semantics — that none of the five edited passages reads as though the instrument still gates a live claim, which needs a human read as a reader who knows nothing about this phase; (2) register — that the seed's annotation matches the FIRED banner's flat, outward-pointing voice. Both are asserted true in this SUMMARY on my own read, but a second read by a human is the honest classification for a semantic/register property."

duration: 20min
completed: 2026-09-17
status: complete
---

# Phase 196 Plan 02: Live-Document Retirement Sweep Summary

**Reworded five live documents — CLAUDE.md, PROJECT.md, REQUIREMENTS.md, ROADMAP.md, and one annotation on the frozen slug-claim seed — so none of them still describes the PyPI per-version download-share instrument as a live open choice or as gating an already-fired claim.**

## Performance

- **Duration:** ~20 min
- **Tasks:** 3 completed
- **Files modified:** 5

## Accomplishments

- `CLAUDE.md` § Repository Structure now reads `tools/` holds one directory, keeps `tools/catalog/`'s description untouched, and carries a new retirement paragraph — final wording, verbatim:

  > The PyPI per-version download-share instrument measured whether it was safe to claim the
  > `henols/firestarter` slug. The operator retired it on 2026-09-17, after the claim had already been
  > made without the trigger being met. The reason is recorded at
  > `.planning/notes/adoption-instrument-retirement.md`. **No instrument measures that download split
  > now.**

  The `tools/wiki/` paragraph, the source-comment paragraph, and every heading count are byte-identical to the pre-plan commit.
- `.planning/PROJECT.md`'s third-item paragraph no longer claims the instrument still runs; it now reads (final wording, verbatim, only the last sentence changed from history):

  > The third item is bookkeeping the v1.38 close left behind: the PyPI per-version download-share
  > instrument was built to measure whether it was safe to claim `henols/firestarter`. The operator
  > claimed it on 2026-09-14 with the trigger unmet, and the seed is `status: fired`. The instrument was
  > retired on 2026-09-17; the reason is recorded at
  > `.planning/notes/adoption-instrument-retirement.md`.

- `.planning/REQUIREMENTS.md` INSTR section heading, reworded (final wording, verbatim):

  > ### INSTR — the adoption instrument is retired, with its reason recorded (v1.38 carry-over)

  INSTR-01 text, reworded (final wording, verbatim):

  > - [ ] **INSTR-01**: The PyPI per-version download-share instrument is removed. The disposition is
  >       recorded with its reason.

  INSTR-02's text is byte-identical to before. Both traceability rows still read `Pending`.
- `.planning/ROADMAP.md` Phase 196 success criterion 1 reworded to the settled disposition and now points at the retirement note by path; criterion 3 gained one appended sentence — final wording, verbatim: `The instrument was not retained, so this criterion is vacuously satisfied and no consumer is named.` The `**Plans:** 3 plans` line was left untouched, as instructed.
- The seed's FIRED banner gained exactly one appended line, alongside the two annotation lines it already ended with — final wording, verbatim:

  > The instrument was retired on 2026-09-17; see `.planning/notes/adoption-instrument-retirement.md`.

  `trigger_condition` and § "Why the trigger is what it is" are byte-identical to before; the diff for this file removes zero lines.
- One commit, `9a3be9c6`, on `v1.39-protocol-0x05-write-correctness`, carries exactly the five paths this plan edits, staged individually. Commit-scope anchor: the plan ledger `gsd-plan-head-before-196-02`, value `d964d0f67335644d4a62b8e81408a2741495b48a` (HEAD immediately before this plan's first commit; Tasks 1 and 2 made no commit of their own, so this is also the true pre-task-1 HEAD).

## Task Commits

1. **Task 1: CLAUDE.md and PROJECT.md — the inventory the deletion falsified, and the paragraph that says the instrument still runs** — no commit (plan design: staged with Task 3's single commit)
2. **Task 2: REQUIREMENTS.md and ROADMAP.md — the closed choice that four live lines still describe as open** — no commit (plan design: staged with Task 3's single commit)
3. **Task 3: The seed — one appended annotation, nothing rewritten, and the sweep commit** — `9a3be9c6` (docs)

**Plan metadata:** committed separately below (see `git_commit_metadata` step).

## Files Created/Modified

- `CLAUDE.md` — corrected `tools/` occupant count, dropped the `tools/adoption/` bullet, added the dated retirement paragraph
- `.planning/PROJECT.md` — third-item paragraph's closing sentence reworded from present-tense "still runs and still reports" to the retirement fact and the note's path
- `.planning/REQUIREMENTS.md` — INSTR section heading and INSTR-01 text reworded to the settled disposition; INSTR-02 and both `Pending` traceability rows untouched
- `.planning/ROADMAP.md` — Phase 196 success criteria 1 and 3 reworded; the `**Plans:**` line untouched
- `.planning/seeds/SEED-claim-firestarter-slug.md` — one line appended inside the FIRED banner; `trigger_condition` and the "Why the trigger is what it is" section untouched

## Decisions Made

- All five edits describe the retired artifact by its function ("the PyPI per-version download-share instrument"), never by its path or filename, per the plan's residual-reference rule — this is the one recurring cost the plan calls out in advance, and it reads slightly more verbose in each of the five passages than naming the script directly would, which is the accepted trade.
- The commit-scope anchor was read from the existing plan ledger written before Task 1 began (no separate anchor file created), per the plan's explicit instruction to reuse `gsd-plan-head-before-196-02` rather than invent a second one.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug in the plan's own verify script] `SEED-AT-CANONICAL-PATH`'s case-statement matches the filename's own letters, not the git status code**

- **Found during:** Task 3, first run of the `SEED-AT-CANONICAL-PATH` automated verify leg
- **Issue:** The leg as written computes `ST="$(git status --porcelain -- "$S")"` — a full porcelain line including the filename — and tests it with `case "$ST" in R*|*D*) ... ;; esac`. The intent is to catch a rename (`R`) or deletion (`D`) status code, which git places in the first one or two characters of the line. But `*D*` is a substring match over the *entire* string, and the filename itself, `SEED-claim-firestarter-slug.md`, contains an uppercase `D` (from `SEED`). So the leg fails on every legitimate `M` (modified) status for this specific file, regardless of the actual status code, because the glob matches the filename rather than the status prefix.
- **Fix:** Verified the actual git status directly with `git status --porcelain -- "$S" | cat -A`, confirming the real code is `" M"` (modified, not renamed, not deleted). Re-ran the leg's intent with a corrected extraction (`CODE="${ST:0:2}"` before the `case`), which passed. Did not edit `196-02-PLAN.md` — the plan file is not a target of this plan's `<files>` and editing a verify script after the fact would be exactly the kind of "re-scope the proof to reach green" this plan is explicitly forbidden from doing (Task 3's own prohibition list). Treated the acceptance criterion itself — "never as renamed or deleted" — as satisfied on the corrected reading, and recorded the leg's defect here rather than silently.
- **Files modified:** None (verification-only; no plan or product file was changed to fix this)
- **Verification:** `git status --porcelain -- .planning/seeds/SEED-claim-firestarter-slug.md` reports ` M .planning/seeds/SEED-claim-firestarter-slug.md` — first two characters `" M"`, matching neither `R*` nor `D*`
- **Committed in:** N/A — a verification-logic observation, not a code change

---

**Total deviations:** 1 auto-fixed (1 bug in the plan's own verify tooling, worked around by direct git-status inspection rather than by editing the plan)
**Impact on plan:** None on scope or deliverables. All nine other automated legs across all three tasks passed as literally written; this one leg's intent (prove the seed was modified, not renamed or deleted) is independently confirmed true.

## Issues Encountered

None beyond the deviation above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 196-03 can now run the graph rebuild and the INSTR-02 proof expression: all four live documents the expression scans (`CLAUDE.md`, `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`) have had their residual references removed, per this plan's `CLAUDE-SWEPT`, `PROJECT-SWEPT`, `REQUIREMENTS-SWEPT` and `ROADMAP-SWEPT` tokens.
- Both `INSTR-01` and `INSTR-02` traceability rows still read `Pending` — confirmed by `TRACEABILITY-STILL-PENDING` — and are left for Plan 196-03 to flip, once the proof is green and the graph is rebuilt.
- The pre-task SHA used for this plan's own commit-scope assertion is `d964d0f67335644d4a62b8e81408a2741495b48a`, recorded in the plan ledger `gsd-plan-head-before-196-02` in the git directory (untracked by construction, invisible to any proof reading of tracked files).
- The seed's own two frozen sites (`trigger_condition` and § "Why the trigger is what it is") remain unedited and out of scope for Plan 196-03 by design (D-14).

## Self-Check: PASSED

- `[ -f CLAUDE.md ]` → FOUND
- `[ -f .planning/PROJECT.md ]` → FOUND
- `[ -f .planning/REQUIREMENTS.md ]` → FOUND
- `[ -f .planning/ROADMAP.md ]` → FOUND
- `[ -f .planning/seeds/SEED-claim-firestarter-slug.md ]` → FOUND
- `git log --oneline --all --grep="196-02"` — no plan-tagged commit yet at self-check time (Task 3's commit predates this SUMMARY's own commit and uses the sweep subject, not a `196-02` grep token); commit `9a3be9c6` verified directly by `git cat-file -e 9a3be9c6` → FOUND
- All 12 required verification tokens confirmed present in this session's tool output: `CLAUDE-SWEPT`, `CITED-BY-DATE-NOT-SHA`, `CLAUDE-UNTOUCHED-ELSEWHERE`, `PROJECT-SWEPT`, `PROJECT-SCOPE-OK`, `REQUIREMENTS-SWEPT`, `TRACEABILITY-STILL-PENDING`, `ROADMAP-SWEPT`, `ROADMAP-SCOPE-OK`, `SEED-APPEND-ONLY`, `SEED-AT-CANONICAL-PATH` (corrected reading), `SWEEP-COMMIT-SCOPE-OK`

---
*Phase: 196-adoption-instrument-disposition*
*Completed: 2026-09-17*
