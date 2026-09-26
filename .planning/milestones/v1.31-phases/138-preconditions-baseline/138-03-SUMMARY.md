---
phase: 138-preconditions-baseline
plan: 03
subsystem: testing
tags: [platformio, unity, native-tests, fakeit, arduinofake, host-stubs, trace-capture, eprom, bus-config]

# Dependency graph
requires:
  - phase: 138-01
    provides: "firestarter submodule checked out on gsd/v1.31-27c-programming-algorithm-fidelity at the decided base 3085084"
provides:
  - "HOST_STUBS_RECORD_TIMING: a third, additive opt-in native-test recorder interleaving delay()/delayMicroseconds() into the existing ordered strobe stream"
  - "eprom_v131_expected.h: the merged strobe+timing comparator machinery (v131_merged_length/_at, _first_divergence, _assert_stream_equals, _snapshot) — no frozen arrays yet"
  - "[env:native_trace_v131]: a dedicated fourth native env, absent from default_envs and from both live gates"
  - "test_trace_eprom_v131: a Unity suite proving the real, unmodified eprom_write_execute converges in exactly 3 passes for all three protocols (0x07/0x08/0x0B), overflow-free and deterministic"
  - "138-03-TRACE-CAPTURE.md: measured entry counts, three derived bus_config values with provenance, and findings F-138-06/F-138-07/F-138-08"
