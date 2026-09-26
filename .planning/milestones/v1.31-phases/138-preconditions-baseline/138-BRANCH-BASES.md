# Phase 138 Plan 01: Branch Bases — PREP-01 / PREP-02 Adjudication

**Owner requirement:** PREP-01 (`firestarter_app`'s v1.30 branch merged into `origin/beta`, verified)
and PREP-02 (milestone branches exist in all three repos off their decided bases, each verified by
naming the base commit, not assumed).

**Measured:** 2026-08-08, this session, live and read-only. Per the plan's own instruction, nothing
below is copied from `138-RESEARCH.md` — every command was re-run fresh, and any divergence from
research's recorded figures is stated explicitly rather than reconciled.

---

## Section 1: Oracles

All commands below were run in `/workspaces/firestarter_app` after `git fetch origin beta` (see
Section 3 for the fetch itself). No branch was created, switched, pushed, merged, or deleted by any
command in this section — measurement only.

| Oracle | Command (as run) | Result |
|--------|-------------------|--------|
| 1. GitHub PR record | `gh pr view 44 --repo henols/firestarter_app --json state,mergedAt,mergeCommit` | `state=MERGED`, `mergedAt=2026-08-05T21:13:01Z`, `mergeCommit.oid=568e58b903338d6e9191b2a165fa0e876c1c84dc` |
| 1b. Merge-commit parent count | `git log -1 --format='%h parents=[%p]' 568e58b` | `568e58b parents=[16a313a]` — **single parent**, confirming a squash (a true merge would show 2 parents) |
| 2. Ancestry | `git merge-base --is-ancestor gsd/v1.30-sdp-surface-retirement origin/beta` | **exit 1** — measured, not assumed. This is the squash-merge false negative (see Section 2 mechanism) |
| 2b. Unmerged commit count | `git rev-list --count origin/beta..gsd/v1.30-sdp-surface-retirement` | **85** |
| 3. Content equivalence (forward, load-bearing) | `comm -23 <(git ls-tree -r --name-only gsd/v1.30-sdp-surface-retirement \| sort) <(git ls-tree -r --name-only origin/beta \| sort)` | **EMPTY — 0 lines.** Zero files exist on the v1.30 branch that are absent from `beta`. |
| 3b. Content equivalence (reverse) | `comm -23 <(git ls-tree -r --name-only origin/beta \| sort) <(git ls-tree -r --name-only gsd/v1.30-sdp-surface-retirement \| sort)` | 2 files present on `beta` and absent from the v1.30 branch: `tests/test_chip_test_blank_check_order.py`, `tests/test_hw_revision_gate.py` — both added by later `beta` PRs (#50, #45 respectively), not evidence of missing v1.30 content |
| 4. Attributable diff | `git diff --stat gsd/v1.30-sdp-surface-retirement origin/beta` | **15 files changed, 1114 insertions(+), 274 deletions(-)** — every file attributable to `beta`'s later PRs #45/#46/#48/#49/#50 plus the `Apply automatic changes` version-bump commits (see Section 2 for the full attribution and the divergence from `138-RESEARCH.md`'s recorded 12-file figure) |
| Supplementary A. Patch-id check | `git cherry origin/beta gsd/v1.30-sdp-surface-retirement \| awk '{print $1}' \| sort \| uniq -c` | `85 +` — **all** 85 commits show as `+` (not found on the other side by patch-id), which is the expected signature of a squash merge, not evidence of non-merger |
| Supplementary B. Re-merge conflict proof | `git merge-tree $(git merge-base origin/beta gsd/v1.30-sdp-surface-retirement) origin/beta gsd/v1.30-sdp-surface-retirement \| grep -E '^(changed\|added) in both'` | 4× `changed in both` (`firestarter/chip_test.py`, `tests/conftest.py`, `tests/test_chip_test.py`, plus one more) and **1× `added in both`: `tests/test_chip_test_sdp_leg.py`** — blob `a9215055…` (ours) vs `e443e56c…` (theirs), different content. This is a genuine, unavoidable conflict under git's default merge — a re-merge is not merely unnecessary, it is actively harmful. |

---

## Section 2: F-138-01 — PREP-01 discharged as content equivalence rather than ancestry

**Mechanism.** A GitHub squash merge creates a single new commit on the target branch (`568e58b`)
whose only parent is the target branch's pre-merge tip (`16a313a`) — **none** of the 85 source-branch
commits are its ancestors. `git merge-base --is-ancestor SOURCE TARGET` walks TARGET's ancestry
looking for SOURCE's tip; because the squash commit's parent chain never touches the source branch's
commit objects, the walk fails and the command **exits 1**. This is a **false negative**: it correctly
reports "SOURCE is not an ancestor of TARGET" while the content SOURCE introduced **is** present on
TARGET. `git cherry`'s "all 85 `+`" result is the same mechanism from a different angle — patch-ids
are computed per-commit, and a squash collapses 85 patches into 1, so none of the 85 individual
patch-ids can match anything on the squashed side.

**Verdict.** v1.30's app content **is** on `beta`. Oracle 3 (forward `comm -23`, empty) is the
load-bearing proof: there is no file that exists on the v1.30 branch and not on `beta`. Oracles 1, 2b,
and Supplementary A corroborate the *mechanism* (a real, GitHub-recorded squash merge, 85 commits,
uniform patch-id mismatch); oracle 3 forward proves the *outcome* (nothing missing). Oracle 4 and
oracle 3-reverse show `beta` is **strictly ahead** of the v1.30 branch, by content that arrived via
five later PRs (#45, #46, #48, #49, #50) plus version-bump automation — not by anything the v1.30
branch still lacks.

**Requirement wording correction (OD-1).** PREP-01's literal text requires
`git merge-base --is-ancestor` to exit 0. That criterion is **unreachable without a redundant
re-merge**, and Supplementary B proves that re-merge would **conflict**
(`tests/test_chip_test_sdp_leg.py`, added independently on both sides with different blobs — git's
default 3-way merge cannot auto-resolve an "added in both, different content" case). The requirement
is corrected, per OD-1, from an **ancestry** criterion to a **content-equivalence** criterion: PREP-01
is satisfied when the four oracles above jointly show (a) a real, GitHub-recorded merge occurred, (b)
it was a squash (explaining the ancestry false negative), and (c) zero files from the source branch
are absent from the target. All three hold, measured live, above.

**D-08 is a no-op.** D-08 specified "agent opens PR, operator merges." **No PR was opened by this
plan and no operator merge was requested or performed** — `git -C /workspaces/firestarter_app log
--oneline -1` (checked below) shows no commit produced by this task; the merge D-08 anticipated had
**already happened**, via PR **#44**, five days before this phase ran. D-08's own "known and accepted
consequence" — that landing the merge would fire `beta-release.yml` and cut a new app pre-release —
**already happened** for the same reason: `beta`'s live tip carries version string
`3.0.0b20` (read live from `firestarter/__init__.py` at `origin/beta`, i.e. `firestarter/__version__ =
"3.0.0b20"`), reached via five `Apply automatic changes` auto-commits sitting on the merge:
`4beda79`, `25b7255`, `6338655`, `04f63de`, `4d18b64` (oldest to newest; `4d18b64` is the live tip
itself). This is exactly the pre-release D-08 flagged as an accepted consequence — it is not a
surprise to be discovered here, and no correction is required of it.

`.planning/v1.30-PR-BODY.md` (the staged, never-opened PR body D-08 was going to open) **remains on
disk as an unused draft** and is **not deleted by this phase** — it stays as an accurate historical
record of what D-08 intended, alongside this finding's record of what actually happened instead.

**Why this re-measurement found more drift than `138-RESEARCH.md` recorded (D-06 evidence
discipline).** Research's own oracle-4 diff recorded **12** files; this session's oracle 4 (Section 1,
row 4) measured **15**. Both are correct measurements — they were taken against different refs, not
different states of the same ref. Research computed `git diff --stat` against a **cached**
`origin/beta` (`04f63de`, fetched 2026-08-07 17:55) that predates PR **#50**
(`fix(dev test): run blank-check after erase…`, merged after research ran). This session's Step 0
`git fetch origin beta` updated the local cache to the truly live tip (`4d18b64`) **before** any oracle
ran, so oracle 4 here correctly attributes **one PR more** than research could see: the three extra
files (`tests/test_chip_test_blank_check_order.py` new, plus `firestarter/chip_test.py`,
`tests/conftest.py`, `tests/test_chip_test.py` modified) are PR #50's content. The **live remote
tip itself did not move between research and now** — both measured `4d18b64` — the divergence is
purely that research's diff ran against a stale local cache while this session's diff ran
post-fetch. Recorded here per D-06 rather than silently reconciled into research's number.

---

## Section 3: Live tips versus local caches

Both fetches below were run in Step 0, before any oracle command. `gh api` reads used the GitHub REST
API directly and never modify any local ref.

| Repo | Cached `origin/beta` (before fetch, this session) | Cached `origin/beta` (after fetch, this session) | Live `beta` (`gh api …/git/refs/heads/beta`) | Drift (cached-before → live) | Matches `138-RESEARCH.md`'s recorded live tip? |
|------|----------------------------------------------------|----------------------------------------------------|-----------------------------------------------|-------------------------------|--------------------------------------------------|
| `firestarter` | `30850845f9c0994706f28d2a74fccc3adbb4b387` (`3085084`) | `6fab4eafdcd0981d24fddc3ff177abc5c74e313c` (`6fab4ea`) | `6fab4eafdcd0981d24fddc3ff177abc5c74e313c` (`6fab4ea`) | **2 commits ahead** | Yes — `6fab4ea`, unchanged since research; no further remote drift |
| `firestarter_app` | `04f63de636231412fabd0d69ee7211bbbd6de93c` (`04f63de`) | `4d18b645ab18a2d2465f0f623062e9249eb24132` (`4d18b64`) | `4d18b645ab18a2d2465f0f623062e9249eb24132` (`4d18b64`) | **2 commits ahead** | Yes — `4d18b64` (`3.0.0b20`), unchanged since research; no further remote drift |

**Fetch route used for both repos: `git fetch origin beta` succeeded in both submodules** (this
session; no network failure was encountered). Because the fetch succeeded,
`git -C /workspaces/firestarter_app cat-file -e 4d18b645ab18a2d2465f0f623062e9249eb24132` and
`git -C /workspaces/firestarter cat-file -e 6fab4eafdcd0981d24fddc3ff177abc5c74e313c` both succeed —
each live tip is now a local object. The `gh api compare` fallback route named in the plan (for use if
the firmware fetch is unavailable) was **not needed**, but was **additionally run** for the firmware
repo as a cross-check (see below) — both routes agree.

**Local `beta` branch state (read-only observation):**

| Repo | Local `beta` branch exists? | Local `beta` pinned at |
|------|-------------------------------|--------------------------|
| `firestarter` | yes | `3085084` (the OD-2 decided fork base — see Section 4) |
| `firestarter_app` | yes | `25b7255` — 4+ commits behind live `origin/beta` |

**Firmware drift enumeration, decided base `3085084` → live tip `6fab4ea`**
(`gh api repos/henols/firestarter/compare/3085084...6fab4ea`, 2 total commits — matches
`138-RESEARCH.md` exactly, confirming no further firmware-side drift since research):

| Commit | Message | Files (additions/deletions) |
|--------|---------|-------------------------------|
| `b1737b2` | `feat(protocol): carry HW revision + FW identity in the MSG_OK_READY ack (#49)` | `src/firestarter.cpp` +37/−1 |
| `6fab4ea` | `Apply automatic changes` | `include/version.h` +1/−1 |

This drift and its size-gate consequence are carried forward as **F-138-02** in Section 5 (Task 2).

**Nothing in this section created, switched, pushed, merged, or deleted any branch.**
`git -C /workspaces/firestarter_app log --oneline -1` and
`git -C /workspaces/firestarter log --oneline -1` were checked and show no commit produced by this
task's measurement work.

---

## Section 4: The three verified bases

Per **D-09**, all three repos carry the **identical branch slug**
`gsd/v1.31-27c-programming-algorithm-fidelity`. Per **OD-2**, each base was re-verified rather than
assumed — none was copied from `138-RESEARCH.md` or from `138-CONTEXT.md`'s now-superseded "verified
during this discussion" bullets.

| Repo | Branch | Base commit (full SHA) | How verified |
|------|--------|--------------------------|----------------|
| meta (`/workspaces`) | `gsd/v1.31-27c-programming-algorithm-fidelity` | `d0f0c6a056efaa3537909d8ff90492f3792403f1` | `git rev-parse gsd/v1.30-sdp-surface-retirement` → `00af577193cdb75d9f0a0743a37a349a39fc97dd`; `git rev-parse gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof` → `d0f0c6a056efaa3537909d8ff90492f3792403f1`; `git merge-base --is-ancestor d0f0c6a0… gsd/v1.31-…` exits **0**; `git merge-base d0f0c6a0… gsd/v1.31-…` returns **exactly** `d0f0c6a0…` (the fork point, not merely an ancestor) |
| `firestarter` (`/workspaces/firestarter`) | `gsd/v1.31-27c-programming-algorithm-fidelity` | `30850845f9c0994706f28d2a74fccc3adbb4b387` | `git cat-file -e 3085084` resolves; `git merge-base --is-ancestor 3085084 6fab4ea` (live tip) exits **0**; branch created with `git checkout -b … 3085084` (worktree had zero tracked modifications, confirmed by `git status --porcelain \| grep -v '^??'` returning empty before the switch); `git rev-parse gsd/v1.31-…` → `30850845…`; `git symbolic-ref --short HEAD` → `gsd/v1.31-27c-programming-algorithm-fidelity` |
| `firestarter_app` (`/workspaces/firestarter_app`) | `gsd/v1.31-27c-programming-algorithm-fidelity` | `4d18b645ab18a2d2465f0f623062e9249eb24132` | live tip re-read via `gh api …/git/refs/heads/beta` immediately before branch creation (`4d18b64…`, identical to Section 3's Task-1 measurement); `git cat-file -e 4d18b64…` re-asserted and succeeded (Task 1's fetch is what made this a local object); `git branch gsd/v1.31-… 4d18b64…` created the ref only; `git rev-parse gsd/v1.31-…` → `4d18b645…`; `git symbolic-ref --short HEAD` still reads `fix/dev-test-blank-check-after-erase` — **not checked out**, per plan (plan 04 does that) |

**Why the firmware row keeps the decided base (`3085084`) rather than the live tip (`6fab4ea`).**
Phase 138 exists to define "before." A fork base whose own size gate arrives RED would make every
downstream TEST-08 flash/RAM delta measure against an already-broken reference — the delta would be
unattributable between "the pre-existing drift" and "v1.31's own change." D-07 forbids fixing that
drift inside this measurement phase. Keeping `3085084` (measured GREEN at
`check_size_baseline.py`, per `138-RESEARCH.md` and re-confirmed by Section 3's unchanged 2-commit
drift enumeration) preserves a clean reference; the drift itself is carried forward, not discarded,
as **F-138-02** below.

---

## Section 5: F-138-02 — firmware `beta` drift carried forward

**Live tip:** `6fab4eafdcd0981d24fddc3ff177abc5c74e313c` (`6fab4ea`), 2 commits ahead of the decided
fork base `3085084` (Section 3's live enumeration, re-run this session and unchanged from
`138-RESEARCH.md`'s figure — no further firmware-side remote drift since research):

| Commit | Message | Files |
|--------|---------|-------|
| `b1737b2` | `feat(protocol): carry HW revision + FW identity in the MSG_OK_READY ack (#49)` | `src/firestarter.cpp` +37/−1 |
| `6fab4ea` | `Apply automatic changes` | `include/version.h` +1/−1 |

**Flash delta and MERGE-05 headroom — recorded as research-measured, not re-built this plan.** This
plan re-verifies the SHA-level facts above live (the commit list and file list came from this
session's own `gh api repos/henols/firestarter/compare/3085084...6fab4ea` call), but it does **not**
rebuild the live tip's AVR targets — doing so would require a cold PlatformIO toolchain build this
measurement-adjudication task is not scoped to repeat. The following flash/RAM figures are quoted
verbatim from `138-RESEARCH.md` §"Gate outcomes (D-07's question, answered)", with their own
provenance stated there: measured 2026-08-08 (same day, hours before this plan ran), in a **cold,
freshly-extracted tree pulled from `gh api …/tarball/6fab4ea`** — cold by construction, per the
project's own warm-vs-cold measurement discipline.

- **Uniform `flash_used` delta: +34 B on all three AVR targets** (`uno`, `uno328pb`, `leonardo`),
  RAM unchanged, attributable to `b1737b2`'s `MSG_OK_READY` ack payload growth.
- **`check_size_baseline.py` default policy: GREEN (exit 0) at `3085084`, RED (exit 1) at `6fab4ea`.**
- **`--policy merge05` band (BASE-01 comparison): `uno` +56/64 B, `uno328pb` +62/64 B,
  `leonardo` −22/0 B** — uno-class headroom is down to **8 B** (`uno`) and **2 B** (`uno328pb`)
  before the next drift fails this band on arrival.

**Owners, recorded not fixed (D-07):**

| Item | Owner |
|------|-------|
| Flash-delta reconciliation (whether v1.31's own change should absorb, offset, or separately account for this +34 B) | **Phase 144 / TEST-08** |
| MERGE-05 band headroom (2–8 B remaining before the uno-class band fails) | **Phase 143 / 144** |
| Escalation if headroom is exhausted before Phase 144 closes | **henols** |

---

## Section 6: F-138-03 — submodule gitlinks deliberately not advanced

Per **OD-3**, the meta index's submodule gitlinks are **not** advanced by this plan. Read live via
`git ls-files -s firestarter firestarter_app` in `/workspaces`:

| Submodule | Gitlink SHA (meta index) | Worktree SHA (this session, after Task 2) |
|-----------|----------------------------|-----------------------------------------------|
| `firestarter` | `0933bd7d602efb30e4a666e8231ecf724e90ab09` | `30850845f9c0994706f28d2a74fccc3adbb4b387` (now on the new `gsd/v1.31-…` branch, same commit) |
| `firestarter_app` | `cc036e8dc3cd77bbdfc7ec5190d79cdb172153c7` | `7fe8dea9143a6ac4da3d656d3e4d5d538e14a175` (unchanged — still `fix/dev-test-blank-check-after-erase`, not checked out onto v1.31) |

Both gitlink SHAs are **identical before and after this plan's git operations** — nothing in Task 1
or Task 2 ran `git add firestarter` / `git add firestarter_app` in the meta repo, and no submodule
commit was made in either submodule. The resulting `M firestarter` / `M firestarter_app` lines that
`git status` shows in the meta repo are **expected divergence, not dirt to clean up**: the gitlinks
point at older commits than each submodule's current worktree HEAD, exactly as `138-RESEARCH.md`'s
"Working-tree state" section already documented before this plan ran. Per `/workspaces/CLAUDE.md`:
"Neither sub-repo is committed here" — the meta repo's job is to name the three base commits in this
narrative artifact, not to carry them as index gitlinks. **Finding owner: henols** (the decision
of whether/when to advance these gitlinks belongs to a later, explicit git-hygiene action, not to
this measurement phase).

---

## Section 7: Hand-off

**What later plans consume from this one:**

1. **The firmware `gsd/v1.31-27c-programming-algorithm-fidelity` branch, already checked out** at
   `/workspaces/firestarter`, base `30850845f9c0994706f28d2a74fccc3adbb4b387` — Wave 2's firmware
   plans (140, 141, 142) land their commits directly on this checked-out branch; no further branch
   setup is needed there.
2. **The app `gsd/v1.31-27c-programming-algorithm-fidelity` ref**, created but **not** checked out, at
   `/workspaces/firestarter_app`, base `4d18b645ab18a2d2465f0f623062e9249eb24132` — Plan 04 (this
   phase's host-baseline plan) is the one that checks it out.
3. **The three verified base SHAs** (Section 4) — the `.planning/`-level `138-BASELINE.md` this
   phase's later plans produce cites these same three commits as "what was measured before" rather
   than re-deriving them.
4. **PREP-01's corrected criterion** (content equivalence, not ancestry) — any later plan that would
   otherwise re-check `git merge-base --is-ancestor` against the v1.30 branch should cite `F-138-01`
   instead of re-running a check whose false-negative mechanism is now on record.
5. **F-138-02 and F-138-03** — Phase 143/144 (flash-delta reconciliation, MERGE-05 headroom) and any
   future git-hygiene action (gitlink advancement) inherit these as named, owned, unfixed findings.

**What this plan did *not* establish — stated plainly, not implied:**

1. **No push.** `git ls-remote --heads origin 'gsd/v1.31*'` is empty in both submodules; nothing this
   plan did is visible outside these three local checkouts.
2. **No CI run.** No workflow was dispatched, and no CI status for any of the three new branches
   exists yet — that is a later, operator- or plan-triggered action, not part of this adjudication.
3. **No gitlink bump.** The meta index's `firestarter`/`firestarter_app` gitlinks are untouched
   (Section 6) — PREP-02 is satisfied by naming the base commits in this artifact, not by advancing
   the superproject's recorded submodule state.
4. **No re-build of the live firmware tip.** F-138-02's flash/RAM figures at `6fab4ea` are quoted from
   `138-RESEARCH.md`'s prior cold measurement, not reproduced by this plan — this plan re-verified the
   SHA-level drift facts (the commit list, the file list) live, but did not re-run PlatformIO.
5. **No `eprom.cpp` (or any write-path file) edit.** This plan is pure git/GitHub measurement; it
   touched no firmware or host source file.
6. **No merge, no PR, no submodule commit.** Confirmed throughout Sections 1–6: zero commits were
   made inside either submodule, and no `gh pr create`/`gh pr merge`/`git merge` command was ever run.
