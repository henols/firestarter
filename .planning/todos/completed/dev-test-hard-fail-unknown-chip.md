---
id: dev-test-hard-fail-unknown-chip
title: dev test must hard-fail (exit 1) on a chip absent from the DB, before energizing hardware
captured: 2026-07-03
status: completed
resolves_phase: "114.1"
resolved: 2026-07-10
type: enhancement
priority: medium
source: /gsd-explore 2026-07-03 (dev-test-unknown-chip-fail-fast.md)
resolution: Delivered by Phase 114.1 (SAFE-04) — guard at cli_handlers.py dev_test (fw_app d6359de), tests TestAbsentChipHardFail (6ab06a7); all 4 acceptance boxes verified in 114.1-VERIFICATION.md (3/3 must-haves, RED→GREEN independently reproduced)
---

# `dev test` — hard-fail on unknown chip before touching hardware

`firestarter_app/firestarter/cli_handlers.py` (`dev_test`, ~L1827)

## Problem

Today `dev test <unknown-chip>` does **not** fail directly. `derive_plan()` returns an
empty plan with `reason="<chip>: not found in database"`
([chip_test.py:336](../../../firestarter_app/firestarter/chip_test.py#L336)), and the
handler then keeps going: it **energizes the board** to read the hardware revision
([cli_handlers.py:1836](../../../firestarter_app/firestarter/cli_handlers.py#L1839)), runs
the empty plan, and renders a full-but-hollow diagnostic report — for a chip that doesn't
exist.

## Change

Guard **case A only** (name absent from DB — NOT in-DB-but-unsupported; see the design
note for why the distinction is load-bearing). In `dev_test`, immediately after the
`--destructive` confirm and **before** building `AutoCapture` / any hardware call:

```python
if not app.db.get_eprom(chip):
    raise ChipNotFoundError(f"{chip}: not found in database")
```

- Exit **1** (via existing `@map_typed_errors` → `click.ClickException`).
- **Bare fail** — no "did you mean…" fuzzy-match suggestion.
- Must short-circuit before `read_hardware_revision_value()` — no serial connection, no
  report rendered.

## Acceptance

- [ ] `dev test <absent-chip>` exits 1 with `Error: <chip>: not found in database`.
- [ ] No serial / hardware call is made on that path (assert the mock is never touched).
- [ ] No report is rendered to stdout on that path.
- [ ] Regression: an in-DB-but-unsupported chip (case B) STILL runs the sweep and renders
      its report — not broken by the guard.

## Notes

Small, self-contained hardening of the Phase-112 `dev test` handler. Could fold into the
v1.21 feature-close (Phase 114) or land as a standalone quick fix. See design note
[`dev-test-unknown-chip-fail-fast.md`](../../notes/dev-test-unknown-chip-fail-fast.md) and
requirement SAFE-04.
