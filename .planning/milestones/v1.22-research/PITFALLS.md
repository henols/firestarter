# Pitfalls Research

**Domain:** Adding a write-protection (Software Data Protection) lock/unlock lifecycle to a mature parallel-EEPROM programmer — Firestarter v1.22, protocol `0x0D` (`PROTO_EEPROM_PARALLEL` / `configure_eeprom28c`), dual-repo lockstep, **software-only validation (no AT28C part on the bench)**
**Researched:** 2026-07-27
**Confidence:** HIGH for everything code- or datasheet-verified in-tree (marked `[CODE]` / `[DATASHEET]`); MEDIUM for community/web-sourced timing and cross-manufacturer claims (marked `[WEB]`); explicitly labelled UNPROVABLE-WITHOUT-SILICON where that is the honest answer.

> **How to read this file.** Every pitfall below was derived by reading the actual tree at `v1.21`/`beta` (fw `0fd7992`, app `86e4563`) plus the in-repo primary datasheet `firestarter_app/datasheets/AT28C256.pdf` (Microchip DS20006386B). Where a claim rests on the datasheet the exact quoted wording is given, because several of this milestone's inputs are wrong and the datasheet is the tiebreaker. Phase attributions use the roadmap's starting number (**116**) and are described **by role** ("the ground-truth phase", "the harness phase") so they survive renumbering.

---

## Executive summary — the five findings that should reshape the roadmap

1. **The existing "success proof" is not weak, it is inverted.** `eeprom28c_wait_for_write(handle, 0x5555, 0x20)` waits to read `0x20` back at `0x5555`. The AT28C256 datasheet states verbatim: *"The data in the enable and disable command sequences **is not written to the device**."* So when the SDP command **is** recognised, `0x5555` keeps its old array content and this check **cannot** pass except by 1-in-256 coincidence — and when the command is **not** recognised (bytes fall through as ordinary writes), `0x20` **does** land at `0x5555` and the check **passes**. The proxy is anti-correlated with the property it claims to prove. `[DATASHEET + CODE]`
2. **The identity gate that D-08 relies on is dead code for the entire class.** `eeprom28c_write_init` only calls `eeprom28c_check_chip_id` when `handle->chip_id > 0`, but **all 84** protocol-`0x0D` DB entries carry `chip_id_check: false` / `chip_id_value: "0x00000000"`, and `database.py:399` only emits `chip-id` when `chip_id_check` is truthy. Across the whole DB 458/746 chips have an ID check — the `0x0D` class has **zero**. So "a mismatch leaves the chip protected" describes a branch that never executes today. `[CODE]`
3. **The native test harness is structurally incapable of telling SDP-enable from SDP-disable from chip-erase.** The recording stub captures only `(reg, data)` pairs from `rurp_write_to_register`; `rurp_write_data_buffer` — which carries the *actual command byte* `0xAA/0x55/0x80/0xA0/0x20/0x10` — is a silent no-op stub. All four sequences share the same address stream. Abandoned commit `0052c42` swapped `EEPROM_SDP_DISABLE` for `FLASH_DISABLE_WRITE_PROTECTION` and reported *"golden traces: all 22 tests PASS (zero-diff)"* — the traces literally cannot see the difference. `[CODE]`
4. **The lock command is one nibble away from a chip-erase command.** `FLASH_ERASE = {AA@5555, 55@2AAA, 80@5555, AA@5555, 55@2AAA, 0x10@5555}`; `EEPROM_SDP_DISABLE` is identical except the last byte is `0x20`. And `FLASH_ENABLE_WRITE_PROTECTION` is **byte-identical** to `FLASH_ENABLE_WRITE` — the name is the *only* thing distinguishing "lock the chip" from "prefix a normal write". `[CODE]`
5. **The write path already verifies 1 byte in 64.** `eeprom28c_write_execute` polls only at page end or last byte. On an SDP-locked chip the datasheet says an unprefixed write starts the timers and writes nothing, so the poll reads back the *old* value — which passes whenever old == new (e.g. `0xFF` in a mostly-blank image). This is a complete, still-shipping mechanism for gh#11's *"accepts the write, only part of the image burned"*. `[DATASHEET + CODE]`

---

## Critical Pitfalls

### Pitfall 1: The false-success trap — proving a command landed by reading back a byte the device never wrote

**What goes wrong:**
`eeprom_28c.cpp:104-108` runs the 6-load SDP-disable sequence and then infers success from `eeprom28c_wait_for_write(handle, 0x5555, 0x20)` — a 2000 × 10 µs poll (~20–40 ms, comfortably longer than the 10 ms `tWC`) waiting for `0x5555` to read `0x20`. Analyse the two possible worlds:

| World | What the silicon does | What the check observes | Verdict reported |
|---|---|---|---|
| Command **recognised** (SDP actually toggled) | Datasheet §6: *"the data in the enable and disable command sequences is not written to the device"* → `0x5555` still holds whatever the array held | `0x20` only if the array coincidentally held `0x20` (~1/256; `0xFF` on a blank part) | **spurious `MSG_ERR_EEPROM_TIMEOUT` (0xB2) → write aborts** |
| Command **not recognised** (tBLC blown, wrong addresses, wrong part) | The six loads degrade toward ordinary byte writes | `0x20` lands at `0x5555` → poll succeeds | **"success"** — and `0x5555` is now silently corrupted |

The check succeeds precisely in the failure case and fails precisely in the success case.

**Why it happens:**
Because SDP state is **not readable** on this family (`firestarter_app/doc/lockable-proms.md` §17: *"Atmel AT28C16/64/256 — usually no explicit SDP flag"*; the AT28C256 datasheet defines no status bit), the implementer reaches for the nearest observable — the last byte of the command sequence — without checking whether the datasheet says that byte is stored. It is the same shape of error as every prior incident in this project's history: `write -b` reporting "successful" while skip-erase left NOR bits unprogrammable (v1.16 Phase 90/91), DQ7 masking hiding a rejected write, the `dev test` absent-chip exit-code-only test that went green on a `Mock` that never touched hardware (Phase 114.1), and AM27C020 write#1 60/64 → write#2 0/64 (v1.18 Phase 99).

**How to avoid:**
- **Delete the read-back-the-command-byte idiom outright.** Do not "improve" it; it has no valid form.
- Replace it with the only positive proof the silicon offers: **a data-effect proof**. After unlock, write a probe byte whose target value **differs from its current value**, then read it back. Changed → unlock worked. Unchanged → unlock did not work.
- **Make "differs from current value" a hard requirement, not an incidental.** A verify-based proof is *vacuous* when the written byte equals the existing byte: the datasheet says a protected write "starts the internal write timers, no data will be written", so a rejected write and a no-op write are byte-indistinguishable. This is the same lesson v1.21 PATT-01 already locked in for `dev test` (address-derived pattern, never fixed) — reuse that reasoning verbatim.
- For the ordinary write path, **stop treating page-end polling as verification**. Firmware `wait_for_write` is a *busy-wait*, not a verify. Whole-image proof belongs to a host-side `verify` (full read-back compare), and the milestone should say so in prose so nobody re-derives the wrong conclusion.
- Record in the milestone honesty ledger: **"we cannot report SDP state"** is a permanent property of the family, not a v1.22 gap.

**Warning signs:**
- Any firmware function whose success condition is `get_data(<command address>) == <command byte>`.
- A test that satisfies a poll by scripting the expected byte into a call-ordered mock (this is exactly what `test_eeprom28c_chip_id.cpp:104` does: `s_mock_bytes[2] = 0x20; /* satisfies eeprom28c_wait_for_write(0x5555, 0x20) */`).
- A PASS claim in which the probe byte's target value was never compared against its pre-write value.
- Users reporting `0xB2 MSG_ERR_EEPROM_TIMEOUT` on chips that are demonstrably fine.

**Phase to address:**
**Phase 116 (ground truth / truth table)** must publish the state-vs-observable table above as a written artifact before any code is planned. **Phase 118 (firmware SDP primitives)** owns removing the proxy and implementing the data-effect proof. The vacuous-verify rule is a hard success criterion of the phase that exposes unlock as an operation.

---

### Pitfall 2: Bricking and irreversibility — what is actually recoverable here, and the two commands that are not

**What goes wrong:**
Three distinct hazards get conflated under "lock could brick the chip":

