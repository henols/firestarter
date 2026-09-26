---
phase: 201-a-partial-write-is-gated-on-its-own-region
plan: 04
subsystem: firmware-protocol
tags: [blank-check, write-path, verify-path, region-scoping, progress-emission, wire-protocol, branch-inventory-golden]

# Dependency graph
requires:
  - phase: 201-03
    provides: "mem_util_operation_end(handle) — the single resolution point for D-04's
      0=absent=whole-device fallback and the fail-closed clamp min(region_end, mem_size),
      defined in memory.cpp precisely so eprom_operations.cpp and eprom.cpp can both call
      it without adding a branch-inventory row or tripping the progress gate's
      parenthesis-intolerant capture."
provides:
  - "op_end local in _process_incoming_data (eprom_operations.cpp), resolved once per call,
    bounding both the done-condition and the MSG_ERR_OUT_OF_RANGE refusal — and, because
    eprom_write and eprom_verify both route through this shared function, bounding verify
    too with no second edit (D-07)."
  - "op_end local in eprom_internal_write_execute_body (eprom.cpp), hoisted before the
    per-byte loop inside the existing #ifndef SERIAL_ON_IO guard, replacing handle->mem_size
    as the write-loop's MSG_DATA_PROGRESS denominator."
  - "test_progress_emission_is_leonardo_only.py's Coverage 6 assertion retargeted from the
    literal handle->mem_size to op_end, with its failure message and module docstring
    rewritten to state the restated one-payload-meaning contract rather than silently
    swapping the string."
  - "tests/golden/protocol_branch_inventory.json re-derived a second time this phase, using
    POSITIONAL (not predicate-keyed) matching to carry class/reason forward safely."
affects: [201-05, 201-06]

actuals:
  tokens: 16297
  tasks: 2
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Golden re-derivation matched old sites to live sites BY POSITION (zip by index),
      not by rebuilding a (predicate, keyed_on, tier) dict key — that key collides for
      sites sharing identical predicate text and is exactly what silently corrupted
      class/reason in plan 201-03's first re-derivation. Positional correspondence was
      verified safe (zero (predicate, keyed_on, tier) mismatches between old[i] and
      live[i] for all i) before being trusted."
    - "A local read only inside an #ifndef SERIAL_ON_IO block is declared INSIDE that same
      guard, not unconditionally — matching the file's own existing last_emit_ms pattern,
      to avoid an unused-variable warning on builds that define the flag."

key-files:
  created: []
  modified:
    - firestarter_fw/src/eprom_operations.cpp
    - firestarter_fw/src/proms/eprom.cpp
    - firestarter_fw/tests/test_progress_emission_is_leonardo_only.py
    - firestarter_fw/tests/golden/protocol_branch_inventory.json

key-decisions:
  - "op_end is declared inside the same #ifndef SERIAL_ON_IO guard as last_emit_ms in
    eprom.cpp, not unconditionally, because it is read only inside that guard's emit
    block and an unreferenced local on a build that defines SERIAL_ON_IO would be an
    unused-variable warning against the AVR zero-warning policy."
  - "The golden's second re-derivation used positional matching, not the
    (predicate, keyed_on, tier) dict-key lookup RESEARCH.md's own script builds — that
    key is exactly what collided and corrupted class/reason in plan 201-03's first
    re-derivation (76fd3c7, repaired in 0c2eac7). See Deviations for the full
    field-by-field proof."

requirements-completed: [BLANK-01, BLANK-02]

