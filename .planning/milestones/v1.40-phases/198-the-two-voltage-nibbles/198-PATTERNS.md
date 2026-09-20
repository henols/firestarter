# Phase 198: The two voltage nibbles - Pattern Map

**Mapped:** 2026-09-18
**Files analyzed:** 13 (9 in `firestarter_app/`, 4 in `.planning/`)
**Analogs found:** 13 / 13 — every file this phase touches has a shipped precedent, most from Phase 197
**Tracked-source gate:** every analog path below was confirmed with `git ls-files` in its own repo
(`firestarter_app` is a submodule; meta paths checked from `/workspaces`). No gitignored mirror is cited.

> **Read this first.** `198-RESEARCH.md` already carries the exact line numbers, measured counts and
> runnable commands. This file does not repeat them. It answers only: *for each file, which existing
> file is the shape to copy, and what does that shape look like?*
>
> **HARD RULE (CLAUDE.md):** no comments in product source. Several excerpts below contain `#`
> comments. They are quoted so an editor knows what text exists and must not be orphaned or
> resurrected as `+` lines. **They are not a pattern to replicate. Add no comment line, ever.**

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/tools/build_db.py` (decode tables + mask) | config/decode-table (build-time generator) | transform | itself — `VCC_VOLTAGES` @ :116-124 is the analog for `VPP_MV` @ :57-79, and vice versa | exact (self-analog) |
| `firestarter_app/tools/datasheet_overrides.json` (+13 keys / +17 fields) | data/config | batch | its own 9 shipped entries — `FUJITSU/MBM27C1001` (cited) and `SGS-THOMSON/M2732A` (`UNSOURCED`) | exact |
| `firestarter_app/tools/DECODE-NOTES.md` § 9 | documentation | — | `DECODE-NOTES.md` § 8 (:302-367), with § 6 "Honest gaps" (:257) for the limits voice | exact |
| `firestarter_app/firestarter/data/chip_database.json` | generated artifact | batch | — regenerated only; **never hand-edited** | n/a |
| `firestarter_app/tests/golden/wire_dict_expected_deltas_198.json` | test fixture (golden delta layer) | batch | `tests/golden/wire_dict_expected_deltas_197.json` | exact |
| `firestarter_app/tests/test_wire_dict_equivalence.py` | test | batch | its own `deltas_197` blocks + `test_the_197_delta_layer_is_capable_of_failing` (:576-612) | exact (self-analog) |
| `firestarter_app/tests/test_datasheet_overrides.py` | test | batch | its own `_EXPECTED_*_COUNT` literals (:335-336); planted-mutation shape from `tests/test_build_db_constant_census.py::TestDetectorCapability` | exact |
| `firestarter_app/tests/__snapshots__/test_characterization.ambr` | test fixture (snapshot) | — | itself, via the 197-04 targeted re-record precedent | exact |
| `firestarter_app/tests/test_build_db_constant_census.py` | test (gate) | transform | itself — check-only, expected unchanged | n/a |
| `.planning/.../198-REGEN-DIFF.md` | record | — | `197-REGEN-DIFF.md` | exact |
| `.planning/.../198-VOLT03-DISPOSITION.md` | record | — | `197-at28c-guard-evidence-for-phase-199.md` + `177-READBACK-INVENTORY.md` | exact |
| `.planning/.../198-GH66-ANSWER.md` | record | — | `197-GH70-ANSWER.md` | exact |
| ROADMAP backlog entry (999.7N) | record | — | ROADMAP `### Phase 999.71` (:8002-8026) | exact |
| todo `git mv` pending → completed | record | — | commit `59481654` (`R100` pure rename) | exact |

---

## Pattern Assignments

### `firestarter_app/tools/build_db.py` (decode tables, transform)

**Analog: the file's own two decode tables.** They are the only two instances of this shape in the
repo, and each is the other's model. `VCC_VOLTAGES` carries the house-style provenance marker;
`VPP_MV` does not — D-01/D-02 must make them match.

**Provenance-marker shape to follow** (`build_db.py:116`, the `[VERIFIED: …]` form — one line,
immediately above the table, naming upstream file, line range, sha, and the named C array):

