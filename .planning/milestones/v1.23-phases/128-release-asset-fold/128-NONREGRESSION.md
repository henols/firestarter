# Phase 128 Non-Regression Sweep — closing plan (128-10)

**Written:** 2026-08-01
**Firmware branch (`firestarter`):** `v1.23-py32f071-integration` · **HEAD at this sweep:**
`0de57da3c9edfb40f86eee8b0964e0f1bcdd8559`
**Host branch (`firestarter_app`):** `v1.23-py32f071-integration` · **HEAD at this sweep:**
`cc9452f4db9a814ffb221bab767c24db67288365`
**Meta branch:** `gsd/v1.23-py32f071-integration`

> **No PY32F071 hardware exists.** Nothing in this milestone has ever run on this silicon,
> and nothing in it can. Everything below is about **publication**: that a file with a
> particular name, carrying a particular version string, becomes a downloadable release
> asset. Nothing here says the published image runs, boots, or installs. The permitted claim
> is exactly one sentence wide.

**Re-execution pledge.** Every row in §2 was executed in **this session** (Plan 128-10's
Task 1), against the trees exactly as they now stand — nothing is copied from any of this
phase's nine prior plans' (128-01 through 128-09) SUMMARY files. Where a prior SUMMARY made a
claim (an exit code, a test count, a parsed literal), this document re-checked it
independently against the live tree and says so below. §3's rows were written as `PENDING —
operator dispatch` by Task 1 and were replaced by Task 3 with evidence from the two
operator-authorised rehearsal runs, each value re-verified read-only against the GitHub API
(see §4's discharge note for what is and is not re-inspectable after cleanup).

---

## 1. The claim, as precise statements

1. **REL-01 (ordering + carried version).** In `beta-build.yml`'s single job, the ARM build
   step (`id: arm`) sits strictly after the `update_version.py` step (`id: version`) and the
   `stefanzweifel/git-auto-commit-action@v5` auto-commit step, and strictly before `Release` —
   verified this session by parsing the YAML step order. In addition, a mechanical assertion
   (added Plan 128-06) converts the published `.hex` back to a flat binary and greps for the
   literal `"<steps.version.outputs.version>:py32f071"` in its `strings` output — this can only
   be observed on a real ARM build, so it is a §3 row, not a §2 row.
2. **REL-02 (published as a release asset, glob-matched).** `firestarter_py32f071.hex` is
   published by `softprops/action-gh-release@v2`'s `files:` key (a real GitHub release asset,
   not an Actions artifact), matched via the glob `build/py32f071/firestarter_*.hex`. The
   requirement's own stated rationale ("warns on unmatched glob, fails on missing literal") is
   corrected by research F-1: the action makes no glob-vs-literal distinction at all: the only
   invariant that matters is that `fail_on_unmatched_files` is never set to `true`, verified
   this session (§2). Actual publication as an asset can only be observed on a real dispatch
   (§3).
3. **REL-03 (broken ARM build still publishes the three AVR assets, proven).** An unconditional
   `Assert all AVR release assets are present` step runs immediately before `Release` with no
   `if:` guard, so it always runs regardless of whether the contained ARM steps above it
   succeeded. Locally, `scripts/check_release_assets.py` is proven live this session to exit 0
   against a clean fixture and exit 1 against two distinct planted violations (missing hex,
   zero-byte hex). The actual containment cascade on a broken CMake configure — the real proof
   that this holds under a live GitHub Actions run — can only be observed on rehearsal run B
   (§3).
4. **REL-04 (emitted filename == `asset_candidates("py32f071")[0]`, SDK SHA logged).** Three
   independent things must all be true: the CMake-emitted basename equals the frozen host
   contract (proven this session, §2, and by Plan 128-03's non-vacuous guard); the workflow's
   own in-CI transcription check and the SDK-SHA-vs-`GIT_TAG` equality check exist as exit-code
   assertions in `beta-build.yml` (Plan 128-06, verified by YAML parse in prior plans, re-parsed
   this session); and both actually fire correctly on a real ARM build, which is CI-only (§3).
   The SDK SHA is resolved from the measured FetchContent source directory
   `build/py32f071/_deps/py32f071_sdk-src` (research F-5, measured from real CI run
   `30676982030`'s ninja object paths — not guessed), compared against the pinned `GIT_TAG`.
5. **The ceiling, stated as a negative.** None of the above says or implies that the published
   `firestarter_py32f071.hex` runs, boots, or installs on PY32F071 silicon. No PY32F071 PCB
   exists. The asset publishes; that is the whole claim.

---

## 2. Locally provable, executed now

All commands below were run in this session, in `/workspaces/firestarter` unless noted.

| # | Mechanism | Command | Expected | Observed |
|---|-----------|---------|----------|----------|
| 2.1 | REL-01 step-order (mechanical read) | `python3 -c` parsing `.github/workflows/beta-build.yml`'s `jobs.build.steps`, printing the indices of the `version`, `git-auto-commit-action`, `arm` and `Release` steps | strictly increasing indices | `{'version': 10, 'git-auto-commit': 11, 'arm': 13, 'Release': 20}` → **strictly increasing: True** |
| 2.2 | REL-02 `files:` block, parsed | `python3 -c` YAML-parsing the `Release` step's `with.files` | two-entry list, `.pio/build/**/...` and `build/py32f071/...` | `['.pio/build/**/firestarter_*.hex', 'build/py32f071/firestarter_*.hex']` |
| 2.3 | REL-02 `fail_on_unmatched_files` absence, non-vacuous | comment-stripped grep of `.github/workflows/beta-build.yml` for the literal key, plus a length check on the stripped source | key absent; stripped source non-empty (guard is meaningful, not vacuously passing on an empty file) | `fail_on_unmatched_files present in comment-stripped source: False`; stripped source length **6703 chars** (non-empty) |
| 2.4 | REL-03 checker, clean fixture | `python3 scripts/check_release_assets.py --build-root tests/fixtures/clean_release_assets_all_three/pio_build` | exit 0 | `PASS: leonardo(32 bytes), uno(32 bytes), uno328pb(32 bytes) (build_root=tests/fixtures/clean_release_assets_all_three/pio_build)` — **exit 0** |
| 2.5 | REL-03 checker, planted missing-hex | `python3 scripts/check_release_assets.py --build-root tests/fixtures/planted_release_assets_missing_uno328pb/pio_build` | exit 1, names the missing target | `FAIL:\n  uno328pb: missing .../pio_build/uno328pb/firestarter_uno328pb.hex` — **exit 1** |
| 2.6 | REL-03 checker, planted zero-byte-hex | `python3 scripts/check_release_assets.py --build-root tests/fixtures/planted_release_assets_zero_byte_leonardo/pio_build` | exit 1, names the zero-byte target | `FAIL:\n  leonardo: .../pio_build/leonardo/firestarter_leonardo.hex is 0 bytes` — **exit 1** |
| 2.7 | Firmware pytest full suite | `python3 -m pytest tests/ -q` | green, count unchanged by this phase's non-firmware-compiled work | **180 passed** in 9.70s |
| 2.8 | `pio test -e native` | `pio test -e native` | 141 cases / 17 suites, matching the BASE-01/Phase-123 baseline, unchanged | **141 test cases: 141 succeeded**, 17 suites listed |
| 2.9 | `pio test -e native_nodevtools` | `pio test -e native_nodevtools` | 141 cases / 17 suites, unchanged | **141 test cases: 141 succeeded**, 17 suites listed |
| 2.10 | `test_checker_convention.py` with raised floors | `python3 -m pytest tests/test_checker_convention.py -q` | 7 passed (`FLOOR=6`, `FIXTURE_FLOOR=15`) | **7 passed** in 0.04s |
| 2.11 | Recounted `planted_*` total (files + directories, per the checker's own `glob("planted_*")`, not a directory-only count) | `python3 -c` using `Path('tests/fixtures').glob('planted_*')` | == `FIXTURE_FLOOR` (15) | **15** entries (9 log/cpp files across BASE-08's other checkers + 6 directories, including this phase's 2 planted release-assets dirs) |
| 2.12 | `GIT_TAG` parse, real `CMakeLists.txt` | `sed` expression extracting the 40-hex `GIT_TAG` from `platform/py32f071/CMakeLists.txt` | 40-hex SHA | `0ed2f4b4d3391eccfd4491006a30295fd78e32c2` (40 chars) |
| 2.13 | Host cross-repo binding, PASS-not-SKIP | (`/workspaces/firestarter_app`) `python3 -m pytest tests/test_py32_asset_name_host.py -v -rs` | 10 passed, 0 skipped, no `firestarter firmware checkout absent` skip line | **10 passed** in 0.32s, `-rs` report empty of any skip reason |
| 2.14 | Host skip census | (`/workspaces/firestarter_app`) `python3 -m pytest tests/test_skip_census.py -v` | 5 passed, no new `ALLOWED_SKIP_REASONS` entry needed | **5 passed** in 79.03s |
| 2.15 | Host full suite | (`/workspaces/firestarter_app`) `python3 -m pytest tests/ -q` + `--collect-only -q` cross-check | count unchanged since Plan 128-09 (1303) | run completed with all progress lines `.` (zero `F`/`E`/`s` characters), `30 snapshots passed`; `--collect-only -q` per-file sum == **1303**, matching Plan 128-09's recorded count exactly |
| 2.16 | Firmware tree clean | `git -C /workspaces/firestarter status --porcelain` | empty | empty; `HEAD` == `0de57da3c9edfb40f86eee8b0964e0f1bcdd8559` |
| 2.17 | Host tree — only pre-existing, unrelated dirt | `git -C /workspaces/firestarter_app status --porcelain` | `.gitignore` modified + 4 untracked files (none from this phase); `HEAD` == `cc9452f...` | ` M .gitignore`, `?? .coverage`, `?? .planning/config.json`, `?? SECURITY.md`, `?? write_test_port.sh` — matches the plan's stated pre-existing dirt exactly; `HEAD` == `cc9452f4db9a814ffb221bab767c24db67288365` |
| 2.18 | Repo-wide hyphenated-basename grep | `grep -rn "firestarter-py32f071" --include={*.yml,*.txt,*.md,*.cmake} .` (excluding `.git`) | zero matches | grep exit code **1** (no matches) — zero occurrences |

**Section 2 result: every row executed in this session; no cell reads `PENDING`.**

---

## 3. CI-only, discharged by the operator-authorised rehearsal dispatches

Every `Observed` cell below was a placeholder until the operator authorised Task 2's
checkpoint dispatches (§4); Task 3 has replaced each with the returned, independently
re-verified evidence below.

| # | Mechanism | Command / Source | Expected | Observed |
|---|-----------|-------------------|----------|----------|
| 3.1 | Run A URL + head commit SHA | operator-reported, orchestrator-dispatched under explicit operator authorisation | a `https://github.com/henols/firestarter/actions/runs/<digits>` URL + 40-hex SHA | **`https://github.com/henols/firestarter/actions/runs/30722352902`**, head SHA **`7a0a375de7e71ed3e9108b9531fffb59d8d95cd8`**. `conclusion: success` (22/22 steps). Dispatched with `rehearsal=true`, `beta_version=3.0.0b99` against a throwaway branch `rehearsal/128-release-asset-fold`, `event: workflow_dispatch`. |
| 3.2 | Run A asset list (API, names + sizes) | `gh release view <rehearsal-tag> --json assets` — draft id `363647320`, tag `rehearsal-30722352902` | four assets: `firestarter_uno.hex`, `firestarter_uno328pb.hex`, `firestarter_leonardo.hex`, `firestarter_py32f071.hex` | **All four present**: `firestarter_leonardo.hex` 73196 B, `firestarter_py32f071.hex` **77284 B**, `firestarter_uno.hex` 67395 B, `firestarter_uno328pb.hex` 67534 B. Cited by run `30722352902` + SHA `7a0a375`. Draft since deleted (§4 cleanup) — this transcript and the run URL are the durable record; the release page cannot be re-inspected. |
| 3.3 | Run A resolved SDK SHA (step summary) | run A's `$GITHUB_STEP_SUMMARY` | `0ed2f4b4d3391eccfd4491006a30295fd78e32c2` (equal to the pinned `GIT_TAG`, §2.12) | Step-summary line: *"Resolved SDK commit SHA: 0ed2f4b4d3391eccfd4491006a30295fd78e32c2 (matches declared GIT_TAG -- pin honoured)"* — **equal to §2.12's pinned value**. |
| 3.4 | Run A resolved `rehearsal` boolean | run A's `mode` step log / step summary | `true` | Step-summary line: *"Resolved rehearsal mode: true"*. |
| 3.5 | Run A REL-01 image-carries-version PASS line | run A's `Assert the py32 image carries the bumped VERSION (REL-01)` step log | PASS, naming `3.0.0b99:py32f071` | *"PASS: image contains version string 3.0.0b99:py32f071"* — step 19, `success`, strictly after step 13 (`git-auto-commit-action@v5`, success) and step 15 (ARM build, success), confirming the §2.1 ordering held on a real dispatch, not just on paper. |
| 3.6 | Run A: draft created no git tag | post-cleanup tag-ref enumeration (equivalent to `gh api .../git/refs/tags/rehearsal-*`) | no tag created | Confirmed post-cleanup: `rehearsal-*` tag refs = **0**, `3.0.0b99` tag refs = **0**. F-3 empirically confirmed, not just cited. |
| 3.7 | Run B URL + head commit SHA | operator-reported, orchestrator-dispatched under explicit operator authorisation | a second, distinct run URL + 40-hex SHA | **`https://github.com/henols/firestarter/actions/runs/30722537152`**, head SHA **`6c1c31ff4bc3fa540cfba8ab0706549421f479d1`** (= `7a0a375` + the throwaway planted break + the workflow's own version-bump auto-commit). `conclusion: success` — the job did not fail; the ARM failure was contained. |
| 3.8 | Run B asset list (API, names + sizes) | `gh release view <rehearsal-tag> --json assets` — draft id `363648361`, tag `rehearsal-30722537152` | exactly three AVR hexes, **no** `firestarter_py32f071.hex` | **Exactly three**: `firestarter_leonardo.hex` 73196 B, `firestarter_uno.hex` 67395 B, `firestarter_uno328pb.hex` 67534 B. **No** `firestarter_py32f071.hex` present. Draft since deleted — run URL + this transcript are the durable record. |
| 3.9 | Run B `::warning::` annotation + step-summary line (D-07 firing) | run B's check-runs annotations API + step summary | `::warning::` present; step summary contains *"PY32F071 image not produced — this release carries no py32f071 asset."* | **Confirmed via the check-runs annotations API**: `warning: "PY32F071 image not produced — this release carries no py32f071 asset."` and `failure: "Process completed with exit code 1."` (the contained ARM step's real failure, keyed on `outcome`, not `conclusion`). Step order: step 15 (ARM build) `conclusion=success` but `outcome=failure`; step 16 ("Report a missing PY32F071 image", keyed on `outcome`) **ran** (it was `skipped` on run A); steps 17–19 (the three REL-01/REL-04 assertions, guarded `if: steps.arm.outcome == 'success'`) **skipped**; step 21 (AVR-assets assertion, unconditional) **success**; step 22 (Release) **success**. Step summary also carries *"Resolved rehearsal mode: true"* and *"PASS: leonardo(73196 bytes), uno(67395 bytes), uno328pb(67534 bytes)"*. |

