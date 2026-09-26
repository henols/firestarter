# Phase 202: One comparison engine, on the host - Context

**Gathered:** 2026-09-20
**Status:** Ready for planning

<domain>
## Phase Boundary

`firestarter verify <chip> <file>` and `firestarter blank <chip>` stop sending `CMD_VERIFY` (6) and
`CMD_BLANK_CHECK` (4). They issue `CMD_READ` instead and compare on the host, chunk by chunk as the
data arrives, through **one** streamed implementation shared with Phase 203's `write --verify` and
Phase 206's `dev test`. A failed compare names one of `classify_fingerprint`'s honest buckets with
total and bad counts, instead of a single address.

**Nothing leaves the firmware in this phase.** Criterion 1 requires the host half to work against
firmware that still carries both command ordinals, without sending either — the ordering is a safety
property, not a preference. The removals are Phase 204 (command surfaces) and Phase 205
(in-algorithm pre-flights).

**This phase is app-only and bench-no**, exactly as the roadmap scopes it. The abort decision below
was taken specifically to keep it that way.

</domain>

<decisions>
## Implementation Decisions

### The comparison engine

- **D-01:** The engine lives in a **new module, `firestarter_app/firestarter/compare.py`**. It must
  be import-light in the same sense `chip_test.py` already is: no dependency on
  `eprom_operations.py` and no dependency on `chip_test.py`. `eprom_operations` imports it for
  `verify`/`blank`, `chip_test` imports it for `classify_fingerprint`, and Phase 203's write guard
  imports it too. Rejected: putting it in `eprom_operations.py` (would force `chip_test` to import
  a 2502-line module that pulls `serial_comm`, breaking the import-lightness its own comment at
  `chip_test.py:113-117` protects) and putting it in `chip_test.py` (would give every `verify` and
  `blank` a new import of a 3774-line module that pulls `chip_resolver` → `database`).
  — **Reversibility:** costly — moving it later rewrites every import site in
  `eprom_operations.py`, `chip_test.py` and Phase 203's and 206's new code.

- **D-02:** The engine is a **streaming accumulator, and the existing
  `classify_fingerprint(expected, actual, *, repeat_divergent, addr_base)` is reimplemented to
  delegate to it.** There must be exactly one divergence implementation — `chip_test.py:113-117`
  states that rule explicitly and it is binding here. Every input `classify_fingerprint` needs
  composes online: `cmp_len`, `bad`, `ff_count`, `first_offset` and the per-bit `set_count` used for
  address-line clustering are all running counters. The single thing that must **not** survive is
  `_diff_offsets`' materialised list of every mismatching offset — that list is precisely what
  CMP-03 forbids.
  — **Reversibility:** costly — `dev test` consumes `Fingerprint` through this function and
  DEVTEST-03 forbids its meaning drifting.

- **D-03:** **A corpus equality test pins the refactor.** The new streamed path must produce
  `Fingerprint` values identical to today's batch implementation across a corpus spanning all five
  buckets. This is the only thing that actually protects DEVTEST-03 in Phase 206; an eyeballed
  refactor does not.

- **D-04:** The **expected side is supplied by a pull callback**, `expected(offset, length) ->
  bytes`. `verify` seeks the input file; `blank` returns `b"\xff" * length`. `blank` must never
  allocate a device-sized constant buffer. This is the matching half of
  `_main_phase_read_data`'s existing `(address, payload)` push callback.

- **D-05:** **Design the interface for all three consumers now**, not just `verify`/`blank`.
  Phase 203 needs a region compare against a just-written buffer; Phase 206 needs the `Fingerprint`
  object rather than printed output. So **"compare and return a structured result" is separated from
  "render a report"** from the start. The widening is near-certain, not speculative — 203 is the
  very next phase.

### Aborting the read in flight (success criterion 5)

