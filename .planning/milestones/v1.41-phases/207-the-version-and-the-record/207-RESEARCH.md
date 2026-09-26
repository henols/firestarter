# Phase 207: The version and the record - Research

**Researched:** 2026-09-23
**Domain:** Release mechanics across two publishing sub-repos (`firestarter_app` → PyPI, `firestarter_fw` → GitHub pre-release), plus user documentation in the GitHub wiki. **Dual-repo commit pair, plus one wiki push. No product-behaviour change. No new dependency.**
**Confidence:** HIGH on the version and CI mechanics. The real bump scripts ran against a `3.1.0b1` source string in scratch copies, and the merge with `beta` was simulated with `git merge-tree`. HIGH on the compatibility facts: they come from the bench transcripts of Phases 204 and 205 and from the published `3.0.0b50` / `3.0.0b35` source. MEDIUM on the wiki information architecture: that is a documentation judgement with no tool to settle it.

<user_constraints>
## User Constraints

**There is no `207-CONTEXT.md`.** The operator chose to plan without `/gsd-discuss-phase`, as for Phase 206. **This phase has no locked decisions.** This document names each fork (F1–F10 in § Open Design Forks), gives a recommendation with its evidence, and does not assume that the recommendation was taken.

### Locked Decisions
None for this phase.

**Inherited and still binding.** These are milestone-level decisions from `.planning/PROJECT.md` § "Decisions taken at activation", read this session:
- **D-4 — Clean break on the protocol.** "Ordinals 4 and 6 are retired outright, not deprecated. The host direction is safe without a version gate … Old host against new firmware is refused by the existing fail-closed dispatch." `[VERIFIED: .planning/PROJECT.md:92-95]` → **The phase adds no host firmware-version gate.**
- **D-5 — `3.1.0b1` in both repos.** "A minor bump, beta series, stable line untouched." `[VERIFIED: .planning/PROJECT.md:96-98]`
- **Meta CLAUDE.md (binding, same authority as a locked decision):** "The meta repository must never publish a GitHub Release — bare milestone tags only." "A push to `beta` in either sub-repo PUBLISHES." "Never commit to `beta` directly."

### Claude's Discretion
Everything else. See § Open Design Forks.

### Obligations carried forward to this phase
Earlier phases filed these explicitly against Phase 207 / REL-04. Each is verified in the record named.
1. **Name the version boundary for a human.** The pre-`3.1.0` refusal text is `Unknown command: 6` / `Unknown command: 4`. Phase 204's D-05 accepted that cost on condition that "Phase 207 owns naming the boundary for a human in the wiki, and the verbatim text above is what it has to work from." `[VERIFIED: 204-BENCH-MATRIX.md:392-397]`
2. **"A `3.1.0` CLI wants `3.1.0` firmware for `write -b`"**, documented beside the retirement of ordinals 4 and 6. `[VERIFIED: 205-CONTEXT.md:120-121]`
3. **The `erase -b` 0/1/2 exit contract (205 D-02) and the `-s`/`-b` refusal (205 OQ-1).** Both are one-way published CLI-contract changes. `[VERIFIED: 205-01-SUMMARY.md:222]`
4. **Decide whether a dedicated retired-command message deserves a catalog id.** 205 wrote: "Best home: Phase 207, which owns REL-04's wiki breaking-change page and will decide whether the wording deserves a catalog id." `[VERIFIED: 205-CONTEXT.md:541-544]` → Fork **F9**.
5. **The `write --verify` exit contract** is "a published CLI surface that Phase 207's REL-04 will document in the wiki". `[VERIFIED: 203-03-PLAN.md:59]`

### Deferred Ideas (OUT OF SCOPE)
- **A host pre-flash firmware-version guard.** Filed as `.planning/todos/pending/2026-09-20-preflight-firmware-version-compat-guard.md`. Excluded by D-4. Note for the record: after this bump the boundary *becomes visible* to the host. `_probe_port`'s `[\d.x]+` truncates `3.1.0b1` to `3.1.0` and `3.0.0b35` to `3.0.0`, so a numeric minor gate would now be precise. That is the "option (b)" of memory `reference_host_cannot_see_firmware_prerelease_suffix`. Do not build it here.
- **Retiring the orphaned catalog ids** (`DBG_VERIFY_PROM`, `DBG_BLANK_CHECK_PROM`, `DBG_FLAG_SKIP_BLANK`, eventually `MSG_ERR_NOT_BLANK`). Deferred by 205 to "any later phase already paying for a codegen run". This phase pays for none. `[VERIFIED: 205-CONTEXT.md:550-554]`
- **`/gsd-secure-phase 206`.** Outstanding, but it is not this phase's work. `[VERIFIED: STATE.md:242]`
- **Merging or publishing.** The beta cut is the ship step and is operator-gated. The milestone tag is created at milestone close, not in this phase.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REL-01 | Both repositories carry `3.1.0b1`, and the two version strings are bumped in the same commit pair. | § Q1: exactly two source strings, and nothing else pins them. The scratch probe shows the bump publishes as `3.1.0b1` on the first beta push. § Q2: commit-pair precedent; the **merge conflict with `beta` that the bump creates** (Fork F1). § Verification Commands V1–V5. |
| REL-04 | The breaking change and the `write --verify` / `--full` surfaces are documented in the wiki, which is the only documentation home. | § Q3: the full compatibility matrix in both directions, with verbatim refusal text. § Q4: wiki inventory, the text that becomes wrong, the unpushed commit already in the clone, push precedent. § Q5: exact current semantics. § Wiki Content Specification. Forks F3–F8. |
| (criterion 4) | No GitHub Release from the meta repo; bare tag. | § Q6: the meta repo has 0 Releases and no workflows. The tag is created at close by `complete-milestone/steps/git-tag.md`, which runs `git tag -a` and never `gh release`. Command V9 proves the negative. |
</phase_requirements>

## Summary

The mechanical half is smaller than it looks, but it hides a trap. Exactly two strings move. `firestarter_app/firestarter/__init__.py:1` reads `__version__ = "3.0.0b48"`. `firestarter_fw/include/version.h:11` reads `#define VERSION "3.0.0b33"`. `pyproject.toml` takes its version dynamically from `firestarter.__version__`. No test, snapshot or native suite pins either string. The whole app suite (2362 passed) and the whole firmware `tests/` tree (284 passed, 32 meta-skips) were re-run with the bump applied, and nothing moved.

CI does not publish the source string verbatim. On a `beta` push, `update_version.py` reads only the `major.minor.patch` *base* from the source, then scans git tags for `<base>b*` and emits `b(N+1)`, or `b1` when none exists. Running the real scripts against a `3.1.0b1` source gives `DRY_RUN: 3.1.0b1` in both repos. Neither repo has any `3.1.0*` tag, and PyPI has no `3.1.x`, so the first beta push publishes `3.1.0b1` in both repos. That restores byte-identical lockstep, which today's `3.0.0b50` / `3.0.0b35` split lacks.

**The trap: `beta` has moved.** v1.40 was merged to `beta` in all three repos on 2026-09-20. `STATE.md` still says it is unmerged, which is stale. Each sub-repo's `beta` then took two bot bumps: app `3.0.0b48→b50`, firmware `b33→b35`. The v1.41 branches fork from the pre-bump v1.40 tip. Without the bump they merge into `beta` cleanly. **With the bump, both merges conflict on exactly the version line** (simulated with `git merge-tree`). A careless resolution that keeps `beta`'s side publishes `3.0.0b51` / `3.0.0b36`. That silently loses the whole point of the milestone and burns a PyPI version that can never be reused. Fork F1 recommends merging `origin/beta` into each sub-repo milestone branch *before* the bump, so the bump lands conflict-free.

The documentation half has more substance than the roadmap suggests. The wiki today has **no command reference at all**. `write`, `verify`, `blank` and `-b` are documented nowhere a user can find them, except in `--help`. The `Breaking-Changes` page opens with a page-wide claim, "a new CLI cannot drive old firmware, and old firmware cannot be driven by a new CLI … fails with a timeout or a decode error". That claim becomes false for this release: a new host drives old firmware for `verify` and `blank`, and an old host fails with `Unknown command: 6`, not a timeout. Research also found **three compatibility consequences that no earlier phase recorded**:
1. A pre-`3.1.0` host (`3.0.0b50` has no host write guard) writing to a non-blank UV part on `3.1.0b1` firmware (which has no write-init check) is refused by **nothing**.
2. The same old host's `erase -b` silently stops checking.
3. The same old host's bare `fw` auto-routes to `--pre` and will *recommend* installing `3.1.0b1`.

The wiki must say "upgrade the CLI first".

**Primary recommendation:** plan three waves.
1. **Wave 0.** Rebuild the broken `.venv311`; its interpreter vanished in today's container rebuild. Merge `origin/beta` into both sub-repo milestone branches.
2. **Plan 01 (autonomous).** The bump pair: firmware, then app, then the meta gitlink advance. Gate it on `DRY_RUN: 3.1.0b1` from both repos' real bump scripts.
3. **Plan 02 (non-autonomous).** Author the wiki changes, then a human-action checkpoint before a push that publishes instantly, then a post-push check from a fresh clone.

