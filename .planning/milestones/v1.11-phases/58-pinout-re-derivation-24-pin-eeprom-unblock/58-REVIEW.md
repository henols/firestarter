---
phase: 58-pinout-re-derivation-24-pin-eeprom-unblock
reviewed: 2026-06-09T00:00:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - firestarter_app/tools/build_db.py
  - firestarter_app/tests/test_decoder.py
findings:
  critical: 0
  warning: 5
  info: 3
  total: 8
status: issues_found
---

# Phase 58: Code Review Report

**Reviewed:** 2026-06-09
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

Phase 58 rewrote `resolve_pinout_key` as a principled, data-driven function and
added five Wave 0 test classes. I focused on the SAFETY-CRITICAL invariant: no
chip may be assigned a VPP-asserting pinout when VPP would land on a WE/RW pin
of a 5V part.

**The core safety invariant holds in the generated artifact.** I ran a direct
cross-check over the committed `chip_database.json`:

- Zero chips on a VPP pinout (`DIP24_2716`, `DIP24_2732`, `DIP28_2764`,
  `DIP28_27256`, `DIP28_27512`, `DIP32_STD`) carry an EPROM algorithm
  (0x07/0x08/0x0B) while being tagged `Flash/EEPROM` or `SRAM`.
- Zero non-UV-EPROM chips landed on `DIP24_2716` (the pin-21-VPP hazard layout).

So I found **no shipping VPP-routing hazard** in the current output, and no
Critical findings. The function passes its own test suite (verified by running
`TestResolvedPinoutKey` + `TestGuessTablesDeleted` — all green).

However, the *robustness* of the rule structure depends on several undocumented
runtime assumptions that, if upstream `infoic.xml` shifts, would silently
re-introduce the hazard the phase exists to prevent. Those are the WARNING
findings below. The most important is WR-01: the safety of the most dangerous
fall-through (24-pin type=4 EPROM-proto parts) rests entirely on a proto-flip
in a *different* function (`main()` Rule 3), with no defense inside
`resolve_pinout_key` and no test covering it.

## Warnings

### WR-01: 24-pin type=4 FRAM/SRAM with pm_idx=23 resolves to a VPP pinout; safety depends solely on the Rule 3 proto-flip in main()

**File:** `firestarter_app/tools/build_db.py:161-178, 423-445`

**Issue:** A 24-pin `type_int==4` chip (e.g. Ramtron FM1208-class FRAM, which
upstream tags type=4 with an EPROM protocol 0x07/0x0B — the exact mislabel
Rule 3 exists to defend against) is resolved by `resolve_pinout_key` purely on
`pm_idx`. If such a chip reports `pm_idx==23` with `variant_lo` other than
0x01/0x10, it falls into the `else` at line 173-174 and is assigned
`DIP24_2716` — which has `vpp-pin=[21]`. Pin 21 is WE on a 5V FRAM. The only
thing that saves it is Rule 3 (line 423) flipping `proto_id` to 0x28
(configure_sram, which never asserts VPP).

The inline comment at lines 443-445 *asserts* "24-pin SRAM chips (FM1208) route
to DIP24_6116 via resolve_pinout_key (pm_idx=0)" — but `resolve_pinout_key`
does NOT consult `type_int` in the 24-pin branch at all (only the 28-pin pm_idx=0
and 32-pin branches do). Nothing guarantees a 24-pin type=4 part has pm_idx=0.
If upstream ever tags one with pm_idx=23, it gets the vpp-pinout, and the only
backstop is the algorithm flip in a different function. Unlike the 28-pin Rule 3
path (lines 425-436), there is no pinout reassignment for the 24-pin case, so
the emitted `pinout` field still references a layout with `vpp-pin`.

**Fix:** Make the 24-pin branch type-aware so SRAM/FRAM cannot land on a
VPP-bearing pinout regardless of pm_idx, mirroring the 28/32-pin branches:
```python
if pin_count == 24:
    if type_int == 4 or proto_id == 0x27:
        key = "DIP24_6116"          # SRAM/FRAM — never VPP, any pm_idx
    elif pm_idx == 23:
        ...
    elif pm_idx == 0:
        key = "DIP24_6116"
    else:
        key = None
```
At minimum, add a `pin_count == 24` pinout reassignment inside Rule 3 (line 425)
so the emitted pinout is forced to `DIP24_6116` when the proto is flipped, rather
than leaving `DIP24_2716` in the entry.

