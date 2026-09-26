# Phase 197: The override mechanism and the program pulse - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-18
**Phase:** 197-the-override-mechanism-and-the-program-pulse
**Areas discussed:** Override key / alias ambiguity, Where overrides apply in the pipeline, What an entry may override, How far the pulse correction reaches

---

## Prerequisite repair (not a gray area)

`init.phase-op 197` returned `phase_found: false`. The v1.40 milestone section wrote its five phases
as bold lines under `### Phase Details`, with unbolded `Goal:` / `Requirements:` labels, where every
GSD roadmap verb scrapes `### Phase N: Name` plus `**Goal**:` and `**Requirements**:`. No phase in
v1.40 could be discussed, planned or executed. Repaired to the format the rest of ROADMAP.md already
uses and committed as `4f99025f` before the discussion began. No requirement, criterion or goal
wording was changed.

---

## Override key / alias ambiguity

**Grounding measurement:** manufacturer+alias is unique across all 746 rows (0 collisions); bare
alias collides on 152 of 953 aliases; 234 rows carry a comma-joined `part_number`. The row gh#70
concerns emits `part_number: "MBM27C1000P,MBM27C1000"`. `NMOS_TRUE_VPP_MV`'s 3 entries reach 6 rows
across INTEL, SGS-THOMSON and ST, three of which ride an Intel datasheet citation.

| Option | Description | Selected |
|--------|-------------|----------|
| Manufacturer + alias | `FUJITSU/MBM27C1000`. Unique across all 746 rows. Dissolves the "highest VPP wins" tie-break. Costs 6 NMOS entries instead of 3, each citing its own datasheet. | ✓ |
| Bare alias, fail closed on multi-row hit | Reads shortest; 152 ambiguous aliases error only if overridden. Keeps 3 entries but preserves the tie-break and the borrowed Intel citation. | |
| Exact `part_number` string | Strictly 1:1, no matching logic. File stops reading like datasheet names; breaks if infoic reorders aliases within a row. | |

**User's choice:** Manufacturer + alias.

### Follow-up: can one entry target more than one row?

| Option | Description | Selected |
|--------|-------------|----------|
| One entry = one row, always | Repetition is the honest cost of OVR-03. Makes a 217-row sweep cost 217 datasheets — a deliberate deterrent. | ✓ |
| An entry may list several targets | Keeps the file small when one datasheet covers several manufacturers' versions of a die. Risk: cheap to attach a datasheet to rows it was never read against — the defect the NMOS entries already have. | |
| One row now, revisit if 198/199 need it | Ship strict, widen later with evidence in hand. | |

**User's choice:** One entry = one row, always.

---

## Where overrides apply in the pipeline

**Grounding measurement:** `support_status` derives from `vpp_mv` against the 25 V ceiling
(`build_db.py:591-600`); `vcc_mv` is rewritten from `vdd_mv` at `:705`; both run before
`chips.append` at `:710`. Reframed from "which line" to "what an override *is*".

| Option | Description | Selected |
|--------|-------------|----------|
| Decoded input — rules still run | Generator's own rules run on the overridden value; `support_status` stays derived, never hand-written. Matches D-1/D-2. Cost: the AT28C verdict cannot move as a plain field override. | ✓ |
| Emitted output — override is final | Post-decode merge like `extra_chips.json`; one clear place, all three hardcodes move uniformly. Cost: an overridden `vpp_mv` of 30000 ships `support_status: supported`. | |
| Input substitution, then re-derive | Merge post-decode, then re-run the derivations. Both properties, at the cost of the derivations existing twice. | |

**User's choice:** Decoded input — rules still run.

**Notes:** The related question — whether OVR-03's recorded prior value is asserted or documentary —
was **decided by Claude rather than asked**, on project precedent (`interpret_timing` raises rather
than masking; the `page_size` validation raises; OVR-04 already requires fail-closed). Asserted; a
mismatch fails the build.

---

## What an entry may override

| Option | Description | Selected |
|--------|-------------|----------|
| Two named sections in one file | `field_overrides` for decoded values, `support` for verdicts; FM1608 as `electrical.type` applied late. | |
| One flat schema, allowlisted fields | Smallest format; loader holds the late-apply semantics. Cost: datasheet facts and support policy look identical in the file. | |
| Only decoded values move; other two stay in code | Most honest to D-1, but contradicts OVR-05 as written. | |

**User's choice:** *Free text* — "I will say that only decoded values can be overridden, and the
things in the code must be solved in some better way and be discussed."

**Notes:** This rejected all three options as posed. The file holds decoded values only, **and** the
non-decoded hardcodes get a real resolution rather than a new home — which turned the rest of this
area into two investigations.

### Follow-up: the AT28C adapter verdict

**Grounding measurement:** 19 rows share `pin_count 24` + `algorithm 13` + `pinout DIP24_2816`. The
14-name hardcode marks 9 of them `adapter-required` and leaves 10 `supported` — `AT28C16` refused
while `X2816A`, `CAT28C16A`, `AM28C16A` and Microchip's plain `2816` are offered. `DIP24_2816` is
fully defined in `pinouts.json` with no `vpp-pin`. `chip_resolver.py:28` guards generically, so no
host source change is implied either way.

| Option | Description | Selected |
|--------|-------------|----------|
| All 19 need the adapter | Verdict derives from `pinout == DIP24_2816`; 10 rows flip to `adapter-required`. | |
| None of them do | 9 refusals were untested names; all 19 become supported. | ✓ |
| Check the hardware first | Defer to a bench-gated phase, leave the list untouched. | |

