---
phase: 195-partial-writes-stop-destroying-the-page
plan: 04
subsystem: docs-and-process
tags: [flash4, protocol-0x05, decision-record, todos, validated-eproms, gitlink]

requires:
  - phase: 195-partial-writes-stop-destroying-the-page
    provides: "the software evidence from plans 01-03: the two-layer refusal (catalog id, firmware guard, host predicate), the full native/host rejection matrices, and the criterion-4 regression-surface measurements"
provides:
  - "the phase's decision record at .planning/v1.39/195-partial-write-refusal-record.md, citing the two RAM measurements (142B/213B) and the payload-length gap that forced the refusal shape"
  - "three pending todos naming the deferred strands and their measured grounds: host-side alignment splicing, the override-flag output contract, and the dev-test write-region rounding"
  - "a VALIDATED-EPROMS.md Notes bullet recording the SST39SF020 scope correction, proven to round-trip through the ledger's own write/check"
  - "a scope-correction comment posted on the originating issue (henols/firestarter_prom#68)"
  - "both meta-repo gitlinks advanced to the commits plans 01-03 produced"
affects: [195-05]

actuals:
  tokens: 5300
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Phase decision record as a first-class project artifact under .planning/v1.39/, separate from plan text, so the reasoning behind a fix shape survives the phase closing"
    - "Deferred-capability todos filed with the measured grounds that justify them, not just a one-line TODO"

key-files:
  created:
    - .planning/v1.39/195-partial-write-refusal-record.md
    - .planning/todos/pending/host-side-page-alignment-splicing.md
    - .planning/todos/pending/protocol-0x05-write-override-flag-output-contract.md
    - .planning/todos/pending/dev-test-write-region-rounds-to-page-size.md
  modified:
    - VALIDATED-EPROMS.md
    - firestarter_fw
    - firestarter_app

key-decisions:
  - "The record's frontmatter states plainly what it is authoritative for (the fix-shape decision, the two measurements, the scope correction) and what it is not (any silicon behavior), with a pairs_with pointer to the bench transcript plan 05 will produce -- following the 194-page-size-27-row-record.md precedent's evidence-class discipline."
  - "The three todos are filed with resolves_phase left unassigned, per the plan's own instruction, since none of them is scheduled work yet -- they are filed so the capability loss and the two other deferred decisions are actionable rather than lost when the phase seals."
  - "The ledger Notes bullet is additive only -- the pre-task sha256 of VALIDATED-EPROMS.md was verified against the value the plan's own repository-mechanics section recorded before any edit, and a write-then-check round trip after the edit confirms the generated table is byte-identical (27 rows, unchanged) and the new bullet survived because it lives in the one section the generator preserves verbatim."
  - "Gitlink advance verified with git submodule status (no +/- prefix means the recorded commit matches HEAD exactly) and git status --ignore-submodules=dirty (empty), because a plain git status -- firestarter_fw firestarter_app reports firestarter_app as modified purely due to three untracked datasheet PDFs left by a concurrent session -- unrelated to this plan's work, not staged, not touched."

requirements-completed: []
# Per this plan's own prohibitions: WRITE-01, WRITE-02 and WRITE-03 are NOT marked Complete here.
# The milestone requires bench validation on real silicon and a green native/host test suite is
# explicitly not sufficient (D-4); the requirement flips belong to the bench plan (195-05) that
# produces the silicon evidence.

coverage:
  - id: D1
    description: "The phase decision record exists with six sections, states the fix shape and its two forcing measurements (142B uno / 213B leonardo remaining RAM; firmware never learns payload length), labels the interior chunk-boundary loss direction as derived and never observed, states the SST39SF020 scope correction and the 25/2 dev-test partition, and states plainly what it does not prove"
    requirement: "WRITE-01"
    verification:
      - kind: other
        ref: "cd /workspaces && grep-based RECORD-COMPLETE / RECORD-HONEST checks from the plan's own <verify> block, re-run against the committed file"
        status: pass
    human_judgment: false
  - id: D2
    description: "Three pending todos filed with measured grounds (host-side alignment splicing, override-flag output contract, dev-test region rounding), and a VALIDATED-EPROMS.md Notes bullet recording the SST39SF020 correction, proven to round-trip through the ledger's write/check commands with the generated table byte-identical"
    requirement: "WRITE-02"
    verification:
      - kind: other
        ref: "cd /workspaces && for-loop TODOS-FILED check; python3 .claude/skills/devtest-triage/scripts/eprom_ledger.py write && check -> LEDGER-ROUNDTRIP-OK; git diff --stat -- VALIDATED-EPROMS.md == 4 insertions only"
        status: pass
    human_judgment: false
  - id: D3
    description: "A scope-correction comment posted on the originating issue (no fix/release claim, no label, no close), and both meta-repo gitlinks advanced to the commits plans 01-03 produced, from branches confirmed clean of tracked-file changes on the milestone branch"
    requirement: "WRITE-03"
    verification:
      - kind: other
        ref: "gh issue comment 68 -R henols/firestarter_prom (https://github.com/henols/firestarter/issues/68#issuecomment-5697049024); git submodule status + git rev-parse HEAD:<submodule> == git -C <submodule> rev-parse HEAD for both sub-repos"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-09-16
