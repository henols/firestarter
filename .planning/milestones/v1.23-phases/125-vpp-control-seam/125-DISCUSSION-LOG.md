# Phase 125: VPP Control Seam - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-31
**Phase:** 125-vpp-control-seam
**Areas discussed:** Four-board proof mechanics, Capability-macro declaration site, Seam API surface, ARM landing of `rurp_vpp.cpp`

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Four-board proof mechanics | One parametrized native run across four board macro-sets vs. a `.cpp` compiled once per PIO env, with both pinned envs frozen at 141/17 | ✓ |
| Capability-macro declaration site | PR #45's silent `#define RURP_HAS_VPP_DAC 0` inside the header is the hollow-guard shape Phase 124 just fixed | ✓ |
| Seam API surface | 3 functions vs. PR #45's 10; DAC hooks and `RURP_VPP_DAC_BITS`; enum breadth | ✓ |
| ARM landing of `rurp_vpp.cpp` | The CMake manifest reverse-check forces name-it-or-exclude-it; naming it implies ARM build evidence | ✓ |

**User's choice:** All four.

---

## Four-board proof mechanics

### Q1 — How should the four board macro-sets be compiled so one run can assert `MANUAL_ADJUSTMENT_REQUIRED` on all four?

| Option | Description | Selected |
|--------|-------------|----------|
| pytest + g++ harness, 4 compiles | A pytest under `firestarter/tests/` compiles the seam four times with `g++`, one per board macro-set, runs each, asserts MANUAL. Descendant of Phase 124 D-14's `g++ -E` fire-proof. Each board is a genuinely separate compile. No new PIO env, no ODR gymnastics, zero risk to 141/17. Cost: criterion 2's "native test" becomes "native compile-and-run, pytest-driven" | ✓ |
| 4th PIO env + namespaced wrapper TUs | New `[env:native_vpp]` with four test-side wrappers `#define`-ing a board macro-set and including the seam under a renamed symbol; one parametrized Unity test walks four function pointers. Exact mirror of `native_pinmap_provisional`. Cost: the header is `extern "C"`, so four copies in one binary need `#define`-renaming gymnastics — and all four still share one native compile | |
| Hybrid: 4× runtime + compile-time assert in real builds | Either runtime mechanism plus a static assertion compiled into each real target build. Strongest — the per-board claim proven where the board exists. Cost: most work, and a new assertion in all four production builds whose flash impact this phase must then measure | |

**User's choice:** pytest + g++ harness, 4 compiles.
**Notes:** Noted that this shape sits outside BASE-08's checker convention — `tests/test_checker_convention.py` governs `scripts/check_*.py` only, so neither `FLOOR` (5) nor `FIXTURE_FLOOR` (10) needs bumping.

### Q2 — Should `src/rurp_vpp.cpp` be deliberately dependency-free, so the harness needs zero stubs?

| Option | Description | Selected |
|--------|-------------|----------|
| Dependency-free by construction | Includes only `rurp_vpp.h` (+ stdint). PR #45 needed `rurp_shield.h` solely to reach the calibration fields VPP-03 forbids, so dropping calibration drops the dependency for free. Any future phase wanting config access must consciously add it | ✓ |
| Include `rurp_shield.h` like PR #45 | Positions the seam for later hardware/config access. Cost: the harness must stub every `rurp_*` symbol pulled in, and on py32 `rurp_shield.h` reaches `py32f0xx_hal.h` — the exact wall Phase 124 D-14 hit and solved by hoisting a dependency-free fragment | |

**User's choice:** Dependency-free by construction.

### Q3 — How does the harness prove it can actually fail?

| Option | Description | Selected |
|--------|-------------|----------|
| Forced `RURP_HAS_VPP_DAC=1` must fail | A fifth leg compiles with the capability forced on and asserts a non-zero `g++` exit carrying a named `#error`. Proves the macro is genuinely consulted rather than decorative — the antidote to the hollow-guard shape. Costs one `#error` line. Does not prove the runtime assertion can fail | ✓ |
| Planted mutated-seam fixture | A deliberately-wrong copy under `tests/fixtures/`; one leg asserts the runtime assertion fails against it. Phase 123's house style verbatim (10 planted fixtures). Cost: a fixture kept in sync by hand | |
| Both legs | The forced-DAC compile proves the macro is load-bearing; the planted fixture proves the runtime assertion is. Neither subsumes the other. Cost: two mechanisms plus a fixture to maintain | |

