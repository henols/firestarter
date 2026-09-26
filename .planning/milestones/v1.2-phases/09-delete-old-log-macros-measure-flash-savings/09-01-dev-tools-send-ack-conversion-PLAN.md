---
phase: 09-delete-old-log-macros-measure-flash-savings
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - firestarter/src/dev_tools.cpp
autonomous: true
requirements:
  - LFW-03
requirements_addressed:
  - LFW-03
tags:
  - logging
  - firmware
  - deletion-precondition
user_setup: []
must_haves:
  truths:
    - "dev_tools.cpp:108 (dt_set_registers) emits an id-frame for MSG_OK_READY (0x01) instead of send_ack(\"\")"
    - "dev_tools.cpp:154 (dt_set_address) emits an id-frame for MSG_OK_READY (0x01) instead of send_ack(\"\")"
    - "After this plan lands, zero callers of the send_ack macro remain anywhere in firmware/src + firmware/include + firmware/lib — the precondition for Plan 02 deletion is met"
    - "pio run -e uno and pio run -e leonardo build clean after the conversion"
    - "pio test -e native -f '*test_dispatch*' stays green (22+ PASS)"
  artifacts:
    - path: "firestarter/src/dev_tools.cpp"
      provides: "Two LOG_OK_ID(MSG_OK_READY) call-sites replacing send_ack(\"\") at lines 108 + 154"
      contains: "LOG_OK_ID(MSG_OK_READY)"
  key_links:
    - from: "firestarter/src/dev_tools.cpp"
      to: "firestarter/include/logging_id.h"
      via: "LOG_OK_ID macro expansion to rurp_log_id with MSG_OK_READY (0x01)"
      pattern: "LOG_OK_ID\\(MSG_OK_READY\\)"
---

<objective>
Convert the last two `send_ack("")` callers in `firestarter/src/dev_tools.cpp` to the Phase 8 id-frame form `LOG_OK_ID(MSG_OK_READY)`. This plan is the precondition for Plan 02's deletion of the entire `send_ack` / `send_ack_const` / `rurp_log` / `rurp_log_P` macro tower — until both call-sites are migrated, deleting the macros would break compilation.

Purpose: unblock Wave 2 (atomic legacy-deletion + LFW-05 inline + version bump). Implements decision D-04 from `09-CONTEXT.md`.
Output: A single firmware commit converting two 1-line call-sites; firmware builds clean on both AVR targets and the native dispatch test suite stays green.
</objective>

<execution_context>
@/workspaces/firestarter_prom/.claude/get-shit-done/workflows/execute-plan.md
@/workspaces/firestarter_prom/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-CONTEXT.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-RESEARCH.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-PATTERNS.md
@firestarter/CLAUDE.md
@firestarter/src/dev_tools.cpp
@firestarter/include/logging_id.h
@firestarter/src/hardware_operations.cpp

<interfaces>
<!-- Key contracts the executor needs. Extracted from the codebase. -->

From firestarter/include/logging.h (being deleted in Plan 02 — DO NOT touch here):
```
extern const char LOG_OK_MSG[] PROGMEM;
#define send_ack(msg)        rurp_log(LOG_OK_MSG, msg)
#define send_ack_const(msg)  rurp_log_P(LOG_OK_MSG, PSTR(msg))
```

From firestarter/include/logging_id.h (Phase 7/8 — the new ID-frame macros):
```
// LOG_OK_ID expands to rurp_log_id(msg_id, NULL, 0) for zero-param messages.
// MSG_OK_READY = 0x01, severity=OK, format="Ready", wire_format=id_frame, params=[]
LOG_OK_ID(MSG_OK_READY);
```

From firestarter/src/hardware_operations.cpp:40-42 (the live analog — Phase 8 commit `ea2a3fb` shipped this exact conversion for MSG_OK_READY):
```cpp
// Send a ready signal to the client to prompt it for the first ACK.
// This establishes a handshake and avoids a race condition.
LOG_OK_ID(MSG_OK_READY);
```

