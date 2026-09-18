# Phase 199: What the rails can actually deliver - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-18
**Phase:** 199-what-the-rails-can-actually-deliver
**Areas discussed:** Scope (AT28C guard), The ceiling and what it may flip, How the rails get measured, The VPE routing decision, Where the warning lives

---

## Scope — the inherited AT28C guard

| Option | Description | Selected |
|--------|-------------|----------|
| Out — file it as backlog | Phase 199 stays on RAIL-01…05; the 197 evidence note becomes the backlog item's brief | ✓ |
| In — narrow it in this phase | Narrow the guard alongside the rail work, rewriting all three test legs in the same change | |
| In, but only if the bench proves it | Gate the narrowing on an actual AT28C part during this phase's bench session | |

**User's choice:** Out — file it as backlog.
**Notes:** The guard narrowing was routed here by the Phase 197 operator ruling, but no RAIL
requirement covers it. Its own honesty limit (no AT28C part has ever been written, read or erased on
any shield revision) stands unaddressed either way.

---

## The ceiling, and what it may flip

### Q1 — What happens to `RURP_VPP_CEILING_MV`?

| Option | Description | Selected |
|--------|-------------|----------|
| Keep it; add a measured max beside it | 25000 stays as the refusal gate; a separate measured per-rail figure feeds only the warning | |
| Keep it, re-label it theoretical, no new constant | 25000 stays, status recorded as theoretical, classification lives in a record, no behaviour change | ✓ |
| Replace it with the measured figure | The literal reading of RAIL-02; flips all 30 rows to `vpp-exceeds-max` and refuses them | |

**User's choice:** Keep it, re-label it theoretical, no new constant.
**Notes:** Claude had flagged that any lowering turns rows into `ChipNotImplementedError` refusals,
which milestone D-4 forbids. The chosen option leaves the refusal path entirely untouched.

### Q2 — What does the RAIL-03 warning compare against?

| Option | Description | Selected |
|--------|-------------|----------|
| The live board reading, before the operation | Host asks the attached board for its rail and warns when required exceeds it | |
| A host-side constant from the bench measurement | One worst-case constant from the bench session | |
| A measured-rails data file the host reads | Per-revision figures in a data file beside `pinouts.json` | |
| *Other (free text)* | | ✓ |

**User's choice (verbatim):** *"a defalt generic constant of 18v, and then vpe must be used as vpp
and read and bloced if its to high the sam way the vpp is dealt with,"*

**Notes:** Claude mapped this onto the existing code before proceeding and the user confirmed the
reading. Findings that came out of that check: `FLAG_VPE_AS_VPP = 0x10` already exists end-to-end
(`write --vpe-as-vpp` → `build_flags` → wire → `eprom_hv_route_mask`); `eprom_check_vpp` already
routes through the same mask before reading, so the ±window already follows whichever rail is
routed. The answer therefore costs **no firmware change** — only a host-side threshold and trigger.
Claude also flagged that the one pot drives both rails, so a routed 21 V part still hard-errors at
22.7 V until the pot is turned down, and that `MBM27128` must move to 21000 first or nothing fires.

### Q3 — How far on the 22 rows capped at 18 V?

| Option | Description | Selected |
|--------|-------------|----------|
| Correct only the vendored-datasheet rows | `MBM27128` 18000 → 21000 from the already-tracked PDF; classify the rest | ✓ |
| Classify only — no value moves this phase | Literal RAIL-02; ships an untested mechanism | |
| Correct every row the NMOS class argument reaches | Class inference without a per-row datasheet | |

**User's choice:** Correct only the vendored-datasheet rows.
**Notes:** Matches Phase 198's D-08, which refused the same inference for `MBM27C2001`.

### Q4 — Where do the theoretical status and the measured figures get recorded?

| Option | Description | Selected |
|--------|-------------|----------|
| `DECODE-NOTES.md` § 10, beside the code | Follows § 8 (PULSE-01) and § 9 (VOLT-01) | ✓ |
| A phase record in `.planning/` only | Keeps bench measurement out of the product repo | |
| Both — § 10 summarises, the phase record holds the raw | Matches how 197 and 198 split the two | |

