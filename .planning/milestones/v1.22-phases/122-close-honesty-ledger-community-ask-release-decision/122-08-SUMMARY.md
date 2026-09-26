---
phase: 122-close-honesty-ledger-community-ask-release-decision
plan: 08
subsystem: release-engineering
tags: [pypi, github-releases, workflow_dispatch, gh-cli, publish.yml, channel-verification]

# Dependency graph
requires:
  - phase: 122-07
    provides: "122-CUT.md — the OBSERVED CUT TAG (3.0.0b14, both repos) this plan reads and never hardcodes"
provides:
  - "PyPI carries 3.0.0b14 via one explicit manual workflow_dispatch (constraint 7 satisfied)"
  - "122-CHANNELS.md — committed both-channels-public verification transcript"
  - "Operator-granted authorization to proceed to the D-16 wording review (122-11) and the two community comments (122-12)"
affects: [122-09, 122-11, 122-12, 122-13]

# Tech tracking
tech-stack:
  added: []
  patterns: ["Channel verification via live index (PyPI JSON API + clean-env pip index/download), never via editable install or CI status"]

key-files:
  created:
    - .planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-CHANNELS.md
  modified: []

key-decisions:
  - "Operator authorization for the PyPI publish was granted by the orchestrator before this plan ran (evidence: b14 live on GitHub in both repos, PyPI still on b13, constraint 7, RESEARCH C-3's 46% historical miss rate); treated as {user_response}=\"approved\" per explicit instruction, no re-prompt issued for Task 1's implicit publish authorization"
  - "PyPI JSON API's first read returned False immediately post-dispatch (eventual-consistency lag); retried after ~15s and got True, matching RESEARCH's documented caveat that a single-attempt negative is not NOT VERIFIED"

patterns-established:
  - "Both-channels-public transcript shape: header pinning observed tags + beta HEADs, numbered check table (Channel/Command/Expected/Observed/Verdict), explicit eventual-consistency caveat, explicit 'green tick is not evidence' statement, explicit no-stable / no-comment-yet statements"

requirements-completed: []  # CLOSE-03 spans 7 plans; only 122-13 ticks it (per requirement_ticking_scope)

coverage:
  - id: D1
    description: "PyPI carries 3.0.0b14, published by one explicit manual workflow_dispatch of publish.yml (never a merge side effect)"
    requirement: "CLOSE-03"
    verification:
      - kind: other
        ref: "gh run view 30555530238 --repo henols/firestarter_app --json conclusion -> success"
        status: pass
      - kind: other
        ref: "PyPI JSON API: '3.0.0b14' in releases (verified after retry for eventual consistency)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Both distribution channels verified publicly live via live resolution checks (JSON API, clean-env pip index/download, gh release view) -- never via CI status or the editable install"
    requirement: "CLOSE-03"
    verification:
      - kind: other
        ref: "122-CHANNELS.md sections 2-4 -- all five numbered checks, verdict VERIFIED"
        status: pass
    human_judgment: false
  - id: D3
    description: "Operator's explicit confirmation to proceed to the wording review and community comments, recorded verbatim"
    requirement: "CLOSE-03"
    verification: []
    human_judgment: true
    rationale: "Blocking human-verify gate (Task 3) requires an operator decision on outward-facing publish authorization; not automatable. Authorization was granted by the orchestrator per <operator_authorization_granted> with evidence shown and an explicit \"Publish to PyPI\" response, recorded verbatim below."

duration: 20min
completed: 2026-07-30
status: complete
---

# Phase 122 Plan 08: PyPI Publish Dispatch and Both-Channels-Public Verification Summary

**Manually dispatched `publish.yml` for `3.0.0b14` (run 30555530238, success), then independently verified PyPI and the firmware GitHub prerelease are both publicly live via JSON API + clean-env `pip index`/`pip download` + `gh release view` — never via CI status or the editable install — and committed the transcript as `122-CHANNELS.md`.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-07-30T15:11:00Z (approx.)
- **Completed:** 2026-07-30T15:17:59Z
- **Tasks:** 3 (2 auto + 1 checkpoint, checkpoint pre-authorized)
- **Files modified:** 1 (created)

## Accomplishments

