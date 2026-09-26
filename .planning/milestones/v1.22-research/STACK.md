# Stack Research — v1.22 AT28C Software Data Protection Lifecycle

**Domain:** Firmware + host lifecycle capability for AT28C-class parallel-EEPROM Software Data Protection (protocol `0x0D` / `PROTO_EEPROM_PARALLEL` / `configure_eeprom28c`)
**Researched:** 2026-07-27
**Confidence:** HIGH on datasheet ground truth and on every codebase claim (primary sources: vendor PDFs read verbatim + files read in-tree). MEDIUM on per-manufacturer timing spread. LOW on nothing that the roadmap depends on.

---

## Executive verdict

**No new technology is required. Zero new third-party dependencies on either side of the wire.** Every mechanism v1.22 needs already exists in-tree: the `byte_flip_t` table + `flash_execute_command` primitive (firmware), the `uint32_t ctrl_flags` wire field (both sides), the codegen'd message catalog, the Click `dev` group, the v1.21 destructiveness gate, and a native register-recording test harness. The "stack additions" are five small, additive integration points plus **one correctness fix that changes the shape of the whole milestone**.

**The load-bearing discovery (§3.3): the SDP-disable sequence that ships in `3.0.0b11` is electrically inert on 66 of the 84 `0x0D` chips in the database.** `PROJECT.md:53` records that unlock "already exists and runs unconditionally… therefore shipped in `3.0.0b11`". That is true of the *source*, and false of the *silicon*. The 6-write sequence is issued through `flash_util_byte_flipping`, which writes raw addresses straight to the LSB/MSB latches (`flash_utils.cpp:62-67`) and **bypasses `mem_util_remap_address_bus` entirely** (`memory.cpp:331-354`). On the two 28-pin `0x0D` pinouts the magic address `0x5555` puts a `1` on RURP bus line 14 — which those pinouts map to socket pin 27, `/WE`. Per AT28C256 datasheet Table 6-1, `WE = V_IH` is a documented **Write Inhibit**. Four of the six disable writes are to `0x5555`, so they are all inhibited. The DIP24 pinout has the inverse collision. So v1.22 does not "complete and expose" a working unlock — it must **first make unlock work at all**, and that is a *fix*, not a feature.

This reframes the milestone a third time, and it is good news: it means v1.22 has a real, provable, software-only deliverable (a native register-trace test that goes RED today and GREEN after the fix) instead of only a lock-half plus cosmetics.

---

## 1. Datasheet ground truth for the SDP command sequences

All sequences below were read **verbatim** from vendor PDFs, not recalled. The AT28C256 PDF is already in-tree at `firestarter_app/datasheets/AT28C256.pdf`; the other two were fetched from `ww1.microchip.com` / a Digi-Key Atmel mirror and are reproducible.

### 1.1 The sequences

| Part | Datasheet | Section / page | Enable | Disable |
|------|-----------|----------------|--------|---------|
| **AT28C256** (32K) | Microchip **DS20006386B**, Rev B Sept 2022 (replaces Atmel doc 0006) | §6.11 p.16 / §6.12 p.17 | `AA→5555`, `55→2AAA`, `A0→5555` | `AA→5555`, `55→2AAA`, `80→5555`, `AA→5555`, `55→2AAA`, `20→5555` |
| **AT28C64B** (8K) | Microchip **DS20006432B**, © 2020-2023 | §6.18 p.16 / §6.19 p.17 | `AA→1555`, `55→0AAA`, `A0→1555` | `AA→1555`, `55→0AAA`, `80→1555`, `AA→1555`, `55→0AAA`, `20→1555` |
| **AT28C64B** (8K, legacy) | Atmel **doc0270**, rev `0270L–PEEPR–2/09` | §19 / §20 p.10 | identical to DS20006432B | identical to DS20006432B |
| **AT28C010** (128K) | Atmel **doc0353**, rev `0353G–PEEPR–10/06` | §19 / §20 p.10 | `AA→5555`, `55→2AAA`, `A0→5555` | `AA→5555`, `55→2AAA`, `80→5555`, `AA→5555`, `55→2AAA`, `20→5555` |

Note the PDF flowchart columns interleave in text extraction; the `55→2AAA` step of the disable sequence renders out of order on AT28C256 p.17. The AT28C64B and AT28C010 extractions render in strict order and both confirm the canonical 6-step reading. Three independent documents agree on the ordering.

**The firmware's `EEPROM_SDP_DISABLE` table (`eeprom_28c.cpp:26-33`) is byte-correct for the AT28C256/AT28C010 address family.** The bug is not in the table.

### 1.2 THE LOAD-BEARING QUESTION — does enable need a following data-write cycle?

**RESOLVED: NO. `AA-55-A0` + `t_WC` is sufficient to latch SDP-enable. No data payload is required.** Confidence **HIGH** — stated three times in three documents:

> **AT28C64B DS20006432B §6.18 note 2 (p.16):** "Write-Protect state will be **activated** at end of write even if no other data is loaded."

> **Atmel doc0270 §19 note 2 (p.10):** "Write Protect state will be activated at end of write even if no other data is loaded." — and the flowchart's terminal box reads `ENTER DATA PROTECT STATE / WRITES ENABLED(2)`, referencing *exactly* note 2. The disable flowchart's terminal box reads `EXIT DATA PROTECT STATE(3)`, referencing note 3 ("…will be deactivated…"). doc0270 is the cleanest citation because its note→terminal-box mapping is unambiguous.

> **AT28C64B §6.6.2 (p.10):** "After writing the 3-byte command sequence and waiting `t_WC`, the entire AT28C64B will be protected against inadvertent writes."

The `LOAD DATA XX TO ANY ADDRESS / LOAD LAST BYTE TO LAST ADDRESS` branch in both flowcharts is the **optional data-payload path**, not a requirement. Why it exists is the key architectural insight:

> **AT28C64B §6.6.2:** "even after SDP is enabled, the user may still perform a byte or page write … by **preceding the data to be written by the same 3-byte command sequence used to enable SDP**."

So `AA-55-A0` is **dual-purpose**: with no payload it *locks*; with a payload it is the *write-while-protected prefix*. This is why `FLASH_ENABLE_WRITE` (`flash_utils.h:42-46`) and `FLASH_ENABLE_WRITE_PROTECTION` (`flash_utils.h:48-52`) are byte-identical. **They are not an accidental duplication** — they are the same three bytes with two different follow-on semantics. The abandoned v1.16 Phase 89-01 dedup commit (`0052c42`, noted as non-ancestor in `PROJECT.md:62`) would have erased a real semantic distinction. Keep both tables, or keep one and name it for the byte sequence rather than the intent.

