# Phase 128: Release-Asset Fold - Context

**Gathered:** 2026-08-01
**Status:** Ready for planning — ROADMAP flags this phase **research-skip**. That flag is *plausible*
here (the fold is spelled out in `platform/py32f071/README.md` and both corrections are already
pinned), but Phases 121, 122 and 127 each ran research despite a skip flag and each time it
overturned locked content. Three load-bearing mechanical facts in this document are **unverified
assumptions**, flagged inline as **⚠ VERIFY** — if any is wrong, D-01 and D-07 change shape.

> **This phase is primarily in `firestarter`, with one deliberate commit in `firestarter_app`.**
> D-08 makes it dual-repo. Both commits land on the respective `v1.23-py32f071-integration`
> milestone branches.

> **Depends on Phase 124** (the ARM target must configure before it is worth folding) and
> **Phase 127** (the `asset_candidates()` filename contract this phase's output must match —
> verified live: `asset_candidates("py32f071")[0] == "firestarter_py32f071.hex"`,
> `firestarter_app/firestarter/firmware.py:129-131`).

<domain>
## Phase Boundary

`beta-build.yml` in the `firestarter` repo grows an ARM build **after** the `update_version.py`
auto-commit and **in the same job**, publishing `firestarter_py32f071.hex` as a real GitHub
**release asset** via a glob — and a broken ARM build can never stop the three AVR `.hex` assets
from publishing.

1. **REL-01** — ARM steps strictly after `update_version.py` + the git-auto-commit step, same job,
   so the image carries the release `VERSION` the host's update decision compares against the tag.
2. **REL-02** — `firestarter_py32f071.hex` published as a release **asset**, matched by a **glob**
   (`softprops/action-gh-release` *warns* on an unmatched glob but *fails* on a missing literal).
3. **REL-03** — a deliberately-broken ARM build still publishes all three AVR assets, **proven**,
   with an AVR-assets-present assertion before the `Release` step.
4. **REL-04** — CI asserts the emitted filename equals `asset_candidates("py32f071")[0]`, and logs
   the resolved SDK commit SHA.

Plus two deliberate in-scope additions with no REL id:
- **D-06** — a composite action so the cmake invocation exists in exactly one place.
- **D-08 (app repo)** — the cross-repo test that actually binds the firmware's emitted name to the
  host function. The workflow-side check alone is a transcription; this is the binding.

**Explicitly NOT in this phase:**
- **Any push to `beta`, any tag, any published (non-draft) release, any public comment — Phase 130.**
  D-01's rehearsal is explicitly designed to leave *no* public footprint precisely so it does not
  pre-empt 130's release decision.
- Folding the ARM build into `build.yml` (stable / `main`) — **D-13**, out of scope with a recorded
  graduation trigger.
- Release-note *content* — the report step writes to `$GITHUB_STEP_SUMMARY` and an annotation, not
  to the release body (rejected twice during discussion; Phase 130 owns release-facing prose).
- The three-tier flash path, `BOOTLOADER` sizing, VID/PID, BOOT0/nBOOT1, SWD pads — **Phase 129**.
- Any host-side change beyond D-08's single test. `asset_candidates()` itself is **frozen** — 127's
  `<code_context>` flags loudly that changing it changes this phase's contract. It must not change.
- **Any claim that the published image runs, boots, or installs.** No PY32F071 PCB exists. The
  permitted ceiling here is narrow and specific: *the asset publishes*. Not *the asset works*.

</domain>

<decisions>
## Implementation Decisions

### Release evidence route — how Criteria 2 & 3 are discharged without cutting a beta

`beta-build.yml` **is** the workflow that cuts beta prereleases, and two stray prereleases from
prior accidents are already public. Criteria 2 and 3 both require it to actually *run*.

