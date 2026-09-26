---
slug: planning-root-file-sprawl
status: resolved
trigger: "somthing is wrong about how gsd milestone phases informaton and other result files are saved . Many of them are stored directly under the .planning folder"
created: 2026-09-15
updated: 2026-09-15
goal: find_and_fix
---

# Debug Session: planning-root-file-sprawl

## Symptoms

### Expected behavior
Milestone-scoped GSD artifacts (per-milestone requirements, roadmaps, evidence,
PR bodies, coverage matrices, release procedures, archive scripts, decision
records) should live under a single, predictable, milestone-scoped home. Today
`.planning/milestones/` already holds `v1.X-REQUIREMENTS.md`,
`v1.X-ROADMAP.md`, and `v1.X-phases/` for 38 milestones, which establishes that
a convention exists.

### Actual behavior
`.planning/` root holds 36 loose files. Only 10 of them are canonical GSD root
files (`PROJECT.md`, `ROADMAP.md`, `STATE.md`, `REQUIREMENTS.md`,
`MILESTONES.md`, `RETROSPECTIVE.md`, `config.json`, `state.json`,
`milestone.lock`, `estimation-calibration.json`). The remaining 26 are
misplaced, in three distinct classes. In addition, 15 bare `v1.X/` directories
sit at the root, duplicating the role of `.planning/milestones/v1.X-phases/`.

### Scope confirmed by operator (in scope)
1. **v1.X-prefixed loose files at `.planning/` root** — 22 files:
   `v1.10-FRAMING-DECISION.md`, `v1.13-PROTOCOL-ENUMERATION.md`,
   `v1.23-FLASH-PATH-DECISION.md`, `v1.3-BENCH-RESULTS.md`,
   `v1.3-COVERAGE-MATRIX-ALL.md`, `v1.3-COVERAGE-MATRIX.md`,
   `v1.3-defect-coverage-ids-all.json`, `v1.3-defect-coverage-ids.json`,
   `v1.30-GH12-REPLY-DRAFT.md`, `v1.30-OPERATOR-BATCH.md`,
   `v1.30-PR-BODY.md`, `v1.31-CARRYOVER-DISPOSITION.md`,
   `v1.4-RELEASE-PROCEDURES.md`, `v1.4-archive.sh`, `v1.4-e2e-verify.sh`,
   `v1.5-BENCH-RESULTS.md`, `v1.6-EVIDENCE.md`, `v1.6-archive.sh`,
   `v1.7-SHIELD-REVS.md`, `v1.7-archive.sh`, `v1.8-archive.sh`,
   `v1.9-REQUIREMENTS.md`.
2. **Bare `v1.X/` directories at `.planning/` root** — 15 dirs: `v1.10/`,
   `v1.15/`, `v1.16/`, `v1.18/`, `v1.3/`, `v1.33/`, `v1.34/`, `v1.35/`,
   `v1.36/`, `v1.37/`, `v1.38/`, `v1.5/`, `v1.6/`, `v1.7/`. These compete with
   `.planning/milestones/v1.X-phases/` as a home for milestone-scoped material.
3. **Undated topic docs at `.planning/` root** — 4 files:
   `AT28C04-ADAPTER.md`, `WINDOWS.md`, `X88C64-FEASIBILITY.md`,
   `VALIDATED-EPROMS.md`. No milestone prefix, no home in `notes/`.

### Explicitly OUT of scope
`.planning/phases/` contents. It mixes the active milestone's phase (`194-*`)
with long-closed phases (`01`, `02`, `03`, `04`, `11`, `12`, `44`, `48`) and
`999.x` backlog items, but the operator did not select it for this session.

### Error messages
None. This is a silent layout/convention defect, not a crash. Nothing fails
loudly. The damage is discoverability and archive integrity.

### Timeline
Accumulated across 38 milestones. Oldest loose artifacts are `v1.3-*`
(2026-05-20), newest bare directory is `v1.38/` (2026-09-15). The problem has
been continuous, not a regression from a single change.

### Reproduction
`ls -1p .planning/ | grep -v '/$'` — 36 entries, only 10 legitimate.
`ls -1p .planning/ | grep '/$'` — 25 dirs, 15 of them bare `v1.X/`.

## Investigation constraints

