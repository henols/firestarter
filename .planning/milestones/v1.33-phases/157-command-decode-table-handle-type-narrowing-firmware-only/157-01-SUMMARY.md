---
phase: 157-command-decode-table-handle-type-narrowing-firmware-only
plan: "01"
subsystem: firmware-measurement
tags: [avr-nm, avr-objdump, avr-gcc, platformio, offsetof, size-baseline, json_parser.c]

# Dependency graph
requires:
  - phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw
    provides: "the clean, closed tree at firestarter 1151dc4 this plan measures against"
provides:
  - "`.planning/v1.33/157-before-figures.md` — the sole authoritative before-half record for Phase 157"
  - "OD-7 discharged: sizeof(firestarter_handle_t) is 601 B on AVR at this position, with the compiler command that proves it"
  - "Nineteen corrections (C-1..C-19) and seven OD decisions recorded as superseding ROADMAP/REQUIREMENTS prose"
affects: [157-02-PLAN, 157-03-PLAN, 157-04-PLAN, 157-05-PLAN, 157-06-PLAN, 157-07-PLAN, phase-158]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "offsetof probe TU compiled twice (avr-gcc + host gcc/g++) to derive struct layout on both architectures, read back via nm --print-size"
    - "offset-resolved strings block dump (vaddr = fileoff - .text-file-offset) as the only valid oracle for ELF string duplication, never an exact-match or substring filter"

key-files:
  created:
    - .planning/v1.33/157-before-figures.md
  modified: []

key-decisions:
  - "OD-7 resolved to 601 B (not RESEARCH's 600 B) by re-deriving sizeof(firestarter_handle_t) from the actual pio run -v -e uno compiler invocation rather than a hand-assembled flag guess"
  - "A further, previously-unflagged discrepancy recorded: native sizeof(firestarter_handle_t) measures 656 B, not RESEARCH's 655 B -- mathematically required by the struct's 8-byte alignment from its trailing function-pointer members"

patterns-established:
  - "Before-figures records for this milestone follow the 155/156 skeleton: git anchors, WARM AVR figures, per-symbol ledger, string/offset evidence, test/gate baselines, reference-carrier applicability, one-sided size gate, coverage ceilings, corrections index"

requirements-completed: []  # This plan captures pre-change measurements only; DECODE-01..07 are discharged across plans 02-07, not by plan 01 alone.

coverage:
  - id: D1
    description: "Before-figures record captured on a tree proven clean before and after, superseding nineteen stale ROADMAP/REQUIREMENTS figures"
    verification:
      - kind: other
        ref: ".planning/v1.33/157-before-figures.md (every figure carries its verbatim command); git -C firestarter status --porcelain empty before and after"
        status: pass
    human_judgment: false

duration: 40min
completed: 2026-08-23
status: complete
---

# Phase 157 Plan 01: Before-Figures Capture Summary

**Captured and committed the sole authoritative before-half record for Phase 157 — the eleven-stub ledger (exactly 1012 B), the two 118 B key-string vaddr blocks, both architectures' compiler-derived struct offsets, OD-7's resolved `sizeof` figure (601 B, not 600 B), and nineteen corrections to stale ROADMAP/REQUIREMENTS prose — on a tree proven clean before and after every measurement.**

## Performance

- **Duration:** ~40 min
- **Tasks:** 2 (measurement, then write + commit the record)
- **Files modified:** 1 (`.planning/v1.33/157-before-figures.md`, created)

## Accomplishments