The phase creates no tag and no Release, and proves the negative with one `gh api` call.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Host version string | `firestarter_app` source (`__init__.py`) | PyPI (published by `beta-release.yml` → `publish.yml`) | `pyproject.toml` reads it via `attr`. CI rewrites it on `beta` from base plus tag scan. |
| Firmware version string | `firestarter_fw` source (`include/version.h`) | GitHub pre-release assets (`beta-build.yml`) | Compiled into `FW_VERSION` (`firestarter.h:44`) and reported in the `MSG_OK_READY` ack and the `FW:` line. |
| Version agreement between the two | Commit pair on the milestone branches | Meta gitlink commit | No mechanical cross-check exists. The pair is a process property, proven by the dry-run commands. |
| User-facing compatibility record | GitHub wiki (`henols/firestarter.wiki.git`) | `--help` text (Click docstrings, snapshot-pinned) | REL-04: "the wiki, which is the only documentation home". |
| "No meta Release" invariant | GitHub repo state of `henols/firestarter` | Milestone-close workflow (`git tag -a` only) | Nothing in this phase can create a Release. The proof is an API count. |

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md`:
- Milestone work forks off `beta` on `v1.X-slug` branches in all three repos. **Never commit to `beta` or `main`.**
- **A push to `beta` in either sub-repo publishes**, with no path filter. A PyPI version can never be reused. Decide the scope before the push.
- **The meta repository must never publish a GitHub Release — bare milestone tags only.**
- Serial-protocol and constants changes stay in sync between the two sub-repos. That is not triggered here: no protocol or constant changes.
- Messages are generated only in the meta repo (`tools/catalog/messages.toml`). Never hand-edit `messages.h` / `messages.py`. This is relevant to Fork F9.
- Before `/gsd-ship`, recreate local `beta` from `origin/beta`. This bears on F1: local `origin/beta` refs were stale this session.
- Comments in product source are allowed again (the 2026-09-19 removal). Nothing here needs one.

From `firestarter_app/CLAUDE.md`:
- **CI runs Python 3.11.** Run the suite on 3.11 before you trust it. CI runs `ruff check`, `ruff format --check`, `pytest --cov-fail-under=70`, and a `pip install -e .` + `firestarter --help` smoke test.
- `beta-release.yml` has no path filter. A docs-only push publishes.

From `firestarter_fw/CLAUDE.md`:
- `build.yml` runs on push to any branch except `beta`, and on PRs. It runs `pio test -e native` on PRs only, and always runs `pio test -e native_nodevtools`, `pytest tests/ -v` and `pio run`.
- `beta-build.yml` bumps the version, builds, and cuts a pre-release. It has no path filter, "because the version compiles into the binary".
- **`include/messages.h` is generated.** Do not edit it by hand.

From memory `feedback_no_gsd_references_in_validated_eproms_notes`: "Treat it as extending to any user-facing artifact this project publishes." → **The wiki text must carry no phase numbers, `D-NN` ids, `.planning/` paths or milestone citations.**

## Standard Stack

### Core (already present — use these, do not add)
| Tool | Version (measured) | Purpose |
|------|-------------------|---------|
| `.github/scripts/update_version.py` (both repos) | in-tree | The publisher's own version derivation. Use its `--dry-run` as the REL-01 oracle. |
| `git merge-tree --write-tree` | git in devcontainer | Proves a branch merges into `beta` cleanly, without touching the working tree. |
| `gh` | 2.101.0 | Release and tag counts for criterion 4. Needs `XDG_CACHE_HOME` redirected (memory `reference_gh_run_log_needs_xdg_cache_home`). |
| `uv` | 0.12.15 | Rebuilds `.venv311`. Needs `UV_CACHE_DIR` redirected, because `~/.cache` is root-owned. |
| PlatformIO | 6.2.0 | Only if the planner wants `pio run` proof that the string lands in an image (optional; see V6). |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Source bump plus auto tag-scan | `workflow_dispatch` with `beta_version=3.1.0b1` | Leaves the source at `3.0.0b*`, which fails criterion 1. Keep it only as the drift-recovery escape hatch (`v1.4-RELEASE-PROCEDURES.md` § Lockstep escape hatch). |
| A new catalog message id for "retired command" | The verbatim `Unknown command: N` text quoted in the wiki | See F9. The id cannot reach its only audience. |

**Installation:** none. The phase installs no package.

## Package Legitimacy Audit

**Not applicable. The phase installs no external package.** The only install is rebuilding `.venv311` from the project's own `pyproject.toml` `[test]` extra, whose packages are already pinned by the project and already used by CI. **Packages removed:** none. **Packages flagged:** none.

## Measured Substrate — the eight questions, answered with evidence

### Q1 — Every place the version lives, and how CI turns it into a published version

**The two source strings.** No others exist.
- `firestarter_app/firestarter/__init__.py:1`: `__version__ = "3.0.0b48"` `[VERIFIED: Read, this session]`
- `firestarter_fw/include/version.h:11`: `#define VERSION "3.0.0b33"` `[VERIFIED: Read, this session]`

**Derived, not stored:**
- `firestarter_app/pyproject.toml:11`: `dynamic = ["version"]`. Lines 92-93 read `[tool.setuptools.dynamic]` and `version = { attr = "firestarter.__version__" }`. `[VERIFIED: Read]` There is no static version anywhere in `pyproject.toml`.
- `firestarter_fw/include/firestarter.h:44`: `#define FW_VERSION VERSION ":" RURP_BOARD_NAME`. `[VERIFIED: grep this session]` `platformio.ini` carries no version. `library.json` does not exist (`ls: cannot access 'library.json'`).
- The published `fw` identity is `<version>:<board>`. The host's `_probe_port` extracts with `re.match(r"[\d.x]+", identity)` (`serial_comm.py:897`) `[VERIFIED: Read]`, so `3.1.0b1:leonardo` reaches the version gate as `3.1.0`. `_validate_firmware_version` refuses only `major < 3` and anything below `2.0.0`, so `3.1.0` passes.

**Nothing pins either string.**
- **Grep:** no test in `firestarter_app/tests/` or `firestarter_fw/tests/` / `test/` pins the live literal. The `3.0.0b*` literals in tests are frozen report fixtures (`3.0.0b11`, `3.0.0b15`, `3.0.0b19`) and monkeypatched channel values (`3.0.0b1`, `3.0.0`). The firmware `tests/test_update_version.py` works on `tmp_path` copies seeded from `tests/golden/stable-baseline.h` (`#define VERSION "1.2.3"`).
- **Falsification probe, app:** the scratch `git archive` copy was bumped to `3.1.0b1` and the full suite re-run on Python 3.11. The result was identical to the unbumped baseline: `1 failed, 2362 passed in 187.19s`. The one failure appears in both runs. It is a scratch-copy artifact: `test_every_datasheet_value_is_a_tracked_path_or_unsourced_with_note` asserts that `datasheets/*.pdf` is git-tracked, and the `git archive` copy has no `.git`. `firestarter --version` printed `Firestarter, version 3.1.0b1`, and `is_prerelease_build()` printed `True`, so the channel stays beta. `[VERIFIED: command output, this session]`
- **Falsification probe, firmware:** a scratch clone was bumped to `#define VERSION "3.1.0b1"`, then `/usr/local/py-utils/bin/pytest tests/ -q` ran: `284 passed, 32 skipped`. All 32 skips are `meta repo checkout absent`, the same skips CI takes. In place, unbumped: `316 passed in 9.93s`. The stale-path failures described by memory `reference_firmware_tests_tree_is_red_stale_planning_paths` **are fixed**. That memory is now historical. `[VERIFIED: command output]`
- **Native Unity suites:** no file under `firestarter_fw/test/` mentions `VERSION` or `3.0.0b` (grep returned nothing). `[env:native]`'s `src_filter = +<proms/>` excludes `firestarter.cpp`, the only `FW_VERSION` consumer besides `hardware_operations.cpp`. The bump is therefore invisible to native tests. `[VERIFIED: grep + firestarter_fw/CLAUDE.md § Native]`
- The firmware size-baseline gate is gone. Only stale `__pycache__` entries mention `test_check_size_baseline`. The string gets one character shorter (8 → 7), so flash moves by one byte or so, and the published FWBLANK-05 figures stay valid to the byte they claim. `[VERIFIED: grep]`

**How CI turns the source into a published version.** Both repos use the same logic.
- `firestarter_app/.github/scripts/update_version.py:13`: `get_version()` parses `(?P<major>…)\.(?P<minor>…)\.(?P<patch>…)(?P<pre>(b|rc)[0-9]+)?` and returns all four groups. `compute_beta_version` (`:81-92`) then uses **only** `f"{major}.{minor}.{patch}"` as `base` unless `BETA_VERSION` is set. `_git_tag_scan_fallback` (`:61-78`) returns `f"{base}b{n}"` with `n = max(nums) + 1 if nums else 1`. `[VERIFIED: Read]` The firmware copy is the same logic on `header_file = "include/version.h"` (`firestarter_fw/.github/scripts/update_version.py:10-95`). `[VERIFIED: cat -n this session]`
- **The source's own pre-release suffix is discarded.** `3.1.0b1`, `3.1.0b7` and plain `3.1.0` all publish as `3.1.0b1` on the first beta push.
- `beta-release.yml` (app) runs the tests, the bump (`env BETA_VERSION: ${{ github.event.inputs.beta_version }}`, empty on a push), a `git-auto-commit-action` (a no-op when the file already reads `3.1.0b1`), and a Release. Its `pypi` job then calls `publish.yml` with `tag: ${{ needs.github.outputs.version }}`. `publish.yml` builds from `ref: ${{ inputs.tag || github.ref }}` and uploads with `skip-existing: true`. `[VERIFIED: cat -n this session]`
- `beta-build.yml` (firmware) runs `pio test -e native`, `pytest tests/ -v`, the bump, an auto-commit, `pio run` with `-D DEV_TOOLS=1`, and the py32 VERSION assertion (`EXPECTED="${EXPECTED_VERSION}:py32f071"`), then a pre-release with `make_latest: false`. `[VERIFIED: cat -n]`

**Falsification probe, the real scripts run against a `3.1.0b1` source, in scratch:**
```
== app, no 3.1.0 tags               DRY_RUN: 3.1.0b1
== app, after a 3.1.0b1 tag exists  DRY_RUN: 3.1.0b2
== app, only 3.0.0bN tags           DRY_RUN: 3.1.0b1
== app, NOT on beta (stable path)   DRY_RUN: 3.1.1
== fw,  no 3.1.0 tags               DRY_RUN: 3.1.0b1
== fw,  after a 3.1.0b1 tag exists  DRY_RUN: 3.1.0b2
== fw,  only 3.0.0bN tags           DRY_RUN: 3.1.0b1
== fw,  NOT on beta (stable path)   DRY_RUN: 3.1.1
```
**Against the real repos today, unbumped:** `firestarter_app` prints `DRY_RUN: 3.0.0b51`, and `firestarter_fw` prints `DRY_RUN: 3.0.0b36`. The dry-run modifies no file (`git status --short` was empty afterwards). `[VERIFIED: command output]`

**No collision is possible for `3.1.0b1`.**
- Remote tags: `git ls-remote --tags origin` in `firestarter_app` ends `3.0.0b48 3.0.0b49 3.0.0b50 v1.21 v1.22 v1.23`, and in `firestarter_fw` it ends `3.0.0b33 3.0.0b34 3.0.0b35 v1.21 v1.22 v1.23`. Neither has any `3.1.0*`.
- PyPI (`https://pypi.org/pypi/firestarter/json`): the latest stable `info.version` is `2.0.9`. The highest releases are `…3.0.0b48, 3.0.0b49, 3.0.0b50`. The `3.1*` list is `[]`.
- `3.1.0b1` sorts above `3.0.0b50` under PEP 440. `[VERIFIED: command output]`