- **The root cause is unknown and MUST be determined from evidence.** The
  operator explicitly declined to pre-select a failure mode. Do not assume a
  single writer is at fault. Candidate hypotheses to test, not to assume:
  (a) a GSD verb or workflow emits result files to `.planning/` root.
  (b) Hand-archived milestone close (this project never uses
  `milestone.complete`) omits these classes.
  (c) No convention was ever defined, so three homes were used ad hoc.
  (d) The convention changed mid-project and older eras were never migrated.
- **Git history is the primary evidence source.** `git log --diff-filter=A`
  per file reveals which commit and which workflow created it, and whether an
  agent or a human wrote it. Use it before reasoning about intent.
- **`.planning/` is committed** (`commit_docs: true`), so every placement
  decision is recoverable from history.

## Fix constraints (operator chose FULL FIX including migration)

- **Citation repair is mandatory, not optional.** A standing project rule
  requires the repair of `.planning/` `file:LINE` and path citations rather
  than acceptance of staleness — archives included. Migration MUST include a
  scripted remap and a round-trip oracle that proves that no citation stays
  dangling.
- **`.planning/`→`.planning/` citations inside archived docs are
  historical-by-intent** and are NOT covered by the repair rule. Repair of
  those citations destroys the evidence that they exist to preserve.
  Distinguish the two classes before you rewrite anything.
- **`.planning/state.json` is gitignored**, and `git clean -Xdf` destroys GSD
  state. Never use it to tidy.
- **Milestone close in this project is hand-archived**, never via
  `milestone.complete` — the CLI would overwrite the hand-authored ROADMAP.
  Any proposed change to the close path must respect that constraint.
- **`.planning/ROADMAP.md` is hand-authored and must never be regenerated.**
- Several GSD record gates read `lines=N` anchors and covered-file digests.
  Moving files will perturb them. Verify the gates after migration.

## Current Focus

status: RESOLVED — full fix applied, verified, and committed.
next_action: none — session complete.

