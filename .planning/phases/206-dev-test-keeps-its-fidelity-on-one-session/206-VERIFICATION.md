---
phase: 206-dev-test-keeps-its-fidelity-on-one-session
verified: 2026-09-23T13:15:00Z
status: passed
score: 10/10 must-haves verified
covered_files: [".planning/REQUIREMENTS.md", ".planning/ROADMAP.md", ".planning/phases/206-dev-test-keeps-its-fidelity-on-one-session/206-01-PLAN.md", ".planning/phases/206-dev-test-keeps-its-fidelity-on-one-session/206-01-SUMMARY.md", ".planning/phases/206-dev-test-keeps-its-fidelity-on-one-session/206-02-PLAN.md", ".planning/phases/206-dev-test-keeps-its-fidelity-on-one-session/206-02-SUMMARY.md", ".planning/phases/206-dev-test-keeps-its-fidelity-on-one-session/206-03-PLAN.md", ".planning/phases/206-dev-test-keeps-its-fidelity-on-one-session/206-03-SUMMARY.md", ".planning/phases/206-dev-test-keeps-its-fidelity-on-one-session/206-04-PLAN.md", ".planning/phases/206-dev-test-keeps-its-fidelity-on-one-session/206-04-SUMMARY.md", ".planning/phases/206-dev-test-keeps-its-fidelity-on-one-session/206-REVIEW.md", ".planning/phases/206-dev-test-keeps-its-fidelity-on-one-session/206-SESSION-COST.md", ".planning/phases/206-dev-test-keeps-its-fidelity-on-one-session/206-UAT.md"]
covered_digest: "v1:sha256:192771cabf9f019d51d4e6895a4e0002678a4f4bfc1db0e9279f6860ded798a0"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 206: `dev test` keeps its fidelity, on one session — Verification Report

**Phase Goal:** The `dev test` verify and blank steps route through the host engine without changing what a verdict means, and a plan uses one leased serial link instead of one port open per call.
**Verified:** 2026-09-23
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth (roadmap success criteria + must_haves) | Status | Evidence |
|---|---|---|---|
| 1 | `OP_VERIFY`/`OP_BLANK_CHECK` produce a fingerprint at least as informative as today's for the same physical outcome (SC1, DEVTEST-01) | ✓ VERIFIED | `StepResult.compare_evidence` (bad/compared/first_offset/first_actual/ff_count/aborted/classification) added at `chip_test.py:2712-2723`, populated from the `on_result` capture; verify fingerprint source unchanged (D-04). Named tests pass: `test_blank_check_carries_compare_evidence_without_a_fingerprint`, `test_verify_verdict_2_performs_no_fingerprint_read_back` (19 passed in `test_chip_test.py`/`test_blast_radius_invariance.py` subset re-run) |
| 2 | A host-path report is distinguishable from a firmware-path one by an empty-default discriminator; no already-filed `dedup_fingerprint` group re-keyed, no two mechanically different runs silently merge (SC2, DEVTEST-02) | ✓ VERIFIED | `compare_path_tag`/`COMPARE_PATH_HOST_TAG = "cmp=host"` at `chip_test.py:1112-1148`, appended to `dedup_fingerprint` only when non-empty (`diagnostic_report.py`). Re-ran `test_dedup_fingerprint_is_frozen` — 19/19 passed (all frozen literals unmoved); `test_planted_compare_path_host_reddens_the_gate` proves the tag is capable of moving the hash (not inert) |
| 3 | Any classification whose meaning changes for a physically identical outcome is named and justified in the phase record (SC3, DEVTEST-03) | ✓ VERIFIED | D-01 (206-01-PLAN.md Decisions) and the "DEVTEST-03 statement" section in `206-01-SUMMARY.md` name the exact change (verify/blank-check verdict 2 moves from `VERDICT_BAD`+implicit-COMPLETE to `VERDICT_SKIPPED`+`STATUS_ERROR`), the affected population (rig-fault reports only), and the reason (false-attribution hazard). Re-key consequence for DEVTEST-02 confirmed at a human `checkpoint:decision` (206-02-SUMMARY.md) |
| 4 | A `dev test` plan opens one validated serial link and reuses it across its steps (SC4, SESS-01) | ✓ VERIFIED | `EpromOperator.lease()` at `eprom_operations.py:769`, one call site `with app.eprom_operator.lease():` at `cli_handlers.py:2950`. Named tests re-run and pass: `test_a_leased_plan_opens_one_link_and_a_cold_plan_opens_one_per_call`, `test_the_cold_path_is_byte_identical_when_the_lease_is_never_acquired` (19/19 in `test_session_lease.py`) |
| 5 | The wall-clock saving is measured on a real run; if it does not pay, the change is reverted and that is recorded (SC5, SESS-02) | ✓ VERIFIED | `206-SESSION-COST.md` §2/§5: 6 real bench runs on `/dev/ttyACM0` (W27C512, Leonardo, Rev 2.0), leased median 228.283s vs cold median 268.992s, saving 40.709s/15.1%, all three pre-registered D-07 clauses passed on the rounded value, spread check, and zero verdict divergence. Lease KEPT as a direct, recorded consequence, not on principle. `ROADMAP.md` Bench cell corrected `no`→`**yes**` |
| 6 | A transport-failed cycle-block step exits 2, not 0; `--fast` and default 3-cycle runs agree (plan-01 must_have, DEVTEST-03) | ✓ VERIFIED | `_aggregate_cycle_results` folds `STATUS_ERROR` over full `results` (not `ran`), `chip_test.py:1379-1380`. Single named tests re-run and pass: `test_a_transport_failed_cycle_block_step_exits_2_not_0`, `test_a_transport_failed_cycle_keeps_the_run_status_error`, `test_fast_and_default_runs_agree_on_a_transport_failed_step_status` |
| 7 | `FP_TRANSPORT` bucket stays dead; phase record says so (D-09, plan-01 must_have) | ✓ VERIFIED | `_run_cycle_block` still calls `_run_step` with `runs=1` (confirmed unchanged in `chip_test.py`); D-09 explicitly states this in `206-01-PLAN.md` and `206-01-SUMMARY.md` |
| 8 | The lease is exactly one revertible commit; sha + clean revert rehearsal recorded (plan-03 must_have, SESS-01) | ✓ VERIFIED | Commit `3853b55` machine-verified as exactly 3 paths (`git show --name-only` re-run, confirmed); revert rehearsal and corrected two-sha recipe documented and re-applied cleanly during the SESS-02 bench measurement (§5 of `206-SESSION-COST.md`) |
| 9 | The 2922-case / `test_compare.py` behavioural corpus shows zero differences after this phase (DEVTEST-03 instrument) | ✓ VERIFIED | Re-ran `tests/test_compare.py` independently — 70 passed |
| 10 | No push to `beta` in any repo during this phase (safety prohibition, all 4 plans) | ✓ VERIFIED | `firestarter_app` remains on `v1.41-verification-to-host` with no upstream configured (`git rev-parse @{u}` fails: no tracking branch); all 7 phase commits are local, unpushed; no `origin/beta` movement attributable to this phase |

