---
phase: 174-blast-radius-invariance-harness
plan: 04
subsystem: testing
tags: [dedup_fingerprint, devtest-issue-corpus, part-number-delta, resolve_chip, gh-cli, anti-vacuity, drift-gate]

requires:
  - phase: 174-blast-radius-invariance-harness (plans 01, 02)
    provides: "report_shapes.py scaffolding (build_shape_from_step_specs, SHAPE_IDS/FROZEN_HASHES), the sixteen-shape frozen table"
provides:
  - "tests/fixtures/devtest_issue_corpus.json: the committed 26-row filed [dev test] issue history (GATE-05), each row carrying its steps/run_counts/coverage_tag as data and its filed_hash reproduced through the real dedup_fingerprint"
  - "tools/build_devtest_issue_corpus.py: generator enumerating henols/firestarter_prom by the [dev test] title prefix, one anchored regex, validate-before-emit"
  - "tests/test_devtest_issue_corpus.py: 26-of-26 live reproduction gate, D-06 four-chip coverage, both real dedup groups asserted by name, anti-vacuity trio"
  - "tests/fixtures/part_number_delta.json: the committed raw-token to part_number delta artifact (GATE-04), whole-database aggregate plus 26 per-issue rows, measured through resolve_chip + get_eprom_config"
  - "tools/measure_part_number_delta.py: generator for the delta artifact, --issues fail-closed input override"
  - "tests/test_part_number_delta_drift.py: four-leg drift gate, absolute aggregate assertions, planted nonexistent-chip-token anti-vacuity leg"
affects: ["174-05", "177 (read-back gating)", "179 (UV run_count collapse)", "181 (canonical naming, RPT-F1)"]

actuals:
  tokens: 64000
  tasks: 3
  commits: 6

tech-stack:
  added: []
  patterns:
    - "Solve-by-trial discriminator tag recovery: try both candidate coverage_policy values against the real dedup_fingerprint and record which one reproduces, rather than re-deriving the tag from schema fields that don't exist for older reports"
    - "Committed step-vector-as-data corpus row: steps/run_counts/coverage_tag committed as JSON data, fed to the SAME build_shape_from_step_specs builder every other shape in this phase uses -- no report deserializer, no issue-body parsing at test time"
    - "Repo-local drift-gate four-leg shape (existence+banner, absolute aggregate, byte-identical regeneration, planted-input fail-closed) with the sibling-repo skip markers deliberately removed"

key-files:
  created:
    - firestarter_app/tools/build_devtest_issue_corpus.py
    - firestarter_app/tests/fixtures/devtest_issue_corpus.json
    - firestarter_app/tests/test_devtest_issue_corpus.py
    - firestarter_app/tools/measure_part_number_delta.py
    - firestarter_app/tests/fixtures/part_number_delta.json
    - firestarter_app/tests/test_part_number_delta_drift.py
    - .planning/phases/174-blast-radius-invariance-harness/evidence/174-04-issue-corpus.txt
    - .planning/phases/174-blast-radius-invariance-harness/evidence/174-04-delta-drift.txt
  modified: []

