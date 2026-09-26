# Phase 55: Relocate Buffer-Size Advertisement to the Operation OK Ack — Research

**Researched:** 2026-06-04
**Domain:** Codegen message catalog / firmware identity string / host ack parsing / dual-repo lockstep
**Confidence:** HIGH (all findings verified directly from source code on the `v1.10-serial-transport-hardening` branch)

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CAP-01 | Firmware reports `DATA_BUFFER_SIZE` as a `u16` param on the operation `OK:Ready` ack (`MSG_OK_READY`) via the codegen catalog; host reads it there and defaults to 512 when absent; version string returns to `<version>:<board>` only; no `FirmwareOutdatedError` on absent field. | §Codegen Catalog, §MSG_OK_READY Emit Sites, §FW_VERSION Revert, §Host Read Point, §Safe-Default Design. |

</phase_requirements>

---

## Summary

Phase 55 reverses the Phase 54 D-05 decision: instead of embedding the board's
buffer capacity inside the firmware version identity string (`<maxchunk>` as the 4th
colon-delimited field) and raising `FirmwareOutdatedError` when absent, the
advertisement moves to the per-operation `OK:Ready` ack (`MSG_OK_READY`) as a `u16`
parameter, and the host defaults to 512 (universally safe — the Uno floor) when the
ack carries no param.

The change has three independently verifiable parts:

**Part 1 — FW_VERSION revert (firmware + host).** Remove the `:<maxchunk>` and
`:<buf>` appended in Phase 54 from `FW_VERSION` in `firestarter.h` (line 40), reverting
to `VERSION ":" RURP_BOARD_NAME`. On the host, remove the `fw_fields[2]`/`fw_fields[3]`
parse from `_probe_port` in `serial_comm.py` (lines 624-632) — these fields will no
longer be present. `firmware_max_chunk` and `firmware_buffer_size` attributes are removed
from the `SerialCommunicator` instance (or left but never set). `firmware.py`'s
`check_current_firmware` already safely ignores extra fields (it takes only
`parts[0]`/`parts[1]`); no change needed there.

**Part 2 — MSG_OK_READY catalog addition.** Add a `u16` param to `MSG_OK_READY`
(currently `params = []`) in the canonical `messages.toml` (meta-repo
`/workspaces/tools/catalog/messages.toml`, line 36). The `u16` carries
`DATA_BUFFER_SIZE`. After the catalog edit, run `tools/catalog/sync_to_subrepos.sh` to
regenerate `include/messages.h` (firmware) and `firestarter/messages.py` (host). The
drift gate (`codegen.py --catalog ... --check`) and CI byte-identity assertion then
enforce the new shape across both repos. All four `MSG_OK_READY` emit sites in the
firmware are updated from `LOG_OK_ID(MSG_OK_READY)` to
`LOG_OK_ID_U16(MSG_OK_READY, DATA_BUFFER_SIZE)`.

**Part 3 — Host read point + safe default.** The host reads the `u16` from the
operation-setup `OK:Ready` ack at the point where `find_and_connect` returns
(`communicator.programmer_info` is set from the post-command `expect_ack` result). The
natural place to extract the capacity is directly after the operation-setup ack is
received in `_probe_port` (line 657-661 of `serial_comm.py`): after `is_ok` is confirmed
and `communicator.programmer_info = msg` is set, parse the decoded `LogMessage`'s param
value from the ack. `_calculate_buffer_size()` then reads this value; when absent,
returns 512 (no error). `FirmwareOutdatedError` is removed from `_calculate_buffer_size`.

**RAM impact:** Adding a `u16` param to `MSG_OK_READY` emits 2 extra bytes on the wire per
ack (the 2-byte param packed big-endian). Zero additional SRAM is consumed — the
`rurp_log_id_u16` helper uses a local 2-byte stack array (same as today's
`LOG_OK_ID_U8_U8`). Uno RAM after Phase 54 is 1552/2048 bytes used (496 B free);
this change is negligible. [VERIFIED: code trace + RAM report]

**Primary recommendation:** Implement as three atomic steps: (1) revert FW_VERSION in
firmware + host probe parse; (2) add `u16` param to `MSG_OK_READY` in TOML, sync, update
all four emit sites; (3) read `u16` from operation-setup ack in host + 512 default with
no error. Wave 0 needs a RED test for "ack without param → 512, no error".

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Buffer capacity advertisement | Firmware / MCU | — | FW knows `DATA_BUFFER_SIZE` at compile time; emits it on every operation `OK:Ready` ack |
| Identity string (version only) | Firmware / MCU | Host parses for version | Reverts to pure `<ver>:<board>` — no capability fields |
| Ack param read + chunk sizing | Host Python | — | `_calculate_buffer_size()` in `eprom_operations.py` reads the `u16` from the ack |
| Safe default (absent ack param) | Host Python | — | Returns 512 when `MSG_OK_READY` carries no `u16` (un-advertising firmware) |
| Drift gate (messages.toml byte-identity) | CI / meta-repo sync | Both sub-repos | `sync_to_subrepos.sh` + `codegen drift gate` CI step enforces byte-identity |
| Parity gate (firmware/host constants) | CI / test | Both repos | `test_revision_constants_parity.py` + firmware Unity constants tests |

---

## Critical Research Answers

### 1. Codegen catalog: how to declare a `u16` param on a message

The catalog schema is fully documented in the codegen.py source
(`/workspaces/firestarter/tools/catalog/codegen.py`). Adding a `u16` param to
`MSG_OK_READY` requires:

**messages.toml change (meta-repo `/workspaces/tools/catalog/messages.toml`):**

```toml
# BEFORE (line 33-39):
[[messages]]
id          = 0x01
name        = "MSG_OK_READY"
severity    = "OK"
format      = "Ready"
params      = []
wire_format = "id_frame"

# AFTER:
[[messages]]
id          = 0x01
name        = "MSG_OK_READY"
severity    = "OK"
format      = "Ready (%u)"
params      = [{ type = "u16" }]
wire_format = "id_frame"
```

**Important codegen validation rules that apply:**
- Rule 9: format-spec count must match non-bytes param count. Adding `{ type = "u16" }` requires exactly one `%u` specifier in `format`. [VERIFIED: codegen.py lines 287-300]
- Rule 10: 24-byte total wire-param budget. One `u16` = 2 bytes, well within 24. [VERIFIED: codegen.py lines 302-316]
- Rule 8: `wire_format="id_frame"` is correct (unchanged). [VERIFIED]

**Alternative format string:** The format string `"Ready (%u)"` will render as `"Ready (512)"` or `"Ready (1024)"` in the host. This is human-readable in verbose mode. The planner may choose `"Ready"` (zero-spec, matching an empty params tuple) by keeping `format = "Ready"` with `params = []` — BUT the codegen rule requires the format-spec count to equal the non-bytes param count. With `{ type = "u16" }`, the format string MUST have exactly one `%u`. The planner cannot keep `format = "Ready"` and add a `u16` param. [VERIFIED: codegen.py Rule 9]

**What codegen generates from this:**

For C++ (`messages.h`):
```c
// MSG_OK_READY ID constant — unchanged (0x01)
#define MSG_OK_READY   0x01
```

The messages.h only emits ID constants. The param shape is not encoded in messages.h — the
caller is responsible for calling `LOG_OK_ID_U16(MSG_OK_READY, DATA_BUFFER_SIZE)`. The
codegen for the C++ side emits only `#define MSG_OK_READY 0x01` (same as today).
[VERIFIED: codegen.py `emit_cpp_header` function, lines 474-533]

