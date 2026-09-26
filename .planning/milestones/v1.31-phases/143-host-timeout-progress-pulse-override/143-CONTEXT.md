# Phase 143: Host Timeout, Progress & Pulse Override - Context

**Gathered:** 2026-08-12
**Status:** Ready for planning

<domain>
## Phase Boundary

A host-initiated write survives the per-byte loop's new worst-case block times **without lying to the
user about progress or failure**, and a tester can override the database-supplied pulse for a single
run. Concretely: the firmware emits intra-block progress from inside Phase 141's per-byte loop and
advertises its own per-block worst-case time budget; the host consumes both, so a long block neither
trips a 10 s response timeout nor presents a frozen bar; `MSG_ERR_MAX_PULSES` / `MSG_ERR_ENERGY_CAP`
surface as **program failures naming the address** rather than transport errors; and
`firestarter write --pulse-us N` overrides the existing `pulse-delay` wire field, bounded before any
serial byte is sent.

**Requirements:** HOST-01, HOST-02, HOST-03, HOST-04, HOST-05.

**This phase is DUAL-REPO — `firestarter_app/` *and* `firestarter/`.** `commits_land_in:` names both
sub-repos plus meta for planning artifacts. This **corrects the roadmap**, which calls Phase 143
"independent of Phases 140–142 (different repo)" — see D-01. A plan that only *reads* a submodule
still names it: a worktree leaves submodules empty and `files_modified` under-detects.

**Not in this phase:**
- Freezing / re-deriving `native_trace_v131`, the frozen-vs-new trace diff, the cross-phase flash/RAM
  reconciliation, the `size_baseline.json` update, the TEST requirement flips — **Phase 144**
  (TEST-01…08). `native_trace_v131` stays RED here by design (D-24).
- Any bench claim about any protocol. **Phase 145** owns bench evidence; this phase's proofs are
  off-hardware (host suite + native envs) and the record says so.
- The 6.25 V ceiling qualification, the honesty ledger, the claim gate, gh#15 reconciliation, and the
  `--pulse-us` documentation entry — **Phase 146** (CLOSE-01…05). CLOSE-03 names `--pulse-us`
  explicitly; this phase ships the flag, not the doc chapter.
- Any `chip_database.json` change, any new database field, any second firmware dispatch selector.
  `protocol_id` remains the sole dispatch key (TABLE-05, still binding).
- Any `eprom_params.cpp` **data** change. The table is read-only this phase.
- Changing the read, verify, blank-check, erase or chip-ID paths' timeout, progress or error
  rendering. `DEFAULT_RESPONSE_TIMEOUT` stays 10 s for every non-write path (D-12).
- Modifying `_read_and_parse_lines`. It is ring-fenced v1.9 RCA territory (D-13).

</domain>

<decisions>
## Implementation Decisions

### Repo scope — the roadmap's framing is corrected, not worked around

- **D-01:** **This phase is dual-repo, and the record states that as a correction.** Hand-off H2
  (`141-LOOP-RECORD.md` §12, and `141-CONTEXT.md` D-12) predicted exactly this and required it be
  named *before* Phase 143 planned rather than discovered during it: HOST-02's own precedent is a
  **firmware** pattern, so choosing real intra-block progress (D-02) puts part of this phase in
  `firestarter/`. The roadmap's "Depends on: Phase 138 … Independent of Phases 140–142 (different
  repo)" line and the milestone's "HOST (143) is independent of 140–142 (different repo) and can run
  in parallel with them" sequencing note are both **factually wrong for the shipped decision** — this
  phase now depends on Phase 141's loop (the thing it emits from) and Phase 140's table (the thing the
  budget is computed from). Planning must treat 140/141/142 as landed prerequisites, not as parallel
  peers. Recording the correction is this phase's obligation; amending the roadmap prose is
  Phase 146 / CLOSE-04's, alongside the C3, F-140-05 and F-140-07 corrections already queued there.

### Progress during a long block (HOST-02)

