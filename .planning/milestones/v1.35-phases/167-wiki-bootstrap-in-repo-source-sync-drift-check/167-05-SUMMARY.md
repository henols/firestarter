---
phase: 167-wiki-bootstrap-in-repo-source-sync-drift-check
plan: 05
subsystem: infra
tags: [github-actions, ci, yaml, wiki, drift-check, documentation]

requires:
  - phase: 167-wiki-bootstrap-in-repo-source-sync-drift-check
    provides: "tools/wiki/wiki.py check subcommand and its exit-code contract; tools/wiki/selftest.sh fixture harness (167-03); wiki/Home.md, wiki/How-This-Wiki-Is-Published.md, wiki/_Sidebar.md as the real content the check runs against (167-04)"
provides:
  - ".github/workflows/wiki-check.yml — the repository's second workflow, keyed to beta (D-06), path-filtered to wiki/**, tools/wiki/** and its own filename, with workflow_dispatch and job-level permissions: contents: read; runs offline legs only (wiki.py check, selftest.sh); zero comment lines"
  - "CLAUDE.md and .planning/codebase/STRUCTURE.md corrected: both now name wiki/, tools/wiki/ and the second workflow instead of asserting a stale two-directory tracked set or a single-workflow CI surface"
  - "WIKI-06 re-verified from the live GitHub API (2026-08-30): has_wiki reads false/false/true across firestarter/firestarter_app/firestarter_prom, matching the reading recorded at milestone activation"
affects: [167-06]

tech-stack:
  added: []
  patterns:
    - "own-filename path filter: wiki-check.yml lists itself inside its own paths: trigger, so editing the check re-runs the check — carried forward from catalog-sync-check.yml's one durable idea, without its branches: [main] dormancy defect"
    - "job-level least-privilege permissions block declared even though the repo default is already read — makes the future write-scoped publish job (167-06) unmistakably distinct by contrast"

key-files:
  created:
    - .github/workflows/wiki-check.yml
  modified:
    - CLAUDE.md
    - .planning/codebase/STRUCTURE.md

key-decisions:
  - "Read catalog-sync-check.yml's comment block as a cautionary record only — it documents a check that ran 5 times, failed 5 times, and never once asserted its property because it was keyed to main while the compared paths only ever existed on beta. Took its good ideas (own-filename path filter, workflow_dispatch, actions/checkout@v4, explicit ref resolution shape) and rejected its main trigger outright; wiki-check.yml is keyed to beta from the start."
  - "No setup-python step and no third-party action beyond actions/checkout@v4 — ubuntu-latest ships a python3 new enough for tools/wiki/wiki.py's stdlib-only script, and pinning a Python version here would be the first such pin in the repository for no measured need."
  - "CLAUDE.md and STRUCTURE.md edits were scoped to the exact sentences that became false (tracked-root enumeration, .github/workflows/ tree entry, tools/ tree entry, CI quick-reference row) rather than a re-map; STRUCTURE.md's frontmatter (last_mapped_commit, mapped_paths) was left untouched since this was a targeted factual repair, not a re-run of the codebase mapper."

requirements-completed: [WIKI-06]

