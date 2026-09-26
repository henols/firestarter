---
phase: 129-flash-path-decision-pcb-requirements-record
plan: 05
subsystem: docs
tags: [decision-record, py32f071, usb-vid-pid, pid-codes, socket-safety, claim-ceiling]

requires:
  - phase: 129-04
    provides: ".planning/v1.23-FLASH-PATH-DECISION.md — header block, §1 Context, §2 [SHARED:S1], §3 [SHARED:S2] the PCB checklist, §4 [SHARED:S3] the flash budget"
provides:
  - ".planning/v1.23-FLASH-PATH-DECISION.md — §5 [SHARED:S4] the USB vendor/product identity decision, §6 [SHARED:S5] the socket-empty-before-install instruction, §7 the rejected-route survey, §8 tracked obligations, §9 open questions, and the closing Claim ceiling — the record is now complete"
affects: [129-06, 129-07, 129-08, 129-09]

tech-stack:
  added: []
  patterns:
    - "Claim ceiling defers to REQUIREMENTS.md §\"Validation Ceiling\" by reference rather than restating its wording — avoids the Phase 125 self-reference trap when check_permitted_claims.py scans the file directly"
    - "§7's obligation and comparative-verdict tables are meta-only (no [SHARED:Sn] marker), keeping the meta layer the authoritative rationale layer over the firmware subset"

key-files:
  created: []
  modified:
    - .planning/v1.23-FLASH-PATH-DECISION.md

key-decisions:
  - "§5(c)'s ship gate sentence is reproduced character-for-character from the gate's _L2_SHIP_GATE constant, wrapped in ** bold on its own line, with no other text inserted inside it"
  - "§6's socket-empty instruction uses U+2014 EM DASH (not a double hyphen) in both dash positions, matching _L3_SOCKET_EMPTY exactly"
  - "§7-§9 carry no [SHARED:Sn] marker — verified by a zero-hit grep for '^## [789]\\..*\\[SHARED:' — keeping them meta-only per the plan's own instruction"
  - "The claim ceiling's toolchain sentence is reworded from CONFIG-STORAGE.md's original: 'not installed by default... installable... delta claims only' rather than 'absent from this environment', since RESEARCH C-3 and D-13 proved a local ARM build byte-identical this phase"
  - "The claim ceiling defers to REQUIREMENTS.md §\"Validation Ceiling\" by reference only — no forbidden phrase from that section's list is reproduced, avoiding the Phase 125 self-reference trap"

patterns-established: []

requirements-completed: []

coverage:
  - id: D1
    description: "§5 [SHARED:S4] — the corrected USB VID/PID provenance (0x36B7 allocated to Puya Semiconductor, pair copied verbatim from the pinned SDK's usbd_cdc_if.c), the pid.codes 0x1209 decision with interim 1209:0001, the verbatim ship gate, sequencing/latency findings, and the no-agent-files-it rule, with usb_cdc.c demonstrably untouched"
    requirement: "PCB-04"
    verification:
      - kind: unit
        ref: "pytest tests/test_flash_path_record_sync.py::TestFlashPathRecordSync::test_meta_extract_is_non_vacuous[S4] and ::test_vid_pid_decision_and_ship_gate[meta] -- 2 passed"
        status: pass
    human_judgment: false
  - id: D2
    description: "§6 [SHARED:S5] — the verbatim socket-empty-before-install instruction and its four-part reason (provisional-by-declaration, direction hazard, unmeasured startup levels, DFU as the acute case), tripping no forbidden claim phrase"
    requirement: "PCB-05"
    verification:
      - kind: unit
        ref: "pytest tests/test_flash_path_record_sync.py::TestFlashPathRecordSync::test_meta_extract_is_non_vacuous[S5] and ::test_socket_empty_instruction_present[meta] -- 2 passed"
        status: pass
    human_judgment: false
  - id: D3
    description: "§7 rejected-route survey (install routes + USB identity routes with a comparative verdict table), §8 tracked-obligations table, §9 five open questions — all meta-only, no [SHARED:Sn] marker"
    verification:
      - kind: unit
        ref: "grep-based acceptance criteria in 129-05-PLAN.md Task 3's <verify><automated> block -- all passed"
        status: pass
    human_judgment: false
  - id: D4
    description: "Closing Claim ceiling section, deferring to REQUIREMENTS.md §\"Validation Ceiling\" by reference; meta commit contains only the record file; REQUIREMENTS.md/ROADMAP.md untouched; RED ledger drops from 24 failed/197 passed to exactly 20 failed/201 passed"
    verification:
      - kind: unit
        ref: "python3 check_permitted_claims.py .planning/v1.23-FLASH-PATH-DECISION.md -- exit 0, PASS; pytest tests/ -q -- 20 failed, 201 passed"
        status: pass
    human_judgment: false