coverage:
  - id: D1
    description: "_process_incoming_data's done-condition and its MSG_ERR_OUT_OF_RANGE
      refusal now bound on op_end (mem_util_operation_end(handle)) instead of
      handle->mem_size. Because eprom_write and eprom_verify both route through this
      shared function via op_execute_stateful_operation, the one edit bounds write AND
      verify (D-07) — no second edit exists anywhere for verify."
    requirement: BLANK-01
    verification:
      - kind: unit
        ref: "firestarter_fw pio test -e native (237/237) and -e native_nodevtools (237/237)"
        status: pass
      - kind: other
        ref: "comment-stripped, brace-matched scan of _process_incoming_data: zero
          handle->mem_size occurrences after the edit"
        status: pass
      - kind: unit
        ref: "firestarter_fw FIRESTARTER_META_ROOT=/tmp/no-meta pytest tests/ (269 passed,
          32 skipped, 0 failed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The write-loop's MSG_DATA_PROGRESS denominator moved from
      handle->mem_size to op_end (hoisted before the per-byte loop), and
      test_progress_emission_is_leonardo_only.py's Coverage 6 assertion, failure message
      and module docstring were rewritten in the same commit to restate the
      one-payload-meaning contract for the new denominator rather than silently swap the
      literal."
    requirement: BLANK-01
    verification:
      - kind: unit
        ref: "firestarter_fw tests/test_progress_emission_is_leonardo_only.py (11 passed,
          no leg reporting found 0)"
        status: pass
    human_judgment: false
  - id: D3
    description: "tests/golden/protocol_branch_inventory.json re-derived a second time this
      phase, in the same commit as the eprom.cpp source change, with class/reason carried
      forward by POSITION rather than by the colliding predicate-keyed lookup that
      corrupted the phase's first re-derivation."
    requirement: ""
    verification:
      - kind: unit
        ref: "firestarter_fw tests/test_protocol_branch_inventory.py (7/7 passed)"
        status: pass
      - kind: other
        ref: "field-by-field diff of all 22 rows against the parent commit (01db51b):
          0 non-line diffs; 8 rows' line shifted, all below the insertion point"
        status: pass
    human_judgment: false
  - id: D4
    description: "The leonardo flash figure after this change is measured and recorded
      against the phase's running baseline trail, since no CI leg gates it."
    requirement: ""
    verification:
      - kind: other
        ref: "firestarter_fw pio run -e leonardo (bootloader-guard tool output)"
        status: pass
    human_judgment: true
    rationale: "No automated ceiling check exists (platformio.ini overrides
      board_upload.maximum_size to 32768 against a real 28672 B Caterina ceiling) — a
      human should see the margin trend across plans in this phase, not just this
      plan's own pass/fail."

duration: ~70min
completed: 2026-09-20
status: complete
---

# Phase 201 Plan 04: Write and Verify Bounded on the Operation's End Summary

**`_process_incoming_data`'s done-condition and out-of-range refusal — shared by `eprom_write` and `eprom_verify` — and the write-loop's `MSG_DATA_PROGRESS` denominator now read `op_end` (`mem_util_operation_end(handle)`) instead of `handle->mem_size`; the progress gate's one-payload-meaning contract is restated rather than silently swapped, and the branch-inventory golden is re-derived a second time this phase using position-based matching to avoid the predicate-key collision that corrupted the phase's first re-derivation.**

## Performance

- **Duration:** ~70 min
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- `src/eprom_operations.cpp` now includes `memory_utils.h` and resolves
  `const uint32_t op_end = mem_util_operation_end(handle);` once at the top of
  `_process_incoming_data`, before the done-condition. `handle->mem_size` is replaced with
  `op_end` at exactly two places — the done-condition (`if (handle->address >= op_end)`) and
  the `OP_MSG_DATA` refusal (`if (handle->address + handle->data_size > op_end)`) — and
  nowhere else in the file. A comment-stripped, brace-matched scan of the function body
  confirms zero remaining `handle->mem_size` occurrences.
- Because `eprom_write` and `eprom_verify` both call `op_execute_stateful_operation(_process_incoming_data, handle)`,
  the one edit bounds both operations. D-07 is satisfied by the shared function, not by a
  second edit — there is no second call site for verify anywhere in the file.