```python
# [VERIFIED: minipro database.c#L130-L135 @ a8efaedc — tl866ii_vcc_voltages[]]
VCC_VOLTAGES = {
    0x00: 5000,
    0x01: 3300,
    0x02: 4000,  # BUG-1 fix: was missing from v1.12
    0x03: 4500,  # BUG-1 fix: was missing from v1.12
    0x04: 5500,
    0x05: 6500,
}
```

Three things the planner must specify on this excerpt:
1. **The marker string is falsified** and appears **twice** — at `:116` and again at `:126` on
   `_VCC_MARGIN_RAIL_MV`. `L130-L135` is `tl866a_vpp_voltages[]`. Both become
   `# [VERIFIED: minipro database.c#L182-L190 @ a8efaedc — xg_vcc_voltages[]]`. This is *correcting*
   an existing comment, not adding one, and it **must not grow a line**.
2. **One key per line is the file's style.** Add the 9 new keys in place, same style. Do not
   re-flow into the compact form — that is Pitfall 4 and it resurrects `:120-121` and `:127-130` as
   `+` lines under the C-2 pre-commit check.
3. **`# BUG-1 fix` at `:120-121` is the only copy of that provenance in the tree.** If any edit
   dislodges it, relocate the fact into `DECODE-NOTES.md` § 9 in the same commit
   (the `.planning/notes/197-build-db-comment-provenance-rescued.md` precedent).

**`VPP_MV`'s marker** (`:61`) is the non-conforming one — `# [minipro database.c + tl866a.c, tl866ii_vpp_voltages[]]`:
no `VERIFIED:` token, no sha, and it names `tl866a.c` whose VPP table conflicts on 8/8 indices.
Bring it to the `VCC_VOLTAGES` marker shape, naming `xg_vpp_voltages[]` at `database.c#L161-L170`.

**The mask expression** (`:674`, with its two neighbours — the `.get(idx, default)` triple is the
established decode idiom and D-03 keeps it):

```python
                _d_vpp_mv = VPP_MV.get(voltages & 0xF0, 0)
                _d_vcc_mv = VCC_VOLTAGES.get((voltages >> 8) & 0x0F, 5000)
                _d_vdd_mv = VCC_VOLTAGES.get((voltages >> 12) & 0x0F, 5000)
```

The replacement must be exact-match-before-mask (RESEARCH Pitfall 1 — a literal `& 0xFF` re-key
breaks 142 rows). The derived-constant idiom to copy for `_VPP_EXACT_LOW_BYTES` is
**`_VCC_MARGIN_RAIL_MV` at `:131`** — `_VCC_MARGIN_RAIL_MV = VCC_VOLTAGES[0x02]`, i.e. *derived from
the table so it cannot drift from it*, never a bare literal. Keep the new constant integer-valued and
part-name-free or the OVR-06 census golden (frozen at exactly one entry, `"DIP28"`) trips.

**Shape reference for D-06's `vdd < vcc` predicate, if it ships** (`:778-790`) — a value-keyed,
part-name-free rewrite guarded on a decoded value compared against a table-derived constant:

```python
                if chip_entry["electrical"]["vcc_mv"] == _VCC_MARGIN_RAIL_MV:
```

