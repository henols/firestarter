---
phase: 205-the-pre-flights-leave-the-firmware
plan: "07"
subsystem: bench, firmware-build, host-cli
tags: [bench, w27c512, blank-check, erase, write, avr, platformio, session-cost]

requires:
  - phase: 205-01
    provides: "erase -b re-implemented host-side (FWBLANK-02), exercised end to end at B7"
  - phase: 205-02
    provides: "the phase-entry firmware sha (a4e002f2) and its .hex digests, reproduced locally at
      B1 as the pre-205 bench artifact"
  - phase: 205-03
    provides: "the write-init/erase-end blank-check machinery deleted from the firmware,
      exercised (its absence) at B5"
  - phase: 205-04
    provides: "FLAG_SKIP_BLANK_CHECK (0x08) fully retired, which is the mechanism the D-07 skew
      leg (B3) observes on silicon"
  - phase: 205-06
    provides: "the phase-exit firmware sha (6e11d05) and its .hex digest, matched at B4; the kept
      and annotated MSG_ERR_NOT_BLANK (0xB0) catalog id, rendered verbatim at B3"
provides:
  - "205-BENCH-MATRIX.md: rig identity, both firmware roles named by sha and .hex digest, B0
    through B7 with exact commands/verbatim output/exit codes/durations, a closed whole-device
    digest chain, and four stated coverage gaps"
  - "205-SESSION-COST.md: erase -b's measured added wall-clock (10.632s, Leonardo-class, N=3)
    alongside the labelled derivation over Phase 203's cited connect-term medians, for Phase
    206's SESS-01"
affects: [206]

actuals:
  tokens: 10900
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "A pre-phase firmware artifact for a bench skew leg is built from a detached git worktree
      at the phase-entry sha, never by checking out the live tree to a different commit --
      keeps every digest and sha recorded by sibling plans valid throughout."
    - "A single non-blank target address, written and overwritten across firmware roles, tests
      both the refusal (pre-205) and the acceptance (post-205) with one whole-device digest
      chain instead of a separate matrix per criterion."
    - "A bench session's own measured wall-clock and a labelled derivation over a prior phase's
      cited figures are recorded side by side, never blended, when the measured figure includes
      cost (here, whole-device read traffic) the derivation deliberately excludes."

key-files:
  created:
    - .planning/phases/205-the-pre-flights-leave-the-firmware/205-BENCH-MATRIX.md
    - .planning/phases/205-the-pre-flights-leave-the-firmware/205-SESSION-COST.md
  modified: []

key-decisions:
  - "The non-blank target for B2/B3/B5/B6 is address 0x000000 with a 64-byte pattern, not a
    separate low-address anchor plus a distant target address as Phase 201-06's rehearsal used.
    One address serves every leg: B2 establishes it non-blank, B3 shows the pre-205 refusal
    against it, B5 shows the post-205 acceptance overwriting it, and B6 shows the erasable path
    overwriting it again -- one whole-device digest chain covers all four legs instead of one
    chain per address."
  - "-f/--force was required on every command against the seated part, for the same documented
    reason 204-BENCH-MATRIX.md recorded: the rig's VPP monitor is a known-noisy proxy that does
    not reliably route to the socket, and an unforced attempt is refused at the chip-ID
    precheck (0x1818 vs expected 0xda08 -- the same WINDOWS.md entry 3 reading) before any chip
    content is exchanged. Forcing past it changes nothing about which command or ordinal is
    sent on the wire."
  - "The operator's Task 1 statement that the seated part IS a W27C512 is recorded as
    independent evidence about the physical part, distinct from and not a resolution of
    WINDOWS.md entry 3's open firmware-side chip-ID mismatch -- the firmware's own chip-ID
    probe still read 0x1818 this session, unforced. Both statements are recorded; neither
    silently overwrites the other."
  - "erase -b's added wall-clock is MEASURED in this plan (10.632s, Leonardo-class, N=3 runs
    each) rather than only derived, per Fork C -- the board was already in the loop for three
    other legs. The measured figure and the derivation over Phase 203's cited connect-term
    medians (2.607s) are recorded side by side rather than reconciled, because the measured
    figure legitimately includes the second port open's own whole-device read traffic (7.40s
    for this 64 KiB part), which the connect-term derivation deliberately excludes."

