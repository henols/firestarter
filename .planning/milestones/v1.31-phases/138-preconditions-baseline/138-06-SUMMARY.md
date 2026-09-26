---
phase: 138-preconditions-baseline
plan: 06
subsystem: infra
tags: [platformio, size-baseline, flash-ram, native-tests, cold-measurement, check-size-baseline, check-build-warnings, ci-gates]

# Dependency graph
requires:
  - phase: 138-05
    provides: "native_trace_v131 env + the frozen EPROM_V131_TRACE_PROTO_07/_08/_0B fixture (5 test cases, 1 suite) that this plan measures cold alongside the three pre-existing native envs"
provides:
  - "Cold PREP-03 firmware baseline: per-target flash/RAM for uno/uno328pb/leonardo and case/suite/warning counts for all four native envs, each figure beside the exact command that produced it"
  - "firestarter/scripts/baseline/size_baseline_v131.json — an immutable v1.31 freeze in BASE-01's schema, with two delta blocks (deltas_vs_base01, deltas_vs_size_baseline) and all four native envs, verified green through check_size_baseline.py's/check_build_warnings.py's existing --baseline seam"
  - "F-138-04 (size gate GREEN at the decided fork base, RED at the live beta tip +34B/target — research-measured, not re-built) and F-138-05 (check_size_baseline.py's unknown-env KeyError exits 1 where its own taxonomy promises 2; NATIVE_ENVS hardcoded makes native_trace_v131 invisible to both live gates) — both recorded with owners, neither checker modified"