**The `v1.2x` tags in the sub-repos are inert.** `gh api repos/henols/firestarter_fw/releases` shows 0 releases with a `v`-prefixed tag, and the same holds for `firestarter_app`. The host's `pre` channel enumerates *Releases*, not tags. `[VERIFIED: gh api]`

**Current published state, which contradicts STATE.md.** `origin/beta` reads `__version__ = "3.0.0b50"` (app) and `#define VERSION "3.0.0b35"` (fw). The PRs `henols/firestarter#91`, `henols/firestarter_app#72` and `henols/firestarter_fw#70` are all `"state":"MERGED"`, `mergedAt 2026-09-20`. `STATE.md:30` says "**v1.40 is still unmerged** … nothing is published and no PyPI version is burned". That is stale. The same line calls the `v1.40` tag "local-only", but `git ls-remote --tags origin` in the meta repo lists `v1.40`. `[VERIFIED: gh pr view + ls-remote]` The planner should hand this to the orchestrator. It is not phase work, but plans must not reason from STATE.md's claim.

### Q2 — The "same commit pair" mechanics

**Precedent inside this milestone.** 204-01 wrote "firmware `268d844`, host `f6d3724`, meta gitlink advance `5e675d35` (feat/feat/chore)" `[VERIFIED: 204-01-SUMMARY.md:153]`. 204-03 wrote "firmware `305b2f4` (feat), host `2a17fd7` (feat), meta gitlink advance `85e49226` (chore)" `[VERIFIED: 204-03-SUMMARY.md:188]`. The meta commit's body names both sub-repo shas (`git show 5e675d35`: "firestarter_fw @ 268d844 …", "firestarter_app @ f6d3724 …").

**Precedent for a version-base move.** v1.4 used `cfc0e1c chore(v1.4): reconcile __version__ base to 3.0.0_dev for lockstep with firmware` (app) and `31fa175 chore(09-02): bump firmware version 2.0.11-dev -> 3.0.0-dev` (fw). Each was a one-line diff to the version file only. `[VERIFIED: git show --stat]` `.planning/milestones/v1.4-RELEASE-PROCEDURES.md` § "Base-version mismatch caveat" option 1 is the same idea: reconcile the bases in source, then let auto-increment run.

**Where commits land.** Directly on `v1.41-verification-to-host` in each sub-repo, inside the submodule, never on `beta`. All three repos are on that branch now, and **none is pushed**: each reports `fatal: no upstream configured`, and the meta `ls-remote` shows no `refs/heads/v1.41-verification-to-host`. `[VERIFIED]` Current gitlinks match the sub-repo HEADs: meta `ls-tree HEAD` gives `firestarter_app d723cf7…` and `firestarter_fw 6e11d05…`, which equal each sub-repo's `rev-parse HEAD`. **The meta gitlink must be advanced after the pair** (memory `reference_gitlink_advanced_per_phase_since_v136`, confirmed by the 204 precedent above).

**The conflict the bump creates.** This is the finding that shapes the plan. `git merge-tree --write-tree` ran in scratch clones:
```
firestarter_app: merge-base version "3.0.0b48"  beta "3.0.0b50"
  bumped branch vs beta   → CONFLICT (content): Merge conflict in firestarter/__init__.py
  unbumped branch vs beta → clean (no conflicted paths)
firestarter_fw:  merge-base version "3.0.0b33"  beta "3.0.0b35"
  bumped branch vs beta   → CONFLICT (content): Merge conflict in include/version.h
  unbumped branch vs beta → clean
```
The *only* commits on `origin/beta` missing from each milestone branch are the v1.40 merge, PR #69/#68 (`docs: point at henols/firestarter, not the old firestarter_prom name`), and two bot "Apply automatic changes" bumps. The diffs are two files each:
- app: `.planning/codebase/STACK.md` and `firestarter/__init__.py`
- fw: `.github/CONTRIBUTING.md` and `include/version.h`

`[VERIFIED: git log v1.41..origin/beta + diff --stat]` → Fork **F1**.

**Gates on a version change.** app CI runs ruff, ruff format, pytest with coverage, and a smoke install. Firmware `build.yml` runs `native_nodevtools`, `pytest tests/` and `pio run` on a push to a non-`beta` branch. **No version-agreement test exists in either repo.** The dry-run pair (V3) is the only mechanical agreement check available. Proposing a new test is not needed for REL-01. Such a test also could not see across repos in CI, because each checkout lacks its sibling (the firmware CLAUDE.md states the same for `test_flash_path_record_sync`).

### Q3 — What each host does with each firmware (the compatibility matrix)

The terms below mean the following:
- **"old host"**: any published CLI up to and including `3.0.0b50`.
- **"old firmware"**: any published firmware up to and including `3.0.0b35`.
- **"new"**: `3.1.0b1`.

**(a) Old host → new firmware:**

| Command | What happens | Evidence |
|---|---|---|
| `verify` | Refused at init. The output is `ERROR: Unknown command: 6` / `Programmer error during VERIFY: Programmer error during init: Unknown command: 6` / `Verify for W27C512 failed.` with exit 1, in 3.56 s, with no side effect (three whole-device reads, one digest). | `[VERIFIED: 204-BENCH-MATRIX.md:353-363]`, host `3.0.0b49` |
| `blank` | Refused at init. The output is `ERROR: Unknown command: 4` / `Programmer error during BLANK_CHECK: Programmer error during init: Unknown command: 4` with exit 1, in 3.49 s. | `[VERIFIED: 204-BENCH-MATRIX.md:372-381]` |
| `dev test` | Its verify and blank-check steps send ordinals 6 and 4. Published `chip_test.py` routes `OP_VERIFY` / `OP_BLANK_CHECK` to `verify_eprom` / `check_eprom_blank`, which send `COMMAND_VERIFY` / `COMMAND_BLANK_CHECK` (`git show 3.0.0b50:firestarter/eprom_operations.py:2165,2348`). Those steps are therefore refused, and a `--submit` from this pairing files a failure that is **not the chip's**. | `[VERIFIED: git show 3.0.0b50]` for the ordinals; step outcome `[ASSUMED]` from the structure, not bench-observed |
| **`write` onto a non-blank UV EPROM** | **Refused by nothing.** The old host has no host write guard: `write_blank_guard.py` "exists on disk, but not in '3.0.0b50'". New firmware has no write-init blank check: `mem_util_blank_check` and `FLAG_SKIP_BLANK_CHECK` are absent from `src/` and `include/`. The program loop runs against non-blank content and fails partway (`MSG_ERR_MAX_PULSES` after the budget), leaving the part partly programmed. PROJECT.md's D-2 already says the host check "is the whole safety net … and it has no second line of defence". The old-host pairing is the case where that net is absent. | `[VERIFIED: git cat-file -e 3.0.0b50:… + grep of firestarter_fw/src,include]`. **Not recorded by any prior phase** (searched 202–206 records). The failure shape (`0xBD` partway) is `[ASSUMED]`. |
| `erase -b` | The old host clears no flag for `-b`, relying on firmware's `CMD_ERASE` arm to run `mem_util_blank_check` as the end operation. New `eprom.cpp:50-52` has `case CMD_ERASE: … = eprom_erase_execute; break;` with no end operation. **`erase -b` silently stops checking**, and exits 0 on the erase alone. | `[VERIFIED: Read firestarter_fw/src/proms/eprom.cpp:50-52; git show 3.0.0b35:src/proms/eprom.cpp:50-55]` `[ASSUMED]`: exact exit behaviour not bench-observed |
| `write -b` | Old host still composes `0x08`. New firmware treats the bit as reserved, so the effect is the same as before (no check). | `[VERIFIED: constants.py:130-141 reserved note]` |
| Bare `fw` / `fw -i` | **Recommends and installs `3.1.0b1`.** Any pre-release host auto-routes to `--pre` (`cli_handlers.py:302-319`, the same in `3.0.0b50:307`). `fetch_release_info('pre')` takes the highest PEP 440 pre-release. `_compare_versions` does `Version(current) >= Version(latest)` (`firmware.py:290`), so `3.0.0b35 < 3.1.0b1` means "not up to date". **The old host's own updater walks the user into the pairing above.** | `[VERIFIED: Read]` |
| Stable users (`2.0.9` host) | Unaffected. `/releases/latest` is `2.0.6 prerelease=false`, and `3.1.0b1` is a pre-release, so it never becomes "latest". | `[VERIFIED: gh api repos/henols/firestarter_fw/releases/latest]` |

**(b) New host → old firmware:**

| Command | What happens | Evidence |
|---|---|---|
| `verify`, `blank` | Work. The new host sends only `CMD_READ`: `verify` matched with exit 0, and `blank` reported not-blank with exit 1, with no unknown-command line. | `[VERIFIED: REQUIREMENTS.md:103, 204-BENCH-MATRIX]` |
| `write` (no `-b`) | Works. The host guard reads the region first, and old firmware also runs its own region-scoped write-init check. The redundant check costs time and does no harm. | `[VERIFIED: 205-BENCH-MATRIX B3 mechanism]` |
| **`write -b`** onto a non-blank UV part | **Refused by the old firmware**: `ERROR: Not blank, at 0x000000, v: 0x11` / `Programmer error during WRITE: Programmer error during init: Not blank, at 0x000000, v: 0x11` / `Write to W27C512 failed.` with exit 1 and no side effect. Cause: the new host never composes `0x08`. | `[VERIFIED: 205-BENCH-MATRIX.md:252-266]` |
| `dev test` masked UV slot writes | Refused by old firmware for the same reason. | `[VERIFIED: 205-CONTEXT.md:115-117]` (stated). Not separately bench-observed. |
| Plain `erase` (no `-b`) on erasable parts that ride the EPROM handler (W27C512 class) | **Now also blank-checks at the end on old firmware.** The new host never sets `0x08`, and old `eprom.cpp` runs `mem_util_blank_check` as the end operation whenever the bit is clear. So an erase that leaves stray bits now *fails* where it used to "succeed". | `[VERIFIED: git show 3.0.0b35:src/proms/eprom.cpp:50-55 quoted: "case CMD_ERASE: … if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) { handle->firestarter_operation_end = mem_util_blank_check; }"]`. **Not recorded by 205's D-04** (only `write -b` and `dev test`). Not bench-observed. |
| `fw` / `fw -i` | Offers `3.1.0b1` (`--pre` auto-route). Installing it resolves every row above. | `[VERIFIED: Read cli_handlers.py:302-319]` |

