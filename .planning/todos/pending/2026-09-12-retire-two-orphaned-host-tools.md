---
created: 2026-09-12T16:30:00Z
revised: 2026-09-12T17:10:00Z
title: Host tools/ have no declared consumer — a code-level scan cannot tell a live operator tool from a dead one
area: tooling
found_in_phase: 187
files:
  - firestarter_app/tools/ (all 24 scripts — the missing invocation contract)
  - firestarter_app/tools/ci_replica_venv.sh (live operator tool, misread as an orphan — see below)
  - firestarter_app/tools/derive_sdp_partition.py (live operator tool, misread as an orphan)
---

## CORRECTION — this todo originally said the wrong thing

As first written on 2026-09-12 this item proposed **deleting** `ci_replica_venv.sh` (363 lines)
and `derive_sdp_partition.py` (263 lines) as unambiguous dead weight, on the evidence that no
workflow, test or script references either. **That conclusion was wrong and acting on it would
have destroyed two working verification tools.**

Both are live and operator-invoked, recorded in `.planning/STATE.md`:

- `ci_replica_venv.sh` — `STATE.md:579-582`: run as a whole-milestone verification leg beside
  `ci_parity.sh`, reporting `CI-REPLICA: PASS`, `mypy 33/35` with the watermark explicitly not
  moved, `129` source files checked. It is the tool that reproduces CI's Python 3.11 locally,
  against a devcontainer that is 3.12 — a known masking hazard.
- `derive_sdp_partition.py` — `STATE.md:768-770`: *"Re-ran against the cached pinned-commit XML:
  PASS, 43/41/84, zero disagreement"*, checked against `sdp_capability_for_entry` and the
  committed partition. `STATE.md:2482` records a deliberate design decision that it duplicates
  `_select_0x0d_chips` locally rather than importing from `tests/`, *"the script must stay fully
  standalone"* — a tool nobody intends to keep would not have earned that decision.

## The real problem, which the error demonstrates

A tool invoked by a human from a procedure recorded only in `.planning/` prose is, to **any**
code-level scan, indistinguishable from a dead one. Reference counts over workflows, tests and
scripts return zero for both a genuinely orphaned script and a load-bearing operator tool.

That is not a hypothetical failure mode. It is the mistake this todo made on its first write,
using exactly the scan a future cleanup pass would use — and the cleanup would have deleted the
operator's CI-parity harness.

## What to do instead of deleting

Give every script in `firestarter_app/tools/` a declared consumer, so the question "is this
live?" is answerable from the file itself rather than by grepping a 52k-line `STATE.md`:

1. **Each tool states who runs it and when** — CI (naming the workflow step), the test suite
   (naming the test), an operator procedure (naming the procedure), or a closed phase (in which
   case it is a retirement candidate).
2. **Operator-run tools are the priority**, since they are exactly the class that scans
   misclassify. `ci_replica_venv.sh`, `ci_parity.sh` and `derive_sdp_partition.py` are the
   known members; there are likely others among the 24.
3. **Only then** is a deletion pass safe, and its criterion becomes "declares no consumer, and
   none can be found" rather than "no code references it".

Constraint: whatever form the declaration takes must respect `CLAUDE.md`'s non-overridable
no-comments rule for anything under `firestarter_app/`. A `--help` string or an `argparse`
description is user-facing text, not commentary, and is the natural carrier; a comment block is
not available. This needs settling before the pass, not during it.

## Context

`.planning/notes/host-tools-checker-apparatus-audit.md` — and note that the audit's own
"unambiguous dead weight" section has been corrected for the same error.