**Section 3 result: every cell discharged with a run URL, a commit SHA, and an independently-legible log/API excerpt. Both draft releases (`363647320`, `363648361`) are deleted; the run URLs and this transcript are the only re-inspectable record — the release pages themselves no longer show these assets.**

---

## 4. The operator dispatch procedure

This procedure is written for the **operator only**. No task in this plan executes any of the
commands below; they are instructions to a human. `beta_version` must be supplied on every
dispatch — see step 2's consequence if it is omitted.

1. **Push a throwaway branch.** From `/workspaces/firestarter` on `v1.23-py32f071-integration`,
   create a new branch and push it to `origin` (any name distinct from `beta`/`main` works,
   e.g. `rehearsal-128-10`). Verified this session and in prior phases: pushing a branch that
   is neither `beta` nor `main` fires **nothing** in this repo —
   `beta-build.yml` is `push: [beta]` + `workflow_dispatch`, `py32f071.yml` is `push: [beta]` +
   `pull_request` + `workflow_dispatch`, `build.yml` is `push: [main]` + `pull_request: [main]`.
   The push itself is safe; only the two dispatches below are gated actions.

2. **Run A (healthy).** Dispatch `beta-build.yml` (`gh workflow run beta-build.yml --ref
   rehearsal-128-10 -f rehearsal=true -f beta_version=3.0.0b99`) with **`rehearsal=true`** and
   **`beta_version=3.0.0b99`**. The second input is not optional: `update_version.py`'s
   `is_beta_mode()` returns `True` only when `--beta` is passed, `GITHUB_REF ==
   refs/heads/beta`, or `BETA_VERSION` is a non-empty string (research F-2). A throwaway-branch
   dispatch with `beta_version` left blank satisfies none of the three, so it silently takes
   the **stable** path and rewrites `include/version.h` from `3.0.0b14` to `3.0.1` — and the
   evidence collected would then record a stable version string as proof of a beta fold, which
   is not what REL-01 asks for. `3.0.0b99` is unmistakable, passes the beta version regex, and
   cannot collide with a real future `b15`. **Grep anchor for the wrong path:** if the version
   step's log shows a plain `3.0.1`-shaped string (no `bNN`/`rcNN` suffix) rather than
   `3.0.0b99`, the dispatch took the stable path — stop and re-dispatch with the input supplied
   correctly rather than proceeding.

