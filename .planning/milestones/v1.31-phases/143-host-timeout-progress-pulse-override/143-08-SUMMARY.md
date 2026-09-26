---
phase: 143-host-timeout-progress-pulse-override
plan: 08
subsystem: firmware
tags: [python, pytest, source-contract, preprocessor-guard, avr, serial-on-io, bf-2, host-02, host-03, d-06]

# Dependency graph
requires:
  - phase: 143-05
    provides: "The time-gated, #ifndef SERIAL_ON_IO-guarded MSG_DATA_PROGRESS (0xE0) emission at the top of eprom_internal_write_execute_body's per-byte loop (src/proms/eprom.cpp), its last_emit_ms state variable (guarded identically), and EPROM_PROGRESS_EMIT_INTERVAL_MS (include/eprom.h) -- the exact code this plan pins."
  - phase: 143-03
    provides: "The stdlib-only source-contract gate precedent (tests/test_ack_layout_source_contract_v143.py): env-seam-per-scanned-file, verbatim comment stripper, brace-matched body extraction, concatenation-built forbidden needles plus a self-check that they never appear verbatim, and the two-part non-vacuity leg shape this plan's Coverage 8 follows."
provides:
  - "tests/test_progress_emission_is_leonardo_only.py -- a 10-leg, stdlib-only source-contract gate (749 lines) pinning: the emit's uniqueness; the emit's and its state variable's INDEPENDENT membership inside a '#ifndef SERIAL_ON_IO' region, determined by preprocessor-directive depth tracking rather than a nearby-substring heuristic; the emit's placement before the 0xFF skip; the named EPROM_PROGRESS_EMIT_INTERVAL_MS interval constant; the one-contract handle->mem_size payload (scoped to the emit's own block, so the loop's own unrelated handle->data_size bound elsewhere in the function cannot false-positive it); and platformio.ini's SERIAL_ON_IO flag scope, pinned to exactly uno/uno328pb in BOTH directions."
  - "Two new environment seams, FIRESTARTER_PROGRESS_SCAN_EPROM_SOURCE and FIRESTARTER_PROGRESS_SCAN_PIO_CONFIG, bound at import time, colliding with neither plan 143-03's FIRESTARTER_ACK_SCAN_DISPATCH_SOURCE nor plan 142-06's two FIRESTARTER_HV_SCAN_* seams."
  - "D-25's full planted-violation campaign: 10 distinct RED transcripts (the 8 named plants, both directions of plant 7, both sub-variants of plant 8) with every leg reachable on the FIRST attempt -- no locator-only repair was needed -- followed by a clean GREEN run against the real source with no env seam set."
  - "D-06's non-claim restated with both dimensions on the record, and this module explicitly labelled a source contract (never behavioural evidence), citing the same structural reason Phase 142's command_done() gate already established."
affects: [143-10, 144, 145]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Source-contract gate for a compile-time #ifdef-scoped guard whose absence is invisible to every native test oracle: preprocessor-directive depth-tracking (a stack pairing each #ifndef/#ifdef with its OWN matching #endif, never a nearby-substring heuristic) proves guard MEMBERSHIP structurally, so an emit that merely follows an unrelated guard elsewhere in the function cannot satisfy the leg."
    - "platformio.ini env-flag scope pinned by splitting the WHOLE file into named [env:NAME] sections (via a generic '^\\[...\\]$' header regex, filtered to the 'env:' prefix) and checking each section's OWN text independently -- a flag added only to the shared [env] defaults block is correctly NOT attributed to any single named env, matching what the two D-25 plant directions actually test."
    - "A forbidden-direction self-check needle whose bare form is the module's own unavoidable subject: register only a NARROWER, compiler-invocation-prefixed composite (the '-D' flag spelling immediately against the macro name) as the concatenation-built needle, never the bare identifier -- the bare identifier legitimately appears throughout the module's own prose and positive-detection regexes, exactly as 'CONTROL_REGISTER' and 'handle->protocol' appear freely, unregistered, in tests/test_hv_routing_source_contract_v142.py."

key-files:
  created:
    - firestarter/tests/test_progress_emission_is_leonardo_only.py
  modified: []

key-decisions:
  - "The Uno-class guard macro's BARE name ('SERIAL_ON_IO') is deliberately EXCLUDED from the concatenation-built self-check needle list, even though the plan's own acceptance criteria names it as one of the forbidden-direction needles. Registering the bare 12-character token would make Coverage 10 fail against this module's OWN necessary docstring prose and its own positive-detection regex patterns (both of which must say 'SERIAL_ON_IO' directly, repeatedly, since it is this module's central subject) -- an unavoidable self-contradiction, empirically confirmed: the first authoring pass DID trip this exact collision (see Deviations). What IS registered instead is the flag's exact COMPILER-INVOCATION spelling (a '-D' flag immediately adjacent to the macro name, exactly as it appears on its own line in platformio.ini) -- prose describing the flag naturally never writes '-D SERIAL_ON_IO' contiguously (nobody writes \"the -D SERIAL_ON_IO flag\" in running English), so this narrower composite is both true to the plan's intent (a SERIAL_ON_IO-keyed forbidden-direction needle exists, is concatenation-built, and is proven absent by Coverage 10) and achievable without contradicting the module's own necessary vocabulary."
  - "Coverage 6's forbidden-needle check ('handle->data_size must not appear') is scoped to the matched emit BLOCK's own text (the regex match's whole span), never the whole function body -- direct inspection of the real eprom_internal_write_execute_body shows handle->data_size legitimately appears TWICE already, as the per-byte loop's own upper bound and the final verify pass's upper bound, both unrelated to the emit's payload. An unscoped whole-body check would false-positive against the real, correct, already-committed source; this was caught empirically while authoring Coverage 6, before the module was ever run (see Deviations)."
  - "Coverage 7's env-scope leg parses platformio.ini into per-env sections by splitting on every '[...]' header (not a per-env regex seam), then checks each named env's OWN text independently -- so a flag hypothetically added to the shared [env] defaults block (which every env inherits via \\${env.build_flags}) is correctly NOT attributed to any single env by this function, matching exactly what D-25's two plant directions (added to leonardo; removed from uno328pb) test, and avoiding a false claim about inheritance this leg was never asked to prove."
  - "Every one of the 10 D-25 plants was reachable and produced the RIGHT leg(s) RED on the FIRST attempt -- no leg needed a locator-only repair (contrast with 143-03's Plant 8, which needed none either, but this plan had zero regex-design misses across all 10 plants, including both directions of plant 7 and both sub-variants of plant 8)."

