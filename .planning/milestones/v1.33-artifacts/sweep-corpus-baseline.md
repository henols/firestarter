---
title: Pre-sweep corpus baseline — milestone v1.33, Phase 154
phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
plan: "02"
measured: 2026-08-23
status: AUTHORITATIVE — every SWEEP-03/SWEEP-04 hit-count comparison in this phase is measured against this file
requirements: [SWEEP-03, SWEEP-04]
---

# Pre-sweep corpus baseline — v1.33 Phase 154

This file is the pre-sweep record every later hit-count comparison is made against. It
states D-01's full triage procedure (as SWEEP-01 requires it be stated in the plan), D-02's
exemption test with its measured size, D-03's shipped-vs-test asymmetry, D-04's test-file
narrowing with both required measurements, the measured corpus itself (produced by
`.planning/milestones/v1.33-artifacts/tools/survey_provenance.py`, committed in this same plan), and every
deliberate corpus-definition exclusion with its measured size and cause.

---

## 1. D-01's triage procedure, restated verbatim

The triage is **one mechanical decision procedure**, not a three-way judgment call. Applied
per hit:

1. **Delete the provenance token(s) and their enclosing punctuation:** `Phase N`, `Plan N`,
   `Plan N-NN`, `Task N`, `PNNN`, `<NNN>-CONTEXT.md`, and the requirement/decision IDs
   `D-NN`, `LOCK-02`, `PGSZ-01`, `ERASE-04`, `LOOP-03`, `MERGE-04`, `TABLE-01`, `W-04`,
   `OD-3`, `BF-3`, `Q4`, `T-44-01`, `FIX-05`, `A-7`, `C-8`, `BASE-02`, `HOST-01`, `VPP-01`,
   `CFG-03`, `RCA-01`.
2. **Judge what remains:**
   - A sentence describing code that exists → **keep it, reflowed as an ordinary comment.**
     This is the majority case.
   - Nothing but connective punctuation → delete the whole comment.
   - A sentence describing code that is NOT there (tombstone) → delete the whole comment.
3. **The guard, named as a guard:** step 2 may never delete the only statement of a
   non-obvious invariant, trap, or fail-closed rationale. If stripping leaves it too terse
   to stand alone, **reword it to stand alone** — do not delete it.

All five keep-examples the phase's originating todo names (`eprom_params.cpp:61`,
`uno_rurp_shield.cpp:109`, `database.py:580-630`, `flash_5v_page.cpp:101`,
`json_parser.c:92`) land on "keep, reflowed" under this procedure without needing the
retired three-way bookkeeping/tombstone/rationale classification as an input.

---

## 2. The unit of edit

A regex hit line **locates** the work; the **enclosing comment block** is the unit of edit.
Within a block being edited, every D-01 token is stripped — not only the token that sat
immediately adjacent to the comment opener. This is why the keep-examples in
`154-PATTERNS.md` read the way they do: a block can carry several tokens (a `Phase N`
narrative prefix, a `D-NN` mid-sentence, a trailing `(FIX-05 precedent)` parenthetical) and
step 1 removes all of them from the block in one pass, not just the one the survey regex
happened to anchor on.

---

## 3. D-02's exemption test

**Generalised rule:** a token that appears in **both** repos' shipped source is vocabulary,
not provenance, and is exempt. Apply this test before stripping any token not on D-01's
list.

