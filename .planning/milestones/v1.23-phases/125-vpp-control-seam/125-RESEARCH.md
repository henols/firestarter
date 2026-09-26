# Phase 125: VPP Control Seam — Research

**Researched:** 2026-07-31
**Domain:** AVR/ARM firmware capability seam; preprocessor-resolved platform properties; PlatformIO/CMake build-manifest gates; cross-repo source-scanning gates
**Confidence:** HIGH — every load-bearing claim below was produced by running a command in this devcontainer, on a throwaway copy of the firmware tree, and is quoted as observed output rather than as an expectation.

**Standing caveat, stated once and binding on everything below:** **no PY32F071 hardware exists.** Nothing in this document claims otherwise. ARM flash and RAM are not measurable here (`arm-none-eabi-gcc`, `cmake` and `ninja` are all absent — verified `command -v` → nothing); every ARM size or build claim must cite a CI workflow run URL + head SHA.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Copied verbatim from `125-CONTEXT.md` `<decisions>`. Research does **not** re-open these; where a decision rests on a factual claim that measurement falsified, the correction is filed in `## Corrections to 125-CONTEXT.md and the upstream record` and the decision's *intent* is preserved.

**The four-board proof (VPP-02, Criterion 2)**

- **D-01:** The four-board assertion is a **pytest under `firestarter/tests/` that compiles `src/rurp_vpp.cpp` with host `g++` four times**, once per board macro-set, links a minimal `main` that surfaces the return value, runs each, and asserts `MANUAL_ADJUSTMENT_REQUIRED`. One pytest invocation = criterion 2's "one run". **Not** a fourth PlatformIO env with namespaced wrapper TUs (rejected: the header is `extern "C"`, so four copies in one binary need `#define`-renaming gymnastics, and all four "boards" would still share a single native compile). **Not** the hybrid with static assertions compiled into the real target builds (rejected: it would put a new assertion into all four production builds, whose flash impact this phase would then have to measure and defend). Direct precedent: `firestarter/tests/test_pinmap_guard_fires.py` (Phase 124 D-14's `g++ -E` fire-proof). Note this shape sits **outside** BASE-08's checker convention — `tests/test_checker_convention.py` governs `scripts/check_*.py` only, so neither `FLOOR` (5) nor `FIXTURE_FLOOR` (10) needs bumping.
- **D-02:** `src/rurp_vpp.cpp` is **dependency-free by construction** — it includes only `rurp_vpp.h` (plus `<stdint.h>`). No `rurp_shield.h`, no `<Arduino.h>`, no PY32 HAL, no `rurp_get_config()`. PR #45 needed `rurp_shield.h` solely to reach the calibration fields in `rurp_configuration_t`, and dropping calibration drops the dependency for free. This is what makes D-01's harness need zero stub scaffolding, and it is a **standing constraint**: a later phase wanting config or hardware access must add the dependency deliberately.
- **D-03:** The harness is proven non-vacuous by a **forced-capability compile leg**: a leg compiling with `-DRURP_HAS_VPP_DAC=1` must produce a **non-zero `g++` exit** carrying a named `#error` (no board ships a VPP DAC implementation). This proves the capability macro is genuinely consulted rather than decorative — the direct antidote to the hollow-guard shape Phase 124 D-14 had to restructure. A planted mutated-seam fixture under `tests/fixtures/` was offered and **declined** as not worth the hand-maintained drift risk.
- **D-04:** The four board macro-sets are **hardcoded literals in the harness, plus one drift leg** asserting each board's defining macro still appears in its real build config (`platformio.ini` for the three AVR envs; `target_compile_definitions` in `platform/py32f071/CMakeLists.txt` for ARM). Explicitly **not** derived by parsing the build files — `tests/scan_paths.py`'s own stated principle ("deliberately explicit, never derived") applies, and the two build systems have incompatible define syntaxes, so a derived version is two parsers. The drift leg is the safety net that keeps the hardcoding honest.

**Where the capability macro gets its value (Criterion 2, anti-hollow)**

- **D-05:** **Operator fact, verbatim:** *"No arduino board will have the DAC so it must be set to disabled."* This is a **permanent** property of the AVR-class boards, not a provisional placeholder — the rail is set by the operator's pot. Record it as permanent wherever it is written; do **not** describe AVR manual control as "for now" or "pending hardware".
- **D-06:** `rurp_vpp.h` carries **no blanket default**. It resolves `RURP_HAS_VPP_DAC` in exactly two ways:

  ```c
  #if !defined(RURP_HAS_VPP_DAC)
  #  if defined(__AVR__)
  /* Permanent, not provisional: no Arduino/AVR-class RURP board carries a
   * VPP DAC — the rail is set by the operator's pot. Operator, 2026-07-31. */
  #    define RURP_HAS_VPP_DAC 0
  #  else
  #    error "RURP_HAS_VPP_DAC must be defined by the board/platform build"
  #  endif
  #endif
  ```

  `__AVR__` is **compiler-supplied**, so D-02's dependency-freedom survives — no `rurp_platform.h`, no `<Arduino.h>`. All three AVR targets are covered by one stated fact, uniformly, and **`platformio.ini` needs no edit**, which keeps the AVR flash delta attributable to source alone rather than to moved build flags. PR #45's shape (`#ifndef RURP_HAS_VPP_DAC / #define ... 0` unconditionally inside the header) was **rejected**: it makes "every board is manual" true because the header says so — structurally the same defect as Phase 124's hollow `#error` guard, one phase later.
- **D-07:** **Every non-AVR board must declare `RURP_HAS_VPP_DAC` explicitly**, and for py32f071 the declaration lives in the **CMake `target_compile_definitions` (`RURP_HAS_VPP_DAC=0`), not in `include/boards/py32f071_rurp_shield.h`.** This is Phase 124 D-14's lesson applied deliberately: the build system supplies what the header only tests. A fifth non-AVR board that forgets fails to compile rather than silently inheriting manual control near an unregulated rail.
- **D-08:** The `#error` arm gets its **own harness leg** — a compile with neither `__AVR__` nor an explicit `RURP_HAS_VPP_DAC` must fail. So the harness has (at minimum) six legs: four board macro-sets, one forced-DAC, one unset-and-non-AVR.

**Seam API surface (VPP-01)**

- **D-09:** The seam declares **three functions and nothing else**: `rurp_vpp_control_mode()`, `rurp_set_vpp_target_mv(target_mv, tolerance_mv, timeout_ms)`, `rurp_disable_vpp_control()`. **Dropped:** PR #45's three DAC hooks (`rurp_vpp_dac_write`, `rurp_vpp_control_enable`, `rurp_vpp_delay_ms`), the `RURP_VPP_DAC_BITS` macro and its consistency `#error` (unreachable now that `RURP_HAS_VPP_DAC=1` is itself an `#error` per D-03), and the whole calibration API (`rurp_calibrate_vpp_two_point`, `rurp_reset_vpp_calibration`, `rurp_vpp_calibration_valid`, `rurp_apply_vpp_calibration`, `rurp_read_voltage_uncalibrated_mv`). Rationale is Phase 124 D-01's rule verbatim: a declaration with no implementation and no consumer comes back **with a consumer attached**, or not at all.
- **D-10:** Each enum carries **exactly two enumerators**: `rurp_vpp_control_mode_t = { RURP_VPP_CONTROL_MANUAL = 0, RURP_VPP_CONTROL_DAC = 1 }` and `rurp_vpp_result_t = { RURP_VPP_OK = 0, RURP_VPP_MANUAL_ADJUSTMENT_REQUIRED = 1 }`. `RURP_VPP_CONTROL_DAC` and `RURP_VPP_OK` are unreachable today but each earns its place — `DAC` names the axis the seam exists to express (a mode enum with one mode expresses nothing) and `OK = 0` is the conventional success slot. PR #45's five-value result enum (`INVALID_ARGUMENT`, `TIMEOUT`, `OUT_OF_RANGE`) is **out**: all three are producible only by the closed-loop control code D-09 cuts, and their numbering would be inherited from a PR this phase must take nothing from.
- **D-11:** **Zero production callers this phase.** Nothing under `src/` or `platform/` calls the three functions, so `--gc-sections` is expected to drop them entirely. The macro's consumers are the `#if` in `src/rurp_vpp.cpp` and the `#if !defined` in `include/rurp_vpp.h` (both in `include/`/`src/`, which is where `check_orphan_provisional.py` would look were the macro `*_PROVISIONAL`-named — it is not, so that gate is not in play). Routing `hw_read_voltage()` through the seam was rejected as being `9134f2a` by another route; exposing the mode on the wire was rejected as cross-repo churn belonging to a later phase (see Deferred).

**ARM landing and evidence (VPP-01, VPP-03)**

- **D-12:** `src/rurp_vpp.cpp` is **named in `FIRESTARTER_COMMON_SOURCES`** in `platform/py32f071/CMakeLists.txt`, **not** allow-listed as `PY32_EXCLUDED`. This is not optional in either direction: `check_cmake_manifest.py`'s reverse check makes a new `src/*.cpp` that is neither named nor reasoned-excluded an **exit-1 violation**, so the phase must choose. Naming it is what the phase goal literally says ("the py32 port compiles against a final VPP capability shape"), it makes the py32 CMake the natural home for D-07's declaration, and D-02's dependency-freedom makes ARM compilation near risk-free. A `PY32_EXCLUDED` line was rejected: it would leave the py32 board with no declared VPP capability at all (so it would hit D-06's `#error` the moment anything includes the header) and hand Phase 126 a second exclusion to unwind.
- **D-13:** Phase 125 obtains **its own ARM CI evidence** — push the firmware milestone branch `v1.23-py32f071-integration` to `origin`, `workflow_dispatch` `py32f071.yml`, record **run URL + head SHA**. Rationale is the same attributability the 125 → 126 ordering exists for: if the seam breaks the ARM build, *this* is the phase that learns it. Deferring ARM evidence to Phase 126's run was offered and declined. **Push safety, re-verified:** `py32f071.yml` fires on `pull_request` + `workflow_dispatch` + `push: branches: [beta]` (MERGE-03's addition) and `beta-build.yml` is untouched — so pushing the milestone branch cuts no beta prerelease. Confirmed by reading the workflow on the current tree, not assumed from Phase 124.
- **D-14:** That push and dispatch is an **outward-facing action requiring an explicit operator gate at execute time**, structurally separated from any autonomous flag. `--auto`/`--chain` auto-approve human-verify checkpoints regardless of `autonomous: false`. Follow Phase 124 Plan 124-11's shape exactly: **no task runs `git push` or `gh workflow run`** — the plan prints the commands and stops.
- **D-15:** Criterion 4 is discharged by **recording** the measured flash **and** RAM figures for all three AVR targets in the phase's evidence artifact. **No new gate, no tolerance band, no new `--policy` flag** — operator decision, taken against the recommendation. The planner must **not** "complete" this by adding a comparator leg of its own.
- **D-16:** `scripts/check_size_baseline.py`'s default `compare_avr()` is **strict equality and already armed** in the existing sweep, so a nonzero delta goes red whether or not this phase gates on it. If it fires: **measure, record the delta and its cause in the evidence artifact, then re-baseline `size_baseline.json` in its own commit whose message states why the bytes are legitimate** — the shape Plan 124-10 used. Never widen a tolerance, never re-baseline silently. Note `size_baseline_base01.json` (Phase 124's frozen MERGE-05 reference) is a **separate** file and is not touched by any re-baseline here.

### Claude's Discretion

- **PR #45 non-ancestry proof (Criterion 1).** House-style default: a **scripted check producing an exit code**, not a prose assertion — assert each of PR #45's commit SHAs (`05f4a77`, `9134f2a`, `b964ee6`, `d285b83`, `71278d0`, `a47228d`, and the earlier `768580f`, `86f351a`, `fc0b2c7`, `04fd9b3`) is **not** an ancestor of the integration branch, with a never-vacuous guard so an empty SHA list cannot pass. Whether to *also* assert content divergence from PR #45's blobs is Claude's call; D-09/D-10 already guarantee substantial divergence.
- **Evidence artifact shape.** Default: a **`125-NONREGRESSION.md`** in the same command / expected / observed row shape as `123-NONREGRESSION.md` and `124-NONREGRESSION.md`, re-executed in the closing plan rather than copied from earlier plans' SUMMARY files. This is where D-15's figures and D-13's run URL + SHA land.
- **How the three untouched files are pinned (Criterion 3).** Default: **literal blob SHAs recorded pre-phase and re-hashed after**, plus `git status --porcelain` empty. Explicitly **never** a path-scoped `git diff`, which passes vacuously on a wrong path. Note `124-VERIFICATION.md` carries a live informational finding on exactly this class of mistake.
- Plan/wave decomposition and commit granularity, subject to D-14's forced ordering (the push/dispatch task is last and gated).
- Exact harness filename, `main`-shim mechanics, and how the return value crosses the process boundary (exit code vs. stdout).
- Where the one `#include "rurp_vpp.h"` line sits in `include/rurp_shield.h`. **Verify, do not assume:** `firestarter_app/tests/test_revision_constants_parity.py` references `rurp_shield.h`, and its `_extract_defines` / `_find_header_guard_line_indices` logic tracks preprocessor nesting. Phase 124's correction C-18 documents a near-miss of exactly this kind. A plain `#include` should be inert, but check it.

### Deferred Ideas (OUT OF SCOPE)

