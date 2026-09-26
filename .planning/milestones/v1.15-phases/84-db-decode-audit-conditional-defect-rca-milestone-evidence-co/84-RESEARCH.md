# Phase 84: DB Decode Audit + Conditional Defect RCA + Milestone Evidence Consolidation - Research

**Researched:** 2026-06-24
**Domain:** Arduino C++ firmware (PlatformIO) VPP-gate logic + Python host CLI (DB codegen, blank-check path, diff/dispatch gates); dual-repo lockstep
**Confidence:** HIGH (all touch points read directly in the submodule source this session)

## Summary

Phase 84 is a tightly scoped firmware+host change phase closing milestone v1.15. All four technical
investigations resolved to **specific functions and line references** in the live submodule source.
The load-bearing findings:

1. **VPP-skip gate (D-11):** the chip-1 read refusal and benign VPP warnings come from a single
   firmware function — `eprom_check_vpp()` in `firestarter/src/proms/eprom.cpp:209`, invoked
   unconditionally by `eprom_generic_init()` (`eprom.cpp:290`), which is the default
   `firestarter_operation_init` for **every** eprom command including `CMD_READ` and
   `CMD_BLANK_CHECK`. `handle->cmd` is in scope at that point, so the cleanest gate is **operation-type
   keyed**: skip the VPP check (and its regulator-enable side effect) when `handle->cmd` is `CMD_READ`
   or `CMD_BLANK_CHECK`. Host parity lives in `firestarter_app/firestarter/eprom_operations.py` but is
   thinner than expected — the host does not run its own VPP gate; it surfaces the firmware's
   ERROR/WARNING verbatim. The real "parity" obligation is the constant/flag-bit duplication rule.

2. **DB relabel (D-40) — the relabel is NOT label-only as written; STOP-and-resurface risk is real.**
   `FLAG_CAN_ERASE` is set in `firestarter_app/firestarter/database.py:605` **directly from**
   `electrical.type ∈ {"EEPROM","Flash/EEPROM"}`. Relabeling **SST39SF040 `Flash/EEPROM`→`Flash`
   FLIPS `FLAG_CAN_ERASE` OFF** — precisely the Phase-77 auto-erase perturbation D-40 forbids. The
   FM1608 `SRAM`→`FRAM` relabel does NOT touch CAN_ERASE but DOES flip the VPP-display gate
   (`eprom_info.py:395`, `ic_layout.py:393`) from hidden to shown. Additionally, **`diff_db.py` will
   classify a type-only change as `unexplained` → exit 1 (BLOCK)** unless a new root-cause rule is added.

3. **FM1608 blank-check "Empty input" (D-30):** "Empty input" is firmware message `0xA4`
   `MSG_ERR_EMPTY_INPUT` (`messages.py:437`, codegen mirror of the firmware catalog). FM1608 routes via
   `configure_sram()` which is a **no-op stub** (`sram.cpp:15`), and `configure_memory()` sets
   `firestarter_operation_main` only for READ/WRITE/VERIFY — so a SRAM/FRAM **blank-check has a NULL
   main op**. The fix is host-side (detect SRAM/FRAM and skip/short-circuit blank-check); FM1608 already
   PASSed its write via `write -b`, so this is tooling polish.

4. **Conditional defect RCA (D-31):** AM27C020 (0x08, DIP32) write uses `configure_eprom`'s
   P1-as-VPP path (`eprom.cpp` + `memory_utils.h:24`); the "0 bits programmed" signature is the
   32-pin Large-EPROM VPP route. W29C040 flash4 (`flash_type_4.cpp:27`) page size is a **capacity
   heuristic** that already returns 256 for W29C040 (524288 > 262144) — so the CR-01 datasheet-page
   todo would NOT change W29C040's page size; the re-bench tests whether 256B page handling actually
   works on silicon, or whether the fault is deeper (SDP/poll/VPP). Both are RCA-and-defer.

**Primary recommendation:** Gate the firmware VPP check on `handle->cmd ∈ {CMD_READ, CMD_BLANK_CHECK}`
inside `eprom_generic_init` (cleanest, no new flag bit, preserves host↔firmware parity). For the DB
relabel, treat **SST39SF040 as a STOP-or-redesign case** (the `Flash` label drops CAN_ERASE) and
**FM1608 as a label-only-for-CAN_ERASE-but-VPP-display-changing case** — plan a `diff_db.py` rule + a
pinning test, and surface the CAN_ERASE collision to the operator per D-40 before shipping.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| VPP error/warning gate | Firmware (`eprom.cpp`) | Host (constant parity only) | Voltage is measured + judged on the Arduino; host only relays the ERROR/WARNING |
| Operation-type keying | Firmware (`firestarter.cpp` cmd dispatch + `eprom.cpp` init) | — | `handle->cmd` is the firmware's authoritative op enum |
| `electrical.type` derivation | Host codegen (`tools/build_db.py`) | — | DB is generated on the host; firmware never sees the type string |
| `FLAG_CAN_ERASE` derivation | Host (`database.py`) | Firmware reads the flag | Host computes from `electrical-type`; firmware acts on the wire flag |
| Blank-check op wiring | Firmware (`memory.cpp`/handler) | Host state machine | NULL main op for SRAM is a firmware gap; host must guard it |
| flash4 page sizing | Firmware (`flash_type_4.cpp`) | — | Page boundary + SDP are firmware write-path concerns |
| Decode-audit doc + EVIDENCE | Meta-repo (`.planning/`) | — | Documentation artifact, no code |

## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-10** Firmware change ALLOWED this phase (dual-repo lockstep); accept `pio test -e native` + Leonardo flash ≤ ~90% gate; firmware may diverge from pinned b10.
- **D-11** Firmware fix bounded to the VPP-skip directive ONLY: gate VPP error/warning checks off `read`/`blank-check` in `firestarter.cpp`/`eprom.cpp` with host parity in `eprom_operations.py`. Do NOT actively drive 0x0B shared OE/VPP pin, touch 0x08 write/VPP, or touch flash4.
- **D-12** Firmware versioning/beta-cut deferred to milestone-close; keep firmware on the `v1.15-…` sub-repo branch; no version bump/tag in this phase.
- **D-20** 2516 read re-attempted (N≥3) AFTER the VPP-skip fix.
- **D-21** Re-validate 2516 read ONLY; never write/preserve-dump it this phase.
- **D-22** GRAD-03 write proof stays DEFERRED; FUT-03 remains OPEN (best-effort). SC#4 cannot be satisfied this phase by design.
- **D-30** FM1608/FRAM (0x40) blank-check "Empty input" gap: FIX host-side this phase, pin with a test.
- **D-31** AM27C020 0x08 write + W29C040 flash4 256B-page: RCA + confirmatory re-bench, fix-if-trivial else defer (0x08→future; W29C040 flash4→Phase-74 Wave-2/CR-01).
- **D-32** Genuine-silicon FAILs (W27E512, W27E040 stuck bits) are NOT FIX-01 material — record as silicon-limited only.
- **D-33** Folded todos: VPP-skip todo IS the D-11 fix; flash4 CR-01 todo IS the D-31(c) tracker.
- **D-40** EDIT the DB to correct the 2 cosmetic `electrical.type` labels at the **build_db.py derivation/override layer (NOT a hand-edit of chip_database.json)**; MUST be verified label-only via `diff_db.py` (clean delta, NO change to FLAG_CAN_ERASE/VPP/pinout/algorithm), `check_dispatch.py` + host suite green, no collateral change to chips sharing infoic flags. **If it cannot be made label-only / risks CAN_ERASE, STOP and re-surface to the operator before shipping.**
- **D-41** Annotate REWR-01/02/04 traceability with silicon dispositions; fix cosmetic UV-01..04 checkbox drift.
- **D-42** Consolidated decode audit = NEW doc `.planning/v1.15/DECODE-AUDIT.md`.
- **D-43** Milestone close = best-effort with documented deferrals; FIX-01 closes as "fixed where in-posture; deeper write-path defects RCA'd + deferred with rationale".
- **D-50** Board lock: Leonardo + RURP Rev 2.0 ONLY; verify `controller:` port identity per task, live `r1 ≈ 270000`, ASK operator which silkscreen rev; Leonardo chip-OUT-sideload-EXEMPT.
- **D-51** SAFE-02 software gate: host suite green incl. 0xA4 guard `test_init_phase_data_frames_not_acked`; validate `ruff check`/`ruff format --check` against CI scope `firestarter/ tests/` and CI target py3.9/3.11; pre-existing `tools/`-tree findings out-of-scope.
- **D-52** Reuse-first, no new harness: `dev write-cycle`, `dev consistency-check --runs 3`, `tools/gen_test_image.py`, `write_test.sh`.
- **D-53** Non-vacuous PASS bar: trustworthy Leonardo read (N≥3 byte-identical/SHA-matched) + negative control (wrong-file `verify` exits non-zero).
- **D-54** Write-failure disposition: reseat + retry up to N=2, then record FAIL/ANOMALY and continue; 2516 exempt (never written).

### Claude's Discretion
- Location/structure of `.planning/v1.15/DECODE-AUDIT.md`; table layout + cross-reference style.
- Whether the firmware VPP-skip gate keys on operation type, FLAG bits, or presence of a VPP-driving step (pick the cleanest mechanism keeping host↔firmware parity).
- Test names/placement for the FM1608 blank-check fix and any firmware native test.
- Whether W29C040's datasheet-256B-page retry uses `write -b` or `dev write-cycle`.
- Order of operations within the bench session (fw flash → 2516 re-read → 0x08/flash4 re-bench).

### Deferred Ideas (OUT OF SCOPE)
- 2516 write proof / GRAD-03 / SC#4 / FUT-03 close — DEFERRED best-effort (read revalidation only).
- Deeper 0x0B firmware fix (actively driving the shared OE/VPP pin).
- 0x08 AM27C020 write/VPP path fix (RCA + re-bench, fix deferred unless trivial).
- W29C040 flash4 256B-page write fix (re-bench; reopens Phase-74 Wave-2/CR-01 if not trivial).
- REWR-02 positive 0x08 write PASS — FUT-05.
- Firmware versioning / lockstep beta cut of the Phase-84 fw delta (D-12).
- v1.9 read-bug RCA (Phase 45 → FUT-C); pushing 2516 upstream into build_db.py (FUT-B).

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FIX-01 | Any per-family write/program/verify defect the bench surfaced is root-caused and fixed (host-only or dual-repo lockstep), re-verified on the bench, full-DB VPP-safety gate green. *(Conditional — closes as "fixed where in-posture; deeper defects RCA'd+deferred" per D-43.)* | The VPP-skip firmware fix (Investigation 1) clears the chip-1 18.8V refusal + benign warnings; FM1608 blank-check host fix (Investigation 3) closes the tooling gap; AM27C020 0x08 + W29C040 flash4 (Investigation 4) get RCA + re-bench + disposition; genuine stuck-bit FAILs explicitly excluded by D-32. |

## Project Constraints (from CLAUDE.md)

- **Host↔firmware constant/flag-bit duplication (load-bearing this phase):** `firestarter/include/firestarter.h` ↔ `firestarter_app/firestarter/constants.py` define the same flag bits and command codes; change in lockstep. The VPP-skip fix uses **existing** constants (`CMD_READ`, `CMD_BLANK_CHECK`, `FLAG_VPE_AS_VPP 0x10`) so no new constant is introduced — but any new flag/command WOULD require both files + the firmware enum.
- **Serial protocol sync:** `serial_comm.py` ↔ `firestarter.cpp` must stay in sync. The VPP-skip change does NOT alter the wire protocol (no new command, no new field) — it changes when the firmware emits an ERROR vs proceeds, which the host already handles.
- **Buffer note:** Uno = 512B, Leonardo = 1024B data buffer. Phase 84 board is Leonardo (1024B) — `DATA_BUFFER_SIZE` is 1024 in the flashed build.
- **DB is codegen:** `chip_database.json` is "do NOT edit by hand" — the D-40 relabel MUST land in `tools/build_db.py` (CLAUDE.md app §Key Files + Database Pipeline).
- **Tooling gate (v1.8):** `ruff check` + `ruff format --check` + `mypy` (strict on 8 modules) + `pytest --cov-fail-under=70`, enforced by `.github/workflows/ci.yml` over `firestarter/ tests/` at **Python 3.11** (single matrix entry, confirmed `ci.yml:32`). Devcontainer is Python 3.12.13 → masks CI; validate against the CI scope/target.

