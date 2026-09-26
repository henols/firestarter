---
phase: 185-records-and-checks-that-are-current
plan: 02
subsystem: infra
tags: [firmware, pio, size-baseline, fixture-hygiene, ci]

requires:
  - phase: 185-01
    provides: "size_baseline.json re-recorded to cold post-Phase-183 figures by fixture severance"
provides:
  - "an independent cold-rebuild confirmation of Plan 185-01's committed size-baseline figures, run now rather than transcribed from the same logs the record was built from"
  - "D-12 re-measured brace-aware and reversed to KEEP: the six candidate fixtures are cited in collapsed brace form and are not orphans"
affects: [185-03, 185-04, 185-05, 185-06]

actuals:
  tokens: 0
  tasks: 2
  commits: 0

tech-stack:
  added: []
  patterns: ["independent verification (transcribe-from-fresh-build, not from the capture the record was made from)", "brace-aware search before acting on a search-form-dependent premise"]

key-files:
  created: []
  modified: []

key-decisions:
  - "D-12 is reversed from DELETE to KEEP on evidence. The exact-filename search that produced D-12's premise was reproduced (zero hits for all six candidates), then a brace-aware + glob-form re-measurement found all three families cited in `tests/fixtures/README.md` and in `tests/test_check_size_baseline.py`'s module docstring. D-12's own stated criterion — a prose citation in the checker's docstring counts as a live reference and is kept — decides this as KEEP. No file was modified."
  - "Criterion 1 is proven by a fresh cold `--rebuild` run now, not by the logs Plan 185-01 transcribed the record from. The run reproduced 185-01's committed figures exactly on all five envs (uno, uno328pb, leonardo, native, native_nodevtools), completed in ~3m21s (well under the 10-15 min estimate, plausibly because the toolchain and `.pio` package cache were already warm), and left `size_baseline.json` byte-unchanged."

requirements-completed: [CLAIM-04, CLAIM-05]

coverage:
  - id: D1
    description: "An independent cold `--rebuild` run (not the capture the record was transcribed from) reproduces Plan 185-01's committed size-baseline figures exactly, proving criterion 1"
    requirement: "CLAIM-04"
    verification:
      - kind: other
        ref: "cd /workspaces/firestarter && python3 scripts/check_size_baseline.py --rebuild"
        status: pass
    human_judgment: false
  - id: D2
    description: "D-12's orphan premise re-measured brace-aware; all six candidates are cited in collapsed brace form in tests/fixtures/README.md and test_check_size_baseline.py's module docstring, so the disposition is reversed from DELETE to KEEP; nothing was deleted or modified"
    requirement: "CLAIM-05"
    verification:
      - kind: other
        ref: "cd /workspaces/firestarter && git grep -nF 'captured_build_v132_{uno,uno328pb,leonardo}.log'"
        status: pass
      - kind: other
        ref: "cd /workspaces/firestarter && git grep -nF 'captured_build_fullflash_{uno,uno328pb,leonardo}.log'"
        status: pass
      - kind: other
        ref: "cd /workspaces/firestarter && git grep -nF 'captured_build_v151_{uno,uno328pb,leonardo}.log'"
        status: pass
      - kind: other
        ref: "cd /workspaces/firestarter && python3 -m pytest tests/ -q -o addopts=\"\" (360 passed)"
        status: pass
    human_judgment: false

duration: 17min
completed: 2026-09-11
status: complete
---

# Phase 185 Plan 02: Independent Cold-Rebuild Confirmation and D-12 Brace-Aware Re-Measurement Summary

**A fresh, backgrounded `check_size_baseline.py --rebuild` reproduced Plan 185-01's committed figures exactly on all five envs, and a brace-aware re-search of the six D-12 orphan candidates found all three families cited in collapsed brace form — reversing D-12 from DELETE to KEEP, on the discretion CONTEXT.md grants for exactly this decision. Neither task modified any file.**

## Performance

- **Duration:** ~17 min
- **Started:** 2026-09-11T18:12:00Z (approx.)
- **Completed:** 2026-09-11T18:29:31Z
- **Tasks:** 2
- **Files modified:** 0

