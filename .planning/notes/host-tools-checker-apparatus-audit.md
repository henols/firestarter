---
title: Host tools/ checker apparatus — measured mass, per-gate ratios, and the one-shot-gate diagnosis
date: 2026-09-12
context: /gsd-explore session during v1.37 Phase 187; operator was reading through firestarter_app/tools/ suspecting over-engineering. All figures measured live against the working tree at that date, not estimated.
---

# Host `tools/` checker apparatus — audit

## VERDICT

The operator's over-engineering suspicion is **confirmed on mass and disproportion**, and
**refuted on quality**. The ten `check_*.py` gates are well built — they are simply one-shot
phase gates that were never retired, and they have accumulated to roughly the size of the
product they guard.

## Where the scripts actually live

`firestarter/tools/` holds **only** the catalog (`codegen.py`, `codegen_vectors.py`,
`messages.toml`, `frame-vectors.toml`). The firmware sub-repo has no checker family at all.
The entire mass is in `firestarter_app/tools/` — 24 scripts, ~10,300 lines of Python plus
two shell scripts.

## Measured mass

| | lines |
|---|---|
| Product — `firestarter_app/firestarter/*.py` | 21,153 |
| The 10 `check_*.py` gates | 3,984 |
| Test files named for a checker (`tests/test_check_*.py`) | 3,537 |
| **Checker apparatus — lower bound** | **7,521** |
| Checker apparatus — upper bound (any test file mentioning a checker) | 19,514 |
| All of `tests/*.py` | 62,909 |

The two bounds differ because a test file that merely *mentions* a checker name is counted in
full by the upper measure, and files are counted once regardless of how much of their content
is checker-related. The honest statement is **7,521–19,514 lines**; even the floor is 36% of
the product codebase.

## Per-gate ratio

| Gate | gate LOC | its tests LOC | guards | target LOC |
|---|---|---|---|---|
| `check_sdp_capability_invariants.py` | 364 | 248 | `firestarter/sdp_capability.py` | 246 |
| `check_protection_readability_invariants.py` | 524 | 394 | `firestarter/protection_readability.py` | 935 |
| `check_diagnostic_report_claims.py` | 269 | 119 | `firestarter/diagnostic_report.py` | 1,147 |
| `check_no_community_support_status_write.py` | 261 | 232 | `firestarter/diagnostic_report.py` | 1,147 |

`check_sdp_capability_invariants` is 612 lines of gate-plus-tests guarding a 246-line file —
**2.5:1**.

## What CI actually invokes

Exactly one checker is named in `firestarter_app/.github/workflows/ci.yml`:
`check_mypy_watermark.py`. The other nine reach CI only indirectly, through `pytest tests/`,
and only where their test file runs them against the real tree rather than against a fixture.
That indirection is real but is not uniform across the ten, and was not resolved per-gate in
this session — see the research question below.

## Live-run result (all ten, against the real tree, 2026-09-12)

Nine exit 0. `check_mypy_watermark` exits 2 in the devcontainer **only** because Python 3.12
rejects numpy's `.pyi` type statements; CI pins 3.11 and is unaffected. This is the known
devcontainer-masking effect, not a gate defect.

**Every one of the ten reports what it scanned** — `scanned ../firestarter/sdp_capability.py`,
`scanned 78 file(s)`, `all 746 chips scanned; 736 supported`. None is a silent zero-scan gate.
They carry planted-violation fixtures, and `check_mypy_watermark` deliberately **fails closed**
on mypy's rc=2 rather than reading a tool crash as a clean tree. On construction quality these
are above the bar, and the audit should not be read as criticising how they were written.

## The diagnosis

Each gate locks in exactly one decision from exactly one phase — SDP capability, protection
readability, no-logging-inside-the-SDP-timing-window, `is_memory_cmd()` carrying no `#ifdef`.
The decision shipped, unit tests were written for it, and the AST checker then stayed on the
payroll permanently. All ten now report **zero findings on every run**, which is the signature
of a gate whose risk is no longer live.

The retirement question is one sentence per gate: *what breaks if this is deleted, that the
existing unit tests would not already catch?*

## Second finding: tools doing GSD's work, inside the product repo

