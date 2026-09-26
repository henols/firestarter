# Phase 118: OBSERVE — auto-unlock visible + opt-out-able (FW half) - Context

**Gathered:** 2026-07-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Turn today's silent, unconditional SDP auto-unlock on protocol `0x0D` into something the user
**sees happened** on a plain `write` and **can decline** — without ever putting a logging call
inside the SDP command sequence's timing window.

**In scope (OBS-01..05):**
- Two report lines around the unlock sequence — one before, one after, **never inside** (OBS-01).
- `FLAG_SKIP_SDP_UNLOCK` (`0x100`) honoured in firmware so the sequence can be declined, proven by
  its total absence from the recorded trace stream (OBS-02).
- A named `AT28C_TBLC_MAX_US = 100` constant cited at every call site the timing window touches,
  plus the source-scan gate with a planted-`LOG_` fixture (OBS-03).
- The emitted sequence's duration **measured** via `micros()` on a real board and logged after the
  sequence (OBS-04).
- With no new flag set, a `0x0D` write's outward behaviour unchanged from `3.0.0b11` apart from
  Phase 117's corrected emitter and the two new report lines (OBS-05).
- The three-repo message-catalog codegen ritual the new report ids require (D-03) — this phase
  **does** write into `firestarter_app`, and that is owned, not incidental.
- The rewrite of `firestarter_app`'s `check_no_log_in_sdp_window.py` window definition and its
  planted fixture (D-06).

**Explicitly NOT in scope:**
- SDP-**enable** / lock, `CMD_SDP_UNLOCK` / `CMD_SDP_LOCK`, `is_memory_cmd()`,
  `configure_eeprom28c`'s `default:` arm — Phase 119 (LOCK-01..06). Phase 119 reuses this phase's
  catalog pattern, codegen ritual, and high-flag-bit plumbing.
- Any host CLI surface, `--skip-sdp-unlock` argparse/Click wiring, `constants.py` FLAG_* emission,
  or wire emission of `0x100` — Phase 120 (HOST-01..06). **Firmware-before-host is
  non-negotiable**; the only `firestarter_app` deltas permitted here are generated catalog code and
  the source-scanning gate rewrite.
- A **runtime** t_BLC budget check on `eeprom28c_write_execute`'s page-load loop — cited only
  (D-10). The check stays at the unlock.
- Widening the trace recorder to a third strobe kind (data-bus direction). Phase 117's D-12 named
  RED-BASELINE's "Declined widening" hook as *"Phase 118's owner"* — **it is not taken here.**
  Nothing in OBS-01..05 or in any decision below requires it. Left deferred, deliberately, so the
  planner neither picks it up nor drops it silently.
- Per-chip `page_size` end-to-end decode — still the separate deferred phase from 117-CONTEXT.md,
  still not inserted into ROADMAP.md.

**Validation ceiling applies.** No AT28C part is on the bench. `0x0D` stays `UNVERIFIED`, zero
chips change `support_status`, the 84-chip count is unchanged. D-12's Leonardo measurement is a
measurement of **the emitter**, never evidence about AT28C silicon — see
`.planning/REQUIREMENTS.md` §"Validation Ceiling" for the exact permitted and forbidden claims.

</domain>

<decisions>
## Implementation Decisions

### Report-line visibility

- **D-01: Both report lines are UNCONDITIONAL.** Emit via `LOG_ID` / `LOG_ID_U32` with new
  INFO-band catalog ids — **not** `LOG_INFO_ID*`. Verified during discussion: every `LOG_INFO_ID*`
  macro is `FLAG_VERBOSE`-gated (`firestarter/include/logging_id.h:42-84`) and all 19 in-tree call
  sites use them, so the house style would leave a default `firestarter write at28c256` silent —
  which is the defect this phase exists to remove. These will be the tree's first
  non-verbose-gated INFO-band call sites; that is intentional and must be stated in the source.
  It also makes OBS-05's "byte-identical apart from the two report lines" a real claim rather than
  a vacuous one (under verbose-gating the default path emits zero new frames and OBS-05 is
  trivially true).

