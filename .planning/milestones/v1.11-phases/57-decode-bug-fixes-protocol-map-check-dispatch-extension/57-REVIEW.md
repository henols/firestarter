---
phase: 57-decode-bug-fixes-protocol-map-check-dispatch-extension
reviewed: 2026-06-08T00:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - firestarter_app/tools/build_db.py
  - firestarter_app/tools/check_dispatch.py
  - firestarter_app/tests/test_decoder.py
  - firestarter_app/firestarter/ic_layout.py
  - firestarter_app/firestarter/database.py
findings:
  critical: 1
  warning: 4
  info: 3
  total: 8
status: issues_found
resolution:
  resolved: [CR-01, WR-01, WR-03]
  resolved_at: 2026-06-08T14:30:00Z
  commits:
    - "ffa74b6 — CR-01: re-key GATE-03 guard on electrical.type (also removes _vpp_pinouts → resolves WR-03)"
    - "f2a05e7 — WR-01: propagate 0x35/0x39 removal to database.py + ic_layout.py"
  deferred: [WR-02, WR-04]
  deferred_note: "WR-02 (protocol-table parity test) and WR-04 (_first_pin empty-list hardening) tracked as debt; no current-DB impact. Operator-approved scope was CR-01 + WR-01."
---

# Phase 57: Code Review Report

**Reviewed:** 2026-06-08
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found (CR-01, WR-01, WR-03 RESOLVED — see frontmatter resolution; WR-02, WR-04 deferred as debt)

> **Resolution (2026-06-08):** CR-01 confirmed via `dispatch()` + DB scan and fixed in `ffa74b6` — the GATE-03 guard now keys on `electrical.type == "Flash/EEPROM" ∧ handler == "configure_eprom"` (pinout-agnostic, true superset of WARNING-5), passes on the regenerated DB, and the removal of the dynamic `_vpp_pinouts` set resolves WR-03. WR-01 fixed in `f2a05e7` (0x35/0x39 removed from `database.py` + `ic_layout.py`). Full suite green (470+ tests, ≥70% coverage), ruff clean. WR-02/WR-04 deferred.

## Summary

Reviewed the Phase 57 decode-correctness fixes (build_db.py decode pipeline, test_decoder.py regression suite), the GATE-03 hardware-safety guard (check_dispatch.py), and the related debug fix in ic_layout.py / database.py.

The four advertised decode bug-fixes in `build_db.py` are correct: the `×100` multiplier is gone, `interpret_timing` now keys on `(0x07, 0x08, 0x0B)`, `VCC_VOLTAGES` gained nibbles `0x02`/`0x03`, the `vcc`/`vdd` bit-field extraction reads bits 11-8 / 15-12 respectively, and the regression tests assert the corrected (not the old buggy) values. The `_first_pin` and `_parse_pulse_duration` helpers behave correctly for the inputs that actually occur.

However, the highest-severity item in the review focus — the GATE-03 VPP-safety guard — is **structurally incapable of firing for the algorithm set it checks**, and the algorithm set it checks does not include the algorithms that actually drive the 12V VPP regulator. This is a false-negative safety guard (CR-01). Separately, the protocol-table canonicalization in `build_db.py` (removing 0x35/0x39) was **not** propagated to `database.py` or `ic_layout.py`, which still carry stale, contradictory mappings for those IDs.

## Critical Issues

### CR-01: GATE-03 VPP-safety guard is a dead/false-negative check — it can never catch the hazard it claims to guard

**File:** `firestarter_app/tools/check_dispatch.py:100, 143-150`

**Issue:** GATE-03 is supposed to be the "full-class VPP-safety guard" catching any chip that would route 12V onto a 5V part. As written it flags a chip only when **all three** conditions hold:

```python
_5v_eeprom_algos = frozenset({0x05, 0x06, 0x0D})
...
if (
    pinout in _vpp_pinouts
    and proto in _5v_eeprom_algos          # {0x05, 0x06, 0x0D}
    and handler == "configure_eprom"
):
```