**User's choice:** *Free text* — "No adapter shall be needed at all, but its only 2.2 and above that
supports it by hardware, but that is not a real blocker, the other versions can do the same with a
wire, but that's nothing to care about here."

**Notes:** The shield-revision distinction (Rev 2.2+ native, earlier with a wire) is explicitly **not
modelled** in the database. The name list is deleted, not moved.

### Follow-up: the FM1608 relabel

Raised by the operator at the readiness gate: *"Im not sure about the FM1608, is the override type
needed? It might be a better way of solving it if the infoic dont have the proof, the app can maybe
calculate whats needs to be known."*

**Grounding measurement, prompted by that challenge:** every host site treats `SRAM` and `FRAM`
identically — `eprom_operations.py:2288`, `eprom_info.py:390`, `database.py:368` and `:576`. The
label changes nothing but a display string. Algorithm 40 holds 34 rows, all SRAM-class, and FM1608 is
the only one relabelled, while Ramtron siblings `FM1208`, `FM16W08`, `FM1808` and `FM18L08` — equally
FRAM parts — read `SRAM`. Separately, `sdp_capability.py:121` holds a second hardcoded FRAM list
(`FM28V020`, `MB85R256H`) covering two **algorithm 13** parts that share nothing with FM1608.

| Option | Description | Selected |
|--------|-------------|----------|
| Delete it, like the AT28C list | FM1608 reads `SRAM`, consistent with its four siblings and the other 29 algorithm-40 rows. Zero functional change; one display snapshot to update. | ✓ |
| Keep FRAM, derive it properly | No infoic FRAM flag exists, and the two parts where FRAM-ness does real work are algorithm 13, so the honest implementation is a larger name list. | |
| Override it as a decoded value | One entry citing the Ramtron datasheet. Cost: a display-only cosmetic as the file's first non-NMOS entry, with four siblings still mislabelled. | |

**User's choice:** Delete it, like the AT28C list.

**Notes:** The operator's instinct was correct and changed the outcome — the earlier plan had FM1608
entering the override file. Two of the three hardcodes OVR-05 assumed were corrections turned out to
be defects.

---

## How far the pulse correction reaches

**Grounding measurement:** 217 of 297 algorithm 7/8 rows carry `pulse_duration_us: 100`. Fujitsu has
12 algorithm 7/8 rows, 9 at 100 µs, and all three community reports (gh#70 MBM27C1000, gh#66
MBM27C4001, gh#71 MBM27128) are inside that block. 12 datasheets sit in `datasheets/`, three of them
Fujitsu. A web search for minipro's `pulse_delay` semantics was inconclusive; the generator's own
`[VERIFIED: minipro database.c#L866]` citation and the observed 10/20/50/100/200/500/1000 µs
distribution are the stronger evidence that the microseconds reading is correct and infoic simply
carries a family default.

| Option | Description | Selected |
|--------|-------------|----------|
| The in-repo Fujitsu rows | Up to 9 rows from three datasheets already on disk; pre-stages gh#66 and gh#71. | ✓ |
| MBM27C1000 only | One entry, exactly PULSE-02. Leaves MBM27C1001 wrong with its datasheet in the repo. | |
| Every row any in-repo datasheet covers | All 12 datasheets across six vendors. Largest diff; pulls in algorithms beyond 7/8. | |

**User's choice:** The in-repo Fujitsu rows.

---

## Folded todo: MAX_27C020_SIZE

| Option | Description | Selected |
|--------|-------------|----------|
| Name it under OVR-06, derive later | One-line deliverable; keeps pinout work out of this phase. | |
| Derive it away in this phase | Replace the constant with `code_memory_size` arithmetic. Cost: it governs the `DIP32_27C020`/`DIP32_STD` fork, so a wrong derivation puts programming voltage on an address line. | ✓ |
| Leave it out of 197 entirely | Defer to a pinout-correctness phase. | |

**User's choice:** Derive it away in this phase.

**Notes:** `mem_size <= 262144` is provably equivalent to `(mem_size - 1).bit_length() <= 18` for
every power-of-two size in the database, so a byte-identical regeneration is the available proof.

---

## Claude's Discretion

- The override file's name, on-disk format and internal ordering.
- Where the loader lives and how it is covered, given that `firestarter_app/tools/` sits outside
  every CI gate.
- The exact wording of generator failure messages, subject to OVR-04's fail-closed requirement.
- Where the 216-row inventory of uncorrected 100 µs rows lands.
- Whether OVR-03's recorded prior value is asserted (decided: yes, fail the build).

## Deferred Ideas

- The wiki page "AT28C04 Adapter" goes stale when the reason string citing it is deleted.
- `FRAM_TOKENS` in `sdp_capability.py:121` — the host's own hardcoded FRAM list; already tracked by
  the pending todo `fram-parts-ride-the-0x0d-handler-by-pinout-promotion.md`.
- The 216 algorithm 7/8 rows still at 100 µs that this phase does not reach.
- Whether the 9 newly-`supported` AT28C parts want bench proof before shipping as writable.
- Whether the generated database should mark a row as datasheet-corrected (guarded by
  `test_chip_database_field_inventory.py`; has firmware-parity consequences).
- The 29 mis-pinouted chips — folded as a design constraint on the file's shape, not as work.
