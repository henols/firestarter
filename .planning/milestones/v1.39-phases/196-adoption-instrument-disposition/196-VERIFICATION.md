---
phase: 196-adoption-instrument-disposition
verified: 2026-09-17T20:00:00Z
status: passed
score: 8/8 must-haves verified
covered_files:
  - ".gitignore"
  - ".planning/PROJECT.md"
  - ".planning/REQUIREMENTS.md"
  - ".planning/ROADMAP.md"
  - ".planning/graphs/.last-build-status.json"
  - ".planning/graphs/GRAPH_REPORT.md"
  - ".planning/notes/adoption-instrument-retirement.md"
  - ".planning/phases/196-adoption-instrument-disposition/196-01-PLAN.md"
  - ".planning/phases/196-adoption-instrument-disposition/196-01-SUMMARY.md"
  - ".planning/phases/196-adoption-instrument-disposition/196-02-PLAN.md"
  - ".planning/phases/196-adoption-instrument-disposition/196-02-SUMMARY.md"
  - ".planning/phases/196-adoption-instrument-disposition/196-03-PLAN.md"
  - ".planning/phases/196-adoption-instrument-disposition/196-03-SUMMARY.md"
  - ".planning/phases/196-adoption-instrument-disposition/196-CONTEXT.md"
  - ".planning/phases/196-adoption-instrument-disposition/196-REVIEW.md"
  - ".planning/seeds/SEED-claim-firestarter-slug.md"
  - "CLAUDE.md"
covered_digest: "v1:sha256:e012f80c22583d5be1eaf47aba3eeec363bf719c3a4bf0b417cb5e0c8d0a1e07"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 196: Adoption Instrument Disposition Verification Report

**Phase Goal:** The instrument built to decide whether the slug claim was safe either measures a
question that still has a consumer, or is retired with its reason recorded.
**Verified:** 2026-09-17
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The instrument is removed from the working tree and the git index | ✓ VERIFIED | `tools/adoption/` absent from disk; `git ls-files -- tools/adoption` empty; `tools/` now holds exactly `catalog/` |
| 2 | The disposition and its reason are recorded where a reader meets the decision, not only in a commit message | ✓ VERIFIED | `.planning/notes/adoption-instrument-retirement.md` exists, 85 lines, 5 ordered section headings, VERDICT states the full D-04 causal chain (2026-09-14, 12.8%, 90%, 116, 10, 2026-09-13), both D-05 declined alternatives named, D-06 cost stated, zero method residue on independent scan |
| 3 | No live document describes the instrument as gating a claim that has already fired — seed, `CLAUDE.md`, and notes agree | ✓ VERIFIED | Independently re-ran the INSTR-02 proof expression (verbatim, from `196-RESEARCH.md`/`196-03-PLAN.md` §R2.1) against the live tree from this session's own shell: `INSTR02_GATE: GREEN - zero residual references (boundary=347)`. Manually read `CLAUDE.md`, `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md` and the seed annotation — all describe the instrument as retired/past-tense, none names it as gating a live claim |
| 4 | Criterion 3 (consumer-naming) is vacuously satisfied because the instrument was not retained | ✓ VERIFIED | `.planning/ROADMAP.md` Phase 196 criterion 3 reads: "The instrument was not retained, so this criterion is vacuously satisfied and no consumer is named." |
| 5 | Requirements INSTR-01 and INSTR-02 are recorded complete only after their proof ran | ✓ VERIFIED | Both checkboxes `[x]`, both traceability rows `Complete`, both carry `**Complete:**` clauses without citing the retired path; git commit order shows the proof-and-flip (`f00f7ac0`) landed after the sweep (`9a3be9c6`) and the graph rebuild (`f6a2b622`) |
| 6 | The knowledge graph is regenerated after the deletion, and no longer carries a file node for the deleted script | ✓ VERIFIED | `.planning/graphs/GRAPH_REPORT.md` (13,276 lines, "Built from commit: `719a6768`") contains no line `- pypi_version_share.sh`; the one surviving hit is a community-node label sourced from the frozen Phase 193 archive, exactly as D-11/R2.4 predict |
| 7 | Neither sub-repo nor the wiki checkout was touched; branch discipline held | ✓ VERIFIED | `git diff --name-only f9806ec5..HEAD` touches no path under `firestarter_app/`, `firestarter_fw/`, or `firestarter.wiki/`; HEAD stays on `v1.39-protocol-0x05-write-correctness` throughout; no tag on HEAD |
| 8 | No commit in this phase carries AI/Claude attribution | ✓ VERIFIED | `git log -1 --format='%B'` for all four phase commits (`4fb83755`, `9a3be9c6`, `f6a2b622`, `f00f7ac0`) scanned for attribution patterns — all clean |

