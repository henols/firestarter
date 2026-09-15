# SAFE-04 Verification — Over-Voltage Guard Chain (v1.16 / firmware a296195)

**Date:** 2026-06-26
**Plan:** 90-03
**Scope:** Verify-present-only (D-08 / D-10 — no source edits)
**SAFE-04 requirement:** Over-voltage stays blocked at the firmware VPP check; the host guard is
never bypassed; no irreplaceable UV part is written on an unstable read path (2516 stays UNVERIFIED).

---

## 1. Firmware Identity

```
git -C firestarter rev-parse HEAD
→ a296195ec757ad7857668342bb1ad381d2b2781a
```

**Matches expected firmware-under-test.** The version string still reports `3.0.0b10` (Phase-89
note: the string was not bumped per-phase; the commit hash is the authoritative build identity).

---

## 2. Over-Voltage HIGH Check — firmware VPP gate

**Command:**
```
grep -n "vpp_mv > (uint32_t)handle->vpp_mv + 500" firestarter/src/proms/primitives.cpp
```

**Result:**
```
106:    if (vpp_mv > (uint32_t)handle->vpp_mv + 500) {
```

**Matched line (primitives.cpp:106, inside `vpp_check_window`):**
```c
    if (vpp_mv > (uint32_t)handle->vpp_mv + 500) {
```

**Verdict:** PRESENT + UNMODIFIED

The `+500 mV` over-voltage threshold is present at the post-recompose location
(`firestarter/src/proms/primitives.cpp`, inside `vpp_check_window`).

**Semantics note (P3/PRIM-04, Phase 89):** This check was extracted from inline per-handler
bodies into the shared `vpp_check_window` primitive during Phase 89 (P3). The threshold
(`+500 mV`) and semantics (`FORCE → WARN / else → ERROR`) are byte-identical to the
pre-recompose form at `eprom.cpp:282` and `flash_intel.cpp:65` (the stale CONTEXT D-08 line
numbers). Behavior is unchanged; the guard moved to the shared primitive.

**Call sites:** `eprom_check_vpp` (`eprom.cpp`) and `flash_intel_check_vpp` (`flash_intel.cpp`)
both call `vpp_check_window(handle)` — the check fires for all VPP-bearing handlers.

---

## 3. Host Guard — `chip_resolver.resolve_chip` support-status check

**Command:**
```
grep -n "support_status" firestarter_app/firestarter/chip_resolver.py
```

**Result:**
```
28:    its ``support_status`` is not ``"supported"`` (covers protocol-not-implemented,
43:    # Read the raw config to access support_status (not carried through _map_data).
46:    # not-found takes priority over the support_status guard: an absent chip cannot
47:    # have a support_status, so raise ChipNotFoundError immediately.
53:    # Driven by support_status, not the incidental electrical.type string.
54:    support_status = raw_config.get("support_status", "supported")
55:    if support_status != "supported":
```

**Key line (chip_resolver.py:55):**
```python
    if support_status != "supported":
```

**Verdict:** PRESENT + UNCHANGED

The `resolve_chip` support-status guard is present at line 55. It fires **before** any wire
dict is built or serial byte emitted, refusing non-`supported` chips (covers
`protocol-not-implemented`, `adapter-required`, `vpp-exceeds-max`). The `info`/`list`/`id`
display paths bypass `resolve_chip` and are unaffected.

---

## 4. 2516 Verification Status

**Source:** `firestarter_app/firestarter/data/chip_database.json`, TEXAS INSTRUMENTS section

**Key fields for the 2516 record:**
```json
{
  "part_number": "2516",
  "support_status": "supported",
  "verification_status": "UNVERIFIED",
  "verification_note": "SAFE-04 / FUT-03: resolvable for read/info but NOT write-graduated. ..."
}
```

**Verdict:** 2516 `verification_status = UNVERIFIED` — no write-graduation this phase.

`support_status = "supported"` is intentional: the chip must remain resolvable for read/info
operations (the host guard refuses non-`supported` chips from ALL operations including read, so
UNVERIFIED is expressed via `verification_status`, not `support_status`). See Phase 86-04
decision.

---

## 5. Working-Tree Cleanliness (D-10 Frozen World)

```bash
git -C firestarter diff --quiet && echo FW-CLEAN
→ FW-CLEAN

git -C firestarter_app diff --quiet && echo HOST-CLEAN || echo HOST-DIRTY
→ HOST-DIRTY
```

**FW-CLEAN:** Firmware working tree has no modifications. ✓