key-decisions:
  - "D-06's four-chip reproduction reduction is fully superseded: this plan reproduces all 26 filed hashes (not 27 -- the count is measured by title, since the dev-test label covers only 15 of 26), correcting 174-RESEARCH.md's 'D-06's four reproduction targets -- feasibility measured' section, which had recorded all four (sst27sf512, m27c512, at28c256, w27e257) as UNMEASURED/not-reproduced-this-session. The cause named there -- reading a step's fingerprint as an object -- is exactly the bug this plan avoids: the fenced JSON's fingerprint field is a bare classification STRING, and reading it as a string reproduces 26 of 26."
  - "The repeat/coverage discriminator-tag split measured this session is 17 rows needing neither tag, 1 needing only the degraded repeat marker, 3 needing only the coverage marker, and 5 needing both -- not the plan's stated 16/1/3/6. All 26 rows still reproduce their filed hash exactly; the discrepancy is issue gh#41 (w27c512, FAIL, filed 2026-08-22, host 3.0.0b27), which carries per-step run_count==2 (not the degraded ==1) for every _REPEAT_POLICY_OPS op and a full-device-sized write with no write_coverage description, yet its filed dedup_fingerprint reproduces with BOTH tags empty. This is reported as a finding per the plan's measurement-discipline instruction, not routed around -- no acceptance criterion in this plan asserts the 16/1/3/6 split numerically, so nothing was changed to force it."
  - "The delta artifact's lowercase-form published-proxy aggregate key is named part_numbers_not_lowercase_published_proxy (the plan names its value, 732/746, but does not fix a literal key name) -- chosen to read unambiguously as 'the published number, not the measurement' per D-15."
  - "measure_part_number_delta.py's validate() rejects a filed-issue row whose raw_token resolves to no chip in the shipped database (Rule 2 addition, see Deviations) -- both a genuine data-quality invariant (every filed issue names a real, testable chip) and the mechanism the plan's Task 3 planted-input anti-vacuity leg needs to observe a real RED."

patterns-established:
  - "A committed corpus's per-row discriminator tags are recovered by SOLVING against the real hash function (try both candidates, keep the one that reproduces) rather than re-deriving them from schema fields a report's own JSON never stored plainly."

requirements-completed: [GATE-04, GATE-05]

coverage:
  - id: D1
    description: "All 26 filed [dev test] issues are committed as a corpus row (issue, chip, embedded 12-hex, steps, run_counts, coverage_tag), each reproducing its filed dedup_fingerprint through the real hash function on a real report"
    requirement: "GATE-05"
    verification:
      - kind: unit
        ref: "tests/test_devtest_issue_corpus.py#test_filed_fingerprint_reproduces_through_the_real_dedup_fingerprint (26 parametrized cases)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The four D-06-named chips (m27c512, sst27sf512, at28c256, w27e257) are covered by both their dedicated builder shape (from plan 174-02) and a corpus reproduction row; both real dedup groups (00e121446ceb N=3, 334c3fa198bf N=2) are asserted by name and proven the only groups of size >=2"
    requirement: "GATE-05"
    verification:
      - kind: unit
        ref: "tests/test_devtest_issue_corpus.py#test_d06_named_chips_are_covered_by_dedicated_corpus_rows"
        status: pass
      - kind: unit
        ref: "tests/test_devtest_issue_corpus.py#test_at28c256_three_member_dedup_group_00e121446ceb"
        status: pass
      - kind: unit
        ref: "tests/test_devtest_issue_corpus.py#test_at28c256_two_member_dedup_group_334c3fa198bf"
        status: pass
      - kind: unit
        ref: "tests/test_devtest_issue_corpus.py#test_only_two_dedup_groups_have_n_gte_2"
        status: pass
    human_judgment: false
  - id: D3
    description: "The corpus reproduction gate and its generator are seen RED against a planted verdict flip, a planted classification flip, and two fail-closed loader legs (missing path, unparsable JSON)"
    requirement: "GATE-05"
    verification:
      - kind: unit
        ref: "tests/test_devtest_issue_corpus.py#test_planted_verdict_flip_reddens_the_gate"
        status: pass
      - kind: unit
        ref: "tests/test_devtest_issue_corpus.py#test_planted_classification_flip_reddens_the_gate"
        status: pass
      - kind: unit
        ref: "tests/test_devtest_issue_corpus.py#test_loader_raises_for_nonexistent_path"
        status: pass
      - kind: unit
        ref: "tests/test_devtest_issue_corpus.py#test_loader_raises_for_non_json_file"
        status: pass
    human_judgment: false
  - id: D4
    description: "The raw-CLI-token to part_number delta is measured through resolve_chip + get_eprom_config over the shipped 746-row database, committed as a script-generated artifact carrying the whole-database aggregate (746 rows/59 vendors/677 distinct part_numbers/234 comma-containing/953 aliases/942 differ/11 match/514 comma-joined/16 not-implemented/0 not-found/732 lowercase-proxy) plus a per-issue row for all 26 filed issues, all with token != part_number"
    requirement: "GATE-04"
    verification:
      - kind: unit
        ref: "tests/test_part_number_delta_drift.py#test_aggregate_numbers_are_asserted_absolutely_not_only_for_drift"
        status: pass
      - kind: integration
        ref: "tools/measure_part_number_delta.py --check"
        status: pass
    human_judgment: false
  - id: D5
    description: "The delta artifact is byte-stable under regeneration and its drift gate is seen RED against a planted nonexistent-chip-token corpus row, proving validate-before-emit"
    requirement: "GATE-04"
    verification:
      - kind: unit
        ref: "tests/test_part_number_delta_drift.py#test_codegen_produces_byte_identical_output"
        status: pass
      - kind: unit
        ref: "tests/test_part_number_delta_drift.py#test_planted_nonexistent_chip_token_fails_closed_and_writes_nothing"
        status: pass
    human_judgment: false

