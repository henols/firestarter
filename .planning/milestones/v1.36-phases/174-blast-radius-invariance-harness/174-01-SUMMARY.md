---
phase: 174-blast-radius-invariance-harness
plan: 01
subsystem: testing
tags: [dedup_fingerprint, build_db_diff, invariance-harness, re-key-ledger, anti-vacuity, sha256, ast]

requires:
  - phase: 174-blast-radius-invariance-harness (context/research)
    provides: "16-name shape_id set, measured hashes, canonical-string model, D-01..D-16 decisions"
provides:
  - "tests/fixtures/report_shapes.py: build_shape/build_shape_from_step_specs, SHAPE_IDS, FROZEN_HASHES, RESERVED_SHAPE_IDS"
  - "tools/snapshot_report_shapes.py: committed to_dict() snapshot generator with --check drift mode"
  - "tests/fixtures/rekey_ledger.py: the append-only LEDGER format later phases append to"
  - "tools/rekey/check_rekey_ledger.py: the meta-side cross-tree checker later phases' re-keys must pass"
  - "the anti-vacuity three-leg contract (clean/planted/fail-closed) as a reusable pattern for plans 174-02..05"
affects: [174-02, 174-03, 174-04, 174-05, "175 (read-back gating)", "177", "178", "179", "180", "181"]

actuals:
  tokens: 12000
  tasks: 3
  commits: 5

tech-stack:
  added: []
  patterns:
    - "Frozen absolute-hash parametrize table (never a relational fp(a)==fp(b) comparison)"
    - "Append-only four-tuple re-key ledger, ast.literal_eval-parsed cross-tree, never imported"
    - "Anti-vacuity three-leg contract: clean input passes, planted mutation fails, missing/unparsable input fails closed"

key-files:
  created:
    - firestarter_app/tests/fixtures/report_shapes.py
    - firestarter_app/tests/fixtures/rekey_ledger.py
    - firestarter_app/tests/fixtures/reports/sst27sf512-six-step.json
    - firestarter_app/tests/fixtures/planted_rekey_mutation.py
    - firestarter_app/tools/snapshot_report_shapes.py
    - firestarter_app/tests/test_blast_radius_invariance.py
    - firestarter_app/tests/test_rekey_ledger.py
    - tools/rekey/check_rekey_ledger.py
    - .planning/phases/174-blast-radius-invariance-harness/evidence/174-01-tracer-end-to-end.txt
    - .planning/phases/174-blast-radius-invariance-harness/evidence/174-01-anti-vacuity-red-green.txt
    - .planning/phases/174-blast-radius-invariance-harness/174-01-DECISION-shape-id-set.md
  modified:
    - .planning/MILESTONES.md

key-decisions:
  - "shape_id name set frozen at full-sixteen (operator-resolved checkpoint), with m27c512-full-canonical-name re-measured to 776846bf2dc8 replacing an unreproduced inherited pair, and uv-slot-write-pass kept RESERVED (unreachable via _mock_operator)"
  - "This plan builds and freezes exactly one shape (sst27sf512-six-step) of the sixteen-name namespace; the remaining fifteen are approved reservations for later plans/phases to build against"
  - "MILESTONES.md's v1.36 Re-Key Ledger section records that 3 of CONTEXT.md D-12's 4 inherited hash pairs (a00791f1c2b4, 7d1cd4157cfa, a6f6c6354047) do not reproduce from any m27c512 report shape across an exhaustive ~2.1e8-candidate pre-image sweep -- seeded from re-measured values instead"
  - "check_rekey_ledger.py parses LEDGER via ast.literal_eval on both plain-Assign and AnnAssign forms, but rekey_ledger.py itself uses a plain (unannotated) assignment to match the plan's own hard-coded ast.Assign-only verify script"

patterns-established:
  - "Anti-vacuity three-leg contract (clean/planted/fail-closed) applied to both an in-process hash gate and a subprocess cross-tree checker in the same plan"
  - "One normaliser shared between the snapshot generator and its drift test (render_shape), never two independently-maintained copies"

requirements-completed: [GATE-01, GATE-02, GATE-03, GATE-05, GATE-06]

