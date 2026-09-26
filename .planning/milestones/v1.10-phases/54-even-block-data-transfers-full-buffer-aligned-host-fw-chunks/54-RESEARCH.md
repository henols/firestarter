# Phase 54: Even-Block Data Transfers (full-buffer-aligned host→fw chunks) — Research

**Researched:** 2026-06-04
**Domain:** Firmware COBS decode-buffer cap / host chunk-sizing / identity-string negotiation
**Confidence:** HIGH (all findings verified directly from source)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01**: Mechanism is research's call — evaluate candidates (a) data-path NUL-skip, (b) grow
  decode buffer, (c) CRC8-out-of-band; RESEARCH.md scores + recommends, planner locks.
- **D-02**: Breaking the frame contract is PERMITTED for Phase 54. Operator (2026-06-04) explicitly
  relaxed the Phase 49/52 "frozen contract" status for this phase.
- **D-03**: Optimise for "as dynamic as possible." No hardcoded per-board constants; full-block
  size derived from firmware-advertised capacity at runtime.
- **D-04**: Firmware advertises an explicit effective-decode-capacity field. Extend the identity
  string (today `"<ver>:<board>:<DATA_BUFFER_SIZE>"`) with a max-data-chunk field; host uses
  exactly what firmware reports. The existing `_calculate_buffer_size()` `−2` reduction is
  removed in favour of the advertised value.
- **D-05**: Beta lockstep, no mixed-version interop. Host may assume the new capacity field is
  present. No fallback branch, no graceful `buf−2` degrade.
- **D-06**: Verify leg moves with the write leg. Both legs go through the same chunk-sizing path.
- **D-07**: Pin a full-buffer round-trip regression (SC4). Extend the vendored `frame-vectors`
  golden-vector corpus with full-buffer-as-data-CHUNK vectors at the new even size. Include a
  no-remainder/division assertion that 65536 ÷ block = whole blocks.
- **D-08**: RAM report is a hard phase-close gate (SC3). Capture `pio run -e uno` (and uno328pb)
  RAM reports; assert under the ~545 B free-RAM ceiling.

### Claude's Discretion

- **D-09**: Exact regression-test shape and home (extend `frame-vectors` corpus vs dedicated
  EVEN test vs both) — operator left this to Claude.
- Exact identity-string capacity-field name and format (D-04).
- Internal decoder/encoder naming and precise decode-in-place cap parameterisation for the
  chosen mechanism (D-01).
- Whether to record measured on-wire frame sizes as quantitative evidence for SC1.

### Deferred Ideas (OUT OF SCOPE)

- **WR-01 — frame-level deadline on the firmware COBS decoder byte-wait**. Phase 54 edits the
  same decoder, making it the natural future home, but it is distinct and out of EVEN scope.
- CRC8-out-of-band as a permanent contract beyond what is needed for even blocks — only adopt
  if D-01 research picks it on merits.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| EVEN-01 | Host→fw write/verify data blocks transfer in full even buffer-sized blocks (512 on Uno/uno328pb, 1024 on Leonardo) with no `buffer−2` reduction, by decoupling the on-wire data-block size from the firmware COBS decode-buffer cap via the mechanism chosen in D-01; the firmware advertises the effective decode capacity in the identity string so the host sizes chunks dynamically per-board with no hardcoded constant (D-03/D-04). | D-01 mechanism analysis (§ below), D-04 identity field extension, D-06 write+verify coverage proof. |

*Note: REQUIREMENTS.md for v1.10 currently has no Phase 54 row (it records EVEN requirement as TBD). EVEN-01 above is proposed wording for the planner to add under the v1.10 Requirements section.*
</phase_requirements>

---

## Summary

Phase 54 removes the last `−2` byte handicap on host→fw write/verify chunks. Today
`_calculate_buffer_size()` returns `fw_buf − 2` (510 on Uno, 1022 on Leonardo) because the
firmware's COBS decoder commits at most `DATA_BUFFER_SIZE − 1` bytes (the CR-01 NUL-slot
reservation) and the payload's trailing CRC8 byte occupies one additional slot. A full-chip
write of 65536 bytes therefore leaves a 256-byte remainder chunk (128×510 + 256) — one extra
firmware round trip. The goal is 128×512 = 65536 exactly, no remainder.

The three candidates for loosening the cap were evaluated by reading the actual code. The
data-path NUL-skip (Candidate A) is safe and recommended: on the MAIN/write-receive path,
`data_buffer` is consumed byte-by-byte via `handle->data_buffer[i]` index access — never as
a C string — so the NUL-terminator slot is genuinely unnecessary for that path. The `−1`
guard is needed only on the CMD_IDLE/JSON-command path where `data_buffer[n] = '\0'` is
written and `jsmn_parse` receives the buffer as a string. The two paths use the same decoder
function (`rurp_communication_read_data`) but are called from distinct sites: `firestarter.cpp`
line 176 (CMD_IDLE, requires NUL) and `operation_utils.cpp` line 164 (MAIN data, does not).
A data-path-only cap of `DATA_BUFFER_SIZE` (instead of `DATA_BUFFER_SIZE − 1`) on the MAIN
path unlocks the full block with zero additional RAM.

The identity-string extension (D-04) makes the effective decode capacity explicit on the wire:
`"<ver>:<board>:<buf>:<maxchunk>"` — where `<maxchunk>` is the value the host should use as
chunk size, advertised by firmware, eliminating any host-side arithmetic. The host's
`_probe_port` already splits on `:` and reads `fw_fields[2]`; adding `fw_fields[3]` is a
minimal change. Both write and verify already go through `_main_phase_send_data` (confirmed
at lines 1140 and 1176 of `eprom_operations.py`).

