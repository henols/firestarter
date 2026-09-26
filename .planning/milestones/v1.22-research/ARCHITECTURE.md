# Architecture Research

**Domain:** Embedded dual-repo device-programmer (AVR C++ firmware + Python Click host CLI) — adding an AT28C Software Data Protection (SDP) lock/unlock lifecycle to protocol `0x0D` (`configure_eeprom28c`)
**Researched:** 2026-07-27
**Milestone:** v1.22, phases from 116
**Confidence:** HIGH for all code-structure findings (first-party source read; every claim carries a reproduction command). MEDIUM for AT28C datasheet *semantics* — see §Confidence & Sources.

---

## 0. Executive summary — read this first

Three findings reframe the milestone. Two of them change the build order.

**F-1 (topology, verified).** The milestone brief's `0052c42` claim is **correct, and understated**. `0052c42` exists, is dated 2026-06-26, and is reachable from *only* `v1.16-protocol-first-architecture-rebuild` — not `beta`, not the v1.21/current line. But the same is true of the **entire v1.16 Phase-89 primitives layer**: `primitives.{h,cpp}` was created in `a10871d` and, like `a296195` (the "v1.16 tip"), is an ancestor of neither `beta` nor `HEAD`. **There is no `primitives.{h,cpp}` in the tree v1.22 will branch from.** Any roadmap phase written against "the primitives layer" or "the v1.16 golden traces" is writing against code that does not exist. The real shared-code seam is `flash_utils.{h,cpp}`; the real golden-trace mechanism is the `HOST_STUBS_RECORD_BUS` recording stub (`test/native/avr/_shared/host_stubs_common.inc:54-80`), which records **only** `rurp_write_to_register` — not data bytes, not strobes.

**F-2 (the load-bearing defect, machine-verified).** The shipped `0x0D` SDP-disable sequence is **almost certainly a no-op or a partial corrupting write on every one of the four `0x0D` pinouts**, and its success check reads a different physical address than it wrote. `flash_util_byte_flipping` (`flash_utils.cpp:21-28`) drives `/WE` via `set_control_register(CTRL_READ_WRITE, 0)` — control-register bit 6 ≡ address bit **22**. That is correct for `DIP32_SST39SF040` (`rw-pin: 22`), the pinout every bench-proven `0x05`/`0x06` flash chip uses. Every `0x0D` pinout has a **different** `rw-pin`: 11, 14, 14, 20. And `fu_flash_fast_address` (`flash_utils.cpp:62-67`) writes only the LSB/MSB registers, bypassing `mem_util_remap_address_bus` entirely — so for `rw-pin` 11 and 14 the `/WE` bit is *inside the raw magic-address value* and toggles with the address, and for `rw-pin` 20 it is in the untouched top-address register. Details and the exact per-pinout numbers in §3. Consequence: **you cannot build a lock path on this seam. The fix must precede the feature.**

**F-3 (data modelling, machine-verified).** Protocol-`0x0D` membership is **provably insufficient** as an SDP-capability predicate. The 84-chip `0x0D` bucket contains two **FRAM** parts (`CYPRESS FM28V020`, `FUJITSU MB85R256H` — no SDP, no write cycle) and ~19 pre-SDP `2804`/`2816`/`2817`-class parts (SDP post-dates them), plus the XICOR `X28C` family whose magic addresses differ on some variants. Firing a 6-cycle "unlock" at those parts is 6 real data writes at magic addresses. See §5.

**Recommendation on the command surface (§2):** a **hybrid** — two new `CMD_*` bytes in the free `9`/`10` slots (option a) for the standalone lock/unlock operations, **plus** two high `ctrl_flags` bits (option b) for the write-path opt-out and lock-after semantics. This does **not** introduce a second dispatch axis, because `handle->cmd` has never been one.

---

## 1. Standard Architecture — where the new capability lands

### System overview (the tree v1.22 forks from, not the v1.16 branch)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ HOST  firestarter_app/  (Python, Click)                                       │
├──────────────────────────────────────────────────────────────────────────────┤
│  cli_handlers.py         @cli.command / @dev.command  + destructive confirm   │
│      │                   (erase :583  ·  dev test :1753  ·  gate :1836-1842)  │
│      ▼                                                                        │
│  chip_resolver.resolve_chip ──► support_status refusal BEFORE any serial byte │
│      │                                                                        │
│      ▼                                                                        │
│  eprom_operations.EpromOperator                                              │
│      _setup_operation :287  ─ builds wire dict, COMMAND_NAMES[cmd] :301       │
│      _operation_context :347 ─ connect / teardown                             │
│      _run_state_machine :392 ─ INIT ▸ MAIN ▸ END + final ACK                  │
│      erase_eprom :1628 / check_eprom_blank :1658 / check_eprom_id :1695       │
│              ◄── THE SHAPE A NEW no-payload OPERATION COPIES                  │
│      │                                                                        │
│      ▼   constants.py  ◄════ LOCKSTEP ════►  firestarter.h                    │
│  serial_comm.SerialCommunicator  (COBS + CRC8, 250000 baud)                  │
└──────────────────────────────────┬───────────────────────────────────────────┘
                        JSON cmd frame │ prefix-tagged id frames
┌──────────────────────────────────▼───────────────────────────────────────────┐
│ FIRMWARE  firestarter/  (AVR C++, PlatformIO)                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│  firestarter.cpp                                                             │
│    parse_json :52      ── json_get_cmd, then TWO NESTED GUARDS:              │
│         :76  if (cmd <  CMD_READ_VPP)      → json_parse() (bus-config, …)    │
│         :79  if (cmd <  CMD_DEV_ADDRESS)   → configure_memory()   ◄── ★ HERE │
│    loop :158           ── switch(cmd) :202-252  → eprom_*() driver           │
│                           default :248 → MSG_ERR_UNKNOWN_CMD                 │
│    command_done :147   ── zeroes CONTROL/LSB/MSB, chip_disable                │
│      │                                                                        │
│      ▼                                                                        │
│  eprom_operations.cpp   eprom_erase :34 / check_chip_id :43 / blank_check :52 │
│      │                     all → op_execute_simple_operation()               │
│      ▼                     ◄── THE FIRMWARE SHAPE A NEW no-payload OP COPIES │
│  operation_utils.cpp    op_execute_simple_operation :58                      │
│                         _single_step_operation_callback :271                 │
│                         INIT=1 MAIN=3 END=5 ENDED=6 (operation_utils.h:24-27)│
│      │                                                                        │
│      ▼                                                                        │
│  memory.cpp::configure_memory :42-113   ── SOLE DISPATCH AXIS = protocol      │
│      :75  protocol == PROTO_EEPROM_PARALLEL (0x0D) → configure_eeprom28c()   │
│      :113 terminal fail-closed → configure_not_implemented() / 0xBB          │
│      │                                                                        │
│      ▼                                                                        │
│  proms/eeprom_28c.cpp                     ◄══ THE TARGET HANDLER              │
│      EEPROM_SDP_DISABLE[] :26-33          (dup of flash_utils.h:53-60)       │
│      configure_eeprom28c :35-48           switch(cmd) :39-47, NO default:    │
│      eeprom28c_check_chip_id :56-95       A9-12V identity gate (SAF-05)      │
│      eeprom28c_write_init :97-117         D-08 id-before-unlock :98-99       │
│                                           flash_execute_command(…) :109  ◄F-2│
│                                           wait_for_write(0x5555,0x20) :111◄F-2│
│      eeprom28c_write_execute :119-133     64 B page + DQ7-ish poll           │
│      eeprom28c_wait_for_write :135-155                                       │
│      │                                                                        │
│      ├──► proms/flash_utils.cpp  byte_flipping :20  fast_address :61  ◄─ F-2 │
│      └──► memory.cpp  memory_set_data :224  ── remap-aware write cycle       │
│                       mem_util_remap_address_bus :259 ── address_mask + rw   │
└──────────────────────────────────────────────────────────────────────────────┘

CODEGEN (meta-repo authoritative, all three copies md5-identical today):
  /workspaces/tools/catalog/messages.toml  ──sync_to_subrepos.sh──►
      firestarter/tools/catalog/  +  firestarter_app/tools/catalog/
          ──codegen.py──► firestarter/include/messages.h  (NEVER hand-edit)
                        + firestarter_app/firestarter/messages.py (NEVER hand-edit)