1. **AT28C SDP itself is fully software-reversible.** `[DATASHEET]` The disable algorithm exists, *"Power transitions do not disable SDP"* but the 6-load sequence does, and the part ships SDP-disabled. `doc/lockable-proms.md` §17 classes the whole 28C parallel-EEPROM family as reversible-SDP with **no** permanent mode. So for a *correctly identified* AT28C, lock is not a one-way door. Say this plainly — over-warning invites the operator to bolt on guards that block the feature's legitimate use.
2. **The nibble-adjacent chip-erase is a data-loss door.** `FLASH_ERASE` (`flash_utils.h:34-41`) is `AA-55-80-AA-55-`**`10`** and `EEPROM_SDP_DISABLE` is `AA-55-80-AA-55-`**`20`**. One typo, one bad copy-paste, one "helpful" table dedup and the unlock path becomes a **full-device erase**. Mitigating factor: the AT28C256 Operating Modes table lists Chip Erase as requiring `OE = V_H = 12.0 V ± 0.5 V`, a rail the `0x0D` path never routes — so on a genuine Atmel part the typo is probably inert `[DATASHEET, but MEDIUM as a safety argument]`. Do **not** lean on that: the `0x0D` class spans 20+ manufacturers (Xicor, Catalyst, Hitachi, NEC, Samsung, SGS-Thomson, EXEL, WED, Maxwell…) whose erase gating may differ.
3. **The genuinely irreversible neighbours are in adjacent buckets, and misidentification is how you reach them.** This project has already hit that wall: the v1.17 W29C040 RCA proved the seated part's first-16K boot block is **permanently locked per datasheet §6.6 with no unlock command** — full write→verify is physically impossible and the milestone shipped detection + an honest deferral (FUT-07) instead of a fix. `doc/lockable-proms.md` documents the same class for W29C020C (boot-block lockout "effectively irreversible through ordinary commands") and for later families with PPB-lock / password / OTP modes. Send an "AT28C lock" at one of those and you can set a bit no software can clear.

**Why it happens:**
The command sequences of *all* these families share the `AA@5555 / 55@2AAA` prefix — the byte streams look interchangeable, so a lock command written for AT28C is syntactically valid input to a W29C, SST39, Am29F or Intel 28F part sitting in the socket. The only thing standing between "AT28C lock" and "arbitrary JEDEC-ish command injection into an unknown chip" is chip identity — see Pitfall 3, where that turns out to be nothing.

**How to avoid:**
- **Scope the lock/unlock operation to `handle->protocol == 0x0D` in firmware, with a fail-closed default**, exactly as the v1.20 dispatch work established (`protocol` unrecognised → `configure_not_implemented()` / `0xBB`, zero hardware side effects). A lock command arriving with any other protocol must reach that terminal arm, not a generic byte-flipper.
- **Never expose a raw "send byte-flip sequence" primitive on the wire.** `dev reg` already exists for register pokes; a generic sequence sender would be a chip-agnostic footgun.
- **Guard the constant, not just the call site.** Add a native test that asserts the last byte of the unlock table is `0x20` and the last byte of the erase table is `0x10`, and that the two tables are not the same object. This is cheap and it is the only defence against the one-nibble typo that no golden trace currently sees (Pitfall 5).
- **Do not implement an AT28C erase.** `configure_eeprom28c` deliberately has no `CMD_ERASE` case. Wiring one would need 12V on `OE` — the exact T-93-CANERASE hazard class v1.17 shipped a fix for (12V asserted on a 5V part). Record "AT28C software chip-erase: out of scope, requires `OE = V_H`, hazard-class T-93" as an explicit anti-feature.
- **Lock must not require writing data.** Datasheet §6.11 note 2: *"Write-Protect state will be activated at end of write even if no other data is loaded."* So `lock` = the 3 loads + wait `tWC`, and **nothing else**. Implementing lock as "3 loads + a dummy byte write" both modifies user data and routes the dummy through `memory_set_data` (full address setup, honours `pulse_delay`), adding latency inside the `tBLC` window.

**Warning signs:**
- A lock/unlock code path reachable with `protocol != 0x0D`.
- Any diff that touches `FLASH_ERASE` or the `0x10`/`0x20` literals.
- A `--force` path that widens *which chips* a lock can be sent to (as opposed to relaxing an ID warning).
- Prose in the plan that says "brick" without distinguishing SDP (reversible) from boot-block/PPB (not).

**Phase to address:**
**Phase 116** classifies reversibility per family and writes the anti-feature list. **Phase 118** owns the protocol scoping + constant guards. The `0x0D`-only invariant should be re-asserted as a non-regression check in the closing phase, mirroring v1.21's SAFE-02/03 AST-scan pattern.

---

### Pitfall 3: Misidentification is the amplifier — and the identity gate you think protects you does not exist

**What goes wrong:**
The premise "D-08 orders the A9-12V chip-ID check *before* SDP-disable so a mismatch leaves the chip protected" is true of the source and false of the running system:

```
eeprom_28c.cpp:95    if (handle->chip_id > 0) { eeprom28c_check_chip_id(handle); ... }
database.py:399       if programming.get("chip_id_check"):   # emits "chip-id"
chip_database.json    all 84 algorithm-13 entries: chip_id_check=false, chip_id_value="0x00000000"
```

`handle->chip_id` is therefore **always 0** for every AT28C-class chip in the shipped DB, the gate short-circuits, and `eeprom28c_check_chip_id` — including its `mem_size < 64` underflow guard and its 12V-on-A9 read — is unreachable in production. (For contrast: 458 of 746 DB chips *do* set `chip_id_check`.) `[CODE]`

Layer on the project's own near-miss: two parts share the name "512" — **ST M27C512** (UV EPROM, 13V, id `0x203d`) vs **Winbond W27C512** (EEPROM, 12V, id `0xda08`) — and the recorded lesson was that a chip-ID mismatch is what fails safe. Here there is no ID to mismatch on.

Now consider exposing lock/unlock as a **standalone** operation. A standalone op that skips `write_init` skips the (already-dead) gate *and* skips the blank check, so the sole remaining identity signal is "the user typed a chip name". A user with an SST39SF040 in the socket who types `firestarter lock AT28C256` gets a raw JEDEC-prefixed command sequence delivered to a different command set.

**Why it happens:**
The DB's `chip_id_check` is inherited from minipro's `infoic.xml` decode and nobody re-checked it when the A9-12V helper was added in Phase 01. The helper's own comment documents its intent ("SAF-05 … D-08 fail-fast on identity") which reads, to a later planner, as an active guarantee. Documented intent outliving its enabling condition is exactly the failure mode this milestone's own promoting note demonstrates (Pitfall 9).

**How to avoid:**
- **Phase 116 must state the gate's real status in writing** and then decide, explicitly, between: (a) populate `chip_id_check`/`chip_id_value` for the AT28C parts that actually implement the A9-12V device-identification window (the AT28C256 datasheet documents *"an extra 64 bytes… by raising A9 to 12V ± 0.5V and using address locations 7FC0H to 7FFFH"* — note this is **user-writable identification space, not a factory signature**, so there may be no canonical value to compare against); or (b) accept that identity is unverifiable for this class and design the safety story without it. **Option (b) is the honest default** and the milestone should say so rather than quietly relying on (a) working out. Do not plan any phase whose safety argument depends on the gate firing until this decision is recorded.
- **Do not expose a bare `lock` / `unlock` top-level command.** Put them behind the existing `dev`-style surface or make them subordinate to a chip-resolved operation so they inherit `chip_resolver.resolve_chip` (the support-status guard the whole codebase already routes through, and which v1.21 SAFE-01 made a CI-enforced invariant). Every prior milestone that added an operation kept `resolve_chip` on the path; breaking that for lock/unlock would be a first, and the wrong first.
- **`--force` semantics, concretely:** `--force` maps to `FLAG_FORCE (0x01)`, which in this codebase means exactly one thing — *downgrade an ID mismatch from ERROR to WARNING* (`eeprom_28c.cpp:86`, `flash_utils.cpp:98`, plus a firmware over-voltage relaxation at `primitives.cpp:121`). Keep it to that. `--force` must **not**: bypass `resolve_chip`, widen the protocol scope, skip a destructive confirmation, or enable lock on a chip whose `support_status` refuses it. For a *lock* specifically, prefer refusing outright over warning: the v1.16 Phase 89 CR-01 regression was precisely an ERROR→WARNING severity slip that the golden traces missed, and lock is the one operation where the warning branch has a hardware consequence.
- **Sequence the destructive-gate work before the operation exists.** v1.21 Phase 109 established the pattern that pays off: `derive_plan(destructive=False)` *structurally omits* destructive steps from `Plan.steps` rather than skipping them at execution time. Apply the same construction — a locked operation should be absent from the executable set, not present-and-guarded.

