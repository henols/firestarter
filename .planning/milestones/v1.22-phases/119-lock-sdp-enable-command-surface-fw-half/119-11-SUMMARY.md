---
phase: 119-lock-sdp-enable-command-surface-fw-half
plan: "11"
subsystem: docs-planning
tags: [meta, bench-measurement, lock-06, timing, three-board, sdp, page-load, validation-ceiling]

# Dependency graph
requires:
  - phase: 119-lock-sdp-enable-command-surface-fw-half
    plan: "08"
    provides: "The worst-per-byte page-load interval tracker (MSG_INFO_PAGE_LOAD_WORST_US, 0x62), reachable on both the completing and the aborting exit"
  - phase: 119-lock-sdp-enable-command-surface-fw-half
    plan: "10"
    provides: "LOCK-06 already closed on the flash axis; 119-NONREGRESSION.md's flash/RAM figures to cross-reference"
provides:
  - "119-MEASUREMENT.md — the three-board bench record of the page-load worst-interval and SDP-unlock duration, with full per-board provenance"
  - "A structural finding (grounded in source, not guessed): a page-boundary-crossing write folds the prior page's completion-poll-plus-readback-verify latency into the reported worst interval, making it not directly comparable to a clean within-page figure"
  - "Two new SDP-unlock duration datapoints (Uno 412us, uno328pb 424us) alongside F-118-01's Leonardo 572us (this run: 568us)"
affects: [122]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Explaining an anomalous measured value via direct source-code control-flow tracing (page_load_previous_us update ordering) rather than re-running hardware to probe it, honoring the plan's 'exactly one write per board' constraint"
    - "Recording a divergence from the plan's own anticipated flow (Leonardo's write succeeding rather than aborting) as an honest finding rather than smoothing it into the expected narrative"

key-files:
  created:
    - .planning/phases/119-lock-sdp-enable-command-surface-fw-half/119-MEASUREMENT.md
  modified: []

key-decisions:
  - "Leonardo's 6080us worst-interval figure is NOT compared apples-to-apples against the Uno/uno328pb's 84us/88us figures in the document -- traced through eeprom28c_write_execute's source (eeprom_28c.cpp:622-655) to show the Leonardo run crossed the page-1-to-page-2 boundary (both pages' completion poll + readback verify succeeded), which folds the ENTIRE page-1 completion-poll-plus-64-byte-readback-verify latency into that one reported interval -- a structurally different, larger quantity than a clean within-page set_data-to-set_data interval. The Uno-class boards aborted during page 1's own verify step, so their figures are clean within-page numbers, directly comparable to the 100us/byte datasheet max."
  - "Did NOT re-run any board to further probe why Leonardo's write succeeded on an empty socket while Uno/uno328pb's failed identically -- the plan forbids repeated sweeps/extra hardware commands beyond one write per board, so the raw logs are reported verbatim with the structural explanation and no further hardware-based root-causing was attempted."
  - "uno328pb needed no retry -- the single attempt completed cleanly (no timeout), so D-18 item 2's retry allowance was not exercised; its 'never trust N=1' caution is applied instead to how the single datapoint is read (one data point, not a proven-stable board figure), not to whether a mechanical retry was triggered."
  - "Recorded the Leonardo-vs-Uno-class divergence explicitly as the plan's own anticipated flow (empty-socket abort at the first page) not holding on every board this run -- Leonardo's write reported fully successful, which the plan text did not predict as guaranteed. Attributed to `-b` skipping the blank check entirely (unlike 118-07's plain `--force`), leaving only the completion-poll/readback-verify gate, which read a floating bus differently on the two MCU families."
  - "Cross-board caution applied per D-18 item 4: uno328pb's outcome (identical failing address, identical expected/observed byte pair, comparable worst-interval to Uno's) is attributed to it being an ATmega328P/PB board like the Uno, NOT to 328PB-specific silicon -- the actual divergence observed is Leonardo (ATmega32U4) vs. Uno-class (ATmega328P/PB), an architecture-class difference."

requirements-completed: []