**Primary recommendation:** Implement Candidate A (data-path NUL-skip, zero RAM growth) as
described below, extend the identity string with `:<maxchunk>`, regenerate the golden-vector
corpus with 512- and 1024-byte data-chunk vectors, and close with a hard Uno RAM gate.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Decode-cap loosening (EVEN-01) | Firmware / MCU | — | The cap is enforced inside `rurp_communication_read_data` on the AVR; the host can only request what the firmware permits |
| Chunk-size advertisement (D-04) | Firmware / MCU | Host parses | FW identity string carries `DATA_BUFFER_SIZE` today; extend with `<maxchunk>` field; host is the consumer |
| Chunk-size calculation (host) | Host Python | — | `_calculate_buffer_size()` in `eprom_operations.py` derives chunk from the advertised `<maxchunk>`; replaces `fw_buf − 2` arithmetic |
| Regression pinning (D-07) | Both repos (lockstep) | CI drift gate | `frame-vectors.toml` vendored byte-identical in both repos; `codegen_vectors.py` drift gate catches divergence |
| RAM gate (D-08) | Firmware build system | — | `pio run -e uno` (and uno328pb) RAM report; hard close gate |

---

## D-01 Mechanism Scoring: Recommendation

### Candidate A — Data-Path NUL-Skip (zero RAM growth)

**Mechanism:** Lift the `DATA_BUFFER_SIZE − 1` overflow cap ONLY on the MAIN/write-receive call
site. The PUSH macro in `rurp_communication_read_data` today guards:

```c
// rurp_serial_utils.cpp line 147
if (out >= DATA_BUFFER_SIZE - 1) { _drain_to_delimiter(); return -2; }
```

This cap is the same for all callers. To make it data-path-specific, the function needs a
parameter (e.g. `int cap`) that the CMD_IDLE caller passes as `DATA_BUFFER_SIZE − 1` and
the MAIN data caller passes as `DATA_BUFFER_SIZE`. The PUSH macro uses `cap` instead of the
hardcoded `DATA_BUFFER_SIZE − 1`.

**Is `data_buffer` ever read as a NUL-terminated string on the write-receive (MAIN) path?**

Code trace (VERIFIED):
- `operation_utils.cpp` line 164: `int res = rurp_communication_read_data(handle->data_buffer);` — this is the MAIN path call under case `'#'`
- After return, line 169: `handle->data_size = res;` and line 170: `return OP_MSG_DATA;` — no NUL write, no string use
- The caller path leads to `eprom_operations.cpp` line 89-95 → `OP_MSG_DATA` branch → `op_execute_function(handle->firestarter_operation_main, handle)` at line 101
- The `firestarter_operation_main` functions (`memory.cpp` write path lines 224-226, `eprom.cpp` write path line 122, `eeprom_28c.cpp` line 122, `flash_intel.cpp` line 136, `flash_type_3.cpp` line 99) ALL consume `handle->data_buffer[i]` via integer index — no `strlen`, `strcmp`, `atoi`, `printf %s`, or implicit NUL-terminator use

**Conclusion: `data_buffer` is NEVER read as a NUL-terminated C string on the write-receive path.** Candidate A is safe. [VERIFIED: source trace]

**Comparison with the CMD_IDLE path (why the NUL is required there):**
- `firestarter.cpp` line 176: `int n = rurp_communication_read_data(handle.data_buffer);`
- Line 185: `handle.data_buffer[n] = '\0';` — explicit NUL write, requires `n < DATA_BUFFER_SIZE`
- Line 59: `jsmn_parse(&parser, handle->data_buffer, handle->data_size, ...)` — jsmn reads length-bounded, but the NUL is also written for safety
- Line 68, 77, 98: `json_get_cmd`, `json_parse`, `json_parse_config` all receive `handle->data_buffer` as a C string pointer

So: the NUL-slot reservation is load-bearing on the CMD_IDLE path and irrelevant on the MAIN path. The fix is to parameterise the cap. [VERIFIED: source trace]

**RAM cost:** Zero. No new buffers. The only change is a `int cap` parameter replacing the
hardcoded `DATA_BUFFER_SIZE − 1` literal in the PUSH macro. Stack impact: +2 bytes (one
additional function parameter in a register or on the stack depending on the ABI — below
measurement noise for the RAM gate). [VERIFIED: code inspection]

**Scoring:**
| Criterion | Score | Notes |
|-----------|-------|-------|
| RAM cost | A+ (0 growth) | Zero new heap/stack; cap is a parameter |
| Contract/diff stability | A (minimal) | One function signature change + one param at each of 2 call sites; command/JSON path unchanged |
| Dynamism (D-03) | A | The `maxchunk` advertisement makes the host fully dynamic; no per-board constant anywhere |
| Risk | Low | The safety proof is conclusive from the code trace above |

**Recommended.** [VERIFIED: source trace]

---

### Candidate B — Grow the Decode Buffer

**Mechanism:** Increase `DATA_BUFFER_SIZE` from 512 to 514 (or `DATA_BUFFER_SIZE + 2`) to
give the decoder room for full block + CRC8 + NUL at the existing cap of `DATA_BUFFER_SIZE − 1`.

**RAM cost:** `data_buffer` is the dominant consumer of the Uno's 2 KB SRAM. The Phase 50
RAM baseline is 1503/2048 bytes used, leaving 545 B free. [VERIFIED: STATE.md line 93]

Growing `DATA_BUFFER_SIZE` by 2 bytes costs at minimum 2 bytes of SRAM (the array), but
the struct also carries `data_size` (u32, 4 bytes) and other fields, so the struct's total
size grows by 2 bytes = 2 bytes net increase.

2 bytes is well within the 545 B ceiling; the immediate RAM impact is negligible. However:
- `CMD_FRAME_MAX` is defined as `DATA_BUFFER_SIZE` (`firestarter.h` line 24). Bumping
  `DATA_BUFFER_SIZE` to 514 changes `CMD_FRAME_MAX` to 514, which breaks parity with
  `constants.py CMD_FRAME_MAX = 512` and requires a constants parity update.
- More critically, `DATA_BUFFER_SIZE` = 514 means the golden vectors (which assert on
  512-byte data blocks) would need to be updated to reflect a 514-byte decode capacity, but
  the useful chunk is still 512 — the 2-byte headroom is artifice. The semantics become
  confusing: the buffer is 514 but the "full block" is 512.