status: complete
---

# Phase 195 Plan 04: The decision record, three deferred strands, and the gitlink advance Summary

**The refusal's reasoning survives the phase as a project record citing the 142B/213B RAM measurements and the payload-length gap that forced it; the capability it costs is filed as three actionable todos; the SST39SF020 scope correction is recorded in the ledger's Notes and posted to the originating issue; and both meta-repo gitlinks now name the commits plans 01-03 produced.**

## Performance

- **Duration:** 35 min
- **Started:** 2026-09-16 (continuing from plans 01-03 on the same branch)
- **Completed:** 2026-09-16
- **Tasks:** 3
- **Files modified:** 6 (4 created, 2 gitlink pointers advanced) plus 1 comment on an external issue tracker

## Accomplishments

- `.planning/v1.39/195-partial-write-refusal-record.md` written: six sections covering the defect
  mechanism and the two deliberately-kept clauses (D-09), the three loss directions with direction
  3 explicitly labelled derived-and-never-observed (D-06), the fix shape with its two forcing
  measurements (D-01), the capability cost and the strand that would restore it (D-03), criterion
  4 as measured including the SST39SF020 correction and the 25/2 dev-test partition (D-07, D-12),
  and a closing section stating plainly that the record proves no silicon behavior.
- Three todos filed under `.planning/todos/pending/`: `host-side-page-alignment-splicing.md` (the
  read-splice-write strand, its three tractability facts, and its two honest caveats),
  `protocol-0x05-write-override-flag-output-contract.md` (what would close the override request --
  a decided output contract, not the flag), and `dev-test-write-region-rounds-to-page-size.md`
  (the 25/2 partition and the proposal to round the fixed region to the page size).
- `VALIDATED-EPROMS.md`'s `## Notes` section gained a bullet recording that `SST39SF020` is
  `algorithm: 6`, outside the protocol `0x05` write path's blast radius entirely -- proven to
  survive a `write` + `check` round trip with the validated-chips table byte-identical (27 rows,
  unchanged; diff is 4 insertions in `## Notes` only).
- A scope-correction comment posted on the originating issue,
  https://github.com/henols/firestarter/issues/68#issuecomment-5697049024 -- states the
  `SST39SF020` correction and the `AE29F2008`/`W29C020` two-name silicon identity, claims no fix
  and no release, attaches no label, closes nothing.
- Both meta-repo gitlinks advanced: `firestarter_fw` `c2b8baa` → `b32d1adf` (plans 01-02),
  `firestarter_app` `3140172` → `2acf5d3` (plans 01-03), each confirmed via `git submodule status`
  (no `+`/`-` prefix) and `git rev-parse HEAD:<path>` equal to `git -C <path> rev-parse HEAD`.

## Task Commits

Each task was committed atomically, in the meta repo on `v1.39-protocol-0x05-write-correctness`:

1. **Task 1: The phase record -- the decision, its measured grounds, and what it costs** - `ac465a74` (docs)
2. **Task 2: File the three deferred strands and record the scope correction in the ledger** - `911d4fb1` (docs)
3. **Task 3: Carry the scope correction back to the originating issue, and advance both gitlinks** - `0eff7fa8` (chore)

**Plan metadata:** this SUMMARY commit, meta repo.

## Files Created/Modified

- `.planning/v1.39/195-partial-write-refusal-record.md` -- the phase decision record, six sections
- `.planning/todos/pending/host-side-page-alignment-splicing.md` -- the deferred host-side alignment strand
- `.planning/todos/pending/protocol-0x05-write-override-flag-output-contract.md` -- the deferred override-flag decision
- `.planning/todos/pending/dev-test-write-region-rounds-to-page-size.md` -- the deferred dev-test region proposal
- `VALIDATED-EPROMS.md` -- `## Notes` gained the `SST39SF020` scope-correction bullet (generated table unchanged)
- `firestarter_fw` (gitlink) -- advanced `c2b8baa` → `b32d1adf`
- `firestarter_app` (gitlink) -- advanced `3140172` → `2acf5d3`

