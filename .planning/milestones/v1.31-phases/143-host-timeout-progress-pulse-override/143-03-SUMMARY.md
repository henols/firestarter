---
phase: 143-host-timeout-progress-pulse-override
plan: 03
subsystem: firmware
tags: [c, cpp, platformio, arduino, eprom, serial-protocol, source-contract, cap-02, cap-03, msg-ok-ready, bf-1]

# Dependency graph
requires:
  - phase: 143-01
    provides: "eprom_block_budget_s (include/eprom_budget.h / src/proms/eprom_budget.cpp) -- the BF-3-corrected per-block write-time budget function, called from the ack pack block"
provides:
  - "BF-1 closed: CAP-02's hardware-revision/firmware-identity tail ported into the v1.31 firmware branch (was firmware-only-2-byte-ack before this plan), so a v1.31 firmware build can connect to the v1.31 app branch at all"
  - "CAP-03: the per-block write-time budget appended to MSG_OK_READY at the computed ver_end-relative offset (4 + _vlen), matching plan 143-02's host decoder byte for byte"
  - "tests/test_ack_layout_source_contract_v143.py -- a 10-leg, stdlib-only source-contract gate pinning the ack pack layout (env seam FIRESTARTER_ACK_SCAN_DISPATCH_SOURCE), with every leg seen RED on a scratch-file plant and GREEN against the real source"
affects: [143-05, 143-08, 143-10, 144, 145]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "One pack block, one commit: CAP-01/CAP-02/CAP-03 all written into the same _ready[] buffer and the same LOG_OK_ID_BYTES emit, rather than as a second independent emit -- keeps the ack's shape a single length-discriminated blob"
    - "Source-contract self-protection leg split into two halves: a seam-INDEPENDENT recomputed-default sanity check (mirrors the analog verbatim) plus a seam-AWARE non-empty-extracted-body check, so an empty-file plant meaningfully turns the leg RED without contradicting the 'never reads os.environ' self-protection discipline"

key-files:
  created:
    - firestarter/tests/test_ack_layout_source_contract_v143.py
  modified:
    - firestarter/src/firestarter.cpp
    - firestarter/tests/test_config_schema_pinned.py

key-decisions:
  - "CAP-02 ported verbatim from upstream commit 13eb350 (cited in the task 1 commit message) inside the SAME pack block as CAP-03, rather than as a separate emit -- the _ready[] buffer and the pack sequence are written once, per RESEARCH Open Question 2's recommendation"
  - "test_scan_targets_are_non_vacuous's non-vacuity check operates on the CURRENT (seam-aware) _SCAN_DISPATCH target, not a second seam-independent recompute, so an empty-scratch-file plant can turn it RED as the plan requires -- documented explicitly in the module docstring as a deliberate, reasoned departure from the strict analog (whose equivalent leg never reads its seam at all)"
  - "Fixed a pre-existing, unrelated line-number-pinned gate (test_config_schema_pinned.py's C-14 consumer census) that the task 1 #include insertion shifted by +1 -- Rule 1 auto-fix, not a deviation from this plan's own scope"

patterns-established:
  - "Pattern: a shared brace-matched body extractor asserts 'exactly one definition found' internally (mirroring _extract_command_done_body), so every leg that depends on it fails loudly -- never vacuously -- when the scan target is broken or empty"
  - "Pattern: needles forbidden from a scanned C++ body (D-07 hand-rolled-restatement guards) AND needles used for this module's own skip-safety self-check are built by concatenation and centralized in one _ALL_SELF_CHECK_NEEDLES tuple, so one final leg proves all of them absent from the gate's own source"

requirements-completed: []

