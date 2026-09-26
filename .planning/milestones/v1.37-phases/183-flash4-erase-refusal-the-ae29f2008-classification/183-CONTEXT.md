# Phase 183: Flash4 Erase Refusal & the AE29F2008 Classification - Context

**Gathered:** 2026-09-11
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers four things and nothing else:

1. **A host-side pre-flight refusal** for `firestarter erase` on a flash4 (`algorithm 5`) part, replacing
   the firmware's bare `Not supported` at the operator's terminal (SAFE-06).
2. **A measured mechanism decision** — three candidates priced against firmware flash before one is
   chosen, with both/all figures recorded (SAFE-07, D-3).
3. **An adjudicated deletion** of `configure_flash_5v_page`'s unreachable `CMD_ERASE` arm and the 12 V
   erase routine behind it (SAFE-08).
4. **A recorded verdict** on whether AE29F2008 is classified `algorithm 5` correctly, grounded in a
   datasheet and the upstream `infoic.xml` row, with any correction landing in `build_db.py` (SAFE-09,
   D-6).

**Not in this phase:** implementing a software chip-erase for the `0x05` family (backlogged, see
Deferred); generalizing the refusal to UV-EPROM / SRAM / `0x0D` (Deferred); any change to the standalone
`firestarter blank` command; any JP4 / socket-pin-25 VPP-reroute gate (Deferred); replying to gh#62 —
that is Phase 187's REPLY-03.

</domain>

<decisions>
## Implementation Decisions

### The refusal's mechanism and placement

- **D-01:** SAFE-07 prices **all three** candidate mechanisms, not the two SAFE-07 names alone. The third
  is a **host pre-flight policy gate** — the pattern already shipped twice in this repo
  (`sdp_capability.py`, `jp5_gate.py`). Excluding the option the repo already uses twice would make
  D-3's pricing incomplete. The phase record states every figure and why the winner won.
  — **Reversibility:** reversible — pricing is a recorded measurement, not a code commitment.

