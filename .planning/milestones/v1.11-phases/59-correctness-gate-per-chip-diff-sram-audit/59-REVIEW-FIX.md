---
phase: 59-correctness-gate-per-chip-diff-sram-audit
fixed_at: 2026-06-09
review_path: .planning/phases/59-correctness-gate-per-chip-diff-sram-audit/59-REVIEW.md
iteration: 1
findings_in_scope: 7
fixed: 7
skipped: 0
status: all_fixed
---

# Phase 59: Code Review Fix Report

**Fixed at:** 2026-06-09
**Source review:** `.planning/phases/59-correctness-gate-per-chip-diff-sram-audit/59-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 7 (CR-01, WR-01..05, IN-01)
- Fixed: 7
- Skipped: 0 (IN-02, IN-03 explicitly out of scope per the task brief)

All fixes are correctness/robustness changes to the GATE-02 tooling and one
HTTP-robustness fix. **No decode semantics changed; `chip_database.json` was NOT
regenerated.** Exit-code contract preserved and extended:
`0 = clean/PASS`, `1 = diff BLOCK (D-03)`, `2 = infra error (new, WR-04)`.

## Commits

Submodule `firestarter_app` (branch `v1.11-infoic-decode-correctness`):
- `f3b2ed7` — `fix(59): rework diff_db index + classifier (CR-01/IN-01/WR-01..04)`
- `76b2a15` — `fix(59): add timeout + raise_for_status to build_db HTTP fetch (WR-05)`

Meta-repo gitlink bump:
- `9c1c9fb` — `chore(59): bump firestarter_app submodule (code-review fixes)`

## Fixed Issues

### CR-01: Non-unique `part_number` index silently drops ~69 chips (BLOCKER)

**File modified:** `firestarter_app/tools/diff_db.py`
**Commit:** `f3b2ed7`
**Applied fix:** Re-keyed `_make_index` on the unique composite `(mfg, part_number)`,
falling back to `(mfg, part_number, i)` when even that collides. Added a
`_raw_total(db)` helper and a `_pn(key)` projection used everywhere a
part_number is displayed. Reworked all `new`/`missing`/`changed`/`unexplained`
set logic and report formatting to operate on the composite key. Added
`assert len(idx) == raw_total` for **both** baseline and current DB in `main()`
so a future collision regression fails loudly instead of silently shadowing
records.

**Proof:** index is now 1:1 with records — `734 chips, 734 diffed` (baseline)
and `743 chips, 743 diffed` (current). Total changed chips rose from **371 →
405** precisely because the previously-shadowed duplicate records now
participate in the diff.

### WR-01: `RULE_ALGO` early-return masked compound changes

**File modified:** `firestarter_app/tools/diff_db.py`
**Commit:** `f3b2ed7`
**Applied fix:** `_classify_diff` no longer early-returns on `algo_diff`. It now
deep-diffs every field path (`_diff_field_paths`) and returns
`(label, extra_paths)`. Any secondary field delta that is itself explained by a
known rule is surfaced in a new **COMPOUND changes** report section
(`<pn> [<cause>] + secondary: <paths>`) rather than being masked by the primary
rationale. 21 compound changes are now surfaced (17 `RULE_ALGO` + 4
`SRAM_PINOUT`) that were previously invisible.

### WR-02: Classifier covered only 5 of ~10 fields

**File modified:** `firestarter_app/tools/diff_db.py`
**Commit:** `f3b2ed7`
**Applied fix:** Introduced `_RULE_FIELD_PATHS` — the explicit set of field paths
each rule is allowed to explain — and computed `_all_rule_paths`. The classifier
now deep-diffs the full record (matching the `bl_chip != cu_chip` equality
check) and routes any chip with a differing field path outside **all** known
rules to `unexplained` (D-03 BLOCK). Verified empirically that `electrical.type`
is a derived field (build_db Pass-2 re-derivation) that **never** changes without
a co-occurring algorithm or pinout change (0 violations across the DB), so it is
legitimately claimed by `RULE_ALGO`/`SRAM_PINOUT`. A probe injecting a change to
an uncovered field (`electrical.vpp`) now correctly produces a BLOCK (exit 1).

> **Requires human verification:** WR-01/WR-02 changed classification *logic*.
> Tiers 1+2 confirm syntax and end-to-end exit codes, but the developer should
> confirm the rule-to-field-path attribution (`_RULE_FIELD_PATHS`) matches the
> intended decode semantics — in particular that `electrical.type` belongs to
> RULE_ALGO/SRAM_PINOUT and that surfacing vcc/vdd/timing as *secondary* (rather
> than escalating) on algo-corrected chips is desired. Confirmed against current
> data: gate is green and the 21 compound notes are all benign Rule-1/Rule-3
> side-effects.

### WR-03: Hard-coded "Rule 1 unblock" header not verified

**File modified:** `firestarter_app/tools/diff_db.py`
**Commit:** `f3b2ed7`
**Applied fix:** The NEW-chips section now inspects each new chip and prints a
`WARN: new chip <pn> is NOT a Rule 1 unblock (pinout=..., algo=...)` when it is
not `pinout==DIP24_2816 and algorithm==0x0D`. It WARNs rather than
asserting/crashing, and a non-Rule-1 new chip does not change the exit code.
Verified: all 9 current new chips pass silently; a synthetic non-Rule-1 new chip
triggers the WARN and the gate still exits 0.

### WR-04: File loads had no error handling

**File modified:** `firestarter_app/tools/diff_db.py`
**Commit:** `f3b2ed7`
**Applied fix:** Added `_load_db(path, label)` wrapping `open`+`json.load` in
`try/except (OSError, json.JSONDecodeError)`, printing an actionable message to
stderr and exiting with a **distinct code 2** (infra error) so it never collides
with the diff-BLOCK code (1). Verified: missing baseline → exit 2; malformed
JSON → exit 2.

### WR-05: `build_db.py` HTTP fetch had no timeout or status check

**File modified:** `firestarter_app/tools/build_db.py`
**Commit:** `76b2a15`
**Applied fix:** Changed `requests.get(MINIPRO_XML_URL)` to
`requests.get(MINIPRO_XML_URL, timeout=30)` followed by `r.raise_for_status()`
before `ET.fromstring(r.content)`. Both calls remain inside the existing
`try/except` that exits 1 on failure.

### IN-01: Header counts diverged from diffed key counts

**File modified:** `firestarter_app/tools/diff_db.py`
**Commit:** `f3b2ed7`
**Applied fix:** Resolved naturally by CR-01 — the header now prints both the raw
record count and the diffed-index size (`734 chips, 734 diffed`), and the
`assert len(idx) == raw_total` enforces they always reconcile.

## Out of Scope (not fixed, per task brief)

- **IN-02** (`_classify_diff` docstring "188 chips" stale count) — explicitly out
  of scope.
- **IN-03** (`interpret_timing` bare `except Exception`) — explicitly out of
  scope (predates this phase).

## Gate Re-run Proof (CR-01 verification)

**Before fixes** (`python3 tools/diff_db.py`):
- Exit code: **0**
- `734 chips` / `743 chips` printed from raw counts; diff reasoned over only
  ~665/674 de-duplicated keys (≈69 records shadowed, invisible).
- `PASS: all 371 changed chips explained (9 new chips confirmed; 0 chips removed)`

**After fixes** (`python3 tools/diff_db.py`):
- Exit code: **0**
- Header: `Baseline: ... (734 chips, 734 diffed)` / `Current: ... (743 chips, 743 diffed)`
- **`assert len(idx) == raw_total` passes for BOTH DBs** → all 734 baseline and
  all 743 current records are now indexed 1:1 (no shadowing).
- `PASS: all 405 changed chips explained (9 new chips confirmed; 0 chips removed from baseline)`
- Changed total rose **371 → 405** (the previously-shadowed duplicate records now
  diff correctly).
- 21 COMPOUND changes surfaced (WR-01); 9 new chips all confirmed Rule 1 (WR-03,
  no WARN).

**Record-count proof for CR-01:** index now **734/734** (baseline) and
**743/743** (current) keys == raw record counts. Previously the index held only
665/674 distinct keys, dropping 69 records each side.

**Exit-code contract verification:**
- Clean run → exit **0** ✓
- Probe with an unexplained uncovered-field change (`electrical.vpp`) → exit **1** (D-03 BLOCK) ✓
- Missing baseline / malformed JSON → exit **2** (infra error, new) ✓

## Test & Lint Results

- `python3 -m pytest -q` → **all pass** (504 tests across the suite; 28 snapshots
  passed; tool-adjacent `test_decoder.py` + `test_audit_coverage_matrix.py`
  green). No test references `diff_db.py` directly; `build_db.py` decode
  functions are referenced but were not changed semantically (only the HTTP
  call). Stated for the record: **diff_db.py has no dedicated tests.**
- `ruff check tools/diff_db.py tools/build_db.py` → **All checks passed!**
- `ruff format --check tools/diff_db.py tools/build_db.py` → **2 files already
  formatted** (applied `ruff format` to diff_db.py once during the fix).

---

_Fixed: 2026-06-09_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
