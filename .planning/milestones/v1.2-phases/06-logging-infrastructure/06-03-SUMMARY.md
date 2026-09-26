---
phase: 06-logging-infrastructure
plan: 03
subsystem: host

tags: [host, decoder, pytest, byte-stream, wire-protocol, crc8, lhost, lmig-coexistence]

# Dependency graph
requires:
  - 06-01 (catalog + codegen produced firestarter_app/firestarter/messages.py with CATALOG + MessageDef + SEVERITY_LABEL)
  - 06-02 (firmware emitter pinned the wire frame: AA-55 magic + len-authoritative body + CRC8 poly 0x07 + 0x0A anchor)
provides:
  - first-ever pytest infrastructure in firestarter_app/ (pyproject [tool.pytest.ini_options] + [project.optional-dependencies] dev = ["pytest>=7.0"])
  - tests/__init__.py + tests/conftest.py shared fixtures (MAGIC_PREAMBLE_REF, _ref_crc8_ccitt [table-FREE], build_frame, fake_serial, make_comm)
  - LogMessage namedtuple + MAGIC_PREAMBLE constant at firestarter.serial_comm module level
  - module-level _CRC8_CCITT_TABLE (256-byte precomputed at import) + _crc8_ccitt + _decode_param helpers
  - SerialCommunicator._decode_id_frame instance method (CRC validation, catalog lookup, MSB-first param decode, printf-style render, structured logger.warning on every failure mode)
  - rewritten SerialCommunicator._read_and_parse_lines — always-on byte-stream reader (D-05) that dispatches BOTH text-lines AND binary frames through the same Response yield surface
  - tests/test_decoder.py — 10 passing acceptance tests covering LHOST-01/02/03 + LMIG-01
affects: [06-04-fw-guard, 06-05-ci-drift-gate, 07-call-site-conversion, 08-call-site-conversion]

# Tech tracking
tech-stack:
  added:
    - pytest>=7.0 (dev optional-dependency)
  patterns:
    - "Always-on byte-stream reader with magic-scan unified text+binary dispatch (CONTEXT §D-05)"
    - "Table-driven CRC8 production path + table-FREE reference in tests (regression catches table drift)"
    - "BytesIO fake-serial fixture + __new__-bypass factory for SerialCommunicator (no real port needed)"
    - "Shape-then-decode-then-render error hierarchy — each failure mode logs a structured warning and returns None so the read loop continues (T-06-12 DoS resilience)"

key-files:
  created:
    - firestarter_app/tests/__init__.py
    - firestarter_app/tests/conftest.py
    - firestarter_app/tests/test_decoder.py
  modified:
    - firestarter_app/pyproject.toml (urls relocated above [project.optional-dependencies]; new dev extra + [tool.pytest.ini_options])
    - firestarter_app/firestarter/serial_comm.py (LogMessage + MAGIC_PREAMBLE + CRC8 table + _decode_param + _decode_id_frame + rewritten _read_and_parse_lines)

key-decisions:
  - "ascii_str parameter decode uses errors='replace' (not 'strict') so a tampered/truncated string surfaces visibly rather than crashing the read loop. Matches catalog grammar tolerance."
  - "Frame body shape check uses entry.param_bytes >= 0 (skip when -1 / variable-length). Variable-length ascii_str entries fall back to _decode_param's IndexError handling for overrun protection."
  - "_decode_id_frame catches the union (IndexError, struct.error, ValueError) during per-param decode. struct.error is the under-buffer surface for u16/i16/u32/i32; IndexError is the over-cursor surface for u8/i8/u24/ascii_str-length-byte."
  - "Format-render error path: logs warning + sets text = f'<format-error: {entry.name}>'. The Response still yields so the read loop progresses; downstream consumers see a tagged placeholder, not a silent drop."
  - "Test fixture make_comm uses SerialCommunicator.__new__ to bypass __init__ entirely (no serial.Serial constructor invocation, no CONNECTION_STABILIZE_DELAY sleep). Per the plan's PATTERNS reference."
  - "Reference CRC in conftest.py is table-FREE (independent of the production lookup table). A regression that mutates _CRC8_CCITT_TABLE off-spec mismatches the reference and fails the suite."