coverage:
  - id: D1
    description: "sst27sf512-six-step's dedup_fingerprint is frozen at the absolute literal 4dc282a5d596, taken off a real DiagnosticReport by the real function"
    requirement: "GATE-01"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_dedup_fingerprint_is_frozen[sst27sf512-six-step-4dc282a5d596]"
        status: pass
    human_judgment: false
  - id: D2
    description: "The suite fails when dedup_fingerprint changes for the frozen shape; assertions are absolute, never relational fp(a)==fp(b)"
    requirement: "GATE-02"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_planted_mutation_clearing_write_fingerprint_reddens_the_gate"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_planted_mutation_lowering_chip_name_reddens_the_gate"
        status: pass
    human_judgment: false
  - id: D3
    description: "build_db_diff's ladder output (proposed_disposition, ladder_state) is pinned for the tracer shape"
    requirement: "GATE-03"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_build_db_diff_ladder_pin_for_tracer_shape"
        status: pass
    human_judgment: false
  - id: D4
    description: "A report corpus lives in firestarter_app/tests/fixtures/ -- the committed to_dict() snapshot plus its drift test"
    requirement: "GATE-05"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_committed_snapshot_matches_a_fresh_regeneration"
        status: pass
    human_judgment: false
  - id: D5
    description: "The re-key ledger is recorded in MILESTONES.md and bound to the app-side ledger by a meta-side checker, observed RED on a planted mismatch and on three fail-closed inputs"
    requirement: "GATE-06"
    verification:
      - kind: integration
        ref: "tests/test_rekey_ledger.py#test_check_rekey_ledger_clean_input_exits_zero"
        status: pass
      - kind: integration
        ref: "tests/test_rekey_ledger.py#test_check_rekey_ledger_planted_input_exits_one"
        status: pass
      - kind: integration
        ref: "tests/test_rekey_ledger.py#test_check_rekey_ledger_fails_closed_on_missing_ledger"
        status: pass
      - kind: integration
        ref: "tests/test_rekey_ledger.py#test_check_rekey_ledger_fails_closed_on_missing_milestones"
        status: pass
      - kind: integration
        ref: "tests/test_rekey_ledger.py#test_check_rekey_ledger_fails_closed_on_unparsable_ledger"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-09-03
status: complete
---

# Phase 174 Plan 01: One-Shape Tracer Through the Blast-Radius Harness Summary

**One `shape_id` (`sst27sf512-six-step`) travels all eight harness layers -- builder, absolute hash `4dc282a5d596`, ladder pin, committed `to_dict()` snapshot, append-only ledger row, `MILESTONES.md` counterpart, and a meta-side `ast`-based cross-tree checker -- with every gate observed RED against a planted mutation before being trusted.**

## Performance

- **Duration:** 55 min (estimated; exact start timestamp not captured at spawn)
- **Completed:** 2026-09-03T15:13:37Z
- **Tasks:** 3 (1 checkpoint:decision, already resolved by the operator; 1 tracer/tdd; 1 auto)
- **Files modified:** 12 (10 created, 2 modified: `.planning/MILESTONES.md` and the `firestarter_app` gitlink)

## Accomplishments

- Built `tests/fixtures/report_shapes.py`, the fixture module every later phase in this milestone imports, with a real `DiagnosticReport` builder for the tracer shape and the `SHAPE_IDS`/`FROZEN_HASHES`/`RESERVED_SHAPE_IDS` registries D-04/D-10 require.
- Proved `dedup_fingerprint(build_shape("sst27sf512-six-step")) == "4dc282a5d596"` by recomputing the hash in-session against the real function -- not transcribing it -- and independently reproduced the SHA-256 of the recovered canonical pre-image to confirm the truncation contract.
- Pinned `build_db_diff`'s ladder output for the tracer shape (`inconclusive -- needs N>=2 agreement (advisory)`, `ladder_state == ""`), which the plan's own behaviour spec predicted from the two `indeterminate`-classified steps.
- Generated and committed a byte-stable `to_dict()` JSON snapshot via a new `tools/snapshot_report_shapes.py` generator with a `--check` drift mode, mirroring `tools/gen_sdp_bus_config.py`'s shape.
- Seeded the append-only re-key ledger (`tests/fixtures/rekey_ledger.py`) with one row and wrote the meta-side `tools/rekey/check_rekey_ledger.py` that binds it to a new `.planning/MILESTONES.md` "v1.36 Re-Key Ledger" section, both directions, via `ast.literal_eval` -- never a cross-tree import.
- Planted three real anti-vacuity legs (an undeclared re-key, two missing input paths, one unparsable-ledger input, two in-process hash mutations) and transcribed every observed RED into `evidence/174-01-anti-vacuity-red-green.txt` before restoring GREEN.
- Recorded, in `MILESTONES.md`'s new ledger section, that 3 of CONTEXT.md D-12's 4 inherited before/after hash pairs do not reproduce from any m27c512 report shape -- an exhaustive ~2.1e8-candidate pre-image sweep found zero hits -- which is itself a blast-radius finding, not a defect this plan owed a fix for.

