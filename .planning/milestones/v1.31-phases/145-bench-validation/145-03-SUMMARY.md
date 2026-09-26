---
phase: 145-bench-validation
plan: 03
subsystem: testing
tags: [pio, avrdude, leonardo, w27c512, chip-id, bench-validation, firmware-reflash]

requires:
  - phase: 145-02
    provides: "Gate 0 complete with zero hardware touched — BENCH-02 skip dispositions, BENCH-03 re-measurement, image generation and instrument inventory"
provides:
  - "Gate 1 identity table fully populated: controller/port, hardware revision (annotated non-authoritative), operator-confirmed silkscreen and seated chip, R1/R2 readbacks, firmware version string with D-18 caveat, firmware commit + working-tree-clean assertion, flash bytes measured, avrdude verified byte count"
  - "Reflash proof: pio run -t upload -e leonardo from clean commit a594173d, 26906 bytes written+verified, no fw --install used anywhere"
  - "MERGE-05 merge05_clause quoted verbatim with the anchor-move disclosure (not an unqualified compliance claim)"
  - "Chip-id confirmation: seated part is Winbond W27C512 at 0xda08, confirmed via firestarter info + id, exit 0, port re-verified independently"
  - "Gate 1 identity-half verdict naming the five cleared conditions; VPP and D-03 pre-flight explicitly left NOT YET RUN for 145-04, plus the carried-forward explicit-expendability requirement"
affects: [145-04, 145-05, 145-06, 146]

tech-stack:
  added: []
  patterns: ["Whole-log capture + read (never hard-coded grep) for the avrdude byte count", "Exit status captured via redirect + $? read directly, never through a pipe to tail", "Port identity re-verified fresh every task rather than carried forward"]

key-files:
  created: []
  modified:
    - .planning/phases/145-bench-validation/145-BENCH-LOG.md

key-decisions:
  - "Recorded Task 1's Part-expendable row honestly as answered-by-implication only — the operator's exact words never used the word 'expendable' — and carried forward an explicit expendability confirmation requirement to 145-04's D-03 pre-flight rather than fabricating a clean confirmation"
  - "Dispatch mode recorded as the orchestrator's attestation, not the operator's restatement, per D-20"
  - "Named the 93.8% / 1766 B flash-headroom figure (against flash_total 28672 B) as the one this record quotes, while also stating the 82.1% figure PlatformIO's own upload banner reports against the 32768 B part"
  - "Quoted size_baseline.json's merge05_clause verbatim and stated the anchor-move disclosure explicitly rather than reporting the 0 B delta as unqualified MERGE-05 compliance"

requirements-completed: []

coverage:
  - id: D1
    description: "Operator's four Task 1 identity answers (silkscreen, seated chip, expendability, dispatch mode) recorded verbatim into Gate 1, with the unanswered expendability question honestly flagged rather than smoothed into a false confirmation"
    verification:
      - kind: manual_procedural
        ref: ".planning/phases/145-bench-validation/145-BENCH-LOG.md Gate 1 identity table, rows 'Shield silkscreen', 'Seated chip', 'Part expendable', 'Dispatch mode'"
        status: pass
    human_judgment: true
    rationale: "Verbatim-transcription honesty (D-20's no-false-green requirement) is a human-judged property of the record, not a machine-checkable one — the operator or a downstream reader must confirm the words match what was actually said."
  - id: D2
    description: "Firmware tree under test reflashed via pio run -t upload -e leonardo from a clean, named commit; image identified by commit + avrdude-verified byte count, never by version string; fw --install never used"
    verification:
      - kind: manual_procedural
        ref: "/tmp/gsd-145/upload_leonardo.log — 'avrdude: 26906 bytes of flash written' / 'avrdude: 26906 bytes of flash verified'; git -C /workspaces/firestarter status --porcelain returned 0 lines before and after"
        status: pass
    human_judgment: false
  - id: D3
    description: "Measured Leonardo flash/RAM (26906/2014) matches size_baseline.json exactly; 0 B delta recorded with the MERGE-05 anchor-move disclosure, not as unqualified compliance"
    verification:
      - kind: manual_procedural
        ref: "pio run -e leonardo --target size output (/tmp/gsd-145/size_leonardo.log) cross-checked against firestarter/scripts/baseline/size_baseline.json avr_targets.leonardo"
        status: pass
    human_judgment: false
  - id: D4
    description: "Seated part confirmed as Winbond W27C512 by chip-id 0xda08 via firestarter id W27C512 (exit 0, captured directly not through a pipe) and firestarter info W27C512; ST 0x203d / TI 0x9785 named as the halting mismatches; port identity re-verified independently this task"
    verification:
      - kind: manual_procedural
        ref: "/tmp/gsd-145/id_w27c512.log (exit=0, 'Chip ID check passed for W27C512'); /tmp/gsd-145/info_w27c512.log ('Chip ID: 0xda08'); /tmp/gsd-145/fw_task3.log ('controller: leonardo on port /dev/ttyACM0')"
        status: pass
    human_judgment: false

