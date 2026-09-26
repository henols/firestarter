# Pitfalls Research

**Domain:** Adding a fourth board target on a new MCU architecture (PY32F071xB / Cortex-M0+) plus a new host firmware-install path (USB DFU), to a mature dual-repo embedded system with three working AVR targets — no silicon for the new target exists.
**Researched:** 2026-07-30
**Confidence:** HIGH for everything tagged **PROVEN** (measured or reproduced in-tree this session); MEDIUM for **PREDICTED** items (mechanism identified in tree, consequence not yet triggered).

---

## How to read this document

Every finding carries one of two tags:

- **PROVEN** — measured, built, run or reproduced during this research session against the live branches. The command and the number are given so any claim can be re-checked.
- **PREDICTED** — the mechanism is confirmed present in the tree, the failure has not been triggered. Treated as a risk, never as a fact.

Prevention is marked **[MECHANICAL]** when a script, test or build step can enforce it, and **[JUDGEMENT]** when it cannot. Per the downstream consumer's instruction: **judgement-only prevention is worth much less here, and is labelled so it can be priced accordingly.**

Nothing in this document proposes a prevention strategy that requires PY32F071 silicon. None exists.

---

## Measured baseline (established this session — use these numbers, not the recorded ones)

Firmware `beta` @ `5c9160a`, devcontainer PlatformIO, default `build_flags` (i.e. **`-D DEV_TOOLS` present — the binding, tighter configuration** per PROJECT.md SIXTH CORRECTION item 3).

| Build | `beta` baseline | + `agent/portability-macros` (5 commits) | + full py32 stack merge |
|---|---|---|---|
| Uno flash | 23932 / 32256 (74.2 %) | 23954 (**+22 B**) | 23954 (**+22 B**) |
| Uno RAM | 1573 / 2048 (76.8 %) | unchanged | unchanged |
| Leonardo flash | **26072 / 28672 (90.9 %) → 2600 B free** | 26016 (**−56 B**) | 26016 (**−56 B**) |
| Leonardo RAM | 2014 / 2560 (78.7 %) → 546 B free | unchanged | unchanged |
| `pio test -e native` | **141 cases / 17 suites, all PASSED** | **0 passed / 17 ERRORED** | **141 / 141 PASSED** |

Commands: `pio run -e leonardo -e uno`, `pio test -e native`, in a throwaway worktree off `beta` with the five `agent/portability-macros` commits cherry-picked (`532997c c0c6695 b253092 adb133a 52d6c1f` — **zero conflicts**), then with `git merge --no-ff feature/py32f071-release-assets` (**zero conflicts**).

**Three recorded figures are corrected by this measurement (PROVEN):**

1. **Leonardo headroom is 2600 B, not 2992 B.** PROJECT.md, STATE.md and the research brief all quote 2992 B (25680/28672). That figure predates Phase 119's own `+392 B` SDP-lock addition: 25680 + 392 = 26072, which is exactly what `beta` builds today. **Judge every v1.23 flash delta against 2600 B.**
2. **RAM is the scarcer resource on Leonardo, and nobody is tracking it.** 546 B free (78.7 %). Every flash discussion in the project's history has a number; RAM has none. A portability layer that turns a `PROGMEM` table into a RAM table, or that adds a function-pointer dispatch table, spends from a 546 B budget.
3. **`DATA_BUFFER_SIZE` for the py32 target is 512, not 1024.** `platform/py32f071/CMakeLists.txt:113` sets `DATA_BUFFER_SIZE=512` on **both** `agent/py32f071-toolchain` and `feature/py32f071-release-assets`. `.planning/notes/py32f071-port-branch-state.md` and STATE.md both record 1024. The linker script declares **16 K RAM** (`PY32F071xB_FLASH.ld:6`), not the 20 K sometimes assumed. Since the host sizes host→fw chunks from the advertised buffer (v1.10 CAP-01), this is a wire-visible datum recorded wrong.

**The good news, and it is real:** the portability layer costs the AVR targets essentially nothing (+22 B Uno, −56 B Leonardo, RAM unchanged), and the *full* stack keeps the native suite at 141/141. The AVR-flash-growth fear that dominates this project's history is **not** where v1.23's risk lives. The risk lives in the intermediate states, the cross-repo gates, and the claims.

---

## Critical Pitfalls

### Pitfall 1: Landing `agent/portability-macros` first breaks the entire native test suite

**What goes wrong:**
**PROVEN.** Cherry-picking the five `agent/portability-macros` commits onto today's `beta` — the exact "land the HAL prep first, then the port" sequence PROJECT.md's target-features list describes — takes `pio test -e native` from **141/141 passing to 0 passing and all 17 suites ERRORED**. Hard compile failure, not a flaky test:

```
src/json_parser.c:302:32: error: implicit declaration of function 'pgm_read_ptr'
src/json_parser.c:453:9:  error: implicit declaration of function 'strncmp_P'
*** [.pio/build/native/src/json_parser.o] Error 1
```

**Why it happens:**
Two commits in that branch (`b253092`, `adb133a`) replace `#include <avr/pgmspace.h>` with `#include "rurp_platform_compat.h"` in `include/rurp_shield.h` and `include/rurp_serial_utils.h`. On the native env, `<avr/pgmspace.h>` used to resolve to the per-test stubs at `test/native/avr/*/avr/pgmspace.h` (seven of them), which **do** define `pgm_read_ptr` and `strncmp_P`. `agent/portability-macros`' version of `rurp_platform_compat.h` **does not** — it defines `pgm_read_byte/word/dword`, `memcpy_P`, `strcpy_P`, `strlen_P`, `strcmp_P` and stops. The four missing helpers (`pgm_read_ptr`, `strncmp_P`, `strncpy_P`, `sprintf_P`) are added by commit **`780a3fb` "Complete non-AVR program-memory compatibility helpers"**, which lives on the *stacked* `agent/py32f071-toolchain` branch, not on the base branch.

So the branch that reads as "the safe, small, board-agnostic half" is the one that is **not self-sufficient**. Its own repair is on the branch stacked on top of it.

**How to avoid:**
- **[MECHANICAL]** Treat the two branches as **one atomic landing**. Never commit an intermediate state where `agent/portability-macros` is on the integration branch and the py32 stack is not. If the plan wants two commits for reviewability, `780a3fb` must be reordered/cherry-picked into the first one.
- **[MECHANICAL]** Add `pio test -e native` as a per-plan gate inside the integration phase, not only at phase end. The failure is instant (~5 s to first error) and unambiguous.
- **[MECHANICAL]** Record the baseline **before** the merge (`141 cases / 17 suites`) as a literal number in the phase's non-regression artifact, and assert the post-merge count is *equal*, not merely "green". A suite that silently stops being collected also reports green.

**Warning signs:**
Any plan step of the form "land the portability macros, verify, then land the port". Any commit whose diff touches `include/rurp_platform_compat.h` without also touching or already containing `pgm_read_ptr`.

**Phase to address:** the firmware integration phase (**suggested Phase 124**), with the baseline captured in the preceding gate phase (123).

---

### Pitfall 2: A firmware rename turns nine cross-repo gates into silent SKIPs, and pytest exits 0

**What goes wrong:**
**PROVEN by direct experiment.** `firestarter_app`'s firmware-source-scanning gates detect "firmware absent" by testing whether **one specific firmware source file exists**:

```python
# tests/test_sdp_table_parity.py:54
_FW_ABSENT = not _EEPROM_28C_CPP.exists()
```

Identical idiom in `test_check_is_memory_cmd_no_ifdef.py` (`firestarter.h`), `test_check_no_log_in_sdp_window.py` (`eeprom_28c.cpp`), `test_revision_constants_parity.py` (`firestarter.h`), `test_gen_validation_header.py` (`validation_matrix.h`), `test_sdp_bus_config_drift.py` (`sdp_bus_config.h`), `test_dispatch_mirror.py` (`PROTOCOLS.md` **and** the fw dispatch test).

Experiment run this session: with a merged firmware sibling present, `mv src/proms/eeprom_28c.cpp src/proms/eeprom_28c_renamed.cpp`, then run the two SDP gate modules:

