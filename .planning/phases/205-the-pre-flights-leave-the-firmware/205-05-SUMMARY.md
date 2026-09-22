---
phase: 205-the-pre-flights-leave-the-firmware
plan: "05"
subsystem: firmware, json-parser
tags: [json_parser.c, simple_strtoul, input-validation, native-unity, defence-in-depth]

requires:
  - phase: 203-the-write-guard-moves-up-a-layer
    provides: "write_blank_guard.require_non_negative_address -- the host half of this same
      folded todo, which this plan's firmware half is defence-in-depth alongside."
provides:
  - "json_parser.c refuses a wire frame whose address value begins with '-', via a new
    FIELD_POLICY_REJECT_NEGATIVE row policy bit set only on key_address."
  - "Three native cases in test_read_timing_params.cpp proving the refusal, the
    unchanged positive-address path, and the OQ-3 scope guard on a non-address field."
  - "205-FLASH-RAM.md's separate fix-cost section: +22 B flash / +0 B RAM, identical on
    uno, uno328pb and leonardo, measured on the post-fix tree."
affects: [205-06, 205-07]

actuals:
  tokens: 4200
  tasks: 2
  commits: 3
  commits_by_repo:
    firestarter_fw: 1
    meta: 2

tech-stack:
  added: []
  patterns:
    - "A third row-policy bit (FIELD_POLICY_REJECT_NEGATIVE, 0x40) added alongside the
      existing FIELD_WIDTH_MASK/FIELD_POLICY_MASK scheme in json_parser.c's field-descriptor
      table -- the dispatch loop reads the matched row's policy bit before calling
      simple_strtoul, so the scope of a wire-level refusal is visible in the table rather
      than buried in a special case keyed on the key name."

key-files:
  created: []
  modified:
    - firestarter_fw/src/json_parser.c
    - firestarter_fw/test/native/avr/test_read_timing/test_read_timing_params.cpp
    - .planning/phases/205-the-pre-flights-leave-the-firmware/205-FLASH-RAM.md

key-decisions:
  - "The refusal is table-driven through a new policy bit (FIELD_POLICY_REJECT_NEGATIVE,
    0x40), set only on the key_address row via a new FIELD_REJECT_NEGATIVE macro -- not a
    special case keyed on the string \"address\". This keeps json_parser.c's existing idiom
    (FIELD / FIELD_MASK) and makes the scope visible in the table."
  - "The refusal reuses json_parse's existing -1 return channel. No new message id was
    minted -- FIELD_MASK's own comment already records why: message ids are generated from
    the meta repository's catalog, never written in the parser."
  - "The not-folded region-end json-parse coverage todo (2026-09-20-region-end-wire-key-has-
    no-json-parse-coverage.md) was NOT taken here, per the plan's own Fork C. It was never
    routed to this phase and region_end demonstrably survives Phase 205 with two
    mem_util_operation_end callers, so the gap neither closes nor widens by this plan."
  - "The plan's own verify command named a nonexistent interpreter
    (/usr/local/py-utils/bin/python -- only pytest exists at that prefix, not python).
    Substituted python3 for the acceptance-criteria scope check; the assertion logic itself
    ran unchanged and passed. Recorded as a deviation, not a design decision."

requirements-completed: [FWBLANK-01]

