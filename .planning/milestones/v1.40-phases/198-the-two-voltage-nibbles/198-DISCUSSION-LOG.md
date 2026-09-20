# Phase 198: The two voltage nibbles - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-18
**Phase:** 198-the-two-voltage-nibbles
**Areas discussed:** The 24 unmapped vdd indices · VOLT-02 the VPP value and its blast radius · VOLT-03 disposing the 28 rows · VOLT-01 how strong a claim the write-down makes

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| The 24 unmapped vdd indices | 0x6/0xD/0xE silently default to 5000 mV; upstream's xg table resolves them | ✓ |
| VOLT-02: the VPP value and its blast radius | 12500 vs 12200; which rows; the firmware guard window | ✓ |
| VOLT-03: disposing the 28 rows | Sub-group 1 now separable from sub-group 2 | ✓ |
| VOLT-01: how strong a claim the write-down makes | Narrow per-family finding vs the general one | ✓ |

**User's choice:** all four.

---

## The 24 unmapped vdd indices

### Q1 — What should the generator do with a vdd index it has no table entry for?

| Option | Description | Selected |
|--------|-------------|----------|
| Complete the table from xg | Add the xg indices; zero conflicts on all 6 shared entries proves one encoding, so this is decoder completion under D-2 | ✓ |
| Complete AND fail closed on the remainder | Same, plus replace the silent `.get(idx, 5000)` default with a raise | |
| Fail closed only, do not extend | Keep the TL866-II table as sole decoder and raise; blocks the build on 24 existing rows | |
| Leave the default, record the gap | No code change; write the finding down and let Phases 199/200 act | |

**User's choice:** Complete the table from xg.
**Notes:** The fail-closed leg was explicitly not taken, so the silent default survives — recorded as D-03 so that nothing mechanical is assumed to report a future gap.

### Q2 — Does VPP_MV get completed too?

| Option | Description | Selected |
|--------|-------------|----------|
| Complete VPP_MV and fix the mask | Add 0xF1=25000, 0xF2=21000 and key on the full low byte with option bits stripped | ✓ |
| Complete VPP_MV, leave the mask | Entries present but unreachable — documented-but-dead | |
| VCC only, record the VPP gap | Hand the 0xF0/0xF1/0xF2 collapse to Phase 199 | |

**User's choice:** Complete VPP_MV and fix the mask.
**Notes:** Zero rows carry 0xF1/0xF2 today, so byte-identical regeneration is the proof. Motivated by the collapse silently under-reporting a 25 V part as 18 V.

### Q3 — What happens when the completed decode yields an implausible value?

| Option | Description | Selected |
|--------|-------------|----------|
| Ship the honest decode, flag it | The 12 EXEL/ST rows become vdd 1800 | |
| Hold the 12 back pending VOLT-03 | Named carve-out for the 0x06 group | |
| Ship the decode and add a plausibility floor | A rule that refuses to emit an implausibly low vdd | ✓ (superseded) |

**User's choice:** the plausibility floor — **subsequently superseded by Q4**.
**Notes:** Claude flagged at the time that a floor cuts against milestone D-1/D-2, being a correction wearing a decoder's clothes. Rather than argue the point, the next step measured what a value-keyed floor would actually select. It selects exactly the 28 rows, which made the floor and VOLT-03's disposition the same decision — and VOLT-03 was then resolved as "leave unchanged", so no floor ships.

### Q4 — The `vdd < vcc` predicate selects exactly the 28 rows. What does the floor emit?

| Option | Description | Selected |
|--------|-------------|----------|
| Fail the build, force an override per row | 28 rows, 28 datasheets, before the generator runs | |
| Emit the decode but mark the row unsupported/unproven | Lets support_status carry the doubt | |
| Clamp vdd up to vcc, record every clamp | Never lowers a rail, but leaves `info` reporting 5.5 V | |
| Leave all 28 unchanged, close the todo with the reason | What VOLT-03 explicitly permits | ✓ |

