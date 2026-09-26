# Phase 194 — Deferred / Out-of-Scope Items

## D1 — `firestarter_fw` `pytest tests/` porcelain-comparison failures caused by an unrelated concurrent-session commit

**Found during:** 194-06, Task 1, firmware test verification.

**Symptom:** `pytest tests/` reports `17 failed, 284 passed` (301 total, matching the
pre-existing total test count) instead of the `301/301` this phase's earlier plans
(194-01, 194-02) measured on their own committed trees. All 17 failures are inside
`tests/test_flash_path_record_sync.py::TestFlashPathRecordSync`, and every one raises
`MissingScanTargetError: /workspaces/.planning/v1.23-FLASH-PATH-DECISION.md does not
exist, but the meta repo IS present`.

**Cause, verified:** a concurrent, unrelated Claude session running in this same
working tree committed meta-repo commit `b51d6b5b` ("refactor(planning): relocate 41
misplaced .planning root items into milestones/ and notes/"), which moved
`.planning/v1.23-FLASH-PATH-DECISION.md` to `.planning/milestones/v1.23-FLASH-PATH-DECISION.md`.
`test_flash_path_record_sync.py` hard-codes the pre-relocation path and fails closed
(by design — its own module docstring: "a missing scan target under a present repo
raises", not skips) the moment that path moves.

**Why out of scope for this plan:** `tests/test_flash_path_record_sync.py` is not in
194-06's `files_modified`, the relocation was performed by a different session with no
relationship to protocol `0x05` page-size correctness, and the failure is not caused by
any edit this plan made — confirmed by isolating the module: it fails identically
whether or not 194-06's own two firmware files (`src/json_parser.c`,
`include/firestarter.h`) are included in the diff. Per the executor's scope-boundary
rule, a failure in an unrelated file caused by unrelated concurrent work is logged, not
fixed, here.

**Verification that 194-06's own changes are unaffected:** `pio test -e native` and
`pio test -e native_nodevtools` both report `208/208 succeeded`, both AVR builds match
the pre-existing byte-for-byte flash figures (`uno` 21616/32256 B, `leonardo`
23734/28672 B), and the firmware planning-citation gate reports `OK: 177 files scanned,
no planning citations`. The only failing module is the one this item names.

**Disposition:** not fixed by 194-06. Whoever fixes the `.planning/v1.23-FLASH-PATH-DECISION.md`
path drift (updating `tests/test_flash_path_record_sync.py`'s hard-coded meta-repo path
to `.planning/milestones/v1.23-FLASH-PATH-DECISION.md`) should also confirm the sibling
`platform/py32f071/FLASH-PATH-AND-PCB.md` shared-section parity still holds against the
relocated file.
