---
phase: 76-spec-only-gaps-adapter-required-x88c64
reviewed: 2026-06-18T00:00:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - firestarter_app/tools/build_db.py
  - firestarter_app/tests/test_build_db_inclusion.py
findings:
  critical: 0
  warning: 2
  info: 3
  total: 5
status: issues_found
---

# Phase 76: Code Review Report

**Reviewed:** 2026-06-18
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

Phase 76 plan 01 adds a NAME-keyed `adapter-required` rule arm for the AT28C04/AT28C16
family to `tools/build_db.py` (D-03) and rewords the X88C64P `unsupported_reason` to be
datasheet-accurate (D-02), plus two RED regression tests. Only the two source files in scope
were reviewed; the regenerated `chip_database.json` and the 76-02 markdown specs were treated
as out of scope (codegen output / documentation).

**Adversarial verdict — the safety claim does NOT hold as written, but the safety OUTCOME does.**
I verified against the live regenerated DB:

- **No chip graduated to `supported`.** Status counts: 730 supported, 9 adapter-required,
  4 vpp-exceeds-max, 1 protocol-not-implemented. No graduation. (T-76-01 holds.)
- **No 12V-VPP dispatch hazard introduced.** All 9 named-arm chips resolve to `pinout=DIP24_2816`
  with `algorithm=0x0D` (`configure_eeprom28c`, 5V, no VPP regulator). None routes to an
  EPROM-family (0x07/0x08/0x0B → `configure_eprom` 12V) handler.
- **Both gates green.** `diff_db.py` exit 0 (10-chip RULE_PHASE66, reason-string-only,
  no status/dispatch delta); `check_dispatch.py` exit 0 (744 chips, 730 supported,
  14 non-dispatchable, 0 violations). `ruff check`/`ruff format --check` clean. Inclusion
  tests pass.
- **X88C64P reword is correct.** `support_status` stays `protocol-not-implemented`,
  `algorithm=0x34` unchanged, reason no longer contains "serial-parallel hybrid", retains
  the "protocol not implemented" substring required by the pre-existing typed-refusal test.

The key defect is **WR-01**: both the in-code comment and the SUMMARY assert a false invariant
("proto_id is already NON_DISPATCHABLE_ALGO from Site B"). I traced the codegen: these 9 chips
do **not** pass through Site B at all — Site B never fires for them, and their `algorithm`
ends up `0x0D` (a *real, dispatchable* handler), set later by Step 4 Rule 1, not demoted to
`0x00`. The chips stay safe only because (a) they route to the no-VPP `configure_eeprom28c`
handler and (b) the host guard in `chip_resolver.resolve_chip` refuses every non-supported chip.
The comment misdescribes *why* the chip is safe, which is a latent-hazard documentation rot:
a future maintainer trusting "Site B already demoted proto_id" could relocate the named arm or
rely on a `0x00` algorithm that is not actually present.

## Warnings

### WR-01: Code comment and SUMMARY assert a false safety invariant — named-arm chips are NOT demoted by Site B

**File:** `firestarter_app/tools/build_db.py:418-419` (also `76-01-SUMMARY.md:20,39,81`)

**Issue:** The named-arm comment states:

```
# proto_id is already NON_DISPATCHABLE_ALGO
# from Site B — do NOT re-demote it here (Site B handles that invariant).
```

This is false for the 9 chips the arm actually matches. I verified in the regenerated DB that
all 9 AT28C04/AT28C16 matches carry `programming.algorithm = 13 (0x0D)`, **not** `0x00
(NON_DISPATCHABLE_ALGO)`. Tracing `build_db.py`: Site B (line 391) requires
`pin_count == 24 AND proto_id in (0x07,0x08,0x0B) AND flags & 0x10`. These chips do not satisfy
that arm in a way that demotes them — instead they resolve to `pinout_key == "DIP24_2816"` and
get `proto_id = 0x0D` assigned by **Step 4 Rule 1** (line 506-508), which runs *after* both the
named arm and Site B. So at runtime the chip is dispatchable to `configure_eeprom28c` (a real
handler), and `dispatch(0x0D, ...) == "configure_eeprom28c"` in `check_dispatch.py:137-138`.

The chip is *electrically* safe (configure_eeprom28c asserts no VPP regulator; pinout is
DIP24_2816), and the host guard (`chip_resolver.resolve_chip` refusing every non-supported chip
before any wire dict) is the authoritative control — so this is not a live hazard today. But
the comment documents a non-existent invariant. If a maintainer ever (a) moves the named arm,
(b) adds a chip to `_AT28C_DIP24_NAMES` that does NOT resolve to DIP24_2816, or (c) deletes the
host guard trusting "Site B demoted proto_id", the false premise becomes a real 12V-VPP path.
This is the exact class of latent-hazard documentation rot the gate architecture is meant to
prevent.

**Fix:** Correct the comment to describe the actual mechanism, e.g.:

```python
# Named rule arm: AT28C04/AT28C16 family (D-03, Phase 76).
# These chips resolve to pinout DIP24_2816 and are assigned algorithm 0x0D
# (configure_eeprom28c, 5V, no VPP) by Step 4 Rule 1 below — they do NOT pass
# through Site B's NON_DISPATCHABLE_ALGO demotion. They remain non-dispatchable
# in practice ONLY via the host guard (chip_resolver.resolve_chip refuses every
# support_status != "supported" chip before any wire dict). This arm changes only
# the reason string; it must NOT be relied upon to demote proto_id.
```

Also correct the corresponding claims in `76-01-SUMMARY.md` (decision D-03, "What Was Built",
and deviation #1) which repeat the same false statement.

### WR-02: Plan must_have required a 1-chip RULE_PHASE66 delta; implementation produced a 10-chip delta

**File:** `firestarter_app/tools/build_db.py:444-449` (effect observed via `diff_db.py`)

**Issue:** The plan's `must_haves.truths` and Task-2/Task-3 acceptance criteria explicitly state
"diff_db.py is green with **exactly a 1-chip** RULE_PHASE66 reason-string delta (no
support_status / dispatch delta)". The actual delta is **10 chips** (9 AT28C04/16 + X88C64P) —
because the named arm overwrites the reason string of all 9 family chips (which previously carried
the generic Site B text in the baseline). The SUMMARY records this as accepted, citing Task-3
prose that permits "additional adapter-required reason-string deltas ... classify cleanly as
RULE_PHASE66 with no status/dispatch change". The deviation is electrically benign (verified:
no status/dispatch change for any of the 10 chips) but it directly contradicts a top-level
`must_haves` truth and two acceptance criteria, so the implementation does not satisfy the plan
as written.

**Fix:** Either (a) reconcile the must_have to read "≤10-chip reason-string-only RULE_PHASE66
delta" to match the implemented intent, or (b) if a true 1-chip delta was required, scope the
named-arm reason rewrite to leave the 8 non-AT28C16 family members on the Site B reason. Option
(a) matches the realized, gate-clean behavior and is the lower-risk reconciliation. No code change
is strictly required for safety — this is a plan/implementation contract mismatch that should be
recorded explicitly so downstream consumers (verification, milestone audit) do not flag the
10-vs-1 discrepancy as an unexplained regression.

## Info

### IN-01: `_AT28C_DIP24_NAMES` is a constant rebuilt on every chip iteration

**File:** `firestarter_app/tools/build_db.py:425-440`

**Issue:** `_AT28C_DIP24_NAMES` is a 14-element frozen literal that is reconstructed on every
iteration of the per-chip loop (it is defined inside the `for ic in mfg.findall(...)` body). It is
semantically a module-level constant — the `_`-prefixed UPPER_CASE name signals exactly that — but
its placement inside the loop is inconsistent with the convention used elsewhere in the file
(e.g. `NMOS_TRUE_VPP_MV`, `KNOWN_PROTOCOLS` are module-level). Performance is out of v1 scope, but
this is a naming/placement convention inconsistency.

**Fix:** Hoist the set to module scope alongside `KNOWN_PROTOCOLS` / `NMOS_TRUE_VPP_MV` and
reference it inside the loop. No behavior change.

### IN-02: New test docstring claims a negative assertion that the test does not perform

**File:** `firestarter_app/tests/test_build_db_inclusion.py:481-482`

**Issue:** `test_at28c16_named_arm_reason_mentions_adapter_doc` docstring point 3 states the reason
"Does NOT contain 'DIP24_2716 pinout maps to the 12V VPP rail' (that is the old generic Site B
wording; named arm overwrites it)". No assertion enforces this negative. The test only checks
`startswith("adapter required:")` and `"AT28C04-ADAPTER.md" in reason`. The positive
`AT28C04-ADAPTER.md` check incidentally distinguishes named-arm from Site B wording, but the
docstring overstates the test's contract.

**Fix:** Either add the negative assertion
`assert "DIP24_2716 pinout maps to the 12V VPP rail" not in reason` or drop point 3 from the
docstring so it matches what is actually asserted.

### IN-03: New AT28C16 test can vacuously pass if the chip is reclassified away from adapter-required

**File:** `firestarter_app/tests/test_build_db_inclusion.py:492-502`

**Issue:** The loop body does `if chip.get("support_status") != "adapter-required": continue`,
mirroring the pre-existing `test_adapter_required_reason_starts_with_adapter_required`. `assert
found` only guarantees an AT28C16 entry exists, not that any entry reached the inner assertions.
If a future build regression reclassified every AT28C16 alias to `supported`, this test would pass
green without asserting the named-arm reason at all — masking exactly the kind of graduation the
phase is meant to forbid.

**Fix:** Track whether at least one chip was asserted and fail if none was, e.g.:

```python
checked = 0
for mfg, chip in found:
    if chip.get("support_status") != "adapter-required":
        continue
    checked += 1
    ...assertions...
assert checked, "no AT28C16 alias was adapter-required — named-arm reason never asserted"
```

---

_Reviewed: 2026-06-18_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