### WR-02: Rule 2 (WARNING-5) for DIP28_2764 relies on flags-based _etype, which the code elsewhere documents as unreliable for 28C parts

**File:** `firestarter_app/tools/build_db.py:354-357, 396-404`

**Issue:** The DIP28_2764 arm of Rule 2 (lines 400-404) only flips a 0x07 chip
to 0x0D EEPROM when `_etype == "Flash/EEPROM"`. That `_etype` comes from the
Pass-1 flags predicate `flags & 0x10` (line 354). But the comment at lines
167-169 explicitly states that many 28C EEPROM parts ship with `flags=0x0000`
("AM28C16A, CAT28C16A, XL2804A — confirmed RESEARCH Pitfall 1"). So a 28C-class
5V EEPROM that lands on `DIP28_2764` (vpp-pin=1) with `flags=0x0000` and
`proto=0x07` would NOT trigger Rule 2 and would keep 0x07 → configure_eprom →
12V on pin 1, which is A14/WE on a 5V part.

This is mitigated in practice because 28C-family parts are expected to cluster
at `pm_idx` 18/19/20 (no-VPP pinouts), so they should never reach DIP28_2764.
But Rule 2's whole purpose is to be the *safety net for when that assumption
fails* — and it is built on the one discriminator (`flags & 0x10`) the codebase
already proved unreliable for exactly these chips. The DIP28_28C256 arm of the
same rule (lines 396-399) correctly avoids the flags guard for this reason; the
DIP28_2764 arm did not get the same treatment.

**Fix:** For the DIP28_2764 arm, prefer a flags-independent discriminator
(e.g. `variant_lo` or `mem_size`, consistent with the 24-pin `variant_lo==0x10`
EEPROM discriminator the function already trusts) instead of `_etype`, or
document why DIP28_2764 can never carry a flags=0x0000 28C part. As written, the
"generalised safety net" is not generalised — it has a hole exactly where the
phase's own research says flags are unreliable.

### WR-03: 32-pin pm_idx==0 branch ignores proto_id/type_int and unconditionally assigns a flash pinout

**File:** `firestarter_app/tools/build_db.py:215-218`

