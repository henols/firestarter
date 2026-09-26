---
phase: 132-retire-dev-sdp-discharge-the-mypy-debt
plan: 09
subsystem: ci
tags: [mypy, watermark, ci-dispatch, github-actions, d-08, d-09, d-11, retire-06]

# Dependency graph
requires:
  - phase: 132-08
    provides: "measured mypy count of 32 (checked 122 source files, watermark 35) held stable across plans 132-06/07/08, and the ring-fence's empty diff, as this plan's pre-dispatch baseline"
provides:
  - "The certifying CI dispatch: run 30856059940 on gsd/v1.30-sdp-surface-retirement @ 42a1971, conclusion success, discharging RETIRE-06 and ROADMAP criterion 4"
  - "132-CI-GREEN.md -- the run's identity, seven-point fail-closed precondition, per-step status table, verbatim gate line, mypy-completion-clause absence investigation, resolved versions, coverage result, and Phase 131 D-11 discharge"
  - "132-CI-PARITY.md section 2 (After) -- both local recipes re-run on the finished tree, compared leg-by-leg against the before-half"
  - "132-MYPY-LEDGER.md section 9 -- the third and final reading (CI's own count), agreeing exactly with the local replica at 32"
  - "132-RECORD.md -- the phase's closing record: eight requirements accounted, fourteen decisions honoured, seven corrections, four residuals, the silicon-proof disclaimer, and the forward handoff to Phases 133/134"
  - "RETIRE-06 marked Complete in REQUIREMENTS.md -- all eight RETIRE requirements now Complete"
affects: [133, 134, 135, 136, 137]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Investigating a missing log line via a gate's own guard-order logic, rather than substituting a locally-computed number (D-08): mypy's raw completion clause was absent from this CI run's log by construction (the hardened checker's success path never echoes result.stdout), but the run's completeness was proven from the fact that the log's post-guard-5 stamp line ('checked N source files') is only reachable if the internal regex match succeeded."
    - "Delta-check substitution for an unreachable literal acceptance criterion, stated explicitly in the record rather than silently claimed: the pre-existing-dirt baseline is quoted verbatim and every 'clean tree' criterion in this phase is checked against it, not against a literal empty status."

key-files:
  created:
    - .planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-CI-GREEN.md
    - .planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-RECORD.md
  modified:
    - .planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-CI-PARITY.md
    - .planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-MYPY-LEDGER.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "No agent ran git push or gh workflow run. Both privileged actions (branch push creating gsd/v1.30-sdp-surface-retirement on origin, and the workflow_dispatch) were performed by the operator per the plan's task 2 handoff; everything read after the dispatch used read-only gh run view/--log calls with XDG_CACHE_HOME exported to a writable path."
  - "Mypy's raw completion clause was investigated, not fabricated, when it did not appear verbatim in the CI log: the hardened check_mypy_watermark.py's success path never re-prints result.stdout/stderr (only the four sys.exit(2) failure branches do), so the workflow step's direct invocation of the script never echoes it -- distinguished explicitly from Phase 131's F-07 (a genuinely aborted run where the clause was structurally uncapturable). The run's completeness was proven from the gate's own guard order instead of substituting a local number."
  - "The pre-existing-dirt substitution is stated as a named delta check in both 132-CI-PARITY.md and 132-RECORD.md, quoting the baseline verbatim, rather than silently treating the literal empty-porcelain criterion as satisfied."

requirements-completed: [RETIRE-06]

