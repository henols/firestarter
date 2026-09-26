---
phase: 162-chip-11-part-dev-test-sweep-on-the-reference-rig
plan: 06
subsystem: bench, on-device
tags: [bench, on-device, cell-CHIP, leonardo, atmega32u4, rev-2-0, dip28, vpp-12v, parts-3-4, sst27sf512, fm1608, sweep-position, operator-ruling, tool-fix]

requires:
  - phase: 162-05
    provides: "bench/cells/CHIP/CELL.md's operator ruling (dev test's own v133 verdict is the sweep's divergence trigger, not a prior milestone's disposition), the 64 KiB class ceiling (856s), and positions 1-2's evidence rows"
  - phase: 162-01
    provides: "rig-pins.json's chips map, DERIVE-PLAN.json's per-part step sets, FM1608-VCC.md's resolved vcc_mv:3300 answer"
provides:
  - "bench/cells/CHIP/ positions 3 (SST27SF512) and 4 (FM1608) recorded — both same/validated/known_carried:no, zero new control rows"
  - "The 28-pin, 12V DIP28 group (positions 1-3) closed out with no pot move and no JP4 change since the session opened"
  - "The sweep's first 8 KiB duration figure (FM1608, 71.0s steps total, well inside the 120s fallback ceiling)"
  - "A live second application of the operator ruling: the phase plan's own D-03 pre-booked FM1608 as diverges:no-comparable-baseline in advance, but the operator ruling (dev test's own verdict is the arbiter) superseded that pre-booking before the run — dev test returned OK, so the row is same/validated with no control arbitration and no flash"
  - "append_chip_evidence.py: derive_vpp_firmware_mv() fixed to read report.voltage.vpp_before_mv directly (the console-log VPP:<N.N>V scrape it replaced never matches a real dev-test invocation's output) — 20/20 selftest legs pass (19 prior + 1 new)"
  - "Positions 1 and 2's already-committed rows (from 162-05) re-derived through the same fix, correcting a false 'not measured' vpp_firmware_mv/vpp_shortfall_mv to their real, on-disk values (12400 / -400) — a scope-boundary judgement call this executor made and got wrong, then corrected on the same day"
affects: [162-07, 162-08, 162-09, 162-10]

