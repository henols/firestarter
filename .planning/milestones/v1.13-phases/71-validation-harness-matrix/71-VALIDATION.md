---
phase: 71
slug: validation-harness-matrix
status: validated
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-16
audited: 2026-06-17
---

# Phase 71 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `71-RESEARCH.md` §Validation Architecture (HIGH confidence).
> Refined 2026-06-16 against the final 6-plan / 2-wave split.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Unity (PlatformIO `[env:native]`, firmware) + pytest 7.x (host) |
| **Config file** | `firestarter/platformio.ini` §`[env:native]`; `firestarter_app/pyproject.toml` |
| **Quick run command** | `pio test -e native -f "*test_dispatch*"` (fw) · `cd firestarter_app && pytest tests/ -x` (host) |
| **Full suite command** | `pio test -e native && cd firestarter_app && pytest tests/ --cov-fail-under=70 && python tools/check_dispatch.py` |
| **Estimated runtime** | ~60–120 seconds (native + host + dispatch gate) |

> ⚠ Devcontainer Python is 3.12 but CI targets py39/3.11 — validate `ruff check` + `ruff format --check` against the target before claiming CI green (see project memory `reference_devcontainer_py312_masks_ci_py39`). The codegen emitter must stay ruff-clean (do NOT hand-normalize generated output — `reference_codegen_ruff_clean_emitter`).

---

## Sampling Rate

- **After every task commit (firmware):** `pio test -e native -f "*test_dispatch*"` (existing regression baseline — proves recording stub flag-off is a no-op)
- **After every task commit (host):** `cd firestarter_app && pytest tests/ -x --cov-fail-under=70 && python tools/check_dispatch.py`
- **After every plan wave:** full `pio test -e native && cd firestarter_app && pytest tests/ --cov-fail-under=70`
- **Before `/gsd-verify-work`:** all Tier-1 + Tier-2 cells GREEN; Tier-3 SKIP-deferred scaffold in place; `check_dispatch.py` exits 0; `pio run -e uno && -e leonardo` flash byte-count unchanged
- **Max feedback latency:** ~120 seconds

---

## Per-Task Verification Map

> Final — task IDs map to the 6-plan / 2-wave split. One row per requirement-behavior from `71-RESEARCH.md` §Phase Requirements → Test Map.

