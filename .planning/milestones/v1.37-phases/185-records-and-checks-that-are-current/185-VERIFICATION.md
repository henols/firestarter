---
phase: 185-records-and-checks-that-are-current
verified: 2026-09-11T20:30:00Z
status: passed
score: 5/5 must-haves verified
covered_files:
  - ".planning/REQUIREMENTS.md"
  - ".planning/ROADMAP.md"
  - ".planning/notes/catalog-sync-check-retirement.md"
  - ".planning/phases/185-records-and-checks-that-are-current/185-01-PLAN.md"
  - ".planning/phases/185-records-and-checks-that-are-current/185-01-SUMMARY.md"
  - ".planning/phases/185-records-and-checks-that-are-current/185-02-PLAN.md"
  - ".planning/phases/185-records-and-checks-that-are-current/185-02-SUMMARY.md"
  - ".planning/phases/185-records-and-checks-that-are-current/185-03-PLAN.md"
  - ".planning/phases/185-records-and-checks-that-are-current/185-03-SUMMARY.md"
  - ".planning/phases/185-records-and-checks-that-are-current/185-04-PLAN.md"
  - ".planning/phases/185-records-and-checks-that-are-current/185-04-SUMMARY.md"
  - ".planning/phases/185-records-and-checks-that-are-current/185-05-PLAN.md"
  - ".planning/phases/185-records-and-checks-that-are-current/185-05-SUMMARY.md"
  - ".planning/phases/185-records-and-checks-that-are-current/185-06-PLAN.md"
  - ".planning/phases/185-records-and-checks-that-are-current/185-06-SUMMARY.md"
  - ".planning/phases/185-records-and-checks-that-are-current/185-REVIEW.md"
  - "firestarter/scripts/baseline/size_baseline.json"
  - "firestarter/tests/test_check_size_baseline.py"
  - "firestarter_app/firestarter/cli_handlers.py"
  - "firestarter_app/tests/test_check_devtest_orchestrator.py"
  - "firestarter_app/tests/test_dev_test_cmd.py"
  - "firestarter_app/tests/test_numeric_schema_source_scan.py"
  - "firestarter_app/tools/check_devtest_orchestrator.py"
  - "tools/catalog/sync_to_subrepos.sh"
covered_digest: "v1:sha256:4f35a3a4477ce8763d64dc0d67fe9e0087c874a8a32544862dacd1021611ac16"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 185: Records and Checks That Are Current — Verification Report

**Phase Goal:** Four records stop describing a tree that no longer exists.
**Requirements:** CLAIM-04, CLAIM-05, CLAIM-06, CLAIM-07, CLAIM-08
**Verified:** 2026-09-11
**Status:** passed
**Re-verification:** No — initial verification

## Note on `covered_digest`

`gsd_run query verification fingerprint` **silently drops its FIRST positional path** — the first
argument is consumed before the covered-file list is read. Measured after this report was first
written: feeding the 24 declared paths returns 23 `covered_files` (`.planning/REQUIREMENTS.md`,
the first argument, missing); feeding the same 24 behind one sacrificial duplicate returns all 24.
The original diagnosis in this section — that the verb dropped `185-01-PLAN.md` specifically —
was the same defect seen through a different argument order, not a property of that filename.

Consequence: the digest first stored here
(`v1:sha256:b1bb2485bda8d17380b842a0c09f8430f323544ac13c81c3ff57c65e48425271`) was computed over
a 23-path set while `covered_files` above declares 24, so it could never match a recomputation
and `gsd_run query verification.status` reported this phase `stale` regardless of actual drift.
`covered_digest` above has been corrected to the digest over exactly the 24 declared paths, with
the dropped-argument defect worked around. No finding in this report is affected.

## Goal Achievement

### Observable Truths

These are the ROADMAP's five success criteria for Phase 185 (the authoritative contract), each
independently re-executed rather than trusted from SUMMARY prose.