```
ssss.s......                                              [100%]
SKIPPED [1] tests/test_sdp_table_parity.py:171: firestarter firmware checkout absent (eeprom_28c.cpp)
... 5 legs skipped ...
exit=0
```

**Five gate legs went from PASS to SKIP, with a false diagnosis ("checkout absent") and a zero exit code, because one file was renamed.** Whole-suite measurement: with no sibling firmware repo at all, **33 tests skip (30 of them firmware-keyed) and `pytest` exits 0**; with the merged sibling present, 3 skip and 0 fail.

**Why it happens:**
The skip guard was written to solve a *different* problem — `beta-release.yml` checks out `firestarter_app` alone (`81fa53c`, 2026-07-30). "Repo absent" and "file moved" are indistinguishable under a file-existence proxy. This project has already been bitten by the adjacent form of this four times in Phase 117 alone (FOURTH CORRECTION item 4) and once more in Phase 118 — but those were **fail-closed** breakages that CI caught. The rename-to-SKIP form is **fail-open**, and it has never been triggered because no prior milestone moved firmware files across repo-scanned paths at scale. **v1.23 is the first milestone whose entire premise is moving and renaming firmware code.**

**How to avoid:**
- **[MECHANICAL] Split the proxy in two.** Key "repo absent" on the *repository* (`../firestarter/.git` exists), and make "repo present but my scan target is missing" a **hard failure**. One shared helper, seven call sites. This is the single highest-value mechanical change available to v1.23 and it is ~30 lines.
- **[MECHANICAL] Assert the skip census.** Add one test that runs the suite's own collected skip reasons — or simpler, a CI step `pytest tests -q -rs` piped through a checker that fails if any skip reason contains "firmware ... absent" **while `../firestarter/.git` exists**. Ship it with a planted-violation fixture per the standing anti-hollow discipline.
- **[MECHANICAL] Re-run the nine-row cross-repo gate sweep at every wave**, as Phase 118 did successfully (FIFTH CORRECTION item 5: *"a named plan owned every one of them ... Zero host CI surprises. Keep doing this"*). The nine rows: `check_dispatch.py`, `test_dispatch_mirror.py`, `check_is_memory_cmd_no_ifdef.py`, `check_no_log_in_sdp_window.py`, `test_sdp_table_parity.py`, `gen_sdp_bus_config.py` / `test_sdp_bus_config_drift.py`, `test_revision_constants_parity.py`, `check_devtest_orchestrator.py`, `test_gen_validation_header.py`.
- **[MECHANICAL] Never prove "firmware untouched" with a path-scoped diff.** `git diff -- some/path` passes **vacuously** when the path is wrong — the FOURTH CORRECTION's own note (`git diff -- src/flash_utils.h` matched nothing because the real path is `src/proms/flash_utils.cpp`). Phase 120 item 9 records the correct proof: `git -C /workspaces/firestarter status --porcelain` being empty, *which subsumes every path*. Use that, or literal blob SHAs.

**Warning signs:**
A gate test reporting "checkout absent" in an environment where the checkout is obviously present. Skip count changing between waves. A plan that renames or relocates any of: `include/firestarter.h`, `include/rurp_shield.h`, `src/proms/eeprom_28c.cpp`, `doc/PROTOCOLS.md`, `test/native/avr/_shared/*`.

**Phase to address:** gate-hardening phase **before** any firmware move (**suggested Phase 123**); re-verified per wave in 124 and in the host phase.

---

### Pitfall 3: The 72-commit merge is conflict-free and semantically wrong

**What goes wrong:**
**PROVEN.** Both merges auto-resolve completely:

```
$ git merge --no-ff feature/py32f071-release-assets   # firmware, 72 behind / 53 ahead
Automatic merge went well; stopped before committing as requested
$ git merge --no-ff beta                              # app, 79 behind / 3 ahead
Automatic merge went well; stopped before committing as requested
```

Zero conflicts in either repo. And the firmware result is broken:

```
MISSING: src/proms/flash_type_3.cpp
MISSING: src/proms/flash_type_4.cpp
```

`platform/py32f071/CMakeLists.txt`'s hand-maintained `FIRESTARTER_COMMON_SOURCES` list names two files that **v1.19 Phase 104 renamed** to `flash_nor_unlock.cpp` / `flash_5v_page.cpp`. Git cannot see this: the CMake file was added by one side and never edited by the other, so there is no hunk to conflict. The ARM target's source list is a *data reference* to paths, and 72 commits of `beta` moved the paths.

The same scan finds four files on `beta` that the ARM list does **not** name: `src/dev_tools.cpp`, `src/rurp_config_utils.cpp`, and (post-rename) `src/proms/flash_5v_page.cpp`, `src/proms/flash_nor_unlock.cpp`. Two of those omissions are deliberate (`platform/py32f071/src/config.cpp` substitutes for config utils; `dev_tools.cpp` is `DEV_TOOLS`-gated); two are the rename damage. **A reader cannot tell which is which from the file.**

**Why it happens:**
PlatformIO builds `src/**` implicitly; CMake builds an explicit list. The port therefore introduced a **hand-maintained duplicate of the source manifest** in a repo where the other three targets have none. Missing-file references fail loudly at configure time (good); **files added to `src/` by a future phase and never added to the CMake list fail silently** — the ARM target simply compiles a different program, and only a link error against a *referenced* symbol would reveal it.

This project already has the correct precedent for this exact situation: v1.22's D-06 (EIGHTH CORRECTION item 5) resolved a merge whole-file `--ours` and justified it by *"a mechanical superset proof ... proven by an empty diff"*, **explicitly because** hunk-level resolution there *"produces code that compiles and passes while being wrong."* The lesson generalises: **a green suite is not evidence of a correct merge; a structural proof is.**

**How to avoid:**
- **[MECHANICAL] Ship a CMake-source-manifest drift gate.** A checker that walks `src/**` on the firmware tree, subtracts a small explicit allow-list of intentionally-AVR-only / intentionally-substituted files, and asserts the remainder is exactly what `platform/py32f071/CMakeLists.txt` lists. Pair it with a planted-violation fixture (add a fake `src/proms/zzz.cpp`, assert the checker exits non-zero). This converts a silent divergence into a loud one **forever**, not just at merge time. It is the single most durable artifact v1.23 can leave behind.
- **[MECHANICAL] Structural merge proofs, enumerated up front.** For each repo, before committing the merge: (a) every path referenced by any build manifest resolves; (b) the AVR flash/RAM figures and the native case count equal the recorded pre-merge baseline; (c) the nine cross-repo gates run (not skip) and pass; (d) the host `git status --porcelain` / firmware `git status --porcelain` proof for anything claimed untouched.
- **[MECHANICAL] Prove which side won for every file the two sides both touched.** Only three shared files exist (`include/rurp_shield.h`, `include/rurp_serial_utils.h`, and the new headers) — small enough to diff each against both parents and record the verdict, rather than trusting auto-merge.
- **[JUDGEMENT]** Read `git log --oneline beta..HEAD --name-only` for the 53 py32 commits and ask, per file, "did `beta` move this concept in the last 72 commits?" The rename class is the one auto-merge is blind to.

**Warning signs:**
"The merge had no conflicts" used as a quality statement. A green `pio run` on AVR taken as evidence about the ARM target (they share no build system). Any plan whose merge verification is only "tests pass".

**Phase to address:** firmware integration (**124**) and host integration (**suggested 126**); the manifest gate is authored in **123** so it is available *before* the merge.

---

### Pitfall 4: The ARM target cannot be built in this devcontainer, and after the merge nothing builds it on `beta`

**What goes wrong:**
**PROVEN.** `which arm-none-eabi-gcc cmake ninja` returns **nothing** in this devcontainer. The ARM target is unbuildable locally: `pio` does not build it (it is a separate CMake project), and the toolchain is absent. Every "the target builds clean" claim v1.23 makes therefore rests on **GitHub Actions**, not on a local run.

And the workflow that builds it, `.github/workflows/py32f071.yml`, triggers on **`pull_request`** and `workflow_dispatch` **only** — no `push` trigger at all. `build.yml` triggers on `main` (never merged under this branch model). `beta-build.yml` does not build the ARM target today. **After the merge lands on `beta`, no workflow builds the PY32F071 image on `beta`.** Any subsequent shared-code change pushed to `beta` can break the ARM target with zero CI signal until someone opens a PR that happens to touch `include/**` or `src/**`.