duration: ~4min (post-gate execution; the prior session's wait at Task 1's checkpoint is not counted)
completed: 2026-08-16
status: complete
---

# Phase 145 Plan 03: Bench Identity, Reflash Proof and Chip-ID Confirmation Summary

**Reflashed the Leonardo from a clean v1.31 tree (commit `a594173d`, 26906/2014 bytes matching baseline exactly) and confirmed the seated Winbond W27C512 by chip-id `0xda08`, clearing Gate 1's identity half while leaving VPP and the D-03 erase pre-flight explicitly outstanding for 145-04.**

## Performance

- **Duration:** ~4 min from the operator's answer to plan completion (Task 1's checkpoint wait in the prior session is not counted)
- **Started:** 2026-08-16T18:45:11Z (first commit after resume)
- **Completed:** 2026-08-16T18:49:09Z
- **Tasks:** 3/3
- **Files modified:** 1 (`145-BENCH-LOG.md`, across three commits)

## Accomplishments

- Recorded the operator's Task 1 answers into Gate 1's identity table verbatim, including the honest, explicitly-flagged non-confirmation of part expendability (carried forward as a required item for 145-04's D-03 pre-flight) and the orchestrator's own dispatch-mode attestation (no `--auto`/`--chain`, per D-20)
- Flashed the tree under test via `pio run -t upload -e leonardo` from clean commit `a594173d`; `firestarter fw --install` never used; avrdude wrote and verified `26906` bytes, matching the pre-upload `pio run -e leonardo --target size` measurement (`26906` program / `2014` data) and `size_baseline.json`'s leonardo record exactly, with the `merge05_clause` quoted verbatim and its anchor-move disclosure stated rather than an unqualified compliance claim
- Confirmed the seated part is the Winbond W27C512 at chip-id `0xda08` via `firestarter info W27C512` and `firestarter id W27C512` (exit `0`, captured by direct redirect + `$?`, never through a pipe to `tail`), named the two wrong-part ids (`0x203d` ST, `0x9785` TI) that would halt the phase, and wrote the fail-safe subsection citing the v1.18 Phase-97 precedent
- Wrote Gate 1's identity-half verdict naming all five cleared conditions (right board, right part, right build, clean tree, zero flash growth) and left the full `Gate 1 verdict:` line, VPP, and the D-03 pre-flight explicitly `NOT YET RUN` for `145-04`

## Task Commits

1. **Task 1: Operator attaches the board, seats the W27C512 and reads the silkscreen** - `0199d378` (docs)
2. **Task 2: Flash the tree under test and identify the image by commit and verified byte count** - `d01e3881` (docs)
3. **Task 3: Confirm the seated part by chip-id and clear the Gate 1 identity check** - `f1c4ad8f` (docs)

_No separate plan-metadata commit; this SUMMARY and the STATE/ROADMAP updates are committed in the final metadata commit per the execute-plan workflow._

## Operator's Verbatim Answers (Task 1)

The operator's answer, repeated identically across three messages, quoted exactly as given:

> Leonardo,  Rev 2.0, w27c512 seated

Mapped onto the four required rows:

1. **Shield silkscreen** — `Rev 2.0`. Directly stated, matches D-01's required Rev 2.0 exactly.
2. **Seated chip** — `w27c512` (Winbond W27C512, canonical form noted alongside the operator's lowercase spelling). Directly stated.
3. **Part expendable** — **NOT separately confirmed.** The operator's exact words never contain the word "expendable" or any equivalent. Recorded as answered-by-implication only: the prompt they answered stated the part's contents would be bulk-erased, and the operator seated the part and separately said "continue" — but no explicit expendability confirmation was given. **Carried forward: 145-04's D-03 erase pre-flight (the phase's first destructive act) requires an explicit expendability confirmation before it runs.** This plan's own Gate 1 identity check spends nothing, so the carry-forward does not block this plan's completion.
4. **Dispatch mode** — not restated by the operator; recorded as the orchestrator's own attestation: dispatched via `/gsd-execute-phase 145 --wave 3`, no `--auto`, no `--chain`, `check auto-mode --pick active` returned `false` before dispatch, and the checkpoint was in fact presented and waited on (the operator's answer arrived only after the gate posted) — the behavioural proof no auto-approval occurred (D-20).

