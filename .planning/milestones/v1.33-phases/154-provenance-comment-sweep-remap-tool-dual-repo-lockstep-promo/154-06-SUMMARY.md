---
phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
plan: "06"
subsystem: firmware
tags: [avr, at28c, eeprom, sdp, comment-sweep, byte-identity, sha256, comment-blind-gate, datasheet-citation]

requires:
  - phase: 154-01
    provides: "The pre-sweep byte-identity record (uno .elf/.hex sha256 + Flash:/RAM:), the clean-tree suite baselines (172/172 native, 323/0 firmware gates), the FW_PRE_SHA anchor, and the `cd firestarter first` pio trap"
  - phase: 154-02
    provides: "survey_provenance.py (the hit oracle), the measured 33-hit count for this file, D-01's triage procedure stated verbatim with its unit-of-edit rule, and the gate dispositions naming test_sdp_table_parity.py as the one genuinely dangerous gate"
  - phase: 154-03
    provides: "The 5 SWEEP-07 planted-violation legs, including the anchoring leg that reads the real (now swept) eeprom_28c.cpp — the control that makes a green run from this gate mean something"
provides:
  - "firestarter/src/proms/eeprom_28c.cpp swept: 33 provenance hits -> 0, in 34 rewritten comment blocks, with the uno .elf AND .hex sha256 both byte-identical to plan 01's pre-sweep record"
  - "The _PAIR_RE collision removed BY CONSTRUCTION (Ruling H), over-delivered: zero brace-wrapped hex pairs AND zero braces of any kind on any of the file's 580 comment lines"
  - "The AT28C datasheet citation of record preserved verbatim; the C++ linkage invariant and the no-payload safety invariant both reworded to stand alone, the latter with its two load-bearing consequences enumerated"
  - "A positive, non-destructive proof that the sweep breaks no gate: the same 6 porcelain-asserting host modules run 60/60 and test_sdp_table_parity.py runs 8/8 against a throwaway clone carrying the swept blob committed"
  - "A measured attribution of all 16 red legs (5 firmware + 11 host) to the single _git_porcelain precondition D-11 mandates, with the case totals shown to be conserved (318+5 = 323)"
affects: [154-07, 154-08, 154-09, 154-10, 154-11, 154-12, 159]

tech-stack:
  added: []
  patterns:
    - "De-shape, do not order: when a comment-blind extractor could mistake a comment's literal for code, rewrite the literal into a non-matching form rather than relying on it staying outside the extractor's slice"
    - "Range-keyed block replacement: apply comment rewrites by verified 1-based line ranges applied bottom-up, so no `old` string is ever retyped and no offset drifts"
    - "Prove-by-clean-clone: when a mandated uncommitted state makes porcelain-asserting gates red, re-run the same gates against a throwaway --shared clone carrying the change COMMITTED, with the blob hash shown equal — a positive proof instead of an argument"
    - "Pristine control for a clone artifact: before calling a clone-only failure an artifact, run it in a clone with no change applied"

key-files:
  created: []
  modified:
    - firestarter/src/proms/eeprom_28c.cpp
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
    - .planning/STATE.md

key-decisions:
  - "Ruling H discharged by construction and deliberately over-delivered: zero braces of ANY kind on any comment line, not merely zero brace-wrapped hex pairs — including the pre-existing payload-order comment that was never in the gate's slice"
  - "The swept block carries a standing instruction to keep every comment in the file free of both shapes, so the collision cannot silently return; the prior state relied on an ordering accident nothing enforced"
  - "All 16 red legs attributed to one cause (_git_porcelain on the D-11-mandated dirty tree) AND disproven as sweep damage positively, by a clean-clone re-run, not argued away from assertion ordering alone"
  - "`(D-16)` on the code line `(void)page_load_aborted;` deliberately LEFT: not a survey hit, and editing it would falsify this plan's own every-changed-line-is-a-comment criterion. Recorded as a named residual"
  - "The plan's task-1 automated verify leg was broken as written (indexes `files`, an integer count, instead of `file_hits`) and was fixed forward against the real schema rather than silently worked around"
  - "No commit in `firestarter` — D-11 reserves that sub-repo's single commit for plan 12; the edit is left in the working tree deliberately"

patterns-established:
  - "Comment-blind-gate hygiene: remove the SHAPE class from comments, not the instance, and leave a written rule so the next editor does not rediscover the hazard"
  - "Non-vacuous zero: every zero-count assertion in this plan is printed beside its denominator (0 of 752 diff lines non-comment; 0 pair shapes over 580 comment lines)"
  - "Conserved-total failure accounting: report N pass / M fail alongside N+M == the baseline case count, so a suite regression cannot hide as a collection change"