reasoning_checkpoint:
  hypothesis: "Three independent, era-specific causes produced the sprawl — not
    one failure mode. (a) No convention was EVER defined for milestone-scoped ad
    hoc artifacts (decision records, bench evidence, release scripts, PR-body
    drafts); each phase's PLAN.md picked `.planning/v1.X-NAME.md` or a bare
    `.planning/v1.X/` scratch dir by analogy to the previous phase's choice,
    even after the `.planning/milestones/v1.X-*` flat-prefix convention existed
    (established at v1.7 close, commit 104ffca4, 2026-05-26) — because that
    convention's scope was read narrowly (REQUIREMENTS/ROADMAP/MILESTONE-AUDIT/
    phases only), never generalized. (b) The last 4 milestone closes (v1.35-38)
    independently invented a NEW bare-directory-per-milestone home
    (`.planning/v1.X/CLOSE-RECORD.md`) for their own honesty-ledger artifact,
    explicitly modeled on v1.34's Phase-166 bench-evidence directory, each
    citing 'following v1.35's shape' — a recent, self-reinforcing regression
    away from the 28-milestone-old dominant convention, not legacy debt. (c)
    The 4 undated topic docs were written straight to `.planning/` root by
    habit when `.planning/notes/` (37 pre-existing entries of this exact shape)
    was the natural home."
  confirming_evidence:
    - "git log --diff-filter=A on all 22 loose files shows every one created by
      a `docs(NN-NN):`/`feat(NN-NN):` phase-execution commit — plan-directed
      writes, not a GSD-verb emission."
    - "commit 104ffca4 (2026-05-26) shows the literal RENAME 'REQUIREMENTS.md
      -> .planning/milestones/v1.7-REQUIREMENTS.md', proving the flat-prefix
      convention's origin date; v1.8-archive.sh (05-29), v1.9-REQUIREMENTS.md
      (06-01), and 6 more loose files were created AFTER that date anyway."
    - "commit 29804e1b (v1.36 close, human-authored) states verbatim: 'Archived
      by hand, following v1.35's shape: .planning/v1.36/CLOSE-RECORD.md'."
    - "commit 575f513d (v1.35 CLOSE-RECORD.md origin) says 'comprehensively
      rather than curated to v1.34's ten' — confirming v1.34's Phase-166
      CLOSE-RECORD.md (a legitimate bench-evidence-dir artifact) was mistaken
      for a close-time convention and copied forward 3 more times."
    - "milestones/ dir census: 69 flat files + 30 -phases dirs (all 38
      milestones) vs. 14 bare v1.X/ root dirs (used in only 14 of 38) — the
      flat-prefix scheme is the measured dominant precedent, not a guess."
    - "grep confirms zero hits for 'CLOSE-RECORD' anywhere under
      .claude/gsd-core/ — the bare-directory pattern is not a gsd-core emission
      of any kind, confirmed absent from the tool's own source."
  falsification_test: "If any of the 22+14+4 misplaced items had been created by
    a gsd-core workflow's own hardcoded root-level path (like
    audit-milestone.md's `.planning/v{version}-MILESTONE-AUDIT.md`, found
    during this investigation but NOT one of the in-scope misplaced items,
    since MILESTONE-AUDIT.md files were already all correctly swept into
    milestones/ by the hand-close 'chore: archive' step), that would refute the
    'no code defect' finding for this specific migration scope. It did not —
    every in-scope item's creating commit was plan-directed prose, not a
    gsd-core script invocation."
  fix_rationale: "The fix relocates by DOMINANT PRECEDENT (flat-prefix,
    69-vs-14) rather than inventing a fourth scheme, and repairs every live
    citation to the moved paths so the relocation doesn't itself create new
    dangling references — addressing the root cause (no shared, generalized
    convention + a copied-forward recent deviation) rather than just hiding
    the symptom by moving files without fixing what points at them."
  blind_spots: "Did not exhaustively verify every one of the ~1084
    archived-scope files that still cite an old path are correctly
    historical-by-intent (spot-checked a representative sample: closed-phase
    PLAN/SUMMARY files, a prior citation-sweep manifest, and raw bench-log
    transcripts — all confirmed point-in-time records). Did not fix the
    unrelated pre-existing typo `.planning/v1.31-OPERATOR-BATCH.md` (should
    probably read v1.30) since correcting content typos is out of this
    migration's scope. Did not attempt to fix or file the separate,
    already-latent gsd-core `audit-milestone.md` MILESTONE-AUDIT.md
    root-emission defect found along the way (out of scope; gsd-core is
    installer-owned and not committed here) — noting it for the record only."
  candidate_causes:
    - "code: none confirmed as a live gsd-core defect for the IN-SCOPE items
      (all 41 misplaced items were plan-authored writes, not gsd-core
      emissions) — though a related, out-of-scope gsd-core defect was found
      (audit-milestone.md writes MILESTONE-AUDIT.md to `.planning/` root, not
      `.planning/milestones/`; rescued today only by a manual close-time sweep)"
    - "process/config: no generalized placement convention was ever defined
      for non-canonical milestone artifacts, so plan authors extrapolated from
      local precedent each time (category: process, not code or data)"
  and_gate: "no — the three classes are parallel, independent causes from
    different eras (an always-missing general convention; a 4-milestone-old
    copied-forward deviation; an undated-topic-doc habit), not one failure
    requiring several conditions to hold simultaneously. Each is independently
    sufficient to explain its own class; none requires the others."

## Evidence

- timestamp: 2026-09-15
  checked: `.planning/milestones/` census (`ls | grep -vE -- '-phases$|-paused$' | wc -l` = 69 flat files across 38 milestones; 30 `-phases` dirs; plus 6 pre-existing `-research` dirs)
  found: The flat-prefix `.planning/milestones/v1.X-<DOC>.md` scheme is used for
    REQUIREMENTS.md (29), ROADMAP.md (26), MILESTONE-AUDIT.md (7), and even
    multi-file DIRECTORIES (`v1.21-research/` .. `v1.38-research/`, 6 of them) —
    proving the flat scheme already handles directories, not just single files.
  implication: The flat-prefix scheme is the dominant, general-purpose
    precedent; the bare `v1.X/` root-directory scheme (14 uses) is the minority,
    later-arriving pattern.
