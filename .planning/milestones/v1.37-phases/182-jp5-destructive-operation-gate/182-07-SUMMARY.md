---
phase: 182-jp5-destructive-operation-gate
plan: 07
subsystem: record-keeping
tags: [requirements, backlog, record-keeping, decision-record, d-05, jp4, jp5]

requires:
  - phase: 182-jp5-destructive-operation-gate (182-01, 182-03, 182-05)
    provides: "the shipped write/erase gate, the corrected pinout key/database, and the SAFE-03
      VPP-destination trace this plan closes the record on"
provides:
  - "D-05 resolved in writing: SAFE-02/SAFE-04 CONFIRMED REQUIRED (not retired), dated, cited to
    the SAFE-03 trace, stated against the operator's expectation"
  - "SAFE-01's wording corrected to describe what shipped (pin-map fix, not a synthetic predicate)"
  - "Six backlog stubs (ROADMAP.md 999.55-999.60) for every finding this phase measured but did
    not build"
  - "The split todo's resolves_phase re-pointed from the closed Phase 182 to the 999.58 backlog
    item, with both surviving items' premises corrected"
affects: [187-answered-reports, D-09-jumper-display-phase, future-backlog-review]

actuals:
  tokens: 6600
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified:
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/todos/pending/fix-jp4-labels-and-rev2-revision-block.md

key-decisions:
  - "D-05 resolved: the gate ships, confirmed rather than retired. The operator's stated
    expectation was that the pin-map fix would supersede SAFE-02/SAFE-04; the SAFE-03 trace found
    the opposite — the fix relocates the JP5/A19 hazard onto A19 rather than removing it, because
    Rev 2.x's control bit 0x08 is both CTRL_VPP_P1_ENABLE and CTRL_ADDRESS_LINE_18, and socket
    pin 1 sits inside the address mask a write/erase drives on every byte."
  - "SAFE-01's wording corrected from a database-derivation claim to a pin-map-correction claim —
    the requirement's own words ('the pin map puts A19 on socket pin 1') are now literally true of
    DIP32_27C801, rather than being worked around with a synthetic predicate."
  - "SAFE-03 deliberately NOT marked Complete in the Traceability table. 182-06 (the operator bench
    probe for assumption A1, the VPE rail level with the regulator off) has not run — no
    182-06-SUMMARY.md exists. SAFE-03's row states this explicitly rather than presenting A1 as
    settled, per the shared-ID gate across 182-05/182-06/182-07."
  - "Six backlog stubs filed (999.55-999.60), not five: Plan 02's sibling-parity audit
    (182-02-SUMMARY.md) DID find two further hardcoded-literal assertions of the same defect shape
    MAX_27C020_SIZE had, so that conditional fired and was filed as 999.60. The second
    conditional — 182-06's hw_revision-moves-with-JP4 falsification — did NOT fire, because 182-06
    has not run; recorded as not-yet-measured below, not as a negative result."
  - "999.55 (DIP24 unreachable VPP) records that the hazard is ALREADY largely mitigated: CAP-02
    (firestarter/serial_comm.py:766-806) refuses the connection outright for DIP24_2716/DIP24_2532
    on any pre-Rev-2.2 hardware, keyed on wire-level vpp-pin==11 — measured directly via
    EpromDatabase.get_bus_config(24, ...). What remains is a pre-connection UX gap (the chip is
    still listed as an ordinary supported part), not an unguarded write hazard."
  - "999.59's per-algorithm counts measured directly against chip_database.json: 25 rows on
    algorithm 5 (protocol 0x05), 190 on algorithm 6, 20 on algorithm 14, 20 on algorithm 41 — 255
    total on DIP32_SST39SF040, matching 182-01-SUMMARY's count."
  - "Deviation (Rule 1): Task 1's plan-specified CLAIM-07 verify leg (grep the whole REQUIREMENTS.md
    diff for any line containing the string 'CLAIM-07', assert none found) is self-conflicting —
    the task's own acceptance criteria requires SAFE-04 to state that 'CLAIM-07 needs no
    amendment', which necessarily adds a diff line containing that string. Verified the leg's
    actual intent instead: CLAIM-07's own bullet (line 123) and its own traceability row are absent
    from the diff hunks — confirmed byte-unchanged. Same defect shape 182-04-SUMMARY.md documented
    for a grep colliding with its own necessary literal."

