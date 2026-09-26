---
id: delete-jp5-dead-renderer
title: Delete the JP5/Rev 2.2 dead jumper renderer — JP5 is the A19_CUT solder jumper, not a config header
captured: 2026-07-10
status: pending
type: cleanup
priority: low
source: /gsd-explore 2026-07-10 (jumper-display-ground-truth.md)
resolves_phase: 182
---

# Delete `_get_rev2_2_jumper_settings_data` (JP5 dead code)

`firestarter_app/firestarter/ic_layout.py` L186-201 + commented-out call at
L659.

## Problem

The renderer presents "JP5" as a Rev 2.2 open/closed config header. In every
Rev 2.x schematic (`.planning/v1.7/upstream-rurp/hardware/`), JP5 is
`A19_CUT` — a factory-bridged **solder** jumper, not something an operator
sets per chip. The call is commented out today, so no wrong output is shown —
but the code is one uncomment away from rendering false guidance for Rev 2.2
boards (which the operator owns).

## Fix

Delete `_get_rev2_2_jumper_settings_data` and the commented call at L659.
Pure dead-code removal; no behavior change, no test updates expected beyond
any that reference the method by name.

## Context

Part of the jumper-display correctness exploration — see
`notes/jumper-display-ground-truth.md` and seed
`jumper-settings-per-pin-map.md`. This piece is independent and can land any
time.
