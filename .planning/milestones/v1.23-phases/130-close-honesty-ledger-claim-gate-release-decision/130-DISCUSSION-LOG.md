# Phase 130: Close — Honesty Ledger, Claim Gate, Release Decision - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-02
**Phase:** 130-close-honesty-ledger-claim-gate-release-decision
**Areas discussed:** The push & b15 cut (CLOSE-04), R-1…R-18 correction mechanism (CLOSE-01),
Ledger claim classes + negative space (CLOSE-02), Renumber mechanics (CLOSE-03)

**Gray-area selection:** all four offered areas were selected.

---

## The push & b15 cut (CLOSE-04)

### Q1 — Does v1.23 merge to `beta` and cut `3.0.0b15` in-phase, or is the recorded decision a deliberate no-push?

| Option | Description | Selected |
|--------|-------------|----------|
| Accept — the merge IS the cut | Record, merge `--no-ff`, push, let CI cut b15, manual `publish.yml` for PyPI, verify both channels. First real publication of `firestarter_py32f071.hex`. No PY32F071 board exists; py32 is beta-only by construction. | ✓ |
| Avoid — record a deliberate no-push | `beta` stays at b14; the merge waits for the close ritual. Nothing advertises a nonexistent board. REL-01..04 stays proven-by-deleted-rehearsal. | |
| Accept, gated on a fresh rehearsal first | `rehearsal=true` dispatch from the milestone branch before the merge. Re-derives evidence from run `30722352902`. | |

**User's choice:** Accept — the merge IS the cut (**D-01**)
**Notes:** Framed with the measured fact that both repos are 0 behind `origin/beta`, so no inbound
catch-up merge exists — the outbound merge is clean either way, which removes the largest source of
risk v1.22 carried.

### Q2 — How are the two b15 release bodies produced and gated before they go public?

| Option | Description | Selected |
|--------|-------------|----------|
| Hand-written, behind a blocking operator wording review | Committed drafts carrying the ceiling, PCB-05's socket-empty instruction, and an explicit never-run-on-silicon statement; human read before either goes out. v1.22 D-08/D-16 + Plan 116-07. | ✓ |
| Hand-written, posted once the claim scanner is green | Same content, mechanical gate only. Faster; but the scanner's own docstring says it cannot detect an implied overclaim or wrong tone. | |
| Hand-write the firmware body only | Firmware carries the py32 asset; app body left to CI default. Cost: the app is the half that gained `fw --board py32f071`. | |

**User's choice:** Hand-written, behind a blocking operator wording review (**D-02**)

### Q3 — If the real b15 firmware release publishes without the py32 asset, is that a hard failure or an honestly-recorded outcome?

| Option | Description | Selected |
|--------|-------------|----------|
| Gate — assert the asset is present on the real cut | Read from `gh release view`; absence is a hard failure to root-cause via `py32f071.yml`'s loud run. Does not touch the containment design. | ✓ |
| Record, don't gate | Absence recorded in the ledger and the release body. Matches `continue-on-error`'s design intent. Cost: REL-02's real-cut evidence stays a rehearsal artifact. | |
| Gate, with one diagnostic re-dispatch allowed | Assert; on absence, operator re-dispatches read-only, then decide. Extra round-trip. | |

**User's choice:** Gate — assert the asset is present on the real cut (**D-03**)
**Notes:** Surfaced because `beta-build.yml`'s ARM steps are `continue-on-error: true` by design,
so b15 can publish perfectly green with no py32 asset at all.

### Q4 — Where is the boundary between Phase 130 and `/gsd-complete-milestone`?

| Option | Description | Selected |
|--------|-------------|----------|
| Publish in-phase; tag + final merge stay with the close ritual | Assert gitlinks still match the tips at phase end, re-bumping only if this phase's own commits move one. Mirrors v1.22 D-07 / v1.21 P115 while keeping this milestone's in-phase gitlink practice. | ✓ |
| Phase 130 does publish + gitlink + the `v1.23` tag | Everything lands here. Cost: local `beta` lags origin after CI's auto-commit, so a tag cut before a fetch points at the wrong commit. | |
| Publish only — say nothing about gitlinks | Cost: v1.22 learned an unasserted gitlink drifts silently. | |

