---
phase: 184-guards-that-exist
verified: 2026-09-11T14:20:00Z
status: passed
score: 4/4 must-haves verified
covered_files:
  - ".planning/REQUIREMENTS.md"
  - ".planning/ROADMAP.md"
  - ".planning/notes/dispatch-invariant-retirement-verdict.md"
  - ".planning/phases/184-guards-that-exist/184-01-PLAN.md"
  - ".planning/phases/184-guards-that-exist/184-01-SUMMARY.md"
  - ".planning/phases/184-guards-that-exist/184-02-PLAN.md"
  - ".planning/phases/184-guards-that-exist/184-02-SUMMARY.md"
  - ".planning/phases/184-guards-that-exist/184-03-PLAN.md"
  - ".planning/phases/184-guards-that-exist/184-03-SUMMARY.md"
  - ".planning/phases/184-guards-that-exist/184-04-PLAN.md"
  - ".planning/phases/184-guards-that-exist/184-04-SUMMARY.md"
  - ".planning/phases/184-guards-that-exist/184-05-PLAN.md"
  - ".planning/phases/184-guards-that-exist/184-05-SUMMARY.md"
  - ".planning/phases/184-guards-that-exist/184-CONTEXT.md"
  - ".planning/phases/184-guards-that-exist/184-REVIEW.md"
  - "CLAUDE.md"
  - "firestarter/PROTOCOLS.md"
  - "firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp"
  - "firestarter_app/tests/fixtures/planted_no_exists_proxy.py"
  - "firestarter_app/tests/scan_paths.py"
  - "firestarter_app/tests/test_scan_paths_resolve.py"
  - "firestarter_app/tools/check_no_exists_proxy.py"
covered_digest: "v1:sha256:aab65c1df2010db1d700968e7d7c4f8669bf4c6e430f3df7ae926e8343e46948"
behavior_unverified: 0
overrides_applied: 0
coincidental_reliance_items: []
---

# Phase 184: Guards That Exist Verification Report

**Phase Goal:** No repository claims a guard it does not have, and the next such claim fails
closed instead of going unnoticed.

**Verified:** 2026-09-11T14:20:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP § Phase 184 success criteria, criterion 1 as AMENDED)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 (amended) | No file in any of the three repositories names `tools/wiki/dispatch_mirror.py` as a live guard | ✓ VERIFIED | `git grep -n 'tools/wiki/dispatch_mirror' -- . ':(exclude).planning'` returns nothing (exit 1) independently re-run in meta, `firestarter`, and `firestarter_app` — each paired with a positive control (`tools/wiki` present in `CLAUDE.md`/`PROTOCOLS.md`; `dispatch_mirror` present in exactly the two D-02-kept app files) proving the search actually scanned the tree. |
| 2 | A test fails when a `ScanPathEntry` names a guard file that is absent — proven by planting one, observed red, then removed | ✓ VERIFIED | Independently reproduced by this verifier: planted a zero-`resolved_by` entry into `scan_paths.py`, re-ran `pytest tests/test_scan_paths_resolve.py`, observed `1 failed, 4 passed` with the exact offender message, then restored the file and re-observed `5 passed`. The phase's own captured RED (against the real 11-day-rotted `tools/wiki/dispatch_mirror.py` entry) matches the assertion message actually present in the shipped `test_every_scan_path_resolver_is_an_existing_tests_module`. Commit ordering confirms the entry was removed in the same commit that added the check (`ae92dd1`), consistent with the plan's "do not commit the red state on its own" instruction. |
| 3 | The two orphaned `planted_dispatch_*` fixtures are deleted or re-pointed at a consumer that exists | ✓ VERIFIED | Both files absent from disk and git index (`git ls-files` empty); `planted_no_exists_proxy.py` survives. Deletion commit `4a90ce4` (13:36:18) postdates the verdict-note commits `52f0211b`/`a76b8f00` (13:17:49/13:18:03) that migrate the fixtures' fail-open finding — confirmed by direct commit timestamp comparison, not taken from the SUMMARY's word. Deleted-file content recovered via `git show 4a90ce4~1:...` matches the quotes in the verdict note verbatim. |
| 4 | Whether the three-way dispatch invariant is worth re-guarding is decided and recorded; "retire it" is acceptable, "unaddressed" is not | ✓ VERIFIED | `.planning/notes/dispatch-invariant-retirement-verdict.md` (351 lines) exists, opens with a bolded "RETIRED OUTRIGHT" verdict, states the operator's-call-against-orchestrator's-recommendation framing, carries the two-deletion evidence chain (`39ea3e8`, `5426d7ef`, both dates independently confirmed via `git log`), the fixtures' fail-open finding, an explicit measured-not-adjudicated drift table (12 host-side vs 13 firmware-side, independently re-counted by this verifier), and a negative record of zero backlog filings (`999.x` count unchanged at 62; `git status --porcelain -- .planning/ROADMAP.md .planning/todos/` empty). |

