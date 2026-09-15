# Phase 192: Live References Only - Context

**Gathered:** 2026-09-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Every reference a reader could act on today points at `firestarter_fw`; every reference that records
history still says what it said. Covers **SWEEP-01, SWEEP-02, SWEEP-03**.

The phase depends on Phase 189 only. It is the milestone's last sweep phase and owns the **meta**
repository's reference surface outright, plus the **re-verification** — not the repair — of both sub-repos.

**In scope:** meta `README.md`; all seven `.planning/codebase/` documents, corrected by a real
`/gsd-map-codebase` remap rather than by hand-patching; the two runnable v1.4 artefacts at `.planning/`
top level (`v1.4-e2e-verify.sh`, `v1.4-RELEASE-PROCEDURES.md`); a hand amendment of SWEEP-03 in
`REQUIREMENTS.md`; the boundary-aware proof that both sub-repos are already clean; and the D-5 proof that
`.planning/milestones/` is untouched.

**Out of scope (settled earlier, not re-litigated here):** claiming `henols/firestarter` (D-1, seed
`SEED-claim-firestarter-slug.md`); mirroring firmware releases onto the meta repository (D-2); everything
under `.planning/milestones/` (D-5); the firmware repository's own slug references (189 D-09, done); the
`firestarter_app` working tree (190 D-04, done); `origin/main` (191, done); the `.gitmodules` history trap
and the adoption instrument (D-6, GATE-01, Phase 193).

**Measured at discussion time, not assumed.** Boundary pattern `henols/firestarter($|[^_A-Za-z0-9])`,
`/usr/bin/grep` over `git ls-files` — **not** PATH `grep`, which is ugrep here and honours `.gitignore`:

| Repository | Branch | Matching tracked files |
|---|---|---|
| `firestarter` (firmware) | `v1.38-repository-rename` | **0** |
| `firestarter_app` (host) | `v1.38-repository-rename` | **0** |
| meta | `gsd/v1.38-repository-rename-activated-2026-09-13` | **244** — 173 under `.planning/milestones/`, 71 outside |

Of the 71 outside `milestones/`: the 6 named by SWEEP-01 (`README.md` 1 hit, `STACK.md` 2,
`INTEGRATIONS.md` 3, `ARCHITECTURE.md` 2, `STRUCTURE.md` 1, `TESTING.md` 1), the 2 runnable artefacts, and
**63 records**. `git log f0307ac8..HEAD -- .planning/milestones/` returns **0 commits** — D-5 holds today.

</domain>

<decisions>
## Implementation Decisions

### The sweep rule — an allowlist, not a 65-row denylist

- **D-01:** **Edit only what a reader could act on today; everything else in `.planning/` is a record.**
  The edited set is therefore closed and small: `README.md`, the seven `.planning/codebase/` documents,
  and the two runnable artefacts of D-02. Every other match is left byte-identical.
  **Why an allowlist and not a classification pass:** the operator's constraint was "simple, not
  over-engineered, future-proof". A per-file judgement over 65 files is neither simple nor stable — a
  future sweep would have to re-derive every call. An allowlist derived from a one-sentence test collapses
  it to "is this a record?", which new phase directories answer automatically by existing.
  **No SWEEP-01 amendment is needed and none is made.** SWEEP-01's opening clause already states the rule
  — *"Every **live tracked** reference … addresses `firestarter_fw`"* — and its em-dash list reads as an
  enumeration of the known instances, not as a boundary. The requirements-coverage gate reads true on the
  written text either way.
  **The executor must enumerate the remainder once**, in phase evidence: the full match list with the
  edited subset marked. The blast radius is then a recorded decision rather than an executor's silence.