But the `dispatch()` function (lines 65-85) returns early for every algorithm in that set, and none of those early returns is `configure_eprom`:

- `0x0D` → `configure_eeprom28c`
- `0x06` → `configure_flash3`
- `0x05` → `configure_flash4`

I proved exhaustively (across every `mem_type` value) that `dispatch(proto, mt) == "configure_eprom"` is **unsatisfiable** for `proto in {0x05, 0x06, 0x0D}`. The third predicate (`handler == "configure_eprom"`) can therefore never be true when the second predicate is true. The guard is dead code — it will report `0 vpp-pin Flash/EEPROM chips` on every conceivable database, including a malicious or regressed one.

Worse, the algorithms that *actually* engage the 12V VPP regulator via `configure_eprom` are `0x07 / 0x08 / 0x0B` (see `dispatch()` line 75-76 and `build_db.py:404-432` / `:491-534`, which both exist precisely because those algorithms drive `P1_VPP_ENABLE`). Those algorithms are **excluded** from `_5v_eeprom_algos`. So the real damage path — a 5V no-VPP part that is mis-tagged with a `0x07/0x08/0x0B` algorithm while carrying a `vpp-pin` pinout (pin 1 = A14/address on the 28C/29C family) — slips straight through GATE-03. I confirmed there are currently 337 chips on `0x07/0x08/0x0B` sitting on `vpp-pin` pinouts; GATE-03 inspects none of them. The narrower WARNING-5 guard (lines 133-140) only covers `pinout == "DIP28_2764" AND type == "Flash/EEPROM"`, so a regression on any other vpp-pinout (`DIP28_27256`, `DIP32_STD`, `DIP24_2716`, etc.) with a Flash/EEPROM type and an EPROM-family algorithm would be caught by neither guard.

The two real candidate-hazard chips (ATMEL `AT29C256`, `AT29LV256` — 5V flash on `DIP28_2764` where pin 1 = A14) happen to be safe today only because they carry algorithm `0x05` → `configure_flash4` (no VPP). They are exactly the chips GATE-03 names, yet they are not actually at risk, while the chips that *are* on the VPP path are not checked.

**Fix:** The guard's algorithm set must be the set that routes to `configure_eprom` (the VPP-asserting handler), not the 5V-EEPROM set. Make the third predicate redundant with the algorithm set, or drop it and key on the handler directly:

```python
# A vpp-pin pinout means socket pin 1 (or 22) carries 12V when configure_eprom
# asserts P1_VPP_ENABLE. Any chip that (a) sits on such a pinout, (b) is NOT a
# genuine 12V UV-EPROM, and (c) still dispatches to configure_eprom is a damage path.
_VPP_ASSERTING_HANDLER = "configure_eprom"
...
# Flag a 5V part (electrical.type in {"Flash/EEPROM"}) on a vpp-pin pinout that
# still reaches the VPP-asserting handler — regardless of which EPROM-family
# algorithm (0x07/0x08/0x0B) got it there.
if (
    pinout in _vpp_pinouts
    and etype == "Flash/EEPROM"
    and handler == _VPP_ASSERTING_HANDLER
):
    vpp_eeprom_in_eprom.append(
        f"{mfg}/{part} proto=0x{proto:02X} pinout={pinout} type={etype}"
    )
```

This makes GATE-03 a true superset of WARNING-5 (any vpp-pinout, not just `DIP28_2764`) and actually exercises the `0x07/0x08/0x0B → configure_eprom` path that drives 12V. At minimum, add a self-test asserting the guard *fires* on a synthetic hazard chip (e.g. a `DIP28_2764` + `Flash/EEPROM` + `0x07` record), so a guard that can never trigger fails CI rather than printing a false `PASS`.

## Warnings

### WR-01: 0x35 / 0x39 canonicalization not propagated — database.py and ic_layout.py contradict the corrected build_db.py truth

