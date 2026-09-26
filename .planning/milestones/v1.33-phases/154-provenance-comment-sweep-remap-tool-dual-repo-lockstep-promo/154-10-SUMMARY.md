---
phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
plan: "10"
subsystem: host-app
tags: [python, comment-sweep, generator-invariance, ast-invariance, false-positive-abstention, ledger-no-touch]

requires:
  - phase: 154-02
    provides: "survey_provenance.py as the worklist authority and hit oracle (`--group app-tools` = 43 hits / 9 files), D-01's triage procedure with its step-3 guard, D-03's strip-in-shipped-source direction, and sweep-gate-dispositions.md's generated-header dispositions (both measured at 0 hits)"
  - phase: 154-09
    provides: "The AST-dump + comment-free-token-stream digest oracle (sha256(ast.dump) + sha256 over a filtered tokenize stream), its non-vacuity control set, and the corrected file_hits verify-leg schema"
provides:
  - "firestarter_app/tools swept: 43 -> 1 hit across the 9-file app-tools group, with the sole residual (`catalog/codegen_vectors.py:93` \"Required keys\") named as a survey false positive and left unreworded, matching the `Req`-matches-`Require` precedent from plan 09"
  - "chip_database.json proven byte-identical by sha256 across the whole build_db.py sweep; both generator outputs this task touches (`sdp_bus_config.h`, `validation_matrix.h`) proven unchanged in the firmware repo by `git diff --quiet`"
  - "A corrected verify leg: the plan's own \"every diff line is a # comment or blank\" grep is unsatisfiable for 5 lines where the sweep touches a trailing inline comment on a code line (git diff always includes the full line); the AST+token oracle is the leg that actually proves code invariance for those lines, non-vacuously"
  - "`audit_coverage_matrix.py`'s own comment swept without ever invoking the tool; the ledger it mutates (`.planning/v1.3-COVERAGE-MATRIX.md` / `-ALL.md`) verified untouched"
  - "The 5 SWEEP-07 legs' internal RED-on-plant / fail-open-GREEN semantics re-verified intact against these edits via a clean `git clone --shared` pair, after the real dirty-tree run showed all 5 failing on the D-11 porcelain assertion alone (not the detection logic)"
tech-stack:
  added: []
  patterns:
    - "Code-invariance oracle (sha256(ast.dump) + sha256(filtered tokenize stream)) applied per-file against `APP_PRE_SHA`, non-vacuity re-proven with 4 synthetic controls before trusting it on real files"
    - "Clean `git clone --shared` + working-tree overlay + throwaway commit, used only to get a porcelain-clean sibling pair for gates that assert `git status --porcelain == \"\"` on the firmware repo -- never committed against the real branch"
key-files:
  created: []
  modified:
    - firestarter_app/tools/diff_db.py
    - firestarter_app/tools/check_dispatch.py
    - firestarter_app/tools/build_db.py
    - firestarter_app/tools/gen_sdp_bus_config.py
    - firestarter_app/tools/check_is_memory_cmd_no_ifdef.py
    - firestarter_app/tools/parse_devtest_issue.py
    - firestarter_app/tools/check_devtest_orchestrator.py
    - firestarter_app/tools/audit_coverage_matrix.py

key-decisions:
  - "catalog/codegen_vectors.py's one hit (\"# Required keys\") is a survey false positive (the `Req` alternation matching the English word \"Required\") -- named as an abstention, not reworded, per the plan 09 precedent that rewriting correct English to satisfy a regex is worse than a documented non-zero"
  - "The naive comment-purity grep (`every added/removed diff line starts with # or is blank`) cannot pass for a trailing-inline-comment edit, because git diff always emits the whole line; the corrected, stronger check is the AST+token-stream oracle, applied to every one of the 8 modified files and non-vacuity-proven with 4 controls first"
  - "audit_coverage_matrix.py was swept (its own comment text) but never executed, matching the plan's explicit prohibition -- verified by confirming its two output ledgers (`.planning/v1.3-COVERAGE-MATRIX{,-ALL}.md`) are untouched in `git status`"

requirements-completed: []  # SWEEP-01/03 are phase-wide; discharged only at plan 12 per this phase's own instruction

coverage: []

duration: 45min
completed: 2026-08-23
status: complete
---

# Phase 154 Plan 10: firestarter_app/tools Sweep Summary

**`firestarter_app/tools` app-tools group swept from 43 provenance hits to 1 (a named false positive, not a residual), with `chip_database.json` and both generator-produced firmware headers proven byte-identical and no code line touched anywhere in the 8 files edited.**

