---
created: 2026-09-20
source: 201-REVIEW.md WR-01
resolves_phase:
severity: warning
---

# `region-end` has no test coverage through the real `json_parse()` path

Phase 201 added the `region-end` wire key: a PROGMEM key string plus a `FIELD()` table row in
`firestarter_fw/src/json_parser.c`, and a per-command reset to 0.

Every test that exercises the region behaviour sets `handle->region_end` **directly on the C
struct**, bypassing the PROGMEM-string / offset / width machinery entirely. So a typo in the key
string, a wrong offset or width in the table row, or a broken per-command reset would not redden
any automated test.

The mechanism *was* proven once on real hardware — the bench session's confirming run could only
have produced its observed progress denominator if `json_parse()` wrote `handle->region_end`
correctly. But a bench record is evidence, not a regression test, and it does not re-run.

**Precedent to follow:** `firestarter_fw/test/native/avr/test_read_timing/test_read_timing_params.cpp`
does exactly this for `read-settling-delay` and `read-strobe-us`, in the same pinned native env.
`201-REVIEW.md` carries ready-to-drop-in cases.

Two things to cover: a round-trip through `json_parse()` asserting the parsed value lands in
`handle->region_end`, and the per-command reset to 0.
