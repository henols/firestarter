# Phase 119: LOCK — SDP-enable + command surface (FW half) - Research

**Researched:** 2026-07-28
**Domain:** AVR firmware command dispatch + admission guards, AT28C SDP-enable sequence emission, PlatformIO native (Unity) proof surfaces, cross-repo source-scanning gates
**Confidence:** HIGH on every in-tree code claim (all read from live source at firmware `1880054`); HIGH on the flash and no-DEV_TOOLS-build figures (measured in this session); HIGH on the datasheet lock body (adjudicated in `.planning/research/SUMMARY.md` CONFLICT 1 with three-document agreement); MEDIUM on the predicted lock golden-trace index (derived arithmetically and cross-validated against an in-tree assertion, but not yet dumped)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

`119-CONTEXT.md` is the authority for this phase. It is 52 KB of adjudicated decisions (D-01..D-20) and this research **does not restate it**. What follows is the delta: which of its claims verified, which need amendment, and the seven answers the planner asked for.

### Locked Decisions

D-01..D-20 in `119-CONTEXT.md` `<decisions>` are locked verbatim. Load-bearing summary of what this research had to honour:

- **D-01/D-02** — `is_memory_cmd()` = `{CMD_READ, CMD_WRITE, CMD_ERASE, CMD_BLANK_CHECK, CMD_CHECK_CHIP_ID, CMD_VERIFY, CMD_SDP_UNLOCK, CMD_SDP_LOCK}`, **no `#ifdef` inside it**; the cmd 7/8 behaviour change is TAKEN and must be recorded as a deliberate safety tightening.
- **D-03** — slots **9** and **10**; LOCK-03 gates LOCK-02.
- **D-04** — proof = a second `[env:native_nodevtools]` PLUS a `firestarter_app` source-scan gate with a planted-violation fixture. Folded todo item 4 discharged as a by-product.
- **⚠ D-05** — **LOCK-04 cannot be implemented as written.** Do not edit `REQUIREMENTS.md`; record the correction in the phase artifacts.
- **D-06/D-07** — ONE guard at the op layer: NULL `main` ⇒ `MSG_ERR_NOT_SUPPORTED`. Generic, not SDP-scoped.
- **⚠ D-08** — Phase 121's DEVTEST-01 firmware half lands here; the cross-family sweep is mandatory; `_SRAM_PROTO_IDS` is identified here, acted on in Phase 120.
- **D-09/D-10** — `EEPROM_SDP_ENABLE[3]` `0x0D`-local with external linkage; three-way byte-identity guard + a no-payload stream-length assertion; `flash_utils.h` byte-frozen.
- **D-11** — `delay(AT28C_TWC_MAX_MS)` and stop. No completion poll on the lock path.
- **D-12/D-13** — OK-with-honest-text; `response_code` untouched; unlock reuses `0x5E`/`0x5F`, lock gets a new pair.
- **D-14** — shared `micros()` bracket + t_BLC budget check helper.
- **⚠ D-15** — `3348 B` is superseded; judge against the live figure and show the arithmetic.
- **⚠ D-16** — page-load worst-case t_BLC measurement TAKEN, reported **once**, aimed at the **conflation** framing.
- **D-17/D-18/D-19/D-20** — bench on **three** boards, `autonomous: true` (all sockets empty), proceed-and-record-not-measured on failure, numbers in `119-MEASUREMENT.md`.

### Claude's Discretion

Six items are listed in CONTEXT.md `### Claude's Discretion`. **Three of them are resolved by facts this research established** — see `## Discretion Items Resolved by Evidence` below. The other three stay open for the planner.

### Deferred Ideas (OUT OF SCOPE)

Copied intent verbatim from CONTEXT.md `<deferred>`: `prove-pio-dev-flag-fails-closed.md` items 1–3 (999.15/gh#8); a per-byte runtime t_BLC WARN in the page-load hot path; a distinct "compiled out" refusal id for `CMD_DEV_*`; a pre-dispatch `protocol != 0x0D` check in `configure_memory`; `default:` arms in all six `configure_*` handlers; a throwaway raw-frame bench script emitting `cmd: 9`/`cmd: 10`; four distinct catalog ids; deleting the host's `_SRAM_PROTO_IDS` workaround; widening the trace recorder to a data-bus-direction strobe kind; the `infoic.xml` `page_size` decode phase; Unity-teardown SIGABRT root cause; SDP-F7/SDP-F8. **Plus the entire host CLI surface (Phase 120) and all docs corrections (Phase 121).**
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LOCK-01 | SDP-enable = 3 loads + `t_WC`, no data payload (`AA→0x5555`, `55→0x2AAA`, `A0→0x5555`), per Atmel doc0270 §19 note 2 | Datasheet body settled with 3-document agreement (F-A). Emission path, table declaration shape and the exact `t_WC` constant located (F-J, F-Q). Predicted golden trace computed (F-I). |
| LOCK-02 | `CMD_SDP_UNLOCK` / `CMD_SDP_LOCK` invocable in their own right — no payload, no host `DONE` round-trip, `init`/`end` NULL | The full standalone wire shape traced through the state machine: **4 host ACKs, 7 framed report lines, zero `#` data frames, zero `DONE` string** (F-U). `CMD_ERASE` is the working precedent. `op_execute_simple_operation` is the wrapper. |
| LOCK-03 | `is_memory_cmd()` replaces the ordinal guard, proven identical with and without `-D DEV_TOOLS` | Accepted set enumerated for both configurations (F-B). **`CMD_DEV_ADDRESS`/`CMD_DEV_REGISTER` are themselves `#ifdef DEV_TOOLS` (F-C)** — constrains the truth-table test's spelling. **No-DEV_TOOLS build empirically compiles and passes 112/112 (F-G).** Predicate must be header-inline to be natively linkable (F-F). |
| LOCK-04 | Lock/unlock fail-closed for any `protocol != 0x0D`, never silently accepted | ROADMAP's literal mechanism **disproven against live source** (F-D). Corrected admission point identified with its refusal path, message id, and a proof that its blast radius cannot reach `read`/`verify` (F-D, F-E). |
| LOCK-05 | `FLASH_ENABLE_WRITE_PROTECTION` preserved, not deduped, duplication recorded as datasheet-correct | **The two-way identity assertion already exists in-tree** (F-K). Only the third leg + distinct-objects + no-payload assertions are new. **⚠ ROADMAP criterion 5's "header comment" conflicts with D-09's byte-frozen `flash_utils.h`** — resolution recommended (F-K). |
| LOCK-06 | Measured `pio run -e leonardo` flash delta within live headroom | **Measured this session at HEAD `1880054`: Leonardo 25680/28672 → 2992 B free** (F-H). `3348 B` superseded, confirmed. All three envs measured. `-D DEV_TOOLS` costs 1292 B (F-G). |
| DEVTEST-01 (firmware half, moved in by D-08) | Firmware fail-closes on `CMD_ERASE` for `0x0D` rather than reporting a phantom OK | Phantom mechanism verified line-exact (F-E). **The complete cmd × protocol NULL-`main` matrix is precomputed** — the D-08 sweep is now an enumeration, not an exploration (F-E). |
</phase_requirements>

## Summary

This phase's own CONTEXT.md is unusually complete — it verified most of the tree during discuss-phase. Research therefore concentrated on (a) *re-verifying* its load-bearing claims against live source rather than trusting them, (b) *measuring* the two numbers it deferred, and (c) hunting the class of surprise that has bitten this milestone four times: a firmware edit that keeps the firmware suite green while breaking a host gate that scans firmware source text.

**Every material CONTEXT.md claim verified.** The `#ifdef`-conditional admission guard, the pre-set generic mains that make LOCK-04's literal mechanism harmful, the bare `return false` phantom-success path, the free command slots, the byte-identical `AA-55-A0` triple, the existing `MSG_ERR_NOT_SUPPORTED`, and the 2992 B live headroom all check out exactly as recorded. Three things CONTEXT.md does not record, and which materially change the plan: **`CMD_DEV_ADDRESS`/`CMD_DEV_REGISTER` are themselves `#ifdef DEV_TOOLS`-guarded** so the truth-table suite cannot name them in the release env; **`[env:native]` does not compile the op layer or the command dispatcher at all**, which forces where `is_memory_cmd()` may be declared and creates a real choice about how D-06's guard gets proven; and **D-14's shared bracket helper will trip `check_no_log_in_sdp_window.py`'s fail-closed rename tripwire** if it moves the emit call out of `eeprom28c_write_init`.

Two experiments were run rather than reasoned about. A temporary `[env:native_nodevtools]` (since removed; `platformio.ini` restored byte-clean) **compiles and passes 112/112 across all 16 suites with zero test-code changes** — folded todo item 4 is answered empirically, today, and D-04's second env carries no hidden porting cost. A temporary release-config Leonardo build reports **24388/28672**, so `-D DEV_TOOLS` costs 1292 B and the *tighter* of the two configurations (the DEV_TOOLS one, 2992 B free) is the binding constraint for LOCK-06.

**Primary recommendation:** land the plan set in the order `catalog ritual → is_memory_cmd() (header-inline, LOCK-03) → new commands + EEPROM_SDP_ENABLE + shared bracket (LOCK-01/02/05) → generic NULL-main guard + cross-family sweep (LOCK-04/DEVTEST-01) → measurement`, and treat the host source-scanning-gate repair as **named task work inside the same plan as the firmware edit that breaks it** — the FIFTH CORRECTION item 5 discipline that produced zero host CI surprises in Phase 118.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Command admission (`is_memory_cmd()`) | Firmware — command dispatcher (`firestarter.cpp`, `firestarter.h`) | — | The guard sits between JSON parse and `configure_memory`; it is a dispatcher concern and must stay protocol-agnostic (v1.20's protocol-only rebuild). |
| Capability refusal for an unimplemented (cmd, protocol) pair | Firmware — operation layer (`operation_utils.cpp`) | Firmware — protocol handler (`configure_*`) sets/omits the main | D-06: the op layer is the single site where "no handler was configured" is observable for every protocol, present and future. Handlers own *whether* a main exists; the op layer owns *what happens when it doesn't*. |
| SDP-enable / SDP-disable sequence emission | Firmware — `0x0D` protocol handler (`proms/eeprom_28c.cpp`) | — | Protocol-specific bus semantics. FIX-01 already established the `0x0D`-local remap-aware emitter; `flash_utils.h` stays frozen. |
| Timing bracket + t_BLC budget check | Firmware — `0x0D` protocol handler (shared helper) | — | The budget is a datasheet property of the AT28C family, not of the dispatcher. |
| Message catalog ids | Meta-repo — `tools/catalog/messages.toml` (canonical) | Firmware `include/messages.h` + host `firestarter/messages.py` (both **generated**) | Single source of truth with a CI drift gate; hand-editing either generated artifact is forbidden. |
| DEV_TOOLS-invariance proof | Firmware — PlatformIO native env (semantic) | Host — `firestarter_app` AST/source-scan gate (textual) | D-04 wants both: a semantic proof the predicate behaves identically, and a textual proof it contains no `#ifdef`. Different failure modes need different oracles. |
| Host CLI surface (`dev sdp`, `--skip-sdp-unlock`, `constants.py`) | **Out of scope — Phase 120** | — | Firmware-before-host is a non-negotiable milestone ordering invariant. |
| Bench measurement + provenance | Meta-repo — `119-MEASUREMENT.md` | Operator hardware (3 boards) | D-20; a rounded figure in prose is not a substitute. |

## Standard Stack

No new libraries. This phase adds firmware C++ to an existing PlatformIO project and Python to an existing pytest suite. The relevant "stack" is the in-tree toolchain, verified present and working in this session.

### Core

| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| PlatformIO Core | 6.x (`/usr/local/bin/pio`) | Firmware build + native Unity test runner | In-tree since v1.0; `platformio.ini` is the project's build source of truth `[VERIFIED: pio run/pio test executed this session]` |
| Atmel AVR platform | 5.2.0 | `uno` / `uno328pb` / `leonardo` targets | Reported by `pio run -e leonardo` this session `[VERIFIED]` |
| framework-arduino-avr | 5.3.0 | Arduino core | Reported by `pio run` this session `[VERIFIED]` |
| toolchain-atmelavr | 1.70300.191015 (GCC 7.3.0) | AVR compiler | Reported by `pio run` this session `[VERIFIED]` |
| Unity | via `test_framework = unity` | Native host test framework | `platformio.ini:70` `[VERIFIED]` |
| ArduinoFake | `fabiobatsilva/ArduinoFake@^0.4.0` | Mocks `Serial`/`millis`/`micros`/`delay` in native suites | `platformio.ini` `lib_deps` `[VERIFIED]` |
| pytest | in-tree host suite | `firestarter_app` gates | 21/21 relevant gates green this session `[VERIFIED]` |
| Python 3.11 | CI codegen target | `tools/catalog/codegen.py` | `.github/workflows/build.yml` pins `python-version: '3.11'` `[VERIFIED]` |

**Installation:** none. `pip install -e '.[test]'` in `firestarter_app` if the host env needs rebuilding (`.planning` memory `reference_firestarter_app_python_test_env.md`).

⚠ **Devcontainer Python is 3.12; host CI targets py3.9/3.11.** Validate ruff/format against the CI targets, never the devcontainer's 3.12 (`.planning` memory `reference_devcontainer_py312_masks_ci_py39.md`; GATE-03 requires it explicitly).

## Package Legitimacy Audit

**N/A — this phase installs zero external packages.** All work lands in existing firmware C++, an existing PlatformIO env definition, an existing TOML catalog, and existing Python test/tool modules. No `npm`/`pip`/`cargo` install step appears anywhere in scope. The Package Legitimacy Gate was therefore not run; no `[SLOP]`/`[SUS]` verdicts exist to report.

## Architecture Patterns

### System Architecture Diagram — a standalone `CMD_SDP_LOCK`, end to end

```
  HOST (3.0.0b11 today; Phase 120 adds `dev sdp`)
    │  COBS frame: {"cmd":10, "algorithm":13, "memory-size":…, "bus_config":…}
    ▼
┌───────────────────────── firestarter.cpp ─────────────────────────┐
│ loop() @ CMD_IDLE ──► rurp_communication_read_data (COBS+CRC8)     │
│         └─► init_programmer_framed ──► parse_json                  │
│                 │                                                  │
│                 ├─ json_get_cmd  ────► handle->cmd = 10            │
│                 │                                                  │
│                 ├─ ADMISSION GUARD  ◄── LOCK-03 CHANGES THIS       │
│                 │   today:  if (cmd < CMD_READ_VPP)   json_parse   │
│                 │           #ifdef DEV_TOOLS                       │
│                 │             if (cmd < CMD_DEV_ADDRESS) ─┐        │
│                 │           #endif                        │        │
│                 │   after:  if (is_memory_cmd(cmd)) ──────┤        │
│                 │                                         ▼        │
│                 └───────────────────────► op_execute_function(     │
│                                              configure_memory)     │
└────────────────────────────────────────────┬───────────────────────┘
                                             ▼
┌──────────────────── proms/memory.cpp: configure_memory ────────────┐
│  init/main/end := NULL                                             │
│  switch(cmd) { READ→memory_read_execute                            │
│                WRITE→memory_write_execute   ◄── PRE-SET generic    │
│                VERIFY→memory_verify_execute }    mains (:48-58)    │
│  set_data/get_data/set_address/ctrl-reg pointers                   │
│  mem_util_set_address(handle, 0)      ◄── writes registers!        │
│  protocol chain (:70-113) ──► 0x0D ──► configure_eeprom28c         │
│                           ──► anything unrecognised ──►            │
│                               configure_not_implemented (0xBB,     │
│                               response_code=ERROR ⇒ MSG_ERR_SETUP) │
└────────────────────────────────────────────┬───────────────────────┘
                                             ▼
┌────────────── proms/eeprom_28c.cpp: configure_eeprom28c ───────────┐
│  pulse_delay = 0                                                   │
│  switch(cmd) { WRITE→write_init/write_execute                      │
│                BLANK_CHECK→mem_util_blank_check                    │
│                SDP_UNLOCK→ ??? ]  ◄── NEW (LOCK-02)                │
│                SDP_LOCK  → ??? ]      init/end left NULL           │
│  ⚠ a blanket `default:` here fires for READ and VERIFY too         │
│    (they arrive with a generic main already set) ⇒ D-05            │
└────────────────────────────────────────────┬───────────────────────┘
                                             ▼
┌──────── eprom_operations.cpp: NEW eprom_sdp_lock/unlock entry ─────┐
│  (mirror eprom_erase's precondition-refusal shape, :34-40)         │
│  return !op_execute_simple_operation(handle);                      │
└────────────────────────────────────────────┬───────────────────────┘
                                             ▼
┌──────── operation_utils.cpp: op_execute_stateful_operation ────────┐
│  :63  if (handle->firestarter_operation_main) { … }                │
│  :83  return false;   ◄── PHANTOM SUCCESS. Caller reports          │
│                            "finished" with response_code == OK     │
│                            and NO error frame at all.              │
│         ◄══ D-06/D-07 PUT THE REFUSAL HERE (MSG_ERR_NOT_SUPPORTED) │
│                                                                    │
│  state machine, 4 host ACKs:                                       │
│    ACK₁ → INIT_START, [init==NULL ⇒ runs EMPTY], INIT_DONE         │
│    ACK₂ → MAIN_START, main(handle) ⇒ 3 latch writes + t_WC,        │
│           MAIN_DONE(INFO) + MSG_MAIN_DONE                          │
│    ACK₃ → END_START,  [end==NULL ⇒ runs EMPTY],  END_DONE          │
│    ACK₄ → command finished ⇒ command_done() (chip disable,         │
│           registers zeroed, cmd := CMD_IDLE)                       │
│  NO `#` data frame. NO `DONE` string round-trip (that lives only   │
│  in eprom_operations.cpp::_process_incoming_data, the write path). │
└────────────────────────────────────────────────────────────────────┘
```

### Recommended file placement

```
firestarter/
├── include/
│   ├── firestarter.h            # CMD_SDP_UNLOCK 9, CMD_SDP_LOCK 10;
│   │                            # is_memory_cmd() as `static inline` (see F-F)
│   ├── operation_utils.h        # (alt. home for the predicate; also has the
│   │                            #  static-inline precedent at :41-49)
│   └── messages.h               # GENERATED — never hand-edit
├── src/
│   ├── firestarter.cpp          # guard site :76-95; two new `case` arms :202-250
│   ├── operation_utils.cpp      # :63/:83 — the ONE generic NULL-main refusal
│   ├── eprom_operations.cpp     # new eprom_sdp_lock / eprom_sdp_unlock entry
│   └── proms/eeprom_28c.cpp     # EEPROM_SDP_ENABLE[3] + extern; the lock/unlock
│                                # ops; shared bracket helper; new switch arms;
│                                # D-16 page-load worst-case tracker
├── platformio.ini               # [env:native_nodevtools] (+ its own test_filter
│                                # allowlist AND its own -I list — see F-N)
├── .github/workflows/build.yml  # + `pio test -e native_nodevtools` step
└── test/native/avr/
    ├── _shared/sdp_expected.h   # + SDP_FIXED_LOCK_* goldens (blob SHA CHANGES)
    ├── test_sdp_harness/        # + the three-way table-identity guard
    ├── test_eeprom28c_sdp/      # + lock stream / no-payload / budget cases;
    │                            # ⚠ micros() mock needs upgrading (F-O)
    └── test_cmd_admission/      # NEW: the is_memory_cmd() truth table
                                 # (needs a platformio.ini test_filter + -I line)

firestarter_app/                 # ONLY generated catalog code + gate work
├── firestarter/messages.py      # GENERATED — never hand-normalise
├── tools/check_is_memory_cmd_no_ifdef.py     # NEW gate (D-04)
└── tests/
    ├── test_check_is_memory_cmd_no_ifdef.py  # NEW paired anti-hollow pytest
    ├── fixtures/planted_ifdef_in_predicate.h # NEW planted-violation fixture
    ├── test_sdp_table_parity.py              # verify (safe today, see F-L)
    └── test_check_no_log_in_sdp_window.py    # ⚠ WILL need repair (F-M)

.planning/phases/119-…/
├── 119-MEASUREMENT.md           # D-20; mirror 118-MEASUREMENT.md §1 and §6
└── 119-NONREGRESSION.md         # mirror 118-NONREGRESSION.md §4
```

### Pattern 1: the `0x0D`-local command table with load-bearing external linkage

**What:** a `const byte_flip_t` array at namespace scope in `eeprom_28c.cpp`, preceded by an `extern` declaration so a native test TU can pin the **production** array rather than a transcription.
**When to use:** for `EEPROM_SDP_ENABLE[3]`. Copy `EEPROM_SDP_DISABLE`'s shape exactly.
**Why the `extern` is load-bearing:** in C++ a namespace-scope `const` array has internal linkage unless a prior declaration with external linkage is visible.

```cpp
// Source: firestarter/src/proms/eeprom_28c.cpp:103-124 (verified live)
extern const byte_flip_t EEPROM_SDP_DISABLE[6];
const byte_flip_t EEPROM_SDP_DISABLE[6] = {
    {0x5555, 0xAA},
    {0x2AAA, 0x55},
    {0x5555, 0x80},
    {0x5555, 0xAA},
    {0x2AAA, 0x55},
    {0x5555, 0x20},
};
```

The new table is therefore, per LOCK-01 and `.planning/research/SUMMARY.md` CONFLICT 1:

```cpp
extern const byte_flip_t EEPROM_SDP_ENABLE[3];
const byte_flip_t EEPROM_SDP_ENABLE[3] = {
    {0x5555, 0xAA},
    {0x2AAA, 0x55},
    {0x5555, 0xA0},   // ⚠ byte-identical to FLASH_ENABLE_WRITE — the
                      // PROTECTED-WRITE PREFIX. Only the ABSENCE of a
                      // following data write makes this a lock (D-10).
};
```

### Pattern 2: the shared emitter, and its hard constraint

**What:** every `0x0D` command sequence goes through one function.
**Hard constraint, stated in its own source comment:** nothing bus-visible may be added inside its body beyond the `rurp_set_data_output()` call and the `set_data` loop, or the `SDP_FIXED_*` full-stream goldens break. **No `LOG_` call belongs there** — enforced by `check_no_log_in_sdp_window.py`.

```cpp
// Source: firestarter/src/proms/eeprom_28c.cpp:214-230 (verified live)
static void eeprom28c_emit_command_sequence(firestarter_handle_t* handle,
                                            const byte_flip_t* sequence,
                                            size_t length) {
    rurp_set_data_output();          // recorder-invisible: no-op in host stubs
    for (size_t i = 0; i < length; i++) {
        handle->firestarter_set_data(handle, sequence[i].address, sequence[i].byte);
    }
}
```

### Pattern 3: the `micros()` bracket + length-parameterised t_BLC budget (D-14's factoring target)

```cpp
// Source: firestarter/src/proms/eeprom_28c.cpp:290, 348-375 (verified live)
size_t sdp_seq_len = sizeof(EEPROM_SDP_DISABLE) / sizeof(EEPROM_SDP_DISABLE[0]);
LOG_ID(MSG_INFO_SDP_UNLOCK);                       // bare LOG_ID on an INFO id
uint32_t sdp_emit_start_us = micros();
eeprom28c_emit_command_sequence(handle, EEPROM_SDP_DISABLE, sdp_seq_len);
uint32_t sdp_emit_us = (uint32_t)(micros() - sdp_emit_start_us);
LOG_ID_U32(MSG_INFO_SDP_UNLOCK_DONE_US, sdp_emit_us);
uint32_t sdp_tblc_budget_us = (uint32_t)sdp_seq_len * AT28C_TBLC_MAX_US;
if (sdp_emit_us > sdp_tblc_budget_us) {
    LOG_WARN_ID_U32(MSG_WARN_SDP_TBLC_EXCEEDED, sdp_emit_us);   // no response_code write
}
```

At `sdp_seq_len == 3` the lock's budget is **300 µs**; at F-118-01's measured ~95 µs/byte it lands near **~286 µs** — the same ~4.7 % margin. The check is as load-bearing on the lock path as on the unlock path.

⚠ **The report lines are UNCONDITIONAL `LOG_ID`/`LOG_ID_U32` on INFO-band ids, not the `FLAG_VERBOSE`-gated `LOG_INFO_ID*` family.** These are the tree's only such call sites (118 D-01). The lock's pair must follow the same spelling or a default `dev sdp enable` goes silent.

### Pattern 4: the precondition-refusal entry point

```cpp
// Source: firestarter/src/eprom_operations.cpp:34-38 (verified live)
bool eprom_erase(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_ERASE_PROM);
    if (!is_flag_set(FLAG_CAN_ERASE)) {
        LOG_ERROR_ID(MSG_ERR_NOT_SUPPORTED);
        return true;                       // true == finished
    }
    return !op_execute_simple_operation(handle);
}
```

This is the model for `eprom_sdp_lock` / `eprom_sdp_unlock`, and it is already the existing `MSG_ERR_NOT_SUPPORTED` caller.

### Anti-Patterns to Avoid

- **A blanket `default:` arm in `configure_eeprom28c`'s switch** — refuses `read` and `verify` on all 84 `0x0D` chips (F-D). This is LOCK-04 as literally written. Never implement it.
- **An `#ifdef DEV_TOOLS` inside `is_memory_cmd()`** — recreates the divergence LOCK-03 exists to remove and makes the invariance test pass vacuously (D-02).
- **Asserting on a call *count* instead of the ordered stream's content** — production register-write elision is invisible to a counting test. `sdp_expected.h`'s comparator "never counts anything; every comparison is positional."
- **Hand-editing `firestarter/include/messages.h` or `firestarter_app/firestarter/messages.py`** — both are codegen output with CI drift gates. Edit `tools/catalog/messages.toml` (meta, canonical) and run `sync_to_subrepos.sh`.
- **Hand-normalising the generated `messages.py`** — raw codegen output is already ruff-clean and format-stable (`.planning` memory `reference_codegen_ruff_clean_emitter.md`).
- **Adding `CMD_SDP_*` to `firestarter_app/firestarter/constants.py`** — Phase 120 HOST-03. Firmware-before-host.
- **A `git diff -- src/flash_utils.h` check to prove the header is untouched** — that path does not exist (the real path is `include/flash_utils.h`); the check passes **vacuously**. FOURTH CORRECTION item 5.
- **Reporting the DQ6 toggle poll's outcome as lock evidence** — a settled toggle bit proves a write cycle finished, not that protection latched. This is FIX-02's deleted mistake in a new costume (D-12).
- **A dummy data byte after the 3 loads** — it both modifies user data and drags the `pulse_delay`-aware `memory_set_data` path into the t_BLC window (research SUMMARY Pitfall 2).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Refusing an unconfigured (cmd, protocol) pair | A per-handler `default:` arm × 6 handlers | ONE NULL-`main` check at `operation_utils.cpp:63/83` | Six sites, most flash against 2992 B, and each arm must be written not to swallow the pre-set generic mains (D-06) |
| Emitting a command sequence on `0x0D` | A second emitter, or `flash_execute_command` | `eeprom28c_emit_command_sequence` | Already remap-aware (FIX-01); `flash_util_byte_flipping` bypasses `bus_config` and inhibits `/WE` on 66 of 84 chips |
| Timing a sequence + checking its budget | A copy-paste of 118's bracket | One shared helper both sequences call (D-14) | The budget is already length-parameterised, so the factoring is nearly free in flash |
| Comparing a recorded bus stream to an expectation | A sub-sequence scan or a length/count check | `sdp_assert_stream_equals` / `sdp_first_divergence` | RESEARCH §F5 proved shipped and fixed streams have identical length and, on DIP32, identical address bytes — only ordered full-stream equality discriminates them |
| Snapshotting a stream to compare two tables | Re-driving and hoping the recorder persists | `sdp_snapshot(snap, N)` before the second `drive()` | `drive()` calls `clear_strobes()`; without a snapshot the first stream is gone |
| A new ERROR message id for the refusal | A new catalog entry | `MSG_ERR_NOT_SUPPORTED` (`0xA5`, `messages.toml:417-423`) | Already exists and is already `eprom_erase`'s refusal id |
| Proving a gate is real | Prose, or a comment | A committed planted-violation fixture + paired pytest | Standing project rule; the v1.12 hollow-GATE-03 debt is what it pays down |
| Distributing catalog changes | Copying `messages.h`/`messages.py` by hand | `tools/catalog/sync_to_subrepos.sh` | Copies TOML+codegen to both sub-repos, regenerates both artifacts, and verifies byte-identity |