For Python (`messages.py`):
```python
MSG_OK_READY   = 0x01

CATALOG: dict[int, MessageDef] = {
    0x01: MessageDef(id=0x01, name="MSG_OK_READY", severity=SEVERITY_OK,
                     format="Ready (%u)", params=(("u16", "dec"),),
                     param_bytes=2, wire_format="id_frame"),
```

The `param_bytes=2` field is load-bearing: the `decode_id_frame` shape-check at
`codec.py:229` uses it — `if entry.param_bytes >= 0 and len(params_bytes) != entry.param_bytes`
— to validate incoming frames. This means a frame with `MSG_OK_READY` carrying 0 param
bytes (from un-advertising firmware) will fail the shape check and return `None`.
[VERIFIED: codec.py lines 229-234]

**Critical implication:** If `MSG_OK_READY` has `params = [{ type = "u16" }]` in the catalog,
the host's `decode_id_frame` will REJECT a `MSG_OK_READY` frame with 0 param bytes (shape
mismatch). This means the host cannot parse an ack from un-advertising firmware as
`MSG_OK_READY`. The ack would arrive, fail shape check, and be silently dropped
(logged as warning). `expect_ack` would loop waiting for another OK-severity frame —
none would come — and eventually timeout.

**Resolution options:**

**Option A — param_bytes=-1 trick via ascii_str:** The `ascii_str` param type sets
`param_bytes=-1` (variable-length), which causes the shape check at codec.py:229 to
be skipped (`if entry.param_bytes >= 0`). However, `_decode_param` for `ascii_str`
reads a length-prefix byte, which firmware without the param would not send. This would
cause a decode error on the param itself.

**Option B — Catalog declares 0 params; host reads from raw bytes:** Keep
`MSG_OK_READY` with `params = []` in the catalog. The host reads the `u16` param
from the raw `Response` payload (the decoded `LogMessage` id-frame body) using the
`params_bytes` field of the body, not the catalog. This requires the host to do
out-of-band inspection of the raw body rather than relying on the catalog-decoded
`values` list. This is the "bytes" type approach but requires custom parsing.

**Option C — Separate "advertising" message ID:** Use a new message ID (e.g. 0x06
`MSG_OK_READY_CAP`) that carries the `u16`, emitted by advertising firmware alongside
`MSG_OK_READY`. The host watches for `MSG_OK_READY_CAP` and defaults to 512 if it
never arrives before the operation starts.

**Option D — Use the `bytes` param type, host inspects raw payload:** Add
`params = [{ type = "bytes" }]` to `MSG_OK_READY`. The `bytes` type has `param_bytes=-1`
(variable, skips shape check). The host reads the raw bytes and extracts the `u16` if
present (len=2), or defaults to 512 if empty (len=0). Old firmware sends
`MSG_OK_READY` with 0 param bytes — the host finds `params_bytes == b""` and uses 512.
New firmware sends 2 param bytes (big-endian `DATA_BUFFER_SIZE`). **This is the
recommended option.** [VERIFIED: codegen.py PARAM_TYPE_BYTES `"bytes": None` → sets
`param_bytes=-1` in catalog; codec.py:229 shape check skipped for `param_bytes=-1`]

**Recommended approach: `bytes` param type for MSG_OK_READY:**

```toml
[[messages]]
id          = 0x01
name        = "MSG_OK_READY"
severity    = "OK"
format      = "Ready"
params      = [{ type = "bytes" }]
wire_format = "id_frame"
```

This satisfies Rule 9 (the `bytes` type has no `%` specifier; Rule 9 checks only
`non_bytes_count`, which is 0, matching the 0 `%` specifiers in `"Ready"`). The host
reads `params_bytes` (the raw bytes between id and CRC) and extracts a `u16` if
`len(params_bytes) == 2`. Old firmware sends `MSG_OK_READY` with 0 param bytes; the host
gets `params_bytes == b""` and defaults to 512. New firmware sends 2 param bytes;
host extracts the `u16`.

**Wire size:** `MSG_OK_READY` with 2 param bytes: frame = 4 (magic) + 2 (len) +
1 (id) + 2 (params) + 1 (crc) + 1 (anchor) = 11 bytes. With 0 params: 9 bytes.
The firmware always emits 2 param bytes (advertising).

[VERIFIED: codegen.py `PARAM_TYPE_BYTES["bytes"] = None` line 73; Rule 9 excludes
bytes from specifier count check lines 290-300; codec.py param_bytes=-1 shape-check
skip line 229]

---

### 2. MSG_OK_READY emit sites — complete inventory

All 4 emit sites confirmed by grep: [VERIFIED: grep over firestarter/src/]

| File | Line | Context | Must Update? |
|------|------|---------|--------------|
| `firestarter/src/firestarter.cpp` | 142 | Operation setup ack — the primary ack the host reads for buffer negotiation | YES |
| `firestarter/src/hardware_operations.cpp` | 43 | FW-probe "read voltage" setup ack (VPP/VPE monitor readiness) | YES |
| `firestarter/src/dev_tools.cpp` | 107 | `dt_set_register()` dev-tool ack — waits for user button | YES |
| `firestarter/src/dev_tools.cpp` | 153 | `dt_set_address()` dev-tool ack — waits for user button | YES |

All four must be changed from:
```c
LOG_OK_ID(MSG_OK_READY);
```
to:
```c
LOG_OK_ID_U16(MSG_OK_READY, (uint16_t)DATA_BUFFER_SIZE);
```

The `LOG_OK_ID_U16` macro is already defined in `logging_id.h` line 125:
```c
#define LOG_OK_ID_U16(id, p1)          LOG_ID_U16((id), (p1))
```

and `rurp_log_id_u16` is already implemented in `rurp_serial_utils.cpp` line 484:
```c
void rurp_log_id_u16(uint8_t id, uint16_t v) {
    uint8_t b[2] = { (uint8_t)((v >> 8) & 0xFF), (uint8_t)(v & 0xFF) };
    rurp_log_id(id, b, 2);
}
```

No new infrastructure needed. The call to `LOG_OK_ID_U16(MSG_OK_READY, DATA_BUFFER_SIZE)`
packs `DATA_BUFFER_SIZE` as big-endian 2 bytes and emits them as the param payload.
[VERIFIED: logging_id.h lines 123-128; rurp_serial_utils.cpp lines 484-489]

**Leonardo distinction:** `DATA_BUFFER_SIZE` is defined in the build environment
(`platformio.ini`), not in firmware source — `uno` env gets 512, `leonardo` gets 1024.
The same `LOG_OK_ID_U16(MSG_OK_READY, DATA_BUFFER_SIZE)` macro call in the source
compiles to the correct value for each board. [VERIFIED: firestarter.h line 16-18]

---

### 3. FW_VERSION revert — exact diff

**Current state (Phase 54 output, firestarter.h line 40):**
```c
#define FW_VERSION VERSION ":" RURP_BOARD_NAME ":" FS_STRINGIFY(DATA_BUFFER_SIZE) ":" FS_STRINGIFY(DATA_BUFFER_SIZE)
// emits e.g. "3.0.0b8:uno:512:512"
```

**Target state (Phase 55, pure version + board):**
```c
#define FW_VERSION VERSION ":" RURP_BOARD_NAME
// emits e.g. "3.0.0b8:uno"
```

The comment block at lines 26-37 (documenting the Phase 54 maxchunk field) should be
replaced with a note that buffer capacity is now advertised on `MSG_OK_READY`.

