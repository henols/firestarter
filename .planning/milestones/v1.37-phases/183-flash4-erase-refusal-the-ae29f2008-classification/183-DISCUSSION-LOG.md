# Phase 183: Flash4 Erase Refusal & the AE29F2008 Classification - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-11
**Phase:** 183-flash4-erase-refusal-the-ae29f2008-classification
**Areas discussed:** Where the refusal lives, What `erase` should DO on a flash4 part, SAFE-08 blast radius, SAFE-09's two branches

---

## Area selection

All four offered gray areas were selected. Todo cross-reference (`todo.match-phase 183`) returned 35
candidates, all generic-keyword false positives; none folded.

---

## Where the refusal lives

### Q1 — Which candidate set does SAFE-07/D-3 price?

| Option | Description | Selected |
|--------|-------------|----------|
| All three | SAFE-07's two plus a host pre-flight policy gate (the `sdp_capability.py` / `jp5_gate.py` pattern) | ✓ |
| Exactly the two SAFE-07 names | Host text decorating the returned 0xA5, vs a new `messages.toml` id | |
| Pre-flight gate only, priced against the id | Drop "decorate the returned 0xA5" as strictly worse | |

**User's choice:** All three.
**Notes:** Orchestrator noted the third option is a pattern this repo already shipped twice, so excluding
it would leave D-3's pricing incomplete.

### Q2 — Where does a host-side refusal fire?

| Option | Description | Selected |
|--------|-------------|----------|
| Before the port opens | Matches `sdp_capability.py`'s stated contract | ✓ |
| After connect, before the ERASE command | Keeps connect + chip-ID validation | |
| You decide | | |

**User's choice:** Before the port opens.
**Notes:** The `Connecting... OK` → refusal sequence is what read as a malfunction in gh#62.

### Q3 — Where does the reasoning live?

| Option | Description | Selected |
|--------|-------------|----------|
| Its own policy module | Third sibling to `sdp_capability.py` and `jp5_gate.py` | ✓ |
| Extend an existing module | Fold into one of the two | |
| Inline in `cli_handlers.erase` | Smallest diff | |

**User's choice:** Its own policy module.
**Notes:** The two existing modules are scoped to different hazard axes; mixing them is how predicates
drift.

### Q4 — Does the phase touch the bare refusal for UV-EPROM and SRAM too?

| Option | Description | Selected |
|--------|-------------|----------|
| Flash4 only | SAFE-06's literal scope; note the others as deferred | ✓ |
| Every family the host can name | Reuse `chip_test.py`'s per-family reason strings | |
| Flash4 now, others as a recorded backlog item | | |

**User's choice:** Flash4 only.

### Follow-up: the design in the operator's own words

Asked as the area's continue/next check, the operator instead stated the design directly:

> *"the cli shall directly tell it's not supported and in the fw directly return not supported if someone
> is bypassing the gate"*

Recorded as CONTEXT D-04 (the firmware refusal stays as the backstop) and confirming D-02. The operator
also flagged uncertainty about the SAFE-08 question, which was re-asked in plain language (see that area
below).

---

## What `erase` should DO on a flash4 part

### Q1 — Exit code

| Option | Description | Selected |
|--------|-------------|----------|
| Exit 0, explicit no-op | Never claims the chip was erased; `erase && write` scripts keep working | |
| Exit 1, better-worded refusal | Keeps the failure signal | |
| Exit 0 only with an explicit flag, else exit 1 | Default stays a refusal; opt-in no-op for scripting | ✓ |

**User's choice:** Exit 0 only with an explicit flag, else exit 1.

### Q2 — How the message points at the alternative

| Option | Description | Selected |
|--------|-------------|----------|
| Literal runnable command | Name `firestarter write <chip> <file>` | |
| Describe it in prose | | |
| You decide | | |
| **(free text)** | *"Erase not supported for the EPROM"* | ✓ |

**User's choice:** Free text — *"Erase not supported for the EPROM"*.

**Notes — the clarification exchange, recorded because it changes three documents.** The orchestrator
flagged that this phrasing is close to today's bare `Not supported` with a part name added, that it
conflicts with SAFE-06's requirement to state *cause and alternative*, and that it is the reading
("unavailable") that pushed gh#62's reporter to `--force` under a forged identity. Three readings were
offered:

- **(a)** that line as a headline, followed by cause and alternative — requirement satisfied without a
  copy-pasteable command;
- **(b)** that single line **and nothing more** — SAFE-06 then needs amending, recorded as a deviation
  rather than quietly under-delivered;
- **(c)** something else, supplied verbatim.

**The operator chose (b)**, with the conflict stated on the record before the choice. CONTEXT D-07 and
D-08 carry it, including the amendment table for `REQUIREMENTS.md` SAFE-06, the ROADMAP Phase 183 goal
and success criterion 1. The cause and alternative move to REPLY-03 (Phase 187), which already owes them
to gh#62.

### Q3 — Does the CLI warn against the forged-identity `--force` workaround?

| Option | Description | Selected |
|--------|-------------|----------|
| Both — CLI says it too | A short "do not run this under another chip's identity with --force" clause | |
| REPLY-03 only | Keep the CLI message short; the warning is issue-specific | ✓ |
| CLI warns only when `--force` is present | | |

**User's choice:** REPLY-03 only.

---

## SAFE-08 blast radius

The first framing of this area was not understood — the operator said so plainly and restated the design
instead (see Area 1's follow-up). It was re-asked in plain language, without jargon, after the
orchestrator confirmed that neither choice affects the refusal itself.

### Q1 (re-asked) — The two dead pointers at the 12 V erase routine

| Option | Description | Selected |
|--------|-------------|----------|
| Delete them and the routine | The 12 V-on-a-5 V-part routine stops existing; firmware shrinks | ✓ |
| Keep both, write down why | Zero firmware change, no Phase 185 knock-on; SAFE-08 permits it | |
| Delete the erase-command pointer only | Routine and write-path pointer survive | |

**User's choice:** Delete them and the routine.
**Notes:** The plain-language re-ask made explicit that the arm's assignment *does* execute while the
function pointer never fires, that the same routine is also pointed at from the write path behind a flag
the host never sets, and that the refusal is unchanged either way.

### Q2 — `check_erase_no_vpp.py`'s stale citation and rationale

| Option | Description | Selected |
|--------|-------------|----------|
| Fix the citation + update the rationale here | Re-cite by symbol and enclosing scope (the CLAIM-06 lesson) | ✓ (orchestrator) |
| Fix the citation only | Leaves a gate whose justification describes deleted code | |
| Route it all to Phase 185 (CLAIM-06) | Same defect class, but 185 is marked independent | |

**User's choice:** No preference — orchestrator recommendation taken (CONTEXT D-14).
**Notes:** The gate's docstring cites `flash_5v_page.cpp` "lines 196-231" for a function at 193-225 in a
225-line file — a range that cannot exist. Measured during discussion: the gate does **not** break
functionally, because its non-vacuity anchor is `eeprom28c_erase_execute`-scoped. Only the prose is false.

### Q3 — Size baseline ordering vs Phase 185

| Option | Description | Selected |
|--------|-------------|----------|
| Record 185 as depending on 183 | Amend ROADMAP so the cold re-record follows 183's firmware delta | ✓ (orchestrator) |
| 183 re-records the baseline itself | Puts CLAIM-04/05's mechanism in two phases | |
| Avoid the collision — no firmware delta in 183 | Only viable with "keep both" above | |

**User's choice:** No preference — orchestrator recommendation taken (CONTEXT D-15).

### Q4 — What counts as the SAFE-07 measurement?

| Option | Description | Selected |
|--------|-------------|----------|
| Cold `pio run` on all three AVR targets | `rm -rf .pio/build/<env>` then one `pio run -e <env>` each | ✓ (orchestrator) |
| Leonardo only | The binding constraint | |
| You decide | | |

**User's choice:** No preference — orchestrator recommendation taken (CONTEXT D-16).

---

## SAFE-09's two branches

### Q1 — If the classification is CORRECT, what happens to the software-chip-erase finding?

| Option | Description | Selected |
|--------|-------------|----------|
| Record + backlog it | Verdict recorded; the `0x05` chip-erase filed for later | ✓ |
| Build it in this phase | Would reverse SAFE-06 and breach the no-firmware-behaviour-change boundary | |
| Record only, no backlog item | | |

**User's choice:** Record + backlog it.

### Q2 — Is datasheet-by-equivalence acceptable evidence?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, if the equivalence is proven and stated | Use the W29C020C datasheet with the chain recorded | |
| No — verdict must be UNVERIFIED without a primary datasheet | | |
| Yes, and additionally check the infoic upstream row | Equivalence plus what upstream actually declares | ✓ |

**User's choice:** Yes, and additionally check the infoic upstream row.
**Notes:** AE29F2008 (ASD-branded) has no retrievable primary datasheet and reads as a re-badge. The
W29C020C datasheet matches the DB row on chip ID (`0xDA45`), size (256K×8 = `0x40000`), page size (128 B)
and 5 V-only operation, and has a 50 ms fast chip-erase — which explains the reporter's successful
`SST39SF020 --force` erase without contradicting the classification.

### Q3 — If MISCLASSIFIED, what override mechanism?

| Option | Description | Selected |
|--------|-------------|----------|
| Named root-cause rule, Phase 182 pattern | `RULE_PHASE182_A19_PINOUT` precedent + `diff_db` + DECODE-NOTES | ✓ |
| Per-part exception table | The hand-kept list D-4 rejects | |
| Don't decide now — only if the branch fires | | |

**User's choice:** Named root-cause rule, Phase 182 pattern.

### Q4 — Does `support_status` change?

| Option | Description | Selected |
|--------|-------------|----------|
| No — untouched | v1.22's zero-status-change precedent on a software-only, no-bench milestone | ✓ (orchestrator) |
| Yes, if research changes the classification | | |
| You decide | | |
| **(free text)** | *"If erase is not need blank check is unnecessary, but for uv EPROMs it's still has real value"* | |

**User's choice:** The operator's answer addressed blank-check policy rather than `support_status`.
Orchestrator took "untouched" (CONTEXT D-22) — the part writes, reads, blank-checks and verifies; only the
standalone erase is refused, correctly, and nothing in the evidence moves the status.

**Notes on the blank-check observation.** Verified during discussion as **already implemented**, in
almost the operator's own words: `chip_test.py:704-714` marks the blank check NA for auto-erase-on-write
protocols (*"no step in this plan can ever leave the device blank"*) while `:691-692` keeps it for UV
(*"the write is irrecoverable and only UV light erases, so 'not blank' is a real pre-write finding"*), and
`flash_5v_page_write_init` has had no pre-write blank check since Phase 153 (*"it was a false
precondition, not a safety net"*). The one remaining surface, the standalone `firestarter blank` command,
was **considered and kept** — it is the oracle gh#62's reporter used to prove their erase had worked, so
refusing it would have destroyed the evidence in the issue.

---

## Claude's Discretion

Four items where the operator expressed no preference and the orchestrator's recommendation was taken,
recorded in CONTEXT.md as decisions rather than left open:

- **D-14** — `check_erase_no_vpp.py`'s citation and rationale are fixed in this phase.
- **D-15** — ROADMAP amended so Phase 185's baseline re-record depends on Phase 183.
- **D-16** — the SAFE-07 measurement is a cold build of all three AVR targets.
- **D-22** — `support_status` for AE29F2008 is untouched.

Wording of the one-line refusal beyond its shape is planner discretion, provided it carries no cause, no
alternative and no `--force` clause.

---

## Deferred Ideas

1. **VPP-reroute confirmation gate for parts needing JP4's third position** — operator-raised during
   Area 1. Socket pin 25 confirmed by Phase 182's bench probe; blocked on two measured facts (`firestarter
   hw` reports a bucket spanning Rev 2.0/2.1/2.2, so "HW < 2.2" is not decidable; and the TI 2516/2532
   family is indistinguishable by every existing DB field, so a D-4-compliant predicate needs a new
   `build_db.py` field first). The operator's escape hatch — early boards may work with a hand-soldered
   wire, so the gate must offer proceed-anyway — is preserved. Cross-refs:
   `.planning/seeds/rev22-3pin-header-2516-family-support.md`, ROADMAP Phase 999.58.
2. **Generalize the refusal beyond flash4** — to UV-EPROM, SRAM and `0x0D`, reusing `chip_test.py`'s
   per-family reason strings so `erase` and `dev test` agree.
3. **Software chip-erase for the `0x05` family** — templated on `eeprom28c_erase_execute`'s AN-0544B
   sequence. Reverses SAFE-06, so it needs an explicit operator scope decision.
4. **`vpp_mv: 12000` on a 5 V-only part** — filed in case research finds the field inert; a new defect if
   it proves live.
