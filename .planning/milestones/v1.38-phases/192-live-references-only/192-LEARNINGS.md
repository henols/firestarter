---
phase: 192
phase_name: "Live References Only"
project: "Firestarter — Protocol-Aware Programming Architecture"
generated: "2026-09-14"
counts:
  decisions: 12
  lessons: 8
  patterns: 10
  surprises: 8
missing_artifacts:
  - "UAT.md"
---

# Phase 192 Learnings: Live References Only

## Decisions

### The sweep rule is an allowlist, not a 65-row denylist (D-01)
Edit only what a reader could act on today — `README.md`, the seven `.planning/codebase/` documents, the two runnable v1.4 artefacts. Every other match in `.planning/` is a record and is left byte-identical. The executor enumerates the remainder once, in phase evidence, with the edited subset marked.

**Rationale:** The operator's constraint was "simple, not over-engineered, future-proof." A per-file judgement over 65 files is neither simple nor stable — a future sweep would have to re-derive every call. An allowlist derived from a one-sentence test collapses it to "is this a record?", which new phase directories answer automatically by existing. The blast radius then becomes a recorded decision rather than an executor's silence.
**Source:** 192-CONTEXT.md, 192-DISCUSSION-LOG.md, 192-01-SUMMARY.md

---

### No SWEEP-01 amendment; SWEEP-03 amended by hand only (D-01, D-07)
SWEEP-01's opening clause already states the rule ("every **live tracked** reference"), and its em-dash list reads as an enumeration of known instances, not a boundary — so the coverage gate reads true on the written text unchanged. SWEEP-03, which named `STACK.md` alone, was widened to name all seven documents by direct `Edit`, confined by content match (`grep -n -F '**SWEEP-03**'`), never a hardcoded line number.

**Rationale:** GSD's requirements verbs reformat the whole file, which would bury a one-line scope correction inside an unreviewable diff. The hand edit left SWEEP-01, SWEEP-02 and the traceability row byte-identical (12-line diff at mark-complete time).
**Source:** 192-CONTEXT.md, 192-04-SUMMARY.md

---

### Repoint both runnable v1.4 artefacts — all 13 sites, no staleness banner (D-02)
`.planning/v1.4-e2e-verify.sh` (7 occurrences) and `.planning/v1.4-RELEASE-PROCEDURES.md` (6) repointed in full. No "not re-validated since v1.4" header.

**Rationale:** They are the only matches in the sweep a reader *executes*. Each sits directly beside a `henols/firestarter_app` twin, so the rewrite is mechanical with no per-site judgement. The banner was declined on both operator constraints: it is overhead that does not reduce the risk, and "not re-validated" asserts a currency claim this phase does not measure.
**Source:** 192-CONTEXT.md, 192-DISCUSSION-LOG.md

---

### Correct `.planning/codebase/` by a real remap, not a fifth hand-patch (D-03)
`/gsd-map-codebase` regenerates the documents rather than surgical edits being applied to them.

**Rationale:** The frontmatter read `last_mapped_commit: 3e2f7d89` / `last_mapped_at: 2026-08-26`, and four later commits (`face9459`, `769a83cd`, `6af22051`, `6d91e338`) hand-patched these files without touching it. A fifth hand-patch continues a pattern that has already produced documents whose own provenance claim is false. The remap is the only option that ends with the documents *and* their frontmatter true.
**Source:** 192-CONTEXT.md, 192-DISCUSSION-LOG.md

---

### Run the remap at the recorded scope verbatim, accepting that `tools/` dies by omission (D-04)
`--paths .claude,.devcontainer,.github,.gitignore,.gitmodules,.vscode,CLAUDE.md` — the same scope as the 2026-08-26 run. A full-repo scan was declined.