Cite this block; do not edit it. Its comment at `:783-786` ("…each drags in sixteen genuinely-5V
EEPROMs and sets them to 3.3V…") is also F-4's key evidence for the VOLT-03 disposition.

---

### `firestarter_app/tools/datasheet_overrides.json` (data, batch)

**Analog: the file's own entries.** Two shapes, both already shipped. Sorted-key order is enforced by
the loader (`build_db.py:372-380`), so insertion position is determined, not chosen.

**Datasheet-cited entry** — the shape for the 2 VPP + 3 vdd corrections:

```json
  "FUJITSU/MBM27C1001": {
    "datasheet": "datasheets/MBM27C1001.pdf",
    "note": "Page 9-90's AC CHARACTERISTICS table: tPW 0.475/0.50/0.525 ms, N 1 to 25, tOPW 1.4/1.5/39.4 ms, measured at VCC1 6V +/- 0.25V and VPP2 12.5V +/- 0.3V.",
    "fields": {
      "programming.pulse_duration_us": { "was": 100, "is": 500 }
    }
  },
```

Note: this key **already exists** and gains a field rather than being created. Same for
`FUJITSU/MBM27128`. Only `FUJITSU/MBM27C4001` is a new Fujitsu key — and per 197 D-19 it must carry
**only** `electrical.vpp_mv` and `electrical.vdd_mv`; a `programming.pulse_duration_us` field there
is a no-op override and raises.

**`UNSOURCED` entry** — the shape for all 12 held `0x06` rows. Copy the sentence form exactly,
including the terminal **`Closed by: <what would close it>.`** which D-05 requires per entry:

```json
  "SGS-THOMSON/M2732A": {
    "datasheet": "UNSOURCED",
    "note": "Value 21000 is inherited verbatim from the deleted NMOS_TRUE_VPP_MV hardcode, which sourced this figure from an Intel datasheet for the Intel NMOS 2732A and applied it to this SGS-THOMSON row with no SGS-THOMSON-specific datasheet backing it. No SGS-THOMSON datasheet for this part is vendored in this repository. Closed by: SGS-THOMSON's own datasheet for M2732A, vendored and git-tracked under datasheets/.",
    "fields": {
      "electrical.vpp_mv": { "was": 18000, "is": 21000 }
    }
  },
```

The note structure to mirror in all 12: *what the value is and where it came from* → *why it is not
credible / not backed* → *what is absent from this repository* → *`Closed by:`*.

---

### `firestarter_app/tools/DECODE-NOTES.md` § 9 (documentation)

**Analog: § 8, `:302-367`.** Appends after `:367`. § 7 "Sources" sits *before* § 8, so § 8 carries
its own trailing `Sources:` paragraph — § 9 must do the same rather than extending § 7.

**Heading form** — number, backticked subject, requirement ID, phase number, and a verdict clause
inside the heading itself:

```markdown
## 8. `pulse_delay` unit finding (PULSE-01, Phase 197 — the decode rule survives)
```

**Body shape** — each element is a **bolded lead clause** stating the claim, then prose, with an
inline `[VERIFIED: file:lines]` tag where a source is cited:

```markdown
**Verdict: the "microseconds for all protocols" decode rule is CONFIRMED**, and the
finding is that `infoic.xml` carries a bulk family default rather than a per-part
value.

**What `interpret_timing` does today** `[VERIFIED: build_db.py:339-380]`: raw
`pulse_delay` is parsed as hex and returned verbatim as microseconds, ...

**The positive confirmation.** `FUJITSU/MBM27C4001` carries raw `pulse_delay=0x0064`
(100). Its own datasheet (`datasheets/MBM27C4001.pdf`, page 8, AC CHARACTERISTICS)
states ... — a positive match, not merely an absence of contradiction.

**The falsification of "per-part value".** ... **675 entries** — raw `pulse_delay=0x0064`
(100) accounts for **462** of them (68.4%). ...

**No uniform multiplier is coherent.** The raw ladder spans `0x0001` (1) to `0x2710`
(10000) — four orders of magnitude. ...
```

Slot ordering to copy: **Verdict → what the code does today (with file:line) → positive confirmation
(one named part, its datasheet, page, exact figures) → falsification of the rejected hypothesis, with
counts → arithmetic argument → edge case / dead branch → `Sources:` line.**
RESEARCH F-13 already maps each slot onto D-15's content.

**Limits voice — § 6 "Honest gaps" (`:257`).** Each limit is a bolded *assertive* clause naming the
thing and its status, followed by why, then an explicit cross-reference naming what owns it:

```markdown
- **No high-byte value is a classification gap.**  … There is therefore **no undecoded high-byte value left guessed**.
- **2516 / 2532 are NOT a decode gap.** … **Cross-reference: Plan 86-04 owns 2516/2532.**
```

Not hedges. D-15's three mandatory limits (plus F-2's fourth) go in this voice.

---

### `firestarter_app/tests/golden/wire_dict_expected_deltas_198.json` (test fixture, batch)

