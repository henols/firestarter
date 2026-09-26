---
phase: 183-flash4-erase-refusal-the-ae29f2008-classification
reviewed: 2026-09-11T00:00:00Z
depth: standard
files_reviewed: 11
files_reviewed_list:
  - firestarter/CLAUDE.md
  - firestarter/PROTOCOLS.md
  - firestarter/scripts/check_erase_no_vpp.py
  - firestarter/src/eprom_operations.cpp
  - firestarter/src/proms/flash_5v_page.cpp
  - firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp
  - firestarter/tests/fixtures/planted_erase_no_vpp_ctrl_write.cpp
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/flash4_erase_gate.py
  - firestarter_app/tests/__snapshots__/test_characterization.ambr
  - firestarter_app/tests/test_flash4_erase_gate.py
findings:
  critical: 0
  warning: 3
  info: 2
  total: 5
status: issues_found
---

# Phase 183: Code Review Report

**Reviewed:** 2026-09-11
**Depth:** standard
**Files Reviewed:** 11 (2 submodule diffs: `firestarter` `origin/beta..HEAD`, `firestarter_app` `4adf719..HEAD`)
**Status:** issues_found

## Summary

Phase 183 wires a new pure-predicate policy module (`flash4_erase_gate.py`) into
`cli_handlers.erase` to refuse `firestarter erase` on flash4 (algorithm `0x05`) parts
before the serial port opens, and deletes the dead 12 V bulk-erase routine
(`flash_5v_page_erase_execute`) from the firmware. Both halves were exercised directly,
not just read: the Python gate's 22 pytest cases pass (including the real-database
coupling test and the CLI end-to-end tests), the firmware native `test_val_5v_page` suite
(15 cases) and the full `pio test -e native` run (185 cases across 17 suites) pass, `uno`
builds clean, and `scripts/check_erase_no_vpp.py` still correctly PASSes the real
`eeprom28c_erase_execute` body and FAILs the planted-violation fixture with the same
exit-code contract as before.

The host-side gate placement, exit-code contract, and fail-open predicate are all
correct: `is_flash4` cannot raise or misclassify on any wire-dict shape reachable from
`resolve_chip`, the gate runs strictly before `jp5_gate` and before
`EpromOperator.erase_eprom` (which is the first call that opens the serial port), and
`--ignore-unsupported` changes only the exit code, not the printed line — all confirmed
by the test suite and by reading `cli_handlers.erase` end to end. The firmware deletion
is safe: `CMD_ERASE` for protocol `0x05` now leaves `firestarter_operation_main` at its
`configure_memory`-reset `NULL`, and `eprom_erase()` in `eprom_operations.cpp` (unchanged,
as intended) refuses before that pointer is ever dereferenced because `FLAG_CAN_ERASE` is
permanently clear for algorithm 5 host-side — verified by reading both the host derivation
(`database.py:579-581`) and the firmware guard (`eprom_operations.cpp:36-39`).

Three quality issues remain from the deletion and the documentation edit, and two minor
items are worth a maintainer's attention; none of them change externally observable
behavior or reopen the hazard the phase closes.

## Warnings

### WR-01: `check_erase_no_vpp.py`'s rewritten rationale asserts something false about the codebase

**File:** `firestarter/scripts/check_erase_no_vpp.py:26-29`
**Issue:** This phase rewrote the checker's "Proximity, not absence" paragraph. The old
text named a *specific* function (`flash_5v_page_erase_execute`) as the one place in the
tree matching the hazard shape, which was accurate and scoped. The new text generalizes:

> "No source file in this tree implements a hardware 12V-on-OE erase path: nothing
> asserts `CTRL_VPE_ENABLE` and the VPP boost regulator around a `rurp_chip_enable()`
> / `rurp_chip_disable()` bracket anywhere in the codebase today."

The first clause ("12V-on-OE") is true — that specific AT28C256 mechanism is gone. But
the second clause, phrased as its elaboration, is not scoped to OE at all, and it is
false: `eprom_internal_erase()` in `firestarter/src/proms/eprom.cpp:541-561` — untouched
by this phase, a legitimate existing feature for the 0x07/0x08/0x0B EE-EPROM erase
path — does exactly this:
```c
handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);
...
handle->firestarter_set_control_register(handle, CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE, 1);
...
rurp_chip_enable();
...
rurp_chip_disable();
```
This is a documentation-accuracy defect in the rationale for a safety-critical gate, not
a defect in the gate's executable mechanism — the regex/brace-matching logic is untouched
and still correctly PASSes the real function and FAILs the planted fixture (verified by
running both). But a future reader relying on this paragraph to judge "is there anywhere
else in this codebase I should worry about a VPE+regulator+chip-enable-bracket hazard
shape appearing near an erase handler" will be told, incorrectly, that there is nowhere
else — when `eprom.cpp` is right there.
**Fix:** Re-scope the sentence to what is actually true, e.g.: "No source file
implements the AT28C256 hardware 12V-on-OE erase path specifically; the structurally
similar `CTRL_VPE_ENABLE` + VPP-regulator + chip-enable/disable pattern does still exist
in `eprom.cpp`'s `eprom_internal_erase()`, for the unrelated and legitimate 0x07/0x08/0x0B
EE-EPROM erase feature — this checker does not and should not guard that function; it
guards only `eeprom28c_erase_execute`."