duration: 65min
completed: 2026-09-03
status: complete
---

# Phase 174 Plan 04: Filed-Issue Corpus and Part-Number Delta Summary

**A 26-row filed `[dev test]` issue corpus (script-generated via `gh`, every row reproducing its embedded `dedup_fingerprint` through the real hash function) and a whole-database `resolve_chip` delta artifact (746 rows, 953 aliases, 942 token/part_number mismatches, 514 comma-joined resolutions) both committed, drift-tested, and seen RED on a planted mutation.**

## Performance

- **Duration:** 65 min
- **Completed:** 2026-09-03
- **Tasks:** 3 (all `type="auto" tdd="true"`)
- **Files modified:** 8 (6 created in `firestarter_app`, 2 evidence transcripts created in the meta repo)

## Accomplishments

- Built `tools/build_devtest_issue_corpus.py`, enumerating `henols/firestarter_prom` by the bracketed `[dev test]` TITLE prefix (never the `dev-test` label, measured to cover only 15 of 26), with one anchored regular expression closed to three verdict literals and `json.loads`-only fenced-block extraction.
- **All 26 filed issues reproduce their embedded `dedup_fingerprint` through the real function on a real `DiagnosticReport`** -- this corrects `174-RESEARCH.md`'s "D-06's four reproduction targets -- feasibility measured" section, which recorded all four named chips (sst27sf512, m27c512, at28c256, w27e257) as UNMEASURED that session. The cause is exactly what that section warned against inverted: a step's `fingerprint` value in the fenced JSON is a bare classification STRING, not an object with a classification key -- read as an object, 0 of 26 reproduce; read as a string, 26 of 26 do. This widens the reproduction assertion from four hand-picked chips to the whole corpus, per the operator's 2026-09-03 ratification recorded in `174-CONTEXT.md` D-06; the four named chips keep their dedicated `report_shapes.py` builder shapes from plan 174-02 unchanged.
- Recovered each row's two per-report discriminator tags (`repeat_policy_tag`, `coverage_tag`) by SOLVING against the real hash function rather than re-deriving them from schema fields no historical report stores plainly -- `run_counts` (when the body's steps carry the key) are stamped and the real `repeat_policy_tag` is read off the built report; `coverage_tag` is solved by trying both candidate `coverage_policy` values and keeping whichever reproduces the filed hash.
- Both real `count_agreeing` dedup groups are proven from the corpus and asserted by name: `00e121446ceb` spans gh#20/gh#21/gh#32 (at28c256, N=3), `334c3fa198bf` spans gh#39/gh#40 (at28c256, N=2), and a third test proves these are the ONLY groups of size two or more in the 26-row corpus.
- Anti-vacuity trio seen RED: a planted verdict flip (gh#47 `id` step OK->BAD: filed `f9dbc31dcd27`, mutated `5e555011e0d9`), a planted classification flip (gh#47 `write` step `indeterminate`->`match`: filed `f9dbc31dcd27`, mutated `07aa99a87c4f`), and two fail-closed loader legs (missing path, unparsable JSON), both transcribed in the module docstring and in the evidence file.
- Built `tools/measure_part_number_delta.py`, measuring through `chip_resolver.resolve_chip` (support-status verdict) plus `EpromDatabase.get_eprom_config`'s raw config (the `part_number` value `resolve_chip`'s own hyphenated-key return does not carry) over `EpromDatabase(skip_local_override=True)`, descending `db.proms` two levels.
- **All eleven measured aggregate numbers matched the plan's expected values exactly on first measurement**: 746 rows / 59 vendors / 677 distinct part numbers / 234 comma-containing / 953 distinct aliases / 942 token-differs / 11 token-matches / 514 comma-joined resolutions / 16 not-implemented / 0 not-found / 732 lowercase-form published proxy. No disagreement to report on GATE-04's aggregate.
- Committed the delta artifact with both the whole-database aggregate and a per-issue row for all 26 filed corpus issues -- all 26 with `token != resolved part_number` (100% per-chip delta), confirming research's measurement.
- `tests/test_part_number_delta_drift.py`'s four legs (existence+banner, ABSOLUTE aggregate assertion -- not drift-only, byte-identical regeneration, planted-input fail-closed) carry no skip marker and no sibling-firmware-path token, unlike the `test_sdp_bus_config_drift.py` analog they mirror -- this artifact lives in this repo.
- Planted-input leg observed RED: a corpus row's `raw_token` mutated to a chip absent from the shipped database makes the generator exit non-zero (`ERROR: derivation validation failed: filed issue #18: raw_token 'totally-nonexistent-eprom-xyz' does not resolve to any chip in the shipped database`, `rc=1`) and write nothing to `--target`.

