# Phase 94: FIX + PGSZ — Firmware Write-Path Fix & Datasheet-Sourced Per-Chip Page Size - Research

**Researched:** 2026-06-27
**Domain:** Firmware/host lockstep fix on AMD/JEDEC page-write flash (`0x05` "flash4"); 12V-on-5V hazard removal (host flag derivation); datasheet-sourced per-chip `page_size` wire field; firmware boot-block-lockout detection diagnostics; native register-trace tests + py3.11 CI gates
**Confidence:** HIGH (every firmware/host claim verified by direct source read; W29C040 §6.6 + command-code tables extracted verbatim from the in-repo PDF; Phase 93 RCA verdict consumed in full)

> **READ THIS FIRST — Phase 94 scope is REFRAMED by the Phase 93 RCA.** The ROADMAP's
> original FIX success criterion ("the flash4 write path is corrected so the W29C040
> programs page 0") is **INVALIDATED**. Phase 93 named the root cause as **SILICON
> (chip-instance-specific): the seated W29C040 has its §6.6 first-16K boot-block
> programming lockout permanently activated** — and §6.6 (extracted below) confirms
> there is a LOCKOUT-ENABLE command but **NO unlock/disable command**: the lock is
> irreversible. **No firmware change can make this chip program 0x0000–0x3FFF.** The
> flash4 page-write algorithm is PROVEN CORRECT (writes to 0x4000+ pass byte-exact).
> Phase 94's FIX scope therefore PIVOTS to the actually-fixable items the RCA surfaced.
> See `## FIX-01 Reframing` (the first content section) for the binding scope.

---

<user_constraints>
## User Constraints (from milestone REQUIREMENTS.md + Phase 93 RCA hand-off)

> No `94-CONTEXT.md` exists yet (pre-discuss). The constraints below are the **locked
> milestone context** from REQUIREMENTS.md + the Phase 93 `93-RCA-FINDINGS.md` hand-off
> + standing bench discipline. They bind the planner exactly as a CONTEXT.md would.
> If `/gsd-discuss-phase 94` runs later, its CONTEXT.md supersedes this section.

### Locked Decisions
- **Branch base:** firmware forks off the **v1.16 tip `a296195`** (primitives recompose), NOT firmware `beta` (stale at v1.13). Dual-repo lockstep wherever a change crosses the wire. Meta `.planning/` on `gsd/v1.17-w29c040-programming-protocol`.
- **Page size is ALREADY correct (256 B) for the W29C040** in the current firmware (`flash4_page_size(524288) → 256`). PGSZ generalizes page sizing for the *other* flash4 families; it is NOT a W29C040 fix.
- **The W29C040 page-0 fault is SILICON (boot-block lockout) — NOT a firmware bug.** Per `93-RCA-FINDINGS.md` (H5 CONFIRMED, exact 16K boundary: 0x3F00 FAIL / 0x4000 PASS) and W29C040.pdf §6.6 (no unlock command exists). The firmware write algorithm is correct and MUST NOT be "fixed" to chase page 0.
- **SAFE-01 (held, conditional):** over-voltage stays blocked at the firmware VPP check; host `chip_resolver.resolve_chip` guard never bypassed; W29C040 flows through the normal `supported` path; no test-only escape hatch.
- **SAFE-01 precondition for Phase 95:** T-93-CANERASE (FIX-01) MUST be implemented + verified before any Phase 95 bench write proceeds *without* `--skip-erase`.
- **Bench LOCKED to Leonardo + RURP Rev 2.0 + operator-seated W29C040** on `/dev/ttyACM0`. Standing discipline: live R1/R2 readback each task (r1 ≈ 270000 ± 25%), verify `controller:` identity per task, Leonardo is chip-OUT-sideload-EXEMPT. Host is firestarter 3.0.0b10 (editable, v1.17 branch, post-HARD-01).
- **No re-refactoring flash4 / primitives** — v1.16's decomposition is the baseline; fix behavior on top of it, not the architecture (Out of Scope, REQUIREMENTS.md).
- **No beta cut / stable promotion / gitlink bump** — operator-gated; gitlinks PINNED at b10 (a1953c2/98b3a92). Not part of this milestone.

### Claude's Discretion
- **FIX-01 implementation choice:** host-only (don't set `FLAG_CAN_ERASE` for protocol 0x05), firmware-only (5V-guard `flash4_erase_execute`), or defense-in-depth (both). Research recommends below; the operator/discuss picks.
- **Boot-block detection feasibility:** firmware-side detection read (datasheet §6.6 ID-mode sequence) with a clear host error, vs a host-side post-failure heuristic hint. Research scopes both; pick based on firmware-budget appetite.
- **PGSZ wire mechanism:** new `page-size` JSON key (mirrors the `read-strobe-us` precedent) vs derive on host only. Research recommends the wire field for correctness; discuss may scope down.
- **Per-chip `page_size` authoring point:** `extra_chips.json` supplement vs inline in `build_db.py` vs a new source table. Research recommends a mechanism below.

### Deferred Ideas (OUT OF SCOPE for Phase 94)
- **Bench graduation (byte-exact full-image write→verify SHA gate)** → Phase 95 (BENCH-01/02/03). **HARDWARE-BLOCKED on this chip** for 0x0000–0x3FFF (see FIX-01 Reframing).
- **PROTOCOL-LEDGER update / CR-01 close / `check_ledger.py`** → Phase 96 (LEDGER-01/02).
- **AM27C020 0x08 (FUT-06), 2516 0x0B (FUT-03), W27E040 0x08 (FUT-05)** — unrelated families, deferred.
- **Obtaining a different (unlocked) W29C040 sample** — operator-only physical action; Phase 95 graduation concern, not Phase 94.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FIX-01 | Firmware flash4 write path corrected so W29C040 programs page 0 and subsequent pages without the fault | **REFRAMED** (see `## FIX-01 Reframing`): page-0 is hardware-blocked (§6.6 lockout, irreversible). The genuine FIX-01 = (a) **T-93-CANERASE** (remove the 12V-on-5V hazard) + (b) **boot-block lockout detection/diagnostics** (clear error instead of cryptic timeout). The write algorithm itself needs NO change. |
| FIX-02 | Fix preserves v1.16 flash4 golden register traces + dispatch-mirror guard; re-pin with cited rationale where a trace legitimately changes | `## Golden Traces & Native Test Structure` — the host-only FIX-01 does NOT touch firmware → all golden traces stay green untouched. A firmware boot-block-detect addition would only run on the verify-timeout error path, NOT the golden write/chip-id traces (which use clean data) — traces stay green. PGSZ firmware change (consume `handle->page_size`) preserves the trace IF the W29C040 page_size resolves to 256 (it does). |
| FIX-03 | Native flash4 tests cover the corrected path; fix delivered dual-repo lockstep wherever it crosses the wire (`constants.py` ↔ `firestarter.h`) | `## Validation Architecture` + `## Don't Hand-Roll` — FIX-01 host change is wire-affecting (changes the `flags` value sent) → add a host wire test asserting `flags & FLAG_CAN_ERASE == 0` for 0x05; constants parity unchanged (no new flag). PGSZ adds a wire field → lockstep `constants.py` JSON key ↔ `json_parser.c` key. |
| PGSZ-01 | Each flash4 chip in the DB carries a datasheet-sourced per-chip `page_size` field (not capacity-derived), authored in the build pipeline with cited datasheet values | `## PGSZ — Per-Chip Page Size` — authoring mechanism (recommend `extra_chips.json` supplement or inline build_db map); cited values (W29C040=256, W29C020=128 confirmed from in-repo PDFs); the heuristic-vs-native delta table. |
| PGSZ-02 | Firmware consumes per-chip `page_size` instead of `flash4_page_size(mem_size)`, fixing under-sized families | `## PGSZ` — replace `flash4_page_size(handle->mem_size)` with `handle->page_size` (new struct field) + a safe fallback to the heuristic when the field is absent/0. |
| PGSZ-03 | `page_size` carried over the wire (lockstep) with a safe default; `check_dispatch.py` passes; `diff_db.py` shows only intended `page_size` additions | `## PGSZ` + `## Validation Architecture` — wire field mirrors the `read-strobe-us` pattern; `diff_db.py` gate run via `tests/test_diff_db_gate.py`; `check_dispatch.py` via `tests/test_check_dispatch_invariants.py`. |
| SAFE-02 | Lockstep wire contract stays in sync (constants parity test green) + host CI green on **py3.11** (ruff check + ruff format --check + mypy + diff_db + check_dispatch), avoiding the py3.12-masks-CI-3.11 trap | `## SAFE-02 / CI` + `## Security Domain` — py3.11 local validation recipe; the f-string-backslash + non-ruff-clean-codegen traps; the gates' actual CI invocation (pytest-wrapped). |
</phase_requirements>

---

## FIX-01 Reframing (BINDING — the corrected FIX scope)

**The ROADMAP success criterion "the flash4 write path is corrected so the W29C040 programs
page 0" is hardware-impossible and must NOT be attempted.** Here is the verbatim datasheet
evidence and the corrected scope.

### Datasheet proof: the lock is irreversible (no unlock command exists)

`[VERIFIED: firestarter/datasheets/0x05-FLASH-AMD-STD/W29C040.pdf §6.6, extracted 2026-06-27]`

> "There are two boot blocks (16K bytes each)… The first 16K or last 16K of the memory can be
> set as a boot block by using a **seven-byte command sequence**. See Command Codes for Boot
> Block Lockout Enable… **Once this feature is set the data for the designated block cannot be
> erased or programmed (programming lockout)**… In order to **detect** whether the boot block
> feature is set… users can perform a **six-byte command sequence**: enter the product
> identification mode… and then read from address **"00002 hex"** (for the first 16K) or
> **"7FFF2 hex"** (for the last 16K). If the output data is **"FF hex," the lockout feature is
> activated**; if **"FE hex," the lockout feature is inactivated**… To return to normal
> operation, perform a **three-byte command sequence to exit** the identification mode."

The §6.6 prose and the two command-code tables (p10 Identification/Boot-Block-Lockout-Detection,
p11 Boot-Block-Lockout-Enable) provide **ENABLE** and **DETECT** sequences only. **There is no
disable/unlock command anywhere in the datasheet.** Combined with the Phase 93 bench step
function (0x3F00 FAIL / 0x4000 PASS, exact 16K boundary), the verdict is final: the seated
chip's first-16K block is permanently locked. **Phase 94 cannot fix page 0 in firmware.**

### The genuine, fixable FIX-01 (two parts)

**FIX-01a — T-93-CANERASE (HIGH-priority safety bug — the real core of FIX-01):**
Remove the 12V-on-5V hazard. `database.py:convert_to_programmer` (line 604–607) sets
`FLAG_CAN_ERASE (0x02)` for every `electrical.type ∈ {"EEPROM","Flash/EEPROM"}` chip, including
the 5V-only protocol-0x05 W29C040. On the wire that flag routes firmware `flash4_write_init`
(flash_type_4.cpp:78) → `flash4_erase_execute` (flash_type_4.cpp:155) which asserts
`CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE | CTRL_VPE_ENABLE` = **12V boost on a
5V chip.** `[VERIFIED: direct source read + SAFE-01-PREFLIGHT.md Item 2 RED/HIGH]`

**FIX-01b — Boot-block lockout detection + clear diagnostics (genuine feature):**
A write into a locked region currently dies with the cryptic
`ERROR: Timeout verifying 0x.. at 0x0000ff (got 0x00)` (MSG_ERR_FL4_VERIFY_TIMEOUT, 0xB3) that
*looks like a firmware bug*. The fix surfaces a clear, correct message
("boot block locked — region 0x0–0x3FFF not programmable on this chip") so the operator/Phase 95
understands the chip is the blocker, not the code.

**FIX-01 does NOT change `flash4_write_execute` or the page-write algorithm.** The algorithm is
proven correct (0x4000+ writes pass byte-exact, Phase 93 Test #5/diag 0x4000).

### Honest milestone-done-bar framing (for discuss/operator)

The v1.17 done-bar (Phase 95 BENCH-01: byte-exact full-image write→verify) is **hardware-blocked
on the seated chip** for 0x0000–0x3FFF. The operator must decide at Phase 94/95 planning:
(1) obtain a different (unlocked) W29C040 sample, OR (2) re-scope Phase 95 BENCH-01 to the
proven-writable region (≥0x4000) with explicit documentation that page-0 needs an unlocked chip.
This is an **operator decision**, not a Phase 94 code task. The writable-region (0x4000+)
write→read→verify proof is the honest demonstration that the algorithm + commands are correct.

---

## Summary

Phase 94 is a **dual-repo lockstep fix + DB-pipeline generalization** phase with production code,
native tests, py3.11 CI gates, and an opportunistic bench writable-region proof. After the Phase
93 RCA, it carries **three independent, fully-fixable work items** plus the test/CI scaffolding:

1. **FIX-01a (T-93-CANERASE)** — the highest-priority item: a latent 12V-on-5V hazard. The
   cleanest fix is **host-side**: `convert_to_programmer` must not set `FLAG_CAN_ERASE` for
   protocol-0x05 chips (flash4 auto-erases per page during the page-write — the separate 12V
   bulk erase is never needed). Recommended **defense-in-depth**: also add a firmware guard so
   `flash4_erase_execute` is a no-op (or VPP-free) for 5V chips, so a stale/hand-crafted JSON
   command can't re-trigger the hazard.

2. **FIX-01b (boot-block detection diagnostics)** — implement the datasheet §6.6 DETECT read in
   firmware (ID-mode entry AA→5555/55→2AAA/90→5555; read 0x00002 → FF=locked/FE=unlocked; exit
   AA→5555/55→2AAA/F0→5555), hooked on a write-verify timeout in the first/last 16K, surfacing a
   new MSG_ERR. The timing constraint (the ID-mode command bytes must be emitted firmware-side —
   a host `dev reg` round-trip cannot meet the byte-load window) makes this firmware-side. A
   **lower-effort fallback** is a host-side post-failure heuristic (failing address in first/last
   16K → emit a boot-block-locked hint) that needs zero firmware change.

3. **PGSZ-01/02/03 (CR-01)** — replace the firmware capacity heuristic `flash4_page_size(mem_size)`
   with a datasheet-sourced per-chip `page_size` carried over the wire (mirroring the existing
   `read-strobe-us` field plumbing), with a safe fallback to the heuristic when absent.

**Primary recommendation:** Implement FIX-01a **host-side first** (it's the safety-critical item,
needs no firmware change, and immediately unblocks Phase 95 from `--skip-erase`), add the
defense-in-depth firmware guard, then do PGSZ as a clean wire-field addition, and finish with
FIX-01b (firmware detection preferred; host heuristic acceptable as a fallback). The host-only
FIX-01a leaves **all v1.16 golden traces untouched** (FIX-02 satisfied trivially).

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| FIX-01a flag derivation (don't 12V a 5V chip) | **Host** `database.py:convert_to_programmer` | Firmware `flash4_erase_execute` 5V-guard (defense-in-depth) | The hazard originates in the host flag derivation; preventing the flag reaching the wire is the cleanest cut (RCA hand-off Fix Item 2 "host-side fix is cleaner") |
| FIX-01b boot-block lockout DETECTION read | **Firmware** `flash_type_4.cpp` (ID-mode byte sequence within timing window) | Host fallback heuristic (post-failure address-range hint) | The §6.6 detect sequence must emit command bytes faster than a host `dev reg` round-trip allows — firmware-side only (objective item 2) |
| FIX-01b clear error surfacing | Firmware MSG_ERR (new id) → host `messages.py`/`frame_parser.py` render | Host-side hint (if firmware detect deferred) | Error plumbing is the firmware MSG catalog → codegen → host render chain |
| PGSZ value authoring (datasheet page sizes) | **Host** DB pipeline (`build_db.py` / `extra_chips.json` / `chip_database.json`) | — | The DB is the host's responsibility; firmware consumes it |
| PGSZ wire transport | **Host** JSON build + **Firmware** `json_parser.c` key | Lockstep `constants.py` ↔ struct field | New wire field crosses the seam — both repos in one change |
| PGSZ firmware consumption | **Firmware** `flash4_write_execute` reads `handle->page_size` | Heuristic fallback retained for absent field | The page-write loop is firmware; fallback keeps backward-compat (PGSZ-03 "safe default") |
| Bench writable-region proof | Bench (Leonardo + Rev 2.0 + seated W29C040, ≥0x4000) | Host CLI driving + SHA verify | Demonstrates the algorithm is correct without the locked region |
| CI parity / py3.11 gate | **Host** CI (`ci.yml`) | Firmware `pio test -e native` | SAFE-02 gates live in the host CI; firmware native tests run via pio |

---

## Standard Stack

This is a fix/generalization phase on existing code — **no new packages are installed.** The
"stack" is the in-repo toolchain, the two chip datasheets, and the existing wire-field plumbing.

### Core (existing tooling — reuse only)
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| PlatformIO (`pio`) | in-repo `platformio.ini` | Build `leonardo` firmware (`pio run -e leonardo`); run native tests (`pio test -e native`) | Project-standard build; `[env:native]` recording-stub suite is the Tier-1 oracle for FIX/PGSZ |
| `firestarter` CLI (host) | editable (`pip install -e '.[test]'`) | Drive write/read/verify + `dev` instrumentation; run pytest gates | Project-standard host |
| `firestarter/src/proms/flash_type_4.cpp` | `a296195` recompose | The handler under change (FIX-01b detect, PGSZ consumption) | Code under change |
| `firestarter_app/firestarter/database.py` | v1.17 branch | `convert_to_programmer` (FIX-01a flag fix) + `_map_data` (exposes `electrical-type`) | The flag-derivation source |
| `firestarter_app/tools/build_db.py` | v1.17 branch | DB pipeline — PGSZ page_size authoring point (`chip_entry` construction line 647) | The DB generator |
| `W29C040.pdf` / `W29C020.pdf` | in-repo (`datasheets/0x05-FLASH-AMD-STD/`) | §6.6 boot-block detect/enable codes + per-chip page sizes | Authoritative silicon spec |
| `pypdf` | container Python | Datasheet text extraction (no poppler in container) | Already present; read-only research use |

### Supporting (existing wire-field + gate plumbing — the templates to copy)
| Mechanism | Where | Purpose | When to Use |
|-----------|-------|---------|-------------|
| `read-strobe-us` wire field | `constants.py:95` (`JSON_KEY_READ_STROBE_US`) ↔ `json_parser.c:91` (`key_read_strobe`) ↔ `eprom_operations.py:647` (emit-when-nonzero) | **The exact precedent for adding `page-size` over the wire** | PGSZ-03 — copy this pattern verbatim |
| Native recording-bus stub | `test/native/avr/test_val_flash4/host_stubs.cpp` + `test_val_flash4.cpp` | Tier-1 register-sequence assertions (no hardware) | FIX/PGSZ native tests |
| Golden trace `.inc` + `GOLDEN_BLESS` | `test/native/avr/test_val_flash4/golden_flash4_write.inc` + `_shared/golden_trace.h` | Byte-exact register-trace pinning (FIX-02) | Re-bless only if a trace legitimately changes |
| `tests/test_diff_db_gate.py` | host pytest | Runs `diff_db.py` as a CI gate (PGSZ-03) | DB-change verification |
| `tests/test_check_dispatch_invariants.py` | host pytest | Runs `check_dispatch.py` invariants (PGSZ-03 / SAFE) | Dispatch-safety verification |
| `tests/test_val_wire_flash4.py` | host pytest | Asserts the flash4 wire dict (algorithm, dispatch) | FIX-01a — add a `flags & FLAG_CAN_ERASE == 0` assertion here |
| `tools/catalog/messages.toml` + `codegen.py` | host | Single-source MSG catalog → `messages.py` (host) + `messages.h` (firmware) | FIX-01b — add a new boot-block MSG here, regenerate both sides |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Host-only FIX-01a | Firmware-only `flash4_erase_execute` 5V-guard | Firmware-only leaves the hazardous flag on the wire (a future/old firmware would still 12V). Host-only is cleaner but a hand-crafted JSON could still set it. **Recommend both (defense-in-depth)** per RCA hand-off. |
| Firmware §6.6 detection (FIX-01b) | Host post-failure address-range heuristic | Firmware detect is authoritative (actually reads the FF/FE lockout bit) but costs flash + the ID-mode timing care; host heuristic is zero-firmware but only *infers* from the address range. Recommend firmware detect if budget allows; host heuristic is an acceptable fallback. |
| `page-size` wire field (PGSZ) | Host-only page derivation (don't send it) | Host-only can't tell the firmware the value — firmware would keep its heuristic. The wire field is required for PGSZ-02's "firmware consumes per-chip page_size." |
| `extra_chips.json` supplement for page_size | Inline `_PAGE_SIZE_BY_PART` map in `build_db.py` | `extra_chips.json` already exists as the supplement seam; an inline map keeps the datasheet citations next to the code. Either works; recommend the inline map with `[CITED:]` comments for traceability. |

**Installation:** None. Confirm host with `firestarter --help`, restore toolchain with
`pip install -e '.[test]'` (from `/workspaces/firestarter_app`), and firmware with
`pio run -e leonardo` (from `/workspaces/firestarter`). `node` is not on PATH in the
devcontainer (`/vscode/vscode-server/bin/linux-x64/*/node`) — relevant only for GSD tooling.

---

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.** All work uses the existing
editable host install + `pio` + in-repo datasheets. The only third-party tool touched is
`pypdf` (datasheet extraction), already present and used read-only for research; not a runtime
dependency of either sub-repo. No `npm`/`pip`/`cargo` install occurs.

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

---

## Architecture Patterns

### System Architecture Diagram — the FIX-01a / FIX-01b / PGSZ data flow

```
                         ┌─────────────────────── HOST (firestarter_app) ───────────────────────┐
 firestarter write W29C040 <img>
        │
        ▼
 chip_resolver.resolve_chip("W29C040")   ── support_status=supported (NEVER bypassed, SAFE-01)
        │
        ▼
 database._map_data()  ── exposes electrical-type="Flash/EEPROM", protocol-id=5, page_size? (PGSZ-01 NEW)
        │
        ▼
 database.convert_to_programmer()
   ├─ flags derivation ⚠ FIX-01a: TODAY sets FLAG_CAN_ERASE(0x02) for Flash/EEPROM
   │                    →  FIX: for algorithm==5 (0x05 flash4), do NOT set FLAG_CAN_ERASE
   └─ page-size emit    ●  PGSZ-03 NEW: carry per-chip page_size (emit-when-present, like read-strobe-us)
        │
        ▼
 eprom_operations.py  ── builds JSON cmd dict
        │
        ▼
 serial_comm.py (COBS + CRC8, 250000 baud)
        │
        ▼  ─────────────────────────── FIRMWARE (Leonardo + Rev 2.0) ────────────────────────────┐
 json_parser.c  ── parses "page-size" → handle->page_size (PGSZ-03 NEW key, mirrors key_read_strobe)
        │           parses "flags"     → handle->ctrl_flags (FIX-01a: no longer carries 0x02 for 0x05)
        ▼
 configure_memory() ── protocol==0x05 → configure_flash4()
        │
        ▼
 flash4_write_init()
   ├─ is_flag_set(FLAG_CAN_ERASE)?  ⚠ FIX-01a host fix means this is now FALSE for 0x05
   │     └─ flash4_erase_execute()  ⚠ 12V hazard — now unreachable for 0x05 (+ optional 5V-guard, defense-in-depth)
   └─ blank_check
        │
        ▼
 flash4_write_execute()
   page_size = handle->page_size ? handle->page_size : flash4_page_size(handle->mem_size)   ● PGSZ-02 NEW
   for each byte: SDP-per-page + set_data + poll_readback(...,1024)
        │
        ▼  on poll timeout in first/last 16K:
 flash4_detect_boot_block_lockout()   ● FIX-01b NEW (firmware): §6.6 ID-mode read 0x00002/0x7FFF2
        │   FF=locked → emit MSG_ERR_FL4_BOOT_BLOCK_LOCKED (new); FE=unlocked → keep MSG_ERR_FL4_VERIFY_TIMEOUT
        ◄──────────────────────────────── ERROR frame ────────────────────────────────────────┘
        "boot block locked — region 0x0–0x3FFF not programmable on this chip"   ← clear diagnostic
```

### Pattern 1: Wire-field addition (copy the `read-strobe-us` precedent for `page-size`)
**What:** A host→firmware JSON scalar field, emitted only when non-zero/present, parsed by a
PROGMEM key entry, with a firmware default when absent.
**When to use:** PGSZ-03 (`page-size`).
**Example (the exact existing template):**
```python
# Source: firestarter_app/firestarter/constants.py:94-95
JSON_KEY_READ_SETTLING_DELAY = "read-settling-delay"
JSON_KEY_READ_STROBE_US = "read-strobe-us"          # ← add JSON_KEY_PAGE_SIZE = "page-size" alongside
```
```python
# Source: firestarter_app/firestarter/eprom_operations.py:640-647 (emit-when-nonzero)
if read_settling_us or read_strobe_us:
    eprom_data_dict = dict(eprom_data_dict)          # shallow copy — never mutate caller's dict
    if read_strobe_us:
        eprom_data_dict[JSON_KEY_READ_STROBE_US] = read_strobe_us
# PGSZ analog: emit eprom_data_dict[JSON_KEY_PAGE_SIZE] when the DB provides a per-chip page_size
```
```c
// Source: firestarter/src/json_parser.c:78-91 + :80 — add a key_page_size entry + get_page_size parser
const char key_read_strobe[]   PROGMEM = "read-strobe-us";   // ← add const char key_page_size[] PROGMEM = "page-size";
// ...register {key_page_size, get_page_size} in key_parsers[]; get_page_size sets handle->page_size
```
The firmware `json_parser.c` already **silently skips unknown fields** (line 134–137), so a host
that sends `page-size` to an old firmware is forward-compatible, and a firmware expecting it but
not receiving it falls back to the heuristic — both directions safe (PGSZ-03 "safe default").

### Pattern 2: New MSG via the codegen catalog (FIX-01b clear error)
**What:** A new firmware error message is authored ONCE in `tools/catalog/messages.toml`, then
`codegen.py` regenerates `firestarter/messages.py` (host) and the firmware `messages.h` stays in
sync. The CI "Codegen drift gate" (`git diff --exit-code firestarter/messages.py`) enforces it.
**When to use:** FIX-01b firmware detection's clear error (e.g., `MSG_ERR_FL4_BOOT_BLOCK_LOCKED`).
**Example:** the existing flash4 timeout entry to copy:
```toml
# Source: firestarter_app/tools/catalog/messages.toml:505-518
[[messages]]
id          = 0xB3
name        = "MSG_ERR_FL4_VERIFY_TIMEOUT"
severity    = "ERROR"
format      = "Timeout verifying 0x%02x at 0x%06lx (got 0x%02x)"
params      = [ { type = "u8", render = "hex_byte" }, { type = "u24", render = "hex_addr" }, { type = "u8", render = "hex_byte" } ]
wire_format = "id_frame"
# New: pick the next free ERROR id (0xB3 is taken; scan messages.toml for the next free 0xB-range id),
#      e.g. MSG_ERR_FL4_BOOT_BLOCK_LOCKED, format "boot block locked — 0x%06lx not programmable".
```
**⚠ codegen rule (CLAUDE.md):** `codegen.py` emits `messages.py` **ruff-clean** — do NOT
hand-normalize the generated file; the drift gate + ruff would contradict (`reference_codegen_ruff_clean_emitter`).

### Pattern 3: Native register-trace assertion (no hardware) — the Tier-1 oracle
**What:** Drive `configure_memory` + `firestarter_operation_main` against the recording-bus stub
and assert on the captured `{reg, data}` sequence (SDP-count, VPP-bit-absence, golden trace).
**When to use:** every FIX/PGSZ firmware change that must be proven without silicon.
**Example:** `test_inv04_flash4_256b_page_boundary` (SDP-count discriminates page_size) and
`test_flash4_write_execute_no_vpp` (VPP-bit absence) — the templates for the PGSZ page_size
consumption test and the FIX-01a no-12V test.

### Anti-Patterns to Avoid
- **"Fixing" the page-write algorithm to chase page 0.** The algorithm is correct; the chip is
  locked (§6.6, irreversible). Any change to `flash4_write_execute`'s SDP/poll/page logic to
  "make page 0 work" is wrong and would risk regressing the proven 0x4000+ path.
- **Firmware-only FIX-01a that leaves `FLAG_CAN_ERASE` on the wire.** The host derivation is the
  source; fix it there (the wire should not carry the hazardous flag for 0x05 at all).
- **Hand-normalizing `messages.py` after codegen** — the emitter is ruff-clean; editing it breaks
  the drift gate (CLAUDE.md / `reference_codegen_ruff_clean_emitter`).
- **Validating CI on py3.12 (the devcontainer default) and assuming py3.11 passes** — the
  py3.12-masks-py3.11 trap (SAFE-02; f-string backslashes, non-ruff-clean codegen). Always
  validate against py3.11 (see `## SAFE-02 / CI`).
- **`write -b` to "skip erase" on a non-blank chip.** Post-HARD-01, `-b` skips only blank-check,
  NOT erase (`reference_write_b_skips_erase`). Use plain `write` (or `--skip-erase` explicitly).
- **N=1 bench conclusions / port-identity drift** — N≥2; verify `controller:` identity + live
  R1/R2 each task (ACM* numbers shuffle on replug).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Carry `page_size` over the wire | A bespoke new transport / struct-packing scheme | The `read-strobe-us` field pattern (constants.py JSON key + json_parser.c PROGMEM key + emit-when-present) | Proven, forward-compatible (unknown-field skip), lockstep-tested |
| Add a new firmware error message | A raw `Serial.print` or ad-hoc string | `tools/catalog/messages.toml` + `codegen.py` (regenerates host `messages.py` + firmware side) | Single-source; CI drift gate enforces parity; host render plumbing is automatic |
| Prove a firmware register sequence | Reading disassembly / scope-only | `pio test -e native` recording-stub (`test_val_flash4`) | Tier-1 oracle; SDP-count + VPP-absence already asserted there |
| Run the DB-change gate | A custom JSON differ | `tools/diff_db.py` via `tests/test_diff_db_gate.py` | The intended-additions gate (PGSZ-03) already wired to pytest/CI |
| Run the dispatch-safety gate | A custom dispatch simulator | `tools/check_dispatch.py` via `tests/test_check_dispatch_invariants.py` | The BLOCKER-2/dispatch invariant guard already in CI |
| Detect the boot-block lock | A new ad-hoc ID read | The datasheet §6.6 exact sequence (ID-mode entry → read 0x00002/0x7FFF2 → exit), reusing `flash_execute_command(FLASH_ENABLE_ID)` / `FLASH_DISABLE_ID` primitives | The ENABLE_ID/DISABLE_ID byte_flip tables already exist in `flash_utils.h`; the detect read just adds the 0x00002 read between them |
| Assert the FIX-01a no-12V invariant | A new test harness | `assert_no_vpp_in_recording` in `test_val_flash4.cpp` | Already asserts CTRL_VPP_REGULATOR_ENABLE/CTRL_VPP_P1_ENABLE absence |

**Key insight:** Every mechanism Phase 94 needs already exists in-tree — the wire-field pattern,
the codegen catalog, the recording-stub oracle, the gate-via-pytest wiring, and the ID-mode
byte_flip tables. The work is **wiring an existing pattern**, not inventing one. The FIX-01b
detect read is the only *new* firmware logic, and it reuses the existing `FLASH_ENABLE_ID`/
`FLASH_DISABLE_ID` sequences with one extra read.

---

## FIX-01a — T-93-CANERASE Fix Detail

### The exact source of the hazard
```python
# Source: firestarter_app/firestarter/database.py:604-607 (convert_to_programmer)
simple_flags = 0
if full_eprom_data.get("electrical-type", "") in ("EEPROM", "Flash/EEPROM"):
    simple_flags |= FLAG_CAN_ERASE  # FLAG_CAN_ERASE is 0x02
programmer_data["flags"] = simple_flags
```
`electrical-type` is supplied by `_map_data` (database.py:456 `"electrical-type": electrical.get("type", "")`).
The W29C040 entry has `"type": "Flash/EEPROM"` → `flags=0x02` on the wire.
`[VERIFIED: chip_database.json W29C040 entry + SAFE-01-PREFLIGHT.md Item 2]`

### Recommended fix (defense-in-depth)
**(a) HOST (primary, cleanest — RCA hand-off "host-side fix is cleaner"):** gate the flag on
protocol. `convert_to_programmer` already has `algorithm = full_eprom_data.get("protocol-id", 0)`
available via `programmer_data["algorithm"]`. Add: do NOT set `FLAG_CAN_ERASE` when
`algorithm == 5` (protocol 0x05 flash4 — auto-erases per page; no separate 12V bulk erase needed).
The other auto-erase EEPROM path (0x0D `configure_eeprom28c`) is firmware-inert to the flag
(D-03: it never reads `is_flag_set(FLAG_CAN_ERASE)`) so leaving the flag for 0x0D is safe and
unchanged. **Scope the change to algorithm 5 only** to avoid disturbing the 0x07 EE-EPROM path.

**(b) FIRMWARE (defense-in-depth):** make `flash4_erase_execute` refuse to assert the 12V bits.
Two options: (i) skip `flash4_erase_execute` entirely on the 0x05 path (flash4 auto-erases on
page write), or (ii) gate the `CTRL_VPP_REGULATOR_ENABLE|...` assertion behind a VPP check (a 5V
chip — `handle->vpp_mv <= 5000` is NOT a reliable signal here because the W29C040 DB carries
`vpp_mv=12000` as the *chip-ID-read* datum, NOT a program rail — so prefer the protocol-keyed
skip, gated on `handle->protocol == 0x05`, consistent with the D-06 "regulator routing keyed on
handle->protocol, never on electrical.type" boundary).

> **D-06 alignment note (important):** `primitives.cpp` documents the design boundary "regulator
> routing is keyed on handle->protocol, never on electrical.type." The firmware-side guard MUST
> follow this — key the erase skip on `handle->protocol == 0x05`, not on a voltage heuristic.

### Wire-contract impact (FIX-03 / SAFE-02)
FIX-01a changes the **value** of an existing field (`flags`), not the field set — **no new
constant, no `constants.py` ↔ `firestarter.h` parity change.** A host wire test must assert
`(flags & FLAG_CAN_ERASE) == 0` for the flash4 rep chip (add to `tests/test_val_wire_flash4.py`).
The firmware defense-in-depth guard needs a native test (no-12V on the erase path for 0x05).

### Golden-trace impact (FIX-02)
- Host-only FIX-01a: **firmware untouched → all golden traces stay green, no re-bless.**
- Firmware defense-in-depth guard: only changes `flash4_erase_execute` (which is NOT exercised by
  `test_golden_flash4_write` — that test sets `FLAG_SKIP_ERASE | FLAG_SKIP_BLANK_CHECK`, so
  `flash4_write_init` is a no-op). **Golden write trace stays green.** A *new* erase-path native
  test is needed; the golden write/chip-id traces are unaffected.

---

## FIX-01b — Boot-Block Lockout Detection Detail

### The datasheet detect sequence (firmware-side; cited verbatim)
`[CITED: W29C040.pdf §6.6 + p10 "Command Codes for Product Identification and Boot Block Lockout Detection"]`

| Step | Action | Address | Data |
|------|--------|---------|------|
| ENTRY | write | 0x5555 | 0xAA |
| ENTRY | write | 0x2AAA | 0x55 |
| ENTRY | write | 0x5555 | 0x90 |
| DETECT | read | **0x00002** (first 16K) / **0x7FFF2** (last 16K) | **0xFF = locked**, **0xFE = unlocked** |
| EXIT | write | 0x5555 | 0xAA |
| EXIT | write | 0x2AAA | 0x55 |
| EXIT | write | 0x5555 | 0xF0 |
| EXIT | pause | — | 10 µS |

Note the ENTRY sequence is **identical to the existing `FLASH_ENABLE_ID` table** (flash_utils.h:24:
`{0x5555,0xAA},{0x2AAA,0x55},{0x5555,0x90}`) and the EXIT is **identical to `FLASH_DISABLE_ID`**
(`{0x5555,0xAA},{0x2AAA,0x55},{0x5555,0xF0}`). So FIX-01b reuses both existing byte_flip tables and
adds only the **read of 0x00002 / 0x7FFF2** between them — minimal new firmware. The
manufacturer/device ID read at 0x00000/0x00001 (0xDA/0x46) can double as a sanity check that
ID-mode entry succeeded.

### Where to hook it
On a write-verify timeout (`flash4_wait_for_page_write` returns false) when the failing address is
in the first 16K (`< 0x4000`) or the last 16K (`>= mem_size - 0x4000`), call the detect read; if it
returns 0xFF, emit the new `MSG_ERR_FL4_BOOT_BLOCK_LOCKED` instead of (or in addition to) the
generic `MSG_ERR_FL4_VERIFY_TIMEOUT (0xB3)`. The detect read is **only on the error path** — it
does NOT run on a successful write, so it does NOT affect `test_golden_flash4_write` (clean data,
no timeout). FIX-02 preserved.

### Timing constraint (why firmware-side, not host `dev reg`)
The ID-mode ENTRY command bytes are part of an AMD/JEDEC command sequence; a host `dev reg`
round-trip (serial COBS frame each direction at 250000 baud) cannot emit the three ENTRY bytes
within the command-sequence window. The detect MUST be firmware-side (objective item 2). This is
the same reason the SDP unlock is firmware-side.

### Lower-effort fallback (host-side heuristic, zero firmware change)
If the firmware detect is deemed too large for the budget: catch the `MSG_ERR_FL4_VERIFY_TIMEOUT`
on the host (in `eprom_operations.py` write-error handling) and, when the failing address is in
the first/last 16K of a W29C040-class chip, append a hint: "failing address is in a boot-block
region — the chip may have §6.6 boot-block lockout enabled (irreversible); writes to ≥0x4000
should succeed." This infers (does not confirm) the lock, but needs no firmware change and no new
MSG. **Recommend firmware detect if budget allows; host heuristic acceptable otherwise.**

### Error plumbing reference
- Firmware emits via `LOG_ERROR_ID_BYTES(MSG_ID, _b, n)` (flash_type_4.cpp:134 is the template);
  MSG ids live in `firestarter/include/messages.h` (generated) ← `tools/catalog/messages.toml`.
- Host renders via `firestarter/messages.py` (generated, ruff-clean) + `frame_parser.py`
  `_decode_id_frame` + `codec.py format_message`. The codegen drift gate keeps both sides in sync.

---

## PGSZ — Per-Chip Page Size Detail

### The heuristic to replace
```c
// Source: firestarter/src/proms/flash_type_4.cpp:38-42
static uint32_t flash4_page_size(uint32_t mem_size) {
    if (mem_size <= 65536)  return 64;
    if (mem_size <= 262144) return 128;
    return 256;
}
```

### Heuristic-vs-datasheet audit (all 27 flash4 chips enumerated)
`[VERIFIED: enumerated from chip_database.json via EpromDatabase, 2026-06-27]`

The capacity heuristic happens to match Winbond W29C020 (128B) and W29C040 (256B) — the two
RCA chips. **But the heuristic is a capacity proxy, not a datasheet fact**, and the objective
calls out under-sized 64KB→128B / 256KB→256B families. The actual per-chip native page sizes
must be authored from each family's datasheet. Examples to verify during planning:

| Chip family (alg 0x05) | size | heuristic page | datasheet page (verify per family) | Notes |
|------------------------|------|----------------|-------------------------------------|-------|
| W29C040,W29C042 | 524288 | 256 | **256** `[CITED: W29C040.pdf §6.2]` | matches |
| W29C020,W29C020C,W29C022 | 262144 | 128 | **128** `[CITED: W29C020.pdf §6.2]` | matches |
| W29C512,W29EE512 | 65536 | 64 | verify (W29EE512 datasheet) | `[ASSUMED]` until datasheet checked |
| AT29C010A / AT29C020 / AT29C040 | 131072 / 262144 / 524288 | 128 / 128 / 256 | Atmel AT29C: **128 / 256 / 256** `[ASSUMED]` | AT29C020 is **256B** per Atmel — heuristic (128) is WRONG → PGSZ target |
| AT29C256 / AT29C257 / AT29C512 | 32768 / 32768 / 65536 | 64 / 64 / 64 | Atmel AT29C: **64 / 64 / 128** `[ASSUMED]` | AT29C512 may be **128B** — heuristic (64) possibly wrong |
| SST29EE010/020/512 | 131072/262144/65536 | 128/128/64 | SST29EE: **128/128/128** `[ASSUMED]` | SST29EE512 may be **128B** — heuristic (64) possibly wrong |
| AE29F1008/2008/4008 | 131072/262144/524288 | 128/128/256 | verify per family | `[ASSUMED]` |
| AT29BV/LV010A/020/040 | per cap | per heuristic | verify (Atmel low-voltage variants) | `[ASSUMED]` |

> **ACTION for the planner:** the only datasheet-confirmed values right now are W29C040=256 and
> W29C020=128 (both in-repo PDFs). **All other per-chip page sizes are `[ASSUMED]`** and must be
> sourced from each family's datasheet during the PGSZ task (or the per-chip field omitted, leaving
> that chip on the heuristic fallback). Do NOT author a `page_size` value that isn't datasheet-cited
> — an omitted field safely falls back to the heuristic (PGSZ-03). This is the honest scoping:
> author the values you can cite; fall back for the rest.

### Authoring mechanism (PGSZ-01)
`chip_entry` is constructed at `build_db.py:647`. Recommended: add a `"page_size"` to the
`programming` block (or a top-level `page_size`) populated from an **inline
`_PAGE_SIZE_BY_PART` map** keyed on part number, each entry carrying a `[CITED: datasheet]`
comment. Chips not in the map omit the field. `extra_chips.json` is an alternative seam but the
inline map keeps the citation next to the code. `diff_db.py` (PGSZ-03 gate) will then show
exactly the intended `page_size` additions and nothing else.

### Firmware consumption (PGSZ-02)
Add `uint32_t page_size;` to `firestarter_handle_t` (firestarter.h:84 struct). In
`flash4_write_execute` (flash_type_4.cpp:92), replace:
```c
uint32_t page_size = flash4_page_size(handle->mem_size);
// with the safe-fallback form (PGSZ-02 + PGSZ-03 "safe default"):
uint32_t page_size = handle->page_size ? handle->page_size : flash4_page_size(handle->mem_size);
```
Keep `flash4_page_size` as the fallback (do not delete it — it is the absent-field default).

### Wire transport (PGSZ-03) — copy `read-strobe-us`
- `constants.py`: add `JSON_KEY_PAGE_SIZE = "page-size"` near line 95.
- `eprom_operations.py`: emit `eprom_data_dict["page-size"]` when the DB provides a per-chip value
  (emit-when-present, like read-strobe-us at line 647).
- `json_parser.c`: add `const char key_page_size[] PROGMEM = "page-size";` + a `get_page_size`
  parser setting `handle->page_size`, registered in `key_parsers[]` (line 75-81).
- **Lockstep:** the JSON key string lives in both `constants.py` and `json_parser.c`; the struct
  field in `firestarter.h`. No new *flag/constant* → the existing `constants.py` ↔ `firestarter.h`
  flag-parity test is unaffected; the new key is a string, validated by the wire test + native test.

### Golden-trace impact (FIX-02)
`test_golden_flash4_write` uses `mem_size=524288` and (post-PGSZ) would set `page_size=256`
explicitly → identical page boundary as today → **golden trace stays green.** If the handle's
`page_size` defaults to 0 in the test (not set), the fallback yields 256 anyway. Either way the
65-byte probe fires exactly 1 SDP — `test_inv04_flash4_256b_page_boundary` and the golden trace
both stay green. **Re-bless is NOT expected for W29C040.** A new native test should prove the
firmware *consumes* `handle->page_size` (e.g., set page_size=128 on a 512KB handle → SDP fires at
the 128B boundary, distinguishing it from the heuristic's 256).

---

## Runtime State Inventory

> Phase 94 changes the DB pipeline + firmware + sideloads firmware + seats silicon, so the
> inventory is filled for completeness (it is a fix/generalization phase, not a pure rename).

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | The seated **W29C040 silicon** holds prior write fragments (page 0 = locked, contains old data); `chip_database.json` is regenerated by `build_db.py` (PGSZ adds `page_size` rows) | None for silicon (device under test). Regenerate DB via `python tools/build_db.py`; verify with `diff_db.py` that ONLY `page_size` rows changed. **Data migration:** none (page_size is a new additive field). |
| Live service config | **Firmware on the Leonardo** must be re-flashed with the FIX-01b/PGSZ build before bench proof; the host editable install must be reinstalled if the toolchain was wiped | Sideload the new firmware (`pio run -t upload -e leonardo`); Leonardo is chip-OUT-sideload-EXEMPT (do NOT remove chip). `pip install -e '.[test]'` to restore host. |
| OS-registered state | None — CLI-driven over serial, no schedulers/services | None — verified (serial-CLI only). |
| Secrets/env vars | `FIRESTARTER_CONFIG_DIR` / `FIRESTARTER_DB_FILE` test seams (used by gates) reference paths, not secrets | Confirm the bench uses the real seated-board config + the regenerated DB, not a stale saved port (v1.14 "live board + saved config port" false-fail lesson). Verify `controller:` identity per task. |
| Build artifacts | Firmware `.hex` (rebuilt), host editable install, generated `messages.py`/`messages.h` (if FIX-01b adds a MSG), regenerated `chip_database.json` | Rebuild firmware; regenerate `messages.py` via codegen (drift gate enforces); regenerate DB. No `egg-info` rename. |

**Nothing found in category:** OS-registered state — None (verified: serial-CLI only, no scheduler/service registration).

---

## Common Pitfalls

### Pitfall 1: Trying to "fix" the page-write algorithm to make page 0 work
**What goes wrong:** Time spent modifying `flash4_write_execute`'s SDP/poll/page logic; risk of
regressing the proven 0x4000+ path.
**Why it happens:** The ROADMAP's stale FIX-01 wording says "programs page 0."
**How to avoid:** The lock is irreversible silicon (§6.6, no unlock command). Treat the algorithm
as correct (0x4000+ passes). FIX-01 is T-93-CANERASE + detection, NOT an algorithm change.
**Warning signs:** any diff to the per-byte SDP/page loop justified by "page 0."

### Pitfall 2: Firmware-only FIX-01a (flag still on the wire)
**What goes wrong:** Guarding only `flash4_erase_execute` leaves `flags=0x02` on the wire; an old
firmware (or a future regression) would still 12V the chip.
**Why it happens:** Firmware feels "closer" to the hazard.
**How to avoid:** Fix the host derivation (the source) AND add the firmware guard (defense-in-depth).
**Warning signs:** `convert_to_programmer` still sets `FLAG_CAN_ERASE` for algorithm 5.

### Pitfall 3: D-06 violation — keying the firmware erase guard on voltage/electrical.type
**What goes wrong:** Guarding `flash4_erase_execute` on `vpp_mv <= 5000` fails because the
W29C040 DB carries `vpp_mv=12000` (the chip-ID-read datum, not a program rail) → guard never
fires.
**Why it happens:** Intuition says "5V chip = low vpp_mv."
**How to avoid:** Key the guard on `handle->protocol == 0x05` (the D-06 boundary: "regulator
routing keyed on protocol, never on electrical.type/voltage").
**Warning signs:** any guard reading `handle->vpp_mv` to decide erase voltage.

### Pitfall 4: py3.12-masks-py3.11 CI trap (SAFE-02)
**What goes wrong:** Code passes locally on the devcontainer's py3.12 but fails CI on py3.11
(f-string backslashes — a SyntaxError on 3.11 but not 3.12; non-ruff-clean codegen).
**Why it happens:** The devcontainer default Python is 3.12; CI pins 3.11 (`ci.yml:32`).
**How to avoid:** Validate against py3.11 before claiming green (see `## SAFE-02 / CI` recipe).
**Warning signs:** backslashes inside f-string expression braces; hand-edited `messages.py`.

### Pitfall 5: Hand-normalizing generated `messages.py` after adding a FIX-01b MSG
**What goes wrong:** Editing the generated file to "tidy" it breaks the codegen drift gate
(`git diff --exit-code firestarter/messages.py`).
**Why it happens:** The file looks like ordinary Python.
**How to avoid:** Add the MSG to `messages.toml`, run `codegen.py`, commit the regenerated file
verbatim. The emitter is already ruff-clean (`reference_codegen_ruff_clean_emitter`).
**Warning signs:** a manual diff to `messages.py` not produced by codegen.

### Pitfall 6: `diff_db.py` flags unintended DB changes after `build_db.py` regen
**What goes wrong:** Regenerating the DB changes rows other than `page_size` (e.g., a drifted
upstream field), and `diff_db.py` / `test_diff_db_gate.py` fails.
**Why it happens:** `build_db.py` regenerates the whole DB from `infoic.xml`.
**How to avoid:** Run `diff_db.py` against the committed baseline; confirm ONLY `page_size`
additions appear. If other rows drift, investigate before committing.
**Warning signs:** diff_db output listing non-page_size deltas.

### Pitfall 7: `write -b` mistaken for skip-erase on a non-blank chip
**What goes wrong:** Using `-b` expecting it to skip erase; post-HARD-01 it skips only blank-check.
**How to avoid:** Use plain `write` (W29C040 auto-erases per page on the 0x4000+ path) or
`--skip-erase` explicitly. After FIX-01a, plain `write` no longer 12V-asserts on the erase path.
**Warning signs:** assuming `-b` ⇒ no erase (`reference_write_b_skips_erase`).

### Pitfall 8: Bench N=1 / port-identity drift
**What goes wrong:** Naming a result from one run or against the wrong port after a reseat.
**How to avoid:** N≥2 deterministic; verify `controller:` identity + live R1/R2 (270000 ± 25%)
each task. Leonardo chip-OUT-sideload-EXEMPT.
**Warning signs:** R1 out of range; controller identity mismatch.

---

## Code Examples

All [VERIFIED: direct source read] unless tagged otherwise.

### FIX-01a — the host flag derivation to change
```python
# Source: firestarter_app/firestarter/database.py:604-607 (convert_to_programmer)
simple_flags = 0
if full_eprom_data.get("electrical-type", "") in ("EEPROM", "Flash/EEPROM"):
    simple_flags |= FLAG_CAN_ERASE  # FLAG_CAN_ERASE is 0x02
programmer_data["flags"] = simple_flags
# FIX: gate on protocol — flash4 (0x05) auto-erases per page; no 12V bulk erase needed.
#   algo = programmer_data["algorithm"]   # already computed above (line 579)
#   if algo != 5 and electrical-type in {"EEPROM","Flash/EEPROM"}: simple_flags |= FLAG_CAN_ERASE
```

### FIX-01a / firmware defense-in-depth — the 12V erase path to guard
```cpp
// Source: firestarter/src/proms/flash_type_4.cpp:72-89 (flash4_write_init)
if (is_flag_set(FLAG_CAN_ERASE)) {
    if (!is_flag_set(FLAG_SKIP_ERASE)) {
        flash4_erase_execute(handle);   // ⚠ asserts CTRL_VPP_REGULATOR_ENABLE (12V) at :155
    } else { LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE); }
}
// Defense-in-depth: guard on handle->protocol == 0x05 (D-06 boundary), skip the 12V erase for flash4.
```

### PGSZ-02 — the heuristic to replace with a fallback form
```cpp
// Source: firestarter/src/proms/flash_type_4.cpp:92 (flash4_write_execute)
uint32_t page_size = flash4_page_size(handle->mem_size);
// → uint32_t page_size = handle->page_size ? handle->page_size : flash4_page_size(handle->mem_size);
```

### PGSZ-03 — the wire-field precedent to copy (read-strobe-us)
```python
# Source: firestarter_app/firestarter/constants.py:90-95
# Dev sweep knobs — Firmware sync: json_parser.c (key_read_settling, key_read_strobe)
JSON_KEY_READ_SETTLING_DELAY = "read-settling-delay"
JSON_KEY_READ_STROBE_US = "read-strobe-us"
```
```c
// Source: firestarter/src/json_parser.c:78-91,80 — the PROGMEM key + parser-table registration
const char key_read_strobe[]   PROGMEM = "read-strobe-us";
// ... {key_read_strobe, get_read_strobe}  in key_parsers[]
```

### FIX-01b — the existing ID-mode tables to reuse for the detect read
```c
// Source: firestarter/include/flash_utils.h:24-33 — ENTRY == FLASH_ENABLE_ID, EXIT == FLASH_DISABLE_ID
const byte_flip_t FLASH_ENABLE_ID[]  = {{0x5555,0xAA},{0x2AAA,0x55},{0x5555,0x90}};  // §6.6 ID-mode ENTRY
const byte_flip   FLASH_DISABLE_ID[] = {{0x5555,0xAA},{0x2AAA,0x55},{0x5555,0xF0}};  // §6.6 ID-mode EXIT
// detect: flash_execute_command(FLASH_ENABLE_ID); v=get_data(0x00002); flash_execute_command(FLASH_DISABLE_ID);
//         v==0xFF → locked; v==0xFE → unlocked.
```

### The native-test invariant assertion to reuse (FIX-01a no-12V; PGSZ page-size consume)
```cpp
// Source: firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp:109-120
static void assert_no_vpp_in_recording(const char* ctx) {
    for (int i = 0; i < bus_recording_count(); i++)
        if (recorded_reg(i) == CONTROL_REGISTER) {
            TEST_ASSERT_BITS_LOW_MESSAGE((uint8_t)CTRL_VPP_REGULATOR_ENABLE, recorded_data(i), ctx);
            TEST_ASSERT_BITS_LOW_MESSAGE((uint8_t)CTRL_VPP_P1_ENABLE,        recorded_data(i), ctx);
        }
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| ROADMAP FIX-01: "correct write path so W29C040 programs page 0" | **REFRAMED**: page-0 is hardware-blocked (§6.6 irreversible lockout); FIX-01 = T-93-CANERASE + detection | Phase 93 RCA (2026-06-27) | Phase 94 fixes the safety bug + diagnostics, NOT the algorithm |
| `FLAG_CAN_ERASE` "latent dead code for flash4" (Phase-74 belief) | **ACTIVE hazard** — `convert_to_programmer` sets it for all Flash/EEPROM incl. 0x05 | SAFE-01-PREFLIGHT Item 2 (Plan 01) | FIX-01a is required, not optional |
| firmware `flash4_page_size(mem_size)` capacity heuristic | datasheet-sourced per-chip `page_size` wire field + heuristic fallback | Phase 94 PGSZ (CR-01) | Under-sized families (e.g., AT29C020 256B) get correct page size |
| flash4 had its own SDP/poll/chip-id code | recomposed onto P5 `poll_readback` + flash_utils P4 | v1.16 Phase 89 | The detect read reuses flash_utils ENABLE_ID/DISABLE_ID tables |
| `-b` ⇒ skip erase | `-b` skips only blank-check; explicit `--skip-erase` for erase | v1.16 Phase 92 (HARD-01) | Use plain `write` for the FIX-01a-cleaned erase path |

**Deprecated/outdated:**
- ROADMAP Phase 94 Success Criterion #1 ("flash4 write path corrected so W29C040 programs page 0")
  — invalidated by Phase 93; the writable-region proof replaces it.
- The notion that `FLAG_CAN_ERASE` is harmless for flash4 — it is a 12V-on-5V hazard.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Per-chip page sizes for non-Winbond flash4 families (AT29C*, SST29EE*, AE29F*, AT29BV/LV*) — only W29C040=256 and W29C020=128 are datasheet-confirmed in-repo | PGSZ heuristic-vs-datasheet table | Authoring a wrong `page_size` would mis-size a page write. **Mitigation:** author ONLY datasheet-cited values; omit the rest (safe heuristic fallback). Do not graduate `[ASSUMED]` values to the DB. |
| A2 | AT29C020 native page is 256B (heuristic gives 128) — the example under-sized case | PGSZ table | If wrong, the cited example is off; PGSZ correctness is per-chip and gated by diff_db regardless. Verify against the Atmel AT29C020 datasheet during planning. |
| A3 | A host post-failure heuristic can reliably infer boot-block lockout from address range alone (fallback path) | FIX-01b fallback | The heuristic *infers* (doesn't confirm) the lock; a different fault in the first/last 16K would be mislabeled. **Mitigation:** prefer the firmware detect (confirms via FF/FE); use the heuristic only as a hint, worded as "may be locked." |
| A4 | The new FIX-01b MSG can take the next free id in the 0xB-range | FIX-01b plumbing | If the chosen id collides, codegen would error (caught at build). Scan `messages.toml` for the next free id before authoring. |
| A5 | `diff_db.py` baseline currently matches the committed DB (so a clean regen shows only page_size deltas) | PGSZ-03 gate | If the baseline already drifts, the gate fails for unrelated reasons. **Mitigation:** run `test_diff_db_gate.py` on a clean tree first to confirm the baseline. |

**If a value here cannot be datasheet-confirmed during planning, omit the per-chip `page_size`
for that chip — the heuristic fallback is the safe default (PGSZ-03).**

---

## Open Questions

1. **FIX-01b: firmware detect vs host heuristic — which scope?**
   - What we know: firmware detect is authoritative (reads FF/FE) and reuses existing ID tables
     (small); host heuristic is zero-firmware but only infers.
   - What's unclear: the firmware flash budget headroom on Leonardo after PGSZ (struct field +
     new parser + detect function + new MSG).
   - Recommendation: implement firmware detect (it's small — one extra read between existing
     tables); fall back to the host heuristic only if the build overflows. Decide at discuss.

2. **Phase 95 done-bar: new chip vs re-scope to ≥0x4000?**
   - What we know: page-0 is hardware-blocked on the seated chip; 0x4000+ writes byte-exact.
   - What's unclear: whether the operator can/will obtain an unlocked W29C040 sample.
   - Recommendation: **operator decision at Phase 94/95 planning** — this RESEARCH surfaces it but
     cannot decide it. Phase 94 delivers the writable-region proof regardless.

3. **PGSZ authoring: how many families to author now?**
   - What we know: only 2 of 27 flash4 chips have in-repo datasheets.
   - What's unclear: appetite for sourcing the other ~25 families' datasheets this milestone.
   - Recommendation: author the datasheet-confirmed values (W29C040, W29C020, and any family whose
     datasheet the operator provides); leave the rest on the heuristic fallback. PGSZ-02/03 (the
     mechanism) is the deliverable; full per-chip coverage is opportunistic.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO (`pio`) | firmware build + native tests | ✓ (project standard) | per `platformio.ini` | — |
| Leonardo + RURP Rev 2.0 + seated W29C040 | bench writable-region proof | ✓ (operator-seated, /dev/ttyACM0) | fw 3.0.0b10 host | — |
| Python 3.11 | SAFE-02 CI parity validation | ✗ in devcontainer (3.12 is default) | 3.12 present | **see SAFE-02 recipe** — use a 3.11 interpreter (pyenv/uv/docker) or rely on CI; do NOT assume 3.12 == 3.11 |
| `pip install -e '.[test]'` host install | gates + pytest | ✓ | editable, v1.17 | — |
| `pypdf` | datasheet extraction (research only) | ✓ | container Python | — |
| `node` (GSD tooling only) | GSD harness, not the build | ✗ on PATH | `/vscode/vscode-server/bin/linux-x64/*/node` | glob the vscode-server node |

**Missing dependencies with no fallback:** none that block code work.
**Missing dependencies with fallback:** py3.11 (the SAFE-02 trap) — validate via a real 3.11
interpreter or treat CI as the authority; never claim green from py3.12 alone.

---

## Validation Architecture

> This phase HAS production code (host DB pipeline + firmware) — native tests + CI gates + a
> bench writable-region proof. `workflow.nyquist_validation` is not disabled in config → enabled.

### Test Framework
| Property | Value |
|----------|-------|
| Firmware native | PlatformIO Unity, `[env:native]` recording-bus stub (`test/native/avr/test_val_flash4/`) |
| Host | pytest + ruff + mypy-watermark; gates wrapped as pytest (`tests/test_diff_db_gate.py`, `tests/test_check_dispatch_invariants.py`, `tests/test_val_wire_flash4.py`) |
| Firmware quick run | `pio test -e native -f "*test_val_flash4*"` (from `/workspaces/firestarter`) |
| Firmware full suite | `pio test -e native` |
| Host quick run | `pytest tests/test_val_wire_flash4.py tests/test_diff_db_gate.py -x` (from `/workspaces/firestarter_app`) |
| Host full suite | `pytest tests/ --cov=firestarter --cov-fail-under=70` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FIX-01a | `convert_to_programmer` does NOT set FLAG_CAN_ERASE for algorithm 5 | unit (host) | `pytest tests/test_val_wire_flash4.py -x` (add assertion) | ⚠ extend existing |
| FIX-01a (fw guard) | `flash4_erase_execute`/init asserts no 12V for 0x05 | native | `pio test -e native -f "*test_val_flash4*"` (add erase-path no-VPP test) | ⚠ add to existing suite |
| FIX-01b | boot-block detect emits clear MSG on locked-region timeout (or host heuristic hint) | native (fw) / unit (host fallback) | `pio test -e native -f "*test_val_flash4*"` | ❌ Wave 0 (new test) |
| FIX-02 | golden flash4 write + chip-id traces unchanged | native (golden) | `pio test -e native -f "*test_val_flash4*"` (test_golden_flash4_write/chip_id) | ✅ exists — must stay green |
| FIX-03 | lockstep wire contract (new key parses; no flag-parity break) | native + host wire | `pio test -e native` + `pytest tests/test_val_wire_flash4.py` | ⚠ extend |
| PGSZ-01 | per-chip `page_size` present + datasheet-cited in DB | unit (host) | `pytest tests/test_diff_db_gate.py -x` (intended additions) | ✅ gate exists |
| PGSZ-02 | firmware consumes `handle->page_size` (not heuristic) | native | `pio test -e native -f "*test_val_flash4*"` (page_size=128 on 512KB → 128B SDP boundary) | ❌ Wave 0 (new test) |
| PGSZ-03 | wire field round-trips; diff_db + check_dispatch pass | unit + native | `pytest tests/test_diff_db_gate.py tests/test_check_dispatch_invariants.py` + json_parser native | ✅ gates exist |
| SAFE-02 | constants parity green + py3.11 CI green | unit (host) | full `ci.yml` on py3.11 (see recipe) | ✅ ci.yml exists |

### Sampling Rate
- **Per task commit:** firmware `pio test -e native -f "*test_val_flash4*"`; host
  `pytest tests/test_val_wire_flash4.py tests/test_diff_db_gate.py -x` + `ruff check`/`ruff format --check`.
- **Per wave merge:** firmware `pio test -e native`; host `pytest tests/ --cov-fail-under=70`.
- **Phase gate:** full firmware native suite + full host CI green **on py3.11** + bench
  writable-region (≥0x4000) write→read→verify SHA match before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] New native test: FIX-01a firmware erase-path no-12V for 0x05 (extend `test_val_flash4.cpp`)
- [ ] New native test: FIX-01b boot-block detect path (locked-region timeout → new MSG) — only if firmware detect chosen
- [ ] New native test: PGSZ-02 firmware consumes `handle->page_size` (page_size=128 on 512KB handle → SDP at 128B boundary)
- [ ] Extend `tests/test_val_wire_flash4.py`: assert `(flags & FLAG_CAN_ERASE) == 0` for the rep chip (FIX-01a) + `page-size` key present when DB supplies it (PGSZ-03)
- [ ] New host test (if fallback chosen): post-failure boot-block heuristic hint
- [ ] Confirm `tests/test_diff_db_gate.py` baseline is clean before adding page_size rows (A5)

---

## Security Domain

> `security_enforcement` is absent in config → enabled. This phase's security surface is the
> **12V-on-5V hardware-damage path (FIX-01a)** and the **non-bypass guard (SAFE-01/02)**.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | yes | `json_parser.c` silently skips unknown fields; new `page-size` parser must bound-check (reject absurd page sizes; 0 → heuristic fallback) |
| V6 Cryptography | no | — |
| V12/hardware-safety (project-specific) | **yes** | FIX-01a: never assert 12V (CTRL_VPP_REGULATOR_ENABLE) on a 5V chip; firmware guard keyed on protocol (D-06); host never sets FLAG_CAN_ERASE for 0x05 |

### Known Threat Patterns for this stack
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| 12V boost regulator asserted on 5V-only W29C040 (T-93-CANERASE) | Tampering / DoS (hardware destruction) | FIX-01a: host omits FLAG_CAN_ERASE for 0x05 + firmware skips `flash4_erase_execute` 12V on protocol 0x05 (D-06) |
| Hand-crafted JSON re-introduces the hazardous flag | Tampering | Firmware defense-in-depth guard (don't rely on host alone) |
| `chip_resolver.resolve_chip` bypass via `--force` | Elevation | SAFE-01: never bypassed; W29C040 flows through `supported`; no `--force` in any plan |
| Unknown/absurd `page-size` over the wire | Tampering | V5: bound-check the new parser; 0/absent → safe heuristic fallback |
| py3.12-masks-py3.11 CI bypass (a real failure shipped as "green") | (process) | SAFE-02: validate on py3.11; CI pins 3.11 |

**SAFE-01 precondition restated:** FIX-01a MUST land + be verified before Phase 95 bench writes
proceed without `--skip-erase`. Until then, any non-`--skip-erase` `firestarter write W29C040`
asserts 12V on the 5V chip.

---

## SAFE-02 / CI — py3.11 Validation Recipe

### What CI actually runs (`firestarter_app/.github/workflows/ci.yml`, py3.11 pinned)
1. Catalog validity: `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check`
2. **Codegen drift gate:** regenerate `firestarter/messages.py` + `git diff --exit-code` (FIX-01b MSG must be committed via codegen, not hand-edited)
3. Vector codegen drift gate (`frame_vectors.py`)
4. `pip install -e .[test]`
5. `ruff check firestarter/ tests/`
6. `ruff format --check firestarter/ tests/`
7. `python tools/check_mypy_watermark.py` (mypy strict on 8 modules)
8. `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70`
   — **this is where `diff_db.py` (test_diff_db_gate.py) and `check_dispatch.py`
   (test_check_dispatch_invariants.py) run** (PGSZ-03 gates are pytest-wrapped, not standalone CI steps).
9. Smoke: `firestarter --help`

### The py3.12-masks-py3.11 trap (why local green ≠ CI green)
- **f-string backslashes:** `f"...{x}\n..."` with a backslash *inside* the `{}` expression is a
  SyntaxError on 3.11 but allowed on 3.12. The devcontainer runs 3.12 → silently passes locally.
- **Non-ruff-clean codegen:** if a new MSG's format string produces a `messages.py` that isn't
  ruff-format-stable, step 6 fails on CI even if local ruff (different cache/version) passes.

### Recommended local validation against py3.11
- Use a real 3.11 interpreter (pyenv `3.11`, `uv venv --python 3.11`, or a python:3.11 container),
  then run the CI step list above verbatim. Do NOT rely on the devcontainer's 3.12.
- Minimum pre-claim check: `ruff check`, `ruff format --check`, the codegen drift gate
  (`codegen.py … && git diff --exit-code firestarter/messages.py`), and
  `pytest tests/test_diff_db_gate.py tests/test_check_dispatch_invariants.py tests/test_val_wire_flash4.py`.
- Treat CI on py3.11 as the **authority**; never mark SAFE-02 green from a py3.12-only run.

---

## Sources

### Primary (HIGH confidence)
- `firestarter/datasheets/0x05-FLASH-AMD-STD/W29C040.pdf` §6.6 + p10 (Identification/Boot-Block-Lockout-Detection codes) + p11 (Boot-Block-Lockout-Enable codes) — extracted verbatim via pypdf 2026-06-27. **No unlock command exists.**
- `firestarter/datasheets/0x05-FLASH-AMD-STD/W29C020.pdf` §6.2 — "128 bytes per page", T_BLC 200µs, A7–A17 page address.
- `.planning/phases/93-.../evidence/93-RCA-FINDINGS.md` — H5 CONFIRMED (silicon boot-block lockout); exact 16K boundary; FIX-01 hand-off.
- `.planning/phases/93-.../evidence/safety/SAFE-01-PREFLIGHT.md` — Item 2 RED/HIGH (T-93-CANERASE causal chain).
- Direct source reads: `flash_type_4.cpp`, `primitives.cpp`, `flash_utils.cpp`, `flash_utils.h`, `firestarter.h`, `json_parser.c`, `database.py`, `constants.py`, `eprom_operations.py`, `build_db.py`, `test_val_flash4.cpp`, `messages.toml`, `ci.yml`.
- `chip_database.json` flash4 enumeration (27 chips) via `EpromDatabase` — heuristic-vs-capacity audit.

### Secondary (MEDIUM confidence)
- `firestarter/CLAUDE.md`, `firestarter_app/CLAUDE.md`, `/workspaces/CLAUDE.md` — dispatch order, lockstep rules, codegen-ruff-clean rule, CI gate list.
- `93-RESEARCH.md` — flash4 internals, D-06 boundary, golden-trace structure.

### Tertiary (LOW confidence — flagged for datasheet confirmation)
- Per-chip page sizes for AT29C*/SST29EE*/AE29F*/AT29BV-LV* families — `[ASSUMED]` (Assumptions A1/A2); must be datasheet-sourced or omitted (heuristic fallback).

## Metadata

**Confidence breakdown:**
- FIX-01 reframing (page-0 hardware-blocked): HIGH — §6.6 datasheet extracted; no unlock command; RCA H5 confirmed by exact 16K boundary.
- FIX-01a (T-93-CANERASE): HIGH — exact source line + causal chain verified; SAFE-01-PREFLIGHT corroborates.
- FIX-01b (boot-block detect): HIGH on the datasheet sequence + reuse-of-existing-tables; MEDIUM on the firmware-budget feasibility (Open Q1).
- PGSZ mechanism: HIGH — `read-strobe-us` wire-field precedent verified end-to-end; per-chip *values* LOW beyond W29C040/W29C020 (Assumptions A1/A2).
- Validation/CI: HIGH — gate invocation + py3.11 trap verified against `ci.yml`.

**Research date:** 2026-06-27
**Valid until:** 2026-07-27 (stable in-repo firmware/host; re-verify if `a296195` base or `ci.yml` py-pin changes)
