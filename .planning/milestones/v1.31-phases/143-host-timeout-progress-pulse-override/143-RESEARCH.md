# Phase 143: Host Timeout, Progress & Pulse Override - Research

**Researched:** 2026-08-12
**Domain:** Cross-repo (Python CLI transport/CLI surface + AVR firmware ack & per-byte loop instrumentation)
**Confidence:** HIGH on every code-located claim; MEDIUM on flash-cost and per-pulse-overhead estimates

> ⚠️ **READ `## Blocking Findings` BEFORE PLANNING ANY TASK.** Three findings falsify premises that
> `143-CONTEXT.md` decisions D-02, D-08 and D-13 rest on. Two of them are hard blockers; one of them
> means the phase as specified would **break** HOST-03 on the Uno. None can be worked around by
> re-ordering tasks.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Copied verbatim from `143-CONTEXT.md` `<decisions>`. Research annotations appear **only** in
`## Blocking Findings` and `## Decision Reconciliation`, never inside this block.

**Repo scope**

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
  Phase 146 / CLOSE-04's.

**Progress during a long block (HOST-02)**

- **D-02:** **Firmware emits the EXISTING `MSG_DATA_PROGRESS` (`0xE0`) from inside the per-byte
  loop.** Chosen over a host-only tick and over an INFO-band heartbeat. Costs **no new message id**.
  **`0xBF` therefore stays free.**
- **D-03:** **The emission is TIME-bounded (`millis()` since the last frame), not byte-counted.**
- **D-04:** **The host applies the frame's `current` and IGNORES the frame's `total`.** A dedicated
  write-progress branch sets the bar position absolutely; `set_progress`'s rebuild path is not
  reached. **The arithmetic the host owes:** `0xE0` carries an **absolute chip address**, but the
  write bar's origin is 0, so the host must subtract the write's start address.
- **D-05:** **The host must NOT ack the progress frame.** The write main-phase branch uses
  `ack_data=False`. **The second half of the same integration:** `_main_phase_send_data`'s loop
  handles only `MAIN`/`ERROR`/`OK` and **raises** on anything else. The loop needs a DATA branch.
- **D-06:** **The emission is EPROM-path only, and that is an explicit non-claim.**

**Response timeout (HOST-01)**

- **D-07:** **The budget is computed from the datasheet-derived pulse counts, and the FIRMWARE
  computes it.** No datasheet-derived value is duplicated host-side.
- **D-08:** **The carrier is a CAP-03 length-discriminated extension of `MSG_OK_READY`'s existing
  variable-length param blob — no catalog edit, no codegen, no new id.** **The hazard:** CAP-02's
  tail is itself variable-length, so the budget field must be read at the **computed `ver_end`
  offset**, never a fixed index.
- **D-09:** **The advertised number is already padded — the firmware owns the safety margin.** The
  host uses the value verbatim and applies no multiplier of its own.
- **D-10:** **An absent advertisement falls back to a generous fixed write-path timeout — never to
  10 s, never to a refusal.** **Recorded default: 120 s**, derived rather than picked. Research may
  revise the number; it may not revise the *derivation requirement*.
- **D-11:** **The formula must bound per-byte time as `min(max_pulses × pulse, energy_cap_us)`, plus
  an overprogram term of `min(3 × overprogram_factor × pulse, overprogram_cap_us)`.**
  `energy_cap_us == 0` means **UNCAPPED**, not "cap at zero".
- **D-12:** **`DEFAULT_RESPONSE_TIMEOUT` (10 s) is left untouched and keeps applying to every
  non-write path.**
- **D-13:** **`_read_and_parse_lines` is not modified. Full stop.** This phase changes the timeout
  **argument** at write call sites and extends the `_decode_id_frame` **override seam** — both
  outside the fence.

**`--pulse-us` (HOST-04, HOST-05)**

- **D-14:** **The override rides the DB dict, following the `read_strobe_us` precedent verbatim.**
  `write_eprom` takes a `pulse_us` parameter, shallow-copies `eprom_data_dict` when non-zero
  (**never** mutating the caller's dict) and sets the existing `"pulse-delay"` key. **No new wire
  field and no new command.**
- **D-15:** **Bounds are enforced by `click.IntRange(1, 65535)` on the option.** **The bound's
  provenance:** `1..65535` is **minipro parity**, **not** the wire type.
- **D-16:** **The `0x0B`-only over-cap case is left to the firmware's existing pre-flight refusal;
  the host mirrors no table value to pre-empt it.**
- **D-17:** **Using `--pulse-us` always prints a default-visible report line naming both values.**
- **D-18:** **`--pulse-us` is exposed on `write` only.**

**HOST-03**

- **D-19:** **HOST-03 is render-and-prove plus a remediation hint, not a re-plumb.** A hint appended
  on the `_boot_block_hint_message` pattern for `0xBD`/`0xBE`/`0xAE`, plus a host test proving the id
  surfaces as a program failure naming the address.
- **D-20:** **No host code may expect `MSG_ERR_WRITE_FAILED` (`0xB1`) on a 27C write.**
- **D-21:** **The hint must state D-05's aborted-block semantics — no retry advice, no resumption
  implication.**

**Flash and gate posture**

- **D-22:** **Flash posture: it must FIT. The MERGE-05 band is not this phase's concern.** MERGE-05
  stays RED (Phase 144 / TEST-08), `size_baseline.json` is read-only, **no** predictions artifact,
  **no** shrink ladder unless the build overruns. `leonardo` must still **build**. F-142-08 hands
  this phase **2130 B**. `check_build_warnings.py`'s native watermark sits at **1166 with zero
  headroom**.
- **D-23:** **All `eprom.cpp` edits are confined to ONE plan and ONE commit, landing the re-derived
  D-13 golden with them.** The golden's `meta.how_to_update` is binding. **This phase must add no new
  tier-1 protocol-keyed site.**
- **D-24:** **`native_trace_v131` stays RED and is NOT re-frozen here.**
- **D-25:** **Every new gate leg is seen RED on a planted violation before its GREEN is believed.**

### Claude's Discretion

- D-14, D-15, D-16, D-17, D-18 — the whole `--pulse-us` surface.
- D-19, D-20, D-21 — HOST-03's scope.
- The advertised budget's **encoding** — recorded default: a `uint16_t` of **seconds**,
  ceiling-rounded with a 1 s floor, appended after CAP-02's variable-length identity tail.
  `uint32_t` milliseconds is the alternative. **Research may override on wire-economy or
  decode-symmetry grounds.**
- The time-bound constant in D-03, the exact per-frame payload source, and where the emission call
  sits inside the loop — subject to D-23 and D-22.
- Plan decomposition and wave structure, including which plan owns the host half and which owns the
  firmware half. The host's D-10 fallback path is testable with **no** firmware change at all.

### Deferred Ideas (OUT OF SCOPE)

- Fixing `set_progress`'s rebuild-on-differing-total (`eprom_operations.py:268-270`).
- Intra-block progress for the non-EPROM write families (flash `0x05`, EEPROM `0x0D`, SRAM, …).
- A combined byte-count-OR-time cadence.
- Host-side warning for a `--pulse-us` above `0x0B`'s energy cap.
- Reconciling H3 (unclamped `extract_long` on `pulse-delay`) — **Phase 146 / CLOSE-04**.
- Correcting the roadmap's "Phase 143 is independent of 140–142" prose — **Phase 146 / CLOSE-04**.
- `DBG_PULSE_DELAY_MISMATCH`'s stale wording, `MSG_INFO_RETRIES`'s orphan status — **Phase 146**.
- `native_trace_v131` re-freeze and the frozen-vs-new diff — **Phase 144 / TEST-06**.
- Cross-phase flash/RAM reconciliation and the `size_baseline.json` update — **Phase 144 / TEST-08**.
- Fixing F-141-11 (`test_flash_path_record_sync.py` whole-repo porcelain) — orphaned.
- Fixing F-138-05 (`check_size_baseline.py` `KeyError`) — inherited, owner `henols`.
- `--pulse-us` on any command other than `write`.
- "Skip VPP error/warning checks when VPP is unused" — deferred again; this phase touches no VPP path.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description (`.planning/REQUIREMENTS.md:216-224`) | Research Support |
|----|--------------------------------------------------|------------------|
| HOST-01 | A write whose block exceeds the previous 10 s `DEFAULT_RESPONSE_TIMEOUT` completes without a serial timeout. | §Architecture Pattern 1 (budget plumbing), §Pattern 2 (CAP-03 carrier), §Budget Arithmetic (corrected formula + verified worst-case table), Blocking Finding **BF-2** (D-02 cannot carry this on Uno-class), Pitfall 6 (test oracle must not burn wall-clock) |
| HOST-02 | The user sees progress during a long write rather than a silent stall. | §Pattern 3 (firmware emission site + time gate), Blocking Finding **BF-2** (Leonardo-only; `#ifndef SERIAL_ON_IO` guard), Pitfall 1 (bar-fighting with `progress.update`), Pitfall 2 (`set_progress` rebuild), §Code Example 3 |
| HOST-03 | A byte that fails at `max_pulses` surfaces as a **program failure naming the address**, not as a transport error. | §Pattern 5 (hint on the `_boot_block_hint_message` seam), Blocking Finding **BF-2** (naive D-02 would *break* this on Uno via deferred-buffer exhaustion), §Code Example 5, §Don't Hand-Roll |
| HOST-04 | `firestarter write --pulse-us N` overrides the database pulse for that run, using the existing wire field. | §Pattern 6 (`read_strobe_us` precedent verbatim), §Code Example 6, §Verified wire-key facts |
| HOST-05 | `--pulse-us` outside `1..65535` is refused with an actionable message **before any serial byte is sent**. | §Pattern 7, Pitfall 3 (**`default=0` + `IntRange(1,65535)` breaks every `write` invocation** — empirically proven), §Decision Reconciliation D-15 (the "before AppContext builds" rationale is false; the guarantee still holds) |
</phase_requirements>

---

## Summary

This phase is two loosely-coupled halves that meet at one wire field. The **host half** (timeout
plumbing, a DATA branch in the write loop, an error hint, `--pulse-us`) is fully implementable and
testable with zero firmware change, using patterns that already ship in-tree. The **firmware half**
(a per-block worst-case time budget advertised on the setup ack, plus intra-block progress emission)
is where the research found the phase's real risk — and it is not the risk `143-CONTEXT.md`
anticipated.

Three findings change what the plan must do:

1. **The v1.31 firmware branch cannot connect to the v1.31 app branch at all.** The firmware branch
   forked at `3085084`, one commit *before* firmware PR #49 landed CAP-02 on `origin/beta`. It emits
   a 2-byte `MSG_OK_READY`; the app branch's `_probe_port` raises `FirmwareOutdatedError` when the
   ack carries no identity, and `tests/test_fwguard.py::test_absent_identity_refuses` asserts exactly
   that refusal. D-08's "append after CAP-02's variable-length identity tail" has no tail to append
   after. CAP-02's firmware emit must be ported into the v1.31 branch before CAP-03 exists, and it is
   a hard precondition for Phase 145's bench work independently of this phase.
2. **D-02's intra-block emission is structurally impossible on `uno`/`uno328pb`, and a naive
   implementation would break HOST-03 there.** Both boards build with `-D SERIAL_ON_IO`;
   `rurp_set_programmer_mode()` calls `rurp_serial_end()` and sets `com_mode = false`, and the Uno's
   strong `rurp_log_id` override then *defers* frames into a 4-slot buffer flushed only when
   communication mode is restored — i.e. **after the whole block**. Filling those 4 slots with
   progress frames means a subsequent `MSG_ERR_MAX_PULSES` frame is **silently dropped**, converting
   the program failure HOST-03 exists to surface into the transport timeout HOST-03 exists to avoid.
3. **D-11's per-byte formula under-estimates by 2× on a reachable input.** `min(max_pulses × pulse,
   energy_cap_us)` is wrong whenever `pulse` does not divide `energy_cap_us`; at `--pulse-us 49999`
   on `0x0B` the true per-byte bound is 99 998 µs (two pulses), not 50 000 µs — 102.4 s per
   1024-byte block against a formula that says 51.2 s. `firestarter/CLAUDE.md`'s own `0x0B` row
   already documents the 99 998 µs figure (F-141-10), so the corrected formula is citable in-tree.

**Primary recommendation:** decompose into five plans — one firmware plan for a **new, unpinned**
`src/proms/eprom_budget.{h,cpp}` translation unit carrying the corrected budget arithmetic with
native tests; one firmware plan for `firestarter.cpp` (port CAP-02, append CAP-03, call the budget
function) with a source-contract gate; one firmware plan owning **all** `eprom.cpp` edits plus the
re-derived golden in a single commit, with the intra-block emission compiled out under
`#ifdef SERIAL_ON_IO`; and two host plans (timeout + progress + hint; `--pulse-us`). Take the
`uint16_t`-seconds encoding, apply a *derived* host-side plausibility clamp, and keep D-10's 120 s
fallback — the research confirms 120 s covers every reachable `0x0B` width and every shipped-database
`0x07`/`0x08` width.

---

## Blocking Findings

### BF-1 — CAP-02's firmware half is NOT in the v1.31 firmware branch. D-08 has nothing to append to, and the two branches cannot talk.

**Evidence (all `[VERIFIED: codebase]`):**

| Fact | Location |
|------|----------|
| v1.31 firmware emits a **2-byte** ack: `LOG_OK_ID_U16(MSG_OK_READY, (uint16_t)DATA_BUFFER_SIZE);` | `firestarter/src/firestarter.cpp:157` |
| CAP-02's emit (`[bufsize u16][hw_rev u8][ver_len u8][ver bytes]`, `uint8_t _ready[4+32]`, `LOG_OK_ID_BYTES`) exists only on `origin/beta` | commits `13eb350` / `b1737b2` (PR #49) |
| `git merge-base --is-ancestor b1737b2 HEAD` → **exit 1** (not an ancestor); `git branch -a --contains b1737b2` → `remotes/origin/beta` only | measured this session |
| Local `beta` is at `3085084`; `origin/beta` is at `6fab4ea`; the v1.31 branch's merge-base with local `beta` is `3085084` | measured this session |
| App branch **requires** the identity: `identity = communicator.firmware_identity`; `if version_match is None: raise FirmwareOutdatedError("Programmer did not report a firmware version in its operation-setup ack…")` | `firestarter_app/firestarter/serial_comm.py` `_probe_port` |
| The refusal is deliberate and **tested**: `test_absent_identity_refuses` — "Pre-CAP-02 firmware emits the 2-byte MSG_OK_READY, leaving firmware_identity None… the host must NOT treat 'no version reported' as 'version fine'." | `firestarter_app/tests/test_fwguard.py:123-134` |
| `FirmwareOutdatedError` is re-raised out of `_probe_port`, not swallowed | `serial_comm.py`, `except (SerialError, FirmwareOutdatedError)` arm |

**Consequences:**

- **Every** command from the v1.31 app against a v1.31 firmware build fails at connect. This is not a
  Phase 143 regression — it is already true on the operator's bench today.
- D-08's stated seam ("firmware appends bytes, host reads further into `params_bytes`") is
  unimplementable as-is: offsets 2 and 3 are already claimed by the host decoder's CAP-02 arm
  (`if len(params_bytes) >= 4: self.hw_revision = params_bytes[2]; ver_end = 4 + params_bytes[3]`,
  `serial_comm.py:370-376`). Writing the budget at offset 2 makes the host read `budget_hi` as a
  hardware revision and `budget_lo` as a version length — a misparse, not a graceful degradation.
- Phase 145 (BENCH-01: full write→read→verify on Leonardo) is blocked by this independently of
  Phase 143.

**Recommended disposition (planner must decide, operator may want to confirm):** port CAP-02's emit
into the v1.31 firmware branch **in the same plan and commit that adds CAP-03**, extending the one
`_ready[]` pack block rather than adding a second one. Cherry-pick `13eb350` (the unsquashed commit)
as the starting point and then append 2 bytes. Cost is already measured by the upstream commit
message: **+34 B flash on uno, 0 B RAM** — and this is *exactly* the +34 B × 3 targets drift that
STATE.md's OD-2 recorded as the reason the firmware forked at `3085084` rather than at the live tip.
Porting it therefore reproduces a **known, already-recorded, already-operator-accepted**
`check_size_baseline.py` RED, not a new one. D-22 already puts `size_baseline.json` off-limits and
MERGE-05 already RED, so nothing new goes red that was green.

**Do not** attempt to satisfy D-08 without CAP-02 present.

---

### BF-2 — D-02's intra-block emission cannot reach the host on `uno`/`uno328pb`, and filling the 4-slot deferred buffer would BREAK HOST-03 there.

**Evidence (all `[VERIFIED: codebase]`):**