coverage:
  - id: D1
    description: "The after-half of the CI-parity recipe and the full local replica run confirm mypy holds at 32 (unchanged from 132-06/07/08) and coverage clears the 70% floor at 81.72%, before the operator turn is requested."
    verification:
      - kind: integration
        ref: "bash tools/ci_parity.sh (legs 1-3 exit 0, leg 4 exit 2 -- unchanged, expected); bash tools/ci_replica_venv.sh (all 5 legs PASS; Found 32 errors in 12 files (checked 122 source files); Required test coverage of 70% reached. Total coverage: 81.72%)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The two privileged operator actions (branch push, workflow dispatch) were performed by the operator, not an agent, and the certifying CI run's ci job concluded success with every certification number read from the log."
    verification:
      - kind: integration
        ref: "gh run view 30856059940 --repo henols/firestarter_app --json conclusion,event,headBranch,headSha -- conclusion: success, event: workflow_dispatch, headBranch: gsd/v1.30-sdp-surface-retirement, headSha: 42a1971a072db2f3bcec558a3dc2bcb3d5d65e08 (matches submodule HEAD)"
        status: pass
    human_judgment: true
    rationale: "The dispatch itself is an irreducibly human action (git push + gh workflow run, both denied to agents); this deliverable's completion depends on the operator's own confirmation that both steps were performed as instructed, which this plan's checkpoint already captured verbatim in the resumed conversation."
  - id: D3
    description: "132-CI-GREEN.md and 132-MYPY-LEDGER.md section 9 record the certifying run's evidence, read never computed, including a seven-point fail-closed precondition check, the ci-vs-ci-py32 scope exclusion, and the CI-vs-local mypy count comparison."
    verification:
      - kind: unit
        ref: "grep -cE 'mypy errors: [0-9]+ \\(watermark: 35\\)' 132-CI-GREEN.md -- 2 (>=1 required); grep -c 'ci-py32' 132-CI-GREEN.md -- present with explicit both-directions exclusion language"
        status: pass
    human_judgment: false
  - id: D4
    description: "132-RECORD.md accounts all eight RETIRE requirements, all fourteen locked decisions (with the two non-literal honourings named), at least seven corrections, and four residuals; RETIRE-06 is the only checkbox this plan's commits move."
    verification:
      - kind: unit
        ref: "grep -cE '^\\- \\[x\\] \\*\\*RETIRE-0[1-8]\\*\\*' REQUIREMENTS.md -- 8; git diff HEAD~1 -- REQUIREMENTS.md | grep -cE '^\\+.*\\[x\\].*RETIRE-06' -- 1; git diff HEAD~1 -- REQUIREMENTS.md | grep -cE '^\\+.*\\[x\\].*RETIRE-0[1-578]' -- 0"
        status: pass
    human_judgment: false

duration: ~20min (two working sessions across the task 2 operator checkpoint)
completed: 2026-08-03
status: complete
---

# Phase 132 Plan 09: The Certifying CI Dispatch (RETIRE-06) Summary

**`firestarter_app`'s primary `ci` job — red for two months, invisible outside PRs and manual dispatch — is certified GREEN: run `30856059940` on `gsd/v1.30-sdp-surface-retirement` @ `42a1971`, conclusion `success`, mypy at 32 against the unratcheted watermark of 35, all eight RETIRE requirements now Complete.**

## Performance

- **Duration:** ~20 min of active work, split across two sessions by the mandatory task 2 operator
  checkpoint (branch push + `workflow_dispatch`, performed by the operator, not this agent)
- **Started:** 2026-08-03 (STATE.md's prior session marker, 132-08 complete)
- **Completed:** 2026-08-03T21:58:25Z
- **Tasks:** 4 (1 auto, 1 checkpoint:human-verify, 2 auto)
- **Files modified:** 5 (`132-CI-PARITY.md`, `132-CI-GREEN.md` [new], `132-MYPY-LEDGER.md`,
  `132-RECORD.md` [new], `REQUIREMENTS.md`)

## The certifying run, stated plainly

- **Run id / URL:** `30856059940` — https://github.com/henols/firestarter_app/actions/runs/30856059940
- **`ci` job's conclusion:** `success` (all 16 steps, including the mypy gate step and both steps
  after it — which were `failure`/`skipped` at the Phase 131 fork base — now `success`)
