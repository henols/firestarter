---
quick_id: 260825-cmt
slug: strip-narrative-comments
created: 2026-08-25
completed: 2026-08-25
status: complete
---

# Strip narrative comments from shipped source — SUMMARY

## Outcome

**2,475 comment lines removed.** Code byte-for-byte unchanged everywhere.

| | code | comment before | comment after | |
|---|---|---|---|---|
| firmware (`src`/`include`/`lib`) | 4,999 | 4,111 (45%) | **2,745 (35%)** | −1,366 |
| app package (`firestarter/`) | 10,763 | 8,287 (44%) | **7,178 (40%)** | −1,109 |

Maintenance tooling, as separately requested:

| | before | after | |
|---|---|---|---|
| `platformio.ini` | 469 L (59% comment) | 277 L | −41% |
| `tools/build_db.py` | 937 L (58% comment) | 804 L | 58% → 38% comment |

`codegen.py` / `codegen_vectors.py` were measured at 13–16% comment and left alone.

## Gates, all green on the final tree

- **Cold builds byte-identical on uno / uno328pb / leonardo** — re-run after
  every batch, not once at the end.
- `pio test -e native` 184/184, `native_nodevtools` 184/184, firmware
  `pytest tests/` **360 passed**.
- App suite **1947 passed / 29 errors** — byte-equal to the pre-cleanup
  baseline; the 29 are pre-existing `test_characterization.py` environment
  failures.
- **`build_db.py` regenerates `chip_database.json` byte-identical**
  (`sha256 0cfd3a83e881bfcc5011832940823ed70bf120e34cc9b9a504f9b77f66d5e9c9`,
  746 chips) and is AST-identical after docstring stripping.
- Every Python file verified **AST-identical** after docstring stripping;
  every C/C++ file verified identical after comment stripping. A final sweep
  of all 64 firmware source files against the pre-cleanup blob found **0 code
  differences**.

## The bar applied

A comment survives only if it explains something genuinely complicated, or
non-obvious usage. Four categories were preserved by name: hazard warnings
with physical consequences, don't-touch warnings a maintainer would otherwise
tidy away, datasheet-sourced numbers with their source, and wire-format
diagrams.

## Defects this work introduced, and what caught them

Recorded because in every case a gate caught it, not a review:

1. **A duplicated region in `eeprom_28c.cpp`** — index-slicing found an anchor
   string inside an *earlier* comment that merely mentioned the same function
   name, blowing the file from 731 to 1221 lines. Reverted; the helper was
   rewritten to fail loudly on anything but exactly one match, and every later
   edit went through it.
2. **23 nested `/*` openers** across 11 firmware files — the block helper
   replaced a *continuation* line inside an existing `/* */`, so the old opener
   then nested the new one. Caught by `-Wcomment` turning two source-contract
   suites RED. Fixed with a detector that walks comment depth; 0 remain.
3. **Four source-scanning gates** asserted exact phrases in comments:
   the firmware's CMD_LOCK_STATUS diagnostic-choice wording, `sdp_capability`'s
   pinned `static fail-closed allow-list` and `12 of the 84` prose (the latter
   broken purely by a line wrap), and `MSG_ERR_MAX_PULSES`, which survived only
   in `#` comments the gate strips. Each phrase was restored *inside* the
   shorter text rather than by reverting it.
4. **Two line-bearing sidecars** needed re-deriving whenever `eprom.cpp` moved:
   `protocol_branch_inventory.json`'s 21 `sites[]` (remapped via difflib, each
   verified by its recorded predicate at the new line) and the C-14 consumer
   census in `test_config_schema_pinned.py`.

## Where it landed, honestly

Firmware reached 35%; the app 40%. The app's residue is mostly contract
documentation the bar preserves — read-only-downstream invariants, fail-closed
rules, the mid-block-frame ack trap, the sticky-gate invariant. Pushing it much
below 40% would start deleting the "explains something complicated" class
rather than narrative.

## Deliberate exemptions, all named

- `CAP-01/02/03` in both repos — live cross-repo wire vocabulary.
- `include/frame_vectors.h` — codegen output.
- Leonardo's scattered-pinout mapping tables — exactly what a comment is for.
- The `_read_and_parse_lines` ring-fence in `serial_comm.py` — its gate says
  changes must be flagged and deferred, not re-pinned.