## Accomplishments

- Task 1: proved criterion 1 by an independent cold rebuild — `--rebuild`, bare, backgrounded, exit 0 — rather than by the logs the committed record was transcribed from.
- Task 2: re-measured D-12's premise with a search whose form matches the form the repository's prose actually uses, and reversed the disposition to KEEP with the evidence recorded in full.

## Task Commits

Neither task modified any file, so neither has a task-level commit — both are verification-only tasks whose `<files>` entries were explicitly conditional (Task 1: "modifies nothing"; Task 2: "under the expected disposition neither is modified").

**Plan metadata:** committed separately (this SUMMARY.md only — `firestarter/` is a submodule and its gitlink is not staged here; plan 185-06 advances it by name).

_Firmware repo `firestarter/` carries zero new commits from this plan. Its `HEAD` remains Plan 185-01's `14be84c02a49bdd456add39832d0278a80768ae4` throughout._

## Files Created/Modified

None. This plan is exclusively a verification/measurement plan; both tasks confirmed their `<files>` listings were conditional and neither condition (a divergent rebuild, a DELETE disposition) occurred.

## Task 1 Evidence — Independent cold-rebuild confirmation (D-11, CLAIM-04)

### Step 1 — Confirm the tree

```
$ cd /workspaces/firestarter && git rev-parse HEAD
14be84c02a49bdd456add39832d0278a80768ae4
$ git status --porcelain
(empty)
```

`HEAD` matches Plan 185-01's committed commit exactly; no modified tracked files (the two pre-existing untracked `datasheets/*.pdf` were also absent in this checkout).

### Step 2 — Run `--rebuild`, backgrounded

Invocation, verbatim, no other arguments (no `--baseline`, no `--policy`, no `--avr-log`):

```
cd /workspaces/firestarter && python3 scripts/check_size_baseline.py --rebuild
```

Run as a background process (`nohup ... &`, output redirected to a scratch log, exit code appended) starting at **2026-09-11T18:14:49Z**. The background job's log file was last written at **2026-09-11T18:18:10Z** — wall-clock duration **≈3m21s**. This is far under the 10-15 minute estimate in RESEARCH.md §F.2, plausibly because PlatformIO's package cache and `.pio` toolchain were already warm from Plan 185-01's own cold pass minutes earlier in the same devcontainer session.

Full captured stdout+stderr:

```
********************************************************************************
Obsolete PIO Core v6.1.19 is used (previous was 6.2.0)
Please remove multiple PIO Cores from a system:
https://docs.platformio.org/en/latest/core/installation/troubleshooting.html
********************************************************************************
Processing uno (platform: atmelavr; board: uno; framework: arduino)
--------------------------------------------------------------------------------
Verbose mode can be enabled via `-v, --verbose` option
Removing .pio/build/uno
Done cleaning
========================= [SUCCESS] Took 1.37 seconds =========================

Environment    Status    Duration
-------------  --------  ------------
uno            SUCCESS   00:00:01.367
========================= 1 succeeded in 00:00:01.367 =========================
********************************************************************************
Obsolete PIO Core v6.1.19 is used (previous was 6.2.0)
Please remove multiple PIO Cores from a system:
https://docs.platformio.org/en/latest/core/installation/troubleshooting.html
********************************************************************************
Processing uno328pb (platform: atmelavr; board: ATmega328PB; framework: arduino)
--------------------------------------------------------------------------------
Verbose mode can be enabled via `-v, --verbose` option
Removing .pio/build/uno328pb
Done cleaning
========================= [SUCCESS] Took 1.06 seconds =========================

Environment    Status    Duration
-------------  --------  ------------
uno328pb       SUCCESS   00:00:01.064
========================= 1 succeeded in 00:00:01.064 =========================
********************************************************************************
Obsolete PIO Core v6.1.19 is used (previous was 6.2.0)
Please remove multiple PIO Cores from a system:
https://docs.platformio.org/en/latest/core/installation/troubleshooting.html
********************************************************************************
Processing leonardo (platform: atmelavr; board: leonardo; framework: arduino)
--------------------------------------------------------------------------------
Verbose mode can be enabled via `-v, --verbose` option
Removing .pio/build/leonardo
Done cleaning
========================= [SUCCESS] Took 1.32 seconds =========================

Environment    Status    Duration
-------------  --------  ------------
leonardo       SUCCESS   00:00:01.324
========================= 1 succeeded in 00:00:01.324 =========================
PASS: uno(flash=22734/32768,ram=1434/2048), uno328pb(flash=22778/32768,ram=1440/2048), leonardo(flash=24830/32768,ram=1875/2560), native(cases=185,suites=17), native_nodevtools(cases=185,suites=17)
EXIT:0
```

