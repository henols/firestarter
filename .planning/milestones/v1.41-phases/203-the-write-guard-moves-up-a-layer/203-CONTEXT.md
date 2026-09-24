# Phase 203: The write guard moves up a layer - Context

**Gathered:** 2026-09-21
**Status:** Ready for planning

<domain>
## Phase Boundary

`firestarter write` gains two things: a **host-side pre-write blank guard** that refuses a write to a
non-blank part before any programming byte reaches the wire, and an opt-in **`--verify`** that
read-back-compares the written region through Phase 202's engine.

**Nothing leaves the firmware in this phase.** The firmware's own write-init pre-flights still run —
harmlessly redundant for one phase — and only Phase 205 removes them. The roadmap states this as a
safety property, not a preference: the host gains each capability *before* the firmware loses it.

**This phase is app-only and bench-no**, exactly as the roadmap scopes it. No firmware file is
modified. Firmware source is read as evidence only.

**Not in this phase:** removing `FLAG_SKIP_BLANK_CHECK`, `mem_util_blank_check*` or
`MSG_ERR_NOT_BLANK` (Phase 205); the serial session lease (Phase 206, SESS-01); making `--verify` the
default (REQUIREMENTS D-3); wiki documentation of the new surfaces (REL-04, Phase 207).

</domain>

<decisions>
## Implementation Decisions

### The exemption predicate — who pays the read

- **D-01:** **The guard's coverage is defined by what the firmware pre-flights today, not by
  `FLAG_CAN_ERASE` alone.** This was measured across every firmware write-init path during
  discussion, and the literal requirement text does not survive the measurement:

  | Protocol | firmware write-init blank check today | host `FLAG_CAN_ERASE` |
  |---|---|---|
  | `0x07` / `0x08` / `0x0B` UV EPROM | **yes**, region-scoped (`eprom.cpp:144-145`, Phase 201) | clear, except W27C512-class `EEPROM` rows |
  | `0x06` NOR unlock | **yes**, whole-device, after an erase (`flash_nor_unlock.cpp:104-105`) | set |
  | `0x10` Intel flash | **yes**, whole-device, after an erase (`flash_intel.cpp:94-95`) | set |
  | `0x05` flash4 (+ `0x35`/`0x39`) | **no** — auto-erases per page (`flash_5v_page.cpp:73-77`) | **deliberately cleared** |
  | `0x0D` 28C parallel | **no** — auto-erases per page (`eeprom_28c.cpp:379-384`) | set |
  | `0x0E`/`0x27`/`0x28`/`0x29` SRAM | **no** — no blank state exists | clear |

  A literal `FLAG_CAN_ERASE`-only exemption would make the host start refusing non-blank writes on
  **protocol 0x05 and on every SRAM/FRAM part** — families the firmware has never checked. The 0x05
  flag is cleared for a hardware-safety reason (`database.py:575-580`: setting it routes a 12 V bulk
  erase onto a 5 V-only part), so it can never be used as a blank-state signal.

  **The guard therefore applies to exactly: `0x07`, `0x08`, `0x0B`, `0x06`, `0x10`** — and within
  those, a part whose erase actually ran is exempt. SRAM/FRAM and `0x05` are **named** exemptions
  with their reasoning at the site, not accidents of a flag test.
  — **Reversibility:** costly — the predicate is the whole safety net after Phase 205, and its test
  is the only thing that detects a later drift.

- **D-02:** **WRITE-02 must be amended before planning**, the same way CMP-04 was amended during the
  Phase 202 discussion. As written it says "a test fails if the exemption widens beyond
  `FLAG_CAN_ERASE`". D-01 exempts two families that flag does not cover. The replacement obligation
  is **stronger, not weaker**: the test pins the **exact guarded set** and fails if it **narrows or
  widens**. Amend both `.planning/REQUIREMENTS.md` WRITE-02 and `.planning/ROADMAP.md` Phase 203
  success criterion 2, which carries the same wording.

