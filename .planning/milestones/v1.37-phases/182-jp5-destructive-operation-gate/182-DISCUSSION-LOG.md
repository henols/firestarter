# Phase 182: JP5 Destructive-Operation Gate - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Phase:** 182-jp5-destructive-operation-gate
**Date:** 2026-09-10 (session 1); 2026-09-10 (session 2 — JP4 correction)
**Areas discussed:** *Session 1* — Affected-part predicate, Operation coverage, Escape hatch &
non-interactive, Jumper-display cleanup scope. *Session 2* — SAFE-03 trace scope, SHIELD-REVS
repair.

---

## Pre-discussion finding that reframed the phase

Before the first question, a measurement against the live database showed SAFE-01's literal
wording could not be implemented:

- No pin map in `pinouts.json` declares A19 at all (15 maps checked).
- All eight 1 MB (8 Mbit) rows — `AM27C080`, `AM27LV080`, `AT27C080`, `MX27C8000`, `MX27C8000A`,
  `UPD27C8001`, `M27C801` ×2 — sit on `DIP32_STD`, which declares 19 address lines (A0–A18) and
  `vpp-pin: [1]`.
- `ic_layout.py` consequently renders **JP4 = Closed** for those parts — actively instructing the
  operator to route VPP to socket pin 1.

This was presented to the operator before any option was offered.

---

## Affected-part predicate

| Option | Description | Selected |
|--------|-------------|----------|
| Shortfall + 32-pin | Address-line shortfall AND `vpp-pin == [1]` AND `pin_count == 32`. Exactly 8 rows; self-corrects if the map is later fixed. Was the recommendation. | |
| Shortfall, unscoped | Same without the pin-count scope. 11 rows — 3 of them (`AT27C011`, `D27011`, `D27C011`) would get a "cut JP5" message that is wrong for them. | |
| Size threshold + VPP-pin-1 | `size_bytes >= 0x100000` AND `vpp-pin == [1]`. Exactly 8 rows, but `0x100000` is a magic constant standing in for "needs A19". | |
| All VPP-on-pin-1 parts | 291 chips. Cannot under-warn, but fires across the whole 27C010/020/040 population where closing JP4 is correct. | |

**User's choice:** *"Other"* — none of the above. Free-text: *"If the pin maps are wrong that must
be created and solved from the infoic.xml. The database must be generated from the infoic.xml
without any special cases or workarounds, we have to consider that new types of EPROMs get
inserted in the infoic and they must apply to the rules without to have to update the db
generator."*

**Notes:** The operator supplied three photographs of their shields (Rev 0 modified, Rev 2,
Rev 2.2) alongside the answer. Follow-up measurement confirmed the operator's position is
implementable: infoic's `variant` field already discriminates the three 32-pin families
(`0x01` = 256 KB, `0x02` = 512 KB, `0x03` = 1 MB) at `pin_map=0x000c` / `protocol_id=0x08`, and
`resolve_pinout_key` already uses `variant_lo` for 24- and 28-pin parts — it abandons the field
only at `pin_count == 32`, substituting a hand-tuned `MAX_27C020_SIZE` threshold.

One correction was put back to the operator rather than accepted: infoic's `<maps>` section
(121 records, lines 16717–17202) carries only a GND pin and a masked-pin list — connectivity with
no signal function — so pin-map **definitions** cannot be generated from it. The chip→layout
**assignment** can be, and that is where the special case lives.

---

## Generator fix scope

| Option | Description | Selected |
|--------|-------------|----------|
| Full fix in 182 | Dispatch 32-pin on `variant_lo`, retire `MAX_27C020_SIZE` and its parity arm, author the new layout, regenerate. Was the recommendation. | ✓ |
| Fix + audit all widths | As above, plus sweep every arm for thresholds standing in for rules — including 3 rows on a 14-line `DIP28_2764` and 18 `DIP32_28C512_EEPROM` rows with 16 lines for up to 512 KB. | |
| Gate only in 182; fix in its own phase | Ship the warning against the current database; correct the generator separately. | |