> **Audited 2026-06-17 (post-execution).** Host tiers re-run live: 110 pytest tests GREEN, `check_dispatch.py` exit 0 (744 chips), codegen drift byte-identical. Native Tier-1 (`pio test -e native`) is unrunnable in the devcontainer (no AVR toolchain) — recorded 77/77 PASS at execution (71-04); operator re-confirms on bench (Phase 73). GAP-1 (HARN-03) closed by 71-07, GAP-2 (HARN-04) closed by 71-08.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 71-01-T1 | 01 | 1 | HARN-01 (recording stub) | T-71-02, T-71-FLASH | Define-guarded recording buffer added to shared stub; bounded at 256 | unit (build) | `grep HOST_STUBS_RECORD_BUS test/native/avr/_shared/host_stubs_common.inc` | ✅ | ✅ green |
| 71-01-T2 | 01 | 1 | HARN-01 (Tier-1 regression) | T-71-FLASH | Existing suites compile unchanged with flag off (no-op); zero production flash | regression (Unity) | `pio test -e native -f "*test_dispatch*"` + `pio run -e uno -e leonardo` | ✅ | ⚠ bench (77/77 at exec; re-run P73) |
| 71-02-T1 | 02 | 1 | HARN-02 | T-71-INPUT, T-71-CONFUSE | Authored matrix JSON enumerates 6 families; validate_spec raises on malformed; input distinct from emitted artifact | unit (pytest) | `pytest tests/test_matrix_schema.py -x` | ✅ | ✅ green |
| 71-02-T2 | 02 | 1 | HARN-02 | T-71-DRIFT | Codegen emits committed C++ header; byte-identical re-generation (drift gate) | unit (pytest) | `pytest tests/test_gen_validation_header.py -x` | ✅ | ✅ green (11-row header, byte-identical) |
| 71-03-T1 | 03 | 1 | HARN-04 | T-71-VPP, T-71-INTEL | Per-family VPP invariants active; non-VPP families never see `vpp_mv > 6000`; gate green on clean DB | integration (script) | `python tools/check_dispatch.py` | ✅ | ✅ green (744 chips, exit 0) |
| 71-03-T2 | 03 | 1 | HARN-04 | T-71-ROGUE | `non_supported_dispatchable` populated; gate FAILS on a synthetic mis-dispatch / VPP-mismatch fixture (non-vacuous) | unit (pytest) | `pytest tests/test_check_dispatch_invariants.py -x` | ✅ | ✅ green |
| 71-04-T1 | 04 | 2 | HARN-01 (Tier-1) | T-71-VACUOUS, T-71-WIRED-WRONG | 5 family suites prove VPP/non-VPP CTL side-effect; VPP families carry a negative-control read | unit (Unity) | `pio test -e native -f "*test_val_eprom*"` (+ flash_intel/eeprom28c/flash3/flash4) | ✅ | ⚠ bench (77/77 at exec; re-run P73) |
| 71-04-T2 | 04 | 2 | HARN-01 (Tier-1 SRAM) | T-71-SRAM-FALSE | SRAM suite asserts `bus_recording_count()==0` (documented no-op; VAL-06 deferred to P73) | unit (Unity) | `pio test -e native -f "*test_val_sram*"` | ✅ | ⚠ bench — PARTIAL (WR-03: dispatch-level VPP assertion for 0x28/0x29 missing; direct-handler no-op covered) |
| 71-04-T3 | 04 | 2 | HARN-01 (Tier-1 wiring) | T-71-FLASH | All 6 suites in positive test_filter allowlist; full native battery green; zero production flash | regression (Unity) | `pio test -e native` + `pio run -e leonardo` | ✅ | ⚠ bench (77/77 + flash unchanged at exec; re-run P73) |
| 71-05-T1 | 05 | 2 | HARN-01 (Tier-2) | T-71-WIREDRIFT | Host wire dict for eprom/eeprom28c/flash3/flash4/flash_intel dispatches to correct handler (no serial port) | unit (pytest) | `pytest tests/test_val_wire_eprom.py … -x` | ✅ | ✅ green |
| 71-05-T2 | 05 | 2 | HARN-01 (Tier-2 SRAM) | T-71-SRAM-EPROM | SRAM rep chip dispatches to configure_sram AND never configure_eprom (BLOCKER-2) | unit (pytest) | `pytest tests/test_val_wire_sram.py -x` | ✅ | ✅ green |
| 71-06-T1 | 06 | 2 | HARN-01 (Tier-3) + HARN-02 | T-71-FORGE | `dev validate-family` composes cycle methods; SKIP-deferred when no board; emits distinct results artifact | integration (pytest) | `pytest tests/test_validate_family_cmd.py tests/test_matrix_artifact.py -x` | ✅ | ✅ green |
| 71-06-T2 | 06 | 2 | HARN-03 | T-71-VACUOUS | Negative control returns FAIL (verify *can* fail) | unit (pytest) | `pytest tests/test_validate_oracle.py -x` | ✅ | ✅ green (de-vacuumed by 71-07; distinct-hash proof) |
| 71-06-T2 | 06 | 2 | HARN-03 | T-71-UNO328 | `uno328pb` cells hard-coded N/A; no write cycle attempted | unit (pytest) | `pytest tests/test_validate_oracle.py -x` | ✅ | ✅ green |
| 71-06-T2 | 06 | 2 | HARN-03 | T-71-STALECAL | r1 ≈ 270000 ±25% precondition aborts the write path before any cycle | unit (pytest) | `pytest tests/test_validate_oracle.py -x` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky/bench-deferred*

---

## Wave 0 Requirements

