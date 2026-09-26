# Phase 125: VPP Control Seam - Context

**Gathered:** 2026-07-31
**Status:** Ready for planning — **partially superseded by research, see below**

> **⚠ CORRECTED BY RESEARCH (2026-07-31). Read `125-RESEARCH.md`
> §"Corrections to `125-CONTEXT.md` and the upstream record" (C-1…C-18) BEFORE acting on
> anything here.** Research was run despite the ROADMAP flagging Phase 125 `research-skip`,
> and it measured — not reasoned — several claims in this file to be wrong. The decision
> **ids** D-01…D-16 stay stable and binding; several of their **mechanisms** do not. Where
> this file and RESEARCH.md disagree, **RESEARCH.md wins**.
>
> **C-1 — BLOCKING, and resolved by the operator on 2026-07-31 → Option A.**
> D-06's `#error` arm plus the one `#include "rurp_vpp.h"` line in `include/rurp_shield.h`
> takes `pio test -e native` from **141 cases / 141 succeeded to 17 suites / 0 succeeded**
> (all 17 ERRORED) — the same A-4 signature this milestone already paid for once with
> `agent/portability-macros`. `rurp_shield.h` has 46 include sites, 14 of them native
> `host_stubs.cpp` files; host `g++` defines no `__AVR__` (measured: 0 matches) and no native
> env declares `RURP_HAS_VPP_DAC` (measured: 0), so D-06's `#else` arm is reached in every
> native TU.
>
> **Operator decision (Option A): `include/rurp_shield.h` is NOT touched by this phase.**
> Both new files land; there is no `#include` line anywhere. Measured green: native
> 141/141 at 17 suites, and 0 B flash / 0 B RAM delta on all three AVR targets. Grounds, all
> checked by research: D-11 already names the macro's only consumers as the `#if` in
> `src/rurp_vpp.cpp` and the `#if !defined` in `include/rurp_vpp.h`; `src/rurp_vpp.cpp` is
> still compiled by all three AVR envs (no AVR env has a `build_src_filter`) and by the ARM
> target (D-12 names it), so D-07's CMake declaration stays load-bearing; `rurp_shield.h` is
> not in Criterion 3's pinned set and no ROADMAP success criterion mentions the `#include` —
> it appears only in prose. Option B (keep the `#include`, add `-D RURP_HAS_VPP_DAC=0` to two
> native envs) was also measured green but was **declined**: it contradicts D-06's own stated
> reason for choosing `__AVR__` and puts a build-flag edit inside the phase whose premise is
> that nothing else moved.
>
> **Therefore the following statements in this file are now WRONG and must not be planned
> against:** `<domain>`'s *"one `#include` line in `include/rurp_shield.h`"*;
> `<canonical_refs>`'s *"`include/rurp_shield.h` — the single `#include` line"*;
> `<code_context>` §Integration Points' *"gains the one `#include`"*; and `<specifics>`'s
> framing of it as the only production-visible edit to an existing shared header. The phase's
> production-visible change is: **two new files, plus two lines in
> `platform/py32f071/CMakeLists.txt`** (one source-list entry, one `RURP_HAS_VPP_DAC=0`
> define). `include/rurp_shield.h` and `platformio.ini` are both untouched.
>
> **Other load-bearing mechanism corrections (ids unchanged, mechanisms replaced):**
>
> - **C-4 → D-03/D-06:** D-06's quoted block does **not** satisfy D-03 — measured,
>   `-DRURP_HAS_VPP_DAC=1` exits **0**. A *second*, separately-authored `#error` is required
>   **in `src/rurp_vpp.cpp`**, and D-03's forced-DAC leg must therefore compile the `.cpp`,
>   not merely include the header. Per C-17 the message must be scoped to *this branch*
>   (`origin/feature/py32f071-full-support`, PR #47 closed, really does implement a py32 VPP
>   DAC with `RURP_HAS_VPP_DAC=1`), never phrased as a universal claim.
> - **C-2 → Criterion 1 / Claude's-discretion default:** the ROADMAP's named mechanism
>   (`git log --all --grep`) is wrong twice — `--grep` searches messages (0 rows today,
>   forever) and any `--all`-scoped reachability test finds all ten PR #45 SHAs because the
>   ref is fetched locally. Use `git cat-file -e <sha>^{commit}` + `git merge-base
>   --is-ancestor <sha> HEAD`, scoped to HEAD, with explicit exit-128 handling and an
>   `n_checked == 10` non-vacuity assertion.
> - **C-11 → Criterion 1 shape:** implement it as **`tests/test_pr45_non_ancestry.py`**, not
>   `scripts/check_*.py`. Proven by planting one: a new `scripts/check_*.py` costs four
>   artifacts plus `FLOOR 5→6` and `FIXTURE_FLOOR 10→11` (2 failed → remove → 7 passed).
> - **C-6 → D-04:** the drift leg's anchor as written **fails on arrival** —
>   `ARDUINO_AVR_UNO`/`_LEONARDO`/`_ATmega328PB` are supplied by the framework and board JSON
>   and appear **nowhere** in `platformio.ini`. Honest anchors: the `[env:<name>]` header plus
>   `board = <uno|ATmega328PB|leonardo>` for AVR, and `RURP_PLATFORM_PY32F071=1` +
>   `RURP_BOARD_NAME="py32f071"` for ARM. Also: the four board legs prove **one AVR fact plus
>   one ARM declaration**, not four independent per-board facts — say so in the artifact.
> - **C-5 → D-11/D-15/D-16:** Criterion 4 is now **measured**, non-vacuously: **0 B flash and
>   0 B RAM on all three AVR targets**, with the `.o` present in all three build dirs and
>   `avr-nm` finding zero of the three seam symbols in the ELF (while finding five unrelated
>   pre-existing `vpp` symbols, so the grep is not matching nothing by accident). The real
>   flags include **`-flto`**, which no upstream document names — the seam's `.o` is an LTO
>   slim object, so LTO and `--gc-sections` both contribute. `check_size_baseline.py` exits 0
>   against the seam tree, so D-16's re-baseline stays a documented contingency and must
>   **not** be pre-emptively performed.
> - **C-7 → D-01:** the new harness runs in **zero CI legs on this branch** — `pytest tests/`
>   appears only in `build.yml` (push/PR to `main`) and `beta-build.yml` (push to `beta`);
>   `py32f071.yml` has no pytest step. Criterion 2 is discharged by an in-phase **local**
>   `pytest` run whose verbatim output lands in `125-NONREGRESSION.md`. Do not claim CI
>   coverage this branch does not have. D-13's push safety was independently re-read on the
>   current tree and **stands**.
> - **C-9 → the `rurp_shield.h` discretion item:** moot under Option A, but recorded as a
>   checked fact — `test_revision_constants_parity.py` parses **only** `include/firestarter.h`
>   (`:145`), `_extract_defines` (`:288`) follows no `#include`, and a bare `#include` matches
>   none of its three line classifiers. Full host suite: 1158 passed, 0 failed, 0 skipped.
> - **C-15 → Criterion 3:** `git status --porcelain` empty is a **post-commit corroboration
>   only** — during the phase the new files make it non-empty by design. The primary proof is
>   the blob-SHA re-hash. Any porcelain row must name the **firmware** repo explicitly;
>   `firestarter_app`'s porcelain is legitimately non-empty right now.
> - **C-16:** `check_permitted_claims.py`'s `_DEFAULT_TARGETS` are four **Phase-130** files —
>   it does not scan Phase 125's artifacts unless named via `FIRESTARTER_CLAIMSCAN_TARGETS`.
>   The closing plan must pass the target explicitly and include the canonical
>   *"no PY32F071 hardware exists"* caveat verbatim.
> - **C-18 → VPP-01:** the record warns that `05f4a77` smuggles a `CONFIG_VERSION` bump
>   (verified, `VER06`→`VER07`). Research found worse: **`768580f`** adds the
>   `rurp_configuration_t` calibration fields *before* the bump — cherry-picking it alone
>   would change the struct layout while `CONFIG_VERSION` stays literally `"VER06"`, a silent
>   schema change with no migration signal. That is the sentence VPP-01 should cite.
>
> **Verified unchanged:** C-3 (all ten PR #45 SHAs enumerated, none an ancestor of `HEAD`),
> C-8 (`compare_avr()` strict equality, armed, never-vacuous; `size_baseline_base01.json`
> genuinely separate), C-10 (no host scan-path inventory entry needed), C-12
> (`check_cmake_manifest.py`'s reverse check behaves exactly as documented — proven both
> directions), C-13 (`__AVR__` is the right predicate, and `RURP_PLATFORM_AVR` is a trap that
> is never defined during an AVR build), C-14 (the ARM defines block; no `-Werror` anywhere).

<domain>
## Phase Boundary

This phase creates a **two-file firmware capability seam** declaring VPP control as a
*platform property*, and proves that landing it moved nothing else:

1. `include/rurp_vpp.h` and `src/rurp_vpp.cpp` are **new, hand-authored** files (VPP-01) —
   nothing cherry-picked from PR #45 (`feature/common-vpp-calibration`), whose `05f4a77`
   smuggles a `CONFIG_VERSION` bump and whose `9134f2a` reroutes AVR voltage measurement.
2. `rurp_set_vpp_target_mv()` returns `MANUAL_ADJUSTMENT_REQUIRED` on **every** board
   macro-set — Uno, Leonardo, uno328pb, py32f071 — asserted across all four in one run
   (VPP-02).
3. A diff gate proves `src/boards/rurp_common.cpp`, `include/rurp_types.h` and
   `src/rurp_config_utils.cpp` byte-identical and `CONFIG_VERSION` still literally
   `"VER06"`, with the AVR flash delta **measured** rather than assumed (VPP-03).

**The entire production-visible change is:** two new files, one `#include` line in
`include/rurp_shield.h`, one source-list line plus one compile definition in
`platform/py32f071/CMakeLists.txt`.

**Explicitly NOT in this phase:**
- **VPP calibration in any form** — no two-point calibration, no gain/offset, no
  `vpp_gain_ppm` / `vpp_offset_mv` / `vpp_cal_*` fields. Those fields are precisely what
  would force the `CONFIG_VERSION` bump VPP-03 forbids.
- **Any change to AVR voltage measurement** — `rurp_read_voltage_mv()`,
  `rurp_read_voltage_uncalibrated_mv()`, `hw_read_voltage()` and the 16× oversampling from
  PR #45's `9134f2a` are all out.
- **DAC control code** — no closed-loop control, no `rurp_vpp_dac_write` /
  `rurp_vpp_control_enable` / `rurp_vpp_delay_ms`, no `RURP_VPP_DAC_BITS`.
- **Any wire-visible change** — the capability is not reported in the firmware identity or
  config response; no `messages.toml` edit, no host constants-parity churn.
- The flash-persistent config backend (Phase 126), the host DFU installer (Phase 127), the
  release-asset fold (Phase 128), the PCB record (Phase 129), and every push to `beta`,
  tag, release or public comment (Phase 130).

**This phase does not merge toward `beta` and cuts no release.** One push of the firmware
milestone branch to `origin` plus one `workflow_dispatch` is in scope, operator-gated
(D-09 below).

</domain>

<decisions>
## Implementation Decisions

### The four-board proof (VPP-02, Criterion 2)

- **D-01:** The four-board assertion is a **pytest under `firestarter/tests/` that compiles
  `src/rurp_vpp.cpp` with host `g++` four times**, once per board macro-set, links a minimal
  `main` that surfaces the return value, runs each, and asserts
  `MANUAL_ADJUSTMENT_REQUIRED`. One pytest invocation = criterion 2's "one run".
  **Not** a fourth PlatformIO env with namespaced wrapper TUs (rejected: the header is
  `extern "C"`, so four copies in one binary need `#define`-renaming gymnastics, and all
  four "boards" would still share a single native compile). **Not** the hybrid with
  static assertions compiled into the real target builds (rejected: it would put a new
  assertion into all four production builds, whose flash impact this phase would then have
  to measure and defend).
  Direct precedent: `firestarter/tests/test_pinmap_guard_fires.py` (Phase 124 D-14's
  `g++ -E` fire-proof). Note this shape sits **outside** BASE-08's checker convention —
  `tests/test_checker_convention.py` governs `scripts/check_*.py` only, so neither `FLOOR`
  (5) nor `FIXTURE_FLOOR` (10) needs bumping.
- **D-02:** `src/rurp_vpp.cpp` is **dependency-free by construction** — it includes only
  `rurp_vpp.h` (plus `<stdint.h>`). No `rurp_shield.h`, no `<Arduino.h>`, no PY32 HAL, no
  `rurp_get_config()`. PR #45 needed `rurp_shield.h` solely to reach the calibration fields
  in `rurp_configuration_t`, and dropping calibration drops the dependency for free. This
  is what makes D-01's harness need zero stub scaffolding, and it is a **standing
  constraint**: a later phase wanting config or hardware access must add the dependency
  deliberately.
- **D-03:** The harness is proven non-vacuous by a **forced-capability compile leg**: a leg
  compiling with `-DRURP_HAS_VPP_DAC=1` must produce a **non-zero `g++` exit** carrying a
  named `#error` (no board ships a VPP DAC implementation). This proves the capability macro
  is genuinely consulted rather than decorative — the direct antidote to the hollow-guard
  shape Phase 124 D-14 had to restructure. A planted mutated-seam fixture under
  `tests/fixtures/` was offered and **declined** as not worth the hand-maintained drift risk.
- **D-04:** The four board macro-sets are **hardcoded literals in the harness, plus one drift
  leg** asserting each board's defining macro still appears in its real build config
  (`platformio.ini` for the three AVR envs; `target_compile_definitions` in
  `platform/py32f071/CMakeLists.txt` for ARM). Explicitly **not** derived by parsing the
  build files — `tests/scan_paths.py`'s own stated principle ("deliberately explicit, never
  derived") applies, and the two build systems have incompatible define syntaxes, so a
  derived version is two parsers. The drift leg is the safety net that keeps the hardcoding
  honest.

### Where the capability macro gets its value (Criterion 2, anti-hollow)

- **D-05:** **Operator fact, verbatim:** *"No arduino board will have the DAC so it must be
  set to disabled."* This is a **permanent** property of the AVR-class boards, not a
  provisional placeholder — the rail is set by the operator's pot. Record it as permanent
  wherever it is written; do **not** describe AVR manual control as "for now" or
  "pending hardware".
- **D-06:** `rurp_vpp.h` carries **no blanket default**. It resolves `RURP_HAS_VPP_DAC` in
  exactly two ways:

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

  `__AVR__` is **compiler-supplied**, so D-02's dependency-freedom survives — no
  `rurp_platform.h`, no `<Arduino.h>`. All three AVR targets are covered by one stated fact,
  uniformly, and **`platformio.ini` needs no edit**, which keeps the AVR flash delta
  attributable to source alone rather than to moved build flags.
  PR #45's shape (`#ifndef RURP_HAS_VPP_DAC / #define ... 0` unconditionally inside the
  header) was **rejected**: it makes "every board is manual" true because the header says
  so — structurally the same defect as Phase 124's hollow `#error` guard, one phase later.