## Task Commits

Each task was committed atomically. Task 2 and Task 3 each produced two commits (app submodule, then meta repo with the advanced gitlink) per this repo's sub-repo commit protocol.

1. **Task 1: Confirm the shape_id name set** (checkpoint:decision, already resolved) - `b6679fd9` (docs, meta) -- decision record
2. **Task 2: One shape_id through all eight layers** (tracer, tdd="true") - `1973345` (feat, app) + `6be45ff0` (feat, meta)
3. **Task 3: Plant mutations, observe RED, restore GREEN** (auto) - `e0baf3e` (test, app) + `3005694e` (test, meta)

## Files Created/Modified

- `firestarter_app/tests/fixtures/report_shapes.py` - shape builders, `SHAPE_IDS`, `FROZEN_HASHES`, `RESERVED_SHAPE_IDS`, the shared deterministic `EpromDatabase` instance
- `firestarter_app/tools/snapshot_report_shapes.py` - deterministic `to_dict()` snapshot generator, `--check` drift mode
- `firestarter_app/tests/fixtures/reports/sst27sf512-six-step.json` - committed output snapshot (schema 1.7)
- `firestarter_app/tests/fixtures/rekey_ledger.py` - the append-only `LEDGER`, one seeded row
- `firestarter_app/tests/fixtures/planted_rekey_mutation.py` - never-imported anti-vacuity counter-example
- `firestarter_app/tests/test_blast_radius_invariance.py` - absolute-hash, twelve-hex-contract, boundary, ladder, key-list, snapshot-drift and two in-process anti-vacuity gates
- `firestarter_app/tests/test_rekey_ledger.py` - ledger row-shape/resolution sweep plus five subprocess legs against the meta checker
- `tools/rekey/check_rekey_ledger.py` - the meta-side cross-tree checker (`ast.literal_eval`, `--repo-root`-anchored, exit 0/1/2)
- `.planning/MILESTONES.md` - new "v1.36 Re-Key Ledger" section
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-01-tracer-end-to-end.txt` - the eight-layer transcript
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-01-anti-vacuity-red-green.txt` - the anti-vacuity transcript
- `.planning/phases/174-blast-radius-invariance-harness/174-01-DECISION-shape-id-set.md` - Task 1's resolved decision record

## Decisions Made

