---
phase: 140-parameter-table
verified: 2026-08-10T03:36:42Z
status: passed
score: 9/9 must-haves verified (4 ROADMAP success criteria + 5 requirement IDs; 0 overrides)
overrides_applied: 0
---

# Phase 140: Parameter Table Verification Report

**Phase Goal:** A single per-`protocol_id` table defines each 27C algorithm's shape — never its
pulse width — without introducing a second dispatch key or a new database field.
**Verified:** 2026-08-10T03:36:42Z
**Status:** passed
**Re-verification:** No — initial verification

## Methodology note

This report does not take SUMMARY.md or 140-PARAM-TABLE-RECORD.md claims at face value. Every
row below reflects a command **I executed myself** in this session against the live submodule
working trees (`firestarter/`, `firestarter_app/`, both on `gsd/v1.31-27c-programming-algorithm-fidelity`),
not a re-statement of a prior transcript. Where the plans required a D-15 planted-violation proof,
I independently re-planted three of the twelve violations myself (one per new gate, in fresh
`mktemp -d` scratch directories, deleted immediately after) rather than trusting the SUMMARY's
own transcript.

## Goal Achievement

### Observable Truths — the four ROADMAP Success Criteria (the actual contract)

| # | Truth (ROADMAP SC) | Status | Evidence |
|---|---------|--------|----------|
| 1 | A `const` table keyed by `protocol_id` carries one row each for `0x07`/`0x08`/`0x0B` with `max_pulses`, `overprogram_factor`, `overprogram_cap_us`, `verify_mode`, `vpp_path` — and no pulse-width column exists anywhere in it. | VERIFIED | Read `firestarter/include/eprom_params.h` (84 lines) and `firestarter/src/proms/eprom_params.cpp` (62 lines) directly: `eprom_params_t` has exactly the 6 named fields in largest-first order, `static_assert(sizeof==12)`, and `EPROM_PARAM_KEYS[]`/`EPROM_PARAMS[]` carry exactly 3 rows (`0x07`,`0x08`,`0x0B`) with no `switch`. Independently planted a `fallback_pulse_us` field into a scratch copy of the header and re-ran the citation gate with `FIRESTARTER_PARAMS_HEADER` — it went RED on `test_struct_field_names_are_exactly_the_frozen_six_in_order` and `test_no_pulse_width_column_exists` (5 of 10 tests failed, naming the extra field), then confirmed the real tree is clean (10/10 pass). Verified the "max_pulses substring trap" is handled correctly: `test_no_pulse_width_column_exists` asserts both a negative regex (`(?i)(pulse_(width|delay|us)\|fallback_pulse)`, which does not match `max_pulses`) AND a positive "only `max_pulses` contains 'pulse'" check. |
| 2 | Every write path reads the program pulse width from `handle->pulse_delay`; a protocol's constant pulse value is consulted only when `pulse_delay == 0`, and a test exercises that fallback rather than merely asserting it. | VERIFIED | `git -C firestarter diff 67d6061 HEAD -- src/proms/eprom.cpp` is 0 lines — the fallback switch at `eprom.cpp:70-75` (`if (handle->pulse_delay == 0) { switch(handle->protocol) { case 0x08: 100; case 0x0B: 500; default: 1000; } }`) is byte-identical to before Phase 140 began (D-10 holds). Ran `pio test -e native_params_v131` myself (cold): **9 test cases: 9 succeeded**, exit 0. Read the suite's source: cases 1-3 call the real `configure_memory()` → `configure_eprom()` path on a `pulse_delay=0` handle and assert 1000/100/500; cases 4-6 are the non-vacuity negative controls (`pulse_delay=777` survives untouched) — without which 1-3 could pass vacuously. This is a running behavioural test, not prose. |
| 3 | Every value in every row cites a named primary datasheet or carries an explicit "no datasheet basis — reasoned from X" note — no unattributed number ships. | VERIFIED | `firestarter/tests/golden/eprom_params_citations.json` has exactly 18 cells (12 `datasheet` + 6 `reasoned`, confirmed by my own `python3 -c` parse), each `datasheet` cell has non-empty `family`/`part`/`document`/`revision`/`section`/`quote`/`scope` with the literal D-09 scope sentence, each `reasoned` cell's `reasoned_from` starts with the exact string `no datasheet basis — reasoned from `. Ran `test_eprom_params_citations.py` myself: **10 passed**, including the bijection test (`test_citations_cover_every_cell_exactly_once`) and the value-drift test (`test_recorded_values_match_the_live_table`). |
| 4 | `chip_database.json` gains no new field and firmware gains no second algorithm selector — `protocol_id` remains the sole dispatch key, verified by a committed gate rather than by inspection. | VERIFIED | Two independent, split gates exist and run for the right reason: (a) firmware half — `firestarter/tests/test_protocol_branch_inventory.py`, ran myself: **7 passed**; independently planted `if (handle->protocol == 0x07) { }` into a scratch copy of `eprom.cpp` and re-ran with `FIRESTARTER_BRANCH_SCAN_SOURCE` — went RED (2 of 7 failed, naming the new line-146 protocol-keyed site and the resulting 4-site count) — then confirmed the real tree is clean (7/7). (b) DB half — `firestarter_app/tests/test_chip_database_field_inventory.py`, ran myself: **8 passed**; independently planted a `"foo": 1` key into one chip's `programming` object in a scratch DB copy and re-ran with `FIRESTARTER_CHIP_DB_JSON` — went RED (`test_programming_field_inventory_matches` named `added={'foo': 1}`) — then confirmed clean (8/8). `git diff --quiet -- firestarter/data/chip_database.json tools/build_db.py` exits 0 (byte-unchanged all phase). `eprom_params.cpp` contains zero `switch` statements (grepped directly). |

