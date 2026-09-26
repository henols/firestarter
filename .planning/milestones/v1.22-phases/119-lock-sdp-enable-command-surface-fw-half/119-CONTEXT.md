# Phase 119: LOCK — SDP-enable + command surface (FW half) - Context

**Gathered:** 2026-07-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Make SDP-**enable** a real, standalone firmware capability — the milestone's only new
state-mutating operation — on top of Phase 118's proven observability, with a command-admission
guard that is provably safe under **both** build configurations.

**In scope (LOCK-01..06):**
- The 3-load `AA→0x5555, 55→0x2AAA, A0→0x5555` SDP-enable sequence plus `t_WC`, **no data
  payload** (LOCK-01).
- `CMD_SDP_UNLOCK` / `CMD_SDP_LOCK` as commands invocable in their own right at the two free
  slots **9 and 10** (LOCK-02).
- `is_memory_cmd()` replacing the `#ifdef DEV_TOOLS`-conditional ordinal guard at
  `firestarter/src/firestarter.cpp:79`, proven identical with and without `-D DEV_TOOLS`
  (LOCK-03).
- Lock/unlock **fail-closed** for any `protocol != 0x0D`, never silently accepted (LOCK-04 —
  see D-06 for the mechanism change).
- `FLASH_ENABLE_WRITE_PROTECTION` preserved, not deduped, with the datasheet-correctness of the
  duplication recorded (LOCK-05).
- A measured `pio run` flash delta reported against live headroom (LOCK-06 — see D-15).
- **Newly pulled in by D-08:** a generic NULL-`main` refusal that also closes `CMD_ERASE` /
  `CMD_CHECK_CHIP_ID` phantom-success on `0x0D` — i.e. **part of Phase 121's DEVTEST-01
  firmware half lands here.** This is an owned, operator-approved scope addition, not a leak.
- **Newly pulled in by D-16:** a worst-case per-byte t_BLC measurement of
  `eeprom28c_write_execute`'s page-load loop, measured on **all three** attached boards.
- The three-repo message-catalog codegen ritual for the two new lock ids (118 D-03's pattern).
- The CORRECTION-4-item-4 cross-repo gate checklist — mandatory in every phase from 118 on.

**Explicitly NOT in scope:**
- Any host CLI surface: `firestarter dev sdp <chip> enable|disable`, `write --skip-sdp-unlock`
  argparse/Click wiring, `constants.py` `CMD_*`/`FLAG_*`/`COMMAND_NAMES` additions, wire
  emission of `cmd 9`/`cmd 10` — **Phase 120 (HOST-01..06)**. Firmware-before-host is
  non-negotiable. The only permitted `firestarter_app` deltas here are **generated catalog code**
  plus **source-scanning-gate additions/repairs**.
- The host-side capability refusal for the non-SDP subset inside `0x0D` (2 FRAM parts, the
  pre-SDP `2804`/`2816`/`2817` class) — Phase 120, HOST-04, zero DB change.
- Any `chip_database.json` change, any `support_status` change, any `PROTOCOL-LEDGER` entry.
- The `${sysenv.*}` DEV_TOOLS gating mechanism matrix — stays with 999.15 / gh#8 (see
  `<deferred>`).
- The lock's own **hardware** duration measurement — unreachable without Phase 120's CLI
  (D-17).
- Docs corrections (`doc/PROTOCOLS.md` §1.6, `doc/lockable-proms.md`, …) — GATE-02, Phase 121.

**Validation ceiling applies, unchanged.** No AT28C part is on the bench. `0x0D` stays
`UNVERIFIED`, **zero** chips change `support_status`, the **84**-chip count is unchanged. Every
number this phase measures is a measurement of **the MCU driving its own latches**, never
evidence about AT28C silicon. See `.planning/REQUIREMENTS.md` §"Validation Ceiling" for the exact
permitted and forbidden claims, and `118-MEASUREMENT.md` §1/§6 for the wording that survived
review.

</domain>

<decisions>
## Implementation Decisions

### Command admission and the fail-closed surface

- **D-01: `is_memory_cmd()` enumerates the memory commands, and the resulting behaviour change for cmd 7/8 is TAKEN, not preserved.**
  The predicate is
  `{CMD_READ, CMD_WRITE, CMD_ERASE, CMD_BLANK_CHECK, CMD_CHECK_CHIP_ID, CMD_VERIFY,
  CMD_SDP_UNLOCK, CMD_SDP_LOCK}` with **no `#ifdef` inside it**. Verified during discussion: the
  guard at `firestarter.cpp:79` is `#ifdef DEV_TOOLS`-conditional, so a **release** build (no
  `-D DEV_TOOLS`) today runs `json_parse` **and `configure_memory`** for `CMD_DEV_ADDRESS (7)`
  and `CMD_DEV_REGISTER (8)` before rejecting them at `loop()`'s `default:` with
  `MSG_ERR_UNKNOWN_CMD` — it configures a memory handler for a command it will refuse. An honest
  enumeration excludes 7/8, so a release build stops doing that. **Record it in the source and
  the SUMMARY as a deliberate safety tightening**, never as an unremarked refactor side effect.
  Cmd 7/8 keep `MSG_ERR_UNKNOWN_CMD` in a release build. Rejected: making the predicate itself
  `#ifdef`-conditional (re-creates the divergence LOCK-03 exists to remove, so the invariance
  test would pass vacuously); rejected: adding a distinct "compiled out" refusal id for 7/8
  (pre-empts 999.15's channel-split question and costs a catalog decision this phase does not
  need).

- **D-02: `is_memory_cmd()` carries no `#ifdef`, and a gate enforces that.** See D-04 for the
  proof shape. The predicate's whole value is that it reads the same in both build
  configurations; an `#ifdef` inside it silently restores the defect.

- **D-03: Two free command slots exist and they are 9 and 10 — above the old guard.** Verified:
  `CMD_DEV_ADDRESS 7`, `CMD_DEV_REGISTER 8`, `CMD_READ_VPP 11` (`firestarter.h:34-51`). This is
  exactly why LOCK-03 is a **prerequisite** for LOCK-02 and not a parallel cleanup: with the
  ordinal guard in place, a DEV_TOOLS build would route cmd 9/10 into the dev-tools branch and
  never call `configure_memory`, so the new commands would have no bus configuration at all.

