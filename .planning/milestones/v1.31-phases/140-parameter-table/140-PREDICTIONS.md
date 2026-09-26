# Phase 140 Plan 01 — Pre-Measurement Predictions

**Written:** 2026-08-10, before Task 3 runs any cold measurement.

**Why this document exists (CONTEXT `<specifics>`):** a ~0 byte AVR flash delta from a
`PROGMEM` table that nothing in `src/` yet references is indistinguishable, after the fact,
from "we forgot to add the table." Stating the prediction and its mechanical basis first —
and committing that statement to git before the measurement runs — is what turns the later
number into evidence rather than a claim that could have been quietly adjusted to fit
whatever was observed.

This document is committed to the meta repo (branch
`gsd/v1.31-27c-programming-algorithm-fidelity`) **before** any cold measurement below is
taken. The exact commit SHA that carries P1-P5, and the timestamps of the measurement runs
that followed it, are recorded in the "Observed (Plan 01, cold)" section appended to this
same file after that commit lands — never before.

---

## P1. AVR flash delta ≈ 0 bytes on `uno`, `uno328pb` and `leonardo`

**Prediction:** Building the AVR targets after this plan's two new files
(`include/eprom_params.h`, `src/proms/eprom_params.cpp`) land will show a flash-used delta of
approximately 0 bytes against the Phase 138 baseline (`23954`/`24004`/`26016` bytes
respectively, per `scripts/baseline/size_baseline_v131.json` `avr_targets`).

**Mechanical basis:**
- `configure_eprom` and every other `src/` call site are untouched this phase (D-10) — nothing
  references `eprom_params_for()`, `EPROM_PARAMS[]` or `EPROM_PARAM_KEYS[]` yet. Phase 141
  wires the table in.
- `~/.platformio/platforms/atmelavr/builder/frameworks/arduino.py` passes
  `-ffunction-sections` (line 98) and `-fdata-sections` (line 99) to `CCFLAGS`, and
  `-Wl,--gc-sections` (line 111) to `LINKFLAGS` — confirmed present in this environment's
  installed platform package. Every function and every PROGMEM array therefore lands in its
  own linker section, and an unreferenced section is dropped entirely at link time (F-140-02).
- The real flash cost of this table — 3 rows x 12 bytes = 36 bytes of `PROGMEM` data, plus the
  `eprom_params_for()` accessor body — lands in Phase 141's flash delta instead, funded by
  LOOP-02's planned removal of `program_mismatched_bytes()` / `verify_and_update_mask()` /
  `NUMBER_OF_RETRIES` and the adaptive-growth formula.
- Uno-class MERGE-05 headroom at this fork base is **42 B (`uno`) / 36 B (`uno328pb`)** against
  the 64 B band (`size_baseline_v131.json` `meta.deltas_vs_base01`); at the live `beta` tip it
  is materially thinner — **8 B / 2 B** (F-138-02). A ~0 delta this plan preserves all of that
  headroom for Phase 141 to spend.

## P2. AVR RAM delta = exactly 0 bytes on all three targets

**Prediction:** RAM-used stays at `1573`/`1579`/`2014` bytes (`uno`/`uno328pb`/`leonardo`)
— an exact-zero delta, not merely a small one.

**Mechanical basis:** both `EPROM_PARAM_KEYS[]` and `EPROM_PARAMS[]` are declared `PROGMEM`
(D-04). A `PROGMEM` array is never copied into `.data`/`.bss` at startup, so it costs zero
static RAM regardless of whether it is referenced. MERGE-05 requires this delta to be exactly
0, not merely inside a band, on every AVR target.

## P3. Cold `native` and `native_nodevtools` total warning counts stay at exactly 1166 each

**Prediction:** `python3 scripts/check_build_warnings.py` against cold logs from both pinned
native envs reports `total warnings=1166` for **both**, and exits 0.