- **D-06:** **The host aborts by stopping its acks. App-only; no firmware change.** This was
  researched during discussion and the mechanism is confirmed to work within the existing protocol,
  unchanged:
  - The read path acks every chunk — `_process_outgoing_data` calls `op_wait_for_ack(handle)` at
    `firestarter_fw/src/eprom_operations.cpp:170`.
  - `op_wait_for_ack` (`firestarter_fw/src/operation_utils.cpp:94-108`) accepts only `OP_MSG_ACK`,
    fails on `OP_MSG_ERROR`, and otherwise spins to a 1000 ms timeout, emitting `MSG_ERR_TIMEOUT`
    and returning false.
  - That false propagates to `eprom_read` returning `finished`, and `loop()` then runs
    `command_done()` (`firestarter_fw/src/firestarter.cpp:208-217`), which disables the chip, zeroes
    the control and both address registers, sets `cmd = CMD_IDLE` and restores communication mode.
    **The port is left clean.**
  - Cost: up to 1 s of firmware timeout per abort.

  Rejected: sending `"DONE"` mid-read. `op_get_message` already parses it into `OP_MSG_DONE`
  (`operation_utils.cpp:131-139`) but `op_wait_for_ack` ignores that case, so making it a clean stop
  is a one-line firmware change — which would put firmware work into an app-only, bench-no phase.
  Filed as a deferred idea for Phase 204.
  — **Reversibility:** reversible on the host side; the deferred firmware variant is purely additive.

- **D-07:** **Criterion 5 is answered affirmatively: the default's saving is temporal, not merely
  diagnostic.** The roadmap's "Known open mechanic" assumed the END phase had to run to leave the
  port clean. That assumption is wrong in the way that matters — `command_done()` is what performs
  the teardown, and it runs on the error path too. On a 512 KB part the host stops after the first
  mismatch instead of draining tens of seconds of read. **This finding must be written into the
  phase record; it corrects the roadmap's stated premise and it is what CMP-F1 was filed against.**

- **D-08:** **The host must not mistake its own abort for a fault.** The deliberate stop produces an
  `MSG_ERR_TIMEOUT` frame indistinguishable on the wire from a genuine timeout. The host sets an
  intent flag before it stops acking and accepts **only** `MSG_ERR_TIMEOUT`, **only** within a
  bounded window after that stop, as its own doing. Any other error id, or one outside the window,
  is a real fault and takes the exit-2 path (D-11).

- **D-09:** **The default's fingerprint is computed over the compared prefix and is always printed
  with that range explicit.** Aborting means the default only ever sees a prefix, and
  `classify_fingerprint` checks `blank/contact` first on an `0xFF` ratio ≥ 0.98 — so a short mostly-
  `0xFF` prefix could otherwise return a confident whole-chip-sounding verdict from a truncated
  sample. Printing the compared range alongside the bucket makes the number unmistakable. Rejected:
  suppressing confident buckets on partial compares (throws away a real signal when the prefix is
  large) and omitting the bucket on the default path (reads against CMP-06 and criterion 4).

### Exit codes

- **D-10:** **`0` match / `1` mismatch / `2` transport-or-hardware trouble.** This is `diff(1)` and
  `cmp(1)`'s contract verbatim, and it is already the in-repo precedent —
  `consistency_check_eprom` returns `2` for hardware error. Accepted cost: Click's `UsageError` also
  exits 2, so a mistyped flag and a dead board share a code on these two commands.
  — **Reversibility:** one-way — exit codes are a published CLI contract; anything scripting against
  them breaks on a change, and REL-04 will document these in the wiki.

- **D-11:** **Scoped to `verify` and `blank` only.** `map_typed_errors`
  (`firestarter_app/firestarter/cli_handlers.py:190-229`) is shared by every chip-op command and
  turns every typed error into a `ClickException` → exit 1. Do **not** change it globally: that
  would silently alter the exit code of ~20 commands, `write` included, with no requirement covering
  it. Implement the exit-2 path for these two commands only. The CLI-wide inconsistency is filed as
  a deferred idea.

