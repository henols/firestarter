---
phase: 172-policy-one-tracker-protected-main
plan: 06
subsystem: infra
tags: [github-rulesets, branch-protection, github-api, policy-03, decision-reversal]

requires:
  - phase: 172-05
    provides: "The captured incumbent (evidence/172-05-ruleset-4998759-pre-delete.json), the canonical body (evidence/172-05-ruleset-body.json, DeployKey bypass), and the live prom canary (id 22043478) used as the equality baseline"
provides:
  - "D-10 reversed: henols/firestarter's ruleset 4998759 amended in place (PUT) rather than deleted and recreated; its id and 2025-04-22 creation date are preserved"
  - "henols/firestarter_app's ruleset created fresh (id 22046179) from the same canonical body"
  - "A three-way read-back proving all three repositories carry an identical, enforcing ruleset, with an order-insensitivity control on the comparison normaliser"
  - "A named record of a harness permission-gate interruption mid-plan, and the genuine PATCH-vs-PUT API-shape finding it surfaced"
affects: [173]

actuals:
  tokens: 4200
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns: ["A checkpoint:decision answer can reverse a plan's own destructive design (D-10) when live measurement shows the destructive path buys nothing functional", "GitHub's ruleset update endpoint is PUT, not PATCH -- PATCH returns HTTP 404 on this route"]

key-files:
  created:
    - .planning/phases/172-policy-one-tracker-protected-main/evidence/172-06-delete-create-sequence.txt
    - .planning/phases/172-policy-one-tracker-protected-main/evidence/172-06-ruleset-readback.txt
  modified: []

key-decisions:
  - "D-10 REVERSED at the Task 1 checkpoint:decision gate (Option B chosen over Option A). Before presenting the decision, the incumbent ruleset 4998759 was compared field-by-field against the already-live prom canary (22043478), excluding id/node_id/created_at/updated_at/source/source_type/_links/current_user_can_bypass. They were IDENTICAL on every remaining field -- name, target, conditions, all three rules (including the pull_request rule's parameters), and bypass_actors -- differing only in enforcement (disabled vs active). Deleting and recreating would have bought uniform birth history and nothing functional, at the cost of permanently destroying 4998759's id and its 2025-04-22T11:42:12.549Z creation date, which the GitHub API cannot restore. The operator selected amend-in-place plus create-firestarter_app-fresh on this measurement."
  - "D-10's own stated rationale for deleting -- 'nothing inherited and no dead DeployKey bypass to reconcile' -- was independently voided by plan 172-05's mid-phase D-09 revision, which made DeployKey the CANONICAL bypass actor (not a legacy one to shed) after GitHub rejected the originally-planned Integration/15368 actor with HTTP 422 on this personal, non-organization account."
  - "Task 2's checkpoint:human-action gate was DISCHARGED, not approved in its original form and not skipped. Its subject was authorizing the irreversible DELETE; the D-10 reversal removed that subject entirely -- nothing left in this plan is one-way (a PUT reverses with a PUT, a POST reverses with a DELETE). The operator authorized the two specific replacement operations (the PUT and the POST) by name when selecting Option B at the decision gate, and the two calls were then issued by the ORCHESTRATOR AGENT via its Bash tool, each individually approved by the operator at a harness permission prompt after the session left auto mode (see Deviations)."
  - "Both write calls (PUT on firestarter, POST on firestarter_app) sent the FULL canonical body from evidence/172-05-ruleset-body.json, not a partial enforcement-only body, so the outcome does not depend on how the API treats fields omitted from a partial PUT."

requirements-completed: [POLICY-03]

