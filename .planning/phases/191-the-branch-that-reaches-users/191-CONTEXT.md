# Phase 191: The Branch That Reaches Users - Context

**Gathered:** 2026-09-13
**Status:** Ready for planning

<domain>
## Phase Boundary

The version a person gets from `pip install firestarter` addresses `henols/firestarter_fw`, and that claim
is verified by installing the published artefact rather than by reading the diff. Covers **URL-02,
STABLE-01, STABLE-02**.

The phase depends on Phase 190 only. It is the milestone's one deliberate write to `firestarter_app`'s
protected `main`, and the only phase that opens a pull request against it.

**In scope:** the single firmware-release constant on `origin/main`
(`firestarter_app/firestarter/constants.py:9`); `origin/main`'s `README.md:17` firmware link; the
`firestarter/__init__.py` version bump that the hand-cut release needs; the stable cut and its PyPI
publish; a new re-runnable clean-install fixture under the phase directory; and a live bench leg on the
attached Leonardo.

**Out of scope (settled at activation or in Phases 189/190, not re-litigated here):** claiming
`henols/firestarter` (D-1); mirroring firmware releases onto the meta repository (D-2); the meta
repository's `README.md` and its five `.planning/codebase/` documents (SWEEP-01, Phase 192); anything under
`.planning/milestones/` (D-5); the `.gitmodules` history trap (D-6, Phase 193); the adoption instrument
(GATE-01, Phase 193); `main`'s `beta`-only surface — `submit.py`, `cli_handlers.py`, `fw --list`, the
`--stable`/`--pre` channel split and every URL-04 improvement from Phase 190, none of which exist on `main`
and none of which this phase backports; and repairing `main`'s release pipeline (D-05 below).

**A stated deviation from the ROADMAP, not an accident.** The v1.38 activation text says **"Bench: none. No
phase needs a board."** That no longer holds for Phase 191: the operator directed a real bench leg (D-09).
The phase record must state this plainly rather than let a verifier read it as scope creep.

</domain>

<decisions>
## Implementation Decisions

### URL-02 on a branch that carries one constant, not three

- **D-01:** **Repoint the one constant that exists.** `origin/main` carries only
  `FIRESTARTER_RELEASE_URL` (`firestarter/constants.py:9`); `FIRESTARTER_RELEASES_URL` and
  `FIRESTARTER_RELEASE_BY_TAG_URL` are `beta`-only surface introduced after `main` diverged. URL-02's
  intent — *no code path on `main` depends on GitHub's rename redirect* — is **fully** met by changing that
  one line, because `firmware.py:107` is its only consumer and `main` has no other network call to the
  firmware repository.
  **The two missing names are NOT backported.** Adding module-level constants that no code on `main`
  imports would ship dead surface to every default install and enlarge the diff on a 951-commit-stale
  protected branch.
  **For the traceability agent:** URL-02's text reads "the same three constants". Record it satisfied with
  the explicit reading above — one constant present, one constant repointed, zero code paths on a redirect.
  Do not mark it partial and do not rewrite the requirement.

- **D-02:** **No regression guard is added on `main`, and the resulting gap is stated rather than
  papered over.** `origin/main` has **no `tests/` directory at all**, no `[test]` extra in
  `pyproject.toml`, and no `ci.yml` — a pin test would have nowhere to live and nothing to run it.
  This continues Phase 189's D-10 and Phase 190's D-05: source-scanning gates in this project have a
  history of failing **open** after renames.
  **The gap is real and must be named in `SUMMARY.md`:** Phase 192's sweep operates on the milestone
  branch, so nothing in this milestone watches `origin/main` for regression. D-10 below closes it by
  assignment rather than by tooling.

- **D-03:** **One pull request, three files** — `firestarter/constants.py:9`, `README.md:17`, and
  `firestarter/__init__.py` (`__version__` `2.0.8` → `2.0.9`, per D-04).
  The first two are the **complete** boundary-aware sweep of `origin/main`: `git grep -nE
  "henols/firestarter([^_a-zA-Z0-9]|$)" origin/main` returns exactly those two lines and nothing else.
  `README.md` sits inside `release.yml`'s `paths-ignore`, so folding it in changes nothing about whether
  the cut fires — `constants.py` already triggers it regardless.
  — **Reversibility:** costly — undoing a merge to a protected default branch requires a second pull
  request through the same protection, and the published 2.0.9 sdist is immutable on PyPI once uploaded.