| Fact | Location |
|------|----------|
| `uno` and `uno328pb` build with `-D SERIAL_ON_IO`; `leonardo` and `native` do not | `firestarter/platformio.ini:38,55` |
| Without `SERIAL_ON_IO`, both mode functions are typed **no-ops** | `include/rurp_shield.h:64-76` |
| With it, `rurp_set_programmer_mode()` sets `com_mode = false`, calls `rurp_serial_end()`, and drives PD0 as data-bus bit 0 | `src/boards/uno_rurp_shield.cpp` (`rurp_set_programmer_mode`) |
| The Uno's strong `rurp_log_id` override **defers** rather than emits while `com_mode == false`, into `deferred_log[DEFERRED_LOG_MAX]` with `DEFERRED_LOG_MAX 4`, `DEFERRED_PARAM_MAX 8` | `src/boards/uno_rurp_shield.cpp:33-40, 109-135` |
| Overflow behaviour is **silent drop**: `// else: buffer full … drop excess rather than risk emitting on the active bus` | same file, end of `rurp_log_id` |
| Deferred frames flush **only** in `rurp_set_communication_mode()` | same file |
| The whole per-byte loop runs inside one programmer-mode window: `rurp_set_programmer_mode(); callback(handle); rurp_set_communication_mode();` | `src/operation_utils.cpp:393-400` (`_execute_operation`) |
| The Uno sizing rationale is explicit: *"an operation emits at most ~1-2 critical frames per programmer-mode window, so DEFERRED_LOG_MAX=4 has ample headroom"* | `src/boards/uno_rurp_shield.cpp:24-33` |
| The identical trap is already documented at the only existing `0xE0` emitter: *"On the Uno, `rurp_log_id` is com_mode-gated and this function runs in programmer mode, so a direct emit here is silently dropped."* | `src/proms/memory.cpp:520-527, 461-467` |
| `MSG_DATA_PROGRESS` payload is exactly 8 bytes (`u32`,`u32`) — precisely `DEFERRED_PARAM_MAX` | `firestarter_app/firestarter/messages.py:765-773` |
| `MSG_ERR_MAX_PULSES` / `MSG_ERR_ENERGY_CAP` are 4-byte payloads emitted from *inside* the same window | `src/proms/eprom.cpp:215-224` |

**The failure chain on a `uno`, in order:**

