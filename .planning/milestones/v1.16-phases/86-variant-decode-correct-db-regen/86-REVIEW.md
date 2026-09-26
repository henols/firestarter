---
phase: 86-variant-decode-correct-db-regen
reviewed: 2026-06-25T00:00:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - firestarter_app/tools/build_db.py
  - firestarter_app/tools/diff_db.py
  - firestarter_app/tools/extra_chips.json
findings:
  critical: 0
  warning: 2
  info: 4
  total: 6
status: issues
---

# Phase 86: Code Review Report

**Reviewed:** 2026-06-25
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found

## Summary

Reviewed the Phase-86 variant-decode rewrite: the new `classify()` classifier
(`build_db.py` ~L283-368) that replaced the deleted Rule 1/2/3 override stack, the
post-decode `extra_chips.json` supplement merge (~L732-761), the `VARIANT_DECODE` /
`EXTRA_CHIPS_SUPPLEMENT` diff-gate labels in `diff_db.py`, and the curated
`extra_chips.json` (2516/2532).

**Safety verdict — the load-bearing invariant holds.** I traced every `classify()`
output path against the 12V-on-a-no-VPP-pin hazard and could not construct a
violation. I independently re-ran both gates against the regenerated DB:
`check_dispatch.py` → `PASS (746 chips, 0 violations)` and `diff_db.py` →
`PASS (0 unexplained, 0 missing)`. I also verified the arm-2 over-broadening fix the
executor already caught: `AT29C256` / `AT29LV256` (proto 0x05 Flash on
`DIP28_28C256`) correctly stay `Flash/EEPROM` because arm-2 is scoped to
`proto_id in {0x07,0x08,0x0B}`. No 28-pin/24-pin EPROM-family chip routes to
`configure_eprom` on a no-VPP pinout, and every `DIP28_2764` chip is a genuine 0x07
UV-EPROM (the deleted WARNING-5 is correctly backstopped). The `MINIPRO_XML_URL` is
pinned to a SHA (`a8efaedc…`), so the regen is deterministic.

No Critical findings. Two Warnings concern the supplement-merge curation (vendor-key
split and absent collision detection), neither of which is a safety or correctness
defect in the current data but both of which are latent traps for future edits. Four
Info items cover a pre-existing classification inconsistency the rewrite preserves,
stale rationale text, and a documented over-spec VPP on the supplement rows.

## Structural Findings (fallow)

No `<structural_findings>` block was provided for this review.

## Narrative Findings (AI reviewer)

## Warnings

### WR-01: Supplement manufacturer key `"TEXAS INSTRUMENTS"` splits the vendor from the decoded `"TI"` group

**File:** `firestarter_app/tools/extra_chips.json:2` (and merge at `build_db.py:751-754`)
**Issue:** The supplement keys both records under manufacturer `"TEXAS INSTRUMENTS"`,
but the infoic.xml decode emits Texas Instruments parts under the key `"TI"` (32
records — `TMS2764`, `TMS27C128`, `SMJ27C128`, etc.). The
`complete_db.setdefault(mfg_name, []).extend(...)` merge therefore creates a *second,
separate* manufacturer group containing only 2516/2532 instead of appending them to
the existing TI vendor group. The generated DB now lists the same physical vendor
under two distinct keys (`"TI"` with 32 chips and `"TEXAS INSTRUMENTS"` with 2). This
is not a safety or lookup defect (part-number resolution is alias-keyed, and both
gates pass), but it is a data-curation defect: any consumer that groups or counts by
manufacturer sees TI twice, and a maintainer adding more TI supplements will not find
the existing TI parts under the supplement key.
**Fix:** Use the same manufacturer key the decoder emits so the records merge into the
existing group:
```json
{
  "TI": [
    { "source": "non-upstream-supplement", "part_number": "2516", ... },
    { "source": "non-upstream-supplement", "part_number": "2532", ... }
  ]
}
```
(Verify the exact decoded key with
`python -c "import json;print('TI' in json.load(open('firestarter/data/chip_database.json')))"`
before re-pinning; then re-run `build_db.py` + re-pin the baseline.)

### WR-02: Supplement merge has no key-collision / duplicate-record detection

**File:** `firestarter_app/tools/build_db.py:748-755`
**Issue:** The merge blindly `extend()`s supplement records onto whatever list already
exists for `mfg_name`:
```python
complete_db.setdefault(mfg_name, []).extend(extra_chips)
```
If a supplement `part_number` ever coincides with a decoded part under the same
manufacturer key (e.g. a future supplement entry, or upstream later adding a `2516`
to infoic.xml), the merge silently produces **two records with the same
part_number**. Nothing warns. Downstream, `EpromDatabase.get_eprom` would resolve to
whichever record it indexes first (non-deterministic precedence between the
upstream-decoded and supplement wire values — a quiet wrong-wire-values hazard on
exactly the safety-critical path this phase exists to protect), and `diff_db._make_index`
would merely disambiguate the collision by positional index rather than flag it. The
review brief explicitly asked about this collision behavior; today no collision exists
(2516/2532 are confirmed absent from infoic.xml), so this is latent, but the merge is
the one place a future regression could re-introduce a misclassified duplicate without
any gate catching it at merge time.
**Fix:** Detect and refuse/warn on a part_number that already exists for the target
manufacturer before extending:
```python
existing = {c.get("part_number") for c in complete_db.get(mfg_name, [])}
for rec in extra_chips:
    pn = rec.get("part_number")
    if pn in existing:
        print(f"ERROR: supplement {mfg_name}/{pn} collides with a decoded record",
              file=sys.stderr)
        sys.exit(1)
complete_db.setdefault(mfg_name, []).append(rec)
```