**Mechanical basis:** `src/proms/eprom_params.cpp` includes only `"eprom_params.h"`, which in
turn includes only `<stdint.h>` and `"rurp_platform_compat.h"` — no Arduino framework header
anywhere in the new TU's include graph, following the one existing precedent in
`src/proms/` that already omits it, `src/proms/not_implemented.cpp` (absent from the
14-warnings-per-TU list in F-140-01). `build_src_filter = +<proms/>` is shared by `native`,
`native_nodevtools` and three other native envs, so this new TU is compiled by all of them —
but since it adds zero warnings, the shared watermark does not move. This was additionally
verified directly in this plan's own Task 2: `g++ -std=gnu++17 -Wall -Wextra -I include -c
src/proms/eprom_params.cpp` and the header compiled standalone both produced **zero**
warnings (one `-Wcomment` trap was found and fixed pre-commit — a glob-pattern comment
containing a literal `/*` substring — see the Plan 01 Summary for the detail).

## P4. Native suite case/suite counts are unchanged

**Prediction:**
- `pio test -e native` and `pio test -e native_nodevtools` both report **141 test cases across
  17 suites**, all passing.
- `pio test -e native_trace_v131` reports **5 test cases across 1 suite**, GREEN.

**Mechanical basis:** this plan adds no test file and no `test_filter` entry to any existing
env — `include/eprom_params.h` and `src/proms/eprom_params.cpp` are production sources, not
test sources, and are added to no allowlist. The suite counts are therefore expected to be
byte-identical to the Phase 138 baseline. `native_trace_v131` was already re-confirmed GREEN
in this plan's Task 2 (`pio test -e native_trace_v131` — 5/5 PASSED) as the direct proof that
`src/proms/eprom.cpp` is still byte-unchanged (D-10); this document's Observed section below
independently re-confirms the two pinned envs' counts under the cold-measurement discipline.

## P5. `native_params_v131` (created in plan 140-04) will be invisible to both live gates

**Prediction:** once plan 140-04 creates the `[env:native_params_v131]` environment, passing
that env name to `scripts/check_size_baseline.py` will raise an uncaught `KeyError` (exit 1,
a false regression signal — not the documented exit-2 "unknown env" path), and passing it to
`scripts/check_build_warnings.py` will exit 2 cleanly (no baseline entry for that env).

**Mechanical basis:** `check_size_baseline.py` hardcodes `NATIVE_ENVS = ("native",
"native_nodevtools")` and `compare_native` does a bare dictionary lookup against the baseline
JSON's `native_envs` key — an env name absent from that dict raises `KeyError` before any
exit-2 configuration-error path is reached (F-138-05, recorded and accepted in
`138-BASELINE.md` §7, owner `henols`, not fixed). Neither script is to be given the
`native_params_v131` env name at any point in this phase; its own counts are recorded only in
`scripts/baseline/size_baseline_v131.json`-style records, per the `native_trace_v131`
precedent this phase already follows.

---

## Reconciliation

P1-P4 above are **predictions recorded before measurement**, committed to this file's own
first version in the meta repo. This is not a retrospective label — the commit that carries
P1-P5 (named in the Observed section below by SHA) predates, in both git history and
wall-clock time, every cold-measurement command this document also records the output of.

Phase 144 / TEST-08 is where the full-phase (Phases 140-143) flash/RAM/warning/suite-count
delta gets reconciled against the sum of every phase's individual predictions, including
this one — the point of writing predictions down per-phase is that Phase 144 discovers a
match or a named discrepancy, never a surprise.

---

## Observed (Plan 01, cold)

**Predictions commit:** `a2705cfb02d848ab1d927da0b784f959300cc4ab` (meta repo, branch
`gsd/v1.31-27c-programming-algorithm-fidelity`), committed `2026-08-10T00:13:30Z` — this
carried P1-P5 above with no Observed section. Every cold-measurement command below ran
**after** this commit landed:

- `native`: `rm -rf .pio/build/native` then `pio test -e native`, started
  `2026-08-10T00:13:53Z` (23 s after the predictions commit), finished `2026-08-10T00:15:47Z`,
  exit 0. Log: `/tmp/140-01-native.log`.
- `native_nodevtools`: `rm -rf .pio/build/native_nodevtools` then `pio test -e
  native_nodevtools`, started `2026-08-10T00:15:54Z`, finished `2026-08-10T00:17:49Z`, exit 0.
  Log: `/tmp/140-01-nodev.log`.

Both commands ran once each, uninterrupted, cold (`.pio/build/<env>` removed immediately
before each single invocation) — the discipline P3/P4's basis depends on.

### Results vs. predictions

| Prediction | Predicted | Observed | Match |
|---|---|---|---|
| P1 (AVR flash delta, `uno`) | ≈ 0 B | **0 B** (23954 B, unchanged from `size_baseline_v131.json`; confirmed directly in this plan's Task 2 `pio run -e uno`) | Yes — exact, not merely approximate |
| P2 (AVR RAM delta, `uno`) | = 0 B | **0 B** (1573 B, unchanged) | Yes |
| P3 (`native` warnings) | exactly 1166 | **1166** (macro_redefinition=1166, total=1166) | Yes |
| P3 (`native_nodevtools` warnings) | exactly 1166 | **1166** (macro_redefinition=1166, total=1166) | Yes |
| P4 (`native` cases/suites) | 141 / 17 | **141 test cases: 141 succeeded**, 17 suite rows in the summary table | Yes |
| P4 (`native_nodevtools` cases/suites) | 141 / 17 | **141 test cases: 141 succeeded**, 17 suite rows in the summary table | Yes |
| P4 (`native_trace_v131`) | 5 / 1, GREEN | **5 test cases: 5 succeeded**, 1 suite, PASSED (confirmed in this plan's Task 2) | Yes |

`check_build_warnings.py` gate run, verbatim:

```
$ python3 scripts/check_build_warnings.py \
    --log native=/tmp/140-01-native.log --log native_nodevtools=/tmp/140-01-nodev.log

PASS: native: total warnings=1166 (== watermark 1166), native_nodevtools: total warnings=1166 (== watermark 1166)
exit=0
```

**No contradiction was found.** Every prediction P1-P4 matches its observation exactly (not
merely within a tolerance band); per the plan's own instruction, a contradiction would have
been recorded verbatim here and execution would have stopped rather than adjusting the
prediction — that branch was not taken because no divergence occurred.

P5 is not yet observable: `native_params_v131` does not exist until plan 140-04 creates it.
This document is not amended when that happens — plan 140-04's own SUMMARY is where P5 gets
its observation, if any is warranted, since predictions are recorded once and stand.

`native_params_v131` and `check_size_baseline.py --policy merge05` were **not** invoked in
this task, per the plan's explicit instruction to run only `check_build_warnings.py` on the
two pinned native envs here; the AVR flash/RAM figures cited under P1/P2 above are the ones
already produced and verified in this plan's Task 2, not re-measured here.
