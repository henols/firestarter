---
phase: 06-logging-infrastructure
verified: 2026-05-18T13:46:58Z
status: passed
score: 6/6 must-haves verified
overrides_applied: 0
---

# Phase 6: Logging Infrastructure Verification Report

**Phase Goal:** A canonical message catalog plus codegen-produced firmware header + host Python module exist, the firmware `rurp_log_id` send-by-ID helper compiles and links alongside the old log helpers, the host `serial_comm.py` can decode an ID-encoded log frame, and CI fails on any drift between the catalog and the generated artifacts. No existing call-site is converted yet — both old and new paths coexist.

**Verified:** 2026-05-18T13:46:58Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
| - | ----- | ------ | -------- |
| 1 | Canonical catalog file declares every firmware log message as `{id, symbolic_name, format_string, parameter_shape}`; codegen run twice produces byte-identical artifacts (LCAT-01/03/04/05) | VERIFIED | `.planning/catalog/messages.toml` exists with 68 entries each carrying `id`, `name`, `severity`, `format`, `params`, `wire_format`. Ran codegen twice into `/tmp/cgtest/`: cpp, python, and cpp-table outputs are byte-identical per `diff` (`IDEMPOTENT cpp`/`IDEMPOTENT python`/`IDEMPOTENT cpp-table` checks). Generated artifacts also match the committed copies (`firestarter/include/messages.h`, `firestarter/src/messages.c`, `firestarter_app/firestarter/messages.py`) — `diff` exits 0. |
| 2 | Invalid catalog (duplicate ID, duplicate name, malformed shape, empty format) fails codegen with a clear error before any source files are written (LCAT-02) | VERIFIED | Manually constructed four bad catalogs in `/tmp/cgtest/`. Each failed with exit=1 and a descriptive `ERROR: catalog validation failed: ...` line: duplicate ID (`Duplicate ID 0x01: 'MSG_B' conflicts with prior 'MSG_A'`), duplicate name (`Duplicate name 'MSG_A' at ID 0x02`), bad param type (`Invalid param type 'u128' ... Allowed: [...]`), empty format (`Missing or empty 'format' for ID 0x01`). Confirmed `--target` write is blocked: file `/tmp/cgtest/should-not-exist.h` was not created when an invalid catalog was passed with `--target` + `--language`. |
| 3 | `pio run -e leonardo` and `pio run -e uno` both compile cleanly with the new `rurp_log_id` helper available in firmware alongside the existing `rurp_log` family (LFW-01/02, LMIG-01) | VERIFIED | Built both boards in this verification run: Leonardo `SUCCESS Took 0.73 s`, Flash 98.7% (28292/28672, 380 bytes free). Uno `SUCCESS Took 0.58 s`, Flash 80.9% (26100/32256). Header `firestarter/include/rurp_shield.h:132` declares `void rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count)`. Weak default emitter in `rurp_serial_utils.cpp:211`, Uno strong override with `com_mode` gate in `uno_rurp_shield.cpp:107-118`. Old `rurp_log`/`rurp_log_P`/`LOG_*_MSG` PROGMEM strings + `log_info_const`/`log_error_format`/`log_warn` macros still exist in `firestarter/include/logging.h` (lines 25-145) and are referenced by 100+ call-sites (e.g. `operation_utils.cpp:195 log_info_const("Main done")`). |
| 4 | Hand-crafted ID-encoded log frame from a Python test fixture into `serial_comm.py` yields a `LogMessage(severity, text)` whose severity matches the catalog category and whose text renders the params per the catalog format (LHOST-01/02/03) | VERIFIED | `pytest tests/` runs 16/16 passing. `tests/test_decoder.py::test_u24_render_as_hex_addr` feeds `MSG_INFO_ADDR` (0x56) with params `01F4A2`, asserts decoded `Response.type == "INFO"` and `message == "Address: 0x01f4a2"` (hex_addr render of u24). `test_severity_routing_preserves_response_shape` asserts OK/ERROR severity labels propagate as strings. `test_data_progress_u32_pair` asserts DATA severity with two u32 params formats correctly. `test_crc_mismatch_rejected` / `test_unknown_id_rejected` cover negative paths. `test_text_then_binary_in_one_read` proves coexistence of text + binary frames through the same `_read_and_parse_lines` generator. |
| 5 | Both sub-repo CI pipelines run codegen and assert `git diff --exit-code` on the generated files (LCI-01/02/03/04) | VERIFIED | `firestarter/.github/workflows/build.yml` lines 60-73: `Catalog validity check` step runs `codegen.py --check`; `Codegen drift gate` step regenerates `include/messages.h` + `src/messages.c` then `git diff --exit-code`. Phase-6 WR-05 fix confirmed: drift gate is positioned BEFORE the `update_version.py` + `stefanzweifel/git-auto-commit-action` so a failure blocks the auto-commit (lines 44-89). `firestarter_app/.github/workflows/ci.yml` lines 34-49: same pattern for `firestarter/messages.py`. `.github/workflows/catalog-sync-check.yml` lines 42-54: meta-repo cross-sub-repo identity assertion via `cmp` + `diff`. Crucially, `tools/**` is NOT in either sub-repo's `paths-ignore`, so catalog/codegen edits trigger CI. |
| 6 | Host's firmware-version check refuses pre-v1.2 major version with operator-facing "upgrade firmware" message; guard unit-tested (LFW-05/LHOST-04) | VERIFIED | `serial_comm.py:682-692` raises `FirmwareOutdatedError("Firmware version {current_version} is pre-v1.2 ... Please upgrade the firmware to v3.0.0 or later using 'firestarter fw --install'. ...")` when `major < 3` AND `FIRESTARTER_DEV_ALLOW_PRE_V12 != "1"`. `firmware.py:92-93` has the explicit `except FirmwareOutdatedError: raise` clause BEFORE the broad `except (ProgrammerNotFoundError, SerialError)` (per PATTERNS gotcha resolution). `tests/test_fwguard.py` covers all four required cases: `test_refuse_pre_v3_firmware` (v2.0.11 → raises, message contains `2.0.11` + `firestarter fw --install` + `v3.0.0 or later`), `test_accept_v3_firmware` (v3.0.0 → no raise), `test_dev_escape_hatch_env_var` (env=1 → no raise even on v2.x), `test_malformed_version_defaults_to_refuse` (`x.x.x` → major=0 → refuses). |

