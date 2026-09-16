---
created: 2026-09-16T13:05:00Z
title: Reject a negative write start address instead of silently clamping it to 0
area: both
resolves_phase: null
files:
  - firestarter_app/firestarter/address_parser.py (parse_address accepts negatives)
  - firestarter_app/firestarter/page_size_gate.py (require_page_alignment modulo check)
  - firestarter_fw/src/json_parser.c (simple_strtoul drops the sign)
---

## Problem

Filed as accepted debt at the Phase 195 UAT checkpoint (2026-09-16), disposition (a).
Recorded in code review as **WR-01**.

`firestarter write W29C020 <file> -a -256` passes the host page-alignment guard and
exits 0. Two independent behaviours combine:

1. `parse_address` does not reject a negative string — it hands `-256` straight through.
2. Python's `%` returns a non-negative result for a negative dividend, so
   `-256 % 256 == 0` reads as **aligned** in `require_page_alignment`.

The firmware does not catch it either. `simple_strtoul` consumes only `[0-9]`; a leading
`-` is not a digit, so the loop body never runs and the function returns 0. Confirmed by
compiling the function verbatim and running it: `-256` -> 0, `-1` -> 0.

## Why this was not fixed in Phase 195

The consequence is narrower than the review could establish. A write requested at a
negative address silently lands at **address 0**, which is page-aligned, for a length
already proven to be a whole number of pages. It therefore erases nothing outside the
range it writes and violates neither WRITE-01 nor WRITE-02.

It is a **wrong-destination** defect — a silent clamp to 0 where a refusal belongs — not
a partial-page-destruction defect. All four of Phase 195's success criteria concern
alignment and length, not address sign, so it was out of scope.

The user still loses data: the write lands at 0 and overwrites whatever is there, with
no diagnostic and a zero exit code.

## Solution

TBD. Candidate shape:

1. Reject a negative start address in `require_page_alignment` **before** the modulo
   check, with a refusal message naming the address — the modulo check cannot be made to
   catch it, because it reports the sign-folded value as aligned.
2. Decide whether `parse_address` itself should refuse negatives. It is shared with the
   read and blank-check paths, so a change there is wider than the write guard and needs
   its own callers audited first.
3. Consider a firmware-side refusal so the host guard is not the only line of defence —
   `simple_strtoul` currently makes a negative address indistinguishable from `0` on the
   wire, which is what hides the defect today.

Any fix needs a regression test pinning `-256` (and `-1`) as a refusal, not a pass.