**Rationale:** Reproducibility and direct comparability to the prior run. A full scan would walk `.planning/` (thousands of files, and `STATE.md` carries a 52k-character single line that is a known performance trap) and both submodule working trees, which are separate repositories tracking their own `.planning/codebase/`. **Stated consequence, recorded rather than left for the executor to discover:** `STRUCTURE.md`'s stale `tools/wiki/` claim dies by omission rather than by correction, and the regenerated document says nothing about `tools/catalog/`, which does exist. An accepted narrowing, not an oversight.
**Source:** 192-CONTEXT.md, 192-DISCUSSION-LOG.md, evidence/192-disposition.md

---

### Preserved history is re-attached verbatim, caveat included (D-05)
The seven documents are captured before the remap; afterwards any dropped `Prior analysis` / preserved section is restored verbatim, including the "not re-verified this run" caveat that already disclaims it.

**Rationale:** Nothing is silently lost, and the restored text carries its own warning rather than needing a new one.
**Source:** 192-CONTEXT.md, 192-02-SUMMARY.md

---

### The remap is the mechanism; the boundary-aware sweep is the gate (D-06)
After the remap, the `/usr/bin/grep` sweep re-runs over all seven documents and any survivor is hand-corrected. Criteria 1, 3 and 4 are proved against the post-remap tree, never against the mapper's intent.

**Rationale:** "The mapper reads `.gitmodules`, so it will write the new slug" is an assumption, and criterion 1 fails **silently** if it is wrong. The gate earned itself: one bare-slug survivor did sit inside `INTEGRATIONS.md`'s preserved Part 2 (the GitHub releases endpoint) and was caught and corrected.
**Source:** 192-CONTEXT.md, 192-02-SUMMARY.md, 192-03-SUMMARY.md

---

### A real remap re-derives every stale fact it can see in scope, not just the named two
Beyond the slug and the retired workflow, the executors corrected GSD version (1.6.1 → 1.13.0), tracked `.claude/skills/` file count (7 → 9), the agent-tooling script inventory in `TESTING.md` (3 files/~1200 lines → 5 files/~2500 lines, adding `diff_db.py` and `test_supersede.py`), `permissions.allow` entries (95 → 110), hook/agent/command/reference/template counts, `.devcontainer/README.md`, and `post-create.sh`'s new GSD-install step.

**Rationale:** A genuine remap re-derives what it can see in scope rather than patching only the two facts the plan named — otherwise it reproduces exactly the half-truthful-document failure mode D-03 exists to end. Established by plan 02 and followed as precedent by plan 03.
**Source:** 192-02-SUMMARY.md, 192-03-SUMMARY.md

---

### In `CONCERNS.md`, sole-subject findings are deleted; still-valid findings keep the finding and lose the citation
Of the six retired-workflow citations, the three whose surrounding finding had no subject beyond the retired workflow (the "never passed" tech-debt entry, the mutable-tag/permissions entry, the "no gate proven RED" entry) were removed in full. The two whose surrounding finding was a still-valid general risk (worktree submodule under-detection, the `.gitignore` orphan-submodule incident) kept the finding and lost only the dead citation. Replaced by one honest present-tense entry: no `.github/workflows/` exists, so nothing tracked here is checked by CI.

**Rationale:** Applying one rule uniformly would either destroy live risk knowledge or leave dead citations standing. The distinction was made explicit per-entry rather than applied wholesale.
**Source:** 192-03-SUMMARY.md

---

### `tools/catalog/` descriptions removed, because the earlier rationale for including `tools/` died with the workflow
`CONVENTIONS.md`'s `tools/catalog/codegen.py` description was dropped and a `CONCERNS.md` test-coverage-gap finding narrowed to drop its `tools/catalog/` items.

**Rationale:** The earlier remap's reason for reaching into `tools/` scope was "a workflow references it" — that workflow is retired, so the justification no longer holds, and D-04 puts `tools/` out of scope.
**Source:** 192-03-SUMMARY.md

---

### No standing regression guard is built; the debt is recorded as deliberately unpaid (D-08)
189 D-10, 190 D-05 and 191 D-02 each declined a check and named this phase as where the boundary-aware pattern would be built. This phase closes that chain by declaration rather than by construction, and states the gap plainly in both the disposition record and the SUMMARY.

