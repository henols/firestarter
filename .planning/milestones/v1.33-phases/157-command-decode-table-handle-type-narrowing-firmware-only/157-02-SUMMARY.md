---
phase: 157-command-decode-table-handle-type-narrowing-firmware-only
plan: "02"
subsystem: firmware-decode
tags: [json_parser.c, PROGMEM, offsetof, _Static_assert, data-table, avr-nm, platformio]

# Dependency graph
requires:
  - phase: 157-command-decode-table-handle-type-narrowing-firmware-only
    provides: "the authoritative before-figures record (.planning/v1.33/157-before-figures.md) this plan's measurement is subtracted from"
provides:
  - "src/json_parser.c's key_parsers[] rewritten as a compiler-derived {key, clamp, offset, width} field_desc_t table plus one shared, inlined store_field"
  - "Twelve _Static_assert compile-time layout guards behind the raw memcpy, proven to fire against two planted negatives (struct reorder, extra row)"
  - "get_flags pointed at key_flags directly (OD-3), making DECODE-02 single-key-storage a source property, re-measured as one surviving key-string block on all three AVR targets"
  - "Measured table-only flash delta on uno/uno328pb/leonardo: -884 B each, RAM unchanged, with the 6 B divergence from the reference -890 B attributed to OD-1's policy column"
affects: [157-03-PLAN, 157-04-PLAN, 157-05-PLAN, 157-06-PLAN, 157-07-PLAN]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "PROGMEM data table + one shared inlined accessor, replacing a PROGMEM function-pointer table, to collapse N structurally identical dispatch stubs into one body (src/proms/eprom_params.cpp precedent, applied to json_parser.c)"
    - "offsetof/sizeof-derived table rows guarded by per-member _Static_assert, proven to fire via a throwaway detached worktree with two planted negatives"
    - "Per-row policy bit (FIELD_POLICY_MASK) encoding SATURATE-vs-MASK semantics in a table column, so a bitmask field can opt out of saturation without a second table shape"

key-files:
  created: []
  modified:
    - firestarter/src/json_parser.c

key-decisions:
  - "ctrl_flags uses FIELD_MASK (mask semantics), never FIELD (saturate semantics) -- saturating a bitmask to 0xFFFF would set FLAG_FORCE/FLAG_SKIP_ERASE/FLAG_SKIP_BLANK_CHECK simultaneously, a fail-open in a fail-closed phase (OD-1)"
  - "key_parsers identifier kept unchanged (OD-2) even though it's now a data table, not a table of parsers -- renaming would break firestarter_app's regex-based parity gate and make its sibling leg pass vacuously"
  - "get_flags hand-expanded to reference key_flags directly (OD-3) rather than depending on the toolchain to keep deduplicating the flags PROGMEM string"
  - "store_field's value parameter typed uint32_t, not unsigned long, so the saturation branch is identical on AVR (32-bit) and native (64-bit unsigned long)"
  - "Measured -884 B per AVR target, not the reference's -890 B; the 6 B difference is attributed to OD-1's per-row mask-vs-saturate policy column, which the reference table did not carry (C-19) -- not closed by editing code"

patterns-established:
  - "A throwaway `git worktree add --detach` probe, leaf-named exactly `firestarter`, is the pattern for proving a _Static_assert actually fires without touching the real tree or firestarter_app's directory-name-sensitive test"

requirements-completed: [DECODE-01, DECODE-02, DECODE-03, DECODE-06]

coverage:
  - id: D1
    description: "key_parsers[] replaced with a compiler-derived {key, clamp, offset, width} data table; ten dispatch stubs and the function-pointer column deleted; one shared store_field inlined"
    requirement: "DECODE-01"
    verification:
      - kind: other
        ref: "avr-nm --print-size --radix=d .pio/build/uno/firestarter_uno.elf | grep -cE ' (get_memory_size|get_address|get_chip_id|get_pin_count|get_delay|get_vpp_mv|get_algorithm|get_read_settling|get_read_strobe|get_page_size|store_field|get_r1|get_r2|get_rev|get_rw_pin|get_vpp_pin)$' => 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "get_flags points at key_flags directly (OD-3); one key-string block survives on all three AVR targets, re-measured as a link-time property now backed by source"
    requirement: "DECODE-02"
    verification:
      - kind: other
        ref: "offset-resolved strings -a -n 2 -t d dump on uno/uno328pb/leonardo ELFs, cross-keyed against avr-nm's key_ symbols -- exactly one flags string per target"
        status: pass
    human_judgment: false
  - id: D3
    description: "Twelve _Static_assert compile-time guards (eleven per-member offset/width checks + one row-count check) stand behind the raw memcpy and are proven to fire"
    requirement: "DECODE-03"
    verification:
      - kind: other
        ref: "throwaway git worktree at /tmp/157-probe/firestarter: planted struct reorder (mem_size after data_buffer) and planted 12th key_parsers row both make pio run -e uno FAIL with the assertion's own message text"
        status: pass
    human_judgment: false
  - id: D4
    description: "Read-timing clamp (T-44-01) folded into the table's clamp column; READ_TIMING_MAX_US hoisted above key_parsers[]"
    requirement: "DECODE-06"
    verification:
      - kind: integration
        ref: "pio test -e native -f \"*test_read_timing*\" => 9 test cases: 9 succeeded"
        status: pass
    human_judgment: false
  - id: D5
    description: "Both native environments still 172/172; both local check scripts pass; host wire-key parity gate reports 24 passed with zero firestarter_app files changed"
    verification:
      - kind: integration
        ref: "pio test -e native and pio test -e native_nodevtools => 172 test cases: 172 succeeded each; python3 scripts/check_build_warnings.py --rebuild and check_no_heap_or_64bit_symbols.py both exit 0; firestarter_app pytest tests/test_json_key_parity.py tests/test_revision_constants_parity.py => 24 passed"
        status: pass
    human_judgment: false

