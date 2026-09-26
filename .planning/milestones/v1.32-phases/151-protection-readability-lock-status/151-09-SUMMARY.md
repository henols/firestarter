---
phase: 151-protection-readability-lock-status
plan: 09
subsystem: testing
tags: [ast, static-analysis, ruff, mypy, pytest, subprocess, protection-readability]

requires:
  - phase: 151-protection-readability-lock-status (plan 151-02)
    provides: "protection_readability.py's curated DOCUMENTED_READABLE_TOKENS / DOCUMENTED_NOT_READABLE_TOKENS frozensets, MECHANISM_BY_TOKEN, PERMANENCE_BY_TOKEN, AMBIGUOUS_DOC_CITATIONS"
  - phase: 151-protection-readability-lock-status (plan 151-06)
    provides: "protection_gate_for_entry's pure (class_token, reason) split, structurally excluding protected/unprotected"
provides:
  - "tools/check_protection_readability_invariants.py — the AST invariant gate freezing the curated table's shape (LOCK-01's mechanical proof)"
  - "Two committed planted fixtures proving the gate is not decorative, one of which doubles as plan 151-12's required D-12 leg 4 fixture"
  - "13-leg subprocess-driven pairing test, zero in-process env redirection"
affects: [151-12, 151-13]

tech-stack:
  added: []
  patterns:
    - "Env-override injection seam (FIRESTARTER_PROTECTION_READABILITY_SRC), fourth instance of the convention"
    - "Parameterised Class 2 (_TOKEN_SET_NAMES tuple) instead of a single gated symbol"
    - "Unconditional (non-dominance-gated) Class 1(a) for tokens that must never appear in a pure module at all"
    - "Deliberately-weaker Class 3 rule, stated as such in the docstring, for reporting-only mappings"

key-files:
  created:
    - firestarter_app/tools/check_protection_readability_invariants.py
    - firestarter_app/tests/test_check_protection_readability.py
    - firestarter_app/tests/fixtures/planted_protection_permit_by_default.py
    - firestarter_app/tests/fixtures/planted_protection_widenable_tokenset.py
  modified: []

key-decisions:
  - "Class 1(a) is generalised to flag a return of a silicon-only class token UNCONDITIONALLY, dominated or not — dominance tracking is retained structurally (mirrors the analog's event-list shape) but never exempts the violation, because protection_gate_for_entry's signature accepts no device response at all."
  - "Class 2 is parameterised into _TOKEN_SET_NAMES (a 2-tuple) rather than authoring a new dict-literal AST matcher (Option B), preserving the analog's literal-frozenset-only machinery for both gated names for free."
  - "Class 3 (MECHANISM_BY_TOKEN / PERMANENCE_BY_TOKEN) is checked by a deliberately weaker rule — exactly-once binding to a literal str->str dict, no dominance analysis, no key-provenance check — stated as such in both the gate's docstring and the module's own comment."
  - "Class 4 requires AMBIGUOUS_DOC_CITATIONS non-empty, so the C-17 documentation disagreement cannot be silently resolved away."

requirements-completed: [LOCK-01]