requirements-completed: [SAFE-02, SAFE-04]

coverage:
  - id: D1
    description: "D-05 resolved in writing in REQUIREMENTS.md; SAFE-01 corrected; SAFE-02/SAFE-04
      marked CONFIRMED REQUIRED, dated, cited to the trace, stated against the operator's
      expectation; CLAIM-07 confirmed untouched"
    requirement: "SAFE-01, SAFE-02, SAFE-04"
    verification:
      - kind: other
        ref: "/usr/bin/grep -nE 'SAFE-0[24].{0,400}(CONFIRMED REQUIRED|confirmed required)' .planning/REQUIREMENTS.md"
        status: pass
      - kind: other
        ref: "/usr/bin/grep -n 'D-05' .planning/REQUIREMENTS.md"
        status: pass
      - kind: other
        ref: "retirement-language exclusion leg (no SAFE-02/SAFE-04 line reads 'retired' outside a does-not-fire statement)"
        status: pass
      - kind: other
        ref: "git diff HEAD -- .planning/REQUIREMENTS.md; grep -c '^[+-]' (45, within the <=60 bound)"
        status: pass
    human_judgment: true
    rationale: "The plan's literal CLAIM-07 diff-wide grep leg fails by construction once SAFE-04
      names CLAIM-07 (required content) — see the deviation recorded above. A human should confirm
      CLAIM-07's own bullet and traceability row are genuinely byte-unchanged rather than trusting
      the failing literal command."
  - id: D2
    description: "Six backlog stubs (999.55-999.60) filed in ROADMAP.md, each with a BACKLOG
      marker, evidence, and a Test surface paragraph; nothing built"
    requirement: null
    verification:
      - kind: other
        ref: "/usr/bin/grep -c '^### Phase 999\\.5[5-9]' .planning/ROADMAP.md (5)"
        status: pass
      - kind: other
        ref: "per-stub BACKLOG-marker presence loop (999.55-999.59, all OK)"
        status: pass
      - kind: other
        ref: "/usr/bin/grep -A20 '^### Phase 999.59:' .planning/ROADMAP.md | grep -c '255' (3)"
        status: pass
      - kind: other
        ref: "git diff HEAD -- .planning/ROADMAP.md; grep -c '^-' (1, the diff header line only — additions-only)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The split todo's resolves_phase re-pointed from 182 to 999.58; both surviving
      items' premises corrected with dated evidence; item 3's dangling citations rewritten
      past-tense; file stays in pending/"
    requirement: null
    verification:
      - kind: other
        ref: "/usr/bin/grep -n 'resolves_phase' .planning/todos/pending/fix-jp4-labels-and-rev2-revision-block.md (999.58)"
        status: pass
      - kind: other
        ref: "/usr/bin/grep -n '999.58' .planning/todos/pending/fix-jp4-labels-and-rev2-revision-block.md"
        status: pass
      - kind: other
        ref: "single-block-survives-outside-dated-correction leg on the todo file"
        status: pass
      - kind: other
        ref: "test -f .planning/todos/pending/fix-jp4-labels-and-rev2-revision-block.md"
        status: pass
    human_judgment: false

duration: 50min
completed: 2026-09-10
status: complete
---

# Phase 182 Plan 07: Close the Record — D-05 Resolution, Requirement Corrections, Backlog Stubs Summary