**User's choice:** Forced `RURP_HAS_VPP_DAC=1` must fail.

### Q4 — Where does the harness get each board's macro set from?

| Option | Description | Selected |
|--------|-------------|----------|
| Hardcoded list + a drift test | Four literals, plus one leg asserting each board's defining macro still appears in its real build config (`platformio.ini` for AVR, py32 CMake defines for ARM). Mirrors `scan_paths.py`'s stated principle — "deliberately explicit, never derived" — with a resolution test as the safety net | ✓ |
| Derived by parsing the build config | Cannot drift by construction. Cost: `scan_paths.py`'s docstring argues against exactly this, and the two build systems have incompatible define syntaxes, so the parser is two parsers | |
| Hardcoded, no drift test | Cheapest; the macro names are stable Arduino/port identifiers this project does not invent. Cost: a rename leaves a green test covering a board that no longer exists | |

**User's choice:** Hardcoded list + a drift test.

---

## Capability-macro declaration site

### Q1 — Where does `RURP_HAS_VPP_DAC` get its value?

| Option | Description | Selected |
|--------|-------------|----------|
| Every board must declare it; undefined is an `#error` | No default in the header. Each of the four supplies `0` explicitly; a fifth board or a botched build config fails to compile rather than silently inheriting manual. Cost: touches build config for all four targets | |
| Silent default 0 in the header, as PR #45 wrote it | Self-contained, zero build-config edits, trivially attributable flash delta. Cost: it passes because nothing contradicts it — the hollow-guard shape Phase 124 just paid to fix | |
| Default 0, plus a gate that all four are known boards | No build-config edits, but an unrecognised board still fails. Cost: couples the seam to board-identity macros it otherwise wouldn't reference | |

**User's choice:** *Other (free text)* — **"No arduino board will have the DAC so it must be set to dissabled, then you decide how to solve it"**

**Notes:** This is a stronger fact than any option offered: on AVR the DAC is **permanently** absent, not absent-for-now, so "manual" on those three boards is not a placeholder to be revisited. Resolved (with the delegated decision) as:

- `rurp_vpp.h` carries no blanket default. `#if !defined(RURP_HAS_VPP_DAC)` → `#if defined(__AVR__)` yields `0` with the permanence stated in a comment; the `#else` arm is a hard `#error`.
- `__AVR__` is compiler-supplied, so dependency-freedom (Q2 above) survives and `platformio.ini` needs no edit — keeping the AVR flash delta attributable to source alone.
- Every non-AVR board must declare explicitly; py32f071 does so in the CMake `target_compile_definitions`, **not** in `py32f071_rurp_shield.h` — Phase 124 D-14's lesson applied on purpose (the build system supplies what the header only tests).
- The `#error` arm gets its own harness leg, bringing the harness to six legs minimum.

---

## Seam API surface

### Q1 — How much of the DAC-side API should the seam declare, given no board will implement it?

| Option | Description | Selected |
|--------|-------------|----------|
| 3 functions, no DAC hooks, no `DAC_BITS` | Only `rurp_vpp_control_mode()`, `rurp_set_vpp_target_mv()`, `rurp_disable_vpp_control()`. `RURP_VPP_DAC_BITS`'s consistency `#error` is unreachable now that `RURP_HAS_VPP_DAC=1` is itself an `#error`. Whoever builds a DAC board adds the hooks with an implementation attached — Phase 124 D-01's rule for `write_checksums.cmake` | ✓ |
| 3 functions + DAC hooks declared under `#if` | A future DAC board only implements rather than redesigns. Cost: with forced-DAC now a hard `#error`, that block is unreachable by construction — declarations that cannot be compiled, let alone tested | |
| Full PR #45 signature set, manual-only bodies | Header stable if calibration returns. Cost: the calibration functions cannot be declared honestly without the `rurp_configuration_t` fields, and adding those is the `CONFIG_VERSION` bump VPP-03 forbids — it reopens `05f4a77` | |

