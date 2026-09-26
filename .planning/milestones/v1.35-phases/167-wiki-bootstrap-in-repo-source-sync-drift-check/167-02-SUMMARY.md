---
phase: 167-wiki-bootstrap-in-repo-source-sync-drift-check
plan: 02
subsystem: testing
tags: [python, bash, argparse, regex, wiki, stdlib-only, link-validation]

requires:
  - phase: 167-wiki-bootstrap-in-repo-source-sync-drift-check
    provides: "tools/wiki/wiki.py CLI skeleton, exit-code contract, sidebar generator; tools/wiki/selftest.sh fixture harness"
provides:
  - "tools/wiki/wiki.py `links` subcommand — orphan detection (Home.md-only reachability evidence), single-legal-link-form enforcement, case-sensitive resolution, filename legality"
  - "tools/wiki/wiki.py `check` subcommand — offline aggregator (sidebar freshness + links), accumulate-then-gate, writes nothing"
  - "five new selftest cases with captured RED-then-GREEN pairs, plus a captured localised-mutation negative control proving the orphan leg is load-bearing"
affects: [167-03, 167-04, 167-05, 167-06, 168]

tech-stack:
  added: []
  patterns:
    - "allowlist-constant + accumulate-then-report idiom copied from tools/catalog/codegen.py (ILLEGAL_NAME_CHARS, sorted() in failure messages, validate-before-emit ordering)"
    - "non-tautology reachability evidence: check_orphans reads only Home.md, never _Sidebar.md, with no flag/config escape hatch"
    - "code-span stripping via newline-count-preserving fence substitution and length-preserving inline-code substitution, so reported line numbers stay accurate"
    - "cmd_check reuses cmd_sidebar/cmd_links directly (accumulate return codes) rather than duplicating comparison or walking logic, following sync_to_subrepos.sh's exit_code structure"

key-files:
  created: []
  modified:
    - tools/wiki/wiki.py
    - tools/wiki/selftest.sh

key-decisions:
  - "extract_internal_links classifies link legality post-hoc by fullmatch()-ing the extracted target against the legal-stem pattern, rather than tagging legality inline during extraction — this means [[Page]] and reference-style [Text][ref] matches (whose 'target' is the whole raw match) fail the same legality check as a .md-suffixed or path-separator target, with one code path instead of three"
  - "check_page_names iterates source_dir.iterdir() directly (not the *.md-only page_files() glob) so a non-.md file or a directory is still caught as illegal, independent of the link-resolution pass"
  - "case-insensitive collision is reported with a distinct message from a fully-unresolved target, naming the case-sensitivity rule explicitly, so a contributor understands why GitHub's own read path will never surface the same failure"

requirements-completed: []

coverage:
  - id: D1
    description: "wiki.py links detects orphan pages using Home.md as the only reachability evidence set — a page linked exclusively from the generated _Sidebar.md still fails (sidebar_link_is_not_evidence, the phase's load-bearing non-tautology proof)"
    requirement: WIKI-05
    verification:
      - kind: unit
        ref: "bash tools/wiki/selftest.sh — case_orphan_exit_1 and case_sidebar_link_is_not_evidence, RED at commit 8c8e4973, GREEN at commit c9211d92"
        status: pass
    human_judgment: false
  - id: D2
    description: "wiki.py links enforces the single legal internal link form [Text](Page-Name[#anchor]); rejects .md-suffixed links, broken links, and resolves links case-sensitively"
    requirement: WIKI-05
    verification:
      - kind: unit
        ref: "bash tools/wiki/selftest.sh — case_broken_link_exit_1 and case_md_suffix_link_exit_1, RED at commit 8c8e4973, GREEN at commit c9211d92"
        status: pass
    human_judgment: false
  - id: D3
    description: "wiki.py links rejects illegal page filenames (\\ / : * ? \" < > | , .., non-.md suffix), naming the offending value and the allowed set"
    requirement: WIKI-05
    verification:
      - kind: unit
        ref: "bash tools/wiki/selftest.sh — case_illegal_filename_exit_1, RED at commit 8c8e4973, GREEN at commit c9211d92"
        status: pass
    human_judgment: false
  - id: D4
    description: "wiki.py check aggregates the sidebar-freshness and links legs unconditionally (accumulate-then-gate), reuses cmd_sidebar/cmd_links without duplicating logic, and writes nothing"
    requirement: WIKI-04
    verification:
      - kind: unit
        ref: "manual: wiki.py check against a fixture with both a stale sidebar and an orphan reports both and exits 1; _Sidebar.md byte-unchanged via cmp after the run"
        status: pass
    human_judgment: false
  - id: D5
    description: "orphan-detection leg proved load-bearing by a localised mutation (check_orphans neutered): exactly orphan_exit_1 and sidebar_link_is_not_evidence go red, the other five cases stay green, and check_orphans is restored byte-identical"
    requirement: WIKI-05
    verification:
      - kind: unit
        ref: "bash tools/wiki/selftest.sh with check_orphans returning [] unconditionally — captured non-zero exit, 2 of 7 red; restored file diffs clean against pre-mutation copy"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-08-30
