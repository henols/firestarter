# Phase 124: Firmware Integration Merge — Research

**Researched:** 2026-07-31
**Domain:** Cross-repo git landing mechanics, PlatformIO/CMake build-system integration, preprocessor-conditional refactor, CI evidence acquisition
**Confidence:** HIGH for everything measured locally; MEDIUM for the ARM/CI half (nothing ARM can be built here)

**Scope of this pass.** The ROADMAP flags Phase 124 `research-skip`. This pass was run as a
**falsification** pass: verify the in-tree facts `124-CONTEXT.md` asserts, and report the ones that
are wrong, stale, or unsatisfiable as worded. Settled scope was not re-litigated.

**Validation-ceiling compliance.** **No PY32F071 hardware exists.** Every number below was produced by
a command actually run in this session and is quoted as observed. Nothing here claims anything about
PY32F071 silicon, and no ARM size, timing or behavioural figure is asserted — `arm-none-eabi-gcc`,
`cmake` and `ninja` are absent from this devcontainer (verified: `command -v` returns nothing for all
three; `g++ 13`, `gcc`, `pio 6.1.19` are present).

---

## Summary

The landing itself is in far better shape than the surrounding evidence apparatus. `git merge --squash`
of `origin/agent/py32f071-toolchain` onto the current firmware milestone tip applies **cleanly**, and
the resulting tree is **byte-identical** to a true merge's tree. On that merged tree both native
environments report **exactly 141 cases / 17 suites**, AVR RAM is **unchanged on all three targets**,
and AVR flash moves **−56 B (Leonardo) / +22 B (Uno) / +28 B (uno328pb)** — independently reproducing
PROJECT.md correction 3 byte-for-byte, and satisfying MERGE-05's band as worded. The full host suite
(1155 passed / 3 environment-only skips) and every host source-scanning gate stay green against the
merged sibling, both before and after D-02's `DEV_TOOLS` conversion, which costs **zero** AVR flash and
RAM.

The problems are all in the *gates*, not the code. Three of them are unrecorded anywhere in CONTEXT,
ROADMAP or `123-NONREGRESSION.md`, and each will stop Phase 124 dead if the planner does not budget for
it: **(1)** `check_size_baseline.py` compares AVR flash/RAM for **strict equality**, so it exits 1 on
exactly the permitted deltas MERGE-05 licenses — it is not, as CONTEXT states, "how MERGE-05 becomes an
exit code"; **(2)** `check_build_warnings.py`'s native arm fails on arrival, because the merge takes
native macro-redefinition warnings from **360 → 998** (and the recorded 360 itself turns out to be a
warm-cache artifact — a cold build of the *unmerged* tree already measures **456**); **(3)** two
Phase-123 pytests assert `stdout.startswith("UNARMED:")` on the real tree and are **designed to expire**
the moment `platform/py32f071/` lands — they go red and stay red even after MERGE-02 and MERGE-04 are
fixed. The armed CMake-manifest gate also fires **9** violations, not the 2 predicted.

Two decision-level corrections matter. D-04's `FLASH_ACR_LATENCY_1` is not a typo — it is commit
`91c6e45`, a *deliberate* workaround made while `HAL_FLASH_MODULE_ENABLED` was absent; `d76910c` later
restored the module and nobody reverted it. And D-04's preferred proof shape is **not achievable**: the
pinned SDK's `RCC_HSICALIBRATION_24MHz` dereferences a factory-trim address at runtime, so no
compile-time system-clock constant exists to `static_assert` against. D-11's refusal placement also
needs re-siting: `src/firestarter.cpp` — where `is_memory_cmd`'s only production caller lives — is
**not compiled by `pio test -e native`**, so a refusal there is structurally unprovable by the very
test MERGE-04 demands.

**Primary recommendation:** land with `git merge --squash` (tree target `693ffdf`), then plan for
**five** gate-repair work items the CONTEXT does not name — the AVR size-policy gap, the native warning
watermark, the two expiring UNARMED tests, the 7 extra CMake reverse-omission violations, and the
native-compilation constraint on MERGE-04's refusal site.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Atomic landing (MERGE-01) | git / meta-history | — | Nothing compiles differently; it is a history-shape property, discharged by a range check |
| CMake source manifest (MERGE-02) | ARM build config | firmware `scripts/` gate | `check_cmake_manifest.py` is a textual gate; the real proof is a CI configure |
| CI trigger (MERGE-03) | GitHub Actions YAML | — | Verified by reading the workflow file on the post-landing tree |
| Pin-map refusal (MERGE-04) | shared op layer (`src/proms/`) | board header + CMake defines | Only `src/proms/` is compiled by `pio test -e native`; see Pitfall 4 |
| Size/RAM evidence (MERGE-05) | firmware `scripts/` + `pio run` | recorded baseline JSON | AVR only; ARM is not measurable here |
| Native suite evidence (MERGE-06) | `pio test` + `check_size_baseline.py --native-log` | — | Both envs, case **and** suite counts |
| Cross-repo gate sweep (MERGE-07) | host repo `tools/` + `tests/` | firmware `tests/` | Must run from a directory literally named `firestarter_app` with a `firestarter` sibling |
| In-branch defect fixes (MERGE-08) | ARM platform tree + shared headers | host parity tests | `DEV_TOOLS` conversion crosses into host-scanned text |

---

## Verified Facts (measured this session)

### Git topology

| Fact | Command | Observed |
|------|---------|----------|
| `agent/portability-macros` is an ancestor of `agent/py32f071-toolchain` | `git merge-base --is-ancestor` | **YES** [VERIFIED] |
| Branch counts vs `origin/beta` | `git rev-list --count` | portability-macros **5 ahead / 72 behind**; py32f071-toolchain **52 ahead / 72 behind**; feature/py32f071-release-assets **53 ahead / 72 behind** [VERIFIED] |
| Firmware milestone branch position | `git rev-list --count` | `v1.23-py32f071-integration` @ `34bda8c` = **14 ahead / 0 behind** `origin/beta` [VERIFIED] |
| Merge base | `git merge-base HEAD origin/agent/py32f071-toolchain` | `a1953c22862ac3fb1e0111985946644a568aee36` [VERIFIED] |
| `780a3fb` is on the branch being landed | `git merge-base --is-ancestor 780a3fb origin/agent/py32f071-toolchain` | **YES** — `780a3fbe746eb751477e913631f4ff44b3ad35aa`, 2026-07-21, *"Complete non-AVR program-memory compatibility helpers"* [VERIFIED] |
| The 52 commits are linear | `git log --first-parent` count == `git rev-list` count | 52 == 52; the 5 portability commits are the **oldest** 5 [VERIFIED] |
| `platform/py32f071/` absent at the portability tip | `git ls-tree -r origin/agent/portability-macros` | **0 paths** — the Criterion-1 hazard is real [VERIFIED] |

### The landing, executed in a scratch clone

```bash
git clone --shared --no-checkout /workspaces/firestarter <scratch>/fw
git -C <scratch>/fw checkout v1.23-py32f071-integration          # 34bda8c
git -C <scratch>/fw merge --squash origin/agent/py32f071-toolchain
```

Observed: `Automatic merge went well; stopped before committing as requested` — **zero conflicts against
the CURRENT tip**, not an older tree. `git status --porcelain` shows **22 paths**: 20 added, 2 modified
(`include/rurp_serial_utils.h`, `include/rurp_shield.h`).

**Tree equality (the acceptance criterion for MERGE-01):**

| Landing | Tree SHA |
|---------|----------|
| `git merge --squash` + commit | `693ffdfd9c01039b12045c1053ec21e688413878` |
| true `git merge` (no-ff) | `693ffdfd9c01039b12045c1053ec21e688413878` |
| | **IDENTICAL** [VERIFIED] |

The squash loses nothing but parentage. Recompute this SHA at execute time — it is a function of both
tips and will change if either moves.

### D-06's Criterion-1 range check, prototyped and discriminating

```bash
for c in $(git rev-list <fork_point>..HEAD); do
  git cat-file -e "$c:include/rurp_platform_compat.h" 2>/dev/null || continue
  git rev-parse -q --verify "$c:platform/py32f071" >/dev/null || echo "VIOLATION $c"
done
```

| Landing shape | Commits scanned | Violations |
|---------------|-----------------|-----------|
| squashed | 15 | **0** |
| true merge | 67 | **5** — `52d6c1f`, `adb133a`, `b253092`, `c0c6695`, `532997c` |

