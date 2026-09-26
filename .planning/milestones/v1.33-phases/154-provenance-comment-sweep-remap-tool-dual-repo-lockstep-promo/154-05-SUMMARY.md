---
phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
plan: "05"
subsystem: tooling
tags: [citation-remap, difflib, line-map, idempotency, range-shrink, fail-closed, tdd, anti-vacuity]

requires:
  - phase: 154-01
    provides: "FW_PRE_SHA=8695ee5 / APP_PRE_SHA=6bfa645 — the pre-sweep anchors the tool reads its `old` side from, and the clean-tree baselines"
  - phase: 154-04
    provides: ".planning/v1.33/sweep-citation-manifest.jsonl (13,692 records, 14-field schema) as the input contract, and citation_paths.py as the SINGLE shared path resolver this tool imports rather than forks"
provides:
  - ".planning/v1.33/tools/remap_citations.py — the citation remap tool: a difflib(autojunk=False) line map, independently-mapped range endpoints, a fixed-point/identity/oracle write predicate, positional record-to-span binding, argv-only repo root, dry-run default, house 0/1/2 exit contract"
  - ".planning/v1.33/tools/test_remap_citations.py — 21 legs, including two ANTI-VACUITY legs that prove the shrink and idempotency proofs actually discriminate against the wrong implementations"
  - ".planning/v1.33/tools/fixtures/ — the chained old/new blob pair (two separated deletion blocks), manifest_min.jsonl, manifest_empty.jsonl, doc_min.md"
  - "citation_paths.FIXTURE_INCLUSIVE_FALLBACK_REASON — the shared constant that lets the T-154-13 guard tell a legitimate fixture citation from a colliding one without an inline string that would fail open"
  - "Measured: the finished tool dry-run over the real 13,692-record manifest — 13,677 examined / 1,228 documents / 129 target files / 0 rewritten / 10,168 fixed points / 0 documents changed"
affects: [154-12, 159]

tech-stack:
  added: []
  patterns:
    - "Bind a record to a citation POSITIONALLY within a (path, variant) group, never by the integer in the text — a line number is not a unique identifier within a line"
    - "Make the round-trip oracle BE the write predicate: one design yields idempotency, the oracle and resumability, and breaking it breaks all three"
    - "Every proof gets a paired anti-vacuity leg that runs the WRONG implementation and asserts it fails — a green test that a blind implementation also passes proves nothing"
    - "Cross-check a stdlib algorithm against an independently-parsed second implementation on a REAL file, because the hazard (autojunk) provably does not reproduce on synthetic fixtures"
    - "Dry-run by default for any tool whose application is scheduled for a later phase — the schedule is enforced by the CLI, not by discipline"

key-files:
  created:
    - .planning/v1.33/tools/remap_citations.py
    - .planning/v1.33/tools/test_remap_citations.py
    - .planning/v1.33/tools/fixtures/citations_chained_old.txt
    - .planning/v1.33/tools/fixtures/citations_chained_new.txt
    - .planning/v1.33/tools/fixtures/manifest_min.jsonl
    - .planning/v1.33/tools/fixtures/manifest_empty.jsonl
    - .planning/v1.33/tools/fixtures/doc_min.md
  modified:
    - .planning/v1.33/tools/citation_paths.py
    - .planning/phases/154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo/deferred-items.md
    - .planning/ROADMAP.md
    - .planning/STATE.md