**Score:** 6/6 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `.planning/catalog/messages.toml` | Canonical 68-entry log catalog (plan said 52, grew to 68 during phase) | VERIFIED | 15529 bytes; 68 `[[messages]]` entries; `[catalog].version = 1`. Schema fields `id`, `name`, `severity`, `format`, `params`, `wire_format` all present. |
| `.planning/catalog/codegen.py` | Deterministic codegen with --check + --language {cpp, cpp-table, python} | VERIFIED | 21603 bytes; 591 lines; 10-rule validator covers all LCAT-02 cases; idempotent (verified empirically by two-pass diff). Stdlib only (tomllib). |
| `.planning/catalog/sync_to_subrepos.sh` | Vendored-copy sync meta → sub-repos with idempotence + identity check | VERIFIED | 2340 bytes; `set -euo pipefail`; runs `cp` + `diff -q` on each file; final cross-sub-repo `cmp messages.toml` invariant assertion. Re-ran during verification: `OK: sub-repo catalogs are byte-identical. OK: catalog synced to both sub-repos.` |
| `firestarter/tools/catalog/{messages.toml,codegen.py}` | Vendored copies byte-identical to meta | VERIFIED | Both files match meta-repo byte-for-byte (`diff` exits 0). |
| `firestarter_app/tools/catalog/{messages.toml,codegen.py}` | Vendored copies byte-identical to meta | VERIFIED | Both files match meta-repo byte-for-byte (`diff` exits 0). |
| `firestarter/include/messages.h` | Generated header: severity defines, MSG_* IDs, `MSG_PARAM_BYTES_TABLE` extern, `MSG_PARAM_COUNT(id)` macro | VERIFIED | 4393 bytes; 68 MSG_* defines, 8 severity defines, extern PROGMEM table declaration, macro present. Header guard `__MESSAGES_H__` with `extern "C"` block. Matches codegen output. |
| `firestarter/src/messages.c` | Generated 256-byte PROGMEM table with designated initializers, 0xFF fill for unallocated IDs | VERIFIED | 7179 bytes; `const uint8_t MSG_PARAM_BYTES_TABLE[256] PROGMEM = { ... };` with `[0x00..0xFF]` designators. Matches codegen output. |
| `firestarter/include/logging_id.h` | `LOG_ID`, `LOG_ID_U8`, `LOG_ID_U16`, `LOG_ID_U24`, `LOG_ID_U32`, `LOG_ID_BYTES`, `LOG_INFO_ID*` macros packing MSB-first | VERIFIED | 5985 bytes; all required macros present (lines 28-119); multi-byte pack uses `>> 24/16/8/0 & 0xFF` MSB-first order. Includes `firestarter.h`, `messages.h`, `rurp_shield.h`. |
| `firestarter/src/boards/rurp_serial_utils.cpp` | `_firestarter_emit_frame`, CRC8_TABLE (256-byte PROGMEM), MAGIC_PREAMBLE, weak `rurp_log_id` | VERIFIED | 8301 bytes; all symbols defined (lines 125-216): MAGIC_PREAMBLE `{0xAA, 0x55, 0xAA, 0x55}`, CRC8 table seeded with poly 0x07, `_firestarter_emit_frame` with wire-frame budget guard (param_count > 253 → silent drop, prevents `len` byte wrap), weak `__attribute__((weak)) rurp_log_id` falls through to emitter. |
| `firestarter/src/boards/uno_rurp_shield.cpp` | Strong Uno override of `rurp_log_id` with `com_mode` gate + SERIAL_DEBUG duplication | VERIFIED | 5839 bytes; lines 102-118: strong (non-weak) `rurp_log_id` definition checks `com_mode` global before delegating to `_firestarter_emit_frame`. Leonardo path is the weak default (no override). |
| `firestarter/include/rurp_shield.h` | `rurp_log_id` declaration alongside `rurp_log`/`rurp_log_P` | VERIFIED | Line 137: `void rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count);`. Lines 132-133 retain `rurp_log` + `rurp_log_P` (LMIG-01 coexistence). |
| `firestarter/test/native/avr/test_messages/{test_rurp_log_id.cpp,host_stubs.cpp,avr/pgmspace.h}` | Native Unity suite asserting wire-frame byte sequence | VERIFIED | All three files exist (8862, 1141 bytes + avr/pgmspace.h). `pio test -e native -f "*test_messages*"` runs 5 cases all PASSED: `test_zero_param_frame`, `test_u32_param_frame`, `test_multi_param_frame`, `test_crc_polynomial_smoke`, `test_oversize_param_count_rejected`. |
| `firestarter_app/firestarter/messages.py` | Generated catalog: SEVERITY_*, MSG_* ID constants, `CATALOG: dict[int, MessageDef]` | VERIFIED | 15817 bytes; `MessageDef` dataclass + `CATALOG` dict + `SEVERITY_LABEL`. Matches codegen output. |
| `firestarter_app/firestarter/serial_comm.py` | `LogMessage` namedtuple, `MAGIC_PREAMBLE`, byte-stream `_read_and_parse_lines`, `_decode_id_frame`, `_decode_param` | VERIFIED | 36023 bytes; `LogMessage = namedtuple('LogMessage', ['severity', 'text', 'id'])` (line 36); `MAGIC_PREAMBLE: bytes = b'\xAA\x55\xAA\x55'` (line 37); `_crc8_ccitt` table-based; `_decode_id_frame` validates CRC + wire_format=text rejection (WR-03 fix line 345) + shape check + format render; `_read_and_parse_lines` byte-stream accumulator (line 391) handles both text 0x0A and 4-byte magic-preamble dispatch. |
| `firestarter_app/firestarter/firmware.py` | Explicit `except FirmwareOutdatedError: raise` before broad handler | VERIFIED | Lines 92-93: `except FirmwareOutdatedError: raise   # Phase 6 (LHOST-04): surface lockstep refuse to operator (do NOT swallow)`. |
| `firestarter_app/pyproject.toml` | `[project.optional-dependencies] dev = ["pytest>=7.0"]` + `[tool.pytest.ini_options]` | VERIFIED | Both sections present (lines 56-60 + 76-79). `testpaths = ["tests"]`, `addopts = "-ra -q"`. |
| `firestarter_app/tests/{__init__.py,conftest.py,test_decoder.py,test_fwguard.py}` | Pytest suite with fake_serial + build_frame fixtures + 16 tests | VERIFIED | All four files exist. `pytest tests/ -v` → 16 passed in 0.25s. test_decoder.py = 284 lines / 12 tests; test_fwguard.py = 125 lines / 4 tests. |
| `firestarter/.github/workflows/build.yml` | Modified: setup-python 3.11 + catalog validity + drift gate before pio | VERIFIED | 3388 bytes; lines 55-73 add setup-python + validity + drift gate; WR-05 ordering correct (gate BEFORE auto-commit); `tools/**` removed from `paths-ignore`. Native unit tests run via `pio test -e native` (line 84). |
| `firestarter_app/.github/workflows/ci.yml` | NEW workflow with codegen + drift + pytest | VERIFIED | 1207 bytes; new file; runs on push/PR to main, no `tools/**` in `paths-ignore`; runs `codegen.py --check`, drift gate on `firestarter/messages.py`, then `pip install -e .[dev]` + `pytest tests/ -v`. |
| `.github/workflows/catalog-sync-check.yml` | NEW meta-repo workflow asserting cross-sub-repo identity | VERIFIED | 1933 bytes; checks out both sub-repos at `main`; `cmp` + `diff` between vendored `messages.toml` copies; also asserts meta vs each sub-repo (`meta/.planning/catalog/messages.toml`). Triggers on `.planning/catalog/**` paths. |
| `.planning/phases/06-logging-infrastructure/06-FLASH-MEASUREMENT.md` | Phase 6 close flash measurement record | VERIFIED | Captures Leonardo 98.7% (380 B free) + Uno 80.9% post-Phase-6-Plan-02. No fall-back triggered (well under cliff). Phase 9 baseline anchor documented. |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `.planning/catalog/codegen.py` | `.planning/catalog/messages.toml` | `tomllib.loads()` | WIRED | Lines 34 (`import tomllib`), 326 (`tomllib.loads(text)`). |
| `.planning/catalog/sync_to_subrepos.sh` | firestarter/tools/catalog + firestarter_app/tools/catalog | `cp` + `diff -q` | WIRED | Lines 35-51 iterate both targets; lines 62-69 cross-sub-repo invariant. Verified by running the script during verification — exit 0. |
| `firestarter/include/messages.h` | `firestarter/src/messages.c` | extern declaration of `MSG_PARAM_BYTES_TABLE` | WIRED | `messages.h:112` declares `extern const uint8_t MSG_PARAM_BYTES_TABLE[256] PROGMEM`; `messages.c:14` provides definition. `pio run` links cleanly on both boards. |
| `firestarter/include/logging_id.h` | `firestarter/include/rurp_shield.h` | calls `rurp_log_id()` | WIRED | All LOG_ID* macros expand to `rurp_log_id(...)`; declared in `rurp_shield.h:132`. |
| `firestarter/src/boards/uno_rurp_shield.cpp` | `firestarter/src/boards/rurp_serial_utils.cpp` | calls `_firestarter_emit_frame` | WIRED | `uno_rurp_shield.cpp:110` calls `_firestarter_emit_frame(...)`; defined at `rurp_serial_utils.cpp:153`. Linker resolves Uno's strong override over the weak default at `rurp_serial_utils.cpp:211`. |
| `firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp` | `firestarter/src/boards/rurp_serial_utils.cpp` | `src_filter += <boards/rurp_serial_utils.cpp>` | WIRED | `pio test -e native -f "*test_messages*"` builds + runs 5 tests all PASSED. |
| `firestarter_app/firestarter/serial_comm.py` | `firestarter_app/firestarter/messages.py` | `from firestarter.messages import CATALOG, SEVERITY_LABEL` | WIRED | Line 26: explicit import; line 331 looks up `CATALOG.get(msg_id)`; line 388 maps via `SEVERITY_LABEL`. |
| `firestarter_app/tests/test_decoder.py` | `firestarter_app/firestarter/serial_comm.py` | imports `LogMessage`, `MAGIC_PREAMBLE`, `Response` | WIRED | Lines 28-39 import from `firestarter.messages` + `firestarter.serial_comm`. Conftest's `build_frame` constructs binary frames; tests drive them through the actual decoder. 12 tests pass. |
| `firestarter_app/firestarter/firmware.py` | `firestarter_app/firestarter/serial_comm.py` | imports `FirmwareOutdatedError`; explicit re-raise | WIRED | `firmware.py:24` imports `FirmwareOutdatedError`; line 92-93 re-raises before broad handler. test_fwguard.py drives this code path via `unittest.mock.patch.object(SerialCommunicator, ...)`. |
| `firestarter/.github/workflows/build.yml` | `firestarter/tools/catalog/codegen.py` | `python3 tools/catalog/codegen.py` | WIRED | Lines 61, 65-67, 69-71 invoke codegen; drift gate at line 73 uses `git diff --exit-code`. |
| `firestarter_app/.github/workflows/ci.yml` | `firestarter_app/tools/catalog/codegen.py` | `python3 tools/catalog/codegen.py --language python` | WIRED | Lines 35, 38-42 invoke codegen; drift gate at line 43. |
| `.github/workflows/catalog-sync-check.yml` | both sub-repos' `tools/catalog/messages.toml` | `cmp` + `diff` byte-identical assertion | WIRED | Lines 28-40 check out both sub-repos; lines 42-54 `cmp` cross-sub-repo + meta-vs-each. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `serial_comm.py::_decode_id_frame` | `entry` (catalog lookup) | `CATALOG.get(msg_id)` from `messages.py` | Yes — CATALOG dict has 68 real entries (verified by running pytest decoder tests which assert format strings + severity labels match catalog) | FLOWING |
| `messages.py::CATALOG` | dict[int, MessageDef] | Generated by codegen from `messages.toml` | Yes — 68 entries deterministically emitted; verified `len(CATALOG)` via decoder tests that look up MSG_INFO_ADDR, MSG_OK_READY, MSG_ERR_WRITE_FAILED, MSG_DATA_PROGRESS | FLOWING |
| `messages.h::MSG_PARAM_BYTES_TABLE` | 256-byte PROGMEM table | Generated by codegen from `messages.toml` | Yes — table populated with byte counts at each allocated ID; 0xFF for variable/unallocated. Read at runtime via `pgm_read_byte` macro. `pio run` links and binary fits in flash budget. | FLOWING |
| `_firestarter_emit_frame` | wire bytes | `MAGIC_PREAMBLE`, `CRC8_TABLE`, caller params | Yes — Unity test `test_u32_param_frame` (and 4 others) assert exact byte sequences emitted: magic preamble, length, id, params, CRC, terminator. | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Codegen idempotence (LCAT-05) | Run codegen twice (cpp + python + cpp-table) and diff outputs | All three pairs byte-identical | PASS |
| Catalog validity rejects duplicate ID | `python3 codegen.py --catalog bad-dup-id.toml --check` | exit=1, clear `Duplicate ID 0x01: 'MSG_B' conflicts with prior 'MSG_A'` | PASS |
| Catalog validity rejects duplicate name | `python3 codegen.py --catalog bad-dup-name.toml --check` | exit=1, clear `Duplicate name 'MSG_A' at ID 0x02` | PASS |
| Catalog validity rejects malformed param shape | `python3 codegen.py --catalog bad-shape.toml --check` | exit=1, `Invalid param type 'u128' ... Allowed: [...]` | PASS |
| Catalog validity rejects empty format | `python3 codegen.py --catalog bad-empty-format.toml --check` | exit=1, `Missing or empty 'format'` | PASS |
| Codegen blocks file write on invalid catalog | `python3 codegen.py --catalog bad-dup-id.toml --target should-not-exist.h --language cpp` | exit=1; target file NOT created | PASS |
| Sub-repos byte-identical to meta-repo (LCI-02 supplementary) | `diff` between meta + each sub-repo's `messages.toml` and `codegen.py` | All 4 diffs exit 0 | PASS |
| Committed generated artifacts match codegen output (drift gate dry-run) | `diff` codegen-output vs committed `messages.h` + `messages.c` + `messages.py` | All 3 exit 0 | PASS |
| Leonardo firmware builds (SC#3) | `pio run -e leonardo` | SUCCESS; Flash 98.7% (380 B free) | PASS |
| Uno firmware builds (SC#3) | `pio run -e uno` | SUCCESS; Flash 80.9% | PASS |
| Native unit tests pass (test_messages) | `pio test -e native -f "*test_messages*"` | 5/5 PASSED in 0.52s | PASS |
| Host pytest suite passes | `cd firestarter_app && python -m pytest tests/ -v` | 16/16 passed in 0.25s | PASS |
| `sync_to_subrepos.sh` idempotent | Re-ran during verification | `OK: catalog synced to both sub-repos.` exit 0 | PASS |

### Probe Execution

No probes declared for Phase 6 (no `scripts/*/tests/probe-*.sh` referenced in PLANs or SUMMARYs; phase is infrastructure-only, behavioral checks above stand in).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| LCAT-01 | 06-01 | Single canonical catalog file declares every message as `{id, symbolic_name, format_string, parameter_shape}` | SATISFIED | `.planning/catalog/messages.toml` is the source of truth (68 entries with required fields); sub-repos consume vendored copies. |
| LCAT-02 | 06-01 | Catalog validation enforces unique IDs, unique names, well-formed param shapes, non-empty format; fails build on violation | SATISFIED | 10-rule validator in `codegen.py:154-304`; behavioral spot-checks above prove rejection paths fire with exit=1. Also enforced in CI via `--check` step. |
| LCAT-03 | 06-01 | Codegen produces C++ header with enum + symbolic name constants + `MSG_PARAM_COUNT(id)` helper | SATISFIED | `messages.h` carries 68 MSG_* `#define`s, severity defines, and `MSG_PARAM_COUNT(id)` macro (line 114). |
| LCAT-04 | 06-01 | Same codegen produces Python module with ID → format-string + param-shape lookup | SATISFIED | `messages.py` carries `MessageDef` + `CATALOG` dict (68 entries) + `SEVERITY_LABEL`. |
| LCAT-05 | 06-01 | Codegen byte-identical across runs (no timestamps, ordering instability, unstable hashes) | SATISFIED | Verified empirically: two-pass `diff` exits 0 for cpp/python/cpp-table outputs. Codegen sorts by id ascending; no timestamps in banner; LF newlines. |
| LFW-01 | 06-02 | `rurp_log_id(uint8_t, const uint8_t*, uint8_t)` helper sends wire frame distinguishable from `DATA:` | SATISFIED | Declared in `rurp_shield.h:132`; weak default at `rurp_serial_utils.cpp:211`; strong Uno override at `uno_rurp_shield.cpp:107`. Wire frame begins with 4-byte 0xAA55AA55 magic preamble, statistically distinct from `DATA:` ASCII prefix. |
| LFW-02 | 06-02 | Convenience macros so `LOG_INFO_ID(MSG_*)` is no more verbose than `log_info_const` | SATISFIED | `logging_id.h` provides `LOG_ID`, `LOG_ID_U8/U16/U24/U32`, `LOG_ID_BYTES`, `LOG_INFO_ID*` (FLAG_VERBOSE-gated). Each macro expands to one `rurp_log_id` call. |
| LFW-05 | 06-04 | Firmware version handshake bumps major; `OK: FW: ...` text-formatted | SATISFIED (host-side guard) | Host refuses pre-major-3 firmware. Catalog entry `MSG_OK_FW_VERSION` (0x03) has `wire_format = "text"` so it stays text-formatted on the wire. Firmware-side actual version bump deferred to Phase 9; host guard is in place and unit-tested NOW (per ROADMAP SC#6 wording "even though no firmware has bumped its version yet"). |
| LHOST-01 | 06-03 | `serial_comm.py` parses ID-encoded log frames using `messages.py` catalog | SATISFIED | `_read_and_parse_lines` byte-stream accumulator (line 391) + `_decode_id_frame` (line 299) implement the parse path; verified by 12 pytest cases in `test_decoder.py`. |
| LHOST-02 | 06-03 | Formatter renders params per declared types (u16 dec, u24 as `0x%06X`, ...) | SATISFIED | `_decode_param` (line 70) decodes all 8 types MSB-first; `entry.format % tuple(values)` renders. `test_u24_render_as_hex_addr` proves u24 → `0x01f4a2` (hex_addr render). |
| LHOST-03 | 06-03 | Existing severity routing preserved; `Response(type=severity, message=text)` | SATISFIED | `_decode_id_frame` returns `LogMessage(severity=SEVERITY_LABEL[entry.severity], ...)`; `_read_and_parse_lines` yields `Response(type=severity_label, message=text)`. `test_severity_routing_preserves_response_shape` asserts OK/ERROR labels propagate. |
| LHOST-04 | 06-04 | Host fw-version check refuses pre-v1.2 (major<3) with operator-facing message; no text-protocol fallback | SATISFIED | `serial_comm.py:682-692` raises `FirmwareOutdatedError`; `firmware.py:92-93` re-raises explicitly. Message says `"firmware version {x} is pre-v1.2 ... upgrade ... to v3.0.0 or later using 'firestarter fw --install'. (No fallback ...)"`. 4 unit tests cover all paths. |
| LCI-01 | 06-05 | Firmware CI step regenerates `messages.h` + asserts no diff | SATISFIED | `firestarter/.github/workflows/build.yml:63-73` regenerates both `include/messages.h` and `src/messages.c` then `git diff --exit-code`. Drift fails CI. |
| LCI-02 | 06-05 | Host CI step regenerates `messages.py` + asserts no diff | SATISFIED | `firestarter_app/.github/workflows/ci.yml:37-43` regenerates `firestarter/messages.py` then `git diff --exit-code`. Additional cross-sub-repo workflow at `.github/workflows/catalog-sync-check.yml` adds end-to-end identity assertion. |
| LCI-03 | 06-05 | Both sub-repo builds run codegen before compile/test | SATISFIED | Firmware: codegen drift gate runs BEFORE `Install PlatformIO` + `pio test` + `pio run` (build.yml lines 55-98). Host: codegen runs BEFORE `pip install -e .[dev]` + `pytest` (ci.yml lines 29-49). `tools/**` dropped from `paths-ignore` in both sub-repos so catalog edits trigger CI. |
| LCI-04 | 06-05 | Catalog validity (LCAT-02) checked as part of codegen and CI | SATISFIED | Both CI files run `codegen.py --check` BEFORE the drift gate. Validation also runs unconditionally during emission so invalid catalog produces no file. |
| LMIG-01 | 06-05 (cross-cutting) | Phase A infrastructure-only: catalog + codegen + helper + decoder + drift gates land WITHOUT removing existing log code | SATISFIED | Verified by inspection: `firestarter/include/logging.h` retains `LOG_INFO_MSG`/`LOG_ERROR_MSG`/`LOG_WARN_MSG`/`LOG_OK_MSG`/`LOG_DATA_MSG`/`LOG_MAIN_DONE_MSG`/`LOG_INIT_DONE_MSG`/`LOG_END_DONE_MSG` PROGMEM strings (lines 25-31) and `log_info_const` (45), `log_warn` (66), `log_warn_const` (69), `log_warn_format` (72), `log_error_const` (80), `log_error_format` (85), `log_ok_const` (145) macros are all present. 100+ existing call-sites still compile (e.g. `operation_utils.cpp:195` uses `log_info_const`). Both Leonardo and Uno link the union of old + new paths. Old `rurp_log`/`rurp_log_P` retained at `rurp_shield.h:127-128`. |

All 17 requirement IDs declared in PLAN frontmatter are accounted for.

REQUIREMENTS.md additionally claims (table lines 82-100) Phase 6 satisfies LCAT-01..05, LFW-01, LFW-02, LFW-05, LHOST-01..04, LCI-01..04, LMIG-01 — exactly the 17 IDs above. No orphaned requirements expected for Phase 6 in REQUIREMENTS.md that aren't claimed by a plan.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |

(None.) Phase-6 modified files were scanned for unreferenced TBD/FIXME/XXX debt markers — zero matches across all 18 files inspected. The few `// log_*_const(...)` commented-out lines (e.g. `operation_utils.cpp:87, 139, 146` and `rurp_serial_utils.cpp:69, 81, 93`) predate Phase 6 (they exist on the legacy text path and are not Phase-6 introductions). REVIEW.md classifies the phase as `critical: 0, warning: 6 (all fixed in commits db495bd / c498eed / 2d5e744 / 5bb3657 / 61ceeee / 0182419), info: 7 (advisory)`.

### Human Verification Required

None. All six success criteria are verifiable programmatically (idempotence, validation, build success, decoder unit tests, CI workflow contents, fwguard unit tests).

### Gaps Summary

No gaps. All six ROADMAP success criteria for Phase 6 are independently verified in the codebase:

1. Canonical catalog + deterministic codegen → confirmed by two-pass diff and committed-artifacts diff.
2. Catalog validation rejects all four classes of invalid input → confirmed by behavioral spot-checks producing exit=1 with descriptive errors and no file written.
3. Both Leonardo and Uno compile cleanly with `rurp_log_id` available alongside the old `rurp_log` family → confirmed by `pio run` SUCCESS on both, and source inspection showing both code paths intact (LMIG-01).
4. Hand-crafted ID-encoded frame yields correct `LogMessage(severity, text)` with catalog-driven format render → confirmed by 12 passing decoder unit tests including u24 hex_addr render, multi-param frames, CRC + unknown-ID rejection, and text/binary coexistence.
5. Both sub-repo CI pipelines run codegen + drift gate, plus a meta-repo cross-sub-repo identity assertion → confirmed by workflow file inspection. `tools/**` is correctly dropped from `paths-ignore` so catalog edits trigger CI; firmware ordering puts drift gate BEFORE the auto-commit (WR-05 fix).
6. Host fw-version refuse guard for pre-major-3 firmware with explicit re-raise and developer escape-hatch env var → confirmed by 4 passing unit tests covering refuse/accept/escape-hatch/malformed cases.

Phase 6 goal achieved. Phase 7 (LMIG-02 — convert ERROR + WARN + INFO call-sites) can proceed.

---

_Verified: 2026-05-18T13:46:58Z_
_Verifier: Claude (gsd-verifier)_
