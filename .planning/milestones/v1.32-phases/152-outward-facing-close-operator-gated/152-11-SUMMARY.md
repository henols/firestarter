---
phase: 152-outward-facing-close-operator-gated
plan: 11
subsystem: release-engineering
tags: [git, github-pr, merge-verification, cherry-oracle, checkpoint, beta-merge]

requires:
  - phase: 152-10
    provides: pre-merge git-cherry measurement, confirmed clean trees, green test suites
provides:
  - Both sub-repos merged to `beta` via pull request (firestarter #53, firestarter_app #53), both merge-commit method, both read back from the GitHub API
  - Post-merge `git cherry origin/beta HEAD` measured live, independently, in both repos — literal empty output in both, confirmed after the pre-release workflows' own auto-commit moved `origin/beta` a second time
  - Confirmation that none of the 5 already-upstream-by-patch-id commits was cherry-picked or dropped (all 5 still exist as commit objects in the app repo)
  - Confirmation both pre-release workflows completed with `conclusion: success`, with zero version numbers transcribed anywhere in this record
affects: [152-12]

tech-stack:
  added: []
  patterns:
    - "git cherry as the sole merge oracle (never merge-base --is-ancestor)"
    - "git merge-tree --write-tree as a side-effect-free local conflict oracle, independent of GitHub's mergeable field"
    - "A stale local branch named identically to a remote-tracking ref (here: local 'beta', 33 commits behind origin/beta) silently poisons a naive clone-and-merge test — always verify which ref a clone's 'origin/X' actually resolved to before trusting a dry-run merge"
    - "Under a merge-commit landing, git cherry origin/beta HEAD produces EMPTY OUTPUT, not '-' lines — every HEAD commit becomes an ancestor of beta, so cherry (which lists only commits in HEAD absent from upstream) has nothing to list. A plan's 'all -' phrasing presumes a rebase-style landing; empty output satisfies the same intent (nothing remains re-mergeable)."
    - "A beta pre-release workflow's own auto-commit step (version bump) lands a further commit ON TOP of the just-created merge commit, moving origin/beta a second time within minutes of the merge. This is additive, not subtractive, so git cherry stays empty across both origin/beta positions -- but it means 'the post-merge origin/beta SHA' is only stable once the workflow run's status is completed, not immediately after gh pr merge returns."

key-files:
  created:
    - .planning/phases/152-outward-facing-close-operator-gated/152-11-SUMMARY.md
  modified: []
  removed:
    - .planning/phases/152-outward-facing-close-operator-gated/152-11-BLOCKED.md

key-decisions:
  - "APPROVAL PROVENANCE, STATED PRECISELY (do not overstate): the operator's checkpoint answer was the literal string \"you decide\" — a delegation of the merge-method choice, not a named method and not a separate explicit acknowledgment of the publish consequence. The orchestrator then selected merge-commit (`--merge`) for both PRs from measured precedent (three recent two-parent merges: firestarter_app #51 -> 91c2add0, firestarter_app #52 -> eaca13ef, firestarter #52 -> bc3ca547) plus this plan's own git-cherry method-sensitivity. When the first `gh pr merge` attempt was denied by the harness's auto-mode classifier, the operator granted the missing permission (editing `.claude/settings.local.json`) and authorized a second time. A retry of the delegation to the plan executor was itself refused by the classifier on the first attempt after that grant, so **the orchestrator executed both `gh pr merge` commands directly**, rather than routing them back through the plan executor a second time."
  - "DEVIATION FROM THE PLAN'S EXECUTION MODEL (recorded, not hidden): Task 3's `<action>` assigns the merge itself to the plan executor (\"gh pr merge <n> ... for each\"). Because the delegation path was blocked by the tool-permission system on the executor side even after the operator's grant, the orchestrator performed the two merge calls itself, each guarded by a pre-merge state assert requiring the PR to read exactly `OPEN|MERGEABLE|CLEAN` before merging. Every other Task 3 action -- the post-merge git cherry verification, the parent-count read-back, the object-existence check on the 5 already-upstream commits, the workflow-completion confirmation, and this record -- was performed by the plan executor, independently re-measuring rather than transcribing the orchestrator's reported numbers."
  - "Every number the orchestrator reported was INDEPENDENTLY RE-MEASURED by this plan executor and found to agree exactly: both PR states (MERGED, same mergedAt timestamps, same mergeCommit OIDs), both merge commits' parent SHAs (2 parents each, read via `gh api repos/<owner>/<repo>/commits/<oid>`), the immediate post-merge `git cherry origin/beta HEAD` (empty, both repos), and the existence of all 5 previously-already-upstream commit objects (`git cat-file -t` returns `commit` for all 5 in firestarter_app). No disagreement was found between the orchestrator's reported numbers and this executor's own measurement."
  - "The plan's must_have literally reads \"git cherry origin/beta HEAD is all '-' in both sub-repos\" after the merge. What was actually observed, twice (immediately post-merge, and again after both pre-release workflows' auto-commit steps moved origin/beta a second time) is LITERALLY EMPTY OUTPUT in both repos, not any `-` lines. This is recorded as the literal finding, not force-read as \"all '-'\": under a merge-commit landing every commit that was on the milestone branch becomes an ancestor of the new origin/beta, and git cherry only lists commits reachable from HEAD but not from upstream, so an ancestor relationship produces nothing to list at all. The criterion's \"all '-'\" phrasing presumes a rebase-style (SHA-preserving, non-ancestor) landing; empty output satisfies the criterion's actual intent -- nothing on the milestone branch remains re-mergeable into beta -- and Plan 152-20 already states the check more accurately as \"only '-' lines (or no output)\"."
  - "origin/beta moved TWICE per repo within the same few minutes: once at the merge itself, and again shortly after when each repo's pre-release workflow's own auto-commit step (a version bump via git-auto-commit-action) landed a further commit on beta. Both moves were fetched and measured live; git cherry origin/beta HEAD stayed empty across both positions in both repos, because the second move is a descendant of the first (additive, not subtractive) -- confirming the criterion is robust to this expected CI side-effect rather than assuming it away."
  - "NO version number is transcribed anywhere in this document. Workflow completion was confirmed via `gh run list --json ...,status,conclusion` (both `status: completed`, `conclusion: success`) -- proving the two cuts fired successfully -- without ever reading `gh release list` or any tag/version string. Plan 152-12 reads both versions; this record states only THAT both cuts succeeded."
  - "Per must_haves.prohibitions, re-confirmed for Task 3: no `git merge-base --is-ancestor` invocation was used as an oracle anywhere in this task (git cherry and the GitHub API's parent-count read-back were the only oracles used). No cherry-pick, no drop of the 5 already-upstream commits -- their continued existence as commit objects was independently verified. No force-push. No push to `beta` by the plan executor at any point -- the two `gh pr merge` calls were made by the orchestrator, not by a `git push`, and the plan executor made zero write calls to either repo's `beta` ref. No `gh workflow run` was invoked -- both pre-release workflows fired automatically as a consequence of the merge, per each repo's own `on: push: branches: [beta]` trigger. The meta repo's PR was not created (152-20's job). No gitlink was re-pinned to `origin/beta` (milestone close's job). `.planning/STATE.md` and `.planning/ROADMAP.md` were not modified by this plan."

requirements-completed: []

coverage:
  - id: D1
    description: "Both PR URLs/numbers recorded; mergeable/mergeStateStatus measured before touching anything, and (for the app) confirmed clean via an independent local oracle, not GitHub's opinion alone"
    verification:
      - kind: other
        ref: "firestarter PR https://github.com/henols/firestarter/pull/53 (mergeable=MERGEABLE, mergeStateStatus=CLEAN after CI settled, later MERGED); firestarter_app PR https://github.com/henols/firestarter_app/pull/53 (mergeable=MERGEABLE, mergeStateStatus=CLEAN after CI settled, later MERGED); git merge-tree --write-tree origin/beta HEAD in firestarter_app exits 0 with a single tree SHA (7322a1e7...) and no CONFLICT markers"
        status: pass
    human_judgment: false
  - id: D2
    description: "git cherry re-measured live, both directions, both repos, matches Plan 152-10's baseline exactly pre-merge; post-merge git cherry origin/beta HEAD is empty in both repos, re-measured independently after both pre-release workflows completed"
    verification:
      - kind: other
        ref: "PRE-MERGE: firestarter 39 '+'/0 '-'; firestarter_app 80 '+'/5 '-' (same 5 SHAs as 152-10). POST-MERGE (measured twice, before and after each repo's version-bump auto-commit): git -C /workspaces/firestarter cherry origin/beta HEAD -> empty, rc=0; git -C /workspaces/firestarter_app cherry origin/beta HEAD -> empty, rc=0"
        status: pass
    human_judgment: false
  - id: D3
    description: "App test suite re-run with the sibling firmware root severed pre-merge (no conflict was found, but the re-run was performed anyway per the acceptance criterion); both merge commits' parent counts and the 5 already-upstream commits' continued existence independently verified post-merge"
    verification:
      - kind: other
        ref: "FIRESTARTER_FW_ROOT=<fresh empty tmpdir> python3 -m pytest -o addopts=\"\" -q -> 1762 passed, 63 skipped, 1 warning in 227.64s; gh api repos/henols/firestarter/commits/a1f474b5... -> 2 parents (7f6afc65be, d990a4ce80); gh api repos/henols/firestarter_app/commits/8f2e8d7d... -> 2 parents (f505ae77d2, a0bfd5e8b3); git cat-file -t on all 5 already-upstream SHAs in firestarter_app -> commit (all 5)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Both PRs MERGED via merge-commit method, read back from the API (not assumed from intent); both pre-release workflows fired and completed with conclusion=success; no version number transcribed; both merge methods, both post-merge origin/beta SHAs (both measured positions), and both workflow run ids recorded"
    verification:
      - kind: other
        ref: "gh pr view 53 --repo henols/firestarter --json state,mergedAt,mergeCommit -> MERGED, 2026-08-21T17:02:46Z, a1f474b5b3acd2f6fb246ec14ad6774dc52ced3f; gh pr view 53 --repo henols/firestarter_app --json state,mergedAt,mergeCommit -> MERGED, 2026-08-21T17:04:01Z, 8f2e8d7de709bf58c5e20daea34b17c073ee59b9; gh run list --repo henols/firestarter --limit 3 (Firestarter beta pre-release build, databaseId 32506085800, status completed, conclusion success); gh run list --repo henols/firestarter_app --limit 3 (Create a new beta pre-release, databaseId 32506199814, status completed, conclusion success); git rev-parse --abbrev-ref HEAD -> milestone branch in all three repos"
        status: pass
    human_judgment: false

# Metrics
duration: ~75min (Task 1 through Task 3, across the checkpoint pause and the classifier-permission blocker)
completed: 2026-08-21
status: complete
---

# Phase 152 Plan 11: Beta Merge — Both PRs Merged, git cherry Empty in Both Repos, Two Pre-Release Cuts Fired

**Opened both PRs against `beta`, measured the app PR's mergeability before touching anything and found it textually clean by two independent oracles (GitHub's own computation and a local `git merge-tree` dry run), so no hand conflict-resolution was needed. The blocking operator checkpoint was presented; the operator delegated the merge-method choice ("you decide"), the orchestrator chose merge-commit from measured precedent, and — after a harness permission denial on the first attempt and a subsequent operator grant — the orchestrator executed both `gh pr merge` calls directly rather than the plan executor, because the delegation path was blocked. Both PRs are now `MERGED`. Post-merge `git cherry origin/beta HEAD` is literal empty output in both repos, independently re-measured by this executor twice (immediately after the merge, and again after each repo's pre-release workflow's own version-bump auto-commit moved `origin/beta` a second time). Both pre-release workflows completed with `conclusion: success`. No version number appears anywhere in this document.**