**File:** `firestarter_app/firestarter/database.py:60-61`, `firestarter_app/firestarter/ic_layout.py:228-229, 510`

**Issue:** Phase 57 corrected `build_db.py` to document `0x35` as `IC2_ALG_ITE` (an ITE EC **MCU**, not a flash memory) and `0x39` as a **phantom** with no `IC2_ALG` constant, and removed both from `KNOWN_PROTOCOLS` (build_db.py:44-45, 99-113). But two consumer modules still carry the old, now-wrong meanings:

- `database.py:60-61` maps `0x35 → mem_type 5` (comment "FLASH_EEPROM_LIKE") and `0x39 → mem_type 5` (comment "FLASH_INTEL_ALT"). These contradict the corrected upstream identity (`0x35` is an MCU; `0x39` does not exist).
- `ic_layout.py:228-229` labels `0x35 → "Flash (EEPROM-like)"` and `0x39 → "Flash (Intel-alt)"`.
- `ic_layout.py:507` includes `0x35, 0x39` in the `can_erase_str = "true (firmware-supported)"` branch.

Since `build_db.py` can no longer emit chips with these algorithms, the entries are dead, but they are actively misleading: a hand-edited `~/.firestarter/database.json` override carrying `algorithm: 53` (0x35) would be silently classified as an erasable flash chip and shown a fabricated "Flash (Intel-alt)" type, when upstream says it is an MCU the firmware cannot drive. The phase claims to canonicalize the protocol map; leaving two of three tables stale defeats the canonicalization.

**Fix:** Remove `0x35` and `0x39` from `database.py:_ALGO_MEM_TYPE`, from `ic_layout.py:get_chip_type_string`'s `proto_display`, and from the `can_erase_str` tuple at `ic_layout.py:507`, mirroring the build_db.py removal. If they must be retained as a defensive fallback for legacy overrides, replace the misleading "Flash" labels with an explicit "Unsupported (upstream MCU / phantom)" string and document why.

### WR-02: build_db.py PROTOCOL_MAP / KNOWN_PROTOCOLS diverge from database.py PROTOCOL_MAP — no single source of truth

**File:** `firestarter_app/tools/build_db.py:27-47, 101-113` vs `firestarter_app/firestarter/database.py:35-44`

**Issue:** Three independent protocol tables now exist with different contents:
- `build_db.py:PROTOCOL_MAP` — 11 entries (includes 0x0E, 0x10, 0x27, 0x28, 0x29; excludes 0x35/0x39).
- `database.py:PROTOCOL_MAP` — 8 entries (omits the SRAM protocols 0x0E/0x27/0x29; keeps only 0x28).
- `check_dispatch.py:_ALGO_MEM_TYPE` (11 entries, no 0x35/0x39) vs `database.py:_ALGO_MEM_TYPE` (13 entries, with 0x35/0x39).

These tables are maintained by hand and are already out of sync (WR-01 is one symptom). The CLAUDE.md "Known protocols" list still advertises `0x35, 0x39` as known. There is no test asserting the three tables agree on their shared keys.

**Fix:** Promote one canonical mapping (e.g. a single module imported by both `build_db.py` and `database.py`, or a generated constant), and add a parity test (analogous to `test_revision_constants_parity.py`) asserting `check_dispatch._ALGO_MEM_TYPE` and `database._ALGO_MEM_TYPE` agree on overlapping keys. Update CLAUDE.md's "Known protocols" line to drop `0x35, 0x39`.

### WR-03: GATE-03 / WARNING-5 / BLOCKER-2 guards silently no-op on a malformed or empty database

**File:** `firestarter_app/tools/check_dispatch.py:97-99, 114-122`

**Issue:** `_vpp_pinouts` is built dynamically from `pinouts.json` (lines 97-99). If `pinouts.json` is missing the `pins` sub-key or a future refactor renames `vpp-pin`, `_vpp_pinouts` becomes empty and **every** vpp-safety check silently passes — the script prints `PASS` with `0 vpp-pin ... chips` regardless of the actual database. Similarly, the outer loop skips any manufacturer whose value is not a list (line 115) without counting or reporting it, so a structurally corrupt DB section is invisible. Because this is a safety gate, "found nothing to check" and "checked and found nothing" must not both render as `PASS`.