**Is there any host firmware-minimum check that should now name `3.1.0`?** No. The only version policy is `major < 3` → refuse, and `< 2.0.0` → refuse (`serial_comm.py:713-747`, read this session). D-4 excludes adding one. The phase changes no host code.

**How a user upgrades:**
- **Host:** `pip install --pre --upgrade firestarter` (a beta install). Verify it with `firestarter --version`. This follows `Install-Beta.md:43-49`.
- **Firmware:** `firestarter fw -i`. A beta host auto-routes to `--pre`: `"Beta app detected — defaulting to --pre. "` (`cli_handlers.py:317`).
- **Pin the old firmware instead:** `firestarter fw -i --firmware-version 3.0.0b35`. The option exists in `3.0.0b50` too (`git show 3.0.0b50:firestarter/cli_handlers.py:1086`), and the help reads `"Pin exact firmware version (e.g. 3.1.0, 3.1.0b2, 3.1.0rc1)."` (`cli_handlers.py:1542`, read this session).
- **The order matters:** upgrade the CLI **first**, then the firmware.

### Q4 — The wiki

**Where it lives.** `/workspaces/firestarter.wiki`, with remote `origin https://github.com/henols/firestarter.wiki.git`. That is the meta repository's wiki, which moved with the `firestarter_prom → firestarter` rename. The sub-repo wikis are disabled (`has_wiki=false`, per STATE.md § v1.35). `.planning/config.json` lists `firestarter.wiki` in `planning.sub_repos`, so GSD tooling treats it as a sub-repo. `[VERIFIED: git remote -v; Read config.json]`

**Is the clone current? It is current plus one unpushed commit.**
- `git ls-remote origin` gives `81229d8… refs/heads/master`.
- The local branch reads `master f967398 [origin/master: ahead 1]`.

The unpushed commit is `f967398` (2026-09-15), "Repoint the tracker at henols/firestarter and fix the firmware repo name". It touches `Contributing.md`, `Install-Beta.md` and `Testing-Chips.md`. **The live wiki still carries the defect it fixes.** `git show origin/master:Contributing.md` reads "`firestarter_prom` is the only repository where GitHub Issues are maintained … Issues are disabled on both `firestarter` and `firestarter_app`". Its PR-routing list still sends firmware changes to `firestarter`, which is now the meta repo. No `.planning/` record mentions `f967398`. **Any push from this clone publishes `f967398` too.** → Fork **F7**. `[VERIFIED: git log/show/ls-remote]`

**Pages (1561 lines total):** `Breaking-Changes` (102), `Chip-Database-Fields` (94), `Contributing` (32), `Home` (56), `Install-Beta` (101), `Lockable-PROMs` (420), `Pin-Maps` (387), `Programming-Protocols` (130), `Shell-Completion` (74), `Shield-Revisions` (47), `Testing-Chips` (107), `_Sidebar` (11).

**Which pages document `verify`, `blank`, `write`, `-b`, firmware update, and compatibility?**
- **None documents `write`, `verify`, `blank`, `-b`, `--verify` or `--full`.** A grep of every page finds only prose uses ("reads, writes, erases and verifies", `Home.md:7`).
- Firmware update: `Home.md:26-37` (`firestarter fw -i`) and `Install-Beta.md:53-63` (`firestarter fw -i -b uno`, "fetches beta firmware automatically").
- Compatibility: `Breaking-Changes.md` only.
- The app README's command table (`README.md:70-88`) lists `write`, `verify` and `blank` one line each and says "Every command takes `--help`". The README points to the wiki for everything else (`README.md:100`).

**Text that becomes wrong or misleading after v1.41.** All of it was read this session.
1. `Breaking-Changes.md:9-12`: "**The firmware and the CLI are upgraded together.** Every wire-protocol change below breaks mixed versions — a new CLI cannot drive old firmware, and old firmware cannot be driven by a new CLI. A mismatched pair fails with a timeout or a decode error rather than misbehaving quietly." **This is false for 3.1.0b1.** A new CLI drives old firmware for `verify` and `blank`. An old CLI fails with a named `Unknown command: N`, not a timeout. And one pairing does "misbehave quietly": the unguarded write and the silent `erase -b`.
2. `firestarter_app/README.md:49-50`: "**The CLI and the firmware are upgraded together.** A mismatched pair fails with a timeout or a decode error" is the same claim, outside the wiki. → Fork **F6**.
3. `Install-Beta.md:47`: "`--version` must print a beta version such as `3.0.0b34`". This is stale as an example. It is not wrong, since the rule is "a beta version".
4. `Testing-Chips.md` does not mention version pairing. A tester with an old CLI on new firmware (or the reverse) produces failing reports that are not the chip's fault. See Q3(a) `dev test` and Q3(b).
5. `Breaking-Changes.md:102` carries `<!-- firestarter-claim-stamp: db-sha256-16=ccbc8d2c4866a5af verified=2026-08-31 -->`. Its checker was retired with `tools/wiki/` (CLAUDE.md). The stamp is inert HTML. Leave it untouched: editing it would claim a re-verification nobody performed.

**Existing section-heading convention.** `## v1.32 — chip database`, `## v1.20 — …`, `## v1.10 — …`. These are *milestone* labels, not product versions. → Fork **F4**.

**How wiki edits were made, reviewed and pushed before.** v1.35 Phase 171-01 is the canonical precedent:
- Author in a working clone and commit there (`bf787fb`, "authored (not yet pushed)").
- Run the link oracle pre-push.
- **Operator human-action checkpoint:** "Operator approved the live wiki push (\"push approved\") after reviewing the pre-flight evidence, the three-file commit stat and both navigation hunks".
- Push (`7ec9988..bf787fb master -> master`).
- Re-run the oracle "against a second, independent fresh clone (not the working scratch clone)".

`[VERIFIED: milestones/v1.35-phases/171-*/171-01-SUMMARY.md:29,82-91]` **The oracle `wiki.py links` no longer exists**: `tools/wiki/` was deleted on 2026-09-08, and CLAUDE.md says "**No automated wiki guard exists now.**" The plan needs an inline link check instead (V8).

**Changelog / release notes.** No `CHANGELOG*` exists in any of the three repos (`ls | grep -i change` found nothing). `firestarter_fw/README.md:81`: "Version history is in [Breaking Changes](…)". **`Breaking-Changes` is the release-notes page.**

**Wiki-specific memories, verified.** `reference_github_wiki_must_be_created_in_web_ui` does not apply: the wiki repo exists and accepts git pushes, and its default branch is `master` (confirmed). `project_v135_wiki_only_reversal`: docs live only in the wiki, with no in-repo source tree and no publish command. That matches the current layout.

**The push is outward-facing.** A wiki push publishes the moment it lands. It needs no build, has no preview, and has no PR. It must sit behind a `checkpoint:human-action`, and the phase **must not run under `--auto` / `--chain`**, which auto-approve human gates (memory `reference_auto_mode_autoapproves_outward_facing_gates`).

### Q5 — The real user-facing semantics to document

Everything below is quoted from the syrupy-pinned help text in `firestarter_app/tests/__snapshots__/test_characterization.ambr`, read this session. The pinned text is what `--help` prints, because the Click docstrings are the help text.

**`write` (`.ambr:375-451`):**
- `-b, --no-blank-check`: "Skip the blank check before write (erase still runs if the chip supports it)." The docstring adds: "skip the blank check only -- a pre-write erase still runs on electrically-erasable chips". **Memory `reference_write_b_skips_erase` ("`write -b` SKIPS ERASE") is obsolete.** The current `-b` does not skip erase. `--skip-erase` does: "Also skip the pre-write erase … WARNING: skipping erase on a non-blank electrically-erasable chip leaves un-erased bits that cannot be reprogrammed."
- Where the check runs: "Before the write reaches the port, the host -- not the firmware -- checks that the target region is blank. Four protocol families never receive that check: 0x0D (28C parallel) and 0x05 (flash4) auto-erase per page immediately before each write, and the SRAM and FRAM families have no blank state to check at all."
- What the help text does *not* say, which the wiki should: the check applies to `GUARDED_PROTOCOL_IDS: frozenset[int] = frozenset({0x06, 0x07, 0x08, 0x0B, 0x10})` (`write_blank_guard.py:58`, Read) **only when no erase ran**. `is_erase_exempt` exempts a part that has `FLAG_CAN_ERASE` set without `--skip-erase`, and **withdraws** that exemption for `0x06` at a non-zero `-a` address. In user terms: **UV EPROMs are checked. Erasable parts are checked only with `--skip-erase`, or for NOR flash when writing at a non-zero address.** The check is region-scoped: it reads exactly the bytes about to be written. The refusal line is `"Refusing write to {chip_name}: not blank at 0x{address:06X}, v: 0x{value:02X}."` (`write_blank_guard.py:118-119`, Read).
- `--verify`: "After a successful write, read the written region back and compare it through the same engine `verify` uses. Changes THIS INVOCATION's exit-code contract:
  - 0: the write landed and the read-back matched;
  - 1: the invocation ended for a reason the host or the firmware decided (a blank-guard refusal, a firmware error during the write, a malformed address, or a read-back that completed and disagreed);
  - 2: the transport or the hardware failed in ANY phase of the run -- the guard read, the write itself, or the read-back.

  Without --verify, write exits 0 on success and 1 on any failure, exactly as before."

  Opt-in: the default write time is unchanged (D-3). The verdict lines (`cli_handlers.py:586-597`, Read) are:
  - `"Write to {eprom}: verified -- the read-back matches."`
  - `"Write to {eprom}: landed, but the read-back did not verify."`
  - `"Write to {eprom}: landed, but could not be verified -- the read-back failed."`
  - `"Write to {eprom}: did not complete -- nothing was verified."`
- `--full`: "With --verify, report every coalesced mismatching range in the read-back comparison, not just the first. Has no meaning and is refused without --verify."

**`verify` (`.ambr:351-373`):** "Exits 0 on a match, 1 on a mismatch, 2 on a transport, hardware, setup, or region failure. … a region refusal -- an explicit --size longer than the input file, or a region running past the chip's end -- is reported before the serial port ever opens. Without --size, the compared region is the input file's own length; with it, --size wins." Options: `-a/--address`, `-s/--size`, `-f/--force`, and `--full` ("Report every mismatching range, not just the first.").