key-decisions:
  - "Records are bound to citation spans POSITIONALLY within a (cited path, variant) group, not by the integer found in the text. The chained fixture caught the number-keyed form drifting a colon_list `10,15` to `10,10` on run 2: after run 1 the `15` is the already-rewritten value of the record for old line 20, while a different record was recorded for old line 15. The generator appends records inside a `finditer` loop, so the manifest's record order for a group IS the document order of that group's spans; a length mismatch is counted and skipped, never guessed at"
  - "The fixed-point check is evaluated over the WHOLE match, not per element. A colon_list whose elements have all been rewritten is a fixed point as a whole even though no single element still sits at its recorded pre-sweep number. The three-check ORDER research specifies is preserved; only the granularity of check 1 is stated"
  - "The T-154-13 fixture guard is a COLLISION guard, not a fixture-path ban. The real manifest legitimately carries 7 records whose resolved path is fixture-shaped, because some documents cite a planted fixture by name and it is the only candidate carrying that basename. A blanket ban made the tool exit 1 on the real corpus. Legitimate iff the citation as written is itself fixture-shaped, or the record resolved through citation_paths' explicitly-labelled fixture-inclusive fallback — recognised via a shared CONSTANT added to citation_paths.py, because an inline string copy would fail open the day the reason is reworded"
  - "The pre-sweep blob is read as `git show <sha>:./<path>` — the `./` prefix makes the path CWD-relative, so one code path serves both production (each root its own repository) and the unit test (a throwaway repo whose roots are plain sub-directories). No test-only escape hatch exists, so the tested path IS the production path"
  - "`--pre-sweep-sha` on argv BEATS the manifest header's recorded `pre_sweep_shas`. The header is a legitimate last resort — it is data inside the declared input, not a path derived from the module's location — but argv must win, because Phase 159 maps a COMPOSITE pre-154-to-post-158 diff whose old side is no revision any manifest was generated at. Finding D3 shows this is not hypothetical"
  - "A violation aborts the WHOLE run: every document is planned before any byte is written, so an oracle mismatch anywhere means nothing is written anywhere, including the records that would have succeeded"
  - "citation_paths.py was edited (additively) rather than string-matched around. Proven behaviour-identical: 0 resolution differences over all 803 distinct cited strings in the manifest, and plan 04's 26 legs plus the --self-check remain green"
  - "The manifest header is NOT the authority for the pre-sweep content of a file the working tree had already modified — see finding D3. The tool's fixed-point-first ordering turned that stale anchor into a safe no-op instead of a wrong rewrite, which is the property SWEEP-11 exists to buy"
  - "ROADMAP.md and STATE.md hand-edited only; roadmap.update-plan-progress and the requirements verbs were NOT run, per this milestone's binding constraint carried from plans 01-04"

patterns-established:
  - "Run the finished tool against the REAL corpus in dry-run before declaring it done. Two defects survived a green 21-leg synthetic suite and were caught in the first real dry run: the blanket fixture ban (exit 1 on 7 legitimate rows) and, earlier, the colon_list drift"
  - "When a hazard provably does not reproduce synthetically, say so and test it on a real file instead of shipping a synthetic leg that proves nothing — the 500-line synthetic autojunk fixture showed ZERO divergence where two real files diverge"
  - "State the expected map as a module constant in the test, so a fixture edit that silently changes the map fails loudly instead of weakening every leg below it"

requirements-completed: [SWEEP-11]

coverage:
  - id: D-09
    covered_by: "test_here_is_absent_from_the_module, test_repo_root_is_a_required_positional_and_manifest_has_no_default, test_exits_nonzero_on_empty_input, test_exits_nonzero_when_no_record_is_actionable, test_unloadable_manifest_exits_2, test_missing_resolved_target_exits_1"
  - id: D-10
    covered_by: "test_dry_run_writes_nothing, test_the_tool_is_not_applied_to_any_real_planning_document"
  - id: T-154-17
    covered_by: "test_oracle_violation_exits_1_and_writes_nothing"
  - id: T-154-18
    covered_by: "test_difflib_map_agrees_with_git_diff_u0, test_autojunk_true_would_corrupt_the_map_on_a_real_file"
  - id: T-154-19
    covered_by: "test_chained_map_has_a_chain (runs before the idempotency legs), test_a_blind_remapper_drifts_along_the_chain"
  - id: T-154-20
    covered_by: "test_here_is_absent_from_the_module, test_exits_nonzero_on_empty_input"
  - id: T-154-21
    covered_by: "test_the_tool_is_not_applied_to_any_real_planning_document, test_dry_run_writes_nothing"