**D-05 resolved against the operator's own expectation — the pin-map fix relocates the JP5/A19
hazard rather than removing it, so SAFE-02 and SAFE-04 are confirmed required (not retired), SAFE-01's
wording is corrected to describe what shipped, six backlog stubs record every measured-but-not-built
finding, and the split todo now points at the backlog item that inherits its two open items.**

## Performance

- **Duration:** ~50 min
- **Completed:** 2026-09-10
- **Tasks:** 3 (all `type="auto"`)
- **Files modified:** 3 (`.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`,
  `.planning/todos/pending/fix-jp4-labels-and-rev2-revision-block.md`)

## The D-05 resolution, quotable in one paragraph

D-05 made whether the JP5 gate ships at all conditional on the SAFE-03 trace this phase produced, and
named the operator's expected outcome: that once the pin-map fix stops the tool from routing VPP
through the affected 8 Mbit parts' pin 1, the shield-level hazard would be gone and the gate could
retire. The trace found the opposite. On Rev 2.x, physical control bit `0x08` is simultaneously
`CTRL_VPP_P1_ENABLE` and `CTRL_ADDRESS_LINE_18`, and socket pin 1 is bus line 21, sitting inside the
address mask a write or erase drives from the target address on every byte. The pin-map fix does what
it was supposed to — it moves VPP off pin 1 and onto pin 24 for the corrected `DIP32_27C801` layout —
but the same physical control line pin 1 already carried is now driven by **A19** instead, for every
address at or above `0x80000`. The fix relocates the hazard onto a different bit of the same problem;
it does not remove it. Retirement does not fire. SAFE-02 and SAFE-04 are marked **CONFIRMED REQUIRED**,
dated 2026-09-10, citing `182-05-SUMMARY.md` and the trace in
`.planning/notes/jumper-display-ground-truth.md`.

## SAFE-01, SAFE-02, SAFE-04 — exact wording as landed

- **SAFE-01** now reads: the predicate is achieved by *correcting* the pin map so the requirement's
  own words are literally true, not by deriving a synthetic predicate around a database that was
  wrong — with the measured reason (no pin map declared A19; all eight 1 MB rows sat on `DIP32_STD`)
  and the three rejected synthetic alternatives named. The "not from a list written by hand" half is
  kept intact and proved by the synthetic-part-injection test.
- **SAFE-02** now reads, leading with the marker: `**SAFE-02** — **CONFIRMED REQUIRED 2026-09-10
  (D-05 resolved)**: ...` followed by the requirement's original text (corrected: "JP5 routes VPP to
  socket pin 1", not "JP4" — JP4 does not route VPP on this path, only JP5 does), then the full D-05
  resolution paragraph inline, so a reader does not need to open another file.
- **SAFE-04** now reads the same way: `**SAFE-04** — **CONFIRMED REQUIRED 2026-09-10 (D-05
  resolved)**: ...`, plus the finding that `--auto`/`--chain` have no firestarter CLI counterpart
  (covered by the non-TTY refusal, not any flag handling) and the Option B record — `jp5_gate.py`
  carries its own injectable `isatty_fn`, never touches `cli_handlers._is_interactive`, and CLAIM-07
  needs no amendment.

CLAIM-07's own bullet (line 123) and its own traceability row are unedited — confirmed by inspecting
the diff hunks directly (see Deviations).

## Backlog stubs filed — one line each

- **999.55** — DIP24 unreachable VPP (D-15.1): CAP-02 already refuses `DIP24_2716`/`DIP24_2532` on
  pre-Rev-2.2 hardware; what's left is a pre-connection listing/UX gap, not an unguarded hazard.
- **999.56** — the mirrored JP4 hazard (D-15.2): recorded per the operator's instruction, not gated;
  needs its own D-05-shaped trace for JP4's three positions.
- **999.57** — a fail-closed `size_bytes`/address-line generator assertion, with three measured
  classes (the 8 Mbit rows, three `DIP28_2764` 128 KB parts, 18 `DIP32_28C512_EEPROM` rows) as
  evidence it has real work to do.