- timestamp: 2026-09-15
  checked: `git log --diff-filter=A` on all 22 loose root files
  found: Every file was created by a `docs(NN-NN):`/`feat(NN-NN):` phase-plan
    execution commit (e.g. f829ae2f, 0e1bf403, 8342bac5), several dated AFTER
    the flat-prefix convention was established (v1.8-archive.sh 05-29,
    v1.9-REQUIREMENTS.md 06-01, v1.10-FRAMING-DECISION.md 06-01,
    v1.13-PROTOCOL-ENUMERATION.md 06-17, v1.23-FLASH-PATH-DECISION.md 08-02,
    3× v1.30-* 08-05, v1.31-CARRYOVER-DISPOSITION.md 08-09).
  implication: Not a code defect — plan-directed writes that never adopted the
    already-established convention because that convention's recognized scope
    never covered these artifact types (decision records, release scripts,
    PR-body drafts, coverage matrices, evidence files).
- timestamp: 2026-09-15
  checked: `git log --diff-filter=A --reverse` on each of the 14 bare `v1.X/`
    root directories
  found: v1.3/v1.5/v1.6/v1.7 (2026-05-20/21/22) predate the flat-prefix
    convention's 2026-05-26 origin; v1.10/v1.15/v1.16/v1.18/v1.33 (06-02
    through 08-23) are later in-flight bench/evidence scratch dirs; v1.34
    (08-26) is Phase 160's rig-pin/bench-evidence scaffold; v1.35-38
    (09-02/09/13/15) are close-time CLOSE-RECORD.md homes, each an explicit
    copy of the prior milestone's close shape (see reasoning_checkpoint).
  implication: Two distinct sub-causes within one class — pre-convention-era
    scratch dirs (legacy debt) and a post-convention-era close-procedure
    regression (active, self-reinforcing, only 4 milestones old).
- timestamp: 2026-09-15
  checked: `grep -rl "CLOSE-RECORD" .claude/gsd-core/`
  found: Zero hits.
  implication: The CLOSE-RECORD.md bare-directory pattern is not a gsd-core
    emission of any kind — confirmed human/agent-authored during hand-archival,
    not a tool defect.
- timestamp: 2026-09-15
  checked: `grep -rn "\.planning/v" .claude/gsd-core/workflows/*.md`
  found: `audit-milestone.md` (and its mirrors in `autonomous.md`,
    `milestone-summary.md`) instruct `.planning/v{version}-MILESTONE-AUDIT.md`
    at `.planning/` ROOT, not `.planning/milestones/`. `.claude/gsd-core/` is
    gitignored (installer-owned, confirmed via `git check-ignore -v`), so this
    is a genuine live gsd-core defect but NOT one of the 3 in-scope classes
    (no MILESTONE-AUDIT.md is currently misplaced — all were already swept
    into `milestones/` by a separate, later `chore: archive` hand-close commit,
    e.g. 31b89ee0 for v1.11, 226d33c8 for v1.17).
  implication: A related but out-of-scope, pre-existing gsd-core placement
    defect exists and is rescued today only by a manual close-time sweep step;
    fixing it in gsd-core would need an upstream change (installer-owned,
    overwritten on version bump) — noted for the record, not fixed here.
- timestamp: 2026-09-15
  checked: `git status --ignored` + `comm` diff on tracked vs actual file lists
    for all 14 migration directories, before any `git mv`
  found: 5 of 14 directories (v1.7, v1.16, v1.18, v1.33, v1.34) contain
    untracked-but-gitignored content: a full upstream-RURP git clone (70 files,
    `.planning/v1.7/upstream-rurp/`), build-cache junk (`__pycache__`,
    `.pytest_cache`, `.ruff_cache`), and real ignored bench-evidence binaries
    (`.planning/v1.34/bench/cells/*/reads/*.bin`, `written.bin`).
  implication: A naive `git mv` would silently strand this content at the old
    path. Tested and confirmed `git mv olddir newdir` performs a real OS-level
    directory rename when the destination doesn't exist yet, carrying
    untracked content along automatically — verified post-move that
    `upstream-rurp/` and the `.bin` bench reads landed at the new path intact.