duration: 70min
completed: 2026-08-23
status: complete
---

# Phase 157 Plan 02: Command-Decode Field Table Summary

**Replaced `key_parsers[]`'s PROGMEM function-pointer column and its ten dispatch stubs with one compiler-derived `{key, clamp, offset, width}` data table and a single inlined `store_field`, measuring -884 B per AVR target (RAM unchanged) and proving both compile-time layout guards fire against planted negatives in a throwaway worktree.**

## Performance

- **Duration:** ~70 min
- **Tasks:** 3 (hand-port the table + guards, measure and commit, prove the guards fire)
- **Files modified:** 1 (`firestarter/src/json_parser.c`)

## Accomplishments

- Hand-ported (not `git apply`d, per C-11) a `field_desc_t {key, clamp, offset, width}` PROGMEM
  table replacing `key_parser_t`'s function-pointer column, with `FIELD`/`FIELD_MASK` macros
  deriving `offset` via `offsetof` and `width` via `sizeof(((firestarter_handle_t*)0)->member)` --
  never a literal, since the AVR and native struct layouts diverge at every member from `protocol`
  down.
- Deleted the ten dispatch stubs (`get_memory_size`, `get_address`, `get_chip_id`,
  `get_pin_count`, `get_delay`, `get_vpp_mv`, `get_algorithm`, `get_read_settling`,
  `get_read_strobe`, `get_page_size`) and their forward declarations; `get_flags` and the five
  zero-cost siblings (`get_r1`, `get_r2`, `get_rev`, `get_rw_pin`, `get_vpp_pin`) survive untouched
  in body (only `get_flags`' internals change, per OD-3).
- Added `store_field`, the single shared write body every table row now dispatches through: reads
  `offset`/`width`/`clamp` via `pgm_read_byte`/`pgm_read_word` (never a direct struct
  dereference), applies the clamp (T-44-01), then saturates to the member's own maximum unless the
  row's `FIELD_POLICY_MASK` bit selects mask semantics instead, then `memcpy`s the low `width`
  bytes into the handle at the compiler-derived `offset`.
- Added twelve `_Static_assert` compile-time guards (eleven per-member offset/width checks plus
  one row-count check) -- a new idiom for this repository in a C translation unit -- and proved
  both fire in a throwaway `git worktree add --detach` probe (leaf-named exactly `firestarter` per
  `test_scope_is_firmware_only`'s hard-coded expectation): a planted struct reorder (`mem_size`
  moved after `data_buffer`) and a planted twelfth `key_parsers[]` row both made `pio run -e uno`
  FAIL with the assertion's own message text.
- Made `ctrl_flags` use `FIELD_MASK` (mask semantics), never `FIELD` (saturate semantics):
  saturating a bitmask to its type maximum would set `FLAG_FORCE`, `FLAG_SKIP_ERASE` and
  `FLAG_SKIP_BLANK_CHECK` simultaneously -- a fail-open in the phase whose headline criterion is
  fail-closed (OD-1).
- Hand-expanded `get_flags`' body to reference `key_flags` directly (OD-3), making DECODE-02's
  single-key-storage claim a source property; re-measured the offset-resolved key-string block on
  all three AVR targets and confirmed exactly one surviving block per target, `flags` included --
  no second anonymous `PSTR` duplicate.
- Measured the table-only flash delta on all three AVR targets: `uno` 24234 -> 23350 (-884 B),
  `uno328pb` 24282 -> 23398 (-884 B), `leonardo` 26378 -> 25494 (-884 B); RAM unchanged at
  1567/1573/2008 (the narrowing is plan 03's). The reference implementation measured -890 B; this
  position's 6 B divergence is attributed to OD-1's per-row mask-vs-saturate policy column, which
  the reference table did not carry (C-19) -- not closed by editing code.
- Confirmed `pio test -e native` and `pio test -e native_nodevtools` both still report `172 test
  cases: 172 succeeded`; both local check scripts (`check_build_warnings.py --rebuild`,
  `check_no_heap_or_64bit_symbols.py`) pass; and `firestarter_app`'s host wire-key parity gate
  reports `24 passed` on the committed firmware tree, with zero `firestarter_app` files touched.

## Task Commits

1. **Task 1: Hand-port the field table, store_field, the twelve compile-time guards and the
   clamp hoist** -- folded into Task 2's commit (both tasks touch the same single file; verified
   independently before commit, per the plan's own verify blocks).
2. **Task 2: Measure the table-only delta on all three targets, run every local gate, and
   commit** -- `19df431` (`refactor(157-02): replace the key-parser dispatch table with a
   compiler-derived field table`)
3. **Task 3: Prove the compile-time guards can actually fire -- two planted negatives** -- no
   commit (all work happened in a throwaway `git worktree`, discarded before the task ended; no
   tracked file in `/workspaces/firestarter` changed).

## Files Created/Modified

- `firestarter/src/json_parser.c` -- `key_parsers[]` is now a `field_desc_t` data table; ten
  dispatch stubs deleted; `store_field` added; twelve `_Static_assert` guards added;
  `READ_TIMING_MAX_US` hoisted above the table; `get_flags` references `key_flags` directly.

## Decisions Made

- **OD-1 (carried from plan 01, applied here):** `ctrl_flags` masks rather than saturates.
- **OD-2 (carried from plan 01, applied here):** `key_parsers` identifier kept, now describing a
  data table rather than a table of parsers.
- **OD-3 (carried from plan 01, applied here):** `get_flags` hand-expanded to reference
  `key_flags` directly.
- **`store_field`'s value parameter typed `uint32_t`, not `unsigned long`:** `simple_strtoul`
  returns `unsigned long` (32-bit on AVR, 64-bit on native x86-64); taking `uint32_t` makes
  `sizeof(value)` 4 on both architectures, so the saturation branch behaves identically on both and
  the native round-trip tests (plans 04/05) are valid oracles for the AVR build. On AVR the two
  types are the same width, so this choice is byte-identical there.
- **Measured -884 B, not -890 B, and did not chase the reference figure:** the divergence is
  attributed to OD-1's per-row policy column (the `FIELD_POLICY_MASK` bit and its branch in
  `store_field`), which the reference table this -890 was measured on did not carry (C-19).

## Deviations from Plan

None -- plan executed exactly as written. Tasks 1 and 2 were executed together as a single edit
pass (both operate on the same file and the plan's own verify blocks for Task 1 were run and
confirmed passing before Task 2's commit step), which does not change what was measured, committed,
or verified.

## Issues Encountered

None. The build, both native suites, both local check scripts, and the host parity gate all passed
on the first attempt after the hand-port.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `firestarter` HEAD is now `19df431` on `gsd/v1.33-source-hygiene-firmware-size-reduction`;
  `git -C firestarter status --porcelain` is empty; no `.rej`/`.orig` file exists anywhere.
- Plan 03 (the `protocol`/`ctrl_flags` type narrowing) can proceed against this table: the eleven
  per-member `_Static_assert` guards and the `FIELD`/`FIELD_MASK` macros will automatically
  re-derive `offset`/`width` once `include/firestarter.h`'s member types narrow -- no table edit is
  needed for the narrowing itself, only for `ctrl_flags`'s width value in the guard messages if
  the member's own type changes size.
- Plans 04/05 (the native round-trip cases OD-5 takes) can dispatch through `store_field` and the
  `field_desc_t` table directly; `store_field`'s `uint32_t` value type is deliberately native/AVR
  invariant for exactly this purpose.
- Plan 06/07 should read this SUMMARY's measured -884 B figures (not the reference's -890 B) when
  composing the after-figures record and the final requirement closure.
- No blockers.

---
*Phase: 157-command-decode-table-handle-type-narrowing-firmware-only*
*Completed: 2026-08-23*

## Self-Check: PASSED

- FOUND: `firestarter/src/json_parser.c`
- FOUND: `.planning/phases/157-command-decode-table-handle-type-narrowing-firmware-only/157-02-SUMMARY.md`
- FOUND: firmware commit `19df431` (`git -C firestarter log --oneline --all`)
- FOUND: meta commit `50541fa` (`git log --oneline --all`)
