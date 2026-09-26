# Phase 153: Write-Path Erase Policy — Research

**Researched:** 2026-08-21
**Domain:** Arduino AVR firmware protocol handlers (`0x0D` 28C EEPROM, `0x05` flash4) + Python host CLI flag derivation; dual-repo lockstep under a zero-headroom AVR size budget
**Confidence:** HIGH on every code fact (all read in-session, line-verified); HIGH on the erase byte sequence (primary manufacturer application note read directly); MEDIUM on the size delta of the not-yet-written erase op (a measurement task, not a research answer)

---

## Summary

Every one of the nine ERASE requirements is reachable, and three of them are cheaper than the roadmap
assumes. **ERASE-02's `0x05` sibling conditional EXISTS** — `flash_5v_page.cpp:88-90`, byte-identical
shape to `0x0D`'s — so it is located, not absent. **ERASE-06 needs no `ic_layout.py` edit at all**:
`info`'s "can be erased" row derives from `electrical.type` only and already prints
`yes (electrically erasable)` for every algorithm-13 chip; the contradiction is entirely on the *wire
flag* side, so restoring `FLAG_CAN_ERASE` (ERASE-03) makes the two agree as a by-product. **ERASE-04's
software 6-byte sequence is already in this tree** as `FLASH_ERASE` in `firestarter/include/flash_utils.h`
(`AA/55/80 + AA/55/10`), verified byte-for-byte against Atmel's own *Software Chip Erase* application
note (Rev. 0544B-10/98) — and the `test_eeprom28c_sdp` suite already calls that table "chip-erase" and
pins its one-nibble divergence from the SDP tables (Case 19).

The GATE-03 question resolves cleanly but **not the way the criterion implies**. The datasheet's
hardware erase path (12 V on OE / pin 22) is real — AT28C256 DS20006386B Table 6-1 confirms
`Chip Erase: CE=VIL, OE=VH(12.0 V ±0.5), WE=VIL` — and it is *already implemented in this tree* for
protocol `0x05` at `flash_5v_page.cpp:195-230`, which asserts `CTRL_VPE_ENABLE` and drives OE to 12 V.
But `tools/check_dispatch.py` is a **database-and-dispatch-table** gate: its GATE-03 guard fires only on
`handler == "configure_eprom" and pinout in no_vpp_pin_pinouts`. It cannot see a control-register write
inside a handler body. So the gate would stay silently green even if this phase implemented the hardware
path. The honest statement is: *the software path is chosen because it is the correct engineering choice
and because `check_dispatch.py` could not have stopped the wrong one* — not because the gate forced it.
The gate must be left byte-unchanged, and the phase should say in writing that its `configure_eeprom28c`
erase writes **no** VPP/VPE control bit.

The hard constraint is **size, and it is RAM, not flash.** Measured this session by `avr-nm` on the
committed leonardo ELF: a 6-entry `byte_flip_t` table occupies **0x1e = 30 bytes in section `d`
(`.data`, i.e. RAM)** — `EEPROM_SDP_DISABLE` at `0x800127`, `FLASH_ERASE` at `0x800163`. MERGE-05's RAM
clause is exact equality plus one named 2 B exemption, already fully consumed. So **any new
`byte_flip_t` table costs +30 B RAM and blows the RAM clause outright.** Two RAM-neutral designs exist
(inline six `set_data` calls, or a `PROGMEM` table with a per-entry copy) and one adjudicated escape
hatch exists (a fourth named, SHA-attributed exemption constant, the mechanism Phases 145/149/151 each
used). This is a design decision the plan must make explicitly at Wave 0, before any code is written.

**Primary recommendation:** three firmware edits (delete two blank-check conditionals; add one
`case CMD_ERASE:` arm plus a RAM-neutral six-write erase emitter reusing
`eeprom28c_emit_command_sequence`), one host one-line edit (`database.py:617`, drop `13` from the
exclusion tuple), one host comment correction, and four **test inversions that are mandatory, not
optional** — `test_configure_memory.cpp` Case group 4 and `test_eeprom28c_sdp` Case 25 both assert
today that `configure_eeprom28c` has no `CMD_ERASE` arm. Plus a cold triple-target re-measure and a
`size_baseline.json` `native_envs` case-count update, because the default-mode gate demands byte
identity on the native case counts too.

---

## User Constraints (from 152-CONTEXT.md — this phase has no CONTEXT.md of its own)

> There is **no `153-CONTEXT.md`**. Phase 153 was created during `/gsd-discuss-phase 152`, so its locked
> decisions live in `.planning/phases/152-report-provenance-close/152-CONTEXT.md`. The following is
> copied verbatim from that file's **D-07**, **D-08** and **D-15**.

### Locked Decisions

**D-07: The operator's write/erase policy becomes a NEW PHASE 153 in v1.32.**

> **Policy, verbatim intent:** on protocols where a blank part is *not* required in order to write —
> `0x0D` (28C family) and `0x05` (flash4), which auto-erase per page during the write — **`write` must
> not perform a blank check at all**. And **`erase` and `blank` must each be available as standalone
> steps.**
>
> Decomposition measured during this discussion:
>
> | what | where | state |
> |---|---|---|
> | pre-write blank check on `0x0D` | `firestarter/src/proms/eeprom_28c.cpp:517` — `if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) { mem_util_blank_check(handle); }` | **one conditional**, in the handler |
> | same, `0x05` | `flash_5v_page.cpp` sibling | to locate |
> | `blank` as its own step | `cli_handlers.py:854` + `eeprom_28c.cpp:218` wires `CMD_BLANK_CHECK` → `mem_util_blank_check` | **ALREADY WORKS — nothing owed** |
> | `erase` as its own step | no `CMD_ERASE` arm in `configure_eeprom28c`; `FLAG_CAN_ERASE` cleared for `algo 13` | **missing** |
> | `info`'s "can be erased" row | `ic_layout.py:579` | contradicts the wire flag |
>
> **⚠ HAZARD for whoever implements erase:** the datasheet's *hardware* path puts **12 V on OE
> (pin 22)** on `DIP28_28C256`. That is precisely what GATE-03 / `tools/check_dispatch.py` exists to
> prevent on a 5 V part, and `check_dispatch.py` is **not to be weakened**. The *software* 6-byte path
> carries no such hazard but needs the app note. **Phase 153 must decide which path it implements and
> fund the GATE-03 question explicitly.**
>
> Phase 153 also owns the `database.py:591` **code comment** correction, since it must touch
> `database.py:621` anyway to restore `FLAG_CAN_ERASE` (D-15).
>
> **Rejected:** a backlog item stated outward as queued; landing the one-conditional blank-check half
> inside 152 (would make the close a dual-repo firmware phase mid-merge, needing native tests and a
> cold triple-target size re-measure against **zero** leonardo MERGE-05 headroom).

**D-08: Phase 153 runs BEFORE Phase 152.**

> 152's `Depends on` gains 153 as a deliberate out-of-number-order dependency. One merge, one cut, one
> set of release notes, and every claim is true at the moment it becomes public.
>
> **Rejected — and the reasoning is load-bearing:** *152 first, 153 gets its own cut* would post
> `write -b` as the recommended path into the most public artifact this project has, hours after the
> operator declared that check should not exist. Writing a known-superseded workaround into the record
> is exactly the failure class OUT-05's gate exists to catch. *Folding 153's work into 152's merge*
> would draft the close's artifacts against code landing after them, collide with 153 on
> `cli_handlers.py` under one-writer-per-file, and run the close's gates against a moving target.
>
> **Consequence the gate must absorb:** by the time 152's notes are written, `0x0D` erase and the
> write-path policy **are shipped**, while `write --sdp-relock` still is not. See D-10/D-11.

**D-15 (the part 153 owns): In-repo record corrections, settled by precedent.**

> - `PROJECT.md`'s *"one firmware-touching workstream"* → **three** (149, 151, 153). The v1.32 roadmap
>   entry and PROJECT.md both carry the stale claim; 151-CONTEXT.md already flagged it and said 152's
>   outward text must not repeat it.
> - `PROJECT.md`'s workstream table gains a row for 153; workstream 4's description updates.
> - Phase 121 D-12's disproven premise is corrected in **`.planning`** by 152. The **code comment** at
>   `firestarter_app/firestarter/database.py:591` is left to **Phase 153**, which must touch
>   `database.py:621` anyway — so 152 never reaches into a sub-repo for a comment edit.