This ships software-proven and unvalidated on silicon.

## Task 1 — PRs created, mergeability measured, no conflict found

### Firmware (`firestarter`) — clean fast-forwardable merge, as expected

```
$ git -C /workspaces/firestarter fetch origin --quiet
$ git -C /workspaces/firestarter rev-list --left-right --count origin/beta...HEAD
0	39
$ git -C /workspaces/firestarter cherry origin/beta HEAD | awk '{print $1}' | sort | uniq -c
     39 +
$ git -C /workspaces/firestarter status --porcelain
(empty)
```

Matches Plan 152-10's baseline exactly — no delta.

PR opened: **https://github.com/henols/firestarter/pull/53** — base `beta`, head `gsd/v1.32-at28c-write-path-root-cause-report-provenance`, 86 changed files, 39 commits.

```
$ gh pr view 53 --repo henols/firestarter --json mergeable,mergeStateStatus
(immediately after opening) {"mergeable":"MERGEABLE","mergeStateStatus":"UNSTABLE"}
(after CI settled)          {"mergeable":"MERGEABLE","mergeStateStatus":"CLEAN"}
```

`UNSTABLE` was CI-pending, not a conflict signal — confirmed via `gh pr checks 53 --repo henols/firestarter`, which showed two `build` jobs `pending` and two already `pass`; all four are `pass` as of the final check.