**User's choice:** Publish in-phase; tag + final merge stay with the close ritual (**D-04**)

---

## R-1…R-18 correction mechanism (CLOSE-01)

### Q1 — Do the corrections land as in-place edits or labeled correction blocks?

| Option | Description | Selected |
|--------|-------------|----------|
| Per document kind — hybrid | `⚠ CORRECTION` blocks in PROJECT.md + ROADMAP.md (both read by `/gsd-new-milestone` to seed scope); in-place in STATE.md; append-only SUPERSEDED section in the dated note. | ✓ |
| Edit in place everywhere | Cleanest grep result. Cost: destroys the correction trail and rewrites a dated capture. | |
| Correction blocks everywhere | Maximally auditable. Cost: block sprawl in STATE.md and the note. | |

**User's choice:** Per document kind — hybrid (**D-05**)
**Notes:** Grounded by confirming the stale figures are live — `2992 B` in three files,
`27 commits behind` and `311eacf` across the note/ROADMAP/PROJECT — and that some hits already sit
inside correctly-labeled blocks.

### Q2 — Does CLOSE-01 amend `REQUIREMENTS.md`, which is not in its own stated file list?

| Option | Description | Selected |
|--------|-------------|----------|
| Amend both, each with an inline supersession note | PCB-03's and FUT-N04's VTOR clauses corrected, citing `129-RESEARCH` C-1. Justified by the false-fact vs narrower-mechanism distinction, and PCB-03's own text assigning the job to CLOSE-01. | ✓ |
| Amend FUT-N04 only; leave PCB-03 alone | FUT-N04 states the falsehood bare on a live item; PCB-03 already carries its correction inline. | |
| Leave REQUIREMENTS.md untouched | Strict standing discipline. Cost: FUT-N04 ships permanently asserting something known false. | |

**User's choice:** Amend both, each with an inline supersession note (**D-06**)

### Q3 — How is the Validation Ceiling's toolchain-absent clause narrowed?

| Option | Description | Selected |
|--------|-------------|----------|
| Narrow in place; recipe goes in the non-regression doc | Premise replaced (toolchain IS installable; local absolute size never comparable to CI — 27260 vs 27344); delta and byte-identity claims newly permitted; recipe lives with the evidence. | ✓ |
| Narrow in place, recipe included | Self-contained ceiling. Cost: a claims policy becomes a how-to, and recipes rot faster. | |
| Leave the ceiling; record the narrowing in the ledger | Cost: the governing document keeps asserting something disproven. | |

**User's choice:** Narrow in place; recipe goes in the non-regression doc (**D-07**)
**Notes:** Noted during the exchange that `v1.23-FLASH-PATH-DECISION.md` §4(b) already uses this
exact narrowed wording independently — the correction is consistent, not novel.

### Q4 — What proves CLOSE-01 complete?

| Option | Description | Selected |
|--------|-------------|----------|
| A committed, label-aware checker + planted-violation fixture | Phrase table skipping labeled blocks; fixture proves non-zero exit on a planted stale figure AND a mislabeled block. Guards the next milestone's seeding. | ✓ |
| A recorded one-off sweep in `130-NONREGRESSION.md` | Cheaper; nothing runs downstream. Cost: nothing prevents reintroduction at seeding time. | |
| Extend the existing `check_permitted_claims.py` phrase table | Cost: conflates two jobs and its all-or-nothing arming is keyed to four artifact names. | |

**User's choice:** A committed, label-aware checker + planted-violation fixture (**D-08**)

---

## Ledger claim classes + negative space (CLOSE-02)

### Q1 — How is `130-LEDGER.md` organised?

| Option | Description | Selected |
|--------|-------------|----------|
| Claim classes by evidence tier | Rows grouped by kind of evidence — CI-compile-only, AVR-measured, native-simulated, mock-only, real-published-artifact, decision-only-unverified. Makes the strength gradient visible. | ✓ |
| Claim classes by requirement category | One row per BASE/MERGE/VPP/CFG/HOST/REL/PCB. Closest 122-LEDGER mirror. Cost: hides the gradient. | |
| Only the honesty surface | The four named non-claims and nothing else. Cost: no single source for the permitted wording the release bodies must match. | |