- **D-02:** **The two runnable v1.4 artefacts are repointed — all 13 occurrences, no staleness banner.**
  `.planning/v1.4-e2e-verify.sh` (**7** occurrences) and `.planning/v1.4-RELEASE-PROCEDURES.md` (**6**).
  Every one is unambiguous: each sits directly beside a `henols/firestarter_app` twin, with surrounding
  comments naming it the firmware side, so this is mechanical with no per-site judgement.
  **Why these two and no other `.planning/` file:** they are the only matches a reader *executes*. The
  script was cited as a working pattern as recently as v1.34 Phase 160
  (`.planning/milestones/v1.34-phases/160-.../160-07-PLAN.md`), and
  `.planning/v1.4-RELEASE-PROCEDURES.md:325` hands the operator
  `gh release delete <tag> -R henols/firestarter`. Everything else in this sweep is stale-and-confusing;
  **that one line is stale-and-destructive** the moment the slug is reclaimed for the meta repository —
  which is precisely what the deferred seed proposes.
  **No banner.** A "not re-validated since v1.4" header is overhead that does not reduce the risk, and it
  would assert a currency claim this phase does not measure.
  — **Reversibility:** reversible — 13 string edits in two untested planning artefacts, no consumer.

### The seven codebase documents — remapped, not patched

- **D-03:** **Correct `.planning/codebase/` by running `/gsd-map-codebase`, not by hand-patching.**
  All **seven** documents are stale, not the five SWEEP-03 and criterion 4 name between them: `CONCERNS.md`
  (9 retired-CI references) and `CONVENTIONS.md` (2) were named by neither. The meta repository has **no
  `.github/workflows/` at all** — `.github/` holds `CONTRIBUTING.md` and `ISSUE_TEMPLATE` only.
  `catalog-sync-check.yml` was retired in `7d7179ec`; `wiki-check.yml` and `wiki-publish.yml` in
  `5426d7ef`; `tools/wiki/` was removed 2026-09-08.
  **Why a remap over surgical edits:** the frontmatter reads `last_mapped_commit: 3e2f7d89` /
  `last_mapped_at: 2026-08-26`, and **four** later commits hand-patched these files without touching it
  (`face9459`, `769a83cd`, `6af22051`, `6d91e338`). A fifth hand-patch continues a pattern that has already
  produced documents whose own provenance claim is false. The remap is the only option that ends with the
  documents *and* their frontmatter true.
  — **Reversibility:** costly — a remap rewrites content far beyond the rename; undoing it means restoring
  seven files from git and re-applying the corrections by hand.

- **D-04:** **Run the remap at the recorded scope, verbatim:**
  `/gsd-map-codebase --paths .claude,.devcontainer,.github,.gitignore,.gitmodules,.vscode,CLAUDE.md`
  Reproducible and directly comparable to the 2026-08-26 run. A full-repo scan is declined: it would walk
  `.planning/` — thousands of files, and `STATE.md` carries a 52k-character single line that is a known
  performance trap — and both submodule working trees, which are separate repositories tracking their own
  `.planning/codebase/`.
  **Stated consequence, so the executor does not discover it:** `tools/` is outside this scope, so
  `STRUCTURE.md`'s stale `tools/wiki/` claim dies **by omission rather than by correction**, and the
  regenerated document will say nothing about `tools/catalog/`, which does exist. That satisfies criterion
  4 as written. It is recorded here as an accepted narrowing, not an oversight.

- **D-05:** **Preserved history is re-attached after the remap, with its existing wording intact.**
  `STACK.md` carries *"Prior analysis: 2026-05-08 (submodule layer — preserved below, not re-verified this
  run)"*. Capture the seven documents before the remap; afterwards, restore any dropped `Prior analysis` /
  preserved sections **verbatim, including the "not re-verified" caveat that already disclaims them**.
  Nothing is silently lost, and the restored text carries its own warning.

- **D-06:** **The remap is the mechanism; the boundary-aware sweep is the gate.**
  After the remap, re-run the `/usr/bin/grep` sweep over the seven documents and hand-correct any survivor.
  *"The mapper reads `.gitmodules`, so it will write the new slug"* is an assumption, and criterion 1 fails
  **silently** if it is wrong. The same post-remap check confirms no document asserts a retired workflow or
  `tools/wiki/` as live. Criteria 1, 3 and 4 are proved against the post-remap tree, never against the
  mapper's intent.

- **D-07:** **SWEEP-03 in `REQUIREMENTS.md` is amended by hand to name all seven documents**, so the
  traceability table stays honest for anyone reading it after close.
  **Hand edit only — do not use a GSD requirements verb.** Those verbs reformat the whole file, which
  would bury a one-line scope correction inside an unreviewable diff.
  — **Reversibility:** reversible — one paragraph in one tracked file.