requirements-completed: [FWBLANK-01, FWBLANK-02, FWBLANK-04]

coverage:
  - id: D1
    description: "A write to a non-blank part on the UV handler reaches the firmware unrefused
      and programs the region it was given, confirmed on silicon by read-back match and a
      whole-device digest showing exactly the expected change (criterion 3, B5)."
    requirement: FWBLANK-01
    verification:
      - kind: manual_procedural
        ref: "205-BENCH-MATRIX.md B5 -- write -b exit 0, verify match 0 bad of 64, whole-device
          digest 88fc2b44... differing from the B2/B3 anchor exactly at the target region"
        status: pass
    human_judgment: true
    rationale: "Real Arduino/RURP hardware and a real seated EPROM. No automated suite can reach
      silicon; the evidence is a bench transcript with a captured digest chain, not a re-runnable
      test."
  - id: D2
    description: "One UV-handler leg (B5) and one erasable leg (B6) show no behaviour change
      other than where the refusal now comes from -- criterion 5, one part in two roles."
    requirement: FWBLANK-04
    verification:
      - kind: manual_procedural
        ref: "205-BENCH-MATRIX.md B6 -- plain write exit 0, whole-device digest differs from B5
          exactly at the target region, no refusal on either side of this phase on this path"
        status: pass
    human_judgment: true
    rationale: "Same bench-only reachability as D1 -- criterion 5 is a claim about an absence,
      and its whole value is in having been run on real silicon."
  - id: D3
    description: "The D-04 skew is captured verbatim on pre-205 firmware, before the reflash,
      with exit code and duration (D-07)."
    requirement: FWBLANK-04
    verification:
      - kind: manual_procedural
        ref: "205-BENCH-MATRIX.md B3 -- MSG_ERR_NOT_BLANK (0xB0) rendered verbatim as 'Not blank,
          at 0x000000, v: 0x11', exit 1, duration 3.81s, post-refusal digest identical to B2"
        status: pass
    human_judgment: true
    rationale: "A claim about what a real user with an un-reflashed board will experience,
      observed rather than argued, per 204's precedent for this exact class of claim."
  - id: D4
    description: "Both firmware roles are named by commit sha and .hex digest, with the label
      substitution stated; the pre-205 artifact is a local build reproducing the phase-entry
      digest exactly."
    requirement: FWBLANK-04
    verification:
      - kind: other
        ref: "205-BENCH-MATRIX.md B1/B4 -- pre-205 .hex sha256 8beeb731... matches
          205-FLASH-RAM.md's phase-entry digest exactly; post-205 .hex sha256 38ed1da7... matches
          the phase-exit digest exactly"
        status: pass
    human_judgment: false
  - id: D5
    description: "erase -b runs end to end on silicon (three times, exit 0 each) and its added
      wall-clock is measured (10.632s, Leonardo-class, N=3), with a labelled derivation (2.607s,
      connect-term only) recorded beside it for Phase 206."
    requirement: FWBLANK-02
    verification:
      - kind: manual_procedural
        ref: "205-BENCH-MATRIX.md B7, 205-SESSION-COST.md SS 2-4"
        status: pass
    human_judgment: true
    rationale: "A real bench timing measurement; not reproducible by an automated suite."
  - id: D6
    description: "Every UV leg records that it ran on an erasable proxy (no true UV part
      available), and the four stated coverage gaps (proxy, 0x10 unbenchable, 0x06's sole
      SST39SF020 unseated -- quoting Phase 201's finding verbatim, no Uno-class board) are
      recorded rather than hidden."
    requirement: FWBLANK-01
    verification:
      - kind: other
        ref: "205-BENCH-MATRIX.md 'Stated coverage gaps' section; 'proxy' appears 5 times across
          the record, including on B2/B3/B5/B7 themselves"
        status: pass
    human_judgment: false

duration: ~20min
completed: 2026-09-22
status: complete
---

# Phase 205 Plan 07: Bench Matrix -- criteria 3 and 5 confirmed on silicon, the D-04 skew captured verbatim, erase -b measured end to end Summary

**A W27C512 riding the UV handler proved criterion 3 (write -b now reaches the firmware unrefused and
programs a non-blank target) and criterion 5 (the erasable leg shows no behaviour change) on real
Arduino/RURP hardware, the D-07 skew regression was captured verbatim on pre-205 firmware before the
only reflash of the session, and erase -b's added wall-clock was measured end to end at 10.632s
(Leonardo-class) alongside a labelled derivation for Phase 206's SESS-01.**

## Performance

- **Duration:** ~20 min (approximate -- no start-time sentinel captured at kickoff; bounded by the
  two task commit timestamps: 18:30:24Z first commit to 18:38:31Z second commit, plus setup/reading
  time before the first commit)
- **Started:** 2026-09-22 (session start)
- **Completed:** 2026-09-22T18:38:31Z
- **Tasks:** 2 of the plan's 3 tasks executed in this dispatch (Task 1, the blocking-human
  checkpoint, was answered by the operator before dispatch -- see "Task 1" below)