## Standard Stack

No new packages this phase (D-52 reuse-first). The existing toolchain:

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| PlatformIO (`pio`) | on PATH (`/usr/local/bin/pio`) | Firmware build + `pio test -e native` dispatch tests + Leonardo flash | Project's firmware build system [VERIFIED: `which pio`] |
| pytest | importable (Py3.12.13 devcontainer) | Host test suite incl. 0xA4 guard | Project's host test runner [VERIFIED: `import pytest`] |
| ruff | per `.github/workflows/ci.yml` | lint + format gate over `firestarter/ tests/` | CI-authoritative gate [VERIFIED: ci.yml:59-63] |
| Firestarter CLI (`firestarter`) | 3.0.0bN | `read`/`blank`/`write`/`verify`/`dev *` bench ops | The host CLI under test [CITED: firestarter_app/CLAUDE.md] |

**Installation:** `pip install -e '.[test]'` in `firestarter_app/` (per memory: restores wiped toolchain; the hardened mypy gate prints OK even when mypy is MISSING — verify mypy actually present).

## Package Legitimacy Audit

> Not applicable — Phase 84 installs **no external packages** (D-52 reuse-first; only new artifacts are the DECODE-AUDIT.md doc + EVIDENCE appends + targeted code fixes/tests). No `npm install` / `pip install <new-dep>` / `cargo add` occurs.

## Architecture Patterns

### System Architecture Diagram — VPP-skip gate (Investigation 1)

```
firestarter <chip> read   (host)
  └─ eprom_operations.py: check_eprom_blank / read_eprom
        builds JSON cmd {cmd:1|4, algorithm, vpp_mv, flags, ...}
        └─ serial_comm.py → COBS frame → Arduino @250000 baud
                                              │
                                              ▼  (FIRMWARE)
        firestarter.cpp:loop() → CMD_READ → eprom_read()  (CMD_BLANK_CHECK → eprom_blank_check())
              └─ op_execute_stateful/simple_operation → operation_utils.cpp:_execute_operation_house_keeping
                    └─ calls handle->firestarter_operation_init   (== eprom_generic_init for read/blank)
                          └─ eprom.cpp:290 eprom_generic_init()
                                └─ eprom.cpp:209 eprom_check_vpp()   ◄── THE GATE
                                      ├─ enables VPP regulator (line 220/223)   ← drives VPP on a READ
                                      ├─ measures rurp_read_voltage_mv()
                                      ├─ vpp_mv > target+500  → ERROR (18.8V refusal)  [or WARN if FLAG_FORCE]
                                      └─ vpp_mv < target*0.95 → WARN  ("VPP is low")
                          ◄── PROPOSED GATE: if handle->cmd ∈ {CMD_READ, CMD_BLANK_CHECK}: skip entirely
        ERROR/WARNING ──(response_code)──► host: _raise_for_error_response / logger.warning
```