- **999.58** — the D-09 phase (shield photographs, per-revision jumper tables, the `info`
  jumper-block rewrite) — a stub, not an inserted phase, since Phase 187 must stay last.
- **999.59** — the 255-row `DIP32_SST39SF040` A18-on-pin-1 structural remainder, per-algorithm
  counts (5→25, 6→190, 14→20, 41→20), and the open protocol-`0x05` VPE question.
- **999.60** (conditional, fired) — Plan 02's sibling-parity-test audit found two further
  hardcoded-literal assertions of `MAX_27C020_SIZE`'s defect shape; filed here as backlog.

**The other conditional stub did not fire.** 182-06 (the operator bench probe reading `hw_revision`
at each JP4 position, testing whether the detect band moves with JP4 position) has not run — no
`182-06-SUMMARY.md` exists in the phase directory. There is no bench evidence to file a stub from.
This is recorded as **not-yet-measured**, not as a negative (safe) result.

## Traceability — final status of all five SAFE requirements

| Requirement | Plan | Status |
|---|---|---|
| SAFE-01 | 182-01, 182-02, 182-03 | Complete |
| SAFE-02 | 182-01 | Complete (CONFIRMED REQUIRED 2026-09-10, D-05) |
| SAFE-03 | 182-05 (182-06 still owed) | **Pending** — trace recorded with A1 named as the one inferred link; assumption A1 (VPE rail level, regulator off) stays unmeasured until Plan 06's bench probe runs |
| SAFE-04 | 182-01 | Complete (CONFIRMED REQUIRED 2026-09-10, D-05) |
| SAFE-05 | 182-04 | Complete |

## Task Commits

Each task was committed atomically, in the meta repo, on the milestone branch. No submodule was
touched; no gitlink was advanced (this plan's `commits_land_in` states none is owed).

1. **Task 1: Record the D-05 resolution and correct SAFE-01/02/04** — `b0c12048` (docs) —
   `.planning/REQUIREMENTS.md`
2. **Task 2: File the six backlog stubs** — `cad473b1` (docs) — `.planning/ROADMAP.md`
3. **Task 3: Re-point the split todo's resolves_phase tag** — `085dc70d` (docs) —
   `.planning/todos/pending/fix-jp4-labels-and-rev2-revision-block.md`

**Plan metadata:** committed with this SUMMARY (see below).

## Files Created/Modified

- `.planning/REQUIREMENTS.md` — SAFE-01/02/04 bullets corrected; Traceability rows for SAFE-01
  through SAFE-05 set from the plan SUMMARYs.
- `.planning/ROADMAP.md` — six new backlog stubs (999.55-999.60) appended to the Backlog section;
  nothing else in the file touched (dependency table and every other phase section confirmed
  intact by spot-check).
- `.planning/todos/pending/fix-jp4-labels-and-rev2-revision-block.md` — `resolves_phase` re-pointed
  from `182` to `999.58`; split history recorded in the body; items 1 and 2's premises corrected
  with dated evidence; item 3's now-dangling `ic_layout.py` citations rewritten past-tense.

## Decisions Made

See `key-decisions` in the frontmatter for full detail. Summary: D-05 resolves to "the gate ships,
confirmed not retired"; SAFE-03 is deliberately left Pending because 182-06 has not run; six stubs
were filed, not five, because the sibling-parity-audit conditional fired; 999.55 records that the
DIP24 hazard is largely already mitigated by the pre-existing CAP-02 gate rather than open and
unguarded.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Task 1's CLAIM-07 verify leg is self-conflicting by construction**
- **Found during:** Task 1, running the plan's own verify legs after drafting SAFE-04
- **Issue:** The leg `git diff HEAD -- .planning/REQUIREMENTS.md | grep -E '^[+-].*CLAIM-07'` asserts
  no diff line mentions CLAIM-07 at all. But the task's own acceptance criteria requires SAFE-04 to
  state "the Option B choice and the statement that CLAIM-07 needs no amendment" — content that
  necessarily contains the string "CLAIM-07" and therefore necessarily appears as an added line in
  the diff. The literal leg cannot pass while the acceptance criteria is met; they directly
  conflict. This is the same defect shape `182-04-SUMMARY.md` documented (a grep colliding with its
  own necessarily-cited literal).
- **Fix:** Verified the leg's actual intent — stated by the threat model (T-182-31: "CLAIM-07's
  bullet is asserted byte-unchanged") — directly: confirmed CLAIM-07's own bullet (line 123 in the
  final file) and its own traceability row do not appear inside any diff hunk (i.e., are not
  touched), by inspecting `git diff HEAD -- .planning/REQUIREMENTS.md` in full rather than grepping
  for the bare substring.