3. **Flag A4 before the first dispatch.** GitHub resolves the workflow *definition* — including
   the `rehearsal` input, which did not exist before this phase — from the **dispatched ref**,
   not from the default branch. Precedent run `30199560282` proves dispatching from a
   non-default branch works at all, but that run's workflow definition had no *new* input. If
   `gh workflow run` (or the GitHub UI) rejects the dispatch with an unexpected-input or
   unrecognized-input error, **stop and report** rather than working around it — that is
   assumption A4 failing loudly, and it needs an operator/planner decision, not an improvised
   fix.

4. **Collect run A's evidence.** Record the run URL and the head commit SHA. Then run
   `gh release view <the rehearsal-...-tag> --json assets` and record asset **names and
   sizes** — **not** download URLs, since a draft release's asset URLs are `untagged-<hash>`
   placeholders and are not stable citations (research F-3). From the run's step summary,
   confirm: the resolved `rehearsal` boolean reads `true`; the SDK SHA line is present and
   equals the pinned `GIT_TAG` (`0ed2f4b4d3391eccfd4491006a30295fd78e32c2`); and the REL-01
   PASS line names `3.0.0b99:py32f071`. Confirm no tag was created (a draft release creates no
   git tag — `finalizeRelease()`'s early return on `draft: true`, corroborated by the action's
   own `untagged-...` comment and issue #722; D-01's ⚠ VERIFY item, RESOLVED by research F-3).

5. **Run B (planted break).** On the same throwaway branch, commit a change to
   `platform/py32f071/CMakeLists.txt`'s source list that renames one referenced source path so
   **CMake configure** fails — reproducing C-1, the real historical failure this exact target
   had in Phase 124 (a stale hyphenated-name reference caught the same way). Dispatch again
   with the same two inputs (`rehearsal=true`, `beta_version=3.0.0b99`). Collect the run URL,
   the head SHA, the asset list, and a textual (not screenshot) confirmation that the
   `::warning::` annotation and the step-summary line *"PY32F071 image not produced — this
   release carries no py32f071 asset."* both appeared.

6. **Cleanup.** Delete the draft release and delete the throwaway branch. Confirm no tag named
   `rehearsal-*` exists, and that `3.0.0b99` exists neither as a tag nor as a release anywhere
   in the repo.

7. **Two failure signatures to watch for, so a wrong result is recognised rather than absorbed
   as success:**
   - A run B that is **green**, publishes **three AVR assets**, and shows **no** `::warning::`
     annotation and no step-summary line is a **passing REL-03 and a failing D-07 simultaneously**
     — report this rather than accepting it as a clean pass.
   - A `draft` value that resolves `true` on anything **other than** a rehearsal dispatch (e.g.
     a real `beta` push) would silently stop publishing real public betas — if this is ever
     observed on a non-rehearsal run, it is a severe regression, not a rehearsal artifact.

**DISCHARGED.** The procedure above was executed under explicit operator authorisation, and
§3 now carries the resulting evidence: both run URLs, both head commit SHAs, both asset lists
(names + sizes), the resolved SDK SHA, the resolved rehearsal boolean, and the D-07 warning's
presence on run B / absence on run A. Each value was re-verified read-only via `gh api` GETs
against the runs, the release assets, the check-run annotations, and the tag/branch refs.

Both rehearsal releases were **drafts and have since been deleted**, so a reader cannot
re-inspect the asset lists on the release page today. The run URLs in §3 and the values
recorded here are the durable record. Verified after cleanup: zero draft releases, zero
`rehearsal-*` tag refs, zero `3.0.0b99` tag refs, zero rehearsal branch refs, and the newest
real release still `3.0.0b14` — no public beta was created by either run.

### 4a. Procedure defect discovered during dispatch (deviation — recorded for Phase 130)

**Step 5 of this procedure, as written, is unusable and must not be reused as-is.** It
prescribes breaking Run B by renaming a source path inside
`platform/py32f071/CMakeLists.txt`'s source list, on the theory that this reproduces C-1 (a
broken CMake **configure**). It does not do what the procedure needs.