## Reflash and Image Identity (Task 2)

- **Firmware commit under test:** `a594173d2bbbabe74e6a470b4751528435246326`, branch `gsd/v1.31-27c-programming-algorithm-fidelity`
- **Working tree:** empty (`0` lines), asserted both immediately before `pio run -e leonardo --target size` and immediately after the upload
- **Size measurement:** `pio run -e leonardo --target size` → `Program: 26906 bytes (82.1% Full)`, `Data: 2014 bytes (78.7% Full)`, matching `size_baseline.json`'s `avr_targets.leonardo` (`flash_used 26906`, `ram_used 2014`) exactly — `0 B` delta against the `0 B` leonardo must-not-grow band. Against `flash_total` `28672` B (bootloader excluded), this equals `93.8%` and `1766` B headroom — the figure this record quotes for the H7 hand-off, distinct from but not in conflict with the `82.1%` figure PlatformIO's own upload banner reports against the raw `32768` B part.
- **Reflash:** `pio run -t upload -e leonardo`, full output tee'd to `/tmp/gsd-145/upload_leonardo.log`. Only one `/dev/ttyACM*` device was present, so no `--upload-port` override was needed; PlatformIO's own `Auto-detected: /dev/ttyACM0` line, and the same port confirmed independently afterward, showed no drift. `firestarter fw --install` was never invoked. avrdude tool actually used this session: `tool-avrdude @ 1.60300.200527 (6.3.0)` — **not** `8.1` as RQ-5's assumption A3 anticipated; the whole log was still captured and read rather than grepped with a hard-coded pattern, per the plan's prohibition. Verbatim lines: `avrdude: 26906 bytes of flash written` / `avrdude: 26906 bytes of flash verified`.
- **MERGE-05 clause, quoted verbatim** from `firestarter/scripts/baseline/size_baseline.json` `meta.deltas_vs_base01.leonardo.merge05_clause`:
  > "Delta vs BASE-01 is now exactly zero -- Phase 144 / D-11 re-anchored BASE-01 to this file's own v1.31-tip figure (26906 B). A zero delta here means the anchor moved to the v1.31 tip, NOT that flash growth stayed inside v1.24's original 0 B must-not-grow band (D-14) -- see meta.supersedes for the full disclosure."

  This record states the anchor-move disclosure explicitly rather than reporting the `0 B` delta as unqualified MERGE-05 compliance.
- **Bench identity from live CLI (`-p /dev/ttyACM0` on every invocation, group option before subcommand):**
  - `firestarter -p /dev/ttyACM0 fw` → `Current firmware version: 3.0.0b17, for controller: leonardo on port /dev/ttyACM0`
  - `firestarter -p /dev/ttyACM0 hw` → `Hardware revision: Rev 2.0-class, Override HW: Rev 2.0-class` — recorded as **NOT authoritative** for distinguishing Rev 2.0 from Rev 2.2 from the modified Rev 0; the operator's silkscreen reading is the authority
  - `firestarter -p /dev/ttyACM0 config` → `R1: 270000, R2: 44000`
  - Version-string D-18 caveat recorded: `3.0.0b17` is byte-identical to the branch's own fork point `3085084` and reads older than `origin/beta`'s `3.0.0b18` — the version string identifies nothing; the commit plus the `26906` B avrdude count are the discriminators

## Chip-ID Confirmation (Task 3)