- **Verbatim gate line:** `mypy errors: 32 (watermark: 35)`, preceded by `checked 122 source files`
- **Mypy's own raw completion clause (`Found N errors in M files (checked K source files)`):**
  **absent from this step's log**, investigated rather than substituted — the hardened checker's
  success path never re-echoes `result.stdout`; the run's completeness is instead proven from the
  gate's own guard order (the log's `checked 122 source files` line is only reachable if the
  internal completion-clause regex matched). Full argument in `132-CI-GREEN.md` §5.
- **Coverage:** `81.72%` against the workflow's `70%` floor, read from the `Run pytest with
  coverage` step (`1251 passed, 46 skipped` — the skip delta from local's `1297 passed, 0 skipped`
  is fully attributable to CI's genuine standalone checkout, no meta-repo tree, no `[py32]` extra)
- **CI-versus-local mypy count comparison:** **exact agreement, 32 errors, checked 122 source
  files, watermark 35** — no reconciliation needed, no divergence recorded
  (`132-MYPY-LEDGER.md` §9)

## The four residuals, one line each

1. **The honesty caveat has no user-reachable carrier between this phase and Phase 134** — the four
   surviving assertions pin wording, not CLI delivery, and the one delivery-path proof (plan 132-02)
   cannot be re-run from the tree.
2. **3 of silent watermark headroom persists** (measured 32 against the unratcheted 35) — a named
   input for a later phase's ratchet, not yet filed as its own backlog item.
3. **The ring-fenced ten `[union-attr]` errors in `eprom_operations.py` remain**, dispositioned to
   `FUT-MYPY-02` by the 2026-08-03 operator decision, untouched throughout this phase.
4. **The coverage-gate gap in `tools/ci_parity.sh` remains a gap in that recipe specifically** —
   `tools/ci_replica_venv.sh`'s leg 5 is the artifact that actually closes it.

**Requirements marked Complete: RETIRE-06 (all eight RETIRE ids now complete).**

## Task Commits

Each task was committed atomically, in the meta-repo (this plan writes no submodule commit):

1. **Task 1: after-half of the CI-parity recipe + full local replica run** — `be91e14` (docs)
2. **Task 2: OPERATOR checkpoint — push + dispatch** — no commit; two privileged operator actions
   against `origin`, confirmed via the resumed conversation (branch pushed, `gh workflow run`
   dispatched, run id `30856059940` returned)
3. **Task 3: read the certifying run, write `132-CI-GREEN.md`, ledger's third reading** — `f6dd6a7` (docs)
4. **Task 4: `132-RECORD.md` + tick RETIRE-06** — `5cb1fa6` (docs)

**Plan metadata:** this summary + STATE.md/ROADMAP.md updates (meta-repo, separate commit per
`<final_commit>`).

## Files Created/Modified

- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-CI-PARITY.md` — appended the
  after-half (section 2), both recipes re-run and compared leg-by-leg against the before-half.
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-CI-GREEN.md` (new) — the
  certifying run's full evidence record: identity table, seven-point fail-closed precondition,
  per-step status table, verbatim gate line, completion-clause absence investigation, resolved
  versions, coverage result, D-11 discharge, and the not-established section.
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-MYPY-LEDGER.md` — appended
  section 9, the third reading (CI's own count), agreeing exactly with the local replica.
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-RECORD.md` (new) — the phase's
  closing record: outcome, eight-row requirements table, fourteen-row decisions table, seven-row
  corrections table, four residuals, the silicon-proof split, and the forward handoff.
- `.planning/REQUIREMENTS.md` — RETIRE-06 ticked with its evidence line; the only checkbox this
  plan's commits move.

## Decisions Made

- **No agent ran `git push` or `gh workflow run`.** Both privileged actions were the operator's,
  per the plan's `autonomous: false` mandate and this plan's task 2 checkpoint; every subsequent
  read used only `gh run view`/`--log` (read-only), with `XDG_CACHE_HOME` exported to a writable
  scratch path first, per the recorded failure mode that log retrieval returns silently empty
  without one.
- **Mypy's raw completion clause's absence was investigated, not papered over.** It is not the
  same absence as Phase 131's F-07 (a genuinely aborted, pre-hardening run) — this run's hardened
  checker internally matched the clause (proven by the guard-order argument in `132-CI-GREEN.md`
  §5) but its success path simply never re-prints `result.stdout`. Stated explicitly rather than
  substituting a locally-run mypy invocation, which would have violated D-08 directly.
- **The pre-existing-dirt substitution is named, not silently claimed.** Every "clean tree"
  criterion in this plan was checked as a delta against the baseline dirt measured before this
  phase began (` M .gitignore`, `?? .coverage`, `?? .planning/config.json`, `?? SECURITY.md`,
  `?? write_test_port.sh`), quoted verbatim in both `132-CI-PARITY.md` §2 and `132-RECORD.md`.

## Deviations from Plan

None — plan executed as written, including the mandatory checkpoint pause and resumption. One
worth naming for a future reader: a concurrent, unrelated commit (`d83caf8b`, "defer Phase 135
(write --sdp-relock) to Backlog 999.28") landed on this branch between this plan's task 1 and task
3 commits, from a process outside this plan's own execution. It touched `PROJECT.md`, `ROADMAP.md`,
`REQUIREMENTS.md`'s RELOCK section, `STATE.md`, a design note, and a todo file — none of which this
plan's tasks own. It was left entirely untouched: this plan's task 3 and task 4 commits were staged
by explicit path only (`132-CI-GREEN.md`, `132-MYPY-LEDGER.md`, `132-RECORD.md`,
`REQUIREMENTS.md`'s RETIRE-06 line), and the `git diff HEAD~1` checks in this summary's coverage
block confirm no RELOCK-section or other unrelated line was re-touched by this plan's own commits.

## Issues Encountered

None beyond the above. The full CI-parity and replica-venv recipes, and the certifying run itself,
all behaved exactly as `132-CONTEXT.md`'s D-06 through D-09 anticipated.

## User Setup Required

**Already discharged by the operator during this plan's execution** (task 2, `checkpoint:human-verify
gate="blocking"`): the operator pushed `gsd/v1.30-sdp-surface-retirement` to `origin` and ran
`gh workflow run "Host CI" --repo henols/firestarter_app --ref gsd/v1.30-sdp-surface-retirement`,
returning run id `30856059940`. No further user setup is required.

## Next Phase Readiness

- All eight RETIRE requirements are Complete. `firestarter_app`'s primary `ci` job is certified
  green at the existing watermark of 35, true count 32.
- `firestarter/sdp_honesty.py`'s API (`emission_summary`, `map_unknown_cmd_to_outdated`) is a
  forward contract for Phase 134's leg and any later `write --sdp-relock` scoping.
- The typed `make_app_context(...) -> AppContext` factory + `app_context` fixture in
  `tests/conftest.py` is the pattern any later test module must use.
- The milestone branch `gsd/v1.30-sdp-surface-retirement` now exists on `origin`, 28 commits ahead
  of `origin/beta` — not yet merged; that is a later, operator-gated milestone-close action.
- Phase 132 is closed pending the standard phase-close verification; `132-RECORD.md` is this
  phase's authoritative closing record for that verification to read against.

---
*Phase: 132-retire-dev-sdp-discharge-the-mypy-debt*
*Completed: 2026-08-03*

## Self-Check: PASSED

Created/modified files verified present on disk:
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-CI-GREEN.md` — FOUND
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-RECORD.md` — FOUND
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-09-SUMMARY.md` — FOUND
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-CI-PARITY.md` — FOUND
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-MYPY-LEDGER.md` — FOUND

Commits verified present in `git log --oneline --all`:
- `be91e14` (task 1, meta-repo) — FOUND
- `f6dd6a7` (task 3, meta-repo) — FOUND
- `5cb1fa6` (task 4, meta-repo) — FOUND
- `ccf096d` (this summary, meta-repo) — FOUND
</content>
