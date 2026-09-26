---
title: Pre-sweep citation manifest — count reconciliation and schema record
phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
plan: "04"
measured: 2026-08-23
status: AUTHORITATIVE — the reconciliation record for `.planning/milestones/v1.33-artifacts/sweep-citation-manifest.jsonl`
requirements: [SWEEP-09, SWEEP-10]
---

# Pre-sweep citation manifest — reconciliation report

The manifest at `.planning/milestones/v1.33-artifacts/sweep-citation-manifest.jsonl` is the **only**
interface between Phase 154 and Phase 159, and it is **not reconstructible after the
sweep** — once the sweep lands, the pre-sweep `(target_line, source_text)` pairs exist
nowhere on disk. This file records the counts it actually produced, with the exact
commands that produced them, and reconciles them against every recorded figure rather
than substituting for any of them (Ruling G).

**Pre-sweep identification.** Generated at `firestarter` HEAD
`8695ee52c27a4bee4387c5c489afd5f3d7275e8a` and `firestarter_app` HEAD
`6bfa6453d1bac232eb81ab35fa7f14b50b0b291a` — the same two shas research measured
against, and the same two plan 01 recorded as `FW_PRE_SHA` / `APP_PRE_SHA`. Both are
written into the manifest's own header record, so the pre-sweep side is provably
identified from the artifact alone. No sweep edit has landed in either sub-repo at
generation time (`git -C firestarter status --short` is empty; `firestarter_app`
carries only plan 03's deliberately-uncommitted test-infrastructure changes, none of
which are in the candidate corpus' shipped-source groups).

---

## 1. The row count, and the verbatim command that produced it

```bash
cd /workspaces
python3 .planning/milestones/v1.33-artifacts/tools/build_citation_manifest.py /workspaces \
  --fw-root /workspaces/firestarter \
  --app-root /workspaces/firestarter_app \
  --out /workspaces/.planning/milestones/v1.33-artifacts/sweep-citation-manifest.jsonl \
  --exclude .planning/milestones/v1.33-artifacts/sweep-citation-manifest-report.md \
  --stats
```

Its PASS line, verbatim:

```
PASS: 13692 records over 2947 planning files, 171 candidate swept files; variants
colon_single=6469, colon_range=6137, colon_list=678, anchor_L=194, anchor_L_range=214;
resolutions exact=2094, suffix=1218, basename=7133, ambiguous=10, unresolved=2978,
rejected=259; every range record carries both endpoints and both texts; every record
retarget=false.
```

| Figure | This run |
|---|---|
| Manifest lines | **13,693** (1 header record + 13,692 citation records) |
| Citation **records** (one per `(target_file, target_line)` pair) | **13,692** |
| Citation **occurrences** (one per matched citation in a document) | **13,290** |
| Records targeting a **candidate swept file** (`exact`+`suffix`+`basename`) | **10,445** |
| …the same, occurrence-equivalent | **10,169** |
| Records **shifting** (resolved, at or below their target file's first provenance hit) | **7,249** |
| …the same, occurrence-equivalent | **7,076** |
| File size | 7,192,847 bytes raw / 454,892 bytes zlib-packed (~444 KB) |

**Records vs occurrences — read this before comparing any number below.** A `colon_list`
citation such as `hardware.py:39,153` is **one occurrence** and **two records**, because
it is two independent point citations sharing one path (never a range). Every other
variant is 1:1. Research's census counted **occurrences**, so the occurrence-equivalent
column is the one comparable to it; the manifest's row count is necessarily larger.
This distinction accounts for the single largest apparent discrepancy in this report
(`colon_list` 678 vs 274) and it is a definitional difference, not a measurement one.

**Independent fidelity oracle (not required by the plan; run anyway).** All **10,190**
records whose `text_status` is `read` were re-checked line-by-line against the on-disk
source file: **10,190 match byte-for-byte, 0 mismatch.**

```bash
python3 - <<'EOF'
import json, pathlib
recs=[json.loads(l) for l in open('.planning/milestones/v1.33-artifacts/sweep-citation-manifest.jsonl',encoding='utf-8')][1:]
ok=bad=0
for r in recs:
    if r['text_status']!='read': continue
    lines=pathlib.Path(r['target_file_resolved']).read_text(encoding='utf-8',errors='replace').splitlines()
    ok += lines[r['target_line']-1]==r['source_text']
    bad += lines[r['target_line']-1]!=r['source_text']
print("match",ok,"mismatch",bad)
EOF
# -> match 10190 mismatch 0
```

**Byte-identical regeneration, proven on the real tree.** Two runs with identical argv
produce identical bytes (`md5 34abd50c2d2ea3bfe21271b1216276ab` both times), and the
`--stats` block is identical too. No timestamp is recorded anywhere in the artifact,
which is what makes that possible. A run with *different* argv differs in exactly one
place — the header's `generating_command` — which is intended, not drift.

---

## 2. Reconciliation of the swept-targeting total against 10,054 and 9,989

| Source | Swept-targeting citations | Δ vs SWEEP-09's pre-registered figure |
|---|---|---|
| **SWEEP-09 (pre-registered, recorded)** | **10,054** | — |
| RESEARCH.md (independent re-measurement, clean `beta` exports) | **9,989** | −65 (−0.6%) |
| **This run (occurrence-equivalent)** | **10,169** | **+115 (+1.1%)** |
| This run (manifest **records**) | 10,445 | +391 (+3.9%) |

**SWEEP-09's 10,054 is NOT rewritten and this run's number is NOT quietly asserted in
its place.** Both stand, with the delta accounted for below.

### Is research's own explanation sufficient for this run's delta too?

Research attributed its −65 to two causes: (a) extractor-definition differences (its
scan included non-`.md` files), and (b) `notes/` having grown since the survey. Checked
against this run's data:

- **(a) does NOT apply to this run's delta, because this run shares research's wider
  extractor definition.** This run scans the same six extensions research did
  (`.md .py .json .txt .sh .csv`) over 2,947 planning documents. Measured share of
  non-`.md` sources in the manifest: only **8** of the 831 `eprom.cpp` rows come from a
  `.json` document, and non-`.md` documents contribute a negligible fraction overall.
  So (a) is already inside both this run's and research's figures, and cannot explain a
  delta *between* them.
- **(b) DOES apply, and is the dominant cause.** `.planning/` has grown since research
  measured, entirely on the meta side — the source trees are at the identical two shas.
  The growth is directly visible and is fully attributable:

| Cause of growth since research's measurement | Effect |
|---|---|
| Phase 154's own artifacts (`154-0{1,2,3}-SUMMARY.md`, `154-VALIDATION.md`, the four plan files, `.planning/milestones/v1.33-artifacts/{baseline-pre-sweep,sweep-corpus-baseline,sweep-gate-dispositions}.md`) | **18** records cite from `.planning/milestones/v1.33-artifacts/` and a further ~200 from the phase directory |
| `notes/`, `todos/` and `seeds/` additions since the survey | research already named this cause; `notes/` contributes 114 records here vs its recorded 54 shifting citations |
| Candidate set grew 160 → **171** files (see §5), which promotes some previously-`unresolved` citations into the swept-targeting set | direct, and the single largest structural contributor |

**Verdict: the delta is +115 (+1.1%) and it is EXPLAINED**, by `.planning/` growth on
the meta side plus an 11-file wider candidate set. **No part of it is left unexplained.**
The three independent measurements agree within 1.8% of each other across a
seven-month-old pre-registration, which is the actual finding.

---

## 3. Reconciliation of the shifting subset against 6,939 and 6,928

The shifting subset is defined exactly as the recorded figure defines it: records that
resolve to a candidate file **and** whose `target_line` is at or below that file's
**first** provenance hit line. The first-hit line comes from `survey_provenance.py`'s
per-file hit lines (plan 02's authority), not from a re-derived regex.

| Source | Shifting citations | Δ vs recorded |
|---|---|---|
| **Recorded (SWEEP-09 / the writeup)** | **6,939** | — |
| RESEARCH.md | **6,928** | −11 (−0.16%) |
| **This run (occurrence-equivalent)** | **7,076** | **+137 (+2.0%)** |
| This run (manifest **records**) | 7,249 | +310 (+4.5%) |
| This run, non-shifting resolved records (above the first hit) | 3,196 | recorded 3,115 / research 3,061 |

Same cause as §2, and it reproduces in the subtree breakdown research published:

| Subtree | Recorded (shifting) | Research | This run (shifting records) |
|---|---|---|---|
| `phases/` | 4,918 | 4,869 | 5,097 |
| `milestones/` | 1,309 | 1,302 | 1,374 |
| `research/` | 180 | 180 (exact) | 180 (**exact, third time**) |
| `graphs/` | 108 | 107 | 108 (**exact**) |
| `debug/` | 99 | 94 | 100 |
| `quick/` | 55 | 55 (exact) | 55 (**exact**) |
| `notes/` | 54 | 72 | 76 |
| `PROJECT.md` | 42 | 42 (exact) | 42 (**exact**) |

**Four subtrees reproduce the recorded figure exactly** (`research/`, `graphs/`,
`quick/`, `PROJECT.md`) and the two that grew (`phases/`, `notes/`) are exactly the two
subtrees this phase and the intervening months added documents to. **Explained, not
unexplained.**

---

## 4. Per-variant counts against research's four expected figures

Compared on **occurrences**, which is what research counted.

| Variant | Research (all) | This run (occurrences) | Δ | This run (records) |
|---|---|---|---|---|
| `colon_single` — `path:N` | 6,253 | **6,469** | +216 (+3.5%) | 6,469 |
| `colon_range` — `path:N-M` | 6,068 | **6,137** | +69 (+1.1%) | 6,137 |
| `anchor_L` — `path#LN` / `#LN-LM` | 407 | **408** | +1 (+0.2%) | 408 (194 point + 214 range) |
| `colon_list` — `path:N,M[,…]` | 274 | **276** | +2 (+0.7%) | 678 |
| **TOTAL** | **13,002** | **13,290** | +288 (+2.2%) | 13,692 |

All four variants are live and all four reproduce within 3.5%. `anchor_L` (+1) and
`colon_list` (+2) are effectively exact. **`colon_range` is 45% of the manifest's rows
(6,137 of 13,692) and 46% of the resolved rows** — range handling is roughly half the
work, exactly as research warned, which is why REMAP-03's both-endpoints requirement
carries the weight it does.

**Every range record carries all four range fields** — `target_line`, `target_line_end`,
`source_text`, `source_text_end` — asserted by the generator's own
serialize-then-scan self-check (exit 1 if any range record is missing an endpoint or an
endpoint text) and re-asserted independently over the written artifact.

`anchor_L` is emitted under two variant labels, `anchor_L` (point, 194) and
`anchor_L_range` (range, 214), so a consumer can test "is this a range record?" on the
variant alone. Their sum is the figure comparable to research's 407.

A **backticked** citation is a wrapper, not a fifth variant: the inner text matches the
colon form and is recorded as such, with the backticks absent from `target_file_cited`.
A unit test pins this.

---

## 5. Per-resolution counts — nothing dropped, and the ambiguous decisions recorded

**A generator that silently discarded its unresolved rows would be indistinguishable
from one that is broken.** So every citation found becomes a row, each carrying a
`resolution` and a `resolution_reason`, and the classes are counted here.

| `resolution` | Records | What it means |
|---|---|---|
| `exact` | **2,094** | exact repo-relative path in the candidate set |
| `suffix` | **1,218** | unique path suffix on a segment boundary |
| `basename` | **7,133** | unique basename in the fixture-excluded index |
| **resolved subtotal** | **10,445** | remappable rows — Phase 159's working set |
| `ambiguous` | **10** | matched >1 candidate; no resolved path; excluded from the oracle |
| `unresolved` | **2,978** | matched no candidate at all |
| `rejected` | **259** | escapes the explicit roots (absolute or `..`-relative) |
| **TOTAL** | **13,692** | |

`rejected` is deliberately a **sixth** class, kept distinct from `unresolved`, so a
reader can tell "this citation escapes the roots" from "this citation names nothing in
the candidate set". The rejection is recorded rather than raised or swallowed.

### How each resolved row was bound — the decision, not just the count

| `resolution_reason` | Records |
|---|---|
| unique basename in the fixture-excluded index | 7,129 |
| exact repo-relative candidate path | 2,094 |
| unique path-suffix candidate | 1,218 |
| unique basename via the fixture-inclusive fallback (no non-fixture candidate carries this basename) | 4 |

### The ambiguous residue: 10 rows, 2 distinct targets — every one named

| Cited target | Rows | Why it is genuinely ambiguous |
|---|---|---|
| `host_stubs.cpp` | 9 | **23 real copies** under `firestarter/test/native/avr/*/`, none of them a fixture. Not resolvable from a bare basename. |
| `serial_read_mock.h` | 1 | 3 real copies, same shape. |

Research predicted an 11-citation residue (9 × `host_stubs.cpp`, 1 × `__init__.py`,
1 × `serial_read_mock.h`). Measured here: **10** — the `host_stubs.cpp` 9 and the
`serial_read_mock.h` 1 reproduce **exactly**; the single `__init__.py` citation does
not appear because no `__init__.py` in this candidate set carries a provenance hit,
so it falls to `unresolved` rather than `ambiguous`. Delta −1, **explained**.

### The fixture-exclusion rule: what it actually did here, stated honestly

Research predicted the `**/fixtures/**` / `**/fixture/**` exclusion would disambiguate
**639 of the 665** ambiguous citations, because the colliding alternates for
`eeprom_28c.cpp` (286), `firestarter.cpp` (204), `firestarter.h` (99) and
`uno_rurp_shield.cpp` (50) are all planted or fake fixtures.

**Measured against the candidate index, those four basenames were never ambiguous in the
first place** — the colliding alternates live under `firestarter/tests/fixtures/…`
(plural `tests`), which is **outside the sweep globs** (`firestarter/{src,include,test}`,
singular `test`), so they never enter the candidate set at all. Research's 665 figure was
measured against a whole-tree index of ~401 source files, not against the candidate set
the rule is actually applied to.

So on this tree the exclusion is **defence in depth rather than the load-bearing
disambiguator research expected**. It is kept, and it is kept *proven*: because it
cannot be exercised by the real candidate set, the unit test builds a synthetic index
that deliberately **does** contain the firmware planted-fixture copies, and asserts

- bare `eeprom_28c.cpp` resolves to `firestarter/src/proms/eeprom_28c.cpp` and not to
  `firestarter/tests/fixtures/planted_cmake_manifest_missing_source/src/proms/eeprom_28c.cpp`;
- bare `firestarter.h` resolves to `firestarter/include/firestarter.h` and not to
  `firestarter_app/tests/fixtures/fake_firestarter/include/firestarter.h` — the
  `firestarter` name-collision trap in citation form;
- the path-suffix form `src/proms/eeprom_28c.cpp`, which is a suffix of **both**, breaks
  toward the real file;
- and feeding a deliberately fixtures-**inclusive** index makes the T-154-13 guard
  **raise**, because a citation bound to a planted fixture would round-trip GREEN
  against the wrong file.

A rule verified only by a tree that cannot exercise it is the "pre-authored gate leg
that is unreachable" failure; this is the correction for it.

### The 2,978 unresolved rows — bridged to research's 1,351, and shown legitimate

Against a **whole-repo** index (405 source files in both repos, build/venv trees
excluded — research measured 401, and the +4 is exactly plan 03's four new
`firestarter_app/tests/fixtures/planted_*.cpp` files):

| Class | Rows |
|---|---|
| Names a **real repo file that is not a candidate** (carries no provenance hit, so needs no remap) | **2,164** |
| Names **nothing in either repo** | **814** |
| plus `rejected` (escapes the roots) | 259 |

Research's `unresolved: 1,351` was measured against that whole-tree index, i.e. it is
comparable to this run's **814 + 259 = 1,073** — a −278 gap. Research's own two figures
for the same quantity disagree (its shape table gives `bare basename, unresolved 553` +
`path, unresolved 402` = **955**, against the 1,351 in its rule statement), and this run
sits between them. **Stated as partly unexplained**: the 1,073-vs-955-vs-1,351 spread is
a definitional spread inside the recorded research, not a discrepancy this run can close,
and it is recorded here rather than smoothed over. What *is* pinned is the number that
matters for Phase 159: **2,978 rows carry no resolved path and are excluded from the
oracle by name, and every one of them is in the manifest.**

Top unresolved targets, sampled to show they are legitimate and must **not** be
force-resolved:

| Target | Rows | What it is |
|---|---|---|
| `flash_intel.cpp` | 160 (+45 as a full path) | A real firmware file that carries **no provenance hit**, so it is not a candidate and needs no remap |
| `rurp_hw_rev_utils.h` | 143 (+35 as a full path) | Same — real file, zero hits |
| `database.c` | 118 | **infoic's external decompiled source** — out of repo by design (`database.c:611` → `device->pin_map = (uint8_t)opts;`) |
| `chip_resolver.py` | 91 | Real host file, zero hits |
| `primitives.cpp` | 60 | **The v1.16 primitives layer that was never merged** — citations into a file that never existed on `beta` |
| `flash_type_3.cpp` / `flash_type_4.cpp` | 57 + 55 | Renamed or removed firmware files |
| `check_size_baseline.py`, `139-check-claims.py`, `check_permitted_claims.py`, `146-check-claims.py` | 46 + 32 + 29 + 25 | Phase-scoped checkers **under `.planning/`** — citations *within* the planning tree, not into swept source |
| `../firestarter/include/rurp_shield.h` | 29 (as `rejected`) | A `../`-relative citation, resolvable only relative to the citing document; **rejected by the path-safety rule and recorded**, never opened |

The `rejected` class also caught one shape worth naming: **6 rows** whose cited "path" is
`//gitlab.com/DavidGriffith/minipro/-/blob/a8efaedc/src/database.c` — a URL fragment that
the extractor correctly refuses as an absolute path rather than opening.

### One further honesty item: 255 resolved rows point past their file's EOF

255 of the 10,445 resolved rows carry `text_status: line_out_of_range` — the target file
resolved, but the cited line is beyond its current EOF, so the citation is already stale
today. Their `source_text` carries the declared `<UNREADABLE>` sentinel rather than a
null, because Phase 159 asserts every range record carries both texts; `text_status`
says authoritatively why, so the oracle skips such a row **by name** instead of failing
open on it. They are counted, not dropped, and they are a **pre-existing** staleness this
phase inherits rather than creates.

### The candidate set: 171 files, reconciled

| Source | Candidate files |
|---|---|
| RESEARCH.md | 160 |
| Plan 02 (`survey_provenance.py`, committed) | 169 |
| **This run** | **171** |

`169 − 160 = 9` is plan 02's already-explained delta (nine committed
`firestarter_app/tests/fixtures/planted_*` files whose GSD-shaped headers are
intentional). `171 − 169 = 2` is **plan 03's `planted_sdp_comment_brace.cpp` and
`planted_sdp_comment_misanchor.cpp`**, which are on disk and deliberately uncommitted
(D-11 reserves that sub-repo's single commit for plan 12). The delta chain is complete
to the file; nothing is unexplained.

---

## 6. SWEEP-10 pre-sweep statement — every record is `retarget: false`

**Every one of the 13,692 records carries `retarget: false`.** This is asserted by the
generator's self-check (exit 1 on any `retarget: true` row in a pre-sweep manifest) and
re-asserted independently over the written artifact.

That is not an omission; it is structural. D-08's retarget subset is *"a citation
pointing AT a comment line the sweep deletes"*, and **that subset cannot exist until the
sweep's diff exists.** It is settled — and its **count reported** — in **Phase 154 plan
12**, against the actual post-sweep diff. Per D-08 and VALIDATION.md's manual-only table,
choosing "the first surviving code line the comment described" is a per-citation human
judgment, and it is **the only manual work in the whole repair**; the reviewable artifact
is the `retarget: true` row set produced there.

The field's presence here with the value `false` is precisely what makes plan 12's update
a **field flip** rather than a schema change — and a schema change to a committed
7 MB pre-sweep artifact is exactly the risk this design removes.

**SWEEP-10 is therefore only half discharged by this plan and is left unticked in
REQUIREMENTS.md.** Its pre-sweep half — "none is silently dropped", i.e. every citation
is in the manifest with a `resolution`, and the field exists to be flipped — is
discharged here. Its post-sweep half — the retargeted rows and their count — is plan 12's.

---

## 7. Ruling B follow-on: does exempting `src/proms/eprom.cpp` change the manifest's shape?

**Answer: NO — and this run's measurement agrees with plan 02's expectation rather than
contradicting it.**

`src/proms/eprom.cpp` is the most-cited file in `.planning/`, recorded by research at
**627** citations. Measured here:

| Measurement | Value |
|---|---|
| Manifest rows resolving to `firestarter/src/proms/eprom.cpp` | **831** |
| …occurrence-equivalent | **816** |
| …of which **shifting** (at or below its first provenance hit line) | **730** |
| Rows arriving via the bare basename `eprom.cpp` | **648** |
| Rows arriving via the exact path `firestarter/src/proms/eprom.cpp` | 133 |
| Rows arriving via a path suffix (`src/proms/eprom.cpp`, `proms/eprom.cpp`) | 50 |
| Rows from `.md` documents / from `.json` documents | 823 / 8 |
| Additional rows **rejected** as `../firestarter/src/proms/eprom.cpp` | 15 |

The **648** bare-basename rows are the figure closest in shape to research's **627**
(+21, +3.3%, consistent with the same `.planning/` growth as §2); the 831 total is larger
because this run also binds the exact-path and path-suffix citation forms to the same
file, which research's basename-shaped census did not aggregate.

**Why the exemption changes nothing about the manifest's shape:** the manifest is
generated over the **candidate** set — every file under the sweep globs carrying at least
one provenance hit — which includes `eprom.cpp` (20 hits) regardless of whether Ruling B
later exempts it from being edited. If it ends up untouched, its 831 rows are **fixed
points** at Phase 159: `source_text` still matches at the recorded `target_line`, so the
round-trip check makes each row a verified no-op rather than a rewrite. The exemption
changes only the **actual swept set** that plan 12's staleness marker names (SWEEP-12) —
never the manifest's row set. The manifest is built from what *could* have moved, not
from what did, and that over-approximation is what lets Phase 159 **prove** the
non-shifting 3,196 rows did not move instead of assuming it (D-07's own reasoning).

The measurement therefore **confirms** the expectation. Had it contradicted it, that
would be recorded here in place of this paragraph.

---

## 8. The ordering resolution, and where it is recorded

"Targets a swept file" is only knowable **after** the sweep, but the manifest is a
**pre-sweep** deliverable. Resolved as research specifies: generated over the
**candidate** set now (171 files, from `survey_provenance.py` — called, never
re-implemented), with the D-08 retarget subset settled in plan 12 against the actual
post-sweep diff.

That resolution is written into the manifest's **own header record**
(`_schema.ordering_resolution`), not only here, so a Phase 159 reader working from the
artifact alone is not left guessing. The header also carries the schema version, the
14-key fixed record order, the `source_text` newline convention, the `<UNREADABLE>`
sentinel and every `text_status` value, the candidate-set definition and count, the
five-step resolution rule, the four variants plus the backtick-wrapper note, the scan
extensions and the declared exclusions with their reason, the generating command, and
both sub-repo pre-sweep shas.

### The JSONL convention, stated because none existed to inherit

No `.jsonl` file existed anywhere in the three repos before this one, so the convention
is **stated rather than inherited**: one JSON object per line; LF terminators; UTF-8 with
`ensure_ascii=False`; keys emitted in the fixed declared order and never sorted; line 1
the header record, the only line carrying `_schema`; `source_text` stored exactly as read
but **without** its line terminator, to be compared against `splitlines()` output; **no
timestamp anywhere**, which is what makes regeneration byte-identical; and an **atomic**
write (temp file plus `os.replace`), so an interrupted run cannot leave a partial
manifest in place.

### The two declared scan exclusions

`.planning/milestones/v1.33-artifacts/tools/` and this generator's own output artifacts are excluded from the
scan. The tools' sources and unit-test fixtures contain citation-shaped literals **by
construction**, a manifest that cites itself grows on every run, and a Phase 159 remapper
that rewrote its own test fixtures would break the tools that produce the manifest.

**Measured, at generation time:**

```bash
grep -roE "[A-Za-z0-9_./+-]*[A-Za-z0-9_+-]\.(cpp|hpp|ino|py|c|h)(:[0-9]+|#L[0-9]+)" \
  .planning/milestones/v1.33-artifacts/tools/ | sort | uniq -c | sort -rn
```

**12 citation-shaped literals live under the excluded prefix, and all 12 are illustrative
or unit-test-fixture strings inside these two tools** — `hardware.py:39` and
`eeprom_28c.cpp:199` and `database.py:580` in the generator's own variant table,
`notes/f.py#L42` in its `anchor_L` example, and the eight fixture citations in
`test_build_citation_manifest.py`'s `_DOC_ALL_VARIANTS` document. **None is a real
citation into swept source.** Without the exclusion all 12 would become manifest rows,
and Phase 159 would then attempt to rewrite the exact fixture strings this generator's
own tests assert on — breaking the toolchain that produced the manifest.

*Correction of record:* when the exclusion was designed, the same grep returned **zero**
matches, because the two tool modules did not exist yet. That earlier zero is superseded
by the 12 above, which were created by this very plan. Recorded rather than quietly
restated — and it is the stronger justification, because a zero-cost exclusion is merely
harmless whereas a 12-row one is load-bearing.

---

## Self-Check

- Every literal count in this file was produced by the §1 command, or by the two short
  scripts quoted inline, re-run at the time this file was written.
- No recorded figure was rewritten: `10,054`, `9,989`, `6,939`, `6,928`, `627`, `665`,
  `1,351`, `160` and `401` all appear as-recorded, each beside this run's own number.
- One item is explicitly marked **partly unexplained** (§5's 1,073 vs 955 vs 1,351
  unresolved-citation spread, which is a definitional spread inside the recorded research).
  Everything else is explained to the file or to the hit.