```

### Component responsibilities (existing, for the new capability)

| Component | File:line | Responsibility for SDP | Touch? |
|---|---|---|---|
| Dispatch | `memory.cpp:75-78` | routes `0x0D` → `configure_eeprom28c`; sole axis is `protocol` | **NO** — do not touch |
| Operation selector | `eeprom_28c.cpp:39-47` | `switch (handle->cmd)` picks INIT/MAIN fn-ptrs | **YES** — add cases + `default:` |
| Command admission | `firestarter.cpp:73-91` | decides which `cmd` values reach `configure_memory` | **YES** — see §2 trap T-1 |
| Loop driver | `firestarter.cpp:197-247` | `cmd` → `eprom_*()` operation driver | **YES** — add 2 cases |
| No-payload op driver | `eprom_operations.cpp:34-55` | `op_execute_simple_operation` wrapper per cmd | **YES** — 2 new drivers |
| State machine | `operation_utils.cpp:58-90,271-295` | INIT▸MAIN▸END + ack handshake | **NO** — reuse as-is |
| Command-cycle emitter (raw) | `flash_utils.cpp:21-28,52-66` | `/WE` via ctrl bit 22, raw LSB/MSB, **no remap** | **NO** — see §4 |
| Command-cycle emitter (remap-aware) | `memory.cpp:228-306` + `:259-282` | full `bus_config` remap + `WRITE_FLAG` + `/CE` pulse | **YES** — build the SDP emitter on this |
| Host wire builder | `eprom_operations.py:287-345` | `command_dict["cmd"]`, `["flags"]`; `COMMAND_NAMES[cmd]` at `:301` | **YES** |
| Host op shape | `eprom_operations.py:1628-1651` | `erase_eprom` = the canonical no-payload op | **YES** — copy |
| Host error seam | `eprom_operations.py:70-86`, `exceptions.py:37-42` | `_raise_for_error_response` → `EpromOperationError.error_code` | **YES** — reuse |
| Destructive gate | `cli_handlers.py:1833-1839` | TTY `Confirm.ask` + `-y` bypass; CLI-only, never config/env (SAFE-01) | **YES** — reuse pattern |

---

## 2. ITEM 1 — The command-surface decision

### The v1.20 invariant, stated precisely

v1.20 removed `mem_type` as a **dispatch axis**. Read `configure_memory` (`memory.cpp:42-113`): it branches **only** on `handle->protocol`. `handle->cmd` is consumed *inside* each handler (`eeprom_28c.cpp:39`, `flash_5v_page.cpp:43`) as an **operation selector**, and always has been. Adding a `case` to that inner switch is structurally identical to what **v1.13 Phase 74 already did** when it added `CMD_CHECK_CHIP_ID` to `flash_5v_page.cpp:54-57`.

**Therefore: option (a) does not create a second dispatch axis.** It extends an existing, orthogonal axis (operation) that v1.20 deliberately left in place.

### The four options, concretely

#### (a) New `CMD_*` bytes — **RECOMMENDED (primary)**

Free slots exist: `CMD_VERIFY = 6`, `CMD_DEV_ADDRESS = 7`, `CMD_DEV_REGISTER = 8`, `CMD_READ_VPP = 11` (`firestarter.h:34-51`). **Slots 9 and 10 are unused.**

| Change | File:line | Lockstep? |
|---|---|---|
| `CMD_SDP_UNLOCK 9`, `CMD_SDP_LOCK 10` | `firestarter.h:34-51` | **YES** ↔ `constants.py:56-70` |
| ⚠ Admission guard (trap T-1 below) | `firestarter.cpp:79` | no |
| 2 `case` arms → new drivers | `firestarter.cpp:197-247` | no |
| `eprom_sdp_lock/_unlock` on `op_execute_simple_operation` | `eprom_operations.{h,cpp}` | no |
| 2 `case` arms + `default:` | `eeprom_28c.cpp:39-47` | no |
| `COMMAND_SDP_UNLOCK/LOCK` + **`COMMAND_NAMES` entries** | `constants.py:56-86` | **YES** |
| `EpromOperator.sdp_unlock/sdp_lock` | `eprom_operations.py` (copy `:1628`) | no |
| Wire dict gains | nothing but `"cmd": 9\|10` — the rest of the dict (`algorithm`, `memory-size`, `bus-config`, `flags`, `chip-id`, `pin-count`) is already emitted for every memory command | — |

**Trap T-1 — the admission guard is the real work.** `firestarter.cpp:73-91`:

```c
if (handle->cmd < CMD_READ_VPP) {            // 11 — cmd 9/10 pass ✔ json_parse runs
    json_parse(...);                          // bus-config, mem_size, flags: all parsed ✔
#ifdef DEV_TOOLS
    if (handle->cmd < CMD_DEV_ADDRESS) {      // 7 — cmd 9/10 FAIL ✘
#endif
        op_execute_function(configure_memory, handle);   // ← never reached for 9/10
#ifdef DEV_TOOLS
    } else { /* logs dev flags only */ }
#endif
}
```

So `cmd = 9` today parses the full memory command but **never calls `configure_memory`** → `firestarter_operation_main` stays `NULL` (`memory.cpp:44-46`) → `MSG_ERR_UNKNOWN_CMD` at `firestarter.cpp:244`. Worse, the guard is `#ifdef DEV_TOOLS`-gated, so a **non-DEV_TOOLS build behaves differently** (the inner `if` vanishes and 9/10 *would* reach `configure_memory`). Fix: replace the ordinal comparison with an explicit predicate, e.g. `is_memory_cmd(cmd)` in `firestarter.h`, enumerating `{READ, WRITE, ERASE, BLANK_CHECK, CHECK_CHIP_ID, VERIFY, SDP_UNLOCK, SDP_LOCK}`. This removes a latent build-config divergence as a side benefit — a legitimate, small, well-bounded refactor with its own native test.

**Trap T-2 — silent-finish on the wrong protocol.** `configure_eeprom28c`'s switch has **no `default:`** (`eeprom_28c.cpp:39-47`), and neither do the other handlers. A `CMD_SDP_LOCK` aimed at, say, `0x07` reaches `configure_eprom`, matches no case, leaves `operation_main = NULL` → `op_execute_stateful_operation` returns `false` (`operation_utils.cpp:89`) → the driver reports **finished with no error**. That is the same class of bug as the `0xA4` SRAM blank-check trap fixed host-side as D-30 (`eprom_operations.py:1661-1676`). Mitigation is required in **both** places: firmware `default:` → `MSG_ERR_NOT_SUPPORTED`, **and** a host pre-wire refusal.

**Trap T-3 — do NOT renumber.** Inserting the new commands at `7`/`8` and pushing the `dev` commands up would mean a stale host's `cmd:7` ("set address") lands on new firmware as **SDP lock**. Hazardous. Use 9/10.

#### (b) New flag bits on `CMD_WRITE` — **RECOMMENDED (complementary, not a substitute)**

All eight low `ctrl_flags` bits are taken (`firestarter.h:59-68`: `0x01 … 0x80`). But `handle->ctrl_flags` is `uint32_t` (`firestarter.h:96`), `is_flag_set` is a plain mask compare (`:70-71`), and the parser uses `simple_strtoul` (`json_parser.c:471-472`) — so **`0x100`+ are available with no plumbing change**. (`ic_layout`/`dev reg` display code reads the low bits only; verify no truncation at the display sites.)

| Flag | Semantics | Serves which milestone target |
|---|---|---|
| `FLAG_SKIP_SDP_UNLOCK 0x100` | do **not** run the auto-unlock on this write | "today's auto-unlock becomes opt-out-able" |
| `FLAG_SDP_LOCK_AFTER 0x200` | re-lock at END phase after a successful write | ergonomic write→lock in one pass |

Host side: extend `build_flags()` (`eprom_operations.py:168-183`) and add `write --skip-sdp-unlock` / `--lock-after` to `cli_handlers.py:463`.

**Why (b) alone is insufficient:** the milestone explicitly requires SDP disable "invocable in its own right, not only as an invisible side effect of `write`" (PROJECT.md:42). A flag on `CMD_WRITE` cannot be invoked without a write payload — `CMD_WRITE` routes to `_process_incoming_data` (`eprom_operations.cpp:23-26,58-107`), which pulls data chunks from the host. A dataless "write" would need the host to immediately send `DONE`, which is exactly the desync shape that produced the `0xA4` regression. **Reject (b) as the sole mechanism.**

#### (c) Ride the `dev reg` low-level surface — **REJECT**

