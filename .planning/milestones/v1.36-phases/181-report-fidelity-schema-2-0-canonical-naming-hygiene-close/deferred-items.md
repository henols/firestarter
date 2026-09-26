## Deferred Items

- `tests/test_blast_radius_invariance.py:565` fails `ruff format --check` (a
  wrapped multi-line expression the formatter would reshape differently).
  status: **CLOSED — the "pre-existing" finding was misattributed, and it was ours**

  **Originally logged as:** pre-existing at app HEAD `ddc0c1c`, out of scope per
  the Scope Boundary rule, ~380 lines from plan 181-05's own edits.

  **Why that was wrong.** `ddc0c1c` is the **wave-3 tip**, not the phase base.
  Measured against the real phase base `04fd982`, `ruff format --check
  firestarter/ tests/` is **clean — 171 files already formatted**. At `ddc0c1c`
  it reports **2 files would be reformatted**. So the finding was introduced by
  this phase's own waves 1-3, not inherited from before it. Comparing against
  the tip of the work already done will call almost any regression
  "pre-existing"; the phase base is the only honest baseline.

  **Why it mattered.** `ruff format --check firestarter/ tests/` is a Host CI
  gate in this repo, so leaving it open would have shipped a red CI, not a
  cosmetic nit.

  **Resolution.** Both affected files — `tests/test_blast_radius_invariance.py`
  and `tests/test_erase_flag_invariants.py` — formatted in `5a21ce2`. Neither
  is under `tests/golden/`, so this does not hit the known
  `ruff format` vs byte-identical-golden gate loop. All 19 `FROZEN_HASHES`
  literals verified byte-identical across the reformat (md5 of the sorted
  literal set unchanged); 108 tests in the two files pass; `ruff check` and
  `ruff format --check` both green over CI's exact scope (174 files).

**Standing lesson for the remaining plans:** measure "pre-existing" against the
phase base `04fd982`, never against the current tip.
