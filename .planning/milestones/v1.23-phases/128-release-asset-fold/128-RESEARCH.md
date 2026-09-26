# Phase 128: Release-Asset Fold - Research

**Researched:** 2026-08-01
**Domain:** GitHub Actions release-asset publication (`softprops/action-gh-release`), composite actions, CMake FetchContent provenance, cross-repo filename-contract gates
**Confidence:** HIGH on every mechanical fact below (all four ⚠ VERIFY items are now RESOLVED against primary sources or a real CI run). LOW-by-construction on anything about PY32F071 silicon — no PCB exists.

> **The ROADMAP flags this phase `research-skip`. That flag was wrong again.** Research overturned
> one premise embedded in a *requirement* (REL-02), found one bug that would have made the D-01
> rehearsal write a **stable** version string, found one `.gitignore` rule that makes D-11's fixture
> **uncommittable as designed**, and found a **historical precedent proving the exact hazard D-01
> guards against has already fired once from precisely this route.** Six of the corrections below
> change task shape. This is the fifth consecutive skip-flagged phase (121, 122, 125, 127, 128)
> where research overturned locked content.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

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

### Deferred Ideas (OUT OF SCOPE)

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
- Also out of scope per `<domain>`: any push to `beta`, any tag, any published (non-draft) release,
  any public comment (Phase 130); release-note *content*; the three-tier flash path / `BOOTLOADER`
  sizing / VID-PID / BOOT0-nBOOT1 / SWD pads (Phase 129); any host-side change beyond D-08's single
  test — **`asset_candidates()` is frozen**; and **any claim that the published image runs, boots or
  installs**.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

Requirement prose read verbatim from `.planning/REQUIREMENTS.md` lines 85-88 (not a paraphrase —
the v1.22 Phase 121 lesson).

