---
phase: 129-flash-path-decision-pcb-requirements-record
plan: 07
subsystem: firmware
tags: [linker-script, py32f071, arm-toolchain, cmake, byte-identity, gate-fix]

requires:
  - phase: 129-flash-path-decision-pcb-requirements-record
    provides: "129-06's firmware subset record (FLASH-PATH-AND-PCB.md) and both docstring-cited records this comment now cross-references"
provides:
  - "BOOTLOADER linker comment names both flash-path record layers and no longer carries the false 'no VTOR' clause"
  - "Locator-only fix to test_linker_comment_cross_references_record, discharging a gate defect that dated to plan 129-02"
  - "D-13 byte-identity proof executed locally: two builds of the same tree/toolchain, identical .bin/.hex digests, confirmed relink"
affects: [129-08, 129-09, 130-close]

tech-stack:
  added: []
  patterns:
    - "Local ARM byte-identity delta proof (cmake --build twice, sha256sum before/after, diff must be empty) -- reusable for any future comment-only linker edit"

key-files:
  created: []
  modified:
    - firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld
    - firestarter/tests/test_flash_path_record_sync.py

key-decisions:
  - "Discovered test_linker_comment_cross_references_record's brace-detection loop required 'MEMORY' and '{' on the same source line, which the linker script's standard two-line GNU ld MEMORY-block opening never satisfies -- the leg was unreachable since it was authored in 129-02, independent of any comment content."
  - "Escalated rather than unilaterally editing the frozen test or restructuring the MEMORY block; operator authorized a narrow locator-only fix to the test, gated on a RED-preserving proof sequence executed before trusting the fix."
  - "D-13's byte-identity proof executed locally (no CI, no push): before/after .bin and .hex SHA-256 digests identical, arm-none-eabi-size row identical, incremental rebuild's [1/1] Linking line confirms LINK_DEPENDS forced a real relink rather than a no-op."

patterns-established:
  - "Escalate-then-fix-with-proof for a frozen-gate bug: revert the substantive edit, apply the locator fix alone, confirm the leg still fails on content (not on 'could not locate'), then restore the edit and confirm green -- proves the fix widened locating ability only, not what is judged."

requirements-completed: []

coverage:
  - id: D1
    description: "BOOTLOADER linker comment cites both flash-path record layers (D-11) and drops the corrected false clause (C-1)"
    requirement: "PCB-03"
    verification:
      - kind: unit
        ref: "tests/test_flash_path_record_sync.py::TestFlashPathRecordSync::test_linker_comment_cross_references_record"
        status: pass
      - kind: unit
        ref: "tests/test_py32_flash_map.py + tests/test_flash_geometry_recorded_before_linker.py (28 tests)"
        status: pass
    human_judgment: false
  - id: D2
    description: "D-13 byte-identity proof: comment-only linker edit changes no emitted byte, confirmed by a real relink"
    verification:
      - kind: other
        ref: "local sha256sum before/after comparison, /tmp/firestarter-py32f071-d13/{before,after}.txt, diff exit 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "Locator-only fix to a frozen gate test's unreachable brace-detection assertion, authorized by the operator with a RED-preserving proof sequence"
    verification:
      - kind: other
        ref: "manual proof sequence: revert linker edit -> single leg fails on needle-miss (not 'could not locate') -> restore edit -> single leg passes"
        status: pass
    human_judgment: false

duration: 18min
completed: 2026-08-02
status: complete
---

# Phase 129 Plan 07: Linker BOOTLOADER Comment Cross-Reference and D-13 Byte-Identity Proof Summary

**Comment-only linker edit closes D-11's cross-reference and corrects C-1's false "no VTOR" clause; a genuine defect in the frozen gate test (unreachable since plan 129-02) was found, escalated, and fixed under an operator-mandated RED-preserving proof, rather than worked around.**

## Performance

- **Duration:** ~18 min
- **Completed:** 2026-08-02T12:15:51Z
- **Tasks:** 3 (Task 1 toolchain/baseline build, Task 2 comment edit, Task 3 byte-identity proof + commit) plus one operator-authorized deviation (test locator fix)
- **Files modified:** 2 (`firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld`, `firestarter/tests/test_flash_path_record_sync.py`)