### The stable cut — an automatic pipeline that will not complete

- **D-04:** **Predict the `release.yml` failure, let it happen, and hand-cut the release.**
  **Measured mechanism:** merging the PR fires `release.yml` (`on: push: branches: [main]`;
  `paths-ignore` covers `**.md`, `**.sh`, `.gitignore`, `docs/**`, `images/**`, `.github/**`, `.vscode/**`,
  `tools/**` — **not** `firestarter/**`). Its `update_version.py` step bumps the patch version, and
  `stefanzweifel/git-auto-commit-action@v5` then **pushes directly to `main`** using the default
  `GITHUB_TOKEN` (its `PERSONAL_ACCESS_TOKEN` env is commented out). The `Protect main` ruleset
  (id `22046179`, created **2026-09-01**, scope `~DEFAULT_BRANCH`) enforces `pull_request`, and its only
  bypass actor is `DeployKey`. `current_user_can_bypass` is `never`, so no PAT of the operator's helps
  either. GitHub's own documentation and community guidance are explicit that `GITHUB_TOKEN` cannot bypass
  a `pull_request` rule even when actors are listed.
  **Therefore the push is rejected, the step fails, the job aborts, and the `Release` step never runs — no
  tag, no GitHub release, nothing on PyPI.**
  **This has never been exercised under protection:** `release.yml`'s last run was `2026-08-07` on
  `e4112ef`, which **predates the ruleset by 25 days**.
  **What the phase does:** carry `__version__ = "2.0.9"` in the PR so the merged commit is already correct,
  then have the operator create tag + GitHub release `2.0.9` on the merged SHA by hand. File the collision
  as a backlog item. No ruleset change, no redesign of the stable release flow inside a rename milestone.

- **D-05:** **PyPI is reached by a manual `workflow_dispatch`, and both pipeline defects are filed, not
  fixed.**
  **Measured:** `publish.yml` has run **8 times in this repository's entire history, every one
  `event=workflow_dispatch`. Zero `release` events, ever.** Its `release: published` trigger has literally
  never fired. The consequence is already visible on disk: GitHub release **`2.0.8` exists (2026-08-07)**
  while **PyPI's latest stable is `2.0.7`** — 2.0.8 was cut and never published, and nothing reported an
  error.
  **The known-good fix already exists in this repository and is NOT ported here:** `beta-release.yml` on
  `beta` carries a `pypi` job (`uses: ./.github/workflows/publish.yml`, `with: tag:`, `secrets: inherit`)
  added precisely because "the `release.published` event does NOT reach publish.yml… the failure was silent
  — GitHub reached b17 while PyPI stopped at b15". It also passes `target_commitish` so the tag lands on
  the bumped commit. `main`'s `release.yml` has **neither**.
  **Why not port it here:** it would be inert. D-04 declined to fix the push blocker, so the job that would
  call `publish.yml` still never runs. Half a fix that cannot execute is worse evidence than a filed defect.
  **Backlog items to file (two, separately):** the `release.yml` auto-commit vs. ruleset collision, and the
  never-firing `release.published` trigger — each naming `beta-release.yml` as the proven pattern.

- **D-06:** **Two operator gates, with agent observation between them — the branch point is decided by
  reading the run, not by assuming D-04 was right.**
  - **Gate 1 (`blocking-human`):** operator pushes the prepared branch, opens the PR, merges it.
  - **Agent, between gates:** reads the `release.yml` run conclusion **live** via `gh run list`, and
    branches on what it actually sees:
    - *failed as predicted* → hand the operator the exact tag + release + `workflow_dispatch` commands for
      the merged SHA;
    - *unexpectedly succeeded* → read back **which version the bot actually cut**. It would be **`2.0.10`**,
      not 2.0.9, because `update_version.py` bumps on top of the `2.0.9` the PR carries. Skip the hand-cut
      and record the real version.
  - **Gate 2 (`blocking-human`):** operator performs the cut and the `publish.yml` dispatch.
  - **Agent, after:** verifies PyPI independently.
  **Precedent this follows (189-04, binding):** the agent prepares the branch in a **scratch worktree off
  `origin/main`** and **never** pushes, opens, or merges; verification is re-run against the **live GitHub
  API** (contents API at `ref=main`), never against the operator's report and never against the local
  clone; and a **positive control** accompanies every zero-count so an absence is proved rather than
  assumed.

