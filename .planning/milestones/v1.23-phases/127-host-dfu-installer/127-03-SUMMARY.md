---
phase: 127-host-dfu-installer
plan: 03
subsystem: testing
tags: [dfu, dfuse, py32f071, known-answer-test, opcode-anchoring, usb-dfu-1.1, um1504]

# Dependency graph
requires:
  - phase: 127-01
    provides: "firestarter/py32_dfu.py, tests/test_py32_dfu.py landed on the milestone branch via the feature/py32f071-fw-install merge"
provides:
  - "tests/test_dfu_opcode_anchors.py — an independent known-answer oracle for firestarter/py32_dfu.py's DFU 1.1 request codes, functional-descriptor type, bitCanUpload mask, UM1504 DfuSe command values, bcdDFUVersion and FLASH_BASE"
  - "A forward-holding test proving tests/test_py32_dfu.py contains no source==source opcode assertion, so research finding 7's oracle cannot be reintroduced there"
  - "A1's status recorded: USB DFU 1.1 spec independently fetched and read (genuine oracle); UM1504 not obtainable this session (network-layer failure, not a document-existence finding) — residual carried to Plan 127-12"
affects: [127-09, 127-12, 130-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Independent known-answer constant block with a citing comment naming the exact spec/table/page, never imported from the module under test (126 D-05 discipline, applied to HOST-06)"
    - "Anchor a not-yet-created production constant as a bare literal only, describing it in prose without naming it, so a forward-referencing plan (127-09) can safely add the first equality assertion later"

key-files:
  created:
    - firestarter_app/tests/test_dfu_opcode_anchors.py
  modified: []

key-decisions:
  - "C-2 re-derived first-hand (not inherited): tests/test_py32_dfu.py's blob SHA f9678411044119e4df66103ea2254704f8569a06 is unchanged before/after this plan; the scan for a source==source assertion returns zero matches both times. D-18's original 'remove or convert' wording is superseded; this plan is purely additive."
  - "A genuine, unplanned network attempt for A1: the USB DFU 1.1 Revision 1.1 PDF (usb.org) was fetched and read directly (sha256 bbe4a3341c3bfc80cc6ba31b676998c379dcc42602f4b2ca7c5ea8b8dccd5c0d), independently confirming all 7 request codes, the 0x21 functional-descriptor type, and the bitCanUpload bit position against Table 3.2 / Table 4.2. UM1504 (Puya/ST DfuSe note) was attempted twice against st.com and failed at the network layer both times (curl HTTP/2 stream error; wget timeout) — an environmental failure, recorded honestly as still-unobtained, not silently treated as 'consistent enough'."
  - "The bitCanUpload mask (0x02) is anchored as a bare literal with zero equality assertion and zero literal occurrence of the not-yet-created production constant's name anywhere in the file (grep -c returns 0) — Plan 127-09 creates that constant and adds the first comparison."

requirements-completed: []  # HOST-06 intentionally left unticked — only Plan 127-12 may tick HOST-01..HOST-08 (Phase-116 4x premature-tick guard)

coverage:
  - id: D1
    description: "Independent oracle anchors all USB DFU 1.1 + UM1504 opcode/version/address literals against firestarter.py32_dfu's constants, never importing the expectation from the module under test"
    requirement: "HOST-06"
    verification:
      - kind: unit
        ref: "tests/test_dfu_opcode_anchors.py::test_dfu_request_codes_match_usb_dfu_11_table_3_2"
        status: pass
      - kind: unit
        ref: "tests/test_dfu_opcode_anchors.py::test_dfu_functional_descriptor_type_matches_usb_dfu_11_section_4_1_3"
        status: pass
      - kind: unit
        ref: "tests/test_dfu_opcode_anchors.py::test_dfuse_commands_match_um1504"
        status: pass
      - kind: unit
        ref: "tests/test_dfu_opcode_anchors.py::test_dfuse_version_matches_um1504"
        status: pass
      - kind: unit
        ref: "tests/test_dfu_opcode_anchors.py::test_flash_base_matches_py32f071xb_memory_map"
        status: pass
      - kind: unit
        ref: "tests/test_dfu_opcode_anchors.py::test_bit_can_upload_mask_is_anchored_pending_plan_127_09"
        status: pass
    human_judgment: false
  - id: D2
    description: "tests/test_py32_dfu.py's 58 tests and blob SHA are untouched by this plan; a forward-holding test proves it stays free of a source==source opcode assertion"
    verification:
      - kind: unit
        ref: "tests/test_dfu_opcode_anchors.py::test_test_py32_dfu_still_contains_no_source_source_opcode_oracle"
        status: pass
      - kind: other
        ref: "git rev-parse HEAD:tests/test_py32_dfu.py == f9678411044119e4df66103ea2254704f8569a06 (unchanged before/after); pytest tests/test_py32_dfu.py -q -> 58 passed"
        status: pass
    human_judgment: false

# Metrics
duration: 35min
completed: 2026-08-01
status: complete
---

# Phase 127 Plan 03: Independent DFU Opcode Anchors Summary

**One new test module (`tests/test_dfu_opcode_anchors.py`) anchors all 12 DFU/DfuSe wire-constant values named in D-18 (plus the functional-descriptor type and the not-yet-created `bitCanUpload` mask) against independently-written literals — with the USB DFU 1.1 half of the citation genuinely fetched and read this plan, not merely trusted; `tests/test_py32_dfu.py`'s 58 tests are untouched.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-08-01T12:00:00Z (approx)
- **Completed:** 2026-08-01T12:35:20Z
- **Tasks:** 2/2 executed
- **Files modified:** 1 (new)

## Accomplishments

- **Task 1 (evidence, no files modified):** Re-derived C-2 first-hand rather than inheriting it.
  - Pinned `tests/test_py32_dfu.py`'s blob SHA: `f9678411044119e4df66103ea2254704f8569a06`, `wc -l` = 654, collected count = 58 (all re-measured live, matching the plan's expectations).
  - Re-ran C-2's scan (`grep -nE "assert\s+(py32_dfu\.)?(DFU|DFUSE|FLASH)_[A-Z_]+\s*==\s*(0x)?[0-9]" tests/test_py32_dfu.py`) — **zero matches**, confirming D-18's "self-referential assertions" do not exist in that file.
  - Classified every line mentioning `DFUSE_ERASE_PAGE`, `DFUSE_SET_ADDRESS`, `DFUSE_VERSION`, `FLASH_BASE` in `tests/test_py32_dfu.py` (grep output, see table below): 4 are `import`, 1 is `other` (a factory-function default-parameter value at `:110`), and the remainder — 13 lines — are `sequencing` (list/tuple membership or equality assertions using the constant as a label, e.g. `assert (DFUSE_ERASE_PAGE, FLASH_BASE) in commands`). None is a source==source numeric-literal comparison.
  - **A1: made a genuine read-only lookup attempt of both cited specifications, with an asymmetric outcome, recorded honestly:**
    - **USB DFU 1.1 Revision 1.1** ("USB Device Firmware Upgrade Specification"), the official PDF from `usb.org`, **was fetched and read directly** (`curl` → 200, 143186 bytes, 47 pages; sha256 `bbe4a3341c3bfc80cc6ba31b676998c379dcc42602f4b2ca7c5ea8b8dccd5c0d`). Table 3.2 "DFU Class-Specific Request Values" (page 10) confirms `DFU_DETACH=0, DFU_DNLOAD=1, DFU_UPLOAD=2, DFU_GETSTATUS=3, DFU_CLRSTATUS=4, DFU_GETSTATE=5, DFU_ABORT=6` verbatim. Table 4.2 "DFU Functional Descriptor" §4.1.3 (page 13) confirms `bDescriptorType = 21h` and "Bit 1: upload capable (bitCanUpload)". This is a **genuinely independent** oracle — text extracted with `pypdf` (installed ad hoc for this one-time read, not added to the project) from the fetched document, not copied from the module under test.
    - **UM1504** (the Puya/ST DfuSe application note) was **not obtained**. Two read-only fetch attempts against `st.com` (the plausible host) both failed at the network layer in this sandbox: `curl https://www.st.com/...` → `HTTP/2 stream 1 was not closed cleanly: INTERNAL_ERROR`; `wget` on the same URL → timed out (exit 124) with zero bytes downloaded. This is an **environmental failure** (host unreachable from here), not evidence the document doesn't exist. The four DfuSe-specific values (`DFUSE_SET_ADDRESS`, `DFUSE_ERASE_PAGE`, `DFUSE_READ_UNPROTECT`, `DFUSE_VERSION`) therefore remain **consistent-with-the-module rather than independently sourced** — the genuine, surviving A1 residual, recorded plainly in the new module's docstring and here.
    - `FLASH_BASE` (0x08000000) is separately and independently corroborated by `127-RESEARCH.md` §C-7/§Q2's live read of the firmware linker script (`platform/py32f071/linker/PY32F071xB_FLASH.ld`) — a different, stronger source than either UM1504 or the module under test.
  - Confirmed: D-18's removal instruction is superseded by C-2; this plan deletes and converts nothing in `tests/test_py32_dfu.py`.