**User's choice:** Leave all 28 unchanged, close the todo with the reason.

### Q5 — Unchanged against today's output, or uncorrected?

| Option | Description | Selected |
|--------|-------------|----------|
| Uncorrected — let the completed decode flow | 24 vdd changes (12→1800, 5→6000, 7→6250) | |
| Byte-identical — carve the 0x06 group out | 12 vdd changes (5→6000, 7→6250) | ✓ |
| Do not complete the vdd table at all this phase | Only VPP_MV completed | |

**User's choice:** Byte-identical — carve the 0x06 group out.

### Q6 — How is the carve-out expressed?

| Option | Description | Selected |
|--------|-------------|----------|
| Complete the table fully, override the 12 rows explicitly | Decoder stays complete; exception is visible and testable | ✓ |
| Complete only the corroborated indices, state the omission | Smallest change, but the 12 reach 5000 through the same silent default being closed | |
| Complete fully and make index 0x06 fail closed | Stops the build on 12 existing rows | |

**User's choice:** Complete the table fully, override the 12 rows explicitly.
**Notes:** Asked specifically because a quiet table omission would recreate the silent-default fault this phase is otherwise fixing.

---

## VOLT-02: the VPP value and its blast radius

### Q1 — What value goes in the override?

| Option | Description | Selected |
|--------|-------------|----------|
| 12500 — the datasheet nominal | 12.5 V ± 0.3 V; matches the sibling MBM27C1000P's index 0x60 | ✓ |
| 12200 — the floor exactly | Satisfies VOLT-02's literal wording but sits at the bottom of the band with no margin | |
| 12500, and record 12.2–12.8 as the accepted band | Value plus the full window in the note | |

**User's choice:** 12500 — the datasheet nominal.

### Q2 — Which rows?

| Option | Description | Selected |
|--------|-------------|----------|
| The two datasheet-backed rows only | MBM27C1001 and MBM27C4001; both PDFs git-tracked | ✓ |
| All three non-P rows, MBM27C2001 as UNSOURCED | Family made consistent, but one part's reading applied to another | |
| Source the MBM27C2001 datasheet first, then decide | Makes the diff depend on finding a 1989 PDF | |

**User's choice:** The two datasheet-backed rows only.

### Q3 — Does Phase 198 correct vdd_mv, or is that Phase 200's?

| Option | Description | Selected |
|--------|-------------|----------|
| Correct it here for the datasheet-backed rows | MBM27C4001, MBM27C1001, MBM27128 → vdd 6000 | ✓ |
| VPP only — leave vdd to Phase 200 | Smallest diff here | |
| Correct the three, and inventory the other 167 | Plus a measured inventory of every index-0x4 row | |

**User's choice:** Correct it here for the datasheet-backed rows.
**Notes:** Raised because all three vendored Fujitsu datasheets state 6.0 V ± 0.25 V against a decoded 5500, and two of the three existing override notes already quote the figure. The 167-row inventory was declined; it is recorded as a deferred idea instead.

### Q4 — How far does the phase pin the firmware guard-band consequence?

| Option | Description | Selected |
|--------|-------------|----------|
| Record it, and state it in the gh#66 answer | Tells the reporter 12.5 V is now settable | |
| Record it and add a host-side test pinning the arithmetic | Duplicates a firmware constant on the host side | |
| Record it in the phase record only | Public answer stays strictly to database values | ✓ |

**User's choice:** Record it in the phase record only.

---

## VOLT-03: disposing the 28 rows

Largely settled by the first area. Two questions remained, plus one Claude decided rather than asked.

### Q1 — How does the blocking todo get disposed?

| Option | Description | Selected |
|--------|-------------|----------|
| Close to completed/, file a successor backlog entry | The todo's question is answered; the residue gets its own tracker | ✓ |
| Close to completed/ only | Residue visible only in the override file | |
| Rewrite the todo in place with the new evidence | Would leave success criterion 3 unmet | |

