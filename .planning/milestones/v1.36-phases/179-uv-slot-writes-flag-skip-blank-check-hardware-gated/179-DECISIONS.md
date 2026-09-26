# Phase 179 Plan 02 — Decisions

## D-179-1: Option A — split criterion 4 across a committed firmware-faithful-double regression (plan 179-03, no skip marker) plus a blocking-human bench wave producing a committed 179-MEASUREMENT.md (plan 179-04), per the Phase 176-05 precedent; the committed test proves HOST logic and the bench artifact proves HARDWARE, and neither alone is criterion 4 — the operator accepted that stated cost.

Rationale: `179-RESEARCH.md` Q4 found no hardware-gated pytest test anywhere in this repository and no precedent for a fifth `ALLOWED_SKIP_REASONS` entry (Option B) or a bench-only shell script outside the suite (Option C). Option A is the recommended route from `179-PATTERNS.md`'s "No Analog Found" table and matches the Phase 176-05 precedent for a committed measurement artifact backing a hardware claim.

## D-179-2: Option A — real-path construction via `_build_real_path_report(chip="m27c512", write_scope="full", operator=<WriteInitPreflightChip seeded with content outside the top slot>, runs=2)`, so the frozen hash is of what the engine actually produces, accepting the coupling to `derive_plan` / `chip_database.json` regeneration that every other real-path shape already has.

Rationale: `179-01` already landed the witness form, the adjudicated verdict, and the flag composition; a real-path build proves the actual witness, the actual positional flag, and the actual adjudicated blank-check verdict, which is the entire reason UV-01/UV-02 wanted this shape. Option B (hand-specified via `build_shape_from_step_specs`) would freeze a `StepResult` combination the engine might never actually produce and would prove nothing about the flag, witness, or adjudication.

Both are this plan's own recommended defaults. Task 2 and plan 179-03 follow their default branches; the plan's inline "Option B/C alternate edits" are NOT taken.
