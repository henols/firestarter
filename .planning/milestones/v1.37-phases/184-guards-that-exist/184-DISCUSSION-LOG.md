# Phase 184: Guards That Exist - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-11
**Phase:** 184-guards-that-exist
**Areas discussed:** The grep's true scope, The consumerless scan-path entry, CLAIM-09's guard shape, CLAIM-03's verdict + grounds

---

## Area selection

All four offered gray areas were selected for discussion.

| Option | Description | Selected |
|--------|-------------|----------|
| The grep's true scope | Criterion 1's bare substring catches 4 files beyond CLAIM-01's target | ✓ |
| The consumerless scan-path entry | `test_configure_memory.cpp`'s only resolver is gone; floor at 6 | ✓ |
| CLAIM-09's guard shape | Which field, how to resolve free-text `resolved_by`, cross-repo posture | ✓ |
| CLAIM-03's verdict + grounds | Retire vs re-guard, and what evidence decides it | ✓ |

---

## The grep's true scope

Pre-question sweep reported to the operator: of the eight files `5426d7ef` deleted, only
`dispatch_mirror.py` is still named outside `.planning/` anywhere. Also surfaced meta `CLAUDE.md:12`'s
stale `tools/wiki/` claim, found by the same sweep.

| Option | Description | Selected |
|--------|-------------|----------|
| Re-date, don't delete | Keep the provenance, cite the deletion (`39ea3e8`, 2026-08-31) so it is recoverable from git; amend criterion 1 to exclude a citation that names its own deletion | ✓ (by discretion) |
| Strip the module name | Describe the shape without naming the deleted module; grep goes literally clean; loses the provenance | |
| Leave them, scope the criterion | Touch neither file; amend criterion 1 to target live-guard claims only, per Phase 182's criterion-4 precedent | |

**User's choice:** "You decide."
**Notes:** Orchestrator selected re-date. Rationale recorded in CONTEXT.md D-02: the provenance is the
only record of why `check_no_exists_proxy.py`'s compound arm exists, so stripping it invites a future
deletion of the arm itself; leaving it untouched keeps the citation unverifiable, which is the CLAIM
strand's own complaint. Meta `CLAUDE.md:12` folded in as D-04.

---

## The consumerless scan-path entry

Established before the question: `scan_paths.py:113` is the only app-repo reference to
`test_configure_memory.cpp`, so the deletion is settled by the inventory's own definition. Both floor
assertions sit at 7 and land on 6; the module docstring claims 8.

| Option | Description | Selected |
|--------|-------------|----------|
| Re-anchor to a reason | Keep 6, replace its census justification with why the inventory cannot work below it; fix the stale 8 | ✓ (by discretion) |
| Leave 6, fix the prose only | Smallest diff; accepts that the next removal forces a floor edit under pressure | |
| Let the new guard remove it | Don't hand-delete; build CLAIM-09's check and let the real entry fail it — plant, observe red, remove | ✓ (by discretion) |

**User's choice:** "You decide."
**Notes:** Orchestrator took options 1 and 3 together — they compose rather than compete. Recorded as
D-13 and D-15. The guard-removes-it path discharges criterion 2 against the genuine defect first, with
the planted synthetic running afterward as a second control.

---

## CLAIM-09's guard shape

Established before the question: after the rotted entry is removed, all remaining `resolved_by` values
are bare `test_*.py` filenames in `tests/`, so no restructuring is needed today. Placement decided
mechanically (fifth test in `test_scan_paths_resolve.py`, not a `tools/` checker, since `tools/` sits
outside every CI gate).

| Option | Description | Selected |
|--------|-------------|----------|
| Forbid it outright | Assert every `resolved_by` is a bare filename under `tests/`; cross-repo or annotated strings fail at authoring time | ✓ |
| Typed cross-repo entries | Carry repo + path; checked when the repo is present — but the meta repo is never in app CI, so it degrades to a skip | |
| Parse by convention | Strip parentheticals, resolve bare names, treat `/` as repo-relative; the prose-parsing is itself unguarded | |

**User's choice:** "[No preference]" — orchestrator's recommendation taken.
**Notes:** Recorded as D-11. The deciding argument: a design where an unverifiable resolver is
*unrepresentable* beats one where it is representable but silently skipped — which is the exact mode
that let 168-04 write a meta-repo path nothing could check.

---

## CLAIM-03's verdict + grounds

