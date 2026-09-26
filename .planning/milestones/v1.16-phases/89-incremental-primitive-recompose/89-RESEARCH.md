# Phase 89: Incremental Primitive Recompose - Research

**Researched:** 2026-06-26
**Domain:** Embedded C++ refactor-under-test (AVR firmware primitive extraction), guarded by byte-exact golden-trace + dispatch-mirror + host-gate oracle
**Confidence:** HIGH (all call sites, gates, and the flash baseline verified against live source + a live `pio run`/`pio test` this session)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01 — Flash gate:** Per-step `≤ +16B` tolerance, phase-cumulative net-decrease. Each extraction step may rise at most +16 B vs the prior step (reuse Phase 87-04's `DELTA≤16` failable gate); the phase as a whole MUST end below the 25654 B Phase-88 baseline. The achieved final flash % is reported at phase close (PRIM-06).
- **D-02 — Abort policy:** Abort-that-primitive-and-continue. If one primitive can't meet its gate (flash, trace reconcile, or `check_dispatch`/`diff_db`), skip it, commit the clean ones, and document the deferred primitive with a FUT/CR-style reason, leaving its call sites in pre-extraction duplicated form. Each extraction is independently reversible.
- **D-03 — Module home:** Dedicated primitives module. Cross-family P4 `chip_id_report`, P3 `vpp_check_window`, P5 `poll_readback` live in NEW `firestarter/src/proms/primitives.cpp` + `firestarter/include/primitives.h`. P7 SDP const-tables stay flash-local in `include/flash_utils.h`. *(Planner discretion on exact symbol names / signatures; module location is fixed.)*
- **D-04 — Re-bless threshold:** Zero-diff is the hard goal; re-bless only on review. Aim for byte-identical golden traces at every step. Re-bless the expected array ONLY when the diff is inspected, confirmed behaviorally-equivalent, and documented in the commit message (Phase-88 D-02 audit checkpoint). A trace failure is "inspect this diff"; a re-bless is a deliberate, human-gated event.
- **D-05 — Frozen gates:** `check_dispatch.py` exits 0 violations and `diff_db.py` is empty against the Phase-86-repinned 746-chip baseline at EVERY extraction step. No DB record change, no dispatch-order change (SAFE-03).
- **D-06 — Protocol keying:** Every extracted primitive keys behavior on `handle->protocol`, never `electrical.type`; the `novpp_in_eprom` / `eeprom28c_in_eprom` (WARNING-5) structural guards are preserved (SAFE-01).
- **D-07 — Invariant oracle:** All NAME-03 INV-01..09 invariants survive each step under the native register-level tests; the byte-exact golden traces (Phase 88 D-01) are the SAFE-02 oracle that each P7/P4/P3/P5 step reruns `pio test -e native` against.
- **D-08 — Safety posture:** Over-voltage stays blocked at the firmware VPP check; `chip_resolver.resolve_chip` host guard never bypassed; 2516 stays `UNVERIFIED` (SAFE-04).
- **D-09 — No lockstep + order:** Firmware-first, NO dual-repo lockstep — wire/constant values unchanged; no `firestarter_app` change beyond rerunning the existing gates (SAFE-06). Extraction order is **P7 → P4 → P3 → P5** (biggest-saving-first, ROADMAP-fixed).

### Claude's Discretion

- Exact primitive symbol names / signatures (module location fixed by D-03).
- Commit granularity within the one-atomic-commit-per-primitive pattern.

### Deferred Ideas (OUT OF SCOPE)

- Per-protocol bench validation + `PROTOCOL-LEDGER.{md,json}` — Phase 90.
- 0x34 X88C64 programming handler — PCB-blocked (FUT-01); not in v1.16 scope.
- Any single primitive that can't meet its gate — deferred per D-02 with a documented reason (FUT/CR row).
- Any DB record change, dispatch-order change, wire/constant change, or golden-trace harness change.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PRIM-02 | P7 SDP/const-table dedup, behavior unchanged | §P7 below — the duplicate tables are byte-identical to existing ones (verified); dedup is a delete + redirect-reference, traced by `test_val_eeprom28c` + `test_val_flash4`/`flash3` golden write traces. |
| PRIM-03 | P4 `chip_id_report` primitive, split from read mechanism | §P4 below — 4 call sites; report tail (compare + `_b[4]` pack + FORCE downgrade) is **already byte-identical** across all 4; read mechanism stays handler-local. |
| PRIM-04 | P3 `vpp_check_window` primitive, protocol-keyed, regulator-routing parameterized | §P3 below — `eprom_check_vpp` and `flash_intel_check_vpp` share the HIGH/LOW window-compare + `_b[8]` pack + FORCE downgrade verbatim; regulator routing + the REV0 guard + the trailing regulator-clear DIVERGE and stay handler-local. |
| PRIM-05 | P5 `poll_readback` primitive, outer algorithms intact | §P5 below — 3 sites have STRUCTURALLY DIFFERENT poll shapes; the genuinely-shared kernel is narrow. Highest reconcile risk after P3. |
| PRIM-06 | Leonardo flash measured each step, net-non-increase, final % reported | §Flash Gate below — exact Phase 87-04 recipe: `.flash-baseline-87.txt`=25654, `pio run -e leonardo`, parse "Flash:…used N bytes", per-step `≤+16`, phase end `<25654`. |
| SAFE-01 | Protocol-keyed; WARNING-5 structural guards preserved | §Landmines — `using_p1_as_vpp`, the `protocol==0x0B \|\| FLAG_VPE_AS_VPP` branch, and host `novpp`/`eeprom28c_in_eprom` checks must survive. |
| SAFE-02 | NAME-03 invariants survive each step under register-level tests | §Oracle — INV-01..09 greppability (≥3 files) + golden traces; rerun full `pio test -e native` per step. |
| SAFE-03 | `check_dispatch.py` 0 violations + `diff_db.py` empty each step | §Host Gates — both reused unchanged; no DB/dispatch change in this phase. |
</phase_requirements>

## Summary

This is a **refactor-under-test** phase, not a feature. Four shared primitives are extracted from the duplicated `proms/` handlers, biggest-saver-first (P7 → P4 → P3 → P5), one atomic commit per primitive, each gated by the same green oracle Phase 88 built: byte-exact golden register traces (`pio test -e native`), the dispatch-mirror suite, the host `check_dispatch.py` / `diff_db.py` frozen-world gates, and a failable Leonardo flash-delta gate. Nothing new is built — the phase **consumes** the Phase-88 harness verbatim and adds one new firmware translation unit (`primitives.cpp` + `primitives.h`).

I read every named call site in live source and verified the line numbers in CONTEXT.md (a few have drifted by a handful of lines — corrected in the per-primitive sections). The key finding is that **the four primitives differ enormously in extraction difficulty**, and the difficulty does NOT track the P7→P4→P3→P5 order's flash savings:

- **P7 (warm-up):** trivial and safe. The duplicate tables are *byte-for-byte identical* to tables that already exist (`FLASH_ENABLE_WRITE_PROTECTION` == `FLASH_ENABLE_WRITE`; `EEPROM_SDP_DISABLE` == `FLASH_DISABLE_WRITE_PROTECTION`). Dedup = delete the duplicate + redirect the one reference. Zero behavioral risk.
- **P4 (clean win):** the report-tail logic (`if (chip_id != handle->chip_id) { pack _b[4]; FORCE→WARN else ERROR }`) is *already byte-identical* in all four call sites, and `flash_utils.cpp` already proves the pattern (`flash_util_check_chip_id_execute`). The shared primitive is essentially that function, generalized.
- **P3 (highest risk — most likely D-02 deferral):** the window-compare body is shared verbatim between `eprom_check_vpp` and `flash_intel_check_vpp`, BUT the two functions diverge on three axes that MUST stay handler-local: (1) regulator routing (eprom toggles the regulator itself + clears it at the end; flash_intel asserts upstream in `write_init` and never clears), (2) the REV0 early-return guard, (3) the trailing `set_control_register(... , 0)` clear. P3 sits one line above the over-voltage check region (D-08) and is protocol-keyed (D-06).
- **P5 (subtle — second-highest risk):** the three call sites are *not* the same shape. `eeprom28c_wait_for_write` and `flash4_wait_for_page_write` poll a single address until it matches `expected` (with different iteration counts: 2000 vs 1024, different timeout error frames). `verify_and_update_mask` (eprom) is a *whole-buffer* compare that writes a mismatch bitmask and returns a count — structurally different. The genuinely-shared kernel ("read address, compare to expected byte") is very small; over-sharing here risks a trace diff.

**Primary recommendation:** Ship P7 and P4 as clean wins (they front-load the flash headroom and are byte-equivalent). Treat P3 and P5 as the candidates for D-02 deferral if their golden traces won't reconcile to zero-diff — extract only the truly-identical inner body, keep every divergent guard/loop handler-local, and bless nothing. The flash gate is generous enough (+16B/step) that a primitive's first call-site overhead won't trip it; the binding constraint per step is the byte-exact trace, not flash.

## Architectural Responsibility Map

This phase is single-tier (Arduino firmware, `src/proms/`). The "tiers" here are the firmware module boundaries the primitives cross.

| Capability | Primary Tier (owner) | Secondary Tier | Rationale |
|------------|----------------------|----------------|-----------|
| SDP / const-table bus sequences (P7) | `include/flash_utils.h` (data) + `flash_utils.cpp` (`flash_util_byte_flipping`) | — | Flash-namespaced DATA, called via the `flash_execute_command` macro; D-03 keeps it flash-local (not cross-family code). |
| Chip-ID compare/report (P4) | NEW `proms/primitives.cpp` | per-handler read mechanism stays in each handler | Report tail is family-agnostic; the *read* (A9-12V vs command-register 0x90 vs AMD unlock) is protocol-specific. |
| VPP window check (P3) | NEW `proms/primitives.cpp` | regulator routing stays in `eprom.cpp` / `flash_intel.cpp` | D-06: keyed on `handle->protocol`; routing + REV0 guard + clear are per-protocol and MUST NOT move. |
| Poll/readback verify (P5) | NEW `proms/primitives.cpp` | outer retry/page/erase loops stay in each handler | Inner "read addr, compare expected" is shared; outer algorithm (bitmask vs single-addr, retry counts) is handler-specific. |
| Top-level dispatch | `proms/memory.cpp::configure_memory` | host `check_dispatch.py::dispatch()` mirror | FROZEN — no change this phase (D-05); both the native `test_dispatch` order and the host mirror must stay byte-identical. |

## Standard Stack

No new dependencies (SAFE-05). The phase reuses the existing toolchain exclusively.

### Core (existing, reused)
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| PlatformIO Core | 6.1.19 [VERIFIED: `pio --version` this session] | Build (`pio run -e leonardo`) + native test (`pio test -e native`) | Project build system (firestarter/CLAUDE.md). |
| Unity + ArduinoFake (`fakeit`) | bundled via `[env:native]` | Host-side register-trace unit tests | Already the golden-trace harness (Phase 88). |
| `golden_trace.h` | Phase 88 | `assert_trace_eq()` byte-exact compare + `GOLDEN_BLESS` print | The D-01 oracle; reused verbatim. |
| `check_dispatch.py` | host tool | 746-chip dispatch + BLOCKER-2 VPP-safety gate | D-05 frozen-world gate. |
| `diff_db.py` | host tool | per-chip diff vs `chip_database.baseline.json` (746) | D-05 frozen-world gate. |

**Installation:** none. `pio` is on PATH at `/usr/local/bin/pio`.

**Version verification:** No packages installed by this phase — Package Legitimacy Audit is N/A (firmware-only refactor, SAFE-05 forbids new deps).

## Package Legitimacy Audit

**Not applicable.** This phase installs no external packages (SAFE-05: "No new third-party dependency is introduced"). The only new artifacts are `firestarter/src/proms/primitives.cpp` and `firestarter/include/primitives.h`, both first-party C++ source.

## Architecture Patterns

### System Architecture Diagram — the per-step refactor-under-test loop

```
                         ┌─────────────────────────────────────────┐
   start each primitive  │  1. MEASURE pre-flash                    │
   (P7 → P4 → P3 → P5)   │     pio run -e leonardo → parse "Flash:" │
                         └───────────────────┬─────────────────────┘
                                             │ pre_bytes
                                             ▼
        ┌────────────────────────────────────────────────────────────┐
        │  2. EXTRACT (one atomic commit)                              │
        │     P7: delete dup table in flash_utils.h, redirect ref      │
        │     P4/P3/P5: move shared body → primitives.{cpp,h},          │
        │               replace call-site body with a call             │
        └───────────────────────────┬──────────────────────────────────┘
                                     ▼
   ┌───────────────────────────────────────────────────────────────────────┐
   │  3. GATE (all must pass before the commit is kept)                       │
   │     a. pio test -e native          → ALL suites green (byte-exact trace) │
   │        ── on diff: INSPECT (D-04). zero-diff is the goal.                │
   │        ── re-bless ONLY if reviewed benign-reorder + documented in msg.  │
   │     b. pio run -e leonardo          → post_bytes; assert (post-pre)≤+16   │
   │     c. cd firestarter_app && python tools/check_dispatch.py  → exit 0    │
   │     d. cd firestarter_app && python tools/diff_db.py          → exit 0    │
   │     e. grep -rn INV-NN (×9)         → each still hits ≥3 files (SAFE-02)  │
   └───────────────────────────────┬───────────────────────────────────────┘
                                    │
                  ┌─────────────────┴──────────────────┐
              all pass                              any fail
                  │                                     │
                  ▼                                     ▼
        commit (atomic, this primitive)      D-02: revert this primitive only,
        record delta in step ledger          document FUT/CR reason, CONTINUE
                  │                           to the next primitive
                  └─────────────────┬──────────────────┘
                                    ▼
                        next primitive in P7→P4→P3→P5
                                    │
                                    ▼  (after all four attempted)
                  phase close: assert final_bytes < 25654 (D-01 net-decrease)
                  report achieved flash % (PRIM-06)
```

The diagram's data flow IS the validation strategy — there is no separate "test" phase; every commit boundary is a gate.

### Recommended Project Structure (delta only)

```
firestarter/
├── include/
│   ├── flash_utils.h        # P7 target: delete dup tables here (stays flash-local, D-03)
│   └── primitives.h         # NEW (D-03): declares chip_id_report / vpp_check_window / poll_readback
├── src/proms/
│   ├── primitives.cpp       # NEW (D-03): the P4/P3/P5 shared bodies
│   ├── eprom.cpp            # P3 (eprom_check_vpp), P4 (eprom_internal_check_chip_id), P5 (verify_and_update_mask)
│   ├── eeprom_28c.cpp       # P7 (EEPROM_SDP_DISABLE), P4 (eeprom28c_check_chip_id), P5 (eeprom28c_wait_for_write)
│   ├── flash_intel.cpp      # P3 (flash_intel_check_vpp), P4 (flash_intel_check_chip_id)
│   ├── flash_type_4.cpp     # P7 (FLASH_ENABLE_WRITE site), P4 (delegates to flash_util_*), P5 (flash4_wait_for_page_write)
│   ├── flash_type_3.cpp     # P7 (FLASH_ENABLE_WRITE site); NO P4 site (Phase 88 D-03 — confirmed: no golden chip-id trace)
│   └── flash_utils.{h,cpp}  # already houses the shared flash chip-id (flash_util_check_chip_id_execute) — P4 precedent
```

### Pattern 1: New TU compiles for both `native` and AVR with no platformio.ini change
**What:** Drop `primitives.cpp` under `src/proms/`; the `[env:native]` `src_filter = +<proms/>` and the AVR envs both pick up everything in `src/proms/` automatically.
**When to use:** Always — this is how every existing proms handler builds.
**Evidence:** `firestarter/CLAUDE.md` §"Reuse pattern for future native tests": *"The `[env:native]` configuration in `platformio.ini` does not need changes for new suites."* The handler TUs are compiled by `src_filter = +<proms/>` (platformio.ini native env). [VERIFIED: read platformio.ini + CLAUDE.md]
**Header convention (match existing `flash_utils.h`):**
```cpp
// Source: firestarter/include/flash_utils.h (existing convention)
#ifndef __PRIMITIVES_H__
#define __PRIMITIVES_H__
#ifdef __cplusplus
extern "C" {
#endif
#include "firestarter.h"      // firestarter_handle_t, rurp_register_t, flags
// ... declarations ...
#ifdef __cplusplus
}
#endif
#endif // __PRIMITIVES_H__
```
Note: `flash_utils.h` uses `extern "C"` wrapping AND **defines** its const tables in the header (an ODR quirk that works only because each table is `const` with internal linkage per-TU). `primitives.cpp` should put *functions* in the .cpp (external linkage) and only *declarations* in the .h — do NOT define functions in the header.

### Pattern 2: P4 shared report tail (the proven precedent already exists)
**What:** `flash_utils.cpp::flash_util_check_chip_id_execute` is *already* the exact compare+report+FORCE-downgrade primitive, used by flash3 and flash4. P4 generalizes this to also serve eprom + eeprom28c + flash_intel.
**Source:** `flash_utils.cpp:110-126` [VERIFIED: read source]
```cpp
// The report tail — IDENTICAL in eprom.cpp:356-369, eeprom_28c.cpp:100-115,
// flash_intel.cpp:218-231, flash_utils.cpp:112-125 (verified byte-for-byte).
if (chip_id != handle->chip_id) {
    uint8_t _b[4];
    _b[0] = (uint8_t)((chip_id >> 8) & 0xFF);
    _b[1] = (uint8_t)(chip_id & 0xFF);
    _b[2] = (uint8_t)((handle->chip_id >> 8) & 0xFF);
    _b[3] = (uint8_t)(handle->chip_id & 0xFF);
    if (is_flag_set(FLAG_FORCE)) {
        LOG_WARN_ID_BYTES(MSG_WARN_CHIP_ID_MISMATCH, _b, 4);
        handle->response_code = RESPONSE_CODE_WARNING;
    } else {
        LOG_ERROR_ID_BYTES(MSG_ERR_CHIP_ID_MISMATCH, _b, 4);
        handle->response_code = RESPONSE_CODE_ERROR;
    }
}
```
**Suggested signature (discretion, D-03):** `void chip_id_report(firestarter_handle_t* handle, uint16_t read_id);` — the caller does the protocol-specific read, then passes the read id in. `eprom_internal_check_chip_id` also takes an `error_code` param that lets `eprom_generic_init` force WARNING; preserve that (pass a `bool force_warn` or reuse `FLAG_FORCE` — note `eprom_generic_init` passes `is_flag_set(FLAG_FORCE) ? WARNING : ERROR`, which is exactly what the shared tail already computes, so the `error_code` param may be redundant — **verify the trace** before collapsing it).

### Anti-Patterns to Avoid
- **Sharing P5's whole loop.** `verify_and_update_mask` is a buffer-wide bitmask updater; the other two are single-address polls with different iteration caps. A "unified poll" would change the trace. Share only the inner compare, or skip eprom's site (the 2/3 wait-for-write sites are the real duplication).
- **Moving the regulator clear into P3.** `eprom_check_vpp` ends with `set_control_register(REGULATOR|VPE_DROP, 0)`; `flash_intel_check_vpp` deliberately does NOT clear (caller holds VPP through the write). Moving the clear into the shared primitive would either strand 12V on flash_intel or fail eprom's trace.
- **Re-blessing to make a diff go away (D-04).** A trace diff is a signal to inspect, not to regenerate.
- **Touching the host repo.** `git -C firestarter_app diff --quiet` is the SAFE-06 machine check; the only host activity is running the two gate scripts (read-only).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Flash-delta gate | a new measurement script | Phase 87-04's exact recipe (`.flash-baseline-87.txt` + parse `pio run -e leonardo` "Flash:" line + `≤16` compare) | Proven, already-pinned baseline (25654); reinventing risks parsing the wrong number. |
| Golden trace compare | a custom diff | `assert_trace_eq()` in `_shared/golden_trace.h` + `GOLDEN_BLESS` | The D-01 oracle; the suites already call it. |
| Dispatch-order guard | a new check | the `test_dispatch` native suite + host `check_dispatch.py::dispatch()` mirror | Both already exist and are FROZEN (D-05). |
| DB drift guard | manual JSON inspection | `diff_db.py` (exit 0 = empty) | Composite-keyed, baseline-pinned; the SAFE-03 gate. |
| Chip-id report tail (P4) | a fresh compare/pack | generalize `flash_util_check_chip_id_execute` | It IS the primitive already, proven across flash3/flash4. |

**Key insight:** Every gate this phase needs already exists and is green at HEAD. The work is *extraction + rerun*, never *new infrastructure*. The single point of original authorship is `primitives.{cpp,h}`.

## Runtime State Inventory

> This is a firmware source refactor with NO data/config/wire change (D-09). The "runtime state" that a naive grep refactor would miss is the **build artifact + gate-baseline** state, enumerated below.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data (DB) | `firestarter_app/firestarter/data/chip_database.json` (746 chips) — frozen | **None.** `diff_db.py` MUST stay empty; this phase changes no DB record (D-05). Verified: SAFE-03 marks 88–89 as "diff_db empty against re-pinned baseline." |
| Gate baselines | `firestarter_app/tools/baseline/chip_database.baseline.json` (746) + `dispatch_baseline.json` — Phase-86-repinned | **None — do not re-pin.** Re-pinning happened in Phase 86 (VAR-03). Phases 87/88/89 run against the frozen baseline. |
| Flash baseline file | `firestarter/.flash-baseline-87.txt` = `25654` [VERIFIED: read file + `pio run` this session matches exactly] | **Reuse as-is** for the per-step `≤+16` gate. Optionally write a fresh per-phase baseline file, but the value is the same 25654. |
| Wire/constant values | `rurp_pinout.h` CTRL_* bits, `firestarter.h` FLAG_* bits, `messages.h` IDs | **None changed** (SAFE-06/D-09). No `messages.py` regen, no codegen. |
| Build artifacts | `.pio/build/{leonardo,native}/` | Rebuilt by each `pio run`/`pio test`; no stale-artifact risk (PlatformIO tracks source deps). Adding `primitives.cpp` is picked up automatically by `src_filter`. |
| Host repo | `firestarter_app/` source/tools/tests | **Frozen** (SAFE-06). Only run `check_dispatch.py`/`diff_db.py` (read-only). Verify with `git -C firestarter_app diff --quiet` at phase close. |

**Live-service config / OS-registered state / secrets:** None — this is offline firmware source. Verified by domain (no daemon, no scheduler, no datastore keyed on a renamed symbol; primitive symbol names are new internal-linkage functions, not external contracts).

## Common Pitfalls

### Pitfall 1: The duplicate tables are byte-identical — dedup is delete-not-merge (P7)
**What goes wrong:** Treating P7 as a "merge two slightly-different tables" task.
**Reality (verified):** In `flash_utils.h`, `FLASH_ENABLE_WRITE_PROTECTION` (lines 48-52) is **byte-for-byte identical** to `FLASH_ENABLE_WRITE` (lines 42-46): both are `{{0x5555,0xAA},{0x2AAA,0x55},{0x5555,0xA0}}`. And `eeprom_28c.cpp`'s `EEPROM_SDP_DISABLE` (lines 47-54) is **identical** to `flash_utils.h`'s `FLASH_DISABLE_WRITE_PROTECTION` (lines 53-60): both are the 6-write `…{0x5555,0x80}…{0x5555,0x20}` sequence.
**How to avoid:** P7 = (a) delete the unused/duplicate `FLASH_ENABLE_WRITE_PROTECTION` (grep confirms it has **no callers** — only `FLASH_ENABLE_WRITE` is used, by flash3/flash4); (b) in `eeprom_28c.cpp`, delete the local `EEPROM_SDP_DISABLE` and call `flash_execute_command(FLASH_DISABLE_WRITE_PROTECTION)` instead of `flash_execute_command(EEPROM_SDP_DISABLE)`. `eeprom_28c.cpp` already `#include "flash_utils.h"`, so the table is in scope.
**Warning sign:** If the eeprom28c golden write trace (`test_golden_eeprom28c_write`) changes after P7, the two tables were NOT identical — STOP and inspect (they are identical; this should be zero-diff).
**Note (ODR subtlety):** these `const byte_flip_t` arrays are *defined* in the header. Each .cpp that includes `flash_utils.h` gets its own internal-linkage copy. Deleting `FLASH_ENABLE_WRITE_PROTECTION` removes dead duplicated data from every TU that includes the header → this is where the flash *savings* come from. Confirm no TU references the deleted symbol (`grep -rn FLASH_ENABLE_WRITE_PROTECTION src/ include/` → only the definition).

### Pitfall 2: P3's two call sites diverge on three axes (highest deferral risk)
**What goes wrong:** Extracting `eprom_check_vpp` and `flash_intel_check_vpp` into one function that also owns regulator routing.
**Reality (verified, line-by-line):**
| Aspect | `eprom_check_vpp` (eprom.cpp:262-325) | `flash_intel_check_vpp` (flash_intel.cpp:52-108) |
|--------|----------------------------------------|---------------------------------------------------|
| REV0 guard | present (early-return WARNING) | present (early-return WARNING) — **same** |
| Regulator enable | toggles it itself: `0x0B\|FLAG_VPE_AS_VPP → REGULATOR` else `REGULATOR\|VPE_DROP`; `delay(100)` | does NOT toggle — caller (`write_init:133`) already set `REGULATOR\|P1` + `delay(500)` |
| Window compare body | `vpp>set+500 → HIGH (FORCE?WARN:ERR)`; `vpp<set*95/100 → LOW WARN`; packs `_b[8]` | **IDENTICAL** body, identical `_b[8]` packing |
| Trailing clear | `set_control_register(REGULATOR\|VPE_DROP, 0)` | NONE — caller holds VPP through write |
**How to avoid:** the shared `vpp_check_window(handle)` owns ONLY the read+window+pack+FORCE block (the verbatim-identical middle). Each handler keeps: its own REV0 guard (or move it in only if both are identical — they are, so it *can* move, but verify), its own regulator enable/delay BEFORE the call, and eprom keeps its trailing clear AFTER the call. Keying is on `handle->protocol` (D-06) only inside the routing each handler retains, never inside the shared window.
**Warning sign:** any change in `test_golden_eprom_0x07/08/0B_write` or `test_golden_flash_intel_write` trace order. If it won't zero-diff, **defer P3 (D-02)** — this is the explicitly-flagged most-likely deferral.

### Pitfall 3: P5's three sites are not the same loop
**What goes wrong:** Building one `poll_readback` that replaces all three loops.
**Reality (verified):**
- `eeprom28c_wait_for_write` (eeprom_28c.cpp:156): `for j<2000 { delayMicroseconds(10); observed=get_data(addr); if(==expected) return true; }` then `MSG_ERR_EEPROM_TIMEOUT` `_b[5]`.
- `flash4_wait_for_page_write` (flash_type_4.cpp:119): `for j<1024 { delayMicroseconds(10); observed=get_data(addr); if(==expected) return true; }` then `MSG_ERR_FL4_VERIFY_TIMEOUT` `_b[5]` (different byte order in the frame!).
- `verify_and_update_mask` (eprom.cpp:182): a whole-buffer loop `for i<data_size { if get_data(addr+i)!=buf[i] {count++; set bitmask bit} else {clear bit} } return count;` — **no timeout, no single address, returns a count, no error frame**.
**How to avoid:** the genuinely-shared kernel between sites 1 and 2 is the bounded single-address poll. eprom's site is a different algorithm. Options: (a) share only eeprom28c+flash4 (different iteration cap and error frame are parameters); (b) extract a tiny "read addr, compare expected byte" leaf used by all three. Either way the **error frames differ** (`MSG_ERR_EEPROM_TIMEOUT` vs `MSG_ERR_FL4_VERIFY_TIMEOUT`, and different `_b[]` byte order) and the iteration counts differ (2000 vs 1024) → these MUST be parameters, or the traces diverge.
**Warning sign:** `test_golden_eeprom28c_write` or `test_golden_flash4_write` count/element drift. If it won't zero-diff, defer P5 (D-02).

### Pitfall 4: configure_memory overwrites `firestarter_get_data` (test-mechanics, from Phase 88)
**What goes wrong:** A new/edited golden test sets a mock `get_data` before `configure_memory()` and the pointer gets clobbered.
**How to avoid:** re-assign the mock pointer AFTER `configure_memory()` and before driving `operation_init`/`main` (documented in `test_val_eprom.cpp` as "Pitfall 3", lines 478-489). You should NOT need to edit tests for a pure extraction (zero-diff goal) — but if a re-bless requires touching a test, honor this order.

### Pitfall 5: The 0x100 bit is invisible in the trace (don't rely on it)
**What goes wrong:** Assuming the golden trace captures `CTRL_VPP_VPE_DROP_ENABLE` (0x100 on Rev2). It does NOT — `rurp_write_to_register` stores `(uint8_t)data`, low-byte only (golden_trace.h LOW-BYTE-ONLY CAVEAT).
**Implication for P3:** the eprom 0x07/0x08 path sets `REGULATOR|VPE_DROP` but the trace only shows the 0x80 regulator bit, not the 0x100 drop bit. The INV-01/INV-03 *bit-level* assertions in `test_val_eprom.cpp` are the complementary guard for that bit. So the golden trace alone won't catch a VPE_DROP regression in P3 — **the INV tests must also stay green** (SAFE-02 / D-07). Run the full suite, not just the golden tests.

### Pitfall 6: `test_flash_intel_vpp` + `test_eeprom28c_chip_id` suites are pre-existing flaky (suite-level)
**What goes wrong:** Interpreting a Unity teardown SIGABRT in those two suites as a P3/P4 regression.
**Reality:** platformio.ini documents these as KNOWN-FLAKY (all individual assertions PASS but the suite ERRORS in teardown — a pre-existing parallel-build race, v1.4 carry-forward). They are EXCLUDED from `test_filter`. The `test_val_*` golden suites (which this phase relies on) are the active ones.
**How to avoid:** rely on `test_val_flash_intel` (the golden suite, in the filter) for flash_intel, not `test_flash_intel_vpp`.

## Code Examples

Verified patterns from the live codebase (not external docs):

### Flash-delta gate (exact Phase 87-04 recipe — reuse per step)
```bash
# Source: .planning/phases/87-naming-documentation-pass/87-04-SUMMARY.md Gate 3
# Baseline file already exists: firestarter/.flash-baseline-87.txt == 25654
PRE=$(cat firestarter/.flash-baseline-87.txt)            # or the previous step's post
POST=$(cd firestarter && pio run -e leonardo 2>&1 \
       | grep -oE 'Flash:.*used [0-9]+ bytes' \
       | grep -oE '[0-9]+ bytes' | grep -oE '[0-9]+')
DELTA=$(( POST - PRE ))
# Per-step gate (D-01): fail if a single step rises more than +16B
[ "$DELTA" -le 16 ] && echo "STEP PASS (delta=$DELTA)" || { echo "STEP FAIL (delta=$DELTA > 16)"; exit 1; }
# Phase-close gate (D-01): final must be strictly below baseline
# [ "$FINAL" -lt 25654 ] || exit 1
```
Live `pio run -e leonardo` this session: `Flash: 89.5% (used 25654 bytes from 28672 bytes)` — baseline confirmed exact. [VERIFIED: ran this session]

### Per-step oracle rerun
```bash
cd firestarter && pio test -e native                 # ALL native suites green (D-07/SAFE-02)
# narrow during dev:
pio test -e native -f "*test_val_eeprom28c*" -f "*test_val_flash4*"   # P7
pio test -e native -f "*test_val_eprom*" -f "*test_val_flash_intel*"  # P3/P4
pio test -e native -f "*test_dispatch*"              # dispatch-mirror order (D-05)
```

### Re-bless (D-04 — only after inspecting a confirmed-benign diff)
```bash
# golden_trace.h prints .inc-ready rows under -DGOLDEN_BLESS.
# Add -DGOLDEN_BLESS to [env:native] build_flags (temporarily), run the one suite,
# redirect print_trace_inc() output into the .inc, REVIEW git diff, document in commit msg.
# This is a deliberate human-gated event — NOT routine.
```

### Host frozen-world gates (read-only, D-05/SAFE-03)
```bash
cd firestarter_app && python tools/check_dispatch.py   # expect exit 0: "0 dispatch regressions, 0 consistency violations"
cd firestarter_app && python tools/diff_db.py          # expect exit 0: "0 changed / 0 new / 0 missing"
git -C firestarter_app diff --quiet -- firestarter/ tools/ tests/   # SAFE-06: exit 0 (host untouched)
```
Note: run host gates with the system python (py3.12 here masks CI py3.11, but these two scripts are pure stdlib JSON logic — no ruff/mypy/codegen involved, so the py-version mask does not affect their result; the SAFE-06 concern is only relevant if a host *source* file were edited, which it must not be).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Duplicated handler bodies (chip-id, VPP, poll, SDP tables) | Shared primitives in `primitives.cpp` + flash-local SDP tables | THIS phase | Flash shrinks; single source per behavior. |
| flash3/flash4 chip-id duplicated | `flash_util_check_chip_id_execute` shared (Phase 74 Plan 02) | v1.14 | The P4 precedent — generalize it to 4 more sites. |
| "monotonically shrinking" strict per-step ≤0 | per-step ≤+16B + phase net-decrease (D-01) | THIS phase | Tolerates first-call-site overhead; biggest-saver-first front-loads headroom. |

**Deprecated/outdated:** none introduced. `FLASH_ENABLE_WRITE_PROTECTION` (flash_utils.h:48) is dead duplicated data (no callers) and is removed by P7.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `FLASH_ENABLE_WRITE_PROTECTION` has no callers (dead duplicate) — safe to delete in P7. | Pitfall 1 | LOW — verify with `grep -rn FLASH_ENABLE_WRITE_PROTECTION src/ include/`; if a caller exists, redirect it to `FLASH_ENABLE_WRITE` (byte-identical) instead of deleting. [ASSUMED — grep this session showed only the definition in flash_utils.h; planner should re-grep at execution time.] |
| A2 | Deleting header-defined duplicate const tables yields measurable flash savings (each including TU drops its internal-linkage copy). | Pitfall 1 / Flash Gate | LOW — if the linker already dead-stripped unused tables, P7 savings may be ~0, but P7 still cannot *increase* flash, so the ≤+16 gate passes regardless; the phase-net-decrease then leans on P4. [ASSUMED — AVR-gcc `-ffunction-sections`/`-fdata-sections` + `--gc-sections` behavior; measure empirically per D-01.] |
| A3 | The `error_code` param of `eprom_internal_check_chip_id` is redundant with the shared FORCE-downgrade tail. | Pattern 2 | MEDIUM — `eprom_generic_init` passes `FORCE?WARNING:ERROR`, which equals what the tail computes; but `eprom_check_chip_id_execute` passes `RESPONSE_CODE_ERROR` unconditionally. The shared tail keys on `FLAG_FORCE`, so behavior may differ if a caller wanted ERROR despite FORCE. **Preserve the param or verify the trace** before collapsing. [ASSUMED — needs trace confirmation.] |

**These three are the only assumed claims; everything else is VERIFIED against live source or a live tool run this session.**

## Open Questions

1. **Does P7 actually shrink flash, or just hold it flat?**
   - What we know: the duplicate tables are byte-identical and `FLASH_ENABLE_WRITE_PROTECTION` appears callerless.
   - What's unclear: whether AVR-gcc already gc-sections'd the unused table (making the delete a no-op for flash) and whether `EEPROM_SDP_DISABLE`'s internal-linkage copy in eeprom_28c.o is currently counted.
   - Recommendation: P7 commit measures empirically (D-01). Even if P7 delta is ~0, it cannot fail the ≤+16 gate, and P4 carries the net-decrease. Do not gate the phase on P7 producing the *largest* saving — gate on the cumulative net-decrease.

2. **Can the REV0 early-return guard move into the shared `vpp_check_window` (P3)?**
   - What we know: both `eprom_check_vpp` and `flash_intel_check_vpp` open with an identical `#ifdef HARDWARE_REVISION … REVISION_0 → WARNING; return;` block.
   - What's unclear: whether moving it changes the trace ordering relative to each handler's regulator-enable (eprom enables AFTER the guard; flash_intel's caller enables BEFORE calling). Since the guard is before any register write in both, it likely moves cleanly — but the eprom path enables the regulator *inside* check_vpp while flash_intel's caller does it outside, so the shared function's internal order matters.
   - Recommendation: keep the REV0 guard handler-local in the first cut (smallest shared surface = lowest trace risk); only fold it in if the trace stays zero-diff and it demonstrably saves flash.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO Core | `pio run -e leonardo`, `pio test -e native` | ✓ | 6.1.19 | — |
| AVR toolchain (avr-gcc) | leonardo build | ✓ | bundled via PlatformIO `atmelavr` | — |
| native toolchain (host g++/clang) | native tests | ✓ (ran 34 tests this session) | host gnu++17 | — |
| Python 3 | `check_dispatch.py`, `diff_db.py` | ✓ | py3.12 devcontainer (scripts are pure stdlib JSON — py-version-insensitive) | — |
| Leonardo board hardware | flash MEASUREMENT only (compile, not upload) | n/a | — | none needed — `pio run -e leonardo` measures flash from the ELF without a board attached |

**Missing dependencies with no fallback:** none. The entire phase runs offline in the devcontainer (no bench hardware required — flash is measured from the build, traces are host-side).

## Validation Architecture

> For this refactor, the validation IS the existing Phase-88 oracle. No new test infrastructure is built (SAFE-05). Every extraction step reruns these exact green gates.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Unity + ArduinoFake (`fakeit`), `[env:native]` (PlatformIO 6.1.19) |
| Config file | `firestarter/platformio.ini` `[env:native]` (no change this phase) |
| Quick run command | `cd firestarter && pio test -e native -f "*test_val_<family>*"` |
| Full suite command | `cd firestarter && pio test -e native` |
| Flash measure | `cd firestarter && pio run -e leonardo` (parse "Flash: … used N bytes") |
| Host gates | `cd firestarter_app && python tools/check_dispatch.py && python tools/diff_db.py` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PRIM-02 (P7) | eeprom28c SDP + flash write traces unchanged after dedup | golden trace | `pio test -e native -f "*test_val_eeprom28c*" -f "*test_val_flash4*" -f "*test_val_flash3*"` | ✅ (`golden_eeprom28c_write.inc`, `golden_flash4_write.inc`, `golden_flash3_write.inc`) |
| PRIM-03 (P4) | chip-id compare/report unchanged for eprom, flash_intel, eeprom28c, flash4 | golden trace | `pio test -e native -f "*test_val_eprom*" -f "*test_val_flash_intel*" -f "*test_val_eeprom28c*" -f "*test_val_flash4*"` | ✅ (`*_chip_id.inc` per family; **flash3 has none** — Phase 88 D-03, confirmed) |
| PRIM-04 (P3) | VPP window-check unchanged for eprom (0x07/08/0B) + flash_intel; INV-01/03 bit guards green | golden trace + INV asserts | `pio test -e native -f "*test_val_eprom*" -f "*test_val_flash_intel*"` | ✅ |
| PRIM-05 (P5) | eeprom28c + flash4 poll + eprom verify-readback unchanged | golden trace | `pio test -e native -f "*test_val_eeprom28c*" -f "*test_val_flash4*" -f "*test_val_eprom*"` | ✅ |
| PRIM-06 | flash net-non-increase per step + final % | build measure | `pio run -e leonardo` + delta script (above) | ✅ (`.flash-baseline-87.txt`=25654) |
| SAFE-01 | protocol-keyed; WARNING-5 guards preserved | dispatch + INV | `pio test -e native -f "*test_dispatch*"` + `check_dispatch.py` | ✅ |
| SAFE-02 | INV-01..09 survive, greppable ≥3 files | INV asserts + grep | full `pio test -e native` + `grep -rn INV-NN doc/ src/ test/` (×9) | ✅ |
| SAFE-03 | dispatch 0 violations, DB diff empty | host gates | `check_dispatch.py` (exit 0) + `diff_db.py` (exit 0) | ✅ |

### Sampling Rate
- **Per task / extraction commit:** the narrow family suites for that primitive + `pio run -e leonardo` delta + INV grep.
- **Per primitive merge (commit kept):** full `pio test -e native` + both host gates + flash delta.
- **Phase gate:** full `pio test -e native` green, `check_dispatch.py`/`diff_db.py` exit 0, `git -C firestarter_app diff --quiet` exit 0, final flash `< 25654`, achieved % reported (PRIM-06) — before `/gsd-verify-work`.

### Wave 0 Gaps
- None — existing test infrastructure covers all phase requirements. The Phase-88 golden traces, the INV-01..09 assertions, the `test_dispatch` mirror, and the two host gates are all present and green at HEAD (verified: 34/34 in `test_val_eprom`+`test_dispatch` this session; leonardo build SUCCESS at 25654 B).
- The ONLY new artifact is the primitive source itself: `firestarter/src/proms/primitives.cpp` + `firestarter/include/primitives.h` (D-03). No new test file is required for a zero-diff extraction; if a re-bless is needed (D-04), it edits an existing `.inc`, not a new file.

## Security Domain

> `security_enforcement` is not set to `false` in config, so this section is included. The "security" surface here is electrical safety (12V/25V on a 5V pin), not classic appsec — there is no auth/session/crypto/input-validation surface in an offline firmware refactor.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | offline firmware, no users |
| V3 Session Management | no | no sessions |
| V4 Access Control | no | no multi-user surface |
| V5 Input Validation | partial | the firmware's existing `vpp_mv`/`mem_size` underflow guards (e.g. eeprom_28c.cpp:78 `mem_size < 64`) — must be PRESERVED by P4 extraction, not relocated |
| V6 Cryptography | no | none |

### Known Threat Patterns for this firmware refactor
| Pattern | STRIDE | Standard Mitigation (must survive each step) |
|---------|--------|---------------------------------------------|
| 12V VPP regulator enabled on a 5V part | Tampering / DoS (chip destruction) | BLOCKER-2 dispatch guard (`check_dispatch.py` SRAM-never-reaches-eprom) + protocol-keyed routing (D-06). FROZEN — P3 must not move regulator routing out of the handlers. |
| Over-voltage past the VPP window | Tampering (chip damage) | the `vpp_mv > set+500` HIGH check (eprom.cpp:282, flash_intel.cpp:65) — D-08; P3 extracts the *compare* but the FORCE/ERROR semantics and the threshold MUST stay byte-identical (golden trace + INV guards). |
| Writing an irreplaceable UV part on an unstable path | (operational) | 2516 stays `UNVERIFIED` (D-08); not exercised by this phase. |
| Host bypassing the support-status guard | Elevation | `chip_resolver.resolve_chip` raises `ChipNotImplementedError` for non-supported chips (chip_resolver.py:55) — never bypassed; this phase makes no host change (SAFE-06). |

**The single highest-stakes invariant:** P3 sits adjacent to the over-voltage check (D-08) and owns the regulator-keying surface (D-06). If P3's extraction cannot keep both the golden trace AND the INV-01/INV-03 bit-level guards green at zero-diff, defer it (D-02) rather than re-bless.

## Sources

### Primary (HIGH confidence — read live this session)
- `firestarter/src/proms/{eprom,eeprom_28c,flash_intel,flash_type_3,flash_type_4,flash_utils,memory}.cpp` — all call sites read; CONTEXT line numbers verified (minor drift noted inline).
- `firestarter/include/flash_utils.h` — confirmed `FLASH_ENABLE_WRITE_PROTECTION`==`FLASH_ENABLE_WRITE` and `FLASH_DISABLE_WRITE_PROTECTION`==`EEPROM_SDP_DISABLE` byte-identical.
- `firestarter/test/native/avr/_shared/golden_trace.h` + `test_val_eprom/test_val_eprom.cpp` + `*.inc` fixtures — the D-01 oracle mechanics, LOW-BYTE caveat, Pitfall 3.
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — dispatch-mirror RUN_TEST order.
- `firestarter/platformio.ini` — `[env:native]` `src_filter=+<proms/>`, `test_filter` (flaky-suite exclusions), no-change-needed for new TU.
- `firestarter/.flash-baseline-87.txt` = `25654`; live `pio run -e leonardo` = 25654 B (89.5%); live `pio test -e native` = 34/34 PASS.
- `.planning/phases/87-naming-documentation-pass/87-04-SUMMARY.md` — the `DELTA≤16` failable flash-gate recipe (the D-01 precedent).
- `firestarter_app/tools/check_dispatch.py` + `diff_db.py` + `firestarter/chip_resolver.py:55` — frozen-world + safety gates.
- `firestarter/doc/PROTOCOLS.md` §3 — INV-01..09 traceability matrix (owning handler + test fn + suite path per INV).
- `.planning/REQUIREMENTS.md` (PRIM-02..06, SAFE-01..04), `.planning/ROADMAP.md` Phase 89 SC#1-5.

### Secondary (MEDIUM)
- `firestarter/CLAUDE.md` + `firestarter_app/CLAUDE.md` — build/test commands, py3.11 CI vs py3.12 devcontainer note, dispatch-order source-of-truth.

### Tertiary (LOW)
- none — no WebSearch needed; this is an internal-codebase refactor.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new deps; toolchain ran successfully this session.
- Architecture / call-site characterization: HIGH — every site read in live source; byte-identity of P7 tables and P4 report-tail confirmed directly.
- Pitfalls (P3/P5 divergence): HIGH — the divergences are quoted from source line-by-line.
- Flash gate: HIGH — baseline file + live build both show 25654; Phase 87-04 recipe documented.
- Assumptions A1/A2/A3: LOW-MEDIUM — flagged in Assumptions Log; resolved by execution-time grep + empirical flash measure + trace inspection.

**Research date:** 2026-06-26
**Valid until:** 2026-07-26 (stable — internal firmware; only invalidated if Phase 88 golden fixtures or the host baselines are re-pinned before execution).
