---
phase: 130-close-honesty-ledger-claim-gate-release-decision
plan: 10
subsystem: docs
tags: [honesty-ledger, planning-record, gate-hardening, requirements-md, vtor-correction]

requires:
  - phase: 130-close-honesty-ledger-claim-gate-release-decision
    provides: "check_record_corrections.py (plan 130-02) — the label-aware checker this plan's edits are measured against"
  - phase: 129-flash-path-decision-pcb-requirements-record
    provides: "129-RESEARCH.md C-1 (PY32F071 HAS a VTOR) and v1.23-FLASH-PATH-DECISION.md §1.6/§4(d)/§4(b)/Claim ceiling, which this plan's wording agrees with"
provides:
  - "REQUIREMENTS.md's PCB-03 and FUT-N04 clauses no longer assert the disproven 'no VTOR' fact; both preserve the superseded wording as a quote and cite 129-RESEARCH.md C-1"
  - "REQUIREMENTS.md's Validation Ceiling toolchain clause narrowed from 'absent' to a delta-and-byte-identity-permitted, absolute-still-needs-CI formulation, agreeing with v1.23-FLASH-PATH-DECISION.md §4(b)/Claim ceiling"
  - "A fact-versus-mechanism exception note recorded in REQUIREMENTS.md itself, naming LOCK-04/LOCK-06/HOST-04/121 D-06/D-17 as the mechanism-class precedents the standing don't-edit discipline was built for"
  - "REQUIREMENTS.md is green under check_record_corrections.py when scanned alone (0 unlabeled hits, down from 3)"
affects: ["130-16"]

tech-stack:
  added: []
  patterns:
    - "recordscan:allow inline markers with stated reasons, quoting a requirement's OWN superseded wording (not another file's reference to it) — a new sub-case of the pattern 130-07/130-08 established for PROJECT.md/STATE.md's pointers to these same two clauses"

key-files:
  modified:
    - .planning/REQUIREMENTS.md

key-decisions:
  - "PCB-03 and FUT-N04 were CORRECTED in place (not merely marked exempt), per D-06's fact-vs-mechanism distinction stated in the plan: these two clauses assert a disproven FACT (no VTOR), not a mechanism that turned out narrower, so the standing don't-edit-REQUIREMENTS discipline does not cover them. Both corrections preserve the superseded wording as a quote and carry a recordscan:allow marker (matching the disposition plan 130-07/130-08 gave the analogous PROJECT.md:97/STATE.md:56,139 sites that merely POINT AT these clauses) so the checker's part-with-no-vtor needle passes without hiding what was previously asserted."
  - "The Validation Ceiling's toolchain clause was narrowed, not corrected-and-dropped: the false 'absent' premise is replaced, but the conclusion (absolute ARM size claims still need a CI run URL + SHA) survives for the better reason research supplied (local/CI compilers differ, measured text=27260 vs text=27344), per D-07. Local delta and byte-identity claims are stated as the newly permitted class, with byte-identity explicitly stated to never imply the image runs."
  - "The reproduction recipe was deliberately NOT added to the ceiling clause (it belongs in 130-NONREGRESSION.md, plan 130-16's artifact, per D-07's explicit prohibition against a claims-policy statement becoming a how-to)."
  - "The fact-versus-mechanism exception note was placed once, adjacent to FUT-N04 (the second/last of the two amendments), naming both PCB-03 and FUT-N04 explicitly rather than duplicating the note at each site."
  - "Task 1's and Task 2's own <verify> python one-liners scope the CLOSE-0N unticked-check by naive substring match (`rid in l`) on any line starting with '- [' — this pre-existed the plan (confirmed against the pre-plan git-committed file: PCB-03's ORIGINAL text already said 'Phase 130 CLOSE-01 owns correcting this line's prose', which already broke that exact substring check before this plan touched anything). Because this plan's own acceptance criteria required PCB-03 to keep naming CLOSE-01 as the line that discharges it, the substring collision could not be avoided without violating the acceptance criteria. Verified the TRUE invariant (no CLOSE-0N checkbox ticked) with a corrected, anchored check (`^- \\[(.)\\] \\*\\*{rid}\\*\\*:`) instead of the plan's unanchored one-liner — see Verification below. Not a REQUIREMENTS.md defect; a latent false-positive in the plan's own diagnostic script, out of scope to fix here (PLAN.md is not a file this plan may modify)."

