---
phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close
plan: 09
subsystem: dev-test-engine
tags: [voltage-schema, ast-census, anti-vacuity, skill-doc, context-amendment, dedup-fingerprint]

requires:
  - phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close
    plan: "08"
    provides: "structured chip-id field, write-refusal predicate, D-16 re-proven at 19/19"
provides:
  - "voltage.vpp_mv and voltage.vpe_mv deleted from DiagnosticReport's dataclass, from _voltage_dict()'s emits and from the schema -- the two standalone non-destructive rail slots no code path ever assigned (RPT-B1)"
  - "tests/test_voltage_field_census.py -- a new attribute-scoped AST census module proving by test, not by sentence, that no code path assigns either deleted name, with a planted-assignment anti-vacuity leg and a separate empty-expected-set vacuity leg, both observed RED"
  - ".claude/skills/devtest-triage/SKILL.md names all four surviving rail fields, states plainly they are regulator-rail readings never socket readings, and adds the pre-2.0 note explaining why a filed body may still carry the deleted keys (RPT-F2)"
  - "181-CONTEXT.md's falsified skill-row instruction (rewrite the :375 datasheet example row as the report's rail field) removed outright under a second Phase 181 amendment marker, replaced by the measured correction: that row is the DATABASE's programming voltage, a different field with the same name"
  - "RPT-E2's forward-only parse test re-run and its docstring extended to record that this is the run that actually establishes the property -- it runs AFTER the deletion, against a tree where the keys are genuinely gone from the current schema"
  - "_VOLTAGE_KEYS shrinks 6 -> 4 in the same commit as _voltage_dict()'s emit change (D-14); its docstring corrects two claims the surrounding record had already gotten wrong -- _BANNER_KEYS (plan 181-04) was the first Phase-174 key-list pin this milestone shrank, not this one, and git log -S'_VOLTAGE_KEYS' returns three commits (not one), because it also matches nearby prose that merely names the pin"
affects: [181-10]

actuals:
  tokens: 13435
  tasks: 3
  commits: 8
  plan_head_before: 70dbad9a

tech-stack:
  added: []
  patterns:
    - "attribute-scoped-not-textual-census: an AST walk matching ast.Attribute assignment targets by name, never a substring match, when the same identifier is legitimately used for an unrelated field elsewhere in the codebase -- the textual scan is measured and recorded beside the census's own count so the difference is a number, not an argument"
    - "correct-a-stale-claim-in-the-same-edit-that-would-otherwise-contradict-it: rather than write a new accurate docstring next to an old wrong one and let them disagree, both the pre-existing false grep citation (_BANNER_KEYS's docstring) and the mislabeled plan-number reference (the anti-vacuity test's docstring) were corrected in the same commit as the new _VOLTAGE_KEYS docstring they sit beside"
    - "remove-a-falsified-plan-instruction-outright-not-annotate: CONTEXT.md's wrong skill-row instruction was deleted, not footnoted -- an annotated caveat still reads as the original instruction with a caveat, and a future reader could act on the footnoted half by mistake"