**Key insight:** every one of these has an in-tree implementation that a prior phase in *this milestone* built and proved. The cheapest correct plan is almost entirely composition.

## Runtime State Inventory

This phase is a firmware feature addition, not a rename/refactor/migration. The inventory is included anyway because D-08's generic guard changes observable behaviour across every protocol family — the closest thing to a migration blast radius here.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | **None.** Zero `chip_database.json` change, zero `support_status` change, zero `PROTOCOL-LEDGER` entry (CONTEXT `<domain>` "Explicitly NOT in scope"; CLOSE-01). Verified: no DB file is in this phase's integration-point list. | None |
| Live service config | **None.** No n8n / Datadog / Tailscale / Cloudflare surface in this project. | None |
| OS-registered state | **None.** No scheduled tasks or daemons. | None |
| Secrets/env vars | **None new.** Existing env seams are test-only overrides (`FIRESTARTER_SDP_SRC`, `FIRESTARTER_DEVTEST_SRC`, `FIRESTARTER_DB_FILE`) — a new gate should follow that fail-closed idiom (`FIRESTARTER_*_SRC` pointing at a missing file must be an error, never a silent pass). | Add one fail-closed override seam for the new D-04 gate |
| Build artifacts / flashed firmware | **Three attached boards carry pre-119 firmware.** `/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0` are all present (verified this session). D-18's bench work reflashes them. `.pio/build/*` is stale after any source change. | Re-flash each board before its measurement; re-verify `controller:` identity per port **first** (port numbers shuffle across replug — `.planning` memory `feedback_verify_port_identity_each_task.md`) |
| Golden-trace blobs | `test/native/avr/_shared/sdp_expected.h` **must change** (D-10 adds `SDP_FIXED_LOCK_*`). Its whole-file blob SHA therefore cannot be used as this phase's identity proof, unlike 117/118. | Shift to **per-array byte-identity of the pre-existing arrays** and say so explicitly in `119-NONREGRESSION.md`. The other two `_shared/` files (`host_stubs_common.inc`, `sdp_bus_config.h`) should stay blob-SHA-identical — assert that. |

## Verified Findings

Each finding is labelled with the research question it answers. All line numbers read from live source at firmware `1880054` / host `d3f9128`, both on `v1.22-at28c-software-data-protection-lifecycle` (branch precondition **verified**).

### F-A — The datasheet-correct lock body (Q4)

`[CITED: .planning/research/SUMMARY.md CONFLICT 1]` — **3 loads + `t_WC`, no data payload.** Confidence HIGH, and it is an adjudicated 3-document / 3-stream agreement rather than one citation:

- Atmel **doc0270** rev `0270L–PEEPR–2/09` §19 note 2 p.10: *"Write Protect state will be activated at end of write even if no other data is loaded."* This is the citation of record (unambiguous note→terminal-box mapping).
- Microchip **DS20006432B** (AT28C64B) §6.18 note 2 p.16: same sentence.
- The dissenting "≥1 data byte" reading is an uncited inference; the in-tree `AT28C256.pdf` has a copy-paste error in its notes 2/3 that is the likely origin.

Byte/address sequence: `{0x5555, 0xAA}`, `{0x2AAA, 0x55}`, `{0x5555, 0xA0}`, then `delay(AT28C_TWC_MAX_MS)` and stop.

**Why the magic addresses need no per-part table** `[CITED: research SUMMARY]`: `0x5555 & 0x1FFF == 0x1555` and `0x2AAA & 0x1FFF == 0x0AAA` — *exactly* AT28C64B's documented `1555h`/`0AAAh`. `0x5555`/`0x2AAA` **are** the alternating bit patterns, so truncation to any width lands on the family's documented pair by construction. Verdict: do **not** add per-part SDP address tables.

**How the three sequences differ** (all verified against `include/flash_utils.h:24-59` and `eeprom_28c.cpp:123-130`):

| Sequence | Bytes at `0x5555 / 0x2AAA / 0x5555 [/ 0x5555 / 0x2AAA / 0x5555]` | Length | Terminal byte |
|---|---|---|---|
| SDP-enable (lock) — **NEW** | `AA · 55 · A0` | 3 | `0xA0` |
| Protected-write prefix (`FLASH_ENABLE_WRITE`) | `AA · 55 · A0` | 3 | `0xA0` — **byte-identical** |
| `FLASH_ENABLE_WRITE_PROTECTION` | `AA · 55 · A0` | 3 | `0xA0` — **byte-identical** |
| SDP-disable (unlock, `EEPROM_SDP_DISABLE`) | `AA · 55 · 80 · AA · 55 · 20` | 6 | `0x20` |
| `FLASH_DISABLE_WRITE_PROTECTION` | `AA · 55 · 80 · AA · 55 · 20` | 6 | `0x20` — byte-identical to unlock |
| Chip erase (`FLASH_ERASE`) | `AA · 55 · 80 · AA · 55 · 10` | 6 | `0x10` — **one nibble from unlock** |