requirements-completed: []

coverage:
  - id: T1
    description: "PCB-03 and FUT-N04 corrected in place: both state the true VTOR fact, quote the superseded wording, cite 129-RESEARCH.md C-1, and (FUT-N04) restate the deferral's continued validity on its three remaining reasons; a fact-vs-mechanism exception note added adjacent to both."
    verification:
      - kind: other
        ref: "python3 -c assertion script (__VTOR_PRESENT present, 129-RESEARCH cited, FUT-N05 named, all four CLOSE-0N lines unticked via anchored check) -- PASS"
        status: pass
      - kind: other
        ref: "FIRESTARTER_RECORDSCAN_TARGETS=.../REQUIREMENTS.md python3 check_record_corrections.py --explain -- part-with-no-vtor at :96 and :116 both verdict inline-allow"
        status: pass
    human_judgment: false
  - id: T2
    description: "Validation Ceiling's toolchain clause narrowed: false 'absent' premise replaced, conclusion kept with the better local-vs-CI reason, delta/byte-identity newly permitted class stated explicitly, recipe pointed at 130-NONREGRESSION.md, wording agrees with v1.23-FLASH-PATH-DECISION.md section 4(b)."
    verification:
      - kind: other
        ref: "python3 -c assertion script (delta+byte-identity stated, 27260/27344 cited, 130-NONREGRESSION pointer present, run URL rule kept, all four CLOSE-0N lines unticked) -- PASS"
        status: pass
      - kind: other
        ref: "FIRESTARTER_RECORDSCAN_TARGETS=.../REQUIREMENTS.md python3 check_record_corrections.py -- PASS, exit 0"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-08-02
status: complete
---

# Phase 130 Plan 10: REQUIREMENTS.md Honesty-Ledger Corrections (VTOR + Toolchain) Summary

**Corrected PCB-03's and FUT-N04's disproven "no VTOR" clauses in place (superseded wording preserved as a quote, per D-06), narrowed the Validation Ceiling's toolchain clause from "absent" to a delta-and-byte-identity-permitted formulation that keeps its absolute-size conclusion for a better reason (D-07), and recorded the fact-versus-mechanism exception in the file itself — `check_record_corrections.py` goes from 3 unlabeled hits to 0 when scanned against `REQUIREMENTS.md` alone. No requirement checkbox touched.**

## Performance

- **Duration:** ~35 min
- **Tasks:** 2
- **Files modified:** 1 (`.planning/REQUIREMENTS.md`)

## Checker Delta (the load-bearing metric)

Scanning `REQUIREMENTS.md` alone with plan 130-02's checker:

| | Before this plan | After this plan |
|---|---|---|
| `unlabeled` | **3** (`:18` arm-toolchain-absent, `:96` part-with-no-vtor, `:116` part-with-no-vtor) | **0** |
| `inline-allow` | 0 | 3 (`:18`, `:96`, `:116`) |

`FIRESTARTER_RECORDSCAN_TARGETS=/workspaces/.planning/REQUIREMENTS.md python3 check_record_corrections.py` now exits **0** with `PASS: scanned .planning/REQUIREMENTS.md; exempt hits by verdict: {'inline-allow': 3}`.

## Accomplishments