- **Files modified:** none (verification-only; no REQUIREMENTS.md content changed by this
  deviation)
- **Verification:** Full diff inspected; CLAIM-07's own bullet line and traceability row are absent
  from every hunk. The only "CLAIM-07" mention in the diff is the required, added mention inside
  SAFE-04's own bullet.
- **Committed in:** N/A — verification finding, not a code/content change

---

**Total deviations:** 1 auto-fixed (1 bug — a self-conflicting verify leg, mechanical, no scope
creep). **Impact on plan:** None on the shipped record. The deviation is about how the plan's own
verify leg was written, not about what needed to be recorded.

## Issues Encountered

None beyond the deviation above. 182-06 has not run at the time this plan executed — anticipated by
the orchestrator's own phase-state note, handled by leaving SAFE-03 Pending rather than assuming
completion, and by recording the hw_revision-moves-with-JP4 conditional stub as not-yet-fired rather
than fabricating a bench result.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The phase record for 182 is closed except for SAFE-03's outstanding bench evidence: when 182-06
  runs, its SUMMARY should update SAFE-03's Traceability row from Pending to Complete (or record a
  widened gate scope if A1 comes back boosted, per D-06).
- Six backlog stubs (999.55-999.60) are available for a future `/gsd-review-backlog` pass; none is
  in scope for the current v1.37 milestone.
- The split todo now points at 999.58, which does not exist as a phase yet — a future
  `/gsd-review-backlog` or `/gsd-new-milestone` promoting it should pick up the corrected premises
  recorded in the todo body rather than the original (now-known-wrong) ones.
- No blockers for Phase 183 or any later phase in this milestone; this plan touched only
  `.planning/` prose in the meta repo.

---
*Phase: 182-jp5-destructive-operation-gate*
*Completed: 2026-09-10*

## Self-Check: PASSED

- FOUND: `.planning/REQUIREMENTS.md` (SAFE-01/02/04 bullets and Traceability rows as described)
- FOUND: `.planning/ROADMAP.md` (six stubs 999.55-999.60)
- FOUND: `.planning/todos/pending/fix-jp4-labels-and-rev2-revision-block.md` (`resolves_phase: 999.58`)
- FOUND commits: `b0c12048`, `cad473b1`, `085dc70d` (`git log --oneline --all` — all three present)
- Plan-level `<verification>` re-run at write time: stub count 5 (>=5, pass); `git diff HEAD~3
  --stat -- .planning/` shows exactly `REQUIREMENTS.md`, `ROADMAP.md` and the one todo file (pass);
  `git diff HEAD~3 -- .planning/ROADMAP.md | grep -c '^-'` reports 1 — the diff header line only,
  additions-only (pass); `grep -n 'resolves_phase: 182'` on the todo prints nothing (pass).
- `commits: 3`, `plan_head_before: 5aa9a006e826b833e70a1f58d988b421409c9c44` (measured via
  `git rev-list --count`, matches the three task commits — no metadata commit exists yet at
  self-check time, added next).