**`blank` (`.ambr:97-118`):** "Exits 0 when blank, 1 when at least one byte is not blank, 2 on a transport, hardware, setup, or region failure. … Without --size, the checked region is the whole chip". Its `--full` reads "Report every non-blank range, not just the first."

**`--full` output shape** (`compare.py`, Read):
- `MAX_RETAINED_RANGES: int = 64` (`:33`), which "keeps `--full`'s output bounded at 65 lines regardless of device size".
- Range line: `f"Mismatch 0x{r.start:06X}-0x{r.end:06X} ({r.count} bytes)"`.
- Overflow line: `f"… and {result.extra_ranges} more ranges, {result.extra_bytes} bytes"`.
- Classification labels: `FP_BLANK_CONTACT = "blank/contact"`, `FP_ADDRESS_LINE = "address-line"`, `FP_TRANSPORT = "transport"`, `FP_INDETERMINATE = "indeterminate"`, `FP_MATCH = "match"` (`:46-50`).

**`erase -b` (`.ambr:164-205`):**
- "`-b`/`--blank-check` requests a blank check performed **after** the erase, through the same host-side engine `blank` uses. Note the inverted sense against `write`, whose `-b`/`--no-blank-check` skips a check performed before it -- that inversion is unchanged."
- Exit codes: "With `-b` … 0 erased and blank, 1 erased but not blank, 2 when the check itself fails on transport, hardware or setup."
- "`-s` and `-b` cannot be combined … That combination is refused, exit 2, before the erase runs."
- Memory `reference_w27c512_bench_write_erase_gotcha`'s "`-b` polarity inverted" is **confirmed**. It means `erase -b` checks, while `write -b` skips.
- Observed, cosmetic, out of scope: the refusal string at `cli_handlers.py:1076-1081` prints literal RST double backticks (`` ``-s``/``--sector-address`` ``) to the terminal.

**How `-b` changed: in where it runs, not in what it means.** Before 3.1.0, `write -b` composed wire bit `0x08` so the *firmware's* write-init check was skipped. From 3.1.0, the firmware has no such check, the bit is reserved, and `-b` skips the *host's* check (`constants.py:130-141`, Read: "`-b` now reaches the host-side write guard … as an explicit keyword-only signal instead of a wire bit"). The meaning ("skip the pre-write blank check, still erase") is identical. **The observable difference appears only in a mixed pairing** (Q3(b), `write -b`).

**Ordinals 4 and 6.** 4 was the standalone blank-check command (`CMD_BLANK_CHECK` / `COMMAND_BLANK_CHECK`), and 6 was the verify command (`CMD_VERIFY` / `COMMAND_VERIFY`). Both are "retired in 3.1.0" and must "NEVER be reused" (`constants.py:53-71`, `firestarter.h:53-73`, read this session). **They were replaced by nothing on the wire.** `verify` and `blank` now issue `CMD_READ` and compare on the host (CMP-01…08, Phase 202). Wire bit `0x08` (skip-blank-check) is retired and reserved the same way (`constants.py:130`, `firestarter.h:159`).

### Q6 — Criterion 4 (no Release from the meta repo, bare tag)

- **The meta repo has no workflows at all.** `ls /workspaces/.github/workflows/` returns `No such file or directory`, and `git ls-files .github` lists only `CONTRIBUTING.md` and four `ISSUE_TEMPLATE` files. **Nothing can cut a Release on a tag push.** `[VERIFIED]`
- **The meta repo has zero Releases.** `gh api repos/henols/firestarter/releases --jq length` prints `0`. `[VERIFIED]`
- **Where the tag is created.** At milestone close, in `.claude/gsd-core/workflows/complete-milestone/steps/git-tag.md`. It runs `git tag -a v[X.Y] -m "…"`, then asks "Push tag to remote? (y/n)", then runs `git push origin v[X.Y]`. **It never calls `gh release`.** `ship.md` pushes branches only (`:194,199,491,521`). `[VERIFIED: grep + cat]` `config.json` sets `"create_tag": true`.
- **In this phase**, `git -C /workspaces tag --list v1.41` is empty. The phase must create no tag in any of the three repos. The sub-repo `3.1.0b1` tags are created by CI at the beta push, which is after this phase.
- **Why it matters.** Old CLIs resolving `henols/firestarter/releases` would parse a `v1.41` tag as PEP 440 `1.41`, making `Version("3.0.0b…") >= Version("1.41")` true, which means "already up to date, forever". `[VERIFIED: .planning/notes/999.9-repo-rename-impact-analysis.md:86-92]`
- **Proving the negative in-phase:** V9. It is a *state* assertion. It cannot prove a future close will not cut a Release. That protection is the CLAUDE.md rule plus the fact that `git-tag.md` has no `gh release` step.

### Q7 — Hazards that change the plan's shape

Each memory lead was verified against the current tree:

| Memory lead | Status now | Effect on the plan |
|---|---|---|
| `reference_gsd_commit_switches_branch_on_stale_milestone` | Standing hazard. | Run `git -C /workspaces rev-parse --abbrev-ref HEAD` after **every** `gsd-tools query commit`, and check `git ls-tree HEAD firestarter_app firestarter_fw`. |
| `reference_fw_build_yml_github_dir_not_ignored_cuts_stable_release` | Live on `main` only. | Nothing in this phase touches `main`. Plans must not open any PR to `main`. |
| `reference_publish_yml_release_trigger_does_fire` | Confirmed by `publish.yml:2-6`. | Beta publishing goes through `workflow_call`. Not triggered in this phase. |
| `feedback_gsd_pushes_at_ship_never_ad_hoc` | Standing. | **No sub-repo or meta push in this phase.** The wiki push is the one sanctioned exception, behind an operator checkpoint, as in v1.35 Phase 171. |
| `feedback_stable_release_operator_gated` | Standing. | `3.1.0b1` is a beta, and nothing is promoted to stable. |
| `reference_host_cannot_see_firmware_prerelease_suffix` | **Partly superseded by this bump.** The `b` suffix is still invisible, but `3.1.0` vs `3.0.0` is now visible. | Recorded under Deferred. It is informational for the wiki: `fw` shows the full `3.1.0b1` string (`check_current_firmware` parses the `FW:` line and does not truncate). |
| `reference_firmware_b23_b24_b25_are_version_bump_only` | Confirms a version bump can be the only delta between two published images. | `3.1.0b1` will differ from `3.0.0b35` in real code (all of v1.41), so nothing to do. |
| `reference_devcontainer_py312_masks_ci_py39` | **Stale in detail.** `requires-python = ">=3.11"` (`pyproject.toml:12`, Read). The warning's substance stands: run on 3.11. | Use the rebuilt `.venv311`. |
| `reference_firestarter_app_python_test_env` | **Stale.** It names `/usr/local` and 3.12. | Use `.venv311`. **Its interpreter is currently dangling** (§ Environment). |
| `reference_firmware_tests_tree_is_red_stale_planning_paths` | **Fixed.** `316 passed` in place. | Run `pytest tests/` without `--ignore`. |
| `reference_gate_idioms_that_fail_open` / `reference_devcontainer_grep_is_ugrep_honors_gitignore` / `reference_grep_qF_dash_leading_pattern_exits_2` | **Confirmed live.** `type grep` shows a shell function that re-execs **ugrep** with `--ignore-files`. `/usr/bin/grep` is `GNU grep 3.11`. | Every verify command uses `/usr/bin/grep`, `-F -e` for patterns, and explicit `[ "$x" = "expected" ]` equality, never a bare pipeline exit. |
| `reference_auto_mode_autoapproves_outward_facing_gates` | Standing. | The wiki plan is `autonomous: false`. Do not run the phase under `--auto` / `--chain`. |
| `reference_gitlink_advanced_per_phase_since_v136` | Confirmed by the 204 precedent. | Advance the gitlinks in the phase. Do not tell executors to leave them alone. |

### Q8 — Runnable verify commands

See § Verification Commands (V1–V10). **The two commands the prompt names do not currently resolve:**
- `.venv311/bin/python` → `No such file or directory`. The venv's `pyvenv.cfg` has `home = /home/vscode/.local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin`, and that directory no longer exists after today's container rebuild (the home dirs are dated 2026-09-23 12:34-12:35). The other `bin/*` entry points (`ruff`, `pytest`) exist but chain through the dangling interpreter.
- A rebuild recipe was tested in scratch: `uv venv --python 3.11` plus `uv pip install -e '.[test]'` finished in about 3.5 s with a redirected cache, gave `Python 3.11.16` and `ruff 0.16.8`, and the suite ran green (Q1).

## Open Design Forks

Each fork gives a recommendation and its evidence. None is decided. The planner either takes the recommendation and records it, or routes the fork to the operator. **Starred forks (★) touch something outward-facing or irreversible. Route those to the operator even if the recommendation seems obvious.**

**F1 ★ — How to keep the bump from conflicting with `beta`.**
- (A) **Recommended.** In each sub-repo, `git fetch origin beta`, then `git merge --no-ff origin/beta` into `v1.41-verification-to-host` *before* the bump. Then bump from `3.0.0b50` / `3.0.0b35` to `3.1.0b1`. Evidence: the unbumped merge is clean, the merged-in content is two trivial files per repo, and the resulting ship PR is mergeable with no resolution. The version line's final value is decided once, in a reviewed commit, not in a ship-time conflict editor.
- (B) Bump only, and resolve at ship. That needs an explicit checklist line: "resolve `__init__.py` / `version.h` to `3.1.0b1`". Failure mode: taking beta's side publishes `3.0.0b51` / `3.0.0b36` permanently.
- (C) Leave the source alone and dispatch with `beta_version=3.1.0b1`. **Rejected**: it fails criterion 1.

Cost of A: two merge commits in the sub-repos, and the meta gitlink points at a merge commit. If the operator objects to merging `beta` into a milestone branch, B is acceptable with the checklist line.

**F2 — Shape and order of the commit pair.** Recommended: follow the 204 precedent exactly.
1. The firmware commit (`include/version.h` only).
2. The app commit (`firestarter/__init__.py` only). Its body names the firmware sha.
3. A meta `chore(207-01): advance firestarter_fw and firestarter_app gitlinks` whose body names both shas.

Keep each version commit to the version file alone, so "the same commit pair" is inspectable by `git show --stat`.