coverage:
  - id: D1
    description: "A wire frame carrying a negative `address` is refused by json_parse
      (returns -1, handle->address left at 0) instead of being silently clamped to 0 by
      simple_strtoul."
    requirement: FWBLANK-01
    verification:
      - kind: integration
        ref: "test/native/avr/test_read_timing/test_read_timing_params.cpp#test_negative_address_is_refused_not_clamped_to_zero"
        status: pass
      - kind: integration
        ref: "pio test -e native -f \"*test_read_timing*\" (observed RED before the fix: Expected -1 Was 0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The refusal is scoped to the address field only -- a positive address and
      a negative value on a non-address numeric field (pulse-delay) both parse exactly as
      they do today, proven by native cases rather than asserted."
    requirement: FWBLANK-01
    verification:
      - kind: integration
        ref: "test/native/avr/test_read_timing/test_read_timing_params.cpp#test_positive_address_still_parses_to_its_value"
        status: pass
      - kind: integration
        ref: "test/native/avr/test_read_timing/test_read_timing_params.cpp#test_negative_value_on_a_non_address_field_is_unchanged"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both native environments (native and native_nodevtools) and all four
      firmware CI legs are green at the fix commit."
    requirement: FWBLANK-01
    verification:
      - kind: integration
        ref: "pio test -e native (244 test cases: 244 succeeded)"
        status: pass
      - kind: integration
        ref: "pio test -e native_nodevtools (244 test cases: 244 succeeded)"
        status: pass
      - kind: integration
        ref: "pytest tests/ -o addopts=\"\" -p no:cacheprovider -q (316 passed)"
        status: pass
      - kind: integration
        ref: "pio run (uno, uno328pb, leonardo: 3 succeeded)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The fix's own per-target flash and RAM cost is measured on the post-fix
      tree and recorded as its own separate section in 205-FLASH-RAM.md, not blended with
      the sweep's reclaim."
    requirement: FWBLANK-01
    verification:
      - kind: other
        ref: "pio run -t clean + pio run on uno/uno328pb/leonardo, reproduced 3 times,
          byte-identical Flash:/RAM: lines and sha256 digests each time (+22 B flash, +0 B
          RAM, identical on all three targets)"
        status: pass
    human_judgment: false
---

# Phase 205 Plan 05: The wire address sign refusal lands as its own commit Summary

**`json_parse` now refuses a negative `address` with its existing -1 channel instead of
`simple_strtoul` silently converting `-256` to `0`, scoped to the address field alone by a
new table-driven policy bit, costing +22 B flash / +0 B RAM identically on all three AVR
targets.**

## Performance

- **Duration:** ~50 min
- **Started:** 2026-09-22T17:05:00Z (approximate — bounded by the git commit timestamps below)
- **Completed:** 2026-09-22T17:55:57Z
- **Tasks:** 2
- **Files modified:** 3 (2 firmware, 1 meta-repo document) + 1 gitlink advance

## Accomplishments

- `json_parser.c` refuses a wire frame whose `address` value begins with `-`, returning
  `json_parse`'s existing `-1` and leaving `handle->address` at its init-block 0 rather than
  a value converted from the digits after the sign.
- The refusal is expressed as a new row-policy bit, `FIELD_POLICY_REJECT_NEGATIVE` (0x40),
  set on the `key_address` row of `key_parsers[]` only — no other `simple_strtoul` call site
  changed, proven by a green scope-guard native case (`pulse-delay` with a negative value
  still parses to 0, exactly as before).
- Three native Unity cases added to `test_read_timing_params.cpp`, observed RED for the
  right reason (parser accepted and clamped, not a compile failure) before the fix, GREEN
  after, under both `native` and `native_nodevtools`.
- `205-FLASH-RAM.md` carries a new, separate section recording this fix's own per-target
  flash/RAM cost (+22 B flash, +0 B RAM, identical on `uno`, `uno328pb`, `leonardo`) with
  both Leonardo denominators and six post-fix artifact digests, reproduced three times with
  byte-identical output.
- The `firestarter_fw` gitlink is advanced to carry this plan's fix commit.

## Task Commits

Each task was committed atomically:

1. **Task 1: refuse a negative address at the wire, address field only** —
   `6e11d057b59977dd870c1ddcc588dd2f6f3ea1db` (feat, in `firestarter_fw`) — added
   `FIELD_POLICY_REJECT_NEGATIVE`, the `FIELD_REJECT_NEGATIVE` macro applied to the
   `key_address` row, and the dispatch-loop check; added the three native cases.
2. **Task 2: measure the fix's own cost and record it separately from the sweep's** —
   `d690daeb` (docs, in the meta repo) — appended the fix-cost section to
   `205-FLASH-RAM.md`.

**Gitlink advance:** `364832f5` (chore, in the meta repo) — advances the `firestarter_fw`
gitlink to `6e11d05`, per this project's per-phase gitlink-advance convention.

_Note: task 1 carried `tdd="true"` — the RED transcript is recorded below under Deviations
is not applicable (no deviation); see "TDD evidence" instead._

## TDD evidence (task 1)

RED, observed against the pre-fix tree (`pio test -e native -f "*test_read_timing*" -v`):