- **D-07:** **Every non-AVR board must declare `RURP_HAS_VPP_DAC` explicitly**, and for
  py32f071 the declaration lives in the **CMake `target_compile_definitions`
  (`RURP_HAS_VPP_DAC=0`), not in `include/boards/py32f071_rurp_shield.h`.** This is Phase 124
  D-14's lesson applied deliberately: the build system supplies what the header only tests.
  A fifth non-AVR board that forgets fails to compile rather than silently inheriting manual
  control near an unregulated rail.
- **D-08:** The `#error` arm gets its **own harness leg** — a compile with neither `__AVR__`
  nor an explicit `RURP_HAS_VPP_DAC` must fail. So the harness has (at minimum) six legs:
  four board macro-sets, one forced-DAC, one unset-and-non-AVR.

### Seam API surface (VPP-01)

- **D-09:** The seam declares **three functions and nothing else**:
  `rurp_vpp_control_mode()`, `rurp_set_vpp_target_mv(target_mv, tolerance_mv, timeout_ms)`,
  `rurp_disable_vpp_control()`. **Dropped:** PR #45's three DAC hooks
  (`rurp_vpp_dac_write`, `rurp_vpp_control_enable`, `rurp_vpp_delay_ms`), the
  `RURP_VPP_DAC_BITS` macro and its consistency `#error` (unreachable now that
  `RURP_HAS_VPP_DAC=1` is itself an `#error` per D-03), and the whole calibration API
  (`rurp_calibrate_vpp_two_point`, `rurp_reset_vpp_calibration`,
  `rurp_vpp_calibration_valid`, `rurp_apply_vpp_calibration`,
  `rurp_read_voltage_uncalibrated_mv`). Rationale is Phase 124 D-01's rule verbatim:
  a declaration with no implementation and no consumer comes back **with a consumer
  attached**, or not at all.