patterns-established:
  - "Pattern: when a plan's acceptance criteria names a bare token as a 'forbidden-direction needle' but that token is also the module's own unavoidable subject, resolve the tension by registering a narrower, naturally-distinct COMPOSITE spelling instead (never the bare token), and record the substitution explicitly in the SUMMARY's Decisions Made -- do not silently weaken Coverage 10's self-check to accommodate an unregisterable bare token."

requirements-completed: []

coverage:
  - id: D1
    description: "The emit's uniqueness, its membership inside a '#ifndef SERIAL_ON_IO' region (determined by preprocessor-directive depth tracking, not a nearby-substring heuristic), its placement before the 0xFF skip, and its use of the named EPROM_PROGRESS_EMIT_INTERVAL_MS constant are all pinned, each independently RED-tested"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_exists_inside_the_write_execute_body"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_is_inside_a_serial_on_io_guard"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_progress_emission_is_leonardo_only.py::test_the_emit_precedes_the_skip_continues"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_progress_emission_is_leonardo_only.py::test_the_emit_uses_the_named_interval_constant"
        status: pass
    human_judgment: false
  - id: D2
    description: "The millis() state variable's declaration is pinned inside the SAME guard class, checked independently of the emit -- proven non-redundant by D-25 plant 3 (leg 3 RED while leg 2 stays GREEN)"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_progress_emission_is_leonardo_only.py::test_the_millis_state_variable_is_inside_the_same_guard_class"
        status: pass
    human_judgment: false
  - id: D3
    description: "The payload keeps exactly one contract for 0xE0 (handle->mem_size, never the block-relative handle->data_size), the check scoped to the emit's own block so the loop's own unrelated data_size bound elsewhere in the function cannot false-positive it"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_progress_emission_is_leonardo_only.py::test_the_payload_keeps_one_contract_for_the_id"
        status: pass
    human_judgment: false
  - id: D4
    description: "platformio.ini's SERIAL_ON_IO flag is pinned to exactly the uno and uno328pb env sections and no other, in BOTH directions -- keeping D-06's 'delivered on leonardo only' non-claim honest against a future edit"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_progress_emission_is_leonardo_only.py::test_serial_on_io_is_defined_on_exactly_the_uno_class_envs"
        status: pass
    human_judgment: false
  - id: D5
    description: "The gate cannot pass vacuously (both default scan targets and the seam-aware extracted body are non-vacuity-checked), cannot be silently skipped, and its own concatenation-built forbidden needles are proven absent verbatim from its own source"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_progress_emission_is_leonardo_only.py::test_scan_targets_are_non_vacuous"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_progress_emission_is_leonardo_only.py::test_this_module_cannot_be_silently_skipped"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_progress_emission_is_leonardo_only.py::test_own_needles_do_not_appear_verbatim_in_this_module"
        status: pass
    human_judgment: false
  - id: D6
    description: "Every leg was seen RED on a planted violation behind the env seams (10 distinct plants: the 8 named mutations, both directions of plant 7, both sub-variants of plant 8) and GREEN for the right reason against the real source, with the working tree confirmed clean (git status --porcelain) after every single plant"
    verification:
      - kind: other
        ref: "D-25 planted-violation campaign -- see this SUMMARY's 'D-25 Evidence' section for all 10 verbatim transcripts"
        status: pass
    human_judgment: false
  - id: D7
    description: "All three AVR targets link with zero flash/RAM delta from post-143-05 (this plan touches no firmware source), zero warnings anywhere (AVR macro_redefinition=0 on all three; native/native_nodevtools unmoved at the 1166 watermark, cold-measured), and the whole firmware pytest suite is green at 292 (282 baseline + this module's 10)"
    verification:
      - kind: unit
        ref: "pio run -e uno / -e uno328pb / -e leonardo (cold)"
        status: pass
      - kind: unit
        ref: "python3 scripts/check_build_warnings.py --rebuild (cold, native + native_nodevtools rebuilt from a clean .pio/build)"
        status: pass
      - kind: unit
        ref: "python3 -m pytest tests/ -o addopts=\"\" -q"
        status: pass
    human_judgment: false

duration: 37min
completed: 2026-08-13
status: complete
---

# Phase 143 Plan 08: BF-2 Source-Contract Gate -- Progress Emission Pinned Leonardo-Only Summary

**A new 10-leg, stdlib-only source-contract gate pins plan 143-05's intra-block `MSG_DATA_PROGRESS` emission (and its `millis()` state variable) as compiled OUT on `uno`/`uno328pb` and compiled in on `leonardo`/native, with every leg proven RED on a planted violation and GREEN against the real source -- no behavioural oracle exists for this `#ifdef`-scoped guard, so this module is explicitly labelled a source contract, never behavioural evidence.**

## Performance

- **Duration:** ~37 min
- **Started:** 2026-08-13T03:26:56Z (STATE.md `last_updated` at hand-off from 143-07)
- **Completed:** 2026-08-13T04:03:37Z
- **Tasks:** 2 completed (both `type="auto"`, no checkpoints)
- **Files touched:** 1 (1 created, 0 modified)

## Accomplishments

