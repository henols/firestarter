# Phase 199 Plan 03 — Firmware notes: the ceiling constant, and three corrected doc sites

This is a planning artifact, not source. It carries the two things that cannot legally live in
`rurp_pinout.h` or `eprom.cpp` as a comment: the constant's full measurement provenance (too much
prose for a `#define` line) and — since the no-comments-in-source rule that used to force this
split has since been removed, see below — a record of what changed and why, kept here rather than
duplicated into the corrected doc blocks themselves.

## 1. The constant's provenance

`RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV` = **17380**, defined in
`firestarter_fw/include/rurp_pinout.h` immediately after `EPROM_HV_ALL_OFF_MASK`.

It is **one operator meter reading**, taken at **socket pin 1** against board ground, on **one
Rev 2.0 shield identified by silkscreen** (operator statement, not measured — `hw_revision`
cannot distinguish Rev 2.0 from Rev 2.2 from the modified Rev 0), with the **socket empty** and the
**pot at maximum**, in **one bench session** (2026-09-19, recorded in full in
`199-BENCH-RECORD.md`).

The reading was taken **after a firmware fix to `dt_set_registers`** (the re-entrancy defect
`199-BENCH-RECORD.md` § "Fault 2" documents) unblocked the session, and **NOT** by the bench plan's
originally prescribed `hold_rail.py` method — that script reports success against a command the
attached board's firmware refused, and separately never held a rail on this rig at all (see
`199-BENCH-RECORD.md` §§ "Fault 1" and "Fault 2" for the full mechanism). The actual invocation was
`firestarter -v -p /dev/ttyACM0 dev reg 0 0 0x188 -f`, held by the firmware's own
`while (!rurp_user_button_pressed()) delay(200);` loop, with no `firestarter` command running while
the rail was held.

**This is a measurement, not a specification.** No Rev 1 or Rev 2.2 board was measured — the pair
(17380 mV drop-resistor, 22140 mV direct-VPE) is for this one Rev 2.0 board at this one pot
setting, not a fleet figure and not a tolerance band. Per the D-21 operator ruling (2026-09-19),
**Rev 0 is explicitly not a concern**: it converts to Rev 1 with a voltage divider, so it is out of
scope for this constant by the same ruling that moved the routing decision into firmware.

## 2. A ceiling, not a threshold

VPE-as-VPP does not deliver a fixed voltage; it delivers the undropped pot voltage the operator
sets, whatever that happens to be. The constant is therefore not "17380 mV is what a routed part
receives" — it is "no pot setting lets the drop-resistor path exceed 17380 mV, so any part
requiring more must take the direct-VPE route instead." Reading it as a threshold for one pot
position rather than a ceiling on the path itself would license comparing it against the wrong
thing (a live monitor reading) instead of the right one (the part's required `vpp_mv`), which is
exactly the confusion D-22 exists to rule out.

## 3. The three stale documentation sites — corrected, not deferred

The no-comments-in-source rule that would have forced these three sites to stay stale until
`199-05` was removed mid-phase, on 2026-09-19, by operator decision (meta commit `41a34c6a`,
`firestarter_fw abfc2ec`, `firestarter_app 029208c`). All three are corrected in this plan's own
commits instead of being left for `199-05` to fix.

**Site 1 — `src/proms/eprom.cpp`, `eprom_hv_route_mask`'s resolution-order doc block, step 1.**

- Was: *"is a pure human override (25V NMOS parts, the manual-pot workflow) set by no database
  entry, so it wins over the table with no table read."*
- Is now: *"is a human override (25V NMOS parts, the manual-pot workflow) set by no database
  entry, so it wins over the table with no table read. It is no longer the only route to the
  undropped rail: step 4 below also raises it when handle->vpp_mv exceeds the drop path's
  ceiling."*
- Why it was stale (D-12): `FLAG_VPE_AS_VPP` used to be the *only* route to the undropped rail
  besides the `vpp_path` table itself. This plan's Task 1 added a second: the ceiling comparison.

**Site 2 — the same doc block, step 3.**

- Was: *"anything else, including unrecognised values, -> EPROM_HV_ROUTE_MASK, also failing closed
  toward the drop path."*
- Is now: *"anything else, including unrecognised values, falls through to step 4 rather than
  returning EPROM_HV_ROUTE_MASK outright."* A new step 4 was added, documenting the ceiling
  comparison itself: *"handle->vpp_mv > RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV ->
  CTRL_VPP_REGULATOR_ENABLE; otherwise EPROM_HV_ROUTE_MASK, failing closed toward the drop path."*
- Why it was stale: the "anything else" arm used to return `EPROM_HV_ROUTE_MASK` immediately; it
  now only does so after the new ceiling check also fails to raise the rail. The `anything else ->
  EPROM_HV_ROUTE_MASK` claim stopped being exhaustive the moment Task 1 landed.

**Site 3 — `include/eprom.h`, the declaration block above `eprom_hv_route_mask`.**

- Was: *"Which high-voltage route to assert (direct-VPE vs drop-resistor), from the eprom_params
  vpp_path column. FLAG_VPE_AS_VPP forces the direct-VPE path regardless of what the table says.
  Returns a fail-closed mask when the protocol has no row."*
- Is now: *"Which high-voltage route to assert (direct-VPE vs drop-resistor), from the
  eprom_params vpp_path column, though not from that column alone: a required voltage above
  RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV (rurp_pinout.h) also selects the direct-VPE path.
  FLAG_VPE_AS_VPP forces the direct-VPE path regardless of what the table says. Returns a
  fail-closed mask when the protocol has no row."*
- Why it was stale: the route no longer comes from the `vpp_path` column alone, since Task 1 added
  a second selector keyed on `handle->vpp_mv`.

Each edit was kept to the sentence that was wrong; no surrounding prose was restructured, and no
phase number, plan id, or `D-NN` decision id was written into either file — those rot and mean
nothing to a reader without `.planning/`.

**A fourth site, found by measurement while making this plan's commits, and also corrected in the
same commit:** `tests/golden/protocol_branch_inventory.json` (the TABLE-05 golden inventory over
`eprom.cpp`'s branch predicates) pinned a blob SHA and a positional site list that Task 1's new
comparison and this doc correction's line-count growth both moved. It was re-derived from the live
file — one new site added at the ceiling comparison's line, every site from the old `eprom_hv_route_mask`
onward shifted by the same offset, nothing hand-edited — and the update is recorded in that file's
own `recorded_by` history field, following the convention every prior re-derivation there already
uses.

## 4. What `199-05` still owes its DECODE-NOTES section

- The posture change for all three sites above: they are now **corrected**, not **left stale
  pending `199-05`** — the plan text `199-05` was originally written against assumed the latter.
- The constant's provenance and its one-shield / one-session / one-pot-setting limit, exactly as
  recorded in § 1 above and in `199-BENCH-RECORD.md` in full.
- The routing decision now lives in **firmware** (`eprom_hv_route_mask`,
  `RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV`), not in a host-side policy module. Any host-side
  `firestarter_app/` prose `199-05` was drafted against a host module (`firestarter/vpp_rail_gate.py`)
  that does not exist and must not be recreated — `199-05-PLAN.md` needs replanning before it runs,
  per this plan's own output note.