- On Leonardo `DATA_BUFFER_SIZE = 1024` would become 1026, same confusion pattern.
- The advertisement becomes ambiguous: `<DATA_BUFFER_SIZE>` would be 514 but maxchunk = 512.

**Scoring:**
| Criterion | Score | Notes |
|-----------|-------|-------|
| RAM cost | B (tiny but non-zero) | 2 bytes growth |
| Contract/diff stability | C (confusing) | `DATA_BUFFER_SIZE` ≠ block size; constants.py parity breaks; vectors need update |
| Dynamism (D-03) | C | Forces a disconnect between buffer size and usable chunk |
| Risk | Low | Fits RAM ceiling |

**Not recommended.** The confusion between `DATA_BUFFER_SIZE` (514) and `maxchunk` (512)
makes D-04 harder to implement cleanly. Candidate A achieves the same goal without this.

---

### Candidate C — CRC8 Out-of-Band

**Mechanism:** Remove the CRC8 byte from inside the COBS-encoded stream and carry it as a
separate trailer byte after the `0x00` delimiter. The decoder would read: COBS-body + 0x00 +
CRC8_byte. Or alternatively, prefix it before the COBS body.

**Frame contract change:** This changes the Phase 49/52 frozen frame contract. Per D-02, this
is permitted — but what is the blast radius?

- `rurp_serial_utils.cpp` encoder (`rurp_communication_write`) currently appends CRC8 inside
  the COBS stream. Removing it requires emitting one extra byte after the `0x00` delimiter.
- `rurp_communication_read_data` currently uses the 1-byte lookahead (`last_byte`) to hold
  the CRC8 — this is architecturally central to the zero-second-buffer claim. Making CRC8
  out-of-band removes this lookahead mechanism entirely.
- `frame_parser.py` `cobs_encode` appends CRC8 before encoding; the call site in
  `_main_phase_send_data` would need to separate the CRC8 append.
- All 12 vectors in `frame-vectors.toml` embed CRC8 as the last pre-delimiter byte.
  Every single vector's `frame_hex` changes. Both repos' generated `frame_vectors.h` and
  `frame_vectors.py` regenerate.
- The command path (`send_json_command`) also currently appends CRC8 inside the COBS frame.
  That would need to change too, or be left inconsistent with the data path.
- The Phase 52 `test_frame_vectors` Unity suite and `test_frame_vectors.py` pytest suite
  both need updating.

**Does it solve the sizing problem?** Yes. With CRC8 out-of-band, the COBS-encoded payload
is exactly `DATA_BUFFER_SIZE` bytes of raw data; the CRC8 is a trailer. The decoder can use
the full `DATA_BUFFER_SIZE` committed-byte budget for payload. Zero additional RAM.

**But:** The diff blast radius is large (all vectors, both encoders, both decoders, both test
suites, command path symmetry question) and the problem it solves is already solved by
Candidate A with zero blast radius. D-02 permits the contract break but the operator's "weigh
on merits" instruction applies — there is no merit to the extra disruption when Candidate A
achieves the same goal cleanly.

**Scoring:**
| Criterion | Score | Notes |
|-----------|-------|-------|
| RAM cost | A+ (0 growth) | Equivalent to A |
| Contract/diff stability | D (large blast) | All 12 vectors change; both encoders; both decoders; both test suites; command-path symmetry question |
| Dynamism (D-03) | A | Equivalent |
| Risk | Medium | More code churn = more regression surface |

**Not recommended.** Achieves the same goal as Candidate A with far more disruption.

---

## Recommended Mechanism: Candidate A

**Parameterise the overflow cap in `rurp_communication_read_data`.** Change the signature to:

```c
// firestarter/src/boards/rurp_serial_utils.h  (or rurp_serial_utils.cpp)
int rurp_communication_read_data(char* buffer, size_t cap);
//   cap = DATA_BUFFER_SIZE - 1  on the CMD_IDLE / JSON-command call (firestarter.cpp:171)
//   cap = DATA_BUFFER_SIZE      on the MAIN / write-receive call (operation_utils.cpp:173)
```

The PUSH macro uses `cap` instead of the hardcoded `DATA_BUFFER_SIZE - 1`:

```c
#define PUSH(b_)                                \
    do {                                        \
        if (has_last) {                         \
            if (out >= cap) {                   \  // <-- was DATA_BUFFER_SIZE - 1
                _drain_to_delimiter();          \
                return -2;                      \
            }                                   \
            buffer[out++] = (char)last_byte;    \
        }                                       \
        last_byte = (b_);                       \
        has_last = true;                        \
    } while (0)
```

**Call site changes (firmware only):**

1. `firestarter.cpp` line 176:
   `int n = rurp_communication_read_data(handle.data_buffer, DATA_BUFFER_SIZE - 1);`
   (CMD_IDLE path — preserves the NUL-slot; `data_buffer[n] = '\0'` at line 185 remains in-bounds)

2. `operation_utils.cpp` line 164:
   `int res = rurp_communication_read_data(handle->data_buffer, DATA_BUFFER_SIZE);`
   (MAIN path — full block; no NUL write follows; VERIFIED safe above)

The host `_calculate_buffer_size()` removes the `fw_buf − 2` reduction and reads the new
`<maxchunk>` field from the identity string instead (D-04).

---

## D-04 Identity-String Extension

### Current wire format (VERIFIED: firestarter.h line 35)

```c
#define FW_VERSION VERSION ":" RURP_BOARD_NAME ":" FS_STRINGIFY(DATA_BUFFER_SIZE)
// emits e.g. "3.0.0b8:uno:512" or "3.0.0b8:leonardo:1024"
```

### Proposed extension

```c
#define FW_VERSION VERSION ":" RURP_BOARD_NAME ":" FS_STRINGIFY(DATA_BUFFER_SIZE) ":" FS_STRINGIFY(DATA_BUFFER_SIZE)
// emits "3.0.0b8:uno:512:512" or "3.0.0b8:leonardo:1024:1024"
```

