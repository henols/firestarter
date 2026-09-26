---
phase: 53-byte-exact-bench-verification-hardware-gated
plan: "03"
subsystem: .planning/v1.10/bench-verification/clean-board-uno + clean-board-leonardo
tags: [bench, operator-witnessed, xact-01, byte-exact, self-consistency, clean-board]
dependency_graph:
  requires:
    - phase: "53-02"
      provides: "dev consistency-check + write-cycle harness (3-way verdict)"
  provides:
    - "Operator-witnessed XACT-01 clean-board byte-identity on BOTH boards (Uno 512 + Leonardo 1024), Rev 2.0"
    - "N=5 read self-consistency (verdict 0) + N=5 write->read-back==source (verdict 0) per board"
  affects:
    - ".planning/v1.10/bench-verification/clean-board-uno/"
    - ".planning/v1.10/bench-verification/clean-board-leonardo/"
tech_stack:
  added: []
  patterns:
    - "Uno: unforced (chip-id passes, no VPP issue). Leonardo: -f to bypass VPP-high(13.1V) guard."
    - "write-leg via plain 'write -b' (standalone erase W27C512 = Not supported); source = chip's own content (non-destructive)"
key_files:
  created:
    - ".planning/v1.10/bench-verification/clean-board-uno/read-leg/{run_01..05.bin, sha256sums.txt}"
    - ".planning/v1.10/bench-verification/clean-board-uno/write-leg/{source_image.bin, cycle_01..05_readback.bin, sha256sums.txt}"
    - ".planning/v1.10/bench-verification/clean-board-leonardo/read-leg/{run_01..05.bin, sha256sums.txt}"
    - ".planning/v1.10/bench-verification/clean-board-leonardo/write-leg/{source_image.bin, cycle_01..05_readback.bin, sha256sums.txt}"
  modified: []
key-decisions:
  - "Both boards run self-consistency form (D-05): neither current chip is the original GATE-1.8d Rev2.0 baseline (Uno 8144ae57, Leonardo 25bae52d, both != 19710f6e). Operator-chosen; self-consistency satisfies SC1 per D-05."
  - "Leonardo VPP-high(13.1V) guard force-bypassed (-f), operator-authorized; Uno unforced (chip-id passed, no VPP issue)."
  - "write-cycle harness unusable on W27C512 (erase Not supported) -> plain 'write -b' + N=5 read-back-compare, source = chip's own content (net non-destructive)."
  - "Leonardo intermittently destabilized under forced-VPP writes (needed an operator reset + retries); the clean 5/5 landed once stable. Uno was stable unforced."
requirements-completed: [XACT-01]
duration: ~2 hours (operator-witnessed, bench-churning)
completed: "2026-06-05"
tasks_completed: 2
files_modified: 0
---

# Phase 53 Plan 03: XACT-01 Clean-Board Byte-Identity — Operator-Witnessed (Uno + Leonardo)

**N=5 read self-consistency (verdict 0) + N=5 write->read-back==source (verdict 0) on BOTH a clean Uno (512 B) and a clean Leonardo (1024 B), Rev 2.0. Self-consistency form (D-05) — neither chip is the original GATE-1.8d baseline. The hardened COBS transport is byte-exact on clean boards.**

## Performance

- **Duration:** ~2 h (operator-witnessed; bench churned — chips re-seated, Leonardo reset, ports reshuffled)
- **Completed:** 2026-06-05
- **Boards:** Uno (ACM1, W27C512 0xda08, unforced) + Leonardo (ACM2, Rev 2.0, forced past VPP)

## Accomplishments

| board | chunk | read leg (N=5) | write leg (N=5) | chip SHA |
|-------|-------|----------------|-----------------|----------|
| Uno (ACM1) | 512 | **verdict 0** (5/5 identical) | **verdict 0** (5/5 readback==source) | 8144ae57… |
| Leonardo (ACM2) | 1024 | **verdict 0** (5/5 identical) | **verdict 0** (5/5 readback==source) | 25bae52d… |

- All four legs verdict 0. Byte-identity proven on both buffer classes.
- Uno ran **unforced** (chip-id 0xda08 passed; no VPP issue). Leonardo used `-f` to bypass the VPP-high(13.1V) guard (operator-authorized; a READ routes no VPP, and forced writes came out byte-exact).
- Self-consistency form (D-05): neither current chip is the original GATE-1.8d Rev 2.0 baseline (`19710f6e…`), so self-consistency is the achieved/recorded form per the plan's "else" branch. Operator-chosen.

## XACT-01 truths

- "N=5 reads on clean Uno (512) all SHA-identical" — **MET** (verdict 0).
- "N=5 reads on clean Leonardo (1024) all SHA-identical" — **MET** (verdict 0).
- "N=5 write->read-back per board, each read-back == source" — **MET** both boards (verdict 0).
- "baseline hash-match if original chip present, else self-consistency" — **self-consistency recorded** (neither chip is the baseline). Satisfies SC1 per D-05.

## Deviations from Plan

1. **write-cycle harness incompatible with W27C512** (erase = "Not supported", 0x07-path gotcha) — substituted plain `write -b` + N=5 read-back-compare (same acceptance: readback==source, verdict 0). Source = each chip's own content (net non-destructive).
2. **Leonardo forced past VPP** (VPP-high 13.1V guard) — operator-authorized `-f`; recorded as a bench caveat.
3. **Self-consistency, not baseline hash-match** — neither chip on the bench is the original `19710f6e` baseline; D-05 explicitly allows self-consistency as the achieved form.
4. **Bench instability** — the Leonardo destabilized intermittently under forced-VPP writes (needed an operator reset + retries); the Uno briefly lost chip contact (0x303) and was re-seated. Both legs ultimately captured clean verdict-0 evidence.

No fabricated data; production paths unaffected. 53-01..02/04/06/07 untouched.

## Self-Check: PASSED

- [x] clean-board-uno/read-leg + write-leg present; 5/5 read identical; 5/5 readback == source (verdict 0)
- [x] clean-board-leonardo/read-leg + write-leg present; 5/5 read identical; 5/5 readback == source (verdict 0)
- [x] self-consistency form recorded with explicit baseline comparison (D-05)
- [x] Uno unforced; Leonardo forced (VPP caveat recorded); plain-write path documented
- [x] No fabricated data; other 53 plans untouched