- Reproduced the phase's stated WARM baseline exactly on all three AVR targets, twice in the same
  session (once before, once after the size-gate's own cold `--rebuild`): `uno` 24234/1567,
  `uno328pb` 24282/1573, `leonardo` 26378/2008. Leonardo Caterina headroom 2294 B.
- Closed the eleven-stub ledger at exactly **1012 B** and confirmed the five zero-cost siblings
  (`get_r1`, `get_r2`, `get_rev`, `get_rw_pin`, `get_vpp_pin`) absent from the `uno` symbol table —
  DECODE-01's entire proof, measured directly rather than quoted.
- Recorded the key-string duplication as two offset-resolved 118 B vaddr blocks on both `uno` and
  `leonardo`, and reproduced both forbidden `strings` oracles with their wrong numbers (`awk
  '$2=="flags"'` → 1, truth 2; substring `grep -c flags` on `leonardo` → 4).
- Derived struct offsets on both AVR and native from a compiled `offsetof` probe TU, confirming the
  ROADMAP's AVR claim ("offsets 3–37, below `data_buffer` at 38") exactly and showing the native
  table diverges at every field from `protocol` down.
- **Discharged OD-7**: re-derived `sizeof(firestarter_handle_t)` from the real compiler invocation
  captured via `pio run -v -e uno` (after a targeted clean to force recompilation) — the result is
  **601 B**, matching `155-after-figures.md` and superseding `157-RESEARCH.md`'s probe-measured
  600 B.
- Proved the pre-existing BASE-01 size-gate red masks nothing: `check_size_baseline.py --policy
  merge05 --rebuild` fails with exactly two lines, both native case counts, no AVR flash/RAM leg.
- Proved the reference patch does **not** apply cleanly at this position: all four
  `git apply --check -C{0,1,2,3}` runs fail identically at `src/json_parser.c:76`, and
  `patch --dry-run -F3` fails hunk #3 alone while #4–#7 succeed with offsets — plan 02's
  implementation is confirmed to be a hand-port.
- Recorded all nineteen corrections (C-1 through C-19) and all seven OD decisions (OD-1 through
  OD-7), each with the alternative declined and that alternative's cost, as superseding the
  ROADMAP/REQUIREMENTS prose they correct.

## Task Commits

1. **Task 1: Assert the tree is unchanged, then measure every irrecoverable pre-change figure** —
   no commit (measurement only; no tracked file edited).
2. **Task 2: Write and commit the before-figures record** — `b9faaa6b`
   (`docs(157-01): capture the pre-change before-figures and the nineteen ROADMAP corrections`)

## Files Created/Modified

- `.planning/v1.33/157-before-figures.md` — the phase's sole authoritative before-half record;
  every figure carries the verbatim command that produced it.

## Decisions Made

- **OD-7 resolved to 601 B**, not RESEARCH's 600 B: re-derived from the actual `pio run -v -e uno`
  compiler invocation rather than a hand-assembled flag set, matching `155-after-figures.md`
  exactly.
- Recorded a further discrepancy beyond OD-7's stated scope: native `sizeof(firestarter_handle_t)`
  measures 656 B, not RESEARCH's 655 B — 656 is the only value consistent with the struct's own
  8-byte alignment requirement (its trailing function-pointer members force `sizeof` to be a
  multiple of 8; 655 is not). This does not change the AVR-only −5 B RAM ceiling.

## Deviations from Plan

None — plan executed exactly as written. One additional measured discrepancy was found and
recorded beyond the plan's own pre-identified C-17/C-18/C-19 (the native `sizeof` figure above);
this is documentation of an honest measurement, not a deviation from the plan's instructions,
which explicitly call for recording what is measured rather than what is expected.

## Issues Encountered

- `pio test -e native -v` and `pio run -v -e native` do not print per-file compiler invocation
  lines the way `pio run -v -e uno` does (native test builds are silent even with `-v`). Worked
  around by deleting the cached `.pio/build/native/src/json_parser.o` object and re-running, and
  by compiling a standalone `sizeof` probe with the native env's own declared flags
  (`-std=gnu++17 -DMONITOR_SPEED=250000 -DHARDWARE_REVISION -DDEV_TOOLS
  -DRURP_BOARD_NAME=\"native\"`) instead of trying to scrape a verbose native build log.
- The size gate's `--rebuild` flag cold-cleans all three AVR `.pio/build/<env>` directories as a
  side effect; re-ran `pio run -e uno -e uno328pb -e leonardo` immediately afterward and confirmed
  all three targets reproduced the exact §2 figures, with `git status --porcelain` empty
  throughout.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `.planning/v1.33/157-before-figures.md` is committed and is the authoritative before-side
  reference for plans 02 (the field table, −890 B), 03 (the narrowing, −258 B / −5 B), 04
  (DECODE-05's fail-closed cases), 05 (the strobe-cap and round-trip cases), 06 (DECODE-07's
  `switch` re-measurement), and 07 (the after-figures record and requirement closure).
- No blockers. `firestarter` HEAD is unchanged at `1151dc4`; `git -C firestarter status
  --porcelain` is empty; no `.rej`/`.orig` file exists anywhere under `/workspaces/firestarter`.
- Plan 02 should read §3 (the eleven-stub ledger and its "why" paragraph), §6 (struct offsets and
  OD-7), §10 (corrections C-1, C-2, C-3, C-7, C-9, C-11, C-12, C-14, C-17, C-19), and §11 (OD-1,
  OD-2, OD-3) before authoring the field table.

---
*Phase: 157-command-decode-table-handle-type-narrowing-firmware-only*
*Completed: 2026-08-23*