**HOST-DIRTY note:** `firestarter_app` shows a single unstaged modification to `.gitignore`
(adding `consistency*`). This is a **pre-existing non-source change**, noted in Phase 89-01
decisions: "Pre-existing .gitignore change in firestarter_app noted (not source, not P7-caused)."
No Python source file, tool, test, or database file was modified. The SAFE-04 guard in
`chip_resolver.py` is unmodified (D-10 satisfied for all source files).

**Diff detail:**
```
--- a/.gitignore
+++ b/.gitignore
@@ -33,3 +33,4 @@
 CLAUDE.md
+consistency*
```

Only the `.gitignore` file. No source change.

---

## 6. Frozen-World Gate Results

### 6.1 `check_dispatch.py` (dispatch integrity gate)

**Command:** `cd firestarter_app && python3 tools/check_dispatch.py`

**Output:**
```
PASS: all 746 chips scanned; 736 supported; 10 chips confirmed non-dispatchable
(D-12: host guard covers non-supported chips with real handlers; non-handler outcomes also safe);
0 non_supported_dispatchable; 0 dispatch regressions; 0 consistency violations
```

**Exit code:** 0 ✓

### 6.2 `diff_db.py` (DB identity gate)

**Command:** `cd firestarter_app && python3 tools/diff_db.py`

**Output:**
```
GATE-02 Per-chip Diff Report
  Baseline: .../chip_database.baseline.json (746 chips, 746 diffed)
  Current:  .../chip_database.json (746 chips, 746 diffed)

--- CHANGED chips (0 total) ---
--- NEW chips (0) ---
--- MISSING chips (0) ---

PASS: all 0 changed chips explained (0 new chips confirmed; 0 chips removed from baseline)
```

**Exit code:** 0 — identity diff ✓

### 6.3 `pio test -e native` (firmware native suite)

**Command:** `cd firestarter && pio test -e native`

**Result:**
```
================ 105 test cases: 105 succeeded in 00:00:17.200 ================

Environment    Test                             Status
-------------  -------------------------------  --------
native         native/avr/test_val_flash4       PASSED
native         native/avr/test_not_implemented  PASSED
native         native/avr/test_dispatch         PASSED
native         native/avr/test_val_flash3       PASSED
native         native/avr/test_read_timing      PASSED
native         native/avr/test_cobs_cmd_frame   PASSED
native         native/avr/test_val_eprom        PASSED
native         native/avr/test_val_sram         PASSED
native         native/avr/test_cobs_data_frame  PASSED
native         native/avr/test_val_flash_intel  PASSED
native         native/avr/test_frame_vectors    PASSED
native         native/avr/test_val_eeprom28c    PASSED
native         native/avr/test_data_input       PASSED
native         native/avr/test_messages         PASSED
```

**105/105 PASSED** — matches Phase-89-close count. ✓

**Interpreter notes:**
- `check_dispatch.py` and `diff_db.py` run under devcontainer Python 3.12.13.
  This phase changes no host source; CI risk is minimal (per RESEARCH Pitfall 4).
  No ruff/mypy validation needed — zero host source files modified.
- Native suite runs under PlatformIO `platform = native` (host C++ compiler).

---

## 7. SAFE-04 Conclusion

All SAFE-04 guard-chain items verified present and unmodified on firmware-under-test `a296195`:

| Item | Location | Status |
|------|----------|--------|
| Over-voltage HIGH check (`vpp_mv > handle->vpp_mv + 500`) | `primitives.cpp:106` (inside `vpp_check_window`) | PRESENT + UNMODIFIED |
| Host support-status guard (`resolve_chip`) | `chip_resolver.py:55` | PRESENT + UNCHANGED |
| 2516 UNVERIFIED status | `chip_database.json` TEXAS INSTRUMENTS section | UNVERIFIED (no write-graduation) |
| Firmware working tree clean | `git -C firestarter diff --quiet` | CLEAN |
| Host source files clean | `chip_resolver.py` + all source unmodified | CLEAN (`.gitignore` pre-existing non-source change) |
| `check_dispatch.py` | 0 violations, 746 chips | EXIT 0 ✓ |
| `diff_db.py` | 0 changed, identity diff | EXIT 0 ✓ |
| `pio test -e native` | 105/105 PASSED | GREEN ✓ |

**Frozen world stands (D-10).** The SAFE-04 guard chain is intact on the firmware-under-test.
No source change was made in this plan. The live over-voltage behavior is exercised under
operator gating in Plan 04.

---

**Cross-reference:** SAFE-04 row in `.planning/phases/90-per-protocol-bench-validation-ledger/90-CONTEXT.md` D-08.
**Satisfies requirements:** SAFE-04, T-90-07, T-90-08, T-90-09, T-90-10.
