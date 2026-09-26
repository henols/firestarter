---
phase: 193-the-deferred-claim-made-measurable
plan: 03
subsystem: infra
tags: [git, submodules, gitmodules, gate-03, archaeology, evidence]

requires:
  - phase: 189-free-the-name
    provides: "189-rename-03-fresh-clone.txt — the analog transcript shape and register this plan's transcripts follow"
provides:
  - "evidence/193-gate-03-fresh-clone.txt — the fresh-clone workaround, executed at the published v1.35 tag, plus a labelled reading of today's benign no-override behaviour"
  - "evidence/193-gate-03-existing-clone.txt — the existing-clone workaround, executed by checking a maintained clone back to v1.35 and showing the .git/config override outlive it"
  - "evidence/193-gate-03-submodule-sync-hazard.txt — the undocumented git submodule sync hazard, reproduced and repaired with both clobbered locations shown separately"
affects: [193-04]

actuals:
  tokens: 5129
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Transcript register from 189/192: ALL-CAPS title + ===== underline, snake_case_key(qualifier): value observables with full 40-char shas, capture_date: per reading, terminal verdict line exactly once at true end of file."
    - "A benign-today reading is captured in the same file as the workaround it exists for, explicitly labelled as a statement about today's world and not a demonstration of a failure (D-16's honesty constraint)."

key-files:
  created:
    - .planning/phases/193-the-deferred-claim-made-measurable/evidence/193-gate-03-fresh-clone.txt
    - .planning/phases/193-the-deferred-claim-made-measurable/evidence/193-gate-03-existing-clone.txt
    - .planning/phases/193-the-deferred-claim-made-measurable/evidence/193-gate-03-submodule-sync-hazard.txt
  modified: []

key-decisions:
  - "Used v1.35 as the pre-rename ref in all three transcripts, not the Phase 189 parent commit 9ccf0414. v1.35 is published and immutable. That parent commit lives only on the unpushed milestone branch and is unreachable in a fresh clone (D-16, 193-RESEARCH.md F-2)."
  - "Recorded the empty firestarter/ placeholder directory as the clean_state_proof. --no-recurse-submodules itself creates that directory. A fresh clone genuinely produces an empty directory there. The transcript states this so a reader does not mistake ordinary git behaviour for dirty state."
  - "Added a head(firestarter): <sha> observable beside the plan-named firestarter_head: key in each transcript. This gives a reading matching the pattern key(firestarter): <40-hex-sha>, which the plan's own verify block requires, without dropping the plan's own named key."
  - "Placed each terminal verdict line exactly once, at the true end of file. An earlier draft placed one after each reading. The plan's own verify block requires the exact count 1, so that draft would have failed."

requirements-completed: [GATE-03]

coverage:
  - id: D1
    description: "The fresh-clone workaround is executed at a published, immutable pre-rename ref: the .git/config override set before submodule init/update resolves the child to firestarter_fw despite the ref's own .gitmodules naming the old slug"
    requirement: GATE-03
    verification:
      - kind: integration
        ref: "evidence/193-gate-03-fresh-clone.txt READING 1, live git clone/checkout/config/submodule sequence against github.com"
        status: pass
    human_judgment: false
  - id: D2
    description: "Today's benign no-override behaviour is captured and explicitly labelled as a statement about today's world, not a demonstrated failure — no transcript claims a breakage that has not happened"
    requirement: GATE-03
    verification:
      - kind: integration
        ref: "evidence/193-gate-03-fresh-clone.txt READING 2, LABEL paragraph"
        status: pass
    human_judgment: true
    rationale: "D-16's honesty constraint is a judgment call about tone and framing (whether the LABEL text reads as 'today's world' rather than 'a demonstrated failure'), which the plan itself routes to a <human-check> rather than to grep."
  - id: D3
    description: "The existing-clone workaround is executed: a maintained clone's .git/config override survives a checkout back to v1.35 and is honoured by the subsequent submodule update, with the .gitmodules/.git-config divergence shown in two adjacent readings"
    requirement: GATE-03
    verification:
      - kind: integration
        ref: "evidence/193-gate-03-existing-clone.txt READING 1 and READING 2, live git sequence"
        status: pass
    human_judgment: false
  - id: D4
    description: "The git submodule sync hazard is reproduced (both .git/config and the child's own origin are clobbered) and repaired with the verified two-command sequence, with a durability check proving the repair is a repair and not a fix"
    requirement: GATE-03
    verification:
      - kind: integration
        ref: "evidence/193-gate-03-submodule-sync-hazard.txt READING 1/2/3 plus the durability check, live git sequence"
        status: pass
    human_judgment: false
  - id: D5
    description: "The operator's working clone at /workspaces is never mutated by any of this work — every command runs inside a disposable mktemp -d clone, and /workspaces' submodule.firestarter.url, firmware child origin, .gitmodules blob sha and both gitlinks read identically before and after all three tasks"
    requirement: GATE-03
    verification:
      - kind: other
        ref: "git -C /workspaces config --get submodule.firestarter.url, git -C /workspaces/firestarter remote get-url origin, git rev-parse HEAD:.gitmodules, git ls-tree HEAD firestarter firestarter_app — re-checked after every task against the orchestrator's pre-recorded values"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-09-14
