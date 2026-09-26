# Phase 80: AT28C04/16 Adapter Graduation — Research

**Researched:** 2026-06-22
**Domain:** Host-only graduation (firestarter_app) + physical DIP24→DIP32 hardware adapter
**Confidence:** HIGH — every finding cites a concrete file:line or Planning artifact; no training-data assumptions

---

## Summary

Phase 80 graduates 9 `adapter-required` AT28C04/AT28C16 DIP24 EEPROMs to `supported` through:

1. A physical DIP24→DIP32 adapter built per the Phase 76 pin-map spec (`.planning/AT28C04-ADAPTER.md`)
2. Two host-only edits: remove the `_AT28C_DIP24_NAMES` arm in `build_db.py` + remove the implied `adapter-required` refusal in `chip_resolver.resolve_chip` (self-heals once the DB flips to `supported`)
3. A golden Leonardo write+read-back round-trip with the adapter seated

The firmware handler `configure_eeprom28c` (protocol `0x0D`) already exists and is correct — NO firmware change is required. Phase 78 confirmed PCB-blocked status for X88C64; Phase 77 established the guard-removal-last graduation discipline that Phase 80 follows exactly.

**Primary constraint:** This phase is HARDWARE-BLOCKED until the physical adapter is built. If the adapter is not built, defer cleanly with chips remaining `adapter-required` — mirroring Phase 78 (FUT-01 discipline) and Phase 79 (NOT CLEARED halt).

**Primary recommendation:** Follow the Phase 77 4-plan structure: (1) hardware gate — adapter build + DMM continuity check, `autonomous:false`; (2) host software edits + test updates; (3) SAFE gates (check_dispatch + parity + full suite); (4) Leonardo bench proof, `autonomous:false`.

---

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ADPT-01 | Physical DIP24→DIP32 adapter built + DMM continuity check (especially chip pin 21 /WE → socket pin 30) before any chip is inserted | §Q1 (pin-map verified), §Q5 (bench gate pattern), §Deferral Path |
| ADPT-02 | `_AT28C_DIP24_NAMES` arm removed from `build_db.py`; `adapter-required` refusal self-heals; host wire round-trip proves correct 0x0D dispatch | §Q2, §Q3, §Q4 |
| ADPT-03 | 9 chips graduate to `supported`; golden Leonardo write+read-back SHA-match + non-vacuous negative control | §Q5, §Q6 |

---

## User Constraints (from CONTEXT.md / STATE.md / ROADMAP.md)

### Locked Decisions
- Firmware handler `configure_eeprom28c` (protocol `0x0D`) is already implemented and correct — NO firmware change, NO constants.py/firestarter.h lockstep bump (SAFE-03 trivially holds: no constants touched).
- Graduation gate (SAFE-01) is always the FINAL step, gated behind native register-bit tests + host wire round-trip + Leonardo bench proof.
- Build order is operator-locked: Phase 80 comes after 77/78/79.
- `check_dispatch.py` full-DB VPP-safety gate (SAFE-02) must pass after the graduation.
- gitlinks are PINNED until the v1.14 beta cut — no meta gitlink bump per-phase.
- Phase is host-only (firestarter_app); firestarter sub-repo stays on beta, unchanged.

### Claude's Discretion
- Exact plan count and wave structure (research recommends 3–4 plans mirroring Phase 77)
- Whether the SAFE gate plan (check_dispatch + full suite) is merged into the software edit plan or kept separate

### Deferred Ideas (OUT OF SCOPE)
- Any firmware modifications to `configure_eeprom28c`
- Supporting AT28C chips without the physical adapter (no blind handler)
- Graduation of AT28HC04, 28C04A family members that are aliases in the same 9 DB entries (they graduate automatically when the named arm is removed — no per-alias action needed)

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Adapter build + DMM check | Operator (hardware) | — | Physical task; Claude can assist with reference to the pin table but cannot build the adapter |
| `_AT28C_DIP24_NAMES` removal | Host (build_db.py) | — | DB-generation-time rule arm; removing it changes the generated JSON |
| DB regeneration | Host (build_db.py) | CI | `python3 tools/build_db.py` regenerates `chip_database.json` |
| Host-guard self-heal | Host (chip_resolver.py) | — | Guard fires on `support_status != "supported"`; self-heals once DB flips |
| VPP-safety gate | Host (check_dispatch.py) | — | Full-DB scan; `configure_eeprom28c` invariant `(0, 6000)` already covers 0x0D |
| Bench write+read-back | Hardware (Leonardo + adapter + chip) | Operator | Leonardo is the only trustworthy write/verify board |

---

## Q&A — Numbered Answers for the Planner

### Q1: Exactly which 9 chips (part numbers + DB state)?

