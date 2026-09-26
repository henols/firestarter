---
phase: 71-validation-harness-matrix
verified: 2026-06-16T12:00:00Z
status: passed
score: 4/4
overrides_applied: 0
re_verification:
  re_verified: 2026-08-09
  previous_status: gaps_found
  previous_score: 2/4
  gaps_closed: [GAP-1, GAP-2]
  gaps_remaining: []
  regressions: []
  note: |
    Both GAP-1 and GAP-2 were closed by later work and this record was never
    re-run. Re-verified 2026-08-09 against the v1.31 app/firmware trees; see
    "Re-Verification 2026-08-09" at the end of this file for the evidence.
gaps:
  - truth: "The matrix bakes in a NON-VACUOUS PASS oracle: a PASS requires an independent post-write full read + SHA compare (SC#3 / HARN-03)"
    status: closed-verified-2026-08-09
    reason: "In dev_validate_family (cli_handlers.py:1556-1562), when write_cycle_eprom returns 0, the code calls _classify_sha_result(evidence_sha, evidence_sha, board) where BOTH arguments are the source-image SHA — the same object compared to itself. The comparison is always equal so the oracle call always yields PASS regardless of what was read back. _classify_sha_result is a correctly-implemented comparator but is never given a readback SHA to compare against. No test exercises a case where write_cycle_eprom returns 0 but the oracle call would fail — the negative-control test only exercises the verdict_int==1 (FAIL) return path, which bypasses _classify_sha_result entirely."
    artifacts:
      - path: "firestarter_app/firestarter/cli_handlers.py"
        issue: "Lines 1558-1564: _classify_sha_result(evidence_sha, evidence_sha, board) — first arg should be readback_sha, second should be source_sha; passing the same SHA for both is a self-comparison that never fails"
      - path: "firestarter_app/tests/test_validate_oracle.py"
        issue: "test_write_cycle_pass_on_leonardo_is_authoritative (line 381) does not detect the bug: it checks verdict=='PASS' when write_cycle_eprom returns 0, which is the exactly the vacuous path"
    missing:
      - "write_cycle_eprom must surface the readback SHA (or per-run file path) to the caller so dev_validate_family can supply a real readback_sha argument to _classify_sha_result"
      - "OR: drop the redundant _classify_sha_result call for the verdict_int==0 branch and trust write_cycle_eprom's return code directly as the authoritative oracle signal (the simplest correct fix per the code review)"
      - "A test must exercise the PASS verdict path through _classify_sha_result with distinct source_sha and readback_sha values to prove the comparator is actually called correctly"
  - truth: "check_dispatch.py is extended with per-family dispatch invariants AND its hollow non_supported_dispatchable inverse detector is populated (SC#4 / HARN-04)"
    status: closed-verified-2026-08-09
    reason: "The dispatch() host mirror (check_dispatch.py:133-157) handles only protocol 0x05 for flash4; protocols 0x35 and 0x39 fall through to the protocol!=0 guard and return 'not_implemented'. The firmware (confirmed in memory.cpp and CLAUDE.md) dispatches all three {0x05, 0x35, 0x39} to configure_flash4. The authored validation_matrix_spec.json explicitly declares [5, 53, 57] (i.e. 0x05, 0x35, 0x39) as flash4 protocols. The Tier-1 C++ tests (test_val_flash4.cpp:104-158) test 0x35 and 0x39 against the real firmware and they pass, proving firmware truth. But the host dispatch mirror is inconsistent with both the spec and firmware. REQUIREMENTS.md itself marks HARN-04 as unchecked ([ ]) / Pending."
    artifacts:
      - path: "firestarter_app/tools/check_dispatch.py"
        issue: "dispatch() at line 141: only 'if protocol == 0x05: return configure_flash4'. Protocols 0x35 and 0x39 are unhandled — if any chip with these protocols were added to the DB, check_dispatch would fail them as not_implemented even though firmware handles them correctly"
    missing:
      - "Option A (minimal): remove 0x35 and 0x39 from validation_matrix_spec.json flash4 protocols entry and regenerate validation_matrix.h, aligning spec with host KNOWN_PROTOCOLS and check_dispatch reality"
      - "Option B (correct the mirror): add 0x35 and 0x39 to dispatch() as configure_flash4 cases and add them to _ALGO_MEM_TYPE, making the host mirror truthful"
      - "REQUIREMENTS.md checkbox for HARN-04 must be checked once the divergence is resolved"
---

# Phase 71: Validation Harness + Matrix Verification Report