**Note on the transcript's shape:** the `-t clean` sub-step of each AVR env's rebuild streams directly to this log (no `capture_output`), which is why only the "Removing .pio/build/&lt;env&gt;" / "Done cleaning" lines appear per env — the actual `pio run -e &lt;env&gt;` compile step is captured in memory by `_rebuild_avr` (per RESEARCH.md §F.1) and consumed internally by the comparator rather than echoed to stdout; only the final `PASS:`/`FAIL:` summary line is printed once all five envs (three AVR, two native) have been rebuilt and compared. This matches the documented mechanics exactly — no size finding was hidden by the streaming behavior, since the comparator's own summary line is the thing being classified.

### Step 3 — Classify the result

**Exit 0, one `PASS:` line naming all five envs** — this is shape 1 of the five distinguishable shapes named in the plan and RESEARCH.md §"Verification Reachability" criterion 1 (`PASS` / `FAIL` divergence / vacuous "no envs compared" / `ERROR: … could not parse` / `rc=124` timeout). **Criterion 1 is satisfied.**

### Step 4 — Reconcile against Plan 185-01

| Env | `--rebuild` (this plan) | Plan 185-01 committed | Agree? |
|---|---|---|---|
| uno flash/ram | 22734/32768, 1434/2048 | 22734, 1434 | YES |
| uno328pb flash/ram | 22778/32768, 1440/2048 | 22778, 1440 | YES |
| leonardo flash/ram | 24830/32768, 1875/2560 | 24830, 1875 | YES |
| native cases/suites | 185/17 | 185/17 | YES |
| native_nodevtools cases/suites | 185/17 | 185/17 | YES |

**Exact reproduction on every field.** No firmware `src/` change has landed since 183-04's deletion (confirmed: `HEAD` is unchanged from Plan 185-01's commit throughout this run), so the reproduction was expected and no re-run-until-agreement was needed or performed.

### Step 5 — `size_baseline.json` unmodified

```
$ git diff --exit-code -- scripts/baseline/size_baseline.json
(empty diff, exit 0)
$ git status --porcelain -- scripts/baseline/size_baseline.json tests/fixtures/ tests/test_check_size_baseline.py
(empty)
```

## Task 2 Evidence — D-12 brace-aware re-measurement and disposition (D-12, CLAIM-05)

The six candidates: `captured_build_fullflash_uno.log`, `captured_build_fullflash_uno328pb.log`, `captured_build_v132_uno.log`, `captured_build_v132_uno328pb.log`, `captured_build_v151_uno.log`, `captured_build_v151_uno328pb.log`. `leonardo` siblings are NOT candidates and are out of scope.

### Step 1 — Reproduce D-12's original measurement (exact-filename search)

```
$ cd /workspaces/firestarter
$ for f in captured_build_fullflash_uno.log captured_build_fullflash_uno328pb.log \
           captured_build_v132_uno.log captured_build_v132_uno328pb.log \
           captured_build_v151_uno.log captured_build_v151_uno328pb.log; do
    git grep -n -- "$f" | grep -v "^tests/fixtures/$f:"
  done
(no output for any of the six — 0 hits each, excluding each file's own self-match)
```