Current state of dev_tools.cpp includes (lines 14-15):
```cpp
#include "logging.h"      // line 14 — provides send_ack (DROP in Plan 02, NOT this plan)
#include "logging_id.h"   // line 15 — provides LOG_OK_ID + MSG_OK_READY (KEEP)
```
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Convert dev_tools.cpp:108 (dt_set_registers) — send_ack("") → LOG_OK_ID(MSG_OK_READY)</name>
  <read_first>
    - firestarter/src/dev_tools.cpp (the file being modified — read lines 72-130 to see the dt_set_registers function context around line 108)
    - firestarter/src/hardware_operations.cpp lines 38-46 (the live analog for LOG_OK_ID(MSG_OK_READY) shipped in Phase 8)
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-CONTEXT.md §"dev_tools.cpp send_ack(\"\") sites" — D-04 + D-05
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-RESEARCH.md §"Deletion Inventory" → "send_ack(msg) — macro" + §"Catalog Entry Status" → "MSG_OK_READY (0x01) — KEEP, reuse"
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-PATTERNS.md §"Pattern Assignment 2" (the before/after diff template)
  </read_first>
  <files>firestarter/src/dev_tools.cpp</files>
  <behavior>
    - Before: `dev_tools.cpp:108` (inside `dt_set_registers`) contains `send_ack("");`
    - After: same line contains `LOG_OK_ID(MSG_OK_READY);  // D-04: was send_ack(""); semantics ≈ "setup done, waiting on user button"`
    - The change is a 1-line surgical edit; no surrounding code changes; the `dt_set_registers` function body otherwise unchanged
    - The `#include "logging.h"` at line 14 stays (will be removed atomically in Plan 02); `#include "logging_id.h"` at line 15 already provides LOG_OK_ID and MSG_OK_READY
  </behavior>
  <action>
    At `firestarter/src/dev_tools.cpp:108` (inside `dt_set_registers`, the actual function name per `09-RESEARCH.md` "Deletion Inventory" — CONTEXT.md's `dt_dump_register` is a typo): replace the single line `send_ack("");` with `LOG_OK_ID(MSG_OK_READY);  // D-04: was send_ack(""); semantics ≈ "setup done, waiting on user button"`. Do NOT touch the `#include "logging.h"` at line 14 (Plan 02 owns the include sweep). Do NOT touch line 154 in this task (Task 2 owns it). Match the comment voice of `hardware_operations.cpp:40-42` (the live analog for this conversion shipped in Phase 8 commit `ea2a3fb`).
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_prom/firestarter && pio run -e leonardo 2>&1 | tail -5 | grep -E '(SUCCESS|Flash:)' &amp;&amp; pio run -e uno 2>&1 | tail -5 | grep -E '(SUCCESS|Flash:)' &amp;&amp; grep -c 'LOG_OK_ID(MSG_OK_READY)' src/dev_tools.cpp</automated>
  </verify>
  <done>
    - `grep -n 'send_ack' firestarter/src/dev_tools.cpp | grep -v '^.*//' | wc -l` returns exactly 1 (line 154 still has it; Task 2 handles that)
    - `grep -c 'LOG_OK_ID(MSG_OK_READY)' firestarter/src/dev_tools.cpp` returns exactly 1
    - `pio run -e leonardo` reports SUCCESS
    - `pio run -e uno` reports SUCCESS
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Convert dev_tools.cpp:154 (dt_set_address) — send_ack("") → LOG_OK_ID(MSG_OK_READY)</name>
  <read_first>
    - firestarter/src/dev_tools.cpp (read lines 130-167 to see the dt_set_address function context around line 154)
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-PATTERNS.md §"Pattern Assignment 2" (before/after diff template)
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-CONTEXT.md §"dev_tools.cpp send_ack(\"\") sites" — D-04
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-RESEARCH.md §"Deletion Inventory" → "send_ack(msg) — macro" (confirms only callers are :108 and :154)
  </read_first>
  <files>firestarter/src/dev_tools.cpp</files>
  <behavior>
    - Before: `dev_tools.cpp:154` (inside `dt_set_address`) contains `send_ack("");`
    - After: same line contains `LOG_OK_ID(MSG_OK_READY);  // D-04: was send_ack(""); semantics ≈ "setup done, waiting on user button"`
    - After this task, `grep -n 'send_ack' firestarter/src/` returns ZERO production-code hits (logging.h still defines the macro; Plan 02 deletes that)
  </behavior>
  <action>
    At `firestarter/src/dev_tools.cpp:154` (inside `dt_set_address`): replace the single line `send_ack("");` with `LOG_OK_ID(MSG_OK_READY);  // D-04: was send_ack(""); semantics ≈ "setup done, waiting on user button"`. Same edit shape as Task 1. After this task, `dev_tools.cpp` should contain exactly 2 occurrences of `LOG_OK_ID(MSG_OK_READY)` (the two converted sites) and zero occurrences of `send_ack(` (the macro definition still lives in `logging.h`, but no caller invokes it from `dev_tools.cpp` anymore).
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_prom/firestarter &amp;&amp; pio run -e leonardo 2>&amp;1 | tail -5 | grep SUCCESS &amp;&amp; pio run -e uno 2>&amp;1 | tail -5 | grep SUCCESS &amp;&amp; [ "$(grep -c 'LOG_OK_ID(MSG_OK_READY)' src/dev_tools.cpp)" = "2" ] &amp;&amp; [ "$(grep -c 'send_ack(' src/dev_tools.cpp)" = "0" ] &amp;&amp; pio test -e native -f '*test_dispatch*' 2>&amp;1 | tail -3 | grep -E '(PASSED|22|23|24)'</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c 'LOG_OK_ID(MSG_OK_READY)' firestarter/src/dev_tools.cpp` returns exactly 2
    - `grep -c 'send_ack(' firestarter/src/dev_tools.cpp` returns exactly 0
    - `grep -rln 'send_ack(' firestarter/src/ firestarter/lib/` returns ZERO files (the production tree has zero callers; `logging.h` macro definition is in `firestarter/include/` and is exempt from this grep since the include tree is not searched here — Plan 02 handles header cleanup)
    - `cd firestarter && pio run -e leonardo` reports SUCCESS with a Flash line
    - `cd firestarter && pio run -e uno` reports SUCCESS with a Flash line
    - `cd firestarter && pio test -e native -f '*test_dispatch*'` reports 22+ PASS (unchanged from Phase 8 close baseline)
  </acceptance_criteria>
  <done>
    - Both `send_ack("")` call-sites in `dev_tools.cpp` are converted to `LOG_OK_ID(MSG_OK_READY)`
    - Both AVR builds compile clean
    - Native dispatch test suite is green
    - The precondition for Plan 02's `send_ack` / `send_ack_const` / `rurp_log` / `rurp_log_P` deletion is met (zero callers remain in production sources)
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| firmware → host (serial wire) | The dev_tools state-machine `OK:` ack crosses this boundary. The visible token changes from `OK: ` (empty body) to `OK: Ready` (id-frame decoded by host catalog). |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-09-01-01 | Tampering | observable change in dev_tools `OK:` body | accept | RESEARCH.md §"Risks & Landmines #4" verified zero operator-side automation scripts (`firestarter_test.sh`, `write_test.sh`, host pytest tree) depend on the empty `OK: ` body. The host's `expect_ack()` discards the body string. Change is purely operator-cosmetic. |
| T-09-01-02 | Information Disclosure | id-frame for MSG_OK_READY exposes a new emit context (dev_tools dt_set_registers + dt_set_address) | accept | MSG_OK_READY is a context-free `id+severity` token (zero params); no new information is disclosed by emitting it from additional sites. The catalog already supports multi-site emission (already emitted from `hardware_operations.cpp:42`). |
| T-09-01-03 | Build-cache poisoning | partial conversion of one of two send_ack sites leaves the build broken for SERIAL_DEBUG configurations or fails the LFW-03 grep gate | mitigate | Task 1 and Task 2 are sequenced inside the same plan; both must land before Plan 02 begins. Plan 02 explicitly grep-asserts that no `send_ack(` callers remain in `firestarter/src/` before deleting the macro definitions. |
</threat_model>

<verification>
### Plan-level acceptance gate

Run after both tasks complete:

```bash
cd /workspaces/firestarter_prom/firestarter
# 1. Zero send_ack callers in production sources
[ "$(grep -rn 'send_ack(' src/ | grep -v '^.*\.h:' | wc -l)" = "0" ] || { echo "FAIL: send_ack callers still present"; exit 1; }
# 2. Two LOG_OK_ID(MSG_OK_READY) hits in dev_tools.cpp (Task 1 + Task 2)
[ "$(grep -c 'LOG_OK_ID(MSG_OK_READY)' src/dev_tools.cpp)" = "2" ] || { echo "FAIL: conversion count wrong"; exit 1; }
# 3. Both AVR targets build
pio run -e leonardo 2>&1 | tail -5 | grep -q SUCCESS || { echo "FAIL: leonardo build"; exit 1; }
pio run -e uno 2>&1 | tail -5 | grep -q SUCCESS || { echo "FAIL: uno build"; exit 1; }
# 4. Native dispatch tests green
pio test -e native -f '*test_dispatch*' 2>&1 | tail -3 | grep -qE '(PASSED|OK)' || { echo "FAIL: native dispatch"; exit 1; }
echo "PLAN 01 GREEN"
```
</verification>

<success_criteria>
- Both `send_ack("")` callers in `firestarter/src/dev_tools.cpp` (lines 108 + 154) converted to `LOG_OK_ID(MSG_OK_READY)` per D-04
- `pio run -e uno` and `pio run -e leonardo` both report SUCCESS with Flash lines
- `pio test -e native -f '*test_dispatch*'` reports 22+ PASS (no regression vs Phase 8 close)
- Production tree has ZERO `send_ack(` callers remaining (verified by grep gate in `<verification>`)
- The Plan 02 atomic deletion is unblocked
</success_criteria>

<output>
After completion, create `.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-01-SUMMARY.md` recording:
- Both conversions completed with line numbers
- AVR build results (Leonardo + Uno Flash percentages — informational, not gating)
- Native dispatch test result (22+ PASS)
- Confirmation that `grep -rn 'send_ack(' firestarter/src/` returns zero hits (Plan 02 precondition met)
</output>