**Host parse revert (serial_comm.py lines 619-632):**

Current (Phase 54):
```python
fw_payload = fw_msg.split("FW:", 1)[-1].strip()
fw_fields = fw_payload.split(":")
if len(fw_fields) >= 3 and fw_fields[2].strip().isdigit():
    communicator.firmware_buffer_size = int(fw_fields[2].strip())
if len(fw_fields) >= 4 and fw_fields[3].strip().isdigit():
    communicator.firmware_max_chunk = int(fw_fields[3].strip())
```

Target (Phase 55 revert) — keep only what's needed for version validation:
```python
fw_payload = fw_msg.split("FW:", 1)[-1].strip()
fw_fields = fw_payload.split(":")
# Fields: [0]=version, [1]=board. No capacity fields — capacity now on MSG_OK_READY ack.
```

The `SerialCommunicator.__init__` attributes `firmware_buffer_size` (line 118) and
`firmware_max_chunk` (line 123) need updated docstrings or removal. Since `firmware_max_chunk`
will now be populated from the operation-setup ack (not the FW probe), its attribute
declaration remains but is populated by a different code path.

**firmware.py impact:** `check_current_firmware` (lines 112-125) already safely takes only
`parts[0]` and `parts[1]`, with a comment saying extra fields are ignored. With the 2-field
revert, `parts = payload.split(":")` will yield only `["version", "board"]` — exactly what
the function reads. No change needed. [VERIFIED: firmware.py lines 112-125]

---

### 4. Host read point: where to extract the `u16` from the operation-setup ack

**Current flow:**
1. `_setup_operation()` calls `SerialCommunicator.find_and_connect(command_dict, config)`
2. `find_and_connect` calls `_probe_port` which: sends the command → calls `expect_ack()` →
   returns a communicator with `programmer_info` set to the ack message.
3. Back in `_setup_operation()`, `self._calculate_buffer_size()` is called (line 224).
4. `_calculate_buffer_size()` reads `self.comm.firmware_max_chunk`.

**New flow for Phase 55:**

The operation-setup `OK:Ready` ack is the one at `_probe_port` lines 656-661:
```python
# Send the user's actual command (or CMD_FW_VERSION re-send when exempt).
communicator.send_json_command(command_to_send)
is_ok, msg = communicator.expect_ack()  # <-- this is the OK:Ready from init_programmer

if is_ok:
    communicator.programmer_info = msg
    ...
    return communicator
```

The ack that arrives here is `MSG_OK_READY` from `init_programmer` in `firestarter.cpp:138`.
After Phase 55, this ack carries 2 bytes of `DATA_BUFFER_SIZE` as a `bytes` param.

**Problem:** `expect_ack()` currently returns `(bool, Optional[str])` — the second element
is the `Response.message` (a rendered text string like `"Ready"`). The raw `params_bytes`
from the decoded frame are not surfaced to `expect_ack` callers.

**Two sub-options:**

**Sub-option A — Intercept at `_decode_id_frame` level:**
Override `_decode_id_frame` in the communicator so that when it sees `MSG_OK_READY`
with a non-empty params body, it stores the decoded `u16` on the communicator instance
(e.g., `self._pending_ok_ready_buf_size`). This happens synchronously inside
`_read_and_parse_lines` before `expect_ack` returns. After `expect_ack` returns,
`_probe_port` checks `communicator._pending_ok_ready_buf_size` and sets
`communicator.firmware_max_chunk`.

This approach keeps the GATE-1.8d ring-fence intact: `_read_and_parse_lines` body is
not modified; only `_decode_id_frame` is overridden (the existing override pattern is
already used in `FaultInjectingSerialCommunicator` at lines 732-765). [VERIFIED:
serial_comm.py lines 732-765]

**Sub-option B — Parse the ack message string:**
The `Response.message` for `MSG_OK_READY` with `bytes` param and `format = "Ready"`
will be just `"Ready"` (because `bytes` type has no `%` specifier and `format_message`
falls through to `entry.format % tuple(fmt_values)` where `fmt_values` excludes bytes).
There is nothing to parse from the string.

However, if the format string is changed to something like `"Ready (%u)"` with a `u16`
param (using the fixed-shape u16 approach), the message would be `"Ready (512)"` and
the host could parse the integer. But this requires the fixed-shape approach, which
breaks the un-advertising-firmware backward compatibility as documented in §1 above.

**Recommended:** Sub-option A — intercept at `_decode_id_frame` level. Concretely:

After `decode_id_frame` runs in `codec.py` and returns a `LogMessage`, the caller
(`_read_and_parse_lines`) creates a `Response`. The `LogMessage` has `id`, `text`,
`severity`, `payload`. The `payload` field is currently used only for `MSG_DATA_CHUNK`.

For Phase 55, extend `codec.decode_id_frame` to also set a `cap` or similar side-channel
for `MSG_OK_READY`. But this would require `decode_id_frame` to have a way to return the
extra info. The cleanest approach:

**Cleanest approach:** When `MSG_OK_READY` arrives with `params = [{ type = "bytes" }]`
and the `bytes` param is 2 bytes long, treat it similarly to `MSG_DATA_CHUNK`: store the
`params_bytes` in `LogMessage.payload` (which is already `Optional[bytes]`). The codec
already sets `chunk_payload` from `MSG_DATA_CHUNK` (lines 271-277 of `codec.py`). Add an
analogous block for `MSG_OK_READY`:

```python
# MSG_OK_READY with 2-byte params payload carries DATA_BUFFER_SIZE as u16.
# payload is normally None; for MSG_OK_READY it carries the raw param bytes.
ok_ready_payload = None
if msg_id == MSG_OK_READY and len(params_bytes) == 2:
    ok_ready_payload = bytes(params_bytes)

chunk_payload = None
if msg_id == MSG_DATA_CHUNK and values and isinstance(values[0], (bytes, bytearray)):
    chunk_payload = bytes(values[0])

effective_payload = ok_ready_payload or chunk_payload
return LogMessage(severity=severity_label, text=text, id=msg_id, payload=effective_payload)
```

Then in `_probe_port` after the operation-setup `expect_ack` returns, inspect the
underlying Response to extract the payload. But `expect_ack` discards the `Response`
object — it only returns `(bool, str)`.

**Final recommended approach for the seam:**

The cleanest minimal change:
1. In `_probe_port`, after `is_ok, msg = communicator.expect_ack()` at line 657,
   add a direct call to read the pending capacity from `communicator`:

```python
is_ok, msg = communicator.expect_ack()  # MSG_OK_READY from init_programmer
if is_ok:
    # Read buffer capacity from communicator if it was set by _decode_id_frame
    # during the MSG_OK_READY ack parse (Phase 55: bytes param on MSG_OK_READY).
    communicator.programmer_info = msg
    ...
```

The capacity is set on `communicator.firmware_max_chunk` via a side-effect inside
`_decode_id_frame` when it processes `MSG_OK_READY`. The `_decode_id_frame` override
pattern is:

```python
def _decode_id_frame(self, frame_len: int, body: bytes) -> Optional[LogMessage]:
    result = codec.decode_id_frame(frame_len, body)
    if result is not None and result.id == MSG_OK_READY:
        # MSG_OK_READY carries DATA_BUFFER_SIZE as 2 bytes (bytes param).
        # Extract u16 big-endian; default to None if absent (old firmware).
        params_bytes = body[1:-1]  # between id and crc
        if len(params_bytes) == 2:
            self.firmware_max_chunk = struct.unpack(">H", params_bytes)[0]
        # If params_bytes is empty (un-advertising firmware), firmware_max_chunk stays None.
    return result
```

