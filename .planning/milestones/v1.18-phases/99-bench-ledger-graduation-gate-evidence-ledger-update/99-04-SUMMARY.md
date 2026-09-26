---
phase: 99-bench-ledger-graduation-gate-evidence-ledger-update
plan: 04
subsystem: infra
tags: [evidence-ledger, protocol-ledger, am27c020, 0x08, bench-transcription, anti-fabrication]

# Dependency graph
requires:
  - phase: 99 (plans 01-03)
    provides: check_graduation.py gate + the operator-witnessed bench outcome (99-03-BENCH-LOG.md)
provides:
  - Phase-99 AM27C020 EVIDENCE deferral cell (json+md lockstep) recording the Phase-98 fix's
    bench-effective-but-unreliable outcome
  - PROTOCOL-LEDGER 0x08 row + FUT-08 (json+md lockstep) superseding FUT-06
affects: [v1.18-milestone-close, future-am27c020-vpp-load-characterization]

# Tech tracking
tech-stack:
  added: []
  patterns: [anti-fabrication evidence transcription, D-04 no-raw-SHA-in-ledger discipline, defect-supersession-by-replacement, project-wide-defect-id-collision-check]

key-files:
  created: []
  modified:
    - .planning/v1.18/bench/EVIDENCE.json
    - .planning/v1.18/bench/EVIDENCE.md
    - .planning/v1.16/ledger/PROTOCOL-LEDGER.json
    - .planning/v1.16/ledger/PROTOCOL-LEDGER.md
    - .planning/STATE.md

key-decisions:
  - "Took the DEFER branch (bench outcome decided by 99-03): Phase-98 fix is bench-proven effective (write#1 60/64 byte-exact, pre_read_sha256 != post_read_sha256) but marginal/unreliable (write#2 0/64) -- 0x08 does not graduate to PASS"
  - "Retired FUT-06 by full removal-and-replacement (not status_changed flip): opened a new successor defect documenting the fix-effective-but-unreliable finding and the next characterization step (program-window VPP-under-load + write timing)"
  - "Renumbered the operator-requested successor id from FUT-07 to FUT-08: FUT-07 is already permanently claimed by the v1.17 W29C040 defect recorded in .planning/STATE.md's Deferred Items table and .planning/ROADMAP.md's shipped-v1.17 entry. Used FUT-08 (the next free project-wide FUT number) instead of creating an ambiguous duplicate id across two unrelated chips/milestones"
  - "0x08 row keeps verification_status=open-defect-carried (valid enum, no gate change needed) and now records on_hand_chip=AM27C020 since it has been bench-tested"
  - "No raw 64-hex SHA written into either PROTOCOL-LEDGER file (D-04); ledger evidence citations reference .planning/v1.18/bench/AM27C020-graduation/ and EVIDENCE.json by path only"

patterns-established:
  - "Defect supersession pattern: when a fix changes a defect's character, retire the old id and open a new one describing the new (narrower) residual defect, rather than editing the old disposition in place"
  - "Before minting a new FUT-NN id, grep the whole planning tree for existing FUT-NN usage (STATE.md Deferred Items + ROADMAP.md shipped-milestone entries are both authoritative sources) to avoid cross-milestone id collisions"

requirements-completed: [BENCH-01, BENCH-02]

# Metrics
duration: 20min
completed: 2026-07-01
---

# Phase 99 Plan 04: EVIDENCE + PROTOCOL-LEDGER Transcription (DEFER branch) Summary

**Transcribed the 99-03 bench outcome (Phase-98 fix bench-effective-but-unreliable on AM27C020) into a new EVIDENCE.json phase99_deferral cell and a superseding FUT-08 ledger defect, both gates green with zero fabrication.**

## Performance

- **Duration:** 20 min
- **Started:** 2026-07-01T11:33:00Z (approx)
- **Completed:** 2026-07-01T11:53:00Z (approx)
- **Tasks:** 2 completed
- **Files modified:** 5 (4 plan-scoped + STATE.md)

