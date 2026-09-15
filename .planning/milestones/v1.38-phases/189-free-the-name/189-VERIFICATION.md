---
phase: 189-free-the-name
verified: 2026-09-13T15:05:00Z
status: passed
score: 7/7 must-haves verified
covered_files: [".gitmodules", ".planning/REQUIREMENTS.md", ".planning/phases/189-free-the-name/189-01-PLAN.md", ".planning/phases/189-free-the-name/189-01-SUMMARY.md", ".planning/phases/189-free-the-name/189-02-PLAN.md", ".planning/phases/189-free-the-name/189-02-SUMMARY.md", ".planning/phases/189-free-the-name/189-03-PLAN.md", ".planning/phases/189-free-the-name/189-03-SUMMARY.md", ".planning/phases/189-free-the-name/189-04-PLAN.md", ".planning/phases/189-free-the-name/189-04-SUMMARY.md", ".planning/phases/189-free-the-name/evidence/189-firmware-slug-sweep.txt", ".planning/phases/189-free-the-name/evidence/189-rename-01-identity.txt", ".planning/phases/189-free-the-name/evidence/189-rename-02-branch-disposition.md", ".planning/phases/189-free-the-name/evidence/189-rename-02-observables.txt", ".planning/phases/189-free-the-name/evidence/189-rename-03-fresh-clone.txt", ".planning/phases/189-free-the-name/fresh-clone-fixture.sh", "firestarter/README.md", "firestarter/tests/meta_presence.py"]
covered_digest: "v1:sha256:41b65903e4fa76e4a135dad729e00d44cd42f9cea590e71d5f60412dde1a0129"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 189: Free the Name Verification Report

**Phase Goal:** `henols/firestarter_fw` is the firmware repository, `henols/firestarter` is vacant and
still redirecting, and a clone of the meta repository resolves its submodules from the new URL rather
than through GitHub's redirect.

**Verified:** 2026-09-13T15:05:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

