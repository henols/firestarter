# Phase 87: Naming + Documentation Pass - Pattern Map

**Mapped:** 2026-06-25
**Files analyzed:** 13 (1 new doc + 10 firmware handlers + native test suites + 2 read-only gates)
**Analogs found:** 13 / 13 (all in-repo analogs exist — no green-field files)

> **Phase nature:** documentation + source-comment + native-test pass. NO behavior
> change, DB-frozen (D-09 `diff_db` empty), near-zero flash delta (D-10 — plain
> `//` and `/* */` comments only, NO PROGMEM strings). Every file below already
> has a close in-repo analog; this phase extends existing patterns, it does not
> invent new ones.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/doc/PROTOCOLS.md` (NEW) | config/doc | reference | `firestarter/doc/SHIELD-REVISIONS.md` | exact (sibling GitHub-visible doc, same 2-col-table style) |
| `firestarter/src/proms/eprom.cpp` (comment) | handler | request-response | self — already has inline rationale (lines 69–76, 144–151) + `flash_type_4.cpp` header block | exact |
| `firestarter/src/proms/eeprom_28c.cpp` (comment) | handler | request-response | `flash_type_4.cpp` lines 19–26 (rationale block) | role-match |
| `firestarter/src/proms/flash_intel.cpp` (comment) | handler | request-response | `flash_type_4.cpp` lines 19–26 | role-match |
| `firestarter/src/proms/flash_type_3.cpp` (comment) | handler | request-response | `flash_type_4.cpp` lines 19–26 | role-match |
| `firestarter/src/proms/flash_type_4.cpp` (comment) | handler | request-response | self (lines 19–26 already the model block) | exact |
| `firestarter/src/proms/flash_utils.cpp` (comment) | utility | transform | `flash_type_4.cpp` lines 19–26 | role-match |
| `firestarter/src/proms/memory.cpp` (comment) | dispatch | request-response | firmware `CLAUDE.md` §Protocol Dispatch (prose to cite); `flash_type_4.cpp` block (format) | role-match |
| `firestarter/src/proms/sram.cpp` (comment) | handler | request-response | `not_implemented.cpp` (minimal-handler header) + `flash_type_4.cpp` block | role-match |
| `firestarter/src/proms/not_implemented.cpp` (comment) | handler | request-response | self (minimal fail-closed handler) | exact |
| `firestarter/src/firestarter.cpp` (comment) | dispatch entry | request-response | `flash_type_4.cpp` block (format); structure unchanged | role-match |
| `firestarter/test/native/avr/test_val_*/` (gap-fill assertions) | test | request-response | `test_val_eprom/test_val_eprom.cpp` | exact (Unity + recording-bus harness) |
| `firestarter_app/tools/check_dispatch.py` (READ-ONLY) | gate | batch | n/a — invoke, do not edit | exact |
| `firestarter_app/tools/diff_db.py` (READ-ONLY) | gate | batch | n/a — invoke, do not edit | exact |

## Bucket Enumeration (the bound on PROTOCOLS.md, from the LIVE DB)

Enumerated from `firestarter_app/firestarter/data/chip_database.json` (746 chips,
`programming.algorithm` field). **This is the authoritative set PROTOCOLS.md must
name — not memory, not CLAUDE.md.**

| protocol_id | DB chip count | handler file | folder slug (col 1, D-02) | status |
|-------------|--------------|--------------|----------------------------|--------|
| 0x05 | 27 | flash_type_4.cpp | (datasheets slug) | real |
| 0x06 | 190 | flash_type_3.cpp | (datasheets slug) | real |
| 0x07 | 170 | eprom.cpp | (datasheets slug) | real |
| 0x08 | 127 | eprom.cpp | (datasheets slug) | real |
| 0x0B | 32 | eprom.cpp | (datasheets slug) | real |
| 0x0D | 84 | eeprom_28c.cpp | (datasheets slug) | real |
| 0x0E | 20 | sram.cpp | (datasheets slug) | real |
| 0x10 | 39 | flash_intel.cpp | (datasheets slug) | real |
| 0x27 | 2 | sram.cpp | (datasheets slug) | real |
| 0x28 | 34 | sram.cpp (FM1608 → SRAM_STD/FRAM) | (datasheets slug) | real (NAME-04 correction) |
| 0x29 | 20 | sram.cpp | (datasheets slug) | real |
| 0x34 | 1 | not_implemented.cpp (X88C64) | (datasheets slug) | real-but-PCB-blocked (FUT-01); `electrical.type` EEPROM (NAME-04) |
| 0x35, 0x39 | 0 each | flash_type_4.cpp dispatch preserved | — | **phantom** — "Honest non-protocols" section (D-08) |
| 0x11, 0x2A, 0x2B, 0x2C | 0 each | not_implemented.cpp | — | **infeasible** — "Honest non-protocols" section (D-08) |

> Cross-check: firmware `CLAUDE.md` §Algorithm Handlers table is the per-protocol
> name + VPP + file source-of-truth to distill into PROTOCOLS.md columns. The
> `.planning/research/PROTOCOLS.md` is the prose source to distill (correct its
> "FM1608 algorithm 40 = 0x28" decimal/hex conflation per NAME-04 / Specifics).

## Pattern Assignments

### `firestarter/doc/PROTOCOLS.md` (NEW doc, GitHub-visible)

**Analog:** `firestarter/doc/SHIELD-REVISIONS.md` (sibling canonical doc, 15.9KB)

**Replicate the opening-orientation pattern** (SHIELD-REVISIONS.md lines 1–22):
a one-paragraph "what this doc is", then an "if you want X, read §Y" reader-router,
then a pointer to the deeper meta-repo source. PROTOCOLS.md should open the same
way and point at `.planning/research/PROTOCOLS.md` + `.planning/v1.13-PROTOCOL-ENUMERATION.md`
as the deeper sources.

**Replicate the two-column wide-table style** (SHIELD-REVISIONS.md §1 lines 29–38,
§2 lines 48–57) — markdown pipe tables with a header row + per-row notes column.
This is exactly the D-02 two-name scheme: **col 1 = `datasheets/<hex>-<NAME>/`
folder slug (unchanged)**, **col 2 = descriptive algorithm-axis name**, plus the
NAME-01 facet columns (write algorithm / erase model / VPP behavior / pin roles).

**Section structure** (Claude's discretion per D-discretion, suggested):
1. Orientation + reader-router (mirror SHIELD-REVISIONS.md lines 1–22).
2. Per-bucket sections (D-08): one section per real `protocol_id` above, each
   covering the 4 NAME-01 facets, datasheet-cited. The FM1608 (0x28 SRAM_STD)
   and X88C64 (0x34, EEPROM `electrical.type`) corrections get explicit NAME-04
   call-outs with their true `infoic.xml` identity tuples (FM1608 =
   type4/proto0x07/variant0x4126 → 0x28; X88C64 = type1/proto0x34/variant0x3100/
   flags0x00414200 → EEPROM — from `86-CONTEXT.md`).
3. "Honest non-protocols" section (D-08): phantom 0x35/0x39 + infeasible
   0x11/0x2A/0x2B/0x2C, **named as non-protocols**, NOT as buckets with behavior.
4. The INV-01..INV-09 traceability matrix section (D-05) — see Shared Patterns.

**Heading-anchor cross-ref style to copy** (SHIELD-REVISIONS.md line 11):
`[§1 (inventory)](#1-inventory)` — use the same `[§N (label)](#anchor)` form so
the matrix section can deep-link to per-bucket sections.

---

### Firmware handler header-comment block (D-07) — applies to all 10 handler files

**Citation-format analog (the model to copy):** `firestarter/src/proms/flash_type_4.cpp`
lines 19–26 — an existing **plain `/* ... */` rationale block** that explains the
*why* of a value (data-driven page size) with worked examples. This is the proven
zero-flash-cost pattern (it is a C comment, compiles to nothing — satisfies D-10).

```c
/* Data-driven page size derived from chip capacity (handle->mem_size).
 * W29C040 (512K = 524288) → 256; SST29EE010 (128K = 131072) → 128;
 * AT29C256 (32K = 32768) → 64. Flash4 DB chips span 32KB–512KB.
 * A fixed 256 would over-run smaller chips' 64-byte page buffers;
 * the old fixed 64 polled mid-page on W29C040 (original bug).
 * ... */
```

**Anchored-citation analog (filename + section/page, D-07):** `test_val_eprom.cpp`
lines 26–30 already cite the *source of a value* by file: `"VPP mechanism (from
eprom.cpp source — not guessed)"`. D-07 wants the same discipline but pointed at
**datasheets**, e.g. (from Specifics): `datasheets/07-W27C512/<file>.pdf p.7 §6.2`.

**Existing inline-rationale precedent already in `eprom.cpp`** (these are the
behaviors to formalize into the file-header block, citing the datasheet origin):
- Lines 69–76 — pulse_delay defaults (`0x08→100µs`, `0x0B→500µs`, default 1ms) →
  **INV-06 pulse-delay defaults**.
- Lines 144–151 — `0x0B`/`FLAG_VPE_AS_VPP` direct-VPE-path vs `0x07/0x08`
  `CTRL_VPP_VPE_DROP_ENABLE` dropping path → **INV-01 (0x0B direct-VPE rail)**.

**What to replicate per file:** ONE block (D-07) placed directly under the existing
MIT license header (`/* Project Name: Firestarter ... */`, identical in all 10
files, e.g. `not_implemented.cpp` lines 1–6). The block states the *why* (timing /
VPP routing / pin behavior) + a datasheet filename+section/page anchor, and names
the INV-0x ids the handler owns (so the matrix is greppable per D-05). Full prose
lives in PROTOCOLS.md; the comment is the concise "why + cite".

Per-file INV ownership (from `87-CONTEXT.md` canonical_refs):

| File | INV ids to cite in the header block |
|------|--------------------------------------|
| `eprom.cpp` | INV-01 (0x0B direct-VPE), INV-02 (0x0B shared OE/VPP read-skip), INV-03 (0x08 P1-as-VPP), INV-05 (VPP-skip-on-read), INV-06 (pulse-delay defaults), INV-08 (WARNING-5 0x07→0x0D preserved-by-decode) |
| `eeprom_28c.cpp` | 0x0D SDP-disable + DQ7 page poll (no INV cell unless gap-fill needs one) |
| `flash_intel.cpp` | 0x10 command-register + SR polling, 12V via `CTRL_VPP_P1_ENABLE` |
| `flash_type_3.cpp` | INV-09 (SST39SF040 keep-Flash/EEPROM) |
| `flash_type_4.cpp` | INV-04 (256B page boundary — block already at lines 19–26; extend with INV id + datasheet cite) |
| `flash_utils.cpp` | shared flash helpers (cite parent handler) |
| `memory.cpp` | dispatch order (cite firmware `CLAUDE.md` §Protocol Dispatch; structure unchanged) |
| `sram.cpp` | 0x28 SRAM_STD / FM1608, INV-07 (SRAM→FRAM) |
| `not_implemented.cpp` | phantom (0x35/0x39) + infeasible (0x11/0x2A/0x2B/0x2C) + 0x34 X88C64 fail-closed |
| `firestarter.cpp` | INV ordering reference (dispatch entry; structure unchanged) |

> **D-10 guard:** every block is a `//` or `/* */` C comment. Do NOT introduce any
> `PSTR()`/PROGMEM string or `LOG_*` call to carry rationale — that would grow flash
> and fail the `pio run -e leonardo` near-zero-delta gate.

---

### Native gap-fill tests (D-05/D-06) — `firestarter/test/native/avr/test_val_*/`

**Analog (the harness to match):** `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp`
— the richest, most recent (Phase 71) `test_val_*` suite. It is the canonical
pattern for "assert handler behavior by side-effect via the recording bus stub".

**Existing suites available to host the gap-fill assertions (extend, don't create
a new harness — code_context):**

| Suite | Hosts INV (natural home) |
|-------|--------------------------|
| `test_val_eprom/` | INV-01, INV-02, INV-03, INV-05, INV-06, INV-08 (0x07/0x08/0x0B family) |
| `test_val_eeprom28c/` | 0x0D SDP/poll cells if any |
| `test_val_flash3/` | INV-09 (SST39SF040 keep-Flash/EEPROM) |
| `test_val_flash4/` | INV-04 (256B page boundary) |
| `test_val_flash_intel/` | 0x10 cells if any |
| `test_val_sram/` | INV-07 (SRAM→FRAM) |

> Decide per-INV host suite at planning time (D-discretion). Only add a test where
> the invariant has NO existing covering assertion (D-06). Full per-family register
> golden traces are explicitly Phase 88 — keep these MINIMAL.

**Test-function naming pattern (D-05 — must be greppable to its INV id):** the
existing convention is `test_<family>_<protocol>_<behavior>` (e.g.
`test_eprom_0x0B_write_enables_vpp_regulator`, line 133). Extend it to embed the
INV id, e.g. `test_inv01_eprom_0x0B_direct_vpe_rail` OR add the INV id to the test
docstring/comment — as long as `grep INV-01` lands on the live test (D-05).

**Recording-bus assertion mechanics to copy** (test_val_eprom.cpp lines 48–100):
```c
extern "C" void clear_bus_recording();
extern "C" int  bus_recording_count();
extern "C" uint8_t recorded_reg(int i);
extern "C" uint8_t recorded_data(int i);

static bool recording_has_vpp_enable(uint8_t vpp_bit) {
    for (int i = 0; i < bus_recording_count(); i++) {
        if (recorded_reg(i) == CONTROL_REGISTER && (recorded_data(i) & vpp_bit))
            return true;
    }
    return false;
}
```
> PITFALL (carried from the suite, lines 92–96): `CTRL_VPP_VPE_DROP_ENABLE` is
> `0x100` when `HARDWARE_REVISION` is defined and does NOT fit `uint8_t`; the
> recording buffer is `uint8_t`. Assert on 8-bit-fit bits (`CTRL_VPP_REGULATOR_ENABLE`
> 0x80, `CTRL_VPP_P1_ENABLE` 0x08) for VPP detection.

**Handle-builder + setUp boilerplate to copy** (lines 54–79): `setUp()` resets
ArduinoFake, stubs `Serial.write/flush` + `delay()`, then `clear_bus_recording()`.
`make_handle(protocol, cmd)` zero-inits a `firestarter_handle_t` with
`vpp_mv=0`, `chip_id=0`, `mem_size=65536`, `ctrl_flags=FLAG_SKIP_BLANK_CHECK|FLAG_SKIP_ERASE`.

**Unity registration boilerplate to copy** (lines 205–220):
```c
int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();
    RUN_TEST(test_...);     // one RUN_TEST per assertion
    return UNITY_END();
}
```

**host_stubs.cpp pattern to copy** (`test_val_eprom/host_stubs.cpp`, all 47 lines):
opt-in flags `#define HOST_STUBS_RECORD_BUS` and `#define HOST_STUBS_CUSTOM_HW_REVISION`
**before** `#include "../_shared/host_stubs_common.inc"` (PITFALL 1, line 17), then
the suite-local hw-rev mock. If a new gap-fill test lands in an existing suite,
its `host_stubs.cpp` likely already covers the needed symbols — extend only if the
new assertion references new `rurp_*` symbols (per firmware `CLAUDE.md` §Reuse pattern).

**Invocation (cite in acceptance criteria):** `pio test -e native` (all suites) or
`pio test -e native -f "*test_val_eprom*"` (one suite).

---

### Read-only gates — `check_dispatch.py` / `diff_db.py` (D-09)

**Do NOT edit.** Re-run only; the phase must leave both green/empty.

**Invocation (cite verbatim in the plan's acceptance criteria):**
```bash
cd firestarter_app
python tools/check_dispatch.py    # PASS line; exit 0 = 0 violations (D-09)
python tools/diff_db.py           # exit 0 = empty diff vs re-pinned baseline (D-09)
```

**Exit-code contract to cite** (from each file's module docstring):
- `check_dispatch.py` (lines 16–21, PASS print lines 491–502): `0` = every chip
  resolves to a real handler AND no SRAM-protocol chip dispatches to
  `configure_eprom` (BLOCKER-2); `1` = any unsupported/unsafe dispatch.
- `diff_db.py` (lines 11–22): `0` = all changes explained + 0 missing; `1` = any
  unexplained diff or missing chip (D-03 BLOCK); `2` = infra/load error (distinct
  so CI doesn't confuse a missing input with a real diff).

**Baselines this phase is frozen against** (`87-CONTEXT.md` canonical_refs):
`firestarter_app/tools/baseline/chip_database.baseline.json` (746-chip Phase-86
re-pinned) + `firestarter_app/tools/baseline/dispatch_baseline.json`. Override env
seams exist (`FIRESTARTER_DB_FILE`, `FIRESTARTER_BASELINE_FILE`) but the default
paths are the frozen baselines — run with defaults.

## Shared Patterns

### INV-01..INV-09 traceability matrix (D-05) — the cross-cutting contract

**Home:** a section inside `firestarter/doc/PROTOCOLS.md` (D-05 — single source of
truth). Each row = one INV id + its one-line behavior + the handler file + the live
native test function name that pins it. The INV ids are the SAFE-02 handoff to
Phases 88/89 — they must survive a recompose grep-intact.

The 9 invariants (from D-04):
| ID | Invariant | Owning handler |
|----|-----------|----------------|
| INV-01 | 0x0B direct-VPE rail | eprom.cpp |
| INV-02 | 0x0B shared OE/VPP read-skip | eprom.cpp |
| INV-03 | 0x08 P1-as-VPP | eprom.cpp |
| INV-04 | flash4 256B page boundary | flash_type_4.cpp |
| INV-05 | VPP-skip-on-read | eprom.cpp |
| INV-06 | pulse-delay defaults | eprom.cpp |
| INV-07 | FM1608 SRAM→FRAM | sram.cpp |
| INV-08 | WARNING-5 0x07→0x0D override (now decode-delivered) | eprom.cpp / build path |
| INV-09 | SST39SF040 keep-Flash/EEPROM | flash_type_3.cpp |

**Greppability wiring (D-05):** the INV id appears in BOTH the matrix row (doc) AND
the native test function name/docstring AND the owning handler's header block. One
`grep -rn INV-04` must hit doc + test + handler.

### MIT license header (all firmware files)
**Source:** identical in every `src/proms/*.cpp` (e.g. `not_implemented.cpp` 1–6).
**Apply to:** the new D-07 rationale block goes DIRECTLY BELOW this existing header,
never replacing it.
```c
/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */
```

### Zero-flash-cost discipline (D-10)
**Apply to:** all 10 handler comment edits. Comments only; verify with
`pio run -e leonardo` near-zero flash delta. No PROGMEM/`PSTR`/`LOG_*` additions.

### Host toolchain green (D-10/SAFE-06)
**Apply to:** check_dispatch.py/diff_db.py runs occur in `firestarter_app`; validate
against CI **py3.11** (firmware-side comment/test changes do not touch host code, so
no ruff/mypy/pytest delta is expected — but the gates run under the host env).

## No Analog Found

None. Every file in scope has a strong in-repo analog (this is a "document-the-frozen-
world" pass over an existing, well-tested codebase). The planner should NOT fall back
to `.planning/research/PROTOCOLS.md` *code examples* for structure — but it IS the
prose source to distill into PROTOCOLS.md content (corrected per NAME-04).

## Metadata

**Analog search scope:** `firestarter/doc/`, `firestarter/src/proms/`,
`firestarter/src/firestarter.cpp`, `firestarter/test/native/avr/`,
`firestarter_app/tools/`, `firestarter_app/firestarter/data/chip_database.json`.
**Files scanned:** ~18 (2 docs, 10 handlers, 1 dispatch entry, 6 test suites + 1 shared stub, 2 gates, 1 DB).
**Pattern extraction date:** 2026-06-25