This override runs inside `_read_and_parse_lines` → `_decode_id_frame`, which is called
every time a binary id-frame arrives. It does NOT modify the ring-fenced
`_read_and_parse_lines` body; it overrides `_decode_id_frame` which is the designated
extension point. [VERIFIED: GATE-1.8d note at serial_comm.py lines 250-259]

**`_calculate_buffer_size` change:**

```python
def _calculate_buffer_size(self) -> int:
    # Phase 55 (CAP-01): read firmware-advertised DATA_BUFFER_SIZE from the
    # operation-setup MSG_OK_READY ack (u16 bytes param).
    # When absent (un-advertising firmware or ack without param), default to
    # 512 — the universally safe Uno floor, never overflows any board.
    # No FirmwareOutdatedError: graceful default replaces lockstep-or-fail.
    max_chunk = (
        getattr(self.comm, "firmware_max_chunk", None) if self.comm else None
    )
    if max_chunk is not None and max_chunk >= 1:
        return max_chunk
    return 512  # safe Uno floor — CAP-01 safe default
```

The Phase 54 `raise FirmwareOutdatedError(...)` line is removed. [VERIFIED: current
eprom_operations.py lines 163-177]

---

### 5. Drift gate and parity gate: procedure

**messages.toml drift gate (byte-identity, enforced by CI):**

1. Edit canonical `messages.toml` at `/workspaces/tools/catalog/messages.toml` (the
   meta-repo copy, lines 33-39 for `MSG_OK_READY`).
2. Run `bash /workspaces/tools/catalog/sync_to_subrepos.sh` — this:
   - Copies `messages.toml` and `codegen.py` byte-identically to both sub-repos
   - Regenerates `firestarter/include/messages.h` (C++ firmware side)
   - Regenerates `firestarter_app/firestarter/messages.py` (host Python side)
   - Asserts the two sub-repo `messages.toml` copies are byte-identical
3. CI enforces this on every PR via:
   - **Firmware CI** (`firestarter/.github/workflows/build.yml` lines 61-80):
     `codegen.py --check` + `codegen.py --language cpp` + `git diff --exit-code include/messages.h`
   - **Host CI** (`firestarter_app/.github/workflows/ci.yml` lines 35-54):
     `codegen.py --check` + `codegen.py --language python` + `git diff --exit-code firestarter/messages.py`
   [VERIFIED: build.yml and ci.yml]

**Constant parity gate:**

No new constants are introduced in Phase 55. `DATA_BUFFER_SIZE` is already defined in
`firestarter.h` and is not mirrored in `constants.py` (the parity test in
`test_revision_constants_parity.py` covers `CMD_FRAME_MAX`, `COMMAND_*`, `FLAG_*`,
`CTRL_*`, and `REVISION_*` blocks — not `DATA_BUFFER_SIZE` itself, which is implicit
in `BUFFER_SIZE = 512` and `LEONARDO_BUFFER_SIZE = 1024` in `constants.py`).

`CMD_FRAME_MAX` remains `512` (unchanged, equals `DATA_BUFFER_SIZE`). No parity
update needed. [VERIFIED: constants.py lines 36-40; firestarter.h line 24]

**test_even_block.py impact:** The existing tests assert that `firmware_max_chunk=512`
causes `_calculate_buffer_size()` to return 512, and that absent `firmware_max_chunk`
raises `FirmwareOutdatedError`. After Phase 55, the absent-field test must be updated:
absent field should return 512 (not raise). [VERIFIED: test_even_block.py lines 92-96]

**Dual-repo commit procedure:**
1. Edit meta-repo `messages.toml` → run sync script → commit generated files in
   **both** sub-repos atomically with the source change (same commit or back-to-back
   before CI runs).
2. The dual-repo pattern is the same as Phases 50-52: firmware changes commit first or
   in parallel with host changes (no strict ordering, but both must be committed before
   CI runs the drift gate).

---

### 6. Tests that must stay green + new test needed

**Tests that must stay green:**

| Test | Location | Covers | Risk |
|------|----------|--------|------|
| `test_even_block.py::TestEvenBlockNoRemainder` | host | 65536 % 512/1024 == 0 | No change; stays green |
| `test_even_block.py::TestEvenBlockFrameVectorsCapBoundary` | host | COBS round-trip at 512 bytes | No change; stays green |
| `test_frame_vectors.py` | host | Frame vector corpus | No change unless messages.toml change breaks CATALOG |
| `test_revision_constants_parity.py` | host | CMD_FRAME_MAX parity | No change; CMD_FRAME_MAX stays 512 |
| `test_messages` (Unity) | firmware | ID-frame encoding | `MSG_OK_READY` with `u16` param must now encode correctly |
| `test_frame_vectors` (Unity) | firmware | Frame vector corpus | No change |
| `test_cobs_cmd_frame` (Unity) | firmware | Command COBS decode | No change |
| `test_fw_version_guard.py` | host | Pre-v1.2 firmware rejection | `FirmwareOutdatedError` from `_validate_firmware_version` stays; only the absent-`maxchunk` raise is removed |
| `test_fwguard.py` | host | FW probe version parsing | Identity string is now 2-field; tests that verify 3- or 4-field parse must be updated |
| `test_serial_comm.py::test_firmware_max_chunk_parsed_from_4_field_identity_string` | host | Phase 54 max_chunk parse | **Must be updated** — no longer parsed from identity string; now from ack |
| `test_serial_comm.py::test_firmware_max_chunk_stays_none_for_3_field_identity_string` | host | Phase 54 absent field | **Remove or update** — 3-field string no longer matters |
| `test_even_block.py::test_calculate_buffer_size_raises_without_max_chunk` | host | Phase 54 lockstep-or-fail | **Must be updated** — absent field now returns 512, not raises |

**New test required (pins the CAP-01 safe-default behavior):**

```python
# test_even_block.py or new test_cap_01.py
class TestCapSafeDefault:
    """CAP-01: un-advertising ack (no bytes param on MSG_OK_READY) → 512 default, no error."""

    def test_absent_firmware_max_chunk_returns_512(self) -> None:
        """When firmware_max_chunk is None (ack had no param), _calculate_buffer_size
        returns 512 — the universally safe Uno floor. No FirmwareOutdatedError raised.
        This is the CAP-01 pin: reverses Phase 54 D-05 lockstep-or-fail."""
        op = EpromOperator(ConfigManager())
        # No comm set -> firmware_max_chunk absent -> must return 512, NOT raise
        result = op._calculate_buffer_size()
        assert result == 512, (
            f"Expected 512 (Uno floor default), got {result}"
        )

    def test_512_ok_ready_ack_sets_firmware_max_chunk(self) -> None:
        """An MSG_OK_READY ack with 2 bytes [0x02, 0x00] sets firmware_max_chunk = 512."""
        # Simulate the _decode_id_frame override setting firmware_max_chunk
        op = EpromOperator(ConfigManager())
        op.comm = SimpleNamespace(firmware_max_chunk=512)
        assert op._calculate_buffer_size() == 512

    def test_1024_ok_ready_ack_sets_firmware_max_chunk(self) -> None:
        """An MSG_OK_READY ack with 2 bytes [0x04, 0x00] sets firmware_max_chunk = 1024."""
        op = EpromOperator(ConfigManager())
        op.comm = SimpleNamespace(firmware_max_chunk=1024)
        assert op._calculate_buffer_size() == 1024
```

