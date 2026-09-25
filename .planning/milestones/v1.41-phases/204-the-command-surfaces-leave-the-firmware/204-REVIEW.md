---
phase: 204-the-command-surfaces-leave-the-firmware
reviewed: 2026-09-22T11:09:17Z
depth: standard
files_reviewed: 31
files_reviewed_list:
  - firestarter_app/firestarter/constants.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/tests/test_eprom_operations.py
  - firestarter_fw/CLAUDE.md
  - firestarter_fw/PROTOCOLS.md
  - firestarter_fw/include/eprom_operations.h
  - firestarter_fw/include/firestarter.h
  - firestarter_fw/include/memory_utils.h
  - firestarter_fw/platformio.ini
  - firestarter_fw/src/eprom_operations.cpp
  - firestarter_fw/src/firestarter.cpp
  - firestarter_fw/src/operation_utils.cpp
  - firestarter_fw/src/proms/eeprom_28c.cpp
  - firestarter_fw/src/proms/eprom.cpp
  - firestarter_fw/src/proms/flash_5v_page.cpp
  - firestarter_fw/src/proms/flash_intel.cpp
  - firestarter_fw/src/proms/flash_nor_unlock.cpp
  - firestarter_fw/src/proms/memory.cpp
  - firestarter_fw/test/native/avr/test_cmd_admission/test_cmd_admission.cpp
  - firestarter_fw/test/native/avr/test_dispatch/test_configure_memory.cpp
  - firestarter_fw/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp
  - firestarter_fw/test/native/avr/test_val_eprom/test_val_eprom.cpp
  - firestarter_fw/test/native/avr/test_val_nor_unlock/test_val_nor_unlock.cpp
  - firestarter_fw/test/native/avr/test_verify_error_ids/host_stubs.cpp
  - firestarter_fw/test/native/avr/test_verify_error_ids/test_verify_error_ids.cpp
  - firestarter_fw/tests/golden/protocol_branch_inventory.json
  - firestarter_fw/tests/test_blank_check_region_source_contract.py
  - firestarter_fw/tests/test_boolean_convention_source_contract_v133.py
  - firestarter_fw/tests/test_protocol_branch_inventory.py
  - firestarter_fw/tests/test_verify_survival_source_contract.py
  - tools/catalog/messages.toml
findings:
  critical: 0
  warning: 0
  info: 1
  total: 1
status: clean
---

# Phase 204: Code Review Report

**Reviewed:** 2026-09-22T11:09:17Z
**Depth:** standard
**Files Reviewed:** 31
**Status:** clean

## Summary

Phase 204 retires two wire-protocol ordinals (`CMD_BLANK_CHECK`/`COMMAND_BLANK_CHECK`, ordinal 4,
and `CMD_VERIFY`/`COMMAND_VERIFY`, ordinal 6) end to end across the firmware and host repositories,
per the phase's own framing as a deliberate, operator-approved breaking change. I traced this as an
adversarial reviewer, assuming defects existed, and checked every high-value target the phase context
flagged:

- **Both retired ordinals are fully gone from live dispatch on both sides.** `firestarter.cpp`'s
  command switch, `is_memory_cmd()`'s admission predicate, and all five protocol `configure_*`
  handlers no longer reference either ordinal anywhere (verified by direct grep, not just reading the
  diff) — a stray frame carrying either ordinal now falls through to `MSG_ERR_UNKNOWN_CMD` as
  documented. The host's `constants.py` and `eprom_operations.py` mirror this exactly, and both
  reserved-ordinal comment blocks are present and consistent between `firestarter.h` and
  `constants.py`.
- **Nothing that must survive was actually removed.** `memory_verify_execute` is still defined in
  `memory.cpp` and is still called from `eprom.cpp`'s `VERIFY_PER_PULSE_PLUS_FINAL` arm (confirmed by
  reading the call site directly, not by trusting a comment). `eeprom28c_verify_page_readback` and
  `flash_util_verify_operation` are both still present and still wired into their respective write
  paths. `mem_util_blank_check` / `mem_util_blank_check_region` / `blank_check_saved_address` /
  `BLANK_CHECK_CHUNK_SIZE` all survive, reachable only from write-init (`eprom.cpp`) and erase-end,
  exactly as the phase context states.
