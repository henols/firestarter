---
phase: 59-correctness-gate-per-chip-diff-sram-audit
reviewed: 2026-06-09T00:00:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - firestarter_app/tools/build_db.py
  - firestarter_app/tools/diff_db.py
findings:
  critical: 1
  warning: 5
  info: 3
  total: 9
status: issues_found
---

# Phase 59: Code Review Report

**Reviewed:** 2026-06-09
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

Reviewed the two Phase 59 deliverables: the one-line determinism hardening in
`build_db.py` (`sort_keys=True`) and the new `diff_db.py` GATE-02 per-chip diff
tool. The `sort_keys=True` change itself is correct and achieves byte-stable
dict-key ordering. However the **central data structure of `diff_db.py` is
unsound**: it keys on `part_number`, but `part_number` is not unique. 65
part_numbers are duplicated across the 743-chip database (69 records collapse),
so `_make_index` silently overwrites colliding records — the diff is blind to
those chips and the "0 chips missing" / "all changed chips explained" PASS is
not trustworthy for them. This directly undermines the correctness-gate purpose
of the phase.

Secondary concerns: the `_classify_diff` priority logic masks compound changes
(17 chips have an algorithm change combined with other field deltas that go
unreported), the classifier only inspects 5 of ~10 chip fields, and the
"NEW chips — Rule 1 unblock" report label is hard-coded rather than verified.

## Critical Issues

### CR-01: Non-unique `part_number` index silently drops 69 chips from the diff

**File:** `firestarter_app/tools/diff_db.py:91-106` (`_make_index`)
**Issue:**
`_make_index` builds `idx[pn] = (mfg, chip)` keyed solely on `part_number`. The
docstring asserts exact-string match is correct, but `part_number` is **not
unique** in the database. Measured against the actual files:

- baseline: 734 records → 665 distinct part_numbers (65 duplicated keys)
- current: 743 records → 674 distinct part_numbers (69 records collapse)

On every key collision the later record overwrites the earlier one, so 69
current-DB records (e.g. `27CX010` ×3, `27CX256` ×3, `AM29F010,AM29F010B` ×2,
many `EN29*`/`PM29*` flash parts) never participate in the diff. Consequences
for a *correctness gate*:

1. A buggy change to a shadowed record is invisible → false PASS.
2. The `for pn in bl_idx: if pn not in cu_idx` missing-chip check (lines
   195-197) cannot detect a removed chip whose part_number is still present
   under a surviving duplicate → the "0 chips missing from baseline" claim
   (and the entire D-03 BLOCK contract on missing chips) is unreliable.
3. `bl_total`/`cu_total` (734/743) are printed from the raw record count, but
   the diff only ever reasons over ~665/674 keys — the report's own numbers are
   internally inconsistent, masking the gap.

The gate currently exits 0, so this defect is latent today, but it defeats the
stated purpose ("re-runnable per-chip DB diff"): the tool cannot prove what it
claims to prove for ~9% of the database.

**Fix:** Key on a tuple that is actually unique. The natural composite is
`(mfg_name, part_number)`, and where that is still ambiguous (same mfg lists the
same part_number twice), fall back to enumerating duplicates. Minimal version:

```python
def _make_index(db):
    idx = {}
    for mfg, chips in db.items():
        if not isinstance(chips, list):
            continue
        for i, chip in enumerate(chips):
            pn = chip.get("part_number", "")
            key = (mfg, pn)
            if key in idx:               # same mfg + pn appears twice
                key = (mfg, pn, i)       # disambiguate by position
            idx[key] = (mfg, chip)
    return idx
```

Then update the `new`/`missing`/`changed` set logic and all `sorted(...)` /
report formatting to operate on the composite key (project the displayed
part_number for printing). After the fix, assert
`len(idx) == sum(len(v) for v in db.values())` so a future collision regression
fails loudly instead of silently shadowing records.

## Warnings

### WR-01: `RULE_ALGO` early-return masks compound (algorithm + other) changes