- **Files created:** 2 (`205-BENCH-MATRIX.md`, `205-SESSION-COST.md`), both meta-repo only

## Accomplishments

- **Task 1 (pre-satisfied):** the operator's answer -- Rev 2.0 shield, JP4/JP5 both intact, W27C512
  seated and expendable, Leonardo on `/dev/ttyACM0` reflashable twice -- is recorded verbatim in
  `205-BENCH-MATRIX.md`, together with a note distinguishing it from the still-open `WINDOWS.md`
  entry 3 chip-ID finding (the firmware's own chip-ID probe still read `0x1818` vs. expected `0xda08`
  this session, unforced -- not re-investigated, recorded as still open).
- **B0-B1:** rig re-confirmed (exactly one `2341:8036` device, `/dev/ttyACM0`); a pre-205 firmware
  artifact built from a detached worktree at the phase-entry sha (`a4e002f2`), its `.hex` digest
  matching `205-FLASH-RAM.md`'s recorded phase-entry digest exactly, flashed via `pio run -t upload`.
  The live `firestarter_fw` tree never left branch `v1.41-verification-to-host` and was never checked
  out to a different commit.
- **B2-B3:** the seated part driven into a known non-blank state at `0x000000` (Phase 201-06's
  `--skip-erase` rehearsal); on pre-205 firmware, the post-205 host's `write -b` against that region
  was refused with `MSG_ERR_NOT_BLANK` (0xB0) rendered verbatim -- `Not blank, at 0x000000, v: 0x11`
  -- exit 1, 3.81s, with a post-refusal whole-device digest identical to the pre-refusal one (no side
  effect). This is the D-07 skew, captured before the only reflash of the session.
  Confirmed twice.
- **B4-B5:** post-205 firmware flashed (`.hex` digest matching the phase-exit figure exactly); the
  identical `write -b` invocation against the same target now reached the firmware UNREFUSED and
  programmed the region -- exit 0, read-back match (0 bad of 64), whole-device digest differing from
  the anchor exactly at the target region and nowhere else. Criterion 3, closed.
- **B6:** the erasable leg (plain `write`, no `-b`) showed no behaviour change -- exit 0, the target
  region overwritten again, no refusal on either side of this phase on this path, because
  `FLAG_CAN_ERASE` parts were always exempted. Criterion 5, closed.
- **B7:** `erase -b` ran end to end three times, exit 0 each time (erased, then a whole-device
  host-side check confirming blank across all 65536 bytes). Added wall-clock measured at **10.632s**
  (Leonardo-class, N=3, median-vs-median) against plain `erase` -- markedly larger than the
  connect-term-only derivation (2.607s, cited from `203-SESSION-COST.md`) because the measured figure
  legitimately includes the second port open's whole-device blank-check read traffic (7.40s for this
  64 KiB part), which the derivation deliberately excludes. Both figures recorded in
  `205-SESSION-COST.md` for Phase 206's SESS-01, never blended.
