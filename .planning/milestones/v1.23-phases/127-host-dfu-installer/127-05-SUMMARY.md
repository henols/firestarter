---
phase: 127-host-dfu-installer
plan: 05
subsystem: firmware-install
tags: [dfu, py32f071, flash-map, linker-script, cross-repo-gate, fail-closed]

# Dependency graph
requires:
  - phase: 127-01
    provides: "firestarter/py32_dfu.py, tests/test_py32_dfu.py landed on the milestone branch via the feature/py32f071-fw-install merge"
  - phase: 126
    provides: "platform/py32f071/linker/PY32F071xB_FLASH.ld with the FLASH/CONFIG/BOOTLOADER map (Phase 126 CFG-06)"
provides:
  - "APP_REGION_SIZE / APP_REGION_END / CONFIG_REGION_SIZE constants in firestarter/py32_dfu.py; FLASH_SIZE kept verbatim as the physical constant"
  - "_check_envelope bounded on APP_REGION_END (0x0801E000) instead of the 128 KiB physical part size"
  - "tests/test_py32_flash_map_host.py -- 16 tests: 8 local envelope-behaviour tests + 5 @requires_fw cross-repo linker-script parity tests + 3 fail-closed RED demonstrations"
affects: [127-08, 127-09, 127-12, 130-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "D-13/D-14 shape: split a physical-size constant from an application-region constant, derive the region END from BASE+SIZE (never re-typed), and hold the pair honest with a fail-closed cross-repo gate rather than a comment"
    - "Non-vacuity assertion runs BEFORE any value comparison (research A-7), with a failure message containing the literal phrase 'vacuously true'"
    - "_REGION_RE / _parse_regions copied byte-identical from the firmware repo's own test module, with a citing comment, so the two parsers cannot quietly diverge"
    - "Fail-closed RED demonstrations carry no @requires_fw -- they use tmp_path plants and synthetic text, and assert the real sibling file's blob SHA plus its repo's porcelain status are unchanged"

key-files:
  created:
    - firestarter_app/tests/test_py32_flash_map_host.py
  modified:
    - firestarter_app/firestarter/py32_dfu.py

key-decisions:
  - "D-13 and D-14 carry no HOST id and are recorded on the plan as `requirements: [HOST-03]` for schema validity and traceability only -- this plan does NOT discharge HOST-03. Plans 127-08 and 127-09 do."
  - "FLASH_SIZE (128 * 1024) is kept verbatim as the physical part-size constant so tests/test_py32_dfu.py::test_image_larger_than_flash_is_refused (which writes FLASH_SIZE + 1 bytes) still passes unmodified. APP_REGION_END is derived as FLASH_BASE + APP_REGION_SIZE rather than re-typed as the literal 0x0801E000, so the two constants cannot disagree."
  - "No override/force flag was added to _check_envelope's non-overridable refusal -- MEASURED: grep -c 'force\\|override' firestarter/py32_dfu.py returns 0, matching the pre-task-0 count derived from the pinned blob 94108960e610eebdaa6a01d7e4526d4ec5308aff (832 lines, unchanged since the 127-01 merge)."
  - "The cross-repo parity gate's path is resolved exclusively through tests/fw_presence.py's fw_path() -- never a hand-built Path(__file__).parent.parent.parent shape. grep -c 'parent.parent.parent' tests/test_py32_flash_map_host.py returns 0."
  - "No new ALLOWED_SKIP_REASONS entry was added or needed -- @requires_fw reuses the already-imported FW_ABSENT_REASON (entry 1 of 4); tests/test_skip_census.py still passes with exactly 4 allow-listed reasons."
  - "The live linker script (read directly from /workspaces/firestarter on v1.23-py32f071-integration) matches CONTEXT's transcription exactly: FLASH (rx) : ORIGIN = 0x08000000, LENGTH = 120K; CONFIG (r) : ORIGIN = 0x0801E000, LENGTH = 8K; BOOTLOADER (rx) : ORIGIN = 0x08000000, LENGTH = 0 -- a named zero-length seam Phase 129 will give a length, which moves the application's ORIGIN (recorded in the BOOTLOADER test's failure message, pointing at 127-CONTEXT.md <deferred>)."
  - "No requirement checkbox in .planning/REQUIREMENTS.md was ticked by this plan (verified: HOST-01..HOST-08 all still Pending in the working tree). This plan is not cited as HOST-03 evidence."

requirements-completed: []  # HOST-03 intentionally left unticked -- this plan does NOT discharge it (D-13/D-14 carry no HOST id); only Plan 127-12 may tick HOST-01..HOST-08

coverage:
  - id: D1
    description: "_check_envelope tightened from the 128 KiB physical part size to APP_REGION_END (0x0801E000); FLASH_SIZE retained verbatim for the existing test that depends on its name; refusal message names the reserved config region"
    requirement: "HOST-03"
    verification:
      - kind: unit
        ref: "tests/test_py32_dfu.py::test_image_larger_than_flash_is_refused"
        status: pass
      - kind: unit
        ref: "tests/test_py32_flash_map_host.py::TestEnvelopeBehaviour::test_rogue_128kib_image_is_now_refused"
        status: pass
      - kind: unit
        ref: "tests/test_py32_flash_map_host.py::TestEnvelopeBehaviour::test_exactly_app_region_size_is_accepted"
        status: pass
    human_judgment: false
  - id: D2
    description: "Eight local envelope-behaviour tests pin both boundaries (accepted-at-exactly-APP_REGION_SIZE, refused-at-APP_REGION_SIZE+1), an image ending inside CONFIG, a base at APP_REGION_END, a base below FLASH_BASE, the empty-image refusal, the rogue-128KiB regression pin, and the four-constant internal-consistency check"
    verification:
      - kind: unit
        ref: "tests/test_py32_flash_map_host.py::TestEnvelopeBehaviour (8 tests)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Fail-closed cross-repo linker-script parity gate: five @requires_fw tests parsing the live linker script against the host's four constants, behind a non-vacuity assertion that runs first; three RED demonstrations (empty-parse, planted mutated copy, K-suffix normalisation) proving the gate can actually fail"
    requirement: "HOST-03"
    verification:
      - kind: unit
        ref: "tests/test_py32_flash_map_host.py::TestLinkerScriptParity (5 tests)"
        status: pass
      - kind: unit
        ref: "tests/test_py32_flash_map_host.py::TestLinkerScriptParityFailsClosedOnBadInput (3 tests)"
        status: pass
      - kind: other
        ref: "git -C /workspaces/firestarter status --porcelain | wc -l == 0 (before and after the planted-copy test)"
        status: pass
    human_judgment: false

# Metrics
duration: ~45min
completed: 2026-08-01
status: complete
---

# Phase 127 Plan 05: Flash-Map Envelope Tightening + Cross-Repo Parity Gate Summary

**`_check_envelope` now refuses any image reaching past `0x0801E000` (the linker script's real application-region end) instead of the 128 KiB physical part size, and the four host constants that encode that map are held honest by a fail-closed gate that parses the live linker script directly.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-08-01 (approx)
- **Completed:** 2026-08-01
- **Tasks:** 3/3 executed
- **Files modified:** 2 (1 modified, 1 new)

## Accomplishments

- **Task 1:** `firestarter/py32_dfu.py` gained three new constants beside the existing `FLASH_BASE`/`FLASH_SIZE`: `APP_REGION_SIZE = 120 * 1024`, `APP_REGION_END = FLASH_BASE + APP_REGION_SIZE` (derived, not re-typed), and `CONFIG_REGION_SIZE = 8 * 1024`. `_check_envelope`'s upper bound moved from `FLASH_BASE + FLASH_SIZE` to `APP_REGION_END`; the refusal message now names the accepted span and explains that the region above it is the firmware's reserved config storage. The empty-image refusal, `FLASH_SIZE`'s name, and the module's non-overridable stance (no force/override token, verified against the pinned pre-merge blob) were all left untouched.
- **Task 2:** Created `tests/test_py32_flash_map_host.py` with its local half — 8 tests calling `Py32DfuFlasher()._check_envelope` directly, covering both new boundaries, the CONFIG-straddling case, the below-`FLASH_BASE` case, the unchanged empty-image refusal, the rogue-128-KiB regression pin, and a four-constant internal-consistency check. No skip marker.
- **Task 3:** Extended the same module with the cross-repo half — `_REGION_RE`/`_parse_regions` copied byte-identical from `firestarter/tests/test_py32_flash_map.py`, a path resolved through `fw_path()`, 5 `@requires_fw` parity tests (non-vacuity first and separately, `ORIGIN(CONFIG)`, `LENGTH(FLASH)`+`ORIGIN(FLASH)`, `LENGTH(CONFIG)`+in-script adjacency, and the zero-length `BOOTLOADER` seam), and 3 RED demonstrations with no `@requires_fw` (empty-parse non-vacuity trip, a planted mutated copy with before/after blob-SHA and porcelain-status proof, and a `K`-suffix normalisation pin).

## Task Commits

1. **Task 1: Split FLASH_SIZE into physical and application-region constants; bound `_check_envelope` on the application region** — `921f9eb` (fix)
2. **Task 2: `tests/test_py32_flash_map_host.py` — envelope behaviour tests** — `1843962` (test)
3. **Task 3: The fail-closed cross-repo linker-script parity gate** — `ee6c5af` (test)

**Meta-repo tracking commit:** pending (this SUMMARY + gitlink bump, committed next per `<final_commit>`)

All three commits are on `firestarter_app`'s `v1.23-py32f071-integration` branch.

## Files Created/Modified

- `firestarter_app/firestarter/py32_dfu.py` — `APP_REGION_SIZE`, `APP_REGION_END`, `CONFIG_REGION_SIZE` added; `_check_envelope` re-bounded; extended block comment citing D-13
- `firestarter_app/tests/test_py32_flash_map_host.py` — new module, 16 tests (8 local + 5 `@requires_fw` + 3 RED)

## Decisions Made

- Kept `FLASH_SIZE` byte-for-byte and derived `APP_REGION_END` arithmetically from `FLASH_BASE + APP_REGION_SIZE` rather than writing `0x0801E000` as a second literal, per the plan's explicit instruction — this makes the two constants structurally incapable of disagreeing.
- Structured the cross-repo parity tests as five small, independently-readable test methods (one assertion group each) rather than one monolithic parity function, matching the plan's "Five `@requires_fw` parity tests" framing while still sharing `_load_regions`/`_assert_non_vacuous`/`_assert_config_origin_matches` helpers so the planted-copy RED test can call the same logic the live tests use.
- The planted-copy RED test reads the real linker script to build its mutation and asserts the real file's blob SHA plus the firmware repo's `git status --porcelain` are unchanged before and after — this makes the test's full RED-detection claim verifiable in this environment (firmware sibling present), matching the acceptance criteria's explicit reference to `/workspaces/firestarter`, while carrying no `@requires_fw` skip marker per the plan's instruction.
- Named the two new test classes `TestLinkerScriptParity` and `TestLinkerScriptParityFailsClosedOnBadInput` to make the plan's two-halves structure (live parity vs. RED demonstrations) visible directly in `pytest -v` output.

## Deviations from Plan

None (Rule 1/2/3 sense) — plan executed exactly as written. No scope creep: only the two files named in the plan's `files_modified` were touched. `/workspaces/firestarter` is unmodified (verified `git status --porcelain | wc -l == 0` both before Task 1's read and after Task 3's planted-copy test). No requirement checkbox in `.planning/REQUIREMENTS.md` was ticked.

## Issues Encountered

- `ruff format` reformatted one line in the newly-created test file after Task 2 (a two-argument call the formatter preferred on one line) — applied via `ruff format tests/test_py32_flash_map_host.py` before committing; re-verified with `ruff format --check` afterward. Not a deviation from plan content, purely mechanical formatting.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `APP_REGION_SIZE`, `APP_REGION_END`, `CONFIG_REGION_SIZE` now exist on `firestarter/py32_dfu.py` for Plans 127-08/127-09 to build on (neither plan needs to introduce these constants itself).
- `tests/test_py32_flash_map_host.py` is green (16/16) and will re-run automatically in every future plan's full-suite verification, catching any future drift between the host constants and the linker script the moment either side changes.
- Full app suite: **1259 collected / 1259 passed / 0 failed / 0 skipped** (1243 baseline + 16 new). `ruff check`, `ruff format --check`, and `python tools/check_mypy_watermark.py` all clean.
- HOST-01..HOST-08 all remain `[ ]` Pending in `.planning/REQUIREMENTS.md` — unaffected by this plan, as instructed.
- `/workspaces/firestarter` remains untouched (read-only input), confirmed clean before and after this plan's execution.

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/py32_dfu.py` (modified)
- FOUND: `firestarter_app/tests/test_py32_flash_map_host.py`
- FOUND: commit `921f9eb` in `firestarter_app` git log
- FOUND: commit `1843962` in `firestarter_app` git log
- FOUND: commit `ee6c5af` in `firestarter_app` git log
- FOUND: `.planning/phases/127-host-dfu-installer/127-05-SUMMARY.md`
