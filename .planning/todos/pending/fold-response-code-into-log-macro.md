---
id: fold-response-code-into-log-macro
title: Fold response_code into the handler-layer log macro (derive from ID band)
captured: 2026-07-28
status: pending
type: refactor
priority: medium
source: /gsd-explore 2026-07-28 (seeds/logging-macro-derives-response-code.md)
blocked_by: Phase 117 (rewrites eeprom_28c.cpp — 6 of the 29 call sites)
---

# Fold `response_code` into the handler-layer log macro

Every handler in `firestarter/src/proms/` hand-writes the same two-line pair —
29 times:

```c
LOG_ERROR_ID_U32(MSG_ERR_MEM_SIZE_TOO_SMALL, (uint32_t)handle->mem_size);
handle->response_code = RESPONSE_CODE_ERROR;
```

Nothing enforces that the two agree. A site can log ERROR and set WARNING, or
log and forget the store entirely, and it compiles clean. This is the fail-safe
path (VPP checks, chip-ID mismatch, verify, blank-check), so a silent
severity/response divergence is the wrong defect class to leave representable.

## Fix

Add a handler-scoped macro family that takes the handle explicitly and derives
the response code from the message ID's severity band (WARN `0x80-0x9F`,
ERROR `0xA0-0xDF`):

```c
LOG_RESP_ID_U32(handle,
    is_flag_set(FLAG_FORCE) ? MSG_WARN_MEM_SIZE_TOO_SMALL : MSG_ERR_MEM_SIZE_TOO_SMALL,
    (uint32_t)handle->mem_size);
```

Full design, grounding facts, and the four decisions (explicit handle; derive
from ID band not macro name; codegen emits the band constants and asserts
`severity` ↔ band; DATA band must not map) are in
`.planning/seeds/logging-macro-derives-response-code.md`.

## Scope

- 29 call sites, all under `src/proms/` — all mechanical (the nested blocks
  around the log calls are `_b[]` scope, not conditionals).
- Do **not** touch the 16 sites outside `src/proms/`. Those signal failure by
  return value, and `_check_response()` (`src/operation_utils.cpp:330-351`)
  resets `response_code` to OK after every callback, so a store there is dead.
- `messages.h` is codegen-generated — band constants go in
  `tools/catalog/codegen.py` + `messages.toml`, never hand-edited.
- Existing native suites already assert `h.response_code` on locally
  constructed handles; they are the regression net.

## Sequencing

Blocked on Phase 117 (remap-aware 0x0D emitter + honest completion signal),
which is actively rewriting `eeprom_28c.cpp`. Land that first.
