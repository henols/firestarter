# Phase 198: The two voltage nibbles - Research

**Researched:** 2026-09-18
**Domain:** Generated-database decode correctness — `infoic.xml` voltage-word semantics, upstream rail-index tables, override-file entries, regeneration blast radius
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Copied verbatim from `198-CONTEXT.md` § Implementation Decisions. **Do not re-litigate any of these.**

- **D-01:** **`VCC_VOLTAGES` is completed from upstream's `xg_vcc_voltages[]`.** Measured against
  the pinned `database.c @ a8efaedc`: the `xg` table is a **strict, conflict-free superset** of
  `tl866ii_vcc_voltages[]` — 6 shared indices, **zero** value conflicts, plus 9 more
  (`0x06`=1800, `0x07`=2500, `0x08`=3000, `0x09`=1200, `0x0A`=4750, `0x0B`=5250, `0x0C`=5750,
  `0x0D`=6000, `0x0E`=6250). That is one encoding implemented to different depths by different
  programmer models, not two encodings — so completing it is **decoder completion under milestone
  D-2**, not a correction, and the table stays in code.
  **Contrast, and the reason this is not model-mixing:** `tl866a_vcc_voltages[]` conflicts on 4 of
  its 6 shared indices and `tl866a_vpp_voltages[]` on **8 of 8**. The TL866A is a genuinely
  different encoding and must not be used.
  **Effect:** 24 rows stop reaching a fabricated 5000 mV through `.get(idx, 5000)`.

- **D-02:** **`VPP_MV` is completed too, and the `& 0xF0` mask is fixed.** Add `0xF1`=25000 and
  `0xF2`=21000. The current `VPP_MV.get(voltages & 0xF0, 0)` collapses `0xF1` and `0xF2` onto
  `0xF0`, so a 25 V part would silently decode as 18 V — a 7 V under-report on the rail gh#71 is
  already about. Key on the full low byte with the option bits stripped instead.
  **No row carries `0xF1` or `0xF2` today** (measured across all 767 filtered rows), so
  **byte-identical regeneration is the proof** this change ships zero diff.
  — **Reversibility:** reversible — the entries are unreachable until upstream adds such a row.

- **D-03:** **The `.get(idx, default)` silent fallback is NOT replaced by a raise.** The
  fail-closed option was offered and declined. The generator keeps defaulting rather than stopping
  the build. Anything still unmapped after D-01 must therefore be named in the write-down, because
  nothing mechanical will report it.

- **D-04:** **The 12 rows at vdd index `0x06` keep `vdd_mv: 5000`, byte-identical to today.**
  The completed table decodes `0x06` to 1800 mV; 1.8 V is not credible as a program rail for a 5 V
  28C64-class EEPROM. Those 12 are exactly sub-group 2 of the VOLT-03 group
  (EXEL ×7, ST ×3, SGS-THOMSON ×2), all carrying `voltages=0x64xx`.
  — **Reversibility:** reversible — deleting the 12 entries restores the decoded 1800.

- **D-05:** **The carve-out is expressed as 12 explicit override entries, not as a table omission.**
  `VCC_VOLTAGES` gets `0x06`=1800 like every other index; the exception then lives in
  `datasheet_overrides.json` as 12 entries (`was: 1800, is: 5000`), each `UNSOURCED`, each stating
  that the completed decode is not credible for the part class and naming what would close it —
  the part's own datasheet. **Rejected: omitting `0x06` from the table.** That would be
  byte-identical too, but the 12 rows would reach 5000 through the same silent `.get` default this
  phase is otherwise closing, and it would read as an oversight rather than a decision.
  This follows the six `UNSOURCED` NMOS entries Phase 197 already ships.

- **D-06:** **The `vdd < vcc` predicate is the group's key, and it is exact.** Measured under the
  completed table across all 767 filtered rows: `decoded vdd < decoded vcc` selects **exactly 28
  rows and nothing else** — 12 at (5500, 1800) and 16 at (5500, 3300) — against 373 rows at
  `vdd == vcc` and 366 at `vdd > vcc`. A program rail below the read rail is internally
  contradictory, so this is value-keyed, part-name-free and non-tunable: the `_VCC_MARGIN_RAIL_MV`
  shape, relational. **Phase 148 measured and rejected the inverse relation** (`vcc < vdd`, 225
  rows, sweeping 167 UV-EPROMs); this is its complement and does not inherit that defect.
  **The predicate is documented, not shipped as a correction** — no value hangs off it this phase.

- **D-07:** **VPP goes to 12500, not 12200.** MBM27C4001's own datasheet (Edition 1.0, March 1993,
  attached to gh#66 by `dim20`) specifies 12.5 V ± 0.3 V, i.e. 12.2–12.8 V. 12500 is the datasheet
  nominal, is what the sibling `MBM27C1000P` already carries via VPP index `0x60`, and is a rail
  the encoding can express. 12200 would satisfy VOLT-02's literal "at or above 12.2 V" while
  sitting at the very bottom of the tolerance band with no margin below it.

- **D-08:** **Two rows get the VPP correction: `FUJITSU/MBM27C1001` and `FUJITSU/MBM27C4001`.**
  Both PDFs are git-tracked, so no OVR-03 citation dangles. **`FUJITSU/MBM27C2001` gets nothing**
  and stays at 12000 — it carries the identical `voltages=0x4000` word but has no vendored
  datasheet, and citing its sibling `MBM27C2000P`'s 12500 would apply one part's reading to another
  without evidence, which is the practice D-02 of Phase 197 exists to make impossible. Record it in
  the write-down as a known, unsourced family inconsistency.

- **D-09:** **`vdd_mv` 5500 → 6000 is corrected in THIS phase, not Phase 200,** for the three rows
  whose vendored datasheets state it: `FUJITSU/MBM27C4001`, `FUJITSU/MBM27C1001` and
  `FUJITSU/MBM27128`. All three datasheets say 6.0 V ± 0.25 V, and two of the three override notes
  already quote that figure verbatim. Phase 200 owns *surfacing* `vdd_mv`, so it should surface a
  correct number rather than open by re-deciding a data correction whose evidence is on disk.

- **D-10:** **The firmware guard-band consequence is recorded in the phase record only.** The
  firmware accepts `vpp_mv × 95/100` (low, warning) to `vpp_mv + 500` (high, hard error). Raising
  to 12500 moves the settable band **11400–12500 → 11875–13000**, which makes the datasheet's
  12.2–12.8 V window fully settable — `dim20` could not set 12.5 V precisely because the database
  targeted 12000. 13000 still sits under the datasheet's 13.5 V abs-max warning. **No host-side
  test encodes this** (it would duplicate a firmware constant across repos) and **the public gh#66
  answer does not mention it** — that answer stays strictly to database values that changed.

- **D-11:** **All 28 rows ship unchanged.** VOLT-03 explicitly permits this: *"Leaving them
  unproven and unchanged is an acceptable outcome; changing them on an unproven assumption is
  not."* No plausibility floor, no clamp, no `support_status` change. The four options of
  fail-the-build, mark-unproven and clamp-to-vcc were each offered and declined.
  — **Reversibility:** reversible — nothing ships differently from today for these rows.

- **D-12:** **The todo closes to `completed/` and a successor backlog entry is filed.**
  `.planning/todos/pending/vcc-5500-high-margin-verify-rail-group.md` asked what the nibbles encode;
  this phase answers it, so it is genuinely completed even though no value moved. The successor
  carries the residue: 28 rows still reporting 5.5 V, 12 of them held at an unsourced 5000, closable
  only at one datasheet per row. Follows Phase 197's 999.69/70/71 pattern.

- **D-13:** **Sub-group 1's premise is tested per row, not restated.** The todo characterises its 16
  rows as *"genuinely-3.3V Microchip memory-family parts"*, but `28C16A`, `28C17A`, `28C64A`,
  `28C64B` and `28C256` are 5 V parts by class and only `28LV64A` is low-voltage. If that is right,
  substituting `vdd` there would set 5 V EEPROMs to 3.3 V — exactly the outcome Phase 148 measured
  and rejected for all three of its alternative keys. Classify all 16 by part class, state which way
  each cuts, on the `197-at28c-guard-evidence-for-phase-199.md` precedent: reproducible method
  first, every row disposed with a reason, a named honesty limit. Note the repo vendors **no**
  Microchip or AMD 28C datasheet, so the honesty limit is real and must be stated.

- **D-14:** **The archived `148-DB-DIFF.md` is NOT edited.** Its § Non-claim states sub-group 2's
  `vdd_mv` "already records" 5.0 V, which this phase falsifies — that 5000 is a fallback from an
  unmapped index, not a decode. **Decided by Claude on project precedent, not asked:** archived
  `.planning` records are historical-by-intent and rewriting one destroys the evidence of what was
  believed. The falsification is recorded in Phase 198's artifacts and in `DECODE-NOTES.md`,
  pointing at the archived text.

- **D-15:** **`DECODE-NOTES.md` § 9 makes the general finding, with its limits named.** The finding:
  the two nibbles and the VPP byte select a **programmer rail index, not a chip requirement**; the
  index→volt map is **model-dependent** (`0x00` is 12 V on the TL866-II and 12.5 V on the TL866A;
  `0x20` is 9.5 V and 21 V respectively); and a part whose datasheet value is not a rail gets the
  **nearest selectable one**. Evidence: upstream's own comment at `database.c:123` —
  *"These are not raw DAC output values, but rather indices into internal lookup tables defined in
  the firmware"* — plus three Fujitsu datasheets on disk that all state 6.0 V ± 0.25 V where the
  index selects 5.5 V, because **neither 5.5 nor 6.5 is inside 5.75–6.25** and those are the only
  two rails the TL866-II has near it.
  **The limits are mandatory:** name that the datasheet corroboration is n = 3, all Fujitsu; that
  no claim is made about the 167 unreached index-`0x4` rows; and that the finding does not assert
  any particular row's value is correct.
  § 9 follows PULSE-01's § 8 — markdown, next to the code, so the no-comments rule does not reach it.
  — **Reversibility:** costly — Phases 199 and 200 will build their warning wording on this
  framing, and it reframes every voltage in the generated database as a programmer setting rather
  than a chip requirement.

- **D-16:** **The NMOS 25 V / 21 V values are NOT secretly decodable — this was checked and closed.**
  `xg_vpp_voltages[]` carries `0xF1`=25 V and `0xF2`=21 V, which are exactly the two figures Phase
  197's six `UNSOURCED` entries hold. Measured: **no filtered row carries `0xF1` or `0xF2`**. All
  eight NMOS 2716/2732 rows carry VPP byte `0xF0` = 18 V, the TL866-II's maximum — as does
  `MBM27128`, which gh#71 measured as needing 21 V. Record this: it is a tempting false lead that
  would otherwise be rediscovered, and the saturation-at-the-model-maximum pattern is direct
  evidence for D-15.

- **D-17:** **The draft is written, held, and claims corrections only.** Carried forward from
  197-08's operator ruling without re-asking: nothing is pushed, the branch has no upstream, so no
  version or sha a reader could look up exists yet. The draft states the two corrected values and
  the confirmed 6.0 V `vdd_mv` finding under an explicit *"this does not close this report"*
  heading, credits `dim20` for the datasheet, and **says nothing new about causation** — `dim20`
  already proved correct VPP alone does not fix it (12.4 V, identical failure at `0x07ff00`), and
  the last-256-byte hypothesis is already posted and is not this phase's to advance.
  **VOLT-04 is left Pending**, exactly as PULSE-04 is.

- **D-18:** **One consolidated held-pending list.** Phase 198 adds gh#66 to the deferral record that
  `197-GH70-ANSWER.md` § "Held-pending deferral" established, so whoever closes v1.40 finds one list
  naming every issue to post with the same four steps each, rather than two held drafts in two
  directories to find independently.

**Carried forward from Phase 197 — locked, do not re-litigate:**

- Override key is **`MANUFACTURER/ALIAS`**; **one entry targets exactly one row** (197 D-01, D-02).
- An override **substitutes the decoded input**, before `classify()`'s downstream derivations
  (197 D-03). `support_status` stays derived and is never written by hand.
- Every entry carries `was`/`is` and a datasheet path or the literal `UNSOURCED`; the recorded
  `was` is asserted against the live decode and a mismatch fails the build (197 D-04, D-20).
- The generator **fails closed** on an unknown key, unknown field, duplicate target, unsorted file,
  per-field type mismatch, and a no-op entry (OVR-04, 197 D-04).
- **Decode tables stay in code** — they are the decoder, not a correction (milestone D-2). Only
  values that contradict the decode move into the override file (milestone D-3).
- **Nothing part-specific is hardcoded in the generator** (milestone D-1); any survivor is named
  with its proof under the OVR-06 census.
- Decode findings land in `tools/DECODE-NOTES.md` as a numbered section (PULSE-01 is § 8).
- Inventory and disposition records land in the phase directory on the
  `177-READBACK-INVENTORY.md` precedent: reproducible method first, every row disposed, a named
  honesty limit.
- `chip_database.json` is **GENERATED**. Never hand-edit.
- **No comments in product source**, for any reason (CLAUDE.md, hard rule).

### Claude's Discretion

- How the 12 `0x06` override entries are covered for non-vacuity — whether one planted-mutation
  test in the 197-06 shape, or per-entry assertions.
- Whether the regeneration diff needs a `tests/golden/wire_dict_expected_deltas_198.json` delta
  layer. It almost certainly does: `vpp_mv` crosses the wire, so the two VPP corrections will
  redden `tests/test_wire_dict_equivalence.py` the way the three pulse corrections did. Measure it
  rather than assuming — note that `vcc`/`vdd` are inert on the wire (148-DB-DIFF § Evidence
  Ceiling), so the vdd changes may contribute nothing.
- Where the sub-group-1 per-row disposition file lands, and its exact name.
- The exact wording of the 12 `UNSOURCED` notes, subject to D-05's requirement that each names what
  would close it.
- Whether the `vdd < vcc` predicate ships as a build-time assertion (reporting, not correcting) or
  only as a documented measurement.

### Deferred Ideas (OUT OF SCOPE)

- **The 167 index-`0x4` rows this phase does not reach.** `vdd 5500` where the datasheet band is
  5.75–6.25 and the programmer has no rail inside it. Fleet-scale, in the same shape as the 215-row
  pulse inventory and the 563-row `vpp 12000` group. One datasheet per row under Phase 197's D-02.
  Phase 200 will surface whatever these say.
- **`FUJITSU/MBM27C2001`** stays at `vpp 12000` with no vendored datasheet while its sibling
  `MBM27C2000P` carries 12500 — the family stays internally inconsistent by decision (D-08).