This reproduces exactly the measurement D-12 was stated on: all six exact filenames are referenced nowhere else in the tracked tree.

### Step 2 — Brace-aware and glob-form re-measurement (verbatim, with file:line)

```
$ git grep -nF -- 'captured_build_fullflash_{uno,uno328pb,leonardo}.log'
tests/fixtures/README.md:87:- **`captured_build_fullflash_{uno,uno328pb,leonardo}.log`** (`captured_`) --
tests/fixtures/README.md:146:  Retires `captured_build_fullflash_{uno,uno328pb,leonardo}.log` for the default-mode
tests/fixtures/README.md:177:leave `captured_build_fullflash_{uno,uno328pb,leonardo}.log` and its planted sibling
tests/test_check_size_baseline.py:349:captured_build_fullflash_{uno,uno328pb,leonardo}.log and its planted sibling
exit=0

$ git grep -nF -- 'captured_build_v132_{uno,uno328pb,leonardo}.log'
tests/fixtures/README.md:91:  `captured_build_v132_{uno,uno328pb,leonardo}.log` for the default-mode legs.
tests/fixtures/README.md:113:leave `captured_build_v132_{uno,uno328pb,leonardo}.log` and its planted sibling
tests/test_check_size_baseline.py:115:  captured_build_v132_{uno,uno328pb,leonardo}.log, transcribed from the committed
tests/test_check_size_baseline.py:273:  captured_build_v132_{uno,uno328pb,leonardo}.log and its planted sibling
exit=0

$ git grep -nF -- 'captured_build_v151_{uno,uno328pb,leonardo}.log'
tests/fixtures/README.md:143:- **`captured_build_v151_{uno,uno328pb,leonardo}.log`** (`captured_`) -- byte-for-byte
tests/test_check_size_baseline.py:302:family, `*_v151*`, thirteen files: `captured_build_v151_{uno,uno328pb,leonardo}.log`
exit=0
```

Glob-form searches, additionally:

```
$ git grep -nF -- 'captured_build_v132_*.log'
tests/test_check_size_baseline.py:26:  1. Clean AVR control — each of the three captured_build_v132_*.log files exits 0
tests/test_check_size_baseline.py:73:      captured_build_v132_*.log logs (SEVERED from captured_build_*.log, Phase 149

$ git grep -nF -- 'captured_build_fullflash_*.log'
tests/test_check_size_baseline.py:240:  captured_build_fullflash_*.log; test_planted_flash_regression_flips_checker_to_

$ git grep -nF -- 'captured_build_v151_*.log'
tests/fixtures/README.md:153:  numerically identical to `captured_build_v151_*.log` but read against BASE-01 under
tests/test_check_size_baseline.py:309:tree exactly, so numerically identical to captured_build_v151_*.log but read against
tests/test_check_size_baseline.py:323:test_default_mode_is_unchanged_by_the_new_flag -> the three captured_build_v151_*.log;
tests/test_check_size_baseline.py:921:    captured_build_v151_*.log but read here against BASE-01 under --policy merge05),
```

`git grep` (never a bare `grep`) was used throughout — this devcontainer's `grep` is ugrep, which honors `.gitignore` and silently under-scans, and `git grep` additionally restricts the search to tracked files only, matching the plan's mandated tooling exactly.

### Step 3 — Apply D-12's own criterion