**Also binding (from 152-CONTEXT.md's D-06 record, the premise this phase acts on):**

> **Phase 121 D-12's stated premise is DISPROVEN.** `database.py:591` records the reason for clearing
> the flag as *"advertising `FLAG_CAN_ERASE` for these 84 chips is a **false capability statement**."*
> The capability is real in the silicon and real in infoic. What is false is only that *firestarter*
> can perform it. D-12 made the host claim less rather than making the firmware do more.

### Claude's Discretion

D-08 (153-before-152) is recorded in 152-CONTEXT.md under "Claude's Discretion" — already decided and
locked above. Within Phase 153 itself, the following are open and this research recommends on each:

- **Which erase mechanism** (inline six writes / `PROGMEM` table / new `.data` table + a fourth named
  exemption) — see `## Architecture Patterns` Pattern 3 and `## Don't Hand-Roll`.
- **Whether `erase -b`'s post-erase blank check is wired on `0x0D`** (an `operation_end` arm). Neither
  sibling protocol wires it (`flash_5v_page.cpp:48-50` has no end; `flash_nor_unlock.cpp:41` has it
  commented out). Recommend: **do not wire it**; blank remains its own step per ERASE-05.
- **Whether `write -b` gets a "vacuous flag" host warning on `0x0D`**, mirroring the existing
  `--skip-erase` warning at `cli_handlers.py:797-804`. Recommend: **no new warning** (see Pitfall 5).
- **Whether the two prose docs are corrected in-phase** (`firestarter/doc/PROTOCOLS.md` §1.6 and
  `firestarter_app/doc/protocol-id.md:22`). Recommend: **yes** — see `## Gap: claims that become false`.

### Deferred Ideas (OUT OF SCOPE)

From `.planning/REQUIREMENTS.md` § Out of Scope, and ERASE-09:

| Item | Reason |
|---|---|
| Graduating `0x0D` to `supported` / any `support_status` change | No AT28C part in inventory. The Evidence Ceiling forbids it; v1.22 and v1.30 both held this line. |
| Closing gh#21 / #32 / #11 / #12 | A code fix is not a validation. Only `devtest-triage` closes a `dev test` issue, and only on a PASS report from real silicon. |
| Any claim that the `0x0D` write path is proven | ERASE-09: ships **software-proven and unvalidated on silicon**, in those words. |
| Requiring an AT28C part for any criterion | ERASE-09, explicit. |
| Editing `chip_database.json` by hand | It is GENERATED (`tools/build_db.py`); the generator/decode function is the only edit site. `.claude/skills/devtest-rootcause/SKILL.md` rule. |
| `write --sdp-relock` | Deferred a second time to Backlog 999.28 (Phase 150 deferral record). |

---

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| **ERASE-01** | `write` performs no blank check on `0x0D`; conditional at `eeprom_28c.cpp:517` no longer gates the write path | **Line verified at 547-549.** Deleting it is behaviourally identical to today's already-shipped `write -b` path on this protocol — see F-1 and Pitfall 1 (INIT loop analysis). Only `mem_util_blank_check` sets `operation_in_progress` during write-INIT, so removal makes INIT single-shot, which is the existing `-b` behaviour. |
| **ERASE-02** | Same for `0x05`; sibling conditional **located in code** before change | **LOCATED: `flash_5v_page.cpp:88-90`**, byte-identical shape. Evidence of presence, not absence. F-2. |
| **ERASE-03** | `CMD_ERASE` arm in `configure_eeprom28c`; `FLAG_CAN_ERASE` restored for `algorithm 13` at `database.py:621` | Arm shape derived from four existing sibling arms (F-3). Host edit is **line 620**, not 621 (`if algo not in (5, 13):` → `(5,)`); 621 is the `simple_flags |=` body. All 84 algorithm-13 rows gain the flag; 0 rows are ineligible (F-6). |
| **ERASE-04** | **software 6-byte** sequence, not the 12 V-on-OE hardware path; `check_dispatch.py` not weakened/exempted/re-baselined; phase states which path and why | Sequence **verified verbatim** against Atmel AN *Software Chip Erase* Rev. 0544B-10/98 (F-4). Already in-tree as `FLASH_ERASE` (`flash_utils.h:33-40`). `check_dispatch.py` analysed in full: it is DB+dispatch-table scoped and **structurally cannot** see a handler-body control-register write (F-5) — so the phase's written statement is the *only* control here. |
| **ERASE-05** | `blank` remains its own step — non-regression only | `cli_handlers.py:854` (`@cli.command(name="blank")`, def at 866) → `check_eprom_blank` (`eprom_operations.py:2161`) → `CMD_BLANK_CHECK` → `eeprom_28c.cpp:218-220` → `mem_util_blank_check`. Existing pinning tests named in `## Validation Architecture`. F-7. |
| **ERASE-06** | `info`'s "can be erased" row agrees with the wire flag | **No `ic_layout.py` edit needed.** `ic_layout.py:578-582` keys on `electrical.type` only and already prints `yes (electrically erasable)` for all 84 rows. Measured today: `AT28C256 → flags=0x00` while `info` says yes. ERASE-03 makes them agree. F-8. |
| **ERASE-07** | Stale Phase 121 D-12 code comment at `database.py:591` corrected | Comment block spans `database.py:585-616`; the false sentence is at **:589-592** (*"has no erase operation at all, so advertising FLAG_CAN_ERASE for these 84 chips is a false capability statement"*); the REVERSAL RECORD paragraph begins at :596 and its *"the 0x0D firmware path genuinely never reads FLAG_CAN_ERASE"* sentence also becomes false. F-9. |
| **ERASE-08** | Constants lockstep; flash/RAM measured against a pre-change baseline on all three AVR targets; leonardo at ZERO MERGE-05 headroom | Full measured position in `## Don't Hand-Roll` and `## Common Pitfalls` Pitfall 3. **A new `byte_flip_t` table = +30 B RAM, and the RAM clause has 0 B headroom.** Baseline reproduced this session: leonardo 27500/2016, byte-identical to `size_baseline.json`. F-10, F-11. |
| **ERASE-09** | Stated **software-proven and unvalidated on silicon**; no graduation, no `support_status` change, no AT28C part required | Every criterion in `## Validation Architecture` is bench-free. Two host gates already forbid `support_status` writes (`tools/check_no_community_support_status_write.py`) and over-claiming diagnostic-report text (`tools/check_diagnostic_report_claims.py`). |

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Deciding *whether* a blank check runs on a write | Firmware handler (`eeprom_28c.cpp`, `flash_5v_page.cpp`) | — | The conditional lives in the handler's `write_init`. The host has no say beyond the flag bit it emits; the policy is "no blank check on this protocol, ever", which is a protocol property, so it belongs where the protocol is implemented. |
| Emitting the chip-erase command sequence | Firmware handler (`eeprom_28c.cpp`) | — | Bus-level byte writes at magic addresses through `handle->firestarter_set_data`. No host tier can do this. |
| Advertising erase capability (`FLAG_CAN_ERASE`) | Host (`database.py::convert_to_programmer`) | Firmware precondition (`eprom_operations.cpp:36`) | The host owns the wire flag; the firmware's `eprom_erase` re-checks it as its refusal precondition. Both must move together or the command is refused one layer earlier. |
| Refusing an unimplemented (cmd, protocol) cell | Firmware op layer (`operation_utils.cpp:170`, the NULL-main guard) | — | Phase 119 D-06 deliberately centralised this at one site instead of six `default:` arms. Adding a `CMD_ERASE` arm *removes* `0x0D` erase from this guard's coverage; nothing else changes. |
| `dev test` plan derivation (which steps exist) | Host (`chip_test.py::derive_plan`) | — | Reads the wire flag. Restoring the flag changes the plan shape on all 84 rows — see Pitfall 4. |
| `info`'s human-readable capability row | Host (`ic_layout.py::build_specifications`) | — | Derives from `electrical.type`, independent of the wire flag. This independence is exactly why ERASE-06 resolves for free. |
| Size/RAM budget enforcement | Firmware repo tooling (`scripts/check_size_baseline.py`) | Committed baseline JSON | Manual/phase gate, **not** run by either repo's CI. |

---

## Standard Stack

No new external dependency. This phase touches only in-tree code. The "stack" is the existing toolchain,
pinned by `size_baseline.json`'s `meta` block and reproduced this session:

### Core
| Component | Version | Purpose | Why Standard |
|---|---|---|---|
| PlatformIO Core | 6.1.19 | Firmware build + native Unity test runner | Pinned in `scripts/baseline/size_baseline.json:meta.platformio_core` `[VERIFIED: file read]` |
| `platform-atmelavr` | 5.2.0 | AVR platform | Pinned, same file `[VERIFIED]` |
| `toolchain-atmelavr` / avr-gcc | 1.70300.191015 / 7.3.0 | Compiler; `avr-nm` used for the RAM-section measurement in F-10 | Pinned, same file `[VERIFIED]` |
| `framework-arduino-avr` | 5.3.0 (MiniCore 3.1.2 for uno328pb) | Arduino core | Pinned, same file `[VERIFIED]` |
| Unity (via `pio test`) | bundled | Firmware native tests | 17 suites / 163 cases in `env:native` `[VERIFIED: platformio.ini:130-151 + size_baseline.json:native_envs]` |
| pytest | repo-pinned `.[test]` | Host tests | `pyproject.toml:105-107`, `addopts = "-ra -q"` `[VERIFIED]` |
| ruff | repo-pinned | Lint + format, `select = [E,F,I,UP]`, `target-version = "py39"` | `pyproject.toml:109-110`, CI `ci.yml:80-84` `[VERIFIED]` |
| mypy | repo-pinned, watermark 35 | Type gate via `tools/check_mypy_watermark.py` | `pyproject.toml:174` comment; current 33 → **2 errors of headroom** `[VERIFIED: file read + memory record]` |

### Supporting
| Component | Purpose | When to Use |
|---|---|---|
| `firestarter/scripts/check_size_baseline.py` | The MERGE-05 band comparator and the default byte-identity gate | Every firmware task; both modes (see Pitfall 3) |
| `firestarter/scripts/check_build_warnings.py` | Native warning watermark (1166 cold, `<=` rule) | After any change that adds a native TU |
| `firestarter_app/tools/check_dispatch.py` | GATE-03 DB/dispatch guard | Must run and must stay byte-unchanged (ERASE-04) |
| `firestarter_app/tools/check_no_log_in_sdp_window.py` | No-logging structural scan over `eeprom28c_emit_command_sequence` + `eeprom28c_wait_for_sdp_completion` bodies | Any edit inside `eeprom_28c.cpp` |
| `firestarter_app/tools/build_db.py` | The ONLY legitimate way to change `chip_database.json` | Not needed this phase — no DB field changes |
| `tools/catalog/messages.toml` (3 byte-identical copies: meta, `firestarter/`, `firestarter_app/`, sha `260066039d…`) | Message-ID catalog; codegen source | Only if a NEW message id is added — avoid (see ERASE-08 / F-12) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|---|---|---|
| A new `byte_flip_t EEPROM_CHIP_ERASE[6]` in `eeprom_28c.cpp` | Reference the existing `FLASH_ERASE` from `flash_utils.h` | **Same 30 B RAM cost.** `flash_utils.h` declares its tables at namespace scope in a header with internal linkage, so each TU gets its own copy — proven by the ELF carrying *two* surviving copies of `FLASH_ENABLE_WRITE` (`_ZL18FLASH_ENABLE_WRITE.lto_priv.92` and `.93`), i.e. LTO does **not** merge them. Also collides with FIX-04's byte-frozen `flash_utils.h` framing and Phase 117 D-10 / 119 D-09's deliberate "keep the `0x0D` tables local" precedent. |
| A `.data` table at all | Six inline `handle->firestarter_set_data(handle, addr, byte)` calls | **RAM-neutral (0 B).** Flash-only. Breaks the table+parity-gate precedent (`test_sdp_table_parity.py` extracts tables *by declared name*), so the erase sequence would have no cross-table parity leg — mitigate with a native stream-equality case instead, which is strictly stronger anyway (Case 17/18/19 precedent). |
| A `.data` table at all | `PROGMEM` table + `pgm_read_dword`/`pgm_read_byte` per entry | RAM-neutral, but `eeprom28c_emit_command_sequence` (`eeprom_28c.cpp:313-330`) dereferences `sequence[i].address` **directly** — a PROGMEM table needs either a second emitter or a per-entry stack copy, both of which cost flash and one of which would fall outside the no-log window gate's scanned body. |
| A new named MERGE-05 RAM exemption | — | The adjudicated, precedented escape hatch (`MERGE05_DEFECT_FIX_EXEMPTION_BYTES` 96, `..._PAGE_SIZE_SEAM_...` 210/2, `..._LOCK_STATUS_READ_...` 288). Legitimate, but spends the milestone's fourth exemption on a table that two other designs make free. |

**Installation:** none. No package is added, so the Package Legitimacy Audit is not applicable — see that
section.

---

## Package Legitimacy Audit

**Not applicable.** This phase installs no external package in either repository. No `pip install`, no
`npm install`, no `lib_deps` addition. `firestarter_app/pyproject.toml`'s dependency list and
`firestarter/platformio.ini`'s `lib_deps` are both untouched by every task this research recommends.

| Package | Registry | Verdict | Disposition |
|---|---|---|---|
| *(none)* | — | — | — |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

If a plan later proposes a dependency (e.g. `pypdf` for datasheet extraction), it must run the Package
Legitimacy Gate then. Note that `pypdf 6.16.1` is **already present in the devcontainer** and was used
this session to read `firestarter_app/datasheets/AT28C256.pdf`; it is a dev-environment tool, not a
package dependency, and must not be added to either repo's manifest for that reason.

---

## Architecture Patterns

### System Architecture Diagram

```
 user
  │
  ├── firestarter write AT28C256 img.bin ─────────────────┐
  ├── firestarter erase AT28C256 ────────────────────┐    │
  └── firestarter blank AT28C256 ───────────────┐    │    │
                                                │    │    │
        HOST (firestarter_app/)                 │    │    │
        cli_handlers.py                         │    │    │
          blank()  :866 ──────────────────┐     │    │    │
          erase()  :901 ────────────────┐ │     │    │    │
          write()  :636 ──────────────┐ │ │     │    │    │
                                     │ │ │     │    │    │
          _build_op_flags() :330 ◄────┴─┴─┴─────┴────┴────┘
              │  -b/--no-blank-check  -> FLAG_SKIP_BLANK_CHECK 0x08
              │  --skip-erase         -> FLAG_SKIP_ERASE       0x04
              ▼
        eprom_operations.py
          write_eprom / erase_eprom :2035 / check_eprom_blank :2161
              │
              │  resolve_chip -> database.py
              │                   convert_to_programmer() :617-622
              │                     electrical-type in {EEPROM, Flash/EEPROM}
              │                       AND algo not in (5, 13)   ◄── ERASE-03 EDIT (drop 13)
              │                         -> flags |= FLAG_CAN_ERASE 0x02
              ▼
        ══ WIRE (JSON cmd + flags, 250000 baud) ═══════════════════════
              ▼
        FIRMWARE (firestarter/)
        firestarter.cpp dispatch :322-325 (CMD_ERASE=3, CMD_BLANK_CHECK=4)
              ▼
        eprom_operations.cpp
          eprom_erase() :34 ── if !FLAG_CAN_ERASE -> MSG_ERR_NOT_SUPPORTED, done
          eprom_blank_check() :52
              ▼
        memory.cpp configure_memory :105  (protocol 0x0D)
              ▼
        eeprom_28c.cpp  configure_eeprom28c() :204
              ├── case CMD_WRITE      :222 -> init=write_init, main=write_execute
              ├── case CMD_BLANK_CHECK:226 -> main=mem_util_blank_check   ◄── ERASE-05 (works)
              ├── case CMD_SDP_UNLOCK :229
              ├── case CMD_SDP_LOCK   :232
              └── case CMD_ERASE      ***MISSING***  ◄── ERASE-03 NEW ARM
                       (today: main stays NULL -> operation_utils.cpp:170
                        NULL-main guard -> MSG_ERR_NOT_SUPPORTED)
              ▼
        eeprom28c_write_init() :463
              ├── chip-id check (if chip_id > 0)
              ├── SDP-disable via eeprom28c_emit_sdp_sequence_timed()
              ├── eeprom28c_wait_for_sdp_completion()
              └── if !FLAG_SKIP_BLANK_CHECK { mem_util_blank_check } :547 ◄── ERASE-01 DELETE
                       (this call is the ONLY thing that sets
                        operation_in_progress during write-INIT ->
                        deleting it makes INIT single-shot)
              ▼
        eeprom28c_write_execute() :582  (page load + DQ7 poll + read-back verify)

        parallel, protocol 0x05:
        flash_5v_page.cpp configure_flash_5v_page :40
              ├── case CMD_ERASE :48 -> flash_5v_page_erase_execute :196
              │        ***THIS IS THE 12 V-ON-OE HARDWARE PATH***
              │        CTRL_VPP_REGULATOR_ENABLE|CTRL_VPP_VPE_DROP_ENABLE|CTRL_VPE_ENABLE
              │        -> ERASE-04 must NOT copy this into eeprom_28c.cpp
              └── flash_5v_page_write_init :72
                     ├── if FLAG_CAN_ERASE && !FLAG_SKIP_ERASE -> erase_execute
                     └── if !FLAG_SKIP_BLANK_CHECK { mem_util_blank_check } :88 ◄── ERASE-02 DELETE
```

### Recommended Project Structure

No new files are required. Every edit lands in files that already exist:

```
firestarter/                                (Arduino C++)
├── src/proms/eeprom_28c.cpp                # ERASE-01 (:547), ERASE-03 (new arm + erase op)
├── src/proms/flash_5v_page.cpp             # ERASE-02 (:88)
├── scripts/baseline/size_baseline.json      # ERASE-08 re-measure (avr_targets + native_envs)
├── scripts/check_size_baseline.py           # ONLY if a 4th named exemption is funded
├── test/native/avr/test_dispatch/
│   └── test_configure_memory.cpp            # MANDATORY inversion (Case group 4)
├── test/native/avr/test_eeprom28c_sdp/
│   └── test_eeprom28c_sdp.cpp               # MANDATORY inversion (Case 25) + new erase cases
├── test/native/avr/test_val_eeprom28c/
│   └── test_val_eeprom28c.cpp               # new configure/no-VPP case for CMD_ERASE
├── test/native/avr/test_val_5v_page/        # ERASE-02 non-regression
└── doc/PROTOCOLS.md                         # §1.6 erase-model prose (see Gap section)

firestarter_app/                             (Python host)
├── firestarter/database.py                  # ERASE-03 (:620) + ERASE-07 (:585-616 comment)
├── firestarter/chip_test.py                 # ripple: :307, :736-750 reason strings; plan shape
├── firestarter/cli_handlers.py              # ripple: :797-804 --skip-erase warning text
├── tests/test_database_conversion.py        # MANDATORY inversion (:98-117)
├── tests/test_chip_test.py                  # inversions (:419, :497)
├── tests/test_chip_test_blank_check_order.py # MANDATORY inversion (case 3, :121-125)
├── tests/test_val_wire_eeprom28c.py         # flag assertion
├── tests/test_write_skip_erase_0x0d.py      # re-examine leg 1's premise
├── tests/test_sdp_table_parity.py           # OPTIONAL new parity leg for the erase table
└── doc/protocol-id.md                       # :22 erase claim (see Gap section)
```

### Pattern 1: Delete the conditional, do not gate it differently

**What:** ERASE-01/ERASE-02 are pure deletions of a three-line `if` block, not a re-flagging.
**When to use:** Both auto-erasing protocols.
**Why this is safe, mechanically:** `mem_util_blank_check` (`memory.cpp:498-512`) is the *only* caller
of `set_operation_in_progress` on the write-INIT path, and `_execute_operation_house_keeping_func`
(`operation_utils.cpp:318-348`) re-invokes INIT **only** while `is_operation_in_progress(handle)` is
true. Deleting the call therefore makes INIT single-shot — which is *already* the shipped behaviour
whenever `FLAG_SKIP_BLANK_CHECK` is set, i.e. every `write -b` run since Phase 92. Nothing new is being
exercised.

```c
// firestarter/src/proms/eeprom_28c.cpp — CURRENT, lines 547-549
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
}   // end of eeprom28c_write_init

// AFTER (ERASE-01): the three lines are gone. Leave a short comment in their
// place naming D-07 and stating that FLAG_SKIP_BLANK_CHECK is now unread on
// this protocol, so a future reader does not "restore" it.
```

The `0x05` twin is identical:

```c
// firestarter/src/proms/flash_5v_page.cpp — CURRENT, lines 88-90
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
}   // end of flash_5v_page_write_init
```

**Do NOT** touch the four other sites — `eprom.cpp:52`, `eprom.cpp:158`, `flash_intel.cpp:128`,
`flash_nor_unlock.cpp:104`. Those protocols do **not** auto-erase per page, and D-07's policy is
explicitly scoped to `0x0D` and `0x05`.

### Pattern 2: The `CMD_ERASE` arm — copy the local shape, not the neighbour's body

**What:** ERASE-03's firmware half.
**When to use:** Exactly once, in `configure_eeprom28c`'s existing switch.

Four sibling arms exist to model on. Note that `configure_eeprom28c` assigns **no**
`firestarter_operation_init` or `_end` before its switch, so unlike `flash_nor_unlock.cpp:59-62` the new
arm has nothing to null:

```c
// firestarter/src/proms/eeprom_28c.cpp — inside configure_eeprom28c, after :228
        case CMD_ERASE:
            handle->firestarter_operation_main = eeprom28c_erase_execute;
            break;
```

Shape precedent: `flash_5v_page.cpp:48-50` (`case CMD_ERASE: main = ...erase_execute; break;`, no
`_end`), `flash_intel.cpp:92-94` (same), `flash_nor_unlock.cpp:39-42` (same, with a commented-out
`_end = memory_blank_check` — the project's own record of *not* wiring a post-erase blank check).

**What the firmware does today for `CMD_ERASE` on an arm-less protocol** (asked in Q3, answered
end-to-end): `configure_memory` (`memory.cpp:105`) calls `configure_eeprom28c`, whose switch has no
matching case, so `firestarter_operation_main` stays `NULL`. `eprom_erase` (`eprom_operations.cpp:34-38`)
first tests `FLAG_CAN_ERASE` — currently clear for algorithm 13, so it emits `MSG_ERR_NOT_SUPPORTED` and
returns *before* the op layer. If the flag were set but the arm absent, Phase 119 D-06's op-layer
NULL-main guard (`operation_utils.cpp:148-173`) would emit the *same* `MSG_ERR_NOT_SUPPORTED` id and set
`RESPONSE_CODE_ERROR`. Both refusals are already pinned: `test_eeprom28c_sdp.cpp` Case 24 (guard) and
Case 25 (this exact cell, end-to-end).

### Pattern 3: The erase body — RAM-neutral by construction

**What:** ERASE-04's implementation.
**Recommended:** reuse the existing emitter, with the sequence supplied in a form that costs no RAM.

```c
// firestarter/src/proms/eeprom_28c.cpp
//
// AT28C-family SOFTWARE chip erase. [CITED: Atmel Application Note
// "Software Chip Erase", Rev. 0544B-10/98, doc0544.pdf. Six load commands,
// tEC = 20 ms max internally timed, no external clock; "after loading the
// 6-byte code, no byte loads are allowed until the completion of the erase
// cycle"; every byte goes to FFH; software data protection REMAINS ENABLED
// after the erase.]
//
// This is DELIBERATELY NOT the datasheet's *hardware* Chip Erase mode
// (AT28C256 DS20006386B Table 6-1, p11: CE=VIL, OE=VH=12.0 V +/-0.5, WE=VIL;
// waveforms sec 6.10 p15). DIP28_28C256 pin 22 is OE, and this handler must
// never assert a VPP/VPE control bit -- see flash_5v_page_erase_execute
// (flash_5v_page.cpp:195-230) for what that path looks like and why it does
// not belong on a configure_eeprom28c chip.
static void eeprom28c_erase_execute(firestarter_handle_t* handle) {
    // Same emitter the SDP sequences use (:313) -- it calls
    // rurp_set_data_output() and routes every write through
    // handle->firestarter_set_data (memory_set_data), so the full
    // mem_util_remap_address_bus remap and the CONTROL-register rewrite on
    // every address change both apply, exactly as FIX-01 requires. Its body
    // is also the window tools/check_no_log_in_sdp_window.py scans, so this
    // call site adds NO logging inside it.
    ...six writes at {0x5555,0xAA} {0x2AAA,0x55} {0x5555,0x80}
                     {0x5555,0xAA} {0x2AAA,0x55} {0x5555,0x10}...
    delay(AT28C_TEC_MAX_MS);   // 20 ms, tEC, AN 0544B
}
```

The three supply forms, with their measured costs (F-10):

| Form | Flash | RAM | MERGE-05 consequence |
|---|---|---|---|
| Six inline `handle->firestarter_set_data(...)` calls (no table) | ~40-70 B est. | **0 B** | Fits within a flash exemption alone; no RAM exemption needed. **Recommended.** |
| `PROGMEM` table + per-entry stack copy | ~30 B table + copy code | **0 B** | Also RAM-neutral, but needs a second emitter or an inline loop; loses the shared-emitter guarantee above. |
| New `const byte_flip_t EEPROM_CHIP_ERASE[6]` in `.data` | 30 B (initializer image) | **+30 B** | **Breaks the RAM clause** (exact-equality + a fully-consumed 2 B exemption). Requires a fourth named RAM exemption. |

Address truncation on narrower parts needs **no** special handling: `0x5555` on a 13-bit part becomes
`0x1555` and `0x2AAA` becomes `0x0AAA` purely because the upper address lines are not routed — exactly
the transposition the Atmel AN requires, and exactly what the existing SDP path already relies on for
`DIP24_2816` (11-bit) and `DIP28_28C64` (13-bit). `[VERIFIED: existing SDP_BUS_CONFIGS cases 13-16 in test_eeprom28c_sdp.cpp cover DIP28_28C256, DIP28_28C64, DIP24_2816 and DIP32_28C512_EEPROM]`

### Anti-Patterns to Avoid

- **Copying `flash_5v_page_erase_execute` into `eeprom_28c.cpp`.** It is the 12 V hardware path
  (`CTRL_VPE_ENABLE` + OE→12 V). It is what D-07's hazard note is about. `check_dispatch.py` would not
  catch it (F-5).
- **Adding a `FLAG_CAN_ERASE` erase-on-write block to `eeprom28c_write_init`.** Both siblings have one
  (`flash_5v_page.cpp:78-85`, `flash_nor_unlock.cpp:92-102`) and an executor mirroring "the sibling
  pattern" will be tempted. **D-07 asks for erase as a STANDALONE step, not as part of write.** Adding
  it would make every `write` chip-erase first — a behaviour change nobody asked for, plus a 20 ms
  penalty and an SDP interaction the AN explicitly does not cover.
- **Weakening, exempting or re-baselining `check_dispatch.py`.** ERASE-04 forbids it in three separate
  words. It also is not necessary: nothing this phase does trips it (F-5).
- **Re-anchoring `size_baseline_base01.json`.** Three prior phases refused this on the record; the
  `merge05_clause` fields in `size_baseline.json` say so verbatim, three times.
- **Editing `chip_database.json`.** It is generated. No DB field changes are needed this phase.
- **Adding a new `messages.toml` id.** Three byte-identical catalog copies + `messages.h` codegen +
  `codec.py` catalog, for PROGMEM bytes against a zero-headroom target. `DBG_CHIP_ERASE` ("Chip erase")
  and `DBG_ERASE_PROM` already exist (F-12).
- **Asserting "tests byte-unchanged" as an acceptance criterion.** Four native/host test files
  *must* change (Pitfall 6); a byte-identity criterion on them would be unreachable.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Emitting a magic-address command sequence with correct bus remapping | A new emit loop, or `flash_util_byte_flipping` / `fu_flash_fast_address` | `eeprom28c_emit_command_sequence` (`eeprom_28c.cpp:292`) | It calls `rurp_set_data_output()` and routes through `handle->firestarter_set_data`, which applies `mem_util_remap_address_bus` and rewrites `CONTROL_REGISTER` on every address change. `fu_flash_fast_address` **bypasses `handle->bus_config` entirely** — that bypass was the `/WE`-inhibit defect FIX-01 fixed for 66 of 84 `0x0D` chips. Using it here would reintroduce it. |
| Knowing the 6-byte erase code | Deriving it from the SDP tables by analogy | `flash_utils.h:33-40` `FLASH_ERASE`, corroborated by Atmel AN 0544B | The nibble difference between SDP-disable (`0x20`) and chip-erase (`0x10`) is one nibble in one byte. `test_eeprom28c_sdp` Case 19 exists **specifically** because that is a recognised hazard class in this tree. Read the table; do not retype it. |
| Waiting for the erase to finish | A DQ7/DQ6 poll | `delay(20)` (tEC max, internally timed) | AN 0544B: "the device will internally time the erase operation so that no external clocks are required… The maximum time required to erase the whole chip is tEC (20 ms)" and "after loading the 6-byte code, **no byte loads are allowed** until the completion of the erase cycle." A poll *is* a byte load's read companion and the AN's Note 2 forbids traffic; `eeprom28c_wait_for_sdp_completion` issues reads and would be wrong here. |
| Refusing `CMD_ERASE` on protocols that cannot do it | A `default:` arm in `configure_eeprom28c` | The existing op-layer NULL-main guard (`operation_utils.cpp:148-173`) | Phase 119 D-05/D-06 disproved the `default:`-arm mechanism: `configure_memory` pre-sets generic mains for READ/WRITE/VERIFY *before* the protocol chain, so a blanket `default:` would refuse read and verify on all 84 rows. This is written into the code as a comment at `eeprom_28c.cpp:208-220` — read it before touching the switch. |
| Measuring the size delta | Reading a number out of a prior phase's prose | `rm -rf .pio/build/<env>` then exactly one `pio run -e <env>`, per target, transcribed | `size_baseline.json:meta.warm_vs_cold_correction` documents a 96-count warm/cold error that persisted through a whole milestone. Warm and cold differ. |
| Deciding whether a size delta is admissible | Widening a band, shrinking the fix, or re-anchoring | A new named, SHA-attributed `MERGE05_*_EXEMPTION_BYTES` constant | Three phases established this exact mechanism (96 / 210+2 / 288). All three alternatives are explicitly rejected on the record in `check_size_baseline.py`'s own module docstring. |

**Key insight:** almost every "new" piece of this phase already exists in the tree under another name,
and the project has already written down *why* the obvious shortcut is wrong. The failure mode here is
not ignorance — it is an executor reaching for the nearest sibling file and copying the 12 V path or the
`FLAG_CAN_ERASE`-on-write block because they *look* like the pattern.

---

## Runtime State Inventory

> This is a code/firmware behaviour change, not a rename or migration. The category sweep is included
> anyway because a firmware flag semantic change has a small but real runtime surface.

| Category | Items Found | Action Required |
|---|---|---|
| **Stored data** | **None.** No datastore keys the erase capability. Verified: `grep -rn "FLAG_CAN_ERASE" firestarter_app/firestarter/` reaches only `database.py` (derivation), `chip_test.py:572` (plan derivation, computed per run), `constants.py:120` (definition) and `serial_comm.py`'s DEBUG-only `_log_command_details`. **No `chip_database.json` entry carries a `flags` key** (re-verified this session against the generated DB), so `diff_db.py` identity cannot break. | none |
| **Live service config** | **None.** No external service (n8n, Datadog, Cloudflare) knows about this flag. | none |
| **OS-registered state** | **None.** No scheduled task, pm2 process or systemd unit references erase capability. | none |
| **Secrets/env vars** | **None new.** Existing test seams that a plan may set: `FIRESTARTER_DB_FILE`, `FIRESTARTER_PINOUTS_FILE`, `FIRESTARTER_SDP_SRC`, `FIRESTARTER_FW_ROOT`, `FIRESTARTER_SIZE_BASELINE`, `FIRESTARTER_CONFIG_DIR`. All read-only seams; none change. | none |
| **Build artifacts / installed packages** | **Two, both real.** (1) `firestarter/.pio/build/{uno,uno328pb,leonardo}/` must be `rm -rf`'d before every ERASE-08 measurement — a warm build gives a different figure than a cold one (`size_baseline.json:meta.warm_vs_cold_correction`). (2) Any **flashed board** on the bench still carries pre-change firmware; a `dev test` run against it would exercise the old refusal. Since ERASE-09 forbids requiring a part, this only matters if someone runs a smoke test — and per the standing operator note, bench boards are a firmware-flash testbed, so re-flashing is fine. | `rm -rf .pio/build/<env>` before each measurement; re-flash before any bench smoke test |

**The canonical question, answered:** after every file in both repos is updated, the only runtime state
still carrying the old behaviour is a physically flashed AVR board. Nothing persistent, nothing
external, nothing that needs a data migration.

---

## Common Pitfalls

### Pitfall 1: Assuming ERASE-01 changes the INIT-phase state machine
**What goes wrong:** an executor worries that deleting `mem_util_blank_check` from `write_init` will
break the multi-call INIT loop, and adds a compensating `set_operation_in_progress` /
`clear_operation_in_progress` pair, or wires an `operation_end`.
**Why it happens:** `flash_nor_unlock_write_init`'s own comment (`:76-90`) explains at length that INIT
is re-invoked "for every 2KB chunk of the stateful blank-check", which reads like the blank check is
load-bearing for the loop.
**How to avoid:** it *is* load-bearing for the loop, and that is exactly why deletion is correct and
sufficient: with no in-progress flag ever set, `_execute_operation_house_keeping_func`
(`operation_utils.cpp:337-339`) never returns `RETURN`, INIT completes in one pass, and the
`if (!is_operation_in_progress(handle))` one-time guards in the two sibling `write_init`s become
trivially true — harmless, because they now run exactly once. This is the shipped `write -b` path.
**Warning signs:** any new `set_operation_in_progress` call, any new `firestarter_operation_end`
assignment, or a `MSG_INIT_DONE` frame count that changes in a golden/stream test.

### Pitfall 2: Reaching for the sibling's erase body
**What goes wrong:** `flash_5v_page_erase_execute` (`flash_5v_page.cpp:195-230`) is 35 lines, sits in
the file the executor is *already editing for ERASE-02*, and is the only in-tree "28C-shaped erase".
It is the **12 V-on-OE hardware path** — `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE |
CTRL_VPE_ENABLE` asserted with the comment `//^OE -> 12v`.
**Why it happens:** proximity plus superficial family resemblance. Both are 5 V parallel parts on
28-pin JEDEC layouts.
**How to avoid:** the plan must state the chosen mechanism *in the task body*, with the AN 0544B
citation, and its acceptance criterion must be a **negative grep**: zero occurrences of `CTRL_VPE`,
`CTRL_VPP_REGULATOR_ENABLE` or `firestarter_set_control_register` inside `eeprom28c_erase_execute`'s
brace-matched body. `check_dispatch.py` will not catch this (F-5) — the negative assertion is the only
control.
**Warning signs:** any `firestarter_set_control_register` call, any `rurp_chip_enable`/`_disable` pair,
or a `delay(2)` cluster appearing in `eeprom_28c.cpp`.

### Pitfall 3: The RAM clause, not the flash clause, is what bites
**What goes wrong:** the plan budgets flash (leonardo: 0 B band + 96 + 210 + 288 = 594 B allowance,
currently at exactly +594 → **0 B flash headroom**) and forgets that MERGE-05's RAM clause is
**exact equality plus a single named 2 B exemption, already fully consumed** (`+2<=2=seam2`). A 6-entry
`byte_flip_t` table lands in `.data` = **+30 B RAM** (measured, F-10), which fails the RAM dimension
even if flash is exempted.
**Why it happens:** every prior v1.32 firmware phase was a flash story. Phase 151's own RAM delta was
0 B; Phase 149's was 2 B.
**How to avoid:** pick a RAM-neutral form (Pattern 3) at Wave 0, before writing code. If a `.data`
table is genuinely wanted, fund a fourth named RAM exemption in the same task, with SHA attribution,
and re-plant the tripwire fixtures on a **new `*_v153*` fixture family** (never edit the `*_v151*`
family — the standing lesson is that re-anchoring reddens four legs unless you sever onto a new
family).
**Warning signs:** `pio run -e leonardo` reporting `used 2046 bytes` instead of `2016`;
`check_size_baseline.py --policy merge05` printing a RAM line other than `+2<=2=seam2`.

### Pitfall 4: `FLAG_CAN_ERASE` restoration silently rewrites every `dev test` plan
**What goes wrong:** ERASE-03 reads as a one-line host change. It is not. `chip_test.py:572` computes
`can_erase` from the wire flag; `:615` computes
`erase_is_executable = can_erase and protocol != _PROTOCOL_FLASH4 and write_execute`; `:723` gates the
erase arm on `can_erase and protocol != _PROTOCOL_FLASH4`. Restoring the flag flips **all 84**
algorithm-13 rows from *NA erase + NA blank-check (case 3)* to *supported destructive erase + a
blank-check that moves to a different index (case 2)*.
**Why it happens:** the coupling is three functions and ~150 lines away from the edit site, behind a
comment block that argues at length for the *old* behaviour.
**How to avoid:** treat the plan-shape change as **intended** (it is: an erase that now really erases
should appear in the sweep, and blank-check-after-erase is the better oracle) and fund it explicitly —
including `tests/test_chip_test_blank_check_order.py`'s case 3 (`:121-125`) and
`tests/test_chip_test.py:497`. Also update the two reason strings that become false:
`chip_test.py:736-750` and its module constant comment at `:307`.
**Warning signs:** `pytest tests/test_chip_test_blank_check_order.py` red with an index mismatch;
`derive_plan("AT28C256", ...)` returning a step list one longer than the pinned length.

### Pitfall 5: Adding a "vacuous flag" warning for `-b` on `0x0D`
**What goes wrong:** `cli_handlers.py:797-804` warns that `--skip-erase` has nothing to skip on `0x0D`.
After ERASE-01, `-b` genuinely has nothing to skip either, and the symmetry invites a second warning.
**Why it happens:** the existing warning is a good precedent for exactly the wrong reason.
**How to avoid:** don't. `-b` becoming a no-op on `0x0D` is *the point of the phase* — warning about it
would train users to think the write needs a flag, which is the failure D-08 exists to prevent in the
release notes. Instead, note the vacuity in `write`'s docstring. Separately, the existing `--skip-erase`
warning's **text becomes false** ("the 28C family (protocol 0x0D) has no erase operation at all") and
must be corrected — the flag is still vacuous on the *write path*, but the family now has an erase op.
**Warning signs:** a new `click.echo` in `write()`; a test asserting a `-b` warning string.

### Pitfall 6: Criteria that assume tests stay unchanged
**What goes wrong:** an acceptance criterion of the form "no test file changes" or "existing suites
byte-identical" is authored, and is unreachable on arrival.
**Why it happens:** the phase reads like additive work.
**How to avoid:** four files carry assertions that are **true today and must become false**:
1. `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp:310-318` —
   `test_case_group4_0x0d_erase_and_chip_id_null_main_devtest01` asserts `CMD_ERASE` on `0x0D` leaves
   `firestarter_operation_main` **NULL** with the message *"configure_eeprom28c has no case CMD_ERASE:
   arm"*.
2. `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp:1447-1473` — Case 25 asserts
   the same precondition **and** that `op_execute_simple_operation` yields
   `RESPONSE_CODE_ERROR` + `MSG_ERR_NOT_SUPPORTED`.
3. `firestarter_app/tests/test_database_conversion.py:98-117` —
   `test_convert_at28c256_flash_eeprom_flag_can_erase_cleared` asserts `flags & FLAG_CAN_ERASE == 0`.
4. `firestarter_app/tests/test_chip_test_blank_check_order.py:121-125` — case 3 asserts the `0x0D`
   blank-check is NA at index 2.
   Plus likely: `tests/test_chip_test.py:419,497`, `tests/test_val_wire_eeprom28c.py`, and leg 1 of
   `tests/test_write_skip_erase_0x0d.py` (whose premise text names the missing erase op).
   Each inversion must **keep a positive assertion**, not merely be deleted — Case 25's shape
   (precondition → drive → response code → frame id) transfers directly to the new "erase now
   dispatches and emits the six-write stream" case.
**Warning signs:** a criterion containing "byte-identical", "unchanged", or "git diff --quiet" over a
`test/` path.

### Pitfall 7: The default-mode size gate checks native **case counts**, not just bytes
**What goes wrong:** new Unity cases are added, the AVR figures are re-measured and updated, and
`check_size_baseline.py` (default mode) still fails.
**Why it happens:** default mode is "strict byte-identity. Every AVR figure … **and every native fact
(cases, suites, all_passed)** must match the baseline EXACTLY" (its own docstring). The baseline records
`native: {cases: 163, suites: 17}` and `native_nodevtools: {cases: 163, suites: 17}`, and
`envs_agree: true` asserts the two agree.
**How to avoid:** update `avr_targets` **and** `native_envs` in the same `size_baseline.json` revision,
with a `meta` note transcribed from the cold logs. Also re-check `warnings.native.*.total_watermark`
(1166, `<=` rule, so more cases is fine unless a new macro-redefinition class appears) — and remember
`envs_agree_note` already excludes `native_pinmap_provisional` from the agreement claim.
**Warning signs:** `check_size_baseline.py` exiting 1 with a `cases` mismatch after a green `pio test`.

### Pitfall 8: Neither repo's CI runs the size gate — and the sibling layout hides cross-repo failures
**What goes wrong:** everything is green locally and in CI, and the size regression ships.
**Why it happens:** `firestarter/.github/workflows/{build,beta-build}.yml` run only `pio test -e native`
and `pio test -e native_nodevtools`. **`check_size_baseline.py` and `check_build_warnings.py` appear in
no CI leg.** Separately, `firestarter_app`'s cross-repo gates key on `../firestarter/.git` presence
(`tests/fw_presence.py:88`) — present in this devcontainer, absent in app CI, so those gates **skip**
there. The standing lesson: point the sibling root at an empty dir before a beta push to see what CI
sees.
**How to avoid:** run both size scripts as explicit plan tasks, and run the cross-repo gates once with
`FIRESTARTER_FW_ROOT` pointed at a nonexistent path to confirm they skip cleanly rather than error.
**Warning signs:** a phase artifact citing "CI green" as size evidence.

### Pitfall 9: `check_no_log_in_sdp_window.py` fails closed on a `write_init` refactor
**What goes wrong:** `eeprom28c_write_init` is restructured while removing the blank check, and the gate
errors out with "not found (or not brace-balanced)".
**Why it happens:** the checker brace-matches `eeprom28c_write_init` as a **secondary rename-tripwire**
and requires one of `_EMIT_ANCHOR_PATTERNS` (`eeprom28c_emit_sdp_sequence_timed(handle, EEPROM_SDP_DISABLE`
and two legacy forms) plus a `_WAIT_ANCHOR_PATTERNS` match inside it. It also scans
`eeprom28c_emit_command_sequence`'s and `eeprom28c_wait_for_sdp_completion`'s bodies for **any** `LOG_*`
call.
**How to avoid:** delete only the three-line `if` block; leave the SDP emit and wait calls, their names
and the function signature alone. Put **no** `LOG_*` inside `eeprom28c_emit_command_sequence` when the
erase reuses it — the erase's own reporting (if any) belongs at the *call site* in
`eeprom28c_erase_execute`, mirroring `eeprom28c_emit_sdp_sequence_timed`'s deliberately-unscanned shape
(`check_no_log_in_sdp_window.py:114-127`).
**Warning signs:** the checker printing `ERROR:` rather than `FAIL:` or `OK` — that is the fail-closed
path, and it means resolution broke, not that a log was found.

### Pitfall 10: Native trace stubs cannot prove the 20 ms wait
**What goes wrong:** a criterion asserts the erase waits tEC, proven by a native test.
**Why it happens:** it looks like a stream/trace property.
**How to avoid:** native stubs record **no time** — `delay()` is unstubbed and the SDP suites mock
`millis()` to `AlwaysReturn(0)` (which is why `AT28C_TOGGLE_POLL_MAX_READS` and
`AT28C_PAGE_POLL_MAX_READS` are *iteration counts*, not deadlines — see `eeprom_28c.cpp:106-115`). A
trace diff cannot prove a timing change. Prove the wait by **source assertion** (a grep for
`delay(AT28C_TEC_MAX_MS)` inside the brace-matched erase body plus a named constant equal to 20) and
cite the AN. Do not claim a timing proof.
**Warning signs:** a criterion phrased "the erase waits 20 ms, verified by `pio test`".

### Pitfall 11: `MERGE-05` headroom and the Caterina cliff are different numbers
**What goes wrong:** the two get conflated and a growth budget is computed from the wrong one.
**How to avoid:** they are, measured: MERGE-05 leonardo flash headroom = **0 B** (at +594 against a
594 B effective allowance). Caterina headroom = **28672 − 27500 = 1172 B**, and it is
**UNGUARDED** — quick task 260820-a7w raised `board_upload.maximum_size` to the real 32768 B on all
three AVR envs, so the linker no longer protects Caterina at all. Past 28672 B the USB bootloader is
overwritten and the board is bricked, with no gate catching it. State both figures separately in any
size record.

---

## Code Examples

### Restoring `FLAG_CAN_ERASE` (ERASE-03, host half)

```python
# firestarter_app/firestarter/database.py — CURRENT, :617-622
        simple_flags = 0
        algo = programmer_data["algorithm"]  # already computed above from protocol-id
        if full_eprom_data.get("electrical-type", "") in ("EEPROM", "Flash/EEPROM"):
            if algo not in (5, 13):
                simple_flags |= FLAG_CAN_ERASE  # FLAG_CAN_ERASE is 0x02
        programmer_data["flags"] = simple_flags

# AFTER: the tuple loses 13. Algorithm 5 STAYS excluded -- its exclusion is a
# hardware-hazard exclusion (FLAG_CAN_ERASE routes flash_5v_page_write_init ->
# flash_5v_page_erase_execute, which asserts 12 V on a 5 V part), which is a
# DIFFERENT and still-valid reason from algorithm 13's retired one.
            if algo not in (5,):
```

**Measured effect** (this session, against the committed generated DB):

```
algorithm==13 rows: 84   (etype: EEPROM 66, Flash/EEPROM 18)
would gain FLAG_CAN_ERASE: 84    not eligible: 0
support_status: supported 75, adapter-required 9
pinouts: DIP28_28C64 35, DIP24_2816 19, DIP32_28C512_EEPROM 18, DIP28_28C256 12

before:  AT28C256 algo=13 etype='EEPROM'        flags=0x00  can_erase_bit=False
         CAT28C512 algo=13 etype='Flash/EEPROM' flags=0x00  can_erase_bit=False
```

**The 66/18 split, and why it does not affect the flag** (Q5): `tools/build_db.py::classify` arm 2
(`:375-390`) **promotes** 66 rows that arrive upstream as protocol `0x07`/`0x08`/`0x0B` on a 5 V-EEPROM
pinout cluster to `("EEPROM", 0x0D)`; arm 4 (`:400-402`) passes through the 18 rows that are natively
upstream `0x0D` as `("Flash/EEPROM", 0x0D)`. Since `FLAG_CAN_ERASE` derives from **`electrical-type`
only**, and both arms produce a qualifying type, promotion is irrelevant to the flag and **all 84 rows
gain it uniformly**. The promoted rows' `programming.*` fields belonging to another algorithm matters for
`page_size` (Phase 149 D-04 left the 66 on the conservative floor for exactly that reason) — it does
**not** matter here. The 9 `adapter-required` rows never reach the wire at all: `chip_resolver`
`ChipNotImplementedError`s on any `support_status != "supported"` before a byte is emitted.

### The stale comment (ERASE-07)

```python
# firestarter_app/firestarter/database.py :585-600 (excerpt) -- CURRENT, FALSE
        # Algorithm 13 / protocol 0x0D (AT28C / 28C-family SDP EEPROMs) --
        # Phase 121 D-12: the firmware's configure_eeprom28c handler
        # (firestarter/src/proms/eeprom_28c.cpp) has no erase operation at
        # all, so advertising FLAG_CAN_ERASE for these 84 chips is a false
        # capability statement. ...
        # REVERSAL RECORD (Phase 121 D-12, ...): ... the 0x0D firmware path
        # genuinely never reads FLAG_CAN_ERASE -- that part of the old note
        # remains true -- ...
```

Both italicised claims become false. The correction must state (a) Phase 153 implements the software
6-byte chip erase, so the capability statement is now **true**; (b) the `0x0D` path **does** read
`FLAG_CAN_ERASE`, at `eprom_operations.cpp:36`, as the standalone `erase` precondition; and (c) it must
**preserve** the still-valid algorithm-5 rationale, which sits in the same comment block at `:580-586`
and is a live hardware-hazard argument, not a retired one. The correction is a **third recorded
reversal of a reversal** — write it in the project's established mechanism-corrected/intent-satisfied
voice rather than as a failure.

### `info`'s row — already correct (ERASE-06)

```python
# firestarter_app/firestarter/ic_layout.py :578-585 -- NO EDIT NEEDED
        # D-02: "Can be erased" derived from electrical.type, NOT protocol_id.
        if etype in ("EEPROM", "Flash/EEPROM"):
            output_data["can_erase_str"] = "yes (electrically erasable)"
        elif etype == "UV-EPROM":
            output_data["can_erase_str"] = "no (UV erase only)"
        # SRAM and absent/unknown: no can_erase_str row
```

`etype` for AT28C256 is `"EEPROM"`, so this already renders
`Can be erased: yes (electrically erasable)` (rendered at `eprom_info.py:254-255`) while the wire flag
is `0x00` and `firestarter erase AT28C256` returns `ERROR: Not supported` — the exact contradiction on
gh#20's 2026-08-07 paste. ERASE-03 removes it with **zero** `ic_layout.py` change. Note that
`_interpret_flags` (`:222-241`) reads a *different* value — the DB's upstream `info-flags` bit `0x10` —
so it is a third axis and is already consistent. **ERASE-06 should be planned as an assertion task, not
an edit task.**

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| `write -b` implied `--skip-erase` | Decoupled; `-b` skips only the blank check | Phase 92 (`cli_handlers.py:361-368`) | **The standing memory note "`write -b` SKIPS ERASE" is STALE.** It was true pre-Phase-92. Today `-b` skips only the blank check; `--skip-erase` is an explicit opt-in with `default=False`. Do not plan around the old behaviour. |
| Silent OK for unimplemented (cmd, protocol) cells | One generic op-layer NULL-main guard emitting `MSG_ERR_NOT_SUPPORTED` | Phase 119 D-06 / Plan 119-07 (`operation_utils.cpp:148-173`) | A `default:` arm inside `configure_eeprom28c` is a **disproven** mechanism; the comment at `eeprom_28c.cpp:208-220` says why. |
| `FLAG_CAN_ERASE` set for `0x0D` (inert) | Cleared for algorithms 5 and 13 | Phase 121 D-12 (`database.py:617`) | This phase reverses the `13` half. The `5` half stays — its reason is a live hazard. |
| Hardcoded `PAGE_SIZE 64` in the `0x0D` handler | Wire-delivered `page-size` with a validated power-of-two mask | Phase 149 (`eeprom_28c.cpp:eeprom28c_page_mask`) | Cost 210 B flash + 2 B RAM, funded as a named exemption. Sets the precedent this phase's size task follows. |
| `flash_total` = bootloader-reduced (leonardo 28672) | `flash_total` = real 32768 on all three AVR envs | Quick task 260820-a7w, 2026-08-20 | **The linker no longer protects Caterina.** Leonardo's real cliff is 28672 B and is unguarded. `flash_free` 5268 B is misleading — 4096 B of it is Caterina's forfeited region. |
| Protection state readable claim | `dev lock-status` reads `0x05`/`0x06` protection; `0x0D` SDP state remains **unreadable** | Phase 151 | An erase on `0x0D` still cannot be verified by reading protection state. Do not plan an oracle that depends on it. |

**Deprecated/outdated:**
- The memory note *"`write -b` SKIPS ERASE, not just blank-check"* — superseded by Phase 92 (above).
- `firestarter/doc/PROTOCOLS.md` §1.6's erase model and `firestarter_app/doc/protocol-id.md:22` — both
  become false the moment ERASE-03 lands (see Gap section).
- `firestarter_app/firestarter/cli_handlers.py:797-804` warning text and
  `chip_test.py:307,736-750` reason strings — become false (see Gap section).

---

## Gap: claims that become false and are not covered by any ERASE requirement

Not requirements, but the planner should decide on each. All four are one-line-to-one-paragraph text
corrections; leaving them is a documented false claim in the shipped artifact, which is precisely the
class D-08 reordered the phases to avoid.

| # | Site | Current false claim | Gated by |
|---|---|---|---|
| G-1 | `firestarter_app/firestarter/cli_handlers.py:797-804` | *"the 28C family (protocol 0x0D) has no erase operation at all"* — printed to the user on `write --skip-erase` | `tests/test_write_skip_erase_0x0d.py` leg 1 asserts this string |
| G-2 | `firestarter_app/firestarter/chip_test.py:307` and `:745-750` | Module comment and the `dev test` step reason *"protocol 0x0D (28C family) has no erase operation; each page write auto-erases internally"* — appears in every diagnostic report | `tests/test_chip_test.py` |
| G-3 | `firestarter/doc/PROTOCOLS.md:305` §1.6 "Erase model" | An entire paragraph: *"Firmware implements **no erase operation at all** for protocol `0x0D`… the blank-check skip (`-b`) … is **required** to write a non-blank AT28C part"* | `test_dispatch_mirror.py` parses only §0's table, **not** this prose — so nothing catches it |
| G-4 | `firestarter_app/doc/protocol-id.md:22` | *"this family has **no erase operation at all** — the host clears the `FLAG_CAN_ERASE` advertisement for it (Phase 121 D-12)"* | no gate |

G-3 is the highest-value correction: it is the document `test_dispatch_mirror.py` calls "the canonical
source of truth", and its `-b`-is-required sentence is the exact recommendation D-08 refused to publish.

Also note for the D-15 record corrections: `.planning/ROADMAP.md:163` **has already been amended** to
"three firmware-touching workstreams" naming 149/151/153. What remains stale is
**`.planning/PROJECT.md:44-45`** (*"Mostly host-side; one firmware-touching workstream (the page-size
seam)"*), the workstream table at `PROJECT.md:80-88` (needs a row for 153; workstream 4's description
updates), and `.planning/ROADMAP.md:37` (the milestone index line still says "two"). `ROADMAP.md:482`
already states the correction is owed.

---

## Wave / File-Conflict Map

One writer per file. Dependency direction: the host `FLAG_CAN_ERASE` restoration and the firmware
`CMD_ERASE` arm are a **matched pair** — landing the host half alone makes `firestarter erase AT28C256`
pass the host, pass `eprom_erase`'s precondition, and then hit the op-layer NULL-main guard (still
refused, still honest, but with a different error path). Landing the firmware half alone leaves the arm
unreachable. Either order is safe; both must land in the same phase.