- **D-12:** **`blank` on an SRAM/FRAM part becomes an exit-2 refusal, not an exit-1 "not blank".**
  The short-circuit at `eprom_operations.py:2325-2343` returns `False` today, which reports "not
  blank" for a part that has no blank state. It stays a pre-wire short-circuit with its existing
  warning; only the exit code changes. Safe to change: `derive_plan` already marks SRAM/FRAM
  blank-check NA up front (`chip_test.py:341-348`) and never reaches this code, so `dev test` is
  unaffected.

### Output

- **D-13:** **One line per mismatching range: `Mismatch 0xSTART-0xEND (N bytes)`. No expected or
  actual byte values are printed.** Operator decision, taken with the CMP-04 conflict stated. The
  default produces exactly one such line; `--full` repeats it per coalesced range. One format, both
  modes.

- **D-14:** **One bucket summary line after the range lines**, carrying the classification, the bad
  count, the compared count and the region total — e.g.
  `address-line, 2305 bad of 65536 compared of 65536`. This is what keeps CMP-06 and criterion 4
  met, and it is the diagnosis the whole milestone exists for.

- **D-15:** **CMP-04 has been amended — DONE, do not repeat.** As written it required "its absolute
  address, the expected value and the value read", which D-13 deliberately drops. Both contradicting
  texts were reworded during this discussion session, in commit `81414f98`:
  - `.planning/REQUIREMENTS.md` CMP-04 — now asks for a single `start–end` range with a byte count
    and no byte values, citing D-13.
  - `.planning/ROADMAP.md` Phase 202 success criterion 3 — carried the same contradiction and was
    amended identically.

  Checked and **not** amended: CMP-05's coalesced `start–end` + byte-count phrasing already matches
  D-13, and CMP-07 is unaffected — it says a transport failure must be "distinguishable" from a
  mismatch without prescribing how, which D-10's exit 2 satisfies.

- **D-16:** **`--full`'s retained range list is capped at a named constant N; the counts stay
  exact.** Past N, ranges stop being retained and a tail line reports `… and M more ranges, K bytes`
  computed from running counters, never from a list length. `--full` does not abort, so a badly
  failing 512 KB part can genuinely produce ~262144 coalesced ranges — this is the case CMP-03's
  "bounded independently of device size" has to survive, in both memory and output volume. Phase 206
  receives the same capped list plus the honest totals.

### Region resolution

- **D-17:** **Explicit wins; conflicts refuse, before the port opens.** `--size` wins when given.
  Without it, `verify`'s region is the input file's length (as today, via
  `os.path.getsize` at `eprom_operations.py:2157-2160`) and `blank`'s is the whole chip. A file
  shorter than `--size` is a usage error. A region running past the chip's end from `--address` is
  refused. Rejected: silently comparing the overlap — `verify -s 64K` against a 4 KB file reporting
  a clean match is exactly the quiet under-check this milestone is removing from the firmware.

### Claude's Discretion

- The value of the range cap `N` in D-16, and the size of the bounded acceptance window in D-08.
- The exact internal shape of the streaming accumulator (class vs closure), provided D-02's
  single-implementation rule and D-03's corpus test hold.
- Exact wording and capitalisation of the two output lines, within D-13 and D-14's stated content.
- Whether the progress bar is shown for `blank`, and what it displays on an aborted run. Raised as a
  candidate gray area and declined — no constraint was placed on it.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

The ROADMAP.md phase entry carries no explicit `Canonical refs:` line; this list was accumulated
during analysis and discussion.

### Milestone scope and locked decisions
- `.planning/ROADMAP.md` lines 175-274 — the v1.41 milestone section and the Phase 202 detail block.
  Read the "Known open mechanic" paragraph (lines 226-230) **together with D-06/D-07 above**, which
  correct its premise.
- `.planning/REQUIREMENTS.md` — CMP-01…CMP-08, activation decisions D-1…D-7, the Out of Scope table,
  and CMP-F1/CMP-F2 in Future Requirements. **D-15 requires CMP-04 to be amended here before
  planning.**

