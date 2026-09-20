---
phase: 198-the-two-voltage-nibbles
reviewed: 2026-09-18T00:00:00Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - firestarter_app/tools/build_db.py
  - firestarter_app/tools/datasheet_overrides.json
  - firestarter_app/tests/test_vpp_decode_table.py
  - firestarter_app/tests/test_vcc_margin_rail.py
  - firestarter_app/tests/test_datasheet_overrides.py
  - firestarter_app/tests/test_wire_dict_equivalence.py
  - firestarter_app/tests/golden/wire_dict_expected_deltas_198.json
  - firestarter_app/tools/DECODE-NOTES.md
findings:
  critical: 0
  warning: 1
  info: 2
  total: 3
status: issues_found
---

# Phase 198: Code Review Report

**Reviewed:** 2026-09-18T00:00:00Z
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Phase 198 completes two decode tables in `build_db.py` (`VPP_MV` gains exact-match entries
`0xF1`/`0xF2`; `VCC_VOLTAGES` grows from 6 to 15 entries), adds 12 `UNSOURCED` carve-out
override entries plus 3 datasheet-cited Fujitsu corrections to `tools/datasheet_overrides.json`,
and extends the wire-dict/vdd-vcc test suites accordingly. I traced the diff against
`0372cc6..HEAD` line by line, re-derived the exact-match VPP logic and the VCC completion by
hand, and cross-checked every new override entry, test assertion, and count against the actual
committed `chip_database.json` and the snapshot/golden fixtures using short verification
scripts (not the file text alone). Everything checked out numerically: 22 total override
entries / 18 `UNSOURCED` / 12 held 0x06-carve-outs / 28 `vdd<vcc` rows / 2 wire-dict VPP deltas /
18-entry `VPP_MV` / 15-entry `VCC_VOLTAGES` — all match what the code and data actually produce,
and the 46 directly-relevant tests I ran locally are green. I found no BLOCKER-class defect: the
exact-match-before-mask ordering is correct and disjoint from the masked domain, the override
loader's abort path is exercised correctly by the new fixtures, and no new value collides with
an already-decoded rail in a way that silently produces a wrong number. The one WARNING below is
a latent, undisclosed ambiguity in the new exact-match logic that the phase's own documentation
comes close to but does not name directly. Two INFO items note a pre-existing test smell this
phase's diff touches, and a minor internal-consistency point in the new documentation.

`firestarter_app/firestarter/data/chip_database.json` (generated artifact) and
`firestarter_app/tests/__snapshots__/test_characterization.ambr` (syrupy snapshot) were
deliberately **not** line-reviewed per the review scope notes; both were queried programmatically
instead (see Warnings/Info below and the verification performed for this report).

## Warnings

### WR-01: `0xF1`/`0xF2` exact-match rails are not distinguished from an option-flagged `0xF0` rail at the bit level