- **Task 2:** Created `firestarter_app/tests/test_dfu_opcode_anchors.py` (280 lines):
  - Independent constant block: 7 USB DFU 1.1 request codes, the functional-descriptor type (0x21), the `bitCanUpload` mask (0x02, anchored but not asserted), 3 UM1504 DfuSe commands, `bcdDFUVersion` (0x011A), and `FLASH_BASE` (0x08000000) — each its own module-level literal with a citing comment, never imported from `firestarter.py32_dfu` to build the expectation.
  - The two 0x21 values (`_DFU_FUNCTIONAL_DESCRIPTOR` and `DFUSE_SET_ADDRESS`) are two visibly distinct constants with distinct citing comments and distinct assertions (T-127-03-05).
  - 5 comparison tests (request codes, functional-descriptor type, DfuSe commands, DfuSe version, flash origin), each with a 126-D-05-shaped failure message naming the spec/table and both values in hex.
  - 1 test keeping the `bitCanUpload` mask on record without asserting it or naming the not-yet-created production constant anywhere in the file.
  - 1 forward-holding test re-running C-2's scan against `tests/test_py32_dfu.py` at test time, with a non-vacuity guard (the file must mention at least one `DFU_*`/`DFUSE_*`/`FLASH_*` name) and a failure message naming the offending line and pointing back at this module.
  - No skip marker; no `ALLOWED_SKIP_REASONS` entry needed or added.

