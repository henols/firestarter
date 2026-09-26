---
quick_id: 260825-cmt
slug: strip-narrative-comments
created: 2026-08-25
status: in-progress
---

# Strip narrative comments from shipped source

## Operator ruling (2026-08-25)

GSD provenance was only half the problem. The **explanations of what was done and
why** are changelog content: git already records them, and in the source they are
bloat. The v1.33 sweep stripped tokens but preserved the narrative, which left the
bloat in place and made it worse — unattributed history with no trace back.

**Bar (strict, operator's own words):** a comment survives only if it explains
something genuinely complicated, or how to use something when that is not obvious.

**Scope:** `firestarter/{src,include,lib}` and `firestarter_app/firestarter`.
NOT the test trees, NOT `firestarter_app/tools/`.

**Preserve — four named categories:**
1. Hazard/safety warnings with physical consequences not visible from the code
   (e.g. the 12V VPP boost regulator on a 5V part).
2. Don't-touch warnings a maintainer would otherwise "tidy" away and break the
   build (e.g. `EPROM_OVERPROGRAM_SUPPORTED` = 0 for leonardo only, Caterina cliff).
3. Datasheet-sourced numbers, with their source — arbitrary and non-re-derivable
   without it.
4. Wire-format / ASCII layout diagrams. One of these is additionally asserted to
   exist by `test_cap03_ack_layout_parity.py`.

## Starting state

| | firmware | app package |
|---|---|---|
| code lines | 5,001 | 10,739 |
| comment lines | 4,111 (45%) | 8,287 (44%) |

## Approach

Sample 3 files first, show the operator, then continue on approval.

## Gates (unchanged from the sweep)

- Cold byte-identical `.elf`/`.hex` on uno/uno328pb/leonardo — comments only.
- `pio test -e native` and `-e native_nodevtools` at 184/184; firmware `pytest tests/` 360.
- App suite at 1947 passed / 29 pre-existing errors.
- Most source-scanning tests strip comments first; the one exception is the
  CAP-03 wire-layout comment, which is a category-4 keeper anyway.