**Score:** 8/8 truths verified (0 present, behavior-unverified)

### Scrutinized Deviations (see task brief)

**1. D-04 verbatim-quote elision (196-01).** The note quotes the operator with a marked
mid-sentence ellipsis (`"I have no idea what it is… Don't understand why we should need it."`)
instead of the full sentence, because the full sentence contains the literal token "clickhouse",
which D-06's own residue gate ("no ClickHouse, anywhere") forbids in this file absolutely. The
elision is disclosed in the ellipsis itself (not hidden), the substance of the operator's grounds
(confusion about the technology, explicit instruction to delete regardless of cost) survives
intact, and the SUMMARY documents the conflict and the resolution in full. Two literal instructions
in the same plan were in direct conflict for this one token; D-06 is explicitly labeled "the hard
constraint on this file" and is a required verification token, so treating it as controlling over
the softer "quoted verbatim" phrasing is a defensible, disclosed judgment call, not a
misrepresentation. **Judgment: honors D-04's intent.** Verified independently — the residue scan on
the finished note is clean (no `[Cc]lick[Hh]ouse` anywhere), and the operator's actual grounds are
present in substance.

**2. `.planning/graphs/.last-build-status.json` hand-authored by the executor (196-03).**
Independently confirmed the executor's own finding: the file is written *only* by
`.claude/hooks/lib/gsd-graphify-rebuild.sh`, invoked by a `PostToolUse` hook gated to
`current branch == default branch`, which is inert on this milestone branch — so the documented
manual build chain the plan directs genuinely never writes this file, and the acceptance criterion
as authored was unsatisfiable by the pipeline it names. The executor wrote the file by hand in the
hook's exact schema (`ts`, `status`, `exit_code`, `duration_ms`, `head_at_build`,
`graphify_version`), which is exactly the shape of a self-attested proof — an executor authoring
the file a gate reads. Independent corroboration, however, is strong and multi-sourced: `graph.json`
(103,434,677 bytes), `graph.html` (3,029,634 bytes) and `GRAPH_REPORT.md` (1,099,432 bytes / 13,276
lines) all carry the identical mtime `2026-09-17 19:19:39 UTC`; `GRAPH_REPORT.md`'s own text states
"Built from commit: `719a6768`" and "64332 nodes · 106869 edges" — matching the SUMMARY's
independently-quoted `gsd_run graphify status` reading exactly; the deleted script's file node is
genuinely absent from the regenerated report (only reproducible if the deletion was on disk when
the 212–248-second build ran); and the mtime sequencing is consistent with the build completing
before the commit that includes the hand-written status file (`f6a2b622` at 19:22:07Z). **This leg
is partly self-attested — the `"status": "ok"` / `"exit_code": 0` fields were not mechanically
produced by the pipeline, they were transcribed by the executor** — but the remaining,
independently checkable parts of GRAPH-FRESH (marker freshness via mtime, ≥5,000-line report,
matching node/edge counts, matching commit stamp, and the genuine absence of the file node) are
sufficient, taken together, to carry the acceptance criterion on this evidence. Flagging plainly
rather than passing silently: **this is a real gap between the plan's documented tooling and its own
acceptance criterion** (a plan defect, not an executor fabrication), and a future phase that reuses
this build chain should either fix the criterion or fix the chain so the status file is genuinely
pipeline-produced.