- **D-01:** `beta-build.yml` gains a **permanent `rehearsal` `workflow_dispatch` input** that sets
  `draft: true` on the `Release` step. The operator dispatches it from a **throwaway branch** forked
  off the firmware milestone branch. The intended footprint is one Actions run, one deletable draft
  release, and one version-bump auto-commit on a deletable branch.
  **⚠ VERIFY (load-bearing, unverified):** the containment rests on *`softprops/action-gh-release`
  creating no git tag for a draft release*. This is standard GitHub behaviour (a draft release's tag
  is created at publish time), but it was **asserted during discussion, not measured**. Confirm it
  against the action's source or docs **before** the first dispatch. If a tag *is* created, D-01
  needs a distinct throwaway `tag_name` on the milestone branch — which D-03 already supplies, so
  the fix is small, but it must be known in advance rather than discovered on a real repo.
  Rejected: a temporary `beta-build-rehearsal.yml` copy deleted at close (the thing proven is a
  *copy* of the thing shipped, and a divergence between them is exactly the bug class this criterion
  exists to catch); rejected: a real dispatch accepting a third stray public prerelease (truest
  evidence, but it pre-empts Phase 130's release decision and adds a real tag); rejected: deferring
  publication evidence to Phase 130 (Criterion 2 goes undischarged, and a wrong fold surfaces during
  the one release you least want to redo).

- **D-02:** Criterion 3's planted violation is a **commit on the throwaway branch**, not a workflow
  input. **Two dispatches off the same branch:** run A healthy (py32 asset present, three AVR assets
  present), run B after a commit that **breaks CMake configure** — a renamed source path, which is
  the historically real failure in this exact target (**C-1**, Phase 124). The cascade is the proof:
  Configure fails → contained → Build fails → contained → the glob matches nothing → the three AVR
  assets still publish. That exercises every ARM step's containment, on the real workflow.
  Rejected: a `break_arm` dispatch input (a permanent sabotage switch on the production release
  workflow); rejected: one healthy run plus a YAML read (the containment is then never observed —
  the "asserted, not proven" shape this milestone's ledger exists to catch).

- **D-03:** The `rehearsal` input **stays permanently**, and in that mode the `Release` step's
  `tag_name` is overridden to something unmistakable — `rehearsal-${{ github.run_id }}`. The version
  bump still runs and still compiles into the image, so **REL-01 stays proven by the rehearsal**;
  what changes is only the name the draft carries, so an accidentally-published draft cannot
  masquerade as `3.0.0b15`.
  Rejected: letting the draft carry the computed version (a draft sitting in the release list
  looking exactly like the next real beta); rejected: deleting the input at close (the next person
  to change this job then has no way to rehearse, and will test on `beta`).

- **D-04 (carry-forward, not re-asked):** The push and both dispatches are **outward-facing actions
  requiring an explicit operator gate at execute time**. No task in any plan may run `git push` or
  `gh workflow run`; the plan carrying them is `autonomous: false`; and **the structural separation
  is the gate, not the checkpoint type** — `--auto`/`--chain` auto-approve human-verify checkpoints
  regardless. Identical shape to 124 D-08/D-09, 125 D-13, 126's CFG evidence plan and 127 D-01.
  **Verified this session:** pushing a branch that is neither `beta` nor `main` fires **nothing** in
  the firmware repo — `beta-build.yml` is `push: [beta]` + dispatch, `py32f071.yml` is `push: [beta]`
  + PR + dispatch, `build.yml` is `push: [main]` + `pull_request: [main]`. The throwaway branch push
  is safe; only the two dispatches are gated actions.

### Double ARM build and failure containment — resolving what 124 D-10 punted here

- **D-05:** **Both ARM builds stay, with distinct roles.** `py32f071.yml` (its `push: branches:
  [beta]` trigger added by 124 MERGE-03) remains the **LOUD** gate — no `continue-on-error`, red and
  staying red when ARM breaks on `beta`. `beta-build.yml`'s ARM steps are the **SOFT** copy —
  `continue-on-error: true`, existing only to produce the asset, never able to block AVR.
  **This pairing is what makes `continue-on-error` defensible:** the containment that hides the
  failure from the release exists alongside a separate workflow whose entire purpose is to not hide
  it. Neither half is sound alone.
  Rejected: dropping `push: beta` from `py32f071.yml` (one build, but a broken ARM build on `beta`
  becomes fully silent — green release, missing asset, nobody notified); rejected: removing
  `continue-on-error` from both (honest and loud, but it directly contradicts REL-03 — a broken ARM
  build would block all three AVR assets, the exact failure the requirement forbids).
  **`continue-on-error` removal trigger, recorded:** it comes off when the target is validated on
  real silicon. No PCB exists, so it is unreachable this milestone and the flag stays. Record the
  trigger so its persistence reads as a decision, not an oversight.

- **D-06:** The cmake invocation lives in **exactly one place** — a composite action at
  `.github/actions/build-py32f071/action.yml` holding toolchain install + configure + build, called
  by both workflows. **A composite action runs *in* the calling job**, so REL-01's "same job, after
  the version bump" still holds. A reusable `workflow_call` workflow would **not** — it is a
  separate job with a separate checkout and would break REL-01 outright. `continue-on-error: true`
  goes on the **call site in `beta-build.yml` only**, so D-05's loud/soft split survives intact.
  This eliminates the drift class rather than detecting it.
  **New pattern:** no `.github/actions/` directory exists in this repo today.
  Rejected: duplicated steps plus a `scripts/check_py32_build_parity.py` drift checker (matches the
  repo's checker-with-fixture house style, but detects drift after it is written instead of making
  it impossible, and adds a fifth checker); rejected: duplication with cross-reference comments (the
  only thing stopping drift is that someone reads the comment — and the `beta-build.yml` copy is
  `continue-on-error`, so drift there fails *silently* by construction).

- **D-07:** A soft ARM failure is **surfaced, not swallowed**. One step after the ARM call reads its
  outcome and, on failure, emits a `::warning::` annotation **and** a line in
  `$GITHUB_STEP_SUMMARY`: *"PY32F071 image not produced — this release carries no py32f071 asset."*
  It fails nothing. `py32f071.yml`'s red run says **what broke**; this says **what the release
  lacks** — and the release run page is the artifact anyone actually looks at.
  **⚠ VERIFY (mechanical, load-bearing):** the step must read **`steps.<id>.outcome`**, not
  `conclusion`. For a `continue-on-error` step GitHub sets `outcome: failure` but
  `conclusion: success` — reading `conclusion` produces a report that can never fire, i.e. exactly
  the hollow gate this project has had to unwind in Phases 118 and 124. Confirm the semantics before
  writing the condition. (`if: always()` is belt-and-braces here: `continue-on-error` keeps the job
  on the success path, so a plain step already runs. Planner's call.)
  Rejected: relying on `py32f071.yml`'s red alone (the two runs are correlated only by timestamp);
  rejected: also appending to the release body (outside REL-01…REL-04, adjacent to Phase 130).

### The filename contract (REL-04) — where the binding actually lives

The firmware repo's CI cannot import the host package, so Criterion 4's *"mechanical string-equality
check in the workflow"* can only ever compare against a transcription.

- **D-08:** Both halves are built, and **this makes Phase 128 dual-repo**.
  (a) **Firmware side:** the workflow performs a real string-equality check of the emitted basename
  against a literal, with a comment citing `asset_candidates()`. This satisfies Criterion 4 as
  written.
  (b) **App side (`firestarter_app`):** a test that reads the firmware sibling and asserts the name
  equals `asset_candidates("py32f071")[0]`. This is the actual binding. It is the **exact sibling**
  of the test 127 already landed for the flash map — `firestarter_app/tests/test_py32_flash_map_host.py`
  — so copy that module's shape rather than inventing one.
  Rejected: `pip install firestarter` inside the release job (truest equality — the real function,
  not a transcription — but the firmware *release* job would gain a PyPI network dependency on the
  host package, the installed version lags `beta` by a release, and a host-side change could break
  the firmware release); rejected: firmware-only literal with the binding deferred (nothing
  mechanically connects the repos; the failure mode — host renames the asset, firmware keeps
  emitting the old name — is precisely what Criterion 4 exists to catch).

- **D-09:** The app-side test is a **three-way** equality: the name extracted from
  `firestarter/platform/py32f071/CMakeLists.txt` (what is actually emitted), the expected literal
  extracted from the firmware workflow (the independent transcription), and
  `asset_candidates("py32f071")[0]` — **all three equal, with a separate non-vacuity assertion per
  parse** so a rename that makes a regex miss fails loudly instead of passing on two empty strings.
  **A-7 is the in-milestone counter-example** — a firmware rename flipped five gate legs PASS→SKIP
  at exit 0 with a false "firmware absent" reason, and moving firmware files is this milestone's
  premise. Bind through `firestarter_app/tests/fw_presence.py`'s `@requires_fw`.
  **Resolved, do not re-derive:** `FW_ABSENT_REASON` is **already** entry 1 in
  `ALLOWED_SKIP_REASONS` and is *imported*, not re-typed — **no new skip-census entry is needed**
  (127 D-14 settled this).
  Rejected: parsing CMake only (the workflow literal is then unbound and could rot to a stale name,
  failing every release with nothing explaining why); rejected: parsing the workflow only (a CMake
  rename is then caught only when a release actually runs — the least convenient moment).

- **D-10:** REL-04's SDK SHA is **logged AND asserted**. `git -C <fetchcontent-src> rev-parse HEAD`,
  echoed to the step summary, and asserted string-equal to the `GIT_TAG` read out of
  `platform/py32f071/CMakeLists.txt`. **Verified live:** the SDK is *already* pinned —
  `GIT_TAG 0ed2f4b4d3391eccfd4491006a30295fd78e32c2` — so this is not a new pin, it is a per-release
  proof that the pin was honoured, catching a cache or mirror serving something else. Consistent
  with the standing operator preference for an exit code over a human reading output (123-CONTEXT).
  **⚠ VERIFY:** the FetchContent source path is *expected* to be
  `build/py32f071/_deps/py32f071_sdk-src` (CMake's default `<binary_dir>/_deps/<name>-src`), but
  this has **not** been observed in a real run — no ARM toolchain exists in this devcontainer.
  Read it off run A's log rather than hardcoding a guess.
  Rejected: log only (a divergence written to a log nobody reads until already debugging a bad
  image); rejected: also recording it in the release body (outside REL-01…REL-04).

### The AVR-assets assertion (REL-03)

- **D-11:** A checker in the repo's established shape: **`scripts/check_release_assets.py`**, with
  **`tests/test_check_release_assets.py`** and a **`tests/fixtures/planted_release_assets_*`** tree
  proving non-zero exit. This is **not optional** — BASE-08's `tests/test_checker_convention.py`
  globs `scripts/check_*.py` non-recursively and *requires* the
  `check_X.py` ↔ `test_check_X.py` ↔ `planted_X*` triple with a hardcoded floor. The workflow calls
  the script; the script is provable locally without CI, and it is an exit code.
  Rejected: three inline `test -s` lines in the YAML (smallest diff, but unprovable outside a
  dispatch — and *"demonstrably fails"* is the requirement's own wording); rejected: one
  do-everything checker also owning the filename equality and the SDK pin (it would bundle a gate
  that must **hard**-fail, AVR missing, with one that must **tolerate absence**, the py32 image when
  the ARM build is contained — forcing internal severity logic into a script whose whole value is
  that it is unambiguous).

- **D-12:** The required set is **derived from `scripts/baseline/size_baseline.json`'s `avr_targets`
  keys** — read the keys, require `firestarter_<key>.hex` present and non-empty under `.pio/build/`
  for each, assert **exactly** that set with nothing missing, and **fail if the key set parses
  empty** (non-vacuity — A-7's lesson again). **Verified live:** that file's `avr_targets` is keyed
  exactly `uno` / `uno328pb` / `leonardo`, and release `3.0.0b13` published exactly
  `firestarter_{uno,uno328pb,leonardo}.hex` — env name and asset board name coincide. It is the same
  recorded-baseline file every other v1.23 gate already cites, so a fourth AVR target updates the
  release gate for free instead of silently not being required.
  Rejected: three hardcoded names with a citing comment (a literal that rots, in a milestone whose
  premise is files moving); rejected: deriving from `platformio.ini` `[env:*]` sections (the
  AVR/native filter is already non-trivial — Phase 124 added a **fourth** native env,
  `native_pinmap_provisional`).

- **D-13:** **`build.yml` (stable / `main`) is out of scope**, with the reason and the graduation
  trigger recorded so it reads as a decision. REL-01 names `beta-build.yml`; `py32f071` is in the
  host's `BETA_ONLY_BOARDS`, so a stable release carrying a py32 asset would advertise an image the
  stable CLI **exits 2 on** — contradicting the channel gating Phase 127 just hardened both ways.
  **Graduation trigger:** fold into `build.yml` when the board leaves `BETA_ONLY_BOARDS`.
  Rejected: adding just the AVR-assets check to `build.yml` (defensible — a silently-missing AVR
  asset on a *stable* release is worse than on a beta — but nothing in REL-01…REL-04 asks for it;
  captured as a deferred idea rather than dropped).

### Claude's Discretion

Stated defaults. Implement as described and flag any surprise.

- **D-14 (how `ad47c3b` lands):** **Re-apply by hand, cite `ad47c3b` in the commit message — do not
  cherry-pick.** Its `py32f071.yml` rewrite is based on a pre-Phase-124 tree with **no
  `push: branches: [beta]` trigger**, so a cherry-pick would silently revert MERGE-03; and D-06's
  composite action supersedes its workflow shape entirely. What carries over intact is the
  **`CMakeLists.txt` hyphen→underscore rename** (`TARGET_NAME`, `-Wl,-Map=`, `BIN_FILE`, `HEX_FILE`
  — all four, plus its explanatory comment) and the **README §"Release integration"** section.
  Verify the rename is grep-consistent across CMakeLists, both workflow files, the composite action
  and the docs — the original commit message notes it was grep-verified but **never built locally**.
- **D-15 (R-16's slip, fix it while in there):** `platform/py32f071/README.md`'s release section
  correctly argues for a **glob** and then supplies the **literal**
  `build/py32f071/firestarter_py32f071.hex`. Correct it to `build/py32f071/firestarter_*.hex` and
  make the shipped `beta-build.yml` `files:` entry match. The README also suggests
  `continue-on-error` "until validated on real silicon" — D-05 adopts that; make the README state
  the trigger rather than leave it as a suggestion.
- **D-16 (`py32f071.yml`'s artifact upload):** **Keep** the single-file
  `actions/upload-artifact` of `firestarter_py32f071.hex` from `ad47c3b`. A PR build stays
  downloadable, which is the only way to obtain an image for a future board bring-up before a
  release exists. The ELF/map/logs/checksum uploads `ad47c3b` removes stay removed.
- **D-17 (toolchain pinning in the composite action):** **Unpinned `apt-get install -y`**, matching
  today's `py32f071.yml` exactly. Pinning toolchain versions is a real improvement and a real
  behaviour change; it is not this phase's scope. Note it as deferred.
- **D-18 (evidence artifact):** **`128-NONREGRESSION.md`**, matching Phases 124/125/126/127. It must
  record: both rehearsal run URLs + commit SHAs, the asset list from run A, the asset list from run
  B (three AVR, no py32), the resolved SDK SHA, and the **explicit non-claim** that nothing here
  says the published image runs — Phase 130's CLOSE-02 ledger will cite it.
- **D-19 (commit sequencing):** Firmware commit(s) first, then the single app commit — the app test
  parses firmware files, so landing it first would make it red or (worse) skip. Both on
  `v1.23-py32f071-integration` in their respective repos.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone-level (read first)
- `.planning/research/SUMMARY.md` — §"Phase 128 — Release-asset fold into `beta-build.yml`" is this
  phase's brief. **R-16** (the README argues glob, supplies literal; and `beta-build.yml:92`'s
  `.pio/build/**/firestarter_*.hex` does **not** reach `build/py32f071/`) grounds D-15. **A-7**
  (cross-repo gates fail OPEN) grounds D-09 and D-12's non-vacuity requirements. **N-01** is why
  this phase is the only new work in v1.23 that makes any of the 21 host capabilities reachable.
  Its R-1…R-18 and A-1…A-7 supersede PROJECT.md and ROADMAP where they disagree.
- `.planning/ROADMAP.md` §"Phase 128: Release-Asset Fold" — the four success criteria, verbatim.
  Also §"Ordering — load-bearing, not preference" for the 127→128 and post-version-bump constraints.
- `.planning/REQUIREMENTS.md` REL-01…REL-04 (lines 85-88). **Read the requirement prose itself, not
  a plan's paraphrase** — the v1.22 Phase 121 lesson.
- `.planning/STATE.md` §"Milestone Context (v1.23)" — the claim ceiling, the no-PCB constraint, the
  release hazard, and §"Release-asset mechanics (already designed, not yet implemented)".

### Prior-phase decisions this phase inherits or discharges
- `.planning/phases/124-firmware-integration-merge/124-CONTEXT.md` — **D-07** (why `ad47c3b` was
  deliberately withheld for this phase), **D-10** (the double-ARM-build question, explicitly
  recorded *for Phase 128 to resolve* — discharged here by D-05), **D-08/D-09** (the operator-gated
  CI dispatch shape D-04 copies).
- `.planning/phases/127-host-dfu-installer/127-CONTEXT.md` — **`<code_context>` §Integration Points
  → Phase 128** (the `asset_candidates()` contract, and the instruction to flag loudly if it
  changes), **D-14** (the cross-repo fail-closed gate shape D-09 copies, including the resolved
  "no new `ALLOWED_SKIP_REASONS` entry" finding), **D-04** (recorded-not-gated counts).
- `.planning/phases/123-non-regression-baselines-gate-hardening/123-CONTEXT.md` — **D-10** (why a
  pinned count is rejected) and the standing operator preference for **an exit code over a human
  reading output**.

### Firmware repo — the code this phase changes
- `firestarter/.github/workflows/beta-build.yml` (104 L) — the fold target. Step order matters:
  `Generate release version` (id `version`) → `git-auto-commit-action@v5` → `Build PlatformIO
  Project` → `Resolve release target SHA` → `Release`. ARM steps go **after** the auto-commit;
  the AVR-assets assertion goes **before** `Release`. `files:` is currently the single glob
  `.pio/build/**/firestarter_*.hex`; `tag_name` is `${{ steps.version.outputs.version }}` (D-03
  overrides it in rehearsal mode).
- `firestarter/.github/workflows/py32f071.yml` (125 L) — the LOUD gate. Carries MERGE-03's
  `push: branches: [beta]` with a comment naming Phase 128 as the resolver. Its build steps become
  a call to the composite action (D-06).
- `firestarter/.github/actions/build-py32f071/action.yml` — **new**, D-06. No `.github/actions/`
  directory exists today.
- `firestarter/platform/py32f071/CMakeLists.txt` — `TARGET_NAME`, `-Wl,-Map=`, `BIN_FILE`,
  `HEX_FILE` (the hyphen→underscore rename, D-14) and the `FetchContent_Declare` `GIT_TAG` pin
  D-10 asserts against.
- `firestarter/platform/py32f071/README.md` — §"Release integration" (D-15's correction).
- `firestarter/scripts/check_release_assets.py` — **new**, D-11.
- `firestarter/scripts/baseline/size_baseline.json` — `avr_targets` keys are D-12's source of truth.
  Already load-bearing: read by `check_size_baseline.py` and `check_build_warnings.py` via the
  `FIRESTARTER_SIZE_BASELINE` seam.
- `firestarter/tests/test_checker_convention.py` — **BASE-08's enforcement.** Read its `CHECKER_GLOB`
  scope note before adding `scripts/check_release_assets.py`; the fixture/test pairing is mandatory
  and the floor is hardcoded so a shrunken glob fails.
- `firestarter/tests/fixtures/` — the planted/clean fixture naming convention D-11 must follow
  (`planted_*` / `clean_*`, see `README.md` there).

### Host repo — the one commit this phase adds
- `firestarter_app/tests/test_py32_flash_map_host.py` — **copy this module's shape** for D-08(b).
  It is 127's cross-repo linker-map gate: `@requires_fw` binding, parse, non-vacuity assertion.
- `firestarter_app/tests/fw_presence.py` — `FW_REPO_PRESENT` / `FW_ABSENT_REASON` / `@requires_fw`,
  all frozen at import time.
- `firestarter_app/tests/test_skip_census.py` — `ALLOWED_SKIP_REASONS`. **No new entry needed**
  (D-09); confirm rather than add.
- `firestarter_app/firestarter/firmware.py:116-152` — `asset_candidates()` and `_pick_asset()`.
  **Read-only this phase. Frozen.**

### External
- `softprops/action-gh-release@v2` — glob-vs-literal semantics (warn vs fail) and **draft-release
  tag-creation behaviour**, which D-01's containment depends on. **⚠ Verify before dispatching.**
- GitHub Actions docs — composite-action-runs-in-calling-job semantics (D-06's REL-01 argument) and
  `steps.<id>.outcome` vs `conclusion` under `continue-on-error` (D-07's fire condition).

</canonical_refs>

<code_context>
## Existing Code Insights

### Measured facts (verified live during this discussion — re-verify, do not assume)
- `asset_candidates("py32f071")` → `["firestarter_py32f071.hex", "firestarter_py32f071.bin"]`;
  `[0]` is the `.hex`. (`firestarter_app/firestarter/firmware.py:129-131`)
- `beta-build.yml:92` — `files: .pio/build/**/firestarter_*.hex`. The CMake image lands at
  `build/py32f071/`, **outside that glob**. A second `files:` entry is required; one glob will not
  cover both trees.
- `py32f071.yml` currently emits **hyphenated** names (`firestarter-py32f071.hex`). The rename to
  underscores is `ad47c3b`'s and has **not** landed (124 D-07 withheld it).
- The SDK is **already pinned**: `GIT_TAG 0ed2f4b4d3391eccfd4491006a30295fd78e32c2`,
  `GIT_SHALLOW FALSE`.
- `size_baseline.json` `avr_targets` keys: `uno`, `uno328pb`, `leonardo`. Release `3.0.0b13`
  published exactly `firestarter_{uno,uno328pb,leonardo}.hex`.
- Firmware workflow triggers: `beta-build.yml` → `push: [beta]` + dispatch · `py32f071.yml` →
  `push: [beta]` + `pull_request` (path-filtered) + dispatch · `build.yml` → `push: [main]` +
  `pull_request: [main]`. **A push to any other branch fires nothing.**
- `firestarter/scripts/` holds five checkers today (`check_build_warnings`, `check_cmake_manifest`,
  `check_landing_range`, `check_orphan_provisional`, `check_size_baseline`); `firestarter/tests/`
  holds their paired tests and `tests/fixtures/` their planted/clean trees.
- **No ARM toolchain in this devcontainer** (`arm-none-eabi-gcc`, `cmake`, `ninja` absent). Nothing
  ARM-side can be built or measured locally; every ARM claim cites a CI run URL + commit SHA.

### Reusable Assets
- **`firestarter_app/tests/test_py32_flash_map_host.py`** — 127's cross-repo gate. D-08(b) is its
  sibling; copy the `@requires_fw` + parse + non-vacuity shape rather than re-deriving it.
- **`firestarter/scripts/check_size_baseline.py` + `tests/test_check_size_baseline.py` +
  `tests/fixtures/planted_size_baseline_*`** — the closest analog for D-11's triple, including how a
  checker reads `size_baseline.json` (via the `FIRESTARTER_SIZE_BASELINE` seam) and how planted logs
  are structured.
- **`tests/fixtures/README.md`** — the fixture naming contract (`planted_*` must fail, `clean_*`
  must pass).
- **`ad47c3b`'s README §"Release integration"** — the three fold steps and the one release line,
  already written. Reuse the prose; correct the literal-vs-glob slip (D-15).

### Established Patterns
- **Every checker ships a planted fixture and a pytest proving non-zero exit** — BASE-08, mechanically
  enforced by `test_checker_convention.py` over `scripts/check_*.py`. Not a style note.
- **Cross-repo gates must fail CLOSED** — bind through `@requires_fw` and carry an explicit
  non-vacuity assertion. A-7 is the measured in-milestone counter-example: a firmware rename flipped
  five legs PASS→SKIP at exit 0 with a false reason.
- **An exit code, never a human reading output** (123-CONTEXT `<specifics>`). D-10's "assert, don't
  just log" and D-11's checker both follow from it.
- **Outward-facing actions are operator-gated by structural separation**, not by checkpoint type —
  `--auto`/`--chain` auto-approve human-verify gates regardless of `autonomous: false`.
- **The version bump is the whole update decision.** `update_version.py` rewrites `include/version.h`
  and auto-commits *before* the build; an image compiled in any other job carries a stale `VERSION`
  string, and the host compares exactly that string against the release tag.

### Integration Points
- **← Phase 127:** `asset_candidates("py32f071")[0]` is this phase's filename contract. Frozen.
- **← Phase 124:** MERGE-03's `push: branches: [beta]` on `py32f071.yml`, and its in-file comment
  naming Phase 128 as the resolver — D-05 discharges it; update that comment to state the resolution
  rather than leaving it pointing at a phase that has closed.
- **→ Phase 130:** CLOSE-02's honesty ledger needs this phase's non-claim in a citable form —
  *the asset publishes; nothing here says the image runs*. D-18's artifact is where it lives.
  Phase 130 also owns the actual `beta` push, which is when the fold first runs for real.
- **→ Phase 129:** unaffected. Nothing here touches the flash map, VID/PID or PCB record.

</code_context>

<specifics>
## Specific Ideas

- **"PY32F071 image not produced — this release carries no py32f071 asset."** — D-07's report
  wording. It states what the *release* lacks, which is the thing a reader of the run page needs;
  `py32f071.yml`'s red run separately states what broke.
- **`rehearsal-${{ github.run_id }}`** — D-03's tag override. Unmistakable, unique per run, and it
  cannot be read as a version.
- **The break is a renamed source path** — D-02 deliberately reproduces **C-1**, the failure this
  exact target actually had in Phase 124, rather than inventing a synthetic one.
- **A glob, never a literal** — `softprops/action-gh-release` *warns* on an unmatched glob but
  *fails* on a missing literal. While the port is unproven, a broken ARM build must leave the py32
  asset simply absent. The README currently argues this correctly and then does the opposite (R-16).
- **Read `outcome`, not `conclusion`** — under `continue-on-error`, `conclusion` is `success` even
  when the step failed. A report keyed on `conclusion` can never fire.
- **Non-vacuity per parse** — D-09 asserts three names are equal; it must also assert it *found*
  three names. Two empty strings compare equal.
- **The permitted claim is exactly one sentence wide:** the asset publishes. Not that it installs,
  boots, or runs. No PY32F071 PCB exists.

</specifics>

<deferred>
## Deferred Ideas

- **Fold the ARM build into `build.yml` (stable / `main`)** → when `py32f071` leaves the host's
  `BETA_ONLY_BOARDS` (D-13). Not a future phase in this milestone — a graduation trigger.
- **Run `check_release_assets.py` in `build.yml` too** → unscheduled. Genuinely defensible (a
  silently-missing AVR asset on a *stable* release is worse than on a beta) but outside
  REL-01…REL-04, and it touches the stable release workflow.
- **Pin the apt toolchain versions in the composite action** → unscheduled (D-17). A real
  reproducibility improvement and a real behaviour change; not this phase's scope.
- **Record the SDK SHA / py32 asset status in the release body** → Phase 130 or later. Rejected
  twice during discussion as release-facing prose this phase does not own.
- **The self-flash bootloader over CDC + COBS**
  (`.planning/seeds/py32f071-no-external-tool-fw-install.md`) — still the intended *primary* install
  route. Publishing a DFU-installable asset does **not** retire it; Phase 129 must say so explicitly.

### Reviewed Todos (not folded)
`todo.match-phase 128` returned five matches, all keyword-only. None folded:

- **`correct-v128-py32-roadmap-prior-art`** (0.6) — the nearest miss by topic, but it is explicitly
  **Phase 130's** CLOSE-03 scope (the ROADMAP slot renumber lands with the prior-art correction, in
  the same change). Folding it here would split one edit across two phases.
- **`avrdude-mcu-detection-fallback`** (0.6) — targets `_install_with_avrdude`, which HOST-01 froze
  as an accepted deviation (127 D-17). No CI or release-asset surface.
- **`2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads`** (0.6) — firmware VPP
  behaviour; no CI surface.
- **`cobs-decoder-framelevel-deadline-wr01`** (0.6) — firmware COBS transport; unrelated.
- Remaining match keyword-only with no release-asset surface.

</deferred>

---

*Phase: 128-Release-Asset Fold*
*Context gathered: 2026-08-01*
