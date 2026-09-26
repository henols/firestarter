---
phase: 145-bench-validation
verified: 2026-08-18T07:05:00Z
status: passed
score: 3/3 must-haves verified
behavior_unverified: 0
overrides_applied: 0
authored_at: milestone-close
---

# Phase 145: Bench Validation — Verification Report

**Phase Goal:** The new algorithm is proven on real silicon for the operator's required part, with the opportunistic parts recorded honestly whether or not they materialize.
**Verified:** 2026-08-18T07:05:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Method, and its one honest limitation

This report was authored at milestone close by `/gsd-complete-milestone`, not during phase
execution. It exists because Phase 145 shipped its evidence into `145-BENCH-LOG.md` and the
`145-08` phase verdict but never emitted the conventional `145-VERIFICATION.md` artifact, so
the readiness projection read the phase as unverified while its three requirements were
already ticked Complete on independently audited evidence.

**This report cites that record; it does not re-derive it.** Every figure below is
hardware-derived — three 65536-byte write→read→verify cycles on a physical Winbond W27C512
seated in a Rev 2.0 shield on a `leonardo` controller, with the operator present. **None of it
is re-runnable at close time**: no board is attached to this session, and re-running it would
cost chip wear the criteria do not require. Where Phase 144's verification could re-execute
every command live, this one cannot, and that difference is stated rather than papered over.

What *was* checked live in this session: the artifact inventory exists on disk, the requirement
checkboxes and traceability rows read Complete, and the `chip_database.json` zero-diff leg
underlying BENCH-03 is re-checkable from git alone. Those are noted per-row below.

## Goal Achievement

### Observable Truths (mapped to ROADMAP Success Criteria 1–4 and BENCH-01..03)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | BENCH-01 / Criterion 1: `0x07` completes a full write→read→verify on W27C512 or TMS27C512 on Leonardo, with per-run evidence recorded | VERIFIED (hardware, cited) | Three full 65536-byte cycles on Winbond **W27C512** (`0xda08`), Leonardo, three **distinct** images so no cycle could pass by rewriting bytes already present. Nine clean oracle cells: firmware write (`exit 0`, 0 bad bytes) × firmware verify (`exit 0`) × independent host-side SHA compare (65536/65536, cycles `f7248960…`/`b566c7a0…`/`74c359c8…`), each with read stability N=3 at one distinct SHA. D-09's pass rule was 3/3 byte-exact on both oracles; that is what was measured. Erase demonstrably fired — 99.8% and 90.6% of inter-cycle bytes require a `0`→`1` transition. No `--force`/`--skip-erase`/`--no-blank-check` in any silicon-touching invocation (D-17), corroborated at the wire by `Flags set: CanErase (0x02)`. `145-BENCH-LOG.md` §"Criterion 1". |
| 2 | BENCH-02 / Criterion 2: `0x08` (AM27C020) validated, or recorded skipped-with-reason naming the missing part — never inferred from `0x07` | VERIFIED | Outcome `skipped-with-reason`, missing part named: **AM27C020**, absent from the bench (operator). The disposition cites Phase 99's figures rather than re-deriving them (write #1 60/64 with `0x1da00`…`0x1da03` staying `0xFF`; write #2 0/64; read stability PASS N=3) and grades that shape a **fail** under D-14, not a qualified pass. The record states explicitly that no `0x08` measurement was taken in this phase and that nothing in Gate 2/Gate 3 is evidence about `0x08`. `145-BENCH-LOG.md` §"Criterion 2". |
| 3 | BENCH-02 / Criterion 3: `0x0B` (M2716/M2732) validated, or recorded skipped-with-reason naming the missing parts — never inferred from `0x07` | VERIFIED | Outcome `skipped-with-reason`, missing parts named: **M2716** and **M2732**, neither on the bench. Cites Phase 79 (VPE 22.4 V DMM vs 23.9 V firmware at max pot; ≥25 V bar **NOT CLEARED**, retired by operator override 79-CONTEXT D-07; four NMOS chips at `supported` best-effort) and carries the rail-vs-socket caveat. Definitive proof remains parked at Phase 79 plan `79-03` pending a physical chip. Not inferred from `0x07`. `145-BENCH-LOG.md` §"Criterion 3". |
| 4 | BENCH-03 / Criterion 4: no chip's `support_status` changes as a result of this milestone's bench runs | VERIFIED (partially re-checkable live) | Four independent legs at Gate 0 **and re-confirmed at the tip after every bench run landed**, answering the criterion's own "as a result of" wording at the end rather than only before. Legs: whole-milestone `chip_database.json` diff `4d18b645`→HEAD is **zero bytes**; generator-inputs diff (`tools/build_db.py`, `tools/extra_chips.json`, `tools/infoic.xml`) **zero bytes**, closing the latent-change gap; AST write-locus checker **exit 0**; histogram **736 supported / 9 adapter-required / 1 protocol-not-implemented / 746 total**. `tools/build_db.py` was deliberately **not** run — regenerating would itself be the change. `145-BENCH-LOG.md` §"Criterion 4" + `145-08` Task 3. |