- **D-02: The skip path reports a WARN and leaves `response_code` untouched.** When
  `FLAG_SKIP_SDP_UNLOCK` is set, a new WARN-band id (e.g. `MSG_WARN_SDP_UNLOCK_SKIPPED`) is
  emitted unconditionally **in place of** the before/after pair. It is honest — on an
  SDP-protected part a skipped unlock means the write will not land — without fabricating an
  operation-level warning for the unprotected case where the skip is harmless. Preserves Phase
  117's D-05: nothing in the SDP path writes `handle->response_code`. Precedent for the severity:
  `MSG_WARN_FL4_BOOT_BLOCK_LOCKED`. Rejected: the `MSG_INFO_SKIPPING_ERASE` INFO shape
  (`flash_5v_page.cpp:70`) — `write -b` silently skipping erase is the footgun v1.16 Phase 92 had
  to fix; rejected: also setting `response_code = RESPONSE_CODE_WARNING` — breaks D-05 and warns
  on every skip regardless of whether it mattered.

- **D-03: The three-repo codegen ritual is owned in-phase as a named plan.** New `MSG_*` ids
  require: edit the canonical meta `tools/catalog/messages.toml` → run
  `tools/catalog/sync_to_subrepos.sh` → regenerate `firestarter/include/messages.h` **and**
  `firestarter_app/firestarter/messages.py` → verify meta `.github/workflows/catalog-sync-check.yml`
  (which `cmp`s all three copies byte-for-byte) plus both sub-repos' `codegen.py --check` drift
  gates. So a "FW half" phase necessarily writes into `firestarter_app`. Named explicitly because
  Phase 117's structural failure was an unowned cross-repo step
  (`.planning` memory `reference_firmware_renames_break_host_source_scanning_gates.md`).
  Firmware-before-host stays intact: the host delta is **generated code plus a gate rewrite** — no
  CLI flag, no wire emission, no `constants.py` FLAG_* addition.

- **D-04: Unlock-specific ids now; Phase 119 adds its own lock pair.** Matches the catalog's own
  precedent — `MSG_INFO_SKIPPING_ERASE` and `MSG_INFO_SKIPPING_ERASE_MEM` are two separate ids
  with literal format strings, not one parameterised id. Each log line reads unambiguously with
  zero param decoding. Phase 119 still reuses the pattern, the ritual, and the high-flag-bit
  plumbing. Rejected: a generic pair carrying a u8 `0=unlock / 1=lock` discriminator.

### Duration measurement and the timing window

- **D-05: `micros()` measures the six command writes ONLY.** Bracket
  `eeprom28c_emit_command_sequence(...)`. That number is the one with engineering meaning: directly
  comparable to the t_BLC per-byte budget, firmware-controlled, and genuinely board-dependent. The
  `t_WC` wait is a fixed `delay(AT28C_TWC_MAX_MS)` and the DQ6 poll is iteration-bounded, so
  including them would add a constant plus mock-dependent noise. **The two `micros()` calls sit
  OUTSIDE the emit loop**, so they perturb inter-byte timing not at all. Rejected: emit + `t_WC` +
  poll; rejected: reporting both numbers.

- **D-06: Redefine the no-log gate's window as the emitter body plus the completion-poll body.**
  Today `firestarter_app/tools/check_no_log_in_sdp_window.py` brace-matches `eeprom28c_write_init`
  and scans the span
  **between** the two call sites (`firestarter_app/tools/check_no_log_in_sdp_window.py:234-236`) —
  it never looks inside `eeprom28c_emit_command_sequence`, which is where the real inter-byte
  window lives. Rewrite it to brace-match the emitter body and
  `eeprom28c_wait_for_sdp_completion`'s body and scan there, replacing the call-site span. The
  after-line then legitimately sits right after the emit call, and OBS-03's claim finally means
  what it says. Rejected: keeping the gate and logging after the wait (gate keeps not scanning
  where timing matters); rejected: the union of all three windows.

  **⚠ Load-bearing consequence — must be an owned task, not a side effect.**
  `firestarter_app/tests/fixtures/planted_log_in_window.cpp` plants its `LOG_` **between the call
  sites**. Under the new definition that placement becomes legal, so the checker returns 0 on the
  fixture and `tests/test_check_no_log_in_sdp_window.py` (which asserts non-zero) goes **RED**
  while the gate itself goes **hollow**. The fixture must be re-planted inside the emitter body in
  the same commit. This is the exact Phase-117 failure class, seen in advance.

