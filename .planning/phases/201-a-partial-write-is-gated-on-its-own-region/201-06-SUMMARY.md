---
phase: 201-a-partial-write-is-gated-on-its-own-region
plan: 06
subsystem: firmware
tags: [bench, eprom, uv-eprom, blank-check, firestarter_fw, firestarter_app]

requires:
  - phase: 201 (plans 01-05)
    provides: the region-scoped write-init blank check (`mem_util_blank_check_region`), the
      `region-end` wire field on both repos, the write/verify bounding, and the D-15.3
      source-contract gate — all landed and green before this bench session ran
provides:
  - a measured, on-silicon confirmation that criterion 1 of Phase 201 holds on a genuinely
    non-erasable part (UV-EPROM, `FLAG_CAN_ERASE` clear)
  - `201-BENCH-RECORD.md`, the evidence artifact: two RED-then-GREEN W27C512 rehearsal pairs plus
    one confirming M27C512 run, all committed and labelled as evidence
affects: [phase-201-close, v1.40-milestone-close]

actuals:
  tokens: 8000
  tasks: 1
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Bench evidence committed as a labelled, non-re-runnable artifact (D-16.4), following the
      Phase 194 `W29C020` precedent"
    - "Operator-authorised deviation from a plan's named part/address, recorded in the artifact
      itself with the reason and the authoriser, rather than silently substituted"

key-files:
  created:
    - .planning/phases/201-a-partial-write-is-gated-on-its-own-region/201-06-SUMMARY.md
  modified:
    - .planning/phases/201-a-partial-write-is-gated-on-its-own-region/201-BENCH-RECORD.md
    - .planning/phases/201-a-partial-write-is-gated-on-its-own-region/deferred-items.md
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/STATE.md