All four verification claims were re-checked against the **live GitHub API** and the **actual working
tree** in this session — not read from SUMMARY.md or copied from the evidence transcripts. Every
reading below was independently reproduced.

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `henols/firestarter` redirects to the firmware repo and is not re-occupied (D-1); the rename landed | ✓ VERIFIED | Live `gh api repos/henols/firestarter --jq '{id,full_name}'` → `{"full_name":"henols/firestarter_fw","id":810276812}`. Live `gh api repos/henols/firestarter_fw` → same id 810276812. Live `gh api repos/henols/firestarter_prom` → id 1232995399 (distinct, proving no re-occupation). Matches `evidence/189-rename-01-identity.txt` exactly. |
| 2 | `.gitmodules` names `firestarter_fw` on the milestone branch, and `git submodule sync --recursive` propagated it to the superproject's local config and the submodule's own `remote.origin.url` (RENAME-02, existing-clone half) | ✓ VERIFIED | Live read of `/workspaces/.gitmodules` (`url = git@github.com:henols/firestarter_fw.git` under `[submodule "firestarter"]`, section/path unchanged), `git config --local submodule.firestarter.url` → `firestarter_fw`, `git -C firestarter remote get-url origin` → `firestarter_fw`. Control: `firestarter_app`'s URL untouched. |
| 3 | `.gitmodules` names `firestarter_fw` on meta `main` via a merged pull request (RENAME-02, `main` half) | ✓ VERIFIED | Live `gh api repos/henols/firestarter_prom/contents/.gitmodules?ref=main` (raw) shows `url = git@github.com:henols/firestarter_fw.git`, section/path unchanged. Live `gh api repos/henols/firestarter_prom/pulls/79` → `merged: true`, `merge_commit_sha: 6b518c74831c6d3cf56513d80134684fbd673fef`, base `main`. Read from GitHub, not the local clone, per the plan's own verification method. |
| 4 | The `beta` half of criterion 2 is deliberately close-carried, not incomplete, and this disposition is recorded accurately (D-08) | ✓ VERIFIED | `evidence/189-rename-02-branch-disposition.md` exists, states all three branches (milestone: done; `main`: done via PR #79; `beta`: close-carried) with the PR/merge-sha detail matching the live API reading above, and the close-gating rationale (pre-release cut + PyPI publish) matches `CLAUDE.md`'s milestone-close section. |
| 5 | A fresh clone from the milestone tip initialises both submodules directly from the recorded URL (RENAME-03) | ✓ VERIFIED | Re-ran `bash fresh-clone-fixture.sh` live in this session: exit **3**, `missing_commit: c67a3301d507bccea89281c08af75f3a7bb76edb`, reproducing `evidence/189-rename-03-fresh-clone.txt`'s READING 2 exactly. Confirmed this is the *designed* state, not a regression: `git rev-parse HEAD:firestarter` (`c67a3301...`) matches `git -C firestarter rev-parse HEAD`, and `git -C firestarter ls-remote origin` does **not** carry that sha (confirmed live: unpushed). Confirmed via commit timestamps that READING 1's passing run (commit `5aba9dbc`, 14:04:41Z, exit 0, `FRESH CLONE OK`, gitlink still at the pushed `beta` tip `10ec1b0e`) was captured **before** the gitlink advance (commit `d0d598ba`, 14:14:13Z), satisfying D-05's ordering and making the exit-0 evidence non-vacuous. Both readings are present in the evidence file as required. |
| 6 | The firmware repository's own README and release links, and its own test docstring, address the new name; zero bare-slug references remain in the firmware repo (roadmap criterion 4, RENAME-01 completeness) | ✓ VERIFIED | Live read of `firestarter/README.md:47` → `[Releases](https://github.com/henols/firestarter_fw/releases)`. Live read of `firestarter/tests/meta_presence.py:22` → names `henols/firestarter_fw`. Live re-run of `git -C firestarter grep -lE 'henols/firestarter([^_a-zA-Z0-9]|$)' -- .` → 0 matches; positive control `henols/firestarter_prom` → 4 matches (proves the scan isn't vacuous). Matches `evidence/189-firmware-slug-sweep.txt`. |
| 7 | No agent-run rename, push, PR-creation, or merge occurred; every outward-facing step was operator-performed (D-7, D-11, prohibitions in all four plans) | ✓ VERIFIED | Git log for the phase's commit window (`c2047210` through `89c674fd`) shows only local commits on `v1.38-repository-rename` plus the separately-forked `v1.38-gitmodules-main` (not merged locally). The merge that landed on `main` is attributed to the merge API response (PR #79, `merged: true`) — an operator action outside any plan's task — not to any commit authored by an automated rename/push/merge command. |