**Warning signs:**
- A plan sentence containing "the chip-ID check protects this" without a cited non-zero `chip_id_value`.
- A `lock`/`unlock` code path that never calls `resolve_chip`.
- `--force` appearing in the same function as a new destructive capability (v1.21 Phase 112-03's scoped AST scan for `--force` on `dev test` is the ready-made detector; extend its target list rather than writing a new one).
- A native test for lock/unlock whose handle sets `chip_id = 0` (i.e. reproducing production) with no sibling test at `chip_id != 0` — the mismatch-case gap that v1.16 Phase 89 CR-01 taught this project to look for.

**Phase to address:**
**Phase 116** (record gate status + the identity decision). The phase that exposes the CLI surface owns `resolve_chip` inheritance, `--force` narrowing, and the destructiveness gate; the closing phase re-asserts them as non-regression checks.

---

### Pitfall 4: Timing — the milestone's headline feature (observability) is the most likely way to break the feature it observes

**What goes wrong:**
Every load of an SDP command sequence must occur within `tBLC` of the previous one — the same constraint as a page write. Numbers: **150 µs max on Atmel; 100 µs max on Xicor and ON Semi/Catalyst** parts, with Xicor forgiving to ~200 µs while **Atmel simply refuses to unlock** when the window is exceeded `[WEB, MEDIUM — TommyPROM 28C256 notes]`. The `0x0D` DB class contains Xicor `X28C256`/`X28C64`, Catalyst `CAT28C256`/`CAT28C64`, Hitachi `HN58C256` and more — so **the design budget is 100 µs, not 150 µs.**

The specific ways v1.22 can blow it:

1. **Logging or serial I/O inside or between the loads.** This is the trap the milestone walks straight into: the goal is "make today's silent auto-unlock *observable*". At 250000 baud one byte is ~40 µs; a COBS-framed `LOG_INFO_ID` message of 8–16 bytes is **320–640 µs** — 3–6× the entire Xicor budget. A single `LOG_*` between load 3 and load 4 silently converts unlock into no-unlock, whereupon (see Pitfall 1) the current proxy reports *success*. **Emit observability before the sequence starts and after it completes — never inside.**
2. **Interrupt latency.** The sequence runs with interrupts enabled. On the Leonardo the USB CDC ISR can take tens of µs; the COBS RX path adds more. `flash_util_byte_flipping` is only ~6 register writes plus pulses, so a short `noInterrupts()`/`interrupts()` bracket around the whole sequence is affordable and is the right mitigation — but it must be *measured*, not assumed, and on the Leonardo it must be short enough not to disturb the USB link (this is the board where `hw_read_voltage`'s process-global state already bit us once — see the v1.21 `dev test vpp/vpe` watchdog-race memory).
3. **`pulse_delay` confusion.** `configure_eeprom28c` sets `handle->pulse_delay = 0` *before* the `cmd` switch, and the comment at `eeprom_28c.cpp:103` records that the SDP path doesn't consult it anyway (`fu_flash_flip_data` has no delay). So `pulse_delay = 0` protects the **page-write byte loop**, not the SDP sequence. Two consequences: (a) implementing lock as "3 loads + a dummy data byte" drags the slow `memory_set_data` path (full address setup, `pulse_delay`-aware) into the timing window — don't; (b) any refactor that moves the SDP emission to a call site reached before `pulse_delay = 0` reintroduces a delay the current path is immune to.
4. **Register-write elision.** `rurp_write_to_register` returns early when the cached value is unchanged (`rurp_register_utils.h`). Consecutive loads at the same address (`0x5555 → 0x5555`, loads 3→4 of the disable sequence) therefore emit **zero** register writes. Electrically correct, but it means (i) the sequence is *faster* than a naive count suggests, and (ii) a test that counts register writes will draw the wrong conclusion (Pitfall 5).
5. **Host-side chunk boundaries.** `write_execute` flushes at `(address+1) % 64 == 0` or last byte. Uno's 512 B and Leonardo's 1024 B data buffers are both multiples of 64, so chunk boundaries coincide with page boundaries — the inter-chunk serial round-trip lands *after* a page flush, not mid-page. Any future buffer-size change (the queued Binary Command Protocol milestone explicitly targets 512 → ~1024 on the Uno) must preserve "buffer size is a multiple of the page size" or partial pages will straddle a multi-millisecond serial gap.
6. **Clock/board differences.** All three targets (Uno 16 MHz, Leonardo 16 MHz, uno328pb) share the clock, so `tBLC` headroom is not board-differentiated in the way pulse widths are — **but** interrupt load is (Leonardo USB vs Uno hardware UART), and uno328pb is already recorded as bench-unstable during reads. Treat Leonardo as the timing-worst-case for ISR jitter, not Uno.

**Why it happens:**
`tBLC` is invisible in the source — there is no constant named for it, no comment quoting 100 µs, and no test that can fail when it is exceeded. It is an unenforced physical contract, which is the category of constraint that decays under refactoring.

**How to avoid:**
- **Introduce a named constant and a comment block** (`AT28C_TBLC_MAX_US = 100`, citing the Xicor/Catalyst floor, not Atmel's 150) in firmware, and cite it at every SDP call site. Constants that exist get grepped; physics that lives in a datasheet does not.
- **Add a static/structural test that the SDP sequence body contains no logging or serial call.** v1.21 shipped two reusable AST-scan precedents (Phase 109 SAFE-02/03, Phase 112-03 scoped scan) with *planted-violation* fixtures to prove the checker isn't hollow — reuse that machinery on the C++ side via a source scan, and include a planted `LOG_` fixture so the check can fail.
- **Instrument, don't assume.** A cycle-count/`micros()` bracket around the sequence, logged *after* it completes, gives a real number on real boards for free (any chip in the socket, no AT28C needed — the timing is a property of the host code path). That is one of the few v1.22 claims that *is* provable without an AT28C. Do it.
- **Bracket with `noInterrupts()`** only after measuring; document the Leonardo USB consideration.

**Warning signs:**
- A `LOG_*`, `Serial.`, or `rurp_log_*` call anywhere between the first and last load of a sequence.
- A measured sequence duration above ~60 µs (leaving <40% margin to the 100 µs floor).
- "Works on the Uno, times out on the Leonardo" (ISR jitter) or "works on Xicor, not on Atmel" (Atmel refuses out-of-window; Xicor tolerates) — the second is a *diagnostic fingerprint* for a tBLC violation and should be written into the docs so a community reporter's data can identify it.

**Phase to address:**
**Phase 118 (firmware primitives)** owns the constant, the no-logging invariant, and the measurement. The observability/opt-out phase owns "log outside the window" as a hard success criterion — this is the coupling that makes those two phases adjacent in the spine.

---

### Pitfall 5: Validating without silicon — the harness cannot currently see the difference between lock, unlock, and erase

**What goes wrong:**
This is the most consequential *test-infrastructure* fact in the milestone:

```
test/native/avr/_shared/host_stubs_common.inc:69  // HOST_STUBS_RECORD_BUS records (reg, data) of rurp_write_to_register
test/native/avr/_shared/host_stubs_common.inc:98  extern "C" void rurp_write_data_buffer(uint8_t data) { (void)data; }   // ← the command byte, discarded
test/native/avr/_shared/host_stubs_common.inc:102 extern "C" uint8_t rurp_read_data_buffer() { return 0; }
```

`fu_flash_flip_data` puts the command byte on the bus via `rurp_write_data_buffer` and pulses CE. Neither the byte nor the pulse is recorded. All four sequences — `FLASH_ENABLE_WRITE` (`…A0`), `FLASH_ENABLE_WRITE_PROTECTION` (`…A0`, byte-identical), `EEPROM_SDP_DISABLE` (`…80…20`) and `FLASH_ERASE` (`…80…10`) — walk the same addresses. Consequently the strongest assertion the existing suite makes is `test_val_5v_page.cpp:200`: *"Look for the MSB sequence: 0x55, 0x2A, 0x55"*. **Address MSBs only.**

Proof that this is not hypothetical: abandoned commit `0052c42` swapped one table for another and its own message records *"test_val_eeprom28c/flash3/flash4 golden traces: all 22 tests PASS (zero-diff)"*.

Second harness hazard, in the one suite that *does* drive `eeprom28c_write_init`: `test_eeprom28c_chip_id.cpp` mocks `firestarter_get_data` with `mock_get_data_scripted`, which **ignores the address** and serves bytes by call order. `s_mock_bytes[2] = 0x20` "satisfies" the SDP wait. A test built this way passes identically whether the sequence used the right addresses, the wrong addresses, or no addresses at all — and it *cements* the Pitfall-1 proxy as expected behaviour.

**Why it happens:**
The stubs were built (Phase 71, v1.13) for a different question — "does this handler enable the VPP regulator?" — where recording control-register writes is exactly right. Reusing a harness past its designed discriminating power is the general form of the v1.16 Phase 89 CR-01 lesson already in this project's memory: *golden traces with a matching chip-ID missed a WARNING-vs-ERROR severity fork because no mismatch/failure-case test existed.* Same shape, new axis.

**How to avoid — the minimum bar for a v1.22 test suite that cannot pass while the sequence is wrong:**
1. **Extend the recording stub to the data bus.** Add an opt-in (`HOST_STUBS_RECORD_DATA_BUS`, mirroring the existing opt-in `HOST_STUBS_RECORD_BUS` convention) that appends `rurp_write_data_buffer` bytes and `rurp_chip_enable/disable` pulses into the **same ordered stream** as register writes. Without ordering, `(addr, data)` pairing cannot be reconstructed. This is a prerequisite, so it belongs in its own early phase — **the harness phase must precede the firmware phase.**
2. **Assert the full ordered tuple stream** — `(LSB, MSB, data, CE-pulse)` × N — as a literal expected array per sequence, for **each** of: lock, unlock, ordinary page write, and (as a negative) chip-erase-must-not-appear.
3. **Ship the mismatch/negative cases as first-class tests**, not afterthoughts: unlock-table-mutated-to-`0x10` must go RED; lock-table-swapped-for-write-prefix must go RED; a `LOG_` planted inside the sequence must go RED; `protocol != 0x0D` must reach `configure_not_implemented()`.
4. **Retire the address-blind scripted mock** for any SDP assertion; make `mock_get_data` address-keyed so a wrong-address read returns a wrong byte.
5. **Add the address-derivation test** (see Pitfall 6) across all six sizes present in the class.
6. **Add a DB-invariant host test**: every `algorithm == 13` entry's `chip_id_check` value is asserted, so the Pitfall-3 fact can never silently change under a DB regen.

**What will remain genuinely unproven — record it, do not paper over it:**

| Claim | Provable software-only? | Honest status at close |
|---|---|---|
| Byte stream matches the datasheet sequence for the target size | **Yes** (harness, once extended) | PROVEN |
| Sequence contains no logging / stays within measured host time | **Yes** (source scan + `micros()` instrumentation) | PROVEN |
| Lock/unlock is `0x0D`-scoped and fail-closed elsewhere | **Yes** (dispatch tests) | PROVEN |
| Real AT28C silicon **actually enters** the protected state | **No** | UNVERIFIED — no part on bench |
| Real AT28C silicon **actually leaves** the protected state | **No** | UNVERIFIED |
| `tBLC` is met on real silicon at 100 µs (Xicor/Catalyst floor) | **No** — host-side duration is measurable, silicon acceptance is not | PARTIAL: timing measured, acceptance UNVERIFIED |
| gh#11's partial-write symptom is gone | **No** | UNVERIFIED — needs the reporter or a community `dev test` report |

Use the project's existing vocabulary for this: the v1.16 `PROTOCOL-LEDGER` already carries no-silicon buckets as explicit `UNVERIFIED`, and v1.13/v1.15 carried `supported`-on-paper vs bench-proven as separate axes. **v1.22 must not graduate anything to a bench-proven claim, and must not let the 84-chip `supported` count change.**

**Warning signs:**
- A verification doc citing "golden traces byte-identical" as evidence for an SDP change (the traces are blind to it).
- A new test that is green on first write with no RED state ever observed (v1.21's discipline: RED→GREEN reproduced, planted-violation fixtures mandatory).
- Any phase success criterion phrased as "SDP lock works" rather than "the emitted byte stream equals the datasheet sequence".

**Phase to address:**
**Phase 117 (harness capability upgrade), immediately after the ground-truth phase and strictly before any firmware behaviour change.** The honesty ledger belongs to the closing phase.

---

### Pitfall 6: Hardcoded SDP command addresses that only work by accident

**What goes wrong:**
`EEPROM_SDP_DISABLE` hardcodes `0x5555` / `0x2AAA`. Two independent problems:

1. **The addresses are part-size dependent.** `[WEB, MEDIUM — cross-checked against Microchip DS20006432 (AT28C64B) and DS20006386 (AT28C256)]` AT28C256 (A14–A0) uses `5555h`/`2AAAh`; **AT28C64B (A12–A0) uses `1555h`/`0AAAh`**. The hardcoded constants work on smaller parts *only* because `0x5555 & 0x1FFF == 0x1555` and `0x2AAA & 0x1FFF == 0x0AAA` — i.e. by the missing upper address lines truncating the value. Benign for the 8K/2K/512B parts (those pins don't exist on the package), but it is accidental correctness, undocumented, and it does **not** extend upward.
2. **The byte-flip path physically cannot address above A15.** `fu_flash_fast_address` writes **only** `LEAST_SIGNIFICANT_BYTE` and `MOST_SIGNIFICANT_BYTE` (`flash_utils.cpp:62-67`). A16/A17/A18 live in the control register (`CTRL_ADDRESS_LINE_16/17/18`) and are **never touched** by the sequence — they retain whatever the previous operation left. The `0x0D` class contains **18 chips at 64 KB–512 KB** (`CAT28C512`, `AT28C010/LV010/MC010`, `M28010`, `X28C010`, `WE128K8/256K8/512K8`, `CAT28C020/040`, `AT28MC020`, `AT28C040`…). For those the sequence's effective address is `<stale A16..A18> | 0x5555`, and the datasheet addresses for the 1 M/2 M/4 M parts have not been verified at all.

Note the local inconsistency that makes this obviously fixable: **the sibling function in the same file already derives its addresses from capacity** — `eeprom28c_check_chip_id` computes `mfr_addr = handle->mem_size - 64` with an explicit comment about `0x7FC0` vs `0x1FC0`. The SDP path just never got the same treatment.

**Why it happens:**
The table was written in the v1.0-era Phase 06-01 (`34cefac`) against a single part (AT28C256), and the `0x0D` bucket subsequently *grew* from 9 chips to 84 through the v1.11 decode work and the v1.14/v1.16 reclassifications. Nothing re-examined the constant when the class widened by 9×.

**How to avoid:**
- **Derive the SDP command addresses from `handle->mem_size`**, mirroring `eeprom28c_check_chip_id`'s style and comment, with the derivation documented per size band.
- **Verify the derived addresses against a datasheet for each of the six distinct sizes** in the class (512 B, 2 KB, 8 KB, 32 KB, 64/128 KB, 256/512 KB) during the ground-truth phase. Where no datasheet is obtainable, say so and **fail closed** for that size band rather than guessing — the project's `support_status` taxonomy (`protocol-not-implemented`, `adapter-required`, `vpp-exceeds-max`) already has room for an honest refusal, and v1.20's Phase 106 fail-closed-before-any-serial-byte guard is the template.
- **Decide explicitly what to do about A16–A18.** Either extend the byte-flip path to set the upper address bits (a real firmware change with its own golden-trace implications) or **restrict lock/unlock to ≤32 KB parts** and refuse the 18 larger ones with a named reason. Silently emitting a command at a stale-upper-bit address is the one option that must not ship.
- Add a native test iterating the six size bands and asserting the emitted address stream per band.

**Warning signs:**
- A literal `0x5555` or `0x2AAA` anywhere in a v1.22 diff.
- An SDP change whose tests only exercise `mem_size = 32768` (which is what every existing 0x0D test uses).
- Community reports of "unlock does nothing" clustering on 8 KB or ≥128 KB parts.

**Phase to address:**
**Phase 116** (build the per-size address table + the ≤32 KB-or-refuse decision). **Phase 118** (implement the derivation). The size-band test belongs to the harness phase's expected-stream fixtures.

---

### Pitfall 7: Backward compatibility — today's silent auto-unlock is load-bearing, and the obvious "fix" is a silent auto-**lock**

**What goes wrong:**
Three ways to get this wrong, in increasing subtlety:

1. **Making unlock opt-in breaks every current user's `firestarter write`.** The unconditional SDP-disable in `write_init` is what makes AT28C writes work at all today (shipped in `3.0.0b11`). Users script `firestarter write image.bin -e AT28C256`; a flag they must now pass silently turns those scripts into failures on locked parts. **Default behaviour must not change** — expose an opt-**out** (`--no-sdp-unlock` or equivalent) plus a visible log line, never an opt-in. This inverts nothing about the safety posture: unlock *reduces* protection, but it is the status quo and it is what the write requires.
2. **Copying the `flash_5v_page` precedent silently locks the user's chip.** The tempting design is the one already in-tree: `flash_5v_page_write_execute` emits `FLASH_ENABLE_WRITE` at the start of every page (`flash_5v_page.cpp:93`) — "keep protection on, prefix every page". On AT28C that is **not** protection-neutral: the datasheet's SDP *enable* algorithm **is** that same 3-load prefix, and §6.11 note 2 says *"Write-Protect state will be activated at end of write even if no other data is loaded."* Prefixing writes on an unprotected AT28C therefore **turns SDP on** as a side effect of every write. Users who then reach for another tool (or an older Firestarter) find their chip refusing writes. And because `FLASH_ENABLE_WRITE` and `FLASH_ENABLE_WRITE_PROTECTION` are byte-identical, **no reviewer and no test can see which intent a call site has** — only the constant's name.
3. **Leaving unlock silent has a real cost too.** A user whose chip was locked cannot tell whether Firestarter unlocked it, whether the chip is still locked, or (per Pitfall 1) whether the timeout they got means "unlock failed" or "your `0x5555` byte isn't `0x20`". Silence is why gh#11/gh#12 were filed as mysteries rather than as "unlock failed at step N". Observability is the actual deliverable; opt-out is a secondary nicety.

Plus one concrete interaction to fix while you are here: **v1.21's `dev test` already issues a bogus erase for AT28C parts.** `chip_test.derive_plan` sets `can_erase` from `FLAG_CAN_ERASE`, which `database.py:571-594` sets for `electrical.type ∈ {EEPROM, Flash/EEPROM}` whenever `algorithm != 5` — true for all 84 `0x0D` chips. With `--destructive` that yields a supported `OP_ERASE` step → `COMMAND_ERASE (3)` → `configure_eeprom28c` has **no `CMD_ERASE` case** → `firestarter_operation_main` stays `NULL` → `op_execute_stateful_operation` returns immediately with `response_code` still `RESPONSE_CODE_OK`. **A sweep step that does nothing and reports OK** — the exact false-green class Phase 114.1 was created to kill, sitting in the milestone's own blast radius. `[CODE]`

**Why it happens:**
`database.py`'s D-03 comment explicitly reasoned "firmware-inert on 0x0D because `configure_eeprom28c` never reads `FLAG_CAN_ERASE`" — correct about the *flag* and blind to the *host-side consumer* that v1.21 added a milestone later. Inert-flag arguments expire when a new consumer appears.

**How to avoid:**
- **Default-preserving change:** unlock stays automatic on `write`; add a log line before and after (never inside — Pitfall 4) and an opt-out flag. No user's existing command line changes meaning.
- **Never emit the SDP-enable prefix on a write path.** If per-page prefixing is ever wanted for AT28C, it must be paired with an explicit unlock afterwards and an explicit user opt-in, and it must be documented as *changing the chip's protection state*.
- **Do not merge the two byte-identical tables** (the abandoned `0052c42` dedup). Keep both names, and add a header comment stating *why* a byte-identical duplicate is deliberate: on AT28C the same silicon command means "enable SDP" and "prefix a protected write", and the semantic distinction lives only in the name. Consider renaming to make intent unmissable (`AT28C_SDP_ENABLE_OR_WRITE_PREFIX`).
- **Fix the `dev test` erase step for `0x0D`** as part of this milestone: either mark `OP_ERASE` NA for protocol 13 with a named reason (mirroring the existing `flash4 (0x05) auto-erases per page` arm) or teach firmware to reject `CMD_ERASE` on `0x0D` with a real error. Prefer **both** — host NA for a clean report, firmware fail-closed for defence in depth. Add the AT28C case to the `dev test` fixtures.
- **Document the `-b` reality for this family.** `0x0D` has no erase, so `write_init`'s blank check aborts writes to a used AT28C; users need `-b`/`--no-blank-check`. Since v1.16 Phase 92 decoupled `-b` from skip-erase this is now safe advice for `0x0D` — but it contradicts the standing project warning that `write -b` skips erase and corrupts NOR/EEPROM parts. Say explicitly in the docs that for protocol `0x0D` there is no erase to skip.

**Warning signs:**
- A diff that changes the default value of an unlock flag.
- `FLASH_ENABLE_WRITE` appearing in `eeprom_28c.cpp`.
- A `dev test` report on an AT28C showing `erase: OK`.
- Any user-visible message change to the existing `write` happy path (this is a scripted interface).

**Phase to address:**
The observability/opt-out phase owns items 1–3 and the table-naming decision. The `dev test` erase-step fix is small and self-contained — a good candidate for the same phase or a micro-phase, in the Phase-114.1 mould.

---

### Pitfall 8: Dual-repo lockstep — the four ways this project has broken lockstep before, and which apply here

**What goes wrong (each row is a real prior incident):**

| Prior incident | Applies to v1.22? | Why / how to sequence |
|---|---|---|
| **Constants drift** `constants.py` ↔ `firestarter.h` | **Yes, if** v1.22 adds a `CMD_` or `FLAG_`. `CMD_` ids 0–8 and 11–15 are taken (**9 and 10 are free**); `FLAG_` bits `0x01`–`0x80` are **all allocated**, but `handle->ctrl_flags` is `uint32_t` and the JSON path uses `extract_long`, so bits ≥ `0x100` are available on the wire. Beware the cosmetic collision: `constants.py` already has `CTRL_VPP_VPE_DROP_ENABLE = 0x100` — a *control-register* bit, a different namespace. | Decide the wire shape in one phase, land both sides in the same phase, and extend the existing constants-parity test (it is the codebase's established landing spot — see Phase 98-05 D-note) in the same commit pair. |
| **Hand-editing codegen output** `messages.h` / `messages.py` | **Yes** — new user-visible SDP messages are near-certain. Both files are **generated from `firestarter/tools/catalog/messages.toml`** with a CI drift gate. v1.20 Phase 107-02 nearly deleted `0x85`/`0xBC` from `messages.py` because they had been added to the host copy but never to canonical. | Edit `messages.toml` → regen → commit both generated files. Never touch `messages.h`/`messages.py` directly. Before regenerating, diff canonical against both copies to catch pre-existing one-sided entries. |
| **Half-landed wire contract** (v1.12/v1.20 shape) | **Yes** — a new command that firmware understands but the host doesn't emit (or vice versa) is a silent capability hole. v1.20's recorded reasoning is the guide: firmware-first is safe because `json_parser.c` silently skips unknown fields, so a host briefly emitting an unknown key is harmless, whereas a host relying on firmware behaviour that isn't there is not. | **Firmware first, host second, docs/gate third** — the v1.20 105→106→107 spine. Never plan a phase boundary that leaves the host emitting a command the shipped firmware fail-closes on. |
| **Beta merge auto-firing a spurious release** | **Yes at close.** Merging + pushing sub-repo `beta` at the v1.21 close auto-cut a stray `3.0.0b12` (firmware prerelease byte-identical to b11, app GitHub release, not on PyPI). | Decide **accept / avoid / cleanup before pushing `beta`**. To validate mid-milestone without cutting a release, use `workflow_dispatch` with an explicit `beta_version` (the Phase-115 technique). |

Two more, project-specific:

- **Branch base.** PROJECT.md states v1.21 **is** merged into `beta` in both sub-repos (1 merge commit ahead, 0 behind), so v1.22 forks off `beta` per standing policy — reversing the v1.15/v1.21 fork-off-the-previous-version exception. **Verify this with `git` at execute time anyway.** The v1.12 base collision and the v1.15/v1.21 exceptions all began as a confident assumption about what was on `beta`. Also note the submodule branch must be checked out *before* dispatching executors.
- **Flash budget.** Leonardo sat at 25136 B / **87.7%** after the v1.16 recompose (which achieved a −518 B *decrease* by deduping primitives — including the SDP-table dedup this milestone must now *not* do). v1.22 adds a command arm, new message IDs, address-derivation arithmetic, and possibly a `noInterrupts()` bracket. **Measure `pio run -e leonardo` before and after and report the delta in the phase verification**, as v1.16/v1.18 did. If the budget bites, the answer is *not* to dedup `FLASH_ENABLE_WRITE_PROTECTION` (Pitfall 7).

**Warning signs:**
- A commit touching `messages.h` without `messages.toml`.
- A constants-parity test that is skipped rather than passing (the file's `FW_ABSENT` skipif pattern can hide real drift).
- CI green under devcontainer Python 3.12 while the target is 3.9/3.11 — this project has been bitten repeatedly; validate `ruff check` + `ruff format --check` against the target, and record `CI-PENDING/structurally-green` honestly when no 3.11 binary is available (the Phase-98 precedent) rather than claiming a PASS.
- A Leonardo build percentage that appears in no verification document.

**Phase to address:**
Wire shape and constants: the firmware phase. Codegen: whichever phase adds a message (add "messages.toml edited, both copies regenerated" to its acceptance criteria). Branch base: the setup step of the first executing phase. Beta/release: the closing phase, with the accept/avoid/cleanup decision made **before** any push.

---

### Pitfall 9: Stale premises — this milestone's own inputs are already disproven, and more of them will be

**What goes wrong:**
The promoting backlog note (999.19, and the ROADMAP `NEXT` entry) asserts protocol `0x0D` *"currently has no SDP path today."* Reading the tree disproves it: SDP-disable has shipped since the v1.0-era Phase 06-01 (`34cefac`) and is live in `3.0.0b11`. That single false premise, if planned against, would have produced a phase that re-implements existing code and a milestone that never noticed the *actual* defects (Pitfalls 1, 5, 6).

**Why it happens:**
Backlog triage reads issue text, not source. The two driving reports are **2024-vintage on app 1.0.13**, predating the entire 3.0.0 architecture — including the 64-byte page write that makes gh#11's "339 s for 32 KB" (≈10 ms/byte, i.e. byte-at-a-time) describe a code path that no longer exists.

**Every remaining premise in the inputs, with an owner:**

| Premise (from the milestone inputs) | Status after this research | Who must verify, how |
|---|---|---|
| "`0x0D` has no SDP path" | **FALSE** — unlock ships in b11 | Already corrected in PROJECT.md; keep the correction visible |
| "`FLASH_ENABLE_WRITE_PROTECTION` has zero callers and is byte-identical to `FLASH_ENABLE_WRITE`" | **TRUE** `[CODE]` — and the identity is *datasheet-correct*, not a bug | Phase 116: record *why* the duplicate is legitimate before anyone deletes it |
| "The A9-12V chip-ID gate is ordered before SDP-disable so a mismatch leaves the chip protected" | **Source-true, runtime-dead** — all 84 chips have `chip_id_check: false` | **Phase 116**, by DB query + `database.py:399` read. Blocks any safety argument that depends on it |
| "SDP state is not readable on AT28C" | **TRUE** `[DATASHEET + doc/lockable-proms.md]` | Phase 116: also record that a truthful state *probe* is inherently destructive to ≥1 byte — which is why `lock-status` is correctly out of scope |
| "The `0x5555`/`0x20` read-back is a weak proxy" | **Understated** — it is inverted (Pitfall 1) | Phase 116 truth table |
| "AT28C parts ship with SDP disabled" | Datasheet says yes `[DATASHEET]`; community reports *"new chips often ship locked"* `[WEB, LOW]` | Phase 116: design for "state unknown", never "factory-unlocked" |
| "Leonardo would have been the only board whose verify read is a valid PASS" | Consistent with the standing bench posture (v1.9 read bug elsewhere) | Moot while there is no part; keep it recorded for a future FUT bench |
| "No AT28C part in operator inventory" | Operator-confirmed at kickoff | Re-confirm at the closing phase before writing any UNVERIFIED ledger row |
| "gh#11 and gh#12 are the acceptance symptom" | They are 2024-vintage; **no requirement may depend on a community reply** | The closing phase comments both issues and asks for a `dev test` report — best-effort only, per the milestone framing |
| "`tBLC` is 150 µs" (implied by Atmel-only reading) | **100 µs** on Xicor/Catalyst parts, which are in the class `[WEB, MEDIUM]` | Phase 116/118: budget to 100 µs |

**How to avoid (generalised):**
- **Make "verify the premises" the literal first phase deliverable**, producing a written artifact. v1.22 is the second milestone in a row (after v1.21's stale "20 requirements" header) where an input document's arithmetic or claim was wrong; treat input verification as a standing phase-0 activity, not diligence.
- **Prefer code and datasheets over planning prose** when they disagree, and record the disagreement rather than silently following the code — the disagreement itself is a finding, as PROJECT.md's v1.22 section already demonstrates.
- **Date every external claim.** A 2024 report against a 2026 architecture is a hypothesis about *history*, not about current behaviour.
- **Check commit reachability, not just existence.** `0052c42` looks authoritative in the log and is *not an ancestor of `beta`* (verified: `git merge-base --is-ancestor` → false). Its dedup never landed. Any plan that assumes a refactor happened must prove ancestry.

**Warning signs:**
- A plan citing a backlog note as evidence for a code-level claim.
- A requirement whose acceptance depends on a third party replying.
- "As of the last milestone…" statements about `beta` content with no `git` output attached.

**Phase to address:**
**Phase 116**, as its primary output. Re-checked at the closing phase before the honesty ledger is written.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|---|---|---|---|
| Keep the `0x5555`/`0x20` read-back "for now" and just add logging around it | Smallest diff; observability ships fast | Ships a success signal that is *anti-correlated* with success; every future report is uninterpretable | **Never** — it is the milestone's core defect |
| Dedup `FLASH_ENABLE_WRITE_PROTECTION` into `FLASH_ENABLE_WRITE` (the abandoned `0052c42`) | ~6 bytes flash; less duplication | Destroys the only signal distinguishing "lock the chip" from "prefix a write"; invisible to every current test | **Never** — document the duplicate instead |
| Assert the SDP sequence via the existing address-MSB signature (`test_val_5v_page` style) | Zero harness work | Hollow gate: cannot distinguish lock/unlock/erase; repeats v1.12's hollow-GATE-03 debt | Only as a *supplementary* assertion alongside a full data-bus trace |
| Ship lock/unlock for all 84 chips including the 18 ≥64 KB parts without verifying A16–A18 | One code path, no size logic | Commands emitted at stale-upper-bit addresses; silent no-ops on 18 chips | **Never** — restrict-and-refuse instead, with a named reason |
| Leave the `dev test` `0x0D` erase step reporting OK | Out of milestone scope, technically | A false-green in the exact harness the community will use to report on AT28C parts | Only if explicitly FUT-tracked with a named owner; better to fix (it is ~10 lines) |
| Claim "software-validated" without a written UNVERIFIED ledger | Cleaner-looking close | Repeats the on-paper-`supported` problem v1.13/v1.15 spent two milestones unwinding | **Never** |
| Skip the Leonardo flash-delta measurement | Faster verification | Flash ceiling is a recurring constraint (87.7% at v1.16); regressions surface a milestone later | Only if the firmware diff is provably zero |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|---|---|---|
| **Firmware ↔ host wire (JSON)** | Adding a `CMD_`/`FLAG_` on one side only, or reusing an allocated id | `CMD_` 9/10 are free; `FLAG_` bits ≤`0x80` are all taken but `ctrl_flags` is `uint32_t` so ≥`0x100` is available; land both sides in one phase + extend the constants-parity test |
| **`messages.toml` codegen** | Editing `messages.h`/`messages.py` directly | Edit canonical `messages.toml`, regenerate both, commit together; diff canonical vs both copies first (the v1.20 `0x85`/`0xBC` near-miss) |
| **`chip_resolver.resolve_chip`** | A new operation that bypasses the support-status guard | Every op routes through it (v1.21 SAFE-01, CI-enforced); a standalone lock/unlock must inherit it |
| **v1.21 `dev test` sweep** | Assuming `derive_plan` is unaffected by a `0x0D` change | `0x0D` gets `FLAG_CAN_ERASE` → a supported `OP_ERASE` → firmware no-op reporting OK; fix host NA + firmware fail-closed, and add an AT28C fixture |
| **Native test host stubs** | Reusing `HOST_STUBS_RECORD_BUS` for a data-byte question | Add an opt-in data-bus recorder into the same ordered stream; the existing stub discards `rurp_write_data_buffer` |
| **`gh` / GitHub issue closeout** | Making a requirement depend on a reporter replying | Best-effort comment + re-test request; zero requirements gated on it (the milestone framing already says this — keep it) |
| **`beta` merge + push at close** | Pushing `beta` and auto-cutting an unintended `bN+1` | Choose accept/avoid/cleanup *before* pushing; `workflow_dispatch` + explicit `beta_version` for mid-milestone validation |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|---|---|---|---|
| Logging/serial inside the SDP command window | Unlock silently ineffective; "works on Xicor, not on Atmel"; unexplained `0xB2` | Emit observability strictly before/after the sequence; source-scan test with a planted `LOG_` fixture | Immediately — one 8-byte framed message at 250 kbaud is ~320 µs vs a 100 µs budget |
| Interrupt latency (Leonardo USB CDC, COBS RX) | Intermittent unlock failure, board-dependent | Measure with `micros()`; short `noInterrupts()` bracket around the sequence | Under host serial load / on the USB-CDC board |
| `pulse_delay` leaking into the sequence | Sequence slower than the immune current path | Keep the SDP emission on `fu_flash_flip_data` (no `pulse_delay`); never add a dummy data-byte write to the lock path | Any refactor moving the emission upstream of `pulse_delay = 0` |
| Buffer size not a multiple of the 64-byte page | Partial page straddles a multi-ms serial round-trip → dropped page | Assert `DATA_BUFFER_SIZE % 64 == 0` in a test | When the queued Binary Command Protocol milestone bumps the Uno buffer 512 → ~1024 |
| Page-end-only polling treated as verification | "Write successful", 63/64 bytes unverified; gh#11's exact symptom | Host-side full read-back `verify` as the real proof; document that firmware polling is a busy-wait | Whenever the polled byte's old value equals its new value (common in `0xFF`-padded images) |

## Security Mistakes

| Mistake | Risk | Prevention |
|---|---|---|
| Exposing a generic "send this byte-flip sequence" primitive on the wire | Arbitrary JEDEC command injection into any seated chip, including irreversible boot-block/PPB locks | Only fixed, named, protocol-scoped sequences cross the wire |
| Lock/unlock reachable with `protocol != 0x0D` | AT28C command bytes delivered to a W29C/SST39/Am29F/28F command set | Scope in firmware; unknown protocol → `configure_not_implemented()` / `0xBB`, zero side effects (v1.20 invariant) |
| `--force` widening scope rather than downgrading severity | Lock sent to a refused/misidentified part | `--force` == `FLAG_FORCE` == ID-mismatch ERROR→WARNING (+ the documented firmware over-voltage relaxation) and nothing else; for `lock`, prefer refuse-over-warn |
| Wiring an AT28C erase | 12V on `OE` of a 5V part — the T-93-CANERASE hazard class | Explicit anti-feature; keep `configure_eeprom28c` free of `CMD_ERASE` and make firmware reject it |
| `0x10` vs `0x20` typo in a sequence table | Full-device erase instead of unlock | Constant-guard native test on both tables' terminal byte + a negative "erase sequence must not appear" trace assertion |
| Sanitizer regression in `dev test --submit` when new fields are added | Leaking local paths/PII in community reports | Any new report field goes through the existing Phase-113 sanitizer + its tests |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---|---|---|
| Silent auto-unlock (today) | Users cannot tell whether unlock happened; mysteries get filed as gh#11/gh#12 instead of actionable reports | One clear line before and one after (never inside the window); name the step so a report can say "unlock step failed" |
| Making unlock opt-in | Every existing `firestarter write` script breaks on locked parts | Opt-**out** only; default behaviour unchanged |
| A `lock` command that appears to report protection state | Users trust an unverifiable claim | Never report SDP state; say plainly that it is not readable on this family. Any truthful probe costs ≥1 byte of user data — which is why `lock-status` is out of scope |
| Reporting `MSG_ERR_EEPROM_TIMEOUT (0xB2)` as the unlock failure | Uninterpretable: means "unlock failed" *or* "your `0x5555` byte isn't `0x20`" | Distinct, named messages for "unlock sequence emitted" vs "post-unlock data-effect proof failed" |
| No guidance that `0x0D` writes to a used chip need `-b` | Users hit blank-check aborts and reach for `--skip-erase`-style advice that doesn't apply | Document: protocol `0x0D` has no erase, so `-b` is required for a non-blank AT28C and skips nothing else |
| A `dev test` AT28C report showing `erase: OK` | Community concludes erase works; a maintainer later trusts it | Mark NA with a named reason; firmware fail-closed as backup |

## "Looks Done But Isn't" Checklist

- [ ] **SDP unlock:** often missing *any valid success signal* — verify the success condition is a **data-effect** proof on a byte whose target value **differs** from its current value, not a read-back of a command byte.
- [ ] **SDP lock:** often missing the "no data byte required" reading — verify it is the 3 loads + `tWC` wait, with **zero** array modification (datasheet §6.11 note 2).
- [ ] **Sequence tables:** often missing a guard on the terminal byte — verify a native test pins unlock to `0x20`, erase to `0x10`, and asserts the two tables are distinct objects.
- [ ] **Golden traces:** often missing the data bus entirely — verify the recorder captures `rurp_write_data_buffer` + CE pulses **in order** with register writes, and that mutating a command byte turns a test RED.
- [ ] **Command addresses:** often missing size-derivation — verify all six size bands in the class emit datasheet-correct addresses, and that the ≥64 KB A16–A18 question is answered (derive or refuse), with `0x5555`/`0x2AAA` appearing nowhere as a literal.
- [ ] **Identity:** often missing the fact that the gate is dead — verify a DB-invariant test pins `chip_id_check` for all 84 `algorithm == 13` entries, and that no safety argument depends on the gate firing.
- [ ] **Timing:** often missing enforcement — verify a named `tBLC` constant (100 µs), a source scan proving no logging inside the window (with a planted-violation fixture), and a real measured duration recorded per board.
- [ ] **Protocol scoping:** often missing the negative case — verify lock/unlock with `protocol != 0x0D` reaches `configure_not_implemented()` / `0xBB` with zero hardware side effects.
- [ ] **Backward compat:** often missing the scripted-user case — verify a default `firestarter write` command line behaves identically to `3.0.0b11`.
- [ ] **`dev test`:** often missing the cross-milestone consumer — verify the AT28C `OP_ERASE` step is NA (host) and rejected (firmware), with a fixture.
- [ ] **Lockstep:** often missing canonical codegen — verify `messages.toml` was the edited file, both copies regenerated, constants parity extended, Leonardo flash delta recorded.
- [ ] **Honesty ledger:** often missing the negative claims — verify every UNVERIFIED row from Pitfall 5's table is present, that no chip's `support_status` changed, and that the 84-chip count is unchanged.
- [ ] **Release:** often missing the CI side effect — verify the accept/avoid/cleanup decision for the `beta` push was made and recorded **before** pushing.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---|---|---|
| SDP accidentally **enabled** on a user's AT28C (write-prefix side effect) | **LOW** | Run the documented disable sequence; SDP is software-reversible on this family and survives power cycles but not the disable command. Ship the fix + a release note naming the affected versions. |
| Unlock silently ineffective due to tBLC violation | **LOW–MEDIUM** | Move logging outside the window / add the interrupt bracket; no chip damage. Detection is the hard part — hence the measured-duration requirement. |
| `0x5555` / `0x2AAA` corrupted by command bytes falling through as writes | **LOW** | Two bytes; a full-image rewrite restores them. Only visible on partial-region writes. Real cost is the lost trust in a "success" report. |
| Chip-erase issued instead of unlock (`0x10`/`0x20` typo) | **HIGH** | Data is gone; recovery = reprogram from a backup image if one exists. Probably inert on genuine Atmel parts (needs `OE = V_H`) but **unverified** across the 20+ manufacturers in the class. Prevention only. |
| Lock command sent to a misidentified irreversible part (boot-block / PPB / OTP) | **UNRECOVERABLE** | No software recovery. The v1.17 W29C040 precedent: RCA, detect proactively, document, defer the graduation, and get a different sample. Prevention is the only control. |
| Shipped a hollow trace test | **MEDIUM** | Extend the recorder, re-derive expected streams, re-bless; re-audit any claim that cited the old traces (the v1.12 hollow-GATE-03 precedent — accepted as debt then, which is why it recurs). |
| Spurious `bN+1` beta cut on the close push | **LOW** | Delete/mark the stray GitHub release; PyPI is unaffected if never uploaded. v1.21 accepted one; decide deliberately this time. |

## Pitfall-to-Phase Mapping

Roles, not a fixed phase count. Suggested spine: **116** ground truth → **117** harness → **118** firmware primitives → **119** wire/command surface → **120** host CLI + gates → **121** observability/opt-out + `dev test` + docs → **122** close/honesty ledger.

| Pitfall | Prevention Phase | Verification |
|---|---|---|
| 9 — Stale premises | **116** (ground truth) | Written artifact resolving every row of the premise table; PROJECT.md/ROADMAP corrections landed |
| 1 — False-success proxy | **116** (analysis) → **118** (removal + data-effect proof) | State-vs-observable truth table published; no `get_data(<cmd addr>) == <cmd byte>` remains in tree; a probe byte whose target equals its current value makes the proof test RED |
| 3 — Misidentification / dead ID gate | **116** (record + decide) → **120** (`resolve_chip`, `--force`, destructive gate) | DB-invariant test on all 84 `algorithm == 13` entries; AST scan shows no `--force` widening; locked ops structurally absent from the executable set (Phase-109 pattern) |
| 6 — Hardcoded SDP addresses | **116** (per-size table + ≤32 KB decision) → **118** (derivation) | Six size bands asserted; zero `0x5555`/`0x2AAA` literals; ≥64 KB parts either addressed correctly or refused with a named reason |
| 5 — Software-only false confidence | **117** (harness) | `rurp_write_data_buffer` + CE pulses recorded in order; mutating any command byte → RED; lock/unlock/write/erase streams distinguishable; planted-violation fixtures present |
| 2 — Bricking / irreversibility | **116** (classification + anti-features) → **118** (protocol scoping + constant guards) | Terminal-byte guards on both tables; `protocol != 0x0D` → `0xBB` with zero side effects; no `CMD_ERASE` arm for `0x0D` |
| 4 — Timing | **118** (constant, no-logging invariant, measurement) → **121** (log outside the window) | Named 100 µs constant; source scan RED on a planted `LOG_`; measured sequence duration recorded per board |
| 7 — Backward compatibility | **121** (observability/opt-out, table naming, `dev test` fix, docs) | Default `firestarter write` behaviour byte-identical to b11; no `FLASH_ENABLE_WRITE` in `eeprom_28c.cpp`; AT28C `erase` reports NA; both duplicate tables still present + documented |
| 8 — Dual-repo lockstep | **119** (wire) + every phase's acceptance criteria + **122** (release) | Constants parity extended; `messages.toml` is the edited file; Leonardo flash delta recorded; branch base proven with `git`; beta-push decision recorded before pushing |
| 5 (honesty half) | **122** (close) | UNVERIFIED ledger rows present; zero `support_status` changes; 84-chip count unchanged; gh#11/gh#12 commented with no requirement depending on a reply |

## Sources

**Primary, in-repo (HIGH confidence):**
- `firestarter_app/datasheets/AT28C256.pdf` — Microchip DS20006386B §3, §6, §6.1 (Operating Modes incl. Chip Erase `OE = V_H`), §6.11 (SDP Enable Algorithm + notes), §6.12 (SDP Disable Algorithm), §6.13 (Software Protected Program Cycle). Load-bearing quotes: *"the AT28C256 is shipped with SDP disabled"*; *"The data in the enable and disable command sequences is not written to the device"*; *"Write-Protect state will be activated at end of write even if no other data is loaded"*; *"any attempt to write to the device without the 3-byte command sequence will start the internal write timers. No data will be written."*; *"Each successive byte must be written within 150 µs (tBLC)"*.
- `firestarter/src/proms/eeprom_28c.cpp`, `firestarter/include/flash_utils.h`, `firestarter/src/proms/flash_utils.cpp`, `firestarter/src/proms/flash_5v_page.cpp`, `firestarter/src/proms/memory.cpp`, `firestarter/src/operation_utils.cpp`, `firestarter/include/rurp_register_utils.h`, `firestarter/include/firestarter.h`.
- `firestarter/test/native/avr/_shared/host_stubs_common.inc`, `test_val_eeprom28c/`, `test_eeprom28c_chip_id/`, `test_val_5v_page/`.
- `firestarter_app/firestarter/database.py`, `chip_test.py`, `constants.py`, `firestarter/data/chip_database.json` (84 `algorithm == 13` entries queried directly).
- `firestarter_app/doc/lockable-proms.md` §1 (Winbond W29C boot-block irreversibility), §14 (SST SDP), §15 (AT29C), §17 (Atmel AT28C16/64/256 — no readable SDP flag), §"no readable protection state" list.
- Git: `0052c42` (abandoned dedup, verified **not** an ancestor of `HEAD`/`beta`), `34cefac` (v1.0-era SDP-disable origin).

**Project failure history (HIGH — the highest-value source available):**
- `.planning/PROJECT.md` — v1.17 (W29C040 permanently locked §6.6 boot block; T-93-CANERASE 12V-on-5V fix), v1.16 (Phase 89 CR-01 severity fork missed by golden traces; Phase 90/91 `write -b` skipped-erase test-method error; Phase 92 HARD-01 decouple), v1.18 (AM27C020 fix effective-but-unreliable, 60/64 → 0/64), v1.12 (hollow GATE-03 accepted debt), v1.20 (fail-closed dispatch, FW→HOST→DOCS sequencing), v1.21 (`dev test`, PATT-01 address-derived pattern, DISP-01 no auto-graduate, Phase 114.1 absent-chip false-green).
- `.planning/STATE.md` — Accumulated Context / Deferred Items (FUT-01/03/04/05/07/08), Decisions log (Phase 109 SAFE-02/03 AST scans with planted violations, Phase 112-03 scoped `--force` scan, Phase 98-05 constants-parity landing spot, Phase 98/103 `CI-PENDING` honesty rule).
- `.planning/ROADMAP.md` §999.18 / §999.19 (the promoting backlog notes, including the disproven "no SDP path today" premise) and the 2026-07-27 triage passes.
- Session memory: `reference_write_b_skips_erase`, `reference_golden_trace_misses_severity_fork`, `reference_firmware_messages_h_is_codegen_generated`, `reference_beta_merge_push_autofires_ci_new_beta`, `reference_devcontainer_py312_masks_ci_py39`, `reference_st_m27c512_vs_winbond_w27c512`, `project_v117_w29c040_locked_bootblock`.

**External (see confidence tags in-line):**
- Microchip AT28C64B datasheet DS20006432 / 20006432A — SDP command addresses `1555h`/`0AAAh` (A12–A0), vs AT28C256's `5555h`/`2AAAh` (A14–A0). `[MEDIUM — cross-checked, two independent datasheet URLs]` — https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/AT28C64B-64-Kbit-8Kx8-Parallel-EEPROM-with-Page-Write-and-Software-Data-Protection-DS20006432.pdf
- Microchip AT28C256 datasheet (public copy, matches the in-repo PDF) — https://ww1.microchip.com/downloads/en/DeviceDoc/doc0006.pdf
- TommyPROM, *28C EEPROMs and Software Data Protection (SDP)* — `tBLC` 150 µs (Atmel) vs **100 µs (Xicor, ON Semi/Catalyst)**; Xicor forgiving to ~200 µs while Atmel refuses to unlock out-of-window; Arduino implementations fail on host speed (direct port access required); *"new chips often ship locked despite datasheets suggesting otherwise"*. `[LOW–MEDIUM — single community source, but from a directly analogous parallel-EEPROM programmer project with named tested parts: AT28C256-15PU, CAT28C256P-12, X28C256P]` — https://tomnisbet.github.io/TommyPROM/docs/28C256-notes
- Bread80, *The Ben Eater EEPROM Programmer, 28C256 and Software Data Protection* — **not retrievable** (HTTP 403). Listed for completeness; no claim in this document rests on it.

---
*Pitfalls research for: AT28C Software Data Protection lock/unlock lifecycle on Firestarter protocol `0x0D` (v1.22, phases from 116)*
*Researched: 2026-07-27*