**Task 1 — corrected PCB-03 and FUT-N04's VTOR clauses.**
- `REQUIREMENTS.md:96` (PCB-03): rewrote the vector-relocation-implication clause to state the corrected fact — the PY32F071 **has** a VTOR, `__VTOR_PRESENT 1` in the pinned SDK's CMSIS header, `SCB->VTOR` written unconditionally at every boot — and the corrected consequence from `v1.23-FLASH-PATH-DECISION.md` §1.6/§4(d): the vector-table move is cheap, the fleet re-flash is the real migration cost. The superseded `"on a part with no VTOR"` wording is quoted, not deleted, and the clause now records that CLOSE-01 **discharged** the correction its own prior text assigned to itself (previously: "Phase 130 CLOSE-01 owns correcting this line's prose" — now: "this edit is CLOSE-01 discharging that assignment").
- `REQUIREMENTS.md:116` (FUT-N04): replaced the bare false first deferral reason ("Cortex-M0+ has no VTOR") with the corrected fact, quoting the superseded wording, and explicitly restated that the deferral **still stands** on its three remaining reasons — `SYSCFG MEM_MODE`'s reported no-effect on sibling F0 parts, the no-silicon validation constraint, and FUT-N05 obsoleting it for the normal path — so a reader does not conclude that correcting one false reason reopens the item.
- A new unbulleted paragraph was added directly after FUT-N04 (before "### Voltage Control") recording the fact-versus-mechanism exception: the standing discipline (satisfy intent, record correction, leave the requirement alone) was built for **mechanisms turning out narrower** (LOCK-04, LOCK-06, HOST-04, 121 D-06/D-17); PCB-03/FUT-N04 instead asserted a **fact** that is false, which is why an in-place edit was made here rather than a pointer elsewhere — and this distinction is stated as bounding the exception, not general license to edit the file.
- Both corrected lines carry a `recordscan:allow` marker quoting their own superseded wording, matching the disposition plan 130-07/130-08 gave the *other* files' pointers to these same two clauses (`PROJECT.md:97`, `STATE.md:56`/`:139`) — this plan's markers are the first instance of the pattern applied to the clauses' own text rather than a reference to them.

**Task 2 — narrowed the Validation Ceiling's toolchain clause.**
- `REQUIREMENTS.md:18` was rewritten in place. The false premise ("`arm-none-eabi-gcc`, `cmake` and `ninja` are absent from this devcontainer") is corrected — quoted as superseded, and replaced with the fact that all three are present, install, and work (measured `arm-none-eabi-gcc` 14.2.1 / `cmake` 4.4.0 / `ninja` 1.13.0; research built the ARM target and ran a 41/41-object byte-identity proof with them — `130-RESEARCH.md` R-15/C-13).
- The conclusion — every **absolute** ARM size claim still cites a CI workflow run URL + commit SHA — is kept, now justified by the measured local-vs-CI compiler divergence (`text=27260` local vs `text=27344` CI) rather than by toolchain absence.
- What becomes newly permitted is stated explicitly: local **delta** claims (same tree, same toolchain, two builds) and local **byte-identity** claims (two local outputs bit-for-bit equal) — and nothing wider. The clause states plainly that byte-identity never implies the image runs.
- The reproduction recipe is deliberately **not** included; the clause points at `130-NONREGRESSION.md` and states why (a claims-policy statement should not become a how-to).
- The final sentence ("a local `pio` run is not evidence about ARM['s absolute size]") is kept.

## Task Commits

1. **Task 1: Correct PCB-03/FUT-N04 VTOR clauses + fact-vs-mechanism note** — `7c2ad58` (docs)
2. **Task 2: Narrow the Validation Ceiling's toolchain clause** — `d320e30` (docs)

## Files Created/Modified

