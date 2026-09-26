---
phase: quick-260920-ib5
plan: 01
status: complete
subsystem: repo-docs
tags: [readme, main-branch, github, partial-scope]
requirements: [QUICK-260920-ib5]
dependency-graph:
  requires: []
  provides: ["local branch docs/readme-on-main with README.md commit"]
  affects: []
tech-stack:
  added: []
  patterns: ["throwaway git worktree for cross-branch file extraction without switching primary checkout"]
key-files:
  created: []
  modified: []
decisions:
  - "Task 2 (push + PR) was deferred during the executor run, then authorized by the operator and completed by the orchestrator: branch pushed, PR #93 opened against `main`, left unmerged. See the addendum at the end of this file."
metrics:
  duration: "~10 minutes"
  completed: "2026-09-20"
actuals:
  tokens: 9000
  tasks: 2
  commits: 0
  plan_head_before: "d8edf479"
---

# Quick Task 260920-ib5: README on main (Task 1 + Task 3 only) Summary

Built and committed a byte-identical copy of `beta`'s README.md onto a new local branch
`docs/readme-on-main`, forked off `origin/main`, inside a throwaway worktree — then removed the
worktree and verified the primary `/workspaces` checkout was untouched. The branch and its commit
now live only in `/workspaces`' local git database, not pushed to origin. This is a deliberate
partial-scope execution: the orchestrator gated Task 2 (push + PR) for later operator
authorization.

## Scope Executed

- **Task 1 — Build the README commit in a throwaway worktree off `origin/main`: EXECUTED.**
- **Task 2 — Push the branch and open the pull request against `main`: SKIPPED (deferred).**
- **Task 3 — Remove the worktree and prove the primary checkout is untouched: EXECUTED**, with one
  adaptation: the plan's own Task 3 action text says deleting the local branch afterward is
  "optional and harmless because origin carries it" — that assumption does not hold in this
  partial-scope run, since Task 2 never pushed anything to origin. The local branch was
  deliberately **kept** (not deleted) so the commit survives for the operator to push later. This
  matches the orchestrator's explicit scope-override instruction.

## What Was Built

- Local branch `docs/readme-on-main` in `/workspaces`, one commit ahead of `origin/main`
  (`6b518c74831c6d3cf56513d80134684fbd673fef`).
- Commit `bb08fd453c764f5061c98730e541fe5e3eb80595`:
  - Subject: `docs: add README to main`
  - Body: `main is the repository's default branch and renders the repository front page, but carried no README until now.`
  - Author: `Henrik Olsson <henols@gmail.se>` (the repo's configured git identity — no AI
    attribution anywhere in the commit).
  - Touches exactly one path: `README.md` (1 file changed, 35 insertions, 0 deletions).
  - `README.md` blob hash: `b0e303e4ec13391bb9654678951cad7c50afdeec` — verified equal to
    `git show origin/beta:README.md`, both via `git hash-object` after materializing the file and
    via `git rev-parse HEAD:README.md` after committing. Byte-identical, unedited, unreworded.

## Verification Run