So the lock's first 3 writes are the unlock's first 3 writes with only the third payload changed (`0x80 → 0xA0`), and the lock is distinguishable from the protected-write prefix **only by what does not follow it**. That is why D-10 pairs a table-identity guard with a stream-length assertion: an absence cannot be asserted by comparing tables.

### F-B — The admission guard today, and the accepted set under both configurations (Q1)

`[VERIFIED: firestarter/src/firestarter.cpp:73-91, read live]`

```cpp
    if (handle->cmd < CMD_READ_VPP) {                 // :76  outer, unconditional (11)
        json_parse(handle->data_buffer, tokens, token_count, handle);
#ifdef DEV_TOOLS
        if (handle->cmd < CMD_DEV_ADDRESS) {          // :79  THE guard LOCK-03 replaces (7)
#endif
            LOG_DEBUG_ID_SUB_U8(DBG_FLAG_FORCE, …);   // 5 flag debug lines
            if (!op_execute_function(configure_memory, handle)) {
                LOG_ERROR_ID(MSG_ERR_SETUP);
                return false;
            }
#ifdef DEV_TOOLS
        } else {
            LOG_DEBUG_ID_SUB_U8(DBG_FLAG_OUTPUT_EN, …);
            LOG_DEBUG_ID_SUB_U8(DBG_FLAG_CHIP_EN, …);
        }
#endif
    } else if (handle->cmd == CMD_CONFIG) { … }
```

Full command enumeration `[VERIFIED: include/firestarter.h:33-49]`:

| Value | Symbol | `-D DEV_TOOLS` build: reaches `configure_memory`? | Release build (no `-D DEV_TOOLS`): reaches `configure_memory`? | In `is_memory_cmd()`? |
|---|---|---|---|---|
| 0 | `CMD_IDLE` | **YES** | **YES** | **no** ⚠ see F-B2 |
| 1 | `CMD_READ` | yes | yes | yes |
| 2 | `CMD_WRITE` | yes | yes | yes |
| 3 | `CMD_ERASE` | yes | yes | yes |
| 4 | `CMD_BLANK_CHECK` | yes | yes | yes |
| 5 | `CMD_CHECK_CHIP_ID` | yes | yes | yes |
| 6 | `CMD_VERIFY` | yes | yes | yes |
| 7 | `CMD_DEV_ADDRESS` † | no (dev branch) | **YES** ⚠ | **no** (D-01) |
| 8 | `CMD_DEV_REGISTER` † | no (dev branch) | **YES** ⚠ | **no** (D-01) |
| **9** | **`CMD_SDP_UNLOCK`** (new) | **no** ⚠ (dev branch — D-03's whole point) | yes | **yes** |
| **10** | **`CMD_SDP_LOCK`** (new) | **no** ⚠ (dev branch) | yes | **yes** |
| 11 | `CMD_READ_VPP` | no (`>= CMD_READ_VPP`) | no | no |
| 12 | `CMD_READ_VPE` | no | no | no |
| 13 | `CMD_FW_VERSION` | no | no | no |
| 14 | `CMD_CONFIG` | no (`else if` branch) | no | no |
| 15 | `CMD_HW_VERSION` | no | no | no |
| other | — | no | no | no |

† `#ifdef DEV_TOOLS`-conditional **definitions** — see F-C.

**Today's divergent set is `{0, 7, 8, 9, 10}`** — five values where the two build configurations disagree, of which `{9, 10}` is fatal to LOCK-02 (a DEV_TOOLS build would route the new commands into the dev branch and never configure a bus), and `{7, 8}` is the pre-existing defect D-01 fixes. `{0}` is F-B2.

**A test can prove set-equality** by asserting `is_memory_cmd(c)` over `c ∈ [0, 255]` (every value, not a sample) in both envs. Because the predicate names only unconditionally-defined symbols, the *same source text* compiles in both — which is precisely the semantic proof D-04 wants.

### F-B2 — ⚠ NEW: a third behaviour delta beyond cmd 7/8 — `CMD_IDLE`

`[VERIFIED: firestarter.cpp:73, :226]` `cmd == 0` satisfies `cmd < CMD_READ_VPP` in **both** configurations, so a host frame `{"cmd":0}` today runs `json_parse` **and** `configure_memory`. With no `protocol` field, `handle->protocol == 0` and the chain terminates at `configure_not_implemented`, which logs `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` (0xBB) and sets `response_code = RESPONSE_CODE_ERROR` → `op_execute_function` returns false → `LOG_ERROR_ID(MSG_ERR_SETUP)`. **Two error frames.**

After `is_memory_cmd()`, cmd 0 skips `configure_memory` entirely and falls to `loop()`'s `case CMD_IDLE: break;` (`:226`) → `finished == false` → no `command_done()`, no frame at all. The handle's `cmd` is already `CMD_IDLE`, so the next `loop()` iteration re-enters the idle branch and waits — inert, but **silent where it used to error**.

**Planner action:** D-01 names cmd 7/8 as the taken behaviour change. `CMD_IDLE` is a *third* one and is a small honesty regression rather than a tightening. Either include `CMD_IDLE` in the loop-switch handling explicitly (e.g. keep the `MSG_ERR_UNKNOWN_CMD` shape for an explicitly-sent cmd 0) or accept it and record it in the SUMMARY alongside 7/8. Do not let it be discovered by a verifier.

### F-C — ⚠ NEW and load-bearing: the `CMD_DEV_*` symbols are themselves `#ifdef DEV_TOOLS`

`[VERIFIED: include/firestarter.h:42-45]`

```c
#ifdef DEV_TOOLS
#define CMD_DEV_ADDRESS 7
#define CMD_DEV_REGISTER 8
#endif
```

Complete reference set `[VERIFIED: grep across all .h/.cpp/.c/.inc]` — five sites: the two definitions, `firestarter.cpp:79` (the guard), and `firestarter.cpp:231,234` (the two loop-switch cases, themselves inside `#ifdef DEV_TOOLS`). **Zero references anywhere in `test/`.**

**Three consequences CONTEXT.md does not record:**

1. **The `#ifdef` around the guard at `:79` is MANDATORY today, not gratuitous.** Removing it without also removing the `CMD_DEV_ADDRESS` reference would fail to compile in a release build. This strengthens D-01's case: the divergence is not laziness, it is structurally forced by the conditional `#define` — and `is_memory_cmd()` removes it by *not naming those symbols at all*.
2. **D-04's truth-table suite must not name `CMD_DEV_ADDRESS`/`CMD_DEV_REGISTER`.** The same source text runs in both envs; in `native_nodevtools` those macros do not exist. Use **numeric literals `7` and `8`** with a comment citing `firestarter.h:42-45`, exactly as the host's `test_revision_constants_parity.py:110-112` already does for the same reason (*"assert Python values as standalone literals only"*).
3. **`is_memory_cmd()` as specified by D-01 is implementable with no `#ifdef`** — all eight named symbols are unconditional. D-01/D-02 are sound.

### F-D — LOCK-04's mechanism is disproven; the corrected admission point (Q2)

**Disproof, verified live.** `configure_memory` pre-sets the generic mains *before* the protocol chain runs:

```cpp
// Source: firestarter/src/proms/memory.cpp:42-58 (verified live)
void configure_memory(firestarter_handle_t* handle) {
    handle->firestarter_operation_init = NULL;
    handle->firestarter_operation_main = NULL;
    handle->firestarter_operation_end  = NULL;
    switch (handle->cmd) {
        case CMD_READ:   handle->firestarter_operation_main = memory_read_execute;   break;
        case CMD_WRITE:  handle->firestarter_operation_main = memory_write_execute;  break;
        case CMD_VERIFY: handle->firestarter_operation_main = memory_verify_execute; break;
    }
    …                                    // pointers, mem_util_set_address(handle, 0)
    if (handle->protocol == PROTO_EEPROM_PARALLEL) { configure_eeprom28c(handle); return; }
    …
}
```

```cpp
// Source: firestarter/src/proms/eeprom_28c.cpp:126-139 (verified live)
void configure_eeprom28c(firestarter_handle_t* handle) {
    handle->pulse_delay = 0;
    switch (handle->cmd) {
        case CMD_WRITE:
            handle->firestarter_operation_init = eeprom28c_write_init;
            handle->firestarter_operation_main = eeprom28c_write_execute;
            break;
        case CMD_BLANK_CHECK:
            handle->firestarter_operation_main = mem_util_blank_check;
            break;
    }
}
```

`CMD_READ` and `CMD_VERIFY` **reach this switch** and fall through it, keeping the generic main. A `default: → MSG_ERR_NOT_SUPPORTED` arm fires for them, on **all 84** `0x0D` chips. And separately: `configure_eeprom28c` runs *only for* `0x0D`, so a `default:` arm there cannot refuse another protocol at all. **CONTEXT.md D-05 is confirmed exactly.**

**The corrected admission point:**

```cpp
// Source: firestarter/src/operation_utils.cpp:62-90 (verified live)
bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t*),
                                   firestarter_handle_t* handle) {
    if (handle->firestarter_operation_main) {      // :63  ◄── the guard site
        …
    }
    return false;                                  // :83  ◄── phantom success
}
```

- **Site:** `operation_utils.cpp`, the `main == NULL` fall-through at `:83`.
- **Refusal path:** `LOG_ERROR_ID(MSG_ERR_NOT_SUPPORTED);` plus `handle->response_code = RESPONSE_CODE_ERROR;` before `return false`.
- **Message id:** `MSG_ERR_NOT_SUPPORTED = 0xA5` `[VERIFIED: tools/catalog/messages.toml:417-423]`. Format `"Not supported"`, `params = []`, `wire_format = "id_frame"`. **No new catalog id required for D-06.** Consider `LOG_ERROR_ID_U8(…, handle->cmd)` for diagnosability — but that needs a `u8` param, which the existing `0xA5` entry does not have, so it would be a *new* id. Recommend reusing `0xA5` as-is (D-06 explicitly costs no catalog decision).
- **Why this cannot break `read`/`verify`:** `configure_memory`'s pre-set means `CMD_READ`/`CMD_WRITE`/`CMD_VERIFY` are **never** NULL for any protocol that reaches a `configure_*` handler. That is a source-level invariant, not a hope, and it is worth pinning as a native test case.

### F-E — The phantom-success mechanism, and the complete cmd × protocol matrix (Q2, D-08's sweep)

**Mechanism, verified line-exact.** With `main == NULL`, `op_execute_stateful_operation` returns `false` at `:83`. Every caller inverts it (`return !op_execute_stateful_operation(...)`), so the command reports **finished**. `loop()` sets `handle.response_code = RESPONSE_CODE_OK` at `:201` *before* the switch and nothing on this path writes it. `command_done()` runs. **Result: the operation reports OK, emits no error, and emits no `MSG_MAIN_DONE` either — it emits nothing at all.** This is DEVTEST-01's phantom erase, and CONTEXT.md D-07 is confirmed.

**Scoping proof — the guard cannot reach the non-memory commands.** `[VERIFIED: grep for op_execute*/firestarter_operation_main across src/hardware_operations.cpp and src/dev_tools.cpp → zero hits]`. `hw_read_voltage`, `fw_get_version`, `hw_get_version`, `hw_get_config`, `dt_set_registers`, `dt_set_address` never touch the op layer. `op_execute_stateful_operation` is reached **only** from the six `eprom_*` entry points in `eprom_operations.cpp:19-56` (three directly, three via `op_execute_simple_operation`). So `vpp`, `vpe`, `fw`, `config`, `hw`, `dev reg`, `dev address` are structurally out of the blast radius.

**The complete matrix.** `[VERIFIED: all six configure_* handler bodies read live]` — `G` = generic pre-set main, `H` = handler-specific main, **`∅` = NULL main (silent OK today)**.

| Protocol(s) | Handler | READ (1) | WRITE (2) | ERASE (3) | BLANK_CHECK (4) | CHIP_ID (5) | VERIFY (6) | SDP_UNLOCK (9) | SDP_LOCK (10) |
|---|---|---|---|---|---|---|---|---|---|
| `0x07 0x08 0x0B` | `configure_eprom` | G | H | H | H | H | G | **∅** | **∅** |
| **`0x0D`** | `configure_eeprom28c` | G | H | **∅** ⚠ | H | **∅** ⚠ | G | **H (new)** | **H (new)** |
| `0x10` | `configure_flash_intel` | G | H | H | H | H | G | **∅** | **∅** |
| `0x06` | `configure_flash_nor_unlock` | G | H | H | H | H | G | **∅** | **∅** |
| `0x05 0x35 0x39` | `configure_flash_5v_page` | G | H | H | H | H | G | **∅** | **∅** |
| `0x0E 0x27 0x28 0x29` | `configure_sram` (empty body!) | G | G | **∅** ⚠ | **∅** ⚠ | **∅** ⚠ | G | **∅** | **∅** |
| `0x11 0x2A–0x2C 0x34 0` | `configure_not_implemented` | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ |

**Reading of the blast radius — every cell that changes from silent-OK to `0xA5`:**

1. **`0x0D` + `CMD_ERASE`** — DEVTEST-01. **Intended, and the reason D-08 pulls Phase 121's firmware half here.**
2. **`0x0D` + `CMD_CHECK_CHIP_ID`** — also a phantom today. But `eprom_check_chip_id` refuses earlier with `MSG_ERR_NO_CHIP_ID` when `handle->chip_id == 0`, and TRACE-05 pinned `chip_id_check: false` across all 84 `algorithm == 13` entries — so in practice the host never sends a non-zero chip id for `0x0D` and this cell is already refused upstream. Note it, don't over-claim it. (`eeprom28c_check_chip_id` exists but is `static` and called only from `write_init`; it is not wired as a `CMD_CHECK_CHIP_ID` main.)
3. **SRAM + `CMD_ERASE`** — new refusal. `configure_sram`'s body is *literally just a debug log*.
4. **SRAM + `CMD_BLANK_CHECK`** — new refusal. See F-F2 on `_SRAM_PROTO_IDS`.
5. **SRAM + `CMD_CHECK_CHIP_ID`** — new refusal, subject to the same upstream `chip_id == 0` gate.
6. **Every non-`0x0D` protocol + cmd 9/10** — the fail-closed refusal LOCK-04 actually wants. Note this is where D-06's "provably total" claim earns its keep: no per-handler arm is needed for any of the six families.
7. **`configure_not_implemented` protocols** — *unchanged*. That handler sets `response_code = RESPONSE_CODE_ERROR`, so `op_execute_function(configure_memory, …)` already returns false and `parse_json` already emits `MSG_ERR_SETUP` — the op layer is never reached. **No double-error, no new frame.** Worth a native case so a reviewer can see it.

**Byte-identity requirement:** the streams for `0x05/0x06/0x07/0x08/0x0B/0x10`/SRAM must stay byte-identical. The matrix shows why that is expected: no cell in a column those families exercise changes from `H`/`G` to anything else. The change is purely in the `∅` cells, none of which emit bus traffic today.

### F-F — ⚠ NEW and structurally decisive: `[env:native]` does not compile the op layer or the dispatcher (Q1, Q2, validation)

`[VERIFIED: platformio.ini build_src_filter, read live]`

```ini
build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c>
test_build_src = yes
```

So the native binaries compile `src/proms/*.cpp`, `src/boards/rurp_serial_utils.cpp`, `src/json_parser.c`, and the test TUs — and **nothing else**. Not `firestarter.cpp`, not `operation_utils.cpp`, not `eprom_operations.cpp`, not `hardware_operations.cpp`, not `dev_tools.cpp`. `[VERIFIED: grep for op_execute_*/op_get_message/op_wait_for_ack across test/ → zero stub definitions]`. There is no linker error today only because nothing in `src/proms/` calls those functions — the only `operation_utils` symbols `proms/` uses (`is_operation_in_progress`, `set_operation_in_progress`) are `static inline` **in the header** at `include/operation_utils.h:41-49`.

**Consequence 1 — this RESOLVES the "where is `is_memory_cmd()` declared" discretion item.** For D-04's truth-table suite to link in either env, the predicate must be **`static inline` in a header**. `firestarter.h` (which every TU already includes) or `operation_utils.h` (which has the `static inline` precedent) both work; a definition in `firestarter.cpp` or a new `.cpp` TU does **not**, unless `build_src_filter` is widened. Recommend `firestarter.h`, immediately after the `CMD_*` block, so the predicate and the enumeration it mirrors are adjacent and reviewable together.

**Consequence 2 — D-06's guard is not natively testable where it belongs.** `operation_utils.cpp:89` is not compiled natively. Two options:

| Option | What it gets | What it costs |
|---|---|---|
| **(a) Widen `build_src_filter` with `+<operation_utils.cpp>`** | D-08's cross-family sweep becomes a machine-checked enumeration: drive `configure_memory` with each (cmd, protocol) pair, then call the real `op_execute_stateful_operation` and assert `0xA5` appears exactly where the F-E matrix says `∅`. This is the strongest available proof and the only one that covers the *wiring*, not just a helper. | Affects **all 16** native suites (one binary per suite). `operation_utils.cpp`'s externals are `rurp_communication_*` (supplied by the already-linked `rurp_serial_utils.cpp`), `millis`/`delay` (ArduinoFake), `strncmp_P`/`PSTR` (the per-suite `avr/pgmspace.h` shim), and the `LOG_*` macros. **Risk: ArduinoFake ABORTS (SIGABRT) on any unmocked virtual** — only 4 suites currently mock `millis`/`delay`. Must be verified suite-by-suite; a SIGABRT here reads exactly like the known Unity-teardown flake but is not it. |
| **(b) Extract `static inline bool op_refuse_if_no_main(handle)` into `operation_utils.h`** and call it from `:83` | The predicate + refusal is natively testable in isolation, in both envs, with zero risk to existing suites. | The one-line call site stays unproven natively; the wiring is only proven by the AVR build compiling. Weaker, but honest if recorded as such. |

Recommend **(a)**, with (b) as the recorded fallback if a suite aborts. D-08 asks for "every command × protocol combination that previously returned a silent OK enumerated with its new outcome" — under (b) that enumeration is prose; under (a) it is a test.

**Consequence 3 — the new lock/unlock ops ARE natively provable end-to-end**, because `src/proms/eeprom_28c.cpp` *is* in the filter. See F-I.

### F-F2 — `_SRAM_PROTO_IDS` becomes belt-and-braces, not dead code (D-08 item 2)

`[VERIFIED: firestarter_app/firestarter/eprom_operations.py:1653-1677]` The host short-circuits SRAM/FRAM blank-check **before issuing any firmware command**, so D-06's guard is not reachable from `check_eprom_blank`. Its comment claims the firmware emits `0xA4 MSG_ERR_EMPTY_INPUT` — that is a **follow-on artifact** of the silent completion (the firmware returns to `CMD_IDLE`, then re-reads the host's next byte as a fresh COBS frame and rejects it), not a firmware refusal. D-07's "no error at all" is correct about the command itself.