Confirmed by querying `firestarter_app/firestarter/data/chip_database.json` 2026-06-22:

| DB Entry (part_number field) | Manufacturer | support_status | algorithm | pinout |
|------------------------------|-------------|----------------|-----------|--------|
| `AT28C04,AT28HC04` | ATMEL | adapter-required | 0x0D | DIP24_2816 |
| `AT28C04E,AT28C04F` | ATMEL | adapter-required | 0x0D | DIP24_2816 |
| `AT28C16,AT28HC16,AT28HC16L` | ATMEL | adapter-required | 0x0D | DIP24_2816 |
| `AT28C16E,AT28C16F` | ATMEL | adapter-required | 0x0D | DIP24_2816 |
| `28C04A` | MICROCHIP memory | adapter-required | 0x0D | DIP24_2816 |
| `28C04AF` | MICROCHIP memory | adapter-required | 0x0D | DIP24_2816 |
| `28C16A` | MICROCHIP memory | adapter-required | 0x0D | DIP24_2816 |
| `28C16AF` | MICROCHIP memory | adapter-required | 0x0D | DIP24_2816 |
| `UPD28C04` | NEC | adapter-required | 0x0D | DIP24_2816 |

**Total: 9 DB entries, 14 individual aliases** (multi-alias entries e.g. `AT28C16,AT28HC16,AT28HC16L`).

The `_AT28C_DIP24_NAMES` set in `build_db.py` matches exactly on name intersection (lines 435–449):
`{AT28C04, AT28HC04, AT28C04E, AT28C04F, AT28C16, AT28HC16, AT28HC16L, AT28C16E, AT28C16F, 28C04A, 28C04AF, 28C16A, 28C16AF, UPD28C04}`.

**Key structural fact:** All 9 entries already have `algorithm=0x0D` (EEPROM_POLL → `configure_eeprom28c`) and `pinout=DIP24_2816` in the DB. `vpp_mv=12000` is the DB-encoded chip-spec voltage (the AT28C-family datasheet Vpp spec); it does NOT mean the VPP rail is asserted — `configure_eeprom28c` is entirely 5V-only (see Q6). The `vpp_mv` value is only read by `check_dispatch.py` for the invariant check; the `(0, 6000)` invariant for `configure_eeprom28c` **will require attention** — see §Critical: vpp_mv issue below.

[VERIFIED: firestarter_app/firestarter/data/chip_database.json — direct read 2026-06-22]

### Q2: Exact edit in build_db.py to stop demoting them?

**Location:** `firestarter_app/tools/build_db.py`, lines 416–459 [VERIFIED: direct read 2026-06-22]

The `_AT28C_DIP24_NAMES` named rule arm (D-03, Phase 76) occupies **lines 416–459**. It fires AFTER Site B (which does NOT fire for these chips — see §Architecture Patterns) and sets only `_support_status = "adapter-required"` and `_unsupported_reason`. It intentionally does NOT touch `proto_id` (the comment at line 419 explicitly says proto_id stays 0x0D).

**The minimal change:** Delete lines 416–459 entirely (the named arm block from the comment `# Named rule arm: AT28C04/AT28C16 family` through the closing `_unsupported_reason = (...)` assignment). No other line in build_db.py needs changing for graduation — `proto_id` is already 0x0D and `pinout` is already DIP24_2816.

```python
# LINES 416–459 TO DELETE — the named arm block:
# Named rule arm: AT28C04/AT28C16 family (D-03, Phase 76)
# ...
_AT28C_DIP24_NAMES = {
    "AT28C04",
    "AT28HC04",
    ...
    "UPD28C04",
}
_chip_aliases = {
    a.split("@")[0].strip() for a in name.split(",") if a.strip()
}
if _chip_aliases & _AT28C_DIP24_NAMES:
    _support_status = "adapter-required"
    _unsupported_reason = (
        "adapter required: AT28C04/AT28C16 DIP24 chip — requires a physical "
        "DIP24-to-DIP32 adapter; see firestarter/doc/AT28C04-ADAPTER.md"
    )
```

After deleting this block, the 9 chips will fall through with `_support_status = "supported"` (the default established earlier in the loop), `proto_id = 0x0D`, `pinout = DIP24_2816`. The DB must then be regenerated with `python3 tools/build_db.py`.

**Important:** The `_chip_aliases` assignment at lines 451–453 is ONLY used for the named arm intersection test. If there is no other use of `_chip_aliases` downstream, both the set construction and the `if _chip_aliases & _AT28C_DIP24_NAMES:` block can be removed. Verify with a grep before deleting.

[VERIFIED: firestarter_app/tools/build_db.py lines 416–459 — direct read 2026-06-22]

### Q3: Does chip_resolver.resolve_chip self-heal, or is there a separate removal?

