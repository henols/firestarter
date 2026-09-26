---
phase: 143
slug: host-timeout-progress-pulse-override
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-12
---

# Phase 143 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `143-RESEARCH.md` § Validation Architecture. This phase is **dual-repo** (D-01), so
> every row names which repo it runs in.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (host)** | `pytest` + `unittest.mock`, `pytest-cov` |
| **Config file (host)** | `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` — `testpaths = ["tests"]`, `addopts = "-ra -q"` |
| **Quick run command (host)** | `cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest tests/test_<file>.py -x -o addopts=""` |
| **Full suite command (host)** | `cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest tests/ --cov=firestarter --cov-fail-under=70 -o addopts=""` |
| **Framework (firmware)** | Unity + ArduinoFake via PlatformIO |
| **Config file (firmware)** | `firestarter/platformio.ini` |
| **Quick run command (firmware)** | `cd /workspaces/firestarter && pio test -e native_loop_v131 -f native/avr/test_loop_eprom_v131` |
| **Full suite command (firmware)** | `pio test -e native` **and** `pio test -e native_nodevtools` (both pinned at 141 cases / 17 suites), plus `pio run -e uno -e uno328pb -e leonardo` |
| **Estimated runtime** | ~20 s host quick · ~60 s host full · ~30 s native quick · ~4 min firmware full (3 AVR builds) |

`-o addopts=""` is **required** to see the pytest count line — `addopts` already carries `-q` and
doubling it suppresses the summary.

---

## Sampling Rate

- **After every task commit (host):** the touched test module —
  `.venv/ci-replica/bin/python -m pytest tests/test_<module>.py -x -o addopts=""`
- **After every task commit (firmware):** `pio test -e native_loop_v131` — and **commit before
  running the full firmware suite** (`test_flash_path_record_sync.py` asserts whole-repo
  `git status --porcelain`, so any uncommitted diff turns it RED).
- **After every plan wave (host):** `ruff check firestarter/ tests/` + `ruff format --check firestarter/ tests/`
  + `python tools/check_mypy_watermark.py` + `pytest tests/ --cov=firestarter --cov-fail-under=70`
- **After every plan wave (firmware):** `pio test -e native` + `pio test -e native_nodevtools`
  (141 cases / 17 suites each) + `pio run -e uno -e uno328pb -e leonardo`
  + `python scripts/check_build_warnings.py`
- **Before `/gsd-verify-work`:** full host suite and all three AVR builds green; `native_loop_v131`
  green; `native_trace_v131` RED **and named as expected** (D-24); `protocol_branch_inventory` green
  against the re-derived golden; `check_size_baseline.py` RED only for the recorded,
  operator-accepted reasons (MERGE-05 + the CAP-02 +34 B drift) and for **no other** reason.
- **Max feedback latency:** 30 s (host quick / native quick)

---

## Per-Task Verification Map

