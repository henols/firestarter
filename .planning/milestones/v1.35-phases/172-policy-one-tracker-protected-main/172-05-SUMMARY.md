---
phase: 172-policy-one-tracker-protected-main
plan: 05
subsystem: infra
tags: [github-rulesets, branch-protection, github-api, policy-03]

requires:
  - phase: 172-04
    provides: ".github/CONTRIBUTING.md pointer files, so the rulesets land after the meta-level policy content is in place"
provides:
  - "The incumbent ruleset 4998759 captured into evidence, before any irreversible action touches it"
  - "One canonical ruleset body (deletion + non_fast_forward + pull_request, enforcement active), revised mid-plan from an Integration bypass actor to a DeployKey bypass actor after GitHub rejected the former"
  - "A live, enforcing ruleset (id 22043478) on henols/firestarter_prom, read back from the API"
  - "D-09's premise settled: the Integration bypass actor is rejected outright on this personal (User-owned) account; a DeployKey bypass validates instead, proven by the incumbent's own bypass entry"
  - "The release-workflow breakage this revision causes in both sub-repos, recorded as a named finding for plan 172-06 and Phase 173's honesty ledger"
affects: [172-06, 173]

actuals:
  tokens: 2600
  tasks: 1
  commits: 7

tech-stack:
  added: []
  patterns: ["GitHub rulesets created via `gh api --method POST --input <committed body file>`, one canonical JSON file feeding every ruleset creation", "Read GitHub state back from the API after every mutation, never from the settings page or the create response"]

key-files:
  created:
    - .planning/phases/172-policy-one-tracker-protected-main/evidence/172-05-ruleset-4998759-pre-delete.json
    - .planning/phases/172-policy-one-tracker-protected-main/evidence/172-05-ruleset-body.json
    - .planning/phases/172-policy-one-tracker-protected-main/evidence/172-05-actions-bypass-probe.txt
    - .planning/phases/172-policy-one-tracker-protected-main/evidence/172-05-prom-canary-readback.txt
  modified: []

key-decisions:
  - "D-09 revised mid-plan: the planned Integration:15368:always bypass actor (GitHub Actions app) was rejected by the API with HTTP 422 ('Actor GitHub Actions integration must be part of the ruleset source or owner organization') because henols is a personal User account, not an organization. Revised to {actor_id: null, actor_type: DeployKey, bypass_mode: always}, proven valid because the incumbent ruleset 4998759 already carries exactly that bypass type on the same account. Operator-approved 2026-09-01."
  - "The DeployKey bypass is currently inert: all three repos (firestarter_prom, firestarter, firestarter_app) measure zero deploy keys, so no person and no bot can use it today."
  - "Nothing irreversible happened in this plan. Ruleset 4998759 is still live and disabled on henols/firestarter; firestarter_app still has zero rulesets. Only henols/firestarter_prom received a new ruleset (id 22043478)."

requirements-completed: []

coverage:
  - id: D1
    description: "The incumbent ruleset 4998759 is captured into committed evidence before any other API call, so plan 172-06's one-way DELETE has a recovery record"
    verification:
      - kind: other
        ref: "gh api /repos/henols/firestarter/rulesets/4998759 > evidence/172-05-ruleset-4998759-pre-delete.json; jq -e '.id == 4998759'"
        status: pass
    human_judgment: false
  - id: D2
    description: "One canonical ruleset body exists as a committed file, revised once from an Integration bypass to a DeployKey bypass after the API rejected the former"
    verification:
      - kind: other
        ref: "evidence/172-05-ruleset-body.json — jq validation of enforcement, rules, bypass_actors, conditions"
        status: pass
    human_judgment: false
  - id: D3
    description: "henols/firestarter_prom carries exactly one ruleset, enforcement active, read back from the API"
    verification:
      - kind: other
        ref: "evidence/172-05-prom-canary-readback.txt — enforcement=active, rules=deletion,non_fast_forward,pull_request, bypass=DeployKey:null:always, include=~DEFAULT_BRANCH, can_bypass=never"
        status: pass
    human_judgment: false
  - id: D4
    description: "firestarter and firestarter_app are provably untouched by this plan"
    verification:
      - kind: other
        ref: "evidence/172-05-prom-canary-readback.txt — fw_rulesets=1, fw_id=4998759, app_rulesets=0"
        status: pass
    human_judgment: false
  - id: D5
    description: "D-09's premise (does an Actions bypass cover a GITHUB_TOKEN push) is settled, and the resulting release-workflow breakage is examined and accepted rather than ridden past"
    verification: []
    human_judgment: true
    rationale: "The premise was settled by the API's own validation error, not by the originally planned throwaway-repo probe. Whether the accepted consequence (both sub-repos' release flows break once 172-06 lands the ruleset) is an acceptable trade is an operator judgment call, made and recorded during the Task 2 checkpoint (approved)."

# Metrics
duration: 72min
completed: 2026-09-01
status: complete
---

# Phase 172 Plan 05: Ruleset Capture, Canonical Body, and Prom Canary Summary