- **D-02:** **Firmware emits the EXISTING `MSG_DATA_PROGRESS` (`0xE0`) from inside the per-byte
  loop.** Chosen over a host-only tick and over an INFO-band heartbeat. It is the only option that
  gives a bar reflecting **bytes actually programmed** rather than bytes handed to the firmware, and it
  costs **no new message id** — `0xE0` already exists with `format="%lu/%lu"`, is already emitted by
  `mem_util_blank_check` (`firestarter/src/proms/memory.cpp:558`), and is already rendered host-side by
  `_handle_progress_response` → `ClassProgressHandler.set_progress`
  (`firestarter_app/firestarter/eprom_operations.py:492-512`, `:268-277`). **`0xBF` therefore stays
  free** — Phase 142's D-08 left the ERROR band's last slot for this phase (F-141-05, H4) and this
  phase does not spend it.
  *Rejected — host-side only (poll `get_response` with a short timeout, tick between calls):* it keeps
  the phase single-repo and spends zero flash, but the bar could only show elapsed time or a spinner —
  it structurally cannot know chip progress — and abandoning/restarting the generator each cycle risks
  discarding a mid-flight frame's accumulator.
  *Rejected — firmware INFO-band heartbeat:* cheapest firmware option, needs zero host change (INFO is
  filtered out of `get_response`'s significant set, `serial_comm.py:524`) and INFO **is** visible at
  default verbosity since the D-09/F-120-02 promotion (`serial_comm.py:273-284`) — but the user would
  watch log lines scroll rather than a bar move.

- **D-03:** **The emission is TIME-bounded (`millis()` since the last frame), not byte-counted.** This
  is the decision HOST-01 hangs off: a byte-count cadence leaves the inter-frame gap unbounded in
  wall-clock (8 frames per block at `N=64` spans ~28 min at `--pulse-us 65535`, ~3.5 min of silence
  each), whereas a time bound feeds the host's response window by construction. Cost accepted: a
  `millis()` call and one `uint32_t` of per-block state inside the hot per-byte loop, which is more
  flash than a counter.
  *Rejected — byte-count every N bytes:* cheapest and trivially testable (a native case can count
  frames per block exactly), but it forces HOST-01 to carry a worst-case budget computed host-side,
  which is the option that would need the parameter table duplicated in `constants.py`.
  *Rejected — both (N bytes OR X ms):* best user-facing behaviour, but the most flash of the three and
  two code paths to test for a smoothness gain on writes that are already fast.

- **D-04:** **The host applies the frame's `current` and IGNORES the frame's `total`.** A dedicated
  write-progress branch sets the bar position absolutely and never consults the advertised total, so
  `set_progress`'s rebuild path is not reached. **This is a real defect being routed around, not a
  theoretical one:** `set_progress` (`eprom_operations.py:268-270`) calls `start(total)` whenever the
  frame's total differs from the bar's, and `start()` (`:247-256`) **closes and re-creates the tqdm
  bar** and zeroes `current_step`. The write bar is started with `file_size` (`:561`) while `0xE0`'s
  only existing emitter sends `handle->mem_size` — so a short input file or an `--address`-offset write
  would tear the bar down and rebuild it on **every single frame**.
  **The arithmetic the host owes:** `0xE0` carries an **absolute chip address**, but the write bar's
  origin is 0, so the host must subtract the write's start address. Getting this wrong shows up as a
  bar that starts mid-way on an `--address` write.
  *Rejected — firmware sends block-relative `(bytes_done, block_size)`:* no host-side offset or
  geometry arithmetic, but `0xE0` would gain a **second payload meaning** depending on which operation
  emitted it, and a future reader of the id could no longer trust one contract.
  *Rejected — fix `set_progress`'s rebuild in place:* arguably fixes a latent defect for every caller,
  but it is shared code on the read and blank-check paths, so the blast radius reaches operations this
  phase does not own and Phase 144's host-suite leg would be proving a change nobody asked for. Logged
  as a deferred idea instead.

- **D-05:** **The host must NOT ack the progress frame.** `_handle_progress_response`'s `ack_data`
  defaults to `True` and sends an `OK` for DATA frames (`eprom_operations.py:492-512`); the firmware is
  mid-block and waiting for nothing, so an ack would desync the stream. This is the
  `#write-empty-input-regression` trap in a new place — that regression's fix was precisely
  `ack_data=False` on the INIT/END progress frames (`:480-488`). The write main-phase branch uses
  `ack_data=False`.
  **The second half of the same integration:** `_main_phase_send_data`'s loop today handles only
  `MAIN` / `ERROR` / `OK` and **raises** on anything else (`:573-576`,
  `"Programmer did not request data chunk, got {type}"`). A DATA frame arriving mid-block hits that
  raise. The loop needs a DATA branch, and that branch is what makes D-02 work rather than break the
  write.

- **D-06:** **The emission is EPROM-path only, and that is an explicit non-claim.** The per-byte loop
  lives in `firestarter/src/proms/eprom.cpp`, so flash, EEPROM (`0x0D`), SRAM and every other family's
  write keeps today's block-granularity progress and today's silent-stall behaviour. The phase record
  states this plainly rather than letting "the user sees progress during a long write" read as
  universal. HOST-02's requirement text is scoped to the write path this milestone rewrote.

### Response timeout (HOST-01)

- **D-07:** **The budget is computed from the datasheet-derived pulse counts, and the FIRMWARE computes
  it.** Operator correction, and the reason this is not a guessed constant: the datasheets specify the
  pulse count — **25 for `0x07`/`0x08`, 255 for `0x0B`** — which is exactly what Phase 140's
  `max_pulses` column already encodes, so the worst-case block time is deterministic. The firmware
  computes the per-block worst case from the table plus the live `pulse_delay` and **advertises** it;
  the host consumes the number. **No datasheet-derived value is duplicated host-side** — `constants.py`
  gains nothing, and the budget self-corrects when the table changes or a future row gains a non-zero
  overprogram factor.
  *Rejected — mirror `max_pulses` + `energy_cap_us` in `constants.py`:* it is the established home for
  firmware-mirrored constants (`CTRL_*`, `REVISION_*`, flag bits) and needs no wire change at all, but
  it creates a second definition site for datasheet values, obliges Phase 144's dual-repo parity leg to
  actually compare them, and silently under-estimates the moment a row gains an overprogram factor.
  *Rejected — one fixed generous constant:* discards the determinism above, and a `--pulse-us 65535`
  run on `0x07` (1024 × 25 × 65535 µs ≈ 28 min per block) makes the constant either useless for that
  case or so large a dead board hangs for half an hour.

- **D-08:** **The carrier is a CAP-03 length-discriminated extension of `MSG_OK_READY`'s existing
  variable-length param blob — no catalog edit, no codegen, no new id.** Verified during discussion:
  `MSG_OK_READY`'s catalog entry is `params=(("bytes","hex"),)` with `param_bytes=-1`
  (`firestarter_app/firestarter/messages.py:142-150`), and **both** prior extensions were decoded
  purely by length in the host's `_decode_id_frame` override — CAP-01's 2-byte buffer size at
  `serial_comm.py:356-363`, CAP-02's `[hw_rev u8][ver_len u8][ver bytes]` tail at `:370-376`. Neither
  required a `messages.toml` change. CAP-03 is therefore "firmware appends bytes, host reads further
  into `params_bytes`": **zero `messages.toml` diff, zero codegen run, zero new message id, and no
  `firestarter_app` constants-parity churn from the catalog.** The extension seam is also explicitly
  documented as *not* touching the ring-fenced generator (`:340-341`).
  **The hazard that comes with it:** CAP-02's tail is itself variable-length, so the budget field must
  be read at the **computed `ver_end` offset**, never a fixed index. A fixed index works on every board
  whose identity string happens to be one length and silently misreads on the next.
  **Degradation shape is already established:** a shorter param region leaves the newer field `None`
  (CAP-01 `T-55-07`, CAP-02's "both stay None against firmware that predates CAP-02"). D-10 defines
  what `None` means here.

- **D-09:** **The advertised number is already padded — the firmware owns the safety margin.** It
  includes firmware's own slack for the verify pass(es), the VPE settle and serial time, because the
  firmware is the only side that knows them. The host uses the value verbatim and applies no multiplier
  of its own. **Why this matters more than it looks:** a budget that is too *tight* causes a spurious
  timeout on a **working** write — a false failure on real silicon, which is strictly worse than a
  generous ceiling. Cost accepted: the padding policy lives in firmware and a host-side reader cannot
  see how conservative it is, so the phase record must state the padding rule in prose.
  *Rejected — host multiplies by a named factor:* the policy would be visible and cheap to test in
  Python, but two sides would contribute to the final number and a spurious timeout would need both
  examined.

- **D-10:** **An absent advertisement falls back to a generous fixed write-path timeout — never to 10 s,
  never to a refusal.** This follows CAP-01's own precedent exactly: absent means safe default, never an
  error (Phase 54 D-05 was *reversed* for precisely this, `eprom_operations.py:300-313`). Old firmware
  then survives a slow write instead of raising the transport error HOST-03 exists to avoid.
  **Recorded default: 120 s**, derived rather than picked — the worst shipped-database block time under
  the new loop with no advertisement is `0x0B` at 50 ms/byte × 1024 B = **51.2 s** (H4: the energy cap
  lands on exactly 50 ms for every shipped `0x0B` width) and `0x07`/`0x08` at 25 × 1000 µs × 1024 B =
  **25.6 s**, so 120 s is >2× the worst case. Research may revise the number; it may not revise the
  *derivation requirement*.
  **The residual non-claim this creates, to be stated in the record:** the realistic "absent
  advertisement" case is not old released firmware but a **mid-milestone v1.31 build** — Phases 140–142
  landed the new loop without CAP-03, and such a build is on the operator's bench right now. On that
  firmware a `--pulse-us` above roughly `120 s / (25 × 1024)` ≈ **4700 µs** can still time out. Named,
  not fixed.
  *Rejected — keep today's 10 s when absent:* no new constant and a dead board still reports fast, but
  HOST-01 would then be satisfied only against matching firmware and the record would owe a non-claim
  covering every unmatched pair.
  *Rejected — refuse the write when no budget is advertised:* never programs silicon under a timeout the
  host cannot reason about, but it is a hard regression — writes that work today would stop — and this
  milestone's *release* is lockstep while users' *boards* are not.

- **D-11:** **The formula must bound per-byte time as `min(max_pulses × pulse, energy_cap_us)`, plus an
  overprogram term of `min(3 × overprogram_factor × pulse, overprogram_cap_us)`.** Two corrections a
  naive `max_pulses × pulse` gets wrong: `0x0B`'s **255 pulses is not its real bound** — `energy_cap_us
  = 50000` bites first, and using 255 would over-estimate ~2.5× on every shipped width (H4 measured
  200/500/1000 µs → 250/100/50 pulses, all landing on exactly 50000); and the overprogram term is
  **exactly 0 today** because all three shipped rows carry `overprogram_factor = 0`, so it must be
  written for the future row rather than omitted as if the column did not exist. `energy_cap_us == 0`
  means **UNCAPPED**, not "cap at zero" — the same trap `eprom.cpp:104-106` guards with
  `energy_cap_us > 0`; an unguarded `min` would clamp every `0x07`/`0x08` byte to zero.

- **D-12:** **`DEFAULT_RESPONSE_TIMEOUT` (10 s, `serial_comm.py:66`) is left untouched and keeps
  applying to every non-write path.** The write call sites pass the advertised budget (or D-10's
  fallback); read, verify, blank-check, erase and chip-ID keep 10 s, so a genuinely dead board still
  reports in ten seconds on those commands instead of inheriting a multi-minute write budget.

- **D-13:** **`_read_and_parse_lines` is not modified. Full stop.** Its header
  (`serial_comm.py:379-389`) ring-fences it as v1.9 RCA territory (GATE-1.8d) and states that "any
  change to the byte-by-byte read loop, the magic-preamble dispatch, the frame-length read, or the
  **timeout reset semantics** MUST be flagged and deferred to v1.9 alongside binary re-validation."
  This phase changes the timeout **argument** at write call sites and extends the `_decode_id_frame`
  **override seam** (`:320-377`) — both outside the fence. It does **not** add a heartbeat callback
  into the read loop, and it does not touch the `start_time = time.time()` resets at `:448` / `:513`.
  Nothing in this phase's design depends on changing them: the resets already fire on every yielded
  frame, which is *why* D-02's emission feeds the window for free.

### `--pulse-us` (HOST-04, HOST-05)

- **D-14:** **The override rides the DB dict, following the `read_strobe_us` precedent verbatim.**
  `write_eprom` takes a `pulse_us: int = 0` parameter, shallow-copies `eprom_data_dict` when non-zero
  (**never** mutating the caller's dict) and sets the existing `"pulse-delay"` key, which then flows
  through `_setup_operation`'s `command_dict = eprom_data_dict.copy()` (`:337`) onto the wire. This is
  the shape `consistency_check_eprom` already uses for `read_settling_us` / `read_strobe_us`
  (`eprom_operations.py:765-777`), whose own comment says it is "consistent with how pulse-delay
  already travels via the DB dict". **No new wire field and no new command** — milestone D-04 satisfied
  structurally, because the key being written is the one `database.py:555` already emits.

- **D-15:** **Bounds are enforced by `click.IntRange(1, 65535)` on the option.** Click refuses
  out-of-range at parse time — before `AppContext` builds, before any port is opened, structurally
  before any serial byte — which is exactly HOST-05's "before any serial byte is sent" and needs no
  hand-rolled check whose guarantee would rest on where it sits in the handler.
  **The bound's provenance, which the record must state:** `1..65535` is **minipro parity** (`-o
  pulse=N` is uint16), **not** the wire type. `pulse-delay` is parsed by `extract_long` into an
  *unclamped* `uint32_t` (`json_parser.c:503`, hand-off H3) — an over-ceiling value is reachable on the
  wire today, before this flag ships. H3 is Phase 146 / CLOSE-04's to reconcile; this phase must not
  imply the bound is a type constraint.
  *Rejected — hand-rolled check with a bespoke message:* more actionable wording, but it re-implements
  what `IntRange` gives free and moves the pre-serial guarantee from Click's parse order into a code
  position a later edit can move.

- **D-16:** **The `0x0B`-only over-cap case is left to the firmware's existing pre-flight refusal; the
  host mirrors no table value to pre-empt it.** A `--pulse-us` between 50001 and 65535 is host-legal but
  firmware-refused on `0x0B` only, because `eprom.cpp:104-110`'s refusal is keyed on `energy_cap_us > 0`
  and just `0x0B` ships a non-zero cap. Warning host-side would require mirroring `energy_cap_us`,
  which contradicts D-07's whole point. The firmware refusal already fires **before the first pulse**
  and reports the offending value via `MSG_ERR_PULSE_TOO_WIDE` (`0xAE`); D-19 makes that render
  actionably. `eprom.cpp:95-101`'s own comment already names itself "the firmware-side backstop for
  Phase 143's `--pulse-us` bounds, independent of host validation" — this decision takes it at its word.

- **D-17:** **Using `--pulse-us` always prints a default-visible report line naming both values** — the
  database pulse it replaced and the override that replaced it. Precedent: the v1.22 D-04 auto-set block
  in `write()` "always prints a mandatory, default-visible report line when it fires"
  (`cli_handlers.py:616-628`). The reason is provenance, which this milestone keeps insisting on: a
  bench artifact or log captured without the command line beside it cannot otherwise tell you the pulse
  was not the database's — and Phase 145's evidence will be read by strangers.

- **D-18:** **`--pulse-us` is exposed on `write` only.** The requirement names
  `firestarter write --pulse-us N`; `read`, `verify`, `blank` and `erase` emit no program pulse, so
  there is nothing to override. Same reasoning that kept `--skip-sdp-unlock` on `write` alone (D-17,
  v1.22).

### HOST-03 — not selected for discussion; decided by Claude

- **D-19:** **HOST-03 is render-and-prove plus a remediation hint, not a re-plumb.** The machinery
  already exists and must not be rebuilt: `messages.py:747-762` carries `MSG_ERR_MAX_PULSES` (`0xBD`)
  and `MSG_ERR_ENERGY_CAP` (`0xBE`) with formats that already interpolate the address, and
  `_main_phase_send_data`'s ERROR branch already routes through `_raise_for_error_response`
  (`eprom_operations.py:75-91`) to an `EpromOperationError` carrying `error_code`. What was actually
  missing is that **the 10 s timeout fired first**, converting a program failure into a transport
  error — which HOST-01 now fixes. HOST-03's own delta is therefore: a hint appended on the
  `_boot_block_hint_message` pattern (`:106-135`, already wired into the same ERROR branch at
  `:568-572`) for `0xBD` / `0xBE` / `0xAE`, plus a host test proving the id surfaces as a program
  failure naming the address.

- **D-20:** **No host code may expect `MSG_ERR_WRITE_FAILED` (`0xB1`) on a 27C write.** F-141-06: it is
  emitted by **nothing** on the 27C path any more (whole-tree grep, zero references under `src/`); the
  budget reporter emits `0xBD`/`0xBE` with a different, smaller payload shape (`u24 address, u8
  pulse_count`) instead of `0xB1`'s three-param `(u24 address, u8 retries, u16 bad bytes)`. Any hint or
  test keyed on `0xB1` for this family is keyed on a dead id.

- **D-21:** **The hint must state D-05's aborted-block semantics — no retry advice, no resumption
  implication.** `141-LOOP-RECORD.md` §4 traced it: `handle->address` does **not** advance,
  `_process_incoming_data` returns `false` immediately, `command_done()` fires and zeroes the control
  and address registers, and the firmware **accepts no further blocks for that write**. "The write
  aborts" and "the firmware stops accepting blocks" are the same event. §4 says in terms that a host
  implementation assuming the firmware might continue past a failed block, or auto-retrying the same
  block expecting firmware-side resumption, "would be building against a behaviour the firmware does
  not have." The hint tells the user what was and was not programmed and points at `--pulse-us` for the
  over-cap case; it does not offer to retry.

### Flash and gate posture

- **D-22:** **Flash posture: it must FIT. The MERGE-05 band is not this phase's concern.** Operator
  decision, verbatim intent: *"don't care about the ceiling of Leonardo, the important thing is that it
  fits in the flash."* So: measure cold and record, MERGE-05 stays RED and is Phase 144 / TEST-08's to
  reconcile, `size_baseline.json` is read-only, **no** predictions artifact, and **no** shrink ladder
  unless the build actually overruns. The one binding constraint is that `leonardo` still **builds** —
  the 28672 B limit is a build *failure*, not a gate. F-142-08 hands this phase **2130 B** of headroom,
  142 B narrower than Phase 141's tip, and names Phase 143 as the phase that must still fit.
  **Also on the watch list, unchanged:** `check_build_warnings.py`'s native watermark sits at **1166
  with zero headroom**, so any new warning in a native TU turns that gate RED.

- **D-23:** **All `eprom.cpp` edits are confined to ONE plan and ONE commit, landing the re-derived
  D-13 golden with them.** That file's blob SHA is pinned by
  `firestarter/tests/golden/protocol_branch_inventory.json`, whose working-tree leg goes RED on the
  first keystroke and whose blob-SHA leg goes RED only after commit — so one commit means the gate goes
  RED once, for one reason. GSD commits after every task, so one commit requires one **task**: the
  Phase 142 tightening of Phase 141's one-*plan* precedent (142-CONTEXT.md's discretion index). The
  golden's `meta.how_to_update` is binding — re-derive by running an independent parse against the new
  file; never hand-edit a line number, a `keyed_on` set, a class or a count; state in the commit
  message which site changed and why. The pinned `protocol_lines` literal in
  `firestarter/tests/test_protocol_branch_inventory.py` moves with it. **This phase must add no new
  tier-1 protocol-keyed site:** the emission is time-keyed and the budget is table-driven, so neither
  reads `handle->protocol` at a new site.

- **D-24:** **`native_trace_v131` stays RED and is NOT re-frozen here.** Carried from Phase 141's D-10
  and Phase 142's D-17. This phase changes the emitted stream again (D-02 adds frames inside the byte
  loop); it captures nothing as a new frozen fixture, records the new failure values so both sides
  exist, and names the RED in its record so `/gsd-verify-work` reads it as expected. Phase 144 /
  TEST-06 owns the freeze and the attributable diff.

- **D-25:** **Every new gate leg is seen RED on a planted violation before its GREEN is believed.** The
  standing D-15 discipline from Phases 140/141/142 (12, 13 and the 142 set of planted runs), with each
  transcript captured verbatim in its plan's SUMMARY. A pre-authored leg can be **unreachable** — RED
  proves nothing until the leg has been seen to pass for the right reason too.

### Claude's Discretion

This is an **index** of the discretionary items, not a second definition site — the decisions are
defined in full above. Their IDs are deliberately unbolded here: a `- **D-NN**` bullet without a `:` or
` — ` inside the bold makes the decision-coverage gate fail closed with `reason: could-not-parse`, and
a label wrapped across lines cannot be read by that gate either.

- D-14, D-15, D-16, D-17, D-18 — the whole `--pulse-us` surface (plumbing, bounds mechanism, the
  `0x0B` over-cap disposition, announcement, and which commands carry the flag). The operator said
  "you decide" for this area; resolutions recorded inline above.
- D-19, D-20, D-21 — HOST-03's scope. Not selected for discussion; decided from the hand-offs
  (F-141-06, §4 of the loop record) rather than invented.
- The advertised budget's **encoding** — recorded default: a `uint16_t` of **seconds**, ceiling-rounded
  with a 1 s floor, appended after CAP-02's variable-length identity tail. Two bytes, and 65535 s
  (~18 h) covers the ~28 min worst case with vast margin; `uint32_t` milliseconds is the alternative if
  research finds sub-second granularity matters (it should not, for a timeout). Research may override
  on wire-economy or decode-symmetry grounds.
- The time-bound constant in D-03, the exact per-frame payload source, and where the emission call sits
  inside the loop — subject to D-23 (one plan, one commit for `eprom.cpp`) and D-22 (it must fit).
- Plan decomposition and wave structure, including which plan owns the host half and which owns the
  firmware half. The two halves are separable: the host's D-10 fallback path is testable with **no**
  firmware change at all, so the host work does not have to wait on the firmware work.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase requirements and milestone framing
- `.planning/REQUIREMENTS.md` §"Host" — HOST-01…05, the exact requirement text.
- `.planning/ROADMAP.md` §"Phase 143: Host Timeout, Progress & Pulse Override" — goal and the five
  success criteria. **Note:** its "Depends on … Independent of Phases 140–142 (different repo)" line and
  the milestone's matching sequencing-spine sentence are **corrected by D-01** — do not plan from them.
- `.planning/PROJECT.md` §"Current Milestone: v1.31" — D-04 (`--pulse-us` overrides the existing wire
  field), D-05 (max-pulse hard-fails the block), the 6.25 V evidence ceiling, and the out-of-scope list.
- `.planning/seeds/27c-algorithm-fidelity-param-table-refactor.md` — the `/gsd-explore` correction pass
  (C1/C2/C3) this milestone is scoped from.

### Prior-phase records (the hand-offs this phase consumes)
- `.planning/phases/141-per-byte-program-loop/141-LOOP-RECORD.md` — **§4** (what "hard-fails the block"
  actually does, traced: `handle->address` does not advance, `command_done()` fires, no further blocks —
  D-21 renders exactly this); **§5** (the `0xBD`/`0xBE` payload shape, `0xBF` as the band's last free
  slot, and `MSG_ERR_WRITE_FAILED` now emitted by nothing on the 27C path); **§9/H4** (the honest
  energy-cap ceiling: exactly 50 ms per byte on every shipped `0x0B` width, worst case 99998 µs — and
  the `99999` figure in `141-CONTEXT.md` is stale, `firestarter/CLAUDE.md` is the corrected source);
  **§10** (the three `native_*_v131` envs run in no CI leg of either repo); **§12 hand-offs H2** (this
  phase is dual-repo) and **H3** (the unclamped `extract_long`); **§15** findings register.
- `.planning/phases/141-per-byte-program-loop/141-CONTEXT.md` — D-12 (the chunking/progress seam
  deliberately left open for this phase, and the requirement to name H2 before planning), plus its
  Deferred Ideas list naming this phase.
- `.planning/phases/142-high-voltage-routing/142-VPP-RECORD.md` — **§1.3** (the Leonardo headroom
  consequence for this phase), **F-142-08** (2130 B), **H4** (`0xBF` still free; budget accordingly).
- `.planning/phases/142-high-voltage-routing/142-CONTEXT.md` — D-08 (`0xBF` left for this phase), D-09
  (`command_done()` as the operation-level disable), D-16 (the flash posture this phase inherits and
  D-22 amends), D-17/D-18 (the trace and golden obligations).
- `.planning/phases/140-parameter-table/140-PARAM-TABLE-RECORD.md` — the shipped row values and their
  per-cell citations (the `max_pulses` / `energy_cap_us` D-07 and D-11 compute from).
- `.planning/phases/138-preconditions-baseline/138-04-HOST-BASELINE.md` — the host-suite baseline and
  the **CI-parity interpreter constraint**: measure with `.venv/ci-replica/bin/python` (3.11) from
  inside `/workspaces/firestarter_app`, never the ambient 3.12.
- `.planning/phases/138-preconditions-baseline/138-02-PULSE-DISTRIBUTION.md` — the live per-protocol
  `pulse_delay` distribution (the widths D-10's fallback derivation is bounded by).

### Host source (current line numbers — re-locate before relying on them)
- `firestarter_app/firestarter/serial_comm.py` — `:66` `DEFAULT_RESPONSE_TIMEOUT` (D-12 leaves it);
  `:92` `NON_RESPONSE_PREFIXES`; `:262-284` `_log_rurp_feedback` and the INFO→`logging.INFO` promotion;
  `:320-377` the `_decode_id_frame` **override seam** with CAP-01 at `:356-363` and CAP-02's
  variable-length tail at `:370-376` (**D-08's extension point and its `ver_end` hazard**);
  `:379-389` the **GATE-1.8d ring-fence header — read this before touching anything below it**;
  `:390-516` the fenced generator, incl. the `start_time` resets at `:448` / `:513`; `:518-531`
  `get_response` and its significant-response filter at `:524`.
- `firestarter_app/firestarter/eprom_operations.py` — `:75-91` `_raise_for_error_response`; `:106-135`
  `_boot_block_hint_message` (**D-19's pattern**); `:241-282` `ClassProgressHandler` with `start` at
  `:247`, `update` at `:258` and the rebuild-on-differing-total at **`:268-270`** (D-04's hazard);
  `:300-313` `_calculate_buffer_size` (CAP-01's consumer and D-10's absent-means-safe-default
  precedent); `:315-372` `_setup_operation` and the `command_dict` copy at `:337`; `:492-512`
  `_handle_progress_response` and its `ack_data` default; `:538-593` `_main_phase_send_data` — bar start
  at `:561`, the `get_response()` call at `:564`, **the raise-on-unexpected-type at `:573-576`** and the
  per-chunk `update` at `:591`; `:699-780` `consistency_check_eprom` with **the DB-dict override pattern
  at `:765-777`** (D-14's precedent); `:1583-1673` `write_eprom`.
- `firestarter_app/firestarter/cli_handlers.py` — `:546-602` the `write` command's existing options and
  signature; `:616-628` the D-04 mandatory-report-line precedent (**D-17**); `:1470-1484` the
  `--read-settling` / `--read-strobe` options (D-14's CLI-side precedent).
- `firestarter_app/firestarter/messages.py` — `:142-150` `MSG_OK_READY`'s variable-length catalog entry
  (`param_bytes=-1`, the fact D-08 turns on); `:747-762` `MSG_ERR_MAX_PULSES` / `MSG_ERR_ENERGY_CAP`;
  `:766-773` `MSG_DATA_PROGRESS`'s `"%lu/%lu"`. **Generated file — never hand-edit** (meta's
  `tools/catalog/messages.toml` is the source), and D-08 means this phase should not need to.
- `firestarter_app/firestarter/constants.py` — `:143-149` the `JSON_KEY_*` naming convention; the
  firmware-mirrored `CTRL_*` / `REVISION_*` blocks D-07 declined to add to.
- `firestarter_app/firestarter/database.py` — `:128-140` `_parse_pulse_duration`; `:549-556` the
  `programmer_data` dict that already emits `"pulse-delay"` (D-14's target key).
- `firestarter_app/CLAUDE.md` — §"Wire Protocol" (the example write command showing `pulse-delay`),
  §"Constants" (the sync obligation with `firestarter/include/firestarter.h`).

### Firmware source (current line numbers — re-locate before relying on them)
- `firestarter/src/proms/eprom.cpp` — `:95-110` the `energy_cap_us`-keyed pre-flight pulse refusal,
  **including the comment that names itself the backstop for this phase's `--pulse-us` bounds** (D-16);
  the per-byte loop and its exits (D-02's emission site, D-23's one-commit constraint).
- `firestarter/src/proms/memory.cpp` — `:391-467` `mem_util_blank_check`'s operation-in-progress /
  `progress_data` pattern and its `LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, handle->address,
  handle->mem_size)` at `:467` — **the only existing `0xE0` emitter and the semantics D-04 reasons
  about**; `:233-250` `mem_util_split_delay` / `mem_util_delay_us` and the 16383 µs accuracy ceiling.
- `firestarter/src/proms/eprom_params.cpp` — `:49-53` the three shipped rows (`0x07`/`0x08`: 25 pulses,
  `energy_cap 0`; `0x0B`: 255 pulses, `energy_cap 50000`) — **read-only this phase**, and the source of
  D-07's advertised budget.
- `firestarter/include/eprom_params.h` — the column semantics, `energy_cap_us == 0` meaning UNCAPPED
  (D-11's trap), and `:28`-adjacent note on the `(factor=3, pulse_count=25, pulse_us=65535)` overflow
  bound.
- `firestarter/src/firestarter.cpp` — `:162-171` `command_done()` (D-21's trace) and `:215-291` the
  dispatch switch that reaches it.
- `firestarter/src/eprom_operations.cpp` — `:93` "The host application shows its own progress, so we
  just ask for data" — the comment D-02 falsifies, and which must move with the change.
- `firestarter/CLAUDE.md` §"Algorithm Handlers" — the `0x07`/`0x08`/`0x0B` rows, and the corrected
  `99998 µs` energy-cap worst case (F-141-10: this is the corrected source, not `141-CONTEXT.md`).

### Gates, tests and budget artifacts
- `firestarter/tests/golden/protocol_branch_inventory.json` — read `meta.how_to_update` and
  `meta.frozen_for` **in full** before touching `eprom.cpp` (D-23).
- `firestarter/tests/test_protocol_branch_inventory.py` — the seven-test D-13 gate and the pinned
  `protocol_lines` literal that moves with the golden.
- `firestarter/scripts/check_build_warnings.py` — the **1166 native watermark with zero headroom**.
- `firestarter/scripts/baseline/size_baseline.json` + `firestarter/scripts/check_size_baseline.py` — the
  141 cases / 17 suites pin and the MERGE-05 policy. **Read-only this phase** (D-22). Do **not** pass
  `native_loop_v131` / `native_trace_v131` / `native_params_v131` to it (F-138-05: uncaught `KeyError`).
- `firestarter/platformio.ini` — `[env:native_loop_v131]` and the comment block on why the v131 envs
  feed neither live gate.
- `firestarter_app/.github/workflows/ci.yml` — the CI-scoped `ruff` + `mypy` (strict on 8 modules,
  **including `serial_comm.py`**) + `pytest --cov-fail-under=70` gate this phase's host half must pass.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`MSG_DATA_PROGRESS` (`0xE0`) end to end** — the id, its `"%lu/%lu"` format, the firmware emit macro
  (`LOG_DATA_ID_U32_U32`) and the host's `_handle_progress_response` → `set_progress` render path all
  already exist and already work for blank-check. D-02 adds a **second emitter**, not a mechanism.
- **`MSG_OK_READY`'s length-discriminated param blob** — `param_bytes=-1` plus two prior extensions
  (CAP-01, CAP-02) decoded by length in one override seam. D-08's budget field is the third, and needs
  **no catalog edit and no codegen**.
- **`read_settling_us` / `read_strobe_us`** (`eprom_operations.py:765-777`, `cli_handlers.py:1468-1482`)
  — a complete, in-tree, shipped example of a per-run µs override riding the DB dict with a shallow copy
  and emit-only-when-non-zero. D-14 copies the shape, not the semantics.
- **`_boot_block_hint_message`** (`eprom_operations.py:106-135`, wired at `:568-572`) — a working
  id-keyed hint-append on the write ERROR branch. D-19 extends the same seam for `0xBD`/`0xBE`/`0xAE`
  rather than inventing an error-framing layer.
- **`_calculate_buffer_size`'s absent-advertisement fallback** (`:300-313`) — the exact precedent D-10
  follows, including its own history: Phase 54's `FirmwareOutdatedError` was **reversed** to a safe
  default, which is the argument against D-10's rejected "refuse the write" option.
- **`_decode_id_frame` override** (`serial_comm.py:320-377`) — the sanctioned way to read new ack fields
  without touching the ring-fenced generator, and it already carries a **plausibility clamp** (CAP-01
  rejects buffer sizes outside `[1, 4096]`) that the budget field should mirror in spirit: a
  hostile/corrupt ack must not be able to install an unbounded timeout.
- **`seen_message_ids`** (`:154-160`) — a bounded per-connection record of every decoded id. Available
  if a test or a hint needs to assert an id was or was not observed (the v1.22 HOST-06 pattern).

### Established Patterns
- **`PROGMEM` table reads** go through `pgm_read_byte` / `pgm_read_dword` — the budget computation must
  not dereference row fields directly.
- **`rurp_write_to_register()` elides a write when the value is unchanged** (F-141-09) — register-write
  elision is invisible to a native suite unless `rurp_register_utils.h` is in the stubs, and raw
  `STROBE_KIND_DATA` counts are not a sound pulse-count oracle. Any native proof of D-02's cadence must
  filter by value, not count strobes.
- **Native trace stubs record NO time** — `delay()` is unstubbed. A trace diff cannot prove a timing
  change, and **it cannot prove D-03's time-bounded cadence either**. Planning must choose an oracle
  that does not depend on stubbed wall-clock, or stub `millis()` deliberately and say so.
- **INFO is user-visible; DEBUG is not** — `_log_rurp_feedback:273-284`. A firmware message intended for
  the user must be in the INFO band or higher; the D-09/F-120-02 incident is the precedent (a two-repo
  requirement passed its own phase's verification while being false end to end).
- **`test_flash_path_record_sync.py` asserts whole-repo `git status --porcelain`** (F-141-11, orphaned
  and unassigned) — **commit in-flight changes before running the full firmware suite**, or it goes RED
  for the wrong reason.
- **One plan owns all `eprom.cpp` edits** (D-23) — Phase 141's precedent, tightened to one commit by
  Phase 142.
- **Every `# noqa: BLE001` in `firestarter_app` is inert** — `ruff select` is `[E,F,I,UP]`, so
  `except Exception:` is gated by nothing. Do not rely on a `noqa` as evidence a broad catch was
  reviewed.
- **`pytest` addopts already include `-q`** — use `-o addopts=""` to see the count line.

### Integration Points
- **`_main_phase_send_data`'s response loop** (`:563-593`) is the single place the write path meets the
  wire. D-02's DATA branch, D-05's `ack_data=False` and D-19's hint all land in or beside it — it is the
  phase's busiest file region and the one most likely to be touched by two plans at once.
- **`write_eprom`'s `_operation_context` block** (`:1591-1673`) — note the existing warning that
  `self.comm` is `None` after the block exits, so anything reading `seen_message_ids` or a decoded ack
  field must do so **inside** the `with`.
- **The `0xE0` payload contract is shared with blank-check** — D-04 deliberately keeps one meaning for
  the id, which means the host's *write* branch must be the thing that differs, not the frame.
- **`firestarter/src/eprom_operations.cpp:89`'s comment** ("The host application shows its own progress,
  so we just ask for data") states the assumption D-02 removes; it goes stale in the same change.
- **`serial_comm.py` is one of the 8 mypy-strict modules** — every new attribute and signature there
  must be annotated to CI-strict standards, and the devcontainer's 3.12 masks the CI 3.11/3.9 result.

</code_context>

<specifics>
## Specific Ideas

- The operator's correction that reframed HOST-01, in their own terms: **the datasheets say how many
  pulses — 25 for `0x07`/`0x08`, 255 for `0x0B`.** The timeout is therefore not a number to be guessed
  but a quantity to be *derived*, and the derivation belongs where the datasheet-sourced table already
  lives — the firmware. Any plan or research output that proposes a hand-picked timeout constant as the
  primary mechanism is reasoning from the superseded framing.
- On flash, verbatim intent: **"don't care about the ceiling of Leonardo, the important thing is that it
  fits in the flash."** MERGE-05 is Phase 144's. "It builds" is the bar.
- The honest headline for this phase is **"a long write now reports what it is doing, and a failed byte
  now reports as a failed byte"** — two user-visible truths, both provable off-hardware. Not "writes are
  faster" and not "writes are more reliable."

</specifics>

<deferred>
## Deferred Ideas

- **Fixing `set_progress`'s rebuild-on-differing-total** (`eprom_operations.py:268-270`) — a latent
  defect for every caller: a differing total closes and re-creates the tqdm bar and zeroes
  `current_step`, where updating the total in place would do. D-04 routes around it because the fix is
  shared code on the read and blank-check paths. Needs an owner outside v1.31.
- **Intra-block progress for the non-EPROM write families** (flash `0x05`, EEPROM `0x0D`, SRAM, …) —
  D-06's explicit non-claim. Each has its own write path; none gets a heartbeat from this phase.
- **A combined byte-count-OR-time cadence** (D-03's rejected third option) — better bar smoothness on
  fast writes, for more flash and a second code path. Revisit only if a bench run shows the
  time-bounded cadence looks jerky at 100 µs.
- **Host-side warning for a `--pulse-us` above `0x0B`'s energy cap** — D-16 left this to the firmware's
  existing pre-flight refusal rather than mirror `energy_cap_us` host-side. If CAP-03 ever advertises
  the cap itself, this becomes free and worth doing.
- **Reconciling H3** (`extract_long` parses `pulse-delay` into an unclamped `uint32_t`, so an
  over-ceiling wire value is reachable independently of `--pulse-us`) — **Phase 146 / CLOSE-04**,
  alongside F-140-05 and F-140-07. This phase must not imply its `1..65535` bound is a type constraint.
- **Correcting the roadmap's "Phase 143 is independent of 140–142" prose and the matching
  sequencing-spine sentence** — D-01 records the correction; amending `ROADMAP.md` / `PROJECT.md`
  milestone text is **Phase 146 / CLOSE-04**'s, on the standing convention of not silently rewriting
  locked planning documents mid-milestone.
- **`DBG_PULSE_DELAY_MISMATCH`'s stale wording** ("retrying with increased pulse delay" — contradicts a
  fixed-width-pulse loop) and `MSG_INFO_RETRIES`'s orphan status — F-141-07, **Phase 146 / CLOSE-04**,
  wording only; a wording-only catalog change is a zero-byte firmware diff.
- **`native_trace_v131` re-freeze and the frozen-vs-new attributable diff** — **Phase 144 / TEST-06**.
- **Cross-phase flash/RAM reconciliation and the `size_baseline.json` update** — **Phase 144 / TEST-08**.
- **Fixing F-141-11** (`test_flash_path_record_sync.py` asserting whole-repo porcelain instead of the one
  file it tests) — still orphaned and unassigned. It will bite this phase too: commit in-flight changes
  before running the full firmware suite.
- **Fixing F-138-05** (`check_size_baseline.py`'s uncaught `KeyError` on an unknown native env) —
  inherited, accepted, not fixed. Owner `henols`.
- **`--pulse-us` on any command other than `write`** — D-18. Nothing else emits a program pulse.

### Reviewed Todos (not folded)

Seven todos matched by keyword; none folded. The top four scored 0.9 on bare-word overlap alone
("error", "phase", "write", "firmware", "firestarter") and belong to other families:

- **"Skip VPP error/warning checks when VPP is unused (reads/blank-checks)"** (score 0.9) — reviewed and
  **deferred again**, with the reason already recorded in `142-CONTEXT.md`: `PROJECT.md`'s v1.31
  out-of-scope list keeps VPP validation behaviour unchanged except where a change is required for safe
  shared cleanup, and skipping the check on reads is a behaviour change. Deferred by `139-`, `140-`,
  `141-`, `142-CONTEXT.md` and now this phase — it needs an owner outside v1.31. This phase touches no
  VPP path at all.
- **"FM1608 byte 0 write never lands — register cache-skip elides all three shift-register strobes"**
  (score 0.9) — adjacent to F-141-09's elision finding and worth remembering as a *testing* caution
  (noted in Established Patterns above), but it is an FRAM write-path defect on a different family. Not
  folded.
- **"CONFIG_VERSION is not bumped when a calibration default changes"** (score 0.9) — EEPROM config
  migration, backlog 999.1's territory. No overlap.
- **"Prove the PlatformIO dev-tools build flag fails CLOSED"** (score 0.9) — a build-flag question; this
  phase adds no dev-gated surface (`--pulse-us` is on production `write`, D-18).
- **"AT28C256 write-path failure (gh#20)"** (score 0.6) — protocol `0x0D`, a different family, and
  explicitly out of D-06's scope.
- **"avrdude MCU-detection fallback for blank-chip / wrong-firmware recovery"** (score 0.6) — bare-word
  match on "firmware"/"phase"; firmware-install territory, untouched here.

</deferred>

---

*Phase: 143-Host-Timeout-Progress-Pulse-Override*
*Context gathered: 2026-08-12*