### Host app (`firestarter_app`) — real merge, textually clean

```
$ git -C /workspaces/firestarter_app fetch origin --quiet
$ git -C /workspaces/firestarter_app rev-list --left-right --count origin/beta...HEAD
7	85
$ git -C /workspaces/firestarter_app cherry origin/beta HEAD | sort
+ <80 SHAs, listed in full in the PR body>
- 94d327d2b2000294e57835b0c9c570dd7b81ff3e
- a7e554d603e9af33fb901606550445a222d49f4f
- c495e9854285115d7224e1a7743718a0e2b9ae04
- da6572b5daef9cea5878cf005324f6cd1ec1921e
- ebbc299654e4483656c031601ac08c18d34486fe
$ git -C /workspaces/firestarter_app status --porcelain
?? .planning/config.json
?? SECURITY.md
?? datasheets/M27C1001.pdf
?? datasheets/M27C512.pdf
?? datasheets/W27C512.pdf
?? datasheets/W27E257.pdf
?? write_test_port.sh
```

Matches Plan 152-10's baseline exactly, same 5 already-upstream-by-patch-id SHAs, same untracked set (the recorded pre-existing one).

PR opened: **https://github.com/henols/firestarter_app/pull/53** — base `beta`, head `gsd/v1.32-at28c-write-path-root-cause-report-provenance`, 86 changed files, 85 commits.