**Rationale:** Three facts say it should stay unbuilt — the meta repository has no `.github/workflows/` to host it; source-scanning gates in this project have a documented history of failing **open** after renames; and a guard that cannot fail is worse evidence than a named gap. `origin/main` in `firestarter_app` has no `tests/` directory, no `[test]` extra and no `ci.yml`, so a pin test would have nowhere to live and nothing to run it. A reader must be able to see that this was chosen, not overlooked.
**Source:** 192-CONTEXT.md, 192-DISCUSSION-LOG.md, evidence/192-disposition.md

---

### The D-5 proof range is anchored on a recomputed merge-base, and taken last (D-09)
Criterion 2's diff is taken over `git merge-base beta HEAD`, recomputed live rather than reusing the discussion-time `f0307ac8`, independently proved an ancestor of HEAD before anything was built on it, and taken after all four prior plans had landed.

**Rationale:** Local `beta` goes stale in this project — which is why the milestone-close procedure recreates it from `origin/beta` before shipping. Taking the proof last means the phase's own final plan cannot be the thing that breaks the property it proves.
**Source:** 192-CONTEXT.md, 192-05-SUMMARY.md

---

## Lessons

### A pure re-wrap breaks a byte-level anchor check — the words unchanged, the line boundary moved
Task 2's rewrap of `CONCERNS.md`'s scope-note paragraph moved "and" from the end of the anchor sentence to the start of the next wrapped line, so a `grep -F` check for the exact pre-remap anchor failed even though the substantive wording was identical. The same class of failure hit plan 05 independently: the first draft of the disposition record wrapped "still correct" onto a second line, breaking the exact-phrase acceptance leg.

**Context:** Twice in one phase, in two different plans, by two different executors. Both were caught by the plans' own verification before commit or before a SUMMARY claim was made. When a paragraph must preserve an exact anchor substring for a later byte-level gate, the line-wrap is part of the contract.
**Source:** 192-03-SUMMARY.md (Deviations, auto-fix 1), 192-05-SUMMARY.md (Deviations)

---

### `/usr/bin/grep` by explicit path is load-bearing in this devcontainer
PATH `grep` here is ugrep, which honours `.gitignore` and silently under-scans. Every sweep reading in the phase — plans, evidence transcripts, and the verifier's own independent re-measurement — used the explicit path.

**Context:** The failure mode is silence, not error: a boundary-aware sweep that under-scans returns a clean zero and the phase's criterion 1 passes falsely.
**Source:** 192-CONTEXT.md, 192-01-SUMMARY.md, 192-SCOUT.md, 192-VERIFICATION.md

---

### `grep -cF` with a dash-leading pattern is parsed as options
`/usr/bin/grep -cF '- [ ] **SWEEP-03**:'` failed because the shell passed the leading `- ` through as an option string. Re-run as `-cFe`, it passed.

**Context:** Hit on an ad hoc verification command, not a plan `<verify>` leg, and no file was affected — but the same construction in a gate would fail open.
**Source:** 192-04-SUMMARY.md (Issues Encountered)

---

### The shared-requirement-ID gate holds IDs Pending until the last declaring plan runs — check it, don't assume
Plans 02, 03 and 04 all declared SWEEP-01/SWEEP-03 and all correctly left them `Pending`; `requirements.ready-ids` reported 0/2 ready during plan 03. Plan 05, the last declaring plan, saw 3/3 ready and marked all three Complete.

**Context:** Verified via `requirements.ready-ids` at each point rather than inferred from "my plan finished." This is the correct behaviour of the gate working, and it is the opposite of the known failure mode where executors prematurely mark multi-plan requirements Complete.
**Source:** 192-03-SUMMARY.md, 192-05-SUMMARY.md

---

### The code-review gate excludes `.planning/`, so a documentation phase gets almost no review coverage
The diff touched many paths, but after the workflow's exclusions removed everything under `.planning/`, exactly one file remained reviewable: `README.md`. One file reviewed, zero findings, status clean — over a phase that modified eleven files.