- **D-04: LOCK-03 is proven by a second native env AND a source-scan gate.** Add
  `[env:native_nodevtools]` overriding `build_flags` to omit `-D DEV_TOOLS` (necessary because
  `-D DEV_TOOLS` lives in the shared `[env]` block at `platformio.ini:26` and is therefore
  inherited by all three AVR envs **and** `native` — a no-DEV_TOOLS build has never been
  compiled, let alone tested). The same truth-table suite — asserting `is_memory_cmd()` over
  **every** cmd value, not a sampled subset — runs in **both** envs, giving a semantic proof
  rather than a textual one. **Plus** a `firestarter_app` AST/source-scan gate asserting the
  predicate's body contains no `#ifdef DEV_TOOLS` and enumerates exactly the expected command
  set, shipped with a **planted-violation fixture** proving the gate fails (the anti-hollow
  discipline of v1.21 SAFE-03 / 118 D-06). The second env also discharges the folded todo item 4
  (`pio test -e native` green with DEV_TOOLS absent) as a by-product.
  **Consequence to own as task work:** the new gate is a *new* firmware-source-scanning gate in
  `firestarter_app`, so it joins the CORRECTION-4-item-4 checklist for Phases 120–122 — and
  `test_filter` must be duplicated into the new env, plus a CI job line in
  `firestarter/.github/workflows/build.yml`.

### Where the protocol/capability refusal lives — LOCK-04's mechanism CORRECTED

- **D-05: ⚠ LOCK-04 CANNOT be implemented as written, and the mechanism is superseded.**
  Verified during discussion: `configure_memory` **pre-sets** the generic `main` for `CMD_READ`,
  `CMD_WRITE` and `CMD_VERIFY` (`memory.cpp:48-58`) and *then* calls `configure_eeprom28c`, whose
  switch only overrides `CMD_WRITE` and adds `CMD_BLANK_CHECK`. A literal
  `default: → MSG_ERR_NOT_SUPPORTED` arm in that switch would therefore **refuse `read` and
  `verify` on all 84 `0x0D` chips.** Separately, `configure_eeprom28c` only ever runs *for*
  `0x0D`, so a `default:` arm there cannot refuse another protocol at all. **LOCK-04's stated
  mechanism is wrong; its intent — lock/unlock fail-closed for any `protocol != 0x0D`, never
  silently accepted — is preserved by D-06.** Do not edit `REQUIREMENTS.md`; record the
  correction in this file, the phase SUMMARY, and `VERIFICATION.md` so a verifier does not read
  LOCK-04 as failed. Any `default:` arm that *is* added to `configure_eeprom28c` must be narrowly
  scoped to commands `0x0D` genuinely cannot do and must leave the pre-set generic mains alone.

- **D-06: One guard, at the op layer — NULL `main` ⇒ `MSG_ERR_NOT_SUPPORTED`.** Single site,
  smallest flash cost, and **provably total** — any protocol whose handler has no arm for a
  command is refused, present and future, with no per-handler maintenance. Rejected: a
  pre-dispatch `protocol != 0x0D` check in `configure_memory` (puts `0x0D`-specific knowledge
  into the generic dispatcher that v1.20's protocol-only rebuild deliberately kept clean);
  rejected: a `default:` arm in every `configure_*` handler (six sites, most flash against
  2992 B remaining, and each arm has to be written not to swallow the pre-set generic mains).

- **D-07: ⚠ The guard is GENERIC — the whole phantom-success class is fixed here.** Verified:
  `op_execute_stateful_operation` returns `false` immediately when `main` is NULL
  (`operation_utils.cpp:63,89`), so the calling `eprom_*` returns "finished" with
  `response_code == RESPONSE_CODE_OK` **and no error logged at all**. That is precisely
  DEVTEST-01's "reports OK having done nothing" for `CMD_ERASE` on `0x0D`. One refusal in the
  shared path fixes SDP, erase and chip-ID phantom-success together, at the lowest total flash
  cost. Rejected: scoping the guard to the SDP path only; rejected: a generic guard behind an
  enumerated allowlist.

- **D-08: ⚠ D-07's consequences are owned, not discovered later.**
  1. **Phase 121's DEVTEST-01 firmware half lands early.** Its ROADMAP scope, its plan set, and
     `REQUIREMENTS.md`'s LOCK/DEVTEST mapping must be amended — as an **explicit task in this
     phase**, with the amendment recorded in `STATE.md` and `PROJECT.md`. DEVTEST-01's host half
     (`OP_ERASE` marked `NA` for `0x0D` with a named reason in the `dev test` sweep) stays in
     Phase 121.
  2. **The blast radius crosses every protocol family.** A full cross-family native trace +
     regression sweep is mandatory: `0x05`/`0x06`/`0x07`/`0x08`/`0x0B`/`0x10`/SRAM streams must
     stay byte-identical, and every command × protocol combination that previously returned a
     silent OK must be enumerated with its new outcome. Expect this to change observable
     behaviour for the SRAM `CMD_BLANK_CHECK` case the host documents as `_SRAM_PROTO_IDS` in
     `firestarter_app/firestarter/eprom_operations.py` — check whether that host workaround
     becomes dead code and say so; **do not delete it in this phase** (host surface = Phase 120).

### The SDP-enable table and the dual-purpose hazard

- **D-09: A new `0x0D`-local `EEPROM_SDP_ENABLE[3]` with external linkage, plus a cross-guard.**
  Mirrors Phase 117 D-10 exactly: `flash_utils.h` stays **byte-frozen**, the emitter stays
  `0x0D`-local, and external linkage lets the guard read the **production** array rather than a
  transcribed test-local copy (in C++ a namespace-scope `const` array has internal linkage
  unless a prior `extern` declaration is visible — the `extern` line is load-bearing, see
  `eeprom_28c.cpp:122`). Rejected: giving the zero-caller `FLASH_ENABLE_WRITE_PROTECTION` its
  first caller (breaks D-10's "`0x0D`-local emitter" framing and couples `0x0D` to a header
  shared with the bench-proven `0x05`/`0x06` families); rejected: a local table with no guard
  (a comment is the decorative-invariant shape v1.12's hollow GATE-03 and 118's D-09 argue
  against).

- **D-10: ⚠ The dual-purpose hazard is a whole-TABLE identity, not a one-nibble one, and it is a safety property.**
  `AA-55-A0` is byte-identical to `FLASH_ENABLE_WRITE` — the **protected- write prefix**. The only thing separating "lock the chip" from "write a byte" is that **no data write follows**. FIX-05 pinned a one-nibble hazard (`…0x20` unlock vs `…0x10` erase); this is
  strictly worse. So LOCK-02's "no data payload" is a hard safety invariant, not a convenience.
  **LOCK-05 is discharged by a three-way guard plus a no-payload trace assertion:** the guard
  asserts `EEPROM_SDP_ENABLE` == `FLASH_ENABLE_WRITE_PROTECTION` == `FLASH_ENABLE_WRITE`
  byte-for-byte **and** that they are three distinct objects, making "the name is the only
  discriminator" a machine-checked fact; a native case asserts the lock stream terminates after
  **exactly 3** command writes with no data write following. The rationale comment sits next to
  the new table in `eeprom_28c.cpp`, backed by the guard rather than standing alone. Rejected:
  guard + comment with no stream-length assertion (a golden pinned to the wrong expectation stays
  green); rejected: comment only.

- **D-11: After the 3 writes, `delay(AT28C_TWC_MAX_MS)` and stop — no completion poll.**
  LOCK-01's literal shape. Verified: `eeprom28c_wait_for_sdp_completion`
  (`eeprom_28c.cpp:260-273`) is the `t_WC` delay **plus** up to 33 reads through
  `handle->firestarter_get_data`, and a `memory_get_data` read folds `READ_FLAG` into
  `DIP32_28C512_EEPROM`'s `CONTROL` bit `0x10` — so reusing it would inject read-induced
  `CONTROL` churn into all four lock goldens for an outcome D-13 says is never reported. The
  3-writes-and-nothing-else stream is also exactly what D-10's no-payload assertion wants to
  observe. Rejected: reusing the full completion function for symmetry; rejected: a third,
  lock-specific poll shape in a file that already has two.

### What a standalone lock/unlock reports

- **D-12: OK means "the sequence was emitted", and that is said in words.** `response_code` is
  left untouched on the SDP path — preserving Phase 117 D-05 and 118 D-02, permanently enforced
  by `test_case8_completion_poll_preserves_prior_severity` — which, since `loop()` initialises it
  to `RESPONSE_CODE_OK`, means an untouched path reports OK. The honesty therefore lives in the
  **message text**, not in a status code the host could misread: the report line states the
  sequence was emitted **and that the protection state cannot be read back**. HOST-05's "never a
  fabricated state boolean" is thus satisfied at the firmware end too, not only in Phase 120.
  Rejected: an unconditional unverifiable-state WARN on every lock/unlock (warns on a correctly
  completed operation — the shape 118 D-02 rejected, and it trains users to ignore the WARN
  band); rejected: reporting the DQ6 poll's outcome as lock evidence (a settled toggle bit proves
  a write cycle finished, **not** that protection was enabled — the inverted-read-back mistake
  FIX-02 deleted, in a new costume).

