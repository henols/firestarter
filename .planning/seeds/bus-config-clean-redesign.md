---
title: Clean bus-config redesign around host-precomputed masks
trigger_condition: a chip layout the current bus-config can't express is hit, OR read/write throughput becomes a binding priority
planted_date: 2026-07-02
status: dormant
---

# Clean bus-config redesign around host-precomputed masks

Redesign the address-bus config so the host resolves all per-pin policy into a
small set of precomputed masks, and the firmware's per-byte remap collapses to
`permute(address) | static_mask[direction]`. Simultaneously more general (any
pin policy: always-high, always-low, multiple control pins, read-vs-write
levels) and faster (no per-byte branching).

Full rationale + decisions: `.planning/notes/bus-config-mask-model.md`.

## Why (payoff)

- **Expressiveness:** first-class always-LOW, multiple control pins, and
  per-direction (read-vs-write) pin levels — none expressible cleanly today.
- **Speed (unverified):** removes `rw_line`/`vpp_line`/`using_p1_as_vpp` branches
  from the per-byte hot path in `mem_util_remap_address_bus`. May be marginal if
  reads/writes are serial-bound — validate first (see research question).
- **De-ad-hoc:** one coherent mask model instead of special-cased rw/vpp/static-high fields.

## Shape (rough)

- **Host (`database.py` + `pinouts.json`):** pinouts.json gains a way to declare
  per-pin policy (address-bit / always-high / always-low / control-per-direction).
  `get_bus_config()` resolves policy + `pin_conversions` into
  `read_static_mask`, `write_static_mask`, and the `address_lines[]` permutation.
- **Firmware:** `bus_config_t` carries the two precomputed static masks + the
  permutation. Hot path = `permute(address) | static_mask[dir]`. Drop the
  per-byte rw/vpp/using_p1 logic. (Always-low = a bit the host never sets → no
  `static_low_mask` field strictly needed.)
- **Keep separate:** CONTROL-register VPP enables (VPP_A9 / VPE / P1 / regulator
  in `mem_util_calculate_top_address_register`) are a distinct axis from the
  address-bus vpp_line — don't fold them into the address masks.

## Scope / compat decision

**Clean redesign** of the bus-config wire schema (operator's choice over
additive). Breaking wire change → firmware + host land in lockstep
(CLAUDE.md protocol-parity rule). Full chip-DB regen; golden traces + native
dispatch tests rewritten.

## Cost / risk

- Breaking wire change on the heels of v1.20's `type`-axis removal and the
  pending binary-command-protocol seed — sequence these deliberately.
- Full DB regen touches every chip's bus-config → GATE-02 (no-new-regression
  vs beta) needs a fresh baseline; golden traces will legitimately change.
- Perf payoff unproven — de-risk with the research question before committing.

## Next steps when triggered

1. **Validate the perf premise** (research question in `questions.md`): profile
   what fraction of a read/write is the remap vs 250kbaud serial transport.
2. If perf is marginal, decide whether generality alone justifies a breaking
   redesign, or whether an additive `static_low` + configure-time mask precompute
   is enough.
3. Decide sequencing vs `binary-command-protocol.md` — both are breaking wire
   changes; consider bundling into one protocol-layer milestone.
4. Scope as a milestone with lockstep host+fw + golden-trace rewrite.

## Related

- Note: `bus-config-mask-model.md`
- Seed: `binary-command-protocol.md`
- Code: `mem_util_remap_address_bus` (`firestarter/src/proms/memory.cpp:331`),
  `bus_config_t` (`firestarter/include/firestarter.h:75`),
  `EpromDatabase.get_bus_config` (`firestarter_app/firestarter/database.py:257`)