- [x] `firestarter/test/native/avr/_shared/host_stubs_common.inc` — add `#define HOST_STUBS_RECORD_BUS` guarded recording buffer (D-04, single-edit-point) — **Plan 01**
- [x] `firestarter_app/tools/validation_matrix_spec.json` — authored matrix source (D-01) — **Plan 02**
- [x] `firestarter_app/tools/gen_validation_header.py` — codegen entrypoint → C++ header (D-01) — **Plan 02**
- [x] `firestarter/test/native/avr/_shared/validation_matrix.h` — GENERATED, committed header (11 rows after 71-08 trim) — **Plan 02 / 08**
- [x] `firestarter_app/tools/check_dispatch.py` — per-family VPP invariants + populated `non_supported_dispatchable` (HARN-04) — **Plan 03**
- [x] `firestarter/test/native/avr/test_val_{eprom,eeprom28c,flash3,flash4,flash_intel,sram}/` — 6 Tier-1 native suites + `platformio.ini` allowlist (HARN-01) — **Plan 04**
- [x] `firestarter_app/tests/test_val_wire_*.py` — 6 Tier-2 host wire round-trip files (HARN-01) — **Plan 05**
- [x] `firestarter_app/tests/test_validate_family_cmd.py` + `test_matrix_artifact.py` — Tier-3 runner scaffold + artifact (HARN-01/02) — **Plan 06**
- [x] `firestarter_app/tests/test_validate_oracle.py` — HARN-03 (negative control + uno328pb N/A + r1 precondition; de-vacuumed) — **Plan 06 / 07**
- [x] `firestarter_app/tests/test_matrix_schema.py`, `test_gen_validation_header.py`, `test_check_dispatch_invariants.py` — Plans 02/03

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Tier-1 native battery green + zero flash delta (`pio test -e native`, `pio run -e uno/-e leonardo`) | HARN-01 (Tier-1 + flash) | Requires PlatformIO + AVR toolchain absent from the devcontainer; recorded 77/77 PASS + flash unchanged at execution (71-01/71-04) | Operator re-runs `pio test -e native` and `pio run -e uno -e leonardo` on bench; expect 77/77 and zero flash-byte delta |
| Tier-1 SRAM dispatch-level VPP assertion for 0x28/0x29 (WR-03) | HARN-01 (Tier-1 SRAM) | Residual PARTIAL: `test_val_sram.cpp` proves no-op for all 4 protocols via direct-handler tests, but dispatch-path `CTRL_VPP` assertions exist only for 0x0E/0x27. Adding the 2 missing dispatch tests requires `pio test -e native` to verify GREEN — unrunnable here. Operator-deferred to Phase 73 (2026-06-17). | Phase 73: add `test_sram_dispatch_0x28/0x29_no_vpp` mirroring the 0x0E/0x27 pattern; run `pio test -e native -f "*test_val_sram*"` |
| Tier-3 HIL real cell evidence (post-write read+SHA on Leonardo, live r1≈270000 calibration) | HARN-03 (oracle, full proof) | Requires physical board + chip; deferred to Phase 73 by D-06/D-07 — Phase 71 records SKIP-deferred cells | Phase 73: run `dev validate-family` on bench with Leonardo/ACM0; software tiers in Phase 71 use deliberate-mismatch / mocked-r1 assertions, not real hardware |

*Phase 71 is software-first/flash-free by design — all host (Tier-2/Tier-3 software) cells are automated and re-verified green on 2026-06-17. Native Tier-1 suites exist and passed at execution (77/77) but require the AVR toolchain to re-run; the only residual coverage gap (WR-03, SRAM 0x28/0x29 dispatch-level VPP assertion) and all real-hardware evidence are explicitly deferred to Phase 73.*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 120s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated (8 plans executed: 6 build + 71-07/71-08 gap-closure; host tiers re-verified green 2026-06-17)

---

## Validation Audit 2026-06-17

Post-execution Nyquist audit (State A — existing VALIDATION.md). All host-automatable validation re-run live in the devcontainer; native Tier-1 deferred to bench (no AVR toolchain).

| Metric | Count |
|--------|-------|
| Requirements audited | 4 (HARN-01..04) |
| Gaps found | 1 (WR-03, native Tier-1 SRAM dispatch coverage) |
| Resolved | 0 (auto) |
| Escalated to manual-only | 1 (WR-03 → Phase 73, operator-chosen) |

**Live re-verification evidence:**
- Tier-2/Tier-3 host pytest (12 files): **110 passed** in 0.83s
- `python tools/check_dispatch.py`: **exit 0** — 744 chips, 730 supported, 14 non-dispatchable, 0 non_supported_dispatchable, 0 regressions
- `python tools/gen_validation_header.py` → `validation_matrix.h`: **byte-identical** (drift gate green, 11 rows)

**Gap-closure cross-check:** the two blockers in `71-VERIFICATION.md` (gaps_found, 12:00Z) were closed before this audit — GAP-1 (HARN-03 vacuous oracle) by Plan 71-07, GAP-2 (HARN-04 host dispatch divergence) by Plan 71-08. `71-UAT.md` records 6 passed / 0 issues / 2 hardware-skipped.

**No test files generated** — host surface had zero gaps; the single residual gap (WR-03) is firmware C++ requiring `pio` to verify GREEN, operator-deferred to Phase 73 rather than ship unrun.