## Task Commits

1. **Task 1: Record the C-2 evidence and pin tests/test_py32_dfu.py's blob SHA** — no commit (read-only capture into this SUMMARY, per the plan)
2. **Task 2: tests/test_dfu_opcode_anchors.py — independent UM1504 / DFU 1.1 anchors** — `5593642` (test)

**Meta-repo tracking commit:** pending (this SUMMARY + gitlink bump, committed next per `<final_commit>`)

## Files Created/Modified

- `firestarter_app/tests/test_dfu_opcode_anchors.py` — new independent-oracle test module for the DFU/DfuSe opcode literals (HOST-06)

## Decisions Made

- Used `getattr(py32_dfu, name)` loops for the multi-value comparisons (request codes, DfuSe commands) rather than one assert per constant, to keep the independent-literal dict and the per-name failure message DRY while still naming exactly which constant failed.
- Named the independent literals with an `_ANCHORED_` prefix (not the production names) so the module can never accidentally shadow or alias the imported observed values — `py32_dfu.<NAME>` is always referenced module-qualified, making "imported from the module under test" structurally impossible to introduce by accident.
- Removed a first draft of a self-check test that asserted the literal string `_DFU_BIT_CAN_UPLOAD` was absent from this file — that assertion necessarily contains the very string it forbids (a self-reference trap, the same class as `reference_byte_identical_test_file_criterion_trap`), which made the file's own `grep -c '_DFU_BIT_CAN_UPLOAD'` gate fail. Replaced with a plain description-only test that never types the name; verified externally with the plan's own grep command, which now returns 0.
- Recorded the A1 network-attempt outcome plainly and asymmetrically (DFU 1.1 obtained; UM1504 not) rather than treating "one document fetched" as discharging the whole residual — the module docstring and this SUMMARY both preserve the distinction.

## Deviations from Plan

**None (Rule 1/2/3 sense) — one genuine correction to my own first draft, self-caught and fixed before commit, documented above under Decisions Made** (the self-reference trap in the `bitCanUpload` guard test). No scope creep: only the one file named in the plan's `files_modified` was touched, and `tests/test_py32_dfu.py` is byte-identical (blob SHA verified equal before and after).

## Issues Encountered

- The full 1243-test suite (`pytest tests/ -q --no-cov`) took ~139s in one run and initially timed out when chained after several other verification commands in a single 120s-capped call; re-run standalone with a longer timeout and completed cleanly. Not a defect — `tests/test_skip_census.py` and the pyusb-absent/channel-gating subprocess tests each spawn a full-suite child process, which is inherently slower than the individual per-module runs.

## User Setup Required

None — no external service configuration required.

## Claim Ceiling

This plan proves that `firestarter/py32_dfu.py`'s DFU 1.1 opcode constants match the official USB DFU 1.1 specification (independently fetched and read) and that its DfuSe-specific constants are internally self-consistent with what the module already claims (UM1504 itself not independently obtained this session — residual A1, carried to Plan 127-12). It proves **nothing** about a PY32F071 bootloader's real behavior: no PCB exists, and this plan asserts only that written-down numbers match written-down numbers.

## Next Phase Readiness

- `tests/test_dfu_opcode_anchors.py` exists and is green; Plan 127-09 can safely add the equality assertion for the module's `bitCanUpload` mask constant once it creates it — this file already anchors the mask value and contains zero references to that constant's name (verified: `grep -c` returns 0).
- A1's asymmetric outcome (DFU 1.1 obtained; UM1504 not, environmental failure) is recorded in both the module docstring and this SUMMARY in a form Plan 127-12's honesty ledger can lift directly.
- `tests/test_py32_dfu.py` is confirmed byte-identical (blob SHA `f9678411044119e4df66103ea2254704f8569a06`) before and after this plan; no later plan needs to reconcile a divergence here.
- Full app suite: **1243 collected / 1243 passed / 0 failed** (1236 baseline + 7 new), `ruff check` and `ruff format --check` both clean. Coverage not measured in this plan's verification (run with `--no-cov` per the plan's own verify command); the primary `ci` job's `--cov-fail-under=70` gate is unaffected since no production code changed.
- No requirement checkbox in `.planning/REQUIREMENTS.md` was ticked (verified: HOST-01..HOST-08 all still `[ ]` Pending).

## Self-Check: PASSED

- FOUND: `firestarter_app/tests/test_dfu_opcode_anchors.py`
- FOUND: commit `5593642` in `firestarter_app` git log
- FOUND: `.planning/phases/127-host-dfu-installer/127-03-SUMMARY.md`
