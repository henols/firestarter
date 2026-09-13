---
created: 2026-09-13T03:10:00Z
title: Close the six stale enforcement claims WR-01..WR-06 left open by Phase 188
area: both
resolves_phase: unassigned
source: .planning/phases/188-the-tools-directory/188-REVIEW.md (WR-01..WR-06), accepted as follow-on debt at 188 UAT
files:
  - firestarter_app/tools/parse_devtest_issue.py:215 (WR-01)
  - firestarter_app/tests/test_sdp_db_invariant.py:165 (WR-02)
  - firestarter_app/tests/test_numeric_schema_source_scan.py:215,235 (WR-03)
  - firestarter_app/tests/test_build_db_inclusion.py:11 (WR-04)
  - firestarter/.github/workflows/beta-build.yml:107 (WR-05)
  - firestarter_app/CLAUDE.md:127 (WR-06)
  - .planning/notes/host-tools-retirement.md (WR-06 must also be recorded here)
---

## What

Phase 188 retired the host `tools/` gate family. Six prose claims elsewhere in the tree still
describe those retired gates as live enforcement. The operator accepted all six as **disclosed
follow-on debt** at the Phase 188 UAT checkpoint on 2026-09-13 — they are recorded here rather
than fixed inside 188, because fixing them expands the phase beyond its nine plans.

**None of these breaks a test or falsifies a roadmap success criterion.** All four suites were
green and all seven Phase 188 criteria verified. These are false *claims about enforcement*, which
matters because the milestone is named "Claim Hygiene".

## The six, each with the claim that is now false

All six were re-measured directly in the tree on 2026-09-13 and confirmed still present.

| ID | Location | The false claim |
|----|----------|-----------------|
| WR-01 | `firestarter_app/tools/parse_devtest_issue.py:215` | "No claim gate scans this file today (P-5); that test is the only enforcement." Both named enforcers are gone: `check_diagnostic_report_claims.py` is deleted (0 tracked files) and the only surviving mention of `test_parser_marker_strings_trip_no_forbidden_claim_pattern` anywhere in the repo is this comment itself. The claim-safety property now has **zero** enforcement, not one test. |
| WR-02 | `firestarter_app/tests/test_sdp_db_invariant.py:165` | Says widening of the SDP allow-set is what "`tools/check_sdp_capability_invariants.py` already gates elsewhere." That checker is deleted (0 tracked files; 0 files match `tools/check_*.py`). The narrowing direction is still gated by this test; the widening direction is not gated at all. |
| WR-03 | `firestarter_app/tests/test_numeric_schema_source_scan.py:215,235` | The non-vacuity test's docstring and its assertion message both still say "tests 1 and 2". The module docstring at line 43 was correctly repaired to "test 1" — these two were missed in the same sweep, so the file now contradicts itself. |
| WR-04 | `firestarter_app/tests/test_build_db_inclusion.py:11` | "the SC#3 dispatch-safety invariant enforced by Plan 04." The enforcing test was deleted with the `check_*` family; the invariant is unenforced. |
| WR-05 | `firestarter/.github/workflows/beta-build.yml:107` | "Same rationale as the vector gates above" — those vector-gate steps were deleted by 188-06, so the comment's antecedent no longer exists in the file. The step it annotates (`native_nodevtools`) is still correct and must stay; only the back-reference is stale. |
| WR-06 | `firestarter_app/CLAUDE.md:127` | The "Tooling gate (v1.8)" line still lists `mypy` among the checks "all enforced by `.github/workflows/ci.yml` on every PR". 188-04 deleted that CI step under D-02. `ruff check`, `ruff format --check` and `pytest --cov-fail-under=70` remain true; only `mypy` is false. |

## WR-06 carries a second, separate obligation

`188-04`'s own SUMMARY promised that the mypy-gate removal would be recorded permanently in
`.planning/notes/host-tools-retirement.md`, and `188-09` did not deliver it in full.

The note **does** record the CI leg's removal ("The mypy CI leg (D-02) — retired, no replacement",
§2). What it does **not** record is that `firestarter_app/CLAUDE.md` still advertises mypy as
CI-enforced — so a later reader who trusts CLAUDE.md is misled with nothing in the retirement note
to correct them. Fixing WR-06 means **both** editing CLAUDE.md line 127 **and** adding that fact to
the retirement note.

## Note on line numbers

`188-REVIEW.md` cites each finding as a **range** covering the whole comment block (212-215,
161-166, 9-11) and those ranges are correct. The `188-UAT.md` table collapsed each range to its
*first* line rather than to the line carrying the false claim. The line numbers in this file are the
measured claim lines — **215, 165 and 11** — and the UAT table has been repaired to match. WR-03,
WR-05 and WR-06 were already exact in both records.

## Done when

- All six claims are corrected in place (WR-05 by rewording the back-reference, not by deleting the
  step it annotates).
- WR-06's CLAUDE.md correction is accompanied by a matching entry in
  `.planning/notes/host-tools-retirement.md`.
- The four app suites and the firmware native gate stay green.
