---
phase: 158-residual-optimizations-cold-baseline-re-record-firmware-only
plan: "02"
subsystem: firmware
tags: [jsmn, json-parser, avr, ram-reduction, source-contract, py32f071, arm]

# Dependency graph
requires:
  - phase: 158-01
    provides: "158-before-figures.md — the cold pre-phase AVR flash/RAM ledger and the 184/184/17 native baseline this plan's own re-measurement is checked against"
provides:
  - "jsmntok_t narrowed from 8 to 6 bytes on AVR (uint8_t type; uint8_t size; int start; int end;), start/end unchanged and signed"
  - "A region-scoped source-contract gate (tests/test_jsmn_token_layout_source_contract_v158.py) pinning the signedness and the two narrowed members, proven RED and GREEN against three probes"
  - "ARM (py32f071) build outcome for LAND-05: built successfully on both the pre- and post-narrowing tree positions"
affects: ["158-04 (baseline re-record)", "158-05 (BASE-01 close-out)", "158-06 (after-figures)", "158-07 (ROADMAP/REQUIREMENTS correction)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Region-scoped source-contract gate (slice text above a `#ifndef X_HEADER` marker, raise rather than widen scan on a missing marker) for a vendored header carrying a dead duplicate implementation"
    - "avr-nm -S sizeof probe compiled directly against the real toolchain, never asserted in a native pytest/Unity test"

key-files:
  created:
    - firestarter/tests/test_jsmn_token_layout_source_contract_v158.py
  modified:
    - firestarter/lib/jsmn/src/jsmn.h

key-decisions:
  - "OD-1 executed: jsmntok_t layout is uint8_t type; uint8_t size; int start; int end; -- RAM -128 B on all three AVR targets, flash a reduction on all three (measured, not merely predicted), superseding REQUIREMENTS LAND-05's stale +30 B flash figure (C-2)."
  - "OD-6 executed: the dead duplicate implementation below #ifndef JSMN_HEADER in jsmn.h is left byte-unedited; the new gate's region slice is the machine-checked reason that is safe (proven by Probe B)."
  - "OD-7 executed: the ARM toolchain (gcc-arm-none-eabi, cmake, ninja-build) installed cleanly via apt in this devcontainer on the first attempt -- no newlib workaround was needed this session, the toolchain already pulled in libnewlib-arm-none-eabi. Both the pre-narrowing (785e644, via a throwaway detached worktree) and post-narrowing (HEAD) py32f071 builds succeeded, so the ARM half of LAND-05 is verified locally, not merely ceiling-recorded."

requirements-completed: [LAND-05]

# Metrics
duration: ~45min
completed: 2026-08-24
status: complete
---

# Phase 158 Plan 02: jsmntok_t narrowing + region-scoped source contract Summary

**`jsmntok_t` narrowed 8 -> 6 bytes on AVR (RAM -128 B on all three targets, flash a measured reduction on all three), pinned by a region-scoped source-contract gate proven RED/GREEN/RED across three probes, with the ARM (py32f071) build verified on both sides of the change.**

## Performance

- **Duration:** ~45 min
- **Completed:** 2026-08-24
- **Tasks:** 3 (3 executed, 2 produced commits, 1 recorded a build outcome with no tracked-file change)
- **Files modified:** 2 (1 changed, 1 created)

## Accomplishments

- `lib/jsmn/src/jsmn.h`'s live `jsmntok` struct narrowed from `jsmntype_t type; int start; int end; int size;` (8 B) to `uint8_t type; uint8_t size; int start; int end;` (6 B), with `start`/`end` explicitly marked UNCHANGED and SIGNED via an inline comment naming the twelve `-1` sentinel field references on six lines of `jsmn.c` (`:15,222,241,256,290,348`). `jsmn.c` is byte-unedited; the dead duplicate implementation below `#ifndef JSMN_HEADER` in `jsmn.h` is left byte-unedited (OD-6).
- `avr-nm -S` sizeof probe (via `~/.platformio/packages/toolchain-atmelavr/bin`, `-mmcu=atmega328p -Os`) confirmed 8 B old / 6 B new. No test asserts `sizeof(jsmntok_t)` anywhere (ceiling 6).
- Three cold `pio run` builds (`rm -rf .pio/build/<env>` + one `pio run -e <env>`, zero warnings each), measured against `158-before-figures.md` Sec.2:
  | Env | Flash before -> after | Flash delta | RAM before -> after | RAM delta |
  |---|---|---|---|---|
  | uno | 23090 -> 22952 | **-138 B** | 1562 -> 1434 | **-128 B** |
  | uno328pb | 23138 -> 23000 | **-138 B** | 1568 -> 1440 | **-128 B** |
  | leonardo | 25234 -> 25098 | **-136 B** | 2003 -> 1875 | **-128 B** |
  RAM delta is exactly -128 B (64 tokens x 2 bytes) on all three targets. Flash is a **reduction** on every target, superseding REQUIREMENTS LAND-05's stale `+30 B flash` prediction (C-2). Leonardo's new Caterina headroom against 28672: `28672 - 25098 = 3574 B` (up from 3438 B pre-edit).
- Both native envs (`native`, `native_nodevtools`) unchanged at 184/184 cases, 17 suites, GREEN on the first run after Task 1's commit -- no D-04 re-run needed. Re-ran `native` again after Task 2's commit: still 184/184, confirming the new `tests/` module moves no native case count.
- `python3 -m pytest tests/ -q -o addopts=""` from `/workspaces/firestarter`: 355 passed after Task 1's commit, 360 passed after Task 2's commit (355 + this module's 5 legs) -- zero `skipped` both times.
- New `tests/test_jsmn_token_layout_source_contract_v158.py` (5 tests), modelled on `tests/test_boolean_convention_source_contract_v133.py`: region-scoped to the text above the `#ifndef JSMN_HEADER` marker, with an import-time environment seam (`FIRESTARTER_JSMN_TOKEN_LAYOUT_SCAN_SOURCE`), a documented `sizeof` prohibition, and the CORRECT CI-coverage framing (`pytest tests/ -v` at `build.yml:161` DOES fire on this milestone branch, per `push: branches: ['**','!beta']`).
- Three RED-first probes run and recorded (header byte-restored between each, verified via `git diff --quiet`):
  - **Probe A (load-bearing):** narrowed the LIVE struct's `start` to `uint16_t` -> `test_token_start_and_end_remain_signed_int` FAILED (`any_start_count == 0`, required `1`).
  - **Probe B (dead-copy hazard):** narrowed ONLY the dead duplicate implementation's local `int start;` (inside the dead `jsmn_parse_primitive`, line 154, below the `#ifndef JSMN_HEADER` marker at line 117) to `uint16_t` -> all 5 legs stayed GREEN, proving the region slice is scoped to the live struct only, by design.
  - **Probe C (non-vacuity):** pointed `FIRESTARTER_JSMN_TOKEN_LAYOUT_SCAN_SOURCE` at a non-existent path in a genuine subprocess environment (`env VAR=... python3 -m pytest ...`, not `monkeypatch`, since the seam binds at import time) -> Coverage 1 and 2 failed with `FileNotFoundError`; Coverage 3/4/5 stayed passing since they never read the seam.
  - All five legs confirmed GREEN again on the restored, committed header (`5 passed`).
- ARM half of LAND-05 (Task 3): `arm-none-eabi-gcc`, `cmake`, and `ninja-build` were absent from this devcontainer and installed once via `apt-get install -y gcc-arm-none-eabi cmake ninja-build` (a distro machine-package install, zero npm/pip/cargo/PlatformIO manifest changes). Built the `py32f071` target using the exact `py32f071.yml`/`build-py32f071` composite-action recipe (`cmake -S platform/py32f071 -B build/py32f071 -G Ninja -DCMAKE_BUILD_TYPE=Release` then `cmake --build build/py32f071`) at **both** positions:
  - Pre-narrowing (`785e644`, `FW_PRE_SHA`, built in a throwaway detached `git worktree` at `/tmp/gsd-158/arm-probe/firestarter`): SUCCESS. `text=26900 data=32 bss=5888 dec=32820`.
  - Post-narrowing (HEAD, `/workspaces/firestarter`): SUCCESS. `text=26924 data=32 bss=5632 dec=32588`.
  Both builds produced a non-empty `firestarter_py32f071.hex`. The ARM half of LAND-05 is therefore **verified locally, not merely ceiling-recorded** this session -- the toolchain install succeeded on the first attempt, so no newlib-package workaround was needed. The throwaway worktree was removed and pruned; `git worktree list` matches its pre-probe output (only the primary tree and the untouched `firestarter_py32_ci` sibling). The `build/` directory created in `/workspaces/firestarter` by the post-narrowing build was removed before the task ended; `git status --porcelain` is empty.

## Task Commits

Each task was committed atomically:

1. **Task 1: Narrow jsmntok_t to 6 bytes on AVR, keeping start and end signed** - `490c435` (refactor)
2. **Task 2: Pin the token layout as a source contract that fails closed, proven RED first** - `8e126f2` (test)
3. **Task 3: Attempt the ARM half once, or record the ceiling** - no commit (build-and-record task; both ARM builds succeeded, no tracked file changed, HEAD unchanged from Task 2's commit)

## Files Created/Modified

- `firestarter/lib/jsmn/src/jsmn.h` - `jsmntok_t` narrowed to `uint8_t type; uint8_t size; int start; int end;`; `#include <stdint.h>` added; dead duplicate implementation below `#ifndef JSMN_HEADER` left byte-unedited.
- `firestarter/tests/test_jsmn_token_layout_source_contract_v158.py` - new region-scoped source-contract gate, 5 tests, proven against three probes (see Accomplishments).

## Decisions Made

- OD-1 (LAND-05 TAKEN, the target layout) executed exactly as researched; flash and RAM deltas re-measured at this plan's own position rather than transcribed from research, and matched the researched expectation on all three targets.
- OD-6 (dead duplicate implementation left unedited) executed; the new gate's region slice is the machine-checked reason this is safe, proven by Probe B rather than merely asserted.
- OD-7 (ARM attempted once): the toolchain install succeeded cleanly on the first attempt in this devcontainer session (`gcc-arm-none-eabi`, `cmake`, `ninja-build` via `apt-get`), so both sides were built and both outcomes recorded as SUCCESS -- no ceiling needed to be recorded this session, though the plan's ceiling-recording branch remains ready for a future session where the install fails.

## Deviations from Plan

None - plan executed exactly as written. The plan's Task 3 anticipated two possible outcomes (toolchain installs and both sides build, or the install fails and a ceiling is recorded); the toolchain installed cleanly on the first attempt and both builds succeeded, which is the plan's own first-listed outcome, not a deviation.

## Issues Encountered

None. Both native suites (`native`, `native_nodevtools`) reported 184/184 on their first run after each commit -- no D-04 re-run for a flake was needed anywhere in this plan.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 04 (baseline re-record) can now transcribe this plan's own cold AVR figures (uno 22952/1434, uno328pb 23000/1440, leonardo 25098/1875) into `scripts/baseline/size_baseline.json`'s `avr_targets`, alongside the native re-record from 158-01.
- Plan 06 (after-figures) can cite this plan's ARM outcome directly: both the pre- and post-narrowing `py32f071` builds succeeded (`text` 26900 -> 26924, `bss` 5888 -> 5632), so LAND-05's ARM half is closed as VERIFIED rather than left as a coverage ceiling.
- Plan 07 (ROADMAP/REQUIREMENTS correction) can cite this plan's measured flash deltas (`-138/-138/-136 B`) as the concrete replacement for LAND-05's stale `+30 B flash` prediction (C-2, opened in `158-before-figures.md`).
- No blockers.

---
*Phase: 158-residual-optimizations-cold-baseline-re-record-firmware-only*
*Completed: 2026-08-24*

## Self-Check: PASSED

- FOUND: firestarter/lib/jsmn/src/jsmn.h
- FOUND: firestarter/tests/test_jsmn_token_layout_source_contract_v158.py
- FOUND: .planning/phases/158-residual-optimizations-cold-baseline-re-record-firmware-only/158-02-SUMMARY.md
- FOUND commit (firestarter): 490c435 (refactor(158-02): narrow jsmntok_t to 6 bytes, start/end stay signed)
- FOUND commit (firestarter): 8e126f2 (test(158-02): pin the jsmn token layout as a region-scoped source contract)
- FOUND commit (meta): 6da5675 (docs(158-02): record jsmntok_t narrowing + source-contract SUMMARY)