D-05's reasoning is **fully confirmed**: a true merge produces exactly the five reachable commits
Criterion 1 forbids. [VERIFIED]

### Post-landing measurements (clean builds, scratch clone)

| Env | Baseline (BASE-01) | Merged | Merged + D-02 | Delta |
|-----|-------------------|--------|---------------|-------|
| leonardo flash | 26072 | **26016** | **26016** | **−56 B** |
| leonardo RAM | 2014 | **2014** | **2014** | **0** |
| uno flash | 23932 | **23954** | **23954** | **+22 B** |
| uno RAM | 1573 | **1573** | **1573** | **0** |
| uno328pb flash | 23976 | **24004** | **24004** | **+28 B** |
| uno328pb RAM | 1579 | **1579** | **1579** | **0** |
| native | 141 cases / 17 suites | **141 / 17** | **141 / 17** | 0 |
| native_nodevtools | 141 cases / 17 suites | **141 / 17** | **141 / 17** | 0 |
| AVR warnings (all three) | 0 | **0** | **0** | 0 |

MERGE-05 is satisfied as worded (Leonardo shrinks; Uno-class +22/+28 ≤ 64 B; RAM unchanged) and
MERGE-06 is satisfied as worded. PROJECT.md correction 3 reproduced byte-exactly. [VERIFIED]

Golden traces: `test/native/avr/_shared/sdp_expected.h` blob is `dd1ba1cce60d8aa8934e8c067ed82ad85cfd3b83`
**before and after** the merge — unchanged. [VERIFIED]

---

## The Five Unrecorded Work Items

These are the highest-value output of this pass. None appears in `124-CONTEXT.md`, the ROADMAP, or
`123-NONREGRESSION.md`.

### W-1 — `check_size_baseline.py` is a byte-identity gate, **not** a MERGE-05 policy gate

CONTEXT `<canonical_refs>` states these scripts "are how MERGE-05/MERGE-06 become exit codes." The
script's own docstring says it *"Turns MERGE-05's rule (Leonardo flash must not grow, Uno-class ≤ 64 B)
… into an exit code."* **The implementation does not do that.** `compare_avr()` (`scripts/check_size_baseline.py`)
asserts `flash_used != rec["flash_used"]` → failure. There is no tolerance, no band, no `--policy` flag
(argv accepts only `--baseline`, `--avr-log`, `--native-log`, `--rebuild`).

Observed against the merged evidence:

```
FAIL:
  leonardo: flash_used baseline=26072 observed=26016
  uno: flash_used baseline=23932 observed=23954
  uno328pb: flash_used baseline=23976 observed=24004
exit=1
```

Every one of those three lines is a **permitted** MERGE-05 outcome. The native arm is fine —
`PASS: native(cases=141,suites=17), native_nodevtools(cases=141,suites=17)`, exit 0 — so **MERGE-06 is
already an exit code; MERGE-05 is not.**

Options for the planner (pick one, do not leave it implicit):
- **(a) Add a policy mode** to `check_size_baseline.py` (e.g. `--policy merge05`) implementing
  "Leonardo `<=` baseline, Uno-class `<= baseline + 64`, RAM `==` baseline". Strongest; honours the
  standing exit-code tie-breaker. Cost: editing a Phase-123 checker mid-milestone, and `tests/test_checker_convention.py`'s
  conventions apply (its `FLOOR`/`FIXTURE_FLOOR` are `>=` assertions, so adding is safe).
- **(b) Re-baseline**: write a post-landing baseline JSON, point the existing gate at it via the
  documented `--baseline PATH` / `FIRESTARTER_SIZE_BASELINE` seam, and record the BASE-01→new deltas in
  `124-NONREGRESSION.md`. Cheap, and it arms Phases 125–129 with a byte-identity gate. But the MERGE-05
  band judgment then rests on a human comparison of two files.
- **(c) Both** — (b) for the ongoing gate, (a) for the one-shot MERGE-05 assertion. This is the shape
  that satisfies both the requirement text and the tie-breaker.

### W-2 — the BASE-06 native warning watermark fails on arrival, and 360 is a warm-cache number

Measured with the documented counting command
(`pio test -e <env> 2>&1 | grep -cE 'warning: *"[^"]+" +redefined'`), same clone, same env:

| Tree | Cold build (first run in a fresh clone) | Warm build (immediate re-run) |
|------|---------------------------------------|-------------------------------|
| pre-merge (`34bda8c`) | **456** | **360** |
| merged | **1166** | **998** |

Two separate findings:

1. **The merge raises native warnings by +638 (warm) / +710 (cold).** `check_build_warnings.py` exits 1
   on every one of these: `native_nodevtools: macro_redefinition observed=998 exceeds recorded=360`.
   Mechanism, read out of the compiler output: `include/rurp_platform_compat.h` now defines the
   program-memory macros, and ArduinoFake's `pgmspace.h` redefines them. The per-macro breakdown grows
   from **8 macros × 57 TUs** to **14 macros × ~84 TUs** — the six new names (`strncpy_P`, `strcmp_P`,
   `sprintf_P`, `strncmp_P`, `PGM_P`, `F`) are exactly `780a3fb`'s additions. This is benign (they are
   identical-purpose redefinitions) but it is not zero, and the gate cannot tell.
2. **The recorded 360 is not reproducible from a cold build.** Phase 123 touched **no** firmware source
   or `test/` file (`git diff --name-only 5c9160a..34bda8c` hits only `tests/` and `scripts/`), so the
   compiled tree is byte-identical to the tree BASE-01 measured. A cold run of that identical tree
   measures **456**; only a warm re-run measures 360. The baseline JSON's `meta.note` asserts every
   figure came from a clean build; for the two native envs that does not hold.

Consequence: Phase 124 must either re-measure the watermark honestly (and record *which* build state
the number belongs to), or raise it with a measured justification. Guessing it down is explicitly
forbidden by the script's own docstring. Note the **AVR** arm is unaffected and stays green:
`PASS: leonardo: macro_redefinition=0 (== 0), uno: … 0, uno328pb: … 0`, exit 0, on clean builds of the
merged tree.

### W-3 — two Phase-123 pytests are designed to expire at this landing

`firestarter/tests/test_check_cmake_manifest.py::test_unarmed_on_the_real_tree_with_no_seam_override`
and `tests/test_check_orphan_provisional.py::test_unarmed_on_the_real_tree_with_no_seam_override` both
assert:

```python
assert result.returncode == 0, "expected exit 0 on the real, still-unarmed tree."
assert result.stdout.startswith("UNARMED:")
```

Their docstrings say *"This must stay true until Phase 124 lands the port."* Measured on the merged tree
in a correctly-named `firestarter` directory:

```
2 failed, 46 passed
```

against `123-NONREGRESSION.md` row F1's recorded **48 passed, 0 skipped**. These two do **not** recover
when MERGE-02 and MERGE-04 are fixed — a fixed gate prints `PASS:`, not `UNARMED:`. **Phase 124 must
rewrite both tests** (invert them to assert the armed `PASS:` shape) and re-record F1's expected count.

*(A third failure, `test_checker_convention.py::test_scope_is_firmware_only`, appears only if the
firmware checkout directory is not literally named `firestarter`. It is an artifact of scratch
directory naming, not a real defect — but it does mean the firmware pytest, like MERGE-07's host sweep,
has a literal-directory-name requirement.)*

### W-4 — the armed CMake-manifest gate fires **9** violations, not 2

Run against the merged tree:

```
FAIL: 9 violation(s) in platform/py32f071/CMakeLists.txt:
  FIRESTARTER_COMMON_SOURCES: '${REPOSITORY_ROOT}/src/proms/flash_type_3.cpp' -> … (not found)
  FIRESTARTER_COMMON_SOURCES: '${REPOSITORY_ROOT}/src/proms/flash_type_4.cpp' -> … (not found)
  src/boards/leonardo_rurp_shield.cpp: present in tree, not named …, not covered by a reasoned PY32_EXCLUDED entry
  src/boards/rurp_common.cpp: …
  src/boards/uno_rurp_shield.cpp: …
  src/dev_tools.cpp: …
  src/proms/flash_5v_page.cpp: …
  src/proms/flash_nor_unlock.cpp: …
  src/rurp_config_utils.cpp: …
exit=1
```