### STABLE-02's instrument

- **D-07:** **A new, board-free, re-runnable `191-stable-install-fixture.sh` under the phase directory**,
  mirroring Phase 189's D-06 and Phase 190's D-16. Phase 190's `endpoint-contract-fixture.sh` **cannot** be
  re-run against the stable despite D-16 saying so: it imports `fetch_release_info(channel=…)`,
  `FIRESTARTER_RELEASES_URL`, `click`, `cli_handlers.cli`, `fw --list` and `fw --stable`, **none of which
  exist in `main`'s argparse-based 2.0.x code**. That expectation in 190's D-16 is hereby corrected, not
  inherited.
  **It MUST assert `redirects == 0`, and that is the substance of this decision.** Measured live
  2026-09-13: `api.github.com/repos/henols/firestarter/releases/latest` and
  `…/henols/firestarter_fw/releases/latest` return **byte-identical bodies** (`sha256` prefix
  `219633ebe41126a6`, both `tag_name` `2.0.6`); the only difference is `len(r.history)` — **1 versus 0**.
  The bare slug's 301 `Location` is `api.github.com/repositories/810276812/releases/latest`, the same
  numeric id Phase 189's D-12 anchored on. **A stale 2.0.7 install would pass any resolve-based check
  identically**, so a green resolve proves nothing on its own.
  **Chain covered:** install → assert resolved version → read `constants.py` out of the **installed**
  package → drive 2.0.x's own `fetch_latest_release_info` → `_download_firmware_file` → assert
  `redirects == 0`.

- **D-08:** **Plain `python3 -m venv` on the devcontainer default interpreter, in a `mktemp` directory
  outside the app working tree**; `pip install firestarter` with **no `--pre` and no local path**.
  **Phase 190's D-17 `uv venv --python 3.11` pin does not carry over** — it existed to match Host CI's
  py3.11, and `origin/main` has **no `ci.yml`** and declares `requires-python = ">=3.9"`. Pinning 3.11 here
  would assert a constraint that does not exist and would be less representative of a real user install.
  **Two traps this project has already hit, both of which the fixture must defend against:**
  - **an editable install in a sibling tree can shadow the PyPI package** — the fixture prints
    `firestarter.__file__` and the resolved version **first**, so the transcript proves which artefact was
    exercised;
  - **the app writes `~/.firestarter/` regardless of `FIRESTARTER_CONFIG_DIR`** — the downloaded `.hex` is
    removed **by explicit path**, never with `git clean -Xdf`.

- **D-09:** **A real bench leg is performed — operator-directed, overriding the board-free
  recommendation.** The attached board is a **Leonardo on `/dev/ttyACM0`, currently at firmware
  `3.0.0b22`**; stable `2.0.6` does ship `firestarter_leonardo.hex`, so the path is live.
  Run `fw --install` from the **clean stable install**, answer **`y`**, flash `2.0.6`, and **leave the board
  on 2.0.6**.
  **No no-flash guard, no per-flash confirmation, no question asked at flash time — it is a test board.**
  This is a standing operator instruction; a plan must not reintroduce a gate here.
  **What the operator will see, measured in advance:** `_compare_versions("3.0.0b22", "2.0.6")` evaluates
  `int("0b22")`, raises `ValueError`, logs *"Could not parse version strings for comparison"*, and returns
  `False`. The CLI therefore prompts *"New firmware 2.0.6 available for leonardo (current: 3.0.0b22). Update
  now?"* — i.e. it offers a **downgrade**. That is the correct, faithful end-to-end demonstration and is not
  a defect to fix here.
  **The fixture stays board-free.** A one-shot hardware flash is transcript evidence, not fixture content
  (189 D-06 / 190 D-16) — Phase 193 and any post-claim milestone must be able to re-run D-07's script
  without a board.
  — **Reversibility:** reversible — the board is re-flashable at any time with the `beta` CLI.

