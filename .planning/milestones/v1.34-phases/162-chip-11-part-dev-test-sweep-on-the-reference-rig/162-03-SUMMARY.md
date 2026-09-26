---
phase: 162-chip-11-part-dev-test-sweep-on-the-reference-rig
plan: 03
subsystem: bench, rig-tooling
tags: [bench, rig-tooling, host-only, wave-3, renderer, gate-suite, no-hardware]

requires:
  - phase: 162-02
    provides: "bench/CHIP-EVIDENCE.jsonl's schema (record_keys, primary_arm, close01_counting_rule, chip_sc04_rule) and tools/append_chip_evidence.py"
provides:
  - "tools/render_chip_evidence.py — deterministic renderer with --check byte-compare, driving CHIP-EVIDENCE.md from CHIP-EVIDENCE.jsonl with no timestamp/hostname and a schema-driven row partition (no literal fallback)"
  - "bench/CHIP-EVIDENCE.md — the zero-row rendered document, --check green"
  - "run_gates.sh's two new live gates (render_chip_evidence.py --check, gate_record.py over CHIP-EVIDENCE.jsonl), suite now measured at 14/14 selftests + 7/7 live gates"
affects: [162-04, 162-05, 162-06, 162-07, 162-08, 162-09, 162-10, 166]

tech-stack:
  added: []
  patterns:
    - "Row partition driven entirely from _schema.primary_arm and record_keys' named_absence column — no schema.get(key, literal) fallback; a schema missing either discriminator is a named refusal (RenderError), never a guess"
    - "Two computed reconciliation statements per render: the close-out identity (validated + skipped == position_count_expected) and SC#4's three conjoined identities plus the 10 + N / 11 + N reading, both evaluated as equations over rows, never hand-counted"

key-files:
  created:
    - .planning/v1.34/tools/render_chip_evidence.py
    - .planning/v1.34/bench/CHIP-EVIDENCE.md
  modified:
    - .planning/v1.34/tools/run_gates.sh

key-decisions:
  - "Control rows are identified as `arm != primary_arm` rather than a literal `arm == 'control'` comparison — avoids baking any arm-value string into the partition logic beyond the one the schema itself names (primary_arm), since the schema's own prose (control_rerun_exclusion, chip_sc04_rule) is the only place the literal 'control' string is authoritative"
  - "The divergence table's six columns (chip, prior_disposition_source, prior_disposition, step_verdicts, divergence_verdict, known_carried) are asserted non-blank for every primary-arm row at render time — a None or empty-string cell is a RenderError, not a silently blank table cell; a not-measured-with-reason string is accepted as a value"
  - "The 'diverging' prefix ('diverges') used to evaluate SC#4's arithmetic is taken as a literal matching the schema's own chip_sc04_rule prose (which itself states 'divergence_verdict starts with \"diverges\"'), not read from a separate schema field — there is no such field in CHIP-EVIDENCE.jsonl's schema, and this mirrors the schema's own convention rather than introducing a hidden default for a row-partition discriminator"
  - "--selftest's fixture combines all 5 positive legs against one 4-row fixture (two v133 positions — one 'same', one 'diverges' — one control row arbitrating the diverging position, and one named-absence row) rather than isolated micro-fixtures per leg, matching the depth needed for Positive 4/5's arithmetic assertions without duplicating fixture-building code"

requirements-completed: []