- **The 4 `adapter-required` rows inside the 28** (`28C04A`, `28C04AF`, `28C16A`, `28C16AF`) flip to
  `supported` if Phase 199 narrows the AT28C hardware-damage guard, and would then ship `vcc 5500`.
  Phase 199 inherits this via `.planning/notes/197-at28c-guard-evidence-for-phase-199.md`.
- **`chip_info` gates `can_adjust_vcc` / `can_adjust_vpp` upstream and the generator ignores it
  entirely.** Unexamined; may say which rows' voltages upstream itself treats as adjustable.
- **Making the `.get(idx, default)` fallbacks fail closed** — offered and declined (D-03). If ever
  wanted, it belongs with whatever phase is willing to absorb a build that stops on existing rows.
- **A build-time assertion on the `vdd < vcc` predicate** — reporting rather than correcting, so a
  29th row joining the group cannot arrive silently. Left to Claude's discretion this phase.
- **`VOLT-F1`** (REQUIREMENTS.md, Future) — the remaining families touching `VCC_VOLTAGES[0x04]`.
  D-15's general finding bears on whether it is ever worth opening.

**Also explicitly out of scope for this research and this phase:** the rail ceiling and
warn-on-shortfall (Phase 199), surfacing `vdd_mv` (Phase 200), the firmware blank-check region
(Phase 201), any firmware change, pinout correctness, adding chips.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| **VOLT-01** | What the two voltage nibbles encode is established per algorithm family — the unproven question that has blocked the 28-row `vcc_mv: 5500` group since v1.32 Phase 148. `[VERIFIED: .planning/REQUIREMENTS.md:68-69]` | F-1 (upstream tables transcribed and every D-01/D-02/D-15 arithmetic claim re-derived), F-2 (the powerdown-flag correction), F-9 (§ 8/§ 6 template for the § 9 write-down) |
| **VOLT-02** | The Fujitsu 1 Mbit and 4 Mbit parts ask for a VPP at or above their datasheet floor of 12.2 V, rather than the 12.0 V that reads as in-band under the accepted window while sitting below the part's own minimum. `[VERIFIED: .planning/REQUIREMENTS.md:70-72]` | F-5 (the exact 15-row regeneration diff, both Fujitsu VPP rows confirmed), F-6 (override-file shape and the datasheet-tracking gate), F-7 (wire-dict delta layer = exactly 2 entries), F-8 (snapshot re-record = exactly 2 lines) |
| **VOLT-03** | The 28 rows reporting 5.5 V either report their real operating voltage or are left unchanged with the reason recorded. Leaving them unproven and unchanged is an acceptable outcome; changing them on an unproven assumption is not. `[VERIFIED: .planning/REQUIREMENTS.md:73-75]` | F-3 (the 28-row predicate re-measured exactly), F-4 (all 16 sub-group-1 rows enumerated and classified, with the in-repo corroboration and the named honesty limit), F-10 (todo-close and backlog-entry mechanics) |
| **VOLT-04** | gh#66 is answered on the issue with the resulting values and the version carrying them. `[VERIFIED: .planning/REQUIREMENTS.md:76-77]` | F-11 (gh#66 live state; the `197-GH70-ANSWER.md` held-pending template and its four steps, which D-18 requires gh#66 be added to) |

**Requirement status today** `[VERIFIED: .planning/REQUIREMENTS.md:146-149]`: all four are `Pending`,
each mapped to Phase 198. VOLT-04 stays `Pending` at phase end by D-17 — the planner must not write a
task that flips it.
</phase_requirements>

## Summary

This phase is a **decode-completion and evidence-writing** phase against a generated artifact. There
is no new library, no new dependency, and no new subsystem. Everything lands in four files inside the
`firestarter_app` submodule (`tools/build_db.py`, `tools/datasheet_overrides.json`,
`tools/DECODE-NOTES.md`, and the regenerated `firestarter/data/chip_database.json`), plus test
fixtures and `.planning/` records. The whole risk profile is therefore *measurement* risk, not
integration risk: the question is not "will it work" but "exactly which rows move, which tests
redden, and which existing claims in the tree are false".

Every numeric claim in `198-CONTEXT.md` was independently re-measured this session against the pinned
upstream and the live tree, and **every one held**. The pinned `infoic.xml` in the prior session's
scratchpad hashes identically to a fresh download of the pinned URL. The 767-row filtered population,
the nibble census, the `0xF1`/`0xF2` absence, the exact 28-row `vdd < vcc` split of 16 + 12, the 4/6
and 8/8 TL866A conflict counts, and the 9-index `xg` superset are all confirmed to the digit. Three
claims in the surrounding documents did **not** hold and the planner must act on them: CONTEXT's
citation of the decisive upstream comment is two lines off (it is `database.c:125-126`, not `:123`);
CONTEXT's "Established Patterns" claim that *both* decode tables carry a `[VERIFIED: … @ a8efaedc]`
marker is false for `VPP_MV`, which carries an unversioned marker naming a different file; and the
`[VERIFIED: minipro database.c#L130-L135 …]` marker that sits on `VCC_VOLTAGES` **and is duplicated
onto `_VCC_MARGIN_RAIL_MV`** points at `tl866a_vpp_voltages[]`, not the `tl866ii_vcc_voltages[]` it
names — a falsified provenance marker on a line D-01 must edit anyway.

The two discretionary questions CONTEXT handed over are both now settled by measurement rather than
inference. **A `wire_dict_expected_deltas_198.json` layer is required**, and it needs exactly two
entries — the twelve `vdd_mv` movements contribute zero wire deltas, as predicted. **The snapshot
re-record is required and is exactly two lines**, verified with `--numstat`. The full blast radius is
**five tests across three files**, not the three a database-only swap reveals: `test_datasheet_overrides.py`
pins the override entry count and the `UNSOURCED` count as exact literals (`9` and `6`), and both
must move to `22` and `18`. That pair is the single most likely thing for a planner to miss, because
it does not redden until the override file itself changes.

The sharpest implementation trap is in D-02. Read literally, "key on the full low byte" breaks **142
rows** — the seven low-byte values `0x01`, `0x04`, `0x08`, `0x0A`, `0x0B`, `0x11`, `0x71` currently
mask down to a real rail and would fall to the `0` default under exact-byte keying. The only
byte-identical expression is an exact-match test for `0xF1`/`0xF2` *before* masking. Both variants
were run against all 767 rows; the numbers below are measured, not reasoned.

**Primary recommendation:** Treat this as a measurement-first phase. Complete `VCC_VOLTAGES` from
`xg_vcc_voltages[]` and special-case `0xF1`/`0xF2` ahead of the `& 0xF0` mask; add 13 override keys
(not 17 — 17 is the field count, and two of the keys already exist); update five test assertions
across three files; write § 9 on the § 8 template; and correct the two false provenance markers you
are already editing. The regeneration diff is exactly 15 rows and 17 field values, and nothing else
in the 746-row database moves.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Rail-index → millivolt decode (`VCC_VOLTAGES`, `VPP_MV`) | Build-time generator (`tools/build_db.py`) | — | It is the decoder. Milestone D-2 keeps decode tables in code; they are not corrections. |
| Per-part contradiction of a decode (Fujitsu VPP/vdd, the 12 held rows) | Build-time data (`tools/datasheet_overrides.json`) | — | Milestone D-3: only values that contradict the decode move into the override file. Nothing part-specific may live in the generator (milestone D-1). |
| Decode rationale and the general finding | Documentation (`tools/DECODE-NOTES.md` § 9) | `.planning/` phase records | CLAUDE.md forbids source comments absolutely; markdown beside the code is the only legal home, and § 8 is the shipped precedent. |
| Per-row disposition evidence | `.planning/` phase artifact | — | The `177-READBACK-INVENTORY.md` / `197-PULSE-INVENTORY.md` precedent: reproducible method, every row disposed, named honesty limit. |
| Emitted voltage values | Generated artifact (`firestarter/data/chip_database.json`) | — | GENERATED. Never hand-edited. Regeneration is the only write path. |
| Regression pinning of the change | Host test suite (`firestarter_app/tests/`) | — | `firestarter_app/tools/` sits outside every CI gate (no mypy, no ruff); coverage must land in `tests/`, which does run. |
| Public answer to the community report | `.planning/` held draft, posted at the v1.40 beta cut | — | D-17: the branch has no upstream, so no version a reader can resolve exists yet. |
| Firmware guard-band consequence | **Nowhere in code** — phase record only | — | D-10 declines to mirror a firmware constant onto the host; this phase is host-only. |

## Project Constraints (from CLAUDE.md)

Extracted from `/workspaces/CLAUDE.md`. These carry the same authority as locked decisions.

| # | Directive | Bearing on this phase |
|---|-----------|----------------------|
| C-1 | **Write no comments into product source.** Covers everything under `firestarter_fw/` and `firestarter_app/`. **Not overridable by a plan, task, skill, or subagent instruction.** The rule is *not* "no GSD citations" — add no `#`, `//` or `/* */` line, for any reason. | `build_db.py` is dense with comments and this phase edits lines that carry them. See F-12 for the exact inventory. **Planners:** do not write "add a comment citing X" into a plan, and do not make "a comment exists" an acceptance criterion. |
| C-2 | **Pre-commit check, pathspec load-bearing:** `git -C firestarter_app diff --cached -- '*.py' \| /usr/bin/grep -E '^\+\s*#' \| /usr/bin/grep -v '^\+\s*#!'` must print nothing. | A **dedent or reflow** makes pre-existing unchanged comments reappear as `+` lines and trips this. This already happened in 197-02 — see F-12 and `.planning/notes/197-build-db-comment-provenance-rescued.md`. |
| C-3 | **Deleting one clause from an existing comment reflows the rest. Read the remainder. Confirm it still parses and that every pronoun still has an antecedent.** | Directly applicable: the `& 0xF0` block (5 lines) and the `_VCC_MARGIN_RAIL_MV` block (5 lines) both sit on edited code. |
| C-4 | **`chip_database.json` is GENERATED. Never hand-edit.** | The regeneration diff is the deliverable, not an edit. |
| C-5 | **Milestone work forks off `beta`, in all three repos. Never commit to `beta`. Never commit to `main`.** Branch is `v1.40-program-parameter-fidelity`. | Confirmed live: `firestarter_app` HEAD is on `v1.40-program-parameter-fidelity` at `0372cc6`. `[VERIFIED: git rev-parse --abbrev-ref HEAD, run this session]` |
| C-6 | **A push to `beta` in `firestarter_app` PUBLISHES to PyPI.** No path filter; a docs-only push publishes. A PyPI version can never be reused. | Nothing in this phase pushes. D-17's hold exists precisely because no published version exists yet. |
| C-7 | **Cross-repo obligations** — this phase is host-only; no firmware change. D-10 deliberately declines to mirror a firmware constant onto the host. | Do not add a host test encoding the firmware guard band. |
| C-8 | Docstrings are a separate question; Click docstrings in `firestarter_app` are user-facing `--help` text, not commentary. | Not reached by this phase — no CLI surface changes. |

**Config note** `[VERIFIED: .planning/config.json, read this session]`: `workflow.nyquist_validation`
is explicitly `false`, so the Validation Architecture section is omitted from this research by its own
skip rule. `parallelization` is a proper JSON boolean `false` (not the always-truthy string form), so
plans execute sequentially.

## Findings

### F-1 — The upstream voltage tables, transcribed verbatim from the pinned sha (HIGH)

Fetched this session from
`https://gitlab.com/DavidGriffith/minipro/-/raw/a8efaedc236c1d9718bd28299dfbb99536b010ff/src/database.c`
— 2114 lines, sha256 `896f1948e67a03f333ade157845ac2cf1d4dda27e571c989729de2dd928ff72e`.

`[VERIFIED: database.c @ a8efaedc, lines 130-190, fetched and read this session]`

```c
 static const parameters_t tl866a_vpp_voltages[] =            // L130-L133
       {
             { "10", 0x40 }, { "12.5", 0x00 }, { "13.5", 0x30 },
             { "14", 0x50 }, { "16", 0x10 }, { "17", 0x70 },
             { "18", 0x60 }, { "21", 0x20 }, { NULL, 0x00 }
       };

 static const parameters_t tl866a_vcc_voltages[] =            // L137-L142
       {
             { "3.3", 0x02 }, { "4", 0x01 }, { "4.5", 0x05 },
             { "5", 0x00 }, { "5.5", 0x04 }, { "6.5", 0x03 },
             { NULL, 0x00 }
       };

 static const parameters_t tl866ii_vpp_voltages[] =           // L144-L152
       {
             { "9", 0x10 }, { "9.5", 0x20 }, { "10", 0x30 },
             { "11", 0x40 }, { "11.5", 0x50 }, { "12", 0x00 },
             { "12.5", 0x60 }, { "13", 0x70 }, { "13.5", 0x80 },
             { "14", 0x90 }, { "14.5", 0xa0 }, { "15.5", 0xb0 },
             { "16", 0xc0 }, { "16.5", 0xd0 }, { "17", 0xe0 },
             { "18", 0xf0 }, { NULL, 0x00 }
       };

 static const parameters_t tl866ii_vcc_voltages[] =           // L154-L159
       {
             { "3.3", 0x01 }, { "4", 0x02 }, { "4.5", 0x03 },
			 { "5", 0x00 }, { "5.5", 0x04 }, { "6.5", 0x05 },
			 { NULL, 0x00 }
       };

 static const parameters_t xg_vpp_voltages[] =                // L161-L170
       {
             { "9", 0x10 }, { "9.5", 0x20 }, { "10", 0x30 },
             { "11", 0x40 }, { "11.5", 0x50 }, { "12", 0x00 },
             { "12.5", 0x60 }, { "13", 0x70 }, { "13.5", 0x80 },
             { "14", 0x90 }, { "14.5", 0xa0 }, { "15.5", 0xb0 },
             { "16", 0xc0 }, { "16.5", 0xd0 }, { "17", 0xe0 },
             { "18", 0xf0 }, { "21", 0xf2 }, { "25", 0xf1 },
             { NULL, 0x00 }
       };

static const parameters_t xg_vcc_voltages[] =                 // L182-L190
       {
             { "1.2", 0x09 }, { "1.8", 0x06 }, { "2.5", 0x07 },
             { "3", 0x08 }, { "3.3", 0x01 }, { "4", 0x02 },
             { "4.5", 0x03 }, { "4.75", 0x0a }, { "5", 0x00 },
             { "5.25", 0x0b }, { "5.5", 0x04 },  { "5.75", 0x0c },
             { "6", 0x0d }, { "6.25", 0x0e },  { "6.5", 0x05 },
             { NULL, 0x00 }
       };
```