**Phase Goal:** A reusable, software-first three-tier validation harness + declarative per-family matrix exists and is the spine through which every family reports — adding zero production firmware flash, and baking in a non-vacuous PASS oracle so bench time is spent only on proven-RED divergences.

**Verified:** 2026-06-16T12:00:00Z
**Status:** passed (re-verified 2026-08-09 — both gaps closed; see "Re-Verification 2026-08-09" at end)
**Re-verification:** Yes — 2026-08-09, `gaps_found` → `passed`, GAP-1 + GAP-2 closed, 0 regressions

> **The two FAILED rows below are the 2026-06-16 findings, preserved verbatim as the
> historical record.** Both were closed by later work; the closure evidence is at the
> end of this file. Current status is 4/4.

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Three-tier harness (Tier-1 native Unity recording stubs, Tier-2 host wire pytest, Tier-3 dev validate-family runner composing cycle methods) exists and runs in CI; zero production flash added | VERIFIED | host_stubs_common.inc has HOST_STUBS_RECORD_BUS guard; 6 Tier-1 suites under native/ all in platformio.ini test_filter; 6 Tier-2 test_val_wire_*.py files; dev validate-family subcommand in cli_handlers.py; production envs are uno/uno328pb/leonardo only |
| 2 | Declarative per-family matrix data file (validation_matrix_spec.json) drives native suites and bench runner; committed validation-matrix.{json,md} artifact emitted per cell | VERIFIED | validation_matrix_spec.json exists in tools/; gen_validation_header.py emits validation_matrix.h (committed, 13-row struct); dev validate-family emits validation-matrix.json/.md; artifact is distinct from spec (hyphens vs underscores per D-02) |
| 3 | Non-vacuous PASS oracle: Leonardo-only authoritative PASS, negative control proving verify CAN fail, retry-count capture, per-task r1 precondition, uno328pb hard-coded N/A | FAILED | Hardware-path oracle is vacuous: cli_handlers.py:1556-1562 calls _classify_sha_result(evidence_sha, evidence_sha, board) — same SHA compared to itself, always PASS regardless of actual readback. The negative-control test only exercises the verdict_int==1 branch (write_cycle_eprom returning 1), which bypasses _classify_sha_result entirely. _classify_sha_result, uno328pb N/A, r1 precondition, and retry_count are all correctly implemented individually; the bug is specifically in the two-arg call site where readback_sha is not distinct from source_sha |
| 4 | check_dispatch.py extended with per-family VPP dispatch invariants AND hollow non_supported_dispatchable inverse detector populated (HARN-04) | FAILED | _FAMILY_VPP_INVARIANTS and family_vpp_violations are implemented and wired. non_supported_dispatchable is populated for dual-violation (VPP mismatch + non-supported). However: dispatch() host mirror only maps 0x05 to configure_flash4; firmware dispatches {0x05, 0x35, 0x39} to configure_flash4 per memory.cpp + CLAUDE.md. Spec declares [5, 53, 57] as flash4 protocols. Host mirror would return not_implemented for 0x35/0x39 — a structural inconsistency between harness tiers. REQUIREMENTS.md marks HARN-04 as [ ] Pending. |