Two are the forward rename defect (MERGE-02). **Seven** are reverse-omission violations. Five of those
seven are exactly D-15's five `PY32_EXCLUDED` lines — **verified**: the tree has 20 sources under
`src/`, the manifest names 15 of them, and the 5 unnamed are precisely
`leonardo_rurp_shield.cpp`, `rurp_common.cpp`, `uno_rurp_shield.cpp`, `dev_tools.cpp`,
`rurp_config_utils.cpp`. The other two (`flash_5v_page.cpp`, `flash_nor_unlock.cpp`) disappear the
moment MERGE-02's rename fix lands. So the gate goes 9 → 0 with one two-line rename plus D-15's five
comment lines — but the planner must expect **9**, not 2, in the first armed run.

`check_orphan_provisional.py` fires as predicted: 1 violation,
`RURP_PY32F071_PINMAP_PROVISIONAL: zero consumers outside its own definition (include/boards/py32f071_rurp_shield.h:38)`,
exit 1.

### W-5 — MERGE-04's refusal cannot sit where CONTEXT implies

See Pitfall 4. `src/firestarter.cpp` is not compiled by `pio test -e native`.

---

## The In-Branch Defects (MERGE-08), Corrected

### D-04 — `FLASH_ACR_LATENCY_1` is a deliberate commit, not a typo

`platform/py32f071/src/main.cpp:48` on the toolchain tip:

```c
if (HAL_RCC_ClockConfig(&clocks, FLASH_ACR_LATENCY_1) != HAL_OK)
```

Commit `91c6e45` (*"Use PY32 flash latency constant"*, 2026-07-21 12:46) changed it **from**
`FLASH_LATENCY_1` **to** `FLASH_ACR_LATENCY_1`. Reading the SDK at the pinned commit
`0ed2f4b4d3391eccfd4491006a30295fd78e32c2` (fetched via `gh api`, since the SDK is `FetchContent`-only
and not present locally), `Drivers/PY32F071_HAL_Driver/Inc/py32f071_hal_flash.h`:

```
133: #define FLASH_LATENCY_0   0x00000000UL         /*!< FLASH Zero wait state SYSCLK<=24MHz */
134: #define FLASH_LATENCY_1   FLASH_ACR_LATENCY_0   /*!< FLASH One wait state 24MHz<SYSCLK<=48MHz */
135: #define FLASH_LATENCY_2   FLASH_ACR_LATENCY_1   /*!< FLASH Two wait state 48MHz<SYSCLK<=72MHz */
```

So the code currently passes the numeric value of **`FLASH_LATENCY_2`** — two wait states. D-04's
diagnosis is **correct**. Two supplementary facts the planner should carry:

- **Why the swap happened, and why the revert is safe now.** At `91c6e45`, `platform/py32f071/include/py32f071_hal_conf.h`
  did **not** define `HAL_FLASH_MODULE_ENABLED` and did not include `py32f071_hal_flash.h` — so
  `FLASH_LATENCY_1` was undefined and `FLASH_ACR_LATENCY_1` (a CMSIS device-header constant) was the
  only thing that compiled. Commit `d76910c` (*"Complete PY32 HAL module configuration"*, three minutes
  later) added both the `#define` and the `#include`. `91c6e45` was never reverted. On the tip being
  landed, `FLASH_LATENCY_1` **is** in scope. [VERIFIED — `git show d76910c -- …py32f071_hal_conf.h`]
- **Severity framing.** More wait states than required is functionally safe; this is an
  over-conservative setting, not a fault. Do not write it up as a correctness bug.

**D-04's preferred proof shape is not achievable.** The configured clock is HSI at 24 MHz
(`oscillator.HSICalibrationValue = RCC_HSICALIBRATION_24MHz`) × `RCC_PLL_MUL2`, `AHBCLKDivider = RCC_SYSCLK_DIV1`
→ 48 MHz. But in the pinned SDK:

```
373: #define RCC_HSICALIBRATION_24MHz  ((0x4<<13) | ((*(uint32_t *)(0x1FFF3220)) & 0x1FFF))
```

That **dereferences a factory-trim address at runtime**. It cannot appear in a `static_assert`.
`RCC_PLL_MUL2` is `0x00000000U` — a register field value, not a multiplier. **The SDK does not expose
the system clock as a compile-time constant**, so D-04's "compile-time assertion tying the chosen
latency to the configured clock" is off the table. What *is* achievable and worth doing:

```c
/* FLASH_LATENCY_1 == FLASH_ACR_LATENCY_0 (one wait state, 24 MHz < SYSCLK <= 48 MHz);
 * FLASH_LATENCY_2 == FLASH_ACR_LATENCY_1. Passing the raw ACR mask selected two
 * wait states at 48 MHz. SDK 0ed2f4b, Drivers/PY32F071_HAL_Driver/Inc/py32f071_hal_flash.h:133-135. */
static_assert(FLASH_LATENCY_1 != FLASH_ACR_LATENCY_1,
              "FLASH_ACR_LATENCY_1 is FLASH_LATENCY_2 (two wait states) - do not reintroduce it");
```

This is a real compile-time regression guard (both operands are SDK compile-time macros) and it is the
honest maximum. Note it can only be evaluated in CI — no local ARM toolchain exists.

### D-01 — `write_checksums.cmake` orphan status confirmed

`git grep -n write_checksums origin/agent/py32f071-toolchain -- .` returns **nothing**; the file exists
at `platform/py32f071/cmake/write_checksums.cmake` (blob `20d8ab7`). Repo-wide grep across the host repo
and `.planning/` finds only planning-document mentions. The functionality it would have provided is
already done inline in `py32f071.yml` (`sha256sum … > firestarter-py32f071.sha256`, steps at lines
75-101). **D-01's deletion is correct and has no consumer to break.** [VERIFIED]

### D-02 — the `DEV_TOOLS` conversion, measured

**Exactly six code sites**, matching CONTEXT's list precisely:

| File | Line | Note |
|------|------|------|
| `include/firestarter.h` | 42 | gates `CMD_DEV_ADDRESS` / `CMD_DEV_REGISTER` |
| `include/dev_tools.h` | 11 | wraps the whole body **including** its `#include "firestarter.h"` |
| `src/dev_tools.cpp` | 8 | wraps the whole file **including** every `#include` |
| `src/firestarter.cpp` | 21, 97, 271 | include guard, debug-log pair, dispatch arm |

`platformio.ini:26` carries `-D DEV_TOOLS` in the shared `[env]` block → expands to `DEV_TOOLS=1`;
`[env:native_nodevtools]` omits it; the py32 CMakeLists' `target_compile_definitions` (lines 99-108)
never mentions it. **No `platformio.ini` edit is needed** — D-02 confirmed. [VERIFIED]

**Trap the planner must avoid:** `grep -c '#ifdef DEV_TOOLS'` returns **4** in `include/firestarter.h`
and **4** in `src/firestarter.cpp`, because comment prose contains the literal string
(`firestarter.h:51,70,73`; `firestarter.cpp:79`). A naive replace-all rewrites documentation that
deliberately describes the *old* mechanism. Use a line-anchored match:

```python
re.compile(r'^#ifdef DEV_TOOLS$', re.MULTILINE).sub('#if DEV_TOOLS', text)
```

Applying exactly that to the six sites and adding the default block yields **6 conversions, 0 residual**
line-anchored `#ifdef DEV_TOOLS`, with all comment prose preserved. [VERIFIED by running it]

**AVR cost is genuinely zero, measured not assumed.** Clean rebuilds of all three AVR targets on
merged+D-02 produce flash/RAM byte-identical to merged-only (26016/2014, 23954/1573, 24004/1579) and
warning count 0. Both native envs stay at 141/17. [VERIFIED]

**The named header-guard trap does NOT fire.** `_find_header_guard_line_indices`
(`firestarter_app/tests/test_revision_constants_parity.py:242`) was exercised directly against two
modified copies of the real header:

| Placement | Guard detected as | `conditional_names` | `test_conditionally_compiled_defines_are_exactly_the_dev_tools_pair` |
|-----------|-------------------|---------------------|------------------------------------------------------------------|
| control (unmodified) | `(7, 196)` `#ifndef __FIRESTARTER_H__` | `{CMD_DEV_ADDRESS, CMD_DEV_REGISTER}` | **PASS** |
| **A** — block above the header guard | `(7, 200)` **`#ifndef DEV_TOOLS`** ← misidentified | `{CMD_DEV_ADDRESS, CMD_DEV_REGISTER}` | **PASS** |
| **B** — block inside the guard, beside `DATA_BUFFER_SIZE` | `(7, 200)` `#ifndef __FIRESTARTER_H__` | `{CMD_DEV_ADDRESS, CMD_DEV_REGISTER}` | **PASS** |