- **Digest chain closed:** B2/B3 identical (no side effect from the refusal); B5, B6, B7 each differ
  from the prior step exactly as predicted, closing on an independently-`read`-confirmed all-`0xFF`
  device at B7.
- **Four coverage gaps stated:** every UV-handler leg is an erasable proxy (no true UV part
  available); `flash_intel.cpp` (`0x10`) has zero validated chips and cannot be benched at all;
  `flash_nor_unlock.cpp` (`0x06`)'s sole validated part (`SST39SF020`) is not seated, with the Phase
  201 note's "one flag deep, not safely latent" finding quoted verbatim rather than re-derived; no
  Uno-class board is attached, so nothing here is evidence about the 512-byte chunked-transfer path.
- **Scratch worktree removed.** `/home/vscode/.local/share/gsd205-fw-pre205-worktree` was created for
  B1 and removed (`git worktree remove --force`) before this SUMMARY was written; no commit was made
  from it.

## Task Commits

Each task was committed atomically, meta-repo only (this plan touches no source in either sub-repo):

1. **Task 2 (B0-B3, Task 1's checkpoint answer recorded):** `97a38ec0` (docs) -- rig identity, the
   two firmware roles' pre-205 half, the non-blank setup, and the D-07 skew refusal captured verbatim.
2. **Task 3 (B4-B7, coverage gaps, session cost):** `b04e74a7` (docs) -- the post-205 half, criteria
   3 and 5 closed on silicon, `erase -b` measured end to end, the digest chain closed, and
   `205-SESSION-COST.md` created.

_Note: no TDD tasks in this plan; this plan changes no source and no test in either sub-repo._

## Files Created/Modified

- `.planning/phases/205-the-pre-flights-leave-the-firmware/205-BENCH-MATRIX.md` -- new. The executed
  bench record: Task 1's verbatim operator answer, rig identity, both firmware roles named by sha and
  `.hex` digest, B0 through B7 each with exact command/verbatim output/exit code/duration, the closed
  whole-device digest chain, four stated coverage gaps, and a chip-identity-independence statement per
  claim.
- `.planning/phases/205-the-pre-flights-leave-the-firmware/205-SESSION-COST.md` -- new. `erase -b`'s
  measured added wall-clock (10.632s, Leonardo-class, N=3) alongside the labelled derivation over
  Phase 203's cited connect-term medians (2.607s), with an explanation of why the two figures
  legitimately differ and what Phase 206's SESS-01 should do with each.

## Decisions Made

See the frontmatter `key-decisions` block for full reasoning. In one sentence each:

1. One non-blank target address (`0x000000`, 64 bytes) served every UV-handler leg (B2/B3/B5/B6),
   so one whole-device digest chain covers all four instead of a chain per address.
2. `-f`/`--force` was required on every command against the seated part, for the documented
   VPP-monitor-noise reason `204-BENCH-MATRIX.md` already recorded -- it changes nothing about which
   command is sent on the wire.
3. The operator's Task 1 identity statement is recorded as independent evidence, not as a resolution
   of `WINDOWS.md` entry 3's still-open firmware-side chip-ID mismatch.
4. `erase -b`'s wall-clock is measured here (Fork C), and the measured figure and Phase 203's
   connect-term derivation are recorded side by side rather than reconciled, because they legitimately
   measure different things (total added cost vs. connect-term-only cost).

## Deviations from Plan

None -- plan executed exactly as written. Task 1's blocking-human checkpoint was pre-satisfied by the
operator before this dispatch began, per the objective's explicit instruction; no auto-approval of a
`gate="blocking-human"` checkpoint occurred -- the operator's own verbatim answer was recorded as
given.

## Known Stubs

None. This plan produces two planning/evidence documents and runs no code that ships; no stub is
introduced.

## Issues Encountered

**The firmware's own chip-ID probe continues to read `0x1818` against the database's expected
`0xda08` for a W27C512** -- the same `WINDOWS.md` entry 3 finding Phase 204 recorded, unresolved by
this plan (not re-investigated, per the standing instruction that this needs the operator who
physically placed the part, not the executor). The operator's Task 1 statement in this plan is
recorded as an independent line of evidence about the same physical part, not as a resolution.

**No whole-device read was taken between B3 (last chip-content-affecting event on pre-205 firmware)
and B4 (the reflash to post-205 firmware).** Chip content on an EEPROM is not expected to be affected
by an AVR program-memory flash, but this record does not assert survival by inference where a read
could have proven it -- stated plainly in the B4 section rather than glossed over. This does not
weaken criterion 3's proof: B5's read-back and digest are self-sufficient regardless of what content
existed immediately before B5's own write.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- `205-BENCH-MATRIX.md` and `205-SESSION-COST.md` are both complete and committed. FWBLANK-01,
  FWBLANK-02 and FWBLANK-04's silicon obligations (criteria 3 and 5) and the D-07 skew leg are all
  satisfied with bench evidence.
- Phase 206's SESS-01 has both a measured figure (10.632s, this plan) and a labelled derivation
  (2.607s, cited from Phase 203) for `erase -b`'s added wall-clock, with an explicit explanation of
  why they differ and which one to use for which reasoning.
- No blocker for the phase close. This plan touched no source in either sub-repo; both sub-repo
  working trees are clean and on `v1.41-verification-to-host`; all four firmware CI legs (pytest
  316/316, `pio test -e native` 244/244, `pio test -e native_nodevtools` 244/244, `pio run` 3/3
  SUCCESS) remain green, unchanged by this plan's bench commands.
- `WINDOWS.md` entry 3 (the open chip-ID mismatch) remains open, unchanged by this plan -- carried
  forward as before, with this plan's operator statement recorded as independent evidence alongside
  it, not a resolution.
- No branch in any of the three repositories was `beta` at any point in this plan's execution; no
  push was made anywhere.

---
*Phase: 205-the-pre-flights-leave-the-firmware*
*Completed: 2026-09-22*

## Self-Check: PASSED

- `[ -f /workspaces/.planning/phases/205-the-pre-flights-leave-the-firmware/205-BENCH-MATRIX.md ]` -> FOUND
- `[ -f /workspaces/.planning/phases/205-the-pre-flights-leave-the-firmware/205-SESSION-COST.md ]` -> FOUND
- `git -C /workspaces log --oneline --all | grep -q 97a38ec0` -> FOUND
- `git -C /workspaces log --oneline --all | grep -q b04e74a7` -> FOUND
- Re-ran acceptance criteria: B0-B7 all present with exit codes and durations; "proxy" appears 5
  times, including on B2/B3/B5/B7 themselves; B3's refusal line matches
  `tools/catalog/messages.toml`'s `MSG_ERR_NOT_BLANK` format string exactly; the post-refusal digest
  at B3 equals B2's; `205-SESSION-COST.md` contains `SESS-01`, `2.607`, `derivation` and `measured`.
- Re-ran the firmware CI legs after the bench session: `pytest tests/` 316 passed; `pio test -e
  native` 244/244; `pio test -e native_nodevtools` 244/244; `pio run` uno/uno328pb/leonardo all
  SUCCESS.
- `git -C /workspaces/firestarter_fw status --porcelain` -> empty; `git -C
  /workspaces/firestarter_fw rev-parse --abbrev-ref HEAD` -> `v1.41-verification-to-host`; HEAD
  unchanged at `6e11d057b59977dd870c1ddcc588dd2f6f3ea1db` throughout.
- `git -C /workspaces rev-parse --abbrev-ref HEAD` -> `v1.41-verification-to-host`.
- Scratch worktree `/home/vscode/.local/share/gsd205-fw-pre205-worktree` confirmed removed (`git
  worktree list` no longer shows it); no commit exists from it.
- No push was made to any branch in any repository during this plan.
