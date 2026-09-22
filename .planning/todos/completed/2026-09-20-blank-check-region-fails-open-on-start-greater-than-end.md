---
created: 2026-09-20
source: 201-REVIEW.md WR-02
resolves_phase: 205
severity: warning
---

# `mem_util_blank_check_region` fails open on `start > end`

`firestarter_fw/src/proms/memory.cpp` — `mem_util_blank_check_region(handle, start, end)` treats a
malformed `start > end` as "blank, nothing to scan": no local guard, no log, no assertion. It
returns success without scanning anything.

This is unreachable today. Both arguments are derived from the same `handle->address` /
`mem_util_operation_end(handle)` pair that `_process_incoming_data` guards independently in
`eprom_operations.cpp`, so a malformed pair cannot reach an out-of-range write.

The objection is structural rather than behavioural: a blank check's safety property is enforced in
a **different function in a different file** from the one that needs it. Any future caller of the
region form that does not inherit that guard gets a silent pass instead of a refusal — and a blank
check that silently passes is the exact shape of defect Phase 201 exists to fix.

Suggested fix: a local fail-closed clamp or refusal inside `mem_util_blank_check_region` itself, so
the guarantee is structural rather than remembered — the same reasoning the phase applied to
`mem_util_operation_end` and to the single-exit HV wrapper.
