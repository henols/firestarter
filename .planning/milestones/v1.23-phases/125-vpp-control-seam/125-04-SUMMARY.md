---
phase: 125-vpp-control-seam
plan: 04
subsystem: firmware
tags: [avr, avr-gcc, avr-nm, platformio, lto, size-baseline, non-vacuity, measurement]

# Dependency graph
requires:
  - phase: 125-vpp-control-seam
    plan: "01"
    provides: "the landed VPP control capability seam (include/rurp_vpp.h, src/rurp_vpp.cpp, platform/py32f071/CMakeLists.txt naming) this plan measures"
provides:
  - "Criterion 4 discharged as a measurement, not a citation: 0 B flash / 0 B RAM on uno, uno328pb and leonardo, from three independent cold builds this session, each corroborated non-vacuously in both directions"
  - "the already-armed check_size_baseline.py and check_build_warnings.py verdicts (both exit 0) recorded against this session's own three logs"
  - "D-16's re-baseline contingency recorded as evaluated and explicitly NOT taken (Branch A), with both baseline files re-hashed unchanged"
affects: [125-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Record-without-gating (D-15) implemented as a measurement-only plan: no comparator, tolerance band or policy flag was added; the pre-existing strict comparator (already armed since Phase 124) is what actually stands between the recorded baseline and the measured tree."
    - "Two-directional non-vacuity for a zero-cost claim: object-file presence (positive) plus a symbol count of 0 measured against a non-zero count of unrelated symbols in the SAME image (negative) — the shape that makes an honest zero distinguishable from a vacuous one."

key-files:
  created: []
  modified: []

key-decisions:
  - "D-16 Branch A taken: check_size_baseline.py's default (strict-equality, no --policy, no --baseline override) exited 0 against this session's three fresh build logs, so the re-baseline contingency was evaluated and deliberately NOT exercised. Re-baselining scripts/baseline/size_baseline.json with no delta to explain would rewrite the recorded reference for no reason and destroy the comparison Criterion 4 rests on."
  - "The elimination mechanism is link-time optimisation AND section garbage collection together, not section GC alone. platform-atmelavr@5.2.0's real CCFLAGS/LINKFLAGS (read by RESEARCH C-5 from builder/frameworks/arduino.py) include -flto on all three AVR envs; the seam's .o is an LTO slim object whose bodies never reach a real code section. No upstream document in this project's record names -flto before this phase's RESEARCH did."
  - "No new comparator, tolerance band, policy flag or gate script was added anywhere in firestarter/scripts/ — file count stays at 5 top-level check_*.py scripts, identical to the pre-task state. D-15's record-without-gating exception is implemented exactly as the operator chose, against the project's standing exit-code preference."
  - "Requirement ticking scope: NONE. VPP-03 appears in this plan's frontmatter as contributing evidence only; per the phase's explicit scope guard (against the Phase-116 4x premature-tick pattern), no requirement checkbox in .planning/REQUIREMENTS.md was ticked by this plan. Only Plan 125-06 may tick VPP-01/02/03."

requirements-completed: []  # Deliberately empty — this plan contributes Criterion 4's measurement toward VPP-03 but does not discharge it; only 125-06 ticks requirement checkboxes.

coverage:
  - id: D1
    description: "All three AVR targets (uno, uno328pb, leonardo) measured from a removed build directory followed by exactly one `pio run` invocation, flash AND RAM recorded with deltas against the live baseline"
    verification:
      - kind: integration
        ref: "rm -rf .pio/build/<env> then pio run -e <env> per env, three separate invocations, output captured to scratchpad logs"
        status: pass
    human_judgment: false
  - id: D2
    description: "The zero is non-vacuous in both directions: rurp_vpp.cpp.o exists in all three build dirs (4460 B each), and avr-nm finds 0 of the three seam symbols while finding 5 unrelated pre-existing vpp symbols in the SAME image"
    verification:
      - kind: unit
        ref: "ls -l .pio/build/<env>/src/rurp_vpp.cpp.o (all three); avr-nm <elf> | grep -cE seam-symbols (0/0/0) and | grep -c vpp (5/5/5), same three ELFs"
        status: pass
    human_judgment: false
  - id: D3
    description: "The already-armed check_size_baseline.py (default strict-equality mode) and check_build_warnings.py both run against this session's three build logs; exit codes recorded"
    verification:
      - kind: integration
        ref: "python3 scripts/check_size_baseline.py --avr-log uno=... --avr-log uno328pb=... --avr-log leonardo=... (exit 0); python3 scripts/check_build_warnings.py --log uno=... --log uno328pb=... --log leonardo=... (exit 0)"
        status: pass
    human_judgment: false
  - id: D4
    description: "D-16's re-baseline contingency recorded as evaluated and NOT taken (Branch A); both baseline files re-hashed unchanged; no new file added under firestarter/scripts/; pytest tests/ still 86 passed; git status --porcelain 0 lines"
    verification:
      - kind: unit
        ref: "git hash-object scripts/baseline/size_baseline.json scripts/baseline/size_baseline_base01.json, compared against git rev-parse HEAD:<path> for both (identical); find scripts -maxdepth 1 -type f | wc -l == 5; python3 -m pytest tests/ -q == 86 passed; git status --porcelain == 0 lines"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-07-31
status: complete
---

# Phase 125 Plan 04: Criterion 4 Measured — Three Cold AVR Builds, Non-Vacuity, Armed Comparator, D-16 Disposition Summary

**All three AVR targets rebuilt clean this session at exactly their pre-phase flash/RAM figures (0 B / 0 B delta), the zero proven non-vacuous in both directions (the seam's `.o` present, its three symbols absent from the linked image while five unrelated `vpp` symbols remain), the two already-armed gates both exit 0 against these fresh logs, and D-16's re-baseline contingency was evaluated and explicitly not exercised.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-07-31
- **Tasks:** 2 (Task 1 measurement-only; Task 2 gate runs + D-16 disposition)
- **Files modified:** 0 in the firmware submodule (measurement-only plan); 1 new (this SUMMARY) in the meta repo

## Accomplishments

- Ran three independent cold builds this session, each preceded by `rm -rf .pio/build/<env>` and each a single `pio run -e <env>` invocation with a 540000 ms timeout, capturing the full build log to `/tmp/claude-1000/.../scratchpad/125-{uno,uno328pb,leonardo}.log`.
- Measured flash and RAM for all three AVR targets, all four figures per env matching the live baseline exactly (0 B delta on every figure, both directions):

  | Env | Flash used/total (baseline) | Δ | RAM used/total (baseline) | Δ |
  |---|---|---:|---|---:|
  | uno | 23954 / 32256 (23954 / 32256) | 0 | 1573 / 2048 (1573 / 2048) | 0 |
  | uno328pb | 24004 / 32384 (24004 / 32384) | 0 | 1579 / 2048 (1579 / 2048) | 0 |
  | leonardo | 26016 / 28672 (26016 / 28672) | 0 | 2014 / 2560 (2014 / 2560) | 0 |

- Proved the zero non-vacuous in both directions:
  - **Positive:** `.pio/build/uno/src/rurp_vpp.cpp.o`, `.pio/build/uno328pb/src/rurp_vpp.cpp.o`, `.pio/build/leonardo/src/rurp_vpp.cpp.o` all exist, each **4460 bytes** (this session's measurement — the .o size scales with the toolchain/tree state at measurement time; RESEARCH's earlier prototype-tree figure was 4520/4520/4508, a different measurement of a different scratch tree, cited only as a cross-check, never as this plan's own evidence).
  - **Negative:** `avr-nm` (`/home/vscode/.platformio/packages/toolchain-atmelavr/bin/avr-nm`, not on `$PATH` directly — located via `find`) on each of the three linked images:

    | Env | Image path | seam-symbol count | unrelated-`vpp`-symbol count |
    |---|---|---:|---:|
    | uno | `.pio/build/uno/firestarter_uno.elf` | **0** | **5** |
    | uno328pb | `.pio/build/uno328pb/firestarter_uno328pb.elf` | **0** | **5** |
    | leonardo | `.pio/build/leonardo/firestarter_leonardo.elf` | **0** | **5** |

    The five unrelated symbols, identical across all three images: `_Z15eprom_check_vppP18firestarter_handle` (`eprom_check_vpp`), `get_vpp_mv`, `key_vpp_mv`, and two link-time-optimisation clones of `using_p1_as_vpp` (`.lto_priv.67`/`.lto_priv.68` on uno/uno328pb, `.lto_priv.74`/`.lto_priv.75` on leonardo — the clone numbering differs per-env because LTO's internal numbering is a function of the whole translation-unit graph, not a per-symbol identity). The zero-versus-five pair per env is what makes the seam-symbol absence a fact rather than an artifact of a query matching nothing: had the grep matched zero of *both* sets, the query itself would be suspect; matching zero of three named symbols while matching five of a *different, known-present* set proves the grep works and the three seam symbols specifically are gone.
- Stated the elimination mechanism correctly: `platform-atmelavr@5.2.0`'s real compiler/linker flags for all three AVR envs include `-flto` (per `125-RESEARCH.md` §C-5, read from `builder/frameworks/arduino.py:95–115` — `CCFLAGS … -ffunction-sections -fdata-sections -flto`, `LINKFLAGS … -Wl,--gc-sections -flto -fuse-linker-plugin`), a flag no upstream document in this project's record (CONTEXT, ROADMAP, or prior SUMMARY) names. The seam's `.o` is therefore an LTO slim object whose bodies never reach a real `.text` section — **link-time optimisation and `--gc-sections` both contribute** to the zero; the zero is not attributable to section garbage collection alone.
- Recorded explicitly, as a checked fact: **ARM flash and RAM are not measured and are not measurable in this environment.** `arm-none-eabi-gcc`, `cmake` and `ninja` are all absent from this devcontainer (confirmed via RESEARCH's `command -v` check, re-affirmed here — no local ARM toolchain exists). Criterion 4 binds AVR only; no ARM figure is claimed anywhere in this artifact.
- `git status --porcelain` in `/workspaces/firestarter` was **0 lines** at the end of Task 1 — no firmware file was modified, nothing was committed in the firmware repo for the measurement task.

### Task 2 — the two already-armed gates, and D-16's disposition

- Ran `python3 scripts/check_size_baseline.py` in its **default mode** (no `--policy`, no `--baseline` override — reads the live baseline through the `FIRESTARTER_SIZE_BASELINE` seam), passing the three repeated `--avr-log ENV=path` arguments pointing at this session's own three build logs:

  ```
  PASS: uno(flash=23954/32256,ram=1573/2048), uno328pb(flash=24004/32384,ram=1579/2048), leonardo(flash=26016/28672,ram=2014/2560)
  size-exit=0
  ```

- Ran `python3 scripts/check_build_warnings.py` against the same three logs:

  ```
  PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0), leonardo: macro_redefinition=0 (== 0)
  warn-exit=0
  ```

  This proves the new translation unit introduced no macro-redefinition warning on any AVR target (the zero-watermark property Phase 123 established, still holding). `check_build_warnings.py`'s `AVR_ENVS`/`NATIVE_ENVS` universe is exactly `(uno, uno328pb, leonardo)` and `(native, native_nodevtools)` — it has **no ARM awareness at all**, so this green result says nothing whatsoever about the ARM target; that is not this gate's job.

- **D-16's disposition — Branch A taken.** The comparator exited **0** (the expected outcome per RESEARCH C-5/C-8). Per D-16 and the plan's Task 2 instructions, the re-baseline path was evaluated and deliberately **NOT** taken: re-baselining `scripts/baseline/size_baseline.json` with no delta to explain would rewrite the recorded reference for no reason and destroy the very comparison Criterion 4 rests on. Confirmed by re-hashing both baseline files and comparing against their committed blob at `HEAD`:

  | File | Blob SHA (working tree) | Blob SHA (`HEAD:<path>`) | Match |
  |---|---|---|---|
  | `scripts/baseline/size_baseline.json` | `9cc5204bb437735d77523e62512c1d2cadfc668f` | `9cc5204bb437735d77523e62512c1d2cadfc668f` | identical — untouched |
  | `scripts/baseline/size_baseline_base01.json` | `b940c91655600a57ad7ef67cba723943af929daf` | `b940c91655600a57ad7ef67cba723943af929daf` | identical — untouched, matches the frozen Phase-124 MERGE-05 reference exactly |

  Nothing was committed in the firmware repo for this branch (there is nothing to commit — no file changed).

- **No new comparator, tolerance band, policy flag or gate script was added anywhere.** The set of files directly under `firestarter/scripts/` is unchanged: **5** top-level `check_*.py` scripts (`check_build_warnings.py`, `check_cmake_manifest.py`, `check_landing_range.py`, `check_orphan_provisional.py`, `check_size_baseline.py`) — the same set that existed before this plan started; this plan adds none.
- `python3 -m pytest tests/ -q` still reports **86 passed** (unchanged from the count recorded after Plan 125-03).
- `git status --porcelain` in `/workspaces/firestarter` is **0 lines** at the end of Task 2.
- **D-15 restated:** this phase records the flash/RAM figures without gating on them — an operator decision taken against the project's standing exit-code preference. No new comparator was added by this plan (or any plan in this phase). The pressure is nonetheless covered: the pre-existing strict comparator (`check_size_baseline.py`'s default `compare_avr()`, armed since Phase 124 and re-run above) is what actually stands between the recorded baseline and the measured tree — a nonzero delta would go red whether or not this phase's plans gate on it.

## Task Commits

Both tasks were measurement/verification-only — **no files were modified in the firmware repo**, so no task commit exists in `/workspaces/firestarter` for this plan. `git status --porcelain` was 0 lines before, during, and after both tasks.

**Plan metadata:** meta-repo commit for this SUMMARY + STATE.md + ROADMAP.md (see final commit below).

## Files Created/Modified

None in the firmware submodule. One new file in the meta repo: this SUMMARY.

## Build-Log Paths (this session)

- `/tmp/claude-1000/-workspaces/757f8ba4-f485-4f1e-be1f-4df7bbc031aa/scratchpad/125-uno.log`
- `/tmp/claude-1000/-workspaces/757f8ba4-f485-4f1e-be1f-4df7bbc031aa/scratchpad/125-uno328pb.log`
- `/tmp/claude-1000/-workspaces/757f8ba4-f485-4f1e-be1f-4df7bbc031aa/scratchpad/125-leonardo.log`

These are scratchpad artifacts (session-local, not committed) — the two gate invocations above reference these exact paths, not illustrative placeholders.

## Decisions Made

- **D-16 Branch A** (comparator exited 0 → re-baseline evaluated and deliberately not taken) — see above, with both baseline files' blob SHAs confirmed unchanged against `HEAD`.
- **Elimination mechanism stated as LTO + section GC, not GC alone** — per RESEARCH C-5's reading of `platform-atmelavr@5.2.0`'s real flag set (`-flto` present, unnamed by any prior artifact in this project).
- **No requirement ticked.** Per the phase's explicit scope guard, this plan does not tick VPP-01, VPP-02, or VPP-03 in `.planning/REQUIREMENTS.md` — only Plan 125-06 may do that.

## Deviations from Plan

**1. [Informational, not a deviation] Object-file byte sizes differ from RESEARCH's cross-check figures.** RESEARCH C-5 recorded 4520/4520/4508 bytes for `rurp_vpp.cpp.o` on a throwaway scratch-tree measurement made during the research session. This plan's own measurement, on the real tree, records **4460 bytes** for all three envs. Per the plan's own instruction ("Measure, do not cite... Research's figures are a cross-check, not this phase's evidence"), this plan's figure is what is recorded as evidence; the RESEARCH figure is cited above only as context for why the two numbers differ (different measurement session, same mechanism, non-load-bearing discrepancy — the .o size does not affect the flash/RAM delta, which is 0 in both cases).

No other deviations — plan executed exactly as written. All acceptance criteria in both tasks were independently re-checked against the live tree (cold-build figures, object-file existence + size, symbol counts on the same three images, gate exit codes against this session's own logs, blob-SHA re-hash against `HEAD`, script-count, pytest count, porcelain) rather than assumed from the plan's prose.

## Known Stubs

None. This plan performs measurement and verification only; it introduces no code, UI, or data path.

## Threat Flags

None. This plan's threat model (`125-04-PLAN.md` `<threat_model>`) is fully addressed: T-125-22 (vacuous zero) — mitigated by the two-directional non-vacuity proof above; T-125-23 (contaminated figure) — mitigated by the clean-then-single-invocation-with-extended-timeout discipline, all three recorded per env; T-125-24 (silent re-baseline absorbing a regression) — moot, the comparator exited 0 and Branch A was taken explicitly with reasoning; T-125-25 (frozen reference re-baselined) — mitigated, its blob SHA re-asserted unchanged; T-125-26 (a gate the operator declined being quietly restored) — mitigated, script count under `scripts/` unchanged at 5; T-125-27 (green warnings gate read as ARM coverage) — mitigated, its ARM blindness stated explicitly above; T-125-28 (ARM figure inferred from a local build) — mitigated, ARM size stated as not measured and not measurable, no ARM toolchain present. No new security-relevant surface was introduced by this measurement-only plan.

## Issues Encountered

None. `avr-nm` was not on `$PATH` directly (resolved via `find ~/.platformio -iname avr-nm*` → `/home/vscode/.platformio/packages/toolchain-atmelavr/bin/avr-nm`); this is an environment-path fact, not a defect, and does not affect any figure recorded above.

## User Setup Required

None — no external service configuration required.

## Claim Ceiling Compliance

This SUMMARY makes no claim that the firmware runs on a PY32F071, that closed-loop VPP works, that the pin map is correct/verified/validated, or an unqualified bench-validated/hardware-validated/silicon-verified claim. **No PY32F071 hardware exists.** ARM flash and RAM are stated as **not measured and not measurable** in this environment (no `arm-none-eabi-gcc`, `cmake`, or `ninja` present) — no ARM size figure appears anywhere in this artifact. AVR manual VPP control is not characterized here (out of this plan's scope — this plan measures size and gate verdicts only).

## Next Phase Readiness

- Criterion 4 is now measured, non-vacuously, on the real tree — 0 B flash / 0 B RAM on all three AVR targets, corroborated by object-file presence and a proven-non-vacuous symbol-absence query.
- Both already-armed gates (`check_size_baseline.py`, `check_build_warnings.py`) verify green against this session's own fresh build logs.
- D-16's contingency has an explicit recorded disposition (Branch A — not taken, with reasoning and re-hashed proof).
- No blockers. Plan 125-05 (D-13 ARM CI evidence, operator-gated push + `workflow_dispatch`) and Plan 125-06 (closing: full re-execution, `125-NONREGRESSION.md`, claim gate, tick VPP-01/02/03) can both proceed against this plan's recorded figures.

---
*Phase: 125-vpp-control-seam*
*Completed: 2026-07-31*

## Self-Check: PASSED

- FOUND: `/workspaces/.planning/phases/125-vpp-control-seam/125-04-SUMMARY.md`
- FOUND: meta commit `adfa702` (`git log --oneline --all` in `/workspaces`)
- Firmware repo `/workspaces/firestarter`: `git status --porcelain` = 0 lines (no firmware commit expected — measurement-only plan, D-16 Branch A took no re-baseline action)