| # | Truth (ROADMAP success criterion) | Status | Evidence |
|---|---|---|---|
| 1 | `check_size_baseline.py` in default mode exits 0 against a fresh cold rebuild of all three AVR targets | ✓ VERIFIED | `check_size_baseline.py --rebuild` (185-02, independently re-confirmed here as still committed and unmodified since) exited 0 and reproduced the committed figures exactly on all five envs: `PASS: uno(flash=22734/32768,ram=1434/2048), uno328pb(flash=22778/32768,ram=1440/2048), leonardo(flash=24830/32768,ram=1875/2560), native(cases=185,suites=17), native_nodevtools(cases=185,suites=17)`. `size_baseline.json` unchanged by the rebuild (`git diff --exit-code`, empty). |
| 2 | `git diff` over the frozen `captured_build_v158_*` fixture paths is empty, and no new MERGE-05 exemption was authored | ✓ VERIFIED | Re-ran `git diff --exit-code ec7c1bbd... -- <4 frozen v158 paths>` myself: exit 0, empty. `MERGE05_*_EXEMPTION_BYTES` count independently re-counted at 34, matching the pre-phase baseline exactly (unchanged). `check_size_baseline.py` and `size_baseline_base01.json` both byte-unchanged against the base sha (re-verified). |
| 3 | `test_numeric_schema_source_scan.py` docstring cites the symbol and its enclosing scope, no line number left to go stale | ✓ VERIFIED | `grep -nE '\.py:[0-9]+' tests/test_numeric_schema_source_scan.py` → no match (was 1 before the phase). The repaired sentence names `_AT28C_DIP24_NAMES` with "a LOCAL variable nested inside a `for` loop several indent levels deep" — matches the symbol's real location (`tools/build_db.py:538`, inside `def main()`, confirmed by direct read), with no replacement number written. |
| 4 | `_is_interactive` is gone, and no test name claims TTY gating the test does not perform | ✓ VERIFIED | `git grep -n _is_interactive` over the whole `firestarter_app` tracked tree → exit 1 (zero references). `git grep -nE 'def test_.*_(on\|off)_a_tty' -- tests/` → exit 1 (zero matching test names). Both re-run independently, not trusted from the SUMMARY. |
| 5 | (AMENDED, D-02) The workflow is deleted and `.planning/notes/catalog-sync-check-retirement.md` names the cause of the standing failure | ✓ VERIFIED | `.github/workflows/catalog-sync-check.yml` confirmed absent (`test ! -e`). The verdict note exists (15056 bytes) and carries all five required `## ` sections (cause, why the 2026-08-18 fix didn't reach it, the now-false comment corrected, the beta-fallback counterfactual, the residual gap). `git grep -n catalog-sync-check -- . ':!.planning'` → exit 1 (nothing outside `.planning/` still names it). |

**Score:** 5/5 truths verified (0 present-but-behavior-unverified).

### Requirements Coverage (CLAIM-04 through CLAIM-08)

| Requirement | Description (REQUIREMENTS.md) | Status | Evidence |
|---|---|---|---|
| CLAIM-04 | `size_baseline.json` records current cold-build figures, default gate green | ✓ SATISFIED | 185-01 cold pass + 185-02 independent `--rebuild` confirmation, both re-verified above |
| CLAIM-05 | Achieved by fixture severance; frozen v158 family byte-unchanged; no new MERGE-05 exemption | ✓ SATISFIED | Empty base-sha diffs re-verified; exemption count unchanged (34); D-12's six orphan candidates re-measured brace-aware and correctly kept (not deleted, not orphaned — verified via `git grep -nF` against the collapsed-brace forms `tests/fixtures/README.md` and the module docstring actually use) |
| CLAIM-06 | `test_numeric_schema_source_scan.py` stops citing `build_db.py:594`, uses symbol+scope form | ✓ SATISFIED | Verified above; boundary is exactly zero `.py:N` citations, confirmed |
| CLAIM-07 | `_is_interactive` removed; no test name claims TTY gating it doesn't perform | ✓ SATISFIED | Verified above; both the test-file severance (185-03) and the source deletion (185-04) landed with zero surviving references anywhere, including the `tools/` module-docstring site the requirement text didn't explicitly name |
| CLAIM-08 | Catalog sync check retired, cause recorded, requirement amended (D-02) | ✓ SATISFIED | Workflow deleted, verdict document complete, REQUIREMENTS.md's amended CLAIM-08 text and ROADMAP criterion 5's amended text are mutually consistent (same two unsatisfiability reasons, same amended wording, same precedent citations) |

**Note on REQUIREMENTS.md checkbox/Traceability state:** CLAIM-04 through CLAIM-08 remain `- [ ]`
(unchecked) and "Pending" in the Traceability table as of this verification. This is **not** a
gap: 185-06-PLAN.md's own Task 3 explicitly instructs "Do not tick either checkbox in this task —
completion state is the phase's own accounting and belongs with its verification, not with the
amendment" (confirmed present in the plan text and honored — neither checkbox was ticked by any of
the six plans). Flipping these five checkboxes and the Traceability rows to Complete is expected to
happen as part of this phase's close-out, following this verification passing — matching the
same sequencing Phase 184 used (its close-out plan 184-05 flipped CLAIM-01/02/03/09 in one
dedicated commit after its own verification).

