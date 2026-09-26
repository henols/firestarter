# Architecture Research

**Domain:** Community chip-validation command (`firestarter dev test <chip>`) integrated into the existing Firestarter host CLI + Arduino firmware
**Researched:** 2026-07-02
**Confidence:** HIGH (grounded in the actual source at `firestarter_app/firestarter/*.py`; firmware identity/error codes read from `firestarter/include/*.h` + `firestarter/src/*.cpp`)

> This is integration research for an EXISTING codebase, not greenfield ecosystem research. Every recommendation names the real file/function it touches. The one place the template's "standard architecture" ideal collides with reality is called out explicitly (auto-capture gaps in the transport/voltage layers).

## Standard Architecture

### System Overview

`dev test` is a NEW orchestration layer that sits ABOVE the existing per-op service methods and reuses them verbatim. It is architecturally a sibling of `dev validate-family` (the closest analog): a `dev` sub-command that composes `EpromOperator` methods and emits an artifact. The key difference: `validate-family` reads an authored spec JSON and runs ONE composed cycle per family; `dev test` DERIVES its op list per-chip from the DB and runs EACH op as an isolated, non-fatal step.

```
┌───────────────────────────────────────────────────────────────────────┐
│  CLI layer  (cli_handlers.py)                                           │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  NEW @dev.command("test")  dev_test(app, eprom, destructive, …)   │  │
│  │  provenance prompts (click.prompt) → then hand off to engine      │  │
│  └───────────────────────────────┬─────────────────────────────────┘  │
├──────────────────────────────────┼─────────────────────────────────────┤
│  Test-plan engine  (NEW module: chip_test.py)                          │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │ derive_plan()│  │ run_step() (non-  │  │ DiagnosticReport model + │  │
│  │ proto→ops    │  │ fatal wrapper)    │  │ dual-output renderer     │  │
│  └──────┬───────┘  └────────┬─────────┘  └────────────┬─────────────┘  │
├─────────┼───────────────────┼──────────────────────────┼───────────────┤
│  Existing service layer  (REUSED verbatim — DO NOT re-implement)       │
│  resolve_chip() · EpromOperator.{check_eprom_id, read_eprom,           │
│  write_eprom, verify_eprom, erase_eprom, check_eprom_blank} ·          │
│  HardwareManager.{read_vpp_voltage, read_vpe_voltage} · EpromDatabase  │
├─────────────────────────────────────────────────────────────────────────┤
│  Transport  (serial_comm.py)  →  COBS+CRC8 @ 250000  →  Arduino firmware │
│  MSG_OK "version:board" identity · MSG_ERR_* codes · VPP/VPE monitor    │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Where it lives |
|-----------|----------------|----------------|
| `dev test` CLI handler | Parse args (`--destructive`, `--submit`, `--output-dir`), run provenance prompts, invoke engine, set exit code | NEW `@dev.command("test")` in `cli_handlers.py` (sibling of `dev_validate_family`, line ~1452) |
| Test-plan engine | Derive supported-op list from the chip's protocol/type; run each op non-fatally; assemble the report | NEW module `firestarter/chip_test.py` (host package) |
| Op step runner | Call one existing `EpromOperator` method, catch its result + firmware error code, never abort the sweep | NEW `run_step()` inside the engine |
| Diagnostic report model | Two-tier dataclass (auto-capture + prompted); dual-output render (human table + fenced JSON) | NEW dataclass in engine module |
| Submission flow | `gh issue create` if `gh` present/authed, else prefilled browser URL | NEW `firestarter/submit.py` (thin, `shutil.which("gh")` + `subprocess` + `webbrowser`) |
| Existing service methods | Actual serial ops — unchanged | `eprom_operations.py`, `hardware.py`, `chip_resolver.py`, `database.py` |

## The Four Questions (grounded answers)

### (1) Where the test-plan engine lives + how it derives supported-ops

**Where it lives:** a NEW host module `firestarter/chip_test.py`, driven by a NEW `@dev.command("test")` in `cli_handlers.py`. It is NOT firmware — the derivation is pure host logic over DB fields already loaded at runtime.

**Critical grounding — `classify()` is a BUILD-TIME function, not runtime.** `classify()` lives in `tools/build_db.py:324` and runs when the DB is generated from `infoic.xml`. Its output is FROZEN into `chip_database.json` as three fields the runtime reads: `electrical.type` (→ host key `electrical-type`), `programming.algorithm` (→ host key `protocol-id`), and `pinout`. **The engine must NOT call `classify()` at runtime.** It derives the op list from what `classify()` already baked in, exposed through:

- `EpromDatabase.get_eprom(name)` → `_map_data()` (database.py:364) yields the runtime dict with `protocol-id`, `electrical-type`, `info-flags`, `memory-size`, `chip-id`, `page_size`.
- `resolve_chip(name, db)` (chip_resolver.py:16) → `convert_to_programmer()` — the programmer-config dict + its guards. This is the SAME chokepoint every existing chip-op uses.

**The protocol→capabilities mapping to build ON TOP of these fields.** There is no existing single "protocol→ops" table; you construct it from the axes `classify()` produced. The authoritative facts to key on:

| Axis | Runtime source | Meaning for capability derivation |
|------|----------------|-----------------------------------|
| `protocol-id` (algorithm) | `_map_data` line ~420 / `convert_to_programmer` `algorithm` | Firmware dispatch key. `PROTOCOL_MAP` (database.py:35) names them: 0x05 FLASH_AMD_STD, 0x06 FLASH_AMD_ALT, 0x07 EPROM_STD, 0x08 EPROM_QUICK, 0x0B EPROM_LEGACY, 0x0D EEPROM_POLL, 0x10 FLASH_INTEL, 0x28 SRAM_STD |
| `electrical-type` | `_map_data` `electrical-type` | `UV-EPROM` / `EEPROM` / `Flash/EEPROM` / `SRAM`. The technology-aware destructiveness axis (UV = no electrical erase; small-region write). |
| erase-capability | `convert_to_programmer` sets `FLAG_CAN_ERASE` (0x02) when `electrical-type ∈ {EEPROM, Flash/EEPROM}` AND `algorithm != 5` (database.py:581–595) | Whether an `erase` step is even applicable. **Reuse this exact predicate** — do not re-derive erase-capability independently. |
| SRAM/FRAM | `_SRAM_PROTO_IDS = {0x0E,0x27,0x28,0x29}` (eprom_operations.py:1656) | Blank-check is N/A (short-circuits, eprom_operations.py:1669); these have no factory-blank state. |
| chip-id present | `info-flags & 0x20` set from `programming.chip_id_check`; `chip-id` key present | Whether the `id` step can produce an expected-vs-actual comparison. |
| `support_status` | raw config via `db.get_eprom_config()` (NOT carried through `_map_data`) | `resolve_chip` refuses non-`supported` chips (chip_resolver.py:54). See design note below. |

**Recommended derivation shape** (host-side, in `chip_test.py`):

```
def derive_plan(runtime_dict, raw_config, destructive) -> list[Step]:
    etype = runtime_dict["electrical-type"]
    proto = runtime_dict["protocol-id"]
    can_erase = bool(programmer_flags & FLAG_CAN_ERASE)   # from convert_to_programmer
    is_sram   = etype in ("SRAM","FRAM") or proto in _SRAM_PROTO_IDS
    steps = ["id", "read"]                        # always non-destructive
    if not is_sram: steps.append("blank")         # blank-check N/A for SRAM
    if destructive:
        steps.append("write")                     # UV → small-region; else full
        steps.append("verify")
        if can_erase: steps += ["erase", "blank"] # electrical erase round-trip
    return steps