### Provenance
- `.planning/todos/pending/2026-08-30-remove-cmd-verify-from-firmware-compare-in-app.md` — the
  original scoping of the verify half. `resolves_phase: 204`, but its § Solution item 3 is the host
  work this phase does. Its § "Open question — protocol compatibility" was settled by milestone
  decision D-4 (clean break).

### Repository rules that bind this phase
- `firestarter_app/CLAUDE.md` — § "What CI runs" (ruff scope `E,F,I,UP`; mypy strict module list in
  `pyproject.toml`, which **includes `cli_handlers`**; 70% coverage floor), and the standing warning
  that **a push to `beta` publishes to PyPI**.
- `firestarter_fw/CLAUDE.md` — read only for the protocol and `op_wait_for_ack` context behind D-06.
  No firmware change is in scope for this phase.
- `/workspaces/CLAUDE.md` — § "Milestone close and branch protection". Milestone work forks off
  `beta`; never commit to `beta` or `main`.

### Host source this phase changes
- `firestarter_app/firestarter/eprom_operations.py:2144-2189` — `verify_eprom`, to be rewritten.
- `firestarter_app/firestarter/eprom_operations.py:2325-2360` — `check_eprom_blank`, to be
  rewritten; its SRAM/FRAM short-circuit stays, its exit code changes per D-12.
- `firestarter_app/firestarter/eprom_operations.py:869-921` — `_main_phase_read_data`, the existing
  chunk-callback read path this phase reuses unchanged.
- `firestarter_app/firestarter/chip_test.py:120-275` — `_diff_offsets`, `classify_fingerprint`,
  `Fingerprint` and the locked bucket ordering. **Read the comment at lines 110-118 before touching
  anything here.**
- `firestarter_app/firestarter/cli_handlers.py:190-229` (`map_typed_errors`), `:794-841`
  (`verify` and `blank` commands), `:529-557` (`read`, whose `-a/--address` and `-s/--size` spelling
  CMP-08 must match).

### Firmware source read as evidence for D-06 (not modified)
- `firestarter_fw/src/eprom_operations.cpp:157-179` — `_process_outgoing_data`, the per-chunk ack.
- `firestarter_fw/src/operation_utils.cpp:94-159` — `op_wait_for_ack` and `op_get_message`.
- `firestarter_fw/src/firestarter.cpp:208-217, 260-347` — `command_done()` and the dispatch loop
  that calls it on the error path.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`_main_phase_read_data`** (`eprom_operations.py:869`) already delivers chip bytes to a
  `process_data_chunk_callback(address, payload)` and acks each chunk. This is the streaming hook —
  the phase needs no new read plumbing. `read_eprom` and `consistency_check_eprom` are both worked
  examples of driving it.
- **`classify_fingerprint` / `_diff_offsets` / `Fingerprint`** (`chip_test.py:120-275`) — the
  four-bucket classifier with its locked ordering and honest `indeterminate` fallback. Already
  tested; the phase refactors it rather than writing anything equivalent.
- **`consistency_check_eprom`** (`eprom_operations.py:973`) — returns `2` for hardware error. The
  in-repo precedent D-10 follows.
- **`address_parser`** — existing hex/decimal address and size parsing for the `-a`/`-s` options.

### Established Patterns
- **One-way import graph.** Neither `chip_test.py` nor `eprom_operations.py` imports the other, and
  `chip_test.py` documents that as deliberate. D-01 preserves it.
- **One divergence implementation, stated as a rule in the source** (`chip_test.py:113-117`).
- **`@map_typed_errors` + `sys.exit(0 if ok else 1)`** is the shape of every chip-op command. D-10
  and D-11 are a scoped, deliberate departure for two of them.
- **Typed exceptions** (`exceptions.py`) are how the service layer signals failure; `EpromOperator`
  also records `last_firmware_error_code` / message for `dev test`'s benefit
  (`chip_test.py:3093-3115`).