The reason it survives: `_DEFINE_PATTERN` is `r"^[ \t]*#[ \t]*define[ \t]+((?:CMD|FLAG)_[A-Za-z0-9_]+)…"`
— it only captures `CMD_*`/`FLAG_*` names, so `#define DEV_TOOLS 0` is never recorded as a define at
all. Placement A still **misidentifies the header guard** and only passes because the spurious `#endif`
decrement exactly cancels the un-skipped real guard's `#ifndef` increment — correct by arithmetic
accident. **Use placement B.** It has an in-tree precedent five lines away:
`include/firestarter.h:16-18` already carries `#ifndef DATA_BUFFER_SIZE / #define DATA_BUFFER_SIZE 512 / #endif`.

**One semantic caveat on "a single default in a shared header".** `include/dev_tools.h:11` and
`src/dev_tools.cpp:8` evaluate their conditional **before** including anything, so the default in
`firestarter.h` is not in scope at those two sites. Behaviour is still correct — ISO C/C++ evaluates an
undefined identifier in `#if` as `0`, which is the intended default — but the `#ifndef/#define` block
is *documentary* there, not load-bearing. If the planner ever adds `-Wundef`, those two sites need the
default pulled into a dependency-free header included unconditionally at the top of each. Say this in
the commit message rather than implying the default covers all six sites.

**Host blast radius: zero.** Against the merged sibling with D-02 applied:

| Gate | Observed |
|------|----------|
| `tools/check_is_memory_cmd_no_ifdef.py` | **PASS**, exit 0 — "no preprocessor conditional and enumerates exactly the eight expected commands", predicate body lines 113-127 |
| `pytest tests/test_revision_constants_parity.py` | **13 passed** |
| full host suite | **1155 passed, 3 skipped** |
| `tools/check_no_log_in_sdp_window.py` | **PASS**, exit 0 |
| `tools/check_dispatch.py` | **PASS**, exit 0 — 746 chips, 0 regressions |
| `tools/check_devtest_orchestrator.py` | **PASS**, exit 0 |
| `tools/check_no_exists_proxy.py` | **PASS**, exit 0 — 78 files scanned |

The 3 skips are `test_audit_coverage_matrix.py` and `test_variant_decode_evidence_stability.py` looking
for **meta-repo** artifacts that do not exist under a scratch path; in the real `/workspaces` layout
they resolve, giving `123-NONREGRESSION.md`'s recorded **1158 passed, 0 skipped**. **No skip cited
firmware absence.** [VERIFIED]

---

## MERGE-02 / MERGE-03 — CI Evidence Mechanics

### `workflow_dispatch` on a non-default branch: empirically YES

The documented GitHub precondition is that a `workflow_dispatch` workflow must be on the **default
branch**. Measured facts:

| Fact | Observed |
|------|----------|
| Repo default branch | `main` (`gh api repos/henols/firestarter --jq .default_branch`) |
| `py32f071.yml` on `main` | **absent** |
| `py32f071.yml` on `beta` | **absent** |
| `py32f071.yml` on `agent/py32f071-toolchain`, `feature/py32f071-release-assets` | **present** |
| Workflow registered | id **316560577**, `.github/workflows/py32f071.yml`, state `active`, 115 total runs |
| **A `workflow_dispatch` run on a non-default branch already succeeded** | run **30376185746**, event `workflow_dispatch`, branch `feature/py32f071-release-assets`, sha `ad47c3b`, conclusion **success** — <https://github.com/henols/firestarter/actions/runs/30376185746> |
| `gh` auth | account `henols`, scopes include `workflow`; repo permissions `admin: true` |

**Verdict:** D-08 is workable. The precedent run is the evidence, not the documentation — once a
workflow has a registered id, dispatching it against a ref where the file exists works in this repo.
Once the landing puts `py32f071.yml` on `v1.23-py32f071-integration`, the same path is available.
Confidence MEDIUM-HIGH (empirical precedent on the same workflow id and repo, different ref).

**Fallback if a dispatch on the milestone branch is rejected:** the three green runs at the toolchain
tip (`29831254712` / `29831285320` / `29831339029`, event `pull_request`, sha `e5abb51`, all **success**)
show the `pull_request` trigger works. A draft PR from `v1.23-py32f071-integration` into `beta` would
fire it — but CONTEXT D-08 already declines that because it attaches a public artifact Phase 130 owns.
Second fallback: temporarily push a branch that a `pull_request` already targets. Prefer asking the
operator over inventing a third route.