- **Closed-loop VPP control / DAC feedback** — PR #45's `rurp_vpp_dac_write`, `rurp_vpp_control_enable`, `rurp_vpp_delay_ms`, `RURP_VPP_DAC_BITS`, and the whole `#if RURP_HAS_VPP_DAC` control loop. Returns **with an implementation and a board attached**, not as declarations. Blocked on hardware that does not exist; D-05 says no Arduino-class board will ever qualify.
- **VPP two-point calibration** (`vpp_gain_ppm`, `vpp_offset_mv`, four `vpp_cal_*` fields, `rurp_calibrate_vpp_two_point`, `rurp_reset_vpp_calibration`, `rurp_vpp_calibration_valid`, `rurp_apply_vpp_calibration`) — requires new `rurp_configuration_t` fields, i.e. the `CONFIG_VERSION` bump VPP-03 forbids. The ROADMAP's queued **v1.26** slot is where the VREFINT + two-point calibration model is designed once for AVR and extended cross-platform; PR #45 `05f4a77` is the prior art to read there.
- **AVR voltage-measurement rework** — PR #45 `9134f2a`'s reroute plus 16× oversampling. Touches an AVR read path with bench history; needs its own phase and its own evidence.
- **Exposing VPP control mode on the wire** — wire-visible → `messages.toml` + codegen + host constants parity, in the phase whose premise is that nothing else moved. Revisit when a host consumer actually exists.
- **Compile-time manual-control assertions in the real target builds** — the rejected third option of D-01.
- **A planted mutated-seam fixture for the harness** — declined under D-03 in favour of the forced-DAC compile leg.
- Reviewed-not-folded todos: `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md`, `correct-v128-py32-roadmap-prior-art.md`, `avrdude-mcu-detection-fallback.md`, `cobs-decoder-framelevel-deadline-wr01.md`, `fold-response-code-into-log-macro.md`, `photograph-modified-rev-0.md`, `prove-pio-dev-flag-fails-closed.md`.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description (verbatim, `REQUIREMENTS.md` lines 54–56) | Research Support |
|----|-------------|------------------|
| **VPP-01** | `include/rurp_vpp.h` and `src/rurp_vpp.cpp` are **hand-authored** — nothing is cherry-picked from PR #45, whose `05f4a77` smuggles a `CONFIG_VERSION` bump and whose `9134f2a` reroutes AVR voltage measurement | §"PR #45 — the ancestry question, answered mechanically" gives the complete verified 10-SHA set, the exact non-vacuous command shape (C-2), and the two blob SHAs to assert divergence from. `05f4a77`'s `VER06`→`VER07` bump is verified line-for-line; C-18 adds a *worse* case the record missed |
| **VPP-02** | `rurp_set_vpp_target_mv()` returns `MANUAL_ADJUSTMENT_REQUIRED` on every board, asserted by a native test across each board macro-set | §"The six-leg harness, prototyped and run" contains a working six-leg prototype with observed output for every leg, plus the process-boundary recommendation. C-6 bounds what the four board legs actually prove |
| **VPP-03** | A diff gate proves `src/boards/rurp_common.cpp`, `include/rurp_types.h` and `src/rurp_config_utils.cpp` untouched and `CONFIG_VERSION` still `"VER06"`, with the AVR flash delta measured rather than asserted | §"Criterion 3 — the pin, with its pre-phase blob SHAs" records the three blob SHAs and the `CONFIG_VERSION` line. §"Criterion 4 — the flash delta, measured" records 0 B / 0 B on all three targets, non-vacuously (the TU provably compiled; the symbols provably absent) |
</phase_requirements>

---

## Summary

This phase is small in code and large in interaction surface. The code is two new files (a ~39-line header, an ~18-line `.cpp`), one line in the ARM source manifest and one line in the ARM compile definitions. The interaction surface is nine firmware/host gates, three pinned baselines, two pinned native-suite counts and a claim gate.

Everything the CONTEXT locked is achievable, and almost all of it is now *measured* rather than expected. Three AVR targets rebuild at **exactly** their recorded flash and RAM figures with the full seam in the tree; the three seam symbols are provably absent from the linked ELF; the ARM manifest gate's reverse check provably fires on an unnamed new `src/*.cpp` and provably passes when named; all ten PR #45 commits are provably not ancestors of the integration branch; the host-repo parity gate provably never reads `rurp_shield.h`; and a six-leg compile-and-run harness prototype produces the exact outcomes D-01/D-03/D-08 specify.

**One locked decision is falsified by measurement, and it is blocking.** D-06's `#error` arm, combined with the "one `#include "rurp_vpp.h"` line in `include/rurp_shield.h"` that the CONTEXT `<domain>`, the ROADMAP's `Depends on` line and `research/SUMMARY.md` all describe, breaks every native environment: `pio test -e native` goes from `141 test cases: 141 succeeded` (17 suites) to **`17 test cases: 0 succeeded`, all 17 ERRORED**. That is the identical signature (A-4) this milestone already paid for once with `agent/portability-macros`. The cause is structural, not incidental: `rurp_shield.h` is included by every native suite's `host_stubs.cpp` and by `src/proms/*.cpp`, host `g++` does not define `__AVR__`, and no native env declares `RURP_HAS_VPP_DAC` — so D-06's `#else #error` fires 17 times. Two resolutions were built and measured; both work; one requires no build-file edit at all.

**Primary recommendation:** implement D-06, D-07, D-09, D-10, D-11 and D-12 exactly as locked, and **do not add the `#include "rurp_vpp.h"` line to `include/rurp_shield.h`**. The seam's only includers become `src/rurp_vpp.cpp` and D-01's harness TU — which is precisely D-11's stated consumer set — leaving native at 141/17 and all three AVR targets at 0 B delta with no `platformio.ini` edit and no widened predicate. Measured, both ways, below.

---

## Corrections to 125-CONTEXT.md and the upstream record

Numbered, in descending consequence. Each states the command run and the output observed.

### C-1 — BLOCKING. D-06's `#error` plus the `rurp_shield.h` `#include` breaks all three native environments

**Claim being corrected.** `125-CONTEXT.md` `<domain>`: *"The entire production-visible change is: two new files, one `#include` line in `include/rurp_shield.h`…"*; `<code_context>` §Established Patterns: *"141 cases / 17 suites on both pinned native envs. This phase must not move either number — and by D-01's design, it does not touch them."*; ROADMAP:2145 *"the merged `rurp_shield.h` this seam's one new `#include` line attaches to"*; `research/SUMMARY.md` §Phase 125 Delivers: *"one `#include` line in `rurp_shield.h`"*.

**What was done.** A throwaway `tar` copy of the firmware tree was made (the real repo was never written to — `git -C firestarter status --porcelain` is empty before and after this entire research session). `include/rurp_vpp.h` was authored with D-06's quoted block verbatim, `src/rurp_vpp.cpp` with D-09/D-10's surface, and `#include "rurp_vpp.h"` inserted into `include/rurp_shield.h` immediately after `#include "rurp_pinout.h"`. Then `pio test -e native`.

**Observed:**

```
pio test -e native exit=1
include/rurp_vpp.h:10:6: error: #error "RURP_HAS_VPP_DAC must be defined by the board/platform build"
  … (the same error, once per suite) …
================== 17 test cases: 0 succeeded in 00:01:31.985 ==================
```

All 17 suites `ERRORED`. Cases collapse 141 → 0.

**Why, structurally.** `grep -rn 'include "rurp_shield.h"' src include test platform` returns 46 hits. Fourteen are under `test/native/avr/*/host_stubs.cpp` and four more are production TUs the native envs compile (`src/proms/memory.cpp`, `flash_intel.cpp`, `sram.cpp`, `flash_utils.cpp`, plus `src/operation_utils.cpp` via `build_src_filter`). Host `g++` 14.2.0 does not define `__AVR__` (`g++ -dM -E - </dev/null | grep -c -i AVR` → **0**). No native env declares `RURP_HAS_VPP_DAC` (`grep -c RURP_HAS_VPP_DAC platformio.ini` → **0**). So D-06's `#else` arm is reached in every native TU. This is not a subtle nesting interaction like Phase 124's C-18 — it is the guard doing exactly what D-06 designed it to do, in a compilation unit nobody accounted for.

**Two resolutions, both measured.**

| Option | Change | `pio test -e native` | AVR uno flash/RAM | Build-file edits |
|---|---|---|---|---|
| **A (recommended)** | Both new files land; **no** `#include` in `rurp_shield.h` | **141 test cases: 141 succeeded**, 17 suites, exit 0 | **23954 / 1573** (0 delta) | **none** |
| B (fallback) | Keep the `#include`; add `-D RURP_HAS_VPP_DAC=0` to `[env:native]` and `[env:native_nodevtools]` `build_flags` | **141 test cases: 141 succeeded**, exit 0 | 23954 / 1573 (0 delta) | 2 lines in `platformio.ini` |

Option A is recommended on four grounds, all checked:

1. It is *already* what D-11 says the macro's consumers are — "the `#if` in `src/rurp_vpp.cpp` and the `#if !defined` in `include/rurp_vpp.h`". Nothing needs the declaration: there are zero production callers.
2. `src/rurp_vpp.cpp` is still compiled by all three AVR envs (no AVR env has a `build_src_filter`; `.pio/build/{uno,uno328pb,leonardo}/src/rurp_vpp.cpp.o` all exist after the build) and by the ARM target (D-12 names it), so D-07's CMake declaration stays genuinely load-bearing — a non-AVR target that forgets it still fails at the preprocessor.
3. It honours D-06's own stated reason for choosing `__AVR__`: *"`platformio.ini` needs no edit, which keeps the AVR flash delta attributable to source alone."* Option B contradicts that sentence in the same decision.
4. `include/rurp_shield.h` is **not** in Criterion 3's pinned set — editing it is *permitted*, never *required*. No ROADMAP success criterion mentions the `#include`; it appears only in prose.

Option B's residual cost, for completeness: three native envs would then carry a board-capability declaration for a target that is not a board, and `[env:native_pinmap_provisional]` inherits `${env:native.build_flags}` so only two literal edits are needed. It works — but it puts a build-flag edit inside the phase whose premise is that nothing else moved.

**If the operator wants the `#include` for discoverability anyway,** option B must ship *with* a re-run of `pio test -e native` and `-e native_nodevtools` recorded at 141/17 in `125-NONREGRESSION.md`. Do not ship the `#include` without one of the two resolutions.

### C-2 — ROADMAP Criterion 1's named mechanism is wrong in two independent ways

Criterion 1 (ROADMAP:2149) prescribes *"checked by `git log --all --grep`/SHA lookup"*. Both halves fail:

- **`--grep` searches commit messages, not SHAs.** `git log --all --grep=05f4a77 --oneline` returns **zero rows** today. It would still return zero rows after a cherry-pick whose message was rewritten — the exact evasion Criterion 1 exists to catch. A gate built on it passes vacuously forever.
- **Any `--all`-scoped reachability test gets the wrong answer.** `origin/feature/common-vpp-calibration` is a fetched local remote-tracking ref, so `git rev-list --all | grep -c '^05f4a775cbae440c5f167f6495531ea101a30635$'` → **1**. Scoped to the branch under test, `git rev-list HEAD | grep -c …` → **0**. `--all` must never appear in this check.

**The correct shape**, verified command by command:

```bash
# non-vacuity part 1: the object must exist locally, or this is a TOOL error (exit 2),
#                     never a silent "not an ancestor" pass
git cat-file -e "$sha^{commit}"            # exit 0 for all ten; exit 128 for a bogus sha
# the ancestry test, scoped to HEAD only
git merge-base --is-ancestor "$sha" HEAD   # exit 0 => ANCESTOR => violation (exit 1)
                                           # exit 1 => clean
                                           # exit 128 => bogus ref => exit 2
# non-vacuity part 2
[ "$n_checked" -eq 10 ] || exit 2          # an empty or short SHA list must not pass
```

Measured: `git merge-base --is-ancestor deadbeef…deadbeef HEAD` → `fatal: Not a valid commit name` / **exit 128**. A naive `if ! git merge-base --is-ancestor …; then pass; fi` therefore treats a typo'd or unfetched SHA as clean. Handle 128 explicitly.

**Fresh-clone caveat:** `git cat-file -e 05f4a77^{commit}` succeeds here only because the PR #45 ref is fetched. In a clone without it, the objects are absent and the gate must exit 2 (tool error), not 0. Recommend a `git fetch origin feature/common-vpp-calibration` precondition, or an explicit exit-2 message naming the missing ref.

### C-3 — The ten-SHA list is complete and correct; none is an ancestor

Verified, not assumed. `git rev-list --count origin/beta..origin/feature/common-vpp-calibration` → **10**. The enumerated set matches CONTEXT's list exactly, in chronological order:

`04fd9b3` → `fc0b2c7` → `86f351a` → `768580f` → `05f4a77` → `b964ee6` → `9134f2a` → `d285b83` → `71278d0` → `a47228d`

Merge base with `origin/beta`: `a1953c22862ac3fb1e0111985946644a568aee36`. Branch tip: `a47228d862b9b53e6d936d1d0993bee9fc74940e`.

`git merge-base --is-ancestor <sha> HEAD` for all ten, against `HEAD = a145081b59d94530583b9ce365db03ff567d0c2c`: **all ten `not-ancestor`**. No blocking finding. PR #47's tip (`cc4a815`) is also not an ancestor.

PR #45 touches exactly six files (`git diff --stat a1953c2 origin/feature/common-vpp-calibration`), confirming CONTEXT's inventory including the −132 rewrite of `rurp_shield.h`:

```
 include/rurp_shield.h      | 132 +++++++++++++---------------------
 include/rurp_types.h       |  12 ++++
 include/rurp_vpp.h         |  70 ++++++++++++++++++
 src/boards/rurp_common.cpp |  62 ++++++++--------
 src/rurp_config_utils.cpp  |  14 ++--
 src/rurp_vpp.cpp           | 176 +++++++++++++++++++++++++++++++++++++++++++++
```

Blob SHAs available for an optional content-divergence assertion: `include/rurp_vpp.h` = `c982173813b38ec745b59d6e02817f2504d6c6b4`, `src/rurp_vpp.cpp` = `fcbe009dffcd46139802f8779865a1d7aa331880`. Asserting the new files' blob SHAs differ from these is cheap and non-vacuous; recommended as a second leg on the same pytest.

### C-4 — D-06's quoted block does not satisfy D-03; a second `#error` is required and is unwritten

D-03 requires that `-DRURP_HAS_VPP_DAC=1` produce a non-zero `g++` exit with a named `#error`. D-06's quoted block does **not** do that — it only fires when the macro is *undefined*. Measured, on the block exactly as CONTEXT quotes it:

| leg | exit |
|---|---|
| bare host `g++` | **1** (the `#error` fires) |
| `-D__AVR__` | 0 |
| `-DRURP_HAS_VPP_DAC=0` | 0 |
| `-DRURP_HAS_VPP_DAC=1` | **0** ← D-03 requires non-zero |

So a *second*, separately-authored guard is needed. D-09's parenthetical (*"unreachable now that `RURP_HAS_VPP_DAC=1` is itself an `#error` per D-03"*) and D-11's *"the `#if` in `src/rurp_vpp.cpp`"* together locate it in the `.cpp`:

```c
#if RURP_HAS_VPP_DAC
#error "RURP_HAS_VPP_DAC=1 selects a closed-loop VPP DAC implementation that this branch does not provide"
#endif
```

Two consequences the planner must carry: (a) D-03's forced-DAC leg must compile `src/rurp_vpp.cpp`, not merely include the header; (b) the `#error` text must be scoped to *this branch*, not to the world — see C-17.

Verified in place: `g++ -D__AVR__ -DRURP_HAS_VPP_DAC=1 … main.cpp src/rurp_vpp.cpp` → **exit 1**, stderr carrying the named message.

### C-5 — `--gc-sections` is now measured, and `-flto` is the flag nobody named

D-11 expects zero flash cost; `research/SUMMARY.md` says *"0 B expected with `--gc-sections`/no callers — measured, not asserted"*. Now measured, on all three AVR targets, with the complete seam in the tree.

**The real flags**, read out of `platform-atmelavr@5.2.0` `builder/frameworks/arduino.py:95–115` (all three envs are `platform = atmelavr` + `framework = arduino`, so all three get them):

```
CCFLAGS   … -Os -Wall -ffunction-sections -fdata-sections -flto
LINKFLAGS … -Os -Wl,--gc-sections -flto -fuse-linker-plugin
```

`-flto` is present and is not mentioned anywhere in CONTEXT, ROADMAP or SUMMARY. It matters: the compiled `src/rurp_vpp.cpp.o` is an **LTO slim object** (`avr-nm` reports `plugin needed to handle lto object` plus `__gnu_lto_slim`), so the seam's bodies never reach a real `.text` section at all. `--gc-sections` and LTO both contribute; the outcome is the same but the mechanism is worth recording so a future reader does not attribute it solely to section GC.

**Measured, clean `rm -rf .pio` then `pio run -e <env>` per env, before and after planting the seam:**

| env | flash before | flash after | Δ | RAM before | RAM after | Δ |
|---|---:|---:|---:|---:|---:|---:|
| uno | 23954 | **23954** | **0** | 1573 | **1573** | **0** |
| uno328pb | 24004 | **24004** | **0** | 1579 | **1579** | **0** |
| leonardo | 26016 | **26016** | **0** | 2014 | **2014** | **0** |

**Non-vacuity of that zero, both directions:**

- The TU really compiled: `.pio/build/{uno,uno328pb,leonardo}/src/rurp_vpp.cpp.o` all exist (4520 / 4520 / 4508 bytes).
- The symbols really vanished: `avr-nm .pio/build/uno/firestarter_uno.elf | grep -cE 'rurp_vpp_control_mode|rurp_set_vpp_target_mv|rurp_disable_vpp_control'` → **0**. (Five unrelated pre-existing `vpp` symbols remain — `eprom_check_vpp`, `get_vpp_mv`, `key_vpp_mv`, two `using_p1_as_vpp` LTO clones — so the grep is not matching nothing by accident.)

**`platformio.ini` needs no edit** to compile the new TU: none of `[env:uno]`, `[env:uno328pb]`, `[env:leonardo]` declares `build_src_filter`, so all of `src/` compiles. Only the three native envs restrict it, and their filter (`+<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>`) does not match `src/rurp_vpp.cpp`. Both halves confirmed by reading `platformio.ini` and by the `.o` files above.

**Consequence for D-16:** the strict comparator does not fire. Verified end to end — `check_size_baseline.py --avr-log uno=<seam log> --avr-log uno328pb=… --avr-log leonardo=…` → **exit 0**, `PASS: uno(flash=23954/32256,ram=1573/2048), uno328pb(flash=24004/32384,ram=1579/2048), leonardo(flash=26016/28672,ram=2014/2560)`. Keep D-16's re-baseline procedure as a documented contingency; do not pre-emptively re-baseline.

### C-6 — The three AVR harness legs are one fact, not three; and D-04's drift anchor is not where D-04 says

`rurp_vpp.h` consults exactly two macros: `__AVR__` and `RURP_HAS_VPP_DAC`. Nothing in the seam distinguishes Uno from Leonardo from uno328pb. The four board legs therefore prove **uniformity across one AVR fact plus one explicit ARM declaration**, not four independent per-board facts. Criterion 2's wording ("across every board macro-set … in one run") is satisfied as written, but the evidence artifact must not imply four independent proofs. This is exactly D-06's design intent (*"All three AVR targets are covered by one stated fact, uniformly"*) — state it, do not let the reader infer more.

**D-04's drift leg needs a different anchor than D-04 names.** D-04 says the leg asserts "each board's defining macro still appears in its real build config (`platformio.ini` for the three AVR envs)". Read against `platformio.ini`:

| board | what is literally in `platformio.ini` | `ARDUINO_AVR_*` present? |
|---|---|---|
| uno | `[env:uno]`, `board = uno`, `-D RURP_BOARD_NAME=\"${this.board}\"`, `-D SERIAL_ON_IO` | **no** |
| uno328pb | `[env:uno328pb]`, `board = ATmega328PB`, `-D RURP_BOARD_NAME=\"uno328pb\"` (literal), `-D SERIAL_ON_IO` | **no** |
| leonardo | `[env:leonardo]`, `board = leonardo`, `-D RURP_BOARD_NAME=\"${this.board}\"`, `-D DATA_BUFFER_SIZE=1024` | **no** |
| py32f071 | `RURP_PLATFORM_PY32F071=1`, `RURP_BOARD_NAME="py32f071"` in `target_compile_definitions` | n/a |

`ARDUINO_AVR_UNO` / `ARDUINO_AVR_LEONARDO` / `ARDUINO_AVR_ATmega328PB` are supplied by the framework and the board JSON (`ARDUINO_AVR_UNO` is visible in the compile command line, never in `platformio.ini`). A drift leg grepping `platformio.ini` for them **fails on arrival**. Note also that `RURP_BOARD_NAME` is a *literal* only for uno328pb — uno and leonardo use `${this.board}`.

Honest anchors, all literal and all present: the `[env:<name>]` section header plus `board = <uno|ATmega328PB|leonardo>` for AVR; `RURP_PLATFORM_PY32F071=1` and `RURP_BOARD_NAME="py32f071"` for ARM. Recommend those.

### C-7 — D-13's push safety confirmed; and the new harness runs in **zero** CI legs on this branch

**Push safety, re-read on the current tree** (not carried from Phase 124):

`.github/workflows/py32f071.yml`:
```yaml
on:
  push:
    branches: [beta]
  pull_request:
    paths:
      - "platform/py32f071/**"
      - "include/**"
      - "src/**"
      - "lib/jsmn/**"
      - ".github/workflows/py32f071.yml"
  workflow_dispatch:
```

`.github/workflows/beta-build.yml`:
```yaml
on:
  push:
    branches:
    - beta
    paths-ignore: [ '**.md', '**.sh', '.gitignore', 'docs/**', 'documents/**', 'images/**', '.vscode/**', '.editorconfig/**' ]
  workflow_dispatch:
    inputs:
      beta_version: …
```

Pushing `v1.23-py32f071-integration` matches neither `push` trigger and opens no pull request. **It cuts no beta prerelease.** D-13 stands.

**The finding CONTEXT does not carry.** `grep -rn pytest .github/workflows/` returns exactly two workflows with a `pytest tests/ -v` step: `build.yml` (triggers on push/PR to **`main`** only) and `beta-build.yml` (push to **`beta`** only). `py32f071.yml` has **no pytest step at all**. Therefore D-01's new harness — like `test_pinmap_guard_fires.py` before it — executes in **no CI leg** on `v1.23-py32f071-integration`. Criterion 2 is discharged by an in-phase local `pytest` run whose verbatim output must land in `125-NONREGRESSION.md`; there is no CI oracle to fall back on. `test_pinmap_guard_fires.py`'s own docstring asserts "both firmware CI workflows run `pytest tests/ -v`" — true of the two workflows, but neither fires on this branch. State it; do not claim CI coverage the branch does not have.

### C-8 — `compare_avr()` is strict equality, armed, and proven strict; the frozen file is genuinely separate

Read (`scripts/check_size_baseline.py:183–211`): `compare_avr()` compares `flash_used`, `flash_total`, `ram_used`, `ram_total` for exact equality against `baseline["avr_targets"][env]`. No band, no tolerance.

**Proven strict**, not merely read: a log perturbed by +2 B (`used 23954` → `used 23956`) yields

```
FAIL:
  uno: flash_used baseline=23954 observed=23956
exit=1
```

**Never-vacuous**: a bare `python3 scripts/check_size_baseline.py` with no logs and no `--rebuild` → `FAIL: no envs compared … (never-vacuous guard: …)`, **exit 1**. Same for `check_build_warnings.py`.

**Seam** (`:95–96`): `FIRESTARTER_SIZE_BASELINE = os.environ.get("FIRESTARTER_SIZE_BASELINE", str(REPO_ROOT / "scripts" / "baseline" / "size_baseline.json"))` — read once at import, so an in-process `monkeypatch.setenv` is ineffective; a subprocess with the child env is required.

**The live baseline's current numbers** (`scripts/baseline/size_baseline.json`, `meta.phase: "124"`, `firmware_tree_sha 2bd7187`):

| env | flash_used | flash_total | ram_used | ram_total |
|---|---:|---:|---:|---:|
| uno | 23954 | 32256 | 1573 | 2048 |
| uno328pb | 24004 | 32384 | 1579 | 2048 |
| leonardo | 26016 | 28672 | 2014 | 2560 |

Native: `native` 141/17 all-passed, `native_nodevtools` 141/17 all-passed, `native_pinmap_provisional` 10/1 all-passed. Warning watermarks (cold): native 1166, native_nodevtools 1166, native_pinmap_provisional 138; AVR all `== 0`.

`ls scripts/baseline/` → `size_baseline.json`, `size_baseline_base01.json`. Two distinct files; `size_baseline_base01.json` is reached only via an explicit `--baseline scripts/baseline/size_baseline_base01.json`. A re-baseline of the live file cannot touch it. D-16 confirmed.

### C-9 — The host parity gate never reads `rurp_shield.h`; a bare `#include` is inert at any position

The discretion item asked for function and line numbers. Answer:

- `firestarter_app/tests/test_revision_constants_parity.py:145` — `FIRMWARE_HEADER = fw_path("include", "firestarter.h")`. That is the **only** firmware header this module parses.
- `_extract_defines(text)` at **:288** operates on the *string it is handed* (`_strip_comments(text)` at :304, `splitlines()` at :305). It follows no `#include`. Its three line classifiers are `_PP_OPEN_PATTERN` (`#if|#ifdef|#ifndef`, :197), `_PP_CLOSE_PATTERN` (`#endif`, :198) and `_DEFINE_PATTERN` (`#define (CMD|FLAG)_…`, :193–196). An `#include` line matches **none** of the three, so it changes neither the yielded define set nor the nesting depth.
- `_find_header_guard_line_indices(lines)` at **:242** matches the first `#`-leading line against `#ifndef <GUARD>` and the next non-blank `#`-leading line against `#define <same GUARD>`, and the last `#`-leading line against `#endif`. An `#include` inserted anywhere in the middle of the file cannot alter any of those three positions.
- `rurp_shield.h` appears in this module only at **:11** and **:150** — both docstrings.

**Verdict: a bare `#include "rurp_vpp.h"` in `include/rurp_shield.h` is inert to this gate, at any position.** Corroborated by the whole host suite: **1158 passed**, 0 failed, **0 skipped** (`python3 -m pytest` in `/workspaces/firestarter_app`).

**Bonus pre-existing gap, recorded not fixed.** `test_revision_byte_values_match_firmware_enum` (:148–160) asserts imported Python constants against hardcoded expected bytes (`assert REVISION_0 == 0x00` …) and **reads no header at all**. The REVISION_* half of CLAUDE.md's cross-repo sync rule is therefore unenforced — a `rurp_shield.h` enum drift would not be caught. Same defect class as the `CMD_*`/`FLAG_*` legs Phase 120 rebuilt. Out of Phase 125's scope; worth a backlog seed.

### C-10 — No host scan-path inventory entry is needed; checked, not omitted

`firestarter_app/tests/scan_paths.py`'s `ALL_CROSS_REPO_PATHS` is the deduplicated union of `CROSS_REPO_TEST_PATHS` (6 entries) and the genuinely-cross-repo `CROSS_REPO_TOOL_RESOLVERS` paths (which all coincide with the 6). The six are:

```
include/firestarter.h
src/proms/eeprom_28c.cpp
doc/PROTOCOLS.md
test/native/avr/test_dispatch/test_configure_memory.cpp
test/native/avr/_shared/sdp_bus_config.h
test/native/avr/_shared/validation_matrix.h
```

None is `include/rurp_shield.h`, `include/rurp_vpp.h`, `src/rurp_vpp.cpp` or `platform/py32f071/CMakeLists.txt`. **No inventory entry is expected, as a checked fact.** Note the module carries a hard `assert len(CROSS_REPO_TOOL_RESOLVERS) == 11` and `assert SAME_REPO_LOOKALIKES` — adding an entry gratuitously would require touching those.

`tools/check_is_memory_cmd_no_ifdef.py:82–86` — `_DEFAULT_CMD_ADMISSION_SRC = os.path.join(_HERE, "..", "..", "firestarter", "include", "firestarter.h")`, overridable via `FIRESTARTER_CMD_ADMISSION_SRC`. It scans `firestarter.h`'s `is_memory_cmd()` body only. Unaffected.