```
$ gh pr view 53 --repo henols/firestarter_app --json mergeable,mergeStateStatus
(immediately after opening, 5s poll) {"mergeable":"MERGEABLE","mergeStateStatus":"UNSTABLE"}
(after CI settled)                    {"mergeable":"MERGEABLE","mergeStateStatus":"CLEAN"}
```

`gh pr checks 53 --repo henols/firestarter_app` (final): `ci` pass ×2, `ci-py32` pass ×2, `security/snyk` pass.

**No `mergeStateStatus` value outside `CLEAN`/`UNSTABLE` (CI-pending) was ever observed on either PR — no `BLOCKED`, `DIRTY`, `BEHIND`, or `UNKNOWN` state occurred.**

### Independent local conflict oracle (because "GitHub said MERGEABLE" is not, by itself, the measurement standard this plan sets)

A first attempt used a throwaway `git clone` of the **local** `/workspaces/firestarter_app` checkout followed by `git merge origin/beta`, which reported `Already up to date` — a misleading result. Root-caused rather than trusted: the local repo carries a **stale local branch literally named `beta`** (`25b7255`, measured `[origin/beta: behind 33]` in `git branch -vv`), and a plain `git clone` of a local path copies the source's `refs/heads/*` into the clone's own `refs/remotes/origin/*`. The scratch clone's `origin/beta` therefore resolved to the **stale local branch**, not the real remote-tracking ref (`f505ae7`).

Corrected measurement, run directly in the real repo against the real ref, with zero working-tree side effects:

```
$ git -C /workspaces/firestarter_app rev-parse origin/beta
f505ae77d20337ba0a15f19ac0ccf1121527c81f
$ git -C /workspaces/firestarter_app merge-tree --write-tree origin/beta HEAD
7322a1e73fc1a8c81f4d5990f5b0f0640eb7ca4e
$ echo $?
0
```

Exit 0, a single resulting tree SHA, no `CONFLICT` section in the output. **Independently confirms GitHub's `mergeable: MERGEABLE` finding: the app merge is real (not a fast-forward) but has zero textual conflicts.** The 5 already-upstream-by-patch-id commits resolve without any hunk-level divergence — nothing was cherry-picked, nothing was dropped, and no hand conflict-resolution step was performed because none was needed.

**Because no conflict occurred, the "for every conflicted file: hunks/resolution/reason" acceptance criterion is vacuously satisfied — there is no conflicted file to record.**

### Post-check: app test suite re-run, sibling root severed

Run anyway (not skipped), because the plan's instruction is conditioned on "a conflict resolution can break a test" and the honest reading of that instruction, given a real (non-fast-forward) merge was confirmed clean rather than assumed clean, is to re-verify rather than to infer:

```
$ EMPTY_FW_ROOT=$(mktemp -d)
$ FIRESTARTER_FW_ROOT="$EMPTY_FW_ROOT" python3 -m pytest -o addopts="" -q
32 snapshots passed.
1762 passed, 63 skipped, 1 warning in 227.64s (0:03:47)
```

Identical count to Plan 152-10's two interpreter runs (1762 passed / 63 skipped). Working tree re-confirmed tracked-clean immediately after (`git status --porcelain | grep -v '^??'` empty).