key-decisions:
  - "The plan's named TMS27C512 was not on hand. The operator substituted an ST M27C512
    (chip-ID 0x203D, not the plan's expected 0x9785) and authorised proceeding after being shown
    that the database clears FLAG_CAN_ERASE for it on the identical basis (electrical-type:
    UV-EPROM) that would clear it for a TMS27C512 — so criterion 1's word non-erasable rests on
    the same measured basis the plan specified, just on a different part."
  - "The plan's target address 0x00FF00 was unusable on this M27C512: a full-device read-back
    showed it as the single last blank byte before a programmed descending ramp starting at
    0x00FF01, so a 64-byte write there would collide with programmed data one byte in. The
    operator authorised 0x008000 instead, which sits inside the blank span and is far from data on
    both sides — a stronger case than the plan's one-sided W27C512 rehearsal, since this device
    holds programmed bytes below AND above the confirming target."
  - "The bench record's TMS27C512 section was retitled to name the part genuinely in the socket
    (M27C512), per D-16.4's rule that the record must not claim a part that was never present."

requirements-completed: [BLANK-01, BLANK-03]

coverage:
  - id: D1
    description: "A write into a blank region of a non-blank, non-erasable part succeeds on real
      silicon (criterion 1 / BLANK-01), confirmed once against an ST M27C512 (FLAG_CAN_ERASE
      clear) at 0x008000, with a full-device read-back proving data on both sides of the target."
    requirement: BLANK-01
    verification:
      - kind: manual_procedural
        ref: ".planning/phases/201-a-partial-write-is-gated-on-its-own-region/201-BENCH-RECORD.md
          § M27C512 confirmation — three-step transcript (blank-check refused at 0x000000,
          write succeeded at 0x008000, verify clean)"
        status: pass
    human_judgment: true
    rationale: "This is a bench session on real Arduino/RURP hardware and a real UV-EPROM chip
      that cannot be re-erased in this session. No automated suite can reach it; the evidence is
      a human-operated transcript, and the write is irreversible so it cannot be re-run to
      generate a second, automatable data point."
  - id: D2
    description: "BLANK-03's regression coverage — a UV part holding data outside the target slot
      accepts a slot write — is satisfied by the same M27C512 confirming run as D1, plus the
      software-side regression tests landed in plans 201-01 through 201-05 (native multi-chunk
      resumption, erase-end arm, source-contract gate, host write -a against fake_chip.py)."
    requirement: BLANK-03
    verification:
      - kind: manual_procedural
        ref: "same bench transcript as D1"
        status: pass
    human_judgment: true
    rationale: "Same bench-only reachability constraint as D1 — the UV-EPROM confirming run is the
      irreplaceable half of this requirement's evidence."

duration: 55min
completed: 2026-09-20
status: complete
---

# Phase 201 Plan 06: Bench Record — Non-Erasable Silicon Proof of Criterion 1 Summary

**A write into a blank region of a non-blank ST M27C512 (UV-EPROM, FLAG_CAN_ERASE clear) succeeded on real silicon at an operator-relocated target address, closing criterion 1 of Phase 201 and completing v1.40's last phase.**

## Performance

- **Duration:** 55 min (this continuation dispatch; Tasks 1-2 ran in a prior session)
- **Started:** 2026-09-20T09:13:00Z
- **Completed:** 2026-09-20T09:20:00Z
- **Tasks:** 1 of 3 in this dispatch (Task 3 — Tasks 1 and 2 completed and left `201-BENCH-RECORD.md`
  populated through the W27C512 rehearsal in a prior session)
- **Files modified:** 5 (`201-BENCH-RECORD.md`, `deferred-items.md`, `REQUIREMENTS.md`,
  `ROADMAP.md`, `STATE.md`)

## Accomplishments

- Closed criterion 1 of Phase 201 on real, non-erasable silicon: a write into a blank 64-byte
  region at `0x008000` of an ST M27C512 succeeded while the part held 16 bytes of programmed data
  at `0x000000`-`0x00000F` and 255 bytes of programmed data at `0x00FF01`-`0x00FFFF` — data on
  *both* sides of the target, a stronger case than the plan's one-sided W27C512 rehearsal.
- Recorded and authorised two operator deviations from the plan's exact wording, each with a
  measured reason: the confirming part (ST M27C512, not TMS27C512 — chip-ID `0x203D`, not
  `0x9785`) and the target address (`0x008000`, not `0x00FF00` — the plan's address was one byte
  from a programmed ramp on this specific part).
- Closed `201-BENCH-RECORD.md` with a `## How to read this record` section stating plainly which
  claims (criterion 1 on non-erasable silicon) rest on this file alone versus which are also
  covered by the native and host suites landed in plans 201-01 through 201-05.
- Marked BLANK-01 and BLANK-03 Complete in `REQUIREMENTS.md`, verified ready via
  `gsd-tools query requirements.ready-ids` rather than by hand-judgment. BLANK-02 (already
  Complete from plan 201-05) was left untouched.
- Phase 201 is now 6/6 plans complete — the last of v1.40's five phases. `STATE.md` and
  `ROADMAP.md` both now reflect the milestone as ready for `/gsd-complete-milestone`.

## Task Commits

Tasks 1 and 2 (rig setup, chip-ID confirmation of the W27C512, and the two RED-then-GREEN
rehearsal pairs) were completed and their content written into `201-BENCH-RECORD.md` in a prior
session; that session did not commit the file, so this dispatch's commits carry all of Task 1-2's
recorded content in addition to Task 3's:

1. **Task 3: Confirm once on the ST M27C512 and commit the transcript as evidence** —
   `6dbae72f` (docs) — the full bench record: Session setup, W27C512 rehearsal (two RED/GREEN
   pairs), the M27C512 confirmation section with both operator-authorised deviations, and
   "How to read this record".
2. **Out-of-scope discovery, logged not fixed** — `496ffca8` (docs) — `deferred-items.md`,
   recording that a pre-existing untracked file in `firestarter_app` (predates this phase) makes
   the submodule read dirty in `git status --porcelain`, unrelated to this plan's own work.

**Plan metadata:** commit pending (this SUMMARY + STATE.md + ROADMAP.md + REQUIREMENTS.md)

## Files Created/Modified

- `.planning/phases/201-a-partial-write-is-gated-on-its-own-region/201-BENCH-RECORD.md` — the
  complete bench evidence artifact (562 lines): session setup, two RED/GREEN W27C512 rehearsal
  pairs, the M27C512 confirming run with both deviations recorded, and the closing
  "How to read this record" section.
- `.planning/phases/201-a-partial-write-is-gated-on-its-own-region/deferred-items.md` — one
  out-of-scope discovery (pre-existing untracked file affecting a dirty-check verify leg).
- `.planning/REQUIREMENTS.md` — BLANK-01 and BLANK-03 marked Complete (checkbox + traceability
  table); BLANK-02 untouched.
- `.planning/ROADMAP.md` — Phase 201's `**Plans:**` line updated to `6/6 plans complete`; plan
  201-06's checkbox flipped to `[x]` with both deviations recorded inline.
- `.planning/STATE.md` — frontmatter (`status`, `stopped_at`, `last_updated`, `last_activity_desc`,
  `progress` block corrected to `completed_phases: 5`/`completed_plans: 26`/`percent: 100`) and
  body (`**Current focus:**`, `## Current Position`) both updated by hand, per this project's
  established practice of hand-editing STATE.md/ROADMAP.md rather than trusting the `gsd-tools
  query state.*`/`roadmap.*` verbs, which are documented in this project's memory as corrupting
  frontmatter and clobbering unrelated ROADMAP rows in this repo.

## Decisions Made

- **Proceed on the ST M27C512 substitute.** The operator does not have a TMS27C512. The plan's own
  Task 3 action anticipated exactly this reading and named the criterion that governs it
  ("...the operator must decide whether it still satisfies criterion 1's word *non-erasable*
  before anything is written"). The operator decided to proceed, and the decision is grounded in
  `firestarter info m27c512`'s database output (`Can be erased: no (UV erase only)`, flags
  `0x00000020` — `FLAG_OUTPUT_ENABLE`, with `FLAG_CAN_ERASE` (`0x02`) absent) rather than in
  assertion.
- **Relocate the confirming target from `0x00FF00` to `0x008000`.** A full-device read-back (not
  the operator's belief) showed `0x00FF00` is the last blank byte before a programmed ramp, one
  byte from collision. `0x008000` sits deep in the blank span and is measurably farther from
  programmed data on both sides than the plan's original address would have been from the single
  side the W27C512 rehearsal exercised.
- **Two separate meta commits, not one.** Task 3's acceptance criteria required the bench-record
  commit to contain only `201-BENCH-RECORD.md`. `deferred-items.md` (an out-of-scope discovery
  from Tasks 1-2, unrelated to Task 3's content) was committed separately immediately after, so
  both artifacts land without either commit message misdescribing its contents.
- **Hand-edit STATE.md and ROADMAP.md rather than call the corresponding `gsd-tools` verbs.** This
  project's accumulated memory documents `state.*` verbs corrupting frontmatter (mangled titles,
  regressed `progress.percent`, destroyed `last_activity_desc`) and `roadmap.update-plan-progress`
  clobbering an unrelated phase's dependency-table row in this specific repo's non-standard
  Progress table shape. Hand-editing produced a two-line ROADMAP diff and a fully-YAML-valid
  STATE.md diff, both confirmed by direct inspection.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 4 - Architectural, operator-adjudicated] Part substitution: TMS27C512 → ST M27C512**
- **Found during:** Task 3 checkpoint (chip-ID read after the operator seated the confirming part)
- **Issue:** The plan named the TMS27C512 as the confirming part, chip-ID `0x9785`. The operator
  does not have one; the part physically on hand read as an M27C512, chip-ID `0x203D` (matched to
  two database rows: SGS-THOMSON and ST manufacturers).
- **Decision:** The plan's own Task 3 action anticipated this exact outcome and named the
  criterion the operator must adjudicate (non-erasability). The operator, shown the database's
  `Can be erased: no (UV erase only)` and the `FLAG_CAN_ERASE`-clear flag value, authorised
  proceeding.
- **Files modified:** `201-BENCH-RECORD.md` (section retitled from "TMS27C512 confirmation" to
  "M27C512 confirmation", the part actually in the socket)
- **Verification:** `firestarter info m27c512` output captured verbatim in the record; the
  `Flags: 0x00000020` value checked against `constants.py`'s `FLAG_CAN_ERASE = 0x02` to confirm
  the bit is clear
- **Committed in:** `6dbae72f`

**2. [Rule 4 - Architectural, operator-adjudicated] Target address: 0x00FF00 → 0x008000**
- **Found during:** Task 3's full-device read-back, run to establish the pre-write state
- **Issue:** The plan's address `0x00FF00` is the single last blank byte before a programmed
  descending ramp starting at `0x00FF01` on this specific M27C512 — a 64-byte write there would
  collide with programmed data one byte in.
- **Decision:** The operator authorised `0x008000` instead, from the read-back map, after being
  shown the full 0x10000-byte device map (271 non-`0xFF` bytes total, in two blocks at each end).
- **Files modified:** `201-BENCH-RECORD.md` (Deviation 2 subsection, full-device map, pre-write
  read-back at both windows)
- **Verification:** Read-back at `0x008000` (64 bytes) confirmed all `0xFF` immediately before the
  write — the last-reversible-moment check the plan requires
- **Committed in:** `6dbae72f`

---

**Total deviations:** 2, both Rule 4 (architectural/operator-adjudicated), both explicitly
anticipated and gated by the plan's own Task 3 wording, both authorised by the operator at the
blocking-human checkpoint before any write occurred.
**Impact on plan:** Neither changes what criterion 1 required — a write into a blank region of a
non-blank, non-erasable part. Both deviations are recorded prominently in the bench record itself,
in `ROADMAP.md`'s plan line, and in this SUMMARY, with reasons and the authorising party named at
each point, per D-16.4's rule that evidence must not misrepresent what was actually done.

## Issues Encountered

The `firestarter read` command's output-file padding (a 64-byte read at a non-zero address
produces a file padded from address 0, so the requested bytes live at file offset = address, not
at offset 0) was identified in the dispatch's own scope note before this session and confirmed in
practice: the pre-write blank confirmation read `confirm_preread.bin` at 32832 (`0x8040`) bytes for
a 64-byte read at `0x008000`, and the correct 64-byte window was extracted from file offset
`0x8000` rather than from the start of the file. Recorded in the bench record's "Last reversible
moment" subsection so a later reader does not repeat the misread.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 201 is complete (6/6 plans), the last of v1.40's five phases (197-201, all now complete).
All three repositories (`/workspaces`, `firestarter_fw`, `firestarter_app`) are on
`v1.40-program-parameter-fidelity`; `firestarter_fw` has zero tracked or untracked changes;
`firestarter_app` has zero tracked modifications (its one untracked file,
`datasheets/LST62832I.pdf`, predates this phase and is logged in `deferred-items.md`).
`REQUIREMENTS.md` now shows all three BLANK requirements Complete. The milestone is ready for
`/gsd-complete-milestone` — no blockers identified.

---
*Phase: 201-a-partial-write-is-gated-on-its-own-region*
*Completed: 2026-09-20*