coverage:
  - id: D1
    description: ".github/workflows/wiki-check.yml exists as the repo's second workflow, keyed to beta with pull_request + workflow_dispatch, path-filtered to wiki/**, tools/wiki/** and its own filename, declares permissions: contents: read, uses only actions/checkout@v4, contains no fail-open construct, no live-wiki contact, and zero comment lines"
    requirement: WIKI-04
    verification:
      - kind: unit
        ref: "grep suite against .github/workflows/wiki-check.yml — all 14 acceptance-criteria greps (name/job count, beta present, no main line, workflow_dispatch, own-filename + both path globs, contents: read=1/contents: write=0, pull_request_target=0, continue-on-error=0, || true=0, ls-remote=0/publish=0/.wiki.git=0, submodules=0, uses:=1 actions/checkout@v4, comment lines=0) — see Observed Output"
        status: pass
      - kind: unit
        ref: "python3 tools/wiki/wiki.py check (exit 0) && bash tools/wiki/selftest.sh (exit 0, 12/12 cases) — the exact two commands the workflow runs, executed locally in the same order"
        status: pass
    human_judgment: false
  - id: D2
    description: "the existing catalog-sync-check.yml workflow is untouched (git diff empty)"
    requirement: WIKI-04
    verification:
      - kind: unit
        ref: "git diff HEAD -- .github/workflows/catalog-sync-check.yml — empty, both before and after this plan's commits"
        status: pass
    human_judgment: false
  - id: D3
    description: "CLAUDE.md and .planning/codebase/STRUCTURE.md describe the repository truthfully via scoped edits (fewer than 10 / 25 changed lines respectively), no surviving singular-workflow claim, wiki.py check still exits 0"
    requirement: WIKI-05
    verification:
      - kind: unit
        ref: "grep suite — CLAUDE.md: wiki/ >=1, tools/wiki/ >=1; STRUCTURE.md: wiki-check.yml=2, catalog-sync-check.yml=2, tools/wiki=1, 'only workflow'=0; git diff --numstat CLAUDE.md=1+1, STRUCTURE.md=6+3; git status --porcelain .planning/codebase/ lists only STRUCTURE.md; python3 tools/wiki/wiki.py check exits 0 post-edit"
        status: pass
    human_judgment: false
  - id: D4
    description: "WIKI-06 re-verified from the live API: has_wiki reads false on firestarter, false on firestarter_app, true on firestarter_prom, with no setting-mutating API call made"
    requirement: WIKI-06
    verification:
      - kind: manual_procedural
        ref: "gh api repos/henols/{firestarter,firestarter_app,firestarter_prom} --jq .has_wiki, run 2026-08-30 — verbatim output false / false / true; no --method PATCH/PUT/POST or -X used anywhere in this task"
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-08-30
status: complete
---

# Phase 167 Plan 05: Wiki Check CI Workflow and Document Corrections Summary

**Added `.github/workflows/wiki-check.yml` — the repository's second workflow, keyed to `beta` (never `main`) with least-privilege `contents: read`, running only the two offline legs (`wiki.py check`, `selftest.sh`) — corrected `CLAUDE.md` and `STRUCTURE.md` to describe the repo truthfully, and re-verified WIKI-06's `has_wiki` reading from the live GitHub API.**

## Performance

- **Duration:** ~6 min
- **Started:** 2026-08-30T12:34:00Z
- **Completed:** 2026-08-30T12:40:00Z
- **Tasks:** 3
- **Files modified:** 3 (1 created, 2 corrected)

## Accomplishments
- Authored `.github/workflows/wiki-check.yml`: `name: Wiki check`, job `wiki-check`, triggers `pull_request` (`branches: [beta]`, `paths: [wiki/**, tools/wiki/**, .github/workflows/wiki-check.yml]`) plus `workflow_dispatch`, job-level `permissions: contents: read`, steps `actions/checkout@v4` → `Assert wiki source integrity` (`python3 tools/wiki/wiki.py check`) → `Run wiki tooling selftest` (`bash tools/wiki/selftest.sh`) — zero comment lines, zero live-wiki contact, zero fail-open constructs
- Verified `catalog-sync-check.yml` stays byte-identical (`git diff HEAD` empty) throughout
- Corrected `CLAUDE.md` line 12 to enumerate the actually-tracked root paths (`.planning/`, `.claude/`, `tools/`, `.github/`) and to name `wiki/` and `tools/wiki/`
- Corrected three sites in `.planning/codebase/STRUCTURE.md`: the tracked-root enumeration, the `.github/workflows/` tree entry (now lists both workflows, no more "the repo's ONLY workflow" claim), the `tools/` tree entry (adds `tools/wiki/` and `wiki/`), and the CI quick-reference table row
- Re-ran `gh api repos/henols/{firestarter,firestarter_app,firestarter_prom} --jq .has_wiki` and recorded the verbatim reading: `false` / `false` / `true`, matching the reading recorded at v1.35 activation — no setting was changed

## Task Commits

Each task was committed atomically:

1. **Task 1: Create the offline wiki-check workflow** - `1f20b4d6` (feat)
2. **Task 2: Correct CLAUDE.md and STRUCTURE.md so the documents of record are true** - `6d91e338` (docs)
3. **Task 3: Re-verify WIKI-06 from the GitHub API and record the reading** - no commit (a read-back task; this SUMMARY is its only artifact)

## Files Created/Modified
- `.github/workflows/wiki-check.yml` - new; offline-only wiki drift/integrity CI check, keyed to `beta`
- `CLAUDE.md` - line 12 rewritten to name the actual tracked root paths, including `wiki/` and `tools/wiki/`
- `.planning/codebase/STRUCTURE.md` - tracked-root list, `.github/workflows/` tree entry, `tools/`/`wiki/` tree entries, and the CI quick-reference row all corrected

