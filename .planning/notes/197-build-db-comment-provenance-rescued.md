# Decode provenance rescued from `build_db.py` comments deleted in 197-02

**Date:** 2026-09-18
**Commit that deleted them:** `firestarter_app` `11351e0` (`feat(197-02): datasheet override mechanism, MBM27C1000 pulse 100->500us`)
**Lines:** 18 comment lines removed, 0 added.

## Why this note exists

Plan 197-02 collapsed the nested VPP-ceiling `if` in `tools/build_db.py`. Dedenting the
surrounding block made pre-existing, unchanged comments reappear as `+` lines in the staged
diff, tripping the mandatory no-new-comments pre-commit check. The executor deleted them whole
rather than re-adding them at the new indentation.

**That deletion is correct under CLAUDE.md's hard rule** — no comments in product source, ever,
and a sweep is the standing direction of travel (v1.33 was a Source Hygiene milestone doing
exactly this). But the same rule says rationale goes "in the commit message or in `.planning/`,
never in source", and this deletion put it in **neither**: commit `11351e0`'s message describes
the override mechanism and does not mention the removed decode records.

Three of the deleted lines carried information that existed nowhere else — two decode bug-fix
records and one external-source verification anchor — on a milestone whose whole subject is
decode correctness. This note is that relocation, made after the fact.

The executor's hand-back reported "three pre-existing explanatory comments". The measured figure
is 18 lines across eight blocks, several of them bug provenance rather than explanation. Treat
comment-deletion counts in a SUMMARY as a claim to verify, not to accept.

## The deleted text, verbatim

VPP ceiling — reason-string contract with the host:

    # Reason string begins with
    # "VPP <x>V exceeds programmer max (<ceil>V)" so the host
    # can render it verbatim.
    # Uses "programmer max" (not "RURP ceiling") per SC#2 wording.

    # Demote to NON_DISPATCHABLE_ALGO so dispatch()
    # returns ERROR instead of configure_eprom (HARD invariant).

    # else: leave _support_status as "supported" — M2732A (21V)
    # is within the RURP ceiling.

VPP nibble decode, and the BUG-B fix:

    # VPP code occupies bits 7-4 of the 16-bit voltages field
    # (the HIGH nibble of the low byte). Bits 3-0 carry option
    # flags. Masking with 0xF0 extracts only the VPP nibble.
    # BUG-B fix: was voltages & 0xFF (caused 0mV for chips with
    # flags bits set, e.g. SST27VF512 voltages=0x0001).

NMOS correction site:

    # NMOS correction (Site C): override vpp/vpp_mv when
    # _nmos_vpp_mv is set (M2716/M2732/M2732A corrected voltage).

VCC/VDD nibble decode, the BUG-3 fix, and the upstream anchor:

    # BUG-3 fix: vcc at bits 11-8, vdd at bits 15-12.
    # v1.12 had them swapped (vdd at bits 11-8, vcc at bits 15-12).
    # [VERIFIED: minipro database.c#L921-L923 @ a8efaedc]

Two trailing markers on code lines, deleted with them:

    ),  # bits 11-8
    ),  # bits 15-12

## What is load-bearing here

- **`voltages & 0xF0`, not `& 0xFF`.** The VPP index is the high nibble of the low byte; bits
  3-0 are option flags. `SST27VF512` (`voltages=0x0001`) is the named witness — masking with
  `0xFF` yielded 0 mV for any row carrying flag bits.
- **VCC is bits 11-8, VDD is bits 15-12.** v1.12 had them swapped. The swap direction is the
  whole content of the record, so a future edit that "corrects" it back reintroduces BUG-3.
- **`minipro database.c#L921-L923 @ a8efaedc`** is the upstream verification anchor, and that
  commit is the same `a8efaedc` that `MINIPRO_XML_URL` is pinned to. It is the only pointer in
  the repo from this decode to the source it was checked against.
- **The reason string is a host-facing contract**, not prose: it begins
  `VPP <x>V exceeds programmer max (<ceil>V)` and the host renders it verbatim. The wording
  "programmer max" rather than "RURP ceiling" was deliberate.
- **The ceiling demotion sets `NON_DISPATCHABLE_ALGO`** so `dispatch()` returns `ERROR` rather
  than falling through to `configure_eprom`. The comment called this a HARD invariant.
- **M2732A at 21 V stays `supported`** — it is within the ceiling. This is the `>` not `>=`
  boundary that plan 197-02 was required to preserve, and six rows sit exactly on 25000 mV.

Related: `.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-02-SUMMARY.md`,
and the v1.33 source-hygiene milestone that set the no-comments direction.
