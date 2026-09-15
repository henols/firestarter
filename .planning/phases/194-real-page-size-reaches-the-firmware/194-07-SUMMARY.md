---
phase: 194-real-page-size-reaches-the-firmware
plan: "07"
subsystem: firmware-protocol
tags: [bench-validation, page-size, protocol-0x05, W29C020, leonardo, chip-id, no-regression]

requires:
  - phase: 194-01
    provides: "flash_5v_page_write_execute resolve-or-refuse via handle->page_size, from-source firmware this run flashed and measured"
  - phase: 194-06
    provides: "the 27-row page-size measurement record and the evidence-class split this transcript pairs with"
provides:
  - ".planning/v1.39/194-w29c020-bench-transcript.md -- a committed no-regression silicon transcript on W29C020, chip-ID-confirmed, byte-identical read-back"
  - "PAGE-03's REQUIREMENTS.md status note extended to cite the transcript, checkbox left open"
affects: [phase-195-w29c512-bench-close-of-page-03]

actuals:
  tokens: 3808
  tasks: 3
  commits: 1
  plan_head_before: "meta@f07982b5"

tech-stack:
  added: []
  patterns:
    - "Bench transcript scope discipline: a no-regression proof on an already-correct part states, in its own section, both what it proves and what it structurally cannot prove, so the record cannot later be misread as evidence for an unrelated part class"

key-files:
  created:
    - .planning/v1.39/194-w29c020-bench-transcript.md
  modified:
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Flashed this phase's firmware by building from source with PlatformIO and uploading directly (pio run -t upload -e leonardo), rather than via the app's fw --install route, because that route downloads the latest public GitHub release (3.0.0b31, matching the version string by coincidence of no version bump in this phase) rather than this session's committed tree. The from-source build's byte-identical flash-size figure (23734/28672 B, matching 194-06-SUMMARY.md exactly) is the attribution evidence, not the version string alone."
  - "Negative control (Task 2 Step 6) recorded as skipped, per the plan's own named condition: all 27 algorithm-5 rows in the shipped database now carry page_size, so no route exists to drive a protocol 0x05 write against a page-size-less chip without editing the shipped database, which this plan prohibits."
  - "Test pattern sized at 2048 bytes (16 x 128-byte pages) rather than a full 262144-byte chip write, since the plan's success criterion is a contiguous multi-page write that would expose a mis-placed page boundary, not a full-chip stress test, and a smaller write reduces wear on a part with finite endurance."

patterns-established:
  - "A no-regression bench run on an already-correct part carries an explicit 'what this does and does not prove' section in its own transcript, not only in the requirements note that cites it."

requirements-completed: []

coverage:
  - id: D1
    description: "A contiguous multi-page write to a chip-ID-confirmed W29C020, with this phase's firmware and host on an operator-described Leonardo/Rev 2.0 rig, reads back byte-identical. Every figure carries the command that produced it."
    requirement: "PAGE-03"
    verification:
      - kind: manual_procedural
        ref: ".planning/v1.39/194-w29c020-bench-transcript.md sections 3-4: pio run -e leonardo (23734/28672 B), pio run -t upload -e leonardo (avrdude verified), firestarter id W29C020 (chip-id 0x0000da45 match), firestarter write W29C020 + read -s 2048 (sha256 d7a3b21b... on both sides)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The transcript states its own scope: proves no regression on the 18 already-correct parts, proves nothing about the 9 previously under-sized parts. PAGE-03 stays open in REQUIREMENTS.md, citing both this transcript and the 27-row record, with PAGE-01/PAGE-02 keeping their Complete state."
    requirement: "PAGE-03"
    verification:
      - kind: unit
        ref: "TRANSCRIPT-OK grep verify (pairs_with, 194-page-size-27-row-record, W29C020 all present); REQ-HONEST grep verify (PAGE-03 still [ ], PAGE-01/PAGE-02 still [x]); ROADMAP-UNTOUCHED commit-scope check -- all pass"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-09-15
status: complete
---

# Phase 194 Plan 07: W29C020 No-Regression Bench Transcript Summary

**A chip-ID-confirmed W29C020 write/read-back on a Leonardo running this phase's from-source firmware (23734/28672 B, byte-identical to 194-06) came back byte-identical over a 2048-byte, 16-page deterministic pattern -- a genuine no-regression proof on the part both reported defects were reproduced on, explicitly incapable of proving the 9 previously under-sized parts were fixed, and PAGE-03 stays open.**