**Score:** 3/3 requirements verified (BENCH-01, BENCH-02, BENCH-03); 4/4 ROADMAP success criteria
answered — criteria 1 and 4 `validated`, criteria 2 and 3 `skipped-with-reason` with parts named.
Criteria 2 and 3 are *satisfied by* a skipped-with-reason record: their own wording admits it, and
the naming plus the not-inferred sentence are exactly what they demand.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `145-BENCH-LOG.md` | The single serialised phase record all nine plans write into | VERIFIED | 3203 lines on disk. Carries session 1's superseded `VERDICT: HALTED` verbatim rather than rewriting it. |
| `runs/cycle{1,2,3}/` | Nine 65536-byte read-backs, three per cycle | VERIFIED | Directories present under the phase dir. |
| `readbacks/readback{1,2,3}.bin`, `readbacks/prewrite.bin` | Per-cycle read-backs plus the pre-write baseline | VERIFIED | Present. |
| `logs/` | `write_cycle{1,2,3}.{stdout.log,stderr.raw}`, `verify_cycle{1,2,3}.log`, `read_cycle{1,2,3}.log`, `consistency_cycle{1,2,3}.log`, plus the operator's pasted eyes-on transcript | VERIFIED | Present, including `eyeson_rerun_pulse4688.operator_paste.log`. |
| `SHA256SUMS.txt` | Digest of every bench artifact | VERIFIED | Present at the phase root. |
| `145-VALIDATION.md` | Validation contract recording that this phase adds **no** automated tests | VERIFIED | `status: approved`, and states plainly that the existing suites run as regression tripwires, not requirement evidence — requirement evidence is the bench record. |
| `.planning/REQUIREMENTS.md` (BENCH-01..03 ticked) | Checklist and traceability both Complete | VERIFIED live | Checklist rows 260–265 all `[x]`; traceability rows 347–349 all `Complete`. Flipped by `145-09` behind its own blocking operator gate with a snapshot-and-diff. |

## Boundaries this verification inherits

This report does not widen a single claim in the phase record. All nine boundaries in
`145-BENCH-LOG.md` §"Boundaries — stated, not implied" carry forward intact. The four that most
constrain how this PASS may be read:

1. **No comparative claim.** Nothing here says v1.31 programs better, faster or more reliably than
   what preceded it. No control run was made or intended (D-08); this milestone claims **fidelity,
   not improvement**. The 22.84 s pre-v1.31 figure in cycle 1's record is a recorded historical
   number, not a control measurement.
2. **No datasheet-conformance claim, in either direction.** The **~6.25 V** program-VCC evidence
   ceiling is unreachable on this shield; that debt belongs to the milestone, not this phase.