**The decisive comment, verbatim** `[VERIFIED: database.c @ a8efaedc, lines 121-129]`:

```c
/*
 * Parameters lookup tables.                                     // L122
 * The Vcc and Vpp settings are linked through the 'voltages'     // L123
 * field of the device database.                                 // L124
 * These are not raw DAC output values, but rather indices into   // L125
 * internal lookup tables defined in the firmware.                // L126
 * For bit-banging operations, we use separately defined          // L127
 * lookup tables.                                                 // L128
 */
```

> **CORRECTION for D-15.** `198-CONTEXT.md` cites this sentence as `database.c:123`. At the pinned
> sha, **L123 is `* The Vcc and Vpp settings are linked through the 'voltages'`**. The quoted
> sentence spans **L125-L126**. The quote itself is exact and the argument is unaffected — only the
> line number is wrong. § 9 must cite `database.c:125-126 @ a8efaedc`, and the planner should write
> that corrected citation into the task rather than copying CONTEXT's.

**Every D-01 / D-02 / D-15 arithmetic claim, re-derived:**

| CONTEXT claim | Re-measured this session | Verdict |
|---|---|---|
| `xg_vcc` is a strict, conflict-free superset of `tl866ii_vcc`, 6 shared indices, zero conflicts | `0x00`=5000, `0x01`=3300, `0x02`=4000, `0x03`=4500, `0x04`=5500, `0x05`=6500 in **both** tables | **HOLDS — zero conflicts** |
| plus exactly 9 more: `0x06`=1800, `0x07`=2500, `0x08`=3000, `0x09`=1200, `0x0A`=4750, `0x0B`=5250, `0x0C`=5750, `0x0D`=6000, `0x0E`=6250 | 15 total − 6 shared = **9**, values identical to the list | **HOLDS exactly** |
| `tl866a_vcc` conflicts on **4 of its 6** shared indices | `0x01` (4 vs 3.3), `0x02` (3.3 vs 4), `0x03` (6.5 vs 4.5), `0x05` (4.5 vs 6.5) conflict; `0x00` and `0x04` agree | **HOLDS — 4/6** |
| `tl866a_vpp` conflicts on **8 of 8** | `0x00` 12.5/12, `0x10` 16/9, `0x20` 21/9.5, `0x30` 13.5/10, `0x40` 10/11, `0x50` 14/11.5, `0x60` 18/12.5, `0x70` 17/13 | **HOLDS — 8/8** |
| `xg_vpp` supplies `0xF1`=25000 and `0xF2`=21000 | `{ "21", 0xf2 }, { "25", 0xf1 }` at L168 | **HOLDS** |
| D-15: `0x00` is 12 V on TL866-II, 12.5 V on TL866A | `tl866ii_vpp` `{ "12", 0x00 }`; `tl866a_vpp` `{ "12.5", 0x00 }` | **HOLDS** |
| D-15: `0x20` is 9.5 V and 21 V respectively | `tl866ii_vpp` `{ "9.5", 0x20 }`; `tl866a_vpp` `{ "21", 0x20 }` | **HOLDS** |

**Bonus, not in CONTEXT and worth stating in § 9:** `xg_vpp_voltages[]` is *also* a strict,
conflict-free superset of `tl866ii_vpp_voltages[]` — the 16 shared indices are byte-identical and
`xg` adds exactly `0xf1` and `0xf2`. So D-01's and D-02's "completion, not correction" argument has
the same shape on both axes, which strengthens the § 9 framing.

**Also present and deliberately NOT used** `[VERIFIED: database.c L172-L180, L192-L232]`:
`xg_pld_vpp_voltages[]` (identical to `tl866ii_vpp`, i.e. *without* `0xf1`/`0xf2`),
`t48_bb_vcc_voltages[]` and `t48_bb_vpp_voltages[]` (bit-banging tables on a completely different
index scale — `t48_bb_vpp` maps `0x00`→9 V where every other table maps `0x00`→12 V), and
`vcc_logic_voltages[]`. **None of these may be mixed in.** The `t48_bb_*` tables are a sharper
model-mixing hazard than `tl866a_*` because their indices are small integers that *look* like the
vcc nibble.

### F-2 — CORRECTION: the powerdown flags are NOT in the low nibble (HIGH)

`198-CONTEXT.md` § Canonical References states: *"`LAST_JEDEC_BIT_IS_POWERDOWN_ENABLE` and
`POWERDOWN_MODE_DISABLE` corroborate that the low nibble is flags."* **This is falsified.**

`[VERIFIED: minipro.h @ a8efaedc, lines 81-85, fetched and read this session]`

```c
/* voltage
 * for ATF20V10C and ATF16V8C variants
 * These flags are in voltages now (ex opts5) */
#define LAST_JEDEC_BIT_IS_POWERDOWN_ENABLE (0x1000)
#define POWERDOWN_MODE_DISABLE		   (0x2000)
#define ATF_IN_PAL_COMPAT_MODE		   (0x4000)
```

Those are **bits 12, 13 and 14** — inside the **vdd nibble** (`(voltages >> 12) & 0x0f`), not the low
nibble of the VPP byte. And the header's own comment scopes them *"for ATF20V10C and ATF16V8C
variants"* — Atmel PLD/GAL parts, which the generator's `type in {1, 4}` filter excludes entirely.

`[VERIFIED: database.c @ a8efaedc, lines 693-697]` — the unpack:

```c
	/* Unpack voltages */
	device->voltages.raw_voltages = voltages;
	device->voltages.vdd = (voltages >> 12) & 0x0f;
	device->voltages.vcc = (voltages >> 8) & 0x0f;
	device->voltages.vpp = voltages & 0xff;
```

Upstream reads the **full low byte** as `vpp`, with no mask, and applies the powerdown tests to the
same word at bits 12/13 (`database.c:678-682`).

**What this means for the planner, concretely:**

1. The in-source comment at `build_db.py:58-59` — *"bits 7-4 are the VPP index (these table keys),
   bits 3-0 are option flags"* — is an **inference with no upstream constant behind it**. There is no
   named low-nibble flag anywhere in `minipro.h`. It may well be right (the `0x00`/`0x01` and
   `0x70`/`0x71` pairings in F-3's census are suggestive), but § 9 must not present it as
   upstream-attested. State it as the generator's own working reading, corroborated by the pairing
   pattern, not as a cited fact.
2. Correspondingly, the vdd **nibble** is the position that genuinely carries named flag bits
   upstream — just only for PLD parts this generator never sees. That is a *second*, independent
   instance of D-15's core claim (the same bits mean different things depending on part family) and
   is worth a sentence in § 9. It also explains why a naive "the nibble is always a voltage index"
   reading is wrong in general while remaining correct for the filtered memory population.
3. It costs D-15 nothing. D-15's argument rests on the L125-L126 comment and on the 5.75–6.25 vs
   5.5/6.5 arithmetic, neither of which touches the powerdown constants. Only the CONTEXT
   *corroboration sentence* has to go.

### F-3 — The filtered population, the nibble census, and the 28-row predicate (HIGH)

Method, reproducible: parse the pinned `infoic.xml` with `ElementTree`, apply the generator's own
DIP-parallel filter verbatim (`24 <= pin_count <= 32`, not SMD, not serial, `type in {1, 4}`), before
the `KNOWN_PROTOCOLS` gate. Script kept at
`/tmp/claude-1000/-workspaces/8b44ccd0-f95d-420c-9c00-1969ab9bbcef/scratchpad/m/census.py`.

**Provenance of the XML** `[VERIFIED: sha256 computed this session]`: the prior session's scratchpad
copy at `…/9f02488d-…/scratchpad/infoic.xml` and a fresh download of the pinned URL **both** hash to
`cdd21319ae6cce2316ca2361a9fb82cba89b27b66bb78d58b01032a441106b8a` (17,861,009 bytes). CONTEXT's
"verify its sha against the pinned URL before relying on it" is discharged — it is the pinned file.

| Measurement | Value | CONTEXT claim | Verdict |
|---|---|---|---|
| Rows passing the DIP-parallel filter | **767** | 767 | HOLDS |
| Rows reaching the database | **746** (744 upstream + 2 supplement), 59 manufacturers | 746 | HOLDS |
| vcc nibble census | `0x0`×641, `0x1`×38, `0x2`×60, `0x4`×28 | same | HOLDS — all four mapped today |
| vdd nibble census | `0x0`×450, `0x1`×20, `0x4`×170, `0x5`×103, **`0x6`×12, `0xD`×5, `0xE`×7** | same | HOLDS — last three unmapped, silently 5000 |
| VPP low-byte census | `0x00`×453, `0x01`×113, `0x04`×2, `0x08`×13, `0x0A`×3, `0x0B`×1, `0x11`×1, `0x60`×7, `0x70`×136, `0x71`×9, `0x80`×1, `0xF0`×28 | `0x00`×453, `0x01`×113, `0x70`×136, `0x71`×9, `0xF0`×28 "and a tail" | HOLDS — **the tail is now fully enumerated** |
| Rows carrying `0xF1` or `0xF2` | **zero** | none | HOLDS — D-02/D-16's byte-identical proof stands |
| `vdd < vcc` under the completed table | **exactly 28** | exactly 28 | HOLDS |
| `vdd == vcc` / `vdd > vcc` | **373 / 366** (28+373+366 = 767) | 373 / 366 | HOLDS |
| The 28's split | **(5500, 1800)×12 and (5500, 3300)×16** | same | HOLDS |

**The generator's baseline is reproducible.** A harness that loads `tools/build_db.py`, substitutes
the local pinned XML for the network fetch, and redirects `OUTPUT_FILE` produces a database
**structurally identical to the shipped `firestarter/data/chip_database.json`**
(`identical to shipped: True`). Every simulation below is differential against that baseline, so the
numbers are the real regeneration numbers, not a model of them.

**Emitted state of the 28** `[VERIFIED: firestarter/data/chip_database.json, queried this session]`:
all 28 reach the database, all carry `programming.algorithm: 13` (promoted rows), all carry
`vpp_mv: 12000`, and **4 are `adapter-required`** — `MICROCHIP memory/28C04A`, `28C04AF`, `28C16A`,
`28C16AF`. The other 24 are `supported`. This confirms CONTEXT's deferred note about Phase 199.

### F-4 — The 16 sub-group-1 rows, enumerated and classified (HIGH measurement, MEDIUM class inference)

The full filtered-population list, with the raw `voltages` word and upstream `protocol_id`:

| # | Manufacturer | infoic `name` | `voltages` | upstream proto | Emitted `part_number` | `support_status` |
|---|---|---|---|---|---|---|
| 1 | AMD | `AM28C16A@DIP24` | `0x1400` | `0x0b` | `AM28C16A` | supported |
| 2 | AMD | `AM28C17A@DIP28,AM28C17A@SOIC28` | `0x1400` | `0x07` | `AM28C17A` | supported |
| 3 | MICROCHIP memory | `2804` | `0x1400` | `0x0b` | `2804` | supported |
| 4 | MICROCHIP memory | `2816` | `0x1400` | `0x0b` | `2816` | supported |
| 5 | MICROCHIP memory | `2817` | `0x1400` | `0x07` | `2817` | supported |
| 6 | MICROCHIP memory | `28C04A,28C04A@SOIC24` | `0x1400` | `0x0b` | `28C04A` | **adapter-required** |
| 7 | MICROCHIP memory | `28C04AF,28C04AF@SOIC24` | `0x1400` | `0x0b` | `28C04AF` | **adapter-required** |
| 8 | MICROCHIP memory | `28C16A,28C16A@SOIC24` | `0x1400` | `0x0b` | `28C16A` | **adapter-required** |
| 9 | MICROCHIP memory | `28C16AF,28C16AF@SOIC24` | `0x1400` | `0x0b` | `28C16AF` | **adapter-required** |
| 10 | MICROCHIP memory | `28C17A,28C17A@SOIC28` | `0x1400` | `0x07` | `28C17A` | supported |
| 11 | MICROCHIP memory | `28C17AF,28C17AF@SOIC28` | `0x1400` | `0x07` | `28C17AF` | supported |
| 12 | MICROCHIP memory | `28C256,28C256F` | `0x1400` | `0x07` | `28C256,28C256F` | supported |
| 13 | MICROCHIP memory | `28C64A,28C64A@SOIC28` | `0x1400` | `0x07` | `28C64A` | supported |
| 14 | MICROCHIP memory | `28C64AF,28C64AF@SOIC28` | `0x1400` | `0x07` | `28C64AF` | supported |
| 15 | MICROCHIP memory | `28C64B,28C64B@SOIC28` | `0x1400` | `0x07` | `28C64B` | supported |
| 16 | MICROCHIP memory | `28LV64A,28LV64A@SOIC28` | **`0x1401`** | `0x07` | `28LV64A` | supported |

`[VERIFIED: measured from infoic.xml @ a8efaedc via the DIP-parallel filter, and cross-read from the
live chip_database.json, this session]`

Notes the planner should carry into the disposition file:

- **The manufacturer string is literally `MICROCHIP memory`, with a space and lowercase `memory`.**
  Any override key or test literal must use it verbatim.
- **15 of 16 carry `voltages = 0x1400`; only `28LV64A` carries `0x1401`** — the low bit set, the same
  bit that distinguishes `0x70`/`0x71` in the VPP census. The one row whose part number says
  "low-voltage" is also the one row with a different voltage word. That is a real, measured signal
  and it cuts *for* the low-voltage reading of that single row.
- **2 of the 16 are AMD, not Microchip.** The todo's own text does say *"plus AMD's second-sourced
  equivalents"* `[VERIFIED: .planning/todos/pending/vcc-5500-high-margin-verify-rail-group.md, read
  this session]`, so D-13's paraphrase of the premise as purely "Microchip memory-family" is
  slightly narrower than what the todo says. Quote the todo accurately in the write-down.

**Which way the evidence cuts, per class:**

| Class | Rows | Evidence direction | What would close it |
|---|---|---|---|
| Microchip/AMD 28C-family 5 V parallel EEPROM (`2804`, `2816`, `2817`, `28C04A/AF`, `28C16A/AF`, `28C17A/AF`, `28C64A/AF/B`, `28C256/F`, `AM28C16A`, `AM28C17A`) | **15** | **Against `vdd` substitution.** These are the canonical 5 V 28C parts by part-number convention; a `vdd`-keyed rewrite would set them to 3.3 V. | The part's own datasheet (Microchip / AMD). **None is vendored.** |
| Low-voltage 28LV part (`28LV64A`) | **1** | **For a genuine 3.3 V rail** — the `LV` designator and the distinct `0x1401` word both point that way. But its `vcc_mv` of 5500 is *also* implausible for a 3.3 V part, so the row is internally odd either way. | Microchip's 28LV64A datasheet. **Not vendored.** |

**The decisive in-repo corroboration — and it is already shipped in code.** The comment the
`_VCC_MARGIN_RAIL_MV` rewrite carries says, verbatim
`[VERIFIED: firestarter_app/tools/build_db.py:783-786, read this session]`:

```
                # Do NOT widen this to a type, algorithm or relational key without
                # re-measuring: all three were tried and each drags in sixteen
                # genuinely-5V EEPROMs and sets them to 3.3V — worse than the
                # defect being fixed.