patterns-established:
  - "Byte-stream reader unifies legacy text + new binary frame dispatch through one generator — no caller branching"
  - "Each decoder failure mode (frame too short, CRC mismatch, unknown ID, shape mismatch, decode error, format error) logs a uniquely-tagged warning containing the offending message ID in hex; outer read loop continues unconditionally"
  - "BytesIO + __new__-bypass = zero-hardware-dependency host-side regression harness"

requirements-completed: [LHOST-01, LHOST-02, LHOST-03]

# Metrics
duration: ~5 min
completed: 2026-05-18
---

# Phase 6 Plan 03: Host Byte-Stream Decoder + pytest Bootstrap Summary

**First-ever pytest infrastructure landed in `firestarter_app/`. `serial_comm.py._read_and_parse_lines` rewritten as an always-on byte-stream reader (D-05) that dispatches text lines and binary ID-frames through the same `Response` yield surface; `_decode_id_frame` validates CRC8 over `[id, params]`, looks up the catalog entry, decodes MSB-first params per the catalog grammar, and renders via the printf format. 10 acceptance tests pass — LHOST-01/02/03 + LMIG-01 all covered with hand-crafted frames over a BytesIO fake serial port. `_log_rurp_feedback` body byte-identical to pre-plan baseline — LHOST-03 routing surface preserved.**

## Performance

- **Duration:** ~5 min (start `2026-05-18T11:57:52Z`, end `2026-05-18T12:02:44Z`)
- **Tasks:** 3/3 complete (all atomic submodule + meta-repo-pointer-bump pairs)
- **Files created:** 3 (tests/__init__.py, tests/conftest.py, tests/test_decoder.py)
- **Files modified:** 2 (pyproject.toml, firestarter/serial_comm.py)
- **Test result:** `pytest -q` → 10 passed in 0.24s

## Accomplishments