### Phase 191 / Phase 192 boundary

- **D-10:** **Phase 191 owns `origin/main`'s slug references outright; Phase 192 re-verifies `origin/main`
  as a ref and does not edit it.** This is exactly the Phase 189 D-09 / Phase 190 D-04 pattern — the phase
  already committing to a branch owns that branch's references, and the later sweep confirms it
  already-clean.
  **Why it matters beyond tidiness:** SWEEP-01 names "both sub-repo READMEs" but Phase 192 sweeps the
  **milestone branch**, where `origin/main`'s README is invisible. Without D-10 the line falls through both
  phases. Re-verifying `origin/main` as a **git ref** needs no test infrastructure and no second pull
  request to a protected branch — and it is also what partially closes D-02's stated gap.

### Claude's Discretion

- The fixture's name, argument handling, temp-directory strategy and transcript capture, so long as the
  chain in D-07 is covered, `redirects == 0` is asserted, `firestarter.__file__` is printed, and it is
  genuinely re-runnable.
- How the bench transcript is captured and where under the phase directory it lands.
- The wording of `README.md:17`'s repointed link beyond changing the slug.
- Commit granularity across the prepared `main` branch, the fixture, the evidence and the backlog items.
- The exact wording of the two backlog items, so long as each names `beta-release.yml` as the proven
  pattern.
- Whether the `_compare_versions` beta-string finding (D-09) becomes its own backlog item or a
  `SUMMARY.md` observation.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope and the decisions that bound this phase
- `.planning/REQUIREMENTS.md` — URL-02, STABLE-01, STABLE-02 verbatim; the D-1…D-7 activation decisions;
  the Out of Scope table. **D-1…D-7 are settled; no plan re-opens them.**
- `.planning/ROADMAP.md` § "Phase 191: The Branch That Reaches Users" (≈ lines 350–375) — the goal, the
  four success criteria, and the outward-facing note that this phase must not run under `--auto`/`--chain`.
  § v1.38 milestone header (≈ lines 172–270) — the branch model, the **948-commit** staleness finding that
  is the sole reason the STABLE strand exists, and the **"Bench: none"** statement that D-09 deviates from.
- `.planning/PROJECT.md` § "Current Milestone: v1.38 Repository Rename" — the five strands and the full
  D-1…D-7 rationale.

### The two prior phases — their decisions are inherited, not re-derived
- `.planning/phases/189-free-the-name/189-CONTEXT.md` — **D-07** (a protected-branch change lands as its
  own pull request inside the phase) is the direct parent of D-03; **D-09** (the phase committing to a
  branch owns its slug references) is the parent of D-10; **D-10** (no regression guard) is the parent of
  D-02; **D-06** (a re-runnable script under the phase directory) is the parent of D-07; **D-11** (plans
  halt at the operator act and resume after) is the parent of D-06.
- `.planning/phases/189-free-the-name/189-04-SUMMARY.md` — **the binding procedural precedent for D-06.**
  Read it before writing any plan that touches `main`: scratch worktree off `origin/main`, agent never
  pushes/opens/merges, verification re-run against the live GitHub API rather than the operator's report or
  the local clone, and a positive control proving a zero is a real absence.
- `.planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/190-CONTEXT.md` — **D-16** claims Phase
  191 re-runs 190's fixture; **D-07 above corrects that** — the fixture imports surface `main` does not
  have. D-02's note that `henols/firestarter` is a **substring** of `henols/firestarter_fw` is why D-03's
  sweep uses a boundary-aware pattern.
- `.planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/endpoint-contract-fixture.sh` — the
  shape to mirror for D-07, and the origin of the `redirects: 0` assertion. Its header comment carries
  RESEARCH Finding 1, which D-07 re-measured and confirmed.
- `.planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/190-RESEARCH.md` — Finding 1 (the
  transparent 301) and Pitfall 7 (constants are imported by name at module scope, so rebinding
  `firestarter.constants` has no effect).

### The rename's measured impact
- `.planning/notes/999.9-repo-rename-impact-analysis.md` — the whole note. Line 83 is the origin of this
  phase: 999.9's own validation plan resolves to 2.0.7 and therefore exercises `main`, so repointing `beta`
  alone "would pass while leaving the default install broken". Note that 999.9's chain includes **flash**,
  which the ROADMAP and STABLE-02 dropped — D-09 restores it.

