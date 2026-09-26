---
phase: 127-host-dfu-installer
plan: 10
subsystem: docs
tags: [documentation, dfu, py32f071, flash-map, pyusb, parity-gate]

# Dependency graph
requires:
  - phase: 127-05
    provides: "APP_REGION_SIZE / APP_REGION_END / CONFIG_REGION_SIZE constants in firestarter/py32_dfu.py; _check_envelope bounded on APP_REGION_END (0x0801E000)"
  - phase: 127-09
    provides: "VerifyResult enum, _read_back()/_verify_readback(), the download -> readback -> _finish() sequence, and firmware.py's 'written but NOT verified' completion line"
  - phase: 127-02
    provides: "the [py32] extra's pyusb>=1.3.1,<2 floor in pyproject.toml"
provides:
  - "doc/PY32F071-FIRMWARE-INSTALL.md corrected for the three facts this phase changed: the reserved 120K/8K flash map, the readback-verification step and its three non-VERIFIED outcomes, and the raised pyusb floor"
  - "tests/test_py32_packaging.py: a third gate family (documentation parity) holding the doc's flash-map figures against py32_dfu.APP_REGION_END/FLASH_BASE, the three readback-outcome strings, and the pyusb floor, with a fail-closed RED demonstration"
affects: [127-12, 129, 130-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Doc-vs-constant parity built from f\"0x{py32_dfu.APP_REGION_END:08X}\" / f\"0x{py32_dfu.FLASH_BASE:08X}\" rather than literals, so a future map move (Phase 129) turns the gate red instead of leaving the doc stale -- same shape as 127-05's cross-repo linker-script gate"
    - "Scoped doc edits confined to three named regions (§1 Dependencies, §3, §5 item 2), verified by an exact heading-list md5 comparison against a pinned pre-edit blob rather than a HEAD~1-relative diff"

key-files:
  created: []
  modified:
    - firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md
    - firestarter_app/tests/test_py32_packaging.py

key-decisions:
  - "The three non-VERIFIED outcome phrases (bitCanUpload, 'load address not under host control', 'written but NOT verified') were written on single un-wrapped lines in the doc's new §3 step 7 -- an early draft split 'load address not under host\\ncontrol' across a markdown line-wrap, which silently broke the exact-phrase grep the plan's own verify block and Task 2's parity gate both depend on. Caught by re-running the plan's automated verify block before committing."
  - "§3's closing sentence ('Every step above is asserted in tests/test_py32_dfu.py against a fake USB device...') was left untouched rather than edited, per the plan's instruction to update it only if it stopped reading true -- the new step 7 is in fact asserted in that same file's TestReadbackVerification class (added by 127-09), so the sentence remains accurate without modification."
  - "The libusb/WinUSB paragraph and the self-flash-seed pointer were left byte-identical (verified via md5 against the pinned pre-edit blob 556fd18859df0bc8e5aa0dacba51132c5599126b) -- the pyusb floor sentence was inserted before that paragraph, not inside it."
  - "No section heading was added, removed, or renamed -- the doc's ^##-and-deeper heading list is byte-identical (md5 5d90f081b03aa702bf81b191cded4aa8, 10 headings) to the pinned pre-edit blob."
  - "The 'unverified against silicon' status header still occurs exactly once (line 7) -- no staleness header was added, and the new readback prose uses 'never run against a PY32F071' / 'asserted only against a fake USB device' instead of repeating the header's exact wording, per the plan's explicit instruction."
  - "The parity gate was added to tests/test_py32_packaging.py (the phase's existing textual-gates module) rather than a fourth scanning module, per the plan's instruction -- module docstring updated to record all three gate families (packaging, D-17 record, documentation parity) living together."
  - "No requirement checkbox in .planning/REQUIREMENTS.md was ticked by this plan -- HOST-01..HOST-08 confirmed still all '[ ] Pending' after the final commit. Only Plan 127-12 may tick them."

requirements-completed: []  # HOST-07 and HOST-03 intentionally left unticked -- this plan documents facts Plans 127-02/127-05/127-09 built; it does not discharge either requirement. Only Plan 127-12 may tick HOST-01..HOST-08.

coverage:
  - id: D1
    description: "§3 step 5 corrected from the superseded 0x08000000-0x08020000 (128 KiB) window to the actual application-region end (0x0801E000), explaining the reserved 8 KiB config region above it and the non-overridable refusal"
    requirement: "HOST-03"
    verification:
      - kind: unit
        ref: "grep -c '0x0801E000' doc/PY32F071-FIRMWARE-INSTALL.md >= 1; grep -c '0x08020000' == 0 (pre-edit value 1)"
        status: pass
      - kind: unit
        ref: "tests/test_py32_packaging.py::test_install_doc_app_region_end_matches_host_constant"
        status: pass
    human_judgment: false
  - id: D2
    description: "§3 gains a new step 7 documenting the DFU_UPLOAD readback-before-leave-DFU-mode sequence and all three non-VERIFIED outcomes (bitCanUpload=0, plain-DFU-1.1 load-address-not-under-host-control, and the hard-failing byte mismatch), stated as asserted only against a mock"
    requirement: "HOST-03"
    verification:
      - kind: unit
        ref: "grep -c 'DFU_UPLOAD|bitCanUpload|load address not under host control|written but NOT verified' doc/PY32F071-FIRMWARE-INSTALL.md, each >= 1"
        status: pass
      - kind: unit
        ref: "tests/test_py32_packaging.py::test_install_doc_documents_all_three_readback_outcomes"
        status: pass
    human_judgment: false
  - id: D3
    description: "§5 item 2 distinguishes the now-automated DfuSe verification path from the still-manual plain-DFU path; §1 Dependencies records the pyusb>=1.3.1,<2 floor and the reason for the upper bound"
    requirement: "HOST-07"
    verification:
      - kind: unit
        ref: "grep -c 'pyusb>=1.3.1,<2' doc/PY32F071-FIRMWARE-INSTALL.md >= 1"
        status: pass
      - kind: unit
        ref: "tests/test_py32_packaging.py::test_install_doc_pyusb_floor_matches_pyproject"
        status: pass
    human_judgment: false
  - id: D4
    description: "Scope discipline: no section heading added/removed/renamed (byte-identical heading list vs the pinned pre-edit blob), the libusb/WinUSB paragraph and self-flash-seed pointer byte-identical, no staleness header added, and the diff confined to §1 Dependencies/§3/§5 item 2"
    verification:
      - kind: unit
        ref: "plan's automated verify block: HEADINGS_IDENTICAL_OK, WINUSB_PARA_IDENTICAL_OK, STALENESS_HEADER_OK pre=1 post=1"
        status: pass
      - kind: other
        ref: "git diff --stat doc/PY32F071-FIRMWARE-INSTALL.md -- 1 file changed, 32 insertions(+), 6 deletions(-), confined to the three permitted regions"
        status: pass
    human_judgment: false
  - id: D5
    description: "Parity gate: doc figures built from py32_dfu.APP_REGION_END/FLASH_BASE (never literals) plus a fail-closed RED demonstration against a planted tmp_path file"
    requirement: "HOST-03"
    verification:
      - kind: unit
        ref: "tests/test_py32_packaging.py -- 12 passed (6 pre-existing + 6 new), including test_install_doc_address_parity_fails_closed_on_a_planted_file_missing_the_address"
        status: pass
    human_judgment: false
  - id: D6
    description: "Full app suite green with 0 skipped; ruff check/format clean; skip census unchanged at 5; mypy watermark unaffected"
    verification:
      - kind: unit
        ref: "pytest tests/ -q --no-cov -> 1293 passed, 0 failed, 0 skipped (1287 baseline + 6 new)"
        status: pass
      - kind: unit
        ref: "ruff check firestarter/ tests/ (clean); ruff format --check firestarter/ tests/ (114 files, clean); pytest tests/test_skip_census.py -q (5 passed); python tools/check_mypy_watermark.py (1 error vs watermark 35, passes)"
        status: pass
    human_judgment: false
  - id: D7
    description: "No requirement checkbox ticked in REQUIREMENTS.md; /workspaces/firestarter left untouched"
    verification: []
    human_judgment: true
    rationale: "Absence of a tick or an external write cannot be proven by a unit test; confirmed by re-grepping REQUIREMENTS.md's HOST-01..HOST-08 rows (still all '[ ] Pending') and git -C /workspaces/firestarter status --porcelain returning empty both before and after this plan's execution."

# Metrics
duration: ~35min
completed: 2026-08-01
status: complete
---

# Phase 127 Plan 10: Doc Corrections + Parity Gate Summary

**`doc/PY32F071-FIRMWARE-INSTALL.md` now states the real 120 KiB flash-write bound (`0x0801E000`), documents the `DFU_UPLOAD` readback and its three non-verified outcomes in the operator's own words, and records the raised `pyusb` floor — held in place by a new parity-gate family in `tests/test_py32_packaging.py` that fails closed the moment the doc's figures and the host constants disagree.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-08-01 (following STATE.md's Plan 09 completion)
- **Completed:** 2026-08-01
- **Tasks:** 2/2 executed
- **Files modified:** 2 (1 doc, 1 test)

## Accomplishments

- **Task 1 (`a195065`):** Made exactly three scoped edits to `doc/PY32F071-FIRMWARE-INSTALL.md`. (a) §3 step 5's superseded `0x08000000`–`0x08020000` (128 KiB) window replaced with the real application-region end `0x0801E000`, explaining the reserved 8 KiB config region above it and that the refusal is deliberately non-overridable (no force flag). (b) A new §3 step 7 documents the `DFU_UPLOAD` readback that runs before the device is told to leave DFU mode, naming all three non-`VERIFIED` outcomes in operator language: `bitCanUpload = 0` → "written but NOT verified"; plain DFU 1.1 → "load address not under host control" → "written but NOT verified"; a byte mismatch (or short read) → a hard, non-zero-exit failure naming the first differing offset, with the device never told to leave DFU mode. States plainly this sequence is asserted only against a fake USB device and has never run against a PY32F071. §5 item 2 updated to say the DfuSe path is now automated while the plain-DFU path still requires manual verification. (c) §1 Dependencies gained one sentence recording the `pyusb>=1.3.1,<2` floor and why the upper bound exists (a future pyusb major could reorder `ctrl_transfer`'s positional parameters). Nothing else changed: the diff is confined to those three regions, no section heading was added/removed, the libusb/WinUSB paragraph and self-flash-seed pointer are byte-identical to the pinned pre-edit blob, and the "unverified against silicon" status header still occurs exactly once.
- **Task 2 (`84cdd86`):** Added a documentation-parity gate family to `tests/test_py32_packaging.py`: `_INSTALL_DOC` + a non-vacuity-checked `_read_install_doc()` helper, then six tests — non-vacuity, the doc's application-region-end figure built from `f"0x{py32_dfu.APP_REGION_END:08X}"`, the flash-base figure built from `f"0x{py32_dfu.FLASH_BASE:08X}"`, all three readback-outcome phrases present, the `[py32]` extra's requirement string present in the doc, and a fail-closed RED demonstration against a planted `tmp_path` file. Module docstring updated to record all three gate families (packaging, D-17 record, documentation parity) and why they live together in one module.

## Task Commits

1. **Task 1: Three scoped corrections — the reserved map, the readback step, the raised floor** — `a195065` (docs)
2. **Task 2: A parity gate so the doc's flash-map figure cannot outlive the constant** — `84cdd86` (test)

**Meta-repo tracking commit:** pending (this SUMMARY + gitlink bump, committed next per `<final_commit>`)

Both commits are on `firestarter_app`'s `v1.23-py32f071-integration` branch.

## Files Created/Modified

- `firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md` — flash-map figure corrected, readback-verification step added, pyusb floor recorded
- `firestarter_app/tests/test_py32_packaging.py` — documentation-parity gate family (6 new tests), module docstring updated

## Decisions Made

See `key-decisions` in the frontmatter for the full list. The most load-bearing: an early draft wrote "load address not under host\ncontrol" across a markdown line-wrap inside a bold span, which silently defeated the plan's own exact-phrase `grep` check; caught before committing by re-running the plan's automated verify block, which returned no output on the first pass (a chain of `&&`-joined `test` commands with no visible failure) rather than a clear error — debugged by re-running each `test` individually to isolate the failing clause.

## Deviations from Plan

None (Rule 1/2/3 sense) — plan executed exactly as written, three scoped doc edits plus the parity gate. No scope creep: only the two files named in the plan's `files_modified` were touched. `/workspaces/firestarter` remains untouched (`git status --porcelain` verified empty before this plan's first read and after its last commit). No requirement checkbox in `.planning/REQUIREMENTS.md` was ticked — HOST-01..HOST-08 all still `[ ]` Pending. No task ran `git push`, `gh workflow run`, or any `git stash` subcommand.