- **D-10:** Each enum carries **exactly two enumerators**:
  `rurp_vpp_control_mode_t = { RURP_VPP_CONTROL_MANUAL = 0, RURP_VPP_CONTROL_DAC = 1 }` and
  `rurp_vpp_result_t = { RURP_VPP_OK = 0, RURP_VPP_MANUAL_ADJUSTMENT_REQUIRED = 1 }`.
  `RURP_VPP_CONTROL_DAC` and `RURP_VPP_OK` are unreachable today but each earns its place —
  `DAC` names the axis the seam exists to express (a mode enum with one mode expresses
  nothing) and `OK = 0` is the conventional success slot. PR #45's five-value result enum
  (`INVALID_ARGUMENT`, `TIMEOUT`, `OUT_OF_RANGE`) is **out**: all three are producible only
  by the closed-loop control code D-09 cuts, and their numbering would be inherited from a
  PR this phase must take nothing from.
- **D-11:** **Zero production callers this phase.** Nothing under `src/` or `platform/`
  calls the three functions, so `--gc-sections` is expected to drop them entirely. The
  macro's consumers are the `#if` in `src/rurp_vpp.cpp` and the `#if !defined` in
  `include/rurp_vpp.h` (both in `include/`/`src/`, which is where
  `check_orphan_provisional.py` would look were the macro `*_PROVISIONAL`-named — it is not,
  so that gate is not in play). Routing `hw_read_voltage()` through the seam was rejected
  as being `9134f2a` by another route; exposing the mode on the wire was rejected as
  cross-repo churn belonging to a later phase (see Deferred).

