# Phase 7: Convert ERROR + WARN + INFO Call-Sites - Context

**Gathered:** 2026-05-18
**Status:** Ready for planning
**Source:** /gsd-discuss-phase 7 — user selected three gray areas: dispatcher-removal depth, macro ergonomics, and catalog/cleanup scope. Commit cadence deferred to planner discretion.

<domain>
## Phase Boundary

**In scope (Phase B of the locked v1.2 phased migration; LMIG-02):**

- Every active firmware **direct** `log_info_* / log_warn_* / log_error_*` call-site (in `firestarter.cpp`, `operation_utils.cpp`, `dev_tools.cpp`, `eprom_operations.cpp`, `hardware_operations.cpp`) is converted to emit via `rurp_log_id` — typically through the new `LOG_INFO_ID_* / LOG_WARN_ID_* / LOG_ERROR_ID_*` convenience macros.
- Every active **populate-site** of `firestarter_error_response_format / firestarter_warning_response_format` (in `proms/*.cpp`) is converted to emit via `rurp_log_id` directly at the populate site, eliminating the `handle->response_msg` round-trip for ERROR/WARN frames. The populate site keeps the `handle->response_code = ERROR/WARNING` assignment so the operation-flow state machine in `_check_response` still aborts on error.
- `_check_response` (`operation_utils.cpp:329-350`) drops its four `log_info(handle->response_msg) / log_warn / log_data / log_error` calls. The `switch` keeps response_code-driven control flow (return-false on ERROR, binary-payload write on DATA). `handle->response_msg` and the `log_*(handle->response_msg)` indirection becomes vestigial — Phase 9 deletes the buffer.
- New `LOG_ERROR_ID_* + LOG_WARN_ID_*` macro families land in `firestarter/include/logging_id.h`, mirroring the existing `LOG_INFO_ID_*` family (LOG_ERROR_ID, _U8, _U16, _U24, _U32, _BYTES) but unconditional (no FLAG_VERBOSE gate).
- The host CLI output for ERROR/WARN/INFO lines is rendered by the new catalog decoder (success criterion #2: toggling the decoder off makes exactly those lines disappear).
- Cleanup: `operation_utils.cpp`'s ~14 commented-out `// log_*_const / log_*_format` breadcrumb lines are deleted in the same diff.

**Out of scope (deferred):**

- `OK:` / `INIT:` / `MAIN:` / `END:` state-machine acks (Phase 8 / LMIG-03). The `RESPONSE_CODE_OK` and `RESPONSE_CODE_DATA` branches of `_check_response` are NOT touched in Phase 7 — they still emit text-formatted acks via `log_info(handle->response_msg)` / `log_data(...)`. Phase 8 converts those.
- `firestarter_data_response_format` populate sites (those still feed the DATA prefix path; DATA prefix marker stays text per the v1.2 milestone lock).
- The `DATA:` binary read-payload prefix and stream (out for v1.2 by milestone lock).
- Deletion of old `log_*_const / log_*_format` macros and `LOG_*_MSG` PROGMEM strings (Phase 9 / LMIG-04).
- Deletion of `handle->response_msg` buffer itself (Phase 9 after Phase 8 clears the OK/INIT/MAIN/END branches).
- Firmware major-version bump to 3.0.0 (Phase 9 / LFW-03).

</domain>

<decisions>
## Implementation Decisions

### Dispatcher refactor depth

- **D-01 — Drop `log_*` calls in `_check_response`; keep response_code state machine.**
  Each populate site emits **immediately** via `LOG_ERROR_ID_*(MSG_ERR_*, ...)` or `LOG_WARN_ID_*(MSG_WARN_*, ...)` AND sets `handle->response_code = RESPONSE_CODE_ERROR / RESPONSE_CODE_WARNING`. Inside `_check_response`:

  ```c
  case RESPONSE_CODE_WARNING:                   // log_warn(handle->response_msg) DELETED
      break;
  case RESPONSE_CODE_ERROR:
  default:                                      // log_error(handle->response_msg) DELETED
      return false;                             // KEPT — drives operation-flow abort
  ```

  The `RESPONSE_CODE_OK` and `RESPONSE_CODE_DATA` branches **stay intact** in Phase 7 (they're state-machine acks — Phase 8 territory). `handle->response_msg` writes from `firestarter_error_response_format` populate sites stop (those sites no longer set response_msg), but the buffer field remains on `firestarter_handle_t` until Phase 9 — it's still written by the OK/DATA paths.

  Net effect: ERROR/WARN frames stop being emitted twice (once by the OLD `firestarter_error_response_format`-via-`_check_response` path, once by the NEW `LOG_ERROR_ID_*` path). Only the new path remains.

### Macro design

- **D-02 — Add symmetric `LOG_ERROR_ID_*` and `LOG_WARN_ID_*` families to `logging_id.h`.**
  Mirror the existing `LOG_INFO_ID_*` shape, but **unconditional** (no `is_flag_set(FLAG_VERBOSE)` gate — ERROR + WARN must always emit). Full family:

  ```c
  // Unconditional ERROR — call-sites read symmetrically with LOG_INFO_ID_*
  #define LOG_ERROR_ID(id)               LOG_ID(id)
  #define LOG_ERROR_ID_U8(id, p)         LOG_ID_U8((id), (p))
  #define LOG_ERROR_ID_U16(id, p)        LOG_ID_U16((id), (p))
  #define LOG_ERROR_ID_U24(id, p)        LOG_ID_U24((id), (p))
  #define LOG_ERROR_ID_U32(id, p)        LOG_ID_U32((id), (p))
  #define LOG_ERROR_ID_BYTES(id, b, n)   LOG_ID_BYTES((id), (b), (n))
  // …same surface for LOG_WARN_ID_*
  ```

  These are thin aliases — they expand to the same underlying `rurp_log_id` calls as `LOG_ID_*`, so zero runtime / flash cost vs raw. The win is readability: call-sites read `LOG_ERROR_ID_U16(MSG_ERR_FOO, val)` next to `LOG_INFO_ID_U16(MSG_INFO_BAR, val)` and the severity is obvious from the macro name (not just the MSG_ prefix).

  **Multi-param packers** (e.g. `LOG_*_ID_U16_U32(...)` for two-param messages) are NOT added preemptively — the planner audits the catalog for actual multi-param ERROR/WARN/INFO entries (e.g. `"VPP is low: %u.%uV < %u.%uV"`, `"Failed to write memory, 0x%06x, retries: %d, bad bytes: %d"`) and adds purpose-built composers only for those, mirroring how `LOG_ID_BYTES` is the escape hatch for everything else.

### Catalog drift policy

- **D-03 — Locked catalog: any uncovered call-site is a Phase 6 gap, fixed via a separate commit.**
  Phase 6 RESEARCH (`06-RESEARCH.md:106`) claims **52 unique format-strings → 55 catalog entries** cover every active call-site (the 3-entry surplus accounts for catalog-design collapses where one ID consolidates multiple identical-format call-sites — e.g. `"VPP is low: %u.%uV < %u.%uV"` shared by `eprom.cpp` + `flash_intel.cpp`).

  If Phase 7 finds a call-site whose format/shape doesn't have a catalog entry:
  1. **Stop the conversion batch.** Do not invent a catalog ID inline.
  2. Add the missing entry to `.planning/catalog/messages.toml`, run `sync_to_subrepos.sh`, regen, and commit as `chore(catalog): add MSG_<NEW> (Phase 6 gap fix, see Phase 7)`.
  3. Resume conversion.

  This preserves the "Phase 6 catalog is authoritative" invariant and makes catalog drift visible in the git history. Acceptable risk: small chance of mid-phase friction if multiple gaps surface. Researcher should audit catalog ↔ call-site coverage as a pre-flight check.

  **Format-string drift sub-case:** If the current code's format string differs from the catalog's (e.g. catalog has `"VPP is low: %u.%uV < %u.%uV"` but the active code path differs by punctuation/casing), the **call-site adapts to the catalog format** (the catalog is canonical for what reaches the wire). Don't fork the catalog to match historical code.

### Cleanup scope

- **D-04a — Convert `dev_tools.cpp`'s 6 INFO call-sites.**
  `dev_tools.cpp` builds and links into both firmware binaries — same flash pressure as everything else, and skipping it leaves residual `log_info_const` usage that would fail success criterion #1's grep. In scope.

- **D-04b — Delete `operation_utils.cpp`'s ~14 commented-out `// log_*` breadcrumb lines.**
  Stale debug breadcrumbs reference legacy macros. Phase 9 will reorganize/delete `logging.h`, at which point these stale comments become actively misleading. Delete in the same diff as the conversions, so the cleanup commit is self-contained.

### Claude's Discretion

The operator skipped commit cadence (G3) and a few smaller items. The planner / researcher should propose concrete choices, ground them in Phase 7's success criteria, and present them in PLAN.md / RESEARCH.md for acceptance:

- **Commit cadence / batching strategy.** LMIG-02 says "Each batch commits separately by call-site cluster (one PROM module at a time)." Recommended interpretation given the call-site inventory: two waves — (a) **populate-site wave** = one commit per `proms/*.cpp` module (eprom, flash_intel, flash_type_4, flash_utils, eeprom_28c, memory) so per-PROM-family churn is bisectable; (b) **direct-log wave** = one commit per file (firestarter.cpp, operation_utils.cpp, dev_tools.cpp, eprom_operations.cpp, hardware_operations.cpp) — biggest is firestarter.cpp at ~20 sites. Plus a final commit for the macro additions (`logging_id.h` LOG_ERROR_ID_* / LOG_WARN_ID_*) which should land **first** as an infrastructure commit so subsequent commits can use them. Net: ~12 commits. Planner can collapse if a batch is genuinely trivial.
- **Multi-param composer macros.** The catalog has at least three multi-param formats (`"VPP is low: %u.%uV < %u.%uV"` 4×u8, `"Failed to write memory, 0x%06x, retries: %d, bad bytes: %d"` u24+u8+u8, `"0x%02x != 0x%02x at 0x%06x"` u8+u8+u24). Planner picks the right composer surface — likely a small set of purpose-built `LOG_ERROR_ID_U24_U8_U8` etc. macros, or rely on raw `LOG_ID_BYTES(MSG, (uint8_t[]){...}, n)` with a per-call stack-array. Recommend the latter for the multi-param edge cases — keeps `logging_id.h` from exploding.
- **`log_error_format_buf(handle.response_msg, "Cmd: %d, timeout", handle.cmd)` at `firestarter.cpp:171`.** This is a hybrid that formats into `handle.response_msg` AND emits via `log_error`. Planner converts to `LOG_ERROR_ID_U8(MSG_ERR_CMD_TIMEOUT, handle.cmd)` directly — no buffer touch, no response_code mutation (this site is outside the populate-then-dispatch pattern).
- **Hand-built `host_stubs.cpp` updates.** The `test/native/avr/test_dispatch/host_stubs.cpp` currently stubs `rurp_log` / `rurp_log_P` / `LOG_*_MSG` PROGMEM strings. After Phase 7, the dispatch tests don't exercise log emission directly, but link-time references may shift. Researcher confirms whether `host_stubs.cpp` needs additions or whether the existing weak-symbol `rurp_log_id` stub from `rurp_serial_utils.cpp` is enough at native link time.
- **Flash-savings target wording.** Success criterion #4 says "binary size has dropped measurably vs the Phase 6 baseline (record the delta — not yet the milestone target, but the trend must be downward)." Phase 6 close baseline: Leonardo 98.7% / 380 bytes free; Uno 80.9%. Phase 7 close should record numbers in a `07-FLASH-MEASUREMENT.md` artifact analogous to Phase 6's. "Measurable" = any non-zero reduction; planner picks the wording.
- **`_check_response` test coverage.** The dispatcher behavior change (drop log_* lines, keep response_code flow) should be exercised at least once in the native dispatch suite, or via a Python integration test against `firmware-simulator` if one exists. Planner picks the gate.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope + requirements (authoritative)
- [.planning/ROADMAP.md](.planning/ROADMAP.md) §"Phase 7: Convert ERROR + WARN + INFO Call-Sites" — four success criteria (grep returns zero hits, host-rendered output, state-machine acks untouched, both boards still compile with measurable size drop).
- [.planning/REQUIREMENTS.md](.planning/REQUIREMENTS.md) §"Logging Migration" — LMIG-02 ("Phase B: ERROR + WARN + INFO conversion; each batch commits separately by call-site cluster — one PROM module at a time").
- [.planning/PROJECT.md](.planning/PROJECT.md) §"Constraints (locked at milestone start)" — milestone-level locks (1-byte IDs, raw byte arrays, English only, lockstep upgrade, CI drift gate).
- [.planning/STATE.md](.planning/STATE.md) §"v1.2 Decisions (locked at milestone start, 2026-05-18)" — same locks restated.

### Phase 6 outputs (the infrastructure being consumed)
- [.planning/phases/06-logging-infrastructure/06-CONTEXT.md](.planning/phases/06-logging-infrastructure/06-CONTEXT.md) §D-01..D-06 — wire frame format (4-byte magic + len + id + params + CRC8 + 0x0A terminator).
- [.planning/phases/06-logging-infrastructure/06-RESEARCH.md](.planning/phases/06-logging-infrastructure/06-RESEARCH.md) §"Call-site inventory" (line 106) — 62 active call-sites, 52 unique format-strings deduped. **Line 204 explicitly states Phase 7 owns the `firestarter_*_response_format` populate-site refactor and the `_check_response` dispatch removal** — that boundary is locked, not gray.
- [.planning/phases/06-logging-infrastructure/06-VERIFICATION.md](.planning/phases/06-logging-infrastructure/06-VERIFICATION.md) — 6/6 success criteria PASSED; Leonardo 98.7% baseline + Uno 80.9% baseline numbers (Phase 7 measures against these).
- [.planning/phases/06-logging-infrastructure/06-FLASH-MEASUREMENT.md](.planning/phases/06-logging-infrastructure/06-FLASH-MEASUREMENT.md) — baseline + fall-back plan template that Phase 7's measurement artifact mirrors.
- [.planning/catalog/messages.toml](.planning/catalog/messages.toml) — canonical catalog, 68 entries (1 sentinel + 7 OK + 1 INIT + 1 MAIN + 1 END + 3 DATA + 26 INFO + 5 WARN + 24 ERROR). The 55 INFO/WARN/ERROR entries are Phase 7's conversion targets; the rest are Phase 8 (OK/INIT/MAIN/END) or stay text (DATA, MSG_OK_FW_VERSION).
- [.planning/catalog/codegen.py](.planning/catalog/codegen.py) — deterministic codegen; the drift gate enforces `regen && git diff --exit-code` in both sub-repos' CI.
- [.planning/catalog/sync_to_subrepos.sh](.planning/catalog/sync_to_subrepos.sh) — re-run after any catalog edit so vendored copies in `firestarter/tools/catalog/` and `firestarter_app/tools/catalog/` stay byte-identical.

### Existing firmware logging surface (call-sites to convert)
- [firestarter/include/logging_id.h](firestarter/include/logging_id.h) — current `LOG_ID_*` + `LOG_INFO_ID_*` macros (Phase 6 output). Phase 7 adds `LOG_ERROR_ID_*` + `LOG_WARN_ID_*` families here.
- [firestarter/include/logging.h](firestarter/include/logging.h) — legacy macro tower (`log_info_const`, `log_info_format`, `log_warn`, `log_warn_const`, `log_warn_format`, `log_error_const`, `log_error_format`, `log_error_format_buf`, `log_info_P_int`, `log_info_P_char`, `log_error_P_int`, `firestarter_error_response`, `firestarter_warning_response`, `firestarter_error_response_format`, `firestarter_warning_response_format`). **Phase 7 leaves logging.h intact — these macros stay declared so the OK/INIT/MAIN/END + DATA paths still build. Deletion is Phase 9.**
- [firestarter/src/firestarter.cpp](firestarter/src/firestarter.cpp) — 20 active direct call-sites (14 INFO, 6 ERROR). Largest single-file conversion batch. Note the `log_error_format_buf(handle.response_msg, ...)` hybrid at line 176.
- [firestarter/src/operation_utils.cpp](firestarter/src/operation_utils.cpp) — 6 active direct call-sites (4 INFO, 1 WARN, 1 ERROR), ~14 commented-out breadcrumb lines (to delete), AND the `_check_response` dispatcher at lines 321-342 (drop log_* in ERROR/WARN cases; keep OK/DATA branches text-format for Phase 8).
- [firestarter/src/dev_tools.cpp](firestarter/src/dev_tools.cpp) — 6 active direct INFO call-sites. In scope.
- [firestarter/src/eprom_operations.cpp](firestarter/src/eprom_operations.cpp) — 3 active direct `log_error_const` call-sites.
- [firestarter/src/hardware_operations.cpp](firestarter/src/hardware_operations.cpp) — 2 active direct `log_error_const` call-sites.
- [firestarter/src/proms/eprom.cpp](firestarter/src/proms/eprom.cpp) — 2 WARN + 1 ERROR via `firestarter_*_response_format` populate-sites (lines 182, 203, 227).
- [firestarter/src/proms/flash_intel.cpp](firestarter/src/proms/flash_intel.cpp) — 2 WARN + 3 ERROR populate-sites (lines 29, 45, 135, 140, 147).
- [firestarter/src/proms/flash_type_4.cpp](firestarter/src/proms/flash_type_4.cpp) — 1 ERROR populate-site (line 88).
- [firestarter/src/proms/flash_utils.cpp](firestarter/src/proms/flash_utils.cpp) — 1 ERROR populate-site (line 46).
- [firestarter/src/proms/eeprom_28c.cpp](firestarter/src/proms/eeprom_28c.cpp) — 1 ERROR populate-site (line 126).
- [firestarter/src/proms/memory.cpp](firestarter/src/proms/memory.cpp) — 3 ERROR populate-sites (lines 116, 219, 287).

### Firmware emit path (Phase 6 infrastructure to keep using)
- [firestarter/include/rurp_shield.h:132](firestarter/include/rurp_shield.h#L132) — `rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count)` declaration.
- [firestarter/src/boards/rurp_serial_utils.cpp](firestarter/src/boards/rurp_serial_utils.cpp) — weak `rurp_log_id` + `_firestarter_emit_frame` + CRC8 table + MAGIC_PREAMBLE. No changes needed in Phase 7.
- [firestarter/src/boards/uno_rurp_shield.cpp:99-110](firestarter/src/boards/uno_rurp_shield.cpp#L99-L110) — strong Uno override with `com_mode` gate. No changes in Phase 7.
- [firestarter/include/messages.h](firestarter/include/messages.h) — generated header with `MSG_*` ID defines and `MSG_PARAM_COUNT(id)` macro. Phase 7 call-sites reference `MSG_*` symbols from this file.

### Host decoder + parser (consuming the new frames)
- [firestarter_app/firestarter/serial_comm.py](firestarter_app/firestarter/serial_comm.py) — `LogMessage` namedtuple, `MAGIC_PREAMBLE`, `_decode_id_frame`, `_read_and_parse_lines` byte-stream reader. **No code changes in Phase 7** — the decoder is already wired in Phase 6. Phase 7 verifies via end-to-end testing that ERROR/WARN/INFO lines now flow through `_decode_id_frame` instead of `_parse_response_line`.
- [firestarter_app/firestarter/messages.py](firestarter_app/firestarter/messages.py) — generated `CATALOG` dict. Phase 7 consumes this via the decoder.
- [firestarter_app/tests/test_decoder.py](firestarter_app/tests/test_decoder.py) — existing 12-test decoder suite; Phase 7 may extend with end-to-end coverage hitting multiple MSG_* IDs in sequence.

### Test harness (verification surface)
- [firestarter/test/native/avr/test_dispatch/](firestarter/test/native/avr/test_dispatch/) — native Unity tests for `configure_memory` dispatch. May need `host_stubs.cpp` review post-conversion.
- [firestarter/test/native/avr/test_messages/](firestarter/test/native/avr/test_messages/) — Phase 6 wire-frame Unity suite. Already validates `rurp_log_id` emit path.
- [firestarter_app/firestarter_test.sh](firestarter_app/firestarter_test.sh) + [firestarter_app/write_test.sh](firestarter_app/write_test.sh) — bench integration tests. Phase 7 close should run these against the simulator (or real hardware) for the end-to-end "ERROR/WARN/INFO lines render via catalog decoder" success criterion. **Carry-forward awareness:** WARNING-4 schema drift from v1.1 still references deleted `database_generated.json`; out of scope for Phase 7, flag if test scripts must be modified.

### Build + CI
- [firestarter/platformio.ini](firestarter/platformio.ini) — `[env:uno]`, `[env:leonardo]`, `[env:native]`. Build must succeed on all three after each commit.
- [firestarter/.github/workflows/build.yml](firestarter/.github/workflows/build.yml) — catalog drift gate (Phase 6 lines 55-73). Phase 7 should not need workflow edits; catalog-drift behavior tested when D-03 fail-fast triggers.
- [firestarter_app/.github/workflows/ci.yml](firestarter_app/.github/workflows/ci.yml) — host CI; runs `pytest tests/` (Phase 7 may add tests under here).

### Carry-forward awareness (not in scope; just don't break)
- [.planning/debug/fm1608-fresh-chip-baseline.md](.planning/debug/fm1608-fresh-chip-baseline.md) — v1.1 FM1608 byte-0 read bug, parked. Phase 7 doesn't touch the EPROM read path; just don't regress.
- v1.1 DOC-01 (milestone close), WARNING-4 test-script drift — both carried forward from v1.1; out of scope for Phase 7.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`LOG_ID_*` macros** in `logging_id.h` — Phase 6 already provides the wire-frame packer for u8 / u16 / u24 / u32 / BYTES + a zero-param `LOG_ID()`. The new `LOG_ERROR_ID_*` + `LOG_WARN_ID_*` are one-line aliases over `LOG_ID_*` — trivial addition.
- **`LOG_INFO_ID_*` macros** — direct template for the new severity families; copy with the FLAG_VERBOSE gate removed.
- **`rurp_log_id` weak symbol + Uno strong override** — already wired board-side; Phase 7 call-sites don't touch this layer.
- **Catalog `MSG_*` constants** — 55 ERROR/WARN/INFO IDs already allocated in `messages.h`; Phase 7 is essentially a 1:1 substitution exercise (modulo D-03 catalog-gap protocol).
- **Phase 6 `_check_response` already handles binary frames** — the host's `_read_and_parse_lines` accumulator splits text vs binary by magic-preamble detection. ERROR/WARN/INFO frames arriving as binary in Phase 7 flow through `_decode_id_frame` automatically.
- **Phase 6 host pytest infrastructure** (`firestarter_app/tests/`) — Phase 7 can extend with end-to-end / sequence tests.

### Established Patterns

- **Each populate site = emit + state-set.** The pattern across `proms/*.cpp` is to do `firestarter_error_response_format("...", args)` which both formats into `response_msg` AND sets `response_code = ERROR`. The new pattern is two adjacent lines: `LOG_ERROR_ID_*(MSG_*, args);` followed by `handle->response_code = RESPONSE_CODE_ERROR;`. The planner may choose to package this into a single macro (`LOG_ERROR_RESPONSE(MSG, ...)` that does both) — see D-02 multi-param composer note — but the operator did not lock that; recommend two-line form for clarity.
- **`MSG_*` symbolic naming** — catalog uses `MSG_ERR_*`, `MSG_WARN_*`, `MSG_INFO_*` prefixes. The MSG name carries severity; macro name does too. Redundant but improves grep-ability — keep both.
- **`is_flag_set(FLAG_VERBOSE)` gate** is INFO-only. ERROR + WARN always emit, regardless of verbose flag. Don't accidentally copy the gate into the new macros.
- **Catalog format strings are AUTHORITATIVE.** When converting, if the current code's format differs from the catalog (punctuation, casing, ordering), the call-site changes — the catalog does not. (D-03 sub-case.)

### Integration Points

- **`logging_id.h`** — single point of entry for new ERROR/WARN macro families; mirrors INFO additions from Phase 6.
- **`_check_response` in `operation_utils.cpp:329-350`** — only the ERROR + WARNING `case` bodies change; OK + DATA branches stay (Phase 8 / out-of-scope).
- **Each `proms/*.cpp` populate site** — surgical replacement: one or two lines change, the surrounding logic stays.
- **No host-code changes** — Phase 6 already wired `_decode_id_frame` + the byte-stream `_read_and_parse_lines`. Phase 7 is firmware-only by design. Verification of host rendering is via existing pytest infrastructure + bench integration.
- **No CI workflow edits** — catalog drift gate already enforces messages.toml consistency. If D-03 fires (catalog gap discovered), the catalog-edit commit goes through the existing drift gate naturally.

</code_context>

<specifics>
## Specific Ideas

- **Macros mirror INFO surface symmetrically** (D-02): the operator wants reading `LOG_ERROR_ID_U16(MSG_ERR_FOO, val)` next to `LOG_INFO_ID_U16(MSG_INFO_BAR, val)` and the severity should jump out. Don't shortcut by reusing `LOG_ID_*` for ERROR/WARN — the surface is the readability win even though the implementation is a one-line alias.
- **The populate-site refactor was anticipated by Phase 6 RESEARCH** (line 204) and is therefore locked, not gray. The gray-area decision was *how aggressively to clean up `_check_response`*, not *whether to refactor populate sites*. Keep this distinction in the planner's mind so it doesn't surface as a "should we?" question again.
- **Locked-catalog policy is meant to surface Phase 6 gaps loudly** (D-03). The operator explicitly prefers fail-fast over fluid because the Phase 6 catalog is supposed to be complete — any drift is a signal worth a separate commit and explanation, not silent absorption.
- **`dev_tools.cpp` is in-binary, therefore in-scope** (D-04a). The operator's mental model: "if it links into the firmware image, it counts toward flash and it counts toward the SC#1 grep." No carve-outs.
- **Commented-out breadcrumbs are technical debt that decays into misinformation** (D-04b). Better to delete now while we're already touching the file than to leave them for Phase 9 to handle (Phase 9 is about deleting macros, not chasing comments).

</specifics>

<deferred>
## Deferred Ideas

- **Commit cadence / batching strategy** — operator did not lock this; planner picks. Recommended interpretation: macro-additions commit first (infrastructure), then per-PROM-module commits for populate-site conversions, then per-file commits for direct-log conversions (~12 commits total). Planner may collapse if a batch is genuinely trivial.
- **Multi-param composer macros** — catalog has at least three multi-param ERROR/WARN formats. Planner picks between purpose-built composers (`LOG_ERROR_ID_U24_U8_U8` etc.) and raw `LOG_ID_BYTES(MSG, (uint8_t[]){...}, n)`. Lean: raw escape hatch for the edge cases, no proliferation of multi-param wrappers.
- **`LOG_ERROR_RESPONSE(MSG, ...)` packaging** — combining emit + response_code-set into a single macro at populate sites. Operator did not lock; recommended two-line form (D-02 specifics) for clarity. Planner may revisit if call-site noise becomes severe.
- **Tests against firmware-simulator harness for end-to-end ERROR/WARN/INFO rendering** — SC#2 references "firmware-simulator harness" but doesn't define it concretely. Planner picks: extend the existing pytest decoder suite with multi-frame sequences, run bench integration via `firestarter_test.sh` against real hardware (mirroring v1.1 Phase 4 patterns), or both.
- **`handle->response_msg` buffer field deletion** — vestigial after Phase 7 (OK/DATA still use it). Final removal is Phase 9 territory.

</deferred>

---

*Phase: 7-Convert ERROR + WARN + INFO Call-Sites*
*Context gathered: 2026-05-18*
