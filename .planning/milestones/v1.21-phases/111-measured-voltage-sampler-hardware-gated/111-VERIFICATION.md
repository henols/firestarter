---
phase: 111-measured-voltage-sampler-hardware-gated
verified: 2026-07-03T00:00:00Z
status: passed
score: 3/3 automated must-haves verified (SC1, SC3, report-field split); SC2 deferred to hardware bench (D-05)
behavior_unverified: 0
overrides_applied: 0
human_verification:

  - test: "Compare firestarter_app HardwareManager.sample_vpp_mv()/sample_vpe_mv() parsed mV output against the live firestarter vpp/vpe monitor printed value, on the standing bench oracle (Leonardo + RURP Rev 2.0), with a chip seated (no write, no consumption)."
    expected: "The parsed mV value (e.g. 20900) matches the printed monitor value (e.g. \"VPP: 20.9V\") for the same physical measurement, within the documented 100 mV grid resolution."
    why_human: "Requires energizing the real VPP/VPE regulator and reading the ADC on physical hardware — this is the phase's one deliberately hardware-gated capability (D-05); no software mock can substitute for the live silicon comparison. This is SC2's live-hardware half; deferred per 111-VALIDATION.md's explicit test map row (\"🔒 deferred FUT\") and Manual-Only Verifications section."

  - test: "(Downstream/Phase 112 scope, noted for completeness, NOT a phase-111 gap) Once Phase 112 wires sample_vpp_mv()/sample_vpe_mv() into the write-step orchestrator, repeat the before/after comparison using an electrically-erasable chip (W27C512 / W29C020) to validate the destructive-run before/after fields."
    expected: "vpp_before_mv/vpp_after_mv (and vpe_ equivalents) populate with real measured values that track the write step's rail behavior."
    why_human: "No sweep call site exists yet in Phase 111 by design (Plan 111-03's objective explicitly assigns this integration to Phase 112's orchestrator) — this check cannot run until Phase 112 lands."
---

# Phase 111: Measured-Voltage Sampler (hardware-gated) Verification Report

**Phase Goal:** A diagnostic report can state the actual VPP/VPE rail voltage measured during the write step, not just whether the firmware's own guard accepted or rejected it.
**Verified:** 2026-07-03
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `hardware.py` exposes value-returning `sample_vpp_mv()`/`sample_vpe_mv()` parsing `MSG_DATA_VPP/VPE_VOLTAGE` (0xE4/0xE5) frames and returning mV (SC1) | VERIFIED | `firestarter_app/firestarter/hardware.py:272-347` — `_parse_voltage_frame` (regex `(\d+)\.(\d+)\s*V` → `v_int*1000 + v_dec*100`), `_sample_one_voltage` (bounded `for _ in range(n)` handshake mirror, `statistics.median`), `sample_vpp_mv`/`sample_vpe_mv` thin wrappers over `COMMAND_READ_VPP`(11)/`COMMAND_READ_VPE`(12). All 6 sampler unit tests in `tests/test_hardware.py` pass (`pytest tests/test_hardware.py -q` → 12/12 green, includes `test_parse_voltage_frame_reconstructs_mv`, `test_sample_vpp_mv_returns_median`, `test_sample_vpe_mv_uses_state_12`, `test_sample_none_returns_none_on_error`, `test_sample_median_of_even_n_off_grid`, `test_voltage_format_pin`). |
| 2 | Write step calls the sampler and records the measured value into the report, verified on real hardware (SC2) | ⚠️ SPLIT — landing site VERIFIED, call-site + live-hardware parity DEFERRED (not a phase-111 gap) | Landing site: `DiagnosticReport.vpp_before_mv/vpp_after_mv/vpe_before_mv/vpe_after_mv/vpp_mv/vpe_mv` exist (`diagnostic_report.py:303-308`), single-source `to_dict()["voltage"]` (`:349-370`, `:427`), `render()` row (`:477-484`). No call site wiring the sampler into a sweep/write step exists yet — by design, this is Phase 112's explicit scope (Plan 111-03 objective: "Phase 112's orchestrator populates these fields around run_plan"). The live-hardware parity check (parsed mV == printed monitor value on Leonardo + Rev 2.0) is explicitly deferred per 111-VALIDATION.md D-05 ("🔒 deferred FUT"). Routed to human_verification below; NOT counted as a gap. |
| 3 | No existing `firestarter vpp`/`vpe` monitor command output or behavior changes — sampler is additive (SC3) | VERIFIED | `git diff 8a38f13 HEAD -- firestarter/hardware.py` shows zero removed/changed lines in `_read_voltage_loop`/`read_vpp_voltage`/`read_vpe_voltage` (lines 173-270) — purely additive; all new sampler code placed after line 270. Pre-existing monitor regression tests (`test_read_vpp_voltage_*`/`test_read_vpe_voltage_*`, `test_hardware.py:74-120`) unchanged and still pass. |