**Captured the incumbent ruleset before anything could destroy it, then discovered and resolved mid-plan that the planned GitHub Actions bypass actor is rejected outright on a personal-account repository — revised to a DeployKey bypass and proved it live on `firestarter_prom`.**

## Performance

- **Duration:** 72 min
- **Started:** 2026-09-01T19:00:53Z
- **Completed:** 2026-09-01T20:13:00Z
- **Tasks:** 1 of 2 (Task 2 was the `blocking-human` checkpoint itself — approved, not a separate unit of work)
- **Files modified:** 4 evidence files created (one revised in place once)

## Accomplishments

- Captured ruleset `4998759`'s full JSON into evidence and committed it before any other API call — the only surviving record once plan 172-06 deletes it
- Wrote one canonical ruleset body as a committed file, so every ruleset in this phase is born from the same bytes
- Discovered, via a real HTTP 422, that the originally planned `Integration:15368:always` bypass actor (GitHub Actions app) cannot be created on any of the three repositories — all three are owned by the personal account `henols`, not an organization, and GitHub's validation requires the actor to be "part of the ruleset source or owner organization"
- Revised D-09 to a `DeployKey` bypass actor (`actor_id: null`, `bypass_mode: always`) on operator approval, proven valid because the incumbent `4998759` already carries exactly that bypass type on the same account
- Created the canary ruleset on `henols/firestarter_prom` (id `22043478`) from the revised body and read it back fresh from the API — `enforcement=active`, correct rule set, correct bypass, `can_bypass=never`
- Confirmed `henols/firestarter` still shows exactly one ruleset (`4998759`, `enforcement=disabled`, untouched) and `henols/firestarter_app` still shows zero rulesets — nothing irreversible happened in this plan

## Task Commits

Each step was committed atomically, in dependency order:

1. **Capture ruleset 4998759** - `5942f932` (docs) — the pre-delete recovery record, committed before any other API call
2. **Write canonical body (Integration bypass)** - `49cda60f` (docs) — the original D-09 design, later superseded
3. **Record Integration 422 rejection** - `2079a235` (docs) — the canary POST failed; nothing was created
4. **Revise body to DeployKey bypass** - `9502252e` (docs) — operator-approved D-09 revision
5. **Record D-09 revision + CI breakage finding** - `0b4dbe68` (docs) — the named finding for plan 172-06 and Phase 173
6. **Create canary and read back from API** - `a173f4ad` (docs) — `firestarter_prom` ruleset `22043478`, verified live

**Plan metadata:** (this commit) — SUMMARY + STATE

_Note: no code was written in this plan — every commit is `docs(172-05)` because the deliverable is GitHub control-plane state plus its evidence trail, not source._

## Files Created/Modified

- `evidence/172-05-ruleset-4998759-pre-delete.json` — the only surviving record of the incumbent ruleset once plan 172-06 deletes it
- `evidence/172-05-ruleset-body.json` — the one canonical POST body, revised once (Integration → DeployKey bypass actor) after the first attempt was rejected by the API
- `evidence/172-05-actions-bypass-probe.txt` — the full D-09 disposition: the original premise, the reproduced 422, the incumbent's DeployKey proof, the operator's revision decision, and the release-workflow breakage this revision causes
- `evidence/172-05-prom-canary-readback.txt` — the fresh API read-back proving the canary ruleset is live, correct, and that the other two repos are untouched

## Decisions Made

- **D-09 revised** from `Integration:15368:always` to `DeployKey:null:always`, on operator approval, after the API rejected the original actor type on this personal (non-organization) GitHub account. See "Deviations from Plan" below for the full trail.
- **Task 2's original A/B probe question became moot before it was asked**: the throwaway-repo probe was designed to test whether an Actions bypass covers a `GITHUB_TOKEN` push. The API's own validation error settled the actor-type question first — the Actions bypass could not be created at all on these repos, for any reason. No throwaway repository was created.
- **Proceed with the DeployKey bypass despite the known consequence.** Operator reviewed the canary outcome, the zero-deploy-key state, and the two named release-workflow breakages, and approved closing out this plan (Task 2 checkpoint: approved).

## Deviations from Plan

### Auto-fixed / Escalated Issues

**1. [Rule 4 - Architectural change] D-09's bypass actor design was rejected by the API and had to be revised**