## Task Commits

Each task produced two commits (app submodule, then meta repo with the evidence transcript and advanced gitlink), per this repo's sub-repo commit protocol.

1. **Task 1: Build and commit the 26-row filed-issue corpus** (auto, tdd="true") -- `1de3786` (test, app)
2. **Task 2: Make the corpus a live gate** (auto, tdd="true") -- `ae077a5` (test, app) + `77642aa9` (docs, meta -- evidence for tasks 1 and 2 together)
3. **Task 3: Measure and drift-test the part-number delta** (auto, tdd="true") -- `1448c83` (test, app) + `03287365` (docs, meta -- evidence)

## Files Created/Modified

- `firestarter_app/tools/build_devtest_issue_corpus.py` -- generator: `gh issue list` enumeration, one anchored title regex, fenced-JSON extraction, solve-by-trial tag recovery, validate-before-emit, `--check` drift mode
- `firestarter_app/tests/fixtures/devtest_issue_corpus.json` -- the committed 26-row corpus, `_generated_by` banner, all `recomputed_hash == filed_hash`
- `firestarter_app/tests/test_devtest_issue_corpus.py` -- 26-of-26 parametrized reproduction gate, D-06 chip coverage, dedup-group tests, anti-vacuity trio (35 tests total)
- `firestarter_app/tools/measure_part_number_delta.py` -- generator: `resolve_chip` + `get_eprom_config` measurement, `--issues` fail-closed input override, validate-before-emit including a filed-issue-resolves check, `--check` drift mode
- `firestarter_app/tests/fixtures/part_number_delta.json` -- the committed delta artifact, whole-database aggregate plus 26 per-issue rows
- `firestarter_app/tests/test_part_number_delta_drift.py` -- four-leg drift gate, no skip marker
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-04-issue-corpus.txt` -- corpus generation, reproduction-gate, and per-row filed-vs-recomputed transcript
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-04-delta-drift.txt` -- aggregate, `--check` legs, byte-identical regeneration, drift-gate transcript

## Decisions Made