coverage:
  - id: D1
    description: "check_protection_readability_invariants.py exists, passes against the real module, and fails closed on a missing path, unparsable source, or a zero-symbol scan on either gated name"
    requirement: LOCK-01
    verification:
      - kind: unit
        ref: "tests/test_check_protection_readability.py#test_checker_exits_zero_on_clean_source"
        status: pass
      - kind: unit
        ref: "tests/test_check_protection_readability.py#test_fail_closed_on_missing_target"
        status: pass
      - kind: unit
        ref: "tests/test_check_protection_readability.py#test_fail_closed_on_zero_symbol_scan_missing_readable_tokens"
        status: pass
      - kind: unit
        ref: "tests/test_check_protection_readability.py#test_fail_closed_on_zero_symbol_scan_missing_not_readable_tokens"
        status: pass
    human_judgment: false
  - id: D2
    description: "Two committed planted fixtures are each SEEN to fail the gate for the right reason, isolated to their own class"
    requirement: LOCK-01
    verification:
      - kind: unit
        ref: "tests/test_check_protection_readability.py#test_checker_exits_nonzero_on_planted_permit_by_default"
        status: pass
      - kind: unit
        ref: "tests/test_check_protection_readability.py#test_checker_exits_nonzero_on_planted_widenable_tokenset"
        status: pass
      - kind: unit
        ref: "tests/test_check_protection_readability.py#test_planted_permit_by_default_also_reports_bare_except"
        status: pass
    human_judgment: false
  - id: D3
    description: "Class 3's weaker rule is proven weaker in exactly the claimed way (not accidentally strong) and still a real checkable negative"
    requirement: LOCK-01
    verification:
      - kind: unit
        ref: "tests/test_check_protection_readability.py#test_class3_non_literal_mechanism_dict_fails"
        status: pass
      - kind: unit
        ref: "tests/test_check_protection_readability.py#test_class3_key_absent_from_gated_sets_still_passes"
        status: pass
    human_judgment: false
  - id: D4
    description: "LOCK-01 flipped (checkbox + traceability row, both REQUIREMENTS.md and ROADMAP.md), and only LOCK-01"
    requirement: LOCK-01
    verification:
      - kind: other
        ref: "git diff .planning/REQUIREMENTS.md .planning/ROADMAP.md — LOCK-01 rows only"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-08-20
status: complete
---

# Phase 151 Plan 09: Protection-Readability AST Gate Summary

**AST invariant gate freezing `protection_readability.py`'s curated table (two parameterised frozensets, a generalised unconditional Class 1(a), and a deliberately-weaker Class 3), paired with a 13-leg subprocess test and two committed planted fixtures.**

## Performance

- **Duration:** 55 min
- **Tasks:** 3
- **Files modified:** 4 (all new)

## Accomplishments

- `tools/check_protection_readability_invariants.py` — copies
  `check_sdp_capability_invariants.py`'s scaffolding (env-override seam, docstring shape,
  `main()` fail-closed behavior, `_print_bucket`) and extends it with four violation classes
  over the three-axis curated table.
- Class 1(a) is generalised from the analog's dominance-gated `True`-tuple check into an
  **unconditional** flag on any tuple return whose first element is a silicon-only class token
  (`_SILICON_ONLY_TOKENS = {"protected", "unprotected"}`) — dominated or not — because
  `protection_gate_for_entry`'s signature accepts no device response at all (D-12 leg 4).
- Class 2 parameterises the analog's single `_TOKEN_SET_NAME` into `_TOKEN_SET_NAMES`
  (`DOCUMENTED_READABLE_TOKENS`, `DOCUMENTED_NOT_READABLE_TOKENS`), applying the
  literal-`frozenset`-only rule to each name independently, with a per-name binding count in
  the PASS line.
- Class 3 (`MECHANISM_BY_TOKEN` / `PERMANENCE_BY_TOKEN`) is a deliberately weaker literal
  `str -> str` dict rule — stated as such in the docstring — proven weaker in exactly the
  claimed way (not accidentally strong) by a dedicated test leg.
- Class 4 requires `AMBIGUOUS_DOC_CITATIONS` non-empty, so the C-17 documentation
  disagreement cannot be silently resolved away.
- Two committed planted fixtures, each verified to fail the gate for its own planted class and
  nothing else — one doubles as plan 151-12's required D-12 leg 4 fixture.
- 13-leg subprocess-driven pairing test (`tests/test_check_protection_readability.py`), zero
  in-process env redirection.
- **LOCK-01 flipped** — checkbox and traceability row in both `REQUIREMENTS.md` and
  `ROADMAP.md`, exclusively.

## Task Commits

Each task was committed atomically, inside `firestarter_app/`:

1. **Task 1: The gate** — `2d74123` (feat) — `check_protection_readability_invariants.py`
2. **Task 2: Two committed planted fixtures** — `a8b2c82` (test) — both fixture files
3. **Task 3: The paired subprocess-driven test** — `df586bf` (test) —
   `test_check_protection_readability.py`, 13 legs

**Meta commit:** this SUMMARY + `.planning/` state updates (LOCK-01 flip, gitlink bump) —
committed separately after this file, per the execution protocol.

## Files Created/Modified

- `firestarter_app/tools/check_protection_readability_invariants.py` — the AST gate, four
  violation classes, ~430 lines