- **The collapse of the command-keyed branches in `mem_util_blank_check_region` and
  `_single_step_operation_callback` is behaviorally equivalent for the surviving callers.** Before this
  phase, the `if (handle->cmd == CMD_BLANK_CHECK) {...} else {direct emit}` forks already took the
  `else` (direct-emit) arm for write-init and erase-end — the only two callers that survive. Removing
  the `if` and keeping only that arm changes nothing observable for those two callers; I verified this
  by diffing the pre- and post-phase bodies line by line rather than trusting the removal comment.
- **The host's `region-end` guard rewrite (`cmd == COMMAND_WRITE` replacing
  `cmd in (COMMAND_WRITE, COMMAND_VERIFY)`) is safe.** `verify_eprom` (post-202) never forwards
  `region_length` to `_operation_context` in the first place, so `COMMAND_VERIFY`'s prior membership in
  that guard was already dead by the time this phase ran; dropping it changes no behavior.
- **The `protocol_branch_inventory.json` golden re-derivation is exactly as claimed.** I parsed both
  the pre- and post-phase JSON and diffed them field-by-field with `line` excluded: 22 sites in both,
  identical `counts`, identical `params_table`, and every non-`line`/non-blob-sha field byte-identical.
  This is not a rubber stamp — I ran the comparison directly rather than trusting the phase-context
  claim.
- **The new `test_verify_error_ids` suite is non-vacuous and correctly wired.** It is registered in
  both `test_filter` and `-I` lists via the shared `[native_base]` section (confirmed it reaches both
  `[env:native]` and `[env:native_nodevtools]`), asserts message IDs in both directions (present /
  absent) for all four failure classes, and includes an explicit non-vacuity check (frame count > 0)
  before every membership assertion. `flash_util_verify_operation` is pinned to raise
  `MSG_ERR_OP_TIMEOUT` and explicitly asserted to never raise `MSG_ERR_VERIFY`, matching the phase
  context's framing exactly.
- **The new `test_verify_survival_source_contract.py` gate is genuinely load-bearing, not
  decorative.** Containment checks (Coverage 1, 7, 8) use brace-matched scanning rather than line
  proximity, has a self-check that its own concatenation-built needles don't appear verbatim in its
  own source (so a future edit can't silently defang it), and a positive counterpart (Coverage 2, 3)
  that prevents Coverage 1 from passing vacuously if the underlying table or function were deleted. I
  independently grepped all five protocol handler files for the literal strings `CMD_VERIFY` and
  `CMD_BLANK_CHECK` to confirm Coverage 9's claim rather than trusting the test.
- **`DBG_VERIFY_PROM` (0x08) and `DBG_BLANK_CHECK_PROM` (0x0B) in `messages.toml`** carry only added
  comments; the diff touches no `id`/`name`/`format`/`params` field, consistent with the "byte-identical
  generated output" claim.

I found no BLOCKER or WARNING-level defects. One INFO-level observation below is a minor
maintainability note, not a correctness issue.

## Info

### IN-01: `firestarter_fw/CLAUDE.md`'s native-suite-registration correction is unrelated to this phase's ordinal retirement

**File:** `firestarter_fw/CLAUDE.md` (native-suite-registration section, "Adding a native test suite")
**Issue:** This phase's diff to `CLAUDE.md` includes a hunk correcting a stale claim ("four new lines"
→ "two new lines, not four") about how many `platformio.ini` lines a new native suite needs, tied to
the `[native_base]` shared-section refactor. That refactor is not part of this phase's ordinal
retirement work — `[native_base]` already existed and was already the effective mechanism before this
phase started (the doc was simply describing it incorrectly). Bundling an unrelated doc fix into a
phase's diff makes the diff slightly harder to audit for "does this commit do only what it claims,"
since a reviewer has to separately establish that the correction is accurate and unrelated rather than
a side effect of the ordinal work.
**Fix:** No action required for correctness — the corrected text is accurate (verified against the
live `platformio.ini`). Consider carrying unrelated doc-staleness fixes in their own commit in future
phases so the diff for a breaking wire-protocol change stays scoped to that change.

---

_Reviewed: 2026-09-22T11:09:17Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