```
test/native/avr/test_read_timing/test_read_timing_params.cpp:467:test_negative_address_is_refused_not_clamped_to_zero:FAIL: Expected -1 Was 0. json_parse must refuse a frame whose address value begins with '-' -- the wire cannot represent a negative address, so the frame is malformed, not zero
test/native/avr/test_read_timing/test_read_timing_params.cpp:540:test_positive_address_still_parses_to_its_value:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:541:test_negative_value_on_a_non_address_field_is_unchanged:PASS

24 Tests 1 Failures 0 Ignored
FAIL
```

The failure is `Expected -1 Was 0` — the parser accepted the negative address and stored
the `simple_strtoul`-converted `0`, exactly the defect this plan fixes. It is not a compile
error. The other two new cases (`test_positive_address_still_parses_to_its_value`,
`test_negative_value_on_a_non_address_field_is_unchanged`) were GREEN from the start, as
the plan requires for the scope-guard case.

GREEN, observed against the post-fix tree (`pio test -e native -f "*test_read_timing*" -v`):

```
test/native/avr/test_read_timing/test_read_timing_params.cpp:539:test_negative_address_is_refused_not_clamped_to_zero:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:540:test_positive_address_still_parses_to_its_value:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:541:test_negative_value_on_a_non_address_field_is_unchanged:PASS

24 Tests 0 Failures 0 Ignored
OK
```

Confirmed GREEN again under `native_nodevtools` (`24 test cases: 24 succeeded`).

## The eight `simple_strtoul` call sites, enumerated (scope evidence)

`git grep -n "simple_strtoul" -- src/json_parser.c` after the fix (line numbers shifted by
the added comments; the set of call sites is unchanged from before the fix):

| Line | What it is | Changed by this plan? |
|---|---|---|
| 30 | the function definition | no |
| 107, 112 | new comment above `FIELD_POLICY_REJECT_NEGATIVE` naming the defect | added (comment only) |
| 258 | pre-existing comment on `store_field`'s `value` parameter | no |
| 356 | `key_parsers[]` dispatch-loop call (all 12 table rows, address included) | **guarded** — the new `if` runs before this call for rows with the policy bit set; the call itself is unchanged |
| 431 | `get_cmd` — the `cmd`/`state` field | no |
| 462 | `parse_bus_config`'s `bus` array (address lines) | no |
| 481 | `parse_bus_config`'s `static-high` array | no |
| 519 | the `extract_num` macro body, expanded by `extract_long`/`extract_int` for `get_rw_pin`, `get_vpp_pin`, `get_r1`, `get_r2`, `get_rev` (rw-pin, vpp-pin, r1, r2, rev) | no |
| 534 | `get_flags` — the `flags` field (`ctrl_flags`) | no |