**File:** `firestarter_app/tools/diff_db.py:142-143`
**Issue:**
`_classify_diff` returns `"RULE_ALGO"` immediately on any `algo_diff`, before
checking timing/voltage/pinout. Measured: 17 changed chips have an algorithm
change **plus** at least one other field delta (pulse_duration, vcc/vdd, or
pinout). All 17 are reported as pure algorithm corrections; the secondary
changes are never surfaced. For a correctness audit this is the failure mode
that matters — a legitimate algo flip could be co-bundled with an *unintended*
pinout or VPP change and the gate would still PASS and print only the benign
rationale. The docstring frames priority as "algo is the primary dispatch key
(any other field delta is secondary)" but provides no evidence the secondary
deltas are always benign.
**Fix:** Either (a) classify into a *set* of causes per chip and report every
matching cause, or (b) after matching `RULE_ALGO`, still test the remaining
predicates and append a `+BUG2`/`+BUG3`/`+SRAM_PINOUT` suffix so compound
changes are visible. At minimum, log the additional field deltas for any chip
where `algo_diff and (timing_diff or voltage_diff or pinout_diff)`.

### WR-02: Classifier ignores most chip fields → latent false BLOCK / false PASS

**File:** `firestarter_app/tools/diff_db.py:128-157`
**Issue:**
`_classify_diff` only inspects `programming.pulse_duration`,
`programming.algorithm`, `electrical.vcc`, `electrical.vdd`, and `pinout`. The
gate at line 188 (`if bl_chip != cu_chip`) compares the **entire** record, so a
change confined to any *uncovered* field — `electrical.vpp`, `electrical.vpp_mv`,
`electrical.size_bytes`, `electrical.pin_count`, `electrical.type`,
`programming.chip_id_check`, `programming.chip_id_value`, or `part_number`
formatting — falls through to `None` and triggers a D-03 BLOCK (exit 1) with
the chip labelled "unexplained," even when the change is fully intended.
Conversely a record that *also* shifts an uncovered field alongside a covered
one is mislabelled by the covered-field bucket. Today no chip hits this (0
verified), but the gate is one upstream-data change away from a spurious BLOCK
that the rationales cannot explain. Note in particular: BUG-3 was a vcc/vdd
*label swap*, which on many parts also changes `vpp`/`vpp_mv` interpretation —
those are not checked.
**Fix:** Make the covered-field set exhaustive relative to the equality check.
Compute the actual set of differing field paths (deep-diff the two records) and
assert every differing path is attributable to a known rule; route anything
else to `unexplained`. This keeps the gate honest: "unexplained" should mean
"a field changed that no rule predicted," not "a field changed that the
classifier forgot to look at."

### WR-03: "NEW chips — Rule 1 unblock" report label is hard-coded, not verified

**File:** `firestarter_app/tools/diff_db.py:222-224`
**Issue:**
The new-chips section header asserts every new chip arrived "via DIP24_2816 +
algo=0x0D" (Rule 1). This is a printed claim, not a checked invariant — the code
never inspects the new chips' `pinout`/`algorithm`. If a future regen adds a new
chip for any other reason, the report will still print "Rule 1 unblock,"
producing a misleading audit artifact. (The 9 current new chips do happen to be
DIP24_2816/0x0D, so it is correct today by coincidence.)
**Fix:** Either drop the causal claim from the header, or verify it:
```python
for pn in new_chips:
    c = cu_idx[<key>][1]
    if not (c["pinout"] == "DIP24_2816"
            and c["programming"]["algorithm"] == 0x0D):
        print(f"WARN: new chip {pn} is not a Rule 1 unblock "
              f"(pinout={c['pinout']}, algo={c['programming']['algorithm']:#x})")
```

### WR-04: Baseline/DB file open has no error handling — uncaught crash