### WR-02: `flash_5v_page_write_init` is now dead branching around an empty body

**File:** `firestarter/src/proms/flash_5v_page.cpp:69-76`
**Issue:** After the erase-on-write block was deleted, the function is:
```c
void flash_5v_page_write_init(firestarter_handle_t* handle) {
    if (!is_operation_in_progress(handle)) {
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
    // No pre-write blank check: ...
}
```
`is_operation_in_progress()` is a pure `const`-handle accessor (`operation_utils.h:44`)
with no side effects, and the function body after the nested `if` is empty. Both branches
of the conditional — the early `return` and falling through to the end of the function —
are now behaviorally identical: nothing happens either way. The conditional is 100% dead
weight left over from the deletion; it was gating the removed erase-on-write call, not the
blank-check removal (which predates this phase). This is confusing: it reads as if the
function is still doing conditional work, when it is unconditionally a no-op.
**Fix:** Either collapse to an explicit no-op with a one-line note on why the function
(and its assignment to `firestarter_operation_init`) must still exist — e.g.
```c
void flash_5v_page_write_init(firestarter_handle_t* handle) {
    (void)handle;
}
```
— or, if the test that drives `firestarter_operation_init` unguarded
(`test_5v_page_write_init_no_vpp_with_flag_can_erase_set` /
`test_5v_page_write_init_no_blank_check_erase02`) can be adapted to tolerate a `NULL`
init pointer, drop the function and its dispatch assignment entirely instead of leaving
dead conditional logic in a firmware file (flash-size-sensitive per this repo's own
`CLAUDE.md`).

### WR-03: Now-unused `rurp_pinout.h` include left in `flash_5v_page.cpp`

**File:** `firestarter/src/proms/flash_5v_page.cpp:17`
**Issue:** `flash_5v_page_erase_execute` was the only user in this file of any
`CTRL_VPP_*`/`CTRL_VPE_*`/`CONTROL_REGISTER` symbol from `rurp_pinout.h`. After its
deletion, nothing in `flash_5v_page.cpp` references anything from that header (confirmed
by grep across the whole file). The include compiles fine (headers don't warn as unused)
but is now dead weight left over from an incomplete deletion.
**Fix:** Remove `#include "rurp_pinout.h"` from `flash_5v_page.cpp`.

## Info

### IN-01: Superfluous `delay()` stub added to `test_val_5v_page.cpp`'s `setUp()`

**File:** `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp:89`
**Issue:** This phase added `When(Method(ArduinoFake(), delay)).AlwaysReturn();` to
`setUp()`. No code path remaining in `flash_5v_page.cpp` calls `delay()` (only
`delayMicroseconds()`, already stubbed) — the only two `delay()` call sites in the file
were inside the now-deleted `flash_5v_page_erase_execute`. The mock has nothing to
intercept and is dead defensive setup.
**Fix:** Drop the line, or leave a one-line note that it is deliberately harmless
belt-and-braces in case a future handler in this file calls `delay()`.

### IN-02: Two internal callers still reach `EpromOperator.erase_eprom` without the new pre-connect gate

**File:** (adjacent, not in this phase's file list) `firestarter_app/firestarter/eprom_operations.py` (`write_cycle_eprom`) and `firestarter_app/firestarter/chip_test.py` (dev-test harness)
**Issue:** `flash4_erase_gate` is wired only into `cli_handlers.erase`. Two other internal
call sites invoke `EpromOperator.erase_eprom()` directly — `write_cycle_eprom`'s per-cycle
erase step and the `dev test` chip-test harness — and neither goes through
`chip_resolver.resolve_chip` → `flash4_erase_gate.is_flash4` first. For a flash4 part,
both still open the serial connection ("Connecting... OK") before being refused by the
firmware's `FLAG_CAN_ERASE` backstop — not a safety regression (the backstop holds, as
verified), but it means the phase's own stated motivation ("the operator only discovered
that after `Connecting... OK`, which reads like a malfunction rather than a correct
refusal") is only fixed for the direct `firestarter erase` CLI path, not for these two
call sites.
**Fix:** Out of this phase's stated scope, but worth a backlog note if the same UX
problem matters for `dev test`/`write-cycle` flows on flash4 parts.

---

_Reviewed: 2026-09-11_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
