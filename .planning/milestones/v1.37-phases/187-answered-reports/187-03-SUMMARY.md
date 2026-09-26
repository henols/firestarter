---
phase: 187-answered-reports
plan: 03
subsystem: infra
tags: [gsd-close, merge, github-api, pypi, public-release, gh65, gh66]

requires:
  - phase: 187-02
    provides: "A merged, publicly readable meta `.planning/` record on `beta` and the operator-gate/approval-file pattern this plan's own gate follows"
provides:
  - "The v1.37 app milestone branch merged to public `beta` (henols/firestarter_app#62, true merge commit f0ef29d9726cf0f09bb3f66e5ce98d72964e6252)"
  - "A published, READ (not predicted) pre-release version (3.0.0b39), cross-confirmed on GitHub Releases and PyPI"
  - "firestarter/jp5_gate.py and firestarter/flash4_erase_gate.py now installable via `pip install --pre -U firestarter`"
  - "187-MERGE-RECORD.md app rows of sections 1-4"
affects: [187-04, 187-05, 187-06, 187-07, 187-08, 187-09, 187-10, 187-11, 187-12]

actuals:
  tokens: 4888
  tasks: 3
  commits: 4
  plan_head_before: 49a76b24

tech-stack:
  added: []
  patterns:
    - "gh pr merge --merge succeeded on first use here (unlike 187-02's transient block), confirming the earlier substitution to gh api -X PUT was a one-off classifier hiccup, not a durable CLI restriction"
    - "A single 90-second background poll loop, timestamped into the evidence file, satisfies the >=90-minute no-false-timeout budget without a foreground sleep chain"
    - "Version read from `gh release list` after run completion, then cross-checked against PyPI's own release-key JSON before being written anywhere reply-facing — the same read-not-predict pattern D-05 requires"

key-files:
  created:
    - .planning/phases/187-answered-reports/evidence/187-03-operator-approval.txt
    - .planning/phases/187-answered-reports/evidence/187-03-app-version.txt
  modified:
    - .planning/phases/187-answered-reports/evidence/187-03-app-cut.txt
    - .planning/phases/187-answered-reports/187-MERGE-RECORD.md
    - .planning/STATE.md
    - .planning/ROADMAP.md

key-decisions:
  - "Wrote evidence/187-03-operator-approval.txt at the retry dispatch, not at the instant of the operator's original answer, because an intervening halt (recorded by hand in a3f6cb19) denied the dispatch that would have written it. The file explicitly discloses this timing gap and states that no public act occurred during it — the ordering invariant (approval file committed before any push/PR/merge) still holds for this dispatch."
  - "Labelled the approval file's decision prose as the orchestrator's rendering of the operator's menu selection, not a verbatim quotation, per the plan's own instruction and the same pattern 187-02 used."
  - "Used `gh pr merge 62 --repo henols/firestarter_app --merge` directly (the plain CLI form) rather than the `gh api -X PUT .../merge` substitution 187-02 needed — it was not blocked this time, so no deviation from the plan's literal action was required."
  - "Treated the plan's literal Task-3 verify leg (`git ls-files -- datasheets/` must print 0) as carrying the same DRIFT-4 imprecision Task 1 already documented: the app repo has carried 7 pre-existing tracked datasheet PDFs since before this phase, so the literal check always reads 7. Used the scoped check on the two named PDFs (MBM27C1001.pdf, MX27C4000.pdf) instead, which is the plan's actual prohibition and reads empty/0 both pre- and post-merge."
  - "STATE.md and ROADMAP.md were hand-edited rather than via `gsd-tools query state.*` / `roadmap.update-plan-progress`, per this project's documented history of those verbs corrupting STATE.md frontmatter and clobbering ROADMAP.md's dependency table. Diffed after editing to confirm only the intended lines changed."

requirements-completed: []