**F3 — Where `write --verify` / `--full` / `-b` are documented "where a user will find them".**
- (A) **Recommended.** A new wiki page, for example `Writing-and-Verifying`, covering `write` (`-b`, `--skip-erase`, `--verify`, `--full`, and which parts get the pre-write check), `verify` and `blank` (`--full`, `-a`/`-s`, exit codes), and `erase -b`. Link it from `Home.md` § Reference, `_Sidebar.md`, and the new `Breaking-Changes` section. Evidence: no wiki page documents any command today (Q4), and a user looking for "how do I verify a write" will not look in "Breaking Changes".
- (B) Document only inside the `Breaking-Changes` 3.1.0b1 section. Cheaper, but criterion 3's "where a user will find them" is then arguable.
- (C) The app README. **Rejected**: REL-04 says the wiki is the only documentation home.

**F4 — The new `Breaking-Changes` section heading.** Recommended: `## 3.1.0b1 — verify and blank check run on the host` (the product version the user sees in `firestarter --version` and `fw`). Do not use `v1.41`. It is a planning label the user never sees, the GSD-reference rule extends to user-facing artifacts, and `v1.41` is the exact string criterion 4 warns parses as `1.41`. Do not relabel the existing `v1.32` / `v1.20` / `v1.10` headings in this phase. That is a separate correction, which the operator can take or leave.

**F5 — The page-wide preamble (`Breaking-Changes.md:9-12`).** Recommended: rewrite it so that compatibility is stated **per entry**, not page-wide. For example: "Each entry says which mixed pairings work. When in doubt, upgrade the CLI first, then the firmware." Keep the `pip install --pre firestarter && firestarter fw -i --pre` line, because it is still the correct order. Alternative: leave the preamble and add an exception line in the new section. That keeps a false general claim on the page.

**F6 — `firestarter_app/README.md:49-50` makes the same false claim.**
- (A) **Recommended.** Correct it in a **separate** app commit (not in the version commit), and point it at the new `Breaking-Changes` section. It reaches PyPI's long_description only at the beta cut.
- (B) Leave it. It is outside REL-04's letter, but it contradicts the milestone value "no page that claims more than the code can back".

**F7 ★ — Which wiki clone to work in, given the unpushed `f967398`.**
- (A) **Recommended.** Work in `/workspaces/firestarter.wiki`. First `git fetch` and confirm `origin/master` is still `81229d8`. **Name `f967398` explicitly in the push checkpoint.** The live `Contributing` page currently routes firmware PRs to the meta repo, so publishing the fix is a correction, not new scope.
- (B) A fresh scratch clone (the 171 precedent). `f967398` stays stranded, and the live defect stays.

Either way, the operator must see the full `git log origin/master..HEAD` before approving.

**F8 ★ — When the wiki push happens.**
- (A) **Recommended.** In-phase, behind a `checkpoint:human-action`, with every new statement version-labelled "from 3.1.0b1". This matches the 171 precedent, and it makes REL-04 verifiable against the live page in this phase.
- (B) Hold the push until the beta cut. Then REL-04 cannot be verified in 207, and a documented surface stays unpublished.

The cost of A: for the days between the push and the beta cut, the wiki describes a version PyPI does not yet serve. The labelling makes that visible.

**F9 — A dedicated "retired command" message or catalog id (the carried-forward obligation 4).** Recommended: **no catalog id.** Evidence:
- The only party that ever sends ordinal 4 or 6 is a pre-`3.1.0` host. It renders firmware messages through its **own shipped** `messages.py`, and "the pre-`3.1.0` host is shipped code this phase cannot change" `[VERIFIED: 204-BENCH-MATRIX.md:392-395]`. A new id would reach an old host as an id it does not know, which is less readable than today's `Unknown command: 6`.
- A new host never sends 4 or 6.
- It would also cost a codegen run and two sub-repo syncs that this phase otherwise avoids.

The wiki quotes the verbatim text instead, so a user who searches for `Unknown command: 6` lands on the explanation. Record the decision in the phase record so the deferral chain (204 D-05 → 205 → 207) closes.

**F10 — Scope of the compatibility matrix in the wiki.** Recommended: include all of Q3.
- **(a) old host → new firmware:**
  - `verify` / `blank` refused, with the verbatim text;
  - `dev test` steps refused, with "do not submit";
  - the **unguarded write to a non-blank UV EPROM** (safety-relevant — lead with it);
  - `erase -b` silently not checking;
  - `fw` offering `3.1.0b1`.
- **(b) new host → old firmware:**
  - `verify` / `blank` work;
  - `write -b` refused, with the verbatim text;
  - `dev test` masked UV slot writes refused;
  - plain `erase` now blank-checks.

The minimum that criterion 2 requires is the two refusals plus "what to do". The unguarded-write row is the one a user can be *harmed* by, so omitting it would leave the page claiming less danger than the code carries. Two rows (old host + new firmware `erase -b`, and new host + old firmware plain `erase`) are code-derived and not bench-observed. Phrase them without the confidence of the bench rows, or put them behind an operator decision.

## Wiki Content Specification

These are the facts the pages must carry, each tied to its evidence. Wording is the executor's, and **it must carry no phase numbers, `D-NN`, `.planning/` paths or milestone labels.**

| # | Must state | Source |
|---|---|---|
| W1 | From firmware `3.1.0b1`, the standalone verify (command 6) and blank-check (command 4) are gone from the firmware. `verify` and `blank` read the chip and compare on your computer. The numbers 4 and 6 are never reused. | Q5 Ordinals |
| W2 | Old CLI with new firmware: `verify` prints `ERROR: Unknown command: 6`, and `blank` prints `ERROR: Unknown command: 4`, both exiting 1. The chip is not touched. | 204-BENCH-MATRIX:353-381 |
| W3 | Old CLI with new firmware: **`write` no longer refuses a non-blank UV EPROM.** Upgrade the CLI before you write. | Q3(a) |
| W4 | Old CLI with new firmware: `erase -b` does not check, and `dev test` results are not valid (do not submit them). | Q3(a) |
| W5 | **What to do: upgrade the CLI first** (`pip install --pre --upgrade firestarter`), then the firmware (`firestarter fw -i`). An old CLI's `fw` will offer the new firmware, so do not accept that offer before upgrading the CLI. To stay on an old CLI, pin the firmware: `firestarter fw -i --firmware-version 3.0.0b35`. | Q3 upgrade path |
| W6 | New CLI with old firmware: `verify` and `blank` work. `write -b` on a non-blank UV EPROM is refused by the old firmware (`ERROR: Not blank, at 0x000000, v: 0x11`, with the address and value varying), and so are `dev test`'s UV slot writes. Fix: `firestarter fw -i`. | 205-BENCH-MATRIX:252-266 |
| W7 | `write -b` / `--no-blank-check` means what it always meant: skip the pre-write blank check, while the erase still runs. `--skip-erase` skips the erase. The check now runs on the CLI. It applies to UV EPROMs, and to erasable parts only when the erase is skipped (NOR flash also at a non-zero start address). It never applies to 28C EEPROMs (`0x0D`), page-write flash (`0x05`), SRAM or FRAM. It reads only the bytes about to be written. Refusal: `Refusing write to <chip>: not blank at 0x…, v: 0x…`. | Q5 write |
| W8 | `write --verify` is opt-in. It reads the written region back and compares it. Exit codes: 0 verified; 1 refused, write error, or read-back mismatch; 2 transport or hardware failure at any step. It prints one of the four verdict lines. Plain `write` keeps 0/1. `--full` needs `--verify`. | Q5 write |
| W9 | `verify` / `blank` exit 0/1/2, accept `-a`/`-s`, and stop at the first mismatch by default. `--full` lists every mismatching range, up to 64 ranges plus a summary line, with a classification (`blank/contact`, `address-line`, `match`, `indeterminate`). | Q5 verify/blank |
| W10 | `erase -b` checks after the erase, with exit codes 0/1/2. It is the inverse of `write -b`. `-s` together with `-b` is refused (exit 2) before anything is erased. For the full picture, run `firestarter blank <chip> --full`. | Q5 erase |

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| "What version will CI publish?" | Reasoning from the source string | `GITHUB_REF=refs/heads/beta python3 .github/scripts/update_version.py --dry-run` in each sub-repo | It is the publisher's own code. It proved the source suffix is discarded (Q1). |
| "Will the PR merge into `beta`?" | Eyeballing `git log` | `git merge-tree --write-tree --name-only HEAD origin/beta` | Exact and working-tree-free. It found the conflict (Q2). |
| A version-agreement test across repos | A new pytest | The dry-run pair (V3) | CI checks out each repo alone, so a cross-repo test would skip in CI. |
| A retired-command catalog id | A codegen run and syncs | Quote the verbatim text in the wiki | F9 |
| A wiki link checker package | A new tool | The inline shell check in V8 | `tools/wiki/` was retired deliberately. A one-off check suffices. |

## Runtime State Inventory

This is a version move, not a rename, so this is not strictly required. The published-state categories matter here, so they are answered:

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| Stored data | None. No datastore keys on the version string. The dev-test report schema carries `host_version` / `fw_board_identity` as recorded data, which is historical by intent. | None |
| Live service config | **GitHub wiki**: the live `master` lacks `f967398` (Q4). **PyPI / GitHub Releases**: `3.0.0b50` / `3.0.0b35` are the newest, and no `3.1.*` exists. | Wiki push (F7/F8). Releases are created at the beta cut, not in this phase. |
| OS-registered state | None. Verified: no scheduler or daemon references a version. | None |
| Secrets / env vars | `BETA_VERSION` (a workflow_dispatch input) must stay empty on the beta push, or it overrides the tag scan. `PYPI_API_TOKEN` and `PERSONAL_ACCESS_TOKEN` are unchanged. | None. Note it for ship. |
| Build artifacts / installed | The bench board's flashed firmware still reports `3.0.0b33:<board>` (the internal post-205 build): Phase 205 flashed `6e11d05`, which carries `3.0.0b33`. `firestarter.egg-info/` in the app tree carries the old version in its metadata until the next editable install. `.venv311` is broken. | Rebuild `.venv311` (Wave 0). Re-flashing the bench is optional and not required by any criterion. |

## Common Pitfalls