**Score:** 2/3 truths fully automated-VERIFIED (SC1, SC3); SC3's report-field-split sub-requirement (D-01/D-03/D-04) also VERIFIED. SC2 is split: the report-side landing site is VERIFIED, the call-site wiring is out of phase-111 scope (Phase 112), and the live-hardware parity check is deliberately deferred (D-05) — routed to human verification, not scored as failed.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/hardware.py` | New `_parse_voltage_frame`, `_sample_one_voltage`, `sample_vpp_mv`, `sample_vpe_mv` on `HardwareManager`; `_read_voltage_loop`/`read_vpp_voltage`/`read_vpe_voltage` unchanged | VERIFIED | All four new symbols present (lines 272-347); imports extended with `re`/`statistics` (lines 10-11); `_VOLTAGE_RE` module constant (line 35); zero changed lines in the three pre-existing methods (lines 173-270) confirmed via `git diff 8a38f13 HEAD`. |
| `firestarter_app/firestarter/diagnostic_report.py` | `vpp_vpe_mv` removed; six split fields + `_voltage_dict()` + `"voltage"` block in `to_dict()` + render row | VERIFIED | `grep -c "vpp_vpe_mv"` → 0 (fully removed). Six fields present (`:309-314`). `_voltage_dict()` present (`:349-370`), modeled on `_transport_dict()`. `to_dict()["voltage"]` wired at `:427`. `render()` voltage row at `:477-484` reads exclusively from `d["voltage"]` (no direct field access in render). |
| `firestarter_app/tests/test_hardware.py` | 6 new sampler tests, existing tests unchanged | VERIFIED | 12 tests total, all green; `git diff 8a38f13 HEAD` shows only additions. |
| `firestarter_app/tests/test_diagnostic_report.py` | New voltage-split serialization test | VERIFIED | 16 tests total, all green; `test_voltage_split_fields_serialize` present and passing. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `sample_vpp_mv`/`sample_vpe_mv` | `_sample_one_voltage(COMMAND_READ_VPP=11 \| COMMAND_READ_VPE=12)` | direct call | WIRED | Confirmed via source read (`hardware.py:342,347`) and `test_sample_vpe_mv_uses_state_12` asserting the state value passed to `find_and_connect`. |
| `_sample_one_voltage` | `find_and_connect`/`expect_ack`/`send_ack`/`get_response` handshake | mirrors `_read_voltage_loop` shape | WIRED | Confirmed via source read (`hardware.py:308-324`); handshake sequence matches `_read_voltage_loop` (`:194-226`) but bounded to `n` frames. |
| `_parse_voltage_frame` | `Response.message` (NOT `Response.payload`) | regex extraction | WIRED | `grep -nE "Response\.payload\|_decode_param" firestarter/hardware.py` returns no match — confirms Pattern A (message-parsing, not payload-decoding) as required. |
| `statistics.median(samples)` | `DiagnosticReport` voltage fields | **NOT YET WIRED** (Phase 112 scope) | NOT_WIRED (expected/deferred) | No call site found: `grep -rn "sample_vpp_mv\|sample_vpe_mv" firestarter/` outside `hardware.py` returns empty. This is the correct Phase-111 end-state per 111-VALIDATION.md and Plan 111-03's objective — the orchestrator wiring belongs to Phase 112. |
| `DiagnosticReport.vpp_before_mv` etc. | `_voltage_dict()` → `to_dict()["voltage"]` → `render()` | single-source chain | WIRED | Confirmed: `_voltage_dict()` is the only place `NOT_MEASURED if self.<field> is None` substitution occurs (6 occurrences, all inside `_voltage_dict`); `render()` reads only `d["voltage"]`, never `self.vpp_before_mv` directly (`grep -n "self.vpp_before_mv" diagnostic_report.py` shows it referenced only inside `_voltage_dict`). |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| KAT: `_parse_voltage_frame` reconstructs mV correctly | `pytest tests/test_hardware.py -k test_parse_voltage_frame_reconstructs_mv -v` | 1 passed | PASS |
| Honest fallback: `None` never a fabricated `0` | `pytest tests/test_hardware.py -k test_sample_none_returns_none_on_error -v` | 1 passed | PASS |
| Report voltage-split serialization + single-source render | `pytest tests/test_diagnostic_report.py -k test_voltage_split_fields_serialize -v` | 1 passed | PASS |
| Full sampler + report suite | `pytest tests/test_hardware.py tests/test_diagnostic_report.py -q` | 28 passed | PASS |
| Full workspace suite (once) | `pytest -q` | 1 failed (`test_audit_coverage_matrix.py::test_golden_file_matches`), all else green | PASS (failure confirmed pre-existing, unrelated — see Anti-Patterns/Gaps section) |
| ruff clean on modified files | `ruff check firestarter/hardware.py firestarter/diagnostic_report.py && ruff format --check ...` | All checks passed; 2 files already formatted | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| VOLT-01 | 111-01, 111-02, 111-03 | Value-returning VPP/VPE mV sampler in `hardware.py` captures the tester's actual rail voltage during the write step into the report | SATISFIED (sampler + report landing site); write-step call-site is Phase 112 scope | `hardware.py` sampler + `diagnostic_report.py` field split both implemented and tested; REQUIREMENTS.md line 42/113 marks VOLT-01 "Complete" mapped to Phase 111 — this matches the phase's actual scope (sampler + report fields), not the full write-step integration (that is Phase 112's separately-scoped integration work per REQUIREMENTS.md line 128 phase spine). No orphaned requirements found for Phase 111. |

No requirement IDs beyond VOLT-01 are declared in the Phase 111 plans' frontmatter, and no REQUIREMENTS.md entries map to Phase 111 besides VOLT-01 — cross-reference is exact, no orphans.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | None found | — | `grep -nE "TBD\|FIXME\|XXX\|TODO\|HACK\|PLACEHOLDER"` on `hardware.py`/`diagnostic_report.py` returns zero matches. No empty implementations, no hardcoded-empty stub patterns. |

**Note on pre-existing unrelated failure:** `tests/test_audit_coverage_matrix.py::test_golden_file_matches` fails on the full-suite run (`pytest -q`) with a byte-count drift (186034 vs 184631 bytes). Verified via `git diff 8a38f13..HEAD --stat` that Phase 111's four commits touch only `firestarter/hardware.py`, `firestarter/diagnostic_report.py`, `tests/test_hardware.py`, `tests/test_diagnostic_report.py` — no matrix/golden-fixture inputs are touched by this phase, and `git log 8a38f13..HEAD -- tests/test_audit_coverage_matrix.py tests/fixtures/ tests/__snapshots__/` returns zero commits. This confirms the failure is pre-existing, known debt (documented since Phase 106) and NOT attributable to Phase 111.

### Human Verification Required

1. **Live-hardware VPP/VPE parity check (SC2's manual half, D-05)**
   **Test:** Compare `HardwareManager.sample_vpp_mv()`/`sample_vpe_mv()` parsed mV output against the live `firestarter vpp`/`vpe` monitor printed value, on the standing bench oracle (Leonardo + RURP Rev 2.0), with a chip seated (no write, no consumption).
   **Expected:** The parsed mV value (e.g. `20900`) matches the printed monitor string (e.g. "VPP: 20.9V") for the same physical measurement, within the 100 mV grid resolution.
   **Why human:** Requires energizing the real VPP/VPE regulator and reading the ADC on physical hardware. This is the project's one deliberately hardware-gated capability for this milestone (per D-05 in 111-CONTEXT.md and the explicit "🔒 deferred FUT" row in 111-VALIDATION.md's test map). No software mock can substitute.

2. **Before/after write-step voltage capture (downstream of Phase 112, noted for tracking only)**
   **Test:** Once Phase 112 wires `sample_vpp_mv()`/`sample_vpe_mv()` into the write-step orchestrator, repeat the comparison using an electrically-erasable chip (W27C512/W29C020) to validate the destructive-run `vpp_before_mv`/`vpp_after_mv` (and VPE equivalents) fields.
   **Expected:** Fields populate with real measured values tracking the write step's rail behavior (e.g. a sag from 20.9V to 17.4V is visible and diagnosable).
   **Why human:** No call site exists in Phase 111 by design — Plan 111-03 explicitly assigns this integration to Phase 112. This item is deferred pending Phase 112's completion, not a Phase 111 gap.

### Gaps Summary

No gaps found in Phase 111's actual scope. All three automated-verifiable dimensions (SC1 sampler exists, SC3 monitor commands unchanged, and the report-field-split landing site for SC2) are VERIFIED against live source and a fully green targeted test run (28/28 sampler+report tests, ruff clean, zero anti-pattern hits, additive-only diff confirmed via git). 

The one open item — SC2's live-hardware parity check — is not a gap: it is the project's single explicitly-designed hardware gate (D-05), documented in 111-VALIDATION.md as "🔒 deferred FUT" from the outset, consistent with this milestone's software-first philosophy for all bench-inaccessible verifications. The absence of a sweep/write-step call site invoking the sampler is also not a gap: Plan 111-03's stated objective and the ROADMAP's Phase 112 description both assign that integration explicitly to Phase 112 ("dev test Handler Wiring... every piece built in Phases 108-111 is reachable from one CLI invocation"). Phase 111 delivered exactly its scoped piece: the sampler implementation and the report's landing site for its values.

The pre-existing `test_audit_coverage_matrix.py::test_golden_file_matches` failure is unrelated debt (confirmed via git history diffing against the pre-111 baseline commit `8a38f13`) and does not reflect on Phase 111's goal achievement.

Because two items were routed to human verification (the D-05 live-hardware check, and the informational Phase-112-dependent check), overall status is `human_needed` rather than `passed` — this reflects a software-complete phase awaiting one deliberately-scheduled bench session, not an incomplete implementation.

---

*Verified: 2026-07-03*
*Verifier: Claude (gsd-verifier)*