**User's choice:** Close to completed/, file a successor backlog entry.

### Q2 — How far does the write-down dispose sub-group 1's premise?

| Option | Description | Selected |
|--------|-------------|----------|
| Test it per row and record the disposition | All 16 classified by part class, on the 197-AT28C-guard-evidence precedent | ✓ |
| Name the premise as unverified and stop | Cheaper; leaves the unproven claim standing in a new document | |
| Classify only where a datasheet is already on disk | Would dispose zero of the 16 — the repo vendors no Microchip or AMD 28C datasheet | |

**User's choice:** Test it per row and record the disposition.

### Decided by Claude, not asked

Whether the archived `148-DB-DIFF.md` § Non-claim is corrected in place. **No** — archived
`.planning` records are historical-by-intent and rewriting one destroys the evidence of what was
believed. The falsification is recorded in Phase 198's own artifacts and in `DECODE-NOTES.md`,
pointing at the archived text. Stated to the user before the questions in this area, not silently.

---

## VOLT-01: how strong a claim the write-down makes

### Q1 — How broad a claim does DECODE-NOTES.md § 9 make?

| Option | Description | Selected |
|--------|-------------|----------|
| The general finding, with its limits named | Rail indices, model-dependent, nearest-rail substitution — plus what it does not prove | ✓ |
| Per-family only, no general claim | VOLT-01's literal wording; leaves the proven mechanism unwritten | |
| General finding, and add the falsified-premise ledger | Plus a one-place list of everything this phase superseded | |

**User's choice:** The general finding, with its limits named.

### Q2 — What does the gh#66 draft claim?

| Option | Description | Selected |
|--------|-------------|----------|
| Corrections only, explicitly not a fix | Values plus a "this does not close this report" heading, crediting dim20 | ✓ |
| Corrections, plus the general nibble finding | More useful to a technical reporter; larger claim surface | |
| Corrections, and restate the causation question as open | Re-raises a thread already moved past | |

**User's choice:** Corrections only, explicitly not a fix.

### Q3 — How does the gh#66 draft relate to gh#70's held draft?

| Option | Description | Selected |
|--------|-------------|----------|
| One consolidated held-pending list | Added to the record 197-GH70-ANSWER.md established | ✓ |
| Separate draft, cross-referenced | Two held drafts in two directories | |
| Draft at milestone close, not now | Moves the writing away from the phase holding the evidence | |

**User's choice:** One consolidated held-pending list.

---

## Not re-asked — carried forward from Phase 197

The override file's key and contract, the input-substitution semantics, the fail-closed legs, "decode
tables stay in code", the DECODE-NOTES.md home for decode findings, the inventory-record precedent,
the never-hand-edit rule on the generated database, the no-comments rule, and the operator's
absolute publishing prohibition until the v1.40 beta cut (197-08). All sourced in CONTEXT.md
§ "Carried forward from Phase 197".

---

## Claude's Discretion

- Non-vacuity coverage for the 12 held override entries.
- Whether a `wire_dict_expected_deltas_198.json` layer is needed — to be measured, not assumed.
- Where the sub-group-1 per-row disposition file lands, and its name.
- The exact wording of the 12 UNSOURCED notes.
- Whether the `vdd < vcc` predicate ships as a build-time assertion or only as a measurement.

---

## Deferred Ideas

- The 167 index-`0x4` rows this phase does not reach.
- `FUJITSU/MBM27C2001` left at vpp 12000 with no vendored datasheet.
- The 4 `adapter-required` rows inside the 28, which Phase 199 may flip to `supported`.
- `chip_info` gating `can_adjust_vcc`/`can_adjust_vpp` upstream, ignored by the generator.
- Making the `.get(idx, default)` fallbacks fail closed.
- A build-time assertion on the `vdd < vcc` predicate.
- `VOLT-F1` — the remaining families touching `VCC_VOLTAGES[0x04]`.
