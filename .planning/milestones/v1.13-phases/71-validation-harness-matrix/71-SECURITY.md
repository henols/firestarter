# SECURITY.md — Phase 71: Validation Harness + Matrix

**Milestone:** v1.13 — Programming Algorithm Validation + Gap Implementation
**Audit type:** `register_authored_at_plan_time: true` — verify declared mitigations exist in code; no new-threat scan.
**ASVS level:** L1 (no `<config>` block declared in plans; defaulted L1 / `block_on: open`).
**Audited:** 2026-06-17
**Result:** SECURED — 18/18 threats CLOSED, `threats_open: 0`.

Repos audited: `firestarter/` (firmware, branch `v1.13-algo-validation`), `firestarter_app/` (host CLI, same branch).

---

## Threat Verification (18 unique, dedup across plans 71-01..71-06)

### MITIGATE (17) — verified present in code

| Threat ID | Category | Evidence (file:line) |
|-----------|----------|----------------------|
| T-71-02 | Denial of Service | `firestarter/test/native/avr/_shared/host_stubs_common.inc:55,70` — `HOST_STUBS_MAX_RECORDING 256`; bound check `if (s_bus_recording_count < HOST_STUBS_MAX_RECORDING)` before each store. CLOSED. |
| T-71-FLASH | Tampering | All val test files live under `firestarter/test/` (PIO `src/`-only production build excludes them); confirmed zero leak into `firestarter/src/`. Build byte-count delta==0 documented (Leonardo 25482 B, 88.9%) — `71-VERIFICATION.md:195`, `71-04-SUMMARY.md`. CLOSED (structural). |
| T-71-INPUT | Tampering | `firestarter_app/tools/gen_validation_header.py:57-90` `validate_spec()` raises `ValueError`; `main():176` calls it BEFORE `emit_cpp_header():181`, returns 1 on failure. Proven by `tests/test_gen_validation_header.py:117` `test_validate_spec_called_before_emission` (exit 1 + no file written). CLOSED. |
| T-71-DRIFT | Tampering | `tests/test_gen_validation_header.py:74` `test_codegen_produces_byte_identical_output` regenerates and asserts `regenerated == committed` (line 106). CLOSED. |
| T-71-CONFUSE | Tampering | Distinct names: input `validation_matrix_spec.json` (underscore, `tools/`) vs runner artifact `validation-matrix.json` (hyphen). `cli_handlers.py:1301,1344` + emitted header `validation_matrix.h`. Test `test_artifact_named_with_hyphen` (`test_validate_family_cmd.py:177`). CLOSED. |
| T-71-VPP | Tampering / Damage | `tools/check_dispatch.py:78-85` `_FAMILY_VPP_INVARIANTS` (0,6000) for 5V handlers; range check `313-318` → `family_vpp_violations` → `sys.exit(1):475`. Non-hollow proof `tests/test_check_dispatch_invariants.py:126`. CLOSED. |
| T-71-ROGUE | Elevation of Privilege | `tools/check_dispatch.py:324-328` populates `non_supported_dispatchable` on dual violation (non-supported + VPP mismatch) → `sys.exit(1):475`. Dual-violation fixture proof (`test_check_dispatch_invariants.py` item 4). Closes v1.12 CR-01. CLOSED. |
| T-71-INTEL | Tampering | `tools/check_dispatch.py:83` `configure_flash_intel: (10000, 22000)` → min_vpp_mv=10000. Test `test_family_vpp_invariants_flash_intel_requires_elevated_vpp` (`:77`, asserts `lo >= 10000`) + zero-vpp violation fixture (`:140`). CLOSED. |
| T-71-VACUOUS | Spoofing | Tier-1 native: read-path negative control asserts VPP NOT set (`test_val_eprom.cpp:154-190`). Runner: `cli_handlers.py:1559-1573` maps `write_cycle_eprom` verdict (no vacuous self-compare; comment 1555-1558); `_classify_sha_result` distinct-hash FAIL proof (`test_validate_oracle.py:69`); negative-control exit-1 proof (`:101`). CLOSED. |
| T-71-WIRED-WRONG | Tampering | VPP families assert VPP-enable bit IS recorded (`test_val_eprom.cpp:113`); non-VPP families assert `TEST_ASSERT_BITS_LOW` for VPP-enable bits in every CTL write (`test_val_flash4.cpp:71-82`, also flash3/eeprom28c). CLOSED. |
| T-71-SRAM-FALSE | Repudiation | `test_val_sram.cpp:87` `TEST_ASSERT_EQUAL_INT_MESSAGE(0, bus_recording_count(), ...)` documents no-op; VAL-06 deferred to Phase 73 per comment (`:80`). CLOSED. |
| T-71-SRAM-EPROM | Tampering / Damage | `tests/test_val_wire_sram.py:90` `dispatch()==configure_sram` AND `:113` `!= "configure_eprom"` (BLOCKER-2). Reinforced in gate `check_dispatch.py:330` `sram_in_eprom`. CLOSED. |
| T-71-WIREDRIFT | Tampering | `tests/test_val_wire_sram.py:64,86,89` reuse production `EpromDatabase.convert_to_programmer` + `check_dispatch.dispatch()` — no hand-rolled mirror. CLOSED. |
| T-71-WRONGBOARD | Tampering | `cli_handlers.py:1269,1401,1559-1575` — `_AUTHORITATIVE_PASS_BOARD = "leonardo"`; only Leonardo yields `pass_type:"authoritative"`, all others `"advisory"`. Test `test_classify_sha_match_is_pass_on_leonardo` + advisory cases. CLOSED. |
| T-71-UNO328 | Damage | `cli_handlers.py:1480-1497` hard N/A branch for `uno328pb`; returns before any `write_cycle_eprom`. Tests `test_uno328pb_write_cell_is_na` (`:154`) + `test_uno328pb_no_write_cycle_called` (`:202`). CLOSED. |
| T-71-STALECAL | Tampering | `cli_handlers.py:1260-1262,1414-1416,1513-1521` — `_check_r1_precondition` (270000 ±25%); out-of-band → `sys.exit(2)` before any cycle. Tests `test_validate_oracle.py:251-265`. CLOSED. |
| T-71-FORGE | Tampering | `cli_handlers.py` — artifact `validation-matrix.json` only ever `write_text` (`:1361,1364`); never read as input. Only spec read is `validation_matrix_spec.json` (`:1281`). Test `test_authored_spec_not_written` (`:190`). CLOSED. |