```

Phase 148 measured those sixteen and called them **"sixteen 5 V Microchip EEPROMs"**
`[VERIFIED: .planning/milestones/v1.32-phases/148-numeric-database-values-the-at28c-vcc-decode/148-DISCUSSION-LOG.md:44]`,
and its threat model records the same figure
`[VERIFIED: …/148-06-PLAN.md:458 — "over-broad margin-rail condition setting 16 genuinely-5 V EEPROMs to 3.3 V"]`.

**These are provably the same sixteen rows.** Measured against the live database, exactly **16** rows
carry the pair `(vcc_mv 5500, vdd_mv 3300)`, and they are the only rows a type- or algorithm-keyed
`vcc := vdd` rule could move to 3300 from 5500. So the repository contains a **direct internal
contradiction**: the pending todo calls these 16 *"genuinely-3.3V"*, while Phase 148's own decision
record and the shipped source comment call the same 16 *"genuinely-5V"*. D-13 sides with Phase 148,
and the part-class reading above agrees for 15 of the 16. **The write-down should name this
contradiction explicitly** — it is the single strongest piece of evidence available, and it costs
nothing to cite because both sides are already in the tree.

**The mandatory honesty limit, measured not assumed.** The repository vendors **13** PDFs
`[VERIFIED: ls datasheets/ + git ls-files datasheets/, run this session]`: `AT28C256.pdf`,
`LST62832I.pdf` *(untracked)*, `M27C1001.pdf`, `M27C512.pdf`, `MBM27128.pdf`, `MBM27C1000.pdf`,
`MBM27C1001.pdf`, `MBM27C4001.pdf`, `MX27C4000.pdf`, `SST39SF0x0A.pdf`, `W27C020.pdf`,
`W27C512.pdf`, `W27E257.pdf`.

**There is no Microchip datasheet and no AMD datasheet in the repository at all.** The two ST parts
present (`M27C1001`, `M27C512`) are UV EPROMs, not 28C EEPROMs. So **not one of the 16 rows has a
vendored datasheet**, and the disposition is a part-class argument plus an in-repo measurement, never
a datasheet reading. State that in exactly those terms; do not soften it.

**Sub-group 2 for contrast** — all 12, from the same measurement:

| Manufacturer | infoic `name` | `voltages` | Emitted `part_number` |
|---|---|---|---|
| EXEL | `XL2804A` | `0x6400` | `XL2804A` |
| EXEL | `XL2816A,XLE28C16A,XLS28C16A` | `0x6400` | `XL2816A,XLE28C16A,XLS28C16A` |
| EXEL | `XLE2865A,XLS2865A` | `0x6400` | `XLE2865A,XLS2865A` |
| EXEL | `XLE28C16B,XLE28C16B@SIOC24,XLS28C16B,XLS28C16B@SIOC24` | `0x6400` | `XLE28C16B,XLS28C16B` |
| EXEL | `XLE28C256,XLS28C256` | `0x6400` | `XLE28C256,XLS28C256` |
| EXEL | `XLE28C64A,XLS28C64A` | `0x6400` | `XLE28C64A,XLS28C64A` |
| EXEL | `XLE28C64B,XLE28C64B@SOIC28,XLS28C64B,XLS28C64B@SOIC28` | `0x6400` | `XLE28C64B,XLS28C64B` |
| SGS-THOMSON | `M28C64,M28C64@SOIC28,M28C64A,M28C64A@SOIC28` | `0x6400` | `M28C64,M28C64A` |
| SGS-THOMSON | `M28C64-xxW,M28C64-xxW@SOIC28` | **`0x6401`** | `M28C64-xxW` |
| ST | `M28C64,M28C64@SOIC28,M28C64A,M28C64A@SOIC28` | `0x6400` | `M28C64,M28C64A` |
| ST | `M28C64-xxW,M28C64-xxW@SOIC28` | **`0x6401`** | `M28C64-xxW` |
| ST | `M28LV64,M28LV64@SOIC28` | **`0x6401`** | `M28LV64` |

EXEL ×7, ST ×3, SGS-THOMSON ×2 — **exactly as D-04 states.** Note `ST/M28LV64` is an `LV` part held
at 5000 by D-04/D-05; the 12 `UNSOURCED` notes should not claim 5 V is *right* for it, only that 1800
is not credible and the datasheet would settle it.

### F-5 — The regeneration diff: exactly 15 rows, 17 field values (HIGH)

Two differential runs against the reproduced baseline.

**Run A — D-01 alone** (`VCC_VOLTAGES` completed to the 15-entry `xg` table, `_VCC_MARGIN_RAIL_MV`
re-derived from it, no override changes):

**24 rows change. `vdd_mv` only. No other field in any section moves. Row keys identical
(no adds, no drops).**

| Group | Rows | Change |
|---|---|---|
| vdd index `0x06` → 1800 | 12 | `EXEL/XL2804A`, `EXEL/XL2816A,…`, `EXEL/XLE2865A,…`, `EXEL/XLE28C16B,…`, `EXEL/XLE28C256,…`, `EXEL/XLE28C64A,…`, `EXEL/XLE28C64B,…`, `SGS-THOMSON/M28C64,M28C64A`, `SGS-THOMSON/M28C64-xxW`, `ST/M28C64,M28C64A`, `ST/M28C64-xxW`, `ST/M28LV64` — all `5000 → 1800` |
| vdd index `0x0D` → 6000 | 5 | `FUJITSU/MBM27C1000P,MBM27C1000`, `FUJITSU/MBM27C2000P,MBM27C2000`, `HITACHI/HN27C301AG,…`, `HITACHI/HN27C301G`, `MITSUBISHI/M5M27C101K` — all `5000 → 6000` |
| vdd index `0x0E` → 6250 | 7 | `FAIRCHILD/NMC27C16B,NMC27C16BQ`, `NSC/NMC27C16`, `NSC/NMC27C16B`, `NSC/NMC27C16Q`, `OKI/MSM27C1000`, `OKI/MSM27C2000`, `SGS-THOMSON/M27C1000` — all `5000 → 6250` |

This confirms CONTEXT's *"24 rows stop reaching a fabricated 5000 mV"* exactly, and confirms every
part name it lists for `0xD` and `0xE`.

**A measured negative worth recording:** the `_VCC_MARGIN_RAIL_MV` rewrite (`vcc := vdd` when
`vcc == 4000`, 60 rows at vcc index `0x02`) and the SRAM `vcc := vdd` rewrite both run *after* the
decode, so a `vdd_mv` change could in principle cascade into `vcc_mv`. **It does not** — zero
`vcc_mv` values move in Run A. None of the 24 rows sits on the 4000 rail or is SRAM-classified. The
planner can state "no `vcc_mv` moves in this phase" as measured fact.

**Run B — the full phase** (D-01 + D-05's 12 held entries + D-07/D-08's 2 VPP + D-09's 3 vdd):

**Net: exactly 15 rows change, 17 field values. Row keys identical. Only `electrical` moves — no
`support_status`, no `programming`, no `pinout`.**

| Row | `vpp_mv` | `vdd_mv` | Source |
|---|---|---|---|
| `FAIRCHILD/NMC27C16B,NMC27C16BQ` | — | 5000 → 6250 | D-01 (`0x0E`) |
| `FUJITSU/MBM27128` | — | **5500 → 6000** | D-09 override |
| `FUJITSU/MBM27C1000P,MBM27C1000` | — | 5000 → 6000 | D-01 (`0x0D`) |
| `FUJITSU/MBM27C1001` | **12000 → 12500** | **5500 → 6000** | D-08 + D-09 overrides |
| `FUJITSU/MBM27C2000P,MBM27C2000` | — | 5000 → 6000 | D-01 (`0x0D`) |
| `FUJITSU/MBM27C4001` | **12000 → 12500** | **5500 → 6000** | D-08 + D-09 overrides |
| `HITACHI/HN27C301AG,HN27C301AP,HN27C301AFP` | — | 5000 → 6000 | D-01 (`0x0D`) |
| `HITACHI/HN27C301G` | — | 5000 → 6000 | D-01 (`0x0D`) |
| `MITSUBISHI/M5M27C101K` | — | 5000 → 6000 | D-01 (`0x0D`) |
| `NSC/NMC27C16` | — | 5000 → 6250 | D-01 (`0x0E`) |
| `NSC/NMC27C16B` | — | 5000 → 6250 | D-01 (`0x0E`) |
| `NSC/NMC27C16Q` | — | 5000 → 6250 | D-01 (`0x0E`) |
| `OKI/MSM27C1000` | — | 5000 → 6250 | D-01 (`0x0E`) |
| `OKI/MSM27C2000` | — | 5000 → 6250 | D-01 (`0x0E`) |
| `SGS-THOMSON/M27C1000` | — | 5000 → 6250 | D-01 (`0x0E`) |

The 12 D-05 held rows contribute **zero** diff — D-04's byte-identical requirement is satisfied,
proven differentially rather than asserted.

**`746 rows in, 746 rows out, 0 added, 0 removed, 15 changed, 0 `support_status` changes.** That is
the line for `198-REGEN-DIFF.md`, on the `197-REGEN-DIFF.md` shape.

**Why `MBM27C1001` and `MBM27128` need a `vdd` override while the `0x0D` Fujitsu rows do not:**
`MBM27C1001`, `MBM27C4001` and `MBM27128` carry vdd index `0x04` (= 5500, already mapped), so their
6000 must come from an override. `MBM27C1000P` carries `0x0D`, so its 6000 comes free from the
completed table. Same manufacturer, same datasheet figure, two different mechanisms — the planner
must not try to unify them, and D-09's three rows are exactly the ones the table cannot reach.

### F-6 — The override file today, and what the phase does to it (HIGH)

`[VERIFIED: firestarter_app/tools/datasheet_overrides.json, read in full this session — 65 lines,
9 top-level keys]`

**Entry shape, verbatim (a datasheet-cited entry):**

```json
  "FUJITSU/MBM27C1001": {
    "datasheet": "datasheets/MBM27C1001.pdf",
    "note": "Page 9-90's AC CHARACTERISTICS table: tPW 0.475/0.50/0.525 ms, N 1 to 25, tOPW 1.4/1.5/39.4 ms, measured at VCC1 6V +/- 0.25V and VPP2 12.5V +/- 0.3V.",
    "fields": {
      "programming.pulse_duration_us": { "was": 100, "is": 500 }
    }
  },
```

**And an `UNSOURCED` entry, verbatim:**

```json
  "SGS-THOMSON/M2732A": {
    "datasheet": "UNSOURCED",
    "note": "Value 21000 is inherited verbatim from the deleted NMOS_TRUE_VPP_MV hardcode, which sourced this figure from an Intel datasheet for the Intel NMOS 2732A and applied it to this SGS-THOMSON row with no SGS-THOMSON-specific datasheet backing it. No SGS-THOMSON datasheet for this part is vendored in this repository. Closed by: SGS-THOMSON's own datasheet for M2732A, vendored and git-tracked under datasheets/.",
    "fields": {
      "electrical.vpp_mv": { "was": 18000, "is": 21000 }
    }
  },
```

Note the `UNSOURCED` house style: *"…Closed by: `<what would close it>`."* D-05 requires each of the
12 new notes to name what would close it — **this is the sentence form to copy.**

**The current 9 keys, in the sorted order the loader enforces:** `FUJITSU/MBM27128`,
`FUJITSU/MBM27C1000`, `FUJITSU/MBM27C1001`, `INTEL/M2716`, `INTEL/M2732`, `SGS-THOMSON/M2716`,
`SGS-THOMSON/M2732A`, `ST/M2716`, `ST/M2732A`. Six are `UNSOURCED`.

**Loader contract** `[VERIFIED: tools/build_db.py:356-447, read this session]`:

- Top-level keys must be in **ascending `sorted()` order**; the first out-of-order key raises and
  names its position (`_validate_datasheet_overrides_shape`, build_db.py:372-380).
- Each entry requires `datasheet` and `fields`; `fields` must be a non-empty object; each field value
  must be exactly a `{"was", "is"}` pair.
- `datasheet` must be either the exact token `"UNSOURCED"` **or** a **repository-relative, existing**
  path. The root is computed as `os.path.dirname(os.path.dirname(os.path.abspath(path)))` — i.e.
  derived from the override file's own location (build_db.py:381). An `UNSOURCED` entry with an empty
  `note` raises.
- `_OVERRIDABLE_DECODED_FIELDS` is exactly `("electrical.size_bytes", "electrical.pin_count",
  "electrical.vpp_mv", "electrical.vcc_mv", "electrical.vdd_mv", "programming.pulse_duration_us")`
  `[VERIFIED: build_db.py:356-363]`. All three fields this phase writes are in it.
- At apply time: unknown field path raises; two entries targeting one field on one row raises;
  `type(was) is not type(live)` raises; `was != live` raises (**stale override**); `was == is` raises
  (**no-op**). After the loop, `check_all_override_keys_consumed` raises on any key that matched no
  row (**dead entry**).

**Counts after this phase — and the number CONTEXT gives is a field count, not a key count:**

| | Today | After 198 | Delta |
|---|---|---|---|
| Top-level keys | **9** | **22** | +13 |
| `UNSOURCED` entries | **6** | **18** | +12 |
| Field-level `was`/`is` pairs added | — | — | **+17** (12 held vdd + 3 D-09 vdd + 2 D-08 vpp) |

CONTEXT says *"this phase adds up to 17 (2 VPP + 3 vdd + 12 held)"*. That is **17 field entries
spread over 13 new keys**, because `FUJITSU/MBM27C1001` and `FUJITSU/MBM27128` **already exist** and
gain fields rather than being created. Only `FUJITSU/MBM27C4001` is a new Fujitsu key. A planner
writing "add 17 entries" will produce a wrong count in every verify leg.