## Info

### IN-01: `classify()` labels proto-0x0D `DIP32_28C512_EEPROM` chips `Flash/EEPROM` while their DIP24/DIP28 cousins get `EEPROM`

**File:** `firestarter_app/tools/build_db.py:346-360`
**Issue:** Arm 2 re-types proto-0x0D 5V EEPROMs to `EEPROM` only when the resolved
pinout is `DIP24_2816`, `DIP28_28C64`, or `DIP28_28C256`. The 18 proto-0x0D chips that
resolve to `DIP32_28C512_EEPROM` skip arm 2 and fall through to arm 4 (Flash families
includes `0x0D`), so they decode as `Flash/EEPROM`. The result is an inconsistent
catalog: a 28C-family 5V EEPROM is `EEPROM` in DIP24/DIP28 packages but
`Flash/EEPROM` in its DIP32 package. This is pre-existing (the baseline already had
these 18 as `Flash/EEPROM`, which is why `diff_db.py` reports 0 changes), and it is
not a safety issue — all 0x0D chips dispatch to `configure_eeprom28c` (5V, no VPP
regulator) and `DIP32_28C512_EEPROM` is in the no-VPP-pin set. But the rewrite was the
opportunity to make the type derivation consistent, and the `VARIANT_DECODE` rationale
in `diff_db.py` (L128-131) reads as if *all* proto-0x0D-pinout chips become `EEPROM`,
which is not what the code does for the DIP32 cluster.
**Fix:** Either add `DIP32_28C512_EEPROM` to the arm-2 pinout set so all 0x0D 28C-family
parts type consistently as `EEPROM`, or document the DIP32 exception explicitly in the
arm-2 comment and the `VARIANT_DECODE` rationale. (If changed, this moves 18 records'
`electrical.type` and must re-pin the baseline; gate it through `diff_db.py`.)

### IN-02: Stale `algo=0x29` claim in the `RULE_ALGO` rationale contradicts the corrected FM1608 identity

**File:** `firestarter_app/tools/diff_db.py:54`
**Issue:** The `RULE_ALGO` rationale string still says
`"Rule 3: fm1608 FRAM chips corrected to algo=0x29 (SRAM_512K_1M)."` Phase 86 deleted
Rule 3 and `DECODE-NOTES.md §5` explicitly corrects the decimal-40↔hex-0x28 / 0x29
conflation: the classifier emits **algorithm 0x28 (SRAM_STD)** for FM1608, which the
generated DB confirms (`algo=40`). The rationale text is historical/no-longer-accurate
and could mislead a future reader auditing a diff.
**Fix:** Update the `RULE_ALGO` rationale (or note that Rule 3 is superseded by the
`VARIANT_DECODE`/`RULE_PHASE84_RELABEL` labels) to state FM1608 → algorithm 0x28
(SRAM_STD), matching `DECODE-NOTES.md §5`.

### IN-03: Supplement rows declare `vpp_mv: 25000`, above the ~22V the RURP hardware can actually deliver

**File:** `firestarter_app/tools/extra_chips.json:16-17,42-43`
**Issue:** Both 2516 and 2532 carry `vpp_mv: 25000` / `vpp: "25V"`. The `build_db.py`
NMOS comment (L66-69) and `RURP_VPP_CEILING_MV` notes record that the RURP boost
regulator tops out at ~22V, so a 25V part cannot actually be programmed on this
hardware. These rows bypass `classify()` and the Site-C NMOS ceiling check entirely
(by design — they arrive fully-specified), so the `vpp-exceeds-max` demotion that
`build_db.py` applies to `M2716`/`M2732` does **not** apply to them; they ship
`support_status: "supported"` with a 25V declaration. This is mitigated — both are
`verification_status: "UNVERIFIED"` and not write-graduated, the provenance note is
honest, and `check_dispatch.py`'s `configure_eprom` invariant `(0, 25000)` is satisfied
at the inclusive boundary — so it is informational, not a defect. But the 25V value
is internally inconsistent with the project's own stated hardware ceiling for a
`supported` chip.
**Fix:** No code change required given the UNVERIFIED posture. Optionally add a one-line
note in the `provenance`/`verification_note` that 25V exceeds the ~22V RURP delivery
ceiling so a future graduation attempt does not assume the rail is reachable, or align
the wire `vpp_mv` to the actual deliverable rail when/if the part is bench-validated.

### IN-04: Broad `except Exception` clauses swallow root-cause detail in the fetch/parse paths

**File:** `firestarter_app/tools/build_db.py:376, 391, 415`
**Issue:** Three `except Exception` blocks: L376 (`interpret_timing` int-parse → 0),
L391 (network fetch / XML parse → `print(e); sys.exit(1)`), and L415 (per-IC field
parse → `continue`, silently dropping the chip). The L415 silent `continue` is the
notable one — a malformed `package_details`/`type`/etc. attribute drops the chip with
no diagnostic, so an upstream schema change could silently shrink the catalog without
any warning (the `diff_db.py` MISSING gate would catch a *baseline* chip vanishing, but
not a newly-malformed one). This is a tool, not runtime code, so the bar is lower, but
a one-line `WARN` on the dropped IC would make upstream-schema drift visible.
**Fix:** Narrow the per-IC catch to the expected parse error and log the skip:
```python
except (TypeError, ValueError) as e:
    print(f"WARN: skipping malformed IC '{ic.get('name')}': {e}", file=sys.stderr)
    continue
```

---

_Reviewed: 2026-06-25_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