**Score:** 10/10 truths verified (0 present-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter_app/firestarter/chip_test.py` | verdict/status vocabulary, compare_evidence/compare_path, dispatch arms | ✓ VERIFIED | Exists, substantive, wired — all cited symbols present and exercised by passing tests |
| `firestarter_app/firestarter/diagnostic_report.py` | `dedup_fingerprint` appends `compare_path_tag` | ✓ VERIFIED | Confirmed via source read + 19/19 frozen-hash tests |
| `firestarter_app/firestarter/eprom_operations.py` | `EpromOperator.lease()`, `on_result` on `check_eprom_blank`/`verify_eprom` | ✓ VERIFIED | `lease()` at line 769; both methods carry `on_result` |
| `firestarter_app/firestarter/cli_handlers.py` | `dev_test` wraps `run_plan` in `.lease()` | ✓ VERIFIED | One call site at line 2950 |
| `firestarter_app/firestarter/serial_comm.py` | `setup_command` extracted | ✓ VERIFIED | Behaviour-identical extraction, `test_serial_characterization.py` unmodified and passing |
| Test files (8 modified/created) | new/updated regression coverage | ✓ VERIFIED | All named tests re-run independently and pass |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `_dispatch_step` `OP_BLANK_CHECK` arm | process exit code | `_aggregate_cycle_results` → `run_status` → `_dev_test_exit_code` | ✓ WIRED | `test_a_transport_failed_cycle_block_step_exits_2_not_0` re-run, passes |
| `EpromOperator.lease()` | `cli_handlers.dev_test` | `with app.eprom_operator.lease():` around `run_plan(...)` | ✓ WIRED | Confirmed by direct source read, one call site only |
| `check_eprom_blank`/`verify_eprom` `on_result` | `StepResult.compare_evidence`/`compare_path` | capture-list closures in `_dispatch_step`/`_dispatch_multi_run` | ✓ WIRED | Confirmed by source read + passing tests |
| `compare_path_tag` | `dedup_fingerprint` | appended after `coverage_tag`, empty-default | ✓ WIRED | 19/19 frozen-hash tests + planted-mutation test |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Transport-failed cycle exits 2 | `pytest tests/test_dev_test_cmd.py::test_a_transport_failed_cycle_block_step_exits_2_not_0` | 1 passed | ✓ PASS |
| Fold uses full `results`, not `ran` | `pytest tests/test_chip_test_cycle.py::test_a_transport_failed_cycle_keeps_the_run_status_error tests/test_chip_test_cycle.py::test_fast_and_default_runs_agree_on_a_transport_failed_step_status` | 2 passed | ✓ PASS |
| Lease: one link per plan vs. one per call | `pytest tests/test_session_lease.py::test_a_leased_plan_opens_one_link_and_a_cold_plan_opens_one_per_call tests/test_session_lease.py::test_the_cold_path_is_byte_identical_when_the_lease_is_never_acquired` | 2 passed | ✓ PASS |
| Frozen `dedup_fingerprint` corpus unmoved | `pytest tests/test_blast_radius_invariance.py -k test_dedup_fingerprint_is_frozen` | 19 passed | ✓ PASS |
| DEVTEST-03's named behavioural instrument | `pytest tests/test_compare.py` | 70 passed | ✓ PASS |
| Full-phase regression subset | `pytest tests/test_session_lease.py tests/test_chip_test_cycle.py tests/test_dev_test_cmd.py` | 113 passed | ✓ PASS |
| Lint/format | `ruff check firestarter/ tests/` / `ruff format --check firestarter/ tests/` | clean / 153 files formatted | ✓ PASS |
| SESS-02 bench measurement | live silicon (not re-run; verified from record) | 15.1% saving, KEPT | ✓ PASS (per `206-SESSION-COST.md`, corroborated by orchestrator's prior full-suite run: 2363 passed, 0 failed) |

Full workspace suite was not re-run in this verification pass (orchestrator already ran it once: 2363 passed, 0 failed, 86.38% coverage, ruff clean) — per the "run the full suite at most once" constraint, this verifier re-ran only the phase-scoped subsets and the two named frozen-corpus/behavioural-corpus modules independently, all of which are consistent with that count.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| DEVTEST-01 | 206-01, 206-02 | `OP_VERIFY`/`OP_BLANK_CHECK` route through host methods, fingerprint at least as informative | ✓ SATISFIED | Truths 1, 6 above |
| DEVTEST-02 | 206-02 | Host-path report distinguishable via empty-default discriminator, no silent re-key/merge | ✓ SATISFIED | Truth 2 above |
| DEVTEST-03 | 206-01 | Verdict meaning changes named/justified, not absorbed | ✓ SATISFIED | Truths 3, 6, 7, 9 above |
| SESS-01 | 206-03 | One leased serial link per plan, reused across steps | ✓ SATISFIED | Truths 4, 8 above |
| SESS-02 | 206-04 | Wall-clock saving measured, kept/reverted on evidence | ✓ SATISFIED | Truth 5 above |

No orphaned requirements: all 5 IDs mapped to REQUIREMENTS.md's `### DEVTEST`/`### SESS` sections, all marked `Complete`, all claimed by exactly one plan each (01: DEVTEST-01/03, 02: DEVTEST-01/02, 03: SESS-01, 04: SESS-02).

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `chip_test.py:2696-2718` (WR-01, 206-REVIEW.md) | — | `captured_compare[0]` silently truncates if `on_result` ever fires more than once (not live today) | ⚠️ Warning | Advisory — does not affect current behavior; `_drive_region_compare` calls `on_result` at most once today |
| `chip_test.py:3410-3452` (WR-02, 206-REVIEW.md) | — | Verify multi-run loop doesn't early-exit after a verdict-2 run | ⚠️ Warning | Advisory — classification is still correct regardless; only affects wall-clock/redundant I/O on an already-faulted run |

No debt markers (`TBD`/`FIXME`/`XXX`) found in any phase-modified source file (independently re-grepped across the full `2756ef0..HEAD` diff). No placeholder/stub patterns found. Both warnings are pre-existing-review findings, non-blocking per the code review's own classification (0 critical), and do not touch a must-have truth.

### Human Verification Required

None. UAT (`206-UAT.md`) already completed 10/10 pass, including the two human-judgment items (dedup-fingerprint re-key consequence confirmation, SESS-02 bench-figure/keep-decision confirmation) both explicitly resolved by the operator.

### Gaps Summary

None. All 5 requirement IDs (DEVTEST-01, DEVTEST-02, DEVTEST-03, SESS-01, SESS-02) are satisfied with independently re-verified evidence: source read, targeted test re-execution (not trusted from SUMMARY narration), the frozen 19-case `dedup_fingerprint` corpus intact, the DEVTEST-03-named `test_compare.py` corpus intact, the lease's exact-3-path commit and clean revert rehearsal confirmed, and the SESS-02 bench record internally consistent (arithmetic re-checked: 268.992−228.283=40.709, 40.709/268.992×100=15.134%→15.1%, clause 2's 5×1.922=9.61 < 40.709). The two code-review warnings (WR-01, WR-02) are real but explicitly non-live/non-blocking findings already surfaced by the phase's own review and do not compromise any must-have truth.

---

_Verified: 2026-09-23_
_Verifier: Claude (gsd-verifier)_