Verified locally before dispatch: planting that exact rename trips Phase 123's CMake
manifest-drift gate, `tests/test_check_cmake_manifest.py::test_armed_and_passing_on_the_real_tree`,
which runs inside `pytest tests/` — `beta-build.yml` step 11, **"Run update_version.py
tests"**, a step with **no `continue-on-error`**. Result observed locally: `1 failed, 179
passed`. Had this been dispatched, the job would have failed at step 11, **before** the ARM
build step ever ran, publishing **nothing at all** — the exact opposite of what REL-03 needs
demonstrated (that a broken ARM build still publishes the three AVR assets). A hard pytest
failure this early is not a "contained ARM break"; it is a whole-job failure.

**Substituted break, used instead for the actual Run B dispatch:** a compile error inserted
into `platform/py32f071/src/timing.cpp` (an undeclared identifier), which is compiled **only**
by the ARM-only PY32F071 target — not by any PlatformIO env (`uno`, `leonardo`, `uno328pb`)
and not by either native pytest suite. Verified locally before dispatch: with this break
applied, `python3 -m pytest tests/ -q` still reports **180 passed** (same count as §2.7,
unaffected), and `pio test -e native` / `pio test -e native_nodevtools` are likewise
unaffected — none of them touch `platform/py32f071/src/`. This break is contained by
construction to the ARM leg, which is what actually let Run B demonstrate the containment
cascade (§3.7–§3.9).

**This is a planning-procedure defect, not an execution error**, and belongs in Phase 130's
CLOSE-02 honesty ledger: the phase's own validation procedure, as written in this plan, could
not have produced the evidence it asked for. The evidence in §3 for Run B was obtained via a
different, but strictly-more-precisely-targeted, planted break than §4 step 5 specifies.

---

## 5. What this phase does NOT claim

- **The published image has never been executed. No PY32F071 PCB exists.** The permitted claim
  ceiling is exactly one sentence wide: the asset publishes; that is the whole claim. Nothing in
  this phase, in any of its nine prior plans, or in this artifact says or implies the image
  runs, boots, or installs.
- **The cross-repo filename binding is enforced by a local run and by developer discipline, not
  by app CI.** Neither `firestarter_app` CI workflow (`ci.yml`, `beta-release.yml`) checks out
  the firmware sibling repository — both `actions/checkout@v4` steps in both files are plain
  single-repo checkouts with no `repository:`/`path:` arguments (verified by grep, Plan 128-09).
  With no `../firestarter/.git` marker present in that environment, `tests/fw_presence.py`'s
  `FW_REPO_PRESENT` is `False` at import, and all six `@requires_fw` legs of
  `test_py32_asset_name_host.py` SKIP there; only the four unmarked RED demonstrations
  (`TestPy32AssetNameFailsClosedOnBadInput`) actually run in app CI. This is a pre-existing,
  accepted property (Phase 127 D-14 landed the same shape), not something this phase fixes.
  **Claiming CI enforcement would be false.**
- **The `continue-on-error` on the ARM call site in `beta-build.yml` is deliberate and
  permanent for now**, with a recorded removal trigger (D-05): it comes off when the PY32F071
  target is validated on real silicon. No PCB exists, so this trigger is unreachable this
  milestone, and the flag stays. This is a decision, not an oversight.
- **No ARM number anywhere in this phase was measured locally.** There is no `arm-none-eabi-gcc`
  / `cmake` / `ninja` toolchain in this devcontainer, so no local ARM build or measurement is
  possible. Every ARM figure in this phase — flash/RAM figures, the resolved SDK SHA, the
  version-string proof, the asset lists — cites a CI workflow run URL plus a commit SHA. A
  local `pio` run is never evidence about ARM.

---

## 6. Precedent and prior art

On **2026-07-26**, run
[`30199560282`](https://github.com/henols/firestarter/actions/runs/30199560282) dispatched
`beta-build.yml` (`workflow_dispatch`) from the **non-default branch**
`v1.21-community-chip-validation-command`. Two minutes later (2026-07-26T11:10:01Z) it
published the **real, public** prerelease `3.0.0b11` with a **real git tag**:
`refs/tags/3.0.0b11` → `0fd7992187467f6d245bc106786253f497ea0ecc`. That commit is contained in
`origin/beta`, `origin/v1.21-community-chip-validation-command` and
`origin/v1.23-py32f071-integration`.

D-01's draft-mode containment is not theoretical caution — **the exact accident it prevents has
already happened once, from precisely this route** (dispatching this workflow from a
non-default branch). Two things follow from this precedent:

1. **The mechanism D-01 needs is proven to work.** The "a `workflow_dispatch` workflow must
   live on the default branch" folklore does not block dispatching from a throwaway branch —
   `gh` is authenticated with `repo` + `workflow` scopes, and GitHub resolves the workflow
   *definition* (including any input new on that ref) from the dispatched ref itself.
2. **D-03's permanent `rehearsal-${{ github.run_id }}` tag override is justified by this
   precedent, not by hypothetical caution.** Without draft mode and the tag override, a
   rehearsal dispatch of this exact workflow, from this exact non-default-branch route, is
   proven capable of publishing a real public prerelease with a real tag — because it already
   did, once, before draft mode existed.

This belongs in Phase 130's CLOSE-02 honesty ledger alongside the two other stray prereleases
already recorded there (the v1.22-era `3.0.0b12` pair) as the strongest available justification
for why the `rehearsal` input is permanent (D-03) rather than removable once this phase closes.

---

## 7. Criterion discharge

Each ROADMAP success criterion is mapped below to the specific, named row(s) of evidence that
discharge it — not to an overall impression of the phase.

**Criterion 1** (ARM build ordered strictly after the `update_version.py` auto-commit, so the
published image carries the release `VERSION`):
- §2.1 — mechanical YAML step-order read: `{'version': 10, 'git-auto-commit': 11, 'arm': 13,
  'Release': 20}`, strictly increasing. This discharges the criterion's *stated* method
  (reading the YAML step order).
- §3.5 — Run A's REL-01 PASS line, *"PASS: image contains version string
  3.0.0b99:py32f071"*, observed on a real dispatch (run `30722352902`, SHA `7a0a375`) after
  the auto-commit step (13) and the ARM build step (15) both ran. The mechanical assertion,
  added alongside the YAML read rather than instead of it, is the form that survives a future
  step reorder — the YAML read alone would not catch a reorder that kept the same *set* of
  steps in a different sequence with a stale cached image.
- **Fully discharged.**

**Criterion 2** (`firestarter_py32f071.hex` published as a GitHub release asset, matched by
glob):
- §2.2 — the `files:` glob entry `build/py32f071/firestarter_*.hex` parsed from the workflow
  source.
- §3.2 — Run A's asset list contains `firestarter_py32f071.hex` (77284 B) as a real GitHub
  release asset (not an Actions artifact), cited by run `30722352902` + SHA `7a0a375`. The
  draft (id `363647320`) is deleted; this transcript and the run URL are the durable citation —
  the release page is no longer inspectable.
- **Fully discharged.**

**Criterion 3** (a deliberately-broken ARM build still publishes all three AVR assets, via an
assertion step proven to demonstrably fail if any AVR asset is missing) — **two distinct
halves, backed by two distinct evidence sources; stated separately rather than conflated:**
- *Half A — "still publishes all three AVR assets under a broken ARM build, unconditionally":*
  discharged by §3.7–§3.9. Run B's ARM step (15) had `outcome=failure` while `conclusion:
  success` (contained, `continue-on-error`); the AVR-assets assertion (step 21, no `if:`
  guard) ran and succeeded regardless; the release (step 22) published exactly the three AVR
  hexes and no py32 asset. This is CI evidence, on a real dispatch, run `30722537152`, SHA
  `6c1c31f`.
- *Half B — "the assertion step demonstrably fails the build if any AVR asset is missing":*
  discharged **only by §2.5 and §2.6** (`check_release_assets.py` exiting 1 against the
  `planted_release_assets_missing_uno328pb` and `planted_release_assets_zero_byte_leonardo`
  fixtures) — **local, subprocess-level evidence, not CI evidence.** Run B's planted break
  (§4a) was deliberately scoped to the ARM leg only, so it never exercised an AVR-missing
  scenario in CI; **no CI run in this phase ever observed the AVR-assets step actually fail.**
  The assertion step in `beta-build.yml` invokes the same script proven to fail in §2.5/§2.6,
  so the local proof is legitimate evidence about the step's behavior, but it is evidence about
  the *script*, not about *that step running inside a real GitHub Actions job*. Do not read
  Half B as CI-verified — it is not.
- **Discharged as combined evidence, with the seam stated explicitly above.**

**Criterion 4** (CI logs the resolved SDK SHA and asserts the emitted filename matches
`asset_candidates("py32f071")[0]`, mechanically, not by a human read of the release page):
- §3.3 — Run A's resolved SDK SHA (`0ed2f4b4d3391eccfd4491006a30295fd78e32c2`) equals the
  pinned `GIT_TAG` parsed in §2.12 from the shipped `CMakeLists.txt`.
- §3.1 (run A's step 17, "Assert the emitted asset filename (REL-04): success") and step 18
  ("Assert and log the resolved SDK commit SHA (REL-04): success") — both mechanical,
  exit-code assertions inside the workflow, not a human read of the release page.
- §2.13 — the host-side cross-repo three-way filename binding, 10 passed, 0 skipped, no
  `firestarter firmware checkout absent` skip line — proving the binding holds locally between
  the two repos, independent of the CI dispatch.
- **Restating the ceiling (F-8), so this criterion is not overclaimed:** neither app CI
  workflow checks out the firmware sibling, so all six `@requires_fw` legs of
  `test_py32_asset_name_host.py` SKIP in app CI (§5). §2.13's 10-passed result is a **local**
  run, not an app-CI-enforced one. The cross-repo binding is enforced by local runs and
  developer discipline, not by CI in either repo — say so rather than implying otherwise.
- **Fully discharged for the mechanical CI assertions and the SDK-SHA equality; the cross-repo
  binding half is local-only, as F-8 already states.**

---

## 8. Deviations recorded during Task 3 (2026-08-01)

Three deviations were found while recording the rehearsal evidence. All three are documented
here for Phase 130's honesty ledger; none required an architectural change or blocked
discharge of any requirement.

**1. Procedure defect in this plan's own §4 step 5 (see §4a above for the full account).** The
prescribed CMake-source-rename break for Run B is unusable — it trips Phase 123's CMake
manifest-drift gate at a `pytest tests/` step with no `continue-on-error`, which would fail
the whole job before the ARM build ever ran, disproving REL-03 rather than proving it.
Verified locally (`1 failed, 179 passed`) before dispatch. A compile error in
`platform/py32f071/src/timing.cpp` was substituted instead — an ARM-only translation unit,
verified not to touch either PlatformIO env or either native pytest suite (180/180 local tests
still pass with it applied). Flagged for Phase 130 as a planning-procedure defect: the plan's
own validation procedure could not have produced the evidence it asked for.

**2. A false, unobserved claim was found and fixed before dispatch.**
`firestarter/.github/workflows/beta-build.yml:50` carried the sentence "Confirmed by
observation on rehearsal run A (Plan 128-10)", shipped in firmware commit `45d2bce` (Plan
128-05) — a commit that landed **before** run A existed, so the claim was unobserved at the
moment it was committed. Fixed on the milestone branch in firmware commit `7a0a375`
("docs(128-05): drop the unobserved 'confirmed by observation' claim"), replacing it with a
pointer to the step-summary line the step actually emits on every run. The underlying property
this comment described **has now been observed** on run A (§3.3–§3.5) — the defect was the
premature claim, not the property itself, which is true.

**3. Firmware HEAD moved.** As a direct consequence of fix #2, the firmware HEAD used for this
sweep is `7a0a375de7e71ed3e9108b9531fffb59d8d95cd8`, not `0de57da3c9edfb40f86eee8b0964e0f1bcdd8559`
as recorded in this file's header (written at Task 1, before fix #2 landed) and in the 128-08
and 128-09 SUMMARYs. Both rehearsal dispatches descend from `7a0a375`: Run A was dispatched
directly from it; Run B's head SHA `6c1c31f` is `7a0a375` plus the throwaway planted break (see
deviation 1) plus the workflow's own `update_version.py` auto-commit. The working tree at
`7a0a375` is clean; the planted break used for Run B never landed on the milestone branch
itself — it existed only on the deleted throwaway branch `rehearsal/128-release-asset-fold`.