**User's choice:** `DECODE-NOTES.md` § 10.
**Notes:** Claude had first established that the label **cannot** go in the source at all — editing
the existing `# RURP boost regulator theoretical ceiling…` comment emits a `+`-prefixed `#` line,
which trips CLAUDE.md's own pre-commit comment check.

---

## How the rails get measured

### Q1 — How many shield revisions?

| Option | Description | Selected |
|--------|-------------|----------|
| Rev 2.0 only, the rest named as unmeasured | The revision gh#71 was reported on | ✓ |
| Rev 2.2 and Rev 2.0, Modified Rev 0 excluded | The two shipped revisions | |
| All three, Rev 0 by DMM alone | Closes part of backlog 999.42 | |

**User's choice:** Rev 2.0 only.
**Notes:** Rev 0 could not have contributed an ADC figure regardless — `hw_read_voltage` returns
`MSG_ERR_REV0_VPP_RD` and `eprom_check_vpp` returns early on that revision.

### Q2 — How is the deliverable maximum taken?

| Option | Description | Selected |
|--------|-------------|----------|
| Held rail at the socket + a paired ADC read | Operator DMM at the socket, plus one `vpp`/`vpe` read at the same pot setting | ✓ |
| DMM at the socket only | No ADC figure to attach RAIL-01's error clause to | |
| ADC monitor readings, error disclosed | Does not meet "at the socket" — the monitors assert no routing bit | |

**User's choice:** Held rail + paired ADC read.
**Notes:** The pair lets the phase measure its own ADC error rather than citing 999.38's. Claude
flagged that `dev reg -f` alone drops the rail on close (DTR reset) and that `hold_rail.py` is the
working approach.

### Q3 — Which routed configurations get a DMM reading?

| Option | Description | Selected |
|--------|-------------|----------|
| All three the 30 rows actually use | Adds direct VPE → pin 21 for the 20 algorithm-`0x0B` rows | |
| Just the two on pin 1 | Drop-resistor → pin 1 and direct VPE → pin 1 | ✓ |
| Just the drop-resistor path | VPE figure taken second-hand from gh#71's log | |

**User's choice:** Just the two on pin 1.
**Notes:** The 20 pin-21 rows are classified against the pin-1 VPE figure as a stated approximation
across a different routing bit (`CTRL_VPE_ENABLE` vs `CTRL_VPP_P1_ENABLE`).

### Q4 — If the bench disagrees with the provisional 18 V?

| Option | Description | Selected |
|--------|-------------|----------|
| 18 V stands; the measurement is recorded beside it | 18000 is upstream's own top-of-scale (`VPP_MV[0xF0]`) | |
| The measurement wins; 18 V was provisional | Ties the shipped threshold to the bench | ✓ |
| Halt and decide at the bench | A `blocking-human` gate mid-phase | |

**User's choice:** The measurement wins.
**Notes:** This makes the bench session load-bearing and imposes a sequencing constraint — the bench
plan is a hard predecessor of the host-threshold plan, and no plan may hardcode 18000 up front.

---

## The VPE routing decision

### Q1 — What decides that the flag gets set?

| Option | Description | Selected |
|--------|-------------|----------|
| The host sets it when required VPP exceeds the threshold | Purely derived; no database field, no generator change | ✓ |
| A per-part field in the database drives it | A 15th emitted field; encodes a shield property into a chip record | |
| Nothing automatic — the warning tells the operator to pass the flag | Preserves the flag's "pure human override" posture | |

**User's choice:** The host sets it.
**Notes:** `write` only was taken as forced rather than asked — `eprom_internal_erase` already runs
undropped and `--vpe-as-vpp` exists on no other command. Recorded as a posture change:
`eprom_hv_route_mask`'s own docs describe the flag as set by no database entry and by a human only.

### Q2 — What does the host say about the pot?

| Option | Description | Selected |
|--------|-------------|----------|
| The warning names the pot target | Everything in one read; firmware then adjudicates | |
| Say nothing about the pot; let the firmware guard speak | No duplicated firmware constant on the host | ✓ |
| Name the pot target only when it is knowable | Two message shapes | |