- `firestarter info W27C512` — verbatim: `Type: EEPROM`, `Can be erased: yes (electrically erasable)`, `VPP: 12.0v`, `Chip ID: 0xda08`, `Pulse delay: 100µS`
- `firestarter -p /dev/ttyACM0 id W27C512` — exit status captured by direct redirect and immediate `$?` read (never through a pipe to `tail`, per the plan's explicit false-green warning): `exit=0`. Verbatim log: `Connecting...Connecting... OK`, `Checking chip ID for W27C512`, `Chip ID check passed for W27C512: (main done) (0.28s)`. A `-v` re-run additionally showed the expected chip-id value sent to the firmware, `'chip-id': 55816` — `55816` decimal `= 0xda08` hex, matching `info`'s printed value exactly.
- The two wrong-part ids named for the record: `0x203d` (ST M27C512, 13 V, non-erasable) and `0x9785` (TI TMS27C512, 13 V, non-erasable, and the part D-01 explicitly forbids spending). Either would halt the phase — not a D-09 re-seat allowance. No mismatch occurred.
- **Fail-safe subsection:** a plain `write` aborts on a chip-id mismatch with no `--force` available, the same mechanism that caught the v1.18 Phase-97 wrong-part mix-up before any silicon was spent. `--force` is banned for this entire phase (D-17); none of the commands actually run in this plan used it (the 9 occurrences of the string `--force` in the record are all inside prohibitions, the `--force used?` row label, or the fail-safe explanation itself — verified by grep).
- **Port identity re-verified this task**, independently of Task 2: `firestarter -p /dev/ttyACM0 fw` again reported `controller: leonardo on port /dev/ttyACM0`, identical to Task 2's recorded values — no re-enumeration occurred between the two tasks.
- **Gate 1 identity-half verdict:** five conditions cleared (right board by silkscreen, right part by chip-id `0xda08`, right build by commit + avrdude byte count, clean tree, zero flash growth with anchor disclosure). VPP and the D-03 erase-capability pre-flight are explicitly `NOT YET RUN` and belong to `145-04`, along with the carried-forward requirement for an explicit expendability confirmation before that pre-flight (the phase's first destructive act). The full `Gate 1 verdict:` line is intentionally left unwritten — that is `145-04 Task 3`'s to close.

## Files Created/Modified

- `.planning/phases/145-bench-validation/145-BENCH-LOG.md` - Gate 1 identity table fully populated, reflash proof and MERGE-05 disclosure, chip-id confirmation and fail-safe subsection, identity-half verdict

## Decisions Made

- Recorded the Part-expendable row as answered-by-implication only, rather than a clean operator confirmation, because the operator's exact words never used the word "expendable" — per D-20, a false attestation here is exactly the false-green this phase's gates exist to prevent
- Recorded the Dispatch-mode row as the orchestrator's own attestation (not restated by the operator), stating precisely what evidence backs it (no `--auto`/`--chain` in the invocation, `check auto-mode` returned `false`, the gate was actually presented and waited on)
- Named the `93.8%` / `1766` B headroom figure (against `flash_total`) as the one quoted for the H7 hand-off, while also recording the `82.1%` figure PlatformIO's own banner reports against the raw part size, per the plan's instruction that both are correct and the record must name which it quotes
- Quoted `merge05_clause` verbatim and stated the anchor-move disclosure explicitly, rather than pairing the `0 B` delta with an unqualified "MERGE-05 compliant" claim

## Deviations from Plan

None — plan executed exactly as written. One noteworthy but non-deviating finding: the avrdude tool actually invoked this session was version `6.3.0`, not the `8.1` RQ-5's assumption A3 anticipated. This did not require any deviation because the plan's own instruction — capture the whole log and read the figure out of it rather than hard-coding a grep pattern — already accounted for exactly this possibility. The byte count (`26906`) matched expectation regardless of tool version.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Gate 1's identity half is cleared: right board, right part (chip-id confirmed), right build (commit + byte count), clean tree, zero flash growth. `145-04` can proceed directly to the VPP confirmation and the D-03 erase-capability pre-flight.
- **Blocker for `145-04`'s D-03 pre-flight specifically:** an explicit, separately-stated operator confirmation that the seated W27C512 is expendable is required before that pre-flight runs (the phase's first destructive act) — Task 1's answer did not supply this word, and this plan does not fabricate it.
- Board remains attached, W27C512 remains seated, firmware remains at commit `a594173d` (`26906`/`2014` B, `3.0.0b17`) — no further reflash should be needed for `145-04` unless the tree changes.

---
*Phase: 145-bench-validation*
*Completed: 2026-08-16*

## Self-Check: PASSED

- FOUND: `.planning/phases/145-bench-validation/145-BENCH-LOG.md`
- FOUND: `.planning/phases/145-bench-validation/145-03-SUMMARY.md`
- FOUND commit: `0199d378` (Task 1)
- FOUND commit: `d01e3881` (Task 2)
- FOUND commit: `f1c4ad8f` (Task 3)
