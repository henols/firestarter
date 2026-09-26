---
title: Log macro derives response_code from the message severity band
trigger_condition: after Phase 117 lands (it rewrites eeprom_28c.cpp, which holds 6 of the 29 call sites), OR the next time a handler is found logging ERROR/WARN without a matching response_code
planted_date: 2026-07-28
status: dormant
---

# Log macro derives response_code from the message severity band

Collapse the repeated `LOG_*_ID(...)` + `handle->response_code = RESPONSE_CODE_*`
pair into a single handler-layer macro that derives the response code from the
message ID's severity band, so the logged severity and the response code can
never disagree.

Today, every handler call site writes the pair by hand:

```c
if (is_flag_set(FLAG_FORCE)) {
    LOG_WARN_ID_U32(MSG_WARN_MEM_SIZE_TOO_SMALL, (uint32_t)handle->mem_size);
    handle->response_code = RESPONSE_CODE_WARNING;
} else {
    LOG_ERROR_ID_U32(MSG_ERR_MEM_SIZE_TOO_SMALL, (uint32_t)handle->mem_size);
    handle->response_code = RESPONSE_CODE_ERROR;
}
```

Target:

```c
LOG_RESP_ID_U32(handle,
    is_flag_set(FLAG_FORCE) ? MSG_WARN_MEM_SIZE_TOO_SMALL : MSG_ERR_MEM_SIZE_TOO_SMALL,
    (uint32_t)handle->mem_size);
```

## Grounding facts (verified 2026-07-28, v1.22 branch)

**`response_code` is a per-callback return channel, not a command status.**
`_check_response()` (`firestarter/src/operation_utils.cpp:330-351`) reads it and
then unconditionally resets it to `RESPONSE_CODE_OK` before the next callback
runs. Consequence: do **not** build a cross-command high-water mark — the
callback boundary is the correct reset point. Monotonicity, if wanted at all,
is only meaningful *within* one callback.

**The severity macros are pure aliases today.** `logging_id.h:105-119` — both
`LOG_ERROR_ID_U32` and `LOG_WARN_ID_U32` expand to the identical `LOG_ID_U32`.
The severity in the name is documentary; nothing consumes it. Free headroom.

**Severity is already first-class and banded.** `tools/catalog/messages.toml`
carries `severity = "WARN" | "ERROR"` per entry, and `messages.h` IDs are banded:
OK `0x01-0x0F`, INIT `0x10`, MAIN `0x20`, END `0x30`, INFO `0x40-0x5F`,
WARN `0x80-0x9F`, ERROR `0xA0-0xDF`, DATA `0xE0-0xEF`, DEBUG `0xF0`.

**The call sites split cleanly along the handler/framework boundary:**

| Layer | ERROR/WARN log sites | Sets `response_code` |
|---|---|---|
| `src/proms/*` (handler callbacks) | 29 | 29 — all of them |
| everything else (framework) | 16 | 0 — none |

Per-file (handler layer): `eeprom_28c.cpp` 6, `eprom.cpp` 7, `flash_intel.cpp` 9,
`flash_utils.cpp` 3, `memory.cpp` 2, `flash_5v_page.cpp` 1, `not_implemented.cpp` 1.
Framework layer: `firestarter.cpp` 8, `eprom_operations.cpp` 3,
`operation_utils.cpp` 3, `hardware_operations.cpp` 2.

The framework sites signal failure by **return value**; their `response_code`
would be reset before anyone read it. So a global fold into `LOG_ERROR_ID_*`
writes dead state at those 16 sites — it must be scoped to the handler layer.

**All 29 handler sites are mechanical to convert.** The ~5 sites where the log
sits inside a nested block with the store after it (`memory.cpp:322`,
`eeprom_28c.cpp:354`/`:419`, `eprom.cpp:190`, `flash_5v_page.cpp:126`) are plain
scope blocks for a `_b[]` byte-array temporary, not conditionals.

## Shape (rough)