### Verification-Focus Checklist (from the dispatch)

1. **Did any plan replace a stale record with a new record that is already stale, or restate a
   figure in a second place where it can drift again?**
   Found one instance, already caught and fixed: `size_baseline.json`'s `envs_agree_note` (a prose
   field, not gate-bearing) still quoted the old `{cases: 184, ...}` figure after 185-01 moved
   `native_envs.native.cases` to 185 — exactly the failure mode this file's own convention exists
   to catch, and exactly what the code reviewer's WR-01 finding named. **Confirmed fixed**: firmware
   commit `3c3c802` ("docs(185): correct envs_agree_note's stale 184 case count to the recorded
   185") updates the note to `{cases: 185, ...}` and explicitly narrates the correction inline
   (`"count corrected Phase 185 Plan 01 from the {cases: 184, ...} Phase 158 Plan 04 C-8 had itself
   corrected..."`). Read directly from the file — confirmed present and correct.
   Separately (not a re-introduced staleness, a pre-existing one the phase's own plans explicitly
   declined to touch): `firestarter_app/tests/test_dev_test_cmd.py`'s module docstring "Coverage
   (post-121-09)" bullet still describes "a UV part on a TTY is asked (yes -> full, no -> partial)"
   — behavior that does not exist; the code (`cli_handlers.py:_process_uv_write`, confirmed by
   reading) unconditionally writes `partial` scope for any UV part, TTY or not, with no ask of any
   kind. This predates Phase 185 (the prompt itself was retired in an earlier phase) and 185-03's
   own SUMMARY names this exact bullet as deliberately out of its declared scope (only docstring
   lines 8-14 were in scope, not this "Coverage" bullet). Recorded here as an advisory finding, not
   a gap — no ROADMAP criterion or CLAIM text requires this bullet's repair, and the plan's scoping
   decision is documented rather than silent.

2. **Did the `sync_to_subrepos.sh` repair produce a check that can actually fail, with the red
   observed for the right reason?**
   Yes. Read the current script directly (not just the SUMMARY): both post-generation
   verifications now `diff -q "$tmp_h" "$FS_ROOT/include/messages.h"` / `diff -q "$tmp_py"
   "$FA_ROOT/.../messages.py"` — two distinct operands (a fresh `mktemp` output vs. the installed
   path), each with an `else` branch that writes an `ERROR: ... did not land at ...` line to stderr
   and `exit 1`. 185-05's SUMMARY carries a verbatim transcript of a genuinely planted break
   (`chmod 0444` on the destination, defeating the `cp` install) producing exactly that `ERROR:`
   line naming the correct path, followed by a restore-by-explicit-path and a re-observed green —
   not a reasoned-about red. This is real, causally-connected failure behavior, not a second
   tautology.

3. **Is ROADMAP criterion 5's amendment honest — checkable now, not just a restatement of what was
   done?**
   Yes. The amended wording ("the workflow is deleted and
   `.planning/notes/catalog-sync-check-retirement.md` names what was actually wrong") states two
   independently checkable facts — file absence and a specific document's existence/content — both
   of which I verified directly above, rather than a vague restatement like "this was handled."

4. **Is CLAIM-08's amendment in REQUIREMENTS.md consistent with criterion 5's?**
   Yes. Both name the same two unsatisfiability reasons (workflow deletion means no run on `main`
   can exist; `main` is protected in all three repos and nothing in this phase lands there), the
   same amended wording, and the same precedent citations (Phase 183 D-08, Phase 184 D-03).

5. **Does any test name still claim coverage the test does not perform?**
   No surviving test name matches the `_(on|off)_a_tty` pattern (`git grep` confirms). The one
   remaining unrelated name containing the substring `_off_tty`
   (`test_submit_off_tty_end_to_end_never_opens_browser_or_runs_gh`) predates this phase, makes no
   TTY-vs-non-TTY behavioral claim, and is out of CLAIM-07's declared scope — documented as such in
   185-03's SUMMARY, not silently left.

### Anti-Pattern Scan

No `TBD`/`FIXME`/`XXX` debt markers in any file this phase touched (checked all 23 files this
phase's plans/summaries name as modified). The pre-existing `TBD` occurrences in `ROADMAP.md` are
all in unrelated phase sections this phase's plans did not touch (confirmed: none inside the
Phase 185 section). No stub returns, no empty handlers, no hardcoded-empty props introduced by any
of the six plans' diffs.

### Behavioral / Suite Re-Runs (independently executed by this verifier, not trusted from SUMMARY)

| Check | Command | Result |
|---|---|---|
| Firmware default gate | `pytest tests/test_check_size_baseline.py -q` | `14 passed` |
| Firmware whole suite | `pytest tests/ -q` | `360 passed` |
| Firmware frozen-v158 diff | `git diff --exit-code <base-sha> -- <4 v158 paths>` | exit 0, empty |
| Firmware checker/BASE-01 diff | `git diff --exit-code <base-sha> -- check_size_baseline.py size_baseline_base01.json` | exit 0, empty |
| App touched-module suite | `.venv311/bin/python -m pytest tests/test_dev_test_cmd.py tests/test_check_devtest_orchestrator.py tests/test_numeric_schema_source_scan.py -q` (py3.11.16) | `97 passed` |
| App whole suite | `.venv311/bin/python -m pytest tests/ -q` (py3.11.16) | `2359 passed, 1 warning` — matches the orchestrator's own measurement exactly |
| Catalog sync script current state | read directly | two-operand `diff -q` + `else`/`ERROR:`/`exit 1` confirmed on both verifications |
| Workflow deletion | `test -e .github/workflows/catalog-sync-check.yml` | absent |
| Cross-repo dangling references | `git grep -n catalog-sync-check -- . ':!.planning'` | exit 1 (none) |

All independently re-run; none merely restated from a SUMMARY.

### Scope Discipline

Diffed both submodules against their pre-phase base shas (`ec7c1bbd..HEAD` firestarter,
`a745cb64..HEAD` firestarter_app) and the meta repo (`2db6e2f1..HEAD`): every changed file matches
exactly the files each plan's frontmatter declared (`files_modified`), with no unrelated file
touched. `firestarter/submit.py` and `firestarter/jp5_gate.py` — the prohibition in 185-04 —
confirmed absent from any diff. No backlog item, todo, or successor-guard artifact was filed for
D-12's reversal or CLAIM-08's residual gap (confirmed: `git status --porcelain -- .planning/todos/
.planning/backlog` shows nothing from this phase).

### Human Verification Required

None. Every truth in this phase resolves to a directly re-executable, deterministic check (fixture
byte content, git diffs, grep absence/presence, pytest exit codes) — no UI, no real-time behavior,
no external service.

## Gaps Summary

None. All five ROADMAP success criteria hold on independent re-execution, all five CLAIM
requirements are satisfied, the one code-review Warning (WR-01, `envs_agree_note`'s stale figure)
was fixed in a follow-up commit and the fix is confirmed present, and no new instance of the
phase's own defect class (a record describing a tree that no longer exists) was introduced by any
of the six plans. The single advisory item (the pre-existing, out-of-scope "Coverage (post-121-09)"
docstring bullet in `test_dev_test_cmd.py`) is not a phase must-have and is explicitly disclosed as
such in 185-03's own SUMMARY — a future phase reopening `dev test`'s TTY-adjacent test coverage
should read it first.

---

*Verified: 2026-09-11*
*Verifier: Claude (gsd-verifier)*