status: complete
---

# Phase 167 Plan 02: Wiki Offline Integrity Legs (links + check) Summary

**`wiki.py links` walker (Home.md-only orphan detection, single-legal-link-form allowlist, case-sensitive resolution, filename legality) and `wiki.py check` aggregator — all five load-bearing offline negative cases observed RED before GREEN, plus a captured localised mutation proving the orphan leg is not decorative.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-08-30T11:48:30Z
- **Completed:** 2026-08-30T11:59:57Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments
- Authored `case_orphan_exit_1`, `case_sidebar_link_is_not_evidence`, `case_broken_link_exit_1`, `case_md_suffix_link_exit_1`, `case_illegal_filename_exit_1` in `tools/wiki/selftest.sh`, observed all five RED against a `wiki.py` with no `links` subcommand
- Implemented `wiki.py links` — `check_page_names`, `check_link_forms`, `check_orphans`, `cmd_links` — all five negative cases turned GREEN with no regression to the two wave-1 cases
- Implemented `wiki.py check` — the single offline aggregator CI and `publish` will call — reusing `cmd_sidebar`/`cmd_links` directly with accumulate-then-gate, no duplicated comparison logic
- Proved the orphan leg is load-bearing: neutered `check_orphans` to return `[]` unconditionally, observed exactly `orphan_exit_1` and `sidebar_link_is_not_evidence` go red while the other five cases stayed green, then restored the function byte-identical

## Task Commits

Each task was committed atomically:

1. **Task 1: Author the five reachability and legality negative cases and observe them RED** - `8c8e4973` (test)
2. **Task 2: Implement the links walker — orphans, link-form allowlist, filename legality** - `c9211d92` (feat)
3. **Task 3: Implement the check aggregator and prove the orphan leg is load-bearing** - `974a25dc` (feat)

_Note: Task 1 and Task 2 form the TDD RED/GREEN pair for the five new cases._

## Files Created/Modified
- `tools/wiki/selftest.sh` - added `case_orphan_exit_1`, `case_sidebar_link_is_not_evidence`, `case_broken_link_exit_1`, `case_md_suffix_link_exit_1`, `case_illegal_filename_exit_1`, registered in `CASES` (now 7 total)
- `tools/wiki/wiki.py` - added `page_stems`, `strip_code_spans`, `extract_internal_links`, `check_page_names`, `check_link_forms`, `check_orphans`, `cmd_links`, `cmd_check`; new constants `ILLEGAL_NAME_CHARS`, `LEGAL_LINK_RE`, `EXTERNAL_LINK_PREFIXES`; registered `links` and `check` in `COMMANDS` and the argparser

## Decisions Made
- `extract_internal_links` returns `(line_number, link_text, target)` for every non-external link (legal or not); legality is determined post-hoc in `check_link_forms`/`check_orphans` by `fullmatch()`-ing the target against the legal-stem pattern, so `[[Page]]` and reference-style `[Text][ref]` (captured with `link_text == target` as the whole raw match) fail the same single check as a `.md`-suffixed target — one legality gate instead of three
- `check_page_names` walks `source_dir.iterdir()` directly rather than the `*.md` glob used elsewhere, so a directory or a non-`.md` file is still caught independent of whether the links pass ever reads it
- Case-insensitive near-misses get a distinct message from a fully-unresolved target, naming the case-sensitivity rule explicitly (GitHub resolves case-insensitively and will never report this drift itself)

## Deviations from Plan

None - plan executed exactly as written. No auth gates, no blocking issues, no architectural changes.

## Issues Encountered
None.

## Load-Bearing Case: sidebar_link_is_not_evidence

Verified per the plan's requirement: the mutated fixture added `Page-Orphan.md`, then regenerated `_Sidebar.md` via `wiki.py sidebar --source-dir <fixture>` so the sidebar legitimately contains `- [Page Orphan](Page-Orphan)`, while `Home.md` was left untouched. The case asserts three things in one run: `wiki.py sidebar --check` exits 0 (the sidebar is fresh — ruling out staleness as the cause), `wiki.py links` exits 1, and stderr names `Page-Orphan`. See "Observed RED" and "Observed GREEN" below for the captured runs.

## Observed RED: orphan_exit_1, sidebar_link_is_not_evidence, broken_link_exit_1, md_suffix_link_exit_1, illegal_filename_exit_1

