---
created: 2026-08-22T00:00:00Z
title: "MAX_27C020_SIZE is derivable, lives in the app instead of the generator, and its firmware-parity test guards a firmware constant that does not exist"
area: host
resolves_phase: unassigned
files:
  - firestarter_app/firestarter/constants.py
  - firestarter_app/tools/build_db.py
  - firestarter_app/firestarter/constants.py  (test_revision_constants_parity.py DELETED 2026-09-14)
  - firestarter_app/firestarter/data/pinouts.json
---

## Closed — 2026-09-18 (Phase 197, plan 197-01)

Point 1, the only point left open after the 2026-09-10 update below, is now closed. Plan
`197-01` (Phase 197, `197-the-override-mechanism-and-the-program-pulse`) derived away the
`_PGM_ON_PIN31_MAX_SIZE` constant per CONTEXT.md's D-09: the fork between `DIP32_27C020`
(pin 31 = PGM) and `DIP32_STD` (pin 31 = A18) is now computed from `code_memory_size`
arithmetic (`(mem_size - 1).bit_length() <= 18`) rather than compared against a named
262144 constant. The byte-identical proof — an exhaustive integer-identity check over the
practical domain plus a full-pipeline regeneration producing a database byte-identical to
the one committed before the change — is `firestarter_app` commit `5fec5eb` (Plan 197-01
Task 3). `197-REGEN-DIFF.md`'s independently measured phase-wide regeneration diff
additionally confirms the derivation contributes zero diff across all 746 rows, exactly as
claimed.

## Status update — 2026-09-10 (Phase 182, plan 182-02)

**Points 2 and 3 are resolved; point 1 is not.** Plan 182-02 deleted `MAX_27C020_SIZE` from
`firestarter/constants.py` and deleted its self-comparing parity arm outright (the docstring cited
a firmware `#define` that does not exist, so the assertion compared the host constant to a literal
copy of itself). The decode boundary now lives in `tools/build_db.py` as a module-local constant
with an honest name and no host-to-firmware parity claim, and a real 32-pin dispatch test replaced
the retired arm.

What remains is point 1 alone: the boundary is still a **constant** rather than derived from
`code_memory_size` arithmetic. Note that 182-02 also narrowed its blast radius — the 32-pin
`0x08` cluster now forks on infoic's `variant_lo` first, and the size threshold survives only as
the fall-through arm (it still correctly keeps SST37VF040 on `DIP32_STD`). So the constant governs
fewer rows than when this was captured, but it has not been derived away.

## Problem

`MAX_27C020_SIZE = 262144` (`firestarter/constants.py:51`) is the size gate that splits
32-pin `0x08` parts between `DIP32_27C020` (pin 31 = PGM) and `DIP32_STD` (pin 31 = A18) at
`tools/build_db.py:300`. Three separate things are wrong with it, and they compound.

### 1. It is derivable, so it should not exist

The claim the constant encodes is *"pin 31 is PGM when the part does not need A18"* — pure
address-line arithmetic on `code_memory_size`, a real infoic field:

```python
n_lines = (mem_size - 1).bit_length()      # 262144 -> 18, 524288 -> 19
```

If `pinouts.json` holds `address-bus-pins` as an ordered superset per layout and the
generator emits `address-bus-pins[:n_lines]`, pin 31's role falls out of the slice: it is PGM
exactly when the slice does not reach it. one-rom corroborates independently
(`27C010`/`27C020`: `programming.pgm.pin = 31`; `27C040`: A18 at 31), and infoic's `<maps>`
confirms the connectivity — see
[`notes/infoic-maps-onerom-three-way-join.md`](../../notes/infoic-maps-onerom-three-way-join.md) §3.

`DIP32_27C020` and `DIP32_STD` then collapse into one layout distinguished only by the slice,
which also removes the D-04 "alias guard" reasoning the constant's comment block carries.

### 2. It is in the app, and the app never uses it

Sole consumer is `tools/build_db.py:8` (`from firestarter.constants import MAX_27C020_SIZE`).
No module under `firestarter/` reads it. It sits in the app purely to be imported back out by
the generator — the inverse of where an irreducible generator constant belongs.

### 3. The firmware constant it claims parity with does not exist

`constants.py:45-51` states:

> `Firmware parity: firestarter.h #define MAX_27C020_SIZE 262144 — a divergence is a`
> `hardware-damage A18 risk; see tests/test_revision_constants_parity.py.`

There is no such define. Verified against the firmware working tree, the checked-out branch,
and `origin/beta`:

```
git grep -n "MAX_27C020_SIZE" origin/beta   ->   (no output)
```

And `test_max_27c020_size_parity` did not read the header. **That whole module was deleted on
2026-09-14** by the source-introspection sweep; the analysis below is retained because the
hardcode in `constants.py` survives it. The test was:

```python
from firestarter.constants import MAX_27C020_SIZE
assert MAX_27C020_SIZE == 262144  # firestarter.h #define MAX_27C020_SIZE 262144
```

— a Python constant compared to a literal typed into the test body. Its `@requires_fw`
decorator and its docstring ("This test FAILs at pytest time on divergence, matching the
existing `CTRL_*`/`FLAG_*` parity discipline") both assert a cross-repo relationship the
assertion does not implement. It passes whether or not the firmware defines anything, so it
can never detect the divergence it was written to detect. Same failure shape as
[[reference_git_revlist_head1_tautology]] and
[[reference_gate_authored_before_content_can_be_unreachable]] — and worse here, because
`@requires_fw` makes it *look* like it reached across the repo boundary.

Consequence for scope: **there is nothing on the firmware side to keep in sync.** Removal is
host-only.

## What to do

1. **Adopt slicing** in `build_db.py`: layouts carry the ordered superset, the generator emits
   `address-bus-pins[:(mem_size - 1).bit_length()]`. Merge `DIP32_27C020` into `DIP32_STD`
   once the slice is in effect, keeping the merged entry's `rw-pin`/`vpp-pin` correct for both
   ends of the range.
2. **Delete** `MAX_27C020_SIZE` from `firestarter/constants.py` and its import at
   `build_db.py:8`.
3. **Delete** `test_max_27c020_size_parity`. Do not "fix" it to read the header — the
   constant should not survive in either repo. If a reviewer wants the boundary asserted, the
   honest test is that `AM27C020` resolves 18 address lines and `AM27C040` resolves 19, from
   the generated database.
4. **Audit the other `@requires_fw` parity tests in the same file** for the same defect
   pattern — a docstring claiming cross-repo validation over an assertion against an inline
   literal. `MAX_27C020_SIZE` was found by accident; there is no reason to think it is the only
   one, and `constants.py` documents several firmware-mirrored blocks (`CTRL_*`, `REVISION_*`,
   `CMD_*`) whose real coverage is now unknown.

## Sequencing

Step 1 is shared with
[`todos/pending/pinout-address-width-and-we-pin-corrections.md`](pinout-address-width-and-we-pin-corrections.md)
— the slice is a prerequisite for both, and that todo's width gate is what proves the slice
correct across all 744 rows. Land the slice once, serve both.

Standing rule this serves: nothing may be hardcoded that breaks when new ICs enter
`infoic.xml`; where a constant is genuinely irreducible it belongs in `tools/build_db.py`, not
in the app.