requirements-completed: [SWEEP-08]

coverage:
  - id: D1
    description: "All 33 provenance hits in eeprom_28c.cpp triaged under D-01's procedure; the file's hit count reaches 0"
    requirement: "SWEEP-08"
    verification:
      - kind: integration
        ref: "python3 .planning/v1.33/tools/survey_provenance.py /workspaces/firestarter /workspaces/firestarter_app --json --group fw-src -> eeprom_28c.cpp absent from file_hits; group total 102 -> 69 (-33)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The AT28C datasheet citation of record survives verbatim"
    requirement: "SWEEP-08"
    verification:
      - kind: integration
        ref: "grep -c '0270L-PEEPR-2/09' -> 1 ; grep -c 'DS20006432B' -> 3 ; the whole [CITED: ...] bracket byte-unchanged in the diff"
        status: pass
    human_judgment: true
    rationale: "Whether the citation is UNALTERED (not merely present) is a reader judgment; the surviving text is quoted in full below so a reviewer need not reconstruct it"
  - id: D3
    description: "The no-data-write-follows safety invariant survives in full, stated so it stands alone"
    requirement: "SWEEP-08"
    verification:
      - kind: integration
        ref: "grep -ic 'no data write' -> 3"
        status: pass
    human_judgment: true
    rationale: "Whether the invariant retains its full FORCE is a reader judgment; the surviving sentence is quoted in full below"
  - id: D4
    description: "Ruling H: no brace-wrapped hex-pair form survives in any comment in the file, so the _PAIR_RE collision is removed rather than depending on ordering"
    requirement: "SWEEP-08"
    verification:
      - kind: integration
        ref: "grep -nE '^[[:space:]]*(//|\\*|/\\*)' src/proms/eeprom_28c.cpp | grep -cE '\\{[[:space:]]*0x[0-9A-Fa-f]+[[:space:]]*,[[:space:]]*0x[0-9A-Fa-f]+[[:space:]]*\\}' -> 0 over a 580-comment-line denominator; and grep for ANY brace on a comment line -> no output"
        status: pass
    human_judgment: false
  - id: D5
    description: "The uno build is byte-identical after this file is swept: sha256 of the .elf (and .hex) matches the pre-sweep record"
    requirement: "SWEEP-05"
    verification:
      - kind: integration
        ref: "cd /workspaces/firestarter && rm -rf .pio/build/uno && pio run -e uno && sha256sum .pio/build/uno/firestarter_uno.{elf,hex} -> 1cfa946f...31ecca / be6e4ac8...05c095, identical before and after; Flash: 26026 / RAM: 1575 unchanged"
        status: pass
    human_judgment: false
  - id: D6
    description: "No code line changed under cover of the comment sweep"
    requirement: "SWEEP-08"
    verification:
      - kind: integration
        ref: "git -C firestarter diff -U0 -- src/proms/eeprom_28c.cpp | grep -E '^[+-]' | grep -vE '^[+-]{3}' | grep -vcE '^[+-][[:space:]]*(//|\\*|/\\*|$)' -> 0, denominator 752"
        status: pass
    human_judgment: false
  - id: D7
    description: "Both SWEEP-07 controls still detect their plants and the anchoring leg still passes against the swept file"
    requirement: "SWEEP-07"
    verification:
      - kind: integration
        ref: "FIRESTARTER_FW_ROOT=<clean clone carrying the swept blob> pytest tests/test_sdp_table_parity.py -o addopts='' -q -> 8 passed; blob hash of clone file == working-tree file (11d4ed50...)"
        status: pass
      - kind: integration
        ref: "Against the real (D-11-dirty) tree: 5 passed / 3 failed, all three exclusively on the trailing _git_porcelain assertion; detection assertions demonstrably fired first"
        status: pass
    human_judgment: false
  - id: D8
    description: "The native and firmware gate suites are no worse than plan 01's baseline, with every new failure named and attributed"
    verification:
      - kind: integration
        ref: "pio test -e native -> 172 test cases: 172 succeeded (baseline 172/172)"
        status: pass
      - kind: integration
        ref: "python3 -m pytest tests/ -q -> 318 passed / 5 failed; 318+5 == 323 baseline total; all 5 messages verbatim 'the firmware repo's working tree is no longer clean after the planted-* test'"
        status: pass
    human_judgment: false

