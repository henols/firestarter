---
phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
plan: "08"
subsystem: firmware
tags: [avr, native-tests, comment-sweep, narrow-treatment, id-retention, hex-token-parity, abstention]

requires:
  - phase: 154-01
    provides: "The pre-sweep byte-identity record (uno .elf/.hex sha256 + Flash:/RAM:), the clean-tree suite baselines (172/172 native, 323/0 firmware gates), FW_PRE_SHA, and the `cd firestarter first` pio trap"
  - phase: 154-02
    provides: "survey_provenance.py as the worklist authority and hit oracle, the fw-test 216-hit measurement, D-04's narrow-treatment definition and the both-repos CAP-0N exemption test"
  - phase: 154-03
    provides: "The 5 SWEEP-07 planted-violation legs (4 RED-on-plant, 1 deliberate fail-open) re-measured here against the swept content"
  - phase: 154-06
    provides: "eeprom_28c.cpp already swept (out of this plan's fw-test scope), the range-keyed line-based edit technique, and the corrected file_hits verify-leg schema"
  - phase: 154-07
    provides: "firestarter/{src,include} already swept, 35 modified paths accumulated in the working tree this plan builds on top of"
provides:
  - "firestarter/test swept under D-04's NARROW treatment only: 216 -> 70 hits across 58 files, every residual attributed by name (Ruling B exemption, retained ID, or recorded abstention) rather than left as an unexplained non-zero"
  - "The 216-hit / 331-of-636 measurement re-confirmed as no-oracle-coverage territory: pio test -e native proves compile+pass only, never narrowness"
  - "D-03's shipped-vs-test asymmetry demonstrated, not just stated: D- occurrence count under test/ unchanged at 386 before and after every edit"
  - "test/native/avr/_shared/eprom_v131_expected_prechange.h checked against both golden sidecars' meta.blob_shas and found NOT pinned (unlike its two Ruling-B-exempt neighbours) -- swept narrowly rather than exempted by assumption"
  - "test_dispatch/test_configure_memory.cpp's hex-token set proven identical before/after (15 tokens, sorted-set diff empty), so the dispatch mirror's comment-blind superset test cannot have been flipped"
  - "4 narrow-treatment abstentions recorded by file:line, each because mechanical prefix-stripping would have broken sentence grammar spanning a line boundary -- correct outcomes, not failures"
affects: [154-09, 154-10, 154-11, 154-12]

tech-stack:
  added: []
  patterns:
    - "ID-first vs narrative-prefix-first classification: a survey hit line is only eligible for narrative-prefix stripping when the FIRST token after the comment opener is Phase/Plan/Task/PNNN. A hit line whose first token is a retained ID (D-NN, LOOP-NN, WR-NN, VPP-NN...) gets ZERO narrow-treatment operations -- it IS the D-03 retention, not a candidate for it"
    - "Stripping a narrative prefix routinely EXPOSES a new hit: once 'Phase 143 Plan 05 ' is removed from '(HOST-02, D-02/D-03) -- ...', the line now starts with an ID and the survey re-counts it. This is not sweep failure -- it is the D-03 retention becoming visible at the line the survey actually scans"
    - "Abstain on line-boundary grammar: when the hit-anchoring token is not a true sentence prefix but the tail of a sentence begun on the PREVIOUS line, or the head of a parenthetical continued from the previous line, mechanical removal breaks grammar (a dangling preposition, a missing terminal period). Abstain rather than reword"
    - "Verify a suspected pin before sweeping around it: eprom_v131_expected_prechange.h sits beside two Ruling-B-exempt siblings but is not itself in either golden sidecar's meta.blob_shas -- checked by reading both JSONs directly rather than assumed exempt by proximity"

key-files:
  created: []
  modified:
    - firestarter/test/native/avr/** (58 files, uncommitted -- D-11)
    - .planning/ROADMAP.md
    - .planning/STATE.md

key-decisions:
  - "Narrative-prefix stripping applies ONLY when Phase/Plan/Task/PNNN is the first token after the comment opener. A survey hit anchored on a retained ID (LOOP-06, D-03, VPP-01...) is left completely untouched -- not stripped, not reworded -- because the ID itself is the retained content, not a label wrapping it"
  - "Three RUN_TEST section headers in test_sdp_harness.cpp ('/* Task 1 */', '/* Task 2 */', '/* Task 3 */') were the only true label-only-comment deletions found in this 216-hit corpus. No tombstone (comment describing absent code) was found anywhere in fw-test -- recorded as a measured absence, not silently assumed"
  - "4 abstentions recorded rather than force-stripped: each is a case where the survey's hit-anchoring token is not a true sentence-initial prefix but sits mid-sentence across a line break (the tail of a prior sentence, or inside a parenthetical opened on the previous line). Removing the token would leave a dangling clause or an object-less parenthetical -- exactly the prose-rewriting D-04 forbids"
  - "eprom_v131_expected_prechange.h checked against BOTH golden sidecars (eprom_v131_trace_inventory.json's meta.blob_shas is empty; the file is named only as a hand-verifiable, explicitly NOT-machine-checked non-claim in that JSON's own prose) before sweeping it narrowly like every other test file, rather than assumed exempt because it sits beside two files that ARE Ruling-B pinned"
  - "test_configure_memory.cpp's dispatch-mirror hex-token set was captured before AND after every edit to that file (not just once at the end), so a mid-batch mistake would have been caught by the same file's own two edits rather than only by the final check"