- **D-13: The standalone unlock reuses 118's ids; the lock gets its own new pair.** The
  standalone unlock emits the existing `MSG_INFO_SDP_UNLOCK` (`0x5E`) and
  `MSG_INFO_SDP_UNLOCK_DONE_US` (`0x5F`) so an SDP unlock reads identically however it was
  triggered; the lock gets a new emitted + duration pair, following 118 D-04's
  separate-literal-ids shape (no parameterised discriminator). **Two** new ids, one three-repo
  codegen ritual. Free ranges: INFO `0x60+`, WARN `0x88+`. Rejected: four distinct ids so the log
  says *why* the sequence ran (more flash and catalog surface, and it re-opens the "is this the
  same operation?" question 118 D-04 closed); rejected: one line for the lock with no duration
  (breaks the D-14 symmetry).

- **D-14: The lock gets the same `micros()` bracket and t_BLC budget check, via a shared helper.**
  Phase 118's budget is already length-parameterised
  (`sdp_seq_len × AT28C_TBLC_MAX_US`, measured 572 vs 600 µs), so factoring the bracket + check
  into one helper both sequences call is nearly free in flash. At 3 writes the lock's budget is
  300 µs and, at F-118-01's ~95 µs/byte, it lands near ~286 µs — **the same ~4.7 % margin**, so
  the check is as load-bearing here as there. Rejected: relying on the shared emitter's existing
  check (a user who only ever locks never exercises it, and the lock's report line would carry no
  number); rejected: bracket without check (the "nothing fails when the budget is blown" shape
  118 D-09 explicitly rejected, reintroduced on a new path).

### LOCK-06's headroom and the page-load measurement

- **D-15: ⚠ LOCK-06's `3348 B` is a superseded pre-117 figure; judge against the live number.**
  `+204 B` (Phase 117) and `+152 B` (Phase 118) are already spent, so Leonardo sits at
  **25680/28672**, leaving **2992 B**. Measure this phase's own delta against that live figure
  and show the arithmetic. **No threshold claim beyond "fits"** — matching how 117 and 118
  recorded their deltas as measured facts with provenance. Record the correction here and in the
  SUMMARY; **do not edit `REQUIREMENTS.md`**. Weight to expect from this phase's own decisions: a
  second native env, the generic NULL-`main` guard, two catalog ids, the three-way cross-guard,
  four new pinout goldens, and the shared bracket helper. Rejected: treating `3348 B` as a
  cumulative milestone budget (LOCK-06 then can't be judged from this phase's artifacts alone);
  rejected: reporting both framings (invites a later reader quoting whichever is more flattering).

- **D-16: ⚠ The page-load t_BLC measurement is TAKEN — worst-case, reported once.** PROJECT.md's
  FIFTH CORRECTION item 3 directs it at this phase. Apply the D-14 shared bracket to
  `eeprom28c_write_execute`'s per-byte `set_data` loop, track the **worst** per-byte interval
  across all pages, and report it in a **single** line after the write completes. A naive
  per-page report would emit ~512 lines on a 32 KB write — unacceptable against 118's OBS-05
  named-exceptions discipline. Note the directive **conflates two budgets**: LOCK-06 is *flash*,
  F-118-01 is *timing*. Say so explicitly, then answer the timing question anyway because the
  page-load loop is where gh#11's symptom actually lives (per Phase 117's conflation
  correction — aim wording at the **conflation**, never at "sampling rate"). Rejected: also
  making it a runtime WARN check (a compare in the hot per-byte path is what 118 D-10 declined,
  and D-16 already surfaces the number); rejected: deferring with a recorded declination.

- **D-17: Bench scope — page-load now on all three boards; the lock's hardware duration waits for Phase 120.**
  The page-load loop is reachable with the **shipped** CLI
  (`write -b --force`, which gets past the blank check an empty socket fails; `0x0D` has no
  erase, so `-b` skips nothing else on this family). `CMD_SDP_LOCK` is **not** reachable — the
  `dev sdp` command is Phase 120 — so every bench byte in this phase is driven by released host
  code and the firmware-before-host invariant holds in practice, not just on paper. Rejected: a
  throwaway raw-frame script COBS-framing `cmd: 9`/`cmd: 10` through `serial_comm.py` (would get
  all three numbers in one session, but exercises a brand-new state-mutating command on hardware
  via an unreviewed instrument); rejected: native-only with the margin recorded not-measured.