status: complete
---

# Phase 193 Plan 03: GATE-03 `.gitmodules` Workarounds, Demonstrated Summary

**Three executed transcripts under `evidence/` prove both D-16 workarounds at the published `v1.35` tag: the fresh-clone override and the existing-clone override surviving a checkout. A third transcript reproduces the undocumented `git submodule sync` hazard and its verified two-command repair. The operator's working clone at `/workspaces` stayed untouched throughout.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-09-14T10:39:00Z
- **Completed:** 2026-09-14T10:51:00Z
- **Tasks:** 3
- **Files modified:** 3 (all new)

## Accomplishments
- Fresh-clone workaround executed at `v1.35`. Setting `git config submodule.firestarter.url` before `git submodule update --init` resolves the child to `firestarter_fw`. This works despite the ref's own `.gitmodules` naming the old slug. `git submodule init` was proven not to clobber a pre-set override.
- Today's benign no-override reading captured in the same file and explicitly labelled. A plain `git submodule update --init` at `v1.35` still succeeds today. GitHub's rename redirect is live — `gh api repos/henols/firestarter` and `repos/henols/firestarter_fw` return the same `id`. The transcript states plainly that this is today's world, not a demonstration of the trap.
- Existing-clone workaround executed. A maintained clone's `.git/config` override was set while `.gitmodules` still agreed with it. The override then survived a `checkout v1.35` where `.gitmodules` reverted to the old slug. The divergence between the two is captured in two adjacent readings. The subsequent `submodule update` followed the override.
- The undocumented `git submodule sync` hazard was reproduced. Running `sync` at a pre-rename ref clobbers both `.git/config`'s override AND the child's own `origin` remote. This is exactly the routine-hygiene command `.planning/notes/999.9-repo-rename-impact-analysis.md`'s own ordered procedure prescribes. The verified two-command repair was executed and shown to restore both. A durability probe proved a second `sync` immediately re-clobbers both — the repair is a repair, not a fix.
- The operator's working clone at `/workspaces` was proven untouched after every task. `submodule.firestarter.url`, the firmware child's `origin`, the `.gitmodules` blob sha (`5f68b4a1…`), and both gitlinks (`c67a3301…` firestarter, `560ec245…` firestarter_app) matched the orchestrator's pre-recorded values throughout.

## Task Commits

Each task was committed atomically:

1. **Task 1: A fresh clone at the published pre-rename ref, worked around and recorded** - `eee9312e` (docs)
2. **Task 2: An existing clone — the override outlives the checkout** - `b5225c1a` (docs)
3. **Task 3: The hazard that quietly undoes the workaround, reproduced and repaired** - `7a3d39bc` (docs)

**Plan metadata:** (this commit)

## Files Created/Modified
- `.planning/phases/193-the-deferred-claim-made-measurable/evidence/193-gate-03-fresh-clone.txt` - the fresh-clone workaround plus the labelled benign-today reading
- `.planning/phases/193-the-deferred-claim-made-measurable/evidence/193-gate-03-existing-clone.txt` - the existing-clone override surviving a checkout back to `v1.35`
- `.planning/phases/193-the-deferred-claim-made-measurable/evidence/193-gate-03-submodule-sync-hazard.txt` - the sync hazard, reproduced and repaired, with a durability check

