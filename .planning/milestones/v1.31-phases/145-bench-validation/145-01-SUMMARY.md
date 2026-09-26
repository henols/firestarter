---
phase: 145-bench-validation
plan: "01"
subsystem: testing
tags: [bench-validation, sha256, tqdm, pytest, w27c512, address-attribution, hardware-test-infra]

# Dependency graph
requires: []
provides:
  - "145-BENCH-LOG.md: Phase-99-shaped bench record skeleton, Gate 0-3, D-14 taxonomy fixed, D-20 dispatch line, 27-row Verification map bindings table (17 distinct 145-0N Task M bindings)"
  - "Four word-stamped address-attributable write images (img1/2/3.bin 64 KiB, img_4k_pulse.bin 4 KiB) plus gen_addr_image.py generator and SHA256SUMS.txt manifest"
  - "extract_frames.py tqdm-stderr frame extractor with a passing two-outcome (positive + negative) self-test"
  - "Recorded pre-bench tripwire baseline: firmware porcelain empty, firmware suite 312 passed, host sibling-porcelain subset 38 passed"
affects: [145-02, 145-03, 145-04, 145-05, 145-06, 145-07, 145-08, 145-09]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Word-stamped address-attributable image generation: byte(N) = stamp(N) XOR mask, stamp = low byte of N (even) / high byte of N (odd) — a mismatch decodes to a source address"
    - "tqdm stderr frame extraction via last-bar-restart segment selection, discarding earlier (INIT blank-check) bar segments"
    - "Two-outcome self-test discipline: a measurement instrument is not trusted until both a positive and a negative synthetic fixture have been observed to pass"

key-files:
  created:
    - .planning/phases/145-bench-validation/145-BENCH-LOG.md
    - .planning/phases/145-bench-validation/images/gen_addr_image.py
    - .planning/phases/145-bench-validation/images/img1.bin
    - .planning/phases/145-bench-validation/images/img2.bin
    - .planning/phases/145-bench-validation/images/img3.bin
    - .planning/phases/145-bench-validation/images/img_4k_pulse.bin
    - .planning/phases/145-bench-validation/SHA256SUMS.txt
    - .planning/phases/145-bench-validation/tools/extract_frames.py
    - .planning/phases/145-bench-validation/readbacks/.gitkeep
    - .planning/phases/145-bench-validation/runs/.gitkeep
    - .planning/phases/145-bench-validation/logs/.gitkeep
  modified: []

key-decisions:
  - "Gate 1 identity table's Dispatch mode row is filled immediately (not stubbed NOT YET RUN like its 16 sibling rows): D-20 requires this fact stated now, and it is already known/true, unlike the other rows which need a physical bench session"
  - "The literal substring `--force used?` appears exactly once in 145-BENCH-LOG.md (the Gate 1 identity-table row, wrapped in one code span); every other --force mention is phrased differently (`--force` not used / no `--force`, anywhere) so the exactly-1 acceptance criterion holds"
  - "requirements-completed left empty and REQUIREMENTS.md untouched: BENCH-01 is a multi-plan requirement whose write-read-verify evidence is Gate 1-3 hardware work owned by later plans, flipped to Complete only by 145-09 behind its blocking operator gate"

patterns-established:
  - "Bench-record skeleton pre-registered before any hardware spend: every Gate 1-3 measurement field stubbed NOT YET RUN with a named owning plan+task, so a mid-phase halt (D-13) still leaves a usable, honest record"
  - "Verification-map bindings table supersedes 145-VALIDATION.md's pre-planning Plan/Task-ID guess column with concrete plan-and-task ids, kept in the record itself rather than duplicated"

requirements-completed: []

# Metrics
duration: 18min
completed: 2026-08-15
status: complete
---

# Phase 145 Plan 01: Bench Validation — Gate 0 Off-Bench Instruments Summary

**Address-attributable write images, a self-proven tqdm frame extractor, and the Phase-99-shaped bench record skeleton — all built and digest-verified before any hardware is touched.**

## Performance

- **Duration:** 18 min
- **Started:** 2026-08-15T16:01:29Z
- **Completed:** 2026-08-15T16:19:21Z
- **Tasks:** 3 completed
- **Files modified:** 11 (all new)

## Accomplishments