- **D-07: OBS-05 is asserted on the recorded BUS stream.** The `SDP_FIXED_*` goldens
  (`firestarter/test/native/avr/_shared/sdp_expected.h`) stay byte-identical and the flag-absent
  path drives the same sequence. Verified: report lines go out via `rurp_log_id` → Serial, which
  the Phase-116 recorder does not observe (it records `rurp_write_to_register` /
  `rurp_write_data_buffer` / `rurp_set_control_pin`), so the bus stream genuinely is unchanged.
  The two new serial frames are a **named, enumerated exception on the serial channel** — written
  down, not hidden. Rejected: building a serial-frame baseline recorder (Phase-116-class harness
  work, not 118's); rejected: golden identity + flash delta + prose only, which leaves the frame
  count unverified.

### `AT28C_TBLC_MAX_US = 100`

t_BLC is a **maximum**, not a delay. Post-117 the emitter is a bare `set_data` loop with
`pulse_delay = 0` and no inter-byte wait, so the constant cannot be something you insert — the six
writes already run far under budget.

- **D-09: It is a RUNTIME BUDGET CHECK.** Compare D-05's measured emit duration against
  `6 × AT28C_TBLC_MAX_US` and emit a WARN when exceeded. This makes the constant load-bearing
  rather than decorative and reuses the number OBS-04 already computes — no extra measurement. On
  a 16 MHz AVR it should never fire, which is exactly what a latent invariant looks like: it
  speaks up only if a future edit puts real work inside the loop. Rejected: a documentation-only
  constant (prose-only satisfaction of OBS-03 is the hollow-gate debt shape this project keeps
  paying down); rejected: folding the budget into the after-line's format string with no branch
  (nothing fails when the budget is blown) — though that composes and may be taken alongside.

- **D-10: Cite at both sites; check only the unlock.** t_BLC also governs the **page-load**
  window — `eeprom28c_write_execute`'s per-byte `set_data` loop runs with `pulse_delay = 0` under
  the identical constraint, and that is where gh#11's slow/failed write actually lives. The
  page-load loop gets a comment naming its shared t_BLC exposure and referencing the constant, so
  a later reader sees the constraint is shared; the **runtime check stays scoped to the unlock**.
  Satisfies OBS-03's "cited at every call site the timing window touches" literally, keeps the hot
  path free of a per-byte compare, keeps the flash delta small (LOCK-06 must be judged against
  Phase 117's measured **+204 B**, not the research's predicted saving), and plants the flag
  without expanding the diff. Rejected: silence at the page-load site — leaving the identical
  physical constraint undocumented at the one place gh#11 surfaces is how this milestone's framing
  went wrong twice; rejected: checking both.

- **D-11: The widened gate keeps ONE job — the no-logging rule.** No citation-presence assertion.
  Comment-text gates rot silently, and the checker deliberately *blanks* comment spans
  (`_strip_comments`), so a citation scan would need a second pass over uncleaned text. D-09's
  runtime enforcement is strictly stronger than a comment scan. Rejected: extending the same
  checker; rejected: a second checker with its own fixture.

### OBS-04's board measurement

- **D-12: One real Leonardo run, driven by Claude, with NO operator confirmations.** Flash the
  Phase-118 firmware to the Leonardo and issue one `write at28c256 --force` against the socket,
  capturing the verbatim output. **Operator statement (2026-07-28): "Leonardo is connected with an
  empty socket"** — so the plan is `autonomous: true` and must not insert a checkpoint asking
  about socket state. Claude still verifies `controller:` port identity before driving the port
  (standing bench discipline, `.planning` memory
  `feedback_verify_port_identity_each_task.md` — a Claude-side check, not an operator
  confirmation). The socket contents do not change the emit duration: this measures the MCU
  driving its own latches. Rejected: shipping the code and recording "not measured" as the plan
  (forfeits the milestone's only empirical result); rejected: also measuring on the Uno (drags in
  the Uno-class chip-OUT-before-sideload rule and uno328pb-class flakiness).

- **D-13: The number lives in a dedicated `118-MEASUREMENT.md`** carrying the exact command, the
  `controller:` identity line, the board + firmware build identity, and the raw captured log.
  Mirrors Phase 116's `RED-BASELINE.md` / `116-PREMISE.md` discipline and the v1.15 per-chip
  `EVIDENCE` precedent. Phase 119's LOCK-06 headroom judgement and any future t_BLC question both
  need the raw number **with its provenance**, not a rounded figure quoted in prose. Rejected:
  inline in a plan SUMMARY (SUMMARYs are read frontmatter-first downstream); rejected: the
  `PROTOCOL-LEDGER` — it records bench-verification status against silicon and `0x0D` must stay
  `UNVERIFIED`, so a measurement there invites exactly the ceiling-crossing misread this milestone
  guards against.

- **D-14: If the Leonardo run fails, PROCEED and record not-measured with the reason.**
  Never a fabricated PASS for an unavailable board. Precedent: this project's own
  CI-PENDING / structurally-green discipline (Phase 98, Phase 103). OBS-04 then closes
  software-complete with the gap stated explicitly. Rejected: hard-blocking five requirements on
  one USB enumeration; rejected: falling through to the Uno.

### Claude's Discretion

- **D-08 — where OBS-02's skip-proof case lives.** Constraints, all three mandatory: it must drive
  **production** `eeprom28c_write_init` (not the harness's reference emitter, which drives
  `FLASH_DISABLE_WRITE_PROTECTION`); it must assert on the ordered stream's **content**, never a
  call count (register-write elision is invisible to a counting test — Phase 116 research finding
  10); and its flag-absent counterpart asserting the full `SDP_FIXED_*` stream ships in the same
  commit. `test_eeprom28c_sdp` is now in `test_filter` and GREEN, so it is available as a home.
- **Exact format strings and wording** of the four new catalog entries (before, after/duration,
  skip WARN, budget-exceeded WARN) and their id numbers — INFO band `0x40–0x7F` has `0x5E+` free;
  WARN band `0x80–0x9F` has `0x86+` free.
- **Whether the budget is expressed as `6 × AT28C_TBLC_MAX_US` total or a per-byte average**, and
  whether the budget WARN carries the measured duration as a param or relies on the after-line's.
- **Native `micros()` mocking strategy.** ArduinoFake supplies `micros()`, but it aborts on an
  unmocked method call, so every suite that drives `eeprom28c_write_init` needs a `micros` mock —
  `test_eeprom28c_sdp` and `test_sdp_harness` already mock `millis()` and are the known sites.
  Whether the mock returns a fixed value (duration 0, budget never exceeded) or a controllable
  counter that enables a budget-exceeded case is Claude's call; adding a case proving the budget
  WARN actually fires is **recommended** but discretionary.
- **The before-line's exact placement** — it must sit **after** `eeprom28c_check_chip_id`'s
  early-return, since reporting an unlock that never ran would be dishonest.
- **Whether to compose D-09's check with reporting the budget on the after-line** (the rejected-
  but-compatible third option).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone framing and constraints (read first)