```

**Design note — `support_status` gate must be handled deliberately.** `resolve_chip()` RAISES `ChipNotImplementedError` for any chip whose `support_status != "supported"` (chip_resolver.py:55) — BEFORE any wire dict is built. That is exactly the community-testing population `dev test` targets (chips the maintainer can't verify are often `protocol-not-implemented` / `adapter-required`). The engine therefore must NOT resolve through the guarded `resolve_chip` for the plan-derivation step. Two safe options: (a) read `raw_config` via `db.get_eprom_config()` + build the runtime dict via `db.get_eprom()`/`convert_to_programmer()` directly (bypassing the guard for the DIAGNOSTIC sweep only), recording `support_status` into the report; or (b) add a `require_supported=False` seam to `resolve_chip`. Option (a) touches no shared code and keeps the guard authoritative for real ops — **recommended**. The open question "does a community PASS graduate `support_status`?" (research/questions.md) is downstream of this and stays a maintainer-triage decision, not an auto-mutation.

### (2) Running each op as an independent non-fatal step

**The reuse targets (all on `EpromOperator`, all take the same `(eprom_name, eprom_data_dict, operation_flags=…)` shape):**

| Step | Method | Return contract |
|------|--------|-----------------|
| id | `check_eprom_id()` (eprom_operations.py:1695) | `Tuple[bool, Optional[int]]` — the detected-id fingerprint source |
| read | `read_eprom()` (line 622) | `bool` (writes a `.bin`) |
| write | `write_eprom()` (line 1555) | `bool` |
| verify | `verify_eprom()` (line 1592) | `bool` |
| erase | `erase_eprom()` (line 1628) | `bool` |
| blank | `check_eprom_blank()` (line 1658) | `bool` (SRAM short-circuits to `False`+warning) |

**Non-fatal wrapping.** Each method already runs inside `_operation_context` (setup + guaranteed disconnect, line 347) and `_run_state_machine` (line 392). The state machine CATCHES `SerialError`/`SerialTimeoutError`/`EpromOperationError` and returns `(False, str(e))` rather than propagating — so a single failed op does NOT crash the process today. The engine wraps each call in its own `try/except EpromOperationError` (and `ChipNotImplementedError`/`ProtocolNotImplementedError`) so even the exceptions that DO escape (e.g. `ProtocolNotImplementedError` from `_raise_for_error_response`, line 84) are recorded as a step FINDING and the loop continues. This is the W29C040 locked-boot-block lesson made structural.

**Capturing the EXACT firmware error code — this is the one real gap in the reuse path.** Firmware error codes are available as `response.id` (e.g. `0xBB` `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`, `0xA4` `MSG_ERR_EMPTY_INPUT`, `0xB3` `MSG_ERR_FL4_VERIFY_TIMEOUT`, `0xBC` `MSG_ERR_FL4_BOOT_BLOCK_LOCKED` — full list in `firestarter/messages.py:85–117`). But `_run_state_machine` today collapses errors to `(False, str(e))` — the numeric `.id` is only used inside `_raise_for_error_response` to pick the exception subclass, then discarded. **Options, cheapest first:**
1. **Recover the code from the message text** — `messages.py` maps id↔name↔template; `frame_parser._decode_param`/`Response` carry `.id`. The engine can reverse-lookup the code from the exception message. Fragile.
2. **Add a code-preserving seam (recommended):** introduce a typed `EpromOperationError.error_code: Optional[int]` populated in `_raise_for_error_response` (it already reads `response.id`), so every escaping exception carries the exact byte. Small, backward-compatible edit to `eprom_operations.py`; every existing caller ignores the new attribute. This is the single most valuable modification for the whole diagnostic contract.

**Isolation between steps.** Each `EpromOperator` op opens and closes its own serial connection (`_operation_context`'s `finally: self._disconnect_programmer()`), so steps are already fully isolated — a hung/failed step leaves no lingering connection state for the next. The engine can call them back-to-back safely.

### (3) The two-tier diagnostic-report data model

**AUTO-CAPTURABLE today (grounded in what the running system actually reports):**

| Field | Source (real name) | Notes / caveats |
|-------|--------------------|-----------------|
| FW version + board | `comm.programmer_info` = `"<version>:<board>"` string; firmware `FW_VERSION VERSION ":" RURP_BOARD_NAME` (`firestarter/include/firestarter.h:30`), emitted by `fw_get_version` | Already parsed during `find_and_connect` FW-probe (serial_comm.py:686). Engine reads `comm.programmer_info`; split on `:`. |
| Host app version | `firestarter.__version__` | Trivially available (already imported into `cli_handlers.py:32`). |
| Chip-ID expected vs actual | expected = `runtime_dict["chip-id"]`; actual = `check_eprom_id()[1]` | `check_eprom_id` returns the detected id (or extracts it from the ERROR message via `extract_hex_to_decimal`, line 1721). Wrong-chip signal. |
| Protocol path | `runtime_dict["protocol-id"]` + `PROTOCOL_MAP` name (database.py:35) | Post-v1.20 dispatch is protocol-only, so the protocol byte IS the handler. |
| Per-op result + exact error code | step bool/verdict + `response.id` (needs the seam from Q2) | The `messages.py` id→name table renders `0xBB`→`MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`. |
| Byte-mismatch fingerprint | Compute host-side from the read/verify `.bin` outputs | `consistency_check_eprom` already computes % divergence + first-offset + offset list (eprom_operations.py:836–863) — **reuse that classification logic** (all-0xFF→blank/contact; high-address clustering→address-line; scattered→transport). Pattern-classify it into the seed's 3 buckets. |
| DB entry used | `runtime_dict` + `raw_config["support_status"]` / `unsupported_reason` | Includes `support_status`, `protocol-id`, `vpp_mv`, pin config, sizes the host assumed. |
| Transport health | **PARTIAL — real gap** | There are NO persistent COBS/CRC/retry/timeout counters today. Resync is only `logger.debug/info`-logged (serial_comm.py:360 "re-syncing"), never tallied. To auto-capture this the engine must either (a) attach a `logging.Handler` during the sweep and count resync/timeout log records, or (b) add counters to `SerialCommunicator`. Option (a) is zero-risk to the transport; recommend it for v1 and note the limitation in the report. |
| Measured VPP/VPE | **PARTIAL — real gap** | `HardwareManager.read_vpp_voltage`/`read_vpe_voltage` (hardware.py:253/259) return **`bool`** and PRINT the voltage to stdout via `_read_voltage_loop` (line 208 `print(...)`); they do NOT return the mV number. To capture the tester's actual rail voltage into the report, add a value-returning variant (e.g. `sample_vpp_mv(samples=N) -> int` that parses `MSG_DATA_VPP_VOLTAGE` 0xE4 / `MSG_DATA_VPE_VOLTAGE` 0xE5 frames and returns the reading instead of only printing). This is a genuine new component, not a reuse. |

**MUST-PROMPT (firmware genuinely cannot self-report — collect BEFORE the sweep so no report lands blank):**

| Field | Why it can't be auto-captured | Prompt shape |
|-------|-------------------------------|--------------|
| Shield revision | The EEPROM `hw_revision` byte **cannot distinguish Rev 2.2 / Rev 2.0 / modified Rev 0** (documented in CLAUDE.md constants + MEMORY: they read the same byte), yet it was decisive for Bug A. `hw` command reads only the ambiguous byte. | `click.prompt` with choices incl. "not sure"; pre-fill the auto-read `hw_revision` byte as a hint. |
| Chip provenance | Physical history unknowable to firmware: new/blank vs pulled/used; whether tester owns a UV eraser. | `click.confirm`/`prompt`. The eraser answer also gates the UV small-region-write retry guidance. |
| Pot adjustments | Whether the tester turned the voltage trim — no self-report path. | `click.confirm`. |

**Design consequence (locked in the seed):** prompts run FIRST, before any op, so a beautiful auto-report is never un-actionable for want of the shield rev.

### (4) Suggested build order + new vs modified components

**New components:**
- `firestarter/chip_test.py` — engine (`derive_plan`, `run_step`, `DiagnosticReport` dataclass, dual-output renderer).
- `firestarter/submit.py` — tiered `--submit` (gh / browser URL).
- `@dev.command("test")` handler in `cli_handlers.py`.
- New value-returning voltage sampler in `hardware.py` (for measured VPP/VPE).

**Modified components (small, backward-compatible):**
- `eprom_operations.py` — add `error_code` attribute preserved through `_raise_for_error_response` (Q2 seam). Optionally a small-region UV write helper (or reuse `write_eprom` with `address_str` + a truncated source image).
- `chip_resolver.py` — OPTIONAL `require_supported=False` seam (or bypass via `get_eprom`+`convert_to_programmer` in the engine — preferred, no shared-code change).
- `hardware.py` — add the mV-returning sampler alongside the existing bool-returning monitors.

**Build order (dependency-respecting):**

1. **Error-code seam** (`eprom_operations.py` `error_code` attribute). Foundational — every step result depends on it. Smallest change, biggest leverage.
2. **Test-plan engine skeleton** (`chip_test.py`): `derive_plan()` over DB fields + a non-fatal `run_step()` that composes the existing `EpromOperator` methods. Pure host logic, unit-testable with `EpromDatabase(skip_local_override=True)` + mock operator (same test seam `validate-family` uses).
3. **Report data model + dual-output renderer**: dataclass with auto/prompt tiers; human table + fenced ```json. Byte-mismatch classifier reuses `consistency_check_eprom`'s divergence math.
4. **Provenance prompts** (`click.prompt` in the handler, run before sweep).
5. **Measured-voltage capture** (`hardware.py` mV sampler + wire into the write step). Independent of 1–4; can land in parallel but is the highest-hardware-risk piece.
6. **`dev test` CLI handler** wiring 2–5 together + `--destructive`/`--output-dir`; non-destructive default with the loud "only N of M tests ran" message.
7. **Submission flow** (`submit.py` + `--submit`). Depends on the report existing (3). Independent of hardware.
8. **Transport-health capture** (log-handler counter). Lowest priority; degrade gracefully if absent (report "not measured").