coverage:
  - id: D1
    description: "henols/firestarter's ruleset 4998759 is amended to enforcement=active in place, preserving its id and 2025-04-22 creation date"
    requirement: "POLICY-03"
    verification:
      - kind: other
        ref: "evidence/172-06-ruleset-readback.txt -- id preservation check: id=4998759, created_at=2025-04-22T11:42:12.549Z"
        status: pass
    human_judgment: false
  - id: D2
    description: "henols/firestarter_app's ruleset is created fresh from the canonical body (id 22046179)"
    requirement: "POLICY-03"
    verification:
      - kind: other
        ref: "evidence/172-06-ruleset-readback.txt -- firestarter_app id=22046179 raw read-back, enforcement=active"
        status: pass
    human_judgment: false
  - id: D3
    description: "All three repositories' rulesets are identical apart from volatile fields, and the equality is proven order-insensitive rather than assumed"
    requirement: "POLICY-03"
    verification:
      - kind: other
        ref: "evidence/172-06-ruleset-readback.txt -- normalised diffs (prom vs firestarter, prom vs firestarter_app) both clean; reversed-array control clean"
        status: pass
    human_judgment: false
  - id: D4
    description: "The decision to reverse D-10 (delete-and-recreate to amend-in-place) was made by the operator with full context, not defaulted or assumed by the executor"
    verification: []
    human_judgment: true
    rationale: "This was a checkpoint:decision answered by the operator via the coordinator, with the measured field-equality evidence presented before the choice. The executor's role was to present the evidence and execute the chosen option, not to judge whether reversing D-10 was correct policy -- that judgment belongs to the operator and is recorded, not re-litigated here."

# Metrics
duration: 62min
completed: 2026-09-01
status: complete
---

# Phase 172 Plan 06: Ruleset Amend-and-Create, Three-Way Read-Back Summary

**D-10's delete-and-recreate reversed to an in-place amend after measurement showed the incumbent already matched the canary on everything but `enforcement`; `firestarter`'s ruleset 4998759 keeps its 2025-04-22 identity, `firestarter_app` gets a fresh one, and all three read back identical and enforcing.**

## Performance