- `.planning/REQUIREMENTS.md` — OBS-01..05 verbatim; the **Locked decisions** table; and
  §"Validation Ceiling", stating the exact permitted and forbidden claims. **Never write or accept
  a plan or success criterion that crosses that line.**
- `.planning/ROADMAP.md` §v1.22 → "Phase Details" → "Phase 118" — the five success criteria this
  phase is verified against, plus the five non-negotiable ordering invariants
  (harness-before-fix, fix-before-observe, observe-before-lock, firmware-before-host,
  `dev-test`-fix-before-closeout).
- `.planning/PROJECT.md` §"Current Milestone: v1.22" — **all four** ⚠ correction blocks. CORRECTION
  3 (**66 of 84**, not "all 84") and CORRECTION 4 items 3 and 4 are load-bearing here: the
  measured Leonardo flash delta is **+204 B** (not net-negative), and *"every phase from 118 on
  must include an explicit task checking firmware renames/deletions against `firestarter_app`'s
  source-scanning gates."*
- `.planning/research/SUMMARY.md` — the 4-stream adjudicated synthesis; §"Critical Pitfalls" 1–2
  (the false-success trap).

### Phase 116 / 117 output — this phase's substrate
- `.planning/phases/117-fix-remap-aware-0x0d-emitter-honest-completion-signal/117-CONTEXT.md` —
  D-01..D-13. **D-05 (SDP path never writes `response_code`) and D-12 (the declined recorder
  widening, nominally named "Phase 118's owner" and NOT taken here) both bind this phase.**
- `.planning/phases/117-fix-remap-aware-0x0d-emitter-honest-completion-signal/117-VERIFICATION.md`
  — what Phase 117 actually proved (6/6) versus assumed.
- `.planning/phases/116-ground-truth-trace-harness/116-PREMISE.md` — TRACE-06's INIT-abort finding
  and the per-pinout inhibit table. §6 covers `DIP32_28C512_EEPROM`'s stale-upper-address hazard.
- `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md` — the seven cases, the verbatim
  RED capture, the post-suite-edit baseline appended by 117-01, and §"Declined widening, recorded
  as an open hook" (the D-12 subject this phase leaves deferred).