metrics:
  duration: ~35min
  completed: 2026-08-23
  tasks: 2
  files_changed: 4

status: complete
---

# Phase 154 Plan 06: `eeprom_28c.cpp` Swept in Isolation (SWEEP-08) Summary

**Swept the densest and highest-risk file in the corpus — 33 hits, 34 comment blocks, 353 insertions / 399 deletions — with the AT28C datasheet citation of record verbatim, the C++ linkage invariant and the no-payload safety invariant both reworded to stand alone, the `uno` `.elf` AND `.hex` sha256 byte-identical to plan 01's pre-sweep record, and the `_PAIR_RE` collision removed by construction rather than by ordering: there is now not one brace of any kind on any of the file's 580 comment lines.**

---

## What was measured, before and after

Every number below carries the command that produced it. Nothing is quoted from research or from the plan.

### Hit count — the SWEEP-03 oracle

```bash
cd /workspaces && python3 .planning/v1.33/tools/survey_provenance.py \
  /workspaces/firestarter /workspaces/firestarter_app --json --group fw-src
```

| Quantity | Before | After |
|---|---|---|
| `src/proms/eeprom_28c.cpp` | **33** | **0** — the path is absent from `file_hits` entirely |
| `fw-src` group total | 102 | **69** (−33, exactly this file's contribution and nothing else) |

The tool omits zero-hit files from `file_hits` rather than emitting a `0` row, so "absent" *is* the zero. Both readings are asserted.

### Byte-identity — the SWEEP-05 oracle, run per file (Ruling E: hash pair **and** size pair)

```bash
cd /workspaces/firestarter && rm -rf .pio/build/uno && pio run -e uno \
  && sha256sum .pio/build/uno/firestarter_uno.elf .pio/build/uno/firestarter_uno.hex
```

| Artifact | Pre-sweep (measured this session) | Post-sweep (measured this session) | Plan 01's record |
|---|---|---|---|
| `firestarter_uno.elf` | `1cfa946f486e041ce5264fc75742ee11e2b437041eaee178ab4d164cbb31ecca` | `1cfa946f486e041ce5264fc75742ee11e2b437041eaee178ab4d164cbb31ecca` | identical |
| `firestarter_uno.hex` | `be6e4ac80a70e251e2c263beb4109f9f7f9852a034b1064a5dbc8dbbcf05c095` | `be6e4ac80a70e251e2c263beb4109f9f7f9852a034b1064a5dbc8dbbcf05c095` | identical |
| `Flash:` | 26026 / 32768 (79.4%) | 26026 / 32768 (79.4%) | identical |
| `RAM:` | 1575 / 2048 (76.9%) | 1575 / 2048 (76.9%) | identical |

**Character for character, on both artifacts, in both directions.** No delta, so SWEEP-05's revert rule never fired and nothing had to be explained. The pre-sweep column was re-measured on this machine rather than trusted from the record — it reproduced plan 01 exactly, which also re-confirms the cold-build convention is deterministic here.

### Diff shape — SWEEP-08's "no code line changed" assertion

```bash
git -C firestarter diff --numstat -- src/proms/eeprom_28c.cpp
# 353  399  src/proms/eeprom_28c.cpp
git -C firestarter status --short
#  M src/proms/eeprom_28c.cpp        <- one path, nothing else

git -C firestarter diff -U0 -- src/proms/eeprom_28c.cpp | grep -E '^[+-]' \
  | grep -vE '^[+-]{3}' | grep -vcE '^[+-][[:space:]]*(//|\*|/\*|$)'
# 0        <- non-comment changed lines
git -C firestarter diff -U0 -- src/proms/eeprom_28c.cpp | grep -E '^[+-]' | grep -vcE '^[+-]{3}'
# 752      <- denominator, so the 0 above is not vacuous
```

**0 of 752** added-or-removed lines is anything other than a comment line or a blank. The denominator is printed beside the zero deliberately.

### Ruling H — the collision, removed by construction

```bash
# brace-wrapped hex pairs, restricted to comment lines
grep -nE '^[[:space:]]*(//|\*|/\*)' firestarter/src/proms/eeprom_28c.cpp \
  | grep -cE '\{[[:space:]]*0x[0-9A-Fa-f]+[[:space:]]*,[[:space:]]*0x[0-9A-Fa-f]+[[:space:]]*\}'
# 0
grep -cE '^[[:space:]]*(//|\*|/\*)' firestarter/src/proms/eeprom_28c.cpp
# 580      <- denominator

# stronger: ANY brace on ANY comment line
grep -nE '^[[:space:]]*(//|\*|/\*)' firestarter/src/proms/eeprom_28c.cpp | grep -E '[{}]'
# (no output)
```

The scope restriction to comment lines is required and deliberate: the real initializer at `:213-217` legitimately uses `{0x5555, 0xAA}` on **code** lines, so a file-wide count would be self-invalidating.

**The over-delivery is the point.** The plan asked for zero pair *shapes* on comment lines. The file now carries zero braces *of any kind* on any comment line — which also removed the pre-existing `{expected, observed, addr>>16, addr>>8, addr}` payload-order comment (old `:883`) that was never in the gate's slice and never a hazard. Removing the shape class beats removing the instance, and it makes the grep in this SUMMARY a total statement rather than a filtered one.

The three literals were rewritten exactly as `154-PATTERNS.md:527-530` recommended:

```
// SAFETY property, not a style point: writing 0xAA / 0x55 / 0xA0 to
// 0x5555 / 0x2AAA / 0x5555 -- the exact three writes this table holds -- is
// byte-identical to FLASH_ENABLE_WRITE (the PROTECTED-WRITE PREFIX) and to
// FLASH_ENABLE_WRITE_PROTECTION.
```

The byte values and their target addresses are both still legible; only the shape changed. And the block now ends with a **written rule** so the collision cannot silently return:

```
// Deliberate de-shaping: the three writes above are spelled as
// value-to-address correspondences, NOT as brace-wrapped address/byte
// literals, on purpose. A host-side parity gate extracts this file's tables
// with a brace-wrapped hex-pair regex and a raw brace-depth walk, and both
// mechanisms are comment-blind -- so a brace-wrapped hex pair, or a stray
// brace, anywhere in a comment here could be mistaken for part of the real
// initializer below. Keep every comment in this file free of both shapes.
```

Before this plan the literals were harmless only because the gate's anchor happened to sit below them. Nothing enforced that. Now the hazard is gone and the next editor is told the rule instead of being left to rediscover it.

---

## The three things that had to survive — quoted in full, for review

The plan named these as reader judgments rather than laundering them into greps. Here is the surviving text so a reviewer does not have to reconstruct it from the diff.

### 1. The datasheet citation of record — verbatim

```
// AT28C SDP enable: 3-write sequence to the same magic addresses, terminal
// byte 0xA0. [CITED: Atmel doc0270 rev 0270L-PEEPR-2/09 section 19 note 2 --
// the citation of record, corroborated by Microchip DS20006432B section 6.18
// note 2, whose sentence is that the Write Protect state activates at the
// end of the write cycle EVEN IF NO OTHER DATA IS LOADED.] That sentence is
// why this table carries no payload byte after the sequence and why the
// standalone lock op (below) issues no data write and no read after it.
```

The `[CITED: … ]` bracket is byte-unchanged. The single edit in this paragraph is the one `154-PATTERNS.md` prescribed: `D-11's standalone lock op (below) issues no data write` became `why the standalone lock op (below) issues no data write`. A citation is not provenance; a decision label inside a citation's prose is.

`grep -c '0270L-PEEPR-2/09'` = **1**. `grep -c 'DS20006432B'` = **3** (this site plus the two `t_WC` / `t_BLC` constant citations).

### 2. The C++ linkage invariant

```
// The `extern` declaration immediately below is LOAD-BEARING, not
// decorative: in C++ a namespace-scope `const` array has INTERNAL linkage
// unless a prior declaration with external linkage is visible, and the
// identity/distinctness cross-guard must be able to pin this PRODUCTION
// array directly rather than a transcribed test-local copy (same shape as
// EEPROM_SDP_DISABLE's extern above).
```

This is `154-PATTERNS.md`'s worked `after`, adopted verbatim. `Plan 119-06`, `FIX-05` and the `.planning/`-only parenthetical are gone; the non-obvious invariant is intact. The sibling `EEPROM_SDP_DISABLE` block at `:146-158` received the same treatment, so both `extern`s now explain themselves without a plan label.

### 3. The safety invariant — reworded to stand alone, and strengthened

```
// SAFETY property, not a style point: writing 0xAA / 0x55 / 0xA0 to
// 0x5555 / 0x2AAA / 0x5555 -- the exact three writes this table holds -- is
// byte-identical to FLASH_ENABLE_WRITE (the PROTECTED-WRITE PREFIX) and to
// FLASH_ENABLE_WRITE_PROTECTION. The ONLY thing separating "lock the chip"
// from "prefix a byte write" is that NO DATA WRITE FOLLOWS this sequence.
// That makes the absence of a payload a hard safety invariant, not a
// convenience. Two consequences follow, and both are load-bearing:
//
//   1. This table is kept 0x0D-LOCAL and the flash_utils.h duplication is
//      PRESERVED rather than deduped. Once the bytes match, the array NAME
//      is the only discriminator left, so folding the three tables into one
//      would destroy real semantics. The byte-frozen flash_utils.h stays
//      untouched for the same reason.
//   2. That absence cannot be asserted by comparing tables -- comparing
//      tables can only ever prove the bytes are equal, which they are by
//      construction. It has to be asserted on the emitted STREAM instead,
//      by a no-payload case plus an exact-divergence-index case.
```

All three facts the plan required survive: that the absence of a payload is a hard safety invariant and not a convenience; why the `flash_utils.h` duplication is preserved rather than deduped (the array NAME is the only discriminator once the bytes match); and why that absence cannot be asserted by comparing tables but has to be asserted on the emitted stream. The labels `D-10`, `LOCK-05`, `Plan 119-05` and the abandoned-commit reference are gone.

It is also **clearer than before**: the two consequences were a single run-on clause and are now enumerated, and consequence 2 now says *why* comparing tables cannot work (it can only re-prove an equality that holds by construction) rather than merely asserting it. `grep -ic 'no data write'` = **3**.

Two further dispositions the plan called for, both done as specified:

- **The `D-09` tombstone-shaped cross-reference block collapsed rather than vanishing.** Its operative fact — this table is deliberately not deduped against `flash_utils.h` — is the same fact the safety block states, so it folded into consequence 1 instead of being lost.
- **The `ROADMAP criterion 5` bookkeeping paragraph went**, keeping only its one durable part: an in-repo pointer to the sibling rationale in `test/native/avr/test_sdp_harness/test_sdp_harness.cpp`, with the line numbers dropped so the pointer cannot go stale.

---

## Gate results — and the honest accounting of every red leg

### Green outright

| Suite | Command | Baseline (plan 01) | This session |
|---|---|---|---|
| native | `pio test -e native` | 172 / 172 | **172 test cases: 172 succeeded** |

### Red, and why — one cause, measured, not inferred

The edit is **deliberately uncommitted** in `firestarter` (D-11 reserves that sub-repo's single commit for plan 12). Sixteen planted-violation legs across both repos assert `_git_porcelain(FW_ROOT) == ""` as their final step, so a dirty firmware tree makes them red *by their own design*. `154-PATTERNS.md` predicted exactly this ("⚠ Note (F7/F8) … These legs are RED today for exactly that reason").

| Suite | Result | Case total conserved? | Failure classification |
|---|---|---|---|
| firmware gates (`pytest tests/`) | **318 passed / 5 failed** | 318 + 5 = **323** = baseline total | All 5 messages verbatim `the firmware repo's working tree is no longer clean after the planted-* test` |
| `test_sdp_table_parity.py` | 5 passed / 3 failed | 8 = baseline total | All 3 on the trailing `_git_porcelain` assertion |
| 6 porcelain-asserting host modules | 11 failed / 42+ passed | — | 2 messages, both porcelain: `…is no longer clean after the planted-copy test -- it is a read-only input to this phase` (×2) and `the sibling firmware repo is not clean after this planted-violation run` (×9) |

The five firmware failures are `test_flash_path_record_sync`, `test_requirement_case_mapping_v131` (×2) and `test_trace_segment_exhaustiveness_v131` (×2) — the modules memory already records as whole-repo-porcelain asserters. Classified by reading the actual assertion messages:

```bash
cd /workspaces/firestarter && python3 -m pytest tests/ -q 2>&1 \
  | grep -E "^E +AssertionError" | sort | uniq -c
#   1 ... no longer clean after the planted-copy test
#   1 ... no longer clean after the planted-delete-and-duplicate test.
#   1 ... no longer clean after the planted-empty-root test.
#   1 ... no longer clean after the planted-rename test.
#   1 ... no longer clean after the planted-unclassifiable-entry test.
```

**Zero content failures.** The case totals are conserved on both sides, so nothing was lost to a collection change.

### The positive proof that the sweep itself breaks nothing

Attribution by assertion-ordering is an argument. It is available here — in `test_sdp_table_parity.py` the porcelain check is the *last* assertion in each leg, so the detection assertions demonstrably fired first, visible in the traceback (`comment mis-anchor detected` matched, `before_sha == after_sha` held) — but an argument is weaker than a measurement.

So the measurement was taken, non-destructively:

```bash
git clone --shared --branch gsd/v1.33-source-hygiene-firmware-size-reduction \
  /workspaces/firestarter /tmp/gsd-154-06-fwclone
cp /workspaces/firestarter/src/proms/eeprom_28c.cpp /tmp/gsd-154-06-fwclone/src/proms/
cd /tmp/gsd-154-06-fwclone && git commit -m '...' -- src/proms/eeprom_28c.cpp
# clone porcelain: ''
# clone blob == working blob: 11d4ed5085889f38df7a500a1932c70d13be65ba (both sides)

cd /workspaces/firestarter_app
FIRESTARTER_FW_ROOT=/tmp/gsd-154-06-fwclone /tmp/gsd-154-venv311/bin/python \
  -m pytest tests/test_sdp_table_parity.py -o addopts="" -q          # 8 passed
FIRESTARTER_FW_ROOT=/tmp/gsd-154-06-fwclone /tmp/gsd-154-venv311/bin/python \
  -m pytest tests/test_dispatch_mirror.py tests/test_cap03_ack_layout_parity.py \
            tests/test_py32_flash_map_host.py tests/test_json_key_parity.py \
            tests/test_py32_asset_name_host.py tests/test_sdp_table_parity.py \
            -o addopts="" -q                                          # 60 passed
```

**8/8 and 60/60 over the swept content**, with the clone's blob hash shown identical to the working-tree file. The anchoring leg — `test_extracted_slice_is_anchored_on_the_real_declaration`, the one leg that could legitimately have changed behaviour as a result of this sweep — passes against the **real, swept** file. That is the evidence Ruling H's de-shaping worked, and it is the reason the de-shaping was preferred over preserving an ordering dependency.

The clone is a throwaway; the parent repo was verified untouched afterwards (`HEAD` still `8695ee5` = `FW_PRE_SHA`, `wip/v1.33-size-reduction-survey-preserved @ a6b46f8` intact, one modified path).

### One clone-only failure, controlled before being dismissed

The clone's full firmware gate run showed `test_checker_convention.py::test_scope_is_firmware_only` failing. Rather than assume "clone artifact", a **pristine** clone with no sweep applied was built and the same module run:

```bash
git clone --shared --branch gsd/... /workspaces/firestarter /tmp/gsd-154-06-fwpristine
cd /tmp/gsd-154-06-fwpristine && python3 -m pytest tests/test_checker_convention.py -q
# 1 failed, 6 passed   <- fails with NO sweep applied
```

It fails identically without the sweep, so it is a clone-path artifact and is **not** attributed to this edit. (The clone run also skips 32 cases the real tree runs, which is why the clone is used as a *supplementary* oracle for the 6 named modules and not as a substitute for the real-tree firmware suite.)

---

## Triage scope, stated so it is reviewable

The unit of edit is the enclosing comment block of each hit, per `sweep-corpus-baseline.md` §2. Within each of the 34 edited blocks, **every** D-01-class token was stripped, not only the one the survey regex anchored on: `Phase NNN`, `Plan NNN-NN`, `Task N`, `D-NN`, `D-153-NN`, `FIX-NN`, `OBS-NN`, `LOCK-NN`, `SAF-05`, `ERASE-NN`, `PGSZ-NN`, `MERGE-05`, `HOST-01/03`, `F-118-01`.

Kept, because they are not GSD provenance:

- Datasheet and application-note citations (`0270L-PEEPR-2/09`, `DS20006432B`, `DS20006386B`, `doc0544.pdf` Rev `0544B-10/98`, `Table 6-1`).
- Real in-repo paths and identifiers (`flash_utils.h`, `memory.cpp:48-58`, `test/native/avr/_shared/host_stubs_common.inc`, `test_case8_completion_poll_preserves_prior_severity`, `test_fix06_page_boundary_window_readback`, `check_no_log_in_sdp_window.py`).
- `gh#11` — a live GitHub issue, an external reference.
- `--policy merge05` — verified a **live CLI value** in `firestarter/scripts/check_size_baseline.py`, not a comment label, so it stays.

Stripped, because they resolve only against `.planning/`: `117-CONTEXT.md`, `152-CONTEXT.md`, `119-MEASUREMENT.md`, `119-04-SUMMARY.md`, `ROADMAP criterion 5`, `PROJECT.md's FIFTH CORRECTION`, `REQUIREMENTS.md's validation ceiling`, `.planning/research/SUMMARY.md`.

Tombstones deleted under step 2 (each describing code that is not there): the `AT28C_PAGE_SIZE_FALLBACK` rename narrative; the "`FIX-02` replaces the inverted read-back" framing (rewritten as a forward-looking *do not add one* rule, which is what step 3's guard protects); the `PROJECT.md` FLASH-vs-TIMING budget conflation paragraph, whose only code-relevant sentence duplicated the paragraph above it.

**Named residual, recorded rather than hidden.** One `(D-16)` token remains in the file, in the trailing comment on the **code** line `(void)page_load_aborted;`. It is deliberately left: it is not a survey hit (the token does not follow the comment opener), and editing it would falsify this plan's own acceptance criterion that every added and removed line is a comment line or blank. Measured to be the only such case:

```bash
grep -nE '^[[:space:]]*[^/[:space:]].*//' src/proms/eeprom_28c.cpp \
  | grep -nE 'D-[0-9]|FIX-[0-9]|LOCK-[0-9]|OBS-[0-9]|SAF-[0-9]|ERASE-[0-9]|Phase |Plan |Task |CONTEXT'
# 833:    (void)page_load_aborted;  // ... report identically (D-16)
```

---

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] The plan's task-1 automated verify leg was broken as written**

- **Found during:** Task 1, first attempt to run the acceptance oracle.
- **Issue:** The leg does `d['fw-src']['files']` and iterates it. `survey_provenance.py` emits `files` as an **integer file count** and puts the per-file table under `file_hits` (a dict). The leg raised `TypeError: 'int' object is not iterable` and therefore measured nothing — it would have failed closed rather than falsely passed, but it could not discharge the criterion.
- **Fix:** Re-expressed against the real schema: assert `'src/proms/eeprom_28c.cpp' not in d['fw-src']['file_hits']` and report the group total delta (102 → 69) beside it. Both readings are recorded above.
- **Files modified:** none (verification command only).

**2. [Rule 2 - Missing critical] Ruling H extended from "no pair shape" to "no brace at all"**

- **Found during:** Task 1, while checking the result of the de-shaping.
- **Issue:** The plan's criterion is satisfied by zero brace-wrapped *hex pairs* on comment lines. But the file still carried a balanced `{expected, observed, addr>>16, addr>>8, addr}` in the `eeprom28c_verify_page_readback` header comment. That one is genuinely harmless today (it sits ~660 lines below the anchor the brace walk starts from, and carries no hex), but it is the same *class* of hazard the ruling exists to remove, and leaving it would make the SUMMARY's grep a filtered claim instead of a total one.
- **Fix:** De-braced it too. The file now has zero braces of any kind on any comment line, and the swept block states the rule for future editors.
- **Files modified:** `firestarter/src/proms/eeprom_28c.cpp`.

### Deliberate deviations

**3. No commit in `firestarter` — as instructed.** D-11 reserves that sub-repo's single commit for plan 12. The swept file sits in the working tree. This plan's only commit is the meta-repo docs commit. Consequence, stated plainly: the 16 porcelain-asserting legs stay red until plan 12 commits, and that is the mandated state, not a regression.

**4. `.planning/v1.33/baseline-pre-sweep.md` was read and NOT committed**, per plan 01's §7 and D-11. It remains uncommitted on disk.

**5. `roadmap.update-plan-progress` deliberately not run.** v1.33's `ROADMAP.md` and `REQUIREMENTS.md` are hand-authored and the GSD verbs reformat whole files. Both were edited by surgical hand replacement with a uniqueness assertion on each `old` string, as plans 01-05 did.

---

## Method note — why the edit was applied by line range

34 comment blocks had to be replaced without touching a single code line. Retyping each block's existing text as an `old` string invites transcription drift, and a whitespace mismatch would have silently skipped a block. Instead the sweep was applied as `(start_line, end_line, new_text)` triples, with two pre-flight assertions: the ranges are disjoint and ascending, and **every line inside every range is a comment line or blank**. Replacement then runs bottom-up so no earlier edit shifts a later range. The `git diff -U0` criterion (0 of 752 non-comment lines) is the independent confirmation that the pre-flight assertion held.

---

## Requirements

- **SWEEP-08 — ticked.** Fully discharged: `eeprom_28c.cpp` was swept as its own plan, both comment-blind gate mechanisms were addressed (one by construction, one by proof), and the datasheet citation of record survives.
- **SWEEP-01 / SWEEP-03 / SWEEP-05 — left Pending.** Phase-wide; complete only at plan 12. This plan's partial contribution: D-01's procedure applied to 33 of the corpus's hits with the step-3 guard exercised on three named comments (SWEEP-01); requirement/decision IDs stripped from a shipped source file, the shipped half of the asymmetry (SWEEP-03); one of the per-file byte-identity measurements, `uno` only (SWEEP-05).
- **SWEEP-07 — left Pending.** Plan 03 owns the RED-before half and plan 12 the RED-after half. This plan contributes the evidence that the swept content keeps all 8 legs green (8/8 on a clean tree carrying the swept blob).

## Issues Encountered

None beyond the two auto-fixed items above. No architectural decision was needed and no checkpoint was reached.

## Handoff Notes

- **Plan 07** starts from a firmware tree with exactly one modified path (`src/proms/eeprom_28c.cpp`). Its own byte-identity run will therefore measure the *cumulative* effect of 06+07 unless it re-baselines; the `uno` hashes above are still the reference, since a comment-only sweep leaves them unchanged.
- **Plan 12** must expect the 16 porcelain-asserting legs to be red until its commit lands, and green immediately after. The 6 host modules and 5 firmware modules are named above; the clean-clone technique (`--shared` clone + commit + `FIRESTARTER_FW_ROOT`) is available if a mid-phase green reading is ever needed again.
- **Phase 159** will remap `.planning/` citations into this file. The composite diff for `eeprom_28c.cpp` in this plan is 353 insertions / 399 deletions, a net −46 lines, concentrated in the first 250 lines — so citations into the lower two thirds of the file shift by roughly that constant while citations into the swept blocks themselves need range shrinking. Plan 05's measurement that `autojunk=False` is load-bearing was taken on **this very file** (812 vs 810 survivors), which is now the file it will actually run against.
- `/tmp/gsd-154-06-fwclone` is a throwaway oracle tree carrying a throwaway commit. It is not a ref of record and can be deleted at any time; it must never be confused with `wip/v1.33-size-reduction-survey-preserved`.

## User Setup Required

None.

---

## Self-Check: PASSED

Ran after the docs commit, before handing back. Every claim above re-verified against disk and git rather than trusted from this session's narrative.

| Check | Command | Result |
|---|---|---|
| Swept source exists | `[ -f firestarter/src/proms/eeprom_28c.cpp ]` | FOUND |
| This SUMMARY exists | `[ -f .planning/phases/154-…/154-06-SUMMARY.md ]` | FOUND |
| Docs commit exists | `git log --oneline --all \| grep 46420f71` | FOUND |
| ROADMAP row ticked | `grep -c '^- \[x\] 154-06-PLAN.md'` | 1 |
| SWEEP-08 ticked + Complete | `grep -c '^- \[x\] \*\*SWEEP-08\*\*'` / `grep -c '\| SWEEP-08 \| Phase 154 \| Complete \|'` | 1 / 1 |
| SWEEP-01/03/05 still Pending | `grep -cE '\| SWEEP-0[135] \| Phase 154 \| Pending \|'` | 3 — correct, phase-wide, plan 12 owns them |
| No commit in `firestarter` | `git -C firestarter log --oneline -1` | `8695ee5` = `FW_PRE_SHA`, unchanged (D-11) |
| Firmware tree = one path | `git -C firestarter status --short` | ` M src/proms/eeprom_28c.cpp` only |
| Preservation branch intact | `git -C firestarter branch -v` | `wip/v1.33-size-reduction-survey-preserved @ a6b46f8` present |
| No commit in `firestarter_app` | `git -C firestarter_app log --oneline -1` | `6bfa645` = `APP_PRE_SHA`, unchanged |
| Plan 03's app work intact | `git -C firestarter_app status --short \| wc -l` | 13 (2 modified + 4 new fixtures + 7 pre-existing untracked) |
| `baseline-pre-sweep.md` still uncommitted | `git ls-files --error-unmatch …` | untracked — correct per D-11 |
| Forbidden git commands | reviewed this session's commands | none of `reset --hard`, `clean`, `checkout -- <path>`, `restore`, `stash`, force-push, branch deletion was run in any repo |