**User's choice:** Claim classes by evidence tier (**D-09**)

### Q2 — How wide is the ledger's negative space?

| Option | Description | Selected |
|--------|-------------|----------|
| Deferrals AND every owned residual | Eight FUT items plus HOST-01's deviation, HOST-04's mypy debt, HOST-06's UM1504, REL-03's local-only half, REL-04's F-8, 129's F-10, and 129's two open hardware questions. | ✓ |
| Deferrals only | Residuals stay with their measurements. Cost: F-10 especially deserves top billing. | |
| Residuals only | REQUIREMENTS.md already lists the deferrals. Cost: v1.22 D-12 considered and rejected exactly this. | |

**User's choice:** Deferrals AND every owned residual (**D-10**)

### Q3 — b15 will publish a firmware image presenting Puya's registered USB vendor identity. How is that handled?

| Option | Description | Selected |
|--------|-------------|----------|
| Land the interim `1209:0001` before the cut, and state it in the body | Two `#define`s plus the source warning pid.codes' terms require. The record itself calls the interim id strictly better. Cost: a firmware change in a close phase, needing an ARM pass and a lockstep `[SHARED:S4]` edit. | ✓ |
| State it plainly in the body; leave `usb_cdc.c` alone | Honors Phase 129 D-06. Cost: the published artifact still presents someone else's identity. | |
| The ship gate blocks the py32 asset from b15 | Literal reading of the gate. Cost: loses REL-02's real-cut proof; §5(e) rates allocation confidence LOW pre-schematic. | |
| Ledger-only — the release body stays silent | Cost: the one option where an outward-facing artifact omits a known problem. | |

**User's choice:** Land the interim `1209:0001` before the cut, and state it in the body (**D-11**)
**Notes:** This collision was found by cross-referencing the ship gate at
`v1.23-FLASH-PATH-DECISION.md:202` against D-01's cut; it was not on the original gray-area list.
It is a deliberate scope addition and reverses Phase 129 D-06 on new facts.

### Q4 — What claim/sourcing vocabulary does the ledger use?

| Option | Description | Selected |
|--------|-------------|----------|
| Both axes, explicitly | 129's sourcing tags plus a v1.22-style claim status per row; orthogonal questions, cross-reference only. | ✓ |
| Phase 129's tag vocabulary only | One vocabulary milestone-wide. Cost: sourcing does not tell a release-notes author what is safe to publish. | |
| v1.22's status key only | Matches the ledger precedent exactly. Cost: drops the sourcing distinction 129 spent five tags establishing. | |

**User's choice:** Both axes, explicitly (**D-12**)

---

## Renumber mechanics (CLOSE-03)

### Q1 — How do the v1.28 / v1.29 py32 slots retire, and what fills the v1.23 line?

| Option | Description | Selected |
|--------|-------------|----------|
| Both replaced by one pointer line; v1.23 gains its real SHIPPED entry | Lines 33–34 collapse into a dated retirement line; line 28 becomes `✅ v1.23 PY32F071 Integration — Phases 123–130 (SHIPPED …)`. The stale prior-art paragraph goes with the entry. | ✓ |
| Delete both outright; v1.23 gains its SHIPPED entry | Shortest list. Cost: the 999.23/999.24 stubs point into a void. | |
| Keep both, marked RETIRED with content intact | Cost: the option the todo explicitly warns against — a scoping pass reads the body regardless of the marker. | |

**User's choice:** Both replaced by one pointer line; v1.23 gains its real SHIPPED entry (**D-13**)
**Notes:** Surfaced mid-question that `ROADMAP.md`'s `## Milestones` list has **no**
`v1.23 PY32F071 Integration` entry at all — the active milestone exists only as a detail section at
line 1993. BCP vacating the v1.23 number is what makes room to fix it.

### Q2 — Where does the renumbered Binary Command Protocol sit, and does v1.30 compact into the freed v1.29?