**3. `SEED-AT-CANONICAL-PATH` case-statement bug (196-02).** Independently reproduced: `case "$ST"
in R*|*D*)` tests the whole porcelain line, and `SEED-claim-firestarter-slug.md` contains an
uppercase `D` (from `SEED`), so a synthetic ` M .planning/seeds/SEED-claim-firestarter-slug.md`
status incorrectly matches `*D*`. Confirmed this is a real bug in `196-02-PLAN.md`'s own verify
leg, that it fails closed (a false rejection of a legitimate `M` status, never a false pass of a
real rename/delete), and that the executor did not edit the plan to route around it — it
inspected the true two-character status code directly and recorded the finding rather than hiding
it. The underlying property holds on independent verification: `git log --follow` on the seed shows
continuous, unbroken history with no rename; `git diff --stat f9806ec5..HEAD` for the seed shows
exactly one file, one insertion, zero deletions; the current `git status --porcelain` for the seed
is empty (clean, tracked, committed, at its canonical path `.planning/seeds/`). **The seed was
modified in place, not renamed or deleted, and stayed at its canonical path — confirmed.**

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.planning/notes/adoption-instrument-retirement.md` | Primary retirement record, ≥55 lines, VERDICT + 4 sections | ✓ VERIFIED | 85 lines; all 5 headings present in order; causal-chain figures present; zero method residue |
| `tools/adoption/pypi_version_share.sh` (deleted) | Removed from tree and index | ✓ VERIFIED | Absent from disk; `git ls-files` confirms not in index; no copy anywhere under version control |
| `CLAUDE.md` | One `tools/` occupant + dated retirement paragraph | ✓ VERIFIED | "holds one directory"; `tools/catalog/` description intact; paragraph cites date + note path, no SHA |
| `.planning/PROJECT.md` | Third-item paragraph no longer claims instrument still runs | ✓ VERIFIED | Reworded closing sentence points at the retirement note |
| `.planning/REQUIREMENTS.md` | INSTR heading + INSTR-01/02 state settled disposition, both rows Complete | ✓ VERIFIED | Both checkboxes `[x]`, both rows `Complete`, Coverage totals unchanged (8/8, Unmapped: 0) |
| `.planning/ROADMAP.md` | Criteria 1 and 3 state settled disposition | ✓ VERIFIED | Criterion 1 points at the note; criterion 3 records vacuous satisfaction |
| `.planning/seeds/SEED-claim-firestarter-slug.md` | One appended annotation, frozen sections untouched | ✓ VERIFIED | Diff is 1 insertion, 0 deletions; file stays at canonical path |
| `.planning/graphs/GRAPH_REPORT.md` | Regenerated, no file node for deleted script | ✓ VERIFIED | 13,276 lines; file node gone; community node from frozen archive legitimately survives |
| `.gitignore` | `.planning/graphs/graph.html` ignored | ✓ VERIFIED | Line present; `git check-ignore -q` exits 0; HTML/JSON untracked |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| INSTR-02 proof expression | `.planning/ROADMAP.md` | boundary computed from `^## v1\.38 ` header | ✓ WIRED | Independently re-run: boundary=347, >300, excludes closed v1.38 section |
| `.planning/notes/adoption-instrument-retirement.md` | `.planning/notes/catalog-sync-check-retirement.md` | precedent skeleton (`^## VERDICT`) | ✓ WIRED | Pattern present |
| `.planning/notes/adoption-instrument-retirement.md` | `.planning/seeds/SEED-claim-firestarter-slug.md` | frozen dated reading (`12.8`) | ✓ WIRED | Figure present, matches seed |
| `CLAUDE.md` / `.planning/PROJECT.md` / seed | `.planning/notes/adoption-instrument-retirement.md` | path citation | ✓ WIRED | All three cite the note's exact path |
| `.planning/graphs/GRAPH_REPORT.md` | frozen Phase 193 archive | community-node label | ✓ WIRED (expected residue) | Confirmed at line 12290, community node not a file node |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|--------------|--------|----------|
| INSTR-01 | 196-01, 196-03 | Instrument removed; disposition recorded with reason | ✓ SATISFIED | Deletion + note verified above; row `Complete` |
| INSTR-02 | 196-02, 196-03 | No document describes instrument as gating a fired claim | ✓ SATISFIED | Sweep verified across 4 live docs + seed annotation; gate independently reproduced GREEN; row `Complete` |