**Self-heals.** `chip_resolver.resolve_chip` at lines 54–57 checks:
```python
support_status = raw_config.get("support_status", "supported")
if support_status != "supported":
    reason = raw_config.get("unsupported_reason", "unsupported on this hardware")
    raise ChipNotImplementedError(f"{name}: {reason}")
```
[VERIFIED: firestarter_app/firestarter/chip_resolver.py:54–57 — direct read 2026-06-22]

This is driven purely by the DB's `support_status` field. Once `build_db.py` stops setting `support_status="adapter-required"` for these chips (Q2), the regenerated `chip_database.json` will have `support_status="supported"` for them, and `resolve_chip` will proceed to `convert_to_programmer` without any change to `chip_resolver.py` itself.

There is NO separate named-arm refusal string to remove from `chip_resolver.py`. The pattern is identical to Phase 77: the software edit is entirely in `build_db.py` + DB regeneration; `chip_resolver.py` is untouched.

[VERIFIED: Phase 77 analogous decision — 77-03-SUMMARY.md: "SAFE-01 is N/A-no-refusal for Phase 77 (D-05): the 8 target chips are already support_status:supported, so there is NO resolve_chip host-guard refusal to remove"]

### Q4: Tests that currently assert adapter-required (will break, must be re-targeted)?

The following tests assert `adapter-required` for AT28C chips and will fail after graduation. All must be updated in the SAME wave as the `build_db.py` edit and DB regeneration:

**`tests/test_build_db_inclusion.py`:**
- `TestAdapterRequired24Pin.test_adapter_required_24pin` (line ~115) — asserts `support_status="adapter-required"` chips exist and AT28C family is among them. After graduation, this test must either be removed (if no other adapter-required chips remain) or updated to exclude AT28C family. **Check first:** are there any non-AT28C adapter-required chips in the DB? Currently the 9 AT28C entries are the only `adapter-required` chips — the class may need to be repurposed or removed entirely.
- `TestUnsupportedReasonStrings.test_adapter_required_reason_starts_with_adapter_required` (line ~425) — asserts `AT28C16` has `support_status="adapter-required"` reason starting with `"adapter required:"`. Will fail after graduation; remove or retarget.
- `TestUnsupportedReasonStrings.test_at28c16_named_arm_reason_mentions_adapter_doc` (line ~475) — asserts `AT28C16` named-arm reason references `"AT28C04-ADAPTER.md"`. Will fail after graduation; remove or retarget.

**`tests/test_chip_resolver.py`:**
- `test_resolve_chip_adapter_required_raises_not_implemented` (line 77) — asserts `resolve_chip("AT28C04", db=db)` raises `ChipNotImplementedError`. This test's purpose INVERTS after graduation: AT28C04 should now succeed. Either delete this test or convert it to a positive assertion (`resolve_chip("AT28C04")` returns a valid dict with `algorithm=0x0D`).