- **D-06's four-chip reproduction reduction is fully superseded** by this plan's 26-of-26 result, per the operator's 2026-09-03 ratification already recorded in `174-CONTEXT.md`. See Accomplishments for the corrected `174-RESEARCH.md` finding and its named cause (bare-string vs. object `fingerprint` read).
- **Reported finding, not routed around:** the measured repeat/coverage discriminator-tag split is 17/1/3/5 (neither/repeat-only/coverage-only/both), not the plan's stated 16/1/3/6. Every one of the 26 rows still reproduces its filed hash exactly -- the single row responsible for the one-off (gh#41, w27c512, filed 2026-08-22 under host `3.0.0b27`) genuinely needs neither tag: its per-step `run_count` is 2 (not the degraded 1) for every repeat-policy-relevant op, and its filed `dedup_fingerprint` (`137e93501512`) reproduces only with both tags empty. No acceptance criterion in this plan machine-checks the 16/1/3/6 split (it appears only as planning-session background prose), so nothing was adjusted to force agreement -- the measured split is recorded here as the finding `<measurement_discipline>` requires.
- **`aliases_resolving_to_comma_joined` etc. named literally rather than reusing a plan-suggested key spelling** -- the plan's `<output>` section names the aggregate's *values*, not a fixed key string, for the lowercase-form published proxy; `part_numbers_not_lowercase_published_proxy` was chosen to read unambiguously as "the published number, not the measurement" (D-15).
- **`measure_part_number_delta.py` validates that every filed-issue row's `raw_token` resolves to a real chip** before emission (see Deviations, Rule 2) -- both a genuine data-quality invariant on the artifact and the mechanism Task 3's planted-input anti-vacuity leg needs to observe a real RED, since resolution to `None` was otherwise silently accepted as "differs=True" and never rejected.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] `measure_part_number_delta.py`'s validate-before-emit had nothing to reject a corpus row referencing a nonexistent chip**
- **Found during:** Task 3, while implementing the planted-input anti-vacuity leg the plan's own action text requires ("mutate one row's raw token to a chip the database does not carry ... assert both that the exit code is non-zero AND that nothing was written")
- **Issue:** Without an explicit check, a filed-issue row whose `raw_token` resolves to no chip (`get_eprom_config` returns `(None, None)`) would silently produce `resolved_part_number: null, differs: true` and the generator would emit successfully -- there was no invariant for the anti-vacuity leg to trip, and no invariant guarding against a corrupted or mistyped corpus row reaching the committed artifact.
- **Fix:** Added a `validate()` check rejecting any `filed_issues` row whose `resolved_part_number` is `None`, naming the issue number and raw token. This is both semantically correct (every filed `[dev test]` issue names a real, previously-tested chip, so an unresolvable token is a genuine data-quality defect) and the mechanism the planted-token leg needs.
- **Files modified:** `firestarter_app/tools/measure_part_number_delta.py`
- **Verification:** `tests/test_part_number_delta_drift.py::test_planted_nonexistent_chip_token_fails_closed_and_writes_nothing` passes; manual run against a planted broken corpus produced `rc=1` and wrote nothing to `--target`.
- **Committed in:** `1448c83` (Task 3 app commit)

