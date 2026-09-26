---
title: dev test — hard-fail on unknown chip (case A) vs run-the-sweep on unsupported (case B)
date: 2026-07-03
context: Captured during /gsd-explore 2026-07-03. Refines the Phase-112 dev test handler behavior. Companion to dev-test-design-decisions.md.
---

# `dev test <chip>` — fail fast when the chip is absent, but only then

Records the decision (and the subtle distinction behind it) so a future editor doesn't
"fix" the wrong branch and quietly break community validation.

## The two "can't really test this" cases

There are two superficially-similar situations that must be handled **oppositely**:

- **Case A — name absent from the DB.** `db.get_eprom(chip)` returns nothing. There is no
  plan to run, no protocol, no expected chip-ID. → **Hard-fail.**
- **Case B — in the DB but its `support_status` would refuse it** (`adapter-required`,
  unimplemented, community-* ladder states). `resolve_chip` would raise, but the chip
  entry exists and has real fields. → **Still run the sweep.** This is the *entire point*
  of the community-validation command — proving support on chips the maintainer can't.

## Decision

- Case A **hard-fails directly**: exit code **1**, a clear `Error: <chip>: not found in
  database` message, and — critically — **before the board is ever energized** (no
  hardware-revision read, no `AutoCapture`, no rendered report). Today the handler builds
  the report and reads hardware even for an unknown chip, producing a hollow report.
- **Bare fail, no "did you mean…"** — no fuzzy-match suggestion. Simple and predictable,
  matching how every other command already rejects unknown chips
  ([cli_handlers.py:385](../../firestarter_app/firestarter/cli_handlers.py#L385)).
- Case B is **unchanged** — the sweep runs and records the guard's refusal as a finding.

## Why the distinction is load-bearing

`chip_test.derive_plan()` deliberately reads the DB via `db.get_eprom()` **not**
`chip_resolver.resolve_chip()` ([chip_test.py:321-323](../../firestarter_app/firestarter/chip_test.py#L321-L323)),
precisely so case B still yields a plan. The absent-chip guard must therefore key off
`get_eprom()` returning empty — **not** off a `resolve_chip` refusal, which would swallow
case B and defeat the command. See SWEEP-01 / SAFE-02 in REQUIREMENTS.md.

## Implementation shape

In `dev_test` ([cli_handlers.py:1824](../../firestarter_app/firestarter/cli_handlers.py#L1827)),
before building `AutoCapture`/reading hardware:

```python
if not app.db.get_eprom(chip):
    raise ChipNotFoundError(f"{chip}: not found in database")
```

`ChipNotFoundError` flows through `@map_typed_errors` → `click.ClickException` → `Error: …`
+ exit 1 ([cli_handlers.py:139](../../firestarter_app/firestarter/cli_handlers.py#L139)).
Regression test asserts exit 1 **and** that no serial/hardware call was made.