**Analog: `tests/golden/wire_dict_expected_deltas_197.json`** — two top-level keys, `deltas` and a
five-key `meta`. The `meta` keys are the composition test's "anti-laundering assertions" and are
mandatory: `decision`, `honesty`, `how_to_update`, `phase`, `provenance`.

```json
{
  "deltas": {
    "FUJITSU|MBM27128|2": { "pulse-delay": 1000 },
    "FUJITSU|MBM27C1000P,MBM27C1000|6": { "pulse-delay": 500 },
    "FUJITSU|MBM27C1001|7": { "pulse-delay": 500 }
  },
  "meta": {
    "decision": "Phase 197: tests/golden/wire_dict_baseline.json is preserved byte-unchanged. This file is the committed, reviewable expected-delta list ... -- the golden itself is never re-captured or re-baselined to make this phase's change disappear.",
    "honesty": "This layer records that these three records' pulse-delay wire value moved ... It does not by itself prove any of the three values is correct ...",
    "how_to_update": "This layer is regenerated by the same script against the live database and never edited by hand. ...",
    "phase": "197-the-override-mechanism-and-the-program-pulse",
    "provenance": "All three records are attributable to tools/datasheet_overrides.json entries: ... Generated programmatically from the live capture ... never transcribed by hand, since the |<i> record-key suffix is a positional index within each manufacturer's list and would silently rot if any row is ever added or reordered."
  }
}
```

Content notes for the 198 layer: `phase` = `198-the-two-voltage-nibbles`; `provenance` must attribute
both records to their `datasheet_overrides.json` entries **and** state that the 15 `vdd_mv` movements
contribute zero wire deltas (the 197 `provenance` does exactly this for its 10 non-wire changes —
copy that sentence pattern); `honesty` must state the values rest on a visually-read datasheet, not
an electrical measurement, exactly as 197's does.

---

### `firestarter_app/tests/test_wire_dict_equivalence.py` (test, batch)

**Analog: the file's own `_197` blocks.** Every 198 edit is a copy of a 197 edit one layer up.

**Constant** (`:133` region) — one line per layer, same naming:

```python
_DELTAS_197 = _HERE / "golden" / "wire_dict_expected_deltas_197.json"
```

**Per-layer load + guard + exact-count block** (`:333-350`) — three assertions, in this order:
keys-exist-in-golden, delta-would-not-be-vacuous, exact count:

```python
    missing_from_golden_197 = sorted(k for k in deltas_197 if k not in recorded)
    already_present_197 = sorted(
        k
        for k in deltas_197
        if k in recorded
        and recorded[k].get("pulse-delay") == deltas_197[k].get("pulse-delay")
    )
    assert not missing_from_golden_197, (
        f"197 delta keys not found in the golden: {missing_from_golden_197}"
    )
    assert not already_present_197, (
        "197 delta keys whose golden record already carries the delta's "
        f"pulse-delay value (the delta would prove nothing): {already_present_197}"
    )

    assert len(deltas_197) == 3, (
        f"expected exactly 3 Phase 197 deltas, found {len(deltas_197)}: "
        f"{sorted(deltas_197)}"
    )
```

The 198 copy swaps `pulse-delay` → `vpp_mv` and `3` → `2`.

**`layer_pairs`** (`:352-362`) — each new layer pairs against **every** prior layer:

```python
    layer_pairs = (
        ("149", deltas_149, "153", deltas_153),
        ...
        ("197", deltas_197, "149", deltas_149),
        ("197", deltas_197, "153", deltas_153),
        ("197", deltas_197, "182", deltas_182),
        ("197", deltas_197, "194", deltas_194),
    )
```

198 adds five tuples (`198×149`, `198×153`, `198×182`, `198×194`, `198×197`) — note the research
names four; the `198×197` pair is the load-bearing one, because `FUJITSU|MBM27C1001|7` is shared and
field-disjointness (`pulse-delay` ∩ `vpp_mv` = ∅) is only checked if the pair is listed. The
assertion message enumerating layer names must also gain "198".

**Composition loop** — one `for` per layer, appended in order:

```python
    for key, delta_wire in deltas_197.items():
        expected[key].update(delta_wire)
```