`dt_set_registers` (`dev_tools.cpp:71+`) writes raw registers from host-supplied bytes. Driving the 6-cycle sequence from the host means 6 round-trips, each `ACK` + COBS frame + serial latency. The AT28C inter-byte window (tBLC, ~150 µs per `doc/PROTOCOLS.md:87,185`) is orders of magnitude smaller than a 250 kbaud round-trip. It also bypasses `bus_config` entirely (the very defect in F-2) and is `DEV_TOOLS`-gated. Physically cannot work.

#### (d) Something else — considered and rejected

- **Overload `CMD_ERASE` with a flag.** `eprom_erase` hard-gates on `FLAG_CAN_ERASE` (`eprom_operations.cpp:36-39`) and "erase" already means auto-erase-before-write for this family. Conflating protection state with content state is exactly the kind of axis-muddling v1.20 spent a milestone undoing.
- **A `sdp` sub-key in the JSON dict rather than a `cmd`.** `json_parser.c:164-97` is a flat key→parser table; a nested mode key would be a *third* thing the firmware branches on, and would leave `cmd` meaningless. This is the option that genuinely *would* create a second axis. Reject.

### Recommendation

> **Adopt (a) + (b).** Two new `CMD_*` bytes at the free `9`/`10` slots give SDP lock and unlock first-class, standalone, no-payload operations on the proven `op_execute_simple_operation` rail. Two high `ctrl_flags` bits give the write-path opt-out and lock-after semantics that the "make today's silent auto-unlock observable and opt-out-able" target needs. `handle->protocol` remains the sole dispatch axis (`memory.cpp:42-113` untouched); `handle->cmd` remains what it has always been — the operation selector inside a protocol handler, extended exactly as v1.13 Phase 74 extended it. The one non-obvious cost is replacing the `cmd < CMD_DEV_ADDRESS` admission guard (`firestarter.cpp:79`) with an explicit `is_memory_cmd()` predicate, which also removes a latent `DEV_TOOLS`-conditional behaviour divergence.

---

## 3. F-2 in full — the emitter fidelity defect (this is the RCA)

### The mechanism

`eeprom28c_write_init` calls `flash_execute_command(EEPROM_SDP_DISABLE)` (`eeprom_28c.cpp:104`) → `flash_util_byte_flipping` (`flash_utils.cpp:21-28`):

```c
handle->firestarter_set_control_register(handle, CTRL_READ_WRITE, 0);   // /WE assert
for (i...) fu_flash_flip_data(handle, byte_flips[i].address, byte_flips[i].byte);
handle->firestarter_set_control_register(handle, CTRL_READ_WRITE, 0);
```

`fu_flash_flip_data` (`:52-59`) → `fu_flash_fast_address` (`:61-66`) writes **only** `LEAST_SIGNIFICANT_BYTE` and `MOST_SIGNIFICANT_BYTE`. It never calls `mem_util_set_address` and never calls `mem_util_remap_address_bus`. So:

1. `bus_config.address_mask` is **not applied**;
2. `bus_config.address_lines[]` reordering is **not applied**;
3. `bus_config.rw_line` is **not applied** — `/WE` is assumed to be `CTRL_READ_WRITE` (`0x40` = control bit 6 ≡ address bit **22**, per `mem_util_calculate_top_address_register`, `memory.cpp:134-148`);
4. `bus_config.static_high_mask` and `vpp_line` are **not applied**.

Assumption (3) holds for `DIP32_SST39SF040` — `rw-pin: 22` — which is the pinout of **every** bench-proven `0x05`/`0x06` chip (W29C020, W29C040, SST39SF040). Address bit 22 is above the 16-bit LSB/MSB window, so the raw magic addresses can never collide with it, and `flash_util_byte_flipping` drives it explicitly. **That is why byte-flipping works on flash.**

### The four `0x0D` pinouts (machine-computed)

Reproduce:
```bash
cd /workspaces/firestarter_app && python3 -c "
from firestarter.database import EpromDatabase
db=EpromDatabase(skip_local_override=True)
for n in ('AM28C16A','AM28C17A','AT28BV256','AT28C010','W29C020'):
    e=db.get_eprom(n); print(n, e['pin-map'], e['bus-config'])"
```

| Pinout | chips | `rw-pin` | `address_mask` | `/WE` bit for `0x5555` | for `0x2AAA` | Verdict |
|---|---|---|---|---|---|---|
| `DIP24_2816` | 19 | **11** | `0x0007FF` | `0` (assert) | **`1` (de-assert)** | cycles 2 & 5 are **not writes** |
| `DIP28_28C64` | 35 | **14** | `0x001FFF` | **`1` (de-assert)** | `0` | cycles 1,3,4,6 — incl. `0x80` **and** `0x20` — are **not writes** |
| `DIP28_28C256` | 12 | **14** | `0x00BFFF` | **`1` (de-assert)** | `0` | same as above |
| `DIP32_28C512_EEPROM` | 18 | **20** | `0x00FFFF` | bit 20 lives in the **top-address/CONTROL register**, never written by `fu_flash_fast_address` | ditto | `/WE` is left at whatever `mem_util_set_address(handle,0)` left it; `CTRL_READ_WRITE` (bit 22) is the wrong line for this pinout |
| *`DIP32_SST39SF040`* (reference, `0x05`/`0x06`) | — | **22** | — | driven explicitly, correct | correct | **works** |

`WRITE_FLAG = 0`, `READ_FLAG = 1` (`memory_utils.h:14-15`) — so `rw` bit LOW = write asserted. On `DIP28_28C64`/`DIP28_28C256` (47 of 84 chips) the decisive `0x80` and `0x20` command cycles are emitted with `/WE` **HIGH**, i.e. as reads.

### The success check is also wrong

`eeprom28c_wait_for_write(handle, 0x5555, 0x20)` (`eeprom_28c.cpp:106`, body `:135-155`) polls through `handle->firestarter_get_data` → `memory_get_data` (`memory.cpp:178`) → **full remap with `READ_FLAG`**. So the write and the read-back target different physical addresses:

| Pinout | raw address the write drove | address the poll reads | match? |
|---|---|---|---|
| `DIP24_2816` | `0x05555` | `0x00D55` | ✘ |
| `DIP28_28C64` | `0x05555` | `0x05555` | ✔ *(coincidence — `rw` bit is 1 in both)* |
| `DIP28_28C256` | `0x05555` | `0x0D555` | ✘ |
| `DIP32_28C512_EEPROM` | `0x05555` | `0x105555` | ✘ |

Independently, the *criterion* is inverted: expecting to read back `0x20` at `0x5555` succeeds precisely when the `0x20` landed **as data** — i.e. when SDP was already **off** (and one byte has just been corrupted) — and fails when SDP was **on** and the sequence was consumed as a command. On a blank/protected part this returns `false` → `MSG_ERR_EEPROM_TIMEOUT` (`0xB2`) → the write aborts in INIT. That is a plausible mechanism for the community reports.

### Why nobody caught it

`git log HEAD -- src/proms/eeprom_28c.cpp` shows the last functional change is `52dc2a2` (2026-05-12, the SAF-05 chip-ID gate); the SDP body is `34cefac` (2026-05-08) and **is** an ancestor of `beta` — so yes, it shipped in `3.0.0b11`. `doc/PROTOCOLS.md:50` records `0x0D` as bench-verified: **`no`**. There has never been an AT28C part on the bench. The existing native suite `test_val_eeprom28c` asserts only that no VPP bit is set during the *configure* phase (`test_val_eeprom28c.cpp:73-114`) and explicitly never enters `operation_init`. Nothing in the tree tests the emitted sequence.

**Roadmap consequence:** "positive proof the SDP sequences landed" (PROJECT.md:45) is not a nice-to-have polish item. It is the **RED test that must exist before any lock code is written**, and the fix it drives must land before the lock path.

---

## 4. ITEM 2 — Where the protocol-family boundary sits

### What already exists in `flash_5v_page.cpp`

`flash_5v_page_write_execute` (`:80-107`) calls `flash_execute_command(FLASH_ENABLE_WRITE)` **once per page start** (`:86-95`) — the AMD/JEDEC 3-cycle `0xAA/0x55/0xA0` prefix. That is v1.13 Phase 74's SDP handling, bench-proven on W29C020 (v1.15) on `DIP32_SST39SF040` / `rw-pin: 22`.

### Real duplication that exists