**File:** `firestarter_app/tools/diff_db.py:165-168`
**Issue:**
Both `open(...)` calls and the two `json.load` calls run with no error handling.
A missing baseline (e.g. mis-set `FIRESTARTER_BASELINE_FILE`) raises an uncaught
`FileNotFoundError` traceback; malformed JSON raises an uncaught
`json.JSONDecodeError`. Verified: missing baseline produces a raw traceback and
exit 1. Exit 1 happens to collide with the BLOCK code, so a CI consumer that
keys only on the exit code will report a "gate failure" when the real cause is a
missing input file — a confusing/misleading signal for a correctness gate.
**Fix:** Wrap loads in try/except and emit a distinct, actionable message
(consider a distinct exit code, e.g. 2, for "infrastructure error" vs. 1 for
"diff BLOCK"):
```python
try:
    with open(BASELINE_FILE, encoding="utf-8") as f:
        bl_db = json.load(f)
except (OSError, json.JSONDecodeError) as e:
    print(f"ERROR: cannot load baseline {BASELINE_FILE}: {e}", file=sys.stderr)
    sys.exit(2)
```

### WR-05: `build_db.py` HTTP fetch has no timeout or status check (determinism caveat)

**File:** `firestarter_app/tools/build_db.py:255-256`
**Issue:**
`requests.get(MINIPRO_XML_URL)` has no `timeout=` (can hang indefinitely on a
stalled connection) and no `r.raise_for_status()`. On an HTTP error (404/5xx) the
error page body is fed straight into `ET.fromstring(r.content)`, which then
either raises a `ParseError` (caught, exits 1 — acceptable) or, worse, parses an
unexpected XML body and silently produces a wrong/empty database. This matters
for Phase 59 specifically: the determinism/byte-stability claim ("two
consecutive runs produce byte-identical output") only holds for a *fixed*
infoic.xml, but the script re-fetches live upstream on every run, so the DB is
not reproducible from the repo alone. That is a design property worth flagging
for a correctness gate that diffs against a pinned baseline.
**Fix:** Add `timeout=30` and `r.raise_for_status()`:
```python
r = requests.get(MINIPRO_XML_URL, timeout=30)
r.raise_for_status()
root = ET.fromstring(r.content)
```
Consider pinning the upstream XML (commit-pinned URL / vendored copy) so the
generated DB is reproducible and the baseline diff is meaningful run-to-run.

## Info

### IN-01: `bl_total`/`cu_total` printed from raw counts diverge from diffed key counts

**File:** `firestarter_app/tools/diff_db.py:174-175, 206-207`
**Issue:** The report prints "734 chips"/"743 chips" from raw record counts, but
the diff reasons over the de-duplicated index (665/674 keys). The two numbers
never reconcile in the output, which can mislead a reader into believing all
734/743 records were compared. (Resolved naturally once CR-01 is fixed and the
index is 1:1 with records.)
**Fix:** After fixing CR-01, `len(idx) == raw_total`; print the index size or
assert equality so the header count matches what was actually diffed.

### IN-02: `_classify_diff` docstring count ("188 chips") is unverifiable/stale

**File:** `firestarter_app/tools/diff_db.py:115-118`
**Issue:** The docstring cites "188 chips have both timing and vcc/vdd changes."
The live run reports 371 total changed chips grouped by cause but does not break
out a 188 figure, and the number is not asserted anywhere, so it can silently
rot. Magic counts embedded in prose tend to drift from the data.
**Fix:** Drop the hard number or compute and print the per-bucket counts (the
report already prints `len(chips)` per bucket — reference that instead of a
frozen literal).

### IN-03: `interpret_timing` bare-`except Exception` swallows all errors to 0

**File:** `firestarter_app/tools/build_db.py:241-244`
**Issue:** `interpret_timing` catches every `Exception` and falls back to
`val = 0`, so a `None` or malformed `pulse_delay` silently becomes "0 us" rather
than surfacing a data problem. For a chip whose timing genuinely failed to
decode, "0 us" is a plausible-looking but wrong value. (Out of strict Phase 59
scope — predates this phase — but adjacent to the determinism work and worth a
note.)
**Fix:** Narrow to `except (TypeError, ValueError)` and, if the raw value was
non-empty/non-None, emit a WARN to stderr rather than silently coercing to 0.

---

_Reviewed: 2026-06-09_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