**User's choice:** 3 functions, no DAC hooks, no `DAC_BITS`.

### Q2 — How wide should the two enums be?

| Option | Description | Selected |
|--------|-------------|----------|
| Two values each — name the axis, nothing more | `{MANUAL=0, DAC=1}` and `{OK=0, MANUAL_ADJUSTMENT_REQUIRED=1}`. `DAC` and `OK` are unreachable today but each earns its place — `DAC` names the axis the seam exists to express, `OK=0` is the conventional success slot | ✓ |
| Only reachable values | Zero dead enumerators. Cost: one-value enums read strangely, a later `OK=0` renumbers `MANUAL_ADJUSTMENT_REQUIRED`, and the mode function can only ever return one thing | |
| PR #45's five-value result enum | Fixes the error vocabulary once. Cost: three of five are producible only by the closed-loop code just cut, and their numbering would be inherited from a PR this phase must take nothing from | |

**User's choice:** Two values each.

### Q3 — Should anything in the firmware actually call the seam this phase?

| Option | Description | Selected |
|--------|-------------|----------|
| Zero production callers this phase | Nothing in `src/` or `platform/` calls it; `--gc-sections` should drop it, which is why criterion 4 expects ~0 B. Keeps the phase's only production-visible change one `#include` line | ✓ |
| Route `hw_read_voltage` through it | Gives the seam a real caller. Cost: this is `9134f2a` by another route — the same behaviour change to a bench-validated AVR read path, in the phase whose premise is that AVR is untouched | |
| Expose the capability on the wire | Useful eventually. Cost: wire-visible → host constants parity → cross-repo churn; Phases 127/128 own the host side | |

**User's choice:** Zero production callers this phase.

---

## ARM landing of `rurp_vpp.cpp`

### Q1 — Does the py32 CMake manifest name `src/rurp_vpp.cpp`, or allow-list it as `PY32_EXCLUDED`?

| Option | Description | Selected |
|--------|-------------|----------|
| Name it in `FIRESTARTER_COMMON_SOURCES` | The ARM target really compiles the seam — what the phase goal literally says — and makes the py32 CMake the natural home for `RURP_HAS_VPP_DAC=0`. Dependency-freedom makes ARM compilation near risk-free. Cost: ARM verification needs a CI run, i.e. a push | ✓ |
| `PY32_EXCLUDED` with a reason | Green gate, no ARM build implication, no push. Cost: contradicts the phase goal, leaves py32 with no declared VPP capability (so it hits the `#error`), and hands Phase 126 a second exclusion to unwind | |
| Name it, and drop the AVR `__AVR__` default | Maximum uniformity: every target declares. Cost: reopens the decision just made, edits `platformio.ini`, and makes the flash delta harder to attribute | |

**User's choice:** Name it in `FIRESTARTER_COMMON_SOURCES`.
**Notes:** Confirmed on the current tree that pushing the milestone branch is still release-safe post-MERGE-03 — `py32f071.yml` fires on `pull_request` + `workflow_dispatch` + `push: [beta]` only, and `beta-build.yml` is untouched.

### Q2 — Does Phase 125 get its own ARM CI run?

| Option | Description | Selected |
|--------|-------------|----------|
| Own operator-gated CI run | Repeat Phase 124 D-08/D-09: push the milestone branch, `workflow_dispatch`, record run URL + head SHA, behind a checkpoint `--chain`/`--auto` cannot wave through. Same attributability the 125→126 ordering exists for | ✓ |
| Host compile only; ARM evidence rides Phase 126 | The harness already compiles the exact dependency-free TU with the exact py32 macro set, so the only untested variable is `arm-none-eabi-g++` on a stdint-only file. Cost: attribution split across two phases — the thing 125→126 was designed to prevent | |
| Host compile only, and say so explicitly | Records that ARM compilation is not verified this phase, with the reason. Cost: leaves the goal prose formally undischarged until later | |