- **D-03:** **`--skip-erase` re-arms the guard on an erase-capable part.** The exemption's whole
  premise is "the erase immediately above the check already guarantees blank". `--skip-erase` makes
  that premise false while leaving `FLAG_CAN_ERASE` set. The firmware behaves this way today —
  `flash_nor_unlock.cpp:93-105` and `flash_intel.cpp:91-95` both gate the erase on
  `!FLAG_SKIP_ERASE` and then blank-check regardless — so guarding here **preserves** behaviour.
  This narrows the exemption, which D-02's test permits by construction.

- **D-04:** **The guard reads the write's region only, on every guarded family.** `address` →
  `address + len(input_file)`. This matches Phase 201 and WRITE-06, and it deliberately **diverges
  from** `flash_nor_unlock.cpp` / `flash_intel.cpp`, which blank-check the whole device today. That
  divergence is an improvement and lands the host half of the pending todo
  `2026-08-30-write-init-blank-check-is-whole-device.md` (filed against Phase 205). Record it as a
  deliberate, measured improvement in the phase record — not as an incidental difference.

- **D-05:** **An unclassifiable part is guarded, not exempted.** A wire dict with no `algorithm` key
  or an unrecognised protocol id **fails closed** — it gets the read. This follows
  `jp5_gate.require_acknowledged` and `sdp_capability`, and deliberately **not**
  `flash4_erase_gate.is_flash4`, whose docstring argues the opposite polarity for its own case.
  The reason the polarities differ must be stated at the site: `flash4_erase_gate` guards an
  *availability* property (refusing an unclassifiable part breaks `erase` for it), this guard is the
  *whole safety net* after Phase 205, and its worst case is an unnecessary read plus a refusal the
  operator clears with `-b`.

- **D-06:** **The policy lives in a new pure-predicate module**, following the four in-repo siblings
  `jp5_gate.py`, `flash4_erase_gate.py`, `sdp_capability.py` and `page_size_gate.py`: a wire dict in,
  a decision out, no I/O, no serial, no environment reads. The reasoning for each carve-out lives in
  that module; the pinning test asserts the exact guarded set without a board. Reuse
  `flash4_erase_gate.FLASH4_PROTOCOL_ID` rather than introducing a second 0x05 constant — that module
  already exists precisely so the 0x05 protocol id and `database.py`'s `algo not in (5,)` exclusion
  share one source of truth.
  — **Reversibility:** reversible — a module boundary, not a contract.

### Where the guard runs

- **D-07:** **The guard lives inside `EpromOperator.write_eprom`** (`eprom_operations.py:2080`), not
  in `cli_handlers.write`. Every caller inherits it, which is where the firmware guard has always
  sat. Consequences, all verified during discussion:
  - `dev write-cycle` (`eprom_operations.py:1302-1305`) erases before every write → exempt.
  - `dev test` (`chip_test.py:3221`) already passes `FLAG_SKIP_BLANK_CHECK` for its monotonic-masked
    UV targets, so **its UV write shortcut keeps working unchanged** provided the guard honours that
    flag host-side — which WRITE-03 requires anyway.
  - The `dev test`-vs-`write` divergence described in the pending todo
    `2026-09-08-uv-write-shortcut-disclosure-key.md` is thereby **preserved exactly**, neither
    widened nor closed. That todo stays open and unfolded.

- **D-08:** **The guard runs after every pure pre-connect gate and before the write's own
  `_operation_context`.** The existing order in `write_eprom` is `require_acknowledged` (JP5 pin-1
  hazard) → `require_page_size` → `require_page_alignment` → `os.path.getsize` → connect. The guard
  is a serial operation, so it cannot join the pure gates; it sits immediately after them, so a part
  that will be refused on a pure ground is never read first.

