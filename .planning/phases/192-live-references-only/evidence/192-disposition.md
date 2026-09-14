# Phase 192 disposition record

Every reference a reader could act on today in any of the three repositories addresses
`henols/firestarter_fw`, and every reference that records history still says what it said
when it was written. This record is the phase's answer to the ROADMAP's four success
criteria, one section each, every claim citing the evidence file and the reading that
supports it rather than restating a conclusion. It closes with a section naming, plainly,
what this phase did not do.

## Criterion 1

**No live tracked file in any of the three repositories addresses `henols/firestarter` as
the firmware repository — swept with `/usr/bin/grep`, not PATH `grep`, which is ugrep here
and honours `.gitignore`.**

- **Meta repository, the two edited runnable surfaces:** `evidence/192-slug-sweep.txt`
  records `reading_1_total: 0` for `README.md` (`/usr/bin/grep -cE
  'henols/firestarter($|[^_A-Za-z0-9])'`), paired with `reading_2_control_total: 5` over the
  same file (`henols/firestarter_(app|prom|fw)`) — a non-vacuity control, and a live
  `gh api repos/henols/firestarter_fw --jq '.full_name'` reading confirming the repointed
  URL resolves to the repository's own identity, not a redirect target. The two runnable
  v1.4 artefacts (`.planning/v1.4-e2e-verify.sh`, `.planning/v1.4-RELEASE-PROCEDURES.md`) were
  repointed at all 13 bare-slug sites, per `192-01-SUMMARY.md`.
- **Meta repository, the enumerated remainder:** `evidence/192-01-enumeration.txt` records
  `tracked_files_visited: 5074`, `reading_1_total: 948` (every remaining tracked bare-slug
  match), paired with `reading_2_control_total: 1595` (non-vacuity control, non-zero), and
  `edited_subset: 10` naming exactly the ten files this phase edits. The 938 matches outside
  the edited subset are records under D-01's allowlist rule — a `.planning/` file that names
  the old slug records what the repository was called when it was written, and repairing it
  destroys that evidence — not live references a reader could act on today.
- **The seven `.planning/codebase/` documents:** `evidence/192-03-codebase-gate.txt` records
  a `bare_slug: 0` reading for all seven documents (`ARCHITECTURE.md`, `CONCERNS.md`,
  `CONVENTIONS.md`, `INTEGRATIONS.md`, `STACK.md`, `STRUCTURE.md`, `TESTING.md`), each paired
  with a non-zero `control_extended_slug:` reading (5 to 32 depending on the document), plus
  an independent live re-reading over the same seven-file list — taken separately from the
  per-document table — confirming 0 survivors and 7/7 non-vacuity control matches.
- **Both sub-repositories:** `evidence/192-04-subrepo-reverify.txt` records
  `fw_bare_slug_matches: 0` paired with `fw_control_prom_matches: 4`, and
  `app_bare_slug_matches: 0` paired with `app_control_prom_matches: 8` — both readings taken
  live on the `v1.38-repository-rename` branch of each sub-repository, matching Phase 189's
  and Phase 190's own prior measurements of the same pairing, with both sub-repositories'
  `git status --porcelain` confirmed clean (nothing was written to either by this phase).

Every zero cited above is paired with a non-zero control, so none is a vacuous reading of an
empty or misdirected scan.

## Criterion 2

**`git diff --stat -- .planning/milestones/` over the milestone's whole range is empty. D-5
is proved, not asserted.**

`evidence/192-05-milestones-untouched.txt` records `range_base: f0307ac811f65490fb8745bb4f9`
`1bdb1c2b8162a`, recomputed live via `git merge-base beta HEAD` after all four prior plans
had landed (D-09) rather than reused from the discussion-time measurement, and independently
proved to be an ancestor of HEAD (`ancestor_rc: 0`) before anything was built on it. Over
that range, `milestones_diff_lines: 0` and `milestones_commits: 0`, each paired with a
non-zero control: `control_sibling_path_commits: 61` (the same range and command form over
the sibling directory `.planning/phases/`, where this milestone's own work lives) and
`control_pathspec_tracked_files: 3440` (the pathspec resolves to real tracked files, not to
nothing). A closing `git status --porcelain -- .planning/milestones/` reading printed no
path, so the property holds in the working tree and index as well as across the committed
range. No plan in this phase named a `.planning/milestones/` path in its `files_modified`,
and every task in every plan carried a scoped porcelain leg over that path before this final
reading was taken.

## Criterion 3

**`.planning/codebase/STACK.md` no longer describes a catalog-sync workflow checking out the
sub-repos via `actions/checkout` — no such workflow exists, and the meta repository has no
workflows at all.**

Every remap this criterion rests on was captured before it ran: `evidence/192-02-preserved-history.txt`
recorded `STACK.md`'s pre-remap preserved-history anchors (its `Prior analysis: 2026-05-08` line
and its `Part 2 — Submodule stacks` heading) against a named `pre_remap_commit` SHA, before the
`/gsd-map-codebase` remap touched the document, so a dropped preserved section would show up as a
diff rather than as a memory exercise. `evidence/192-03-codebase-gate.txt` records `STACK.md`'s
`retired_ci_tokens: 0`
(`/usr/bin/grep -cE 'catalog-sync-check|wiki-check|wiki-publish|tools/wiki'`), paired with
`control_extended_slug: 10` proving the file is non-trivially populated, and states the
`criterion_3:` verdict directly: "`STACK.md`'s retired_ci_tokens reading is 0; the workflow's
frontmatter/prose does not appear anywhere in the document ... `STACK.md` was remapped in
plan 02 (`192-02-SUMMARY.md`), which removed the retired CI section outright, and this task's
independent re-reading re-confirms it stayed removed." `STACK.md`'s preserved 2026-05-08
`Part 2 — Submodule stacks` section survived the remap verbatim (`preserved_anchor: present`
in the same transcript).