metrics:
  duration: "~40 minutes"
  completed: 2026-08-23
  tasks: 2
  commits: 3
  files_created: 7
  files_modified: 2
  tests_added: 21
  tool_lines: 1010
  test_lines: 758

status: complete
---

# Phase 154 Plan 05: Remap Tool — difflib Line Map, Range Shrink, Chained-Map Idempotency Summary

`remap_citations.py` exists, is proven on synthetic diffs for all three named
properties, and was **not applied** — and the chained fixture earned its keep twice by
catching two real defects a smaller fixture would have passed.

## What was built

| Artifact | Lines | What it carries |
|---|---|---|
| `.planning/v1.33/tools/remap_citations.py` | 1010 | the tool |
| `.planning/v1.33/tools/test_remap_citations.py` | 758 | 21 legs |
| `fixtures/citations_chained_old.txt` | 20 | pre-sweep side |
| `fixtures/citations_chained_new.txt` | 15 | post-sweep side |
| `fixtures/manifest_min.jsonl` | 1 header + 8 records | the canonical valid input |
| `fixtures/manifest_empty.jsonl` | 1 header + 0 records | the exit-2 leg |
| `fixtures/doc_min.md` | 9 | the citing document, all five variants |

## The three properties, as measured

### 1. Range shrink, not translate

One fixture pair carries both the chain **and** research's measured shrink reference case,
because five lines are deleted in two separated blocks (old 4-5 and old 11-13) rather than
one:

```
map: {1:1, 2:2, 3:3, 4:None, 5:None, 6:4, 7:5, 8:6, 9:7, 10:8,
      11:None, 12:None, 13:None, 14:9, 15:10, 16:11, 17:12, 18:13, 19:14, 20:15}

map_range(m, 3, 18, 20) == (3, 13, False)     old span 16 -> new span 11, shrank by 5
```

The span-changed assertion is what discriminates. `test_a_constant_offset_implementation_fails_the_shrink_leg`
runs the wrong implementation and measures `(-2, 13)` — span preserved at 16 — so the shrink
leg is proven to be more than a numeric coincidence.

Both endpoints are mapped by the same `map_point` with different clamp directions (start
forward, end backward). No branch computes "shrink"; it falls out of the differing
accumulated deletion offset at the two endpoints, exactly as REMAP-03 requires.

### 2. Idempotency, on a chain that is asserted rather than assumed

`test_chained_map_has_a_chain` runs **before** any idempotency assertion and proves the
fixture contains what the proof needs:

- the chain `map[15] = 10` **and** `map[10] = 8` (with `8 != 10`);
- exactly two maximal non-surviving runs, `[4, 5]` and `[11, 12, 13]`, separated by five
  surviving lines.

`test_a_blind_remapper_drifts_along_the_chain` then measures the drift a blind
implementation produces on that same map — `[10, 8, 6]` — reproducing research's
`:15 -> :10 -> :8 -> :6` exactly. Only after both does the tool get tested:

| run | records examined | rewritten | fixed point | retarget | document |
|---|---|---|---|---|---|
| 1 | 8 | 7 | 0 | 1 | changed |
| 2 | 8 | 0 | 7 | 1 | **byte-identical to run 1** |
| 3 | 8 | 0 | 7 | 1 | **byte-identical to run 1** |

`test_idempotent_range_span_is_stable` covers the harder case — a range whose *both*
endpoints chain (`map[10]=8` with `map[8]=6`, and `map[20]=15` with `map[15]=10`). Old
`10-20` becomes `8-15` on run 1 and stays `(8, 15, span 8)` on runs 2 and 3; the same test
measures that a blind implementation would have gone on to `6-10`.

### 3. Fail closed, never fail open

| leg | outcome |
|---|---|
| `manifest_empty.jsonl` (header only) | **exit 2**, "parsed to ZERO records" |
| every record `retarget: true` | **exit 2**, "NONE is actionable" |
| manifest absent / not JSON / root absent | **exit 2** |
| oracle mismatch | **exit 1**, nothing written *anywhere* |
| `target_file_resolved` missing on disk | **exit 1** |
| `planning_file` carrying `..` | **exit 1**, nothing written |
| `grep -c '_HERE'` / `grep -c '__file__'` on the tool | **0 / 0** |
| `grep -c 'autojunk=False'` | **4** |
| no `--apply` | dry run; the citing document, the target file and `git status` all unchanged |

