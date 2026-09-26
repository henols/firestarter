---
phase: 176-transport-instrumentation-connect-cost-measurement-partially
verified: 2026-09-04T23:21:01Z
status: passed
score: 9/9 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 176: Transport Instrumentation + Connect-Cost Measurement Verification Report

**Phase Goal:** The two re-sync events and the two failure paths beside them stop being invisible, and the milestone's one genuinely unmeasured number — per-connect cost — gets measured per board class instead of assumed.
**Verified:** 2026-09-04T23:21:01Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Each of the two re-sync events, a decode-id-frame failure, and a response timeout increments its own dedicated counter, proven by a test that triggers each path independently and asserts exactly-one-counter-moved | ✓ VERIFIED | `transport_counters.py` has 5 record_* functions; `test_transport_counters.py` (39 tests, all pass) includes per-site "and-nothing-else" tests: `test_decode_id_frame_corrupt_crc_raises_decode_failures_by_one_and_nothing_else`, `test_established_timeout_raises_timeouts_and_nothing_else`, `test_probe_scoped_timeout_raises_probe_timeouts_and_nothing_else`, `test_magic_preamble_with_no_length_bytes_raises_resync_length_missing_and_nothing_else`, `test_declared_length_longer_than_body_raises_resync_body_truncated_and_nothing_else`, plus the adjacency case `test_truncated_frame_then_timeout_raises_both_resync_body_truncated_and_timeouts`. Ran directly: 39/39 pass. Source inspection of `serial_comm.py` confirms all 4 named sites (`_decode_id_frame:352`, `get_response:561`, and the two re-sync branches at `:493`/`:509`) call the correct counter, placed beside the existing `logger.warning`, before the `continue`/`raise`. |
| 2 | `transport_health` surfaces real counts for every wired counter, and any genuinely-unwired counter still reads `NOT_MEASURED`, never a fabricated 0 | ✓ VERIFIED | `diagnostic_report.py`: `TransportHealth` defaults every counter to `None`; `_transport_dict()` substitutes `NOT_MEASURED` only for `None`. `test_transport_not_measured` (in `test_diagnostic_report.py`, run directly, passes) asserts all 8 counters read `NOT_MEASURED` on a default-constructed report AND `!= 0`. Independently re-verified the `cobs_decode` production-call-site claim myself: `/usr/bin/grep -rn "cobs_decode" --include="*.py" .` (excluding `build/` and `tests/`) shows zero production callers — only the definition itself — confirming the docstring's stated reason for `cobs_errors` staying `NOT_MEASURED` is factually true, not merely asserted. |
| 3 | Per-connect cost recorded as two distinct bench-measured artifacts (Uno 512B, Leonardo 1024B), never blended | ✓ VERIFIED | `176-MEASUREMENT.md` (328 lines, 8 top-level sections) contains two clearly separate sections (§4a Uno-class, §4b Leonardo-class) each with its own min/median/max/structural_floor/remainder/probe_timeouts. Explicit sentence: "These two per-board-class figures are never blended, and no single per-connect cost number that combines both board classes exists or should be quoted anywhere in this document." `grep -in "average\|mean\|blended"` finds only the never-blended disclaimers, no averaged figure. Port identity independently verified two ways in the artifact (`fw` command's `controller:` field, and a second `firmware_max_chunk` read: 512 vs 1024) before either board was driven further. |
| 4 | `_SUSPECT_THRESHOLD`'s value of 5 is justified against the newly measured real counts or re-derived, with the basis recorded | ✓ VERIFIED | `_is_transport_suspect`'s docstring in `diagnostic_report.py` records the basis verbatim (the 32-connect / sixth-wrong-port-probe argument, and the rejected per-counter-threshold alternative), pinned by `test_meas02_basis_is_recorded_and_pinned_in_docstring`. `probe_timeouts` is provably excluded from the suspicion domain (`test_probe_timeouts_excluded_from_suspicion_domain`), and a closure test (`test_suspicion_domain_is_closed_against_a_silently_added_counter`, built from `dataclasses.fields()`) proves no counter can silently escape classification. The bench run (176-05) corroborates empirically: both board classes measured `probe_timeouts: 0` with a single pinned port. |

**Score:** 4/4 roadmap success criteria verified, plus 5/5 PLAN-frontmatter must-have truth clusters (below) verified.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/transport_counters.py` | Process-lifetime resettable counter sink | ✓ VERIFIED | Exists; exports `record_decode_failure`, `record_resync_length_missing`, `record_resync_body_truncated`, `record_response_timeout`, `probe_scope`, `reset`, `snapshot`; zero comment lines (tokenize-verified); imports nothing from `serial_comm`/`diagnostic_report` (acyclic). |
| `firestarter_app/tests/test_transport_counters.py` | Sink contract + per-site legs + suspicion-domain tests | ✓ VERIFIED | 39 tests, all pass; covers every must-have behavior across plans 01-03. |
| `firestarter_app/tests/fixtures/reports/*.json` | 16 snapshots carrying `decode_failures`/nine-key shape | ✓ VERIFIED | All 16 files carry exactly the 9-key `transport_health` shape (`cobs_errors, crc_failures, decode_failures, probe_timeouts, resync_body_truncated, resync_length_missing, retries, timeouts, transport_suspect`), confirmed programmatically. |
| `firestarter_app/firestarter/eprom_operations.py` | `measure_connect_cost`, `_summarize_connect_samples`, `_write_connect_cost_log` | ✓ VERIFIED | All three exist; numeric contract (three-decimal seconds, `statistics.median_low`, no mean, honest `unmeasured` on empty) confirmed by direct source read and by 8 passing tests in `test_connect_cost_harness.py`. |
| `firestarter_app/tests/test_connect_cost_harness.py` | Rounding/ordering/no-mean/empty-sample contract | ✓ VERIFIED | 8 tests, all pass, including the odd/even median-tie-break case and the empty-sample honesty case. |
| `.planning/phases/176.../COVERAGE.md` | Reasoned no-external-API declaration | ✓ VERIFIED | Exists, correctly scoped to the whole phase. |
| `.planning/phases/176.../176-MEASUREMENT.md` | Two never-blended per-board-class sections + provenance | ✓ VERIFIED | 328 lines, 8 sections, min_lines constraint (60) satisfied by a wide margin. |
| `firestarter_app/tests/test_serial_comm.py` | Re-pinned ring-fence digest with Phase 176 justification recorded | ✓ VERIFIED | `_PINNED_SHA256` recomputed independently from `inspect.getsource(SerialCommunicator._read_and_parse_lines)`: matches exactly (`8b77800003a44fb21f2054fe8d0584e804648a76e52c3f23f55f06df74127b41`). Confirmed the fence still discriminates by introducing a trivial one-line body change and re-running the test: it went RED with the `GATE-1.8d VIOLATION` message, then restored clean (`git status --short` empty afterward). |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `serial_comm.py` (`_decode_id_frame`) | `transport_counters.py` | `record_decode_failure()` on decode failure | ✓ WIRED | Confirmed at line 352, only on the `result is None` branch. |
| `serial_comm.py` (`get_response`) | `transport_counters.py` | `record_response_timeout()` before the timeout raise | ✓ WIRED | Confirmed at line 561, immediately before `raise SerialTimeoutError`. |
| `serial_comm.py` (`find_and_connect`) | `transport_counters.py` | `probe_scope()` wraps only the single `_probe_port` call | ✓ WIRED | Confirmed at line 1016 — the sole `probe_scope()` occurrence, scoping exactly the `_probe_port` call and nothing after. |
| `serial_comm.py` (`_read_and_parse_lines`, two re-sync branches) | `transport_counters.py` | `record_resync_length_missing()` / `record_resync_body_truncated()` | ✓ WIRED | Confirmed at lines 493 and 509, each placed between the existing `logger.warning` and `continue` — the ONLY change to the ring-fenced body, confirmed by the re-pinned, re-verified SHA-256. |
| `cli_handlers.py` (`dev_test`) | `transport_counters.py` | reset before window, `snapshot()` after `run_plan`, assigned onto `report.transport.*` | ✓ WIRED | Confirmed at lines 2404/2440-2445 — all 5 wired counters assigned. |
| `cli_handlers.py` (`dev fault-inject --mode connect-cost`) | `eprom_operations.py` | `measure_connect_cost(...)` dispatch, exit 0/1 on boolean | ✓ WIRED | Confirmed at line 1636-1639; no chip resolution reached on this branch (matches `176-MEASUREMENT.md`'s claim that `resolve_chip` is unreached in connect-cost mode). |
| `diagnostic_report.py` | (import graph) | Still imports no transport/hardware class | ✓ VERIFIED | Module-level imports scanned by hand and by the existing AST-based `test_report_module_is_orchestrator_only` (passes) — no `SerialCommunicator`/`HardwareManager` import. |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|-----------------|--------------|--------|----------|
| RPT-C1 | 176-01, 02, 03 | Four named sites each increment a real, report-reachable counter | ✓ SATISFIED | All four sites wired and tested (see Key Links + Truth #1); `REQUIREMENTS.md` line 91 ticked Complete. |
| RPT-C2 | 176-01, 02, 03 | `transport_health` reports real counts; `NOT_MEASURED` only for genuinely-unwired counters; suspicion rule unchanged | ✓ SATISFIED | See Truth #2; `REQUIREMENTS.md` line 92 ticked Complete. |
| MEAS-01 | 176-04, 05 | Per-connect cost measured per board class, gates PRUNE-08/R4-01 | ✓ SATISFIED | `176-MEASUREMENT.md` bench-measured on two real attached boards; `REQUIREMENTS.md` line 103 ticked Complete. |
| MEAS-02 | 176-02 | `_SUSPECT_THRESHOLD=5` justified or re-derived | ✓ SATISFIED | See Truth #4; `REQUIREMENTS.md` line 104 ticked Complete. |
| MEAS-03 | 176-02 | Which counters are genuinely wireable traced end to end | ✓ SATISFIED | `TransportHealth` docstring records the full per-counter trace (`cobs_errors`, `crc_failures`, `retries`), each reason independently verified true (see Truth #2); `REQUIREMENTS.md` line 105 ticked Complete. |

No orphaned requirements — `.planning/REQUIREMENTS.md`'s "Phase 176" tags (lines 156-160) match exactly the 5 IDs declared across all 5 plans' frontmatter, no more, no less.

### Anti-Patterns Found

None. Scanned all phase-created/modified files (`transport_counters.py`, `serial_comm.py`, `diagnostic_report.py`, `cli_handlers.py`, `eprom_operations.py`, `test_transport_counters.py`, `test_connect_cost_harness.py`) for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` — zero matches. `transport_counters.py` and `test_transport_counters.py` carry zero comment lines (tokenize-verified); `test_connect_cost_harness.py` carries exactly 3 comment lines, all `# type: ignore[attr-defined]` mypy pragmas, consistent with this codebase's existing, pervasive use of typed `# type: ignore` pragmas elsewhere (not a narrative-comment violation).

### Behavioral Spot-Checks / Independent Reproduction

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Phase 174 oracle | `pytest tests/test_blast_radius_invariance.py tests/test_rekey_ledger.py -q` | 114 passed | ✓ PASS |
| Transport counter unit tests | `pytest tests/test_transport_counters.py -q` | 39 passed | ✓ PASS |
| Connect-cost harness unit tests | `pytest tests/test_connect_cost_harness.py -q` | 8 passed | ✓ PASS |
| Diagnostic report tests | `pytest tests/test_diagnostic_report.py -q` | 70 passed | ✓ PASS |
| Serial comm tests (incl. ring-fence) | `pytest tests/test_serial_comm.py -q` | 44 passed | ✓ PASS |
| Ring-fence digest recompute | `python3 -c "hashlib.sha256(inspect.getsource(...))"` | Matches pinned `8b778000...4127b41` exactly | ✓ PASS |
| Ring-fence discrimination | one-line body edit, re-run test, revert | Went RED with `GATE-1.8d VIOLATION`, then clean after revert | ✓ PASS |
| `cobs_decode` production-call-site claim | `grep -rn cobs_decode --include="*.py" . \| grep -v tests/` | Only the definition itself; zero production callers | ✓ PASS |
| `channel.py` byte-unchanged | `git diff a9c0bde..HEAD -- firestarter/channel.py` | Empty diff | ✓ PASS |
| Full app suite (independent rerun, this verification session) | `pytest tests/ -o addopts="" -q` | **2198 passed, 32 snapshots passed**, exit 0 | ✓ PASS |
| ruff / format (phase-touched files) | `ruff check` / `ruff format --check` on the 10 phase-touched files | All checks passed / all formatted | ✓ PASS |
| Firmware repo / chip database byte-unchanged | `git status --porcelain` in `firestarter/`; `git status --short` on `chip_database.json` | Both clean | ✓ PASS |
| Commit existence | `git cat-file -e` on all 7 claimed app-repo commits | All 7 exist, HEAD matches latest | ✓ PASS |

Note: the first two attempts at an independent full-suite rerun stalled for several minutes at a fixed point in the run; investigation traced this to a stray, unrelated `pytest tests/ -rs -q --ignore=tests/test_skip_census.py` process repeatedly spawning and contending for the same real serial-port hardware attached to this container (`/dev/ttyACM0`, `/dev/ttyACM1`) — not a defect in this phase's code. After killing the interfering process, the rerun completed cleanly at 2198 passed in 185s, matching the executor's own recorded 2198-passed evidence from earlier in the day.

### Human Verification Required

None. This phase's must-haves are fully addressable by presence, wiring, and behavioral test evidence, and the one hardware-gated deliverable (MEAS-01's bench measurement) was already executed by the phase's own executor with full command-verified provenance (port identity confirmed two independent ways, socket confirmed empty, firmware build pinned identical across both boards) — independently spot-checked above and found internally consistent.

### Gaps Summary

None. All 4 roadmap success criteria hold, all 5 declared requirements (RPT-C1, RPT-C2, MEAS-01, MEAS-02, MEAS-03) are satisfied with direct code/test/artifact evidence (not merely SUMMARY.md narrative), the v1.9 ring-fence re-pin was independently recomputed and its discrimination re-proven live, the `cobs_decode` "zero production call sites" claim was independently verified rather than taken on faith, and a full independent test-suite rerun in this verification session reproduced the claimed 2198-passed result.

**Minor informational notes (non-blocking):**
- `.planning/REQUIREMENTS.md` line 91's cited source locations (`serial_comm.py:485-490` and `:500-505`) are stale by a handful of lines relative to the current file (actual sites are at lines 493 and 509) — an artifact of earlier lines shifting as the phase's own commits added code above them. The described mechanism is still exactly correct; only the line numbers drifted.
- `.planning/ROADMAP.md`'s own per-requirement status table (lines 432-436) still reads "Pending" for all five Phase 176 requirement IDs, while the authoritative `.planning/REQUIREMENTS.md` correctly reads "Complete" for all five. This is a bookkeeping table that appears to only get refreshed at phase-close/milestone-close time elsewhere in this project's workflow; per this verification's explicit instruction not to modify ROADMAP.md, it is reported here rather than corrected.

---

_Verified: 2026-09-04T23:21:01Z_
_Verifier: Claude (gsd-verifier)_