- **D-18: ⚠ THREE boards, not one — reversing 118's D-12 Leonardo-only scope.** Operator
  decision, 2026-07-28: *"Same as 118 and test uno and uno328pb that is also connected."* Per
  `118-MEASUREMENT.md` §2 the ports were `/dev/ttyACM0` = leonardo, `/dev/ttyACM1` = uno,
  `/dev/ttyUSB0` = uno328pb — **re-verify `controller:` identity per candidate port before
  driving anything** (`.planning` memory `feedback_verify_port_identity_each_task.md`; port
  numbers shuffle across replug). This is worth the reversal: F-118-01's 4.7 % headroom may not
  be board-invariant, since the Leonardo is an ATmega32u4 and the Uno-class boards are
  ATmega328P/PB with different register-write paths and a 512-byte data buffer. Constraints that
  come with it, all mandatory:
  1. **Operator statement, 2026-07-28: all three sockets are EMPTY.** So the plan is
     `autonomous: true` with **no** operator checkpoint anywhere, including before the Uno-class
     uploads. The chip-OUT-before-sideload rule
     (`.planning` memory `feedback_chip_out_before_sideload.md` — Uno-class only, Leonardo
     exempt) is satisfied by that statement, and the plan must say so rather than silently
     skipping the rule.
  2. **uno328pb is bench-unstable** (`.planning` memory
     `project_uno328pb_bench_instability_27_04.md`): retry on timeout, **never trust N=1**.
  3. **uno328pb has a VPP-recal / program-brownout history** (`project_uno328pb_vpp_recal_...`) —
     but `0x0D` is a 5 V protocol with no VPP rail, so that mechanism should not apply. State the
     reasoning; if it browns out anyway, that is a **finding**, not a failed plan.
  4. **uno328pb is really a plain Uno carrying mismatched firmware**
     (`project_uno328pb_correction.md`) — do not read a per-board difference as 328PB silicon.
  5. Report the flash delta for **all three** envs (118 reported Leonardo + Uno; uno328pb is the
     third).
  6. **D-19: On any board's failure, PROCEED and record not-measured with the reason** — 118's
     D-14 discipline. Never a fabricated PASS, never a hard block on five requirements because
     of one USB enumeration.

- **D-20: The numbers live in a dedicated `119-MEASUREMENT.md`** carrying, per board: the exact
  command, the `controller:` identity line, board + firmware build identity, `pio run` flash/RAM
  figures cross-checked against the non-regression sweep, and the raw captured log. Mirrors
  `118-MEASUREMENT.md` exactly, including its §1 "what this is not" and §6 validation-ceiling
  sections — **a rounded figure in prose is not a substitute.** Phase 122's closeout and any
  future gh#11 work both need the raw numbers with provenance.

### Claude's Discretion

- **Whether lock and unlock share one op-layer function** (cmd-discriminated, like the shared
  emitter) **or take two.** 118 D-04's separate-literal-ids preference points at two; flash cost
  points at one. Either is acceptable provided the three-way distinctness assertion (D-10) and
  the no-payload assertion both hold.