**Field name:** `<maxchunk>` — the exact number of raw payload bytes the firmware can decode in
one call on the MAIN/write-receive path. After the Candidate A change: `maxchunk == DATA_BUFFER_SIZE`.

**Why the same value as `DATA_BUFFER_SIZE`?** After the Candidate A cap change, the MAIN path
cap is `DATA_BUFFER_SIZE` exactly. The identity string already carries `DATA_BUFFER_SIZE` in
field 3 (index 2). Field 4 (index 3) carries `maxchunk`, which equals `DATA_BUFFER_SIZE`.
This seems redundant but makes the contract future-proof: if a future change makes
`maxchunk ≠ DATA_BUFFER_SIZE` (e.g. a version where CMD_FRAME_MAX needs its own range), the
host reads `maxchunk` directly and has no arithmetic to do.

**Alternative (simpler):** Since `maxchunk == DATA_BUFFER_SIZE` post-Phase 54, the host could
re-derive it from `fw_fields[2]` without a separate field. However D-04 explicitly says
"firmware advertises an explicit effective-decode-capacity field" and "no hardcoded per-board
constant". A dedicated field makes the contract explicit and eliminates the `− 2` from the
host side entirely. The two-field approach is the correct implementation of D-04.

**Host parsing (VERIFIED: serial_comm.py lines 619-624)**

```python
# Existing:
fw_payload = fw_msg.split("FW:", 1)[-1].strip()
fw_fields = fw_payload.split(":")
if len(fw_fields) >= 3 and fw_fields[2].strip().isdigit():
    communicator.firmware_buffer_size = int(fw_fields[2].strip())

# Extended (add after firmware_buffer_size capture):
if len(fw_fields) >= 4 and fw_fields[3].strip().isdigit():
    communicator.firmware_max_chunk = int(fw_fields[3].strip())
```

Add `self.firmware_max_chunk: Optional[int] = None` to `SerialCommunicator.__init__` (near
line 118 where `firmware_buffer_size` is declared).

**`_calculate_buffer_size()` replacement (VERIFIED: eprom_operations.py lines 163-179)**

```python
def _calculate_buffer_size(self) -> int:
    # D-04: host reads firmware-advertised maxchunk field (4th ':' field of
    # "<ver>:<board>:<buf>:<maxchunk>") — no arithmetic, no per-board constant.
    # D-05: no fallback; host assumes new firmware with the maxchunk field.
    max_chunk = getattr(self.comm, "firmware_max_chunk", None) if self.comm else None
    if max_chunk is not None and max_chunk >= 1:
        return max_chunk
    raise FirmwareOutdatedError(
        "Firmware does not advertise a max-chunk capacity field. "
        "Please upgrade the firmware using 'firestarter fw --install'."
    )
```

Note: D-05 says "no fallback branch, no graceful `buf−2` degrade" — the error raise is
correct. The existing `MAX_DATA_CHUNK` constant in `constants.py` becomes unused (leave in
place with a comment, or remove — planner discretion).

**Backward-compatible parsing:** The existing `split(":")` approach already tolerates trailing
fields — hosts that only know 3 fields simply don't read the 4th. Since D-05 requires no
old-host support, this tolerance is a non-issue, but it confirms no fragility is introduced.

---

## D-06: Write and Verify Path Confirmation

Both `write_eprom` and `verify_eprom` call `_main_phase_send_data` and obtain `buf_size`
from `_calculate_buffer_size()` via `_setup_operation()`. [VERIFIED: eprom_operations.py
lines 1125-1143 and 1161-1179]

```python
# write_eprom (line 1140)
main_phase_handler=self._main_phase_send_data,
input_file_path=input_file_path,
buffer_size=buf_size,   # <-- comes from _calculate_buffer_size()

# verify_eprom (line 1176)
main_phase_handler=self._main_phase_send_data,
input_file_path=input_file_path,
buffer_size=buf_size,   # <-- same path
```

`_main_phase_send_data` uses `buffer_size` directly at line 388:
`data_chunk = file_handle.read(buffer_size)` — then `cobs_encode(data_chunk + bytes([crc]))`.

One mechanism covers both operations. No separate verify-specific chunk path exists.

---

## D-07: Regression Mechanism

### Existing corpus (VERIFIED: frame-vectors.toml)

The golden-vector catalog already includes:
- `VEC_512_ALL_FF` (id=0x09): 512-byte all-0xFF payload → frame_len=517
- `VEC_512_ALL_ZERO` (id=0x0A): 512-byte all-0x00 payload → frame_len=515
- `VEC_1024_ALL_FF` (id=0x0B): 1024-byte all-0xFF payload → frame_len=1031
- `VEC_1024_ALL_ZERO` (id=0x0C): 1024-byte all-0x00 payload → frame_len=1027

However, these vectors were created under the Phase 52 context where `DATA_BUFFER_SIZE − 1`
was the decode cap. Critically, these 512-byte and 1024-byte vectors CURRENTLY fail the
firmware decoder (it returns -2 for them) because the cap is `DATA_BUFFER_SIZE − 1 = 511`.
After Phase 54 changes the MAIN-path cap to `DATA_BUFFER_SIZE = 512`, these vectors become
valid for the MAIN path.

**Phase 54 change to corpus:** The existing 512/1024 vectors serve as the new even-block
regression vectors for Phase 54 — no additional vectors need to be added. What changes is
the decode assertion in the firmware Unity test:

- **Before Phase 54:** `test_frame_vectors` (Unity) likely has a note or skip for the 512/1024
  decode direction under the MAIN path (or tests the CMD_IDLE cap = 511 path).
- **After Phase 54:** the 512/1024 vectors decode successfully under the MAIN path (cap=512/1024).

The recommendation (D-09) is:
1. In `firestarter/test/native/avr/test_frame_vectors/`: add test cases that call
   `rurp_communication_read_data(buffer, DATA_BUFFER_SIZE)` (the new MAIN-path signature)
   against the VEC_512_* vectors and assert successful decode.
2. Ensure the CMD_IDLE path tests still call
   `rurp_communication_read_data(buffer, DATA_BUFFER_SIZE - 1)` and the 512-byte decode
   returns -2 (confirming the CMD_IDLE cap is unchanged).
