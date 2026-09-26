---
phase: 120
slug: host-cli-surface-wire-emission-capability-refusal
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-07-29
settled: 2026-07-29
---

> **Status note (settled by Plan 120-12).** All twelve plans landed. Every row below that was
> `❌ W0` at plan-creation time was individually re-verified this sweep to exist on disk and to be
> reachable by a real, passing command before `nyquist_compliant`/`wave_0_complete` were flipped
> true — see the per-row corrections in the Requirement → Oracle Map below. A small number of the
> map's originally-authored `-k` substrings do not literally match the test names the executing
> plans actually chose (e.g. HOST-02's D-18 warn-and-proceed test and HOST-04's D-04 auto-set test
> both landed in `tests/test_write_skip_sdp_unlock.py`, not `tests/test_dev_sdp_cmd.py` as
> originally written) — those rows are corrected in place, with the real file and test name, not
> silently left pointing at a command that would collect zero tests.

# Phase 120 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `120-RESEARCH.md` § Validation Architecture. Baseline measured 2026-07-29 at
> `firestarter_app` HEAD `9ead17f`, firmware HEAD `0048b3d` (tree clean, and required to stay so).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` (+ `pytest-randomly`, `syrupy`, `pytest-cov`), invoked as `python3 -m pytest` |
| **Config file** | `firestarter_app/pyproject.toml` — `[tool.pytest.ini_options]`, `[tool.mypy]`, `mypy_error_watermark = 35` |
| **Quick run command** | `cd /workspaces/firestarter_app && python3 -m pytest tests/test_sdp_capability.py tests/test_dev_sdp_cmd.py tests/test_revision_constants_parity.py -q` |
| **Full suite command** | `cd /workspaces/firestarter_app && python3 -m pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` |
| **Lint/format gate (CI-scoped)** | `ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/` — **CI scope is `firestarter/ tests/`, not `.`**; four `tools/` files are lint-dirty at baseline |
| **Type gate** | `python3 tools/check_mypy_watermark.py` — assert the reported error count stays at **1** (watermark 35 has 34 slack; a bare `mypy` run is red at baseline) |
| **Estimated runtime** | quick ~5 s · full suite ~90 s |
| **Baseline** | Exactly **one** pre-existing failure: `test_audit_coverage_matrix.py::test_golden_file_matches`. Everything else green, measured this session. |

**Two known environment artifacts — name them, never silently tolerate them:**
- `test_audit_coverage_matrix` is a stale golden, not this phase's regression (`reference_audit_coverage_matrix_golden_stale`).
- `test_no_programmer_found_*` go RED when a board is attached (`/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0` are present). Did **not** reproduce this session.

---

## Sampling Rate

- **After every task commit:** quick run command, plus `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/`.
- **After every plan wave:** full suite + `python3 tools/check_mypy_watermark.py` (error count ≤ 1) + the nine-row CORRECTION-4 gate table if the wave touched `cli_handlers.py`, `constants.py`, or anything the gates scan.
- **Before `/gsd-verify-work`:** full suite green except the single named pre-existing failure; all nine gate rows re-run at the final commit; both sub-repo trees in their expected state.
- **Max feedback latency:** ~5 s (quick), ~90 s (full).

---

## Requirement → Oracle Map

Task IDs are filled in after planning. Every row below must be reachable by an automated command.

| Req ID | Behavior | Test Type | Automated Command | File Exists |
|--------|----------|-----------|-------------------|-------------|
| HOST-01 | `dev sdp <chip> enable\|disable` exists with the locked CLI surface | unit (CliRunner) | `pytest tests/test_dev_sdp_cmd.py -k surface -x` (`test_surface_is_chip_then_mode_with_a_yes_flag`) | ✅ 120-08, verified 120-12 |
| HOST-01 | Gate order absent → capability → support-status → confirm; **`Confirm.ask` not called** on any refusal | unit | `pytest tests/test_dev_sdp_cmd.py -k gate_order -x` (2 tests: absent-chip leg + capability-refusal leg) | ✅ 120-08, verified 120-12 |
| HOST-01 | **No serial port opened** on any refusal (`find_and_connect.assert_not_called()`) — not exit code | integration (mock transport) | `pytest tests/test_dev_sdp_cmd.py -k no_port_opened -x` (`test_no_port_opened_on_any_refusal_with_a_real_operator`) | ✅ 120-08, verified 120-12 |
| HOST-01 | On-TTY confirms; `-y` bypasses; off-TTY without `-y` refuses (D-06) | unit | `pytest tests/test_dev_sdp_cmd.py -k consent -x` (`test_consent_matrix`) | ✅ 120-08, verified 120-12 |
| HOST-01 | An `adapter-required` `0x0D` part with no SDP hears the **capability** reason, not the adapter reason (D-08) — exhaustive over all **nine** `adapter-required` `0x0D` parts (`120-SDP-PARTITION.md` §2.2), so D-08's gate ordering is load-bearing on every part in the bucket, not a hypothetical subset | unit + DB invariant | `pytest tests/test_dev_sdp_cmd.py -k adapter_required -x` (CLI leg: `test_adapter_required_part_hears_the_capability_reason_not_the_adapter_reason`); `pytest tests/test_sdp_capability.py -k test_all_nine_adapter_required_parts_are_refused_by_capability -x` (DB-level exhaustive leg, plan 120-05) | ✅ 120-08 (CLI leg) / ✅ 120-05 (DB leg), both verified 120-12 |
| HOST-02 | `write --skip-sdp-unlock` sets bit `0x100` in the emitted `flags` | unit | `pytest tests/test_eprom_operations.py -k skip_sdp_unlock_bit -x` | ✅ extend |
| HOST-02 | `build_flags`' new param is keyword-only, defaults `False`; BUG-1 contract intact | characterization | `pytest tests/test_bug_characterization.py -q` | ✅ re-run |
| HOST-02 | D-18: non-`0x0D` chip warns and the write still runs (bit still emitted) | unit | `pytest tests/test_write_skip_sdp_unlock.py -k non_0x0d -x` (**correction**: landed in `test_write_skip_sdp_unlock.py`, not `test_dev_sdp_cmd.py` as originally written — `test_non_0x0d_chip_with_the_flag_warns_and_proceeds` + `test_non_0x0d_chip_without_the_flag_is_unchanged`) | ✅ 120-09, verified 120-12 |
| HOST-03 | Every firmware `#define CMD_*`/`FLAG_*` maps two-way to `constants.py`, with `COMMAND_NAMES` coverage; exemptions enumerated explicitly | parity gate | `pytest tests/test_revision_constants_parity.py -q` | ✅ rebuild |
| HOST-03 | The parity gate **actually fails** on planted drift | planted-violation | `pytest tests/test_revision_constants_parity.py -k planted -x` | ✅ 120-07, verified 120-12 (4 planted-violation legs) |
| HOST-03 | The gate fails closed on an unreadable/absent header path | fail-closed | `pytest tests/test_revision_constants_parity.py -k fails_closed -x` (**correction**: actual test name is `test_gate_fails_closed_on_an_unreadable_header_path`, matched by `-k fails_closed`, not the literal substring `fail_closed`) | ✅ 120-07, verified 120-12 |
| HOST-04 | `allow-set ∪ refuse-set == exactly the 84 `algorithm == 13` entries`, with the derived **43 / 41** split pinned — full arithmetic the gate pins: 84 manufacturer+part-number pairs (43 ALLOW / 41 REFUSE); 81 distinct `part_number` strings (40 ALLOW / 41 REFUSE); 134 total alias-token instances; 130 distinct uppercased tokens (65 ALLOW / 65 REFUSE, empty intersection). Supersedes the interim operator placeholder (74 ALLOW / 10 REFUSE) and RESEARCH F-01's curated split (37 ALLOW / 47 REFUSE) — `120-SDP-PARTITION.md` is authoritative | DB invariant | `pytest tests/test_sdp_capability.py -k test_partition_covers_exactly_the_84_0x0d_entries -x`; `pytest tests/test_sdp_capability.py -k test_allow_and_refuse_token_sets_are_disjoint_and_total -x` | ✅ (`tests/test_sdp_capability.py` created by plan 120-01) |
| HOST-04 | Every refuse-set member is refused with a reason naming why — now exhaustive: all **nineteen** `DIP24_2816` parts refuse with `REASON_NOT_CAPABLE`, both FRAM parts refuse with the FRAM-specific reason (`REASON_FRAM`, with `REASON_NOT_CAPABLE` absent, proving branch order), and the 8 HOST-04-named pre-SDP entries incl. **`2817`** refuse — supersedes the narrower "8 named + 2 FRAM" claim | unit | `pytest tests/test_sdp_capability.py -k test_all_dip24_2816_parts_are_refused -x`; `pytest tests/test_sdp_capability.py -k test_both_fram_parts_are_refused_with_the_fram_reason -x`; `pytest tests/test_sdp_capability.py -k test_host04_named_pre_sdp_class_is_refused -x` | ✅ 120-05 extends |
| HOST-04 | Non-vacuity: a synthetic `algorithm == 13` entry in neither set makes the helper raise | non-vacuity | `pytest tests/test_sdp_capability.py -k test_synthetic_unknown_0x0d_entry_is_refused_non_vacuous -x` | ✅ (created by plan 120-01) |
| HOST-04 | **Shape leg (F-06):** the predicate is name-keyed, and a `resolve_chip` dict provably lacks `protocol-id`/`name` | anti-vacuity | `pytest tests/test_sdp_capability.py -k test_predicate_is_name_keyed_and_a_programmer_dict_is_rejected -x` | ✅ 120-05 extends |
| HOST-04 | A user-override `0x0D` part (simulating `~/.firestarter/database.json`) is refused at **runtime** | unit | `pytest tests/test_sdp_capability.py -k test_local_override_0x0d_entry_is_refused_at_runtime -x` | ✅ 120-05 extends |
| HOST-04 | **Structural invariants (new leg):** the allow-set contains **no** `adapter-required` part and **no** part on pinout `DIP24_2816` — two consequences of the derived partition, not its rule (RESEARCH F-03 still holds: no structural rule expresses the partition, `DIP28_28C64` splits 15/20 ALLOW/REFUSE); added to catch a careless hand-widening of the table | DB invariant | `pytest tests/test_sdp_capability.py -k test_allow_set_contains_no_adapter_required_and_no_dip24_2816_part -x` | ✅ 120-05 extends |
| HOST-04 | D-04: a refused part gets `FLAG_SKIP_SDP_UNLOCK` auto-set on `write` **and** an unconditional report line | unit | `pytest tests/test_write_skip_sdp_unlock.py -k auto_set -x` (**correction**: landed in `test_write_skip_sdp_unlock.py`, not `test_dev_sdp_cmd.py` — `test_refused_0x0d_part_gets_the_bit_auto_set_with_an_unconditional_report_line` + the scoping negative + no-duplication legs) | ✅ 120-10, verified 120-12 |
| HOST-05 | No SDP report text contains a lock/unlock state boolean; the unreadable-state caveat is on **both** directions | text assertion | `pytest tests/test_dev_sdp_cmd.py -k no_fabricated -x` (`test_no_fabricated_lock_state_boolean_in_the_report`) | ✅ 120-08, verified 120-12 |
| HOST-05 | An INFO-band decoded frame logs at `logging.INFO`, not DEBUG (D-09) | unit | `pytest tests/test_serial_comm.py -k info_band_promoted -x` | ✅ extend |
| HOST-05 | D-10: the host summary line carries **no** duration figure | text assertion | `pytest tests/test_dev_sdp_cmd.py -k carries_no_duration -x` (`test_summary_line_carries_no_duration_figure`) | ✅ 120-08, verified 120-12 |
| HOST-05 | D-11: `0x87` `MSG_WARN_SDP_TBLC_EXCEEDED` prints at WARNING and the exit code stays `0` | unit | `pytest tests/test_dev_sdp_cmd.py -k tblc -x` (`test_tblc_warn_prints_at_warning_and_exit_code_stays_zero`) | ✅ 120-08, verified 120-12 |
| HOST-06 | D-14: `MSG_ERR_UNKNOWN_CMD` on the SDP path renders as a firmware-too-old refusal | unit | `pytest tests/test_dev_sdp_cmd.py -k firmware_too_old -x` (`test_firmware_too_old_is_reported_when_unknown_cmd_comes_back`) | ✅ 120-08, verified 120-12 |
| HOST-06 | D-15: flag set **and** `0x86` absent → loud report + operation fails | unit | `pytest tests/test_eprom_operations.py -k missing_sdp_ack -x` | ✅ 120-10, verified 120-12 |
| HOST-06 | D-15 converse: flag set **and** `0x86` present → no complaint, operation succeeds | unit | `pytest tests/test_eprom_operations.py -k sdp_ack_honoured -x` | ✅ 120-10, verified 120-12 |
| SUB-fix | `dev test --submit` targets `henols/firestarter_prom`, asserted on **argv**, never on exit code | unit | `pytest tests/test_submit.py -k repo_target -x` | ✅ extend |
| all | Nine-row CORRECTION-4 sweep green at the final commit | regression | see `120-RESEARCH.md` § F-18 (nine commands) | ✅ present |
| all | Firmware sub-repo **byte-untouched** | regression | `git -C /workspaces/firestarter status --porcelain` empty **and** tip still `0048b3d` | ✅ |
| all | DB + generated codegen untouched | regression | `git -C /workspaces/firestarter_app diff --stat -- firestarter/data/ firestarter/messages.py` empty | ✅ |

