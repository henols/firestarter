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

Related: `.planning/milestones/v1.40-phases/197-the-override-mechanism-and-the-program-pulse/197-02-SUMMARY.md`,
and the v1.33 source-hygiene milestone that set the no-comments direction.

---

# Second rescue: the NMOS block deleted in 197-03

**Date:** 2026-09-18
**Commit:** `firestarter_app` `047a5bd` (`feat(197-03): move NMOS_TRUE_VPP_MV into six one-row override entries`)
**Lines:** 16 comment lines removed, 0 added.

197-03 deleted `NMOS_TRUE_VPP_MV` and its surrounding comment paragraph, replacing it with six
`UNSOURCED` entries in `tools/datasheet_overrides.json`. The regeneration is **byte-identical**
to 197-02's database, so the move is value-preserving.

The six `note` fields carry the vendor/datasheet provenance well — each states the value is
inherited verbatim from the hardcode, that the Intel reading was applied to an SGS-THOMSON or ST
part with no vendor-specific backing, and what would close it. That part needs no rescue.

**Three operational facts in the deleted block are not in those notes**, and are rescued here.

## 1. The shield cannot reach 25 V — "~22 V max"

    # Upstream caps VPP at 18 V, which some antique Intel NMOS parts exceed:
    # M2716 and M2732 need 25 V, M2732A needs 21 V. They report 18 V here because
    # upstream aliases them under generic 2716/2732 entries. The 25 V parts are
    # unprogrammable on this shield regardless (~22 V max); for the rest the
    # operator must override via ~/.firestarter/database.json.

**This is the load-bearing one, and it bears directly on the rest of v1.40.** The four rows now
overridden to 25000 mV are, by this comment's own account, **unprogrammable on real hardware** —
the shield tops out around 22 V. `RURP_VPP_CEILING_MV` is 25000, so a 25000 mV row passes the
`>` ceiling check and ships `support_status: supported` while being physically unreachable.

That is the same defect gh#71 reports from the other direction: the ROADMAP records VPP measuring
17.8 V and VPE 22.7 V against a 21 V ± 0.5 requirement, and notes the 25 V ceiling is "a regulator
figure, not a socket measurement". This deleted comment is independent corroboration of the ~22 V
socket reality, written before that issue existed. Phases 198–201 (VOLT/RAIL/VCC, and the
bench-gated Phase 199) are where it has to be resolved; D-4 already rules that the operation
proceeds with a warning naming both numbers rather than refusing silently.

Also recorded here: the pre-197 operator escape hatch was `~/.firestarter/database.json`, which is
a *runtime user* override, distinct from the build-time `tools/datasheet_overrides.json` this
phase introduces. The two are not the same mechanism and the deleted comment is the only place
the older one was written down in this file.

## 2. The ordering invariant

    # Must run AFTER all fm1608/WARNING-5 overrides (ordering invariant).

The NMOS correction had to run after the fm1608/WARNING-5 overrides. The new design applies every
override at a single point between `classify()` and the VPP ceiling check, so the invariant is
satisfied by construction rather than by ordering discipline — but nothing now states that it was
ever a constraint. A future refactor that reintroduces a second application site needs to know.

## 3. "Highest VPP wins", and why there is no `INTEL/M2732A` key

    # Matched against part_number aliases; "highest VPP wins" for entries with
    # multiple NMOS aliases (e.g., INTEL/2732,2732A,M2732,M2732A).

    # "Highest VPP wins": iterate all aliases; the match with the highest
    # VPP determines the final voltage + status (conservative — avoids
    # M2732/M2732A match-order ambiguity on combined entries like
    # INTEL/2732,2732A,M2732,M2732A).

The hardcode resolved alias collisions by taking the highest VPP, deliberately conservative, to
avoid match-order ambiguity on comma-joined rows such as `INTEL/2732,2732A,M2732,M2732A`. The
override file replaces that rule with one entry per row and a duplicate-target check, which is why
the shipped file has **no `INTEL/M2732A` key** — it would target the same row as `INTEL/M2732` and
trip the duplicate-target leg. The conflict rule is therefore gone by design, not by oversight.
The `was: 18000` figures were measured by regenerating with the hardcode deleted, not copied from
the comment.