Compounding: the CMake project fetches the SDK over the network at configure time (`FetchContent` from `github.com/OpenPuya/PY32F071_Firmware.git` @ `0ed2f4b`). The ARM build has a **network dependency**, in what is about to become the release path.

**Why it happens:**
The workflow was authored to validate a PR-stage port; PROJECT.md's own release-asset design (STATE.md §Release-asset mechanics) already anticipates the fold into `beta-build.yml`, but until that fold lands there is a coverage hole exactly where the merge lands.

**How to avoid:**
- **[MECHANICAL]** Add `push: branches: [beta]` to `py32f071.yml` **in the same phase that lands the merge**, or fold into `beta-build.yml` in that phase. Do not leave the target unbuilt on `beta` between phases.
- **[MECHANICAL]** Every claim of the form "the PY32F071 target builds clean" must cite a **workflow run URL plus the commit SHA it ran against**. A local `pio` run is not evidence about ARM and must never be recorded as if it were.
- **[MECHANICAL]** Mirror the SDK pin: keep `GIT_TAG 0ed2f4b…` as a full SHA (it already is) and add a build step that records the resolved SDK SHA into the job log, so a silently-moved upstream is visible.
- **[MECHANICAL]** If the devcontainer is to be the place ARM regressions get caught, add `gcc-arm-none-eabi` + `cmake` + `ninja` to `.devcontainer/Dockerfile`. Otherwise state plainly in the phase artifact that ARM verification is CI-only.

**Warning signs:**
A phase SUMMARY asserting an ARM build result with no run URL. `arm-none-eabi-size` output pasted without provenance. A green `beta` push read as covering four targets when it covers three.

**Phase to address:** the release-plumbing phase (**suggested 127**), with the trigger fix pulled forward into **124**.

---

### Pitfall 5: A broken ARM build blocks the AVR beta release

**What goes wrong:**
**PREDICTED, mechanism confirmed.** `beta-build.yml`'s release step is:

```yaml
- name: Release
  uses: softprops/action-gh-release@v2
  with:
    files: .pio/build/**/firestarter_*.hex
```

`action-gh-release` **warns** on a glob that matches nothing and **fails** on a missing literal path. The ARM image lands at `build/py32f071/firestarter_py32f071.hex` — a single, specific path. The obvious fold ("add the file to `files:`") is therefore the wrong one: a broken ARM build, or an SDK fetch failure, or an ARM toolchain apt hiccup, would **fail the release job and cut no beta at all**, for three targets that built fine.

Second failure mode in the same step: any ARM build step placed before `Release` without `continue-on-error` aborts the whole job on ARM failure, before any AVR asset is published.

**Why it happens:**
The instinct when adding a fourth asset is to add a fourth literal filename. STATE.md already records the correct answer; the risk is that the implementing plan does not read that far.

**How to avoid:**
- **[MECHANICAL]** Use a **glob**, e.g. `build/py32f071/firestarter_*.hex`, as a second `files:` line. Warn-on-miss is the desired semantics.
- **[MECHANICAL]** Put `continue-on-error: true` on the ARM configure/build/copy steps, and add an explicit "AVR assets present" assertion before `Release` so an AVR miss still fails loudly.
- **[MECHANICAL]** Add a negative test to the phase: run the workflow (or a local reproduction) with the ARM build deliberately broken and confirm the AVR beta still publishes three `.hex` assets. This is the planted-violation discipline applied to CI.
- **[MECHANICAL]** Keep the ARM build **after** `update_version.py` + the `git-auto-commit-action` step. The version bump rewrites `include/version.h` and commits *before* building; an image built anywhere else carries a stale `VERSION`, and the host's entire update decision is that string compared against the release tag. `py32f071.yml`'s own header comment already documents this — quote it in the plan.

**Warning signs:**
A `files:` entry with no `*`. An ARM build step above `Release` without `continue-on-error`. Any ARM image published from a job that does not run `update_version.py`.

**Phase to address:** **suggested Phase 127** (release plumbing).

---

### Pitfall 6: Pushing `beta` cuts a release as a side effect

**What goes wrong:**
**PROVEN historically (twice).** Pushing `beta` in either sub-repo auto-fires CI and cuts a new beta prerelease. It has happened twice already — the repos are at `3.0.0b14` with stray public `3.0.0b12` prereleases left in place (D-05, cleanup declined). The next beta number is derived by `update_version.py`'s `_git_tag_scan_fallback`, which scans `git tag --list "<base>b*"` in the checkout — so the numbering is a function of tags present, and a release created off-cycle permanently shifts the sequence.

Secondary, and worse for a milestone that ships a host feature: **six of thirteen published app GitHub betas never reached PyPI** — b4, b5, b6, b9, b10, b12, a 46 % historical miss rate — because `beta-release.yml` creates the release with a PAT lacking `workflow` scope, which suppresses the `release.published` event that `publish.yml` needs. **"CI is green" is not evidence a channel is live** (EIGHTH CORRECTION item 6).

Third: a green beta workflow is a **narrower** statement than "CI is green". `ci.yml` and firmware `build.yml` trigger on `main` and pull requests only, so a `beta` push runs **no ruff, no mypy, no coverage floor, no vector-catalog gate, no CLI smoke test** (EIGHTH CORRECTION item 7).

**Why it happens:**
The release trigger is the same operation as the integration operation. There is no way to land work on `beta` without cutting a beta.

**How to avoid:**
- **[MECHANICAL]** Write the release decision to a committed artifact (`12X-DECISION.md`) **before** the push, as v1.22 did, and derive the cut tag from `gh release list` **after** — never assume the computed number.
- **[MECHANICAL]** Verify the PyPI resolution directly (`pip index versions firestarter --pre` or the JSON API) rather than reading a green workflow. If the release event was suppressed, dispatch `publish.yml` manually — that dispatch is **the norm, not a contingency**.
- **[MECHANICAL]** Run the gates that a `beta` push does *not* run (`ruff`, `mypy` watermark, `pytest --cov`, catalog codegen `--check`) locally or in a PR before the merge push, and record the results. Otherwise the milestone ships having never run its own quality gates on the merged tree.
- **[MECHANICAL]** `--auto` / `--chain` **auto-approves human-verify checkpoints**. `autonomous: false` does not protect an outward-facing gate. Any plan step that pushes `beta`, publishes to PyPI, or posts a public comment must be its own gate, structured so auto-approval cannot reach it.
- **[JUDGEMENT]** Decide up front whether v1.23 accepts "the merge IS the cut" (as v1.22 did) or defers the merge. Do not discover this at push time.

**Warning signs:**
A plan step that says "merge to beta" without a preceding decision artifact. A closing SUMMARY citing a workflow status as proof a channel is live. A beta number assumed rather than read.

**Phase to address:** the close phase (**suggested Phase 129**), with the decision artifact authored before any push.

---

### Pitfall 7: A provisional pin map with no mechanical enforcement, next to a PROM socket

**What goes wrong:**
**PROVEN.** `include/boards/py32f071_rurp_shield.h` carries an excellent 20-line warning ("*This is NOT a verified Firestarter PCB assignment ... validate the signals on hardware before connecting a PROM or enabling programming voltage*") and then defines:

```c
#define RURP_PY32F071_PINMAP_CONFIGURED  1
#define RURP_PY32F071_PINMAP_PROVISIONAL 1
...
#if !RURP_PY32F071_PINMAP_CONFIGURED
#error "Configure the PY32F071 Firestarter wiring in ..."
#endif
```

Two defects, both mechanical:

1. **The `#error` guard cannot fire.** `RURP_PY32F071_PINMAP_CONFIGURED` is unconditionally `1` two lines above the `#if !`. This is a **hollow gate in the very branch being landed** — structurally incapable of failing, exactly the shape of v1.12's GATE-03 debt that the project's standing discipline exists to prevent.
2. **`RURP_PY32F071_PINMAP_PROVISIONAL` has zero consumers.** Grepped across `.h`, `.cpp`, `.c`, `.md`, `.yml`: it appears at its own definition and in one README sentence. It gates nothing. Meanwhile `platform/py32f071/src/py32f071_rurp_shield.cpp` drives the provisional pins live (`RURP_PY32F071_DATA_PORT`, `..._CE_PIN`, `..._OE_PIN`, and `rurp_read_voltage_mv()` off `ADC_CHANNEL_4`) with no gate.