Phases 1–4 + 6 are the software MVP (no bench needed, fully unit-testable). Phase 5 is the only hardware-gated piece. Phase 7 is pure host/tooling. This mirrors the project's standing "software-first, hardware-gated last" discipline.

## Architectural Patterns

### Pattern 1: Compose-don't-reimplement (the `validate-family` precedent)
**What:** the engine calls existing `EpromOperator` methods; it never re-opens serial or re-implements a state-machine loop.
**When:** every op step.
**Trade-off:** inherits every method's exact behavior (good: byte-for-byte parity with `firestarter write`; constraint: each op re-connects — slightly slower, but gives free step isolation). This is the documented reuse rule from `write_cycle_eprom`/`consistency_check_eprom` ("Do NOT refactor into a parallel read implementation").

### Pattern 2: Non-fatal step wrapper
**What:** `run_step()` catches `EpromOperationError`/`ProtocolNotImplementedError`/`ChipNotImplementedError` per step, records `{op, ok, error_code, detail}`, continues.
**When:** the whole sweep.
**Trade-off:** a report can show mostly-FAIL and still be the valuable artifact (the surprise is the value).

### Pattern 3: Two-tier field contract (auto + prompt), prompts-first
**What:** collect human-only provenance up front; auto-capture the rest during the sweep; render both tiers into one document.
**Trade-off:** slightly more interactive friction, but eliminates un-actionable reports.