| File | Repo | Requirement(s) | Can parallelise with | Serialises against |
|---|---|---|---|---|
| `src/proms/eeprom_28c.cpp` | fw | ERASE-01, ERASE-03, ERASE-04 | everything in `firestarter_app/` | **Itself only** — ERASE-01's deletion and ERASE-03/04's addition are in the same file and should be ONE task, not two waves. Also serialises against the two host gates that scan it (`check_no_log_in_sdp_window.py`, `test_sdp_table_parity.py`), which must run *after*. |
| `src/proms/flash_5v_page.cpp` | fw | ERASE-02 | `eeprom_28c.cpp` (disjoint) | `test_val_5v_page` regeneration |
| `firestarter/database.py` | host | ERASE-03 (host half), ERASE-07 | `cli_handlers.py`, `chip_test.py`, `ic_layout.py` | **Nothing else in v1.32 writes it** — Phase 148 (closed) was the last writer. Free. |
| `firestarter/cli_handlers.py` | host | G-1 | `database.py`, `chip_test.py` | **Phase 151 was the milestone's other writer and is CLOSED**; Phase 152 was going to touch it and D-08 explicitly reordered to avoid the collision. Free now, but 152 must land after. |
| `firestarter/chip_test.py` | host | G-2 + Pitfall-4 ripple | `database.py`, `cli_handlers.py` | free |
| `firestarter/ic_layout.py` | host | ERASE-06 | — | **NO EDIT.** Assertion only. |
| `test/native/avr/test_dispatch/test_configure_memory.cpp` | fw | ERASE-03 inversion | other test files | must land in the same wave as the arm, or `pio test -e native` is red |
| `test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` | fw | ERASE-03/04 inversion + new cases | other test files | same wave as the arm |
| `test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` | fw | new configure/no-VPP case | other test files | same wave |
| `tests/test_database_conversion.py`, `test_chip_test*.py`, `test_val_wire_eeprom28c.py`, `test_write_skip_erase_0x0d.py` | host | inversions | each other (distinct files) | same wave as `database.py` |
| `scripts/baseline/size_baseline.json` | fw | ERASE-08 | — | **LAST wave, single writer.** Depends on every code change being final. |
| `scripts/check_size_baseline.py` + `tests/test_check_size_baseline.py` | fw | ERASE-08 only if a 4th exemption is funded | — | same wave as the baseline; new `*_v153*` fixture family |
| `.planning/PROJECT.md`, `.planning/ROADMAP.md` | meta | D-15 | everything (different repo) | must not collide with Phase 152's own PROJECT.md edits — 153 lands first per D-08 |
| `doc/PROTOCOLS.md` (fw), `doc/protocol-id.md` (app) | both | G-3, G-4 | everything | free |

