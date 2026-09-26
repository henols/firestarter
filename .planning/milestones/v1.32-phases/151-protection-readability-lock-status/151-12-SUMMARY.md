---
phase: 151-protection-readability-lock-status
plan: 12
subsystem: testing
tags: [d-12, invariant, ast, subprocess, protection-readability, lock-status, python, firestarter_app]

requires:
  - phase: 151-protection-readability-lock-status (plan 06)
    provides: "protection_gate_for_entry's pure (entry, display_name) -> (class_token, reason) resolution over the four protocol-id frozensets"
  - phase: 151-protection-readability-lock-status (plan 09)
    provides: "tools/check_protection_readability_invariants.py and the committed planted fixture tests/fixtures/planted_protection_permit_by_default.py"
  - phase: 151-protection-readability-lock-status (plan 11)
    provides: "lock_status.py's SILICON_ONLY_TOKENS frozenset"
provides:
  - "firestarter_app/tests/test_lock_status_class_partition.py — the D-12 invariant: 18 test functions across exhaustiveness, determinism, pinned census, structural unreachability, citation presence, robustness controls, and the live AMBIGUOUS_DOC_CITATIONS proof"
affects: [151-13]

tech-stack:
  added: []
  patterns:
    - "Whole-database walk helper (_walk_database_for_class_tokens / _resolve_database_or_raise) that collects per-row failures into one message rather than raising on the first, reused by both the real-DB exhaustiveness leg and the synthetic-mutation non-vacuity control"
    - "Pinned-set-with-symmetric-difference-message style for small buckets (not_implemented's 40, the algorithm-0x05 population's 27), per-algorithm-decomposition style for the large no_mechanism bucket (405) -- both copied from test_sdp_db_invariant.py / test_b15_page_size_corroboration.py"
    - "AST-based Return-value scan (never grep) paired with a real subprocess-driven planted-fixture proof through the existing FIRESTARTER_PROTECTION_READABILITY_SRC env seam, so the AST rule's ability to fail is demonstrated rather than assumed"

key-files:
  created:
    - firestarter_app/tests/test_lock_status_class_partition.py
  modified: []

key-decisions:
  - "The exhaustiveness helper never raises per-row; it collects failures into a list and a single wrapper (_resolve_database_or_raise) turns 'any failures' into one AssertionError naming every offender. This is what let leg 6(c)'s synthetic-mutation control reuse the exact same code path the real-DB leg 1 test does, rather than a parallel reimplementation."
  - "Leg 4's AST assertion (4a) is paired with a subprocess-driven proof (4b) using 151-09's already-committed planted fixture, per the plan's explicit non-vacuity requirement -- an absence assertion alone would pass trivially because the real module was never going to contain the literal."
  - "Leg 6(c)'s synthetic novel-algorithm id is 999, verified absent from both the committed database's twelve distinct algorithm values (5,6,7,8,11,13,14,16,39,40,41,52) and from every classified protocol-id frozenset -- satisfying orchestrator constraint 5's 'genuinely novel' requirement rather than a merely unused-in-this-module id."
  - "Leg 5's citation-presence check is deliberately scoped to DOCUMENTED_READABLE_TOKENS only and its docstring states the overlap with test_protection_table_citations.py is intentional: that file gates the curated table's authoring, this leg gates the partition's inputs, per 151-VALIDATION.md's Required Assertion Set naming citation presence as one of D-12's own six legs."
  - "A stray 'monkeypatch.setenv' substring initially appeared only inside a docstring (never an actual call) explaining why the seam uses a real subprocess; reworded to avoid tripping the plan's literal grep -c check, since the check does not distinguish prose from code."

requirements-completed: []  # advances LOCK-03, LOCK-04 per plan frontmatter; both flip at 151-13

# Metrics
duration: ~70min
completed: 2026-08-20
status: complete
---

# Phase 151 Plan 12: The D-12 Class-Partition Invariant Summary