3. Add a small assertion in both repos:
   ```python
   # test_even_block.py (or inline in test_frame_vectors.py)
   assert 65536 % 512 == 0, "Uno: 65536-byte chip divides evenly into 512-byte blocks"
   assert 65536 % 1024 == 0, "Leonardo: 65536-byte chip divides evenly into 1024-byte blocks"
   ```
   and the equivalent C assertion:
   ```c
   TEST_ASSERT_EQUAL_UINT32(0, 65536 % DATA_BUFFER_SIZE);  // no-remainder assertion
   ```

**Drift gate:** The `frame-vectors.toml` is not modified (no new vectors needed — existing
512/1024 vectors suffice). The `codegen_vectors.py` `--check` drift gate therefore stays clean
without a regen step, since the TOML is unchanged and the generated `frame_vectors.h` /
`frame_vectors.py` are unchanged.

If the planner decides to add new explicitly-named "even-block data-chunk" vectors (e.g. to
document the new decode capacity semantically), the drift gate is: regenerate
`frame_vectors.h` and `frame_vectors.py` in both repos and `git diff --exit-code` confirms
byte-identity.

---

## D-08: RAM Gate Specification

**Command (Uno):**
```bash
cd /workspaces/firestarter && pio run -e uno 2>&1 | grep -E "RAM|SRAM|bytes"
```

**Command (uno328pb):**
```bash
cd /workspaces/firestarter && pio run -e uno328pb 2>&1 | grep -E "RAM|SRAM|bytes"
```

**Assert:** `DATA used` ≤ 1503 bytes (the Phase 50 baseline was 1503/2048 = 73.4% SRAM used,
leaving 545 B free). Candidate A adds 0 new bytes; the function parameter `cap` lives in a
register or 2-byte stack slot that is already accounted for in the call frame. The gate is:

**PASS criterion:** `DATA used ≤ 1503` on both Uno and uno328pb envs. Because Candidate A
is zero-growth, the gate should pass trivially, but it must still be run as a hard close
gate per D-08.

**Leonardo:** No explicit gate required (2.5 KB SRAM; 1024-byte buffer; well within limits),
but the build should remain clean.

---

## Standard Stack

No new external packages. This phase modifies existing files in both sub-repos. No new
dependencies are introduced.

### Files Modified

**Firmware (`firestarter/`):**

| File | Change |
|------|--------|
| `src/boards/rurp_serial_utils.h` | Add `size_t cap` parameter to `rurp_communication_read_data` declaration |
| `src/boards/rurp_serial_utils.cpp` | Add `cap` parameter to `rurp_communication_read_data`; replace `DATA_BUFFER_SIZE − 1` literal in PUSH macro with `cap` |
| `src/firestarter.cpp` line 176 | Pass `DATA_BUFFER_SIZE - 1` as `cap` (CMD_IDLE path) |
| `src/operation_utils.cpp` line 164 | Pass `DATA_BUFFER_SIZE` as `cap` (MAIN path) |
| `include/firestarter.h` line 35 | Extend `FW_VERSION` macro with `":" FS_STRINGIFY(DATA_BUFFER_SIZE)` for the `<maxchunk>` field |
| `test/native/avr/test_frame_vectors/` | Add MAIN-path decode assertions for VEC_512_*/VEC_1024_*; add CMD_IDLE-path overflow assertion (512-byte block returns -2); add no-remainder assertion |

**Host (`firestarter_app/`):**

| File | Change |
|------|--------|
| `firestarter/serial_comm.py` | Add `self.firmware_max_chunk: Optional[int] = None`; extend `_probe_port` to parse `fw_fields[3]` → `communicator.firmware_max_chunk` |
| `firestarter/eprom_operations.py` | Replace `_calculate_buffer_size()` body: remove `fw_buf − 2`; read `firmware_max_chunk`; raise on missing field (D-05) |
| `firestarter/constants.py` | Mark `MAX_DATA_CHUNK` as obsolete (add comment); leave in place to avoid breaking any external reference |
| `test/test_even_block.py` (new) or `test/test_frame_vectors.py` (extended) | No-remainder assertion; `firmware_max_chunk` parse test |

---

## Architecture Patterns

### System Architecture Diagram

```
Host (Python)                                Firmware (AVR)
──────────────────────────────────────────────────────────────────

CMD_FW_VERSION probe
 └─ send_json_command({"state": 13})  ──COBS+CRC8──▶  rurp_communication_read_data(buf, CAP=511)
                                                          │ CMD_IDLE path: cap = DATA_BUFFER_SIZE-1
                                      ◀── "FW: <ver>:<board>:<buf>:<maxchunk>"
 └─ parse fw_fields[3] → firmware_max_chunk


Write/Verify operation
 └─ _calculate_buffer_size() → firmware_max_chunk (= DATA_BUFFER_SIZE = 512/1024)
 └─ file.read(chunk_size)
 └─ cobs_encode(chunk + CRC8(chunk)) ──b"#"──▶  case '#': rurp_communication_read_data(buf, CAP=DATA_BUFFER_SIZE)
                                                   │ MAIN path: cap = DATA_BUFFER_SIZE (NEW)
                                                   │ Decoded payload: exactly DATA_BUFFER_SIZE bytes
                                                   │ data_buffer[i] consumed by index (no string)
                                      ◀── "OK: Req data"
 └─ (repeat until file exhausted: 128×512 = 65536 with no remainder)
```

### Key Invariant: Two Cap Values, One Decoder

