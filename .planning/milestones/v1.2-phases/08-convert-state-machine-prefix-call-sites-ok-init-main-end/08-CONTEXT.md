# Phase 8: Convert State-Machine Prefix Call-Sites (OK/INIT/MAIN/END) - Context

**Gathered:** 2026-05-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Eliminate every remaining firmware text-emit path for state-machine acks and operation-flow messages. After Phase 8, every wire byte from the firmware is either:
- a binary ID frame (`<MAGIC> <len> <id> <params> <crc> <term>`) carrying a single catalog message, OR
- raw chip content bytes wrapped in a `MSG_DATA_CHUNK` ID frame (the streaming protocol — see W-04 below).

State-machine acks (`OK:` / `INIT:` / `MAIN:` / `END:`) lose their text prefix entirely — the host stops line-prefix matching for these and dispatches on the catalog severity-band lookup. The `response_msg[96]` scratch buffer in `firestarter_handle_t` goes away (the populate-sites that filled it convert to direct `LOG_*_ID_*` emits). The 34 firmware `debug()` call-sites convert to a `MSG_DEBUG + sub_id` channel that is still production-stripped via `#ifdef SERIAL_DEBUG`.

Phase 8 does NOT delete the legacy `logging.h` macro tower (that's Phase 9 / LFW-03/04), does NOT bump the firmware major version to v3.0.0 (Phase 9), and does NOT take the final flash-savings measurement vs the Phase 6 baseline (Phase 9). It DOES bump the wire-format major version because of W-04 (len-field widening).

</domain>

<decisions>
## Implementation Decisions

### Wire format for state-machine acks

- **W-01:** Pure ID-frame, no text prefix. `OK:` / `INIT:` / `MAIN:` / `END:` literal prefixes are removed from the wire. Every firmware emit is `<MAGIC> <len> <id> <params> <crc> <term>`. The host parser's prefix-line matching path for these severities is deleted; only `_decode_id_frame` remains for state-machine acks.
- **W-02:** Host distinguishes ack frames from log frames via catalog severity-band lookup. The existing band layout (OK 0x00-0x0F, INIT 0x10-0x1F, MAIN 0x20-0x2F, END 0x30-0x3F, INFO 0x40-0x7F, WARN 0x80-0x9F, ERROR 0xA0-0xDF, DATA 0xE0-0xFF) is authoritative. `expect_ack()` filters by severity band. No new wire metadata.
- **W-03:** Both DATA-class log lines AND chip-read streaming convert in Phase 8. DATA-class logs (VPP/VPE/SENDING) become pure ID frames; chip-read streaming gets its own wrapped framing — see W-04. The current `DATA:` text prefix is removed everywhere.
- **W-04:** Chip-read streaming wraps each chunk inside a single MAGIC_PREAMBLE-prefixed ID frame (treating the chunk body as the params payload of a `MSG_DATA_CHUNK` catalog entry). Because the existing 1-byte `len` field caps params at 253 B and current buffers are 256 B (Uno) / 1024 B (Leonardo), **the wire-format `len` field widens from u8 to u16** (big-endian, consistent with existing MSB-first params). This is a wire-format major-version bump — firmware and host must change together. Single localized change in `_firestarter_emit_frame` (firmware) and `_read_and_parse_lines` / `_decode_id_frame` (host). A single Leonardo 1024-byte chunk now fits in one frame; no sub-chunking needed.

### `_check_response` buffer deconstruction

- **R-01:** Delete `response_msg[96]` from `firestarter_handle_t`. Once every populate-site emits via `LOG_*_ID_*` directly, no code reads or writes the buffer. SRAM win: ~96 B per operation invocation (Uno: 4.7% of 2 KB; Leonardo: 3.8% of 2.5 KB). The buffer-clear sites (`handle->response_msg[0] = '\0'` at firestarter.cpp:64/168, operation_utils.cpp:300, eprom.cpp:169) disappear with the field.
- **R-02:** Populate-sites use the two-line pattern locked in Phase 7 D-02: `LOG_*_ID_*(MSG_*, args); handle->response_code = RESPONSE_CODE_*;`. No combined "emit + set state" macro — explicit state changes only. OK + DATA sites may omit the `response_code` line where the default `OK` is already correct (e.g., a populate-site that always succeeds may rely on the operation entry-point's response_code = OK initialization). Convert sites to mirror this pattern:
  - `proms/eprom.cpp:104` `copy_to_buffer(handle->response_msg, "Skipping erase.")` → `LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE)` (existing ID 0x58)
  - `proms/eprom.cpp:171` `format(handle->response_msg, "Number of retries: %d", retries)` → `LOG_INFO_ID_U8(MSG_INFO_RETRIES, retries)` (existing ID 0x51)
  - `proms/flash_type_3.cpp:88` `copy_to_buffer(handle->response_msg, "Skipping erase of memory")` → `LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE_MEM)` (existing ID 0x59)
  - `proms/flash_type_4.cpp:52` `copy_to_buffer(handle->response_msg, "Skipping erase.")` → `LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE)` (existing ID 0x58)
  - `proms/memory.cpp:397` `firestarter_data_response_format("%lu/%lu", addr, mem_size)` → `LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, addr, mem_size)` (existing ID 0xE0)
- **R-03:** `_check_response` minimal strip: drop the `log_info(handle->response_msg)` line at operation_utils.cpp:320 and `log_data(handle->response_msg)` at operation_utils.cpp:325. Keep `rurp_communication_write(handle->data_buffer, handle->data_size)` in the DATA case. Keep `return false` in the ERROR case (operation-flow abort). Keep `op_reset_timeout()` and `handle->response_code = RESPONSE_CODE_OK` at the bottom. Final shape is a switch that drives operation flow only — no log emit. Same 3-branch switch structure preserved.

### OK_REV / OK_CFG / FW_VERSION / FW_HANDSHAKE payload shape

- **P-01:** `MSG_OK_FW_VERSION` (0x03) uses `ascii_str` as the single param. Preserves arbitrary suffixes (`-dev`, `-rc1`, `+sha7af3b2c`, etc.) without locking the wire to a fixed grammar. Wire shape: `<sub_byte length><N data bytes>`.
- **P-02:** `MSG_OK_REV` (0x04) becomes fixed-shape: `u8 physical + u8 effective`. `effective = 0xFF` means no override is active and the host renders `Rev{physical}`. `effective != physical` means the operator-installed override applies and the host renders `Rev{effective}, Override HW: Rev{physical}` (mirrors today's text). Lossless wire-format vs the current `ascii_str`.
- **P-03:** `MSG_OK_CFG` (0x05) becomes fixed-shape: `u32 r1 + u32 r2 + u8 override`. `override = 0xFF` means no override; otherwise the override hardware-revision byte. 9 wire bytes fixed. Mirrors the P-02 convention.
- **P-04:** `MSG_OK_FW_HANDSHAKE` (0x06) becomes a composite frame: `u8 hw + u8 cmd + ascii_str fw_version`. Single ID-frame per command-ack — same number of frames + round-trips as today's `send_ack_format(PARSE_RESPONSE, ...)`. Replaces both branches at firestarter.cpp:150 (HARDWARE_REVISION defined) and firestarter.cpp:153 (no HARDWARE_REVISION) — when HARDWARE_REVISION is undefined, emit hw = 0xFF as the sentinel. Fixed-shape params first per Phase 6 convention; ascii_str last.
- **VPP/VPE pre-decided (carry-forward from prior conversation):** `log_data_format("%s: %u.%uV, Internal VCC: %u.%uV", ...)` at hardware_operations.cpp:67-69 splits into two NEW DATA-class catalog IDs, each `u16 voltage_mv + u16 vcc_mv` (4 wire bytes):
  - `MSG_DATA_VPP_VOLTAGE` — host renders `VPP: {voltage_mv/1000}.{(voltage_mv/100)%10}V, Internal VCC: {vcc_mv/1000}.{(vcc_mv/100)%10}V`
  - `MSG_DATA_VPE_VOLTAGE` — same pattern with `VPE:` prefix
  Wire savings vs the current text: ~25 bytes/sample → 4 bytes/sample.

### debug() conversion via MSG_DEBUG + sub_id

- **B-01:** Convert the 34 firmware `debug()` / `debug_format()` call-sites in Phase 8. Single main catalog entry `MSG_DEBUG` carries all debug strings; sub_id namespace identifies which specific debug message. Production unchanged: `#ifdef SERIAL_DEBUG` still gates the macro to a no-op in release builds, so production wire traffic is unaffected.
- **B-02:** sub_id width = `u8` (256-entry namespace). Today: 34 debug strings; ~7x headroom. If we ever approach 256 entries, that signals a firmware-side over-instrumentation problem to address separately, not a wire-format change.
- **B-03:** Debug-strings table lives **inline in `tools/catalog/messages.toml` under a `[debug]` section**. Single canonical file with two sections: main `[messages]` (production protocol) + `[debug]` (sub_id namespace). Codegen.py extends to emit firmware-side `#define DBG_*` constants (alongside `MSG_*`) and a host-side `DEBUG_CATALOG` dict (parallel to `CATALOG`). Drift gate covers both sections.
- **B-04:** Sub_id entries declare params just like main messages. Each `[debug.DBG_*]` entry has its own `params` shape — including fixed-shape (u8/u16/u24/u32) and `ascii_str`. Wire frame for a debug emit: `<MAGIC> <len_u16> MSG_DEBUG sub_id [params] <crc> <term>`. Lets `debug_format("address: 0x%06lx", addr)` convert cleanly to `LOG_DEBUG_ID_U24(DBG_ADDR, addr)` with `DBG_ADDR` declaring `params = [{type = "u24"}]`.

### Claude's Discretion

The operator did not lock the following — researcher and planner should propose concrete choices grounded in Phase 8's scope, surface them in RESEARCH.md / PLAN.md, and proceed without re-asking:

- **Commit cadence for the cutover** — Phase 7 used per-file commits within a wave. Phase 8 has fewer files but bigger semantic shifts (wire-format `len` widening, response_msg buffer deletion). Plan likely groups: (1) catalog additions + codegen sub_id support, (2) wire-format `len` u8→u16 (firmware + host together), (3) host parser refactor (drop prefix matching for OK/INIT/MAIN/END), (4) per-file populate-site conversions, (5) `_check_response` strip + `response_msg` deletion, (6) `debug()` conversion sweep.
- **Native test impact** — the wire-format widening will break the existing `test_messages` Unity suite assertions about frame layout. Planner should fold a `test_messages` revision into the wire-format-widening commit so the suite stays green wave-by-wave.
- **Host parser refactor depth** — Phase 7's host changes were zero (the decoder was Phase 6 infra). Phase 8 deletes a substantial code path in `_read_and_parse_lines` (the prefix-line matching for OK/INIT/MAIN/END). Researcher should map the existing parser branches and identify the smallest surgical removal.
- **Debug conversion ordering** — convert in a single sweep at the end of Phase 8, or piecewise alongside each touched file? Recommended single-sweep so the catalog-add commit cluster is contiguous, but planner may differ.
- **`copy_to_buffer` helper fate** — the helper currently exists only because populate-sites needed to fill `response_msg`. After R-01, every caller is gone. Plan should include deleting `copy_to_buffer` from logging.h (or marking deprecated for Phase 9 deletion).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope + requirements (authoritative)
- [.planning/ROADMAP.md](.planning/ROADMAP.md) §"Phase 8: Convert State-Machine Prefix Call-Sites (OK/INIT/MAIN/END)" — phase goal locked; Phase C of the migration.
- [.planning/REQUIREMENTS.md](.planning/REQUIREMENTS.md) §"Logging Migration" — LMIG-03 ("Phase C: OK/INIT/MAIN/END conversion; host parser switches to ID-frame decoding for state-machine acks").
- [.planning/PROJECT.md](.planning/PROJECT.md) §"Phased migration" — locked phase ordering A→B→C→D→Close; Phase 8 is C.

### Phase 6 wire-format spec (the protocol Phase 8 modifies)
- [firestarter/src/boards/rurp_serial_utils.cpp:120](firestarter/src/boards/rurp_serial_utils.cpp#L120) — wire-format spec comment: `MAGIC | len | id | params | crc | term`.
- [firestarter/src/boards/rurp_serial_utils.cpp:153-191](firestarter/src/boards/rurp_serial_utils.cpp#L153-L191) — `_firestarter_emit_frame` — the function whose `len` write (line 177) widens from u8 to u16 per W-04.
- [firestarter_app/firestarter/serial_comm.py:299-378](firestarter_app/firestarter/serial_comm.py#L299-L378) — `_decode_id_frame` — the corresponding host decoder.
- [firestarter_app/firestarter/serial_comm.py:418-505](firestarter_app/firestarter/serial_comm.py#L418-L505) — `_read_and_parse_lines` — the host byte-stream reader whose state-machine prefix matching path Phase 8 deletes (W-01, W-02).
- [.planning/phases/06-logging-infrastructure/06-CONTEXT.md](.planning/phases/06-logging-infrastructure/06-CONTEXT.md) §D-01..D-06 — wire-format decisions Phase 6 locked. Phase 8's W-04 changes one of them (len width); other decisions stand.

### Phase 7 outputs to consume / extend
- [.planning/phases/07-convert-error-warn-info-call-sites/07-CONTEXT.md](.planning/phases/07-convert-error-warn-info-call-sites/07-CONTEXT.md) §D-01 — "drop log_* calls in _check_response but PRESERVE OK + DATA branches" — Phase 8 owns those preserved branches per R-03.
- [.planning/phases/07-convert-error-warn-info-call-sites/07-CONTEXT.md](.planning/phases/07-convert-error-warn-info-call-sites/07-CONTEXT.md) §D-02 — two-line emit pattern (`LOG_*_ID_*(...); handle->response_code = ...;`). Phase 8 R-02 continues this pattern for OK + DATA conversion.
- [firestarter/include/logging_id.h](firestarter/include/logging_id.h) — Phase 7 added `LOG_ERROR_ID_*` + `LOG_WARN_ID_*` families. Phase 8 adds `LOG_OK_ID_*` + `LOG_INIT_ID_*` + `LOG_MAIN_ID_*` + `LOG_END_ID_*` + `LOG_DATA_ID_*` + `LOG_DEBUG_ID_*` families.
- [.planning/phases/07-convert-error-warn-info-call-sites/07-FLASH-MEASUREMENT.md](.planning/phases/07-convert-error-warn-info-call-sites/07-FLASH-MEASUREMENT.md) — Phase 7 close baseline (Leonardo 27,026 / 28,672 B, Uno 24,838 / 32,256 B). Phase 8's SRAM win (R-01) is independent of the flash trend; SRAM measurement is also a phase-close deliverable.

### Catalog + codegen (additions in Phase 8)
- [tools/catalog/messages.toml](tools/catalog/messages.toml) — canonical catalog. Phase 8 additions: VPP/VPE DATA IDs; MSG_DATA_CHUNK; `[debug]` section with sub_id entries; param-shape changes for existing OK_REV / OK_CFG / OK_FW_HANDSHAKE.
- [tools/catalog/codegen.py](tools/catalog/codegen.py) — extends to emit `DBG_*` constants + `DEBUG_CATALOG` for the `[debug]` section (B-03).
- [tools/catalog/sync_to_subrepos.sh](tools/catalog/sync_to_subrepos.sh) — re-syncs the updated `messages.toml` + `codegen.py` to both submodules.
- [firestarter/.github/workflows/build.yml](firestarter/.github/workflows/build.yml) — CI drift gate; covers `messages.h` only post-Phase-7. Phase 8 may need a drift-gate revision if the new debug header is split out.

### Firmware handle struct (R-01 target)
- [firestarter/include/firestarter.h:21](firestarter/include/firestarter.h#L21) — `RESPONSE_MSG_SIZE` = 96.
- [firestarter/include/firestarter.h:79](firestarter/include/firestarter.h#L79) — `char response_msg[RESPONSE_MSG_SIZE]` — the field Phase 8 deletes.

### Populate-sites (R-02 conversions)
- [firestarter/src/proms/eprom.cpp:104](firestarter/src/proms/eprom.cpp#L104), [:171](firestarter/src/proms/eprom.cpp#L171) — OK-path buffer fills (`Skipping erase`, `Number of retries`).
- [firestarter/src/proms/flash_type_3.cpp:88](firestarter/src/proms/flash_type_3.cpp#L88) — `Skipping erase of memory`.
- [firestarter/src/proms/flash_type_4.cpp:52](firestarter/src/proms/flash_type_4.cpp#L52) — `Skipping erase`.
- [firestarter/src/proms/memory.cpp:397](firestarter/src/proms/memory.cpp#L397) — DATA-path `firestarter_data_response_format("%lu/%lu", addr, mem_size)`.
- [firestarter/src/hardware_operations.cpp:44](firestarter/src/hardware_operations.cpp#L44), [:67-69](firestarter/src/hardware_operations.cpp#L67-L69), [:80](firestarter/src/hardware_operations.cpp#L80), [:89](firestarter/src/hardware_operations.cpp#L89), [:100/102](firestarter/src/hardware_operations.cpp#L99-L101) — `send_ack_const` / `send_ack_format` sites (`Ready`, VPP/VPE voltage, FW_VERSION, HW_REV, R1/R2 config).
- [firestarter/src/eprom_operations.cpp:80](firestarter/src/eprom_operations.cpp#L80), [:121](firestarter/src/eprom_operations.cpp#L116) — `send_ack_const("Req data")`, `log_data_const("Sending data")`.
- [firestarter/src/firestarter.cpp:150](firestarter/src/firestarter.cpp#L150), [:153](firestarter/src/firestarter.cpp#L153) — `send_ack_format(PARSE_RESPONSE, ...)` — the per-command FW_HANDSHAKE ack (P-04).
- [firestarter/src/operation_utils.cpp:320](firestarter/src/operation_utils.cpp#L320), [:317](firestarter/src/operation_utils.cpp#L325) — `_check_response` D-01 OK + DATA log calls (R-03).

### Legacy macros (NOT deleted in Phase 8 — Phase 9 owns deletion)
- [firestarter/include/logging.h](firestarter/include/logging.h) — `log_info_const`, `log_data_const`, `log_data_format`, `send_ack_const`, `send_ack_format`, `copy_to_buffer`, `firestarter_response_format`, etc. Phase 8 stops calling them (every call-site converts) but leaves the macro definitions in place. Phase 9 (LFW-03/04) deletes them and any remaining `log_*` infrastructure.

### Test surface
- [firestarter/test/native/avr/test_messages/](firestarter/test/native/avr/test_messages/) — Phase 6 wire-frame Unity suite. Asserts the current `len = u8` shape; Phase 8 W-04 wire-format widening must update these tests in the same commit as the `_firestarter_emit_frame` change.
- [firestarter/test/native/avr/test_dispatch/](firestarter/test/native/avr/test_dispatch/) — operation dispatch tests. May need stub updates if `_check_response` minimization changes link surface.
- [firestarter_app/tests/test_decoder.py](firestarter_app/tests/test_decoder.py) — host decoder regression. Wire-format widening AND prefix-matching deletion need test coverage updates.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`LOG_ID_*` primitives + `LOG_ERROR_ID_*` / `LOG_WARN_ID_*` / `LOG_INFO_ID_*` families** in `logging_id.h` — Phase 7's macro tower. Phase 8 adds `LOG_OK_ID_*` + `LOG_INIT_ID_*` + `LOG_MAIN_ID_*` + `LOG_END_ID_*` + `LOG_DATA_ID_*` + `LOG_DEBUG_ID_*` as one-line aliases over the same `LOG_ID_*` primitives. Same trivial pattern as Phase 7 Plan 01.
- **`_firestarter_emit_frame`** in `boards/rurp_serial_utils.cpp` — single emit function. W-04 widens its `len` write from 1 byte to 2 bytes; no other change needed firmware-side.
- **`_decode_id_frame` + `_read_and_parse_lines`** in `serial_comm.py` — single host-side decode surface. W-04 widens the `len` read; W-01 + W-02 delete the prefix-matching branches for OK/INIT/MAIN/END.
- **Existing catalog IDs that need no shape change**: `MSG_OK_READY` (0x01, 0 params), `MSG_OK_REQ_DATA` (0x02, 0 params), `MSG_INIT_DONE` (0x10), `MSG_MAIN_DONE` (0x20), `MSG_END_DONE` (0x30), `MSG_INFO_SKIPPING_ERASE` (0x58), `MSG_INFO_SKIPPING_ERASE_MEM` (0x59), `MSG_INFO_RETRIES` (0x51 u8), `MSG_DATA_PROGRESS` (0xE0, 2×u32), `MSG_DATA_SENDING` (0xE2, 0 params). Most Phase 8 conversions slot into existing IDs.

### Established Patterns

- **Each populate-site = emit + state-set (two-line pattern)** — Phase 7 D-02 locked this. Phase 8 R-02 continues: every OK + DATA populate-site converts to `LOG_*_ID_*(MSG_*, args); handle->response_code = ...;`. No combined macro.
- **Catalog-additions-first, then call-site conversion** — Phase 7 D-03 wave-1 added the missing ERROR catalog entries before any Wave-2 call-site touched them. Phase 8 mirrors this: add the new DATA IDs (VPP, VPE, CHUNK), the OK redesigns (REV/CFG/FW_HANDSHAKE shape changes), and the `[debug]` section in Wave 1; then convert call-sites in Wave 2+.
- **Fixed-shape with sentinel byte for optional fields** — P-02 and P-03 use `0xFF` as the no-override sentinel. Established pattern; mirrors how the param-byte-count table used `0xFF` for variable-length entries pre-deletion.
- **Wire-format major-version bump = coordinated firmware + host commit** — W-04 widens `len`. Host backward-compat is not preserved (no transitional dual-decoder). Firmware version bumps to 3.0.0 in Phase 9, but the wire-format change in Phase 8 will need its own coordination commit.

### Integration Points

- **Host probe (`_send_command` / `expect_ack` in serial_comm.py)** — every command-ack flows through this. W-02's severity-band ack-vs-log dispatch and P-04's composite FW_HANDSHAKE shape change land here.
- **Continuous DATA streams (vpp/vpe read loop)** — `hw_read_voltage` emits a DATA-class log every ~500 ms. New shape (P/VPP/VPE) is 4 bytes vs ~25 bytes today; emit cadence stays the same (host throttles).
- **Chip-read streaming (eprom_operations.cpp `read` path)** — emits N data frames per buffer fill. W-04's MAGIC-wrapped chunk replaces the current `DATA:` text-prefix + raw bytes format. Host's `_read_chunk` (or equivalent) becomes a single-frame decode.
- **CI catalog-sync drift gate** — `.github/workflows/catalog-sync-check.yml` (meta-repo) + `firestarter/.github/workflows/build.yml` codegen-drift step. Both need to remain green through the messages.toml additions; `firestarter_app/.github/workflows/ci.yml` likewise for the host-side regen.

</code_context>

<specifics>
## Specific Ideas

- **No string runtime-built**: the user's explicit goal — every wire byte from production firmware is a structured ID frame or a wrapped chunk; no `printf`-style runtime string assembly. Maps to W-01..W-04 + R-01..R-03 + P-01..P-04.
- **Debug as catalog-uniform-but-still-stripped**: the `MSG_DEBUG + sub_id` design (B-01..B-04) lets us claim "every emit is an ID frame" without sacrificing the SERIAL_DEBUG production-stripping. The user specifically requested NOT to balloon the catalog with per-string debug IDs (B-01 chose the single-main-ID design with a sub_id namespace).
- **Lossless wire-format for OK_REV / OK_CFG**: the override field is rarely active but operationally informative; sentinel-byte encoding (P-02, P-03) keeps the existing diagnostic surface intact.
- **Composite FW_HANDSHAKE** (P-04): single frame per command, ascii_str FW last so fixed-shape params parse first. Matches Phase 6 emit-order convention.

</specifics>

<deferred>
## Deferred Ideas

- **Firmware major-version bump to 3.0.0** — pre-conditioned on the wire-format major bump (W-04), but the version-string change itself is Phase 9 scope. Phase 8 wire-format changes will be visible to the host's `FIRESTARTER_DEV_ALLOW_PRE_V12` escape hatch as needed for bench testing.
- **Deletion of legacy `logging.h` macro tower** (`log_info_const`, `log_data_format`, `send_ack_const`, `copy_to_buffer`, `firestarter_response_format`, etc.) — Phase 9 territory (LFW-03/04). Phase 8 stops calling them but leaves the definitions.
- **Final Leonardo flash measurement vs Phase 6 baseline** — Phase 9 deliverable (after the legacy macros are deleted, the strings drop out, and the real flash win materializes). Phase 8 measures its own delta but the milestone-level number waits for Phase 9.
- **Host CLI rendering of decoded debug frames** — once `DEBUG_CATALOG` exists host-side, the CLI can render decoded debug strings the same way it renders INFO/WARN/ERROR today. Whether the rendering path is silent-by-default (only show on a `--debug` host flag) is a host-side concern, deferred to Phase 8 plan or Phase 9 polish.
- **Wire-format minor-version negotiation** — currently the firmware version gate is binary (refuse-if-pre-v1.2). After Phase 8 widens `len`, the host might want to negotiate (`v2 frames = u8 len; v3 frames = u16 len`). For now: hard cutover, version-coupled. Negotiation is a future-phase concern if a mixed-version fleet ever becomes a real scenario.

</deferred>

---

*Phase: 8-convert-state-machine-prefix-call-sites-ok-init-main-end*
*Context gathered: 2026-05-18*