coverage:
  - id: ACK-01
    description: "CAP-02 ported (BF-1 closed) and CAP-03 appended in one pack block, budget computed by calling the shipped eprom_block_budget_s, emitted unconditionally on every command"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_ack_layout_source_contract_v143.py::test_the_retired_two_byte_ready_emit_is_gone"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_ack_layout_source_contract_v143.py::test_exactly_one_byte_blob_ready_emit_exists"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_ack_layout_source_contract_v143.py::test_the_budget_comes_from_the_shipped_budget_function"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_ack_layout_source_contract_v143.py::test_the_revision_byte_is_emitted_on_every_build_configuration"
        status: pass
    human_judgment: false
  - id: ACK-02
    description: "The budget is written at a COMPUTED offset never a literal, the pack buffer has room for it, and the emitted length accounts for it -- D-08's fixed-index hazard closed"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_ack_layout_source_contract_v143.py::test_the_ready_pack_buffer_has_room_for_the_budget"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_ack_layout_source_contract_v143.py::test_the_budget_is_written_at_a_computed_offset_not_a_literal"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_ack_layout_source_contract_v143.py::test_the_emitted_length_accounts_for_the_budget"
        status: pass
    human_judgment: false
  - id: ACK-03
    description: "Self-protection: the gate cannot pass vacuously on a broken or empty scan target, cannot be silently skipped, and its own forbidden needles are concatenation-built"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_ack_layout_source_contract_v143.py::test_scan_targets_are_non_vacuous"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_ack_layout_source_contract_v143.py::test_this_module_cannot_be_silently_skipped"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_ack_layout_source_contract_v143.py::test_own_needles_do_not_appear_verbatim_in_this_module"
        status: pass
    human_judgment: false
  - id: ACK-04
    description: "Build/warning/size posture: all three AVR targets build (leonardo fits), zero AVR warnings, both pinned native envs and native_loop_v131 unmoved, whole firmware pytest suite at 282 (272 + 10), check_size_baseline.py RED for the recorded MERGE-05/OD-2 reasons only, native_trace_v131 RED and named as expected (D-24)"
    verification:
      - kind: unit
        ref: "pio run -e uno / -e uno328pb / -e leonardo"
        status: pass
      - kind: unit
        ref: "python3 scripts/check_build_warnings.py --rebuild (cold)"
        status: pass
      - kind: unit
        ref: "pio test -e native / -e native_nodevtools / -e native_loop_v131"
        status: pass
      - kind: unit
        ref: "python3 -m pytest tests/ -o addopts=\"\" -q"
        status: pass
    human_judgment: false

duration: ~48min
completed: 2026-08-13
status: complete
---

# Phase 143 Plan 03: BF-1 Closure -- CAP-02 Port + CAP-03 Write-Budget Ack, Source-Contract Pinned Summary

**The operation-setup ack now packs CAP-01, a PORTED CAP-02 identity tail and CAP-03's per-block write-time budget into one `LOG_OK_ID_BYTES(MSG_OK_READY, ...)` emit -- closing BF-1 (a v1.31 firmware build could not previously connect to the v1.31 app at all) -- and the layout is pinned by a new 10-leg, stdlib-only source-contract gate, every leg proven RED on a scratch-file plant and GREEN against the real source.**

## Performance

- **Duration:** ~48 min
- **Started:** 2026-08-12T23:50:33Z (STATE.md `last_updated` at hand-off from 143-02)
- **Completed:** 2026-08-13T00:38:31Z
- **Tasks:** 2 completed (both `type="auto"`, no checkpoints)
- **Files touched:** 3 (1 created, 2 modified; one modification was a Rule 1 auto-fix to an unrelated pre-existing gate)

## Accomplishments