**Suggested wave shape:**
- **Wave 0** — decide and record the erase mechanism (RAM-neutral vs. exemption); capture the cold
  pre-change baseline for all three AVR targets; capture the pre-change host suite counts.
- **Wave 1** — firmware: `eeprom_28c.cpp` (ERASE-01 + 03 + 04) ‖ `flash_5v_page.cpp` (ERASE-02).
- **Wave 2** — firmware tests: the two mandatory inversions + new erase cases (three distinct files, all
  parallel).
- **Wave 3** — host: `database.py` (ERASE-03/07) ‖ `chip_test.py` (G-2) ‖ `cli_handlers.py` (G-1), then
  host test inversions.
- **Wave 4** — docs: `doc/PROTOCOLS.md` ‖ `doc/protocol-id.md` ‖ meta `PROJECT.md`/`ROADMAP.md`.
- **Wave 5** — ERASE-08: cold triple-target re-measure, `size_baseline.json` revision (avr_targets **and**
  native_envs), `--policy merge05` run against BASE-01, and (if needed) the fourth named exemption with
  re-planted `*_v153*` tripwire fixtures.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| PlatformIO CLI (`pio`) | firmware build + native tests + ERASE-08 measurement | ✓ | 6.1.19 (`/usr/local/bin/pio`) | — |