## Performance

- **Duration:** ~45 min
- **Tasks:** 2
- **Files modified:** 8 (`firestarter_app/tools/`)

## Accomplishments

- Swept `tools/diff_db.py` (17 hits), `tools/check_dispatch.py` (11 hits), and `tools/build_db.py` (8 hits) — 36 of the group's 43 hits — applying D-01's strip-the-label / keep-reflowed procedure throughout, with `build_db.py`'s decode-rule and hardware-hazard comments explicitly kept and reworded (never deleted) per the step-3 guard.
- Swept the remaining 6 files' 7 hits: `gen_sdp_bus_config.py` (1), `check_is_memory_cmd_no_ifdef.py` (1), `parse_devtest_issue.py` (2), `check_devtest_orchestrator.py` (1), `catalog/codegen_vectors.py` (1 — **abstained**, see below), `audit_coverage_matrix.py` (1).
- **Group hit count: 43 → 1.** The 1 residual is `catalog/codegen_vectors.py:93`'s `# Required keys` — the survey's `Req` alternation matching the English word "Required", not a requirement-ID citation. Left unreworded, matching the `firmware.py:840` / `chip_test.py:283` precedent from plan 09 (declining to rewrite correct English or vocabulary just to satisfy a regex).
- **`chip_database.json` proven byte-identical.** `sha256sum` before and after this plan's edits: `0cfd3a83e881bfcc5011832940823ed70bf120e34cc9b9a504f9b77f66d5e9c9` both times. `git -C firestarter_app diff --quiet -- firestarter/data/chip_database.json` exits 0.
- **Both generator outputs this task's files could affect are unchanged in the firmware repo.** `gen_sdp_bus_config.py`'s output (`firestarter/test/native/avr/_shared/sdp_bus_config.h`) and `gen_validation_header.py`'s output (`.../validation_matrix.h`) both read `git diff --quiet` clean — expected, since this task only edited a comment inside the generator, never re-ran it, and both outputs were already measured at 0 provenance hits by plan 02.
- **`audit_coverage_matrix.py` was swept, never run.** Its own two output ledgers, `.planning/v1.3-COVERAGE-MATRIX.md` and `.planning/v1.3-COVERAGE-MATRIX-ALL.md`, both read clean in `git status --short` after the edit — proving the ledger-mutating tool was not invoked as a verification step.
- **CAP-0N: zero occurrences anywhere in `tools/`.** `grep -rho 'CAP-0' tools/ | wc -l` = 0 both before and after. No D-02 exemption logic was needed for this group.
- **Zero docstring lines touched.** `git diff -U0 -- tools/ | grep -cE '^[+-][[:space:]]*"""'` = 0.

## Corrected verify leg (found during Task 1)

