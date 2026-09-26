# Phase 73: Bench-Validate the 6 Families on Leonardo (hybrid-gated) - Research

**Researched:** 2026-06-17
**Domain:** Bench validation invocation — `dev validate-family` runner reuse, matrix schema,
oracle mechanics, FM1608 SRAM two-pattern bench method, USB-passthrough driving model
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** On hand (run Tier-3 now): W27C512 (0x07), AM29F040 (Flash AMD 0x06), FM1608 (SRAM family
  — actually FRAM/non-volatile, no-VPP). These three families get real Leonardo Tier-3 cells.
- **D-02:** SKIP-deferred (no chip): AT28C256 (0x0D), AT29C040 (0x05), AM28F010 (0x10). Tier-3
  SKIP-deferred with reason "no chip on hand".
- **D-03:** Shield = Rev 2.0 on Leonardo. Re-confirm `controller:` identity per port at each task
  start.
- **D-04:** W27C512 `electrical.type = "EEPROM"` (electrically-erasable, 12V VPP) — NOT UV-EPROM.
  The "UV-EPROM 0x07/08/0B" label is handler-family shorthand.
- **D-05:** SRAM Tier-3 chip is FM1608 (FRAM, non-volatile) — volatility confound disappears.
- **D-06:** Anti-false-positive = two distinct patterns A then B (non-trivial, not all-0x00/0xFF).
- **D-07:** Verdict bar = baseline initial read + N≥2 confirm.
- **D-08:** Per-byte verdict logic: all bytes fail → FIX-01 defect; bytes 1..N OK but byte-0 wrong
  → VAL-06 table-stakes-PASS (byte-0 = separate parked FRAM bug, out of v1.13 scope).
- **D-09:** VAL-06 is hard gate — FM1608 bench must reach a definitive verdict.
- **D-10:** Claude drives `dev validate-family` / serial / sideload over USB passthrough. Operator
  handles only physical actions (chip insertion, shield swap, multimeter, photos).
- **D-11:** Pre-write gate = verify-port + live R1/R2 readback (`r1 ≈ 270000`) + Tier-1
  recording-stub VPP assertions. No separate physical chip-OUT VPP multimeter dry-run required
  (Leonardo is chip-OUT-exempt for sideload; W27C512 12V EVEN-01-proven clean on Leonardo).
- **D-12:** On-hand families close on any recorded Tier-3 verdict (PASS or FAIL) + passing negative
  control.
- **D-13:** Milestone closeable at partial coverage — 3 chipless families close as Tier-3
  SKIP-deferred.
- **D-14:** Non-vacuous PASS oracle already built (Phase 71 D-08). Carried forward, not re-litigated.
- **D-15:** `dev validate-family` runner, SKIP-deferred, matrix artifact ALL already exist from Phase
  71. Phase 73 adds zero production firmware flash.

### Claude's Discretion

- Exact pattern bytes for FM1608 A/B test (subject to D-06 non-trivial rule).
- Run ordering across the 3 on-hand families and how operator hardware-action checkpoints are
  sequenced within Claude-driven sessions.