**Non-vacuity test** (`:576-612`) — this is the template for `test_the_198_delta_layer_is_capable_of_failing`:

```python
def test_the_197_delta_layer_is_capable_of_failing() -> None:
    doc = json.loads(_GOLDEN.read_text(encoding="utf-8"))
    recorded = doc["records"]
    deltas_149 = json.loads(_DELTAS_149.read_text(encoding="utf-8"))["deltas"]
    ...
    composed = copy.deepcopy(recorded)
    for key, delta_wire in deltas_149.items():
        composed[key].update(delta_wire)
    ...
    mutated = copy.deepcopy(composed)
    some_key = next(iter(sorted(deltas_197)))
    mutated[some_key]["pulse-delay"] = mutated[some_key].get("pulse-delay", 0) + 100000

    diff = _describe_record_diff(composed, mutated)

    assert diff != "(no difference detected)", (
        "non-vacuity failure: mutating one of the 3 records' pulse-delay "
        "did not produce a reported diff -- the 197 delta layer's gate is "
        "incapable of failing"
    )
    assert diff == f"changed={{'{some_key}': ['pulse-delay']}}", (
        f"the failure-capability leg must report EXACTLY the one mutated "
        f"record {some_key!r} and no other -- got: {diff}"
    )
```

198's copy mutates `vpp_mv` and asserts `changed={{'{some_key}': ['vpp_mv']}}`.

**The count test** — `test_exactly_84_records_change_flags_and_no_other_field_moves`, assertion at
`:500`. The count is in the **test name**, so bumping `84` → `86` requires a rename. Its
`changed_fields == {"flags"}` assertion is the companion leg; check whether the two new records'
changed field set keeps it satisfied, or whether the test's own composition list (which currently
omits `deltas_153`) needs the 198 layer added.

---

### `firestarter_app/tests/test_datasheet_overrides.py` (test, batch)

**Analog: the file's own `TestShippedOverrideFileContract` literals** (`:334-336`):

```python
_UNSOURCED = "UNSOURCED"
_EXPECTED_UNSOURCED_COUNT = 6
_EXPECTED_ENTRY_COUNT = 9
```

`6 → 18`, `9 → 22`. **These are key counts, not field counts** (RESEARCH Pitfall 3). They read
`tools/datasheet_overrides.json` directly, so they stay green until the override file itself is
edited — plan both in the same task.