### Integration Points
- `cli_handlers.verify` gains `-s/--size` and `--full`; `cli_handlers.blank` gains `-a/--address`,
  `-s/--size` and `--full` (CMP-08).
- `chip_test.py` imports the new engine for `classify_fingerprint`; its `OP_VERIFY` and
  `OP_BLANK_CHECK` call sites (`chip_test.py:2690-2691` and the multi-run dispatch) are **Phase
  206's** work, not this phase's.
- `COMMAND_VERIFY` and `COMMAND_BLANK_CHECK` in `constants.py` become unreferenced by the
  verify/blank paths but **stay in place** — they are removed in Phases 204/205.

### Known traps that apply here
- **`mypy` is strict on `cli_handlers`** (see the override list in `pyproject.toml`, not this
  sentence). New options and the exit-code path must be fully typed.
- **Run the suite on Python 3.11**, not the devcontainer default — a green local run on a later
  interpreter has broken app CI before.
- **`ruff`'s selection is `E,F,I,UP`.** A `# noqa` for any other code is inert.
- **Comments in product source are allowed again** — the no-comments rule was removed on 2026-09-19.
  D-02, D-08 and D-12 each describe reasoning that belongs at its site in the code.

</code_context>

<specifics>
## Specific Ideas

- The operator asked for the mismatch report to be **one line, giving start address, end address and
  number of bytes — and explicitly no byte values**. Stated twice, the second time to rule out the
  `expected 0x5A read 0xFF` suffix. Honour it literally; D-15 amends the requirement to match rather
  than the other way round.
- The operator chose to **break the read and stop the programmer sending more bytes**, rejecting both
  "keep comparing, it is free" framings on offer. The abort is the point, not a consolation.
- Terse output is a standing preference: at v1.40 Phase 200 UAT a multi-line warning was rejected in
  favour of a one-line form (commit `b3a777e`).

</specifics>

<deferred>
## Deferred Ideas

- **A clean `DONE`-based mid-read stop.** `op_get_message` already parses `"DONE"` into
  `OP_MSG_DONE`; teaching `op_wait_for_ack` to treat it as a clean stop removes the ≤1 s timeout and
  the `MSG_ERR_TIMEOUT` ambiguity (D-08) for one line of firmware. **Best home: Phase 204**, which is
  already dual-repo and bench-gated. The host would prefer `DONE` and fall back to the ack-stop
  against pre-`3.1.0` firmware — which it must do anyway for REL-02. This is a cheaper route to
  CMP-F1 than the protocol-level abort that requirement assumes.
- **CLI-wide exit-code consistency.** D-11 scopes exit 2 to `verify` and `blank`. The other ~20
  commands still exit 1 for a transport or hardware failure. File as backlog.
- **Progress-bar behaviour on an aborted read**, and whether `blank` shows a bar at all. Raised,
  declined, left to discretion.
- **Proving criteria 1 and 2 needs harness work with no obvious existing home** — criterion 1 wants a
  wire-level assertion that neither ordinal is sent, and criterion 2 wants a peak-memory measurement
  on a 512 KB part. Raised as a candidate area and declined; flagged here so the researcher and
  planner treat them as real work rather than assumed-easy.

### Reviewed Todos (not folded)

- `2026-08-30-remove-cmd-verify-from-firmware-compare-in-app.md` — `resolves_phase: 204`. Its host
  half is what this phase implements, so it is cited as provenance above, but it is **not** folded:
  it closes when the firmware surface goes in Phase 204.
- `2026-08-30-write-init-blank-check-is-whole-device.md` — `resolves_phase: 205`.
- `2026-09-20-blank-check-region-fails-open-on-start-greater-than-end.md` — `resolves_phase: 205`.

`todo.match-phase 202` returned only broad keyword matches (`blank`, `read`, `check`, `firestarter`)
against firmware and host todos with no scope overlap; none were folded.

</deferred>

---

*Phase: 202-One comparison engine, on the host*
*Context gathered: 2026-09-20*