| Option | Description | Selected |
|--------|-------------|----------|
| BCP moves into version order; v1.30 stays; annotate BCP's stale sequence line | Preserves the list's strict version ordering; v1.29 left vacant and explained; honors the v1.30 entry's own "at activation, not now". | ✓ |
| BCP moves into version order; v1.30 compacts to v1.29 now | No vacant numbers. Cost: contradicts the v1.30 entry's written instruction and risks two renumbers disagreeing. | |
| BCP moves into version order; change nothing else | Minimum surface. Cost: "v1.28 … Sequence ahead of v1.24" left unexplained. | |

**User's choice:** BCP moves into version order; v1.30 stays; annotate BCP's stale sequence line (**D-14**)

### Q3 — Do the backlog stubs that reference the retired slots get updated?

| Option | Description | Selected |
|--------|-------------|----------|
| Retire 999.23/999.24 as shipped-into-v1.23; fix the v1.29 back-references | Their work landed in Phases 123–130; the "→ v1.28" pointer is actively wrong once v1.28 is BCP. 999.22 and 999.25 untouched. | ✓ |
| Retarget the slot references only | Smallest diff. Cost: two stubs stay QUEUED for finished work, overstating the open-item count. | |
| Leave the backlog untouched | Literal criterion scope. Cost: two stubs point at BCP as the home of PY32F071 HAL work. | |

**User's choice:** Retire 999.23/999.24 as shipped-into-v1.23; fix the v1.29 back-references (**D-15**)

### Q4 — How is the v1.24–v1.27 byte-unchanged claim proven?

| Option | Description | Selected |
|--------|-------------|----------|
| Recorded before/after hashes + path-scoped diff, one-shot | SHA-256 per entry before and after, plus the exact `git diff` and its output, in `130-NONREGRESSION.md`. Deliberately no checker, with the reason recorded. | ✓ |
| A committed checker + planted-violation fixture | Maximally consistent with BASE-08. Cost: wrong the day v1.24 is scoped; ships pre-obsolete. | |
| Fold the assertion into the CLOSE-01 checker | Cost: mixes a permanent invariant with a one-shot one; the combined tool inherits the shorter lifetime. | |

**User's choice:** Recorded before/after hashes + path-scoped diff, one-shot (**D-16**)

---

## Wrap-up

Offered a further round covering plan-ordering constraints, whether the `1209:0001` edit needs its
own operator-gated ARM CI run, the stray `3.0.0b12` prereleases, and whether any community thread
gets a comment. **User chose "I'm ready for context."** The sequencing constraints were derived and
recorded in CONTEXT.md rather than asked; the b12 cleanup and the no-community-comment position are
recorded as deferred/declined.

## Claude's Discretion

- Every word of both release bodies and of `130-LEDGER.md`, within the four stated wording constraints.
- The ledger's exact row count, column set and section order.
- Whether the ledger quotes the ceiling verbatim or cites it by location (the self-reference trap
  that tripped all six `125-0N-SUMMARY.md` files).
- The shape of the channel-verification evidence.
- Whether any artifact beyond the contracted four is added — and if so, amending `_DEFAULT_TARGETS`
  in the same commit.
- Plan ordering, subject to the ten hard sequencing constraints in CONTEXT.md.
- Commit granularity for the R-N corrections.

## Deferred Ideas

- Deleting the stray `3.0.0b12` prereleases (not re-opened; declined at v1.22 D-05).
- A fresh `rehearsal=true` dispatch before the merge (declined at D-01).
- Compacting `v1.30` into the freed `v1.29` (declined at D-14).
- A committed checker for the v1.24–v1.27 byte-unchanged claim (declined at D-16, reason recorded).
- Blocking the py32 asset from b15 on the ship gate (declined at D-11).
- Filing the pid.codes PR for a real `1209:<pid>` — operator's act, prerequisite is public PCB
  design files.
- FUT-N02/N04/N05/N06, FUT-VPP, FUT-CAL, FUT-ORACLE, FUT-ARMSIZE — recorded in the ledger, none
  acted on.
- Phase 129's two open hardware questions (`nBOOT1` default, USB D+ pull-up).
- F-10's part-selection consequence (QFN56/QFN32 cannot carry a contiguous PB0–PB7 bus).
- The v1.30 SDP milestone's gh#12 outward-facing debt — owned by its own todo, not this phase.