## Decisions Made
- Took `catalog-sync-check.yml`'s good ideas (own-filename path filter, `workflow_dispatch`, `actions/checkout@v4` pin) and explicitly rejected its `branches: [main]` trigger — keyed `wiki-check.yml` to `beta` from the start, per D-06 (`origin/beta` is ~2,842 commits ahead of `origin/main`, so a `main`-keyed check here is dormant in practice, exactly as `catalog-sync-check.yml`'s own comment block documents it ran 5 times and failed 5 times for that reason).
- No `setup-python` step and no third-party action beyond `actions/checkout@v4` — `ubuntu-latest`'s stock `python3` is sufficient for a stdlib-only script, and adding a version pin here would be the repository's first such pin with no measured justification.
- Scoped the `CLAUDE.md`/`STRUCTURE.md` edits to only the sentences and tree entries that had become false, leaving `STRUCTURE.md`'s frontmatter (`last_mapped_commit`, `mapped_paths`) and every other section untouched — this is a factual repair, not a codebase re-map.

## Deviations from Plan

None - plan executed exactly as written. All acceptance-criteria greps and the WIKI-06 API read-back matched the plan's expected values on the first attempt.

## Issues Encountered
None.

## WIKI-06 read-back

Command (run 2026-08-30):
```
for r in firestarter firestarter_app firestarter_prom; do printf '%s: %s\n' "$r" "$(gh api "repos/henols/$r" --jq .has_wiki)"; done
```

Verbatim output:
```
firestarter: false
firestarter_app: false
firestarter_prom: true
```

This matches the expected reading exactly. No repository setting was read via, or changed by, any mutating method (`--method PATCH/PUT/POST`, `-X`) — every call in this task was a plain `gh api ... --jq .has_wiki` GET.

## Phase 167 outstanding

- **WIKI-01 is outstanding.** `https://github.com/henols/firestarter_prom.wiki.git` does not exist. GitHub creates a repository wiki only when the operator saves the first page through the web UI; there is no REST endpoint that creates it, and no command run in this phase (or any prior plan in this phase) has created it.
- **The live halves of WIKI-02, WIKI-03 and WIKI-04 are outstanding**, for the same reason: `wiki.py publish`'s mirror-authority (WIKI-02), idempotence (WIKI-03) and drift-detection (WIKI-04) properties are proven in plan 167-03 only against local `git init --bare` fixtures reached via `--wiki-remote`. None of them has been demonstrated against the real `firestarter_prom.wiki.git` remote, because that remote does not exist yet.
- **The CI wiki-comparison leg is unproven in CI.** `wiki-check.yml`'s two offline steps (`wiki.py check`, `selftest.sh`) have been run and passed locally in this plan, but the workflow itself has not yet executed on a GitHub Actions runner — its first real run happens on the first PR into `beta` that touches `wiki/**`, `tools/wiki/**` or its own file. No live wiki-comparison job exists in this workflow at all; that job is plan 167-06's operator-gated work, wired only after the wiki exists.
- **Whether `secrets.GITHUB_TOKEN` can push to the wiki is unproven and unprovable until the wiki exists.** `tools/wiki/wiki.py publish --push` has never been run against `github.com` in this phase — only against local bare-repository fixtures — so nothing in this phase's evidence base speaks to the wiki-specific auth/permission behavior GitHub Actions tokens have against a repository wiki remote.

None of these four items is reported as resolved, complete, or covered by CI in this SUMMARY.

## Observed Output

`ls .github/workflows/`:
```
catalog-sync-check.yml
wiki-check.yml
```

Acceptance-criteria grep suite against `.github/workflows/wiki-check.yml` (all as required by the plan):
```
name-count: 1
job-count: 1
beta-count: 1
main-line-count: 0
workflow_dispatch-count: 1
own-filename-count: 1
wiki-glob-count: 1
toolswiki-glob-count: 1
contents-read-count: 1
contents-write-count: 0
pull_request_target-count: 0
continue-on-error-count: 0
or-true-count: 0
ls-remote-count: 0
publish-count: 0
wikigit-count: 0
submodules-count: 0
uses-count: 1
uses-line:       - uses: actions/checkout@v4
comment-lines: 0
diff-existing-workflow (line count): 0
```