## Performance

- **Duration:** ~50 min
- **Completed:** 2026-09-15
- **Tasks:** 3/3
- **Files modified:** 2 (1 created, 1 modified)

## Accomplishments

- **Task 1 (operator checkpoint):** the orchestrator had already put the four required questions to the operator and received answers before this executor was spawned. Re-confirmed rather than re-asked: a `W29C020` seated, shield "Rev 2.0 (operator-stated)", port `/dev/ttyACM1` at the time of the answer, and none of the 9 previously under-sized parts on hand.
- **Task 2 (drive the rig):** re-verified the rig identity independently rather than trusting the orchestrator's prior measurement -- exactly one serial device, USB descriptors `idVendor=2341 idProduct=8036` "Arduino LLC" "Arduino Leonardo". Confirmed the pre-flash board answered `Bad JSON` (pre-command-framing firmware), matching the documented signature. Built this phase's firmware from source (`pio run -e leonardo`, `23734/28672 B`, byte-identical to `194-06-SUMMARY.md`'s own figure) and flashed it directly via PlatformIO (`pio run -t upload -e leonardo`), not via the app's release-downloading `fw --install` route. The board re-enumerated as `/dev/ttyACM0` after the bootloader touch (device numbers shuffle across a replug, confirmed by comparing the USB sysfs physical path across the rename). Confirmed the seated part by chip-ID (`0x0000da45`, matching the database's `W29C020` row), never by marking. Wrote a 2048-byte, 16-page deterministic pattern (`byte[i] = ((i//128)*17 + i%128) & 0xFF`) with a plain `write` (no `-b`, no `--skip-erase`), read it back, and confirmed byte-identical by both `cmp` and independent `sha256sum`. Ran the app's own `verify` command as additional corroboration. Recorded the negative control as skipped, per the plan's own named condition: all 27 algorithm-5 rows in the shipped database now carry `page_size`, so no route exists to reach the refusal path without editing the shipped database.
- **Task 3 (commit and record honestly):** wrote `.planning/v1.39/194-w29c020-bench-transcript.md` with every figure attributed to its verbatim command, a `pairs_with` frontmatter key naming the 27-row record, and an explicit "what this proves / what it does not" section. Extended PAGE-03's status note in `.planning/REQUIREMENTS.md` to cite the new transcript alongside the 27-row record, leaving the checkbox open. Diffed `.planning/REQUIREMENTS.md` before committing and confirmed every hunk was mine (the concurrent session's edits, if any, were untouched). Committed both files with an explicit pathspec (never a bare `git commit`), confirmed the commit's stat line named only the two files, and confirmed `.planning/ROADMAP.md` was not modified.

## Task Commits

1. **Task 1 (operator checkpoint):** no files edited -- answers already recorded by the orchestrator before this run
2. **Task 2 (drive the rig):** no tracked-file commits -- drives hardware and captures output for Task 3, per the plan's own file scope
3. **Task 3 (transcript + REQUIREMENTS.md):** meta `d3bf465f` (docs, `.planning/v1.39/194-w29c020-bench-transcript.md` + `.planning/REQUIREMENTS.md`)

**Plan metadata:** this SUMMARY only -- STATE.md/ROADMAP.md are owned by the orchestrator in this repo, per the shared_artifact_rule override

## Files Created/Modified

- `.planning/v1.39/194-w29c020-bench-transcript.md` -- new, the committed no-regression bench transcript: rig identity (measured and operator-stated), firmware/host versions, chip-ID confirmation, pattern rule, write/read-back result, negative-control disposition, scope section
- `.planning/REQUIREMENTS.md` -- PAGE-03's status note extended to cite the new transcript; checkbox stays `[ ]`; PAGE-01/PAGE-02 keep `[x]`

## Decisions Made

- **Flashed by building from source, not via `fw --install`.** The app's install route downloads the latest public GitHub release (`3.0.0b31`), which happens to match the firmware's static version string only because this phase never bumped it. Building and uploading directly from the checked-out `firestarter_fw` tree (`firestarter_fw@aabd0dd`) and confirming the byte-identical flash-size figure against `194-06-SUMMARY.md` is the actual attribution evidence, recorded explicitly in the transcript so the version-string coincidence cannot be mistaken for proof.
- **Test pattern sized at 2048 bytes / 16 pages**, not a full-chip write. The plan's success criterion is a contiguous multi-page write that would expose a mis-placed page boundary, which 16 pages already demonstrates repeatedly; a full 262144-byte write was not needed and adds needless wear to a part with finite write endurance.
- **Negative control skipped, with the reason recorded.** All 27 `algorithm: 5` rows in the shipped, regenerated database carry `page_size` (measured directly, `missing: []`), so no supported route exists to reach the page-size refusal path on real hardware without editing the shipped database, which this plan prohibits. The refusal path itself is already proven natively in plan 02 (four rejected classes, one positive control) and at the host layer in plan 05.

## Deviations from Plan

None -- plan executed exactly as written. Task 1's checkpoint had already been answered by the orchestrator before this executor was spawned; this executor re-verified (rather than re-asked) the rig facts per the plan's own instruction that the port identity be confirmed on the exact named port before any operation.

## Issues Encountered

- **`avrdude` reported `ser_open() OS error: cannot open port /dev/ttyACM1: No such file or directory` on the first upload attempt via the app's `fw --install` path**, because the Leonardo's 1200bps-touch bootloader reset causes the board to disconnect and re-enumerate under a new device number (`/dev/ttyACM0`) -- exactly the "device numbers shuffle across a replug" hazard this project's bench rules name. Resolved by re-checking `/dev/ttyACM*` after the reset, confirming the new node was the same physical board via its USB sysfs path, and directing all subsequent commands (including the successful `pio run -t upload --upload-port /dev/ttyACM0`) at the new port.
- **The app's `fw --install` route is not the right tool for flashing an unreleased in-session build.** It downloads the latest tagged GitHub release rather than the locally built `.pio/build/leonardo/firestarter_leonardo.hex`. Switched to driving PlatformIO directly (`pio run -e leonardo` then `pio run -t upload -e leonardo --upload-port /dev/ttyACM0`), which is the same build/flash path plans 01, 02, and 06 used and measured.

## User Setup Required

None -- no external service configuration required. The bench run itself needed the operator only for Task 1's four already-answered questions (seating the part, naming the shield revision, naming the port, and confirming none of the 9 was on hand).

## Next Phase Readiness

- Phase 194's software half (plans 01-06) plus this plan's no-regression silicon leg are both landed. PAGE-01 and PAGE-02 remain Complete. PAGE-03 stays open with a note citing both the 27-row record (0 of 9 on hardware, 9 of 9 on the database comparison) and this transcript (the 18's no-regression proof).
- **PAGE-03's hardware leg for the 9 previously under-sized parts is unchanged by this plan** -- still 0 of 9 on hardware. Closing it needs a bench write on one of the 9 (the ordered `W29C512` has not yet arrived, per D-10). That is out of this plan's scope and is explicitly not claimed here.
- No stubs, skipped tests, or unrun `<verify>` blocks exist in this plan's own deliverables. Both automated verify legs from `194-07-PLAN.md` (`BENCH-TARGET-OK`, `TRANSCRIPT-OK`/`REQ-HONEST`/`ROADMAP-UNTOUCHED`) ran and passed, in addition to the physical bench run itself.

## Self-Check: PASSED

`.planning/v1.39/194-w29c020-bench-transcript.md` confirmed present: `[ -f .planning/v1.39/194-w29c020-bench-transcript.md ]` succeeds. Commit `d3bf465f` confirmed present: `git log --oneline --all | grep -q d3bf465f` succeeds. `git show --stat --format='' d3bf465f` names only `.planning/REQUIREMENTS.md` and `.planning/v1.39/194-w29c020-bench-transcript.md`. Meta HEAD confirmed on `v1.39-protocol-0x05-write-correctness` (`git rev-parse --abbrev-ref HEAD`); no stray `gsd/v1.39-...` branch was created during this plan. `.planning/ROADMAP.md` confirmed untouched (`git status --short .planning/ROADMAP.md` reports nothing; `ROADMAP-UNTOUCHED` verify leg passed). `.planning/REQUIREMENTS.md`'s diff confirmed to contain only this plan's own PAGE-03 edit (`git diff .planning/REQUIREMENTS.md` before commit showed a single hunk).

---
*Phase: 194-real-page-size-reaches-the-firmware*
*Completed: 2026-09-15*