- **D-09:** **`-f`/`--force` does not bypass the guard.** `--force` forces past a chip-ID or VPP
  mismatch and has never bypassed the blank check. `-b`/`--no-blank-check` is the documented way
  past it, per WRITE-03. Preserving today's behaviour.

### The refusal

- **D-10:** **Host-voiced, one line, no remedy clause, address and value included.** Shape:
  `Refusing write to W27C512: not blank at 0x008000, v: 0xAB.` — exact wording and capitalisation are
  Claude's discretion within that content. Three properties are decided:
  - It names the **host** as the refuser, so an operator cannot mistake it for a programmer fault.
  - It carries the **first non-blank address and its value**, as WRITE-01 requires. This is a
    deliberate, recorded exception to Phase 202's D-13 ("no expected or actual byte values are
    printed"), which governs *compare* output. A blank-guard refusal is not a compare report, and
    the value is the same evidence the firmware's `MSG_ERR_NOT_BLANK` has always carried
    (`Not blank, at 0x%06x, v: 0x%02x`, `tools/catalog/messages.toml:556-565`).
  - It carries **no remedy clause** — no mention of `-b`. This follows
    `flash4_erase_gate.refusal_text`'s stated reasoning: an operator who reads the way out at the
    refusal site can route around a correct refusal.

- **D-11:** **The refusal prints that line and nothing else.** The guard drives the same
  `CompareAccumulator` as `verify`, so it *could* emit 202's `Mismatch 0xSTART-0xEND (N bytes)` range
  line and its bucket summary. It does not. The guard aborts at the first non-blank byte, so the
  range is always one byte and the bucket would be classified from a one-byte sample — the worst case
  of the confident-verdict-from-a-short-prefix trap 202's D-09 already named. Terse output is also a
  standing operator preference (v1.40 Phase 200 UAT, commit `b3a777e`).

- **D-12:** **The refusal text belongs in the predicate module**, built from a format constant so a
  test asserts the exact sentence rather than a substring of a log line —
  `flash4_erase_gate.refusal_text`'s shape.

### `write --verify`

- **D-13:** **`--verify` opts the invocation into Phase 202's `0` / `1` / `2` exit-code contract;
  plain `write` keeps `0` / `1` unchanged.** *(Operator answered "you decide"; decided by Claude with
  the reasoning recorded here.)* Phase 202's D-11 declined to change `write`'s exit codes because no
  requirement covered them — WRITE-05 now covers the `--verify` path and nothing covers plain
  `write`. So:
  - `firestarter write …` with no `--verify`: unchanged. A guard refusal exits **1**, exactly as the
    firmware refusal does today (`cli_handlers.py:793`, `sys.exit(0 if ok else 1)`). A transport
    failure exits 1, as today.
  - `firestarter write … --verify`: **0** verified, **1** write failed or comparison mismatched,
    **2** transport or hardware failure anywhere in the invocation, including the guard read.
  - The cost — one command with two contracts — is accepted and **must be stated in the `--verify`
    help text**, so it is documented rather than folklore.
  — **Reversibility:** one-way — exit codes are a published CLI contract, and REL-04 will document
  them in the wiki.

- **D-14:** **One combined verdict line under `--verify`; the word "successful" never appears on a
  `--verify` run.** `--verify` suppresses the plain `Write to X successful (t).` line and prints a
  single terminal line for the whole operation — verified / landed-but-did-not-verify / failed. This
  satisfies WRITE-05 structurally: the forbidden word is absent from the path, so a later edit to one
  of the two failure lines cannot reintroduce it. Exact wording is Claude's discretion; the
  three-way distinction is not.

- **D-15:** **`write --verify` accepts `--full`, with the same meaning it has on `verify` and
  `blank`** — scan the whole written region and report every coalesced mismatching span, rather than
  stopping at the first. A half-landed write is exactly the case that needs it, and
  `_drive_region_compare` already supports both modes through one parameter.

- **D-16:** **`--verify` compares the written region only** — the same `address` → `address + len`
  region the write touched and the guard read. Not the whole chip.

