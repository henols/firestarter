---
phase: 162-chip-11-part-dev-test-sweep-on-the-reference-rig
plan: 05
subsystem: bench, on-device
tags: [bench, on-device, cell-CHIP, leonardo, atmega32u4, rev-2-0, dip28, vpp-12v, parts-1-2, sweep-position, operator-ruling]

requires:
  - phase: 162-01
    provides: "rig-pins.json's 11-part chips map, CHIPS-MAP-DERIVATION.md, PRE-PHASE.md's CLOSE-04 before-count and A3/B2 anchors"
  - phase: 162-02
    provides: "bench/CHIP-EVIDENCE.jsonl's schema and tools/append_chip_evidence.py"
  - phase: 162-04
    provides: "PROCEDURE.md's Chip-sweep step list (C-01..C-09) and render_steps.py --section C"
provides:
  - "bench/cells/CHIP/ opened: PREFLIGHT.md (non-null fw_board_identity proven before any part ran), POT.md (VPP record including a retracted-and-corrected finding), CELL.md (both positions' full record, an operator ruling that redefines the sweep's divergence trigger for every remaining position, and three self-caused-deviation disclosures)"
  - "Two CHIP-EVIDENCE.jsonl rows, both same/validated/known_carried:no: CHIP__v133__w27c512 (the phase's first measured dev test duration and the real 64 KiB ceiling) and CHIP__v133__w27e512 (a dev test OK, per the operator ruling, despite a prior-milestone FAIL disposition for this part)"
  - "append_chip_evidence.py: --pending-readback flag (chip-sweep positions never flash on their own), repeat_policy/read_divergence derivation fixes, and a whole-row required-field self-check added as defense in depth"
  - "A live operator ruling that redefines CHIP-04/SC#4's divergence trigger for the whole remaining sweep: dev test's own v133 verdict is the baseline, not a prior milestone's disposition; a control-arm row is now earned only by a live dev test FAIL/BAD, never by a mismatch against an old record"
affects: [162-06, 162-07, 162-08, 162-09, 162-10]

tech-stack:
  added: []
  patterns:
    - "A chip-sweep position's row is validated against gate_record's FULL record_keys list, not just the four human-supplied fields, immediately after build_row() and before either --dry-run's return or the real write — catches a derivation bug at append time instead of a later, separate full-file gate run"
    - "A firmware flash from this executor's sandboxed Bash tool needs env -C <dir> <cmd>, never cd <dir> && <cmd> nor <cmd> -d <dir> — cwd, exported PATH, and exported shell functions do not persist across this harness's Bash calls, and PlatformIO's own project-config resolution runs unconditionally before any subcommand flag is parsed"
    - "Never pass markdown containing backtick-quoted code snippets to git commit -m as a plain string — bash command-substitutes backtick pairs even inside a quoted -m argument; use git commit -F <file> for any message containing backticks"

