---
phase: 144-tests-build-verification
verified: 2026-08-14T11:04:04Z
status: passed
score: 8/8 must-haves verified
overrides_applied: 0
---

# Phase 144: Tests & Build Verification — Verification Report

**Phase Goal:** Native, host, and cross-repo test suites all prove the new table-driven per-byte algorithm's behavior, the golden-trace shift is deliberate and named rather than blanket-applied, and per-target size cost is measured against the pre-change baseline.
**Verified:** 2026-08-14T11:04:04Z
**Status:** passed
**Re-verification:** No — initial verification

## Method

This report is built entirely from commands independently re-run against the live submodule
checkouts (`/workspaces/firestarter` @ `a594173`, `/workspaces/firestarter_app` @ `68820a6`, both on
`gsd/v1.31-27c-programming-algorithm-fidelity`), not from re-stating `144-TEST-RECORD.md`'s prose.
Every figure below was reproduced live in this session; where a figure could not be reproduced
without a bench (none applicable here), that is stated. No file under `firestarter/src/` was found
modified (`git diff --name-only 59a8a42..HEAD -- src/` → empty), consistent with D-04.

## Goal Achievement

### Observable Truths (mapped to ROADMAP Success Criteria 1-4 and TEST-01..08)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | TEST-01: `0x07`/`0x08`/`0x0B` each resolve to their own table row | VERIFIED | Re-ran `pio test -e native_params_v131` live: **9/9 passed**, including `test_each_protocol_resolves_to_its_own_distinct_row`, `test_row_values_match_the_frozen_table`. Matches TEST-RECORD exactly. |
| 2 | TEST-02: fixed-width pulse/verify per byte, no width escalation between attempts | VERIFIED | Read `test_loop01_pulse_width_never_grows_between_attempts` source — asserts every `delayMicroseconds` entry is one of {1,3,100}us and any 4th distinct value would fail; re-ran `pio test -e native_loop_v131`: **79/79 passed**. |
| 3 | TEST-03: overprogram duration derives from successful byte's pulse count, honours the cap | VERIFIED (bounded) | Read `test_loop03_overprogram_duration_is_three_times_the_pulse_count_times_the_width` — direct pure-function proof of `eprom_overprogram_us()`. Confirmed via code read that no shipped row sets `overprogram_factor != 0` (`eprom_params.cpp:46-48`), so `test_loop04_no_live_row_emits_an_overprogram_pulse` correctly witnesses the in-loop-wiring-on-live-data non-claim (D-03) rather than hiding it. Per verification constraints, this bounded claim is not a gap. |
| 4 | TEST-04: max-pulse failure aborts the block, reports the address, disables every HV route | VERIFIED (register-stream-scoped) | Read `test_loop05_a_byte_that_misses_within_max_pulses_aborts_the_block` — asserts bytes after the failing byte are never touched (abort), and a `u24` address + `u8` pulse-count payload on `MSG_ERR_MAX_PULSES` (reports address). Read `test_loop05_the_loops_own_strobes_disable_the_high_voltage_route` — asserts the LAST control-register write clears both `CTRL_VPP_REGULATOR_ENABLE` and the drop bit, with an explicit non-vacuity check that an earlier write had them SET (avoiding the "never energised" vacuity trap) and a documented reason the assertion is scoped to `eprom_write_execute`'s own strobes rather than `command_done()`'s blanket clear. Bounded correctly to the emitted register stream, not real silicon, per the phase's own D-03/non-claims section. |
| 5 | TEST-05: `0xFF`/already-matching skips, `pulse_delay==0` fallback | VERIFIED | Read `test_loop06_an_ff_target_byte_is_never_read_and_never_pulsed` — asserts zero reads for an `0xFF` target byte. Re-ran `native_params_v131`: all six `test_0x{07,08,0B}_{zero,nonzero}_pulse_delay_*` fallback cases pass (the corrected 6-case shape per C-04, not CONTEXT's phantom "two cases"). |
| 6 | TEST-06: pre-change trace frozen, new trace authored, diff attributed per-strobe | VERIFIED | `git rev-parse HEAD:test/native/avr/_shared/eprom_v131_expected_prechange.h` → `ca3e09f164e6e1c541ecb63d15bbebf5bce41d70` (exact match to the Phase 138 blob). Re-ran `pio test -e native_trace_v131`: **5/5 passed, 0 failed**. Re-ran `test_trace_segment_exhaustiveness_v131.py`: **11/11 passed** — the six-segment, 885-entry, set-equality attribution gate. Re-ran `test_golden_trace_identity_eprom_v131.py`: **6/6 passed**. |
| 7 | TEST-07: `uno`/`uno328pb`/`leonardo`/`native` build+pass; host suite passes; CI-scoped ruff/mypy clean; constants parity holds | VERIFIED | Re-built all three AVR targets live: `uno` 24824/32256 flash, 1573/2048 RAM; `uno328pb` 24874/32384, 1579/2048; `leonardo` 26906/28672 (93.8%), 2014/2560 — all SUCCESS, exact match to TEST-RECORD. Re-ran `pio test -e native`: **141/141 passed**. Re-ran host `test_cap03_ack_layout_parity.py` + `test_revision_constants_parity.py`: **26 passed** (present path); absent-path child process (`FIRESTARTER_FW_ROOT` at a verified-empty dir): **6 passed, 8 skipped** exact match. Re-ran `.venv/ci-replica/bin/ruff check`/`format --check`/`check_mypy_watermark.py`/full `pytest --cov` on Python 3.11.15: all four exit 0, **1590 passed, 82.92% coverage** — byte-for-byte match to TEST-RECORD §3.9. Confirmed `ci.yml` lines 81/84/87/90 are exactly these four commands. |
| 8 | TEST-08: flash/RAM delta measured vs. PREP-03 baseline; Leonardo ceiling checked explicitly | VERIFIED | Re-ran `check_size_baseline.py` (strict identity) against the committed `captured_build_*.log` fixtures: `PASS: uno(...24824/32256...), uno328pb(...24874/32384...), leonardo(...26906/28672...)` exit 0 — exact match. Re-ran `--policy merge05 --baseline size_baseline_base01.json`: `PASS ... [+0<=64] ... [+0<=0]` exit 0 — exact match. Leonardo ceiling independently recomputed: 26906/28672 = 93.8%, 1766B headroom, matching the record's explicit statement (not a discovered-after-the-fact figure — the ceiling is named in the record's §2.1 alongside the measurement). |

