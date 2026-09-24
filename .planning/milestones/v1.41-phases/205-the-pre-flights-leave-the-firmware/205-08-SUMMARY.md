---
phase: 205-the-pre-flights-leave-the-firmware
plan: 08
subsystem: firmware-host-write-guard
tags: [write-blank-guard, nor-unlock, protocol-0x06, cr-01, gap-closure]

requires:
  - phase: 205-the-pre-flights-leave-the-firmware
    provides: >
      Plan 205-03's removal of the firmware write-init blank check and 205-04's
      blank_check_requested keyword-only re-plumb, both of which this plan's guard-skip
      branch builds directly on top of.
provides:
  - "An address-aware erase exemption on write_blank_guard.is_erase_exempt/requires_blank_check for protocol 0x06 (NOR-unlock)."
  - "A 13-test regression matrix pinning the address dimension against hand-built and real resolve_chip dicts, plus a live-database census."
  - "A recorded decision (205-CR-01-DECISION.md) closing CR-01 inside Phase 205 rather than deferring it."
affects: [206-dev-test-session-lease, 207-release-version-bump]

actuals:
  tokens: 7809
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Keyword-only address parameter threaded through a pure predicate, default-0 behaviour-preserving (mirrors 205-04's blank_check_requested)."
    - "Check-not-refuse fallback for a region-scoped guard, contrasted explicitly with cli_handlers.py's whole-device refuse (_erase_sector_blank_refusal_exit_code)."

key-files:
  created:
    - .planning/phases/205-the-pre-flights-leave-the-firmware/205-CR-01-DECISION.md
  modified:
    - firestarter_app/firestarter/write_blank_guard.py
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/tests/test_write_blank_guard.py
    - firestarter_app/tests/test_write_blank_guard_pinning.py

key-decisions:
  - "D-G1: the address parameter lives on is_erase_exempt itself (not only its caller), keyword-only, default 0."
  - "D-G2: a non-zero-address 0x06 write falls back to the ordinary region-scoped blank check — checked, not refused. The rejected refusal route is recorded as one-way."
  - "D-G3: no sector-size model invented; any non-zero address withdraws the exemption conservatively."
  - "D-G4: an absent or unparseable -a resolves to address 0, preserving the existing malformed-address error contract in _setup_operation."

requirements-completed: [FWBLANK-01]

coverage:
  - id: D1
    description: "is_erase_exempt/requires_blank_check withdraw the erase exemption for protocol 0x06 at a non-zero write address, proven end to end through the genuine write_eprom against a fake serial port."
    requirement: FWBLANK-01
    verification:
      - kind: unit
        ref: "tests/test_write_blank_guard.py#test_is_erase_exempt_is_false_for_nor_unlock_at_a_non_zero_address"
        status: pass
      - kind: integration
        ref: "tests/test_write_blank_guard.py#test_write_at_a_non_zero_address_on_an_erase_capable_nor_unlock_part_pays_a_guard_read"
        status: pass
    human_judgment: false
  - id: D2
    description: "The exemption is unchanged for algorithm 0x10 at every address and for 0x07/0x08/0x0B, each pinned to the firmware fact that makes it sound."
    requirement: FWBLANK-01
    verification:
      - kind: unit
        ref: "tests/test_write_blank_guard.py#test_is_erase_exempt_is_true_for_intel_flash_at_every_address"
        status: pass
    human_judgment: false
  - id: D3
    description: "A blank non-zero-address region still writes; a non-blank one is refused with the existing one-line host refusal; -b and --skip-erase keep their documented behaviour."
    requirement: FWBLANK-01
    verification:
      - kind: integration
        ref: "tests/test_write_blank_guard.py#test_write_at_address_zero_on_an_erase_capable_nor_unlock_part_still_pays_no_guard_read"
        status: pass
      - kind: integration
        ref: "tests/test_write_blank_guard.py#test_write_at_a_non_zero_address_on_a_non_blank_nor_unlock_region_is_refused"
        status: pass
      - kind: unit
        ref: "tests/test_write_blank_guard.py#test_requires_blank_check_blank_check_requested_false_still_bypasses_at_a_non_zero_nor_unlock_address"
        status: pass
    human_judgment: false
  - id: D4
    description: "The 13-test regression matrix plus the tracer's own leg pin the address dimension against hand-built dicts, real resolve_chip dicts, and a live-database census that the affected surface is the whole protocol-0x06 family."
    requirement: FWBLANK-01
    verification:
      - kind: unit
        ref: "tests/test_write_blank_guard_pinning.py#test_every_shipped_nor_unlock_row_resolves_erase_capable"
        status: pass
    human_judgment: false
  - id: D5
    description: "The decision to close CR-01 inside Phase 205, with its displaced alternative, behaviour delta, provenance and four reversibility ratings, is recorded in the phase record."
    requirement: FWBLANK-01
    verification: []
    human_judgment: true
    rationale: "A decision record's completeness and clarity for a future reader is a judgment call, not something an automated check proves."

duration: 55min
completed: 2026-09-22
status: complete
---

# Phase 205 Plan 08: The write guard's erase exemption becomes address-aware for protocol 0x06 Summary

**Closed CR-01: `write_blank_guard.is_erase_exempt`/`requires_blank_check` now take the write's own resolved start address, withdrawing the erase exemption for protocol 0x06 (NOR-unlock) at any non-zero address, with a 13-test regression matrix and a recorded decision that this landed inside Phase 205 rather than being deferred.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-09-22T20:46:00Z
- **Completed:** 2026-09-22T21:41:00Z
- **Tasks:** 3
- **Files modified:** 4 in `firestarter_app`, 1 created in the meta repo

## Accomplishments
- `is_erase_exempt`/`requires_blank_check` gained a keyword-only `address: int = 0` parameter; on protocol `0x06` a non-zero address withdraws the exemption, falling back to the existing region-scoped host blank-check read rather than refusing outright.
- `write_eprom` resolves its own start address once (`parse_address`, `None`/`ValueError` both yielding `0`) and threads it into the guard call.
- 13 new tests (1 tracer + 12 regression-matrix) plus a live-database census pin the address dimension against hand-built dicts, real `resolve_chip` dicts, and every shipped protocol-`0x06` row.
- `205-CR-01-DECISION.md` records the decision, the displaced deferral alternative, the behaviour delta, the regression's provenance (commit `1cf1b22`), and the four design decisions' reversibility ratings.
- No firmware file, wire field, flag bit, or `--help` text changed.

## Task Commits

Each task was committed atomically:

1. **Task 1: End to end — a non-zero-address protocol-0x06 write pays the guard read** — `d78404d` (feat, inside `firestarter_app`)
2. **Task 2: The regression matrix WR-02 asked for — the address dimension, pinned** — `2756ef0` (test, inside `firestarter_app`)
3. **Task 3: Record the decision in the phase record, and advance the gitlink** — `e16f3adc` (docs, meta repo) then `61f96fcf` (chore, meta repo — gitlink advance)

**Submodule (`firestarter_app`) final commit:** `2756ef005b0db5ba7146c9d6f38a73cba66ee2ed`
**Meta repo final commit:** `61f96fcf` — `chore(205-08): advance firestarter_app gitlink to 2756ef0`

_Note: task 3 makes no commit inside `firestarter_app`; its two commits are both in the meta repo._

## Files Created/Modified
- `firestarter_app/firestarter/write_blank_guard.py` — `NOR_UNLOCK_PROTOCOL_ID` constant; `is_erase_exempt`/`requires_blank_check` gain the keyword-only `address` parameter.
- `firestarter_app/firestarter/eprom_operations.py` — `write_eprom` resolves `guard_address` from `address_str` and threads it into the guard call.
- `firestarter_app/tests/test_write_blank_guard.py` — the tracer's proof plus 8 of the 12 regression-matrix legs, and the `_sst39sf020_data()`/`_am28f256_data()` helpers.
- `firestarter_app/tests/test_write_blank_guard_pinning.py` — 4 remaining regression-matrix legs plus the live-database census leg.
- `.planning/phases/205-the-pre-flights-leave-the-firmware/205-CR-01-DECISION.md` — the decision record (new file).

## Decisions Made
- **D-G1** (predicate location): the address parameter lives on `is_erase_exempt` itself, not only its caller, because that function is the one making the false claim about erase scope.
- **D-G2** (check, not refuse): a withdrawn exemption falls back to the existing region-scoped blank-check read. The rejected alternative — refusing the write outright — would have been a `one-way` user-facing contract change on 190 shipped chip models; declined and recorded as such.
- **D-G3** (no sector-size model): any non-zero address withdraws the exemption conservatively; no attempt to narrow to "inside the erased sector" since the database carries no sector-size field.
- **D-G4** (malformed-address handling): an absent or unparseable `-a` resolves to address `0`, preserving `_setup_operation`'s existing `parse_address`/`ValueError` error contract rather than opening a port to produce a transport-failure verdict.
- **CR-01 closed in-phase, not deferred**: recorded in `205-CR-01-DECISION.md` § 2 — the displaced alternative (D-04's accepted-risk-window shape) was declined because CR-01's regression (silent, irreversible overwrite on 190/190 shipped rows, no operator flag required) is not the same shape as D-04's (a recoverable version skew behind an explicit `-b` flag).

## Deviations from Plan

None — plan executed exactly as written. One out-of-scope, pre-existing condition is worth recording so it is not mistaken for something this plan left behind:

**Pre-existing untracked file inside the `firestarter_app` submodule.** `datasheets/LST62832I.pdf` (dated 2026-09-19, three days before this plan's execution) was present, untracked, in the submodule working tree before task 1 began — confirmed by its mtime and by the first `git status --porcelain` run in this session, before any edit. Because it is untracked, `git status --porcelain -- firestarter_app` in the meta repo reports `firestarter_app` as modified ("untracked content") even after both submodule commits and the gitlink advance land cleanly. This is out of scope per the deviation rules' scope boundary (pre-existing, unrelated to CR-01) — it was neither committed nor deleted. The substantive parts of task 3's verify (byte-identical `205-CONTEXT.md`/`205-VERIFICATION.md`/`205-REVIEW.md`/every `205-0N-SUMMARY.md`, the meta gitlink SHA matching the submodule HEAD SHA exactly, and the two meta commits landing in the stated order) all pass; only the literal `git status --porcelain` emptiness check is affected, by content this plan did not introduce.

## Issues Encountered
None.

## RED Observations (verbatim, per `<verification>`)

**Task 1 — the tracer's own RED, against the pre-edit tree** (`test_write_at_a_non_zero_address_on_an_erase_capable_nor_unlock_part_pays_a_guard_read`):

```
F                                                                        [100%]
=================================== FAILURES ===================================
_ test_write_at_a_non_zero_address_on_an_erase_capable_nor_unlock_part_pays_a_guard_read _

    ...
    assert ok is True
>       assert opened == [COMMAND_READ, COMMAND_WRITE]
E       assert [2] == [1, 2]
E
E         At index 0 diff: 2 != 1
E         Right contains one more item: 2
E         Use -v to get more diff

tests/test_write_blank_guard.py:477: AssertionError
=========================== short test summary info ============================
FAILED tests/test_write_blank_guard.py::test_write_at_a_non_zero_address_on_an_erase_capable_nor_unlock_part_pays_a_guard_read
1 failed in 0.64s
```

**Task 2 — the sensitivity check, protocol branch temporarily reverted** (`if algorithm == NOR_UNLOCK_PROTOCOL_ID and address != 0:` replaced with `if False:`):

```
F.                                                                       [100%]
=================================== FAILURES ===================================
______ test_is_erase_exempt_is_false_for_nor_unlock_at_a_non_zero_address ______

    d = {"algorithm": NOR_UNLOCK_PROTOCOL_ID, "flags": 2}
>       assert is_erase_exempt(d, 0, address=0x10000) is False
E       AssertionError: assert True is False
E        +  where True = is_erase_exempt({'algorithm': 6, 'flags': 2}, 0, address=65536)

tests/test_write_blank_guard.py:178: AssertionError
=========================== short test summary info ============================
FAILED tests/test_write_blank_guard.py::test_is_erase_exempt_is_false_for_nor_unlock_at_a_non_zero_address
1 failed, 1 passed, 43 deselected in 0.58s
```

The headline leg (`test_is_erase_exempt_is_false_for_nor_unlock_at_a_non_zero_address`) reddened; the address-0 control (`test_write_at_address_zero_on_an_erase_capable_nor_unlock_part_still_pays_no_guard_read`) stayed green (the `.` in `F.`). The revert was undone (`git diff firestarter/write_blank_guard.py` confirmed byte-identical to the task-1 committed state) before task 2's commit.

## Final Pass Counts

- `tests/test_write_blank_guard.py` + `tests/test_write_blank_guard_pinning.py`: **69 passed** (measured baseline 55 → 56 after task 1 → 69 after task 2).
- `-k "nor_unlock"` selector: **8 passed** (matches the plan's stated expectation exactly).
- Whole host suite (`pytest tests/ -k "not no_programmer_found"`): **2331 passed, 2 deselected** (measured baseline 2317 → 2318 after task 1 → 2331 after task 2).
- `ruff check`/`ruff format --check` over `firestarter/` and `tests/`: clean at every commit.
- `firestarter_fw`: `git status --porcelain` empty throughout — no firmware file touched.

## `dev test` Partial-Write Expectation (flagged assumption, confirmed)

The plan's `<flagged_assumptions>` named an unmeasured expectation: that `chip_test.py:3237-3245`'s `write_eprom` call, which passes `address_str=_address_arg(region_start)` for every write (not just partial writes), would gain one guard read on a protocol-`0x06` part at a non-zero `region_start`. **Confirmed, not disproved**, by direct code read during task 2's `<read_first>`: the call site is unconditional for `OP_WRITE`/`OP_WRITE_PARTIAL` alike, region_start becomes `guard_address` inside `write_eprom` exactly as task 1 implements, and a grep across `tests/` during planning and again during task 2 found no existing test driving a protocol-`0x06` write through `chip_test.py` (`wire_dict_baseline.json`'s `algorithm: 6` entries are golden wire-dict snapshots, unaffected by a predicate change) — so this expectation was not measured against a live test in this plan, but the code path it describes is confirmed to exist exactly as flagged, and the whole-suite green run (2331 passed) confirms no test collateral broke.

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness
FWBLANK-01's substance is now complete: the one gap `205-VERIFICATION.md` found (`gaps[0]`, truth 9) is closed, its regression matrix is pinned, and the decision to close it in-phase is recorded. Phase 206 (`dev test`/session-lease work) and Phase 207 (version bump + wiki) proceed unblocked by this gap. No blockers.

## Self-Check: PASSED

- `205-CR-01-DECISION.md` exists on disk: FOUND.
- `firestarter_app/firestarter/write_blank_guard.py` exists on disk: FOUND.
- Meta-repo SUMMARY commit `826aebc4` present in `git log --oneline --all`: FOUND.
- Submodule task 1 commit `d78404d` present in `git log --oneline --all`: FOUND.
- Submodule task 2 commit `2756ef0` present in `git log --oneline --all`: FOUND.

---
*Phase: 205-the-pre-flights-leave-the-firmware*
*Completed: 2026-09-22*