### Firmware — the code this phase changes
- `firestarter/src/proms/eeprom_28c.cpp` — post-117 state, read it whole. `PAGE_SIZE 64` at :33,
  `AT28C_TWC_MAX_MS` at :42 (the **sibling** constant, whose comment already forward-declares
  `AT28C_TBLC_MAX_US = 100` and the distinction: t_BLC bounds the *inter-byte* window, t_WC the
  *internal write cycle*), `EEPROM_SDP_DISABLE[6]` at :106-114 (external linkage, load-bearing),
  `eeprom28c_emit_command_sequence` at :206-222 (**D-06's new window; its comment already reserves
  this phase's report lines and flag gate at :190-205**),
  `eeprom28c_wait_for_sdp_completion` at :256-269, `eeprom28c_write_init` at :271-301 (the emit
  call at :291, the wait at :297), `eeprom28c_write_execute` at :303-341 (**D-10's citation site**
  — the per-byte `set_data` loop at :317-320).
- `firestarter/include/firestarter.h` — `FLAG_*` block at :59-68 (`0x80` is the highest used;
  `0x100` is free), `is_flag_set` at :70-71, `ctrl_flags` as **`uint32_t`** at :96 (so `0x100`
  needs no widening).
- `firestarter/include/logging_id.h` — `LOG_ID` / `LOG_ID_U32` (unconditional) at :28-37 versus
  the `FLAG_VERBOSE`-gated `LOG_INFO_ID*` family at :42-84. **D-01 turns on this distinction.**
- `firestarter/src/json_parser.c` — `key_flags` at :58, `get_flags` at :284-285 using
  `extract_long`, so `0x100` already parses off the wire unchanged. **No wire change is needed or
  permitted in this phase.**
- `firestarter/platformio.ini` §`[env:native]` — the `test_filter` allowlist and its long
  provenance comment block (`test_eeprom28c_sdp` was ENABLED by 117-01 and is now GREEN).

### The message catalog — three-repo ritual (D-03)
- `tools/catalog/messages.toml` — **the canonical copy; edit ONLY this one.** Severity bands are
  declared in its own section comments: OK `0x01–0x0F`, INIT `0x10–0x1F`, MAIN `0x20–0x2F`,
  END `0x30–0x3F`, INFO `0x40–0x7F`, WARN `0x80–0x9F`, ERROR `0xA0–0xDF`, DATA `0xE0–0xEF`.
- `tools/catalog/sync_to_subrepos.sh` — the required distribution step; the file header states the
  edit-then-sync contract.
- `.github/workflows/catalog-sync-check.yml:44-53` — `cmp`s meta ↔ firmware ↔ host byte-for-byte.
  **This is what makes the ritual mandatory rather than optional.**
- `firestarter/tools/catalog/codegen.py` + `firestarter/.github/workflows/build.yml:61-66` — the
  firmware `--check` drift gate. `firestarter/include/messages.h` is **generated**; never
  hand-edit it (`.planning` memory `reference_firmware_messages_h_is_codegen_generated.md`).
- `firestarter_app/firestarter/messages.py` — the generated host mirror; `CATALOG` at :121+.
  Its raw codegen output is format-stable — **do NOT hand-normalise it** (`.planning` memory
  `reference_codegen_ruff_clean_emitter.md`).
- `firestarter_app/firestarter/codec.py:206-209` — verified: an unknown message id logs
  `"Unknown message ID 0x.. — catalog out of date?"` and **drops the frame**. So new firmware ids
  degrade gracefully against a released b11 host: no crash, no garbled render.

### `firestarter_app` gates that scan firmware source (the Phase-117 lesson checklist)
**Every one of these must be checked against this phase's firmware edits — CORRECTION 4 item 4.**
- `firestarter_app/tools/check_no_log_in_sdp_window.py` — **D-06 rewrites this.** Read the whole
  file: `_EMIT_ANCHOR_PATTERNS` :89-94 and `_WAIT_ANCHOR_PATTERNS` :104-107 are **append-only** by
  contract; `_strip_comments` :119-151; the window computation at :234-236; the fail-closed
  `ValueError` paths at :208-232.
- `firestarter_app/tests/test_check_no_log_in_sdp_window.py` +
  `firestarter_app/tests/fixtures/planted_log_in_window.cpp` — **D-06's load-bearing consequence
  lives here.** The fixture must be re-planted inside the new window or the gate goes hollow and
  this pytest goes RED.
- `firestarter_app/tests/test_sdp_table_parity.py` — scans `eeprom_28c.cpp` source text; it was
  broken 3× by Phase 117's identifier and declaration-syntax changes. Re-verify after every edit
  to that file.
- `firestarter_app/tools/gen_sdp_bus_config.py` — generates `_shared/sdp_bus_config.h`; its drift
  gate is `firestarter_app/tests/test_sdp_bus_config_drift.py`.
- `firestarter_app/tests/test_revision_constants_parity.py:123-144` — the `FLAG_*` parity block.
  Verified: it asserts **eight hardcoded literals** under a `FW_ABSENT` skipif and does **not**
  enumerate the header, so a firmware-only ninth flag does **not** break it. Do not add
  `FLAG_SKIP_SDP_UNLOCK` to `constants.py` here — that is Phase 120 HOST-03.
- `firestarter_app/tools/check_dispatch.py` and `firestarter_app/tools/build_db.py` — also read
  firmware paths; expected untouched, but confirm.

### Firmware — the test surfaces
- `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` — now GREEN and in
  `test_filter`; the 8 cases post-117 including
  `test_case8_completion_poll_preserves_prior_severity`, which **permanently enforces D-05** and
  will catch any new `response_code` write in the SDP path.
- `firestarter/test/native/avr/test_sdp_harness/test_sdp_harness.cpp` — the always-green harness;
  FIX-05's terminal-byte + table-identity guards landed here (117-04).
- `firestarter/test/native/avr/_shared/sdp_expected.h` — the `SDP_FIXED_*` arrays and
  `sdp_assert_stream_equals`. **D-07's byte-identity subject; no regeneration expected.**
- `firestarter/test/native/avr/_shared/host_stubs_common.inc` — the recorder and the
  `HOST_STUBS_RECORD_BUS` / `HOST_STUBS_REAL_REGISTER_UTILS` opt-in contract, plus the list of
  suites that MUST NOT define the flags.
- `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` — the `0x0D` Tier-1
  suite; 117-03 added its write-path cases.

### Project conventions
- `firestarter/CLAUDE.md` — `[env:native]` layout, dispatch order source-of-truth, suite-addition
  pattern.
- `CLAUDE.md` (meta) — the constants/flag-bit duplication rule between `constants.py` and
  `firestarter.h`. **Read alongside the firmware-before-host invariant: the rule says change both
  together, this milestone's ordering says firmware first. Phase 120 closes the pair.**

</canonical_refs>

<code_context>
## Existing Code Insights

### Verified facts established during this discussion (do not re-derive)
- **`LOG_INFO_ID*` is `FLAG_VERBOSE`-gated** — `logging_id.h:42-84`, all 19 in-tree call sites.
  `LOG_ID` / `LOG_ID_U32` are the unconditional forms. There are **zero** existing unconditional
  emissions of an INFO-band id; D-01 creates the first.
- **`ctrl_flags` is `uint32_t`** (`firestarter.h:96`) and `get_flags` uses `extract_long`
  (`json_parser.c:471-472`) — `FLAG_SKIP_SDP_UNLOCK = 0x100` works on the wire with **no** parser
  or struct change.
- **The host FLAG parity test is non-exhaustive** — eight hardcoded literals, `FW_ABSENT` skipif
  (`test_revision_constants_parity.py:123-144`). A firmware-only ninth flag does not trip it.
- **A b11 host drops unknown message ids gracefully** — `codec.py:206-209` logs
  `"Unknown message ID 0x.. — catalog out of date?"` and returns `None`. No crash, no garbling.
- **`micros()` appears NOWHERE in the firmware today.** ArduinoFake supplies it for native, but
  aborts on an unmocked method call — so every suite driving `eeprom28c_write_init` needs a
  `micros` mock. `test_eeprom28c_sdp` and `test_sdp_harness` already mock `millis()`.
- **`messages.toml` is currently byte-identical across all three repos** (verified by `diff`), and
  `catalog-sync-check.yml` enforces that. Free ids: INFO `0x5E+`, WARN `0x86+`.
- **The existing SDP no-log gate does NOT scan the emitter body** — its window is the span between
  the two call sites inside `eeprom28c_write_init`
  (`check_no_log_in_sdp_window.py:234-236`). The real inter-byte window is inside
  `eeprom28c_emit_command_sequence`'s loop, which the gate never examines. D-06 fixes this.

### Reusable Assets
- **Phase 117's emitter was shaped for this phase.** `eeprom28c_emit_command_sequence`'s comment
  (`eeprom_28c.cpp:190-205`) explicitly reserves *"Phase 118 (report lines wrapped around the
  call, `FLAG_SKIP_SDP_UNLOCK` gating it)"* and states the hard constraint: **nothing bus-visible**
  may be added inside its body beyond the `rurp_set_data_output()` and the `set_data` loop, or the
  `SDP_FIXED_*` full-stream equality breaks.