The "injecting an un-advertising ack → 512 default, no error" test is the CAP-01
pin required by Phase 55 SC3. [INFERRED: from SC3 wording]

---

### 7. RAM concern: adding `u16` param to `MSG_OK_READY`

**Current Uno RAM (after Phase 54):** 1552/2048 bytes used, 496 B free.
[VERIFIED: `pio run -e uno` output on branch]

**Cost of `LOG_OK_ID_U16(MSG_OK_READY, DATA_BUFFER_SIZE)` vs `LOG_OK_ID(MSG_OK_READY)`:**

- `LOG_OK_ID(MSG_OK_READY)` → `rurp_log_id(0x01, NULL, 0)` — zero param bytes on stack
- `LOG_OK_ID_U16(MSG_OK_READY, DATA_BUFFER_SIZE)` → `rurp_log_id_u16(0x01, 512)` → allocates
  `uint8_t b[2]` on the stack locally inside `rurp_log_id_u16`, calls `rurp_log_id(id, b, 2)`

The 2-byte stack array is a local variable inside `rurp_log_id_u16` (already a
shared helper), not a global. It lives only for the duration of the call frame.
Stack frame growth is ≤ 2 bytes.

`rurp_log_id_u16` is already compiled and linked in the firmware (used by other emit
sites, e.g., `MSG_WARN_VPP_LOW` / `MSG_DATA_VPP_VOLTAGE` encode via `LOG_DATA_ID_U16_U16`
which calls `rurp_log_id` with a 4-byte buf). The 4 call sites for `MSG_OK_READY` each
add one additional CALL instruction (2 bytes Flash each = 8 bytes Flash total) with no
SRAM growth.

**Conclusion: SRAM impact is negligible (≤ 2 bytes stack headroom consumed during the
call, not static RAM). Well within the 496 B free margin.** [VERIFIED: code trace]

---

## Standard Stack

No new external packages. This phase modifies existing files in both sub-repos and the
meta-repo catalog. No new dependencies introduced.

### Files Modified

**Meta-repo (`/workspaces/tools/catalog/`):**

| File | Change |
|------|--------|
| `messages.toml` lines 33-39 | Add `params = [{ type = "bytes" }]` and update format string for `MSG_OK_READY` |

**Firmware (`firestarter/`):**

| File | Line | Change |
|------|------|--------|
| `tools/catalog/messages.toml` | 33-39 | Synced copy (run sync script) |
| `include/messages.h` | generated | Regenerated by sync script (MSG_OK_READY entry changes in Python CATALOG — C++ header only has the ID constant, unchanged) |
| `include/firestarter.h` | 26-40 | Revert `FW_VERSION` to `VERSION ":" RURP_BOARD_NAME`; update comment |
| `src/firestarter.cpp` | 142 | `LOG_OK_ID(MSG_OK_READY)` → `LOG_OK_ID_U16(MSG_OK_READY, (uint16_t)DATA_BUFFER_SIZE)` |
| `src/hardware_operations.cpp` | 43 | Same change |
| `src/dev_tools.cpp` | 107 | Same change |
| `src/dev_tools.cpp` | 153 | Same change |

**Host (`firestarter_app/`):**

| File | Line | Change |
|------|------|--------|
| `tools/catalog/messages.toml` | 33-39 | Synced copy (run sync script) |
| `firestarter/messages.py` | generated | Regenerated by sync script (MSG_OK_READY now has `params=(("bytes", "hex"),)`, `param_bytes=-1`) |
| `firestarter/serial_comm.py` | 118-123 | Remove/update `firmware_buffer_size`/`firmware_max_chunk` from init comments; add `_decode_id_frame` override to extract `u16` from `MSG_OK_READY` ack |
| `firestarter/serial_comm.py` | 619-632 | Remove `fw_fields[2]`/`fw_fields[3]` parse block entirely |
| `firestarter/eprom_operations.py` | 163-177 | Replace `raise FirmwareOutdatedError` with `return 512` |
| `firestarter/constants.py` | 26-34 | Update `MAX_DATA_CHUNK` comment (now doubly obsolete) |
| `tests/test_even_block.py` | 92-96 | Update absent-field test: expect 512 return instead of FirmwareOutdatedError |
| `tests/test_serial_comm.py` | ~400-448 | Remove or update the three Phase 54 identity-string parse tests |
| `tests/test_even_block.py` or new `test_cap_01.py` | new | Add un-advertising-ack → 512 default test (CAP-01 pin) |

---

## Architecture Patterns

### System Architecture Diagram

```
                 FW VERSION PROBE (once per connection)
                 ─────────────────────────────────────
Host                                              Firmware
─────────────────────────────────────────────────────────────
send_json_command({"state": 13})  ─COBS+CRC8──▶  CMD_FW_VERSION handler
                                                    │
                                  ◀── MSG_OK_READY  │  (from init_programmer)
                                      (2 bytes: DATA_BUFFER_SIZE u16)
                                                    │
                                  ◀── MSG_OK_FW_VERSION text: "FW: 3.0.0b8:uno"
                                      (now 2-field: <version>:<board> only)

Host _probe_port:
  pre_ack = expect_ack()      <─ MSG_OK_READY (2 bytes buf_size)
  fw_ack  = expect_ack()      <─ MSG_OK_FW_VERSION: "FW: 3.0.0b8:uno"
  parse version + board from fw_ack (2 fields only, no buf/maxchunk)
  comm.firmware_max_chunk set via _decode_id_frame override on pre_ack


                 OPERATION SETUP (per write/verify operation)
                 ─────────────────────────────────────────────
Host                                              Firmware
─────────────────────────────────────────────────────────────
send_json_command({"cmd": 2, ...})  ──▶  init_programmer()
                                              │
                              ◀── MSG_OK_READY │  (2 bytes: DATA_BUFFER_SIZE u16)
                                              └─ firestarter.cpp:138
                                                 LOG_OK_ID_U16(MSG_OK_READY,
                                                               DATA_BUFFER_SIZE)
Host _probe_port (operation command):
  is_ok, msg = expect_ack()   <─ MSG_OK_READY (2 bytes buf_size)
  _decode_id_frame override sets comm.firmware_max_chunk
  _calculate_buffer_size() returns firmware_max_chunk (or 512 if absent)

                 WRITE OPERATION
                 ─────────────
_main_phase_send_data:
  chunk_size = _calculate_buffer_size()   # 512 or 1024 from ack, else 512 default
  file.read(chunk_size)
  cobs_encode(chunk + CRC8)  ────────▶  rurp_communication_read_data(buf, DATA_BUFFER_SIZE)
                                         (MAIN path, cap = DATA_BUFFER_SIZE, Phase 54)
```

### Key Flow: Two Acks for FW-probe CMD

When the host sends `CMD_FW_VERSION` (state=13), `init_programmer` fires at `firestarter.cpp:138`:
- Emits `MSG_OK_READY` (now with 2-byte `DATA_BUFFER_SIZE` param)

Then `fw_get_version` fires and emits:
- `MSG_OK_FW_VERSION` text line: `"OK: FW: 3.0.0b8:uno"` (2-field version only)

The host's `_probe_port` already handles this 2-ack sequence (lines 587-602 of `serial_comm.py`):
```python
pre_is_ok, _pre_msg = communicator.expect_ack()   # MSG_OK_READY — discard msg, but _decode_id_frame extracts buf_size
...
fw_is_ok, fw_msg = communicator.expect_ack()       # MSG_OK_FW_VERSION — parse version/board
```