The repo root is a required positional argument. `--manifest` has no default at all — an
absent manifest is exit 2, never a derived path — which is the specific correction to the
named analog `check_ledger.py`, whose every input has a location-derived default.

## `autojunk=False`: measured, not asserted

The flag is load-bearing and the measurement is the interesting part:

| corpus | lines | survivors `autojunk=False` | survivors `autojunk=True` | diverges? |
|---|---|---|---|---|
| `firestarter/src/proms/eeprom_28c.cpp` | 920 | 812 | **810** | yes, old 412-413 |
| `firestarter_app/firestarter/cli_handlers.py` | 2694 | 2537 | **2535** | yes |
| `firestarter/src/firestarter.cpp` | 400 | 377 | 377 | no |
| synthetic 500-line fixture, 8 popular elements | 500 | 489 | 489 | **no** |

The synthetic fixture built specifically to trigger the hazard did **not** diverge. That is
research Pitfall 2's point precisely — the bug hides on small fixtures — so the leg is a
real-file measurement (`test_autojunk_true_would_corrupt_the_map_on_a_real_file`) that
skips with a stated reason if the firmware sub-repo is absent, rather than a synthetic leg
that would pass either way.

`test_difflib_map_agrees_with_git_diff_u0` adds an independent oracle: a second
implementation parses `git diff -U0` `@@` hunks into the same shape and the two maps are
asserted **exactly equal** over a real 498-line file with two 6-line deletions. The test
picks its own deletion windows by requiring every line in them to be unique in the file, so
the two diff algorithms cannot legitimately disagree about the alignment.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `colon_list` elements drifted on run 2 — number-keyed record lookup**
- **Found during:** Task 2, the first end-to-end run of the chained fixture.
- **Issue:** run 1 correctly rewrote `chained_demo.cpp:15,20` to `:10,15`. Run 2 then
  produced `:10,10`. The `15` in the rewritten text is the already-rewritten value of the
  record for old line 20, but a lookup keyed on the integer bound it to the *other* record —
  the one recorded for old line 15 — whose identity check then passed (`15 == 15`) and whose
  oracle also passed. Both guards were satisfied and the write was still wrong: **a line
  number is not a unique identifier within a line.**
- **Fix:** records are bound to spans **positionally** within a `(cited path, variant)`
  group, and check 1 (fixed point) is evaluated over the **whole match** rather than per
  element. Every record of a line takes part in the binding, including inert ones, because
  dropping an inert row would misalign every later element of its group. A length mismatch
  between records and spans is counted and skipped, never guessed at.
- **Regression leg:** `test_colon_list_element_does_not_drift`, asserting `:10,15` across
  runs 1, 2 and 3.
- **Files modified:** `remap_citations.py` (`_associate`, `remap_document`, `is_fixed_point`).
- **Commit:** `7fedf886`

**2. [Rule 1 - Bug] The T-154-13 fixture guard rejected 7 legitimate records**
- **Found during:** Task 2, the first dry run against the real 13,692-record manifest.
- **Issue:** the guard treated *any* fixture-shaped `target_file_resolved` as a collision and
  exited 1 on the real corpus. Measured, the manifest carries **7** such records across 4
  fixture files (`planted_log_in_window.cpp`, `planted_ifdef_in_predicate.h`,
  `planted_constants_value_drift.h`, `planted_json_parser_key_string_drift.c`), and all 7 are
  legitimate: the document cites the planted fixture **by name**, and `citation_paths`
  resolved it either by `suffix` (the citation itself names the fixture path) or through its
  explicitly-labelled fixture-inclusive fallback, which runs only when no non-fixture
  candidate carries the basename at all.
