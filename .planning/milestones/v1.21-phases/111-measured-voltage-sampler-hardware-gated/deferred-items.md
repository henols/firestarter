# Deferred Items — Phase 111

## 111-01: Pre-existing ruff F841 unmasked in test_diagnostic_report.py (out of scope)

- **File:** `firestarter_app/tests/test_diagnostic_report.py:519`
- **Line:** `table = report.render()  # must not raise` (inside the pre-existing `test_full_report_all_four_sub_objects_single_source`)
- **Issue:** `ruff check` now flags this as F841 (unused local variable). It appears ruff does not flag an assigned-but-unused variable when it is the very last statement in the module; Plan 01's addition of `test_voltage_split_fields_serialize` after it in the same file exposed the pre-existing issue.
- **Why deferred:** This line is untouched by Plan 01's diff (`git diff` confirms only additions after it), and Plan 01 explicitly prohibits modifying any existing test body (SC3-equivalent constraint). Fixing it is out of this plan's scope per the scope-boundary rule (only auto-fix issues directly caused by this plan's changes).
- **Suggested fix (future plan):** Either remove the `table =` assignment (replace with a bare `report.render()  # must not raise` call) or add an assertion using `table`, in whichever future plan next touches `test_diagnostic_report.py`.

## 111-UAT: Before/after write-step voltage capture → Phase 112 re-verify

- **What:** SC2's destructive-run half — confirm `vpp_before_mv`/`vpp_after_mv`/`vpe_before_mv`/`vpe_after_mv` populate with real measured values around a live write step, on an electrically-erasable chip (W27C512 / W29C020).
- **Why deferred:** No write-step call site invokes `sample_vpp_mv()`/`sample_vpe_mv()` in Phase 111 by design — Plan 111-03's objective and the ROADMAP both assign that orchestrator wiring to Phase 112. `111-VERIFICATION.md` classifies this as informational/tracking-only, explicitly NOT a Phase 111 gap.
- **Disposition:** Reclassified out of Phase 111's blocking UAT test set per operator decision (2026-07-03) so Phase 111 could complete; the sampler + report landing site (Phase 111's actual scope) are fully verified.
- **Re-verify in Phase 112:** After the `dev test` orchestrator wires the sampler around `run_plan`, run a write on W27C512/W29C020 and confirm the before/after voltage fields track real rail behavior (e.g. a sag from ~20.9V to ~17.4V is visible and diagnosable).