## Decisions Made
- `v1.35` used as the pre-rename ref throughout, per D-16 and 193-RESEARCH.md F-2 — it is published, immutable, and reachable from a fresh clone, unlike the Phase 189 parent commit.
- The `clean_state_proof:` lines describe the empty placeholder directory `--no-recurse-submodules` itself creates, rather than asserting the path is absent, because that is what a genuinely clean fresh clone actually produces.
- Added a `head(firestarter): <sha>` observable in each transcript alongside the plan-named `firestarter_head:` key, so a reading matching the plan's own verify regex (`key(firestarter): <40-hex>`) exists without dropping the originally-named key.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added a `head(firestarter): <sha>` transcript key not in the plan's named-key list**
- **Found during:** Task 1 verification
- **Issue:** The plan's `artifacts_this_phase_produces` names `firestarter_head:` (no parenthetical qualifier) as the key holding the child's sha. But the plan's own `<verify>` block for Task 1 (and matching blocks in Tasks 2-3) greps for `^[a-z_]+\(firestarter\): [0-9a-f]{40}$`. That pattern needs a `(firestarter)` qualifier holding a sha. No key in the named list matches that shape. `gitmodules_url(firestarter)`, `config_url(firestarter)`, and `remote_origin(firestarter)` all hold URLs, not shas.
- **Fix:** Added `head(firestarter): <sha>` beside each existing `firestarter_head:` line in all three transcripts. This satisfies both the plan's named-key convention and its own verify regex.
- **Files modified:** all three evidence files
- **Verification:** `/usr/bin/grep -cE '^[a-z_]+\(firestarter\): [0-9a-f]{40}$'` returns non-zero on all three transcripts
- **Committed in:** `eee9312e`, `b5225c1a`, `7a3d39bc` (part of each task's commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** The fix reconciles two parts of the plan's own spec that did not otherwise share a key shape — a named key list and a verify regex. No scope creep. No new claim is made, and no new mechanism is demonstrated.

## Issues Encountered
- An initial draft of each transcript placed the terminal verdict line after every reading, not once at the true end of the file. The plan's own verify blocks require the exact count 1 for each verdict string. This was found and changed before any commit. No failed verify run occurred. No re-commit was needed.
- The ASD-STE100 lint hook flagged semicolons and word-choice rotation in transcript prose after each `Write`: `confirm`/`check`, `fetch`/`get`, `fix`/`repair`. Semicolons were split into separate sentences throughout. The `confirm`/`check` flag was resolved by using "confirm" every time. The `fetch`/`get` and `checkout`/`checked out` flags were left as-is where the flagged word names a literal git subcommand (`remote get-url`, `git checkout`), not a prose synonym choice. The `fix`/`repair` distinction in the sync-hazard transcript was kept on purpose. The plan's own action text requires exactly this contrast: "the repair is a repair and not a fix".

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
Three transcripts exist under `evidence/`. Each carries capture dates, full-sha observables, clean-state proofs preceding every submodule update, and a single terminal verdict line. Plan 193-04 can now write the `.gitmodules` archaeology-trap note citing these transcripts directly, per this plan's stated objective. No blockers.

---
*Phase: 193-the-deferred-claim-made-measurable*
*Completed: 2026-09-14*

## Self-Check: PASSED

- All three evidence files exist on disk (verified with `[ -f ]`).
- All three task commits (`eee9312e`, `b5225c1a`, `7a3d39bc`) are present in `git log --oneline --all`.
- All acceptance criteria and `<verify>` blocks for Tasks 1-3 re-ran and passed after the `head(firestarter):` fix.
- The plan-level `<verification>` items (execution over narration, published/immutable ref, clean-state proofs, unchanged working clone) hold, re-checked directly against `/workspaces` after Task 3.
- The `<human-check>` requirement (READING 2's LABEL reads as today's world, not a demonstrated failure) was reviewed and confirmed to hold.
- No credential material appears in any transcript (confirmed absent: private keys, tokens, passwords, SSH material).
- `/workspaces`' `submodule.firestarter.url`, `.gitmodules` blob sha, and both firmware/app gitlinks match the orchestrator's pre-recorded values exactly.
- No temp clones remain under `/tmp`.