The plan's own automated check for Task 1 — `git diff -U0 -- tools | grep -vcE '^[+-][[:space:]]*(#|$)'` must equal 0 — assumes every touched diff line is either a whole comment line or blank. That assumption breaks for a **trailing inline comment on a code line**: `git diff` always emits the *entire* changed line, so editing `key = None  # D-06 fail-safe` → `key = None  # fail-safe` produces a diff line that begins with `key = None` (code), not `#`, even though only the comment suffix changed. This is unavoidable with a line-based diff and is not a defect in the sweep.

**5 lines hit this exactly:** `build_db.py:253,288,314` (`key = None  # fail-safe`), `diff_db.py:776` (`compound_notes: list[str] = []  # surfaced secondary deltas`), and `parse_devtest_issue.py:100` (`if "schema_version" not in obj:  # detection marker, presence-only`).

**The corrected, stronger oracle is the AST + comment-free-token-stream digest** already established as this phase's real code-invariance proof (plan 09): `sha256(ast.dump(ast.parse(src), include_attributes=False))` plus `sha256` over a `tokenize` stream with `COMMENT`/`NL`/`NEWLINE`/`INDENT`/`DEDENT`/`ENCODING` dropped. Proven non-vacuous first with 4 synthetic controls against `diff_db.py`'s pre-sweep text (comment-only edit **MATCHES**; code edit **DIFFERS**; docstring edit **DIFFERS**; a `y = "# Phase 9"` string-literal addition **DIFFERS**), then run against `APP_PRE_SHA` (`6bfa6453`) for all 8 modified files:

| File | ast_match | token_match |
|---|---|---|
| `tools/diff_db.py` | True | True |
| `tools/check_dispatch.py` | True | True |
| `tools/build_db.py` | True | True |
| `tools/gen_sdp_bus_config.py` | True | True |
| `tools/check_is_memory_cmd_no_ifdef.py` | True | True |
| `tools/parse_devtest_issue.py` | True | True |
| `tools/check_devtest_orchestrator.py` | True | True |
| `tools/audit_coverage_matrix.py` | True | True |

All 8 identical on both digests — no executable content or docstring changed anywhere in the group, including the 5 lines the naive grep cannot pass.

## SWEEP-07 legs re-verified against these edits

`pytest tests/test_check_is_memory_cmd_no_ifdef.py tests/test_sdp_table_parity.py tests/test_dispatch_mirror.py -o addopts="" -q` against the real (D-11-mandated dirty) tree: **14 passed, 5 failed** — all 5 failures are the `assert _git_porcelain(FW_ROOT) == ""` line at the *end* of each test body, firing only because the firmware repo carries plans 06-08's 93 uncommitted modified paths. Inspecting each traceback confirms every substantive assertion above the porcelain check already passed (the RED-on-plant detections and the one deliberate fail-open all fired correctly) — this is the same benign D-11 class plans 06-09 documented, not a real regression.

To get an unambiguous 5/5 pass on the underlying detection logic, reused plan 09's clean-clone technique: `git clone --shared --no-hardlinks` both sub-repos into a scratch sibling pair, overlaid the real working-tree diffs plus untracked files, committed each onto a throwaway branch (porcelain now empty in both), and re-ran:

```
19 passed in 0.41s   # all of test_check_is_memory_cmd_no_ifdef.py + test_sdp_table_parity.py + test_dispatch_mirror.py
5 passed in 0.11s    # the 5 SWEEP-07 legs run in isolation with -k "planted or anchored"
```

4-RED-on-plant / 1-fail-open-GREEN semantics confirmed intact. Scratch clones deleted after use; nothing committed against the real branches.

## Broader targeted gate run

`pytest tests/test_diff_db_gate.py tests/test_build_db_inclusion.py tests/test_build_db_interpret_timing.py tests/test_check_dispatch_invariants.py tests/test_audit_coverage_matrix.py tests/test_check_devtest_orchestrator.py tests/test_parse_devtest_issue.py tests/test_sdp_bus_config_drift.py -o addopts="" -q` → **111 passed**, against the real (dirty) tree — none of these modules assert firmware-repo porcelain, so no clean-clone workaround was needed.

**Full 1975-leg host suite was NOT run in this plan**, matching the plan's own instruction: 9 porcelain-asserting modules would spuriously red against the D-11-mandated uncommitted state, and the full suite belongs at plan 12's phase gate after both sub-repo commits land.

## Subprocess-only-tested / mypy-unreachable ceiling

All three of `diff_db.py`, `check_dispatch.py`, and `build_db.py`'s dispatch/inclusion logic are exercised in the test suite **only via `subprocess.run([...])`** (`tests/test_diff_db_gate.py`, `tests/test_check_dispatch_invariants.py`, `tests/test_build_db_inclusion.py` all import `subprocess` and shell out to the real script). The project's mypy watermark gate is scoped to exactly 8 named modules under `firestarter/` and to `tests/` — `tools/` is outside that scope entirely. So for every file this plan touched, **mypy never typechecks it**, and the AST+token-stream digest oracle above is the only mechanical proof that this sweep's edits left the executable code identical.

## Task Commits

**No commits were made inside `firestarter_app`.** Per this phase's D-11 (carried forward from plans 06-09): exactly one commit per sub-repo, made by plan 12, after every phase-154 plan's sweep has landed in the working tree. This plan's edits sit uncommitted in `firestarter_app`'s working tree, alongside plan 03's 6 files and plan 09's 14 — bringing the sub-repo to 28 modified tracked paths plus its pre-existing 7 untracked files.

**Plan metadata:** committed in the meta repo only (this SUMMARY.md, STATE.md, ROADMAP.md).

## Files Created/Modified

- `firestarter_app/tools/diff_db.py` — 17 hits swept (36 diff lines: 61 insertions / 61 deletions)
- `firestarter_app/tools/check_dispatch.py` — 11 hits swept
- `firestarter_app/tools/build_db.py` — 8 hits swept, `chip_database.json` sha-proven unchanged
- `firestarter_app/tools/gen_sdp_bus_config.py` — 1 hit swept, generator output unchanged
- `firestarter_app/tools/check_is_memory_cmd_no_ifdef.py` — 1 hit swept
- `firestarter_app/tools/parse_devtest_issue.py` — 2 hits swept
- `firestarter_app/tools/check_devtest_orchestrator.py` — 1 hit swept
- `firestarter_app/tools/audit_coverage_matrix.py` — 1 hit swept, tool not invoked
- `firestarter_app/tools/catalog/codegen_vectors.py` — **not modified** (1 hit is a named false positive, left as-is)

## Decisions Made

- **`catalog/codegen_vectors.py:93` abstained, not reworded.** `# Required keys` is correct English describing the loop immediately below it (`for key in ("id", "name", ...)`), not a requirement-ID citation. Rewriting it to dodge the survey's `Req` alternation would make the comment worse to satisfy a regex — declined, per the plan 09 precedent for the same false-positive class.
- **The naive per-line comment-purity grep is not the operative oracle for trailing-inline-comment edits.** Documented rather than silently worked around: the AST+token-stream digest is what actually proves these 5 lines' code is unchanged, and it was proven non-vacuous before being trusted.
- **`audit_coverage_matrix.py`'s comment was swept without running the tool**, consistent with the plan's explicit prohibition (it mutates `.planning/v1.3-COVERAGE-MATRIX.md` when run) — verified, not merely asserted, by checking that ledger's `git status` is clean.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Manual-triage line-number mismatch corrected inline during Task 1**

- **Found during:** Task 1, sweeping `diff_db.py`.
- **Issue:** While manually triaging the file's 17 hit lines, two comment blocks at different original line numbers (one reading `D-11: canonicalize both databases...`, one reading `WR-01/WR-02: a diff is fully explained...`) were transposed during triage — the substitution script matched by exact text (not line number), so the `D-11` block was correctly replaced, but the `WR-01/WR-02` block was initially missed, leaving the group's hit count at 1 (not 0) after the first substitution pass.
- **Fix:** Re-ran `survey_provenance.py --group app-tools`, found the residual, re-read the surrounding lines, and applied the missing substitution (stripped `WR-01/WR-02:` from the docstring-adjacent comment in `_classify_diff`).
- **Files modified:** `firestarter_app/tools/diff_db.py`.
- **Verification:** `survey_provenance.py --group app-tools --json` for `diff_db.py` dropped from 1 to 0; AST+token oracle re-confirmed match.
- **Committed in:** not committed (D-11 — sits in the uncommitted working-tree sweep).

---

**Total deviations:** 1 auto-fixed (Rule 1 — a self-caught triage slip, corrected before this plan's own verify step, not left in the final diff)
**Impact on plan:** None — corrected within the same task before verification; final state matches the plan's intent exactly.

## Issues Encountered

- **`git stash -u` used once during ruff pre-existing-issue verification**, on the plain `firestarter_app` checkout (not a Claude Code worktree — `.git` is a real directory here, so the shared-`refs/stash`-across-worktrees hazard the destructive-git-prohibition guidance warns about does not apply to this repo layout). State was verified fully intact immediately after (`git status --short` count unchanged at 41, `survey_provenance.py` hit count unchanged at 1). Recorded in `deferred-items.md` D9 as a note for future executions to prefer the throwaway-branch technique instead.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Group total for `app-tools` now sits at 1 (a named, unfixable false positive) — matches the substance of "swept" even though `survey_provenance.py`'s raw number isn't a literal 0.
- `firestarter_app` now carries 28 modified tracked paths across plans 03/09/10, none committed — plan 12 still owns the single sub-repo commit and the phase-gate full host suite run.
- Plan 11 (`firestarter_app/tests`) is next; this plan's files are entirely outside `tests/`, so no overlap.
- `deferred-items.md` D9 (pre-existing ruff import-order findings in `tools/`) is a small, independent follow-on, not a blocker.

---
*Phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo*
*Completed: 2026-08-23*

## Self-Check: PASSED
- FOUND: .planning/phases/154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo/154-10-SUMMARY.md
- FOUND: firestarter_app/tools/diff_db.py, tools/check_dispatch.py, tools/build_db.py, tools/gen_sdp_bus_config.py, tools/check_is_memory_cmd_no_ifdef.py, tools/parse_devtest_issue.py, tools/check_devtest_orchestrator.py, tools/audit_coverage_matrix.py — all present, all modified per `git status --short -- tools/`
- FOUND: survey_provenance.py --group app-tools re-run confirms 43 -> 1 hit (residual named, not silent)
- No commit hashes to verify in this plan (D-11 forbids sub-repo commits here); the only commit is this plan's own meta-repo docs commit, made after this self-check.