### The deferred destructive half — this phase must not advance it
- `.planning/seeds/SEED-claim-firestarter-slug.md` — the dormant seed. Phase 193 turns its trigger into a
  number, and **that instrument has nothing to measure until this phase publishes a stable** (the ROADMAP's
  one stated cross-phase dependency beyond 189).

### The pipeline this phase observes but does not repair
- `firestarter_app/.github/workflows/release.yml` (on `origin/main`) — the `paths-ignore` list, the
  `update_version.py` bump and the `git-auto-commit-action` push that D-04 predicts will be rejected.
- `firestarter_app/.github/workflows/publish.yml` (on `origin/main`) — the `workflow_dispatch` input D-05
  uses, and the comment block that already documents the suppressed `release.published` event.
- `firestarter_app/.github/workflows/beta-release.yml` (on `origin/beta`) — **the known-good fix pattern
  both backlog items must name:** the `pypi` job calling `publish.yml` directly with `secrets: inherit`,
  and `target_commitish` on the release. Read for reference only; **not** edited or ported by this phase.

### Standing repository rules — binding on every plan in this phase
- `CLAUDE.md` § "Source code comments — hard rule" — **no comments in product source, not overridable by a
  plan, a task, a skill, or a subagent instruction.** This phase edits `constants.py` and `__init__.py` on
  `main`; rationale goes in `SUMMARY.md` or the commit message, never in source.
- `CLAUDE.md` § "Milestone close and branch protection" — `main` is protected in all three repositories;
  this project's close targets `beta`, not `main`.
- `.planning/notes/v135-close-procedure-under-protection.md` — how changes land on protected branches.

</canonical_refs>

<code_context>
## Existing Code Insights

### Measured facts — do not re-measure, cite these

Captured 2026-09-13 against the live GitHub API, the live PyPI API, and `origin/main`.

**`origin/main` carries ONE firmware-release constant, not three:**

| file:line | content |
|---|---|
| `firestarter/constants.py:9` | `"https://api.github.com/repos/henols/firestarter/releases/latest"` |
| `firestarter/firmware.py:107` | `requests.get(FIRESTARTER_RELEASE_URL, timeout=10)` — the only consumer |

**The complete boundary-aware sweep of `origin/main`** —
`git grep -nE "henols/firestarter([^_a-zA-Z0-9]|$)" origin/main` returns exactly two lines:
`README.md:17` and `firestarter/constants.py:9`. Everything else on the branch is `firestarter_app` or
`firestarter_prom`.

**`origin/main` is a different codebase from `beta`:** argparse (not click), `__version__ = "2.0.8"`,
`requires-python = ">=3.9"`, **no `tests/` directory**, no `[test]` extra, **no `ci.yml`**. Its `fw`
supports `--install`, `--board {uno,leonardo}`, `--port`, `--force`, `--avrdude-path`,
`--avrdude-config-path`. There is **no `--list`, no `--json`, no `--stable`/`--pre`**. Last commit
`1625aef` (2026-09-02); **951 commits behind `beta`**.