### ARM landing and evidence (VPP-01, VPP-03)

- **D-12:** `src/rurp_vpp.cpp` is **named in `FIRESTARTER_COMMON_SOURCES`** in
  `platform/py32f071/CMakeLists.txt`, **not** allow-listed as `PY32_EXCLUDED`. This is not
  optional in either direction: `check_cmake_manifest.py`'s reverse check makes a new
  `src/*.cpp` that is neither named nor reasoned-excluded an **exit-1 violation**, so the
  phase must choose. Naming it is what the phase goal literally says ("the py32 port
  compiles against a final VPP capability shape"), it makes the py32 CMake the natural home
  for D-07's declaration, and D-02's dependency-freedom makes ARM compilation near
  risk-free. A `PY32_EXCLUDED` line was rejected: it would leave the py32 board with no
  declared VPP capability at all (so it would hit D-06's `#error` the moment anything
  includes the header) and hand Phase 126 a second exclusion to unwind.
- **D-13:** Phase 125 obtains **its own ARM CI evidence** — push the firmware milestone
  branch `v1.23-py32f071-integration` to `origin`, `workflow_dispatch` `py32f071.yml`,
  record **run URL + head SHA**. Rationale is the same attributability the 125 → 126
  ordering exists for: if the seam breaks the ARM build, *this* is the phase that learns it.
  Deferring ARM evidence to Phase 126's run was offered and declined.
  **Push safety, re-verified:** `py32f071.yml` fires on `pull_request` + `workflow_dispatch`
  + `push: branches: [beta]` (MERGE-03's addition) and `beta-build.yml` is untouched — so
  pushing the milestone branch cuts no beta prerelease. Confirmed by reading the workflow on
  the current tree, not assumed from Phase 124.
- **D-14:** That push and dispatch is an **outward-facing action requiring an explicit
  operator gate at execute time**, structurally separated from any autonomous flag.
  `--auto`/`--chain` auto-approve human-verify checkpoints regardless of
  `autonomous: false`. Follow Phase 124 Plan 124-11's shape exactly: **no task runs
  `git push` or `gh workflow run`** — the plan prints the commands and stops.
- **D-15:** Criterion 4 is discharged by **recording** the measured flash **and** RAM
  figures for all three AVR targets in the phase's evidence artifact. **No new gate, no
  tolerance band, no new `--policy` flag** — operator decision, taken against the
  recommendation. The planner must **not** "complete" this by adding a comparator leg of its
  own.
- **D-16:** `scripts/check_size_baseline.py`'s default `compare_avr()` is **strict equality
  and already armed** in the existing sweep, so a nonzero delta goes red whether or not this
  phase gates on it. If it fires: **measure, record the delta and its cause in the evidence
  artifact, then re-baseline `size_baseline.json` in its own commit whose message states why
  the bytes are legitimate** — the shape Plan 124-10 used. Never widen a tolerance, never
  re-baseline silently. Note `size_baseline_base01.json` (Phase 124's frozen MERGE-05
  reference) is a **separate** file and is not touched by any re-baseline here.

### Claude's Discretion

- **PR #45 non-ancestry proof (Criterion 1).** House-style default: a **scripted check
  producing an exit code**, not a prose assertion — assert each of PR #45's commit SHAs
  (`05f4a77`, `9134f2a`, `b964ee6`, `d285b83`, `71278d0`, `a47228d`, and the earlier
  `768580f`, `86f351a`, `fc0b2c7`, `04fd9b3`) is **not** an ancestor of the integration
  branch, with a never-vacuous guard so an empty SHA list cannot pass. Whether to *also*
  assert content divergence from PR #45's blobs is Claude's call; D-09/D-10 already
  guarantee substantial divergence.
- **Evidence artifact shape.** Default: a **`125-NONREGRESSION.md`** in the same
  command / expected / observed row shape as `123-NONREGRESSION.md` and
  `124-NONREGRESSION.md`, re-executed in the closing plan rather than copied from earlier
  plans' SUMMARY files. This is where D-15's figures and D-13's run URL + SHA land.
- **How the three untouched files are pinned (Criterion 3).** Default: **literal blob SHAs
  recorded pre-phase and re-hashed after**, plus `git status --porcelain` empty. Explicitly
  **never** a path-scoped `git diff`, which passes vacuously on a wrong path. Note
  `124-VERIFICATION.md` carries a live informational finding on exactly this class of
  mistake (a `git diff --stat | grep -v memory.cpp` pipeline whose trailer survived the
  grep) — do not reproduce that shape.
- Plan/wave decomposition and commit granularity, subject to D-14's forced ordering (the
  push/dispatch task is last and gated).
- Exact harness filename, `main`-shim mechanics, and how the return value crosses the
  process boundary (exit code vs. stdout).
- Where the one `#include "rurp_vpp.h"` line sits in `include/rurp_shield.h`.
  **Verify, do not assume:** `firestarter_app/tests/test_revision_constants_parity.py`
  references `rurp_shield.h`, and its `_extract_defines` / `_find_header_guard_line_indices`
  logic tracks preprocessor nesting. Phase 124's correction C-18 documents a near-miss of
  exactly this kind. A plain `#include` should be inert, but check it.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone contract (read first)

- `.planning/REQUIREMENTS.md` — VPP-01, VPP-02, VPP-03 verbatim (lines 54–56); §"Validation
  Ceiling" (line 14) is the forbidden-claim list every artifact this phase writes is scanned
  against. Note *"closed-loop VPP works"* and unqualified *"bench-validated"* are explicitly
  forbidden — this phase must never imply VPP control does anything.
- `.planning/ROADMAP.md` §"Phase 125: VPP Control Seam" (from line 2106) — the four success
  criteria; §"v1.23 — PY32F071 Integration" (from line 1957) for the non-regression
  invariant, the **125 → 126** ordering rationale (both touch
  `src/rurp_config_utils.cpp`; landing the seam first with a gate proving that file
  untouched keeps the "no `CONFIG_VERSION` bump" claim attributable), and the
  structural-verification discipline.
- `.planning/PROJECT.md` §"Current Milestone: v1.23 PY32F071 Integration" (from line 36) —
  the research corrections and the software-only validation ceiling.
- `.planning/research/SUMMARY.md` §"Phase 125 — VPP control seam" (line 271) — the ~40-line
  header / ~15-line `.cpp` sizing, the "cherry-pick nothing from PR #45" rationale naming
  `05f4a77` and `9134f2a` specifically, and the "0 B expected with `--gc-sections`/no
  callers — measured, not asserted" expectation. Also line 242: *"No VPP claim without a
  DMM; there is no DMM path without a PCB. State 'not measured'."*

### Phase 123/124 output this phase consumes

- `.planning/phases/123-non-regression-baselines-gate-hardening/123-CONTEXT.md` — D-01…D-16
  still binding; the `<specifics>` tie-breaker (*prefer the shape that produces an exit
  code*; *prefer the shape that cannot be silently forgotten*) governs here too, **except**
  where D-15 above deliberately overrides it for the flash figures.
- `.planning/phases/124-firmware-integration-merge/124-CONTEXT.md` — D-14 (a guard that
  defines what it tests is structurally dead; the build system must supply it) is the direct
  ancestor of D-06/D-07. D-01 (a declaration comes back with a consumer attached) is the
  direct ancestor of D-09. D-02's uniformity invariant (*the same switch means the same
  thing on every platform*) shapes D-06. D-08/D-09's push-gate shape is reused by D-13/D-14.