**User's choice:** Full fix in 182.
**Notes:** The declined audit was captured as a deferred idea, together with a suggested
fail-closed generator assertion (every row's `size_bytes` must fit the address lines its layout
declares) that would have caught the 8 Mbit defect at build time.

---

## Operation coverage

### Round 1 — does the gate survive the map fix?

| Option | Description | Selected |
|--------|-------------|----------|
| Both — gate still required | Silkscreen says "Cut for ROMs with A19 on P1" unconditionally; JP5 is unreadable, so the gate covers what the map fix cannot. Was the recommendation. | |
| Map fix supersedes the gate | Treat the hazard as closed once the tool stops asking for VPP on pin 1; strike SAFE-02 and SAFE-04. | ✓ (round 1) |

**User's choice (round 1):** Map fix supersedes the gate.

**Notes:** This voided two of the phase's five requirements on a circuit fact not yet established,
so the concern was raised once, specifically: the silkscreen instruction is unconditional; A19 is
not broken out anywhere on the Rev 2 pin labels, so the JP5 path may be *how* A19 reaches pin 1
rather than merely a VPP disconnect; and either way an 8 Mbit read with JP5 bridged returns wrong
data silently.

### Round 2 — drop now, or gate on the evidence?

| Option | Description | Selected |
|--------|-------------|----------|
| Evidence-gated | Map fix and SAFE-03 trace first; the trace decides whether SAFE-02/04 retire (with the trace as the recorded reason) or a warning ships. Was the recommendation. | ✓ |
| Drop the gate now | Strike SAFE-02/04 at discuss time; the trace is recorded but gates nothing. | |
| Drop the refusal, keep a notice | No prompt or refusal, but an unconditional informational line. | |

**User's choice (round 2):** Evidence-gated. The operator's expected outcome — that the map fix
supersedes the gate — is retained as the expectation, with the trace required underneath it.

### Round 3 — if a warning does ship, what does it cover?

| Option | Description | Selected |
|--------|-------------|----------|
| Every operation | read, write, verify, blank, erase, id, dev test — because no operation on an 8 Mbit part is correct if pin 1 cannot carry A19. Was the recommendation. | |
| Writes and erases only | Gate only VPP-asserting or modifying operations. | |
| Whatever the trace proves energizes pin 1 | Let the evidence define the set exactly. | |

**User's choice:** *"Other"* — *"Only when its a dangerus operation that can damage an EPROM."*

**Notes:** Narrower than the recommendation and coherent with the round-2 split: the gate is about
**damage**, the map fix is about **correctness**. Silently-wrong reads are explicitly not gated;
they were recorded as a deferred item instead.

---

## Escape hatch & non-interactive

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated flag, `--force` excluded | Interactive prompt; non-interactive refuses unless a purpose-built flag (e.g. `--jp5-cut`) is given. Was the recommendation. | |
| Hard refuse, no escape at all | No flag, no override; `dev test` skips with a stated reason. | |
| `--force` satisfies it | Reuse the existing `-f/--force`. | |

**User's choice:** *"Other"* — *"force excluded and when it is dangerus a question to continue."*

**Notes:** `-f/--force` is excluded as an escape hatch, and no substitute flag was authorised.
Since SAFE-04 permits only "refuse" or "an explicit, separate acknowledgement flag — never a
default-yes", the remaining branch is refusal, so non-interactive invocations (no TTY, piped
stdin, `dev test`, `--auto`/`--chain`) refuse. This reading was stated back to the operator
before being recorded. Rejecting `--force` reuse was reinforced by gh#62, where a reporter reached
for `--force` to get past a refusal.

---

## Jumper-display cleanup scope

| Option | Description | Selected |
|--------|-------------|----------|
| Own phase, wiki + info output | Photographs and per-revision tables to the prom wiki; `info` prints only the rows that matter and says when a jumper is irrelevant. New capability, so its own phase. | ✓ |
| Fold the info-output half into 182 | Phase 182 also rewrites the `info` jumper block; photographs still separate. | |
| All of it in 182 | Gate, generator fix, info rewrite, photographs and wiki tables together. | |