**`FUJITSU/MBM27C4001` is safe to create** `[VERIFIED: git ls-files datasheets/]`:
`datasheets/MBM27C4001.pdf` exists **and is git-tracked**, which
`test_every_datasheet_value_is_a_tracked_path_or_unsourced_with_note` requires. **Caution:** Phase
197 D-19 deliberately refused a `programming.pulse_duration_us` override on this exact row (its 100 µs
already matches its datasheet), and `test_mbm27c4001_noop_entry_raises` pins that refusal using a
synthetic fixture. The new entry must carry **only** `electrical.vpp_mv` and `electrical.vdd_mv`.
Adding a pulse field would be a no-op override and would raise at build time.

**The 12 held-row override keys — verified to resolve, one entry to one row.** These exact keys were
run through a full generation this session and all 12 were consumed, with no dead-key error, no
duplicate-target error, and zero net diff:

```
EXEL/XL2804A            EXEL/XL2816A            EXEL/XLE2865A
EXEL/XLE28C16B          EXEL/XLE28C256          EXEL/XLE28C64A
EXEL/XLE28C64B          SGS-THOMSON/M28C64      SGS-THOMSON/M28C64-xxW
ST/M28C64               ST/M28C64-xxW           ST/M28LV64
```

Each takes `"fields": {"electrical.vdd_mv": {"was": 1800, "is": 5000}}`. `SGS-THOMSON/M28C64` and
`ST/M28C64` are distinct keys for distinct rows with the same part number under different
manufacturers — that is correct and the loader handles it.

**999.72 does not bite this phase.** Backlog entry 999.72 records that `apply_datasheet_override`
runs *after* `resolve_pinout_key`/`classify`, so `electrical.size_bytes` and `electrical.pin_count`
half-apply `[VERIFIED: .planning/ROADMAP.md:8024-8052]`. It explicitly warns that *"phases 198, 199
and 200 all write into this same override file"*. Phase 198 writes only `vpp_mv`, `vcc_mv`(none) and
`vdd_mv` — three of the four **fully-hoisted** fields — so it is unaffected. Worth one sentence in the
plan so a reviewer does not flag it.

### F-7 — The wire-dict delta layer IS required, and needs exactly 2 entries (HIGH)

**Measured, not inferred.** With the phase's regenerated database in place, the wire-dict tests were
run under Python 3.11:

```
FAILED tests/test_wire_dict_equivalence.py::test_live_capture_matches_golden_plus_the_149_and_153_and_182_and_194_and_197_deltas
FAILED tests/test_wire_dict_equivalence.py::test_exactly_84_records_change_flags_and_no_other_field_moves
2 failed, 7 passed
```

The failure names the delta precisely: **86 records change where 84 are expected**, and the two extra
keys are exactly `FUJITSU|MBM27C1001|7` and `FUJITSU|MBM27C4001|12`.

**`vpp_mv` is one of the nine wire keys** `[VERIFIED: tests/test_wire_dict_equivalence.py:140-150]`:
`algorithm`, `bus-config`, `chip-id`, `flags`, `memory-size`, `page-size`, `pin-count`, `pulse-delay`,
`vpp_mv`. **The 12 `vdd_mv` movements and the 3 D-09 `vdd_mv` movements contribute zero wire deltas**
— confirmed by the fact that only 2 extra records appear, not 15. CONTEXT's "`vcc`/`vdd` are inert on
the wire" prediction is therefore measured true for this phase's specific changes.
`test_vcc_and_vpp_volts_never_cross_the_wire` stays green throughout.

**The 198 layer, then, is:**

`tests/golden/wire_dict_expected_deltas_198.json`
```json
{
  "deltas": {
    "FUJITSU|MBM27C1001|7":  { "vpp_mv": 12500 },
    "FUJITSU|MBM27C4001|12": { "vpp_mv": 12500 }
  },
  "meta": { "decision": "...", "honesty": "...", "how_to_update": "...", "phase": "...", "provenance": "..." }
}
```

The `meta` block is not optional decoration — the 197 layer carries five keys (`decision`, `honesty`,
`how_to_update`, `phase`, `provenance`) and the composition test's docstring calls them the
"anti-laundering assertions"
`[VERIFIED: tests/golden/wire_dict_expected_deltas_197.json, read in full this session]`.

**Key-shape hazard.** The record key is `MANUFACTURER|part_number|<positional index within that
manufacturer's row list>`. The 197 layer's own `provenance` field warns it *"would silently rot if any
row is ever added or reordered"*. This phase adds and removes **zero** rows (measured: `keys equal:
True` in both runs), so the indices `7` and `12` are stable. **Generate the layer programmatically
from the live capture; do not transcribe it by hand** — that is the 197 layer's stated rule.

**Shared-key note the planner must check:** `FUJITSU|MBM27C1001|7` appears in **both** the 197 layer
(carrying `pulse-delay`) and the new 198 layer (carrying `vpp_mv`). The composition test asserts
**field-disjointness on shared keys**
`[VERIFIED: tests/test_wire_dict_equivalence.py:352-378]`. `pulse-delay` ∩ `vpp_mv` = ∅, so the pair
passes — but the new `("198", deltas_198, "197", deltas_197)` tuple **must be added to `layer_pairs`**
alongside `198×149`, `198×153`, `198×182` and `198×194`, or the disjointness is never checked for the
new layer.

**Every site in `tests/test_wire_dict_equivalence.py` that must change** (612 lines total):

| Site | Lines | Change |
|---|---|---|
| Module docstring, items 1-9 | ~29-118 | Describe the 198 layer and the new non-vacuity test |
| `_DELTAS_198` constant | after :133 | `_HERE / "golden" / "wire_dict_expected_deltas_198.json"` |
| `test_live_capture_matches_…` — load, missing-key check, value check, exact-count assert | ~222-350 | Add a `deltas_198` block mirroring the `deltas_197` block at :333-350; assert `len(deltas_198) == 2` |
| `layer_pairs` | 352-362 | Add the four `198×…` tuples |
| Composition `for` loop | ~380-390 | Add `for key, delta_wire in deltas_198.items(): expected[key].update(delta_wire)` |
| Final assertion message | ~392-408 | Mention the 2 named Phase 198 deltas |
| `test_exactly_84_records_change_flags_and_no_other_field_moves` | 460+, assert at **:500** | **`84` → `86`** — and rename the test, since its name states the count |
| New `test_the_198_delta_layer_is_capable_of_failing` | after :612 | Mirror `test_the_197_delta_layer_is_capable_of_failing` (:576-612), mutating `vpp_mv` instead of `pulse-delay` |

The 197 non-vacuity test is the exact template: deep-copy the golden, apply all layers, mutate
`next(iter(sorted(deltas_198)))`'s `vpp_mv`, and assert
`diff == f"changed={{'{some_key}': ['vpp_mv']}}"`.

### F-8 — The snapshot re-record is required, and is exactly 2 lines (HIGH)

`tests/test_characterization.py::test_list` fails with the regenerated database — *"1 snapshot failed.
31 snapshots passed."* **Both Fujitsu rows appear in the snapshot.**

Running `--snapshot-update` and measuring with `--numstat` gives **`2	2`** —
two lines added, two removed, in `tests/__snapshots__/test_characterization.ambr`:

```diff
   | MBM27C1000P,MBM27C1…| FUJITSU          |   32 | 0x04E5     | UV-EPROM    | 12.5v|
-  | MBM27C1001          | FUJITSU          |   32 | 0x04E5     | UV-EPROM    | 12.0v|
+  | MBM27C1001          | FUJITSU          |   32 | 0x04E5     | UV-EPROM    | 12.5v|
   | MBM27C128P          | FUJITSU          |   28 |            | UV-EPROM    | 18.0v|
   | MBM27C2000P,MBM27C2…| FUJITSU          |   32 | 0x040B     | UV-EPROM    | 12.5v|
   | MBM27C2001          | FUJITSU          |   32 |            | UV-EPROM    | 12.0v|
   | MBM27C256A          | FUJITSU          |   28 |            | UV-EPROM    | 12.0v|
-  | MBM27C4001          | FUJITSU          |   32 | 0x04F4     | UV-EPROM    | 12.0v|
+  | MBM27C4001          | FUJITSU          |   32 | 0x04F4     | UV-EPROM    | 12.5v|
```

`[VERIFIED: measured this session by swapping the regenerated database in, running
--snapshot-update, capturing git diff --numstat, then restoring with git checkout --]`

The exact command, matching the 197-04 precedent:

```bash
cd /workspaces/firestarter_app && \
  .venv/ci-replica/bin/python -m pytest "tests/test_characterization.py::test_list" \
    -o addopts="" -q -p no:randomly --snapshot-update
git diff --numstat tests/__snapshots__/test_characterization.ambr   # must print exactly: 2	2
```

**`--numstat` returning `2	2` is a usable verify leg** and is far stronger than "the snapshot was
updated". Make it an acceptance criterion.

Two bonuses visible in that diff, both usable as evidence in the write-down: `MBM27C2001` sits at
`12.0v` two lines below the corrected `MBM27C4001` — D-08's deliberate family inconsistency is
**visible in a shipped test fixture**, which is a good place to point at. And `MBM27C1000P` /
`MBM27C2000P` already read `12.5v`, corroborating D-07's "the sibling already carries 12500 via VPP
index `0x60`".

### F-9 — The full test blast radius: 5 tests, 3 files (HIGH)

The full suite was run under **Python 3.11.16** (`.venv/ci-replica/bin/python`) against the
regenerated database:

```
3 failed, 2062 passed in 175.75s
```

Then the override file was swapped in separately, revealing **two more**:

```
FAILED tests/test_datasheet_overrides.py::TestShippedOverrideFileContract::test_unsourced_count_is_pinned_exactly
FAILED tests/test_datasheet_overrides.py::TestShippedOverrideFileContract::test_total_entry_count_is_pinned_exactly
2 failed, 18 passed
```

**The complete list — five tests, three files:**

| # | File | Test | Why it moves | Fix | Command |
|---|---|---|---|---|---|
| 1 | `tests/test_characterization.py` | `test_list` | `vpp_str` renders `12.0v` → `12.5v` on 2 Fujitsu rows | `--snapshot-update`; assert `--numstat` = `2	2` | `pytest tests/test_characterization.py::test_list -o addopts="" -q` |
| 2 | `tests/test_wire_dict_equivalence.py` | `test_live_capture_matches_golden_plus_the_149_…_and_197_deltas` | 2 new `vpp_mv` wire deltas | Add the 198 layer + wire it in (F-7) | `pytest tests/test_wire_dict_equivalence.py -o addopts="" -q` |
| 3 | `tests/test_wire_dict_equivalence.py` | `test_exactly_84_records_change_flags_and_no_other_field_moves` | 86 records now change | `84` → `86` at **:500**; rename the test | same |
| 4 | `tests/test_datasheet_overrides.py` | `TestShippedOverrideFileContract::test_unsourced_count_is_pinned_exactly` | `_EXPECTED_UNSOURCED_COUNT = 6` at **:335** | `6` → `18` | `pytest tests/test_datasheet_overrides.py -o addopts="" -q` |
| 5 | `tests/test_datasheet_overrides.py` | `TestShippedOverrideFileContract::test_total_entry_count_is_pinned_exactly` | `_EXPECTED_ENTRY_COUNT = 9` at **:336** | `9` → `22` | same |

**Tests 4 and 5 are the trap.** They read `tools/datasheet_overrides.json` directly, so they stay
green if you only regenerate the database — which is exactly what a "run the suite after regen" check
does if the override file edit lands in a later task. **Plan the override-file edit and these two
literals in the same task**, or the phase reports green on a state that does not exist.

**Measured-green, i.e. explicitly NOT in the blast radius** — each of these was a plausible candidate
and each passed:

- **`tests/test_build_db_constant_census.py`** (the OVR-06 gate). It `ast.parse`s `tools/build_db.py`
  and matches **string** constants against a part-number shape
  `[VERIFIED: tests/golden/build_db_part_specific_constants.json, read this session]`. D-01/D-02 add
  **integer** dict keys and values only, so nothing surfaces. The frozen golden holds exactly one
  entry (`"DIP28"`) and `test_golden_length_is_exact` pins that. **Standing caution:** if the planner
  chooses to ship D-06's predicate as a build-time assertion whose message embeds a part number, or
  introduces any new part-number-shaped *string* literal, this gate trips and the golden needs a new
  entry with a recorded reason.
- `tests/test_vcc_margin_rail.py` — the 4000-rail rewrite is untouched (Run A measured zero `vcc_mv`
  movement).
- `tests/test_chip_database_field_inventory.py` — the 14-field set is unchanged; no provenance field
  is added to rows.
- `tests/test_pulse_us_override.py`, `tests/test_extra_chips_supplement.py`,
  `tests/test_build_db_inclusion.py`, `tests/test_eprom_info.py`, `tests/test_sdp_db_invariant.py`,
  `tests/test_blast_radius_invariance.py` — all green.
- The other 18 tests in `tests/test_datasheet_overrides.py`, including
  `test_mbm27c4001_noop_entry_raises` and
  `test_every_datasheet_value_is_a_tracked_path_or_unsourced_with_note`.

**Target green state: 2067 passed** (2062 + the 3 fixed + 2 more from the override file, assuming the
new non-vacuity test adds 1 → treat the exact end count as a measurement to take, not a number to
assert blind). Today's baseline on this branch is 2065.

**Python floor.** `.venv/ci-replica/bin/python` is **Python 3.11.16** with the app installed editable
`[VERIFIED: --version and import check, run this session]`. `.venv/bin/python` is a symlink to
`/bin/python` and is **not** 3.11. The devcontainer default `python3` is **3.12.14**. Use
`.venv/ci-replica/bin/python` for every suite run in a verify leg.

**`-o addopts=""` is required to see the count line** — the project's `addopts` is `-ra -q` and
doubling `-q` suppresses it.

### F-10 — Todo close and backlog-entry mechanics (HIGH)

**The todo close is a plain `git mv`, with no frontmatter edit.** The Phase 197 precedent
`[VERIFIED: git log --diff-filter=R --name-status, run this session]`:

```
59481654 docs(197-07): file three backlog entries (999.69-71), close derive-away-max-27c020-size-hardcode todo
R100	.planning/todos/pending/derive-away-max-27c020-size-hardcode.md	.planning/todos/completed/derive-away-max-27c020-size-hardcode.md
```

**`R100` = 100% similarity = pure rename, zero content change.** No GSD verb is involved; no
frontmatter field is touched. Across 20 such commits in history the pattern is consistent (some show
R061–R089, i.e. a rename plus an edit, but the 197 precedent D-12 names is R100). The target file
already carries `resolves_phase: 198` in its frontmatter
`[VERIFIED: .planning/todos/pending/vcc-5500-high-margin-verify-rail-group.md, read this session]`,
so nothing needs changing.

```bash
git mv .planning/todos/pending/vcc-5500-high-margin-verify-rail-group.md \
       .planning/todos/completed/vcc-5500-high-margin-verify-rail-group.md