- `src/proms/eprom.cpp`'s `eprom_internal_write_execute_body` gained a second local,
  `const uint32_t op_end = mem_util_operation_end(handle);`, hoisted before the per-byte
  loop and declared inside the SAME `#ifndef SERIAL_ON_IO` guard as the pre-existing
  `last_emit_ms` — for the identical zero-warning reason the file's own comment already
  gives for that local: `op_end` is read only inside the guarded emit block. The emit's
  second argument changed from `handle->mem_size` to the bare identifier `op_end`; nothing
  inline (no ternary, no cast, no function call) was written inside the
  `LOG_DATA_ID_U32_U32(...)` argument list, since `_EMIT_BLOCK_RE`'s `arg2` capture group
  cannot match an expression containing parentheses. The `:381` prose comment describing the
  payload was rewritten to state what the emit now sends: `(absolute chip address, op_end)`,
  "the end of the operation's range", not merely "the device size".
- `tests/test_progress_emission_is_leonardo_only.py`'s Coverage 6 test
  (`test_the_payload_keeps_one_contract_for_the_id`) is retargeted:
  - **Old literal:** `arg2 == "handle->mem_size"`
  - **New literal:** `arg2 == "op_end"`
  - **Restated contract** (failure message and module docstring, both rewritten in the same
    commit): *"D-06: after this plan, 0xE0's denominator means the end of the operation's
    range, which is the device size for a whole-device operation and the region end for a
    bounded one — still one meaning, expressed by a value that equals the device size
    whenever no region was supplied. A block-relative pair would give the id a second
    meaning depending on which operation emitted it; that argument is not overturned by
    this change, only restated."* The assertion stayed an exact-literal equality — no
    substring match, no regex, no any-identifier check. All 11 legs in the module pass with
    none reporting `found 0`.