## Accomplishments

- The `BOOTLOADER` region's preceding comment block now names both record layers it always instructed a future reader to consult (`platform/py32f071/FLASH-PATH-AND-PCB.md` §"Flash budget, as actually reserved" and, in the Firestarter meta-repo, `.planning/v1.23-FLASH-PATH-DECISION.md`), states the corrected fleet-migration cost, and no longer carries the false "on a part with no VTOR" clause.
- D-13's local byte-identity proof executed successfully: two builds of the same tree with the same toolchain produced identical `.bin`/`.hex` SHA-256 digests and an identical `arm-none-eabi-size` row, with the incremental rebuild's `[1/1] Linking` line confirming `LINK_DEPENDS` forced a real relink (not a vacuous no-op).
- A genuine, pre-existing defect in `tests/test_flash_path_record_sync.py::TestFlashPathRecordSync::test_linker_comment_cross_references_record` was found (its brace-detection loop could never locate the `MEMORY` block's opening brace against this file's real two-line `MEMORY`/`{` structure), escalated to the operator rather than worked around, and fixed under an explicit RED-preserving proof.

## Task Commits

1. **Task 1: Toolchain preflight and the baseline build** — no commit (no files written inside either repository; build-only, evidence captured to the scratch directory).
2. **Task 2: Replace the BOOTLOADER comment block** — folded into the Task 3 commit below (the plan's own flow: verify, then commit once).
3. **Locator fix (operator-authorized deviation)** — `2ef7b57` (`fix(129-07): locate the MEMORY block brace across lines in the linker cross-reference gate`)
4. **Task 3: The D-11 comment edit** — `5a89ee7` (`docs(129-07): linker BOOTLOADER comment cites the flash-path record and drops the corrected clause`)

**Plan metadata:** this SUMMARY's own meta-repo commit (created immediately after this file).

## Files Created/Modified

- `firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld` — the `BOOTLOADER` region's preceding comment block replaced: adds the cross-reference to both record layers, restates the migration-vs-resize instruction, states the corrected fleet-re-flash cost with its attribution (`__VTOR_PRESENT` / `SCB->VTOR`), and drops the false "no VTOR" clause. No `MEMORY`/`FLASH`/`CONFIG`/`RAM` region line, `PROVIDE`, `ASSERT`, or symbol changed.
- `firestarter/tests/test_flash_path_record_sync.py` — `test_linker_comment_cross_references_record`'s brace-detection loop changed from a same-line `"MEMORY" in line and "{" in line` check to an exact-match `MEMORY` line followed by the first exact-match `{` line. No needle set, forbidden-clause regex, or non-vacuity span judgment changed.

## Decisions Made

- **Escalate, don't unilaterally fix the frozen test.** When `test_linker_comment_cross_references_record` failed with `brace_idx is None` regardless of the comment edit's content, I verified the same failure occurred against the pre-edit `git HEAD` content too (confirming the defect was independent of my edit and pre-existing since 129-02), then stopped and reported rather than editing the frozen test file or restructuring the `MEMORY` block (both were explicitly out of scope). The operator authorized a narrow, locator-only fix.
- **RED-preserving proof before trusting the fix.** Per the operator's mandatory sequence: reverted the linker script to its committed HEAD content, applied the locator fix alone, confirmed the single leg still failed — on a needle-miss (`missing: ['FLASH-PATH-AND-PCB.md', 'v1.23-FLASH-PATH-DECISION.md', '__VTOR_PRESENT', 'SCB->VTOR']`), not the former "could not locate" message — then restored the D-11 comment edit and confirmed the same leg passed. This proves the locator fix only widened the gate's ability to *find* the span; it did not weaken what the gate *judges*.
- **Two separate commits**, as instructed: the locator fix (test file only) landed first, the D-11 comment edit (linker script only) landed second — kept as distinct concerns with distinct rationale.
- **D-13 was not re-run after the test fix** — the byte-identity proof (captured before the deviation was discovered) remains valid evidence, unaffected by a test-locator change; its digests are transcribed below unchanged.

## Toolchain and Build Evidence (D-13)

**Toolchain versions (already present in this devcontainer — no install needed):**
- `arm-none-eabi-gcc (15:14.2.rel1-1) 14.2.1 20241119`
- `GNU size (2.44-3+23+b1) 2.44`
- `cmake version 4.4.0`
- `ninja 1.13.0.git.kitware.jobserver-pipe-1`

**Scratch build directory:** `/tmp/firestarter-py32f071-d13` (outside both repository working trees; left in place for `129-09`'s transcription — see "Next Phase Readiness" below).

**Resolved SDK commit:** `0ed2f4b4d3391eccfd4491006a30295fd78e32c2` (matches the pinned `GIT_TAG`).

**`before.txt`** (baseline build, HEAD `8102d0f`, before any edit):
```
66b6a8dca982d6c6a6fb8bf19a99a0b9197b261950be1f118f1677753c5b495e  /tmp/firestarter-py32f071-d13/firestarter_py32f071.bin
9599a625b1bc7357ec512952f76ee27c6897fabd1c7a1eb4645068c1935913dc  /tmp/firestarter-py32f071-d13/firestarter_py32f071.hex
   text	   data	    bss	    dec	    hex	filename
  27260	    112	   5888	  33260	   81ec	/tmp/firestarter-py32f071-d13/firestarter_py32f071.elf
```
`before-build.log` contains `[42/42] Linking CXX executable firestarter_py32f071.elf`. 42/42 objects built, exit 0.

**`after.txt`** (incremental rebuild after the comment-only linker edit, no reconfigure):
```
66b6a8dca982d6c6a6fb8bf19a99a0b9197b261950be1f118f1677753c5b495e  /tmp/firestarter-py32f071-d13/firestarter_py32f071.bin
9599a625b1bc7357ec512952f76ee27c6897fabd1c7a1eb4645068c1935913dc  /tmp/firestarter-py32f071-d13/firestarter_py32f071.hex
   text	   data	    bss	    dec	    hex	filename
  27260	    112	   5888	  33260	   81ec	/tmp/firestarter-py32f071-d13/firestarter_py32f071.elf
```
`after-build.log` contains `[1/1] Linking CXX executable firestarter_py32f071.elf` — **zero objects recompiled**, confirming `LINK_DEPENDS` forced a real relink (the only work was the link step and the objcopy steps that depend on it), not a vacuous no-op.

`diff before.txt after.txt` → empty, exit 0. **Byte-identical.**

**The two honesty ceilings, restated:** (a) these are delta-comparable figures only (same local tree, same local toolchain, two builds) and must never be set beside a CI figure — the local GCC differs from CI's and produces different absolute sizes for identical source. (b) A byte-identical image proves the emitted output is unchanged; it proves nothing about whether the image runs, and no PY32F071 hardware exists on which to find out.

## Deviations from Plan

### Auto-fixed / Escalated Issues

**1. [Rule 4 — escalated, operator-authorized] Locator-only fix to a frozen gate test's unreachable assertion**
- **Found during:** Task 3 (running the gate leg after Task 2's comment edit).
- **Issue:** `test_linker_comment_cross_references_record`'s brace-detection loop (`if brace_idx is None and "MEMORY" in line and "{" in line`) required `"MEMORY"` and `"{"` to co-occur on a single source line. The linker script has always opened its `MEMORY` block as GNU ld's own two-line convention (`MEMORY` then `{` on the next line), so `brace_idx` was permanently `None` — the leg was unreachable since it was authored in plan 129-02, independent of any comment-edit content. Verified by running the identical detection logic against `git show HEAD:...` (pre-129-07 content): `brace_idx` was `None` there too.
- **Escalation:** stopped and reported to the orchestrator per hard constraint #3 ("the gate is frozen; if a leg looks wrong, STOP and report") rather than editing the test unilaterally or restructuring the `MEMORY` block (both out of this plan's scope).
- **Resolution:** operator reviewed, independently confirmed the diagnosis, and authorized a narrow locator-only fix: find the exact-match `"MEMORY"` line, then the first exact-match `"{"` line that follows it. No needle set (`_LINKER_NEEDLES`), forbidden-clause regex (`_LINKER_FORBIDDEN_RE`), or non-vacuity span judgment (`_assert_non_vacuous` call/span) was touched.
- **Mandatory RED-preserving proof executed, per the operator's condition:**
  - Step 1: Task 2's edited linker script was saved to `/tmp/firestarter-py32f071-d13/PY32F071xB_FLASH.ld.task2-edit`, then `git checkout --` reverted the working file to committed HEAD content.
  - Step 2: the locator fix was applied to the test.
  - Step 3: single leg re-run against the **unedited** linker script — result: **FAILED**, verbatim:
    ```
    AssertionError: linker script missing needles: ['FLASH-PATH-AND-PCB.md', 'v1.23-FLASH-PATH-DECISION.md', '__VTOR_PRESENT', 'SCB->VTOR']
    ```
    This is a needle-miss failure, **not** the former "could not locate the MEMORY block opening brace" failure — proof the locator fix did not manufacture a false pass.
  - Step 4: Task 2's comment edit was restored from the saved copy.
  - Step 5: single leg re-run — result: **PASSED** (`1 passed`), verbatim: `PASSED tests/test_flash_path_record_sync.py::TestFlashPathRecordSync::test_linker_comment_cross_references_record`.
  - Step 6: full suite re-run — result: **`1 failed, 220 passed`**, the one remaining failure being `test_seed_status_is_no_longer_dormant` (owned by 129-08), exactly the state the plan targeted before the gate defect was found.
- **Files modified:** `firestarter/tests/test_flash_path_record_sync.py`.
- **Committed in:** `2ef7b57` (locator fix, test file only) — landed before `5a89ee7` (the D-11 comment edit, linker script only), as two distinct commits per the operator's instruction.

---

**Total deviations:** 1 escalated-and-authorized (Rule 4). No scope creep: the fix was strictly locator-only, verified not to weaken the gate, and proven via an explicit RED/GREEN sequence before being trusted.
**Impact on plan:** without this fix, the plan's own success criterion ("one gate leg discharged; exactly one remains" / full suite `1 failed, 220 passed`) would have been unreachable, and this plan would have had to report `2 failed, 219 passed` (the linker leg permanently red through no fault of the comment content). With the fix, the end state matches the plan's original target exactly.

## Issues Encountered

None beyond the gate defect documented above.

## Next Phase Readiness

- The scratch build directory `/tmp/firestarter-py32f071-d13` was **left in place** (not removed) with `before.txt`, `after.txt`, `before-build.log`, `after-build.log`, `configure.log`, and the saved intermediate `PY32F071xB_FLASH.ld.task2-edit`, for `129-09` to transcribe into `129-NONREGRESSION.md`.
- Firmware working tree is clean (`git status --porcelain` empty) at HEAD `5a89ee7`, on branch `v1.23-py32f071-integration`.
- `python -m pytest tests/ -q` → `1 failed, 220 passed`. The sole remaining failure is `test_seed_status_is_no_longer_dormant`, owned by plan 129-08 — left RED intentionally, as instructed.
- No requirement was ticked (`PCB-03` remains open for `129-09` alone to close). `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, and `.planning/STATE.md` were not touched. The meta gitlink was not bumped. No `git push`, no `gh workflow run` — verified by session transcript (only `git`, `cmake`, `ninja`, `sha256sum`, `arm-none-eabi-size`, `python -m pytest`, `diff`, `cp` and `grep`/`ls`/`cat` were invoked).

---
*Phase: 129-flash-path-decision-pcb-requirements-record*
*Completed: 2026-08-02*

## Self-Check: PASSED

- FOUND: `.planning/phases/129-flash-path-decision-pcb-requirements-record/129-07-SUMMARY.md`
- FOUND: firmware commit `2ef7b57` (locator fix)
- FOUND: firmware commit `5a89ee7` (D-11 comment edit)
- Firmware working tree clean at HEAD `5a89ee7` on branch `v1.23-py32f071-integration`
- Meta repo shows only ` M firestarter` (gitlink deliberately unbumped) and ` M firestarter_app` (pre-existing, unrelated) after this SUMMARY's own commit
