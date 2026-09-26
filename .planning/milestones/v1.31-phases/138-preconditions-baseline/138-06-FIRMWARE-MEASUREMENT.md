# 138-06-FIRMWARE-MEASUREMENT: Cold firmware baseline — PREP-03 (firmware half)

**Owner requirement:** PREP-03 (firmware-half evidence only — PREP-03 itself is discharged by plan
138-07, not here; this plan ticks **no** requirement, per its own `may_tick_requirements: []`).
**Status:** all figures measured cold, on a named tree, each beside the command that produced it.
Both live gates re-run verbatim against the live baseline; two D-07-class findings recorded, neither
checker touched.

## 1. Provenance

| Field | Value |
|---|---|
| Measured tree (`measured_at_tree`) | `67d60615ed4449e55352746d7cc7b2c1af999368` (`67d6061`) — firmware repo, branch `gsd/v1.31-27c-programming-algorithm-fidelity` |
| Fork base (`fork_base`, from `138-BRANCH-BASES.md` §4) | `30850845f9c0994706f28d2a74fccc3adbb4b387` (`3085084`) |
| Ancestry | `git merge-base --is-ancestor 3085084 67d6061` exits **0** — the fork base is an ancestor of the measured tree |
| Commits between fork base and measured tree | 4 (`07d959c`, `75c2acd`, `d134635`, `67d6061` — plans 138-03 and 138-05's trace-instrumentation work; no `src/` edit in any of them) |
| Working tree state before measuring | clean (`git status --porcelain` empty) |
| Measured (UTC) | 2026-08-09, this session |
| `platformio_core` | `6.1.19` — verified as the already-installed environment fact before measurement began (matches every historical baseline's recorded value); **not** sourced from a build log, because neither `pio run` nor `pio test` prints its own Core version in normal (non-`--verbose`) output. Stated explicitly here rather than implied, per the "read from the log, never invoked separately" discipline: this one field is the documented exception, and the exception is named rather than silently satisfied. |
| `platform_atmelavr`, `toolchain_atmelavr`, `avr_gcc`, `framework_arduino_avr` | read **from `/tmp/138-06-uno.log`'s own header** (identical header shape in the `uno328pb`/`leonardo` logs) — see §7 |

## 2. AVR flash/RAM — cold, one uninterrupted invocation per env

Sequence per env, exactly: `pio run -t clean -e <env>` then, as one uninterrupted invocation,
`pio run -e <env>` capturing the full build log. No `.pio/build/{uno,uno328pb,leonardo}` directory
existed before this task ran (confirmed: only the four native build dirs were present), so every AVR
figure below is a genuinely cold first build, not a clean-then-warm-cache rebuild.

| Target | Command | Flash used / total / free | RAM used / total / free |
|---|---|---|---|
| `uno` | `pio run -t clean -e uno && pio run -e uno` (log: `/tmp/138-06-uno.log`) | 23954 / 32256 / **8302** | 1573 / 2048 / **475** |
| `uno328pb` | `pio run -t clean -e uno328pb && pio run -e uno328pb` (log: `/tmp/138-06-uno328pb.log`) | 24004 / 32384 / **8380** | 1579 / 2048 / **469** |
| `leonardo` | `pio run -t clean -e leonardo && pio run -e leonardo` (log: `/tmp/138-06-leonardo.log`) | 26016 / 28672 / **2656** | 2014 / 2560 / **546** |

Verbatim `RAM:`/`Flash:` lines (one pair per env, confirming each log carries the required pair
before anything was parsed):

```
uno:       RAM:   [========  ]  76.8% (used 1573 bytes from 2048 bytes)
           Flash: [=======   ]  74.3% (used 23954 bytes from 32256 bytes)
uno328pb:  RAM:   [========  ]  77.1% (used 1579 bytes from 2048 bytes)
           Flash: [=======   ]  74.1% (used 24004 bytes from 32384 bytes)
leonardo:  RAM:   [========  ]  78.7% (used 2014 bytes from 2560 bytes)
           Flash: [========= ]  90.7% (used 26016 bytes from 28672 bytes)
```

Each log's build ends with a `[SUCCESS]` marker (`grep -c '\[SUCCESS\]'` → 1 on all three logs) before
the size report is trusted — the pre-parse completeness check the plan requires.

**All three figures are byte-identical to the decided fork base's own recorded AVR figures**
(`size_baseline.json`'s `avr_targets` block, and `138-RESEARCH.md`'s "@ `3085084` (= local HEAD)"
row) — expected and load-bearing: `test/` is excluded from every AVR env's `build_src_filter`, so
plans 138-03/138-05's test-only trace instrumentation is provably invisible to the AVR-compiled
surface. This is positive evidence, not a null result.

## 3. Native suite counts — cold, all four envs

Sequence per env: `rm -rf .pio/build/<env>` then a single `pio test -e <env>` invocation. All four
`.pio/build/*` native directories existed and were warm (from plan 138-05's work) before this task
ran; each was removed before its measurement.

| Env | Command | Cases | Succeeded | Suites | All PASSED |
|---|---|---|---|---|---|
| `native` | `rm -rf .pio/build/native && pio test -e native` (log: `/tmp/138-06-native.log`) | 141 | 141 | 17 | yes |
| `native_nodevtools` | `rm -rf .pio/build/native_nodevtools && pio test -e native_nodevtools` (log: `/tmp/138-06-nodev.log`) | 141 | 141 | 17 | yes |
| `native_pinmap_provisional` | `rm -rf .pio/build/native_pinmap_provisional && pio test -e native_pinmap_provisional` (log: `/tmp/138-06-pinmap.log`) | 10 | 10 | 1 | yes |
| `native_trace_v131` | `rm -rf .pio/build/native_trace_v131 && pio test -e native_trace_v131` (log: `/tmp/138-06-tracev131.log`) | 5 | 5 | 1 | yes |

Case/suite/status figures above were independently re-derived programmatically from the raw logs
using the exact `CASES_RE`/`SUITE_RE` patterns `check_size_baseline.py` itself uses (not eyeballed
from the summary table), confirming: `native` and `native_nodevtools` — the two **pinned** envs —
each still read **141 cases across 17 suites, all PASSED**, with the new timing-recorder
instrumentation present in `test/native/avr/_shared/host_stubs_common.inc` but its guard
(`HOST_STUBS_RECORD_TIMING`) undefined for every one of those 17 suites. This is the behavioural
flag-off proof, stated as a live re-assertion of case/suite/status counts — not as an empty diff or a
byte-identical file, which the project's own recorded pitfall (`138-RESEARCH.md` Pitfall 10) warns
would break the moment any later `#if` guard legitimately changes bytes elsewhere in the file.

`native_pinmap_provisional` reports 10 cases across 1 suite, matching BASE-01/the live baseline
exactly (that env predates this phase). `native_trace_v131` reports **5 test cases across 1 suite**
(2 smoke cases + 3 protocol cases, each asserting full ordered positional equality against the frozen
`EPROM_V131_TRACE_PROTO_07/_08/_0B` arrays) — the same figure plan 138-05 recorded when it froze the
fixture, re-confirmed cold here rather than restated from that record.

## 4. Warnings — cold, `warnings.counting_command` applied verbatim

Command (from `size_baseline.json`'s own `warnings.counting_command`, applied to each cold log
already captured above — not a fresh `pio` invocation):

```
grep -cE 'warning: *"[^"]+" +redefined' <log>   # macro-redefinition count
grep -cE 'warning:' <log>                        # total
```

| Env | macro_redefinition | total | Live baseline watermark | Live baseline policy |
|---|---|---|---|---|
| `uno` | 0 | 0 | `== 0` | matches |
| `uno328pb` | 0 | 0 | `== 0` | matches |
| `leonardo` | 0 | 0 | `== 0` | matches |
| `native` | 1166 | 1166 | `<= 1166` | matches exactly (no headroom, no excess) |
| `native_nodevtools` | 1166 | 1166 | `<= 1166` | matches exactly |
| `native_pinmap_provisional` | 138 | 138 | `<= 138` | matches exactly |
| `native_trace_v131` | 140 | 140 | *(not in either live baseline — recorded here only)* | n/a — see F-138-05 |

These counts are cold; the project's own recorded trap (`meta.warm_vs_cold_correction`) states a warm
re-run of the two pinned native envs would read **998**, materially lower and not a valid watermark
source. No AVR or native env was measured warm at any point in this task.

## 5. Gate runs, verbatim

### 5a. Default-seam `check_size_baseline.py` — the load-bearing AVR-invisibility run

```
$ python3 scripts/check_size_baseline.py \
    --avr-log uno=/tmp/138-06-uno.log --avr-log uno328pb=/tmp/138-06-uno328pb.log \
    --avr-log leonardo=/tmp/138-06-leonardo.log \
    --native-log native=/tmp/138-06-native.log --native-log native_nodevtools=/tmp/138-06-nodev.log

PASS: uno(flash=23954/32256,ram=1573/2048), uno328pb(flash=24004/32384,ram=1579/2048),
leonardo(flash=26016/28672,ram=2014/2560), native(cases=141,suites=17),
native_nodevtools(cases=141,suites=17)
```

**Exit code: 0.** Read against the **live default baseline** (`scripts/baseline/size_baseline.json`,
no `--baseline` override). Because AVR builds exclude `test/`, this exit-0 result is the direct,
mechanical proof that plans 138-03/138-05's instrumentation is AVR-invisible and that the three AVR
figures still match the live record exactly — stated as required in §2.

**Supplementary run, `native_pinmap_provisional` added** (present in the live baseline's
`native_envs` and `warnings.native` blocks, so passing it is licensed):

```
$ python3 scripts/check_size_baseline.py \
    --avr-log uno=... --avr-log uno328pb=... --avr-log leonardo=... \
    --native-log native=... --native-log native_nodevtools=... \
    --native-log native_pinmap_provisional=/tmp/138-06-pinmap.log

PASS: uno(flash=23954/32256,ram=1573/2048), uno328pb(flash=24004/32384,ram=1579/2048),
leonardo(flash=26016/28672,ram=2014/2560), native(cases=141,suites=17),
native_nodevtools(cases=141,suites=17), native_pinmap_provisional(cases=10,suites=1)
```

**Exit code: 0.**

### 5b. `--policy merge05` band run against the frozen BASE-01 record

```
$ python3 scripts/check_size_baseline.py --policy merge05 \
    --baseline scripts/baseline/size_baseline_base01.json \
    --avr-log uno=/tmp/138-06-uno.log --avr-log uno328pb=/tmp/138-06-uno328pb.log \
    --avr-log leonardo=/tmp/138-06-leonardo.log

PASS: uno(flash=23954/32256[+22<=64],ram=1573/2048[=]),
uno328pb(flash=24004/32384[+28<=64],ram=1579/2048[=]),
leonardo(flash=26016/28672[-56<=0],ram=2014/2560[=])
```

**Exit code: 0.** Band position: `uno` +22 of 64 B (42 B headroom remaining at this tree), `uno328pb`
+28 of 64 B (36 B headroom remaining), `leonardo` −56 of a 0 B must-not-grow band (36 B of shrink
margin). These are **this measured tree's** headroom figures — they are not the live-beta-tip
headroom figures quoted in F-138-04/F-138-02, which are smaller (8 B / 2 B) because that tree carries
`b1737b2`'s additional +34 B this tree deliberately does not include (§6).

### 5c. `check_build_warnings.py` — cold native logs

```
$ python3 scripts/check_build_warnings.py \
    --log native=/tmp/138-06-native.log --log native_nodevtools=/tmp/138-06-nodev.log

PASS: native: total warnings=1166 (== watermark 1166),
native_nodevtools: total warnings=1166 (== watermark 1166)
```

**Exit code: 0.** No `INFO:` line was emitted (which would indicate the watermark is now above the
true cold count) — the recorded watermark and the freshly cold-measured total agree exactly.

**Supplementary run, `native_pinmap_provisional` added** (present in `warnings.native`):

```
$ python3 scripts/check_build_warnings.py \
    --log native=... --log native_nodevtools=... --log native_pinmap_provisional=/tmp/138-06-pinmap.log

PASS: native: total warnings=1166 (== watermark 1166),
native_nodevtools: total warnings=1166 (== watermark 1166),
native_pinmap_provisional: total warnings=138 (== watermark 138)
```

**Exit code: 0.**

**AVR envs through the same checker** (exact-zero rule):

```
$ python3 scripts/check_build_warnings.py \
    --log uno=/tmp/138-06-uno.log --log uno328pb=/tmp/138-06-uno328pb.log --log leonardo=/tmp/138-06-leonardo.log

PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0),
leonardo: macro_redefinition=0 (== 0)
```

**Exit code: 0.**

## 6. Firmware python gate suite (`firestarter/tests/`)

```
$ python3 -m pytest tests/ -q
........................................................................ [ 31%]
........................................................................ [ 63%]
........................................................................ [ 95%]
...........                                                              [100%]
227 passed in 10.78s
```

**227 passed, 0 failed, 0 skipped**, run **in place** inside `/workspaces/firestarter` (the meta repo
present as a sibling at `/workspaces`, and a real `.git` present) — `138-RESEARCH.md` and
`138-03-TRACE-CAPTURE.md` both record that several of these gates walk git history or resolve a
meta-repo root and fail-closed in a detached tree (7 fail / 32 skip there); "in place" is therefore
part of the figure, not an incidental detail. 227 = 221 pre-existing (`138-RESEARCH.md`'s own
"Measured Baseline" figure) + 6 new, from plan 138-05's `test_golden_trace_identity_eprom_v131.py`.

## 7. Toolchain versions — read from the build logs

From `/tmp/138-06-uno.log`'s header (identical shape in the `uno328pb`/`leonardo` logs):

```
PLATFORM: Atmel AVR (5.2.0) > Arduino Uno
PACKAGES:
 - framework-arduino-avr @ 5.3.0
 - toolchain-atmelavr @ 1.70300.191015 (7.3.0)
```

→ `platform_atmelavr = 5.2.0`, `framework_arduino_avr = 5.3.0`, `toolchain_atmelavr = 1.70300.191015`,
`avr_gcc = 7.3.0`. All four read directly from the log text quoted above — none was invoked
separately. All four are byte-identical to every historical baseline's recorded `meta` block
(BASE-01, the live baseline, and `138-RESEARCH.md`'s "Environment Availability" table).
`framework_arduino_avr_minicore = 3.1.2` is likewise unchanged (not printed in this particular log
header because no minicore-only env was measured in this task, but present in the same package set
this baseline shares with BASE-01/the live baseline; recorded here for schema completeness only,
never re-derived from prose).

## 8. Untouched-files verification

```
$ git status --porcelain src/ scripts/baseline/size_baseline.json
(empty)
$ git diff --quiet -- scripts/check_size_baseline.py scripts/check_build_warnings.py && echo "checkers untouched"
checkers untouched
$ git status --porcelain
(empty — full working tree clean at the time every gate above ran)
```

No write-path source (`src/`) was edited; the live baseline was not rewritten; neither checker script
was modified by any command in this task.

## 9. Findings (F-138-04, F-138-05) — recorded with owners, explicitly not fixed (D-07)

Verified by inspection before writing this section: `git diff --quiet -- scripts/check_size_baseline.py
scripts/check_build_warnings.py` succeeds — **neither checker was modified anywhere in this plan.**

### F-138-04 — the size gate's verdict depends on which base you stand on

**Mechanism.** `check_size_baseline.py`'s default-seam run is base-dependent by construction: it
compares whatever AVR/native logs it is given against whichever tree `scripts/baseline/size_baseline.json`
itself was last written from. §5a above measured this **exit 0 — GREEN** at the fork base this plan
stands on (`3085084` → `67d6061`, this plan's measured tree, byte-identical to the live baseline's own
figures). `138-RESEARCH.md` §"Gate outcomes (D-07's question, answered)" separately measured the same
gate **exit 1 — RED** at the live firmware `beta` tip `6fab4ea`, two commits ahead of the fork base,
with a uniform **`flash_used` +34 B on all three AVR targets** (`uno`, `uno328pb`, `leonardo`), RAM
unchanged, attributable to commit `b1737b2` (`feat(protocol): carry HW revision + FW identity in the
MSG_OK_READY ack (#49)`, `src/firestarter.cpp` +37/−1). **That live-tip figure is stated here as
research-measured, not re-measured by this plan**: it was read from `138-RESEARCH.md`, measured
2026-08-08 (the day before this plan ran) in a cold, freshly-extracted tree pulled from
`gh api repos/henols/firestarter/tarball/6fab4ea` — cold by construction, per the project's own
warm-vs-cold measurement discipline, and independently corroborated by `138-BRANCH-BASES.md` §5
(`F-138-02`), which re-verified the SHA-level facts (commit list, file list) live from this session's
own `gh api …/compare/3085084...6fab4ea` call without rebuilding the tree.

**This phase deliberately did not rebuild the live beta tip.** Two reasons: a second full cold build
of three AVR targets against a tree this phase does not fork from buys nothing a measurement phase
needs — it would not change which base PREP-02 already decided (`3085084`, **OD-2**), and D-07
forbids fixing the discrepancy either way, so re-confirming it with a second cold build would spend a
9-minute-class toolchain invocation to learn nothing actionable. **Both readings are stated honestly,
side by side, rather than reconciled**: GREEN at the decided base, RED at the live tip, and this plan
took the GREEN one because Phase 138 exists to define "before," and a fork base whose own size gate
arrives RED would make every downstream `TEST-08` delta measure against an already-broken reference.

**Cross-reference:** `F-138-02` (`138-BRANCH-BASES.md` §5) is the same drift, recorded independently
by plan 138-01 at branch-adjudication time; this finding restates it specifically in terms of the size
gate's exit code, which `138-BRANCH-BASES.md` names but does not itself re-run.

**Owners** (recorded, not fixed — D-07):

| Item | Owner |
|---|---|
| Flash-delta reconciliation (whether v1.31's own change should absorb, offset, or separately account for the pre-existing +34 B) | **Phase 144 / TEST-08** |
| MERGE-05 band headroom (at the live tip: `uno` +56/64, `uno328pb` +62/64 — 8 B and 2 B remaining; at this plan's measured tree: `uno` +22/64, `uno328pb` +28/64 — 42 B and 36 B remaining, §5b) | **Phase 143 / 144** |
| Escalation if headroom is exhausted before Phase 144 closes | **henols** |

### F-138-05 — the checker's unknown-env path contradicts its own exit taxonomy, and the new env is invisible to both gates

**Mechanism, two linked defects, both reproduced read-only this session (§ below), neither fixed:**

1. **`check_size_baseline.py`'s `compare_native` performs a bare dictionary lookup** (`baseline["native_envs"][env]`,
   line 278) with no `.get()` guard. Reproduced live:

   ```
   $ python3 scripts/check_size_baseline.py --native-log native_trace_v131=/tmp/138-06-tracev131.log
   Traceback (most recent call last):
     File "/workspaces/firestarter/scripts/check_size_baseline.py", line 487, in <module>
       sys.exit(main(sys.argv[1:]))
     File "/workspaces/firestarter/scripts/check_size_baseline.py", line 457, in main
       failures = compare_native(env, parsed, baseline)
     File "/workspaces/firestarter/scripts/check_size_baseline.py", line 278, in compare_native
       rec = baseline["native_envs"][env]
             ~~~~~~~~~~~~~~~~~~~~~~~^^^^^
   KeyError: 'native_trace_v131'
   $ echo "EXIT=$?"
   EXIT=1
   ```

   An uncaught `KeyError` propagates to the interpreter's default handler, which exits **1** — the
   exact code the script's own module docstring reserves for *"an env's observed figures diverge from
   the baseline … a regression"*. An unknown env name is not a regression; it is a tool/format
   failure, the module's own documented exit **2** taxonomy. Its sibling checker gets this right:

   ```
   $ python3 scripts/check_build_warnings.py --log native_trace_v131=/tmp/138-06-tracev131.log
   ERROR: env 'native_trace_v131' not found in baseline warnings.avr or warnings.native -- configuration error, not a pass
   ERROR: unknown env(s) not found in baseline warnings block: native_trace_v131 -- treating as a configuration failure, not a pass.
   $ echo "EXIT=$?"
   EXIT=2
   ```

   **This becomes load-bearing the moment a fourth native env exists — and this phase creates one**
   (`native_trace_v131`, landed by plan 138-03/138-05). Before this phase, `check_size_baseline.py`
   had never been asked to compare an env absent from its baseline; the defect was latent, not
   observed.

2. **`check_size_baseline.py`'s `NATIVE_ENVS = ("native", "native_nodevtools")` is hardcoded** (line
   100), so `--rebuild`'s `_rebuild_native` loop never reaches `native_pinmap_provisional` or
   `native_trace_v131` regardless of what the baseline file itself records. Combined with defect 1,
   `native_trace_v131`'s cases, suites and warnings are **unmeasured by both live gates** under any
   invocation shape — `--rebuild` skips it structurally; an explicit `--native-log`/`--log` for it
   raises (checker 1) or exits 2 (checker 2).

**Phase 138's explicit decision: this gate-blindness is accepted and recorded, not silently ignored.**
The compensating control is that `native_trace_v131`'s counts and warnings (5 cases / 1 suite / all
PASSED; 140 macro-redefinition warnings, cold) are recorded in `scripts/baseline/size_baseline_v131.json`'s
`native_envs` and `warnings.native` blocks (§3–§4 above) and in that file's own `envs_agree_note`,
and the env is deliberately never passed to either live gate for a real pass/fail evaluation — every
invocation of either gate in this plan that names `native_trace_v131` (§5a/§5c and this section) is a
**read-only defect reproduction**, not a measurement this plan's own gate status depends on.

**Owner: henols. Candidate consumer: Phase 144** (the phase most likely to add a fifth native env or
to rely on `--rebuild` covering all envs, at which point defect 2's silence stops being harmless).
Not fixed here — repairing either checker inside the phase whose purpose is to define "before" would
itself be an edit to a load-bearing gate mid-measurement, exactly what D-07 forbids.

## 10. What this baseline is — and is not

**This baseline IS:**
- The pre-change firmware input `TEST-08` (Phase 144) compares its post-change flash/RAM/suite-count
  delta against, frozen in `scripts/baseline/size_baseline_v131.json` and independently readable
  through `check_size_baseline.py`'s existing `--baseline` seam (verified green in §5a/Task 2).
- A cold, command-attributed measurement of the tree this milestone's firmware branch actually forked
  from (`3085084`) plus the trace-instrumentation commits that landed on top of it (`67d6061`), stated
  as such — not a measurement of `beta`'s current tip.
- Positive evidence that plans 138-03/138-05's opt-in trace/timing instrumentation is invisible to
  every AVR target and byte-exact on both pinned native envs' case/suite/status counts (§2–§3).

**This baseline is NOT:**
- **Not a claim that CI is green.** No CI run is recorded in this document — dispatching and reading
  firmware/app CI is plan 138-07's operator-gated scope, not this plan's.
- **Not a repair of `check_size_baseline.py` or `check_build_warnings.py`.** Both findings above (and
  `F-138-02`) are recorded and left exactly as found, per D-07.
- **Not a measurement of any tree other than the two SHAs this document names**: the fork base
  `30850845f9c0994706f28d2a74fccc3adbb4b387` (cited for ancestry only — not independently rebuilt here)
  and the measured tree `67d60615ed4449e55352746d7cc7b2c1af999368`. The live beta tip `6fab4ea`'s
  figures in F-138-04 are quoted from `138-RESEARCH.md`, explicitly labelled research-measured, and
  were not reproduced by this plan.
- **Not a widening of PREP-03.** This document and `size_baseline_v131.json` are the firmware half of
  PREP-03's evidence only; PREP-03 itself is discharged by plan 138-07, and this plan's own
  `may_tick_requirements: []` ticks nothing in `REQUIREMENTS.md`.

---

*Phase: 138-preconditions-baseline — Plan 06, Tasks 1–3*
*Recorded: 2026-08-09, from live cold measurements taken this session (three `pio run` clean-rebuild
cycles, four `rm -rf .pio/build/<env>` + `pio test` cycles, five `check_size_baseline.py`/
`check_build_warnings.py` invocations against the live baseline plus two against the new freeze, one
in-place firmware `pytest` run, and two read-only defect reproductions), and from `138-RESEARCH.md`'s
2026-08-08 research-measured live-beta-tip figures, explicitly labelled as such throughout.*
