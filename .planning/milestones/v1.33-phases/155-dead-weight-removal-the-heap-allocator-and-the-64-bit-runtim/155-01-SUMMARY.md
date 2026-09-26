---
phase: 155-dead-weight-removal-the-heap-allocator-and-the-64-bit-runtim
plan: "01"
subsystem: firmware-size-measurement
tags: [avr-nm, avr-objdump, platformio, symbol-table, disassembly-attribution, size-baseline]

requires: []
provides:
  - ".planning/v1.33/155-before-figures.md — authoritative before-figures record for DEAD-01/02/03"
  - "Independently re-measured three AVR flash/RAM pairs, full 7-symbol heap table, full 11-symbol 64-bit table, disassembly-derived sole-caller attribution"
  - "Corrected derivations for the RAM headroom sentence, the 64-bit symbol count, the 'same statement' claim, and the -650/-714 split"
affects: ["155-02", "155-04", "155-05", "155-06"]

tech-stack:
  added: []
  patterns:
    - "Disassembly call/jmp attribution script (session-scratch-only, not committed) to prove sole-caller status mechanically rather than by reading source"
    - "Before-figures record convention copied from .planning/v1.33/baseline-pre-sweep.md: every number carries its verbatim producing command"

key-files:
  created:
    - .planning/v1.33/155-before-figures.md
  modified: []

key-decisions:
  - "Built the multi-phase preserved reference branch (wip/v1.33-size-reduction-survey-preserved) in an isolated git worktree to check whether it could supply the -650/-714 split's function-body deltas independently; confirmed it bundles later phases' reductions too (measures -2938 B vs this phase's -1366 B), so it cannot isolate the Phase-155-only deltas -- those two figures are instead quoted from 155-RESEARCH.md's own [VERIFIED: pio run] measurement, with the reason stated in the record, rather than fabricated or silently omitted"
  - "Recorded 'shared heap-and-stack headroom' (473/467/544 B) rather than 'free RAM available to the allocator' per RESEARCH's C-3 correction, since ram_used counts .data/.bss only and the AVR stack grows down into that region"

requirements-completed: [DEAD-01, DEAD-02, DEAD-03]

coverage:
  - id: D1
    description: "Committed before-figures record capturing flash/RAM, symbol tables, sole-caller attribution and corrected derivations, all measured this session on the unedited tree"
    requirement: "DEAD-01"
    verification:
      - kind: other
        ref: "avr-nm heap-set and 64-bit-set match counts (7 and 11) reproduced on all three ELFs; text-check grep over the committed file for all 20 key figures"
        status: pass
    human_judgment: false
  - id: D2
    description: "Full 11-symbol 64-bit table with both the 438 B named-subset and 528 B contiguous-blob totals recorded"
    requirement: "DEAD-03"
    verification:
      - kind: other
        ref: "avr-nm --print-size --size-sort -C .pio/build/uno/firestarter_uno.elf, arithmetic sum verified against both totals"
        status: pass
    human_judgment: false
  - id: D3
    description: "Corrected RAM headroom derivation (473/467/544 B, 'shared heap-and-stack headroom') replacing the double-counted 1115 B claim"
    requirement: "DEAD-02"
    verification:
      - kind: other
        ref: "pio run -e {uno,uno328pb,leonardo} ram_used matched against avr-nm handle/tokens sizes"
        status: pass
    human_judgment: false

duration: ~40min
completed: 2026-08-23
status: complete
---

# Phase 155 Plan 01: Before-Figures Record Summary

**Independently re-measured every pre-change flash/RAM figure, the full 7-symbol heap table and 11-symbol 64-bit table with disassembly-proven sole-caller attribution, then committed a corrected-derivation record before touching a single line of firmware source.**

## Performance

- **Duration:** ~40min
- **Completed:** 2026-08-23
- **Tasks:** 2/2 completed
- **Files modified:** 1 created (`.planning/v1.33/155-before-figures.md`)

## Accomplishments