Task IDs are assigned by the planner. Until plans exist, the contract is requirement-level; each
plan MUST refine these rows into `{143}-{plan}-{task}` IDs and carry the command in its
`<verify><automated>` block. **Plan column `TBD` is a Wave-0 debt, not an exemption.**

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | 1 | HOST-01 | — | N/A | unit (call-arg) | `pytest tests/test_write_response_budget.py::test_write_uses_advertised_budget -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 1 | HOST-01 | — | Absent capability → safe default, never a refusal | unit | `…::test_absent_budget_falls_back_to_120s -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 1 | HOST-01 | — | Implausible advertised value is clamped away, not trusted | unit | `…::test_implausible_budget_is_clamped_away -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 1 | HOST-01 | — | N/A (D-12 negative proof) | unit (call-arg) | `…::test_non_write_paths_keep_default_timeout -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 1 | HOST-01 | — | Length-discriminated decode at computed `ver_end`, ≥2 identity lengths | unit (byte layout) | `pytest tests/test_hw_revision_gate.py -k cap03 -x` | ⚠️ extend | ⬜ pending |
| TBD | TBD | 1 | HOST-01 | — | N/A | unit (fake clock) | `…::test_long_gap_within_budget_does_not_time_out -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 1 | HOST-01 | — | N/A (BF-3: `0x0B` @ 49999 µs → 99 998 µs bound) | native | `pio test -e native_loop_v131 -f native/avr/test_loop_eprom_v131` | ⚠️ extend | ⬜ pending |
| TBD | TBD | 1 | HOST-01 | — | `energy_cap_us == 0` is UNCAPPED, not "cap at zero" | native | same | ⚠️ extend | ⬜ pending |
| TBD | TBD | 1 | HOST-01 | — | Overprogram term 0 for `factor == 0`, non-zero-and-capped for `factor == 3` | native | same | ⚠️ extend | ⬜ pending |
| TBD | TBD | 2 | HOST-02 | — | Mid-block DATA frame rendered, not raised on | unit | `pytest tests/test_write_progress.py::test_data_frame_in_main_phase_is_rendered -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 2 | HOST-02 | — | Frame is NOT acked (D-05) — stream stays in sync | unit (negative) | `…::test_progress_frame_is_not_acked -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 2 | HOST-02 | — | N/A | unit | `…::test_offset_write_bar_starts_at_zero -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 2 | HOST-02 | — | `start()` not re-entered on differing total | unit (negative) | `…::test_differing_total_does_not_rebuild_the_bar -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 2 | HOST-02 | — | Bar never rewinds across a block boundary | unit | `…::test_bar_does_not_rewind_when_firmware_drives_it -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 2 | HOST-02 | — | N/A | native (advancing `millis()` mock) | `pio test -e native_loop_v131` | ⚠️ extend + mock change | ⬜ pending |
| TBD | TBD | 2 | HOST-02 | — | Non-vacuity: zero frames when the clock does not advance | native | same | ⚠️ extend | ⬜ pending |
| TBD | TBD | 2 | HOST-02 | — | Emission compiled out under `SERIAL_ON_IO` (BF-2) — protects HOST-03 on Uno | source contract | `pytest tests/test_progress_emission_is_leonardo_only.py -x` (firmware repo) | ❌ W0 | ⬜ pending |
| TBD | TBD | 2 | HOST-03 | — | `0xBD` → `EpromOperationError` with `error_code == 0xBD`, message names the address | unit | `pytest tests/test_budget_failure_render.py::test_max_pulses_is_a_program_failure -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 2 | HOST-03 | — | Same for `0xBE`; `0xAE` carries the `--pulse-us` remediation clause | unit | `…::test_energy_cap_and_pulse_too_wide -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 2 | HOST-03 | — | Hint states abort semantics, offers NO retry (D-21) — forbidden substrings | unit (negative) | `…::test_hint_offers_no_retry_and_no_resumption -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 2 | HOST-03 | — | No host path keys on `0xB1` for this family (D-20) | source contract | `…::test_no_host_path_expects_write_failed_on_27c -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 2 | HOST-04 | — | Override rides the existing `pulse-delay` wire field; mutates no caller dict | unit | `pytest tests/test_pulse_us_override.py::test_override_rides_the_db_dict -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 2 | HOST-04 | — | No new wire key, no new command in the emitted frame | unit (negative) | `…::test_no_new_wire_field_is_added -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 2 | HOST-04 | — | Absent flag → DB pulse emitted unchanged | unit | `…::test_absent_flag_leaves_db_pulse -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 2 | HOST-04 | — | D-17 report line always prints and names both values | unit (CliRunner) | `…::test_override_always_reports -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 2 | HOST-05 | — | `0` / `65536` / `abc` → exit 2 with an actionable message | unit (CliRunner) | `…::test_out_of_range_is_refused_at_parse_time -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 2 | HOST-05 | — | NO serial port opened on refusal (`find_and_connect` not called) | unit (negative) | `…::test_refusal_opens_no_port -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 2 | HOST-05 | — | `write` with NO `--pulse-us` still exits 0 (Pitfall 3 regression guard) | unit (CliRunner) | `…::test_write_without_pulse_us_still_works -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 2 | HOST-05 | — | Flag absent from `read`/`verify`/`blank`/`erase` (D-18) | unit (negative) | `…::test_flag_is_write_only -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 1 | HOST-01 (BF-1) | — | Firmware ack layout matches the host decoder byte for byte | source contract / byte-layout parity | fixture built to the documented layout, decoded by the real `_decode_id_frame` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter_app/tests/test_write_response_budget.py` — HOST-01 host half
- [ ] `firestarter_app/tests/test_write_progress.py` — HOST-02 host half
- [ ] `firestarter_app/tests/test_budget_failure_render.py` — HOST-03
- [ ] `firestarter_app/tests/test_pulse_us_override.py` — HOST-04 + HOST-05
- [ ] `firestarter_app/tests/conftest.py` — `make_comm` gains `write_block_budget_s` (fail-closed
      obligation, mirrors the CAP-02 comment at `serial_comm.py:104-113`)
- [ ] `firestarter_app/tests/test_hw_revision_gate.py` — extend `_cap02_params` with an optional
      budget tail; add ≥2 identity lengths to prove the `ver_end` offset
- [ ] `firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp` — budget arithmetic
      cases **and** the `millis()` mock change (`AlwaysReturn(0)` → advancing counter, per
      `test_cobs_data_frame.cpp:140-167`)
- [ ] `firestarter/tests/test_progress_emission_is_leonardo_only.py` — the `#ifndef SERIAL_ON_IO`
      source-contract gate (BF-2)
- [ ] `firestarter/tests/golden/protocol_branch_inventory.json` — re-derived by independent parse, in
      the same commit as the `eprom.cpp` edit (D-23), with the changed site named in the commit message
- [ ] No framework install needed — both suites exist.

**D-25 obligation:** each new gate leg above must be **seen RED on a planted violation** and **seen
GREEN for the right reason**, with both transcripts captured verbatim in the owning plan's SUMMARY.
A pre-authored leg can be unreachable — RED alone proves nothing.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real bar motion during a real long write on hardware | HOST-02 | Needs a seated chip and a wall-clock-long write; this phase's proofs are off-hardware by scope (bench evidence is **Phase 145**) | Deferred to Phase 145 — do **not** claim it here |
| Intra-block progress on `uno` / `uno328pb` | HOST-02 | Structurally impossible — `SERIAL_ON_IO` defers frames into a 4-slot buffer (BF-2); the emission is compiled out | Record as an **explicit non-claim**, not as an untested behavior |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30 s
- [ ] Every `<automated>` block contains real shell bytes — **no HTML entities** (`&amp;&amp;` for
      `&&` made 30/37 legs unrunnable in a prior phase; check the bytes on disk, not the rendered view)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