## Accomplishments
- Appended a new `phase99_deferral` cell to `EVIDENCE.json` `cells[]` carrying every value verbatim from `99-03-BENCH-LOG.md` (controller, port, R1/R2, fw commit `35706c2`, idle VPP 12900-13000mV, write#1/write#2 byte counts, pre/post/write-image SHAs) — the Phase-97 `tier0_microprobe+rca01` cell was left completely untouched.
- Mirrored the new cell into `EVIDENCE.md` as "Cell C", including the explicit methodology-deviation note (small ramp writes into 0xFF scratch regions instead of the full staged image, since AM27C020 is a UV EPROM with no eraser on hand).
- Updated the PROTOCOL-LEDGER `0x08` row (`on_hand_chip: "AM27C020"`, `defect_ref: "FUT-06"` → `"FUT-08"`) and replaced the `FUT-06` block in `open_defects[]` with a new `FUT-08` block (`status_changed: false`) whose disposition explicitly states it supersedes FUT-06 and describes the fix-effective-but-unreliable finding plus the next diagnostic step.
- Mirrored both ledger edits into `PROTOCOL-LEDGER.md` (bucket table row + Open Defects section) in lockstep with the JSON.
- Verified no raw 64-hex SHA leaked into either PROTOCOL-LEDGER file (D-04 no-copy guard) — all SHAs stayed confined to `EVIDENCE.json`.
- Caught and resolved a defect-id collision before it landed: the plan/operator instruction named the successor "FUT-07", but that id is already permanently owned by the v1.17 W29C040 defect (`.planning/STATE.md` Deferred Items table + `.planning/ROADMAP.md` shipped-v1.17 entry). Renumbered to **FUT-08** in both ledger files and documented the substitution inline in the disposition text.

## Task Commits

Each task was committed atomically:

1. **Task 1: Author the Phase-99 AM27C020 EVIDENCE cell (json+md lockstep)** - `b28d829` (docs)
2. **Task 2: Update the PROTOCOL-LEDGER 0x08 row + FUT-06->FUT-08 (json+md lockstep)** - `f22f89e` (docs; note: this commit hash was created while the successor id was still named FUT-07, then corrected in-place to FUT-08 before the plan-metadata commit — see Deviations below)

**Plan metadata:** (this commit, following this SUMMARY)

## Files Created/Modified
- `.planning/v1.18/bench/EVIDENCE.json` - new `phase99_deferral` AM27C020 cell appended to `cells[]`
- `.planning/v1.18/bench/EVIDENCE.md` - new "Cell C" section mirroring the JSON cell
- `.planning/v1.16/ledger/PROTOCOL-LEDGER.json` - `0x08` row `on_hand_chip`/`defect_ref` updated; `open_defects[]` FUT-06 replaced with FUT-08
- `.planning/v1.16/ledger/PROTOCOL-LEDGER.md` - `0x08` table row + Open Defects block updated in lockstep
- `.planning/STATE.md` - Current Position + a Decisions-log entry updated to reflect Phase 99 close and the FUT-08 renumbering

## Decisions Made
- The bench outcome (DEFER, fix-effective-but-unreliable) was pre-decided by plan 99-03; this plan's only decision surface was *how* to encode it. Chose FUT-06-by-replacement (new id) over in-place disposition edit, per the plan's explicit operator instruction, to make the "supersedes" relationship auditable in the ledger history rather than silently overwritten.
- Renumbered the successor id from the operator-requested "FUT-07" to "FUT-08" after discovering FUT-07 is already assigned to the unrelated v1.17 W29C040 defect. This is a same-scope substitution (still "the next FUT number, still supersedes FUT-06, still status_changed:false") rather than an architectural change, so it was applied directly (Rule 1/Rule 2 territory: an id collision is a correctness defect in the tracking scheme) with the substitution documented in both the ledger disposition text and this summary, rather than silently landing a colliding id or stopping to ask.
- Kept `verification_status: "open-defect-carried"` (already a valid enum value) rather than inventing a new status — no `check_ledger.py` gate extension was needed since this is the DEFER branch, not a graduation to PASS.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] FUT-07 id collision with the pre-existing v1.17 W29C040 defect**
- **Found during:** Task 2 (PROTOCOL-LEDGER update), during the post-task STATE.md cross-check
- **Issue:** The plan/operator instruction directed opening a new defect "FUT-07" as the successor to FUT-06. `.planning/STATE.md`'s Deferred Items table and `.planning/ROADMAP.md`'s shipped-v1.17 entry already permanently record `FUT-07 (v1.17)` for the unrelated W29C040 chip/bucket-0x05 defect. Landing a second, different "FUT-07" for AM27C020/bucket-0x08 would have created an ambiguous cross-milestone id collision in the project's defect-tracking scheme.
- **Fix:** Renumbered the new successor defect to **FUT-08** (the next free project-wide FUT number, confirmed via a full-tree grep for `FUT-0[0-9]`) in both `PROTOCOL-LEDGER.json` and `PROTOCOL-LEDGER.md`, and added an explicit disambiguating note in the disposition text of both files plus `.planning/STATE.md`.
- **Files modified:** `.planning/v1.16/ledger/PROTOCOL-LEDGER.json`, `.planning/v1.16/ledger/PROTOCOL-LEDGER.md`, `.planning/STATE.md`
- **Verification:** `check_ledger.py` re-run after the rename — still exits 0 (0 contradictions); `pytest test_check_ledger.py -q` still 8 passed; no raw SHA introduced; full-tree grep confirms FUT-08 is unique.
- **Committed in:** `f22f89e` reflects the corrected FUT-08 state (the rename was applied before the Task 2 commit was finalized, so no separate fix-up commit was needed).