**User's choice:** Own phase, wiki + info output.
**Notes:** Decided without asking (precedent settled it): SAFE-05 is a named requirement of
Phase 182, so deleting `_get_rev2_2_jumper_settings_data` stays here. The
`fix-jp4-labels-and-rev2-revision-block` todo therefore splits — its dead-renderer item is SAFE-05
here; its JP4-label and Rev-2-block items move to the new phase, whose number does not exist yet.

---

## Claude's Discretion

- Name of the new 32-pin layout key (`DIP32_27C801` suggested, following the existing
  exemplar-part convention).
- Whether the SAFE-03 trace is a standalone `.planning/notes/` file or lives in the phase
  `SUMMARY.md` — it must be citable by Phase 187's gh#60 reply either way.
- Disposal of the retired `MAX_27C020_SIZE` parity arm — deleted, or replaced with a test that
  asserts something real about the 32-pin dispatch.
- Preservation of the operator's photographs: downscaled to 900×1600 / ~250 KB each (from 44 MB
  of originals) and placed under the phase `evidence/` directory, with silkscreen legibility
  verified after downscaling.

## Deferred Ideas

- The wider pin-map audit the operator declined for 182 — `AT27C011`/`D27011`/`D27C011` on a
  14-address-line `DIP28_2764`, and 18 `DIP32_28C512_EEPROM` rows with 16 lines for up to 512 KB —
  plus a suggested fail-closed generator assertion that every row's size fits its layout's address
  lines.
- Silently-wrong 8 Mbit reads if the SAFE-03 trace concludes "no damage".
- The new shield-documentation phase (wiki photographs, per-revision jumper tables, `info`
  rewrite) — needs inserting into `ROADMAP.md` before Phase 187, which must stay last.
- Two `REQUIREMENTS.md` edits arising from this discussion: SAFE-01's wording, and marking
  SAFE-02/SAFE-04 conditional on the SAFE-03 trace.

---

# Session 2 — 2026-09-10 — the JP4 correction

Re-entered `/gsd-discuss-phase 182` with an operator correction supplied inline:

> *"the rev 2.2 silk screen is wrong (mayby corrected on 2.3) the jp4 is 3 pins instead of a 2 pin
> that 2.0 and 2.1 have. The second jummper setting can route the vpp to pin 21 (24 pin) and this
> will enable to be able to program some old legacy EPROMs like 2516, but earlier revisions don
> have this feature"*

CONTEXT.md already existed; the **Update it** branch was taken without prompting, since the
invocation was itself an explicit update.

## Pre-discussion verification

The correction contradicted `.planning/v1.7-SHIELD-REVS.md`, which places the JP4 footprint change
at Rev 2.3 and records Rev 2.1 → Rev 2.2 as *"no change (JP4 1x2 vertical header preserved per
shared schematic blob)"*. Four independent checks were run before any option was offered:

| Check | Result |
|---|---|
| Rev 2.2's own `W27C512Programmer-top-pos.csv` | `"JP4","P1_VPP_JMP","PinHeader_2x02_P2.54mm_Vertical"` |
| Rev 2.1's own `W27C512Programmer-top-pos.csv` | `"JP4","P1_VPP_JMP","PinHeader_1x02_P2.54mm_Vertical"` |
| `RelativelyUniversalROMProgrammer.kicad_sch:22555` | `Description "Jumper, 3-pole, both open"`, pins 1/2/3 |
| upstream commit `7c8f262` | *"2716 / TMS2532 support"* — the capability the third pole serves |
| Operator photo `evidence/shield-rev2.2-jp4-jp5-jp6-jp9.jpg` | silkscreen reads *"Open … Closed …"* — two-state text on a three-pole part |

**The operator was correct on both counts.** The record's error has the same cause as the
already-resolved R41 4k7-vs-10k error: Rev 2.2 has no committed schematic (Phase 31 Finding E), so
both times it was inferred from Rev 2.1's shared blob while Rev 2.2's own artefacts sat in the
same directory.