| `avr-gcc` / `avr-nm` toolchain | AVR build; the `.data` vs `.text` section measurement | ✓ | 7.3.0 (`~/.platformio/packages/toolchain-atmelavr/bin/`) | — |
| `.pio/build/{uno,uno328pb,leonardo}` warm caches | — (must be **deleted** before measuring) | ✓ present | — | `rm -rf` each before measuring |
| Python 3 + pytest + `.[test]` extra | host tests | ✓ | devcontainer python3.12 — **NOT CI's 3.11** | `uv venv --python 3.11` recipe (needs `UV_CACHE_DIR`); the watermark gate can fail **open** under 3.12 |
| `pypdf` (+ `cryptography`) | reading `datasheets/AT28C256.pdf` (AES-encrypted; `pdftotext` absent) | ✓ | 6.16.1 | — (already used this session) |
| Network (microchip.com) | fetching Atmel AN doc0544 | ✓ | — | **Already fetched and read this session** — the sequence and tEC are recorded verbatim in this document, so no plan task needs the network |
| Sibling `../firestarter/.git` marker | `firestarter_app`'s 8 cross-repo gates | ✓ present | — | Gates **skip** when absent (correct, by design since Phase 123 BASE-02) — this is why app CI does not run them |
| An AT28C256 part | **NOTHING** | ✗ | — | **ERASE-09 forbids requiring one.** Every criterion in this document is bench-free. |
| A flashed AVR board | optional smoke test only | ✓ (bench boards are a standing flash testbed) | — | skip; no criterion depends on it |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** an AT28C part — and its absence is a *requirement*, not a gap.