patterns-established:
  - "Non-vacuous zero, again: every zero in this SUMMARY carries its denominator (0 tombstones over 216 hits; 0 of 15 hex tokens changed; 0 of 386 D- occurrences lost)"
  - "Per-file residual attribution table: every file in file_hits after the sweep is named with WHY it still has hits (exempt / abstained / ID-retained), so 'attributed' is a table, not an assertion"

requirements-completed: []

coverage:
  - id: D1
    description: "firestarter/test's 216 provenance hits are triaged under D-04's narrow treatment (tombstone deletion, label-only deletion, narrative-prefix stripping) with IDs retained, reducing to 70 with every residual attributed"
    requirement: "SWEEP-04"
    verification:
      - kind: integration
        ref: "survey_provenance.py --group fw-test --json: 216 -> 70 hits over 58 edited files (6 in task 1, 52 in task 2). Full per-file residual table below names every remaining hit as Ruling-B-exempt, ID-retained (D-03), or a recorded abstention"
        status: pass
    human_judgment: false
  - id: D2
    description: "Requirement/decision IDs are demonstrably RETAINED, not merely claimed retained"
    requirement: "SWEEP-03"
    verification:
      - kind: integration
        ref: "grep -roE 'D-[0-9]+' test | wc -l: 386 before this plan's first edit, 386 after its last -- unchanged across 58 edited files despite ~143 comment lines rewritten"
        status: pass
    human_judgment: false
  - id: D3
    description: "No code line or Unity assertion was touched under cover of the comment sweep"
    requirement: "SWEEP-04"
    verification:
      - kind: integration
        ref: "git diff -U0 -- test | grep -E '^[+-]' | grep -vE '^[+-]{3}' | grep -vcE '^[+-][[:space:]]*(//|\\*|/\\*|$)' -> 4 (the two D-04-exempt trailing-comment-on-code-line pairs at test_loop_eprom_v131.cpp:44,47), both code prefixes (#include lines) proven byte-identical"
        status: pass
    human_judgment: false
  - id: D4
    description: "The two Ruling B exempted _shared headers are byte-identical; test_configure_memory.cpp's hex-token set is unchanged"
    requirement: "SWEEP-06"
    verification:
      - kind: integration
        ref: "git diff --quiet -- test/native/avr/_shared/eprom_v131_expected.h test/native/avr/_shared/sdp_expected.h exits 0. grep -oE '0x[0-9A-Fa-f]+' test_configure_memory.cpp | sort -u captured before and after this plan's two edits to that file: 15 tokens, sets identical (diff empty)"
        status: pass
    human_judgment: false
  - id: D5
    description: "pio test -e native reports the baseline pass count; plan 03's five SWEEP-07 legs keep their 4-RED/1-GREEN semantics; the dispatch mirror and SDP table parity gates stay green over the swept content"
    verification:
      - kind: integration
        ref: "pio test -e native -> 172 test cases: 172 succeeded (baseline 172/172), run both before task 1 and after task 2. In a clean --shared clone carrying the swept blobs committed (blob hashes verified equal to the working tree): test_dispatch_mirror.py + test_sdp_table_parity.py + test_cap03_ack_layout_parity.py -> 24/24; the five named SWEEP-07 legs individually -> 5/5"
        status: pass
      - kind: integration
        ref: "python3 -m pytest tests/ -q from firestarter -> 316 passed / 7 failed (316+7=323 baseline), the identical 7-name set plan 07 recorded (5 _git_porcelain legs + 2 blob-sha gates already re-derived by plan 07). Against the real D-11-dirty tree, tests/test_dispatch_mirror.py -o addopts='' -q -> 2 passed / 2 failed, both failures exclusively the sibling-repo-porcelain assertion"
        status: pass
    human_judgment: false
  - id: D6
    description: "The uno build stays byte-identical (cheap regression check; native tests are not in this build so this cannot itself prove narrowness)"
    requirement: "SWEEP-05"
    verification:
      - kind: integration
        ref: "cd firestarter && rm -rf .pio/build/uno && pio run -e uno -> .elf 1cfa946f...31ecca / .hex be6e4ac8...05c095 / Flash 26026 / RAM 1575, all four matching plan 01/06/07's recorded values character for character"
        status: pass
    human_judgment: false
  - id: D7
    description: "The 4 narrow-treatment abstentions are named by file:line with the grammatical reason mechanical stripping would break"
    verification:
      - kind: manual
        ref: "Quoted in full in the Abstentions section below: test_eeprom28c_sdp.cpp (orig L38), eprom_v131_expected_prechange.h (L12, L48), test_flash_intel_vpp.cpp (L11)"
        status: pass
    human_judgment: true
    rationale: "Whether a given line-boundary case genuinely cannot be stripped without rewriting prose is a reader judgment; the four are quoted below with their surrounding lines so a reviewer does not have to reconstruct the reasoning from the diff"