1. Progress frames emitted inside the per-byte loop are deferred, not sent. They **cannot** feed the
   host's response window — so D-13's stated reason for HOST-01 working ("the resets already fire on
   every yielded frame, which is *why* D-02's emission feeds the window for free") is **false on
   Uno-class boards**. HOST-01 is carried entirely by D-07/D-08/D-10 there.
2. After 4 progress frames the buffer is full. Every later frame in that window is dropped.
3. A byte that fails at `max_pulses` calls `eprom_internal_report_budget_failure`, which emits
   `MSG_ERR_MAX_PULSES` — **dropped**.
4. `handle->response_code = RESPONSE_CODE_ERROR` still propagates: `_check_response` returns false →
   `_execute_operation` returns `ERROR` → `_process_incoming_data` returns false → `finished = true`
   → `command_done()`. The firmware goes idle having emitted **no error frame**.
5. The host is blocked in `_main_phase_send_data`'s `get_response()`; nothing arrives; it raises
   `SerialTimeoutError`. **A transport error — exactly what HOST-03 forbids.**
6. This is a *regression*: today, without progress frames, the 4-byte error frame fits in the
   deferred buffer and is delivered on the flush. **HOST-03 works on Uno today and D-02 would break
   it.**

**Also note:** D-05's ack-desync hazard is symmetrically Leonardo-specific. On the Uno the UART is
*off* during the block and `rurp_set_communication_mode()` drains the RX buffer
(`while (SERIAL_PORT.available()) SERIAL_PORT.read();`), so a stray mid-block ack is discarded. On
the Leonardo it is buffered, and `op_get_message` returns `OP_MSG_ACK`, which hits
`_process_incoming_data`'s `default: return false` (`src/eprom_operations.cpp:113-118`) — the write
aborts with **no error frame at all**. D-05 is load-bearing and its failure mode is severe.

**Recommended mitigation — compile the emission out on Uno-class targets:**

```c
/* HOST-02 is a Leonardo-and-later capability by construction, not by choice.
 * On SERIAL_ON_IO targets the UART is torn down for the whole programmer-mode
 * window (rurp_set_programmer_mode -> rurp_serial_end), rurp_log_id defers
 * into a 4-slot buffer flushed only after the block, and a 5th frame is
 * DROPPED -- which would consume the slots MSG_ERR_MAX_PULSES needs and turn
 * a program failure into a host transport timeout (HOST-03's exact
 * anti-goal). See src/boards/uno_rurp_shield.cpp:24-33 and
 * src/proms/memory.cpp:520-527 for the same trap already documented twice. */
#ifndef SERIAL_ON_IO
    if ((uint32_t)(millis() - last_emit_ms) >= EPROM_PROGRESS_EMIT_INTERVAL_MS) {
        last_emit_ms = millis();
        LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, addr, handle->mem_size);
    }
#endif
```

Rejected alternatives, with reasons:

| Option | Why not |
|--------|---------|
| Expose `com_mode` via a new accessor and gate at runtime | Costs an accessor on every target; still delivers no intra-block progress on Uno; still no mechanism to reserve error slots |
| Raise `DEFERRED_LOG_MAX` | RAM cost on the tightest-RAM target (`uno` 1573/2048 used) and still zero intra-block delivery — fixes nothing |
| Reserve headroom (emit at most `DEFERRED_LOG_MAX - 2` frames) | Fragile invariant across two files; still no intra-block delivery |

**Consequences for the record:** D-06's non-claim gains a **second dimension**. The honest statement
is: *intra-block write progress is emitted on the EPROM path only, and delivered on `leonardo` only.*
Both halves must appear in the phase record and in HOST-02's requirement note. This is the
D-09/F-120-02 class of incident (a two-repo requirement that passes its own phase's verification
while being false end to end) and the CONTEXT's own `code_context` already names that precedent.

**Corollary — the native oracle is structurally blind to this.** `host_stubs_common.inc:268` provides
a plain capturing `rurp_log_id` with **no** `com_mode` gate, and `build_src_filter` is
`+<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>` — so
`src/boards/uno_rurp_shield.cpp` is compiled in **no** native env. A native test will happily show
the frames being emitted. The `#ifndef SERIAL_ON_IO` guard therefore needs a **source-contract**
gate (Phase 142's `command_done()` precedent — a pytest leg that greps the source and says so), not
a behavioural one.

---

### BF-3 — D-11's per-byte formula under-estimates by up to 2× on a reachable `--pulse-us` value.

D-11 states the bound as `min(max_pulses × pulse, energy_cap_us)`. The shipped loop
(`src/proms/eprom.cpp:334-361`) increments `accumulated += org_delay` and only *then* tests
`accumulated >= energy_cap_us`, so the real number of pulses is `min(max_pulses, ceil(C / P))` and
the real per-byte bound is `min(max_pulses, ceil(C / P)) × P`, which exceeds `C` whenever `P` does
not divide `C`.

`[VERIFIED: computed]` and independently `[CITED: firestarter/CLAUDE.md §Algorithm Handlers, 0x0B row]`
which already documents this precise arithmetic — *"the actual achievable worst case is two pulses at
`w = 49999` … giving `2 * 49999 = 99998` us"* (F-141-10).

| Protocol | `--pulse-us` | Pulses | True per-byte µs | True block s (1024 B) | D-11 naive per-byte µs | Naive block s | Under-estimate |
|----------|-------------|--------|------------------|------------------------|------------------------|---------------|----------------|
| 0x07/0x08 | 100 (modal) | 25 | 2 500 | 2.6 | 2 500 | 2.6 | 0 % |
| 0x07/0x08 | 1000 (max shipped) | 25 | 25 000 | 25.6 | 25 000 | 25.6 | 0 % |
| 0x07/0x08 | 65535 (host max) | 25 | 1 638 375 | **1677.7** | 1 638 375 | 1677.7 | 0 % |
| 0x0B | 200 | 250 | 50 000 | 51.2 | 50 000 | 51.2 | 0 % |
| 0x0B | 300 | 167 | 50 100 | 51.3 | 50 000 | 51.2 | 0.2 % |
| 0x0B | 500 (modal) | 100 | 50 000 | 51.2 | 50 000 | 51.2 | 0 % |
| 0x0B | 25001 | 2 | 50 002 | 51.2 | 50 000 | 51.2 | 0.004 % |
| 0x0B | **49999** | 2 | **99 998** | **102.4** | 50 000 | 51.2 | **100 %** |
| 0x0B | 50000 | 1 | 50 000 | 51.2 | 50 000 | 51.2 | 0 % |

`--pulse-us 49999` on a `0x0B` part is host-legal (inside `1..65535`) and firmware-accepted
(`energy_cap_us > 0 && pulse_delay > energy_cap_us` is false at 49999, `eprom.cpp:105-110`). A budget
computed with D-11's literal formula would time out a **working** write at ~51 s — the "too tight"
failure D-09 names as strictly worse than a generous ceiling.

**Second error in the same decision:** D-11's overprogram term, `min(3 × overprogram_factor × pulse,
overprogram_cap_us)`, does not match the shipped function. `eprom_overprogram_us(pulse_count,
pulse_us, factor, cap_us)` computes `factor × pulse_count × pulse_us` clamped at `cap_us`
(`eprom.cpp:189-195`). The `3` in `eprom_params.h`'s comment (`min(3 x overprogram_factor x pulse,
cap)`) is a documentation defect that double-counts the datasheet's `3×N` rule; `3` *is* the factor
and `N` *is* `pulse_count`. With `factor = 3`, `pulse = 1000`, `max_pulses = 25`, D-11's literal form
yields 9 000 µs where the shipped function yields `min(75 000, 75 000) = 75 000` µs — an 8.3× *under*
-estimate for the first future row that sets a non-zero factor.

**Recommended correction — reuse the shipped function instead of restating it:**

```c
/* Per-byte worst case, corrected (BF-3). Two departures from the CONTEXT's
 * D-11 wording, both measured against the shipped loop:
 *   (a) the pulse count is min(max_pulses, ceil(C/P)), not implied by
 *       min(max_pulses*P, C) -- the loop tests `accumulated >= C` AFTER the
 *       increment, so the last pulse can overshoot C by up to P-1.
 *   (b) the overprogram term calls eprom_overprogram_us() with pulse_count =
 *       max_pulses rather than re-deriving it, so the budget cannot drift from
 *       runtime behaviour when a future row sets overprogram_factor != 0.
 * energy_cap_us == 0 is UNCAPPED (eprom_params.h), guarded exactly as
 * eprom.cpp:105 guards it. */
static uint32_t eprom_worst_pulses(uint8_t max_pulses, uint32_t pulse_us, uint32_t energy_cap_us) {
    if (energy_cap_us == 0 || pulse_us == 0) {
        return max_pulses;
    }
    uint32_t by_energy = (energy_cap_us + pulse_us - 1) / pulse_us;   /* ceil */
    return by_energy < max_pulses ? by_energy : max_pulses;
}
```

Then `per_byte_us = n × pulse_us + eprom_overprogram_us((uint8_t)n, pulse_us, factor, cap)`.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Per-block worst-case time budget **computation** | Firmware — `src/proms/` (natively compiled, table-adjacent) | — | D-07 locks the computation to the side that owns the datasheet-derived table; `src/proms/` is the only firmware directory inside every native `build_src_filter`, so the arithmetic gets a real unit-test oracle |
| Budget **advertisement** (wire encoding + pack) | Firmware — `src/firestarter.cpp` (`init_programmer_framed`) | — | The ack is emitted there and nowhere else; this is thin glue that *calls* the tier above |
| Budget **consumption** (decode + clamp) | Host — `serial_comm.py` `_decode_id_frame` override | — | D-08/D-13: the sanctioned extension seam outside the GATE-1.8d ring-fence |
| Write-path response **timeout selection** | Host — `eprom_operations.py` write call sites | — | D-12: per-call-site, so read/verify/blank/erase/id keep 10 s |
| Intra-block **progress emission** | Firmware — `src/proms/eprom.cpp` per-byte loop | — | Only the firmware knows bytes *programmed*; **Leonardo-only** delivery (BF-2) |
| Intra-block progress **rendering** | Host — `_main_phase_send_data` DATA branch | `ClassProgressHandler.set_progress` | D-04: the write branch differs, not the frame; the shared handler is untouched |
| Program-failure **rendering + remediation hint** | Host — `_boot_block_hint_message`-shaped helper + the existing ERROR branch | `_raise_for_error_response` | D-19: the typed-exception plumbing already exists; only the hint is new |
| `--pulse-us` **bounds enforcement** | Host — Click parameter type | — | D-15: parse-time refusal, structurally before any port is opened |
| `--pulse-us` **transport** | Host — DB-dict shallow copy → `_setup_operation`'s `command_dict` | Firmware `json_parser.c` `get_delay` | D-14: the `"pulse-delay"` key already exists on the wire and is already parsed |
| `--pulse-us` **over-cap refusal** | Firmware — `configure_eprom`'s pre-flight `MSG_ERR_PULSE_TOO_WIDE` | — | D-16: the backstop already exists and names itself as this phase's backstop |

---

## Project Constraints (from CLAUDE.md)

### Meta repo (`/workspaces/CLAUDE.md`)

- Only `.planning/` and `.claude/` are tracked here. **Neither sub-repo is committed to meta** —
  plan `commits_land_in:` must name `firestarter`, `firestarter_app` **and** meta.
- **Serial-protocol changes must be kept in sync** between `firestarter_app/firestarter/serial_comm.py`
  and `firestarter/src/firestarter.cpp`. CAP-03 is exactly such a change: both sides move together.
- Constants/flag bits are duplicated between `firestarter_app/firestarter/constants.py` and
  `firestarter/include/firestarter.h` — **change both together**. D-07 deliberately adds nothing to
  `constants.py`, so this obligation is discharged by *not* mirroring the table.
- Board buffer sizes differ: **Uno 512 B, Leonardo 1024 B** — and buffer size affects chunked
  transfer in `eprom_operations.py`. The budget must be computed against the firmware's own
  `DATA_BUFFER_SIZE`, which is the same value CAP-01 already advertises at ack offsets 0-1.

### App repo (`/workspaces/firestarter_app/CLAUDE.md`)

- `firestarter/messages.py` is **codegen-generated** from meta's `tools/catalog/messages.toml` —
  never hand-edit. D-08 means this phase needs no catalog change; a CI leg (`codegen drift gate`)
  enforces it.
- `firestarter/data/chip_database.json` is generated — do NOT edit by hand. Out of scope anyway.
- Tooling gate: `ruff check` + `ruff format --check` + `mypy` (**strict on 8 modules including
  `serial_comm.py`**) + `pytest --cov-fail-under=70`, all enforced by `.github/workflows/ci.yml` on
  every branch push.
- CAP-03's new `SerialCommunicator` attribute lands in a **mypy-strict** module and must be annotated
  and declared at class level as well as in `__init__` — the existing CAP-02 comment
  (`serial_comm.py:104-113`) explains why: `conftest.make_comm` builds instances via `__new__`, and
  an instance-only attribute becomes an `AttributeError` swallowed by `_probe_port`'s broad
  `except Exception`, degrading to "no programmer found". **`tests/conftest.py`'s `make_comm` factory
  must gain the new attribute in the same change.**

### Firmware repo (`/workspaces/firestarter/CLAUDE.md`)

- `include/messages.h` is codegen-generated and ID-only.
- §Algorithm Handlers documents the corrected `0x0B` energy-cap worst case (**99 998 µs**) — this is
  the corrected source, not `141-CONTEXT.md`. Any row text this phase changes moves in lockstep.
- PROGMEM table reads go through `pgm_read_byte` / `pgm_read_dword` — never a direct dereference.

---

## Standard Stack

**No new third-party dependency is required or recommended for this phase.** Every mechanism it needs
already ships in-tree. The stack table below records the *existing* versions the work must be
compatible with.

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `click` | 8.4.2 (CI-replica venv), 8.3.3 (ambient), floor `>=8.1` in `pyproject.toml` | `--pulse-us` option, `IntRange` bounds | Already the CLI framework since the v1.8 argparse→Click migration; `IntRange` is a first-party type, no new dep `[VERIFIED: pyproject.toml:50; python -c "import click"]` |
| `tqdm` | as installed | Progress bar behind `ClassProgressHandler` | Already the only bar in the tree `[VERIFIED: eprom_operations.py:240-282]` |
| `pyserial` | as installed | Transport | Unchanged; `_read_and_parse_lines` is ring-fenced |
| Unity + ArduinoFake | as pinned by PlatformIO | Native firmware tests | Already the framework for all 20 native suites |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `struct` (stdlib) | — | `>H` pack/unpack of the CAP-03 field | Mirror CAP-01's `struct.unpack(">H", …)` exactly `[VERIFIED: serial_comm.py:357]` |
| `pytest` + `unittest.mock` | as pinned | Host tests | 1547 tests currently collected `[VERIFIED: pytest --collect-only]` |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `click.IntRange(1, 65535)` | Hand-rolled `if not 1 <= n <= 65535: raise click.BadParameter(...)` | Bespoke wording, but moves the pre-serial guarantee from Click's parse order into a code position a later edit can move — D-15 already rejected it |
| `uint16_t` seconds on the wire | `uint32_t` milliseconds | 2 extra bytes for granularity a timeout cannot use; **research confirms seconds** — see §Budget Encoding |
| New `src/proms/eprom_budget.cpp` TU | Put the budget function in `eprom.cpp` or `eprom_params.cpp` | Both are pinned by `tests/golden/protocol_branch_inventory.json`'s `blob_shas`, so either choice folds the arithmetic into D-23's single `eprom.cpp` commit. A new TU under `src/proms/` is **not** pinned, is still natively compiled (`+<proms/>` is a directory glob), and lets the arithmetic land in its own plan with its own native tests |

**Installation:** none. No `pip install`, no `npm install`, no new PlatformIO library.

---

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.**

Verified by inspection of the phase's decision set: D-14/D-15 use `click` (already a declared
dependency, `pyproject.toml:50`), D-08 uses `struct` (stdlib), and the firmware half uses only
in-tree headers. No `pip install`, `npm install`, `cargo add`, or `lib_deps` addition appears anywhere
in the CONTEXT's decisions or in this research's recommendations.

`slopcheck` was therefore not run. If a plan later proposes a new dependency, the Package Legitimacy
Gate must be run before that plan is approved.

---

## Runtime State Inventory

> Included despite this not being a rename phase, because BF-1 is a **runtime-state** finding: the
> firmware image on the bench board is state that no repo edit updates.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| **Flashed firmware on bench boards** | The operator's boards carry whatever was last flashed. A v1.31 build emits a 2-byte `MSG_OK_READY` and is **refused** by the v1.31 app (BF-1). A released `beta` build (`3.0.0b20`-era) has CAP-02 but not CAP-03, so it exercises D-10's fallback path. | Port CAP-02 (BF-1), then **re-flash before any bench check**. Phase 145's evidence must record which image was on the board. |
| **Stored data / databases** | None. No datastore keys, collection names or user_ids are involved — this phase adds no persisted field. `chip_database.json` is explicitly out of scope. | None — verified by the CONTEXT's out-of-scope list and by grep: no new `JSON_KEY_*` or DB field is proposed. |
| **Live service config** | None. No n8n workflow, Datadog service, Tailscale ACL or Cloudflare tunnel touches this phase. | None — verified: this phase's surface is one CLI flag and one wire field. |
| **Secrets / env vars** | `FIRESTARTER_DEV_ALLOW_PRE_V12` (existing bypass read in `_probe_port`) is the only env var on the affected path; it bypasses the **version** check, **not** the identity-absent refusal, so it does **not** unblock BF-1. `FIRESTARTER_SIZE_BASELINE` is read by two firmware gates. `FIRESTARTER_CONFIG_DIR` affects bench runs. | None changed. Note in the record that `FIRESTARTER_DEV_ALLOW_PRE_V12=1` does **not** work around BF-1 — the raise happens before `_validate_firmware_version` is reached. |
| **Build artifacts / installed packages** | `firestarter_app` is installed `-e`, so a source edit is live. `.pio/build/<env>` caches affect **cold vs warm** warning counts — the recorded 1166 native watermark is a **COLD** figure and a warm re-run measures 998. `.venv/ci-replica` (Python 3.11) is the CI-parity interpreter per 138-04. | Measure flash/warnings **cold** (`pio run -t clean -e <env>` then `pio run -e <env>`); run the host suite with `.venv/ci-replica/bin/python` from inside `/workspaces/firestarter_app`. |

---

## Architecture Patterns

### System Architecture Diagram

```
                          HOST  (firestarter_app)                                FIRMWARE (firestarter)
                          ───────────────────────                                ──────────────────────

  user types
  `firestarter write CHIP file.bin --pulse-us N`
        │
        ▼
  ┌──────────────────────────────┐
  │ Click parse                  │   HOST-05 gate: IntRange(1,65535) refuses
  │  cli() group callback runs    │   out-of-range HERE, before the handler body
  │  FIRST, then write()'s params │   → exit 2, zero serial bytes written
  │  are type-converted           │
  └──────────────┬───────────────┘
                 │ pulse_us valid or None
                 ▼
  ┌──────────────────────────────┐
  │ write() handler               │  D-17: report line naming DB pulse -> override
  │  resolve_chip() -> prog dict  │
  └──────────────┬───────────────┘
                 ▼
  ┌──────────────────────────────┐
  │ write_eprom(pulse_us=…)       │  D-14: shallow-copy dict, set "pulse-delay"
  └──────────────┬───────────────┘
                 ▼
  ┌──────────────────────────────┐   COBS+CRC8 setup frame
  │ _setup_operation              │ ─────────────────────────────►  ┌──────────────────────────┐
  │  command_dict = dict.copy()   │                                 │ loop(): read_data,       │
  └──────────────┬───────────────┘                                 │  CRC8, parse_json        │
                 │                                                  │  get_delay -> pulse_delay│
                 │                                                  │  configure_eprom:        │
                 │                                                  │   pulse fallback if 0,   │
                 │                                                  │   row=eprom_params_for,  │
                 │                                                  │   REFUSE if row==NULL,   │
                 │                                                  │   REFUSE 0xAE if pulse   │
                 │                                                  │     > energy_cap_us      │
                 │                                                  └────────────┬─────────────┘
                 │                                                               │
                 │       MSG_OK_READY  [bufsize u16][hw_rev u8][ver_len u8][ver…][BUDGET u16]  ◄── CAP-03
                 │  ◄──────────────────────────────────────────────────────────  │  (needs CAP-02
                 ▼                                                               │   ported first —
  ┌──────────────────────────────┐                                              │   BF-1)
  │ _decode_id_frame override     │  CAP-01 @0..1  → firmware_max_chunk
  │  (outside GATE-1.8d fence)    │  CAP-02 @2..3+ → hw_revision, identity
  │                               │  CAP-03 @ver_end → write_block_budget_s
  │  each field length-gated,     │  each absent → None (never an error)
  │  each with a plausibility     │
  │  clamp                        │
  └──────────────┬───────────────┘
                 │ budget_s or None
                 ▼
  ┌──────────────────────────────┐
  │ _probe_port gates             │  version gate needs CAP-02 identity  ← BF-1 blocks here
  │  → _validate_hardware_revision│
  └──────────────┬───────────────┘
                 ▼
  ┌──────────────────────────────┐
  │ _run_state_machine            │
  │  INIT  ── ack ──►             │ ───────────────►  eprom_write_init: erase?, blank check
  │        ◄── 0xE0 progress ───  │ ◄───────────────  (chunked 2048 B/step, one frame per step)
  │        ◄── INIT done ───────  │                   [10 s timeout, D-12 — unchanged]
  │                               │
  │  MAIN  ── ack ──►             │
  │   ┌───────────────────────┐   │
  │   │ get_response(TIMEOUT) │◄──┼─── OK: Req data ─  _process_incoming_data
  │   │  TIMEOUT = budget_s   │   │                    (waiting for a chunk)
  │   │   or 120 s fallback   │   │
  │   └──────────┬────────────┘   │
  │              │ OK             │
  │              ▼                │
  │      send chunk (COBS+CRC8)   │ ───────────────►  eprom_write_execute
  │              │                │                   ┌────────────────────────────────┐
  │              │                │                   │ once/block: assert HV route,   │
  │              │                │                   │             delay(500)          │
  │              │                │                   │ per byte:                       │
  │        ◄── 0xE0 progress ───  │ ◄─────────────────│   skip 0xFF / already-matching   │
  │        (Leonardo ONLY —        │  time-gated,      │   pulse -> verify, fixed width  │
  │         BF-2: deferred &       │  #ifndef          │   until converge / max_pulses / │
  │         dropped on Uno)        │  SERIAL_ON_IO     │   energy cap                     │
  │              │                │                   │ then: final verify pass (0x07/08)│
  │              │                │                   └────────────────┬───────────────┘
  │              │                │                                    │ on failure
  │        ◄── 0xBD/0xBE/0xAF ──  │ ◄──────────────────────────────────┘
  │              │                │   HV off, response_code=ERROR, address does NOT advance,
  │              ▼                │   command_done() -> no further blocks accepted
  │   _raise_for_error_response   │
  │    + D-19 hint (0xBD/0xBE/0xAE)│
  │    -> EpromOperationError      │
  │              │                │
  │  END   ── ack ──►             │
  └──────────────────────────────┘
```

### Recommended Firmware Structure

```
firestarter/
├── include/
│   ├── eprom_budget.h            # NEW: pure, dependency-free budget API (no Arduino.h)
│   ├── eprom_params.h            # UNCHANGED (read-only this phase)
│   └── eprom.h                   # UNCHANGED unless the emission needs a constant
├── src/
│   ├── proms/
│   │   ├── eprom_budget.cpp      # NEW: the corrected BF-3 arithmetic. Inside +<proms/> so it is
│   │   │                         #      natively compiled AND natively testable; NOT pinned by
│   │   │                         #      protocol_branch_inventory.json
│   │   ├── eprom.cpp             # D-23: ONE plan, ONE commit — the time-gated emission only
│   │   └── eprom_params.cpp      # UNCHANGED (data read-only)
│   └── firestarter.cpp           # CAP-02 port + CAP-03 append, calling eprom_budget
└── test/native/avr/
    └── test_loop_eprom_v131/     # cadence + budget cases (env native_loop_v131)
```

### Recommended Host Structure

No new modules. All edits land in four existing files:

```
firestarter_app/firestarter/
├── serial_comm.py         # _decode_id_frame CAP-03 arm + a new annotated attribute (+ class default)
├── eprom_operations.py    # write-path timeout kwarg, DATA branch, budget-hint helper, pulse_us param
├── cli_handlers.py        # --pulse-us option + D-17 report line
└── constants.py           # OPTIONAL: JSON_KEY_PULSE_DELAY, following the :143-149 convention
firestarter_app/tests/
└── conftest.py            # make_comm must gain the new attribute (mypy/fail-closed obligation)
```

---

### Pattern 1: Thread the write-path timeout as a handler kwarg, not as global state

**What:** `_run_state_machine` forwards `**handler_kwargs` verbatim to `main_phase_handler`
(`eprom_operations.py:442`). Add `response_timeout: Optional[float] = None` to
`_main_phase_send_data` and pass it **only** from `write_eprom`.

**When to use:** for every write-path `get_response()`. Do **not** change
`DEFAULT_RESPONSE_TIMEOUT`, and do **not** thread it into `_execute_phase`.

**Why this shape:**
- `_main_phase_send_data` is shared by `write_eprom` (`:1606`) **and** `verify_eprom` (`:1698`)
  `[VERIFIED: eprom_operations.py]`. A default of `None` → 10 s keeps verify byte-identical, which is
  exactly D-12.
- `verify_eprom` already does not pass `eprom_data_dict`, so the write-only hint context is already
  precedented on the same function.
- `get_response(timeout)` is an already-supported call form — `expect_ack` uses it at
  `serial_comm.py:540`. No new API.
- The INIT phase of a write (erase + chunked blank check) emits one `0xE0` per 2048-byte chunk
  (`memory.cpp:489-558`, `BLANK_CHECK_CHUNK_SIZE 2048`) and each yielded frame resets
  `_read_and_parse_lines`' `start_time`, so its 10 s window is fed by construction. The END phase for
  `CMD_WRITE` has `firestarter_operation_end == NULL` (`configure_eprom` only sets it for
  `CMD_ERASE`), so it is a bare ack round-trip.

```python
def _main_phase_send_data(
    self,
    progress: ClassProgressHandler,
    input_file_path: str,
    buffer_size: int,
    eprom_data_dict: Optional[dict] = None,
    response_timeout: Optional[float] = None,   # HOST-01 / D-12: write-only
) -> None:
    ...
    timeout = (
        response_timeout
        if response_timeout is not None
        else DEFAULT_RESPONSE_TIMEOUT
    )
    while True:
        response = self.comm.get_response(timeout)
```

**Where the budget is read:** inside `write_eprom`'s `_operation_context` `with` block. The existing
D-15 comment at `eprom_operations.py:1620-1631` is explicit that `self.comm` is `None` after the
block exits, so any read of a decoded ack field must happen inside it.

---

### Pattern 2: CAP-03 as a third length-discriminated field, read at the computed `ver_end`

**What:** extend the `_decode_id_frame` override with a fourth `if`, keyed on length, reading at
`ver_end` — never a fixed index.

**When to use:** this is the only sanctioned way to read a new ack field. `_read_and_parse_lines`
stays untouched (D-13); the override's own docstring already records this
(`serial_comm.py:340-341`).

```python
# Inside _decode_id_frame, after the CAP-02 arm.
#
# CAP-03: the per-block write-time budget, appended AFTER CAP-02's
# variable-length identity tail. The offset is COMPUTED (ver_end), never
# fixed: a fixed index works on every board whose identity string happens
# to be one length and silently misreads on the next.
#
# Degradation matches CAP-01/CAP-02 exactly: a shorter param region leaves
# this None, and None means "use the D-10 fallback", never an error
# (_calculate_buffer_size:300-313 is the precedent -- Phase 54's
# FirmwareOutdatedError was REVERSED to a safe default).
if len(params_bytes) >= 4:
    self.hw_revision = params_bytes[2]
    ver_end = 4 + params_bytes[3]
    if ver_end <= len(params_bytes):
        self.firmware_identity = params_bytes[4:ver_end].decode("ascii", errors="replace")
        if len(params_bytes) >= ver_end + 2:
            value = struct.unpack(">H", params_bytes[ver_end : ver_end + 2])[0]
            # Plausibility clamp, mirroring CAP-01's [1, 4096] in spirit
            # (serial_comm.py:358-363): a hostile or corrupt ack must not be
            # able to install an unbounded timeout. Ceiling DERIVED, not
            # picked -- see RESEARCH "Budget Encoding".
            if 1 <= value <= WRITE_BUDGET_MAX_S:
                self.write_block_budget_s = value
```

**Two obligations that travel with it:**
1. Declare `write_block_budget_s: Optional[int] = None` at **class** level as well as in `__init__`,
   for the reason the CAP-02 comment at `:104-113` records.
2. Add it to `tests/conftest.py`'s `make_comm` factory alongside `firmware_identity` / `hw_revision`.

---

### Pattern 3: Time-gated emission inside the per-byte loop, compiled out on Uno-class targets

**What:** one `uint32_t` of per-block state plus a `millis()` compare, inside the outer per-byte
loop, wrapped in `#ifndef SERIAL_ON_IO` per BF-2.

**Placement:** immediately after the two LOOP-06 `continue` skips and before the inner pulse loop, or
at the top of the outer loop body. Placing it at the top of the loop body means the cadence is
independent of how many bytes get skipped, which is the more honest reading of "progress".

**Payload:** `(addr, handle->mem_size)` — matching `mem_util_blank_check`'s existing
`LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, handle->address, handle->mem_size)` at `memory.cpp:558`, so
`0xE0` keeps exactly one payload contract (D-04's rejected alternative was a second meaning).

**Interval:** the CONTEXT leaves the constant to discretion. Recommended **1000 ms**:
- It is 10× inside the previous 10 s window, so even against a host that somehow kept the 10 s
  timeout, the window is fed with 10× margin.
- At the modal `0x07` width (100 µs) a full 1024-byte block takes 2.6 s worst-case, so a 1 s interval
  yields ~2 frames per block — visible movement, negligible wire cost.
- At `--pulse-us 65535` a block takes 1678 s → ~1678 frames per block, 10 bytes of payload each ≈
  17 kB of frame traffic over 28 minutes. Irrelevant at 250 000 baud.
- A larger interval (5 s) halves nothing that matters and makes the bar feel dead on ordinary writes.

**Does this add a golden "site"?** No — `_is_relevant` in
`firestarter/tests/test_protocol_branch_inventory.py:268-274` keeps a predicate only if it contains
`handle->` or one of three named helpers. `if ((uint32_t)(millis() - last_emit_ms) >= INTERVAL)`
contains neither, so it is **not** recorded as a site. **But** every site *below* the insertion point
shifts line number (the final-verify loop's `i < handle->data_size` is one), so the golden must still
be re-derived — which is D-23. The pinned `protocol_lines == [70]` literal is unaffected because the
insertion is far below line 70.

---

### Pattern 4: The write-path DATA branch — and the bar-fight it must resolve

**What:** add a DATA arm to `_main_phase_send_data`'s loop, *before* the `response.type != "OK"`
raise, with `ack_data=False`, absolute positioning, and a resolution for the double-counting problem
described in Pitfall 1.

```python
while True:
    response = self.comm.get_response(timeout)
    if response.type == "MAIN":
        break
    if response.type == "ERROR":
        ...  # D-19 hint, then _raise_for_error_response
    if response.type == "DATA":
        # D-05: NEVER ack. The firmware is mid-block reading nothing; on the
        # Leonardo a stray "OK" is buffered, op_get_message returns
        # OP_MSG_ACK, and _process_incoming_data's `default: return false`
        # aborts the write with NO error frame at all
        # (src/eprom_operations.cpp:113-118). This is the
        # #write-empty-input-regression trap in a new place.
        #
        # D-04: apply `current`, IGNORE `total`. 0xE0 carries an ABSOLUTE
        # chip address; the bar's origin is the write's start address.
        self._apply_write_progress(response, progress, start_addr)
        continue
    if response.type != "OK":
        raise EpromOperationError(...)
```

**The offset source:** `command_dict["address"]` is set by `_setup_operation` only when an
`--address` was supplied (`eprom_operations.py:340-343`), so
`start_addr = (eprom_data_dict or {}).get("address", 0)` is correct and already available —
`write_eprom` already forwards `eprom_data_dict=cmd_data`.

---

### Pattern 5: The budget-failure hint, on the `_boot_block_hint_message` seam

**What:** a second id-keyed hint function beside `_boot_block_hint_message`
(`eprom_operations.py:106-170`), wired into the same ERROR branch that already appends
`" -- " + hint` at `:568-572`.

**Keyed on:** `MSG_ERR_MAX_PULSES` (0xBD), `MSG_ERR_ENERGY_CAP` (0xBE), `MSG_ERR_PULSE_TOO_WIDE`
(0xAE). **Never** on `MSG_ERR_WRITE_FAILED` (0xB1) — D-20 / F-141-06: zero references under `src/`.

**What the hint must say (D-21):** the firmware's own catalog format already names the address
(`"Byte at 0x%06x failed to program within %d pulses"`, `messages.py:747-762`), so the hint adds
*disposition*, not location:
- what was and was not programmed — everything before this block landed; this block is partial; no
  later block was attempted;
- that the firmware **stops accepting blocks for this write** (`handle->address` does not advance,
  `command_done()` fires — `141-LOOP-RECORD.md` §4);
- **no** retry advice and **no** resumption implication;
- for `0xAE` only: point at `--pulse-us` and name the refused value the firmware already reported.

**Why a helper, not inline:** `_boot_block_hint_message` is already a pure, unit-testable function
taking `(response, protocol, mem_size)`. Mirroring it keeps the new logic testable without a serial
port and keeps the ERROR branch a two-line composition.

---

### Pattern 6: `--pulse-us` transport — the `read_strobe_us` shape, verbatim

`[VERIFIED: eprom_operations.py:762-773]` — the shipped precedent:

```python
if read_settling_us or read_strobe_us:
    eprom_data_dict = dict(eprom_data_dict)   # shallow copy — never mutate caller's dict
    if read_settling_us:
        eprom_data_dict[JSON_KEY_READ_SETTLING_DELAY] = read_settling_us
```

Two verified differences for `pulse-delay`:
1. `"pulse-delay"` is emitted **unconditionally** by `convert_to_programmer`
   (`database.py:549-556`), unlike the read-timing keys which are emit-only-when-non-zero. So the
   override **replaces** an always-present key rather than adding one.
2. There is no `JSON_KEY_PULSE_DELAY` constant today; the key is a literal in `database.py`.
   `constants.py:142-148` establishes the `JSON_KEY_*` convention. Adding one is optional and
   cosmetic; if added, use it at both sites so a single definition exists.

The dict then flows onto the wire via `_setup_operation`'s `command_dict = eprom_data_dict.copy()`
(`:335`), and the firmware parses it in `get_delay` → `extract_long("pulse-delay",
handle->pulse_delay)` (`json_parser.c:503`). **No new wire field, no new command** — HOST-04
satisfied structurally.

---

### Pattern 7: HOST-05 — `click.IntRange(1, 65535)` with `default=None`

**`default=0` is a hard bug.** `[VERIFIED: empirical, click 8.4.2 in .venv/ci-replica]`

| Option shape | Invocation | Result |
|--------------|-----------|--------|
| `IntRange(1,65535)`, `default=0` | *no flag* | **exit 2** — `Error: Invalid value for '--pulse-us': 0 is not in the range 1<=x<=65535.` **Every `write` breaks.** |
| `IntRange(1,65535)`, `default=None` | *no flag* | exit 0, `pulse_us=None` |
| `IntRange(1,65535)`, `default=None` | `--pulse-us 100` | exit 0, `pulse_us=100` |
| `IntRange(1,65535)`, `default=None` | `--pulse-us 0` | exit 2 — `0 is not in the range 1<=x<=65535.` |
| `IntRange(1,65535)`, `default=None` | `--pulse-us 65536` | exit 2 — `65536 is not in the range 1<=x<=65535.` |
| `IntRange(1,65535)`, `default=None` | `--pulse-us abc` | exit 2 — `'abc' is not a valid integer range.` |

Mechanism: Click type-casts the default through `type_cast_value`, but short-circuits on `None`. The
existing `--read-settling` / `--read-strobe` options use `type=int, default=0` with **no** range
(`cli_handlers.py:1467-1480`) — so `default=0` is the shape a developer copying the nearest precedent
would reach for, and it is the shape that breaks. **Name this in the plan.**

Exit code note: Click's refusal is `UsageError` → **exit 2**, not the app's usual `sys.exit(1)`. Tests
must assert 2. `@map_typed_errors` never sees it — the raise happens during parameter processing,
before the callback.

---

### Anti-Patterns to Avoid

- **Emitting `0xE0` unconditionally from inside the per-byte loop.** Breaks HOST-03 on `uno` and
  `uno328pb` (BF-2). Guard with `#ifndef SERIAL_ON_IO`.
- **Writing the CAP-03 field at a fixed index, or at offset 2.** Offset 2/3 are CAP-02's;
  `ver_end` is variable (D-08's own named hazard, and BF-1 makes the collision concrete).
- **Restating D-11's formula literally.** It under-estimates 2× at `--pulse-us 49999` on `0x0B`
  (BF-3) and 8.3× for a future non-zero `overprogram_factor` row.
- **Lowering `DEFAULT_RESPONSE_TIMEOUT`'s value or scope.** D-12 forbids it; a genuinely dead board
  must still report in 10 s on read/verify/blank/erase/id.
- **Touching `_read_and_parse_lines`, including its `start_time` resets at `:448`/`:513`.** D-13,
  GATE-1.8d.
- **Acking a mid-block DATA frame.** Aborts the write on Leonardo with no error frame at all.
- **Keying any hint or test on `MSG_ERR_WRITE_FAILED` (0xB1).** Dead id on this family (D-20).
- **A HOST-01 test that waits out a real timeout.** `_FakeSerial.read()` returns `b''` immediately
  and `_read_and_parse_lines` sleeps 1 ms per empty read — a 120 s budget means a 120-second test.
  See Pitfall 6.
- **Dereferencing a PROGMEM row field directly** in the budget function. `pgm_read_byte` /
  `pgm_read_dword` only.
- **Including `Arduino.h` (or anything that pulls it) in a new `src/proms/` TU.** Pairing the Arduino
  framework header with the `avr/pgmspace.h` shim emits 14 macro-redefinition warnings, and the
  native watermark is at 1166 with zero headroom. `eprom_params.cpp` and `not_implemented.cpp` are
  the two TUs that deliberately omit it — follow them.

---

## Budget Arithmetic and Encoding

### The corrected formula

```
n(P)          = (C == 0 || P == 0) ? M : min(M, ceil(C / P))          # pulses per byte
per_byte_us   = n(P) * P + eprom_overprogram_us(n(P), P, factor, cap) # reuse the shipped fn
raw_block_us  = per_byte_us * DATA_BUFFER_SIZE
```

where `M = max_pulses`, `C = energy_cap_us` (0 = **UNCAPPED**), `P = handle->pulse_delay`, all read
via `pgm_read_*` from `eprom_params_for(handle->protocol)`.

### The padding (D-09 — the firmware owns it, and the record must state the rule)

`raw_block_us` counts **only** pulse widths. The block also pays, per `[VERIFIED: codebase]`:

| Cost | Value | Location |
|------|-------|----------|
| Once-per-block VPE settle | `delay(500)` = 500 ms | `eprom.cpp:286-289` (and the wrapper comment quantifies it: 128 blocks × 500 ms ≈ 64 s on a 64 K Uno write) |
| Fixed pre-pulse settle, per pulse | `delayMicroseconds(3)` | `memory.cpp:407` in `memory_set_data` |
| Read strobe + settling, per verify | 3 µs default strobe; settling 0 by default | `memory.cpp:355-377` |
| Register writes per address change | 3 × `rurp_write_to_register`, minus elision (F-141-09) | `memory.cpp:327-342` |
| Final full-block verify pass | `DATA_BUFFER_SIZE` extra reads, `0x07`/`0x08` only | `eprom.cpp:378-400` |
| Serial | 1024 B chunk ≈ 41 ms at 250 000 baud | — |

`[ASSUMED]` The per-pulse fixed overhead is on the order of **20–60 µs** (3 µs + 3 µs of documented
delays plus shift-register register writes). This matters: at `0x0B` with `--pulse-us 200` the loop
runs 250 pulses × 1024 bytes = 256 000 iterations, so a 60 µs overhead adds ~15 s on top of a 51.2 s
pulse budget — **~30 %**. An additive constant slack therefore does **not** scale; a multiplier does.

**Recommended padding rule, stated as prose for the record:**

```
budget_s = max(1, ceil(raw_block_us / 1000000) * 2 + 2)
```

"Twice the pulse-only worst case, plus two seconds." Verified coverage:

| Case (1024 B block) | raw | ×2+2 | Covers raw + overhead? |
|---------------------|-----|------|------------------------|
| 0x07 @ 100 µs | 2.6 s | 8 s | yes (2.6 + ~1.5) |
| 0x07 @ 1000 µs | 25.6 s | 54 s | yes (25.6 + ~1.5) |
| 0x07 @ 65535 µs | 1677.7 s | 3358 s | yes |
| 0x0B @ 200 µs | 51.2 s | 105 s | yes (51.2 + ~15.4) |
| 0x0B @ 49999 µs | 102.4 s | 207 s | yes |

Every value fits `uint16_t` seconds with room to spare (max 3358 s vs 65535).

### Encoding — `uint16_t` seconds CONFIRMED

The CONTEXT allows research to override on wire-economy or decode-symmetry grounds. It should not be
overridden:

| Criterion | `uint16_t` seconds | `uint32_t` ms |
|-----------|--------------------|---------------|
| Range needed | 3358 s worst case; 65535 s ceiling gives 19× margin | fine |
| Wire cost | 2 B | 4 B |
| Decode symmetry | `struct.unpack(">H", …)` — **identical** to CAP-01's existing line | `>I`, a second pattern |
| Granularity | 1 s — irrelevant for a timeout whose floor is 10 s today | sub-ms precision no caller can use |
| Firmware pack | two `>>`/`&` lines, same as CAP-01's | four |
| Flash | smaller | larger |

**Recommended host clamp ceiling, DERIVED not picked:** the largest legitimate advertisement is
`ceil(25 × 65535 µs × BUFFER / 1e6) × 2 + 2` evaluated at CAP-01's own plausibility ceiling
(`BUFFER = 4096`): `6711 × 2 + 2 = 13424 s`. Round to **`WRITE_BUDGET_MAX_S = 14400`** (4 h). Values
outside `[1, 14400]` leave the attribute `None`, so the D-10 fallback applies — matching CAP-01's
`T-55-06` behaviour exactly.

### D-10's 120 s fallback — CONFIRMED, with a sharper derivation

Live pulse-width distribution `[CITED: .planning/phases/138-preconditions-baseline/138-02-PULSE-DISTRIBUTION.md]`:

| Protocol | n | Histogram | Max shipped |
|----------|---|-----------|-------------|
| 0x07 | 170 | 100 µs ×113, 200 ×27, 1000 ×22, 50 ×4, 500 ×4 | 1000 µs |
| 0x08 | 127 | 100 µs ×104, 50 ×11, 10 ×7, 200 ×2, 1000 ×2, 20 ×1 | 1000 µs |
| 0x0B | 32 | 500 µs ×21, 1000 ×6, 200 ×5 | 1000 µs |

- Worst **shipped-database** block: `0x0B` @ 1000 µs = **51.2 s** (1024 B). `0x07`/`0x08` @ 1000 µs =
  25.6 s. 120 s is **2.3×** the worst shipped case. ✓
- **Sharper than D-10 states:** 120 s covers **every reachable `0x0B` width**, including the
  pathological 49999 µs case, because `0x0B`'s per-byte bound can never exceed 99 998 µs and
  `99998 × 1024 = 102.4 s < 120 s`. ✓
- The residual gap is `0x07`/`0x08` only, and the threshold is exact: `120 s / (25 × 1024) =`
  **4687 µs** on a Leonardo, `120 s / (25 × 512) =` **9375 µs** on an Uno. D-10's "roughly 4700 µs"
  is correct for the Leonardo case; the Uno case is 2× more forgiving and should be named too.
- **The realistic "absent advertisement" case is NOT what D-10 says.** D-10 names "a mid-milestone
  v1.31 build" as the realistic case. BF-1 shows such a build **cannot connect at all**, so it never
  reaches the fallback. The reachable absent-advertisement cases are: (a) a released `beta` firmware
  (has CAP-02, lacks CAP-03) — the genuinely realistic one, and (b) a v1.31 build after CAP-02 is
  ported but before CAP-03 lands. Correct the non-claim accordingly.

**Verdict: keep 120 s.** No revision needed to the number; the derivation is sharper and one
non-claim changes.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Bounds-checking `--pulse-us` before I/O | An `if not 1 <= n <= 65535: click.echo(...); sys.exit(1)` in the handler | `type=click.IntRange(1, 65535)` | Refusal happens during parameter processing, structurally before the handler body — the guarantee is Click's parse order, not a code position a later edit can move (D-15) |
| A new error id for a program failure | Claiming `0xBF` | `MSG_ERR_MAX_PULSES` (0xBD) / `MSG_ERR_ENERGY_CAP` (0xBE) / `MSG_ERR_PULSE_TOO_WIDE` (0xAE) — all three already exist with address-interpolating formats | D-02/H4 keep `0xBF` free; the band `0xA0..0xBF` has exactly one slot left |
| A progress message for the write path | A new DATA id | `MSG_DATA_PROGRESS` (0xE0), already emitted by `mem_util_blank_check` and already rendered by `_handle_progress_response` → `set_progress` | D-02: adds a second emitter, not a mechanism; keeps one payload contract for the id |
| A new command or wire field for the pulse override | `CMD_SET_PULSE` or `"pulse-us"` | The existing `"pulse-delay"` key, already emitted by `convert_to_programmer` and already parsed by `get_delay` | HOST-04 forbids both; milestone D-04 satisfied structurally |
| A capability/version handshake for the budget | A new command exchange | `MSG_OK_READY`'s `param_bytes=-1` variable blob, third length-discriminated extension | Zero catalog edit, zero codegen, zero constants-parity churn (D-08) — but see BF-1 |
| An error-framing layer for budget failures | A new exception type or a re-plumbed ERROR path | `_raise_for_error_response` + a `_boot_block_hint_message`-shaped helper on the existing ERROR branch | D-19: the machinery works; only the hint is missing |
| A per-run µs override plumbing pattern | Adding a parameter to `_setup_operation` or a new wire builder | A shallow dict copy set before `_setup_operation`, exactly as `consistency_check_eprom` does for `read_settling_us`/`read_strobe_us` | D-14; it is a shipped, in-tree, working example on the same code path |
| Restating the overprogram worst case | `3 * factor * pulse` | Call `eprom_overprogram_us(max_pulses, pulse, factor, cap)` | BF-3: the budget cannot drift from runtime behaviour if it calls the same function |
| An advancing-clock mock for the cadence test | A hand-rolled `millis()` counter | `test_cobs_data_frame.cpp:140-167` / `test_frame_vectors.cpp:150-171` already do this: `When(Method(ArduinoFake(Function), millis)).AlwaysDo([]() { millis_counter += 100; return millis_counter; })` | Two shipped precedents; `test_loop_eprom_v131.cpp:133` currently pins `millis()` to `AlwaysReturn(0)` and must be changed |
| A log-frame capture harness for the native cadence test | A new capture buffer | `host_stubs_common.inc:268`'s `rurp_log_id` override with `clear_logged_ids()` / `logged_id_count()` / `logged_id_at(i)` / `logged_id_param(i,j)` / `logged_ids_overflowed()` | Already wired into `test_loop_eprom_v131`'s `setUp` |
| A full-write host integration harness | A new fake transport | `tests/conftest.py`'s `_FakeSerial` + `build_frame()` + `make_comm` + a patched `find_and_connect`, as used at `tests/test_eprom_operations.py:1213-1255` | A complete, hardware-free INIT→MAIN→END write already runs there |
| A CAP-03 ack fixture | A new frame builder | `tests/test_hw_revision_gate.py`'s `_ready_body()` + `_cap02_params()` helpers | Extend `_cap02_params` with an optional budget tail — three lines |

**Key insight:** this phase has an unusually high reuse ratio. Almost nothing here is new machinery;
it is new *wiring* between pieces that already exist and already have tests. The failure modes are
therefore integration failures — the wrong offset, the wrong default, the wrong board, the wrong
formula — not missing capability. Plan verification legs accordingly: prefer call-argument and
byte-layout oracles over end-to-end behaviour where the behaviour is already covered.

---

## Common Pitfalls

### Pitfall 1: Two progress sources fight over the same bar

**What goes wrong:** `_main_phase_send_data` already calls `progress.update(len(data_chunk))` when a
chunk is **handed off** (`eprom_operations.py:591`). Adding an absolute `set_progress` from `0xE0`
means: bar jumps to 1024 the instant chunk 1 is sent, then the firmware's frames set it back to
0…1024 as bytes are actually programmed, then it jumps to 2048, then crawls again. `tqdm` permits
`pbar.n` to move backward (`set_progress` does `self.pbar.n = current; self.pbar.refresh()`,
`:275-277`), so the bar visibly rewinds.

**Why it happens:** the two sources measure different things — bytes *sent* vs bytes *programmed* —
and the existing one runs first.

**How to avoid:** latch. On the write path, once the first `0xE0` frame is observed, stop calling
`update()` on handoff and let the firmware drive the bar absolutely; until then, keep today's
handoff-based bar. This is the only shape that is correct on both boards: Leonardo gets a
bytes-programmed bar, Uno-class keeps today's bytes-sent bar (BF-2 means Uno never delivers a frame
mid-block). Do **not** simply delete the `update()` call — that regresses Uno-class boards to a bar
that never moves.

**Warning signs:** a bar that rewinds once per block; a bar that reaches 100 % before the write
finishes; a bar stuck at 0 on an Uno.

---

### Pitfall 2: `set_progress`'s rebuild-on-differing-total tears the bar down every frame

**What goes wrong:** `set_progress(current, total)` calls `self.start(total)` whenever
`self.total_steps != total` (`:268-270`), and `start()` **closes and re-creates** the `tqdm` bar and
zeroes `current_step` (`:247-256`). The write bar is started with `file_size` (`:561`), while `0xE0`
carries `handle->mem_size`. For a full-chip write they match; for a short input file or an
`--address`-offset write they do **not**, so every single frame destroys and rebuilds the bar.

**Why it happens:** `0xE0`'s `total` is chip geometry; the write bar's total is file length.

**How to avoid:** D-04 — the write branch applies `current` only and never passes `total` into
`set_progress`. Call `progress.update(...)` with a delta, or set `progress.current_step` and
`pbar.n` directly, but never reach `set_progress`'s rebuild arm. Fixing `set_progress` itself is a
**deferred idea**, out of scope (shared code on read and blank-check paths).

**Warning signs:** flickering bar; multiple bar lines in the terminal; `logging_redirect_tqdm()`
re-entered per frame.

---

### Pitfall 3: `--pulse-us` with `default=0` breaks every `write` invocation

**What goes wrong:** `click.IntRange(1, 65535)` type-casts the default. `0` is out of range → Click
raises `UsageError` before the handler runs → **`firestarter write` exits 2 with no flag supplied
at all.**

**Why it happens:** the nearest in-tree precedent (`--read-settling`, `--read-strobe`) uses
`type=int, default=0`, and `0` is also the wire sentinel for "use the DB value". Copying that shape
and adding a range is the natural move and it is fatal.

**How to avoid:** `default=None`. Click short-circuits `type_cast_value` on `None`. Then `None` means
"not supplied" and an explicit `--pulse-us 0` is correctly refused (HOST-05 requires refusing 0).

**Warning signs:** the CI smoke step (`firestarter --help`) still passes — it never invokes `write`.
Only a `CliRunner` invocation of `write` with no `--pulse-us` catches it. **Author that test.**

---

### Pitfall 4: The 4-slot deferred-log buffer converts a program failure into a transport timeout

Covered in full as **BF-2**. Summary: on `uno`/`uno328pb`, progress frames emitted inside the
programmer-mode window fill `deferred_log[4]`; the subsequent `MSG_ERR_MAX_PULSES` frame is silently
dropped; the firmware goes idle having emitted nothing; the host times out. **This is a regression
of HOST-03, caused by HOST-02's implementation.** Mitigate with `#ifndef SERIAL_ON_IO`.

---

### Pitfall 5: The native oracle cannot see the `com_mode` gate, and `millis()` is pinned at 0

**What goes wrong:** two independent blindnesses in the same suite.

1. `build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c>
   +<operation_utils.cpp>` — `src/boards/uno_rurp_shield.cpp` is in **no** native env, and
   `host_stubs_common.inc:268`'s `rurp_log_id` has **no** `com_mode` gate. A native test therefore
   records every emitted frame and proves nothing about Uno-class delivery.
2. `test_loop_eprom_v131.cpp:133` sets `When(Method(ArduinoFake(), millis)).AlwaysReturn(0)` with the
   comment *"Unused by any case in this plan"*. A time-gated emission with `millis()` frozen at 0
   **never fires** — a cadence test would pass vacuously with zero frames.

**How to avoid:**
- For the `#ifndef SERIAL_ON_IO` guard, author a **source-contract** gate (Phase 142's
  `command_done()` precedent) and label it as such in the plan and the record.
- For the cadence, replace the `millis()` mock with an advancing counter, copying
  `test_cobs_data_frame.cpp:140-167`. State in the test file *why* the mock changed.
- Make the cadence assertion non-vacuous in both directions: with the clock frozen, **zero** frames;
  with the clock advancing past the interval, **N ≥ 2** frames with monotonically increasing first
  params. `logged_ids_overflowed()` gives a third, free assertion.

**Corollary for D-24:** `native_trace_v131`'s `setUp` also pins `millis()` to `AlwaysReturn(0)`
(`test_trace_eprom_v131.cpp:92`), so **D-02's emission will produce no new frames in the trace env**.
`native_trace_v131` stays RED for the reasons Phases 141/142 already recorded, but this phase should
**not** claim it made the trace diverge further. Phase 144/TEST-06's "every changed strobe
attributable to a named decision" analysis will find zero D-02-attributable strobes — state that
plainly rather than implying otherwise.

---

### Pitfall 6: A HOST-01 test that waits out a real timeout takes as long as the timeout

**What goes wrong:** `_FakeSerial.read()` returns `b''` immediately when the buffer is empty, and
`_read_and_parse_lines` responds with `time.sleep(0.001); continue` (`serial_comm.py:426-430`)
without resetting `start_time`. A test that feeds nothing and asserts "no `SerialTimeoutError`" runs
for the full budget — **120 s, or 3358 s against an advertised budget.**

**How to avoid** — three oracles, in order of preference:

1. **Call-argument oracle (primary).** Patch or wrap `SerialCommunicator.get_response` and assert the
   `timeout` positional it receives equals the advertised budget (or 120.0 when absent, or 10 when
   the caller is `verify_eprom`). This tests exactly what HOST-01 requires — that the write call
   sites use the budget — deterministically and in milliseconds.
2. **Fake-clock oracle (behavioural).** Monkeypatch `time.time` inside `serial_comm` to a
   controllable counter and drive a `_FakeSerial` that yields `b''` for a scripted number of reads,
   then a frame. Prove the generator survives a simulated >10 s gap and raises at >budget. Never
   patch `time.sleep` away without also bounding the loop, or the test spins.
3. **Small-budget oracle (integration smoke).** Feed an ack advertising a 2 s budget and prove the
   plumbed value is 2.0 — cheap, but does not exercise the >10 s claim.

Also assert the **negative**: `verify_eprom`, `read_eprom`, `check_eprom_blank`, `erase_eprom` and
the chip-id path still see 10. That is D-12's proof and it is a pure call-argument assertion.

---

### Pitfall 7: `test_flash_path_record_sync.py` asserts whole-repo `git status --porcelain`

**What goes wrong:** the firmware suite goes RED for an unrelated reason if any file in the repo is
dirty (F-141-11, orphaned and unassigned).

**How to avoid:** commit in-flight changes before running the full firmware suite. Every firmware
plan's verification block must sequence commit-then-test, not test-then-commit.

---

### Pitfall 8: AVR builds must produce **zero** warnings — a stricter rule than the native watermark

**What goes wrong:** the CONTEXT names only the native 1166 watermark. But
`scripts/baseline/size_baseline.json`'s `policy` is `{"avr_rule": "== 0", "native_rule": "<=
total_watermark"}`, with all three AVR targets recorded at `total: 0`. **Any** new warning on `uno`,
`uno328pb` or `leonardo` turns `check_build_warnings.py` RED.

**How to avoid:** a new `src/proms/` TU must compile clean on all three AVR targets *and* add nothing
to the native count. Concretely: no `Arduino.h`, no unused parameters, no sign-compare, no implicit
narrowing. `eprom_params.cpp`'s include discipline (`#include "eprom_params.h"` only) is the model.

---

### Pitfall 9: Measure firmware size and warnings COLD

`size_baseline.json`'s `meta.warm_vs_cold_correction` records that the native watermark is 1166 COLD
and 998 WARM, and that a prior baseline's figure was silently a warm measurement. The recorded
watermark is the COLD figure. Measure with `pio run -t clean -e <env>` then `pio run -e <env>` in one
uninterrupted invocation, and beware the default 2-minute Bash timeout truncating a cold toolchain
build (a documented trap from 124-04).

---

### Pitfall 10: Never pass a `native_*_v131` env name to `check_size_baseline.py`

F-138-05: `NATIVE_ENVS` is hardcoded to `("native", "native_nodevtools")` and an unknown env raises
an **uncaught `KeyError`** (exit 1 — a false regression signal, not the documented exit 2).
`check_build_warnings.py` handles it as exit 2 but has no baseline entry either way. The three
`native_*_v131` envs' counts are a **local, run-by-name** obligation recorded in the phase record
only, and **no CI leg of either repo runs them**.

---

## Code Examples

### Example 1: The budget function (new, unpinned TU — natively testable)

```c
/* src/proms/eprom_budget.cpp -- deliberately in src/proms/ so it lands inside
 * every native build_src_filter (+<proms/>) and gets a real unit-test oracle,
 * and deliberately NOT in eprom.cpp or eprom_params.cpp, both of which are
 * pinned by tests/golden/protocol_branch_inventory.json's blob_shas.
 *
 * No Arduino framework header (140-RESEARCH Pitfall 1): pairing it with the
 * avr/pgmspace.h shim emits 14 macro-redefinition warnings and the native
 * watermark has zero headroom. eprom_params.cpp is the include-discipline model. */
#include "eprom_budget.h"
#include "eprom_params.h"

/* Pulses a single byte can consume before the loop gives up. Mirrors
 * eprom.cpp:334-361 exactly: `accumulated += P` happens BEFORE the
 * `accumulated >= C` test, so the last pulse may overshoot C by up to P-1 --
 * which is why ceil() is load-bearing and why min(M*P, C) is WRONG.
 * C == 0 means UNCAPPED (eprom_params.h), guarded as eprom.cpp:105 guards it. */
uint32_t eprom_worst_pulses(uint8_t max_pulses, uint32_t pulse_us, uint32_t energy_cap_us) {
    if (energy_cap_us == 0U || pulse_us == 0U) {
        return (uint32_t)max_pulses;
    }
    uint32_t by_energy = (energy_cap_us + pulse_us - 1U) / pulse_us;   /* ceil */
    return by_energy < (uint32_t)max_pulses ? by_energy : (uint32_t)max_pulses;
}

/* Advertised per-block budget, in SECONDS, already padded (D-09: the firmware
 * owns the margin because it is the only side that knows delay(500), the final
 * verify pass, the per-pulse fixed settle and the serial time).
 *
 * Padding rule, stated here because a host-side reader cannot see it:
 *   TWICE the pulse-only worst case, PLUS two seconds, floor of one second.
 * The multiplier (not an additive constant) is required because the per-pulse
 * fixed overhead scales with pulse COUNT: 0x0B at 200 us runs 250 pulses x
 * 1024 bytes = 256000 iterations, so a ~60 us overhead adds ~15 s to a 51.2 s
 * pulse budget -- about 30 %.
 *
 * A budget that is too TIGHT causes a spurious timeout on a WORKING write --
 * a false failure on real silicon, strictly worse than a generous ceiling. */
uint16_t eprom_block_budget_s(uint32_t protocol, uint32_t pulse_us, uint32_t block_bytes) {
    const eprom_params_t* row = eprom_params_for(protocol);
    if (row == NULL) {
        return 0U;   /* not an EPROM protocol: advertise nothing, host uses its fallback */
    }
    uint8_t  max_pulses = pgm_read_byte(&row->max_pulses);
    uint8_t  factor     = pgm_read_byte(&row->overprogram_factor);
    uint32_t energy_cap = pgm_read_dword(&row->energy_cap_us);
    uint32_t op_cap     = pgm_read_dword(&row->overprogram_cap_us);

    uint32_t n = eprom_worst_pulses(max_pulses, pulse_us, energy_cap);
    /* Reuse the SHIPPED overprogram function rather than restating its
     * formula, so the budget cannot drift from runtime behaviour when a
     * future row sets overprogram_factor != 0. factor == 0 on all three
     * shipped rows, so this term is exactly 0 today -- written for the
     * future row, not omitted as if the column did not exist. */
    uint32_t per_byte_us = n * pulse_us
                         + eprom_overprogram_us((uint8_t)n, pulse_us, factor, op_cap);

    uint32_t raw_s = (per_byte_us / 1000000UL) * block_bytes
                   + ((per_byte_us % 1000000UL) * block_bytes) / 1000000UL;  /* avoid 32-bit overflow */
    uint32_t padded = raw_s * 2UL + 2UL;
    if (padded > 65535UL) {
        padded = 65535UL;
    }
    return (uint16_t)(padded < 1UL ? 1UL : padded);
}
```

> Note the two-term division: `per_byte_us * block_bytes` overflows `uint32_t` at
> `1638375 × 1024 ≈ 1.68e9`… which fits, but `per_byte_us * 4096` does not. Divide first.

---

### Example 2: CAP-02 port + CAP-03 append, one pack block

```c
/* src/firestarter.cpp, replacing LOG_OK_ID_U16(MSG_OK_READY, DATA_BUFFER_SIZE) at :157.
 *
 * CAP-02 is being PORTED here, not invented: it shipped on origin/beta as PR
 * #49 (13eb350 / b1737b2) and the v1.31 branch forked one commit earlier, at
 * 3085084. Without it the v1.31 host REFUSES every connection --
 * _probe_port raises FirmwareOutdatedError when firmware_identity is None, and
 * tests/test_fwguard.py::test_absent_identity_refuses asserts exactly that.
 *
 * Wire layout, three length-discriminated extensions of one variable blob:
 *   [buffer_size u16 BE][hw_revision u8][ver_len u8][ver bytes][write_budget_s u16 BE]
 *      CAP-01              CAP-02                                CAP-03
 * MSG_OK_READY is params=(("bytes","hex"),) with param_bytes=-1, so this needs
 * NO messages.toml edit and NO codegen run. */
{
    const char* _ver = FW_VERSION;
    uint8_t _vlen = (uint8_t)strlen(_ver);
    if (_vlen > 32) _vlen = 32;
    uint8_t _ready[4 + 32 + 2];
    _ready[0] = (uint8_t)(((uint16_t)DATA_BUFFER_SIZE >> 8) & 0xFF);
    _ready[1] = (uint8_t)((uint16_t)DATA_BUFFER_SIZE & 0xFF);
#ifdef HARDWARE_REVISION
    _ready[2] = (uint8_t)rurp_get_hardware_revision();
#else
    _ready[2] = 0xFE;   /* REVISION_UNKNOWN -- the symbol lives inside that same #ifdef */
#endif
    _ready[3] = _vlen;
    memcpy(_ready + 4, _ver, _vlen);
    /* CAP-03 (HOST-01): the per-block write-time budget. Emitted for every
     * command, not just CMD_WRITE -- the shape must not vary by command or a
     * length-discriminating host decoder loses its only discriminator.
     * eprom_block_budget_s returns 0 for a non-EPROM protocol; the host's
     * [1, MAX] plausibility clamp then leaves the attribute None and the
     * D-10 fallback applies, which is the correct behaviour for a family
     * whose block time this table cannot bound. */
    uint16_t _budget = eprom_block_budget_s(handle->protocol,
                                           handle->pulse_delay,
                                           (uint32_t)DATA_BUFFER_SIZE);
    _ready[4 + _vlen]     = (uint8_t)((_budget >> 8) & 0xFF);
    _ready[4 + _vlen + 1] = (uint8_t)(_budget & 0xFF);
    LOG_OK_ID_BYTES(MSG_OK_READY, _ready, (uint8_t)(4 + _vlen + 2));
}
```

**Ordering fact `[VERIFIED]`:** `init_programmer_framed` runs `parse_json(handle)` before this block
(`firestarter.cpp:126-128`), so `handle->protocol` and `handle->pulse_delay` are populated. But
`configure_memory`/`configure_eprom` — which applies the `pulse_delay == 0` fallback switch — also
runs before the ack. Confirm the exact ordering at plan time: if the fallback has **not** yet been
applied when the ack is packed, a chip whose DB pulse is 0 would advertise a budget computed from
`pulse_us = 0`, and `eprom_worst_pulses` returns `max_pulses` for `pulse_us == 0` — which yields a
budget of 2 s. **That is a spurious-timeout path.** Either pack the ack after the fallback, or apply
the same fallback inside the budget function. Flagged as Open Question 1.

---

### Example 3: The host's write-progress branch

```python
def _apply_write_progress(
    self,
    response,
    progress: ClassProgressHandler,
    start_addr: int,
) -> None:
    """Render an intra-block MSG_DATA_PROGRESS frame on the write path.

    D-04: applies the frame's `current` and IGNORES its `total`.
    set_progress() calls start(total) whenever the frame's total differs from
    the bar's (eprom_operations.py:268-270), and start() CLOSES and RE-CREATES
    the tqdm bar (:247-256). The write bar is started with file_size (:561)
    while 0xE0 carries handle->mem_size, so a short input file or an
    --address-offset write would tear the bar down and rebuild it on EVERY
    frame. This branch never reaches that arm.

    D-04 arithmetic: 0xE0 carries an ABSOLUTE chip address; the write bar's
    origin is the write's start address. Getting this wrong shows up as a bar
    that starts mid-way on an --address write.

    D-05: NEVER acks. Callers must not route this through
    _handle_progress_response, whose ack_data defaults to True.
    """
    if not response.message or "/" not in response.message:
        return
    try:
        absolute, _total_ignored = (int(x) for x in response.message.split("/"))
    except (ValueError, TypeError):
        return                      # not a parsable progress update
    position = max(0, absolute - start_addr)
    progress.current_step = position
    if progress.progress_callback:
        progress.progress_callback(position, progress.total_steps)
    if progress.pbar:
        progress.pbar.n = position
        progress.pbar.refresh()
```

---

### Example 4: The D-17 report line, on the v1.22 D-04 precedent

```python
# cli_handlers.py, inside write(), after resolve_chip.
#
# D-17: ALWAYS print a default-visible line when --pulse-us fires, naming both
# values. Precedent: the D-04 auto-set block below "always prints a mandatory,
# default-visible report line when it fires" (:667-677). The reason is
# provenance: a bench artifact or log captured without the command line beside
# it cannot otherwise tell you the pulse was not the database's -- and Phase
# 145's evidence will be read by strangers.
if pulse_us is not None:
    db_pulse = eprom_data.get("pulse-delay", 0)
    db_shown = f"{db_pulse} us" if db_pulse else "firmware default (database supplied none)"
    click.echo(
        f"{eprom.upper()}: --pulse-us {pulse_us} overrides the database "
        f"program pulse for this run ({db_shown} -> {pulse_us} us). "
        "This run's timing is NOT the database's."
    )
```

---

### Example 5: The budget-failure hint (D-19, D-21)

```python
_BUDGET_FAILURE_IDS = (MSG_ERR_MAX_PULSES, MSG_ERR_ENERGY_CAP, MSG_ERR_PULSE_TOO_WIDE)

def _budget_failure_hint_message(response) -> Optional[str]:
    """Return a program-failure disposition hint, or None.

    D-19: mirrors _boot_block_hint_message's shape (:106-170) and lands on the
    same ERROR branch (:568-572). The firmware's catalog format already names
    the ADDRESS ("Byte at 0x%06x failed to program within %d pulses"), so this
    adds disposition, not location.

    D-21 -- what it must and must not say. 141-LOOP-RECORD.md §4 traced the
    firmware's behaviour: handle->address does NOT advance,
    _process_incoming_data returns false immediately, command_done() fires and
    zeroes the control and address registers, and the firmware accepts NO
    further blocks for that write. "The write aborts" and "the firmware stops
    accepting blocks" are the same event. So: no retry advice, no resumption
    implication.

    D-20 / F-141-06: deliberately NOT keyed on MSG_ERR_WRITE_FAILED (0xB1) --
    a whole-tree grep finds zero references under src/, so on this family it is
    a dead id and a hint keyed on it would never fire.
    """
    if response.id not in _BUDGET_FAILURE_IDS:
        return None
    if response.id == MSG_ERR_PULSE_TOO_WIDE:
        return (
            "the firmware refused this pulse width before enabling any high "
            "voltage -- no byte was programmed by this command and the chip is "
            "unchanged by it. This protocol caps accumulated per-byte program "
            "energy; retry with a smaller --pulse-us (or omit it to use the "
            "database value)."
        )
    return (
        "the write ABORTED at this address. Bytes before this block were "
        "programmed; this block is partially programmed; no later block was "
        "attempted -- the firmware stops accepting blocks for this write and "
        "the address counter does not advance. Re-running the write repeats "
        "the whole file from the start. A byte that will not converge usually "
        "means insufficient program voltage or a worn/failing cell, not a "
        "timing problem."
    )
```

---

### Example 6: `--pulse-us` end to end

```python
# cli_handlers.py -- the option
@click.option(
    "--pulse-us",
    "pulse_us",
    type=click.IntRange(1, 65535),
    default=None,           # NOT 0 -- IntRange type-casts the default and 0 is
                            # out of range, which would make EVERY `write`
                            # invocation exit 2 (RESEARCH Pitfall 3, measured).
    help="Override the database program-pulse width for this run (µs, 1-65535). "
         "Bound is minipro parity (-o pulse=N is uint16), NOT a wire-type limit.",
)

# eprom_operations.py -- write_eprom
def write_eprom(self, eprom_name, eprom_data_dict, input_file_path,
                operation_flags=0, address_str=None, pulse_us: int = 0) -> bool:
    # D-14: ride the DB dict, exactly as consistency_check_eprom does for
    # read_settling_us / read_strobe_us (:762-773), whose own comment says the
    # pattern is "consistent with how pulse-delay already travels via the DB
    # dict". Shallow copy -- NEVER mutate the caller's dict. The key already
    # exists (database.py:554 emits "pulse-delay" unconditionally), so this
    # REPLACES a value rather than adding a field: no new wire field, no new
    # command (HOST-04 satisfied structurally).
    if pulse_us:
        eprom_data_dict = dict(eprom_data_dict)
        eprom_data_dict["pulse-delay"] = pulse_us
    with self._operation_context(...) as (cmd_data, buf_size, op_name):
        ...
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Buffer size parsed from the 3rd colon-field of the FW identity string | CAP-01: 2-byte big-endian u16 in `MSG_OK_READY`'s param blob, with a `[1, 4096]` plausibility clamp | Phase 55 | Established the "extend one variable blob, discriminate by length" pattern this phase's CAP-03 is the third instance of |
| `FirmwareOutdatedError` when the advertisement was absent | Safe default (512-byte Uno floor); Phase 54 D-05 **reversed** | Phase 54→55 | The precedent D-10 follows, and the argument against D-10's rejected "refuse the write" option |
| A dedicated `CMD_FW_VERSION` pre-probe (a full command exchange per connect) | CAP-02: `[hw_rev u8][ver_len u8][ver bytes]` appended to the same ack | firmware PR #49 (`origin/beta`), app PR #45 | One fewer round trip per connect — **and, per BF-1, present on the app branch but absent from the firmware branch** |
| Block-retry loop with escalating pulse width, failing as `MSG_ERR_WRITE_FAILED` (0xB1) with `(u24 addr, u8 retries, u16 bad bytes)` | Per-byte fixed-width pulse→verify, failing as `MSG_ERR_MAX_PULSES` (0xBD) / `MSG_ERR_ENERGY_CAP` (0xBE) with `(u24 addr, u8 pulse_count)` | Phase 141 | **0xB1 is emitted by nothing on the 27C path** (D-20). Any hint or test keyed on it is keyed on a dead id |
| Hand-rolled `protocol == 0x0B \|\| FLAG_VPE_AS_VPP` route forks, duplicated | One `eprom_hv_route_mask()` driven by the table's `vpp_path` column | Phase 142 | Tier-1 protocol-keyed sites in `eprom.cpp` fell 3 → **1** (line 70's pulse fallback). This phase must not add a second |
| `argparse` CLI | Click | v1.8 | `IntRange` is available as a first-party type; no new dependency for HOST-05 |

**Deprecated / outdated in the CONTEXT itself:**
- `141-CONTEXT.md`'s `99999 µs` energy-cap figure — superseded by **99 998 µs** (F-141-10);
  `firestarter/CLAUDE.md` §Algorithm Handlers is the corrected source.
- The roadmap's "Phase 143 independent of 140–142" line — corrected by D-01, amended in Phase 146.
- `eprom_params.h`'s `min(3 x overprogram_factor x pulse, cap)` comment — does not match the shipped
  `eprom_overprogram_us` (BF-3). Worth a Phase 146 wording fix; **do not** copy it into a formula.

---

## Decision Reconciliation

Every CONTEXT decision this research either confirms, sharpens, or contradicts. The planner should
treat "CONTRADICTED" rows as requiring an explicit plan-level disposition (and, for D-02 and D-08,
probably an operator note).

| Decision | Verdict | What research found |
|----------|---------|---------------------|
| D-01 dual-repo | **CONFIRMED and strengthened** | The firmware half is larger than the CONTEXT assumes: CAP-02's port (BF-1) is also required |
| D-02 emit `0xE0` from the loop | **CONTRADICTED in scope** | Structurally undeliverable on `uno`/`uno328pb`, and a naive form **breaks HOST-03** there (BF-2). Keep the decision; add `#ifndef SERIAL_ON_IO` and a second non-claim dimension |
| D-03 time-bounded cadence | CONFIRMED; **oracle correction** | `test_loop_eprom_v131.cpp:133` pins `millis()` to 0, so the cadence needs an advancing mock (two in-tree precedents). Recommended interval: **1000 ms** |
| D-04 apply `current`, ignore `total` | **CONFIRMED; hazard verified as real** | `set_progress:268-270` + `start:247-256` do rebuild the bar; write bar total is `file_size` (`:561`) vs `0xE0`'s `mem_size`. Offset source is `command_dict["address"]` |
| D-05 do not ack; add a DATA branch | **CONFIRMED; severity higher than stated** | An ack returns `OP_MSG_ACK` → `_process_incoming_data`'s `default: return false` → write aborts with **no error frame**. Leonardo-only (Uno drains its RX on mode restore) |
| D-06 EPROM-path only | CONFIRMED; **needs a second dimension** | Add "and delivered on `leonardo` only" (BF-2) |
| D-07 firmware computes the budget | CONFIRMED | And `src/proms/` is the right home so the arithmetic is natively testable |
| D-08 CAP-03 on `MSG_OK_READY` | **BLOCKED by BF-1** | `param_bytes=-1` and the two prior length-discriminated extensions are verified. But the firmware branch has no CAP-02 tail; port it first |
| D-09 firmware owns the padding | CONFIRMED; **rule made concrete** | An additive constant is insufficient (per-pulse overhead scales with pulse count). Recommended: ×2 + 2 s, floor 1 s, stated in prose in the record |
| D-10 120 s fallback | **CONFIRMED; derivation sharpened; one non-claim corrected** | 120 s covers **all** reachable `0x0B` widths and shipped `0x07`/`0x08`. Threshold is 4687 µs on Leonardo, 9375 µs on Uno. The "mid-milestone v1.31 build" case is unreachable (BF-1) — the realistic case is released `beta` firmware |
| D-11 per-byte formula | **CONTRADICTED** | Under-estimates 2× at `--pulse-us 49999` on `0x0B`, and the overprogram term is 8.3× low for a future `factor=3` row (BF-3). Corrected form supplied |
| D-12 10 s stays for non-write paths | CONFIRMED; **shape supplied** | A default-`None` kwarg on `_main_phase_send_data` keeps `verify_eprom` byte-identical |
| D-13 do not touch `_read_and_parse_lines` | CONFIRMED | `get_response(timeout)` is already a supported call form (`serial_comm.py:540`). Note the stated *reason* is Uno-false (BF-2) even though the decision is right |
| D-14 override rides the DB dict | **CONFIRMED verbatim** | Precedent read line-by-line; `"pulse-delay"` already emitted unconditionally and already parsed |
| D-15 `IntRange(1,65535)` | **CONFIRMED with a fatal caveat and one false rationale** | `default=0` breaks every `write` (measured). "Before `AppContext` builds" is **false** — Click's group callback runs first — but the guarantee holds: nothing in `cli()` or `AppContext` opens a port |
| D-16 leave the over-cap case to firmware | CONFIRMED | `eprom.cpp:105-110` refuses pre-flight and names itself this phase's backstop |
| D-17 mandatory report line | CONFIRMED | Precedent at `cli_handlers.py:667-677` |
| D-18 `write` only | CONFIRMED | No other command emits a program pulse |
| D-19 render-and-prove + hint | CONFIRMED | Formats interpolate the address; the ERROR branch and hint seam both exist |
| D-20 no `0xB1` | CONFIRMED | Zero references under `src/` |
| D-21 abort semantics in the hint | CONFIRMED | §4's trace re-verified against live source |
| D-22 it must fit | CONFIRMED; **one rule missing** | AVR warnings policy is `== 0`, stricter than the native watermark. Leonardo headroom 2130 B; CAP-02 costs +34 B |
| D-23 one plan / one commit for `eprom.cpp` | CONFIRMED; **scope reducible** | A time-only guard adds **no** golden "site" (`_is_relevant` requires `handle->`), but line numbers shift so the golden must still be re-derived. Putting the budget math in a **new** TU keeps it out of this commit |
| D-24 `native_trace_v131` stays RED | CONFIRMED; **premise corrected** | `test_trace_eprom_v131.cpp:92` pins `millis()` to 0, so D-02 adds **no** new frames to the trace. Do not claim it diverged further |
| D-25 planted-RED before believed-GREEN | CONFIRMED | Especially applicable to the `#ifndef SERIAL_ON_IO` source-contract leg |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The per-pulse fixed overhead is ~20–60 µs (3 µs set settle + 3 µs read strobe + shift-register register writes) | §Budget Arithmetic | If materially higher, the ×2+2 padding could still be tight on `0x0B` at 200 µs. Mitigation: the ×2 multiplier already absorbs a 100 % error; a plan may measure it on the bench in Phase 145 and record the figure |
| A2 | CAP-02's port costs ~+34 B flash on `leonardo` (the upstream commit measured +34 B on `uno`) | BF-1 | Only matters against the 2130 B headroom; a 3× miss is still inside it |
| A3 | The D-02 emission + time gate costs on the order of 40–120 B flash on `leonardo` | BF-2, D-22 | If it overruns, D-22's "must fit" bar fails and a shrink ladder becomes necessary. Measure cold, early — do not defer to the last plan |
| A4 | A 1000 ms emission interval is a good user-facing cadence | Pattern 3 | Purely cosmetic; adjustable without design change |
| A5 | Advertising the budget on **every** command's ack (not just `CMD_WRITE`) is correct | Example 2 | If a non-write command's protocol makes `eprom_block_budget_s` return a misleading value, the host's write-only consumption makes it inert. Keeping the ack shape command-invariant is what CAP-02's own commit message argues for ("the ack's shape therefore never varies by build config") |
| A6 | `handle->pulse_delay` has already had `configure_eprom`'s `pulse_delay == 0` fallback applied by the time the ack is packed | Example 2, Open Question 1 | **If wrong, a DB-pulse-of-0 chip advertises a 2 s budget — a spurious-timeout path.** Must be verified at plan time by reading `init_programmer_framed`'s call order |
| A7 | No plan will need a new message id, so `0xBF` stays free | D-02 | If a plan reaches for one, Phase 142's H4 hand-off must be revisited |
| A8 | `pio` and the AVR toolchain are available for cold size measurement in this environment | §Environment Availability | If absent, D-22's "measure cold and record" becomes a bench obligation rather than a devcontainer one |

---

## Open Questions (RESOLVED)

All five were settled during planning. Each carries an inline **RESOLVED** marker naming where it was
actually settled — none is left for an executor to decide.

1. **Is `configure_eprom`'s `pulse_delay == 0` fallback applied before `MSG_OK_READY` is packed?**
   - What we know: `init_programmer_framed` runs `parse_json` at `:130` and emits the ack at `:157`;
     `configure_memory` → `configure_eprom` (which applies the fallback switch at `eprom.cpp:68-75`)
     is described by `_probe_port`'s own comment as running "before emitting MSG_OK_READY".
   - What's unclear: the exact statement order between `configure_memory` and the ack emit was not
     traced line-by-line in this session.
   - Recommendation: the firmware plan's first task must read the order and either pack the ack after
     the fallback or apply the same fallback inside `eprom_block_budget_s`. Add a native or
     source-contract assertion either way — this is A6 and it is a spurious-timeout path.
   - **RESOLVED: YES — the fallback has already run.** Traced line-by-line in `143-PATTERNS.md` (the
     "Ordering fact — RESEARCH Open Question 1 / A6 is RESOLVED YES" note, and the A6 row of the
     corrections table): `parse_json` (`src/firestarter.cpp:52`) calls `configure_memory` at `:92`;
     `init_programmer_framed` (`:115`) calls `parse_json` at `:130` and emits the ack at `:157`, so
     `configure_eprom`'s fallback (`src/proms/eprom.cpp:68-75`) precedes the pack. No spurious-timeout
     path. Residual, also recorded there: non-memory commands skip `configure_memory`, where
     `eprom_params_for()` returns NULL → budget 0 → host clamp → `None` → D-10's fallback. Plan
     **143-03 task 1** re-reads the ordering rather than trusting this note, and its acceptance criteria
     require the RESOLVED-YES chain and its residual to be restated in the SUMMARY.

2. **Should CAP-02's port be a `git cherry-pick` of `13eb350` or a re-implementation?**
   - What we know: `13eb350` is the unsquashed commit and touches only `src/firestarter.cpp`
     (+37/−1). `b1737b2` is its squashed form on `origin/beta`.
   - What's unclear: whether the operator wants the commit's authorship preserved (cherry-pick) or a
     fresh commit attributable to this phase.
   - Recommendation: re-implement inside the CAP-03 pack block, in one commit, and cite `13eb350` in
     the commit message. This is cleaner than a cherry-pick followed by an amend, and it lets the
     `_ready[]` size and the pack sequence be written once. Ask the operator to confirm — this is a
     provenance question, and this milestone cares about provenance.
   - **RESOLVED: re-implementation, with `13eb350` cited — and the operator confirms it, not the
     planner.** Plan **143-03** ships the recommendation: CAP-02 is *ported, not invented*, re-implemented
     inside the CAP-03 pack block in one commit that cites `13eb350`, explicitly **not** a cherry-pick
     followed by an amend, and it reads `git show 13eb350 -- src/firestarter.cpp` first rather than
     reconstructing the code from prose. The provenance half — the part only the operator can answer — is
     carried to plan **143-10**'s blocking `checkpoint:human-verify` (Part C), which puts the
     re-implementation-vs-cherry-pick choice in front of the operator by name and cites this open question
     as the reason it is being asked.

3. **Does the plan want an `#ifdef SERIAL_ON_IO` *positive* arm — an INFO-band heartbeat on Uno?**
   - What we know: INFO frames are also `rurp_log_id` calls and are therefore deferred too, so an
     INFO heartbeat is equally undeliverable mid-block on Uno. INFO **is** user-visible at default
     verbosity since the D-09/F-120-02 promotion (`serial_comm.py:262-308`).
   - What's unclear: nothing technically — the answer is that no firmware-side mechanism can deliver
     anything mid-block on Uno-class boards. The only Uno option is a **host-side** elapsed-time
     spinner, which D-02 already rejected.
   - Recommendation: no positive arm. Record it as an explicit non-claim and, if desired, defer a
     host-side tick to a future milestone.
   - **RESOLVED: no positive arm, exactly as recommended.** Plan **143-05** wraps both the emission *and
     its state variable* in `#ifndef SERIAL_ON_IO` and records the three rejected alternatives with their
     reasons (a runtime `com_mode` accessor, raising `DEFERRED_LOG_MAX`, and reserving headroom by emitting
     at most `DEFERRED_LOG_MAX - 2` frames). The non-claim is not left to prose goodwill: D-06 gains a
     second dimension — *intra-block write progress is emitted on the EPROM path only, and delivered on
     `leonardo` only* — which plan **143-05**'s SUMMARY and plan **143-10**'s record gate both require,
     and plan **143-08** proves the guard with a source-contract gate because the native oracle is
     structurally blind to it. No host-side Uno tick is added here.

4. **Does Phase 144's `dual-repo constants parity` leg (TEST-07) need to know about CAP-03?**
   - What we know: D-07 deliberately adds nothing to `constants.py`, so the `CMD_*`/`FLAG_*` parity
     surface is unchanged. But CAP-03 is a **wire-layout** parity concern that no existing gate
     covers, and meta's `CLAUDE.md` explicitly requires `serial_comm.py` and `firestarter.cpp` to
     move in lockstep.
   - Recommendation: hand this to Phase 144 as a named finding — a byte-layout parity assertion (the
     host decodes a fixture built to the firmware's documented layout) is worth one test and is
     exactly what BF-1 would have caught.
   - **RESOLVED: handed to Phase 144 / TEST-07 as a named finding, as recommended.** Plan **143-10**'s
     record gate asserts the string `test-07` appears in `143-HOST-RECORD.md` ("the wire-layout parity
     hand-off must be recorded"), so the hand-off is a machine-checked closure condition of this phase
     rather than a hope. `constants.py` is deliberately untouched (D-07), so the existing `CMD_*`/`FLAG_*`
     parity surface is unchanged and TEST-07's *new* obligation is exactly the byte-layout assertion
     described here.

5. **Should the `--pulse-us` bound be documented as minipro parity in `--help`?**
   - What we know: D-15 requires the record to state the provenance (`1..65535` is minipro parity,
     not the wire type; `extract_long` is unclamped `uint32_t`). CLOSE-03 owns the doc chapter.
   - Recommendation: put one clause in the `--help` text (as Example 6 does) so the bound is not
     mistaken for a hardware limit by a user who never reads the docs. The full reconciliation stays
     Phase 146's.
   - **RESOLVED: yes, one `--help` clause, exactly as recommended.** Plan **143-07** task 2 requires the
     `help` text to name the microsecond unit, the `1-65535` range and the minipro-parity provenance, with
     an acceptance criterion asserting all three; threat **T-143-BOUNDCLAIM** makes describing the bound as
     a hardware or wire limit a recorded, mitigated repudiation risk. H3's unclamped `extract_long` and the
     full reconciliation stay Phase 146 / CLOSE-03 + CLOSE-04, and plan **143-10**'s record gate asserts
     `minipro` appears in the record "as parity, not a type limit".

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `python3` (ambient) | quick host scripting | ✓ | 3.12 | — |
| `.venv/ci-replica/bin/python` | **CI-parity host suite** (138-04 constraint) | ✓ | 3.11 | Ambient 3.12 **masks CI results** — do not use for gate verdicts |
| `click` | `--pulse-us` | ✓ | 8.4.2 (ci-replica) / 8.3.3 (ambient) | — |
| `pytest` | host suite (1547 tests collected) | ✓ | as pinned by `.[test]` | — |
| `ruff` / `mypy` | CI-scoped gates | ✓ (via `.[test]`) | as pinned | Must be run CI-scoped: `ruff check firestarter/ tests/`, `ruff format --check`, `python tools/check_mypy_watermark.py` (watermark **35**) |
| `git` | golden blob-SHA gate (`git rev-parse HEAD:<path>`) | ✓ | — | The gate hard-requires it (`test_git_is_required_not_optional`) |
| `pio` (PlatformIO) + AVR toolchain | cold flash/warning measurement on `uno`/`uno328pb`/`leonardo`; `pio test -e native_loop_v131` | **not probed this session** | — | If absent, D-22's measurement becomes a bench obligation and must be named as such in the plan, not silently skipped |
| Bench hardware (Leonardo on `/dev/ttyACM*`) | none in this phase | n/a | — | Phase 145 owns all bench evidence; this phase's proofs are off-hardware |

**Missing dependencies with no fallback:** none identified.

**Not probed — the planner must confirm before writing a measurement task:** `pio`. Every firmware
plan that claims a flash figure or a native suite count depends on it. Probe with
`command -v pio && pio --version` as the plan's first verification step, and if it is absent, mark
the measurement as a bench obligation rather than asserting a number.

---

## Validation Architecture

`.planning/config.json` has no `workflow.nyquist_validation` key → treated as **enabled**.

### Test Framework

| Property | Value |
|----------|-------|
| Framework (host) | `pytest` + `unittest.mock`, `pytest-cov` |
| Config file (host) | `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` — `testpaths = ["tests"]`, `addopts = "-ra -q"` |
| Quick run (host) | `cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest tests/test_<file>.py -x -o addopts=""` |
| Full suite (host) | `cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest tests/ --cov=firestarter --cov-fail-under=70 -o addopts=""` |
| Framework (firmware) | Unity + ArduinoFake via PlatformIO |
| Config file (firmware) | `firestarter/platformio.ini` |
| Quick run (firmware) | `cd /workspaces/firestarter && pio test -e native_loop_v131 -f native/avr/test_loop_eprom_v131` |
| Full suite (firmware) | `pio test -e native` **and** `pio test -e native_nodevtools` (both pinned at 141 cases / 17 suites), plus `pio run -e uno -e uno328pb -e leonardo` |

`-o addopts=""` is required to see the count line — `addopts` already carries `-q` and doubling it
suppresses the summary.

### Phase Requirements → Test Map

| Req | Behavior | Test Type | Automated Command | File Exists? |
|-----|----------|-----------|-------------------|-------------|
| HOST-01 | The write call site passes the advertised budget to `get_response`, not 10 s | unit (call-arg) | `pytest tests/test_write_response_budget.py::test_write_uses_advertised_budget -x` | ❌ Wave 0 |
| HOST-01 | Absent CAP-03 → 120 s fallback, never 10 s, never a refusal | unit | `…::test_absent_budget_falls_back_to_120s -x` | ❌ Wave 0 |
| HOST-01 | Implausible advertised budget (0, 65535, >clamp) leaves the attribute `None` → fallback | unit | `…::test_implausible_budget_is_clamped_away -x` | ❌ Wave 0 |
| HOST-01 | `verify`/`read`/`blank`/`erase`/`id` still get 10 s (D-12 negative proof) | unit (call-arg) | `…::test_non_write_paths_keep_default_timeout -x` | ❌ Wave 0 |
| HOST-01 | CAP-03 decodes at the computed `ver_end` for **two different identity lengths** (the D-08 hazard) | unit (byte layout) | `pytest tests/test_hw_revision_gate.py -k cap03 -x` | ⚠️ extend existing (`_ready_body`/`_cap02_params` at `:160-172`) |
| HOST-01 | The generator survives a simulated >10 s inter-frame gap (fake clock) | unit | `…::test_long_gap_within_budget_does_not_time_out -x` | ❌ Wave 0 |
| HOST-01 | Budget arithmetic: `0x0B` @ 49999 µs yields the 99 998 µs per-byte bound (BF-3) | native | `pio test -e native_loop_v131 -f native/avr/test_loop_eprom_v131` | ⚠️ extend existing suite |
| HOST-01 | Budget arithmetic: `energy_cap_us == 0` is UNCAPPED, not "cap at zero" | native | same | ⚠️ extend |
| HOST-01 | Budget arithmetic: overprogram term is 0 for `factor == 0` and non-zero-and-capped for `factor == 3` | native | same | ⚠️ extend |
| HOST-02 | A mid-block DATA frame is rendered, not raised on (the `:573-576` raise) | unit | `pytest tests/test_write_progress.py::test_data_frame_in_main_phase_is_rendered -x` | ❌ Wave 0 |
| HOST-02 | The frame is **not** acked (D-05) — assert `send_ack` call count | unit | `…::test_progress_frame_is_not_acked -x` | ❌ Wave 0 |
| HOST-02 | Bar position subtracts the write start address (`--address` case) | unit | `…::test_offset_write_bar_starts_at_zero -x` | ❌ Wave 0 |
| HOST-02 | `start()` is **not** re-entered when the frame's total differs from the bar's | unit | `…::test_differing_total_does_not_rebuild_the_bar -x` | ❌ Wave 0 |
| HOST-02 | The bar never rewinds across a block boundary (Pitfall 1 latch) | unit | `…::test_bar_does_not_rewind_when_firmware_drives_it -x` | ❌ Wave 0 |
| HOST-02 | Firmware emits `0xE0` from the per-byte loop when the clock advances past the interval | native | `pio test -e native_loop_v131` with an **advancing** `millis()` mock | ⚠️ extend + change the `millis()` mock |
| HOST-02 | Zero frames when the clock does **not** advance (non-vacuity of the above) | native | same | ⚠️ extend |
| HOST-02 | The emission is compiled out under `SERIAL_ON_IO` (BF-2) | **source contract** | `pytest tests/test_progress_emission_is_leonardo_only.py -x` (firmware repo) — greps `eprom.cpp` for the guard around the emit | ❌ Wave 0 |
| HOST-03 | `0xBD` surfaces as `EpromOperationError` carrying `error_code == 0xBD` and a message naming the address | unit | `pytest tests/test_budget_failure_render.py::test_max_pulses_is_a_program_failure -x` | ❌ Wave 0 |
| HOST-03 | Same for `0xBE`; and `0xAE` gets the `--pulse-us` remediation clause | unit | `…::test_energy_cap_and_pulse_too_wide -x` | ❌ Wave 0 |
| HOST-03 | The hint states abort semantics and offers **no** retry (D-21) — assert forbidden substrings | unit | `…::test_hint_offers_no_retry_and_no_resumption -x` | ❌ Wave 0 |
| HOST-03 | No host code keys on `0xB1` for this family (D-20) | **source contract** | `…::test_no_host_path_expects_write_failed_on_27c -x` | ❌ Wave 0 |
| HOST-04 | `--pulse-us N` sets `"pulse-delay"` on the wire dict and mutates **no** caller dict | unit | `pytest tests/test_pulse_us_override.py::test_override_rides_the_db_dict -x` | ❌ Wave 0 |
| HOST-04 | No new wire key and no new command appear in the emitted frame | unit (negative) | `…::test_no_new_wire_field_is_added -x` | ❌ Wave 0 |
| HOST-04 | Absent flag → the DB pulse is emitted unchanged | unit | `…::test_absent_flag_leaves_db_pulse -x` | ❌ Wave 0 |
| HOST-04 | The D-17 report line always prints and names both values | unit (CliRunner) | `…::test_override_always_reports -x` | ❌ Wave 0 |
| HOST-05 | `--pulse-us 0` / `65536` / `abc` → exit **2** with an actionable message | unit (CliRunner) | `…::test_out_of_range_is_refused_at_parse_time -x` | ❌ Wave 0 |
| HOST-05 | **No** serial port is opened on refusal (assert `find_and_connect` not called) | unit (negative) | `…::test_refusal_opens_no_port -x` | ❌ Wave 0 |
| HOST-05 | **`write` with NO `--pulse-us` still exits 0** (Pitfall 3 regression guard) | unit (CliRunner) | `…::test_write_without_pulse_us_still_works -x` | ❌ Wave 0 |
| HOST-05 | `--pulse-us` is absent from `read`/`verify`/`blank`/`erase` (D-18) | unit (negative) | `…::test_flag_is_write_only -x` | ❌ Wave 0 |
| BF-1 | The firmware's ack layout matches the host's decoder byte for byte | **source contract** or byte-layout parity | a fixture built to the documented layout, decoded by the real `_decode_id_frame` | ❌ Wave 0 (hand to Phase 144 as well) |

### Sampling Rate

- **Per task commit (host):** the touched test module, e.g.
  `.venv/ci-replica/bin/python -m pytest tests/test_pulse_us_override.py -x -o addopts=""`
- **Per task commit (firmware):** `pio test -e native_loop_v131` — and **commit before running the
  full firmware suite** (Pitfall 7).
- **Per wave merge (host):** `ruff check firestarter/ tests/` + `ruff format --check firestarter/ tests/`
  + `python tools/check_mypy_watermark.py` + `pytest tests/ --cov=firestarter --cov-fail-under=70`
- **Per wave merge (firmware):** `pio test -e native` + `pio test -e native_nodevtools` (141 cases /
  17 suites each) + `pio run -e uno -e uno328pb -e leonardo` + `python scripts/check_build_warnings.py`
- **Phase gate:** the full host suite and all three AVR builds green; `native_loop_v131` green;
  `native_trace_v131` RED **and named as expected** (D-24); `protocol_branch_inventory` green against
  the re-derived golden; `check_size_baseline.py` RED for the recorded, operator-accepted reasons
  (MERGE-05 + the CAP-02 +34 B drift) and for **no other** reason.

### Wave 0 Gaps

- [ ] `firestarter_app/tests/test_write_response_budget.py` — HOST-01 host half
- [ ] `firestarter_app/tests/test_write_progress.py` — HOST-02 host half
- [ ] `firestarter_app/tests/test_budget_failure_render.py` — HOST-03
- [ ] `firestarter_app/tests/test_pulse_us_override.py` — HOST-04 + HOST-05
- [ ] `firestarter_app/tests/conftest.py` — `make_comm` must gain `write_block_budget_s` (fail-closed
      obligation, mirrors the CAP-02 comment at `serial_comm.py:104-113`)
- [ ] `firestarter_app/tests/test_hw_revision_gate.py` — extend `_cap02_params` with an optional
      budget tail; add ≥2 identity lengths to prove the `ver_end` offset
- [ ] `firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp` — budget arithmetic
      cases **and** the `millis()` mock change (from `AlwaysReturn(0)` to an advancing counter,
      copying `test_cobs_data_frame.cpp:140-167`)
- [ ] `firestarter/tests/test_progress_emission_is_leonardo_only.py` — the `#ifndef SERIAL_ON_IO`
      source-contract gate (BF-2)
- [ ] `firestarter/tests/golden/protocol_branch_inventory.json` — re-derived by independent parse,
      in the same commit as the `eprom.cpp` edit (D-23), with the changed site named in the commit
      message
- [ ] No framework install needed — both suites exist.

**D-25 obligation:** each new gate leg above must be **seen RED on a planted violation** and **seen
GREEN for the right reason**, with both transcripts captured verbatim in the owning plan's SUMMARY. A
pre-authored leg can be unreachable — RED alone proves nothing.

---

## Security Domain

`.planning/config.json` has no `security_enforcement` key → treated as **enabled**.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Local USB serial to an attached microcontroller; no identity, no credential |
| V3 Session Management | no | No session concept on the wire |
| V4 Access Control | no | No multi-user surface; the CLI runs with the invoking user's privileges |
| V5 Input Validation | **yes** | Two inputs are validated in this phase: the user's `--pulse-us` (`click.IntRange(1, 65535)`, parse-time) and the firmware's advertised budget (a **plausibility clamp** in `_decode_id_frame`, mirroring CAP-01's `[1, 4096]`) |
| V6 Cryptography | no (unchanged) | CRC8-CCITT is an integrity check, not a cryptographic control, and is untouched. Never describe it as one |
| V12 Files & Resources | partial (unchanged) | `_main_phase_send_data` reads a user-named binary; the existing `os.path.exists` check is untouched |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A corrupt or hostile ack installs an unbounded host timeout (a wedge/DoS) | Denial of Service | The CAP-03 plausibility clamp — `if 1 <= value <= WRITE_BUDGET_MAX_S`. Verified precedent: CAP-01 rejects buffer sizes outside `[1, 4096]` (`serial_comm.py:358-363`, `T-55-06`) |
| A length-prefixed field is read past the buffer, or a partial value is trusted | Tampering / Information Disclosure | Every arm is length-gated before indexing, and a truncated tail leaves the field `None` rather than yielding a partial value. Existing precedent and test: `test_decode_truncated_version_prefix_leaves_identity_none` |
| An out-of-range `--pulse-us` reaches silicon as an unintended program pulse | Tampering (physical) | **Two independent gates**: Click's parse-time `IntRange` (host) and `configure_eprom`'s pre-flight `MSG_ERR_PULSE_TOO_WIDE` refusal **before any high voltage is enabled** (firmware, `eprom.cpp:92-110`). D-16 deliberately keeps both rather than mirroring the table host-side |
| A frame-count-unbounded emission exhausts a fixed-size buffer and drops a **safety-relevant** frame | Denial of Service / Repudiation | **This is BF-2, and it is real.** The `deferred_log[4]` buffer drops the excess. Mitigated by compiling the emission out on the affected targets, not by growing the buffer |
| An unbounded allocation sized from frame content | Denial of Service | Not introduced: the CAP-03 field is a fixed 2 bytes and nothing is allocated from it. `seen_message_ids` remains a bounded set of ints (`T-120-39`) |
| A high-voltage route is left energised on an error exit | Tampering (physical) | Already discharged by Phase 142's single-exit wrappers (VPP-02/VPP-03). **This phase touches no VPP path** and must not weaken them: the emission goes inside the body that the wrapper already covers |

**Non-claim:** nothing in this phase changes the trust model. The host trusts the attached firmware,
which it must; the two clamps above exist to prevent a *malfunctioning or mismatched* board from
wedging the host, not to defend against an adversarial one.

---

## Sources

### Primary (HIGH confidence — read directly this session)

**Firmware (`/workspaces/firestarter`, `gsd/v1.31-27c-programming-algorithm-fidelity` @ `1d64bb5`)**
- `src/proms/eprom.cpp` — `configure_eprom` fallback + both refusals (`:68-110`),
  `eprom_overprogram_us` (`:189-195`), `eprom_internal_report_budget_failure` (`:215-224`),
  `eprom_hv_route_mask` (`:256-266`), `eprom_internal_write_execute_body` incl. the `delay(500)`
  settle and the per-byte loop (`:277-401`), `eprom_write_execute` wrapper (`:425-430`)
- `src/proms/eprom_params.cpp` — the three shipped rows, verbatim
- `include/eprom_params.h` — column semantics, `energy_cap_us == 0` = UNCAPPED, the `sizeof == 12`
  assert, the `3 x overprogram_factor` comment defect
- `src/proms/memory.cpp` — `mem_util_split_delay`/`mem_util_delay_us` (`:233-253`),
  `memory_get_data` (`:283-305`), `memory_set_data` (`:329-339`), `mem_util_blank_check` and the only
  existing `0xE0` emitter with its **programmer-mode drop warning** (`:389-467`)
- `src/boards/uno_rurp_shield.cpp` — `com_mode`, `deferred_log[4]`/`DEFERRED_PARAM_MAX 8`,
  `rurp_set_programmer_mode`/`rurp_set_communication_mode`, the `rurp_log_id` strong override and its
  silent-drop arm
- `include/rurp_shield.h:64-76` — `SERIAL_ON_IO` conditional; typed no-ops otherwise
- `src/firestarter.cpp` — `init_programmer_framed` incl. `LOG_OK_ID_U16(MSG_OK_READY, …)` at `:157`
  and `op_reset_timeout()` at `:158`; `command_done` (`:162-171`); `loop()`'s `TIMEOUT_MS` watchdog
  (`:174`) and dispatch switch (`:215-291`)
- `src/operation_utils.cpp` — `op_execute_stateful_operation` (`:63-83`), `op_get_message`
  (`:209-250`), `op_wait_for_ack` (`:185-196`), `_execute_operation_house_keeping` (`:276-300`),
  `_single_step_operation_callback` and its programmer-mode comment (`:352-375`),
  `_execute_operation` (`:385-392`), `_check_response` (`:402-418`)
- `src/eprom_operations.cpp` — `_process_incoming_data` (`:76-125`) and the `:93` "host shows its own
  progress" comment D-02 falsifies
- `src/json_parser.c` — `key_pulse_delay` (`:61`), `get_delay` → `extract_long` (`:304-306`)
- `include/logging_id.h` — `LOG_OK_ID_U16`/`LOG_OK_ID_BYTES` (`:125-128`), `LOG_DATA_ID_U32_U32` (`:180`)
- `include/firestarter.h:52-56` — CAP-01 note and `TIMEOUT_MS 1000`
- `platformio.ini` — `SERIAL_ON_IO` on `uno`/`uno328pb` only (`:38,55`); `build_src_filter` (`:163`,
  `:252`, `:290`); `[env:native_loop_v131]` and its NO-CI-COVERAGE caveats (`:373-420`)
- `tests/golden/protocol_branch_inventory.json` — `meta.how_to_update`, `blob_shas`, `frozen_for`,
  `counts` (26 sites / 1 protocol-keyed)
- `tests/test_protocol_branch_inventory.py` — `_is_relevant` (`:268-274`), the blob-SHA test
  (`:398-415`), the site-by-site test (`:417-441`), `protocol_lines == [70]` (`:443-461`)
- `scripts/baseline/size_baseline.json` — AVR/native figures, `policy.avr_rule == "== 0"`,
  `warm_vs_cold_correction`, `deltas_vs_base01`
- `test/native/avr/test_loop_eprom_v131/{test_loop_eprom_v131.cpp,host_stubs.cpp}` — `setUp`'s
  `millis()` `AlwaysReturn(0)` (`:133`), the log-frame capture API, `make_loop_handle`
- `test/native/avr/_shared/host_stubs_common.inc:219-268` — the ungated capturing `rurp_log_id`
- `test/native/avr/test_cobs_data_frame/test_cobs_data_frame.cpp:140-167` — the advancing `millis()`
  mock precedent
- `CLAUDE.md` §Algorithm Handlers — the 0x07/0x08/0x0B rows and the corrected 99 998 µs derivation
- Git: `git merge-base --is-ancestor b1737b2 HEAD` → 1; `git branch -a --contains b1737b2` →
  `origin/beta`; `git show 13eb350 -- src/firestarter.cpp` (the full CAP-02 emit)

**Host (`/workspaces/firestarter_app`, same branch @ `924f943`)**
- `firestarter/serial_comm.py` — `DEFAULT_RESPONSE_TIMEOUT` (`:66`), `NON_RESPONSE_PREFIXES` (`:92`),
  the class-level CAP-02 attribute comment (`:104-113`), `__init__`'s attribute block (`:126-160`),
  `_log_rurp_feedback`'s INFO→`logging.INFO` promotion (`:295-317`), `_decode_id_frame` with CAP-01
  (`:356-363`) and CAP-02 (`:364-376`), the GATE-1.8d ring-fence header (`:379-389`), the fenced
  generator incl. both `start_time` resets (`:390-516`), `get_response` and its significant filter
  (`:518-531`), `expect_ack`'s `get_response(timeout)` (`:533-540`), `_probe_port` in full
- `firestarter/eprom_operations.py` — `_raise_for_error_response` (`:75-91`),
  `_boot_block_hint_message` (`:106-170`), `ClassProgressHandler` (`:240-282`),
  `_calculate_buffer_size` (`:300-313`), `_setup_operation` and the `command_dict` copy (`:315-373`),
  `_run_state_machine` (`:420-461`), `_execute_phase` with its `ack_data=False` regression comment
  (`:463-490`), `_handle_progress_response` (`:492-518`), `_main_phase_simple` (`:522-536`),
  `_main_phase_send_data` incl. `:561`/`:564`/`:568-576`/`:591`, `consistency_check_eprom`'s
  DB-dict override (`:750-773`), `write_eprom` (`:1583-1673`), `verify_eprom` (`:1676-1710`)
- `firestarter/cli_handlers.py` — `AppContext` (`:116-128`), `cli()` group callback (`:405-442`),
  the `write` command's options and docstring (`:546-628`), the D-04 report-line block (`:667-690`),
  `--read-settling`/`--read-strobe` (`:1469-1494`)
- `firestarter/messages.py` — `MSG_OK_READY` (`:142-150`), `MSG_ERR_PULSE_TOO_WIDE` (`:610-619`),
  `MSG_ERR_MAX_PULSES`/`MSG_ERR_ENERGY_CAP` (`:745-762`), `MSG_DATA_PROGRESS` (`:763-772`)
- `firestarter/database.py` — `_parse_pulse_duration` (`:128-142`), `programmer_data` (`:549-560`)
- `firestarter/constants.py:142-148` — the `JSON_KEY_*` convention
- `firestarter/chip_resolver.py` — `resolve_chip`
- `tests/conftest.py` — `build_frame` (`:125-135`), `_FakeSerial` (`:138-192`), `make_comm`
  (`:200-231`), `make_app_context`
- `tests/test_hw_revision_gate.py:155-220` — `_ready_body`/`_cap02_params` and the four ack-decode tests
- `tests/test_fwguard.py:114-134` — `test_absent_identity_refuses`
- `tests/test_eprom_operations.py:1205-1260` — the full hardware-free write harness
- `.github/workflows/ci.yml` — every gate step
- `pyproject.toml` — `click>=8.1` (`:50`), pytest config (`:105-107`), `mypy_error_watermark = 35`
  (`:174`)
- `tools/check_mypy_watermark.py` — the gate's shape
- `CLAUDE.md` — codegen/constants/gate obligations

**Planning artifacts**
- `.planning/phases/143-host-timeout-progress-pulse-override/143-CONTEXT.md` (in full)
- `.planning/REQUIREMENTS.md:214-224, 318-325`
- `.planning/ROADMAP.md:180, 377-403`
- `.planning/STATE.md:1-171` (incl. OD-1/OD-2/OD-3 and the C1/C2/C3 corrections)
- `.planning/phases/141-per-byte-program-loop/141-LOOP-RECORD.md` §4, §5, §12 (H2/H3/H4)
- `.planning/phases/142-high-voltage-routing/142-VPP-RECORD.md` §1.3, F-142-08, H4
- `.planning/phases/138-preconditions-baseline/138-02-PULSE-DISTRIBUTION.md`

### Secondary (MEDIUM confidence — measured this session, single method)

- Click's `IntRange`/default interaction, measured empirically with
  `.venv/ci-replica/bin/python` + `CliRunner` on click 8.4.2 (7 cases, transcript in
  `/tmp/claude-1000/…/scratchpad/click_probe.py`). Cross-checked against Click's documented
  `type_cast_value` None short-circuit.
- The per-block worst-case table, computed in Python this session; **cross-confirmed** for the `0x0B`
  49 999 µs case by `firestarter/CLAUDE.md`'s own 0x0B row (F-141-10), which derives 99 998 µs
  independently.
- Test collection count (1547) from a single `--collect-only` run.

### Tertiary (LOW confidence — flagged for validation)

- The per-pulse fixed-overhead range (A1). Derived from two citable `delayMicroseconds(3)` calls plus
  an estimate of shift-register register-write cost. **Not measured.** A Phase 145 bench run should
  record the real figure.
- Flash-cost estimates for the D-02 emission (A3) and CAP-02's Leonardo cost (A2). **Measure cold.**
- `pio` availability in this devcontainer — **not probed.**

### Not consulted (and why)

Context7, WebFetch and WebSearch were **not** used. Every question in this phase is answered by
in-tree source, in-tree tests, in-tree records, or a local empirical measurement. `brave_search`,
`exa_search` and `firecrawl` are all `false` in the init context. No external library API, version, or
ecosystem practice is in question: the only third-party surface is `click`, whose behaviour was
measured directly against the pinned interpreter rather than read about — a stronger source than any
documentation page.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|------|-------|--------|
| Standard stack | HIGH | No new dependency; every version read from the pinned config or the installed interpreter |
| Architecture / integration points | HIGH | Every line number, predicate and call chain re-located and read this session in both repos |
| BF-1 (CAP-02 absent) | HIGH | Four independent oracles: the emit site, `git merge-base --is-ancestor`, `git branch --contains`, and the app-side test that asserts the refusal |
| BF-2 (Uno com_mode gate) | HIGH | The mechanism is documented in-tree **twice** (`uno_rurp_shield.cpp:24-33`, `memory.cpp:520-527`) and the buffer constants, the drop arm and the `SERIAL_ON_IO` scoping were each read |
| BF-3 (formula correction) | HIGH | Derived from the shipped loop's statement order, computed numerically, and independently corroborated by `firestarter/CLAUDE.md`'s own derivation |
| Budget encoding / clamp ceiling | HIGH on the arithmetic; MEDIUM on the padding multiplier | The worst-case table is exact; the ×2+2 rule rests on A1's overhead estimate |
| Click / HOST-05 behaviour | HIGH | Measured empirically on the CI-parity interpreter, 7 cases |
| Pitfalls | HIGH | Every one is located in source or measured; none is recalled |
| Flash costs | MEDIUM-LOW | Estimated, not measured (A2, A3). Marked as assumptions |
| Per-pulse overhead | LOW | Estimated from two documented delays plus reasoning (A1). Marked as an assumption |
| Environment (`pio`) | LOW | Not probed |

**Research date:** 2026-08-12
**Valid until:** 2026-09-11 (30 days) for the in-tree findings — **but** BF-1's ancestry claim is
invalidated the moment CAP-02 is ported into the v1.31 firmware branch, and the golden's `blob_shas`
are invalidated by the first `eprom.cpp` keystroke. Re-locate every symbol before relying on a line
number.