The `_decode_id_frame` override intercepts the first ack (`MSG_OK_READY`) and sets
`communicator.firmware_max_chunk`.

For operation commands (non-FW-version probe), the flow at lines 655-661:
```python
communicator.send_json_command(command_to_send)
is_ok, msg = communicator.expect_ack()             # MSG_OK_READY — _decode_id_frame extracts buf_size
if is_ok:
    communicator.programmer_info = msg
```

After this, `_setup_operation` calls `_calculate_buffer_size()` which reads
`self.comm.firmware_max_chunk`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| u16 param encoding | Custom big-endian packer | `LOG_OK_ID_U16(MSG_OK_READY, DATA_BUFFER_SIZE)` + `rurp_log_id_u16` | Already implemented; correct MSB-first encoding verified by test_messages Unity suite |
| TOML parsing | Custom TOML reader | `codegen.py` + `tomllib` (stdlib, Python 3.11+) | Already the authoritative toolchain for catalog changes |
| messages.toml sync | Manual file copy | `tools/catalog/sync_to_subrepos.sh` | Enforces byte-identity; verifies the invariant in CI |
| Frame shape validation | Custom validator | `codegen.py --check` | Runs 10 rules including param-count ↔ format-specifier match |
| u16 extraction from bytes | struct | `struct.unpack(">H", params_bytes)` | Standard library; already used elsewhere in frame_parser.py |

---

## Common Pitfalls

### Pitfall 1: `bytes` param type conflicts with codegen Rule 9 (format specifier count)
**What goes wrong:** Developer uses `{ type = "bytes" }` in the catalog and also adds
a `%u` specifier to the format string. Rule 9 checks `non_bytes_count` (params that are
NOT `bytes` type) against specifier count. `bytes` params are excluded, so a format
with `%u` and `params = [{ type = "bytes" }]` fails Rule 9 (1 specifier, 0 non-bytes
params).
**How to avoid:** Keep `format = "Ready"` (zero `%` specifiers) with `params = [{ type = "bytes" }]`.
The `bytes` param contributes to the wire payload but has no printf representation.
[VERIFIED: codegen.py lines 289-300]

### Pitfall 2: Fixed-shape u16 approach breaks un-advertising firmware compat
**What goes wrong:** Developer uses `{ type = "u16" }` instead of `{ type = "bytes" }`.
The catalog sets `param_bytes=2`. The `decode_id_frame` shape check then rejects any
`MSG_OK_READY` frame with 0 param bytes (old firmware sends 0 params). The ack is
silently dropped, `expect_ack` times out.
**How to avoid:** Use `{ type = "bytes" }` which sets `param_bytes=-1` (variable),
skipping the shape check. The host manually extracts the `u16` if `len(params_bytes) == 2`.
[VERIFIED: codec.py line 229; codegen.py PARAM_TYPE_BYTES `"bytes": None`]

### Pitfall 3: _decode_id_frame override in `_probe_port` vs standalone calls
**What goes wrong:** The override is placed on the `SerialCommunicator` class, affecting
ALL calls (not just _probe_port). If `MSG_OK_READY` is emitted mid-operation
(e.g., dev_tools), the `firmware_max_chunk` attribute is overwritten by the later ack.
**Why it's OK:** `firmware_max_chunk` is written on EVERY `MSG_OK_READY` ack. In dev-tool
contexts, the capacity is the same constant (`DATA_BUFFER_SIZE`), so overwriting with the
same value is idempotent. In the operation flow, the write-setup ack sets it correctly
before `_calculate_buffer_size()` is called. [INFERRED: from code structure]

### Pitfall 4: Forgetting to update the FW-version probe test
**What goes wrong:** `test_serial_comm.py` lines 402-448 test that `firmware_max_chunk`
is parsed from the 4th field of the identity string. After Phase 55, the identity string
is 2-field; these tests will pass trivially (3- or 4-field string becomes
`["version", "board"]` or similar — depends on test input). However, the behavioral
contract tested (identity string carries maxchunk) is now wrong.
**How to avoid:** Remove the Phase 54 identity-string parse tests and replace with tests
that verify the `_decode_id_frame` override sets `firmware_max_chunk` from the ack bytes.

### Pitfall 5: Hardware_operations.cpp MSG_OK_READY carries wrong semantics
**What goes wrong:** The `hardware_operations.cpp:43` ack is for the VPP/VPE read-voltage
probe (`CMD_READ_VPP`, `CMD_READ_VPE`), not a write/verify operation. The host doesn't
call `_calculate_buffer_size()` for these commands. Emitting `DATA_BUFFER_SIZE` on this
ack is harmless but potentially confusing.
**Why it's OK per SC2:** SC2 requires "ALL `MSG_OK_READY` emit sites updated". The value
advertised is `DATA_BUFFER_SIZE` which is constant per board — correct in all contexts.
The host override reads it and stores it; even if a read-voltage command fires first,
`firmware_max_chunk` will be set to the correct value before any write operation.

### Pitfall 6: `firmware_max_chunk` is populated from FW-probe ack for the FW-probe command itself
**What goes wrong:** When `command_to_send` IS the `CMD_FW_VERSION` probe (the exempt
case, `exempt_cmds` line 584), the operation-setup ack at line 657 is the
`MSG_OK_READY` from `fw_get_version`'s `init_programmer`. The `_decode_id_frame`
override will set `firmware_max_chunk` correctly. But the FW probe's second ack
(`MSG_OK_FW_VERSION`) is a text-format message (not an id-frame) so the override
won't interfere. This path is safe. [VERIFIED: serial_comm.py lines 584-661 flow]

---

## Code Examples

### messages.toml change (MSG_OK_READY)
```toml
# meta-repo /workspaces/tools/catalog/messages.toml, lines 33-39
# BEFORE (Phase 54 state):
[[messages]]
id          = 0x01
name        = "MSG_OK_READY"
severity    = "OK"
format      = "Ready"
params      = []
wire_format = "id_frame"

# AFTER (Phase 55):
[[messages]]
id          = 0x01
name        = "MSG_OK_READY"
severity    = "OK"
format      = "Ready"
params      = [{ type = "bytes" }]
wire_format = "id_frame"
```

### FW_VERSION revert (firestarter.h)
```c
// firestarter.h lines 26-40 — BEFORE (Phase 54):
/* FW identity string: "<version>:<board>:<data_buffer_size>:<maxchunk>". ... */
#define FW_VERSION VERSION ":" RURP_BOARD_NAME ":" FS_STRINGIFY(DATA_BUFFER_SIZE) ":" FS_STRINGIFY(DATA_BUFFER_SIZE)

// AFTER (Phase 55 — pure version:board, capacity on MSG_OK_READY ack):
/* FW identity string: "<version>:<board>".
 * Buffer capacity (DATA_BUFFER_SIZE) is advertised as a u16 bytes param
 * on every MSG_OK_READY ack (Phase 55 / CAP-01). */
#define FW_VERSION VERSION ":" RURP_BOARD_NAME
```

### Firmware emit site update (all 4 sites, same pattern)
```c
// BEFORE:
LOG_OK_ID(MSG_OK_READY);

// AFTER:
LOG_OK_ID_U16(MSG_OK_READY, (uint16_t)DATA_BUFFER_SIZE);
```