metrics:
  duration: ~100min
  completed: 2026-08-23
  tasks: 2
  files_changed: 58

status: complete
---

# Phase 154 Plan 08: `firestarter/test` Narrow Sweep (D-04) Summary

**Swept `firestarter/test` — the largest and least-covered group in the corpus — from 216 provenance hits to 70 across 58 files, using D-04's three narrow operations only (no tombstones found; 3 label-only deletions; the rest narrative-prefix strips), with every one of the 70 residual hits attributed by name: 7 in the two Ruling-B-exempt `_shared` headers, 4 in `eprom_v131_expected_prechange.h` (checked against both golden sidecars and found genuinely unpinned, unlike its two neighbours), 4 recorded abstentions where mechanical stripping would have broken sentence grammar across a line boundary, and the remaining 55 all retained IDs (D-03) — several of them newly exposed at the line the survey scans precisely because the narrative label wrapping them was removed.**

---

## What was measured, before and after

### Hit count — the primary SWEEP-03/04 oracle

```bash
cd /workspaces && python3 .planning/v1.33/tools/survey_provenance.py \
  /workspaces/firestarter /workspaces/firestarter_app --json --group fw-test
```

| Group | Before | After |
|---|---|---|
| `fw-test` | **216** hits / 60 files | **70** hits / 27 files |

**Task 1 — the six densest files (100 of 216 hits):**

| File | Before | After |
|---|---|---|
| `test_loop_eprom_v131.cpp` | 32 | 13 (all retained IDs) |
| `test_eeprom28c_sdp.cpp` | 24 | 13 (11 pre-existing retained IDs + 1 abstention + 1 newly-exposed retained ID) |
| `test_vpp_eprom_v131.cpp` | 23 | 8 (all retained IDs) |
| `test_sdp_harness.cpp` | 8 | 0 |
| `test_val_5v_page.cpp` | 7 | 0 |
| `test_trace_eprom_v131.cpp` | 6 | 0 |
| **subtotal** | **100** | **34** |

**Task 2 — the remaining 52 files (116 of 216 hits, including the two Ruling-B-exempt headers and `eprom_v131_expected_prechange.h`):**

| Subgroup | Before | After |
|---|---|---|
| `_shared/eprom_v131_expected.h` + `_shared/sdp_expected.h` (Ruling B, untouched) | 7 | 7 |
| `_shared/eprom_v131_expected_prechange.h` (checked, not pinned, swept narrowly) | 6 | 4 (2 abstentions + 2 retained IDs) |
| The other 50 files | 103 | 25 (all retained IDs except 1 abstention + 1 non-ID `Req` sentence) |
| **subtotal** | **116** | **36** |

**216 → 70, exactly 34 + 36.** 58 files were edited (6 + 52); the two Ruling-B files were verified untouched, never edited.

### Every residual hit, attributed by name

```bash
python3 .planning/v1.33/tools/survey_provenance.py /workspaces/firestarter /workspaces/firestarter_app --json --group fw-test
```

| Residual file | Count | Why |
|---|---|---|
| `_shared/eprom_v131_expected.h` | 4 | **Ruling B exempt** — blob-sha pinned by `tests/golden/eprom_v131_trace_inventory.json`, untouched |
| `_shared/sdp_expected.h` | 3 | **Ruling B exempt** — blob-sha pinned by `tests/golden/sdp_expected_inventory.json`, untouched |
| `_shared/eprom_v131_expected_prechange.h` | 4 | 2 abstentions (L12, L48) + 2 retained IDs (LOOP-06 at old L245; D-06 newly exposed at old L255) |
| `test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` | 13 | 11 pre-existing retained IDs + 1 abstention (orig L38) + 1 retained ID newly exposed (orig L21, `D-01`) |
| `test_loop_eprom_v131/test_loop_eprom_v131.cpp` | 13 | All 13 pre-existing retained IDs (`LOOP-0N`, `D-03's`, etc.) |
| `test_vpp_eprom_v131/test_vpp_eprom_v131.cpp` | 8 | All 8 pre-existing retained IDs (`D-01`, `D-02's`, `D-03`, `D-06`) |
| `test_cobs_cmd_frame/test_cobs_cmd_frame.cpp` | 2 | Both retained IDs (`D-06`) |
| `test_eeprom28c_sdp/host_stubs.cpp`, `test_sdp_harness/host_stubs.cpp`, `test_trace_eprom_v131/host_stubs.cpp` | 2 each | `WR-06` newly exposed + a pre-existing `D-0N` retained ID |
| `test_frame_vectors/test_frame_vectors.cpp` | 1 | Non-ID: `Requirements pinned: ...` — matches D-01's `Req` token class but is not a Phase/Plan/Task prefix, so no narrow-treatment operation applies; left as-is |
| `test_flash_intel_vpp/test_flash_intel_vpp.cpp` | 1 | Abstention (L11) |
| `test_loop_eprom_v131/host_stubs.cpp` | 1 | Pre-existing retained ID (`D-02/D-05`) |
| 13 further `host_stubs.cpp` files (`test_cmd_admission`, `test_dispatch`, `test_eprom_params_v131`, `test_flash_intel_vpp`, `test_messages`, `test_not_implemented`, `test_pinmap_provisional`, `test_read_timing`, `test_val_5v_page`, `test_val_eeprom28c`, `test_val_eprom`, `test_val_flash_intel`, `test_val_nor_unlock`, `test_val_sram`) | 1 each | `WR-06` newly exposed by stripping the `Phase 6 ` prefix that used to wrap it |