- **`AT28C_TWC_MAX_MS`'s comment (`eeprom_28c.cpp:35-42`) already forward-declares this phase's
  constant** and draws the t_BLC-vs-t_WC distinction. Extend that comment block; do not restate it.
- **`MSG_INFO_SKIPPING_ERASE` / `_MEM`** (`flash_5v_page.cpp:70`, `flash_nor_unlock.cpp:86`) — the
  two-separate-ids precedent behind D-04, and the shape D-02 deliberately upgrades to WARN.
- **`test_case8_completion_poll_preserves_prior_severity`** — already in the suite, already
  enforcing D-05. Any new SDP-path `response_code` write fails it automatically.
- **`_strip_comments` / `_find_function_body` / `_find_anchor`** in
  `check_no_log_in_sdp_window.py` — D-06 rewrites the *window resolution*, not this machinery.
  Reuse all three.
- **v1.21 SAFE-03 / DISP-01 planted-violation fixtures** — the anti-hollow shape D-06's re-planted
  fixture follows.

### Established Patterns
- **`[env:native]` uses a positive `test_filter` allowlist** — a suite is invisible until its line
  is added AND it has an `-I` entry.
- **Assert on the ordered stream's content, never on a count** — register-write elision is
  invisible to a call-counting test.
- **Every gate ships a planted-violation fixture proving it actually fails.** Structural/AST scans
  over substring greps, because these files' own prose describes the invariants.