- **BF-2's trap is now mechanically pinned, not merely commented.** `tests/test_progress_emission_is_leonardo_only.py` (749 lines) proves, by scanning the checked-in source text of `src/proms/eprom.cpp` and `platformio.ini`: the `MSG_DATA_PROGRESS` emit exists exactly once inside `eprom_internal_write_execute_body`; the emit's offset and the `last_emit_ms` state variable's declaration each independently fall inside their OWN `#ifndef SERIAL_ON_IO` ... `#endif` region, determined by scanning every preprocessor conditional directive in the body IN ORDER and pairing each with its own matching `#endif` via depth tracking (never a nearby-substring heuristic); the emit's offset is less than the `expected == 0xFF` skip's offset; the emit's own predicate names `EPROM_PROGRESS_EMIT_INTERVAL_MS` rather than a bare literal; the emit's second argument is `handle->mem_size` (never the block-relative `handle->data_size`); and `platformio.ini` defines `-D SERIAL_ON_IO` on exactly the `uno` and `uno328pb` env sections, never `leonardo` or any `native*` env.
- **Labelled honestly as a source contract, never behavioural evidence, with the reason spelled out in the module's own docstring**: `src/boards/uno_rurp_shield.cpp` (the file implementing `com_mode`, the strong `rurp_log_id()` override and the 4-slot `deferred_log` buffer) is compiled in NO native environment -- confirmed directly this session (`grep -rn` over every native `build_src_filter` in `platformio.ini`) -- and the native `rurp_log_id` capture stub (`test/native/avr/test_loop_eprom_v131/host_stubs.cpp` and its siblings) captures every frame UNCONDITIONALLY, with zero `com_mode` gate anywhere under `test/` (independently confirmed: `grep -rln com_mode test/` returns nothing). A native test therefore cannot distinguish "delivered" from "would have been delivered if the UART were not torn down" -- only a source scan can pin this guard.
- **Both this-module-specific self-protection dilemmas were caught empirically, before the module was ever run against real data, and resolved by design changes** (see Decisions Made and Deviations): the guard macro's bare name cannot be a self-check needle (it is the module's own unavoidable subject), and the payload's forbidden-needle check cannot scan the whole function body (the forbidden field name legitimately appears twice elsewhere, as unrelated loop bounds).
- **D-25's full campaign discharged with zero locator-only repairs.** All 10 required transcripts (the 8 named plants, both directions of plant 7, both sub-variants of plant 8) were captured; every plant turned exactly the leg(s) it targets RED on the FIRST attempt, including the primary plant (2, the naive "guard removed" implementation BF-2 says would regress HOST-03) landing on leg 2 alone, and plant 3 proving leg 3's independence (leg 3 RED, leg 2 GREEN). Two plants (1 and 8's both sub-variants) produced honest, stronger-than-required spillover onto other legs that share the same extraction helper -- documented below, not glossed over.
- **Re-confirmed, cold, that the guard truly costs nothing on the two `SERIAL_ON_IO` targets and nothing new anywhere else:** `pio run -e uno` / `-e uno328pb` / `-e leonardo` are all byte-identical to post-143-05 (24824 / 24874 / 26906 B respectively -- this plan touches zero firmware source), and a truly COLD `check_build_warnings.py --rebuild` (native and native_nodevtools rebuilt from a removed `.pio/build`, not reused from an earlier warm run) reports `macro_redefinition=0` on all three AVR targets and `total warnings=1166` (== the recorded watermark, unmoved) on both native envs.
- **The whole firmware pytest suite now reports 292 passed** (282 post-143-05/143-03 baseline + this module's 10), committed before the full-suite run per L-1/S-8 (`test_flash_path_record_sync.py` asserts whole-repo porcelain).
- **D-06's non-claim is now on the record with both dimensions mechanically enforced for the second one:** intra-block write progress is emitted on the EPROM path only (a documentation fact, unenforced by this module), and delivered on `leonardo` only (a fact this module's Coverage 7 leg now enforces mechanically against a future `platformio.ini` edit in either direction).
- **This plan marks no requirement Complete**, per its own frontmatter (`requirements: []`, deliberately not repopulated) -- it contributes the gate that keeps HOST-02 honest and protects HOST-03 on Uno-class boards; plan 143-10 flips the `HOST-*` checkboxes once every plan's evidence exists.

## Task Commits

Each task was committed atomically, inside `/workspaces/firestarter` on branch `gsd/v1.31-27c-programming-algorithm-fidelity`:

1. **Task 1: Author `tests/test_progress_emission_is_leonardo_only.py` and get it green against the real source** - `9349fce` (test)
2. **Task 2: Run the D-25 planted-violation campaign, verify no locator-only repair was needed, and confirm the build/warning/whole-suite posture** - no additional commit. Every one of the 10 plants turned exactly the intended leg(s) RED on the first attempt; no regex, extractor or assertion needed repair, so there is no code change to commit for this task. All D-25 evidence (transcripts, the final clean-tree confirmation, and the build/warning re-verification) is recorded below.

**Plan metadata:** committed in the meta repo (`/workspaces`), see below.

## Files Created/Modified

- `firestarter/tests/test_progress_emission_is_leonardo_only.py` (new, 749 lines) - the source-contract gate described above; two env seams (`FIRESTARTER_PROGRESS_SCAN_EPROM_SOURCE`, `FIRESTARTER_PROGRESS_SCAN_PIO_CONFIG`); imports only `os`, `re`, `pathlib` from the stdlib; no `pio` invocation, no shelling out, no import from `src/`.

## Decisions Made

- **The Uno-class guard macro's bare name (`SERIAL_ON_IO`) is deliberately excluded from the self-check needle list; only its exact `-D`-prefixed compiler-invocation spelling is registered.** See Deviations for the empirical trigger. This is a considered, explicit departure from a literal reading of the plan's own acceptance-criteria parenthetical (which names `SERIAL_ON_IO` bare as one of the "forbidden-direction needles"); the module's own Naming note documents the substitution and its reasoning so a future reader does not mistake it for an oversight.
- **Coverage 6's forbidden-needle absence check is scoped to the matched emit block's own text, never the whole function body.** `handle->data_size` legitimately appears twice elsewhere in `eprom_internal_write_execute_body` (the per-byte loop's own upper bound, and the final verify pass's upper bound) -- an unscoped check would false-positive against the real, already-committed, correct source.
- **Coverage 7 parses `platformio.ini` by splitting on every section header (`^\[...\]$`), not via a per-env seam**, so a flag hypothetically added only to the shared `[env]` defaults block (inherited by every env via `${env.build_flags}`) is correctly not attributed to any single named env -- matching exactly what D-25's two plant directions test (a flag added/removed from a NAMED env's own literal text) and avoiding an unrequested claim about flag inheritance.
- **No `native_trace_v131`, `native_params_v131` or `native_loop_v131` run was performed or is claimed as evidence for this plan** -- D-24 (this plan touches no firmware source, so there is nothing for those envs to newly prove) and this plan's own `<verification>` block explicitly excludes `native_trace_v131`. Unlike 143-05 (which modified `eprom.cpp` and therefore had to re-confirm the native Unity suites), this plan's task 2 acceptance criteria name only the AVR builds, `check_build_warnings.py`, and the whole-repo pytest count -- no native Unity suite re-run is required or was performed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed a literal, verbatim mention of the forbidden self-check needle from the module's own docstring**
- **Found during:** Task 1, on the FIRST run of the freshly-authored module against the real source (`python3 -m pytest tests/test_progress_emission_is_leonardo_only.py -v -o addopts=""`), before any commit
- **Issue:** `test_own_needles_do_not_appear_verbatim_in_this_module` (Coverage 10) failed immediately: Coverage 6's own docstring, explaining why the forbidden-needle check is scoped to the emit's block rather than the whole body, had written the reasoning by literally quoting the forbidden field reference ("the per-byte loop's own bound (`i < handle->data_size`)") -- exactly the needle Coverage 10 checks is absent from this module's own source. This is precisely the "Naming note" hazard both analog modules document for their own forbidden identifiers (the dead regulator-helper name in `test_hv_routing_source_contract_v142.py`; the retired-emit-macro name in `test_ack_layout_source_contract_v143.py`), independently re-encountered here for a different token.
- **Fix:** Reworded the docstring sentence to describe the location structurally ("the for-loop condition just above this function's own final verify pass") instead of quoting the forbidden text verbatim. No logic change; message/docstring text only.
- **Files modified:** `firestarter/tests/test_progress_emission_is_leonardo_only.py` (not yet committed at the time this was found -- folded into task 1's own single commit, not a separate one)
- **Verification:** Full module re-run: 10 passed.
- **Committed in:** `9349fce` (Task 1's own commit -- the fix was applied before that commit was made, so no separate commit exists for it)

---

**Total deviations:** 1 auto-fixed (1 bug, Rule 1), found and fixed entirely within Task 1, before any commit.
**Impact on plan:** Cosmetic (a docstring rewording); no assertion was weakened, no needle was un-concatenated, and no scan target or regex changed. Confirms the "Naming note" discipline both analog modules already document generalizes correctly to a third, independently-authored forbidden token.

## D-25 Evidence: RED-on-plant for all 10 plants, then GREEN, for `tests/test_progress_emission_is_leonardo_only.py`

Per the plan's obligation, every plant was applied to a **scratch copy** of `src/proms/eprom.cpp` or `platformio.ini` under this session's scratchpad directory (`/tmp/claude-1000/-workspaces/e4dbfb7a-5869-4346-b80f-215eeb93af79/scratchpad/143-08-plants/`), never on the tracked, committed source, with the relevant env seam pointed at the mutated copy. `git status --short` (equivalent to `--porcelain`) was checked immediately after every single plant and was clean every time -- confirmed again in the transcript below where shown. Full `-v` PASS/FAIL tables are shown for each plant; the specific assertion text is shown beneath each table.

### Plant 1 -- delete the emit entirely (`LOG_DATA_ID_U32_U32(...)` call replaced with a comment)

Targets leg 1 (`test_the_progress_emit_exists_inside_the_write_execute_body`) RED.

```
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_exists_inside_the_write_execute_body FAILED [ 10%]
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_is_inside_a_serial_on_io_guard FAILED [ 20%]
tests/test_progress_emission_is_leonardo_only.py::test_the_millis_state_variable_is_inside_the_same_guard_class PASSED [ 30%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_precedes_the_skip_continues FAILED [ 40%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_uses_the_named_interval_constant FAILED [ 50%]
tests/test_progress_emission_is_leonardo_only.py::test_the_payload_keeps_one_contract_for_the_id FAILED [ 60%]
tests/test_progress_emission_is_leonardo_only.py::test_serial_on_io_is_defined_on_exactly_the_uno_class_envs PASSED [ 70%]
tests/test_progress_emission_is_leonardo_only.py::test_scan_targets_are_non_vacuous PASSED [ 80%]
tests/test_progress_emission_is_leonardo_only.py::test_this_module_cannot_be_silently_skipped PASSED [ 90%]
tests/test_progress_emission_is_leonardo_only.py::test_own_needles_do_not_appear_verbatim_in_this_module PASSED [100%]
========================= 5 failed, 5 passed in 0.22s =========================
```

**Finding (honest, not glossed): this plant turns 5 legs RED, not only the targeted leg 1.** Legs 2, 4, 5 and 6 all locate the emit via the same `MSG_DATA_PROGRESS`-keyed regex (or the emit-block regex built on top of it) before checking anything else about it; with the emit deleted, each of those legs' own "expected exactly 1 / at least 1, found 0" guard fires first. Leg 3 (the state variable, untouched by this plant) and leg 7 (`platformio.ini`, an unrelated file) correctly stay GREEN, proving leg 3 does not depend on the emit's own presence. `git status --short` after this run: clean.

### Plant 2 -- move the emit outside the `#ifndef SERIAL_ON_IO` block (keep the guard, keep the variable) -- THE PRIMARY PLANT

This is the primary plant: it reproduces exactly the naive implementation BF-2 says would regress HOST-03 on `uno`/`uno328pb` (an unconditional intra-block progress emit that would fill the Uno's 4-slot `deferred_log` buffer and starve a subsequent `MSG_ERR_MAX_PULSES` frame of its slot). Targets leg 2 (`test_the_progress_emit_is_inside_a_serial_on_io_guard`) RED.

```
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_exists_inside_the_write_execute_body PASSED [ 10%]
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_is_inside_a_serial_on_io_guard FAILED [ 20%]
tests/test_progress_emission_is_leonardo_only.py::test_the_millis_state_variable_is_inside_the_same_guard_class PASSED [ 30%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_precedes_the_skip_continues PASSED [ 40%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_uses_the_named_interval_constant PASSED [ 50%]
tests/test_progress_emission_is_leonardo_only.py::test_the_payload_keeps_one_contract_for_the_id PASSED [ 60%]
tests/test_progress_emission_is_leonardo_only.py::test_serial_on_io_is_defined_on_exactly_the_uno_class_envs PASSED [ 70%]
tests/test_progress_emission_is_leonardo_only.py::test_scan_targets_are_non_vacuous PASSED [ 80%]
tests/test_progress_emission_is_leonardo_only.py::test_this_module_cannot_be_silently_skipped PASSED [ 90%]
tests/test_progress_emission_is_leonardo_only.py::test_own_needles_do_not_appear_verbatim_in_this_module PASSED [100%]
========================= 1 failed, 9 passed in 0.14s =========================
```

The failing assertion:
```
AssertionError: the MSG_DATA_PROGRESS emit's offset does not fall inside any '#ifndef SERIAL_ON_IO' ... '#endif' region of eprom_internal_write_execute_body's body (determined by preprocessor-directive depth tracking, not a nearby-substring heuristic) -- BF-2/HOST-03: an unguarded emission on uno/uno328pb would fill the 4-slot deferred_log buffer and starve a subsequent MSG_ERR_MAX_PULSES frame of its slot, turning a program failure into a host transport timeout on a path that works today.
  Regions found (macro, kind, true_start, true_end): [('SERIAL_ON_IO', 'ifndef', 2987, 3025)]
```

**Finding:** exactly the targeted leg (2) went RED; every other leg -- including 3, the state variable's own guard, left untouched by this plant -- stayed GREEN. The depth-tracker correctly identified the ONE remaining guard region (the variable's own, at offsets 2987-3025) and correctly determined the emit's offset (7143) falls outside it. `git status --short` after this run: clean.

### Plant 3 -- move only the `millis()` state variable's declaration outside its guard

Targets leg 3 (`test_the_millis_state_variable_is_inside_the_same_guard_class`) RED, leg 2 GREEN -- the asymmetry that proves leg 3 is not redundant with leg 2.

```
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_exists_inside_the_write_execute_body PASSED [ 10%]
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_is_inside_a_serial_on_io_guard PASSED [ 20%]
tests/test_progress_emission_is_leonardo_only.py::test_the_millis_state_variable_is_inside_the_same_guard_class FAILED [ 30%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_precedes_the_skip_continues PASSED [ 40%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_uses_the_named_interval_constant PASSED [ 50%]
tests/test_progress_emission_is_leonardo_only.py::test_the_payload_keeps_one_contract_for_the_id PASSED [ 60%]
tests/test_progress_emission_is_leonardo_only.py::test_serial_on_io_is_defined_on_exactly_the_uno_class_envs PASSED [ 70%]
tests/test_progress_emission_is_leonardo_only.py::test_scan_targets_are_non_vacuous PASSED [ 80%]
tests/test_progress_emission_is_leonardo_only.py::test_this_module_cannot_be_silently_skipped PASSED [ 90%]
tests/test_progress_emission_is_leonardo_only.py::test_own_needles_do_not_appear_verbatim_in_this_module PASSED [100%]
========================= 1 failed, 9 passed in 0.10s =========================
```

The failing assertion:
```
AssertionError: the millis() state variable's declaration does not fall inside any '#ifndef SERIAL_ON_IO' ... '#endif' region of eprom_internal_write_execute_body's body -- D-22: an unreferenced local on a build that defines the flag is an unused-variable warning, and the AVR warning policy is exactly zero; a leg pinning only the emit would let that regression back in.
  Regions found (macro, kind, true_start, true_end): [('SERIAL_ON_IO', 'ifndef', 6980, 7189)]
```

**Finding:** exactly leg 3 went RED; leg 2 (the emit's own guard, untouched by this plant, now the ONLY surviving region) stayed GREEN. This is the precise asymmetry D-25 requires as proof leg 3 is not redundant with leg 2. `git status --short` after this run: clean.

### Plant 4 -- move the emit after the `expected == 0xFF` skip

Targets leg 4 (`test_the_emit_precedes_the_skip_continues`) RED. The guard itself (both `#ifndef`/`#endif` lines) was relocated bodily along with the if-block, so the guard membership (leg 2) is unaffected -- only the emit's position relative to the skip changes.

```
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_exists_inside_the_write_execute_body PASSED [ 10%]
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_is_inside_a_serial_on_io_guard PASSED [ 20%]
tests/test_progress_emission_is_leonardo_only.py::test_the_millis_state_variable_is_inside_the_same_guard_class PASSED [ 30%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_precedes_the_skip_continues FAILED [ 40%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_uses_the_named_interval_constant PASSED [ 50%]
tests/test_progress_emission_is_leonardo_only.py::test_the_payload_keeps_one_contract_for_the_id PASSED [ 60%]
tests/test_progress_emission_is_leonardo_only.py::test_serial_on_io_is_defined_on_exactly_the_uno_class_envs PASSED [ 70%]
tests/test_progress_emission_is_leonardo_only.py::test_scan_targets_are_non_vacuous PASSED [ 80%]
tests/test_progress_emission_is_leonardo_only.py::test_this_module_cannot_be_silently_skipped PASSED [ 90%]
tests/test_progress_emission_is_leonardo_only.py::test_own_needles_do_not_appear_verbatim_in_this_module PASSED [100%]
========================= 1 failed, 9 passed in 0.11s =========================
```

The failing assertion:
```
AssertionError: expected the MSG_DATA_PROGRESS emit's offset (7449) to be LESS than the 'expected == 0xFF' skip's offset (7220) inside eprom_internal_write_execute_body's body -- D-03: the cadence must be independent of how many bytes are skipped.
```

**Finding:** only the targeted leg (4) failed; every other leg -- including 2 and 3, since the guard moved WITH the emit -- correctly stayed GREEN. `git status --short` after this run: clean.

### Plant 5 -- replace `EPROM_PROGRESS_EMIT_INTERVAL_MS` with a bare `1000` in the predicate

Targets leg 5 (`test_the_emit_uses_the_named_interval_constant`) RED.

```
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_exists_inside_the_write_execute_body PASSED [ 10%]
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_is_inside_a_serial_on_io_guard PASSED [ 20%]
tests/test_progress_emission_is_leonardo_only.py::test_the_millis_state_variable_is_inside_the_same_guard_class PASSED [ 30%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_precedes_the_skip_continues PASSED [ 40%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_uses_the_named_interval_constant FAILED [ 50%]
tests/test_progress_emission_is_leonardo_only.py::test_the_payload_keeps_one_contract_for_the_id PASSED [ 60%]
tests/test_progress_emission_is_leonardo_only.py::test_serial_on_io_is_defined_on_exactly_the_uno_class_envs PASSED [ 70%]
tests/test_progress_emission_is_leonardo_only.py::test_scan_targets_are_non_vacuous PASSED [ 80%]
tests/test_progress_emission_is_leonardo_only.py::test_this_module_cannot_be_silently_skipped PASSED [ 90%]
tests/test_progress_emission_is_leonardo_only.py::test_own_needles_do_not_appear_verbatim_in_this_module PASSED [100%]
========================= 1 failed, 9 passed in 0.18s =========================
```

The failing assertion:
```
AssertionError: expected the emit's own time-since-last-frame comparison to use the named EPROM_PROGRESS_EMIT_INTERVAL_MS constant, found '1000' instead -- a literal would let the native cadence case and the firmware's own predicate drift apart silently.
```

**Finding:** only the targeted leg (5) failed. `git status --short` after this run: clean.

### Plant 6 -- change the emit's second argument from `handle->mem_size` to `handle->data_size`

Targets leg 6 (`test_the_payload_keeps_one_contract_for_the_id`) RED.

```
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_exists_inside_the_write_execute_body PASSED [ 10%]
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_is_inside_a_serial_on_io_guard PASSED [ 20%]
tests/test_progress_emission_is_leonardo_only.py::test_the_millis_state_variable_is_inside_the_same_guard_class PASSED [ 30%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_precedes_the_skip_continues PASSED [ 40%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_uses_the_named_interval_constant PASSED [ 50%]
tests/test_progress_emission_is_leonardo_only.py::test_the_payload_keeps_one_contract_for_the_id FAILED [ 60%]
tests/test_progress_emission_is_leonardo_only.py::test_serial_on_io_is_defined_on_exactly_the_uno_class_envs PASSED [ 70%]
tests/test_progress_emission_is_leonardo_only.py::test_scan_targets_are_non_vacuous PASSED [ 80%]
tests/test_progress_emission_is_leonardo_only.py::test_this_module_cannot_be_silently_skipped PASSED [ 90%]
tests/test_progress_emission_is_leonardo_only.py::test_own_needles_do_not_appear_verbatim_in_this_module PASSED [100%]
========================= 1 failed, 9 passed in 0.10s =========================
```

The failing assertion (the arg2-equality check, checked first):
```
AssertionError: expected the emit's second argument to be handle->mem_size (the chip's absolute geometry), found 'handle->data_size' -- D-04: 0xE0 must keep exactly one payload meaning across its two emitters; a block-relative pair would give the id a second meaning depending on which operation emitted it.
```

**Defense in depth, independently verified:** the leg's SECOND assertion (the forbidden-needle absence check, scoped to the matched emit block's own text) was also confirmed to independently catch this plant on its own -- calling the module's own extraction and regex functions directly against this plant's text (outside pytest) found exactly 1 occurrence of the forbidden needle within the emit block. Only the targeted leg (6) failed in the actual pytest run, since the first (arg2-equality) assertion stops the test before reaching the second. `git status --short` after this run: clean.

### Plant 7a -- `platformio.ini` scratch copy: add `-D SERIAL_ON_IO` to the `leonardo` env

Targets leg 7 (`test_serial_on_io_is_defined_on_exactly_the_uno_class_envs`) RED, direction 1 of 2.

```
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_exists_inside_the_write_execute_body PASSED [ 10%]
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_is_inside_a_serial_on_io_guard PASSED [ 20%]
tests/test_progress_emission_is_leonardo_only.py::test_the_millis_state_variable_is_inside_the_same_guard_class PASSED [ 30%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_precedes_the_skip_continues PASSED [ 40%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_uses_the_named_interval_constant PASSED [ 50%]
tests/test_progress_emission_is_leonardo_only.py::test_the_payload_keeps_one_contract_for_the_id PASSED [ 60%]
tests/test_progress_emission_is_leonardo_only.py::test_serial_on_io_is_defined_on_exactly_the_uno_class_envs FAILED [ 70%]
tests/test_progress_emission_is_leonardo_only.py::test_scan_targets_are_non_vacuous PASSED [ 80%]
tests/test_progress_emission_is_leonardo_only.py::test_this_module_cannot_be_silently_skipped PASSED [ 90%]
tests/test_progress_emission_is_leonardo_only.py::test_own_needles_do_not_appear_verbatim_in_this_module PASSED [100%]
========================= 1 failed, 9 passed in 0.10s =========================
```

The failing assertion:
```
AssertionError: expected the Uno-class build flag on exactly the uno and uno328pb env sections of platformio.ini and on no other env (leonardo and every native* env included), found it on: ['leonardo', 'uno', 'uno328pb'] -- D-06's non-claim ("delivered on leonardo only") is false the moment an env gains or loses this flag; this leg is what keeps that non-claim honest against a future platformio.ini edit in EITHER direction.
```

**Finding:** only the targeted leg (7) failed. `git status --short` after this run: clean.

### Plant 7b -- `platformio.ini` second scratch copy: remove `-D SERIAL_ON_IO` from `uno328pb`

Targets leg 7 RED again, direction 2 of 2 -- the other direction D-06's non-claim can be falsified from.

```
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_exists_inside_the_write_execute_body PASSED [ 10%]
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_is_inside_a_serial_on_io_guard PASSED [ 20%]
tests/test_progress_emission_is_leonardo_only.py::test_the_millis_state_variable_is_inside_the_same_guard_class PASSED [ 30%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_precedes_the_skip_continues PASSED [ 40%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_uses_the_named_interval_constant PASSED [ 50%]
tests/test_progress_emission_is_leonardo_only.py::test_the_payload_keeps_one_contract_for_the_id PASSED [ 60%]
tests/test_progress_emission_is_leonardo_only.py::test_serial_on_io_is_defined_on_exactly_the_uno_class_envs FAILED [ 70%]
tests/test_progress_emission_is_leonardo_only.py::test_scan_targets_are_non_vacuous PASSED [ 80%]
tests/test_progress_emission_is_leonardo_only.py::test_this_module_cannot_be_silently_skipped PASSED [ 90%]
tests/test_progress_emission_is_leonardo_only.py::test_own_needles_do_not_appear_verbatim_in_this_module PASSED [100%]
========================= 1 failed, 9 passed in 0.16s =========================
```

The failing assertion:
```
AssertionError: expected the Uno-class build flag on exactly the uno and uno328pb env sections of platformio.ini and on no other env (leonardo and every native* env included), found it on: ['uno'] -- D-06's non-claim ("delivered on leonardo only") is false the moment an env gains or loses this flag; this leg is what keeps that non-claim honest against a future platformio.ini edit in EITHER direction.
```

**Finding:** only the targeted leg (7) failed, in the OTHER direction from plant 7a -- one assertion (a set-equality check) catches both directions, exactly as D-25 requires. `git status --short` after this run: clean.

### Plant 8a -- point the eprom seam at an EMPTY scratch file

Targets the non-vacuity self-protection leg (8) specifically.

```
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_exists_inside_the_write_execute_body FAILED [ 10%]
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_is_inside_a_serial_on_io_guard FAILED [ 20%]
tests/test_progress_emission_is_leonardo_only.py::test_the_millis_state_variable_is_inside_the_same_guard_class FAILED [ 30%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_precedes_the_skip_continues FAILED [ 40%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_uses_the_named_interval_constant FAILED [ 50%]
tests/test_progress_emission_is_leonardo_only.py::test_the_payload_keeps_one_contract_for_the_id FAILED [ 60%]
tests/test_progress_emission_is_leonardo_only.py::test_serial_on_io_is_defined_on_exactly_the_uno_class_envs PASSED [ 70%]
tests/test_progress_emission_is_leonardo_only.py::test_scan_targets_are_non_vacuous FAILED [ 80%]
tests/test_progress_emission_is_leonardo_only.py::test_this_module_cannot_be_silently_skipped PASSED [ 90%]
tests/test_progress_emission_is_leonardo_only.py::test_own_needles_do_not_appear_verbatim_in_this_module PASSED [100%]
========================= 7 failed, 3 passed in 0.14s =========================
```

**Finding, stated honestly (a stronger result than the minimum asked for, mirroring plan 143-03's own Plant 8 finding for the exact same reason): this plant turns leg 8 RED, PLUS legs 1, 2, 3, 4, 5 and 6 -- all seven share the same `_extract_write_execute_body` helper, whose own internal "exactly 1 definition" assertion fires FIRST and LOUDEST**, before leg 8's own explicit non-empty-body check is even reached:
```
AssertionError: expected exactly 1 definition of static void eprom_internal_write_execute_body(firestarter_handle_t* handle) in the comment-stripped src/proms/eprom.cpp, found 0 -- this is a source-contract claim (see module docstring): BF-2's guard can only be pinned if there is exactly one function body to pin.
```
Leg 7 (`platformio.ini`, an unrelated file, unaffected by this seam) and legs 9/10 (self-checks reading only this module's own source) correctly stayed GREEN. `git status --short` after this run: clean.

### Plant 8b -- point the eprom seam at a scratch file with the real function signature but an EMPTY body

Targets leg 8 RED again, this time on its OWN non-empty-body assertion specifically (not the shared extractor's).

```
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_exists_inside_the_write_execute_body FAILED [ 10%]
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_is_inside_a_serial_on_io_guard FAILED [ 20%]
tests/test_progress_emission_is_leonardo_only.py::test_the_millis_state_variable_is_inside_the_same_guard_class FAILED [ 30%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_precedes_the_skip_continues FAILED [ 40%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_uses_the_named_interval_constant FAILED [ 50%]
tests/test_progress_emission_is_leonardo_only.py::test_the_payload_keeps_one_contract_for_the_id FAILED [ 60%]
tests/test_progress_emission_is_leonardo_only.py::test_serial_on_io_is_defined_on_exactly_the_uno_class_envs PASSED [ 70%]
tests/test_progress_emission_is_leonardo_only.py::test_scan_targets_are_non_vacuous FAILED [ 80%]
tests/test_progress_emission_is_leonardo_only.py::test_this_module_cannot_be_silently_skipped PASSED [ 90%]
tests/test_progress_emission_is_leonardo_only.py::test_own_needles_do_not_appear_verbatim_in_this_module PASSED [100%]
========================= 7 failed, 3 passed in 0.13s =========================
```

Leg 8's own specific failing assertion this time (the shared extractor did NOT raise -- the signature was found exactly once, and the brace-matcher successfully returned an empty body):
```
AssertionError: the extracted eprom_internal_write_execute_body (from the CURRENT scan target .../plant8b_empty_body.cpp) is empty -- a brace-matcher that silently returns an empty body would make every positive-presence leg in this module (Coverage 1-6) fail to find anything to check.
```

**Finding:** confirms the plan's precise expectation -- "leg 8 RED again on the non-empty-body assertion" (leg 8's OWN assertion, not the shared extractor's internal one, since this time the extraction itself succeeds). Legs 1-6 again show honest spillover (same shared-body-is-empty root cause, each failing on its OWN "found 0" check against an empty body). `git status --short` after this run: clean.

### Final GREEN (no env seam set; real source; working tree confirmed clean throughout the whole campaign)

```
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_exists_inside_the_write_execute_body PASSED [ 10%]
tests/test_progress_emission_is_leonardo_only.py::test_the_progress_emit_is_inside_a_serial_on_io_guard PASSED [ 20%]
tests/test_progress_emission_is_leonardo_only.py::test_the_millis_state_variable_is_inside_the_same_guard_class PASSED [ 30%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_precedes_the_skip_continues PASSED [ 40%]
tests/test_progress_emission_is_leonardo_only.py::test_the_emit_uses_the_named_interval_constant PASSED [ 50%]
tests/test_progress_emission_is_leonardo_only.py::test_the_payload_keeps_one_contract_for_the_id PASSED [ 60%]
tests/test_progress_emission_is_leonardo_only.py::test_serial_on_io_is_defined_on_exactly_the_uno_class_envs PASSED [ 70%]
tests/test_progress_emission_is_leonardo_only.py::test_scan_targets_are_non_vacuous PASSED [ 80%]
tests/test_progress_emission_is_leonardo_only.py::test_this_module_cannot_be_silently_skipped PASSED [ 90%]
tests/test_progress_emission_is_leonardo_only.py::test_own_needles_do_not_appear_verbatim_in_this_module PASSED [100%]
============================== 10 passed in 0.07s ==============================
```
`git status --short` and `git diff --exit-code`: both clean/silent. Every plant was made on a scratch copy; the committed `src/proms/eprom.cpp` and `platformio.ini` were never touched.

**No leg required a locator-only repair.** Every leg was reachable and produced exactly its intended RED (or an honest, documented spillover onto legs sharing the same extraction helper) on the FIRST attempt across all 10 plants.

## Verification Results (final state)

| Check | Result |
|---|---|
| `python3 -m pytest tests/test_progress_emission_is_leonardo_only.py -v -o addopts=""` (no env seam) | **10 passed** |
| `python3 -m pytest tests/ -o addopts="" -q` (post-commit, per L-1/S-8) | **292 passed** (282 baseline + 10 new) |
| `pytest tests/test_hv_routing_source_contract_v142.py tests/test_write_path_source_contract_v131.py tests/test_ack_layout_source_contract_v143.py tests/test_protocol_branch_inventory.py -o addopts=""` | **45 passed** -- all named "must stay green" modules confirmed unbroken |
| `pio run -e uno` (cold) | SUCCESS; RAM 76.8% (1573/2048 B); Flash 77.0% (24824/32256 B) -- **byte-identical to post-143-05** |
| `pio run -e uno328pb` (cold) | SUCCESS; RAM 77.1% (1579/2048 B); Flash 76.8% (24874/32384 B) -- **byte-identical to post-143-05** |
| `pio run -e leonardo` (cold) | SUCCESS; RAM 78.7% (2014/2560 B); Flash 93.8% (26906/28672 B, **1766 B headroom**) -- **byte-identical to post-143-05** |
| `python3 scripts/check_build_warnings.py --rebuild` (COLD -- native/native_nodevtools `.pio/build` removed first, not reused warm) | `PASS`: uno/uno328pb/leonardo macro_redefinition=0; native/native_nodevtools total warnings=1166 (== watermark 1166) -- **unmoved** |
| `git status --porcelain` (after the full D-25 campaign) | clean |
| `git status --short` in `/workspaces/firestarter_app` | not applicable this plan -- firmware submodule only (D-01) |

## Issues Encountered

- **The plan's own acceptance-criteria parenthetical names the bare `SERIAL_ON_IO` token as a "forbidden-direction needle," which is unregisterable as written** -- resolved by registering a narrower, compiler-invocation-prefixed composite instead. Full reasoning in Decisions Made; the collision was caught empirically (Deviations #1) before any commit, not reasoned away in the abstract.
- **A whole-body forbidden-needle scope for Coverage 6 would have false-positived against the real source** (`handle->data_size` legitimately appears twice elsewhere in the same function). Caught during authoring, before the module was ever run; the shipped module scopes the check to the matched emit block only. No incident occurred against the real source because this was fixed before the first run.
- No other issues. No `native_*_v131` env was passed to either baseline script (F-138-05 avoided by construction -- neither script was invoked with any such env name).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- BF-2 is closed as a source contract: the Uno-class non-delivery of intra-block write progress is now mechanically pinned against regression in either direction (an unguarded emission regressing HOST-03, or a `platformio.ini` edit silently widening/narrowing the guard's scope), with the explicit, repeated caveat that this is source-contract evidence, never behavioural evidence -- no native environment can prove Uno-class delivery either way, and this SUMMARY does not claim otherwise.
- **D-06's non-claim, both dimensions, restated for the phase record:** intra-block write progress is emitted on the EPROM path only (not flash/EEPROM/SRAM -- a deferred idea with no owner in this milestone, per `143-CONTEXT.md`'s own Deferred Ideas list), and delivered on `leonardo` only (compiled out on `uno`/`uno328pb` -- now mechanically enforced by this plan's Coverage 7 leg, in both directions).
- **Real bar motion during a real long write on hardware is Phase 145's and is not claimed here.** This plan's evidence is entirely off-hardware (a source scan plus three cold AVR builds); no bench claim of any kind is made.
- This plan intentionally marks no requirement Complete (frontmatter `requirements: []`); plan 143-10 flips the `HOST-*` checkboxes once every plan's evidence exists.
- `native_trace_v131` was neither run as evidence nor re-frozen (D-24); this plan touches no firmware source, so there was nothing for that fixture to newly prove or disprove.
- **Flash headroom unchanged:** this plan spent 0 B on all three AVR targets (test-file-only change). `leonardo` still has the same **1766 B** of headroom plan 143-05 left behind -- no further firmware plan remains in this phase to consume it.
- `check_size_baseline.py`'s flash-growth RED and `native_trace_v131`'s RED both remain exactly as recorded and operator-accepted; neither is this plan's or this phase's to fix (Phase 144/TEST-06, TEST-08).
- No blockers. All pinned artifacts this plan must not touch (`scripts/baseline/size_baseline.json`, `platformio.ini` itself, every other test module, every firmware source file) are confirmed untouched by `git diff --exit-code`.

## Self-Check: PASSED

- FOUND: `firestarter/tests/test_progress_emission_is_leonardo_only.py` (created)
- FOUND commit `9349fce` (Task 1)

---
*Phase: 143-host-timeout-progress-pulse-override*
*Completed: 2026-08-13*