- `.planning/phases/124-firmware-integration-merge/124-NONREGRESSION.md` — the row-shape
  template for `125-NONREGRESSION.md`, and §6 for the "never prove untouched with a
  path-scoped diff" precedent.
- `.planning/phases/124-firmware-integration-merge/124-VERIFICATION.md` — carries the live
  informational finding about a `git diff --stat | grep` pipeline reported as "(empty)" when
  a trailer survived the grep. Read before writing any "untouched" proof.
- `firestarter/scripts/baseline/size_baseline.json` — the **post-124 live baseline** D-15/D-16
  measure against (re-baselined by Plan 124-10). Read via the `FIRESTARTER_SIZE_BASELINE`
  env seam; never re-embed the numbers.
- `firestarter/scripts/baseline/size_baseline_base01.json` — Phase 124's **frozen** MERGE-05
  reference. Not this phase's comparison point and **not** to be re-baselined.
- `firestarter/scripts/check_size_baseline.py` — default `compare_avr()` is strict equality;
  already armed (D-16).
- `firestarter/scripts/check_cmake_manifest.py` — **read the module docstring in full.** Its
  reverse check is what makes D-12 non-optional, and it documents the mandatory
  `# PY32_EXCLUDED: <path> -- <reason>` format and the 0/1/2 exit taxonomy.