### Session cost

- **D-17:** **Three open/reset cycles per guarded `write --verify` are accepted for this phase, and
  the added wall-clock is measured and recorded.** `_operation_context` disconnects in its `finally`
  and every operation opens its own port, so guard-read + write + verify-read is three port opens,
  each resetting an Uno-class board. Phase 206's SESS-01 owns collapsing them. **203 must record the
  measured added wall-clock in its phase record**, so Phase 206's SESS-02 ("measure the saving; if it
  does not pay for the structural change, revert it and record that") has a real before-figure
  instead of inventing its own baseline.

### Claude's Discretion

- Exact wording and capitalisation of the refusal line (within D-10's content) and of the three
  `--verify` verdict lines (within D-14's three-way distinction).
- The predicate module's name, and whether the guarded set is expressed as a protocol allowlist or as
  a named predicate over the wire dict — provided D-02's pin-the-exact-set test holds.
- Whether the guard read shows a progress bar.
- Whether the measured session cost in D-17 is taken from a bench run or a harnessed
  connect-cost measurement (`tests/test_connect_cost_harness.py` exists).
- The mechanism of the refusal — a typed exception through `map_typed_errors` (the shape the four
  sibling gates use) versus a `False` return — provided D-13's exit codes come out right.

### Folded Todos

- **`2026-09-16-reject-negative-write-start-address.md`** (`area: both`, `resolves_phase: null`) —
  `firestarter write W29C020 <file> -a -256` exits 0 today. Two independent behaviours combine:
  `address_parser.parse_address` does not reject a negative string, and Python's `%` makes
  `-256 % 256 == 0` read as **aligned** in `page_size_gate.require_page_alignment`. The firmware does
  not catch it either — `json_parser.c`'s `simple_strtoul` consumes only `[0-9]`, so a leading `-`
  makes the loop body never run and the address silently becomes 0. Recorded in code review as
  WR-01 and accepted as debt at the Phase 195 UAT checkpoint.
  **Why it fits here:** this phase rewires the write path's region arithmetic — the guard and
  `--verify` both derive their region from the same `address` and file length — and a negative start
  address would make both of them compute a region that is not the one the firmware writes.
  **Scope note:** fold the **host half only**. The firmware half (`simple_strtoul`) is a
  `firestarter_fw` change and this phase is app-only and bench-no; leave the todo open for its
  firmware half, or hand it to Phase 205, which is already dual-repo.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

The ROADMAP.md Phase 203 entry carries no explicit `Canonical refs:` line; this list was accumulated
during analysis and discussion.

### Milestone scope and locked decisions
- `.planning/ROADMAP.md` lines 175-315 — the v1.41 milestone section and the Phase 203 detail block.
  Read the **"Two removals, not one" (D-1)**, **"What must NOT be removed" (D-7)** and **"What
  replaces the device-side refusal" (D-2)** paragraphs, and the **"Ordering is a safety property"**
  paragraph, which is why the firmware pre-flight still runs during this phase.
  **D-02 above requires success criterion 2 to be amended here before planning.**
- `.planning/REQUIREMENTS.md` — WRITE-01…WRITE-06, activation decisions D-1…D-7, the Out of Scope
  table. **D-02 above requires WRITE-02 to be amended here before planning.**

### Phase 202's output — this phase's engine
- `.planning/phases/202-one-comparison-engine-on-the-host/202-CONTEXT.md` — **read in full.** D-01
  (the module boundary), D-05 (compare and render separated *specifically so this phase can use it*),
  D-10/D-11 (exit codes and their deliberate scoping away from `write` — D-13 above widens that by
  one command), D-13/D-14 (output shape), D-16 (the range cap).
- `.planning/phases/202-one-comparison-engine-on-the-host/202-READ-ABORT-ANSWER.md` — the abort
  mechanism, its measured ≤1 s per-abort cost, and the four-condition discrimination
  `write --verify` will drive again.
- `.planning/phases/202-one-comparison-engine-on-the-host/202-VERIFICATION.md` and `202-REVIEW.md` —
  what was actually delivered and the three findings filed against it.

### Provenance
- `.planning/todos/pending/2026-09-16-reject-negative-write-start-address.md` — folded, host half
  only. See Folded Todos above.
- `.planning/todos/pending/2026-08-30-write-init-blank-check-is-whole-device.md`
  (`resolves_phase: 205`) — **not folded**, but D-04 lands its host half. Read it before writing the
  region logic.
- `.planning/todos/pending/2026-09-08-uv-write-shortcut-disclosure-key.md` — **not folded.** Read it
  to confirm D-07 preserves the divergence rather than changing it.

### Repository rules that bind this phase
- `firestarter_app/CLAUDE.md` — § "What CI runs": `ruff` scope is `E,F,I,UP` (a `# noqa` for anything
  else is inert), the mypy strict module list in `pyproject.toml` **includes `cli_handlers`**, and
  the 70% coverage floor. Plus the standing warning that **a push to `beta` publishes to PyPI**.
- `firestarter_fw/CLAUDE.md` — read only for protocol context. **No firmware change is in scope.**
- `/workspaces/CLAUDE.md` — § "Milestone close and branch protection". Milestone work forks off
  `beta`; never commit to `beta` or `main`. Current branch is `v1.41-verification-to-host`.

### Host source this phase changes
- `firestarter_app/firestarter/eprom_operations.py:2080-2229` — `write_eprom`. The guard goes here
  (D-07), after `require_page_alignment` and before `_operation_context` (D-08).
- `firestarter_app/firestarter/eprom_operations.py:2230-2334` — `_drive_region_compare`. **Reuse
  unchanged for both the guard read and `--verify`.** Its `expected` pull callback is
  `lambda _addr, n: b"\xff" * n` for the guard; `--verify` seeks the input file, exactly as
  `verify_eprom` does.
- `firestarter_app/firestarter/cli_handlers.py:733-793` — the `write` command, its options and its
  `sys.exit(0 if ok else 1)`. Gains `--verify` and `--full`.
- `firestarter_app/firestarter/cli_handlers.py:796-…` — `_region_refusal_exit_code`, the pre-port
  region refusal `verify`/`blank` already use. Consider it for `--verify`'s region checks.
- `firestarter_app/firestarter/address_parser.py` — `parse_address`, for the folded negative-address
  todo.
- `firestarter_app/firestarter/page_size_gate.py` — `require_page_alignment`'s modulo check, same
  todo.

### Source read as evidence for D-01 (not modified)
- `firestarter_app/firestarter/database.py:553-581` — the `FLAG_CAN_ERASE` derivation and the
  algorithm-5 exclusion, with the live 12 V-on-a-5 V-part argument. **Read the whole comment block.**
- `firestarter_app/firestarter/flash4_erase_gate.py` — `FLASH4_PROTOCOL_ID`, the fail-open reasoning
  D-05 deliberately departs from, and `refusal_text`'s no-remedy reasoning D-10 follows.
- `firestarter_app/firestarter/chip_test.py:210-226` — why `FLAG_CAN_ERASE` is cleared for 0x05.
- `firestarter_fw/include/proto_constants.h` — the protocol id constants.
- `firestarter_fw/src/proms/memory.cpp:47-110` — `configure_memory`, the protocol → handler dispatch.
- `firestarter_fw/src/proms/eprom.cpp:130-147`, `flash_nor_unlock.cpp:73-107`,
  `flash_intel.cpp:70-97`, `flash_5v_page.cpp:68-77`, `eeprom_28c.cpp:379-385` — the five write-init
  paths the D-01 table is derived from.
- `tools/catalog/messages.toml:556-565` — `MSG_ERR_NOT_BLANK`'s format string, the wording D-10
  departs from.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`_drive_region_compare`** (`eprom_operations.py:2230`) — built in 202-05 as the one shared compare
  drive. Takes an `expected(offset, length) -> bytes` pull callback, a `full` switch and a
  `region_length`; returns `0`/`1`/`2`. It already does read → stream-compare → abort-on-first-
  mismatch → D-08 abort-vs-fault discrimination → D-13/D-14 rendering. **Both** of this phase's reads
  are one call each. 202's D-05 says in as many words that this shape exists for Phase 203.
- **`compare.py`** — `CompareAccumulator`, `CompareResult`, `MismatchRange`, `Fingerprint`,
  `render_compare_lines`. Import-light by design; importing it from a new predicate module or from
  `write_eprom` costs nothing new.
- **The four sibling gates** — `jp5_gate.py`, `flash4_erase_gate.py`, `sdp_capability.py`,
  `page_size_gate.py`. D-06's module is the fifth, and `flash4_erase_gate` is the closest analogue:
  same protocol-id input, same one-line refusal, opposite fail polarity (D-05).
- **`tests/fake_chip.py`** — `FakeChip` models UV physics (a write ANDs into existing content) and
  absolute-offset reads. This is the bench-free harness WRITE-06 and criterion 5 need.

### Established Patterns
- **Pure predicate modules carry their own reasoning and their own refusal string**, and are tested
  without a board. All four siblings do this; `flash4_erase_gate.refusal_text` is built from a format
  constant precisely so a test can assert the whole sentence.
- **`@map_typed_errors` + `sys.exit(0 if ok else 1)`** is the shape of every chip-op command.
  `verify` and `blank` are the two deliberate departures (202 D-10/D-11); `write --verify` becomes the
  third (D-13).
- **Every operation opens and closes its own port.** `_operation_context`'s `finally` calls
  `_disconnect_programmer`, which sets `self.comm = None`. Anything that must read `self.comm` — as
  the `--skip-sdp-unlock` ack check does — has to do it inside the `with`.

### Integration Points
- `cli_handlers.write` gains `--verify` and `--full`; `_build_op_flags` is unchanged (the guard reads
  `operation_flags & FLAG_SKIP_BLANK_CHECK`, which `-b` already sets).
- `chip_test.py`'s `OP_WRITE` / `OP_WRITE_PARTIAL` call sites (`chip_test.py:3228`, `:3482`) inherit
  the guard through `write_eprom` and are expected to be **behaviourally unchanged** — proving that
  is part of the work, not an assumption.
- `MSG_ERR_NOT_BLANK` (`0xB0`) stays in place and stays emitted by the firmware for one more phase.
  Nothing in 203 retires it.

### Known traps that apply here
- **`write --help` is pinned by TWO full-text syrupy snapshots** — `test_help_write` and
  `test_no_blank_check_polarity`, both in `tests/__snapshots__/test_characterization.ambr`, each
  carrying the entire help output including the whole docstring. Adding `--verify` and `--full`
  changes both. **Never `--snapshot-update`; hand-edit with the diff shown.**
- **The `write` docstring currently states**: "On protocols 0x0D and 0x05 the write path performs no
  pre-write blank check at all, so -b is a no-op on those families." Under D-01 that sentence stays
  **true** (0x05 and 0x0D remain unguarded) — but it now describes a host policy, not a firmware one,
  and its wording should be re-read rather than assumed still accurate.
- **`tests/fake_chip.py`'s `WriteInitPreflightChip` (line 253) overrides `EpromOperator.write_eprom`
  wholesale** to model the firmware pre-flight — which is exactly the method the guard now lives
  inside. **Every test using that double will pass regardless of what the real guard does.** WRITE-06
  requires a test that "exercises the host path and fails if the host refuses a blank region on a
  non-blank part"; that double cannot provide it. Raised during discussion and deliberately left to
  the researcher and planner to shape — but it is **real work, not a rename**, and must not be
  assumed easy. The same applies to criterion 1's "before the port carries a programming command",
  which needs a wire-level ordering assertion.
- **`mypy` is strict on `cli_handlers`** (see the override list in `pyproject.toml`). New options and
  the exit-code path must be fully typed.
- **Run the suite on Python 3.11**, not the devcontainer default — a green local run on a later
  interpreter has broken app CI before.
- **`ruff`'s selection is `E,F,I,UP`.** A `# noqa` for any other code is inert.
- **Comments in product source are allowed again** — the no-comments rule was removed on 2026-09-19.
  D-01, D-03, D-05 and D-10 each describe reasoning that belongs at its site in the code, and WRITE-02
  requires it.

</code_context>

<specifics>
## Specific Ideas

- The operator chose **"preserve today's coverage"** over both the literal requirement text and a
  flag-plus-carve-outs formulation. The instruction behind it: the guard must not start refusing
  writes that work today. Any later simplification that widens the guarded set is a regression, not a
  tidy-up.
- The operator chose **region scoping on every family**, knowingly diverging from the firmware's
  whole-device check on 0x06 and 0x10, and accepting that this lands part of a Phase 205 todo early.
- The operator chose a **host-voiced refusal over preserving the firmware's greppable string**. The
  operator wants it unmistakable that the *host* refused.
- The operator chose **one combined verdict line** over keeping the existing success line plus a
  second verify line — consistent with the standing terse-output preference (v1.40 Phase 200 UAT
  rejected a multi-line warning for a one-line form, commit `b3a777e`).
- The operator declined to pre-empt Phase 206's session lease, and asked instead that the cost be
  **measured**, so 206 inherits a real number.

</specifics>

<deferred>
## Deferred Ideas

- **Collapsing the three port opens into one leased session.** Offered and declined for this phase.
  **Best home: Phase 206**, SESS-01, which already owns it. D-17 requires 203 to hand it a measured
  baseline.
- **The firmware half of the negative-address todo** (`json_parser.c`'s `simple_strtoul` dropping the
  sign). Out of scope here — this phase is app-only and bench-no. **Best home: Phase 205**, already
  dual-repo and bench-gated.
- **CLI-wide exit-code consistency.** D-13 widens the `0`/`1`/`2` contract to a third command path.
  The other ~20 commands still exit 1 for a transport or hardware failure. Carried forward from
  Phase 202's deferred list, still backlog.

### Reviewed Todos (not folded)

- `2026-09-08-uv-write-shortcut-disclosure-key.md` — the `dev test`-vs-`write` UV divergence. D-07
  **preserves it exactly** rather than changing it, so there is nothing for this phase to close. It
  becomes actionable when the harness and the product path are reconciled, which is Phase 206's
  territory.
- `2026-09-20-compare-accumulator-empty-offsets-branch-is-dead.md` (202-REVIEW IN-01) — dead branch in
  `CompareAccumulator.feed()`. Not folded; a `compare.py` cleanup with no bearing on WRITE-01…06.
- `2026-09-20-read-abort-window-untested-at-its-boundary.md` (202-REVIEW WR-01) — the 3.0 s
  `READ_ABORT_ACCEPTANCE_WINDOW_S` untested at its true failure boundary. Not folded, but
  `write --verify` drives that same discrimination, so a boundary failure would now surface on the
  write path too. Worth the planner's awareness even though it is not in scope.
- `2026-08-30-write-init-blank-check-is-whole-device.md` (`resolves_phase: 205`) — not folded, but
  D-04 lands its host half. Its firmware half stays with Phase 205.

`todo.match-phase 203` returned 45 of 48 pending todos, almost all on broad keyword overlap
(`write`, `host`, `check`, `phase`). Only the four above and the one folded had real scope overlap.

</deferred>

---

*Phase: 203-The write guard moves up a layer*
*Context gathered: 2026-09-21*
