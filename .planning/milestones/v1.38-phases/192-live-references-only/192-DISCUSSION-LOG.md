# Phase 192: Live References Only - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-13
**Phase:** 192-live-references-only
**Areas discussed:** Sweep boundary, Runnable files, Codebase docs, Regression guard

---

## Area selection

All four offered gray areas were selected.

| Option | Description | Selected |
|--------|-------------|----------|
| Sweep boundary — what counts as "live" | SWEEP-01's opening clause says *every* live tracked reference; its second half names a closed list of 8 files. 65 further tracked meta files match outside `.planning/milestones/`. | ✓ |
| The two runnable files nobody assigned | `v1.4-e2e-verify.sh` and `v1.4-RELEASE-PROCEDURES.md` are followable today and reach the firmware repo only through the rename redirect. Named by no requirement, protected by no decision. | ✓ |
| Codebase docs — how wide, and the requirement fork | Seven docs carry retired-CI text, not the five named between SWEEP-03 and criterion 4. Plus the stale `last_mapped_commit` four hand-patches never updated. | ✓ |
| The regression guard deferred three times | 189 D-10, 190 D-05, 191 D-02 each named Phase 192 as where the boundary-aware pattern gets built; SWEEP-01/02/03 never ask for one. | ✓ |

---

## Sweep boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Classification test, with the remainder enumerated | Edit only what a reader could act on today; leave records; enumerate the classified-as-history set in evidence. | |
| Closed list only — the 8 named files | SWEEP-01's second half is operative; everything else out of scope by construction. | |
| Classification test, and amend SWEEP-01 to carry it | Same test, written into SWEEP-01 in place of the closed list. | |

**User's choice:** *Other* — "You decide, as long as it's simple, not over-engineered and future-proof."

**Notes:** Resolved as **D-01**. Chosen form is the first option, expressed as an **allowlist** rather than
a per-file classification pass, because a 65-file judgement is neither simple nor stable across future
sweeps. "Future-proof" was read as the decisive constraint: the real future event is the bare slug being
claimed for the meta repository (the deferred seed), at which point every unrepaired *actionable*
reference silently retargets — which the closed-list option does not survive. No SWEEP-01 amendment: its
opening clause already states the rule and the em-dash list reads as enumeration, so the coverage gate
reads true on the written text.

---

## Runnable files

| Option | Description | Selected |
|--------|-------------|----------|
| Repoint both — they are live tooling, not records | Rewrite every `-R henols/firestarter` occurrence to `henols/firestarter_fw`. | |
| Repoint, and mark both as v1.4-era | Same edits plus a "not re-validated" header on each. | |
| Leave both — v1.4 artifacts are records | Treat them as the same class as `MILESTONES.md`; keep the phase diff minimal. | |

**User's choice:** *Other* — "you decide, least overhead and clearest workflow."

**Notes:** Resolved as **D-02** — repoint both, no banner. 13 occurrences total (7 in the script, 6 in the
procedures doc), each sitting beside a `henols/firestarter_app` twin, so the rewrite is mechanical. The
banner was declined on both stated constraints: it is overhead that does not reduce the risk, and
"not re-validated since v1.4" is a currency claim this phase does not measure. Decisive evidence was
`v1.4-RELEASE-PROCEDURES.md:325`, which carries `gh release delete <tag> -R henols/firestarter` — the only
match in the whole sweep where staleness is destructive rather than merely confusing.

---

## Codebase docs

**Question 1 — how should the seven documents be corrected?**

| Option | Description | Selected |
|--------|-------------|----------|
| Hand-patch the stale claims only | Surgical edits; leaves `last_mapped_commit` stale, consistent with the four prior hand-patches. | |
| Hand-patch, and correct the frontmatter too | Same edits plus a frontmatter update, which would claim a mapping that did not happen. | |
| Run `/gsd-map-codebase` for a real remap | Regenerate from the current tree; truthful content and truthful frontmatter, at the cost of a wide diff. | ✓ |

**Question 2 — should `REQUIREMENTS.md` be amended?**