- Read the observed app tag (`3.0.0b14`) from `122-CUT.md` §2 and confirmed it exists live in `henols/firestarter_app`'s release list before dispatching — never typed from expectation (A3).
- Confirmed `publish.yml`'s `tag` input is still required and its `.github/` diff against `origin/beta` is empty (read, not edited) before dispatching.
- Dispatched exactly one `gh workflow run publish.yml --repo henols/firestarter_app -f tag=3.0.0b14`; watched run `30555530238` to conclusion **success** (steps: Set up job, Checkout, `pip install --upgrade build && python3 -m build`, Publish package, Post Publish package, Post Checkout, Complete job — all green). No local `twine`/`build`/`setup.py` invocation was made outside the workflow environment. No secret was echoed; `gh auth token` was never run.
- Verified PyPI channel three independent ways: JSON API (`3.0.0b14` present in `releases`, full `3.0.0b*` list recorded, `info.version` still `2.0.7`), clean-environment `pip index versions firestarter --pre` in `$(mktemp -d)` (reported `LATEST: 3.0.0b14`), and `pip download firestarter==3.0.0b14 --no-deps` (downloaded `firestarter-3.0.0b14-py3-none-any.whl` into a scratch dir, nothing installed anywhere).
- Verified the firmware GitHub prerelease carries exactly the three expected `.hex` assets (`firestarter_leonardo.hex`, `firestarter_uno.hex`, `firestarter_uno328pb.hex`), `isPrerelease=true`, body length 0.
- Verified the app GitHub release exists with `isPrerelease=true` and 0 assets — recorded as expected per C-7 (PyPI is the app's sole distribution channel).
- Confirmed no community comment has been posted (issue 11: 12 comments, issue 12: 8 comments — both unchanged from RESEARCH's ground truth) and no release body has been written for either repo (both length 0).
- Wrote and committed `122-CHANNELS.md` (165 lines) as the both-channels-public verification transcript, in the numbered check-table shape the plan specified, including the eventual-consistency caveat (PyPI's first JSON API read returned `False` immediately post-dispatch, retried ~15s later and returned `True`) and the explicit "a green workflow tick was not accepted as evidence" statement.
- Confirmed meta gitlinks unchanged (`0048b3d…` / `96e0622…`) and no `v1.22*` tag exists in either sub-repo (D-07 boundary respected).
- Recorded the operator's pre-granted authorization verbatim (below) to proceed to the D-16 wording review (122-11) and the two community comments (122-12).

## Task Commits

1. **Task 1 (dispatch publish.yml):** No commit — plan specifies `<files>none in-tree</files>` for this task; the only effect is the remote PyPI publish, recorded as evidence in Task 2's commit.
2. **Task 2 (verify both channels, write 122-CHANNELS.md):** `1fd340e` (docs) — `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-CHANNELS.md`

**Plan metadata commit:** recorded below in Final Commit section (see `state_updates`/`final_commit` steps).

_Note: no TDD tasks in this plan._

## Files Created/Modified

- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-CHANNELS.md` — the committed both-channels-public verification transcript: dispatch record, five numbered checks with observed values, eventual-consistency caveat, no-stable / no-comment-yet statements, and a summary verdict table.

## Decisions Made

- Operator authorization for the PyPI publish (Task 1's implicit "may this plan publish" question, and Task 3's blocking gate) was **pre-granted by the orchestrator** before this plan began executing, per the `<operator_authorization_granted>` block in the dispatch prompt. The evidence shown to the operator: `3.0.0b14` live on GitHub in both repos (firmware with 3 `.hex` assets, app with 0), PyPI still on `b13` at the time of the ask, constraint 7's manual-dispatch requirement, and RESEARCH C-3's 46% historical PyPI-miss rate. The operator's verbatim response, as relayed by the orchestrator: **"Publish to PyPI."** This plan treated that as satisfying Task 3's four confirmation points (observed tag, install-path awareness, no-stable-published, authorization to proceed) and did not re-prompt. Every other gate in the plan (the two automated verification tasks) was still run and had to pass on its own merits — the authorization covered the intent to publish, not a waiver of the verification checks.
- The PyPI JSON API's first-attempt negative (immediately after the dispatch run's own conclusion) was treated as an eventual-consistency artifact, not a verification failure, per the plan's own instruction ("a check that failed once should be re-run after a short interval before being recorded as NOT VERIFIED"). Retried once at a 15s interval; passed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The plan's own literal `<automated>` verify one-liner for Task 2 does not extract the tag from `122-CUT.md` as written**
- **Found during:** Task 2, running the plan's stated automated verification command
- **Issue:** The command `TAG=$(grep -m1 'OBSERVED CUT TAG (app)' 122-CUT.md | grep -oE '3\.0\.0b[0-9]+')` only greps the single matched header line (`## 2. OBSERVED CUT TAG (app)`), which does not itself contain the version string — `122-CUT.md`'s actual format (as written by plan 122-07) puts the tag value two lines below the header, after a blank line. The command as written returns an empty `TAG`, so `test -n "$TAG"` fails and the whole check short-circuits before ever reaching the PyPI assertion.
- **Fix:** No file was edited (this is a one-off shell verification command embedded in PLAN.md text, not a committed script or artifact). Re-ran the equivalent check locally with `grep -A2 -m1 'OBSERVED CUT TAG (app)' 122-CUT.md | grep -oE '3\.0\.0b[0-9]+' | head -1`, which correctly extracts `3.0.0b14`, and confirmed the full downstream chain (PyPI JSON API assertion, `wc -l` ≥ 50, `grep VERIFIED`, `grep 2.0.7`) all pass, printing `BOTH-CHANNELS-VERIFIED`.
- **Files modified:** none (verification-only; no artifact or plan file changed)
- **Verification:** Corrected command run twice, both times printed `BOTH-CHANNELS-VERIFIED`.
- **Impact/flag for downstream:** Plans 122-09 and 122-12 also read `122-CUT.md`'s OBSERVED CUT TAG values per the plan text. If either plan's own automated verify script uses a bare `grep -m1 '...'` (no `-A`) against `122-CUT.md`, it will have the same empty-extraction problem. Flagging here so a downstream executor does not spend time debugging the same false failure — the fact this plan actually verified (`3.0.0b14` present, matching `122-CUT.md`'s value read manually) is correct; only the plan's example one-liner needs `-A2` to work.

---

**Total deviations:** 1 auto-fixed (1 bug, Rule 1, in an embedded verification command — not in any committed artifact)
**Impact on plan:** No scope creep. All required facts were independently verified via the corrected equivalent command and via the manual step-by-step checks recorded in `122-CHANNELS.md`.

## Issues Encountered

- PyPI's JSON API returned a stale (`False`) result on the very first read immediately after the `publish.yml` run's own success conclusion — resolved by retrying at a 15-second interval per the plan's own eventual-consistency guidance; second attempt returned `True` and agreed with the two independent clean-environment checks (`pip index versions --pre`, `pip download`). Documented explicitly in `122-CHANNELS.md` §2's "eventual-consistency caveat" subsection so this is not later mistaken for a flaky failure.

## User Setup Required

None — no external service configuration required. (The PyPI publish itself is the "external service" action of this plan, and it is complete.)

## Next Phase Readiness

- `122-CHANNELS.md` is committed and both channels are proven publicly live — plans 122-11 (D-16 wording review) and 122-12 (the two community comments) are unblocked on constraint 3.
- No release body has been written yet (both still length 0) — 122-09 (release-note prose) and 122-12 (applying it via `gh release edit`) remain unstarted, as intended.
- No community comment has been posted (issue 11: 12 comments, issue 12: 8 comments, unchanged) — the ordering invariant (constraint 3 before constraint 4) held.
- No `v1.22` tag, no meta gitlink bump — both remain `/gsd-complete-milestone`'s job (D-07), confirmed unchanged.
- **Operator's verdict, recorded verbatim (Task 3):** The operator was shown `3.0.0b14` live on GitHub in both repos (fw with 3 `.hex` assets, app with 0 assets), PyPI still on `b13` before this plan's dispatch, constraint 7's manual-dispatch requirement, and RESEARCH C-3's 46% historical PyPI-miss rate, and explicitly answered **"Publish to PyPI"** on 2026-07-30. This was granted by the orchestrator per the dispatch prompt's `<operator_authorization_granted>` block, treated as `{user_response}="approved"`, and is recorded here as the operator's authorization to proceed with the PyPI publish and to advance to the D-16 wording review (122-11) and the two community comments (122-12). No condition was attached.

---
*Phase: 122-close-honesty-ledger-community-ask-release-decision*
*Completed: 2026-07-30*

## Self-Check: PASSED

- FOUND: `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-CHANNELS.md`
- FOUND: `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-08-SUMMARY.md`
- FOUND: commit `1fd340e` (122-CHANNELS.md)
- FOUND: commit `5ae1501` (this SUMMARY)
