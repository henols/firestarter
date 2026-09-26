# Deferred Items — Plan 112-01

Out-of-scope issues discovered during verification but NOT caused by this
plan's changes (`firestarter_app/firestarter/chip_test.py`,
`firestarter_app/tests/test_chip_test.py`). Logged per scope-boundary rule;
not fixed.

- `tests/test_diagnostic_report.py:519` — `ruff check` F841: local variable
  `table` assigned but never used (`table = report.render()  # must not
  raise`). Pre-existing; file untouched by this plan (`git status --short`
  shows no diff).
- `tests/test_validate_family_cmd.py` — `ruff format --check` reports the
  file "would reformat". Pre-existing; file untouched by this plan.