| ID | Description (verbatim) | Research Support |
|----|------------------------|------------------|
| **REL-01** | "The ARM build runs inside `beta-build.yml`'s job **after** `update_version.py` rewrites and auto-commits `include/version.h`, so the published image carries the release `VERSION` the host compares against the tag" | **§Finding F-9 upgrades this from a YAML read to a mechanical assertion.** `include/firestarter.h:54` defines `FW_VERSION VERSION ":" RURP_BOARD_NAME`; `src/firestarter.cpp` and `src/hardware_operations.cpp` (both in `FIRESTARTER_COMMON_SOURCES`) reference it; and on ARM `PSTR(v)` is `(v)` and `PROGMEM` is empty (`include/rurp_platform_compat.h:23-32`), so `"3.0.0b14:py32f071"` is a **plain ASCII string in `.rodata`** of the ARM image. The image can therefore be asserted to carry the bumped string, which survives a future step reorder that a YAML read does not. §Architecture Pattern 1 gives the exact steps; §Finding F-2 is the blocker to fix first (the rehearsal takes the *stable* version path unless `beta_version` is supplied). |
| **REL-02** | "`firestarter_py32f071.hex` is published as a GitHub **release asset** — not an Actions artifact — matched by a **glob**, because the release action warns on an unmatched glob but fails on a missing literal path" | **The clause after "because" is FALSE — see §Finding F-1, verified from the action's own source.** The action makes *no* glob-vs-literal distinction; the *only* knob is `fail_on_unmatched_files`, default `false`, which the shipped `beta-build.yml` does not set. The requirement's *prescription* (a glob) is still satisfiable and harmless; its *rationale* must be corrected and the real invariant pinned instead: **never set `fail_on_unmatched_files: true`**. §Don't Hand-Roll and §Pitfall 1 give the shape. |
| **REL-03** | "A deliberately broken ARM build still publishes all three AVR `.hex` assets, proven rather than assumed, with an AVR-assets-present assertion before the release step" | §Finding F-6 (the `.pio` `.gitignore` trap makes D-11's fixture uncommittable without a build-root seam) and §Finding F-11 (`test_checker_convention.py` floors must rise in the same commit). §Architecture Pattern 3 gives the checker's exact house shape, taken from `scripts/check_size_baseline.py`. §Finding F-14 confirms the AVR glob is already sufficient and that native envs emit no `.hex`. |
| **REL-04** | "CI asserts the emitted filename matches `asset_candidates("py32f071")[0]`, and logs the resolved SDK commit SHA" | `asset_candidates("py32f071")[0] == "firestarter_py32f071.hex"` re-verified live (`firestarter_app/firestarter/firmware.py:116-131`). §Finding F-5 **resolves D-10's ⚠ VERIFY by measurement**: the FetchContent source dir is `build/py32f071/_deps/py32f071_sdk-src`, read off real CI run `30676982030`'s object paths. §Finding F-15 corrects D-10's stated rationale (no cache covers `_deps`). §Architecture Pattern 4 gives the three-way app-side gate; §Finding F-8/F-9-app cover its CI-skip and clean-tree preconditions. |
</phase_requirements>

---

## Summary

Everything this phase changes is CI plumbing in two repos, and the whole risk profile is *hollow
gates* rather than *hard problems*. Nothing here needs new technology: the ARM target already
builds green on the milestone branch in 49 seconds (run
[`30676982030`](https://github.com/henols/firestarter/actions/runs/30676982030), 2026-08-01T01:02Z,
branch `v1.23-py32f071-integration`, flash 27 456 B, RAM 6 000 B), `beta-build.yml` already
publishes exactly three AVR assets per release (verified live against `3.0.0b14`), and the host's
filename contract is already frozen and correct. The work is: move the ARM build into the release
job behind a composite action, add two provable exit-code gates, and produce citable evidence from
two dispatches that leave no public footprint.

The research found **six corrections that change task shape**, in rough order of severity.
(1) **REL-02's stated rationale is false** — `softprops/action-gh-release` treats a literal path
exactly like a glob (`glob.sync()` on both) and only fails when `fail_on_unmatched_files: true`,
which defaults to false; the soft-absence property REL-03 depends on comes from that default, not
from choosing a glob. (2) **The D-01 rehearsal will write a *stable* version string** —
`update_version.py`'s `is_beta_mode()` requires `--beta`, `GITHUB_REF == refs/heads/beta`, or a
non-empty `BETA_VERSION`; a throwaway-branch dispatch with the input blank satisfies none, so it
takes the stable path and rewrites `include/version.h` from `3.0.0b14` to `3.0.1`. The dispatch must
supply `beta_version` explicitly. (3) **D-11's planted fixture cannot be committed as designed** —
`.gitignore` line 1 is the bare pattern `.pio`, which matches at any depth
(`git check-ignore -v` confirms it swallows `tests/fixtures/planted_release_assets_x/.pio/...`), so
the checker needs a build-root seam. (4) **The hazard D-01 guards against has already fired once** —
run `30199560282` was a `workflow_dispatch` of `beta-build.yml` from the non-default branch
`v1.21-community-chip-validation-command` and it published the **real, public** prerelease
`3.0.0b11` with a **real tag** (`refs/tags/3.0.0b11` → `0fd7992`). D-01's draft mode is not
theoretical caution. (5) **The app-side binding is enforced locally only** — neither app CI workflow
checks out the firmware sibling, so `@requires_fw` skips there. (6) **`test_checker_convention.py`'s
floors must rise in the same commit** as the sixth checker, and `FIXTURE_FLOOR` has already drifted
(10 recorded vs 13 actual).

All four of CONTEXT's ⚠ VERIFY items are now **RESOLVED**: a draft release creates no tag (proven
from `finalizeRelease()`'s early return plus the action's own "untagged-…" comment plus issue #722);
`outcome` is before `continue-on-error` and `conclusion` after, so D-07 must read `outcome`; the
FetchContent source dir is `build/py32f071/_deps/py32f071_sdk-src`, measured from a real run's
object paths; and a composite action does run in the calling job on the same workspace, so D-06's
REL-01 argument holds. One bonus: **REL-01 can be proven mechanically rather than by reading YAML** —
the version string is a plain ASCII literal in the ARM image's `.rodata`, so `strings` over the
published `.hex` (converted back to binary with `objcopy -I ihex -O binary`) is a two-line exit-code
gate that survives a future step reorder.

**Primary recommendation:** Implement the fold exactly as D-01…D-19 describe, with these five
mechanical substitutions: give `check_release_assets.py` a `FIRESTARTER_PIO_BUILD_ROOT` env seam so
its planted fixture can avoid a `.pio` directory name; supply `beta_version` on every rehearsal
dispatch; pin `fail_on_unmatched_files`'s absence with a comment instead of relying on glob-vs-literal
folklore; read `steps.<id>.outcome`; and add the `strings`-over-the-hex REL-01 assertion because it
is nearly free and it is the only REL-01 evidence that cannot rot.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| ARM toolchain install + cmake configure + build | CI composite action (`.github/actions/build-py32f071`) | — | D-06: one definition, called by both workflows; runs in the calling job so REL-01's same-job constraint survives |
| Version bump + auto-commit | `beta-build.yml` job, before the ARM call | `.github/scripts/update_version.py` | Existing, unchanged. REL-01 is entirely an *ordering* property of this job |
| AVR-assets-present gate | `firestarter/scripts/check_release_assets.py` (repo script, exit code) | `beta-build.yml` step calls it | D-11: provable locally without CI; the workflow is only the call site |
| Required-AVR-target set | `firestarter/scripts/baseline/size_baseline.json` → `avr_targets` keys | — | D-12: the same recorded-baseline file every other v1.23 gate cites |
| Emitted-filename source of truth | `firestarter/platform/py32f071/CMakeLists.txt` (`TARGET_NAME`/`BIN_FILE`/`HEX_FILE`) | — | The CMake build is what actually names the file |
| Filename-contract source of truth | `firestarter_app/firestarter/firmware.py::asset_candidates` | — | **Frozen.** Read-only this phase (127 `<code_context>`) |
| Cross-repo filename binding | `firestarter_app/tests/test_*_host.py` (app repo) | firmware workflow literal (transcription) | D-08/D-09: the firmware repo cannot import the host package; the binding can only live app-side |
| Soft-ARM-failure reporting | `beta-build.yml` step reading `steps.<id>.outcome` → `::warning::` + `$GITHUB_STEP_SUMMARY` | `py32f071.yml`'s red run | D-07: two different statements — *what the release lacks* vs *what broke* |
| Asset publication | `softprops/action-gh-release@v2` `files:` | — | Release assets, not Actions artifacts — a different API (`ad47c3b`'s point 1) |

---

## Standard Stack

Nothing new is installed. Every tool below is already in use in this repo; the phase adds no
dependency to either sub-repo. **No `## Package Legitimacy Audit` section applies** — this phase
installs zero external packages in either ecosystem (the composite action's `apt-get install` is a
verbatim move of `py32f071.yml`'s existing four-package line, unpinned per D-17).

### Core

| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| `softprops/action-gh-release` | `@v2` (already pinned in `beta-build.yml:90`) | Creates the release and uploads assets | Already the repo's release action; the `files:` glob is the whole publication mechanism [VERIFIED: source read of `master` `src/{run,util,github}.ts`] |
| GitHub Actions composite action | `runs.using: composite` | D-06's single definition of the cmake invocation | Runs *in* the calling job on the same runner/workspace, unlike `workflow_call` [CITED: actions/runner ADR 0549 `composite-run-steps`] |
| `gcc-arm-none-eabi` + `binutils-arm-none-eabi` + `cmake` + `ninja-build` | apt, unpinned (D-17) | ARM build | Verbatim from `py32f071.yml:28-35`; proven green on `ubuntu-latest`, 49 s end to end [VERIFIED: run 30676982030] |
| `python3` stdlib only | 3.11 (already set up by `beta-build.yml:40-43`) | `check_release_assets.py` | House convention: every `scripts/check_*.py` is stdlib-only with a hand-rolled argv parser, no argparse [VERIFIED: `check_size_baseline.py:330` comment "Manual argv parser (no third-party/argparse dependency; house convention…)"] |
| `pytest` | already installed by `beta-build.yml:62-63` and in the app's `.[test]` extra | The paired anti-hollow test | BASE-08's mechanically-enforced convention |

### Supporting

| Component | Purpose | When to Use |
|-----------|---------|-------------|
| `arm-none-eabi-objcopy -I ihex -O binary` | Convert the published `.hex` back to a binary so `strings` can find the version literal | REL-01's mechanical assertion (§Pattern 1). Already on PATH via `binutils-arm-none-eabi` |
| `strings` (binutils, always present on `ubuntu-latest`) | Find `"<VERSION>:py32f071"` in the image | Same |
| `gh api` / `gh release view --json assets` | Read the draft release's asset list for D-18's evidence | Draft asset download URLs are `untagged-<hash>` placeholders — the **API asset list**, not a URL, is the citable evidence [VERIFIED: `src/run.ts:82-84` comment] |
| `$GITHUB_STEP_SUMMARY` | D-07's report and D-10's SDK-SHA echo | Both; rejected for the release body twice |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Composite action (D-06) | Reusable workflow (`workflow_call`) | **Breaks REL-01 outright** — separate job, separate checkout, so the image would not be built in the version-bumped job. D-06 already rejects it; research confirms the mechanism [CITED: docs — composite steps run in the calling job; `workflow_call` creates a new job] |
| Composite action (D-06) | Duplicated steps + a parity checker | D-06 rejected it. Research adds one supporting point: the `beta-build.yml` copy is `continue-on-error`, so drift there fails **silently**, which is exactly the class a post-hoc checker detects too late |
| `strings` over the converted `.hex` (§Pattern 1) | `strings` over the ELF | The ELF is not the published artifact. Converting the `.hex` asserts on the exact bytes that ship. Cost: one extra `objcopy` line |
| Glob `build/py32f071/firestarter_*.hex` | Literal `build/py32f071/firestarter_py32f071.hex` | **Behaviourally identical** under the action's default (§F-1). The glob is still preferable — it does not need editing on a rename, and it reads consistently with the AVR entry — but the choice is now a *style* argument, not a *failure-mode* argument |

**Installation:** none. The only new files are `.github/actions/build-py32f071/action.yml`,
`scripts/check_release_assets.py`, `tests/test_check_release_assets.py`, a
`tests/fixtures/planted_release_assets_*` tree (plus a `clean_release_assets_*` control), and one
app-repo test module.

**Version verification:** N/A — no package is added to `package.json`, `pyproject.toml`, or
`platformio.ini`. `softprops/action-gh-release@v2` is already the pinned major and this phase does
not change it.

---

## Findings — the six corrections and the four resolved ⚠ VERIFY items

### F-1 — CORRECTION (severity: HIGH, changes REL-02's rationale, R-16, D-15 and `<specifics>`)

**The claim:** *"`softprops/action-gh-release` warns on an unmatched glob but fails on a missing
literal."* This appears in REL-02's own text, in milestone research finding **R-16**, in
`platform/py32f071/README.md` (via `ad47c3b`), in CONTEXT D-15, and in CONTEXT `<specifics>`
("A glob, never a literal").

**It is false.** [VERIFIED: primary source read of `softprops/action-gh-release@master`]

`src/util.ts:193-206` — `unmatchedPatterns()` runs `glob.sync(normalizeFilePattern(pattern))` over
**every** entry in `files:`, glob or literal alike, and reports the pattern as unmatched when zero
matches survive the `statSync(p).isFile()` filter. `src/run.ts:13-21` then decides severity:

```ts
patterns.forEach((pattern) => {
  if (config.input_fail_on_unmatched_files) {
    throw new Error(`⚠️  Pattern '${pattern}' does not match any files.`);
  } else {
    console.warn(`🤔 Pattern '${pattern}' does not match any files.`);
  }
});
```

`action.yml` documents `fail_on_unmatched_files` as *"Fails if any of the `files` globs match
nothing. Defaults to false"*, and `src/util.ts:132` implements the default as
`env.INPUT_FAIL_ON_UNMATCHED_FILES == 'true'` — absent means `false`. There is **no code path that
treats a literal path differently from a glob.**

**What this means for the plan:**

1. REL-02's *prescription* (use a glob) is unaffected and still worth doing — but for readability
   and rename-resilience, not for failure semantics. Do not repeat the false rationale in any new
   comment, README line, or SUMMARY.
2. The invariant that actually protects REL-03 is: **`fail_on_unmatched_files` must never be set to
   `true` on this step.** The shipped `beta-build.yml:89-96` does not set it, so the property holds
   today by omission. An omission is not a decision — pin it with a comment on the `Release` step
   naming REL-03, so a future contributor adding `fail_on_unmatched_files: true` for "stricter CI"
   sees why it is forbidden.
3. D-15's README correction should *both* change the literal to a glob **and** replace the incorrect
   glob-vs-literal justification with the real one. Leaving the old sentence in place would ship a
   corrected code line next to a wrong explanation — the shape C-5 caught in Phase 122.

**Secondary observation from the same read:** `paths()` (`util.ts:177-191`) filters on
`statSync(p).isFile()` — a **zero-byte** file is still a file and *would* be uploaded. D-11/D-12's
non-empty requirement (`test -s` semantics) is therefore load-bearing, not belt-and-braces.

### F-2 — CORRECTION (severity: HIGH, blocks D-01/D-03's rehearsal procedure)

`.github/scripts/update_version.py`'s `is_beta_mode(args)` returns `True` only if `args.beta`, or
`os.environ["GITHUB_REF"] == "refs/heads/beta"`, or `os.environ.get("BETA_VERSION")` is truthy.
The workflow passes `BETA_VERSION: ${{ github.event.inputs.beta_version }}` and nothing else.

On a **throwaway-branch `workflow_dispatch` with `beta_version` left blank**:

- `GITHUB_REF` is `refs/heads/<throwaway>` → no match.
- `BETA_VERSION` is the empty string → falsy → no match.
- `--beta` is never passed.

→ `is_beta_mode()` is **False** → the **stable path** runs: `get_header_version()` parses
`3.0.0b14` into `(3, 0, 0, "b14")`, discards the pre-release group, increments patch, and writes
**`3.0.1`** into `include/version.h`, emitting `version=3.0.1` on `$GITHUB_OUTPUT`. The
git-auto-commit step then commits that stable regression to the throwaway branch.

[VERIFIED: source read of `.github/scripts/update_version.py:53-59, 176-194`, plus
`include/version.h:11` == `"3.0.0b14"`]

**Consequences and the fix.** The branch is deletable, so this is contained, not dangerous — but it
makes D-03's premise (*"the version bump still runs and still compiles into the image, so REL-01
stays proven by the rehearsal"*) evidence for a *stable* string, and it puts a confusing `3.0.1` in
the evidence artifact. **Fix: every rehearsal dispatch must supply `beta_version` explicitly** —
e.g. `3.0.0b99`, which is unmistakable, passes `BETA_VERSION_RE`
(`^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$`), forces the beta path, and never collides with a real
`b15`. This is a **dispatch-procedure requirement**, not a code change; it must appear verbatim in
the operator-gated plan's dispatch instructions and in `128-NONREGRESSION.md`, or the next person
rehearsing will hit it.

Also worth pinning while in there: REL-01's real assertion target is
`include/version.h` == `steps.version.outputs.version`, **not** `== tag_name`. In rehearsal mode
D-03 deliberately overrides `tag_name` to `rehearsal-<run_id>`, so a tag-equality assertion would be
red by design. Assert against the step output.

### F-3 — RESOLVED ⚠ VERIFY (D-01's containment holds)

**A draft release creates no git tag.** Three independent confirmations:

1. `src/github.ts:755-764` — `finalizeRelease()` returns the release untouched when
   `config.input_draft === true`. Publishing is what triggers GitHub's tag-ref creation, and
   publishing never happens. [VERIFIED: source read]
2. `src/run.ts:82-84` — the action's own comment: *"Draft releases use temporary `untagged-...`
   URLs for assets. URLs will be changed to correct ones once the release is published."* A release
   whose assets live under `untagged-…` demonstrably has no tag. [VERIFIED: source read]
3. `softprops/action-gh-release` issue **#722** — a draft release is created *even when repository
   rulesets forbid creating the tag*, i.e. draft creation precedes and does not require tag
   creation. [CITED: github.com/softprops/action-gh-release/issues/722]

**Therefore D-01 needs no change**, and D-03's `rehearsal-${{ github.run_id }}` override is
belt-and-braces rather than a tag-hazard fix — keep it anyway for exactly the reason D-03 gives (an
accidentally-published draft must not look like `3.0.0b15`).

**One consequence for D-18's evidence:** the draft's asset *download URLs* are `untagged-<hash>`
placeholders and are not stable citations. Collect the asset list from the API —
`gh release view <tag> --json assets` or `gh api repos/henols/firestarter/releases/<id>/assets` —
and record asset **names + sizes**, exactly as the live `3.0.0b14` check in §F-14 did.

### F-4 — RESOLVED ⚠ VERIFY (D-07 must read `outcome`)

GitHub's contexts reference, quoted: `steps.<step_id>.outcome` is *"The result of a completed step
before `continue-on-error` is applied"*; `steps.<step_id>.conclusion` is *"…after `continue-on-error`
is applied."* A `continue-on-error` step that fails has `outcome: failure` and
`conclusion: success`. [CITED: docs.github.com/en/actions/reference/workflows-and-actions/contexts]

**D-07's ⚠ VERIFY was correct as written.** The report condition is
`if: steps.<id>.outcome == 'failure'`. A `conclusion`-keyed condition could never fire — the exact
hollow-gate shape unwound in Phases 118 and 124.

On CONTEXT's open sub-question (*"`if: always()` is belt-and-braces here … Planner's call"*): the
research view is **omit `always()`**. Because the ARM call site is `continue-on-error: true`, the
job stays on the success path, so a plain step already runs. Adding `always()` would additionally
make the report fire on a *cancelled* job, where `outcome` is `cancelled`, not `failure` — a
condition that reads `== 'failure'` would then simply not print, so `always()` buys nothing and
costs one more thing a reader has to reason about. A one-line comment stating why it is absent is
worth more than the `always()`.

### F-5 — RESOLVED ⚠ VERIFY (D-10's FetchContent path, MEASURED not guessed)

CMake's documented defaults: `FETCHCONTENT_BASE_DIR` defaults to `${CMAKE_BINARY_DIR}/_deps`, and
`SOURCE_DIR` defaults to `<base>/<lowercaseName>-src`.
[CITED: cmake.org/cmake/help/latest/module/FetchContent.html]

**Measured on a real run** — job log for run
[`30676982030`](https://github.com/henols/firestarter/actions/runs/30676982030) (job `91306188205`,
branch `v1.23-py32f071-integration`, 2026-08-01T01:02Z) contains ninja lines such as:

```
[26/42] Building C object CMakeFiles/firestarter-py32f071.elf.dir/_deps/py32f071_sdk-src/Templates/PY32F071xx_Templates/Src/system_py32f071.c.obj
```

Those paths are relative to the build dir `build/py32f071`, so the SDK source tree is
**`build/py32f071/_deps/py32f071_sdk-src`**. [VERIFIED: CI run 30676982030 job log]

D-10 may therefore hardcode that path *with the run URL cited in a comment* rather than reading it
off run A. Two guards still required, both cheap:

- **Fail loudly if the directory is absent** (a future `FETCHCONTENT_BASE_DIR` override or a CMake
  upgrade could move it) — do not let a missing dir degrade to an empty SHA compared against an
  empty `GIT_TAG`. That is A-7's failure shape.
- **Assert the parsed `GIT_TAG` is 40 hex characters** before comparing. `FetchContent_Declare`
  accepts a branch or tag name too; a non-SHA `GIT_TAG` would make the comparison meaningless
  rather than red.

Two related notes: `GIT_SHALLOW FALSE` means a full clone, so `.git` exists and
`git -C <src> rev-parse HEAD` returns the pinned SHA from a detached HEAD. And
`FetchContent_Populate(<name>)` (the single-argument form used at `CMakeLists.txt:22`) is
**deprecated as of CMake 3.30** under `CMP0169`; `ubuntu-latest`'s apt cmake will eventually warn
here. Out of scope for this phase — record it as an observation, do not fix it (D-17's spirit).

### F-6 — CORRECTION (severity: HIGH, blocks D-11's fixture as designed)

`firestarter/.gitignore` line 1 is the bare pattern `.pio` — with no leading slash, gitignore
matches it **at every depth**. Verified directly:

```
$ git check-ignore -v tests/fixtures/planted_release_assets_x/.pio/build/uno/firestarter_uno.hex
.gitignore:1:.pio	tests/fixtures/planted_release_assets_x/.pio/build/uno/firestarter_uno.hex
```

[VERIFIED: `git check-ignore -v` in `/workspaces/firestarter`]

So a `planted_release_assets_*` fixture tree that reproduces a realistic `.pio/build/<env>/…`
layout **cannot be committed**. Worse, `git add` on an ignored path is silent — and
`tests/fixtures/README.md` already warns that fixture presence must be verified with
`git ls-files`, never with `git add`'s exit code. A plan that skips that check would land a fixture
directory that does not exist in the index, and `test_checker_convention.py`'s
`test_every_checker_has_planted_fixture` would pass locally (the directory is on disk) while being
red for everyone else.

**Fix: give `check_release_assets.py` a build-root seam** and use a non-dotted directory name in the
fixture. The house precedent is exact: `check_size_baseline.py:95-97` reads its input path through
`FIRESTARTER_SIZE_BASELINE` with a committed default, and
`test_check_size_baseline.py`'s coverage item 7 is a dedicated *seam-precedence* test proving the
checker genuinely reads the env var rather than embedding the path. Mirror it:

- `FIRESTARTER_PIO_BUILD_ROOT` (env), defaulting to `<repo>/.pio/build`, and/or a
  `--build-root <path>` argv entry.
- Fixture trees named `tests/fixtures/planted_release_assets_missing_uno328pb/pio_build/…` and
  `tests/fixtures/clean_release_assets_all_three/pio_build/…` — **no dot**, so nothing is ignored.
- A `git ls-files tests/fixtures/` verification step in the plan, per the fixtures README.
- A seam-precedence test in the paired module, so the seam itself is proven live.

### F-7 — NEW (severity: HIGH for D-01's justification; de-risks D-04's mechanics)

**Dispatching `beta-build.yml` from an arbitrary non-default branch works in this repo, and doing it
without `draft: true` has already published a real public prerelease with a real tag.**

- `beta-build.yml` does **not** exist on the default branch. `henols/firestarter`'s default branch is
  `main`, and `git ls-tree -r origin/main .github/workflows/` lists **only `build.yml`**.
  [VERIFIED: `gh repo view --json defaultBranchRef`, `git ls-tree`]
- Nevertheless the workflow is registered (`gh workflow list` → *"Firestarter beta pre-release
  build  active  280350856"*) and **has been dispatched from a milestone branch**: run
  [`30199560282`](https://github.com/henols/firestarter/actions/runs/30199560282), event
  `workflow_dispatch`, branch `v1.21-community-chip-validation-command`, 2026-07-26T11:08:10Z.
  [VERIFIED: `gh run list --workflow=beta-build.yml`]
- That run published the **real, public** prerelease `3.0.0b11` two minutes later
  (2026-07-26T11:10:01Z) and created a **real tag**: `refs/tags/3.0.0b11` →
  `0fd7992187467f6d245bc106786253f497ea0ecc`, contained in `origin/beta`,
  `origin/v1.21-community-chip-validation-command` and `origin/v1.23-py32f071-integration`.
  [VERIFIED: `gh api repos/henols/firestarter/git/ref/tags/3.0.0b11`, `git branch -r --contains`]

Two things follow. **First, the mechanism D-01 needs is proven to work** — the "a `workflow_dispatch`
workflow must live on the default branch" folklore does not block this, and `gh` is authenticated
with `repo` + `workflow` scopes, so `gh workflow run beta-build.yml --ref <throwaway>` will succeed.
Note that GitHub resolves the workflow *definition* (including the new `rehearsal` input) from the
dispatched ref, so the input only needs to exist on the throwaway branch. **Second, D-01's draft
containment is not hypothetical caution: the exact accident it prevents has already happened once
from precisely this route.** Say so in `128-NONREGRESSION.md` — it is the strongest possible
justification for the `rehearsal` input's permanence (D-03), and it belongs in Phase 130's honesty
ledger alongside the two stray prereleases already recorded.

### F-8 — NEW (severity: MEDIUM; changes what D-08(b)'s evidence can claim)

**Neither app CI workflow checks out the firmware sibling, so the D-08(b) binding SKIPS in CI.**
`firestarter_app/.github/workflows/ci.yml` has exactly two `actions/checkout@v4` steps (lines 31 and
90), both plain single-repo checkouts with no `repository:`/`path:`; `beta-release.yml` runs
`pytest tests/ -v` on the same single-repo tree. With no `../firestarter/.git` marker,
`tests/fw_presence.py`'s `FW_REPO_PRESENT` is `False` at import and `@requires_fw` skips every
cross-repo leg. [VERIFIED: grep of both workflow files; `fw_presence.py:77-102`]

This is a pre-existing, accepted property (127 D-14 landed the same shape and the census already
allows `FW_ABSENT_REASON`), **not** something to fix here. But it constrains the evidence:

- The plan's verification step must run the app-side test **locally, in the devcontainer**, and
  record a **PASS with no skip** — `pytest tests/test_<new>.py -q -rs` and assert the `-rs` report
  is empty of the FW-absent reason. A green run that actually skipped is the A-7 shape.
- `128-NONREGRESSION.md` must state plainly that the cross-repo binding is enforced by a local run
  and by developer discipline, **not** by app CI. Claiming CI enforcement would be false.
- Confirmed working today: `python3 -m pytest tests/test_py32_flash_map_host.py -q` → 16 passed in
  `/workspaces/firestarter_app`, i.e. the sibling layout resolves and the 127 precedent is live.
  [VERIFIED: run this session]

### F-9 — NEW OPPORTUNITY (severity: MEDIUM; strengthens REL-01 at near-zero cost)

**The version string is a plain ASCII literal inside the ARM image, so REL-01 can be an exit code
rather than a YAML read.** Chain, all read live:

- `include/version.h:11` → `#define VERSION "3.0.0b14"`.
- `include/firestarter.h:54` → `#define FW_VERSION VERSION ":" RURP_BOARD_NAME`.
- `src/firestarter.cpp:151` (`LOG_INFO_ID_ASTR(MSG_INFO_FW, FW_VERSION)`) and
  `src/hardware_operations.cpp:98` (`SERIAL_PORT.println(FW_VERSION)`) both reference it, and both
  files are in the ARM target's `FIRESTARTER_COMMON_SOURCES` (`CMakeLists.txt:36, 38`).
- `platform/py32f071/CMakeLists.txt:139` sets `RURP_BOARD_NAME="py32f071"`.
- On ARM, `include/rurp_platform_compat.h:23-32` defines `PROGMEM` as empty and `PSTR(value)` as
  `(value)`, so no PROGMEM/flash-string indirection applies — the concatenated literal
  `"3.0.0b14:py32f071"` lands in `.rodata` as ordinary bytes.

[VERIFIED: source reads of all five files]

Criterion 1's stated method is *"verified by reading the YAML step order"*. That is satisfiable but
it rots the moment someone reorders steps. A two-line addition asserts the property on the artifact
that actually ships (see §Pattern 1). Recommend adding it **alongside**, not instead of, the YAML
read — the requirement's wording is satisfied either way, and the mechanical form is what makes the
claim survive Phase 130 and beyond.

### F-10 — CORRECTION (severity: LOW, factual only)

CONTEXT D-12 says *"Phase 124 added a **fourth** native env, `native_pinmap_provisional`."*
`platformio.ini` has **six** envs total and **three** native ones: `[env:uno]`, `[env:uno328pb]`,
`[env:leonardo]`, `[env:native]`, `[env:native_nodevtools]`, `[env:native_pinmap_provisional]`.
`native_pinmap_provisional` is the **third** native env (and the sixth env overall).
[VERIFIED: `grep -n '^\[env' platformio.ini`]

D-12's *argument* is unaffected — the AVR/native filter is still non-trivial and deriving from
`avr_targets` keys is still the right call. Only the count is wrong. Do not repeat "fourth native
env" in any plan or SUMMARY.

### F-11 — NEW (severity: MEDIUM; a hard precondition for D-11)

`tests/test_checker_convention.py` currently declares `FLOOR = 5` and `FIXTURE_FLOOR = 10`
(lines 123-124). Measured today: **5** `scripts/check_*.py` and **13** `tests/fixtures/planted_*`
entries. The module's own docstring is explicit: *"A later phase that adds a firmware checker under
`firestarter/scripts/` raises both floors deliberately in the SAME commit that adds the checker;
lowering a floor is never the correct response to a red gate here."*
[VERIFIED: file read + `pathlib` count; the suite currently passes 7/7]

So adding `check_release_assets.py` requires, **in the same commit**:

- `FLOOR` 5 → **6**.
- `FIXTURE_FLOOR` 10 → the true post-phase count (**14** if this phase adds one `planted_*` entry;
  count it, do not predict it). Note `FIXTURE_FLOOR` has **already drifted** — Phases 124 and 126
  added planted fixtures without raising it, so it sits three below reality. Correcting it is in the
  spirit of the docstring and costs nothing.
- The paired test module must contain the literal string `check_release_assets.py` (test 5) and a
  literal `returncode != 0` assertion (test 6). Both are textual checks over the module source.

### F-12 — RESOLVED (R-17 is already closed; nothing to do)

Milestone research finding R-17 flagged `platform/py32f071/cmake/write_checksums.cmake` as orphaned
with zero references. It **no longer exists** — `platform/py32f071/cmake/` contains only
`arm-none-eabi.cmake`, and a repo-wide grep for `write_checksums` returns nothing.
[VERIFIED: `ls`, `grep -rn`] A prior phase already deleted it. Do not schedule work against R-17.

### F-13 — MEASURED (the ARM target's current state and the cost of the fold)

Run [`30676982030`](https://github.com/henols/firestarter/actions/runs/30676982030), branch
`v1.23-py32f071-integration`, 2026-08-01T01:02Z, **49 s**, all 11 steps green:

| Fact | Value |
|------|-------|
| Emitted names | `firestarter-py32f071.{elf,bin,hex,map,sha256}` — **still hyphenated**; `ad47c3b`'s rename has not landed (confirms 124 D-07's withholding) |
| ARM flash | text 27 344 + data 112 = **27 456 B** |
| ARM RAM | data 112 + bss 5 888 = **6 000 B** |
| Objects linked | 42 |
| hex SHA-256 (that run) | `d4fee7fbb6fb155569d76b5437fc667ef362f0cb2a2ee5e11c9de7540623d448` |
| Pre-existing annotation | Node.js-20 deprecation on `actions/checkout@v4` and `actions/upload-artifact@v4` — **already present**, not this phase's concern, but it means D-07's `::warning::` will not be the only annotation on the run page |

`beta-build.yml` currently runs ~1m51s–2m13s. Adding apt install + a full SDK clone (the SDK repo is
~71 MB per `gh api repos/OpenPuya/PY32F071_Firmware`, and `GIT_SHALLOW FALSE`) + the ARM build costs
**~50-90 s** on the observed evidence. Total release-job time roughly doubles to ~3-4 min. That is
acceptable and needs no caching; note it in the SUMMARY so the increase is a recorded expectation
rather than a surprise. [VERIFIED: run logs and `gh run list` durations]

### F-14 — MEASURED (D-12's premise, re-verified live on `3.0.0b14` not `3.0.0b13`)

`gh release view 3.0.0b14 --repo henols/firestarter --json assets` returns **exactly three** assets:
`firestarter_leonardo.hex` (73 347 B), `firestarter_uno.hex` (67 338 B),
`firestarter_uno328pb.hex` (67 452 B) — `isPrerelease: true`, `isDraft: false`, **no py32 asset**.
`scripts/baseline/size_baseline.json`'s `avr_targets` keys are exactly
`['leonardo', 'uno', 'uno328pb']`. The committed build-log fixtures show the on-disk paths as
`.pio/build/<env>/firestarter_<env>.hex` for all three, and `name_firmware.py:60-61` derives
`PROGNAME = "firestarter_<RURP_BOARD_NAME>"` from each env's `build_flags`, which is why env name and
asset name coincide. The three native envs produce no `.hex`, which is why a bare `pio run` does not
pollute the existing `.pio/build/**/firestarter_*.hex` glob.
[VERIFIED: `gh release view`, `size_baseline.json` parse, fixture grep, `name_firmware.py` read]

**D-12 is confirmed on stronger evidence than CONTEXT recorded** (it cited `3.0.0b13`; `3.0.0b14` is
the current tip and shows the same three).

### F-15 — CORRECTION (severity: LOW; D-10's rationale, not its design)

D-10 justifies the SDK-SHA assertion as *"catching a cache or mirror serving something else."*
`beta-build.yml:33-38`'s `actions/cache@v4` caches only `~/.cache/pip` and `~/.platformio/.cache`.
`build/py32f071/_deps` is **not cached** by anything, so the SDK is cloned fresh from GitHub on every
run and the cache scenario cannot occur. [VERIFIED: workflow read]

The assertion is still worth having, for the reasons that *do* apply: it catches a `GIT_TAG` edit
that does not match what was actually fetched, an upstream force-push behind a moved ref, and a
future contributor adding an SDK cache without re-checking the pin. Restate the rationale in those
terms rather than the cache one.

---

## Architecture Patterns

### System Architecture Diagram

```
                       OPERATOR (gated — D-04; no task may run these)
                              │
              ┌───────────────┴────────────────┐
              │ git push <throwaway>           │  fires NOTHING (F-004/D-04 verified:
              │  (forked off firmware          │  beta-build=push:[beta], py32f071=push:[beta],
              │   v1.23 milestone branch)      │  build=push:[main])
              └───────────────┬────────────────┘
                              │
              ┌───────────────▼──────────────────────────────────────────┐
              │ gh workflow run beta-build.yml                            │
              │   --ref <throwaway>                                       │
              │   -f rehearsal=true                                       │
              │   -f beta_version=3.0.0b99   ◄── F-2: MANDATORY,          │
              │                                  else the stable path     │
              │                                  writes 3.0.1             │
              └───────────────┬──────────────────────────────────────────┘
                              │  (run A = healthy;  run B = after the
                              │   planted broken-source-path commit, D-02)
                              ▼
╔═════════════ beta-build.yml · job `build` · ONE job, ordered ═════════════╗
║                                                                           ║
║  checkout(fetch-depth:0) → cache → py3.11 → codegen gates → pio test      ║
║        → pytest tests/ → ┐                                                ║
║                          │                                                ║
║        ┌─────────────────▼──────────────────────────────┐                 ║
║        │ Generate release version  (id: version)        │                 ║
║        │   .github/scripts/update_version.py            │                 ║
║        │   rewrites include/version.h                   │                 ║
║        └─────────────────┬──────────────────────────────┘                 ║
║        ┌─────────────────▼──────────────────────────────┐                 ║
║        │ git-auto-commit-action@v5  (pushes to the ref) │                 ║
║        └─────────────────┬──────────────────────────────┘                 ║
║                          │  ══ REL-01 BOUNDARY: everything ARM ══         ║
║                          │     must be BELOW this line                    ║
║        ┌─────────────────▼──────────────────────────────┐                 ║
║        │ Build PlatformIO Project  (pio run)            │                 ║
║        │   → .pio/build/{uno,uno328pb,leonardo}/        │                 ║
║        │        firestarter_<env>.hex                   │                 ║
║        └─────────────────┬──────────────────────────────┘                 ║
║        ┌─────────────────▼──────────────────────────────┐                 ║
║        │ uses: ./.github/actions/build-py32f071         │  ◄── D-06       ║
║        │   id: arm                                      │      composite: ║
║        │   continue-on-error: true   ◄── D-05 SOFT      │      runs IN    ║
║        │   [apt toolchain → cmake configure → build]    │      this job   ║
║        │   → build/py32f071/firestarter_py32f071.hex    │                 ║
║        └───────┬──────────────────────┬─────────────────┘                 ║
║                │ outcome==failure     │ outcome==success                  ║
║        ┌───────▼──────────────┐  ┌────▼────────────────────────────────┐  ║
║        │ Report missing image │  │ (a) filename == literal  [REL-04]   │  ║
║        │  ::warning:: +       │  │ (b) SDK SHA == GIT_TAG   [REL-04]   │  ║
║        │  STEP_SUMMARY        │  │     src: build/py32f071/_deps/      │  ║
║        │  reads .outcome ◄F-4 │  │          py32f071_sdk-src (F-5)     │  ║
║        │  FAILS NOTHING (D-7) │  │ (c) strings(hex) ∋ "<VER>:py32f071" │  ║
║        └───────┬──────────────┘  │                          [REL-01,F-9]│ ║
║                │                 └────┬────────────────────────────────┘  ║
║                └────────────┬─────────┘                                   ║
║        ┌────────────────────▼───────────────────────────┐                 ║
║        │ scripts/check_release_assets.py    ◄── D-11    │                 ║
║        │   required set ← size_baseline.json            │                 ║
║        │        avr_targets keys        ◄── D-12        │                 ║
║        │   HARD FAIL if any AVR hex missing/empty       │                 ║
║        │   TOLERATES py32 absence          [REL-03]     │                 ║
║        └────────────────────┬───────────────────────────┘                 ║
║        ┌────────────────────▼───────────────────────────┐                 ║
║        │ Resolve release target SHA (id: release_target)│                 ║
║        └────────────────────┬───────────────────────────┘                 ║
║        ┌────────────────────▼───────────────────────────┐                 ║
║        │ Release · softprops/action-gh-release@v2       │                 ║
║        │   files: |                                     │                 ║
║        │     .pio/build/**/firestarter_*.hex            │                 ║
║        │     build/py32f071/firestarter_*.hex  ◄── D-15 │                 ║
║        │   fail_on_unmatched_files: NEVER set  ◄── F-1  │                 ║
║        │   draft:    ${{ inputs.rehearsal }}   ◄── D-01 │                 ║
║        │   tag_name: rehearsal-<run_id> | <version>  D-3│                 ║
║        └────────────────────┬───────────────────────────┘                 ║
╚═════════════════════════════│═════════════════════════════════════════════╝
                              ▼
      draft release · assets under untagged-<hash> URLs · NO git tag (F-3)
                              │
                              ▼  evidence via `gh release view --json assets`
                    128-NONREGRESSION.md  (D-18)  ──►  Phase 130 CLOSE-02

── the LOUD half, unchanged in role (D-05) ──────────────────────────────────
  py32f071.yml · push:[beta] + PR + dispatch
    └─ uses: ./.github/actions/build-py32f071   (same composite, NO
       continue-on-error) → red and staying red when ARM breaks on beta
       └─ actions/upload-artifact (single hex, D-16) → PR-downloadable image

── the cross-repo binding, the only app-repo change (D-08b/D-09) ────────────
  firestarter_app/tests/test_<name>_host.py   @requires_fw
    ├─ parse TARGET_NAME/HEX_FILE from ../firestarter/platform/py32f071/CMakeLists.txt
    ├─ parse the expected literal from ../firestarter/.github/workflows/beta-build.yml
    └─ asset_candidates("py32f071")[0]        ── all three EQUAL
       + one non-vacuity assertion PER PARSE  (A-7)
       ⚠ SKIPS in app CI — no firmware sibling there (F-8)
```

### Recommended Project Structure

```
firestarter/                                   (firmware repo, commits FIRST — D-19)
├── .github/
│   ├── actions/                               # NEW directory — none exists today
│   │   └── build-py32f071/
│   │       └── action.yml                     # D-06: toolchain + configure + build
│   └── workflows/
│       ├── beta-build.yml                     # the fold: rehearsal input, ARM call,
│       │                                      #   report, asset gate, 2nd files: entry
│       ├── py32f071.yml                       # LOUD gate: build steps → composite call
│       └── build.yml                          # UNTOUCHED (D-13)
├── platform/py32f071/
│   ├── CMakeLists.txt                         # D-14: hyphen→underscore ×4 + comment
│   └── README.md                              # D-15: glob + corrected rationale (F-1)
├── scripts/
│   ├── check_release_assets.py                # NEW — D-11 (+ build-root seam, F-6)
│   └── baseline/size_baseline.json            # READ-ONLY input (D-12)
└── tests/
    ├── test_check_release_assets.py           # NEW — mandatory pairing (BASE-08)
    ├── test_checker_convention.py             # FLOOR 5→6, FIXTURE_FLOOR→actual (F-11)
    └── fixtures/
        ├── planted_release_assets_*/pio_build/…   # NO dot in the dir name (F-6)
        └── clean_release_assets_*/pio_build/…     # control

firestarter_app/                               (host repo, commits SECOND — D-19)
├── tests/
│   ├── test_<name>_host.py                    # NEW — D-08(b)/D-09, one module
│   ├── fw_presence.py                         # READ-ONLY: @requires_fw, fw_path
│   └── test_skip_census.py                    # READ-ONLY: confirm, do not add (D-09)
└── firestarter/firmware.py                    # READ-ONLY. FROZEN.
```

### Pattern 1 — REL-01 as an exit code, not a YAML read (F-9)

**What:** After the ARM build, assert the *published* image contains the *bumped* version string.
**When to use:** Always. It is two lines and it is the only REL-01 evidence that survives a step
reorder. Keep the YAML-order read as well — Criterion 1 names it explicitly.

```yaml
      # REL-01, mechanically. include/firestarter.h defines
      #   FW_VERSION == VERSION ":" RURP_BOARD_NAME
      # and on ARM include/rurp_platform_compat.h makes PSTR() a no-op and
      # PROGMEM empty, so "<version>:py32f071" is a plain ASCII literal in
      # .rodata. Asserting it in the PUBLISHED .hex proves the image was built
      # AFTER the update_version.py auto-commit -- a property a YAML step-order
      # read cannot keep proving once someone reorders the job.
      # NOTE: compare against steps.version.outputs.version, NEVER against
      # tag_name -- in rehearsal mode D-03 overrides tag_name by design.
      - name: Assert the py32 image carries the bumped VERSION (REL-01)
        if: steps.arm.outcome == 'success'
        run: |
          set -euo pipefail
          EXPECTED='${{ steps.version.outputs.version }}:py32f071'
          test -n "${EXPECTED%%:*}"   # non-vacuity: an empty version must FAIL
          arm-none-eabi-objcopy -I ihex -O binary \
            build/py32f071/firestarter_py32f071.hex "$RUNNER_TEMP/py32.bin"
          strings "$RUNNER_TEMP/py32.bin" | grep -Fqx -- "$EXPECTED" \
            || { echo "FAIL: '$EXPECTED' not found in the published image"; exit 1; }
          echo "PASS: image carries $EXPECTED" >> "$GITHUB_STEP_SUMMARY"
```

`grep -Fqx` requires the whole `strings` line to equal the expected token; if `.rodata` packing ever
makes that too strict, drop `-x` (keep `-F` and `-q`) rather than dropping the assertion.

### Pattern 2 — the composite action (D-06), with the two first-use traps

**What:** One definition of the ARM build, called by both workflows.
**When to use:** D-06 locks it. No `.github/actions/` exists in this repo, so both traps below are
first-use hazards.

```yaml
# .github/actions/build-py32f071/action.yml
name: Build PY32F071 firmware
description: >
  Install the GNU Arm toolchain, configure and build platform/py32f071.
  D-06: the ONLY definition of this invocation. A composite action runs in the
  CALLING job on the same runner and workspace, which is what keeps REL-01's
  "same job, after the version bump" property intact -- a reusable
  workflow_call would be a separate job with a separate checkout and would
  break REL-01 outright.
outputs:
  hex_path:
    description: Path to the emitted Intel HEX image
    value: ${{ steps.build.outputs.hex_path }}
  sdk_sha:
    description: Resolved FetchContent SDK commit SHA
    value: ${{ steps.build.outputs.sdk_sha }}
runs:
  using: composite
  steps:
    # TRAP 1: `shell:` is REQUIRED on every run step in a composite action --
    # unlike a workflow step, where the runner picks a default. Omitting it is
    # a hard error at action-load time.
    - name: Install GNU Arm toolchain and build tools
      shell: bash
      run: |
        sudo apt-get update
        sudo apt-get install -y \
          cmake ninja-build gcc-arm-none-eabi binutils-arm-none-eabi
    - name: Configure
      shell: bash
      run: |
        set -o pipefail
        cmake -S platform/py32f071 -B build/py32f071 -G Ninja \
          -DCMAKE_BUILD_TYPE=Release 2>&1 | tee configure.log
    - name: Build
      id: build
      shell: bash
      run: |
        set -o pipefail
        cmake --build build/py32f071 2>&1 | tee build.log
        # ...emit hex_path and sdk_sha to $GITHUB_OUTPUT
```

- **TRAP 1 (above):** `shell:` is *"Required if `run` is set"* for composite steps.
- **TRAP 2:** `continue-on-error: true` goes on the **call site in `beta-build.yml` only** (D-05),
  never inside the action — otherwise the LOUD `py32f071.yml` copy inherits the containment and
  D-05's whole loud/soft split collapses silently. `runs.steps[*].continue-on-error` *is* supported
  inside composite actions, which is precisely why this is easy to get wrong.
- **Known edge case, does not bite here:** `actions/runner#3510` reports that `continue-on-error` at
  a composite call site may fail to suppress an error raised by a *node* action nested inside
  another composite. This action contains only `run:` steps, so the caveat does not apply — but note
  it so a future addition of a nested `uses:` step is recognised as a containment risk.

### Pattern 3 — the AVR-assets checker (D-11/D-12), in the house shape

**What:** A stdlib-only `scripts/check_*.py` with a hand-rolled argv parser, an explicit exit
taxonomy, `PASS:`/`FAIL:` output prefixes, an env seam for its inputs, and a paired pytest that
invokes it as a real subprocess against committed fixtures.
**When to use:** D-11 makes it mandatory; `test_checker_convention.py` enforces the triple.

The closest analog is `scripts/check_size_baseline.py` + `tests/test_check_size_baseline.py` +
`tests/fixtures/planted_size_baseline_*`. Copy its conventions exactly:

| House convention | Where it is established | Applies to the new checker as |
|------------------|-------------------------|-------------------------------|
| Long module docstring naming phase, plan, requirements, decisions, exit taxonomy, and an explicit **"Anti-hollow contract"** paragraph naming the paired test | `check_size_baseline.py:1-70` | Same, naming REL-03/REL-02 and D-11/D-12 |
| Manual argv parser, **no argparse** | `check_size_baseline.py:330` ("house convention") | Same |
| Exit `0` clean / `1` violation / `2` tool-or-CLI failure, with the taxonomy documented in the docstring | `check_size_baseline.py:40-52` | `0` all required AVR hexes present and non-empty; `1` any missing or empty, **or** the `avr_targets` key set parsed empty (non-vacuity); `2` the baseline JSON is unreadable/unparseable, or the argv is malformed |
| Input path read through an env seam with a committed default | `FIRESTARTER_SIZE_BASELINE`, `check_size_baseline.py:95-97` | Reuse `FIRESTARTER_SIZE_BASELINE` for the baseline **and add `FIRESTARTER_PIO_BUILD_ROOT` for the build root** (F-6 makes the second one mandatory) |
| A "never-vacuous" guard that fails when zero items were compared | `check_size_baseline.py` return-1 path; `test_...::test_never_vacuous_with_no_logs_and_no_rebuild` | `1` when `avr_targets` yields zero keys — a gate that requires nothing must not print `PASS:` |
| Paired test invokes the script via list-form `subprocess.run([sys.executable, CHECKER, ...])`, `cwd=REPO_ROOT`, **never `shell=True`, never an in-process import** | `test_check_size_baseline.py:121-133` | Same |
| A **seam-precedence** test proving the env var is genuinely read | `test_check_size_baseline.py` coverage item 7 | One per seam — including the new build-root seam |
| Fixture prefixes: `planted_*` must fail, `clean_*` must pass; each planted derived from a real source by **one stated edit** | `tests/fixtures/README.md` | `planted_release_assets_missing_<env>/pio_build/…` (two of three hexes), plus a zero-byte variant (F-1: a 0-byte file still uploads), plus `clean_release_assets_all_three/` |
| Fixture presence verified with `git ls-files`, **never** `git add`'s exit code | `tests/fixtures/README.md` | Mandatory here (F-6 makes silent ignoring the likely failure) |
| Floors raised in the same commit | `test_checker_convention.py:53-66` docstring | `FLOOR` 5→6, `FIXTURE_FLOOR` 10→actual (F-11) |

The checker's own logic, stated once so the plan does not re-derive it: read `avr_targets` keys from
the baseline JSON → **fail 1 if the key set is empty** → for each key `k`, require
`<build_root>/<k>/firestarter_<k>.hex` to exist with size > 0 → assert **exactly** that set, nothing
missing → **never** mention or require the py32 image (its absence must be tolerated, which is why
D-11 rejected one do-everything checker).

### Pattern 4 — the cross-repo three-way filename gate (D-08b/D-09)

**What:** The app-side binding. **When to use:** D-09 locks the shape. Copy
`firestarter_app/tests/test_py32_flash_map_host.py` structurally.

Structural elements to reproduce, each one already load-bearing in the 127 module:

1. **Import the seam, never re-derive it:**
   `from tests.fw_presence import FW_ROOT, fw_path, requires_fw`.
2. **Resolve every firmware path through `fw_path(...)`**, never by hand-building a relative path.
   `fw_path` raises `MissingScanTargetError` when the repo is present but the file is not — so a
   Phase-129 rename becomes a hard failure, never a silent skip (A-7).
3. **`@requires_fw` is the ONLY skip marker.** No module-local `skipif` keyed on a scan-target proxy.
4. **A separate, first-running non-vacuity test per parse.** The 127 module's `_assert_non_vacuous`
   runs before *any* value comparison and its message contains the phrase "vacuously true". D-09
   requires **one per parse** — the CMake parse and the workflow parse are two independent regexes,
   so two independent non-vacuity assertions. Assert the extracted names are non-empty *and* match
   `^firestarter_[a-z0-9_]+\.hex$`, so a regex that captures whitespace fails loudly.
5. **A planted-mutation RED demonstration** written to `tmp_path`, reached by monkeypatching the
   module's path constant, with the real file's `git hash-object` blob SHA asserted unchanged before
   and after **and** `git status --porcelain` of `FW_ROOT` asserted empty. See F-16 below — that last
   assertion is a precondition, not just a check.
6. **`git` resolved fail-closed** via `shutil.which("git")` with an `assert ... is not None` — a
   missing `git` must fail the suite, never skip it.
7. **No new `ALLOWED_SKIP_REASONS` entry.** D-09 already resolved this (127 D-14): `FW_ABSENT_REASON`
   is imported at `test_skip_census.py:92` and matching is by prefix. **Confirm, do not add** — and
   confirm by *running* `tests/test_skip_census.py`, not by reading it.

### F-16 — the clean-tree precondition hidden inside Pattern 4

`test_py32_flash_map_host.py::test_planted_mutated_config_origin_is_detected` ends with
`assert _git_porcelain(FW_ROOT) == ""`. If the new module copies that shape — and D-08(b) says copy
it — then **the app-side test is RED whenever the firmware working tree is dirty.** D-19's ordering
(firmware commits first, app second) already delivers this, but it upgrades D-19 from a preference to
a hard precondition: the plan must not run the app test while any firmware edit is uncommitted, and
the verification step should check `git -C ../firestarter status --porcelain` is empty *before*
invoking pytest, so a red result is attributed correctly. [VERIFIED: source read, lines 376-380]

### Anti-Patterns to Avoid

- **Repeating the glob-vs-literal rationale.** It is false (F-1). A comment or README line asserting
  it would ship a wrong explanation next to correct code — the Phase 122 C-5 shape.
- **Keying D-07's report on `steps.<id>.conclusion`.** It is `success` for a failed
  `continue-on-error` step, so the report can never fire (F-4). Phases 118 and 124 both had to unwind
  gates of exactly this shape.
- **`continue-on-error` inside the composite action.** It would silently disarm the LOUD
  `py32f071.yml` gate and collapse D-05.
- **Setting `fail_on_unmatched_files: true`** "for stricter CI". It converts the contained
  broken-ARM case into a hard release failure — a direct REL-03 violation.
- **A fixture tree with a literal `.pio` directory.** Silently ignored by `.gitignore` line 1 (F-6),
  and `git add` reports success while staging nothing.
- **Dispatching the rehearsal with `beta_version` blank.** Takes the stable path and writes `3.0.1`
  (F-2).
- **Dispatching without `rehearsal=true`.** Publishes a real public prerelease and a real tag — this
  has already happened once, from this exact route (F-7).
- **Asserting the emitted filename against a value imported from `asset_candidates()` on the
  firmware side.** The firmware repo cannot import the host package; D-08(a) is explicitly a
  *transcription* and D-08(b) is what binds it. Do not blur them.
- **Lowering a floor in `test_checker_convention.py`** to make it green. Its docstring says outright
  that a red floor means something went missing.
- **Claiming CI enforces the cross-repo binding.** It skips in app CI (F-8).
- **Any wording implying the published image runs, boots, or installs.** No PCB exists. The permitted
  claim is exactly one sentence wide: *the asset publishes.*

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Publishing files as release assets | A `gh release upload` shell step, or an `actions/upload-artifact` + follow-up job | The existing `softprops/action-gh-release@v2` `files:` list | Already the repo's release mechanism; artifacts are a different API that expires in 90 days, needs auth, and always arrives as a ZIP (`ad47c3b` point 1) |
| "Don't fail the release when ARM breaks" | Wrapping cmake in `|| true`, or `if: ${{ ... }}` juggling | `continue-on-error: true` on the composite call site (D-05) + `steps.<id>.outcome` for the report (D-07) | `|| true` also hides the failure from `outcome`, so the D-07 report could never fire — it converts a soft failure into an invisible one |
| "Warn instead of fail on a missing asset" | Custom pre-flight `test -f` logic before the Release step | The action's default `fail_on_unmatched_files: false` (F-1) | The behaviour already exists; the only work is *not* overriding it, plus a comment saying so |
| Duplicating the cmake invocation in two workflows | Copy-paste + a parity checker | A composite action (D-06) | Eliminates the drift class instead of detecting it; and the `beta-build.yml` copy is `continue-on-error`, so drift there fails silently |
| Knowing which AVR assets are required | Three hardcoded filenames | `size_baseline.json` `avr_targets` keys (D-12) | A literal rots in a milestone whose premise is files moving; a fourth AVR target updates the gate for free |
| An inline YAML asset check | Three `test -s` lines in the workflow | `scripts/check_release_assets.py` + paired pytest + planted fixture (D-11) | *"Demonstrably fails"* is the requirement's own wording; a YAML line is unprovable outside a dispatch, and BASE-08 mechanically requires the triple |
| Resolving the SDK source directory | Hardcoding a guessed path | `build/py32f071/_deps/py32f071_sdk-src`, measured from run 30676982030 (F-5), with a fail-loud existence check | CMake's documented default *and* an observed run agree — but a silent empty-string SHA compared against an empty `GIT_TAG` is the A-7 shape |
| Cross-repo firmware presence detection | A module-local `Path(...).exists()` proxy | `tests/fw_presence.py`'s `@requires_fw` + `fw_path()` | A-7: seven modules once derived "firmware absent" from scan-target proxies; a rename flipped five gate legs PASS→SKIP at exit 0 with a false reason |
| Proving the image was built after the version bump | Reading YAML step order and trusting it | `strings` over the objcopy'd published `.hex` (Pattern 1) | The version string is genuinely in `.rodata` (F-9); an assertion on the shipped bytes cannot be silently reordered away |

**Key insight:** every "hand-rolled" alternative in this table is *cheaper to write and impossible to
prove*. That is the trade this milestone's ledger exists to refuse. The phase's whole value is that
four claims become exit codes: AVR assets present, filename equal, SDK pin honoured, and (with
Pattern 1) the image carries the bumped version.

---

## Runtime State Inventory

This phase edits CI configuration and adds two test/checker files. It renames build *outputs* (the
hyphen→underscore change, D-14), which is a rename in the sense this inventory exists to catch, so
all five categories are answered explicitly.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| **Stored data** | **None.** No database, no datastore, no collection name, no user_id anywhere in scope. The only "stored" artifacts are GitHub release assets, and the existing three AVR names are unchanged (F-14). The ARM name changes from `firestarter-py32f071.*` to `firestarter_py32f071.*`, but **no release has ever carried either name** — `3.0.0b14` and `3.0.0b13` both publish exactly three AVR hexes and no py32 asset. There is no historical asset to migrate. | None — verified by `gh release view 3.0.0b14 --json assets` |
| **Live service config** | **GitHub Actions run history and existing artifacts.** Prior `py32f071.yml` runs uploaded an **artifact** named `firestarter-py32f071` containing hyphenated filenames (run 30676982030 confirms). Those artifacts live in GitHub's storage, not git, and expire on the repo's retention policy. They are **not** release assets and no host code path reads them. | None — code edit only. Do not attempt to rename historical artifacts; note in the SUMMARY that pre-rename artifacts carry the old names so a future reader downloading run 30676982030 is not confused |
| **OS-registered state** | **None.** No Task Scheduler entry, no pm2 process, no systemd unit, no launchd plist references anything in scope. The only "registration" is the GitHub-side workflow registry (`gh workflow list` → IDs 280350856 / 103010485 / 316560577), which is keyed on the workflow **file path**, and no workflow file is renamed by this phase. | None — verified by `gh workflow list` |
| **Secrets and env vars** | `secrets.GITHUB_TOKEN` (built-in, already used; `beta-build.yml:97-103` records why no PAT is needed). No new secret. **Two NEW env seam names are introduced by the checker**: `FIRESTARTER_PIO_BUILD_ROOT` (new, F-6) and a reuse of the existing `FIRESTARTER_SIZE_BASELINE`. Both are read with committed defaults, so an unset value is correct behaviour, not a break. The `BETA_VERSION` env var already exists and is unchanged — but see F-2: its *value* on a rehearsal dispatch is load-bearing. | Document both seam names in the checker docstring and in the plan; no secret change |
| **Build artifacts / installed packages** | **Yes — one real item.** `build/py32f071/` in any local or CI workspace will contain **both** the old hyphenated and the new underscored outputs after an incremental build across the rename, because CMake will not delete the previous `TARGET_NAME`'s products. A stale `firestarter-py32f071.hex` sitting beside a fresh `firestarter_py32f071.hex` is harmless for the release glob (`firestarter_*.hex` requires the underscore) but would make a hand-inspection of the build dir confusing. CI is unaffected — each run starts from a clean workspace and `build/py32f071` is not cached (F-15). Also present: `firestarter/scripts/__pycache__/` and `firestarter/tests/__pycache__/`, both gitignored. | CI: nothing. Local: state in the SUMMARY that a local rebuild across the rename should `rm -rf build/py32f071` first. **No data migration** — a code edit only |

**The canonical question, answered:** after every file in both repos is updated, the only runtime
systems still carrying the old string are (a) GitHub's stored Actions **artifacts** from pre-rename
runs, which nothing reads and which expire on their own, and (b) a stale local
`build/py32f071/firestarter-py32f071.*` if someone rebuilds incrementally. Neither requires a
migration task.

---

## Common Pitfalls

### Pitfall 1 — `fail_on_unmatched_files` looks like a hardening win and is a REL-03 violation
**What goes wrong:** A future contributor (or a plan-checker optimising for strictness) adds
`fail_on_unmatched_files: true` to the `Release` step. The next broken ARM build fails the release
outright and no AVR asset publishes.
**Why it happens:** The requirement's own text implies the glob is what provides the tolerance
(F-1), so the *actual* mechanism — the input's `false` default — is invisible in the YAML. Nothing
in the file records that its absence is deliberate.
**How to avoid:** A comment on the `Release` step naming REL-03 and stating that the omission is
load-bearing. Optionally a grep assertion in `check_release_assets.py`'s paired test that
`beta-build.yml` does not contain `fail_on_unmatched_files` — cheap, and it fails closed.
**Warning signs:** Any PR touching the `Release` step that mentions "strict" or "fail fast".

### Pitfall 2 — a `.pio` fixture directory that is silently never committed
**What goes wrong:** `check_release_assets.py`'s planted fixture is created on disk, the paired test
passes locally, `test_checker_convention.py` passes locally, and the commit contains no fixture.
Everyone else's checkout is red — or worse, the convention test passes for them too because the
missing fixture makes the glob match a different entry.
**Why it happens:** `.gitignore:1` is the bare pattern `.pio`, which matches at any depth, and
`git add` exits 0 while staging nothing (already documented in `tests/fixtures/README.md` for the
`.git`-component case).
**How to avoid:** Never name a fixture directory `.pio`. Use the `FIRESTARTER_PIO_BUILD_ROOT` seam
with `pio_build/` fixtures, and verify with `git ls-files tests/fixtures/` — never with `git add`'s
exit code.
**Warning signs:** `git status` shows nothing after adding fixture files;
`git check-ignore -v <path>` prints a match.

### Pitfall 3 — a rehearsal that writes a stable version and nobody notices
**What goes wrong:** The rehearsal dispatch leaves `beta_version` blank; `include/version.h` goes
from `3.0.0b14` to `3.0.1`; the evidence artifact records a stable version string as proof of a
*beta* release fold; and if the throwaway branch is ever merged the regression travels with it.
**Why it happens:** `is_beta_mode()` keys on `GITHUB_REF == refs/heads/beta` or a non-empty
`BETA_VERSION`, and the dispatch input defaults to blank (F-2). Nothing in the workflow surfaces
which path was taken.
**How to avoid:** Always dispatch with `-f beta_version=3.0.0b99`. Additionally, the REL-01
assertion in Pattern 1 makes the actual computed string visible in `$GITHUB_STEP_SUMMARY`, so the
wrong path is at least *observable*. Verify the throwaway branch is deleted, not merged.
**Warning signs:** `Generate release version` logs `New versin created: 3.0.1` (note the upstream
typo, useful as a grep anchor) instead of a `bNN` string.

### Pitfall 4 — a hollow report keyed on `conclusion`
**What goes wrong:** The D-07 report step never fires. A release silently ships without the py32
asset and the run page says nothing.
**Why it happens:** `conclusion` is `success` for a failed `continue-on-error` step (F-4). It is the
more intuitive-sounding word.
**How to avoid:** `if: steps.<id>.outcome == 'failure'`. Prove it in run B — the whole point of
D-02's second dispatch is that the report is *observed* firing, not asserted to fire.
**Warning signs:** Run B is green, publishes three AVR assets, and has **no** `::warning::`
annotation and no summary line. That is a passing REL-03 and a failing D-07 simultaneously.

### Pitfall 5 — composite action missing `shell:`
**What goes wrong:** The action fails to load with an unhelpful error; both workflows break at once.
**Why it happens:** Workflow `run:` steps get a default shell; composite `run:` steps do not —
`shell` is *"Required if `run` is set"*. No `.github/actions/` exists in this repo, so nobody here
has hit it before.
**How to avoid:** `shell: bash` on every `run:` step in `action.yml`.
**Warning signs:** Both `py32f071.yml` and `beta-build.yml` red on the first push, at the ARM step,
before any compilation.

### Pitfall 6 — a green cross-repo test that actually skipped
**What goes wrong:** The D-08(b) binding is recorded as proven; it never ran.
**Why it happens:** `@requires_fw` skips when `../firestarter/.git` is absent — always true in app
CI (F-8) — and pytest's default output does not distinguish a skip from a pass at a glance. This is
A-7 verbatim: a firmware rename once flipped five legs PASS→SKIP at exit 0 with a false reason.
**How to avoid:** Run `pytest tests/<module>.py -q -rs` locally and assert the `-rs` skip report
contains **no** FW-absent line; record the observed pass count. State in
`128-NONREGRESSION.md` that CI skips it.
**Warning signs:** A `s` in the pytest progress line; `-rs` output naming
`firestarter firmware checkout absent`.

### Pitfall 7 — the app test red because the firmware tree is dirty
**What goes wrong:** The new app-side test fails on `assert _git_porcelain(FW_ROOT) == ""` and the
failure is misread as a filename mismatch.
**Why it happens:** The 127 module the plan is told to copy asserts the firmware working tree is
clean (F-16), because it plants a mutated copy and must prove it never touched the source of truth.
**How to avoid:** Honour D-19 strictly — all firmware commits land first. Check
`git -C ../firestarter status --porcelain` is empty *before* invoking the app test.
**Warning signs:** An assertion message about "the firmware repo's working tree is no longer clean".

### Pitfall 8 — a non-vacuity assertion that is itself vacuous
**What goes wrong:** D-09's three-way equality passes because all three parses returned the empty
string. Two empty strings compare equal.
**Why it happens:** A rename makes a regex miss; the parse returns `None`/`""`; the comparison is
trivially true.
**How to avoid:** One non-vacuity assertion **per parse**, running *before* any comparison, and
strong enough to be meaningful: non-empty **and** matching `^firestarter_[a-z0-9_]+\.hex$`. Plus a
RED demonstration test that feeds the parser text with no match and asserts the guard raises.
**Warning signs:** A three-way equality test with only one `assert x` guard, or a guard that merely
checks `is not None`.

---

## Code Examples

### D-07's report step (reads `outcome`, F-4)

```yaml
      # D-07. Reads .outcome, NOT .conclusion: for a continue-on-error step
      # GitHub sets outcome=failure but conclusion=success, so a
      # conclusion-keyed condition could never fire (Phases 118/124 both had to
      # unwind gates of exactly that shape).
      # No `if: always()`: continue-on-error keeps the job on the success path,
      # so a plain conditional step already runs; always() would only add a
      # cancelled-job case this condition does not match anyway.
      - name: Report a missing PY32F071 image
        if: steps.arm.outcome == 'failure'
        run: |
          MSG='PY32F071 image not produced — this release carries no py32f071 asset.'
          echo "::warning::${MSG}"
          echo "### PY32F071" >> "$GITHUB_STEP_SUMMARY"
          echo "${MSG}" >> "$GITHUB_STEP_SUMMARY"
          # Fails nothing, by design (D-05/D-07): py32f071.yml says WHAT BROKE;
          # this says WHAT THE RELEASE LACKS.
```

### D-10's SDK-pin assertion (path measured, F-5; non-vacuity guards)

```yaml
      # REL-04, D-10. Source dir measured on a real run, not guessed:
      # CI run 30676982030 (job 91306188205) shows ninja object paths under
      # _deps/py32f071_sdk-src/ relative to build/py32f071, matching CMake's
      # documented default <binary_dir>/_deps/<lowercaseName>-src.
      # The SDK is NOT cached by anything (actions/cache covers only ~/.cache/pip
      # and ~/.platformio/.cache), so this asserts the declared pin was honoured
      # by the fetch -- it catches a GIT_TAG edit or a moved upstream ref.
      - name: Assert and log the resolved SDK commit SHA (REL-04)
        if: steps.arm.outcome == 'success'
        run: |
          set -euo pipefail
          SRC=build/py32f071/_deps/py32f071_sdk-src
          test -d "$SRC" || { echo "FAIL: $SRC missing — FetchContent layout changed"; exit 2; }
          RESOLVED=$(git -C "$SRC" rev-parse HEAD)
          PINNED=$(sed -n 's/^[[:space:]]*GIT_TAG[[:space:]]\+\([0-9a-f]\{40\}\)[[:space:]]*$/\1/p' \
                     platform/py32f071/CMakeLists.txt)
          # Non-vacuity, both sides: two empty strings compare equal.
          printf '%s' "$PINNED"   | grep -Eq '^[0-9a-f]{40}$' \
            || { echo "FAIL: no 40-hex GIT_TAG parsed from CMakeLists.txt"; exit 2; }
          printf '%s' "$RESOLVED" | grep -Eq '^[0-9a-f]{40}$' \
            || { echo "FAIL: rev-parse returned no SHA"; exit 2; }
          test "$RESOLVED" = "$PINNED" \
            || { echo "FAIL: SDK $RESOLVED != pinned $PINNED"; exit 1; }
          echo "PY32F071 SDK commit: \`$RESOLVED\` (pin honoured)" >> "$GITHUB_STEP_SUMMARY"
```

### D-08(a)'s filename equality (a transcription, and labelled as one)

```yaml
      # REL-04 / D-08(a). This is deliberately a TRANSCRIPTION: the firmware
      # repo cannot import the host package, so the literal below is checked
      # against the real function by firestarter_app's own test (D-08(b)),
      # which is where the binding actually lives.
      # Source of the literal: firestarter_app/firestarter/firmware.py:116-131
      #   asset_candidates("py32f071")[0] == "firestarter_py32f071.hex"
      - name: Assert the emitted asset filename (REL-04)
        if: steps.arm.outcome == 'success'
        run: |
          set -euo pipefail
          EXPECTED=firestarter_py32f071.hex
          MATCHES=(build/py32f071/firestarter_*.hex)
          test "${#MATCHES[@]}" -eq 1 \
            || { echo "FAIL: expected exactly one hex, got ${MATCHES[*]}"; exit 1; }
          ACTUAL=$(basename "${MATCHES[0]}")
          test "$ACTUAL" = "$EXPECTED" \
            || { echo "FAIL: emitted '$ACTUAL' != '$EXPECTED'"; exit 1; }
          echo "PASS: emitted $ACTUAL"
```

*(Note the `${#MATCHES[@]}` check: an unmatched bash glob expands to the literal pattern, so without
it a missing hex would set `ACTUAL` to `firestarter_*.hex` and produce a confusing mismatch message
rather than a clear "no image" one. `shopt -s nullglob` is the alternative.)*

### The `Release` step after the fold

```yaml
      - name: Release
        uses: softprops/action-gh-release@v2
        with:
          # Two entries: PlatformIO writes under .pio/build/, CMake under
          # build/py32f071/. One glob cannot cover both trees.
          files: |
            .pio/build/**/firestarter_*.hex
            build/py32f071/firestarter_*.hex
          # `fail_on_unmatched_files` is deliberately UNSET (its default is
          # false). REL-03 requires a broken ARM build to leave the py32 asset
          # simply ABSENT rather than failing the release. Setting it to true
          # would violate REL-03 directly.
          # Correction on the record: the action makes NO glob-vs-literal
          # distinction -- src/util.ts unmatchedPatterns() globs every entry and
          # src/run.ts warns-or-throws purely on this input. The glob above is
          # chosen for rename-resilience, not for failure semantics.
          tag_name: ${{ inputs.rehearsal && format('rehearsal-{0}', github.run_id) || steps.version.outputs.version }}
          target_commitish: ${{ steps.release_target.outputs.sha }}
          draft: ${{ inputs.rehearsal }}
          prerelease: true
          make_latest: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

*(Planner note: `inputs.rehearsal` in a `workflow_dispatch`-only context is `github.event.inputs.rehearsal`
on a `push` trigger — a boolean `workflow_dispatch` input is absent on a `push` event, so guard with
`${{ github.event.inputs.rehearsal == 'true' }}` or a `type: boolean` input plus an `env:` normalisation
step. Verify the exact expression against a rehearsal run; a `push: [beta]` run must resolve
`draft` to false. **This is the one YAML expression in the phase that should be observed in run A
rather than reasoned about** — a `draft: true` leaking onto a `beta` push would silently stop
publishing real betas.)*

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `actions/upload-artifact` with 10 files as the py32 delivery mechanism | A single `.hex` published as a **release asset**, plus a single-file artifact retained for PR builds (D-16) | `ad47c3b` (2026-07-28, unlanded) | Assets are a different API: no auth, no 90-day expiry, no ZIP wrapper. The host installer reads assets |
| Hyphenated `firestarter-py32f071.*` | Underscored `firestarter_py32f071.*` | `ad47c3b`, landing in this phase (D-14) | Matches `asset_candidates()` and the existing `firestarter_*.hex` glob shape |
| `FetchContent_Populate(<name>)` single-arg form | `FetchContent_MakeAvailable()` | CMake **3.30** deprecated the old form (`CMP0169`) | `CMakeLists.txt:22` uses the deprecated form. **Out of scope** — record only; changing it is a build-behaviour change (D-17's spirit) |
| Node 20 actions | Node 24 | GitHub deprecation, Sept 2025 | `actions/checkout@v4` and `actions/upload-artifact@v4` already emit a deprecation annotation on every run (F-13). Pre-existing; not this phase's concern, but it means D-07's `::warning::` will share the annotation list |

**Deprecated/outdated:**
- The glob-vs-literal justification for REL-02 — never true of this action at any version in its
  current source (F-1).
- R-17's `write_checksums.cmake` concern — the file is gone (F-12).
- CONTEXT's "fourth native env" (F-10) — it is the third native env / sixth env.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `${{ inputs.rehearsal }}` / `${{ github.event.inputs.rehearsal }}` resolves to falsy on a `push: [beta]` event, so a real beta push publishes a non-draft release | §Code Examples, `Release` step | **HIGH.** A `draft: true` leaking onto a `beta` push would silently stop publishing real betas. **Mitigation: this is the one expression to confirm by observation** — run A is dispatched (rehearsal true, draft expected), and the next real `beta` push is Phase 130's, which is gated anyway. Consider an explicit `env:` normalisation step whose value is echoed to the step summary so the resolved boolean is visible in every run |
| A2 | `strings` finds `"<version>:py32f071"` as one whole line in the objcopy'd image | §Pattern 1 | LOW. `-Os` and `--gc-sections` do not split a referenced string literal, and `PSTR` is a no-op on ARM (F-9 verified the macro chain), but the *packing* of `.rodata` was not observed. Mitigation: drop `grep`'s `-x` if the whole-line form proves too strict; the `-F -q` core assertion stands either way. Falsifiable in run A at zero cost |
| A3 | A composite action's `run:` steps see the same `$GITHUB_WORKSPACE` and the checkout performed by the calling job | §Pattern 2 | LOW. Documented and corroborated (ADR 0549 + `github.action_path` semantics), and this is D-06's core premise. Falsified immediately by run A if wrong — cmake would not find `platform/py32f071` |
| A4 | `gh workflow run beta-build.yml --ref <throwaway>` picks up the `rehearsal` input as defined **on the throwaway branch**, not on some other ref | §F-7 | MEDIUM. Precedent run 30199560282 proves dispatch from a non-default branch works, but that run's workflow file had no *new* input. If GitHub validates inputs against a different ref, the dispatch errors with "unexpected input" — a loud, immediately-diagnosable failure, not a silent one. Mitigation: try it; if it errors, the fallback is to push the workflow change to `beta`… which is Phase 130's gate, so the real fallback is to dispatch with no new input and set `draft` via a different mechanism. Flag this to the operator before the first dispatch |
| A5 | `FIXTURE_FLOOR` should be raised to the true post-phase count rather than left at 10 | §F-11 | LOW. `test_checker_convention.py`'s docstring mandates raising both floors in the same commit; the drift (10 vs 13) means the mandate was not followed by 124/126. Correcting it is in-spirit but is a judgement call the operator may prefer to defer |
| A6 | The `.hex` → binary conversion for Pattern 1 needs no `--gap-fill`/`--pad-to` | §Pattern 1 | LOW. `objcopy -I ihex -O binary` produces a sparse image whose bytes still contain the literal. Falsifiable in run A |

**Every other factual claim in this document is tagged `[VERIFIED: …]` or `[CITED: …]` inline** and
was confirmed this session by a source read, a real CI run log, a `gh` API query, or a command
executed in the devcontainer.

---

## Open Questions

1. **How is `rehearsal` typed, and does it resolve correctly on a `push` event?** (A1/A4)
   - *What we know:* `workflow_dispatch` inputs are absent on `push` events. A `type: boolean` input
     yields a real boolean on dispatch and nothing on push. The existing `beta_version` input is
     read via `env: BETA_VERSION: ${{ github.event.inputs.beta_version }}`, which is the string-typed
     pattern already in the file.
   - *What's unclear:* Whether the planner should use `inputs.rehearsal` (newer, works for
     `workflow_dispatch`/`workflow_call`) or `github.event.inputs.rehearsal` (string, `'true'`/absent),
     and how `draft:` coerces an empty string.
   - *Recommendation:* Use `type: boolean` with `default: false`, normalise once into a job-level
     `env` var, echo the resolved value to `$GITHUB_STEP_SUMMARY` in every run, and **confirm on run
     A** that `draft` was true. Add a comment stating that a `beta` push must resolve it false.

2. **Should the `objcopy`/`strings` REL-01 assertion (Pattern 1) be in scope?**
   - *What we know:* Criterion 1's stated method is a YAML read; the mechanical form is ~6 lines,
     uses tools already installed, and is the only REL-01 evidence that survives a reorder (F-9).
   - *What's unclear:* Whether the operator considers it scope creep against a criterion that names
     a different method.
   - *Recommendation:* Include it **in addition to** the YAML read. It carries no new dependency, no
     new file, and no behaviour change — and it converts the phase's weakest claim into an exit code,
     which is the standing operator preference (123-CONTEXT).

3. **Does `check_release_assets.py` also assert the *absence* of `fail_on_unmatched_files`?**
   - *What we know:* F-1 makes that omission the real REL-03 mechanism. A grep assertion in the
     paired pytest is ~5 lines and fails closed.
   - *What's unclear:* Whether pinning a workflow property belongs in a checker whose subject is
     build outputs.
   - *Recommendation:* Put it in `tests/test_check_release_assets.py` as a separate test function
     (not in the checker itself), so the checker stays single-purpose per D-11's rejection of a
     do-everything script, while the invariant still has a test.

4. **`FIXTURE_FLOOR`: raise to 14, or only `FLOOR` to 6?** (A5)
   - *Recommendation:* Raise both, and note the pre-existing 10-vs-13 drift in the commit message so
     the correction is attributable rather than looking like an unrelated change.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `git` | everything | ✓ | (on PATH) | — |
| `python3` | the checker + both test suites | ✓ | 3.12 in the devcontainer (CI uses 3.11) | — |
| `pytest` | both paired suites | ✓ | firmware `tests/` and app `.[test]` both run green this session | — |
| `gh` CLI, authenticated | D-04's gated dispatches; all evidence collection | ✓ | scopes `gist, read:org, repo, workflow` — `workflow` is what `gh workflow run` needs | — |
| `arm-none-eabi-gcc` / `cmake` / `ninja` | building the ARM target locally | ✗ | — | **CI-only.** Every ARM claim cites a workflow run URL + commit SHA. This is a standing v1.23 constraint, not new |
| `arm-none-eabi-objcopy` / `strings` | Pattern 1's REL-01 assertion | ✗ locally / ✓ on CI | — | CI-only, same as above. `binutils-arm-none-eabi` is already in the composite action's apt line |
| A PY32F071 board | proving the image runs | ✗ | — | **None. No fallback exists.** The permitted claim is exactly one sentence wide: *the asset publishes* |

**Missing dependencies with no fallback:**
- **PY32F071 silicon.** Nothing in this phase may claim the image runs, boots, or installs. D-18's
  artifact must carry that non-claim explicitly for Phase 130's CLOSE-02 ledger.

**Missing dependencies with fallback:**
- **The whole ARM toolchain.** Fallback is CI, exercised by the two gated dispatches. Every ARM
  number in any plan or SUMMARY must cite a run URL + SHA, never a local measurement.

---

## Validation Architecture

`workflow.nyquist_validation` is **absent** from `.planning/config.json` → treated as enabled.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (both repos). Firmware: `firestarter/tests/` (no `conftest.py` anywhere — a recorded house rule). App: `firestarter_app/tests/` with `tests/conftest.py` (`collect_ignore`) |
| Config file | Firmware: none for `tests/` (PlatformIO's `platformio.ini` governs only `test/`, which is invisible to these). App: `pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | Firmware: `cd firestarter && python3 -m pytest tests/test_check_release_assets.py tests/test_checker_convention.py -q` (~1 s). App: `cd firestarter_app && python3 -m pytest tests/test_<new>_host.py -q -rs` (~1 s) |
| Full suite command | Firmware: `python3 -m pytest tests/ -v` (what `beta-build.yml:66` runs) **plus** `pio test -e native` and `pio test -e native_nodevtools`. App: `python3 -m pytest tests/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REL-01 | ARM steps are positioned after the version-bump auto-commit in the same job | static (YAML order) | Read `beta-build.yml`; optionally a pytest asserting the ARM step's line index > the `git-auto-commit-action` line index | ❌ Wave 0 (optional; Criterion 1 accepts a read) |
| REL-01 | The published image carries `steps.version.outputs.version` | CI assertion (F-9/Pattern 1) | in-workflow `strings` gate; observed in run A | ❌ Wave 0 |
| REL-02 | `firestarter_py32f071.hex` present as a release **asset** | CI + API evidence | `gh release view <rehearsal-tag> --json assets` on run A's draft | ❌ Wave 0 (evidence, not a test) |
| REL-02 | `fail_on_unmatched_files` is never set | unit | `pytest tests/test_check_release_assets.py -k unmatched -x` (grep over `beta-build.yml`) | ❌ Wave 0 |
| REL-03 | AVR-assets checker exits non-zero on a planted missing/empty hex | unit (subprocess + fixture) | `pytest tests/test_check_release_assets.py -x` | ❌ Wave 0 |
| REL-03 | Required set derived from `avr_targets`; empty key set fails (non-vacuity) | unit | same module, dedicated test | ❌ Wave 0 |
| REL-03 | The build-root seam is genuinely read | unit (seam precedence) | same module, dedicated test | ❌ Wave 0 |
| REL-03 | A broken ARM build still publishes three AVR assets | CI evidence | run B's asset list via `gh release view --json assets` | ❌ Wave 0 (evidence) |
| REL-04 | Emitted basename == the literal | CI assertion | in-workflow; observed in run A | ❌ Wave 0 |
| REL-04 | Three-way filename equality, one non-vacuity assertion per parse | unit (cross-repo) | `pytest tests/<new>_host.py -q -rs` **in the app repo** | ❌ Wave 0 |
| REL-04 | Resolved SDK SHA == `GIT_TAG`, both 40-hex | CI assertion | in-workflow; observed in run A | ❌ Wave 0 |
| BASE-08 | The new checker satisfies the convention triple with raised floors | meta | `pytest tests/test_checker_convention.py -q` | ✅ exists — must stay green after the floor bump |
| D-09 | No new `ALLOWED_SKIP_REASONS` entry is needed | regression | `pytest tests/test_skip_census.py -q` (app) | ✅ exists — **confirm by running**, do not read |

### Sampling Rate

- **Per task commit:** firmware — `python3 -m pytest tests/ -q`; app — `python3 -m pytest tests/ -q`.
  Both are seconds.
- **Per wave merge:** firmware — `python3 -m pytest tests/ -v` plus `pio test -e native` and
  `pio test -e native_nodevtools` (unchanged by this phase; a regression there means something
  unrelated broke). App — full `pytest tests/`.
- **Phase gate:** both full suites green; `test_checker_convention.py` green with the raised floors;
  `git ls-files tests/fixtures/` shows every new fixture; the app cross-repo module observed
  **PASS not SKIP** with `-rs`; and both dispatch runs recorded with URL + SHA in
  `128-NONREGRESSION.md` before `/gsd-verify-work`.

### Wave 0 Gaps

- [ ] `firestarter/scripts/check_release_assets.py` — covers REL-03
- [ ] `firestarter/tests/test_check_release_assets.py` — covers REL-03 + REL-02's
      `fail_on_unmatched_files` grep + the build-root seam precedence
- [ ] `firestarter/tests/fixtures/planted_release_assets_*/pio_build/…` — **non-dotted directory
      name** (F-6); at least a missing-hex plant and a zero-byte plant
- [ ] `firestarter/tests/fixtures/clean_release_assets_all_three/pio_build/…` — the control
- [ ] `firestarter/tests/test_checker_convention.py` — `FLOOR` 5→6, `FIXTURE_FLOOR` 10→actual
- [ ] `firestarter/.github/actions/build-py32f071/action.yml` — new; `shell:` on every step
- [ ] `firestarter_app/tests/test_<name>_host.py` — the three-way binding, D-08(b)/D-09
- [ ] Framework install: **none needed** — pytest already present in both repos

*(No new shared fixture module is needed: the firmware side has no `conftest.py` by house rule and
resolves paths self-containedly; the app side reuses `tests/fw_presence.py`.)*

---

## Security Domain

`security_enforcement` is not present in `.planning/config.json` → treated as enabled. This phase's
surface is CI configuration in a repo with `permissions: contents: write` and a release-publishing
step, so the relevant categories are supply chain and CI privilege — not application auth.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No auth surface. The only credential is the built-in `secrets.GITHUB_TOKEN`; `beta-build.yml:97-103` already records why no PAT is needed |
| V3 Session Management | no | No sessions |
| V4 Access Control | **yes** | The job holds `permissions: contents: write` — enough to push commits and create tags/releases. This phase adds no new permission and must not. D-04's structural gate (no task may run `git push`/`gh workflow run`) is the human-side control |
| V5 Input Validation | **yes** | Two workflow inputs reach shell/expression context: `beta_version` (already validated — `update_version.py`'s `BETA_VERSION_RE` rejects anything not `X.Y.Z(b|rc)N` and raises) and the new `rehearsal`. Type `rehearsal` as `boolean` so it cannot carry a string into `draft:`/`tag_name:`. `github.run_id` is integer-valued and GitHub-supplied. **Never interpolate an input directly into a `run:` body** — pass via `env:` |
| V6 Cryptography | no | Nothing cryptographic is authored. SHA-256 checksums (existing `py32f071.yml` steps) are integrity checks, not crypto controls, and `ad47c3b` removes their upload |
| V14 Configuration | **yes** | Third-party action pinning. `softprops/action-gh-release@v2`, `actions/checkout@v4`, `actions/cache@v4`, `stefanzweifel/git-auto-commit-action@v5`, `actions/upload-artifact@v4` are all pinned to a **mutable major tag**, not a SHA. Pre-existing repo-wide posture; this phase adds no new third-party action (the composite action is first-party, `./.github/actions/...`). **Do not change it here** — SHA-pinning every action is a real improvement and a real behaviour change, and it is not in REL-01…REL-04. Record as a deferred idea |

### Known Threat Patterns for GitHub Actions release workflows

| Pattern | STRIDE | Standard Mitigation | Status in this phase |
|---------|--------|---------------------|----------------------|
| Script injection via `${{ }}` interpolated into a `run:` body | Tampering / Elevation | Pass untrusted values through `env:` and reference `"$VAR"`; never inline into shell | `beta_version` already uses the `env:` pattern (`beta-build.yml:70-72`). New steps must follow it |
| Unpinned third-party action mutated upstream | Tampering (supply chain) | SHA-pin actions | Pre-existing `@vN` posture; **out of scope**, recorded as deferred |
| Unpinned `apt-get install` pulling a changed toolchain | Tampering (supply chain) | Version-pin apt packages | D-17 keeps it unpinned deliberately, matching `py32f071.yml` exactly; recorded as deferred |
| Dependency source substitution (a moved SDK ref) | Tampering (supply chain) | Pin by commit SHA **and assert the pin was honoured** | **Mitigated and strengthened here** — `GIT_TAG` is already a 40-hex SHA, and D-10 adds the per-release assertion that the fetched tree matches it (F-15 restates the correct rationale) |
| A rehearsal dispatch publishing a real release/tag | Repudiation / integrity of the release record | `draft: true` (no tag created — F-3) + an unmistakable `tag_name` (D-03) + structural operator gating (D-04) | **Mitigated.** F-7 shows this threat has already materialised once in this repo, from this exact route |
| A privileged workflow triggered from an untrusted ref | Elevation | Keep `pull_request` (not `pull_request_target`); restrict `push` triggers | Unchanged: `beta-build.yml` is `push: [beta]` + dispatch; `py32f071.yml`'s `pull_request` is path-filtered and holds no write permission |
| A broken build silently shipping an incomplete release | Tampering / integrity | An assets-present gate before publish | **This is REL-03.** `check_release_assets.py` is the control |

---

## Project Constraints (from CLAUDE.md)

`/workspaces/CLAUDE.md` (meta) and `/workspaces/firestarter/CLAUDE.md` (firmware) both apply. The
firmware file is almost entirely about protocol dispatch and the native test env — none of which
this phase touches. The directives that *do* bind:

| Directive | Source | Bearing on this phase |
|-----------|--------|----------------------|
| The meta repo tracks only `.planning/` and `.claude/`; neither sub-repo is committed here | `/workspaces/CLAUDE.md` | This RESEARCH.md and `128-NONREGRESSION.md` are meta-repo commits; **all** code lands inside the sub-repos, on their own `v1.23-py32f071-integration` branches (D-19) |
| `firestarter/` is Arduino C++/PlatformIO; `firestarter_app/` is the Python host CLI | `/workspaces/CLAUDE.md` | Confirms the dual-repo split D-08 creates and which repo each new file belongs to |
| Serial-protocol changes must be kept in sync between `serial_comm.py` and `firestarter.cpp` | `/workspaces/CLAUDE.md` | **N/A** — this phase touches no protocol surface |
| Constants/flag bits are duplicated between `constants.py` and `firestarter.h`; change both together | `/workspaces/CLAUDE.md` | **N/A** — no constant is changed. (The analogous cross-repo duplication *this* phase creates is the filename literal, and D-08(b)/D-09 is exactly the "change both together" enforcement for it) |
| `pio run -e <env>` / `pio test` are the firmware build/test commands | `/workspaces/CLAUDE.md`, `firestarter/CLAUDE.md` | The full-suite gate includes `pio test -e native` and `pio test -e native_nodevtools`; this phase must not change either |
| `messages.h` is codegen-generated and ID-only — edit `messages.toml` and regenerate | `firestarter/CLAUDE.md` (and `beta-build.yml:48-54`'s drift gate) | **N/A but load-bearing:** `beta-build.yml` runs a `git diff --exit-code include/messages.h` drift gate *before* the version bump. This phase adds no message, so that gate must stay green — if it goes red, something outside this phase's scope changed |
| Adding a native test suite requires updating **both** native envs' `test_filter` **and** `-I` `build_flags` | `firestarter/CLAUDE.md` (v1.22 P119 correction) | **N/A** — the new tests are pytest under `tests/`, invisible to PlatformIO (documented in `tests/fixtures/README.md`). `platformio.ini` stays untouched |
| Shield-revision docs are two-layered and must move in lockstep | `firestarter/CLAUDE.md` | **N/A** — no hardware doc changes |

No directive in either file conflicts with any locked decision D-01…D-19.

---

## Sources

### Primary (HIGH confidence)

- **`softprops/action-gh-release@master` source** — `src/run.ts` (lines 10-21, 43-51, 79-84),
  `src/util.ts` (lines 132, 177-206), `src/github.ts` (`finalizeRelease`, lines 755-780),
  `action.yml` (inputs table). Established F-1 and F-3.
- **`softprops/action-gh-release` issue #722** — corroborates F-3 (draft created without a tag).
- **`docs.github.com/en/actions/reference/workflows-and-actions/contexts`** —
  `steps.<id>.outcome` vs `.conclusion`. Established F-4.
- **`docs.github.com/en/actions/reference/workflows-and-actions/metadata-syntax`** — composite
  actions: `shell` required for `run`, `runs.steps[*].id`, `runs.steps[*].continue-on-error`,
  `outputs.*.value`. Established Pattern 2's traps.
- **`actions/runner` ADR 0549 `composite-run-steps`** + `actions/runner#3510` — composite steps run
  in the calling job; the nested-node-action `continue-on-error` caveat.
- **`cmake.org/cmake/help/latest/module/FetchContent.html`** — `FETCHCONTENT_BASE_DIR` and
  `SOURCE_DIR` defaults; `FetchContent_Populate` deprecated in 3.30 (`CMP0169`).
- **CI run [`30676982030`](https://github.com/henols/firestarter/actions/runs/30676982030)** (job
  `91306188205`) — the measured FetchContent path (F-5), the hyphenated names, ARM size, 42 objects,
  49 s duration (F-13).
- **CI run [`30199560282`](https://github.com/henols/firestarter/actions/runs/30199560282)** +
  `gh api .../git/ref/tags/3.0.0b11` — the dispatch-from-a-milestone-branch precedent and the real
  tag it created (F-7).
- **`gh release view 3.0.0b14 --json assets`** — the live three-AVR-asset list (F-14).
- **Direct source reads in `/workspaces/firestarter`:** `.github/workflows/beta-build.yml`,
  `.github/workflows/py32f071.yml`, `.github/scripts/update_version.py`, `name_firmware.py`,
  `platform/py32f071/CMakeLists.txt`, `include/version.h`, `include/firestarter.h`,
  `include/rurp_platform_compat.h`, `platformio.ini`, `.gitignore`,
  `scripts/baseline/size_baseline.json`, `scripts/check_size_baseline.py`,
  `tests/test_check_size_baseline.py`, `tests/test_checker_convention.py`,
  `tests/fixtures/README.md`, and `git show ad47c3b`.
- **Direct source reads in `/workspaces/firestarter_app`:** `firestarter/firmware.py:100-155`,
  `firestarter/channel.py:34`, `tests/fw_presence.py`, `tests/test_py32_flash_map_host.py`,
  `tests/test_skip_census.py`, `tests/conftest.py`, `.github/workflows/ci.yml`,
  `.github/workflows/beta-release.yml`.
- **Commands executed this session:** `git check-ignore -v` (F-6), `python3 -m pytest
  tests/test_checker_convention.py` (7 passed), `python3 -m pytest tests/test_py32_flash_map_host.py`
  (16 passed), `gh auth status`, `gh workflow list`, `gh repo view --json defaultBranchRef`,
  `git ls-tree -r origin/main .github/workflows/`, `git status --porcelain` in both sub-repos (both
  clean).

### Secondary (MEDIUM confidence)

- WebSearch corroboration on draft-release tag timing (`orgs/community` discussions #24690, #16500;
  `cli/cli#9367`) — used only to cross-check the primary source reads, never as the basis for a claim.
- WebSearch corroboration on `continue-on-error` inside composite actions (`actions/runner#1457`,
  `#2418`, `github/docs#32097`).

### Tertiary (LOW confidence)

- None. No claim in this document rests on a search result alone.

### Not used

- **The knowledge graph.** `gsd-tools graphify status` reports it **stale**: built at `f4150b8`,
  **668 commits behind** `f6e0ad2`, `age_hours: 748`. Every relationship this phase needs was read
  directly from the two sub-repos instead, which is authoritative. If a later agent queries the
  graph for this phase, treat every semantic relationship as approximate and re-read the file.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|------|-------|--------|
| Standard stack | **HIGH** | Nothing is added. Every tool is already in the repo and every version claim was read from the file that pins it |
| Architecture (the fold's shape) | **HIGH** | Composite-action-in-calling-job and the ordering constraint are both documented and corroborated; the ARM target's real build was measured on CI, not predicted |
| `action-gh-release` semantics | **HIGH** | Read from the action's own TypeScript source, three files, plus an issue corroborating the draft/tag behaviour. This is the strongest-evidenced finding in the document and it **overturns a requirement's stated rationale** |
| `update_version.py` behaviour (F-2) | **HIGH** | Traced line by line against `include/version.h`'s actual current value; the conclusion (`3.0.1`) is arithmetic on read code, not inference |
| Fixture/`.gitignore` trap (F-6) | **HIGH** | Confirmed by `git check-ignore -v` printing the matching rule |
| House checker/test conventions | **HIGH** | Derived from five existing checkers and their five paired tests, plus the meta-test that enforces them, plus the fixtures README |
| Pitfalls | **HIGH** | Seven of eight are grounded in a measured fact in this document or a recorded in-milestone failure (A-7, Phases 118/124/122); only Pitfall 5 is documentation-derived |
| Rehearsal-dispatch mechanics | **MEDIUM** | The route is proven by precedent run 30199560282, but the *new input's* resolution on a non-default ref (A4) and the `draft:` expression's behaviour on a `push` (A1) are unobserved. Both fail loudly rather than silently, and both are falsifiable in run A |
| Anything about PY32F071 silicon | **LOW by construction** | No PCB exists. The permitted claim is exactly one sentence wide: *the asset publishes* |

**Research date:** 2026-08-01
**Valid until:** 2026-08-31 for the in-repo facts (stable; only Phase 129/130 will move them).
**2026-08-08 for the `action-gh-release` source reads** — `@v2` is a mutable major tag, so its
behaviour can change under the repo without a version bump. If the fold is not exercised within a
week, re-read `src/run.ts` before the first dispatch.