key-files:
  created:
    - firestarter_app/tests/test_voltage_field_census.py
    - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/evidence/181-09-voltage-census.txt
    - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/evidence/181-09-skill-same-commit.txt
  modified:
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/tests/test_blast_radius_invariance.py
    - firestarter_app/tests/test_diagnostic_report.py
    - firestarter_app/tests/test_dev_test_cmd.py
    - firestarter_app/tests/fixtures/reports/*.json (19 files, snapshot regeneration)
    - .claude/skills/devtest-triage/SKILL.md
    - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-CONTEXT.md

key-decisions:
  - "The SKILL.md's :375 datasheet cross-check example row (vpp_mv: 13500) was left byte-unchanged, per the orchestrator's own pre-flight measurement in the plan: it is the DATABASE's programming voltage for the part, compared via the `firestarter info` view -- a different field that happens to share a name with the report's deleted key. Rewriting it would have turned a correct row into a false one."
  - "The plan's own must_haves/action text ('this is the FIRST time a Phase-174 key-list pin has ever been SHRUNK') was measured wrong against the live tree and corrected rather than followed verbatim: _BANNER_KEYS (locked_steps) was already shrunk by plan 181-04, landed before this plan ran, so _VOLTAGE_KEYS's shrink is the SECOND overall and the first of _VOLTAGE_KEYS specifically. Additionally, `git log -S'_VOLTAGE_KEYS'` returns three commits (5693bf7 creation, 90a5472/181-01, c5db256/181-04), not the single creation commit the plan claimed, because two of those commits only edited nearby prose NAMING the pin without touching its list content -- confirmed by diffing the list's own defining lines directly across every commit. Both pre-existing docstrings carrying the stale claims (_BANNER_KEYS's grep citation, and the anti-vacuity test's mislabeled 'plan 181-05' reference for this deletion, which actually landed in canonical-naming plan 181-05) were corrected in the same commit as the new accurate docstring, so the file does not contain two contradicting claims about the same gate."
  - "The census's anti-vacuity plant targets cli_handlers.py's real sampler body (inserting `report.vpp_mv = vpp` after the real `report.vpp_before_mv = vpp` line) rather than a synthetic snippet -- matching test_readback_inventory.py's established idiom of mutating real, loaded source in memory, never a fixture file."

requirements-completed: [RPT-B1, RPT-F2]

coverage:
  - id: D1
    description: "voltage.vpp_mv and voltage.vpe_mv deleted from the dataclass, from _voltage_dict()'s emits, and from _VOLTAGE_KEYS' pin (6 -> 4 entries, same commit); a keyword named for either deleted field raises TypeError on construction; to_dict()['voltage'] carries exactly 4 keys"
    requirement: RPT-B1
    verification:
      - kind: unit
        ref: "Task 1 inline verify legs 1-3 (dataclass field check, TypeError construction check, AST voltage-pin check)"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py::test_voltage_split_fields_serialize (re-pointed), tests/test_dev_test_cmd.py::TestSamplerBracketing::test_every_run_fills_split_voltage_slots (re-pointed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "D-12's premise proven by an attribute-scoped AST census, not asserted: zero assignment sites and zero emit sites for either deleted name across firestarter/diagnostic_report.py and firestarter/cli_handlers.py, with the four surviving before/after names found and attributed to _make_sampler's _sampler closure"
    requirement: RPT-B1
    verification:
      - kind: unit
        ref: "tests/test_voltage_field_census.py::test_no_code_path_assigns_the_deleted_rail_fields"
        status: pass
    human_judgment: false
  - id: D3
    description: "The census is observed RED against a planted in-memory assignment to a report object's deleted-field attribute (anchor uniqueness asserted first, zero fixture files written), and separately against an empty expected-site set -- proving the positive claim is falsifiable, not trivially true"
    requirement: RPT-B1
    verification:
      - kind: unit
        ref: "tests/test_voltage_field_census.py::test_a_planted_assignment_reddens_the_census, ::test_an_empty_expected_site_set_fails_rather_than_passing_vacuously"
        status: pass
    human_judgment: false
  - id: D4
    description: "A textual scan of the two deleted names across firestarter/ and tests/ returns materially more hits (115) than the census's own zero, with named false-positive modules (ic_layout.py and eight test modules) carrying the unrelated DATABASE field of the same name"
    requirement: RPT-B1
    verification:
      - kind: unit
        ref: "tests/test_voltage_field_census.py::test_a_textual_scan_would_return_false_positives_a_census_does_not"
        status: pass
      - kind: other
        ref: "evidence/181-09-voltage-census.txt Section 1 (measured counts and false-positive module list)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The devtest-triage skill names all four surviving rail fields, states plainly they are regulator-rail readings never socket readings (citing the report's own rail_reading_disclosure field), and adds the pre-2.0 note explaining that a body carrying the deleted keys predates schema 2.0 -- landed in meta FIRST, before the app-side deletion, so no window existed where the report had dropped a key the skill still presented as live"
    requirement: RPT-F2
    verification:
      - kind: other
        ref: "Task 1 verify leg (grep for vpp_after_mv/vpe_after_mv presence in SKILL.md); evidence/181-09-skill-same-commit.txt"
        status: pass
    human_judgment: false
  - id: D6
    description: "The skill's datasheet cross-check example row (vpp_mv: 13500) is byte-unchanged -- it is the DATABASE's programming voltage, a different field sharing the deleted key's name; both frozen devtest-triage fixtures are byte-unchanged against meta base 2facbc8f"
    requirement: RPT-F2
    verification:
      - kind: other
        ref: "Task 1 verify legs (occurrence-count + no-added-or-removed-13500-line diff against 2facbc8f; fixtures porcelain and base-diff legs)"
        status: pass
    human_judgment: false
  - id: D7
    description: "181-CONTEXT.md's falsified skill-row instruction (identifying :375 as the report field, asking for its replacement) is removed outright -- not annotated -- under a second Phase 181 amendment marker, replaced by the measured correction and the D-5 two-repo residue statement"
    verification:
      - kind: other
        ref: "Task 3 verify legs (amendment-marker presence, exact-string absence of the original instruction)"
        status: pass
    human_judgment: false
  - id: D8
    description: "The forward-only parse test (RPT-E2) is re-run explicitly AFTER the deletion lands, and its docstring records that this is the run that actually establishes the property; both frozen fixture bodies still parse and still carry the deleted keys as their own frozen pre-2.0 content"
    requirement: RPT-B1
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py::test_frozen_pre_2_0_fixtures_still_parse_forward_only (re-run post-deletion, 1 passed)"
        status: pass
    human_judgment: false
  - id: D9
    description: "All 19 FROZEN_HASHES literals byte-identical to app base 04fd982 across this plan's entire deletion (voltage was never in dedup_fingerprint's five-entry pre-image); md5 of the sorted literal set unchanged (555a6d762d528102b74061b504183df6)"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py -k test_dedup_fingerprint_is_frozen (19 passed, re-run after every task)"
        status: pass
      - kind: other
        ref: "git diff 04fd982 -- tests/fixtures/report_shapes.py: zero frozen-hash literal lines moved, at every checkpoint"
        status: pass
    human_judgment: false
  - id: D10
    description: "Zero # comments added to product source across the mandated full census (git diff --name-only 04fd982..HEAD, all .py files); files over baseline: 0/28"
    verification:
      - kind: unit
        ref: "Mandated tokenize COMMENT-token census script, run after every task and at plan end: files over baseline: 0/28"
        status: pass
    human_judgment: false
  - id: D11
    description: "Whole-repo porcelain across the meta repo, the firmware submodule, and the app repo after this plan's own commits"
    verification:
      - kind: other
        ref: "git -C /workspaces/firestarter status --porcelain (clean); git -C /workspaces/firestarter_app status --porcelain firestarter/ (clean); git -C /workspaces/firestarter_app status --porcelain (clean, whole repo)"
        status: pass
    human_judgment: false

duration: ~65min
completed: 2026-09-09
status: complete
---

# Phase 181 Plan 09: Delete `voltage.vpp_mv`/`vpe_mv` -- proven by a census, not a sentence Summary

**The two standalone rail slots no code path ever assigned are gone from `DiagnosticReport`, `_voltage_dict()` and the schema, proven by a new attribute-scoped AST census observed RED against both a planted assignment and an empty expected-site set, with the triage skill's paired update landing first and a falsified plan instruction corrected in the record rather than followed.**

## Performance

- **Duration:** ~65 min
- **Started:** 2026-09-09 (required-reading pass)
- **Completed:** 2026-09-09
- **Tasks:** 3 of 3 completed
- **Files modified:** 7 app-repo product/test files + 19 regenerated report-snapshot fixtures + 4 meta-repo files (1 new module's worth of skill prose, 1 CONTEXT.md amendment, 2 new evidence transcripts)

## Accomplishments

- **Task 1 -- the two standalone rail slots are gone, argued with the gate that predates them.** `DiagnosticReport` no longer carries `vpp_mv`/`vpe_mv`; `_voltage_dict()` emits exactly the four destructive before/after keys; a keyword named for either deleted field raises `TypeError` on construction. The class docstring and `render()`'s docstring sentence both stop naming the dead fields while keeping their substance (`render()`'s sentence now says the two standalone slots "are gone from the schema entirely now (RPT-B1) -- not merely hidden from this console table"). `tests/test_diagnostic_report.py::test_voltage_split_fields_serialize` was re-pointed: its two hand assignments and two standalone assertions are gone, its docstring records that "the standalone half of this test's original claim had no subject after RPT-B1," and it now asserts the emitted mapping carries exactly the four survivor keys. `tests/test_dev_test_cmd.py`'s end-to-end sampler-bracketing test asserts the same four-key shape on a real run. `tests/test_parse_devtest_issue.py`'s two parse-INPUT fixtures carrying the deleted keys were left untouched, as required -- they are RPT-E2's forward-only evidence. 19 report-shape snapshots regenerated, every diff confined to the two removed keys. The `devtest-triage` skill (meta repo) was edited and committed FIRST: the report-voltage sentence now names all four surviving rail fields, states plainly they are regulator-rail readings never socket readings (citing the report's own `rail_reading_disclosure` field), and states the pre-2.0 note -- landing before the app-side deletion so no window existed where the report had dropped a key the skill still presented as live. The skill's datasheet cross-check example row (`vpp_mv: 13500`, the DATABASE's programming voltage) and both frozen `devtest-triage` fixtures are byte-unchanged.

  **A discrepancy the plan's own must_haves got wrong, measured and corrected during execution:** the plan's action text instructed writing that `_VOLTAGE_KEYS` is "the FIRST time a Phase-174 key-list pin has ever been SHRUNK." Measured against the live tree at execution time, this is false -- `_BANNER_KEYS` (`locked_steps`) was already shrunk by plan `181-04`, landing three waves before this plan ran, so its docstring (still present in the file) already claims that honor for itself. `_VOLTAGE_KEYS`'s shrink is therefore the SECOND Phase-174 key-list-pin shrink overall, and the first of `_VOLTAGE_KEYS` specifically. Separately, the plan's cited evidence -- `git log -S'_VOLTAGE_KEYS' returns only the commit that created these pins` -- is also false: it returns THREE commits (`5693bf7` creation, `90a5472`/181-01, `c5db256`/181-04), because two of those commits only edited nearby prose docstrings that mention the pin's name without touching its list content. Confirmed by diffing `_VOLTAGE_KEYS`'s own defining lines directly across every commit from creation onward: the list's six values were byte-identical at every one of those three commits, only changing in this plan's own deletion. This is itself a small addition to this phase's catalogue of "measured traps": `git log -S<identifier>` matches prose that merely NAMES an identifier, not only changes to the identifier's own value -- a distinction that matters when a codebase's own docstrings talk about their neighboring pins by name (as this phase's do, extensively). Both pre-existing docstrings carrying the now-stale claims were corrected in the SAME commit as this plan's own accurate `_VOLTAGE_KEYS` docstring, so the file does not end up containing two contradicting claims about the same gate: `_BANNER_KEYS`'s docstring now correctly attributes the "first shrink" honor to itself and points to `_VOLTAGE_KEYS`'s docstring for the measured `git log -S` caveat, and the anti-vacuity test's docstring's mislabeled "plan `181-05`" reference (that plan actually landed canonical database naming, not the voltage deletion) is corrected to "plan `181-09`."

- **Task 2 -- D-12's census, proven not asserted.** New module `tests/test_voltage_field_census.py` (zero `#` comment tokens) parses `firestarter/diagnostic_report.py` and `firestarter/cli_handlers.py` with the AST, matching an `ast.Attribute` assignment target by name -- never a substring -- because the same two names (`vpp_mv`/`vpe_mv`) are DATABASE fields on an unrelated code path (a chip record's dict key in `ic_layout.py`, the wire-dict key set in `tools/check_devtest_orchestrator.py`, and eight more test modules). Four tests: the positive claim (zero assignment sites and zero dict-literal emit-site keys for either deleted name; the four surviving before/after names found, all attributed to `_make_sampler`'s `_sampler` closure, proving the census finds real sites rather than passing on an empty tree); a planted-assignment anti-vacuity leg (anchor-uniqueness asserted before a single in-memory `str.replace` inserts `report.vpp_mv = vpp`; the mutant's census reddens, observed RED, zero fixture files written); a separate, explicitly named empty-expected-set vacuity leg (also observed RED); and the textual-versus-census measurement itself, which counted 115 textual hits for the two deleted names across `firestarter/` and `tests/` (excluding this module and the six modules the census's own scan already covers) against the census's own zero, naming nine false-positive modules by name (`ic_layout.py`, `test_check_dispatch_invariants.py`, `test_chip_resolver.py`, `test_diff_db_gate.py`, `test_eprom_database.py`, `test_extra_chips_supplement.py`, `test_sdp_capability.py`, `test_variant_decode_evidence_stability.py`, `test_wire_dict_equivalence.py`).

- **Task 3 -- the falsified skill-row claim is amended out of the record, and the forward-only claim is re-proven on the only tree where it means anything.** `181-CONTEXT.md`'s pre-existing instruction to rewrite the skill's `:375` example row as the report's rail field is removed OUTRIGHT (not annotated) under a second `## Status: Phase 181 amendment` marker, labelled `measured correction`, dated 2026-09-09. The passage in its place records the true measurement (the row sits in the datasheet-versus-database cross-check table, whose firestarter-side column is the `firestarter info` view), names the correct discharge (extending the report-voltage sentence at `:330` instead), and states the D-5 two-repo residue in one sentence: one commit across two git repositories is structurally impossible, so the criterion is discharged as two commits landing inside Task 1, skill first, each naming the other's sha. `tests/test_blast_radius_invariance.py::test_frozen_pre_2_0_fixtures_still_parse_forward_only` was re-run explicitly AFTER the deletion landed -- the run that actually establishes RPT-E2's property, since before the deletion there was nothing forward about the claim -- and its docstring extended to record that this run never constructs a `DiagnosticReport` (it parses the frozen fixture's raw JSON directly), so the dataclass field removal cannot affect it. All 19 `FROZEN_HASHES` literals reconfirmed byte-identical to app base `04fd982` (md5 `555a6d762d528102b74061b504183df6`, unchanged). The invariance re-proof section of `evidence/181-09-voltage-census.txt` closes in the state-the-verdict form (mirroring `177-READBACK-INVENTORY.md`): naming the verdict, what is excluded and why, and the gates that would redden if any of it moved.

- **Zero `#` comments added to product source.** The mandated full census (`git diff --name-only 04fd982..HEAD`, all `.py` files, 28 files including the new census module) found `files over baseline: 0/28` at every checkpoint this plan re-ran it.

## Task Commits

Each task committed atomically, split across the app submodule (code) and the meta repo (skill/evidence/context), skill-first per D-5's ordering requirement:

1. **Task 1: delete voltage.vpp_mv/vpe_mv, land the skill's paired half**
   - `d2116df9` (docs, meta repo): SKILL.md -- four rail fields, rail-not-socket, pre-2.0 note (landed FIRST)
   - `c994849` (fix, app repo): the deletion, `_VOLTAGE_KEYS` shrink + corrected docstrings, re-pointed tests, 19 regenerated snapshots
   - `947c279d` (docs, meta repo): `181-09-skill-same-commit.txt`
2. **Task 2: D-12's attribute-scoped AST census**
   - `776d746` (test, app repo): `test_voltage_field_census.py`, all four tests
   - `fce662fe` (docs, meta repo): `181-09-voltage-census.txt` Section 1
3. **Task 3: amend the falsified claim, re-prove forward-only post-deletion**
   - `ca1ef72` (docs, app repo): forward-only test docstring extension
   - `8a424701` (docs, meta repo): `181-CONTEXT.md` amendment + `181-09-voltage-census.txt` Section 2

**Plan metadata commit:** this SUMMARY.md, committed separately in the meta repo per the sequential-executor protocol (`STATE.md`/`ROADMAP.md` NOT touched -- owned by the orchestrator).

## Files Created/Modified

- `firestarter_app/firestarter/diagnostic_report.py` -- `vpp_mv`/`vpe_mv` deleted from the dataclass and `_voltage_dict()`; class and `render()` docstrings stop naming the dead fields
- `firestarter_app/tests/test_blast_radius_invariance.py` -- `_VOLTAGE_KEYS` 6 -> 4; three docstrings corrected/extended (the pin's own, `_BANNER_KEYS`'s stale "first shrink" grep citation, and the anti-vacuity test's mislabeled plan reference); the forward-only test's docstring extended
- `firestarter_app/tests/test_diagnostic_report.py` -- `test_voltage_split_fields_serialize` re-pointed
- `firestarter_app/tests/test_dev_test_cmd.py` -- end-to-end sampler-bracketing test's assertion re-pointed
- `firestarter_app/tests/test_voltage_field_census.py` -- new, D-12's four-test attribute-scoped census
- `firestarter_app/tests/fixtures/reports/*.json` (19 files) -- regenerated via `tools/snapshot_report_shapes.py`, every diff confined to the two removed keys
- `.claude/skills/devtest-triage/SKILL.md` -- report-voltage sentence extended
- `.planning/phases/181-.../181-CONTEXT.md` -- second Phase 181 amendment marker, falsified skill-row instruction removed
- `.planning/phases/181-.../evidence/181-09-skill-same-commit.txt` -- new, D-5 two-repo adjudication
- `.planning/phases/181-.../evidence/181-09-voltage-census.txt` -- new, census counts + RED observations + post-deletion re-proof

## Decisions Made

See `key-decisions` in frontmatter for the full text. In summary: the SKILL.md datasheet example row was left untouched per the plan's own pre-flight measurement; the plan's own "first shrink" claim was measured wrong against the live tree (it is the second, not the first) and corrected in place alongside a stale grep citation and a mislabeled plan-number reference already present in the file; and the census's anti-vacuity plant mutates the real sampler source rather than a synthetic snippet, matching this project's established idiom.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The plan's own "first Phase-174 key-list pin ever shrunk" claim was measured false against the live tree**
- **Found during:** Task 1, while writing `_VOLTAGE_KEYS`'s new docstring
- **Issue:** The plan's must_haves and action text instructed recording that `_VOLTAGE_KEYS`'s shrink is "the FIRST time a Phase-174 key-list pin has ever been SHRUNK." Measured: `_BANNER_KEYS` (`locked_steps`) was already shrunk by plan `181-04`, landing three waves before this plan, and its own docstring already makes that "first shrink" claim for itself. Additionally the plan's cited evidence (`git log -S'_VOLTAGE_KEYS'` "returns only the commit that created these pins") is itself false -- it returns three commits, because two of them only edited nearby prose naming the pin without touching its list content.
- **Fix:** Wrote `_VOLTAGE_KEYS`'s new docstring with the accurate claim (second overall shrink, first of `_VOLTAGE_KEYS` specifically) and the accurate `git log -S` caveat (measured by diffing the list's own defining lines directly, confirming zero value changes across all three commits until this plan's own deletion). Corrected the two pre-existing docstrings that would otherwise have contradicted this new one: `_BANNER_KEYS`'s stale grep citation, and the anti-vacuity test's mislabeled "plan `181-05`" reference (the deletion actually lands in this plan, `181-09`; `181-05` performed canonical database naming instead).
- **Files modified:** `firestarter_app/tests/test_blast_radius_invariance.py`
- **Verification:** `git log --oneline -S'_VOLTAGE_KEYS' -- tests/test_blast_radius_invariance.py` (3 hits); `git show <commit>:tests/test_blast_radius_invariance.py | grep -A7 '_VOLTAGE_KEYS = \['` at each of the three hits, confirming byte-identical list contents until this plan's deletion; full module suite green (103 passed).
- **Committed in:** `c994849` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 -- a stale factual claim in the record, corrected against a live measurement). **Impact:** Necessary for the record's own internal consistency -- leaving the plan's stale claim in place would have made the newly-written docstring contradict the already-landed `_BANNER_KEYS` docstring sitting three lines below it in the same file. No scope creep: the fix stayed within the exact file and exact concern (key-list pin shrink history) the plan's own Task 1 already required editing.

## Issues Encountered

None beyond the deviation above.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

RPT-B1 and RPT-F2 are both fully discharged. `voltage.vpp_mv`/`vpe_mv` are gone from the dataclass, the serializer and the schema; the no-path-assigns-them claim is proven by an attribute-scoped AST census observed RED against both a planted assignment and an empty expected-site set, not merely asserted in prose. The `devtest-triage` skill's paired update landed first, per D-5's ordering requirement, and now correctly describes the four surviving rail fields as regulator-rail-only readings. `181-CONTEXT.md`'s one falsified instruction in this phase's record is corrected in place under its own amendment marker. D-16 holds after this plan's entire deletion: 19 frozen hashes, zero moved literal lines, md5 unchanged. RPT-E2 is re-proven on the only tree where the claim actually means something -- the one where the keys are genuinely gone from the current schema. Plan `181-10` (phase close: HYG-03 in `MILESTONES.md`, the seven-leg green-tree battery at floor 2239) is the only remaining plan in the phase.

**Do not run the seven-leg green-tree battery here, do not invoke `check_rekey_ledger.py`, and do not assert a suite floor of 2239 or 2242.** Per the plan's own `<verification>` section, that battery runs once, in `181-10`. This plan's own automated legs (per-module pytest across every touched/dependent module -- 300 passed across the combined six-module run -- `ruff check`/`ruff format --check`, the snapshot-drift check, the claims checker, the frozen-hash reproof, the mandated tokenize census, and the three porcelain legs) all pass independently of that battery.

## Comment Census (mandated full census, `git diff --name-only 04fd982..HEAD`, all `.py` files)

```
files over baseline: 0 / 28
```

## Self-Check: PASSED

- All three evidence-bearing files confirmed present on disk with `[ -f ]`: `tests/test_voltage_field_census.py`, `evidence/181-09-voltage-census.txt`, `evidence/181-09-skill-same-commit.txt`.
- All seven commit hashes confirmed present via `git log --oneline --all`: app `c994849`, `776d746`, `ca1ef72`; meta `d2116df9`, `947c279d`, `fce662fe`, `8a424701`.
- `pytest` re-run across all six touched/dependent test modules combined (`test_blast_radius_invariance.py`, `test_diagnostic_report.py`, `test_dev_test_cmd.py`, `test_parse_devtest_issue.py`, `test_voltage_field_census.py`, `test_readback_inventory.py`): `300 passed`, zero failed/error/skipped.
- All plan-level `<verification>` items re-confirmed: both standalone rail fields gone from the dataclass, `_voltage_dict()` and `_VOLTAGE_KEYS` (docstring records the corrected first/second-shrink claim); a keyword named for either deleted field raises `TypeError`; `to_dict()["voltage"]` has four keys; the attribute-scoped census reports zero assignment/emit sites, finds the four survivors, and has been observed RED against both a planted assignment and an empty expected set; the textual-versus-census difference measured (115 vs 0) with nine false-positive modules named; the skill names all four rail fields, states rail-not-socket, states the pre-2.0 note, and its datasheet example row is byte-unchanged; both frozen skill fixtures and both parse-input fixtures are unmodified; `181-CONTEXT.md` carries the amendment marker with the falsified instruction gone; the forward-only parse test passes post-deletion with 19/19 shapes reproducing and zero frozen-hash literal lines moved; no comment count rose (pin module exactly 0); all three porcelain legs print nothing.
- `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` both green (175 files formatted).
- `firestarter_app/tools/snapshot_report_shapes.py --check` and `tools/check_diagnostic_report_claims.py` both exit 0.
- `firestarter/data/chip_database.json` untouched by this plan (not in `files_modified`; no diff exists for it).

---
*Phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close*
*Completed: 2026-09-09*