- **Exact format strings, wording and id numbers** of the two new lock catalog entries. Must
  satisfy D-12's honesty requirement in the text itself. Keep names ≤32 chars to avoid
  `messages.h` column reflow (118-02's finding).
- **Where `is_memory_cmd()` is declared** (`firestarter.h` `static inline`, `operation_utils.h`,
  or a new TU) and whether it is also used to gate `loop()`'s `switch` — provided the predicate
  itself contains no `#ifdef` (D-02) and the truth-table suite covers every cmd value.
- **The shared bracket helper's signature** and whether the worst-case page-load tracker is a
  file-static or threaded through the handle.
- **Whether the new `[env:native_nodevtools]` env runs the full `test_filter` or a subset.** The
  truth-table suite is mandatory in both; running everything twice is a CI-time judgement.
- **Whether `configure_eeprom28c` gets any narrowly-scoped `default:` arm at all** (D-05 permits
  one, D-06 makes it non-load-bearing). If added, it must not swallow the pre-set generic
  `read`/`verify` mains.
- **The order of the plan set**, subject to the hard constraint that the catalog ritual precedes
  the call sites that emit the new ids, and that `is_memory_cmd()` (LOCK-03) precedes the new
  commands (LOCK-02) — see D-03.

### Folded Todos

- **`prove-pio-dev-flag-fails-closed.md` (resolves 999.15) — item 4 ONLY.** Its item 4 asks for
  confirmation that `pio test -e native` passes with `DEV_TOOLS` **absent**, noting *"the
  shared-`[env]` inheritance means it has never actually been exercised without the flag."* That
  is precisely the prerequisite for LOCK-03's DEV_TOOLS-invariance proof, and D-04's second
  native env discharges it as a by-product. Record the result against the todo so 999.15 inherits
  the answer. **Items 1–3 are NOT folded** — see `<deferred>`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone framing and constraints (read first)
- `.planning/REQUIREMENTS.md` — LOCK-01..06 verbatim; the **Locked decisions** table; the
  **Out of Scope** table (note "Promoting SDP into shared `flash_utils` code" and "Deleting
  `FLASH_ENABLE_WRITE_PROTECTION`"); and §"Validation Ceiling", which states the exact permitted
  and forbidden claims. **Never write or accept a plan or success criterion that crosses that
  line.** Note D-05 and D-15 correct LOCK-04's mechanism and LOCK-06's headroom figure — record
  the corrections in phase artifacts, do **not** edit this file.
- `.planning/ROADMAP.md` §v1.22 → "Phase Details" → "Phase 119" — the six success criteria this
  phase is verified against, plus the five non-negotiable ordering invariants
  (harness-before-fix, fix-before-observe, observe-before-lock, **firmware-before-host**,
  `dev-test`-fix-before-closeout). Also read **Phase 121** — D-08 amends its scope.
- `.planning/PROJECT.md` §"Current Milestone: v1.22" — **all five** ⚠ correction blocks.
  Load-bearing here: THIRD CORRECTION item 2 (**66 of 84**, per-pinout inhibit table);
  FOURTH CORRECTION item 3 (`+204 B`), item 4 (*"every phase from 118 on must include an explicit
  task checking firmware renames/deletions against `firestarter_app`'s source-scanning gates"*)
  and item 5's `flash_utils.{h,cpp}` vacuous-path warning; FIFTH CORRECTION item 3
  (**F-118-01** — the 4.7 % headroom finding and its explicit page-load directive at LOCK-06) and
  item 4 (the two flash datapoints).
- `.planning/research/SUMMARY.md` — the 4-stream adjudicated synthesis; §"Critical Pitfalls" 1–2
  (the false-success trap).

### Phase 116 / 117 / 118 output — this phase's substrate
- `.planning/phases/118-observe-auto-unlock-visible-opt-out-able-fw-half/118-CONTEXT.md` —
  D-01..D-14. **D-01 (unconditional `LOG_ID` on INFO-band ids), D-02 (WARN without touching
  `response_code`), D-03 (the three-repo codegen ritual as an owned plan), D-04 (separate literal
  ids), D-09 (the runtime t_BLC budget check) and D-10 (the page-load citation, no check) all
  bind this phase.**
- `.planning/phases/118-observe-auto-unlock-visible-opt-out-able-fw-half/118-MEASUREMENT.md` —
  the **572 µs / 600 µs** figure with full provenance; §7 names LOCK-06 as its downstream
  consumer. §1 and §6 are the template `119-MEASUREMENT.md` must follow (D-20).
- `.planning/phases/118-observe-auto-unlock-visible-opt-out-able-fw-half/118-NONREGRESSION.md` §4
  — both flash datapoints with their bases (`+152 B` Leonardo **and** Uno; base `f8d10a5` →
  `1880054`; Leonardo `25680/28672`, Uno `23542/32256`). Also §"expected-red-until-merge" for
  `catalog-sync-check.yml`.
- `.planning/phases/117-fix-remap-aware-0x0d-emitter-honest-completion-signal/117-CONTEXT.md` —
  **D-05 (the SDP path never writes `response_code`), D-10 (the `0x0D`-local table decision this
  phase mirrors), D-11 (the cross-guard pattern) and D-12 (the declined recorder widening, still
  not taken) all bind this phase.**
- `.planning/phases/116-ground-truth-trace-harness/116-PREMISE.md` — TRACE-06's INIT-abort
  finding and the **per-pinout inhibit table** (§6 covers `DIP32_28C512_EEPROM`'s stale-upper-
  address hazard). D-10's four-pinout lock coverage is judged against this.
- `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md` — the case list, the verbatim
  RED captures, and §"Declined widening, recorded as an open hook".

### Firmware — the code this phase changes
- `firestarter/src/firestarter.cpp` — **the `#ifdef DEV_TOOLS`-conditional admission guard at
  :76-95** (the `if (handle->cmd < CMD_DEV_ADDRESS)` D-01 replaces), and `loop()`'s command
  `switch` at :202-250 with its `default: MSG_ERR_UNKNOWN_CMD`.
- `firestarter/include/firestarter.h` — `CMD_*` at :34-51 (**slots 9 and 10 free, above
  `CMD_DEV_ADDRESS 7`** — D-03), `FLAG_*` at :59-76 (`FLAG_SKIP_SDP_UNLOCK 0x100` is 118's), and
  `ctrl_flags` as `uint32_t` at :104.
- `firestarter/src/operation_utils.cpp` — **`op_execute_stateful_operation` at :62-84: the
  `if (handle->firestarter_operation_main)` at :63 and the bare `return false` at :83 are the
  phantom-success mechanism D-07 fixes.** Also `_execute_operation_house_keeping` :195-217,
  `_execute_operation_house_keeping_func` :230-260 (which still calls `op_wait_for_ack` and emits
  INIT/END frame pairs even for a NULL callback — so "init/end NULL ⇒ those phases are skipped"
  is imprecise; the phases run **empty**, and it is the *`DONE` round-trip* that is absent),
  `_execute_operation` :304-312 (NULL ⇒ `CONTINUE`), `op_execute_function` :97-102 (NULL ⇒
  `false`), and the state macros at :21-39 with `INIT 1 / MAIN 3 / END 5 / ENDED 6`
  (`include/operation_utils.h:24-27`).
- `firestarter/src/eprom_operations.cpp` — the `eprom_*` command entry points at :19-56;
  **`eprom_erase`'s `FLAG_CAN_ERASE` precondition at :34-40 is the shape a new SDP entry point
  mirrors**, and `op_execute_simple_operation` is the single-step wrapper the standalone commands
  need.
- `firestarter/src/proms/memory.cpp` — **`configure_memory` at :42-114. The pre-set generic
  mains at :48-58 are why D-05 corrects LOCK-04**; the protocol chain at :70-113 ends in the
  fail-closed `configure_not_implemented`.
- `firestarter/src/proms/eeprom_28c.cpp` — read it whole (555 lines, post-118). `PAGE_SIZE 64`
  :33, `AT28C_TWC_MAX_MS` :42, **`AT28C_TBLC_MAX_US` :58** (D-14's budget), `EEPROM_SDP_DISABLE`
  :108-130 (**D-09's shape template, including the load-bearing `extern` at :122 and D-10's
  rationale comment**), `configure_eeprom28c` :132-145 (**the switch D-05 constrains**),
  `eeprom28c_check_chip_id` :153+, `eeprom28c_emit_command_sequence` :222-238 (**shared by both
  sequences — its comment states nothing bus-visible may be added inside its body or
  `SDP_FIXED_*` equality breaks**), `eeprom28c_wait_for_sdp_completion` :272-285 (**D-11 declines
  reusing this**), `eeprom28c_write_init` :287+ (118's report lines and bracket),
  `eeprom28c_write_execute` :417+ (**D-16's per-byte page-load loop and D-10's existing citation
  comment**).
- `firestarter/include/flash_utils.h` — **FIX-04-frozen; stays byte-frozen (D-09).**
  `FLASH_ENABLE_WRITE` and `FLASH_ENABLE_WRITE_PROTECTION` are the two byte-identical `AA-55-A0`
  tables at :42-53 — **D-10's three-way identity subject**, alongside `FLASH_ERASE`'s `…0x10`
  and `FLASH_DISABLE_WRITE_PROTECTION`'s `…0x20`.
- `firestarter/platformio.ini` — **`-D DEV_TOOLS` in the shared `[env]` block at :26 (the leak
  D-04 works around)**, `[env:native]` at :69+ with its `test_filter` allowlist and long
  provenance comment block, and the `default_envs` constraint at :16 (`pio run` must not link
  `native`).
- `firestarter/src/json_parser.c` — `json_get_cmd` / `get_flags`; **verified in Phase 118 that a
  `uint32_t` flag and an arbitrary `cmd` integer already parse off the wire unchanged. No wire
  change is needed or permitted in this phase.**

### The message catalog — three-repo ritual (118 D-03)
- `tools/catalog/messages.toml` — **the canonical copy; edit ONLY this one.** Bands: OK
  `0x01–0x0F`, INIT `0x10–0x1F`, MAIN `0x20–0x2F`, END `0x30–0x3F`, INFO `0x40–0x7F`, WARN
  `0x80–0x9F`, ERROR `0xA0–0xDF`, DATA `0xE0–0xEF`. Free after 118: INFO `0x60+`, WARN `0x88+`.
  `MSG_ERR_NOT_SUPPORTED` already exists (:419) — **D-06 needs no new ERROR id.**
- `tools/catalog/sync_to_subrepos.sh` — the required distribution step.
- `.github/workflows/catalog-sync-check.yml:44-53` — `cmp`s meta ↔ firmware ↔ host byte-for-byte.
  **Known-and-expected: it cannot go green for v1.22 catalog work because it checks out both
  sub-repos at `ref: main`.** The in-phase proof is a local three-way `cmp` plus both
  `codegen.py --check` gates. Do not read that red job as this phase's damage.
- `firestarter/tools/catalog/codegen.py` + `firestarter/.github/workflows/build.yml:61-66` — the
  firmware `--check` drift gate. `firestarter/include/messages.h` is **generated**; never
  hand-edit (`.planning` memory `reference_firmware_messages_h_is_codegen_generated.md`).
- `firestarter_app/firestarter/messages.py` — the generated host mirror. Its raw codegen output
  is format-stable; **do NOT hand-normalise** (`.planning` memory
  `reference_codegen_ruff_clean_emitter.md`).
- `firestarter_app/firestarter/codec.py:206-209` — an unknown id logs
  `"Unknown message ID 0x.. — catalog out of date?"` and **drops the frame**, so new firmware ids
  degrade gracefully against a released b11 host.

### `firestarter_app` gates that scan firmware source — the mandatory checklist
**Every one must be checked against this phase's firmware edits (CORRECTION 4 item 4). This
phase adds a NEW one (D-04) — add it to the list for Phases 120–122.**
- `firestarter_app/tools/check_no_log_in_sdp_window.py` + `tests/test_check_no_log_in_sdp_window.py`
  + `tests/fixtures/planted_log_in_window.cpp` — 118's D-06 rewrote the window to brace-match the
  **emitter body + completion-poll body**. `_EMIT_ANCHOR_PATTERNS` and `_WAIT_ANCHOR_PATTERNS` are
  **append-only by contract**. A new lock emitter or a refactor of
  `eeprom28c_emit_command_sequence` will interact with this.
- `firestarter_app/tests/test_sdp_table_parity.py` — scans `eeprom_28c.cpp` **source text**; it
  was broken 3× by Phase 117's identifier and declaration-syntax changes. **Adding
  `EEPROM_SDP_ENABLE[3]` is exactly the change class that breaks it.** Re-verify after every edit.
- `firestarter_app/tools/gen_sdp_bus_config.py` + `tests/test_sdp_bus_config_drift.py` —
  generates `_shared/sdp_bus_config.h`.
- `firestarter_app/tests/test_revision_constants_parity.py:123-144` — the `FLAG_*` parity block
  asserts **eight hardcoded literals** under a `FW_ABSENT` skipif and does not enumerate the
  header, so firmware-only additions do not trip it. **Do not add the new `CMD_*` to
  `constants.py` here — that is Phase 120 HOST-03.**
- `firestarter_app/tools/check_dispatch.py` and `firestarter_app/tools/build_db.py` — also read
  firmware paths; expected untouched, but confirm.
- `firestarter_app/tests/test_audit_coverage_matrix.py` — **pre-existing RED**, not this phase's
  regression (`.planning` memory `reference_audit_coverage_matrix_golden_stale.md`).
- `firestarter_app/tests/test_no_programmer_found_*` — go RED with a live board attached; env
  artifact, not a regression (`.planning` memory
  `reference_characterization_no_programmer_tests_fail_with_live_board.md`). Expect this during
  D-18's bench work.

### Firmware — the test surfaces
- `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` — GREEN, in
  `test_filter`, drives **production** `eeprom28c_write_init`. **D-10's production stream
  equality and three-way distinctness live here** (118 D-08's constraint: assert on the ordered
  stream's *content*, never a call count — register-write elision is invisible to a counting
  test). `test_case8_completion_poll_preserves_prior_severity` permanently enforces D-05.
- `firestarter/test/native/avr/test_sdp_harness/test_sdp_harness.cpp` — always-green;
  **117-04's table-identity cross-guard and FIX-05's terminal-byte guards live here, so D-10's
  three-way guard goes here too.**
- `firestarter/test/native/avr/_shared/sdp_expected.h` — the `SDP_FIXED_*` arrays and
  `sdp_assert_stream_equals`. **D-10 extends it with `SDP_FIXED_LOCK_*`, so its whole-file blob
  SHA necessarily changes and this phase's identity proof shifts to per-array byte-identity of
  the pre-existing arrays — state that explicitly, since 117/118's whole-file-SHA shorthand no
  longer applies to this file.**
- `firestarter/test/native/avr/_shared/host_stubs_common.inc` — the recorder and the
  `HOST_STUBS_RECORD_BUS` / `HOST_STUBS_REAL_REGISTER_UTILS` opt-in contract. Native stubs must
  `#include rurp_register_utils.h` for zero-drift register-elision fidelity (`.planning` memory
  `reference_native_stub_misses_register_elision.md`).
- `firestarter/test/native/avr/test_dispatch/` and `test_not_implemented/` — the
  `configure_memory` dispatch suites D-07's cross-family sweep must keep green.
- `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` — the `0x0D` Tier-1
  suite; 117-03 added its write-path cases.

### Todos folded / consulted
- `.planning/todos/prove-pio-dev-flag-fails-closed.md` — **item 4 folded** (D-04). Read the whole
  file: its "Why symbol-checking, not exit codes" section explains why a passing `pio run` and a
  flash-size delta are both weak oracles here.

### Project conventions
- `firestarter/CLAUDE.md` — `[env:native]` layout, the **dispatch-order source-of-truth table**
  (must match `memory.cpp` line-for-line), and the suite-addition pattern.
- `CLAUDE.md` (meta) — the constants/flag-bit duplication rule between `constants.py` and
  `firestarter.h`. **Read alongside firmware-before-host: the rule says change both together,
  this milestone's ordering says firmware first. Phase 120 closes the pair.**

</canonical_refs>

<code_context>
## Existing Code Insights

### Verified facts established during this discussion (do NOT re-derive)
- **`CMD_*` slots 9 and 10 are free, and both sit ABOVE `CMD_DEV_ADDRESS 7`**
  (`firestarter.h:34-51`). This is the whole reason LOCK-03 gates LOCK-02.
- **The admission guard is `#ifdef DEV_TOOLS`-conditional** (`firestarter.cpp:73-91`). With
  `-D DEV_TOOLS`, only `cmd < 7` reaches `configure_memory`; **without** it, everything
  `< CMD_READ_VPP (11)` does — including 7, 8, 9, 10. So a release build already configures a
  memory handler for dev commands it will refuse (D-01).
- **`configure_memory` pre-sets the generic `main`** for `CMD_READ`/`CMD_WRITE`/`CMD_VERIFY`
  (`memory.cpp:48-58`) *before* calling the protocol handler. `configure_eeprom28c` only
  overrides `CMD_WRITE` and adds `CMD_BLANK_CHECK`, so `read` and `verify` on `0x0D` run on the
  generic mains. **A blanket `default:` arm in that switch would refuse them on all 84 chips**
  (D-05).
- **NULL `main` ⇒ silent OK, no error at all.** `op_execute_stateful_operation` returns `false`
  at `operation_utils.cpp:89` when `main` is NULL; the caller reports finished with
  `response_code == RESPONSE_CODE_OK`. This is DEVTEST-01's phantom-erase mechanism, verified in
  code (D-07).
- **INIT/END with NULL callbacks are not *skipped* — they run empty.**
  `_execute_operation_house_keeping_func` still calls `op_wait_for_ack()` and emits
  `MSG_INFO_INIT_START` / `MSG_INIT_DONE` (and the END pair) before `_execute_operation(NULL)`
  returns `CONTINUE`. What is genuinely absent for a payload-free command is the **`DONE`
  round-trip** (that lives in `_process_incoming_data`, the write path) and any `#` data frame.
  **ROADMAP criterion 1's stated reason is imprecise; its claim is still true.** `CMD_ERASE` is
  the working precedent — same shape, driven by the host's generic `_run_state_machine`.
- **`-D DEV_TOOLS` lives in the shared `[env]` block** (`platformio.ini:26`), so all three AVR
  envs **and `native`** inherit it. A no-DEV_TOOLS build has never been compiled or tested (D-04;
  the folded todo says the same).
- **`AA-55-A0` appears THREE times byte-identically**: `FLASH_ENABLE_WRITE`,
  `FLASH_ENABLE_WRITE_PROTECTION` (`flash_utils.h:42-53`) and the new `EEPROM_SDP_ENABLE`. The
  first is the **protected-write prefix** — so lock-vs-write is discriminated only by the absence
  of a following data write (D-10).
- **`MSG_ERR_NOT_SUPPORTED` already exists** (`tools/catalog/messages.toml:419`) — D-06 needs no
  new ERROR id, and `eprom_erase` already uses it for the `FLAG_CAN_ERASE` refusal.
- **`eeprom28c_wait_for_sdp_completion` is `t_WC` delay + up to 33 reads**
  (`eeprom_28c.cpp:260-273`), and a `memory_get_data` read folds `READ_FLAG` into
  `DIP32_28C512_EEPROM`'s `CONTROL` bit `0x10` — which is why D-11 declines reusing it for the
  lock.
- **118's t_BLC budget is already length-parameterised** (`sdp_seq_len × AT28C_TBLC_MAX_US`), so
  D-14's shared helper is nearly free.
- **Live flash state: Leonardo `25680/28672` (2992 B free), Uno `23542/32256`** — measured at
  `1880054` (`118-NONREGRESSION.md` §4). D-15's arithmetic starts here.

### Reusable Assets
- **`eeprom28c_emit_command_sequence`** — the shared emitter. Both sequences go through it; its
  comment states the hard constraint that **nothing bus-visible** may be added inside its body
  beyond `rurp_set_data_output()` and the `set_data` loop, or `SDP_FIXED_*` full-stream equality
  breaks.
- **`EEPROM_SDP_DISABLE[6]`'s declaration shape** (`eeprom_28c.cpp:103-124`) — the exact template
  for `EEPROM_SDP_ENABLE[3]`, including the load-bearing `extern` line and the rationale comment
  format.
- **117-04's table-identity cross-guard** in `test_sdp_harness` — D-10's three-way guard extends
  this pattern and belongs beside it.
- **118's `micros()` bracket + budget check** in `eeprom28c_write_init` — D-14 factors it into a
  shared helper rather than copying it.
- **`eprom_erase`'s precondition-refusal shape** (`eprom_operations.cpp:34-38`) — the model for a
  new SDP command entry point, and the existing `MSG_ERR_NOT_SUPPORTED` caller.
- **`op_execute_simple_operation`** — the single-step wrapper a payload-free command needs; no
  new state-machine work required.
- **v1.21 SAFE-03 / DISP-01 planted-violation fixtures** — the anti-hollow shape D-04's new gate
  follows.
- **`118-MEASUREMENT.md`** — a working, ceiling-reviewed template for `119-MEASUREMENT.md`.

### Established Patterns
- **`[env:native]` uses a positive `test_filter` allowlist** — a suite is invisible until its
  line is added AND it has an `-I` entry. D-04's second env needs its own.
- **Assert on the ordered stream's content, never on a count** — register-write elision is
  invisible to a call-counting test (116 research finding 10).
- **Every gate ships a planted-violation fixture proving it actually fails.** Structural/AST
  scans over substring greps.
- **`gh#11` framing discipline** — it is a **conflation** bug, not a sampling-rate bug (Phase 117
  correction). D-16's page-load measurement must be written aimed at the conflation.
- **Executors prematurely mark multi-plan requirements Complete** — 4× in Phase 116
  (`.planning` memory `reference_executors_prematurely_mark_requirements_complete.md`). **Name
  the allowed LOCK-NN ids in every dispatch prompt** and re-check `REQUIREMENTS.md` after each
  plan.
- **Firmware renames/deletions break host source-scanning gates** — 4× in Phase 117, 4 pytest
  cases in Phase 118. The firmware suite stays green while host CI goes red
  (`.planning` memory `reference_firmware_renames_break_host_source_scanning_gates.md`).
- **The ROADMAP's `flash_utils.{h,cpp}` shorthand does not match the real paths** — a
  `git diff -- src/flash_utils.h` check passes **vacuously**. Same trap for any new path-based
  gate.
- **STATE.md tooling under-writes and re-clobbers fields.** Call `state.record-session` FIRST,
  then progress/metric/decision calls, then hand-verify `current_phase_name` (em-dash/parenthetical
  splitting) and `progress.percent` regardless of order. Never trust the returned `updated` array.

### Integration Points
- `firestarter/src/firestarter.cpp` — `is_memory_cmd()` at the guard site; two new `case` arms in
  `loop()`'s switch.
- `firestarter/src/operation_utils.cpp` (or `eprom_operations.cpp`) — D-06/D-07's single generic
  NULL-`main` refusal.
- `firestarter/src/eprom_operations.cpp` — the new SDP command entry point(s).
- `firestarter/src/proms/eeprom_28c.cpp` — `EEPROM_SDP_ENABLE[3]`, the lock/unlock ops, the
  shared bracket helper, `configure_eeprom28c`'s new arms, D-16's page-load worst-case tracker.
- `firestarter/include/firestarter.h` — `CMD_SDP_UNLOCK 9`, `CMD_SDP_LOCK 10`, and the predicate
  if it lands here.
- `firestarter/platformio.ini` — `[env:native_nodevtools]`; `firestarter/.github/workflows/build.yml`
  — its CI job line.
- `tools/catalog/messages.toml` (meta, canonical) + `sync_to_subrepos.sh` + both generated
  artifacts — the owned codegen ritual plan.
- `firestarter_app/tools/` + `tests/` — D-04's new source-scan gate and its fixture; repairs to
  `test_sdp_table_parity.py` and `check_no_log_in_sdp_window.py` anchors.
- `firestarter/test/native/avr/_shared/sdp_expected.h`, `test_eeprom28c_sdp/`, `test_sdp_harness/`.
- New `.planning/phases/119-…/119-MEASUREMENT.md` (D-20) and a non-regression record.
- `.planning/ROADMAP.md` Phase 121 + `.planning/REQUIREMENTS.md` DEVTEST-01 mapping — D-08's
  owned amendment.

### Setup precondition (verify at plan time, do not assume)
Both sub-repos must be on `v1.22-at28c-software-data-protection-lifecycle` before any sub-repo
write. At Phase 118 close: firmware at `1880054`, host carrying 118's catalog + gate commits.
Confirm with `git branch --show-current` in each submodule — the milestone-branch check has been
a real trap twice (`.planning` memory `project_v121_submodule_branch_base.md`).

</code_context>

<specifics>
## Specific Ideas

- **LOCK-04 is the second requirement this milestone whose *mechanism* was wrong while its
  *intent* was right.** The pattern is now established: the criterion names an implementation, the
  code disproves it, and the honest move is to satisfy the intent and record the correction rather
  than either editing REQUIREMENTS.md or implementing something harmful. A literal reading here
  would have broken `read` and `verify` on all 84 `0x0D` chips — the exact class of damage this
  milestone exists to prevent.
- **The phantom-success finding is the best thing found in this discussion, and it was found by
  reading three lines of the state machine.** `op_execute_stateful_operation`'s bare
  `return false` on a NULL `main` means every unconfigured command on every protocol reports OK
  having done nothing. That is not a `0x0D` bug — it is a whole-dispatch-layer bug that DEVTEST-01
  happened to notice one instance of. Fixing it generically is cheaper than fixing it twice, and
  the operator chose that knowingly, accepting the cross-family sweep and the Phase 121 amendment.
- **`AA-55-A0` being the write prefix is the sharpest hazard in the phase.** FIX-05 guarded a
  one-nibble difference between unlock and chip-erase. Here the whole table is identical to the
  write-enable prefix, and the discriminator is an *absence* — no data write follows. An absence
  cannot be asserted by comparing a table; it has to be asserted on the stream. That is why D-10
  pairs the three-way identity guard with an explicit "stream ends after 3 writes" case.
- **Reporting OK for an operation whose result is physically unobservable is only honest if the
  message says so.** The status code cannot carry that nuance and the host must never invent it
  (HOST-05). Putting the honesty in the text — and putting it in the *firmware*, not just the
  CLI — is what stops Phase 120 from having to manufacture a boolean.
- **F-118-01 turned a "should never fire" premise into a 4.7 % margin, and the same margin applies
  at n=3.** That is why the lock gets the check too rather than inheriting an assumption, and why
  the page-load loop — running under the identical constraint, on the path where gh#11's symptom
  actually lives — finally gets measured instead of cited.
- **Three boards, not one, reverses a decision Phase 118 made deliberately.** 118's D-12 declined
  the Uno-class boards to avoid the chip-OUT rule and uno328pb flakiness. The operator reversed it
  because a per-board t_BLC margin is worth having when the headroom is 4.7 % — and the reversal
  only works because all three sockets are empty. Record the reversal *as* a reversal, with its
  constraints named, so the next phase does not read it as the new default.
- **The measurement is of the MCU driving its own latches. It is never evidence about AT28C
  silicon.** Any sentence in `119-MEASUREMENT.md` readable as bench-validating `0x0D` crosses the
  validation ceiling. `118-MEASUREMENT.md` §1 and §6 are the wording that already survived that
  review — follow them.

</specifics>

<deferred>
## Deferred Ideas

### Declined during this discussion
- **`prove-pio-dev-flag-fails-closed.md` items 1–3** — the `${sysenv.FIRESTARTER_DEV_TOOLS}`
  vs `${sysenv.FIRESTARTER_DEV_FLAGS}` fail-open/fail-closed matrix with `avr-nm` symbol capture,
  and the choice of gating mechanism. Belongs to **999.15 / gh#8**, the release-channel split
  (`.planning/notes/dev-tools-gating-channel-split.md`). Phase 119 folds only item 4; the todo
  stays open with item 4 marked answered.
- **A per-byte runtime t_BLC WARN on the page-load loop** — D-16 measures and reports the
  worst-case interval but adds no compare in the hot path, preserving 118's D-10. Natural home:
  whatever phase revisits gh#11 on real silicon.
- **A distinct "compiled out" refusal id for `CMD_DEV_*` in a release build** — D-01. More honest
  than `MSG_ERR_UNKNOWN_CMD`, but it pre-empts 999.15's channel-split design and costs a catalog
  decision this phase does not need.
- **A pre-dispatch `protocol != 0x0D` check in `configure_memory`** — D-06. Would put
  protocol-specific capability knowledge into the generic dispatcher v1.20 deliberately cleaned.
- **`default:` arms in all six `configure_*` handlers** — D-06. Most self-documenting, most flash,
  and each arm risks swallowing the pre-set generic mains.
- **A throwaway raw-frame bench script emitting `cmd: 9`/`cmd: 10`** — D-17. Would measure the
  lock's real duration now; declined because it exercises a brand-new state-mutating command on
  hardware through an unreviewed instrument. Phase 120's `dev sdp` is the right vehicle.
- **Four distinct catalog ids** so the log distinguishes auto-unlock from standalone unlock —
  D-13. Revisit if the reused pair proves ambiguous in practice.
- **Deleting the host's `_SRAM_PROTO_IDS` workaround** if D-07's generic guard makes it dead code
  — noted, not taken. Host surface belongs to Phase 120; identify it here, act there.

### Carried forward from Phase 118, still not taken
- **Widening the trace recorder to a third strobe kind (data-bus direction).** Phase 117's D-12
  named RED-BASELINE's "Declined widening" as *"Phase 118's owner"*; 118 declined it explicitly.
  Nothing in LOCK-01..06 or any decision above requires it either. **Still deferred** — recorded
  so the next owner finds it rather than inheriting silence.
- **The end-to-end `infoic.xml` `page_size` decode phase** — still operator-approved, still
  **not inserted into ROADMAP.md**. Insert with `/gsd-phase`; heed `.planning` memory
  `reference_new_milestone_phases_clear_destructive.md`.
- Unity-teardown SIGABRT root cause (`test_flash_intel_vpp`); recording every side-effecting
  `rurp_*` call; all-84-chips table-driven trace coverage; `DIP24_2816`'s missing
  `static-high-pins` (**SDP-F8**); datasheet verification of SDP magic addresses (**SDP-F7**).

### Reviewed Todos (not folded)
`todo.match-phase 119` returned **13** matches. Eleven are generic keyword overlap carrying the
same disposition as Phases 116–118 (VPP-on-reads, avrdude fallback, COBS frame deadline, v1.28
PY32 roadmap prior-art, JP4/JP5 renderer, Rev-0 photography and MODIFICATIONS trace, dead
`json_init()`, `DATA_BUFFER_SIZE` spike). Two were considered on their merits:

- **`fold-response-code-into-log-macro.md`** (0.6) — derive `response_code` from the log id's
  severity band. Declined at Phase 118 and declined again: it still shares `eeprom_28c.cpp`
  (now with this phase), and it still **conflicts with 118 D-02 / 117 D-05** — a WARN line that
  deliberately does *not* set `response_code` becomes inexpressible once severity is derived from
  the band, and `test_case8_completion_poll_preserves_prior_severity` makes that separation a
  permanently enforced invariant of the `0x0D` path. D-12 above deepens the conflict: the
  standalone lock's OK-with-honest-text shape depends on exactly that separation. Needs its own
  phase.
- **`decode-infoic-flags-bits-14-15-protect-metadata.md`** (0.6) — decode `infoic.xml` flags bits
  14/15 (protect-before / protect-after) in `build_db.py`. Real SDP-protection metadata, but
  host/DB work with no LOCK requirement behind it, and HOST-04 explicitly requires **zero DB
  change**. Natural home: Phase 120 or the deferred `page_size` phase.

</deferred>

---

*Phase: 119-LOCK — SDP-enable + command surface (FW half)*
*Context gathered: 2026-07-28*