The single `rurp_communication_read_data` function serves both paths with different caps:
- **CMD_IDLE** (line 176, firestarter.cpp): `cap = DATA_BUFFER_SIZE − 1` → preserves CR-01 NUL-slot; `data_buffer[n] = '\0'` is safe
- **MAIN data** (line 164, operation_utils.cpp): `cap = DATA_BUFFER_SIZE` → full block; no NUL write; safe because `data_buffer` is consumed by index

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CRC8 computation | New CRC routine | Existing `crc8_ccitt()` PROGMEM table (firmware) / `_crc8_ccitt()` table (host) | Phase 50 D-05: polynomial change is forbidden; existing implementations are byte-identical and verified by the frame-vector KAT |
| COBS encode/decode | New encoder/decoder | Existing `rurp_communication_read_data` / `rurp_communication_write` / `cobs_encode` / `cobs_decode` | Phase 52 lockstep contract is in place; adding new codec code would need to be added to the round-trip test corpus |
| Per-board chunk constant | `if board == "uno": chunk = 512` | `firmware_max_chunk` from identity string | D-03 bans hardcoded per-board constants |
| Frame-vector computation at test time | Dynamic `cobs_encode(payload)` in test assertions | Hardcoded literals in `frame-vectors.toml` | D-01 (Phase 52): "frozen contract" — computed values in tests can hide encoder bugs |

---

## Common Pitfalls

### Pitfall 1: Forgetting the CMD_IDLE Cap
**What goes wrong:** Developer changes the PUSH macro to use `DATA_BUFFER_SIZE` everywhere.
The CMD_IDLE path now allows a 512-byte JSON command. `data_buffer[512] = '\0'` writes one
byte past the end of the 512-byte array into `handle.data_size` — OOB write (CR-01 regression).
**Why it happens:** The fix looks like "just remove the `−1`" without tracing both call sites.
**How to avoid:** The `cap` parameter pattern ensures the difference is explicit at every call
site. Add a Unity test that sends a 512-byte payload on the CMD_IDLE path and asserts
`rurp_communication_read_data(buffer, DATA_BUFFER_SIZE - 1)` returns -2.
**Warning signs:** The existing CR-01 Unity test (from Phase 51) will catch this if it remains.

### Pitfall 2: Updating Only the Write Path, Not Verify
**What goes wrong:** `_calculate_buffer_size()` is changed but `verify_eprom` still uses a
different code path with the old constant.
**Why it happens:** Developer follows only the write code path.
**How to avoid:** D-06 confirms both paths go through `_main_phase_send_data` with `buf_size`
from `_calculate_buffer_size()`. Grep for all `_main_phase_send_data` call sites confirms
there are exactly two (lines 1140 and 1176), both using `buf_size`.

### Pitfall 3: firmware_max_chunk Not Set for Pre-Phase-54 Firmware
**What goes wrong:** The host raises `FirmwareOutdatedError` even when communicating with
Phase 53-era firmware that has `<buf>` but not `<maxchunk>`.
**Why it happens:** D-05 says "no fallback" but the firmware may be slightly behind.
**How to avoid:** The Phase 54 firmware and host are upgraded together (lockstep). Since Phase
53 firmware advertises 3 fields and Phase 54 firmware advertises 4, the host upgrade is
gated on the firmware upgrade. This is the stated D-05 beta lockstep posture. Document in
the breaking-change notes.

### Pitfall 4: On-Wire Frame Size Change Breaks Golden Vectors
**What goes wrong:** The new firmware sends 512-byte data chunks instead of 510-byte chunks;
the golden vector tests that encode 512 bytes previously expected the decoder to return -2
(overflow) but now expect success.
**Why it happens:** The existing VEC_512_ALL_FF and VEC_512_ALL_ZERO vectors test the
round-trip at 512 bytes but the decode direction was previously blocked by the `DATA_BUFFER_SIZE − 1`
cap on the CMD_IDLE path test. After Phase 54 the MAIN-path decoder cap is 512, so those
vectors should succeed on the MAIN path.
**How to avoid:** The firmware test suite must clearly separate CMD_IDLE-path decode tests
(cap=511, 512-byte payloads return -2) from MAIN-path decode tests (cap=512, 512-byte payloads
return 512). Add both test directions.

### Pitfall 5: No-Remainder Check Only for 65536-Byte Chips
**What goes wrong:** The no-remainder assertion passes for 65536-byte chips but other chip
sizes (e.g. 32768, 131072, 262144) leave a remainder with 512-byte blocks.
**Why it happens:** The assertion only checks `65536 % 512 == 0`.
**How to avoid:** The Phase 54 goal is specifically about even-block transfers. The no-remainder
guarantee is chip-size-dependent. A full-chip 65536-byte write divides evenly; a 32768-byte
write divides evenly (64×512); a 131072-byte write divides evenly (256×512); a 262144-byte
write divides evenly (512×512). All powers-of-two chip sizes divide evenly by 512 or 1024.
The assertion `assert chip_size % chunk_size == 0` is valid for the common EPROM sizes. The
test should use `65536 % 512 == 0` as the representative case per the phase motivation.

---

## Code Examples

### Parameterised Cap: PUSH Macro Change
```c
// Source: rurp_serial_utils.cpp — current PUSH macro
#define PUSH(b_)                                                   \
    do {                                                           \
        if (has_last) {                                            \
            if (out >= DATA_BUFFER_SIZE - 1) {  /* <-- CHANGE */  \
                _drain_to_delimiter();                             \
                return -2;                                         \
            }                                                      \
            buffer[out++] = (char)last_byte;                       \
        }                                                          \
        last_byte = (b_);                                          \
        has_last = true;                                           \
    } while (0)

// After Phase 54 — cap is a parameter:
#define PUSH(b_)                                \
    do {                                        \
        if (has_last) {                         \
            if (out >= cap) {                   \
                _drain_to_delimiter();          \
                return -2;                      \
            }                                   \
            buffer[out++] = (char)last_byte;    \
        }                                       \
        last_byte = (b_);                       \
        has_last = true;                        \
    } while (0)
```

### Identity String Extension
```c
// Source: firestarter.h line 35 — current:
#define FW_VERSION VERSION ":" RURP_BOARD_NAME ":" FS_STRINGIFY(DATA_BUFFER_SIZE)

// After Phase 54 — adds :<maxchunk>:
#define FW_VERSION VERSION ":" RURP_BOARD_NAME ":" FS_STRINGIFY(DATA_BUFFER_SIZE) ":" FS_STRINGIFY(DATA_BUFFER_SIZE)
// e.g. "3.0.0b8:uno:512:512"  or  "3.0.0b8:leonardo:1024:1024"
```