**File:** `firestarter_app/tools/build_db.py:78, 681-685`
**Issue:** The deleted comment this phase removed (previously at `VPP_MV`'s definition) documented
that the VPP low byte packs two sub-fields: bits 7-4 are the rail index, bits 3-0 are "option
flags" — which is why every pre-198 key had a zero low nibble and the decode masked with `& 0xF0`.
The two new keys, `0xF1` and `0xF2`, are *not* instances of that pattern — they are two entirely
distinct DAC-table indices from upstream's `xg_vpp_voltages[]` that happen to also have a non-zero
low nibble. The new code correctly exact-matches them first via `_VPP_EXACT_LOW_BYTES`, so today's
767-row filtered population (where no row carries either value) decodes without ambiguity. But if
upstream ever emits a row whose low byte is the *option-flagged* rail `0xF0` combined with the
low bit set — i.e. a literal `0xF1` meaning "rail 0xF0 (18000 mV) + option flag" rather than "the
distinct 25000 mV rail" — `_d_vpp_mv` would silently resolve it to 25000 mV instead of 18000 mV.
There is no way to distinguish the two readings from the raw byte alone, and nothing in the code
or `DECODE-NOTES.md` §9 states which reading wins if that byte is ever observed on a real chip
(§9's D-16 discussion comes close — it discusses `0xF1`/`0xF2` as a "dead branch" and flags the
option-flag reading as the generator's own unattested working theory — but it does not name this
specific collision between the two theories). A future `infoic.xml` update introducing exactly
this byte would ship a silently-wrong 7000 mV VPP figure with no test catching it, because
`_VPP_EXACT_LOW_BYTES` by construction always wins over the mask.
**Fix:** Not a required fix for this phase (the branch is unreachable against the pinned
`infoic.xml`), but worth naming explicitly in `DECODE-NOTES.md` §9's "surviving silent fallback"
discussion so a future maintainer who does see `0xF1`/`0xF2` on a real row knows this ambiguity
exists before trusting the exact-match value, e.g.:
```
Because 0xF1 and 0xF2 are the only two VPP_MV keys with a non-zero low nibble, a future chip
whose low byte happens to be one of these values from the option-flag pattern (rail 0xF0 +
option bit) rather than the distinct xg_vpp_voltages[] index would be silently misdecoded by
the exact-match branch. This has not been observed and cannot be resolved from the raw byte
alone; treat a newly-observed 0xF1/0xF2 row as requiring manual disambiguation, not a free
decode.
```

## Info

### IN-01: `TestVddBelowVccPredicate` re-opens and re-parses `chip_database.json` independently in each of its two test methods

**File:** `firestarter_app/tests/test_datasheet_overrides.py:485-524`
**Issue:** `test_the_28_row_group_is_exact_and_matches_the_5500_rail` and
`test_the_three_buckets_partition_the_whole_population` each independently `open()` and
`json.load()` the 433 KB `chip_database.json`, duplicating work that every other real-DB test in
this module (and in `test_vcc_margin_rail.py`, via `_load_db`) already factors into a shared
helper. This isn't a correctness bug — each test's `rows`/`below`/`at_5500` lists are internally
consistent because they're derived from that same single in-test load, so the `id()` comparison
in the first test is valid — but it's an avoidable duplication the rest of the module already
solved.
**Fix:** Factor the load into a shared module-level fixture or reuse `_load_db`/`_DB_FILE` from
`test_vcc_margin_rail.py`'s pattern, e.g. a `@pytest.fixture(scope="module")` that loads once and
is passed into both test methods.

### IN-02: `DECODE-NOTES.md` §9's positive-confirmation VCC argument is stated only for `vdd`, but the same three rows' `vcc_mv` also lands on a value the datasheets never mention

**File:** `firestarter_app/tools/DECODE-NOTES.md:419-427`
**Issue:** The "positive confirmation" paragraph argues that `VCC_VOLTAGES[0x04]` (5500) cannot
represent the three Fujitsu datasheets' 5.75-6.25 V program-VCC band, and that the override
correctly moves `electrical.vdd_mv` to the datasheet's 6000. That argument is sound and I
independently confirmed the three rows now emit `vdd_mv: 6000` in the live database. The section
is silent, however, on what `electrical.vcc_mv` reads for these same three rows post-override —
I confirmed it is 5000 (the read/verify rail, unrelated to the datasheet's program-VCC figure, and
untouched by this phase). That's very likely correct given the codebase's existing vcc/vdd split
(vcc = read rail, vdd = elevated program rail per the `SRAM`-only special case elsewhere in
`build_db.py`), but the section's framing ("VCC = 6.0 V ± 0.25V" quoted from the datasheet) reads,
on a skim, as if it corroborates `vcc_mv` specifically, when the field it actually corrects is
`vdd_mv`. This is a documentation-clarity note, not a decode defect — the code path is right.
**Fix:** Optional. If `DECODE-NOTES.md` §9 is revised again, consider one clause making explicit
that the datasheet's "program VCC" reading maps onto this codebase's `vdd_mv` field, not
`vcc_mv`, to pre-empt a future reader assuming the two are being conflated.

---

_Reviewed: 2026-09-18T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