key-files:
  created:
    - .planning/v1.34/bench/cells/CHIP/PREFLIGHT.md
    - .planning/v1.34/bench/cells/CHIP/POT.md
    - .planning/v1.34/bench/cells/CHIP/CELL.md
    - .planning/v1.34/bench/cells/CHIP/provenance_CHIP__v133__w27c512.json
    - .planning/v1.34/bench/cells/CHIP/provenance_CHIP__v133__w27e512.json
    - .planning/v1.34/bench/cells/CHIP/provenance_CHIP__control__w27e512.json (retracted control row's provenance; kept on disk, not referenced by any live JSONL row)
    - .planning/v1.34/bench/cells/CHIP/READBACK-VERDICT.json
    - .planning/v1.34/bench/cells/CHIP/readback_control/
    - .planning/v1.34/bench/cells/CHIP/readback_control_restore_v133/
    - .planning/v1.34/bench/cells/CHIP/readback_final_confirm/
    - .planning/v1.34/bench/cells/CHIP/reports/CHIP__v133__w27c512.{json,md}
    - .planning/v1.34/bench/cells/CHIP/reports/CHIP__v133__w27e512.{json,md}
    - .planning/v1.34/bench/cells/CHIP/reports/CHIP__control__w27e512.{json,md} (retracted row's copied-out report, kept for the audit trail)
    - .planning/v1.34/bench/cells/CHIP/human-inputs/*.txt, *.json
  modified:
    - .planning/v1.34/bench/CHIP-EVIDENCE.jsonl
    - .planning/v1.34/bench/CHIP-EVIDENCE.md
    - .planning/v1.34/tools/append_chip_evidence.py

key-decisions:
  - "Position 1's C-03 pot finding was corrected mid-plan: the orchestrator's first framing (a ~600 mV drift since Phase 161) was itself wrong — it cited A3/B2's superseded pre-adjustment reading, not its settled state. Retracted in POT.md rather than silently overwritten, with the correct sequence (11.4 V correctly inherited -> mistaken up-adjustment to 11.97 V produced a 12800 mV over-guard reading -> corrected to 11.6 V / 12400 mV, in band) recorded as its own atomic commit"
  - "OPERATOR RULING (supersedes this plan's earlier work on position 2, applies to the whole remaining sweep): if dev test reports OK, the part is OK — a prior milestone's disposition is historical context, never an authoritative baseline, and is not the divergence trigger. A dev test FAIL/BAD is now the only thing that earns a control-arm re-run. This replaces CHIP-04/SC#4's original framing (compare each result to its v1.15 disposition); plan 162-10 must reconcile against this ruling, not the phase plan's original wording — recorded explicitly in CELL.md rather than silently reinterpreted"
  - "Position 2 (W27E512) was worked through TWO characterisations before the ruling arrived: first same-vs-diverges reasoning purely from the outer verdict (rejected as too strong — 'symptom absent' overclaimed 'healed'), then a sharpened diverges verdict citing three internal report indicators (read.reason='read runs diverged', write/verify.fingerprint='indeterminate') consistent with the old disposition persisting unreported, which triggered a full C-08 control-arm arbitration. The control arm reproduced the identical shape (not a hard FAIL), so the arbitration's own conclusion was 'not a v1.33 regression.' The operator ruling then arrived and superseded BOTH characterisations: the row is now `same`/`known_carried:no`, the three internal-field observations are kept as recorded detail but explicitly not divergence grounds, and the control row is retracted from CHIP-EVIDENCE.jsonl (its work is preserved in CELL.md as historical record only)"
  - "The C-08 control-arm interleave was physically completed (both flashes, both independently read-back-proven, the control dev test re-run) before the ruling arrived. No physical rework was needed after the ruling — firestarter/ was already restored to v1.33 with proven read-back and empty porcelain — only the evidentiary record (the JSONL row and CELL.md's framing) needed correcting"
  - "append_chip_evidence.py's READBACK-VERDICT.json load was unconditional for every position (inherited from the WRV sibling, where every position genuinely flashes-and-reads-back); a chip-sweep position only does that on a divergence. Fixed with an additive --pending-readback flag rather than weakening the check — default behaviour (flag omitted) is byte-for-byte unchanged, and a control-rerun row still hard-requires a real judged read-back"
  - "repeat_policy's healthy-case value was changed from a bare empty string to a descriptive non-blank string, and read_divergence's unconditional None was changed to the schema's own not-measured shape naming the exact host-app export gap — both found live when the orchestrator's own run_gates.sh caught gate_record RED on position 1's row after this executor's checkpoint had (correctly, but incompletely) reported only the render gate as green"
  - "A firmware flash on this executor's sandboxed Bash tool requires env -C <dir> <cmd> — cd as a separate call, -d/-c flags, and a PATH-shim script were all tried and either failed technically (Pitfall 4 fires regardless of -d/-c) or were blocked by the harness's own auto-mode permission classifier (the PATH-shim), which was correctly treated as a stop-and-report signal rather than something to route around further"

patterns-established:
  - "Under the operator ruling, a chip-sweep position's divergence_verdict is judged SOLELY against dev test's own v133 outer verdict (OK -> same, FAIL/BAD -> diverges) — a prior milestone's disposition, and any internal report field (reason strings, fingerprint buckets) consistent with it, is recorded as context but is never itself divergence grounds"
  - "A control-arm arbitration is now earned only by a live dev test FAIL/BAD on the v133 arm, to distinguish 'control also fails the same way' (not v1.33-attributable) from 'control passes where v133 fails' (a genuine v1.33 regression) — never by a mismatch against an old record"

requirements-completed: []

# Coverage omitted per this plan's own explicit instruction: "This plan produces the first two of
# ten positions. It closes none of CHIP-01…CHIP-05 ... Do not mark any CHIP requirement complete
# here." Full ten-position coverage closes only in plan 162-10's reconciliation, which must also
# reconcile CHIP-04/SC#4's wording against the operator ruling recorded here.

duration: 2h 5m
completed: 2026-08-28
status: complete
---

# Phase 162 Plan 05: Cell CHIP — Session Open, Positions 1-2 (W27C512, W27E512), Operator Ruling on the Sweep's Divergence Trigger Summary

**Opened the 11-part chip sweep's bench cell on the standing Leonardo + Rev 2.0 rig: W27C512 ran clean (`same`, matching v1.34's own A3/B2 result and v1.16's PASS) and supplied the phase's first real `dev test` duration and 64 KiB ceiling. W27E512 initially diverged from its pre-declared stuck-erase-bit disposition and was fully arbitrated against pre-v1.33 control firmware (which reproduced the same result) — then an operator ruling arrived mid-plan and redefined the sweep's own divergence trigger: `dev test`'s own OK/FAIL verdict is now the baseline, not a prior milestone's disposition, so W27E512's row was corrected to `same` and the control row retracted. The ruling applies to every remaining position in the sweep.**

## Performance

- **Duration:** 2h 5m
- **Started:** 2026-08-28T21:18:09Z
- **Completed:** 2026-08-28T23:23:00Z
- **Tasks:** 5 of 5 (2 checkpoints, 3 auto; Task 5's own divergence work was fully superseded mid-task by an operator ruling, corrected in place)
- **Files modified:** ~60 (see `key-files`; the bulk is per-position artifacts under `bench/cells/CHIP/`)

## Accomplishments

- Firmware identity proven non-null (`3.0.0b22:leonardo`) before any part ran (CHIP-02's hard pre-flight requirement), after working through a genuine live port-identity shuffle (ttyACM0 -> ACM1 -> ACM0, one transient I/O error) rather than assuming a number.
- Position 1 (W27C512): all six `dev test` steps OK, `divergence_verdict: same`, matching both v1.34 cell A3/B2's own judged full-device result on this exact rig and v1.16 Phase 91's PASS. Supplied the phase's first measured `dev test` total (214s wall-clock) and the real 64 KiB class ceiling (4×214s = 856s), superseding the 500s derived-fallback estimate.
- Position 2 (W27E512): outer verdict OK on all six steps. Worked through a full divergence investigation and control-arm arbitration (both flashes independently read-back-proven, control dev test re-run reproduced the identical OK-with-indeterminate-fingerprint shape) before an **operator ruling** arrived: `dev test`'s own OK verdict is the sweep's operative baseline, a prior milestone's disposition is not authoritative, and this is not a divergence. Final row: `same`, `known_carried: no`. The internal-field observations (`read.reason='read runs diverged'`, `write`/`verify.fingerprint='indeterminate'`) are kept as recorded detail, explicitly not divergence grounds.
- **The operator ruling redefines the sweep's own divergence trigger for every remaining position** (162-06 through 162-10): a `dev test` OK is always `same`, no control row; only a live FAIL/BAD earns a control-arm re-run (to distinguish "control fails the same way" from "a genuine v1.33 regression"). Recorded explicitly in `CELL.md` so 162-10 reconciles against the ruling, not the phase plan's original CHIP-04/SC#4 wording.
- `append_chip_evidence.py` gained a genuine defect fix (a whole-row required-field self-check) after the orchestrator's own `run_gates.sh` caught a gate failure this executor's own checkpoint had missed — documented plainly rather than smoothed over.
- SC#4 balances trivially at plan close: 0 diverging rows, 0 control rows. `run_gates.sh` exits 0, 14/14 selftests, 7/7 live gates, `ALL GATES PASSED`, record-shape gate explicitly checked (not just the render gate).

## Task Commits

1. **Task 1: Session open** — `66f38035` (docs) — rig confirmed (Leonardo/ttyACM0, Rev 2.0, W27C512 seated JP4 28-pin), first VPP finding recorded
2. **Task 2: Pre-flight** — `3c9526b0` (docs) — port re-verified by signature, v1.33 arm confirmed, `fw_board_identity` non-null before any part ran
   - C-03 finding (VPP over the high guard) — `4355c99e` (docs)
   - Correction — retracted false drift finding, orchestrator error — `bb6a4754` (docs)
3. **Task 3: Position 1 (W27C512)** — `d7b613f0` (feat) — `dev test` PASS, `same` verdict, 64 KiB ceiling measured
   - Gate fix — `e8e2b56b` (fix) — `repeat_policy`/`read_divergence` corrected at the derivation layer after `run_gates.sh` caught the row RED
4. **Task 4: Chip swap checkpoint** — no code commit (physical action only; recorded inline in Task 5's own commits)
5. **Task 5: Position 2 (W27E512)** — `bd798f98` (feat) — original divergence finding + C-08 control-arm arbitration (both flashes independently read-back-proven)
   - Self-disclosed deviation — `b149caa2` (docs) — a stray `pio` flash caused by a backtick in the prior commit message, investigated and confirmed harmless
   - **Operator ruling applied** — `20c9e564` (fix) — position 2's row corrected to `same`/`known_carried:no`; the control row retracted; `CELL.md` records the ruling, its effect on 162-10, and preserves the superseded C-08 work as historical record

**Plan metadata:** (this commit, immediately following)

## Files Created/Modified

- `.planning/v1.34/bench/cells/CHIP/PREFLIGHT.md` — port/arm/identity pre-flight record
- `.planning/v1.34/bench/cells/CHIP/POT.md` — full VPP record for the 12 V group, including the retracted-and-corrected drift finding and the position-1/position-2 firmware readings
- `.planning/v1.34/bench/cells/CHIP/CELL.md` — both positions' full record, the operator ruling and its effect on 162-10, the superseded C-08 arbitration preserved as historical record, the erase-duration/fast-fail-assumption check, and three self-caused-deviation disclosures
- `.planning/v1.34/bench/CHIP-EVIDENCE.jsonl` / `.md` — two final rows (both `same`/`validated`/`known_carried:no`); a third row (the control arbitration) was appended then removed per the ruling
- `.planning/v1.34/tools/append_chip_evidence.py` — `--pending-readback` flag, `repeat_policy`/`read_divergence` derivation fixes, whole-row required-field self-check (19 selftest legs pass, 18 prior + 1 new)
- `.planning/v1.34/bench/cells/CHIP/reports/`, `provenance_*.json`, `readback_control/`, `readback_control_restore_v133/`, `readback_final_confirm/`, `human-inputs/`, `logs/` — full per-position and per-flash evidentiary artifacts, including the retracted control row's own report/provenance (kept on disk for the audit trail, not referenced by any live JSONL row)

## Decisions Made

See `key-decisions` in frontmatter. In prose: this plan surfaced and corrected two of its own mistakes live (a mis-cited VPP baseline, and a gate-failing row), disclosed a third (a stray flash from a backtick in a commit message), and absorbed a live operator ruling that overturned its own in-progress divergence analysis for position 2 — all four are recorded in the artifacts rather than smoothed over, per this project's standing disclosure convention.

## Deviations from Plan

### Auto-fixed / self-corrected issues

**1. [Rule 1 - Bug] `append_chip_evidence.py`'s unconditional `READBACK-VERDICT.json` load**
- **Found during:** Task 3 (C-04, position 1)
- **Issue:** The tool hard-refused every chip-sweep position because it required a read-back-verdict artifact that only a divergence's `C-08` ever produces.
- **Fix:** Added an additive `--pending-readback` flag; default behaviour unchanged.
- **Files modified:** `.planning/v1.34/tools/append_chip_evidence.py`
- **Committed in:** `d7b613f0`

**2. [Rule 1 - Bug] `repeat_policy`/`read_divergence` derivation bugs, caught by `run_gates.sh` RED**
- **Found during:** post-Task-3 checkpoint, by the orchestrator's own independent gate run (not by this executor)
- **Issue:** `repeat_policy`'s healthy-case value was a bare `""`, and `read_divergence` was an unconditional `None` — both fail `gate_record.check_required_fields`'s universal non-blank rule.
- **Fix:** `repeat_policy` now returns a descriptive non-blank string for the healthy case; `read_divergence` returns the schema's own `not measured — <reason>` shape naming the real host-app export gap (`diagnostic_report.py` never serializes `steps[].divergence`). Added a whole-row self-check as defense in depth.
- **Files modified:** `.planning/v1.34/tools/append_chip_evidence.py`; corrected row re-appended.
- **Committed in:** `e8e2b56b`

**3. [Rule 1 - Bug, self-caused] A backtick in a `git commit -m` string executed as a real command**
- **Found during:** Task 5's own commit
- **Issue:** A markdown code-span inside a plain `-m "..."` string was command-substituted by bash, causing an unintended third `pio run -t upload -e leonardo`.
- **Fix:** Investigated immediately; `firestarter/` was already at the correct v1.33 SHA, so the stray rebuild wrote byte-identical content (confirmed by an extra independent read-back proof, matching whole-flash SHA). No corrective action needed beyond verification. Commit messages containing backticks now go through `git commit -F <file>`.
- **Files modified:** none (verification only); disclosed in `CELL.md`.
- **Committed in:** `b149caa2`

**4. [Operator ruling - not an executor deviation, but a live redefinition of the plan's own criteria] Position 2's divergence trigger overturned**
- **Found during:** after Task 5's C-08 control-arm arbitration had already completed
- **Issue:** This plan's original divergence trigger (compare `dev test` against the v1.15 disposition) was superseded by an operator ruling: `dev test`'s own OK/FAIL verdict is the sweep's baseline.
- **Fix:** Position 2's row corrected to `same`/`known_carried:no`; the control row removed from `CHIP-EVIDENCE.jsonl`. The already-completed C-08 work (both flashes, both read-back proofs, the control `dev test` re-run) required no physical rework — only the evidentiary record needed correcting. Preserved as historical record in `CELL.md`, clearly marked superseded.
- **Files modified:** `CHIP-EVIDENCE.jsonl`, `CHIP-EVIDENCE.md`, `CELL.md`, four `human-inputs/*.txt` files for position 2.
- **Committed in:** `20c9e564`

---

**Total deviations:** 3 tool/process issues (2 tool bugs fixed at the correct layer, 1 self-caused process mistake investigated and confirmed harmless), plus 1 live operator ruling that changed the plan's own success criteria for this and every remaining position (recorded, not silently reinterpreted).
**Impact on plan:** All four were caught and resolved within this plan's own session, before the plan was closed. No scope creep — every fix was scoped to the exact defect or ruling in front of it, and no gate, schema, or required-field list was weakened to make a row pass.

## Issues Encountered

- **Live port-identity shuffle** (Task 2): the Leonardo bounced between `/dev/ttyACM0` and `/dev/ttyACM1` across a touch/probe/kill sequence. Worked through by signature re-verification rather than assumed away; the working sequence (touch immediately followed by probe, no interposed command) is the one whose result is authoritative.
- **Bash-tool default timeout aborted `dev test`'s first invocation** (Task 3): the outer harness's 120s default fired before this task's own intended 500s ceiling could. Logged as an executor tooling mistake (not a PD-15 ceiling kill, not a P-H1 rig finding); the clean retry completed normally.
- **The C-08 flash needed a non-obvious invocation shape**: neither cross-call `cd`, nor `-d`/`-c` flags, nor a PATH-shim script (blocked by the harness's own classifier) worked. The working form, confirmed live: `env -C /workspaces/firestarter pio run -t upload -e leonardo`.
- **A full control-arm arbitration was completed and then retracted by a live ruling** that arrived after the work was already done. No hardware harm resulted (the board was already correctly restored to v1.33 before the ruling arrived), but the evidentiary record (JSONL row, CELL.md framing) needed a full, careful correction rather than a quiet edit.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

Plan 162-06 inherits this plan's leave-state at zero physical cost: Leonardo at `/dev/ttyACM0`, v1.33 arm flashed and independently read-back-proven, W27E512 seated (DIP28, JP4 28-pin, unchanged since Task 4), pot at meter 11.6 V / firmware 12400 mV (in band), Rev 2.0 shield mounted. No blockers.

**Carried forward for every remaining plan in this phase (162-06 through 162-10):** the operator ruling on the divergence trigger — `dev test`'s own v133 verdict (OK -> `same`, no control row; FAIL/BAD -> `diverges`, control-arm arbitration required) is now the sweep's operative rule, superseding CHIP-04/SC#4's original wording (compare against the v1.15 disposition). Plan 162-10's own reconciliation must account for this explicitly, not silently.

The `diagnostic_report.py` export gaps (`steps[].divergence` never serialized; `total`/`bad`/`bad_pct`/`evidence` behind the `indeterminate` fingerprint bucket dropped before export) remain filed in `CELL.md` for Phase 165/166's backlog — not fixed here (D-16 boundary: no product-code changes), and now explicitly not a divergence trigger either way.

---
*Phase: 162-chip-11-part-dev-test-sweep-on-the-reference-rig*
*Completed: 2026-08-28*