---

## Wave 0 Requirements

- [x] `tests/test_sdp_capability.py` — the partition invariant, named refusals, non-vacuity, the F-06 shape leg, local-override refusal (plans 120-01, 120-05; verified present and green 120-12)
- [x] `tests/test_dev_sdp_cmd.py` — CliRunner surface, gate ordering, no-port-opened, consent matrix, report-text assertions (plan 120-08; verified present and green 120-12)
- [x] `tests/test_revision_constants_parity.py` — rebuilt as a real header-parsing gate (replaces hardcoded literals) (plan 120-07; verified present and green 120-12, 13 tests)
- [x] The parity gate's planted-violation fixtures (**correction**: plan 120-07 shipped three separate header fixtures rather than one combined `planted_constants_drift.h` — `tests/fixtures/planted_constants_value_drift.h`, `tests/fixtures/planted_constants_fw_missing.h`, `tests/fixtures/planted_constants_host_missing.h`, one per drift class named in the Planted-Violation Fixtures table below — plus a `COMMAND_NAMES`-coverage monkeypatch leg and a fail-closed leg pointed at a nonexistent path) — all four confirmed present on disk and green 120-12

---

## Planted-Violation Fixtures Required

The project's mandatory anti-hollow contract: every gate ships a companion proving it can fail.