- **`gh#11`-adjacent framing discipline:** Phase 117 established that gh#11 is a **conflation**
  bug, not a sampling-rate bug. D-10's page-load citation must not be written as if it fixes gh#11.
- **Executors prematurely mark multi-plan requirements Complete** — 4× in Phase 116
  (`.planning` memory `reference_executors_prematurely_mark_requirements_complete.md`). Name the
  allowed OBS-NN ids in each dispatch prompt and re-check `REQUIREMENTS.md` after every plan.
- **The ROADMAP's `flash_utils.{h,cpp}` shorthand does not match the real paths** — a
  `git diff -- src/flash_utils.h` check passes **vacuously**. Same trap class applies to any new
  path-based gate written here.

### Integration Points
- `firestarter/src/proms/eeprom_28c.cpp` — the sole firmware production file this phase edits.
- `firestarter/include/firestarter.h` — one new `FLAG_SKIP_SDP_UNLOCK 0x100` define.
- `tools/catalog/messages.toml` (meta, canonical) + `sync_to_subrepos.sh` + both generated
  artifacts — D-03's owned plan.
- `firestarter_app/tools/check_no_log_in_sdp_window.py` + its pytest + its fixture — D-06.
- `firestarter/test/native/avr/test_eeprom28c_sdp/` and/or `test_sdp_harness/` — D-08's cases plus
  the `micros` mocks.
- A new `.planning/phases/118-…/118-MEASUREMENT.md` — D-13.

### Setup precondition (verify at plan time, do not assume)
Both sub-repos are on `v1.22-at28c-software-data-protection-lifecycle` (verified 2026-07-28 via
`git branch --show-current`: firmware at `f8d10a5`, host at `9dd11a9`). Confirm again before any
sub-repo write. Note the host branch already carries the quick-task `SUBMIT_REPO` retarget commits
— unrelated to this phase, leave them alone.

</code_context>

<specifics>
## Specific Ideas

- **The whole point of this phase is that silence was the defect** — so a decision that leaves the
  default path silent is not a smaller version of this phase, it is a no-op. That is why D-01
  breaks the tree's 19-call-site verbose-gating convention rather than following it, and why the
  break must be argued in the source comment, not just done.
- **The gate-window rewrite is the phase's sharpest hazard, and it was foreseen in advance.** Rewriting the
  window silently hollows the gate the rewrite is meant to strengthen, and turns its own
  anti-hollow pytest RED. Phase 117 shipped a commit claiming "zero `firestarter_app` files
  changed" while four host gates were broken; this phase starts from the knowledge that a
  cross-repo consequence with no owning task **is** the failure. Make the fixture re-plant a task
  line, not a footnote.
- **`AT28C_TBLC_MAX_US` was nearly a decorative constant.** The requirement says "cited at every
  call site", which a comment satisfies — and the project's own history (v1.12's hollow GATE-03)
  is what a decorative invariant becomes. D-09 makes it a check that will almost certainly never
  fire, and that is the correct outcome for a latent invariant.
- **t_BLC governs the page load too, and that is where gh#11 actually lives.** D-10 documents it
  without acting on it, deliberately. If a future phase revisits gh#11 on real silicon, the
  citation at `eeprom28c_write_execute`'s loop is the breadcrumb to follow — aimed at the
  conflation, per Phase 117's correction, not at the sampling rate.