**Issue:** The 32-pin `pm_idx == 0` branch assigns `DIP32_SST39SF040`
unconditionally, with a comment claiming it is "SRAM/NVRAM (type=4; proto
0x0E/0x29)". But unlike the 28-pin pm_idx==0 branch (line 202), this branch does
not actually check `type_int` or `proto_id`. Any 32-pin chip with pm_idx==0 —
including, hypothetically, a UV-EPROM (proto 0x07) — would receive the
`DIP32_SST39SF040` layout, which puts `rw-pin=31` and no VPP. The error
direction is *safe* (no VPP gets routed where it shouldn't), but a genuine
32-pin UV-EPROM mis-clustered to pm_idx=0 would be silently mapped to a 5V-flash
pinout and would fail to program (wrong WE/VPP/address mapping) with no warning.

**Fix:** Mirror the 28-pin branch — gate on `type_int == 4 or proto_id in
{0x0E, 0x29}` and return `None` (D-06 fail-safe) for anything else at pm_idx==0,
rather than blindly assigning a flash layout:
```python
if pm_idx == 0:
    if type_int == 4 or proto_id in {0x0E, 0x29}:
        key = "DIP32_SST39SF040"
    else:
        key = None
```

### WR-04: `flags_int` parameter is accepted but never used inside resolve_pinout_key

**File:** `firestarter_app/tools/build_db.py:139`

**Issue:** `resolve_pinout_key(pin_count, variant, flags_int, ...)` declares
`flags_int` as a positional parameter, and `main()` passes `flags` into it
(line 317), but the function body never references `flags_int`. It is dead.
Worse, its presence is misleading: a future maintainer may assume flags
participate in pinout selection when the design (and the comments at lines
167-169) deliberately do *not* use flags here. A dead positional parameter is
also a fragility: any caller passing args positionally could shift the
`pm_idx`/`proto_id`/`type_int` alignment.

**Fix:** Remove `flags_int` from the signature and from the call site at
line 317, or rename to `_flags_unused` and add a comment if it must stay for
call-site symmetry. Removing it is cleaner since all real call sites and tests
pass it positionally as the third arg (e.g. test line 847-849), so the tests
must be updated in lockstep.

### WR-05: Rule 1 fires on pinout identity alone and can override a genuinely non-EEPROM chip's protocol

**File:** `firestarter_app/tools/build_db.py:367-375`

**Issue:** Rule 1 forces `proto_id = 0x0D` for *any* chip whose `pinout_key ==
"DIP24_2816"`, with no guard on `type_int` or the original protocol. This is
correct for the intended 28C-EEPROM family. But because `resolve_pinout_key`
assigns `DIP24_2816` purely on `(pin_count==24, pm_idx==23, variant_lo==0x10)`
— never checking type or proto — a chip that happens to share those decoded
field values but is electrically something else (e.g. a future type=4 part with
variant_lo==0x10) would be silently forced onto the EEPROM algorithm. The
override is unconditional and irreversible within the loop. There is no
assertion that the chip's original proto was in the expected EPROM/EEPROM set.

This is lower-risk than WR-01/WR-02 because forcing 0x0D (configure_eeprom28c,
5V, no VPP) is the *safe* direction, but it can mis-program a non-EEPROM chip
that lands on this pinout. It also has no test: `TestResolvedPinoutKey`
verifies the pinout key but the Rule 1 proto-flip is only exercised indirectly
via the integration DB tests, none of which cover an unexpected type/proto on
variant_lo==0x10.

**Fix:** Add a sanity guard so Rule 1 only flips protocols that were plausibly
EPROM/EEPROM family, and log a WARN if a chip on DIP24_2816 arrives with an
unexpected original proto (e.g. SRAM proto 0x27) so the mis-cluster surfaces
instead of being silently coerced.

## Info

### IN-01: `tools` is not a package but tests import `from tools.build_db`

**File:** `firestarter_app/tests/test_decoder.py:703, 711, 719, 730, 758, 775` (and others)

**Issue:** `tools/` has no `__init__.py`, yet the Phase 57/58 tests do
`from tools.build_db import ...`. This currently works only because pytest's
default rootdir-prepend import mode puts the project root on `sys.path` (I
verified the import resolves and the tests pass). It is fragile: a change to
pytest import mode, `pythonpath`, or running the tests from a different CWD would
break every build_db test at collection time. The `firestarter` package is
properly packaged; `tools` is not.

**Fix:** Add an empty `tools/__init__.py`, or set
`pythonpath = ["."]` under `[tool.pytest.ini_options]` to make the dependency
explicit rather than relying on default rootdir behavior.

### IN-02: Stale module-docstring contract for KNOWN_PROTOCOLS in firestarter_app/CLAUDE.md vs build_db.py

**File:** `firestarter_app/tools/build_db.py:101-113`

**Issue:** `firestarter_app/CLAUDE.md` documents the known-protocol set as
including `0x35, 0x39`, but Phase 57 correctly removed those (build_db.py
KNOWN_PROTOCOLS no longer contains them, per the verified comment at lines
98-100). The project doc is now out of sync with the source of truth. Not a
code defect, but it will mislead future maintainers and any cross-repo sync.

**Fix:** Update the "Known protocols" line in `firestarter_app/CLAUDE.md` to
match the 11-entry KNOWN_PROTOCOLS set in build_db.py.

### IN-03: `interpret_timing` swallows all exceptions to a silent 0

**File:** `firestarter_app/tools/build_db.py:241-244`

**Issue:** `except Exception: val = 0` silently maps any malformed `pulse_delay`
to "0 us". This is intentional (test `test_interpret_timing_non_hex_falls_back_to_zero`
pins it) and the bare-except was already narrowed to `except Exception` per
DEC-03, so this is acceptable. Minor: a malformed timing value silently becomes
a real-looking "0 us" with no WARN, so a corrupt upstream entry would produce a
plausible-but-wrong programming pulse with no signal. A one-line WARN on the
except path would make data corruption visible without changing behavior.

**Fix:** Add `print(f"WARN: unparseable pulse_delay {raw_hex!r}", file=sys.stderr)`
in the except branch.

---

_Reviewed: 2026-06-09_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