affects: [Phase 144 TEST-08 (compares its post-change flash/RAM/suite-count delta against this freeze via --baseline), 138-07 (discharges PREP-03 itself using this plan's firmware-half evidence)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Cold-measurement discipline (rm -rf .pio/build/<env> or pio run -t clean, then a single invocation, 540000ms timeout) applied for the second time this phase, this time across all three AVR targets and all four native envs in one measurement pass"
    - "Two delta blocks in one freeze file (deltas_vs_base01, deltas_vs_size_baseline) because BASE-01 and the live baseline disagree with each other (+22/+28/-56) even though this measurement agrees with the live baseline exactly (delta zero) — stated as a measured fact, not forced into a single-delta narrative"
    - "D-07-class finding recorded with owner and an explicit non-fix, applied a third and fourth time this phase (after F-138-02/F-138-03 in 138-01): F-138-04 (base-dependent gate verdict) and F-138-05 (unknown-env KeyError vs its own exit-2 taxonomy)"
    - "Read-only defect reproduction as evidence: the KeyError and the sibling checker's clean exit-2 message were both deliberately reproduced against the live gates, quoted verbatim, and never used to gate this plan's own pass/fail status"

key-files:
  created:
    - firestarter/scripts/baseline/size_baseline_v131.json
    - .planning/phases/138-preconditions-baseline/138-06-FIRMWARE-MEASUREMENT.md
  modified: []

key-decisions:
  - "Combined Task 1 (measurement tables) and Task 3 (Findings + closing section) into ONE meta commit for 138-06-FIRMWARE-MEASUREMENT.md, per the plan's own explicit repo_topology instruction ('meta for 138-06-FIRMWARE-MEASUREMENT.md ... Two repos, two commits') — the same amend-for-single-commit precedent 138-05 established, applied here without needing an amend because both tasks wrote to the same untracked file before either was committed"
  - "Passed native_pinmap_provisional to both check_size_baseline.py and check_build_warnings.py as a supplementary run beyond the plan's explicitly-named native/native_nodevtools pair, because the plan's own 'pass it only if present' rule licenses it and the live baseline carries its key in both native_envs and warnings.native — recorded as supplementary evidence, not a replacement for the primary named run"
  - "Deliberately did not rebuild the live beta tip (6fab4ea) for F-138-04 — quoted 138-RESEARCH.md's figure verbatim, explicitly labelled research-measured, because a second cold 3-target AVR rebuild against a tree this phase does not fork from would spend a 9-minute-class toolchain invocation to learn nothing D-07 permits acting on"

requirements-completed: []

# Coverage metadata
coverage:
  - id: D1
    description: "Per-target flash and RAM for uno, uno328pb and leonardo measured cold (clean + single pio run, 540000ms timeout) and recorded beside the exact command; all three byte-identical to the live baseline's own figures, confirming the plan 138-03/138-05 trace instrumentation is AVR-invisible"
    verification:
      - kind: integration
        ref: "pio run -t clean -e {uno,uno328pb,leonardo} && pio run -e {uno,uno328pb,leonardo} -- RAM/Flash pairs 1573/23954, 1579/24004, 2014/26016 (bytes used), each log ending [SUCCESS]"
        status: pass
      - kind: other
        ref: "check_size_baseline.py default-seam run against the live baseline with all three AVR logs + native + native_nodevtools -- PASS, exit 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "Case and suite counts measured cold for all four native envs; native/native_nodevtools still read 141 cases across 17 suites with HOST_STUBS_RECORD_TIMING present but undefined for every pre-existing suite"
    verification:
      - kind: integration
        ref: "rm -rf .pio/build/<env> && pio test -e <env> for native (141/17), native_nodevtools (141/17), native_pinmap_provisional (10/1), native_trace_v131 (5/1), all all_passed=true"
        status: pass
      - kind: other
        ref: "case/suite counts independently re-derived via check_size_baseline.py's own CASES_RE/SUITE_RE regexes against the raw logs, matching the summary-table figures exactly"
        status: pass
    human_judgment: false
  - id: D3
    description: "Immutable size_baseline_v131.json committed beside BASE-01 in the firestarter submodule; live size_baseline.json and BASE-01 byte-for-byte untouched; freeze independently verified green through check_size_baseline.py --baseline and check_build_warnings.py --baseline"
    verification:
      - kind: unit
        ref: "python3 -c \"...schema assertions...\" -- schema ok; len(avr_targets)==3; len(native_envs)==4; fork_base != measured_at_tree"
        status: pass
      - kind: integration
        ref: "check_size_baseline.py --baseline scripts/baseline/size_baseline_v131.json (+ 3 AVR logs + native + native_nodevtools[+ native_pinmap_provisional]) -- PASS, exit 0; check_build_warnings.py --baseline scripts/baseline/size_baseline_v131.json (+ 6 logs) -- PASS, exit 0"
        status: pass
      - kind: other
        ref: "git diff --quiet -- scripts/baseline/size_baseline.json && scripts/baseline/size_baseline_base01.json -- both untouched; every JSON figure cross-checked programmatically against 138-06-FIRMWARE-MEASUREMENT.md, byte-for-byte match"
        status: pass
    human_judgment: false
  - id: D4
    description: "F-138-04 and F-138-05 recorded with mechanisms, verbatim evidence and owners; neither check_size_baseline.py nor check_build_warnings.py modified; artifact closes with a 'what this baseline is and is not' section denying any CI claim"
    verification:
      - kind: other
        ref: "reproduced (read-only) the uncaught KeyError in check_size_baseline.py (exit 1) and the clean exit-2 message in check_build_warnings.py for native_trace_v131, both quoted verbatim in 138-06-FIRMWARE-MEASUREMENT.md section 9; git diff --quiet on both checker scripts confirms neither was modified"
        status: pass
    human_judgment: false

# Metrics
duration: 22min
completed: 2026-08-09
status: complete
---

# Phase 138 Plan 06: Preconditions & Baseline — Cold Firmware Measurement Summary

**Cold flash/RAM for three AVR targets and case/suite/warning counts for four native envs, frozen into an immutable `size_baseline_v131.json` beside BASE-01 and verified green through the existing `check_size_baseline.py`/`check_build_warnings.py` `--baseline` seam; two D-07-class gate findings (base-dependent verdict, unknown-env KeyError) recorded with owners and left unfixed.**

## Performance

- **Duration:** ~22 min
- **Started:** 2026-08-09T00:19:19Z (approx., per STATE.md's pre-execution timestamp)
- **Completed:** 2026-08-09T00:41:10Z
- **Tasks:** 3
- **Files modified:** 2 (both created)

## Accomplishments

- Measured every AVR target cold (`pio run -t clean -e <env>` then a single uninterrupted `pio run -e
  <env>`, 540000ms timeout each): `uno` 23954/32256 flash, 1573/2048 RAM; `uno328pb` 24004/32384 flash,
  1579/2048 RAM; `leonardo` 26016/28672 flash, 2014/2560 RAM — no `.pio/build/{uno,uno328pb,leonardo}`
  directory existed beforehand, so every figure is a genuinely cold first build. All three are
  byte-identical to the live baseline's own recorded figures, the direct proof that plan 138-03/138-05's
  test-only trace/timing instrumentation is invisible to AVR-compiled surface.
- Measured every native env cold (`rm -rf .pio/build/<env>` then a single `pio test -e <env>`, same
  timeout): `native` and `native_nodevtools` both 141 cases / 17 suites / all PASSED (the two pinned
  envs, re-confirming the behavioural flag-off proof with the new `HOST_STUBS_RECORD_TIMING` guard
  present but undefined); `native_pinmap_provisional` 10/1; `native_trace_v131` 5/1 (2 smoke + 3
  protocol cases). Independently re-derived every case/suite count programmatically using
  `check_size_baseline.py`'s own regexes rather than eyeballing the summary tables.
- Ran every live gate verbatim and recorded exit codes: the default-seam `check_size_baseline.py`
  (exit 0 — the load-bearing AVR-invisibility proof), the `--policy merge05` band run against BASE-01
  (exit 0, uno-class headroom 42B/36B remaining at this tree), and `check_build_warnings.py` on the
  cold native logs (exit 0, all three measured native watermarks matching exactly: 1166/1166/138).
  Ran `python3 -m pytest tests/ -q` in place inside `/workspaces/firestarter`: 227 passed, 0 failed.
- Froze `firestarter/scripts/baseline/size_baseline_v131.json` as an immutable sibling of BASE-01 in
  its exact schema, carrying `fork_base`/`measured_at_tree` provenance, two delta blocks
  (`deltas_vs_base01`: +22/+28/−56, matching size_baseline.json's own recorded deltas exactly;
  `deltas_vs_size_baseline`: 0/0/0, since this tree's AVR-compiled surface is byte-identical to the
  live baseline's), and all four native envs. Verified independently through
  `check_size_baseline.py --baseline` and `check_build_warnings.py --baseline` (both accept the flag;
  both exit 0). The live `size_baseline.json` and `size_baseline_base01.json` are confirmed
  byte-for-byte untouched (`git diff --quiet`).
- Recorded **F-138-04** (the size gate's verdict is base-dependent: GREEN at the decided fork base
  `3085084`, RED at the live beta tip `6fab4ea` with a uniform +34B flash delta attributable to
  `b1737b2` — the live-tip figure quoted from `138-RESEARCH.md` and explicitly labelled
  research-measured, not re-built by this plan) and **F-138-05** (`check_size_baseline.py`'s
  `compare_native` raises an uncaught `KeyError` on an unknown env, exiting 1 where its own taxonomy
  promises 2 — reproduced verbatim for `native_trace_v131` — while `NATIVE_ENVS` being hardcoded makes
  that env invisible to both live gates regardless of invocation shape). Both findings carry an owner
  (`henols`, plus phase-specific consumers) and an explicit "not fixed here" statement; verified by
  inspection that neither `check_size_baseline.py` nor `check_build_warnings.py` was modified anywhere
  in this plan.

## Task Commits

1. **Task 1: Take the cold measurements and run both gates verbatim** — combined with Task 3 below
   into one meta commit (`1d4f5726`, docs) — **meta**
2. **Task 2: Freeze size_baseline_v131.json and verify it through the existing seam** — `fb7949c`
   (feat) — **firestarter**
3. **Task 3: Record the two D-07-class findings with owners, and do not fix them** — combined with
   Task 1 above into `1d4f5726` (docs) — **meta**

Tasks 1 and 3 both write to the same file (`138-06-FIRMWARE-MEASUREMENT.md`); the plan's own
`commits_land_in` directive states "meta (`/workspaces`) for 138-06-FIRMWARE-MEASUREMENT.md ... Two
repos, two commits" — one commit per repo, not one per task. Task 1's content was written and held
uncommitted; Task 2's fully independent file was committed immediately in the firestarter submodule;
Task 3's Findings/closing section was then appended to the same held file, which was committed once,
whole, in the meta repo — mirroring plan 138-05's own precedent for an explicit plan-mandated
single-commit structure.

**Plan metadata:** (this commit, immediately following) — meta

## Files Created/Modified

- `firestarter/scripts/baseline/size_baseline_v131.json` (created, 151 lines) — immutable v1.31
  freeze: `avr_targets` (3), `native_envs` (4), two delta blocks, `envs_agree_note`, `warnings`
- `.planning/phases/138-preconditions-baseline/138-06-FIRMWARE-MEASUREMENT.md` (created, 391 lines) —
  provenance, AVR/native/warnings tables, five verbatim gate-run sections, the firmware pytest result,
  two D-07-class findings (F-138-04, F-138-05), and a closing "is/is not" section

## Decisions Made

- **Combined Task 1 + Task 3 into one meta commit** (see Task Commits above) — an explicit
  plan-topology requirement, not a correction of a mistake.
- **Ran two supplementary gate invocations beyond the plan's explicitly-named pair** (adding
  `native_pinmap_provisional` to both `check_size_baseline.py` and `check_build_warnings.py`, since
  the live baseline carries its key in both blocks and the plan's own "pass it only if present" rule
  licenses it) — extra evidence, not a substitute for the primary named runs the acceptance criteria
  describe.
- **Did not rebuild the live beta tip for F-138-04** — quoted `138-RESEARCH.md`'s figure verbatim with
  its provenance (2026-08-08, cold freshly-extracted tarball tree) explicitly labelled
  research-measured rather than re-measured, because D-07 forbids acting on the discrepancy either way
  and a second 9-minute-class cold rebuild would not change which base PREP-02 already decided.
- **`platformio_core` (6.1.19) recorded as an already-verified environment fact, not "read from a
  build log"** — neither `pio run` nor `pio test` prints its own Core version in normal output; stated
  explicitly in the artifact's Provenance section rather than silently implying a log-sourced figure
  that does not exist. The four env-specific toolchain identifiers (`platform_atmelavr`,
  `toolchain_atmelavr`, `avr_gcc`, `framework_arduino_avr`) genuinely were read from the build log
  header, quoted verbatim in section 7.

## Deviations from Plan

None — plan executed exactly as written. All three tasks' automated `<verify>` blocks and every
acceptance criterion in `138-06-PLAN.md` passed; no bug, missing functionality, or architectural
question arose that required a Rule 1-4 classification.

## Issues Encountered

- **A `tail -3`-based SUCCESS-marker check produced a false "no marker" warning during self-verification
  (not a defect in the measurement).** An early sanity pass checked only the last 3 lines of each AVR
  log for `[SUCCESS]`, missing it because `pio run` prints the environment status summary table after
  the `[SUCCESS]` line. Widened the check to the whole log (`grep -c '\[SUCCESS\]'`), confirmed exactly
  one marker in each of the three AVR logs, and proceeded — no re-measurement was needed since the logs
  themselves were never in question, only the narrowness of the first check.
- **A `git diff --quiet` check for "checkers untouched" needed re-verification with an explicit `-C`
  path.** Because the Bash tool's working directory persisted from an earlier `cd /workspaces/firestarter`
  in this session (rather than resetting, as the environment's general note warns it might), a
  plain `git diff --quiet -- scripts/check_size_baseline.py ...` without an explicit path could have
  silently passed against the wrong repo if cwd had drifted. Re-ran with an explicit
  `git -C /workspaces/firestarter diff --quiet ...` and confirmed the check was genuinely scoped to the
  firestarter repo before trusting it.

## User Setup Required

None — no external service configuration required. All work is local cold measurement plus two
committed artifacts (one per repo).

## Next Phase Readiness

- The firmware half of PREP-03's pre-change baseline is fully measured and frozen. Plan 138-07 (host
  half + PREP-03 discharge) can now cite `size_baseline_v131.json` and
  `138-06-FIRMWARE-MEASUREMENT.md` directly.
- **PREP-03 remains open** (`[ ]` in `REQUIREMENTS.md`) — this plan produces further firmware-half
  evidence toward it but ticks nothing, per its own `may_tick_requirements: []`. Plan 138-07 discharges
  PREP-03 itself.
- Phase 144's TEST-08 has its comparison point: `size_baseline_v131.json`, read via an explicit
  `--baseline` argument to `check_size_baseline.py` (and `check_build_warnings.py`, which also accepts
  the flag) — never the default `FIRESTARTER_SIZE_BASELINE` seam, which still resolves to the live,
  unmodified `size_baseline.json`.
- F-138-04 and F-138-05 are carried forward with named owners (`henols`, plus Phase 143/144/TEST-08 as
  consumers) — neither blocks this plan or 138-07, but both are live risks for whichever phase next
  rebuilds against the live beta tip or adds a fifth native env.
- No push, no CI dispatch, and no write-path (`src/`) edit occurred at any point in this plan —
  confirmed via `git status --porcelain src/` immediately before writing this summary.

## Self-Check: PASSED

- FOUND: `/workspaces/firestarter/scripts/baseline/size_baseline_v131.json`
- FOUND: `/workspaces/.planning/phases/138-preconditions-baseline/138-06-FIRMWARE-MEASUREMENT.md`
- FOUND commit (firestarter): `fb7949c`
- FOUND commit (meta): `1d4f5726`

No missing items.

---
*Phase: 138-preconditions-baseline*
*Completed: 2026-08-09*