**`tests/test_cli_handlers.py`:**
- `test_info_adapter_required_no_crash` (line 169) — asserts `info AT28C16` exits 0. This test remains valid post-graduation (info still exits 0 — it just won't show the adapter-required status notice). The test itself passes, but the `caplog` assertions in `test_info_adapter_required_shows_status` (line 809) may fail.
- `test_info_adapter_required_shows_status` (line 809) — asserts `info AT28C16` shows `"adapter"` in log output. After graduation, the chip is supported — no adapter-status notice. This test will fail; remove or retarget to check that the chip is now shown as `supported`.
- `test_read_adapter_required_status_refusal` (line 871) — asserts `read AT28C16 out.bin` exits 1 with `"adapter"` in output. After graduation, AT28C16 should succeed (or at least reach the adapter-present logic). This test will fail; remove or retarget.

**`tests/test_check_dispatch_invariants.py`:**
- The `non_supported_dispatchable` invariant scenario at line ~185 uses a synthetic `configure_sram` chip — NOT the AT28C chips — so it is unaffected.

**New tests to add (same wave as edits):**
- `test_resolve_chip_at28c16_supported_resolves` — positive assertion: `resolve_chip("AT28C16")` returns a dict with `algorithm == 0x0D` and valid `memory-size`.
- `test_resolve_chip_at28c04_supported_resolves` — positive assertion for 512B chip.
- `test_at28c16_is_supported_in_db` — asserts `support_status="supported"` for AT28C16 in DB.
- In `test_cli_handlers.py`: `test_read_at28c16_dispatches_no_refusal` — `read AT28C16 out.bin` no longer exits 1 with "adapter" (or exits 1 for a different reason, e.g. no port, not a refusal reason).

[VERIFIED: grep of /workspaces/firestarter_app/tests/ 2026-06-22]

### Q5: Golden Leonardo write+read-back round-trip for 0x0D VPP-free chip?

The 0x0D `configure_eeprom28c` handler is VPP-free: no chip-OUT dry-run is required (unlike Phase 77/79 which need VPP rail verification). This LOWERS the bench pre-work significantly — the entire chip-OUT step is for VPP hazard mitigation, and 0x0D never asserts the VPP rail.

**However:** The standing bench precondition still applies before any write operation (per ROADMAP §v1.14):
- Leonardo is the ONLY trustworthy write/verify board (uno328pb N/A for program/write)
- ASK which silkscreen shield rev is mounted (Rev 2.2 / Rev 2.0 — do NOT use Modified Rev 0 for these tests unless absolutely necessary; Rev 2.0 preferred for write tests per bench history)
- Live R1/R2 reconcile (`r1 ≈ 270000`) each task
- Verify `controller:` port identity per task

**VPP note:** The AT28C16/28C04 `vpp_mv=12000` in the DB is the chip-specification voltage, not an assertion. The firmware `configure_eeprom28c` NEVER calls `CTRL_VPP_REGULATOR_ENABLE` (confirmed: `eeprom_28c.cpp` lines 71/78 only fire from `eeprom28c_check_chip_id`, which is for the A9-12V chip-ID check, not normal writes). A wiring error on the adapter cannot route 12V to the chip — the worst case is non-function, not chip destruction.

**Bench sequence (mirrors Phase 77 Plan 04):**

```
# 1. Standing bench precondition
firestarter --port /dev/ttyACMx version          # confirm Leonardo, record port
firestarter --port /dev/ttyACMx config           # confirm r1 ≈ 270000

# 2. Insert adapter + chip (AT28C16 or AT28C04)
# 3. Write a known test pattern
firestarter --port /dev/ttyACMx AT28C16 write <testfile>

# 4. Independent post-write read + SHA match
firestarter --port /dev/ttyACMx AT28C16 read readback.bin
sha256sum <testfile> readback.bin                # must match

# 5. Non-vacuous negative control
firestarter --port /dev/ttyACMx AT28C16 verify <wrong_file>
# Must exit non-zero (verify fails when content differs)
```

**AT28C EEPROMs are self-erasing on write:** The `configure_eeprom28c` handler issues the 6-byte SDP disable sequence then page-writes; each byte location is individually re-programmable. The `-b` flag (skip blank check) is likely needed if the chip is not factory-blank. If the chip has been previously written, use `-b` to skip the blank check:

```
firestarter --port /dev/ttyACMx AT28C16 write -b <testfile>
```

**N≥1 write + read-back is sufficient** (the Phase 77 bench standard for the graduation proof; N≥5 is not required for the first graduation evidence). The ROADMAP SC#3 says "golden write + read-back round-trip."

[VERIFIED: firestarter/src/proms/eeprom_28c.cpp — direct read 2026-06-22; ROADMAP Phase 80 SC#3 — direct read 2026-06-22]

### Q6: Confirm configure_eeprom28c firmware handler exists and needs NO change?

**Confirmed: handler exists, no change needed.**

The dispatch chain in `firestarter/src/proms/memory.cpp` at line 79:
```cpp
if (handle->protocol == 0x0D) {
    configure_eeprom28c(handle);
    return;
}
```
[VERIFIED: firestarter/src/proms/memory.cpp:79–80 — direct read 2026-06-22]

The handler implementation is in `firestarter/src/proms/eeprom_28c.cpp` (`configure_eeprom28c` function at line 35). It handles `CMD_WRITE` (page write with SDP disable + DQ7 polling) and `CMD_BLANK_CHECK`. It NEVER calls `CTRL_VPP_REGULATOR_ENABLE` in the normal write path. The optional A9-12V chip-ID check (`eeprom28c_check_chip_id`) does briefly assert VPP on A9 for ID verification, but this is only triggered by the `CMD_ID` command (not `CMD_WRITE` or `CMD_READ`).

The firmware CLAUDE.md (algorithm handler table) confirms:
> `0x0D | EEPROM_POLL | eeprom_28c.cpp | None (5V) | SDP disable + DQ7 page poll`

This handler was designed for the AT28C256/AT28C64 family (already supported 32-pin variants) and is fully compatible with AT28C16/AT28C04 (smaller address space — firmware restricts address generation to `mem_size` bytes). The `DIP24_2816` pinout comment in `pinouts.json` confirms:
> "Over-allocated to A0-A10 (11 address bits = AT28C16 maximum); AT28C04 has 9 address lines and firmware restricts driving via mem_size."

[VERIFIED: firestarter/src/proms/eeprom_28c.cpp — direct read 2026-06-22; firestarter_app/firestarter/data/pinouts.json DIP24_2816 entry — cited in .planning/AT28C04-ADAPTER.md §2.1]

### Q7: Confirm host-only — NO lockstep version/gitlink bump, parity tests unaffected?

**Confirmed: host-only, no lockstep needed.**

- `configure_eeprom28c` is an existing firmware handler — no firmware source change.
- No `FLAG_*` constants are added or changed: `FLAG_CAN_ERASE` (0x02) is already set by `convert_to_programmer` for Flash/EEPROM electrical type (Phase 77 edit) — AT28C16/AT28C04 are `electrical.type="Flash/EEPROM"`, so they already get `FLAG_CAN_ERASE` in the wire JSON; this is correct and requires no new edit.
- `constants.py` and `firestarter/include/firestarter.h` are untouched — parity tests pass trivially (SAFE-03 N/A-no-constants-touch).
- Meta gitlink stays pinned until the v1.14 beta cut (operator decision).
- `firestarter/` sub-repo stays on the current beta branch commit — no change.
- The v1.14 branch `v1.14-feasible-gap-implementation` is the active branch in `firestarter_app/` only.

[VERIFIED: STATE.md ("Sub-repo branch: firestarter_app on `v1.14-feasible-gap-implementation`…firestarter sub-repo stayed on beta, unchanged"); REQUIREMENTS.md SAFE-03 ("any FLAG_*/protocol constant touched in constants.py + firestarter.h is changed in lockstep")]

---

## Critical: vpp_mv Invariant — ALREADY HANDLED (no gate failure)

**Non-issue: `check_dispatch.py` already excludes `configure_eeprom28c` from the DB-level VPP invariant check.**

`check_dispatch.py` at line 93 defines:
```python
_DB_CHECKED_VPP_INVARIANTS: frozenset[str] = frozenset({"configure_flash_intel"})
```
[VERIFIED: firestarter_app/tools/check_dispatch.py:93 — direct read 2026-06-22]

The VPP invariant check at line 312 only fires for handlers in `_DB_CHECKED_VPP_INVARIANTS`. `configure_eeprom28c` is explicitly NOT in this frozenset. The gate comment at lines 306–309 explains:
> "For 5V-only handlers, electrical.vpp_mv encodes the WP-pin voltage (not programming VPP), producing false positives — those invariants are proven via synthetic fixture only."

Confirmed by querying the live DB: all 75 currently-`supported` `configure_eeprom28c` chips have `vpp_mv=12000` and `check_dispatch.py` already passes for them. The AT28C16/AT28C04 chips have the same `vpp_mv=12000` value. Graduating them will NOT cause a gate failure.

**The `(0, 6000)` invariant in `_FAMILY_VPP_INVARIANTS["configure_eeprom28c"]` is only tested via synthetic fixture** (`test_check_dispatch_invariants.py` at line 111). No DB-level check fires for real chips. SAFE-02 will pass without any change to `check_dispatch.py`.

[VERIFIED: firestarter_app/tools/check_dispatch.py:93, 306–312 + DB query 2026-06-22]

---

## Standard Stack

No new third-party dependencies. All tooling is pre-existing.

| Tool | Purpose | Version |
|------|---------|---------|
| `python3 tools/build_db.py` | Regenerate chip_database.json after named-arm removal | existing |
| `python3 tools/check_dispatch.py` | Full-DB VPP-safety gate (SAFE-02) | existing |
| `pytest --cov --cov-fail-under=70` | Full test suite + coverage gate | existing |
| `ruff check --target-version py39 .` | Lint gate (py3.12 masks CI; must use py39 target) | existing |
| `ruff format --check --target-version py39 .` | Format gate | existing |

---

## Architecture Patterns

### Phase 77 Graduation Pattern (Proven — FOLLOW EXACTLY)

Phase 77 establishes the graduation discipline that all v1.14 graduations follow. Phase 80 mirrors it:

| Phase 77 | Phase 80 Analog |
|----------|----------------|
| Plan 01: Wire `FLAG_CAN_ERASE` from `electrical.type` in `database.py` | Plan 01: `autonomous:false` hardware gate — adapter build + DMM continuity check |
| Plan 02: D-07 0xA4 regression test | Plan 02: Remove `_AT28C_DIP24_NAMES` arm from `build_db.py` + regenerate DB + update tests |
| Plan 03: SAFE gates (check_dispatch, parity, full suite) | Plan 03: SAFE gates (check_dispatch after invariant fix + full suite) |
| Plan 04: `autonomous:false` Leonardo bench proof | Plan 04: `autonomous:false` Leonardo bench proof (adapter seated) |

Phase 77 had both a software edit wave AND a regression test plan (02) because the 0xA4 fix needed a dedicated test. Phase 80 has no analogous regression fix — the edit is purely removal. The planner may merge the software edits + test updates into a single plan.

### Named-Arm Removal Pattern

The named arm (build_db.py lines 416–459) is the only location asserting `adapter-required` for these chips. The pattern matches Phase 79's NMOS ceiling change (host-only, build_db.py constant edit, DB regenerate, gate rerun) — except here it is a block deletion rather than a constant change.

### Self-Healing Guard Pattern

`chip_resolver.resolve_chip` is driven purely by `support_status` in the DB. Once the DB flips from `adapter-required` to `supported`, the guard self-heals without any change to `chip_resolver.py`. This is identical to how Phase 77's 8 chips worked (they were already `supported` — the guard was N/A).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Chip SDP unlock on AT28C writes | Custom SDP sequence | `configure_eeprom28c` already implements the 6-write SDP disable | firmware handles it since v1.11 Phase 58 unblocking |
| Adapter pin-map | Re-derive from scratch | `.planning/AT28C04-ADAPTER.md` + `firestarter/doc/AT28C04-ADAPTER.md` — verified derivation | Re-deriving risks errors; Phase 76 derivation is ground-truth-verified |
| VPP-safety analysis | Custom safety review | `check_dispatch.py` + `_FAMILY_VPP_INVARIANTS` | The gate already encodes the correct invariant for this handler family |

---

## Common Pitfalls

### Pitfall 1: Assuming Site B also fires for AT28C named-arm chips

**What goes wrong:** Site B at build_db.py lines 391–414 fires for `pin_count == 24 AND proto_id in (0x07, 0x08, 0x0B) AND (flags & 0x10)`. The AT28C chips arrive with `proto_id=0x0D` (NOT in `{0x07, 0x08, 0x0B}`), so Site B does NOT fire for them. They have NO `proto_id` demotion to `NON_DISPATCHABLE_ALGO`. The named arm (lines 416–459) only sets `support_status` and `unsupported_reason`, leaving `proto_id=0x0D` intact.

**Why it matters for graduation:** When the named arm is removed, these chips fall through with `proto_id=0x0D`, `support_status="supported"` — exactly what we want. No need to touch Site B. Do NOT add a Site B exemption.

**Warning signs:** If after removing the named arm, the chips still appear with `support_status="adapter-required"` in the regenerated DB — that would indicate Site B unexpectedly fired, which should not happen for 0x0D chips.

[VERIFIED: build_db.py:391–414 + 416–459 — direct read 2026-06-22]

### Pitfall 2: Expecting check_dispatch.py VPP gate to fail for AT28C chips

**What goes wrong:** It is tempting to assume `check_dispatch.py` will fail for the AT28C chips after graduation because their `vpp_mv=12000` exceeds the `configure_eeprom28c` invariant ceiling `(0, 6000)`. This assumption is WRONG.

**Reality:** `_DB_CHECKED_VPP_INVARIANTS` (line 93) only contains `configure_flash_intel`. The `configure_eeprom28c` handler is explicitly excluded from the DB-level invariant check (5V-only handlers use `vpp_mv` for the chip-spec voltage, not the asserted rail; confirmed by 75 currently-supported 0x0D chips all passing with `vpp_mv=12000`). SAFE-02 gate will pass without any change to `check_dispatch.py`.

**Prevention:** No action needed. Run `python3 tools/check_dispatch.py` after graduation and confirm 0 violations.

### Pitfall 3: test_build_db_inclusion.py class leaves no adapter-required chips

**What goes wrong:** `TestAdapterRequired24Pin.test_adapter_required_24pin` asserts that SOME chip has `support_status="adapter-required"` in the DB. After graduating all 9 AT28C chips, zero `adapter-required` chips remain — the test `assert adapter_chips` will fail.

**Prevention:** Remove or repurpose the entire `TestAdapterRequired24Pin` class. After graduation, it should become a test asserting `"AT28C16" NOT adapter-required` (positive graduation test).

### Pitfall 4: Physical adapter pin 21 → 30 skip

**What goes wrong:** The 23 "direct" connections (A0–A8, D0–D7, /CE, /OE, VCC, GND) follow a simple offset pattern. It is easy to build an adapter that gets those right but forgets the critical reroute: chip pin 21 (/WE) must connect to socket pin 30, NOT socket pin 21 (which is D7 on the DIP32 layout).

**Prevention:** The DMM continuity check BEFORE chip insertion must explicitly verify pin 21 → 30 continuity AND the absence of a short between pin 21 → 21 (or confirm pin 21 of the adapter is NC on the socket side). The ADPT-01 hardware gate plan must include this as an explicit named check item.

### Pitfall 5: AT28C04 NC pins (A9, A10) driven by firmware

**What goes wrong:** AT28C04 has 9 address bits (A0–A8). The adapter connects chip pin 22 (A9) → socket 26 and chip pin 19 (A10) → socket 23. These are NC on the AT28C04 die. The firmware drives them within `mem_size` (512 bytes = 9 bits), so A9/A10 are never asserted. Safe — but verify `mem_size` in the DB is 512 (not 2048).

[VERIFIED: AT28C04-ADAPTER.md §5 "AT28C04 NC Pins"]

### Pitfall 6: ruff target-version must be py39, not implicit py312

**What goes wrong:** The devcontainer runs Python 3.12; `ruff check .` without `--target-version py39` passes locally but fails CI (py39/3.11). f-string backslashes (py312 feature) are the common trap.

**Prevention:** Always gate with `ruff check --target-version py39 . && ruff format --check --target-version py39 .` from `firestarter_app/`. [VERIFIED: reference_devcontainer_py312_masks_ci_py39.md memory entry]

---

## Deferral Path (if adapter not built)

If the adapter is not physically built and DMM-verified at the Plan 01 hardware gate, the phase **defers cleanly** following the Phase 78 and Phase 79 deferral discipline:

1. Plan 01 produces a `80-01-SUMMARY.md` with verdict: `HARDWARE-GATE: NOT CLEARED — adapter not built`.
2. Plans 02, 03, 04 are marked BLOCKED.
3. Chips remain `adapter-required` — no DB change, no code change.
4. A `FUT-04` item (or extend FUT-01) is recorded: "Phase 80 ADPT-01 hardware gate not cleared; resume when physical adapter is built."
5. v1.14 may close with only Phases 77/78/80 complete (79 is already hardware-blocked), or v1.14 closes as 77/78 + partial 80 with documented deferral.

The adapter build + DMM check (ADPT-01) is the ONLY hardware gate in this phase. Unlike Phase 79 (which had an electrical VPP rail concern) or Phase 77 (which had a 14V VPP dry-run), Phase 80's gate is purely mechanical — it is adapter-has-been-built vs. adapter-not-yet-built. No dangerous voltage measurement is involved.

---

## Bench Evidence Template (ADPT-03 / Plan 04)

Mirror of 77-04-PLAN.md pattern. The bench summary (80-04-SUMMARY.md) must record:

| Item | Required |
|------|---------|
| Board | Leonardo (confirm — uno328pb N/A) |
| Port | /dev/ttyACM* (verify per-task — numbers shuffle) |
| Shield rev (silkscreen) | Operator-confirmed (ask which rev: 2.2 or 2.0; NOT Modified Rev 0 for write tests) |
| R1 readback | `r1 ≈ 270000` from `firestarter config` |
| Adapter in socket | Yes (chip pin 21 ↔ socket pin 30 verified by DMM in Plan 01) |
| Chip in adapter | AT28C16 (2KB) or AT28C04 (512B) — state part number |
| Write command | `firestarter AT28C16 write [-b] <testfile>` |
| Write exit code | 0 |
| Read command | `firestarter AT28C16 read readback.bin` |
| SHA match | `sha256sum <testfile> readback.bin` — both lines identical |
| Negative control | `firestarter AT28C16 verify <wrong_file>` exits non-zero |

---

## Validation Architecture

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | File | Status |
|--------|----------|-----------|------|--------|
| ADPT-01 | Adapter built + DMM continuity check | manual/bench (autonomous:false) | 80-01-SUMMARY.md | New (plan 01 artifact) |
| ADPT-02 | Named arm removed; resolve_chip succeeds for AT28C16/AT28C04 | unit | test_chip_resolver.py (new tests) | New |
| ADPT-02 | AT28C16 no longer adapter-required in DB | unit | test_build_db_inclusion.py (update) | Update existing |
| ADPT-02 | check_dispatch.py passes with graduated chips | integration | `python3 tools/check_dispatch.py` | Existing gate |
| ADPT-03 | Leonardo write+read-back SHA match | manual/bench (autonomous:false) | 80-04-SUMMARY.md | New (plan 04 artifact) |
| SAFE-01 | Guard removal is FINAL step | discipline | 77-03-SUMMARY.md (established) | Pattern inherited |
| SAFE-02 | check_dispatch.py full-DB VPP-safety gate passes | integration | `python3 tools/check_dispatch.py` | Existing gate (no change needed — 0x0D excluded from DB-level invariant check) |
| SAFE-03 | No constants.py/firestarter.h touched | review | N/A (no constants changed) | Trivially holds |

### Wave 0 Gaps (tests to create before or in the same wave as edits)

- [ ] `tests/test_chip_resolver.py` — add `test_resolve_chip_at28c16_supported_resolves` + `test_resolve_chip_at28c04_supported_resolves` (positive post-graduation assertions)
- [ ] `tests/test_build_db_inclusion.py` — update `TestAdapterRequired24Pin` class: remove or invert the AT28C assertions; add `test_at28c16_is_supported` positive test
- [ ] `tests/test_build_db_inclusion.py` — update `TestUnsupportedReasonStrings.test_adapter_required_reason_starts_with_adapter_required` and `test_at28c16_named_arm_reason_mentions_adapter_doc` — both will fail after graduation; remove them
- [ ] `tests/test_chip_resolver.py` — update `test_resolve_chip_adapter_required_raises_not_implemented` — invert from "must raise" to "must succeed"
- [ ] `tests/test_cli_handlers.py` — update `test_info_adapter_required_shows_status` + `test_read_adapter_required_status_refusal` (line 809, 871) — both will fail after graduation

### Sampling Rate
- **Per task commit:** `ruff check --target-version py39 . && ruff format --check --target-version py39 . && pytest tests/test_chip_resolver.py tests/test_build_db_inclusion.py -v`
- **Per wave merge:** `pytest --cov --cov-fail-under=70 && python3 tools/check_dispatch.py`
- **Phase gate (SAFE-01):** Full suite green before guard removal; bench proof on record before `/gsd-verify-phase`

---

## Security Domain

This phase has no security-relevant scope. The VPP hazard class is lower than Phase 77 (0x0D is 5V-only; no VPP rail to mis-calibrate). The `check_dispatch.py` gate is the structural security boundary; it is run as part of SAFE-02 and already has the `configure_eeprom28c` handler listed with a `(0, 6000)` invariant (to be updated to `(0, 13000)` per §Critical above).

ASVS categories: None applicable (no authentication, session, crypto, or user input paths in this phase).

---

## Environment Availability

| Dependency | Required By | Available | Notes |
|------------|------------|-----------|-------|
| Leonardo + firmware 3.0.0b8 | ADPT-03 bench proof | ✓ (bench-confirmed, STATE.md) | Firmware untouched; existing version sufficient |
| Rev 2.0 or 2.2 shield | ADPT-03 bench proof | ✓ (operator owns both) | Ask silkscreen rev before each task |
| AT28C16 or AT28C04 chip | ADPT-03 bench proof | **unknown — must ask operator** | Phase is hardware-blocked if no chip on hand |
| Physical DIP24→DIP32 adapter | ADPT-01/03 | **unknown — must build** | The primary hardware gate |
| DMM | ADPT-01 continuity check | ✓ (operator-owned) | For continuity test, not voltage |

**Missing dependencies with no fallback:**
- Physical adapter (not built yet) — this is the phase gate
- AT28C chip (unconfirmed availability) — ask operator at phase start

**Missing dependencies with fallback:**
- If only AT28C04 on hand (not AT28C16): bench proof works identically; 512B chip, 9 address bits; A9/A10 NC on the die; firmware uses `mem_size=512`

---

## Sources

### Primary (HIGH confidence — codebase, direct read 2026-06-22)
- `firestarter_app/tools/build_db.py` lines 416–459 (named arm block)
- `firestarter_app/firestarter/chip_resolver.py` lines 54–57 (support_status guard)
- `firestarter_app/tools/check_dispatch.py` lines 78–80 (VPP invariants)
- `firestarter_app/firestarter/data/chip_database.json` (all 9 AT28C entries confirmed)
- `firestarter/src/proms/memory.cpp` lines 79–80 (0x0D dispatch)
- `firestarter/src/proms/eeprom_28c.cpp` line 35 (`configure_eeprom28c` implementation)
- `.planning/AT28C04-ADAPTER.md` (full verified pin table + safety analysis)
- `.planning/phases/77-erase-write-path-graduation-0x07-ee-eproms/77-PATTERNS.md` (graduation pattern)
- `.planning/phases/77-erase-write-path-graduation-0x07-ee-eproms/77-03-SUMMARY.md` (SAFE gate evidence)
- `.planning/REQUIREMENTS.md` ADPT-01/02/03 + SAFE-01/02/03

### Secondary (HIGH confidence — planning artifacts)
- `.planning/ROADMAP.md` §Phase 80 (goal, success criteria, standing bench precondition)
- `.planning/STATE.md` (current Phase 79 halted status; bench config: leonardo/ACM0/Rev2.0/R1=270000)

---

## Metadata

**Confidence breakdown:**
- Named-arm location + exact edit: HIGH — direct read of file:line
- chip_resolver self-heal: HIGH — confirmed by direct code read + Phase 77 analogy
- test update list: HIGH — grep + direct read
- vpp_mv invariant issue: HIGH — direct read of check_dispatch.py + DB values; resolution approach MEDIUM (need to verify AT28C256 vpp_mv to confirm correct ceiling)
- Bench pattern: HIGH — mirrors verified Phase 77 Plan 04

**Research date:** 2026-06-22
**Valid until:** Stable — codebase facts; no external dependencies; valid until Phase 80 executes