Raised by the operator mid-session and confirmed. Several tools in `firestarter_app/tools/` are
not product tooling at all — they are GSD process bookkeeping that was committed into the
shipped package repo.

Measured by counting planning vocabulary per file:

| tool | LOC | `.planning` refs | phase/plan refs | `D-NN` | REQ-shaped IDs |
|---|---|---|---|---|---|
| `audit_coverage_matrix.py` | 1,924 | 13 | 12 | 10 | 31 |
| `diff_db.py` | 984 | 9 | 19 | 9 | 13 |
| `measure_plan_shapes.py` | 370 | 0 | 5 | 5 | 2 |
| `snapshot_report_shapes.py` | 190 | 0 | 2 | 2 | 3 |
| `measure_part_number_delta.py` | 303 | 0 | 1 | 1 | 1 |

Their own docstrings state it plainly:

- `measure_plan_shapes.py` — *"Generator for the committed plan-shape pin (Phase 175,
  D-10/D-11/D-16, plan 175-03) -- the frozen half of D-10's no-drop proof."*
- `measure_part_number_delta.py` — *"(Phase 174, D-14/D-15/D-16, GATE-04, plan 174-04 task 3)"*
- `snapshot_report_shapes.py` — *"(Phase 174, GATE-05, D-01, D-07)"*
- `audit_coverage_matrix.py` — *"Wave 1 lands §1 (Summary Statistics) + §2 (DB Count
  Reconciliation). §3/§4/§5 are placeholder headers populated by Waves 2-4 (Plans 11-03 / 04 /
  05)."*

### The structural case, not the stylistic one

`audit_coverage_matrix.py` is the clearest instance and it is broken, not merely misplaced. Its
own source comment says:

> the tool lives at `<repo-root>/firestarter_app/tools/audit_coverage_matrix.py`, so the repo
> root is three `dirname()` hops up

Resolved live, `_REPO_ROOT` is `/workspaces` — **the meta repo**. So a script committed inside
the published pip-package repo climbs out of its own submodule to write
`.planning/v1.3-COVERAGE-MATRIX.md` (184 KB, tracked in meta) and to mutate
`.planning/v1.3-defect-coverage-ids.json`.

The consequence for anyone who is not this operator: in a standalone clone of
`henols/firestarter_app`, the same three-hop arithmetic resolves to the **parent of the clone
directory**, and the tool writes a `.planning/` tree outside the repository entirely. The tool
is only correct under one person's submodule layout.

### It also breaks the project's own hard rule

`CLAUDE.md` states, non-overridably, that no GSD process commentary may appear in source under
`firestarter/` or `firestarter_app/` — *"no `// Phase NNN (REQ-NN):`, no `// D-06`, no
plan/task/milestone citations… The reader of the firmware or the pip package does not have
`.planning/` and never will."* The docstrings quoted above are exactly that, and they sit under
`firestarter_app/`. This is consistent with the known-incomplete host-side provenance sweep;
`tools/` is where the remainder is concentrated.

The two findings compound in a way worth stating: these citations **cannot** simply be stripped,
because without them the tools are unexplainable — a generator whose only reason to exist is
"the frozen half of D-10's no-drop proof" has no product-facing rationale to substitute. That
inability to write a product-facing docstring is the diagnostic: the tool does not belong in the
product repo at all.

## Unambiguous dead weight (no analysis needed)

- `tools/ci_replica_venv.sh` — 363 lines, referenced by **nothing**: no workflow, no test, no
  other script.
- `tools/derive_sdp_partition.py` — 263 lines, zero test files, one stray mention.

## Adjacent finding, out of scope here

`frame-vectors.toml` and `codegen_vectors.py` are duplicated in both sub-repos with **no**
meta-canonical copy and are absent from `sync_to_subrepos.sh`'s `FILES=(messages.toml
codegen.py)`. Measured consequence: the two synced files are byte-identical across all three
repos, while the unsynced `codegen_vectors.py` has already drifted between the sub-repos
(`01fb1a9b` firmware vs `53b4190d` host — comment-only, output unaffected). A CI gate is *not*
the remedy; that route was already tried and retired (see
`catalog-sync-check-retirement.md`). Folding the two files into the existing sync script is.