- **D-02:** If a host-side refusal wins, it fires **before the serial port is opened** — the
  `sdp_capability.py` contract verbatim ("enforced by the caller before the serial port is even
  opened"). The operator must not see `Connecting... OK` followed by a refusal; that sequence is what
  read as a malfunction in gh#62.
  — **Reversibility:** reversible.

- **D-03:** The refusal's reasoning lives in **its own policy module** — a third sibling to
  `sdp_capability.py` and `jp5_gate.py`: pure predicate, no I/O, no serial access, unit-testable with no
  board. It must NOT be folded into either existing module: `jp5_gate` is a socket-pin-1 electrical
  hazard and `sdp_capability` is a `0x0D` allow-list; mixing hazard axes in one module is how predicates
  drift. It must NOT be inlined in `cli_handlers.erase` — keeping policy out of the CLI layer is the
  stated purpose of both precedents.
  — **Reversibility:** costly — undo means moving the predicate and its tests, and re-deciding the
  boundary the two precedents established.

- **D-04:** **Firmware keeps refusing.** The host gate is the operator-facing refusal; `eprom_erase`'s
  `MSG_ERR_NOT_SUPPORTED` stays as the backstop for anything that reaches the firmware another way
  (operator's own words: "in the fw directly return not supported if someone is bypassing the gate").
  Defence in depth, not a replacement.
  — **Reversibility:** one-way in intent — removing the firmware backstop would leave a bypassable gate;
  it must not be removed on the grounds that the host gate makes it redundant.

- **D-05:** **Scope is flash4 (`0x05`) only.** `eprom_erase`'s bare refusal also fires for UV-EPROM and
  SRAM — every part without `FLAG_CAN_ERASE` — but widening this phase to every family is a separate
  capability. Recorded as a Deferred idea with its design already named.
  — **Reversibility:** reversible.

### What the refusal says and returns

- **D-06:** **Exit 1 by default; exit 0 only behind an explicit flag.** The default stays a refusal, so
  the exit code keeps saying the requested operation was not performed. A no-op exit 0 is available only
  as an opt-in for scripting. (Operator chose this over an unconditional exit-0 no-op.)
  — **Reversibility:** costly — the exit code is a published CLI contract; scripts depend on it.

- **D-07:** **The message is ONE LINE and nothing more** — of the shape
  `Erase not supported for <EPROM>`. It carries **no cause**, **no alternative**, and **no literal
  `firestarter write` command**. Operator decision, taken knowingly after the orchestrator stated that
  it conflicts with SAFE-06's own words and with gh#62's reading of "not supported" as *unavailable*.
  — **Reversibility:** reversible — wording is a string.

- **D-08:** **Three documents must be amended by this phase to match D-07** — this is a deliverable, not
  a side effect, and an executor must not quietly under-deliver SAFE-06 instead:
  | Document | Current text | Amend to |
  |---|---|---|
  | `.planning/REQUIREMENTS.md` § SAFE-06 | "states its cause and its alternative — the part self-erases per page during the write, so `erase` is unnecessary rather than unavailable" | names the part; cause and alternative are NOT carried in the CLI |
  | `.planning/ROADMAP.md` Phase 183 **Goal** | "A refusal that is right for a reason **says the reason**" | the refusal names the part; the reason is recorded and answered to the reporter, not printed |
  | `.planning/ROADMAP.md` Phase 183 **success criterion 1** | "names the cause (a page-write part self-erases during the write) and the alternative (`write` directly) — not a bare `Not supported`" | names the part, in place of a bare `Not supported` |
  — **Reversibility:** reversible, but the amendment must land in the same phase as the code, or the
  records describe a tool that does not exist.

- **D-09:** **The cause and the alternative are not lost — they move to REPLY-03** (Phase 187), which
  already owes gh#62 "why the refusal exists, what changed, and — explicitly — that re-running under
  another chip's identity with `--force` is not a safe workaround."
  — **Reversibility:** reversible.

- **D-10:** **The CLI does not warn about the forged-identity `--force` workaround.** That warning is
  REPLY-03's alone. (Operator chose this over also carrying a clause in the CLI text.)
  — **Reversibility:** reversible.

- **D-11:** D-07 **weakens the new-firmware-id candidate specifically**, because the chip name is
  host-side context the firmware does not carry at the refusal site. The three-way pricing in D-01 still
  runs as specified — this is a stated expectation of its outcome, not a pre-emption of it. A researcher
  or planner must not skip the measurement on the strength of this note.
  — **Reversibility:** n/a — an observation.

### SAFE-08 — the dead 12 V erase path

- **D-12:** **Delete all of it:** `configure_flash_5v_page`'s `CMD_ERASE` arm
  (`flash_5v_page.cpp:49`), `flash_5v_page_erase_execute` itself (`flash_5v_page.cpp:193-225`), and
  `flash_5v_page_write_init`'s `is_flag_set(FLAG_CAN_ERASE)` erase-on-write block
  (`flash_5v_page.cpp:80-86`) — its only other caller, equally unreachable. The 12 V-on-a-5 V-part
  routine stops existing rather than standing one host-side policy line away from a real chip.
  — **Reversibility:** costly — restoring it means re-deriving the 12 V sequence from the original
  commit; but nothing calls it, so nothing breaks.

- **D-13:** **Precision required in the phase record.** The arm's *assignment* DOES execute
  (`configure_memory` runs at `firestarter.cpp:91`, during INIT); it is the *function pointer* that never
  fires, because `eprom_erase` refuses at `firestarter.cpp:273`. SAFE-08's "unreachable" must be stated
  that way and not as "the arm never runs".
  — **Reversibility:** n/a.

- **D-14:** **`scripts/check_erase_no_vpp.py` is this phase's to fix**, not Phase 185's. Two separate
  jobs:
  1. Its docstring cites *"flash_5v_page.cpp lines 196-231 (`flash_5v_page_erase_execute`)"* — the file
     is **225 lines** and the function is at **193-225**, so the cited range **cannot exist**. Re-cite by
     **symbol and enclosing scope, never a line number** (the CLAIM-06 lesson), so the next sweep cannot
     stale it again.
  2. Its "**proximity, not absence, is the risk**" rationale rests on that function existing in the
     tree. After D-12 it does not. Update the rationale and record that the copy-source hazard is gone,
     while keeping the gate armed.
  **Measured: the gate does not break functionally.** Its non-vacuity anchor is scoped to
  `eeprom28c_erase_execute`'s body (`handle->firestarter_set_data(` plus `delay(AT28C_TEC_MAX_MS)`), not
  to `flash_5v_page`, and `--function` defaults to the `0x0D` symbol. Only the prose is false.
  *(Orchestrator recommendation taken — operator expressed no preference.)*
  — **Reversibility:** reversible.

- **D-15:** **Phase 185's baseline re-record now depends on Phase 183.** `check_size_baseline.py`'s
  default mode is a **byte-identity** gate, so D-12's firmware shrink reddens it; CLAIM-04/05 re-records
  `size_baseline.json` against a cold rebuild. The ROADMAP currently marks Phase 185 "independent" —
  **amend it to depend on Phase 183**, so CLAIM-04's green gate describes the real tree. A *shrink*
  authors **no new MERGE-05 exemption** (the four existing ones total 724 B against BASE-01 and are
  additive allowances), so CLAIM-05's "no new exemption" clause survives.
  *(Orchestrator recommendation taken — operator expressed no preference.)*
  — **Reversibility:** reversible.

- **D-16:** **The SAFE-07 measurement is a cold build of all three AVR targets**:
  `rm -rf .pio/build/<env>` then exactly one `pio run -e <env>`, for `uno`, `uno328pb` and `leonardo` —
  the procedure `size_baseline.json`'s own `meta` documents. **Leonardo is the figure that decides D-3**
  (0 B flash and 0 B RAM headroom since v1.32 Phase 153).
  *(Orchestrator recommendation taken — operator expressed no preference.)*
  — **Reversibility:** n/a — a measurement procedure.

- **D-17:** **Watch for tests going vacuous.** After D-12, `test_val_5v_page.cpp`'s ERASE-02 cases
  (around lines 327-355) assert that `flash_5v_page_write_init` performs no erase **with
  `FLAG_CAN_ERASE` clear** — once the branch is deleted, that assertion is tautological. This is the
  CLAIM-07 defect class ("no test claims coverage that does not exist") appearing inside this phase's own
  blast radius; it must be adjudicated here, not left for a later sweep. The same file also carries a
  line-number citation to `flash_5v_page.cpp:80-86` (line 234) and a prose NOTE naming
  `flash_5v_page_erase_execute` (lines 20-21), both of which D-12 invalidates.
  — **Reversibility:** reversible.

### SAFE-09 — the AE29F2008 classification

- **D-18:** **Datasheet-by-equivalence is acceptable evidence, AND the upstream `infoic.xml` row must be
  checked too.** AE29F2008 (ASD-branded, 2 Mbit, 32-pin DIP) has no retrievable primary datasheet and
  reads as a re-badge. The equivalence chain must be recorded explicitly and the verdict must name itself
  as equivalence-based, never as a direct AE29F2008 datasheet reading. Re-fetching the pinned upstream
  `infoic.xml` closes the "is the generator right" half directly, rather than inferring it.
  — **Reversibility:** reversible.

- **D-19:** **Expected verdict — classification CORRECT — with the reporter also correct.** Stated here
  as a projection to be falsified, NOT as a conclusion research may assume. The Winbond **W29C020C** is
  *"a 2-megabit, 5-volt only CMOS flash organized as 256K x 8"*, written *"on a page basis, with every
  page containing 128 bytes"*, and it has a **fast chip-erase (50 ms)** via the JEDEC software sequence.
  Every DB field agrees: `chip_id_value 0x0000da45`, `size_bytes 262144` (= the reporter's `0x40000`),
  `infoic_page_size_raw 128`, `algorithm 5`. And the reporter's `erase SST39SF020 --force` succeeding in
  0.14 s is explained by `0x06` (AMD unlock) emitting a compatible chip-erase sequence the silicon
  accepts. **Both observations are true at once** — the classification is right and the erase was real;
  the `0x05` firmware path simply does not implement the chip-erase this silicon supports. The reporter
  even names `W29C020C` in gh#62 as one of the identities they tried.
  — **Reversibility:** n/a — a projection.

- **D-20:** **On the CORRECT branch, the software chip-erase is recorded and BACKLOGGED, not built.** It
  is a new firmware capability; the milestone excludes firmware behaviour changes, and Leonardo has no
  headroom. The `0x0D` family's own `eeprom28c_erase_execute` (AN-0544B six-byte software chip erase, 0 B
  RAM via inline literal writes) is the template for whoever picks it up.
  — **Reversibility:** reversible.

- **D-21:** **On the MISCLASSIFIED branch, the override mechanism is the Phase 182 named-root-cause-rule
  pattern:** a named rule in `build_db.py` carrying its evidence, a `diff_db.py` run proving **exactly**
  the expected changed rows, and `DECODE-NOTES.md` brought current — the `RULE_PHASE182_A19_PINOUT`
  precedent. A per-part exception table is **rejected**: it is the hand-kept list D-4 refuses, and the
  standing rule is that the generator may not invent fields absent from `infoic.xml`. `chip_database.json`
  is never hand-edited (D-6).
  — **Reversibility:** one-way in effect — a regeneration rewrites 746 rows; the rule, not the output,
  is the artifact under review.

- **D-22:** **`support_status` for AE29F2008 is UNTOUCHED.** It reads `supported` today and the part
  writes, reads, blank-checks and verifies; only the standalone erase is refused, correctly. Consistent
  with v1.22's zero-`support_status`-change precedent on a software-only, no-bench milestone.
  *(Orchestrator decision — operator's answer addressed blank-check policy instead; nothing in the
  evidence moves the status.)*
  — **Reversibility:** reversible.

- **D-23:** **One thing in the same row that looks wrong, for research to settle, not to fix blind:** the
  DB row carries `"vpp_mv": 12000` for a part the datasheet calls **5-volt only**, on a protocol
  `PROTOCOLS.md` lists as *"None (5V)"*. Whether that field is inert display data or reaches a live check
  is a research question. If it proves live, it is a **new finding** — file it; do not widen this phase
  to fix it without an explicit scope decision.
  — **Reversibility:** n/a — an open question.

### Claude's Discretion

The operator expressed no preference on four items; the orchestrator's recommendation was taken and is
recorded above as a decision rather than left open — **D-14** (fix `check_erase_no_vpp.py` here),
**D-15** (Phase 185 depends on 183), **D-16** (cold build, all three AVR targets) and **D-22**
(`support_status` untouched). Any of these may be revisited by the operator; a planner should treat them
as locked.

Wording of the one-line refusal (D-07) beyond its shape is planner discretion, provided it carries no
cause, no alternative and no `--force` clause.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements, decisions and ordering
- `.planning/REQUIREMENTS.md` — SAFE-06…SAFE-09 and activation decisions D-1…D-7. **D-3** (price the
  mechanism before choosing), **D-4** (the SAFE predicate is database-derived, never a hand list) and
  **D-6** (a classification correction lands in `build_db.py`, never in the generated database) bind this
  phase. **SAFE-06 must be AMENDED by this phase — see D-08.**
- `.planning/ROADMAP.md` § "v1.37" and § "Phase 183" — the phase goal and the four success criteria.
  **The goal and criterion 1 must be AMENDED by this phase — see D-08.** § "Phase 185" must gain a
  dependency on Phase 183 — see D-15.

### The refusal path, end to end
- `firestarter_app/firestarter/database.py:556-584` — `convert_to_programmer`'s `if algo not in (5,)`:
  the single place `FLAG_CAN_ERASE` is cleared for flash4, with the standing hazard argument recorded
  around it.
- `firestarter/src/eprom_operations.cpp:34-38` — `eprom_erase`'s `!is_flag_set(FLAG_CAN_ERASE)` →
  `LOG_ERROR_ID(MSG_ERR_NOT_SUPPORTED)`. **This is where gh#62's `Not supported` comes from.** Stays, per
  D-04.
- `firestarter/src/firestarter.cpp:91` and `:273` — `configure_memory` during INIT, then `eprom_erase`.
  The two line numbers that make SAFE-08's unreachability claim precise (D-13).
- `firestarter/src/operation_utils.cpp:82` — the generic op-layer NULL-`main` refusal, a second
  `MSG_ERR_NOT_SUPPORTED` site. Do not confuse it with `eprom_erase`'s.
- `firestarter_app/firestarter/cli_handlers.py:853-883` — `erase`'s Click handler: the `jp5_gate`
  call site the new gate sits beside, and the `sys.exit(0 if ok else 1)` D-06 modifies.

### The two refusal-pattern precedents (D-03)
- `firestarter_app/firestarter/sdp_capability.py` — pure predicate, fail-closed, "enforced by the caller
  before the serial port is even opened". The import-purity discipline at its head is the model.
- `firestarter_app/firestarter/jp5_gate.py` — Phase 182's gate: "No I/O, no environment reads — the wire
  dict and the operation name are the whole input", with its own injectable `isatty_fn` rather than
  importing `cli_handlers._is_interactive` (which Phase 185 deletes).

### SAFE-08's blast radius
- `firestarter/src/proms/flash_5v_page.cpp` — the file D-12 edits. Arm at `:49`, write_init erase block
  at `:80-86`, the 12 V routine at `:193-225`.
- `firestarter/scripts/check_erase_no_vpp.py` — the gate D-14 repairs. Read its full docstring: the
  stale citation is at lines 26-28, the "proximity, not absence" rationale immediately after, and the
  non-vacuity anchor (which is `0x0D`-scoped and therefore safe) at lines 60-70.
- `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` — the ERASE-02 cases D-17 warns
  about (≈327-355), the `flash_5v_page.cpp:80-86` citation at line 234, and the
  `flash_5v_page_erase_execute` NOTE at lines 20-21.
- `firestarter/scripts/baseline/size_baseline.json` — read `meta.note` and `meta.deltas_vs_base01` for
  the cold-measurement procedure D-16 follows and the four named MERGE-05 exemptions D-15 reasons about.
- `firestarter/scripts/check_size_baseline.py` — the default-mode byte-identity gate and the
  `MERGE05_*_EXEMPTION_BYTES` literals.
- `firestarter/PROTOCOLS.md` and `firestarter/CLAUDE.md` § "Algorithm Handlers" — the `0x05` row ("Page
  write + DQ7", VPP "None (5V)") and the `0x0D` row's warning: *"Do not 'optimise' the erase by reaching
  for `flash_5v_page_erase_execute` — that IS the 12 V path, and it belongs only to algorithm 5, which
  keeps its `FLAG_CAN_ERASE` exclusion for exactly that reason."*

### SAFE-09's evidence base
- `firestarter_app/firestarter/data/chip_database.json` → vendor `ASD`, `part_number` `AE29F2008`. The
  row under investigation. **Generated — never hand-edit** (D-6).
- `firestarter_app/tools/build_db.py` — `classify()` at ≈284-366: flash families (`0x05/0x06/0x0D/0x10`)
  return `proto_id` **unchanged**, so `algorithm 5` comes straight from upstream `infoic.xml`'s
  `protocol_id`. `infoic.xml` is fetched from the pinned commit named at `build_db.py:17`, not committed.
- `firestarter_app/tools/DECODE-NOTES.md` — brought current by D-21 if the misclassification branch
  fires.
- `firestarter_app/tools/diff_db.py` — the regeneration diff tool D-21 requires.
- W29C020C datasheet — https://datasheet.octopart.com/W29C020C-90B-Winbond-datasheet-181529584.pdf
  (2 Mbit, 5 V only, 256K×8, 128-byte page write, 50 ms fast chip-erase). The equivalence anchor for
  D-18/D-19.
- gh#62 — https://github.com/henols/firestarter_prom/issues/62 — the reporter's verbatim transcript:
  the refusal, the `SST39SF020 --force` erase at 0.14 s with `Chip ID 0xda45 does not match expected ID
  0xbfb6`, and the clean `blank AE29F2008` over `0x40000` in 27.96 s.

### Adjacent already-shipped behaviour — read before proposing a change here
- `firestarter_app/firestarter/chip_test.py:670-724` and `:765-812` — `dev test`'s plan already carries
  honest per-family reasons (`"flash4 (0x05) auto-erases per page; no separate erase op"`) and already
  marks the blank check **NA** for auto-erase-on-write protocols while keeping it for UV. The operator's
  blank-check policy is already implemented; do not re-implement it.
- `.planning/notes/jumper-display-ground-truth.md` — Phase 182's VPP-destination record, cited by the
  deferred JP4 idea below.
- `.planning/phases/182-jp5-destructive-operation-gate/182-06-SUMMARY.md` — the bench measurements the
  deferred JP4 idea rests on: socket pin 25, and `hw_revision` reporting a **bucket**.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`sdp_capability.py` / `jp5_gate.py`**: the two pure-predicate refusal modules D-03 makes the new
  module a sibling of. `jp5_gate.confirm_or_refuse` is the closest shape — a policy call at the top of
  the Click handler, before the operator object is touched.
- **`chip_test.py`'s per-family reason strings**: already-authored, already-reviewed wording for exactly
  this refusal. Not reused under D-07 (which wants one line naming the part), but they are the source to
  draw on if the Deferred generalization is ever taken.
- **`eeprom28c_erase_execute`** (`firestarter/src/proms/eeprom_28c.cpp`): the AN-0544B six-byte software
  chip erase, 0 B RAM via inline literal writes. The template for D-20's backlogged `0x05` chip-erase.
- **`RULE_PHASE182_A19_PINOUT`** in `build_db.py`: the named-root-cause-rule precedent D-21 follows.

### Established Patterns
- **Message ids are host-rendered.** `firestarter/include/messages.h` is codegen-generated and
  **ID-only** (176 lines of `#define`); format strings live in `firestarter_app/firestarter/messages.py`,
  both emitted from `tools/catalog/messages.toml`. `LOG_ERROR_ID(id)` → `LOG_ID(id)`. **So a new id is
  nearly free as a constant** — swapping the literal at an existing call site costs ~0 bytes. **The cost
  is the discriminator:** `eprom_erase` refuses for *every* part without `FLAG_CAN_ERASE` (UV-EPROM and
  SRAM included), so a flash4-specific id needs a new `handle->protocol` compare-and-branch that does not
  exist today. That is the figure D-16 measures.
- **The firmware would be re-deriving what the host already knows.** `database.py` clears the flag from
  `algo not in (5,)` before the command is built — the host has the protocol pre-connect.
- **Line-number citations stale here, repeatedly.** CLAIM-06 is one instance; D-14 found a second
  (`check_erase_no_vpp.py`) and D-17 a third (`test_val_5v_page.cpp:234`). Cite symbol + enclosing scope.
- **NO COMMENTS IN PRODUCT SOURCE.** Hard rule, `/workspaces/CLAUDE.md`, not overridable by a plan. It
  covers everything under `firestarter/` and `firestarter_app/`. Note that the existing files this phase
  edits are heavily commented — do **not** read that as licence. Click docstrings in `firestarter_app`
  are user-facing `--help` text, not comments, and are exempt.

### Integration Points
- **`cli_handlers.erase`** — the new gate's call site, beside the existing `jp5_gate.confirm_or_refuse`;
  and the `sys.exit` D-06 changes.
- **`flash_5v_page.cpp`** — three deletions (D-12), which cascade into `check_erase_no_vpp.py` (D-14),
  `test_val_5v_page.cpp` (D-17) and `size_baseline.json` (D-15).
- **`build_db.py` → `chip_database.json`** — only on SAFE-09's misclassification branch, and only via a
  named rule plus a regeneration (D-21).
- **Phase 187 / REPLY-03** — consumes D-07/D-09: the cause and alternative this CLI no longer prints are
  what that reply must carry.

</code_context>

<specifics>
## Specific Ideas

- **The operator's own words on the design (Area 1):** *"the cli shall directly tell it's not supported
  and in the fw directly return not supported if someone is bypassing the gate."* D-04 and D-02 are that
  sentence.
- **The message wording (Area 2):** *"Erase not supported for the EPROM"* — supplied as freeform, then
  confirmed as option (b): that line **and nothing more**, with the orchestrator's statement of the
  SAFE-06 conflict on the record before the choice was made. D-07/D-08.
- **On blank checks (Area 4):** *"If erase is not need blank check is unnecessary, but for uv EPROMs it's
  still has real value."* Verified as **already implemented** — `chip_test.py:704-714` marks the blank
  check NA for auto-erase-on-write protocols (*"no step in this plan can ever leave the device blank"*)
  and `:691-692` keeps it for UV (*"the write is irrecoverable and only UV light erases, so 'not blank' is
  a real pre-write finding"*); `flash_5v_page_write_init` has had no pre-write blank check since Phase
  153 (*"it was a false precondition, not a safety net"*). **The standalone `firestarter blank` command
  is deliberately left alone** — it is the oracle gh#62's reporter used to prove their erase had worked,
  and refusing it would have destroyed the evidence in the issue. Considered and kept, not deferred.

</specifics>

<deferred>
## Deferred Ideas

### VPP-reroute confirmation gate for parts needing JP4's third position

Operator-raised during Area 1, and out of this phase's domain — a different hazard on a different jumper.
Captured with the facts that change its shape, all measured in Phase 182:

- **Socket pin 25 is confirmed** — `182-06-SUMMARY.md`: *"The pole toward the board periphery (board +Y)
  reaches socket pin 25 — the periphery-facing pole, the 24-pin destination."* Bench-probed on the
  operator's Rev 2.2. The affected parts are the TI 2516/2532 family.
- **"If HW < 2.2, ask" is NOT decidable today.** Same summary: `firestarter hw` reports a **bucket**, and
  `Rev 2.0-class` **spans 2.0 / 2.1 / 2.2**. The host cannot tell a Rev 2.2 from a Rev 2.0, so the gate
  must prompt whenever the revision is not provably ≥ 2.2 — i.e. always on Rev 2.x. That is `jp5_gate`'s
  warn-never-detect shape, and the opposite of what a revision check implies.
- **The affected-part predicate does not exist, and D-4 forbids a hand list.**
  `.planning/seeds/rev22-3pin-header-2516-family-support.md` records that the 2516 family is
  indistinguishable from ordinary 24-pin EPROMs by *every* existing DB field — `pin_count` 24, `vpp`
  25 V, `pinout` collides with `DIP24_2716`, `algorithm` `0x0B`. A database-derived predicate needs that
  seed's blocker 1 first: a new per-chip field in `build_db.py`, since it cannot come from `infoic.xml`.
- **The operator's escape hatch, to be preserved:** early boards may work with a hand-soldered wire to
  the right pin, so the gate must offer **proceed-anyway**, never a hard refusal.
- **Cross-refs:** `.planning/seeds/rev22-3pin-header-2516-family-support.md`, `.planning/ROADMAP.md`
  Phase 999.58, `.planning/todos/pending/` (the JP4-third-position recording todo).

### Generalize the refusal beyond flash4

D-05's other half. `eprom_erase`'s bare `Not supported` also fires for UV-EPROM, SRAM and `0x0D`
electrical-type outliers. The design is already done and should be named in the backlog entry: reuse
`chip_test.py`'s existing per-family reason strings so `erase` and `dev test` say the same thing about the
same chip.

### Software chip-erase for the `0x05` family

D-20. A new firmware capability, excluded by this milestone's boundary and by Leonardo's 0 B headroom.
Template: `eeprom28c_erase_execute`'s AN-0544B six-byte sequence, 0 B RAM via inline literal writes.
Would make `erase AE29F2008` actually work rather than refuse — which reverses SAFE-06, so it needs an
explicit operator scope decision, not a quiet follow-on.

### `vpp_mv: 12000` on a 5 V-only part

D-23. Filed here so it is not lost if research finds the field inert. If research finds it **live**, it is
a new defect and needs its own scope decision.

### Reviewed Todos (not folded)

`todo.match-phase 183` returned **35 candidates and no genuine matches** — every one scored on generic
keywords (`firestarter`, `phase`, `safe`, `cmd`) rather than on this phase's subject. None folded. The
single nearest-adjacent item, *"FM28V020 and MB85R256H (FRAM) ride the 0x0D EEPROM handler by pinout
promotion — a classification…"*, is a classification concern in a **different** family (`0x0D`, not
`0x05`) and stays out.

</deferred>

---

*Phase: 183-Flash4 Erase Refusal & the AE29F2008 Classification*
*Context gathered: 2026-09-11*