| Table | Location | Duplicate of | Note |
|---|---|---|---|
| `EEPROM_SDP_DISABLE` | `eeprom_28c.cpp:26-33` | `FLASH_DISABLE_WRITE_PROTECTION`, `flash_utils.h:53-60` | **byte-identical** — this is what `0052c42` tried to dedup |
| `FLASH_ENABLE_WRITE_PROTECTION` | `flash_utils.h:48-52` | `FLASH_ENABLE_WRITE`, `flash_utils.h:42-46` | **byte-identical — and correctly so**, see below |

`FLASH_ENABLE_WRITE_PROTECTION ≡ FLASH_ENABLE_WRITE` is **not a copy-paste bug**. Per the AT28C SDP model (`doc/PROTOCOLS.md:87,185`): the `0xAA/0x55/0xA0` 3-cycle prefix is *both* the per-page write-enable prefix on an SDP-protected part *and* the sequence that **turns SDP on** when it is currently off. The bytes coincide because the operation is the same operation. `0052c42`'s "delete dead table" framing is therefore wrong on the merits, quite apart from being unmerged.

**Pitfall P-1 (design-critical).** Because SDP-enable *is* a protected page write, it is **not** "emit 3 cycles and done". The enable latches at the end of the following write cycle, so the lock body must be `3-cycle prefix → ≥1 data byte → tWC wait`. `flash_execute_command(FLASH_ENABLE_WRITE_PROTECTION)` alone does nothing — which is likely exactly *why* it has zero callers. To keep lock non-destructive of content, the correct body is **read-modify-write-identical**: read one byte, emit the prefix, write that same byte back, poll. A roadmap that "just wires up the existing table" ships a no-op.

### Recommendation: keep it scoped to `eeprom_28c.cpp`. Do NOT promote to shared code.

Rationale:

1. **The shared implementation is the broken one.** F-2 shows `flash_util_byte_flipping` is correct only for `rw-pin: 22`. Promoting the `0x0D` sequence *into* it, or extending it to serve both, means either (a) making the raw fast path remap-aware — which changes the emitted register stream for the bench-proven `0x05`/`0x06` families, or (b) parameterising it, which adds branches inside the one function all four flash/EEPROM families share. Both put proven silicon behaviour at risk to serve an unproven family. **Wrong direction of risk.**
2. **The correct `0x0D` emitter is a different mechanism, not a variant.** It should be built on `handle->firestarter_set_data` (= `memory_set_data`, `memory.cpp:228-306`) — which already does remap + `WRITE_FLAG` + `/CE` pulse — the very function `eeprom28c_write_execute:123` already uses for page data. Timing is viable: `pulse_delay = 0` for `0x0D` (`eeprom_28c.cpp:38`), so a cycle is ~3 µs settle + register writes + `/CE` pulse, comfortably inside the ~150 µs tBLC window (this µs budget is an **assumption** — see §7 ceiling).
3. **`flash_utils.h`/`flash_utils.cpp`/`flash_5v_page.cpp`/`flash_nor_unlock.cpp` stay byte-untouched**, so the `0x05`/`0x06`/`0x10` native suites and any register trace over them are trivially non-regressed. That is the cheapest possible non-regression argument.
4. **Flash cost of not deduping is ~0 today.** The tables are `const` at namespace scope in a header → internal linkage → one private copy per including TU, **elided when unreferenced**. `FLASH_ENABLE_WRITE_PROTECTION` has zero references, so it costs zero bytes now; deleting it saves nothing. The `EEPROM_SDP_DISABLE`/`FLASH_DISABLE_WRITE_PROTECTION` dedup is worth at most ~48 B (6 × 8 B `byte_flip_t`). Measured Leonardo baseline is **88.3 % flash (25324 / 28672 B, 3348 B free)** and **78.0 % RAM (1998 / 2560 B, 562 B free)** (`pio run -e leonardo`, 2026-07-27). 48 B is not worth touching shared code for.

Concretely: add `EEPROM_SDP_ENABLE[]` next to `EEPROM_SDP_DISABLE[]` in `eeprom_28c.cpp`, so both `0x0D` protection tables are co-located with the only handler that uses them, and add a comment in `flash_utils.h:48-52` recording *why* `FLASH_ENABLE_WRITE_PROTECTION` is retained-but-unused rather than deleting it (defusing a future "dead code" cleanup from re-litigating `0052c42`).

### Golden-trace / mirror-guard implications

There is **no** v1.16 golden-trace suite in this tree (F-1). What exists:

- `HOST_STUBS_RECORD_BUS` (`test/native/avr/_shared/host_stubs_common.inc:54-80`) — an **opt-in** stub that records `(reg, data)` pairs from `rurp_write_to_register`, exposed via `clear_bus_recording/bus_recording_count/recorded_reg/recorded_data`. Cap 256 entries. **It does not record `rurp_write_data_buffer` (`:98-100`, a no-op) nor the `/CE`,`/OE` strobes** (`rurp_chip_enable` etc. are macros over `rurp_set_chip_enable`, `rurp_shield.h:99-102`).
- Consumers: the 6 `test_val_*` suites (`platformio.ini [env:native] test_filter`).

**Therefore a golden trace *can* prove an SDP sequence emits exactly the right transitions — but only after the recording stub is extended** to also capture data bytes and chip-enable/output edges. That extension must be a **second opt-in flag** (e.g. `HOST_STUBS_RECORD_FULL`) so the eight existing suites that do *not* define it stay byte-exact, exactly as `HOST_STUBS_RECORD_BUS` was introduced (`:47-53` documents that discipline). This is the single most valuable deliverable in the milestone and belongs in Phase 116.

---

## 5. ITEM 3 — How SDP capability should be modelled in data

### Recommendation: **zero DB change in v1.22.** Hand-curated, host-side, code-level capability set.

`0x0D` membership is insufficient. Reproduce:

```bash
cd /workspaces/firestarter_app && python3 -c "
import json,collections
d=json.load(open('firestarter/data/chip_database.json'))
p=[(m,c['part_number'],c['support_status'],c['pinout'],c['electrical']['type'])
   for m,cs in d.items() for c in cs if c['programming']['algorithm']==0x0D]
print(len(p)); print(collections.Counter(x[2] for x in p)); print(collections.Counter(x[3] for x in p))"
```

**84 chips · 75 `supported` + 9 `adapter-required` · 4 pinouts · `electrical.type` ∈ {EEPROM ×66, Flash/EEPROM ×18}.** Inside that bucket:

| Sub-population | Examples | SDP reality |
|---|---|---|
| **FRAM mislabelled as EEPROM** | `CYPRESS FM28V020`, `FUJITSU MB85R256H` | **No SDP at all.** No write cycle, no page buffer. 6 magic-address writes = 6 data corruptions. |
| **Pre-SDP 2804/2816/2817 class** | `AM28C16A`, `X2804A`, `X2816A/B/C`, `MICROCHIP 2804/2816/2817`, `XL2804A`, `XL2816A` (~19 parts, all `DIP24_2816`) | SDP post-dates these parts. Same corruption exposure. |
| **XICOR X28C family** | `X28C64`, `X28C256`, `X28C010` | SDP exists but magic addresses differ on some variants — needs per-family datasheet confirmation, not inference. |
| **Genuine AT28C-style SDP** | `AT28C64B`, `AT28C256`, `AT28C010`, `CAT28C*`, `HN58C256AP`, `M28C64`, `UPD28C*` | the actual target population |

`infoic.xml` cannot supply this. `.planning/notes/infoic-xml-protection-flags-research.md` is a pinned **negative** result: bits 14/15 (`MP_OFF_PROTECT_BEFORE` / `MP_PROTECT_AFTER`) do not discriminate — `W29C020C` (permanent boot-block lockout) and `W29EE011` (SDP-only, unreadable) carry **identical** flags `0x0040c078`, and the whole AMD readable-sector-protect group is all-zeros. Verdict recorded as "do not re-investigate this angle."

Why not a new DB field:

- `build_db.py` derives everything from `infoic.xml`; a field the XML cannot supply would be a hand-maintained override table inside the generator — precisely the "Rule 1/2/3 override stack" that v1.16 spent a milestone **deleting**.
- Every DB touch drags in `diff_db.py` baseline re-pinning, `check_dispatch.py`, and the regen/CI ritual (plus the py3.12-masks-CI-3.11 ruff trap) — cost with no benefit for a set of ~60 part numbers.
- `support_status` is the established capability-honesty mechanism, and its **sole write locus is human-authored `build_db.py:714`**, machine-guarded by `tools/check_no_community_support_status_write.py`. Adding a competing capability axis fragments that contract. (And SDP capability is *not* a support status: an `AT28C16` is `adapter-required` **and** SDP-capable; an `FM28V020` is `supported` **and** SDP-incapable. Orthogonal.)