All three collapsed-brace family names are cited in `tests/fixtures/README.md` (each family's "Retired... KEPT, not deleted" narrative section) and in `tests/test_check_size_baseline.py`'s module docstring (the severance-history paragraphs for each generation). By D-12's own stated criterion — *"prose citations in the checker's own docstring count as a live reference and are kept as prior exemptions' evidence"* (185-CONTEXT.md §D-12) — these six are **NOT orphans**.

**Disposition: KEEP. Nothing was deleted, nothing was edited.**

This also agrees with the standing in-tree decision `tests/fixtures/README.md` already records for exactly these families — each family's own "Retired, read by no leg after this severance — KEPT, not deleted" paragraph explicitly asks a future severance to apply the same reasoning rather than re-litigate it, which this task's disposition does.

### Step 4 — Record as a correction

D-12, as stated in 185-CONTEXT.md, is **revised on evidence**: `185-CONTEXT.md` § "Claude's Discretion" lists D-12 explicitly as one of the calls "a planner may revisit... on evidence," so this reversal is within the discretion CONTEXT.md grants for exactly this decision — it is not a departure from D-01 or D-04, neither of which is touched by this task. No backlog item, todo, successor guard, or tracking artefact was filed for this finding, per D-04's standing instruction ("name the gap, file nothing") applying to the whole phase.

### Verification confirmations

```
$ git ls-files -- tests/fixtures/captured_build_fullflash_uno.log tests/fixtures/captured_build_fullflash_uno328pb.log \
    tests/fixtures/captured_build_v132_uno.log tests/fixtures/captured_build_v132_uno328pb.log \
    tests/fixtures/captured_build_v151_uno.log tests/fixtures/captured_build_v151_uno328pb.log
tests/fixtures/captured_build_fullflash_uno.log
tests/fixtures/captured_build_fullflash_uno328pb.log
tests/fixtures/captured_build_v132_uno.log
tests/fixtures/captured_build_v132_uno328pb.log
tests/fixtures/captured_build_v151_uno.log
tests/fixtures/captured_build_v151_uno328pb.log
# count: 6 — consistent with KEEP (all six paths still tracked)

$ python3 -m pytest tests/ -q -o addopts=""
360 passed in 25.03s

$ git status --porcelain -- tests/fixtures/ tests/test_check_size_baseline.py
(empty)
```

All four of Task 2's `<verify>` checks pass under the KEEP disposition exactly as its `<fails_when>` clauses require.

## Decisions Made

See `key-decisions` in frontmatter. Both decisions were reached by measurement rather than by inheriting the planner's prediction: Task 1's reproduction was independently re-run (not assumed from RESEARCH.md's prediction), and Task 2's disposition was independently re-derived from a fresh `git grep`, even though the plan's own `<flagged_assumptions>` section noted the planner had already found the same brace-form citations at planning time.

## Deviations from Plan

None — plan executed exactly as written. Both tasks' expected outcomes (exact reproduction; KEEP disposition) occurred, matching the plan's own stated expectations, and both were independently re-measured rather than assumed.

## Issues Encountered

None. The `--rebuild` pass completed in ~3m21s rather than the estimated 10-15 minutes — not an issue, just faster than planned for, plausibly due to a warm PlatformIO cache carried over from Plan 185-01's cold pass in the same session. It was still run backgrounded per the plan's mandatory instruction, since the estimate at authoring time could not assume a warm cache.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

Criterion 1 is now proven by a build run taken now, not by the transcript the record was copied from, and D-12's disposition is settled by a search whose form matches the form the repository's prose actually uses. Both CLAIM-04 and CLAIM-05 have full evidence trails. `firestarter/` remains at Plan 185-01's commit `14be84c02a49bdd456add39832d0278a80768ae4` (no new firmware commit from this plan). Ready for plan 185-03 and the rest of this phase's work. No blockers.

## Self-Check: PASSED

- `firestarter` `HEAD` = `14be84c02a49bdd456add39832d0278a80768ae4`, matching Plan 185-01's committed sha — confirmed via `git -C /workspaces/firestarter rev-parse HEAD`.
- `firestarter/scripts/baseline/size_baseline.json` unmodified — confirmed via `git diff --exit-code`, empty.
- `firestarter` working tree clean over `tests/fixtures/`, `tests/test_check_size_baseline.py`, `scripts/baseline/size_baseline.json` — confirmed via `git status --porcelain`, empty.
- All six D-12 candidate fixtures remain tracked (`git ls-files`, count 6) — consistent with the recorded KEEP disposition.
- `python3 -m pytest tests/ -q -o addopts=""` reports `360 passed` — matching Plan 185-01's post-commit whole-suite count exactly.

---
*Phase: 185-records-and-checks-that-are-current*
*Completed: 2026-09-11*