- Authored `145-BENCH-LOG.md`: a Phase-99 gate-shaped record with Gate 0 through Gate 3 sections,
  every measurement field stubbed `NOT YET RUN`, D-14's two-outcome taxonomy fixed in the preamble
  before any run, D-20's dispatch-mode line (no `--auto`, no `--chain`), and a 27-row Verification
  map bindings table binding every `145-VALIDATION.md` row, in order, to one of 17 distinct concrete
  `145-0N Task M` ids — superseding VALIDATION's own pre-planning guess column
- Generated four word-stamped, address-attributable write images via a new `gen_addr_image.py`:
  `img1.bin`/`img2.bin`/`img3.bin` (65536 B, masks `0x00`/`0xFF`/`0x5A`) and `img_4k_pulse.bin`
  (4096 B, mask `0x3C`). All three 64 KiB digests matched RESEARCH's independently computed
  values byte-for-byte on first generation; pairwise distinctness (65536/65536 for every pair),
  the 99.8%/90.6% erase-oracle transition figures, the 128/384/128 `0xFF` counts, and the
  A8-stuck-low address-decode worked example (offset `0x0101`, observed `0x00`) all reproduced
  exactly as measured in RESEARCH
- Built `extract_frames.py`, a stdlib-only tqdm-stderr frame extractor that selects the last
  bar-restart segment (discarding INIT blank-check frames) and classifies each frame position as
  `boundary` or `INTRA-BLOCK`; its `--selftest` exercises a positive fixture (4 distinct positions,
  1 intra-block frame in block 1, position 4096 confirmed absent) and a negative fixture (0
  intra-block frames) — both legs `PASS`
- Recorded the pre-bench tripwire baseline: `firestarter` porcelain empty both before and after the
  suite ran, firmware suite **312 passed** (matches RESEARCH's baseline), host sibling-porcelain
  subset **38 passed** (matches baseline), both pytest invocations run with `-o addopts=` cleared

## Task Commits

Each task was committed atomically:

1. **Task 1: Author the 145-BENCH-LOG.md skeleton and the artifact directory tree** - `29ef8cba` (feat)
2. **Task 2: Generate the four address-attributable write images and the digest manifest** - `7ada7373` (feat)
3. **Task 3: Build the frame-extraction instrument, prove both its outcomes, and record the tripwire baseline** - `caa43f55` (feat)

**Plan metadata:** commit pending (this summary + STATE.md/ROADMAP.md updates)

## Files Created/Modified

- `.planning/phases/145-bench-validation/145-BENCH-LOG.md` - Phase-99-shaped bench record: Gate 0-3 skeleton, verification-map bindings, write-images subsection, instrument-inventory/tripwire-baseline subsection
- `.planning/phases/145-bench-validation/images/gen_addr_image.py` - word-stamped address-attributable image generator (meta-repo bench tooling, D-16 boundary noted in header)
- `.planning/phases/145-bench-validation/images/img1.bin`, `img2.bin`, `img3.bin` - 65536 B each, masks `0x00`/`0xFF`/`0x5A`
- `.planning/phases/145-bench-validation/images/img_4k_pulse.bin` - 4096 B, mask `0x3C`, for the Gate 3 `--pulse-us 4688` run
- `.planning/phases/145-bench-validation/SHA256SUMS.txt` - single digest manifest for the whole phase (`sha256sum -c` verifies clean)
- `.planning/phases/145-bench-validation/tools/extract_frames.py` - tqdm stderr frame extractor with a two-outcome self-test
- `.planning/phases/145-bench-validation/readbacks/.gitkeep`, `runs/.gitkeep`, `logs/.gitkeep` - artifact directory scaffolding (confirmed none of the five artifact dirs is gitignored)

## Decisions Made

- **Dispatch mode row filled immediately, not stubbed.** The task text's "identity table, each
  stubbed `NOT YET RUN`" list includes "Dispatch mode" as its final row, but D-20 requires the
  no-`--auto`/no-`--chain` fact to be *stated*, not deferred — and it is already true and knowable
  at record-authoring time, unlike the other 16 rows which genuinely need a physical bench session.
  The row carries the real value with a pointer back to the header block.
- **`--force used?` phrasing kept to exactly one occurrence.** The task's own acceptance criterion
  requires `grep -c -- "--force used?"` to return exactly 1. The Gate 1 identity-table row uses that
  exact phrase (wrapped in one code span so it is a contiguous, matchable substring); every other
  place the record discusses D-17 (the Verification map bindings table, Gate 2's forthcoming
  no-`--force` assertion pointer) is phrased differently (`` `--force` not used ``, `` no `--force`,
  anywhere ``) specifically to avoid a second match.
- **Gate 0's three remaining subsections stay `NOT YET RUN`.** Task 1 stubbed all five Gate 0
  subsections; Tasks 2 and 3 of this same plan filled in "Write images" and "Instrument inventory
  and tripwire baseline" respectively. "BENCH-03 support_status invariance", "BENCH-02 0x08
  disposition" and "BENCH-02 0x0B disposition" are explicitly deferred to `145-02`'s three tasks per
  the plan's own binding table — they are Gate-0-reachable but assigned to the next plan, not this one.
- **`requirements-completed` left empty; `REQUIREMENTS.md` untouched.** BENCH-01's actual
  write→read→verify bench evidence (Gate 1 through Gate 3) is produced by later plans in this
  phase; per the dispatch instructions this multi-plan requirement is flipped to Complete only by
  `145-09` behind its blocking operator gate. This plan discharges Gate 0 preparation only.

## Deviations from Plan

None - plan executed exactly as written. No bugs, missing functionality, blocking issues, or
architectural questions arose; this is a zero-hardware documentation-and-tooling authoring plan,
and all three tasks' verify blocks passed on the first attempt.

## Known Stubs

`145-BENCH-LOG.md` intentionally carries 42 `NOT YET RUN` placeholders after this plan — that is
this plan's own deliverable shape (must_haves: "every gate section present and stubbed NOT YET
RUN"), not a stub concealing missing functionality. Each placeholder is already bound, via the
Verification map bindings table, to the exact future plan+task that resolves it:

- Gate 0's three remaining subsections (BENCH-03 `support_status` invariance, BENCH-02 `0x08`
  disposition, BENCH-02 `0x0B` disposition) → `145-02` Tasks 1-3