**Landed `test_lock_status_class_partition.py` — an 18-leg invariant walking `protection_gate_for_entry` over all 746 committed database rows, pinning the corrected 405/40/84/217 census as literals and proving `protected`/`unprotected` structurally unreachable via a real planted-fixture failure through the subprocess gate seam.**

## Performance

- **Duration:** ~70 min
- **Tasks:** 2 (Task 1 `tdd="true"`, Task 2 `type="auto"`)
- **Files modified:** 1 (new)
- **Commits:** 2, both inside `firestarter_app/`

## Accomplishments

- Created `firestarter_app/tests/test_lock_status_class_partition.py` (878 lines, 18 test functions) implementing all seven required D-12 legs from `151-VALIDATION.md`:
  1. **Exhaustiveness** — all 746 rows resolve into the frozen gate-token set; the walk raises for none.
  2. **Disjointness/determinism** — one token per row, two consecutive walks byte-equal.
  3. **Census pinned as literals** — `no_mechanism` 405 (with the seven per-algorithm counts 170/127/32/20/2/34/20), `not_implemented` 40 (pinned as a **set**, the OD-2 39+1 decomposition superseding `151-VALIDATION.md`'s earlier 39), `not_readable` 84 (0x0D) + 24 (curation) = 108, the algorithm-0x05 population's 27 rows pinned as a set, the 0x05+0x06 curation surface split 81/24/112 (matching `151-06-SUMMARY.md`'s measurement exactly), and the total arithmetic 405+40+84+217==746.
  4. **Structural unreachability** — an AST scan of `protection_readability.py` proving neither silicon-only token appears in any `Return` value, paired with plan `151-09`'s committed planted fixture routed through the subprocess `FIRESTARTER_PROTECTION_READABILITY_SRC` seam (observed failing, naming Class 1) and the real module through the same seam (observed exit 0).
  5. **Citation presence** — every `DOCUMENTED_READABLE_TOKENS` member has a citation comment whose quoted `lockable-proms.md` fragment resolves verbatim in the document; docstring states the deliberate overlap with `test_protection_table_citations.py`.
  6. **Robustness** — the two key-less TEXAS INSTRUMENTS rows (`2516`, `2532`) resolve `no_mechanism` without raising; the ten non-`"supported"` rows all resolve; a synthetic novel-algorithm control (id `999`, absent from the DB and every classified protocol-id set) makes the exhaustiveness walk raise, naming only the synthetic row.
  7. **`AMBIGUOUS_DOC_CITATIONS` liveness** — the C-17 record reaches a real refusal reason produced from the real `WINBOND/W29C020,W29C020C,W29C022` database entry.

## Task Commits

1. **Task 1: exhaustiveness, determinism, census** — `8db05a5` (test, `firestarter_app` repo)
2. **Task 2: unreachability, citations, robustness** — `c2872c6` (test, `firestarter_app` repo)

**Plan metadata:** (this commit + gitlink bump, meta repo)

## Files Created/Modified

- `firestarter_app/tests/test_lock_status_class_partition.py` — new, 18 test functions.

## Non-Vacuity Evidence (recorded verbatim, per the plan's `<output>` requirement)

### Leg 1: the red-then-green transcript on the `0x34` row

Before committing, `NOT_IMPLEMENTED_PROTOCOL_IDS` in `firestarter/protection_readability.py` was temporarily edited from `frozenset({16, 52})` to `frozenset({16})` (removing the OD-2 `0x34` classification), and `test_all_746_rows_resolve_exhaustively` was run in isolation. **Observed failure, verbatim:**

```
AssertionError: D-12 leg 1: the following rows did not resolve into the frozen class-token set: ["XICOR/X88C64P,X88C64S (protocol-id=52, 0x34): protection_gate_for_entry: protocol-id 52 for 'X88C64P' is not classed by this module. Every protocol id must land in NO_MECHANISM_PROTOCOL_IDS, NOT_IMPLEMENTED_PROTOCOL_IDS, NOT_READABLE_PROTOCOL_IDS or CURATION_PROTOCOL_IDS -- a synthetic or newly-added algorithm must be classed there before this row can be answered. No default branch exists; a silent fallback would make D-12 leg 6's exhaustiveness walk unwritable."]
```

The edit was then reverted (`frozenset({16, 52})` restored) and the full test file was re-run: **10/10 passed.** `git status --short firestarter/protection_readability.py` confirmed zero diff before the task-1 commit — the temporary removal was never committed.

### Leg 4(b): the gate's observed output for the planted fixture and the real module

Planted fixture, routed through the subprocess env seam:
```
$ FIRESTARTER_PROTECTION_READABILITY_SRC=tests/fixtures/planted_protection_permit_by_default.py python3 tools/check_protection_readability_invariants.py
FAIL: 2 Class 1 (permit-by-default) violation(s):
  tests/fixtures/planted_protection_permit_by_default.py:59: tuple return starting with silicon-only class token 'unprotected' is forbidden here UNCONDITIONALLY, dominated or not, because this pure module's signature accepts no device response and protected/unprotected must never be returned from it at all (Class 1a)
  tests/fixtures/planted_protection_permit_by_default.py:57: bare `except:` handler could swallow a refusal into a silent permit (Class 1b) -- any `# noqa: BLE001` here is inert because this repository's ruff select list is [E, F, I, UP]
rc=1
```

Real module, through the same seam:
```
$ python3 tools/check_protection_readability_invariants.py
PASS: scanned ../firestarter/protection_readability.py; 0 Class 1, 0 Class 2, 0 Class 3, 0 Class 4 violations; bound exactly once each: DOCUMENTED_READABLE_TOKENS=1, DOCUMENTED_NOT_READABLE_TOKENS=1
rc=0
```

### Leg 6(c): the observed raise message for the synthetic novel-algorithm control

```
D-12 leg 1: the following rows did not resolve into the frozen class-token set: ["SYNTHETIC_MFR/SYNTHETIC_NOVEL_ALGORITHM_ROW (protocol-id=999, 0x3E7): protection_gate_for_entry: protocol-id 999 for 'SYNTHETIC_NOVEL_ALGORITHM_ROW' is not classed by this module. Every protocol id must land in NO_MECHANISM_PROTOCOL_IDS, NOT_IMPLEMENTED_PROTOCOL_IDS, NOT_READABLE_PROTOCOL_IDS or CURATION_PROTOCOL_IDS -- a synthetic or newly-added algorithm must be classed there before this row can be answered. No default branch exists; a silent fallback would make D-12 leg 6's exhaustiveness walk unwritable."]
```

Names only `SYNTHETIC_NOVEL_ALGORITHM_ROW`; the control row `AM28F010` does not appear anywhere in the message. `id 999` was independently verified absent from the committed database's twelve distinct `programming.algorithm` values (`5, 6, 7, 8, 11, 13, 14, 16, 39, 40, 41, 52`) before use.

## The Full Landed Census

Computed by the committed walk over the real `chip_database.json` (746 rows):

| gate token | count | source |
|---|---|---|
| `no_mechanism` | 405 | 0x07(170)+0x08(127)+0x0B(32)+0x0E(20)+0x27(2)+0x28(34)+0x29(20) |
| `not_implemented` | 40 | 0x10(39) + 0x34(1, OD-2) |
| `not_readable` | 108 | 0x0D(84) + curation(24) |
| `read_permitted` | 81 | curation |
| `undocumented_alias` | 112 | curation |
| **total** | **746** | 405+40+84+217 |

The 0x05+0x06 curation surface (217 rows: 27 at 0x05, 190 at 0x06) splits `read_permitted`/`not_readable`/`undocumented_alias` as `81/24/112`, matching `151-06-SUMMARY.md`'s independently measured distribution exactly. Cross-checked directly against 151-06's numbers per orchestrator constraint 4 — no disagreement, no adjustment needed.

## Verification

- `pytest tests/test_lock_status_class_partition.py -x -o addopts="-ra"` — **18 passed**, no skips.
- `pytest tests/test_lock_status_class_partition.py -o addopts="" --collect-only -q` — **18 tests collected**.
- `FIRESTARTER_PROTECTION_READABILITY_SRC=tests/fixtures/planted_protection_permit_by_default.py python3 tools/check_protection_readability_invariants.py` — exit 1, naming Class 1 (see transcript above).
- `python3 tools/check_protection_readability_invariants.py` (real module, same seam) — exit 0, `PASS:` (see transcript above); confirms `151-09`'s gate is **not weakened** by this plan.
- `grep -c 'monkeypatch.setenv' tests/test_lock_status_class_partition.py` — **0**.
- `ls tools/ | grep -c 'check_claims\|check_permitted'` — **0**; no phase-local checker created.
- Full host suite (`pytest tests/ -o addopts="-ra" --cov=firestarter --cov-report=term-missing --cov-fail-under=70`, Python 3.11 venv): **1788 passed**, coverage **83.32%** (>= 70% required). Baseline was 1770; delta of exactly 18 matches this file's test count, confirming zero regressions elsewhere.
- `ruff check tests/test_lock_status_class_partition.py` / `ruff format --check tests/test_lock_status_class_partition.py` — clean.
- `python3 tools/check_mypy_watermark.py` — **35 errors, watermark 35** (at watermark, zero new).

Python environment used: the pre-provisioned py3.11 venv at
`/tmp/claude-1000/-workspaces/f3ebf666-a01b-4de4-9860-8a006054ba0c/scratchpad/p151/venv311`
(per orchestrator constraint 7).

## Deviations from Plan

**1. [Rule 1 — cosmetic] Reworded a docstring to avoid a literal-substring false positive on the `monkeypatch.setenv` grep gate.** The plan's acceptance criterion requires `grep -c 'monkeypatch.setenv' tests/test_lock_status_class_partition.py` to be `0`. A helper docstring initially explained the subprocess seam by name-checking the pattern it deliberately avoids ("never `monkeypatch.setenv`"), which is prose, not a call — but the grep does not distinguish the two. Reworded to "never an in-process pytest env-patching fixture" instead, preserving the same meaning without tripping the literal check. No behavior change; commit `c2872c6`.

No other deviations — both tasks landed exactly as the plan specified, including the mandatory red-then-green transcript for leg 1 and the planted-fixture-through-subprocess-seam proof for leg 4.

## Requirement Flips

**None.** This plan advances `LOCK-03` and `LOCK-04` per its frontmatter, but per the phase's convention both flip at `151-13`. No requirement checkbox or traceability row was touched in `.planning/REQUIREMENTS.md`, matching the plan's explicit "Requirement flips owned by this plan: none" statement.

## Issues Encountered

None beyond the docstring rewording noted above.

## User Setup Required

None.

## Next Phase Readiness

- `test_lock_status_class_partition.py` is committed and green; `151-13` (which owns the `LOCK-02`/`LOCK-03`/`LOCK-04` requirement-checkbox flips and the `dev lock-status` CLI wiring) can now rely on the D-12 partition being provably exhaustive, deterministic, and structurally incapable of leaking `protected`/`unprotected` from the pure path.
- `151-09`'s AST gate was re-verified passing on the real module after this plan's changes — not weakened.
- No blockers for `151-13`.

## Self-Check: PASSED

- FOUND: firestarter_app/tests/test_lock_status_class_partition.py
- FOUND commit: 8db05a5
- FOUND commit: c2872c6

---
*Phase: 151-protection-readability-lock-status*
*Completed: 2026-08-20*