- `firestarter/tests/test_checker_convention.py` — BASE-08 meta-test, `FLOOR = 5` /
  `FIXTURE_FLOOR = 10`. Scoped to `scripts/check_*.py`, so D-01's pytest harness does
  **not** require a bump. Confirm before assuming otherwise.
- `firestarter/tests/test_pinmap_guard_fires.py` — the in-tree precedent D-01's harness
  follows (a pytest that drives a host compiler to prove a compile-time property).

### PR #45 — read as a design reference, take nothing

- `origin/feature/common-vpp-calibration` @ `a47228d` — ten commits. `include/rurp_vpp.h`
  (70 lines) and `src/rurp_vpp.cpp` (176 lines) are the shape this phase deliberately
  narrows. **Forbidden as ancestors:** `05f4a77` (adds the calibration API *and* bumps
  `CONFIG_VERSION`, deleting Phase-33/34 provenance comments), `9134f2a` (reroutes AVR
  voltage measurement, adds 16× oversampling), plus `768580f`, `86f351a`, `fc0b2c7`,
  `04fd9b3`, `b964ee6`, `d285b83`, `71278d0`, `a47228d`.
  The branch touches six files: `include/rurp_shield.h` (−132/+…, a large rewrite),
  `include/rurp_types.h` (+12, the calibration fields), `include/rurp_vpp.h`,
  `src/boards/rurp_common.cpp`, `src/rurp_config_utils.cpp`, `src/rurp_vpp.cpp` — **three of
  those six are the files VPP-03 requires byte-identical.** That overlap is the whole reason
  cherry-picking is forbidden.

### Firmware sources this phase creates, edits or measures

- `firestarter/include/rurp_vpp.h` — NEW (D-06, D-09, D-10).
- `firestarter/src/rurp_vpp.cpp` — NEW (D-02, D-03, D-11).
- `firestarter/include/rurp_shield.h` — the single `#include` line. `CONFIG_VERSION "VER06"`
  lives at line 46 and must stay literally that.