**Context:** "Code review clean" is a true statement about ~7% of what the phase changed. For planning-artifact-heavy phases the review report is not a coverage signal, and the phase's own evidence gates are what carry the proof.
**Source:** 192-REVIEW.md, .planning/STATE.md

---

### Hand-patching a generated document leaves it asserting a provenance it does not have
Four commits hand-patched `.planning/codebase/` documents without touching `last_mapped_commit` / `last_mapped_at`, so the documents claimed to be a faithful 2026-08-26 mapping while carrying four rounds of later edits.

**Context:** The stale stamp was not a cosmetic detail — it was the decisive argument for D-03's full remap over a fifth surgical pass. A document whose own provenance claim is false cannot be repaired by another surgical pass.
**Source:** 192-CONTEXT.md, 192-DISCUSSION-LOG.md

---

### Once you actually re-derive, more is stale than the two things you came to fix
The remap surfaced six-plus additional drifted facts across the seven documents that no plan had named — version numbers, file counts, script inventories, config entry counts, and two files/steps that did not exist at the last mapping.

**Context:** Both executors treated these as in-scope under "rewrite the sections from that scan" rather than as scope creep, and recorded the reasoning. Stale facts in generated docs cluster around whatever was last hand-patched.
**Source:** 192-02-SUMMARY.md, 192-03-SUMMARY.md

---

### `phase.complete`'s warnings need reading, not obeying
Phase close emitted 5 warnings, all verified as false positives: 4 path-resolution misses on files that do exist, and D-1..D-7 treated as unresolved REQ-IDs when they are milestone decision identifiers.

**Context:** Each was checked individually rather than acted on or waved through, and the verdict recorded in STATE.md.
**Source:** .planning/STATE.md

---

## Patterns

### Every zero is paired with a non-vacuity control
No zero reading is reported as evidence without a non-zero control over the same file, range or pathspec: a bare-slug `0` beside a `henols/firestarter_(app|prom|fw)` count of 5–32; `milestones_commits: 0` beside `control_sibling_path_commits: 61` over `.planning/phases/` and `control_pathspec_tracked_files: 3440`; each sub-repo's `0` beside its `_prom` control of 4 and 8.

**When to use:** Any time a proof is an absence. A zero from a broken command, an unresolvable pathspec, an empty range or an under-scanning grep is indistinguishable from a zero that means what you want it to mean. Established in plan 01 and carried through all five plans and the verifier.
**Source:** 192-01-SUMMARY.md, 192-04-SUMMARY.md, 192-05-SUMMARY.md, evidence/192-disposition.md

---

### Boundary-anchored substitution, idempotent by construction
`sed -i -E 's|henols/firestarter\b|henols/firestarter_fw|g'` — the `\b` keeps `_app`, `_prom` and already-corrected `_fw` twins untouched, so re-running the command is a no-op.

**When to use:** Mechanical slug/identifier repointing where the old name is a prefix of the new one. `henols/firestarter` is a substring of `henols/firestarter_fw`, which is exactly why a naive negative grep on the bare slug is vacuous (190 D-02) and why the boundary pattern exists.
**Source:** 192-01-SUMMARY.md, 192-CONTEXT.md

---

### Capture preserved history before the rewrite, keyed to a named pre-remap SHA
`evidence/192-02-preserved-history.txt` recorded verbatim anchor lines for **all seven** documents against a `pre_remap_commit` SHA before any of them was rewritten — including the three owned by a later plan.

**When to use:** Before any regeneration that could silently drop content you intend to keep. A dropped section then shows up as a diff rather than as a memory exercise, and the later plan inherits a capture taken before the tree moved.
**Source:** 192-02-SUMMARY.md, 192-03-SUMMARY.md

---

### A not-re-verified marker is extended additively, never replaced
`[unverified in 2026-08-26 and 2026-09-14 scoped remaps]` — each remap's date joins the list rather than erasing the prior one.

**When to use:** Any provenance caveat on carried-forward content. Replacing the date would make a section look freshly verified by the newest run while hiding how long it has actually gone unchecked.
**Source:** 192-02-SUMMARY.md, 192-03-SUMMARY.md