### Host _decode_id_frame override (serial_comm.py — to be added to SerialCommunicator)
```python
import struct as _struct  # already imported at top of serial_comm.py

def _decode_id_frame(self, frame_len: int, body: bytes) -> Optional[LogMessage]:
    """Intercept MSG_OK_READY to extract buffer-capacity advertisement (Phase 55 CAP-01)."""
    result = codec.decode_id_frame(frame_len, body)
    if result is not None and result.id == MSG_OK_READY:
        # body: [id][params_bytes...][crc] — params_bytes is body[1:-1]
        params_bytes = body[1:-1]
        if len(params_bytes) == 2:
            # Firmware advertises DATA_BUFFER_SIZE as big-endian u16 bytes param.
            self.firmware_max_chunk = _struct.unpack(">H", params_bytes)[0]
        # else: un-advertising firmware (0 bytes) — firmware_max_chunk stays None/unchanged;
        # _calculate_buffer_size() will use the 512 safe default.
    return result
```

Note: `MSG_OK_READY = 0x01` is imported from `firestarter.messages` at the top of
`serial_comm.py`. Verify `from firestarter.messages import MSG_OK_READY` is present
(or use `0x01` directly if preferred).

### Host _calculate_buffer_size update (eprom_operations.py)
```python
def _calculate_buffer_size(self) -> int:
    # Phase 55 (CAP-01): read firmware-advertised DATA_BUFFER_SIZE from the
    # operation-setup MSG_OK_READY ack (bytes param, u16 big-endian).
    # When absent (un-advertising firmware or ack with no param), default to
    # 512 — the universally safe Uno floor. No FirmwareOutdatedError (reverses
    # Phase 54 D-05 lockstep-or-fail → safe default).
    max_chunk = (
        getattr(self.comm, "firmware_max_chunk", None) if self.comm else None
    )
    if max_chunk is not None and max_chunk >= 1:
        return max_chunk
    return 512  # CAP-01 safe Uno floor default
```

### Host parse revert: remove fw_fields[2]/[3] from _probe_port (serial_comm.py)
```python
# BEFORE (serial_comm.py lines 619-632):
fw_payload = fw_msg.split("FW:", 1)[-1].strip()
fw_fields = fw_payload.split(":")
if len(fw_fields) >= 3 and fw_fields[2].strip().isdigit():
    communicator.firmware_buffer_size = int(fw_fields[2].strip())
if len(fw_fields) >= 4 and fw_fields[3].strip().isdigit():
    communicator.firmware_max_chunk = int(fw_fields[3].strip())

# AFTER (Phase 55 — capacity now from MSG_OK_READY ack, not identity string):
# fw_payload = fw_msg.split("FW:", 1)[-1].strip()
# (only version and board extracted — existing code already does this for version check)
# Remove the fw_fields[2]/[3] block entirely.
```

---

## Validation Architecture

> `workflow.nyquist_validation` is absent from `.planning/config.json` — treated as enabled.

### Test Framework

| Property | Value |
|----------|-------|
| Firmware framework | Unity (PlatformIO native env) |
| Host framework | pytest |
| Firmware quick run | `pio test -e native` |
| Host quick run | `pytest tests/test_even_block.py tests/test_cap_01.py -x` (or `test_even_block.py` with updated tests) |
| Full suite (firmware) | `cd /workspaces/firestarter && pio test` |
| Full suite (host) | `cd /workspaces/firestarter_app && pytest --cov=firestarter --cov-fail-under=70` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| CAP-01 (SC1) | `FW_VERSION` is `<version>:<board>` only — no buf/maxchunk | Unit | `pio test -e native -f "*test_messages*"` | Extend existing |
| CAP-01 (SC2a) | `LOG_OK_ID_U16(MSG_OK_READY, DATA_BUFFER_SIZE)` emits 2-byte param correctly | Unit (firmware) | `pio test -e native -f "*test_messages*"` | New test case |
| CAP-01 (SC2b) | All 4 emit sites updated; drift gate passes | Drift gate | `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` | CI / manual |
| CAP-01 (SC3a) | Un-advertising ack (0 param bytes) → 512 default, no error | Unit (host) | `pytest tests/test_even_block.py::TestCapSafeDefault -x` | New class ❌ Wave 0 |
| CAP-01 (SC3b) | 2-byte ack → `firmware_max_chunk` set correctly | Unit (host) | `pytest tests/test_even_block.py::TestCapSafeDefault -x` | New tests ❌ Wave 0 |
| CAP-01 (SC4) | EVEN-01 preserved: chunks still 512/1024 (full buffer); Phase 52 round-trips green | Unit | `pio test -e native && pytest tests/test_frame_vectors.py -x` | Existing ✅ |
| CAP-01 (SC5) | messages.toml byte-identical across repos; parity gates green | Drift gate | `bash tools/catalog/sync_to_subrepos.sh && pio test -e native && pytest -x` | CI / manual |

### Sampling Rate

- **Per task commit:** `pio test -e native && pytest tests/ -x`
- **Per wave merge:** Full suite: `pio test && pytest --cov=firestarter --cov-fail-under=70`
- **Phase gate (SC1):** `firestarter fw` output verified as `<version>:<board>` only (manual)
- **Phase gate (SC5):** `bash tools/catalog/sync_to_subrepos.sh` exits 0 before `/gsd-verify-work`

### Wave 0 Gaps (RED tests needed before implementation)

- [ ] `firestarter_app/tests/test_even_block.py` or `test_cap_01.py` — add `TestCapSafeDefault`:
  - `test_absent_firmware_max_chunk_returns_512` (absent → 512, no raise) — currently the inverse is tested
  - `test_512_ok_ready_ack_via_decode_override` (2-byte body → firmware_max_chunk=512)
- [ ] Update `test_even_block.py::test_calculate_buffer_size_raises_without_max_chunk` — change `pytest.raises(FirmwareOutdatedError)` to `assert result == 512`
- [ ] Firmware Unity: extend `test_messages/test_rurp_log_id.cpp` with a test asserting `MSG_OK_READY` emits a frame with 2-byte params (the u16 `DATA_BUFFER_SIZE` value) — currently the test covers zero-param frames

*(If no Wave 0 gaps are preferred: implement the tests in Wave 1 alongside the implementation)*

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO / pio | Firmware build + tests | ✓ (used in Phases 49-54) | — | — |
| Python 3.11+ (for tomllib) | `codegen.py` | ✓ (devcontainer has 3.12) | 3.12.x | — |
| pytest | Host tests | ✓ (installed via `pip install -e '.[test]'`) | — | — |
| Uno + Leonardo bench hardware | SC1 on-wire verify | operator-gated | — | Software-only tests cover SC2-SC5; wire verify is Phase 53 scope |

---

## Security Domain

No new attack surface. MSG_OK_READY with a `bytes` param:
- The `bytes` param is 0 or 2 bytes, from a trusted endpoint (the firmware).
- The host extracts the `u16` only if `len(params_bytes) == 2`; otherwise defaults to 512.
- The `struct.unpack(">H", ...)` call is bounded-safe (2 bytes input, 2 bytes output).
- No user-controlled input reaches the param extraction path.

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | yes (marginal) | `len(params_bytes) == 2` guard before `struct.unpack` |
| V6 Cryptography | no (phase does not change CRC) | CRC8-CCITT unchanged (D-05) |
| V4 Access Control | no | No authentication changes |

---

## State of the Art