## Anti-Patterns

### Anti-Pattern 1: Calling `classify()` at runtime
**What people do:** import `tools/build_db.classify` into the engine to "re-derive" the family.
**Why it's wrong:** `classify()` is a build-pipeline function operating on raw `infoic.xml` ints (`type_int`, `pm_idx`, `flags`) that are NOT present in the runtime dict; it also mutates pinout. It would drift from the frozen DB truth.
**Do this instead:** read `electrical-type` + `protocol-id` + the `FLAG_CAN_ERASE` predicate that `convert_to_programmer` already computes.

### Anti-Pattern 2: Routing the diagnostic sweep through the `resolve_chip` support-status guard
**What people do:** call `resolve_chip(name)` and let it raise for `protocol-not-implemented` chips.
**Why it's wrong:** those are exactly the chips a community tester is validating; the guard would abort before a single finding.
**Do this instead:** bypass via `get_eprom()`+`convert_to_programmer()` for the sweep, record `support_status` in the report, keep the guard authoritative for real user ops.

### Anti-Pattern 3: Treating `read_vpp_voltage()`'s return as the measurement
**What people do:** assume the bool return carries the voltage.
**Why it's wrong:** it returns success/failure and PRINTS the mV; the number is not returned.
**Do this instead:** add a value-returning sampler that parses `MSG_DATA_VPP_VOLTAGE`/`MSG_DATA_VPE_VOLTAGE` frames.