### The regression guard inherited from three phases

- **D-08:** **No standing guard is built. The debt is recorded as deliberately unpaid.**
  189 D-10, 190 D-05 and 191 D-02 each declined a check and named this phase as where the boundary-aware
  pattern would be built. **SWEEP-01, SWEEP-02 and SWEEP-03 do not ask for one**, and three facts say it
  should stay unbuilt: the meta repository has no `.github/workflows/` to host it; source-scanning gates in
  this project have a documented history of failing **open** after renames; and a guard that cannot fail is
  worse evidence than a named gap.
  **`SUMMARY.md` must state the gap plainly, not omit it:** after this phase, **nothing watches any of the
  three repositories for slug regression** — including `origin/main`, which Phase 191 left with no
  `tests/` directory, no `[test]` extra and no `ci.yml`. 191 D-02 closed that by assignment to this phase;
  this phase closes it by declaration instead. A reader must be able to see that this was chosen.

### Claude's Discretion

The operator delegated the sweep rule (D-01) and the runnable-file disposition (D-02) explicitly —
"you decide, as long as it's simple, not over-engineered and future-proof" and "you decide, least overhead
and clearest workflow". Both are recorded above as locked decisions, not as open latitude.

Settled mechanically, without consuming a question:

- **D-09:** **The D-5 proof range is anchored on the merge-base, not on local `beta`.** Criterion 2's
  diff is taken as `git diff --stat f0307ac8..HEAD -- .planning/milestones/` — `f0307ac8` being
  `git merge-base beta HEAD` as measured 2026-09-13 — and the plan recomputes the merge-base rather than
  hardcoding that SHA. Local `beta` goes stale in this project, which is why the milestone-close procedure
  recreates it from `origin/beta` before shipping. Measured now: **0 commits**, diff empty. The proof is
  re-taken at verification time, because this phase itself must not be the thing that breaks it.
- The todo cross-reference is **not** folded — see `<deferred>`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### This phase's own inventory
- `.planning/phases/192-live-references-only/192-SCOUT.md` — pre-discussion evidence produced by
  `/gsd-plan-phase 192` before it exited at the CONTEXT gate. The per-file hit tables and the
  retired-workflow line numbers are already derived; **do not re-derive them**. Its "Open fork" is
  resolved by D-07. Note its operator-answer section is *input*, superseded by the `D-NN` rows above.

### Requirements and scope
- `.planning/REQUIREMENTS.md` §SWEEP — SWEEP-01, SWEEP-02, SWEEP-03. **D-07 amends SWEEP-03 here.**
- `.planning/REQUIREMENTS.md` §Decisions — D-5 (`.planning/milestones/` is historical-by-intent) and the
  "Repairing the 672 archived references" out-of-scope row.
- `.planning/ROADMAP.md` §"Phase 192: Live References Only" — goal and the four success criteria.

### Prior-phase decisions this phase inherits
- `.planning/phases/189-free-the-name/189-CONTEXT.md` — D-09 (firmware repo owned by 189; 192 re-verifies
  only) and D-10 (no guard in 189; the pattern deferred here).
- `.planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/190-CONTEXT.md` — D-04 (`firestarter_app`
  working tree owned by 190), D-05 (no guard), and D-02, which records **why a naive negative grep on the
  bare slug is vacuous**: `henols/firestarter` is a substring of `henols/firestarter_fw`. The
  boundary-aware pattern exists for exactly this reason.
- `.planning/phases/191-the-branch-that-reaches-users/191-CONTEXT.md` — D-02, which names the
  `origin/main` regression gap and assigns it here. D-08 answers it.

### Tooling this phase drives
- `.claude/gsd-core/workflows/map-codebase.md` — the `--paths` contract used by D-04. Lines 33–66 define
  incremental-remap mode; line 44 documents the `last_mapped_commit` stamp.

