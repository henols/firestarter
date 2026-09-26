---
phase: 61-list-search-display-correctness-and-table-layout
fixed_at: 2026-06-10T11:18:00Z
review_path: .planning/phases/61-list-search-display-correctness-and-table-layout/61-REVIEW.md
iteration: 1
findings_in_scope: 2
fixed: 2
skipped: 0
status: all_fixed
---

# Phase 61: Code Review Fix Report

**Fixed at:** 2026-06-10T11:18:00Z
**Source review:** .planning/phases/61-list-search-display-correctness-and-table-layout/61-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 2 (WR-01, WR-02 — critical_warning scope)
- Fixed: 2
- Skipped: 0

> Cross-repo note: all source fixes live in the `firestarter_app` submodule and
> were committed there on branch `v1.11-infoic-decode-correctness`. The commit
> SHAs below are submodule commits. The meta-repo `firestarter_app` gitlink was
> intentionally left pinned (not bumped).

## Fixed Issues

### WR-01: Fallback label from `get_chip_type_string` overflows the 12-char Type column

**Files modified:** `firestarter/eprom_info.py`
**Commit:** `8512324`
**Applied fix:** In `print_eprom_list_table`, clamp the resolved Type label to 12
characters (`type_str_display = type_str[:12]`) before the fixed-width
`{type_str_display: <12}` cell formatting, so protocol-based fallback labels
(13–39 chars, e.g. legacy/operator-override entries lacking `electrical-type`)
can no longer rupture table column alignment.

**Deviation from REVIEW.md fix direction (verified, intentional):** The review
guidance suggested clamping "in BOTH views." After confirming the actual info-view
rendering (`present_eprom_details`, `eprom_info.py:233` →
`f"{'Type:': <{pos}}{chip_data.get('type_str')}"`), the info view is a *free-form
line with no fixed-width Type cell* — it deliberately shows the full descriptive
label and cannot overflow a column. Clamping it would be a presentation regression.
The D-04 parity invariant concerns the shared label *source* (`resolve_type_label`),
which both views already call identically; it does not require identical truncation.
The clamp was therefore applied only to the list view, where the fixed-width
overflow actually occurs. This preserves D-04 (single-helper source) while fixing
the alignment bug.

### WR-02: `vpp_str` fallback value diverges between list and info views

**Files modified:** `firestarter/eprom_info.py`
**Commit:** `279e771`
**Applied fix:** In `print_eprom_list_table`, changed the list-view VPP fallback
from `f"{ic.get('vpp_volts', '-')}v"` (→ `"-v"`) to
`f"{ic.get('vpp_volts', 'N/A')}v"` (→ `"N/Av"`), matching the info view's
`f"{eprom_data.get('vpp_volts', 'N/A')}v"` fallback in
`build_specifications` (`ic_layout.py:578`). Now when the D-03 gate passes
(`vpp_mv > 0` AND `etype != "SRAM"`) but `vpp_volts` is absent (e.g.
operator-override entries), both views render the identical `"N/Av"` string,
restoring the D-03 list-vs-info parity guarantee.

Aligned to the `"N/A"` convention (the review's first suggested direction) rather
than suppressing the cell, because the list table's VPP column is fixed-width and
always renders a cell — suppression is not available in the table layout the way
key-omission is in the info view. Aligning the fallback string is the minimal
change that yields byte-identical output across both views.

## Verification

- `python -m pytest tests/test_eprom_info.py -q` → 35 passed.
- `python -m pytest -q` (full suite) → all passed, 28 snapshots passed; only
  environment-related skips (meta-repo ledger / firmware checkout absent in
  standalone worktree). No regressions; no snapshot drift.
- `ruff check firestarter/eprom_info.py` → All checks passed.
- `ruff format --check firestarter/eprom_info.py` → already formatted.
- Both edits confirmed present and surrounding code intact (Tier 1); Python
  `ast.parse` clean (Tier 2).

Both findings are presentation/string-formatting fixes (not logic-control
branches), fully exercised by the existing parity and width tests once the
fallback paths are reasoned about, so neither is flagged for human logic review.

## Skipped Issues

None.

---

_Fixed: 2026-06-10T11:18:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