## Issues Encountered

- The plan's Task 1 automated verify block (a long `&&`-joined chain of `test` assertions) initially produced no output at all on the first run after the doc edit, because the `load address not under host control` phrase was accidentally split across a markdown line-wrap inside a bold span — the `test ... -ge 1` clause failed silently and short-circuited the rest of the `&&` chain before any `echo` ran. Resolved by re-running each `test` clause individually to isolate the failing one, then rewriting the affected §3 step 7 bullet so all three outcome phrases sit on single, un-wrapped lines. Re-ran the full verify block afterward with the expected `STALENESS_HEADER_OK` / `HEADINGS_IDENTICAL_OK` / `WINUSB_PARA_IDENTICAL_OK` output.

## User Setup Required

None — no external service configuration required.

## Claim Ceiling

This plan edits operator-facing documentation and a source-scan test. It proves that the doc's flash-map figures and readback-outcome vocabulary match the host code, and that the doc and `pyproject.toml`'s pyusb floor agree. It proves nothing about a PY32F071 board — the doc explicitly states the readback sequence has never run against real silicon, consistent with the file's own "unverified against silicon" status header, and this plan neither asserts nor implies otherwise.

## Next Phase Readiness

- Full app suite: **1293 collected / 1293 passed / 0 failed / 0 skipped** (1287 baseline + 6 new). `ruff check`, `ruff format --check` (114 files) both clean. `tools/check_mypy_watermark.py`: 1 error vs watermark 35 (unaffected, passes). Skip census unchanged at 5 passed.
- `tests/test_py32_packaging.py` now collects 12 tests (6 pre-existing + 6 new), all passing.
- The parity gate is derived from `py32_dfu.APP_REGION_END`/`FLASH_BASE`, so when Phase 129 gives `BOOTLOADER` a non-zero length and moves the application's `ORIGIN`, this gate — plus 127-05's cross-repo linker-script gate — will turn red rather than leaving the doc silently stale.
- HOST-01..HOST-08 all remain `[ ]` Pending in `.planning/REQUIREMENTS.md` — unaffected by this plan, as instructed. Only Plan 127-12 may tick them.
- `/workspaces/firestarter` remains untouched (read-only input), confirmed clean before and after this plan's execution.
- Everything Phase 129 owns (the three-tier flash-path framing, `BOOTLOADER` sizing, VID/PID, BOOT0/nBOOT1 strapping, SWD pads, the socket-empty safety line, and the statement that landing DFU does not retire the self-flash seed) is exactly as Phase 129 will find it — none of it was touched.

## Self-Check: PASSED

- FOUND: `firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md` (modified)
- FOUND: `firestarter_app/tests/test_py32_packaging.py` (modified)
- FOUND: commit `a195065` in `firestarter_app` git log
- FOUND: commit `84cdd86` in `firestarter_app` git log
- FOUND: `.planning/phases/127-host-dfu-installer/127-10-SUMMARY.md`