Decisive evidence presented before the question: `KNOWN_PROTOCOLS` (12 entries) and
`kAllProtocolFamilies` (13 rows) have already drifted in both directions — `0x34` host-only, `0x35`/`0x39`
firmware-only — and the firmware test's comment asserting "one row per `KNOWN_PROTOCOLS` entry" is
therefore false in three places, with nothing watching.

| Option | Description | Selected |
|--------|-------------|----------|
| Retire 3-way, backlog 2-way | Retire the three-way as designed; file the narrower machine-readable successor to the backlog (orchestrator's recommendation) | |
| Retire it outright | Record the retirement and close the question; no successor filed; a future need re-opens it from scratch | ✓ |
| Re-guard, promote it | Pull the two-way guard into scope now; would require amending the milestone's Out of Scope table | |

**User's choice:** Retire it outright.
**Notes:** Operator chose against the orchestrator's recommendation. Recorded as D-05, with D-06 added
so that no planner or executor "helpfully" files the successor or an unverified-drift item and quietly
reinstates what was closed.

### Follow-up: the two documents that still assert the invariant

The project's source-comment hard rule was stated before the options: writing a corrected comment is not
available, so only deletion or leaving-it-standing were on the table for the firmware test.

| Option | Description | Selected |
|--------|-------------|----------|
| Delete both claims | Drop `PROTOCOLS.md`'s paragraph entirely and the firmware test's false clause | |
| Delete + state the absence | Same deletions, but `PROTOCOLS.md` gains one honest line that no tool machine-reads it — mirrors meta `CLAUDE.md`'s "no automated wiki guard exists now" | ✓ |
| PROTOCOLS.md only | Fix only the document CLAIM-01 names; leave the firmware test's comment alone | |

**User's choice:** Delete + state the absence.
**Notes:** Recorded as D-09 and D-10. D-10 carries the hard-rule constraint explicitly: an executor who
cannot remove the false clause without authoring replacement prose must leave it and record the
deviation.

### Follow-up: the drift

| Option | Description | Selected |
|--------|-------------|----------|
| Record it, don't adjudicate | State the three divergences as measured, name the reason each side carries, say explicitly that this phase did not verify them | ✓ (by discretion) |
| Adjudicate each difference | Trace all three against v1.11 DEC-05 and the X88C64P decision; a real clearance rather than an assumption | |
| Omit the drift entirely | Keep the note strictly about the decision asked for | |

**User's choice:** "You decide."
**Notes:** Orchestrator selected record-don't-adjudicate (D-16). Adjudicating means protocol-domain work
the milestone's Out of Scope bars, and a defect surfaced there would have no room to be fixed here. No
backlog item filed either — the operator had just chosen the branch that files nothing, and an
open-question item would partially reinstate it.

---

## Claude's Discretion

Four decisions were deferred by the operator ("You decide" ×3, "[No preference]" ×1):

- **The surviving provenance citations** → re-date, not strip or ignore (D-02), plus the criterion
  amendment that follows from it (D-03)
- **The floor, and how the stale entry is removed** → re-anchor to a reason, and let the new guard's RED
  remove the entry (D-15, D-13)
- **The cross-repo posture for `resolved_by`** → forbid it outright (D-11)
- **The drift** → record, don't adjudicate (D-16)

Decided by the orchestrator as mechanical consequences rather than offered as questions: folding in meta
`CLAUDE.md:12` (D-04), deleting rather than re-pointing the fixtures (D-07), the `.planning/notes/`
verdict document and its four required contents (D-08), the sweep being complete at `dispatch_mirror`
(D-01), and the guard's placement (D-12).

Operator decisions that must not be revisited without asking: **D-05** (retire outright) and
**D-09/D-10** (delete and state the absence).

## Deferred Ideas

- **The two-way `KNOWN_PROTOCOLS` ↔ `kAllProtocolFamilies` successor guard** — considered and explicitly
  declined by the operator. Recorded in CONTEXT.md as a rejected option, **not** as a backlog candidate.
- **`test_configure_memory.cpp:9` cites `build_db.py:89`** for a symbol at line 137 — same defect class
  as CLAIM-06, but firmware-side and outside this phase's requirements. Not filed.
- **The three unadjudicated divergences** (`0x34`, `0x35`, `0x39`) — named as an open question in the
  verdict note, with no tracker, by the operator's choice.

### Todos reviewed, none folded

`todo.match-phase 184` returned 35 matches, all 0.4–0.6 on generic keyword overlap and none touching
this phase's subject. A targeted search for `scan_paths` / `dispatch_mirror` / `ScanPathEntry` across
`.planning/todos/` found only two completed todos, both already consulted. Zero folded.
