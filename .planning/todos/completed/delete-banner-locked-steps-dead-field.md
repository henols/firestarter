---
id: delete-banner-locked-steps-dead-field
title: Delete banner.locked_steps and Plan.locked_destructive — provably unreachable since Phase 121, and the code says so
captured: 2026-08-23
status: resolved
type: cleanup
priority: low
source: /gsd-explore 2026-08-23 (devtest-report-known-but-unstated-fields.md)
resolves_phase: 181
resolved: 2026-09-09 (plan 181-04's RPT-B2 deletion)
---

# Delete `banner.locked_steps` / `Plan.locked_destructive`

`firestarter_app/firestarter/chip_test.py:567` (`Plan.locked_destructive`),
`:3905`/`:3931` (`BannerCounts.locked_steps`), and
`firestarter_app/firestarter/diagnostic_report.py:860-864` (the JSON key).

## Problem

`locked_destructive` records the `(op, reason)` of write/erase steps a
`destructive=False` call would have omitted. It is populated **only** on a
`write_scope="none"` plan.

`_resolve_write_scope` (`cli_handlers.py:2453-2456`) returns **only** `"full"`
or `"partial"`:

```python
del interactive  # no branch keys on it any more -- see the docstring
if not _is_uv_eprom(app, chip):
    return "full"
return "partial"
```

`"none"` is unreachable from every CLI path. So `locked_destructive` is always
`[]`, `BannerCounts.locked_steps` is always `[]`, and every filed report carries
`"locked_steps": []`.

The `Plan` docstring already states this — "As of Phase 121 (this plan's D-02
correction) this list becomes permanently empty in production after plan
`121-09` lands -- no CLI path will reach `write_scope='none'` any longer" — and
then declines to act on it: "Removal is an explicitly deferred cleanup, not this
phase's work."

## Fix

Delete the field from `Plan`, from `BannerCounts`, and from
`_banner_dict()`'s output. Keep the N-of-M banner itself — it renders
unconditionally and still carries signal when the chip-ID destructive gate closes
or `resolve_chip` refuses a step (RESEARCH C-6). Only the always-empty list goes.

## Constraints

- **Not in `dedup_fingerprint`.** That hash is `chip | protocol |
  op=verdict:classification` plus the policy/coverage tags — `locked_steps` was
  never an input, so no filed report re-keys and no `count_agreeing` group
  resets.
- **Forward-only deletion.** The frozen schema-1.2 fixtures in
  `.claude/skills/devtest-triage/fixtures/` carry `"locked_steps": []` and their
  headers forbid regeneration. Old bodies must keep parsing.
- Schema-version bump belongs to whichever change lands first; both `[dev test]`
  parsers accept `schema_version` by presence only, so the bump is invisible to
  them.

## Why it is split out

Independent of the rest of Backlog **999.36** — it touches no timing semantics
and populates nothing. It can land alone, or ride 999.36's deletion task if that
phase is planned first. Do not do it twice.

## RESOLUTION (2026-09-09)

Fixed by plan `181-04` (RPT-B2, D-08 adjudicated at the fullest depth). `banner.locked_steps`,
`Plan.locked_destructive` and `write_scope="none"` are all deleted, along with
`_resolve_write_scope`, per the operator's own choice to go deeper than this todo's narrower
request. The N-of-M banner itself is kept, unconditionally rendering as this todo's "Fix" section
asked. Not in `dedup_fingerprint`'s pre-image, so no re-key; the frozen schema-1.2 fixtures in
`.claude/skills/devtest-triage/fixtures/` were left forward-only-parseable, unchanged.
