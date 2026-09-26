---
title: dev test --destructive is type-agnostic — but the UV write-region branch misses 89% of UV-EPROMs
date: 2026-07-28
context: Captured during /gsd-explore 2026-07-28. Answers "is --destructive EPROM-only?" (no) and records a live defect candidate found while answering it. Companion to dev-test-design-decisions.md and dev-test-unknown-chip-fail-fast.md.
---

# `dev test --destructive` — what is and is not type-conditioned

Written because the question "is `--destructive` only affecting EPROMs and ignored by the
other types?" is a reasonable thing to suspect from reading the report output, and the
answer needs to be on record so nobody "fixes" the gate. It also documents a real gap the
question surfaced one layer down.

## The flag itself: fully type-agnostic

`firestarter_app/firestarter/chip_test.py:382` and `:393` gate the write and verify steps
on the `destructive` kwarg **alone** — no `electrical-type`, no `protocol` term in the
condition. Every chip type gets the same structural omission from `Plan.steps` (D-01 /
SAFE-01), recorded on the advisory `locked_destructive` list instead.

**There is no per-type bypass and no per-type exemption.** Do not add one.

## Two asymmetries that DO exist — inside what destructive *does*

These are what make a non-EPROM run *look* like the flag was ignored.

### 1. Erase composition (`chip_test.py:404`)

An erase step is only added when `FLAG_CAN_ERASE` is set **and** protocol != 0x05
(flash4 auto-erases per page). Consequences:

| type | `--destructive` executes | recoverable by the tool? |
|---|---|---|
| UV-EPROM | write + verify (never erase — flag never set) | **no** — UV eraser required |
| EEPROM / Flash with the flag | write + verify + erase | yes |
| flash4 (0x05) | write + verify (erase NA by design) | per-page auto-erase |
| SRAM / FRAM | write + verify (erase NA) | trivially — volatile / byte-rewritable |

So one flag, one confirm prompt — `"--destructive will sacrifice the chip. Continue?"`
(`cli_handlers.py:1838`) — spans three genuinely different risk profiles: irreversible
(UV), reversible (EEPROM/Flash), and essentially free (SRAM/FRAM). The wording is
literally true only for the UV row. Not changed; recorded as a known
over/under-warning.

### 2. Write region (`chip_test.py:640`, `_write_region_for`)

UV-EPROM gets a top-anchored `[mem_size - 256, mem_size)` window so
`generate_pattern`'s address-XOR-fold exercises the **upper-address decode** — the
Phase-44 Bug-A fault surface (PATT-03). Every other type gets `[0, 256)`.
Width always comes from the `_UV_WRITE_REGION_LENGTH` module constant, never a DB
field (SC4).

## Defect candidate: the UV signal matches ~11% of UV-EPROMs

`_write_region_for` detects UV at **execution** time via `algorithm == 0x0B`
(`_PROTOCOL_UV_EPROM`), because `_dispatch_multi_run` sees `resolve_chip`'s
**programmer** dict, which `convert_to_programmer` has already stripped of
`electrical-type`. Tally of the shipped `chip_database.json`:

| electrical type | algorithm | entries |
|---|---|---|
| UV-EPROM | **0x0B** | **32** |
| UV-EPROM | 0x07 | 163 |
| UV-EPROM | 0x08 | 106 |

**32 of 301 UV-EPROM entries — 10.6%.** The remaining ~269 fall through to the default
`[0, 256)` window on a live bench run.

The docstring's justification ("0x0B ... is UV-EPROM-exclusive across the whole chip
database — verified: no non-UV chip uses protocol-id 0x0B") is **true but is the
converse of what the branch needs**: it establishes `0x0B ⟹ UV`, not `UV ⟹ 0x0B`.
Exclusivity makes the branch safe (no non-UV part is misrouted into the UV window); it
does not make it *complete*.

Why the test suite is green: the `electrical-type == "UV-EPROM"` arm only ever fires on
the `full`-DB-dict path, which is exactly the bench-free unit-test path. The live path
takes the `algorithm` arm and misses.

### What is and is not lost

- **Not lost — retry safety.** `_UV_WRITE_REGION_LENGTH == _WRITE_REGION_LENGTH == 256`,
  so both branches write the same 256 bytes. An eraser-less tester is equally able to
  retry either way.
- **Lost — upper-address-decode coverage.** For ~269 UV parts the pattern lands at
  `0x0000`, so all-high-bits address folding never happens and the exact surface PATT-03
  was built to probe is silently unexercised.

### If this gets fixed

The fix needs a UV signal that survives `convert_to_programmer` — either carry
`electrical-type` (or a derived `is_uv` bit) through into the programmer dict, or widen
the execution-time predicate to the UV-carrying algorithms. Note that 0x07 and 0x08 are
**not** UV-exclusive: 0x07 also carries 7 electrically-erasable EEPROMs
(W27C512, SST27SF512/VF512, W27C257, W27E257, SST27SF256/VF256 — see the WARNING-5
discussion in `firestarter_app/CLAUDE.md`) and 0x08 carries 21 EEPROMs. So a naive
`algorithm in {0x07, 0x08, 0x0B}` widening would pull non-UV parts into the UV window
and forfeit the exclusivity property that currently makes the branch safe. Prefer
plumbing the real type through over widening the algorithm set.

## Source references

- `firestarter_app/firestarter/chip_test.py:382,393` — the type-agnostic gate
- `firestarter_app/firestarter/chip_test.py:404` — erase composition
- `firestarter_app/firestarter/chip_test.py:619-670` — write-region constants + `_write_region_for`
- `firestarter_app/firestarter/cli_handlers.py:1833-1839` — the confirm prompt