`python3 tools/wiki/wiki.py check` (run standalone, before and after the CLAUDE.md/STRUCTURE.md edits — identical output both times):
```
OK: _Sidebar.md is fresh (2 entries).
Home -> "Home"
How-This-Wiki-Is-Published -> "How This Wiki Is Published"
OK: 2 pages, all reachable from Home.md, all internal links resolve, all filenames legal.
OK: all offline legs passed (2 legs).
```
Exit code: `0`.

`bash tools/wiki/selftest.sh` (run standalone, same commit as the check above):
```
[... 12 case blocks, each reporting OK for every sub-assertion ...]
case | expected | observed | control | note | verdict
stale_sidebar_exit_1 | 1 | 1 | 0 | a failing --check must not rewrite the file it checks | PASS
sidebar_deterministic | 0 | 0 | 0 | two runs over an unchanged source must be byte-identical | PASS
orphan_exit_1 | 1 | 1 | 0 | orphan absent from Home.md | PASS
sidebar_link_is_not_evidence | 1 | 1 | 0 | home-only evidence | PASS
broken_link_exit_1 | 1 | 1 | 0 | unresolved internal link target | PASS
md_suffix_link_exit_1 | 1 | 1 | 0 | md-suffixed internal link rejected | PASS
illegal_filename_exit_1 | 1 | 1 | 0 | illegal filename character | PASS
wiki_absent_exit_2 | 2 | 2 | 1 | nonexistent remote vs existing bare fixture | PASS
drift_detected_exit_1 | 1 | 1 | 0 | wiki-side edit pushed then dry-run detects drift | PASS
hand_edit_overwritten | 0 | 0 | 0 | wiki-side hand edit and stray page both destroyed by republish | PASS
idempotent_head_unchanged | 0 | 0 | 0 | two pushes with no source change: HEAD identical | PASS
deleted_page_removed | 0 | 0 | 0 | source page deleted then republished; wiki tree matches source exactly | PASS
OK: selftest complete (12 cases)
```
Exit code: `0`.

**`.github/workflows/wiki-check.yml` has not yet executed on a GitHub Actions runner.** Its first real run will be on the first pull request into `beta` that touches `wiki/**`, `tools/wiki/**`, or its own filename (or via a manual `workflow_dispatch`). Everything above is local proof only, run in the same order the workflow specifies.

`git diff --numstat HEAD -- CLAUDE.md`: `1  1  CLAUDE.md`
`git diff --numstat HEAD -- .planning/codebase/STRUCTURE.md`: `6  3  .planning/codebase/STRUCTURE.md`
`git status --porcelain .planning/codebase/`: ` M .planning/codebase/STRUCTURE.md` (only file changed under that directory)

## Pre-existing condition noted, not caused by this plan

`git status --short` shows `M firestarter_app` (submodule commit-pointer drift) and `M .planning/config.json`, both present before this plan's first task and left exactly as found, per the plan's hard rule that `firestarter_app/` is out of scope for this phase.

## User Setup Required
None - no external service configuration required. (WIKI-01's operator action — the one web-UI page save that creates `firestarter_prom.wiki.git` — remains scoped to plan 167-06, not this plan.)

## Next Phase Readiness
- `.github/workflows/wiki-check.yml` is in place and will run automatically on the next PR into `beta` touching its watched paths; no further authoring is needed before 167-06 adds the live-comparison job and `wiki-publish.yml`.
- `CLAUDE.md` and `.planning/codebase/STRUCTURE.md` now describe the repository truthfully as of this plan; no other `.planning/codebase/` document was touched.
- WIKI-06 is now `Complete` — the API re-verification in this plan is its own re-verification, with no dependency on plan 167-06.
- **WIKI-04 and WIKI-05 remain `Pending`** — both still depend on plan 167-06's operator-gated live-wiki demonstration (the CI wiki-comparison job for WIKI-04's live half, and WIKI-05's live navigability check against the real published wiki).
- No blockers for plan 167-06. The wiki content, the offline CI check, and the corrected documents of record are all in place for the operator-gated wave.

## Self-Check: PASSED

- FOUND: .github/workflows/wiki-check.yml
- FOUND: 1f20b4d6
- FOUND: 6d91e338
- FOUND: da056da7

---
*Phase: 167-wiki-bootstrap-in-repo-source-sync-drift-check*
*Completed: 2026-08-30*
