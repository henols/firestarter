---
title: Phase-gate expiry discipline — make every new gate answer "when does this stop earning its keep?"
trigger_condition: a tooling/hygiene milestone is scoped, OR the per-gate retirement research question is answered, OR the next time a phase plan proposes a new check_*.py gate
planted_date: 2026-09-12
status: dormant
---

# Phase-gate expiry discipline

## The pattern this is aimed at

`firestarter_app/tools/` accumulated ten `check_*.py` gates, 3,984 lines plus 3,537 lines of
their own tests, guarding a 21,153-line product. Each gate locks in exactly one decision from
exactly one phase. None was ever retired. All ten now report zero findings on every run.

The gates are individually well built — they report their scan surface, carry planted-violation
fixtures, and fail closed. The failure is not in any one gate. It is that **nothing in the
process ever asks a gate to justify its continued existence**, so the only possible direction of
travel is accumulation.

## The idea

Give every new phase gate an expiry question at the moment it is created, and re-ask it at
milestone close:

- When a plan proposes a `check_*.py` gate, it states **what the gate prevents that a unit test
  cannot**. If the answer is "nothing, but it is broader", that is a unit test, not a gate.
- The gate records a **retirement condition** in its own header — the concrete circumstance
  under which it should be deleted (e.g. "retire once `sdp_capability.py`'s allow-set is
  derived rather than hand-maintained").
- Milestone close asks, once, of each gate: *what breaks if this is deleted, that the existing
  unit tests would not already catch?* A gate with no answer is retired, not carried.

## Why a seed and not a todo

Answering this well depends on the per-gate retirement analysis (see
`.planning/research/questions.md`) — without it, a blanket rule would either retire gates that
are load-bearing or add ceremony that changes nothing. Plant now, act once the analysis exists.

## Prior art in this project

The retirement instinct already exists and has been exercised correctly: the meta-repo's
`Catalog sync check` workflow was deleted outright in Phase 185 once it was shown it could not
assert what it claimed (`.planning/notes/catalog-sync-check-retirement.md`), and the
`tools/wiki/` checkers were retired wholesale on 2026-09-02. Both were operator-initiated at
the moment the gate was examined. The gap is that examination is not scheduled — it happens
only when someone happens to read the directory, as in the exploration that produced this seed.

## Context

`.planning/notes/host-tools-checker-apparatus-audit.md`