- `firestarter_app/tests/test_check_protection_readability.py` — 13-leg paired test
- `firestarter_app/tests/fixtures/planted_protection_permit_by_default.py` — Class 1(a)+1(b),
  and plan 151-12's D-12 leg 4 fixture
- `firestarter_app/tests/fixtures/planted_protection_widenable_tokenset.py` — Class 2(b) on one
  gated name, Class 2(c) on the other

## Verification Evidence

### The PASS line against the real module

```
$ python3 tools/check_protection_readability_invariants.py
PASS: scanned ../firestarter/protection_readability.py; 0 Class 1, 0 Class 2, 0 Class 3, 0 Class 4 violations; bound exactly once each: DOCUMENTED_READABLE_TOKENS=1, DOCUMENTED_NOT_READABLE_TOKENS=1
rc=0
```

### The permit-by-default fixture, seen to fail (Class 1)

```
$ FIRESTARTER_PROTECTION_READABILITY_SRC=tests/fixtures/planted_protection_permit_by_default.py \
    python3 tools/check_protection_readability_invariants.py
FAIL: 2 Class 1 (permit-by-default) violation(s):
  tests/fixtures/planted_protection_permit_by_default.py:59: tuple return starting with silicon-only class token 'unprotected' is forbidden here UNCONDITIONALLY, dominated or not, because this pure module's signature accepts no device response and protected/unprotected must never be returned from it at all (Class 1a)
  tests/fixtures/planted_protection_permit_by_default.py:57: bare `except:` handler could swallow a refusal into a silent permit (Class 1b) -- any `# noqa: BLE001` here is inert because this repository's ruff select list is [E, F, I, UP]
rc=1
```

Grep counts confirming isolation: `grep -ci 'class 1'` = 3 (both bucket header and each
violation line); `grep -ci 'class [234]'` = 0 — Classes 2/3/4 are not named in this fixture's
output.

### The widenable-token-set fixture, seen to fail (Class 2, both gated names)

```
$ FIRESTARTER_PROTECTION_READABILITY_SRC=tests/fixtures/planted_protection_widenable_tokenset.py \
    python3 tools/check_protection_readability_invariants.py
FAIL: 2 Class 2 (widenable-token-set) violation(s):
  tests/fixtures/planted_protection_widenable_tokenset.py:38: DOCUMENTED_READABLE_TOKENS is not bound from a direct frozenset(...) call over a set/list/tuple display of string literals only (widenable-token-set, Class 2b)
  tests/fixtures/planted_protection_widenable_tokenset.py: DOCUMENTED_NOT_READABLE_TOKENS bound 2 time(s) at module level (expected exactly 1) -- the gate cannot vacuously pass when its subject symbol is not found exactly once (widenable-token-set, Class 2a)
