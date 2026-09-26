---
quick_id: 260822-aq6
description: Surface run_count on every dev test disclosure surface and add a --fast flag whose weaker-test cost is stated
date: 2026-08-22
status: complete
branch: quick-devtest-runcount-fast
commits:
  - 6dd29a2 firestarter_app — run_count on every disclosure surface (schema 1.7)
  - 50df202 firestarter_app — dev test --fast + the weaker-run dedup guard
verification: 1911 tests pass on python 3.11 (the CI interpreter), 32 snapshots; ruff check + ruff format clean on the CI scope; mypy watermark at 35/35
bench: none — no hardware run is part of this task
---

# Quick Task 260822-aq6 — SUMMARY

## What the investigation found

The `read, read, write, write` ordering is **intentional**, and the mechanism
is v1.21 Phase 121's N≥2 repeat policy:

- `run_plan(..., runs: int = 2)`, with a **fail-closed** `runs < 2` guard that
  fails the whole plan — N≥2 was required, not merely defaulted.
- `read ×N` → `_dispatch_read` SHA-compares the runs and reports `divergence`
  as a metric only, never a verdict flip (D-06).
- `write / write-partial / verify / erase ×N` → `_dispatch_multi_run`; outcome
  disagreement yields `MARGINAL`. This is the AM27C020 write#1 60/64 vs
  write#2 0/64 detector (v1.18 Phase 99).

**But it was invisible.** `StepResult.run_count` was populated on every step
and read by nothing outside the test suite — absent from `_step_dict`, so
absent from the JSON artifact, the saved markdown and the filed issue body;
and the console table showed no run indication. On a clean run the repeat left
**no trace at all**; the only time it surfaced was a failure. That is the
defect this task fixes.

## Delivered

### 1. `run_count` on all four disclosure surfaces (`6dd29a2`)

Found **three** other surfaces, not the two the request assumed:

| Surface | Change |
|---|---|
| `diagnostic_report._step_dict` | `run_count` key — reaches JSON, and via `to_json_block()` the markdown file and issue body |
| `DiagnosticReport.render()` | new `xN` cell per step row, via `_runs_cell` |
| saved `dev-test-<chip>.md` | new `Runs` column |
| `submit.build_body` (issue body) | new `Runs` column, via `_runs_text` |

`SCHEMA_VERSION` 1.6 → 1.7. Additive **inside** `steps[]` only — the
top-level shape `tools/parse_devtest_issue.py` consumes is untouched, and both
markdown formatters render `-` for a report that predates the key.

Verified end to end: a default run renders `read x2 / write x2 / verify x2 /
erase x2 / blank-check x1`; a `--fast` run renders `x1` throughout.

### 2. `dev test --fast` (`50df202`)

`run_plan` gained `allow_single_run`. The `runs < 2` guard **stays
fail-closed** for every existing caller, and `runs < 1` fails regardless, so
an accidental `runs=1` still costs nothing. `--fast` opts in explicitly and
must say so twice (`runs=1` *and* `allow_single_run=True`).

The help text names the cost, not just the speed:

> Run each step once, not twice. WEAKER TEST: with nothing to compare, an
> intermittent write cannot be reported marginal and read nondeterminism goes
> unmeasured; such reports never count toward community agreement. Omit it for
> the accurate test.

The docstring states the default is the accurate one. The cost is **proven**,
not asserted: `test_single_run_write_cannot_report_marginal` runs the exact
operator that yields `marginal` at `runs=2` and shows it reporting a confident
OK at `runs=1`.

### 3. The dedup guard — required, not scope creep (`50df202`)

`parse_devtest_issue.count_agreeing` groups filed reports by the **embedded**
`dedup_fingerprint` and never re-hashes. Without a discriminator, two `--fast`
runs could have promoted a chip that no accurate run ever passed. Phase 121
D-06/D-08 already set the precedent — `write-partial` hashes differently from
`write` precisely so a weaker run cannot join a stronger run's group.

New `chip_test.repeat_policy_tag(results)` derives the policy from the results
themselves (`run_count == 1` over `_MULTI_RUN_OPS | {OP_READ}` — never the SDP
leg's by-design `1`s), and `dedup_fingerprint` appends it **only when
non-empty**. Deliberate consequence: every accurate run's fingerprint is
byte-identical to the ones already filed, so unlike v1.30 D-11 **no**
historical grouping or promotion count resets. Proven by
`test_dedup_fingerprint_unchanged_for_any_non_degraded_run_count`.

`doc/community-validation.md` gained a paragraph parallel to its existing
"Why a partial-region write can never poison the N≥2 count" section — that
section's claim would otherwise have read as complete while a second case
existed.

## Decisions recorded rather than smuggled

- **D-05 zero-option surface REVERSED for one option.** `dev test` had a
  recorded zero-option surface since Phase 121 D-05, gated by
  `TestZeroOptionSurface::test_dev_test_accepts_no_options` asserting
  `options == []`. The gate is **narrowed** to pin the set exactly (`{fast}`),
  not deleted; the sibling tests proving `--destructive`, `--output-dir`,
  `--submit` and `-y` are still rejected are untouched. The reversal is stated
  in the class docstring.
- **v1.30 LEG-01 narrowed.** `test_derive_plan_allow_dev_test_exposes_zero_
  cli_options` was written as `options == []` when "the SDP leg adds no
  option" and "the command has no options" were the same sentence. They no
  longer are. Renamed to `test_derive_plan_allow_adds_no_cli_option` and
  pinned to the set, keeping LEG-01's actual claim testable.
- **`--help` ceiling 14 → 16.** The entire increase is the Options block the
  flag brings with it (two docstring lines + four wrapped help lines). Kept as
  a *tight* pin at the real number so the next accidental growth still trips.
- **Three surfaces, not two.** The request said "the step dict and the 2
  others"; `submit.build_body` is a fourth and was included — without it the
  community triage path, the one place a stranger's report is read, would not
  show the repeat policy.

## Verification

| Gate | Result |
|---|---|
| `pytest tests/` on **python 3.11** (CI's interpreter) | 1911 passed, 32 snapshots, 0 failed |
| Collected-test delta | 1898 → 1911 = **+13**, measured before/after on the same interpreter |
| `ruff check` / `ruff format --check` on `firestarter/ tests/` (CI scope) | clean |
| `tools/check_mypy_watermark.py` | 35 errors, watermark 35 — **at** watermark |
| Both intermediate commits | each verified green before committing |
| End-to-end console + md + JSON, default vs `--fast` | inspected; dedup fingerprints differ (`ed3f19d0…` vs `a9da3739…`) |

Notes on the environment, since local green is not CI green: the devcontainer's
python is 3.12 and `tools/check_mypy_watermark.py` **fails open there** on an
unrelated numpy-stub syntax error (confirmed identical with these changes
stashed). Every number above was measured in a purpose-built python 3.11 venv.
The two mypy errors this task initially introduced (`int()` needing
`call-overload` rather than `arg-type`; a second `Group.commands` subscript in
a new test) were only visible there and are fixed.

## Not done

- No firmware change — host-only.
- No bench run. Nothing here needs hardware, but nothing here has *seen*
  hardware either.
- The default `runs=2` is unchanged, per the operator's direction that
  accuracy is the goal.
- Branch `quick-devtest-runcount-fast` in both repos is **unmerged**.