Captured at commit `8c8e4973`, before `wiki.py` had a `links` subcommand (`python3 wiki.py links ...` fails with argparse exit 2, "invalid choice"). Observed selftest exit code: `1`.

```
=== stale_sidebar_exit_1 ===
OK: stale_sidebar_exit_1_control exit 0
OK: stale_sidebar_exit_1 exit 1
=== sidebar_deterministic ===
OK: sidebar_deterministic_run1 exit 0
OK: sidebar_deterministic exit 0
=== orphan_exit_1 ===
ERROR: orphan_exit_1_control: expected exit 0, observed 2
ERROR: orphan_exit_1: expected exit 1, observed 2
ERROR: orphan_exit_1: stderr missing Page-Orphan
=== sidebar_link_is_not_evidence ===
ERROR: sidebar_link_is_not_evidence_control: expected exit 0, observed 2
OK: sidebar_link_is_not_evidence_sidebar_check exit 0
ERROR: sidebar_link_is_not_evidence: expected exit 1, observed 2
ERROR: sidebar_link_is_not_evidence: stderr missing Page-Orphan
=== broken_link_exit_1 ===
ERROR: broken_link_exit_1_control: expected exit 0, observed 2
ERROR: broken_link_exit_1: expected exit 1, observed 2
ERROR: broken_link_exit_1: stderr missing No-Such-Page
=== md_suffix_link_exit_1 ===
ERROR: md_suffix_link_exit_1_control: expected exit 0, observed 2
ERROR: md_suffix_link_exit_1: expected exit 1, observed 2
ERROR: md_suffix_link_exit_1: stderr missing Home.md
=== illegal_filename_exit_1 ===
ERROR: illegal_filename_exit_1_control: expected exit 0, observed 2
ERROR: illegal_filename_exit_1: expected exit 1, observed 2
ERROR: illegal_filename_exit_1: stderr missing offending filename
case | expected | observed | control | note | verdict
stale_sidebar_exit_1 | 1 | 1 | 0 | a failing --check must not rewrite the file it checks | PASS
sidebar_deterministic | 0 | 0 | 0 | two runs over an unchanged source must be byte-identical | PASS
orphan_exit_1 | 1 | 2 | 2 | orphan absent from Home.md | FAIL
sidebar_link_is_not_evidence | 1 | 2 | 2 | home-only evidence | FAIL
broken_link_exit_1 | 1 | 2 | 2 | unresolved internal link target | FAIL
md_suffix_link_exit_1 | 1 | 2 | 2 | md-suffixed internal link rejected | FAIL
illegal_filename_exit_1 | 1 | 2 | 2 | illegal filename character | FAIL
ERROR: selftest failed (5 of 7 cases red)
```