Rev 2.3's silkscreen could **not** be checked — the only Rev 2.3 image upstream ships is a fab
render with no instructional text. Recorded as open.

## Area selection

Three areas were offered: *SAFE-03 trace scope*, *The mirrored hazard*, *SHIELD-REVS repair*.
The operator selected the first and third. The second was dispositioned by Claude and recorded
(see D-15.2) rather than dropped.

---

## SAFE-03 trace scope

### Q1 — What does the trace cover?

| Option | Description | Selected |
|--------|-------------|----------|
| VPP-destination table | Revision family × JP4 state → which socket pin carries VPP. ~9 cells; answers gh#60; resolves the standing "DIP24 JP3/JP4 guidance unconfirmed" defect as a by-product. Recommended. | ✓ |
| Pin 1 only, JP4 states as a caveat | Trace which operations assert `P1_VPP_ENABLE`; name JP4's states without tabulating destinations. Leaves "can the shield reach VPP for an 8 Mbit part" unanswered. | |
| Full per-pin-map reachability matrix | Destination table plus a reachability verdict for all 15 pin maps. Pulls the deferred D-07 audit back in. | |

**User's choice:** VPP-destination table.

### Q2 — What evidence settles it for Rev 2.2?

| Option | Description | Selected |
|--------|-------------|----------|
| Desk trace + operator continuity probe | Rev 2.3 schematic for the 3-pole net, Rev 2.2 gerbers/CSV for the footprint, then a DMM confirmation on the operator's Rev 2.2 board. The only method that has not yet produced a wrong Rev 2.2 answer. Recommended. | ✓ |
| Desk trace only | No operator time; accepts the same inference-from-adjacent-revision method that produced both known Rev 2.2 errors. | |
| Desk trace, probe only if ambiguous | Middle cost — but both prior errors were cases where the desk trace looked unambiguous and was wrong. | |

**User's choice:** Desk trace + continuity probe.

### Q3 — Where does the table live?

| Option | Description | Selected |
|--------|-------------|----------|
| Extend `jumper-display-ground-truth.md` | Add the table and fix that file's wrong JP4 row in place. One home for jumper ground truth — where the D-09 phase already looks and Phase 187 can cite. Recommended. | ✓ |
| New standalone `.planning/notes/` trace note | Cleaner separation between display defects and electrical routing; a second file to keep in sync. | |
| Inline in Phase 182 `SUMMARY.md` | Cheapest, but archived at milestone close while Phase 187 and D-09 still need to cite it. | |

**User's choice:** Extend `jumper-display-ground-truth.md`.
**Note:** that file's JP4 row currently reads *"VPP to socket pin 1 only"* and *"Footprint changes
to 3-pole 2x2 selector at Rev 2.3"* — both halves wrong for Rev 2.2, so it needed correcting
regardless of where the table landed.

### Q4 — What does the DIP24 unreachable-VPP finding oblige?

| Option | Description | Selected |
|--------|-------------|----------|
| Record + file a backlog item | Table states it; a backlog item captures "tool offers writes it cannot physically perform on some revisions". No host behaviour change in 182. Recommended. | ✓ |
| Record in the table only | Lightest; risks the finding sitting in a note nobody re-reads once gh#60 is answered. | |
| In scope — fold into the gate | Widens the phase and makes D-05's "does a gate ship at all" harder to answer from the trace. | |

**User's choice:** Record + backlog item.

---

## SHIELD-REVS repair

Two further consequences were surfaced before the questions:

- **§6 capability rows** list Rev 2.1, 2.2 and 2.3 as all supporting "24-pin legacy DIP UV-EPROM"
  and call Rev 2.3's capability set *"unchanged from Rev 2.1/2.2"* — but if the third pole is what
  makes 24-pin VPP reachable, there is a capability delta at 2.1 → 2.2 the record denies.