---

## Validation Architecture

### Test Framework

| Property | Value |
|---|---|
| Firmware framework | PlatformIO + Unity (`pio test`) |
| Firmware config file | `firestarter/platformio.ini` (`[env:native]` at :97, `test_filter` allowlist at :130-151 — 17 suites) |
| Firmware quick run | `pio test -e native -f native/avr/test_eeprom28c_sdp` (single suite) |
| Firmware full suite | `pio test -e native` then `pio test -e native_nodevtools` (both must report 163→N cases / 17 suites, `envs_agree`) |
| Host framework | pytest (`pyproject.toml:105-107`, `addopts = "-ra -q"`) |
| Host quick run | `pytest tests/test_database_conversion.py tests/test_chip_test_blank_check_order.py -o addopts="" -q` (**`-o addopts=""` is required** — doubling `-q` suppresses the count line) |
| Host full suite | `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` (CI's exact leg; current 82.92 %, floor 70) |
| Host static gates | `ruff check firestarter/ tests/`; `ruff format --check firestarter/ tests/`; `python tools/check_mypy_watermark.py` (watermark 35, current 33) |
| Cross-repo gates | `python tools/check_dispatch.py`; `python tools/check_no_log_in_sdp_window.py`; `pytest tests/test_sdp_table_parity.py tests/test_dispatch_mirror.py` |
| Size gates | `python scripts/check_size_baseline.py --avr-log <env>=<log>` (default byte-identity) and `python scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log …` (band mode — **always name BASE-01 explicitly**) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|---|---|---|---|---|
| ERASE-01 | No `mem_util_blank_check` call remains in `eeprom28c_write_init`; write-INIT is single-shot | source-scan + unit | `grep -c 'mem_util_blank_check' firestarter/src/proms/eeprom_28c.cpp` → expect **1** (the `CMD_BLANK_CHECK` arm at :227 only); plus a native case driving `CMD_WRITE` init with `FLAG_SKIP_BLANK_CHECK` **clear** and asserting zero read strobes at addresses ≥ 0 before the SDP stream | ❌ Wave 2 (new native case in `test_eeprom28c_sdp`) |
| ERASE-01 | The `0x0D` write stream is otherwise unchanged | golden/stream | `pio test -e native -f native/avr/test_eeprom28c_sdp` — Cases 1-5 (`*_stream_matches_fixed`) must stay green **unmodified** | ✅ `test_eeprom28c_sdp.cpp:1708-1712` |
| ERASE-02 | Sibling located and removed; `0x05` write path otherwise intact | source-scan + unit | `grep -n 'FLAG_SKIP_BLANK_CHECK' firestarter/src/proms/flash_5v_page.cpp` → expect **0 hits**; `pio test -e native -f native/avr/test_val_5v_page` | ✅ suite exists; ❌ new negative case Wave 2 |
| ERASE-03 (fw) | `CMD_ERASE` on `0x0D` sets a non-NULL main | unit | `pio test -e native -f native/avr/test_dispatch` — Case group 4 **inverted** to `TEST_ASSERT_NOT_NULL` | ✅ exists at `test_configure_memory.cpp:310` (must invert) |
| ERASE-03 (fw) | End-to-end: `CMD_ERASE` dispatches, emits the six-write stream, returns `RESPONSE_CODE_OK`, emits **no** `MSG_ERR_NOT_SUPPORTED` | unit/stream | `pio test -e native -f native/avr/test_eeprom28c_sdp` — Case 25 **inverted** + a new stream-equality case | ✅ exists at `:1390` (must invert) |
| ERASE-03 (fw) | `configure_eeprom28c`'s `CMD_ERASE` arm asserts no VPP | unit | new case in `test_val_eeprom28c.cpp` modelled on `test_eeprom28c_blank_check_configure_no_vpp` (`:399`) | ❌ Wave 2 |
| ERASE-03 (host) | All 84 algorithm-13 rows carry `FLAG_CAN_ERASE`; algorithm-5 rows still do **not**; UV-EPROM still does not | unit | `pytest tests/test_database_conversion.py -o addopts="" -q` — `:98-117` inverted, `:120-131` (W29C040, algo 5) and `:89-95` (M27C512 UV) unchanged as negative controls | ✅ (one inversion, two controls already green) |
| ERASE-03 (host) | Exhaustive: **exactly 84** rows gain the flag and 0 non-13 rows change | unit | new leg iterating all 746 DB rows, modelled on `tests/test_page_size_invariants.py` leg 6 | ❌ Wave 3 |
| ERASE-04 | The emitted sequence equals AN 0544B's six pairs, in order | unit/stream | native stream-equality case asserting the six `(address, byte)` writes; plus optional parity leg in `tests/test_sdp_table_parity.py` if a named table is used | ❌ Wave 2 |
| ERASE-04 | The erase stream **diverges** from SDP-disable at exactly the terminal byte (`0x10` vs `0x20`) — the one-nibble hazard class | unit/stream | new case modelled verbatim on `test_case18/19_..._diverges_at_exact_index` (`:1082-1124`), asserting an exact divergence index, **never `!= -1`** | ❌ Wave 2 (Case 19 is the template) |
| ERASE-04 | **No** VPP/VPE control-register write anywhere in the erase path | source-scan (negative) | brace-match `eeprom28c_erase_execute` and assert 0 occurrences of `CTRL_VPE`, `CTRL_VPP_REGULATOR_ENABLE`, `firestarter_set_control_register` | ❌ Wave 2 — this is the **primary** GATE-03 control |
| ERASE-04 | `check_dispatch.py` unweakened, unexempted, un-re-baselined | source + behaviour | `git diff --quiet -- tools/check_dispatch.py` at phase end **and** `python tools/check_dispatch.py` exits 0 **and** `pytest tests/test_check_dispatch_invariants.py` green (proves the fixture-only 5 V-family invariant still fires) | ✅ all three exist |
| ERASE-05 | `blank` still reaches `mem_util_blank_check` and still reports not-blank correctly | unit | `pytest tests/test_characterization.py tests/test_eprom_operations.py -k blank -o addopts="" -q`; firmware side: `pio test -e native -f native/avr/test_val_eeprom28c` case `test_eeprom28c_blank_check_configure_no_vpp` (`:399`) unchanged | ✅ both exist — **non-regression, no new work** |
| ERASE-06 | `info`'s row and the wire flag agree for an algorithm-13 chip | unit | new leg asserting `build_specifications(...)["can_erase_str"].startswith("yes")` **and** `convert_to_programmer(...)["flags"] & FLAG_CAN_ERASE` for the same chip — one assert pair, both directions | ❌ Wave 3 (`tests/test_ic_layout.py`) |
| ERASE-07 | The comment no longer asserts the two false claims | source-scan | `grep -c 'has no erase operation at' firestarter_app/firestarter/database.py` → **0**; `grep -c 'never reads FLAG_CAN_ERASE' …` → **0**; and the algorithm-5 rationale still present | ❌ Wave 3 (grep criteria are sufficient) |
| ERASE-08 | Constants lockstep | source-scan | `python -c` parity check of `FLAG_CAN_ERASE`/`FLAG_SKIP_ERASE`/`FLAG_SKIP_BLANK_CHECK`/`CMD_ERASE`/`CMD_BLANK_CHECK` between `firestarter/include/firestarter.h` and `firestarter_app/firestarter/constants.py`; `pytest tests/test_revision_constants_parity.py` | ✅ exists |
| ERASE-08 | Cold flash/RAM on all three AVR targets, vs pre-change baseline | measurement | per target: `rm -rf .pio/build/<env> && pio run -e <env> 2>&1 \| tee <log>`, then `python scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log <env>=<log>` | ✅ script exists |
| ERASE-08 | Native case/suite counts recorded and agreeing | measurement | `pio test -e native` + `pio test -e native_nodevtools`, then `python scripts/check_size_baseline.py --native-log native=<log> --native-log native_nodevtools=<log>` | ✅ |
| ERASE-08 | Tripwire still armed above any new allowance | unit | `pytest tests/test_check_size_baseline.py -o addopts="" -q` with a **new `*_v153*` fixture family**, each fixture re-derived from `allowance+1` and **observed** to fail | ✅ suite exists (new family needed only if an exemption is funded) |
| ERASE-09 | No `support_status` write, no graduation | source + gate | `python tools/check_no_community_support_status_write.py`; `python tools/check_diagnostic_report_claims.py`; `git diff -- firestarter/data/chip_database.json` empty | ✅ all exist |
| ERASE-09 | The phrase "software-proven and unvalidated on silicon" appears in the phase's own record | source-scan | `grep -c 'software-proven and unvalidated on silicon' .planning/phases/153-*/` ≥ 1 | ❌ Wave 5 (artifact) |

### Sampling Rate

- **Per task commit (firmware):** `pio test -e native -f native/avr/<touched suite>` (< 30 s per suite).
- **Per task commit (host):** `pytest tests/<touched file> -o addopts="" -q` (< 30 s).
- **Per wave merge (firmware):** `pio test -e native` **and** `pio test -e native_nodevtools` (both must
  agree) + `pio run -e leonardo` for an early flash/RAM read.
- **Per wave merge (host):** `ruff check` + `ruff format --check` + `python tools/check_mypy_watermark.py`
  + `pytest tests/ --cov=firestarter --cov-fail-under=70`.
- **Phase gate:** all of the above, plus `python tools/check_dispatch.py`,
  `python tools/check_no_log_in_sdp_window.py`, the three cold AVR builds, both
  `check_size_baseline.py` modes, and `python scripts/check_build_warnings.py`.

### Wave 0 Gaps

- [ ] **Decision record** naming the erase mechanism (inline / PROGMEM / `.data`+exemption) with the
      measured 30 B RAM figure cited — this is a gap because it is a *precondition* to writing code, and
      choosing wrong is a MERGE-05 blocker (not a note).
- [ ] `firestarter/scripts/baseline/` pre-change cold logs for uno / uno328pb / leonardo — reproduced for
      leonardo this session (27500 / 2016, byte-identical to the committed baseline), **not** yet for
      uno / uno328pb.
- [ ] Pre-change host suite count + coverage figure, captured once with `-o addopts=""`.
- [ ] New native case: `CMD_ERASE` on `0x0D` dispatches (Wave 2, `test_configure_memory.cpp` inversion).
- [ ] New native case: erase stream equality against the six AN-0544B pairs
      (`test_eeprom28c_sdp.cpp`).
- [ ] New native case: erase stream diverges from SDP-disable at an exact index
      (`test_eeprom28c_sdp.cpp`, Case 19 template).
- [ ] New native case: `CMD_ERASE` configure asserts no VPP (`test_val_eeprom28c.cpp`).
- [ ] New native negative case: `0x05` write-init no longer blank-checks (`test_val_5v_page.cpp`).
- [ ] New host leg: exhaustive 84-row flag assertion over the generated DB (`test_database_conversion.py`
      or a new module modelled on `test_page_size_invariants.py`).
- [ ] New host leg: `info` row ⇄ wire flag agreement, both directions (`test_ic_layout.py`).
- [ ] `*_v153*` size-tripwire fixture family — **only if** a fourth named exemption is funded.

Framework install: **none needed.** Both frameworks are present and green.

---

## Security Domain

`security_enforcement` is not set to `false` in `.planning/config.json`, so this section is required. The
threat model here is **physical/hardware**, not network — the applicable ASVS categories are mostly
inapplicable, and saying so explicitly is more useful than forcing a mapping.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | No identity surface. Local CLI over USB serial. |
| V3 Session Management | no | Stateless per-operation serial connection (`EpromOperator.comm` is torn down after every call). |
| V4 Access Control | no | No multi-user model. |
| V5 Input Validation | **yes** | Two live surfaces: (a) `--sector-address` on `erase` → `address_str` → the host address parser (`tests/test_address_parser.py`); this phase's `0x0D` erase is device-global chip erase and must **ignore** a sector address rather than pass it to the bus. (b) The wire `page-size` / `flags` values arriving at `json_parser.c` — unchanged this phase. Existing control: `eeprom28c_page_mask`'s reject-zero-then-power-of-two validation (`eeprom_28c.cpp:562-580`), and `eeprom28c_check_chip_id`'s `mem_size < 64` underflow guard (`:243-252`), which exists precisely because a wrapped address would "drive 12 V on A9 of an arbitrary address". |
| V6 Cryptography | no | None involved. |
| **Hardware safety (project-specific, the real category)** | **yes** | See below. This project's `check_dispatch.py`, `rurp_pinmap_guard.h`, and the `_FAMILY_VPP_INVARIANTS` table are its ASVS-equivalent. |

### Known Threat Patterns for AVR firmware driving a 5 V parallel EEPROM socket

| Pattern | STRIDE | Standard Mitigation |
|---|---|---|
| **12 V asserted on a 5 V part's pin** (the DIP28_28C256 OE/pin-22 hazard D-07 names) | Destruction of the user's chip / shield | **This phase's central control.** Implement the software path only; assert zero `firestarter_set_control_register` calls in the erase body by brace-matched source scan. Note honestly that `check_dispatch.py`'s GATE-03 guard (`handler == "configure_eprom" and pinout in no_vpp_pin_pinouts`) operates at the DB/dispatch layer and **cannot** detect a handler-body register write — the source scan is the only real control, and `_FAMILY_VPP_INVARIANTS["configure_eeprom28c"] = (0, 6000)` is fixture-proven, not DB-checked. |
| A capability advertised that the firmware cannot perform | Repudiation / false capability | ERASE-03/06 close the current instance in the *honest* direction (make the firmware do more), reversing Phase 121 D-12's make-the-host-claim-less. |
| A destructive operation reporting success having done nothing (phantom erase) | Spoofing (false green) | The op-layer NULL-main guard (`operation_utils.cpp:170`) exists for exactly this. Adding the `CMD_ERASE` arm removes `0x0D` from its coverage — so the **new** case must prove the arm really emits the stream, not merely that it dispatches. `dev test`'s destructive-step gate (`chip_test.py` `locked_destructive`) still applies. |
| A user's non-blank part silently corrupted by a skipped erase | Tampering | The Phase 92 defect class. Not reintroduced: on `0x0D` the silicon auto-erases per page and the write path read-back-verifies (`eeprom28c_verify_page_readback`); on `0x05` the erase remains gated by `FLAG_CAN_ERASE`, which the host still clears for algorithm 5. |
| Bricking the leonardo USB bootloader by linking over Caterina | Denial of service (unrecoverable without ISP) | Caterina headroom is **1172 B** and **UNGUARDED** since quick task 260820-a7w raised `flash_total` to 32768. Record it as a distinct figure from MERGE-05's 0 B. |
| A gate that cannot fail (hollow detector) | Spoofing (false assurance) | This project's own recorded tech debt (v1.12's hollow GATE-03). Every new gate leg in this phase must be **observed** to fail on a planted violation before being trusted — the standing lesson: a pre-authored leg is not known reachable until it is seen to pass. |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | Six inline `set_data` calls cost roughly 40-70 B flash and 0 B RAM | Architecture Pattern 3, alternatives table | **Only the 0 B RAM part is measured-certain** (no `.data` object is created). The flash figure is an estimate from comparable in-tree ops (Phase 149's whole page-size seam = 210 B; Phase 151's whole lock-status op = 288 B). If the real cost exceeds leonardo's 0 B allowance — which it will, since the allowance is zero — a **named flash exemption is required regardless of form**. Wave 0's measurement task is what resolves this; no plan should treat the estimate as a budget. |
| A2 | LTO does not merge identical internal-linkage `byte_flip_t` tables across TUs | Alternatives table | Partially measured: the leonardo ELF carries **two** surviving copies of `FLASH_ENABLE_WRITE` (`.lto_priv.92`, `.lto_priv.93`), which proves non-merging for at least that table. Whether a *third* copy of `FLASH_ERASE` would also survive is inferred from that, not directly measured. If LTO did merge it, referencing `FLASH_ERASE` from `eeprom_28c.cpp` would be free — which would be good news, not bad. Cheap to check: build the spike and re-run `avr-nm -S`. |
| A3 | The `0x0D` software chip erase does not require a preceding SDP-disable | Don't Hand-Roll / Pattern 3 | AN 0544B states SDP *remains enabled after* the erase but says nothing about a precondition. On an SDP-protected part, if the command decoder does **not** recognise the erase code without an unlock prefix, the erase would silently do nothing. Impact: an erase that reports OK having erased nothing — the exact phantom-erase class Phase 121 D-12 fought. **Mitigation the plan should take:** either emit SDP-disable before the erase sequence (reusing `eeprom28c_emit_sdp_sequence_timed`, ~0 extra bytes) or state the limitation explicitly in the erase op's comment and in the phase record. Recommend the former; it is strictly safer and the code already exists. **This is the single most important open question in this document.** |
| A4 | `delay(20)` is sufficient for tEC across the whole `0x0D` family, not just AT28C256 | Pattern 3 | AN 0544B's 20 ms is the family figure ("Chip Erase Cycle Time 20 ms Max") and applies to Atmel parallel EEPROMs generally, but the 84-row bucket spans AMD, Microchip, NEC, Xicor, Catalyst and Winbond variants. A part with a longer tEC would return non-blank after a "successful" erase. Low risk (the value is a family maximum, and blank-check is a separate step the user can run), but worth one sentence in the record. |
| A5 | No CI leg needs changing | Pitfall 8, Environment | Verified by reading both `firestarter/.github/workflows/{build,beta-build}.yml` (only `pio test -e native` / `native_nodevtools`) and `firestarter_app/.github/workflows/ci.yml`. If a plan adds a **new** `pio` environment or a test outside `tests/`, this stops holding. |
| A6 | ERASE-06 needs no `ic_layout.py` edit | ERASE-06 row, Code Examples | Verified by reading `:578-585` and measuring `convert_to_programmer` output for four algorithm-13 chips. The residual risk is interpretive: if "agrees with the wire flag" is read as *"`info` must derive from the wire flag"* rather than *"the two must not contradict"*, a real edit is owed. Recommend the plan state which reading it adopts. Given D-07's decomposition says the row *"contradicts the wire flag"* — i.e. names the contradiction, not the derivation — the no-edit reading is the intended one. |
| A7 | The `0x0D` erase should ignore `--sector-address` | Security Domain V5 | The software chip erase is device-global by construction (AN 0544B: "the entire device"). `erase`'s `-s/--sector-address` exists for `0x06` sector erase (`flash_nor_unlock_sector_erase`). Passing an address through on `0x0D` would be meaningless at best. Not verified against any existing test — the plan should add one negative leg or state the disposition. |