- Evidence-SHA capture/log format for each recorded cell (within the Phase-71 artifact schema).
- Whether AM29F040's sector-vs-chip erase is exercised as part of its Tier-3 cell or recorded as
  advisory (Flash AMD erase is part of VAL-03's algorithm surface).

### Deferred Ideas (OUT OF SCOPE)

- FM1608 byte-0 write bug — pre-existing parked debug item, out of v1.13 scope.
- Acquiring AT28C256 / AT29C040 / AM28F010 to lift their Tier-3 SKIP-deferred cells.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| VAL-01 | UV-EPROM family (`configure_eprom`, 0x07/0x08/0x0B) write + verify + chip-id + blank-check validated — pulse-delay retry loop convergence; 0x0B direct-VPE path distinct from 0x07/0x08 | Tier-1 + Tier-2 already GREEN (verified live). Tier-3: `dev validate-family eprom --board leonardo --chip W27C512 --source <file>`. |
| VAL-02 | 5V EEPROM family (`configure_eeprom28c`, 0x0D) — SDP-disable, 64-byte page write, DQ7 polling (AT28C256 rep) | Tier-1 + Tier-2 already GREEN. Tier-3: SKIP-deferred (no AT28C256 on hand). |
| VAL-03 | Flash AMD family (`configure_flash3`, 0x06) — write + sector/chip erase (AM29F040 rep) | Tier-1 + Tier-2 already GREEN. Tier-3: `dev validate-family flash3 --board leonardo --chip AM29F040 --source <file>`. |
| VAL-04 | Flash type-4 family (`configure_flash4`, 0x05/35/39) — write + verify (AT29C040 rep) | Tier-1 + Tier-2 already GREEN. Tier-3: SKIP-deferred (no AT29C040 on hand). |
| VAL-05 | Flash Intel family (`configure_flash_intel`, 0x10) — 12V P1 handling, status-register error branches (AM28F010 rep) | Tier-1 + Tier-2 already GREEN. Tier-3: SKIP-deferred (no AM28F010 on hand). |
| VAL-06 | SRAM family (`configure_sram`, 0x0E/27/28/29) — empty-no-op question resolved; matrix records table-stakes-PASS or FIX-01 defect | Tier-3 bench with FM1608 using two-pattern A→B method (D-05..D-09). Hard gate (D-09). |
</phase_requirements>

---

## Summary

Phase 73 is a **run phase, not a build phase**. Everything required to execute it was shipped in
Phase 71. The planner's job is to write plans that *invoke* the existing `dev validate-family`
runner with the correct arguments, verify the current Tier-1/Tier-2 software cells are still
GREEN (confirmed live below), run the three on-hand Tier-3 HIL cells on Leonardo, SKIP-defer
the three chipless families, and resolve VAL-06 using the FM1608 two-pattern method.

The board on `/dev/ttyACM0` is confirmed Leonardo (`controller: leonardo`, firmware `3.0.0b8`),
shield Rev 2.0, R1=270000 (within the ±25% band), R2=44000. This is the standing valid-PASS
configuration per the milestone precondition.

The SRAM handler (`sram.cpp:15-17`) is a confirmed one-liner no-op (configures nothing). The
Tier-1 suite documents this as a GREEN baseline for Phase 71. VAL-06 asks whether real FRAM
writes still persist despite the no-op configure — the firmware falls back to
`generic_memory_write_execute` for the MAIN phase, so bytes may or may not persist. The FM1608
two-pattern bench test provides the evidence.

**Primary recommendation:** For each of the 3 on-hand families, invoke
`firestarter -p /dev/ttyACM0 dev validate-family <family> --board leonardo --chip <chip> --source <image> --output-dir <dir>`. For chipless families, invoke with no `--board/--chip/--source` to auto-emit SKIP-deferred. For VAL-06, drive the two-pattern FM1608 sequence manually (write+read-back × 2 distinct patterns) and record the per-byte verdict into the matrix artifact.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Tier-1 native suite execution | Firmware (PlatformIO native) | — | `pio test -e native` runs on-host; no board needed |
| Tier-2 host wire round-trip | Host Python (pytest) | — | `fake_serial` / `make_comm` — no port needed |
| Tier-3 HIL bench run | Host Python CLI → Leonardo | Arduino firmware | `dev validate-family` drives the board over USB |
| Matrix artifact emission | Host Python CLI | — | `_write_artifact()` in `cli_handlers.py` emits JSON+MD |
| Non-vacuous oracle | Host Python CLI | — | `_classify_sha_result()` + `write_cycle_eprom` return code |
| SRAM no-op verdict | Host Python CLI + bench | Leonardo firmware | Two-pattern FM1608 write+read-back; per-byte analysis |
| R1 precondition | Host config layer | Arduino EEPROM | `config_manager.get_value("r1")` gates before any cycle |
| Controller identity | Host firmware.py | — | `firestarter fw` or `firestarter config` reads board name |

---

## Standard Stack

This phase installs **zero new packages**. All tooling is already present.

### Core (already installed, no changes needed)

| Tool | Version | Purpose |
|------|---------|---------|
| `firestarter` CLI | 3.0.0b8 | `dev validate-family` runner, `dev write-cycle`, `config`, `hw` |
| `pytest` | existing | Tier-2 wire round-trip test runner |
| `pio test -e native` | existing | Tier-1 native Unity suite runner |
| `/dev/ttyACM0` | — | Leonardo on USB passthrough (confirmed) |

### Package Legitimacy Audit

No packages installed this phase.

---

## The `dev validate-family` Invocation Contract

[VERIFIED: direct code read of `firestarter_app/firestarter/cli_handlers.py:1417-1591`]

### Full command signature

```bash
firestarter [-p <port>] dev validate-family \
    <family> \
    [--board <board>] \
    [--chip <chip-override>] \
    [--source <path-to-binary>] \
    [--output-dir <dir>]
```

**`<family>`** accepts: `eprom | eeprom28c | flash3 | flash4 | flash_intel | sram | all`

**SKIP-deferred path (D-06):** If any of `--board`, `--chip`, `--source` is absent, OR if the
configured port is absent, the runner auto-emits SKIP-deferred cells for all targeted families
and exits 0. This is how chipless families (AT28C256, AT29C040, AM28F010) get recorded.

**Hardware path:** All four must be present (port in config + `--board` + `--chip` + `--source`).

### Per-family canonical invocations

```bash
# Confirm Tier-1/Tier-2 still GREEN (no hardware needed):
pio test -e native -f "test_val_*"            # all 6 Tier-1 suites
cd firestarter_app && pytest tests/test_val_wire_*.py  # all 6 Tier-2 suites

# VAL-01 (eprom / W27C512 — Tier-3 HIL):
firestarter -p /dev/ttyACM0 dev validate-family eprom \
    --board leonardo --chip W27C512 \
    --source <image.bin> --output-dir val-eprom/

# VAL-03 (flash3 / AM29F040 — Tier-3 HIL):
firestarter -p /dev/ttyACM0 dev validate-family flash3 \
    --board leonardo --chip AM29F040 \
    --source <image.bin> --output-dir val-flash3/

# VAL-02 (eeprom28c / AT28C256 — SKIP-deferred, no chip):
firestarter -p /dev/ttyACM0 dev validate-family eeprom28c --output-dir val-eeprom28c/
# OR (equivalent — missing --board/--chip/--source triggers SKIP):
firestarter dev validate-family eeprom28c --output-dir val-eeprom28c/

# VAL-04 (flash4 / AT29C040 — SKIP-deferred):
firestarter dev validate-family flash4 --output-dir val-flash4/

# VAL-05 (flash_intel / AM28F010 — SKIP-deferred):
firestarter dev validate-family flash_intel --output-dir val-flash_intel/
```

**VAL-06 (SRAM / FM1608)** does NOT use `dev validate-family` directly because the standard
runner calls `write_cycle_eprom` which calls `erase_eprom` first — and FM1608 (FRAM) has no
erase step. The plan must use `dev write-cycle` (or raw write + read commands) to perform the
two-pattern sequence manually and then record the verdict into the matrix artifact. See
"VAL-06 FM1608 Two-Pattern Method" below.

### What the runner does internally

1. Loads `tools/validation_matrix_spec.json` (spec path: `firestarter_app/tools/validation_matrix_spec.json`).
2. Filters families by `<family>` arg.
3. Checks: port in config AND `--board` AND `--chip` AND `--source` all present → hardware path.
   If any missing → `_emit_skip_deferred_artifact()` → exits 0.
4. Checks `--board == "uno328pb"` → emits N/A cells, exits 0.
5. Reads `r1` from `config_manager.get_value("r1", None)`. If not None and out of band → exits 2.
   **Note:** `r1` is only in local config.json if previously set there. The live R1=270000
   (from `firestarter config`) does NOT automatically populate `~/.firestarter/config.json`.
   The plan must either: (a) run `firestarter config` to visually confirm R1≈270000 as a
   precondition check, or (b) run `firestarter config -r1 270000` to persist r1 into local
   config so the precondition gate fires.
6. Calls `write_cycle_eprom(rep_chip, eprom_data, source_image_path=source, runs=1, output_dir=...)`.
7. Maps verdict_int (0/1/2) to cell verdict (PASS/FAIL/SKIP-deferred).
8. Determines `pass_type`: "authoritative" for Leonardo, "advisory" for others.
9. Records `evidence_sha = sha256(source_image_path)` and `retry_count=1`.
10. Calls `_write_artifact(cells, output_dir)` → emits `<output_dir>/validation-matrix.json` +
    `<output_dir>/validation-matrix.md`.

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | PASS (or SKIP-deferred / N/A — all non-error) |
| 1 | FAIL (write_cycle_eprom returned 1 = SHA mismatch) |
| 2 | hw-error (write_cycle_eprom returned 2 = erase/write/read-back failure) OR r1 out of band |

---

## Validation Matrix Spec + Results Schema

[VERIFIED: direct read of `firestarter_app/tools/validation_matrix_spec.json`]

### Authored spec (input, hand-maintained)

**Path:** `firestarter_app/tools/validation_matrix_spec.json`

Per-family structure:

```json
{
  "id": "eprom",
  "handler": "configure_eprom",
  "protocols": [7, 8, 11],
  "rep_chip": "W27C512",
  "tier3": {
    "test_chip": "W27C512",
    "boards": ["leonardo"],
    "skip_boards": ["uno328pb"]
  }
}
```

**Representative chips per family (from spec):**

| Family id | Handler | Rep chip (spec) | Tier-3 chip (D-01/D-02) |
|-----------|---------|-----------------|------------------------|
| `eprom` | `configure_eprom` | W27C512 | W27C512 (on hand) |
| `eeprom28c` | `configure_eeprom28c` | AT28C256 | SKIP-deferred (no chip) |
| `flash3` | `configure_flash3` | AM29F040 | AM29F040 (on hand) |
| `flash4` | `configure_flash4` | AT29C040 | SKIP-deferred (no chip) |
| `flash_intel` | `configure_flash_intel` | AM28F010 | SKIP-deferred (no chip) |
| `sram` | `configure_sram` | 6116 | FM1608 (on hand, via --chip override) |

**Important for SRAM:** The spec's `rep_chip` is `"6116"` but D-05 uses FM1608. The `--chip FM1608`
override replaces the spec's rep chip. FM1608 algorithm is 0x28 (decimal 40) — within SRAM family
protocols {0x0E/14, 0x27/39, 0x28/40, 0x29/41}. [VERIFIED: chip_database.json entry for FM1608:
`"algorithm": 40`, `"support_status": "supported"`, `"pinout": "DIP28_JEDEC_SRAM_8K"`]

### Emitted results artifact (output, generated)

**Path:** `<output_dir>/validation-matrix.json` and `<output_dir>/validation-matrix.md`

**Per-cell schema:**

```json
{
  "family": "eprom",
  "board": "leonardo",
  "tier": 3,
  "verdict": "PASS",
  "pass_type": "authoritative",
  "evidence_sha": "<sha256-of-source-image>",
  "retry_count": 1
}
```

SKIP-deferred cells omit `pass_type`:
```json
{
  "family": "eeprom28c",
  "board": "leonardo",
  "tier": 3,
  "verdict": "SKIP-deferred",
  "reason": "no chip on hand",
  "evidence_sha": null,
  "retry_count": 0
}
```

**Top-level artifact wrapper:**
```json
{
  "generated": "<ISO8601 UTC>",
  "harness_version": "71",
  "cells": [...]
}
```

**Fields:** `family` (string), `board` (string), `tier` (int), `verdict`
(`"PASS"` / `"FAIL"` / `"SKIP-deferred"` / `"N/A"`), `pass_type` (`"authoritative"` /
`"advisory"`), `evidence_sha` (sha256 hex or null), `retry_count` (int).

**Where are Tier-1 and Tier-2 cells?** The emitted artifact only records Tier-3 cells (the `dev
validate-family` runner only emits Tier-3). Tier-1 and Tier-2 are confirmed by running the native
and pytest suites; their GREEN status is documented in the plan's verification log, not in the
matrix artifact JSON.

---

## The Non-Vacuous PASS Oracle (Phase 71 D-08)

[VERIFIED: `cli_handlers.py:1388-1409`, `eprom_operations.py:766-873`, `tests/test_validate_oracle.py`]

### What "non-vacuous" means

A PASS is only valid if:
1. **Independent post-write full read + SHA compare** — `write_cycle_eprom` writes the source
   image, then reads the whole chip back and computes SHA-256. The compare is `readback_sha ==
   source_sha` inside `write_cycle_eprom`. The runner calls `write_cycle_eprom` and trusts its
   return code directly (0 = PASS) — it does NOT re-compare source vs. source. [VERIFIED:
   `cli_handlers.py:1555-1573` comments: "The real readback compare already happened inside
   write_cycle_eprom."]
2. **Leonardo-authoritative** — only `board == "leonardo"` yields `pass_type = "authoritative"`.
   All others yield "advisory". [VERIFIED: `cli_handlers.py:1560-1561`]
3. **Passing negative control** — the oracle is proven non-vacuous by the test in
   `tests/test_validate_oracle.py:TestNegativeControl.test_classify_sha_mismatch_is_fail_on_leonardo`:
   `_classify_sha_result(wrong_sha, source_sha, "leonardo")` returns `"FAIL"` (not `"PASS"`).
   For the bench plan: a deliberate wrong-file verify step (or a verify on a blank chip) must
   also be demonstrated to return FAIL — confirming the oracle can distinguish a bad write from a
   good one.
4. **Retry-count capture** — `retry_count` is recorded in each cell (`1` for a single run from
   `dev validate-family`). The D-07 N≥2 confirm for FM1608 is done at the plan level by running
   the sequence twice; the matrix records the final verdict.
5. **Live R1/R2 precondition** — `r1 ≈ 270000 ±25%` gate fires before any cycle. Currently
   R1=270000 confirmed via `firestarter config`. The plan must persist r1 into local config or
   verify it live before each Tier-3 task.
6. **uno328pb hard N/A** — `board == "uno328pb"` → N/A cell, no cycle attempted. [VERIFIED:
   `cli_handlers.py:1480-1497`]

### R1 precondition practical notes

`config_manager.get_value("r1", None)` reads from `~/.firestarter/config.json`. Currently that
file only has `"port": "/dev/ttyACM0"` — no `r1` key. So the precondition gate is **currently
skipped** (r1_raw is None → check not triggered). To arm the gate, run:

```bash
firestarter -p /dev/ttyACM0 config -r1 270000  # sets r1=270000 in Arduino EEPROM + local config
```

OR just use `firestarter config` (no args) to display current R1 and verify manually before
running `dev validate-family`. The plan should document whichever approach is used.

### Negative control bench procedure

For each Tier-3 HIL run, add a deliberate mismatch step:

```bash
# After a successful write, verify against a wrong file:
firestarter -p /dev/ttyACM0 verify W27C512 <wrong_file.bin>
# Expected: exits non-zero (verify FAIL) — this is the passing negative control
```

The plan must record this FAIL result as evidence that verify CAN fail.

---

## write_cycle_eprom and Cycle Methods

[VERIFIED: `firestarter_app/firestarter/eprom_operations.py:766-873`]

`write_cycle_eprom(eprom_name, eprom_data_dict, source_image_path, runs=1, ...)`:
- Loop `runs` times:
  1. `erase_eprom(...)` → sends `COMMAND_ERASE` to firmware; returns bool.
  2. `write_eprom(...)` → sends `COMMAND_WRITE` to firmware; returns bool.
  3. Read-back via `COMMAND_READ` + `_run_state_machine`.
  4. SHA-256 compare: `readback_sha == source_sha` → returns 0 (PASS), 1 (mismatch), 2 (hw-error).

**For W27C512 (0x07 EEPROM):**
- Step 1 sends `COMMAND_ERASE` → firmware `configure_eprom:CMD_ERASE` →
  `eprom_erase_execute` → `eprom_internal_erase` (drives VPP at 12V, A9/OE high) — works
  unconditionally. [VERIFIED: `eprom.cpp:88-91`]
- The `-b` flag (skip blank check) is NOT needed for `write_cycle_eprom` because it calls
  `erase_eprom` first (explicit erase step), then `write_eprom`. The standalone
  `firestarter write W27C512 <file>` command needs `-b` for a non-blank chip because it only
  auto-erases if `FLAG_CAN_ERASE` is set — and `FLAG_CAN_ERASE` is NOT set in the DB for
  W27C512 (info-flags: 0x0). But `write_cycle_eprom` calls erase explicitly. [ASSUMED: the
  erase step in `write_cycle_eprom` handles the W27C512 pre-erase correctly; bench will confirm]

**For AM29F040 (0x06 Flash):**
- Erase is handled by `flash3_erase_execute`. The `flash3_write_init` auto-erase is gated on
  `FLAG_CAN_ERASE` (not set for AM29F040 in DB). But `write_cycle_eprom` calls `erase_eprom`
  (standalone COMMAND_ERASE) which routes to `flash3_erase_execute` unconditionally. Erase
  should succeed. [ASSUMED: flash3 standalone erase path works; bench will confirm]

**For FM1608 (0x28 SRAM/FRAM):**
- `write_cycle_eprom` calls `erase_eprom` first. `configure_sram:CMD_ERASE` behavior is
  unknown — sram.cpp is a one-liner no-op. This may cause `erase_eprom` to return False or
  succeed vacuously. **The VAL-06 test uses a different approach** (see below) to avoid the
  erase step.

---

## VAL-06 FM1608 Two-Pattern Method

[Derived from D-05..D-09 in CONTEXT.md + `sram.cpp:15-17`]

The standard `dev validate-family sram` runner calls `write_cycle_eprom` which includes an
`erase_eprom` step — FRAM chips have no erase operation, so this may fail. The plan must use a
**direct write → read-back sequence** to test SRAM persistence, bypassing the erase step.

### Approach: `dev write-cycle` with FLAG_SKIP_ERASE equivalent or raw write

The `dev write-cycle` command (`cli_handlers.py:1137-1187`) also calls `write_cycle_eprom`.
To skip the erase step, the plan needs to use `firestarter write` (which skips blank-check and
erase when `--no-blank-check` / `-b` is passed) followed by `firestarter read` + `firestarter
verify`.

**Two-pattern procedure (D-06, D-07, D-08):**

```bash
# Step 1: Read initial baseline
firestarter -p /dev/ttyACM0 read FM1608 --output baseline.bin

# Step 2: Write pattern A (non-trivial, e.g. 0x5A repeating for 8KB)
# Create pattern A:
python3 -c "import sys; sys.stdout.buffer.write(bytes([0x5A]*8192))" > pattern_a.bin
firestarter -p /dev/ttyACM0 write FM1608 pattern_a.bin -b  # -b = skip blank check

# Step 3: Read back and compare
firestarter -p /dev/ttyACM0 read FM1608 --output readback_a.bin
sha256sum pattern_a.bin readback_a.bin  # must match for persistence

# Step 4: Verify against wrong file (negative control)
firestarter -p /dev/ttyACM0 verify FM1608 baseline.bin  # must FAIL

# Step 5: Write pattern B (non-trivial, e.g. 0xA5 repeating)
python3 -c "import sys; sys.stdout.buffer.write(bytes([0xA5]*8192))" > pattern_b.bin
firestarter -p /dev/ttyACM0 write FM1608 pattern_b.bin -b

# Step 6: Read back and compare
firestarter -p /dev/ttyACM0 read FM1608 --output readback_b.bin
sha256sum pattern_b.bin readback_b.bin

# Step 7: Repeat for N≥2 (D-07) to avoid contact-fault false negative
# (Repeat Steps 2-6 for the second run)

# Step 8: Per-byte verdict (D-08)
python3 -c "
a = open('readback_a.bin','rb').read(); p = open('pattern_a.bin','rb').read()
mismatches = [i for i,(x,y) in enumerate(zip(a,p)) if x!=y]
if not mismatches: print('ALL bytes match — persistence confirmed (VAL-06 PASS)')
elif mismatches == [0]: print('Only byte-0 mismatches — parked FRAM bug (VAL-06 PASS, byte-0 is separate bug)')
else: print(f'{len(mismatches)} bytes fail including non-byte-0 — FIX-01 DEFECT: {mismatches[:10]}')
"
```

**Note on FM1608 database entry:** `algorithm=40` (0x28), `support_status=supported`,
`pinout=DIP28_JEDEC_SRAM_8K`. The chip resolves via `resolve_chip("FM1608", db=app.db)` without
issues. [VERIFIED: chip_database.json entry]

**Note on `dev validate-family sram --chip FM1608`:** Because `write_cycle_eprom` includes
`erase_eprom` which sends `COMMAND_ERASE` to `configure_sram`, and `sram.cpp` is a no-op (wires
no `CMD_ERASE` handler), the erase will likely succeed vacuously (no-op) or fail with a hw-error
depending on firmware error handling. The plan must test this flow and record the actual behavior.
If `erase_eprom` returns True (no-op success), `write_cycle_eprom` may actually work for FM1608.
[ASSUMED: sram.cpp CMD_ERASE path behavior; bench determines actual behavior]

---

## Tier-1 Recording Bus Stub (VPP Assertion)

[VERIFIED: `firestarter/test/native/avr/_shared/host_stubs_common.inc:54-80`]

The recording bus stub is activated by `#define HOST_STUBS_RECORD_BUS` before including
`host_stubs_common.inc`. It captures every `rurp_write_to_register(reg, data)` call into a
circular buffer `s_bus_recording[256]`.

**API exposed to native test suites:**
```c
extern "C" void clear_bus_recording();
extern "C" int  bus_recording_count();
extern "C" uint8_t recorded_reg(int i);   // register ID
extern "C" uint8_t recorded_data(int i);  // data byte written
```

**VPP assertion backing D-11:** The Tier-1 eprom suite (`test_val_eprom.cpp`) uses this to
prove `CTRL_VPP_REGULATOR_ENABLE` (0x80) is set during a configure_eprom write configure call
and NOT set during a read configure call. This provides software proof of the VPP register-write
sequence without requiring a multimeter dry-run. The Tier-1 eprom tests are already GREEN
(verified live: all 6 `test_val_eprom` tests PASSED).

**How to invoke:** `pio test -e native -f "test_val_eprom"` (or `test_val_*` for all families).

---

## Bench-Driving Mechanics

[VERIFIED: live hardware state confirmed 2026-06-17 via devcontainer USB passthrough]

### Current bench state (confirmed live)

```
Port:       /dev/ttyACM0
Controller: leonardo (confirmed via `firestarter fw`)
Firmware:   3.0.0b8
Shield:     Rev 2.0 (confirmed via `firestarter hw`)
R1:         270000 (within ±25% band; confirmed via `firestarter config`)
R2:         44000
```

### Port identity verification (per D-03)

At each task start:
```bash
firestarter -p /dev/ttyACM0 fw  # must show "controller: leonardo"
```
ACM port numbers shuffle on USB unplug/replug. Never assume `/dev/ttyACM0` == Leonardo between
tasks without re-verifying.

### Sideload (only if needed — NOT needed for Phase 73)

Phase 73 adds zero production firmware flash. No sideload needed. But if a sideload ever is
required:
- **Leonardo is chip-OUT-EXEMPT** — no chip removal needed before sideload (per memory
  `feedback_chip_out_before_sideload`).
- Uno-class boards (Uno, uno328pb) require chip-OUT before sideload — NOT applicable here.

### W27C512 specific gotchas

- **Erase unsupported on the 0x07 write-path** — `FLAG_CAN_ERASE` is not set in the DB for
  W27C512, so `firestarter write W27C512 <file>` will NOT auto-erase before writing. Use `-b`
  flag (`--no-blank-check`) to skip the blank-check gate when chip is not blank.
- **`write_cycle_eprom` (used by `dev validate-family`) calls `erase_eprom` explicitly**, so
  the chip's prior state doesn't matter — erase fires before write.
- **12V VPP** — W27C512 erase uses 12V VPP (A9/OE-VPP high rail per `eprom_internal_erase`).
  EVEN-01-proven clean on Leonardo with Rev 2.0. No multimeter dry-run needed per D-11.
- **64KB chip** — source image must be exactly 65536 bytes for a clean SHA compare.

### AM29F040 specific gotchas

- **512KB chip** — source image must be 524288 bytes.
- **Flash3 sector-erase** — `configure_flash3:CMD_ERASE` routes to `flash3_erase_execute` which
  does sector erase by default. The chip erases BEFORE write in the `write_cycle_eprom` flow
  (via `erase_eprom`). This is expected and correct.
- **No VPP** — AM29F040 is 5V-only Flash. No VPP-related preconditions needed.

### FM1608 specific gotchas

- **FRAM (non-volatile)** — data persists without power. This is what makes the two-pattern test
  clean (no volatility confound).
- **8KB chip** — algorithm 0x28 (SRAM family), `DIP28_JEDEC_SRAM_8K` pinout. Source images
  must be 8192 bytes.
- **No VPP** — FM1608 operates at 5V. No VPP-related preconditions.
- **Byte-0 bug** — a pre-existing, parked FRAM write bug affects byte 0. Per D-08, this does
  NOT constitute a VAL-06 failure if bytes 1..N persist correctly.
- **No erase** — FRAM cells rewrite directly. Using `firestarter write FM1608 <file> -b` (skip
  blank check + no auto-erase) is the correct path. Using `dev validate-family` or `dev
  write-cycle` risks a spurious `erase_eprom` call.

---

## Architecture Patterns

### Validation run structure

```
Plan per family (6 plans or 3 on-hand + 3 skip-deferred)
    ↓
Tier-1 confirm: pio test -e native -f "test_val_<family>"    # re-confirm GREEN
    ↓
Tier-2 confirm: pytest tests/test_val_wire_<family>.py       # re-confirm GREEN
    ↓
Tier-3 HIL (on-hand families only):
    verify-port identity → live R1 readback → negative control proof
    → dev validate-family <family> --board leonardo --chip <chip> --source <img>
    → inspect output-dir/validation-matrix.json → record verdict
    ↓
Tier-3 SKIP-deferred (chipless families):
    dev validate-family <family> [no hardware args] --output-dir <dir>
    → artifact emitted with SKIP-deferred cells
```

### System Architecture Diagram

```
Operator actions (physical only)
  → chip insertion / removal → bench ready
            ↓
Claude (devcontainer) → firestarter CLI → /dev/ttyACM0
            ↓                                   ↓
  dev validate-family                    Leonardo (Rev 2.0)
  write_cycle_eprom                      configure_eprom / configure_flash3 / configure_sram
  write / read / verify                  register writes, VPP control
            ↓                                   ↓
  validation-matrix.{json,md}           chip responds (PASS / FAIL)
  (per-cell: verdict + evidence_sha
   + pass_type: authoritative)
```

### Recommended plan wave structure

**Suggested plan decomposition (6 plans → one per family):**

| Plan | Family | On-hand? | Action |
|------|--------|----------|--------|
| 73-01 | eprom (VAL-01) | W27C512 | Tier-1 + Tier-2 confirm GREEN + Tier-3 HIL |
| 73-02 | flash3 (VAL-03) | AM29F040 | Tier-1 + Tier-2 confirm GREEN + Tier-3 HIL |
| 73-03 | sram/VAL-06 | FM1608 | Tier-1 + Tier-2 confirm GREEN + Two-pattern FM1608 HIL |
| 73-04 | eeprom28c (VAL-02) | none | Tier-1 + Tier-2 confirm GREEN + SKIP-deferred emit |
| 73-05 | flash4 (VAL-04) | none | Tier-1 + Tier-2 confirm GREEN + SKIP-deferred emit |
| 73-06 | flash_intel (VAL-05) | none | Tier-1 + Tier-2 confirm GREEN + SKIP-deferred emit |

Or collapse into 2 plans (HIL families / SKIP-deferred families) + 1 VAL-06 plan. Planner's
discretion per plan granularity preferences.

### Recommended Project Structure (no new files needed)

```
firestarter_app/
├── tools/validation_matrix_spec.json   # authored input (DO NOT MODIFY — Phase 71 artifact)
└── [output-dir]/                        # created per run by the runner
    ├── validation-matrix.json           # emitted results artifact
    ├── validation-matrix.md             # human-readable table
    └── cycle_01_readback.bin            # write_cycle_eprom read-back

firestarter/
└── (no changes — Phase 73 adds zero production firmware flash)
```

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Write → read-back → SHA compare | Custom write+verify loop | `dev validate-family` / `write_cycle_eprom` | Already built, tested, non-vacuous oracle baked in |
| Matrix artifact emission | Custom JSON writer | `_write_artifact()` inside `dev validate-family` | Already emits both JSON and MD with correct schema |
| SKIP-deferred recording | Custom "skip" logic | Run `dev validate-family` with no `--board/--chip/--source` | Auto-emits SKIP-deferred cells and exits 0 (D-06) |
| VPP assertion proof | New hardware test | Tier-1 recording bus stub (already GREEN) | `host_stubs_common.inc` already captures register sequences |
| Negative control | New test framework | `firestarter verify <chip> <wrong_file>` | Standard CLI verify against wrong file = negative control proof |

---

## Common Pitfalls

### Pitfall 1: Using `-b` vs. not using `-b` for W27C512

**What goes wrong:** Running `firestarter write W27C512 <file>` on a non-blank chip without `-b`
fails blank-check because `FLAG_CAN_ERASE` is not set → chip never erases → blank-check fails
→ write aborted.
**Why it happens:** `info-flags: 0x0` for W27C512 in chip_database.json → `FLAG_CAN_ERASE` never
set → `eprom_write_init` never calls `eprom_internal_erase`.
**How to avoid:** Use `dev validate-family` (which calls `write_cycle_eprom` → `erase_eprom`
first) instead of standalone `write`. If using standalone `write`, always pass `-b`.
**Warning signs:** "Blank check failed" error on write.

### Pitfall 2: Assuming r1 is in local config.json

**What goes wrong:** `dev validate-family` silently skips the r1 precondition because
`config_manager.get_value("r1")` returns None (not in `~/.firestarter/config.json`).
**Why it happens:** `firestarter config` reads R1 from Arduino EEPROM and prints it but does NOT
auto-persist it to local config.json.
**How to avoid:** Either (a) run `firestarter config -r1 270000` to persist r1, or (b) use
`firestarter config` as a manual visual precondition check before `dev validate-family`.
**Warning signs:** `dev validate-family` runs without printing r1 precondition error even if
calibration is wrong.

### Pitfall 3: Using dev validate-family sram for FM1608 erase path

**What goes wrong:** `dev validate-family sram --chip FM1608` calls `write_cycle_eprom` which
calls `erase_eprom` first. `configure_sram` is a no-op — it may or may not error on
`CMD_ERASE`. If it errors, `write_cycle_eprom` returns 2 (hw-error), not 1 (mismatch), and the
cell is recorded as SKIP-deferred.
**Why it happens:** `sram.cpp:15-17` is a one-liner that wires nothing — no CMD_ERASE handler.
**How to avoid:** Use `firestarter write FM1608 <file> -b` (skips blank check, no auto-erase)
followed by `firestarter read FM1608` for the two-pattern test. Test whether the `erase_eprom`
step vacuously succeeds or fails before committing to a run structure.
**Warning signs:** `dev validate-family sram` exits 2 (hw-error) instead of 0 or 1.

### Pitfall 4: Port identity assumption after any USB replug

**What goes wrong:** `controller:` on `/dev/ttyACM0` is uno328pb, not Leonardo. Plan writes to
the wrong board.
**Why it happens:** ACM device numbers shuffle on USB unplug/replug.
**How to avoid:** Run `firestarter -p /dev/ttyACM0 fw` at the start of every task to confirm
`controller: leonardo`.
**Warning signs:** `firestarter hw` shows a different shield revision than expected.

### Pitfall 5: Vacuous PASS from wrong-file mismatch not demonstrated

**What goes wrong:** The oracle may not detect a no-op write (e.g., if configure_sram does
nothing, verify against source still shows "PASS" because the chip was already erased or has
random data that happens to match). Without a demonstrated negative control, a PASS is
uninformative.
**Why it happens:** configure_sram no-op means `write_eprom` may silently do nothing; if the
chip's contents happen to match the source, `verify` returns 0.
**How to avoid:** Always run a verify-against-wrong-file step and record its FAIL as the
negative control proof.
**Warning signs:** A PASS on the first run without any prior negative-control failure.

### Pitfall 6: FM1608 byte-0 confound misclassified as VAL-06 failure

**What goes wrong:** FM1608 bytes 1..N write correctly but byte 0 always reads back wrong. A
naive `sha256(readback) != sha256(source)` gives FAIL — but this is the PARKED byte-0 bug, not
the VAL-06 no-op question.
**Why it happens:** Pre-existing FRAM write issue at byte 0 (`.planning/debug/fm1608-fresh-chip-baseline.md`).
**How to avoid:** Apply per-byte verdict logic (D-08): compare bytes individually; if only byte 0
mismatches → VAL-06 table-stakes-PASS (configure_sram does write; byte-0 is a separate bug).
**Warning signs:** SHA mismatch with only 1 differing byte at offset 0.

---

## Runtime State Inventory

Not applicable — Phase 73 is purely a bench-run phase. No renaming, refactoring, or migration.
No stored data items change.

---

## Environment Availability

[VERIFIED: live check 2026-06-17 via devcontainer]

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `/dev/ttyACM0` | Tier-3 HIL | ✓ | — | — |
| Leonardo (controller) | Tier-3 HIL | ✓ | firmware 3.0.0b8 | — |
| Shield Rev 2.0 | Tier-3 HIL | ✓ | confirmed by `hw` cmd | — |
| R1=270000 | R1 precondition | ✓ | 270000 (live) | — |
| W27C512 chip | VAL-01 Tier-3 | ✓ (D-01) | — | — |
| AM29F040 chip | VAL-03 Tier-3 | ✓ (D-01) | — | — |
| FM1608 chip | VAL-06 Tier-3 | ✓ (D-05) | — | — |
| AT28C256 chip | VAL-02 Tier-3 | ✗ | — | SKIP-deferred (D-02) |
| AT29C040 chip | VAL-04 Tier-3 | ✗ | — | SKIP-deferred (D-02) |
| AM28F010 chip | VAL-05 Tier-3 | ✗ | — | SKIP-deferred (D-02) |
| Source images (binary files) | Tier-3 writes | needs creation | — | generate with python3 |
| `firestarter` CLI | all Tier-3 | ✓ | 3.0.0b8 | — |
| `pytest` | Tier-2 | ✓ | existing | — |
| `pio` (PlatformIO) | Tier-1 | ✓ | existing | — |

**All three Tier-1 on-hand suites currently PASS** (verified live: test_val_eprom PASSED,
test_val_flash3 PASSED, test_val_sram PASSED).

**All six Tier-2 suites currently PASS** (verified live: 26 tests PASSED).

**Missing dependencies with no fallback:** None — all critical dependencies are available.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Tier-1 Framework | PlatformIO Unity (`pio test -e native`) |
| Tier-2 Framework | pytest |
| Tier-1 run command | `cd firestarter && pio test -e native -f "test_val_<family>"` |
| Tier-2 run command | `cd firestarter_app && pytest tests/test_val_wire_<family>.py -v` |
| Full Tier-1 suite | `pio test -e native` |
| Full Tier-2 suite | `pytest tests/` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | Status |
|--------|----------|-----------|-------------------|--------|
| VAL-01 | eprom Tier-1 register-sequence GREEN | native Unity | `pio test -e native -f "test_val_eprom"` | ✓ PASS (live) |
| VAL-01 | eprom Tier-2 wire round-trip GREEN | pytest | `pytest tests/test_val_wire_eprom.py` | ✓ PASS (live) |
| VAL-01 | eprom Tier-3 HIL PASS + negative control | bench | `dev validate-family eprom --board leonardo ...` | Pending Phase 73 |
| VAL-02 | eeprom28c Tier-1 GREEN | native Unity | `pio test -e native -f "test_val_eeprom28c"` | ✓ PASS (live) |
| VAL-02 | eeprom28c Tier-2 GREEN | pytest | `pytest tests/test_val_wire_eeprom28c.py` | ✓ PASS (live) |
| VAL-02 | eeprom28c Tier-3 SKIP-deferred | bench | `dev validate-family eeprom28c` (no hw args) | Pending Phase 73 |
| VAL-03 | flash3 Tier-1 GREEN | native Unity | `pio test -e native -f "test_val_flash3"` | ✓ PASS (live) |
| VAL-03 | flash3 Tier-2 GREEN | pytest | `pytest tests/test_val_wire_flash3.py` | ✓ PASS (live) |
| VAL-03 | flash3 Tier-3 HIL PASS + negative control | bench | `dev validate-family flash3 --board leonardo ...` | Pending Phase 73 |
| VAL-04 | flash4 Tier-1 GREEN | native Unity | `pio test -e native -f "test_val_flash4"` | ✓ PASS (live) |
| VAL-04 | flash4 Tier-2 GREEN | pytest | `pytest tests/test_val_wire_flash4.py` | ✓ PASS (live) |
| VAL-04 | flash4 Tier-3 SKIP-deferred | bench | `dev validate-family flash4` (no hw args) | Pending Phase 73 |
| VAL-05 | flash_intel Tier-1 GREEN | native Unity | `pio test -e native -f "test_val_flash_intel"` | ✓ PASS (live) |
| VAL-05 | flash_intel Tier-2 GREEN | pytest | `pytest tests/test_val_wire_flash_intel.py` | ✓ PASS (live) |
| VAL-05 | flash_intel Tier-3 SKIP-deferred | bench | `dev validate-family flash_intel` (no hw args) | Pending Phase 73 |
| VAL-06 | sram Tier-1 GREEN (no-op documented) | native Unity | `pio test -e native -f "test_val_sram"` | ✓ PASS (live) |
| VAL-06 | sram Tier-2 GREEN (dispatch safety) | pytest | `pytest tests/test_val_wire_sram.py` | ✓ PASS (live) |
| VAL-06 | sram Tier-3 FM1608 two-pattern verdict | bench | `firestarter write FM1608 ... -b` × 2 patterns | Pending Phase 73 |

### Wave 0 Gaps

None — test infrastructure exists and is GREEN. No new test files needed for Phase 73.
Phase 73 drives the existing infrastructure; it does not add new tests.

---

## Security Domain

Phase 73 is bench-validation only — it runs existing code against real hardware, no new
production code paths opened. The oracle preconditions (R1≈270000, Leonardo-only-PASS,
uno328pb-N/A) are the relevant safety controls, already implemented in Phase 71.

ASVS not applicable to a bench-run phase. The `FLAG_CAN_ERASE` / VPP safety invariants are
verified by the Tier-1 recording-bus tests (already GREEN) not by new code in this phase.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `write_cycle_eprom`'s `erase_eprom` step handles W27C512 pre-erase correctly (erase fires, chip accepts it, write succeeds) | Cycle Methods | If erase returns failure, `dev validate-family eprom` exits 2 (hw-error); would require using standalone write with `-b` instead |
| A2 | `configure_sram:CMD_ERASE` silently no-ops (returns ok) rather than erroring | FM1608 method | If it errors, `write_cycle_eprom` returns 2 for FM1608; `dev write FM1608 -b` is the fallback |
| A3 | AM29F040 standalone `erase_eprom` (COMMAND_ERASE → flash3_erase_execute) succeeds when called from `write_cycle_eprom` | Cycle Methods | If chip-erase fails, `dev validate-family flash3` exits 2; would need to investigate flash3 CMD_ERASE |
| A4 | FM1608 bytes 1..N actually persist data (FRAM write path through generic_memory_write_execute) despite `configure_sram` being a no-op | VAL-06 | If firmware write path is also a no-op (no op pointer wired), ALL bytes fail → FIX-01 defect |

---

## Open Questions

1. **Does `configure_sram:CMD_ERASE` succeed or error for FM1608?**
   - What we know: `sram.cpp` is a pure no-op (no CMD_ERASE handler wired).
   - What's unclear: Does the firmware return OK or ERROR for an unhandled CMD on a no-op handler?
   - Recommendation: Try `firestarter erase FM1608` first (before the two-pattern test) and note
     the exit code. This determines whether `write_cycle_eprom` is usable for FM1608.

2. **Does FM1608 write path (generic_memory_write_execute) actually write bytes?**
   - What we know: `configure_sram` wires no `firestarter_operation_main`. The MAIN phase in
     `_run_state_machine` may fire the generic write handler or fail with no-op.
   - What's unclear: Does firmware's generic memory write execute fire when no init/main are wired?
   - Recommendation: This is exactly what VAL-06 resolves empirically. The two-pattern test is
     the answer.

---

## Sources

### Primary (HIGH confidence)

- `firestarter_app/firestarter/cli_handlers.py:1257-1591` — `dev validate-family` implementation
- `firestarter_app/firestarter/eprom_operations.py:766-873` — `write_cycle_eprom` implementation
- `firestarter_app/tools/validation_matrix_spec.json` — authored matrix spec with rep chips
- `firestarter/test/native/avr/_shared/host_stubs_common.inc:54-80` — recording bus stub
- `firestarter/src/proms/sram.cpp:15-17` — configure_sram no-op confirmed
- `firestarter/src/proms/eprom.cpp:88-106` — eprom_erase_execute + eprom_write_init FLAG_CAN_ERASE
- `firestarter/src/proms/flash_type_3.cpp:31-90` — configure_flash3 CMD_ERASE path
- `firestarter_app/firestarter/data/chip_database.json` — W27C512, AM29F040, FM1608, 6116 entries
- `firestarter_app/tests/test_validate_oracle.py` — oracle / negative control tests
- `firestarter_app/firestarter/firmware.py:100-130` — controller identity reporting

### Secondary (MEDIUM confidence)

- `.planning/phases/73-bench-validate-the-6-families-on-leonardo-hybrid-gated/73-CONTEXT.md` —
  D-01..D-15 locked decisions
- `.planning/phases/71-validation-harness-matrix/71-CONTEXT.md` — D-05/D-06/D-08 oracle decisions
- `.planning/v1.13-PROTOCOL-ENUMERATION.md` — Phase 72 findings (erase gap, SRAM routing)
- Live bench verification: `firestarter fw`, `firestarter hw`, `firestarter config` — 2026-06-17

### Tertiary (LOW confidence)

- None

---

## Metadata

**Confidence breakdown:**
- Invocation contract: HIGH — read directly from source
- Matrix schema: HIGH — read directly from source
- Oracle mechanics: HIGH — read directly from source + tests
- FM1608 behavior: ASSUMED — empirically unknown until bench run
- Bench state: HIGH — verified live 2026-06-17

**Research date:** 2026-06-17
**Valid until:** 30 days (stable harness code; bench state may change if hardware is moved)

---

## RESEARCH COMPLETE

Phase 73 is a **pure invocation phase** — the harness, oracle, matrix spec, and artifact schema
are all confirmed present and GREEN (Tier-1: 6/6 native suites PASSED; Tier-2: 26/26 pytest
tests PASSED). The board state is confirmed (Leonardo on `/dev/ttyACM0`, R1=270000, Rev 2.0).
The planner has a complete invocation contract: exact CLI commands per family, the SKIP-deferred
auto-path for chipless families, the two-pattern FM1608 procedure for VAL-06, and the negative
control step required per cell.