---

### A correction inside a "carried forward verbatim" section is disclosed in that section's own caveat
`INTEGRATIONS.md`'s Part 2 releases endpoint had to be corrected; the section's caveat sentence was extended in place to name it as the one documented exception, rather than the correction being made silently.

**When to use:** Whenever a preserved/frozen block must be touched. The alternative — silently editing text labelled verbatim — destroys the label's meaning for every future reader.
**Source:** 192-02-SUMMARY.md

---

### Merge-base anchoring, recomputed live, ancestor-verified, and taken last
The range base is recomputed via `git merge-base beta HEAD` rather than reused from a discussion-time SHA, proved an ancestor of HEAD before anything is built on it, cross-checked against the earlier value, and the whole proof is taken after every other plan has landed.

**When to use:** Any "this path was never touched over the milestone" proof in this project, where local `beta` goes stale. Taking it last prevents the phase's own final plan from being what breaks the property it claims.
**Source:** 192-05-SUMMARY.md, 192-CONTEXT.md (D-09)

---

### A disposition record: one section per ROADMAP criterion, evidence filename cited inline
`evidence/192-disposition.md` answers each of the four success criteria in its own `## Criterion N` section, every claim naming the evidence file *and* the keyed reading that supports it, inline in the section rather than only in a closing table.

**When to use:** At phase close, so verification and the milestone audit can read the phase's own answer directly instead of re-deriving it from five SUMMARYs. Inline citation means a byte-level grep over the section range proves the citation, rather than trusting a summary table.
**Source:** 192-05-SUMMARY.md, evidence/192-disposition.md

---

### A "What this phase did not do" section, naming the debt in plain words
The disposition record closes by stating that nothing now watches any of the three repositories for slug regression, that the v1.4 procedure's currency is not claimed, that 938 matches are left as records under D-01, and that `STRUCTURE.md`'s `tools/wiki/` claim died by omission under D-04.

**When to use:** Any phase that declines work a prior phase assigned to it, or accepts a narrowing whose consequence a later reader would otherwise read as an oversight. Three phases had deferred the guard here; without this section the chain would simply have gone quiet.
**Source:** evidence/192-disposition.md, 192-05-SUMMARY.md

---

### Two-step enumeration: materialise the file list, then loop over it
A `git ls-files` enumeration is taken as two steps — write the list, then run a NUL-delimited loop over it — so no fallible `git` sits in a non-final pipeline stage where its exit status is swallowed.

**When to use:** Any repo-wide scan whose completeness is itself part of the evidence. The transcript then carries a `tracked_files_visited:` count checkable against a separately captured `git ls-files` total.
**Source:** 192-01-SUMMARY.md

---

### Re-read live and independently, not from the table you just wrote
Plan 03's Task 3 re-read all seven documents live rather than aggregating its own per-document transcript table, and the verifier re-took all four criterion readings itself rather than copying them from any SUMMARY or evidence file.

**When to use:** Any gate over output produced in the same plan or phase. A summary row derived from the numbers it is meant to check proves only internal consistency.
**Source:** 192-03-SUMMARY.md, 192-VERIFICATION.md

---

## Surprises

### Seven documents described the retired workflow as live, not the five the requirements named
SWEEP-03 named `STACK.md`; ROADMAP criterion 4 named four more. `CONCERNS.md` (9 retired-CI references) and `CONVENTIONS.md` (2) were named by neither.

**Impact:** Drove D-07's hand amendment of SWEEP-03 to name all seven documents, so the traceability table stays honest for anyone reading it after close, and expanded the remap's document set by 40%.
**Source:** 192-SCOUT.md, 192-CONTEXT.md, 192-04-SUMMARY.md

---

### The single most consequential stale reference was destructive, not merely confusing
`.planning/v1.4-RELEASE-PROCEDURES.md:325` hands the operator `gh release delete <tag> -R henols/firestarter` — the one match in the whole sweep where staleness deletes something rather than confusing someone, the moment the bare slug is reclaimed for the meta repository (which is exactly what the deferred seed proposes).