Instead: a **NEW host module** (`firestarter/sdp.py`) holding a curated, datasheet-cited capability resolver — exactly the shape of the existing in-code family tables `_SRAM_PROTO_IDS` (`eprom_operations.py:1656`) and `_FLASH4_PROTOCOL_ID` (`:98`), and mirroring the D-30 pre-wire short-circuit at `:1661-1676`. Three-valued, fail-closed: `SDP_CAPABLE` / `SDP_ABSENT` / `SDP_UNKNOWN`, where `UNKNOWN` **refuses** without `--force`. One file gives the new AST gate one file to scan. Defer any DB-level protection metadata to the explicitly out-of-scope `lock-status` seed (`.planning/seeds/lock-status-command-hand-curated-protection-table.md`).

**Bonus:** this same table is what makes today's unconditional auto-unlock safe. Gating `eeprom28c_write_init`'s unlock on host-asserted capability is the *real* fix for the FRAM/pre-SDP corruption exposure — arguably a SAFE requirement, not a feature.

---

## 6. ITEM 4 — Existing seams to reuse (file + line)

| # | Seam | Location | Reuse as |
|---|---|---|---|
| S-1 | `flash_execute_command(cmd)` macro | `flash_utils.h:15-16` | **do not reuse for `0x0D`** (F-2). Keep for `0x05`/`0x06`. |
| S-2 | `flash_util_byte_flipping` | `flash_utils.cpp:21-28` | pattern only — the `set_control_register(rw,0)` → N cycles → restore shape. Reimplement remap-aware. |
| S-3 | `byte_flip_t` + table pattern | `flash_utils.h:19-22` | **reuse the type verbatim**; declare new `0x0D` tables locally in `eeprom_28c.cpp` beside `:26-33`. |
| S-4 | **`handle->firestarter_set_data`** (`memory_set_data`) | `memory.cpp:228-306` | ★ **the emitter to build on** — remap + `WRITE_FLAG` + `/CE` pulse. Already used at `eeprom_28c.cpp:123`. |
| S-5 | `mem_util_remap_address_bus` | `memory.cpp:331-354` | the address translation S-2 skips; `WRITE_FLAG=0`/`READ_FLAG=1` at `memory_utils.h:14-15`. |
| S-6 | `eeprom28c_wait_for_write` | `eeprom_28c.cpp:135-155` | polling **loop shape** reusable (2000 × 10 µs, `MSG_ERR_EEPROM_TIMEOUT` + 5 param bytes). Its `(0x5555, 0x20)` call site at `:111` must be **replaced**, not reused. |
| S-7 | `flash_util_verify_operation` (DQ7 toggle poll) | `flash_utils.cpp:30-51` | alternative poll primitive (150 ms budget, double-read confirm) — closer to the datasheet DQ7 model than S-6. |
| S-8 | `eeprom28c_check_chip_id` + **D-08 identity-before-unlock ordering** | `eeprom_28c.cpp:56-95`, ordering comment `:98-99` | ★ **reuse verbatim and preserve the ordering.** Lock/unlock must run the identity gate first so a mismatch leaves the chip in its current protection state. Note it drives 12 V on A9 (`:71-78`) — the only VPP use on `0x0D`; the `test_val_eeprom28c` 5V-only invariant must be extended to cover the new commands *in the configure phase*. |
| S-9 | `flash_util_check_chip_id_execute` | `flash_utils.cpp:97` | the `FLAG_FORCE` → WARNING vs ERROR fork. Mirror it; and heed the recorded lesson that a golden trace with a *matching* id misses this fork — plant a **mismatch** test. |
| S-10 | `op_execute_simple_operation` | `operation_utils.cpp:58-60`, `.h:74` | ★ **the no-payload operation rail.** `eprom_erase/check_chip_id/blank_check` all ride it (`eprom_operations.cpp:34-55`). |
| S-11 | `_single_step_operation_callback` | `operation_utils.cpp:279-303` | note its `cmd == CMD_BLANK_CHECK` special case for programmer-mode frame flushing — an SDP op that needs to emit an outcome frame from programmer mode faces the same Uno `com_mode` gate. |
| S-12 | v1.21 destructiveness gate | `cli_handlers.py:1833-1839` | ★ TTY `Confirm.ask` + `-y/--yes` bypass; **CLI-only flag, never config/env (SAFE-01)**. Note `dev test`'s own gate is `if destructive:` and `derive_plan(..., destructive=)` (`chip_test.py:318`) keeps omitted destructive steps on the advisory `locked_destructive` list (`:315`) with no code path to execute them — the same discipline applies to lock. |
| S-13 | `SAFE-04` absent-chip hard-fail | `cli_handlers.py:1841-1847` | pre-hardware `app.db.get_eprom(chip)` emptiness check; reuse for the new commands. |
| S-14 | `EpromOperator` no-payload method shape | `eprom_operations.py:1628-1651` (`erase_eprom`) | ★ copy: `_operation_context(...) → _run_state_machine(op_name)`; `_main_phase_simple` (`:494`) handles the MAIN wait. |
| S-15 | `_raise_for_error_response` → `EpromOperationError.error_code` | `eprom_operations.py:70-86`; `exceptions.py:37-42` | ★ typed-error seam; add the new SDP error id here (or let it fall through to the generic branch). `ProtocolNotImplementedError` (`exceptions.py:45`) is the `0xBB` subclass. |
| S-16 | D-30 pre-wire short-circuit | `eprom_operations.py:1656,1661-1676` | ★ the exact shape for the SDP-capability refusal (§5), and the precedent that a host-side refusal is the right fix for a NULL-main-op firmware trap. |
| S-17 | `_boot_block_hint_message` | `eprom_operations.py:101-165` | precedent for an id-keyed, protocol-keyed, honest **inference** hint ("this is an inference, not a confirmed detection"). Reuse the wording discipline for "SDP may still be enabled". |
| S-18 | `HOST_STUBS_RECORD_BUS` recording stub | `test/native/avr/_shared/host_stubs_common.inc:54-80` | ★ the trace oracle — **must be extended** (data bytes + strobes) behind a new opt-in flag. |
| S-19 | `test_val_eeprom28c` suite | `test/native/avr/test_val_eeprom28c/` | extend for the new commands; the `assert_no_vpp_in_recording` helper (`:73-84`) is directly reusable. |
| S-20 | Message catalog | `/workspaces/tools/catalog/messages.toml` (+ `sync_to_subrepos.sh`, `codegen.py`) | ★ **only** edit locus. Free ids: **INFO `0x44`–`0x50`, `0x5E`+ · WARN `0x86`+ · ERROR `0xBD`–`0xBF`**. ⚠ **`0xAE` is free but was deliberately retired in v1.20 — do not reuse.** All three `messages.toml` copies are md5-identical today. |
| S-21 | Anti-hollow AST-gate pattern | `tools/check_no_community_support_status_write.py`, `tools/check_devtest_orchestrator.py`, `tools/check_dispatch.py` | every gate paired with a pytest that plants a violation and proves the gate fails. |

---

## 7. ITEM 5 — Validation architecture with NO silicon: the honest ceiling

Tier 3 (HIL) is **unavailable** — no AT28C part in operator inventory (PROJECT.md:59), and `doc/PROTOCOLS.md:50` already records `0x0D` bench-verified = `no`.

### What Tier 1 (native, `pio test -e native`) CAN prove — and it is a lot

Once the recording stub is extended (§4), a golden register trace can assert, byte-exact and per-pinout:

1. **The complete emitted transition sequence** for SDP-unlock and SDP-lock: ordered `(register, value)` writes, data-buffer bytes, and `/CE`//`/OE` edges.
2. **Address fidelity** — that each emitted cycle, after `mem_util_remap_address_bus` with `WRITE_FLAG`, lands on the datasheet's `0x5555`/`0x2AAA` **within the chip's `address_mask`**, for all four `0x0D` pinouts.
3. **Strobe fidelity** — that the pinout's own `rw_line` bit is asserted LOW on **every** command cycle. This is the assertion that turns F-2 from a hypothesis into a machine-checked fact, and it is a **RED baseline** on today's code.
4. **Read-back coherence** — that the success poll reads the same physical address the sequence wrote.
5. **Lock body completeness (P-1)** — that SDP-enable emits `3-cycle prefix → ≥1 data byte → poll`, not a bare 3 cycles; and that the data byte written equals the byte previously read (non-destructive read-modify-write-identical).
6. **D-08 ordering** — that the A9-12 V identity gate runs and an ERROR short-circuits **before** any protection-state cycle is emitted.
7. **5 V-only invariant extended** — no VPP-enable control bit set for `CMD_SDP_LOCK`/`CMD_SDP_UNLOCK` in the configure phase (`test_val_eeprom28c.cpp:73-84`).
8. **Fail-closed on the wrong protocol** — an SDP command on `0x05`/`0x07`/`0x0E`/… yields `MSG_ERR_NOT_SUPPORTED`, never a silent NULL-main-op finish (trap T-2).
9. **Non-regression** — `0x05`/`0x06`/`0x07`/`0x10`/SRAM traces byte-identical (trivially, since `flash_utils.*` is untouched).
10. **Admission-guard equivalence** — `is_memory_cmd()` accepts exactly the pre-existing set plus the two new commands, identically **with and without `-D DEV_TOOLS`** (trap T-1).

### What Tier 2 (host pytest, mock operator) CAN prove

Wire-dict exactness (`cmd`, `flags`, `algorithm`, `bus-config`) · `constants.py` ↔ `firestarter.h` parity for the new `CMD_*`/`FLAG_*` (extend `tests/test_revision_constants_parity.py`) · `COMMAND_NAMES` completeness (missing entry = `KeyError` at `eprom_operations.py:301`) · destructive confirm fires and aborts **without opening a port** · SDP-capability refusal for non-`0x0D` and for `SDP_ABSENT`/`SDP_UNKNOWN` parts, **before any serial byte** · INIT/MAIN/END transcript handling of the new INFO/WARN frames · `error_code` propagation via `_raise_for_error_response`.

⚠ Harness trap (recorded, v1.21): **exit-code-only tests lie on this mock harness.** The load-bearing assertion is a `assert_not_called()` on the hardware call — assert that the refusal path never reaches the operator, not merely that exit ≠ 0.

### The ceiling — the specific claim only silicon can prove

> **That an AT28C-family die actually latches the emitted bus cycles as the SDP-disable / SDP-enable commands, and that its protection state consequently changed.**

Decomposed, the three sub-claims software cannot reach:

- **T-A (timing).** The recording stub has **no time axis**. It cannot show that a cycle's duration and the inter-cycle gap fall inside the part's tBLC (~150 µs) and outside tWC (~5–10 ms). Partial mitigation: assert the *count* of register writes per cycle and carry a computed worst-case µs budget in a test comment — an **assumption**, explicitly labelled, not a proof. This is the weakest link.
- **T-B (semantics).** That the die's SDP state machine interprets `0xAA/0x55/0x80/0xAA/0x55/0x20` as disable and `0xAA/0x55/0xA0`+data as enable. Corroborated only by `doc/PROTOCOLS.md:185-186`, which *cites* `datasheets/0x0D-EEPROM-POLL/AT28C256.pdf` — **a path that does not exist in this tree** (`datasheets/` is another v1.16-branch artifact, never merged). Confidence MEDIUM. Acquiring the AT28C256 PDF is a cheap, high-value pre-requirement.
- **T-C (capability-table accuracy).** That the curated `SDP_CAPABLE`/`SDP_ABSENT` partition of the 84-chip `0x0D` bucket (§5) is right for each family. Datasheet-verifiable per family; not silicon-verifiable without parts.

**Permitted claim at close:** *"The SDP lock and unlock sequences are emitted exactly as specified, verified byte-exact by golden register trace across all four `0x0D` pinouts, with a documented timing assumption."*
**Forbidden claim:** *"SDP lock/unlock works on an AT28C256."*
**Corollaries:** the `0x0D` PROTOCOL-LEDGER cell stays `UNVERIFIED`; **no chip graduates `support_status` on the strength of v1.22**; and `gh#11`/`gh#12` closeout must be phrased as "here is what changed and why we believe it fixes your report — please re-test and file a `dev test` report", never as a verified fix.

---

## 8. ITEM 6 — Suggested phase build order (from 116)

### Dual-repo lockstep rule for this milestone

v1.20's precedent (`v1.20-ROADMAP.md:1289`): *"firmware stops parsing `type` first (safe: `json_parser.c` silently skips unknown fields…), then the host stops emitting it — the wire contract is never left half-broken."* v1.22 is the **inverse operation** (adding, not removing), so the rule inverts to the same conclusion:

- **Firmware CAN be half-landed safely.** New firmware that understands `cmd 9/10` and `flags 0x100/0x200` is fully backward-compatible with the current host, which emits neither. Zero behaviour change until the host opts in.
- **Host CANNOT be half-landed.** A host emitting `cmd:9` to `3.0.0b11` firmware hits `MSG_ERR_UNKNOWN_CMD` (`firestarter.cpp:244`) — fail-closed, but with an unhelpful message and no capability negotiation. A host setting `flags 0x100` on old firmware is **silently ignored** (`is_flag_set` just doesn't match) → the user asked to skip the unlock and it ran anyway. That is the dangerous half-landing. **FW-first is mandatory.**
- Note there is **no minimum-firmware-version gate** for capabilities: `_validate_firmware_version` (`serial_comm.py:556-591`) only enforces `major >= 3` / `>= 2.0.0`. Consider whether the host should refuse SDP commands below a known-good FW version, or accept the `UNKNOWN_CMD` failure as sufficient.

### Proposed phases

| # | Phase | Repos | Half-landable | Depends on |
|---|---|---|---|---|
| **116** | **TRACE — SDP observability harness + RED golden trace of today's emission** · extend `host_stubs_common.inc` recording behind a new opt-in flag (data bytes + `/CE`//`/OE` edges); new `test/native/avr/test_eeprom28c_sdp/` suite pinning the exact sequence `eeprom28c_write_init` emits for each of the four `0x0D` pinouts; `platformio.ini` wiring. **ZERO production code change** — pure oracle construction. Deliverable: F-2 confirmed or refuted as a machine-checked fact. Also: acquire the AT28C256 datasheet (T-B). | FW (tests only) | yes | — |
| **117** | **FIX — remap-aware `0x0D` command emitter + honest success signal** · replace `flash_execute_command(EEPROM_SDP_DISABLE)` (`eeprom_28c.cpp:104`) with a `0x0D`-local emitter on `handle->firestarter_set_data`; replace the inverted `wait_for_write(0x5555,0x20)` (`:111`) with a coherent check; 116's traces flip RED→GREEN. `flash_utils.*` / `flash_5v_page.cpp` / `flash_nor_unlock.cpp` **untouched**. No wire change, no lockstep, host untouched. | FW only | **yes** | 116 |
| **118** | **OBSERVE — auto-unlock becomes visible + opt-out-able** (FW half of the lockstep) · new INFO/WARN ids in meta `messages.toml` → `sync_to_subrepos.sh` → `codegen.py` regen both sub-repos; `FLAG_SKIP_SDP_UNLOCK 0x100` in `firestarter.h`; firmware honours it and emits an outcome frame. Delivers the `gh#11`/`gh#12` user-visible value earliest. ⚠ `is_flag_set` on `>0x80` — audit display sites for uint8 truncation. | FW + meta catalog | **yes** | 117 |
| **119** | **LOCK — SDP-enable path + new command surface** (FW half) · `CMD_SDP_UNLOCK 9` / `CMD_SDP_LOCK 10`; replace the `cmd < CMD_DEV_ADDRESS` admission guard with `is_memory_cmd()` (T-1); `case` arms in `firestarter.cpp:197-247`; `eprom_sdp_lock/_unlock` on `op_execute_simple_operation`; `EEPROM_SDP_ENABLE[]` + read-modify-write-identical lock body (P-1); `default:` → `MSG_ERR_NOT_SUPPORTED` in the handler switches (T-2); D-08 identity-first preserved; `FLAG_SDP_LOCK_AFTER 0x200`. Carries a `pio run -e leonardo` flash-budget criterion (3348 B headroom). | FW + meta catalog | **yes** | 117, 118 |
| **120** | **HOST — CLI surface, wire emission, capability refusal, destructive gate** · `constants.py` `COMMAND_SDP_*` + **`COMMAND_NAMES` entries** + `FLAG_*`; NEW `firestarter/sdp.py` curated capability resolver (§5); `EpromOperator.sdp_lock/sdp_unlock` on the `erase_eprom` shape; CLI commands behind the S-12 destructive confirm + `-y`; `write --skip-sdp-unlock` / `--lock-after`; pre-wire refusal for non-`0x0D` and `SDP_ABSENT`/`SDP_UNKNOWN` (S-16); constants-parity test extended. **Closes the lockstep — this is the half that must not land first.** | HOST | **NO** | 119 |
| **121** | **GATE + DOCS (close)** · NEW `tools/check_sdp_capability.py` + anti-hollow planting pytest (S-21); correct `doc/PROTOCOLS.md` §1.6 (`:185-186` currently describes a sequence that does not faithfully reach silicon) and `firestarter/CLAUDE.md` command/flag tables; PROTOCOL-LEDGER `0x0D` stays `UNVERIFIED` with the §7 ceiling recorded verbatim; re-verify full native suite + `check_dispatch.py` (0 violations) + `diff_db.py` (identity — DB unchanged) + host pytest + py3.11-target CI; comment `gh#11`/`gh#12`. | both + meta | — | 120 |

### Ordering rationale (the three questions asked)

**Does firmware or host lead?** Firmware, unambiguously — see the lockstep rule above. Phases 116–119 are all firmware/meta and all individually shippable; 120 is the single host phase that closes the contract.

**Where does the golden-trace / gate work fall?** Trace work goes **first** (116), not last. It is the oracle for both the fix and the feature, it has zero production-code risk, and it is what converts F-2 from a research hypothesis into a phase-gating fact. The *policy* gate (`check_sdp_capability.py`) goes last (121), after the thing it guards exists.

**Should "make the auto-unlock observable" come before or after the lock path?** **Before** (118 before 119) — but critically, **after the fix** (117). Reasons: (i) advertising success for a sequence that doesn't reach silicon is worse than silence, so 117 must precede 118; (ii) 118 is the cheap, non-breaking half of the wire change and it builds the message-catalog + high-flag-bit plumbing that 119 reuses; (iii) 118 is what closes the community reports, so it delivers value earliest; (iv) lock is the only genuinely *new destructive capability* in the milestone and should land last, on top of proven observability.

**Risk note on 116's outcome.** If 116's trace shows F-2 is *wrong* and the current sequence is faithful, 117 collapses to "replace the inverted success check only" and the milestone gets cheaper. If 116 confirms F-2, 117 is load-bearing and the milestone's honest framing shifts from "add the lock half" to "the unlock half never worked either." Either way 116 is the correct first phase, and the roadmap should carry both branches.

---

## 9. ITEM 7 — NEW vs MODIFIED components

### Firmware — `/workspaces/firestarter/`

| Status | Path | Change |
|---|---|---|
| **MODIFIED** | `src/proms/eeprom_28c.cpp` | remap-aware SDP emitter (S-4); `EEPROM_SDP_ENABLE[]` beside `:26-33`; lock/unlock init+main bodies (read-modify-write-identical, P-1); `switch (handle->cmd)` `:39-47` gains 2 cases **+ `default:`**; replace `flash_execute_command` `:109` and `wait_for_write(0x5555,0x20)` `:111` |
| **MODIFIED** | `include/eeprom_28c.h` | export the SDP entry points only if native tests need external linkage (today it exports `configure_eeprom28c` alone) |
| **MODIFIED** | `include/firestarter.h` | `CMD_SDP_UNLOCK 9`, `CMD_SDP_LOCK 10` (`:34-51`); `FLAG_SKIP_SDP_UNLOCK 0x100`, `FLAG_SDP_LOCK_AFTER 0x200` (`:59-68`); NEW `is_memory_cmd()` predicate — **LOCKSTEP** |
| **MODIFIED** | `src/firestarter.cpp` | `:79` guard → `is_memory_cmd()` (T-1); 2 `case` arms in `:202-252` |
| **MODIFIED** | `src/eprom_operations.cpp` + `include/eprom_operations.h` | NEW `eprom_sdp_lock()` / `eprom_sdp_unlock()` on `op_execute_simple_operation` |
| **MODIFIED** | `src/proms/eprom.cpp`, `sram.cpp`, `flash_intel.cpp` | add `default:` → `MSG_ERR_NOT_SUPPORTED` to each `switch (handle->cmd)` (T-2) — minimal, or rely on the host guard + document as accepted debt |
| **MODIFIED (generated)** | `include/messages.h` | **CODEGEN — never hand-edit** (`tools/catalog/codegen.py`) |
| **MODIFIED** | `platformio.ini` | `[env:native]` `test_filter` + `-I` for the new suite |
| **MODIFIED** | `test/native/avr/_shared/host_stubs_common.inc` | extend recording (data bytes + `/CE`//`/OE`) behind a **new opt-in flag** so the 8 existing suites stay byte-exact |
| **MODIFIED** | `test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` | 5 V-only invariant extended to the two new commands |
| **MODIFIED** | `test/native/avr/test_dispatch/test_configure_memory.cpp` | new-command dispatch + fail-closed-on-wrong-protocol cases |
| **NEW** | `test/native/avr/test_eeprom28c_sdp/{test_eeprom28c_sdp.cpp,host_stubs.cpp,avr/pgmspace.h}` | the golden-trace suite (Phase 116) |
| **MODIFIED** | `firestarter/CLAUDE.md` | command list, flag list, handler notes |
| **MODIFIED** | `doc/PROTOCOLS.md` | §1.6 `:180-191` correction + honest ceiling |
| **UNCHANGED (deliberate, load-bearing)** | `include/flash_utils.h`, `src/proms/flash_utils.cpp`, `src/proms/flash_5v_page.cpp`, `src/proms/flash_nor_unlock.cpp`, `src/proms/memory.cpp` | protects bench-proven `0x05`/`0x06`/`0x10` and the single dispatch axis. Optionally add a *comment only* at `flash_utils.h:48-52` explaining why `FLASH_ENABLE_WRITE_PROTECTION` is retained-unused. |

### Meta — `/workspaces/`

| Status | Path | Change |
|---|---|---|
| **MODIFIED** | `tools/catalog/messages.toml` | **the only edit locus.** New INFO (`0x44`–`0x50`/`0x5E`+), WARN (`0x86`+), ERROR (`0xBD`–`0xBF`). **Do not reuse `0xAE`.** Then `tools/catalog/sync_to_subrepos.sh` + regen both sub-repos. |
| **MODIFIED** | `.planning/…` PROJECT/ROADMAP/MILESTONES/LEDGER | routine |

### Host — `/workspaces/firestarter_app/`

| Status | Path | Change |
|---|---|---|
| **MODIFIED** | `firestarter/constants.py` | `COMMAND_SDP_UNLOCK/LOCK` (`:56-70`) **+ `COMMAND_NAMES` entries** (`:72-86`, mandatory — `eprom_operations.py:301` `KeyError`s otherwise); `FLAG_SKIP_SDP_UNLOCK`/`FLAG_SDP_LOCK_AFTER` (`:90-99`) — **LOCKSTEP** |
| **NEW** | `firestarter/sdp.py` | curated three-valued SDP-capability resolver + datasheet citations (§5); single file for the AST gate to scan |
| **MODIFIED** | `firestarter/eprom_operations.py` | `sdp_unlock()`/`sdp_lock()` copying `erase_eprom` (`:1628-1651`); `build_flags()` (`:168-183`) new kwargs; capability pre-wire refusal in the D-30 shape (`:1661-1676`) |
| **MODIFIED** | `firestarter/cli_handlers.py` | new command(s) with the S-12 destructive confirm (`:1836-1842`) + `-y` + SAFE-04 absent-chip check (`:1844-1850`); `write` gains `--skip-sdp-unlock` / `--lock-after` (`:463`) |
| **MODIFIED (generated)** | `firestarter/messages.py` | **CODEGEN — never hand-edit** |
| **NEW** | `tools/check_sdp_capability.py` | gate: no SDP op may be routed to a non-`0x0D` or non-`SDP_CAPABLE` chip |
| **NEW** | `tests/test_check_sdp_capability_gate.py` | anti-hollow — plants a violation, proves the gate fails |
| **NEW** | `tests/test_sdp_operations.py` | wire-dict, refusal, confirm-gate, transcript, `error_code` |
| **MODIFIED** | `tests/test_revision_constants_parity.py` | new `CMD_*`/`FLAG_*` parity |
| **MODIFIED** | `README.md` / changelog | new commands + write-path flags |
| **OPTIONAL** | `firestarter/chip_test.py`, `firestarter/diagnostic_report.py` | an SDP step in `dev test`. Recommend **out of scope** for v1.22 — it would pull the v1.21 orchestrator-only + no-auto-graduate gates into a milestone that has no silicon to validate against. |
| **UNCHANGED (deliberate)** | `firestarter/data/chip_database.json`, `tools/build_db.py`, `tools/diff_db.py` baselines | §5 — **zero DB change**; `diff_db.py` must show identity at close |

---

## 10. Anti-patterns specific to this change

**AP-1 — "Just wire up `FLASH_ENABLE_WRITE_PROTECTION`."** It is byte-identical to `FLASH_ENABLE_WRITE` **because SDP-enable *is* a protected page write** (P-1). Emitting the 3 cycles alone does nothing; the enable latches on the following data byte. Instead: prefix → ≥1 data byte (the byte you just read, so content is preserved) → poll.

**AP-2 — "Reuse `flash_execute_command` — it's the shared seam."** It is correct only for `rw-pin: 22`. Every `0x0D` pinout differs (F-2). Reusing it is how the current bug happened.

**AP-3 — "Promote the SDP tables into `flash_utils`/a new primitives module to dedup."** Saves ≤48 B against 3348 B of Leonardo headroom, while putting the only bench-proven families at risk. And the primitives module does not exist in this tree (F-1). Do the dedup, if ever, in a dedicated flash-budget milestone with silicon on the bench.

**AP-4 — "Add an `sdp_capable` field to `chip_database.json`."** `infoic.xml` cannot supply it (pinned negative result); it would resurrect the override stack v1.16 deleted; and it competes with `support_status`, whose single-write-locus invariant is machine-guarded.

**AP-5 — "Renumber `CMD_DEV_ADDRESS`/`CMD_DEV_REGISTER` to make room at 7/8."** A stale host's `cmd:7` becomes SDP-lock on new firmware. Use the free 9/10 slots.

**AP-6 — "The exit code is non-zero, so the refusal works."** Recorded v1.21 lesson: exit-code-only tests lie on the mock harness. Assert `assert_not_called()` on the hardware call.

**AP-7 — "A golden trace with a matching chip-ID proves the identity gate."** Recorded v1.16 lesson: it misses the `FLAG_FORCE` WARNING-vs-ERROR fork. Plant an explicit **mismatch** case.

**AP-8 — "Declare `0x0D` verified because the traces are green."** Traces prove emission, not latching (§7 T-A/T-B). PROTOCOL-LEDGER stays `UNVERIFIED`; nothing graduates.

**AP-9 — "Hand-edit `messages.h` / `messages.py`."** Both are codegen with a CI drift gate. Edit `/workspaces/tools/catalog/messages.toml`, sync, regen — and validate `ruff check` + `ruff format --check` against **py3.11**, not the devcontainer's 3.12.

---

## 11. Scaling / budget considerations (the real constraint is flash, not users)

Measured 2026-07-27 (`cd /workspaces/firestarter && pio run -e leonardo`):

| Board | Flash | RAM | Headroom |
|---|---|---|---|
| Leonardo (ATmega32u4) | **88.3 %** — 25324 / 28672 B | **78.0 %** — 1998 / 2560 B | **3348 B flash · 562 B RAM** |

| Budget scenario | Guidance |
|---|---|
| ≤ ~500 B added | Comfortable. Expected for 117 (may be net-negative: dropping the `flash_utils` call in `eeprom_28c.cpp` sheds the 48 B table + a call site). |
| ~500–2000 B | Phase 119's most likely band (2 CMD arms + 2 op drivers + lock body + `is_memory_cmd`). Carry a `pio run -e leonardo` success criterion per firmware phase, as v1.13/v1.17 did. |
| > 2000 B | Re-scope. First lever: collapse the two commands into **one** `CMD_SDP` + a flag bit selecting lock vs unlock (frees slot 10, one op driver instead of two). Second lever: skip the `default:` arms in the non-`0x0D` handlers (AP: T-2) and rely solely on the host refusal — cheaper in flash, weaker in defence-in-depth; record as explicit accepted debt if taken. |
| RAM | Stay away from new `malloc` in the SDP path (`mem_util_blank_check` already mallocs at `memory.cpp:372`). The SDP bodies need no heap. |

---

## 12. Confidence & Sources

All findings are **first-party reads of the working tree at `firestarter@0fd7992` / `firestarter_app@v1.21` (both clean)**, plus git topology and one measured build. The `classify-confidence` seam models external providers only — `gsd-tools query classify-confidence --provider repo-read --verified` returns `LOW`, the fail-closed default for an unrecognized provider id, which is not meaningful for source reading. Tiers below are therefore stated with the reproduction command that verifies each claim, which is a stronger warrant than any provider tier.

| Claim | Confidence | Verification |
|---|---|---|
| `0052c42` is abandoned (only on `v1.16-…`, ancestor of neither `beta` nor `HEAD`) | **HIGH** | `git cat-file -t 0052c42; git merge-base --is-ancestor 0052c42 beta; git branch -a --contains 0052c42` |
| **`primitives.{h,cpp}` does not exist in this tree**; `a10871d`/`a296195` are on the v1.16 branch only | **HIGH** | `ls include/ src/proms/`; `git log --all --oneline --diff-filter=A -- '*primitives*'`; `git merge-base --is-ancestor a296195 beta` → NO |
| `datasheets/` does not exist in the meta-repo (despite `PROTOCOLS.md` citations) | **HIGH** | `ls -d /workspaces/datasheets` → ENOENT |
| SDP-disable shipped in `3.0.0b11`; `0x0D` handler functionally untouched since 2026-05-12 | **HIGH** | `git merge-base --is-ancestor 34cefac beta` → YES; `git log HEAD -- src/proms/eeprom_28c.cpp` |
| **F-2**: `rw-pin` is 11/14/14/20 for the four `0x0D` pinouts vs 22 for `DIP32_SST39SF040`; `fu_flash_fast_address` bypasses remap; write/read-back addresses diverge | **HIGH** | script in §3 + reading `flash_utils.cpp:21-67`, `memory.cpp:228-354`, `json_parser.c:401-418` |
| **F-3**: 84 `0x0D` chips incl. 2 FRAM + ~19 pre-SDP parts | **HIGH** | script in §5 |
| `CMD` slots 9/10 free; `cmd < CMD_DEV_ADDRESS` guard blocks them; `DEV_TOOLS`-conditional divergence | **HIGH** | `firestarter.h:34-51`, `firestarter.cpp:73-91,248-251` |
| Recording stub captures registers only, not data bytes or strobes | **HIGH** | `host_stubs_common.inc:54-80,98-100`; `rurp_shield.h:99-102` |
| Flash/RAM baseline 88.3 % / 78.0 % | **HIGH** | `pio run -e leonardo`, 2026-07-27 |
| Free message-id slots; `0xAE` retired in v1.20; all 3 `messages.toml` copies identical | **HIGH** | `md5sum` ×3; id-scan script over `messages.toml` |
| `infoic.xml` protection flags unusable for capability derivation | **HIGH** | `.planning/notes/infoic-xml-protection-flags-research.md` (pinned negative result, minipro `@a8efaed`) |
| **AT28C SDP command semantics** (6-cycle disable; `0xA0` prefix + data = enable; tBLC ≈150 µs; tWC 5–10 ms) | **MEDIUM** | `doc/PROTOCOLS.md:87,90,185-191` only. Its cited `datasheets/0x0D-EEPROM-POLL/AT28C256.pdf` is **absent from the tree**. → **acquire the AT28C256 PDF as a Phase-116 pre-requirement.** |
| Timing viability of a `memory_set_data`-based emitter inside tBLC | **LOW / assumption** | Not measurable by the trace harness (§7 T-A). Compute a worst-case µs budget; label as an assumption; silicon-gated. |

**Gaps for later phases:** the per-family SDP magic-address audit for the XICOR `X28C` line; whether `is_flag_set` on `>0x80` bits is truncated at any host display site; whether the host should carry a minimum-firmware-version capability gate for the new commands; and whether the `default:`-arm defence-in-depth in the non-`0x0D` handlers is worth its flash.

---
*Architecture research for: AT28C Software Data Protection lifecycle on Firestarter protocol `0x0D` (v1.22, phases 116+)*
*Researched: 2026-07-27*