tech-stack:
  added: []
  patterns:
    - "derive_vpp_firmware_mv() now prefers the dev-test report's own machine-readable voltage.vpp_before_mv field over a console-log regex scrape — the regex only ever matched the standalone `vpp` subcommand's continuous-print output, never dev test's own rich-rendered summary table, so every real chip-sweep position was silently mis-deriving 'not measured' until this fix"
    - "CHIP-EVIDENCE.jsonl is append-only immutable by design (render_evidence.append_row_to_file refuses to rewrite an existing position_id) — correcting an already-committed row's derived field requires removing back to the schema line and re-appending every row in original order through the normal tool path, never a patch-in-place and never a hand-edit; a byte-for-byte key diff against a pre-removal snapshot is the verification that nothing else drifted"
    - "The operator ruling (dev test's own v133 verdict is the sweep's divergence arbiter) overrides the phase plan's own pre-booked D-03 divergence text when they conflict — a plan's advance booking is not authoritative once a live ruling supersedes the reasoning it was based on; apply the ruling as written, not the plan's literal words"
  key-files:
    created:
      - .planning/v1.34/bench/cells/CHIP/provenance_CHIP__v133__sst27sf512.json
      - .planning/v1.34/bench/cells/CHIP/provenance_CHIP__v133__fm1608.json
      - .planning/v1.34/bench/cells/CHIP/reports/CHIP__v133__sst27sf512.{json,md}
      - .planning/v1.34/bench/cells/CHIP/reports/CHIP__v133__fm1608.{json,md}
      - .planning/v1.34/bench/cells/CHIP/human-inputs/*_CHIP__v133__sst27sf512.*
      - .planning/v1.34/bench/cells/CHIP/human-inputs/*_CHIP__v133__fm1608.*
      - .planning/v1.34/bench/cells/CHIP/logs/CHIP__v133__sst27sf512.* (incl. one aborted attempt), logs/CHIP__v133__fm1608.*, logs/03_vpp_sst27sf512.*, logs/04_vpp_fm1608.*
      - .planning/v1.34/bench/cells/CHIP/board_probe_pos{3,4}.json(.stderr.log), touch_pos{3,4}.json
    modified:
      - .planning/v1.34/bench/CHIP-EVIDENCE.jsonl
      - .planning/v1.34/bench/CHIP-EVIDENCE.md
      - .planning/v1.34/bench/cells/CHIP/CELL.md
      - .planning/v1.34/tools/append_chip_evidence.py

key-decisions:
  - "vpp_firmware_mv scraping bug fixed at the derivation layer (read report.voltage.vpp_before_mv directly, fall back to console-log scrape only when absent) rather than by weakening any check — additive, selftested, backward-compatible with the function's three pre-existing selftest legs"
  - "This executor's own first call was that positions 1 and 2's already-committed rows were out of scope for this plan's own deviation rules (a closed-plan boundary) and deferred the fix to 162-10. The orchestrator reversed that call: CHIP-EVIDENCE.jsonl is one phase-spanning artifact, not plan 162-05's private output, and the deferred rows asserted a FALSE not-measured when the real value was already on disk. Re-derived both rows through the appender's own machinery (remove-to-schema-line, re-append in original order from retained artifacts), diffed key-by-key against a pre-removal snapshot to prove only the two VPP columns changed. CELL.md keeps the wrong scope call and its correction both visible."
  - "FM1608's divergence framing: the phase plan's own D-03 pre-booked 'diverges: no comparable baseline' in advance. The orchestrator instructed applying the operator ruling literally instead: run dev test alone first, and only a live FAIL/BAD earns C-08. dev test returned OK, so the row is same/validated, no control row, no flash — a live, on-hardware demonstration that the ruling (not the plan's advance booking) governs when they conflict."
  - "The predicted register-cache-elision byte-0 write defect did not manifest on this run (verify succeeded on both alternating-pattern cycles). Recorded as an explicit non-manifestation data point on the still-open todo, not claimed as a fix or closure — hardware-gated defects are not reliably reproducible-or-absent from a single run."

patterns-established:
  - "A phase plan's advance-booked divergence text (D-03-style pre-booking) is provisional against a live operator ruling that changes the trigger it was reasoned from — the executor applies the ruling as written and records the deviation from the plan's own words explicitly, rather than treating the plan's pre-booking as binding once superseded."
  - "Correcting an append-only evidence ledger's already-written row: never patch in place (render_evidence enforces immutability by design); remove to the schema line, re-append every affected row in original order from retained artifacts through the normal tool path, and prove correctness via a key-by-key diff against a pre-removal snapshot (a no-op re-append of an already-correct row is the control that the mechanism itself introduces no drift)."

requirements-completed: []
# This plan produces positions 3 and 4 of 10 and discharges none of CHIP-01...CHIP-05 per its own
# explicit instruction. It contributes to CHIP-02, CHIP-04 and CHIP-05. Full coverage closes only
# in plan 162-10's reconciliation.

duration: ~45 min of active bench/tool work across two operator-gated physical checkpoints (chip swaps); real-world elapsed time additionally includes the operator's own seating time between checkpoints, not measured by this executor
completed: 2026-08-28
status: complete
---

# Phase 162 Plan 06: Cell CHIP — Positions 3-4 (SST27SF512, FM1608), a Tool Fix, and a Second Live Application of the Operator Ruling Summary

**SST27SF512 ran clean (all six steps OK, closing out the 28-pin/12V DIP28 group), and FM1608 ran clean too (three applicable steps OK, three structurally NA) — but FM1608's phase-plan-pre-booked "diverges: no comparable baseline" verdict was overridden live by the operator ruling before the run, so it landed `same`/`validated` with zero flashes and zero control arbitration. Along the way, a genuine derivation bug in `append_chip_evidence.py` was found and fixed (VPP firmware reading was silently reading "not measured" on every real position because it scraped a console-log line dev test never prints), and — after an initial wrong scope call by this executor — positions 1 and 2's already-committed rows from plan 162-05 were corrected through the same fix, using the appender's own re-derivation machinery, never a hand-edit.**

## Performance

- **Duration:** ~45 min of active bench/tool work (three commits spanning 23:36-23:50 UTC), plus preceding provenance/setup work from ~23:22 UTC; two operator-gated physical checkpoints (chip swaps) paused this executor for an unmeasured real-world interval each
- **Started:** 2026-08-28T23:22:22Z (position 3's port re-verification)
- **Completed:** 2026-08-28T23:50:30Z (position 4's commit)
- **Tasks:** 4 of 4 (2 checkpoints — chip swaps, operator-performed; 2 auto — dev test + evidence recording), plus one out-of-band correction task inserted between checkpoints by orchestrator instruction
- **Files modified:** 34 (see `key-files`; the bulk is per-position artifacts under `bench/cells/CHIP/`)

## Accomplishments

- **Position 3 (SST27SF512):** all six `dev test` steps OK (`id`, `read`, `write`, `verify`, `erase`, `blank-check`), banner 6 of 6, steps total 201.6s — well inside the measured 856s 64 KiB ceiling. `divergence_verdict: same`, matching the cleanest prior comparison in the DIP28 group (v1.15 Phase 82 PASS, obtained without a now-forbidden flag). **The 28-pin, 12V group (positions 1-3) is now complete** with zero pot moves and zero JP4 changes since the session opened.
- **Tool fix (Rule 1, found live at position 3):** `append_chip_evidence.py`'s `derive_vpp_firmware_mv()` scraped `--console-log` for a literal `VPP: <N.N>V` line — a string shape only the standalone `vpp` CLI subcommand ever prints, never `dev test`'s own console output. Every real chip-sweep position was silently deriving `vpp_firmware_mv`/`vpp_shortfall_mv` as `not measured`, including the already-committed positions 1 and 2. Fixed to read the report's own `voltage.vpp_before_mv` field directly, falling back to the console-log scrape only when absent — additive, byte-compatible with the function's three pre-existing selftest legs, one new positive leg added (20/20 total).
- **Scope-call correction (self-disclosed):** this executor's first response to the above finding was to defer re-deriving positions 1 and 2's already-committed rows to plan 162-10 (a "closed-plan boundary" judgement). The orchestrator overturned that call — `CHIP-EVIDENCE.jsonl` is one phase-spanning artifact, and the deferred rows asserted a **false** `not measured` when the retained reports on disk already carried the real value. Both rows were re-derived immediately, using the appender's own re-derivation machinery (never a hand-edit, since the ledger is append-only immutable by design): all three then-existing rows were removed back to the schema line and re-appended in original order from each position's own retained artifacts, with every field except the two VPP columns confirmed byte-identical via a pre-removal key-diff (position 3's own re-append diffed as zero changed keys — a working control proving the mechanism itself is inert). Corrected values: `vpp_firmware_mv: 12400`, `vpp_shortfall_mv: -400` on both positions 1 and 2 (previously both a false `not measured`).
- **Position 4 (FM1608):** three applicable steps OK (`read`, `write` over the full 8192 B device with an alternating payload, `verify`), three structurally NA by construction (`id`, `blank-check`, `erase`), banner 3 of 3 ran, steps total 71.0s — **the sweep's first 8 KiB duration figure**, well inside the 120s fallback ceiling. **The phase plan's own D-03 had pre-booked this position's divergence as `diverges: no comparable baseline` in advance; the orchestrator instructed applying the operator ruling literally instead** — run `dev test` alone first, and only a live FAIL/BAD earns the `C-08` control arbitration. `dev test` returned OK, so the row is `same`/`validated`, with **zero control rows and zero flashes** for this position. This is the second live instance in the sweep (after W27E512 in 162-05) where a pre-declared framing was superseded by the operator ruling in real time.
- **The predicted register-cache-elision byte-0 write defect did NOT manifest** on FM1608 this run — `verify` succeeded on both alternating-pattern write/verify cycles, no byte-0 mismatch anywhere in the console output or the report's step verdicts. Recorded explicitly as a non-manifestation data point on the still-open todo, not claimed as a fix or closure.
- Family-label conflation (v1.15's decimal-40-written-as-hex "0x40" vs. this row's true hex `0x28`) stated once for FM1608, not booked as a divergence — matching the v1.16 ledger's own retirement of the same conflation. `vcc_mv: 3300` cited from Wave 0's `FM1608-VCC.md` rather than re-derived; `chip_database.json` untouched throughout.
- `run_gates.sh` RC=0, 14/14 selftests, 7/7 live gates, `ALL GATES PASSED` after every position and after the re-derivation; `gate_record.py` explicitly re-run standalone against `CHIP-EVIDENCE.jsonl` each time (0 violations) — the record-shape gate checked separately from the render gate, per the standing instruction not to conflate the two.
- Four of ten positions now recorded overall, all `same`/`validated`/`known_carried:no`, **zero control rows in the live ledger** — SC#4 still balances trivially.

## Task Commits

1. **Task 1: Swap to the SST27SF512** — no code commit (physical action only, operator-performed; recorded inline in Task 2's commit)
2. **Task 2: Position 3 (SST27SF512)** — `acd0ecf2` (feat) — all six steps OK, `same`, the VPP scraping bug found and fixed
   - **Out-of-band correction, orchestrator-instructed** — `f3077f22` (fix) — positions 1 and 2's rows re-derived through the same fix, scope call reversed
3. **Task 3: Chip swap checkpoint to FM1608** — no code commit (physical action only, operator-performed; recorded inline in Task 4's commit)
4. **Task 4: Position 4 (FM1608)** — `97cb0bc4` (feat) — three applicable steps OK, `same` per the operator ruling superseding D-03's pre-booking; predicted defect did not manifest

**Plan metadata:** (this commit, immediately following)

## Files Created/Modified

- `.planning/v1.34/bench/CHIP-EVIDENCE.jsonl` / `.md` — four rows total now (positions 1-4), all `same`/`validated`/`known_carried:no`, zero control rows
- `.planning/v1.34/bench/cells/CHIP/CELL.md` — positions 3 and 4's full records, the vpp-scraping tool fix and its scope-call correction (both the wrong call and the fix kept visible), FM1608's D-03-override, the predicted-vs-observed byte-0 defect comparison, and this plan's leave-state
- `.planning/v1.34/tools/append_chip_evidence.py` — `derive_vpp_firmware_mv()` fixed to prefer `report.voltage.vpp_before_mv`; one new positive selftest leg (20/20 total)
- `.planning/v1.34/bench/cells/CHIP/provenance_*`, `reports/`, `logs/`, `human-inputs/`, `board_probe_pos{3,4}.json`, `touch_pos{3,4}.json` — full per-position evidentiary artifacts for both positions

## Decisions Made

See `key-decisions` in frontmatter. In prose: this plan surfaced and fixed a genuine, previously-undetected derivation bug affecting every position in the sweep so far (not just this plan's own); made a wrong scope-boundary call about how far to reach back to fix it, got corrected the same session, and left both the wrong call and its correction visible in `CELL.md` rather than smoothing it over; and demonstrated the operator ruling overriding the phase plan's own advance-booked divergence text for the second time in the sweep (FM1608, following W27E512 in 162-05).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `append_chip_evidence.py`'s `vpp_firmware_mv` derivation silently produced `not measured` on every real chip-sweep position**
- **Found during:** Task 2 (position 3, SST27SF512)
- **Issue:** `derive_vpp_firmware_mv()` regex-scraped `--console-log` for a literal `VPP: <N.N>V` line — a string shape only the standalone `vpp` CLI subcommand's own continuous-print loop ever emits. `dev test`'s own console output (a rich-rendered summary table) never contains that literal line, so this field (and the shortfall computed from it) silently read `not measured` on every real position, including the already-committed positions 1 and 2.
- **Fix:** Read the report JSON's own `voltage.vpp_before_mv` field (an exact mV int, already present on every real report) directly when numeric, falling back to the original console-log scrape only when absent — preserves the function's three pre-existing selftest legs byte-for-byte.
- **Files modified:** `.planning/v1.34/tools/append_chip_evidence.py`
- **Verification:** 20/20 selftest legs pass (19 prior + 1 new positive leg proving the report field wins even when the console log carries no `VPP:` line at all — the real `dev test` shape).
- **Committed in:** `acd0ecf2`

**2. [Orchestrator-directed correction, not a self-initiated deviation] Positions 1 and 2's already-committed rows re-derived**
- **Found during:** immediately after Task 2's commit, by orchestrator review
- **Issue:** This executor's own first response to finding #1 above was that positions 1 and 2's rows (committed in the already-closed plan 162-05) were out of scope for this plan's deviation rules — a "closed-plan boundary" call. The orchestrator determined this was wrong: `CHIP-EVIDENCE.jsonl` is a single phase-spanning artifact (not plan-private), and the deferred rows asserted a **false** `not measured` — the retained reports for both positions already carried the real `voltage.vpp_before_mv: 12400` on disk.
- **Fix:** Re-derived both rows using the appender's own machinery (never a hand-edit): `CHIP-EVIDENCE.jsonl`'s rows are append-only immutable by design (`render_evidence.append_row_to_file` refuses to rewrite an existing `position_id`), so all three then-existing rows were removed back to the schema line and re-appended in original order from each position's own retained report/provenance/console-log/human-input files, through the now-fixed code path. Every field besides the two VPP columns was diffed key-by-key against a pre-removal snapshot and confirmed byte-identical; position 3's own re-append diffed as **zero** changed keys, confirming the mechanism itself introduces no drift.
- **Files modified:** `.planning/v1.34/bench/CHIP-EVIDENCE.jsonl`, `.md`, `.planning/v1.34/bench/cells/CHIP/CELL.md`
- **Verification:** `run_gates.sh` RC=0, 14/14 + 7/7, `ALL GATES PASSED`; `gate_record.py` standalone: 0 violations; both sub-repo porcelains empty throughout; `firestarter/` confirmed still at the v1.33 SHA (no flash occurred).
- **Committed in:** `f3077f22`

**3. [Orchestrator-directed application of the operator ruling, not a self-initiated deviation] FM1608's D-03 pre-booking overridden**
- **Found during:** before Task 4's run (orchestrator instruction, received before `dev test FM1608` was invoked)
- **Issue:** The phase plan's own D-03 pre-booked FM1608's `divergence_verdict` as `diverges: no comparable baseline` in advance, reasoning that the newest prior disposition was obtained via a now-forbidden flag. This executor's prior message (end of the previous turn) had stated an intent to run `dev test` first and branch on its live verdict, which the orchestrator confirmed was the correct application of the operator ruling — the plan's own pre-booking is superseded, since "no comparable baseline" is an absence of history, not a live failure, and does not by itself earn a control-arm re-run under the ruling.
- **Fix:** Ran `dev test FM1608` alone first, with no pre-emptive flash and no pre-emptive control re-run. It returned OK on all three applicable steps, so the row was recorded `same`/`validated`, with the deviation from the plan's own D-03 wording stated explicitly in the row's `verdict` text and in `CELL.md`.
- **Files modified:** none beyond the normal position-4 artifacts (this is a procedural deviation from the plan's own pre-booked text, not a code fix)
- **Verification:** the row's `divergence_verdict: same`, `control_rerun_for: not applicable`, and the explicit deviation note are all present and machine-checked in the position-4 verify script.
- **Committed in:** `97cb0bc4`

---

**Total deviations:** 1 self-found tool bug fixed at the correct layer (Rule 1), 1 orchestrator-directed scope-call reversal (re-deriving positions 1-2), 1 orchestrator-directed application of the operator ruling over the plan's own pre-booked text (FM1608). None involved product code; both sub-repos stayed byte-unchanged throughout.
**Impact on plan:** The tool fix and its retroactive application improve data integrity across the whole phase-spanning ledger, not just this plan's own rows — a net positive beyond this plan's narrow scope, applied only after orchestrator confirmation rather than unilaterally. FM1608's outcome (a live PASS, zero flashes) is the correct, cheaper result under the operator ruling; no scope creep in any direction.

## Issues Encountered

- **This executor made one wrong scope-boundary call** (deferring positions 1-2's re-derivation to 162-10) that was corrected within the same session before any further work proceeded. See Deviation #2 above for the full account — kept visible in `CELL.md` rather than smoothed over, per this project's standing disclosure convention.
- No hardware anomalies this plan beyond the already-known, already-filed classes: the same reproducible `ERROR: Empty input` transient recurred on position 3 at the identical point in the six-step sequence as positions 1-2 (self-recovering, no effect on any verdict); `read_divergence`/`read_consistency_followup` stayed `not measured`/`not applicable` on both positions, the same already-filed `diagnostic_report.py` export gap.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

Plan 162-07 inherits this plan's leave-state at zero physical cost: Leonardo at `/dev/ttyACM0`, v1.33 arm still flashed and never touched this plan (no divergence occurred at either position), FM1608 seated (DIP28, JP4 28-pin, unchanged since Task 3), pot at meter 11.6 V / firmware 12400 mV (in band, unchanged since position 1), Rev 2.0 shield mounted. No blockers.

**Carried forward for the remaining plans in this phase (162-07 through 162-10):**
- The `derive_vpp_firmware_mv()` fix and the fact that positions 1-4 all now carry correct, non-fabricated `vpp_firmware_mv`/`vpp_shortfall_mv` values — no further backlog item needed for this specific gap (it has been fully resolved, not deferred).
- The `read_divergence`/`read_consistency_followup` export gap (`diagnostic_report.py` never serializes `steps[].divergence`) remains filed for Phase 165/166's backlog — unaffected by this plan's fix, a different, still-open gap.
- FM1608's non-manifestation of the register-cache-elision byte-0 defect is a recorded data point, not a closure — the todo (`fm1608-byte0-write-never-lands-register-cache-elision.md`) stays open.
- Plan 162-10's reconciliation must account for the phase plan's own D-03 pre-booking having been overridden live for FM1608 (the second such override in the sweep, after W27E512), not silently reinterpreted.
- **The JP4 move to the 32-pin group belongs to plan 162-07's own first handover** — explicitly not begun here, per orchestrator instruction.

---
*Phase: 162-chip-11-part-dev-test-sweep-on-the-reference-rig*
*Completed: 2026-08-28*

## Self-Check: PASSED

All claimed commits (`acd0ecf2`, `f3077f22`, `97cb0bc4`, `2215413e`) confirmed present in `git log`. All claimed created files (`provenance_CHIP__v133__sst27sf512.json`, `provenance_CHIP__v133__fm1608.json`, `reports/CHIP__v133__sst27sf512.json`, `reports/CHIP__v133__fm1608.json`, this SUMMARY.md) confirmed present on disk.