---

## Open Questions

1. **Does the software chip erase need an SDP-disable prefix on a protected part?** (= A3)
   - *What we know:* AN 0544B Rev. 0544B-10/98 says SDP "is still enabled even after the software chip
     erase is performed", and that after the 6-byte code no byte loads are allowed until completion. The
     SDP-disable code shares the first five of the six writes and differs only in the terminal byte
     (`0x20` vs `0x10`), which strongly suggests both are decoded by the same command state machine and
     that the erase code is recognised regardless of protection state.
   - *What's unclear:* the AN does not state it, and no datasheet page read this session does either.
   - *Recommendation:* emit SDP-disable first, reusing `eeprom28c_emit_sdp_sequence_timed` (already
     present, already gate-compatible, and `eeprom28c_write_init` proves the pattern). Cost is small and
     the failure mode it removes — a phantom erase reporting OK — is the exact class this project has
     twice fought. If the plan instead declines, it must say so in the erase op's comment and in the
     phase record, and must not claim the erase is proven for protected parts.

2. **Does `sdp_capability`'s 43-ALLOW / 41-REFUSE partition gate the erase?**
   - *What we know:* `sdp_capability(name, db)` is a fail-closed, count-pinned decision source consumed
     by `chip_test.py`'s SDP leg and by `write`'s D-04 auto-set of `FLAG_SKIP_SDP_UNLOCK`.
   - *What's unclear:* if Q1 resolves to "emit SDP-disable before erase", then on a capability-refused
     chip the erase inherits the same question `write` already answers by auto-setting the skip flag and
     printing a mandatory report line.
   - *Recommendation:* keep `erase` out of the auto-set path (it takes no `--skip-sdp-unlock`, by the
     D-17 reasoning that scopes that flag to `write` only) and state the disposition. Do not silently
     extend the auto-set.