| Gate | Planted violation | Proves |
|---|---|---|
| Constants parity (D-12/D-13) | **(correction, verified 120-12)** three separate fixtures, not one combined file: `tests/fixtures/planted_constants_value_drift.h` (a `CMD_*` value changed), `tests/fixtures/planted_constants_fw_missing.h` (a `FLAG_*` deleted from the firmware side), `tests/fixtures/planted_constants_host_missing.h` (a new `CMD_*` present in firmware but absent from `constants.py`) | Value drift, host-missing, and firmware-missing are each detected, each by its own fixture |
| Constants parity — `COMMAND_NAMES` leg | in-test `monkeypatch.delitem` on a `COMMAND_NAMES` copy | A missing name entry is caught, not just a missing constant |
| Constants parity — fail-closed | point the path constant at a non-existent file | An unreadable header is an ERROR, never a silent pass |
| Allow-set exhaustiveness (D-02) | synthetic in-memory DB with one `algorithm == 13` entry in neither set | The partition invariant can fail — mirrors `test_sdp_db_invariant.py:151-184` |
| Allow-set shape leg (F-06) | assert `"protocol-id" not in resolve_chip(...)` | The vacuity mode that broke `_SRAM_PROTO_IDS` is machine-excluded |
| Gate ordering (D-08) | reorder gates in a test double, or assert reason-string identity per gate | Gate *order* is tested, not merely gate presence |
| D-09 mapping | assert `DEBUG` still applies to a non-INFO/WARN/ERROR label | The promotion is scoped, not a blanket level change |
| D-15 missing ack | frame stream with the flag set and `0x86` **omitted** | The check fires; the converse case proves it does not over-fire |

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | — | — |

**All phase behaviors have automated verification.** This phase adds **no bench work**: no AT28C part is on the bench, `0x0D` stays `UNVERIFIED`, zero `support_status` changes, the 84-chip count is unchanged.

---

## What CANNOT Be Validated — the ceiling, restated

- **That the curated capability partition is correct per family.** `REQUIREMENTS.md` § "Validation Ceiling" lists this explicitly. The gate proves the partition is **total and stable**, never that it is **right**.
- Any claim about actual silicon protection state, before or after either sequence.
- That `tBLC` is met as accepted by the die.
- That gh#11's symptom is gone.
- Nothing in this phase is evidence about AT28C silicon.

---

## Validation Sign-Off

- [x] All tasks have an `<automated>` verify or a Wave 0 dependency — confirmed across all twelve plans' PLAN.md task lists
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all ❌ references above — every row individually re-verified present on disk and reachable by a real, passing command in Plan 120-12's sweep (corrected commands recorded in place where the originally-authored `-k` substring or file path did not match what landed)
- [x] No watch-mode flags
- [x] Feedback latency < 90 s — full suite measured at ~62 s this sweep (`1050 passed, 1 failed in 61.68s`)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** Settled by Plan 120-12, 2026-07-29. All Wave 0 requirements and Validation Sign-Off items satisfied; see `120-NONREGRESSION.md` for the full nine-row cross-repo gate re-run and both frozen-artifact fences.