**Finding for the plan:** the workaround does **not** become dead code. It fires earlier and produces a materially better user-facing message than a bare `0xA5` would. **Identify it here, do not delete it (host surface = Phase 120), and record that the correct Phase-120 disposition is "keep".**

### F-G — ⚠ MEASURED THIS SESSION: a no-DEV_TOOLS build compiles and passes (Q1, folded todo item 4)

The folded todo `prove-pio-dev-flag-fails-closed.md` notes that *"the shared-`[env]` inheritance means it has never actually been exercised without the flag."* `[VERIFIED: platformio.ini:26 — `-D DEV_TOOLS` is in the shared `[env]` block, inherited by all three AVR envs AND `[env:native]` (whose `build_flags` begins `${env.build_flags}`)]`.

**Experiment run.** A temporary `[env:native_nodevtools]` was appended (a copy of `[env:native]` with `${env.build_flags}` replaced by `-D MONITOR_SPEED=250000 -D HARDWARE_REVISION`), and a temporary `[env:leonardo_nodevtools]`. Both were removed afterwards; **`platformio.ini` restored byte-clean, verified by an empty `git status --short`.**

| Command | Result |
|---|---|
| `pio test -e native` (baseline, DEV_TOOLS present) | **112/112 test cases, 16/16 suites PASSED** in 18.1 s |
| `pio test -e native_nodevtools` (DEV_TOOLS absent) | **112/112 test cases, 16/16 suites PASSED** in 52.2 s |
| `pio run -e leonardo_nodevtools` | **SUCCESS** — Flash **24388**/28672 (85.1%), RAM 1958/2560 (76.5%) |

**Findings:**

1. **Folded todo item 4 is ANSWERED: yes, `pio test` passes with `DEV_TOOLS` absent.** Record this against the todo so 999.15 inherits the answer.
2. **D-04's second env carries zero test-porting cost.** No test file references `DEV_TOOLS` or `CMD_DEV_*` (`[VERIFIED: grep across test/ → zero non-markdown hits]`), so the whole existing `test_filter` runs green as-is. This resolves the discretion item "*whether the new env runs the full `test_filter` or a subset*" in favour of **the full filter** — it costs ~52 s of CI and buys DEV_TOOLS-invariance coverage across all 16 suites, not just the truth table.
3. **`-D DEV_TOOLS` costs 1292 B of Leonardo flash and 40 B of RAM** (25680 → 24388; 1998 → 1958). Useful for 999.15/gh#8's channel-split question, and it establishes that **the DEV_TOOLS build is the tighter configuration and therefore the binding constraint for LOCK-06.**
4. The `native_nodevtools` run is ~3× slower purely because it is a cold build. Not a finding.

### F-H — ⚠ MEASURED THIS SESSION: the live flash figures (Q6)

`pio run -e uno -e uno328pb -e leonardo` at firmware HEAD `1880054`:

| Board | MCU / capacity | Flash used | % | **Free** | RAM used |
|---|---|---|---|---|---|
| **Leonardo** | ATmega32U4, 28 KB | **25680** / 28672 | 89.6 % | **2992 B** | 1998 / 2560 (78.0 %) |
| Uno | ATmega328P, 31.5 KB | 23542 / 32256 | 73.0 % | 8714 B | 1559 / 2048 (76.1 %) |
| uno328pb | ATmega328PB | 23592 / 32384 | 72.9 % | 8792 B | 1563 / 2048 (76.3 %) |

**D-15 is confirmed exactly.** Leonardo `25680/28672` → **2992 B free** is the live number. LOCK-06's `3348 B` is a superseded pre-117 figure (`+204 B` Phase 117 and `+152 B` Phase 118 are already spent). **Judge this phase's delta against 2992 B and show the arithmetic; make no threshold claim beyond "fits".** Do not edit `REQUIREMENTS.md`.

Note the Uno / uno328pb *capacities* differ (32256 vs 32384) because the two board JSONs reserve different bootloader sizes — so a cross-board flash comparison must compare **deltas**, never percentages or free-space figures.