### Host Cap Replacement
```python
# Source: eprom_operations.py lines 163-179 — current:
def _calculate_buffer_size(self) -> int:
    fw_buf = getattr(self.comm, "firmware_buffer_size", None) if self.comm else None
    if fw_buf is not None and fw_buf >= 3:
        return fw_buf - 2  # reserve 1 byte CRC8 + 1 byte decoder NUL slot
    return MAX_DATA_CHUNK

# After Phase 54 — reads maxchunk directly, no arithmetic:
def _calculate_buffer_size(self) -> int:
    max_chunk = getattr(self.comm, "firmware_max_chunk", None) if self.comm else None
    if max_chunk is not None and max_chunk >= 1:
        return max_chunk
    raise FirmwareOutdatedError(
        "Firmware does not advertise a max-chunk capacity field. "
        "Please upgrade firmware using 'firestarter fw --install'."
    )
```

### No-Remainder Assertion
```python
# In test_even_block.py or test_frame_vectors.py (host):
def test_full_chip_no_remainder_uno():
    assert 65536 % 512 == 0, "65536-byte chip divides exactly into 512-byte blocks"

def test_full_chip_no_remainder_leonardo():
    assert 65536 % 1024 == 0, "65536-byte chip divides exactly into 1024-byte blocks"
```

```c
// In Unity test (firmware):
void test_even_block_no_remainder_uno(void) {
    TEST_ASSERT_EQUAL_UINT32(0, 65536 % DATA_BUFFER_SIZE);
}
```

---

## Validation Architecture

> `workflow.nyquist_validation` is absent from config.json — treated as enabled.

### Test Framework
| Property | Value |
|----------|-------|
| Firmware framework | Unity (PlatformIO native env) |
| Host framework | pytest |
| Firmware quick run | `pio test -e native` |
| Host quick run | `pytest firestarter_app/tests/test_frame_vectors.py firestarter_app/tests/test_even_block.py -x` |
| Full suite (firmware) | `pio test` |
| Full suite (host) | `pytest --cov=firestarter --cov-fail-under=70` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| EVEN-01 (SC1) | 512-byte data chunk decodes successfully on MAIN path (cap=512) | Unit | `pio test -e native -f "*test_frame_vectors*"` | New test cases in existing file |
| EVEN-01 (SC1) | 1024-byte data chunk decodes successfully on MAIN path (cap=1024) | Unit | `pio test -e native -f "*test_frame_vectors*"` | New test cases in existing file |
| EVEN-01 (SC1) | 512-byte data chunk still returns -2 on CMD_IDLE path (cap=511) | Unit | `pio test -e native -f "*test_frame_vectors*"` | New test case |
| EVEN-01 (SC2) | 65536 % 512 == 0 (no-remainder Uno) | Unit | `pytest tests/test_even_block.py::test_full_chip_no_remainder_uno -x` | New file ❌ Wave 0 |
| EVEN-01 (SC2) | 65536 % 1024 == 0 (no-remainder Leonardo) | Unit | `pytest tests/test_even_block.py::test_full_chip_no_remainder_leonardo -x` | New file ❌ Wave 0 |
| EVEN-01 (D-04) | `firmware_max_chunk` parsed from 4-field identity string | Unit | `pytest tests/test_serial_comm.py -x -k max_chunk` | Extend existing file |
| EVEN-01 (D-04) | `_calculate_buffer_size()` returns `firmware_max_chunk` directly | Unit | `pytest tests/test_eprom_operations.py -x -k buffer_size` | Extend existing file |
| EVEN-01 (D-08) | Uno SRAM ≤ 1503 bytes after firmware change | Build/RAM | `pio run -e uno 2>&1 \| grep "DATA used"` | Build output |
| EVEN-01 (D-08) | uno328pb SRAM ≤ 1503 bytes | Build/RAM | `pio run -e uno328pb 2>&1 \| grep "DATA used"` | Build output |
| EVEN-01 (SC4) | Round-trip: cobs_encode(512 bytes + CRC8) → rurp_communication_read_data(cap=512) → original 512 bytes | Unit | `pio test -e native -f "*test_frame_vectors*"` | Extend existing |

### Sampling Rate
- **Per task commit:** `pio test -e native && pytest tests/ -x`
- **Per wave merge:** Full suite: `pio test && pytest --cov=firestarter --cov-fail-under=70`
- **Phase gate (SC3):** `pio run -e uno 2>&1 | grep "DATA used"` asserts ≤ 1503 before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `firestarter_app/tests/test_even_block.py` — no-remainder assertions (EVEN-01 SC2)
- [ ] New Unity test cases in `firestarter/test/native/avr/test_frame_vectors/` — MAIN-path cap=512 decode assertions + CMD_IDLE overflow at 512 bytes (EVEN-01 SC1/SC4)
- [ ] `firmware_max_chunk` attribute declaration in `SerialCommunicator.__init__` and `_probe_port` parse extension (host `serial_comm.py`)

---

## Security Domain

Phase 54 changes the decode-buffer cap for one call site. No new attack surface is introduced:
- The `cap` parameter is a compile-time constant at both call sites — no runtime user input
- The overflow guard in PUSH still fires at `out >= cap` and returns -2 with drain; the
  security boundary is unchanged
- The identity-string `<maxchunk>` field is controlled by the firmware (trusted endpoint)
  and parsed as an integer with `isdigit()` guard

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | yes | Integer-only parse of `fw_fields[3]` with `.isdigit()` guard (mirrors existing `fw_fields[2]` pattern) |
| V6 Cryptography | no (phase does not change CRC) | CRC8-CCITT unchanged (D-05) |
| V4 Access Control | no | No authentication changes |

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Fixed `fw_buf − 2` chunk | Advertised `maxchunk` from identity string | Phase 54 | Host has no arithmetic; pure dynamic negotiation |
| `DATA_BUFFER_SIZE − 1` cap on both paths | `DATA_BUFFER_SIZE − 1` (CMD_IDLE) / `DATA_BUFFER_SIZE` (MAIN) | Phase 54 | Full even block on write/verify path; NUL-slot preserved on command path |
| 510/1022 bytes per write chunk | 512/1024 bytes per write chunk | Phase 54 | 128×512 = 65536 exactly; no 256-byte remainder round |

