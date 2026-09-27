---
created: 2026-08-19T00:00:00Z
title: "Phase 44 read-timing knobs (read_settling_us, read_strobe_us) are missing from json_parse's optional-key reset block"
area: firmware
adjacent_phase: 157  # RENAMED from resolves_phase 2026-08-23 at the Phase 157 close. The field name
# was wrong for what it meant and would have auto-closed this todo into .planning/todos/completed/
# on `phase.complete`, burying a live defect. Phase 157 did NOT adopt it: json_parser.c:474-477 now
# states in-source that the two read-timing knobs are "deliberately NOT in this reset block" and
# that their absence "is not an oversight". Keep this as adjacency only.
# ADJACENCY link, set 2026-08-22 at v1.33 activation: Phase 157 rewrites this exact
# file (json_parser.c) — replacing key_parsers[] and the eleven get_* stubs with a {key, offset, width,
# clamp} data table, and deleting get_read_settling / get_read_strobe outright. No v1.33 requirement
# currently covers the optional-key RESET block this todo is about (DECODE-06 covers the
# READ_TIMING_MAX_US clamp surviving, which is a different concern). Linked anyway because fixing it
# during 157 is nearly free whereas fixing it afterwards means touching the file twice — exactly the
# double-remap cost D-01 exists to avoid, and json_parser.c loses 198 of 198 of its .planning/
# citations to 157. /gsd-discuss-phase 157 decides whether to adopt it; this link is not a commitment.
files:
  - firestarter/src/json_parser.c
  - firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp
---

## Problem

Research Open Question 5 (149-RESEARCH.md). `firestarter_handle_t handle` is a single
file-scope global (`firestarter/src/firestarter.cpp:33`) with **no per-command `memset`** --
`json_parse` resets only its *optional* keys at the top of each parse, because the mandatory
keys are always overwritten by the current command. Phase 149 / D-05 added exactly this reset
for the new `page_size` field, on the reasoning that without it, a 128 parsed for one chip would
persist into the next command's chip if that command omitted `page-size` -- turning "absent means
64" false in practice.

**Measured (`firestarter/src/json_parser.c:83-100`):** the two Phase 44 read-timing knobs,
`read_settling_us` and `read_strobe_us`, are **not** in that reset block. This is the exact same
category of latent defect one field over -- it predates Phase 149 and Phase 149 does not
introduce it, but Phase 149's own D-05 fix makes its absence for these two fields conspicuous by
contrast (the reset block's own comment now says so explicitly, filed as this todo).

## Why this is not simply a page overrun

Both knobs treat `0` as "use the firmware default" (`read_settling_us == 0` -> no settling
delay; `read_strobe_us == 0` -> use the default 3µs), per
`firestarter/src/json_parser.c:358-359`. So the symptom of the missing reset is a **stale
non-zero knob value persisting into a later command** that did not specify one -- e.g. a read
issued with `read-settling-delay: 500` followed by a plain read for a different chip would
silently keep applying a 500µs settling delay -- rather than any buffer or address overrun. Lower
severity than the page-size case, but the same shape of bug.

## Deliberately not fixed in this phase

Adding the reset here would perturb
`firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp`'s
`test_read_timing_fields_default_zero_when_absent` test, which characterizes the current
(pre-fix) behaviour. A defect in this neighbouring field is its own change, with its own test
update, not a page-size phase's business.

## What would close it

Add `handle->read_settling_us = 0;` and `handle->read_strobe_us = 0;` to `json_parse`'s
optional-key reset block (`firestarter/src/json_parser.c:83-100`, immediately alongside the
existing `chip_id`/`page_size` resets), and update
`test_read_timing_fields_default_zero_when_absent` (and any sibling test asserting persistence
across commands) to match the corrected behaviour.

## Filed by

Phase 149 (dual-repo lockstep), research Open Question 5, Plan 07.