```c
/* logging_id.h — handler layer only */
static inline void _resp_from_id(firestarter_handle_t* h, uint8_t id) {
    if (id >= MSG_BAND_ERROR_MIN && id <= MSG_BAND_ERROR_MAX)     h->response_code = RESPONSE_CODE_ERROR;
    else if (id >= MSG_BAND_WARN_MIN && id <= MSG_BAND_WARN_MAX)  h->response_code = RESPONSE_CODE_WARNING;
    /* OK/INIT/MAIN/END/INFO/DATA/DEBUG: leave untouched */
}

#define LOG_RESP_ID(h, id)             do { LOG_ID(id);              _resp_from_id((h), (id)); } while (0)
#define LOG_RESP_ID_U8(h, id, p1)      do { LOG_ID_U8((id), (p1));   _resp_from_id((h), (id)); } while (0)
#define LOG_RESP_ID_U16(h, id, p1)     do { LOG_ID_U16((id), (p1));  _resp_from_id((h), (id)); } while (0)
#define LOG_RESP_ID_U32(h, id, p1)     do { LOG_ID_U32((id), (p1));  _resp_from_id((h), (id)); } while (0)
#define LOG_RESP_ID_BYTES(h, id, b, n) do { LOG_ID_BYTES((id),(b),(n)); _resp_from_id((h), (id)); } while (0)
```

## Key decisions (and why)

- **Explicit `handle` argument, not implicit capture.** An implicit-`handle`
  macro is blocked anyway: `firestarter.cpp:32` declares the handle as a
  file-scope struct **by value**, so sites like `:160` and `:249` spell
  `handle.cmd`, not `handle->cmd` — one macro can't spell both. Explicit costs
  one token per site and buys the layer boundary: the macro cannot be misapplied
  in the framework layer.
- **Derive from the ID band, not the macro name.** Keying on `LOG_ERROR_*` →
  ERROR still lets a site log WARN and set ERROR. Deriving from the ID makes
  that combination unrepresentable.
- **Codegen emits the band constants AND asserts the invariant.** `messages.h`
  is codegen-generated from `messages.toml` (never hand-edit — see the drift CI
  gate). Have `codegen.py` emit `MSG_BAND_{WARN,ERROR}_{MIN,MAX}` and fail the
  build if any entry's declared `severity` disagrees with its ID band. This
  turns a convention into a machine-checked invariant.
- **DATA band must NOT map.** `RESPONSE_CODE_DATA` is set deliberately at
  `memory.cpp:420`; progress frames (`LOG_DATA_ID_U32_U32` at
  `operation_utils.cpp:293`) must not set it as a side effect.
- **Leave `LOG_ERROR_ID_*` / `LOG_WARN_ID_*` alone.** They stay the framework
  layer's spelling. No behavior change at those 16 sites.

## Payoff

- **Correctness:** logged severity and response code cannot diverge. Removes a
  whole "forgot the second line" defect class from a fail-safe-critical path.
- **Size:** 29 hand-written stores deleted; 6 `if (FLAG_FORCE)` warn/error forks
  flatten to a single ternary on the message ID.
- **Cost:** ~zero on AVR. Every ID is a compile-time constant, so `_resp_from_id`
  constant-folds to exactly the store written by hand today; the ternary sites
  fold to a 2-way select.

## Sequencing

Phase 117 is actively rewriting `eeprom_28c.cpp` (remap-aware 0x0D emitter +
honest completion signal), which owns 6 of the 29 sites. Land 117 first or this
gets rebased through it.

## Open

- Naming: `LOG_RESP_ID_*` signals "this writes state" reasonably well, but
  something stronger (`LOG_SET_RESP_ID_*`) may read better at the call site.
- Whether the 4 WARN/ERROR twin pairs that share an identical `format` and
  `params` (`CHIP_ID_MISMATCH`, `MEM_SIZE_TOO_SMALL`, `VPP_HIGH`,
  `FL4_BOOT_BLOCK_LOCKED`) should be declared as pairs in `messages.toml` so
  codegen can emit the ternary itself — deferred; the ternary is already one line.