| Old Approach (Phase 54) | Phase 55 Approach | When Changed | Impact |
|-------------------------|-------------------|--------------|--------|
| `<version>:<board>:<buf>:<maxchunk>` in identity string | `<version>:<board>` — pure version only | Phase 55 | Version string is clean; capacity is on the operation ack |
| `FirmwareOutdatedError` when `<maxchunk>` absent | 512 safe default | Phase 55 | Un-advertising firmware degrades gracefully |
| Capacity read once at FW probe time | Capacity read per operation (from OK:Ready ack) | Phase 55 | More accurate — firmware can in future vary capacity per operation type |
| `firmware_max_chunk` from identity field 3 | `firmware_max_chunk` from MSG_OK_READY bytes param | Phase 55 | Decouples version from transport capability |

**Deprecated/outdated post-Phase-55:**
- The `fw_fields[2]`/`fw_fields[3]` parse block in `serial_comm.py` `_probe_port` — removed
- The Phase 54 D-05 decision "no fallback, lockstep or fail" — replaced by CAP-01 safe default
- The `firmware_buffer_size` attribute on `SerialCommunicator` — was a Phase 53 carry; can be removed
  (or left with deprecation comment since nothing reads it after Phase 55)

---

## Open Questions (RESOLVED)

1. **Should the format string for `MSG_OK_READY` with `bytes` param be `"Ready"` or something more descriptive?**
   - **RESOLVED: Keep `"Ready"`** (planner decision, implemented in Plan 55-01).
   - What we know: `format = "Ready"` with `params = [{ type = "bytes" }]` passes codegen Rule 9 (bytes excluded from specifier count). The rendered text is always `"Ready"` regardless of the param value.
   - Recommendation followed: Keep `"Ready"` for minimal diff. Verbose buffer-size visibility, if wanted later, goes to a separate debug log — out of scope for Phase 55.

2. **Should `firmware_buffer_size` (the Phase 53 attribute, currently set from `fw_fields[2]`) be removed?**
   - **RESOLVED: Executor-time grep-gated removal** (Plan 55-03 Task 2 carries the decision path).
   - What we know: After Phase 55, the identity string is 2-field — `fw_fields[2]` no longer exists. `firmware_buffer_size` is never read (only `firmware_max_chunk` is used by `_calculate_buffer_size`). `conftest.py` line 146 sets it to `None` in the mock communicator.
   - Resolution: Plan 55-03 Task 2 greps for references; if none, removes the attribute; if present in tests, updates them.

3. **Does the `_decode_id_frame` override on `SerialCommunicator` conflict with the GATE-1.8d ring-fence?**
   - **RESOLVED: No conflict** — verified.
   - What we know: The ring-fence (lines 250-259 of `serial_comm.py`) applies to `_read_and_parse_lines` body — "structural-only changes to the signature are OK; any change to the byte-by-byte read loop, magic-preamble dispatch, frame-length read, or timeout reset semantics MUST be flagged." Overriding `_decode_id_frame` is explicitly NOT protected by this note — the GATE-1.8d fence is on `_read_and_parse_lines`.
   - Conclusion: The `_decode_id_frame` override is safe and within the extension point pattern already established by `FaultInjectingSerialCommunicator`. No conflict with GATE-1.8d.
   [VERIFIED: serial_comm.py lines 250-259]

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The `bytes` param type with `len == 0` from old firmware correctly passes through `decode_id_frame` (the shape check is skipped, decode returns `values = [b""]`) | §Codegen Catalog §1 | If old firmware sends an id-frame with `body = [0x01, crc]` (1 id + 1 crc = frame_len=2, params_bytes=b""), the shape check at codec.py:229 is skipped (param_bytes=-1), `_decode_param("bytes", b"", 0)` returns `(b"", 0)`, values=[b""], result=LogMessage with text="Ready". This is safe. [INFERRED from code path — not bench-verified] |
| A2 | The `_decode_id_frame` instance method override pattern on `SerialCommunicator` (not a subclass) works in Python without affecting other instances | §Host Read Point | Python instance method override via `types.MethodType` or direct `self._decode_id_frame = ...` would work. More cleanly, it should be an override IN the class body (not per-instance). The planner must decide: add it to the SerialCommunicator class body or create a subclass. [ASSUMED — planner decision] |

**All other claims in this research were verified by direct source code reading on the `v1.10-serial-transport-hardening` branch. No web search was used.**

---

## Sources

### Primary (HIGH confidence — verified from source)

- `/workspaces/tools/catalog/messages.toml` lines 33-39 — `MSG_OK_READY` current definition (params=[], wire_format=id_frame)
- `/workspaces/firestarter/tools/catalog/codegen.py` — codegen rules 1-10; `bytes` param type behavior; format-specifier count validation
- `/workspaces/firestarter/include/messages.h` — generated artifact; MSG_OK_READY=0x01 confirmed
- `/workspaces/firestarter/include/firestarter.h` lines 16-40 — `DATA_BUFFER_SIZE`, `FW_VERSION` macro (current 4-field form)
- `/workspaces/firestarter/include/logging_id.h` lines 123-128 — `LOG_OK_ID`, `LOG_OK_ID_U16` macros
- `/workspaces/firestarter/src/boards/rurp_serial_utils.cpp` lines 484-489 — `rurp_log_id_u16` implementation
- `/workspaces/firestarter/src/firestarter.cpp` line 142 — MSG_OK_READY emit site (operation setup)
- `/workspaces/firestarter/src/hardware_operations.cpp` line 43 — MSG_OK_READY emit site (VPP/VPE probe)
- `/workspaces/firestarter/src/dev_tools.cpp` lines 107, 153 — MSG_OK_READY emit sites (dev-tool acks)
- `/workspaces/firestarter_app/firestarter/serial_comm.py` lines 118-123, 562-674 — `firmware_max_chunk`, `_probe_port`, identity-string parse
- `/workspaces/firestarter_app/firestarter/eprom_operations.py` lines 163-228 — `_calculate_buffer_size`, `_setup_operation`, `_operation_context`
- `/workspaces/firestarter_app/firestarter/codec.py` lines 171-282 — `decode_id_frame`, shape check, bytes-param handling
- `/workspaces/firestarter_app/firestarter/frame_parser.py` line 131-182 — `_decode_param` for `bytes` type
- `/workspaces/firestarter_app/tests/test_even_block.py` — Phase 54 tests that must be updated
- `/workspaces/firestarter_app/tests/test_serial_comm.py` lines 397-448 — Phase 54 identity-string parse tests
- `/workspaces/tools/catalog/sync_to_subrepos.sh` — sync procedure
- `/workspaces/firestarter/.github/workflows/build.yml` lines 46-80 — firmware CI drift gate
- `/workspaces/firestarter_app/.github/workflows/ci.yml` lines 1-54 — host CI drift gate
- `pio run -e uno` output on branch — Uno RAM after Phase 54: 1552/2048 bytes (496 B free)

### Secondary (MEDIUM confidence)
- None — all claims verified from source.

---

## Metadata

**Confidence breakdown:**
- Codegen catalog mechanics: HIGH — rules verified from codegen.py source
- MSG_OK_READY emit sites: HIGH — grep-confirmed all 4 sites with file:line
- FW_VERSION revert: HIGH — exact macro at firestarter.h:40 verified
- Host read point: HIGH — _probe_port flow verified; _decode_id_frame override pattern verified
- Safe default: HIGH — current code path traced; 512 is correct Uno floor
- RAM impact: HIGH — pio run -e uno measured after Phase 54; analysis confirmed

**Research date:** 2026-06-04
**Valid until:** 2026-07-04 (stable — pure code analysis, no external dependencies)