## Integration Points

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `dev test` handler ↔ engine | direct call, `AppContext` DI (ctx.obj) | Same DI container every handler uses (cli_handlers.py:79). |
| engine ↔ `EpromOperator` | direct method calls on `app.eprom_operator` | Reuse target; needs the `error_code` seam. |
| engine ↔ `EpromDatabase` | `get_eprom`, `get_eprom_config`, `convert_to_programmer` | Bypass `resolve_chip` guard for the sweep. |
| engine ↔ `HardwareManager` | new mV sampler | Only new intra-host method needed. |
| host ↔ firmware | `serial_comm.py` COBS+CRC8; `response.id` error bytes, `programmer_info` identity | No firmware change required for v1 (all diagnostic data already crosses the wire). |
| submit ↔ GitHub | `subprocess` `gh issue create` OR `webbrowser` prefilled URL | `shutil.which("gh")` + auth probe; auto-label → `gsd-inbox`. |

## Sources

- `firestarter_app/firestarter/cli_handlers.py` (Click `dev` group, `dev_validate_family` analog, `AppContext`, `@map_typed_errors`) — HIGH
- `firestarter_app/firestarter/eprom_operations.py` (op method signatures, `_run_state_machine`, `_raise_for_error_response`, `consistency_check_eprom` divergence math, `_SRAM_PROTO_IDS`) — HIGH
- `firestarter_app/firestarter/database.py` (`PROTOCOL_MAP`, `_map_data`, `convert_to_programmer` FLAG_CAN_ERASE derivation) — HIGH
- `firestarter_app/firestarter/chip_resolver.py` (`resolve_chip` support_status + algorithm guards) — HIGH
- `firestarter_app/firestarter/serial_comm.py` (`programmer_info` `version:board`, FW-probe, resync logging) — HIGH
- `firestarter_app/firestarter/hardware.py` (`read_vpp_voltage`/`read_vpe_voltage` bool-return + print) — HIGH
- `firestarter_app/firestarter/messages.py` (MSG_ERR_* / MSG_OK_* / MSG_DATA_* code table) — HIGH
- `firestarter_app/tools/build_db.py:324` (`classify()` — build-time, not runtime) — HIGH
- `firestarter/include/firestarter.h` (`FW_VERSION VERSION ":" RURP_BOARD_NAME`) — HIGH
- `.planning/seeds/community-chip-validation-command.md`, `.planning/notes/dev-test-design-decisions.md` — HIGH (locked decisions)

---
*Architecture research for: `firestarter dev test <chip>` community chip-validation command (v1.21)*
*Researched: 2026-07-02*