- `firestarter/platform/py32f071/CMakeLists.txt` — `FIRESTARTER_COMMON_SOURCES` (lines
  35–52) gains the seam; `target_compile_definitions` gains `RURP_HAS_VPP_DAC=0` (D-07,
  D-12). The five existing `# PY32_EXCLUDED:` lines are at 30–34.
- `firestarter/src/boards/rurp_common.cpp`, `firestarter/include/rurp_types.h`,
  `firestarter/src/rurp_config_utils.cpp` — the three files VPP-03 pins byte-identical.
- `firestarter/platformio.ini` — the three AVR envs (31–68) and the three native envs.
  **No edit expected** under D-06. Both pinned native envs are frozen at **141 cases /
  17 suites**, and their `build_src_filter`
  (`+<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>`)
  does **not** compile `src/rurp_vpp.cpp` — so no native test count moves.
- `firestarter/.github/workflows/py32f071.yml` — the workflow D-13 dispatches; re-read its
  trigger block before pushing.

### Host-repo gates that scan firmware source text

- `firestarter_app/tests/test_revision_constants_parity.py` — references `rurp_shield.h`
  (the `REVISION_*` enum) and `rurp_pinout.h`; `_extract_defines` tracks preprocessor
  nesting. Verify the new `#include` line is inert here rather than assuming it.
- `firestarter_app/tests/scan_paths.py`, `firestarter_app/tests/fw_presence.py` — the
  central cross-repo scan-path inventory. `include/rurp_vpp.h` is scanned by no host gate,
  so **no inventory entry is expected** — state that as a checked fact, not an omission.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`firestarter/tests/test_pinmap_guard_fires.py`** — Phase 124 D-14's fire-proof: a pytest
  that drives a host compiler to prove a compile-time property no PlatformIO env can reach.
  D-01's harness is the same pattern with a compile-and-*run* step added.
- **`platform/py32f071/CMakeLists.txt`'s existing `PY32_EXCLUDED` block and
  `target_compile_definitions`** — both the reverse-check pressure (D-12) and the
  build-supplies-the-macro home (D-07) already exist; this phase adds lines, invents nothing.
- **`scripts/check_size_baseline.py` + the post-124 `size_baseline.json`** — the measurement
  machinery for D-15 exists and is armed; the phase reads figures, it does not build a
  comparator.
- **`123-NONREGRESSION.md` / `124-NONREGRESSION.md`** — the evidence-artifact template,
  reused verbatim in structure.
- **`include/boards/py32f071_rurp_shield.h`'s provisional-flag bridge block** (Phase 124
  Plan 08) — the in-tree example of a macro made deliberately load-bearing with its
  reasoning written next to it. D-06's `__AVR__` block should read the same way.

### Established Patterns

- **A guard that supplies the answer it checks is dead.** Phase 124 found
  `#define ...CONFIGURED 1` two lines above `#if !...CONFIGURED → #error` and had to hoist
  the test away from the definition. D-06/D-07 are that lesson applied before the fact.
- **A declaration with no implementation and no consumer does not land.** Phase 124 D-01
  deleted `write_checksums.cmake` rather than inventing a consumer. D-09 applies it to the
  DAC hooks.
- **Assert counts, never "tests pass."** 141 cases / 17 suites on both pinned native envs.
  This phase must not move either number — and by D-01's design, it does not touch them.
- **Never prove "untouched" with a path-scoped `git diff`.** Blob SHAs or empty
  `git status --porcelain`.
- **Cross-repo gates scan firmware source *text*.** A firmware rename silently broke a host
  gate four times in Phase 117. This phase adds a file and one `#include` — small surface,
  but the check is cheap.
- **`firestarter/tests/` is PIO-invisible; `firestarter/test/` is globbed into builds.**
  D-01's harness must live in `tests/`.
- **`include/messages.h` is codegen-generated** from the meta repo's canonical
  `messages.toml`. D-11's refusal to expose the capability on the wire is partly the refusal
  to pay that cost here.

### Integration Points

- **`include/rurp_shield.h`** gains the one `#include` — the only production-visible edit to
  an existing shared header.
- **Phase 126** touches `src/rurp_config_utils.cpp`, which this phase pins byte-identical;
  that pin is what makes any Phase-126 regression attributable. Phase 126 also revisits the
  `src/rurp_config_utils.cpp` `PY32_EXCLUDED` entry — this phase adds a *source-list* line,
  not another exclusion, so it does not enlarge that debt.
- **`platform/py32f071/CMakeLists.txt`** is edited by this phase and again by Phase 126
  (config backend) and Phase 128 (release fold). Keep this phase's diff to the two lines.
- **All three repos are on their milestone branches** — firmware and host on
  `v1.23-py32f071-integration`, meta on `gsd/v1.23-py32f071-integration`. Firmware `origin`
  is at `a145081`. Verify with `git` at execute time regardless.
- **The two gitignored py32 worktrees** (`firestarter_py32_ci/`, `firestarter_app_py32/`) are
  checkouts of the same repos, never gitlinked. Do not write into them.