### Pattern 1: Operation-type-keyed VPP skip (recommended mechanism — Claude's discretion D-11)
**What:** In `eprom_generic_init` (or inside `eprom_check_vpp`), early-return without enabling the
regulator or measuring when `handle->cmd == CMD_READ || handle->cmd == CMD_BLANK_CHECK`.
**Why this over alternatives:**
- **vs FLAG bits:** would require a new flag bit in BOTH `firestarter.h` and `constants.py` + host plumbing to set it — more surface, more parity risk, and the operator directive is about the *operation*, not a per-chip property.
- **vs presence-of-a-VPP-driving-step:** `read`/`blank-check` use `mem_util_blank_check` / `memory_read_execute` as `firestarter_operation_main` — neither drives VPP, so the gate is conceptually "init for a non-VPP op shouldn't enable VPP." `handle->cmd` already encodes this cleanly.
**Where:** `firestarter/src/proms/eprom.cpp` — `eprom_generic_init` (line 290) is the single choke point; it is the default init for read/blank-check (`configure_eprom`'s switch at `eprom.cpp:46` has NO case for CMD_READ/CMD_BLANK_CHECK, so they keep `firestarter_operation_init = eprom_generic_init` set at line 44).
**Note:** `CMD_CHECK_CHIP_ID` uses `eprom_check_chip_id_init` → `eprom_check_vpp` directly (eprom.cpp:79-81). Chip-ID check DOES need VPP (A9 12V for ID). Do NOT gate CHECK_CHIP_ID. Only READ + BLANK_CHECK.
**Example (current gate, the code to fence):**
```cpp
// Source: firestarter/src/proms/eprom.cpp:290 (read this session)
void eprom_generic_init(firestarter_handle_t* handle) {
    eprom_check_vpp(handle);                 // ◄── enables regulator + measures + may ERROR/WARN
    if (handle->response_code == RESPONSE_CODE_ERROR) {
        return;
    }
    if (handle->chip_id > 0) {
        eprom_internal_check_chip_id(handle, is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR);
    }
}
```

### Pattern 2: DB label override at the codegen layer (Investigation 2, D-40)
**What:** Inject a per-chip `electrical.type` override in `tools/build_db.py` AFTER Pass-2 re-derivation
(`build_db.py:629-643`), keyed on part_number, WITHOUT touching `proto_id`/`pinout`/`vpp` so dispatch is unperturbed.
**Where exactly:** Pass-2 sets `_etype` from `proto_id` at lines 629-643. A per-chip override must run
after this block and before `chip_entry` construction. The `_etype` value flows into the generated
`electrical.type`.
**CRITICAL caveat (the D-40 STOP trigger):** changing `_etype` to a value outside `{"EEPROM","Flash/EEPROM","SRAM","UV-EPROM"}` changes downstream consumers (see Don't-Hand-Roll + Common Pitfalls). For SST39SF040 the `Flash` label drops FLAG_CAN_ERASE — see Pitfall 1.

### Anti-Patterns to Avoid
- **Hand-editing `chip_database.json`:** regenerates away on next `build_db.py` run AND silently changes CAN_ERASE (D-40 explicitly forbids). Always edit `build_db.py`.
- **Gating CMD_CHECK_CHIP_ID's VPP:** chip-ID read needs 12V on A9; gating it would break ID checks.
- **Adding a new flag bit for the VPP skip:** unnecessary parity surface; `handle->cmd` already encodes the operation.
- **Touching the 0x0B shared-pin driving, 0x08 write/VPP, or flash4 page logic as part of the fix:** explicitly out of scope (D-11/D-31) — those are RCA-and-defer.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Asserting the DB relabel is label-only | A bespoke JSON differ | `tools/diff_db.py` (GATE-02) | Already classifies per-field deltas vs a pinned baseline; **but you MUST add a root-cause rule** (see Pitfall 3) |
| Asserting no dispatch/VPP-safety regression | Manual chip-by-chip review | `tools/check_dispatch.py` (GATE-03) | Full-DB structural + WARNING-5 type-keyed VPP-safety scan [CITED: check_dispatch.py header] |
| N≥3 read oracle for 2516 re-read | A loop calling `read` | `dev consistency-check --runs 3` | Built-in N-read oracle, 3-way verdict, writes per-run binaries [VERIFIED: cli_handlers.py:1047] |
| Write+readback re-bench (W29C040) | Manual write/verify steps | `dev write-cycle <chip> <image>` or `write -b` | Built-in write→read-back→SHA cycle (default `--runs 5`) [VERIFIED: cli_handlers.py:1137] |
| Deterministic re-bench image | Random bytes | `tools/gen_test_image.py <size> <seed>` | Reproducible SHA oracle [CITED: EVIDENCE.md Phase 83 image table] |
| Firmware native dispatch test | Hardware round-trip | `pio test -e native` | Host-side Unity dispatch suite, no board [CITED: firestarter/CLAUDE.md §Native Test] |

**Key insight:** `FLAG_CAN_ERASE` is **not** hand-rolled anywhere except `database.py:605` — it is derived
from `electrical-type ∈ {"EEPROM","Flash/EEPROM"}`. The single source means a relabel cannot avoid
touching CAN_ERASE if the new label leaves that set. There is no separate override seam; the planner must
either (a) keep CAN_ERASE by some other means, (b) leave SST39SF040 as `Flash/EEPROM` and reconsider the
"Flash" relabel, or (c) STOP and re-surface per D-40.

## Runtime State Inventory

> Phase 84 is firmware+host code/DB + bench re-validation. The "runtime state" that matters here is which
> physical artifacts carry stale state after the code/DB change.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | Generated `firestarter/data/chip_database.json` carries the OLD `electrical.type` for SST39SF040/FM1608 + the OLD FLAG_CAN_ERASE-relevant labels. It is a build artifact of `build_db.py`. | Re-run `python tools/build_db.py` after the override edit; commit the regenerated JSON. A hand-edit regenerates away (D-40). |
| Live service config | None — no external service holds the renamed/relabeled string. (`~/.firestarter/database.json` user-override holds the 2516 entry, untouched this phase — 2516 read-only per D-21.) | None — verified: 2516 override is read-only this phase. |
| OS-registered state | Flashed firmware on the Leonardo is currently **b10** (`firestarter` submodule HEAD a1953c2 on `beta`). The Phase-84 VPP-skip build must be flashed to the board before the 2516 re-read / 0x08 re-bench. | Re-flash Leonardo with the Phase-84 firmware build (`pio run -t upload -e leonardo`) at the bench session. |
| Secrets/env vars | `FIRESTARTER_CONFIG_DIR` test seam + `FIRESTARTER_DB_FILE`/`FIRESTARTER_BASELINE_FILE`/`FIRESTARTER_PINOUTS_FILE` env overrides for the gate scripts (code-level, no secret values). | None — names unchanged. |
| Build artifacts | `diff_db.py` baseline `tools/baseline/chip_database.baseline.json` (744-chip pinned Phase-70 output) is the comparison point for GATE-02; the relabel diff is measured against it. | Do NOT re-baseline blindly; add a root-cause rule so the legitimate label delta is *explained* (Pitfall 3). |

**The canonical question:** after the build_db.py override + regen, the flashed Leonardo firmware and the
committed chip_database.json both carry new state — both must be refreshed (re-flash + re-regen) for the
re-bench to test the actual Phase-84 build.

## Common Pitfalls

### Pitfall 1: SST39SF040 `Flash` relabel silently disables auto-erase
**What goes wrong:** Relabeling SST39SF040 from `Flash/EEPROM` to `Flash` removes it from the
`{"EEPROM","Flash/EEPROM"}` set at `database.py:605` → `FLAG_CAN_ERASE` (0x02) is no longer set on the
wire command → the firmware's `flash4_write_init`/`eprom_write_init` skip the auto-erase branch
(`is_flag_set(FLAG_CAN_ERASE)` guard, `flash_type_4.cpp:67` / `eprom.cpp:100`). SST39SF040 is proto 0x06
(`configure_flash3`), but the CAN_ERASE wire flag is still computed identically by the host.
**Why it happens:** `electrical.type` is the SOLE input to CAN_ERASE; there is no independent erase-capability field.
**How to avoid:** This is the D-40 STOP trigger. Options for the planner: keep SST39SF040 as `Flash/EEPROM`
(accept the cosmetic label, document in DECODE-AUDIT.md as observation), OR redesign so the `Flash` display
label is decoupled from the CAN_ERASE-deciding `electrical.type` string. Prove via a CAN_ERASE pinning test
(the Phase-81 81-01 re-audit test is the baseline) BEFORE shipping.
**Warning signs:** `diff_db.py` shows `("programming","algorithm")` unchanged but `("electrical","type")`
changed for SST39SF040; the host `flags` for SST39SF040 drop from 0x02 to 0x00.

### Pitfall 2: FM1608 `FRAM` relabel turns ON the VPP display + falls out of the curated label map
**What goes wrong:** `eprom_info.py:395` and `ic_layout.py:393` gate VPP display on `electrical-type != "SRAM"`.
FM1608 has `vpp_mv = 12000` in the DB. Relabel `SRAM`→`FRAM` makes `"FRAM" != "SRAM"` true → **VPP starts
displaying** for FM1608 (`12v`). Also `_ELECTRICAL_TYPE_LABEL` (`ic_layout.py:469`) has no `"FRAM"` key → the
Type label falls back to the protocol-based label (`get_chip_type_string(0x28)` = "SRAM (28-pin)"), so the
visible Type may NOT actually read "FRAM" unless the curated map is extended.
**Why it happens:** SRAM is special-cased as "no VPP, volatile" throughout the display layer.
**How to avoid:** If FM1608 must show "FRAM", extend `_ELECTRICAL_TYPE_LABEL` with `"FRAM": "FRAM"` AND
decide whether the VPP-display change is acceptable (FRAM has no programming VPP — arguably the VPP field
should stay hidden, so the relabel may need a companion guard `electrical-type not in {"SRAM","FRAM"}`).
CAN_ERASE is unaffected (FRAM ∉ {EEPROM, Flash/EEPROM}) — that part IS label-only.
**Warning signs:** `firestarter info FM1608` suddenly shows a VPP row; `firestarter list` VPP column flips from `-` to `12v`.

### Pitfall 3: `diff_db.py` BLOCKS a legitimate type-only relabel
**What goes wrong:** `diff_db.py` (`_RULE_FIELD_PATHS`, line 184) only allows `("electrical","type")` to
change as a side-effect of `RULE_ALGO`, `SRAM_PINOUT`, or `BUG_A_ETYPE`. The comment at line 176-183 states
explicitly: "a type change with no algo/pinout delta would (correctly) remain unexplained" → **exit code 1
(BLOCK)**. A deliberate Phase-84 relabel has NO co-occurring algorithm/pinout change → unexplained → gate fails.
**Why it happens:** The gate is designed to catch *accidental* type drift; a deliberate label correction is
indistinguishable from drift without a new rule.
**How to avoid:** Add a new root-cause rule (e.g. `RULE_PHASE84_RELABEL`) to `_RULE_FIELD_PATHS` claiming
`{("electrical","type")}` scoped to the two part_numbers, OR re-pin the baseline (riskier — loses the guard).
Plan a `tests/test_diff_db_gate.py` assertion update (the gate is exercised by that test via subprocess).
**Warning signs:** `diff_db.py` exits 1 with "unexplained diff" naming SST39SF040 / FM1608.

### Pitfall 4: FM1608 blank-check "Empty input" is a FIRMWARE 0xA4, not a host-generated string
**What goes wrong:** Treating "Empty input" as a host string to suppress. It is firmware message
`0xA4 MSG_ERR_EMPTY_INPUT` (`messages.py:437` is the codegen host MIRROR; the firmware emits it at
`firestarter.cpp:115`/`:194`). FM1608 routes to `configure_sram` (no-op stub, `sram.cpp:15`); `configure_memory`
sets NO `firestarter_operation_main` for `CMD_BLANK_CHECK` (`memory.cpp:52-62` only handles READ/WRITE/VERIFY),
so the SRAM/FRAM blank-check has a NULL main op.
**Why it happens:** SRAM/FRAM has no meaningful "blank" concept; the firmware path was never wired for it.
**How to avoid (D-30, host-side):** Detect SRAM/FRAM (proto ∈ {0x0E,0x27,0x28,0x29} or electrical-type
SRAM/FRAM) in the host blank-check entry (`eprom_operations.py:check_eprom_blank` / `cli_handlers.py:blank`)
and short-circuit with a clear message instead of sending a command the firmware can't service. Pin with a test.
DO NOT change the wire protocol or firmware (D-11 bounds firmware to the VPP-skip only).
**Warning signs:** `firestarter blank FM1608` returns the firmware's "Empty input" / 0xA4.

### Pitfall 5: Devcontainer Python 3.12 masks the CI gate (D-51)
**What goes wrong:** Running `ruff`/`pytest` only under devcontainer Py3.12 can pass while CI (Py3.11,
`firestarter/ tests/` scope) fails, or surface pre-existing `tools/`-tree findings that are OUT of CI scope.
**Why it happens:** CI is `ci.yml:32` Python 3.11, ruff scoped to `firestarter/ tests/` (lines 59-63);
broad `ruff check .` reports 4 pre-existing `tools/`-tree I001/UP031 findings that are NOT in the gate.
**How to avoid:** Run `ruff check firestarter/ tests/` + `ruff format --check firestarter/ tests/` (CI-authoritative
scope), confirm green; FLAG (don't mask, don't fix) the `tools/`-tree findings. Confirm `mypy` actually present
(the hardened gate prints OK even when mypy is MISSING — memory note).
**Warning signs:** `ruff check .` reports `tools/audit_coverage_matrix.py`, `tools/catalog/codegen.py`,
`tools/catalog/codegen_vectors.py` (I001/UP031) — these are the known pre-existing out-of-scope items.

### Pitfall 6: Firmware submodule is on `beta` (b10), not the v1.15 branch
**What goes wrong:** The D-11 firmware commit would land on `beta` (the wrong branch) or fail because the
v1.15 firmware branch doesn't exist yet. `git -C firestarter rev-parse --abbrev-ref HEAD` = **`beta`**
(only `beta` exists locally; HEAD = a1953c2 = b10). The host (`firestarter_app`) IS on
`v1.15-bench-validation-of-operator-inventory`.
**Why it happens:** v1.15 was host-only until D-10 authorized a firmware change; the firmware branch was
never forked (memory: "v1.15 sub-repo branch forked off v1.14 NOT beta" applied to the app; firmware stayed on beta).
**How to avoid:** Create/checkout the firmware `v1.15-bench-validation-of-operator-inventory` branch off the
current beta HEAD (b10) BEFORE the firmware edit, so the fw delta lands on the v1.15 branch (D-12: no version
bump/tag this phase). Keep the meta-repo gitlink pinned until the operator-gated beta cut.

## Code Examples

### VPP gate — current measurement + ERROR/WARN logic (the code to fence)
```cpp
// Source: firestarter/src/proms/eprom.cpp:209-272 (read this session)
void eprom_check_vpp(firestarter_handle_t* handle) {
    // ... REVISION_0 warn-and-return ...
    if (handle->protocol == 0x0B || is_flag_set(FLAG_VPE_AS_VPP)) {
        handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);          // 0x0B/legacy direct path
    } else {
        handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE, 1);
    }
    delay(100);
    uint16_t vpp_mv = rurp_read_voltage_mv();
    if (vpp_mv > (uint32_t)handle->vpp_mv + 500) {            // ◄── chip-1 "18.8V > 12.0V"
        if (is_flag_set(FLAG_FORCE)) { /* WARN */ } else { /* ERROR (refusal) */ }
    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {// ◄── "VPP is low" benign warning
        /* WARN */
    }
    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE, 0);
}
```

### Host CAN_ERASE derivation (the D-40 load-bearing site)
```python
# Source: firestarter_app/firestarter/database.py:604-607 (read this session)
simple_flags = 0
if full_eprom_data.get("electrical-type", "") in ("EEPROM", "Flash/EEPROM"):
    simple_flags |= FLAG_CAN_ERASE  # FLAG_CAN_ERASE is 0x02
programmer_data["flags"] = simple_flags
```

### flash4 page-size heuristic (D-31c — already 256 for W29C040)
```cpp
// Source: firestarter/src/proms/flash_type_4.cpp:27-31 (read this session)
static uint32_t flash4_page_size(uint32_t mem_size) {
    if (mem_size <= 65536)  return 64;
    if (mem_size <= 262144) return 128;   // W29C020 (262144) → 128 (PASSed)
    return 256;                            // W29C040 (524288) → 256 (FAILed @0x0000ff despite correct size)
}
```

### build_db.py Pass-2 type derivation (where the relabel override must land)
```python
# Source: firestarter_app/tools/build_db.py:629-643 (read this session)
if proto_id in {0x0E, 0x27, 0x28, 0x29}:
    _etype = "SRAM"                       # FM1608 (after Rule 3 → 0x28) lands here
elif proto_id in {0x07, 0x08, 0x0B}:
    _etype = "EEPROM" if (flags & 0x10) else "UV-EPROM"
elif proto_id in {0x05, 0x06, 0x0D, 0x10}:
    _etype = "Flash/EEPROM"               # SST39SF040 (0x06) lands here
# ◄── a per-chip override keyed on part_number must run AFTER this block
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| CAN_ERASE via synthetic `info-flags & 0x10` round-trip | Direct `electrical-type ∈ {EEPROM,Flash/EEPROM}` at `database.py:605` | Phase 77 (v1.14) | Relabel directly toggles CAN_ERASE — the D-40 constraint |
| flash4 fixed 64B page (W29C040 mid-page poll bug) | Data-driven `flash4_page_size(mem_size)` | Phase 74 (native-test-only, Wave-2 deferred) | W29C040 gets 256; bench re-test of this fix is the D-31(c) RCA |
| firmware identity = buffer/board | `version:board` + MSG_OK_READY ack (CAP-01) | Phase 55 (v1.10) | Unrelated to this phase but governs the connect handshake |

**Deprecated/outdated:**
- Hand-editing `chip_database.json`: forbidden (codegen overwrites; D-40).
- Adding `MSG_ERR_BAD_FRAME`: deferred — firmware reuses `MSG_ERR_EMPTY_INPUT` for frame errors (`firestarter.cpp:194` comment). Do not add new messages this phase.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The chip-1 "18.8V > 12.0V" refusal and "VPP is low" warnings originate from `eprom_check_vpp` (not a separate host gate) | Investigation 1 | LOW — the message strings + ERROR/WARN logic are uniquely in `eprom_check_vpp`; host only relays. Confirm at bench by reading the verbose log source line. |
| A2 | FM1608 blank-check "Empty input" is the NULL-main-op SRAM path surfacing firmware 0xA4 | Investigation 3 | MEDIUM — the exact trigger (data_size==0 vs frame error vs NULL main) should be reproduced at the bench/native to pin the precise origin before writing the host guard. The fix shape (host short-circuit for SRAM/FRAM) holds regardless. |
| A3 | The W29C040 flash4 fault is NOT fixed by a datasheet page-size change (b10 already returns 256) | Investigation 4 | LOW — verified W29C040 size=524288 → heuristic returns 256. Re-bench confirms whether the fault is SDP/poll/VPP-deeper. |
| A4 | No new flag bit/command is needed for the VPP-skip (operation-type keying via existing `handle->cmd`) | Investigation 1 | LOW — `handle->cmd` is set before init runs and is in scope in `eprom_generic_init`. |
| A5 | Operator intends SST39SF040 to display as algorithm `flash3`/type `Flash` AND keep auto-erase working | Investigation 2 | HIGH — if "Flash" relabel is taken literally it disables CAN_ERASE (Pitfall 1). This is the D-40 STOP-and-resurface case; the planner must get operator confirmation. |

## Open Questions

1. **Can SST39SF040 be relabeled to `Flash` without dropping FLAG_CAN_ERASE?**
   - What we know: CAN_ERASE is set iff `electrical-type ∈ {EEPROM, Flash/EEPROM}` (`database.py:605`); SST39SF040 is auto-erase-capable (proto 0x06 flash3, PASSed A→B in Phase 82 implying erase worked).
   - What's unclear: whether the operator wants the display label changed while preserving erase, or accepts keeping `Flash/EEPROM`.
   - Recommendation: per D-40, **STOP and re-surface to the operator** — present the CAN_ERASE collision; likely outcome is "keep Flash/EEPROM, note as observation in DECODE-AUDIT.md" OR decouple display label from the erase-deciding string.

2. **Should FM1608 `FRAM` relabel also hide VPP display?**
   - What we know: FM1608 has vpp_mv=12000 in DB but FRAM has no programming VPP; relabel turns the VPP row ON (Pitfall 2).
   - What's unclear: whether the operator wants VPP shown for FRAM (probably not).
   - Recommendation: extend the VPP-display gate to `electrical-type not in {"SRAM","FRAM"}` and add `"FRAM"` to `_ELECTRICAL_TYPE_LABEL`; pin both with tests.

3. **Exact origin of the FM1608 blank-check 0xA4.**
   - What we know: SRAM blank-check has NULL main op; firmware emits 0xA4 on empty/frame error.
   - What's unclear: the precise firmware line that fires for this case (data_size==0 vs the loop's NULL-main handling).
   - Recommendation: reproduce against the bench (or native dispatch stub) to confirm before writing the host guard; the host short-circuit is robust either way.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO `pio` | Firmware build, `pio test -e native`, Leonardo flash | ✓ | `/usr/local/bin/pio` | — |
| pytest | Host suite + 0xA4 guard | ✓ | Py3.12.13 devcontainer | — |
| ruff | CI-scope lint/format gate | assumed ✓ (CI uses it) | per ci.yml | run via CI scope |
| mypy | strict gate on 8 modules | VERIFY | — | memory: gate prints OK even when MISSING — confirm installed |
| Leonardo + RURP Rev 2.0 board | bench re-validation (2516 re-read, 0x08/flash4 re-bench) | operator-owned | flashed b10 → must reflash Phase-84 build | none — D-50 board lock; no non-Leonardo read authoritative |
| Native test env (`test/native/avr/test_dispatch/`) | firmware dispatch tests | ✓ | present | — |
| firmware v1.15 branch | landing the D-11 fw commit | ✗ (only `beta` exists) | — | create/checkout off beta HEAD (b10) — Pitfall 6 |

**Missing dependencies with no fallback:**
- The Leonardo + Rev 2.0 bench is operator-gated; the 2516 re-read / 0x08 / flash4 re-bench require an operator session (D-50).

**Missing dependencies with fallback:**
- The firmware v1.15 branch must be created off the current beta HEAD before the firmware edit (mechanical, no blocker).

## Validation Architecture

> nyquist_validation is not explicitly false in `.planning/config.json` (the milestone-audit shows Nyquist tracking is active for v1.15 phases). This section is INCLUDED.

### Test Framework
| Property | Value |
|----------|-------|
| Framework (host) | pytest (Py3.11 CI / Py3.12 devcontainer) |
| Framework (firmware) | PlatformIO Unity `[env:native]` |
| Config file | `firestarter_app/.github/workflows/ci.yml` (ruff/mypy/pytest gate); `firestarter/platformio.ini` `[env:native]` |
| Quick run command (host) | `cd firestarter_app && python -m pytest tests/test_eprom_operations.py -x` |
| Full suite command (host) | `cd firestarter_app && python -m pytest` |
| Firmware native | `cd firestarter && pio test -e native` |
| Gate scripts | `cd firestarter_app && python tools/check_dispatch.py && python tools/diff_db.py` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FIX-01 (VPP-skip) | read/blank-check init does NOT enable VPP regulator / emit VPP ERROR-WARN | firmware native (unit) | `pio test -e native -f "*test_dispatch*"` (extend dispatch suite) | ✅ suite exists; ❌ Wave 0: add VPP-skip assertion |
| FIX-01 (FM1608 blank) | `blank` on SRAM/FRAM short-circuits cleanly, no 0xA4 | host unit | `pytest tests/test_eprom_operations.py::<new_test> -x` | ✅ file exists; ❌ Wave 0: add test |
| D-40 (relabel label-only) | `diff_db.py` exits 0 (relabel explained); CAN_ERASE pinning test unchanged | host integration | `python tools/diff_db.py && pytest tests/test_diff_db_gate.py -x` + CAN_ERASE pinning test | ✅ `test_diff_db_gate.py`; ❌ Wave 0: add RULE_PHASE84_RELABEL + assertion |
| D-40 (no dispatch regression) | full-DB VPP-safety gate green | host integration | `python tools/check_dispatch.py` | ✅ exists |
| SAFE-02 (D-51) | 0xA4 ack guard green before bench | host unit | `pytest tests/test_eprom_operations.py::test_init_phase_data_frames_not_acked -x` | ✅ exists |
| FIX-01 re-bench (2516/0x08/flash4) | manual bench, Leonardo + Rev 2.0 | manual-only (hardware) | operator-gated; `dev consistency-check --runs 3`, `dev write-cycle`/`write -b` | n/a — manual, recorded in EVIDENCE |

### Sampling Rate
- **Per task commit:** host quick run (`pytest tests/test_eprom_operations.py -x`) + `pio test -e native` if firmware touched.
- **Per wave merge:** full host suite + `check_dispatch.py` + `diff_db.py` (all green) + 0xA4 guard.
- **Phase gate:** full host suite green + `pio test -e native` green + Leonardo flash ≤ ~90% (if firmware touched) before `/gsd-verify-work`; bench re-validation recorded in EVIDENCE.{md,json}.

### Wave 0 Gaps
- [ ] Native dispatch assertion that `eprom_generic_init` skips VPP for `CMD_READ`/`CMD_BLANK_CHECK` (extend `test/native/avr/test_dispatch/test_configure_memory.cpp` or a new suite) — covers FIX-01 firmware.
- [ ] Host test pinning the FM1608/SRAM blank-check short-circuit in `tests/test_eprom_operations.py` — covers FIX-01 host (D-30).
- [ ] `tools/diff_db.py` `RULE_PHASE84_RELABEL` root-cause rule + `tests/test_diff_db_gate.py` assertion — covers D-40 diff-gate (Pitfall 3).
- [ ] CAN_ERASE pinning assertion that the relabel does NOT change SST39SF040/FM1608 `flags` (reuse/extend the Phase-81 81-01 re-audit test) — proves D-40 label-only-for-CAN_ERASE.
- [ ] *(If FM1608 FRAM label taken)* host test pinning the VPP-display gate + `_ELECTRICAL_TYPE_LABEL` "FRAM" entry.

## Security Domain

> `security_enforcement` is not set false for this project. This phase touches firmware voltage gating and
> a DB safety classification — both have a hardware-safety dimension. STRIDE/ASVS web-app categories are
> mostly N/A (no auth/session/network), but the hardware-safety analogue is load-bearing.

### Applicable categories (hardware-safety adaptation)

| Category | Applies | Standard Control |
|----------|---------|-----------------|
| Input validation (DB → wire command) | yes | `check_dispatch.py` GATE-03 (no SRAM chip reaches `configure_eprom`'s 12V VPP; structural + WARNING-5 type-keyed) |
| Cryptography | no | n/a |
| Over-voltage / VPP hazard | yes | The VPP-skip (D-11) only removes the *error/warning* on non-VPP ops; it must NOT remove the regulator-disable or alter VPP for write/erase/chip-id. Over-voltage stays BLOCKED throughout (SC#5 carry). |
| DB classification safety | yes | `electrical.type` drives both CAN_ERASE and the WARNING-5/Rule-3 VPP-safety routing in build_db.py; the D-40 relabel must NOT perturb dispatch (verified via check_dispatch.py) |

### Known hazard patterns for this stack

| Pattern | Hazard | Standard Mitigation |
|---------|--------|---------------------|
| 12V VPP on a 5V part's address/data pin | hardware damage | build_db.py Rule 2 (WARNING-5) + Rule 3 (SRAM/FRAM 0x28 reroute) + check_dispatch.py gate |
| Relabel silently disabling auto-erase | data-integrity (write fails / stale data) | CAN_ERASE pinning test (Pitfall 1); STOP-and-resurface per D-40 |
| VPP-skip over-broadening to write/erase | over-voltage hazard | Gate ONLY on CMD_READ/CMD_BLANK_CHECK; native dispatch test asserts write/erase/chip-id still gate VPP |

## Sources

### Primary (HIGH confidence — read this session)
- `firestarter/src/proms/eprom.cpp` (eprom_check_vpp:209, eprom_generic_init:290, configure_eprom:41, eprom_write_execute:143)
- `firestarter/src/firestarter.cpp` (loop cmd dispatch:200-234, init_programmer_framed:109, MSG_ERR_EMPTY_INPUT:119/194)
- `firestarter/src/proms/memory.cpp` (configure_memory:46, protocol dispatch:74-113)
- `firestarter/src/proms/sram.cpp` (configure_sram no-op:15), `firestarter/src/proms/flash_type_4.cpp` (flash4_page_size:27, write paths)
- `firestarter/src/eprom_operations.cpp` (eprom_read/eprom_blank_check:19-55), `firestarter/src/operation_utils.cpp` (house-keeping/init invocation:195-231)
- `firestarter/include/firestarter.h` (CMD/FLAG defines), `firestarter/include/memory_utils.h` (using_p1_as_vpp:24)
- `firestarter_app/firestarter/database.py` (_map_data:412-457, FLAG_CAN_ERASE:604-607)
- `firestarter_app/firestarter/eprom_operations.py` (check_eprom_blank:1540, _main_phase_simple:406, _setup_operation:199)
- `firestarter_app/firestarter/ic_layout.py` (resolve_type_label:479, _ELECTRICAL_TYPE_LABEL:472, VPP gate:395), `firestarter_app/firestarter/eprom_info.py` (VPP gate:352/395)
- `firestarter_app/tools/build_db.py` (_etype Pass-1:487-506, Rules 1/2/3:508-605, Pass-2:629-643)
- `firestarter_app/tools/diff_db.py` (_RULE_FIELD_PATHS:184-221, derived-field comment:176-183), `firestarter_app/tools/check_dispatch.py` (header + _ALGO_MEM_TYPE)
- `firestarter_app/firestarter/cli_handlers.py` (blank:512, dev consistency-check:1049, dev write-cycle:1139), `firestarter_app/firestarter/messages.py` (MSG_ERR_EMPTY_INPUT 0xA4:437)
- `firestarter_app/.github/workflows/ci.yml` (Py3.11:32, ruff scope:59-63)
- `firestarter_app/firestarter/data/chip_database.json` (FM1608 algo=40/SRAM/DIP28_JEDEC_SRAM_8K:10010; SST39SF040 + W29C040/W29C020 entries)
- `.planning/v1.15/bench/EVIDENCE.md`, `.planning/v1.15-MILESTONE-AUDIT.md`, `.planning/ROADMAP.md` Phase 84, `.planning/REQUIREMENTS.md`
- `CLAUDE.md` (meta), `firestarter/CLAUDE.md`, `firestarter_app/CLAUDE.md`
- Submodule branch state: `git -C firestarter rev-parse --abbrev-ref HEAD` = `beta` (b10 a1953c2); `git -C firestarter_app ...` = `v1.15-bench-validation-of-operator-inventory`

### Secondary / Tertiary
- None — all findings verified against source this session; no WebSearch used.

## Metadata

**Confidence breakdown:**
- VPP-skip mechanism (Investigation 1): HIGH — single choke point identified, `handle->cmd` in scope confirmed.
- DB relabel + CAN_ERASE collision (Investigation 2/D-40): HIGH — `database.py:605` derivation read directly; the SST39SF040 CAN_ERASE flip is a verified consequence, not a guess.
- FM1608 blank-check (Investigation 3): MEDIUM — root cause (NULL SRAM main op + firmware 0xA4) identified; exact emitting line to be pinned at bench/native (A2).
- AM27C020 0x08 + W29C040 flash4 (Investigation 4): HIGH on the code surface (page-size heuristic already 256; P1-as-VPP path located); the silicon RCA is inherently a bench activity (RCA-and-defer per D-31).
- diff_db BLOCK risk (Pitfall 3): HIGH — the gate's own comment documents the unexplained-type-change behavior.

**Research date:** 2026-06-24
**Valid until:** 2026-07-24 (stable codebase; re-verify if submodules advance past current HEADs)