**Score:** 4/4 ROADMAP success criteria verified.

### Requirements Coverage (TABLE-01..05 cross-referenced against REQUIREMENTS.md)

All five requirement IDs declared across the seven plans' frontmatter (`TABLE-01` in 140-01/04/05;
`TABLE-02` in 140-01/05; `TABLE-03` in 140-04; `TABLE-04` in 140-05/06; `TABLE-05` in 140-02/03) are
present in `.planning/REQUIREMENTS.md` § "Parameter Table" and its Traceability table, and in
`.planning/ROADMAP.md`'s Traceability table — no orphaned requirement exists for Phase 140 beyond
these five (`grep -n "Phase 140" REQUIREMENTS.md` returns exactly the five TABLE rows).

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| TABLE-01 | 140-01, 140-04, 140-05 | `const` `protocol_id`-keyed table, 3 rows, 5 named columns | SATISFIED | Header/TU exist and compile; `native_params_v131` cases 7 (distinct-row resolution) and 9 (frozen values) pass; citation gate's field-name freeze passes. `- [x]` in REQUIREMENTS.md; `Complete` in both Traceability tables. |
| TABLE-02 | 140-01, 140-05 | No pulse-width column; pulse width from `handle->pulse_delay` | SATISFIED | `test_no_pulse_width_column_exists` passes (verified non-vacuous by my own planted-field run); `eprom.cpp`'s fallback switch confirmed byte-unchanged. `- [x]`/`Complete`. |
| TABLE-03 | 140-04 | Fallback consulted only at `pulse_delay==0`, exercised not asserted | SATISFIED | `native_params_v131` cases 1-6 (3 positive + 3 negative-control) ran and passed under my own cold invocation. Record correctly states no bench oracle exists (0/329 chips yield `pulse_delay==0`) — this is stated, not a gap. `- [x]`/`Complete`. |
| TABLE-04 | 140-05, 140-06 | Every value cited or reasoned; docs reconciled | SATISFIED | 18-cell sidecar + 10-test gate pass; `doc/PROTOCOLS.md` and `CLAUDE.md` no longer contain the disproven claims (`3× overpulse`, `Same Intelligent Programming`, `1ms pulse, DQ7 verify`, `12–18V direct`) — confirmed with byte-exact UTF-8 string search, not an ASCII-only grep (avoiding the exact `×`-vs-`x` fail-open trap this phase's own CONTEXT names). `- [x]`/`Complete`. |
| TABLE-05 | 140-02, 140-03 | No new DB field, no second algorithm selector, gate-verified | SATISFIED | Both split gates pass and were independently proven non-vacuous by my own planted violations (see Truth 4 above). `- [x]`/`Complete`. |

**Orphan check:** `TEST-01` ("Native tests prove `0x07`/`0x08`/`0x0B` each resolve to their own
table row") remains `[ ]` / `Pending` in both `REQUIREMENTS.md` and `ROADMAP.md`, correctly NOT
flipped by this phase even though `native_params_v131` case 9 proves part of its content — this
matches the plan's explicit "TEST-01 belongs to Phase 144" instruction. Confirmed by direct grep.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/include/eprom_params.h` | type+enums+accessor decl, ≥40 lines | VERIFIED | 84 lines; no `Arduino.h`/`rurp_shield.h`; `static_assert(sizeof==12)` present |
| `firestarter/src/proms/eprom_params.cpp` | PROGMEM table + accessor, ≥45 lines | VERIFIED | 62 lines; no `Arduino.h`, no `switch`; `pio run -e uno/uno328pb/leonardo` all SUCCESS (ran cold myself) |
| `.planning/phases/140-parameter-table/140-PREDICTIONS.md` | pre-measurement predictions | VERIFIED | Committed at `a2705cfb0...` before any cold run; P1-P4 independently re-measured by me this session and matched exactly (flash 23954/24004/26016, RAM 1573/1579/2014, warnings 1166/1166, 141/17 both envs) |
| `firestarter/tests/golden/protocol_branch_inventory.json` | two-tier inventory, ≥60 lines | VERIFIED | 280 lines; 24 sites (3 protocol + 21 other), matches floor set exactly |
| `firestarter/tests/test_protocol_branch_inventory.py` | 7-test D-13 gate, ≥180 lines | VERIFIED | 565 lines; 7/7 passed; independently seen RED on a planted violation (this session) |
| `firestarter_app/tests/golden/chip_database_field_inventory.json` | frozen inventory, ≥50 lines | VERIFIED | 86 lines; totals `{manufacturers:59, chips:746}` confirmed live |
| `firestarter_app/tests/test_chip_database_field_inventory.py` | 8-test DB gate, ≥170 lines | VERIFIED | 445 lines; 8/8 passed; independently seen RED on a planted violation (this session) |
| `firestarter/platformio.ini` → `[env:native_params_v131]` | 5th native env, own suite only | VERIFIED | `test_filter` names exactly `native/avr/test_eprom_params_v131`; not in `default_envs` (`uno, uno328pb, leonardo`); not between `[env:native]`/`[env:native_nodevtools]` markers |
| `firestarter/test/native/avr/test_eprom_params_v131/{host_stubs.cpp,test_eprom_params_v131.cpp}` | pass-through stub + 9 Unity cases | VERIFIED | 38 + 220 lines; `RUN_TEST` count = 9 = reported case count; ran cold, 9/9 succeeded |
| `firestarter/tests/golden/eprom_params_citations.json` | 18-cell sidecar, ≥120 lines | VERIFIED | 264 lines; 18 cells, bijection over 3 rows × 6 columns confirmed programmatically |
| `firestarter/tests/test_eprom_params_citations.py` | 10-test gate, ≥200 lines | VERIFIED | 558 lines; 10/10 passed |
| `firestarter/doc/PROTOCOLS.md` (§§1.3-1.5 correction) | corrected claims, cites sidecar | VERIFIED | `eprom_params_citations.json` referenced ≥4×; disproven claims removed (byte-exact check) |
| `firestarter/CLAUDE.md` (Algorithm Handlers correction) | corrected Notes/VPP cells, D-11 exception | VERIFIED | Old claims gone; `native_params_v131` D-11 exception present; zero `SHARED:S` lines touched (verified via correct-scope diff, not the commit-message false-positive) |
| `.planning/phases/140-parameter-table/140-PARAM-TABLE-RECORD.md` | phase close record, ≥120 lines | VERIFIED | 281 lines; all 11 required sections present; names both divergences (F-140-05, D-06/0x08 contradiction) |
| `.planning/REQUIREMENTS.md` / `.planning/ROADMAP.md` | TABLE-01..05 flipped, only those | VERIFIED | Diff scoped to exactly 16 changed lines across both files (5+5 in REQUIREMENTS.md, 1+5 in ROADMAP.md); `PROJECT.md` byte-unchanged; no `LOOP-*`/`VPP-*`/`HOST-*`/`TEST-*`/`BENCH-*`/`CLOSE-*` row touched |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `eprom_params.cpp` | `eprom_params.h` | sole `#include` | WIRED | Confirmed by direct read; no other include |
| `eprom_params.h` | `rurp_platform_compat.h` | PROGMEM/pgm_read_* shims | WIRED | Confirmed; compiles identically on `pio run -e uno` (AVR) and `pio test -e native_params_v131` (host) |
| `test_protocol_branch_inventory.py` | `src/proms/eprom.cpp` | live re-parse | WIRED | Confirmed non-vacuous by planting a violation and observing the correct RED |
| `test_chip_database_field_inventory.py` | `chip_database.json` + `tools/build_db.py` | two-level traversal + `ast` scan | WIRED | Confirmed non-vacuous by planting a violation in each and observing the correct RED (a generator-only planted key was not separately re-tested by me but was confirmed present as Run D in `140-03-SUMMARY.md`'s verbatim transcript, cross-checked against the actual gate code) |
| `test_eprom_params_citations.py` | `eprom_params.h` + `eprom_params.cpp` | live re-parse | WIRED | Confirmed non-vacuous by planting a pulse-width field and observing correct RED |
| `platformio.ini` `[env:native_params_v131]` | `test/native/avr/test_eprom_params_v131` | positive `test_filter` allowlist | WIRED | `pio test -e native_params_v131` finds and runs the suite; not reachable via `[env:native]` |
| `140-PARAM-TABLE-RECORD.md` | `140-PREDICTIONS.md` | prediction-vs-measurement reconciliation | WIRED | Commit SHA `a2705cfb0...` quoted and precedes every measurement I re-ran, which matched |

### Data-Flow Trace (Level 4)

Not applicable in the UI/API sense this check targets. Phase 140 ships a firmware constant table
(PROGMEM), test gates, and documentation — there is no rendered UI or API response to trace. The
closest analog is "does the table's data reach a consumer," which is explicitly and correctly
**not yet true** by design (D-10: `src/` does not reference the table this phase; Phase 141 wires
it in). This is stated in the phase record §9 and is not a gap for a phase whose own success
criteria and locked scope explicitly exclude wiring.

### Behavioral Spot-Checks (self-executed this session, not taken from SUMMARY.md)

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| TABLE-03 fallback genuinely exercised | `pio test -e native_params_v131` (cold) | `9 test cases: 9 succeeded` | PASS |
| Pinned env `native` unmoved | `pio test -e native` (cold) | `141 test cases: 141 succeeded`, 17 suite rows | PASS |
| Pinned env `native_nodevtools` unmoved | `pio test -e native_nodevtools` (cold) | `141 test cases: 141 succeeded`, 17 suite rows | PASS |
| D-10 frozen trace still green | `pio test -e native_trace_v131` (cold) | `5 test cases: 5 succeeded` | PASS |
| Warning watermark unmoved | `check_build_warnings.py --log native=... --log native_nodevtools=...` | `PASS: ... total warnings=1166 ... total warnings=1166` | PASS |
| AVR builds still succeed | `pio run -e uno/uno328pb/leonardo` (cold, all 3) | all `SUCCESS` | PASS |
| AVR flash/RAM delta reconciles to 0 | `check_size_baseline.py` (default seam) | `PASS: uno(flash=23954/32256...)...` exit 0 | PASS |
| MERGE-05 band holds | `check_size_baseline.py --policy merge05 --baseline size_baseline_base01.json` | `PASS: uno(...[+22<=64],ram=...[=])...` exit 0 | PASS |
| Firmware pytest suite | `pytest tests/ -q` (firestarter) | `244 passed` | PASS |
| App pytest suite | `pytest tests/ -o addopts="" -q` (firestarter_app) | `1547 passed` | PASS |
| Branch-inventory gate | `pytest tests/test_protocol_branch_inventory.py -v` | `7 passed` | PASS |
| Citation gate | `pytest tests/test_eprom_params_citations.py -v` | `10 passed` | PASS |
| DB field-inventory gate | `pytest tests/test_chip_database_field_inventory.py -o addopts="" -v` | `8 passed` | PASS |
| Citation gate non-vacuous (self-planted) | pulse-width field injected into scratch header + `FIRESTARTER_PARAMS_HEADER` | `5 failed, 5 passed`, named the planted field | PASS (gate correctly RED) |
| Branch gate non-vacuous (self-planted) | protocol-keyed branch injected into scratch `eprom.cpp` + `FIRESTARTER_BRANCH_SCAN_SOURCE` | `2 failed, 5 passed`, named line 146 and the 4-site count | PASS (gate correctly RED) |
| DB gate non-vacuous (self-planted) | `"foo":1` injected into one chip's `programming` object + `FIRESTARTER_CHIP_DB_JSON` | `1 failed, 7 passed`, named `added={'foo': 1}` | PASS (gate correctly RED) |
| `eprom.cpp` byte-unchanged (D-10) | `git diff 67d6061 HEAD -- src/proms/eprom.cpp` | 0 lines | PASS |
| `chip_database.json`/`build_db.py` byte-unchanged | `git diff --quiet -- firestarter/data/chip_database.json tools/build_db.py` | exit 0 | PASS |
| Baselines byte-unchanged | `git diff --quiet -- scripts/baseline/ src/proms/eprom.cpp` | exit 0 | PASS |
| CMake manifest gate (collateral fix) | `python3 scripts/check_cmake_manifest.py` | `PASS: ... 27 enforced source(s) resolved ...` exit 0 | PASS |
| Working trees left clean after my own testing | `git status --porcelain` (firestarter) | empty | PASS |

### Probe Execution

Not applicable. No `scripts/*/tests/probe-*.sh` convention exists in either repository, and neither
the PLAN nor SUMMARY files for this phase declare a probe script. (Step 7c correctly skipped.)

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter/platformio.ini` | 77 | `TODO(v1.5)` | INFO | Pre-existing (introduced commit `fd087f1`, unrelated v1.5-era note about a Unity teardown SIGABRT), outside the diff range Phase 140 touched (140-04 only appended `[env:native_params_v131]` near line 331). Not introduced or touched by this phase. |
| `firestarter/doc/PROTOCOLS.md` | 401 | "not available on current RURP Rev 2.x hardware... No handler will be committed" | INFO | Pre-existing prose (git blame: 2026-07-01, well before Phase 140), inside an out-of-scope §2.x section Phase 140's plan explicitly excludes. Not a stub introduced by this phase. |

No `FIXME`, `XXX`, `TBD`, `HACK`, or `PLACEHOLDER` markers exist in any file this phase created or
modified. No debt-marker gate triggered.

### Human Verification Required

None. This phase ships firmware constants, test gates, and documentation corrections — no UI, no
real-time behavior, no external service integration, and no ambiguous behavior requiring human
judgment. The one item that could have needed a human call (the `0x07 overprogram_factor` value,
where datasheets disagree with `PROJECT.md`'s throughput table) was already resolved by an explicit
operator decision recorded in this same session (2026-08-09, quoted in the phase record §3) — I
verified that decision is correctly implemented and cited, not that it needs to be re-litigated.

### Gaps Summary

None found. All four ROADMAP success criteria and all five requirement IDs (TABLE-01 through
TABLE-05) are independently verified against the live codebase, not merely asserted by
SUMMARY.md/140-PARAM-TABLE-RECORD.md prose. Every regression baseline this phase was required to
leave unmoved (native/native_nodevtools 141 cases/17 suites, warning watermark exactly 1166,
`native_trace_v131` 5/5, AVR flash/RAM deltas reconciling to the pre-committed P1-P4 predictions,
`eprom.cpp`/`chip_database.json`/`tools/build_db.py`/`scripts/baseline/*` byte-unchanged) was
re-measured cold by me this session and matched exactly. All three new gates (D-13 branch
inventory, D-12 DB field inventory, D-14 citation coverage) were proven non-vacuous by violations I
planted myself in scratch directories — independent of, and consistent with, the SUMMARY.md's own
recorded planted-violation transcripts. The known, accepted limitations (no bench oracle for
TABLE-03; `native_params_v131`/`native_trace_v131` run in no CI leg; `check_mypy_watermark.py`'s
pre-existing devcontainer numpy conflict; wiring deferred to Phase 141 by D-10; F-140-05 and
F-140-07 divergences deferred to Phase 146) are all correctly stated in-repo rather than hidden, and
are not treated as gaps here per the task's explicit guidance.

---

*Verified: 2026-08-10T03:36:42Z*
*Verifier: Claude (gsd-verifier)*