**User's choice:** Own operator-gated CI run.

### Q3 — Criterion 4 says the flash delta must be measured, not assumed. What's the pass/fail rule?

| Option | Description | Selected |
|--------|-------------|----------|
| Strict equality — exactly 0 B, gated by the existing checker | `check_size_baseline.py`'s default `compare_avr()` is already strict equality against the live post-124 baseline, so this needs no new machinery and turns criterion 4 into an exit code | |
| A tolerance band, like MERGE-05's policy | Reuse the `--policy` pattern with a small allowance. Cost: a band invites an unexplained delta to pass, and no mechanism here should cost a byte | |
| Record the numbers, gate nothing | Measure all three targets, write the figures into the evidence artifact, no pass/fail. Cost: departs from the standing exit-code preference | ✓ |

**User's choice:** Record the numbers, gate nothing.
**Notes:** A deliberate, recorded exception to the project's standing exit-code preference — the planner must implement it as chosen and not quietly restore a gate. Flagged in response that `check_size_baseline.py`'s strict comparator is **already armed** in the existing sweep, so a nonzero delta goes red regardless of what this phase gates on.

### Q4 — If the already-armed strict comparator goes red, how should the phase handle it?

| Option | Description | Selected |
|--------|-------------|----------|
| Re-baseline in a named commit with the reason | Measure, record the delta and its cause, then re-baseline `size_baseline.json` in its own commit stating why the bytes are legitimate — Plan 124-10's shape. Green because the numbers are the truth, not because a tolerance widened | ✓ |
| Stop and surface it | A nonzero delta on a caller-free, gc-eligible TU means an assumption is wrong; halt and bring the cause back first. Cost: blocks on what may be a benign alignment artifact | |
| Re-baseline silently, note it in the artifact only | Cheapest. Cost: a baseline that moves without an attached reason is exactly what the 125→126 attributability ordering exists to prevent | |

**User's choice:** Re-baseline in a named commit with the reason.

---

## Wrap-up

| Option | Description | Selected |
|--------|-------------|----------|
| I'm ready for context | Record the PR #45 non-ancestry check shape and the evidence-artifact shape as Claude's-discretion house-style defaults | ✓ |
| Explore more gray areas | Discuss provenance proof, artifact shape, and the untouched-file pinning explicitly | |

**User's choice:** I'm ready for context.

---

## Claude's Discretion

Recorded as locked defaults in `125-CONTEXT.md` so downstream agents do not re-ask:

- The shape of the PR #45 non-ancestry proof (scripted exit-code SHA/ancestry check with a never-vacuous guard; whether to also assert content divergence).
- The evidence artifact: a `125-NONREGRESSION.md` in the `123`/`124` command/expected/observed row shape, re-executed in the closing plan.
- How the three untouched files are pinned: literal blob SHAs plus empty `git status --porcelain`, never a path-scoped `git diff`.
- Plan/wave decomposition and commit granularity, subject to the push/dispatch task being last and gated.
- Harness filename, `main`-shim mechanics, and how the return value crosses the process boundary.
- Where the one `#include "rurp_vpp.h"` line sits in `rurp_shield.h` — with an explicit instruction to *verify*, not assume, that it is inert to `test_revision_constants_parity.py`.

Two flagged as the most consequential discretion calls, cheap to reverse before planning: naming the seam in the ARM manifest (which pulls in the push), and taking an ARM CI run in this phase rather than riding Phase 126's.

---

## Deferred Ideas

- Closed-loop VPP control / DAC feedback — returns with an implementation and a board attached.
- VPP two-point calibration — needs new `rurp_configuration_t` fields, i.e. the forbidden `CONFIG_VERSION` bump; natural carrier is the queued v1.26 calibration milestone.
- AVR voltage-measurement rework (PR #45 `9134f2a` reroute + 16× oversampling) — its own phase, its own evidence.
- Exposing VPP control mode on the wire — revisit when a host consumer exists.
- Compile-time manual-control assertions in the real target builds — the rejected third option of the harness question.
- A planted mutated-seam fixture for the harness — declined in favour of the forced-DAC leg.