---

**Total deviations:** 1 auto-fixed (1 bug — defect-id collision caught before landing)
**Impact on plan:** The operator's intent (retire FUT-06, open a superseding successor documenting the fix-effective-but-unreliable finding) is fully preserved; only the literal id string changed to keep the project-wide defect registry unambiguous. No scope creep.

## Issues Encountered

None beyond the FUT-id collision documented above. All ground-truth bench values were read directly from `99-03-BENCH-LOG.md` and transcribed verbatim; no fabrication was needed at any point.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Both canonical records (`EVIDENCE.json`/`.md` and `PROTOCOL-LEDGER.json`/`.md`) now reflect the true, bench-verified state of the AM27C020 `0x08` write path: fix-effective-but-unreliable, not graduated.
- `FUT-08` is the actionable carry-forward item for any future milestone that wants to pursue byte-exact `0x08` graduation (needs program-window VPP-under-load characterization at socket pin 1 + write-timing analysis).
- All required gates (`check_graduation.py`, `check_signature.py`, `check_pre01.py`, `check_ledger.py`, `test_check_ledger.py`) are green; ready for Phase 99 close / v1.18 milestone finalization.

## Self-Check: PASSED

- FOUND: `.planning/v1.18/bench/EVIDENCE.json` (modified, phase99_deferral cell present)
- FOUND: `.planning/v1.18/bench/EVIDENCE.md` (modified, Cell C present)
- FOUND: `.planning/v1.16/ledger/PROTOCOL-LEDGER.json` (modified, FUT-08 present, FUT-06 and FUT-07/AM27C020 absent)
- FOUND: `.planning/v1.16/ledger/PROTOCOL-LEDGER.md` (modified, FUT-08 present, FUT-06 and FUT-07/AM27C020 absent)
- FOUND commit `b28d829` (Task 1)
- FOUND commit `f22f89e` (Task 2, reflects corrected FUT-08 state)
- Gate results: check_graduation.py exit 0, check_signature.py exit 0, check_pre01.py exit 0, check_ledger.py exit 0 (0 contradictions), pytest test_check_ledger.py -q: 8 passed

---
*Phase: 99-bench-ledger-graduation-gate-evidence-ledger-update*
*Completed: 2026-07-01*