```

**Hazard from the 197 record, worth writing into the task:** a `git mv` run against an
**uncommitted** edit stages the pre-edit blob and silently produces a 0-diff rename. The 197 executor
hit this. Commit any content edit *before* the `git mv`, and check `git diff --stat` rather than
trusting the commit summary.

**Backlog entries go into `.planning/ROADMAP.md`, and the executor must NOT write them.** The 197
precedent is explicit: *"The executor drafted and verified them, then REVERTED its own edit
(`d883d9f6`) to respect single-writer; orchestrator confirmed ROADMAP byte-identical to its
pre-dispatch snapshot before applying"* `[VERIFIED: .planning/ROADMAP.md:255]`. The verify legs used
were: N entries present, `### Phase ` heading count increased by exactly N with zero lost, and all
required tokens found.

**Entry shape** — the closest analogue is 999.71 (`[VERIFIED: .planning/ROADMAP.md:8003-8026]`), which
is itself about `UNSOURCED` override entries:

```markdown
### Phase 999.NN: <one-line finding> (BACKLOG — filed <date> during v1.40 Phase 198, from `<artifact>`)

**Goal:** <what closing it would achieve>

**The N entries** / **MEASURED**: <the measured facts, with counts>

**What would close each:** <per-class, naming the specific datasheet needed>

**Consequence of leaving them:** <honest statement of the residue>
```

The successor entry D-12 requires must carry: 28 rows still reporting 5.5 V; 12 of them held at an
unsourced 5000 by D-04/D-05; closable only at one datasheet per row; and that **no Microchip or AMD
datasheet is vendored**, so 16 of the 28 have no route to closure without new PDFs.

**Where the per-row disposition file lands (discretion).** Two live precedents:
`.planning/phases/197-…/197-PULSE-INVENTORY.md` (in the phase directory) and
`.planning/notes/197-at28c-guard-evidence-for-phase-199.md` (in notes, because Phase 199 consumes it).
Since sub-group 1's disposition is **consumed by the successor backlog entry and by VOLT-F1**, not by
a named next phase, the phase directory is the better fit —
`198-VOLT03-DISPOSITION.md`, on the shared section shape:

```
# <Title>
## Reproducible method          ← the exact script/command, runnable
## <census / the N-row table>   ← every row, no elision
## Per-row disposition          ← every row, with a reason
## Honesty limit                ← the named limit
```

`[VERIFIED: heading survey of 197-PULSE-INVENTORY.md, 197-REGEN-DIFF.md and
197-at28c-guard-evidence-for-phase-199.md, run this session]`

### F-11 — gh#66 and the consolidated held-pending list (HIGH)

`[VERIFIED: gh issue view 66 --repo henols/firestarter, run this session]`

```json
{"number":66,"state":"OPEN","title":"[dev test] MBM27C4001 — FAIL (9b5ff85b0649)",
 "labels":["dev-test","cause:firmware","cause:database"],
 "ncomments":6,"authors":["henols","dim20","henols","dim20","dim20","henols"]}
```

OPEN, 6 comments, alternating maintainer and reporter — matching CONTEXT exactly. The
`cause:database` label is already applied, so this phase's corrections land on an issue already
triaged to this cause.

**The template D-18 points at** `[VERIFIED: 197-GH70-ANSWER.md:113-143, read in full this session]`.
`197-GH70-ANSWER.md` has the heading structure `# gh#70 Answer — Draft` → `## Status` →
`## Internal provenance (project bookkeeping only — do not post)` → `## Comment Body` →
`## Held-pending deferral (internal — do not post)`. The deferral section has five bolded bullets —
**What is held**, **Why**, **What releases the hold**, **Exactly what to do at that point** (a
numbered 4-step list), **Requirement status** — and the four steps are:

1. Replace the `**Version:**` line with the real published version.
2. Re-run the no-over-claim and no-attribution checks against the final Comment Body text only.
3. Post **only** the Comment Body, verbatim, with
   `gh issue comment <N> --repo henols/firestarter --body-file`. Never paste the header, Status,
   Internal provenance or Held-pending sections.
4. Record the returned comment URL back into the file and mark the requirement complete in
   `.planning/REQUIREMENTS.md`.

**D-18 requires editing `197-GH70-ANSWER.md`** so its deferral section names both issues. That is
legitimate: the "historical-by-intent, do not edit" rule (D-14) applies to **archived** records under
`.planning/milestones/` — such as `148-DB-DIFF.md` — not to the current milestone's live phase
directory. The planner should state that distinction in the task so an executor does not refuse the
edit by misreading D-14.

The new `198-GH66-ANSWER.md` should mirror the same five-section shape, and VOLT-04 must be left
`Pending` in `.planning/REQUIREMENTS.md:149` (D-17), exactly as PULSE-04 is.

### F-12 — The generator's edit sites, and every comment sitting on them (HIGH)

All line numbers `[VERIFIED: firestarter_app/tools/build_db.py @ 0372cc6, read this session]`.
The file is 848 lines.

**Site 1 — `VPP_MV`, lines 57-79.** The comment block is lines **57-61**:

```python
# Key on (voltages & 0xF0), NOT (voltages & 0xFF). The low byte packs two      # 57
# fields: bits 7-4 are the VPP index (these table keys), bits 3-0 are option   # 58
# flags. Masking the full byte yields Unknown/0 mV whenever the option bits are# 59
# set — e.g. SST27VF512 has voltages=0x0001, and 0x01 is not a key here.       # 60
# [minipro database.c + tl866a.c, tl866ii_vpp_voltages[]]                      # 61
VPP_MV = {                                                                      # 62
    0x00: 12000, 0x10: 9000, 0x20: 9500, 0x30: 10000, 0x40: 11000,
    0x50: 11500, 0x60: 12500, 0x70: 13000, 0x80: 13500, 0x90: 14000,
    0xA0: 14500, 0xB0: 15500, 0xC0: 16000, 0xD0: 16500, 0xE0: 17000,
    0xF0: 18000,
}                                                                               # 79
```

Three problems, all on lines D-02 must edit:

- Line 57 states the **opposite** of what D-02 does. It becomes actively false.
- Line 58's "bits 3-0 are option flags" has **no upstream constant behind it** (F-2).
- Line 61 is a provenance marker that (a) is **not** in `[VERIFIED: …]` form, (b) carries **no sha**,
  and (c) names `tl866a.c` — a file whose VPP table **conflicts with this one on 8 of 8 indices**
  (F-1). The table's values are `tl866ii_vpp_voltages[]`'s.

> **CORRECTION for CONTEXT § Established Patterns.** It claims *"Both `VPP_MV` and `VCC_VOLTAGES`
> carry a `[VERIFIED: minipro … @ a8efaedc]` provenance marker naming the upstream file and sha."*
> **False for `VPP_MV`** — its marker has no `VERIFIED:` token and no sha. Only `VCC_VOLTAGES` has
> the versioned form.

**Site 2 — line 674**, the mask expression, verbatim:

```python
                _d_vpp_mv = VPP_MV.get(voltages & 0xF0, 0)
```
(adjacent: `_d_vcc_mv = VCC_VOLTAGES.get((voltages >> 8) & 0x0F, 5000)` at **675**,
`_d_vdd_mv = VCC_VOLTAGES.get((voltages >> 12) & 0x0F, 5000)` at **676**.)

**Site 3 — `VCC_VOLTAGES`, lines 116-124, with two inline comments inside the table:**

```python
# [VERIFIED: minipro database.c#L130-L135 @ a8efaedc — tl866ii_vcc_voltages[]]  # 116
VCC_VOLTAGES = {                                                                 # 117
    0x00: 5000,
    0x01: 3300,
    0x02: 4000,  # BUG-1 fix: was missing from v1.12                             # 120
    0x03: 4500,  # BUG-1 fix: was missing from v1.12                             # 121
    0x04: 5500,
    0x05: 6500,
}                                                                                # 124
```

> **FALSIFIED CITATION, and it is duplicated.** `database.c#L130-L135 @ a8efaedc` is
> **`tl866a_vpp_voltages[]`** (L130-L133) plus the start of `tl866a_vcc_voltages[]` — *not*
> `tl866ii_vcc_voltages[]`, which lives at **L154-L159** (F-1). The marker is wrong by ~24 lines and
> names the wrong table, and the **identical wrong string is repeated at line 126** on the
> `_VCC_MARGIN_RAIL_MV` block. D-01 requires extending this very marker to name `xg_vcc_voltages[]`
> (**L182-L190**), so the correction is unavoidable — do it deliberately rather than propagating the
> error. Suggested replacement, subject to C-1 (this is an existing comment being *corrected*, not a
> new one being added — it must not grow a line):
> `# [VERIFIED: minipro database.c#L182-L190 @ a8efaedc — xg_vcc_voltages[]]`

The two `# BUG-1 fix` inline comments at 120-121 are **bug provenance that exists nowhere else** —
the same class of content `.planning/notes/197-build-db-comment-provenance-rescued.md` was written to
rescue. If reformatting the table dislodges them, relocate the fact to § 9 first.

**Site 4 — `_VCC_MARGIN_RAIL_MV`, lines 126-131:**

```python
# [VERIFIED: minipro database.c#L130-L135 @ a8efaedc — tl866ii_vcc_voltages[]]  # 126  ← same false citation
# VCC_VOLTAGES index 0x02 is the TL866's low-margin VCC *verify* rail, not an   # 127
# operating supply — no part here has a 4.0 V nominal VCC. Any chip whose       # 128
# decoded vcc_mv lands on this rail is being misreported. Written as a lookup   # 129
# rather than a literal so it cannot drift from the table.                      # 130
_VCC_MARGIN_RAIL_MV = VCC_VOLTAGES[0x02]                                         # 131
```

`VCC_VOLTAGES[0x02]` still resolves to 4000 under the completed table (the `xg` table agrees on
`0x02`), so **line 131 needs no change**. But it sits immediately below the table being edited — a
reformat that shifts indentation makes 127-130 reappear as `+` lines and trips the C-2 pre-commit
check.

**Site 5 — the value-keyed rewrite, lines 778-790** (not itself edited, but load-bearing):

```python
                # Same category error as the block above, but keyed on the      # 778
                # decoded VALUE rather than the type: any chip landing on the   # 779
                # TL866's low-margin verify rail is reporting it as an operating# 780
                # supply. Substituting vdd can only ever raise the figure.      # 781
                #                                                               # 782
                # Do NOT widen this to a type, algorithm or relational key without # 783
                # re-measuring: all three were tried and each drags in sixteen  # 784
                # genuinely-5V EEPROMs and sets them to 3.3V — worse than the   # 785
                # defect being fixed.                                           # 786
                if chip_entry["electrical"]["vcc_mv"] == _VCC_MARGIN_RAIL_MV:   # 787
```

This is D-06's shape reference **and** F-4's key evidence. Do not edit it; cite it.

**The SRAM rewrite** sits immediately above at lines **766-776** with its own 7-line comment.

**The 197-02 precedent, and why this matters** `[VERIFIED:
.planning/notes/197-build-db-comment-provenance-rescued.md, read this session]`: plan 197-02
collapsed a nested `if` in this file; **dedenting made 18 lines of pre-existing, unchanged comments
reappear as `+` lines in the staged diff**, tripping the no-new-comments check. The executor deleted
them whole, losing two decode bug-fix records and one external-source anchor, and the commit message
did not mention the deletion. The note also records that *"the executor's hand-back reported 'three
pre-existing explanatory comments'. The measured figure is 18 lines across eight blocks"* — i.e.
**treat comment-deletion counts in a SUMMARY as a claim to verify, not to accept.**

**Task wording the planner should use:** *"Edit `VCC_VOLTAGES`/`VPP_MV` in place, adding dict entries
only. Do not reformat, re-indent, or reflow the surrounding blocks. Add no comment line. If a comment
is deleted or dislodged, relocate its content to `tools/DECODE-NOTES.md` § 9 in the same commit, read
the remainder of the block, and confirm it still parses with every pronoun keeping an antecedent
(CLAUDE.md C-3). Before committing, run the pathspec-scoped pre-commit check and confirm it prints
nothing."*

### F-13 — `DECODE-NOTES.md` § 8 and § 6, as the § 9 template (HIGH)

`[VERIFIED: firestarter_app/tools/DECODE-NOTES.md, 367 lines, headings surveyed and §§ 6 and 8 read
in full this session]`

Section map: `§ 0` Pinned upstream reproducibility (:18) · `§ 1` LOW byte (:46) · `§ 2` HIGH byte
(:100) with `§ 2.1`–`§ 2.3` · `§ 3` build_db.py provenance decision (:195) · `§ 4` X88C64 fix
rationale (:206) · `§ 5` FM1608 identity (:230) · `§ 6` Honest gaps (:257) · `§ 7` Sources (:286) ·
`§ 8` `pulse_delay` unit finding (:302, runs to :367). **§ 9 appends after :367**, and § 7 "Sources"
sits *before* § 8 — so § 8 carries its own trailing `Sources:` paragraph rather than extending § 7.
§ 9 must do the same.

**§ 8's heading form:** `## 8. \`pulse_delay\` unit finding (PULSE-01, Phase 197 — the decode rule survives)`
— number, backticked field, requirement ID, phase number, and a **verdict clause in the heading
itself**. § 9's analogue: `## 9. The voltage word's two nibbles and VPP byte (VOLT-01, Phase 198 — …)`.

**§ 8's internal shape**, each a bolded lead sentence followed by prose:

1. `**Verdict: … is CONFIRMED**` — the claim, first line, before any evidence.
2. `**What \`interpret_timing\` does today** \`[VERIFIED: build_db.py:339-380]\`:` — current behaviour
   with an inline file:line provenance tag.
3. `**The positive confirmation.**` — one named part, its datasheet, page number, and the exact
   figures, framed as *"a positive match, not merely an absence of contradiction"*.
4. `**The falsification of "per-part value".**` — the rejected hypothesis named in quotes, killed
   with counts (675 entries, 462 sharing one value, 68.4%).