3. **Which of the four "becomes false" text sites are in scope?** (G-1…G-4)
   - *Recommendation:* all four. G-3 (`firestarter/doc/PROTOCOLS.md` §1.6) is the one that most needs it —
     its "`-b` is **required** to write a non-blank AT28C part" sentence is the exact recommendation D-08
     reordered the phases to keep out of the public record.

4. **Should `erase -b`'s post-erase blank check be wired on `0x0D`?**
   - *What we know:* `erase`'s `-b` sets `FLAG_SKIP_BLANK_CHECK` when *absent* (inverse polarity from
     `write`'s). `configure_eprom` honours it via `operation_end` (`eprom.cpp:52-55`); neither
     `flash_5v_page` nor `flash_nor_unlock` does.
   - *Recommendation:* do not wire it — ERASE-05 keeps `blank` as its own step, an `operation_end` arm
     costs bytes against a zero-headroom target, and the two closest siblings both decline. State the
     decision so `erase -b` on `0x0D` is documented as a no-op rather than discovered as one.

5. **Is a fourth named MERGE-05 exemption acceptable to the operator, or must this phase be byte-neutral?**
   - *What we know:* leonardo has **0 B** flash and **0 B** RAM MERGE-05 headroom. Three exemptions
     (96 / 210+2 / 288) are already stacked, and each was individually adjudicated. Any code addition
     needs a fourth flash exemption; only a `.data` table needs a RAM one.
   - *Recommendation:* fund a flash-only exemption, sized from Wave 0's actual measurement, and design
     the erase to need **no** RAM exemption. Surface this to the operator at plan time rather than at
     verification time — it is a policy question, not an engineering one.

---

## Sources

### Primary (HIGH confidence — read directly this session)

- **Firmware source**, `firestarter/` @ `gsd/v1.32-at28c-write-path-root-cause-report-provenance`:
  `src/proms/eeprom_28c.cpp` (:100-250, :313-365, :460-600), `src/proms/flash_5v_page.cpp` (:1-231),
  `src/proms/flash_nor_unlock.cpp` (:17-110), `src/proms/flash_intel.cpp` (:85-140),
  `src/proms/eprom.cpp` (:25-75, :150-165), `src/proms/memory.cpp` (:395-470),
  `src/operation_utils.cpp` (:108-390), `src/eprom_operations.cpp` (:25-75),
  `include/flash_utils.h` (full), `include/firestarter.h` (:61-62, :153-154, :175),
  `platformio.ini` (:1-195), `scripts/check_size_baseline.py` (:1-150, constants at 147/191/249/323/367),
  `scripts/baseline/size_baseline.json` (full).
- **Firmware tests**: `test/native/avr/test_dispatch/test_configure_memory.cpp` (:270-340),
  `test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` (:1078-1180, :1390-1416, :1645-1671),
  `test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` (:397-411),
  `test/native/avr/_shared/validation_matrix.h` (:20).
- **Host source**, `firestarter_app/`: `firestarter/database.py` (:555-640),
  `firestarter/ic_layout.py` (:222-245, :565-600), `firestarter/cli_handlers.py` (:325-400, :630-700,
  :790-940), `firestarter/chip_test.py` (:300-340, :560-770, :1885-1900),
  `firestarter/eprom_operations.py` (:305-340, :2035-2075), `firestarter/constants.py` (:120-122),
  `tools/check_dispatch.py` (full), `tools/build_db.py` (:318-405),
  `tools/check_no_log_in_sdp_window.py` (:1-190), `tests/fw_presence.py` (:55-140),
  `tests/scan_paths.py` (:85-200), `tests/test_sdp_table_parity.py` (:1-70, :120-270),
  `pyproject.toml`, `.github/workflows/ci.yml`.
- **Measured this session:**
  - `pio run -e leonardo` after `rm -rf .pio/build/leonardo` → **flash 27500 / 32768, RAM 2016 / 2560** —
    byte-identical to the committed baseline, so the baseline is reproducible.
  - `avr-nm -S --size-sort` on `firestarter_leonardo.elf` → `EEPROM_SDP_DISABLE` **0x1e (30 B)** at
    `0x800127` **section `d` = `.data` = RAM**; `EEPROM_SDP_ENABLE` 0x0f (15 B) at `0x800118`;
    `_ZL11FLASH_ERASE` 0x1e at `0x800163`; **two** surviving copies of `FLASH_ENABLE_WRITE`
    (`.lto_priv.92`/`.93`), proving cross-TU non-merging.
  - `convert_to_programmer` over the generated DB → 84 algorithm-13 rows, 66 `EEPROM` / 18
    `Flash/EEPROM`, **84 would gain `FLAG_CAN_ERASE`, 0 ineligible**, 75 supported / 9 adapter-required.
  - `sha256sum` of the three `tools/catalog/messages.toml` copies → identical (`260066039d…`).
- **Datasheet**, `firestarter_app/datasheets/AT28C256.pdf` (Microchip DS20006386B, 32 pp., AES-encrypted,
  read via `pypdf`): p11 *OPTIONAL CHIP ERASE MODE* — *"The entire device can be erased using a 6-byte
  software code. See Software Chip Erase application note for details."*; p11 Table 6-1 Operating Modes
  — `Chip Erase: CE=VIL, OE=VH(3), WE=VIL, I/O=High-Z` with note `3. VH = 12.0 V ± 0.5V`; p15 §6.10 Chip
  Erase Waveforms.
- **Pinouts**, `firestarter_app/firestarter/data/pinouts.json`: `DIP28_28C256` has **no `vpp-pin`**
  (A14 at pin 1, WE at 27), `oe-pin: [22]`; `DIP28_2764` **does** have `vpp-pin: [1]` and `oe-pin: [22]`.
- **Planning**: `.planning/REQUIREMENTS.md` (:285-345), `.planning/ROADMAP.md` (:37, :163, :461-490),
  `.planning/PROJECT.md` (:44-120), `.planning/phases/152-report-provenance-close/152-CONTEXT.md`
  (D-06/D-07/D-08/D-15 and the erase finding's primary-source list), `.planning/config.json`.

### Secondary (MEDIUM confidence — authoritative document, generic web transport)

- **Atmel Application Note "Software Chip Erase", Rev. 0544B-10/98**
  `[CITED: https://ww1.microchip.com/downloads/en/Appnotes/doc0544.pdf]` — fetched and read directly
  this session (4 pp.). The six load commands verbatim: `5555←AA, 2AAA←55, 5555←80, 5555←AA, 2AAA←55,
  5555←10`; *"the device will set each byte to the high state (FFH)"*; *"the device will internally time
  the erase operation so that no external clocks are required"*; `tEC` Chip Erase Cycle Time **20 ms
  Max**; Note 2 *"After loading the 6-byte code, no byte loads are allowed until the completion of the
  erase cycle"*; *"The software data protection is still enabled even after the software chip erase is
  performed"*; p2 waveform note *"OE must be high only when WE and CE are both low"*.
  Confidence note: `gsd-tools query classify-confidence --provider webfetch --verified` returns **LOW**
  because the transport was a generic fetch. The *document* is the manufacturer's own application note
  and its content was read, not summarised by a search engine — treat the byte sequence as HIGH and the
  provider tier as the transport caveat it is. Corroborated independently by the in-tree `FLASH_ERASE`
  table (byte-identical) and by `test_eeprom28c_sdp.cpp` Case 19, which already names that table
  "chip-erase".
- Digi-Key TechForum, *"ATMEL — AT28HC64BF EEPROM Software Erase"*
  `[CITED: https://forum.digikey.com/t/atmel-at28hc64bf-eeprom-64k-8k-x-8-software-erase/28116]` —
  corroborates that AN_0544 is the citation of record and that narrower parts transpose
  `0x5555 → 0x1555`, `0x2AAA → 0x0AAA` (i.e. plain truncation, which the RURP bus already effects).

### Tertiary (LOW confidence — not relied on for any claim)

- `.planning/graphs/graph.json` — **not queried.** `gsd-tools graphify status` reports
  `stale: true, age_hours: 1213, commits_behind: 1525`, built at `f4150b8` against a current tip of
  `19fb603`. It predates all of v1.30, v1.31 and v1.32, so any relationship it reported about
  `eeprom_28c.cpp` or `database.py` would describe code that no longer exists. Deliberately excluded
  rather than cited with a caveat.
- General web search results on the AT28C erase sequence — one summary actively conflated the erase
  terminal byte `0x10` with the SDP-disable terminal byte `0x20`. Discarded in favour of the primary
  application note. Recorded here because it is exactly the one-nibble hazard class Case 19 guards.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| Code locations & line numbers | **HIGH** | Every cited line read in-session and re-verified with a targeted `grep -n`. Two roadmap line numbers corrected: the `database.py` edit site is **620**, not 621; `cli_handlers.py:854` is the `@cli.command(name="blank")` decorator, the `def blank` is at 866. |
| ERASE-02's sibling existence | **HIGH** | Located at `flash_5v_page.cpp:88-90`, read, byte-identical shape to `0x0D`'s. |
| The erase byte sequence | **HIGH** | Primary manufacturer application note read directly, corroborated by an in-tree byte-identical table and an existing test that names it. |
| The GATE-03 analysis | **HIGH** | `check_dispatch.py` read end to end (509 lines); its GATE-03 guard, its VPP-invariant scope and its `_DB_CHECKED_VPP_INVARIANTS` narrowing are quoted from the source, including the comment that says the 5 V-family invariants are fixture-proven only. |
| Size / RAM position | **HIGH for the current position and the table cost** (baseline reproduced; `avr-nm` section+size read directly); **MEDIUM for the delta** of code not yet written — that is a Wave-0 measurement task, and this document says so rather than guessing a budget. |
| Test surfaces & mandatory inversions | **HIGH** | All four inverting assertions read verbatim, with line numbers and the exact assertion messages. |
| Whether the erase needs an SDP prefix | **MEDIUM** | The strongest available evidence is structural (shared five-write prefix, one decoder) plus the AN's silence. Logged as A3 and as Open Question 1 — the single item most worth resolving before code is written. |
| tEC generality across all 84 rows | **MEDIUM** | 20 ms is the Atmel family maximum; the bucket spans six other vendors. |

**Research date:** 2026-08-21
**Valid until:** 2026-09-20 (30 days) — the code facts are stable, but `size_baseline.json` and the
leonardo position move with every firmware phase, so **re-measure rather than re-read** if this document
is consulted after Phase 152 lands or after any other firmware change.