The consequence is not hypothetical once a PCB exists: an image built from a provisional map, flashed onto a board wired differently, drives the wrong lines with a PROM seated. This project's whole v1.18 milestone was one wrong pin (DIP32 pin 31 modeled as A18 rather than held `/PGM`).

**How to avoid:**
- **[MECHANICAL] Make `RURP_PY32F071_PINMAP_PROVISIONAL` load-bearing.** While it is `1`, the target must refuse every operation that can energise a PROM. Concretely: gate `configure_memory`'s programming paths, or refuse at the command-admission layer, and make the refusal a native test. The cleanest shape given the milestone's own scope: `rurp_set_vpp_target_mv()` already returns `MANUAL_ADJUSTMENT_REQUIRED` on every board (the VPP seam) — extend the same fail-closed posture to write/erase on a provisional-pinmap build.
- **[MECHANICAL] Fix the dead `#error`.** Either delete it (it asserts nothing) or restructure so `CONFIGURED` is *not* defined in the same file — e.g. require it from the build system, so an unconfigured build genuinely fails. Ship a planted-violation proof that the guard can fail.
- **[MECHANICAL] Grep-gate the orphan macro class.** A checker asserting that every `RURP_*_PROVISIONAL`-style flag has at least one consumer outside its own definition would have caught this in seconds, and generalises to future ports.
- **[JUDGEMENT]** Keep the prose warning. It is good. It is also unenforceable, and this project's own history (D-14's overclaim reaching a locked decision) shows prose is not a control.

**Warning signs:**
A `#define X 1` immediately followed by `#if !X #error`. A macro whose only other occurrence is in documentation. Any pin-map constant reachable from a code path that toggles VPP/VPE.

**Phase to address:** the firmware integration phase (**124**) must not land the provisional map without the refusal; the flash-config/VPP-seam phase (**suggested 125**) owns the seam side.

---

### Pitfall 8: Claiming more than the evidence supports — and the specific shapes it will take here

**What goes wrong:**
The permitted ceiling is narrow and explicit: **the target builds clean, native and host suites pass, and the DFU sequence is exercised against device descriptors and mocks.** Forbidden: *"the firmware runs on a PY32F071"*, *"the install works end to end."*

The failure modes are not people lying. They are these specific substitutions, each of which has an in-project precedent:

| Substitution | Why it is tempting | Precedent |
|---|---|---|
| "CI is green" → "the firmware works" | A 2000-line ARM build succeeding *feels* like a result | v1.22: *"a green beta workflow is a narrower statement than CI is green"* |
| "the DFU sequence is correct" → "the install works" | 654 lines of tests, all passing | v1.22 D-01: the install/flash chain was *"trusted, not re-verified"* — and said so |
| "the pin map compiles" → "the pin map is right" | The header has a `#error` guard (which cannot fire) | v1.18: one mis-modeled pin was an entire milestone |
| "VPP control seam landed" → "VPP control works" | `rurp_read_voltage_mv()` exists and returns a number | **A closed loop that cannot be validated must not be claimed to work** (PROJECT.md's own scoping note) |
| "43/41 style derivation" → over-precision | Derived numbers read as authoritative | v1.22 C-5: a locked decision (D-14) overclaimed and was caught only by re-measuring |

The VPP case deserves its own sentence, because it is the one place where an unvalidatable claim could reach hardware. `platform/py32f071/src/py32f071_rurp_shield.cpp:292` implements `rurp_read_voltage_mv()` against `ADC_CHANNEL_4` on a **provisional** pin, VREFINT-compensated, with no calibration and no reference measurement possible. That function returning plausible integers is not evidence of anything. The milestone's decision to land **the seam only** — `RURP_VPP_CONTROL_MANUAL` everywhere, `rurp_set_vpp_target_mv()` returning `MANUAL_ADJUSTMENT_REQUIRED` — is the correct control, and it must be enforced, not merely intended.

**How to avoid:**
- **[MECHANICAL] Ship a v1.23 `check_permitted_claims.py`.** The v1.22 original is at `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/check_permitted_claims.py` — 8 forbidden regex patterns, one required-caveat pattern, an explicit five-element target list (never tree-walked, so the fixtures directory can never poison a default run), an env-var seam (`FIRESTARTER_CLAIMSCAN_TARGETS`), fail-closed on a missing target **and** on zero targets resolved, plus `test_check_permitted_claims.py` with **7 subprocess legs** and **4 fixtures** (`planted_forbidden_claim.md`, `planted_missing_caveat.md`, `clean_control.md`, `clean_control_second.md`). Copy the shape; replace the phrase table.
  Suggested v1.23 forbidden set: `runs on (a |the )?PY32`, `works end[- ]to[- ]end`, `silicon[- ]verified`, `bench[- ]validated` (unqualified), `flashed (a|the) PY32`, `hardware[- ]validated`, `closed[- ]loop VPP (works|verified)`, `pin map (is )?(correct|verified|validated)`. Suggested required caveat: **"no PY32F071 hardware exists"**.
- **[MECHANICAL] Assert the seam refuses.** A native test that calls `rurp_set_vpp_target_mv()` on every compiled board and asserts `MANUAL_ADJUSTMENT_REQUIRED`. Without it, "seam only" is a comment.
- **[MECHANICAL] Assert the beta-only gate holds on a stable build.** `firestarter/channel.py` is good work (fails closed on unparseable versions, reads no environment, and its docstring correctly cites the firmware's `-D X=${sysenv.VAR}` fail-open lesson). It already has 8 test legs inside `test_py32_dfu.py`. Keep them; add one asserting `py32f071` is absent from `_BOARD_CHOICES` on a stable build — note `_BOARD_CHOICES` is computed at **import time** (`cli_handlers.py:140`), so a late monkeypatch of `__version__` does not affect it. The existing tests already work around this correctly.
- **[JUDGEMENT] A blocking operator wording review.** v1.22's item 9 is the honest statement of the limit: the claim gate is *"the mechanizable half ... ONLY. It cannot detect an implied overclaim, a misleading omission, or wrong tone."* Budget the review; do not let a green scan close the criterion.

**Warning signs:**
The word "validated" without a named instrument. A phase artifact citing a test count as a hardware claim. Any sentence about VPP that does not contain the word "manual".

**Phase to address:** the claim gate is authored in **123** (so it guards every phase's artifacts, not just the last one) and enforced in the close phase (**129**).

---

### Pitfall 9: Hollow verification specific to new-target work

**What goes wrong:**
New-target milestones manufacture confidence in three characteristic ways, all present or adjacent in this tree:

1. **A build that succeeds proves nothing about correctness.** The ARM target compiles the shared command processor, framing and PROM algorithms for Cortex-M0+ — a genuine achievement, and entirely orthogonal to whether the emitted register sequences are right. Nothing on the ARM side records or asserts a bus trace. The project's own `HOST_STUBS_RECORD_BUS` oracle (v1.22 Phase 116) records `rurp_write_to_register` calls and runs on `native`, **not** on ARM. **PREDICTED risk:** the ARM target could diverge from the AVR targets' emitted sequences with no oracle able to notice.
2. **A test passes because a stub returns success.** The canonical in-project instance is PR #47 (`feature/py32f071-full-support`, closed): `src/usb.c` is a ring buffer over `__attribute__((weak))` **no-op** hooks — *it links*, and a board flashed with it is silent on USB. It also *reads* as the most complete branch (24 files, all-inclusive CMake list). **Start from PR #48; never #47.**
3. **A golden trace matches because both sides were regenerated.** In-repo precedent: abandoned commit `0052c42` swapped two lookup tables and still reported **"22 tests PASS (zero-diff)"**, because the recording layer did not observe what mattered. The v1.22 antidote — build the oracle first and prove it RED, with two index-precise planted-fault negatives per suite — is now house style.

Fourth, newly measured this session: **PROVEN.** The merged tree emits **58 additional macro-redefinition warnings per native suite** (138 total vs 80 on baseline for `test_dispatch`), all from `rurp_platform_compat.h` colliding with ArduinoFake:

```
warning: "F" redefined            (×10)   warning: "pgm_read_ptr" redefined  (×10)
warning: "PGM_P" redefined        (×9)    warning: "sprintf_P" redefined     (×10)
warning: "PSTR" redefined         (×10)   warning: "strncmp_P" redefined     (×9)
... 14 distinct macros ...
```

Zero such warnings exist on `beta`. They are harmless individually and collectively they **bury the next real warning**. That is how a genuine regression gets shipped past a green suite.

**How to avoid:**
- **[MECHANICAL] Eliminate the redefinition warnings, do not tolerate them.** Include-order fix or `#undef`-before-`#define`; then add a warning-count gate (`pio test -e native 2>&1 | grep -c 'redefined'` must equal 0) so they cannot come back. Cheap, and it restores warnings as a signal.
- **[MECHANICAL] Every new checker ships with a committed planted-violation fixture and a pytest proving the checker exits non-zero on it.** This is already the project's standing discipline (v1.21: 9 legs; v1.22: 7 legs). Apply it to all four checkers this milestone should add (FW-path split, CMake manifest drift, orphan-provisional-macro, claims).
- **[MECHANICAL] Assert test *counts*, not just status.** `141` native cases and the app suite's collected total are the anti-vacuity numbers. A suite that stops being collected reports green.
- **[MECHANICAL] Weak/no-op symbols are a build-time detectable class.** A checker asserting no `__attribute__((weak))` no-op body survives in `platform/py32f071/src/**` would have made PR #47's trap impossible to ship. Worth ~20 lines given the trap is documented and the branch is still on `origin`.
- **[JUDGEMENT]** For each verification artifact, write the sentence "this would still pass if ___ were wrong" and check the blank is acceptable.

**Phase to address:** **123** (checkers + baselines), enforced through **124–129**.

---

### Pitfall 10: Host packaging — an optional extra, a driver, and an install path that silently no-ops

**What goes wrong:**
The DFU installer adds a `py32` extra (`pyusb>=1.2.1`) to a CLI targeting py3.9 and py3.11 in CI. Four distinct hazards, three measured:

1. **PROVEN: `pyusb` is not installed anywhere in the test or CI path, and the suite passes anyway.** `python -c "import usb"` fails in this devcontainer; `tests/test_py32_dfu.py` (654 lines) passes regardless — its docstring states plainly *"No hardware and no pyusb are required: `find_dfu_interfaces` is monkeypatched."* And `ci.yml` installs `pip install -e .[test]`, never `.[test,py32]`. **The entire real pyusb API surface — `usb.core.find`, `usb.util.dispose_resources`, `ctrl_transfer` argument order, `extra_descriptors` availability — is unexercised in CI and unexercisable locally.** A pyusb API misuse ships undetected.
2. **PROVEN: the branch every plain-install user will hit is marked untestable.** `py32_dfu.py:375` carries `except ImportError as exc:  # pragma: no cover — environment-dependent`, raising a well-written `PyusbMissingError` with an actionable message. It is coverage-excluded and untested — yet `ci.yml`'s own smoke test is `pip install -e . && firestarter --help`, i.e. exactly the no-extra install. The branch is trivially testable (`monkeypatch.setitem(sys.modules, "usb", None)`).
3. **PREDICTED: Windows WinUSB/Zadig.** Raw USB access to a DFU device on Windows requires a WinUSB driver installed via Zadig — *"an external tool install in all but name"*, which is precisely the constraint the seed was written to avoid. The seed's verdict stands: the DFU path is the **runner-up**, and landing it **does not retire the self-flash bootloader seed**. A phase artifact must say so, or the seed gets quietly closed by implication.
4. **PROVEN-adjacent: DFU opcode values are asserted against the module's own constants.** `tests/test_py32_dfu.py` imports `DFUSE_ERASE_PAGE`, `DFUSE_SET_ADDRESS`, `FLASH_BASE` from `py32_dfu` and asserts against them — a source==source oracle for the *values*, exactly the class the project killed in v1.13 ("non-vacuous PASS oracle kills source==source false-PASS"). The *sequencing* assertions are genuinely independent and good (block numbering `[2,3,4]`, zero-length terminator, `wTransferSize` honoured, DfuSe-vs-DFU-1.1 fork). Only the opcode literals are unanchored.

**Credit where due, and it matters for scoping:** the two safety defects found against real hardware are both **fixed and properly tested** on the branch. `test_runtime_only_bus_is_refused_and_untouched` and `test_named_runtime_device_is_detached` cover the webcam class (`04f2:b751` advertising a DFU runtime interface — an early revision would have `DFU_DETACH`ed it and flashed Firestarter firmware into it); the implementation refuses ambiguity and only touches a runtime interface when explicitly named via `--usb-id`. `test_explicit_board_conflicting_with_attached_board_is_refused` + `test_default_board_still_yields_to_detection` cover the `board_to_use = current_board or board_override` defect (which really did flash a live Leonardo during development), and the fix uses `ctx.get_parameter_source("board")` so it refuses a *typed* `--board` conflict without over-refusing the default. `test_avr_asset_name_is_unchanged`, `test_avr_path_is_not_routed_to_dfu` and `test_avr_board_still_requires_a_port` are explicit AVR non-regression legs. `_install_with_avrdude` is untouched by the branch.

**The generalisable class:** *any host code that selects a physical target from an enumeration must refuse ambiguity rather than pick a default, and the identity it acts on must be the one the operator named.* Both defects were instances. Both only surfaced against real hardware. The third instance is waiting somewhere in port selection, and cannot be found by unit tests.

**How to avoid:**
- **[MECHANICAL]** Add `pyusb` to the `test` extra (or a dedicated CI leg installing `.[test,py32]`) plus one test that imports the real `usb` module and asserts the API surface the code depends on. Without this, py3.9-vs-py3.11 pyusb behaviour differences are invisible.
- **[MECHANICAL]** Delete the `pragma: no cover` and test the `PyusbMissingError` branch.
- **[MECHANICAL]** Assert the DFU opcode literals against the spec: one test containing `assert DFUSE_SET_ADDRESS == 0x21` / `DFUSE_ERASE_PAGE == 0x41` with a UM1504/DFU-1.1 citation, so the values are anchored outside the module.
- **[MECHANICAL]** A test asserting `firestarter fw --list` / `--help` succeeds with `pyusb` absent (import-time independence). The lazy import at `py32_dfu.py:373` is correct today; a future top-level import would break every AVR user's `fw` command.
- **[MECHANICAL]** `fw --install` **flashes the attached board and ignores `--board`** unless the conflict guard fires — it is not a dry run. Use `fw` / `--list` / `--dfu-probe` for smoke tests. Any plan step that runs `fw --install` against attached hardware must be an explicit human gate.
- **[JUDGEMENT]** State in the phase artifact that the self-flash bootloader seed remains open, and record the PCB consequences (BOOT0/nBOOT1 strapping, SWD pads, contiguous 8-bit port confirmed against the final package, flash budget reservation for bootloader + app + dual-slot CRC config in 128 KiB, and whether reboot-into-bootloader is a protocol command). These are cheap while the board is paper.

**Phase to address:** host integration (**suggested 126**) for 1–4 and the packaging gates; the PCB/flash-path decision record (**suggested 128**) for the seed and its consequences.

---

### Pitfall 11: The portability abstractions that were *not* actually introduced

**What goes wrong:**
**PROVEN.** PROJECT.md and STATE.md describe `agent/portability-macros` as providing *"`rurp_millis()`/`rurp_delay_ms()`/`rurp_delay_us()` so common code never calls Arduino timing APIs."* Against the branch, that is false. `RURP_DELAY_US` / `RURP_DELAY_MS` / `RURP_MILLIS` / `RURP_MICROS` have **zero call sites in `src/` or shared `include/`** — grepped. Their only consumers are `platform/py32f071/src/usb_cdc.c` and `platform/py32f071/include/Arduino.h`.

Shared code still calls Arduino APIs directly: `delay(100)` / `delay(500)` (`hardware_operations.cpp:37,57`), `delayMicroseconds(10)` + `delay(2/20)` (`flash_type_4.cpp:113,150,158,162,166`), `delay(FLASH_ERASE_DELAY_MS)` (`flash_type_3.cpp:83`), `millis()` (`operation_utils.cpp:111-112`, `flash_utils.cpp:34-35`), `delay(2)` (`rurp_common.cpp:32`).

**The ARM target compiles this by shipping a 76-line fake `platform/py32f071/include/Arduino.h`** that defines `delay`/`delayMicroseconds`/`millis`/`micros` as inline wrappers over `RURP_*`. That is a legitimate porting technique and it explains why the AVR flash delta is ~zero — *no shared code changed*. But it means:

- **PREDICTED:** the timing-abstraction work is still owed. Any future phase that "finishes the HAL" by rewriting those ~12 call sites to `RURP_DELAY_US(...)` is the change that can alter AVR generated code, and it has **not** been measured. The +22/−56 B figures do **not** cover it.
- **PREDICTED:** the fake `Arduino.h` sits first on the ARM include path. Any shared code that starts using a *new* Arduino API compiles on AVR and fails (or worse, silently resolves elsewhere) on ARM — and per Pitfall 4, nothing builds ARM on `beta` to notice.

Two further shared-header changes that *did* land, both AVR-measured-clean but worth naming:

- `include/rurp_shield.h` converts six control macros (`rurp_chip_enable`, `rurp_chip_disable`, `rurp_chip_output`, `rurp_chip_input`, `rurp_set_chip_enable`, `rurp_set_chip_output`) from function-like macros to `static inline` functions, and converts `rurp_set_programmer_mode`/`rurp_set_communication_mode` from `((void)0)` macros to empty `static inline` bodies in the `#else` of `#ifdef SERIAL_ON_IO`. `SERIAL_ON_IO` is set for `uno` and `uno328pb` only — so the macro→function conversion lands on **Leonardo and native**, two of the four incumbent verification surfaces. Measured: Leonardo flash **−56 B**, native 141/141. Clean, but the golden register traces are the thing that proves *behaviour* identical, not the size.
- `include/avr/pgmspace.h` (new) intercepts `#include <avr/pgmspace.h>` for **every** translation unit in the repo and re-emits it via GCC's `#include_next` on AVR. This works (AVR builds clean) and depends on `include/` preceding the toolchain's include dir. It also shadows the seven per-test `test/native/avr/*/avr/pgmspace.h` stubs, which is the proximate mechanism behind Pitfall 1.

**How to avoid:**
- **[MECHANICAL]** Correct the recorded description of what `agent/portability-macros` does, in the requirements, before it becomes a success criterion nobody can satisfy. It is a *compat-shim* layer, not a timing-abstraction layer.
- **[MECHANICAL]** If any phase rewrites shared timing call sites, gate it on: golden register traces byte-identical, `pio test -e native` case count equal, and AVR flash/RAM deltas recorded against 2600 B / 546 B.
- **[MECHANICAL]** Assert the golden register traces are byte-identical across the merge, by blob SHA on `test/native/avr/_shared/*` — and note the SIXTH CORRECTION item 7 caveat: the whole-file blob-SHA shorthand is **retired for `_shared/sdp_expected.h`** (Phase 119 added four `SDP_FIXED_LOCK_*` arrays); use per-array byte-identity there.

**Phase to address:** **124** for the merge-as-is; the timing rewrite should be explicitly **out of v1.23 scope** unless a phase owns its measurement.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|---|---|---|---|
| Hand-maintained CMake `FIRESTARTER_COMMON_SOURCES` list duplicating PlatformIO's implicit `src/**` | ARM target builds today | Silent divergence forever; a file added to `src/` compiles on 3 targets and not the 4th, with no signal | Only with the manifest-drift gate (Pitfall 3). Never bare. |
| Fake `platform/py32f071/include/Arduino.h` shimming `delay`/`millis` | Shared code compiles for ARM with zero shared-code churn (and zero AVR risk — measured) | The portability work is owed, not done; a new Arduino API in shared code breaks ARM invisibly | Acceptable now, and honestly the right call for v1.23 — provided it is *described* as a shim, not as a HAL |
| `include/avr/pgmspace.h` intercepting every TU via `#include_next` | Legacy `<avr/pgmspace.h>` includes keep working unchanged | Include-order fragility; shadows the per-test stubs (caused Pitfall 1); 58 redefinition warnings/suite | Acceptable with the warning-count gate at zero |
| `# pragma: no cover` on the `PyusbMissingError` branch | Coverage floor stays green | The branch every plain-install user hits is the one never exercised | Never — it is a 3-line monkeypatch test |
| Mocking `find_dfu_interfaces` away in all DFU tests | No pyusb, no hardware needed; suite is fast and green | The pyusb API contract is untested in CI and untestable locally | Acceptable for the protocol layer; **not** as the only coverage — add one real-`usb`-import API-surface test |
| Leaving stray public `3.0.0b12` prereleases | No cleanup work | Community installers see a version that was never intended; the tag scan sequence is permanently shifted | Accepted by D-05; revisit only if it confuses a community installer |
| `81fa53c` living on `beta` only | Branch HEAD byte-matches Plan 122-03's recorded merge SHA | `ci.yml`'s standalone-checkout failure resurfaces at the next merge toward `main` | Acceptable while `main` is never merged; must be reintroduced at that merge |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|---|---|---|
| firestarter_app ↔ firmware source-scanning gates | Assuming a firmware rename fails the gate | It **SKIPs** it (PROVEN). Split the "repo absent" proxy from the "target missing" proxy; the latter must hard-fail |
| Proving "firmware untouched" | `git diff -- some/path` (passes vacuously on a wrong path) | `git -C /workspaces/firestarter status --porcelain` empty, or literal blob SHAs |
| The 72/79-commit merge | Reading "no conflicts" as "correct" | Structural proofs: every manifest path resolves; baseline flash/RAM/case-count equality; nine gates *run* and pass |
| `platform/py32f071/CMakeLists.txt` ↔ `src/**` | Adding a shared source and forgetting the ARM list | Manifest-drift checker + planted fixture |
| `beta-build.yml` + ARM asset | A literal `files:` path (fails the whole release on a broken ARM build) | A **glob** second `files:` line + `continue-on-error` on ARM steps + an "AVR assets present" assertion |
| ARM build ↔ version stamping | Building the ARM image in `py32f071.yml` and publishing it | Only `beta-build.yml` runs `update_version.py` + auto-commit; an image from any other job carries a stale `VERSION`, which *is* the host's update decision |
| ARM build ↔ `beta` | Assuming the ARM target is covered on `beta` | `py32f071.yml` has **no push trigger**; add one or fold into `beta-build.yml` in the same phase as the merge |
| PY32 SDK (`FetchContent` @ `0ed2f4b`) | Treating a network fetch in the release path as free | Keep the full-SHA pin; log the resolved SHA; never let the fetch gate the AVR release |
| GitHub release → PyPI (app) | Reading a green workflow as "the wheel is live" | 46 % historical miss (b4/b5/b6/b9/b10/b12 — PAT lacks `workflow` scope, suppressing `release.published`). Verify resolution; manual `publish.yml` dispatch is the norm |
| pyusb / libusb / Windows | Shipping a DFU path as if it needs no driver | WinUSB via Zadig on Windows; udev rule or root on Linux. The self-flash bootloader seed stays open |
| `firestarter fw --install` | Treating it as a dry run for smoke-testing | It flashes the attached board and ignores `--board` unless the conflict guard fires. Use `fw` / `--list` / `--dfu-probe` |
| `gsd-tools query commit` | Assuming it stays on the current branch | It silently switched checkouts on 2026-07-30 and reverted gitlinks. `git rev-parse --abbrev-ref HEAD` after every call |
| Meta `catalog-sync-check.yml`, firmware `build.yml` | Chasing them as red | Both are `main`-gated and dormant under this branch model. A known property |

---

## Performance / Budget Traps

Scale here is **flash bytes, RAM bytes and microseconds**, not users.

| Trap | Symptoms | Prevention | When it breaks |
|---|---|---|---|
| Leonardo flash ceiling | `pio run -e leonardo` at 90.9 %; **2600 B free** with `-D DEV_TOOLS` (the binding config — it *costs* 1292 B vs release) | Record Uno + Leonardo flash and RAM per plan against **2600 B**, not the stale 2992 B | Any shared-code growth; the timing-macro rewrite is the untested candidate |
| Leonardo RAM ceiling — **untracked** | 2014/2560, **546 B free**; no historical figure exists | Record RAM alongside flash every time. A `PROGMEM`→RAM regression is invisible in a flash number | A dispatch table, a non-`PROGMEM` string, a widened struct |
| PY32 RAM is 16 K, not 20 K | Linker `RAM : LENGTH = 16K`; `DATA_BUFFER_SIZE=512` (not the recorded 1024) | Correct the recorded figure; if 1024 is desired, prove it fits and that the host chunking follows | Raising the buffer without measuring |
| t_BLC / SDP timing headroom | Leonardo emits the 6-write SDP sequence in **572 µs against 600 µs** — 4.7 % margin (F-118-01); page-load 84/88 µs vs 100 µs max | Any change to shared timing/logging on the `0x0D` path must re-measure both windows | Adding a log call, a function-call layer, or a slower `delay` implementation into the window |
| Warning noise as a masking agent | 138 warnings/suite vs 80 on baseline, all macro redefinitions | Fix the redefinitions; gate `grep -c redefined` at 0 | Already broken on the merge — fix it in the integration phase |
| ARM build in the release critical path | Beta cut fails or is delayed by an SDK fetch or apt hiccup | Glob + `continue-on-error` + AVR-assets assertion | First transient network failure |

---

## Safety Mistakes (physical, not web)

| Mistake | Risk | Prevention |
|---|---|---|
| Provisional pin map with no enforcement | Wrong lines driven with a PROM seated once a PCB exists; a repeat of v1.18's pin-31 class | Make `RURP_PY32F071_PINMAP_PROVISIONAL` refuse energising operations; fix the dead `#error` **[MECHANICAL]** |
| Claiming a closed-loop VPP path works | An unvalidatable control loop on a 12–25 V rail | Land the seam only; native test asserting `MANUAL_ADJUSTMENT_REQUIRED` on every board **[MECHANICAL]** |
| Treating `rurp_read_voltage_mv()` output as a measurement | Uncalibrated ADC on a provisional pin returns plausible numbers | No VPP claim without a DMM; there is no DMM path without a PCB. State "not measured" |
| Selecting a USB device by position | An early revision would have `DFU_DETACH`ed a webcam (`04f2:b751`) and flashed Firestarter firmware into it | **Already fixed + tested.** Generalise: refuse ambiguity, act only on the named identity |
| A detected board beating a typed `--board` | Really did flash a live Leonardo during development | **Already fixed + tested** via `ctx.get_parameter_source`. Generalise to port selection too |
| Shipping the DFU install path on stable | Offering users a flash operation nobody has ever completed | `channel.py` + `BETA_ONLY_BOARDS`; graduation is deletion from the tuple. Keep the stable-build refusal tests |
| Chip seated during a sideload | Uno-class upload drives the shield bus (Leonardo exempt) | Standing bench discipline — chip OUT before sideload on Uno-class |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---|---|---|
| `pip install firestarter` then `fw --install --board py32f071` → bare `ImportError` | Dead end with no next step | `PyusbMissingError` with the `pip install 'firestarter[py32]'` hint — **already implemented**, just untested |
| A stable build offering `py32f071` in `--board` choices | User attempts an unvalidated flash | `available_boards()` filters the click `Choice` at import; refusal message names the pre-release install command — **already implemented** |
| "Install works" in release notes | A community member bricks a board they built to a different pin map | Ceiling-compliant wording enforced by the claim gate |
| DFU install requiring Zadig on Windows with no warning | Silent failure that reads as a bug | `doc/PY32F071-FIRMWARE-INSTALL.md` exists on the branch; keep its driver + bootloader-entry table in the shipped docs |
| A community `dev test` report arriving against a firmware the reporter cannot identify | Unattributable evidence | Known limitation: `_probe_port`'s `[\d.x]+` truncates the pre-release suffix, so the **host cannot distinguish b11 from b14**. Detect capability via an ack, never by gating on a version string |

---

## "Looks Done But Isn't" Checklist

- [ ] **Portability layer landed:** often missing `780a3fb`'s four compat helpers — verify `pio test -e native` reports **141 cases / 17 suites**, not just "green"
- [ ] **Merge complete:** often missing manifest reconciliation — verify every path in `platform/py32f071/CMakeLists.txt` resolves, and that `src/**` minus the allow-list equals the list
- [ ] **AVR non-regression:** often missing RAM and the *golden traces* — verify Uno/Leonardo flash **and** RAM against 23932/1573 and 26072/2014, and `_shared/*` blob SHAs (per-array for `sdp_expected.h`)
- [ ] **Cross-repo gates green:** often missing the run-vs-skip distinction — verify **3** skips with the firmware sibling present, and that no skip reason says "firmware ... absent"
- [ ] **ARM target builds:** often missing provenance — verify a workflow run URL + SHA; a local `pio` run says nothing about ARM
- [ ] **ARM covered on `beta`:** often missing a trigger — verify `py32f071.yml` has `push: branches: [beta]` or the `beta-build.yml` fold landed
- [ ] **Release asset published:** often still an Actions artifact — verify `firestarter_py32f071.hex` appears under a GitHub **release**, via a glob, from the job that ran `update_version.py`
- [ ] **ARM failure cannot block AVR:** often untested — verify with a deliberately broken ARM build that three AVR `.hex` assets still publish
- [ ] **VPP seam landed:** often just a comment — verify a native test asserts `MANUAL_ADJUSTMENT_REQUIRED` on every board and no `CONFIG_VERSION` bump occurred
- [ ] **Provisional pin map safe:** often prose-only — verify `RURP_PY32F071_PINMAP_PROVISIONAL` has a consumer that refuses energising operations, and that the `#error` guard can actually fire
- [ ] **Flash-persistent config:** often runtime-only — verify CRC-validated dual-slot flash records exist and `rurp_configuration_t`'s schema is untouched
- [ ] **DFU installer done:** often missing the real pyusb surface — verify a CI leg installs `.[test,py32]`, the `PyusbMissingError` branch is tested, and opcode literals are anchored to UM1504/DFU 1.1
- [ ] **Beta published:** often missing the PyPI half — verify PyPI resolution directly, not the workflow status
- [ ] **Claims within ceiling:** often gate-only — verify the claim gate is green **and** the blocking operator wording review happened
- [ ] **Seed not silently retired:** verify a phase artifact states the self-flash bootloader remains the intended primary route, and records the PCB consequences
- [ ] **ROADMAP corrections owed:** verify the stale v1.28 prior-art paragraph is corrected (all five claims) and the slot renumber landed (v1.28/v1.29 retired into v1.23; Binary Command Protocol v1.23 → v1.28; v1.24–v1.27 untouched)

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---|---|---|
| Portability-macros-only intermediate state committed | LOW | Cherry-pick `780a3fb`, or squash the two branches into one landing. `pio test -e native` confirms in ~80 s |
| Cross-repo gate silently skipping | LOW to find once the split-proxy checker exists; **HIGH if discovered after close** (the gate was reported green for a whole milestone) | Fix the proxy, re-run the nine-row sweep, and re-audit every artifact that cited a green gate |
| CMake manifest drift | LOW (configure-time error) for missing files; **MEDIUM** for missing *additions* (ARM silently compiles a different program) | Manifest gate; re-derive the list from `src/**` minus the allow-list |
| Merge landed semantically wrong, tests green | HIGH | Re-run the structural proofs against both parents; if a divergence is found, redo the merge with the v1.22 whole-file + superset-proof + empty-diff discipline |
| Broken ARM build blocked the AVR beta | MEDIUM | Fix the workflow, re-dispatch; the beta number advanced, so a version is burned |
| Spurious beta cut | MEDIUM (irreversible in the numbering) | Leave the prerelease public (D-05 precedent) or delete it; either way the tag scan sequence has moved |
| An overclaim reached a public artifact | HIGH (reputational; a stranger acted on it) | v1.22's C-5 shape: correct in place, record as a divergence flagged for accept-or-overturn, never a silent rewrite |
| Provisional pin map trusted near a PROM | **Potentially unrecoverable** (a destroyed part, or worse) | Prevention only. There is no recovery path, which is why the enforcement must be mechanical |

---

## Pitfall-to-Phase Mapping

Phase numbers are **suggestions** — v1.23 starts at Phase 123 and the roadmapper owns the spine. What is *not* negotiable is the ordering: **the gates and baselines must exist before the merge**, because their whole value is detecting what the merge changes.

| Pitfall | Prevention Phase | Verification |
|---|---|---|
| 1 — portability-macros breaks native | 124 (atomic landing), baseline in 123 | `pio test -e native` = 141 cases / 17 suites, equal to the recorded baseline |
| 2 — gates SKIP on rename | **123** (split the FW-absent proxy) | Rename experiment reproduced: with the sibling present, a moved firmware file **fails**, not skips. Skip census = 3 |
| 3 — conflict-free wrong merge | 123 (manifest gate) → 124 / 126 (merges) | Every manifest path resolves; flash/RAM/case-count equality; nine gates run+pass; `status --porcelain` proofs |
| 4 — ARM unbuildable locally / uncovered on `beta` | 124 (trigger) + 127 (fold) | Workflow run URL + SHA cited for every ARM claim; `py32f071.yml` triggers on `beta` |
| 5 — broken ARM blocks AVR beta | 127 | Deliberately-broken-ARM run still publishes three AVR `.hex` assets |
| 6 — `beta` push cuts a release | 129 (close), decision artifact before any push | `12X-DECISION.md` committed pre-push; cut tag read from `gh release list`; PyPI resolution verified directly |
| 7 — provisional pin map unenforced | 124 (refusal) + 125 (VPP seam) | `PINMAP_PROVISIONAL` has a consumer; `#error` guard proven able to fail; native test asserts refusal |
| 8 — overclaiming | **123** (author the claim gate) → 129 (enforce) | Claim gate green with ≥2 planted-violation fixtures **and** the blocking operator wording review recorded |
| 9 — hollow verification | 123 (checkers + fixtures), enforced 124–129 | Every new checker has a pytest proving it fails on a committed fixture; `grep -c redefined` = 0; test counts asserted |
| 10 — host packaging / silent no-op install | 126 | CI leg installs `.[test,py32]`; `PyusbMissingError` tested; opcode literals anchored; `fw --list` works with pyusb absent |
| 11 — abstractions not actually introduced | 123 (correct the record) | Requirements describe a compat-shim layer; the timing rewrite is explicitly out of scope or owns its measurement |

**Suggested spine (7 phases, 123–129):**

1. **123 — Non-regression baseline & gate hardening.** Record AVR flash/RAM + native counts; split the FW-absent proxy; author the CMake manifest gate, the orphan-provisional-macro gate, the warning-count gate and `check_permitted_claims.py`, each with planted fixtures. *No firmware code moves in this phase.*
2. **124 — Firmware integration merge** (atomic: portability + py32 stack, `780a3fb` included; provisional-pinmap refusal; `beta` build trigger).
3. **125 — Flash-persistent config + VPP control seam** (CRC dual-slot; `rurp_configuration_t` schema untouched; no `CONFIG_VERSION` bump; `MANUAL_ADJUSTMENT_REQUIRED` on every board).
4. **126 — Host DFU installer integration** (merge forward 79 commits; packaging + CI extras; pyusb API-surface leg; opcode anchoring; AVR path proven untouched).
5. **127 — Release-asset fold** (`beta-build.yml` after the version bump; glob; `continue-on-error`; broken-ARM negative test).
6. **128 — Flash-path decision record + PCB requirements + ROADMAP corrections** (self-flash bootloader stays primary; BOOT0/nBOOT1, SWD, contiguous port, flash budget; the five stale prior-art corrections; the slot renumber).
7. **129 — Close: honesty ledger, claim gate, release decision** (decision artifact before any push; cut tag read, not computed; PyPI verified directly; blocking wording review).

Hard ordering constraints, all evidence-backed: **123 before 124** (gates must predate the moves they detect); **124 atomic** (Pitfall 1); **124 before 127** (nothing to publish otherwise); **126 after 124** only if a host change depends on the firmware identity — otherwise 126 is independent and can run in parallel; **129 last, and its push is its own gate** (`--auto` auto-approves human-verify checkpoints).

---

## Sources

**Primary — verified in tree this session (2026-07-30):**
- `firestarter` @ `beta` `5c9160a`; `firestarter_py32_ci` @ `feature/py32f071-release-assets` `ad47c3b`; `firestarter_app` @ `beta` `e7d3ee8`; `firestarter_app_py32` @ `feature/py32f071-fw-install` `4ee64a1`
- Measured builds: `pio run -e leonardo -e uno`, `pio test -e native` — baseline, +portability-macros, +full-stack-merge (throwaway worktrees, since removed)
- Reproduced experiments: cherry-pick of `532997c c0c6695 b253092 adb133a 52d6c1f` (zero conflicts, native 0/17); `git merge --no-ff` both directions (zero conflicts); `mv src/proms/eeprom_28c.cpp` → 5 gate legs SKIP, exit 0; whole-app-suite skip census with and without the firmware sibling (33 → 3)
- `platform/py32f071/CMakeLists.txt`, `linker/PY32F071xB_FLASH.ld`, `include/boards/py32f071_rurp_shield.h`, `include/rurp_platform{,_compat}.h`, `include/avr/pgmspace.h`, `include/rurp_shield.h`, `platformio.ini`
- `.github/workflows/{beta-build,py32f071,build}.yml`, `.github/scripts/update_version.py`
- `firestarter/{channel,py32_dfu,firmware,cli_handlers}.py`, `pyproject.toml`, `tests/test_py32_dfu.py`, `.github/workflows/ci.yml`
- The nine cross-repo gates: `tools/check_{dispatch,is_memory_cmd_no_ifdef,no_log_in_sdp_window,devtest_orchestrator}.py`, `tools/gen_sdp_bus_config.py`, `tests/test_{sdp_table_parity,revision_constants_parity,sdp_bus_config_drift,dispatch_mirror,gen_validation_header,check_is_memory_cmd_no_ifdef,check_no_log_in_sdp_window}.py`, and `81fa53c`
- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/{check_permitted_claims.py,test_check_permitted_claims.py,fixtures/}`

**Project post-mortems (this repo's own record):**
- `.planning/PROJECT.md` v1.22 Archive — all eight ⚠ CORRECTION blocks; FOURTH item 4 (four gates broken in one phase; the vacuous `src/flash_utils.h` path trap), FIFTH item 3 (F-118-01, 572/600 µs) + item 5 (the checklist that worked), SIXTH item 3 (2992 B, `DEV_TOOLS` costs 1292 B) + item 7 (nine-row list; retired blob-SHA shorthand), SEVENTH item 5 (vacuous predicate) + item 9 (`status --porcelain` subsumes every path), EIGHTH items 5–7 + 9 (whole-file merge + superset proof; 46 % PyPI miss; `beta` push runs no gates; the half-mechanizable criterion)
- `.planning/RETROSPECTIVE.md` — hollow GATE-03 (lines 404, 409, 749), `0052c42` "22 tests PASS (zero-diff)" (889, 904), cross-repo gate coupling (897), stale fork base → unplanned integration phase (402, 724)
- `.planning/notes/py32f071-port-branch-state.md` — PR #47 weak-stub trap; four host seams; the two hardware-found safety defects
- `.planning/seeds/py32f071-no-external-tool-fw-install.md` — the rejected-route table; PCB requirements; why landing DFU does not retire the seed
- `.planning/STATE.md` §Milestone Context (v1.23), §Accumulated Context

**Corrections this research makes to the recorded record (all PROVEN):** Leonardo headroom 2600 B not 2992 B · Leonardo RAM 546 B free, previously untracked · py32 `DATA_BUFFER_SIZE` 512 not 1024 · PY32 RAM 16 K · `agent/portability-macros` is a compat-shim layer, not a timing abstraction (`RURP_DELAY_*` has zero shared-code call sites) · both merges are conflict-free, so the rebase risk is semantic drift, not conflict resolution · the FW-absent proxy converts renames into SKIPs.

---
*Pitfalls research for: adding the PY32F071 (Cortex-M0+) fourth board target and a USB-DFU host install path to Firestarter, with no silicon in existence*
*Researched: 2026-07-30*