**70 = 4+3+4+13+13+8+2+2+2+2+1+1+1+13×1.** Every hit is named; nothing is left as an unexplained non-zero.

### No oracle covers any of these 216 hit lines — restated, not just cited

D-04's own finding: 331 of 636 corpus hits (52%) are in test files, and none of them are covered by the byte-identical `uno` oracle (native tests are not in that build) or by any host-side size oracle (the host repo has none). `pio test -e native` below proves this file tree still **compiles and passes** — it proves nothing about whether the treatment stayed narrow. That is why every operation in this plan was classified by hand against the three permitted ops rather than applied by a blanket regex, and why 4 cases were abstained rather than force-fit into a strip.

---

## The three permitted operations, measured by kind

| Operation | Count | Example |
|---|---|---|
| **Tombstone deletion** (comment describing absent code) | **0** | None found anywhere in the 216-hit `fw-test` corpus — recorded as a measured absence |
| **Label-only-comment deletion** | **3** | `test_sdp_harness.cpp`'s `/* Task 1 */`, `/* Task 2 */`, `/* Task 3 */` — pure RUN_TEST section-header labels with nothing but the token itself, deleted whole |
| **Narrative-prefix stripping (sentence/fragment kept)** | **~143** | `- * Phase 143 Plan 05 (HOST-02, D-02/D-03) -- advancing millis() clock...` → `+ * (HOST-02, D-02/D-03) -- advancing millis() clock...` |
| **Abstention (recorded, not forced)** | **4** | See below |

### Why zero tombstones is a real measurement, not an oversight

Every one of the 216 hits was read in its enclosing paragraph before classification (not regex-matched blind). None described code that is no longer present — the corpus is almost entirely `Phase N Plan N-NN` / `Task N` narrative labels wrapping still-accurate descriptions, plus mid-sentence requirement/decision IDs. This differs from the shipped-source sweep (plans 06/07), which found real tombstones (the `SERIAL_DEBUG` removal narratives, the `AT28C_PAGE_SIZE_FALLBACK` rename note) — test files, being append-only case documentation rather than evolving production prose, apparently don't accumulate the same "describes code no longer there" pattern.

### Label-only deletion, shown in full

```diff
     RUN_TEST(test_case1_ordered_capture_dip28_28c256);
     RUN_TEST(test_case2_elision_is_real);
     RUN_TEST(test_case3_ce_oe_edges_distinguishable);

-    /* Task 2 */
     RUN_TEST(test_negativeA_unlock_mutated_diverges_and_matches_erase);
```