- **pytest infrastructure bootstrapped** in `firestarter_app/` for the first time. `pip install -e .[dev]` installs `pytest>=7.0`; `pytest` discovers `tests/` automatically via `[tool.pytest.ini_options] testpaths = ["tests"]`.
- **Shared fixtures** in `tests/conftest.py`:
  - `MAGIC_PREAMBLE_REF = b"\xAA\x55\xAA\x55"` — independent of the production constant.
  - `_ref_crc8_ccitt(data)` — table-FREE reference (poly 0x07, seed 0x00, no reflection, no final XOR). Documented as the regression sentinel for the production lookup table.
  - `build_frame(msg_id, params)` — assembles `magic | len | id | params | crc | 0x0A` exactly per CONTEXT §D-01.
  - `fake_serial` — `_FakeSerial` (`BytesIO`-backed) with `read(n)`, `feed(data)`, `is_open`, `in_waiting`, `port`, `timeout`. Returns `b''` on empty (matches pyserial timeout-empty semantics).
  - `make_comm` — factory returning a `SerialCommunicator` constructed via `__new__` (bypasses `__init__`'s real-serial open + 2s stabilize sleep) with the fake serial port injected.
- **`serial_comm.py` module-level additions:**
  - `LogMessage = namedtuple('LogMessage', ['severity', 'text', 'id'])`.
  - `MAGIC_PREAMBLE: bytes = b'\xAA\x55\xAA\x55'`.
  - `_build_crc8_table()` (private, called once at import) → `_CRC8_CCITT_TABLE: bytes`.
  - `_crc8_ccitt(data) -> int` — table-driven CRC8 over bytes.
  - `_decode_param(ptype, buf, cursor) -> (value, new_cursor)` — handles `u8 / i8 / u16 / i16 / u24 / u32 / i32 / ascii_str` MSB-first.
- **`SerialCommunicator._decode_id_frame(frame_len, body)`** — full validation pipeline:
  1. Frame-too-short / truncated check → `logger.warning(...)`, return None.
  2. CRC8 over `[id, params]` recompute vs the wire's CRC byte → `logger.warning("CRC mismatch for ID 0x...")`, return None.
  3. Catalog lookup → `logger.warning("Unknown message ID 0x... — catalog out of date?")`, return None.
  4. Shape check (`entry.param_bytes >= 0`) → `logger.warning("Param shape mismatch ...")`, return None.
  5. Per-param decode (IndexError / struct.error / ValueError caught) → `logger.warning("Param decode failed ...")`, return None.
  6. Format render (TypeError / ValueError caught) → `text = f"<format-error: {entry.name}>"`, still yields Response so loop progresses.
  7. Success → `LogMessage(severity=SEVERITY_LABEL[entry.severity], text=text, id=msg_id)`.
- **`_read_and_parse_lines` rewritten as the always-on byte-stream reader (D-05):**
  - Single `read(1)` loop appending to a bytearray accumulator.
  - On 4-byte tail match `bytes(accumulator[-4:]) == MAGIC_PREAMBLE`: flush any preceding text via `_parse_response_line`, then consume `len + body + terminator` and dispatch via `_decode_id_frame`. Terminator is read + ignored (D-04 re-sync anchor, not delimiter).
  - On `b == 0x0A`: flush accumulator as a text line via `_parse_response_line`.
  - Otherwise: keep accumulating.
  - Yields `Response(type, message)` for BOTH paths → existing callers untouched.
  - Catches `serial.SerialException` per read and re-raises as `SerialError` (preserves the read-loop's error semantics from the prior implementation).
- **`_log_rurp_feedback` unchanged** — byte-identical to pre-plan baseline. LHOST-03 severity routing surface preserved.
- **`tests/test_decoder.py` — 10 passing acceptance tests** in `class TestIdFrameDecoder`:

| # | Test                                              | Requirement | What it proves                                                             |
| - | ------------------------------------------------- | ----------- | -------------------------------------------------------------------------- |
| 1 | `test_zero_param_frame_decodes_as_ready`          | LHOST-01    | `MSG_OK_READY` → `Response('OK', 'Ready')`; direct `_decode_id_frame` path |
| 2 | `test_u32_param_renders_via_format_string`        | LHOST-01/02 | `MSG_INFO_MEM_SIZE` u32=0x10000 → `'Memory size 0x10000'`                  |
| 3 | `test_u24_render_as_hex_addr`                     | LHOST-02    | `MSG_INFO_ADDR` u24=0x01F4A2 → `'Address: 0x01f4a2'` (render hint)         |
| 4 | `test_multi_param_frame`                          | LHOST-01    | `MSG_ERR_WRITE_FAILED` (u24, u8, u16) full rendered string                 |
| 5 | `test_crc_mismatch_rejected`                      | LHOST-01    | Tampered CRC → returns None + caplog warning matches `"CRC mismatch ..."`  |
| 6 | `test_unknown_id_rejected`                        | LHOST-01 + T-06-14 | ID 0x77 not in catalog → returns None + warning `"Unknown message ID 0x77 ..."` |
| 7 | `test_severity_routing_preserves_response_shape`  | LHOST-03    | `Response.type` is the SEVERITY_LABEL string (`'OK'`, `'ERROR'`)           |
| 8 | `test_text_line_coexistence`                      | LMIG-01     | `b"OK: Hello\n"` → `Response('OK', 'Hello')` (legacy text path unmodified) |
| 9 | `test_text_then_binary_in_one_read`               | LMIG-01     | Text + binary in one fake-serial buffer → both yield in order              |
| 10 | `test_data_progress_u32_pair` (extra)            | LHOST-01    | `MSG_DATA_PROGRESS` (two back-to-back u32) → `'1/65536'`, DATA severity    |

## Verification Commands

```bash
# Install + collect
cd firestarter_app
pip install -e .[dev]                          # => pytest 9.0.3 installed alongside firestarter
pytest --collect-only tests/                   # => 10 collected, exit 0

# Full suite
pytest -q                                      # => 10 passed in 0.24s

# Production constants (CRC poly + magic pinned)
python3 -c "
from firestarter.serial_comm import LogMessage, MAGIC_PREAMBLE, _crc8_ccitt, SerialCommunicator
assert MAGIC_PREAMBLE == b'\xaa\x55\xaa\x55'
assert _crc8_ccitt(b'\x01') == 0x07            # pins poly 0x07 / seed 0x00 / no refl / no XOR
assert callable(SerialCommunicator._decode_id_frame)
print('OK')
"

# Frame builder cross-check (table-FREE conftest reference vs production table)
python3 -c "
from tests.conftest import build_frame
f = build_frame(0x01, b'')
assert f == b'\xAA\x55\xAA\x55\x02\x01\x07\x0A', f.hex()
print('OK', f.hex())
"

# _log_rurp_feedback regression — body byte-identical to pre-plan
git show HEAD~3:firestarter_app/firestarter/serial_comm.py | sed -n '/def _log_rurp_feedback/,/def _read_and_parse_lines/p'
```

All pass.

## Task Commits

Each task = submodule commit + meta-repo pointer bump (established repo pattern).

### Task 1 — Bootstrap pytest infrastructure

1. **firestarter_app:** `ca9470b` (test) — `pyproject.toml` adds `[project.optional-dependencies] dev = ["pytest>=7.0"]` + `[tool.pytest.ini_options]`; `tests/__init__.py` + `tests/conftest.py`.
2. **meta-repo:** `27157cd` (chore) — bump firestarter_app pointer.

### Task 2 — Byte-stream reader + `_decode_id_frame`

3. **firestarter_app:** `527323f` (feat) — `serial_comm.py` adds `LogMessage`, `MAGIC_PREAMBLE`, `_CRC8_CCITT_TABLE`, `_crc8_ccitt`, `_decode_param`, `_decode_id_frame`; rewrites `_read_and_parse_lines`.
4. **meta-repo:** `8ab481e` (chore) — bump firestarter_app pointer.

### Task 3 — LHOST acceptance suite

5. **firestarter_app:** `89aed6b` (test) — `tests/test_decoder.py` (10 tests).
6. **meta-repo:** `7036e98` (chore) — bump firestarter_app pointer.

**Plan metadata commit** (this SUMMARY.md + STATE.md + ROADMAP.md + REQUIREMENTS.md): added at end-of-plan via `gsd-sdk query commit`.

## Files Created / Modified

### firestarter_app submodule — created

- `tests/__init__.py` — zero-byte package marker.
- `tests/conftest.py` — shared fixtures and reference CRC; 133 lines.
- `tests/test_decoder.py` — `TestIdFrameDecoder` class with 10 acceptance tests; 201 lines.

### firestarter_app submodule — modified

- `pyproject.toml` — relocated bare `urls = ...` UP into `[project]` (above the new block) to fix TOML scoping; added `[project.optional-dependencies] dev = ["pytest>=7.0"]`; appended `[tool.pytest.ini_options] testpaths = ["tests"]; addopts = "-ra -q"`.
- `firestarter/serial_comm.py` — 262 insertions / 9 deletions:
  - Module-level: `import struct`; `from firestarter.messages import CATALOG, SEVERITY_LABEL`; `LogMessage` namedtuple; `MAGIC_PREAMBLE` constant; `_build_crc8_table` / `_CRC8_CCITT_TABLE` / `_crc8_ccitt` / `_decode_param`.
  - `SerialCommunicator`: new method `_decode_id_frame`; rewritten `_read_and_parse_lines` body (preserved generator signature, preserved start_time-reset-on-yield discipline, preserved SerialError semantics).
  - `_log_rurp_feedback` body unchanged. `_parse_response_line` body unchanged. All public-method signatures (`get_response`, `expect_ack`, `consume_remaining_input`, etc.) unchanged.
  - `read_line_bytes` retained as-is (legacy callers may rely on it).

## Decisions Made

1. **`ascii_str` decode uses `errors='replace'`** — a tampered/truncated string surfaces as visible replacement characters rather than crashing the read loop. Matches the catalog grammar's tolerance and the threat model's T-06-12 DoS-resilience disposition.
2. **`_decode_id_frame` shape check only fires for fixed-width entries (`entry.param_bytes >= 0`)** — variable-length `ascii_str`-containing entries cannot be pre-validated; they fall back to `_decode_param`'s IndexError handling for over-cursor protection.
3. **`_decode_param` errors are caught as the union `(IndexError, struct.error, ValueError)`** — `struct.error` is the under-buffer surface for u16/i16/u32/i32 fixed-width unpacks; `IndexError` covers u8/i8/u24/ascii_str-length-byte over-cursor; `ValueError` is raised explicitly for unknown ptypes. All three log a unified warning and return None.
4. **Format-render errors yield a tagged placeholder, not None** — `text = f"<format-error: {entry.name}>"` keeps the Response yield surface continuous so the read loop progresses. Visible in `rurp_logger` output but does not stall the protocol.
5. **`_FakeSerial.read(n)` returns `b''` on empty buffer** — matches pyserial's timeout-empty semantics rather than raising. Lets `_read_and_parse_lines` exercise its empty-chunk continue path naturally.
6. **`make_comm` factory uses `__new__` bypass** — sidesteps the real `SerialCommunicator.__init__`'s 2-second `CONNECTION_STABILIZE_DELAY` sleep. Per the plan's PATTERNS reference.
7. **CRC reference in `conftest.py` is table-FREE** — independent of `_CRC8_CCITT_TABLE`. A regression that mutates the production table off-spec (different poly, wrong seed, accidental reflection) will mismatch the reference and fail every frame-building test.
8. **Extra 10th test (`test_data_progress_u32_pair`) added** — exercises the back-to-back u32 case (`MSG_DATA_PROGRESS`'s two u32 params) and `DATA` severity routing. Not in the plan's 9-test minimum but a low-cost edge-case strengthener.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `urls = ...` line after new `[project.optional-dependencies]` table broke `pip install -e .[dev]`**

- **Found during:** Task 1, first `pip install -e .[dev]` after editing `pyproject.toml`.
- **Issue:** The original `pyproject.toml` had `urls = { "Homepage" = "..." }` as a bare key inside `[project]` immediately after `dependencies`. When I inserted `[project.optional-dependencies]\ndev = [...]` between `dependencies` and `urls = ...`, the bare `urls = ...` line landed UNDER the new table header — TOML therefore parsed it as `project.optional-dependencies.urls`, which setuptools rejected with `` `project.optional-dependencies.urls` must be array ``.
- **Fix:** Move the `urls = { ... }` line UP into the `[project]` block (immediately after `dependencies`) so it remains a `[project]` key, then insert `[project.optional-dependencies]` after it. Restores the original key/scope while still threading the new optional-dependency.
- **Files modified:** `firestarter_app/pyproject.toml`.
- **Verification:** `pip install -e .[dev]` → installs `pytest 9.0.3`, exits 0.
- **Committed in:** `ca9470b` (Task 1 submodule commit).

### No other deviations

The plan's specified algorithm for `_read_and_parse_lines` (always-on byte-stream reader, magic-scan with text fallback) and `_decode_id_frame` (CRC validation → catalog lookup → shape check → per-param decode → printf render) was implemented exactly per RESEARCH §"Always-On Byte-Stream Reader" and §"Frame Decode + CRC Validation". No architectural changes; no Rule 4 escalations.

## Authentication Gates

None. The plan is fully autonomous host-side infrastructure; no external service, no hardware, no auth flow.

## Issues Encountered

- One blocking issue: TOML scoping (documented as deviation 1 above). Fixed inline.
- Pre-existing dirty `firestarter_app` files (`firestarter/config.py`, `firestarter/main.py`) were left untouched per orchestrator instruction. Verified via `git status` after each commit: those two files remain `M` (unstaged) throughout; none of the three task commits touch them.

## Confirmation: `_log_rurp_feedback` Not Modified (LHOST-03 surface)

`_log_rurp_feedback` was deliberately left byte-identical to its pre-plan baseline. Confirmed by:

```bash
$ git diff HEAD~6 HEAD -- firestarter_app/firestarter/serial_comm.py | \
    awk '/def _log_rurp_feedback/,/def _decode_id_frame/' | head -50
# (no `-` or `+` lines for any byte inside the function body — only context lines)
```

Severity routing therefore works without any modification: the byte-stream reader wraps every decoded `LogMessage` as `Response(type=<SEVERITY_LABEL string>, message=<rendered text>)` BEFORE yielding, and the existing `_log_rurp_feedback` routes on `response.type` exactly as it did pre-plan for text responses.

## User Setup Required

None.

## Next Plan Readiness

**Plan 06-04 (host fw-version refuse guard)** is unblocked:
- `tests/conftest.py` provides the BytesIO-backed `fake_serial` + `make_comm` fixtures the guard's unit test will reuse.
- `pytest -q` from `firestarter_app/` is the canonical host test gate.

**Plan 06-05 (CI drift gate)** has a stable pytest target to invoke:
- `cd firestarter_app && pip install -e .[dev] && pytest -q` is the host-side gate command.

**Phases 7-8 (call-site conversion)** are unblocked on the host side: the moment firmware call-sites start emitting `rurp_log_id(...)` frames, the host decoder will yield them as `Response` namedtuples through the unchanged `_read_and_parse_lines` surface — no further host code modification required.

## Self-Check: PASSED

Files exist:

- `firestarter_app/pyproject.toml` (modified: `[tool.pytest.ini_options]` + `[project.optional-dependencies] dev`) — FOUND (lines 56-60, 79-81)
- `firestarter_app/tests/__init__.py` — FOUND (zero bytes)
- `firestarter_app/tests/conftest.py` (MAGIC_PREAMBLE_REF, _ref_crc8_ccitt, build_frame, fake_serial, make_comm) — FOUND
- `firestarter_app/firestarter/serial_comm.py` (LogMessage, MAGIC_PREAMBLE, _CRC8_CCITT_TABLE, _crc8_ccitt, _decode_param, _decode_id_frame, rewritten _read_and_parse_lines) — FOUND
- `firestarter_app/tests/test_decoder.py` (10 tests) — FOUND
- `.planning/phases/06-logging-infrastructure/06-03-SUMMARY.md` (this file) — FOUND

Commits (all on `feature/phase-10-static-pins`):

- firestarter_app `ca9470b` — FOUND (Task 1)
- firestarter_app `527323f` — FOUND (Task 2)
- firestarter_app `89aed6b` — FOUND (Task 3)
- meta-repo `27157cd`     — FOUND (Task 1 pointer bump)
- meta-repo `8ab481e`     — FOUND (Task 2 pointer bump)
- meta-repo `7036e98`     — FOUND (Task 3 pointer bump)

Behavioural verification:

- `pytest -q` → `10 passed in 0.24s`
- `python3 -c "from firestarter.serial_comm import _crc8_ccitt; assert _crc8_ccitt(b'\\x01') == 0x07"` → exits 0 (poly pinned)
- `python3 -c "from firestarter.serial_comm import MAGIC_PREAMBLE; assert MAGIC_PREAMBLE == b'\\xaa\\x55\\xaa\\x55'"` → exits 0
- `python3 -c "from firestarter.serial_comm import SerialCommunicator; assert hasattr(SerialCommunicator, '_decode_id_frame')"` → exits 0

---
*Phase: 06-logging-infrastructure*
*Completed: 2026-05-18*