coverage:
  - id: D1
    description: "render_chip_evidence.py renders CHIP-EVIDENCE.md deterministically (two renders byte-identical, no timestamp/hostname), --check is green on a fresh render and red with a unified diff on a one-byte drift (writes nothing), and the document carries the schema's close01_counting_rule verbatim, the 10 + N arithmetic with the 11 + N deviation on the same line, and a divergence-table section"
    requirement: "CHIP-03"
    verification:
      - kind: unit
        ref: "python3 render_chip_evidence.py --selftest (9/9 legs: 5 positive + 4 negative); direct render + --check against the real JSONL/target; byte-mutation negative check with stderr diff assertion"
        status: pass
    human_judgment: false
  - id: D2
    description: "The row partition (sweep positions vs. control re-runs) is driven entirely from _schema.primary_arm and record_keys' named_absence column, with no literal fallback — a schema missing both discriminators is refused by name rather than defaulted"
    requirement: "CHIP-04"
    verification:
      - kind: unit
        ref: "render_chip_evidence.py --selftest negative-4 leg; ast-based source scan asserting no BRINGUP-style literal leaked into the chip renderer"
        status: pass
    human_judgment: false
  - id: D3
    description: "run_gates.sh gates bench/CHIP-EVIDENCE.md and bench/CHIP-EVIDENCE.jsonl on every wave: two new live gate blocks, placed outside --quick, header's WHAT THIS RUNS list updated to name all seven; the suite measures 14/14 tool selftests + 7/7 live gates, exit 0, read directly; the negative control (a one-byte CHIP-EVIDENCE.md drift) is observed to fire, not merely configured, and the suite returns green after restore"
    requirement: "CHIP-01"
    verification:
      - kind: integration
        ref: "bash .planning/v1.34/tools/run_gates.sh; RC=$? (full and --quick, read directly, never piped); byte-mutation-then-restore negative control transcript"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-08-28
status: complete
---

# Phase 162 Plan 03: render_chip_evidence.py + run_gates.sh wiring Summary

