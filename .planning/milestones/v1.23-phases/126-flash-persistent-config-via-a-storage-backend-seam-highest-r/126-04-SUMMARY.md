---
phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r
plan: 04
subsystem: firmware/avr size-measurement gate
tags: [avr, size-baseline, non-regression, config-storage, measurement]

# Dependency graph
requires:
  - phase: 126-03
    provides: "the atomic AVR split (include/rurp_config_storage.h + src/rurp_config_utils.cpp policy-only + src/boards/rurp_config_storage_eeprom.cpp AVR backend), the only point at which an AVR size delta is attributable to the policy split alone"
provides:
  - "CFG-04's measurement half: all three AVR targets (uno, uno328pb, leonardo) measured cold, flash AND RAM, immediately after the split and before any ARM work — every figure byte-identical to the pre-existing size_baseline.json"
  - "Both named comparators run and recorded against their own baseline files: compare_avr (strict) against the live size_baseline.json, compare_avr_policy_merge05 (A-5 band) against the frozen size_baseline_base01.json — both PASS, exit 0"
  - "Disposition Arm A taken and recorded: the zero delta is a measured result with its mechanism (-flto + --gc-sections) and its structural attribution (D-03: the dual-slot core lives under platform/py32f071/src/, so zero new bytes reach any AVR build from it) — no re-baseline commit made, none needed"
affects: [126-12]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Cold-build measurement discipline: pio run -t clean -e <env> then pio run -e <env> as one uninterrupted invocation with an extended (>=540000ms) timeout, per size_baseline.json's own meta.note, run twice this plan (once without an explicit extended timeout for a quick read, then re-run explicitly with the 540000ms timeout to satisfy the acceptance criteria's literal wording) — both runs reproduced byte-identical figures"

key-files:
  created: []
  modified: []

key-decisions:
  - "Arm A taken: every AVR flash/RAM figure across uno, uno328pb, leonardo is byte-identical to the recorded live baseline. No file was modified by this plan. scripts/baseline/size_baseline.json's blob SHA is unchanged (9cc5204bb437735d77523e62512c1d2cadfc668f) and no re-baseline commit was created."
  - "The measurement was re-run a second time with an explicit >=540000ms Bash timeout (even though the first pass already completed in ~1-2s per env) to satisfy the plan's literal acceptance-criteria wording that the invocation carry that timeout value, not merely complete quickly. Both passes produced byte-identical RAM/Flash figures and object-file presence."
  - "No commit was made in the firmware repo by this plan (Arm A requires none); only this SUMMARY + STATE/ROADMAP land in the meta repo."

requirements-completed: []  # CFG-04 completes structurally at this plan's measurement, but per 126-CONTEXT.md/126-RESEARCH.md only Plan 126-12 may tick CFG-01..CFG-07 in REQUIREMENTS.md. This plan ticks NOTHING.

coverage:
  - id: D1
    description: "All three AVR targets (uno, uno328pb, leonardo) built cold (clean + build, single invocation, >=540000ms timeout) with the new src/boards/rurp_config_storage_eeprom.cpp.o backend translation unit confirmed present in each build output"
    requirement: "CFG-04"
    verification:
      - kind: unit
        ref: "pio run -t clean -e uno && pio run -e uno (and uno328pb, leonardo) -- all exit 0; .pio/build/<env>/src/boards/rurp_config_storage_eeprom.cpp.o confirmed present for all three"
        status: pass
    human_judgment: false
  - id: D2
    description: "Both named comparators (compare_avr strict against the live baseline; compare_avr_policy_merge05 band against the frozen BASE-01 baseline) run against the three cold build logs and recorded PASS with exit 0"
    requirement: "CFG-04"
    verification:
      - kind: unit
        ref: "python3 scripts/check_size_baseline.py --avr-log uno=... --avr-log uno328pb=... --avr-log leonardo=...; python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log ...=..."
        status: pass
    human_judgment: false
  - id: D3
    description: "Warning gate (check_build_warnings.py) run for all three AVR logs, each reporting macro_redefinition=0 (== 0)"
    requirement: "CFG-04"
    verification:
      - kind: unit
        ref: "python3 scripts/check_build_warnings.py --log uno=... (and uno328pb, leonardo) -- all PASS exit 0"
        status: pass
    human_judgment: false
  - id: D4
    description: "Disposition recorded: Arm A (measured zero) with its mechanism and structural attribution; no baseline file touched; both comparator-script and frozen-baseline blob SHAs unchanged; ARM non-claim recorded; pytest tests/ at 102, both native envs at 141/17"
    requirement: "CFG-04"
    verification:
      - kind: unit
        ref: "git hash-object confirms unchanged SHAs; python3 -m pytest tests/ -q -> 102 passed; pio test -e native / -e native_nodevtools -> 141/141/17 both"
        status: pass
    human_judgment: false

