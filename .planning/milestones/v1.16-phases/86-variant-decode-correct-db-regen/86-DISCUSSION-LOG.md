# Phase 86: infoic.xml Variant-Field Decode + Correct DB Regen - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-25
**Phase:** 86-variant-decode-correct-db-regen
**Areas discussed:** (started on the *original* Phase 86 "Naming + Documentation Pass"; pivoted mid-discussion to insert this new phase) — Invariant test strategy, Vocabulary doc location, 'Why' rationale placement, Naming convention, NAME-04 diff mechanics → **variant-field scope** → roadmap restructure → variant override-collapse + re-validation gate

---

## (Original Phase 86 areas — now belong to the displaced Phase 87)

These were discussed before the pivot and are captured in this phase's CONTEXT
`<deferred>` for Phase 87:

| Area | Decision |
|------|----------|
| Invariant test strategy | Matrix-first (invariant→existing native test) + gap-fill; enumerate all **9** invariants (roadmap "8" is stale) |
| Vocabulary doc location | `firestarter/doc/PROTOCOLS.md` — single canonical, GitHub-visible |
| 'Why' rationale placement | Inline per-handler header-comment citing its datasheet + full prose in PROTOCOLS.md |
| Naming convention | Two-name: keep `datasheets/` folder slugs + add descriptive algorithm-axis name column; NO folder rename |

---

## NAME-04 diff mechanics → the pivot

I asked how to record NAME-04's `diff_db` expectation given FM1608 is already 0x28 in
the DB (so only X88C64 0x34 would diff). The operator did not engage with the narrow
verifier-mechanics question and instead surfaced the substantive issue:

> *"when I read the infoic.xml FM1608 has a protocol id that is 0x07 but have a different
> variant value. I think this is important to sort out and investigate what the variant
> field means… then if it makes sense to use the protocol id or create our own type value
> is up to you to decide. It's the info.xml that is the ground truth and we shall try to
> understand and extract as much information from it as possible, to support our code."*

Investigation (grounded in raw `infoic.xml`) confirmed the operator: FM1608 = `type=4,
proto=0x07, variant=0x4126`; X88C64 = `type=1, proto=0x34, variant=0x3100,
flags=0x00414200` (`flags&0x10==0`, which is why the erasable-flag rule misses it). The
`variant` high byte is structured and entirely undecoded in `build_db.py`.

## Variant scope (how far Phase 86 goes with the variant field)

| Option | Description | Selected |
|--------|-------------|----------|
| Document + investigate now, defer code change | Correct narrative + survey + document; keep DB-frozen | |
| **Act on variant in build_db.py this phase** | Decode variant, regenerate correct DB, collapse overrides | ✓ |
| Just fix the two corrections, skip the variant dig | Lightest; discards the investigation | |

**User's choice:** Act on the variant now — *"we need to act on the variant now so we
can generate a correct db. Preferably shall we put in a phase to do that work before we
continue. If needed download more datasheets to solve the hi value of the variant. This
is super important and I think we can save a lot of code if it's done and we don't need
to have some edge cases."*
**Notes:** The "edge cases" = `build_db.py` Rule 1/2/3 override stack. This is a
deliberate scope amendment to v1.16, consciously lifting the DB-frozen lock.

## Roadmap restructure

| Option | Description | Selected |
|--------|-------------|----------|
| **New Phase 86 = Variant Decode; shift the rest** | Insert variant decode as Phase 86; naming→87, golden traces→88, recompose→89, bench→90 | ✓ |
| Merge decode + naming into one Phase 86 | One bigger phase | |
| Let me reconsider scope first | Hold the edit | |

**User's choice:** New Phase 86 = Variant Decode; renumber 86→90.

## Variant override-collapse aggressiveness (VAR-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Collapse to decode, rules become asserted-equivalent guard (Claude-recommended) | Decode primary; rules' safety intent kept as assertions | |
| **Full replacement, delete the rules** | Variant decode is sole classifier; Rule 1/2/3 deleted | ✓ |
| Add variant decode alongside, keep rules | Safest, doesn't deliver "save code" goal | |

**User's choice:** Full replacement — delete Rule 1/2/3.
**Notes:** Made safe by the re-validation gate below — `check_dispatch.py` 0-violations
is the structural backstop for the deleted WARNING-5 override.

## Re-validation gate for the regenerated DB (VAR-03 / VAR-04)

| Option | Description | Selected |
|--------|-------------|----------|
| **check_dispatch 0 + every diff explained + bench chips unchanged** | Software gates + on-hand bench chips' wire values protected (re-bench if moved) | ✓ |
| Software gates only (no bench requirement) | Defer all silicon re-validation to Phase 90 | |

**User's choice:** check_dispatch 0 violations + every `diff_db` row explained (re-pin
baseline) + the 11 bench-proven on-hand chips' wire values unchanged-or-rebenched.

---

## Claude's Discretion

- Whether the decode is a lookup table vs. bitfield parse, the high-byte field naming,
  and the exact `build_db.py` restructure (operator: *"up to you to decide"* re proto_id
  vs. own type value).
- How datasheet provenance for high-byte resolution is recorded.

## Deferred Ideas

- Naming/documentation vocabulary → Phase 87 (decisions already captured, see CONTEXT
  `<deferred>`).
- 0x34 X88C64 programming handler → still PCB-blocked (FUT-01); this phase only corrects decode.
- Open write-path defects (CR-01 / FUT-06 / FUT-03) → preserved as-is.