**Built `tools/render_chip_evidence.py` — a deterministic, `--check`-able sibling to `render_evidence.py` that renders `bench/CHIP-EVIDENCE.md` from `bench/CHIP-EVIDENCE.jsonl` with a schema-driven row partition (no literal fallback) and a two-statement Reconciliation section (the close-out identity plus SC#4's `10 + N` arithmetic naming the roadmap's `11 + N` deviation on the same line) — then wired both a `--check` live gate and a `gate_record.py` live gate into `run_gates.sh`, measuring the suite at 14/14 tool selftests and 7/7 live gates, exit 0.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-08-28T16:52:00Z (approx, after the prior-wave tracking commit)
- **Completed:** 2026-08-28T17:04:05Z
- **Tasks:** 2/2 completed
- **Files modified:** 1 modified (`run_gates.sh`), 2 created

## Accomplishments

- `tools/render_chip_evidence.py` built as a full sibling to `render_evidence.py`: stdlib-only
  (`argparse`, `difflib`, `json`, `os`, `sys`, `pathlib`, plus `contextlib`/`io`/`shutil`/`tempfile`
  inside `--selftest` only), same determinism contract (no timestamp/hostname, deterministic row
  order, fixed-separator sorted-key nested-value JSON encoding, explicit LF atomic write). Row
  partition (`_partition_rows`) requires `_schema.primary_arm` and a `named_absence` entry in
  `record_keys` to both exist — neither ever falls back to a literal; a schema missing either is a
  named `RenderError`, not a guess. `--check`'s three exit shapes match the analog exactly: 0 on
  green, 1 on drift with a unified diff on stderr, 1 on a missing target — nothing written under
  `--check`.
- Document body: an H1 naming the milestone/phase read from the schema, a generated-by blockquote
  naming the exact `--check` command, a provenance paragraph, `## Close-out counting rule` printing
  `close01_counting_rule` verbatim, `## Positions (arm == 'v133')` over the full `record_keys` table,
  `## Excluded rows` over control re-runs with `control_rerun_exclusion` printed verbatim above it,
  `## Divergence table` (the 6 SC#3 columns, every cell asserted non-blank at render time — a
  not-measured-with-reason string counts as a value, a blank raises), and `## Reconciliation`
  carrying both computed statements.
- `--selftest` carries 9 named legs (5 positive + 4 negative), all green, over a single 4-row
  fixture (two `v133` positions — one `same`, one `diverges` — one `control` row arbitrating the
  diverging position, and one named-absence row):
  1. `positive 1: rendering twice is byte-identical`
  2. `positive 2: --check is green against a freshly rendered target`
  3. `positive 3: --check is red on a byte-mutated target with a named diff, writes nothing`
  4. `positive 4: reconciliation states 10 + N with the 11 + N deviation on the same line`
  5. `positive 5: a named-absence row counts in close-out but is excluded from SC#4`
  6. `negative 1: a row key outside record_keys is refused by name`
  7. `negative 2: line 1 without a _schema header is refused by name`
  8. `negative 3: --check against a missing target is refused by name, exit 1`
  9. `negative 4: a schema missing both the control-re-run and named-absence discriminators is refused, never defaulted`
- Rendered the real file: `bench/CHIP-EVIDENCE.md` (zero rows, since no position has been run yet).
  `--check` confirmed green against it immediately after.
- `run_gates.sh` gained two new live-gate blocks (both outside the `--quick` skip block), copying
  the existing four-part shape verbatim (banner, `if python3 …; then`, `FAILURES+=` else branch,
  `>&2` FAIL echo):
  - `live gate: render_chip_evidence.py --check (bench/CHIP-EVIDENCE.md vs a fresh render)`
  - `live gate: gate_record.py (bench/CHIP-EVIDENCE.jsonl record-shape gate)`
  The header comment's `WHAT THIS RUNS` list was extended from 5 to 7 live-gate entries.
- **Measured:** `bash run_gates.sh` — **14/14 tool selftests, 7/7 live gates, exit 0** (read
  directly, `RC=$?` on the next line, never piped). `bash run_gates.sh --quick` also runs both new
  gates and exits 0. `ls .planning/v1.34/tools/*.py | wc -l` = **14**.
- **Negative control, observed to fire:** appended one byte to `bench/CHIP-EVIDENCE.md`, ran
  `run_gates.sh --quick` — exited **1**, stderr named `render_chip_evidence.py --check`. Restored
  the file byte-for-byte from a pre-mutation backup; re-ran the suite — exited **0** again. The
  mechanism was seen to trip, not merely configured.
- `bench/EVIDENCE.jsonl` and `bench/EVIDENCE.md` confirmed byte-unchanged throughout (`git diff
  --quiet`). Both sub-repo porcelains (`git -C firestarter status --porcelain`, `git -C
  firestarter_app status --porcelain`) stayed empty for the whole plan.

## Task Commits

1. **Task 1: Build render_chip_evidence.py — deterministic render plus byte-compare** - `1f2bfd6e` (feat)
2. **Task 2: Add the two chip live gates to run_gates.sh and measure 14/14 with 7 live gates** - `842c671b` (feat)

**Plan metadata:** committed via this SUMMARY + STATE.md update (docs commit follows)

## Files Created/Modified

- `.planning/v1.34/tools/render_chip_evidence.py` — new, ~500 lines, 9-leg `--selftest`
- `.planning/v1.34/bench/CHIP-EVIDENCE.md` — new, rendered zero-row document
- `.planning/v1.34/tools/run_gates.sh` — two new live-gate blocks + header list update (18 lines added)

## Decisions Made

- **Renderer's document section list, as built (byte-for-byte matching the plan's spec, no
  divergence):** H1, generated-by blockquote, provenance paragraph, `## Close-out counting rule`,
  `## Positions (arm == 'v133')`, `## Excluded rows — divergence-arbitration control re-runs`,
  `## Divergence table`, `## Reconciliation` (two statements: close-out identity, then SC#4).
- **Control-row identification without a literal `'control'` string:** `arm != primary_arm` rather
  than `arm == 'control'`. The schema's own prose (`control_rerun_exclusion`, `chip_sc04_rule`)
  names the literal `'control'` value, but the code never repeats it as a comparison target — this
  is stricter than the plan required, chosen to keep the partition entirely anchored to the one
  field the schema declares (`primary_arm`) rather than a second implicit assumption.
  See "Deviations" — this is not a deviation, it satisfies the plan's literal instruction
  ("no literal fallback that could silently mis-count") with more margin than the minimum.
- **The "diverging" prefix (`"diverges"`) is a literal in the code,** matching the exact string the
  schema's own `chip_sc04_rule` prose specifies ("divergence_verdict starts with 'diverges'").
  This is not a forbidden hidden default because there is no schema field carrying this value to
  read instead — the prohibition targets row-partition discriminators with a schema-driven-with-
  fallback shape (the WRV analog's `bringup_cell_id_prefix`), not a prose-pinned string with no
  corresponding schema key at all.
- **Zero-row real render's reconciliation, exactly as first rendered:**
  `0 validated + 0 skipped-with-reason = 0 of 11 positions accounted for (11 not yet recorded).`
  and
  `SC#4: count(control)=0 == count(v133 rows whose divergence_verdict starts 'diverges')=0: holds. Every control row's control_rerun_for names an existing diverging v133 row: yes. No two control rows share the same control_rerun_for: yes. Total runs this cell records: 10 + N = 10 + 0 = 10 (the roadmap's reading is 11 + N = 11 + 0 = 11; this file deliberately uses 10, not 11, as the run-count base, because the 2516 is a named absence -- never seated, never run -- and contributes 0 to this term).`
  The identity holds vacuously at N=0, exactly as the plan anticipated.
- **Measured selftest/live-gate counts and exit code:** `tool self-tests run: 14 / 14`, `live gate
  PASS` count 7 (independently counted via `grep -c`), `ALL GATES PASSED`, `RC=0` — both full and
  `--quick` runs.
- **Negative-control transcript (verbatim outcome):** one-byte append to `CHIP-EVIDENCE.md` →
  `run_gates.sh --quick` exit 1, `FAILURES (1): - render_chip_evidence.py --check: bench/CHIP-EVIDENCE.md diverges from a fresh render -- hand-edit suspected` on stderr → file restored →
  `run_gates.sh --quick` exit 0, `ALL GATES PASSED`.

## Deviations from Plan

None — plan executed exactly as written. The control-row-partition choice (`arm != primary_arm`
instead of a literal `'control'` comparison) is a stricter reading of the plan's own "no literal
fallback" prohibition, not a divergence from its intent or any acceptance criterion.

## Known Stubs

None. The zero-row render is the plan's own expected output at this point in the phase (no chip
position has been seated or run yet) — not a stub, and explicitly anticipated in the plan's
`<action>` and `<success_criteria>` ("No part has been seated and no row exists").

## Threat Flags

None beyond what the plan's own `<threat_model>` already covers (T-162-13 through T-162-17,
T-162-SC). No new network endpoint, auth path, or schema change at a trust boundary was introduced.