**Deprecated/outdated post-Phase-54:**
- `MAX_DATA_CHUNK = BUFFER_SIZE − 2 = 510` constant in `constants.py` — still present but no longer used by `_calculate_buffer_size()`
- The `fw_buf − 2` comment block in `_calculate_buffer_size()` — removed as part of the body replacement

---

## Open Questions

1. **Should `firmware_max_chunk` replace or supplement `firmware_buffer_size` on the `SerialCommunicator`?**
   - What we know: `firmware_buffer_size` is already set and used; `firmware_max_chunk` is the new field; both come from the identity string
   - What's unclear: whether any downstream code other than `_calculate_buffer_size()` uses `firmware_buffer_size` directly
   - Recommendation: keep `firmware_buffer_size` (no removal — it may be used by test/logging code); add `firmware_max_chunk` as a new attribute. Planner verifies usage with a grep.

2. **Golden vector test assertion: should VEC_512_ALL_FF / VEC_512_ALL_ZERO decode direction be added to the existing `test_frame_vectors` Unity suite or a new `test_even_block` Unity suite?**
   - What we know: D-09 leaves this to Claude; the existing suite already carries these vectors for the encode direction
   - What's unclear: whether mixing CMD_IDLE and MAIN path tests in one suite is confusing
   - Recommendation (D-09 answer): extend the existing `test_frame_vectors` suite with a clearly-labelled MAIN-path section rather than creating a new suite. Add the CMD_IDLE overflow case there too. Keep the no-remainder assertion in a separate small file (`test_even_block.c`) for clarity.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `firmware_max_chunk == DATA_BUFFER_SIZE` is the correct value to advertise after the Candidate A change (i.e. the firmware can actually decode exactly `DATA_BUFFER_SIZE` bytes on the MAIN path). | D-04 section | If the new cap still fails for some COBS overhead reason, the advertised value would cause decode errors. Mitigated: the PUSH guard fires at `out >= cap`; the CRC lookahead is held in `last_byte`; the total committed bytes is `cap = DATA_BUFFER_SIZE` payload bytes, which fits `data_buffer[DATA_BUFFER_SIZE]` exactly. Verified by tracing the lookahead invariant. |
| A2 | The `FS_STRINGIFY(DATA_BUFFER_SIZE)` expansion in `FW_VERSION` produces the same integer for both the `<buf>` and `<maxchunk>` fields after the change. | D-04 identity string | Trivially true since both use the same macro. |

**If this table is empty for a claim:** All other claims in this research were verified by direct source code reading. No web search was used; all findings are from the actual codebase on `v1.10-serial-transport-hardening`.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO / pio | D-08 RAM gate, firmware build | ✓ (assumed — used in Phases 50-53) | see `firestarter/platformio.ini` | — |
| Python 3.12 (devcontainer) | Host tests | ✓ | 3.12.x | — |
| pytest | Host tests | ✓ (installed via `pip install -e '.[test]'`) | — | — |
| Uno + Leonardo bench hardware | SC1 on-wire verification | gated | — | Software-only tests cover SC3/SC4; SC1 bench is operator-gated per Phase 53 pattern |

---

## Sources

### Primary (HIGH confidence — verified from source)
- `/workspaces/firestarter/src/boards/rurp_serial_utils.cpp` — COBS decoder, PUSH macro, `DATA_BUFFER_SIZE − 1` cap location
- `/workspaces/firestarter/src/firestarter.cpp` lines 176-185 — CMD_IDLE call site, NUL write, jsmn_parse string use
- `/workspaces/firestarter/src/operation_utils.cpp` lines 164-170 — MAIN data call site, OP_MSG_DATA branch
- `/workspaces/firestarter/src/eprom_operations.cpp` lines 89-106 — OP_MSG_DATA consumer: index-only access to data_buffer
- `/workspaces/firestarter/src/proms/memory.cpp` lines 224-225, 244 — write/verify consumers: `handle->data_buffer[i]` index
- `/workspaces/firestarter/include/firestarter.h` lines 17, 24, 35 — DATA_BUFFER_SIZE, CMD_FRAME_MAX, FW_VERSION macro
- `/workspaces/firestarter_app/firestarter/eprom_operations.py` lines 163-179, 1125-1179 — `_calculate_buffer_size()`, write_eprom, verify_eprom
- `/workspaces/firestarter_app/firestarter/serial_comm.py` lines 114-118, 557-624 — `firmware_buffer_size`, `_probe_port` identity parse
- `/workspaces/firestarter_app/firestarter/constants.py` lines 21-37 — `MAX_DATA_CHUNK`, `CMD_FRAME_MAX`
- `/workspaces/firestarter/tools/catalog/frame-vectors.toml` — existing 512/1024 vectors, TOML structure
- `/workspaces/.planning/v1.10-FRAMING-DECISION.md` §4.5 — ~545 B free-RAM ceiling, streaming constraint
- `/workspaces/.planning/STATE.md` line 93 — Uno RAM baseline 1503/2048 used

### Secondary (MEDIUM confidence)
- None — all claims verified from source.

---

## Metadata

**Confidence breakdown:**
- Mechanism analysis (D-01): HIGH — full code trace of both call sites and all consumers
- Identity-string extension (D-04): HIGH — existing pattern verified; extension is minimal
- Write/verify coverage (D-06): HIGH — call sites verified at exact line numbers
- RAM gate (D-08): HIGH — baseline from STATE.md; Candidate A is zero-growth
- Vector corpus (D-07): HIGH — existing vectors verified in frame-vectors.toml

**Research date:** 2026-06-04
**Valid until:** 2026-07-04 (stable — no external dependencies; pure code analysis)