duration: ~10min
completed: 2026-08-02
status: complete
---

# Phase 129 Plan 05: USB Identity Decision, Socket-Empty Instruction, Rejected Routes and Open Questions Summary

**Completed `.planning/v1.23-FLASH-PATH-DECISION.md` with §5 (pid.codes VID/PID decision, PCB-04), §6 (socket-empty instruction, PCB-05), §7-§9 (meta-only rejected routes, obligations, open questions), and a closing Claim ceiling that defers to REQUIREMENTS.md by reference.**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-08-02T11:43:00Z (approx, first task commit at 11:43:46)
- **Completed:** 2026-08-02T11:46:55Z
- **Tasks:** 4
- **Files modified:** 1

## Accomplishments

- **Task 1 — §5 USB vendor and product identity `[SHARED:S4]`.** Recorded the corrected provenance (`0x36B7` allocated to Puya Semiconductor; the exact `36B7:FFFF` pair copied verbatim from the pinned SDK's own USB CDC example at `usbd_cdc_if.c:9-10` / `pycdc.inf:28,31`, `GIT_TAG 0ed2f4b4d3391eccfd4491006a30295fd78e32c2`), the pid.codes `0x1209` decision with interim `1209:0001` and target `1209:<allocated>`, the verbatim ship gate as a checkable condition, the `usb_cdc.c`-not-edited disposition (D-06) with the `py32_dfu.py` interface-class `0xFE/0x01` discovery fact and the `0x0448` clarification, and the pid.codes sequencing tension plus date-stamped queue latency (64 open PRs, measured 2026-08-02).
- **Task 2 — §6 Socket empty before any PY32F071 firmware install `[SHARED:S5]`.** Recorded the verbatim instruction and the four reasons it is stronger here: the map is provisional by declaration (`RURP_PY32F071_PINMAP_PROVISIONAL`), the specific hazard is pin direction, the startup levels are asserted but unmeasured, and a DFU install is the acute case since no Firestarter code runs during it. Recorded placement (firmware subset verbatim, README.md pointer) and the out-of-scope propagation into `firestarter_app`.
- **Task 3 — §7 rejected routes, §8 tracked obligations, §9 open questions.** Three meta-only sections (no `[SHARED:Sn]` marker): the four rejected install routes and four USB-identity routes with a comparative verdict table; an obligation table naming the operator-filed pid.codes PR, the eventual `usb_cdc.c` edit, Phase 130's CLOSE-01/CLOSE-02 sweeps, the `PY32F071-FIRMWARE-INSTALL.md` propagation, and FUT-N05/FUT-N06; and five open questions including D-15's two-sided reboot-into-bootloader board cost.
- **Task 4 — the claim ceiling, the claim-gate run, and the commit.** Appended the closing `## Claim ceiling` section, reworded from `CONFIG-STORAGE.md`'s original to reflect RESEARCH C-3 (the ARM toolchain is installable, not absent) and deferring to `REQUIREMENTS.md` §"Validation Ceiling" by reference. Ran the claim gate to a clean `PASS`. Committed on `gsd/v1.23-py32f071-integration`, staging only the record file.

## Task Commits

Each task was committed atomically:

1. **Task 1: §5 USB vendor and product identity** - `0170810` (docs)
2. **Task 2: §6 Socket empty before any PY32F071 firmware install** - `b5a971e` (docs)
3. **Task 3: §7 rejected routes, §8 tracked obligations, §9 open questions** - `7c80810` (docs)
4. **Task 4: Claim ceiling, claim-gate run, and commit** - `a81e8c2` (docs)

**Recorded verbatim (per plan's `<output>` instruction):**

- Claim-gate command and full output:
  ```
  $ python3 .planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py .planning/v1.23-FLASH-PATH-DECISION.md
  PASS: scanned ../../v1.23-FLASH-PATH-DECISION.md; 1 file(s) carry the required silicon caveat (this PASS is the mechanizable half of the honesty criterion only -- see the module docstring's explicit non-claim)
  ```
  Exit code: `0`.
- Pytest summary line before Task 1 (this plan's baseline, inherited from 129-04): `24 failed, 197 passed`
- Pytest summary line after Task 3 (§7-§9 add no gated content): `20 failed, 21 passed` (scoped run of `test_flash_path_record_sync.py` only)
- Pytest summary line after Task 4 (full suite): `20 failed, 201 passed` (matches the plan's own prediction exactly)
- Discharged node ids: `TestFlashPathRecordSync::test_meta_extract_is_non_vacuous[S4]`, `TestFlashPathRecordSync::test_vid_pid_decision_and_ship_gate[meta]`, `TestFlashPathRecordSync::test_meta_extract_is_non_vacuous[S5]`, `TestFlashPathRecordSync::test_socket_empty_instruction_present[meta]`
- Meta commit SHAs: `0170810`, `b5a971e`, `7c80810`, `a81e8c2`, all on branch `gsd/v1.23-py32f071-integration`
- Firmware branch: `v1.23-py32f071-integration` @ `42395cf` (unchanged this plan — no firmware file touched, no gitlink bump; `git status --porcelain` returned zero bytes at every check)

**Interim note on Task 1's own acceptance criterion:** the plan specifies that `check_permitted_claims.py` must exit non-zero after Task 1 (claim ceiling not yet written) and record that exit code. Recorded here: after Task 1, the checker printed `FAIL: 1 missing required silicon caveat` and exited `1` — the only failure bucket was the missing caveat, exactly as the plan anticipated.

## Files Created/Modified

- `.planning/v1.23-FLASH-PATH-DECISION.md` — appended `## 5. USB vendor and product identity [SHARED:S4]`, `## 6. Socket empty before any PY32F071 firmware install [SHARED:S5]`, `## 7. Candidate survey — the rejected routes`, `## 8. Consequences and tracked obligations`, `## 9. Open questions`, and `## Claim ceiling`. The record is now complete end to end (§1 through §9 plus the claim ceiling).

## Decisions Made

- **§5(c)'s ship gate** is reproduced character-for-character against the gate's `_L2_SHIP_GATE` constant, wrapped in `**` bold on its own line with nothing else inserted inside it.
- **§6's socket-empty instruction** uses U+2014 EM DASH in both dash positions (not a double hyphen), matching `_L3_SOCKET_EMPTY` exactly.
- **§7-§9 carry no `[SHARED:Sn]` marker** — confirmed by a zero-hit grep for `^## [789]\..*\[SHARED:` — so they stay meta-only rather than being pulled into the firmware subset by 129-06.
- **The claim ceiling's toolchain sentence is reworded, not copied, from `CONFIG-STORAGE.md`'s original**: it says the toolchain is "not installed by default... but is installable from the same packages CI uses" and that a local build supports delta claims only, rather than the older "absent from this environment" phrasing — because RESEARCH C-3 proved a local ARM build byte-identical this phase, and the older phrasing is contradicted by that evidence. The correction is flagged as owed to `REQUIREMENTS.md` §"Validation Ceiling" via Phase 130's CLOSE-01 sweep, not fixed in place here.
- **The claim ceiling defers to `REQUIREMENTS.md` §"Validation Ceiling" by reference only** — no forbidden phrase from that section's own list is reproduced anywhere in this document, avoiding the Phase 125 self-reference trap that `check_permitted_claims.py` is built to catch.

## Deviations from Plan

None — plan executed exactly as written. Every acceptance-criteria grep and every `<verify><automated>` block in the plan's four tasks was run and passed before each commit.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `.planning/v1.23-FLASH-PATH-DECISION.md` is now complete: §1 through §9 plus the closing `## Claim ceiling`. All five `[SHARED:Sn]` bodies (S1-S5) exist on the meta side.
- 129-06 mirrors all five `[SHARED:Sn]` bodies into the firmware subset (`platform/py32f071/FLASH-PATH-AND-PCB.md`) and discharges the `fw`-side and `test_shared_sections_match` legs, plus the planted-mutation leg against the real subset.
- 129-07 fixes the linker comment's false "on a part with no VTOR" clause (D-11/C-1).
- 129-08 updates the seed's frontmatter status (D-17).
- 129-09 is the only plan permitted to tick PCB-01…PCB-05, and also owns the meta gitlink bump for `firestarter` (D-05) — deliberately unbumped by this plan and every plan before it.
- No blockers. Meta repo clean apart from the intentional pre-existing dirty gitlinks (`firestarter`, `firestarter_app` — both left unbumped, confirmed unchanged by every one of this plan's four commits via `git diff HEAD~1 HEAD -- firestarter firestarter_app` returning zero bytes at each). Firmware tree untouched and clean at `42395cf` throughout.

---
*Phase: 129-flash-path-decision-pcb-requirements-record*
*Completed: 2026-08-02*

## Self-Check: PASSED

- `.planning/v1.23-FLASH-PATH-DECISION.md` — FOUND
- Commits `0170810`, `b5a971e`, `7c80810`, `a81e8c2` — FOUND in `git log --oneline --all`
- This SUMMARY.md itself, committed as `bc30f6b` — FOUND