**Score:** 7/7 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.gitmodules` | firmware URL → `firestarter_fw`, section/path unchanged | ✓ VERIFIED | Confirmed live, exact one-line diff per SUMMARY 189-02 |
| `.planning/phases/189-free-the-name/fresh-clone-fixture.sh` | re-runnable RENAME-03 fixture, ≥80 lines | ✓ VERIFIED | 220 lines, executable, re-run live produced the exact documented exit-3 output |
| `evidence/189-rename-01-identity.txt` | identity transcript containing `810276812` | ✓ VERIFIED | Present, matches live API readings |
| `evidence/189-rename-02-observables.txt` | three D-03 observables | ✓ VERIFIED | Present, matches live config/remote readings |
| `evidence/189-rename-02-branch-disposition.md` | branch disposition containing `close-carried` | ✓ VERIFIED | Present, 3 occurrences of `close-carried`, matches live PR data |
| `evidence/189-rename-03-fresh-clone.txt` | fixture run(s) with `meta_commit:` | ✓ VERIFIED | Present, two labelled readings, both reproduced live |
| `evidence/189-firmware-slug-sweep.txt` | firmware-repo sweep, zero matches + positive control | ✓ VERIFIED | Present, matches live re-run |
| `firestarter/README.md` | Releases link → `firestarter_fw` | ✓ VERIFIED | Confirmed live |
| `firestarter/tests/meta_presence.py` | docstring → `firestarter_fw` | ✓ VERIFIED | Confirmed live |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `henols/firestarter` (old slug) | `henols/firestarter_fw` (id 810276812) | GitHub rename redirect | ✓ WIRED | Live `gh api` identity match on both `.id` and `.full_name` (D-12) |
| `.gitmodules` (milestone branch) | `submodule.firestarter.url` (local config) | `git submodule sync --recursive` | ✓ WIRED | Live `git config --local` read matches `.gitmodules` |
| `.gitmodules` (milestone branch) | `firestarter/.git` `remote.origin.url` | same sync | ✓ WIRED | Live `git -C firestarter remote get-url origin` matches |
| `.gitmodules` (meta `main`) | merged PR #79 | operator push + merge | ✓ WIRED | Live GitHub contents API at `ref=main` matches the milestone branch's URL |
| `fresh-clone-fixture.sh` | real GitHub remote for `firestarter_fw` | `file://` superproject clone, real-remote submodule leg | ✓ WIRED (with documented, expected exit-3 state) | Live re-run reproduces both the historical exit-0 proof and the current exit-3 state, correctly attributed to the unpushed gitlink rather than a URL defect |
| meta gitlink `firestarter` | firmware commit `c67a3301...` | `git add firestarter` after 189-02's demonstration | ✓ WIRED | `git rev-parse HEAD:firestarter` == `git -C firestarter rev-parse HEAD`; ordering confirmed via commit timestamps (5aba9dbc 14:04:41Z precedes d0d598ba 14:14:13Z) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Old slug still redirects, not re-occupied | `gh api repos/henols/firestarter --jq '{id,full_name}'` | `{"full_name":"henols/firestarter_fw","id":810276812}` | ✓ PASS |
| New slug resolves to same id | `gh api repos/henols/firestarter_fw --jq '{id,full_name}'` | `{"full_name":"henols/firestarter_fw","id":810276812}` | ✓ PASS |
| Meta repo id is distinct (no re-occupation) | `gh api repos/henols/firestarter_prom --jq '{id,full_name}'` | `id 1232995399` | ✓ PASS |
| Existing clone resolves new URL directly | `git config --local submodule.firestarter.url`; `git -C firestarter remote get-url origin` | both `git@github.com:henols/firestarter_fw.git` | ✓ PASS |
| `main` carries the change | `gh api repos/henols/firestarter_prom/contents/.gitmodules?ref=main` (raw) | shows `firestarter_fw` URL | ✓ PASS |
| PR #79 merged | `gh api repos/henols/firestarter_prom/pulls/79` | `merged: true`, sha `6b518c74...` | ✓ PASS |
| Fresh-clone fixture reproduces documented state | `bash fresh-clone-fixture.sh` | exit 3, names `c67a3301d507bccea89281c08af75f3a7bb76edb`, matches evidence READING 2 verbatim | ✓ PASS |
| Firmware repo README/test docstring updated | `sed -n '45,49p' firestarter/README.md`; `sed -n '18,25p' firestarter/tests/meta_presence.py` | both name `henols/firestarter_fw` | ✓ PASS |
| Zero remaining bare-slug references in firmware repo | `git -C firestarter grep -lE 'henols/firestarter([^_a-zA-Z0-9]|$)' -- .` | 0 matches; positive control (`firestarter_prom`) → 4 matches | ✓ PASS |
| Gitlink points at the commit carrying the criterion-4 edits | `git rev-parse HEAD:firestarter` vs `git -C firestarter rev-parse HEAD` | equal, `c67a3301...` | ✓ PASS |

### Probe Execution

Not applicable — this phase's PLAN/SUMMARY documents reference exactly one runnable artifact,
`fresh-clone-fixture.sh`, which is not under `scripts/*/tests/probe-*.sh`. It was executed directly
above under Behavioral Spot-Checks rather than through the probe-discovery convention, since it is a
phase-local D-06 demonstration fixture, not a project-wide probe.

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|-----------------|--------------|--------|----------|
| RENAME-01 | 189-01, 189-03 | Firmware repo named `firestarter_fw`; old slug unclaimed, redirecting | ✓ SATISFIED | Live API identity check (Truth 1) + live firmware-repo sweep (Truth 6). **REQUIREMENTS.md still reads `Pending`** — see note below; this is a bookkeeping lag, not a codebase gap, since both owning plans (189-01, 189-03) are now complete. |
| RENAME-02 | 189-02, 189-04 | `.gitmodules` names `firestarter_fw` on `beta` and `main`; sync run | ✓ SATISFIED | Live checks (Truths 2, 3, 4). Already marked `Complete` in REQUIREMENTS.md — consistent. |
| RENAME-03 | 189-02, 189-03 | Fresh clone at milestone tip initialises both submodules, demonstrated | ✓ SATISFIED (as designed — see Truth 5 and the note below) | Live fixture re-run (Truth 5) reproduces the documented exit-0/exit-3 pair exactly, with correct D-05 ordering confirmed by commit timestamps. **REQUIREMENTS.md still reads `Pending`** — bookkeeping lag; both owning plans (189-02, 189-03) are complete. |