- **Duration:** 62 min (spanning two coordinator interruptions: the decision-gate resolution, and a harness permission-gate resolution)
- **Started:** 2026-09-01T20:31:00Z (approx, immediately after 172-05's completion)
- **Completed:** 2026-09-01T21:41:00Z
- **Tasks:** 3 of 3 (Task 1 decision gate resolved to Option B; Task 2 human-action gate discharged as moot; Task 3 executed as amend-and-create)
- **Files modified:** 2 evidence files created, 1 cross-phase ledger file created (`.planning/WINDOWS.md`), SUMMARY + STATE this commit

## Accomplishments

- Measured `henols/firestarter`'s incumbent ruleset `4998759` against the live prom canary before the decision gate was presented, finding them identical on every field except `enforcement` -- the evidence that justified reversing D-10
- `henols/firestarter`'s ruleset amended in place via `PUT .../rulesets/4998759` with the full canonical body -- `enforcement: active`, id and 2025-04-22 creation date preserved, no DELETE issued
- `henols/firestarter_app`'s ruleset created fresh via `POST .../rulesets` from the identical canonical body (id `22046179`)
- Three-way read-back proves all three repositories (`firestarter_prom:22043478`, `firestarter:4998759`, `firestarter_app:22046179`) carry an identical, enforcing ruleset apart from volatile fields -- `enforcement=active`, `bypass=DeployKey:null:always`, `can_bypass=never`, `rules=deletion,non_fast_forward,pull_request`, `include=~DEFAULT_BRANCH`, on all three
- The comparison normaliser proven order-insensitive with a reversed-array control, not merely assumed correct
- POLICY-03's live GitHub state is now correct on all three repositories; the requirement mark itself stays pending in REQUIREMENTS.md because it is shared with plans 172-08 and 172-09, which have not yet produced a SUMMARY (the shared-ID gate, #2388, correctly reports `0/1 ready`)

## Task Commits

1. **Task 1: decision gate (checkpoint:decision)** -- no commit (a checkpoint, not code); resolved to Option B by the operator via the coordinator
2. **Task 2: human-action gate (checkpoint:human-action)** -- no commit (a checkpoint); discharged as moot once Option B removed its subject (the irreversible DELETE)
3. **Task 3: run the amend-and-create sequence, prove three-way equality** -- `c9ac3c90` (docs) -- both evidence files

**Plan metadata:** (this commit) -- SUMMARY + STATE

_Note: the two write calls themselves (`PUT` on `firestarter`, `POST` on `firestarter_app`) were issued by the orchestrator agent via its Bash tool, each individually approved by the operator at a harness permission prompt once the session left auto mode -- not by this executor, and not typed or run by the operator. See Deviations. Nothing else in Task 3 required a commit beyond the evidence files, since the write calls are against GitHub's control plane, not the repository._

## Files Created/Modified

- `evidence/172-06-delete-create-sequence.txt` -- records the actual sequence executed (PUT, then POST, both rc=0), states plainly that no DELETE occurred and why, and carries the two named findings (CI auto-commit breakage now live; the `actor_id: null` residual)
- `evidence/172-06-ruleset-readback.txt` -- three raw read-backs, the three-way equality diff (two clean comparisons), the order-insensitivity control, the id/creation-date preservation check, and the six-assertion summary block
- `.planning/WINDOWS.md` -- created (first entry in this project); records the unrun literal verify-script and the D-10 reversal as ledger entries

## Decisions Made

See `key-decisions` in the frontmatter for the full record. In short: D-10 (delete-and-recreate) was reversed to Option B (amend-in-place plus fresh create) at the Task 1 checkpoint on the strength of a field-by-field equality measurement against the canary; Task 2's checkpoint was discharged rather than approved or skipped, because its only subject (the irreversible DELETE) no longer existed once D-10 was reversed.

## Deviations from Plan

### Auto-fixed / Escalated Issues

**1. [Rule 4 - Architectural change, operator-resolved via checkpoint:decision] D-10 reversed from delete-and-recreate to amend-in-place**

- **Found during:** Task 1, before presenting the decision gate
- **Issue:** The plan as written (D-10) called for deleting `4998759` and creating all three rulesets fresh from one body. A field-by-field comparison against the already-live prom canary, run before the checkpoint was presented, showed the incumbent already matched the canary on every field except `enforcement`.
- **Resolution:** The operator selected Option B at the decision gate: `PUT` (amend) `firestarter`'s ruleset to `enforcement: active`, `POST` (create) only `firestarter_app`'s fresh. No DELETE issued on any repository.
- **Files modified:** none directly by this deviation; it changed which API calls Task 3 issued
- **Verification:** `evidence/172-06-ruleset-readback.txt` -- id and creation-date preservation check passes; three-way equality passes; `enforcement=active` on all three
- **Committed in:** `c9ac3c90` (evidence recording the outcome)

**2. [Process] Task 2's checkpoint:human-action gate discharged, not approved in original form**

- **Found during:** Task 2
- **Issue:** Task 2's original subject was authorizing the DELETE-then-two-POSTs sequence. That subject no longer existed after D-10's reversal.
- **Resolution:** Recorded explicitly, per the coordinator's instruction, as *discharged* rather than *passed* or *skipped* -- the operator's Option-B selection at the decision gate named the replacement PUT and POST operations directly, which stands as the authorization for those specific calls.
- **Files modified:** `evidence/172-06-delete-create-sequence.txt` documents this disposition
- **Verification:** n/a (process record)
- **Committed in:** `c9ac3c90`

**3. [Rule 3 - Blocking, environment permission gate] Harness auto-mode Bash classifier blocked mutating `gh api` calls mid-plan**

- **Found during:** Task 3, attempting to issue the PUT and POST myself
- **Issue:** A first `PATCH` attempt returned a genuine HTTP 404 from GitHub -- this was a real API-shape finding, not a permission issue: GitHub's "Update a repository ruleset" endpoint is `PUT`, not `PATCH`. A subsequent retry with the correct `PUT` method, and a further verbose retry, were both denied by the Claude Code auto-mode Bash classifier before reaching the network, with an explicit instruction not to attempt workarounds and to stop and report instead.
- **Resolution:** I verified no partial mutation had occurred (both repositories' state unchanged) and reported the blocker to the coordinator rather than attempting further retries. The coordinator relayed that the operator switched the session out of auto mode, and that the coordinator itself then issued both calls (`PUT` on `firestarter`, `POST` on `firestarter_app`, both with the full canonical body, both rc=0), with the operator approving each at a harness permission prompt. The operator authorized; the agent executed. I then re-derived the read-back and equality checks independently from fresh `gh api` reads rather than copying the coordinator's reported values, per the coordinator's explicit instruction.
- **Files modified:** none from the block itself; the eventual evidence files record the outcome
- **Verification:** fresh, independently-run `gh api` reads in `evidence/172-06-ruleset-readback.txt` cross-check against (and match) the coordinator's reported values
- **Committed in:** `c9ac3c90`

**4. [Rule 1/2 - stale verify-script literals] Task 3's plan-authored `<automated>` verify blocks were not run as written**

- **Found during:** Task 3, before the verify step
- **Issue:** The plan's literal verify scripts hardcode `bypass=Integration:15368:always` (superseded by D-09's DeployKey revision in plan 172-05) and assume all three rulesets are freshly created (asserting no repository's list contains id `4998759`, and that `firestarter`'s id is not `4998759`) -- both false by design once D-10 was reversed to amend-in-place.
- **Resolution:** Ran the equivalent checks by hand, adapted to the actual outcome: `bypass=DeployKey:null:always` asserted (not `Integration:15368:always`); `firestarter`'s ruleset id asserted to equal `4998759` (not to differ from it) and its `created_at` asserted to equal the original `2025-04-22T11:42:12.549Z` (proving amend, not recreate); the "no repository's list contains id 4998759" assertion dropped, replaced with an explicit id-preservation check. All other assertions (list length 1 per repo, `enforcement=active` ×3, `rules=deletion,non_fast_forward,pull_request` ×3, `include=~DEFAULT_BRANCH` ×3, `can_bypass=never` ×3, order-insensitivity control, settings-page-reference grep) carried over unchanged from the plan's intent.
- **Files modified:** `evidence/172-06-ruleset-readback.txt` records the adapted assertions and their results
- **Verification:** all adapted assertions pass, recorded in the evidence file
- **Committed in:** `c9ac3c90`
- **Ledger note:** the plan's literal, unadapted verify scripts were never executed as written (they would fail by design against the reversed outcome); recorded as an `unrun-verify` entry in `.planning/WINDOWS.md`

---

**Total deviations:** 4 (1 architectural/operator-resolved, 1 process/discharge, 1 blocking/environment-permission, 1 stale-literal-adaptation). **Impact on plan:** POLICY-03's live GitHub state is fully correct on all three repositories and more conservative than the original design (no permanent destruction of `4998759`'s identity). No scope creep -- every deviation traces directly to the operator's Option-B decision and its consequences.