**The branch protection, read live:** ruleset `22046179` "Protect main", `enforcement: active`, scope
`~DEFAULT_BRANCH` (and `firestarter_app`'s default branch **is** `main`). Rules: `deletion`,
`non_fast_forward`, `pull_request` (`required_approving_review_count: 0`,
`require_extra_approval_for_unattributed_changes: true`). **Bypass actors: `DeployKey` only.**
`current_user_can_bypass: never`. **Created 2026-09-01.**

**Release / publish history, read live:**

| workflow | runs | detail |
|---|---|---|
| `release.yml` | 2 | both `success`; last `2026-08-07` on `e4112ef` — **25 days before the ruleset** |
| `publish.yml` | 8 | **all 8 `event=workflow_dispatch`; zero `release` events ever** |

**The resulting inconsistency, on disk today:** GitHub stable releases run `2.0.8` (2026-08-07), `2.0.7`,
`2.0.6`…; PyPI `info.version` is **`2.0.7`**, and `2.0.8` is **absent** from PyPI entirely. Tag `2.0.8`
points at `584bcdb` ("Apply automatic changes" — the auto-commit).

**The transparent-redirect measurement (D-07's premise):**

| URL | status | `len(r.history)` | `tag_name` | body `sha256` |
|---|---|---|---|---|
| `…/repos/henols/firestarter/releases/latest` | 200 | **1** (`[301]`) | `2.0.6` | `219633ebe41126a6` |
| `…/repos/henols/firestarter_fw/releases/latest` | 200 | **0** | `2.0.6` | `219633ebe41126a6` |

Bodies are **byte-identical**. No-follow reading of the bare slug: `301 → https://api.github.com/repositories/810276812/releases/latest`.

**Firmware release state on `henols/firestarter_fw`:** stable `/releases/latest` → `2.0.6`, assets
`firestarter_leonardo.hex` and `firestarter_uno.hex` — exactly the two boards `main`'s `fw` offers, so the
board/asset match is total and no asset-less case exists on this path.

**The bench board:** Leonardo on `/dev/ttyACM0`, firmware `3.0.0b22`. `_compare_versions("3.0.0b22",
"2.0.6")` raises `ValueError` on `int("0b22")`, is caught, logs a warning, returns `False` → the stable CLI
offers a downgrade to `2.0.6`.

**The meta repository has 0 GitHub releases** — D-4's standing rule holds today.

### Established patterns this phase inherits

- **A protected branch is reached only through a prepared local branch built in a scratch worktree off
  `origin/main`, plus an operator-performed push/PR/merge behind a `blocking-human` gate.** The agent never
  pushes, opens, or merges (189-04).
- **Verification is re-run against the live API, never copied from the operator's report or the local
  clone**, and a positive control accompanies every zero-count (189-04).
- **Evidence lives under the phase directory and is re-runnable where it reasonably can be** (189 D-06,
  190 D-16).
- **Executors commit inside the submodule** on the milestone branch; the meta repository re-pins the
  gitlink, advanced **per phase** since v1.36.
- **Pushes happen at ship time, never ad hoc.** This phase is the deliberate exception the ROADMAP's branch
  model names — and every push here is operator-performed under D-7.

### Integration points

- `firestarter_app/firestarter/constants.py:9` on `origin/main` — URL-02 (D-01).
- `firestarter_app/README.md:17` on `origin/main` — the firmware link (D-03, D-10).
- `firestarter_app/firestarter/__init__.py` on `origin/main` — `__version__` `2.0.8` → `2.0.9` (D-04).
- GitHub: the pull request, the hand-cut tag + release, and the `publish.yml` `workflow_dispatch` (D-04,
  D-05, D-06) — all operator-performed.
- The phase directory — D-07's fixture, its transcript, and D-09's bench transcript.
- `.planning/todos/` — the two backlog items from D-05.

### Explicitly NOT integration points for this phase

- The milestone branch's `constants.py` — already repointed by Phase 190 (URL-01).
- Any `.github/workflows/` file in any repository — D-05 files defects rather than fixing them;
  `beta-release.yml` is **read** for the pattern, never edited or ported.
- `firestarter_app/firestarter/submit.py` — does not exist on `origin/main`.
- The meta repository's `README.md` and its five `.planning/codebase/` documents — SWEEP-01, Phase 192.
- Anything under `.planning/milestones/` — D-5; Phase 192 must prove a diff over that path is empty.
- The firmware repository — renamed and repointed in Phase 189; untouched here.

### One housekeeping hazard a planner must know about

`.planning/config.json` **does** carry submodule routing — at `planning.sub_repos`, not at the top level —
listing `firestarter`, `firestarter_app`, `firestarter_app_py32`, `firestarter_py32_ci`.

**The hazard is that GSD verbs silently prune it.** Writing this context did exactly that: a
`state.record-session` / `commit` run dropped `firestarter_app_py32` and `firestarter_py32_ci`, leaving two
entries. It was restored by hand. Two consequences for this phase, which commits inside `firestarter_app`:

- **Check `git status -- .planning/config.json` after any `gsd-tools query` call that writes state**, and
  restore the block rather than committing the prune.
- `config.json` is a VERIFICATION-covered file, so an unnoticed prune reads as `stale` and blocks the phase
  transition.

The same run also under-wrote `STATE.md`'s `progress.completed_phases` (2 → 0) and `progress.percent`
(40 → 0); both were repaired by hand in commit `b019c706`. Expect to repair both files again.

</code_context>

<specifics>
## Specific Ideas

- **`redirects == 0` is the whole point of the fixture.** The two endpoints return byte-identical bodies;
  an exit code, a version string and an asset URL are all compatible with the pre-change state. Any
  transcript that shows only a successful resolve is worthless as evidence for this phase.
- **The fixture must print `firestarter.__file__` before anything else.** A fixture that silently exercised
  a shadowing editable install would produce a perfect, meaningless transcript — and this project has hit
  that trap before.
- **The failed `release.yml` run is evidence, not an incident.** D-04 records the prediction *before* the
  merge specifically so the run's failure reads as a confirmed measurement. The run URL and conclusion
  belong in the phase record.
- **Criterion 4's "what this does NOT achieve" must name three things, not one:** users who never upgrade
  remain unreachable and the eventual claim will break `fw` for them; `origin/main` is left with no
  regression guard (D-02); and `main`'s stable release pipeline is left broken in two places (D-05), so the
  *next* stable cut will need the same manual handling.

</specifics>

<deferred>
## Deferred Ideas

- **`release.yml`'s auto-commit cannot push to a protected `main`.** `GITHUB_TOKEN` cannot bypass a
  `pull_request` ruleset, and the only bypass actor is `DeployKey`. Filed as backlog under D-05. The fix is
  a credential/settings change or a redesign that stops the workflow pushing at all — both outside a rename
  milestone.
- **`publish.yml`'s `release: published` trigger has never fired (0 of 8 runs).** Filed as backlog under
  D-05. `beta-release.yml`'s `pypi` job (`uses: ./.github/workflows/publish.yml`, `secrets: inherit`) is
  the proven fix, along with `target_commitish` on the release step.
- **`main`'s `_compare_versions` cannot parse a `3.0.0bNN` firmware string** — `int("0b22")` raises
  `ValueError`, so a stable CLI reports every beta-flashed board as out of date and offers a downgrade.
  Measured, not theorised (D-09). Whether this is filed or merely noted is Claude's discretion; it is a
  `main`-branch defect and `beta` already uses PEP 440 comparison.
- **GitHub release `2.0.8` is orphaned** — cut 2026-08-07, never published to PyPI. Nothing in this phase
  cleans it up or back-publishes it; `2.0.9` supersedes it for `pip install` purposes.
- **Porting Phase 190's URL-04 improvements to `main`** (the dead-endpoint error, the `--list` failure/empty
  split, the `--json` contract). Out of scope — `main` has no `--list` and no `cli_handlers.py`, and URL-02
  names constants only.
- **A `tests/` directory and `ci.yml` on `main`.** Declined under D-02. If `main` ever becomes a
  development branch again rather than a release branch, revisit.
- **Resolving the PyPI/GitHub name incoherence** — after the eventual claim, PyPI `firestarter` is the app
  while GitHub `firestarter` is the meta repository. Already in the milestone's Out of Scope table.
- **A standing guard against GSD verbs pruning `planning.sub_repos` from `.planning/config.json`.** Repo-hygiene, not this phase's scope — but see the hazard note in `<code_context>`; it fired during this discussion.

### Reviewed Todos (not folded)

`todo.match-phase 191` returned **35** pending todos with 34 scoring matches. **All are keyword noise** —
the top entries score 0.6 on the bare word `firestarter` plus generic terms (`test`, `firmware`, `phase`),
and none touches a repository slug, a release endpoint, a branch, or PyPI. Representative:

- *Skip VPP error/warning checks when VPP is unused* — firmware behaviour; v1.38 changes no firmware source.
- *Drive outputs/pins to a safe state on power-up and on ANY fault* — firmware behaviour; same reason.
- *Strip residual GSD provenance comments from product source* — host app, but a repo-wide hygiene sweep;
  this phase edits two lines on a branch that carries no such comments.
- *Reclaim ~172M of local scratch from the meta-repo working tree* — unrelated housekeeping.

None folded.

</deferred>

---

*Phase: 191-The Branch That Reaches Users*
*Context gathered: 2026-09-13*