Nine textual occurrences after the fix (was eight before — the two new comment mentions at
lines 107/112 add one net occurrence beyond the pre-existing comment at 258, satisfying the
plan's own acceptance criterion of "still contains at least nine occurrences of
`simple_strtoul`"). Every actual call site is unchanged; only the address row gained a
guard in front of its call, not a changed call.

## Files Created/Modified

- `firestarter_fw/src/json_parser.c` — `FIELD_POLICY_REJECT_NEGATIVE` (0x40), the
  `FIELD_REJECT_NEGATIVE` macro, the `key_address` row's macro swap, and the dispatch-loop
  sign check.
- `firestarter_fw/test/native/avr/test_read_timing/test_read_timing_params.cpp` — three new
  cases (negative-address refusal, positive-address round-trip, non-address scope guard)
  and their `RUN_TEST` lines.
- `.planning/phases/205-the-pre-flights-leave-the-firmware/205-FLASH-RAM.md` — new "Plan 05
  — the negative-address fix's own flash/RAM cost" section.

## Decisions Made

- **Table-driven policy bit, not a special case.** `FIELD_POLICY_REJECT_NEGATIVE` follows
  the file's existing `FIELD`/`FIELD_MASK` idiom (Fork A). The scope — one row, one bit — is
  visible in `key_parsers[]` rather than buried in an `if (jsoneq(...,"address"))` special
  case in the dispatch loop.
- **`-1` return, no new message id.** Fork B: reuses the channel a non-JSON-object frame and
  a malformed bus-config already use. `tools/catalog/messages.toml` is untouched by the
  firmware commit, confirmed by `git show --name-only`.
- **The not-folded `region-end` json-parse coverage todo was NOT taken** (Fork C, as the
  plan pre-decided). `2026-09-20-region-end-wire-key-has-no-json-parse-coverage.md` remains
  unrouted to this phase; taking its ready-to-drop-in cases here was permitted but not
  required, and was not done. Recorded here so the todo's next reader knows it was
  considered.
- **`/usr/local/py-utils/bin/python` does not exist** on this machine (only
  `/usr/local/py-utils/bin/pytest` does, per the project's own stated test environment).
  The plan's acceptance-criteria verify command named that path; `python3` was substituted
  to run the identical assertion logic, which passed. This is a tooling-path correction, not
  a change to what was being verified.

## Deviations from Plan

None — plan executed exactly as written. The `/usr/local/py-utils/bin/python` → `python3`
substitution (Rule 3 — blocking issue with the verify tooling path, not the implementation)
is recorded above under Decisions Made rather than as a separate deviation entry, because it
changed no code and no test outcome — only which interpreter ran an unmodified assertion.

## Issues Encountered

None. The three `firestarter_fw/tests/` failures observed transiently while the working
tree had uncommitted edits (`test_flash_path_record_sync.py` and
`test_trace_segment_exhaustiveness_v131.py`'s porcelain-assertion legs) were the known
"asserts whole-repo porcelain — commit before running it" trap, not a regression. They
disappeared on the post-commit re-run (316 passed).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The folded todo `2026-09-16-reject-negative-write-start-address.md` is now resolved by
  **both** halves: the host half in Phase 203
  (`write_blank_guard.require_non_negative_address`, `NegativeStartAddressError`) and the
  firmware half here (`firestarter_fw` commit `6e11d057b59977dd870c1ddcc588dd2f6f3ea1db`).
  The todo file itself was left in `.planning/todos/pending/` unmoved, matching this phase's
  established precedent for its two sibling folded todos (`2026-08-30-...` and
  `2026-09-20-blank-check-region-...`), both also still pending — moving folded todos to
  `completed/` was not this plan's stated artifact and is left for a later closing action.
- `205-FLASH-RAM.md`'s plan-05 fix-cost section (+22 B flash, +0 B RAM per target) is ready
  for plan 06 to add onto the sweep's own reclaim when it fills the phase-exit section and
  computes the phase's net delta.
- No blocker for plan 06. This plan's commit (`6e11d05`) sits on top of plan 04's HEAD
  (`9061dd1`) with no conflicting file touched by the sweep plans.

## Self-Check: PASSED

- `[ -f /workspaces/firestarter_fw/src/json_parser.c ]` → FOUND
- `[ -f /workspaces/firestarter_fw/test/native/avr/test_read_timing/test_read_timing_params.cpp ]` → FOUND
- `[ -f /workspaces/.planning/phases/205-the-pre-flights-leave-the-firmware/205-FLASH-RAM.md ]` → FOUND
- `git -C /workspaces/firestarter_fw log --oneline --all | grep -q 6e11d05` → FOUND
- `git -C /workspaces log --oneline --all | grep -q d690daeb` → FOUND
- `git -C /workspaces log --oneline --all | grep -q 364832f5` → FOUND
- Re-ran all task 1 `<acceptance_criteria>`: native (`native`/`native_nodevtools`) 24/24
  PASSED each, `pytest tests/` 316 passed, `pio run` 3/3 SUCCESS, scope python check passed,
  `git show --name-only HEAD` in `firestarter_fw` lists exactly the two files — all PASS.
- Re-ran all task 2 `<verify>` legs: clean `pio run` prints 3 `Flash:`/3 `RAM:` lines, six
  digests produced, `205-FLASH-RAM.md` contains both `pre-fix`/`post-fix` markers, and
  `git status --porcelain` in `firestarter_fw` is empty — all PASS.
- `git -C /workspaces/firestarter_fw rev-parse --abbrev-ref HEAD` → `v1.41-verification-to-host`
- `git -C /workspaces rev-parse --abbrev-ref HEAD` → `v1.41-verification-to-host`
- Meta gitlink for `firestarter_fw` (`git ls-tree HEAD -- firestarter_fw`) → `6e11d057b59977dd870c1ddcc588dd2f6f3ea1db`, matching firmware HEAD exactly.

---
*Phase: 205-the-pre-flights-leave-the-firmware*
*Completed: 2026-09-22*