**Score:** 8/8 truths verified (all bounded/scoped claims match the constraints supplied for this verification — none are unbounded overclaims).

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/tests/test_requirement_case_mapping_v131.py` | D-01 mapping gate, 805 lines | VERIFIED | 805 lines confirmed; 9/9 tests pass live, including both D-18 planted-violation legs (`test_planted_renamed_case_is_detected`, `test_planted_emptied_scan_root_fails_the_non_vacuity_leg`). |
| `firestarter/tests/test_trace_segment_exhaustiveness_v131.py` | D-07 exhaustiveness gate, 1234 lines | VERIFIED | 1234 lines confirmed; 11/11 tests pass live. |
| `firestarter/test/native/avr/_shared/eprom_v131_expected_prechange.h` | Frozen Phase-138 trace, byte-identical | VERIFIED | Blob hash `ca3e09f164e6e1c541ecb63d15bbebf5bce41d70` reproduced live via `git rev-parse HEAD:...`. |
| `firestarter/test/native/avr/_shared/eprom_v131_expected.h` | Fresh trace at this phase's tip, 91/115/59 | VERIFIED (indirect) | Exhaustiveness gate's live pass (11/11), which parses and set-checks this exact file against 265 total new entries, is the operative proof; file exists and is included by `test_trace_eprom_v131`, itself passing 5/5 live. |
| `firestarter_app/tests/test_cap03_ack_layout_parity.py` | Cross-repo CAP-03 layout parity gate | VERIFIED | Exists, 12/12 tests pass live (part of the 26-passed present-path run), including both planted-violation legs against committed fixtures `planted_cap03_literal_index.cpp` / `planted_cap03_truncated_length.cpp` (both present on disk). |
| `firestarter/scripts/baseline/size_baseline.json`, `size_baseline_base01.json`, `size_baseline_v131.json` | Re-anchored to v1.31 tip; `size_baseline_v131.json` gains `native_loop_v131`/`native_params_v131` records | VERIFIED | Live JSON read confirms `native_envs` block in `size_baseline_v131.json` contains both new records (79/79/2/true and 9/9/1/true); strict-identity and merge05 checker runs both PASS at zero delta against the current tree. |
| `.planning/phases/144-tests-build-verification/144-TEST-RECORD.md` | Phase record, 568 lines | VERIFIED | 568 lines confirmed (`wc -l`); every verbatim transcript in it that was independently re-run in this session reproduced exactly. |
| `.planning/REQUIREMENTS.md` (TEST-01..08 ticked) | Both the checklist and the traceability-matrix table show Complete | VERIFIED | Checklist rows 228-243 all `[x]`; traceability-matrix rows 326-333 all `Complete` (the latter closed by a follow-up hand commit `dc5dd5a4` after the original 144-07-SUMMARY.md was written — a minor SUMMARY staleness, not a functional gap; see Anti-Patterns/Notes). |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `test_requirement_case_mapping_v131.py` | `test/native/avr/test_{loop,vpp,eprom_params}_eprom_v131/*.cpp` | `FIRESTARTER_CASE_MAP_SCAN_ROOT` import-time seam | WIRED | Live run passes 9/9; two planted child-process legs prove the seam is load-bearing, not decorative. |
| `test_cap03_ack_layout_parity.py` | `firestarter/src/firestarter.cpp` | `fw_path("src","firestarter.cpp")` behind `requires_fw` | WIRED | Present-path run reads real firmware source live and passes 12/12; absent-path run (verified separately) skips cleanly rather than erroring. |
| `test_trace_segment_exhaustiveness_v131.py` | `eprom_v131_expected.h` + `eprom_v131_expected_prechange.h` | `FIRESTARTER_TRACE_SEGMENT_SCAN_NEW`/`_PRECHANGE` seams | WIRED | Live run passes 11/11, including both planted-violation legs against real parsed arrays. |
| `check_size_baseline.py` | `captured_build_*.log` / `size_baseline*.json` | `--avr-log`/`--baseline` CLI flags | WIRED | Live invocation with the committed log fixtures reproduces the exact PASS transcripts recorded in the TEST-RECORD. |
| `.planning/REQUIREMENTS.md` / `.planning/ROADMAP.md` | `144-TEST-RECORD.md` | Hand-edit citing the record, snapshot-and-diff scoped | WIRED | `git show --stat` on both flip commits confirms a scoped 16/18-line diff touching only the eight `TEST-0N` rows and the phase's own plan checkboxes — no other requirement row moved. |

### Behavioral Spot-Checks / Probe Execution

All of the following were executed live in this session (not narrated from SUMMARY.md):

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Native params suite | `pio test -e native_params_v131` | 9 test cases: 9 succeeded | PASS |
| Native loop+VPP suite | `pio test -e native_loop_v131` | 79 test cases: 79 succeeded | PASS |
| Native trace suite | `pio test -e native_trace_v131` | 5 test cases: 5 succeeded, 0 failed | PASS |
| Pinned native suite | `pio test -e native` | 141 test cases: 141 succeeded | PASS |
| AVR builds | `pio run -e uno / uno328pb / leonardo` | All 3 SUCCESS, figures exact match | PASS |
| Firmware pytest | `python3 -m pytest tests/ -q` | 312 passed | PASS |
| Mapping gate | `pytest tests/test_requirement_case_mapping_v131.py` | 9 passed | PASS |
| Exhaustiveness gate | `pytest tests/test_trace_segment_exhaustiveness_v131.py` | 11 passed | PASS |
| Identity gate | `pytest tests/test_golden_trace_identity_eprom_v131.py` | 6 passed | PASS |
| Protocol-branch inventory (D-04) | `pytest tests/test_protocol_branch_inventory.py` | 7 passed | PASS |
| Size-baseline + build-warnings gates | `pytest tests/test_check_size_baseline.py tests/test_check_build_warnings.py` | 22 passed | PASS |
| size_baseline.py, strict identity | `check_size_baseline.py --avr-log ...` (captured logs) | PASS: exact figures | PASS |
| size_baseline.py, merge05 | `check_size_baseline.py --policy merge05 ...` | PASS: `[+0<=64]`/`[+0<=0]` | PASS |
| Host CAP-03 + constants parity, present | `pytest tests/test_cap03_ack_layout_parity.py tests/test_revision_constants_parity.py` | 26 passed | PASS |
| Host constants parity, absent-path | child process, `FIRESTARTER_FW_ROOT` empty dir | 6 passed, 8 skipped | PASS |
| ruff/format/mypy (ci-replica 3.11.15) | 3 commands per `ci.yml` :81/:84/:87 | All checks passed / 135 formatted / 33≤35 watermark | PASS |
| Full host suite + coverage (ci-replica 3.11.15) | `pytest tests/ --cov=firestarter --cov-fail-under=70` | 1590 passed, 82.92% coverage | PASS |

No probe was skipped; no probe required a bench/hardware connection.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| TEST-01 | 144-01/144-05/144-07 | `0x07`/`0x08`/`0x0B` resolve to own table row | SATISFIED | `native_params_v131` 9/9 live |
| TEST-02 | 144-01/144-05/144-07 | fixed-width pulse/verify, no escalation | SATISFIED | `native_loop_v131` (loop01 cases) live |
| TEST-03 | 144-01/144-05/144-07 | overprogram duration from pulse count, honours cap | SATISFIED (bounded) | `native_loop_v131` (loop03 cases) live; D-03 non-claim correctly disclosed |
| TEST-04 | 144-01/144-05/144-07 | max-pulse abort/address-report/route-disable | SATISFIED (register-stream-scoped) | `native_loop_v131`+`native_vpp` (loop05/vpp02) live |
| TEST-05 | 144-01/144-05/144-07 | `0xFF`/matching skip, zero-delay fallback | SATISFIED | `native_params_v131`+`native_loop_v131` (loop06, fallback cases) live |
| TEST-06 | 144-03/144-04 | golden trace freeze+fresh+attributed diff | SATISFIED | blob hash match, exhaustiveness+identity gates live |
| TEST-07 | 144-02/144-05/144-06 | builds+native+host pass; CI-scoped clean; parity holds | SATISFIED | all builds/suites/gates re-run live, exact match |
| TEST-08 | 144-05 | flash/RAM delta vs. baseline; Leonardo ceiling checked | SATISFIED | checker re-run live, exact match |

No requirement is orphaned: `grep "Phase 144" .planning/REQUIREMENTS.md` returns exactly the eight `TEST-0N` traceability rows plus one unrelated cross-reference (F-138-02 footnote) — no ninth requirement is silently mapped to this phase.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` found in any of the 9 new/modified files scanned (both new gate modules, both planted fixtures, `check_size_baseline.py`/`check_build_warnings.py` and their test files) | — | none |
| `.planning/phases/144-tests-build-verification/144-07-SUMMARY.md` | n/a | SUMMARY states the traceability-matrix table (REQUIREMENTS.md lines 326-333) was "left untouched" at `Pending`, but the live file shows `Complete` there | INFO | A follow-up commit `dc5dd5a4` (same author, 6 minutes after the SUMMARY's commit) applied exactly that missing edit. Current file state is internally consistent (both tables agree) and is not a functional gap — it strengthens traceability rather than weakening it. Flagged only because the SUMMARY narrative no longer matches the final state; not a blocker. |

No blockers. No files under `firestarter/src/` were touched (confirmed via `git diff --name-only 59a8a42..HEAD -- src/` → empty), matching D-04's claim exactly.

### Human Verification Required

None. Every must-have in this phase is a code/test/build assertion, independently re-executed in
this session. The one `<human-check>` block present in the phase's plans (144-07's Task 2 operator
checkpoint gating the requirement flip) was already closed during execution — the SUMMARY records a
verbatim operator response ("approved", auto-mode confirmed off), and the resulting commits
(`11ef9042`, `dc5dd5a4`) show the exact, scoped diff that approval authorized. There is nothing left
in this phase's scope requiring visual, real-time, or hardware judgment (bench validation is
explicitly Phase 145's, per this phase's own non-claims and per the constraints supplied for this
verification).

### Gaps Summary

None. All eight `TEST-0N` requirements and all four ROADMAP success criteria were independently
reproduced against the live codebase in this session — not accepted on SUMMARY.md's word. Every
figure quoted in `144-TEST-RECORD.md` that this verification attempted to reproduce (build sizes,
native test counts, checker verdicts, ruff/mypy/coverage results, blob hashes, skip counts) matched
exactly. The phase's own documented non-claims (D-03's live-row overprogram wiring, D-08's un-gated
prechange file, D-15's CI-leg absence for the three `*_v131` envs, TEST-04's register-stream-only
scope) are honestly bounded, consistent with the constraints supplied for this verification, and are
not treated as gaps. The one INFO-level note above (SUMMARY staleness vs. a beneficial follow-up
edit) does not affect goal achievement.

---

*Verified: 2026-08-14T11:04:04Z*
*Verifier: Claude (gsd-verifier)*

---

## Staleness Reconciliation (orchestrator, post-verification)

`gsd-tools query verification.status` reported `stale` immediately after this report was
written. That check is a pure **mtime comparison**: it flags any `*-SUMMARY.md` whose mtime is
newer than this file (`bin/lib/verification.cjs:103-128`). It exists to catch *new work landing
after verification ran*.

**What actually landed after `verified: 2026-08-14T11:04:04Z`:** exactly one commit, `4b2a1249`,
touching exactly one file — `144-07-SUMMARY.md` — and only its prose. It appends a note recording
that the REQUIREMENTS.md traceability-matrix rows were flipped to `Complete` after that SUMMARY
claimed they had been left `Pending`.

**Evidence the verified subject is unchanged:**

| Check | Result |
|-------|--------|
| `git log --since=11:03:00Z` | one commit, `4b2a1249` |
| Files changed since verification | `144-07-SUMMARY.md` only |
| `firestarter` HEAD | `a594173` — unchanged |
| `firestarter_app` HEAD | `68820a6` — unchanged |
| `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` | unchanged since verification (`dc5dd5a4` predates it) |

No production code, no test, no fixture, no baseline and no coverage document moved. The
substantive change the note describes (`dc5dd5a4`) landed **before** this verification and was
explicitly observed by it — recorded above as the INFO-level documentation-staleness item.

**Verdict unchanged: passed, 8/8.** This section is the orchestrator's reconciliation of an mtime
artifact, not a re-verification and not an override of the verifier's finding.