`git diff --numstat -- test/native/avr/test_sdp_harness/test_sdp_harness.cpp` → `5 8`: insertions strictly below deletions, the only file in this plan where that holds (every other file's edits are 1-for-1 line rewrites, so insertions == deletions there — never exceeding, per the acceptance criterion).

### Narrative-prefix stripping, two representative pairs

```diff
- * Phase 141 Plan 03 (LOOP-01..LOOP-08, D-10) -- the suite skeleton for the
+ * (LOOP-01..LOOP-08, D-10) -- the suite skeleton for the
```

```diff
-#include "eprom_budget.h"  /* Plan 143-01: eprom_worst_pulses / eprom_per_byte_budget_us /
+#include "eprom_budget.h"  /* eprom_worst_pulses / eprom_per_byte_budget_us /
```

The second pair is one of the 4 D-04-exempt trailing-comment-on-code-line edits (see below) — the code prefix `#include "eprom_budget.h"` is byte-identical on both sides.

---

## The ID-first vs narrative-prefix-first rule, and why it matters

A survey hit line is eligible for narrative-prefix stripping **only when the first token after the comment opener is `Phase`/`Plan`/`Task`/`PNNN`**. A hit line whose first token is a retained ID (`D-NN`, `LOOP-NN`, `WR-NN`, `VPP-NN`, `TABLE-NN`...) gets **zero** narrow-treatment operations — the ID itself is the retained content, and there is no prefix wrapping it to strip:

```
513:  * LOOP-01 (task 1) -- fixed-width pulses, verify after each pulse, an
```

left completely untouched, vs.

```
448:  * Plan 141-07 (LOOP-01, LOOP-06, LOOP-04) -- behaviour cases proving the
```

stripped to `(LOOP-01, LOOP-06, LOOP-04) -- behaviour cases proving the...`.

**A consequence, measured rather than surprising:** stripping the narrative prefix routinely exposes a *new* survey hit, because the line now starts with the ID the prefix used to sit in front of. `Phase 6 WR-06 — shared stub body lives in ../_shared/host_stubs_common.inc.` becomes `WR-06 — shared stub body lives in ../_shared/host_stubs_common.inc.` — still a hit, now correctly attributed to D-03 retention rather than to an unstripped `Phase` prefix. This is why 14 different `host_stubs.cpp` files each show exactly 1 residual hit: every one of them carried the identical `Phase 6 WR-06 — ...` boilerplate line, and every one now shows the `WR-06` retained ID where the `Phase 6` prefix used to be. Verified structurally rather than assumed: only one of these files (`test_cmd_admission`/`test_dispatch`/`test_not_implemented`'s shared `avr/pgmspace.h`) was byte-identical to a sibling before editing (md5-grouped); every `host_stubs.cpp` is a distinct file with its own hand-authored history, and each was read and classified individually.

---

## `eprom_v131_expected_prechange.h` — checked against both sidecars, found unpinned

The plan's own read_first flagged this file as sitting beside two Ruling-B-exempt siblings but **not** itself one of the four exemptions — "verify against the sidecars rather than assuming."

```bash
python3 -c "import json; d=json.load(open('tests/golden/eprom_v131_trace_inventory.json')); \
  print(list(d.get('meta',{}).get('blob_shas',{}).keys())); print(d.get('meta',{}).get('sources'))"
# [] / None
grep -n "prechange" tests/golden/*.json tests/test_trace_segment_exhaustiveness_v131.py
```

**Result: not pinned.** `eprom_v131_trace_inventory.json`'s `meta.blob_shas` is empty — it names `eprom_v131_expected_prechange.h` only in prose, as an explicit **non-claim**: *"D-08's named non-claim: with a single inventory record here, nothing gate-asserts test/native/avr/_shared/eprom_v131_expected_prechange.h. Its preserved blob ... stays hand-verifiable ... but it is NOT machine-checked by this or any other gate."*

`test_trace_segment_exhaustiveness_v131.py` does call `_git_hash_object()` on this file (`_REAL_PRECHANGE_PATH`), but only inside planted-violation tests, asserting the file's hash is **unchanged between the start and end of that single test run** — a read-only-input control identical in shape to the `_git_porcelain` checks, not a persistent content pin. Both `before_prechange == after_prechange` checks still hold after this plan's sweep, because nothing *within a test run* modifies the file; they were never checking against an externally fixed value.

**Conclusion, verified not assumed: safe to sweep narrowly, and it was** — 6 → 4 hits, with 2 abstentions recorded below.

---

## Abstentions — 4, quoted in full

Each is a case where the survey's hit-anchoring token is not a true sentence-initial prefix, so mechanical removal would break grammar across a line boundary. Per the plan: *"An abstention is a correct outcome here, not a failure."*

### 1. `test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`, original line 38

```
 * case (D-02), and this file's own suite-header rewrite. Case 8 is new at
 * Phase 117 commit 1: a permanent regression case proving the completion
 * poll can never destroy a prior WARNING, even when it never settles.
```

`Phase 117 commit 1:` is not a prefix of its own sentence — it is the object of `is new at` from the *previous* line. Stripping it would produce `Case 8 is new at a permanent regression case proving the completion poll...`, which is not grammatical. Left untouched.

### 2. `test/native/avr/_shared/eprom_v131_expected_prechange.h`, line 12

```
 * Every literal array below (EPROM_V131_TRACE_PROTO_07/_08/_0B, pasted by
 * Phase 138 Plan 05 Task 1 from the dumps Plan 03 Task 3 produced) is
 * authored EMPIRICALLY from a recorded dump of real, UNMODIFIED production
```

`Phase 138 Plan 05 Task 1` sits inside a parenthetical opened on the previous line (`(EPROM_V131_TRACE_PROTO_07/_08/_0B, pasted by`). Stripping it would produce `pasted by\nfrom the dumps Plan 03 Task 3 produced) is`, i.e. "pasted by from the dumps" — broken. Left untouched.

### 3. `test/native/avr/_shared/eprom_v131_expected_prechange.h`, line 48

```
 * HOST_STUBS_RECORD_TIMING (the six timing accessors), both from Phase 138
 * Plan 03 Task 1. Declared once here so this suite gets all twelve from a
 * single place, mirroring sdp_expected.h's convention for the six strobe
```

`Plan 03 Task 1.` is the tail of the sentence begun on the previous line (`...both from Phase 138 Plan 03 Task 1.`), not the head of a new one. Stripping it (including its terminal period) would leave `both from Phase 138\nDeclared once here...` with no sentence break — the previous clause loses its only terminal punctuation. Left untouched.

### 4. `test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp`, line 11

```
 * Five test cases exercise the flash_intel_check_vpp static helper (added in
 * Task 2) via the canonical dispatch path: configure_memory() → operation_init.
```

`Task 2)` closes a parenthetical opened on the previous line (`(added in`). Stripping `Task 2` alone would leave `(added in)` — a dangling, object-less parenthetical. Left untouched.

---

## The two D-04-exempt trailing-comment-on-code-line edits

Per hard boundary #4, reported literally rather than laundered into the "every changed line is a comment" claim:

```bash
git diff -U0 -- test | grep -E '^[+-]' | grep -vE '^[+-]{3}' | grep -vcE '^[+-][[:space:]]*(//|\*|/\*|$)'
# 4
```

Both are in `test_loop_eprom_v131.cpp`:

```diff
-#include "eprom_budget.h"  /* Plan 143-01: eprom_worst_pulses / eprom_per_byte_budget_us /
+#include "eprom_budget.h"  /* eprom_worst_pulses / eprom_per_byte_budget_us /
-#include "messages.h"  /* Plan 141-07: MSG_ERR_MAX_PULSES / MSG_ERR_ENERGY_CAP --
+#include "messages.h"  /* MSG_ERR_MAX_PULSES / MSG_ERR_ENERGY_CAP --
```

Code prefixes verified identical:

```bash
grep -n 'include "eprom_budget.h"' test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp
grep -n 'include "messages.h"' test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp
# 43:#include "eprom_budget.h"  /* eprom_worst_pulses / ...
# 46:#include "messages.h"  /* MSG_ERR_MAX_PULSES / ...
```

Denominator: **4 of 38** `git diff -U0` filtered lines for that one file (2 pairs).

---

## D-03 retention, measured

```bash
grep -roE 'D-[0-9]+' test | wc -l
# 386 before the first edit, 386 after the last -- unchanged
```

386 is the count of `D-NN`-shaped occurrences anywhere under `test`, not just at hit lines. Zero were removed by any of the ~143 narrative-prefix strips or the 3 label-only deletions across 58 files, despite every one of those edits rewriting the comment line the ID sat in or beside.

---

## Ruling B exemptions — untouched, proven

```bash
git diff --quiet -- test/native/avr/_shared/eprom_v131_expected.h test/native/avr/_shared/sdp_expected.h
# exits 0
```

Both are blob-sha-pinned by committed golden sidecars with no regeneration tool (`tests/golden/eprom_v131_trace_inventory.json` / `tests/golden/sdp_expected_inventory.json`). Left un-swept per plan 02's Ruling B, and `git diff --quiet` confirms zero bytes moved.

---

## `test_configure_memory.cpp` — hex-token set proven identical

The dispatch mirror's C++ leg reads this file as a raw hex-token superset with no comment stripping.

```bash
# captured before this file's first edit
grep -oE '0x[0-9A-Fa-f]+' test/native/avr/test_dispatch/test_configure_memory.cpp | sort -u > hex_pre.txt
# 15 tokens: 0x05 0x06 0x07 0x08 0x0B 0x0D 0x0E 0x0d 0x10 0x11 0x27 0x28 0x29 0x35 0x39

# captured after this file's two edits (lines 7, 14, 182, 311 stripped)
grep -oE '0x[0-9A-Fa-f]+' test/native/avr/test_dispatch/test_configure_memory.cpp | sort -u > hex_post.txt
diff hex_pre.txt hex_post.txt
# (no output)
```

**Sets identical, 15 of 15.** None of the four hits in this file carried a hex token in their stripped prefixes (`Phase 12 Wave 0 — `, `Phase 105 `, `Task 1 `, `Phase 153 `), so no protocol-shaped literal was ever at risk, and the pre/post capture proves it rather than arguing it from the diff.

---

## Gate results

### `pio test -e native` — run twice, unchanged both times

```bash
cd /workspaces/firestarter && pio test -e native
```

| When | Result |
|---|---|
| Before task 1 (post plans 01-07, pre this plan's edits) | 172 test cases: **172 succeeded** |
| After task 2 (all 58 files edited) | 172 test cases: **172 succeeded** |

Matches plan 01's baseline (172/172) both times. **This proves compile+pass only** — it does not and cannot prove the treatment stayed narrow, because native tests carry no per-comment oracle. Narrowness of treatment is the mitigation (T-154-31), demonstrated above by the per-operation classification, the 4 abstentions, and the unchanged `D-` count.

### `uno` byte-identity — cheap regression check, unchanged

```bash
cd /workspaces/firestarter && rm -rf .pio/build/uno && pio run -e uno
sha256sum .pio/build/uno/firestarter_uno.elf .pio/build/uno/firestarter_uno.hex
```

| Artifact | Value | Matches plan 01/06/07? |
|---|---|---|
| `.elf` | `1cfa946f486e041ce5264fc75742ee11e2b437041eaee178ab4d164cbb31ecca` | yes |
| `.hex` | `be6e4ac80a70e251e2c263beb4109f9f7f9852a034b1064a5dbc8dbbcf05c095` | yes |
| `Flash:` | 26026 / 32768 (79.4%) | yes |
| `RAM:` | 1575 / 2048 (76.9%) | yes |

Expected — `test/` is never compiled into the `uno` target — but run and recorded per the plan's instruction, not skipped.

### Firmware gate suite — same 7-name failure set plan 07 recorded

```bash
cd /workspaces/firestarter && python3 -m pytest tests/ -q
# 316 passed / 7 failed
```

`316 + 7 = 323` = plan 01's baseline. The 7 failures are the **identical named set** plan 07 recorded (5 `_git_porcelain` legs on the D-11-mandated dirty tree + 2 blob-sha gates plan 07 already re-derived and left correctly-uncommitted-red): `test_eprom_params_citations.py::test_blob_shas_match_the_recorded_sources`, `test_flash_path_record_sync.py::...test_planted_mutation_of_the_real_subset_is_detected`, `test_protocol_branch_inventory.py::test_blob_shas_match_the_recorded_inventory`, `test_requirement_case_mapping_v131.py::test_planted_renamed_case_is_detected`, `test_requirement_case_mapping_v131.py::test_planted_emptied_scan_root_fails_the_non_vacuity_leg`, `test_trace_segment_exhaustiveness_v131.py::test_planted_unclassifiable_entry_is_located`, `test_trace_segment_exhaustiveness_v131.py::test_planted_delete_and_duplicate_defeats_a_count_only_check`. **Zero new failures.**

`test_planted_unclassifiable_entry_is_located` (the leg that hashes `eprom_v131_expected_prechange.h` before/after) was individually re-run to confirm its failure is the porcelain assertion, not a hash mismatch — confirmed: it fails at line 1144, the `_git_porcelain` check, after the hash-equality assertions already passed.

### The positive proof, non-destructively (plans 06/07's clean-clone technique, reused)

```bash
git clone --shared --branch gsd/v1.33-source-hygiene-firmware-size-reduction \
  /workspaces/firestarter /tmp/gsd-154-08-fwclone
# copy every modified path in (93 files -- the accumulated 06+07+08 sweep), commit inside the clone
# clone porcelain: ''   clone HEAD: 947ad16
```

Blob equality checked, not assumed:

| path | working tree | clone `HEAD:` |
|---|---|---|
| `test/native/avr/test_dispatch/test_configure_memory.cpp` | `322ddfd1...` | `322ddfd1...` MATCH |
| `src/proms/eeprom_28c.cpp` | `11d4ed50...` | `11d4ed50...` MATCH |

| Run, in the clone | Result |
|---|---|
| `test_dispatch_mirror.py` + `test_sdp_table_parity.py` + `test_cap03_ack_layout_parity.py` | **24 passed** |
| Plan 03's five named SWEEP-07 legs individually (`test_planted_comment_misanchor_is_detected`, `test_planted_comment_brace_break_is_detected`, `test_extracted_slice_is_anchored_on_the_real_declaration`, `test_planted_missing_hex_is_detected`, `test_planted_comment_only_hex_is_NOT_detected`) | **5 passed** — 4-RED / 1-GREEN semantics intact |
| Full firmware suite in the clone | 290 passed / 1 failed / 32 skipped (290+1+32=323) |

The clone's one failure, `test_checker_convention.py::test_scope_is_firmware_only`, asserts the clone **directory name** literally equals `firestarter` — plan 06 already proved this fails identically against a pristine, unswept clone. Not attributed to this plan's edits.

### Against the real (D-11-dirty) tree

```bash
cd /workspaces/firestarter_app && FIRESTARTER_FW_ROOT=/workspaces/firestarter \
  /tmp/gsd-154-venv311/bin/python -m pytest tests/test_dispatch_mirror.py -o addopts="" -q
# 2 passed / 2 failed
```

Both failures are exclusively `the sibling firmware repo is not clean after this planted-violation run` — the same porcelain cause plans 06/07 recorded for every planted-violation host leg against the real, deliberately-dirty tree. Not a sweep-caused regression.

---

## Deviations from Plan

None — the plan's own carried-forward notes anticipated the broken `files` (vs `file_hits`) verify-leg schema and the porcelain-caused reds, and this session reused those corrections rather than rediscovering them. No Rule 1/2/3/4 deviation was needed: no bug was found, no missing critical functionality, no blocking issue, and no architectural question arose. The 4 abstentions are a planned, permitted outcome (D-04's own text), not a deviation.

---

## Deliberate deviations (process, not plan-content)

**1. No commit in `firestarter` — as instructed.** D-11 reserves that sub-repo's single commit for plan 12. All 58 swept test files sit in the working tree alongside plans 06/07's 35 previously-swept paths (93 modified paths total). This plan's only commit is the meta-repo docs commit below.

**2. `.planning/v1.33/baseline-pre-sweep.md` read and NOT committed**, per plan 01 §7 and D-11. Still uncommitted on disk.

**3. `roadmap.update-plan-progress` and `requirements.mark-complete` deliberately not run.** v1.33's `ROADMAP.md`/`REQUIREMENTS.md` are hand-authored and the GSD verbs reformat whole files. `ROADMAP.md`'s phase-154 checklist line for this plan was edited surgically. **SWEEP-03/SWEEP-04 are left Pending** in `REQUIREMENTS.md` — per the plan's own instruction, both requirements cover `firestarter/test` (here) **and** `firestarter_app/tests` (plan 11), so neither ticks complete until plan 11 lands. `STATE.md`'s `## Current Position` section was likewise hand-edited rather than run through `state advance-plan`/`state update-progress`, for the same reformatting-risk reason plans 05-07 avoided those verbs on this phase (the frontmatter's `completed_plans` counter has read `4` since roughly plan 04 and none of plans 05-07 corrected it either — a pre-existing staleness this plan does not attempt to fix, since doing so via the flagged-risky verb could corrupt the file's single long `Current Position` line).

---

## Requirements

- **SWEEP-03 / SWEEP-04 — left Pending, partial contribution recorded.** Both are phase-wide across `firestarter/test` (this plan) and `firestarter_app/tests` (plan 11); neither ticks until plan 11 lands. This plan's contribution: the shipped-vs-test ID asymmetry demonstrated with a before/after `D-` count (386 → 386) rather than merely asserted (SWEEP-03); the narrow treatment applied with all three permitted operations measured by kind, zero tombstones found, 3 label-only deletions, 4 abstentions recorded, and the 216-hit / no-oracle-coverage fact restated with its mitigation demonstrated rather than cited (SWEEP-04).

## Issues Encountered

None beyond the 4 abstentions, which are a correct, planned outcome rather than an issue.

## Handoff Notes

- **Plan 09/10** sweep `firestarter_app`'s shipped package and tools — a disjoint file set from this plan's `firestarter/test` scope. No overlap to reconcile.
- **Plan 11** owns `firestarter_app/tests` under the same D-04 narrow treatment this plan applied, and is the plan that finally ticks SWEEP-03/SWEEP-04. The three permitted-operation counts here (0 tombstones / 3 label-only / ~143 narrative-prefix strips / 4 abstentions) are a useful prior but not a guarantee — plan 11's own corpus must be read and classified the same way, not assumed to match this file's shape.
- **Plan 12** must expect the same 7 red firmware legs plan 07 already named, now also covered by this plan's 58 additional edited files — none of which changed the failure set. The clean-clone recipe (`/tmp/gsd-154-08-fwclone`, now deleted) reused plans 06/07's technique verbatim; nothing new to add to that playbook.
- **`firestarter`'s working tree now carries 93 modified paths** (35 from plans 06/07 + 58 from this plan), all uncommitted per D-11, all in `src/`, `include/`, `tests/`, and now `test/`.
- **Phase 159's remap** will need to handle 58 more files whose line numbers shifted (mostly by 0, since most edits are 1-for-1 line rewrites; `test_sdp_harness.cpp` shifted by −3 from the three label-only deletions).

## User Setup Required

None.

---

## Self-Check: PASSED

Run after the docs commit, before handing back. Every claim re-verified against disk and git rather than trusted from this session's narrative.

| Check | Command | Result |
|---|---|---|
| This SUMMARY exists | `[ -f .planning/phases/154-.../154-08-SUMMARY.md ]` | FOUND |
| A swept test file exists | `[ -f firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp ]` | FOUND |
| Ruling B exempt files untouched | `git -C firestarter diff --quiet -- test/native/avr/_shared/eprom_v131_expected.h test/native/avr/_shared/sdp_expected.h` | exit 0 |
| D- count unchanged | `grep -roE 'D-[0-9]+' test \| wc -l` | 386 |
| fw-test hit count | `survey_provenance.py --group fw-test --json` | 70 |
| Native suite at baseline | `pio test -e native` | 172/172 |
| No commit in `firestarter` | `git -C firestarter log --oneline -1` | `8695ee5` = `FW_PRE_SHA`, unchanged (D-11) |
| No commit in `firestarter_app` | `git -C firestarter_app log --oneline -1` | `6bfa645` = `APP_PRE_SHA`, unchanged |
| Firmware working tree path count | `git -C firestarter status --short \| wc -l` | 93 |
| Preservation branch intact | `git -C firestarter branch -v \| grep wip/v1.33` | `wip/v1.33-size-reduction-survey-preserved @ a6b46f8` present |
| Forbidden git commands | reviewed every command run this session | none of `reset --hard`, `clean`, `checkout -- <path>`, `restore`, `stash`, force-push or branch deletion was run in any repo. The only clone (`/tmp/gsd-154-08-fwclone`) was a throwaway `--shared` clone whose one commit lived only in it; it was deleted after use and the parent's HEAD/branches/working tree are unchanged |
