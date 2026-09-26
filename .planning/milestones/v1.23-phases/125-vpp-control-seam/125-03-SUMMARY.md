---
phase: 125-vpp-control-seam
plan: 03
subsystem: firmware
tags: [pytest, git, ancestry-proof, non-regression-gate, pr45, vpp]

# Dependency graph
requires:
  - phase: 125-vpp-control-seam
    provides: "125-01's hand-authored include/rurp_vpp.h + src/rurp_vpp.cpp seam, at HEAD 9c11f63 when this plan started (later commits: 27b2f17, 2b5e8c8)"
provides:
  - "firestarter/tests/test_pr45_non_ancestry.py -- 4 test functions / 4 collected cases discharging ROADMAP Criterion 1: none of PR #45's ten commits is an ancestor of the integration branch's HEAD, proven by an exit code; plus content-divergence corroboration on the two seam files' blob hashes"
  - "pytest tests/ moved 82 -> 84 (Task 1) -> 86 (Task 2), verified at each step"
affects: [125-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "HEAD-scoped ancestry proof via git subprocess, three-bucket exit-code classification (0=ancestor/violation, 1=clean, anything else=tool-error), never a negated single call and never --all-scoped"
    - "Never-vacuous guard runs BEFORE any ancestry question: list-length assertion, distinctness assertion, then per-object existence check (git cat-file -e <sha>^{commit}), each a real assertion not a precondition-only check"

key-files:
  created:
    - firestarter/tests/test_pr45_non_ancestry.py
  modified: []

key-decisions:
  - "Landed as tests/test_pr45_non_ancestry.py, a pytest, never scripts/check_*.py -- RESEARCH C-11 planted the scripts/ shape and measured it costs four extra artifacts (checker + paired test module + planted fixture + two floor bumps in tests/test_checker_convention.py). The tests/ shape is invisible to that checker's non-recursive scripts/ glob and costs zero."
  - "Split into two commits matching the plan's two-task structure, even though the whole module was authored as one design: Task 1 commit contains only Coverage 1+2 (never-vacuous guard + HEAD-scoped ancestry), verified at 2 passed / 84 in tests/ before committing; Task 2 commit adds Coverage 3+4 (blob divergence + self-enforcement), verified at 4 passed / 86 before committing. Each task's acceptance criteria specify an exact count 'at this task's end', so the single-shot draft was decomposed into the two commits the plan calls for."
  - "Requirement ticking scope: NONE. VPP-01 appears in this plan's frontmatter as the requirement this plan's proof discharges evidence toward, but per the phase's explicit guard (Phase-116 premature-tick pattern) no requirement checkbox in .planning/REQUIREMENTS.md was ticked. Only Plan 125-06 may tick VPP-01/02/03."

requirements-completed: []  # Deliberately empty -- this plan authors half of VPP-01's proof (the non-ancestry half) but does not discharge the requirement checkbox; only 125-06 ticks it.

coverage:
  - id: D1
    description: "Never-vacuous guard: the module-level 10-SHA tuple is exactly 10 entries, all distinct, and each commit object resolves locally via `git cat-file -e <sha>^{commit}` BEFORE any ancestry question is asked. A non-zero exit here is a TOOL-ERROR (absent/unfetched object), never read as 'not an ancestor'"
    requirement: "VPP-01"
    verification:
      - kind: integration
        ref: "firestarter/tests/test_pr45_non_ancestry.py::test_pr45_commit_list_is_never_vacuous"
        status: pass
    human_judgment: false
  - id: D2
    description: "HEAD-scoped ancestry proof: for each of the ten PR #45 commits, `git merge-base --is-ancestor <sha> HEAD` is classified into exactly three buckets (0=ancestor/violation, 1=clean, else=tool-error, never a negated single call); examined count asserted ==10; violation list asserted empty"
    requirement: "VPP-01"
    verification:
      - kind: integration
        ref: "firestarter/tests/test_pr45_non_ancestry.py::test_no_pr45_commit_is_an_ancestor_of_head"
        status: pass
    human_judgment: false
  - id: D3
    description: "Content-divergence corroboration: the two new seam files' live worktree blob hashes (git hash-object) differ from PR #45's recorded blob SHAs; mapping asserted to have exactly 2 entries, both paths asserted to exist before comparison"
    requirement: "VPP-01"
    verification:
      - kind: integration
        ref: "firestarter/tests/test_pr45_non_ancestry.py::test_seam_files_diverge_from_pr45_blobs"
        status: pass
    human_judgment: false
  - id: D4
    description: "Fail-closed self-enforcement: the git resolver is fail-closed and exercised directly; this module's own source contains no pytest.skip call and no @pytest.mark.skipif decorator anywhere (needles built by concatenation so the leg does not trip on itself)"
    requirement: "VPP-01"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_pr45_non_ancestry.py::test_git_is_required_not_optional"
        status: pass
    human_judgment: false

duration: 30min
completed: 2026-07-31
status: complete
---

# Phase 125 Plan 03: PR #45 Non-Ancestry Gate Summary

**A pytest module (4 functions / 4 collected cases) discharges ROADMAP Criterion 1 with a real exit code: all ten of PR #45's commits are proven not-ancestor of `HEAD` via a `HEAD`-scoped, three-bucket `git merge-base --is-ancestor` classification -- replacing the ROADMAP's own named mechanism (`git log --all --grep`), which RESEARCH C-2 measured wrong in two independent ways -- plus a content-divergence corroboration leg on the two seam files' blob hashes.**

## Performance

- **Duration:** ~30 min
- **Completed:** 2026-07-31
- **Tasks:** 2 (Task 1: never-vacuous guard + ancestry proof, 2 cases; Task 2: blob-divergence + self-enforcement legs, +2 cases)
- **Files modified:** 1 new file in the firmware submodule (`firestarter/tests/test_pr45_non_ancestry.py`); 1 new SUMMARY in the meta repo

## The Ten-Commit Tuple, As Authored

```python
PR45_SHAS = (
    "04fd9b3", "fc0b2c7", "86f351a", "768580f", "05f4a77",
    "b964ee6", "9134f2a", "d285b83", "71278d0", "a47228d",
)
```

Chronological order, exactly matching `git rev-list origin/beta..origin/feature/common-vpp-calibration` (RESEARCH C-3). Merge base with `origin/beta`: `a1953c22862ac3fb1e0111985946644a568aee36`. PR #45 branch tip: `a47228d862b9b53e6d936d1d0993bee9fc74940e`.

## Observed Existence-Query Exit Codes (Coverage 1), Re-Run By Hand For This SUMMARY

Command shape: `git -C /workspaces/firestarter cat-file -e "<sha>^{commit}"`. Firmware `HEAD` at time of this hand-run: `9c11f63e2f9a42e11bdbc0d668ca6e33af56f1b0` (before this plan's own two commits landed):

| SHA | existence exit |
|---|---:|
| `04fd9b3` | 0 |
| `fc0b2c7` | 0 |
| `86f351a` | 0 |
| `768580f` | 0 |
| `05f4a77` | 0 |
| `b964ee6` | 0 |
| `9134f2a` | 0 |
| `d285b83` | 0 |
| `71278d0` | 0 |
| `a47228d` | 0 |

All ten objects resolve locally (the PR #45 ref is fetched in this devcontainer).

## Observed Ancestry-Query Exit Codes (Coverage 2), Re-Run By Hand For This SUMMARY

Command shape: `git -C /workspaces/firestarter merge-base --is-ancestor "<sha>" HEAD`, against the same `HEAD = 9c11f63e2f9a42e11bdbc0d668ca6e33af56f1b0`:

| SHA | ancestry exit | verdict |
|---|---:|---|
| `04fd9b3` | 1 | not-ancestor |
| `fc0b2c7` | 1 | not-ancestor |
| `86f351a` | 1 | not-ancestor |
| `768580f` | 1 | not-ancestor |
| `05f4a77` | 1 | not-ancestor |
| `b964ee6` | 1 | not-ancestor |
| `9134f2a` | 1 | not-ancestor |
| `d285b83` | 1 | not-ancestor |
| `71278d0` | 1 | not-ancestor |
| `a47228d` | 1 | not-ancestor |

**Examined count: 10.** All ten exit 1 (clean, not-ancestor). This result holds at both the pre-plan `HEAD` (`9c11f63`) and the plan's own final `HEAD` (`2b5e8c8`, this plan's last commit) -- re-running the module itself (which reads `HEAD` live) after each of this plan's own commits kept passing, confirming the plan's own two new commits do not themselves become ancestor-violations of anything (they are firmware-repo-local test-only additions, not PR #45 commits).

## Hand-Observed Fabricated-SHA Tool-Error Exit (Non-Negotiable Three-Bucket Distinction)

```
$ git merge-base --is-ancestor deadbeefdeadbeefdeadbeefdeadbeefdeadbeef HEAD
fatal: Not a valid commit name deadbeefdeadbeefdeadbeefdeadbeefdeadbeef
exit=128
```

Confirms RESEARCH C-2's measurement: a naive `if ! git merge-base --is-ancestor ...; then pass; fi` would read a bogus or unfetched SHA (exit 128) as clean. The module's `test_no_pr45_commit_is_an_ancestor_of_head` classifies exit codes into exactly three buckets (0=ancestor/violation, 1=clean, else=raised `AssertionError` quoting stderr) and never negates a single call, so this exit-128 case is caught as a loud failure rather than silently passing.

## Every `git` Argv The Module Builds, Enumerated

Read from the module's own `_git(*args)` call sites (`grep -n '_git(' tests/test_pr45_non_ancestry.py`):

| Call site | Subcommand + args |
|---|---|
| `test_pr45_commit_list_is_never_vacuous` | `git -C <repo> cat-file -e "<sha>^{commit}"` (×10) |
| `test_no_pr45_commit_is_an_ancestor_of_head` | `git -C <repo> merge-base --is-ancestor <sha> HEAD` (×10) |
| `test_seam_files_diverge_from_pr45_blobs` | `git -C <repo> hash-object <path>` (×2) |

**Exact subcommand set invoked by this module: `cat-file` (existence, `-e` flag), `merge-base` (ancestry, `--is-ancestor` flag), `hash-object` (blob hash).** No other `git` subcommand appears anywhere in the module. Every reachability query (`cat-file -e`, `merge-base --is-ancestor`) names `HEAD` or a fixed SHA — none is repository-graph-wide in scope (`--all` appears nowhere in the file), and none searches commit messages (`--grep` appears nowhere in the file). All three subcommands are invoked via `subprocess.run([...], capture_output=True, text=True)` with list-form argv built from the module's own `_git()` helper — `shell=True` appears nowhere in the file.

## Two Live Seam Blob Hashes Beside PR #45's Two (Coverage 3)

| File | Live worktree blob (`git hash-object`) | PR #45's recorded blob | Equal? |
|---|---|---|---|
| `include/rurp_vpp.h` | `48f9f061ddf0affe743a4020f755ae3688e3fe8c` | `c982173813b38ec745b59d6e02817f2504d6c6b4` | **no** |
| `src/rurp_vpp.cpp` | `5d8b645db14636e895f37582e7a2847e4aa7bae9` | `fcbe009dffcd46139802f8779865a1d7aa331880` | **no** |

Both live blobs differ from PR #45's, corroborating (not replacing) the ancestry proof: ancestry catches a cherry-pick, this leg catches a copy-paste that left no commit behind.

## Zero-Hit Needle Search (Self-Enforcement Leg), Command And Result

```
$ grep -n "pytest\.skip\|mark\.skipif" tests/test_pr45_non_ancestry.py
(no output)
$ echo $?
1
```

Zero hits for either literal needle (`pytest.skip`, `mark.skipif`) anywhere in the committed file, including inside failure messages -- confirmed by an independent `grep` run outside the module's own concatenation-built assertion, not just by the module's own passing test.

## `FLOOR` / `FIXTURE_FLOOR` -- Confirmed Unchanged

`tests/test_checker_convention.py`: `FLOOR = 5` (line 123), `FIXTURE_FLOOR = 10` (line 124) -- both unchanged, `7 passed`. No file was added under `firestarter/scripts/` (`ls scripts/ | grep -i pr45` -> no match). This module lives under `tests/`, never `scripts/check_*.py` (RESEARCH C-11).

## `pytest tests/` Before / After

- Before this plan (post-125-02): **82 passed**.
- After Task 1 (2 new cases: never-vacuous guard + ancestry proof): **84 passed**, re-measured immediately before the Task 1 commit.
- After Task 2 (2 more new cases: blob-divergence + self-enforcement): **86 passed**, re-measured immediately before the Task 2 commit and again as a final check after both commits.

## Module Totals (from `--collect-only -q`)

**4 collected cases from 4 test functions:** `test_pr45_commit_list_is_never_vacuous`, `test_no_pr45_commit_is_an_ancestor_of_head`, `test_seam_files_diverge_from_pr45_blobs`, `test_git_is_required_not_optional`.

## Task Commits

1. **Task 1: The non-vacuity guard and the HEAD-scoped ancestry proof** — `27b2f17` (test, firmware repo `/workspaces/firestarter`)
2. **Task 2: The blob-divergence leg and the fail-closed self-enforcement leg** — `2b5e8c8` (test, firmware repo `/workspaces/firestarter`)

**Plan metadata:** meta-repo commit for this SUMMARY + STATE.md + ROADMAP.md (see final commit below).

## Files Created/Modified

- `firestarter/tests/test_pr45_non_ancestry.py` — new, 4 functions / 4 collected cases (232 lines after both tasks)

## Decisions Made

- **`tests/test_pr45_non_ancestry.py`, never `scripts/check_pr45_ancestry.py`.** RESEARCH C-11 planted the `scripts/` shape and measured the cost: `2 failed, 5 passed` in `tests/test_checker_convention.py` (`test_every_checker_has_paired_test_module` + `test_every_checker_has_planted_fixture`), requiring four extra artifacts (the checker itself, a paired `tests/test_check_pr45_ancestry.py`, a planted `tests/fixtures/planted_pr45_ancestry*` fixture, and `FLOOR 5->6` + `FIXTURE_FLOOR 10->11`). The `tests/` shape costs zero — confirmed here: `test_checker_convention.py` stayed at `7 passed`, `FLOOR`/`FIXTURE_FLOOR` unchanged.
- **Two-commit split matching the plan's task structure.** The whole module was authored as one coherent design, then deliberately split so Task 1's commit contains only Coverage 1+2 (verified 2 passed / 84 in `tests/` before committing) and Task 2's commit adds Coverage 3+4 (verified 4 passed / 86 before committing) — matching each task's own `<acceptance_criteria>` count assertions "at this task's end" exactly, rather than landing both in one commit.
- **Never `--all`, never `--grep`.** Every reachability query in the module is scoped to `HEAD` (or a fixed SHA pair), matching RESEARCH C-2's measured finding that `--all` finds all ten PR #45 commits reachable via the fetched `origin/feature/common-vpp-calibration` ref regardless of `HEAD`, and that `--grep` searches commit messages (zero rows today, would stay zero after a message-rewritten cherry-pick).
- **Requirement ticking scope: NONE.** Per the phase's explicit scope guard, this plan does not tick VPP-01 (or VPP-02/VPP-03) in `.planning/REQUIREMENTS.md` — only Plan 125-06 may do that.

## Deviations from Plan

None. The plan's action block, acceptance criteria and verification commands were followed as written; no auto-fix, no architectural question, no auth gate.

## Known Stubs

None. This plan authors test code only; there is no UI or downstream consumer, and no hardcoded empty value flows to any rendering layer.

## Threat Flags

None. This plan's threat model (see `125-03-PLAN.md` `<threat_model>`) is fully addressed: T-125-15 (a Criterion-1 check that cannot fail) is mitigated by replacing the message-searching mechanism with the object-existence + HEAD-scoped ancestry query pair, with every argv the module builds enumerated above; T-125-16 (a mistyped/unfetched SHA reading as clean) is mitigated by the never-vacuous existence check plus the three-bucket ancestry classification, and the fabricated-SHA behavior was independently re-observed by hand (exit 128); T-125-17 (a vacuous pass from a shortened/emptied commit list) is mitigated by the length-10 + distinctness assertions plus the in-loop examined-count assertion; T-125-18 (a copy-paste leaving no commit to detect) is mitigated by the blob-SHA inequality leg with a length-2 mapping assertion; T-125-19 (a silent schema change smuggled by a partial cherry-pick) is mitigated by "cherry-pick nothing" plus C-18's specific mechanism recorded in the blob-divergence leg's docstring; T-125-20 (a missing `git` binary silently skipped) is mitigated by the fail-closed resolver plus the self-enforcement source scan (independently re-confirmed via a standalone `grep`, zero hits); T-125-21 (landing as a checker script and lowering a floor) is avoided by construction — the module lives under `tests/`, confirmed against `FLOOR`/`FIXTURE_FLOOR` staying unchanged at 5/10. No new security-relevant surface was introduced — this plan adds test code only, exercising `git` read-only subprocess calls against the already-fetched local object graph.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Claim Ceiling Compliance

This SUMMARY makes no claim that the firmware runs on a PY32F071, that closed-loop VPP works, that the pin map is correct/verified/validated, or an unqualified bench-validated/hardware-validated/silicon-verified claim. This plan's scope is entirely a `git`-history and blob-hash proof about the firmware repository's own commit graph; it touches no board-specific behavior and makes no claim about the py32f071 target, PR #47's closed-branch VPP DAC implementation, or any silicon.

## Next Phase Readiness

- VPP-01's non-ancestry half is committed and green (4/4 passing, 86/86 in the full `tests/` suite). Requirement VPP-01 remains unticked in `.planning/REQUIREMENTS.md`, as required — reserved for Plan 125-06's closing sweep.
- No blockers. `check_cmake_manifest.py` and `check_size_baseline.py` are unaffected — this plan adds no production source file and touches no CMake or platformio.ini line.
- Plan 125-04 (Criterion 4: three cold AVR builds, two-directional non-vacuity, D-16 disposition) is unaffected by this plan and can proceed independently.

---
*Phase: 125-vpp-control-seam*
*Completed: 2026-07-31*

## Self-Check: PASSED

- FOUND: `firestarter/tests/test_pr45_non_ancestry.py`
- FOUND: firmware commit `27b2f17` (`git log --oneline --all` in `/workspaces/firestarter`)
- FOUND: firmware commit `2b5e8c8` (`git log --oneline --all` in `/workspaces/firestarter`)
- FOUND: `/workspaces/.planning/phases/125-vpp-control-seam/125-03-SUMMARY.md`