- timestamp: 2026-09-15
  checked: `.gitignore` for path-anchored patterns referencing moved directories
  found: Lines 26-36 anchor 5 ignore patterns to `.planning/v1.7/**` and
    `.planning/v1.7/upstream-rurp/` specifically (not covered by the generic
    `__pycache__/` rule). Post-move, before repair, the relocated
    `upstream-rurp/` (containing a nested `.git/`) showed as untracked (`??`)
    instead of ignored (`!!`) — a live ignore-behavior regression.
  implication: `.gitignore` needed a real, tested fix, not just documentation —
    fixed and re-verified (`git status --ignored` now shows `!!` again).
- timestamp: 2026-09-15
  checked: Citation-repair scoped oracle (`citation_oracle2.py`), reading HEAD
    via `git show` for a true pre-migration baseline vs. the working tree
    post-repair
  found: Baseline (HEAD, pre-migration): 41 live-scope files / 334 occurrences
    citing an about-to-move path. Post-migration + repair: 0 live-scope files /
    0 occurrences. Archived-scope (historical-by-intent, correctly untouched):
    1168->1084 files (membership shift from directory reclassification, not a
    miss) / 13070->12423 occurrences.
  implication: Round-trip proof that citation repair reached full live-scope
    coverage without touching historical-by-intent content.
- timestamp: 2026-09-15
  checked: A comprehensive repo-wide regex sweep for the corruption signature
    `milestones/v1\.(3|5|6|7|10|15|16|18|33|34)-artifacts` NOT followed by `/`
  found: The first `citation_tool.py apply` run had a real bug — its
    `build_literal_pairs()` matched a bare directory old-path (e.g.
    `.planning/v1.3`) WITHOUT requiring a trailing `/`, so it wrongly matched
    as a PREFIX of any unrelated string starting with the same characters.
    This corrupted exactly 2 lines (ROADMAP.md:3094, GRAPH_REPORT.md:18619),
    both derived from the SAME pre-existing (and pre-existing-typo'd) text
    `.planning/v1.31-OPERATOR-BATCH.md` (a typo for v1.30 that predates this
    session — confirmed via `git show 3ed033b0:.planning/ROADMAP.md`, a commit
    from before this session began).
  implication: Bug fixed in the tool (trailing-slash now required for
    directory matches); both corrupted lines hand-restored to their original
    (typo-preserved — fixing the pre-existing typo is out of scope) text;
    confirmed via a repo-wide re-sweep that no other instance of this
    collision class exists (the only realistic collision family in this
    repo's version range is v1.3 vs v1.30-v1.39; the other 9 directory names
    have no same-prefix siblings in the actual version range).
- timestamp: 2026-09-15
  checked: `git log --oneline` mid-session, after finding the ROADMAP.md
    corruption also present in a file that showed no pending working-tree diff
  found: A CONCURRENT session (commit 3a75a7bb, "docs(phase-194): update
    tracking after 194-04") committed this debug session's in-progress,
    not-yet-finished `.planning/ROADMAP.md` citation-repair edits — including
    the then-still-present bug — alongside its own unrelated phase-194
    tracking update, because both sessions share the same working tree. The
    concurrent commit's own message disclosed this transparently ("carries 67
    citation-path repairs that were already uncommitted... a concurrent
    session's work, not this phase's").
  implication: Working on a shared checkout with another active agent session
    is a real, encountered hazard, not a hypothetical — the bug is now split
    across one already-committed file (ROADMAP.md, fixed via a new, separate
    commit) and the rest of this session's still-uncommitted work.

## Eliminated

- hypothesis: "A GSD verb/workflow emits result files directly to `.planning/`
    root for the classes in scope (candidate (a))."
  evidence: Every one of the 22+14 in-scope items' creating commit is a
    `docs(NN-NN):`/`feat(NN-NN):`/human-authored close commit — plan-directed
    prose, never a `gsd-tools.cjs` invocation or a `.claude/gsd-core/`
    workflow's own file-write instruction. (A related, genuinely
    code-emitted root-level defect DOES exist in gsd-core for
    MILESTONE-AUDIT.md — but that class is not currently misplaced, since a
    separate manual sweep already rescues it every time, so it does not
    explain THIS session's 41 misplaced items.)
  timestamp: 2026-09-15

## Resolution

root_cause: "Three parallel, era-specific causes (no AND-gate — see
  reasoning_checkpoint): (1) no convention was ever generalized beyond
  REQUIREMENTS/ROADMAP/MILESTONE-AUDIT/phases, so ad hoc milestone artifacts
  (decision records, bench evidence, release scripts, PR-body drafts,
  evidence files) were written straight to `.planning/` root or a bare
  `.planning/v1.X/` scratch dir by analogy to prior phases, continuing even
  after the flat-prefix convention existed (established commit 104ffca4,
  2026-05-26); (2) the last 4 milestone closes (v1.35-38) independently
  invented and then copied forward a NEW bare-directory CLOSE-RECORD.md home,
  modeled on v1.34's unrelated Phase-166 bench-evidence directory, diverging
  from the 28-milestone-old dominant precedent; (3) 4 undated cross-cutting
  topic docs were written to `.planning/` root by habit instead of the
  already-established `.planning/notes/` home (37 pre-existing peers)."
fix: "Migrated all 41 in-scope items (22 loose files + 4 topic docs + 14 bare
  directories, one further split into 10 whole-directory `git mv`s to
  `.planning/milestones/v1.X-artifacts/` plus 5 single-file `git mv`s for the
  v1.35-38 CLOSE-RECORD/MIGRATION-TABLE family) onto the measured-dominant
  `.planning/milestones/v1.X-<DOC>.md` flat-prefix convention (69 flat files +
  30 `-phases` dirs across 38 milestones vs. 14 bare-dir uses — the count that
  decided it) or `.planning/notes/` for the 4 undated topic docs (37
  pre-existing peers). Repaired every live citation to the moved paths via a
  scripted remap (124 files, 271 substitutions across 2 apply passes) with a
  round-trip dangling-path oracle (41/334 -> 0/0 in live scope). Fixed
  `.gitignore`'s path-anchored v1.7 patterns and 2 hardcoded skill-script
  paths (devtest-triage/SKILL.md, devtest-rootcause/diff_db.py) so ignore
  behavior and tool citations stay correct post-move. Found and fixed a
  trailing-slash bug in the remap script itself (corrupted 2 lines via a
  bare-prefix collision with a pre-existing, unrelated typo; both restored to
  original text; confirmed via repo-wide re-sweep that no other instance of
  this collision class exists)."