**Impact:** Decisive evidence for D-02. It converted the two runnable v1.4 artefacts from "arguably records, keep the diff minimal" into must-repoint, and it is the site the phase's evidence calls out by line number.
**Source:** 192-CONTEXT.md, 192-DISCUSSION-LOG.md, 192-01-SUMMARY.md

---

### The record surface dwarfs the live surface by two orders of magnitude
D-01's enumeration found **948** remaining tracked bare-slug matches across **5074** tracked files, against an edited subset of **10** files.

**Impact:** Retroactively justified the allowlist over a per-file classification pass — a judgement call over ~950 matches was never going to be "simple, not over-engineered." The 938 unrepaired matches are now a recorded decision with a reproducible transcript (two consecutive runs produce identical md5sums) rather than an executor's silence.
**Source:** 192-01-SUMMARY.md, evidence/192-01-enumeration.txt, evidence/192-disposition.md

---

### The gate caught the phase's own self-inflicted defect
Plan 03's Task 3 — the gate D-06 exists to provide — is what found that Task 2's own rewrap had broken a preserved-history anchor.

**Impact:** Fixed in-phase (`3496be22`) rather than shipping a document that would have failed a later byte-level check. The SUMMARY names it as "exactly the failure mode D-06's gate exists to catch," which is the strongest available evidence that the gate was worth its cost.
**Source:** 192-03-SUMMARY.md

---

### A `CONCERNS.md` finding was stale in the opposite direction — the thing it complained about had been fixed
The "CLAUDE.md understates what the repo tracks" finding no longer matched `CLAUDE.md`, which a prior phase had corrected to name `tools/` and `.github/`. What is still wrong is `.gitignore`'s own `skills-lock.json` comment, which still carries the old premise.

**Impact:** The finding was rewritten to record what is actually wrong today rather than deleted or left false — a third disposition beyond "remove outright" and "strip the citation."
**Source:** 192-03-SUMMARY.md

---

### All 37 todo matches were false positives
`todo.match-phase 192` returned 37 items, every one scoring on generic keywords (`firestarter`, `phase`, `planning`, `live`). The list was dominated by firmware defects (`FM1608` byte 0, `CONFIG_VERSION`, VPP checks) and host database questions. Two adjacent-looking items were genuinely unrelated on inspection.

**Impact:** None folded, and the cross-reference was not put to the user — it did not consume a discussion question. A 37-match hit rate of zero is worth knowing before the next phase reads the same signal as meaningful.
**Source:** 192-CONTEXT.md, 192-DISCUSSION-LOG.md

---

### Plan token cost varied ~50× across five plans of similar shape
Actuals: plan 01 — 92,502 tokens / 3 tasks; plan 02 — 12,857 / 2; plan 03 — 17,123 / 3; plan 04 — 1,877 / 2; plan 05 — 4,200 / 2. Durations ran 25 / 45 / 42 / 15 / 20 minutes, which does not track the token spread.

**Impact:** The repo-wide enumeration in plan 01 (5074 files visited) dominated the phase's entire token budget — more than all four other plans combined, at roughly 5× the next largest. Wall-clock is a poor proxy for cost when one plan's work is a full-tree scan.
**Source:** 192-01-SUMMARY.md, 192-02-SUMMARY.md, 192-03-SUMMARY.md, 192-04-SUMMARY.md, 192-05-SUMMARY.md

---

### The verifier found zero gaps on a four-criterion phase, including the declared one
All four ROADMAP criteria verified on independent live re-measurement, and the verifier independently spot-checked the *disclosed gap* too — confirming `origin/main` in `firestarter_app` genuinely has no `tests/` directory, no `[test]` extra and no `ci.yml`.

**Impact:** The D-08 debt is recorded as a verified-accurate declared gap rather than an unexamined claim, which is the difference between a named gap and an excuse.
**Source:** 192-VERIFICATION.md

---

*Phase: 192-live-references-only*
*Extracted: 2026-09-14*