- `tests/golden/protocol_branch_inventory.json` re-derived a second time this phase (the
  first was plan 201-03's `76fd3c7`), in the same commit as the `eprom.cpp` source change.
  **Blob sha:** `8fa3c7a00869ed6ee3165e5ba538d42c144eb347` → `e3b53d9d2f7bf7925d1c1fc16bc4a0aaee17884b`
  (matches `git hash-object src/proms/eprom.cpp` on the committed tree). **`recorded_at_head`:**
  `01db51b79a77255e13f2fc201635ad0cf48b0f77` (this commit's parent — Task 1's own commit,
  per the golden's established one-commit-offset convention). Zero new predicate rows
  (the new `op_end` local is a plain function-call assignment, not a ternary); all 22 sites
  unchanged in predicate/keyed_on/tier/class/reason, only 8 line numbers shifted below the
  insertion point (see "Golden re-derivation" below for the full field-by-field proof).
  `protocol_lines` stays `[70]` — no line was inserted above `eprom.cpp:70`.
- **Commit contains exactly the three expected paths:** `src/proms/eprom.cpp`,
  `tests/golden/protocol_branch_inventory.json`, `tests/test_progress_emission_is_leonardo_only.py`
  — confirmed by `git diff --name-only` against Task 2's own pre-edit base commit.
- `operation_utils.cpp` and `src/proms/memory.cpp` are byte-unchanged across the whole plan
  (both BLANK-02's frozen standalone blank-check emit and plan 201-03's write-init/erase-end
  resolution point are untouched).
- Both native environments report **237 succeeded, 0 failed** at every checkpoint;
  `FIRESTARTER_META_ROOT=/tmp/no-meta pytest tests/` reports **269 passed, 32 skipped, 0
  failed** post-commit, including `test_protocol_branch_inventory.py`. `pio run` builds all
  three AVR environments SUCCESS.

## Task Commits

Each task was committed atomically, inside `firestarter_fw` on `v1.40-program-parameter-fidelity`:

1. **Task 1: Bound write and verify on the operation's end, not the device's size** — `01db51b` (feat)
2. **Task 2: Move the write-loop denominator, re-argue the one-payload-meaning contract, re-derive the golden** — `cb6b434` (feat)

**Meta-repository gitlink advance:** `13981bed` (feat) — `firestarter_fw` pointer moved
`0c2eac79` → `cb6b4343` in `/workspaces` on `v1.40-program-parameter-fidelity`.

### `pio test` summary, both environments (post-commit)

```
native             : 237 test cases: 237 succeeded in 00:00:44.867
native_nodevtools  : 237 test cases: 237 succeeded in 00:00:47.466
```

### `FIRESTARTER_META_ROOT=/tmp/no-meta pytest tests/` (post-commit)

```
269 passed, 32 skipped in 12.68s
```

### `pio run` — leonardo flash figure

```
leonardo: Flash 24134/32768 B (73.7%)
bootloader-guard: leonardo 24134/28672 B (84.2% of the safe ceiling, 4538 B margin, 4096 B bootloader reserved)
```

Baseline trail: 23816 B (pre-phase, RESEARCH.md) → 23850 B (201-02) → 23932 B (201-03) →
**23970 B** (this plan, Task 1: the `op_end` local + comment in `eprom_operations.cpp`) →
**24134 B** (this plan, Task 2: the second `op_end` local + comment in `eprom.cpp`). +318 B
over the pre-phase baseline, +202 B over 201-03. uno and uno328pb both `SUCCESS`
(21850/32256 B and 21894/32384 B respectively — Uno-class targets carry no
`op_end`/progress-emit change at all, since `SERIAL_ON_IO` compiles that whole block out; the
small movement there is the shared `_process_incoming_data` edit only). No size gate exists
in CI (`platformio.ini:78-82` overrides `board_upload.maximum_size` to `32768` against the
real 28672 B Caterina ceiling), so this figure is a measurement, not an enforced pass.

### Golden re-derivation — field-by-field proof

Positional correspondence verified BEFORE trusting it to carry `class`/`reason` forward:

```
counts old->new: 0 (predicate, keyed_on, tier) mismatches between old[i] and live[i] for all 22 i
```

Field-by-field diff of all 22 rows, re-derived golden vs. parent commit `01db51b`:

```
per-row non-line field diffs (predicate/keyed_on/tier/class/reason): 0
rows with line diff (expected -- shifted below the op_end insertion point): 8
top-level keys that differ from parent: ['meta', 'sites']
  meta.blob_shas['src/proms/eprom.cpp'] old: 8fa3c7a00869ed6ee3165e5ba538d42c144eb347
  meta.blob_shas['src/proms/eprom.cpp'] new: e3b53d9d2f7bf7925d1c1fc16bc4a0aaee17884b
  meta.recorded_at_head old: af47bf464a24c005e556cf3d7308679064feca5e
  meta.recorded_at_head new: 01db51b79a77255e13f2fc201635ad0cf48b0f77
  counts: unchanged ({total_sites: 22, protocol_keyed_sites: 1, other_sites: 21})
  recorded_by: appended (this plan's paragraph)
```

Zero per-row field diffs on all 22 rows besides the 8 expected line-number shifts; only the
two legitimate `meta` fields plus the appended `recorded_by` paragraph differ from the
parent. `test_protocol_branch_inventory.py` 7/7 passed post-commit.

## Files Created/Modified

- `firestarter_fw/src/eprom_operations.cpp` — adds `#include "memory_utils.h"`; resolves
  `op_end` once at the top of `_process_incoming_data`; replaces `handle->mem_size` with
  `op_end` at the done-condition and the `OP_MSG_DATA` out-of-range refusal.
- `firestarter_fw/src/proms/eprom.cpp` — adds `op_end` inside the existing
  `#ifndef SERIAL_ON_IO` guard in `eprom_internal_write_execute_body`; changes the
  `MSG_DATA_PROGRESS` emit's second argument from `handle->mem_size` to `op_end`; rewrites
  the `:381` prose comment describing the payload.
- `firestarter_fw/tests/test_progress_emission_is_leonardo_only.py` — retargets Coverage 6's
  assertion from `handle->mem_size` to `op_end`; rewrites the assertion's failure message and
  the module docstring's Coverage 6 entry to restate the one-payload-meaning contract.
- `firestarter_fw/tests/golden/protocol_branch_inventory.json` — re-derived a second time
  this phase: blob sha, `recorded_at_head`, and `recorded_by` updated in the same commit as
  the source edit; `class`/`reason` on all 22 rows carried forward by position, not by the
  colliding predicate-keyed lookup RESEARCH.md's own script builds.

## Decisions Made

See `key-decisions` in frontmatter. Both are recorded in more detail in the Deviations
section below, since the second one corrects a defect the plan's own action text (quoting
RESEARCH.md's script verbatim) would have reproduced.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The plan's own cited re-derivation script (RESEARCH.md § G-2) would have repeated plan 201-03's `class`/`reason` corruption; used positional matching instead**
- **Found during:** Task 2, running a field-by-field comparison against the parent commit
  after the first re-derivation attempt (following the plan's action text, which points at
  RESEARCH.md § G-2's script verbatim)
- **Issue:** RESEARCH.md's own runnable re-derivation script builds an old-value lookup keyed
  on `(predicate, keyed_on, tier)`, exactly the technique that corrupted plan 201-03's first
  re-derivation (`76fd3c7`, repaired in `0c2eac7`): that key collides for two site pairs
  sharing identical predicate text (`FLAG_SKIP_BLANK_CHECK`/`ctrl_flags` and
  `RESPONSE_CODE_ERROR`/`response_code`, the latter appearing at four lines in this file), so
  a plain dict comprehension keeps only the last-inserted value per colliding key and earlier
  sites silently inherit a sibling's `reason`. Running that exact script here reproduced the
  identical failure mode: a first field-by-field diff against the parent showed real
  divergences at indices 6, 10 and 15 (a `class` value and `reason` text both replaced with
  an unrelated sibling's content), even though I had added `class`-carrying logic on top of
  the script's own key — the key itself, not merely the missing `class` field, was the
  defect. This project's `firestarter_fw/CLAUDE.md`-adjacent operator guidance for this exact
  phase names the fix directly: key on `line`, which is unique, never on predicate text — but
  `line` differs between the parent (pre-edit) and live (post-edit) golden here, unlike plan
  201-03's case where no line shifted, so a direct line-keyed lookup does not apply as-is.
- **Fix:** Matched old sites to live sites BY POSITION (`zip(old, live)`) instead of by any
  dict key. Verified this was safe FIRST — a positional comparison of
  `(predicate, keyed_on, tier)` between `old[i]` and `live[i]` for all 22 `i` showed zero
  mismatches, confirming no site was added, removed, or reordered by the `op_end` insertion
  (the only structural change RESEARCH.md's own "Predicted impact" section already
  anticipated: a plain function-call assignment adds no new predicate, only shifts line
  numbers below the insertion point). Only then were `class` and `reason` carried forward
  positionally. A second field-by-field diff against the parent then showed 0 non-line
  diffs across all 22 rows, with exactly 8 rows' `line` shifting (all below the insertion
  point) and only the two legitimate `meta` fields plus the appended `recorded_by`
  paragraph differing.
- **Files modified:** `tests/golden/protocol_branch_inventory.json`
- **Verification:** positional `(predicate, keyed_on, tier)` comparison — 0 mismatches
  across 22 rows; field-by-field diff against parent `01db51b` — 0 non-line diffs across 22
  rows; `test_protocol_branch_inventory.py` 7/7 passed; `pio test -e native` 237/237,
  `-e native_nodevtools` 237/237; `FIRESTARTER_META_ROOT=/tmp/no-meta pytest tests/` 269
  passed / 32 skipped / 0 failed.
- **Committed in:** `cb6b434` (the golden was never committed in its first, corrupted form —
  the defect was caught and corrected before staging, unlike plan 201-03 where it reached a
  commit and needed a follow-up repair)

---

**Total deviations:** 1 (Rule 1 — a bug correction to the plan's own cited re-derivation
technique, caught before it reached a commit). No architectural change and no scope creep;
the correction uses a strictly stronger verification (positional correspondence checked
first, then a full field-by-field diff) than either the plan's own action text or
RESEARCH.md's script specified.
**Impact on plan:** Necessary to keep the branch-inventory golden's documentation intact
this time, rather than repeating plan 201-03's corrupt-then-repair sequence. No assertion
was weakened; if anything, this plan's re-derivation is now the more careful precedent for
plan 201-05 and any future re-derivation of this golden.

## Issues Encountered

None beyond the deviation documented above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- BLANK-01 and BLANK-02 remain `Pending` in REQUIREMENTS.md by design (the shared-ID gate):
  BLANK-01 is also declared by plan 201-06 (no `SUMMARY.md` yet, bench-gated); BLANK-02 is
  also declared by plan 201-05 (no `SUMMARY.md` yet). Both flip once their last declaring
  plan finishes.
- Plan 201-05 has its target: the D-15.3 source-contract gate over all nine
  `mem_util_blank_check` reference sites (3 direct calls + 6 function-pointer assignments).
  This plan touched none of those nine sites — `_process_incoming_data` and
  `eprom_internal_write_execute_body` call `mem_util_operation_end`, not
  `mem_util_blank_check` — so all nine remain exactly as plan 201-03 left them, ready for
  201-05's gate to enumerate.
- Plan 201-05 also inherits a working, verified template for the golden's THIRD potential
  re-derivation, if its own source edit needs one: match by position after confirming
  positional `(predicate, keyed_on, tier)` correspondence first, never by rebuilding the
  colliding dict-key lookup.
- Write and verify now agree with the blank check on where the operation ends: all three of
  D-06's named sites (`_process_incoming_data`'s two, and the write-loop progress
  denominator) plus plan 201-03's write-init call site read from the same
  `mem_util_operation_end(handle)` resolution point.
- No blockers. All three repositories remain on `v1.40-program-parameter-fidelity`.

## Self-Check: PASSED

- FOUND: `firestarter_fw/src/eprom_operations.cpp`
- FOUND: `firestarter_fw/src/proms/eprom.cpp`
- FOUND: `firestarter_fw/tests/test_progress_emission_is_leonardo_only.py`
- FOUND: `firestarter_fw/tests/golden/protocol_branch_inventory.json`
- FOUND: commit `01db51b` (`git -C firestarter_fw log --oneline --all`)
- FOUND: commit `cb6b434` (`git -C firestarter_fw log --oneline --all`)
- FOUND: commit `13981bed` (`git log --oneline --all`, meta repo gitlink advance)
- Re-ran acceptance criteria and plan-level `<verification>`: `pio test -e native` 237/237;
  `-e native_nodevtools` 237/237; `FIRESTARTER_META_ROOT=/tmp/no-meta pytest tests/` 269
  passed / 32 skipped / 0 failed (including `test_protocol_branch_inventory.py` and
  `test_progress_emission_is_leonardo_only.py`); comment-stripped scan of
  `_process_incoming_data` shows zero `handle->mem_size` occurrences; the write-loop emit
  carries `op_end` as a bare identifier exactly once; the golden's recorded blob sha matches
  `git hash-object src/proms/eprom.cpp` on the committed tree; `protocol_lines == [70]`; no
  `reason` starts with `TODO`; `operation_utils.cpp` and `src/proms/memory.cpp` confirmed
  byte-unchanged via diff against each task's own pre-edit base commit; `pio run` 3/3
  SUCCESS, leonardo 24134/28672 B with 4538 B bootloader-guard margin;
  `git -C firestarter_fw rev-parse --abbrev-ref HEAD` and `git rev-parse --abbrev-ref HEAD`
  (meta) both `== v1.40-program-parameter-fidelity`; the meta gitlink in `13981bed` matches
  `firestarter_fw`'s own HEAD exactly.

---
*Phase: 201-a-partial-write-is-gated-on-its-own-region*
*Completed: 2026-09-20*