5. `**No uniform multiplier is coherent.**` — an arithmetic argument, not an appeal.
6. `**What \`pulse_duration_us\` means on the wire** \`[VERIFIED: <three firmware paths>]\`` — the
   consumer's semantics.
7. `**Empty-input behaviour is fail-closed … and is provably dead against the pinned upstream.**` —
   the edge case, naming *"this branch's only coverage"*.
8. `Sources: <phase research doc> § "<section>"; <inventory doc>; <override entries>.`

**Mapping § 8's slots onto § 9's D-15 content** (the planner can specify this concretely):

| § 8 slot | § 9 content |
|---|---|
| Verdict | The nibbles and VPP byte select a **programmer rail index, not a chip requirement** |
| What the code does today | `_d_vpp_mv` / `_d_vcc_mv` / `_d_vdd_mv` at `build_db.py:674-676`, with the corrected `xg_*` provenance |
| Positive confirmation | The three Fujitsu datasheets all stating 6.0 V ± 0.25 V where the index selects 5.5 V — **neither 5.5 nor 6.5 is inside 5.75–6.25**, and those are the TL866-II's only two nearby rails |
| Falsification of "these are chip requirements" | Model-dependence: `0x00` = 12 V (II) vs 12.5 V (A); `0x20` = 9.5 V vs 21 V; upstream's own L125-L126 comment |
| Arithmetic argument | The 5.75–6.25 vs 5.5/6.5 gap; and the D-16 saturation pattern — 28 rows pinned at `0xF0` = 18 V, the model maximum, including `MBM27128` which gh#71 measured as needing 21 V |
| Edge case / dead branch | `0xF1`/`0xF2` exist in `xg_vpp_voltages[]` but **no filtered row carries them**; D-03 means nothing mechanical reports a future unmapped index |
| Sources | `198-RESEARCH.md`, `198-VOLT03-DISPOSITION.md`, `198-REGEN-DIFF.md`, the new override entries, `database.c:125-126 @ a8efaedc` |

**§ 6 "Honest gaps" phrasing pattern** — each limit is a **bolded assertive clause that names the
thing and its status**, not a hedge:

- `- **No high-byte value is a classification gap.**` → then *why*, then *"There is therefore **no
  undecoded high-byte value left guessed**."*