- **OBS-04 is the milestone's only empirical result.** Everything else in v1.22 is a structural or
  source-level proof. That asymmetry is why D-12 spends the five minutes on the Leonardo and why
  D-13 insists on raw output with provenance rather than a number in prose.
- **The measurement's subject is the emitter, never the chip.** `micros()` around six latch writes
  says nothing about AT28C silicon. Any wording in `118-MEASUREMENT.md` that could be read as
  bench-validating `0x0D` crosses the validation ceiling.

</specifics>

<deferred>
## Deferred Ideas

### Named as Phase 118's hook by Phase 117 — explicitly NOT taken
- **Widening the trace recorder to a third strobe kind (data-bus direction).** Phase 117's D-12
  took only the production half (`rurp_set_data_output()` in the emitter) and named
  RED-BASELINE's §"Declined widening" as *"Phase 118's owner"*. **Not taken here** — it is absent
  from OBS-01..05 and no decision above needs it. Taking it would force regeneration of
  `_shared/sdp_expected.h` plus `test_sdp_harness`'s reference-emitter guards, and Phase 116
  declined it partly because the extra stub guards were never verified to compile. Recorded here
  so the next owner finds it rather than inheriting silence.

### Declined during this discussion
- **A runtime t_BLC budget check on the page-load loop** (`eeprom28c_write_execute`) — D-10 cites
  but does not check. A per-byte compare in the hot path plus the flash cost, for a surface OBS
  does not cover. Natural home: whatever phase next revisits gh#11 on silicon.
- **A citation-presence gate for `AT28C_TBLC_MAX_US`** — D-11. Would need a second pass over
  uncleaned source text; D-09's runtime check supersedes the need.
- **A serial-frame baseline recorder** so OBS-05's "exactly two new frames" is machine-checked —
  D-07. Phase-116-class harness work; none exists today.
- **Measuring on the Uno as well as the Leonardo** — D-12. Would surface the per-board t_BLC
  headroom difference; drags in the Uno-class chip-OUT-before-sideload rule.
- **A generic report-id pair with an unlock/lock discriminator param** — D-04. Phase 119 may
  revisit if four ids prove unwieldy.

### Carried forward, unchanged
- **The end-to-end `infoic.xml` `page_size` decode phase** (117-CONTEXT.md `<deferred>`) — still
  operator-approved, still **not inserted into ROADMAP.md**. Insert with `/gsd-phase`; heed
  `.planning` memory `reference_new_milestone_phases_clear_destructive.md`.
- Unity-teardown SIGABRT root cause (`test_flash_intel_vpp`); recording every side-effecting
  `rurp_*` call; all-84-chips table-driven trace coverage; `DIP24_2816`'s missing
  `static-high-pins` (**SDP-F8**); datasheet verification of SDP magic addresses (**SDP-F7**).

### Reviewed Todos (not folded)
`todo.match-phase 118` returned 11 matches. Nine are generic keyword overlap and carry the same
disposition as Phases 116/117 (VPP-on-reads, avrdude fallback, COBS deadline, Rev-0 photography
and MODIFICATIONS trace, dead `json_init()`, JP4/JP5 display, DATA_BUFFER_SIZE spike). **Two are
genuinely relevant and were put to the operator, who declined both folds:**

- **`fold-response-code-into-log-macro.md`** (0.6) — derive `response_code` from the log id's
  severity band. It was recorded as *"blocked on Phase 117 (shares `eeprom_28c.cpp`)"*; Phase 117
  is closed, so **it is now blocked on Phase 118 instead**, same file conflict. More importantly
  it **conflicts with D-02**: a WARN line that deliberately does *not* set `response_code` becomes
  inexpressible once severity is derived from the band, and Phase 117's D-05 plus
  `test_case8_completion_poll_preserves_prior_severity` make that separation a permanently
  enforced invariant of the `0x0D` path. That tension needs its own phase, not a fold.
- **`decode-infoic-flags-bits-14-15-protect-metadata.md`** (0.6) — decode `infoic.xml` flags bits
  14/15 (protect-before / protect-after) in `build_db.py`. Real SDP-protection metadata, but
  host/DB work with no OBS requirement behind it. Natural home: Phase 120 (host surface) or the
  deferred `page_size` phase, which already touches `build_db.py`.

</deferred>

---

*Phase: 118-OBSERVE — auto-unlock visible + opt-out-able (FW half)*
*Context gathered: 2026-07-28*