- **Fix:** the guard now flags only a genuine **collision** — a fixture-shaped resolved path
  reached from a non-fixture-shaped citation *and* not via the declared fallback. The fallback
  is recognised through a new shared constant `citation_paths.FIXTURE_INCLUSIVE_FALLBACK_REASON`
  rather than an inline string copy, which would have failed **open** the day that reason was
  reworded. The PASS line reports the legitimate count so it cannot be silently zero.
- **Files modified:** `remap_citations.py`, `citation_paths.py`.
- **Commit:** `7fedf886`

**3. [Rule 3 - Blocking] `citation_paths.py` (plan 04's artifact) edited additively**
- **Issue:** deviation 2's fix needs the fallback reason as a shared constant; a string
  literal duplicated in the remapper is a fail-open seam.
- **Fix:** `FIXTURE_INCLUSIVE_FALLBACK_REASON` defined once in `citation_paths.py` and used at
  its single emission site. The string value is byte-identical to what the committed manifest
  already carries.
- **Proven behaviour-identical:** `index.resolve()` compared across `HEAD` and the edited
  module over **all 803 distinct `target_file_cited` strings** in the manifest — **0
  differences**. Plan 04's 26 legs pass and `citation_paths.py --self-check` still reports
  `PASS: 8 probes ... index of 171 candidate swept files`.
- **Commit:** `7fedf886`

**4. [Rule 1 - Bug] `--pre-sweep-sha` did not override the manifest header**
- **Issue:** the header's recorded `pre_sweep_shas` won over a bare `--pre-sweep-sha` argument,
  so `manifest_min.jsonl`'s deliberate all-zeros placeholder made `git show` fail and the tool
  exit 2 in its own test harness.
- **Fix:** `ShaResolver` with a stated precedence — `--pre-sweep-sha NAME=SHA`, then a bare
  `--pre-sweep-sha SHA`, then the header. Argv must win: Phase 159 maps a composite diff whose
  old side is no revision any manifest was generated at.
- **Commit:** `7fedf886`

### Deferred (logged to `deferred-items.md`, not fixed here)

- **D3 — the manifest's `source_text` side is the WORKING TREE, not `pre_sweep_shas`.** The
  generator reads every `source_text` from disk while the header records each sub-repo's
  `HEAD`. For the two files plan 03 had already modified in `firestarter_app`'s working tree
  those differ: `6bfa645:./tests/test_dispatch_mirror.py` is 222 lines, the working tree is
  362, and old lines >= 23 shift by **+5**. All 7 manifest records targeting that file were
  correctly recognised as **fixed points** and the tool was a safe no-op. Phase 159's app-side
  old anchor is the plan-12 commit, not `6bfa645` — which is exactly why `--pre-sweep-sha` is
  an argv argument. Out of scope: fixing it means regenerating plan 04's manifest, and D-11
  reserves that sub-repo's commit for plan 12.
- **D4 — 15 manifest records against `.planning/STATE.md` no longer bind.** All 15
  "binding is ambiguous" residues in the real dry run are STATE.md, whose lines drift on every
  plan's `state_updates`. The tool names each one and refuses rather than guessing. Whether to
  regenerate the manifest at Phase 159 or exclude STATE.md from the corpus is a Phase 159 /
  SWEEP-12 decision.

## Scale check: the finished tool against the real corpus, dry-run only

Run as a measurement, writing nothing:

```
PASS [DRY RUN (no bytes written; pass --apply)]: 13677 record(s) examined across
1228 document(s) and 129 target file(s); 0 rewritten, 10168 already at their fixed
point, 0 flagged retarget, 0 not at their recorded line, 3509 skipped as unreadable,
15 unmatched in their document; 7 record(s) legitimately cite a planted fixture by
name; 0 document(s) would change.        (2.25 s, exit 0)
```

The accounting closes exactly: `10168 + 3509 = 13677` examined, and `13692 - 13677 = 15`
unmatched. The `3509` unreadable is `3502` rows whose `text_status` is not `read` (2,978
unresolved + 259 rejected + 255 past-EOF + 10 ambiguous), **minus** the 5 of those that fell
inside the 15 unmatched STATE.md groups, **plus** 12 range rows whose *end* endpoint is past
EOF while the start read fine — a class the header's `by_text_status` block does not count
because it keys on `text_status` alone.

**0 rewritten and 0 documents changed is the correct pre-sweep answer**: the sub-repos are
unswept, so old and new coincide for 169 of the 171 candidate files and every readable
citation is already at its fixed point. The tool is a no-op before the sweep, which is what
makes it safe to keep in the tree between now and Phase 159.

## Built, not applied

| check | result |
|---|---|
| dry run is the default; `--apply` required | yes, asserted by `test_dry_run_writes_nothing` |
| citation-bearing `.planning/` documents modified outside `.planning/v1.33/` | **none** |
| `git diff --name-only -- .planning` outside `v1.33/` and `phases/154-` | `.planning/config.json` only |
| `firestarter` working tree | clean |
| `firestarter_app` working tree | plan 03's 2 modified test modules + 4 new fixtures + 7 pre-existing untracked files, **all intact and uncommitted** |

`.planning/config.json` is the GSD harness's own `_auto_chain_active: false -> true` flag, set
by `/gsd-execute-phase --auto`. It is **not** citation-bearing — verified absent from all
1,228 `planning_file` values in the manifest — so the plan's raw
`git diff --name-only -- .planning` verify line reads 1 while its *intent* holds exactly.
`test_the_tool_is_not_applied_to_any_real_planning_document` asserts the intent directly:
the intersection of the modified set with the manifest's citation-bearing set, excluding
`.planning/v1.33/`, is empty — and it asserts the citation-bearing set has more than 100
entries first, so the leg cannot pass by being vacuous.

## Verification

```
python3 -m pytest .planning/v1.33/tools/test_remap_citations.py -o addopts="" -q
  -> 21 passed in 1.89s

python3 -m pytest .planning/v1.33/tools/test_build_citation_manifest.py \
                  .planning/v1.33/tools/test_remap_citations.py -o addopts="" -q
  -> 47 passed in 2.60s        (plan 04's 26 legs unaffected by the citation_paths edit)

python3 .planning/v1.33/tools/citation_paths.py --fw-root /workspaces/firestarter \
        --app-root /workspaces/firestarter_app --self-check
  -> PASS: 8 probes, all resolved to their expected class against an index of 171
     candidate swept files.

grep -c '_HERE'        remap_citations.py -> 0
grep -c '__file__'     remap_citations.py -> 0
grep -c 'autojunk=False' remap_citations.py -> 4
grep -c 'fixtures/\*\*'  remap_citations.py -> 0
grep -c 'tempfile.mkstemp' test_remap_citations.py -> 0
named-test grep (9 required names)                 -> 9

remap_citations.py /workspaces --manifest fixtures/manifest_empty.jsonl -> exit 2
```

## Requirements

- **SWEEP-11 — fully discharged.** The tool is built; range shrink, chained-map idempotency
  and the fail-closed contract are each proven by a named test against committed synthetic
  fixtures, with the chain itself asserted before idempotency and two anti-vacuity legs
  proving the proofs discriminate; and the tool is proven not applied.

## Notes for Phase 159 (REMAP-01..05)

1. Pass `--pre-sweep-sha firestarter=<composite-old-sha> --pre-sweep-sha firestarter_app=<plan-12-commit>`.
   Do **not** rely on the manifest header for the app side — see finding D3.
2. Expect a `retarget` count > 0 once plan 12 flips D-08's subset; those records are reported
   and counted, never written, and their new targets are hand-chosen.
3. `.planning/STATE.md`'s 15 stale bindings will need either a manifest regeneration
   immediately before the remap or an explicit corpus exclusion — see finding D4.
4. A violation aborts everything. If the run exits 1, nothing was written, so the fix-and-rerun
   loop is safe; and a partially-applied run resumes correctly, because already-correct records
   are recognised as fixed points rather than re-shifted.

## Self-Check: PASSED

All 7 created files exist on disk; both modified files carry the changes; all 3 commits
(`7fedf886`, `39455a8c`, `0502cc28`) are present in `git log`.