duration: ~25min
completed: 2026-07-31
status: complete
---

# Phase 126 Plan 04: AVR Flash/RAM Size Measurement (CFG-04 Measurement Half) Summary

**Measured AVR flash and RAM cold on all three targets (uno, uno328pb, leonardo) immediately after Plan 126-03's policy-split, found every figure byte-identical to the pre-existing baseline under both named comparators, and recorded the zero delta as Arm A (measured, not assumed) with its `-flto`+`--gc-sections` mechanism and D-03's structural attribution — no re-baseline commit needed.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-07-31T23:15:00Z
- **Tasks:** 2/2 completed
- **Files modified:** 0 (measurement and comparison only; no re-baseline was needed)

## Accomplishments

- **Pre-measurement blob SHAs recorded and confirmed unchanged at end of plan:**
  - `scripts/check_size_baseline.py` — `94adba22cc99b8c8e1b757f2127eb4ebd38b0853` (the plan's read-order did not specify an expected value for this file, only that it must not change across the plan — confirmed identical before and after).
  - `scripts/baseline/size_baseline.json` (live) — `9cc5204bb437735d77523e62512c1d2cadfc668f` (matches the expected value from the plan's `read_first`).
  - `scripts/baseline/size_baseline_base01.json` (frozen BASE-01) — `b940c91655600a57ad7ef67cba723943af929daf` (matches the expected value; Phase 124's immutable MERGE-05 reference).
- **Three cold AVR builds, each `pio run -t clean -e <env>` (confirmed completed, exit 0) followed by `pio run -e <env>` as one uninterrupted invocation with an explicit 540000ms timeout, exit 0 for all three.** Re-run twice (once with an implicit shorter timeout for a fast initial read, once explicitly with the >=540000ms timeout per the acceptance criteria's literal wording) — both passes produced byte-identical figures, confirming no truncation/warm-tree contamination in either pass.
- **`RAM:`/`Flash:` lines, verbatim, and the new backend object file confirmed present, for all three envs:**

  | env | `RAM:` line (verbatim) | `Flash:` line (verbatim) | Object file present |
  |---|---|---|---|
  | uno | `RAM:   [========  ]  76.8% (used 1573 bytes from 2048 bytes)` | `Flash: [=======   ]  74.3% (used 23954 bytes from 32256 bytes)` | `.pio/build/uno/src/boards/rurp_config_storage_eeprom.cpp.o` — present |
  | uno328pb | `RAM:   [========  ]  77.1% (used 1579 bytes from 2048 bytes)` | `Flash: [=======   ]  74.1% (used 24004 bytes from 32384 bytes)` | `.pio/build/uno328pb/src/boards/rurp_config_storage_eeprom.cpp.o` — present |
  | leonardo | `RAM:   [========  ]  78.7% (used 2014 bytes from 2560 bytes)` | `Flash: [========= ]  90.7% (used 26016 bytes from 28672 bytes)` | `.pio/build/leonardo/src/boards/rurp_config_storage_eeprom.cpp.o` — present |

- **Comparator 1 — `compare_avr` (strict byte-identity), default mode, against the LIVE `scripts/baseline/size_baseline.json`:**
  ```
  $ python3 scripts/check_size_baseline.py --avr-log uno=<log> --avr-log uno328pb=<log> --avr-log leonardo=<log>
  PASS: uno(flash=23954/32256,ram=1573/2048), uno328pb(flash=24004/32384,ram=1579/2048), leonardo(flash=26016/28672,ram=2014/2560)
  ```
  Exit code: **0**.
- **Comparator 2 — `compare_avr_policy_merge05` (the A-5 band), against the FROZEN `scripts/baseline/size_baseline_base01.json`, `--baseline` passed explicitly:**
  ```
  $ python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log uno=<log> --avr-log uno328pb=<log> --avr-log leonardo=<log>
  PASS: uno(flash=23954/32256[+22<=64],ram=1573/2048[=]), uno328pb(flash=24004/32384[+28<=64],ram=1579/2048[=]), leonardo(flash=26016/28672[-56<=0],ram=2014/2560[=])
  ```
  Exit code: **0**. These `+22`/`+28`/`-56` deltas are versus the frozen BASE-01 pre-landing figures (Phase 124's own recorded MERGE-05 deltas) — they are **unchanged from what `size_baseline.json`'s own `deltas_vs_base01` block already recorded**, which is exactly the evidence that Plan 126-03's split contributed **zero additional** bytes on top of Phase 124's landing.
- **Warning gate, all three envs, each exit 0:**
  ```
  PASS: uno: macro_redefinition=0 (== 0)
  PASS: uno328pb: macro_redefinition=0 (== 0)
  PASS: leonardo: macro_redefinition=0 (== 0)
  ```
- **A-5 rule, stated as written:** Leonardo flash must not grow (band = 0); Uno-class flash growth <= 64 B, recorded; RAM strict on all three. **Live headroom: leonardo 2656 B, uno 8302 B, uno328pb 8380 B** — `126-CONTEXT.md`'s "2600 B" figure for leonardo is stale; this measurement uses the correct 2656 B (matching `126-RESEARCH.md` and `126-01-SUMMARY.md`'s pre-phase pin).
- **Delta table** (recorded figure = `scripts/baseline/size_baseline.json`'s `avr_targets` block; observed = this plan's cold-build figures):

  | env | recorded flash used/total | observed flash used/total | flash delta | recorded RAM used/total | observed RAM used/total | RAM delta |
  |---|---|---|---|---|---|---|
  | uno | 23954/32256 | 23954/32256 | **0** | 1573/2048 | 1573/2048 | **0** |
  | uno328pb | 24004/32384 | 24004/32384 | **0** | 1579/2048 | 1579/2048 | **0** |
  | leonardo | 26016/28672 | 26016/28672 | **0** | 2014/2560 | 2014/2560 | **0** |

  No env's flash_total or ram_total changed — a changed total would mean the board or framework moved and would be a finding, not a pass; none occurred.

## Task Commits

**No commits were made in the firmware repo by this plan.** Both tasks are measurement-only (Task 1) and disposition-recording-only (Task 2); Arm A (every delta is zero) requires no re-baseline commit and no code change. `git status --porcelain` in `/workspaces/firestarter` is 0 lines throughout.

**Plan metadata:** (this SUMMARY commit, to follow, in the meta repo)

## Files Created/Modified

None in the firmware repo. This SUMMARY (and the corresponding STATE.md/ROADMAP.md/REQUIREMENTS.md updates) are the only artifacts this plan produces, all in the meta repo.

## Decisions Made

- **Arm A taken** (see Task 2's disposition below) — the zero delta is recorded as measured, with its mechanism and structural attribution, rather than assumed inevitable.
- **The cold-build measurement was performed twice**, the second time with an explicit `>=540000ms` Bash timeout, to satisfy the plan's literal acceptance-criteria wording even though the environment's toolchain is already warm-cached and each build completed in ~1.3–1.7 seconds regardless of the timeout ceiling. Both passes are recorded because they independently confirm the figures are stable, not an artifact of one particular invocation's timing.

## D-03/D-04 Attribution Argument (why this measurement is attributable to the policy split alone)

Per `126-CONTEXT.md` D-03 and `126-RESEARCH.md`'s Pitfall 5: the dual-slot py32 core (`platform/py32f071/src/config_storage_dualslot.cpp` etc.) does not exist yet — it lands in Plan 126-07, two waves after this one — so **zero new bytes could reach any AVR build from ARM-only code that has not been written**. The only AVR-compiled change in flight at this measurement point is Plan 126-03's split of `src/rurp_config_utils.cpp` into a policy-only TU plus the new `src/boards/rurp_config_storage_eeprom.cpp` backend, both already linked into every AVR target before this plan ran. This is the ROADMAP's load-bearing internal ordering (AVR move first, ARM backend second) working as designed: a delta measured here is unambiguously attributable to the split, and none fired.

## Disposition: Arm A — every delta is zero (flash and RAM, all three envs)

Both comparators exited 0 (see verbatim output above). The result is recorded as **measured**, not assumed:

- **Observed figures are byte-identical to the recorded baseline** for all three envs, both flash and RAM (see the delta table above — every delta column reads 0).
- **The mechanism that makes a zero plausible:** `-flto` (link-time optimization) plus `--gc-sections` (dead-code/section garbage collection), the same mechanism `125-NONREGRESSION.md` recorded for the VPP seam's measured 0 B flash / 0 B RAM precedent. Splitting one translation unit into two and adding a `bool` return type to each of the two new seam functions can, in principle, move bytes even under this optimization — but here it did not, because the split is a pure move (per Plan 126-03's SUMMARY: `rurp_validate_config`'s body is byte-for-byte unchanged, and the AVR backend's `EEPROM.get`/`.put` calls are unconditional `true`-returning wrappers around the exact same `CONFIG_START 48` / `sizeof(rurp_configuration_t)` access pattern that existed pre-split).
- **The structural reason the result is attributable:** the policy split moved code between two translation units that are **both already linked into every AVR target** (the policy layer was always compiled; the new backend TU is unconditionally compiled by every AVR env's wholesale `src/` compilation, per `platformio.ini`'s lack of a `build_src_filter` on the AVR envs). D-03 placed the ARM-only dual-slot core under `platform/py32f071/src/`, which is not yet authored and, when it is (Plan 126-07), will never reach any AVR build by construction — so this measurement's zero result is the expected and now-confirmed outcome of a pure-move refactor, not a coincidence.
- **The baseline JSON was NOT edited in this arm.** Confirmed: `git hash-object scripts/baseline/size_baseline.json` is still `9cc5204bb437735d77523e62512c1d2cadfc668f` (identical before and after all measurement work).
- **No commit was made in this task.**

## ARM Non-Claim

**No ARM flash or RAM figure of any kind is claimed by this plan.** `arm-none-eabi-gcc`, `cmake` and `ninja` are absent from this devcontainer; ARM flash and RAM are unmeasurable locally. `FUT-ARMSIZE` (checking ARM sizes into a baseline with a RAM ceiling) remains a deferred item — CI already runs `arm-none-eabi-size` (per `py32f071.yml`) but only into a job log where a multi-kilobyte regression would pass unnoticed. This plan measures **AVR only**, per `.planning/REQUIREMENTS.md` §"Validation Ceiling".

## Re-run confirmation (both frozen references and the full suite)

- `git hash-object scripts/baseline/size_baseline_base01.json` → `b940c91655600a57ad7ef67cba723943af929daf` — **unchanged**, confirmed at end of plan. Phase 124's frozen MERGE-05 reference; this phase never touches it.
- `git hash-object scripts/check_size_baseline.py` → `94adba22cc99b8c8e1b757f2127eb4ebd38b0853` — **unchanged** from the value recorded at the start of Task 1. No tolerance was widened; the comparator script was never edited.
- `python3 -m pytest tests/ -q` → **102 passed** — identical to Plan 126-03's end state (no test added or removed by this plan).
- `pio test -e native` → **141 test cases: 141 succeeded**, **17 suites**.
- `pio test -e native_nodevtools` → **141 test cases: 141 succeeded**, **17 suites**.
- `git status --porcelain` for `/workspaces/firestarter` → **0 lines** at the end of the plan (repo: `firestarter`).
- `git rev-parse --abbrev-ref HEAD` in the firmware repo → `v1.23-py32f071-integration`. In the meta repo → `gsd/v1.23-py32f071-integration`. Both re-checked after every measurement pass (no commit occurred in the firmware repo, but the branch was re-verified per RESEARCH Pitfall 7's standing discipline regardless).
- Both gitignored py32 worktrees (`firestarter_py32_ci`, `firestarter_app_py32`) — `git status --porcelain` returns 0 lines in each; neither was written to.
- No requirement checkbox in `.planning/REQUIREMENTS.md` was ticked (`git status --porcelain -- .planning/REQUIREMENTS.md` — 0 lines). Only Plan 126-12 may tick CFG-01…CFG-07.

## Deviations from Plan

None — plan executed exactly as written. The only elaboration beyond the plan's literal text: the cold-build measurement was performed a second time with an explicit `>=540000ms` Bash timeout parameter (the first pass had already succeeded quickly without an explicit timeout override), purely to satisfy the acceptance criteria's literal wording that the invocation carry that timeout value. Both passes agree byte-for-byte on every figure, so this is not a correction of any kind, just an extra confirmation pass.

## Issues Encountered

None. Every measurement matched the expected baseline on the first attempt of both passes; no STOP finding, no Arm B path was needed.

## Next Phase Readiness

- CFG-04's measurement half is discharged: the AVR side of the policy split cost zero bytes, cold-measured under both named comparators, with the new backend TU confirmed present in every build. Plan 126-05 (CFG-03's structural seam-shape gate, same wave) can proceed independently.
- Plan 126-06 (Wave 4, the linker/flash-map work) can now proceed knowing the AVR baseline has zero pending delta from this phase's earlier work — any AVR change measured after this point is attributable to whatever plan makes it, not to a carried-over 126-03/126-04 delta.
- No blockers.

---
*Phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r*
*Completed: 2026-07-31*

## Self-Check: PASSED

- FOUND: `.planning/phases/126-flash-persistent-config-via-a-storage-backend-seam-highest-r/126-04-SUMMARY.md`
- CONFIRMED: `scripts/baseline/size_baseline.json` blob SHA unchanged (`9cc5204bb437735d77523e62512c1d2cadfc668f`)
- CONFIRMED: `scripts/baseline/size_baseline_base01.json` blob SHA unchanged (`b940c91655600a57ad7ef67cba723943af929daf`)
- CONFIRMED: `scripts/check_size_baseline.py` blob SHA unchanged (`94adba22cc99b8c8e1b757f2127eb4ebd38b0853`)
- CONFIRMED: three AVR build logs reproduced byte-identical figures across two independent measurement passes
- CONFIRMED: `git status --porcelain` in `/workspaces/firestarter` is 0 lines
- No missing items. No firmware-repo commit exists for this plan (Arm A requires none).