### 1.3 Timing

| Symbol | Meaning | AT28C256 | AT28C64B | Xicor X28C256 |
|--------|---------|----------|----------|---------------|
| `t_BLC` | **Byte Load Cycle — max time between consecutive sequence bytes** | 150 µs max (Table 6-4, p.14) | 150 µs max (Table 6-4, p.14) | **100 µs max** (MEDIUM) |
| `t_WC` | Internal write cycle — wait after the last sequence byte | 10 ms max (3 ms for `-F` suffix) | 10 ms max (2 ms for `-BF`) | ~10 ms |
| `t_WP` | Write pulse width (`/WE` or `/CE` low) | 100 ns min | 100 ns min | — |
| `t_WPH` | Write pulse width high | 50 ns min | 50 ns min | — |
| `t_AH` / `t_DS` | Address hold / data setup | 50 ns min | 50 ns min | — |

> **AT28C256 §6.6.2 / p.10:** "All command sequences must conform to the page write timing specifications." — i.e. the SDP bytes are subject to `t_BLC`, exactly as page-write bytes are.

**`t_BLC` is almost certainly NOT Firestarter's problem, and that is worth stating explicitly** because it is the community's #1 reported failure mode (see §4). `fu_flash_flip_data` (`flash_utils.cpp:53-60`) contains **no `delay*()` call of any kind**: two register latches, a data-buffer write, and a `/CE` strobe. On a 16 MHz AVR with direct port access that is single-digit microseconds — an order of magnitude inside even Xicor's 100 µs. Recommend adding a native assertion that no delay is introduced into this path (a regression guard), not a timing fix.

### 1.4 The other load-bearing datasheet fact — the read-back inference is not weak, it is invalid

> **AT28C64B DS20006432B §6.6.2 (p.10):** "The data in the enable and disable command sequences **are not actually written into the device**; their addresses may still be written with user data in either a byte or page write operation."

> **AT28C256 DS20006386B p.10:** same claim, phrased "The data in the enable and disable command sequences is not written to the device…"

`eeprom_28c.cpp:106` does:

```c
if (!eeprom28c_wait_for_write(handle, 0x5555, 0x20)) { return; }
```

`eeprom28c_wait_for_write` (`eeprom_28c.cpp:135-155`) polls address `0x5555` for a **full-byte equality** against `0x20`, up to 2000 × 10 µs ≈ 20 ms. Since `0x20` is never stored at `0x5555`, this succeeds only if user data at chip address `0x5555` coincidentally equals `0x20`. On a blank (`0xFF`) part it always times out → `MSG_ERR_EEPROM_TIMEOUT` (catalog id `0xB4`, `messages.toml:494`) → `RESPONSE_CODE_ERROR` → `eeprom28c_write_init` aborts before `mem_util_blank_check` ever runs.

**Prediction the milestone can test in software:** `firestarter write` on a blank AT28C-class part fails during INIT today. This is independently consistent with the gh#11/gh#12 reports the milestone intends to close, and it means those reports may *not* be stale after all — a re-test request should be framed as "please re-test, we found a second defect" rather than "we already fixed this in b11."

The datasheet-correct completion signals, in preference order:
1. **`t_WC` wall-clock wait** — the datasheets' own instruction ("after writing the 3-byte command sequence and waiting `t_WC`"). One `delay(10)`. Cheapest, provably correct, no read at all.
2. **Toggle bit (I/O6)** — AT28C256 §6.16/§6.17 pp.19-20. Note 3 on p.20: "**Any address location may be used** but the address should not vary." This is the only in-band signal that is valid for a command sequence with no stored data.
3. **DQ7 data polling** — valid only for real array writes (there is a "last byte written"), which is what `eeprom28c_write_execute` legitimately uses. Not valid for the SDP sequence. Note `flash_util_verify_operation` (`flash_utils.cpp:30-51`) already implements a correct DQ7-only, double-read, 150 ms-bounded poll and **is not used by `0x0D` at all** — a reuse candidate for the write path, not for the SDP path.

**Recommendation:** option 1 for the SDP sequences (`delay(10)`, matching `t_WC` max) plus option 2 only if positive proof is required beyond a fixed wait. Do **not** try to salvage the `0x5555`/`0x20` read-back.

---

## 2. Whether SDP state is readable at all

**NO — there is no documented way to query SDP state on any 28C family, short of attempting a write.** Confidence **HIGH**, and the project already owns the citation.

- `firestarter_app/doc/lockable-proms.md:289-303` (§17 "Parallel EEPROM families: 28Cxxx") — Atmel AT28C16/64/256, AT28HC64/HC256, Microchip 28C64/28C256, Xicor X28C64/X28C256, Catalyst CAT28C64/256, Winbond W28Cxxx: all "Usually no explicit SDP flag". Line 303: "For example, the AT28C256 has software-controlled data protection, but the datasheet does not define a readable status bit telling you whether SDP is active."
- `lockable-proms.md:3` states the standard the project already holds itself to: readable "does **not** include merely attempting a write and seeing whether it fails."
- Independently confirmed by absence: the AT28C256 (DS20006386B) and AT28C64B (DS20006432B) operating-mode tables (§6.1 / §6.8) enumerate Read, Write, Standby/Write Inhibit, Output Disable, Chip Erase — and no status/identification mode beyond the A9-12V 64-byte device-ID array, which is user-writable general storage, not a vendor protection register.

Consequence for the milestone: **`lock` and `unlock` are write-only operations with no observable pre-state.** The honest report line is "SDP state is not readable on this family; the operation reports whether the sequence was issued and its `t_WC` completed, not whether the chip's protection state changed." Anything stronger is a lie. This is precisely why `PROJECT.md:64` puts the `lock-status` command out of scope, and that decision is **correct and should be reaffirmed, not revisited**.

The one legitimate empirical probe — write a byte, read it back, infer lock state from failure — is destructive, ambiguous (a failure could be a stuck bit, a `t_BLC` violation, or a bus fault), and belongs to `dev test`'s existing finding vocabulary if anywhere. Do not build it as a `lock-status` command.