| Option | Description | Selected |
|--------|-------------|----------|
| Amend SWEEP-03 to name all seven | Requirement matches what ships; traceability table stays honest. | ✓ |
| Extend without amending — record it in CONTEXT.md | No requirements churn; a reader of REQUIREMENTS.md alone would not know. | |

**Question 3 — what scope should the remap run at?**

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse the recorded scope exactly | `.claude,.devcontainer,.github,.gitignore,.gitmodules,.vscode,CLAUDE.md` — reproducible, comparable to the 2026-08-26 run. | ✓ |
| Recorded scope plus `tools/` | Would let STRUCTURE.md actively describe `tools/catalog/` instead of dropping `tools/wiki/` by omission. | |
| Full-repo scan | Walks `.planning/` and both submodule trees; expensive and off-target. | |

**Question 4 — what happens to preserved `Prior analysis` sections?**

| Option | Description | Selected |
|--------|-------------|----------|
| Re-attach after the remap, marked as before | Restore verbatim with the existing "not re-verified" caveat intact. | ✓ |
| Let it go, and record the deletion | Accept the loss and name it in SUMMARY.md; recoverable from git. | |
| Diff first, then decide per section | Most careful, but adds a review gate inside execution. | |

**Notes:** Resolved as **D-03** through **D-07**. The remap was chosen over a fifth hand-patch because the
frontmatter (`last_mapped_commit: 3e2f7d89`, 2026-08-26) has already been invalidated by four later
hand-patching commits — `face9459`, `769a83cd`, `6af22051`, `6d91e338`. Two consequences were recorded
rather than left for the executor: with `tools/` outside the chosen scope, `STRUCTURE.md`'s stale
`tools/wiki/` claim dies by omission and the regenerated document says nothing about `tools/catalog/`
(**D-04**); and the remap is a mechanism, not a gate, so the boundary-aware sweep re-runs afterwards and
hand-corrects survivors (**D-06**). The SWEEP-03 amendment must be a hand edit — GSD's requirements verbs
reformat the whole file.

---

## Regression guard

| Option | Description | Selected |
|--------|-------------|----------|
| No guard — record the debt as deliberately unpaid | One-shot sweep; SUMMARY.md states that nothing watches any repo for slug regression. | ✓ |
| Ship the pattern as a runnable script, no CI | A re-runnable instrument under the phase directory or `tools/`, run by nobody automatically. | |
| Build a real CI guard for the meta repo | Stand up `.github/workflows/` and fail on a bare-slug match. | |

**Notes:** Resolved as **D-08**. Three phases deferred this here and none of the three SWEEP requirements
asks for it. Grounds recorded: the meta repository has no `.github/workflows/` to host a guard; this
project's source-scanning gates have a documented history of failing **open** after renames; and a guard
that cannot fail is worse evidence than a named gap. The resulting gap must be stated plainly in
`SUMMARY.md`, `origin/main` included — Phase 191 D-02 closed it by assignment to this phase, and this
phase closes it by declaration instead.

---

## Claude's Discretion

- **D-01** (sweep rule) and **D-02** (runnable files) were explicitly delegated — "you decide" on both,
  under the stated constraints. Recorded in CONTEXT.md as locked decisions, not as open latitude.
- **D-09** — the D-5 proof range was settled without consuming a question: anchor on
  `git merge-base beta HEAD` (`f0307ac8` as measured), recomputed rather than hardcoded, because local
  `beta` goes stale in this project. Measured at discussion time: 0 commits, diff empty.
- The todo cross-reference was not put to the user: all 37 matches scored on generic keywords with no
  relation to the reference surface.

## Deferred Ideas

- A standing slug-regression guard — declined by D-08; it would need a host that does not exist yet.
- `origin/main` has no test surface at all (no `tests/`, no `[test]` extra, no `ci.yml`), so any future
  guard for the default install has nowhere to live.
- Re-validating `.planning/v1.4-RELEASE-PROCEDURES.md` as a procedure — D-02 repoints its URLs and makes
  no claim about whether the v1.4 release flow is still correct.