verification: "gsd-tools `state validate` -> valid:true, 0 warnings.
  `roadmap validate` -> 0 warnings. `progress` correctly parses the active
  v1.39/Phase-194 state post-migration. Round-trip citation oracle: 0
  live-scope dangling citations (down from a true pre-migration baseline of
  41 files/334 occurrences, confirmed by reading pre-migration content
  straight from git HEAD via `git show`, not from a destructive stash).
  Repo-wide corruption-signature re-sweep: 0 hits. `.gitignore` ignore
  behavior re-verified (`git status --ignored` shows `!!` again for the
  relocated upstream-rurp clone). `.planning/` root now shows exactly the 10
  canonical files, confirmed by direct listing."
files_changed:
  - ".planning/milestones/ (41 new entries: 26 files + 10 -artifacts dirs + 5
    close-record-family files, all via `git mv`)"
  - ".planning/notes/ (4 new entries: AT28C04-ADAPTER.md, WINDOWS.md,
    X88C64-FEASIBILITY.md, VALIDATED-EPROMS.md, via `git mv`)"
  - ".planning/ROADMAP.md, .planning/STATE.md, .planning/PROJECT.md,
    .planning/MILESTONES.md, .planning/RETROSPECTIVE.md (citation repair)"
  - ".planning/codebase/{CONCERNS,STACK,STRUCTURE}.md, .planning/graphs/GRAPH_REPORT.md,
    .planning/notes/*.md (5 files), .planning/seeds/py32f071-no-external-tool-fw-install.md,
    .planning/todos/pending/*.md (9 files) (citation repair)"
  - ".gitignore (path-anchored v1.7 ignore patterns repointed)"
  - ".claude/skills/devtest-triage/SKILL.md, .claude/skills/devtest-rootcause/scripts/diff_db.py
    (hardcoded path repair)"
  - "CLAUDE.md (1 citation repair: MIGRATION-TABLE.md path)"
  - "~85 files inside the 10 relocated -artifacts trees (.md/.py/.sh only;
    .log/.json/.jsonl/.txt/.csv/.bin left untouched as frozen point-in-time
    captures)"