## Criterion 4

**The four other `.planning/codebase/` documents (`STRUCTURE.md`, `INTEGRATIONS.md`,
`ARCHITECTURE.md`, `TESTING.md`) agree with the renamed reality.**

`evidence/192-03-codebase-gate.txt` records `bare_slug: 0` and `retired_ci_tokens: 0` for all
four documents, each paired with a non-zero `control_extended_slug:` reading (`STRUCTURE.md`
18, `INTEGRATIONS.md` 5, `ARCHITECTURE.md` 15, `TESTING.md` 9), and states the `criterion_4:`
verdict directly: "All four read 0 for both the bare slug and the retired-CI token set, each
paired with a non-zero control, and each still carries its preserved 2026-05-08 section
verbatim ... `STRUCTURE.md`'s tree no longer lists `.github/workflows/` or `tools/wiki/` as
tracked (`192-02-SUMMARY.md`); `TESTING.md`'s meta-repository half ... now states plainly that
no `.github/workflows/` directory exists and therefore no automated check of any kind runs in
this repo." All four preserved-anchor readings in the same transcript read `present`.

## What this phase did not do

**First — the regression-guard debt, stated plainly rather than omitted (D-08).** After this
phase, **nothing watches any of the three repositories for slug regression.** No standing
guard, workflow or lint rule was added by this phase, and none of SWEEP-01, SWEEP-02 or
SWEEP-03 asks for one. The meta repository has no `.github/workflows/` directory at all to
host such a guard; source-scanning gates in this project have a documented history of
failing open after renames, which is the load-bearing reason a guard was declined rather than
built; and a guard that cannot fail is worse evidence than a named gap. This includes
`origin/main` in the host repository, `firestarter_app`, which has no `tests/` directory, no
`[test]` extra in `pyproject.toml`, and no `ci.yml` — a pin test asserting the corrected slug
stays corrected would have nowhere to live and nothing to run it. Phases 189, 190 and 191
each declined a guard in turn and named this phase as where the boundary-aware pattern would
be built (189 D-10, 190 D-05, 191 D-02); this phase closes that chain **by declaration rather
than by construction** — a reader must be able to see that this was chosen, not overlooked.

**Second — the currency of the two runnable v1.4 artefacts.** `.planning/v1.4-e2e-verify.sh`
and `.planning/v1.4-RELEASE-PROCEDURES.md` had their repository URLs repointed at all 13
bare-slug sites (`192-01-SUMMARY.md`; `evidence/192-slug-sweep.txt`). Nothing else about them
was touched, and this phase makes no claim that the v1.4 release procedure is still correct
— re-validating either artefact's own currency is separate, unclaimed work.

**Third — D-01's allowlist boundary: the records this phase deliberately left alone.**
`evidence/192-01-enumeration.txt` enumerates 948 remaining tracked bare-slug matches, of
which 938 lie outside this phase's ten-file edited subset. Every one of those 938 is a
`.planning/` record — a phase summary, a context file, a note, a seed, a todo, an archived
milestone entry — and D-01's rule is that such a record names what the repository was called
when it was written; repairing it would destroy that evidence rather than correct anything a
reader could act on today. `.planning/PROJECT.md` is a named example of the same principle:
its two matching lines are historical (a run-log URL that now resolves only through the
rename redirect, and a sentence describing the destructive act of claiming the old slug as a
backlog item) and neither is edited.

**Fourth — D-04's accepted narrowing: `tools/` was outside the remap scope.** The
`/gsd-map-codebase` remap this phase ran (`192-02-SUMMARY.md`, `192-03-SUMMARY.md`) was scoped
to `.claude,.devcontainer,.github,.gitignore,.gitmodules,.vscode,CLAUDE.md` — `tools/` was
never in scope, by decision, not by oversight. As a direct consequence, `STRUCTURE.md`'s
previously-stale `tools/wiki/` claim **died by omission rather than by correction**: the
regenerated document simply no longer mentions `tools/wiki/` at all (confirmed by
`evidence/192-03-codebase-gate.txt`'s `retired_ci_tokens: 0` reading for `STRUCTURE.md`), and
none of the seven regenerated documents says anything about `tools/catalog/`, which does
exist as a tracked directory in this repository today. This satisfies criterion 4 as written,
and is recorded here as an accepted narrowing rather than a gap a later reader would have to
discover on their own.