- `- **2516 / 2532 are NOT a decode gap.**` → then the distinction (*"absent from `infoic.xml`
  entirely — a categorically different concern from a chip whose fields we cannot decode"*), then an
  explicit cross-reference naming what owns it (*"**Cross-reference: Plan 86-04 owns 2516/2532.**"*),
  then a later `**[Plan 86-04 IMPLEMENTED]**` update marker.

**D-15's three mandatory limits, in that voice:**

- **The datasheet corroboration is n = 3, and all three are Fujitsu.** `MBM27C4001`, `MBM27C1001`,
  `MBM27128` — no second manufacturer corroborates the rail-index reading from a datasheet.
- **No claim is made about the 167 rows at vdd index `0x4` this phase does not reach.** They carry
  5500 where the same arithmetic would suggest 6000; **Phase 200 owns surfacing them**, one datasheet
  per row under Phase 197's D-02. *(Cross-reference form, per § 6.)*
- **This finding does not assert that any particular row's value is correct.** It says what the field
  *is*, not that any instance of it is right.

Add a fourth, earned by this research: **the low nibble's "option flags" reading is the generator's
own, not upstream's** (F-2) — no `minipro.h` constant names it, and the named powerdown bits are at
12/13, scoped to ATF PLD parts the filter excludes.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Holding a per-part value that contradicts the decode | A dict, an `if`, or a value literal in `build_db.py` | `tools/datasheet_overrides.json` entries | Milestone D-1 forbids part-specific hardcodes; OVR-06's census gate would surface a string one. The mechanism ships with 5 fail-closed legs and 20 tests. |
| Asserting the 12 held rows didn't move | A hand-written expected-value list | The differential regeneration diff (`was: 1800, is: 5000` + byte-identical output) | The loader already asserts `was` against the live decode and raises on drift; a separate list would rot silently. |
| Recording the wire-value change | Re-capturing `wire_dict_baseline.json` | A new `wire_dict_expected_deltas_198.json` layer | The golden is never re-baselined — that is the anti-laundering discipline the 197 layer's `meta.decision` states explicitly. |
| Regenerating the snapshot | A blanket `--snapshot-update` across all 32 snapshots | Targeted `pytest tests/test_characterization.py::test_list --snapshot-update`, then `--numstat` = `2	2` | The 197-04 precedent. A blanket update hides unrelated drift. |
| Explaining a decode in code | Any `#` comment | `tools/DECODE-NOTES.md` § 9 | CLAUDE.md hard rule, not overridable. |
| Closing the todo | A GSD verb or a frontmatter edit | `git mv pending/ → completed/` | The 197 precedent is a pure `R100` rename. |
| Writing the backlog entry | An executor edit to `ROADMAP.md` | Executor drafts + verifies, orchestrator applies | Single-writer discipline; `roadmap.*` verbs reformat the whole file and `update-plan-progress` clobbers the dependency table. |
| Parsing `infoic.xml` for a measurement | A fresh filter implementation | Load `tools/build_db.py` as a module, patch `requests`/`OUTPUT_FILE`, diff two runs | It reproduces the shipped database exactly, so the numbers are the real ones. Harness at `…/scratchpad/m/harness.py`. |

**Key insight:** every artifact this phase touches already has a shipped precedent from Phase 197 or
148. There is nothing to design — only to measure, copy the shape, and correct the three false claims
the measurement exposed.

## Common Pitfalls

### Pitfall 1 — Reading D-02 literally and keying on the full low byte
**What goes wrong:** `VPP_MV.get(voltages & 0xFF, 0)` with `0xF1`/`0xF2` added. **142 rows lose their
VPP entirely**, dropping to the `0` default.
**Measured breakage, by low byte:** `0x01`→113 rows (12000→0), `0x08`→13 (12000→0), `0x71`→9
(13000→0), `0x0A`→3 (12000→0), `0x04`→2 (12000→0), `0x0B`→1 (12000→0), `0x11`→1 (9000→0).
**Why it happens:** D-02's phrase *"Key on the full low byte with the option bits stripped"* reads as
one instruction but is two. `0xF1`/`0xF2` are **distinct indices**, not `0xF0` plus flags — so no
single mask both preserves them and strips the real option bits.
**How to avoid:** exact-match `0xF1`/`0xF2` **before** masking. Measured byte-identical across all 767
rows:
```python
_vpp_lo = voltages & 0xFF
_d_vpp_mv = VPP_MV[_vpp_lo] if _vpp_lo in _VPP_EXACT_LOW_BYTES else VPP_MV.get(_vpp_lo & 0xF0, 0)
```
(with `_VPP_EXACT_LOW_BYTES = (0xF1, 0xF2)` — express it as a derived constant, not two literals, and
keep it non-part-specific.)
**Warning signs:** the regeneration diff shows more than 15 changed rows, or any row emits
`vpp_mv: 0`.

### Pitfall 2 — Believing the suite is green after regenerating only the database
**What goes wrong:** `test_unsourced_count_is_pinned_exactly` and `test_total_entry_count_is_pinned_exactly`
read `tools/datasheet_overrides.json` directly. Regenerate the database without editing the override
file and they stay green; edit the override file in a later task and they redden then.
**How to avoid:** put the override-file edit and the two literal updates
(`_EXPECTED_UNSOURCED_COUNT = 6 → 18`, `_EXPECTED_ENTRY_COUNT = 9 → 22`, both at
`tests/test_datasheet_overrides.py:335-336`) in the **same task**. Make "5 named tests move from red
to green" the acceptance criterion, not "the suite is green".
**Warning signs:** a SUMMARY reporting 3 failures fixed rather than 5.

### Pitfall 3 — Counting override *entries* when CONTEXT counts *fields*
**What goes wrong:** "adds up to 17 entries" becomes `_EXPECTED_ENTRY_COUNT = 26`. The real count is
**22** — 17 field pairs over **13 new keys**, because `FUJITSU/MBM27C1001` and `FUJITSU/MBM27128`
already exist and gain fields.
**How to avoid:** assert the key count (22) and the `UNSOURCED` count (18) separately, and derive both
from the file rather than from arithmetic.

### Pitfall 4 — A dedent or reflow resurrecting comments as `+` lines
**What goes wrong:** exactly the 197-02 failure. Re-indenting near `VCC_VOLTAGES` or `VPP_MV` makes
unchanged comment lines appear as additions; the C-2 pre-commit check trips; the executor deletes
them and loses the only copy of the `# BUG-1 fix` provenance.
**How to avoid:** add dict entries **in place**. Do not reformat. Run the pathspec-scoped check before
every commit:
```bash
git -C firestarter_app diff --cached -- '*.py' | /usr/bin/grep -E '^\+\s*#' | /usr/bin/grep -v '^\+\s*#!'
```
It must print nothing. **The pathspec is load-bearing** — without it the pattern also matches markdown
and reports `DECODE-NOTES.md` § 9, a file it does not govern.
**Warning signs:** a staged diff touching more comment lines than code lines.

### Pitfall 5 — Propagating the falsified `database.c#L130-L135` citation
**What goes wrong:** D-01 says to *extend* the existing `[VERIFIED: …]` marker. Extending it verbatim
carries a wrong line range and a wrong table name into the phase's own evidence — on a phase whose
subject is decode provenance.
**How to avoid:** replace with `database.c#L182-L190 @ a8efaedc — xg_vcc_voltages[]` (F-1's measured
line numbers). Fix **both** occurrences, at `build_db.py:116` and `:126`.

### Pitfall 6 — A hand-transcribed wire-dict delta layer
**What goes wrong:** the `|<i>` suffix is a positional index within a manufacturer's row list. A
hand-written `FUJITSU|MBM27C4001|12` is right today and rots on any reorder.
**How to avoid:** generate from the live capture programmatically — the 197 layer's `provenance` field
states this rule explicitly. Verify `keys equal: True` between baseline and regenerated databases
first (this phase adds and removes zero rows, so it holds).

### Pitfall 7 — Running the suite under the devcontainer default Python
**What goes wrong:** `python3` is 3.12.14 and `.venv/bin/python` is a symlink to `/bin/python`. The
app's CI floor is 3.11 and a 3.12 run has masked real CI failures before.
**How to avoid:** every suite verify leg uses `.venv/ci-replica/bin/python` (3.11.16, editable
install confirmed), with `-o addopts=""` so the count line is visible.

### Pitfall 8 — Editing the archived `148-DB-DIFF.md`
**What goes wrong:** its § Non-claim is falsified by D-04, and the reflex is to fix it. D-14 forbids
this: archived records are historical-by-intent. **But note the converse** — `197-GH70-ANSWER.md` is
in the *current* milestone's live phase directory and D-18 **requires** editing it. State both halves
in the task so an executor does not over-apply D-14.

### Pitfall 9 — Adding a part-number-shaped string to `build_db.py`
**What goes wrong:** the OVR-06 census `ast.parse`s every string constant and pins the survivor list
at exactly one entry (`"DIP28"`). D-01/D-02 add integers only and are safe — but a D-06 build-time
assertion whose message embeds a part number would trip `test_real_source_matches_frozen_allow_list_exactly`.
**How to avoid:** if the predicate ships, keep its message value-keyed and part-name-free, mirroring
`_VCC_MARGIN_RAIL_MV`. Otherwise add the survivor to the golden with a recorded reason in the same
commit.

## Code Examples

### Reproducing the baseline and diffing a candidate change

```python
# Harness — reproduces the shipped chip_database.json exactly, offline.
# Kept at /tmp/claude-1000/-workspaces/8b44ccd0-.../scratchpad/m/harness.py
import importlib.util, json, types

APP = "/workspaces/firestarter_app"
XML = ".../infoic_pinned.xml"   # sha256 cdd21319ae6cce2316ca2361a9fb82cba89b27b66bb78d58b01032a441106b8a

def load():
    spec = importlib.util.spec_from_file_location("bdb", APP + "/tools/build_db.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def patch_fetch(m):
    raw = open(XML, "rb").read()
    class R:
        content = raw
        def raise_for_status(self): pass
    m.requests = types.SimpleNamespace(get=lambda *a, **k: R())
    return m

def run(m, out):
    m.OUTPUT_FILE = out
    m.main()
    return json.load(open(out))
```

To simulate the phase: set `m.VCC_VOLTAGES` to the 15-entry `xg` table, set
`m._VCC_MARGIN_RAIL_MV = m.VCC_VOLTAGES[0x02]`, and point `m.DATASHEET_OVERRIDES_FILE` at a candidate
file. **The candidate override file must live under `firestarter_app/tools/`** — the loader derives
the repository root from the override file's own path (`build_db.py:381`), so a scratchpad copy makes
every `datasheets/*.pdf` citation fail validation.

### The completed `VCC_VOLTAGES` (D-01)

```python
# [VERIFIED: minipro database.c#L182-L190 @ a8efaedc — xg_vcc_voltages[]]
VCC_VOLTAGES = {
    0x00: 5000, 0x01: 3300, 0x02: 4000, 0x03: 4500, 0x04: 5500,
    0x05: 6500, 0x06: 1800, 0x07: 2500, 0x08: 3000, 0x09: 1200,
    0x0A: 4750, 0x0B: 5250, 0x0C: 5750, 0x0D: 6000, 0x0E: 6250,
}
```
*(Layout shown compactly; preserve the file's existing one-key-per-line style to minimise diff noise
and avoid the Pitfall-4 reflow. `0x0F` is genuinely absent upstream and must stay absent.)*

### A held-row override entry (D-05)

```json
  "EXEL/XL2804A": {
    "datasheet": "UNSOURCED",
    "note": "The completed decode maps vdd index 0x06 to 1800 mV. 1.8 V is not credible as a program rail for a 5 V 28C-class parallel EEPROM, so the emitted value is held at the 5000 this row shipped before VCC_VOLTAGES was completed — a figure that was itself an unmapped-index fallback, not a decode. Closed by: EXEL's own datasheet for the XL2804A, vendored and git-tracked under datasheets/.",
    "fields": {
      "electrical.vdd_mv": { "was": 1800, "is": 5000 }
    }
  },
```
Verified to load, resolve to exactly one row, and produce zero net diff.

### The verify legs that resolved in a real run this session

```bash
cd /workspaces/firestarter_app

# Regeneration + row count
python tools/build_db.py 2>&1 | tail -1 | /usr/bin/grep -q '= 746 total\.'

# Byte-identical proof for a no-diff change (D-02 alone)
git diff --quiet -- firestarter/data/chip_database.json

# Suite, under the 3.11 CI replica, with the count line visible
.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q -p no:randomly 2>&1 | tail -5

# Targeted snapshot re-record, then the narrowness proof
.venv/ci-replica/bin/python -m pytest "tests/test_characterization.py::test_list" \
  -o addopts="" -q -p no:randomly --snapshot-update
git diff --numstat tests/__snapshots__/test_characterization.ambr   # must print exactly: 2<TAB>2

# Override file counts, derived not asserted
.venv/ci-replica/bin/python -c "import json;d=json.load(open('tools/datasheet_overrides.json'));print(len(d), sum(1 for v in d.values() if v['datasheet']=='UNSOURCED'))"
# must print: 22 18

# The no-new-comments gate (pathspec is load-bearing)
git -C /workspaces/firestarter_app diff --cached -- '*.py' | /usr/bin/grep -E '^\+\s*#' | /usr/bin/grep -v '^\+\s*#!'
# must print nothing
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| Part-specific values hardcoded in `build_db.py` (`NMOS_TRUE_VPP_MV`, `MAX_27C020_SIZE`) | `tools/datasheet_overrides.json`, fail-closed, with `was`/`is` and a citation or `UNSOURCED` | Phase 197 (v1.40) | This phase adds entries only; the loader needs no change |
| Decode rationale in source comments | `tools/DECODE-NOTES.md` numbered sections | v1.33 Source Hygiene → CLAUDE.md hard rule | § 9 is the only legal home for the VOLT-01 finding |
| Re-baselining `wire_dict_baseline.json` on each change | Append-only, field-disjoint delta layers (149, 153, 182, 194, 197) | Phase 149 onward | A 198 layer is the only permitted route |
| `tools/diff_db.py` | **Does not exist** — a throwaway script, uncommitted | before v1.40 | Do not plan a task that edits it |
| `tools/baseline/chip_database.baseline.json` | **Stale** (475857 vs 432461 bytes); use `git show <sha>:firestarter/data/chip_database.json` | noted in 197-REGEN-DIFF | Using the stale baseline produces a large spurious diff |

**Deprecated/outdated in the surrounding documents:**
- The todo's *"748-chip generation"* — the database is 746 today.
- The todo's *"genuinely-3.3V Microchip memory-family parts"* — contradicted by Phase 148's own
  record and the shipped source comment (F-4).
- `148-DB-DIFF.md` § Non-claim's *"already records 5.0 V"* for sub-group 2 — falsified by D-04.
  **Do not edit it** (D-14).
- CONTEXT's `database.c:123`, its "both tables carry a `[VERIFIED: … @ a8efaedc]` marker", and its
  powerdown-flag corroboration — all corrected in F-1, F-12 and F-2.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | The 15 non-`LV` sub-group-1 rows are 5 V parts **by part-number class convention** (28C04/16/17/64/256 family). No datasheet is vendored for any of them. | F-4 | Low for this phase — D-11 ships all 28 unchanged, so nothing depends on it. It is the *stated reason* in the disposition file, so it must be labelled a class inference, not a datasheet reading. Corroborated independently by Phase 148's own measurement. |
| A2 | `28LV64A` is a genuine low-voltage part, so `vdd 3300` is plausible for that one row. | F-4 | Low — no value moves. Its `vcc 5500` remains implausible either way, which the disposition should say. |
| A3 | The low nibble of the VPP byte carries option flags (the generator's existing reading). Upstream defines **no** constant for it (F-2). | F-2, F-13 | Medium — if § 9 asserts it as upstream-attested it would be a false provenance claim on a provenance phase. Mitigation: state it as the generator's working reading, corroborated by the `0x00`/`0x01` and `0x70`/`0x71` pairings. |
| A4 | The end-state suite count is ~2067. | F-9 | Low — measure it rather than asserting it; only the 5 named tests are load-bearing. |
| A5 | `198-VOLT03-DISPOSITION.md` is the right filename/location (discretion). | F-10 | None — pure naming; both the phase-directory and `notes/` precedents are live. |

**Everything else in this document was measured this session** against the pinned upstream
(sha-verified) or the live tree, and is tagged `[VERIFIED: …]` at its point of use.

## Open Questions

1. **Should the `vdd < vcc` predicate ship as a build-time assertion?** (CONTEXT discretion)
   - What we know: it selects exactly 28 rows, is value-keyed and part-name-free, and mirrors
     `_VCC_MARGIN_RAIL_MV`'s shape. A reporting-only assertion would make a 29th row loud.
   - What's unclear: D-03 declined fail-closed behaviour for the `.get` defaults; a raise here would
     sit oddly beside that. A `print(..., file=sys.stderr)` matching the existing `WARN:`/`INFO:`
     lines is the consistent middle.
   - Recommendation: **document-only this phase**, with the reporting variant left in the deferred
     list where CONTEXT already put it. If it does ship, keep the message part-name-free (Pitfall 9).

2. **How to cover the 12 held entries for non-vacuity.** (CONTEXT discretion)
   - What we know: the 197-06 shape is one planted-mutation test proving the gate can fail. The
     override loader already raises on stale `was`, so a wrong `1800` fails the build loudly.
   - Recommendation: **one planted-mutation test** asserting that flipping one held entry's `is` from
     5000 changes exactly that row's emitted `vdd_mv` — plus a cheap structural assertion that
     exactly 12 entries carry `{"electrical.vdd_mv": {"was": 1800, "is": 5000}}`. Per-entry tests
     would be 12 near-duplicates with no extra failure-detection power.

3. **Does § 9 restate D-16's `0xF1`/`0xF2` dead-entry finding, or only § 8-style "provably dead"?**
   - Recommendation: § 8's precedent is to state it as a fail-closed/dead-branch paragraph naming the
     only coverage. Mirror that: the entries are unreachable against the pinned upstream, the proof is
     byte-identical regeneration, and **no test can cover them** until upstream ships such a row.

4. **Exact end-state suite count.** Measure at the end; do not assert a number in a plan.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| Python 3.11 (CI replica) | Suite runs, generator | ✓ | 3.11.16 at `firestarter_app/.venv/ci-replica/bin/python`, app installed editable | none needed |
| Python 3.12 (devcontainer default) | — | ✓ | 3.12.14 | **Do not use** — masks CI |
| `pytest` + `syrupy` | Suite, snapshots | ✓ | in ci-replica venv; 2065 tests collect and run in ~176 s | — |
| `requests` | `build_db.py` network fetch | ✓ | in ci-replica venv | Local pinned XML via the harness |
| Network → gitlab.com | Pinned `infoic.xml` / `database.c` | ✓ | verified this session | Pinned XML cached locally, sha-matched |
| `gh` CLI | gh#66 read | ✓ | works with `XDG_CACHE_HOME` set to a writable dir | — |
| `git` in submodule | Commits, `git mv`, `ls-files` | ✓ | `firestarter_app` on `v1.40-program-parameter-fidelity` @ `0372cc6` | — |
| Vendored Microchip / AMD datasheets | Closing the 16 sub-group-1 rows | **✗** | none in `datasheets/` | **None.** This is D-13's mandatory honesty limit, not a blocker — D-11 ships all 28 unchanged. |
| Vendored EXEL / ST-28C / SGS-28C datasheets | Closing the 12 held rows | **✗** | none | **None.** Drives the `UNSOURCED` marking and the successor backlog entry. |
| Bench hardware | — | n/a | — | Not required: host-only, no firmware change, no electrical claim made. |

**Missing dependencies with no fallback:** none that block execution. The two missing datasheet
classes are *findings this phase must state*, not obstacles to it.

## Security Domain

`security_enforcement` is not disabled in `.planning/config.json`, so this section is included. The
phase has **no authentication, session, access-control, cryptography or network-input surface** — it
edits a build-time generator, a JSON data file, markdown, and test fixtures.

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | No auth surface |
| V3 Session Management | no | No sessions |
| V4 Access Control | no | No access control |
| V5 Input Validation | **yes** | Already shipped: `_validate_datasheet_overrides_shape` + `apply_datasheet_override` fail closed on 8 distinct malformations (shape, sort order, missing key, empty fields, bad pair, unknown field path, duplicate target, type mismatch, stale `was`, no-op, dead key). **This phase adds data to that validated surface and must not weaken any leg.** |
| V6 Cryptography | no | None. (`sha256sum` used here only to verify pinned-source integrity.) |

**Domain-specific hazard — the real one.** The genuine safety surface is **electrical, not
informational**: `vpp_mv` crosses the wire and sets a physical rail on the programmer. A wrong value
can damage a chip.

| Pattern | STRIDE | Mitigation |
|---|---|---|
| Over-voltage on a corrected row | Tampering (physical) | 12500 is the part's own datasheet nominal (D-07), far below `RURP_VPP_CEILING_MV` (25000). The firmware's `vpp_mv + 500` hard error keeps the band at 13000, under the datasheet's 13.5 V abs-max. **No `support_status` moves** — measured. |
| Under-voltage from a mis-implemented mask | Denial of service | Pitfall 1: the naive keying drops 142 rows to `vpp_mv: 0`. Mitigation: the exact-match-then-mask expression, plus the regeneration diff bounding changes at 15 rows. |
| Unsourced value presented as sourced | Repudiation | The `UNSOURCED` token is structurally enforced (a non-path value must be exactly `UNSOURCED`, and must carry a note), and every citation path must be **git-tracked**, asserted by `test_every_datasheet_value_is_a_tracked_path_or_unsourced_with_note`. |
| Silent decode regression | Tampering | Five named tests plus the byte-identical/differential regeneration proof. |

## Sources

### Primary (HIGH confidence — fetched or read this session)
- `https://gitlab.com/DavidGriffith/minipro/-/raw/a8efaedc236c1d9718bd28299dfbb99536b010ff/src/database.c`
  — sha256 `896f1948e67a03f333ade157845ac2cf1d4dda27e571c989729de2dd928ff72e`, 2114 lines. Voltage
  tables L130-L190; the decisive comment L121-L129; the unpack L693-L697; powerdown tests L678-L682.
- `.../a8efaedc.../src/minipro.h` — `LAST_JEDEC_BIT_IS_POWERDOWN_ENABLE` / `POWERDOWN_MODE_DISABLE` /
  `ATF_IN_PAL_COMPAT_MODE` at L83-L85 with their ATF scoping comment; `can_adjust_vpp`/`can_adjust_vcc`
  at L185-L186.
- `.../a8efaedc.../infoic.xml` — sha256 `cdd21319ae6cce2316ca2361a9fb82cba89b27b66bb78d58b01032a441106b8a`,
  17,861,009 bytes. Confirmed identical to the prior session's scratchpad copy.
- `firestarter_app/tools/build_db.py` @ `0372cc6` — 848 lines, read at every site named in F-12.
- `firestarter_app/tools/datasheet_overrides.json` — 65 lines, 9 keys, read in full.
- `firestarter_app/tools/DECODE-NOTES.md` — 367 lines; headings surveyed, §§ 6 and 8 read in full.
- `firestarter_app/tests/test_wire_dict_equivalence.py` (612 lines),
  `tests/test_datasheet_overrides.py`, `tests/test_build_db_constant_census.py`,
  `tests/golden/wire_dict_expected_deltas_197.json`, `tests/golden/build_db_part_specific_constants.json`.
- Live measurement runs: baseline reproduction, Run A (D-01), Run B (full phase), D-02 mask variants,
  full suite under Python 3.11, targeted snapshot re-record with `--numstat`, override-count run.
  **Working tree restored to its pre-measurement state and verified clean.**
- `gh issue view 66 --repo henols/firestarter`.

### Secondary (HIGH — project records read this session)
- `.planning/phases/198-.../198-CONTEXT.md`; `.planning/REQUIREMENTS.md` (VOLT-01…04 at :68-77,
  VOLT-F1 at :120, status table :146-149); `.planning/config.json`; `/workspaces/CLAUDE.md`.
- `.planning/phases/197-.../197-GH70-ANSWER.md` (§ Held-pending deferral, :113-143),
  `197-REGEN-DIFF.md`, `197-PULSE-INVENTORY.md`.
- `.planning/notes/197-build-db-comment-provenance-rescued.md`,
  `.planning/notes/197-at28c-guard-evidence-for-phase-199.md`.
- `.planning/todos/pending/vcc-5500-high-margin-verify-rail-group.md`.
- `.planning/ROADMAP.md` :255 (197-07 record), :7944-8052 (999.69/70/71/72).
- `.planning/milestones/v1.32-phases/148-.../148-DISCUSSION-LOG.md` :44, `148-06-PLAN.md` :458,
  `148-06-SUMMARY.md` :72/:108 — the "sixteen 5 V EEPROMs" measurement.

### Tertiary (MEDIUM/LOW)
- Part-class conventions for the 28C/28LV families (A1, A2) — training knowledge, **no vendored
  datasheet**. Corroborated in-repo by Phase 148's independent measurement but not datasheet-verified.

## Metadata

**Confidence breakdown:**
- Upstream tables and every derived count: **HIGH** — fetched at the pinned sha, transcribed verbatim,
  each CONTEXT claim independently re-derived.
- Regeneration diff (15 rows / 17 fields): **HIGH** — differential against a baseline proven identical
  to the shipped artifact.
- Test blast radius (5 tests, 3 files): **HIGH** — every failure observed by running the suite, not
  predicted.
- Wire-dict layer (2 entries) and snapshot (2 lines): **HIGH** — observed failures and `--numstat`.
- Sub-group-1 per-row **class** disposition: **MEDIUM** — measurement of the rows is HIGH; the 5 V/3.3 V
  class reading is an inference with no vendored datasheet, corroborated by Phase 148.
- Documentation templates and close mechanics: **HIGH** — read from the live precedents.

**Package legitimacy audit:** not applicable — this phase installs no external package. No entry in
the Standard Stack; all tooling (`pytest`, `syrupy`, `requests`) is already present in the CI-replica
environment and unchanged by this phase.

**Validation Architecture:** omitted — `workflow.nyquist_validation` is explicitly `false` in
`.planning/config.json`.

**Research date:** 2026-09-18
**Valid until:** stable — the upstream source is pinned at `a8efaedc`, so the measurements do not
expire. Re-measure only if `firestarter_app` HEAD moves past `0372cc6` or `MINIPRO_XML_URL` is
re-pinned.

---
*Phase: 198-the-two-voltage-nibbles*
*Researched: 2026-09-18*