3. **Scope is exactly one part, one controller, one shield revision** — W27C512 `0xda08`, `leonardo`,
   shield Rev 2.0 read off the silkscreen (the EEPROM `hw_revision` byte cannot distinguish 2.0 from
   2.2 from the modified Rev 0). Nothing extrapolates to another protocol, part, revision or board.
4. **Gate 2 and Gate 3 both ran on a build carrying an open, un-adjudicated MERGE-05 breach** —
   `ebe9cb3` is **+96 B** against a 0 B leonardo must-not-grow band, and BASE-01 was **not**
   re-anchored a second time to make it green. 144 H7 was answered green at 26906 B and then went
   red underneath the answer; the record says so rather than citing the green reading.

## Gaps

**None that block the phase goal.** The phase goal asked for proof on the operator's required part
with the opportunistic parts recorded honestly; all three requirements are discharged on that
standard.

Twelve items carry forward with **no v1.31 owner**, and sixteen readings were **not taken**, each
with its blocker named — both lists are in `145-BENCH-LOG.md` §"Carry-forward hand-offs" and
§"Not measured". They are not gaps in this phase: Phase 146 is docs-and-claims only and cannot run a
bench or ship code, so they were unrecoverable *within* the milestone by construction, which is
precisely why D-12 forbade dropping any of them silently. The two with named real successors:
`0x0B` graduation at Phase 79 plan `79-03`, and MERGE-05's band breach with the operator as a
requirements judgement.

Three carry into the project backlog as filed items rather than as loose ends: **999.30** (the MAIN
write progress bar never reaching 100% — cosmetic, all six affected writes verified byte-exact),
**999.31** (no firmware-side `--pulse-us` ceiling for `0x07`/`0x08`), and the T-145-45
threat-register defect that 999.31 subsumes.

## Anti-Patterns / Notes

- **Session 1's genuine failure is not laundered out.** Cycle 1 attempt 1 failed on the first byte
  of the first block (`Byte at 0x000000 failed to program within 25 pulses`, exit 1) and stands in
  the record as a **fail** with its cause — a v1.31 firmware defect (Phase 141 had deleted the only
  `CTRL_VPE_ENABLE` assert), root-caused by a debug session, not a bench fault. It is **not** one of
  Gate 2's three counted cycles.
- **D-09's single re-seat allowance is UNCONSUMED** — never spent in either session, no re-seat
  performed at any point. Session 1 offered and declined it for want of a named physical cause, a
  refusal the firmware root-cause later vindicated. It must not be read as a pending mitigation.
- **The intermittent single-byte margin failure is mitigated, not explained.** ~17 clean cycles is
  not a root cause.
- **D-16 held on its own terms, and the nuance is stated:** no *plan* in this phase touched either
  sub-repo, but a debug session — which is not a plan — changed eleven files under `firestarter/`
  (`eb563d2` + `ebe9cb3`, +96 B). Every bench measurement from 2026-08-17 onward came from `ebe9cb3`
  (27002 B), not the `a594173d` (26906 B) image Gate 1 recorded.
- **Dispatch mode:** no `--auto` and no `--chain`; `check auto-mode` resolved `false`. Per D-20
  auto-modes auto-approve `human-verify` gates and `autonomous: false` is not self-protecting alone,
  so every operator gate in this phase was real and none was self-approved.
- **Witness:** the operator, Henrik (henrik@predictly.se) — who seated the part, read the shield
  revision off the silkscreen, authorized every destructive spend, and supplied D-10's eyes-on half
  in their own words from a run they executed themselves.

## Verdict

**Phase 145 — Bench Validation: PASSED**, 3/3 requirements and 4/4 ROADMAP success criteria, on
hardware evidence recorded in `145-BENCH-LOG.md` and cited here rather than re-derived. The PASS is
bounded by every limit in the section above, and by the phase record's own closing sentence: the
evidence is one part, one controller, one shield revision.