---

## 3. Per-part variation

### 3.1 The magic addresses do NOT hold across parts

| Family | Size | Addr lines | Documented SDP addresses | Datasheet "Address format" |
|--------|------|-----------|--------------------------|----------------------------|
| AT28C64 / AT28C64B / AT28HC64 | 8K | A0–A12 | **`0x1555` / `0x0AAA`** | A12–A0 |
| AT28C256 / AT28HC256 | 32K | A0–A14 | `0x5555` / `0x2AAA` | A14–A0 |
| AT28C010 | 128K | A0–A16 | `0x5555` / `0x2AAA` | **A14–A0** (A15/A16 don't-care) |
| AT28C040 (extrapolated, same family) | 512K | A0–A18 | `0x5555` / `0x2AAA` expected | expect A14–A0 — **UNVERIFIED**, datasheet not read |
| AT28C16 / AT28C04 (24-pin) | 2K / 512 | A0–A10 / A0–A8 | **UNVERIFIED** — not read; expect `0x0555`/`0x02AA` and `0x0155`/`0x00AA` by truncation, but early AT28C16 revisions may lack SDP entirely | — |

**The good news: the truncation is self-correcting, by construction.** `0x5555` and `0x2AAA` are the alternating bit patterns `…010101` and `…101010`. Masking `0x5555` to 13 bits gives `0x1555`; masking `0x2AAA` to 13 bits gives `0x0AAA` — *exactly* the AT28C64B's documented addresses. AT28C010's "A14–A0" format note is the same phenomenon seen from the other side: the upper lines are simply don't-care. So a programmer that drives absolute `0x5555`/`0x2AAA` and leaves the unimplemented high lines unconnected lands on the correct address on every part in the 8K–512K range.

**Firestarter satisfies this precondition.** `DIP28_28C64` declares pins 1 and 26 as `nc-pin` and maps only 13 address lines (`pinouts.json`), so chip A13/A14 genuinely do not exist. Verified by executing the real host code:

```
AT28C64  pinout=DIP28_28C64  bus=[0..12]   intended 0x5555 → chip sees 0x1555 ✓
                                            intended 0x2AAA → chip sees 0x0AAA ✓
```

**Verdict on item 2: the addresses are fine. Do not add per-part SDP address tables.** That is a tempting-but-wrong addition (§7).

### 3.2 What DOES vary per part, and matters

1. **`t_BLC`:** Atmel/Microchip 150 µs, Xicor/ON-Semi **100 µs** (MEDIUM). 8 XICOR + 11 CATALYST(CSI) chips sit on `0x0D`. Firestarter's ~µs-scale sequence clears both, so this is a "do not regress" constraint rather than a change.
2. **Page size.** `eeprom_28c.cpp:19` hard-codes `#define PAGE_SIZE 64`. AT28C010's own §19 note 4 says "**1 to 128 bytes** of data are loaded" — the AT28C010 page is 128 B, and AT28C040 is 256 B. 18 of the 84 `0x0D` chips are 64K–512K parts on `DIP32_28C512_EEPROM`. A 64-byte poll on a 128-byte page mid-page is precisely the W29C040 bug that v1.17 CR-01 fixed for `0x05`. **Adjacent, real, but arguably out of v1.22's scope** — flag it for the roadmap as a candidate slice or an explicit deferral, not silence.
3. **Latent trap if you touch page size:** `constants.py:107-111` declares `JSON_KEY_PAGE_SIZE = "page-size"` with the comment "Firmware sync: json_parser.c (key_page_size)". **That comment is false.** `json_parser.c:67` `key_parsers[]` contains only `memory-size, address, flags, chip-id, pin-count, pulse-delay, vpp_mv, algorithm, read-settling-delay, read-strobe-us`; `grep -rn page_size src/ include/` in the firmware returns only `flash_5v_page.cpp`'s local heuristic. The host emits `page-size` and the firmware **silently discards it** (unknown JSON fields are skipped). Any plan that says "reuse the existing `page_size` wire field" is planning against a field that does not exist on the wire.

### 3.3 THE DEFECT — `/WE` collides with the magic address on 66 of 84 chips

`flash_util_byte_flipping` (`flash_utils.cpp:21-28`) calls `fu_flash_flip_data` → `fu_flash_fast_address` (`:61-66`), which does:

```c
uint8_t lsb = address & 0xFF;   rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, lsb);
uint8_t msb = ((address >> 8) & 0xFF); rurp_write_to_register(MOST_SIGNIFICANT_BYTE, msb);
```

Raw address → bus lines 0–15. It never calls `mem_util_remap_address_bus` (`memory.cpp:331-354`), so it applies **no** chip-pin remap, **no** `rw_line` polarity (`memory.cpp:343-345`, `WRITE_FLAG 0` / `READ_FLAG 1` per `memory_utils.h:16-17`), and **no** `static_high_mask` (`memory.cpp:352`). Bus line *n* = bit *n* of the 24-bit physical word: 0–7 in the LSB latch, 8–15 in the MSB latch, 16+ in CONTROL.

`flash_util_byte_flipping:22,26` does clear `CTRL_READ_WRITE` (`0x40` = bus line 22) — which is the correct `/WE` bit only for pinouts whose `rw-pin` resolves to line 22 (the v1.18 `DIP32_27C020` case). None of the four `0x0D` pinouts do.

Executed against the real `database.py` / `pinouts.json` (`pin_conversions` at `database.py:57-120`, `get_bus_config` at `:257-313`):

| Pinout | Chips | `rw_line` | Result |
|--------|------:|-----------|--------|
| `DIP28_28C64` | **35** | 14 (pin 27, MSB bit 6) | `0x5555` → MSB `0x55` sets line 14 → **`/WE` HIGH → all four `0x5555` writes inhibited**. Addresses otherwise correct (`0x1555`/`0x0AAA`). |
| `DIP28_28C256` | **12** | 14 (pin 27, MSB bit 6) | Same `/WE` inhibit on all four `0x5555` writes, **and** A14 is on line 15 so the chip sees `0x1555`, not `0x5555`. Two defects stacked. |
| `DIP24_2816` | **19** | 11 (pin 21, MSB bit 3) | Inverse: `0x2AAA` → MSB `0x2A` sets line 11 → **both `0x2AAA` writes inhibited**. Also drops line 13, which `pin_conversions[24][24]` documents as the DIP24 chip's **VCC** feed. |
| `DIP32_28C512_EEPROM` | 18 | 20 (pin 30, in CONTROL) | Addresses correct (`0x5555`/`0x2AAA`, identity bus map). `/WE` lives in CONTROL bit `0x10`, which `fu_flash_fast_address` never touches and `flash_util_byte_flipping` does not clear (it clears `0x40`). State is whatever the last `mem_util_set_address` left. **Unproven, works only by accident if at all.** |

Reproduction (worth keeping as the phase's RED test fixture):

```
== AT28C256  pinout=DIP28_28C256  bus=[0..13,15]  rw_line=14
   intended 0x5555 data 0xAA -> chip sees 0x1555  /WE=1  WRITE-INHIBIT
   intended 0x2AAA data 0x55 -> chip sees 0x2AAA  /WE=0  write ok
   intended 0x5555 data 0x80 -> chip sees 0x1555  /WE=1  WRITE-INHIBIT
   intended 0x5555 data 0xAA -> chip sees 0x1555  /WE=1  WRITE-INHIBIT
   intended 0x2AAA data 0x55 -> chip sees 0x2AAA  /WE=0  write ok
   intended 0x5555 data 0x20 -> chip sees 0x1555  /WE=1  WRITE-INHIBIT
```

**Every one of the 84 `0x0D` chips has at least one inhibited write in the shipped sequence.** Per AT28C64B §6.8 Table 6-1, row "Write Inhibit — X, X, V_IH", a `/WE`-high cycle is a documented no-op. The sequence cannot latch.

**The fix is a stack decision, and it is small.** `0x0D` must not use `flash_util_byte_flipping`. It needs a byte-flip that routes each command byte through the normal `handle->firestarter_set_data(handle, addr, data)` path — which already applies `mem_util_remap_address_bus` with `WRITE_FLAG`, driving `/WE` low and placing every address bit on the right pin (`memory.cpp:228-306`). `handle->pulse_delay` is already set to 0 for `0x0D` (`eeprom_28c.cpp:39-40`), so `memory_set_data`'s `delayMicroseconds(3)` + zero pulse keeps the per-byte cost around 5-10 µs — still an order of magnitude inside Xicor's 100 µs `t_BLC`. Reuse over rewrite: a small `eeprom28c_execute_command(handle, table, n)` looping `firestarter_set_data` is ~10 lines and needs no new primitive.

Caveat to verify in the fix phase: `DIP24_2816` has **no** `static-high-pins` key in `pinouts.json`, unlike `DIP24_2716` and `DIP24_2732` which both declare `[24]`. So `static_high_mask == 0` and VCC (bus line 13) is not force-driven for the 19 DIP24 EEPROMs even on the remapped path. Routing through `firestarter_set_data` fixes `/WE` and the addresses but not this; treat it as a separate, named finding.

### 3.4 X28C and W29EE — a factual correction to the research brief

The brief asks to "check X28C and W29EE families since they share the `0x0D` protocol bucket in this project's DB." Verified against `chip_database.json`:

- **X28C is present** — 8 XICOR entries on `0x0D`: `X2804A`, `X2816A`, `X2816B/C`, `X28256/X28C256`, `X2864AP`, `X28C010`, `X28C64/X28HC64`, `X28C64(NonStandard)/X28HC64(NonStandard)`. Same AA/55/A0 + 6-write shape, tighter `t_BLC`.
- **W29EE is NOT on `0x0D`.** Zero Winbond entries in the 84-chip `0x0D` set. `W29EE011`/`W29EE012` are AT29C-class page-program *flash* and live on the `0x05` (`PROTO_FLASH_5V_PAGE`) / `0x06` (`PROTO_FLASH_NOR_UNLOCK`) handlers, whose SDP is already exercised by `flash_5v_page.cpp:85-94`. **Do not pull W29EE into v1.22's scope.**

Full `0x0D` population: 84 chips, 15 manufacturers (ATMEL 20, MICROCHIP memory 14, CATALYST 11, XICOR 8, EXEL 7, ST 5, WED 4, AMD 3, NEC 3, SGS-THOMSON 3, SAMSUNG 2, CYPRESS/FUJITSU/HITACHI/MAXWELL 1 each); 75 `supported`, 9 `adapter-required`.

---

## 4. How other tools expose SDP lock/unlock

### 4.1 minipro / TL866 — the canonical precedent (HIGH; read from upstream `main.c`)

There is **no standalone lock or unlock command**. SDP is handled automatically around `write`, gated on a per-device capability bit, with two opt-out flags:

```c
/* main.c usage block */
"	-u 		Do NOT disable write-protect\n"
"	-P 		Do NOT enable write-protect\n"

/* write flow */
if (cmdopts.no_protect_off == 0 && device->opts4 & 0xc000) { minipro_protect_off(handle); }
/* ... write_page_file + verify ... */
if (cmdopts.no_protect_on  == 0 && device->opts4 & 0xc000) { minipro_protect_on(handle); }
```

Three properties Firestarter currently has **none** of:
1. **A DB capability gate** — `device->opts4 & 0xc000`. Firestarter unlocks unconditionally for all 84 chips (`eeprom_28c.cpp:104`), including parts that may not implement SDP.
2. **Automatic RE-LOCK after write.** minipro restores the chip's protected state. Firestarter leaves every part it writes permanently unlocked, silently.
3. **Explicit opt-outs**, one per direction.

### 4.2 Arduino-side programmers (MEDIUM)

TommyPROM (`tomnisbet.github.io/TommyPROM/docs/28C256-notes`), the Ben Eater programmer community, and bread80.com converge on:
- **28C parts frequently arrive from the factory with SDP already enabled**, contradicting the datasheets' "shipped with SDP disabled". So unlock-before-write is treated as effectively mandatory, and a *hard* unlock failure must not be assumed to be a bus fault.
- TommyPROM ships a **separate dedicated unlock sketch**, not a flag — precedent for a standalone unlock operation.
- The dominant reported failure is the host being **too slow** between sequence bytes (`t_BLC`), not a wrong sequence. TommyPROM measures ~80 µs/byte and notes Atmel parts hard-refuse outside spec while Xicor parts tolerate ~200 µs despite the tighter published number.

### 4.3 flashrom (LOW — negative result)

flashrom's parallel support targets LPC/FWH Firmware-Hub block-lock *registers*, a different and readable mechanism (`lockable-proms.md:305-319`). It is not a precedent for 28C SDP. Do not model the CLI on it.

### 4.4 Verdict: is automatic-unlock-on-write the norm or a hazard?

**Both, and the distinction is exactly what v1.22 should ship.** Automatic unlock-on-write is the norm (minipro, every Arduino programmer). What makes Firestarter's version a hazard is not the automation — it is that the automation is *unconditional, silent, irreversible, and unverified*. minipro proves the safe shape: capability-gated, announced, opt-out-able, and **paired with a re-lock**.

---

## 5. Firmware-side additions

### 5.1 Recommended: NO new `CMD_*` byte — use a new flag bit on `CMD_WRITE`, plus reuse `CMD_ERASE`-style single-step ops for the standalone case

| Option | Cost | Verdict |
|--------|------|---------|
| **A. New flag bits on `ctrl_flags`** | Zero wire change. `handle->ctrl_flags` is `uint32_t` (`firestarter.h:96`) and `get_flags` parses via `extract_long`/`simple_strtoul` into it (`json_parser.c:471-473`), so bits ≥ `0x100` are already wire-legal on both sides today. All eight low bits are taken (`firestarter.h:59-68`). | **RECOMMENDED for the write-path modifiers** (`FLAG_SKIP_SDP_UNLOCK`, `FLAG_SDP_RELOCK`) |
| **B. New `CMD_*` value** | `CMD` 9 and 10 are free (`firestarter.h:34-51`). **But there is a trap:** `firestarter.cpp:73-91` gates `configure_memory()` behind `cmd < CMD_READ_VPP` **and**, when `DEV_TOOLS` is defined, `cmd < CMD_DEV_ADDRESS` (7). A new `cmd` 9/10 would fall into the dev-flags `else` branch and **never reach `configure_memory`**, leaving `firestarter_operation_main` NULL. It would also need a new `case` in `loop()`'s switch (`:202-252`) or hit `MSG_ERR_UNKNOWN_CMD`. Renumbering `CMD_DEV_*` is a gratuitous breaking wire change. | Viable but requires restructuring a safety-relevant gate. **Prefer A.** |
| **C. Sub-op selector field** | New JSON key + new `key_parsers[]` entry. More surface than A for no gain. | No |

**For the standalone `lock` / `unlock` operations**, the cleanest fit is **B-with-eyes-open** *or* modelling on `CMD_ERASE`. Study `eprom_erase` (`eprom_operations.cpp:34-41`):

```c
bool eprom_erase(firestarter_handle_t* handle) {
    if (!is_flag_set(FLAG_CAN_ERASE)) { LOG_ERROR_ID(MSG_ERR_NOT_SUPPORTED); return true; }
    return !op_execute_simple_operation(handle);
}
```

That is the exact archetype v1.22 needs: **a capability-gated, no-data-payload, single-step operation that reports success/failure via `response_code`.** `op_execute_simple_operation` (`operation_utils.cpp:58-60`) wraps `_single_step_operation_callback` (`:271-295`), which runs `firestarter_operation_main` once and immediately calls `set_operation_to_done`. `eprom_check_chip_id` (`:43-50`) and `eprom_blank_check` (`:52-55`) are the same shape.

### 5.2 What the three-phase INIT/MAIN/END machine implies

`_execute_operation_house_keeping` (`operation_utils.cpp:203-225`) runs INIT → MAIN → END, **each phase waiting for a host ACK first** (`op_wait_for_ack`, `:203`, `:233`). For a no-payload operation:
- Set **only** `firestarter_operation_main`; leave `init` and `end` NULL. `_execute_operation_house_keeping_func` returns `CONTINUE` for a NULL callback (`:244` → `_execute_operation` returns `CONTINUE` at `:311`) and the phase is skipped without an ACK round-trip. `configure_eeprom28c`'s existing `CMD_BLANK_CHECK` arm (`eeprom_28c.cpp:44-46`) does exactly this.
- **Do not** put the SDP sequence in `firestarter_operation_init` for a standalone op. INIT is for write-preamble work; a standalone lock has no MAIN to precede.
- The `RESPONSE_CODE_OK / WARNING / ERROR` triad and `_check_response` (`:322-338`) give the success signal for free — no new response mechanism needed. Match the `FLAG_FORCE` → WARNING-instead-of-ERROR convention already used at `eeprom_28c.cpp:58-64` and `:86-92`.
- Per-command timeout is `TIMEOUT_MS 1000` (`firestarter.h:32`), reset by `op_reset_timeout()`. A `t_WC` `delay(10)` is far inside it; a 6-byte sequence + `delay(10)` is ~10 ms total.

### 5.3 Concrete firmware change list

| Change | Location | Notes |
|--------|----------|-------|
| **Fix the byte-flip path (must-do)** | new `eeprom28c_execute_command()` in `eeprom_28c.cpp`; stop calling `flash_execute_command` at `:109` | Route each command byte through `handle->firestarter_set_data` so `mem_util_remap_address_bus` applies. ~10 lines. This is §3.3. |
| **Fix the completion wait (must-do)** | `eeprom_28c.cpp:106` | Replace the `(0x5555, 0x20)` read-back with `delay(10)` (`t_WC` max) and/or a toggle-bit poll. §1.4. |
| **Add `EEPROM_SDP_ENABLE` table** | `eeprom_28c.cpp` alongside `EEPROM_SDP_DISABLE` (`:26-33`) | `{0x5555,0xAA},{0x2AAA,0x55},{0x5555,0xA0}`. Keep it **local to `eeprom_28c.cpp`**, mirroring the existing local `EEPROM_SDP_DISABLE`, rather than wiring the zero-caller `FLASH_ENABLE_WRITE_PROTECTION` in `flash_utils.h:48-52` — that header's tables are `const` at file scope in a header included by multiple TUs and are the wrong sharing boundary for a `0x0D`-specific table. |
| **Add `CMD_*` arms** | `configure_eeprom28c` switch, `eeprom_28c.cpp:39-47` | Today only `CMD_WRITE` and `CMD_BLANK_CHECK`. Note `CMD_CHECK_CHIP_ID` has **no arm** even though `eeprom28c_check_chip_id` exists (`:56-95`) — it is reachable only from write-init. A cheap adjacent win. |
| **New flag bits** | `firestarter.h` after `:68`; mirror in `constants.py:88-99` | `0x100`+. **Lockstep — must change together.** |
| **New message IDs** | `tools/catalog/messages.toml` | ERROR range is `0xA0..0xDF`, highest used `0xBC` (`MSG_ERR_FL4_BOOT_BLOCK_LOCKED`); `0xAE` was retired in v1.20. Next free: **`0xBD`, `0xBE`, `0xBF`**. INFO `0x40..0x7F`, WARN `0x80..0x9F` also have room. |

### 5.4 The codegen constraint — non-negotiable

`messages.toml` in the **meta-repo** `tools/catalog/` is canonical; `codegen.py` emits **both** `firestarter/include/messages.h` and `firestarter_app/firestarter/messages.py`; `sync_to_subrepos.sh` distributes the TOML byte-identically. A CI drift gate enforces it. Therefore: **edit `messages.toml`, run codegen, never hand-edit either generated file.** Two known traps from prior milestones:
- Raw codegen output is already `ruff`-clean and format-stable — do **not** hand-normalise `messages.py`.
- The devcontainer's Python 3.12 masks CI's 3.9/3.11 `ruff` behaviour. Validate `ruff check` + `ruff format --check` against the target version before claiming green.

### 5.5 Native test additions

`pio test -e native` already has `test_val_eeprom28c/` — but it is **configure-phase only**: it asserts no VPP-enable bit appears in any `CONTROL_REGISTER` write during `configure_memory` (`test_val_eeprom28c.cpp:70-113`). It never executes `eeprom28c_write_init`, so it cannot see the §3.3 defect. The recording harness needed already exists (`clear_bus_recording` / `bus_recording_count` / `recorded_reg` / `recorded_data`, plus `_shared/host_stubs_common.inc`).

**Add a `test_val_eeprom28c_sdp/` suite** that drives `eeprom28c_write_init` with a real `bus_config` for each of the four `0x0D` pinouts and asserts, per command byte, the exact `(LSB, MSB, CONTROL)` triple — specifically that the `rw_line` bit is **LOW** on every one of the six writes. **That test goes RED against today's tree and GREEN after the fix.** It is the milestone's proof-of-work and needs no silicon, which matters because there is no AT28C part in operator inventory.

---

## 6. Host-side additions

### 6.1 No new third-party dependency — confirmed

`click` and `rich` are already imported in `cli_handlers.py:29-32`. The wire encoding is `json` (stdlib). `constants.py` is pure constants. Everything below is additive within the existing dependency set. The one thing to sanity-check at plan time is `mypy --strict`, which is enforced on `cli_handlers.py` (and 7 other modules) — new handlers need full annotations.

### 6.2 Recommended CLI shape

Match the existing grammar. `erase` (`cli_handlers.py:583-630`) is the closest sibling: a top-level chip-argument command with `-f/--force`, delegating to a one-line `EpromOperator` method (`erase_eprom`, `eprom_operations.py:1628-1652`) that wraps `_operation_context` + `_run_state_machine`.

| Surface | Shape | Rationale |
|---------|-------|-----------|
| `firestarter unlock <chip>` | new `@cli.command`, behind an explicit confirm | Standalone, TommyPROM precedent, and the only way to rescue a chip that arrived locked. Top-level (not under `dev`) because it is a real user need, not a diagnostic. |
| `firestarter lock <chip>` | new `@cli.command` | The missing half. Non-destructive to data, but changes device state — still confirm. |
| `firestarter write --no-sdp-unlock` | new flag → `FLAG_SKIP_SDP_UNLOCK` | The opt-out `PROJECT.md:44` asks for. Naming mirrors the existing `--skip-erase` / `-b/--no-blank-check` idiom (v1.16 HARD-01) far better than minipro's opaque `-u`. |
| `firestarter write --sdp-relock` | new flag → `FLAG_SDP_RELOCK` | minipro's `protect_on`-after-write, but **opt-in** rather than default. Defaulting to re-lock would silently change every existing user's chip state — a v1.16-HARD-01-class footgun. |
| Log line on every auto-unlock | INFO message via the catalog | Turns today's silent side effect into an observable one. This alone satisfies most of `PROJECT.md:44`. |

Reject `firestarter sdp <lock|unlock> <chip>` — a two-level verb for two operations, inconsistent with the flat `read`/`write`/`erase`/`blank`/`id` grammar.

### 6.3 Gating

Two distinct gates, do not conflate them:

1. **`firestarter unlock` / `lock` gates** — these are new top-level commands and need their own confirm. Reuse the `dev test` pattern verbatim (`cli_handlers.py:1833-1840`): `_is_interactive()` → `Confirm.ask(...)` on a TTY, `-y/--yes` bypass, and off-TTY the explicit flag is itself consent. That helper (`_is_interactive`, `:1719-1726`) exists precisely because `CliRunner.invoke` replaces `sys.stdin`, so patch the helper, not `sys.stdin.isatty`.

2. **The v1.21 `dev test` destructiveness gate** — `derive_plan(..., destructive=...)` (`chip_test.py:318`) with `_DESTRUCTIVE_OPS = frozenset({OP_WRITE, OP_ERASE})` (`:453`) and the `locked_destructive` advisory list (`:295-330`). **If, and only if, an SDP step is added to the `dev test` plan**, it must join `_DESTRUCTIVE_OPS` and be omitted (not skipped) from a non-destructive plan per D-01/SAFE-01. Note the op vocabulary is a closed set of six strings (`chip_test.py:273-278`) consumed by `parse_devtest_issue.py` and the report renderer — adding `OP_SDP_LOCK`/`OP_SDP_UNLOCK` ripples into the issue parser, the ladder-state taxonomy (`diagnostic_report.py:207-243`), and the `audit_coverage_matrix` golden.

**Recommendation: keep SDP out of the `dev test` plan in v1.22.** Ship the CLI commands + write-path flags first. Adding an op to `dev test` triples the blast radius (op vocabulary + issue parser + report golden + orchestrator AST gate) for a chip family nobody can bench.

3. **The orchestrator-only AST gate** (`tools/check_devtest_orchestrator.py`) denies VPP-set calls, raw wire-JSON dict construction, and `force=True` pass-through in `chip_test.py`, `submit.py`, and the `dev_test`-scoped functions in `cli_handlers.py`. New **top-level** `lock`/`unlock` handlers are outside its scanned function set (`_HANDLER_FUNCTION_NAMES`) — but they must still go through `resolve_chip` + `convert_to_programmer` + an `EpromOperator` method and must never hand-assemble a command dict, because that is the project's standing architecture, gate or no gate.

### 6.4 Host change list

| Change | Location |
|--------|----------|
| `FLAG_SKIP_SDP_UNLOCK`, `FLAG_SDP_RELOCK` | `constants.py:88-99` — **lockstep with `firestarter.h:59-68`** |
| `COMMAND_*` + `COMMAND_NAMES` entry, only if option B is chosen | `constants.py:54-86` |
| `build_flags(...)` kwargs | `eprom_operations.py:168-183` |
| `sdp_lock_eprom` / `sdp_unlock_eprom` operator methods | `eprom_operations.py` — copy `erase_eprom` (`:1628-1652`) verbatim in shape |
| `lock` / `unlock` Click commands + `write` flags | `cli_handlers.py` (near `erase`, `:583`) |
| Protocol-doc row | `doc/protocol-id.md:22` (the `0x0D` row) and `doc/lockable-proms.md` |

---

## 7. What NOT to add

| Avoid | Why | Do instead |
|-------|-----|------------|
| **A `lock-status` command, or any "is it locked?" query** | No 28C part has a readable SDP status bit — §2, cited from two vendor datasheets and the project's own `lockable-proms.md:289-303`. Any such command would report an inference dressed as a measurement. | Keep it out of scope (`PROJECT.md:64` already does). If a probe is ever wanted, it belongs in `dev test`'s finding vocabulary as an explicitly advisory result. |
| **Per-part SDP magic-address tables in the DB** | The alternating-bit patterns truncate correctly: `0x5555 & 0x1FFF == 0x1555`, `0x2AAA & 0x1FFF == 0x0AAA` — exactly the AT28C64B's documented values (§3.1, verified by executing the real host code). A per-part table would be 84 rows of redundancy plus 84 chances to typo an address into a wrong-pin write. | One absolute pair, `0x5555`/`0x2AAA`, driven through the existing bus remap. |
| **AMD Autoselect / Winbond product-ID protection-state query sequences** | Different command sets on different protocol buckets (`0x05`/`0x06`). W29EE is **not on `0x0D`** at all (§3.4). Pulling them in imports the `0x05`/`0x06` handlers' concerns into a `0x0D` milestone. | Already out of scope (`PROJECT.md:64`). Reaffirm. |
| **Making `--sdp-relock` the default** | Silently changes device state for every existing user of `firestarter write`. Precisely the v1.16 HARD-01 `write -b` footgun class, and the project has already paid for that lesson once. | Opt-in flag + an INFO log line stating which SDP action was taken. |
| **A new `CMD_*` byte "because lock is a new operation"** | `CMD` 9/10 are free but sit **above** `CMD_DEV_ADDRESS`, so `firestarter.cpp:79` skips `configure_memory` for them when `DEV_TOOLS` is defined; and `loop()`'s switch would reject them. Renumbering `CMD_DEV_*` is a breaking wire change for a cosmetic gain. | Flag bits on `ctrl_flags` (`uint32_t`, wire-ready today) for write-path modifiers; if a standalone command byte really is needed, budget the `DEV_TOOLS` gate restructure explicitly. |
| **Deleting `FLASH_ENABLE_WRITE_PROTECTION` as a duplicate of `FLASH_ENABLE_WRITE`** | They are byte-identical because the AT28C datasheet makes `AA-55-A0` genuinely dual-purpose: lock-with-no-payload vs write-while-protected-with-payload (§1.2). The abandoned v1.16 `0052c42` dedup would have erased real semantics. | Keep both, or collapse to one table named for the bytes (`SDP_CMD_PREFIX_A0`) with both intents documented at the call sites. |
| **Hand-editing `messages.h` or `messages.py`** | Both are codegen output from `messages.toml`; CI has a drift gate. | Edit the meta-repo TOML, run `codegen.py`, run `sync_to_subrepos.sh`. |
| **"Reuse the existing `page-size` wire field"** | It does not exist on the wire. `constants.py:107-111` claims firmware sync; `json_parser.c:67` has no such key and the firmware silently discards it (§3.2 item 3). | If page size is needed, add the `key_parsers[]` entry as real lockstep work — or correct the false comment and defer. |
| **A `--force` path that bypasses a firmware SDP refusal** | The project's standing posture, and the orchestrator AST gate denies `force=True` pass-through in the `dev test` surface. `FLAG_FORCE` in this family means "downgrade ERROR to WARNING" (`eeprom_28c.cpp:58-64`), not "ignore". | Keep `FLAG_FORCE` semantics unchanged. |
| **A bench-graduation requirement** | No AT28C part in operator inventory (`PROJECT.md:59`). | Software-only validation: native register traces + host tests. The §5.5 RED→GREEN test is stronger evidence than a single-sample bench run would be anyway. |
| **Trusting the `PROJECT.md` "unlock already ships in b11" premise** | True at source level, false electrically (§3.3). | Re-baseline the milestone on the §3.3 finding before writing requirements. |

---

## 8. Recommended stack summary

### Core (all already in-tree — no installs)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| PlatformIO + Arduino AVR | as pinned in `firestarter/platformio.ini` | Firmware build for uno / leonardo / uno328pb | Unchanged; SDP work is ~50 lines of C, no flash-budget risk |
| Unity via `pio test -e native` | as configured | Host-side register-trace tests, no board needed | The only validation path available with no AT28C silicon; harness + recording stubs already exist |
| Click | already a dependency | `lock` / `unlock` commands + `write` flags | 14 `@cli.command()` + a `dev` group already established |
| rich (`Confirm.ask`) | already a dependency | TTY safety confirm | Exact v1.21 `dev test` gate pattern, `cli_handlers.py:1833-1840` |
| `tools/catalog/codegen.py` + `messages.toml` | v1 catalog | New message IDs `0xBD`–`0xBF` | Mandatory path; CI drift gate |

### Development tools (unchanged, all already gating CI)

`ruff check` + `ruff format --check` + `mypy --strict` (8 modules incl. `cli_handlers.py`) + `pytest --cov-fail-under=70`; firmware `pio test -e native`; `tools/check_dispatch.py`, `tools/diff_db.py`, `tools/check_devtest_orchestrator.py`.

### Installation

```bash
# Nothing to install. Verify the existing toolchain instead:
cd /workspaces/firestarter_app && pip install -e '.[test]'
cd /workspaces/firestarter    && pio test -e native
```

### Version compatibility / lockstep contract

| Pair | Constraint |
|------|-----------|
| `firestarter/include/firestarter.h` ↔ `firestarter_app/firestarter/constants.py` | New `FLAG_*` (and any `CMD_*`) values must change in the **same commit pair**. `tests/test_revision_constants_parity.py` is the existing precedent guard. |
| `tools/catalog/messages.toml` → `messages.h` + `messages.py` | Regenerate both; never hand-edit. |
| Devcontainer Python 3.12 vs CI 3.9/3.11 | Validate `ruff` against the CI target before claiming green. |
| Branch base | v1.21 **is** merged to `beta` in both sub-repos, so v1.22 forks off `beta` per standing policy (`PROJECT.md:61`) — no v1.15/v1.21-style exception. Firmware-touching → dual-repo lockstep. |

---

## 9. Open questions for the roadmap

1. **RESOLVED (was the top risk):** enable-vs-write-cycle — `AA-55-A0` + `t_WC` latches SDP with no payload. §1.2, three citations.
2. **NEW TOP QUESTION — scope:** does v1.22 absorb the §3.3 `/WE`-collision fix, or does the fix become its own phase with lock/unlock stacked on top? **Recommendation: absorb it as Phase 116.** Everything else in the milestone is untestable until unlock actually works, and the RED→GREEN native test is the milestone's only real proof.
3. **`PAGE_SIZE 64` vs AT28C010's 128 B / AT28C040's 256 B** (§3.2 item 2) — in scope, or an explicit named deferral? Affects 18 of 84 chips. Note the `page-size` wire field does not exist, so "in scope" means real lockstep work.
4. **`DIP24_2816` missing `static-high-pins: [24]`** (§3.3 caveat) — VCC is not force-driven for the 19 DIP24 EEPROMs. Separate finding; confirm against the shield schematic before acting.
5. **AT28C040 and AT28C16/AT28C04 SDP addresses are UNVERIFIED** — datasheets not read. Low risk given the truncation argument, but state it as UNVERIFIED in the milestone's evidence record rather than implying coverage.
6. **gh#11 / gh#12 framing:** §1.4 + §3.3 suggest those reports may describe live defects, not stale ones. Re-word the planned close-out comments accordingly.
7. **Should `dev test` gain SDP steps?** Recommendation: **no**, in v1.22 (§6.3).

---

## Sources

**Primary — vendor datasheets, read verbatim (HIGH):**
- Microchip **DS20006386B** *AT28C256 Industrial Grade 256-Kbit Paged Parallel EEPROM*, Rev B Sept 2022 — §6 pp.10-11 (SDP description, `t_BLC`, "data … not written to the device", Table 6-1 operating modes), §6.6 p.13 / §6.8 p.14 (AC + page-mode timing), §6.11 p.16 (enable), §6.12 p.17 (disable), §6.16-6.17 pp.19-20 (toggle bit), §8 p.27 (revision history). **In-tree at `firestarter_app/datasheets/AT28C256.pdf`.**
- Microchip **DS20006432B** *AT28C64B 64-Kbit Parallel EEPROM with Page Write and Software Data Protection*, © 2020-2023 — §6.6.1/§6.6.2 + §6.8 p.10, Table 6-4 p.14, §6.18 p.16, §6.19 p.17. `ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/AT28C64B-64-Kbit-8Kx8-Parallel-EEPROM-with-Page-Write-and-Software-Data-Protection-DS20006432.pdf`
- Atmel **doc0270**, rev `0270L–PEEPR–2/09` *AT28C64B* — §19/§20 p.10. The unambiguous note→terminal-box mapping for §1.2. `ww1.microchip.com/downloads/en/DeviceDoc/doc0270.pdf`
- Atmel **doc0353**, rev `0353G–PEEPR–10/06` *AT28C010 1-megabit (128K x 8) Paged Parallel EEPROM* — §19/§20 p.10.

**Primary — upstream source code (HIGH):**
- minipro `main.c` (DavidGriffith upstream) — usage block ll.60-61, `cmdopts.no_protect_off/on` ll.39-40 + 108-112, write flow ll.516-543.

**Community / cross-checked (MEDIUM):**
- TommyPROM, *28C EEPROMs and Software Data Protection (SDP)* — `tomnisbet.github.io/TommyPROM/docs/28C256-notes`. Atmel 150 µs vs Xicor/ON-Semi 100 µs `t_BLC`; Atmel parts hard-refuse out-of-spec timing; ~80 µs/byte achieved; tested part list.
- bread80.com, *The Ben Eater EEPROM Programmer, 28C256 and Software Data Protection*; 6502.org forum thread 2043 — factory-locked parts despite datasheet claims.

**Negative result (LOW):**
- flashrom parallel support is LPC/FWH block-lock registers, not 28C SDP — no usable precedent.

**In-tree, read directly (HIGH — every file:line in this document was read, not inferred):**
`firestarter/src/proms/eeprom_28c.cpp`, `flash_utils.cpp`, `flash_5v_page.cpp`, `memory.cpp`; `firestarter/src/firestarter.cpp`, `eprom_operations.cpp`, `operation_utils.cpp`, `json_parser.c`; `firestarter/include/{firestarter,flash_utils,eeprom_28c,memory_utils,rurp_pinout,rurp_types}.h`; `firestarter/tools/catalog/messages.toml`; `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp`; `firestarter_app/firestarter/{constants,database,eprom_operations,cli_handlers,chip_test,diagnostic_report}.py`; `firestarter_app/firestarter/data/{chip_database,pinouts}.json`; `firestarter_app/tools/check_devtest_orchestrator.py`; `firestarter_app/doc/{protocol-id,lockable-proms}.md`; `.planning/PROJECT.md`.

The §3.1 and §3.3 bus-pattern results were produced by **executing the project's own `database.py`** (`EpromDatabase.convert_to_programmer` → `get_bus_config` → `pin_conversions`) against the shipped `chip_database.json` / `pinouts.json` and applying `fu_flash_fast_address`'s documented arithmetic — not by hand calculation.

---
*Stack research for: AT28C parallel-EEPROM SDP lifecycle on protocol `0x0D` (firmware + host CLI)*
*Researched: 2026-07-27*