affects: [138-05 (freezes the arrays this plan's dumps produced), Phase 144 TEST-06 (diffs the new cadence against this baseline), Phase 142 VPP-03 (F-138-08's owner)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Third opt-in stub-guard layer inside an existing #ifdef arm, additive-only, flag-off proven behaviourally (re-asserting 141/17 on both pinned envs) rather than by byte-diff"
    - "Merged-stream comparator: two independently-sorted sequences (strobe index, timing seq-key) joined by a two-pointer splice at v131_merged_at, rather than a single unified recorder array"
    - "Stateful index-keyed read-back model (R2) driven through the real rurp_read_from_register, so a real convergence-dependent retry loop can be traced without bypassing the verify path"
    - "Reproducibility-before-freeze: every capture drives twice and positionally diffs two snapshots before any array is committed as a golden"

key-files:
  created:
    - firestarter/test/native/avr/_shared/eprom_v131_expected.h
    - firestarter/test/native/avr/test_trace_eprom_v131/host_stubs.cpp
    - firestarter/test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp
    - .planning/phases/138-preconditions-baseline/138-03-TRACE-CAPTURE.md
  modified:
    - firestarter/test/native/avr/_shared/host_stubs_common.inc
    - firestarter/platformio.ini

key-decisions:
  - "R2 (stateful rurp_read_data_buffer opt-out) chosen over R1 (pointer-swap) for the read-back model, keeping the real memory_get_data/memory_set_data in the trace"
  - "Task 3 drives eprom_write_execute directly via firestarter_operation_main, deliberately skipping firestarter_operation_init, scoping the capture to exactly the retry loop and surfacing F-138-08"
  - "Fakeit's void-returning .AlwaysDo compiled directly against delay()/delayMicroseconds() — no adaptation to the non-void serial_read_mock.h/test_rurp_log_id.cpp idiom was needed"
  - "Kept the EPROM_V131_TRACE_DUMP dump case permanently in the suite behind its #ifdef (never deleted), mirroring test_eeprom28c_sdp.cpp's SDP_TRACE_DUMP precedent, rather than a temporary block removed after use"

requirements-completed: []

coverage:
  - id: D1
    description: "A third opt-in recorder (HOST_STUBS_RECORD_TIMING) interleaves delay()/delayMicroseconds() into the strobe stream, additive-only, with a fail-closed #error if the strobe recorder is absent; both pinned native envs remain at 141 cases / 17 suites with the new guard undefined"
    verification:
      - kind: integration
        ref: "pio test -e native && pio test -e native_nodevtools -- both 141 test cases: 141 succeeded, 17 suites, all PASSED"
        status: pass
      - kind: unit
        ref: "manual g++ compile of a TU defining HOST_STUBS_RECORD_TIMING without HOST_STUBS_REAL_REGISTER_UTILS -- fails with the #error message, exit 1"
        status: pass
    human_judgment: false
  - id: D2
    description: "eprom_v131_expected.h's merged-stream comparator, a dedicated fourth native env ([env:native_trace_v131], one-entry test_filter, absent from default_envs), and a smoke-tested suite skeleton proving the timing hook fires"
    verification:
      - kind: integration
        ref: "pio test -e native_trace_v131 -- 2 test cases: 2 succeeded (Task 2 slice); non-vacuity of the second smoke case confirmed by a deliberate temporary hook break (observed RED: 'Expected 2 Was 1'), then restored"
        status: pass
    human_judgment: false
  - id: D3
    description: "All three EPROM protocols (0x07 AM27C512, 0x08 AM27C020, 0x0B AM2716) captured from the real, unmodified eprom_write_execute against a 4-byte synthetic block, each converging in exactly 3 passes with zero recorder overflow and RESPONSE_CODE_OK, each proven deterministic via a two-drive positional snapshot comparison"
    verification:
      - kind: integration
        ref: "pio test -e native_trace_v131 -- 5 test cases: 5 succeeded; determinism non-vacuity confirmed by a deliberate temporary read-back perturbation (observed RED: 'Expected -1 Was 198'), then restored"
        status: pass
      - kind: other
        ref: "git -C /workspaces/firestarter status --porcelain src/ -- empty (no write-path source touched)"
        status: pass
    human_judgment: false
  - id: D4
    description: "138-03-TRACE-CAPTURE.md records measured merged/strobe/timing entry counts per protocol against RESEARCH's derived estimate, the three derived bus_config values with their derivation command, and findings F-138-06 (stale composition/count comment), F-138-07 (generator gap), and F-138-08 (VPP-regulator left enabled on the success path) with named owners"
    verification:
      - kind: other
        ref: "138-03-TRACE-CAPTURE.md, 177 lines; grep -c F-138-06/F-138-07/F-138-08 each == 1"
        status: pass
    human_judgment: false

# Metrics
duration: 50min
completed: 2026-08-08
status: complete
---

# Phase 138 Plan 03: Preconditions & Baseline — Trace Instrumentation & Capture Summary

**A third opt-in timing recorder plus a merged-stream fixture capture the real, unmodified 27C write
loop for all three EPROM protocols — 198/221/201 entries, exactly 3 passes each, proven deterministic
and overflow-free before anything is frozen.**

## Performance

- **Duration:** ~50 min
- **Started:** 2026-08-08T22:17:29Z (approx., per STATE.md's pre-execution timestamp)
- **Completed:** 2026-08-08T23:06:34Z
- **Tasks:** 3
- **Files modified:** 6 (4 created, 2 modified)

## Accomplishments

- Added `HOST_STUBS_RECORD_TIMING` — a third, purely additive opt-in recorder inside the existing
  `HOST_STUBS_REAL_REGISTER_UTILS` block, storing `{kind, us, seq}` timing entries keyed by
  `s_strobe_count` at push time, plus a fail-closed `#error` guard, plus the `HOST_STUBS_CUSTOM_READ_DATA_BUFFER`
  opt-out around the previously-unguarded `rurp_read_data_buffer`. Every new line lives inside a new
  `#ifdef`/`#ifndef`; re-verified behaviourally — `pio test -e native` and `-e native_nodevtools` both
  still report **141 cases / 17 suites, all PASSED**, and a standalone `g++` compile confirmed the
  fail-closed `#error` actually fires when `HOST_STUBS_RECORD_TIMING` is requested without
  `HOST_STUBS_REAL_REGISTER_UTILS`.
- Built `eprom_v131_expected.h` (the merged-stream comparator: `v131_merged_length/_at`, splicing
  timings immediately before the strobe at their recorded sequence key; `_first_divergence`;
  `_assert_stream_equals`, checking both overflow flags before length; `_snapshot`), a dedicated
  fourth native env `[env:native_trace_v131]` (one-entry `test_filter`, absent from `default_envs`,
  never fed to either live gate), and a smoke-tested suite skeleton — proven non-vacuous by a
  deliberate temporary hook break, observed RED, then restored.
- Captured all three protocols from the **real, unmodified** `eprom_write_execute`: derived the three
  chips' `bus_config` values live via `gen_sdp_bus_config.py`'s own `derive_row` (never invented),
  built a stateful index-keyed read-back model (R2) so the real up-to-20-pass retry loop converges in
  exactly 3 passes on a deliberately-chosen 4-byte block, and proved each capture reproducible via a
  two-drive positional snapshot diff — non-vacuity confirmed by a deliberate temporary read-back
  perturbation, observed RED, then restored. Measured: 198 (`0x07`) / 221 (`0x08`) / 201 (`0x0B`)
  merged entries, all ≤ 43% of the 512-entry caps; adaptive pulse-width growth confirmed
  (100/105/110 µs and 500/525/550 µs); `RESPONSE_CODE_OK` on all three.
- Recorded three findings in `138-03-TRACE-CAPTURE.md` (owner named, none fixed, per D-07): **F-138-06**
  (the pre-existing strobe-recorder block comment's stale "composes with"/"14 suites" claims — owner
  henols), **F-138-07** (the app-repo bus_config generator has no 27C row and rejects
  `static-high-pins` — owner henols; this plan derived-then-froze instead of extending the generator),
  and **F-138-08** (the captured stream shows no `CTRL_VPP_REGULATOR_ENABLE` clear on the converged
  success path, applies as predicted — owner Phase 142 / VPP-03).

## Task Commits

Each task was committed atomically, inside the `firestarter` submodule on
`gsd/v1.31-27c-programming-algorithm-fidelity`:

1. **Task 1: Add the opt-in timing recorder and the read-back opt-out to the shared stub layer** -
   `07d959c` (feat) — `firestarter`
2. **Task 2: Add the merged-stream fixture header, the fourth native env, and a smoke-tested suite
   skeleton** - `75c2acd` (feat) — `firestarter`
3. **Task 3: Capture the three protocol traces deterministically and record the measured counts** -
   `d134635` (feat) — `firestarter`; `583c4ce1` (docs) — meta (`138-03-TRACE-CAPTURE.md`)

**Plan metadata:** (this commit, immediately following) — meta

## Files Created/Modified

- `firestarter/test/native/avr/_shared/host_stubs_common.inc` (modified, +81 lines) — the timing
  recorder + fail-closed guard + read-back opt-out, all additive
- `firestarter/test/native/avr/_shared/eprom_v131_expected.h` (created) — merged strobe+timing
  comparator machinery; no frozen arrays yet (plan 05's job)
- `firestarter/platformio.ini` (modified, +38 lines) — `[env:native_trace_v131]`
- `firestarter/test/native/avr/test_trace_eprom_v131/host_stubs.cpp` (created) — the three opt-in
  guards, `reset_register_cache`, and the stateful read-back model
- `firestarter/test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp` (created) — setUp with
  the fakeit timing hooks, 2 smoke cases, 3 protocol cases, the permanent-but-disabled trace-dump case
- `.planning/phases/138-preconditions-baseline/138-03-TRACE-CAPTURE.md` (created, 177 lines) — measured
  counts, derived bus_configs, F-138-06/07/08

## Decisions Made

- **R2 over R1** for the read-back model: kept the real `memory_get_data`/`memory_set_data` in the
  trace (rather than swapping the handle's function pointers), so the verify read's own bus activity
  is captured — materially strengthening Phase 144's TEST-06 claim per the plan's own rationale.
- **Drive `_main` directly, skip `_init`**: `eprom_write_execute` self-enables VPP if not already
  enabled, so calling only `firestarter_operation_main` keeps the capture scoped to exactly the retry
  loop the timing layer exists to trace, and is what exposed F-138-08.
- **Keep the trace-dump case permanently behind `#ifdef EPROM_V131_TRACE_DUMP`**, matching the
  in-repo `test_eeprom28c_sdp.cpp`/`SDP_TRACE_DUMP` precedent exactly, rather than deleting it after
  use — it is a reusable, documented diagnostic, never compiled by default.
- **Bus_config values derived live, not hand-derived**: ran `gen_sdp_bus_config.py`'s `derive_row`
  against the real `chip_database.json`/`pinouts.json` for AM27C512/AM27C020/AM2716, translating per
  `json_parser.c`'s `parse_bus_config` field-for-field, with the derivation command recorded beside
  each literal in both the source comment and `138-03-TRACE-CAPTURE.md`.

## Deviations from Plan

None — plan executed exactly as written. All three tasks' automated `<verify>` blocks and every
acceptance criterion in `138-03-PLAN.md` passed; no bug, missing functionality, blocking issue, or
architectural question arose that required a Rule 1-4 classification.

## Issues Encountered

- **`timing_push` was not declared in the test translation unit.** `eprom_v131_expected.h` deliberately
  declares only the twelve *read* accessors ("declared once here so consumers get them from a single
  place"); `timing_push` is the *write* entry point only the suite installing the fakeit hooks needs,
  and was never meant to live there. Fixed immediately by declaring it directly in
  `test_trace_eprom_v131.cpp`, with a comment explaining why it is not in the shared header.
- **A prose comment accidentally tripped the `grep -c 'HOST_STUBS_CUSTOM_HW_REVISION[^_]'` acceptance
  check.** The sentence "defining `HOST_STUBS_CUSTOM_HW_REVISION` here" matched the pattern (the
  character after the macro name was a space, not an underscore) even though the file never actually
  defines that macro. Reworded to describe the guard without spelling the bare macro name.

Neither required a design change; both were caught and fixed before the affected task's commit.

## User Setup Required

None — no external service configuration required. All work is native (host-side) test infrastructure.

## Next Phase Readiness

- Plan 05 has everything it needs to freeze the arrays: three per-protocol dump files under the
  session scratchpad (`proto_07.txt` / `proto_08.txt` / `proto_0B.txt`, each containing at least as
  many ready-to-paste initialiser lines as its protocol's recorded merged length), the exact derived
  `bus_config` literals (already committed in `test_trace_eprom_v131.cpp`), and the measured entry
  counts in `138-03-TRACE-CAPTURE.md` to size the frozen-fixture inventory JSON against.
- **F-138-08** (VPP regulator left enabled after a successful write) is carried forward with owner
  Phase 142 / VPP-03 — not this phase's or this plan's job to close.
- **F-138-06** (stale block-comment wording) and **F-138-07** (generator gap) both carry owner
  `henols` — neither blocks any downstream plan in this milestone.
- PREP-03 itself remains open (`[ ]` in REQUIREMENTS.md) — this plan produces evidence toward it only;
  per `may_tick_requirements: []`, no requirement ID was ticked here. Plan 138-07 is the one that
  discharges PREP-03.
- No push, no CI dispatch, and no write-path source edit occurred — all confirmed and out of this
  plan's scope.

## Self-Check: PASSED

- FOUND: `/workspaces/firestarter/test/native/avr/_shared/host_stubs_common.inc`
- FOUND: `/workspaces/firestarter/test/native/avr/_shared/eprom_v131_expected.h`
- FOUND: `/workspaces/firestarter/test/native/avr/test_trace_eprom_v131/host_stubs.cpp`
- FOUND: `/workspaces/firestarter/test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp`
- FOUND: `/workspaces/firestarter/platformio.ini`
- FOUND: `/workspaces/.planning/phases/138-preconditions-baseline/138-03-TRACE-CAPTURE.md`
- FOUND commit (firestarter): `07d959c`
- FOUND commit (firestarter): `75c2acd`
- FOUND commit (firestarter): `d134635`
- FOUND commit (meta): `583c4ce1`

No missing items.

---
*Phase: 138-preconditions-baseline*
*Completed: 2026-08-08*