### Files the phase edits
- `README.md` (meta) — 1 occurrence.
- `.planning/codebase/{ARCHITECTURE,CONCERNS,CONVENTIONS,INTEGRATIONS,STACK,STRUCTURE,TESTING}.md`.
- `.planning/v1.4-e2e-verify.sh` (7) and `.planning/v1.4-RELEASE-PROCEDURES.md` (6).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **The boundary-aware sweep command itself** — `git ls-files | while read -r f; do /usr/bin/grep -nE
  'henols/firestarter($|[^_A-Za-z0-9])' "$f"; done`. Used by 189, 190 and 191 and by this discussion; it
  is the phase's single instrument. **`/usr/bin/grep` is load-bearing**: PATH `grep` in this devcontainer
  is ugrep, which honours `.gitignore` and silently under-scans.
- **Per-phase evidence directories** — 189, 190 and 191 each wrote their sweep transcript under
  `${phase_dir}/evidence/` (`189-firmware-slug-sweep.txt`, `190-slug-sweep.txt`). D-01's enumeration
  follows that established shape.

### Established Patterns
- **Records are never repaired.** D-5 states it for `.planning/milestones/`; D-01 generalises it. The
  project already holds the converse rule for `file:LINE` citations, and the two do not conflict: a
  `.planning/`→`.planning/` citation is historical-by-intent and repairing it destroys the evidence.
- **Source-scanning gates fail open after renames.** Cited by 189 D-10, 190 D-05 and 191 D-02; it is the
  load-bearing reason for D-08.

### Integration Points
- **`/gsd-map-codebase` writes the seven documents in place** and stamps `last_mapped_commit` with the
  current HEAD. It is the only writer this phase does not control line-by-line, which is why D-06 puts a
  sweep between it and the acceptance criteria.
- **`.gitmodules`** already resolves `firestarter_fw` (Phase 189) and is inside the remap scope, so the
  mapper reads the corrected URL rather than the redirect.

</code_context>

<specifics>
## Specific Ideas

- The operator's two standing constraints, in their own words: **"simple, not over-engineered and
  future-proof"** for the sweep rule, and **"least overhead and clearest workflow"** for the runnable
  files. A planner adding review gates, per-file classification tables, banners or CI scaffolding is
  working against both.
- `.planning/PROJECT.md` is deliberately untouched despite 6 matches, and two of them show why the
  record/act-on test is the right cut: **line 1396** carries a live
  `https://github.com/henols/firestarter/actions/runs/30722352902` link that now resolves only through the
  redirect, and **line 69** says the destructive act in 999.9 is *claiming* `henols/firestarter` — correct
  exactly as written. Both are records. Neither is edited.

</specifics>

<deferred>
## Deferred Ideas

- **A standing slug-regression guard** — D-08 declines it here. If it is ever built it needs a host: the
  meta repository has no `.github/workflows/`, and firmware CI is `native` + `native_nodevtools` +
  `pytest tests/` only.
- **`origin/main` has no test surface at all** (191 D-02) — no `tests/`, no `[test]` extra, no `ci.yml`.
  Any future guard for the default install has nowhere to live until that changes.
- **`.planning/v1.4-RELEASE-PROCEDURES.md` currency** — D-02 repoints its URLs but makes **no claim** that
  the v1.4 release procedure is still correct. Re-validating it is separate work.

### Reviewed Todos (not folded)

`gsd-tools query todo.match-phase 192` returned **37** matches. **None folded.** Every one scored on
generic keywords (`firestarter`, `phase`, `planning`, `live`) with no relation to the reference surface —
the list is dominated by firmware defects (`FM1608 byte 0`, `CONFIG_VERSION`, VPP checks) and host database
questions. Two adjacent-looking items are genuinely unrelated: *"Separate the .gitignore classes"* concerns
bench-measurement retention, and *"Strip residual GSD provenance comments from product source"* concerns
`firestarter/` and `firestarter_app/` source, which this phase does not touch.

Two tracker items are about the **release pipeline**, not references, and belong to the backlog Phase 191
filed them in: *"release.yml's git-auto-commit-action push to main is rejected by the Protect main
ruleset"* and *"publish.yml's release published trigger is suppressed for bot-created releases"*.

</deferred>

---

*Phase: 192-live-references-only*
*Context gathered: 2026-09-13*