### ACCEPT (1) — documented accepted risk

| Threat ID | Category | Disposition rationale | Verification |
|-----------|----------|-----------------------|--------------|
| T-71-SC | Tampering (supply-chain / package installs) | **ACCEPTED.** Phase 71 installs NO packages. Reuses the present PlatformIO / Unity / ArduinoFake firmware substrate and the present pytest / ruff / stdlib-json host substrate (D-10). No new dependency was added: `firestarter_app/pyproject.toml` change in 71-07 edits only a mypy-watermark comment (no dependency line); `firestarter/platformio.ini` change in 71-04 registers test suites + build flags, adds no `lib_deps` source. No package-legitimacy checkpoint is warranted. |

---

## Unregistered Flags

None. SUMMARY `## Threat Flags` sections reviewed for all 8 plans:
- 71-01, 71-02, 71-04, 71-05, 71-07: "None" — no new attack surface.
- 71-06: 5 flags, all map to existing registered IDs (T-71-VACUOUS, T-71-WRONGBOARD, T-71-UNO328, T-71-STALECAL, T-71-FORGE) — informational, no unmapped surface.
- 71-03, 71-08: gap-closure plans with no `## Threat Flags` section emitted; SUMMARY `tech_stack.added: []` confirms no new dependency/surface. 71-08 trimmed the flash4 host-matrix spec to `protocols=[5]` (CR-02), regenerated header byte-identically (drift gate green) — no new surface.

No `unregistered_flag` recorded.

---

## Gap-closure plans (71-07, 71-08) — threat impact

The two iteration gaps from `71-VERIFICATION.md` were closed without leaving any declared mitigation absent:

- **GAP-1 (SC#3 / HARN-03, oracle vacuousness):** the vacuous `_classify_sha_result(evidence_sha, evidence_sha)` self-match call was removed; the cell verdict now derives from `write_cycle_eprom`'s own internal source-vs-readback SHA compare (`cli_handlers.py:1536,1559`). Directly strengthens T-71-VACUOUS — verified non-vacuous by `test_validate_oracle.py` negative-control (mismatch → FAIL → exit 1).
- **GAP-2 (SC#4 / HARN-04, flash4 dispatch consistency):** resolved by trimming the host matrix spec to `protocols=[5]` so the host mirror reflects what `check_dispatch.dispatch()` actually routes. Firmware-level 0x35/0x39 coverage remains in the native C++ suite (`test_val_flash4.cpp`), which asserts no-VPP for those protocols (T-71-WIRED-WRONG). Internal-consistency fix; no declared threat mitigation removed.

---

## Disposition

**SECURED.** All 17 MITIGATE threats have their declared mitigation present in implemented code with a corresponding negative-control / non-hollow proof; the 1 ACCEPT threat (T-71-SC) is documented above as accepted risk. `threats_open: 0`.

Implementation files were not modified (read-only audit).