- **Found during:** Task 1, the canary `POST /repos/henols/firestarter_prom/rulesets` call
- **Issue:** The plan's canonical body (per D-09 and `172-RESEARCH.md` Pattern 1) specified `bypass_actors: [{actor_id: 15368, actor_type: "Integration", bypass_mode: "always"}]` — the GitHub Actions app. GitHub rejected the create request with HTTP 422: `"Actor GitHub Actions integration must be part of the ruleset source or owner organization"`. Confirmed via `gh api /users/henols --jq '{login,type}'` → `{"login":"henols","type":"User"}`: all three target repositories are owned by the same personal account, which has no "owner organization" for this purpose.
- **Why this required a stop rather than an auto-fix:** the plan's `destructive_action_boundary` explicitly forbids inventing an alternate bypass-actor configuration without approval, and CONTEXT.md's D-09 had already deliberated and rejected the nearest alternative (admin bypass) for reasons that don't automatically extend to a DeployKey bypass. This was escalated as a `checkpoint:decision` (Rule 4) rather than resolved unilaterally.
- **Resolution:** the operator resolved it by directing a revision to `{actor_id: null, actor_type: "DeployKey", bypass_mode: "always"}`, citing the incumbent ruleset `4998759`'s own bypass entry (captured in this same plan) as proof that `DeployKey` validates on this account where `Integration` does not.
- **Files modified:** `evidence/172-05-ruleset-body.json` (revised in place), `evidence/172-05-actions-bypass-probe.txt` (documents both the rejection and the revision)
- **Verification:** the revised body was POSTed to `henols/firestarter_prom` and succeeded (id `22043478`); read back fresh from the API with all assertions passing (see `evidence/172-05-prom-canary-readback.txt`)
- **Committed in:** `2079a235` (rejection recorded), `9502252e` (body revised), `0b4dbe68` (revision + consequence recorded), `a173f4ad` (canary created and verified)

**Total deviations:** 1 escalated-and-resolved (Rule 4, operator-approved). **Impact:** the phase's bypass-actor design changed from an app-identity bypass to a deploy-key-type bypass. The immediate impact on this plan is none (the canary is live and correct). The impact on plan 172-06 and beyond is real and is recorded below as a named finding, not folded into this paragraph.

## Known Findings — Release Workflows Will Break (for Phase 173's ledger and backlog filing)

**This heading exists so a later reader — Phase 173's honesty ledger, or whoever files the backlog item — finds this without having to read prose.**

1. **`firestarter_app/.github/workflows/release.yml`** pushes a version-bump commit to `main` via the default `GITHUB_TOKEN` (`stefanzweifel/git-auto-commit-action@v5`, `on: push: branches: [main]`) on every push to `main`. Once plan 172-06 activates this same ruleset body on `henols/firestarter_app`, **that push will be rejected** — a `DeployKey` bypass does not cover a `GITHUB_TOKEN`-authenticated push, and the repository has zero deploy keys.
2. **`firestarter/.github/workflows/build.yml`** runs the identical auto-commit pattern below its "PUBLISH BOUNDARY" comment, gated `if: github.event_name == 'push' && github.ref == 'refs/heads/main'`. The `softprops/action-gh-release` publish step that follows depends on that push succeeding and **will not run** once the same breakage occurs there.
3. **This is a known, operator-accepted consequence**, not a defect discovered later. It was put to the operator explicitly at the Task 2 checkpoint and approved. It must not be described as "preserved" or "handled" by the bypass — it is breakage, accepted in exchange for a stronger honesty position (see below).
4. **Residual: the `actor_id: null` any-deploy-key caveat.** The DeployKey bypass currently grants nothing to anybody — all three repos measure zero deploy keys. But `actor_id: null` matches *any* deploy key, present or future. Adding a deploy key to any of the three repositories later would silently confer bypass on whatever process holds that key, with no further ruleset change required. Tracked here as a named residual against future deploy-key additions, not hidden by the null value.

Full narrative, dates, and the exact reproduced API responses live in `evidence/172-05-actions-bypass-probe.txt`.

## Threat Flags

| Flag | File | Description |
|------|------|--------------|
| threat_flag: elevation-of-privilege-residual | `evidence/172-05-ruleset-body.json` | `bypass_actors[0].actor_id: null` on a DeployKey bypass matches any deploy key added to the repository in the future, not just keys present today. Currently inert (zero deploy keys on all three repos) but is a standing residual risk that a future deploy-key addition would silently activate. |

## Next Phase Readiness

Ready for **plan 172-06** (delete `4998759`, create fresh rulesets on `firestarter` and `firestarter_app` from `evidence/172-05-ruleset-body.json`) with two carry-forwards it must account for:

1. The canonical body it reads is now the **DeployKey-bypass** version, not the Integration-bypass version the original phase design assumed.
2. Both sub-repos' release workflows **will break** the first time CI tries to auto-commit a version bump to `main` after their rulesets go active — 172-06 should surface this at its own checkpoint rather than let it be discovered at the next release.

## Self-Check: PASSED

- `evidence/172-05-ruleset-4998759-pre-delete.json` — FOUND, `.id == 4998759` verified
- `evidence/172-05-ruleset-body.json` — FOUND, DeployKey bypass verified
- `evidence/172-05-actions-bypass-probe.txt` — FOUND, both the rejection and the revision narrative present
- `evidence/172-05-prom-canary-readback.txt` — FOUND, all six assertions (`enforcement`, `rules`, `bypass`, `include`, `can_bypass`, `fw_id`/`app_rulesets`) pass
- Commits `5942f932`, `49cda60f`, `2079a235`, `9502252e`, `0b4dbe68`, `a173f4ad` all present in `git log --oneline`
- Live API re-check at close-out: `henols/firestarter_prom` returns exactly one ruleset (id `22043478`, `enforcement=active`); `henols/firestarter` returns exactly one ruleset (id `4998759`, `enforcement=disabled`, untouched); `henols/firestarter_app` returns zero rulesets