**Exact commands (execute-time, behind D-09's gate):**

```bash
# 1. push the milestone branch (fires NOTHING - see trigger table below)
git -C /workspaces/firestarter push -u origin v1.23-py32f071-integration

# 2. dispatch
gh workflow run py32f071.yml --repo henols/firestarter --ref v1.23-py32f071-integration

# 3. capture the run URL + SHA (the two things MERGE-02's evidence must cite)
gh run list --repo henols/firestarter --workflow py32f071.yml --branch v1.23-py32f071-integration \
    --limit 1 --json databaseId,headSha,conclusion,event,url

# 4. wait / read result
gh run watch <databaseId> --repo henols/firestarter
```

### Pushing the milestone branch fires nothing

Every workflow trigger on the **post-landing** tree, read from the YAML:

| Workflow | Triggers |
|----------|----------|
| `beta-build.yml` | `push: branches: [beta]` (with `paths-ignore`), `workflow_dispatch` |
| `build.yml` | `push: branches: [main]`, `pull_request: branches: [main]` |
| `py32f071.yml` | `pull_request:` with a `paths:` filter, `workflow_dispatch` |

`v1.23-py32f071-integration` matches **no** `push` branch filter. MERGE-03 adds `push: branches: [beta]`
to `py32f071.yml`, which likewise cannot fire on this branch. **No beta prerelease can be cut by this
push.** D-08's safety argument is confirmed. [VERIFIED]

### The rename defect is real and currently invisible to CI

`platform/py32f071/CMakeLists.txt:40-41` names `flash_type_3.cpp` / `flash_type_4.cpp`. Those files
exist on the **py32 branch's own tree** (72 commits behind `beta`, i.e. before v1.19 Phase 104's
rename), which is why its three `pull_request` runs are green. They do **not** exist on the merged tree
— `src/proms/` has `flash_nor_unlock.cpp` and `flash_5v_page.cpp`. PROJECT.md correction 2 is confirmed;
its line reference "46-47" is wrong, CONTEXT's "40-41" is right. `DATA_BUFFER_SIZE=512` is at line
**107** (CONTEXT correct; PROJECT.md correction 7's "113" is wrong). [VERIFIED]

---

## MERGE-04 — The Refusal, Made Concrete

### (a) Insertion point: `configure_memory()`, not the `is_memory_cmd` call site

**The constraint CONTEXT misses.** `[env:native]`'s source filter is:

```
build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>
```

`src/firestarter.cpp` — home of `is_memory_cmd`'s **only production caller** (line 86) — is **not
compiled into the native test binary**. `include/firestarter.h:100-108` says so explicitly, and it is
the stated reason `is_memory_cmd` is `static inline` in the header rather than a `.cpp` function. A
refusal placed at the admission point is therefore as unprovable-by-native-test as the
`py32f071_rurp_shield.cpp` placement D-11 rejects.

**The reachable chokepoint is `configure_memory()` at `src/proms/memory.cpp:42`:**

- It is under `src/proms/` → compiled into **both** native envs.
- `src/firestarter.cpp:91` calls it via `op_execute_function(configure_memory, handle)` inside the
  `is_memory_cmd(handle->cmd)` arm — so it sits behind exactly D-12's eight commands, with no
  hand-maintained second list.
- It already NULLs the three operation function pointers at lines 44-46, so the
  `configure_not_implemented` shape (`src/proms/not_implemented.cpp`) drops straight in:
  NULL the three pointers, `LOG_ERROR_ID_U8(MSG_ERR_NOT_SUPPORTED, (uint8_t)handle->cmd)`,
  `handle->response_code = RESPONSE_CODE_ERROR`.
- `MSG_ERR_NOT_SUPPORTED` is `0xA5` at `include/messages.h:82` — D-13 confirmed. (`messages.h` is
  codegen-generated from the meta repo's `messages.toml`; D-13's whole point is to avoid touching it,
  and reusing an existing id does.)
- **Existing native suites already exercise it**: `test/native/avr/test_dispatch/test_configure_memory.cpp`
  (also listed in the host's `scan_paths.ALL_CROSS_REPO_PATHS`), plus `test_val_sram` at lines 122/139,
  and every `test_val_*` suite.

Under a platform-neutral macro that AVR never defines, `#if RURP_PINMAP_PROVISIONAL` compiles to nothing
on all three AVR targets → zero flash cost, consistent with the measured `+22/+28/−56` staying put.

### (b) Defining the macro for one suite only

PlatformIO `build_flags` are **environment**-scoped, not suite-scoped, and `build_src_filter` compiles
`src/proms/memory.cpp` **once per environment**. A `#define` at the top of one test `.cpp` therefore
cannot change how the shared object was compiled. Two workable shapes:

- **A third environment** — e.g. `[env:native_pinmap_provisional]` with
  `build_flags = ${env:native.build_flags} -D RURP_PINMAP_PROVISIONAL=1` and a `test_filter` naming
  **only** the new suite. This tests the genuine production path. **Hard constraint:** the new suite
  must NOT be added to `[env:native]` or `[env:native_nodevtools]`'s `test_filter` — both are pinned at
  17 entries and MERGE-06 asserts 141 cases / 17 suites on both. Also do **not** feed the new env to
  `check_build_warnings.py` unless it is added to the baseline's `warnings` block first (an unknown env
  name is exit 2 there).
- **A `static inline` predicate in a shared header** (e.g. `rurp_pinmap_refuses(uint8_t cmd)` returning
  `is_memory_cmd(cmd)` under `#if RURP_PINMAP_PROVISIONAL`), consumed by `configure_memory()`. A test
  file can then `#define RURP_PINMAP_PROVISIONAL 1` before the `#include` and assert all eight commands
  refuse, in one suite, with no `platformio.ini` change. `is_memory_cmd` itself is the in-tree precedent
  for exactly this technique, for exactly this reason.

The second is cheaper and does not perturb the pinned env pair; the first is stronger evidence. If both
are affordable, do both — the header seam proves the predicate, the third env proves `configure_memory`
actually consults it.

### (c) `check_orphan_provisional.py` — satisfiable, with one gotcha

The consumer scan covers `SCAN_DIRS = ("include", "src", "platform", "test")` with suffixes
`.h/.hpp/.c/.cpp`. Two consequences:

1. **`firestarter/tests/` is NOT scanned.** D-14's fire-proof pytest cannot serve as the consumer that
   silences this gate. The consumer must live in `include/`, `src/`, `platform/` or `test/`.
2. `DEFINE_RE` matches `RURP_[A-Z0-9_]*_PROVISIONAL`. Introducing a new neutral
   `RURP_PINMAP_PROVISIONAL` does **not** discharge the existing
   `RURP_PY32F071_PINMAP_PROVISIONAL` at `include/boards/py32f071_rurp_shield.h:38` — **both** must have
   consumers. The clean shape is for the board header to consume the py32-specific flag in order to
   define the neutral one:

   ```c
   #if RURP_PY32F071_PINMAP_PROVISIONAL
   #define RURP_PINMAP_PROVISIONAL 1
   #endif
   ```

   That single block makes the py32 flag consumed (a `#if` test) and the neutral flag defined; the
   `configure_memory()` guard then consumes the neutral one. Both satisfied, one consumer each.
   `#undef`s and comment-only mentions are explicitly excluded by the checker, so neither shortcut works.

### (d) Proving the `#error` fires — mechanically confirmed

`g++` is present (`/usr/bin/g++`); `arm-none-eabi-gcc` is not. A dependency-free fragment header
preprocesses fine with the host compiler. Executed:

| Arm | Command | Observed |
|-----|---------|----------|
| macro unset | `g++ -E -I. tu.c -o /dev/null` | **exit 1**, `pinmap_guard.h:3:2: error: #error "…"` |
| macro `=1` | `g++ -E -I. -DRURP_PY32F071_PINMAP_CONFIGURED=1 tu.c -o /dev/null` | **exit 0** |
| macro `=0` | `g++ -E -I. -DRURP_PY32F071_PINMAP_CONFIGURED=0 tu.c -o /dev/null` | **exit 1**, same `#error` |

Three discriminating arms, all mechanical. Note `#if !defined(X) || !X` is needed if "unset" must also
fire — a bare `#if !X` treats an undefined `X` as `0` and *would* fire, but stating the `defined()` half
makes the intent explicit and survives a later `-Wundef`.

D-14's supporting claims check out: `include/boards/py32f071_rurp_shield.h` `#include`s `py32f0xx_hal.h`
at file line 6 (so the full header is unpreprocessable locally — hoisting is mandatory, not stylistic),
and the hollow guard is exactly where CONTEXT says: `#define RURP_PY32F071_PINMAP_CONFIGURED 1` at
line **37**, `#define RURP_PY32F071_PINMAP_PROVISIONAL 1` at line **38**, `#if !RURP_PY32F071_PINMAP_CONFIGURED`
→ `#error` at lines **71-73**. [VERIFIED]

`firestarter/tests/` is PIO-invisible: `platformio.ini` sets no `test_dir`, so PlatformIO uses the
default `test/`. And **both** firmware CI workflows run `pytest tests/ -v` (`build.yml` line 108,
`beta-build.yml` line 66) on `ubuntu-latest`, which has `g++` — so the fire-proof runs in CI, not just
locally. [VERIFIED]

---

## MERGE-06 — The Golden-Trace Comparison, Made Concrete

`test/native/avr/_shared/sdp_expected.h` holds **nine** `static const sdp_strobe_t` arrays:

| Array | Entries |
|-------|---------|
| `SDP_SHIPPED_DIP28_28C256` | 54 |
| `SDP_FIXED_DIP28_28C256` | 54 |
| `SDP_FIXED_DIP28_28C64` | 54 |
| `SDP_FIXED_DIP24_2816` | 54 |
| `SDP_FIXED_DIP32_28C512_EEPROM` | 54 |
| `SDP_FIXED_LOCK_DIP28_28C256` | 30 |
| `SDP_FIXED_LOCK_DIP28_28C64` | 30 |
| `SDP_FIXED_LOCK_DIP24_2816` | 30 |
| `SDP_FIXED_LOCK_DIP32_28C512_EEPROM` | 33 |

Consumers: `test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` and
`test/native/avr/test_sdp_harness/test_sdp_harness.cpp`.

"Byte-identical, per-array" is therefore discharged by **three** mechanical checks, not one:

1. **Blob identity of the fixture**: `git rev-parse <ref>:test/native/avr/_shared/sdp_expected.h` must
   equal `dd1ba1cce60d8aa8934e8c067ed82ad85cfd3b83` at both the fork point and the landing. **Already
   verified identical across the merge.**
2. **Per-array inventory**: the nine names and their entry counts above, re-extracted and compared — so
   an array that is *deleted* (and whose consuming assertions vanish with it) is caught, which a
   whole-file diff of an edited file would also catch but a passing test suite would not.
3. **The two consuming suites pass** — covered by the 141/17 count, which both envs meet.

`_shared/sdp_bus_config.h` and `_shared/validation_matrix.h` are also in the host's cross-repo scan-path
inventory and are likewise untouched by the merge.

---

## MERGE-07 — The Nine Gates, Post-Landing

Executed from a directory literally named `firestarter_app` with a merged `firestarter` sibling
(merge + D-02 conversion applied):

| Row | Gate | Observed |
|-----|------|----------|
| H1 | `tools/check_no_log_in_sdp_window.py` | **PASS** exit 0 — emitter lines 298-314, poll lines 348-361 (unchanged from 123's record) |
| H2 | `pytest tests/test_check_no_log_in_sdp_window.py` | passed (within the full-suite run) |
| H3 | `pytest tests/test_sdp_table_parity.py` | passed |
| H4a | `tools/check_is_memory_cmd_no_ifdef.py` | **PASS** exit 0 — predicate body lines **113-127** (was 109-123 pre-D-02; the +4 is D-02's default block) |
| H4b | `pytest tests/test_check_is_memory_cmd_no_ifdef.py` | passed |
| H5 | `tools/gen_sdp_bus_config.py` idempotence | not re-run (writes into the firmware tree; deferred to execute time) |
| H6 | `pytest tests/test_sdp_bus_config_drift.py` | passed |
| H7 | `pytest tests/test_revision_constants_parity.py` | **13 passed** |
| H8 | `pytest tests/test_dispatch_mirror.py` | passed |
| H9a | `tools/check_dispatch.py` | **PASS** exit 0 — 746 chips, 736 supported, 0 regressions, 0 consistency violations |
| H9b | `tools/check_devtest_orchestrator.py` | **PASS** exit 0 |
| — | full host suite | **1155 passed, 3 skipped** (3 = meta-repo artifacts absent under a scratch path) |
| — | `tools/check_no_exists_proxy.py` | **PASS** exit 0, 78 files scanned |

**No gate's scan path is invalidated by the landing.** `scan_paths.ALL_CROSS_REPO_PATHS` resolves six
firmware paths — `doc/PROTOCOLS.md`, `include/firestarter.h`, `src/proms/eeprom_28c.cpp`,
`test/native/avr/_shared/sdp_bus_config.h`, `test/native/avr/_shared/validation_matrix.h`,
`test/native/avr/test_dispatch/test_configure_memory.cpp`. The merge **adds** 20 files and **modifies**
only `include/rurp_serial_utils.h` and `include/rurp_shield.h`; neither is in the inventory.
`include/firestarter.h` **is** in the inventory and **is** edited by D-02 — and the whole suite stays
green through it. A-7's fail-open hazard did not materialise here. [VERIFIED]

**The gates that do break are all in the firmware repo**, not the host repo: W-1 (`check_size_baseline.py`
AVR arm), W-2 (`check_build_warnings.py` native arm), W-3 (two expiring pytests), W-4 (armed CMake
manifest, 9 violations) and the orphan-provisional gate (1 violation, as designed).

---

## Common Pitfalls

### Pitfall 1: treating `check_size_baseline.py` as MERGE-05's exit code
**What goes wrong:** the plan claims MERGE-05 is discharged by a green gate; the gate is red on the
correct answer. **How to avoid:** W-1 above — decide the policy shape explicitly, in the plan.

### Pitfall 2: re-measuring the native warning watermark in the wrong build state
**What goes wrong:** cold vs warm builds differ by ~96 warnings pre-merge and ~168 post-merge, and the
recorded 360 is a warm number. A plan that says "re-measure and compare" without pinning the build
state produces an irreproducible figure. **How to avoid:** state the exact sequence (fresh clone vs
`pio run -t clean` vs warm re-run) in the plan step, and record it in `124-NONREGRESSION.md` next to the
number. Never lower the watermark without a measured justification (the script's docstring forbids it).

### Pitfall 3: `sed`-replacing `#ifdef DEV_TOOLS` globally
**What goes wrong:** four comment occurrences in `firestarter.h` and one in `firestarter.cpp` describe
the *historical* mechanism (including Phase 119's LOCK-02/LOCK-03 rationale). Rewriting them destroys
the record and makes the comments claim something false. **How to avoid:** line-anchored regex, verified
by `grep -c` before and after (expect `firestarter.h` 4 → 3, `firestarter.cpp` 4 → 1).

### Pitfall 4: putting MERGE-04's refusal where `pio test -e native` cannot see it
**What goes wrong:** the natural site (`src/firestarter.cpp:86`, the `is_memory_cmd` admission arm) is
excluded by `build_src_filter`. The test that MERGE-04 requires cannot be written. **How to avoid:**
`configure_memory()` in `src/proms/memory.cpp`. See MERGE-04 (a).

### Pitfall 5: adding the provisional-refusal suite to `[env:native]`'s `test_filter`
**What goes wrong:** 17 becomes 18, MERGE-06's suite-count assertion fails, and the failure looks like a
regression. **How to avoid:** a separate env with its own `test_filter`, or a header-seam test placed
inside an existing suite that keeps the count at 141/17 — in which case the *case* count changes
instead, which is equally fatal. Read the count assertion before choosing.

### Pitfall 6: assuming the two Phase-123 UNARMED tests recover once the gates are fixed
**What goes wrong:** they assert `stdout.startswith("UNARMED:")`, which a *fixed, armed* gate never
prints. **How to avoid:** rewrite both in the same plan that lands the port; re-record F1's expected
count in `124-NONREGRESSION.md`.

### Pitfall 7: running the firmware pytest from a differently-named directory
**What goes wrong:** `tests/test_checker_convention.py::test_scope_is_firmware_only` asserts the
resolved scripts path ends in `("firestarter", "scripts")`. **How to avoid:** run it from
`/workspaces/firestarter`. This mirrors MERGE-07's `firestarter_app` literal-name requirement.

### Pitfall 8: citing a local `pio` run as ARM evidence
Forbidden by the Validation Ceiling and impossible here anyway. Every ARM claim needs a run URL + SHA.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Producing the atomic landing | a scripted `read-tree`/patch-apply pipeline | `git merge --squash <tip>` then one commit | Proven clean against the current tip; tree byte-identical to a true merge |
| Proving Criterion 1 | a human reading `git log` | the `git rev-list` loop in "D-06's Criterion-1 range check" | Discriminates squash (0) from merge (5) mechanically |
| Refusing the eight bus commands | a new hand-listed command set | `is_memory_cmd()` behind `configure_memory()` | The set cannot drift, and `check_is_memory_cmd_no_ifdef.py` keeps it conditional-free |
| A refusal response | a new `MSG_ERR_*` id | `MSG_ERR_NOT_SUPPORTED` (0xA5) + cmd ordinal | `messages.h` is codegen-generated from the meta repo; a new id costs a regen plus host parity churn |
| The refusal's code shape | a bespoke error path | mirror `configure_not_implemented()` (`src/proms/not_implemented.cpp`) | Six lines, already the in-tree template, already natively tested |
| Firing the `#error` in a test | an ARM cross-compile | `g++ -E` on a dependency-free fragment | Proven three-armed above; `arm-none-eabi-gcc` is absent, `g++` is present and already used by `check_build_warnings.py`'s paired pytest |
| Recording evidence | prose in a SUMMARY | `124-NONREGRESSION.md` in `123-NONREGRESSION.md`'s shape | D-16; command / expected / observed per row |

---

## Project Constraints (from CLAUDE.md)

- **Constants/flag-bit parity**: `firestarter_app/firestarter/constants.py` ↔ `firestarter/include/firestarter.h`
  must change together. D-02 edits `firestarter.h` but adds **no** `CMD_*`/`FLAG_*` define, so no
  `constants.py` change is required — **verified** by `test_revision_constants_parity.py` staying at 13
  passed.
- **`firestarter/include/messages.h` is codegen-generated** from the meta repo's canonical
  `tools/catalog/messages.toml` and is never hand-edited. D-13's reuse of `MSG_ERR_NOT_SUPPORTED`
  respects this; the deferred dedicated-id option does not.
- **Serial protocol changes** must stay in sync between `serial_comm.py` and `firestarter.cpp` — this
  phase changes no wire behaviour on AVR.
- **Board buffer sizes**: py32's `DATA_BUFFER_SIZE=512` (CMakeLists line 107) is wire-visible via v1.10
  CAP-01. Out of scope here; flagged for Phases 127/128.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `gh workflow run --ref v1.23-py32f071-integration` will succeed for `py32f071.yml` | MERGE-02/03 | MEDIUM — based on a same-workflow precedent run on a *different* non-default branch, not on this ref. If rejected, MERGE-02's evidence needs the draft-PR fallback, which touches Phase 130's territory. Test it early, behind D-09's gate. |
| A2 | The `static_assert(FLASH_LATENCY_1 != FLASH_ACR_LATENCY_1, …)` compiles under `arm-none-eabi-gcc` with `-fno-exceptions -std=c++17` | MERGE-08 / D-04 | LOW — both operands are SDK integral macros; but nothing ARM compiles here, so only the CI run proves it. |
| A3 | The 3 host-suite skips are purely scratch-path artifacts and become 0 in `/workspaces` | MERGE-07 | LOW — the skip reasons name `.planning/` paths explicitly, and `123-NONREGRESSION.md` H13 records 1158 passed / 0 skipped in the real layout. Re-run in place to confirm. |
| A4 | Re-running `gen_sdp_bus_config.py` (H5) stays idempotent post-landing | MERGE-07 | LOW — the merge does not touch `sdp_bus_config.h` (blob unchanged), but this row was deliberately not re-run here because it writes into the firmware tree. |
| A5 | A third `[env:native_*]` environment does not perturb the two pinned envs | MERGE-04/06 | LOW — `test_filter` is per-env; but `check_build_warnings.py` exits 2 on an env name absent from the baseline's `warnings` block, so do not feed it the new env. |

---

## Corrections to `124-CONTEXT.md` and the upstream record

This is the section the planner should read first.

| # | Claim | Source | Status | Evidence |
|---|-------|--------|--------|----------|
| C-1 | *"`check_size_baseline.py`, `check_build_warnings.py` — these are how MERGE-05/MERGE-06 become exit codes"* | CONTEXT `<canonical_refs>` | **HALF FALSE** | MERGE-06 yes (`PASS: native(cases=141,suites=17)…` exit 0). MERGE-05 **no** — `compare_avr()` is strict equality and exits 1 on the permitted −56/+22/+28. See W-1. |
| C-2 | *"123-NONREGRESSION … predicts which violations fire on arrival"* | CONTEXT `<canonical_refs>` | **INCOMPLETE** | Predicts 2 gates. Actual: CMake manifest fires **9** (not 2); `check_build_warnings.py`'s native arm **also** fires (unpredicted, 360 → 998). See W-2, W-4. |
| C-3 | *(unstated anywhere)* two Phase-123 pytests expire at this landing | — | **MISSING WORK ITEM** | `test_check_cmake_manifest.py` and `test_check_orphan_provisional.py` both assert `startswith("UNARMED:")`; merged tree → **2 failed, 46 passed** vs F1's recorded 48/0. See W-3. |
| C-4 | D-11: refusal *"in the shared operation layer … because a native test proves it"* | CONTEXT D-11 | **UNDER-SPECIFIED / would fail as implied** | `build_src_filter` excludes `src/firestarter.cpp`, home of `is_memory_cmd`'s only caller. The refusal must go in `src/proms/` (`configure_memory()` at `memory.cpp:42`). |
| C-5 | D-04: *"a compile-time assertion tying the chosen latency to the configured clock if the pinned SDK exposes the clock as a compile-time constant"* | CONTEXT D-04 | **NOT ACHIEVABLE** | `RCC_HSICALIBRATION_24MHz` = `((0x4<<13) \| ((*(uint32_t *)(0x1FFF3220)) & 0x1FFF))` — a runtime pointer dereference (SDK `0ed2f4b`, `py32f071_hal_rcc.h:373`). Fall back to the constant-identity `static_assert` + cited comment. |
| C-6 | D-04 framing implies a typo/oversight | CONTEXT D-04 | **INCOMPLETE** | It is commit `91c6e45`, a deliberate workaround for a then-missing `HAL_FLASH_MODULE_ENABLED`; `d76910c` restored the module 3 min later and the swap was never reverted. Also: two wait states at 48 MHz is over-conservative but **safe**, not a fault. Say so. |
| C-7 | D-02: *"a single `#ifndef DEV_TOOLS / #define DEV_TOOLS 0` default in a shared header"* covers every site | CONTEXT D-02 | **PARTLY DECORATIVE** | `dev_tools.h:11` and `dev_tools.cpp:8` gate **before** including anything. Behaviour is still correct (`#if` on an undefined identifier is 0), but the default is not in scope there. |
| C-8 | *"the branch is 72 commits behind `beta`"* | prompt / PROJECT.md phrasing | **MISREAD** | The three **py32 source branches** are 72 behind. The **integration branch** `v1.23-py32f071-integration` is **14 ahead / 0 behind** `origin/beta`. No rebase or catch-up merge is needed. |
| C-9 | *"the landing is a `--no-ff` merge of `agent/portability-macros` **and** `feature/py32f071-release-assets`"* | `research/SUMMARY.md:266` | **SUPERSEDED** | By CONTEXT D-05 (squash) and D-07 (`ad47c3b` deferred to Phase 128). Recorded so a planner reading SUMMARY does not resurrect it. |
| C-10 | *"eliminate the 58 macro-redefinition warnings"* | `research/SUMMARY.md:266` | **UNDER-COUNTED BY ~11×** | Measured increase: **+638** (warm) / **+710** (cold). The 58 figure is not reproducible by the documented counting command. |
| C-11 | `platform/py32f071/CMakeLists.txt` — `DATA_BUFFER_SIZE` at line 113; rename defect at lines 46-47 | PROJECT.md corrections 2, 7 | **FALSE (line numbers)** | Actual: `DATA_BUFFER_SIZE=512` at line **107**; `flash_type_3/4.cpp` at lines **40-41**. CONTEXT has both right. |
| C-12 | D-14's fire-proof pytest under `firestarter/tests/` also satisfies the orphan-provisional consumer rule | implied by CONTEXT D-14 + `<discretion>` | **FALSE** | `check_orphan_provisional.py`'s `SCAN_DIRS = ("include","src","platform","test")` — **`tests/` is not scanned**. The consumer must live in one of those four. Also: **both** `RURP_PY32F071_PINMAP_PROVISIONAL` and any new neutral flag need their own consumer. |
| C-13 | BASE-01's `meta.note`: every figure measured via clean builds | `size_baseline.json` | **FALSE for the two native warning figures** | Phase 123 changed no compiled file; the identical tree measures **456** cold and **360** warm. The recorded 360 is a warm-cache number. |
| C-14 | D-08's push is safe — no beta prerelease can be cut | CONTEXT D-08 | **VERIFIED** | Post-landing triggers read from YAML: `beta-build.yml` push=`beta`; `build.yml` push=`main` + PR→`main`; `py32f071.yml` PR + dispatch (+ MERGE-03's `beta`). `v1.23-py32f071-integration` matches none. |
| C-15 | D-01 `write_checksums.cmake` has zero references | CONTEXT D-01 | **VERIFIED** | `git grep write_checksums origin/agent/py32f071-toolchain` → empty; checksumming is done inline in `py32f071.yml` steps 75-101. |
| C-16 | D-05's ancestry + reachability argument | CONTEXT D-05 | **VERIFIED** | Ancestor: yes. True merge → 5 violating commits (`52d6c1f`, `adb133a`, `b253092`, `c0c6695`, `532997c`); squash → 0. |
| C-17 | D-15's five `PY32_EXCLUDED` lines are the right set | CONTEXT D-15 | **VERIFIED** | Tree has 20 `src/` sources; manifest names 15; the 5 unnamed are exactly D-15's five. |
| C-18 | The named `_find_header_guard_line_indices` trap | CONTEXT `<canonical_refs>` | **DOES NOT FIRE** | Both placements pass (`_DEFINE_PATTERN` only captures `CMD_*`/`FLAG_*`). But placement A **misidentifies the guard** and passes only by arithmetic cancellation — use placement B, precedent at `firestarter.h:16-18`. |

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `pio` (PlatformIO Core) | MERGE-05, MERGE-06 | ✓ | 6.1.19 | — |
| `g++` | D-14 fire-proof, BASE-06 fixture | ✓ | `/usr/bin/g++` | — |
| `python3` + `pytest` | all gates | ✓ | pytest 9.1.1 | — |
| `gh` CLI | MERGE-02/03 evidence | ✓ | authed as `henols`, scopes incl. `workflow`, repo admin | — |
| `arm-none-eabi-gcc` | ARM configure/build/size | ✗ | — | **CI only** — run URL + SHA |
| `cmake` | ARM configure | ✗ | — | **CI only** |
| `ninja` | ARM build | ✗ | — | **CI only** |
| OpenPuya SDK `0ed2f4b` | `FLASH_LATENCY_*`, RCC macros | ✗ locally (FetchContent) | read via `gh api` this session | `gh api repos/OpenPuya/PY32F071_Firmware/contents/<path>?ref=0ed2f4b…` |

**Missing dependencies with no fallback:** none that block planning. **Missing with fallback:** the
entire ARM toolchain — every ARM claim routes through CI, exactly as the Validation Ceiling requires.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Firmware native | PlatformIO + Unity — `pio test -e native`, `-e native_nodevtools` |
| Firmware scripts | pytest — `python3 -m pytest tests/` (PIO-invisible; runs in both CI workflows) |
| Host | pytest — `python3 -m pytest` from `firestarter_app` |
| ARM | CMake + Ninja in `py32f071.yml` — **CI only** |

### Phase Requirements → Test Map

| Req | Behaviour | Type | Command | Exists? |
|-----|-----------|------|---------|---------|
| MERGE-01 | no commit carries the portability half alone | git range check | the `git rev-list` loop above | ❌ new script |
| MERGE-02 | manifest names the renamed files | textual gate | `python3 scripts/check_cmake_manifest.py` | ✅ (armed by the landing) |
| MERGE-02 | ARM configures **and** builds | CI | `gh workflow run py32f071.yml --ref …` + run URL/SHA | ✅ workflow exists |
| MERGE-03 | `push: branches: [beta]` present | read the YAML | `grep -A3 '^on:' .github/workflows/py32f071.yml` | ✅ |
| MERGE-04 | eight commands refused under the provisional flag | native suite | new suite (see MERGE-04 (b)) | ❌ new |
| MERGE-04 | `#error` provably fires | pytest + `g++ -E` | new test under `firestarter/tests/` | ❌ new |
| MERGE-04 | provisional flag has consumers | gate | `python3 scripts/check_orphan_provisional.py` | ✅ |
| MERGE-05 | AVR flash/RAM within policy | gate | `check_size_baseline.py` — **needs W-1 resolution** | ⚠ policy gap |
| MERGE-06 | 141 cases / 17 suites, both envs | gate | `check_size_baseline.py --native-log …` | ✅ **measured green** |
| MERGE-06 | golden traces byte-identical per array | blob SHA + array inventory | see MERGE-06 section | ❌ new (blob half trivial) |
| MERGE-07 | eleven gate rows run and pass | tools + pytest | see MERGE-07 table | ✅ **measured green** |
| MERGE-08 | `FLASH_LATENCY_1` in use | grep + CI build | `grep -n FLASH_ .../main.cpp` + run URL | ✅ |
| MERGE-08 | `write_checksums.cmake` gone | `git ls-tree` | `git ls-tree <ref> platform/py32f071/cmake/` | ✅ |
| MERGE-08 | ARM `DEV_TOOLS`-off explicit | read CMake defines + native counts | `grep DEV_TOOLS platform/py32f071/CMakeLists.txt` | ✅ |

### Sampling Rate

- **Per task commit:** the touched gate only (`pio test -e native` is ~105 s cold, ~40 s warm).
- **Per wave merge:** both native envs + all three AVR clean builds + the firmware pytest.
- **Phase gate:** the full `124-NONREGRESSION.md` sweep, re-executed in the closing plan (D-16).

### Wave 0 Gaps

- [ ] Criterion-1 range-check script (MERGE-01 / D-06)
- [ ] W-1 resolution: AVR size policy — new gate mode **or** re-baseline + recorded comparison
- [ ] W-2 resolution: native warning watermark re-measured with the build state pinned
- [ ] W-3: rewrite the two expiring `UNARMED` pytests
- [ ] MERGE-04 native refusal suite + the `g++ -E` fire-proof pytest
- [ ] Golden-trace per-array inventory check

---

## Security Domain

Firmware/build-integration phase; no network service, no authentication surface, no user input parsing
changes. ASVS categories V2/V3/V4 do not apply. The one security-adjacent property is **physical
safety**, and it is the phase's own MERGE-04 requirement.

| Concern | STRIDE | Mitigation in this phase |
|---------|--------|--------------------------|
| Provisional pin map energises a PROM on unknown hardware | Tampering / physical damage | MERGE-04's refusal at `configure_memory()`, gated by a flag whose orphan-status is machine-checked |
| A guard that cannot fire (false assurance) | Repudiation | D-14's hoisted fragment + the three-armed `g++ -E` fire-proof |
| Supply chain: pinned SDK fetched at configure time | Tampering | `GIT_TAG 0ed2f4b4d3391eccfd4491006a30295fd78e32c2` is a full SHA, not a tag or branch — immutable [VERIFIED, `CMakeLists.txt:16`] |
| Accidental public release from a CI push | Elevation of privilege (process) | Verified: no `push` trigger matches the milestone branch; D-09's operator gate on the push itself |

No external packages are installed by this phase, so the Package Legitimacy Audit is not applicable.

---

## Open Questions

1. **Which W-1 option does the operator want?**
   - Known: `check_size_baseline.py` is strict-equality; the deltas are permitted by MERGE-05.
   - Unclear: whether editing a Phase-123 checker inside Phase 124 is acceptable, given 123's premise
     was that gates predate the changes they judge.
   - Recommendation: option (c) — re-baseline for the ongoing gate, plus a one-shot policy assertion for
     MERGE-05 — and raise it at plan review, not at execute time.

2. **What is the honest native warning watermark?**
   - Known: 360 warm / 456 cold pre-merge; 998 warm / 1166 cold merged.
   - Unclear: which number Phase 123 intended to record.
   - Recommendation: re-measure cold, record the build state alongside the number, and note in
     `124-NONREGRESSION.md` that the BASE-01 figure was warm — a correction to the record, not a
     regression.

3. **Does `gh workflow run --ref v1.23-py32f071-integration` succeed?**
   - Known: the same workflow id dispatched successfully on a different non-default branch.
   - Unclear: nothing structural suggests it will not, but it is the one MERGE-02 blocker that cannot be
     tested without the outward-facing push D-09 gates.
   - Recommendation: make it the **first** step behind the D-09 checkpoint, so a failure is discovered
     before the rest of the phase is built on it.

---

## Sources

### Primary (HIGH confidence — measured or read in-tree this session)
- `git` on `/workspaces/firestarter` — ancestry, counts, merge/squash trees, range check
- `pio run` / `pio test` on a scratch clone — all size, RAM, case, suite and warning figures
- `firestarter/scripts/check_{size_baseline,build_warnings,cmake_manifest,orphan_provisional}.py` — docstrings and implementation
- `firestarter/platformio.ini` — `build_src_filter`, `test_filter`, `build_flags`
- `firestarter/include/{firestarter.h,dev_tools.h,messages.h}`, `src/{firestarter.cpp,dev_tools.cpp,proms/memory.cpp,proms/not_implemented.cpp}`
- `firestarter_app/tests/test_revision_constants_parity.py`, `tests/scan_paths.py`, `tests/fw_presence.py`, `tools/check_*.py`
- `firestarter/.github/workflows/{build,beta-build,py32f071}.yml`

### Primary (HIGH confidence — authoritative remote)
- GitHub Actions API via `gh` — workflow registry, run 30376185746, runs 29831254712/29831285320/29831339029, repo default branch and permissions
- OpenPuya SDK @ `0ed2f4b4d3391eccfd4491006a30295fd78e32c2` via `gh api` — `py32f071_hal_flash.h:133-135`, `py32f071_hal_rcc.h:373,425`

### Secondary (MEDIUM confidence)
- `.planning/phases/123-*/123-NONREGRESSION.md` — the eleven-row gate table and recorded expectations (several corrected above)
- `.planning/research/SUMMARY.md`, `STACK.md` — R-17, H-7 (corroborated); SUMMARY:266 (superseded)

### Tertiary (LOW confidence — not relied on)
- GitHub's documented `workflow_dispatch` default-branch requirement — contradicted by the empirical run in this repo; the run is what is cited.

---

## Metadata

**Confidence breakdown:**
- Landing mechanics (MERGE-01): **HIGH** — executed, tree-compared, range-checked
- AVR/native measurements (MERGE-05/06): **HIGH** — clean builds, reproduced PROJECT.md's figures byte-exactly
- Gate behaviour post-landing (MERGE-07 + W-1…W-4): **HIGH** — every gate actually run
- `DEV_TOOLS` conversion (MERGE-08 / D-02): **HIGH** — applied and measured end to end
- Flash latency (MERGE-08 / D-04): **HIGH** on the diagnosis and the SDK reading; **MEDIUM** on the `static_assert` compiling under ARM (unverifiable here)
- CI dispatch (MERGE-02/03): **MEDIUM-HIGH** — empirical precedent, different ref
- ARM build outcome after the rename fix: **NOT MEASURABLE HERE** — no ARM toolchain; CI only

**Research date:** 2026-07-31
**Valid until:** the moment either `v1.23-py32f071-integration` or `origin/agent/py32f071-toolchain`
moves — every SHA and tree hash above is tip-dependent. Re-run the landing check if more than a few days
pass.