## Issues Encountered

- The harness's auto-mode Bash classifier blocking mutating `gh api` calls (see Deviation 3) required the operator to switch to a manual session to complete the two write calls. This is worth surfacing as a process note for future GSD plans that mutate external control-plane state (GitHub rulesets, deploy targets, etc.) under `autonomous: false` -- the checkpoint gates in the plan correctly required human sign-off, but the harness's own permission layer added a second, unplanned gate on top of them that the plan's authors could not have anticipated.

## User Setup Required

None -- no external service configuration required beyond the `gh` CLI authentication already in place.

## Next Phase Readiness

Ready for plan 172-07 (branch `policy/contributor-policy` and the three `.github` pull requests) and plan 172-08/172-09, which both also declare `POLICY-03` and will complete its requirement mark once their own SUMMARYs land (per the shared-ID gate, this plan alone cannot flip `POLICY-03` to Complete in REQUIREMENTS.md).

Two carry-forwards for Phase 173's honesty ledger, now live rather than prospective:

1. Both sub-repositories' CI version-bump auto-commits to `main` (`firestarter_app/.github/workflows/release.yml`, `firestarter/.github/workflows/build.yml`) will fail on their next push to `main` -- `enforcement: active` is live on all three repositories as of this plan.
2. `actor_id: null` on the DeployKey bypass matches any future deploy key on any of the three repositories, not a specific one -- currently inert (zero deploy keys measured) but a standing residual.

---
*Phase: 172-policy-one-tracker-protected-main*
*Completed: 2026-09-01*

## Self-Check: PASSED

- `evidence/172-06-delete-create-sequence.txt` -- FOUND
- `evidence/172-06-ruleset-readback.txt` -- FOUND
- `172-06-SUMMARY.md` -- FOUND
- Commit `c9ac3c90` -- FOUND in `git log --oneline --all`
- Live re-check: `firestarter_prom`, `firestarter`, `firestarter_app` each return exactly 1 ruleset; `firestarter`'s ruleset id is `4998759` (confirming amend, not recreate)