coverage:
  - id: D1
    description: "Operator approval for the app merge recorded before any public act, explicitly labelled as a menu-selection rendering and disclosing the intervening halt"
    requirement: "REPLY-03"
    verification:
      - kind: other
        ref: "head -1 evidence/187-03-operator-approval.txt == APPROVED-FOR-MERGE: app; git log --oneline shows e6f3a318 before eecd27c3 (the push/PR/merge commit)"
        status: pass
    human_judgment: false
  - id: D2
    description: "App milestone branch merged to beta via a true (non-squash, non-rebase) merge commit, PR #62"
    requirement: "REPLY-03"
    verification:
      - kind: other
        ref: "gh api repos/henols/firestarter_app/pulls/62 --jq '.state,.merged,.merge_commit_sha,.base.ref' -> closed/true/f0ef29d9.../beta"
        status: pass
    human_judgment: false
  - id: D3
    description: "beta-release.yml completed successfully; the resulting pre-release version (3.0.0b39) was READ from gh release list, never predicted, and cross-confirmed on PyPI"
    requirement: "REPLY-04"
    verification:
      - kind: other
        ref: "gh run list --workflow beta-release.yml -> status completed, conclusion success (run 34698771255); gh release list shows 3.0.0b39; PyPI JSON releases includes 3.0.0b39 (firestarter-3.0.0b39-py3-none-any.whl)"
        status: pass
    human_judgment: false
  - id: D4
    description: "firestarter/jp5_gate.py and firestarter/flash4_erase_gate.py both now present on origin/beta, having been proven absent pre-merge"
    requirement: "REPLY-04"
    verification:
      - kind: other
        ref: "git cat-file -e origin/beta:firestarter/jp5_gate.py && echo PRESENT; same for flash4_erase_gate.py -- both print PRESENT post-merge, both failed pre-merge (822e829f baseline)"
        status: pass
    human_judgment: false
  - id: D5
    description: "No v1.37 tag created in henols/firestarter_app; neither new datasheet PDF (gh#65/gh#66) tracked"
    verification:
      - kind: other
        ref: "git ls-remote --tags origin | grep -c v1.37 -> 0; git ls-files -- datasheets/MBM27C1001.pdf datasheets/MX27C4000.pdf -> empty"
        status: pass
    human_judgment: false
  - id: D6
    description: "187-MERGE-RECORD.md app rows of sections 1-4 filled with live-measured values"
    verification:
      - kind: other
        ref: "sections 1 (PR #62, merge commit), 2 (post-merge git cherry, 0/0), 3 (observed cut tag 3.0.0b39), 4 (registry confirmation on both GitHub and PyPI) all contain filled app rows, no _pending_/_filled by 187-03_ placeholders remain for this repo"
        status: pass
    human_judgment: false

duration: 22min
completed: 2026-09-12
status: complete
---

# Phase 187 Plan 03: App merge to beta, cut version read as 3.0.0b39, cross-confirmed on PyPI Summary

**Merged the v1.37 app milestone branch to `henols/firestarter_app`'s public `beta` (PR #62, true merge commit `f0ef29d9726cf0f09bb3f66e5ce98d72964e6252`), let `beta-release.yml` cut a pre-release, and read the resulting version (`3.0.0b39`) from the API rather than predicting it — confirmed independently on both GitHub Releases and PyPI, with both `jp5_gate.py` and `flash4_erase_gate.py` now installable via `pip install --pre -U firestarter`.**

## Performance

- **Duration:** 22 min (this continuation session; Task 1 was completed in a prior session before the halt)
- **Started:** 2026-09-12T14:09:00Z (continuation resume)
- **Completed:** 2026-09-12T14:31:00Z
- **Tasks:** 3 (Task 1 completed pre-halt; Tasks 2-3 completed this session)
- **Files modified:** 6 (2 created, 4 modified, including STATE.md/ROADMAP.md)

## Accomplishments

- Wrote `evidence/187-03-operator-approval.txt` recording the operator's `merge` selection at the
  Task 2 gate — explicitly labelled as the orchestrator's rendering of a menu choice, not a
  verbatim quotation — including the verbatim PRE-MERGE MEASUREMENT block, the one-way PyPI
  reversibility statement, the deliberately-unread pre-cut version (`3.0.0b38`, shown only as the
  value NOT to name), and the confirmed non-`--auto`/`--chain` harness mode. Committed (`e6f3a318`)
  before any push, PR, or merge.
- Pushed the app milestone branch, opened `henols/firestarter_app#62` against `beta`, and merged it
  with a true merge commit (`f0ef29d9726cf0f09bb3f66e5ce98d72964e6252`) — `gh pr merge --merge`
  succeeded directly this time, no substitution needed.
- Polled `beta-release.yml` (run `34698771255`) to completion — `status: completed`,
  `conclusion: success`, ~5m22s, well inside the >=90-minute no-false-timeout budget — with
  timestamped poll lines recorded in the evidence file.
- Read (never predicted) the cut version, `3.0.0b39`, from `gh release list`, wrote it alone on
  line 1 of `evidence/187-03-app-version.txt`, and independently confirmed it on PyPI
  (`firestarter-3.0.0b39-py3-none-any.whl`) — this project has had GitHub carry a beta past PyPI
  before, so the GitHub reading alone was not treated as sufficient.