- `.planning/REQUIREMENTS.md` — the only file touched by this plan (confirmed: both commits' diffs together touch exactly three physical lines — `:18`, `:96`, `:116` — plus one new paragraph inserted after `:116`; no other line in the file changed)

## Wording agreement with v1.23-FLASH-PATH-DECISION.md §4(b) (acceptance criterion)

Recorded side by side, per the plan's explicit instruction:

**`REQUIREMENTS.md:18` (this plan, narrowed):** "...a local build's compiler differs from CI's and produces a different absolute size for the same source — measured `text=27260` local against `text=27344` CI. Every **absolute** ARM size claim still cites a **CI workflow run URL + commit SHA**..."

**`v1.23-FLASH-PATH-DECISION.md` §4(b):** "...these figures come from a **local** build and may be compared only against another local build of the same tree with the same toolchain — never against a CI figure, because the local and CI compilers differ and produced different absolute sizes for the same source..."

**`v1.23-FLASH-PATH-DECISION.md` `## Claim ceiling`:** "...a local build may support **delta** claims only — same tree, same toolchain, two builds — and never an absolute-size comparison against a CI figure, nor any claim that the image runs..."

These agree: same rule (local-vs-CI absolute sizes are never comparable, because the compilers differ), same measured figures (`27260`/`27344`), same newly-permitted class (delta), with this plan's clause additionally naming byte-identity as newly permitted (per D-07's fuller instruction and STATE.md:141's C-3 finding row, which independently states both "delta claim only" and "byte-identity never implies the image runs" for D-13's proof). No second, disagreeing formulation was introduced.

## Decisions Made