**Fix:** After building `_vpp_pinouts`, assert it is non-empty (a vpp-pin pinout is known to exist — `DIP28_2764` at minimum) and fail loudly otherwise. Track `skipped` manufacturers and include the count in the summary line; a non-zero skip count on a safety gate should be surfaced, not swallowed.

### WR-04: `_first_pin` raises an unhandled IndexError on an empty pin list and silently ignores extra elements

**File:** `firestarter_app/firestarter/ic_layout.py:122-131`

**Issue:** The docstring states the field is "a single-element list" and the body does `return pin_field[0]`. On an empty list (e.g. a malformed user `~/.firestarter/pinmaps.json` override with `"vpp-pin": []`) this raises `IndexError`, which is not caught anywhere in `_generate_pin_names_for_display` and would abort `firestarter info`. On a multi-element list it silently uses only the first element with no warning. The packaged `pinouts.json` is clean (all such fields are exactly one element, verified), so this is latent rather than active, but the helper was added specifically to harden this extraction and currently does not defend its own contract.

**Fix:** Guard the access and degrade gracefully:

```python
@staticmethod
def _first_pin(pin_field: list) -> int | None:
    if not isinstance(pin_field, list) or not pin_field:
        logger.warning("Expected single-element pin list, got %r", pin_field)
        return None
    if len(pin_field) > 1:
        logger.warning("Pin field %r has >1 element; using first", pin_field)
    return pin_field[0]
```

Callers at lines 407-421 already handle `None` (the `if ... is not None` guards), so returning `None` is consistent with the existing call sites.

## Info

### IN-01: `interpret_timing` ignores `0x0D` after the WARNING-5 override flips `0x07 → 0x0D`

**File:** `firestarter_app/tools/build_db.py:330-341, 489, 588-592`

**Issue:** The WARNING-5 override (line 489) and the fm1608 override (line 513) mutate `proto_id` (e.g. `0x07 → 0x0D`, `0x07 → 0x28`) **before** `interpret_timing` is called with the mutated `proto_id` (line 590-592). For the ~23 chips flipped to `0x0D`, `interpret_timing` now returns `"Algorithm Controlled"` instead of the microsecond pulse value the raw `pulse_delay` carries. This is arguably correct (28C-family EEPROMs are DQ7-polled, not fixed-pulse), but it is an undocumented behavioral consequence of override ordering, and `_parse_pulse_duration` will then yield `pulse-delay: 0` for those parts. Confirm this is intended; if the raw pulse value is still wanted for display, capture it before the overrides run.

### IN-02: `interpret_timing` comment overstates the fix ("microseconds for ALL protocols") while the code only emits a value for three protocols

**File:** `firestarter_app/tools/build_db.py:331-341`

**Issue:** The comment says "Raw pulse_delay is microseconds for ALL protocols — no multiplier," but the function returns `"Algorithm Controlled"` for every protocol outside `(0x07, 0x08, 0x0B)`. The comment and behavior do not match; a future reader may assume `0x05/0x06/0x0D/0x10` also emit a microsecond value. Tighten the comment to state that only the three EPROM-family algorithms carry a meaningful fixed pulse and the rest are algorithm-controlled.

### IN-03: `resolve_pinout_key` accepts `flags` parameter that is never used

**File:** `firestarter_app/tools/build_db.py:266`

**Issue:** `resolve_pinout_key(pin_count, variant, flags_int, pm_idx=None, proto_id=None)` declares `flags_int` but never references it in the body. The caller at line 435-437 passes `flags` positionally. Dead parameter — remove it (and the corresponding caller argument) or document why it is reserved.

---

_Reviewed: 2026-06-08_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