## Decisions Made

- **The record's frontmatter states an explicit authority boundary** (what it proves vs. what the
  bench transcript must prove), matching the evidence-class discipline `194-page-size-27-row-record.md`
  established, rather than presenting a uniform confidence level across every section.
- **All three todos leave `resolves_phase: unassigned`**, per the plan's own instruction -- none is
  scheduled work, they exist so the capability loss and the two other deferred decisions are
  visible and actionable rather than silently absorbed when the phase seals.
- **The ledger edit round-trips**: `eprom_ledger.py write` then `check` both exit 0 after the Notes
  addition, and the validated-chips table is byte-identical (27 rows before and after) -- the edit
  lives entirely inside the one section the generator preserves verbatim.
- **Gitlink cleanliness was verified two ways** because a plain `git status -- firestarter_fw
  firestarter_app` reports `firestarter_app` as modified. `git submodule status` (no `+`/`-`
  prefix -- the checked-out commit matches the recorded gitlink exactly) and `git status
  --ignore-submodules=dirty` (empty) both confirm this is not a tracked-file or gitlink problem;
  it is three untracked datasheet PDFs (`datasheets/LST62832I.pdf`, `datasheets/MBM27128.pdf`,
  `datasheets/MBM27C4001.pdf`) left by the concurrent session mentioned in this plan's
  repository-mechanics briefing. They were not staged, not committed, and not touched, per the
  standing instruction to leave other sessions' working-tree changes alone.

## Deviations from Plan

### Auto-fixed Issues

None — no bugs, missing critical functionality, or blocking issues were found in this plan's own
work.

---

**Total deviations:** 0.
**Impact on plan:** None on scope.

## Issues Encountered

- **`firestarter_app` carries three untracked datasheet PDFs from a concurrent session**, making a
  literal `git status --porcelain -- firestarter_fw firestarter_app` report `firestarter_app` as
  modified even after the gitlink advance committed cleanly. Verified via `git submodule status`
  (gitlink matches HEAD exactly) and `git status --ignore-submodules=dirty` (empty) that this is
  untracked noise, not a tracked-file or gitlink defect. The files were left untouched, per the
  standing instruction not to stage or delete another session's working-tree changes. This does
  not affect the correctness of the gitlink advance: a submodule pointer records a commit hash,
  not a working-tree snapshot, and both submodules' HEAD commits contain exactly this phase's
  plans 01-03 work with no uncommitted tracked-file changes.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The phase's reasoning, cost, and scope correction are now project records rather than only plan
  text: `.planning/v1.39/195-partial-write-refusal-record.md` is the citable record, three pending
  todos make the deferred strands actionable, and `VALIDATED-EPROMS.md`'s Notes carries the
  `SST39SF020` correction where a reader of the validated-parts ledger will meet it.
- Plan 05 (bench evidence on `W29C020`) can proceed against this foundation. The record's
  `pairs_with` field already points at the bench transcript path plan 05 will produce.
- Per this plan's own prohibitions: `WRITE-01`, `WRITE-02` and `WRITE-03` are deliberately **NOT**
  marked Complete in `REQUIREMENTS.md` — confirmed untouched (`git status --porcelain --
  .planning/REQUIREMENTS.md` empty). The requirement flips belong to plan 05, once silicon
  evidence exists.
- `.planning/STATE.md` and `.planning/ROADMAP.md` were deliberately not touched — the orchestrator
  owns those writes after the wave completes.
- Both meta-repo gitlinks now name commits reachable from each sub-repo's current branch head, so
  the phase's software evidence (plans 01-03) is reproducible from the meta repo alone.

---
*Phase: 195-partial-writes-stop-destroying-the-page*
*Completed: 2026-09-16*

## Self-Check: PASSED

- All 4 created key files confirmed present on disk with `[ -f ]`.
- All 3 production commits confirmed present via `git log --oneline --all` in the meta repo:
  `ac465a74`, `911d4fb1`, `0eff7fa8`.
- All task-level `<acceptance_criteria>` re-run and passing: RECORD-COMPLETE, RECORD-HONEST
  (Task 1); TODOS-FILED, LEDGER-ROUNDTRIP-OK, table diff confined to 4 insertions in `## Notes`
  (Task 2); GITLINKS-ADVANCED, REQS-UNTOUCHED, and the submodule-porcelain check re-verified with
  `--ignore-submodules=dirty` given the documented untracked-file caveat (Task 3).
- Plan-level `<verification>` re-run: the record carries six sections and every measured token;
  both gitlinks equal their sub-repo branch heads from tracked-clean trees on the milestone
  branch; `.planning/REQUIREMENTS.md` shows no diff.