</code_context>

<specifics>
## Specific Ideas

- The operator's one substantive intervention replaced a three-option question with a
  **fact**: *"No arduino board will have the DAC so it must be set to disabled, then you
  decide how to solve it."* Two things follow. First, AVR manual control is **permanent**,
  and every artifact this phase writes should say so rather than hedging it as provisional —
  hedging would misrepresent the hardware. Second, where a further choice arises that this
  CONTEXT does not settle, and one option makes the manual-only reality *stated* while
  another leaves it *implied*, choose stated.
- On the flash figures the operator deliberately chose **record-without-gating** over the
  project's standing exit-code preference (D-15). That is a real, intentional exception —
  the planner should implement it as chosen and not quietly restore the gate. The pressure
  is already covered anyway: the pre-existing strict comparator is armed (D-16).
- Phase 124's `<specifics>` observation still holds and applies twice here: where one option
  makes a target special-cased and another makes the mechanism uniform, choose uniform — and
  pay for it with a measurement, not an assurance. D-06 (one `__AVR__` fact for three
  targets) and D-07 (every non-AVR board declares) are both that choice.
- Nine of the sixteen decisions above are Claude's-discretion defaults on areas the operator
  did not elect to discuss in detail. They are recorded as **locked** so downstream agents do
  not re-ask. The two most consequential are **D-12** (naming the seam in the ARM manifest,
  which is what pulls in D-13's push) and **D-13** (taking an ARM CI run in this phase rather
  than riding Phase 126's) — if either should be reversed, before planning is the cheap moment.

</specifics>

<deferred>
## Deferred Ideas

- **Closed-loop VPP control / DAC feedback** — PR #45's `rurp_vpp_dac_write`,
  `rurp_vpp_control_enable`, `rurp_vpp_delay_ms`, `RURP_VPP_DAC_BITS`, and the whole
  `#if RURP_HAS_VPP_DAC` control loop. Returns **with an implementation and a board
  attached**, not as declarations. Blocked on hardware that does not exist; D-05 says no
  Arduino-class board will ever qualify.
- **VPP two-point calibration** (`vpp_gain_ppm`, `vpp_offset_mv`, four `vpp_cal_*` fields,
  `rurp_calibrate_vpp_two_point`, `rurp_reset_vpp_calibration`,
  `rurp_vpp_calibration_valid`, `rurp_apply_vpp_calibration`) — requires new
  `rurp_configuration_t` fields, i.e. the `CONFIG_VERSION` bump VPP-03 forbids. The
  ROADMAP's queued **v1.26** slot is where the VREFINT + two-point calibration model is
  designed once for AVR and extended cross-platform; that is the natural carrier, and PR #45
  `05f4a77` is the prior art to read there.
- **AVR voltage-measurement rework** — PR #45 `9134f2a`'s reroute plus 16× oversampling.
  Touches a bench-validated AVR read path; needs its own phase and its own evidence.
- **Exposing VPP control mode on the wire** — reporting the capability in the firmware
  identity or config response so the host can tell a self-regulating board from a
  pot-adjusted one. Genuinely useful, but wire-visible → `messages.toml` + codegen + host
  constants parity, in the phase whose premise is that nothing else moved. Revisit when a
  host consumer actually exists.
- **Compile-time manual-control assertions in the real target builds** — the rejected third
  option of D-01. Would prove the per-board claim where the board actually exists rather than
  in a native simulation. Cheap to add later; costs a new assertion in all four production
  builds plus its flash measurement.
- **A planted mutated-seam fixture for the harness** — declined under D-03 in favour of the
  forced-DAC compile leg. Revisit if the runtime assertion ever grows beyond a single
  equality check.

### Reviewed Todos (not folded)

- **`2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md`**
  (`resolves_phase: 84`, matched 0.6) — the only genuinely VPP-related pending todo, and
  reviewed-not-folded for the second time (Phase 124 did the same). Its claim is that the
  firmware measures the VPP rail and refuses or warns during `read` / `blank-check`, which
  need no VPP; the fix is a behaviour change to `hw_read_voltage` plus the host read path.
  That is the *measurement gate*, not the *control capability seam* — and touching it would
  be D-11's rejected `hw_read_voltage` reroute wearing a different hat. Stays in the backlog.
- **`correct-v128-py32-roadmap-prior-art.md`** (0.6) — the ROADMAP slot renumber and stale
  prior-art correction are **Phase 130's** explicit scope (ROADMAP line 2195). Not folded.
- **`avrdude-mcu-detection-fallback.md`**, **`cobs-decoder-framelevel-deadline-wr01.md`**,
  **`fold-response-code-into-log-macro.md`**, **`photograph-modified-rev-0.md`**,
  **`prove-pio-dev-flag-fails-closed.md`** (all 0.6) — keyword matches on
  "firmware"/"phase"/"status" only; none intersects this phase's scope.

</deferred>

---

*Phase: 125-vpp-control-seam*
*Context gathered: 2026-07-31*