rc=1
```

Both gated symbol names (`DOCUMENTED_READABLE_TOKENS`, `DOCUMENTED_NOT_READABLE_TOKENS`)
appear in the output — the parameterisation itself is exercised, not only the first name.
`grep -ci 'class 1'` on this fixture's output = 0.

### Leg 10's second half — Class 3 proven weaker in exactly the claimed way

Input (`test_class3_key_absent_from_gated_sets_still_passes`, written inline to `tmp_path`):

```python
DOCUMENTED_READABLE_TOKENS = frozenset({'W29C020C'})
DOCUMENTED_NOT_READABLE_TOKENS = frozenset({'W29C020'})
MECHANISM_BY_TOKEN = {'SOME_TOKEN_IN_NEITHER_GATED_SET': 'boot_block_lockout'}
PERMANENCE_BY_TOKEN = {'W29C020C': 'permanent'}
AMBIGUOUS_DOC_CITATIONS = {'W29C020': 'x'}
```

`MECHANISM_BY_TOKEN`'s sole key is a member of **neither** gated token set. Result: exit **0**,
`PASS:` in stdout — proving Class 3 does not check key provenance against the curated sets,
which is the deliberate weakening the docstring claims, not an accidental strength. The paired
leg (`test_class3_non_literal_mechanism_dict_fails`, a `MECHANISM_BY_TOKEN` bound from a
function call) exits 1 naming `Class 3`, proving the weaker rule is still a real checkable
negative.

### Full-suite and tooling confirmation

- `pytest tests/test_check_protection_readability.py -x -o addopts=""` — 13 passed.
- `pytest tests/test_check_sdp_capability.py -x -o addopts=""` — still 9 passed (analog
  untouched; `git status --porcelain tools/check_sdp_capability_invariants.py` empty).
- `pytest tests/test_protection_table_citations.py -x -o addopts=""` — 6 passed (confirmed
  green before flipping LOCK-01, per the plan's explicit precondition).
- Full host suite (`pytest tests/ -o addopts="-ra" --cov=firestarter --cov-fail-under=70`):
  **1759 passed**, coverage **83.86%** (>= 70% required);
  `firestarter/protection_readability.py` itself at 97% line coverage.
- `ruff check` / `ruff format --check` clean on all four new files. (`tools/catalog/codegen.py`
  and `tools/catalog/codegen_vectors.py` have pre-existing, out-of-scope ruff findings —
  confirmed untouched by `git diff --stat` returning empty for those paths.)
- `python3 tools/check_mypy_watermark.py`: 35 errors, **at** the watermark (35), zero new.
  `check_protection_readability_invariants.py` is genuinely type-checked in that run, not
  merely subprocess-tested: `check_mypy_watermark.py` invokes mypy as `mypy firestarter/
  tests/`, and `tests/test_check_protection_readability.py` imports
  `_DEFAULT_PROTECTION_READABILITY_SRC` from the tool, so mypy follows that import — confirmed
  via `mypy --verbose`: `Metadata fresh for tools.check_protection_readability_invariants`,
  and the run's "(checked 152 source files)" clause includes it. This is the same mechanism
  the analog gate (`check_sdp_capability_invariants.py`) already relies on via its own test's
  import of `_DEFAULT_SDP_CAPABILITY_SRC`.
- `grep -c 'monkeypatch.setenv' tests/test_check_protection_readability.py` = 0.

## Decisions Made

- Class 1(a)'s dominance-tracking machinery (the `_SiliconOnlyReturnVisitor`'s `member_test`
  events) is retained structurally, mirroring the analog's `_PermitByDefaultVisitor` shape, but
  never gates the violation — every silicon-only-token return is flagged unconditionally,
  dominated or not, per the plan's explicit instruction and D-12 leg 4's requirement.
- Option A (parameterise `_TOKEN_SET_NAME` into a tuple) taken over Option B (one three-tuple
  dict), per `151-DESIGN.md`'s recorded rationale: it preserves Class 1(a) dominance detection
  (`PROTECTION_TABLE[token][1]` would be an `ast.Subscript`, not an `ast.Compare`) and reuses
  the existing literal-frozenset-only machinery for both readability-axis names for free.
- Class 3's weaker rule is stated in words in three places (this gate's docstring, the module's
  own comment above `MECHANISM_BY_TOKEN`/`PERMANENCE_BY_TOKEN`, and this SUMMARY), per
  `151-PATTERNS.md`'s requirement that a weakening never be left implicit.

## Deviations from Plan

None — plan executed exactly as written. One clarification, not a deviation: the plan's
instruction to "reuse the analog's dominance resolution verbatim in shape" was interpreted as
retaining the event-collection/sort structure while making the resolution unconditional (per
the same task's explicit "flag such a return unconditionally... dominated or not" instruction)
— both instructions are satisfied simultaneously by this reading, and no other reading
reconciles them.

## Issues Encountered

None. Two ruff-format-only fixups were applied inline during Task 1/2/3 (line-wrapping); no
behavior change, folded into each task's own commit.

## Next Phase Readiness

- Plan 151-12 (D-12 invariant) can consume `planted_protection_permit_by_default.py` directly
  as its required leg-4 fixture — confirmed it returns `"unprotected"` undominated from the
  pure path.
- Plan 151-13 owns LOCK-02/LOCK-03/LOCK-04's flip; this plan touched only LOCK-01.
- No blockers.

---
*Phase: 151-protection-readability-lock-status*
*Completed: 2026-08-20*

## Self-Check: PASSED

All 4 created files found on disk; all 3 task commit hashes (`2d74123`, `a8b2c82`, `df586bf`)
found in `firestarter_app`'s git history.