- **§"JP4 Caveat"** bases the `hw_revision` detect model on R41's lower terminal connecting to a
  JP4 pin, while openly saying *"consult upstream schematic … for the exact wiring"* — i.e. never
  traced. In the current schematic R41 sits at x≈281 and JP4 at x≈178, different regions.

### Q1 — How far does the repair go?

| Option | Description | Selected |
|--------|-------------|----------|
| Every JP4 claim the trace settles | ~10 spots (§1 r19, §3 r44/r45, §4 r58, §5 r73/r74, §6 r89/r91, §7 r132, §Detect r175, §JP4 Caveat), using the destination table as evidence. Recommended. | ✓ |
| Footprint-attribution rows only | Fix where the change is dated; knowingly leave the capability rows and the JP4 Caveat stating things the trace just disproved. | |
| Errata note only, defer edits to D-09 | Tightest phase; leaves ten wrong cells in place for however long D-09 takes. | |

**User's choice:** Every JP4 claim the trace settles.

### Q2 — How is §6's 24-pin capability row corrected?

| Option | Description | Selected |
|--------|-------------|----------|
| Revision-qualify the 24-pin row only | Read-only on Rev 0/2.0/2.1, programmable on Rev 2.2+; correct the "unchanged" note; leave other families' rows alone. Recommended. | ✓ |
| Split every row into read vs program | Most honest table, but it is the full reachability matrix under another name. | |
| Footnote pointing at the destination table | Cheapest; the cells stay wrong at a glance. | |

**User's choice:** Revision-qualify the 24-pin row only.

### Q3 — Does Phase 182 resolve the untraced R41↔JP4 coupling?

| Option | Description | Selected |
|--------|-------------|----------|
| Resolve in the trace, characterize only | Desk-trace the coupling; read `hw_revision` at each JP4 position while the board is open — operator moves the jumper, Claude drives the board over USB. Recorded, not fixed; no firmware change. Recommended. | ✓ |
| Flag as untraced, file a todo | Keeps the phase off anything firmware-adjacent; leaves the detect model resting on an assumption beside a proven-wrong claim. | |
| Out of scope entirely | Cleanest boundary; the repair would edit rows around the caveat while leaving its premise unexamined. | |

**User's choice:** Resolve in the trace, characterize only.

### Q4 — How is the correction marked?

| Option | Description | Selected |
|--------|-------------|----------|
| Inline convention + systemic-cause note | Correct each cell in the file's existing bold/dated/evidence-cited style, plus one note naming the failure mode (Rev 2.2 twice inferred from Rev 2.1's blob). Recommended. | ✓ |
| Inline convention only | Records what was wrong but not why it recurs. | |
| Errata block at the top | Auditable as a set; departs from the file's convention and splits each fact from its row. | |

**User's choice:** Inline convention + systemic-cause note.

---

## Claude's Discretion (session 2)

- The exact shape of the VPP-destination table — column order, how a JP4 state is named, whether
  Rev 0 gets its own row or a "JP4/JP5 not present" sentinel.
- **Disposition of the unselected area.** The mirrored hazard (JP4 in the 24-pin position with a
  28/32-pin part seated) is **named in the destination table but not gated**, and gets a backlog
  item. Rationale: the tool can read JP4 no better than JP5, so gating it needs the same D-05
  evidence decision the phase has not yet made. Recorded at the operator's instruction rather than
  dropped. Session 1's discretion item on where the trace lives is **superseded** by D-12.

## Deferred Ideas (session 2)

- 2516 / 2716 / 2532 programming support as a capability — new capability, own phase.
- Backlog: the tool offers writes it cannot physically perform (`DIP24_2716` / `DIP24_2532`
  declare `vpp-pin: [21]`, unreachable on Rev 0/2.0/2.1).
- Backlog: the mirrored hazard, per the discretion note above.
- Open question: was the Rev 2.3 silkscreen corrected? Needs an upstream question to Anders or a
  photograph from someone holding a Rev 2.3 board. Matters to D-09, not to Phase 182.
- The D-09 phase inherits a larger job: three JP4 states per revision, and it must not reproduce
  the Rev 2.2 silkscreen's Open/Closed sentence.