**2. [Rule 3 - Blocking, verification-only] The plan's own Task 2 `<verify>` python snippet imports `REGION_POLICY_FULL_DEVICE` from the wrong module**
- **Found during:** Task 2, running the plan's own literal `<verify>` per-row transcript command
- **Issue:** The plan's verify script reads `from firestarter.constants import REGION_POLICY_FULL_DEVICE`. The constant is defined in `firestarter/chip_test.py:381`, not `firestarter/constants.py`; the literal command fails with `ImportError: cannot import name 'REGION_POLICY_FULL_DEVICE' from 'firestarter.constants'`. This mirrors the same class of plan-verify-text defect 174-01's SUMMARY documented (a `/usr/bin/grep` BRE bracket-range trap in that plan's own verify text) -- a defect in the plan's prose, not in anything this plan wrote.
- **Fix:** No source file was changed. When generating the evidence transcript, the import was corrected to `from firestarter.chip_test import ... REGION_POLICY_FULL_DEVICE` (the module every other builder and this plan's own generator already imports it from). The failed literal-command attempt is preserved verbatim in the evidence file alongside the corrected, successful run, so the transcript is honest about what happened.
- **Files modified:** none (verification-only)
- **Verification:** The corrected per-row command reproduced all 26 filed hashes exactly (`reproduced=26/26`), transcribed in `evidence/174-04-issue-corpus.txt`.
- **Committed in:** N/A (no file changed; documented here for transparency)

---

**Total deviations:** 2 (1 Rule 2 missing-critical addition to the generator's own validation, 1 Rule 3 verification-only fix to the plan's own verify text)
**Impact on plan:** Neither deviation touched a frozen hash, a measured aggregate number, or any file outside this plan's declared `files_modified`. Both were necessary for the plan's own stated acceptance criteria (the planted-input leg observing a real RED; the literal per-row verify command running at all) to hold.

## Issues Encountered

None beyond the deviations above and the measured 17/1/3/5 vs. 16/1/3/6 tag-split finding (Decisions Made), both resolved/reported within the task they were found in.

## User Setup Required

None -- `gh` was already authenticated against `henols/firestarter_prom` at plan start; no external service configuration was required.

## Next Phase Readiness

- GATE-04 and GATE-05 are both complete: the filed-issue corpus is a live 26-of-26 reproduction gate and the part-number delta is a committed, drift-tested, absolutely-asserted artifact.
- `firestarter_app/firestarter/` (production code) and `firestarter_app/firestarter/data/chip_database.json` were never touched, confirmed by an empty `git status --porcelain firestarter/` after every commit in this plan.
- `tests/fixtures/report_shapes.py` and `tests/test_blast_radius_invariance.py` were never edited by this plan, confirmed by `git diff --stat` over this plan's three commits touching only the six declared `firestarter_app` files -- 174-03 owns the next changes to those two files.
- Plan 174-05 (or whichever plan closes this phase) can now cite both a complete filed-issue history with a machine-checked hash-continuity gate and a measured, non-assumed part_number delta as inputs.
- No blockers.

## Self-Check: PASSED

- `firestarter_app/tools/build_devtest_issue_corpus.py` -- FOUND
- `firestarter_app/tests/fixtures/devtest_issue_corpus.json` -- FOUND, 26 rows, all reproduce
- `firestarter_app/tests/test_devtest_issue_corpus.py` -- FOUND, 35 tests collected, 35 passed
- `firestarter_app/tools/measure_part_number_delta.py` -- FOUND
- `firestarter_app/tests/fixtures/part_number_delta.json` -- FOUND, eleven aggregate numbers match measured values exactly
- `firestarter_app/tests/test_part_number_delta_drift.py` -- FOUND, 4 tests collected, 4 passed
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-04-issue-corpus.txt` -- FOUND
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-04-delta-drift.txt` -- FOUND
- Commit `1de3786` -- FOUND in `git log` (firestarter_app)
- Commit `ae077a5` -- FOUND in `git log` (firestarter_app)
- Commit `77642aa9` -- FOUND in `git log` (meta)
- Commit `1448c83` -- FOUND in `git log` (firestarter_app)
- Commit `03287365` -- FOUND in `git log` (meta)
- `firestarter_app/firestarter/` porcelain check -- EMPTY (no production code touched) after every commit
- `tests/test_devtest_issue_corpus.py` + `tests/test_part_number_delta_drift.py` -- 39 passed, 0 failed, 0 skipped
- `tools/build_devtest_issue_corpus.py --check` and `tools/measure_part_number_delta.py --check` -- both exit 0

---
*Phase: 174-blast-radius-invariance-harness*
*Completed: 2026-09-03*
