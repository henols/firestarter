---
title: Bus-config mask-model — host-resolved pin policy, firmware gets precomputed masks
date: 2026-07-02
context: /gsd-explore session on making pinmaps more general and speeding up mem_util_remap_address_bus
---

# Bus-config mask-model

Design decisions from exploring a smarter, faster bus-config for the address-bus
remap. Anchor code: `mem_util_remap_address_bus` in
`firestarter/src/proms/memory.cpp:331`; struct `bus_config_t` in
`firestarter/include/firestarter.h:75`; host composer
`EpromDatabase.get_bus_config` in `firestarter_app/firestarter/database.py:257`.

## The motivation (all four, per operator)

1. Reads/writes feel slow — suspicion the per-byte remap loop is part of it.
2. Some chip layouts can't be expressed with today's config.
3. Layouts that want pins pinned always-HIGH or always-LOW.
4. The remap + host composition feels ad-hoc; want a cleaner general model.

The "can't express a layout" and "always high/low" cases are currently
**forward-looking / hypothetical** — no single chip is blocking today. So this
is a generalization + perf redesign, not a bug fix.

## Key insight — generality and speed are NOT opposed here

Everything the operator wants to express — always-LOW, always-HIGH, VPP routing,
multiple control pins, a pin whose level differs read-vs-write — is **invariant
for the duration of one operation**. Only the address permutation actually
changes per byte.

So resolve all per-pin policy into a small set of precomputed masks **once**, and
the per-byte hot path collapses to:

```
reorg_address = permute(address) | static_mask[direction]
```

This is simultaneously **more general** (arbitrary pin policy) and **faster**
than today's per-byte branching on `rw_line != 0xFF`, `vpp_line != 0xFF`, and
`using_p1_as_vpp(handle)`.

## Decision — the cleverness lives on the HOST

`database.py` / `pinouts.json` resolve the rich per-pin policy into precomputed
masks; the firmware receives the masks and stays dumb + fast. Fits the codebase
grain: the host already composes function→socket-pin (pinouts.json) with
socket-pin→bus-line (`pin_conversions`) in `get_bus_config()`. Keeps AVR flash/RAM
cost minimal.

Three consequences worth remembering:

1. **"Always-LOW" needs zero firmware support.** The remap builds up from `0`, so
   a low pin is simply one the host *never sets* in any mask. Already expressible
   at the bit level — the host just needs a way to *declare* it in pinouts.json so
   it's intentional, not incidental. (No `static_low_mask` field strictly
   required in firmware.)
2. **`rw_line` / `vpp_line` / `using_p1_as_vpp` leave the hot path entirely.** The
   host bakes read-vs-write pin levels into two precomputed masks
   (`read_static_mask`, `write_static_mask`); firmware just indexes
   `static_mask[direction]`. Fewer branches → smaller and faster AVR code.
   (Note: the CONTROL-register VPP enables in `mem_util_calculate_top_address_register`
   — VPP_A9 / VPE / P1 / regulator — are a separate axis from the address-bus
   `vpp_line`; don't conflate the two when redesigning.)
3. **Multiple control pins fall out for free** — they're just more bits in the
   precomputed masks; no new struct fields per control pin.

The one thing the host **cannot** precompute is the address permutation itself
(it depends on the running address), so `address_lines[]` stays as the per-byte
permutation input.

## Scope decision — clean redesign (not additive)

Operator chose a **clean redesign of the bus-config wire schema** over an
additive backward-compatible path. End state is more coherent; cost is a breaking
change landing across firmware + host + golden traces in one milestone, plus a
full chip-DB regen. Treat as milestone-scale (see seed
`bus-config-clean-redesign.md`).

## Open premise to validate first

The "faster" motivation is a suspicion, not a measurement. At 250000 baud
(~25 KB/s) a 512-byte read is ~20 ms of transport; the per-byte remap may be a
negligible fraction of that (serial-bound). Validate before letting perf drive
the design — the generality goal may have to carry the redesign on its own. See
research question in `.planning/research/questions.md`.

## Related

- Seed: `bus-config-clean-redesign.md`
- Seed: `binary-command-protocol.md` (also a breaking wire change; sequence/merge consideration)
- Prior protocol milestones: v1.10 (COBS), v1.12 (dispatch), v1.16 (rebuild), v1.19 (naming), v1.20 (protocol-only dispatch)