No orphaned requirements — `REQUIREMENTS.md` Coverage totals (8 total, 8 mapped, 0 unmapped) match this phase's two IDs plus the six from prior phases.

### Anti-Patterns Found

Scanned all files this phase's diff touches (`f9806ec5..HEAD`), restricted to the added lines
(`git diff -U0` filtered to `^\+`), for `TBD|FIXME|XXX`: **clean across all seven files** (`CLAUDE.md`,
`.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, the seed, `.gitignore`,
the new note). Pre-existing `TBD` markers found in `.planning/PROJECT.md` and `.planning/ROADMAP.md`
are unrelated historical content, outside this phase's edited line bands, and untouched by any hunk
in this phase's commits — not a debt-marker gate hit.

No AI/Claude attribution in any of the four phase commits. No stray comments (this phase touches no
`firestarter_fw/`/`firestarter_app/` source; the rule does not apply). No `git add -A`/`-A .`/`-a`
evidence — every commit's diff is scoped to its documented explicit paths.

### Behavioral Spot-Checks / Probe Execution

Not applicable in the strict sense (documentation-only phase), but the phase's own proof mechanism
*is* a runnable check, and it was re-run independently rather than trusted from the SUMMARY:

| Check | Command | Result | Status |
|-------|---------|--------|--------|
| INSTR-02 gate, live tree | verbatim expression from `196-03-PLAN.md` Task 1/3 | `INSTR02_GATE: GREEN - zero residual references (boundary=347)` | ✓ PASS |
| `tools/` occupant count | `ls tools/` | only `catalog/` | ✓ PASS |
| Diff scope vs sub-repos/wiki | `git diff --name-only f9806ec5..HEAD` | no path under `firestarter_app/`, `firestarter_fw/`, `firestarter.wiki/` | ✓ PASS |
| Graph freshness | mtime + line count + node/edge counts vs report text | consistent, 13,276 lines, counts match | ✓ PASS (see deviation 2 above for the self-attested sub-field) |

### Human Verification Required

None. All must-haves resolved to VERIFIED via independently reproduced, mechanical evidence. The
one self-attested sub-field (`.last-build-status.json`'s `status`/`exit_code`) is corroborated by
enough independent, cross-checked physical evidence (matching mtimes across three generated
artifacts, matching node/edge counts against the report's own text, and the genuine, otherwise
unreproducible absence of the deleted script's file node) that it does not rise to an open question
requiring a human read — but it is recorded here, plainly, as a real gap between this plan's
documented tooling and its own acceptance criterion, for whoever next touches this build chain.

### Gaps Summary

No gaps. The phase goal is achieved: the adoption instrument is deleted from the working tree and
the index; the full retirement reason (causal chain, declined alternatives, accepted cost) is
recorded in a single, durable, tracked note; every live document that previously described the
instrument as live or as gating an open claim now agrees with the settled disposition, verified via
an independently re-run single-expression gate proven red before green; the frozen seed carries
exactly one appended annotation and is otherwise untouched; the knowledge graph was regenerated
after the sweep and no longer carries a file node for the deleted script; and both requirements are
recorded `Complete` only after their proof ran, with the proof re-run once more afterward to confirm
`REQUIREMENTS.md`'s own edit did not reintroduce a residual reference.

Three deviations were recorded by the executors and independently scrutinized above (a disclosed
quote elision under genuine instruction conflict, a self-attested build-status sub-field with strong
independent corroboration, and a fail-closed bug in one plan's verify leg with the underlying
property confirmed true by hand). None of them falls below the bar for the phase's success
criteria, and none was accepted uncritically — each was independently reproduced or reasoned through
rather than taken on the SUMMARY's word.

---

_Verified: 2026-09-17_
_Verifier: Claude (gsd-verifier)_