- **shape_id namespace: full-sixteen, operator-resolved before this executor spawned.** All sixteen proposed names are frozen as the namespace; three later-phase names are RESERVED (not frozen) in `RESERVED_SHAPE_IDS`, asserted disjoint from `SHAPE_IDS` at import time. This plan itself builds and freezes only `sst27sf512-six-step` -- the tracer's whole point is proving the spine with one shape before the remaining fifteen are built across plans 174-02 through 174-05.
- **`m27c512-full-canonical-name` freezes at the measured `776846bf2dc8`**, not CONTEXT.md D-12's inherited, unreproduced `a00791f1c2b4` -> `a6f6c6354047` pair (see 174-01-DECISION-shape-id-set.md and the new MILESTONES.md section).
- **`rekey_ledger.py`'s `LEDGER` uses a plain (unannotated) assignment, not `LEDGER: tuple[...] = (...)`.** The plan's own Task 2 verify script parses the ledger with `isinstance(n, ast.Assign)` only; an `AnnAssign` (the annotated form) would make that exact literal script find zero matches and crash on `v[0]`. `check_rekey_ledger.py` itself defensively accepts both `Assign` and `AnnAssign` forms, but the fixture file follows the narrower form to match the plan's hard-coded verification.
- **The meta checker enforces a fourth rule beyond the plan's literal action text**: an undeclared ledger row (`after_hash is None`) with a `MILESTONES.md` counterpart must have that counterpart's `after` cell read as non-hash-shaped ("undeclared"), not a filled 12-hex value -- this closes a gap the plan's prose named ("its after_hash cell must read as undeclared") but did not spell out as a check.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `check_rekey_ledger.py`'s `ast.Assign`-only LEDGER lookup did not match an annotated assignment**
- **Found during:** Task 2, first run of the meta checker against the real ledger
- **Issue:** `rekey_ledger.py` was initially authored as `LEDGER: tuple[tuple[str, str, str | None, str], ...] = (...)` (an `ast.AnnAssign` node). Both my own checker's original `ast.Assign`-only lookup AND the plan's own hard-coded Task 2 verify script's inline `ast.walk` (`isinstance(n, ast.Assign)`) miss this node type, so both would report "no LEDGER assignment found" / crash on an empty match list.
- **Fix:** Removed the type annotation from `rekey_ledger.py`'s `LEDGER` assignment (now a plain `LEDGER = (...)`), and separately hardened `check_rekey_ledger.py`'s own `parse_ledger` to accept both `ast.Assign` and `ast.AnnAssign` for defensiveness against a future phase's ledger file using the annotated form.
- **Files modified:** `firestarter_app/tests/fixtures/rekey_ledger.py`, `tools/rekey/check_rekey_ledger.py`
- **Verification:** Both the plan's literal `python3 -c "...ast.walk...isinstance(n,ast.Assign)..."` snippet and `check_rekey_ledger.py` now succeed against the committed file.
- **Committed in:** `1973345` (app), `6be45ff0` (meta) (part of Task 2's commits)

**2. [Rule 3 - Blocking] Plan's own literal grep assertion `shape_ids=['sst27sf512-six-step']` triggers a BRE bracket-range parse error under plain `/usr/bin/grep -qx`**
- **Found during:** Task 2, running the plan's own first `<verify><automated>` block verbatim
- **Issue:** `/usr/bin/grep -qx "shape_ids=['sst27sf512-six-step']"` fails with `grep: Invalid range end` -- POSIX basic regular expressions interpret `['sst27sf512-six-step']` as a bracket expression, and `12-s` inside it is parsed as an invalid character range (digit to letter). This is a defect in the plan's own verify command, not in anything this plan wrote; the evidence file's actual content is unaffected.
- **Fix:** No source file was changed. When manually re-verifying this specific line's presence (after the plan's compound `&&` chain aborted at this grep), I substituted an equivalent `grep -qxF` (fixed-string mode) invocation, which performs the same exact-line-match check without BRE bracket parsing. The evidence file `174-01-tracer-end-to-end.txt` was generated by running the plan's script exactly as given (only the assertion-checking grep needed the `-F` substitution, and only for this one line); every other assertion in both verify blocks ran unmodified and passed.
- **Files modified:** none (verification-only; the plan text itself is not a file this plan is scoped to edit)
- **Verification:** All 14 assertion conditions across Task 2's two verify blocks, and all 13 across Task 3's two verify blocks, pass -- transcribed in the two evidence files and reproduced interactively during this session.
- **Committed in:** N/A (no file changed; documented here for transparency)

---