**User's choice:** Say nothing about the pot.
**Notes:** Follows Phase 198's D-10. Accepted consequence: the first attempt on a newly-routed part
may hard-error on the pot setting, and the firmware message is what tells the operator.

### Q3 — Is the operator told when even VPE falls short?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — one message, both numbers, both rails named | The eight 21–25 V rows read as unreachable | |
| No — one wording for every shortfall | Single message shape; RAIL-03 asks only that both voltages be named | ✓ |
| Yes, and mark those rows in the classification record too | Adds a column true only for the one measured revision | |

**User's choice:** No — one wording for every shortfall.
**Notes:** VPE is still routed and the operation still proceeds in every case, per D-4.

---

## Where the warning lives

### Q1 — Where does the shortfall policy live?

| Option | Description | Selected |
|--------|-------------|----------|
| Its own policy module, `jp5_gate` shape | Pure functions over the wire dict; testable without a board | ✓ |
| Inline in `eprom_operations.py`'s flag build | Smallest diff; untestable without the operator layer | |
| In `eprom_info.py`, beside the existing `support_status` warning | Wrong path — would not reach a direct `write` | |

**User's choice:** Its own policy module.
**Notes:** Difference from all three existing gates: this one never refuses. It warns and returns a
flag.

### Q2 — Which surfaces emit it?

| Option | Description | Selected |
|--------|-------------|----------|
| `write` and `info` | `write` is the path RAIL-03 names; `info` is where a part is checked beforehand | ✓ |
| `write` only | Literal RAIL-03; Phase 200 would have to add `info` anyway | |
| `write`, `info`, and the `dev test` report | Most reach; moves the report's schema version | |

**User's choice:** `write` and `info`.
**Notes:** Also gives Phase 200's VCC-01 its surface without adding one.

### Q3 — What may the held gh#71 draft claim?

| Option | Description | Selected |
|--------|-------------|----------|
| Corrections + the routing answer, no causation claim | Follows 198's D-17; answers `dim20`'s VPE-as-VPP proposal directly | ✓ |
| Add the measured rail figures | Corrects `dim20`'s reading of their own ADC log; from one shield | |
| Post it now rather than holding it | Nothing is pushed; the answer would name changes nobody can install | |

**User's choice:** Corrections + the routing answer, no causation claim.
**Notes:** The maintainer's 2026-09-16 comment already argues the last-256-byte boundary rather than
VPP, across three part sizes. The draft does not advance that. RAIL-05 stays Pending.

### Q4 — What does "reproducible from the recorded numbers" require?

| Option | Description | Selected |
|--------|-------------|----------|
| A table plus a test that can fail | § 10's table, and a test over the live database | ✓ |
| A written table with its method | Nothing catches the table going stale | |
| A checked-in script that regenerates the table | `tools/` sits outside every CI gate | |

**User's choice:** A table plus a test that can fail.

---

## Claude's Discretion

- The exact wording of the shortfall message, subject to one shape and no pot guidance.
- The policy module's name, and whether the threshold reaches it as a constant or a parameter.
- The exact control-register composites held for each of the two measured configurations, and
  whether `hold_rail.py` is copied or invoked from the v1.18 artifacts path.
- Whether the classification test is one file or an extension, and one test or split by `vpp_path`.
- § 10's table ordering.
- Whether a `wire_dict_expected_deltas_199.json` layer is needed — almost certainly yes, since
  `vpp_mv` crosses the wire. Measure rather than assume.

## Deferred Ideas

- Narrowing the AT28C DIP24 hardware-damage guard — ruled out of this phase, becomes its own backlog
  item with `.planning/notes/197-at28c-guard-evidence-for-phase-199.md` as its brief.
- Rev 2.2 and Modified Rev 0 rail measurements (overlaps backlog 999.42).
- The direct-VPE → pin 21 configuration.
- The two TI rows at a hardcoded `vpp_mv: 25000` in `extra_chips.json`, reachable by neither rail.
- Naming the pot target in the host message.
- A distinct wording for "no rail reaches this part".
- The `dev test` diagnostic report as a third warning surface.
- Restoring the pot before Phase 201's bench work; whether Phase 79's ≥25 V pre-gate still stands.
- Whether `--vpe-as-vpp` should stay a manual override at all.
