# `planted_no_heap_or_64bit_symbols_prechange_uno/`

A planted violation proving `check_no_heap_or_64bit_symbols.py`'s (Phase 155
Plan 02, DEAD-01/DEAD-03) forbidden-symbol assertion: neither the heap set
(`malloc`, `free`, `realloc`, `calloc`, `__brkval`, `__flp`,
`__malloc_heap_start`, `__malloc_heap_end`, `__malloc_margin`) nor the full
eleven-symbol 64-bit runtime set (`__muldi3`, `__muldi3_6`, `__umulsidi3`,
`__umulsidi3_helper`, `__umoddi3`, `__udivdi3`, `__udivdi3_umoddi3`,
`__udivmod64`, `__ashrdi3`, `__lshrdi3`, `__adddi3`) may appear in a linked
AVR image's symbol table, or the checker fails closed.

## What is committed

`avr-nm-uno.txt` is the **verbatim stdout** of

```bash
$HOME/.platformio/packages/toolchain-atmelavr/bin/avr-nm \
  --print-size --size-sort -C .pio/build/uno/firestarter_uno.elf
```

run against the **real, unedited pre-change** `uno` build, captured at
firmware SHA `2ad5b322a37ba4a88afd09cc946f5c4114e51483` (`FW_PRE_SHA`, per
`.planning/v1.33/155-before-figures.md` section 1) on a tree asserted clean
(`git -C firestarter status --porcelain` empty, `HEAD` equal to `FW_PRE_SHA`)
immediately before capture. The text was **not edited afterwards** -- this is
a real negative, not a hand-authored one.

## The four asserted properties

Before this file was committed, all four were checked mechanically against
its own committed content:

1. Exactly **7** lines whose symbol name is in the heap set (`malloc` 312 B,
   `free` 274 B, `__brkval` 2 B, `__flp` 2 B, `__malloc_heap_end` 2 B,
   `__malloc_heap_start` 2 B, `__malloc_margin` 2 B).
2. Exactly **11** lines whose symbol name is in the 64-bit runtime set
   (`__muldi3` 158 B, `__muldi3_6` 18 B, `__umulsidi3` 2 B,
   `__umulsidi3_helper` 84 B, `__umoddi3` 4 B, `__udivdi3` 2 B,
   `__udivdi3_umoddi3` 22 B, `__udivmod64` 162 B, `__ashrdi3` 4 B,
   `__lshrdi3` 54 B, `__adddi3` 18 B).
3. `mem_util_blank_check` is present (the DEAD-01 non-vacuity anchor).
4. `rurp_read_voltage_mv` is present (the DEAD-03 non-vacuity anchor).

`realloc` and `calloc` are genuinely absent from this listing too (confirmed
in `155-before-figures.md` section 3) -- this fixture does not fabricate
their presence; the gate still lists them in `HEAP_SYMBOLS` so a future
caller pulling either back in would trip it.

## Expected gate behaviour

`python3 scripts/check_no_heap_or_64bit_symbols.py --nm-output uno=<this dir>/avr-nm-uno.txt`:

- Exit **1** (`FAIL:`)
- stdout names all 18 offending symbols, including `malloc`, `free`,
  `__muldi3` and `__umulsidi3_helper` -- the last of these is the 84 B
  symbol DEAD-03's eight-name list omits, so its presence in the failure
  output is what proves this gate covers eleven symbols, not eight.
- stdout never contains `PASS:`

## Why committed as TEXT, not an ELF

No binary fixture exists anywhere in this repository, and CI leg 3 (which
runs this pytest module) has no AVR toolchain installed. The `--nm-output`
seam lets the checker read a captured text listing directly, keeping the
paired pytest module hermetic. Same reasoning as
`tests/fixtures/planted_release_assets_missing_uno328pb/README.md`'s own
"Why `pio_build/`, not `.pio/`" section, applied to a different toolchain
output.
