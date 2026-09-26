---
created: 2026-09-12T16:30:00Z
revised: 2026-09-12T17:10:00Z
title: Host tools/ have no declared consumer — a code-level scan cannot tell a live operator tool from a dead one
area: tooling
found_in_phase: 187
resolves_phase: 188
resolved: 2026-09-13
status: closed
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

## CLOSED — Phase 188 (2026-09-13)

**This phase *is* this todo.** The operator answered it with the same subtraction he applied to
everything else in `firestarter_app/tools/`: *"I believe that they aren't bringing any value at all
to the projects."* This todo's own recommendation — declare a consumer for every script, then
delete only what declares none — was **not implemented**. The declaration layer (both halves: the
convention and the fail-closed check that would assert it) was dropped on operator decision (D-12),
and the audit's blind spot this todo exists to name — a code-level scan cannot tell a live operator
tool from a dead one — is carried forward, not closed. See
`.planning/notes/host-tools-retirement.md` §2 cost 2 for the long form.

**The two tools this todo's correction names split, and the split matters.** Both
`ci_replica_venv.sh` and `derive_sdp_partition.py` — the two tools this todo's own first-write error
had misread as dead, then corrected to "live and operator-invoked" — are **deleted in this phase
anyway** (188-05). The irony this todo's own correction predicted is exactly what happened, but not
by the same error twice: this time the operator was shown, by name, that both tools were live
(`ci_replica_venv.sh`'s CI-parity role; `derive_sdp_partition.py`'s `STATE.md`-recorded standalone
verification role and its "keep it standalone" design decision) and chose to retire them **on
judgment about their value**, not on the reference-count evidence this todo's own correction had
already retracted. That is the distinction to keep straight for anyone reading this file later:
this todo was right the second time about what the scan could and could not see; the operator's
retirement of both tools in Phase 188 is a values decision made with that limitation disclosed, not
a repeat of the todo's original mistake. Full account: `.planning/notes/host-tools-retirement.md`
§1 (line counts, per-tool disposition) and §2 cost 4 (the judgment-vs-reference-count distinction,
stated for `derive_sdp_partition.py` specifically).

No successor guard and no backlog item were filed for the declaration-layer gap this todo names —
that is Phase 188's own deliberate choice (D-23), recorded in the verdict note, not an omission here.