**Score (2026-06-16, historical):** 2/4 truths verified (SC#1 VERIFIED, SC#2 VERIFIED, SC#3 FAILED, SC#4 FAILED)

**Score (2026-08-09, current):** 4/4 — SC#3 closed (vacuous call site removed, distinct-SHA
negative control added, 19/19 oracle tests pass); SC#4 closed (CR-02 spec/mirror alignment,
`check_dispatch.py` exit 0 over 746 chips, firmware truth preserved in `test_val_5v_page.cpp`)

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/test/native/avr/_shared/host_stubs_common.inc` | Recording bus stub with HOST_STUBS_RECORD_BUS guard | VERIFIED | Guard exists at line 54; clear_bus_recording/bus_recording_count/recorded_reg/recorded_data all present; #else preserves (void)reg;(void)data; no-op; bound-check at HOST_STUBS_MAX_RECORDING=256 |
| `firestarter/test/native/avr/_shared/validation_matrix.h` | Generated C++ header with VAL_FAMILIES struct from spec | VERIFIED | 13-row table present; DO NOT EDIT banner; all 6 families represented across 13 protocol entries |
| `firestarter_app/tools/validation_matrix_spec.json` | Authored spec driving both native suites and bench runner | VERIFIED | 6 families; handlers/protocols/rep_chip/tier1/tier2/tier3 per family; note: flash4 declares protocols [5,53,57] including 0x35/0x39 which creates host-dispatch inconsistency (CR-02) |
| `firestarter_app/tools/gen_validation_header.py` | Codegen script producing validation_matrix.h | VERIFIED | Validate-first; deterministic; mirrors codegen.py shape; drift gate in test_gen_validation_header.py |
| `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp` | Tier-1 EPROM suite using recording bus | VERIFIED | Positive/negative tests present; uses clear_bus_recording + recording_has_vpp_enable assertions; covers 0x07/0x08/0x0B |
| `firestarter/test/native/avr/test_val_sram/test_val_sram.cpp` | Tier-1 SRAM suite proving zero-VPP | VERIFIED (partial) | Direct handler tests cover all 4 protocols; full dispatch tests cover only 0x0E and 0x27 — 0x28 and 0x29 have no dispatch-level test (WR-03 from code review) |
| `firestarter_app/firestarter/cli_handlers.py` | dev validate-family subcommand + oracle | PARTIAL | Subcommand exists with SKIP-deferred path, uno328pb N/A, r1 precondition, retry_count; oracle function _classify_sha_result is correctly coded; hardware-path call site passes source_sha as both arguments (CR-01 bug) |
| `firestarter_app/tools/check_dispatch.py` | Per-family VPP invariants + non_supported_dispatchable populated | PARTIAL | _FAMILY_VPP_INVARIANTS defined; family_vpp_violations wired to gate; non_supported_dispatchable populated for dual-violation case via synthetic test; dispatch() missing 0x35/0x39 → configure_flash4 mapping (CR-02) |
| `firestarter_app/tests/test_validate_oracle.py` | HARN-03 oracle proof | PARTIAL | 18 tests; negative control tests verdict_int==1 path only; test_write_cycle_pass_on_leonardo_is_authoritative does not verify the oracle is called with distinct hashes |
| `firestarter_app/tests/test_check_dispatch_invariants.py` | HARN-04 proof | VERIFIED (for VPP invariants) | 10 tests; real-DB exits 0; synthetic sram+vpp=12000 fires; synthetic flash_intel+vpp=0 fires; inverse detector fires on dual-violation |
| `firestarter_app/tests/test_val_wire_eprom.py` through `test_val_wire_sram.py` | 6 Tier-2 wire round-trip suites | VERIFIED | All 6 exist; rep_chip from spec; dispatch() from check_dispatch; no serial port; SRAM adds BLOCKER-2 safety assertion |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| host_stubs_common.inc #ifdef HOST_STUBS_RECORD_BUS | rurp_write_to_register recording | define guard + function replacement | WIRED | All 6 Tier-1 host_stubs.cpp define HOST_STUBS_RECORD_BUS before including the shared .inc |
| test_val_*.cpp | recording API (clear_bus_recording/bus_recording_count) | extern "C" declarations in each test file | WIRED | Verified in test_val_eprom.cpp:48-52 and test_val_sram.cpp pattern |
| gen_validation_header.py | validation_matrix.h | codegen from spec | WIRED | Drift gate test verifies byte-identical output; committed header present |
| dev_validate_family | write_cycle_eprom | composes cycle method (D-10 no re-impl) | WIRED | cli_handlers.py:1539-1546 calls app.eprom_operator.write_cycle_eprom |
| dev_validate_family verdict_int==0 path | _classify_sha_result oracle | oracle call at 1558-1564 | WIRED (VACUOUS) | Oracle is called but with evidence_sha as both args — self-comparison always PASS |
| check_dispatch.py scan loop | _FAMILY_VPP_INVARIANTS | per-chip vpp_mv range check | WIRED (scoped to flash_intel only) | _DB_CHECKED_VPP_INVARIANTS limits DB-level enforcement to configure_flash_intel; 5V-family invariants proven only via synthetic fixtures |
| dispatch() | configure_flash4 | protocol 0x35/0x39 | NOT WIRED | dispatch() only maps 0x05; 0x35 and 0x39 return not_implemented |

---

## Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|-------------------|--------|
| cli_handlers.py dev_validate_family | cell_verdict on PASS path | _classify_sha_result(evidence_sha, evidence_sha, board) | No — source_sha compared to itself | HOLLOW — oracle call is self-comparison; result is always match |
| cli_handlers.py dev_validate_family | cell_verdict on FAIL path (verdict_int==1) | write_cycle_eprom return code directly | Yes — write_cycle_eprom's internal SHA comparison is real | FLOWING |
| check_dispatch.py | family_vpp_violations | vpp_mv from electrical block + _FAMILY_VPP_INVARIANTS[handler] | Yes — for configure_flash_intel; DB-level only | FLOWING (scoped) |

---

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Tier-2 + oracle + dispatch invariant tests pass | pytest tests/test_validate_oracle.py tests/test_check_dispatch_invariants.py tests/test_val_wire_eprom.py tests/test_val_wire_flash4.py tests/test_matrix_artifact.py | 51 passed, 0 failed | PASS |
| check_dispatch exits 0 on clean DB (744 chips) | python tools/check_dispatch.py | "PASS: all 744 chips scanned; exit 0" | PASS |
| dispatch(0x35, 5) returns configure_flash4 | python -c "from tools.check_dispatch import dispatch; print(dispatch(0x35,5))" | "not_implemented" | FAIL — expected configure_flash4, got not_implemented; confirms CR-02 |

---

## Probe Execution

Step 7c: No probe scripts found or declared in PLAN files. Skipped.

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| HARN-01 | Plans 01, 04, 05 | Three-tier harness: recording stub + wire tests + Tier-3 runner | SATISFIED | All three tiers implemented and wired; flash unchanged |
| HARN-02 | Plans 02, 06 | Declarative per-family matrix spec driving suites + artifact | SATISFIED | validation_matrix_spec.json + gen_validation_header.py + validation-matrix.json emitter all present and functional |
| HARN-03 | Plan 06 | Non-vacuous PASS oracle | BLOCKED | Hardware-path oracle call site at cli_handlers.py:1556-1560 passes source_sha as both args — always self-matches; negative-control test exercises verdict_int==1 bypass path only |
| HARN-04 | Plan 03 | check_dispatch per-family VPP invariants + non_supported_dispatchable populated | BLOCKED | VPP invariants implemented and flash_intel enforced against DB; dispatch() host mirror missing 0x35/0x39 → configure_flash4; REQUIREMENTS.md marks this [ ] Pending |

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| cli_handlers.py | 1559-1562 | _classify_sha_result(evidence_sha, evidence_sha, board) — SHA compared to itself | BLOCKER | SC#3 non-vacuous oracle is false for the hardware PASS path |
| cli_handlers.py | 1358 | datetime.utcnow() deprecated since Python 3.12 | WARNING | DeprecationWarning in tests; will become error in future Python |
| cli_handlers.py | 1263-1265 | _EVIDENCE_SHA_SOFTWARE_SENTINEL defined but never used | INFO | Dead code; unnecessary sha256 computation on module import |
| check_dispatch.py | 141 | dispatch(0x35, ...) and dispatch(0x39, ...) return not_implemented | WARNING | Inconsistent with firmware memory.cpp and validation_matrix_spec.json; latent regression if 0x35/0x39 chips added to DB |
| test_val_sram.cpp | 152-167 | main() registers dispatch tests for 0x0E and 0x27 only; 0x28 and 0x29 missing | WARNING | BLOCKER-2 "SRAM never reaches VPP" not exercised end-to-end for 2 of 4 protocols |

---

## CR-01 Assessment: Non-Vacuous Oracle (SC#3 / HARN-03)

**Finding: BLOCKER — SC#3 is not achieved for the hardware path.**

The code review finding CR-01 is confirmed by direct code inspection:

```python
# cli_handlers.py:1548-1562
evidence_sha: Optional[str]
try:
    evidence_sha = hashlib.sha256(Path(source).read_bytes()).hexdigest()