**Analog for the 12-entry non-vacuity coverage (Claude's discretion):** two shipped shapes exist.

1. **Synthetic-fixture raise test**, in this same file — `test_mbm27c4001_noop_entry_raises` builds a
   dict literal, calls `build_db.apply_datasheet_override(...)` and asserts on `str(exc.value)`
   substrings. This is the shape if the coverage is "a wrong `was` raises".
2. **Planted-mutation capability class** — `tests/test_build_db_constant_census.py::TestDetectorCapability`,
   the cleaner analog for "prove the gate can fail":

```python
class TestDetectorCapability:
    def test_planted_literal_is_reported(self):
        source = 'PLANTED_NAMES = {"AT28C16"}\n'
        result = find_part_specific_constants(source, set())
        assert result == ["AT28C16"], result
```

Note its three-class file layout — `TestDetectorCapability` / `TestRealSourceCensus` /
`TestGoldenContract` — i.e. *capability* proven on synthetic input, kept separate from the *real*
assertion. A 198 test asserting "exactly 12 entries carry `{"electrical.vdd_mv": {"was": 1800, "is": 5000}}`"
belongs in the `TestShippedOverrideFileContract` class alongside the count literals.

---

### `firestarter_app/tests/__snapshots__/test_characterization.ambr` (test fixture)

**Analog: itself, under the 197-04 targeted-re-record precedent.** The pattern is not "edit the
file" — it is: run `--snapshot-update` scoped to the single failing test node id, then prove
narrowness with `git diff --numstat` returning exactly `2	2`. A blanket update across all 32
snapshots hides unrelated drift. `--numstat` equality is the acceptance criterion, not "the snapshot
was updated".

---

### `.planning/phases/198-.../198-REGEN-DIFF.md` (record)

**Analog: `.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-REGEN-DIFF.md`** (tracked).

Headings, in order:

```
# Phase 197 — The 746-Row Regeneration Diff
   (then a dated **Measured:** line naming the submodule sha and branch, and a
    one-paragraph statement of which requirement this artifact is evidence for)
## Reproducible method
## Row-count line
## The 14 changed fields, one line per field
## The two zero-diff claims
## Honesty limit
```

Slot content to mirror:
- **Reproducible method** — names the baseline as `git show <sha>:firestarter/data/chip_database.json`
  and explicitly rules out `tools/baseline/chip_database.baseline.json` (stale) and `tools/diff_db.py`
  (does not exist); then the full throwaway script text inline.
- **Row-count line** — four bullets exactly: `Rows in`, `Rows out`, `Rows changed`,
  `support_status values changed`, followed by a reconciliation sentence against the phase's
  pre-regeneration prediction. For 198: 746 / 746 / 15 / 0.
- **Changed-fields table** — columns `Manufacturer | Part number | Field path | Before | After | Cause`,
  **one line per field, not per row** (so 17 lines for 15 rows), each `Cause` reading either
  `Decode rule: …` or `Override: entry <KEY> in tools/datasheet_overrides.json, datasheet: <path>`.
  Closes with the sentence "Every one of the N changed fields fits one of the two kinds …
  No row fits neither kind."
- **Zero-diff claims** — the section exists *because a table of changes cannot show what did not
  move*. 198's two: the 12 held `0x06` entries contributing zero diff, and the `0xF1`/`0xF2`
  `VPP_MV` additions being byte-identical. Each cites the commit that proved it.
- **Honesty limit** — states the diff proves *which values moved and why each was expected to*, and
  explicitly **does not** prove any new value is electrically correct; names which values rest on a
  visually-read datasheet.

---

### `.planning/phases/198-.../198-VOLT03-DISPOSITION.md` (record)

**Analog: `.planning/notes/197-at28c-guard-evidence-for-phase-199.md`** (tracked), with
`.planning/milestones/v1.36-phases/177-evidence-gated-read-back/177-READBACK-INVENTORY.md` as the
older instance of the same shape.

`197-at28c-guard-evidence-for-phase-199.md`:
```
# AT28C DIP24 hardware-damage guard — evidence for Phase 199
## Search method (reproducible)
## The 19-row table
## Per-fact disposition
## Operator ruling (verbatim)
## Honesty limit
## What Phase 199 must decide
```

`177-READBACK-INVENTORY.md`:
```
# PRUNE-04 Read-Back Call-Site Inventory
## Search method
## The eight-row inventory
## The two engine call sites, pinned
## Replacement primitive, named
## PRUNE-04's closure
```

`197-PULSE-INVENTORY.md` (same phase directory, the closest sibling by subject):
```
# PULSE-01/D-12 — The 100 µs Program-Pulse Inventory
## Reproducible method
## Census figures
## The twelve Fujitsu algorithm 7/8 rows, each disposed
## The 100 µs rows outside the Fujitsu block: 208 rows, per-manufacturer
## Honesty limit
```

**The invariant across all three:** reproducible method first (a runnable command or script, not a
description) → the full N-row table with **no elision** → per-row/per-fact disposition each carrying a
reason → a named **Honesty limit** → optionally a "what the next consumer must decide" section. 198's
honesty limit is pre-written by the research: no Microchip or AMD datasheet is vendored, so all 16
sub-group-1 dispositions are a part-class inference plus an in-repo measurement, never a datasheet
reading.

---

### `.planning/phases/198-.../198-GH66-ANSWER.md` (record)

**Analog: `.planning/phases/197-.../197-GH70-ANSWER.md`** (tracked). Five sections:

```
# gh#70 Answer — Draft
   (immediately followed by a bolded internal-only warning paragraph:
    "**This is an internal draft-tracking file. Only the "Comment Body" section below is the text
      intended for posting … must never be pasted onto the issue.**")
## Status
## Internal provenance (project bookkeeping only — do not post)
## Comment Body
## Held-pending deferral (internal — do not post)
```

**§ Status** opens with a single all-caps verdict line, then the numbered operator decisions:

```markdown
**DRAFT — APPROVED, HELD PENDING THE BETA CUT. NOT POSTED.**

Operator decision recorded 2026-09-18:

1. **Publication route: `hold`.** … Reason given: nothing in this milestone is pushed …
2. **One text amendment approved, and only one.** …

**Nothing has been posted.** See "Held-pending deferral" near the end of this file …
```

**§ Held-pending deferral** — five bolded bullets in this order, the fourth being a numbered 4-step
list:

```markdown
- **What is held:** the entire "## Comment Body" section above …
- **Why:** … `git branch -r --contains` on this branch's tip returns nothing in either repository …
- **What releases the hold:** the v1.40 beta cut …
- **Exactly what to do at that point:**
  1. Replace the `**Version:**` line in the "## Comment Body" section above with the real published version …
  2. Re-run the no-over-claim and no-attribution checks against the final "## Comment Body" text only …
  3. Post ONLY the "## Comment Body" section — verbatim, starting after the opening `---` and ending
     before the closing `---` — to gh#70 with
     `gh issue comment 70 --repo henols/firestarter --body-file`. Never paste this file's header,
     "Status", "Internal provenance", or this "Held-pending deferral" section onto the issue.
  4. Record the returned comment URL back into this file (in this section) and mark PULSE-04
     complete in `.planning/REQUIREMENTS.md`.
- **Requirement status:** PULSE-04 is NOT satisfied by this plan. It is explicitly carried forward
  to the milestone close …
```

**D-18's consolidation** edits *this* section in `197-GH70-ANSWER.md` so it names both gh#70 and
gh#66. That file is in the **live** phase directory, not under `.planning/milestones/`, so D-14's
"archived records are historical-by-intent" prohibition does not reach it — state both halves in the
task (RESEARCH Pitfall 8).

---

### ROADMAP backlog entry (record)

**Analog: `.planning/ROADMAP.md` `### Phase 999.71`** (:8002-8026) — same subject class (`UNSOURCED`
override entries) and the closest shape available:

```markdown
### Phase 999.71: Six `UNSOURCED` override entries carry an Intel VPP reading applied to non-Intel parts (BACKLOG — filed 2026-09-18 during v1.40 Phase 197, from `197-03-SUMMARY.md`)

**Goal:** Close each `UNSOURCED` entry … or revert the entry if no such datasheet substantiates it.

**The six entries**, all on `electrical.vpp_mv`, all inherited verbatim from … : `INTEL/M2716` (18000 → 25000), …

**What would close each:** the two `INTEL` rows need Intel's own 2716 and 2732 datasheets, vendored and git-tracked …

**Consequence of leaving them:** … it is now visible — each entry's `note` field says so in plain language — but it is not yet fixed.
```

Heading suffix form is fixed: `(BACKLOG — filed <date> during v1.40 Phase 198, from \`<artifact>\`)`.
Four bolded lead-ins: **Goal** / **The N entries** (or **MEASURED**) / **What would close each** /
**Consequence of leaving them**. 999.72 shows the optional extra bolded paragraphs (**DORMANT, not
live.**, **Why it is worth fixing before more entries land:**) when a caveat is needed.

**Writer discipline:** the executor drafts and verifies but **must not write ROADMAP.md** — the 197
executor reverted its own edit (`d883d9f6`) and the orchestrator applied it after confirming the file
was byte-identical to its pre-dispatch snapshot. Verify legs used: N entries present, `### Phase `
heading count up by exactly N with zero lost, all required tokens found.

---

### Todo close (`git mv`)

**Analog: commit `59481654`** —
`R100  .planning/todos/pending/derive-away-max-27c020-size-hardcode.md → .planning/todos/completed/…`.
A pure rename, 100% similarity, no frontmatter edit, no GSD verb. The 198 target already carries
`resolves_phase: 198`, so nothing needs changing. Hazard from the 197 record: a `git mv` run against
an **uncommitted** edit stages the pre-edit blob and silently produces a 0-diff rename — commit any
content edit first, and check `git diff --stat` rather than the commit summary.

---

## Shared Patterns

### No comments in product source
**Source of rule:** `/workspaces/CLAUDE.md` § "Source code comments — hard rule"
**Apply to:** every edit under `firestarter_app/` (and `firestarter_fw/`, untouched here)
Add no `#` line, for any reason. Correcting an existing comment's *content* is permitted and required
(the falsified `[VERIFIED: …]` markers) but must not grow a line. Deleting a clause reflows the rest —
read the remainder and confirm every pronoun keeps an antecedent. **Planner: do not write "add a
comment" into a plan and do not make "a comment exists" an acceptance criterion.**
Pre-commit gate, pathspec load-bearing:
```bash
git -C firestarter_app diff --cached -- '*.py' | /usr/bin/grep -E '^\+\s*#' | /usr/bin/grep -v '^\+\s*#!'
```
must print nothing.

### Provenance markers on decode tables
**Source:** `tools/build_db.py:116`
**Apply to:** both decode tables
`# [VERIFIED: minipro <file>#L<a>-L<b> @ <sha> — <named_c_array>[]]` — file, line range, pinned sha,
and the specific array. Not a bare file name, not an unversioned marker.

### Derived constants, never literals
**Source:** `tools/build_db.py:131` — `_VCC_MARGIN_RAIL_MV = VCC_VOLTAGES[0x02]`
**Apply to:** any new named constant in the generator
Derive from the table so it cannot drift. Keep values integer and part-name-free, or the OVR-06
census golden (frozen at exactly one entry) trips.

### Append-only golden delta layers
**Source:** `tests/golden/wire_dict_expected_deltas_197.json` `meta.decision` / `meta.how_to_update`
**Apply to:** any change that moves a wire value
`wire_dict_baseline.json` is **never** re-captured. A new numbered layer is the only route, generated
**programmatically from the live capture**, never hand-transcribed — the `|<i>` key suffix is a
positional index that rots on any row add or reorder.

### Non-vacuity proof per gate
**Source:** `test_the_197_delta_layer_is_capable_of_failing`;
`tests/test_build_db_constant_census.py::TestDetectorCapability`
**Apply to:** every new fixture or gate this phase adds
A gate that has never been seen to fail proves nothing. Plant a mutation, assert the diff names
**exactly** the one mutated record and no other.

### Measured-not-asserted counts
**Source:** `197-REGEN-DIFF.md` § Row-count line; `197-PULSE-INVENTORY.md` § Census figures
**Apply to:** every count in every artifact and verify leg
Derive counts from the file or the run, not from arithmetic. Suite runs use
`.venv/ci-replica/bin/python` (3.11.16) with `-o addopts=""`; the devcontainer default 3.12 has
masked CI before.

### Every evidence record ends with a named honesty limit
**Source:** `197-REGEN-DIFF.md`, `197-PULSE-INVENTORY.md`, `197-at28c-guard-evidence-for-phase-199.md`,
`177-READBACK-INVENTORY.md` — all four carry a `## Honesty limit` section
**Apply to:** `198-REGEN-DIFF.md`, `198-VOLT03-DISPOSITION.md`, and § 9's limits
State what the artifact does **not** prove, in assertive form, not as a hedge.

## No Analog Found

None. Every file this phase touches has a shipped precedent, in Phase 197 for twelve of the thirteen
and in Phase 148/177 for the disposition-record shape. There is nothing to design.

The nearest thing to a gap is **D-06's `vdd < vcc` build-time assertion**, if it ships: no existing
build-time *reporting* (non-raising) assertion exists in `build_db.py`. The nearest analog is the
generator's own `WARN:` / `INFO:` stderr lines, and the shape constraint is `_VCC_MARGIN_RAIL_MV`'s —
value-keyed, part-name-free. RESEARCH recommends document-only this phase.

## Metadata

**Analog search scope:** `firestarter_app/tools/`, `firestarter_app/tests/`,
`firestarter_app/tests/golden/`, `.planning/phases/197-*/`, `.planning/notes/`,
`.planning/milestones/v1.36-phases/177-*/`, `.planning/ROADMAP.md`
**Files read for excerpts:** 11
**Tracked-source verification:** `git ls-files` run in both `firestarter_app` and the meta repo; all
14 cited analog paths returned non-empty
**Pattern extraction date:** 2026-09-18