**Total deviations:** 2 auto-fixed (2 Rule 3 - blocking issues, both mechanical: an AST node-type mismatch and a shell tooling quirk in the plan's own verify text)
**Impact on plan:** Neither deviation touched the harness's actual measurement logic (`dedup_fingerprint`, `build_db_diff`, or any hash literal). Both were parsing/tooling fixes needed to make the plan's own specified verification actually run; the frozen hash, the ladder pin, and the anti-vacuity legs are exactly as the plan specified.

## Issues Encountered

None beyond the two deviations above, both resolved within the task they were found in.

## User Setup Required

None - no external service configuration required.

## Transcribed Anti-Vacuity Evidence (verbatim from `evidence/174-01-anti-vacuity-red-green.txt`)

```
== A clean ledger, real milestones
OK: 1 ledger row(s), 1 MILESTONES.md row(s) bound
rc=0
== B planted undeclared after_hash
ERROR: declared ledger row 'RK-174-99-planted-undeclared' (after_hash='000000000000') has no MILESTONES.md row
ERROR: MILESTONES.md row 'RK-174-01-p177-readback-gating' has no matching ledger row
rc=1
== C ledger path does not exist
ERROR: ledger not found: /tmp/tmp.n2fWFvX5yk/nope.py
rc=2
== D milestones path does not exist
ERROR: milestones file not found: /tmp/tmp.n2fWFvX5yk/nope.md
rc=2
== E parses but declares no ledger
ERROR: no LEDGER assignment found in /tmp/tmp.n2fWFvX5yk/noledger.py
rc=2
== F in-process mutations, both axes
clean=4dc282a5d596
fp_cleared=399fd0f0521c
chip_lowered=b49cef21b252
rc=0
== G clean again, nothing was left mutated on disk
OK: 1 ledger row(s), 1 MILESTONES.md row(s) bound
rc=0
== H both test modules
..................                                                       [100%]
18 passed in 0.80s
rc=0
```

Leg B is the planted-mismatch RED (an undeclared re-key nobody recorded, `RK-174-99-planted-undeclared`, correctly rejected). Legs C/D/E are the three fail-closed REDs (missing ledger path, missing `MILESTONES.md` path, a ledger file that parses as Python but declares no `LEDGER`). Leg F's `fp_cleared`/`chip_lowered` values (`399fd0f0521c`, `b49cef21b252`) are the two in-process mutation REDs -- both differ from `clean=4dc282a5d596`, proving the gate is sensitive on both the per-step and the chip-name axis `dedup_fingerprint` reads.

## Next Phase Readiness

- The spine is proven: builder -> real `dedup_fingerprint` -> real `build_db_diff` -> committed `to_dict()` snapshot -> append-only ledger -> `MILESTONES.md` -> meta-side checker, all bound together and all observed RED before being trusted.
- Plans 174-02 through 174-05 can now build the remaining fifteen shape_ids from the frozen namespace against this same `report_shapes.py`/`rekey_ledger.py`/`check_rekey_ledger.py` scaffolding without re-deriving any of it.
- No blockers. `firestarter_app/firestarter/` (production code) was never touched, confirmed by an empty `git status --porcelain firestarter/` at every checkpoint in this plan.

## Self-Check: PASSED

- `firestarter_app/tests/fixtures/report_shapes.py` -- FOUND
- `firestarter_app/tests/fixtures/rekey_ledger.py` -- FOUND
- `firestarter_app/tests/fixtures/reports/sst27sf512-six-step.json` -- FOUND
- `firestarter_app/tests/fixtures/planted_rekey_mutation.py` -- FOUND
- `firestarter_app/tools/snapshot_report_shapes.py` -- FOUND
- `firestarter_app/tests/test_blast_radius_invariance.py` -- FOUND
- `firestarter_app/tests/test_rekey_ledger.py` -- FOUND
- `tools/rekey/check_rekey_ledger.py` -- FOUND
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-01-tracer-end-to-end.txt` -- FOUND
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-01-anti-vacuity-red-green.txt` -- FOUND
- Commit `b6679fd9` -- FOUND in `git log` (meta)
- Commit `1973345` -- FOUND in `git log` (firestarter_app)
- Commit `6be45ff0` -- FOUND in `git log` (meta)
- Commit `e0baf3e` -- FOUND in `git log` (firestarter_app)
- Commit `3005694e` -- FOUND in `git log` (meta)
- `firestarter_app/firestarter/` porcelain check -- EMPTY (no production code touched)
- `tests/test_blast_radius_invariance.py` + `tests/test_rekey_ledger.py` -- 18 passed, 0 failed, 0 skipped

---
*Phase: 174-blast-radius-invariance-harness*
*Completed: 2026-09-03*