except OSError:
    evidence_sha = None

if verdict_int == 0:
    oracle = _classify_sha_result(
        evidence_sha or "",   # <-- source image SHA
        evidence_sha or "",   # <-- SAME source image SHA (not readback SHA)
        board,
    )
    cell_verdict = oracle["verdict"]
```

`write_cycle_eprom` returns `int` (0/1/2) and does not surface the readback SHA to the caller. `dev_validate_family` derives `evidence_sha` from the source image only. Both args to `_classify_sha_result` are the same source SHA — the oracle call is a guaranteed PASS when `verdict_int == 0`.

The negative-control test (`test_negative_control_write_cycle_returns_fail`) proves `verdict_int==1` maps to FAIL verdict — this is correct. But it does not exercise the "write_cycle_eprom returns 0 yet readback differs from source" scenario — that scenario is impossible to detect through the current call site.

**Important nuance:** `write_cycle_eprom` internally performs the real SHA comparison (eprom_operations.py:774: `source_sha = hashlib.sha256(Path(source_image_path).read_bytes()).hexdigest()`) and returns 1 if any readback fails. So the PASS verdict is not *wrong* — if write_cycle_eprom returns 0, the chip did match. But the SC#3 requirement asks for an *independent post-write full read + SHA compare*, meaning the validate-family runner should do its own comparison. The current design delegates entirely to write_cycle_eprom and the `_classify_sha_result` call adds no actual verification.

The requirement "a PASS requires an independent post-write full read + SHA compare" is not satisfied — the oracle call is a self-comparison stub.

---

## CR-02 Assessment: Host Dispatch Divergence (SC#4 / HARN-04)

**Finding: BLOCKER — SC#4 (HARN-04) has a structural inconsistency.**

`dispatch()` in `check_dispatch.py:141` handles only `protocol == 0x05` → `configure_flash4`. Protocols `0x35` (0x35 = decimal 53) and `0x39` (0x39 = decimal 57) fall through to line 149 (`if protocol != 0: return "not_implemented"`).

Confirmed by spot-check:
```
dispatch(0x35, 5) → "not_implemented"  (expected: "configure_flash4")
dispatch(0x39, 5) → "not_implemented"  (expected: "configure_flash4")
```

Firmware `memory.cpp` (confirmed in CLAUDE.md: "protocol ∈ {0x05, 0x35, 0x39} → configure_flash4") and `test_val_flash4.cpp` (tests 0x35 and 0x39 against real firmware, both pass) both treat all three as flash4.

`validation_matrix_spec.json` declares `"protocols": [5, 53, 57]` for flash4.

No current DB chip uses 0x35 or 0x39 (confirmed by DB scan: 0 chips), so this is a **latent** inconsistency — the gate does not fail today. But the spec, the Tier-1 native tests, and the firmware all agree that 0x35/0x39 are flash4 protocols, while the host dispatch mirror disagrees.

REQUIREMENTS.md marks HARN-04 as `[ ]` (Pending), consistent with the finding that this SC was not completed.

---

## Human Verification Required

### 1. Firmware Flash Byte-Count Unchanged

**Test:** Run `pio run -e uno` and `pio run -e leonardo` before and after the Phase 71 changes; compare reported flash byte-counts.
**Expected:** Zero delta — test-only .inc file under test/ is excluded from production src_filter.
**Why human:** PlatformIO + AVR toolchain not available in the devcontainer; cannot run pio commands.

### 2. Tier-1 Native Suites Pass (pio test -e native)

**Test:** Run `pio test -e native` for all 6 new validation suites (test_val_eprom, test_val_eeprom28c, test_val_flash3, test_val_flash4, test_val_flash_intel, test_val_sram).
**Expected:** All pass; no linker "undefined reference to recording API" errors with HOST_STUBS_RECORD_BUS off for existing suites.
**Why human:** PlatformIO + ArduinoFake not available in the devcontainer.

---

## Gaps Summary

Two blockers prevent goal achievement:

**GAP-1 (SC#3 / HARN-03): Vacuous hardware-path oracle.** The `dev validate-family` hardware PASS verdict is never independently verified against the chip readback — `_classify_sha_result` is called with `evidence_sha` as both arguments, making it a guaranteed self-match. The oracle function itself is correct; the call site is wrong. Fix: either extend `write_cycle_eprom` to surface the readback SHA, or trust `write_cycle_eprom`'s return code directly and remove the vacuous `_classify_sha_result` call for `verdict_int==0`.

**GAP-2 (SC#4 / HARN-04): Host dispatch mirror missing flash4 protocols 0x35/0x39.** `check_dispatch.dispatch()` returns `not_implemented` for protocols 0x35 and 0x39, while firmware dispatches them to `configure_flash4`. The spec and Tier-1 C++ tests declare and test them as flash4. This is a latent inconsistency (no current DB chips use them) but means the harness has an internal contradiction across tiers. REQUIREMENTS.md itself marks HARN-04 as Pending.

**Secondary findings (not blockers for plan-phase, noted for awareness):**
- WR-03: SRAM Tier-1 dispatch tests cover only 0x0E/0x27; 0x28/0x29 have no dispatch-level VPP assertion (the BLOCKER-2 guarantee is not fully exercised).
- WR-01: `datetime.utcnow()` deprecation in cli_handlers.py:1356.
- IN-03: `_EVIDENCE_SHA_SOFTWARE_SENTINEL` defined but never used.

---

_Verified: 2026-06-16T12:00:00Z_
_Verifier: Claude (gsd-verifier)_

---

## Re-Verification 2026-08-09

Re-run during the v1.31 pre-close carry-over sweep. Both gaps were closed by later
work; this record simply was never re-run. **Status: `gaps_found` → `passed` (4/4).**

### GAP-1 (SC#3 / HARN-03) — vacuous PASS oracle — CLOSED

The vacuous call site is **gone**. `_classify_sha_result` is no longer called from
production code at all — `grep -rn "_classify_sha_result" firestarter/ tests/` returns
one definition (`firestarter/cli_handlers.py:1775`) and test call sites only. No
`cli_handlers.py` caller remains.

The fix taken is the second option this very report recommended — "trust
`write_cycle_eprom`'s return code directly and remove the vacuous
`_classify_sha_result` call for `verdict_int==0`". `dev_validate_family` now maps the
verdict directly, with the reasoning recorded inline:

> `verdict_int==0`: write_cycle_eprom's own source-vs-readback SHA compare returned 0
> (PASS). Map directly to board-class verdict … The real readback compare already
> happened inside write_cycle_eprom.

The missing negative control also now exists. `tests/test_validate_oracle.py` asserts
the comparator can fail with **distinct** hashes:

- line 70-80 — "`_classify_sha_result` with DISTINCT hashes on Leonardo yields FAIL …
  This proves `_classify_sha_result` CAN return FAIL — it is not a vacuous oracle."
- line 373 — `_classify_sha_result(readback_sha=sha, source_sha=sha, board="uno")` (equal case)
- line 381 — `_classify_sha_result(readback_sha=sha_a, source_sha=sha_b, board="uno")` (distinct case)

**Measured 2026-08-09:** `python3 -m pytest tests/test_validate_oracle.py` → **19 passed**.

### GAP-2 (SC#4 / HARN-04) — host dispatch mirror vs 0x35/0x39 — CLOSED

Resolved **2026-06-16** as "CR-02" — the same day this report was written — via the
report's own Option A (align spec with the host mirror), with the rationale recorded
in `tools/validation_matrix_spec.json` as a `protocols_note`. Every factual claim in
that note was independently re-checked today:

| Claim in the CR-02 note | Verified 2026-08-09 |
|---|---|
| Spec no longer declares 0x35/0x39 as a host-dispatchable family | ✓ `5v_page` → `protocols=[5]`; no `53`/`57` anywhere in the spec |
| `check_dispatch.py` mirror is consistent with the spec | ✓ `KNOWN_PROTOCOLS` omits 0x35/0x39; `dispatch()` maps `0x05` → `configure_flash_5v_page` |
| Firmware still dispatches 0x35/0x39 to the 5V-page handler | ✓ `firestarter/src/proms/memory.cpp:110` — `protocol == PROTO_FLASH_5V_PAGE \|\| PROTO_PHANTOM_0x35 \|\| PROTO_PHANTOM_0x39` |
| Firmware truth is preserved by native Tier-1 coverage | ✓ `test/native/avr/test_val_5v_page/test_val_5v_page.cpp` — `make_handle(0x35, …)` at lines 112/121 and `make_handle(0x39, …)` at lines 132/141, read + write, VPP-absence asserted |
| Zero DB chips carry algorithm 0x35/0x39, so the host path is unreachable | ✓ consistent with `check_dispatch.py` scanning 746 chips with 0 violations |

The v1.19 rename landed on top of this (`configure_flash4` → `configure_flash_5v_page`),
and `include/proto_constants.h:32-39` now documents *why* these two are phantoms —
0x35 is minipro's ITE-EC label, 0x39 has no `IC2_ALG` constant at all. The
harness-internal contradiction the gap described no longer exists in either direction.

**Measured 2026-08-09:** `python3 tools/check_dispatch.py` → **EXIT 0** — "all 746
chips scanned; 736 supported; 10 confirmed non-dispatchable; 0
non_supported_dispatchable; 0 dispatch regressions; 0 consistency violations".

### Secondary findings from the original report

Not re-audited in this sweep — they were explicitly recorded as non-blockers (WR-03
SRAM 0x28/0x29 dispatch-level VPP assertions, WR-01 `datetime.utcnow()` deprecation,
IN-03 unused `_EVIDENCE_SHA_SOFTWARE_SENTINEL`). They remain outside this status flip.

_Re-verified: 2026-08-09 · v1.31 pre-close carry-over sweep · evidence-based, no code changed_