(All five new cases fail with `observed 2` here rather than a mismatched `0`/`1`, because `python3 "$WIKI_PY" links ...` could not be dispatched — `links` did not exist as a registered subcommand at this commit, so argparse itself exits 2 for "invalid choice". This is the expected RED shape for a case whose capability has not been built yet, matching wave 1's precedent.)

## Observed GREEN: orphan_exit_1, sidebar_link_is_not_evidence, broken_link_exit_1, md_suffix_link_exit_1, illegal_filename_exit_1

Captured at commit `c9211d92`, after `wiki.py links` was implemented. Observed selftest exit code: `0`.

```
=== stale_sidebar_exit_1 ===
OK: stale_sidebar_exit_1_control exit 0
OK: stale_sidebar_exit_1 exit 1
=== sidebar_deterministic ===
OK: sidebar_deterministic_run1 exit 0
OK: sidebar_deterministic exit 0
=== orphan_exit_1 ===
OK: orphan_exit_1_control exit 0
OK: orphan_exit_1 exit 1
=== sidebar_link_is_not_evidence ===
OK: sidebar_link_is_not_evidence_control exit 0
OK: sidebar_link_is_not_evidence_sidebar_check exit 0
OK: sidebar_link_is_not_evidence exit 1
=== broken_link_exit_1 ===
OK: broken_link_exit_1_control exit 0
OK: broken_link_exit_1 exit 1
=== md_suffix_link_exit_1 ===
OK: md_suffix_link_exit_1_control exit 0
OK: md_suffix_link_exit_1 exit 1
=== illegal_filename_exit_1 ===
OK: illegal_filename_exit_1_control exit 0
OK: illegal_filename_exit_1 exit 1
case | expected | observed | control | note | verdict
stale_sidebar_exit_1 | 1 | 1 | 0 | a failing --check must not rewrite the file it checks | PASS
sidebar_deterministic | 0 | 0 | 0 | two runs over an unchanged source must be byte-identical | PASS
orphan_exit_1 | 1 | 1 | 0 | orphan absent from Home.md | PASS
sidebar_link_is_not_evidence | 1 | 1 | 0 | home-only evidence | PASS
broken_link_exit_1 | 1 | 1 | 0 | unresolved internal link target | PASS
md_suffix_link_exit_1 | 1 | 1 | 0 | md-suffixed internal link rejected | PASS
illegal_filename_exit_1 | 1 | 1 | 0 | illegal filename character | PASS
OK: selftest complete (7 cases)
```

## Negative control: check_orphans neutered

`check_orphans` was temporarily replaced with `return []` unconditionally (no other change), the selftest run captured, then the function restored byte-identical (verified with `diff -q` against a pre-mutation copy) and the selftest re-run to confirm all seven cases green again.

Observed selftest exit code with `check_orphans` neutered: `1`.

```
=== stale_sidebar_exit_1 ===
OK: stale_sidebar_exit_1_control exit 0
OK: stale_sidebar_exit_1 exit 1
=== sidebar_deterministic ===
OK: sidebar_deterministic_run1 exit 0
OK: sidebar_deterministic exit 0
=== orphan_exit_1 ===
OK: orphan_exit_1_control exit 0
ERROR: orphan_exit_1: expected exit 1, observed 0
=== sidebar_link_is_not_evidence ===
OK: sidebar_link_is_not_evidence_control exit 0
OK: sidebar_link_is_not_evidence_sidebar_check exit 0
ERROR: sidebar_link_is_not_evidence: expected exit 1, observed 0
=== broken_link_exit_1 ===
OK: broken_link_exit_1_control exit 0
OK: broken_link_exit_1 exit 1
=== md_suffix_link_exit_1 ===
OK: md_suffix_link_exit_1_control exit 0
OK: md_suffix_link_exit_1 exit 1
=== illegal_filename_exit_1 ===
OK: illegal_filename_exit_1_control exit 0
OK: illegal_filename_exit_1 exit 1
case | expected | observed | control | note | verdict
stale_sidebar_exit_1 | 1 | 1 | 0 | a failing --check must not rewrite the file it checks | PASS
sidebar_deterministic | 0 | 0 | 0 | two runs over an unchanged source must be byte-identical | PASS
orphan_exit_1 | 1 | 0 | 0 | orphan absent from Home.md | FAIL
sidebar_link_is_not_evidence | 1 | 0 | 0 | home-only evidence | FAIL
broken_link_exit_1 | 1 | 1 | 0 | unresolved internal link target | PASS
md_suffix_link_exit_1 | 1 | 1 | 0 | md-suffixed internal link rejected | PASS
illegal_filename_exit_1 | 1 | 1 | 0 | illegal filename character | PASS
ERROR: selftest failed (2 of 7 cases red)
```

The mutation was exactly localised — precisely `orphan_exit_1` and `sidebar_link_is_not_evidence` went red, the other five cases (including the two wave-1 cases) stayed green — proving the orphan leg is load-bearing rather than decorative. After restoration, `bash tools/wiki/selftest.sh` returned to exit `0` with all seven cases `PASS`, and `diff -q tools/wiki/wiki.py <pre-mutation copy>` reported no difference (verified via commit `974a25dc`, which contains only the `cmd_check`/argparser addition, not the transient mutation).

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `tools/wiki/wiki.py`'s `COMMANDS` dispatch map now carries `sidebar`, `links`, `check`; plan 167-03 adds `publish` and `_git` without needing to touch any function added here.
- `cmd_check` is the single entry point plan 167-03's `publish` must call before touching the remote (per Pattern 3 / T-167-01's mitigation) — it is already structured to be called with no wiki present (both legs are purely offline).
- **WIKI-04 is still only partially delivered** — this plan adds the `check` aggregator leg, but `drift_detected_exit_1`, `hand_edit_overwritten`, `idempotent_head_unchanged` and `deleted_page_removed` remain in plans 167-03/167-05/167-06. Do not mark WIKI-04 complete until all of those plans have a SUMMARY.md.
- **WIKI-05 is still only partially delivered** in the sense that this plan carries all of its enumerated negative cases (`orphan_exit_1`, `sidebar_link_is_not_evidence`, `broken_link_exit_1`, `md_suffix_link_exit_1`, `illegal_filename_exit_1`), but per the plan frontmatter WIKI-05 also spans 167-04/167-05 — do not mark it complete in REQUIREMENTS.md until those plans land too.
- No blockers for the next wave.

## Self-Check: PASSED

- FOUND: tools/wiki/wiki.py
- FOUND: tools/wiki/selftest.sh
- FOUND: 8c8e4973
- FOUND: c9211d92
- FOUND: 974a25dc

---
*Phase: 167-wiki-bootstrap-in-repo-source-sync-drift-check*
*Completed: 2026-08-30*
</content>