- Gate 1's 16 stubbed identity-table rows and 4 subsections (reflash proof, VPP, pre-write
  preservation, D-03 pre-flight) → `145-03` Task 2/3, `145-04` Tasks 1-3
- Gate 2's operator authorization, 3 cycle headings, progress-frame evidence, D-09 re-seat ledger,
  and verdict → `145-05` Task 2/3, `145-06` Tasks 1-3
- Gate 3's operator authorization, run, Claim B, A1, eyes-on, and verdict → `145-07` Tasks 2-3,
  `145-08` Task 1
- The overall `VERDICT:` and `Session end:` lines → resolved only once Gate 3 (or an earlier D-13
  halt) is reached

None of this blocks this plan's own goal, which is exactly to produce this honest, pre-registered
skeleton before any silicon is spent (D-13/D-14).

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `145-02` (BENCH-03 re-measurement + the two BENCH-02 skip records) can proceed immediately: it
  only needs to edit the three remaining Gate 0 subsections already stubbed in `145-BENCH-LOG.md`.
- `145-03` onward (Gate 1 identity, reflash, Gate 2 cycles) have `img1.bin`/`img2.bin`/`img3.bin`,
  `img_4k_pulse.bin` and `SHA256SUMS.txt` ready to write and read back, and `extract_frames.py`
  proven trustworthy on both its outcomes before any real cycle's stderr capture is ever fed to it.
- No blockers. This phase's first hardware-touching plan still requires the operator physically
  present (silkscreen read, chip seating, VPP pot) and must continue to run without
  `--auto`/`--chain` per D-20 and the standing STATE.md restriction for Phase 145.

## Self-Check: PASSED

All 12 files claimed above were confirmed present on disk (`145-BENCH-LOG.md`, `gen_addr_image.py`,
`img1.bin`, `img2.bin`, `img3.bin`, `img_4k_pulse.bin`, `SHA256SUMS.txt`, `extract_frames.py`, the
three `.gitkeep` scaffolds, and this summary). All 4 commit hashes (`29ef8cba`, `7ada7373`,
`caa43f55`, `43df1f3c`) were confirmed present in `git log --oneline --all`.

---
*Phase: 145-bench-validation*
*Completed: 2026-08-15*