coverage:
  - id: D1
    description: "Port identity verified by command for all three candidate ports before any board was driven, and the port-to-board map matched Phase 118's recorded map exactly (re-verified, not assumed)"
    verification:
      - kind: manual_procedural
        ref: "firestarter -p /dev/ttyACM0|/dev/ttyACM1|/dev/ttyUSB0 -v fw -- controller: leonardo/uno/uno328pb respectively, captured verbatim in 119-MEASUREMENT.md section 2a"
        status: pass
    human_judgment: false
  - id: D2
    description: "All three envs built and matched 119-NONREGRESSION.md section 4 exactly before upload; firmware SHA 0048b3d and branch recorded as build identity"
    verification:
      - kind: unit
        ref: "pio run -- 3/3 SUCCESS, Leonardo 26072/28672, Uno 23932/32256, uno328pb 23976/32384 -- exact match to 119-NONREGRESSION.md section 4"
        status: pass
    human_judgment: false
  - id: D3
    description: "Each board uploaded and re-verified running the just-built firmware; exactly one firestarter write at28c256 -b --force <128-byte payload> issued per board with complete verbatim output captured"
    verification:
      - kind: manual_procedural
        ref: "119-MEASUREMENT.md sections 2c/3a/3b/3c -- three upload+re-verify+write sequences, one per board"
        status: pass
    human_judgment: false
  - id: D4
    description: "Worst per-byte page-load interval and SDP-unlock duration recorded per board, unrounded, with the structural page-boundary-crossing caveat named explicitly; WARN absence stated as expected"
    verification:
      - kind: manual_procedural
        ref: "119-MEASUREMENT.md section 4 -- 6080us (Leonardo, page-boundary figure)/84us (Uno)/88us (uno328pb); unlock 568/412/424us against 600us budget; MSG_WARN_SDP_TBLC_EXCEEDED absent on all three (grep for 'W:' in section 3's three raw logs -- zero hits)"
        status: pass
    human_judgment: false
  - id: D5
    description: "119-MEASUREMENT.md written mirroring 118-MEASUREMENT.md's shape (sections 1-7 + Disposition), reviewed line-by-line for validation-ceiling compliance"
    verification:
      - kind: unit
        ref: "grep -n -iE 'die accept|silicon (state|actually)|works on an AT28C|SDP lock/unlock works' 119-MEASUREMENT.md -- 4 hits, all inside the verbatim REQUIREMENTS.md blockquote or explicit negation statements ('no run here shows... because no AT28C part was present'); zero affirmative silicon-validation claims"
        status: pass
    human_judgment: false
  - id: D6
    description: "REQUIREMENTS.md unchanged by this plan; LOCK-01 through LOCK-06 read Complete; DEVTEST-01 reads Pending"
    verification:
      - kind: unit
        ref: "git diff --quiet .planning/REQUIREMENTS.md -- prints REQS_UNCHANGED; grep confirms all six LOCK rows Complete, DEVTEST-01 Pending"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-07-28
status: complete
---

# Phase 119 Plan 11: Three-Board Page-Load Bench Measurement (D-16/D-18) Summary