**Score:** 4/4 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/tests/test_scan_paths_resolve.py` | Fifth test, fail-closed, unmarked | ✓ VERIFIED | `test_every_scan_path_resolver_is_an_existing_tests_module` present, no `@requires_fw`/marker, uses `is_file()` not `exists()`, collects offenders then asserts once. `5 passed` confirmed live. |
| `firestarter_app/tests/scan_paths.py` | Rotted entry removed, count figures true | ✓ VERIFIED | `dispatch_mirror` count 0, `ScanPathEntry(` count 6, `8 paths` count 0 — all re-run live. |
| `firestarter/PROTOCOLS.md` | Honest retirement line, no `dispatch_mirror` | ✓ VERIFIED | Replacement paragraph present with all 6 required elements (`tools/wiki/`, `5426d7ef`, `2026-09-02`, bolded absence, human-readers statement, zero `dispatch_mirror`). |
| `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` | False clause deleted, nothing added | ✓ VERIFIED | Comment reads exactly the surviving words; `KNOWN_PROTOCOLS` count 3 (down from 4); `kAllProtocolFamilies` 13 rows unchanged; native dispatch suite 23/23. |
| `firestarter_app/tools/check_no_exists_proxy.py` / `tests/fixtures/planted_no_exists_proxy.py` | Citations re-dated, lint behavior unchanged | ✓ VERIFIED | `test_dispatch_mirror` name kept (1×/2×), `39ea3e8`/`2026-08-31` present at each site, comment-line count unchanged (5), `test_check_no_exists_proxy.py` passes. |
| `.planning/notes/dispatch-invariant-retirement-verdict.md` | CLAIM-03 verdict record | ✓ VERIFIED | Exists, 351 lines, contains all required elements (see truth 4 above). |
| `CLAUDE.md` | `tools/wiki` claim repaired | ✓ VERIFIED | Diff is exactly one paragraph (1 insertion/1 deletion); `tools/` on disk holds only `catalog/`; `.planning/v1.35/MIGRATION-TABLE.md` exists. |
| `.planning/ROADMAP.md` | Criterion 1 amended in place | ✓ VERIFIED | 26-line insertion at criterion 1 only; `999.x` count unchanged (62); rest of file untouched. |
| `.planning/REQUIREMENTS.md` | CLAIM-01/02/03/09 ticked in both places | ✓ VERIFIED | `### CLAIM` checkbox list and `## Traceability` table both show all four complete with evidence notes. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `184-03` verdict-note commits | `184-04` fixture-deletion commit | Ordering precondition (note must hold finding before deletion) | ✓ WIRED | Verdict-note commits at 13:17–13:18 predate the deletion commit at 13:36, confirmed by direct `git log` timestamp comparison in `firestarter_app`. |
| meta HEAD | `firestarter` HEAD | Gitlink advance | ✓ WIRED | `git rev-parse HEAD:firestarter` (`ec7c1bb...`) equals `firestarter`'s own `HEAD`. |
| meta HEAD | `firestarter_app` HEAD | Gitlink advance | ✓ WIRED | `git rev-parse HEAD:firestarter_app` (`a745cb6...`) equals `firestarter_app`'s own `HEAD`. |
| `.planning/REQUIREMENTS.md` | `.planning/notes/dispatch-invariant-retirement-verdict.md` | CLAIM-03 evidence citation | ✓ WIRED | Traceability table row names the note file directly. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Fail-closed check catches an empty `resolved_by` | Planted a zero-tuple `ScanPathEntry`, re-ran `pytest tests/test_scan_paths_resolve.py -o addopts="" -q`, restored file | `1 failed, 4 passed` with the exact "resolved_by is empty" message, then `5 passed` after restore; `git status --porcelain` clean | ✓ PASS |
| Native dispatch suite unaffected by comment edit | `pio test -e native -f 'native/avr/test_dispatch'` | `23 test cases: 23 succeeded` | ✓ PASS |
| App suite still collects after fixture deletion | `pytest tests/ --collect-only -q -o addopts=""` | `2360 tests collected` | ✓ PASS |
| Targeted app tests pass | `pytest tests/test_check_no_exists_proxy.py tests/test_sdp_honesty.py tests/test_scan_paths_resolve.py -o addopts="" -q` | `22 passed` | ✓ PASS |
| No `tools/wiki/dispatch_mirror.py` reference in any repo | `git grep -n 'tools/wiki/dispatch_mirror' -- . ':(exclude).planning'` (meta, firestarter, firestarter_app) | All three: no output, exit 1 | ✓ PASS |
| `KNOWN_PROTOCOLS` set contents (drift-table basis) | `python3 -c "..."` counting the literal set | `12` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|--------------|------------|-------------|--------|----------|
| CLAIM-01 | 184-01, 184-02, 184-04, 184-05 | No file names `tools/wiki/dispatch_mirror.py` as a live guard | ✓ SATISFIED | Zero hits across all three repos; criterion-1 amendment records the resolved substring collision. |
| CLAIM-02 | 184-04 | Two orphaned `planted_dispatch_*` fixtures disposed | ✓ SATISFIED | Both deleted; fail-open finding migrated to verdict note first (ordering confirmed by commit timestamps). |
| CLAIM-03 | 184-02, 184-03 | Three-way dispatch invariant decided and recorded | ✓ SATISFIED | Verdict note: RETIRED OUTRIGHT, with grounds, evidence chain, drift table, negative record. |
| CLAIM-09 | 184-01 | Fail-closed check asserts every `ScanPathEntry` guard file exists | ✓ SATISFIED | New test proven RED on the real rotted entry and on three synthetic edges (empty, non-bare, absent); independently re-verified by this verifier. |

No orphaned requirements: `.planning/REQUIREMENTS.md`'s "Phase 184" references cover exactly CLAIM-01/02/03/09, matching every plan's declared `requirements` field.

### Anti-Patterns Found

None. Comment-line counts in all touched files stayed at or below their pre-phase ceilings (`test_scan_paths_resolve.py` 14, `scan_paths.py` 26, `planted_no_exists_proxy.py` 5 — all confirmed live). No `TBD`/`FIXME`/`XXX` markers were introduced by this phase's diff to `CLAUDE.md`, `ROADMAP.md`, `REQUIREMENTS.md`, or any of the touched source files (checked via `git diff <phase-base> HEAD` restricted to added lines). No escape hatch, allowlist, or bypass branch was added to the new fail-closed check. `184-REVIEW.md` (code review, 7 files, 0 findings) independently confirms this.

### Two Recorded Corrections (both re-checked against source, not merely restated)

1. **184-02's must-have truth 3** claimed `PROTOCOLS.md` "carries no claims-region delimiter of any kind." This verifier confirmed the claim is indeed false — `<!-- firestarter-claims-begin -->` / `<!-- firestarter-claims-end -->` are present at lines 53/82 of the live file, predating the phase (`git show bbcdc39:PROTOCOLS.md`). The disclosure is accurate: the delimiters are orphaned inert markup (no live script in any of the three repositories references them, confirmed by grep), left in place deliberately and outside CLAIM-01's scope (which is about a checker being *named*, not a marker existing). The must-have's two operative requirements (no table-shape-preservation instruction, no "claims region" reference) both hold, confirmed by grep.
2. **184-04's Task 3 precondition** cited `firestarter_app/tests/test_flash_path_record_sync.py`. Confirmed: no such file has ever existed in the app repo (`git log --all --name-only -- '*flash_path_record_sync*'` empty); the 54 KB file of that name lives in `firestarter/tests/`. The misattribution did not affect execution — Tasks 1 and 2 were already committed before Task 3 ran, per GSD's atomic-commit-per-task discipline — and is disclosed rather than silently carried.

### Human Verification Required

None. All four success criteria, all plan-level must-haves, and both recorded corrections were independently re-derived from the live codebase and git history by this verifier (not merely re-stated from SUMMARY.md), including one live behavioral reproduction of the fail-closed check's RED/GREEN cycle.

### Gaps Summary

No gaps. All four ROADMAP success criteria are met, both submodule gitlinks are advanced to the correct commits, both requirement-tracking locations in REQUIREMENTS.md are ticked with named evidence, zero new backlog/todo items were filed, and the phase's own two self-disclosed corrections were independently re-verified as accurate and non-blocking.

---
_Verified: 2026-09-11T14:20:00Z_
_Verifier: Claude (gsd-verifier)_
