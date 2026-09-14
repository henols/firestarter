---
status: awaiting_human_verify
trigger: "things like this 'But four of them carry .planning references in comments:' must be debugged  so it will not happend again and cleanedup"
created: 2026-09-14T18:40:00Z
updated: 2026-09-14T21:05:00Z
---

## Current Focus

reasoning_checkpoint:
  hypothesis: "The Phase 154 detector binds its token alternation to the comment
    marker via `\s*`, and omits `.planning` entirely. Deleting the marker-adjacent
    label -- the normal repair -- therefore removes the line from the detector's
    view without removing the citation, so the detector confirms its own partial
    repair. No CI gate exists in any of the three repositories to catch what the
    detector cannot see."
  confirming_evidence:
    - "The verbatim regex, recovered from 154-RESEARCH.md:801 and :1583, contains
      `\s*` between the marker group and the token group, and has no `.planning`
      alternation."
    - "Of 620 marker-independent citation lines, 480 carry a token that is present
      but NOT marker-adjacent and 55 carry only a `.planning` path. 86% are
      unreachable by that regex."
    - "One consistent oracle over firestarter_fw/{src,include,test}: 718 lines
      pre-sweep, 357 at HEAD. The sweep's own commit records 345 -> 94. Its
      visibility fell from 48% to 26% ACROSS its own remediation."
    - "test_eeprom28c_sdp.cpp:7 opened mid-sentence -- subject deleted, citations
      two words to the right. The mechanism is visible in the source."
    - "git blame of all 620: 612 predate the sweeps, 8 postdate them."
    - "No .github/workflows/ file in any of the three repositories runs any
      comment or provenance check. The meta repository has no workflows at all."
  falsification_test: "Run the verbatim 154 regex over HEAD. If it reported near
    zero while a marker-independent scan reported hundreds, the blind spot is
    load-bearing. If it reported hundreds too, the defect is elsewhere -- a scope
    carve-out or plain non-execution."
  fix_rationale: "Two artifacts, because there are two causes. A replacement
    oracle that matches anywhere inside comment TEXT and never binds a token to a
    marker addresses the blind spot. A CI step in each sub-repository's existing
    primary workflow addresses the missing gate: both workflows already trigger on
    every branch and every pull request, and `main` is protected with
    pull-request-required in all three repositories, so a red check blocks the
    merge. A pre-commit hook would not -- it is bypassable with --no-verify, it is
    per-clone, and a fresh clone has none."
  blind_spots:
    - "Python DOCSTRINGS are deliberately out of scope: CLAUDE.md flags them as a
      separate question, and Click command docstrings are user-facing --help text.
      Measured residue: firestarter_fw/tests/*.py module docstrings carry heavy
      planning narration that this gate does not see."
    - "`.github/workflows/*.yml` comments carry planning citations in both
      sub-repositories. Not scanned -- a workflow file is not product source."
    - "The requirement-id rule is a shape (`[A-Z]{2,12}-\d{2}`), not a list, so a
      future all-caps technical token of that shape needs a TECHNICAL_VOCABULARY
      entry. Seventeen are seeded; AA-55 and CRC-32 were found as real false
      positives and are among them."
    - "Deleting a whole comment paragraph can delete the only prose statement of a
      non-obvious invariant. Deletion was the instructed default; the invariants
      concerned are all executable in the suites that sit beside them."
  candidate_causes:
    - "code: the detector regex binds its tokens to the comment marker (CONFIRMED,
      load-bearing)"
    - "config/process: no CI gate in any of the three repositories (CONFIRMED,
      load-bearing for the 8 reintroductions and for the 612 going unnoticed)"
    - "process: Phase 154 discharged a narrower contract than CLAUDE.md states --
      SWEEP-03 retains ids in test files, SWEEP-04 gives them narrow treatment
      only, Ruling B leaves four blob-sha-pinned paths un-swept (CONFIRMED,
      contributory: 60 of its 94 declared survivors)"
    - "authoring behaviour keeps introducing them (REFUTED as load-bearing: 8 of
      620)"
  and_gate: "YES. No single cause explains the outcome. The blind spot explains
    why 535 lines were never seen; the scope carve-out explains why 85 that WERE
    seen were left; the missing gate explains why neither was noticed for three
    weeks and why 8 more arrived. Remove any one and the defect still occurs --
    which is why the fix is a new oracle AND a CI gate, not either alone."

hypothesis: CONFIRMED (see reasoning_checkpoint)
test: complete
expecting: complete
next_action: await human confirmation that the gate and cleanup are acceptable
bug_class: Bohrbug (fully deterministic; reproduces on every scan)
tdd_checkpoint:

## Symptoms

**Expected behavior**
`firestarter_fw/` and `firestarter_app/` contain no GSD process commentary in
source. CLAUDE.md states this as a hard rule that is "not overridable by a plan,
task, skill, or subagent instruction", and a sweep was recorded as complete for
the firmware repo.

**Actual behavior**
A casual grep during an unrelated test-cleanup session surfaced four `.planning`
citations in `firestarter_fw/test/`. A proper count finds far more.

**Measured 2026-09-14** (`/usr/bin/grep`, not the devcontainer's ugrep, which
honors .gitignore and under-scans):

| class | pattern | firestarter_fw | firestarter_app |
|---|---|---|---|
| block-comment continuation | `^\s*\*.*(\.planning\|GSD\|Phase N\|Plan N-\|D-NN\|REQ-)` | **255** | — |
| comment opener | `^\s*(//\|/\*).*(same)` | 32 | — |
| python comment | `^\s*#.*(same)` | — | 6 |

Breakdown of the 255: `firestarter_fw/test/` **253**, `firestarter_fw/src/` 2
(`json_parser.c`), `firestarter_fw/include/` 0.

Also present: an 887-line GSD planning document committed inside the firmware
test tree at `test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md`, carrying GSD
frontmatter and citing `116-RESEARCH.md` / `116-05-SUMMARY.md`.

**Error messages**
None. This is a silent-failure class: no gate exists, so nothing goes red.

**Timeline**
The rule was broadened on 2026-08-29 from provenance-only to "zero comments, EVER".
A firmware sweep was executed and recorded as complete (Phase 154). Memory
`reference_provenance_sweep_oracle_anchored_at_comment_opener` already records
that the sweep oracle under-measured — 43 reported against 1174 actual — and
asserts "fw fully swept", which the measurement above contradicts.

**Reproduction**
```
/usr/bin/grep -rnE '^\s*\*.*(\.planning|GSD|Phase [0-9]+)' firestarter_fw/test | wc -l
```

## Evidence

- timestamp: 2026-09-14T18:40:00Z
  observation: 255 continuation-line hits vs 32 opener-line hits in firestarter_fw.
  An 8:1 skew toward the line class the oracle cannot see.
  source: direct grep of the working tree

- timestamp: 2026-09-14T18:40:00Z
  observation: 253 of the 255 are under `test/`, which the "no comments in product
  source" rule covers ("everything under firestarter_fw/ and firestarter_app/")
  but which comment sweeps have historically treated as lower priority.
  source: per-directory count

- timestamp: 2026-09-14T18:40:00Z
  observation: No CI workflow in either repository runs any comment/provenance
  check. The retired `tools/wiki/` checkers and the Phase 188 `tools/check_*.py`
  family are both gone. No replacement gate exists.
  source: .planning/notes/host-tools-retirement.md, CLAUDE.md repository-structure note

- timestamp: 2026-09-14T19:05:00Z
  checked: the verbatim Phase 154 survey regex, recovered from
    `.planning/milestones/v1.33-phases/154-.../154-RESEARCH.md:801` and `:1583`:
    `(//|/\*|^\s*\*|#)\s*(Task|Phase|Plan|P\d{3}|Req|REQ-|CAP-0|D-\d|WR-\d|LOOP-\d|\d{3}-CONTEXT)`
  found: `^\s*\*` IS one of the four alternations. Block-comment continuation
    lines were NEVER invisible to the sweep on account of the marker.
  implication: the session's opening hypothesis is FALSIFIED as stated. The
    blind spot is not the marker class; it is the `\s*` that binds the token
    group to the marker, plus the absence of `\.planning` from the token list.

- timestamp: 2026-09-14T19:06:00Z
  checked: classification of all 620 citation-bearing comment lines across both
    sub-repos against that regex
  found: 85 VISIBLE (13.7%); 480 INVISIBLE because the token is present but not
    adjacent to the marker (77.4%); 55 INVISIBLE because no 154 token appears at
    all -- these are bare `.planning/...` paths (8.9%).
  implication: 535 of 620 (86%) are structurally unreachable by the sweep's own
    detector. `\.planning` was never a pattern in it.

- timestamp: 2026-09-14T19:08:00Z
  checked: one marker-independent oracle applied to the pre-sweep tree
    (`2ad5b32^` = 8695ee52) and to HEAD, over firestarter_fw/{src,include,test}
  found: PRE-SWEEP 718 -> HEAD 357. The sweep's own commit message records
    "345 provenance hits -> 94".
  implication: the sweep saw 345 of 718 (48%) going in and 94 of 357 (26%)
    coming out. Its visibility DEGRADED across its own remediation, because
    deleting the marker-adjacent label is exactly what pushes the residue out of
    marker-adjacency. Reported 73% removal; actual 50%.

- timestamp: 2026-09-14T19:10:00Z
  checked: git blame of every surviving citation comment line, split at each
    repo's last sweep commit (fw 2026-08-25 `5759dc8`; app 2026-08-30 `d56424e`)
  found: firestarter_fw 357 survivors, 0 reintroduced. firestarter_app 255
    survivors, 8 reintroduced (all in tests/test_chip_test.py, 2026-09).
  implication: authoring-time behaviour is NOT the load-bearing cause. 612 of
    620 lines predate the sweeps. This is an incomplete-remediation defect
    masked by a self-confirming oracle, not a recurring-introduction defect.
    The 8 app reintroductions are real but are 1.3% of the corpus; they are what
    the ABSENCE of a gate permits, and they are why a gate is still required.

- timestamp: 2026-09-14T19:12:00Z
  checked: Phase 154's own scope rulings, in 154-CONTEXT.md and commit 2ad5b32
  found: SWEEP-03 retains requirement/decision IDs in TEST files where the ID is
    "the case's traceability key"; SWEEP-04 gives test files "narrow treatment
    only"; Ruling B leaves four blob-sha-pinned paths entirely un-swept. The
    commit attributes 60 of its 94 survivors to "requirement/decision IDs that
    D-03 deliberately RETAINS in test files".
  implication: a THIRD mechanism, independent of the oracle -- the sweep
    discharged a NARROWER contract than CLAUDE.md states. CLAUDE.md covers
    "everything under firestarter_fw/ and firestarter_app/" with no test-file
    carve-out. "Sweep complete" was true of SWEEP-01..13 and false of the rule.

- timestamp: 2026-09-14T19:14:00Z
  checked: `.github/workflows/` in all three repositories
  found: firmware has build.yml, beta-build.yml, py32f071.yml; app has ci.yml,
    beta-release.yml, publish.yml, release.yml; meta has NO workflows directory
    at all. None of the seven runs any comment or provenance check.
  implication: no gate exists anywhere. Nothing can go red, so both the 612
    survivors and the 8 reintroductions are invisible to CI by construction.

- timestamp: 2026-09-14T19:16:00Z
  checked: blob-sha pins in firestarter_fw/tests/golden/*.json
  found: comment edits to include/eprom_params.h, src/proms/eprom_params.cpp,
    src/proms/eprom.cpp, test/native/avr/_shared/sdp_expected.h and
    test/native/avr/_shared/eprom_v131_expected.h each invalidate a recorded
    blob sha and turn a gate RED until the golden is re-derived.
  implication: these are Phase 154's "Ruling B" abstentions. Cleanup must
    re-derive each golden in the SAME commit (the one-commit property the
    goldens themselves document), never hand-edit a sha.

- timestamp: 2026-09-14T19:18:00Z
  checked: pre-change baselines
  found: `pio run -e uno` SUCCESS, Flash 22734 / RAM 1434,
    elf 69ecb20a90549811c1f0c7610d2cb4076022dde8821bc979732b19711cda7023,
    hex b68031c3f502e09cd1363f80f05ab360a1a46fb0a1771b6f31a46975074d4a44.
    `pio test -e native` 179/179. `pytest tests/` 315 passed, 1 failed
    (test_checker_convention.py::test_scope_is_firmware_only, a PRE-EXISTING
    v1.38 rename artifact asserting the directory is named `firestarter`).
  implication: the 1 red is the control, not a regression. It must stay exactly
    1 red for the same reason after the cleanup.

- timestamp: 2026-09-14T19:35:00Z
  checked: firestarter_fw/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp:7
  found: the suite header opens mid-sentence -- "* authored this suite PARKED
    and RED-by-design\n * (v1.22 Phase 116 Plan 06, TRACE-02/TRACE-04/TRACE-06)."
    The subject of the sentence is gone. The sweep deleted the marker-adjacent
    label ("Phase 116 Plan 06 --") and left the rest of the sentence, including
    its citations, on the following line.
  implication: DIRECT visual confirmation of the mechanism. The repair that
    silenced the detector is visible in the source as a dangling fragment, and
    the citation it was supposed to remove is two words further right.

- timestamp: 2026-09-14T19:40:00Z
  checked: the replacement oracle against planted controls
  found: a mid-sentence citation on a block-comment continuation line is
    DETECTED by the new oracle and MISSED by the Phase 154 regex; a bare
    `.planning/...` path on a `//` line is DETECTED by the new oracle and MISSED
    by the Phase 154 regex; a marker-adjacent citation is detected by both. A
    citation inside a C string literal and inside a Python docstring fires
    NEITHER -- Click `--help` text is safe by construction.
  implication: the replacement oracle is non-vacuous and strictly dominates the
    old one on the exact classes that produced the 612 survivors.

- timestamp: 2026-09-14T19:45:00Z
  checked: full measurement with the replacement oracle
  found: firestarter_fw 794 citation comment lines in 87 of 187 files;
    firestarter_app 460 in 69 of 140 files. TOTAL 1254.
  implication: the true corpus is 2.0x the marker-independent count taken at
    session open (620) and 8.9x what the Phase 154 detector can see (141).

## Eliminated

- hypothesis: "The sweep oracle is anchored at comment OPENER lines and cannot
    match block-comment CONTINUATION lines (`^\s*\*`)."
  evidence: the verbatim Phase 154 regex recovered from 154-RESEARCH.md:801
    contains `^\s*\*` as its third alternation. Continuation lines were matched.
    The 8:1 opener/continuation skew measured at session open is a property of
    the SOURCE (block comments dominate this codebase), not of the detector.
  timestamp: 2026-09-14T19:05:00Z

- hypothesis: "Authoring-time behaviour keeps reintroducing citations, so the
    defect is a recurrence problem."
  evidence: blame of all 620 surviving lines shows 612 predate the sweeps and
    only 8 postdate them. Reintroduction is real but is 1.3% of the corpus and
    cannot explain the other 98.7%.
  timestamp: 2026-09-14T19:10:00Z

## Resolution

root_cause: |
  Three contributing causes, all required (AND-gate).

  1. LOAD-BEARING -- a self-confirming detector. Phase 154's sweep oracle was
     `(//|/\*|^\s*\*|#)\s*(Task|Phase|Plan|P\d{3}|Req|REQ-|CAP-0|D-\d|WR-\d|
     LOOP-\d|\d{3}-CONTEXT)`. The `\s*` binds the token group to the comment
     marker, so a citation anywhere further right is invisible; and `.planning`
     was never one of the tokens, so a bare path was always invisible. The
     sweep's own repair -- delete the marker-adjacent label -- is precisely the
     operation that pushes the rest of the line out of marker-adjacency. The
     oracle's visibility therefore FELL across its own remediation, from 345 of
     718 lines (48%) to 94 of 357 (26%), and it reported 73% removal against an
     actual 50%. It confirmed its own partial fix.
  2. LOAD-BEARING -- no gate anywhere. None of the seven workflow files across
     the three repositories runs any comment or provenance check, and the meta
     repository has no workflows at all. Nothing could go red, so neither the
     612 survivors nor the 8 later reintroductions were ever announced.
  3. CONTRIBUTORY -- a narrower contract than the rule. SWEEP-03 deliberately
     RETAINS requirement and decision ids in test files, SWEEP-04 gives test
     files "narrow treatment only", and Ruling B leaves four blob-sha-pinned
     paths entirely un-swept. The sweep commit attributes 60 of its 94 declared
     survivors to that retention. CLAUDE.md has no test-file carve-out:
     "everything under firestarter_fw/ and firestarter_app/". "Sweep complete"
     was true of SWEEP-01..13 and false of the rule.

  NOT the cause: authoring-time reintroduction. 612 of 620 lines predate the
  sweeps; only 8 postdate them.

fix: |
  ORACLE -- tools/planning_citation_gate.py, vendored into both sub-repositories.
  Scans comment TEXT. Matches anywhere inside a comment and never binds a token
  to a marker. Consumes string and character literals before looking for
  comments, so a citation inside a string cannot trip it. Never reads a Python
  docstring, so Click --help text is safe by construction. Five rules: planning
  path, GSD artifact filename, phase/plan/task/milestone reference, decision id,
  requirement id -- with a 17-entry TECHNICAL_VOCABULARY allow-list (AA-55,
  CRC-32, RS-232, ...) applied per matched token, never per line. Exits 2 rather
  than 0 when it scans no files, so a wrong path cannot pass vacuously.

  GATE -- a CI step in each sub-repository's existing primary workflow:
  firestarter_fw build.yml and beta-build.yml (ahead of the build),
  firestarter_app ci.yml (ahead of ruff). Both workflows already trigger on every
  branch and every pull request, and `main` is protected with
  pull-request-required in all three repositories, so a red check blocks the
  merge. Rejected: a pre-commit hook (bypassable with --no-verify, per-clone,
  absent from a fresh clone, and never runs on a PR from another machine) and
  meta-repository-only tooling (no authority over a separate GitHub repository's
  merge). Deliberately NOT a pytest module: the operator has ruled that tests
  must not scan source text.

  CLEANUP -- 1254 citation comment lines to 0. firestarter_fw 794 -> 0 across
  187 files; firestarter_app 460 -> 0 across 140 files. Comment paragraphs that
  were pure planning narration were deleted whole; paragraphs carrying hardware,
  datasheet or protocol facts were restated without the identifier. `# noqa`,
  `# type: ignore` and the MIT licence header were never touched.
  test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md (887 lines) moved to
  .planning/milestones/v1.22-phases/117-.../117-RED-BASELINE.md.

verification: |
  guardrail_verdict: accepted

  1 ORACLE NON-VACUITY -- planted and removed, four controls. A mid-sentence
    citation on a block-comment continuation line: DETECTED by the new oracle,
    MISSED by the Phase 154 regex. A bare `.planning/` path on a `//` line:
    DETECTED, MISSED. A marker-adjacent citation: detected by both. Controls that
    must NOT fire: a citation inside a C string literal (silent), and a Click
    docstring containing "D-07", "Phase 154" and a `.planning` path (silent) --
    while the same words in a real `#` comment in the same file DO fire. The gate
    script is itself scan-clean from any working directory, and a verbatim copy
    of it still reddens on a planted line.
  2 DIGEST NON-VACUITY -- code_digest.py --self-test proves both halves before
    any run: a comment-only edit must not move the digest, a one-token code edit
    must. Passes for C and for Python.
  3 CODE INVARIANCE -- per-file comment-blind sha256, before against after:
    all 187 firestarter_fw files identical; 139 of 140 firestarter_app files
    identical. The single exception is the one disclosed, deliberate code change
    (item 6).
  4 FIRMWARE BUILD -- `pio run -e uno` byte-identical.
    .elf 69ecb20a90549811c1f0c7610d2cb4076022dde8821bc979732b19711cda7023
    .hex b68031c3f502e09cd1363f80f05ab360a1a46fb0a1771b6f31a46975074d4a44
    Flash 22734 / 32768, RAM 1434 / 2048 -- all four figures unchanged.
  5 TEST SUITES -- `pio test -e native` 179/179; `pio test -e native_nodevtools`
    179/179; firmware `pytest tests/` 315 passed / 1 failed, identical to the
    pre-change baseline (test_checker_convention.py::test_scope_is_firmware_only,
    a PRE-EXISTING v1.38 rename artifact asserting the directory is still named
    `firestarter`); host `ruff check` pass, `ruff format --check` pass,
    `pytest tests/` 1886 passed / 0 failed.
  6 PINS RE-DERIVED, NEVER HAND-EDITED -- three source-text pins are invalidated
    by construction because they hash source INCLUDING comments:
    - sdp_expected_inventory.json      dd1ba1cc -> cb254374
    - eprom_v131_trace_inventory.json  ae279eba -> df780397
      Both re-derived with each gate module's OWN _parse_arrays() against the
      live header; every array name and entry count unchanged, so only blob_sha
      moved. Landed in the same commit as the source change, per the one-commit
      property those goldens document.
    - test_serial_comm.py ring-fence   8b778000 -> 4aa34549
      The only code line changed anywhere in this session. The invariant it
      guards is independently proven intact: the comment-stripped sha256 of
      firestarter/serial_comm.py is
      cb1f35d7a34bf61653b3534d038c5385d743e838a2f7212b937c931f2985d573 before and
      after, so no read() call, no branch on a wire byte and no write to
      start_time moved.
  7 DISCLOSED RESIDUE -- the firestarter_app tip carries 132 citation lines in 33
    files that the operator's already-staged, deliberately uncommitted test-module
    deletion removes. That same pending commit also clears the `ruff format
    --check` failure already present at HEAD (tests/fixtures/planted_unparsable.py).
    The operator's index and working tree were left byte-untouched: the 20 test
    modules their pending change also edits carry their comment cleanup in this
    session's commit, taken from HEAD, so their residual diff is now 1113 removed
    lines of which 0 are planning-citation comments.

files_changed:
  - firestarter_fw/tools/planning_citation_gate.py (new -- the oracle)
  - firestarter_fw/.github/workflows/build.yml, beta-build.yml (the gate)
  - firestarter_fw: 95 source files cleaned; 2 goldens re-derived; RED-BASELINE.md removed
  - firestarter_app/tools/planning_citation_gate.py (new -- the oracle)
  - firestarter_app/.github/workflows/ci.yml (the gate)
  - firestarter_app: 86 source files cleaned; 1 ring-fence pin re-derived
  - tools/citations/code_digest.py (new -- the comment-blind invariance instrument)
  - .planning/milestones/v1.22-phases/117-.../117-RED-BASELINE.md (relocated)
