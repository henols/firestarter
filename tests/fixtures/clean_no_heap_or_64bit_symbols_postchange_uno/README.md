# `clean_no_heap_or_64bit_symbols_postchange_uno/`

The **real post-change clean control** for
`check_no_heap_or_64bit_symbols.py` (Phase 155 Plan 06, DEAD-01/DEAD-03). It
replaces the SYNTHETIC clean control
`test_check_no_heap_or_64bit_symbols.py::test_derived_clean_listing_exits_zero_and_names_the_target`
derived at test time -- this one is a real, unedited `avr-nm` capture of the
real post-change `uno` build.

## What is committed

`avr-nm-uno.txt` is the **verbatim stdout** of

```bash
$HOME/.platformio/packages/toolchain-atmelavr/bin/avr-nm \
  --print-size --size-sort -C .pio/build/uno/firestarter_uno.elf
```

run against the real, post-change `uno` build, captured at firmware SHA
`98e70af1a89ea69ba9d5a925fa7073fb0bfc61a6` (`FW_POST_SHA` -- HEAD of
`gsd/v1.33-source-hygiene-firmware-size-reduction`, plans 04 and 05 both
landed) on a tree asserted clean (`git status --porcelain` empty)
immediately before capture. The text was **not edited afterwards**.

## The three asserted properties

Before this file was committed, all three were checked mechanically against
its own committed content:

1. **Zero** lines whose symbol name is in the heap set (`malloc`, `free`,
   `realloc`, `calloc`, `__brkval`, `__flp`, `__malloc_heap_start`,
   `__malloc_heap_end`, `__malloc_margin`).
2. **Zero** lines whose symbol name is in the full eleven-symbol 64-bit
   runtime set (`__muldi3`, `__muldi3_6`, `__umulsidi3`,
   `__umulsidi3_helper`, `__umoddi3`, `__udivdi3`, `__udivdi3_umoddi3`,
   `__udivmod64`, `__ashrdi3`, `__lshrdi3`, `__adddi3`).
3. Both non-vacuity anchors present: `mem_util_blank_check` and
   `rurp_read_voltage_mv`.

## Expected gate behaviour

`python3 scripts/check_no_heap_or_64bit_symbols.py --nm-output uno=<this dir>/avr-nm-uno.txt`:

- Exit **0** (`PASS:`)
- stdout names the target (`uno`) and both counts as zero, both anchors
  found.
- stdout never contains `FAIL:`

## Why committed as TEXT, not an ELF

Same reasoning as the sibling planted fixture's own "Why committed as TEXT,
not an ELF" section: no binary fixture exists anywhere in this repository,
`.gitignore` line 1 (`.pio`) would silently swallow a real build-tree path
at any depth, and CI leg 3 (which runs the paired pytest module) has no AVR
toolchain installed. The `--nm-output` seam lets the checker read this
captured text listing directly, keeping the pytest module hermetic.

## Relationship to the sibling planted fixture

`tests/fixtures/planted_no_heap_or_64bit_symbols_prechange_uno/avr-nm-uno.txt`
is the real PRE-change listing (7 heap-set matches, 11 sixty-four-bit-set
matches, both anchors) -- proof the gate is RED on the shipped pre-change
tree. This directory is the real POST-change listing (zero, zero, both
anchors) -- proof the gate is GREEN on the shipped post-change tree,
replacing the synthetic derived control the paired pytest used before this
plan landed. Together with the throwaway-worktree planted negative recorded
in `155-06-SUMMARY.md` (one allocation call reinstated against
`FW_POST_SHA`, proving the gate still fires on an otherwise-shipped tree),
the gate's non-hollowness is now proven from both directions: a real
negative pre-change, a real positive post-change, and a planted negative
post-change.
