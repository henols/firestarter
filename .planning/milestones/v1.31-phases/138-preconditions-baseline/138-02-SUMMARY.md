---
phase: 138-preconditions-baseline
plan: 02
subsystem: infra
tags: [python, git, chip_database.json, pulse-distribution, gh15, evidence-script, reproducibility]

# Dependency graph
requires: []
provides:
  - "138-pulse-distribution.py — reproducible, self-checking per-protocol pulse-width re-derivation for 0x07/0x08/0x0B, importing (never reimplementing) the production _parse_pulse_duration parser"
  - "138-02-PULSE-DISTRIBUTION.md — three verbatim runs (one planted failure, two agreeing passes) reconciled against the seed's C2 table and 138-RESEARCH.md, plus independent confirmation of database blob identity and the D-11 layer distinction"
  - "Confirmation that chip_database.json's blob (ebd1eaac01698f64dc0861f8478b8931493d3bab) is byte-identical on the firestarter_app worktree, origin/beta, and gsd/v1.30-sdp-surface-retirement -- proving PREP-04 is independent of PREP-01/PREP-02"
affects: ["138-07 (the plan that ticks PREP-04 using this plan's evidence)", "139 (ISSUE-01 quotes 138-02-PULSE-DISTRIBUTION.md's output verbatim into the gh#15 comment)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Bucket from the RAW string, never the parsed int (D-11): the parsed integer 0 is a four-way collision across an absent key, an empty string, 'Algorithm Controlled', and malformed input, so classification must branch on the raw JSON value before ever calling the parser"
    - "Synthetic self-test gates the real scan (assertion 6): every real bucket is expected to measure zero on the shipped data, so a small hand-counted synthetic database proves the bucketing routine itself, run before the real scan, rather than trusting silence as correctness"
    - "Planted-failure non-vacuity proof via an env-var seam (DB_PATH pointed at a scratchpad-only file), so a script's PASS is never relied on until its FAIL has been observed for an attributable reason, with zero repository files touched by the exercise"

key-files:
  created:
    - .planning/phases/138-preconditions-baseline/138-pulse-distribution.py
    - .planning/phases/138-preconditions-baseline/138-02-PULSE-DISTRIBUTION.md
  modified: []

key-decisions:
  - "Used `git rev-parse REF:path` (a single call) rather than `git show | hash-object --stdin` for the DB_REF seam's blob-SHA reporting -- simpler, and verified live to produce the identical SHA"
  - "Assertion 3's 'falsifies C2' violation fires only when a target protocol has n>0 AND distinct_count<=1 -- a protocol with zero chips in a given input (as in Task 2's minimal planted fixture, where 0x08/0x0B are empty) is a degenerate non-finding, not a C2 violation, and must not be flagged alongside the real plant"
  - "requirements-completed left empty and REQUIREMENTS.md untouched: this plan produces PREP-04's deliverables only -- the tick is Plan 138-07's job once the whole phase's baseline is assembled, per this plan's own may_tick_requirements: [] constraint"
  - "No EpromDatabase() construction anywhere, even in prose: the shipped JSON is read directly via open()/git show, avoiding any ~/.firestarter/database.json local-override merge (T-138-06)"

requirements-completed: []

coverage:
  - id: D1
    description: "Self-checking pulse-distribution script authored: imports the production parser, buckets from the raw string across six named kinds (absent/non-string/empty/algorithm-controlled/unparseable/explicit-zero), and enforces six numbered assertions including a synthetic self-test that gates the real scan"
    requirement: "PREP-04"
    verification:
      - kind: other
        ref: "python3 .planning/phases/138-preconditions-baseline/138-pulse-distribution.py -- exits 0, VIOLATIONS: 0, RESULT: PASS; DB_REF=origin/beta invocation also exits 0 with identical substantive figures"
        status: pass
    human_judgment: false
  - id: D2
    description: "Script observed to FAIL non-vacuously on a planted single-protocol synthetic database before its PASS was ever relied on -- exit 1, RESULT: FAIL, exactly one attributable violation naming assertion 3, no repository file touched"
    requirement: "PREP-04"
    verification:
      - kind: other
        ref: "138-02-PULSE-DISTRIBUTION.md Run 1 -- verbatim planted-failure output via the DB_PATH seam against a scratchpad-only file, deleted after use; git status --porcelain confirmed unchanged in both /workspaces and /workspaces/firestarter_app"
        status: pass
    human_judgment: false
  - id: D3
    description: "Verbatim committed output artifact recording three runs, reconciling every headline figure against the seed's C2 table and 138-RESEARCH.md (every count reproduces exactly, zero divergence), and independently confirming database blob identity across three refs plus the D-11 layer distinction"
    requirement: "PREP-04"
    verification:
      - kind: other
        ref: "138-02-PULSE-DISTRIBUTION.md -- Reconciliation section, both Independent confirmation sections; re-running the script fresh at commit time still prints RESULT: PASS"
        status: pass
    human_judgment: false

# Metrics
duration: 26min
completed: 2026-08-08
status: complete
---

# Phase 138 Plan 02: Preconditions & Baseline — Pulse Distribution Summary

**Self-checking Python script re-derives the live 0x07/0x08/0x0B pulse-width distribution from chip_database.json via the production parser (170/127/32 chips, matching the seed's C2 table exactly), observed to fail on a planted input before its three verbatim runs were committed as C2's evidence for gh#15.**

## Performance

- **Duration:** 26 min
- **Started:** 2026-08-08T21:47:00Z
- **Completed:** 2026-08-08T22:13:00Z
- **Tasks:** 3
- **Files modified:** 2 (2 created, 0 modified)

## Accomplishments

- Authored `138-pulse-distribution.py`: stdlib-only, imports `firestarter.database._parse_pulse_duration`
  directly (never reimplemented), buckets every chip's `pulse_duration` from the **raw string**
  across six named kinds, and enforces six numbered assertions (denominator completeness,
  whole-database closure, C2 testability, parser-identity, blob-identity, and a synthetic
  self-test that runs *before* the real scan and gates it — printing `RESULT: FAIL` without any
  distribution if it fails).
- Measured live: `0x07` **n=170** (100 µs ×113, 200×27, 1000×22, 500×4, 50×4), `0x08` **n=127**
  (100 µs ×104, 50×11, 10×7, 200×2, 1000×2, 20×1), `0x0B` **n=32** (500 µs ×21, 1000×6, 200×5) —
  every count reproduces the seed's C2 table and `138-RESEARCH.md` **exactly**, with zero
  divergence. Whole-database partition closes exactly: 329 + 417 = 746, zero crossover in
  either direction. All six D-11 buckets measure zero on the real data across all three
  protocols — confirmed, not assumed, by the self-test proving the bucketing routine itself
  would have caught it if it hadn't.
- Proved the script's own non-vacuity obligation: ran it against a deliberately-planted,
  scratchpad-only, two-chip single-protocol database (never committed, deleted immediately
  after use) designed to trip assertion 3 (C2 testability). It failed exactly as designed —
  exit 1, `RESULT: FAIL`, exactly one violation naming assertion 3, zero unrelated violations —
  before its `RESULT: PASS` on the two real runs was ever relied on.
- Committed `138-02-PULSE-DISTRIBUTION.md`: all three verbatim runs (planted-failure first,
  then the default invocation and `DB_REF=origin/beta`, which agree on every substantive figure),
  a reconciliation paragraph tying every headline number to the seed and to
  `138-RESEARCH.md`, independent confirmation that the `chip_database.json` blob
  (`ebd1eaac01698f64dc0861f8478b8931493d3bab`) is identical on the worktree, `origin/beta`, and
  `gsd/v1.30-sdp-surface-retirement` (the fact that makes PREP-04 independent of PREP-01/PREP-02),
  and a restatement of the D-11 layer distinction (`pulse_duration` string vs. `pulse-delay`
  wire field) citing the C1 adjudication in `infoic-field-dictionary.md`.
- Recorded the `firestarter_app` submodule's actual checkout honestly, per this plan's
  no-branch-switch constraint: `fix/dev-test-blank-check-after-erase` @
  `7fe8dea9143a6ac4da3d656d3e4d5d538e14a175` — not the v1.31 branch (Plan 138-01 created it but
  did not check it out; Plan 138-04 is the one that switches it).

## Task Commits

Each task was committed atomically:

1. **Task 1: Author the self-checking pulse-distribution script** - `fcde0c78` (feat)
2. **Task 2: Prove the script can fail, then take the two recorded runs** - *no commit* — see
   below
3. **Task 3: Commit the verbatim output artifact with its reconciliation** - `f4064f99` (docs)

**Plan metadata:** (this SUMMARY's own commit, immediately following)

_Task 2 produced no commit by design._ Its own action text is explicit: "Record nothing to a
committed file in this task except the script itself if a defect surfaced." The script (already
committed in Task 1) handled the planted single-protocol fixture correctly on the first attempt
— no defect surfaced, so no fix was needed and nothing further was staged. The two "recorded
runs" Task 2 captures are consumed by Task 3's artifact, not committed independently by Task 2
itself. All of Task 2's verification (the planted-failure exit code and violation list, the
scratchpad cleanup, the two repos' unchanged `git status`) was performed and confirmed live —
see "Self-Check" below and `138-02-PULSE-DISTRIBUTION.md` Run 1 for the verbatim evidence.

## Files Created/Modified

- `.planning/phases/138-preconditions-baseline/138-pulse-distribution.py` (created, 492 lines) —
  the self-checking script: env-var seams `SUBMODULE_DIR`/`DB_PATH`/`DB_REF`, six bucket kinds,
  six numbered assertions, stdlib only
- `.planning/phases/138-preconditions-baseline/138-02-PULSE-DISTRIBUTION.md` (created, 348
  lines) — three verbatim runs, reconciliation, two independent-confirmation sections, and a
  "what this artifact is not" section

## Decisions Made

- **Blob-SHA reporting mechanism:** `git rev-parse REF:path` (one call) rather than
  `git show REF:path | git hash-object --stdin` (two calls) for the `DB_REF` seam's assertion-5
  reporting — verified live to produce the identical 40-character SHA either way; the simpler
  form was kept.
- **Assertion 3's guard condition:** written as `n > 0 and distinct_count <= 1`, not merely
  `distinct_count <= 1`. Without the `n > 0` guard, Task 2's minimal two-chip planted fixture
  (which deliberately carries zero `0x08`/`0x0B` chips) would have produced two *additional*,
  unintended violations for those protocols purely because a protocol with no chips also has
  zero distinct values — that would have violated the acceptance criterion that the planted
  run's violation list "contains no violation unrelated to the plant." This was caught and
  fixed during Task 1's own testing, before its commit (see Deviations below).
- **`requirements-completed: []`, REQUIREMENTS.md untouched:** although this plan's own
  frontmatter lists `requirements: [PREP-04]` for traceability, its `may_tick_requirements: []`
  field is the controlling instruction. PREP-04 stays `[ ]`/`Pending` — this plan produces its
  *deliverables* only; Plan 138-07 ticks it once the whole phase's baseline is assembled.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Docstring prose accidentally tripped the script's own anti-local-override grep**
- **Found during:** Task 1, self-testing against the plan's own acceptance criteria before commit
- **Issue:** The `DB_PATH` seam's docstring paragraph explained *why* `EpromDatabase()` must
  never be constructed here — but typing the literal substring `EpromDatabase()` (with
  parentheses) in prose caused `grep -v '^#' 138-pulse-distribution.py | grep -c 'EpromDatabase()'`
  to return 1 instead of the required 0, since grep cannot distinguish an explanatory docstring
  from executable code.
- **Fix:** Reworded to "never by constructing an `EpromDatabase` instance" (no trailing
  parentheses) — meaning preserved, literal substring removed.
- **Files modified:** `138-pulse-distribution.py` (docstring only, pre-commit)
- **Verification:** `grep -v '^#' 138-pulse-distribution.py | grep -c 'EpromDatabase()'` → `0`
- **Committed in:** `fcde0c78` (folded into Task 1's own commit — the fix landed before the
  file was ever committed, so there is no separate remediation commit)

**2. [Rule 1 - Bug] A required literal phrase was split across two `print()` calls**
- **Found during:** Task 1, verifying the output against the acceptance criterion requiring the
  literal substring "both correct at different layers"
- **Issue:** The LAYER paragraph's `print()` calls broke the phrase across a line boundary
  (`"...are both correct at different"` / `"layers -- the database layer..."`), so the two words
  "different" and "layers" never appeared contiguously in stdout — `grep -c 'both correct at
  different layers'` returned 0 instead of the required 1.
- **Fix:** Moved the line break so the full phrase "both correct at different layers" prints on
  one line.
- **Files modified:** `138-pulse-distribution.py` (print statements only, pre-commit)
- **Verification:** `grep -c 'both correct at different layers'` on live output → `1`
- **Committed in:** `fcde0c78` (same as above — fixed before the first commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1, both self-caught during Task 1's own
verification against the plan's acceptance criteria, both landed inside Task 1's single commit
with no separate remediation commit needed).
**Impact on plan:** Both fixes are textual/output-formatting corrections with no effect on the
script's logic, its measured figures, or its scope. No scope creep.

## Issues Encountered

**Namespace-package hazard, investigated and defended against (not a defect in the delivered
script, but worth recording):** this session found that `import firestarter` in this
devcontainer resolves to a **bogus PEP 420 namespace package rooted at `/workspaces/firestarter`
(the sibling firmware submodule, not the Python app)** whenever the current working directory
is on `sys.path` — which happens under `python3 -c` / interactive invocation (cwd joins
`sys.path[0]` as `''`), but does **not** happen under the plan's own specified invocation form
(`python3 path/to/script.py`, where `sys.path[0]` is the script's own directory). Confirmed live,
both ways, before writing the script. The plan's own instruction to
`sys.path.insert(0, SUBMODULE_DIR)` before importing already defends against this regardless of
invocation style — verified live that the insert makes `firestarter.database` resolve correctly
to `/workspaces/firestarter_app/firestarter/database.py` even when the hazard is artificially
triggered. Documented with a code comment at the insert site so a future reader understands why
the insert is not merely stylistic. No fix needed elsewhere; no repository file affected.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `138-pulse-distribution.py` and `138-02-PULSE-DISTRIBUTION.md` are committed and ready for
  Plan 138-07 to cite when assembling the phase's overall baseline record and ticking PREP-04.
- Phase 139's ISSUE-01 can quote `138-02-PULSE-DISTRIBUTION.md`'s Run 2 or Run 3 output verbatim
  into the public gh#15 comment — both are byte-identical in every substantive figure and both
  independently confirmed against two sources.
- No blockers: this plan touched neither `firestarter` nor `firestarter_app` beyond read-only
  `git` inspection; the app submodule remains exactly where Plan 138-01 left it
  (`fix/dev-test-blank-check-after-erase` @ `7fe8dea9143a6ac4da3d656d3e4d5d538e14a175`, with the
  `gsd/v1.31-27c-programming-algorithm-fidelity` ref created but not checked out) for Plan
  138-04 to act on.
- PREP-04 remains `[ ]` / `Pending` in `REQUIREMENTS.md`, exactly as required — this plan ticked
  nothing.

## Self-Check: PASSED

- FOUND: `.planning/phases/138-preconditions-baseline/138-pulse-distribution.py`
- FOUND: `.planning/phases/138-preconditions-baseline/138-02-PULSE-DISTRIBUTION.md`
- FOUND commit: `fcde0c78`
- FOUND commit: `f4064f99`
- Re-ran the script fresh at self-check time: `RESULT: PASS` confirmed

No missing items.

---
*Phase: 138-preconditions-baseline*
*Completed: 2026-08-08*
