---
created: 2026-09-12T16:30:00Z
title: Retire two orphaned firestarter_app/tools scripts — ci_replica_venv.sh and derive_sdp_partition.py
area: tooling
found_in_phase: 187
files:
  - firestarter_app/tools/ci_replica_venv.sh (363 lines — referenced by no workflow, no test, no other script)
  - firestarter_app/tools/derive_sdp_partition.py (263 lines — zero test files, one stray mention)
---

## Problem

Two scripts in `firestarter_app/tools/` have no live caller. Measured 2026-09-12 against the
working tree:

| script | lines | workflows naming it | test files naming it | other scripts naming it |
|---|---|---|---|---|
| `ci_replica_venv.sh` | 363 | 0 | 0 | 0 |
| `derive_sdp_partition.py` | 263 | 0 | 0 | 1 |

`ci_replica_venv.sh` is referenced by nothing at all. `derive_sdp_partition.py` has a single
stray mention and no test coverage.

Both sit in `firestarter_app/tools/`, which is outside every CI gate — no mypy, no `ruff check`,
no `ruff format`. So they are unexecuted, unlinted, untyped, and untested, while still reading
as part of the project's tooling surface to anyone browsing the directory.

## Why it is worth doing

626 lines removed for no behavioural change, and one less pair of scripts a future reader has to
understand before concluding they do nothing. This is the unambiguous slice of the wider
checker-apparatus question — it needs no per-gate analysis, unlike the ten `check_*.py` gates.

## Before deleting

1. Confirm the single `derive_sdp_partition.py` mention is not a live invocation path —
   locate it and read it, do not trust the count alone.
2. Confirm `ci_replica_venv.sh` is not referenced from the firmware sub-repo or from
   `.planning/` runbooks that an operator still follows by hand. A script invoked only by a
   human from a documented procedure is not an orphan, and the reference scan above covered
   code and workflows, not prose.
3. Check whether `ci_parity.sh` (162 lines, also CI=0/tests=0) is the surviving half of the
   same pair — if the two were built together, decide them together rather than leaving one.

## Context

Full measurements, per-gate ratios and the wider diagnosis:
`.planning/notes/host-tools-checker-apparatus-audit.md`.