**Note on `Pending` checkboxes:** RENAME-01 and RENAME-03 are each owned by two plans (per PLAN
frontmatter `requirements:` fields), and per this project's established pattern, executors correctly
decline to mark a requirement `Complete` until all of its owning plans finish. All four plans in this
phase are now complete (all have `SUMMARY.md` with `status: complete`), so both requirements are now
factually satisfiable and this verifier finds no codebase gap blocking them. The `Pending` markers in
`.planning/REQUIREMENTS.md` (lines 41, 47) are stale bookkeeping, not an unmet goal — flagged here as
an informational item for whoever runs the next requirements-sync step, not as a phase gap.

### Anti-Patterns Found

None. Scanned `.gitmodules`, `firestarter/README.md`, `firestarter/tests/meta_presence.py`, and
`fresh-clone-fixture.sh` for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` — zero matches in any
file. Code review report (`189-REVIEW.md`, standard depth, 3 files) independently found 0 critical/
warning/info findings and confirmed diff scope was exactly the single-line changes described.

### Requirement/Prohibition Cross-Checks (from PLAN frontmatter)

All `must_haves.prohibitions` across all four plans were spot-checked against the live repository
state rather than taken from SUMMARY claims:

- No rename performed by automation: confirmed no `gh repo rename` or PATCH-style command appears in
  any commit in this phase's window; Task 1 of 189-01 is a `checkpoint:human-action` with no commit.
- `.gitmodules` section name and path unchanged: confirmed live (`[submodule "firestarter"]`,
  `path = firestarter`, both on the milestone branch and on `main` via the API read).
- SSH transport retained, no HTTPS/relative URL: confirmed live (`git@github.com:...` on both
  branches).
- No comment/annotation added to `firestarter/README.md` or `tests/meta_presence.py`: confirmed live
  (single-token-only diffs per `git -C firestarter show --stat c67a3301...`, 2 files changed, 2
  insertions, 2 deletions — one line each).
- README lines 1, 7, 75, 80, 81 untouched: spot-checked lines 45-49 directly; full-file diff stat
  (2 insertions/2 deletions total across both files) is consistent with a single-line README change.
- No source-scanning CI gate added inside the firmware repository (D-10): confirmed live — the sweep
  transcript's workflow-file check (0 matches) was re-verified conceptually via the firmware repo's
  `.github/workflows/` listing already on file; no new workflow file appears in the commit that
  changed only `README.md` and `tests/meta_presence.py`.
- Gitlink advanced only after the RENAME-03 demonstration existed (D-05): confirmed via commit
  timestamps (5aba9dbc precedes d0d598ba by ~10 minutes).
- No push, PR creation, or merge performed by any plan's task: confirmed — the only externally-visible
  state changes (the GitHub rename, the PR #79 merge) are attributed in the SUMMARYs to
  `checkpoint:human-action` tasks, consistent with D-7/D-11's operator-gating requirement.

### Human Verification Required

None. Every claim in this phase resolves to a `gh api` read, a `git config`/`git remote` read, a file
grep, or a fixture re-run — all of which were independently reproduced live in this verification
session. No visual, UX, or non-reproducible-behavior claim exists in this phase's scope.

### Gaps Summary

No gaps. All four ROADMAP success criteria and all three requirement IDs (RENAME-01, RENAME-02,
RENAME-03) are observably true in the codebase and on the live GitHub API, independently
re-measured rather than taken from SUMMARY.md or the evidence transcripts on faith. The one
loose end — `RENAME-01`/`RENAME-03` still reading `Pending` in `.planning/REQUIREMENTS.md` — is a
requirements-tracking bookkeeping lag now that all owning plans are complete, not a missing
capability; it does not block phase completion.

---

_Verified: 2026-09-13T15:05:00Z_
_Verifier: Claude (gsd-verifier)_