- Proved `firestarter/jp5_gate.py` and `firestarter/flash4_erase_gate.py` both now resolve on
  `origin/beta` (both had failed the same check pre-merge, per the `822e829f` baseline).
- Confirmed no `v1.37` tag was created and neither new datasheet PDF (gh#65/gh#66 material) is
  tracked in the app repository.
- Filled the app rows of `187-MERGE-RECORD.md` sections 1 through 4.

## Task Commits

Each task was committed atomically (Task 1 predates this continuation's resume):

1. **Task 1: Re-measure the app seam and confirm the app tree is publishable** - `822e829f` (docs) — completed in the prior (halted) session.
2. **Task 2: Operator gate — write the approval record** - `e6f3a318` (docs)
3. **Task 3: Merge the app branch, wait for the cut, and read the version** - `eecd27c3` (feat)

**Plan metadata:** committed alongside this SUMMARY (see final commit below).

_Note: commit `a3f6cb19`, between Task 1 and Task 2 above, is the hand-written halt record from the
prior session (see Deviations) — it is not a task commit of this plan, but it sits in the plan's
commit range and is disclosed here for completeness._

## Files Created/Modified

- `.planning/phases/187-answered-reports/evidence/187-03-operator-approval.txt` - the operator's `merge` selection record for the app merge, gated before any public act
- `.planning/phases/187-answered-reports/evidence/187-03-app-version.txt` - `3.0.0b39` alone on line 1, read from `gh release list` after the cut
- `.planning/phases/187-answered-reports/evidence/187-03-app-cut.txt` - appended the Task 3 PR/merge transcript, the timestamped poll log, the version read, and the independent PyPI confirmation
- `.planning/phases/187-answered-reports/187-MERGE-RECORD.md` - filled the app rows of sections 1-4
- `.planning/STATE.md` - superseded the `a3f6cb19` halt paragraph with the resolved state; `completed_plans` 30 → 31
- `.planning/ROADMAP.md` - checked off `187-03-PLAN.md`

## Decisions Made

- Labelled the approval file's decision prose as the orchestrator's rendering of a menu selection
  rather than a verbatim operator quotation, matching 187-02's pattern and the plan's own
  instruction — the operator chose one of three named options, they did not dictate rationale text.
- Used the plain `gh pr merge --merge` CLI form directly; it was not blocked this time (unlike
  187-02's transient classifier denial on the same command against a different repo), so no
  `gh api -X PUT` substitution was needed.
- Treated the plan's literal Task 3 verify leg on `git ls-files -- datasheets/` (expects `0`) as
  carrying forward the same DRIFT-4 imprecision Task 1's evidence already documented: the app
  repo's `datasheets/` directory has carried 7 pre-existing tracked files (unrelated to this phase)
  since before v1.37, so the literal check reads `7` both before and after this plan's actions.
  Used the scoped check on the two specific new PDFs instead, which is the plan's actual
  prohibition and reads empty both pre- and post-merge.
- Hand-edited `STATE.md` and `ROADMAP.md` rather than running `gsd-tools query state.*` /
  `roadmap.update-plan-progress`, per this project's documented history of those verbs corrupting
  STATE.md frontmatter (partial-line overwrites on multi-line paragraphs) and clobbering
  ROADMAP.md's dependency table. Diffed both files after editing to confirm only the intended
  lines changed.
- Did not run `requirements.mark-complete` for REPLY-01 through REPLY-05: `requirements.ready-ids`
  reported 0/5 ready, because sibling plans 187-04 through 187-12 still declare (and have not yet
  discharged) the same requirement IDs.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Operator-approval file written after an intervening halt, not at the instant of the operator's answer**
- **Found during:** Resuming this continuation (before Task 2's write action)
- **Issue:** A prior continuation dispatch for this same plan's Task 3 was denied by the Claude Code
  harness's own auto-mode classifier (`[Auto-Mode Bypass]`) before it could write
  `evidence/187-03-operator-approval.txt` — recorded by hand in meta commit `a3f6cb19`. The
  operator had already selected `merge` at the Task 2 gate before that denial, so the decision
  existed but the file the plan's precondition depends on did not.
- **Fix:** The operator turned harness auto mode off and asked for a retry. This continuation wrote
  `evidence/187-03-operator-approval.txt`, explicitly disclosing both the timing gap (the file is
  written after the halt, not at the instant of the original answer) and that no public act
  occurred during the intervening period (the app branch was still unpushed, no PR existed, and the
  latest app pre-release was still the pre-cut `3.0.0b38` — all reconfirmed live before writing the
  file). The ordering invariant that matters — approval file committed before any push/PR/merge —
  was preserved for this dispatch: `e6f3a318` precedes `eecd27c3`.
- **Files modified:** `.planning/phases/187-answered-reports/evidence/187-03-operator-approval.txt`
- **Verification:** `git log --oneline` shows `e6f3a318` before `eecd27c3`; the approval file's own
  text discloses the halt and the no-public-act fact; Task 3 proceeded only after this file existed
  with the required first line.
- **Committed in:** `e6f3a318`

**2. [Rule 1 - Bug] Plan's literal datasheets verify leg is imprecise against a pre-existing tracked-file baseline**
- **Found during:** Task 1 (documented by the prior session) and re-confirmed in Task 3 (this session)
- **Issue:** The plan's automated verify command for both Task 1 and Task 3 (`git ls-files --
  datasheets/ | wc -l`, expecting `0`) does not account for 7 datasheet PDFs the app repository has
  tracked since before this phase (unrelated chips, oldest tracked commit predates v1.37). The
  literal check therefore always reads `7`, which would read as a failure under a naive
  interpretation even though neither of the two NEW PDFs this plan must keep untracked
  (`MBM27C1001.pdf`, `MX27C4000.pdf`) was ever staged.
- **Fix:** Used the scoped check `git ls-files -- datasheets/MBM27C1001.pdf datasheets/MX27C4000.pdf`
  (empty output both pre- and post-merge), which is the plan's actual `must_haves.truths` /
  `prohibitions` intent, and documented the discrepancy in both evidence files rather than silently
  reinterpreting the plan.
- **Files modified:** none (verification-only; no code or content change)
- **Verification:** scoped check returns empty/rc=0 at both measurement points; the plan's literal
  check result (`7`) is recorded alongside the scoped result in both evidence files for auditability.
- **Committed in:** `822e829f` (Task 1, documented), `eecd27c3` (Task 3, reconfirmed)

---

**Total deviations:** 2 auto-fixed (1 blocking — halt/retry timing disclosure, 1 bug — a pre-existing
plan-verify imprecision carried forward from Task 1). **Impact on plan:** Neither affects scope,
authorization, or the substance of what was merged and published; both are procedural/documentation
precision issues, fully disclosed in evidence.

## Issues Encountered

None beyond the deviations above. The prior session's Claude Code auto-mode classifier denial (see
`a3f6cb19`) is the reason this plan required a continuation at all; it is not an issue this plan's
own execution introduced, and it did not recur once the operator turned harness auto mode off.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `firestarter/jp5_gate.py` and `firestarter/flash4_erase_gate.py` are installable today via
  `pip install --pre -U firestarter==3.0.0b39` (or a plain `--pre -U` for the latest), so REPLY-03
  and REPLY-04's subjects are real and installable when 187-05 and 187-06 draft those replies.
- `evidence/187-03-app-version.txt` holds `3.0.0b39` alone on line 1 for every downstream reply body
  to copy verbatim.
- `187-MERGE-RECORD.md` now has sections 1-4 filled for both meta and app; only the firmware rows
  (187-04) remain before 187-12 can write the tail-disclosure section.
- No blockers for 187-04 (the firmware cut). Waves 4 and 7-11 remain outward-facing acts and would
  hit the same auto-mode classifier this plan hit if harness auto mode were ever re-enabled; it is
  currently off, per the operator.

## Self-Check: PASSED

- `.planning/phases/187-answered-reports/evidence/187-03-operator-approval.txt` — FOUND
- `.planning/phases/187-answered-reports/evidence/187-03-app-version.txt` — FOUND, line 1 is exactly `3.0.0b39`
- `.planning/phases/187-answered-reports/evidence/187-03-app-cut.txt` — FOUND, contains both `PRE-MERGE MEASUREMENT (app)` and `READ AFTER THE CUT` blocks
- `.planning/phases/187-answered-reports/187-MERGE-RECORD.md` — FOUND, app rows filled in sections 1-4
- Commit `822e829f` — FOUND
- Commit `e6f3a318` — FOUND
- Commit `eecd27c3` — FOUND
- All Task 1-3 `<verify>` legs and acceptance criteria re-run and passed (see body above); PR #62 confirmed `MERGED` against `beta`; `beta-release.yml` run `34698771255` confirmed `completed`/`success`; `3.0.0b39` confirmed present in both `gh release list` and PyPI's release JSON; no `v1.37` tag present on `origin`; neither new datasheet PDF tracked.

---
*Phase: 187-answered-reports*
*Completed: 2026-09-12*