## Issues Encountered

- The first draft of the module docstring's "do not copy" note quoted the WRV analog's literal
  `schema.get("bringup_cell_id_prefix", "BRINGUP-")` snippet and referenced `"BRINGUP-"` directly.
  Task 1's own acceptance script asserts no uppercase `BRINGUP` substring appears anywhere in the
  non-comment source (a docstring counts) — a Rule 3 blocking-issue fix, caught immediately by
  running the acceptance script before moving on: the docstring was reworded to describe the same
  contrast without quoting the literal identifier or its default string. No behavior changed; only
  documentation prose.

## Next Steps

Plan 162-04 extends `render_steps.py`'s existing gate block with the procedure's second step-list
section (`## Chip-sweep step list`, ids `C-01`...`C-09`) — it does **not** add an eighth live gate,
keeping the count at 7 per PD-2. Plans 162-05 through 162-10 will append rows to
`bench/CHIP-EVIDENCE.jsonl` via `append_chip_evidence.py`; every append should be followed by a
`render_chip_evidence.py` (no `--check`) to keep `CHIP-EVIDENCE.md` in sync, then `run_gates.sh
--quick` to confirm the `--check` gate stays green before committing.

## Self-Check: PASSED

All created/modified files verified present on disk (`render_chip_evidence.py`,
`bench/CHIP-EVIDENCE.md`, `run_gates.sh`'s two new gate blocks); both task commit hashes
(`1f2bfd6e`, `842c671b`) verified present in `git log --oneline --all`.
