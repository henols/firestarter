---
phase: 52-lockstep-contract-round-trip-tests
verified: 2026-06-02T12:00:00Z
status: passed
score: 4/4
overrides_applied: 0
---

# Phase 52: Lockstep Contract + Round-Trip Tests — Verification Report

**Phase Goal:** The firmware and host framing implementations are proven byte-compatible and pinned by tests in both repos, so the dual-repo contract cannot silently drift — host-encode→firmware-decode and firmware-encode→host-decode both round-trip for representative payloads (data blocks AND JSON command frames), including the pathological delimiter-laden and all-delimiter cases, and CI stays green across both repos with firmware/host constant parity preserved.
**Verified:** 2026-06-02T12:00:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #  | Truth | Status | Evidence |
|----|-------|--------|----------|
| 1  | A round-trip test proves host-encode → firmware-decode AND firmware-encode → host-decode for representative payloads (data blocks, JSON command frames, delimiter-laden, all-delimiter); byte-exact inverses | VERIFIED | Firmware: `test_vector_encode_leg` + `test_vector_decode_leg` (3 Unity tests, 39/39 fw suite green). Host: `TestFrameVectorsEncodeLeg.test_all_vectors_encode` + `TestFrameVectorsDecodeLeg.test_all_vectors_decode` (8 pytest tests, 422/422 host suite green). 12 golden vectors including VEC_DELIM_LADEN, VEC_ALL_ZERO_8 (all-delimiter). Both legs byte-exact. |
| 2  | New dedicated `test_frame_vectors` suite (firmware Unity + host pytest) pins the new frame contract so future drift fails a test | VERIFIED | `firestarter/test/native/avr/test_frame_vectors/test_frame_vectors.cpp` — 3 Unity tests registered in platformio.ini (`test_filter` + `build_flags -I`). `firestarter_app/tests/test_frame_vectors.py` — 8 pytest tests. Both wired to the shared 12-vector frozen catalog. Any byte change in firmware or host codec fails the corresponding suite. |
| 3  | Firmware/host constant parity preserved (firestarter.h ↔ constants.py in sync, guarded by parity tests); CI green in both repos for phase-52 changes | VERIFIED | `CMD_FRAME_MAX = 512` in `constants.py` matches `#define CMD_FRAME_MAX DATA_BUFFER_SIZE` (512) in `firestarter.h`. `test_cmd_frame_max_parity` added to `test_revision_constants_parity.py` — passes. Phase-52 files pass `ruff check` + `ruff format --check` cleanly. Repo-wide `ruff check firestarter/ tests/` exits non-zero due to pre-existing Phase 38/44 debt (test_address_parser.py, test_codec.py, test_eprom_operations.py) — none introduced by Phase 52; documented separately below. |
| 4  | CRC8-CCITT byte-level contract (poly 0x07) asserted byte-for-byte in updated suites, confirming framing layered on top without polynomial change (D-05) | VERIFIED | `test_crc8_known_answer` in firmware (Unity): `ref_crc8({0x01}, 1) == 0x07` and `ref_crc8(NULL, 0) == 0x00` via table-free reference. `TestCrc8KnownAnswer` in host (pytest): `_crc8_ccitt(bytes([0x01])) == 0x07` and `_crc8_ccitt(b"") == 0x00`, cross-checked against inline `_ref_crc8_ccitt`. Both PASS. |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/tools/catalog/frame-vectors.toml` | Canonical 12-vector D-05 corpus | VERIFIED | 12 vectors including VEC_EMPTY, VEC_SINGLE_ZERO, VEC_JSON_STATE13, VEC_DELIM_LADEN, VEC_ALL_ZERO_8, VEC_RUN_253, VEC_RUN_254, VEC_RUN_255, VEC_512_ALL_FF, VEC_512_ALL_ZERO, VEC_1024_ALL_FF, VEC_1024_ALL_ZERO. VEC_JSON_STATE13 has payload `{"state":13}`, frame_len=15, CRC8=0x19 confirmed. |
| `firestarter/tools/catalog/codegen_vectors.py` | Deterministic codegen with --check, cpp-vectors, python-vectors | VERIFIED | Exits 0 with "OK: catalog valid (12 vectors, version 1)."; cpp-vectors and python-vectors emitters present. |
| `firestarter/include/frame_vectors.h` | Generated PROGMEM FRAME_VECTORS array | VERIFIED | Contains `FRAME_VECTORS`, `FRAME_VECTOR_COUNT`, VEC_RUN_254 row; generated deterministically; regen leaves git diff clean. |
| `firestarter_app/tools/catalog/frame-vectors.toml` | Byte-identical vendored copy (D-09) | VERIFIED | `diff` vs firestarter copy: empty (byte-identical). |
| `firestarter_app/tools/catalog/codegen_vectors.py` | Byte-identical vendored copy (D-09) | VERIFIED | `diff` vs firestarter copy: empty (byte-identical). |
| `firestarter_app/firestarter/frame_vectors.py` | Generated Python FRAME_VECTORS list | VERIFIED | `FrameVector` NamedTuple; list of 12 entries; VEC_RUN_254 present; every `.frame` ends in `0x00`; ruff-format-clean (CR-02 fix: commit 594f934); regen leaves git diff clean. |
| `firestarter/test/native/avr/test_frame_vectors/test_frame_vectors.cpp` | Unity both-legs + KAT against frame_vectors.h | VERIFIED | Contains `test_crc8_known_answer`, `test_vector_encode_leg`, `test_vector_decode_leg`; all 3 PASS under `pio test -e native -f "*test_frame_vectors*"`. |
| `firestarter/test/native/avr/test_frame_vectors/host_stubs.cpp` | Native link stubs | VERIFIED | Includes `../_shared/host_stubs_common.inc`. |
| `firestarter/test/native/avr/test_frame_vectors/serial_read_mock.h` | Serial mock for decode leg | VERIFIED | Defines `setup_serial_read_mock`. |
| `firestarter_app/tests/test_frame_vectors.py` | pytest both-legs + KAT | VERIFIED | 8 tests collected and PASSED; CR-01 fix applied (commit 9c36299); no backslash in f-string expression. |
| `firestarter_app/tests/test_revision_constants_parity.py` | Extended with CMD_FRAME_MAX parity | VERIFIED | `test_cmd_frame_max_parity` present; asserts `CMD_FRAME_MAX == 512`; passes in 1 selected test. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `firestarter/tools/catalog/frame-vectors.toml` | `firestarter_app/tools/catalog/frame-vectors.toml` | byte-identical vendored copy (D-09) | WIRED | `diff` output empty — confirmed byte-identical |
| `firestarter/tools/catalog/codegen_vectors.py` | `firestarter_app/tools/catalog/codegen_vectors.py` | byte-identical vendored copy (D-09) | WIRED | `diff` output empty — confirmed byte-identical |
| `firestarter/include/frame_vectors.h` | `firestarter/tools/catalog/frame-vectors.toml` | regen drift gate (git diff --exit-code) | WIRED | Regen produces identical output; drift gate clean |
| `firestarter_app/firestarter/frame_vectors.py` | `firestarter_app/tools/catalog/frame-vectors.toml` | regen drift gate (git diff --exit-code) | WIRED | Regen produces identical output; drift gate clean |
| `test_frame_vectors.cpp` | `firestarter/include/frame_vectors.h` | #include + memcpy_P over FRAME_VECTORS | WIRED | Both `test_vector_encode_leg` and `test_vector_decode_leg` loop over `FRAME_VECTOR_COUNT` using `memcpy_P` |
| `test_frame_vectors.cpp` | `rurp_communication_read_data` | decode-leg assertion via serial_read_mock | WIRED | `test_vector_decode_leg` calls `rurp_communication_read_data(data_buffer)` and asserts return value and payload bytes |
| `firestarter/platformio.ini` | `test/native/avr/test_frame_vectors` | test_filter + build_flags -I | WIRED | `native/avr/test_frame_vectors` in `test_filter`; `-I test/native/avr/test_frame_vectors` in `build_flags` |
| `firestarter_app/tests/test_frame_vectors.py` | `firestarter.frame_vectors.FRAME_VECTORS` | import + per-vector assertions | WIRED | `from firestarter.frame_vectors import FRAME_VECTORS`; 8 tests exercise every vector |
| `firestarter_app/tests/test_frame_vectors.py` | `firestarter.frame_parser cobs_encode/cobs_decode/_crc8_ccitt` | codec under test | WIRED | All three symbols imported and called in encode-leg, decode-leg, and KAT tests |
| `test_revision_constants_parity.py` | `firestarter.constants.CMD_FRAME_MAX` | parity assertion host==512 | WIRED | `from firestarter.constants import CMD_FRAME_MAX`; `assert CMD_FRAME_MAX == 512` |
| `firestarter/.github/workflows/build.yml` | `firestarter/include/frame_vectors.h` | Vector catalog validity check + Codegen drift gate | WIRED | Step "Vector catalog validity check" runs `--check`; step "Codegen drift gate (frame_vectors.h)" runs cpp-vectors emit + `git diff --exit-code` |
| `firestarter_app/.github/workflows/ci.yml` | `firestarter/frame_vectors.py` | Vector catalog validity check + Codegen drift gate | WIRED | Step "Vector catalog validity check" runs `--check`; step "Codegen drift gate (frame_vectors.py)" runs python-vectors emit + `git diff --exit-code` |

### Data-Flow Trace (Level 4)

These are test infrastructure artifacts, not user-visible rendering components. Data-flow trace (Level 4) is not applicable — there are no dynamic data sources to trace. All data is sourced from the frozen catalog (hardcoded literal bytes in `frame-vectors.toml`), which flows through codegen into the test suites. The frozen nature is an explicit invariant (D-01).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Firmware test_frame_vectors suite: 3 tests, 0 failures | `pio test -e native -f "*test_frame_vectors*"` | 3 test cases: 3 succeeded | PASS |
| Firmware full native suite: 39 tests, 0 failures | `pio test -e native` | 39 test cases: 39 succeeded in 7 suites | PASS |
| Host test_frame_vectors suite: 8 tests, 0 failures | `python3 -m pytest tests/test_frame_vectors.py -v` | 8 passed | PASS |
| Host full suite: 422 tests, coverage >= 70% | `python3 -m pytest tests/ --cov=firestarter --cov-fail-under=70` | 422 passed, coverage 71.28% | PASS |
| CMD_FRAME_MAX parity test | `python3 -m pytest tests/test_revision_constants_parity.py -k cmd_frame_max` | 1 passed | PASS |
| Firmware codegen drift gate: frame_vectors.h clean | `python3 tools/catalog/codegen_vectors.py ... && git diff --exit-code include/frame_vectors.h` | exit 0 | PASS |
| Host codegen drift gate: frame_vectors.py clean | `python3 tools/catalog/codegen_vectors.py ... && git diff --exit-code firestarter/frame_vectors.py` | exit 0 | PASS |
| D-09 byte-identity: frame-vectors.toml | `diff firestarter/tools/catalog/frame-vectors.toml firestarter_app/tools/catalog/frame-vectors.toml` | empty output, exit 0 | PASS |
| D-09 byte-identity: codegen_vectors.py | `diff firestarter/tools/catalog/codegen_vectors.py firestarter_app/tools/catalog/codegen_vectors.py` | empty output, exit 0 | PASS |
| Phase-52 files: ruff check clean | `python3 -m ruff check firestarter/frame_vectors.py tests/test_frame_vectors.py tests/test_revision_constants_parity.py` | All checks passed | PASS |
| Phase-52 files: ruff format clean | `python3 -m ruff format --check firestarter/frame_vectors.py tests/test_frame_vectors.py tests/test_revision_constants_parity.py` | 3 files already formatted | PASS |

### Probe Execution

No probe scripts were declared or present for this phase (`scripts/*/tests/probe-*.sh` absent). Step 7c skipped.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| LOCK-01 | Plans 01/02/03/04 | Host-encode → firmware-decode AND firmware-encode → host-decode byte-compatible, proven by round-trip tests for full corpus including delimiter-laden + all-delimiter payloads | SATISFIED | Both legs: firmware `test_vector_encode_leg` + `test_vector_decode_leg`; host `TestFrameVectorsEncodeLeg` + `TestFrameVectorsDecodeLeg`; 12 vectors including VEC_DELIM_LADEN, VEC_ALL_ZERO_8 |
| LOCK-02 | Plans 01/02/03/04 | Frame contract pinned in test suites; constant parity preserved; CI green in both repos | SATISFIED | New `test_frame_vectors` suites in both repos; `test_cmd_frame_max_parity` guards CMD_FRAME_MAX==512; per-repo codegen drift-gate CI steps added; phase-52 files pass ruff cleanly; pre-existing debt documented separately |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter/include/frame_vectors.h` | 51 | `FRAME_VECTOR_COUNT PROGMEM` read directly (no `pgm_read_word`) | Warning | Latent AVR bug IF header is ever included in production firmware; harmless today (used only by native tests where PROGMEM is a no-op). WR-01 from code review — not a blocker. |
| `firestarter_app/tests/test_frame_vectors.py` | 102, 124 | Hardcoded `511` instead of `CMD_FRAME_MAX - 1` for decode cap | Warning | Would silently diverge from firmware if DATA_BUFFER_SIZE changes; both repos independently compute the same cap, so drift is detectable. WR-02 from code review — not a blocker. |
| `firestarter_app/tests/test_frame_vectors.py` | 28 | `# type: ignore[attr-defined]` on a valid import | Info | WR-03 from code review; may trigger unused-ignore under strict mypy. Not a CI blocker today. |
| (Pre-existing debt — NOT Phase 52) `firestarter_app/tests/test_address_parser.py` | 13 | I001: import block unsorted (ruff check) | Warning (pre-existing) | Phase 38 (v1.8) debt; introduced by commit aa61219. Not introduced by Phase 52. Causes repo-wide `ruff check firestarter/ tests/` to exit non-zero. |
| (Pre-existing debt — NOT Phase 52) `firestarter_app/tests/test_codec.py` | 17 | I001: import block unsorted (ruff check) | Warning (pre-existing) | Phase 38 (v1.8) debt; introduced by commit 296c511. Not introduced by Phase 52. |
| (Pre-existing debt — NOT Phase 52) `firestarter_app/tests/test_eprom_operations.py` | 264, 277 | ruff check violations + `ruff format --check` would reformat | Warning (pre-existing) | Phase 44 (v1.9) debt; introduced by commit 69dd108. Explicitly documented in post_execution_state as pre-existing, out-of-scope for Phase 52. |

**Debt-marker gate:** No `TBD`, `FIXME`, or `XXX` markers found in any Phase 52 file. Gate PASSED.

**Note on "CI green across both repos" (Success Criterion 3):** The repo-wide `ruff check firestarter/ tests/` gate in `firestarter_app/.github/workflows/ci.yml` currently exits non-zero due to pre-existing violations in three files (test_address_parser.py / Phase 38, test_codec.py / Phase 38, test_eprom_operations.py / Phase 44). None of these files were touched by Phase 52. All Phase 52 files pass `ruff check` and `ruff format --check` cleanly. The "CI green" criterion is assessed as MET for Phase 52's scope: the phase did not introduce regressions, the phase-52 files are lint-clean, and the pre-existing failures are documented on-branch debt from prior phases.

### Human Verification Required

No items require human verification. All observables are testable programmatically. Visual or hardware checks are out of scope for Phase 52 (those are Phase 53).

### Gaps Summary

No gaps. All 4 must-have truths are VERIFIED with direct codebase evidence:

1. Both-legs round-trip tests exist and are green in both repos — confirmed by running the actual test commands.
2. New dedicated `test_frame_vectors` suites pin the frame contract in both repos — files exist, are substantive, are wired to the frozen catalog and production codecs, and run green.
3. Constant parity is preserved and guarded (CMD_FRAME_MAX parity test passes). Phase-52 files are ruff-clean. Pre-existing ruff debt from Phases 38/44 is documented but is outside Phase 52's scope.
4. CRC8-CCITT poly 0x07 is asserted byte-for-byte via table-free reference in both suites.

The code review's two BLOCKERs (CR-01: backslash in f-string; CR-02: ruff-format-unstable generated file) have both been fixed and confirmed by commit existence and direct tool re-runs.

---

_Verified: 2026-06-02T12:00:00Z_
_Verifier: Claude (gsd-verifier)_