- Rebuilt all three AVR targets (`uno`, `uno328pb`, `leonardo`) warm and confirmed flash/RAM matched the expected figures (26026/1575, 26074/1581, 28170/2016) exactly, with capacities 32768/2048/2048/2560 — no toolchain or tree drift since research.
- Captured the full `avr-nm --print-size --size-sort -C` symbol listing for all three ELFs; confirmed the heap-set match count is exactly 7 and the 64-bit-set match count is exactly 11 on every target; confirmed `realloc`/`calloc` are ABSENT by explicit check.
- Computed both contiguous spans on `uno` from raw addresses: the 64-bit blob `0x6036`–`0x6246` (528 B) directly abuts the heap blob `0x6246`–`0x6490` (586 B), one 1114 B contiguous region.
- Wrote and ran a throwaway `avr-objdump -d` call/jmp attribution script (session scratch, not committed) that mechanically confirmed `malloc` and `free` each have exactly one caller (`mem_util_blank_check`), and five of the eleven 64-bit symbols (`__muldi3`, `__adddi3`, `__lshrdi3`, `__udivdi3`, `__umulsidi3`) each have exactly one user-code caller (`rurp_read_voltage_mv`) — reproducing `155-RESEARCH.md`'s claimed attribution independently rather than trusting it.
- Ran both native suites sequentially (172/172 each, 17 suites), the system-python pytest suite (323 passed), and `check_build_warnings.py` (PASS, exit 0) on the unedited tree.
- Computed the +478/+476/+540 B baseline-staleness arithmetic against `scripts/baseline/size_baseline.json` and quoted its own `meta` block's admission verbatim.
- Wrote `.planning/v1.33/155-before-figures.md` with 12 sections covering git anchors, flash/RAM, heap set, 64-bit set, sole-caller attribution, function/object sizes, the corrected RAM derivation, the pre-change defect, the "same statement" correction, the unverified −650/−714 split, baseline staleness, and test/gate baselines — then committed it as the sole file in one meta-repo commit.
- Confirmed the `firestarter` tree was provably unedited throughout: `git status --porcelain` and `git diff --name-only HEAD` both empty before and after.

## Task Commits

1. **Task 1: Assert the tree is unchanged, then capture every irrecoverable pre-change measurement** — no commit (measurement-only task; nothing was edited)
2. **Task 2: Write and commit the AUTHORITATIVE before-figures record** — `e0926e53` (docs)

**Plan metadata:** committed together with this SUMMARY per the final-commit step (see STATE.md/ROADMAP.md update below).

## Files Created/Modified

- `.planning/v1.33/155-before-figures.md` — authoritative before-figures record for Phase 155's DEAD-01/DEAD-02/DEAD-03 half; every figure carries its producing command.

## Decisions Made

- **The multi-phase preserved reference branch cannot supply the −650/−714 split's component deltas.** Built `wip/v1.33-size-reduction-survey-preserved` in an isolated `git worktree` (never touching the tracked `firestarter` tree) to check; it measures `uno` flash at 23088 B (a −2938 B delta from this record's 26026 B baseline), matching STATE.md's combined Phases-155-158 figure — confirming it bundles DEDUP/DECODE/LAND reductions, not just DEAD-01/02/03's. The two function-body deltas (−204, −58) needed for that split are instead quoted from `155-RESEARCH.md`'s own `[VERIFIED: pio run]` measurement, with the reason stated explicitly in §10 of the record, since this before-only plan is prohibited from producing a Phase-155-only post-change build itself.
- **"Shared heap-and-stack headroom", not "free RAM"** — used throughout §7, per RESEARCH's C-3 correction, because `ram_used` counts `.data`/`.bss` only and the AVR stack grows down into the same region during every operation.

## Deviations from Plan

None — plan executed exactly as written. Both tasks' acceptance criteria were met without needing any Rule 1-4 auto-fix: the tree matched every expected figure on the first measurement, and no blocking issue arose.

## Issues Encountered

None. The one open question — how to source the −650/−714 split's function-body deltas without a post-change build — was resolved by building the multi-phase preserved reference in an isolated worktree, confirming it was unsuitable, and citing the narrower, already-verified figure from research with the reason stated (see Decisions above and record §10).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

`.planning/v1.33/155-before-figures.md` is committed and holds every figure plans 02, 04, 05 and 06 will need: the 7/11 symbol match counts for plan 02's gate, the sole-caller attribution plans 01/03 (DEAD-01) depend on, the corrected RAM derivation for DEAD-02, and the 438 B/528 B pair for DEAD-03. The `firestarter` tree remains byte-for-byte unedited at `FW_PRE_SHA` `2ad5b322a37ba4a88afd09cc946f5c4114e51483` — plan 02 (the mechanical gate) can proceed without any further before-state capture. No blockers.

---
*Phase: 155-dead-weight-removal-the-heap-allocator-and-the-64-bit-runtim*
*Completed: 2026-08-23*

## Self-Check: PASSED

- FOUND: `.planning/v1.33/155-before-figures.md`
- FOUND: commit `e0926e53` (`git log --oneline --all | grep e0926e53`)