### Pitfall 1 — Resolving the ship-time version conflict to `beta`'s side
**What goes wrong:** the PR shows a conflict on the one version line. Accepting "theirs" publishes `3.0.0b51` / `3.0.0b36` permanently, and v1.41 never gets its `3.1.0` base.
**How to avoid:** F1(A). If F1(B) is chosen, put an explicit resolution line in the ship checklist, and re-run V3 on the merged result before the push.
**Warning sign:** `DRY_RUN:` prints a `3.0.0b…` value.

### Pitfall 2 — Believing STATE.md about v1.40
**What goes wrong:** a plan that reasons "nothing is published yet, so the next beta is b49" or "the `v1.40` tag is local-only" is wrong on both counts (Q1, the last paragraph).
**How to avoid:** base every published-state claim on `git ls-remote` / `gh pr view` / the PyPI JSON, never on STATE.md prose.

### Pitfall 3 — Pushing the wiki from the existing clone without noticing `f967398`
**What goes wrong:** a three-page tracker fix from 2026-09-15 publishes unreviewed inside a "3.1.0b1 docs" push.
**How to avoid:** the checkpoint shows `git log --oneline origin/master..HEAD` in full (F7).

### Pitfall 4 — A "new CLI cannot drive old firmware" sentence surviving the edit
**What goes wrong:** the preamble keeps the page-wide claim, and the new section contradicts it two screens down.
**How to avoid:** F5. V7 greps the preamble lines for the retired phrase.

### Pitfall 5 — Tests or gates run on a dangling interpreter
**What goes wrong:** `.venv311/bin/pytest` fails with `No such file or directory`, which reads as "suite red".
**How to avoid:** V0 first. A stale memory also points at `/usr/local` 3.12, which masks 3.11-only CI behaviour.

### Pitfall 6 — ugrep, and grep patterns that fail open
**What goes wrong:** the shell's `grep` is a ugrep wrapper with `--ignore-files`. A `grep -qF '-b'` exits 2 (memory `reference_grep_qF_dash_leading_pattern_exits_2`).
**How to avoid:** use `/usr/bin/grep -F -e '<pattern>'`, and assert with `[ "$(…)" = "expected" ]` or explicit `|| { echo FAIL; exit 1; }`.

### Pitfall 7 — GSD references leaking into the wiki
**What goes wrong:** "Phase 204", "D-4", "v1.41" or `.planning/` paths appear in user text.
**How to avoid:** V7's negative grep over the changed pages.

### Pitfall 8 — `gsd-tools query commit` switching branches
**How to avoid:** assert `v1.41-verification-to-host` after every gsd commit (V10).

## Code Examples

### The bump (after F1(A)'s merge). Firmware first, then app.
```bash
# firmware — expects the pre-bump line to be the beta-merged value
cd /workspaces/firestarter_fw
/usr/bin/grep -Fx -e '#define VERSION "3.0.0b35"' include/version.h   # F1(A); use 3.0.0b33 under F1(B)
sed -i 's/^#define VERSION "3\.0\.0b3[35]"$/#define VERSION "3.1.0b1"/' include/version.h
git add include/version.h && git commit -m "chore(207-01): bump firmware version to 3.1.0b1"

cd /workspaces/firestarter_app
sed -i 's/^__version__ = "3\.0\.0b\(48\|50\)"$/__version__ = "3.1.0b1"/' firestarter/__init__.py
git add firestarter/__init__.py && git commit -m "chore(207-01): bump app version to 3.1.0b1" \
  -m "Pairs with firestarter_fw <fw-sha>."

cd /workspaces
git add firestarter_fw firestarter_app
git commit -m "chore(207-01): advance firestarter_fw and firestarter_app gitlinks" \
  -m "- firestarter_fw @ <fw-sha>" -m "- firestarter_app @ <app-sha>"
git rev-parse --abbrev-ref HEAD   # must print v1.41-verification-to-host
```

### F1(A) — sync `beta` in before the bump (per sub-repo)
```bash
git -C /workspaces/firestarter_app fetch origin beta
git -C /workspaces/firestarter_app merge-tree --write-tree --name-only HEAD origin/beta   # expect: one line (tree sha) only
git -C /workspaces/firestarter_app merge --no-ff origin/beta -m "Merge origin/beta into v1.41-verification-to-host before the 3.1.0b1 bump"
# repeat for /workspaces/firestarter_fw
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `paths-ignore` on beta workflows | Every beta push publishes | before v1.39 (`beta-release.yml:3-16`) | A docs-only push after this phase would still cut a release |
| `release.published` → PyPI for betas | `workflow_call` from `beta-release.yml` | `publish.yml:8-20` | No event-delivery dependence |
| App base `2.0.7_dev` vs fw `3.0.0-dev` | Shared `3.0.0` base since v1.4 | `cfc0e1c` / `31fa175` | The pattern this phase repeats for `3.1.0` |
| `wiki.py links` oracle | No wiki guard (retired 2026-09-02, deleted 2026-09-08) | CLAUDE.md | The inline check in V8 |

**Deprecated / outdated memories:** `reference_write_b_skips_erase` (obsolete: `-b` no longer skips erase), `reference_firestarter_app_python_test_env` (3.12 `/usr/local`), `reference_firmware_tests_tree_is_red_stale_planning_paths` (fixed), and the version floor in `reference_devcontainer_py312_masks_ci_py39` (now `>=3.11`).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | A pre-3.1.0 host's `write` to a non-blank UV EPROM on 3.1.0b1 firmware fails partway with `MSG_ERR_MAX_PULSES`, leaving the part partly programmed. The *absence of any check* is verified, but the failure shape is not bench-observed. | Q3(a), W3 | Low for the docs, which should say "not refused" and not over-specify the error. |
| A2 | A pre-3.1.0 host's `erase -b` on 3.1.0b1 firmware exits 0 without checking. The absence of the end operation is verified. The exit path is inferred. | Q3(a), W4 | Low. Phrase it as "does not check". |
| A3 | Plain `erase` from a 3.1.0b1 host on old firmware now blank-checks at the end (code-derived, not bench-observed). | Q3(b), F10 | Medium. If it is wrong, the wiki states a cost that does not exist. Gate the line behind the operator, or omit it. |
| A4 | A pre-3.1.0 host's `dev test` verify and blank steps are marked failed, not crashed (the ordinals are verified, the step outcome is inferred). | Q3(a), W4 | Low. The advice "do not submit" holds either way. |
| A5 | Merging `origin/beta` into a milestone branch (F1(A)) is acceptable to the operator. | F1 | If it is not, use F1(B) with the checklist line. |
| A6 | A wiki page named `Writing-and-Verifying` is a suitable home (F3). The name and the split are a judgement call. | F3 | Cosmetic. The operator reviews at the checkpoint. |

## Open Questions (RESOLVED)

1. **Does the operator want `f967398` published with the 3.1.0b1 docs?** It fixes a live routing defect. Recommend yes (F7). It needs an explicit answer at the push checkpoint. RESOLVED: yes, operator decision D-02 (207-CONTEXT.md); 207-03's push checkpoint names it.
2. **F1 — merge `beta` in now, or resolve at ship?** Recommend now. This is the only fork where a wrong choice burns a PyPI version. RESOLVED: merge now, operator decision D-01 (207-CONTEXT.md).
3. **Should STATE.md's stale v1.40 claims ("unmerged", "`v1.40` tag local-only", "held gh#70/66/71 answers … release at merge") be corrected?** This is not phase work. Hand it to the orchestrator. The held-answers note may itself be actionable, since the merge already happened on 2026-09-20. RESOLVED: deferred to orchestrator housekeeping (207-CONTEXT.md Deferred Ideas).
4. **Should the `devtest-triage` skill learn that `Unknown command: 6` / `Unknown command: 4` in a report means host/firmware skew, not a chip fault?** `.claude/skills/devtest-triage/SKILL.md` has no such rule (grep found nothing). Out of scope. Worth a todo. RESOLVED: deferred (207-CONTEXT.md Deferred Ideas).
5. **Should the existing `v1.32` / `v1.20` / `v1.10` headings be relabelled to product versions?** Out of scope (F4). Offer it to the operator. RESOLVED: excluded from Phase 207 scope; offered to the operator at plan completion.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `firestarter_app/.venv311` (Python 3.11) | App gates (CI parity) | **✗ — interpreter dangling** | — | Rebuild (V0). Tested in scratch: Python 3.11.16, ruff 0.16.8, suite green |
| `uv` | Rebuilding `.venv311` | ✓ | 0.12.15 | Needs `UV_CACHE_DIR` (`~/.cache` is root-owned: "Permission denied (os error 13)") |
| `/usr/local/py-utils/bin/pytest` | Firmware `tests/` tree | ✓ | pytest 9.x | — |
| PlatformIO | Optional image check (V6) | ✓ | 6.2.0 | Skip V6. The native suites cannot see the version |
| `gh` | V9, PR/tag state | ✓ | 2.101.0 | Needs `XDG_CACHE_HOME=/tmp/…` |
| GNU grep | Every verify command | ✓ at `/usr/bin/grep` | 3.11 | The shell `grep` is a ugrep wrapper. Always use the absolute path |
| Network to github.com / pypi.org | `git fetch`, `ls-remote`, `gh api`, wiki push | ✓ (used this session) | — | — |
| Bench hardware | Nothing in this phase | not required | — | Every compatibility fact already has bench evidence from Phases 204 and 205 |

**Missing dependencies with no fallback:** none. **Missing with a fallback:** `.venv311`, via rebuild (V0).

## Verification Commands

`nyquist_validation` is `false` in `.planning/config.json`, so there is no Validation Architecture section. These are the concrete commands. Each states what it prints on failure.

**V0 — Rebuild the 3.1 test venv (Wave 0).**
```bash
cd /workspaces/firestarter_app && export UV_CACHE_DIR=/tmp/claude-uv-cache && \
uv venv --clear --python 3.11 .venv311 && uv pip install --python .venv311/bin/python -e '.[test]' && \
.venv311/bin/python --version
```
Passes with `Python 3.11.x`. It fails with `No such file or directory` (dangling) or `Permission denied (os error 13)` (cache not redirected).

**V1 — Both source strings read `3.1.0b1`.**
```bash
[ "$(sed -n 1p /workspaces/firestarter_app/firestarter/__init__.py)" = '__version__ = "3.1.0b1"' ] && \
[ "$(/usr/bin/grep -E '^#define VERSION ' /workspaces/firestarter_fw/include/version.h)" = '#define VERSION "3.1.0b1"' ] && echo PASS || { echo FAIL; exit 1; }
```

**V2 — The pair is two single-file commits, and the meta gitlinks match.**
```bash
[ "$(git -C /workspaces/firestarter_fw show --name-only --format= HEAD)" = "include/version.h" ] && \
[ "$(git -C /workspaces/firestarter_app show --name-only --format= HEAD)" = "firestarter/__init__.py" ] && \
[ "$(git -C /workspaces ls-tree HEAD firestarter_app | awk '{print $3}')" = "$(git -C /workspaces/firestarter_app rev-parse HEAD)" ] && \
[ "$(git -C /workspaces ls-tree HEAD firestarter_fw | awk '{print $3}')" = "$(git -C /workspaces/firestarter_fw rev-parse HEAD)" ] && echo PASS || { echo FAIL; exit 1; }
```
If F6(A) adds a README commit after the bump, point the `show` checks at the recorded shas rather than `HEAD`.

**V3 — The publisher's own code says `3.1.0b1` in both repos. This is the REL-01 oracle.**
```bash
for r in firestarter_app firestarter_fw; do git -C /workspaces/$r fetch -q --tags origin; \
  out=$(cd /workspaces/$r && GITHUB_REF=refs/heads/beta python3 .github/scripts/update_version.py --dry-run); \
  [ "$out" = "DRY_RUN: 3.1.0b1" ] || { echo "FAIL $r: $out"; exit 1; }; done; echo PASS