- **BF-1 closed.** `src/firestarter.cpp`'s `init_programmer_framed` no longer emits the bare CAP-01-only `LOG_OK_ID_U16(MSG_OK_READY, (uint16_t)DATA_BUFFER_SIZE)`. It now packs `[buffer_size u16 BE][hw_revision u8][ver_len u8][ver bytes][write_budget_s u16 BE]` in one `_ready[]` buffer and one `LOG_OK_ID_BYTES` emit. CAP-02 (the hardware-revision/firmware-identity tail) is **ported**, not invented -- verbatim from upstream commit `13eb350` (`origin/beta` PR #49), cited in the task 1 commit message. Before this plan, every command from the v1.31 app against a v1.31 firmware build failed at connect (`_probe_port` raising `FirmwareOutdatedError`); that is not a regression this plan introduced, it is a pre-existing bench-blocking condition this plan removes.
- **CAP-03 wired to plan 143-01's shipped function.** The budget is computed by calling `eprom_block_budget_s(handle->protocol, handle->pulse_delay, (uint32_t)DATA_BUFFER_SIZE)` -- no datasheet-derived value is restated at the ack site. Verified this session, before writing any code, that the ordering chain has **no** spurious-timeout path: `parse_json` (defined at `src/firestarter.cpp:50`) calls `configure_memory` (via `op_execute_function` at line 93, inside the `is_memory_cmd` guard at line 87) for every memory command; `init_programmer_framed` (line 116) calls `parse_json` at line 131 and packs the ack afterwards, at line 208 -- so `configure_eprom`'s `pulse_delay == 0` fallback switch (`src/proms/eprom.cpp:68-75`, unmodified this plan) has already run by the time the budget is computed. The non-memory-command residual (pulse_delay stays 0, `eprom_block_budget_s` then returns 0 for that case only if the protocol also has no EPROM row) is stated, not fixed, per the plan's own instruction.
- **The budget is written at a computed offset, never a literal**, and the pack buffer (`_ready[4 + 32 + 2]`) has room for it -- closing D-08's named hazard (a fixed index works for one identity length and silently misreads the next).
- **A new 10-leg, stdlib-only source-contract gate** (`tests/test_ack_layout_source_contract_v143.py`, env seam `FIRESTARTER_ACK_SCAN_DISPATCH_SOURCE`) pins the pack layout: the retired emit is gone, exactly one byte-blob emit exists, the buffer is sized correctly, the budget offset is computed (with a negative check that no `_ready[` index anywhere in the body is a bare literal above 3), the emitted length accounts for the budget, the budget comes from the shipped function (with three concatenation-built forbidden-restatement needles), and the revision byte is emitted on both build configurations. Three self-protection legs (non-vacuous scan targets, cannot be silently skipped, own needles never appear verbatim) close it out.
- **D-25 fully discharged**: all 7 layout legs plus the empty-file plant were seen RED on a scratch-file mutation (never the real `src/firestarter.cpp`, confirmed byte-identical throughout via `git diff --exit-code`) and GREEN against the real, unseamed source. Transcripts below.
- **Rule 1 auto-fix, caught by this plan's own required whole-suite run:** task 1's one-line `#include "eprom_budget.h"` shifted three of `tests/test_config_schema_pinned.py`'s hand-pinned C-14 consumer-census line numbers (`src/firestarter.cpp:40,99,105` -> `41,104,110`) by +1. Fixed in a dedicated commit; see Deviations below.
- Whole-repo `python3 -m pytest tests/ -o addopts="" -q` reports **282 passed** (272 baseline + this plan's 10 new tests), committed first per L-1. All three AVR targets build (`leonardo` fits with 1874 B headroom remaining), zero AVR warnings, both pinned native envs and `native_loop_v131` unmoved. `check_size_baseline.py` reproduces the recorded, operator-accepted flash-growth RED and no other. `native_trace_v131` recorded RED and named as expected (D-24), not re-frozen.

## Task Commits

Each task was committed atomically, inside `/workspaces/firestarter` on branch `gsd/v1.31-27c-programming-algorithm-fidelity`:

1. **Task 1: Replace the 2-byte ack with one pack block carrying CAP-01, the ported CAP-02 tail and CAP-03's budget** - `67127e2` (feat)
2. **Task 2: Author `tests/test_ack_layout_source_contract_v143.py` and see every leg RED on a planted violation** - `d9154b0` (test)
   - **Rule 1 auto-fix, caught while running this task's own required whole-suite verification** - `a5a39d9` (fix) -- see Deviations below

**Plan metadata:** committed in the meta repo (`/workspaces`), see below.

## Files Created/Modified

- `firestarter/src/firestarter.cpp` - `init_programmer_framed`'s ack site: one `#include "eprom_budget.h"` line added to the include block; the single `LOG_OK_ID_U16(MSG_OK_READY, ...)` line replaced with a comment block (naming BF-1, the wire layout, the no-codegen fact, the every-command fact, the returns-0 contract, the firmware-owns-the-padding note) and a brace-scoped pack block. 53 insertions, 1 deletion. `command_done`, the dispatch switch, `op_reset_timeout()`'s position and every `LOG_INFO_ID_*` line are byte-unchanged (confirmed by `git diff`).
- `firestarter/tests/test_ack_layout_source_contract_v143.py` (new, 568 lines) - the source-contract gate described above.
- `firestarter/tests/test_config_schema_pinned.py` - `_C14_CONSUMER_SITES`'s three `src/firestarter.cpp` line numbers re-pinned (40/103/109 -> 41/104/110) plus the matching docstring citation; the other six sites (different files, untouched by this plan) are unaffected.

## Decisions Made

- **CAP-02 ported inside the same pack block as CAP-03**, not as a second independent emit -- the `_ready[]` buffer and the pack sequence are written once, per RESEARCH Open Question 2's own recommendation. Cited `13eb350` in the commit message rather than cherry-picking and amending, per the plan's explicit instruction.
- **`test_scan_targets_are_non_vacuous` reads the current (seam-aware) `_SCAN_DISPATCH` for its non-empty-body half**, not a second seam-independent recompute. This is a deliberate, reasoned departure from the strict analog (`test_hv_routing_source_contract_v142.py`'s equivalent leg never reads its seam at all) -- without it, the plan's own instruction to "plant an empty scratch file and confirm `test_scan_targets_are_non_vacuous` goes RED" would be unimplementable, since a leg that never reads the seam cannot be affected by anything pointed at through it. The leg's *other* half (the default-target sanity check) still recomputes fresh from `_REPO_ROOT` without reading `os.environ`, preserving the self-protection discipline for that half. Documented explicitly in the module's own docstring so a future reader does not mistake this for an oversight.
- **The three D-07 forbidden-restatement needles and the three skip-safety needles were unified into one `_ALL_SELF_CHECK_NEEDLES` tuple**, checked by a single `test_own_needles_do_not_appear_verbatim_in_this_module` leg, per the plan's acceptance criterion naming all seven explicitly (a slightly broader scope than the strict analog, which keeps its skip needles local to the skip-check test only).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Re-pinned `test_config_schema_pinned.py`'s C-14 consumer-census line numbers**
- **Found during:** Task 2's own required verification step (`python3 -m pytest tests/ -o addopts="" -q`, run after committing both tasks per L-1)
- **Issue:** `tests/test_config_schema_pinned.py::test_the_seven_consumers_call_only_the_public_api` went RED: `_C14_CONSUMER_SITES` hand-pins nine exact `(file, line, function)` triples proving each site still calls one of the four public config functions. Task 1's `#include "eprom_budget.h"` line, added above all three of that file's `src/firestarter.cpp` sites, shifted every line after it by +1 -- `rurp_load_config()` moved from line 40 to 41, `rurp_get_config()` from 103 to 104, `rurp_save_config()` from 109 to 110 -- so the pinned tuple's stale line numbers pointed at the wrong text (`rurp_load_config()` at old line 40 now reads a blank line; the two `CMD_CONFIG` sites shifted into adjacent `else if`/`if` lines).
- **Fix:** Re-verified the three call sites' actual current line numbers by direct inspection (`sed -n`) and updated `_C14_CONSUMER_SITES`'s three literals plus the matching docstring citation. This tuple is a hand-pinned census, not a re-derivable golden (no update script exists for it), so the fix is a direct edit, not a regeneration. The other six sites, in four different files this plan never touches, were confirmed unaffected by inspection (no line count in those files changed).
- **Files modified:** `firestarter/tests/test_config_schema_pinned.py`
- **Verification:** `python3 -m pytest tests/test_config_schema_pinned.py -o addopts="" -q` reports 17 passed; whole-suite `python3 -m pytest tests/ -o addopts="" -q` reports **282 passed**.
- **Committed in:** `a5a39d9`

---

**Total deviations:** 1 auto-fixed (1 bug, Rule 1)
**Impact on plan:** Necessary to reach a clean whole-repo pytest run, which both this plan's own acceptance criteria and L-1's "commit before running the full suite" discipline require. No scope creep: the fix is three integer literals plus a docstring citation in a file this plan does not otherwise touch, and does not affect any pinned golden, `size_baseline.json`, or `platformio.ini`.

## D-25 Evidence: RED-on-plant for all 8 plants, then GREEN, for `tests/test_ack_layout_source_contract_v143.py`

Per the plan's obligation, each plant was applied to a **scratch copy** of `src/firestarter.cpp` under this session's scratchpad directory (never the real, committed file), with `FIRESTARTER_ACK_SCAN_DISPATCH_SOURCE` pointed at the mutated copy. `src/firestarter.cpp` was confirmed byte-identical to its committed state via `git diff --exit-code` throughout (`git status --short` at the end of this task shows only the new test file). Full `-v` runs are shown for the first two plants; later plants show the same pass/fail table (identical shape) followed by the specific assertion detail.

### Plant 1 -- restore the retired 2-byte emit alongside the new block

Targets leg 1 (`test_the_retired_two_byte_ready_emit_is_gone`).

```
tests/test_ack_layout_source_contract_v143.py::test_the_retired_two_byte_ready_emit_is_gone FAILED
tests/test_ack_layout_source_contract_v143.py::test_exactly_one_byte_blob_ready_emit_exists PASSED
tests/test_ack_layout_source_contract_v143.py::test_the_ready_pack_buffer_has_room_for_the_budget PASSED
tests/test_ack_layout_source_contract_v143.py::test_the_budget_is_written_at_a_computed_offset_not_a_literal PASSED
tests/test_ack_layout_source_contract_v143.py::test_the_emitted_length_accounts_for_the_budget PASSED
tests/test_ack_layout_source_contract_v143.py::test_the_budget_comes_from_the_shipped_budget_function PASSED
tests/test_ack_layout_source_contract_v143.py::test_the_revision_byte_is_emitted_on_every_build_configuration PASSED
tests/test_ack_layout_source_contract_v143.py::test_scan_targets_are_non_vacuous PASSED
tests/test_ack_layout_source_contract_v143.py::test_this_module_cannot_be_silently_skipped PASSED
tests/test_ack_layout_source_contract_v143.py::test_own_needles_do_not_appear_verbatim_in_this_module PASSED

E       assert [<re.Match object; span=(4882, 4908), match='LOG_OK_ID_U16(MSG_OK_READY'>] == []
E         Left contains one more item: <re.Match object; span=(4882, 4908), match='LOG_OK_ID_U16(MSG_OK_READY'>

1 failed, 9 passed in 0.08s
```

**Finding:** exactly the targeted leg went RED; all 9 others stayed GREEN.

### Plant 2 -- duplicate the byte-blob `LOG_OK_ID_BYTES` call

Targets leg 2 (`test_exactly_one_byte_blob_ready_emit_exists`).

```
tests/test_ack_layout_source_contract_v143.py::test_the_retired_two_byte_ready_emit_is_gone PASSED
tests/test_ack_layout_source_contract_v143.py::test_exactly_one_byte_blob_ready_emit_exists FAILED
tests/test_ack_layout_source_contract_v143.py::test_the_ready_pack_buffer_has_room_for_the_budget PASSED
tests/test_ack_layout_source_contract_v143.py::test_the_budget_is_written_at_a_computed_offset_not_a_literal PASSED
tests/test_ack_layout_source_contract_v143.py::test_the_emitted_length_accounts_for_the_budget FAILED
tests/test_ack_layout_source_contract_v143.py::test_the_budget_comes_from_the_shipped_budget_function PASSED
tests/test_ack_layout_source_contract_v143.py::test_the_revision_byte_is_emitted_on_every_build_configuration PASSED
tests/test_ack_layout_source_contract_v143.py::test_scan_targets_are_non_vacuous PASSED
tests/test_ack_layout_source_contract_v143.py::test_this_module_cannot_be_silently_skipped PASSED
tests/test_ack_layout_source_contract_v143.py::test_own_needles_do_not_appear_verbatim_in_this_module PASSED

assert 2 == 1
 +  where 2 = len([<re.Match object; span=(4807, 4835), match='LOG_OK_ID_BYTES(MSG_OK_READY'>, <re.Match object; span=(4880, 4908), match='LOG_OK_ID_BYTES(MSG_OK_READY'>])

2 failed, 8 passed in 0.15s
```

**Finding (honest, not glossed): this plant also turned leg 5 RED**, not only the targeted leg 2. Root cause: duplicating the whole `LOG_OK_ID_BYTES(MSG_OK_READY, _ready, (uint8_t)(4 + _vlen + 2));` statement duplicates BOTH the "byte-blob emit exists" shape leg 2 pins AND the "(4 + _vlen + 2) emitted length" shape leg 5 pins, since they are regex matches against the same statement. The targeted leg went RED as required; the spillover onto leg 5 is a stronger, not weaker, result -- it proves a duplicated emit is caught from two independent angles.

### Plant 3 -- shrink `_ready` to `4 + 32` (drop the budget's 2 bytes of room)

Targets leg 3 (`test_the_ready_pack_buffer_has_room_for_the_budget`).

```
FAILED tests/test_ack_layout_source_contract_v143.py::test_the_ready_pack_buffer_has_room_for_the_budget
1 failed, 9 passed in 0.08s

AssertionError: expected exactly 1 '_ready[4 + 32 + 2]'-shaped buffer declaration inside init_programmer_framed's body, found 0 -- a buffer sized for the identity tail alone would overflow by two bytes on a 32-character identity once CAP-03's two budget bytes are written.
assert 0 == 1
 +  where 0 = len([])
```

**Finding:** only the targeted leg went RED; all other 9 stayed GREEN (confirmed via the full `-v` run, table omitted here for brevity -- identical shape to Plant 1's).

### Plant 4 -- replace the budget high byte's computed offset with the literal `36`

Targets leg 4 (`test_the_budget_is_written_at_a_computed_offset_not_a_literal`).

```
FAILED tests/test_ack_layout_source_contract_v143.py::test_the_budget_is_written_at_a_computed_offset_not_a_literal
1 failed, 9 passed in 0.08s

E       _ready[36]     = (uint8_t)((_budget >> 8) & 0xFF);
E       _ready[4 + _vlen + 1] = (uint8_t)(_budget & 0xFF);
...
assert 0 == 1
 +  where 0 = len([])
```

The leg's first assertion (`_ready[4 + _vlen]` must exist exactly once) is what fails and stops the test. Independently confirmed by hand (calling the module's own regexes against this plant outside pytest) that the leg's SECOND assertion -- no bare `_ready[` index above 3 -- would also have caught this plant on its own: `bare_over_3 == [36]`. Defense in depth verified, not merely assumed.

### Plant 5 -- omit the budget's 2 bytes from the emitted length (`4 + _vlen + 2` -> `4 + _vlen`)

Targets leg 5 (`test_the_emitted_length_accounts_for_the_budget`).

```
FAILED tests/test_ack_layout_source_contract_v143.py::test_the_emitted_length_accounts_for_the_budget
1 failed, 9 passed in 0.08s

E       LOG_OK_ID_BYTES(MSG_OK_READY, _ready, (uint8_t)(4 + _vlen));
...
assert 0 == 1
 +  where 0 = len([])
```

**Finding:** only the targeted leg went RED.

### Plant 6 -- replace the shipped-function call with an inline `pgm_read_byte`-based restatement

Targets leg 6 (`test_the_budget_comes_from_the_shipped_budget_function`).

```
FAILED tests/test_ack_layout_source_contract_v143.py::test_the_budget_comes_from_the_shipped_budget_function
1 failed, 9 passed in 0.13s

E       uint16_t _budget = (uint16_t)(pgm_read_byte(&max_pulses_col) *
E                                      pgm_read_byte(&energy_cap_us_col));
...
assert 0 >= 1
 +  where 0 = len([])
```

The leg's first assertion (at least one call to the shipped function) is what fails and stops the test. Independently confirmed by hand that all three forbidden-restatement needle regexes ALSO match this plant's inline restatement (the plant deliberately spells `max_pulses`/`energy_cap_us`/`pgm_read_`-shaped tokens): `max_pulses`-restatement 1 hit, `energy_cap_us`-restatement 1 hit, `pgm_read_`-restatement 2 hits. Defense in depth verified.

### Plant 7 -- delete the `#else` arm (hardware-revision byte no longer emitted on every build)

Targets leg 7 (`test_the_revision_byte_is_emitted_on_every_build_configuration`).

```
FAILED tests/test_ack_layout_source_contract_v143.py::test_the_revision_byte_is_emitted_on_every_build_configuration
1 failed, 9 passed in 0.10s

assert 0 >= 1
 +  where 0 = len([])
```

**Finding:** only the targeted leg went RED.

### Plant 8 -- an empty scratch file (proves `test_scan_targets_are_non_vacuous` is not the only leg protected, but IS among those protected)

Targets the non-vacuity self-protection leg specifically, per the plan's explicit instruction.

```
tests/test_ack_layout_source_contract_v143.py::test_the_retired_two_byte_ready_emit_is_gone FAILED
tests/test_ack_layout_source_contract_v143.py::test_exactly_one_byte_blob_ready_emit_exists FAILED
tests/test_ack_layout_source_contract_v143.py::test_the_ready_pack_buffer_has_room_for_the_budget FAILED
tests/test_ack_layout_source_contract_v143.py::test_the_budget_is_written_at_a_computed_offset_not_a_literal FAILED
tests/test_ack_layout_source_contract_v143.py::test_the_emitted_length_accounts_for_the_budget FAILED
tests/test_ack_layout_source_contract_v143.py::test_the_budget_comes_from_the_shipped_budget_function FAILED
tests/test_ack_layout_source_contract_v143.py::test_the_revision_byte_is_emitted_on_every_build_configuration FAILED
tests/test_ack_layout_source_contract_v143.py::test_scan_targets_are_non_vacuous FAILED
tests/test_ack_layout_source_contract_v143.py::test_this_module_cannot_be_silently_skipped PASSED
tests/test_ack_layout_source_contract_v143.py::test_own_needles_do_not_appear_verbatim_in_this_module PASSED

8 failed, 2 passed in 0.13s

AssertionError: expected exactly 1 definition of bool init_programmer_framed(firestarter_handle_t* handle) in the comment-stripped src/firestarter.cpp, found 0 -- the ack pack layout can only be pinned if there is exactly one function body to pin.
Got (comment-stripped src/firestarter.cpp):

assert 0 == 1
 +  where 0 = len([])
```

**Finding, stated honestly (a stronger result than the minimum asked for):** the plan's instruction was to confirm `test_scan_targets_are_non_vacuous` specifically goes RED under this plant; it does. **In addition**, all 7 layout legs also go RED, because they share the same `_extract_ack_pack_body` helper, and that helper's own internal "exactly 1 definition" assertion fires loudly on empty text rather than silently returning an empty body. This is the strongest possible proof of the property this leg exists to guard: a brace-matcher bug that made the extraction silently vacuous is structurally impossible here, because the shared extractor never returns without either a real body or an `AssertionError`. Only the two legs that never call the extractor at all (`test_this_module_cannot_be_silently_skipped`, `test_own_needles_do_not_appear_verbatim_in_this_module`) stayed GREEN, exactly as their own designs -- reading only this module's own source -- predict.

### Final GREEN (all plants were scratch-only; `git diff --exit-code -- src/firestarter.cpp` is clean throughout)

```
tests/test_ack_layout_source_contract_v143.py::test_the_retired_two_byte_ready_emit_is_gone PASSED
tests/test_ack_layout_source_contract_v143.py::test_exactly_one_byte_blob_ready_emit_exists PASSED
tests/test_ack_layout_source_contract_v143.py::test_the_ready_pack_buffer_has_room_for_the_budget PASSED
tests/test_ack_layout_source_contract_v143.py::test_the_budget_is_written_at_a_computed_offset_not_a_literal PASSED
tests/test_ack_layout_source_contract_v143.py::test_the_emitted_length_accounts_for_the_budget PASSED
tests/test_ack_layout_source_contract_v143.py::test_the_budget_comes_from_the_shipped_budget_function PASSED
tests/test_ack_layout_source_contract_v143.py::test_the_revision_byte_is_emitted_on_every_build_configuration PASSED
tests/test_ack_layout_source_contract_v143.py::test_scan_targets_are_non_vacuous PASSED
tests/test_ack_layout_source_contract_v143.py::test_this_module_cannot_be_silently_skipped PASSED
tests/test_ack_layout_source_contract_v143.py::test_own_needles_do_not_appear_verbatim_in_this_module PASSED

10 passed in 0.10s
```

Every leg (7 layout + 3 self-protection) was seen RED under its own plant (with two honest, stronger-than-required spillovers noted above) and GREEN against the real, unmodified source. `git status --short` in `/workspaces/firestarter`, checked immediately after committing task 2, showed only the new test file.

## Verification Results (final state)

| Check | Result |
|---|---|
| `python3 -m pytest tests/test_ack_layout_source_contract_v143.py -v -o addopts=""` | 10 passed (7 layout + 3 self-protection) |
| `python3 -m pytest tests/ -o addopts="" -q` | **282 passed** (272 baseline + 10 new) |
| `pytest tests/test_hv_routing_source_contract_v142.py tests/test_write_path_source_contract_v131.py tests/test_protocol_branch_inventory.py tests/test_golden_trace_identity.py tests/test_golden_trace_identity_eprom_v131.py tests/test_config_schema_pinned.py tests/test_check_cmake_manifest.py tests/test_flash_path_record_sync.py -o addopts=""` | 113 passed -- all named "must stay green" modules confirmed unbroken |
| `pio run -e uno` | SUCCESS; RAM 76.8% (1573/2048 B, unchanged from 143-01); Flash 77.0% (24824/32256 B, +256 B vs. 143-01's 24568) |
| `pio run -e uno328pb` | SUCCESS; RAM 77.1% (1579/2048 B, unchanged); Flash 76.8% (24874/32384 B, +256 B vs. 143-01's 24618) |
| `pio run -e leonardo` | SUCCESS; RAM 78.7% (2014/2560 B, unchanged); Flash 93.5% (26798/28672 B, +256 B vs. 143-01's 26542) -- **1874 B headroom remaining**, D-22 |
| `python3 scripts/check_build_warnings.py --rebuild` (COLD) | `PASS`: uno/uno328pb/leonardo macro_redefinition=0; native/native_nodevtools total warnings=1166 (== watermark 1166) -- unmoved |
| `python3 scripts/check_cmake_manifest.py` | `PASS`: 28 enforced sources resolved -- unmoved (no new firmware TU this plan) |
| `pio test -e native` | 141 test cases: 141 succeeded, 17 suites -- unmoved |
| `pio test -e native_nodevtools` | 141 test cases: 141 succeeded, 17 suites -- unmoved |
| `pio test -e native_loop_v131` | 77 test cases: 77 succeeded (45 + 32) -- unmoved, includes 143-01's six budget cases |
| `python3 scripts/check_size_baseline.py --rebuild` | `FAIL` (expected, D-22/OD-2): `uno: flash_used baseline=23954 observed=24824`; `uno328pb: flash_used baseline=24004 observed=24874`; `leonardo: flash_used baseline=26016 observed=26798` -- **flash_used only**, on all three AVR targets; no RAM mismatch, no native mismatch. This is the recorded, already-operator-accepted MERGE-05 / OD-2 drift (cumulative across Phases 140-143 against the Phase-124-frozen baseline), reproduced here, not newly created. `size_baseline.json` untouched (`git diff --exit-code` clean). |
| `pio test -e native_trace_v131` | `ERRORED` (expected, D-24): `0x07` expected 198 was 91; `0x08` expected 221 was 115; `0x0B` expected 201 was 59. Recorded, not re-frozen; Phase 144/TEST-06 owns the freeze. |
| `git diff --exit-code -- scripts/baseline/size_baseline.json platformio.ini include/messages.h src/proms/` | clean |
| `git status --short` in `/workspaces/firestarter_app` | unchanged from session start (pre-existing untracked files only) -- confirms "write nothing, commit nothing" in the read-only-named submodule |

## Issues Encountered

- **A pre-existing, unrelated gate (`test_config_schema_pinned.py`) broke as a side effect of a routine `#include` insertion.** See Deviations above. This is now a standing hazard worth naming for future plans touching `src/firestarter.cpp`'s top-of-file include block: any line inserted or removed above line 110 will shift `_C14_CONSUMER_SITES`'s three `src/firestarter.cpp` entries again. Not fixed structurally in this plan (that would mean building a re-derivation script for a census this plan was not asked to touch); named as a residual risk for the next editor of that region.
- **Plants 2, 4, 6 and 8 produced honest spillover beyond their single targeted leg** (documented in each plant's own "Finding" above). In every case the spillover is a STRONGER demonstration of the guarded property, not a weaker one, and no leg failed to go RED under its own plant.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- BF-1 is closed: a v1.31 firmware build now advertises the identity tail the v1.31 app's `_probe_port` requires, and plan 143-02's host decoder reads this exact byte layout (both sides independently pinned; the standing cross-repo comparison gate remains Phase 144/TEST-07's, per RESEARCH Open Question 4 -- not claimed here).
- The firmware half of HOST-01 (CAP-03 on the wire) is complete and proven, joining plan 143-01's arithmetic and plan 143-02's host decode. This plan intentionally marks no requirement Complete (frontmatter `requirements: []`); plan 143-10 flips the `HOST-*` checkboxes once every plan's evidence exists.
- **Flash headroom consumed:** this plan spent 256 B of F-142-08's 2130 B hand-off on all three AVR targets (uno/uno328pb/leonardo all +256 B identically). `leonardo` has **1874 B** of headroom remaining for the phase's two other firmware plans (143-05's progress emission, 143-08's Leonardo-only gate) -- worth tracking, not yet a concern.
- `check_size_baseline.py`'s flash-growth RED and `native_trace_v131`'s RED both remain exactly as recorded and operator-accepted; neither is this plan's or this phase's to fix (Phase 144/TEST-06, TEST-08).
- No blockers. All pinned artifacts this plan must not touch (`scripts/baseline/size_baseline.json`, `platformio.ini`, `include/messages.h`, `src/proms/*`, everything under `/workspaces/tools/catalog/`) are confirmed untouched by `git diff --exit-code`.

## Self-Check: PASSED

- FOUND: `firestarter/src/firestarter.cpp` (modified)
- FOUND: `firestarter/tests/test_ack_layout_source_contract_v143.py` (created)
- FOUND: `firestarter/tests/test_config_schema_pinned.py` (modified)
- FOUND commit `67127e2` (Task 1)
- FOUND commit `d9154b0` (Task 2)
- FOUND commit `a5a39d9` (Rule 1 deviation)

---
*Phase: 143-host-timeout-progress-pulse-override*
*Completed: 2026-08-13*