**What this phase's own decisions will spend flash on** (for the plan's own estimate, to be replaced by measurement): a generic NULL-`main` refusal (one `LOG_ERROR_ID` + one store — small); two new catalog ids (each id costs a PROGMEM format string plus a table row); two new `case` arms in `loop()`; two new `eprom_*` entry points; `EEPROM_SDP_ENABLE[3]` (3 × `sizeof(byte_flip_t)`, likely 18 B of PROGMEM/flash); the shared bracket helper (should be roughly **flash-neutral or negative**, since it de-duplicates 118's inline bracket); D-16's worst-case tracker (2 `micros()` calls + a compare + a `uint32_t` in the per-byte loop, plus one report line). The second native env and the four goldens cost **zero** production flash.

**On the defence-in-depth `default:`-arms-across-other-handlers option (Q6's last clause):** it is D-06's rejected alternative. Cost estimate: six arms × (a `LOG_ERROR_ID` call + a `response_code` store) ≈ 6 × ~14–20 B of AVR code plus the loss of the shared call site, so **roughly 90–130 B** — 3–4 % of the remaining Leonardo headroom, for zero additional coverage over the generic guard, *and* each arm must be hand-written not to swallow the pre-set generic mains (the F-D hazard, six times over). **Recommend not taken.** If the planner wants any `default:` arm in `configure_eeprom28c` at all (D-05 permits one; the discretion item is open), scope it to commands `0x0D` genuinely cannot do — i.e. explicitly `case CMD_ERASE:` and `case CMD_CHECK_CHIP_ID:` rather than `default:` — so it structurally cannot reach `CMD_READ`/`CMD_VERIFY`. That is a strictly safer spelling of the same intent and it makes the F-D hazard unrepresentable.

### F-I — How a golden trace is added and what makes traces "distinct" (Q5)

**Where goldens live.** `test/native/avr/_shared/sdp_expected.h`: a `static const sdp_strobe_t NAME[]` array of `{kind, pin, value}` triples plus a `#define NAME_LEN (int)(sizeof(NAME)/sizeof(NAME[0]))`. `kind` is `STROBE_KIND_DATA (1)` or `STROBE_KIND_PIN (2)`. Recorded by the `HOST_STUBS_REAL_REGISTER_UTILS` opt-in layer in `_shared/host_stubs_common.inc:81-130`, which hooks exactly two symbols (`rurp_write_data_buffer`, `rurp_set_control_pin`) and lets the **real** `rurp_register_utils.h` supply `rurp_write_to_register`, so production's cache-compare elision is captured rather than replicated.

**How a golden is authored.** Empirically, never hand-derived: drive the code, dump, then hand-check against an independently-derived latch table. The dump is guarded behind `#ifdef SDP_TRACE_DUMP` and — critically — **`pio test` swallows `printf` from test bodies, so you must run the built binary directly** (`.pio/build/native/firestarter_native`). `sdp_expected.h`'s own header calls this "the single most valuable diagnostic in this phase."

**How a golden is asserted.**

```cpp
// Source: test/native/avr/_shared/sdp_expected.h (verified live)
sdp_assert_stream_equals(SDP_FIXED_DIP28_28C256, SDP_FIXED_DIP28_28C256_LEN, "ctx");
//   1. TEST_ASSERT_EQUAL(0, strobe_overflowed())
//   2. TEST_ASSERT_EQUAL(expected_len, strobe_count())
//   3. positional {kind,pin,value} equality; on failure, names the first
//      diverging index AND both triples at that index.
```

**What makes traces "distinct" as an assertion.** Not `!= -1`. The in-tree discipline asserts the **exact divergence index**:

```cpp
// Source: test/native/avr/test_sdp_harness/test_sdp_harness.cpp:283-289 (verified live)
int div = sdp_first_divergence(SDP_SHIPPED_DIP28_28C256, SDP_SHIPPED_DIP28_28C256_LEN);
TEST_ASSERT_EQUAL_MESSAGE(26, div,
    "Negative B: three-write lock/write-prefix table must diverge from the six-write unlock "
    "stream at index 26 -- write #3's payload byte (0xA0 vs 0x80)");
```

To compare two *tables'* streams, snapshot the first — `drive()` calls `clear_strobes()`:

```cpp
sdp_strobe_t snap[32];
int len = sdp_snapshot(snap, 32);          // after driving table A
… drive table B …
TEST_ASSERT_EQUAL_MESSAGE(-1, sdp_first_divergence(snap, len), "…identical…");
```

**Predicted lock golden** `[ASSUMED — derived, must be dump-confirmed]`. The remap-aware (FIXED) per-write shape is **10 entries** for an un-elided write:

```
{2,4,1}                      // OE->1  (memory_set_data calls rurp_chip_input FIRST)
{1,0,lsb} {2,1,1} {2,1,0}    // DATA(lsb), LSB latch ^v
{1,0,msb} {2,2,1} {2,2,0}    // DATA(msb), MSB latch ^v
{1,0,payload} {2,0x20,0} {2,0x20,1}   // DATA(payload), CE low, CE high
```

So write #1 → indices 0–9, write #2 → 10–19, write #3 → 20–29, and **write #3's payload sits at index 27**. `SDP_FIXED_LOCK_DIP28_28C256` is therefore `SDP_FIXED_DIP28_28C256[0..29]` with index 27's value `0xA0` instead of `0x80`; length **30**.

- Divergence vs the 6-write unlock stream: **index 27** (payload `0xA0` vs `0x80`).
- Divergence vs the `FLASH_ERASE` stream: **index 27** (same reason — erase's third payload is also `0x80`).
- Divergence vs the `FLASH_ENABLE_WRITE` / `FLASH_ENABLE_WRITE_PROTECTION` streams: **none, by construction** (F-K).

*Method validated:* the same arithmetic on the **shipped** shape (payload at offset 6, since `OE->1` comes last there) predicts index `20 + 6 = 26`, which is exactly what the in-tree assertion above already asserts. Confidence MEDIUM → treat as a starting expectation and confirm by dump, per the standing empirical-authoring rule.

**Four pinouts, per D-10.** `SDP_BUS_CONFIGS` rows are `DIP28_28C256`, `DIP28_28C64`, `DIP24_2816`, `DIP32_28C512_EEPROM`. The MSB byte differs per pinout (`0x95` / `0x15` / `0x05` / `0x55` for `remap(0x5555)`); DIP32's remap is the identity under a zero CONTROL seed, so **only the OE-edge reordering distinguishes shipped from fixed there** — which is why the DIP32 case needs a deliberately stale upper-address seed rather than a plain trace.

**Driving the new lock op natively.** `eeprom_28c.cpp` is in `build_src_filter`, so:

```cpp
firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[0]);
h.cmd = CMD_SDP_LOCK;
configure_memory(&h);                      // ⚠ this itself writes registers
reset_register_cache(0x00, 0x00, ctrl_seed);   // ⚠ MUST come AFTER configure_memory
clear_strobes();
h.firestarter_operation_main(&h);          // init/end are NULL by design
```

The `configure_memory` → `reset_register_cache` ordering is load-bearing and already documented in both suites' helpers (`configure_memory` calls `mem_util_set_address(handle, 0)`).

### F-J — What a standalone command's declaration/registration looks like (Q3)

**Registration.** There is no dispatch *table* — the "table" is three function pointers on the handle, assigned by `configure_*`. A command is "registered" by (1) a `#define CMD_X n` in `firestarter.h`, (2) a `case CMD_X:` in `loop()`'s switch calling an `eprom_*`/`hw_*` entry point, (3) an arm in the relevant `configure_*` handler setting at least `firestarter_operation_main`. Leaving `init`/`end` unassigned is the default — `configure_memory` NULLs all three at entry (`memory.cpp:45-47`).

**The existing example to copy: `CMD_ERASE`.** `[VERIFIED]` `eprom_erase` (`eprom_operations.cpp:33-39`) → `op_execute_simple_operation` → `_single_step_operation_callback` (`operation_utils.cpp:278-305`), which calls the main once and marks the operation done. `configure_eprom`/`configure_flash_*` set only a main for `CMD_ERASE` (`configure_eprom` additionally sets an `end` when the blank-check isn't skipped — the new SDP commands need neither). This is the shape, and its host-side driver is the generic `_run_state_machine`, which already works today.

**⚠ `op_execute_simple_operation` has one command-specific branch.** `_single_step_operation_callback` special-cases `CMD_BLANK_CHECK` to flush progress/error frames in communication mode (`operation_utils.cpp:291-300`). Harmless for cmd 9/10 — the branch simply doesn't fire — but the planner should know the wrapper is not fully generic.

### F-K — LOCK-05 is already half-discharged in-tree, and criterion 5 conflicts with D-09 (Q4)

**Already in-tree.** `[VERIFIED: test/native/avr/test_sdp_harness/test_sdp_harness.cpp:291-310]` — `test_lock05_enable_write_and_write_protection_identical` already drives both `FLASH_ENABLE_WRITE_PROTECTION` and `FLASH_ENABLE_WRITE` and asserts element-wise stream identity, and its comment says:

> *"LOCK-05 finding, recorded as a case (not prose) … Atmel doc0270 section 19 note 2 — this duplication is datasheet-correct. Phase 119 LOCK-05 requires the duplication be PRESERVED, not deduplicated. A trace-based negative between THESE TWO SPECIFIC tables is therefore impossible by construction — **a later editor must not try to add one.**"*

So the two-way identity **and** the datasheet rationale are already machine-checked and recorded. What D-10 adds is only: the **third** leg (`EEPROM_SDP_ENABLE` == the other two), the **distinct-objects** assertions (`(const void*)A != (const void*)B` for all three pairs — the alias-refactor hazard `test_fix05_...` already guards for the unlock table at `:257-260`), and the **no-payload stream-length** assertion. The natural home is beside `test_fix05_terminal_byte_and_table_identity_guards` in the same suite, reusing its `sdp_tables_identical()` helper (`test_sdp_harness.cpp:152-160`).

**⚠ ROADMAP criterion 5 vs D-09 — a fourth divergence the planner must own.** ROADMAP criterion 5 requires *"a **header comment** recording why the duplication is datasheet-correct."* `[VERIFIED: include/flash_utils.h:42-53 has NO such comment today — the two tables sit bare]`. But `flash_utils.h` is **FIX-04 byte-frozen** and D-09 keeps it *"byte-frozen"*; FIX-04 is a closed, `[x]` requirement asserting `flash_utils.{h,cpp}` are byte-untouched. Editing it — even comment-only — would re-open that claim and break `118-NONREGRESSION.md`'s framing.

**Recommended resolution (planner must record it as a deliberate deviation, like D-05 and D-15):** satisfy criterion 5's *intent* by placing the rationale comment beside `EEPROM_SDP_ENABLE` in `eeprom_28c.cpp` — which is exactly what D-10 already directs ("*the rationale comment sits next to the new table in `eeprom_28c.cpp`, backed by the guard rather than standing alone*") — and cite the pre-existing `test_sdp_harness.cpp:291-296` comment as the second record. Do **not** edit `flash_utils.h`. Do **not** edit `REQUIREMENTS.md`.

### F-L — `test_sdp_table_parity.py` is safe against `EEPROM_SDP_ENABLE`, but gains no coverage

`[VERIFIED: tests/test_sdp_table_parity.py:117-125]` The extractor is `re.compile(rf"\b{re.escape(decl_name)}\s*\[\s*\d*\s*\]\s*=\s*")` with `decl_name = "EEPROM_SDP_DISABLE"`. `EEPROM_SDP_ENABLE` is not a substring of it and `\b` anchors the start, so **adding the new table cannot break this gate.** The bracket group already accepts both `NAME[] = {` and `NAME[6] = {` (Phase 117 widened it for exactly this reason), and the required trailing `=` excludes the bare `extern … NAME[3];` line. **Re-verify after every edit anyway** — this module was broken 3× by Phase 117's identifier and declaration-syntax changes.

**Opportunity (cheap, recommended):** add a sibling test asserting `EEPROM_SDP_ENABLE` == `FLASH_ENABLE_WRITE_PROTECTION` == `FLASH_ENABLE_WRITE` at the *source-text* level, reusing `_extract_byte_flip_pairs` unchanged. It is a second, independent oracle for D-10's three-way identity (the firmware one is a link-time object comparison; this one is textual), and it costs ~15 lines. It also keeps the host gate's coverage in step with the firmware, which is the CORRECTION-4 item-4 spirit.

### F-M — ⚠ HIGH RISK: `check_no_log_in_sdp_window.py` will FAIL CLOSED if D-14's helper moves the emit call

`[VERIFIED: tools/check_no_log_in_sdp_window.py:249-317, read live]` The gate does four things, each fail-closed:

1. Brace-match `eeprom28c_emit_command_sequence`'s **definition** → scan its body for `LOG_*`.
2. Brace-match `eeprom28c_wait_for_sdp_completion`'s **definition** → scan its body.
3. Brace-match `eeprom28c_write_init`'s **definition**.
4. **Inside `write_init`'s body**, require an emit anchor, then a wait anchor *after* it.

Anchors (append-only by contract):
```python
_EMIT_ANCHOR_PATTERNS = (
    re.compile(r"flash_execute_command\s*\(\s*EEPROM_SDP_DISABLE\s*\)"),
    re.compile(r"eeprom28c_emit_command_sequence\s*\(\s*handle\s*,\s*EEPROM_SDP_DISABLE\b"),
)
_WAIT_ANCHOR_PATTERNS = (
    re.compile(r"eeprom28c_wait_for_write\s*\("),
    re.compile(r"eeprom28c_wait_for_sdp_completion\s*\("),
)
```

**The breakage.** D-14 factors 118's `micros()` bracket + budget check into a shared helper both sequences call. If that helper also wraps the **emit call** (the natural factoring — the bracket exists *to time the emit*), then `eeprom28c_write_init` no longer contains a literal `eeprom28c_emit_command_sequence(handle, EEPROM_SDP_DISABLE` and step 4's `emit_anchor is None` → `raise ValueError` → **exit 1**. Same if the completion-wait call moves in. **The firmware suite stays 112/112 green; only `firestarter_app` CI catches it.** This is the exact pattern that bit Phase 117 four times and broke 4 of 6 of this very gate's own pytest cases in Phase 118.

**Two further tripwires on the same gate:**
- `_func_def_pattern` is `\bvoid\s+NAME\s*\([^)]*\)\s*\{` — it requires the return type to be **literally `void`**. Changing `eeprom28c_emit_command_sequence` to return `bool` (e.g. to report a budget breach) breaks window resolution.
- D-11 declines reusing `eeprom28c_wait_for_sdp_completion` for the lock, so that function survives — good. But if a later edit deletes or renames it, step 2 fails closed.

**Required task work (name it in the plan, do not let it be discovered):**
1. **Append** a new `_EMIT_ANCHOR_PATTERNS` entry matching the shared helper's call site inside `write_init` (append-only — keep both superseded patterns).
2. Consider whether the *helper's own body* should become a third scanned window. It will contain `LOG_ID`/`LOG_ID_U32`/`LOG_WARN_ID_U32` calls **by design** (D-12/D-14), so it must **not** be scanned by the no-log rule. State that explicitly in a comment so a future editor doesn't "helpfully" add it. The no-log invariant remains correctly enforced because the *emitter* body — the actual inter-byte window — is still scanned and is still shared by both sequences.
3. Repair `tests/test_check_no_log_in_sdp_window.py` and `tests/fixtures/planted_log_in_window.cpp`: the fixture is a temp/committed `.cpp` shaped like the old source, and the resolver's fail-closed `ValueError` is what broke 2 of its cases in Phase 118. Any case asserting a specific line number (Phase 118 had one hardcoding `"line 29"`) will shift.
4. Re-run `python3 tools/check_no_log_in_sdp_window.py` (expect the `PASS:` line naming both resolved ranges) after **every** firmware edit in this phase, not just at the end.

**Baseline established this session:** `PASS: no logging call in SDP timing window (…/eeprom_28c.cpp, emitter lines 222-238, completion-poll lines 272-285)`, exit 0.

### F-N — The second native env's real requirements (D-04)

`[VERIFIED: platformio.ini:69-157]` `[env:native]` uses a **positive `test_filter` allowlist** — a suite is invisible until its directory is listed there **and** it has a matching `-I test/native/avr/<dir>` entry in `build_flags`. Both lists are 16 entries long today.

So `[env:native_nodevtools]` needs: `platform = native`, `test_framework = unity`, its **own** full `test_filter` block, its **own** full `-I` list, `-std=gnu++17`, `-I include`, `-D RURP_BOARD_NAME=\"native\"`, `lib_deps = fabiobatsilva/ArduinoFake@^0.4.0`, `build_src_filter`, `test_build_src = yes`, and `build_flags` that **do not** reference `${env.build_flags}` — instead spelling out `-D MONITOR_SPEED=250000` and `-D HARDWARE_REVISION` explicitly. (F-G's experiment used exactly this and it worked.)

⚠ `-D HARDWARE_REVISION` is **load-bearing**, not incidental: `host_stubs_common.inc:208-224` gates four hardware-revision stubs on it, and `HOST_STUBS_REAL_REGISTER_UTILS` suppresses them precisely because `[env:native]` inherits that flag. Dropping it changes which stubs compile and will break the SDP suites.

⚠ `default_envs = uno, uno328pb, leonardo` (`platformio.ini:16`) must **not** gain the new env — `pio run` would try to link a `main()`-less target ("undefined reference to main"), the exact failure the `default_envs` constraint exists to prevent.

**CI:** `firestarter/.github/workflows/build.yml:91` runs `pio test -e native` (one env only) and `:111` runs `pio run`. **A new step `pio test -e native_nodevtools` must be added** or the second env never runs in CI and D-04's proof is local-only. The workflow's `on:` triggers are `push`/`pull_request` to `main` only — so it will not fire on the milestone branch; the in-phase proof is the local run, exactly as with the catalog-sync job.

### F-O — ⚠ D-16 breaks the `micros()` mock's parity model

`[VERIFIED: test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp:133-137, 209-215]`

```cpp
static uint32_t s_micros_ticks[2];
…
unsigned long v = s_micros_ticks[s_micros_call_count % 2];
```

A 2-slot **parity alternator**: call #0 → `ticks[0]`, call #1 → `ticks[1]`, call #2 → `ticks[0]`, … Cases 11 and 12 depend on `drive_write_init` producing exactly two `micros()` calls.

**D-14's shared bracket keeps 2 calls per sequence, so a lock case can reuse the model as-is.** But **D-16's per-byte page-load tracker adds `micros()` calls inside `eeprom28c_write_execute`** — 1–2 per byte. For any case that drives `write_init` *and* `write_execute` in one test body, the parity shifts and every subsequent interval alternates between `0` and `ticks[1]`, which is meaningless. And `test_sdp_harness` mocks `micros()` to `AlwaysReturn(0)` (`test_sdp_harness.cpp:88`), so the tracker measures 0 there — inert, but zero coverage.

**Required task work:** upgrade the mock to a scripted tick **queue** (a `std::vector<uint32_t>` with a monotonic cursor and a documented default-tail value), then **re-verify cases 11 and 12** explicitly. Do not treat this as incidental refactoring — it is the oracle 118's OBS-03 proof rests on. Also decide whether the page-load report line participates in Case 12's "exactly two report frames" count: if `write_execute` gains a report line, any case that drives both phases will see three, and Case 12's assertion must be re-scoped to `write_init` (it already is — it drives `drive_write_init` only — but state that this is now load-bearing).

### F-P — Message catalog: free ids and the exact entry shape (D-13)

`[VERIFIED: tools/catalog/messages.toml, read live]`

- Bands: OK `0x01–0x0F`, INIT `0x10–0x1F`, MAIN `0x20–0x2F`, END `0x30–0x3F`, INFO `0x40–0x7F`, WARN `0x80–0x9F`, ERROR `0xA0–0xDF`, DATA `0xE0–0xEF`.
- **Highest INFO in use: `0x5F` (`MSG_INFO_SDP_UNLOCK_DONE_US`). Free from `0x60`.**
- **Highest WARN in use: `0x87` (`MSG_WARN_SDP_TBLC_EXCEEDED`). Free from `0x88`.**
- `MSG_ERR_NOT_SUPPORTED = 0xA5` exists (`"Not supported"`, `params = []`). **D-06 needs no new ERROR id.**

Template — 118's pair, which the lock's pair mirrors:

```toml
[[messages]]
id          = 0x5E
name        = "MSG_INFO_SDP_UNLOCK"
severity    = "INFO"
format      = "SDP unlock: disabling write protection"
params      = []
wire_format = "id_frame"

[[messages]]
id          = 0x5F
name        = "MSG_INFO_SDP_UNLOCK_DONE_US"
severity    = "INFO"
format      = "SDP unlock emitted in %lu us"
params      = [{ type = "u32", render = "dec" }]
wire_format = "id_frame"
```

**D-12's honesty requirement lives in the `format` string.** The lock's "emitted" line must say the sequence was emitted **and that the protection state cannot be read back**. Suggested shape (wording is discretion): `"SDP enable: sequence emitted; protection state is not readable"`. Keep **names ≤ 32 chars** to avoid `messages.h` column reflow (118-02's finding) — e.g. `MSG_INFO_SDP_LOCK` (17) and `MSG_INFO_SDP_LOCK_DONE_US` (25) both fit.

**The three-repo ritual (118 D-03):** edit `tools/catalog/messages.toml` (meta, **only** this) → `tools/catalog/sync_to_subrepos.sh` → verify with a local three-way `cmp` plus both `codegen.py --check` gates. `.github/workflows/catalog-sync-check.yml` **cannot go green** for v1.22 catalog work because it checks out both sub-repos at `ref: main` — known and expected, not this phase's damage.

**Graceful degradation:** `firestarter_app/firestarter/codec.py:206-209` logs `"Unknown message ID 0x.. — catalog out of date?"` and drops the frame, so a released `3.0.0b11` host handles the new ids without crashing.

### F-Q — The `t_WC` constant and the header surface

`[VERIFIED: eeprom_28c.cpp:42, :58, :101-106; include/eeprom_28c.h]`

- `AT28C_TWC_MAX_MS 10` — D-11's `delay()` argument. `[CITED: Microchip DS20006432B §6.6.2 p.10 / DS20006386B p.10, via research SUMMARY]`.
- `AT28C_TBLC_MAX_US 100` — D-14's per-byte budget.
- **Both are `#define`s inside `eeprom_28c.cpp` and are NOT exported via `eeprom_28c.h`.** Case 11 handles this by mirroring the value as a named local with an explicit `eeprom_28c.cpp:54` citation. The lock's budget case must do the same (`3 × 100 = 300 µs`).
- `eeprom_28c.h` exports **only** `configure_eeprom28c`. The new lock/unlock op functions can stay file-`static` (they're reached through the function pointers), so **no header change is needed** — good for flash and for keeping the host gates' scanned surface stable. The forward declarations go in the existing block at `:101-106`.

### F-R — Host gates that scan firmware source: the complete checklist (CORRECTION 4 item 4)

`[VERIFIED: grep for firmware-path references across firestarter_app/tools/ and tests/]` — nine files reference the firmware sub-repo. Disposition for this phase:

| Gate | Scans | This phase's risk | Action |
|---|---|---|---|
| `tools/check_no_log_in_sdp_window.py` + `tests/test_check_no_log_in_sdp_window.py` + `tests/fixtures/planted_log_in_window.cpp` | `eeprom_28c.cpp` — 3 brace-matched function definitions + 2 anchor sets | **HIGH — will fail closed** (F-M) | Named task work: append emit anchor, repair pytest + fixture, re-run after every edit |
| `tests/test_sdp_table_parity.py` | `eeprom_28c.cpp` + `flash_utils.h` source text | LOW — name-exact extractor is safe (F-L) | Re-verify; **recommend adding an `EEPROM_SDP_ENABLE` parity leg** |
| `tools/gen_sdp_bus_config.py` + `tests/test_sdp_bus_config_drift.py` | `firestarter/data/pinouts.json`; generates `_shared/sdp_bus_config.h` | LOW — no pinout change in scope | Re-run the regenerate-and-diff gate; the generated header must stay blob-identical |
| `tests/test_revision_constants_parity.py` | `firestarter.h` / `rurp_shield.h` / `rurp_pinout.h` — via **hardcoded literals**, not header enumeration | **NONE** — verified at `:103-117`; firmware-only `CMD_*`/`FLAG_*` additions are invisible to it (F-S) | Confirm still green. **Do NOT add `CMD_SDP_*` to `constants.py`** — Phase 120 HOST-03 |
| `tools/check_dispatch.py` | `memory.cpp::configure_memory` dispatch order | LOW — this phase changes no dispatch **order** | Re-run (green this session, exit 0) |
| `tests/test_dispatch_mirror.py` | `firestarter/doc/PROTOCOLS.md` + `test_configure_memory.cpp` hex tokens | LOW — no new protocol | Re-run |
| `tools/check_devtest_orchestrator.py` | **explicitly REJECTS any firmware path** (`:310-327`) — asserts `dev test` is host-only Python | **NONE** — verified | Confirm untouched; DEVTEST-01's firmware half does not interact with it |
| `tools/build_db.py`, `tools/diff_db.py`, `tools/audit_coverage_matrix.py` | DB / `infoic.xml` | NONE — zero DB change | `diff_db.py` identity is a GATE-03/CLOSE-01 item |
| **NEW: the D-04 `is_memory_cmd()` no-`#ifdef` gate** | `firestarter.h` (or wherever the predicate lands) | — | **Add it to this table for Phases 120–122.** Follow the fail-closed `FIRESTARTER_*_SRC` override idiom + a committed planted-violation fixture |

**Known-RED, not this phase's damage** (do not chase, do record): `tests/test_audit_coverage_matrix.py` is pre-existing RED (`.planning` memory `reference_audit_coverage_matrix_golden_stale.md`); `tests/test_no_programmer_found_*` go RED with a live board attached — **and all three boards ARE attached right now** (`/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0`, verified this session), so expect this during D-18's bench work (`.planning` memory `reference_characterization_no_programmer_tests_fail_with_live_board.md`).

### F-S — The host constants surface is untouched by design

`[VERIFIED: tests/test_revision_constants_parity.py:103-146]` The `CMD_*` block asserts thirteen hardcoded literals; the `FLAG_*` block asserts eight. Neither enumerates the firmware header. And it already carries the right precedent for F-C's problem:

> *"`COMMAND_DEV_ADDRESS` (0x07) and `COMMAND_DEV_REGISTERS` (0x08) are inside `#ifdef DEV_TOOLS` in the firmware header. The Python side defines them unconditionally so the parity assertions below stand as Python-value-only checks (not against a header literal that may not be compiled in)."*

Confirms both that firmware-only additions are safe **and** the exact idiom the firmware truth-table test should copy.

### F-T — Standalone lock/unlock wire shape (Q3, LOCK-02's honest claim)

`[VERIFIED: operation_utils.cpp:62-90, 195-260, 304-312; state macros at include/operation_utils.h:24-27 — INIT 1 / MAIN 3 / END 5 / ENDED 6]` Traced by hand through the state machine for a command with `init == NULL`, `end == NULL`, `main` set, via `op_execute_simple_operation`:

| Pass | `operation_state` | Host must send | Firmware emits |
|---|---|---|---|
| 1 | 0 → 1 → 2 | **ACK₁** | `MSG_INFO_INIT_START`, then `MSG_INIT_DONE` — the INIT phase runs **empty**, not skipped |
| 2 | 2 → 3 → 4 | **ACK₂** | `MSG_INFO_MAIN_START`; `main()` runs (3 latch writes + `t_WC` + the report pair); `MSG_INFO_MAIN_DONE` + `MSG_MAIN_DONE` |
| 3 | 4 → 5 → 6 | **ACK₃** | `MSG_INFO_END_START`, then `MSG_END_DONE` — END also runs empty |
| 4 | 6 (ENDED) | **ACK₄** | `command_done()`: chip disable, CONTROL/LSB/MSB zeroed, `cmd := CMD_IDLE` |

**So: 4 host ACKs, 7 framed lines around the op's own frames, ZERO `#` data frames, ZERO `DONE` string.** The `DONE` round-trip lives only in `eprom_operations.cpp::_process_incoming_data` (the write path), which the SDP commands never enter.

**This is the precise sense in which LOCK-02's claim is true.** CONTEXT.md already flags that ROADMAP criterion 1's *reason* ("`init`/`end` left NULL for both" ⇒ phases skipped) is imprecise — confirmed: the phases **run empty and each still costs an `op_wait_for_ack()` round-trip**. `op_wait_for_ack` has a **1000 ms** timeout and emits `MSG_ERR_TIMEOUT` on expiry (`operation_utils.cpp:110-123`). Phrase the criterion as *"no data payload and no `DONE` round-trip"* — that is exactly what is absent — and note that the host's generic `_run_state_machine` already supplies all four ACKs today, which is why `CMD_ERASE` works.

### F-U — D-16's page-load measurement, framed correctly

`[VERIFIED: eeprom_28c.cpp:417-470]` `eeprom28c_write_execute`'s per-byte loop calls `handle->firestarter_set_data` once per byte, flushing at `PAGE_SIZE 64` boundaries or the last byte, then polls (`eeprom28c_wait_for_page_write`) and reads back (`eeprom28c_verify_page_readback`).

- **The two budgets are different things, and the directive conflates them.** LOCK-06 is a **flash** budget (bytes of program memory). F-118-01 is a **timing** budget (µs per byte load). Say so explicitly in `119-MEASUREMENT.md`, then answer the timing question anyway — the page-load loop runs under the identical `AT28C_TBLC_MAX_US` constraint and is where gh#11's symptom actually lives.
- **gh#11 framing discipline:** it is a **CONFLATION** bug (Phase 117's finding — a whole-byte equality compare that passed spuriously whenever the old byte already equalled the new one), **not** a sampling-rate bug. Aim every sentence at the conflation. The existing citation comment at `:431-445` already says this; reuse its wording.
- **Reporting shape:** track the **worst** per-byte interval across all pages, report it in **one** line after the write completes. A naive per-page report emits ~512 lines on a 32 KB write (32768 / 64), which violates 118's OBS-05 named-exceptions discipline.
- **No runtime compare in the hot path** (D-16 explicitly, preserving 118's D-10).
- **Reachability:** `write -b --force` on the shipped CLI. `-b` gets past the blank check an empty socket fails; `0x0D` has **no erase arm** (F-E), so `-b` skips nothing else on this family. ⚠ Standing caveat for any *other* family: `write -b` SKIPS ERASE and can silently corrupt a non-blank chip while still reporting success (`.planning` memory `reference_write_b_skips_erase.md`) — but on `0x0D` that hazard does not exist because there is no erase to skip. State the reasoning rather than relying on the memory.

## Common Pitfalls

### Pitfall 1: The literal LOCK-04 `default:` arm

**What goes wrong:** `read` and `verify` break on all 84 `0x0D` chips.
**Why:** `configure_memory` pre-sets their mains *before* `configure_eeprom28c` runs, and they fall through its switch (F-D).
**How to avoid:** put the refusal at the op layer (D-06). If any arm is added to `configure_eeprom28c`, spell it `case CMD_ERASE: case CMD_CHECK_CHIP_ID:` — never `default:`.
**Warning sign:** a native `test_val_eeprom28c` read/verify case going RED, or `configure_memory` dispatch cases failing for `0x0D`.

### Pitfall 2: A firmware rename that only host CI catches

**What goes wrong:** the firmware suite stays 112/112 green while `firestarter_app` CI goes red.
**Why:** four host gates resolve firmware **source text** by literal function name, path, or regex anchor. Fail-closed by design, so a rename becomes an error, not a silent pass.
**How to avoid:** F-M's four named repairs, executed in the *same plan* as the firmware edit. Re-run all of `check_no_log_in_sdp_window.py`, `check_dispatch.py`, `test_sdp_table_parity.py`, `test_sdp_bus_config_drift.py`, `test_revision_constants_parity.py` at **every wave**, not just at phase end.
**Warning sign:** the gate printing `ERROR:` / raising `ValueError` instead of its `PASS:` line. Track record: 4× in Phase 117, 4 pytest cases in Phase 118.

### Pitfall 3: An `#ifdef` sneaking into `is_memory_cmd()` — or the test naming a conditional macro

**What goes wrong:** either the invariance test passes vacuously (an `#ifdef` inside the predicate), or `native_nodevtools` fails to compile (the test naming `CMD_DEV_ADDRESS`).
**Why:** those two macros only exist under `-D DEV_TOOLS` (F-C).
**How to avoid:** the predicate names only the eight unconditional `CMD_*`; the test uses numeric literals `7`/`8` with a citation, copying `test_revision_constants_parity.py:110-112`'s idiom. The D-04 source-scan gate catches the first case; compiling in both envs catches the second.

### Pitfall 4: A golden pinned to the wrong expectation stays green

**What goes wrong:** the "no payload" invariant is asserted against a table comparison, which cannot observe an absence.
**Why:** `EEPROM_SDP_ENABLE` is byte-identical to the protected-write prefix; the discriminator is that **no data write follows** (F-A, D-10).
**How to avoid:** the three-way identity guard **plus** an explicit assertion that the lock stream terminates after exactly 3 command writes (length 30 in the FIXED shape) with no trailing data write. Assert an **exact** divergence index against the unlock and erase streams, never merely `!= -1`.

### Pitfall 5: SIGABRT in a new native suite reads like the known Unity flake

**What goes wrong:** a new suite aborts and gets misdiagnosed as the deferred `test_flash_intel_vpp` Unity-teardown SIGABRT.
**Why:** **ArduinoFake ABORTS on any unmocked virtual.** The SDP suites mock `delayMicroseconds`, `delay`, `millis`, `micros` and comment them as *"load-bearing — do not remove as unused."*
**How to avoid:** any new suite (the truth table; a widened `build_src_filter` per F-F option (a)) must mock every Arduino virtual its call path reaches. `op_execute_stateful_operation` reaches `millis()` and `delay()`.
**Warning sign:** an abort in a brand-new suite — that is this, not the deferred flake.

### Pitfall 6: Register-cache seeding in the wrong order

**What goes wrong:** the first write's LSB/MSB latches are elided or wrong, shifting every golden index.
**Why:** `configure_memory` itself calls `mem_util_set_address(handle, 0)`, which writes registers.
**How to avoid:** always `configure_memory(&h)` **then** `reset_register_cache(...)` **then** `clear_strobes()`. Both existing suites' helpers encode this and label it "load-bearing order."

### Pitfall 7: Asserting on the whole-file blob SHA of `sdp_expected.h`

**What goes wrong:** the non-regression proof 117 and 118 used becomes unusable, and someone either weakens it to prose or silently re-blesses a golden.
**Why:** D-10 adds `SDP_FIXED_LOCK_*` to that file, so its blob SHA **necessarily** changes.
**How to avoid:** shift to **per-array byte-identity of the pre-existing arrays** and say so explicitly in `119-NONREGRESSION.md`. Keep the whole-file blob-SHA assertion for `host_stubs_common.inc` and `sdp_bus_config.h`.

### Pitfall 8: The `micros()` mock's parity model silently degrading D-16's number

**What goes wrong:** the worst-case per-byte interval alternates `0`/`N` and means nothing; or cases 11/12 break.
**Why:** the mock is `s_micros_ticks[s_micros_call_count % 2]` (F-O).
**How to avoid:** upgrade to a scripted tick queue and re-verify cases 11 and 12 as named task work.

### Pitfall 9: The vacuous path check

**What goes wrong:** `git diff -- src/flash_utils.h` passes because that path does not exist (the real one is `include/flash_utils.h`).
**Why:** the ROADMAP's `flash_utils.{h,cpp}` shorthand is not a real path (FOURTH CORRECTION item 5).
**How to avoid:** enumerate this phase's firmware diff explicitly (`git diff --name-only <base>..HEAD`) and assert against the resulting list, as `118-NONREGRESSION.md:147-149` does. Same trap for any new path-based gate.

### Pitfall 10: Marking a multi-plan requirement Complete early

**What goes wrong:** LOCK-NN gets ticked by a plan that only did part of it. Happened 4× in Phase 116.
**How to avoid:** **name the allowed LOCK-NN ids in every dispatch prompt**, and re-check `REQUIREMENTS.md` after each plan (`.planning` memory `reference_executors_prematurely_mark_requirements_complete.md`).

## Discretion Items Resolved by Evidence

CONTEXT.md lists six discretion items. Three are now settled by facts; three remain the planner's call.

| Discretion item | Status | Evidence |
|---|---|---|
| **Where `is_memory_cmd()` is declared** | **RESOLVED → a header, `static inline`.** Recommend `firestarter.h`, adjacent to the `CMD_*` block. | `[VERIFIED]` `[env:native]` does not compile `firestarter.cpp` or any non-`proms/` TU, and no stub supplies those symbols. A `.cpp` definition is not natively linkable, so D-04's truth-table suite could not exist. `operation_utils.h:41-49` is the in-tree `static inline` precedent (F-F). |
| **Whether `native_nodevtools` runs the full `test_filter` or a subset** | **RESOLVED → the full filter.** | `[VERIFIED]` measured: 112/112 pass with `DEV_TOOLS` absent, zero test-code changes, ~52 s cold. The marginal CI cost is small and it buys DEV_TOOLS-invariance across all 16 suites (F-G). |
| **Whether `configure_eeprom28c` gets any narrowly-scoped `default:` arm** | **RESOLVED → if any, use explicit `case CMD_ERASE: case CMD_CHECK_CHIP_ID:`, never `default:`.** | `[VERIFIED]` the F-D hazard is unrepresentable under an explicit-case spelling, and F-E shows those are exactly the two commands `0x0D` cannot do. Non-load-bearing either way (D-06 covers it), so this is a self-documentation choice with the hazard removed. |
| **Whether lock and unlock share one op-layer function or take two** | **OPEN** — either is acceptable. Note one datum: two functions make the "which sequence ran" question answerable from a stack trace and keep D-13's separate-literal-ids shape literal; one function costs less flash against 2992 B. | — |
| **Exact format strings, wording and id numbers of the two new catalog entries** | **OPEN**, with constraints established: free INFO `0x60+`, free WARN `0x88+`, names ≤ 32 chars, the text itself must carry D-12's "state is not readable" honesty (F-P). | — |
| **The shared bracket helper's signature; whether the page-load tracker is file-static or on the handle** | **OPEN**, with one hard constraint added: the helper's signature and call-site spelling **must** be reflected in `_EMIT_ANCHOR_PATTERNS`, and the emitter must keep a `void` return type or `check_no_log_in_sdp_window.py`'s window resolution breaks (F-M). | — |
| **The order of the plan set** | **OPEN**, with the recommended order in `## Summary` and the two hard constraints from CONTEXT.md (catalog before emitting call sites; LOCK-03 before LOCK-02). Add a third: **`is_memory_cmd()` must land before or with the new `CMD_*` defines**, since under `-D DEV_TOOLS` cmd 9/10 would otherwise route to the dev branch and get no bus configuration (D-03, confirmed in F-B). | — |

## Runtime / Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| PlatformIO Core | firmware build + native tests | ✓ | `/usr/local/bin/pio` | — |
| Atmel AVR platform + avr-gcc | all three AVR envs | ✓ | 5.2.0 / GCC 7.3.0 | — |
| ArduinoFake | native suites | ✓ | 0.4.0 (in `.pio/libdeps`) | — |
| Python 3 (codegen) | catalog ritual | ✓ | 3.12 in devcontainer | ⚠ CI pins 3.11 for codegen and py3.9/3.11 for host lint — **validate against those, not 3.12** |
| pytest + host dev extras | `firestarter_app` gates | ✓ | 21/21 relevant gates green | `pip install -e '.[test]'` |
| Leonardo board | D-18 bench + F-118-01 comparison | ✓ | one of ACM0/ACM1 | D-19: record not-measured with reason |
| Uno board | D-18 bench | ✓ | one of ACM0/ACM1 | D-19 |
| uno328pb board | D-18 bench | ✓ | `/dev/ttyUSB0` (expected) | D-19; bench-unstable — retry on timeout, never trust N=1 |
| **AT28C silicon** | *nothing* | **✗** | — | **None needed. Validation ceiling: zero requirement depends on it.** |

**All three boards are attached right now** (`/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0` — verified this session), matching `118-MEASUREMENT.md` §2's port map. ⚠ **Port numbers shuffle across replug — re-verify the `controller:` identity line per candidate port before driving anything** (`.planning` memory `feedback_verify_port_identity_each_task.md`). Operator statement 2026-07-28: **all three sockets are EMPTY**, which is what makes `autonomous: true` with no operator checkpoint legitimate and satisfies the Uno-class chip-OUT-before-sideload rule — **the plan must say so rather than silently skipping the rule.**

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none blocking. The AT28C part is absent by design.

## Validation Architecture

### Test Framework

| Property | Value |
|---|---|
| Firmware framework | Unity via PlatformIO (`test_framework = unity`, `platformio.ini:70`) |
| Firmware config | `firestarter/platformio.ini` — `[env:native]` (+ NEW `[env:native_nodevtools]`) |
| Firmware quick run | `pio test -e native -f "*test_eeprom28c_sdp*"` (~1 s) |
| Firmware full suite | `pio test -e native` **and** `pio test -e native_nodevtools` |
| Firmware build check | `pio run` (links `uno`, `uno328pb`, `leonardo`) |
| Host framework | pytest |
| Host quick run | `python3 -m pytest tests/test_sdp_table_parity.py tests/test_check_no_log_in_sdp_window.py -q` (~2 s) |
| Host full suite | `python3 -m pytest -q` + `ruff` against py3.9/3.11 |
| Host gate scripts | `python3 tools/check_no_log_in_sdp_window.py`; `python3 tools/check_dispatch.py`; the NEW D-04 gate |
| **Baseline established this session** | **`pio test -e native`: 112/112, 16/16 suites. `pio test -e native_nodevtools`: 112/112. `pio run`: 3/3 SUCCESS. Host: 21/21 on the 4 relevant modules; `check_no_log_in_sdp_window.py` PASS; `check_dispatch.py` exit 0.** |

### Phase Requirements → Test Map

| Req | Behaviour to observe | Test type | Automated command | Exists? |
|---|---|---|---|---|
| LOCK-01 | The lock emits exactly the 3-load `AA·55·A0` stream on each of the 4 pinouts, then `delay(t_WC)`, with no data write following | firmware unit (golden trace) | `pio test -e native -f "*test_eeprom28c_sdp*"` | ❌ new cases + new `SDP_FIXED_LOCK_*` goldens |
| LOCK-01 | The lock stream diverges from the unlock stream at an exact index, and from `FLASH_ERASE`'s at an exact index | firmware unit (negative) | same | ❌ new |
| LOCK-02 | `configure_eeprom28c` sets a main for cmd 9 and cmd 10, and leaves `init`/`end` NULL | firmware unit (dispatch) | `pio test -e native -f "*test_dispatch*"` | ❌ new cases |
| LOCK-02 | The standalone command is a single-step op — 4 ACKs, no `#` frame, no `DONE` | **partly unprovable natively** — `operation_utils.cpp` is not linked (F-F). Provable under F-F option (a); otherwise reasoned from F-T + `CMD_ERASE` precedent | `pio test -e native` (option a) | ❌ / ⚠ see F-F |
| LOCK-03 | `is_memory_cmd(c)` returns the identical value for **every** `c ∈ [0,255]` in both build configurations | firmware unit (truth table, run in **2 envs**) | `pio test -e native -f "*test_cmd_admission*"` **and** `pio test -e native_nodevtools -f "*test_cmd_admission*"` | ❌ new suite (+ `test_filter` + `-I` in both envs) |
| LOCK-03 | The predicate's body contains no `#ifdef DEV_TOOLS` and enumerates exactly the 8 expected commands | host source-scan gate | `python3 tools/check_is_memory_cmd_no_ifdef.py` | ❌ new gate |
| LOCK-03 | …and that gate can actually fail | host pytest + planted fixture | `python3 -m pytest tests/test_check_is_memory_cmd_no_ifdef.py` | ❌ new |
| LOCK-03 (folded todo item 4) | The whole native suite passes with `DEV_TOOLS` absent | firmware full suite | `pio test -e native_nodevtools` | ✅ **already demonstrated this session: 112/112** |
| LOCK-04 | Lock/unlock against a non-`0x0D` protocol is refused with `MSG_ERR_NOT_SUPPORTED`, never silently accepted | firmware unit — **needs F-F option (a)**, else host-observable only on hardware | `pio test -e native` | ❌ / ⚠ |
| LOCK-04 (safety) | `CMD_READ`/`CMD_WRITE`/`CMD_VERIFY` are **never** NULL-main for any protocol reaching a handler | firmware unit (dispatch, positive invariant) | `pio test -e native -f "*test_dispatch*"` | ❌ new case — cheap and high value |
| LOCK-05 | `EEPROM_SDP_ENABLE` == `FLASH_ENABLE_WRITE_PROTECTION` == `FLASH_ENABLE_WRITE` byte-for-byte, **and all three are distinct objects** | firmware unit (constant-level cross-guard) | `pio test -e native -f "*test_sdp_harness*"` | ⚠ **two-way leg already exists** (`test_lock05_...`); third leg + distinctness ❌ |
| LOCK-05 | The lock stream terminates after exactly 3 command writes — no trailing data write | firmware unit (stream length) | same | ❌ new |
| LOCK-05 | (recommended second oracle) source-text parity of the three tables | host pytest | `python3 -m pytest tests/test_sdp_table_parity.py` | ❌ optional new leg |
| LOCK-06 | Measured flash delta on all three envs, within 2992 B Leonardo headroom | **flash-size measurement** | `pio run -e uno -e uno328pb -e leonardo`, diffed against a `git worktree` at the phase base | ✅ base measured this session; delta pending |
| DEVTEST-01 (fw half) | `CMD_ERASE` on `0x0D` is refused, not silently OK | firmware unit — **needs F-F option (a)** | `pio test -e native` | ❌ / ⚠ |
| D-08 sweep | `0x05/0x06/0x07/0x08/0x0B/0x10`/SRAM bus streams stay byte-identical | firmware unit + per-array golden byte-identity | `pio test -e native` (all 16 suites) + explicit per-array assertions | ✅ suites exist; the per-array identity record ❌ |
| D-08 sweep | Every (cmd × protocol) cell that previously returned a silent OK is enumerated with its new outcome | firmware unit table under F-F(a); otherwise a documented matrix | `pio test -e native` | ⚠ **F-E supplies the precomputed matrix either way** |
| D-14 | The lock's t_BLC budget WARN fires when over budget **and does not fire** at the default elapsed | firmware unit (paired positive + anti-hollow control) | `pio test -e native -f "*test_eeprom28c_sdp*"` | ❌ new; **requires the F-O micros mock upgrade** |
| D-14 | The budget WARN never writes `response_code` | firmware unit | same (extend `test_case8_...`'s invariant) | ✅ pattern exists |
| D-16 | Worst-case per-byte page-load interval, reported **once** per write | **bench measurement, 3 boards** | `firestarter write <chip> -b --force` on each port | ❌ — **hardware, Leonardo + Uno + uno328pb** |
| D-12 | The lock reports OK **and** the message text says the state is unreadable | firmware unit (frame-id + catalog format assertion) | `pio test -e native -f "*test_eeprom28c_sdp*"`; `codegen.py --check` | ❌ new |
| Catalog ritual | meta ↔ firmware ↔ host byte-identical; both generated artifacts drift-free | three-way `cmp` + two `--check` gates | `tools/catalog/sync_to_subrepos.sh`; `codegen.py --check` in each sub-repo | ✅ tooling exists |
| GATE-03 slice | host lint against the **CI** Python targets | host lint | `ruff check` / `ruff format --check` under py3.9/3.11, **not** 3.12 | ✅ |

### Sampling Rate

- **Per task commit:** `pio test -e native -f "*test_eeprom28c_sdp*" -f "*test_sdp_harness*"` (~2 s) **plus** `python3 tools/check_no_log_in_sdp_window.py` (~0.2 s). The second is non-negotiable on any `eeprom_28c.cpp` touch — it is the gate that fails closed (F-M).
- **Per wave merge:** `pio test -e native` **and** `pio test -e native_nodevtools` **and** `pio run` (all three envs) **and** the full host gate set from F-R. Phase 118 proved that re-running every gate at every wave is what produced zero host CI surprises.
- **Phase gate:** everything above, green, plus `119-MEASUREMENT.md` and `119-NONREGRESSION.md` complete with provenance, before `/gsd-verify-work`.

### Wave 0 Gaps

- [ ] `firestarter/test/native/avr/test_cmd_admission/` — the `is_memory_cmd()` truth table over **every** cmd value (LOCK-03). Needs `test_*.cpp`, a `host_stubs.cpp` including `_shared/host_stubs_common.inc`, an `avr/pgmspace.h` shim if any header pulls PROGMEM, **plus a `test_filter` line and a matching `-I` line in BOTH native envs**.
- [ ] `firestarter/platformio.ini` — `[env:native_nodevtools]` with its own full `test_filter` + `-I` list and explicit `-D MONITOR_SPEED=250000 -D HARDWARE_REVISION` (F-N). Verified working shape.
- [ ] `firestarter/.github/workflows/build.yml` — a `pio test -e native_nodevtools` step.
- [ ] `firestarter/test/native/avr/_shared/sdp_expected.h` — `SDP_FIXED_LOCK_{DIP28_28C256, DIP28_28C64, DIP24_2816, DIP32_28C512_EEPROM}` (4 goldens, dump-authored).
- [ ] `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` — **upgrade the `micros()` mock from a 2-slot parity alternator to a scripted queue** (F-O), then re-verify cases 11 and 12.
- [ ] `firestarter_app/tools/check_is_memory_cmd_no_ifdef.py` + `tests/test_check_is_memory_cmd_no_ifdef.py` + `tests/fixtures/planted_ifdef_in_predicate.h` — the D-04 gate, its paired pytest, and its planted-violation fixture.
- [ ] `firestarter_app/tools/check_no_log_in_sdp_window.py` — append the new emit anchor; repair `tests/test_check_no_log_in_sdp_window.py` and `tests/fixtures/planted_log_in_window.cpp` (F-M).
- [ ] **Decision required before Wave 1:** F-F option (a) (widen `build_src_filter` with `+<operation_utils.cpp>`, verifying all 16 suites for ArduinoFake aborts) or option (b) (a `static inline` helper in `operation_utils.h`). This determines whether LOCK-04's and DEVTEST-01's proofs are tests or prose. **Recommend (a).**
- [ ] `.planning/phases/119-…/119-MEASUREMENT.md` and `119-NONREGRESSION.md` — mirror `118-MEASUREMENT.md` §1/§6 and `118-NONREGRESSION.md` §4.

### Provable natively vs. requires Leonardo-class hardware

| Provable in CI (native / build / lint) | Requires real hardware — **flag, never rubber-stamp** |
|---|---|
| LOCK-01's exact emitted stream on all 4 pinouts | D-16's worst-case per-byte page-load interval (**3 boards**) |
| LOCK-01's `t_WC` call presence and the no-payload stream length | D-18's per-board flash figures cross-checked against a real `pio run` (build is CI-able; the *board identity* line is not) |
| LOCK-02's dispatch wiring (main set, init/end NULL) | The **lock's own** hardware duration — **unreachable until Phase 120's `dev sdp` CLI** (D-17) |
| LOCK-02's full ACK/frame shape — **only under F-F(a)** | `controller:` identity per port |
| LOCK-03's truth table, in both build configurations | — |
| LOCK-03's no-`#ifdef` textual gate + its planted violation | — |
| LOCK-04's refusal — **only under F-F(a)** | — |
| LOCK-04's "read/verify never NULL-main" invariant | — |
| LOCK-05's three-way identity, distinctness, and stream length | — |
| LOCK-06's flash figures (`pio run` is deterministic) | — |
| D-14's budget WARN firing **and** not firing | — |
| DEVTEST-01 firmware refusal — **only under F-F(a)** | — |
| The cross-family byte-identity sweep | — |
| The three-repo catalog byte-identity | — |

**⚠ Validation ceiling, unchanged.** No AT28C part is on the bench. Every number this phase measures is a measurement of **the MCU driving its own latches**, never evidence about AT28C silicon. `0x0D` stays `UNVERIFIED`; **zero** chips change `support_status`; the **84**-chip count is unchanged. Any sentence in `119-MEASUREMENT.md` readable as bench-validating `0x0D` crosses that line — `118-MEASUREMENT.md` §1 and §6 are the wording that already survived that review.

## Security Domain

`security_enforcement` is not disabled in `.planning/config.json`, so this section is included. This is embedded firmware with a local serial control plane and no network surface; most ASVS categories are structurally inapplicable, and the real risk model is **physical**: this phase adds the milestone's only new state-mutating operation, and that operation is *irreversibly* protective on some parts.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | Local USB serial only; no identity model. The physical-access boundary is the trust boundary. |
| V3 Session Management | no | Stateless per-command; `command_done()` resets `cmd := CMD_IDLE`, chip-disable, and zeroes CONTROL/LSB/MSB. |
| V4 Access Control | **yes** | **`is_memory_cmd()` IS the access-control gate for this phase** (LOCK-03) — it decides which commands may configure the hardware bus. Its correctness is a *safety* property, not a hygiene one: `configure_eprom` enables the 12 V VPP boost regulator, which is a hazard on a 5 V part. Enumerate explicitly, never ordinally; prove set-equality across build configurations. |
| V5 Input Validation | **yes** | `json_parser.c` + `jsmn` on the wire; CRC8-verified COBS frames decoded **before** any JSON byte is examined; `is_flag_set` on `uint32_t ctrl_flags`. **No wire change is needed or permitted in this phase** — an arbitrary `cmd` integer and a `uint32_t` flag already parse unchanged (verified in Phase 118). |
| V6 Cryptography | no | CRC8 is an integrity check, not a security control; no secrets, no crypto. |
| V7 Error Handling & Logging | **yes** | The `MSG_*` catalog with severity bands. **The specific control this phase adds is D-06/D-07: replacing a silent OK with an explicit refusal.** A generated catalog + drift gate is the anti-drift control. |
| V10 Malicious Code | **yes (supply chain)** | Zero new packages (see Package Legitimacy Audit). `messages.h`/`messages.py` are generated from one TOML with a CI `--check` drift gate — the anti-tamper control for the message surface. |
| V12 Files & Resources | **yes** | `data_buffer[DATA_BUFFER_SIZE]` bounds. `eeprom28c_write_execute`'s index invariant (`window_start <= i < data_size` by construction, never derived from a wire field) and `_process_incoming_data`'s `address + data_size > mem_size` → `MSG_ERR_OUT_OF_RANGE` guard. D-16's tracker must not introduce a new index. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---|---|---|
| **Phantom success — an operation reports OK having done nothing** | **Repudiation / Tampering** | **This phase's headline control (D-06/D-07).** `MSG_ERR_NOT_SUPPORTED` at the single NULL-`main` site. Precomputed blast radius in F-E. |
| **Fabricated state claim — reporting a protection state that cannot be read back** | **Repudiation** | D-12: OK means "the sequence was emitted", said in the **message text**, not encoded in a status code the host could misread. HOST-05 forbids a fabricated boolean; putting the honesty in firmware means Phase 120 never has to manufacture one. |
| **Dual-purpose command table — `AA-55-A0` locks OR prefixes a write** | **Tampering (destructive)** | D-10: the three-way byte-identity guard makes "the name is the only discriminator" a machine-checked fact, and a stream-length assertion makes the load-bearing *absence* (no trailing data write) observable. |
| **One-nibble slip turning SDP-disable into chip erase (`0x20` → `0x10`)** | **Tampering (destructive)** | Already mitigated: `test_fix05_terminal_byte_and_table_identity_guards` pins terminal bytes, array distinctness, and the one-nibble claim; a planted-mutation fixture proves the guard can fail. |
| **Ordinal admission guard admitting an unintended command into hardware configuration** | **Elevation of Privilege** | LOCK-03's explicit enumeration + the two-env truth table + the no-`#ifdef` source gate. Three independent oracles for one gate. |
| **Compile-configuration divergence — a release build behaving differently from a tested build** | **Tampering** | The `[env:native_nodevtools]` semantic proof (F-G: verified feasible, 112/112) plus the textual gate. This is precisely 999.15/gh#8's concern, partially discharged here. |
| **Unknown-protocol reaching a 12 V VPP path** | **Tampering (destructive)** | Pre-existing and preserved: `configure_not_implemented` is the terminal fail-closed exit for every unrecognised protocol including `0` (DISP-01/T-64-01). F-E confirms the new guard adds no double-error and does not disturb it. |
| **Irreversible protective action on an unrecoverable part** | **Denial of Service (physical)** | Out of scope here by ordering: `CMD_SDP_LOCK` is **unreachable from the shipped CLI** (D-17), so no bench byte in this phase can lock a part. The destructiveness confirm + `-y` + the SAFE-04 absent-chip hard-fail land in Phase 120 (HOST-01). **This is the strongest safety argument for firmware-before-host and should be stated as one.** |
| **Cross-repo gate hollowing via a firmware rename** | **Tampering (of controls)** | Every gate fails closed and names its own fix; anchor tuples are append-only by contract; every gate ships a planted-violation fixture. F-M is the concrete instance this phase must handle. |

## State of the Art

| Old approach | Current approach | When changed | Impact on this phase |
|---|---|---|---|
| Secondary `mem_type`/`type` dispatch axis | `handle->protocol` only; unrecognised → `configure_not_implemented` | v1.20 (Phases 105–107) | D-06 rejects a `protocol != 0x0D` check in `configure_memory` **because** v1.20 deliberately cleaned protocol-specific knowledge out of the dispatcher. Honour that. |
| `flash_execute_command(EEPROM_SDP_DISABLE)` via `flash_util_byte_flipping` | `eeprom28c_emit_command_sequence` on `handle->firestarter_set_data` (full remap, CONTROL rewrite per address change) | v1.22 Phase 117 (FIX-01) | The lock **must** use the new emitter. The old path inhibits `/WE` on 66 of 84 `0x0D` chips. |
| Inverted `(0x5555, 0x20)` read-back as the success check | `delay(t_WC)` + a bounded DQ6 toggle poll that draws **no conclusion** | v1.22 Phase 117 (FIX-02) | D-11 declines even this for the lock: 3 writes, `t_WC`, stop. |
| Conflated whole-byte completion-plus-verify poll | Two functions, one job each: DQ7-complement completion poll + per-byte read-back | v1.22 Phase 117 (FIX-06) | gh#11 is a **conflation** bug. D-16's wording must aim there, never at sampling rate. |
| A silent auto-unlock | Two unconditional `LOG_ID` INFO-band report lines + `FLAG_SKIP_SDP_UNLOCK 0x100` + a runtime t_BLC budget check | v1.22 Phase 118 | The lock's report pair copies this spelling exactly (bare `LOG_ID`, **not** `LOG_INFO_ID*`). |
| "The t_BLC check should never fire" | **Measured 572/600 µs — a 4.7 % margin** | v1.22 Phase 118 (F-118-01) | The lock gets its own check rather than inheriting an assumption; the page-load loop finally gets measured instead of cited. |
| Whole-file blob SHA of `_shared/` as the non-regression proof | Per-array byte-identity (forced by adding `SDP_FIXED_LOCK_*`) | **this phase** | Say so explicitly; 117/118's shorthand no longer applies to `sdp_expected.h`. |
| `check_no_log_in_sdp_window.py` scanning the span *between* two call sites in `write_init` | Brace-matching the **emitter body** and the **completion-poll body** | v1.22 Phase 118 (D-06) | F-M: D-14's helper threatens the surviving `write_init` rename tripwire. |

**Deprecated / outdated — do not target:**
- `include/primitives.h` and `src/proms/primitives.cpp` **do not exist**; the v1.16 Phase-89 primitive recompose sits on an unmerged branch. Any plan written against "the primitives layer" targets absent code (`.planning` memory `reference_v116_primitives_layer_never_merged.md`).
- Commit `0052c42` ("delete dead `FLASH_ENABLE_WRITE_PROTECTION` + redirect `EEPROM_SDP_DISABLE`") is **abandoned** — not an ancestor of `beta` nor of the v1.21 line. Its dedup never merged, so both tables are live. **This is exactly what LOCK-05 must keep live.**
- `eeprom28c_wait_for_write(handle, 0x5555, 0x20)` — deleted outright in Phase 117. Its regex survives in `_WAIT_ANCHOR_PATTERNS` only as an append-only revert tripwire.
- The legacy `type` JSON key — no longer parsed; unknown fields are silently skipped.
- Comparing firmware branches against `main` — `main` lags `beta` by ~224 commits and live branches look abandoned against it. **Compare against `beta`** (`.planning` memory `reference_firmware_branches_compare_vs_beta_not_main.md`).

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | The lock's FIXED-shape golden is `SDP_FIXED_DIP28_28C256[0..29]` with index 27 = `0xA0`, length 30, diverging from unlock and erase at **index 27** | F-I | LOW-MEDIUM. Derived arithmetically and cross-validated against the in-tree index-26 assertion on the shipped shape, but not dumped. **Mitigation: author the goldens empirically via `SDP_TRACE_DUMP` + running the built binary directly, per the standing rule.** A wrong index makes a negative case assert the wrong thing and stay green. |
| A2 | Widening `build_src_filter` with `+<operation_utils.cpp>` will link cleanly across all 16 suites | F-F option (a) | MEDIUM. Its externals are all present (`rurp_communication_*` from the linked `rurp_serial_utils.cpp`; `millis`/`delay` from ArduinoFake; `strncmp_P`/`PSTR` from the pgmspace shims), but **ArduinoFake aborts on unmocked virtuals** and only 4 suites currently mock `millis`/`delay`. **Mitigation: verify empirically as the first task of the plan that needs it; option (b) is the recorded fallback.** |
| A3 | The shared bracket helper is flash-neutral or negative | F-H | LOW. It de-duplicates 118's inline bracket, and 118's own bracket cost is part of the `+152 B`. Only affects the *estimate*, never the measured delta. |
| A4 | Six `default:` arms across the `configure_*` handlers would cost ~90–130 B | F-H | LOW. An estimate offered only to price a **rejected** option; nothing depends on it. |
| A5 | The report-line spelling for the lock's pair (bare `LOG_ID` on an INFO id) will not trip `_LOG_CALL_PATTERN` | F-M | LOW. Verified: the pattern is `\bLOG_[A-Z][A-Z0-9_]*\s*\(`, which **does** match `LOG_ID(` — but only inside the two scanned bodies. The report lines sit **outside** the emitter and poll bodies today, and D-12/D-14 keep them there. Confirm after the helper factoring: if the helper's body ever becomes a scanned window, its by-design `LOG_` calls become violations. |
| A6 | `MSG_ERR_NOT_SUPPORTED`'s zero-param shape is adequate for the generic refusal | F-D | LOW. A `cmd`-carrying variant would be more diagnosable but requires a new catalog id, which D-06 explicitly avoids. Revisit only if bench diagnosis proves painful. |

**Everything else in this document is `[VERIFIED]` against live source or measured in this session.** In particular: the guard structure and its `#ifdef`, the conditional `CMD_DEV_*` definitions, the pre-set generic mains, the phantom-success lines, the complete cmd × protocol matrix, the native `build_src_filter`, the gate anchor patterns and their fail-closed behaviour, the `micros()` parity mock, the free catalog ids, the flash figures, the no-DEV_TOOLS build outcome, and the existing `test_lock05_...` case.

## Open Questions (ALL 5 RESOLVED by the Phase 119 plan set, 2026-07-28)

> Every question below was dispositioned during planning. Each carries a **RESOLVED** line naming the plan/task that owns it. The *recommendation* text is preserved verbatim as the reasoning of record — read the RESOLVED line for what was actually decided.

1. **F-F option (a) vs (b) — is `operation_utils.cpp` linkable into all 16 native suites?**
   - Known: the TU's externals are all satisfiable; the risk is ArduinoFake aborting on unmocked `millis`/`delay` in the 12 suites that don't mock them.
   - Unclear: whether it links and runs clean without per-suite stub work.
   - **Recommendation: make this the first task of the plan that owns LOCK-04/DEVTEST-01.** It is a 5-minute experiment (`+<operation_utils.cpp>` → `pio test -e native`) that determines whether two requirements are proven by tests or by prose. Record the outcome either way. Do not defer it to a later wave — it changes the plan's shape.
   - **RESOLVED → `119-07-PLAN.md` Task 1.** Planned as a bounded spike-then-commit as the *first* task of the plan owning LOCK-04 / DEVTEST-01, with an explicit fallback to option (b) if (a) aborts any suite. No earlier wave's proof depends on the outcome.

2. **ROADMAP criterion 5's "header comment" vs D-09's byte-frozen `flash_utils.h`.**
   - Known: `flash_utils.h:42-53` has no such comment; FIX-04 asserts the file is byte-untouched; D-09 keeps it frozen; D-10 directs the rationale comment to `eeprom_28c.cpp`; `test_sdp_harness.cpp:291-296` already records the datasheet rationale.
   - Unclear: whether the operator reads criterion 5 as literally requiring a `flash_utils.h` edit.
   - **Recommendation: satisfy the intent in `eeprom_28c.cpp` + cite the existing test comment; record the deviation in CONTEXT-correction style alongside D-05 and D-15; do not edit `flash_utils.h` and do not edit `REQUIREMENTS.md`.** Flag it for the operator in the plan so it is a decision, not a discovery. (F-K)
   - **RESOLVED → `119-04`, `119-06`, `119-09`.** Recommendation taken: `flash_utils.h` stays byte-frozen (D-09), the rationale comment lands in `eeprom_28c.cpp`, and LOCK-05's third identity leg + distinctness are asserted in `119-06`. The criterion-5 deviation is recorded as mechanism-corrected/intent-satisfied so a verifier does not read it as failed.

3. **`CMD_IDLE`'s behaviour delta — accept or handle?**
   - Known: `{"cmd":0}` today produces `0xBB` + `MSG_ERR_SETUP`; after `is_memory_cmd()` it produces silence.
   - Unclear: whether anything sends an explicit cmd 0 (the host's own `CMD_IDLE` is a firmware-internal state, not a command it emits).
   - **Recommendation: accept it and record it in the SUMMARY beside the cmd 7/8 change, or add an explicit refusal arm if the flash is free. Either way, name it — D-01 currently names only 7/8.** (F-B2)
   - **RESOLVED → `119-02` and `119-09`.** Accepted, not handled: an explicit refusal arm was declined on flash grounds. `CMD_IDLE` is carried as the **third** behaviour delta (beside cmd 7 and cmd 8) in both plans, since D-01 names only 7/8.

4. **Does the page-load report line perturb any existing frame-count assertion?**
   - Known: `test_case12_...` asserts *exactly two* report frames but drives `drive_write_init` only, so `write_execute`'s new line is out of its scope today.
   - Unclear: whether `test_val_eeprom28c`'s write-path cases (added by 117-03) count frames.
   - **Recommendation: enumerate every frame-count assertion in the native suite before adding D-16's line, and re-run all 16 suites immediately after.** The `micros()` mock upgrade (F-O) touches the same file, so bundle them.
   - **RESOLVED → `119-05` Task 1 (mock upgrade + explicit re-verification of cases 11 and 12 by name) and `119-08` (the D-16 report line, with the full-suite re-run in its acceptance criteria).**

5. **Should the new D-04 gate scan `firestarter.h` or a dedicated file?**
   - Known: `firestarter.h` is scanned by `test_revision_constants_parity.py` only via hardcoded literals, so a new structural scan of the same file is not a conflict.
   - Unclear: whether a C++-header brace/AST scan of `firestarter.h` is more brittle than scanning a small dedicated TU.
   - **Recommendation: scan `firestarter.h` with a brace-matched extraction of the predicate body (the `check_no_log_in_sdp_window.py` idiom, not a bare grep) plus a fail-closed `FIRESTARTER_*_SRC` override for the planted fixture.** Keeping the predicate in `firestarter.h` is worth more (F-F consequence 1) than the gate's marginal simplicity.
   - **RESOLVED → `119-03`.** Recommendation taken: `check_is_memory_cmd_no_ifdef.py` uses the brace-matched extraction idiom with the fail-closed `FIRESTARTER_*_SRC` seam, shipped with `tests/test_check_is_memory_cmd_no_ifdef.py` and a planted-violation fixture proving the gate can fail.

## Sources

### Primary (HIGH confidence — live source read this session, at firmware `1880054` / host `d3f9128`)

- `firestarter/src/firestarter.cpp` — `parse_json` :52-108 (guard :76-95), `command_done` :147-156, `loop` :158-253
- `firestarter/include/firestarter.h` — `CMD_*` :33-49, `FLAG_*` :57-77, `is_flag_set` :79, handle struct :86-115
- `firestarter/src/operation_utils.cpp` — `op_execute_simple_operation` :58-60, `op_execute_stateful_operation` :62-84, `op_execute_function` :97-102, `op_wait_for_ack` :104-117, `op_get_message` :128-178, `set_operation_to_done` :180-184, `_execute_operation_house_keeping` :195-217, `_execute_operation_house_keeping_func` :230-260, `_single_step_operation_callback` :270-297, `_execute_operation` :304-312, `_check_response` :322+
- `firestarter/include/operation_utils.h` — state macros :24-27, `static inline` precedent :41-49, function declarations :74-124
- `firestarter/src/eprom_operations.cpp` — entry points :19-56, `_process_incoming_data` :57-107, `_process_outgoing_data` :108+
- `firestarter/src/proms/memory.cpp` — `configure_memory` :42-114 (pre-set mains :48-58, protocol chain :70-113)
- `firestarter/src/proms/eeprom_28c.cpp` — read whole (556 lines)
- `firestarter/src/proms/{eprom,sram,flash_intel,flash_nor_unlock,flash_5v_page,not_implemented}.cpp` — all six `configure_*` bodies
- `firestarter/include/flash_utils.h` :20-69; `firestarter/include/eeprom_28c.h`
- `firestarter/src/hardware_operations.cpp`, `firestarter/src/dev_tools.cpp` — confirmed no op-layer use
- `firestarter/platformio.ini` — read whole
- `firestarter/.github/workflows/build.yml` :1-115
- `firestarter/test/native/avr/_shared/sdp_expected.h` — read whole
- `firestarter/test/native/avr/_shared/host_stubs_common.inc` — read whole
- `firestarter/test/native/avr/test_sdp_harness/test_sdp_harness.cpp` :1-400
- `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` :130-800
- `firestarter_app/tools/check_no_log_in_sdp_window.py` — read whole
- `firestarter_app/tools/check_devtest_orchestrator.py` :300-345
- `firestarter_app/tests/test_sdp_table_parity.py` :1-175
- `firestarter_app/tests/test_revision_constants_parity.py` :75-150
- `firestarter_app/tests/test_dispatch_mirror.py` :190-240
- `firestarter_app/firestarter/eprom_operations.py` :1650-1690
- `tools/catalog/messages.toml` (meta, canonical); `tools/catalog/sync_to_subrepos.sh`
- `firestarter/CLAUDE.md` — dispatch-order source-of-truth table, `[env:native]` layout
- `/workspaces/CLAUDE.md` — constants/flag-bit duplication rule

### Primary (HIGH confidence — measurements executed this session)

- `pio run -e uno -e uno328pb -e leonardo` → the three flash/RAM figures in F-H
- `pio test -e native` → 112/112, 16/16 suites (baseline)
- `pio test -e native_nodevtools` (temporary env, removed; `platformio.ini` restored byte-clean) → **112/112** — F-G
- `pio run -e leonardo_nodevtools` (temporary env, removed) → 24388/28672 — F-G
- `python3 tools/check_no_log_in_sdp_window.py` → PASS, exit 0
- `python3 tools/check_dispatch.py` → exit 0
- `python3 -m pytest tests/test_sdp_table_parity.py tests/test_check_no_log_in_sdp_window.py tests/test_sdp_bus_config_drift.py tests/test_revision_constants_parity.py -q` → 21 passed
- `ls /dev/ttyACM* /dev/ttyUSB*` → all three boards attached
- `git branch --show-current` in both sub-repos → `v1.22-at28c-software-data-protection-lifecycle` (CONTEXT's setup precondition **verified**)
- `grep` sweeps: `CMD_DEV_*` (5 sites), `FLASH_ENABLE_WRITE*` callers, `op_*` from `proms/`, `DEV_TOOLS` in `test/` (0 hits), host files referencing firmware paths (9 files)

### Secondary (HIGH/MEDIUM — project artifacts, adjudicated or measured by prior phases)

- `.planning/phases/119-…/119-CONTEXT.md` — the authority; D-01..D-20
- `.planning/research/SUMMARY.md` — CONFLICT 1 (the lock body, 3-document agreement), the truncation arithmetic, Critical Pitfalls, the validation-ceiling permitted/forbidden claims
- `.planning/REQUIREMENTS.md` — LOCK-01..06 verbatim, locked decisions, out-of-scope table, validation ceiling
- `.planning/ROADMAP.md` — Phase 119 criteria; **Phase 121 criterion 2** (the DEVTEST-01 firmware half D-08 moves here)
- `.planning/PROJECT.md` — THIRD (66 of 84), FOURTH (`+204 B`, item 4's gate lesson, item 5's vacuous path), FIFTH CORRECTION (F-118-01's 572/600 µs, the page-load directive at LOCK-06, `+152 B`, item 5's "keep doing this for 119–122")
- `.planning/phases/118-…/118-NONREGRESSION.md` §4 — the `f8d10a5 → 1880054` flash provenance this session's figures match exactly
- `.planning/phases/118-…/118-MEASUREMENT.md` — the §1/§6 template `119-MEASUREMENT.md` must follow
- `.planning/todos/prove-pio-dev-flag-fails-closed.md` — item 4, **answered by F-G**

### Tertiary (MEDIUM — project memory, treat as prompts to verify, not as facts)

`.planning` memory: `reference_firmware_messages_h_is_codegen_generated`, `reference_firmware_renames_break_host_source_scanning_gates`, `reference_native_stub_misses_register_elision`, `reference_codegen_ruff_clean_emitter`, `reference_devcontainer_py312_masks_ci_py39`, `reference_audit_coverage_matrix_golden_stale`, `reference_characterization_no_programmer_tests_fail_with_live_board`, `reference_executors_prematurely_mark_requirements_complete`, `reference_write_b_skips_erase`, `reference_v116_primitives_layer_never_merged`, `reference_firmware_branches_compare_vs_beta_not_main`, `feedback_verify_port_identity_each_task`, `feedback_chip_out_before_sideload`, `project_uno328pb_bench_instability_27_04`, `project_uno328pb_correction`, `project_uno328pb_vpp_recal_and_program_brownout`, `project_devtools_gating_channel_split`

### Not used (recorded so a later reader does not assume it was consulted)

`.planning/graphs/graph.json` exists but is **650 h / 329 commits stale** (`built_at_commit f4150b8`, current `4073619`). Given that every question this phase asks is about code that Phases 116–118 changed *after* that build, the graph would have been actively misleading. **Skipped deliberately; all structural claims come from direct source reads instead.** Consider `/gsd-graphify` before Phase 120.

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| Admission guard, command enumeration, `#ifdef` structure | **HIGH** | Read live; the `CMD_DEV_*` conditional-definition finding cross-checked by a full-tree grep (5 sites) |
| LOCK-04's disproof and the corrected admission point | **HIGH** | Both switch bodies and both call chains read live; the op layer's caller set closed by grep |
| The cmd × protocol NULL-`main` matrix | **HIGH** | All six `configure_*` bodies read in full; `configure_sram`'s empty body is the surprise and it is verbatim |
| Flash figures and headroom | **HIGH** | Measured this session; matches `118-NONREGRESSION.md` §4 to the byte |
| No-DEV_TOOLS build viability | **HIGH** | Executed: 112/112 native, and a successful release-config Leonardo link |
| Datasheet lock body | **HIGH** | 3-document / 3-stream adjudicated agreement in `research/SUMMARY.md` CONFLICT 1 |
| Golden-trace mechanism and the "distinct" assertion form | **HIGH** | Comparator and three in-tree negative cases read live |
| The predicted lock golden's exact indices | **MEDIUM** | Derived arithmetically; method validated against the in-tree index-26 assertion; **must be dump-confirmed** (A1) |
| `build_src_filter` consequences for `is_memory_cmd()` | **HIGH** | Filter read live; absence of `op_*` stubs confirmed by grep |
| `operation_utils.cpp` linking cleanly into all 16 suites | **MEDIUM** | Dependencies analysed and all satisfiable; ArduinoFake abort risk unmeasured (A2) |
| Host gate breakage analysis (F-M) | **HIGH** | The resolver's fail-closed logic and both anchor tuples read live; current PASS baseline captured |
| Flash cost estimates for individual additions | **LOW–MEDIUM** | Estimates only, offered to price options (A3, A4). **LOCK-06 must be settled by measurement, per D-15.** |

**Research date:** 2026-07-28
**Valid until:** ~2026-08-11 for the in-tree code claims (invalidated by any commit to `eeprom_28c.cpp`, `operation_utils.cpp`, `firestarter.cpp`, `platformio.ini`, or any of the nine host gates). **The flash figures are invalidated by the first commit of this phase** — that is by design; they are the base of LOCK-06's arithmetic. The datasheet claims do not expire.