**Bench-measured the page-load worst-per-byte interval and SDP-unlock duration on all three attached boards (Leonardo/Uno/uno328pb) with full provenance, discovering and documenting a structural characteristic of the D-16 tracker — a page-boundary crossing folds the prior page's full completion-poll-plus-readback-verify latency into the reported interval — and recording an honest divergence from the plan's anticipated flow (the Leonardo's write completed successfully rather than aborting on the empty socket, while the Uno-class boards failed as expected).**

## Performance

- **Duration:** ~50 min
- **Completed:** 2026-07-28
- **Tasks:** 2/2
- **Files modified:** 1 (new `119-MEASUREMENT.md`)

## Accomplishments

- **Task 1 (bench run, all three boards):** Verified `controller:` identity for all three candidate ports by command (`firestarter -p <port> -v fw`) — `/dev/ttyACM0`=leonardo, `/dev/ttyACM1`=uno, `/dev/ttyUSB0`=uno328pb, matching Phase 118's recorded map exactly (re-verified, not assumed; it did not shuffle this time). Built all three envs from the clean, unmodified `firestarter` tree at `0048b3d` (`v1.22-at28c-software-data-protection-lifecycle`) — all three flash/RAM figures matched `119-NONREGRESSION.md` section 4 exactly (Leonardo 26072/28672, Uno 23932/32256, uno328pb 23976/32384), confirming the build was the phase's own final swept image. Uploaded and identity-re-checked each board in turn (Leonardo `pio run -t upload -e leonardo --upload-port /dev/ttyACM0`, Uno similarly, uno328pb via the `urclock` bootloader protocol, first attempt, no timeout, no retry needed). Prepared one 128-byte incrementing-pattern scratch payload (spanning exactly two 64-byte pages) and issued exactly one `firestarter write at28c256 -b --force <payload>` per board.
- **The results, honestly divergent across boards:** The **Leonardo's** write completed fully successfully — SDP unlock in 568 µs (nearly identical to F-118-01's 572 µs), page-load worst interval **6080 µs**. The **Uno** and **uno328pb** both failed identically at page 1's readback verify (`ERROR: 0x00 != 0x03 at 0x000000`) — SDP unlock in 412 µs / 424 µs, page-load worst interval **84 µs / 88 µs**. `MSG_WARN_SDP_TBLC_EXCEEDED` did not fire on any board. No brownout occurred on uno328pb.
- **The structural finding (grounded in code, not hardware experimentation):** Traced `eeprom28c_write_execute`'s source (`eeprom_28c.cpp:622-655`) to explain why the Leonardo's number is ~70x the Uno-class boards' — `page_load_previous_us` is updated immediately after each byte's `set_data` call, *before* that byte's page-boundary completion-poll and readback-verify run. Because the Leonardo's write crossed the page-1→page-2 boundary (both pages succeeded), its reported worst interval folds in the *entire* page-1 completion-poll-plus-64-byte-readback-verify latency — a structurally larger and different quantity than a clean per-byte bus-write time. The Uno-class boards aborted during page 1's own verify step, before ever reaching the boundary, so their figures are clean within-page numbers directly comparable to the 100 µs/byte datasheet maximum. This distinction is named explicitly in `119-MEASUREMENT.md` section 1 and section 4 so a later reader does not compare the two kinds of number as if they measured the same thing. No additional hardware command was run to further probe this — the plan's "exactly one write per board, no repeated sweeps" constraint was honored; the explanation rests entirely on static source analysis.
- **Task 2 (the document):** Wrote `119-MEASUREMENT.md` mirroring `118-MEASUREMENT.md`'s seven-section-plus-Disposition shape, with sections 2/3 repeated per board. Section 1 states the MCU-not-the-chip framing before any number, names the flash-vs-timing conflation, restates gh#11's conflation-not-sampling-rate shape, and introduces the page-boundary structural caveat. Section 4 records all six numbers (three worst-intervals, three unlock durations) unrounded, with the cross-board caution that the uno328pb tracked the Uno's behaviour closely (same failing address, same byte pair, comparable interval) — the observed divergence is Leonardo (ATmega32U4) vs. Uno-class (ATmega328P/PB), never 328PB-specific silicon. Section 5 records the three-board scope as a reversal of Phase 118's D-12, with the operator's words and every constraint, and states the lock's own hardware duration was deliberately not attempted (D-17). Section 6 quotes the validation ceiling verbatim. Section 7 names Phase 122's closeout and future gh#11 work as consumers. Performed the line-by-line ceiling review (documented below).

## Task Commits

1. **Task 2 (119-MEASUREMENT.md creation)** — `a12e632` (docs), staged as the single explicit path `.planning/phases/119-lock-sdp-enable-command-surface-fw-half/119-MEASUREMENT.md`

