---
created: 2026-09-16T00:00:00Z
title: "Decide the output contract for a protocol 0x05 write override, before any override flag ships"
area: host
resolves_phase: unassigned
files:
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/eprom_operations.py
---

## Problem

The originating issue (gh#68, `henols/firestarter_prom` issue #68) requested the alignment
refusal be offered behind an explicit override flag, so an operator who understands the risk could
proceed anyway. Phase 195 declined to ship one (D-03).

## The trap that made this phase decline it

An override that proceeds past the alignment refusal and then prints the plain success line
(`Write to X successful`) violates WRITE-02 **literally** -- that requirement is unconditional: no
protocol `0x05` write reports `successful` when bytes outside the requested address range were
erased. An override flag alone does not change what actually happened to the chip; it only changes
whether the operator asked for it. Shipping the flag without first deciding what the override path
*reports* would be the single easiest way to fail this phase's own requirement while believing the
requirement had been honoured, because the failure is in the output line, not in the write itself.

## What would close it

Not the flag -- **a decided output contract for the override path**, specifically:

- What the outcome line says (it must not be the plain "successful" line WRITE-02 forbids for this
  case; it needs wording that is honest about partial/unaligned collateral damage having occurred)
- What the exit code is (whether an overridden write that completes its protocol steps should still
  exit 0, given that the operation itself did not fail -- only the safety property did)
- What the operator must acknowledge before the override takes effect (a confirmation prompt, a
  required second flag, or some other friction proportional to the risk)

Once that contract is decided and recorded, the override flag itself is a small, mechanical
addition behind it.

## Filed by

Phase 195 (partial writes stop destroying the page), D-03, Plan 04.

## Closed by