`tests/fw_presence.py` — `FW_ROOT` (:80) from `FIRESTARTER_FW_ROOT` or `_APP_REPO_ROOT.parent / "firestarter"`; `FW_REPO_MARKER = FW_ROOT / ".git"` (:86); `requires_fw` (:102) skips only when the marker is absent; `fw_path()` (:117) raises `MissingScanTargetError` for a present repo with a missing target. A *new* firmware file interacts with none of it.

### C-11 — BASE-08 obligation the CONTEXT missed: only the *pytest* shape is free

CONTEXT correctly notes D-01's pytest needs no floor bump. But the Criterion-1 discretion default is *"a scripted check producing an exit code"* — and if that lands as `scripts/check_*.py`, `tests/test_checker_convention.py` bites. Read: `CHECKER_GLOB = "check_*.py"` (:119) globbed non-recursively over `firestarter/scripts/`; `FLOOR = 5` (:123); `FIXTURE_FLOOR = 10` (:124); paired module required at `tests/test_check_<X>.py`; at least one `tests/fixtures/planted_<X>*` entry required.

**Proven, not inferred.** In a scratch copy placed in a directory literally named `firestarter` (the suite's `test_scope_is_firmware_only` asserts the resolved scripts dir ends in `("firestarter","scripts")`):

```
--- WITH planted scripts/check_pr45_ancestry.py ---
FAILED tests/test_checker_convention.py::test_every_checker_has_paired_test_module
FAILED tests/test_checker_convention.py::test_every_checker_has_planted_fixture
2 failed, 5 passed
--- WITHOUT it (control) ---
7 passed
```

So a `scripts/check_pr45_ancestry.py` costs four artifacts in the same commit: the checker, `tests/test_check_pr45_ancestry.py`, a `tests/fixtures/planted_pr45_ancestry*` entry, and `FLOOR 5→6` + `FIXTURE_FLOOR 10→11`.

**Recommendation:** implement Criterion 1 as **`tests/test_pr45_non_ancestry.py`** — a pytest that shells out to `git cat-file -e` / `git merge-base --is-ancestor` per C-2, exactly the shape `test_pinmap_guard_fires.py` uses for a compiler. It still "produces an exit code" (pytest's), still cannot be silently forgotten (it runs with the suite), and incurs zero BASE-08 debt. If the operator prefers a `scripts/` checker, pay the four artifacts deliberately — never lower a floor.

### C-12 — `check_cmake_manifest.py`'s reverse check does behave as documented; here is what it actually keys on

Read from the implementation, then proven.

- `enumerate_tree_sources()` (:240–251) — `rglob("*")` over `<root>/src`, filtered by `_SOURCE_EXTS = (".cpp", ".c")` (:173), returned as repo-relative POSIX strings. **Recursive** into subdirectories; sorted, so ordering is irrelevant.
- The reverse loop (:311–322) — every enumerated relpath not in `enforced_common_relpaths` and not a key of `excluded_valid` becomes a violation.
- `enforced_common_relpaths` is built from `FIRESTARTER_COMMON_SOURCES` entries via `resolved.relative_to(_ROOT)` (:293–299), so the manifest must name the file as `"${REPOSITORY_ROOT}/src/rurp_vpp.cpp"` for the strings to match.

**Proven both directions.** Planted `src/rurp_vpp.cpp` **unnamed**:

```
FAIL: … src/rurp_vpp.cpp: present in tree, not named in FIRESTARTER_COMMON_SOURCES,
      and not covered by a reasoned PY32_EXCLUDED entry
exit=1
```

Named in `FIRESTARTER_COMMON_SOURCES`:

```
PASS: …/platform/py32f071/CMakeLists.txt -- 24 enforced source(s) resolved …;
      14 PY32_SDK_SOURCES entries structurally exempt …; allow-listed omission(s):
      src/boards/leonardo_rurp_shield.cpp, src/boards/rurp_common.cpp,
      src/boards/uno_rurp_shield.cpp, src/dev_tools.cpp, src/rurp_config_utils.cpp
exit=0
```

Current real-repo state: `PASS`, **23** enforced sources, exit 0. Naming the seam takes it to 24. D-12 confirmed non-optional and confirmed satisfiable.

**One gap worth knowing:** the manifest-side `PATH_RE` accepts `.s`/`.S`, but `_SOURCE_EXTS` does not enumerate them — a new `src/*.s` would escape the reverse check entirely. Not this phase's problem (the seam is `.cpp`), but do not assume the reverse check covers assembly.

### C-13 — `__AVR__` is the right predicate, and the tree's own family macro is a trap

**`__AVR__` is unconditional** for all three targets — `avr-gcc -mmcu=<m> -dM -E - </dev/null` (avr-gcc 7.3.0, `toolchain-atmelavr`):

| mcu | `__AVR__` | also |
|---|---|---|
| atmega328p | `#define __AVR__ 1` | `__AVR_ATmega328P__ 1`, `__AVR_ARCH__ 5` |
| atmega328pb | `#define __AVR__ 1` | `__AVR_ATmega328PB__ 1`, `__AVR_ARCH__ 5` |
| atmega32u4 | `#define __AVR__ 1` | `__AVR_ATmega32U4__ 1`, `__AVR_ARCH__ 5` |

**`-D__AVR__` on host `g++` has no side effect** on a TU including only `rurp_vpp.h` plus `<cstdio>`: compiled under `-std=gnu++17 -Wall -Wextra`, stderr was **0 bytes**, and the linked binary ran to exit 0.

**And the better-looking predicate is unusable.** `include/rurp_platform.h:32` defines `RURP_PLATFORM_AVR 1` inside an `#elif defined(__AVR__)` arm — so it is *derived from* `__AVR__`, not independent of it. Worse, `rurp_platform.h` is reachable from no AVR build: its only includers are `platform/py32f071/src/usb_cdc.c`, `platform/py32f071/include/Arduino.h` and `include/boards/py32f071_rurp_shield.h`. `RURP_PLATFORM_AVR` is therefore **never actually defined during an AVR build**. And `rurp_platform.h` carries its own terminal `#else #error "Unsupported Firestarter target platform"`, whose `RURP_PLATFORM_NATIVE` escape arm (:40) references a macro that is **defined nowhere in either repo** (`grep -rn RURP_PLATFORM_NATIVE` → one hit, that `#elif` itself) — so including `rurp_platform.h` from the seam would break native even harder than C-1 does.

D-06's choice is correct and should be recorded *with this reasoning attached*, so a later phase does not "improve" it into `RURP_PLATFORM_AVR`.

### C-14 — The ARM defines block, quoted; and `check_build_warnings.py` does not know ARM exists

`platform/py32f071/CMakeLists.txt`, current tree (the `target_compile_definitions` block, preceded by Phase 124 D-02's comment):

```cmake
# DEV_TOOLS is deliberately NOT defined for the ARM target (MERGE-08, D-02):
# the shared value-semantics default (#ifndef DEV_TOOLS / #define DEV_TOOLS 0
# / #endif) resolves it to 0 here, the same as native_nodevtools. This is an
# explicit commented decision, not an accident of the defines below.
# …
target_compile_definitions(
    ${TARGET_NAME}
    PRIVATE
        USE_HAL_DRIVER
        PY32F071xB
        RURP_PLATFORM_PY32F071=1
        RURP_BOARD_NAME="py32f071"
        MONITOR_SPEED=250000
        DATA_BUFFER_SIZE=512
        RURP_PY32F071_PINMAP_CONFIGURED=1
)
```

Note for Q9's framing: after Phase 124's D-02 conversion, `DEV_TOOLS` is **absent** from this block entirely — it lives as a shared header default and is named here only in the comment. `RURP_HAS_VPP_DAC=0` goes as an eighth entry, directly after `RURP_PY32F071_PINMAP_CONFIGURED=1`, which keeps the two "the build supplies what the header tests" macros adjacent and lets one comment cover both.

`FIRESTARTER_COMMON_SOURCES` is 16 entries (`src/firestarter.cpp` … `lib/jsmn/src/jsmn.c`); the five `# PY32_EXCLUDED:` lines sit immediately above it. Adding the seam makes it 17.

**No `-Werror` anywhere.** `grep -rn Werror platform/ scripts/ .github/` → **zero hits**. The ARM warning budget is `-Wall -Wextra` (plus `-Os -ffunction-sections -fdata-sections -fno-common`, and `-fno-exceptions`/`-fno-rtti` for C++), uncounted. Link options include `-Wl,--gc-sections` and a map file. A new TU cannot trip a warnings gate on ARM because there isn't one — and the prototype compiles warning-free under host `-Wall -Wextra`, which is the best local proxy available.

**`check_build_warnings.py` has no ARM awareness at all**: `AVR_ENVS = ("uno", "uno328pb", "leonardo")` (:86) and `NATIVE_ENVS = ("native", "native_nodevtools")` (:87) are its entire universe. (Note `native_pinmap_provisional` is *not* in `NATIVE_ENVS` despite being recorded in the baseline — it must be passed explicitly.)

### C-15 — Criterion 3's "porcelain empty" clause is only meaningful post-commit, and only for the firmware repo

Criterion 3 offers `git status --porcelain` empty **or** a literal blob-SHA match. During the phase the two new files plus the CMake edit make porcelain non-empty *by design*, so:

- **Primary proof = the blob-SHA re-hash** (`git hash-object <path>` compared to the pre-phase values recorded below, and `git rev-parse HEAD:<path>` after committing).
- `git status --porcelain` empty is a **post-commit corroboration**, run after the phase's last code commit.

Current state, verified: `git -C firestarter status --porcelain` → **empty**. `git -C firestarter_app status --porcelain` → **not empty** (`M .gitignore`, untracked `.coverage`, `.planning/config.json`, `SECURITY.md`, `write_test_port.sh`). Any porcelain row in `125-NONREGRESSION.md` must name the firmware repo explicitly, or it will read as a failure it is not.

Also heed `124-VERIFICATION.md`'s live informational finding: never prove "untouched" with `git diff --stat | grep -v <file>` — the `N file changed` trailer survives the grep and the pipeline reports "(empty)" when it is not.

### C-16 — `check_permitted_claims.py` does not scan Phase 125's artifacts by default

`_DEFAULT_TARGETS` (:86–91) is exactly four Phase-130 files: `130-LEDGER.md`, `130-DECISION.md`, `130-RELEASE-NOTES-fw.md`, `130-RELEASE-NOTES-app.md`. Phase 125's artifacts are scanned only if explicitly named via `FIRESTARTER_CLAIMSCAN_TARGETS` (`os.pathsep`-separated; present-but-empty means zero targets, never a fall-back to defaults).

The eight patterns (`FORBIDDEN_PATTERNS`, :119–142), all case-insensitive, reported only when a `py32` token appears within `PROXIMITY_WINDOW = 1` lines. **Labels below are rendered with `_` in place of the source's `-`, and the regex column is the regex source rather than any matching string, so that this document does not trip the very gate it documents** — the same self-avoidance technique `test_pinmap_guard_fires.py`'s coverage-6 leg uses via string concatenation:

| label (`_` for `-`) | regex source |
|---|---|
| `runs_on_py32` | `runs\s+on\s+(?:a\s+|the\s+)?py32` |
| `works_end_to_end` | `works\s+end[-\s]to[-\s]end` |
| `silicon_verified` | `silicon[-\s]verified` |
| `bench_validated` | `bench[-\s]validated` |
| `hardware_validated` | `hardware[-\s]validated` |
| `flashed_a_py32` | `flashed\s+(?:a\s+|the\s+)?py32` |
| `closed_loop_vpp` | `closed[-\s]loop\s+vpp\s+(?:works|verified)` |
| `pin_map_correct` | `pin\s+map\s+(?:is\s+)?(?:correct|verified|validated)` |

Plus `REQUIRED_CAVEAT_PATTERN = no\s+PY32F071\s+hardware\s+exists` (document-level, not proximity-scoped). **Recommendation:** have the closing plan run `FIRESTARTER_CLAIMSCAN_TARGETS=.../125-NONREGRESSION.md python3 …/check_permitted_claims.py` as a real row, and include the canonical caveat sentence verbatim in the artifact.

### C-17 — A closed branch *does* implement a py32 VPP DAC; scope the `#error` wording to this branch

D-03's parenthetical says *"no board ships a VPP DAC implementation"*. True of the integration branch; not true of the repo's ref namespace. `origin/feature/py32f071-full-support` (PR #47, closed — Out of Scope per `REQUIREMENTS.md`) contains:

- `platform/py32f071/CMakeLists.txt:64` — `RURP_HAS_VPP_DAC=1`
- `include/rurp_platform.h:23–30` and `platform/py32f071/include/py32f071_board.h:15–19` — `RURP_HAS_VPP_DAC 1`, `RURP_VPP_DAC_BITS 12u`, `RURP_VPP_DAC_MAX_CODE 4095u`
- `platform/py32f071/src/analog.c:168–237` — `rurp_vpp_dac_write`, `rurp_vpp_control_enable`, and a proportional feedback loop

Nothing changes: PR #47 is excluded by requirement, and its tip is not an ancestor of `HEAD`. But two things follow. (1) The forced-DAC `#error` message must be scoped — *"…that this branch does not provide"* — not a universal claim a reader can falsify with one `git show`. (2) The py32 declaration being `0` here while a closed branch chose `1` is a genuine divergence worth one sentence in the artifact, so a later reader does not treat PR #47's `1` as prior art to restore. There is no hardware, so `0` is the only defensible value.

### C-18 — `768580f` adds the schema fields *without* the version bump — a worse cherry-pick than the one the record warns about

The record (`REQUIREMENTS.md` line 184, `125-CONTEXT.md` `<canonical_refs>`) warns that `05f4a77` "smuggles a `CONFIG_VERSION` bump". Verified exactly — `git show 05f4a77 -- include/rurp_shield.h` shows `-#define CONFIG_VERSION "VER06"` / `+#define CONFIG_VERSION "VER07"`, and walking all ten commits confirms the boundary:

```
04fd9b3  VER06     b964ee6  VER07
fc0b2c7  VER06     9134f2a  VER07
86f351a  VER06     d285b83  VER07
768580f  VER06     71278d0  VER07
05f4a77  VER07     a47228d  VER07
```

But `768580f` ("Persist common VPP calibration in board configuration") is **`include/rurp_types.h` only, +12 lines** — the calibration fields — and it sits *before* the bump. Cherry-picking `768580f` alone would change `rurp_configuration_t`'s layout while leaving `CONFIG_VERSION` literally `"VER06"`: a silent schema change with no migration signal, which is strictly worse than the visible bump. This strengthens "cherry-pick nothing" and should be the sentence the plan cites for VPP-01, because it is the failure mode a well-meaning "just take the types" shortcut would produce.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Declaring VPP control as a platform property (`RURP_HAS_VPP_DAC`) | **Build system** (`platformio.ini`-implicit via `__AVR__`; CMake `target_compile_definitions` for ARM) | Header (tests only) | Phase 124 D-14's lesson: a guard that defines what it tests is dead. `__AVR__` is compiler-supplied; every other target declares |
| Resolving the property to a compile-time constant | **Shared header** `include/rurp_vpp.h` | — | One file, two arms, no blanket default (D-06) |
| Refusing an impossible request at runtime | **Shared source** `src/rurp_vpp.cpp` | — | Returns `RURP_VPP_MANUAL_ADJUSTMENT_REQUIRED`; dependency-free (D-02) |
| Rejecting a capability nobody implements | **Shared source** `src/rurp_vpp.cpp` (`#if RURP_HAS_VPP_DAC → #error`) | — | C-4: the header's `!defined` arm cannot do this |
| Proving the refusal on every board macro-set | **Host test harness** `firestarter/tests/*.py` + host `g++` | — | PIO-invisible; no production build carries a test assertion (D-01) |
| Proving no ARM source-list drift | **Firmware gate** `scripts/check_cmake_manifest.py` | — | Reverse check forces name-or-reasoned-exclude (D-12, C-12) |
| Proving AVR cost | **Real AVR builds** + `scripts/check_size_baseline.py` | Evidence artifact (D-15 records, does not gate) | Three cold `pio run` invocations are also the *real cross-compiler* proof that the seam resolves |
| Proving PR #45 non-ancestry | **Host `git`, driven from a pytest** | — | C-2 command shape; C-11 says pytest, not `scripts/check_*.py` |
| ARM compile evidence | **GitHub Actions** `py32f071.yml` (`workflow_dispatch`) | — | `arm-none-eabi-gcc`/`cmake`/`ninja` absent locally; run URL + head SHA is the only admissible evidence (D-13/D-14) |
| Wire/host visibility of the capability | **nowhere, deliberately** | — | D-11 refuses `messages.toml` + codegen + host parity churn |

---

## Standard Stack

No new dependency is introduced or needed. The "stack" is the tooling already in the tree, at the versions measured this session.

### Core

| Tool | Version (measured) | Purpose | Why standard |
|---|---|---|---|
| PlatformIO Core | 6.1.19 | AVR + native builds and test runs | The project's build system since v1.0 |
| `platform-atmelavr` | 5.2.0 | Supplies `-ffunction-sections -fdata-sections -flto` / `-Wl,--gc-sections -flto -fuse-linker-plugin` | C-5's measurement rests on it |
| `toolchain-atmelavr` avr-gcc | 7.3.0 | The real cross compiler for the three AVR targets | Defines `__AVR__` unconditionally (C-13) |
| host `g++` | 14.2.0 (Debian) | D-01's harness compiler; also the native-env compiler | `test_pinmap_guard_fires.py`'s precedent resolves `$CXX` then `g++` |
| pytest | 9.1.1 (Python 3.12.13) | The harness runner and every firmware gate's paired test | 72 tests currently pass in `firestarter/tests/` |
| Unity (via PIO) | bundled | The native suites' framework — **untouched by this phase** | 141 cases / 17 suites on both pinned envs |

### Supporting

| Tool | Purpose | When to use |
|---|---|---|
| `avr-nm` | Prove a symbol is absent from the linked ELF | C-5's non-vacuity leg; reusable in the evidence artifact |
| `git cat-file -e` / `git merge-base --is-ancestor` | Criterion 1 | C-2's command shape |
| `git hash-object` / `git rev-parse HEAD:<path>` | Criterion 3 blob pin | Never a path-scoped `git diff` |
| `scripts/check_cmake_manifest.py` | ARM manifest reverse check | Must be run after the CMake edit |
| `scripts/check_size_baseline.py` (default mode) | Strict-equality AVR figures | D-16's already-armed comparator |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|---|---|---|
| Host `g++ -D__AVR__` legs | `avr-g++ -mmcu=<m> -c` legs (verified working: `static_assert(RURP_HAS_VPP_DAC == 0)` compiles clean for all three MCUs; `-DRURP_HAS_VPP_DAC=1` fails with the named `#error`) | Higher fidelity, but requires the PIO toolchain package on PATH; a leg that skips when it is absent fails OPEN (A-7). The three real `pio run` builds already discharge the real-compiler question — prefer those |
| A `scripts/check_pr45_ancestry.py` | `tests/test_pr45_non_ancestry.py` | The `scripts/` shape costs four BASE-08 artifacts (C-11) |
| `git status --porcelain` as Criterion 3's primary | Blob-SHA re-hash | Porcelain is non-empty mid-phase by design (C-15) |

**Installation:** none. No package is added to any manifest by this phase.

---

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.** No `npm`, `pip`, `cargo` or PlatformIO `lib_deps` entry is added. `lib_deps` is untouched (`fabiobatsilva/ArduinoFake@^0.4.0` remains the only entry, in the native envs). Both new files are hand-authored C/C++ in the existing tree, and the harness uses stdlib + pytest, both already present. Verdict: **no packages to audit; nothing removed, nothing flagged.**

---

## Architecture Patterns

### System Architecture Diagram

```
                     ┌──────────────────── build systems (the declaring tier) ────────────────────┐
                     │                                                                            │
   avr-gcc  ─────────┤  __AVR__ = 1  (compiler-supplied, all 3 MCUs — C-13)                       │
   (uno / uno328pb / │                                                                            │
    leonardo)        │                                                                            │
                     │                                                                            │
   CMake / ARM  ─────┤  target_compile_definitions: RURP_HAS_VPP_DAC=0  (D-07, explicit)          │
                     │                                                                            │
   host g++  ────────┤  neither  ──────────────────────────────────────────────┐                  │
   (harness leg 6)   └────────────────────────────────────────────────────────┼──────────────────┘
                                                                              │
                                    ┌─────────────────────────────────────────▼───────────────┐
                                    │  include/rurp_vpp.h                                      │
                                    │    #if !defined(RURP_HAS_VPP_DAC)                        │
                                    │      #if defined(__AVR__)  → define 0   (permanent)      │
                                    │      #else                 → #error     ◄─ leg 6 fires   │
                                    │    two enums, three declarations                         │
                                    └───────────────┬─────────────────────────────────────────┘
                                                    │ (included by exactly two things)
                    ┌───────────────────────────────┴───────────────────────────────┐
                    ▼                                                               ▼
      ┌──────────────────────────────────────┐                    ┌────────────────────────────────┐
      │ src/rurp_vpp.cpp                     │                    │ tests/<harness>.py's temp TU   │
      │   #if RURP_HAS_VPP_DAC → #error  ◄── leg 5 (forced DAC)   │   #include "rurp_vpp.h"        │
      │   control_mode()  → MANUAL           │                    │   main() prints mode + result  │
      │   set_vpp_target() → MANUAL_ADJ_REQ  │                    │   → 4 board legs, compile+run  │
      │   disable_vpp_control() → no-op      │                    └────────────┬───────────────────┘
      └──────────┬──────────────┬────────────┘                                 │
                 │              │                                              │ stdout: "mode=0 result=1"
     compiled by │              │ compiled by                                  ▼
                 ▼              ▼                                    pytest assertions
   3 AVR envs (all of src/)   ARM target (named in                   (exit 0 required, value parsed
   → -flto slim .o            FIRESTARTER_COMMON_SOURCES)             from stdout — never the exit code)
   → gc-sections + LTO drop
     all 3 symbols
   → 0 B flash, 0 B RAM
                 │
                 ▼
   ┌──────────────────────────────────────────────────────────────────────────┐
   │ NOT reached, deliberately (C-1):                                          │
   │   include/rurp_shield.h  — no #include; 46 TUs incl. 14 native host_stubs │
   │   the 3 native envs      — build_src_filter excludes src/rurp_vpp.cpp     │
   │   the wire / messages.toml / host constants (D-11)                        │
   └──────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| File | Responsibility | Status |
|---|---|---|
| `firestarter/include/rurp_vpp.h` | Resolve `RURP_HAS_VPP_DAC` (two arms, no default); declare two 2-value enums and three functions | **NEW** (~39 lines measured on the prototype) |
| `firestarter/src/rurp_vpp.cpp` | Reject `RURP_HAS_VPP_DAC=1` at the preprocessor; return `MANUAL` / `MANUAL_ADJUSTMENT_REQUIRED`; no-op disable | **NEW** (~18 lines) |
| `firestarter/platform/py32f071/CMakeLists.txt` | Name the seam in `FIRESTARTER_COMMON_SOURCES`; declare `RURP_HAS_VPP_DAC=0` | **+2 lines** (D-07, D-12) |
| `firestarter/tests/<harness>.py` | Six legs: 4 board compile-and-run, 1 forced-DAC compile-fail, 1 unset-non-AVR compile-fail; plus a no-skip meta leg and D-04's drift leg | **NEW** |
| `firestarter/tests/test_pr45_non_ancestry.py` | Criterion 1, C-2's command shape, `n == 10` guard, optional blob-divergence leg | **NEW** (recommended shape, C-11) |
| `firestarter/include/rurp_shield.h` | **unchanged** under the recommended resolution | see C-1 |
| `src/boards/rurp_common.cpp`, `include/rurp_types.h`, `src/rurp_config_utils.cpp` | **byte-identical** (Criterion 3) | blob SHAs below |
| `firestarter/platformio.ini` | **unchanged** under the recommended resolution | see C-1 / C-5 |

### Pattern 1: The build system declares; the header only tests

**What:** a capability macro's *value* comes from the compiler or the build file. The header contains only `#if !defined(...)` / `#error` and any derived-from-compiler arm.
**When to use:** every platform property. This is Phase 124 D-14's lesson, and D-06/D-07 are it applied before the fact.
**Example** (the in-tree precedent, `include/boards/py32f071_pinmap_guard.h` + `CMakeLists.txt`'s `RURP_PY32F071_PINMAP_CONFIGURED=1`, and the shape verified for this seam):

```c
/* include/rurp_vpp.h — no blanket default; the build supplies or the build breaks */
#if !defined(RURP_HAS_VPP_DAC)
#  if defined(__AVR__)
/* Permanent, not provisional: no Arduino/AVR-class RURP board carries a VPP DAC —
 * the rail is set by the operator's pot. Operator, 2026-07-31. */
#    define RURP_HAS_VPP_DAC 0
#  else
#    error "RURP_HAS_VPP_DAC must be defined by the board/platform build"
#  endif
#endif
```

```c
/* src/rurp_vpp.cpp — the second guard C-4 shows is required by D-03 */
#if RURP_HAS_VPP_DAC
#error "RURP_HAS_VPP_DAC=1 selects a closed-loop VPP DAC implementation that this branch does not provide"
#endif
```

### Pattern 2: A pytest that drives a real compiler, fail-closed

**What:** prove a compile-time property no PlatformIO env can reach, by resolving a host compiler and running it on a temp TU. Never skip when the compiler is missing.
**When to use:** any `#error`/`static_assert`/macro-resolution claim.
**Source:** `firestarter/tests/test_pinmap_guard_fires.py:65–108`, read end to end.

```python
def _resolve_compiler():
    compiler = shutil.which(os.environ.get("CXX", "g++"))
    assert compiler is not None, (
        "host C++ compiler not found on PATH (checked $CXX, falling back to "
        "'g++'). This must FAIL the suite, never be silently skipped"
    )
    return compiler

def _write_tu(tmp_path):                       # no fixture TU is committed
    tu_path = tmp_path / "pinmap_guard_tu.cpp"
    tu_path.write_text('#include "py32f071_pinmap_guard.h"\n')
    return tu_path

def _preprocess(compiler, tu_path, define=None):
    argv = [compiler, "-E", "-I", str(_INCLUDE_BOARDS)]   # argv list; no shell
    if define is not None:
        argv += [f"-D{_MACRO_NAME}={define}"]
    argv += [str(tu_path), "-o", os.devnull]
    return subprocess.run(argv, capture_output=True, text=True)
```

Also copy its **coverage-6 self-enforcement leg**, which reads its own source and asserts the strings `pytest.skip` and `mark.skipif` appear nowhere (built by concatenation so the assertion text does not trip its own check). That is the mechanism that keeps the fail-closed contract from being edited away.

### Pattern 3: The compile-and-run variant — what changes, and the process boundary

The pinmap precedent is preprocess-only (`-E`, output to `os.devnull`). D-01 needs compile-and-**run**. Four concrete differences, all validated by the prototype:

1. Drop `-E`; emit a real binary (`-o tmp_path/<leg>`), and pass both the temp `main.cpp` and the production `src/rurp_vpp.cpp` in one `g++` invocation.
2. Add `-std=gnu++17 -Wall -Wextra` and `-I <repo>/include` (the seam header lives in `include/`, not `include/boards/`).
3. Run the binary as a second `subprocess.run`, argv-list, `capture_output=True`.
4. **Cross the process boundary on stdout, not the exit code.** `RURP_VPP_MANUAL_ADJUSTMENT_REQUIRED == 1`, so `return (int)result;` would make the *correct* answer indistinguishable from a compile failure, a link failure or a crash — all of which also produce exit 1. Instead: require **run exit 0** and parse the value from stdout.

**Measured prototype output** (all six legs, one run):

```
leg=uno       compile=0 run_exit=0 stdout='mode=0 result=1' warnings=0B
leg=leonardo  compile=0 run_exit=0 stdout='mode=0 result=1' warnings=0B
leg=uno328pb  compile=0 run_exit=0 stdout='mode=0 result=1' warnings=0B
leg=py32f071  compile=0 run_exit=0 stdout='mode=0 result=1' warnings=0B
--- leg forced-DAC (must fail) ---        exit=1
#error "RURP_HAS_VPP_DAC=1 selects a closed-loop VPP DAC implementation that no board provides"
--- leg unset-and-non-AVR (must fail) --- exit=1
#error "RURP_HAS_VPP_DAC must be defined by the board/platform build"
```

The shim, verbatim:

```cpp
#include "rurp_vpp.h"
#include <cstdio>
int main(void) {
    printf("mode=%d result=%d\n", (int)rurp_vpp_control_mode(),
           (int)rurp_set_vpp_target_mv(12000, 200, 50));
    rurp_disable_vpp_control();
    return 0;
}
```

Board macro-sets used (the four legs; note C-6 on what they prove):

| leg | defines |
|---|---|
| uno | `-D__AVR__ -DARDUINO_AVR_UNO -DRURP_BOARD_NAME="uno" -DSERIAL_ON_IO` |
| leonardo | `-D__AVR__ -DARDUINO_AVR_LEONARDO -DRURP_BOARD_NAME="leonardo" -DDATA_BUFFER_SIZE=1024` |
| uno328pb | `-D__AVR__ -DARDUINO_AVR_ATmega328PB -DRURP_BOARD_NAME="uno328pb" -DSERIAL_ON_IO` |
| py32f071 | `-DRURP_PLATFORM_PY32F071=1 -DRURP_HAS_VPP_DAC=0 -DRURP_BOARD_NAME="py32f071"` |

`firestarter/tests/` is genuinely PlatformIO-invisible (PIO globs `test/`, not `tests/`) and has **no `conftest.py` anywhere in the repo** — `find . -name conftest.py -not -path './.pio/*'` returns nothing, and there is no `pytest.ini`, `pyproject.toml`, `setup.cfg` or `tox.ini` either. Registration is by filename convention alone; path resolution must be self-contained in the module, as `test_pinmap_guard_fires.py:56–60` does.

### Anti-Patterns to Avoid

- **Including `rurp_vpp.h` from `rurp_shield.h` without resolving C-1.** Measured cost: 141 → 0 native cases, 17 suites ERRORED.
- **Using the seam's return value as the process exit code.** `1` collides with every failure mode.
- **`git log --all --grep` or any `--all`-scoped reachability test for Criterion 1.** Passes vacuously; `--all` sees PR #45's own ref (C-2).
- **Treating `git merge-base --is-ancestor`'s exit 128 as "clean".** A bogus or unfetched SHA must be exit 2.
- **`git diff --stat <path> | grep -v <file>` to prove untouched.** The `N file changed` trailer survives the grep (`124-VERIFICATION.md`'s live finding).
- **Reaching for `RURP_PLATFORM_AVR` instead of `__AVR__`.** Never defined during an AVR build, and its header breaks native (C-13).
- **Adding a comparator or tolerance for Criterion 4.** D-15 deliberately chose record-without-gating; the strict comparator is already armed (C-8).
- **Lowering `FLOOR` or `FIXTURE_FLOOR` to quiet BASE-08.** A red gate there means an artifact went missing (C-11).
- **Describing AVR manual VPP control as provisional, "for now", or "pending hardware".** D-05: it is permanent.

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Prove a `#error` fires | A prose assertion, or a fixture header committed next to the real one | `subprocess.run([g++, ...])` on a `tmp_path` TU, per `test_pinmap_guard_fires.py` | The precedent exists, is 6-tests green, and is fail-closed by construction |
| Prove a commit is not an ancestor | A `git log` grep, a message scan, or a manual eyeball | `git cat-file -e` + `git merge-base --is-ancestor`, scoped to HEAD | C-2: the grep shape returns 0 rows today and would keep doing so after a cherry-pick |
| Prove a file is byte-identical | A path-scoped `git diff` | `git hash-object` / `git rev-parse HEAD:<path>` against the pre-phase blob SHA | Criterion 3 forbids the diff shape explicitly; `124-VERIFICATION.md` documents why |
| Prove a source list has no drift | A hand-maintained list, or a CMake parser of your own | `scripts/check_cmake_manifest.py` (already armed, reverse check proven in C-12) | It already resolves the three path idioms and enforces reasoned exclusions |
| Prove AVR flash didn't move | A remembered number, or a re-derived expectation | `scripts/check_size_baseline.py` default mode against `size_baseline.json` | Strict equality, armed, never-vacuous, proven strict in C-8 |
| Prove a symbol was eliminated | Inferring it from an unchanged byte count | `avr-nm <elf> \| grep -cE '<the three names>'` | An unchanged total can hide an addition offset by a removal; the symbol query cannot |
| Detect an unnamed new `src/` file | A grep of `CMakeLists.txt` | The reverse check that already exists | C-12: `rglob` + `_SOURCE_EXTS`, exit 1, exact message |
| Enforce "no forbidden claim" | Careful prose | `check_permitted_claims.py` via `FIRESTARTER_CLAIMSCAN_TARGETS` | Eight patterns + proximity + required caveat, already written (C-16) |

**Key insight:** every gate this phase needs already exists and is already armed. Phase 125's engineering risk is not in the two new files — it is in the *interaction* between a new preprocessor `#error` and the 46 translation units that include `rurp_shield.h`. That is exactly the surface a custom, hand-rolled check would have missed and the existing `pio test -e native` caught in 92 seconds.

---

## Runtime State Inventory

Not a rename/refactor/migration phase — it adds two files and two build-file lines, renames nothing and migrates nothing. Filled in anyway, because the interaction surface is the whole risk.

| Category | Items found | Action required |
|---|---|---|
| Stored data | **None.** No datastore keys the seam's names; `rurp_configuration_t` is untouched and `CONFIG_VERSION` stays `"VER06"` (verified at `include/rurp_shield.h:46`) | none |
| Live service config | **None in the sense of external services.** The one live-config item is CI: `py32f071.yml`'s `workflow_dispatch` must be triggered against the pushed ref for D-13's evidence. Triggers verified on the current tree (C-7) | operator-gated push + dispatch (D-14) |
| OS-registered state | **None** — no task, service, launchd plist or pm2 entry references anything this phase adds. Verified by scope: nothing outside `firestarter/` changes | none |
| Secrets / env vars | **None added.** Three *existing* env seams are read by the gates this phase runs, all read once at import so `monkeypatch.setenv` is ineffective: `FIRESTARTER_SIZE_BASELINE`, `FIRESTARTER_MANIFEST_ROOT`, `FIRESTARTER_CLAIMSCAN_TARGETS` (plus `FIRESTARTER_FW_ROOT` / `FIRESTARTER_CMD_ADMISSION_SRC` host-side). Any test pointing them elsewhere must use a real subprocess | none |
| Build artifacts | **`.pio/build/{uno,uno328pb,leonardo}/` gain `src/rurp_vpp.cpp.o`** (verified present, 4520/4520/4508 B, LTO slim). This is automatic — no AVR env has a `build_src_filter`. Existing `.pio` trees are stale after the phase; every measurement must follow `rm -rf .pio/build/<env>` (or `pio run -t clean`) then a **single** `pio run` invocation with an extended timeout — a default 2-minute Bash timeout truncates the toolchain build mid-compile and silently contaminates the figure (`124-04-SUMMARY.md`'s recorded trap) | clean-then-single-invocation per env |

**Not found, stated explicitly:** no `messages.toml` / `include/messages.h` codegen interaction (D-11 refuses the wire surface, and `messages.h` is codegen-generated from the meta repo — a wording-only edit there gives a zero header diff); no `pinouts.json` / `chip_database.json` interaction; no golden-trace interaction (`tests/test_golden_trace_identity.py` is 6-tests green and pins blob SHAs of files this phase does not touch).

---

## Common Pitfalls

### Pitfall 1: The native envs are non-AVR compile targets, and D-06 treats them as unconfigured boards

**What goes wrong:** 141 cases / 17 suites → 0 cases / 17 ERRORED, on both pinned envs plus `native_pinmap_provisional`.
**Why:** `rurp_shield.h` is included by 14 `host_stubs.cpp` files and by the production TUs the native envs compile; host `g++` defines no `__AVR__`; no native env declares `RURP_HAS_VPP_DAC`.
**How to avoid:** don't include the seam header from `rurp_shield.h` (option A), or declare the macro in both native envs (option B). Both measured in C-1.
**Warning signs:** `include/rurp_vpp.h:N:6: error: #error "RURP_HAS_VPP_DAC must be defined..."` repeated once per suite; `pio test` reporting a *case* count equal to the *suite* count.

### Pitfall 2: A zero flash delta that means nothing

**What goes wrong:** the phase records "0 B" without establishing that the new TU was compiled at all — the same number a `build_src_filter` typo would produce.
**Why:** `-flto` + `--gc-sections` genuinely produce 0 B here, so the honest result and the vacuous result look identical.
**How to avoid:** pair the figure with two positive facts, as C-5 does — the `.o` exists in each build dir, and `avr-nm` on the ELF finds zero of the three seam symbols (while finding the five unrelated pre-existing `vpp` symbols, proving the grep isn't matching nothing).
**Warning signs:** a delta table with no `.o`/`avr-nm` corroboration; a measurement taken without `rm -rf .pio/build/<env>` first.

### Pitfall 3: Criterion 1 discharged by a command that cannot fail

**What goes wrong:** `git log --all --grep=<sha>` returns 0 rows forever, so the gate is green regardless of what landed.
**Why:** `--grep` searches messages; `--all` (in any reachability variant) sees PR #45's own fetched ref.
**How to avoid:** C-2's shape, with the `n == 10` count assertion and explicit exit-128 handling.
**Warning signs:** a check whose green output does not name how many SHAs it examined; any appearance of `--all`.

### Pitfall 4: The forced-DAC leg passes because the header cannot reject `=1`

**What goes wrong:** D-03's non-vacuity leg exits 0, and the whole "the macro is genuinely consulted" argument evaporates.
**Why:** D-06's block only tests `!defined` (measured in C-4: `-DRURP_HAS_VPP_DAC=1` → exit 0).
**How to avoid:** author the second `#if RURP_HAS_VPP_DAC → #error` in `src/rurp_vpp.cpp`, and make the forced-DAC leg compile the `.cpp`.
**Warning signs:** a forced-DAC leg that only `#include`s the header; a leg using `-E` where a `.cpp` compile is needed.

### Pitfall 5: A `scripts/check_*.py` that silently owes BASE-08 four artifacts

**What goes wrong:** `tests/test_checker_convention.py` goes red on two legs the moment the checker lands (proven in C-11).
**Why:** the convention is filesystem-derived with hardcoded floors; there is no allow-list.
**How to avoid:** use `tests/test_pr45_non_ancestry.py`, or add all four artifacts in the same commit.
**Warning signs:** `FAILED …::test_every_checker_has_paired_test_module` / `…::test_every_checker_has_planted_fixture`.

### Pitfall 6: D-04's drift leg grepping `platformio.ini` for `ARDUINO_AVR_*`

**What goes wrong:** the leg fails on arrival; the "fix" is then to weaken it into something vacuous.
**Why:** those macros come from the framework/board JSON, never from `platformio.ini` (C-6's table).
**How to avoid:** anchor on `[env:<name>]` + `board = <name>` for AVR, and `RURP_PLATFORM_PY32F071=1` / `RURP_BOARD_NAME="py32f071"` for ARM.
**Warning signs:** a drift assertion whose failure message mentions `ARDUINO_AVR_UNO`.

### Pitfall 7: A `git status --porcelain` empty row that reads as a failure

**What goes wrong:** Criterion 3's porcelain clause is run mid-phase, or run against `firestarter_app`, and reports dirt.
**Why:** the phase's own new files make the firmware repo dirty until committed; `firestarter_app` is dirty right now for unrelated reasons (C-15).
**How to avoid:** blob-SHA re-hash is primary; run porcelain only post-commit and only against `firestarter`, naming the repo in the row.

### Pitfall 8: Overclaiming what the four board legs prove

**What goes wrong:** the artifact implies four independent per-board verifications; a reader with `git grep` finds the seam reads only two macros.
**Why:** C-6 — the three AVR legs are one fact.
**How to avoid:** say "uniformity across three AVR targets by one compiler-supplied predicate, plus one explicit ARM declaration", and note that the *real* AVR-compiler resolution is discharged by the three `pio run` builds Criterion 4 already requires.

### Pitfall 9: Assuming the new harness has CI coverage

**What goes wrong:** the phase closes believing CI runs the six legs; it does not, on this branch.
**Why:** `pytest tests/ -v` lives only in `build.yml` (`main`) and `beta-build.yml` (`beta`); `py32f071.yml` has no pytest step (C-7).
**How to avoid:** record the verbatim local `pytest` output in `125-NONREGRESSION.md` as the primary evidence, and say plainly that no CI leg on this branch executes it.

### Pitfall 10: A stale knowledge graph read as current

`.planning/graphs/graph.json` exists but is **720 h old and 577 commits behind** (`gsd-tools graphify status`: `stale: true`, `built_at_commit: f4150b8`, `current_commit: 24f7544`). It predates Phase 124's entire landing, so it does not know `include/rurp_platform.h`, `platform/py32f071/`, or any Phase-123/124 gate. Every structural claim in this document was derived from the live trees instead; treat graph relationships as approximate at best.

---

## Code Examples

### Criterion 1 — non-vacuous PR #45 non-ancestry (verified command shapes)

```python
# tests/test_pr45_non_ancestry.py  (recommended shape — C-11)
PR45_SHAS = (
    "04fd9b3", "fc0b2c7", "86f351a", "768580f", "05f4a77",
    "b964ee6", "9134f2a", "d285b83", "71278d0", "a47228d",
)  # exactly the 10 in `git rev-list origin/beta..origin/feature/common-vpp-calibration`

def _git(*args):
    return subprocess.run(["git", "-C", str(_REPO_ROOT), *args],
                          capture_output=True, text=True)

def test_no_pr45_commit_is_an_ancestor_of_head():
    assert len(PR45_SHAS) == 10, "never-vacuous: the SHA list must be the full 10"
    checked, ancestors = 0, []
    for sha in PR45_SHAS:
        exists = _git("cat-file", "-e", f"{sha}^{{commit}}")
        assert exists.returncode == 0, (            # exit-2 class: tool/config error,
            f"{sha} is not a local object -- fetch "  # NEVER a silent clean pass
            f"origin/feature/common-vpp-calibration first; an absent object must "
            f"not read as 'not an ancestor'"
        )
        r = _git("merge-base", "--is-ancestor", sha, "HEAD")
        assert r.returncode in (0, 1), f"git failed unexpectedly for {sha}: {r.stderr}"
        if r.returncode == 0:
            ancestors.append(sha)
        checked += 1
    assert checked == 10
    assert not ancestors, f"PR #45 commits reachable from HEAD: {ancestors}"
```

Observed against `HEAD = a145081b59d94530583b9ce365db03ff567d0c2c`: all ten `not-ancestor`; `git cat-file -e` exit 0 for all ten; exit 128 for a fabricated SHA.

Optional second leg — content divergence from PR #45's blobs:

```python
PR45_BLOBS = {
    "include/rurp_vpp.h":  "c982173813b38ec745b59d6e02817f2504d6c6b4",
    "src/rurp_vpp.cpp":    "fcbe009dffcd46139802f8779865a1d7aa331880",
}
# assert git hash-object <path> != PR45_BLOBS[path] for both
```

### Criterion 3 — the pin, with its pre-phase blob SHAs

Recorded this session from `HEAD = a145081`, with worktree `git hash-object` agreeing exactly:

| path | blob SHA (pre-phase) |
|---|---|
| `src/boards/rurp_common.cpp` | `5de1c8a1494200d8b2db210c3fd9d2d577a19b2b` |
| `include/rurp_types.h` | `d3fe5203a91527bdb7b20a33843c81065e21c613` |
| `src/rurp_config_utils.cpp` | `6705fd46e07a2d359d161dc2e7728cb4e45f89c7` |
| `include/rurp_shield.h` (not pinned; recorded for the option-A/B decision) | `602fe6f326a042ab71efd111e4dfcf3a6e41dd46` |

```bash
# post-phase, per file — the only admissible shape
git -C firestarter hash-object src/boards/rurp_common.cpp    # must equal 5de1c8a…
git -C firestarter hash-object include/rurp_types.h          # must equal d3fe520…
git -C firestarter hash-object src/rurp_config_utils.cpp     # must equal 6705fd4…
grep -n 'define CONFIG_VERSION' firestarter/include/rurp_shield.h
#   46:#define CONFIG_VERSION "VER06"        <- must stay literally this
git -C firestarter status --porcelain        # post-commit corroboration only (C-15)
```

### Criterion 4 — the flash delta, measured (the exact sequence used)

```bash
rm -rf .pio                                  # or: pio run -t clean -e <env>
for e in uno uno328pb leonardo; do
  pio run -e $e | grep -E '^(RAM|Flash):'    # ONE invocation per env, extended timeout
done
# non-vacuity, both directions:
ls .pio/build/$e/src/rurp_vpp.cpp.o
avr-nm .pio/build/uno/firestarter_uno.elf \
  | grep -cE 'rurp_vpp_control_mode|rurp_set_vpp_target_mv|rurp_disable_vpp_control'   # 0
# then the armed comparator:
python3 scripts/check_size_baseline.py \
  --avr-log uno=<log> --avr-log uno328pb=<log> --avr-log leonardo=<log>
```

Observed with the seam present: `PASS: uno(flash=23954/32256,ram=1573/2048), uno328pb(flash=24004/32384,ram=1579/2048), leonardo(flash=26016/28672,ram=2014/2560)` — exit 0, 0 B / 0 B on all three.

### The ARM manifest edit (two lines, both gate-verified)

```cmake
set(FIRESTARTER_COMMON_SOURCES
    "${REPOSITORY_ROOT}/src/firestarter.cpp"
    "${REPOSITORY_ROOT}/src/rurp_vpp.cpp"          # ← D-12: named, never PY32_EXCLUDED
    …
)

target_compile_definitions(
    ${TARGET_NAME}
    PRIVATE
        …
        RURP_PY32F071_PINMAP_CONFIGURED=1
        RURP_HAS_VPP_DAC=0                          # ← D-07: the build declares; the
                                                    #   header only tests (Phase 124 D-14)
)
```

Verified: gate exit 0 at 24 enforced sources with both lines; exit 1 with the named message if the source line is omitted.

---

## State of the Art

| Old approach | Current approach | When changed | Impact on this phase |
|---|---|---|---|
| `DEV_TOOLS` presence semantics (`#ifdef`) | value semantics (`#ifndef DEV_TOOLS / #define DEV_TOOLS 0`), shared default | Phase 124 Plan 06 (D-02) | `DEV_TOOLS` is **absent** from the ARM `target_compile_definitions` block; do not expect to find it there (C-14) |
| `RURP_PY32F071_PINMAP_CONFIGURED` defined by the header that tested it | `#define` moved into CMake defines; header tests only, via a dependency-free fragment | Phase 124 Plan 09 (D-14) | The direct ancestor of D-06/D-07, and the in-tree template for the seam's comment style |
| Two pinned native envs | three (`native_pinmap_provisional` added, 10 cases / 1 suite, never folded into either pinned `test_filter`) | Phase 124 Plan 08 | C-1 breaks **all three**; the third is not in `check_build_warnings.py`'s `NATIVE_ENVS` |
| `size_baseline.json` = BASE-01 figures | re-baselined to the post-landing tree; BASE-01 frozen as `size_baseline_base01.json` | Phase 124 Plan 10 | D-15/D-16 measure against the live file; the frozen one is reached only by explicit `--baseline` |
| 48 tests in `firestarter/tests/` | **72** | Phase 124 | The harness raises it again; assert the new number, don't recall the old |
| host suite ~1134 | **1158 passed, 0 skipped** | post-124 | The number to re-assert if any host row is run |

**Deprecated / not what it looks like:**

- `include/rurp_platform.h`'s `RURP_PLATFORM_AVR` — never defined during an AVR build; its `RURP_PLATFORM_NATIVE` arm references a macro defined nowhere (C-13).
- `research/SUMMARY.md`'s "`RURP_VPP_DAC_BITS` + consistency `#error`" in the header — dropped by D-09; C-4 replaces it with a plain `#if RURP_HAS_VPP_DAC → #error` in the `.cpp`.
- `firestarter/.github/workflows/build.yml` — `main`-only, therefore dormant under this branch model; not an oracle for anything here.

---

## Assumptions Log

Deliberately short. Almost everything above was executed.

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | The ARM target compiles `src/rurp_vpp.cpp` cleanly (`-Wall -Wextra`, `-fno-exceptions`, `-fno-rtti`, `cxx_std_17`, Cortex-M0+). Grounds: D-02 dependency-freedom, and the identical source compiles warning-free under host `g++ -std=gnu++17 -Wall -Wextra`. **Not locally measurable — `arm-none-eabi-gcc`, `cmake`, `ninja` all absent.** | ARM landing | Low. If wrong, D-13's CI run is exactly what surfaces it — which is the reason D-13 exists. Must be discharged by a run URL + head SHA, never by a local `pio` run |
| A2 | ARM flash/RAM cost of the seam is also ~0 B (same `-ffunction-sections -fdata-sections` + `-Wl,--gc-sections`, no `-flto` on ARM, zero callers) | ARM landing | Low, and out of scope: Criterion 4 binds AVR only, and no ARM size baseline exists (FUT-ARMSIZE). State ARM size as **not measured** |
| A3 | `origin/feature/common-vpp-calibration` still exists on the remote, so a fresh clone can fetch the ten objects Criterion 1 needs. Verified present locally; the remote was not re-queried | Criterion 1 | Low. The gate must exit 2 (not 0) when the objects are absent — C-2 already requires that |
| A4 | The prototype header/`.cpp` I measured are *representative* of what the plan will author (39 / 18 lines; enums and signatures per D-09/D-10). A materially larger `.cpp` could in principle change the delta | Criterion 4 | Low, but it is why Criterion 4 says *measure*. Re-measure on the real files; do not carry my figures forward as the phase's evidence |

---

## Open Questions

1. **Option A or option B for C-1?** — This is the one decision research cannot make, because it changes what the `<domain>` section says the phase delivers.
   - What we know: both work, measured. A needs zero build-file edits and matches D-11's own statement of the macro's consumers; B keeps the `#include` the ROADMAP's `Depends on` line describes, at the cost of two `platformio.ini` lines and a capability declaration for a non-board target.
   - What's unclear: whether the operator values the `#include` as a discoverability signal enough to pay B's cost.
   - Recommendation: **A**, and record the `#include`'s absence as a deliberate decision in `125-NONREGRESSION.md` with C-1's measured numbers as the reason. If B is chosen, it must ship with a recorded 141/17 on both pinned envs.

2. **Where does D-03's forced-DAC `#error` live, and what does it say?** — C-4 shows one is required and CONTEXT never quotes it.
   - What we know: D-09/D-11 point to `src/rurp_vpp.cpp`; the message must be scoped to this branch (C-17), because PR #47 does contain a py32 DAC implementation.
   - Recommendation: `.cpp`, with branch-scoped wording. The forced-DAC leg then compiles the `.cpp`, not just the header.

3. **Does D-04's drift leg keep its `platformio.ini` anchor?** — C-6 shows the named macros are not there.
   - Recommendation: keep the leg, change the anchor to `[env:<name>]` + `board = <name>` (AVR) and `RURP_PLATFORM_PY32F071=1` / `RURP_BOARD_NAME="py32f071"` (ARM). Do not widen it into a parser.

4. **Should the phase also run the three `avr-g++` compile legs?** — Verified working (`static_assert(RURP_HAS_VPP_DAC == 0)` clean for atmega328p/328pb/32u4; forced-DAC fails).
   - What's unclear: how to require the toolchain without a skip that fails OPEN.
   - Recommendation: **no.** The three cold `pio run` builds Criterion 4 already requires *are* the real-cross-compiler proof — a `#error` would have failed those builds. Adding a toolchain-dependent pytest leg buys nothing and risks a fail-open skip.

5. **Is `test_revision_byte_values_match_firmware_enum`'s hollowness worth a seed?** (C-9) — Out of scope here; recommend a backlog seed rather than a Phase-125 fix, since it edits a host gate this phase otherwise does not touch.

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| PlatformIO Core | AVR + native builds, Criterion 4 | ✓ | 6.1.19 | — |
| `platform-atmelavr` | the three AVR envs | ✓ | 5.2.0 | — |
| `toolchain-atmelavr` (`avr-gcc`/`avr-g++`/`avr-nm`) | AVR builds, symbol-elimination proof | ✓ | avr-gcc 7.3.0 | — |
| host `g++` | D-01 harness, native envs | ✓ | 14.2.0 | — |
| Python + pytest | harness, all gates | ✓ | 3.12.13 / pytest 9.1.1 | — |
| `git` (with PR #45 refs fetched) | Criterion 1, Criterion 3 | ✓ | all ten objects resolve locally | `git fetch origin feature/common-vpp-calibration`; absent objects → exit 2 |
| `gh` | D-13's dispatch + run-URL capture | ✓ (used read-only in Phase 124) | — | operator-gated; **no task may run it** (D-14) |
| `arm-none-eabi-gcc` | ARM compile/size | ✗ | — | **CI only** (`py32f071.yml`), cited by run URL + head SHA |
| `cmake` | ARM configure | ✗ | — | same |
| `ninja` | ARM build | ✗ | — | same |
| PY32F071 hardware | any silicon claim | ✗ | — | **none — no PY32F071 hardware exists.** Every such claim is out of scope by requirement |

**Missing with no fallback:** PY32F071 silicon. Nothing in this phase needs it, and nothing may claim it.
**Missing with fallback:** the entire ARM toolchain. The fallback is a CI `workflow_dispatch`, which is exactly D-13, and it is operator-gated by D-14.

---

## Validation Architecture

`workflow.nyquist_validation` is not set to `false` in `.planning/config.json` (the key is absent; `workflow` carries `research`, `plan_check`, `verifier`, `code_review`) → treated as enabled.

### Test Framework

| Property | Value |
|---|---|
| Framework (gates + harness) | pytest 9.1.1 on Python 3.12.13 |
| Config file | **none** — no `pytest.ini`, `pyproject.toml`, `setup.cfg`, `tox.ini`, and **no `conftest.py` anywhere** in `firestarter/`. Path resolution is self-contained per module (house rule, `test_pinmap_guard_fires.py:26–28`) |
| Framework (firmware unit) | Unity via PlatformIO — **not touched by this phase** |
| Quick run command | `cd firestarter && python3 -m pytest tests/ -q` (currently **72 passed**, ~3 s) |
| Full suite command | `cd firestarter && python3 -m pytest tests/ -q` **and** `pio test -e native` **and** `pio test -e native_nodevtools` (141/17 each, ~2 min each cold) |
| Host suite (regression only) | `cd firestarter_app && python3 -m pytest -q` (**1158 passed, 0 skipped**, ~145 s) |
| CI legs on this branch | **none** for `pytest tests/` — see C-7 |

### Phase Requirements → Test Map

| Req ID | Behavior | Test type | Automated command | File exists? |
|---|---|---|---|---|
| VPP-01 | No PR #45 commit is an ancestor of `HEAD`; the SHA list is the full ten; an unresolvable SHA is exit 2 | unit (git) | `python3 -m pytest tests/test_pr45_non_ancestry.py -q` | ❌ Wave 0 |
| VPP-01 | The two new files' blob SHAs differ from PR #45's (`c982173…`, `fcbe009…`) | unit | same module, second leg | ❌ Wave 0 |
| VPP-02 | `rurp_set_vpp_target_mv()` → `MANUAL_ADJUSTMENT_REQUIRED` and `rurp_vpp_control_mode()` → `MANUAL` on all four board macro-sets, compiled and **run** | integration (compile+run) | `python3 -m pytest tests/test_vpp_seam_manual_on_every_board.py -q` | ❌ Wave 0 |
| VPP-02 | Forced-capability leg: `-DRURP_HAS_VPP_DAC=1` → non-zero `g++` exit with the named `#error` (D-03) | integration | same module | ❌ Wave 0 |
| VPP-02 | Unset-and-non-AVR leg: no `__AVR__`, no `RURP_HAS_VPP_DAC` → non-zero exit with the named `#error` (D-08) | integration | same module | ❌ Wave 0 |
| VPP-02 | Drift leg: each board's real anchor still present in its build config (C-6's anchors, **not** `ARDUINO_AVR_*`) | unit | same module | ❌ Wave 0 |
| VPP-02 | No-skip self-enforcement: the harness module's own source contains no `pytest.skip` / `mark.skipif` | unit | same module (copy `test_pinmap_guard_fires.py` coverage 6) | ❌ Wave 0 |
| VPP-03 | Three pinned files byte-identical (blob-SHA re-hash, never a path-scoped diff) | smoke | `git -C firestarter hash-object <3 paths>` vs the table in §"Criterion 3" | ✅ (git) |
| VPP-03 | `CONFIG_VERSION` still literally `"VER06"` | smoke | `grep -n 'define CONFIG_VERSION' firestarter/include/rurp_shield.h` | ✅ |
| VPP-03 | AVR flash **and** RAM measured for all three targets, non-vacuously | integration (build) | `rm -rf .pio; pio run -e {uno,uno328pb,leonardo}` + `ls .pio/build/$e/src/rurp_vpp.cpp.o` + `avr-nm … \| grep -cE '<3 names>'` | ✅ (tooling) |
| VPP-03 | Strict comparator green (or the D-16 re-baseline path taken) | integration | `python3 scripts/check_size_baseline.py --avr-log …×3` | ✅ |
| non-regression | Both pinned native envs still 141 cases / 17 suites, all PASSED | integration | `pio test -e native`; `pio test -e native_nodevtools` | ✅ — **the C-1 tripwire; non-optional** |
| non-regression | Third native env still 10/1 | integration | `pio test -e native_pinmap_provisional` | ✅ |
| non-regression | ARM manifest reverse check green with the seam named | unit | `python3 scripts/check_cmake_manifest.py` (expect 24 enforced sources) | ✅ |
| non-regression | Existing firmware gates still green | unit | `python3 -m pytest tests/ -q` (expect > 72), `check_landing_range.py`, `check_orphan_provisional.py` | ✅ |
| non-regression | Host repo unmoved | unit | `cd firestarter_app && python3 -m pytest -q` (expect 1158, 0 skipped); `pytest tests/test_revision_constants_parity.py -q` (expect 13) | ✅ |
| claim gate | `125-NONREGRESSION.md` carries no forbidden phrase and does carry the canonical caveat | unit | `FIRESTARTER_CLAIMSCAN_TARGETS=<path> python3 .planning/phases/123-…/check_permitted_claims.py` | ✅ (C-16: must be named explicitly) |
| D-13 | ARM compile evidence | manual-only | operator runs `git push` + `gh workflow run py32f071.yml`; record run URL + head SHA | **manual — no local ARM toolchain, and D-14 forbids any task running either command** |

### Sampling Rate

- **Per task commit:** `cd firestarter && python3 -m pytest tests/ -q` (~3 s). Cheap, and it covers the harness plus every existing gate's paired test.
- **After the file-authoring task, and after any edit to `rurp_shield.h` or `platformio.ini`:** `pio test -e native` (~2 min cold). This is the C-1 tripwire; it is the single highest-value check in the phase and it must not be deferred to the closing plan.
- **Per wave merge:** `pytest tests/ -q` + `pio test -e native` + `pio test -e native_nodevtools` + `check_cmake_manifest.py`.
- **Phase gate (closing plan, all re-executed, never copied from a SUMMARY):** the full row table above, including three cold AVR builds with the `rm -rf .pio/build/<env>` + single-invocation + extended-timeout discipline, the `avr-nm` non-vacuity leg, the blob-SHA re-hash, the host suite, and the claim gate. Then `/gsd-verify-work`.

### Wave 0 Gaps

- [ ] `firestarter/tests/test_vpp_seam_manual_on_every_board.py` — VPP-02, six legs + drift leg + no-skip meta leg
- [ ] `firestarter/tests/test_pr45_non_ancestry.py` — VPP-01, ten SHAs, `n == 10` guard, exit-2 handling, optional blob-divergence leg
- [ ] No shared fixtures needed — the project's house rule is self-contained per-module path resolution, and there is no `conftest.py` to extend
- [ ] No framework install needed — pytest 9.1.1, `g++` 14.2.0, PIO 6.1.19 and the AVR toolchain are all present
- [ ] **If a `scripts/check_*.py` is chosen for VPP-01 instead:** additionally `tests/test_check_<X>.py`, `tests/fixtures/planted_<X>*`, and `FLOOR 5→6` + `FIXTURE_FLOOR 10→11` in the same commit (C-11)

---

## Security Domain

`security_enforcement` is not set in `.planning/config.json`, so it is treated as enabled. This phase adds no network, parsing, authentication, storage or cryptographic surface; the relevant category is physical safety near a high-voltage rail, which the project treats with the same seriousness.

### Applicable ASVS Categories

| ASVS category | Applies | Standard control here |
|---|---|---|
| V2 Authentication | no | No identity surface; nothing wire-visible (D-11) |
| V3 Session Management | no | No session surface |
| V4 Access Control | **partly** | The declaration is *deny-by-default*: a non-AVR target that forgets `RURP_HAS_VPP_DAC` fails at the preprocessor rather than silently inheriting manual control near an unregulated rail (D-07). Verified: bare host `g++` → exit 1 |
| V5 Input Validation | **no, deliberately** | `rurp_set_vpp_target_mv()` accepts any `(target_mv, tolerance_mv, timeout_ms)` and unconditionally refuses. D-10 drops PR #45's `INVALID_ARGUMENT` because only the closed-loop code could produce it. Refusing everything is stricter than validating anything |
| V6 Cryptography | no | None used or added |
| V14 Configuration | **yes** | `CONFIG_VERSION` stays literally `"VER06"`; `rurp_configuration_t` is untouched; three files pinned byte-identical. C-18 is the concrete configuration-integrity threat this pin defends against |

### Known Threat Patterns

| Pattern | STRIDE | Standard mitigation | Status here |
|---|---|---|---|
| A capability guard that defines what it tests, so it can never fire | Tampering / Repudiation | The build system supplies the value; the header only tests it | D-06/D-07 by design; the `#error` proven able to fire (exit 1 measured), and D-03/D-08 give it two dedicated legs |
| A silent schema change to persisted configuration | Tampering | Pin the schema files by blob SHA and the version string literally | Criterion 3, with pre-phase SHAs recorded. C-18 shows `768580f` is precisely this attack shape by accident |
| A new capability declaration widening an untested code path near a 12–25 V rail | Elevation of privilege (physical) | Zero production callers; the seam returns a refusal; no register is touched | D-09/D-11, and `avr-nm` proving all three symbols absent from the shipped AVR image |
| An honest-looking measurement that proves nothing (a vacuous zero, a vacuous gate) | Repudiation | Never-vacuous guards; positive corroboration of every negative | C-2, C-5, C-8, C-12 — each verified to fail when it should |
| A claim about silicon that no evidence supports | Repudiation | The Validation Ceiling plus `check_permitted_claims.py` (8 patterns + required caveat) | C-16; and **no PY32F071 hardware exists**, stated in this document's header |

---

## Sources

### Primary (HIGH confidence — executed in this devcontainer, this session)

- Firmware tree `/workspaces/firestarter` @ `v1.23-py32f071-integration` `a145081b59d94530583b9ce365db03ff567d0c2c`, `git status --porcelain` empty before and after.
- Throwaway `tar` copy of that tree under the scratchpad: seam authored, `pio run -e {uno,uno328pb,leonardo}` before/after, `pio test -e native` in three configurations, `avr-nm` on the linked ELFs, `check_cmake_manifest.py` / `check_size_baseline.py` / `test_checker_convention.py` driven against planted violations. **Neither real repo nor either gitignored worktree (`firestarter_py32_ci/`, `firestarter_app_py32/`, both `git status --porcelain` = 0 lines) was written to.**
- `firestarter/platformio.ini`, `include/rurp_shield.h`, `include/rurp_platform.h`, `platform/py32f071/CMakeLists.txt`, `scripts/check_{cmake_manifest,size_baseline,build_warnings,orphan_provisional,landing_range}.py`, `tests/test_{pinmap_guard_fires,checker_convention}.py`, `scripts/baseline/size_baseline.json`, `.github/workflows/{py32f071,beta-build,build}.yml` — all read directly.
- `firestarter_app` @ `ccbc401e16e2d2298f7376c3086164700bba0278`: `tests/test_revision_constants_parity.py`, `tests/scan_paths.py`, `tests/fw_presence.py`, `tools/check_is_memory_cmd_no_ifdef.py`; full suite run (**1158 passed, 0 skipped**).
- `origin/feature/common-vpp-calibration` @ `a47228d` (10 commits, merge base `a1953c2`) and `origin/feature/py32f071-full-support` @ `cc4a815` — read as design references; nothing taken.
- `~/.platformio/platforms/atmelavr/builder/frameworks/arduino.py:95–115` (the real CCFLAGS/LINKFLAGS).
- `avr-gcc -mmcu={atmega328p,atmega328pb,atmega32u4} -dM -E -`; `g++ -dM -E -`.
- `.planning/phases/123-…/check_permitted_claims.py`; `.planning/phases/124-firmware-integration-merge/124-NONREGRESSION.md`.

### Secondary (MEDIUM confidence — project record, cross-checked against the trees)

- `.planning/REQUIREMENTS.md` (Validation Ceiling; VPP-01…03), `.planning/ROADMAP.md` §Phase 125 (lines 2142–2155), `.planning/research/SUMMARY.md` §Phase 125 (line ~271) and its evidence table (lines 238–248), `.planning/STATE.md`, `125-CONTEXT.md`, `firestarter/CLAUDE.md`, `firestarter_app/CLAUDE.md`.

### Tertiary (LOW confidence — noted, not relied on)

- `.planning/graphs/graph.json` — `stale: true`, 720 h old, 577 commits behind, built at `f4150b8` (pre-Phase-124). Queried for status only; **no structural claim in this document derives from it.**

---

## Metadata

**Confidence breakdown:**

- Standard stack: **HIGH** — nothing new is added; every version was measured, not recalled.
- Architecture / the seam's shape: **HIGH** — the full six-leg harness and both new files were prototyped, compiled and run; all outcomes quoted as observed.
- The C-1 blocking finding: **HIGH** — reproduced from a clean `.pio`, and both resolutions independently measured green.
- Criterion 4 figures: **HIGH for AVR** (three cold builds, exact baseline match, corroborated by `.o` presence and `avr-nm`); **NOT MEASURED for ARM** and not measurable here.
- Gate behaviour (manifest reverse check, strict comparator, BASE-08 convention, host parity inertness): **HIGH** — each driven to both a green and a red outcome.
- ARM compile success with the seam: **MEDIUM (A1)** — reasoned from dependency-freedom plus a warning-free host compile; discharged only by D-13's CI run URL + head SHA.

**Self-check against `check_permitted_claims.py` — run, not asserted.** This document was scanned with the real gate:

```bash
FIRESTARTER_CLAIMSCAN_TARGETS=".planning/phases/125-vpp-control-seam/125-RESEARCH.md" \
  python3 .planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py
```

The **first** run returned `FAIL: 7 forbidden phrase match(es)` — and every one of the seven was in my own *documentation* of the gate: six in a paragraph that quoted the forbidden phrases in order to claim I had avoided them, and one in the C-16 pattern table's label column, where the label `hardware_validated` is spelled in the source with a hyphen and therefore matches its own regex. That is precisely the interaction the checker's own comment at `:144–153` predicts, and its prescribed remedy — *reword the artifact, never narrow the patterns* — is what was applied: the quoting paragraph was deleted rather than defended, and the label column is now rendered with `_` for `-` (the same self-avoidance technique `test_pinmap_guard_fires.py`'s coverage-6 leg uses).

The phrasings chosen deliberately to stay clear of the eight labels, listed by label rather than by phrase: for `hardware_validated` — "no hardware evidence exists"; for `bench_validated` — "an AVR read path with bench history"; for `closed_loop_vpp` — "PR #47 does contain a py32 DAC implementation"; for `pin_map_correct` — "the pin map is provisional"; for `runs_on_py32` — "the ARM target compiles"; for `works_end_to_end` and `flashed_a_py32` — no install-outcome claim is made anywhere in this document; for `silicon_verified` — the standing caveat carries the point instead. The canonical caveat **"no PY32F071 hardware exists"** appears verbatim in this document's header, satisfying `REQUIRED_CAVEAT_PATTERN`.

Note C-16: this gate's default target set is only Phase 130's four artifacts, so this file is scanned only when named via `FIRESTARTER_CLAIMSCAN_TARGETS`, as above. **The lesson generalises to Phase 125's own closing artifact: any section of `125-NONREGRESSION.md` that quotes the ceiling's forbidden phrases in order to disclaim them will fail this gate.** Reference them by label, never by phrase.

**Research date:** 2026-07-31
**Valid until:** ~7 days, or until any of these moves — `firestarter` `HEAD` (`a145081`), `platform/py32f071/CMakeLists.txt`, `platformio.ini`, `scripts/baseline/size_baseline.json`, or the three pinned blob SHAs. Re-measure Criterion 4 on the real files regardless of this date (A4).