```
It fails with `DRY_RUN: 3.0.0b51` / `3.0.0b36` (not bumped) or `DRY_RUN: 3.1.0b2` (a `3.1.0b1` tag already exists, meaning a collision). It writes no file.

**V4 — The ship PR will merge cleanly** (after F1(A)).
```bash
for r in firestarter_app firestarter_fw; do git -C /workspaces/$r fetch -q origin beta; \
  n=$(git -C /workspaces/$r merge-tree --write-tree --name-only HEAD origin/beta | wc -l); \
  [ "$n" = "1" ] || { echo "FAIL $r: conflicts"; exit 1; }; done; echo PASS
```
The output is one line (the tree sha) when the merge is clean. A conflict adds path lines and `CONFLICT` messages.

**V5 — The app and firmware gates.**
```bash
cd /workspaces/firestarter_app && .venv311/bin/ruff check firestarter/ tests/ && .venv311/bin/ruff format --check firestarter/ tests/ && \
PYTHONDONTWRITEBYTECODE=1 .venv311/bin/python -m pytest tests/ -o addopts="" -p no:cacheprovider -q 2>&1 | tail -2
cd /workspaces/firestarter_fw && /usr/local/py-utils/bin/pytest tests/ -q -p no:cacheprovider 2>&1 | tail -1
```
Expect `All checks passed!`, `… files already formatted`, `2363 passed` (about 190 s, measured 2362 + 1 git-dependent test in scratch), and `316 passed` (about 10 s). Any `failed` fails the check. The firmware native suites are optional (`pio test -e native_nodevtools`), because they cannot observe the version.

**V6 (optional) — The string lands in a built image.**
```bash
cd /workspaces/firestarter_fw && PLATFORMIO_BUILD_FLAGS="-D DEV_TOOLS=1" pio run -e leonardo >/dev/null && \
strings .pio/build/leonardo/firestarter_*.elf | /usr/bin/grep -F -e '3.1.0b1' >/dev/null && echo PASS || echo FAIL
```

**V7 — Wiki content: required facts present, forbidden text absent** (run in the wiki clone before and after the push).
```bash
W=/workspaces/firestarter.wiki
for p in 'Unknown command: 6' 'Unknown command: 4' '3.1.0b1' 'pip install --pre --upgrade firestarter' '--verify' '--full' '--no-blank-check'; do
  /usr/bin/grep -rqF -e "$p" "$W"/*.md || { echo "MISSING: $p"; exit 1; }; done
! /usr/bin/grep -nE 'Phase [0-9]{3}|\bD-[0-9]+\b|\.planning/|v1\.41' "$W"/Breaking-Changes.md "$W"/Writing-and-Verifying.md || { echo "GSD REF"; exit 1; }
! sed -n 1,25p "$W"/Breaking-Changes.md | /usr/bin/grep -qF -e 'a new CLI cannot drive old firmware' || { echo "STALE PREAMBLE"; exit 1; }
echo PASS
```
Adjust the page name to whatever F3 chose.

**V8 — Every internal wiki link resolves to a page.**
```bash
cd /workspaces/firestarter.wiki && bad=0; for l in $(/usr/bin/grep -ohE '\]\([A-Za-z-]+\)' *.md | sed -E 's/^\]\(|\)$//g' | sort -u); do
  [ -f "$l.md" ] || { echo "BROKEN: $l"; bad=1; }; done; [ $bad = 0 ] && echo PASS
```

**V9 — Criterion 4: no meta Release, no stray tag.**
```bash
export XDG_CACHE_HOME=/tmp/claude-gh-cache
[ "$(gh api repos/henols/firestarter/releases --jq length)" = "0" ] && [ ! -d /workspaces/.github/workflows ] && \
[ -z "$(git -C /workspaces tag --list 'v1.41')" ] && echo PASS || { echo FAIL; exit 1; }
```
`gh` errors print text, not `0`, so an error fails closed. The tag clause holds only until milestone close, so run V9 in-phase.

**V10 — The branch has not moved.** After every gsd commit:
```bash
[ "$(git -C /workspaces rev-parse --abbrev-ref HEAD)" = "v1.41-verification-to-host" ] || { echo "BRANCH MOVED"; exit 1; }
```

**Post-push (wiki):**
```bash
[ "$(git -C /workspaces/firestarter.wiki ls-remote origin refs/heads/master | cut -f1)" = "$(git -C /workspaces/firestarter.wiki rev-parse HEAD)" ]
```
Then re-run V7 and V8 on a fresh `git clone https://github.com/henols/firestarter.wiki.git` in scratch (the 171 precedent).

## Security Domain

`security_enforcement` is absent from `config.json`, which means enabled.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | yes (publishing rights) | Branch protection on `main`/`beta`. The wiki push goes through an operator checkpoint. No `beta` push in this phase. |
| V5 Input Validation | no new input | `BETA_VERSION_RE` already validates dispatch input (`update_version.py:8`) |
| V6 Cryptography | no | — |
| V14 Configuration / supply chain | yes | Version-collision avoidance (V3). Explicit review of the wiki commit list before publishing (F7). |

### Known Threat Patterns
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Publishing a wrong or colliding version (`3.0.0b51` from a mis-resolved conflict) | Tampering / Repudiation | F1(A) plus V3 and V4 before ship. PyPI `skip-existing: true` masks a collision, so the GitHub tag is the loud failure. |
| An unreviewed commit riding a wiki push (`f967398`) | Tampering | The checkpoint shows `git log origin/master..HEAD` |
| A meta Release arming stranded-CLI "up to date forever" | Spoofing | V9, the CLAUDE.md rule, and `git-tag.md` having no `gh release` step |
| Documentation understating a hazard (the unguarded write) | Information disclosure (omission) | F10. W3 leads the compatibility section. |

## Sources

### Primary (HIGH confidence — read or executed this session)
- `firestarter_app`: `firestarter/__init__.py:1`; `pyproject.toml:11-12,92-93`; `.github/scripts/update_version.py:1-200`; `.github/workflows/{beta-release,publish,release}.yml`; `firestarter/{constants.py:8-16,53-71,128-141; firmware.py:150-412,758-900; serial_comm.py:712-747,885-945; cli_handlers.py:279-321,586-597,1074-1081,1528-1560,1700-1745; write_blank_guard.py:58,118-119,140-235; compare.py:33-50}`; `tests/__snapshots__/test_characterization.ambr:97-118,164-205,351-451`; `README.md:40-100`; `git show 3.0.0b50:` (the absence of `write_blank_guard.py`, `constants.py`, `eprom_operations.py`, `cli_handlers.py`).
- `firestarter_fw`: `include/version.h:11`; `include/firestarter.h:44,53-73`; `src/proms/eprom.cpp:40-59`; `git show 3.0.0b35:src/proms/eprom.cpp:40-62`; `.github/scripts/update_version.py:1-120`; `.github/workflows/beta-build.yml:1-379`.
- The wiki clone: all 12 pages listed; `Breaking-Changes.md` in full; `Install-Beta.md` in full; `Home.md`; `_Sidebar.md`; `Testing-Chips.md:28-107`; `git log/show f967398`; `git ls-remote origin`.
- Meta: `.planning/{PROJECT.md:60-130, REQUIREMENTS.md:60-110, ROADMAP.md:175-215,450-470, config.json}`; the 204 and 205 records cited inline; `.planning/notes/999.9-repo-rename-impact-analysis.md:86-92`; `.planning/milestones/v1.4-RELEASE-PROCEDURES.md`; `.claude/gsd-core/workflows/complete-milestone/steps/git-tag.md`.
- Live state: `git ls-remote` (all 4 repos), `gh pr view` (#91/#72/#70), `gh api` (releases), PyPI JSON for `firestarter`.
- Executed probes: scratch dry-runs of both bump scripts, `merge-tree` conflict simulation, the full app suite on 3.11 (bumped and unbumped), and the firmware `tests/` tree (in place and bumped).

### Secondary / Tertiary
- None. No web documentation was needed: every question was answered from the repositories, their CI definitions and live GitHub/PyPI state. The research-plan seam was not used, because this phase has no library or ecosystem question. The knowledge graph (`.planning/graphs/graph.json`, dated 2026-09-18) predates Phases 202–206 and was not queried.

## Metadata

**Confidence breakdown:**
- Version / CI mechanics: HIGH. Executed the publisher's own code, and simulated the merge.
- Compatibility matrix: HIGH for the bench-observed rows (204 and 205). MEDIUM for three code-derived rows (A1–A3).
- Wiki information architecture: MEDIUM. A judgement call (F3/F4/F5), with no oracle.
- Pitfalls: HIGH. Each one was reproduced or read this session.

**Research date:** 2026-09-23
**Valid until:** the next push to `beta` in either sub-repo, or to the wiki. Either changes the published state this relies on. Otherwise 7 days.

**Side effects of this research, disclosed:**
- One `git fetch origin beta main` in `firestarter_fw` updated its remote-tracking refs (`origin/main 00a085a..b21f94a`). No working-tree or branch change.
- Scratch clones, the scratch venv and the uv caches live under `/tmp/claude-1000/`.
- No sub-repo file, wiki file, tag or remote was modified.