### No `git merge-base --is-ancestor` used as an oracle

One informational-only `--is-ancestor` check was run purely to *diagnose* the stale-local-branch discrepancy above (to confirm the scratch clone's `origin/beta` really was the stale ref) — it was immediately superseded by `merge-tree` and is not relied on for any acceptance criterion or checkpoint claim. No other invocation appears anywhere in this task.

### Milestone-branch pushes (not `beta` pushes)

```
$ git -C /workspaces/firestarter push origin gsd/v1.32-at28c-write-path-root-cause-report-provenance
 * [new branch] gsd/v1.32-... -> gsd/v1.32-...
$ git -C /workspaces/firestarter_app push origin gsd/v1.32-at28c-write-path-root-cause-report-provenance
 * [new branch] gsd/v1.32-... -> gsd/v1.32-...
```

Both pushes target each sub-repo's own milestone branch on `origin`, solely so `gh pr create` had a head ref to point at. **Neither push touched `beta`.**

## Task 2 — Checkpoint presented and resolved (approval provenance, stated precisely)

The operator's checkpoint answer was the literal string **"you decide"** — a delegation of the merge-method choice, not a named method and not a separate, explicit acknowledgment of the publish consequence. The orchestrator then selected **merge commit (`--merge`) for both PRs** from measured precedent: every recent v1.31 milestone merge to `beta` in both repos (`firestarter_app` #51 → `91c2add0`, #52 → `eaca13ef`; `firestarter` #52 → `bc3ca547`) was a two-parent merge commit, and a merge commit is what makes `git cherry`'s post-merge criterion actually achievable (v1.30's PR #44 squash was the one-off exception that produced the project's known `--is-ancestor` false negative).

## Task 3 — Both PRs merged; the orchestrator executed the merge calls (deviation from the plan's execution model)

### The permission-denial-and-grant sequence, and who actually ran `gh pr merge`

The plan's `<action>` assigns `gh pr merge <n> --repo henols/<repo> --<method>` to the plan executor. On the first attempt, the executor's `gh pr merge 53 --repo henols/firestarter --merge` was denied by the harness's own auto-mode classifier — a tool-permission-system-level block, confirmed at the time to be independent of the checkpoint approval (read-only `gh pr view` continued to work; only the mutating call was refused). No workaround was attempted. This was reported back as a blocker.

**The operator then granted the missing permission** (editing `.claude/settings.local.json`) and authorized the merge a second time. A retry of the delegation to the plan executor was itself refused by the classifier on that first retry attempt, so **the orchestrator executed both `gh pr merge` commands directly**, each guarded by a pre-merge state assert that aborted unless the PR read exactly `OPEN|MERGEABLE|CLEAN`:

```
gh pr merge 53 --repo henols/firestarter     --merge   -> rc=0
gh pr merge 53 --repo henols/firestarter_app --merge   -> rc=0
```

**This is recorded as a deviation from the plan's execution model, not concealed:** Task 3 assigns the merge action to the plan executor; because the delegation path was blocked by the tool-permission system even after the operator's grant, the orchestrator performed the merge itself. Every other Task 3 action below — all verification, all read-back, all independent re-measurement — was performed by the plan executor, not the orchestrator.

### Independent re-measurement of every reported number (none transcribed without verification)

The orchestrator reported specific merge commits, parent SHAs, timestamps and `git cherry` results after performing the merges. Per this plan's own measured-not-assumed discipline, every one of those numbers was independently re-measured by the plan executor rather than transcribed:

```
$ gh pr view 53 --repo henols/firestarter --json state,mergedAt,mergeCommit,url
{"mergeCommit":{"oid":"a1f474b5b3acd2f6fb246ec14ad6774dc52ced3f"},"mergedAt":"2026-08-21T17:02:46Z","state":"MERGED","url":"https://github.com/henols/firestarter/pull/53"}

$ gh pr view 53 --repo henols/firestarter_app --json state,mergedAt,mergeCommit,url
{"mergeCommit":{"oid":"8f2e8d7de709bf58c5e20daea34b17c073ee59b9"},"mergedAt":"2026-08-21T17:04:01Z","state":"MERGED","url":"https://github.com/henols/firestarter_app/pull/53"}
```

Both match the orchestrator's reported values exactly.

**Merge-commit method, read back from the API, not assumed from intent** — parent-count verification:

```
$ gh api repos/henols/firestarter/commits/a1f474b5b3acd2f6fb246ec14ad6774dc52ced3f --jq '{sha,parents:[.parents[].sha]}'
{"parents":["7f6afc65be2022575989772cc0a5945611741831","d990a4ce80fcb56c9becf2312d1fe8757e1fc54d"],"sha":"a1f474b5b3acd2f6fb246ec14ad6774dc52ced3f"}

$ gh api repos/henols/firestarter_app/commits/8f2e8d7de709bf58c5e20daea34b17c073ee59b9 --jq '{sha,parents:[.parents[].sha]}'
{"parents":["f505ae77d20337ba0a15f19ac0ccf1121527c81f","a0bfd5e8b32989a60fc93b94e7b102506e6cf56f"],"sha":"8f2e8d7de709bf58c5e20daea34b17c073ee59b9"}
```

Both merge commits have exactly **2 parents** — the previous `origin/beta` tip and the milestone branch HEAD — confirming the merge-commit method independently of the orchestrator's report.

**Post-merge `git cherry`, measured live, immediately after the merge:**

```
$ git -C /workspaces/firestarter fetch origin --quiet
$ git -C /workspaces/firestarter rev-parse origin/beta
a1f474b5b3acd2f6fb246ec14ad6774dc52ced3f
$ git -C /workspaces/firestarter cherry origin/beta HEAD
(no output)
$ echo $?
0

$ git -C /workspaces/firestarter_app fetch origin --quiet
$ git -C /workspaces/firestarter_app rev-parse origin/beta
8f2e8d7de709bf58c5e20daea34b17c073ee59b9
$ git -C /workspaces/firestarter_app cherry origin/beta HEAD
(no output)
$ echo $?
0
```

**LITERAL RESULT: empty output, rc=0, in both repos.** Not `-` lines — nothing at all. This is reported exactly as observed, per the plan's explicit instruction not to force-read an empty result as "all `-`". See the "Handling the git cherry criterion" section below for why this is the expected and correct result under a merge-commit landing, and why it satisfies the criterion's intent.

**The 5 already-upstream-by-patch-id commits were neither cherry-picked nor dropped** — the merge resolved them, as required. Confirmed by object existence, not merely by absence from `git cherry`'s output:

```
$ cd /workspaces/firestarter_app
$ for sha in ebbc299654e4483656c031601ac08c18d34486fe da6572b5daef9cea5878cf005324f6cd1ec1921e 94d327d2b2000294e57835b0c9c570dd7b81ff3e a7e554d603e9af33fb901606550445a222d49f4f c495e9854285115d7224e1a7743718a0e2b9ae04; do echo -n "$sha -> "; git cat-file -t "$sha"; done
ebbc299654e4483656c031601ac08c18d34486fe -> commit
da6572b5daef9cea5878cf005324f6cd1ec1921e -> commit
94d327d2b2000294e57835b0c9c570dd7b81ff3e -> commit
a7e554d603e9af33fb901606550445a222d49f4f -> commit
c495e9854285115d7224e1a7743718a0e2b9ae04 -> commit
```

All 5 exist as `commit` objects. Nothing was removed from the object database.

### `origin/beta` moved a SECOND time — the pre-release workflows' own auto-commit, and why the criterion survives it

Immediately after the merge, each repo's pre-release workflow (`beta-build.yml` / `beta-release.yml`) started running (triggered automatically by the `push: branches: [beta]` event the merge itself produced — no `gh workflow run` was invoked by anyone). Each workflow's own auto-commit step (a version bump, via `git-auto-commit-action`) lands a further commit on `beta` once the workflow completes. Both were observed to fire and move `origin/beta` again within minutes of the merge, before this record was finalized:

```
$ gh run list --repo henols/firestarter --limit 1 --json status --jq '.[0].status'
in_progress   (first poll)
completed     (second poll, after a wait loop)

$ gh run list --repo henols/firestarter_app --limit 1 --json status --jq '.[0].status'
in_progress   (first poll)
completed     (second poll, after a wait loop)
```

Final, post-workflow-completion measurement — `origin/beta` moved again, and `git cherry` is re-measured against this new position too:

```
$ git -C /workspaces/firestarter fetch origin --quiet
$ git -C /workspaces/firestarter rev-parse origin/beta
88d204a5a023bcad6f708b33150502ba90fdec2b
$ git -C /workspaces/firestarter cherry origin/beta HEAD
(no output)
$ echo $?
0

$ git -C /workspaces/firestarter_app fetch origin --quiet
$ git -C /workspaces/firestarter_app rev-parse origin/beta
86f85d77d8102b633da82aef4b5601947f6cc80b
$ git -C /workspaces/firestarter_app cherry origin/beta HEAD
(no output)
$ echo $?
0
```

**Still empty in both repos, at this second `origin/beta` position too.** This is expected: the version-bump auto-commit is a descendant of the merge commit (additive on top of it), never a rewrite or a removal, so it cannot reintroduce any milestone commit as "ahead" of `beta`. The criterion is robust to this CI side-effect; it was measured across both positions rather than assumed to hold.

**The gitlink each sub-repo should eventually be pinned to** (recorded for the milestone close, per Task 3's acceptance criterion — not acted on here): `firestarter` → `88d204a5a023bcad6f708b33150502ba90fdec2b`; `firestarter_app` → `86f85d77d8102b633da82aef4b5601947f6cc80b`. **No gitlink was re-pinned by this plan.**

### Handling the `git cherry` "all `-`" criterion — literal finding, not force-read

The plan's must_have states: *"After both merges, `git cherry origin/beta HEAD` is all `-` in both sub-repos."* What was actually observed, in both repos, at both measured `origin/beta` positions, is **literal empty output** — not any `-` lines. This is recorded exactly as observed. The reason empty output is correct rather than a failure: `git cherry upstream HEAD` lists only commits reachable from `HEAD` that are **absent** from `upstream` by patch-id. Under a merge-commit landing, every commit that was on the milestone branch becomes an ancestor of the new `origin/beta` (via the merge commit's second parent), so there is nothing in `HEAD` that `origin/beta` doesn't already contain — the list is empty by construction, not populated with `-` markers. The criterion's "all `-`" phrasing implicitly presumes a rebase-style (SHA-preserving, non-ancestor) landing, which this milestone deliberately did not use (see Task 2's rationale). **Empty output satisfies the criterion's actual intent — nothing on the milestone branch remains re-mergeable into `beta`** — and Plan 152-20 already states the same check more accurately as "only `-` lines (or no output)."

### Two pre-release cuts fired — confirmed without reading any version number

```
$ gh run list --repo henols/firestarter --limit 3 --json databaseId,name,status,conclusion
[{"conclusion":"success","databaseId":32506085800,"name":"Firestarter beta pre-release build","status":"completed"}, ...]

$ gh run list --repo henols/firestarter_app --limit 3 --json databaseId,name,status,conclusion
[{"conclusion":"success","databaseId":32506199814,"name":"Create a new beta pre-release","status":"completed"}, ...]
```

Both repos' pre-release workflows ran to completion with `conclusion: success`. **No `gh release list` call was made, and no version/tag string was read or transcribed anywhere in this document.** Plan 152-12 reads both versions.

### Repo state after everything above

```
$ git -C /workspaces/firestarter status --porcelain | grep -v '^??'
(clean, ignoring untracked)
$ git -C /workspaces/firestarter_app status --porcelain | grep -v '^??'
(clean, ignoring untracked)
$ git -C /workspaces/firestarter rev-parse --abbrev-ref HEAD
gsd/v1.32-at28c-write-path-root-cause-report-provenance
$ git -C /workspaces/firestarter_app rev-parse --abbrev-ref HEAD
gsd/v1.32-at28c-write-path-root-cause-report-provenance
$ git -C /workspaces rev-parse --abbrev-ref HEAD
gsd/v1.32-at28c-write-path-root-cause-report-provenance
```

All three repos remain on the milestone branch, both sub-repos tracked-clean (only the recorded pre-existing untracked set present).

### No prohibited invocation appears anywhere in this task

No `git merge-base --is-ancestor` used as an oracle (`git cherry` and the API parent-count read-back were the only oracles). No cherry-pick or drop of the 5 already-upstream commits. No force-push. No push to `beta` by the plan executor (the merges were API-level `gh pr merge` calls made by the orchestrator, not a `git push` by anyone). No `gh workflow run` invoked. No meta-repo PR created. No gitlink re-pinned. No `.planning/STATE.md` or `.planning/ROADMAP.md` modification.

## The one-line no-re-merge handoff sentence, for Plan 152-12

**The beta merges for this milestone are complete; do not re-merge; verify with `git cherry`, never with ancestry.**

## Files Created/Modified

- `.planning/phases/152-outward-facing-close-operator-gated/152-11-SUMMARY.md` — this document (final; supersedes and replaces `152-11-BLOCKED.md`)
- `.planning/phases/152-outward-facing-close-operator-gated/152-11-BLOCKED.md` — removed (`git rm`), superseded by this SUMMARY; it held the interim halt report from when Task 3 was blocked and no longer describes current, correct state

## Deviations from Plan

### Auto-fixed / Process Deviations

**1. [Execution-model deviation, not a Rule 1-4 code fix] The orchestrator, not the plan executor, ran both `gh pr merge` commands.**
- **Found during:** Task 3, second attempt.
- **Issue:** The plan's `<action>` assigns `gh pr merge <n> --repo henols/<repo> --<method>` to the plan executor. The first attempt was denied by the harness's auto-mode classifier. The operator granted the missing permission and re-authorized, but a retry of the delegation to the plan executor was itself refused by the classifier on the first attempt after that grant.
- **Resolution:** The orchestrator executed both merge commands directly, each guarded by a pre-merge state assert (`OPEN|MERGEABLE|CLEAN`) matching the plan's own acceptance-criteria discipline. The plan executor then independently re-measured every resulting fact (PR state, merge-commit parent SHAs, post-merge `git cherry`, object existence of the 5 already-upstream commits, workflow completion) rather than transcribing the orchestrator's report — see coverage D4 and the "Independent re-measurement" section above.
- **Files modified:** none (GitHub-side state only).
- **Commit:** N/A (no local commit corresponds to a `gh pr merge` call; the merge commits themselves are `a1f474b5b3acd2f6fb246ec14ad6774dc52ced3f` (firestarter) and `8f2e8d7de709bf58c5e20daea34b17c073ee59b9` (firestarter_app), both on each sub-repo's `beta`, neither in this meta repo).

No other deviations. Task 1's conflict-resolution step was skipped because no conflict was found (a plan-anticipated branch, not a deviation) — this is documented in Task 1 above, not listed as a deviation.

## Issues Encountered

- The harness's auto-mode classifier denies `gh pr merge` by default, same as it denies `gh workflow run` — an undocumented-by-this-plan but consistent extension of the same protection class (irreversible public-publish actions). Resolved by an explicit operator permission grant, not by any workaround.
- A misleading local dry-run merge test (stale-branch-poisoned scratch clone) — root-caused and corrected in Task 1, documented above as a `key-decisions` / `tech-stack.patterns` entry for future plans to avoid repeating.

## User Setup Required

None further — the operator's permission grant (editing `.claude/settings.local.json`) already happened as part of resolving the Task 3 blocker; no other external configuration is needed.

## Next Phase Readiness

- Plan 152-12 (`152-MERGE-RECORD.md`) can cite this plan's measured facts directly: both PR numbers/URLs, both merge methods (read back from the API, both merge-commit with 2 parents), both post-merge `git cherry` results (empty, both repos, both measured `origin/beta` positions), both post-merge `origin/beta` SHAs and their intended future gitlink targets, both workflow run ids (databaseId 32506085800 firestarter, 32506199814 firestarter_app — both `conclusion: success`), and the verbatim no-re-merge handoff sentence above.
- Plan 152-12 must read both cut versions itself, from `gh release list`, after this plan — none is recorded here.
- The claim gate (`152-check-claims.py` over `_DEFAULT_TARGETS`, and `test_check_claims_152.py`) is verified green over this document below.

This ships software-proven and unvalidated on silicon.

## Self-Check: PASSED

- FOUND: `/workspaces/.planning/phases/152-outward-facing-close-operator-gated/152-11-SUMMARY.md`
- FOUND (via `gh pr view`): firestarter PR #53, state MERGED, mergeCommit `a1f474b5b3acd2f6fb246ec14ad6774dc52ced3f`
- FOUND (via `gh pr view`): firestarter_app PR #53, state MERGED, mergeCommit `8f2e8d7de709bf58c5e20daea34b17c073ee59b9`
- FOUND (via `gh api .../commits/<oid>`): both merge commits have exactly 2 parents each
- FOUND (via `git cherry`, re-measured live twice, both repos): empty output, rc=0, at both measured `origin/beta` positions
- FOUND (via `git cat-file -t`): all 5 already-upstream commit objects still exist in firestarter_app
- FOUND (via `gh run list`): both pre-release workflows `status: completed`, `conclusion: success`
- No commit SHA in the meta repo needs verification beyond this file's own commit (below) — this plan made no other local commits; the merge commits are in the sub-repos, already independently verified above.

---
*Phase: 152-outward-facing-close-operator-gated*
*Completed: 2026-08-21*