Task 1 produced no file diff (bench run / data-gathering only, consumed by Task 2's write) — no separate commit, matching Plan 119-10's own precedent for a data-gathering task that feeds a single write-up commit.

**Plan metadata:** committed alongside this SUMMARY (docs, meta commit staging SUMMARY.md + STATE.md + ROADMAP.md).

## Files Created/Modified

- `.planning/phases/119-lock-sdp-enable-command-surface-fw-half/119-MEASUREMENT.md` — new, the three-board bench measurement record with full per-board provenance, raw logs, the structural page-boundary finding, and the validation-ceiling review

## Decisions Made

See `key-decisions` in frontmatter for the five load-bearing ones (the page-boundary-crossing structural explanation and why the two board classes' numbers are not directly comparable; declining to re-run hardware to further probe the divergence; uno328pb needing no retry and how its single-attempt caveat is applied; recording the Leonardo/Uno-class divergence from the plan's anticipated flow honestly; and the D-18 item 4 cross-board attribution caution).

## Deviations from Plan

### Not a Rule violation — an honest empirical divergence from the plan's anticipated flow, documented rather than smoothed over

**1. The Leonardo's write completed successfully instead of aborting at the first page**
- **Found during:** Task 1, the Leonardo's write run
- **What the plan anticipated:** Mirroring 118-07, the write failing at the first page because the socket is empty (the plan's Step 5 text: "the write failing at the first page because the socket is empty... is expected and is not a defect").
- **What actually happened:** The Leonardo's write reported "successful" (0.09s) — both pages' completion polls and readback verifies passed despite the empty socket.
- **Why (traced via source, not guessed):** `-b` skips the blank check entirely (118-07 used plain `--force`, which still ran the blank check and failed there). With `-b`, the only remaining gate on an empty socket is the completion-poll (`eeprom28c_wait_for_page_write`) and readback-verify (`eeprom28c_verify_page_readback`), both reading through `handle->firestarter_get_data` off a floating bus. On the Leonardo both checks passed for both pages; on the Uno-class boards the first readback byte disagreed (`0x00 != 0x03`).
- **No further hardware investigation was performed** (the plan forbids repeated sweeps/extra commands beyond one write per board), so no claim is made about *why* the floating-bus read happened to agree on Leonardo and not on the Uno-class boards — only that the raw logs show it, verbatim, in `119-MEASUREMENT.md` sections 3a-3c.
- **Files modified:** none (finding recorded in `119-MEASUREMENT.md`, no code change — this is a bench observation document, not a firmware plan)
- **Impact:** None on plan scope. The divergence is exactly the kind of honest, non-fabricated reporting D-19's spirit and this plan's own instructions require — recorded plainly, not rounded away.

---

**Total deviations:** 1 (an honest empirical divergence from anticipated flow, not a Rule 1-4 auto-fix; no code was touched, no requirement was affected)
**Impact on plan:** None — the plan's acceptance criteria required capturing the complete verbatim output and the exact reported values "as printed," which is what happened; the anticipated abort was a prediction, not a requirement.

## Issues Encountered

None beyond the documented divergence above. All three boards enumerated correctly, all three uploads succeeded on the first attempt, and all three writes produced a definite outcome (no timeouts, no need for retries even on uno328pb).

## User Setup Required

None — no external service configuration required.

## Known Stubs

None. This plan is a bench-measurement document (`119-MEASUREMENT.md`); no UI or data-rendering path is affected.

## Requirement Status

**No requirement marked Complete by this plan**, per the plan's explicit instruction — `REQUIREMENTS.md` is byte-unchanged (confirmed: `git diff --quiet .planning/REQUIREMENTS.md` succeeds, printing `REQS_UNCHANGED`). LOCK-06 was already closed by Plan 119-10 on the flash axis and is **not** re-opened or re-marked here; this plan discharges only the timing directive PROJECT.md's FIFTH CORRECTION item 3 attached to LOCK-06, naming the conflation explicitly rather than inheriting it. LOCK-01 through LOCK-06 all re-confirmed Complete; DEVTEST-01 re-confirmed Pending (Phase 121's host half).

## Next Phase Readiness

- `119-MEASUREMENT.md` is the single artifact a later reader should open for the page-load timing question — it is cross-referenced by name, not duplicated, from Phase 122's closeout and any future gh#11-adjacent silicon work.
- The page-boundary-crossing structural characteristic named in section 1/4 is new information for any future phase that revisits this tracker or writes a similar per-byte measurement — a future author should not assume "worst per-byte interval" always means a clean single-byte figure once a payload spans more than one page.
- The three-board scope is explicitly recorded as this plan's own reversal of Phase 118's Leonardo-only D-12, not a new default — the next phase (120) should not assume three-board bench work is now standard scope.
- No blockers for Phase 120. This is the last plan in Phase 119's plan set (11 of 11).

---
*Phase: 119-lock-sdp-enable-command-surface-fw-half*
*Completed: 2026-07-28*

## Self-Check: PASSED

- FOUND: `.planning/phases/119-lock-sdp-enable-command-surface-fw-half/119-MEASUREMENT.md`
- FOUND: `.planning/phases/119-lock-sdp-enable-command-surface-fw-half/119-11-SUMMARY.md`
- FOUND: `a12e632` (meta commit, 119-MEASUREMENT.md)