Both automated `<verify>` legs from the plan were run as written (the operator's scope override
explicitly instructed running Task 1 and Task 3's verify legs and skipping Task 2's, since Task
2's verify queries `gh pr list` for a PR that does not exist):

- **Task 1 verify:** PASS — branch name, blob hash, single-file diff, correct parent
  (`origin/main` tip), `/workspaces` still on `v1.41-verification-to-host`, no attribution markers
  in commit message/author/email.
- **Task 3 verify:** PASS — worktree directory gone, `git worktree list` shows only
  `/workspaces`, HEAD still `v1.41-verification-to-host`, `/workspaces/README.md` unchanged
  (still the pre-existing `beta`-sourced blob), `.gitmodules` still tracked, and the pre/post
  `status --porcelain` diff (filtered of `.planning/quick/`) is byte-identical — confirmed by
  direct `diff` with zero output.

Submodule commit guard (`firestarter_fw firestarter_app`) was run immediately before the commit
and passed — the only staged path was `README.md`, which falls inside neither submodule.

No `git submodule init/update/sync` was run inside the throwaway worktree; its `firestarter` and
`firestarter_app` submodule directories were left empty, as required.

## Deviations from Plan

### Auto-fixed Issues

None — plan Task 1 and Task 3 executed exactly as written, with the one adaptation noted above
(keeping the local branch rather than treating its deletion as harmless, since it is not yet
mirrored to origin).

### Scope Deviation (Orchestrator-Directed, Not a Rule 1-4 Deviation)

Task 2 was not attempted at all — no `git push`, no `gh pr create`, no `$SCRATCH/pr-body.md` was
written, and Task 2's verify leg was not run. This was a direct instruction in the orchestrator's
scope override, not a deviation discovered during execution.

## Task 2 — DEFERRED, Not Failed, Not Forgotten

Task 2 (push the branch, open the PR against `main`) requires operator authorization of the
push/ship gate and was intentionally not executed. Everything Task 2 needs is ready and waiting in
`/workspaces`:

- Branch `docs/readme-on-main` exists locally at commit `bb08fd453c764f5061c98730e541fe5e3eb80595`,
  one commit ahead of `origin/main`.
- The PR body text is specified verbatim in the plan's `<pr_description>` block (87 words, already
  within the 50-120 word band required by `/workspaces/CLAUDE.md` § "Pull requests and merge
  requests").

**Exact commands the operator would run to complete Task 2**, from `/workspaces`:

```bash
BR="docs/readme-on-main"

# 1. Write the PR body verbatim from the plan's <pr_description> block to a scratch file, e.g.:
cat > /tmp/pr-body.md <<'EOF'
`main` is the repository's default branch, so github.com/henols/firestarter currently renders no README on its front page. This adds the README that already lives on `beta`, unchanged, so visitors landing on the default branch get the project description, a link to the wiki, and pointers to the firmware and CLI repositories.

- Adds `README.md` only; no other file is touched.
- Byte-identical to the copy on `beta`, so the two branches do not diverge.
- No workflow is triggered: the repository's only main workflow is path-filtered to `tools/catalog/**`.
EOF

# 2. Push the branch (from /workspaces directly, since the branch already exists there locally —
#    no worktree needed for this step)
git -C /workspaces push -u origin "$BR"

# 3. Open the PR with an explicit --base main
gh pr create -R henols/firestarter --base main --head "$BR" \
  --title "docs: add README to main" --body-file /tmp/pr-body.md

# 4. Do NOT merge, do NOT enable auto-merge, do NOT create a tag or GitHub Release.
#    Merging is the operator's call.
```

After pushing and opening the PR, Task 2's own `<verify>` block in the plan
(`260920-ib5-PLAN.md`) can be run to confirm: PR state `OPEN`, base `main`, head
`docs/readme-on-main`, `mergedAt` null, changed files exactly `README.md`, body word count in
[50, 120], and no AI attribution markers in the PR body.

## Threat Model Coverage (Partial Scope)

Of the six threats in the plan's STRIDE register, this partial run covers:

- **T-quick-ib5-01** (Tampering — commit contents): mitigated and verified — single-path staging,
  Task 1 verify confirms exact file list and parent commit.
- **T-quick-ib5-02** (Information disclosure — milestone files leaking): mitigated and verified —
  worktree checked out from `origin/main` never had milestone-v1.41 files present; Task 3's
  pre/post diff confirms zero leakage.
- **T-quick-ib5-03** (Repudiation — attribution): mitigated and verified for the commit (author,
  message). The PR-body half of this threat does not apply yet since no PR exists.
- **T-quick-ib5-06** (Tampering — submodule layout): mitigated and verified — no submodule
  commands run, Task 3 status diff confirms no submodule directory churn in `/workspaces`.
- **T-quick-ib5-04** (Elevation of privilege — branch protection bypass) and **T-quick-ib5-05**
  (DoS — stray tag/Release starving `fw` update checks): not yet applicable — no push, no PR, no
  tag, no Release occurred in this run. Both remain relevant when Task 2 eventually executes.

## Self-Check

```
FOUND: /workspaces (branch docs/readme-on-main exists, commit bb08fd453c764f5061c98730e541fe5e3eb80595)
FOUND: git -C /workspaces branch --list docs/readme-on-main → prints the branch
FOUND: git -C /workspaces rev-parse docs/readme-on-main → bb08fd453c764f5061c98730e541fe5e3eb80595
FOUND: worktree removed — git -C /workspaces worktree list shows only /workspaces
FOUND: /workspaces still on v1.41-verification-to-host, status --porcelain unchanged outside .planning/quick/
```

## Self-Check: PASSED

---

## Addendum — Task 2 completed by the orchestrator (2026-09-20, after this summary was written)

Everything above describes the executor's partial-scope run and remains an accurate record of it.
Task 2 did not stay deferred. After the executor returned, the operator was asked to rule on the
push/ship gate and chose **"Push branch + open PR, don't merge."** The orchestrator then executed
Task 2 directly.

**What ran**

- `git push origin docs/readme-on-main:docs/readme-on-main` — refspec-scoped, so no tag and no
  other ref could ride along. Remote ref confirmed at `bb08fd453c764f5061c98730e541fe5e3eb80595`,
  identical to the local commit.
- PR body written verbatim from the plan's `<pr_description>` block. `wc -w` = 87, inside the
  50–120 band; attribution grep over the body returned 0 matches.
- `gh pr create -R henols/firestarter --base main --head docs/readme-on-main --title "docs: add
  README to main" --body-file …` → **https://github.com/henols/firestarter/pull/93**

**Verified after the fact**

| Check | Result |
|---|---|
| PR state | `OPEN`, `mergedAt` null, `isDraft` false, `autoMergeRequest` none |
| Base / head | `main` / `docs/readme-on-main` |
| Changed files | `README.md`, and nothing else |
| GitHub Releases in meta repo | none — `gh release list` empty |
| `origin/main` | still `6b518c74`, unmoved |
| `/workspaces` checkout | still on `v1.41-verification-to-host`, milestone work intact |

**Left for the operator:** merging PR #93. It was deliberately not merged, not approved, and
auto-merge was not enabled.