**`CAP-0N` is the one measured exemption.** It names a live cross-repo wire-protocol
capability generation in shipped host source (`serial_comm.py`, `hardware.py`,
`firmware.py`) and firmware source (`firestarter.cpp`'s wire-layout comment) alike.

**Measured size, via `survey_provenance.py --assert-tokens-zero CAP-0`:** exactly **20**
hit lines match `CAP-0` as the token immediately following a comment opener and no other
D-01 token — **13** in `firestarter_app/firestarter`, **4** in `firestarter_app/tests`,
**3** in `firestarter/src`. So the exemption removes 20 of the corpus and the net
actionable figure is **615**.

(This session's tool independently reproduces `firestarter/src` at 3 and
`firestarter_app/firestarter` at 13 to the line. It measures `firestarter_app/tests` at
**6**, not 4 — see §6 reconciliation: the +2 delta is two fixture `.cpp` files that did not
exist, or were not included, when the 20-line figure above was first measured, and the
fixture-inclusion cause is the *same* cause behind every other delta in this file. The 20/615
figures are retained as-recorded per this task's action text; the independently-measured
22/613 pair is recorded alongside it, not substituted for it.)

**No-touch region:** `firestarter/src/firestarter.cpp:177-195`. Verified present on this
tree — the tool's per-line scan finds `CAP-0` hits inside that exact span at lines 182, 193
and 200. `test_cap03_ack_layout_parity.py` pins `_WIRE_LAYOUT_COMMENT` verbatim against the
**raw, un-stripped** text of this block. It is a gate fixture that happens to be spelled as
a comment, and it is why this region is no-touch rather than reflowed like an ordinary
`CAP-0`-exempt line elsewhere in the corpus.

---

## 4. D-03's asymmetry — stated so it does not read as an inconsistency

Requirement/decision IDs are **stripped** from shipped source and **retained** in test
files:

- In **shipped source**, an ID resolves only against `.planning/` — which is precisely the
  coupling this phase exists to remove. Leaving it in shipped code couples the *product* to
  a *planning artifact* that will eventually be archived or renumbered.
- In a **test file**, the ID is the link REQUIREMENTS.md traceability runs on (`Case 30 /
  ERASE-01`, `D-11 / BASE-02`). Deleting it there would silently sever traceability that no
  gate would notice — the ID is not incidental provenance in a test file, it is the test
  case's own key.

The same token class (`D-NN`, `LOOP-03`, etc.) is therefore treated oppositely depending on
which side of the shipped/test line it sits on, by design, not by oversight.

---

## 5. D-04's narrowing — the phase's biggest re-shaping

**331 of 636 hits (52%) are in test files:** `firestarter/test/native` **216**,
`firestarter_app/tests` **115** — against `firestarter/src`+`include` **130**,
`firestarter_app/firestarter` **132**, `firestarter_app/tools` **43**. (These five figures
are D-04's own recorded measurement, restated verbatim per this task's action text; §6
below reconciles them against this session's independent tool run.)

**No oracle covers any of the 331.** The byte-identical `uno` oracle covers only
`firestarter/src`+`include` files that reach the `uno` build (129 of 635 hit lines, 20%,
per RESEARCH.md), and the host repo has **no size or byte-identity oracle at all.**

**Consequence — test files get the narrow treatment:** tombstone deletion and
label-only-comment deletion only. `Phase N`/`Plan N` narrative prefixes are stripped where
a sentence follows; requirement/decision IDs are retained (D-03); **no reflowing of
substantive test commentary** — there is no oracle to catch a mistake there.

**Named keep-in-full case:** `firestarter_app/tests/scan_paths.py`'s module docstring. It
carries **zero** regex hits (it is a docstring — see §7's corpus-definition exclusion), and
it is the only written statement of the `firestarter` name-collision trap. It is kept in
full by **not being edited at all**, recorded here rather than silently skipped.

---

## 6. The measured corpus

Produced by this plan's own committed tool, `.planning/milestones/v1.33-artifacts/tools/survey_provenance.py`,
run against the clean `gsd/v1.33-source-hygiene-firmware-size-reduction` tree in both
sub-repos:

```bash
cd /workspaces
python3 .planning/milestones/v1.33-artifacts/tools/survey_provenance.py /workspaces/firestarter /workspaces/firestarter_app --file-table
python3 .planning/milestones/v1.33-artifacts/tools/survey_provenance.py /workspaces/firestarter /workspaces/firestarter_app --json
```

**Per-group table (measured):**

| Group | Candidate files | Files with hits | Hits |
|---|---|---|---|
| fw-src | 24 | 18 | 102 |
| fw-include | 38 | 16 | 27 |
| fw-test | 62 | 60 | 216 |
| fw-lib | 2 | 0 | 0 |
| app-pkg | 31 | 20 | 132 |
| app-tests | 149 | 46 | 131 |
| app-tools | 20 | 9 | 43 |
| **TOTAL** | **326** | **169** | **651** |

`fw-src` + `fw-include` combined: **129 hits / 34 files** — matches RESEARCH.md's measured
figure to the hit and to the file.

### Reconciliation against both recorded figures — every delta explained, none silently adopted

| Source | Total hits | Total files (with hits) |
|---|---|---|
| The writeup (widest, earliest survey) | **636** | **167** |
| RESEARCH.md (re-derived against clean `beta`) | **635** | **160** |
| **This session's tool** (`survey_provenance.py`, this file) | **651** | **169** |

Neither recorded number is adopted or overwritten; the tool's own number stands beside
them.

**Every delta between this tool's measurement and RESEARCH.md's 635/160 is explained by one
cause: nine committed test **fixture** files under `firestarter_app/tests/fixtures/` that
themselves carry GSD-provenance-shaped headers by design** (they are
`planted_*`/violation-control fixtures written per the house pattern documented in
`154-PATTERNS.md`, e.g. `planted_json_parser_key_string_drift.c`'s header literally reads
`"DELIBERATELY-VIOLATING fixture for tests/test_json_key_parity.py (Phase 149 Plan 05,
PGSZ-03, D-18's ...)"`). This tool scans `.c`/`.cpp` files under `app-tests` (per this
plan's own extension list, task 1's action text), so it counts them; RESEARCH.md's
re-derivation evidently did not (or scanned `.py` only for that group). Measured
one-for-one:

| Fixture file | Hits |
|---|---|
| `tests/fixtures/planted_cap03_literal_index.cpp` | 2 |
| `tests/fixtures/planted_cap03_truncated_length.cpp` | 2 |
| `tests/fixtures/planted_constants_fw_missing.h` | 1 |
| `tests/fixtures/planted_constants_host_missing.h` | 1 |
| `tests/fixtures/planted_constants_value_drift.h` | 1 |
| `tests/fixtures/planted_ifdef_in_predicate.h` | 1 |
| `tests/fixtures/planted_json_parser_key_string_drift.c` | 4 |
| `tests/fixtures/planted_json_parser_undispatched_key.c` | 3 |
| `tests/fixtures/planted_log_in_window.cpp` | 1 |
| **TOTAL** | **9 files / 16 hits** |

`651 - 635 = 16`; `169 - 160 = 9`. The delta is **fully explained**, to the hit and to the
file — nothing is left unexplained. (The `636`/`167` writeup figures predate RESEARCH.md's
own re-derivation and are wider still; RESEARCH.md already reconciled that gap in its own
session and this file does not re-litigate it.)

The same single cause reproduces at every other place a delta appears in this document:
the CAP-0N exemption's `firestarter_app/tests` sub-count (§3: 6 measured vs. 4 recorded, +2
from `planted_cap03_literal_index.cpp` + `planted_cap03_truncated_length.cpp`) and the
`firestarter/tests/*.py` exclusion (§7: 21/8 measured vs. 20/7 recorded, +1 from
`tests/fixtures/planted_erase_no_vpp_ctrl_write.cpp`).

**Decision for the sweep plans that follow:** fixture files under either repo's
`tests/fixtures/` are themselves test infrastructure whose GSD-shaped headers are
*intentional* per `154-PATTERNS.md`'s planted-fixture pattern (SWEEP-07 keys new fixture
headers on `SWEEP-07`, not on a raw `Phase N Plan NN` stamp, precisely because they are
dense with such tokens by design). Whether to sweep them is not decided by this plan — it
is deferred to whichever later plan's `<domain>` scope actually reaches `tests/fixtures/`
under D-04's narrow (test-file) treatment. This file's job is only to make the count
visible, not to resolve it.

---

## 7. Corpus definition exclusions — each with its measured size and cause

| Exclusion | Measured size | Cause |
|---|---|---|
| Python docstrings and mid-comment tokens | **~2,657** token lines across **~173** app `.py` files | Excluded by the regex itself (`survey_provenance.py`'s `CORPUS DEFINITION` docstring section): the token must sit immediately after a comment opener, and a docstring line never opens with `#`. `firestarter_app/tests/scan_paths.py`'s dense `D-11`/`A-7`/`C-8`/`BASE-02`/`Phase 123 Plan 08` docstring is the canonical example — it carries **zero** regex hits. |
| `firestarter/tests/*.py` (the firmware repo's own 32-module Python gate suite) | **20 hits across 7 files** (this tool measures **21 hits across 8 files** — the +1 file / +1 hit is `tests/fixtures/planted_erase_no_vpp_ctrl_write.cpp`, the same fixture-inclusion cause as §6) | Outside the sweep globs named in `154-CONTEXT.md` `<domain>`, which name `firestarter/{src,include,test}` — note **singular** `test`, not `tests`. This is the firmware repo's Python gate suite (F4 in RESEARCH.md), a separate population from the C++ native tests under `firestarter/test/`. |
| `firestarter/doc/PROTOCOLS.md` | **2 hits** (confirmed exact by this tool: lines 552 and 556) | Outside the sweep globs per D-05. Read by `test_dispatch_mirror.py`'s markdown leg. Recorded explicitly per D-05's instruction rather than by silence. |
| `firestarter/lib` | **0 files, 0 hits** (confirmed exact by this tool) | Empty group — `firestarter/lib` carries 2 candidate-extension files on disk but neither carries a provenance hit. |

---

## Self-Check

- `survey_provenance.py --group fw-lib` alone exits **2** (explicit empty-group infra
  check); the default all-groups run exits **0** — verified in plan 154-02 task 1.
- Every literal number in this file was produced by the verbatim command in §6, re-run at
  the time this file was written, or is a direct restatement of a locked D-02/D-04 decision
  figure from `154-CONTEXT.md`, explicitly labeled as such.