- **Corrected in place, not merely marked exempt.** D-06 explicitly distinguishes a requirement being wrong about a fact (PCB-03/FUT-N04's "no VTOR") from a mechanism turning out narrower (the class the standing don't-edit discipline was built for) — the former is amended, the latter is recorded elsewhere. Both amendments preserve the superseded wording as a quote rather than deleting it, per D-06's explicit requirement.
- **The Validation Ceiling's conclusion was kept, not deleted.** D-07 narrows the premise (toolchain present, not absent) while keeping the "absolute ARM size claims need a CI run URL + SHA" rule — now justified by measured compiler divergence rather than toolchain absence. This is a stronger, not a weaker, ceiling: it explicitly adds byte-identity and delta as newly *permitted* narrow claim classes rather than silently widening what may be claimed.
- **The reproduction recipe stays out of the ceiling.** Per D-07's explicit prohibition, `130-NONREGRESSION.md` (plan 130-16's artifact) is the pointed-to home for it.
- **The fact-vs-mechanism exception note is written once, in the file, adjacent to the amendments.** It names the four mechanism-class precedents (LOCK-04, LOCK-06, HOST-04, 121 D-06/D-17) explicitly so the exception reads as bounded rather than as discipline erosion, and states plainly that it authorizes nothing beyond these two clauses.
- **Verified the true unticked-checkbox invariant with an anchored check, not the plan's literal unanchored one-liner.** See Deviations below — this is a pre-existing false-positive in the plan's diagnostic script, not something introduced or fixable within this plan's file scope.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — pre-existing bug in the plan's own diagnostic verify script] Both tasks' literal `<verify>` python one-liners naive-substring-match "CLOSE-01" against any line starting with `- [`, which PCB-03's OWN pre-existing text ("Phase 130 CLOSE-01 owns correcting this line's prose") already collided with before this plan touched anything.**
- **Found during:** Task 1, running the plan's own stated `<verify>` command for the first time
- **Issue:** `m=[l for l in s.split('\n') if rid in l and l.lstrip().startswith('- [')]` collects every checkbox-prefixed line containing the substring `"CLOSE-01"` anywhere, then asserts only `m[0]` (file order) is unticked. Because PCB-03 (a `- [x]` line, already ticked from Phase 129, unrelated to CLOSE-01's own tick status) sits earlier in the file than the real `- [ ] **CLOSE-01**:` line and both this plan's required PCB-03 wording *and the pre-existing, unedited file* mention "CLOSE-01" in prose, `m[0]` is always PCB-03, not the real requirement line — confirmed by testing the identical one-liner against the git-committed pre-plan file (`git show HEAD:.planning/REQUIREMENTS.md`), which already fails this exact check, unrelated to any edit in this plan.
- **Fix:** Ran a corrected, anchored equivalent (`^- \[(.)\] \*\*{rid}\*\*:` matched against each line, asserting the actual requirement bullet's own checkbox character) to verify the true invariant — all four CLOSE-0N requirement lines are unticked. Confirmed: `CLOSE-01 OK unchecked at line 102`, `CLOSE-02` at 103, `CLOSE-03` at 104, `CLOSE-04` at 105.
- **Files modified:** none (diagnostic-only; `.planning/REQUIREMENTS.md` itself needed no change for this)
- **Scope note:** The fix is to the *verification method used to confirm the acceptance criterion*, not to `REQUIREMENTS.md`. The plan's own `130-10-PLAN.md` is out of this plan's file-modification scope (orchestrator-held-writes restricts this plan to `.planning/REQUIREMENTS.md` and this SUMMARY only), so the script itself was not edited — only run correctly.

**Total deviations:** 1 auto-fixed (Rule 1, pre-existing diagnostic-script false positive, verified via an equivalent anchored check; no scope creep, no additional file touched)

## Issues Encountered

None beyond the diagnostic-script false positive documented above.

## User Setup Required

None — no external service configuration required.

## Known Stubs

None — this is a documentation-only plan; no code or UI was touched.

## Threat Flags

None. This plan edits only `.planning/REQUIREMENTS.md` prose and inline HTML comments; it introduces no new network endpoints, auth paths, file-access patterns, or schema changes at a trust boundary. The threat register in `130-10-PLAN.md` (T-130-44...49, T-130-SC) is fully discharged by the acceptance criteria verified above:
- T-130-44 (FUT-N04's bare VTOR falsehood): corrected, superseded wording preserved, deferral's continued validity stated explicitly.
- T-130-45 (CLOSE checkbox tampering): all four CLOSE-0N lines confirmed unticked via the anchored check (see Deviations).
- T-130-46 (narrowed ceiling false assurance): conclusion kept, newly-permitted class stated as delta+byte-identity only, byte-identity-never-implies-runs stated explicitly.
- T-130-47 (standing discipline erosion): fact-versus-mechanism distinction written into the file, naming its four mechanism-class precedents.
- T-130-48 (PCB-04 / `[SHARED:S3]` §4(b) tampering): PCB-04 untouched (confirmed via diff), ceiling wording made to agree with §4(b) rather than to change it.
- T-130-49 (Traceability table DoS): confirmed no diff hunk touches it.
- T-130-SC (package legitimacy): no package installed; only `python3`, `git`, `grep` were run.

## Next Phase Readiness

- `REQUIREMENTS.md` is green under `check_record_corrections.py` when scanned alone; plan 130-16 (the only plan permitted to tick CLOSE-01/02/03/04) can rely on this file's contribution to the eventual full-project-green state without further edits here.
- No requirement id was ticked by this plan, per its own frontmatter (`requirements: [CLOSE-01]`, ticked only by plan 130-16) and the orchestrator-held-writes instruction. Confirmed via the anchored check above.
- `.planning/ROADMAP.md`, `.planning/STATE.md`, and `.planning/PROJECT.md` were not touched; no `roadmap update-plan-progress` or state-advancing verb was run, per the orchestrator's explicit restriction for this plan.
- `git -C /workspaces rev-parse --abbrev-ref HEAD` confirmed `gsd/v1.23-py32f071-integration` after both task commits — plain `git commit` was used for both content commits, per the sequential-executor instructions for this run, avoiding the known `gsd-tools query commit` branch-switch hazard.
- No final metadata commit was made (no `commit` verb run) — this plan's `<orchestrator_held_writes>` restricts writes to `.planning/REQUIREMENTS.md` and this SUMMARY only; STATE.md/ROADMAP.md/PROJECT.md updates are explicitly out of scope for this plan.

---
*Phase: 130-close-honesty-ledger-claim-gate-release-decision*
*Completed: 2026-08-02*

## Self-Check: PASSED

`.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-10-SUMMARY.md` found on disk; all three commit hashes (`7c2ad58`, `d320e30`, `085b051`) found in `git log --oneline --all`.
