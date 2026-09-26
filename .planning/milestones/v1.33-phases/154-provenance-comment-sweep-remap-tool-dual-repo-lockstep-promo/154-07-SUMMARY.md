---
phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
plan: "07"
subsystem: firmware
tags: [avr, comment-sweep, byte-identity, sha256, blob-sha-sidecar, no-touch-region, cap-0n, line-pinned-gate]

requires:
  - phase: 154-01
    provides: "The pre-sweep byte-identity record for all THREE AVR targets (.elf/.hex sha256 + Flash:/RAM:), the clean-tree suite baselines (172/172 native, 323/0 firmware gates, 29/0 on the four F3 blob-sha gates), FW_PRE_SHA/APP_PRE_SHA, and the `cd firestarter first` pio trap"
  - phase: 154-02
    provides: "survey_provenance.py as the worklist authority and the hit oracle, D-01's triage procedure stated verbatim with its unit-of-edit rule and step-3 guard, Ruling B's four exemptions with their blob-sha pins, and the double-pin consequence on eprom_params.cpp"
  - phase: 154-03
    provides: "The 5 SWEEP-07 planted-violation legs (4 asserting RED-on-plant, 1 asserting deliberate fail-open) whose post-sweep behaviour this plan re-measures"
  - phase: 154-06
    provides: "eeprom_28c.cpp already swept (excluded from this plan's worklist), the range-keyed bottom-up block-replacement technique, the corrected `file_hits` verify-leg schema, and the prove-by-clean-clone pattern"
provides:
  - "The shipped firmware source sweep: firestarter/{src,include} 96 -> 24 provenance hits over 31 files, the residual being exactly 3 D-02-exempt CAP-0 lines + 20 + 1 in the Ruling B exempted paths"
  - "A byte-identity result stronger than the plan asked for: the COMMENT-STRIPPED text of all 32 modified src/include files is byte-identical to FW_PRE_SHA (0 differences of 32), and all THREE AVR targets' .elf AND .hex sha256 and Flash:/RAM: match plan 01's record character for character"
  - "The D-02 no-touch region proven untouched by content search rather than by line range: the pre-sweep 182-200 block is present VERBATIM at its new line 177, and the pinned _WIRE_LAYOUT_COMMENT string appears on zero added or removed diff lines"
  - "BOTH sidecars pinning eprom_params.cpp re-derived by content hash (5dffe841 -> 7817c142), proven correct positively: 29/29 on the four F3 blob-sha gates in a clean clone carrying the swept blobs committed"
  - "A previously-unrecorded gate exposure found and repaired: test_config_schema_pinned.py's _C14_CONSUMER_SITES pins exact source LINE NUMBERS, which sweep-gate-dispositions.md section B classified as `control -- safe`. It went RED; re-pinned to the live call sites with the shift recorded"
  - "88/88 on the nine comment-sensitive host gate modules and 5/5 on plan 03's SWEEP-07 legs against a clean clone carrying the swept blobs, hash-verified identical to the working tree"
affects: [154-08, 154-09, 154-10, 154-11, 154-12, 155, 156, 157, 158, 159]

tech-stack:
  added: []
  patterns:
    - "Comment-stripped equality as the diff-line-class oracle: instead of grepping the diff for non-comment lines, strip comments from every modified file at both revisions and assert byte equality -- a total statement that also absorbs trailing-comment edits on code lines"
    - "Search-based no-touch proof: extract the protected region from the pre-sweep blob, then assert that exact text is a substring of the post-sweep file. Immune to the line shift that a line-range diff would report as a false positive"
    - "Content-addressed pin re-derivation with a subset assertion on the meta key set: update the one pin, add a note key, and assert (a) every exempt pin is a literal match and (b) the pre-task meta keys are a subset of the post-task keys"
    - "Per-file oracle cadence: a 2 s cold uno rebuild after every file, so a hash divergence localises to one file instead of to a batch of 31"

key-files:
  created: []
  modified:
    - firestarter/src/** (17 files, uncommitted -- D-11)
    - firestarter/include/** (15 files, uncommitted -- D-11)
    - firestarter/tests/golden/eprom_params_citations.json
    - firestarter/tests/golden/protocol_branch_inventory.json
    - firestarter/tests/test_config_schema_pinned.py
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
    - .planning/STATE.md
    - .planning/phases/154-.../deferred-items.md

key-decisions:
  - "The worklist authority is the survey's hit table, so the strip scope is the hit line plus every D-01 token in the enclosing comment block. Mid-comment tokens in blocks carrying NO hit are out of scope and MEASURED as a residual (203 -> 152 lines) rather than swept silently or claimed absent"
  - "Four provenance hits sit on CODE lines with trailing comments, one of them SWEEP-01's named keep-example eprom_params.cpp:58 -- so the plan's own `every changed line is a comment` criterion is unsatisfiable together with its own named-keep requirement. Resolved by measuring the stronger property instead: each of the four code prefixes is byte-identical, and comment-stripped equality holds over all 32 files"
  - "The D-02 no-touch region is the CONTIGUOUS comment block 182-232, not just 182-200: the block spans the boundary. Only lines 182-200 are pinned, but the whole block was left alone, so the `(D-09)` token at old line 209 is a deliberate named residual rather than a surgical edit next to a gate fixture"
  - "test_config_schema_pinned.py's line pins were RE-PINNED, not relaxed -- the file's own established idiom, which already carried two earlier re-pins for the same class of cause. The alternative (loosening the census to a grep) would have destroyed a real gate to make a comment sweep look cleaner"
  - "No commit in `firestarter` -- D-11 reserves that sub-repo's single commit for plan 12. 35 modified paths sit in the working tree deliberately"

patterns-established:
  - "Non-vacuous zero, again: every zero in this SUMMARY is printed beside its denominator (0 of 32 files, 8 of 1201 diff lines with all 8 accounted for, 0 of 3 targets diverging)"
  - "A broken gate is repaired at its pin, in the same sub-repo commit as the change that broke it -- the same discipline Ruling B applies to a blob-sha sidecar, applied to a line-number census"
  - "Conserved-total failure accounting: 316 pass + 7 fail == 323 baseline, and every one of the 7 classified by reading its own assertion message"

requirements-completed: [SWEEP-02]

coverage:
  - id: D1
    description: "Every provenance hit in firestarter/src and firestarter/include is triaged under D-01, except the D-02 no-touch region and the four Ruling B exempted files"
    requirement: "SWEEP-01"
    verification:
      - kind: integration
        ref: "survey_provenance.py --group fw-src --group fw-include --json: 96 -> 24 hits. Residual is EXACTLY src/firestarter.cpp 3 (D-02 CAP-0, no-touch), src/proms/eprom.cpp 20 (Ruling B), include/eprom_params.h 1 (Ruling B). All 28 other hit-bearing files absent from file_hits"
        status: pass
    human_judgment: false
  - id: D2
    description: "firestarter/src/firestarter.cpp:177-195 is byte-identical to its pre-sweep state"
    requirement: "SWEEP-02"
    verification:
      - kind: integration
        ref: "`git show FW_PRE_SHA:src/firestarter.cpp | sed -n '182,200p'` (sha256 233ecb44...d97c9) is present VERBATIM as a substring of the post-sweep file, now starting at line 177 (shift -5, recorded). `git diff -U0 -- src/firestarter.cpp | grep -c 'buffer_size u16 BE'` == 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "test_cap03_ack_layout_parity.py stays green including its planted legs, so the gate is green AND still able to fail"
    requirement: "SWEEP-02"
    verification:
      - kind: integration
        ref: "Against a clean clone carrying the swept blobs committed: 12/12, both planted legs (test_planted_literal_index_is_detected, test_planted_truncated_emitted_length_is_detected) passing -- those two legs ARE the still-able-to-fail proof. Against the D-11-dirty real tree: 10 passed / 2 failed, both failures verbatim `the firmware repo's working tree is no longer clean after the planted-copy test`"
        status: pass
    human_judgment: false
  - id: D4
    description: "CAP-0N survives everywhere it appears, as cross-repo wire-protocol vocabulary"
    requirement: "SWEEP-02"
    verification:
      - kind: integration
        ref: "grep -c 'CAP-0' src/firestarter.cpp include/firestarter.h == 6 and 1, before and after -- unchanged"
        status: pass
    human_judgment: false
  - id: D5
    description: "eprom_params.cpp is swept and BOTH sidecars pinning its blob SHA are re-derived in the same working-tree state"
    requirement: "SWEEP-06"
    verification:
      - kind: integration
        ref: "`git hash-object src/proms/eprom_params.cpp` == 7817c1422d698547e5da5e0bee197b9951fb4465 == meta.blob_shas['src/proms/eprom_params.cpp'] in BOTH tests/golden/eprom_params_citations.json AND tests/golden/protocol_branch_inventory.json (was 5dffe841... in both)"
        status: pass
      - kind: integration
        ref: "In a clean clone carrying the swept blobs committed: the four F3 blob-sha gates run 29/29 (baseline 29/0)"
        status: pass
    human_judgment: false
  - id: D6
    description: "The four exempted pinned files are untouched, verified by an empty git diff on each, and their pins are unchanged literals"
    requirement: "SWEEP-06"
    verification:
      - kind: integration
        ref: "`git diff --quiet -- include/eprom_params.h src/proms/eprom.cpp test/native/avr/_shared/eprom_v131_expected.h test/native/avr/_shared/sdp_expected.h` exits 0; protocol_branch_inventory.json's eprom.cpp pin still literally 838aca47986103969be4caca3cef71a033bac069 and eprom_params_citations.json's eprom_params.h pin still literally b04c788b02c1be51200d22a876f03f4de876cd9e"
        status: pass
    human_judgment: false
  - id: D7
    description: "The uno, uno328pb and leonardo artifacts are byte-identical to the pre-sweep record"
    requirement: "SWEEP-05"
    verification:
      - kind: integration
        ref: "Cold `rm -rf .pio/build/<env> && pio run -e <env>` for all three: uno .elf 1cfa946f...31ecca / .hex be6e4ac8...05c095 / 26026 / 1575; uno328pb .elf 6650baec...d98d8c / .hex 7b86c1aa...20ebba / 26074 / 1581; leonardo .elf fcca68e9...2d7aef / .hex 2b9ad44e...b0ee88 / 28170 / 2016. All six hashes and all six size figures match plan 01's record character for character"
        status: pass
    human_judgment: false
  - id: D8
    description: "No executable-code change is hidden inside the comment sweep"
    requirement: "SWEEP-05"
    verification:
      - kind: integration
        ref: "Comment-stripped text of every modified src/include file compared against FW_PRE_SHA: 32 files compared, 0 differences. Independent second measurement: `git diff -U0 -- src include` filtered non-comment count == 8 of 1201, and all 8 are the +/- halves of the FOUR trailing-comment-only edits on code lines, each with its code prefix proven byte-identical"
        status: pass
    human_judgment: false
  - id: D9
    description: "The native and firmware gate suites are no worse than plan 01's baseline, with every failure named and attributed"
    verification:
      - kind: integration
        ref: "pio test -e native -> 172 test cases: 172 succeeded (baseline 172/172). python3 -m pytest tests/ -q -> 316 passed / 7 failed; 316+7 == 323 baseline. The 7: 5 porcelain-asserting planted legs (verbatim `the firmware repo's working tree is no longer clean after the planted-* test`, the identical set plan 06 recorded) + 2 blob-sha gates whose message reads `recorded=7817c142... observed=5dffe841...` -- i.e. the sidecar is right and HEAD is stale, which is precisely the uncommitted state D-11 mandates"
        status: pass
    human_judgment: false
  - id: D10
    description: "Plan 03's five SWEEP-07 legs keep their semantics after the sweep"
    requirement: "SWEEP-07"
    verification:
      - kind: integration
        ref: "In the clean clone: all 5 named legs pass (4 asserting RED-on-plant, 1 asserting the deliberate fail-open), and the anchoring leg test_extracted_slice_is_anchored_on_the_real_declaration passes against the REAL swept eeprom_28c.cpp. Against the dirty real tree all 5 fail exclusively on the trailing _git_porcelain assertion"
        status: pass
    human_judgment: false
  - id: D11
    description: "The three keep-examples in this plan's scope, plus task 2's, land on `keep, reflowed` with their surviving sentence shown"
    requirement: "SWEEP-01"
    verification:
      - kind: manual
        ref: "All four surviving sentences quoted in full below (uno_rurp_shield.cpp:106, flash_5v_page.cpp:103, json_parser.c:282, eprom_params.cpp:58); the reviewable artifact is `git -C firestarter diff -- src include`"
        status: pass
    human_judgment: true
    rationale: "Whether the step-3 guard was honoured -- whether each surviving sentence still stands alone and still carries its full force -- is a reader judgment. The text is quoted rather than greped for so a reviewer need not reconstruct it from a 1201-line diff"

metrics:
  duration: ~70min
  completed: 2026-08-23
  tasks: 3
  files_changed: 39

status: complete
---

# Phase 154 Plan 07: The Shipped Firmware Sweep (SWEEP-02 discharged) Summary

**Swept `firestarter/{src,include}` from 96 provenance hits to 24 across 31 files, with the residual being exactly the 3 D-02-exempt `CAP-0` lines plus the 21 in Ruling B's exempted paths; proved the no-touch region byte-identical by content search rather than line range; re-derived BOTH sidecars pinning `eprom_params.cpp` and proved them right positively (29/29 in a clean clone); and measured all THREE AVR targets' `.elf` AND `.hex` sha256 and `Flash:`/`RAM:` identical to plan 01's record — while finding and repairing a real gate exposure the dispositions table had classified as safe.**

---

## What was measured, before and after

Every number below carries the command that produced it.

### Hit counts — the primary oracle

```bash
cd /workspaces && python3 .planning/v1.33/tools/survey_provenance.py \
  /workspaces/firestarter /workspaces/firestarter_app --json --group fw-src --group fw-include
```

| Group | Before | After |
|---|---|---|
| `fw-src` | 69 hits / 17 files | **25 → 23** hits / 2 files |
| `fw-include` | 27 hits / 16 files | **1** hit / 1 file |
| **combined** | **96 / 33** | **24 / 3** |

The `--json` output after both tasks, pasted so the residual is visible and attributed rather than merely asserted zero:

```json
{
  "fw-include": { "candidate_files": 38, "file_hits": { "include/eprom_params.h": 1 },
                  "files": 1, "hits": 1 },
  "fw-src":     { "candidate_files": 24, "file_hits": { "src/firestarter.cpp": 3,
                                                        "src/proms/eprom.cpp": 20 },
                  "files": 2, "hits": 23 },
  "summary":    { "candidate_files": 62, "groups_selected": ["fw-src","fw-include"], "hits": 24 }
}
```

**Every one of the 24 is accounted for, by name:**

| Residual | Count | Why it survives |
|---|---|---|
| `src/firestarter.cpp` | 3 | The `CAP-0` lines at old 182/193/200 — **D-02-exempt vocabulary inside the no-touch region.** Not swept by design. |
| `src/proms/eprom.cpp` | 20 | **Ruling B exempted** — blob-sha-pinned by `protocol_branch_inventory.json`, no regeneration tool. |
| `include/eprom_params.h` | 1 | **Ruling B exempted** — blob-sha-pinned by `eprom_params_citations.json`. |

The tool omits zero-hit files from `file_hits` rather than emitting a `0` row, so *absent* **is** the zero. Both readings are asserted: the 28 other hit-bearing files are gone from `file_hits`, and the combined total moved 96 → 24 (−72, which is exactly task 1's 70 plus task 2's 2 and nothing else).

`src/proms/eeprom_28c.cpp` was already at 0 from plan 06 and was **not touched** by this plan.

### Byte-identity — SWEEP-05, all three AVR targets (Ruling E: hash pair **and** size pair)

```bash
cd /workspaces/firestarter
for e in uno uno328pb leonardo; do
  rm -rf .pio/build/$e && pio run -e $e
  sha256sum .pio/build/$e/firestarter_$e.elf .pio/build/$e/firestarter_$e.hex
done
```

| env | `.elf` sha256 (post-sweep, measured) | matches plan 01? | `.hex` sha256 | matches? | Flash: | RAM: |
|---|---|---|---|---|---|---|
| uno | `1cfa946f486e041ce5264fc75742ee11e2b437041eaee178ab4d164cbb31ecca` | **yes** | `be6e4ac80a70e251e2c263beb4109f9f7f9852a034b1064a5dbc8dbbcf05c095` | **yes** | 26026 / 32768 (79.4%) | 1575 / 2048 (76.9%) |
| uno328pb | `6650baecf09ca0fb5ffbf7a377e0528b021568c1ab7f9c4afdafc4254ed98d8c` | **yes** | `7b86c1aac5642b968bd9604bde249b7d68643ebe135f0d05690e56e43e20ebba` | **yes** | 26074 / 32768 (79.6%) | 1581 / 2048 (77.2%) |
| leonardo | `fcca68e967798a1a133149fa5736dd0d5dd04384d5cf02feeff861f8672d7aef` | **yes** | `2b9ad44e23dd6dc88e76a5aeb9105050f56c84d470a14b9a9d2597feffb0ee88` | **yes** | 28170 / 32768 (86.0%) | 2016 / 2560 (78.8%) |

**Six hashes and six size figures, all identical, character for character.** SWEEP-05's revert rule never fired, so nothing had to be explained. The `.hex` is recorded as corroboration only (per Ruling E, `avr-objcopy -O ihex` drops non-loadable sections); the `.elf` is the primary.

The oracle was also run **per file**, 31 times, at ~2 s per cold `uno` rebuild. Every intermediate run matched. That is why a divergence would have localised to one file instead of to a batch — it never diverged, so the cadence bought insurance rather than a bisect.

**Coverage caveat, stated rather than left implicit:** the three AVR builds do not compile `include/boards/py32f071_*.h` or `include/rurp_pinmap_guard.h`'s py32 arm. Those three files' edits are covered by the comment-stripped equality measurement below, not by a compiled artifact — this project's only ARM build is FetchContent-only and cannot run in this devcontainer.

### "No code line changed" — measured two independent ways

The plan's stated criterion is a `git diff -U0` line-class grep. Run as written:

```bash
git -C firestarter diff -U0 -- src include | grep -E '^[+-]' | grep -vE '^[+-]{3}' \
  | grep -vcE '^[+-][[:space:]]*(//|\*|/\*|$)'      # 8
git -C firestarter diff -U0 -- src include | grep -E '^[+-]' | grep -vcE '^[+-]{3}'  # 1201
git -C firestarter diff --shortstat -- src include
# 32 files changed, 557 insertions(+), 644 deletions(-)
```

**8 of 1201.** Not zero — and the eight are not a defect, they are the plan's own requirement colliding with its own criterion. See the deviation section: four provenance hits sit on **code lines with trailing comments**, and one of them is SWEEP-01's *named* keep-example `eprom_params.cpp:58`, which the plan explicitly requires be swept. Each of the 8 lines is one half of one of those four edits:

```
- LOG_OK_ID_U16(MSG_OK_READY, (uint16_t)DATA_BUFFER_SIZE);  // D-04: was legacy ack; semantics ≈ …
+ LOG_OK_ID_U16(MSG_OK_READY, (uint16_t)DATA_BUFFER_SIZE);  // semantics ≈ …          (×2, dev_tools.cpp)
- return NULL; /* D-05: fail closed, zero hardware side effects -- never &EPROM_PARAMS[0] */
+ return NULL; /* Fail closed: a null pointer with zero hardware side effects, never &EPROM_PARAMS[0]. */
-             mask |= CTRL_VPP_VPE_DROP_ENABLE;  // D-01 / D-02
+             mask |= CTRL_VPP_VPE_DROP_ENABLE;
```

So the **stronger** property was measured instead, and it is a total statement rather than a filtered one. For every modified file under `src`/`include`, strip all comments at `FW_PRE_SHA` and in the working tree, then compare:

| Measurement | Result |
|---|---|
| files compared | **32** |
| comment-stripped **differences** | **0** |
| the four trailing-comment code lines: code prefix before the comment opener, byte-identical? | **4 of 4 IDENTICAL** |

```
src/dev_tools.cpp:108->107        IDENTICAL: '    LOG_OK_ID_U16(MSG_OK_READY, (uint16_t)DATA_BUFFER_SIZE);'
src/dev_tools.cpp:154->153        IDENTICAL: '    LOG_OK_ID_U16(MSG_OK_READY, (uint16_t)DATA_BUFFER_SIZE);'
src/proms/memory.cpp:217->216     IDENTICAL: '            mask |= CTRL_VPP_VPE_DROP_ENABLE;'
src/proms/eprom_params.cpp:58->57 IDENTICAL: '    return NULL;'
```

Comment-stripped equality over 32 files subsumes the grep: it would catch a code change on a comment line, a code change on a trailing-comment line, and a code change anywhere else, and it reports **zero**. The three-target `.elf` equality is the independent third confirmation.

---

## The D-02 no-touch region — proven untouched, by search not by line range

The plan anticipated that the region's line numbers could shift and asked for content comparison in that case. They did shift, by exactly −5.

```bash
git show 8695ee52c27a4bee4387c5c489afd5f3d7275e8a:src/firestarter.cpp | sed -n '182,200p' \
  > /tmp/.../notouch_pre.txt          # sha256 233ecb440a35ccd003cdd375c72d7c56e92a7eee0a33dcd9ff04f9ef125d97c9
python3 -c "…; print(pre in post)"    # True — present VERBATIM, now starting at line 177
git -C firestarter diff -U0 -- src/firestarter.cpp | grep -c 'buffer_size u16 BE'   # 0
```

| Check | Result |
|---|---|
| pre-sweep lines 182–200 present verbatim in the post-sweep file | **True** |
| new starting line | **177** (shift −5, recorded) |
| pinned `_WIRE_LAYOUT_COMMENT` string on any **added or removed** diff line | **0** |
| `grep -c 'CAP-0'` in `src/firestarter.cpp` / `include/firestarter.h` | **6 / 1** before, **6 / 1** after |

**A boundary correction worth recording.** D-02 names `182-200` as the no-touch region, but the *contiguous comment block* it sits in runs **182–232** — it continues past 200 with the CAP-03 rationale, the padding note and PR #49's two preserved facts. Only 182–200 is pinned (verified: `test_cap03_ack_layout_parity.py` reads raw text for `_WIRE_LAYOUT_COMMENT` alone, at `:449`; everything else in that module goes through `_strip_comments`). The whole 182–232 block was nevertheless left alone rather than surgically edited above and below the pinned lines. **Consequence, recorded not hidden:** one `(D-09)` token survives at old line 209 (`// The advertised budget is already PADDED by the firmware (D-09): only`). It is not a survey hit — the token is mid-comment — and editing a line inside the block that carries a gate fixture, to remove a token no oracle asks about, is a bad trade. Named residual, same shape as plan 06's `(D-16)`.

`test_cap03_ack_layout_parity.py`, green **and** shown still able to fail:

| Tree | Result |
|---|---|
| clean clone carrying the swept blobs committed | **12 passed** — including both planted legs, which *are* the still-able-to-fail proof |
| the real, D-11-dirty tree | 10 passed / 2 failed, both verbatim `the firmware repo's working tree is no longer clean after the planted-copy test -- it is a read-only input to this phase` |

---

## The four keep-examples, quoted in full for review

SWEEP-01 requires all five *named* keep-examples be **shown** to land on "keep, reflowed". Four are in this plan's scope (`database.py:581-620` is plan 09's). Here is the surviving text, so a reviewer does not have to reconstruct it from a 1201-line diff.

### 1. `src/boards/uno_rurp_shield.cpp:106` → now `:103-105`

```c
// Uno strong override of rurp_log_id. The com_mode gate is critical:
// emitting on the wire while PORTD is repurposed as the data bus would
// corrupt the programming pulse.
```

`Phase 6 — ` and the `(per CONTEXT §"Specific Ideas")` pointer are gone. The invariant — *why* the gate is critical — is intact. The two tombstone lines that followed it (`Phase 8 Plan 07: debug_msg_buffer path removed; …`) were deleted under step 2; their only forward-looking fact is stated by the block at the file's end, which was itself collapsed from a tombstone into the durable statement `// Structured debug emit routes through the main serial port as id-frames (LOG_DEBUG_ID_SUB* in logging_id.h) rather than through a separate soft-serial debug channel.`

### 2. `src/proms/flash_5v_page.cpp:103` → now `:100-102`

```c
    // An erase-on-write block gated this way, inside a protocol's
    // write-init, is a pattern that must NOT be copied into
    // eeprom28c_write_init.
```

`D-153-05:` stripped; the prohibition kept, reworded from `an executor must NOT copy` (GSD vocabulary) to `must NOT be copied` so it reads as a standing rule about the code rather than an instruction to a workflow.

### 3. `src/json_parser.c:282` → still `:92`, C `/* */` delimiter form preserved

```c
    /* page_size resets to 0 exactly like chip_id above. handle is a
     * single file-scope global with no per-command memset, and page-size is
     * emit-when-present, so without this reset a 128 parsed for one chip
     * would persist into the next command and "absent means 64" becomes
     * false in practice -- the exact overrun this reset exists to prevent.
     * The two read-timing knobs (read_settling_us, read_strobe_us) are
     * deliberately NOT in this reset block: that is a pre-existing latent
     * instance of the same defect, filed as a todo, so their absence here is
     * not an oversight. */
```

This is the explicit step-3 keep: it is the only written statement of the reset invariant that prevents the `phase-44-read-timing-knobs-missing-json-parse-reset` bug class. `D-05`, `PGSZ-02`, `Phase 44` and `plan 07` are gone; **both** halves survive — the invariant itself, and the honest statement that the read-timing knobs are a known latent instance of the same defect rather than an oversight. The two clauses that referred to their labels were reworded so each stands on its own (`the exact overrun PGSZ-02 exists to prevent` → `the exact overrun this reset exists to prevent`).

### 4. `src/proms/eprom_params.cpp:58` → now `:57` (task 2)

```c
    return NULL; /* Fail closed: a null pointer with zero hardware side effects, never &EPROM_PARAMS[0]. */
```

`D-05:` stripped. Both load-bearing facts survive and now stand alone: the accessor returns a **null pointer with zero hardware side effects**, and it **never** returns `&EPROM_PARAMS[0]` — i.e. it never silently substitutes the first table row for an unrecognised protocol. Delivering this sentence is exactly why Ruling B chose to regenerate this file's sidecars rather than exempt it, so it is the one keep-example whose survival the ruling was written for.

---

## Task 2 — both sidecars re-derived, and the two facts that bound the regeneration

### The re-derivation

```bash
cd /workspaces/firestarter && git hash-object src/proms/eprom_params.cpp
# 7817c1422d698547e5da5e0bee197b9951fb4465
```

| Sidecar | `src/proms/eprom_params.cpp` pin | other pin |
|---|---|---|
| `tests/golden/eprom_params_citations.json` | `5dffe841…ae22da` → **`7817c142…fb4465`** | `include/eprom_params.h` = `b04c788b02c1be51200d22a876f03f4de876cd9e`, **unchanged (literal match asserted)** |
| `tests/golden/protocol_branch_inventory.json` | `5dffe841…ae22da` → **`7817c142…fb4465`** | `src/proms/eprom.cpp` = `838aca47986103969be4caca3cef71a033bac069`, **unchanged (literal match asserted)** |

This is the double-pin Ruling B does not name and plan 02 recorded. Updating only the first would have left `test_protocol_branch_inventory.py::test_blob_shas_match_the_recorded_inventory` RED for a reason a reader would misdiagnose as sweep damage.

Both gates' failure messages instruct re-deriving rather than hand-editing, and that is what happened: a blob SHA is content-addressed, so `git hash-object` on the swept working tree is exactly what `git rev-parse HEAD:<path>` will report once plan 12's commit lands. **Proven, not argued** — in a clean clone carrying the swept blobs committed, the four F3 blob-sha gates run **29/29**, matching plan 01's 29/0 baseline.

A `meta.sweep_note` key was added to each, naming SWEEP-01 and SWEEP-06 (not a phase or plan label) and recording that only comment text changed. Neither gate asserts an exact `meta` key set (verified by reading both modules: they iterate `meta["blob_shas"]`, and the only other `meta[...]` reads are `reasoned_prefix` and `row_chip_counts`). Both files round-trip byte-identically through `json.dumps(indent=2, ensure_ascii=False) + "\n"`, verified before writing, so the rewrite introduced no formatting churn. Assertions run at write time: every exempt pin a literal match, the pre-task `meta` key set a **subset** of the post-task set, and the added key set exactly `{"sweep_note"}`. `meta.recorded_at_head` was not touched.

### The two verified facts, restated so a reviewer need not re-derive them

1. **`eprom_params_citations.json`'s `cells` carry no line-number field.** Measured: `cells[0]` keys are exactly `['basis','column','notes','reasoned_from','row','value']`, and a scan of **every** cell for any key containing `line` returns the empty set. So no cell can be invalidated by a line shift.
2. **`protocol_branch_inventory.json`'s line-bearing `sites` array is extracted from `src/proms/eprom.cpp` only** (`meta.sources` = `['src/proms/eprom.cpp','src/proms/eprom_params.cpp']`; `sites[0]` keys are `class/keyed_on/line/predicate/reason/tier`), and `eprom.cpp` is exempt and unedited. Its separate `params_table` scan of `eprom_params.cpp` is `{"keys": ["0x07","0x08","0x0B"], "switch_statements": 0, "key_comparisons": 1}` — a structural count produced **after** `_strip_comments_and_literals()`, so it is immune to a comment-only edit by construction.

**Therefore the only thing this sweep can invalidate in either sidecar is the one blob SHA** — and it did, and it was re-derived.

**Expected-RED-until-plan-12, recorded here explicitly so plan 12 does not diagnose it as a defect.** Both gates read `git rev-parse HEAD:<path>`, and this plan commits nothing in `firestarter`. Actual pre-commit result observed:

```
AssertionError: src/proms/eprom_params.cpp blob SHA changed --
  recorded='7817c1422d698547e5da5e0bee197b9951fb4465'
  observed='5dffe841aeb7013f9f53e9991a6248b203ae22da'
```

The **recorded** value is the new, correct one and the **observed** value is what `HEAD` still carries. That direction is the signature of an uncommitted-but-correct sidecar, not of a wrong one. Plan 12's commit flips both green — already demonstrated, in the clone.

---

## Gate results — and the honest accounting of every red leg

### Green outright

| Suite | Command | Baseline (plan 01) | This session |
|---|---|---|---|
| native | `pio test -e native` | 172 / 172 | **172 test cases: 172 succeeded** |

### Firmware gate suite — totals conserved, every failure classified

```bash
cd /workspaces/firestarter && python3 -m pytest tests/ -q      # 316 passed / 7 failed
```

**316 + 7 = 323 = plan 01's baseline total**, so nothing was lost to a collection change.

```bash
python3 -m pytest tests/ -q 2>&1 | grep -E "^E +AssertionError" | sort | uniq -c
#  1 ... src/proms/eprom_params.cpp blob SHA changed -- recorded='7817c142…' observed='5dffe841…'
#  1 ... src/proms/eprom_params.cpp blob SHA changed -- recorded=7817c142…  observed=5dffe841…
#  1 ... the firmware repo's working tree is no longer clean after the planted-copy test
#  1 ... the firmware repo's working tree is no longer clean after the planted-delete-and-duplicate test.
#  1 ... the firmware repo's working tree is no longer clean after the planted-empty-root test.
#  1 ... the firmware repo's working tree is no longer clean after the planted-rename test.
#  1 ... the firmware repo's working tree is no longer clean after the planted-unclassifiable-entry test.
```

| Count | Cause | Disposition |
|---|---|---|
| 5 | `_git_porcelain` on the D-11-mandated dirty tree — `test_flash_path_record_sync`, `test_requirement_case_mapping_v131` ×2, `test_trace_segment_exhaustiveness_v131` ×2. **The identical set plan 06 recorded.** | Mandated state, not a regression |
| 2 | The two blob-sha gates read `HEAD:<path>`; this plan's edits are uncommitted; plan 12's commit resolves it | Expected, direction verified above |

**Zero content failures.**

### The positive proof, non-destructively (plan 06's technique, reused)

```bash
git clone --shared --branch gsd/v1.33-source-hygiene-firmware-size-reduction \
  /workspaces/firestarter /tmp/gsd-154-07-fwclone
# copy every modified path in, then commit inside the clone
# clone porcelain: ''   clone HEAD: 97420d8
```

Blob equality between the parent's working tree and the clone's **committed** content, so the clone is provably testing the same bytes:

| path | working tree | clone `HEAD:` | |
|---|---|---|---|
| `src/proms/eprom_params.cpp` | `7817c1422d69` | `7817c1422d69` | MATCH |
| `src/firestarter.cpp` | `7d1ccf1199ed` | `7d1ccf1199ed` | MATCH |
| `include/rurp_shield.h` | `4a16c5c0155c` | `4a16c5c0155c` | MATCH |
| `tests/golden/eprom_params_citations.json` | `945ba3de80f7` | `945ba3de80f7` | MATCH |
| `tests/golden/protocol_branch_inventory.json` | `83e0c752bb93` | `83e0c752bb93` | MATCH |
| `tests/test_config_schema_pinned.py` | `a8607a93853b` | `a8607a93853b` | MATCH |

| Run, in the clone | Result |
|---|---|
| the four F3 blob-sha gates | **29 passed** |
| full firmware suite | **290 passed / 1 failed / 32 skipped** (290+1+32 = 323) |
| nine comment-sensitive host modules, `FIRESTARTER_FW_ROOT=<clone>` | **88 passed** |
| plan 03's five SWEEP-07 legs, named individually | **5 passed** |

The single clone failure is `test_checker_convention.py::test_scope_is_firmware_only`, and its own message names the cause: `At index 0 diff: 'gsd-154-07-fwclone' != 'firestarter'` — it asserts the repo **directory name**. Plan 06 already controlled this against a *pristine* clone with no sweep applied and found it fails identically; the message here is self-evidently a path assertion, not a content one. Not attributed to this edit.

### Host gates against the real tree — 11 failures, all one cause

```bash
cd /workspaces/firestarter_app
FIRESTARTER_FW_ROOT=/workspaces/firestarter /tmp/gsd-154-venv311/bin/python -m pytest \
  tests/test_sdp_table_parity.py tests/test_dispatch_mirror.py \
  tests/test_cap03_ack_layout_parity.py tests/test_json_key_parity.py \
  tests/test_revision_constants_parity.py tests/test_check_no_log_in_sdp_window.py \
  tests/test_check_is_memory_cmd_no_ifdef.py tests/test_py32_flash_map_host.py \
  tests/test_py32_asset_name_host.py -o addopts="" -q
# 11 failed, 77 passed
```

Classified by reading the assertions, not by inference: **2** × `the firmware repo's working tree is no longer clean after the planted-copy test -- it is a read-only input to this phase` and **9** × `the sibling firmware repo is not clean after this planted-violation run -- the plant must never write into the real repo`. The identical 2+9 split plan 06 measured. Against the clone the same nine modules run **88/88**.

### Plan 03's five SWEEP-07 legs — semantics intact

Plan 03's own record reads "3 new legs in `test_sdp_table_parity.py` … module now 8/8 passing" and "2 new legs in `test_dispatch_mirror.py` (`test_planted_missing_hex_is_detected` RED, `test_planted_comment_only_hex_is_NOT_detected` deliberately GREEN) — module now 4/4 passing". So **4-RED / 1-GREEN describes what the legs assert, and all five legs PASS.** Post-sweep, in the clone:

| Leg | Asserts | Result |
|---|---|---|
| `test_planted_comment_misanchor_is_detected` | gate goes RED on the plant | **pass** |
| `test_planted_comment_brace_break_is_detected` | gate goes RED on the plant | **pass** |
| `test_extracted_slice_is_anchored_on_the_real_declaration` | the live extraction anchors inside the **real, swept** `eeprom_28c.cpp` | **pass** |
| `test_planted_missing_hex_is_detected` | gate goes RED on the plant | **pass** |
| `test_planted_comment_only_hex_is_NOT_detected` | gate deliberately does **not** detect (the recorded fail-open) | **pass** |

4-RED / 1-GREEN, unchanged. The anchoring leg is the one that could legitimately have changed behaviour as a result of this milestone's sweeps, and it passes against the real swept file.

---

## Triage scope, stated so it is reviewable

**The worklist is the survey's hit table**, exactly as the plan directs (`survey_provenance.py --group fw-src --group fw-include`). 30 files edited in task 1 (70 hits), 1 in task 2 (2 hits).

Within each edited comment block, **every** D-01-class token was stripped, not only the one the regex anchored on — §2's unit-of-edit rule. The strip set used, extended by *shape* from D-01's list (recorded so a reviewer can check the boundary): `Phase N`, `Plan N[-NN]`, `Task N`, `<NNN>-CONTEXT.md` and sibling `.planning/` document references (`151-DESIGN.md`, `140-RESEARCH.md`, `51-04-PLAN.md`, `.planning/v1.7-SHIELD-REVS.md`), requirement IDs (`LOCK-02`, `PGSZ-01/02`, `ERASE-02`, `HOST-01/02`, `TABLE-01/02/05`, `MERGE-04`, `CFG-03/04`, `VPP-01/02`, `LFW-05`, `LMIG-01`, `FRAME-03`, `EVEN-01`), decision IDs (`D-NN`, `D-153-05`), correction IDs (`C-16`, `CR-01/02`, `C-12`), threat IDs (`T-50-01`, `T-51-01/02`, `T-54-01`, `T-44-01`), finding/assumption labels (`BF-1/2/3`, `F-140-05`, `RCA-01`, `Assumption A4`, `Pitfall N`, `SC#1`/`SC1 win`, `OD-3`, `Q4`).

**Kept, because they are not GSD provenance:**

- `CAP-0N` — D-02-exempt cross-repo wire-protocol vocabulary. The both-repos exemption test was applied before stripping any token not on D-01's list; `CAP-0N` is the only token in this corpus that passes it. Counts unchanged (6 / 1).
- Real in-repo paths and identifiers: `src/proms/eprom.cpp`, `flash_utils.h`, `eeprom28c_write_init`, `test_vpp_eprom_v131.cpp`'s two named cases, `scripts/check_orphan_provisional.py`, `doc/SHIELD-REVISIONS.md`, `tests/golden/eprom_params_citations.json`, `tests/test_vpp_seam_manual_on_every_board.py`.
- Datasheet and part references: `Winbond W27C512`, `ST M27C512`, `Microchip 27C512A`, `W29C040`.
- External refs: `PR #49`, `PR #55`, the commit shas inside the no-touch region.
- Standards refs: `V5`, `ADR §4.4`.
- Bench dates that are measurements, not labels: `bench measurement (2026-05-26)`, `amended 2026-08-11, operator-confirmed`.

**Tombstones deleted outright under step 2** (each describing code that is not there): the four `Phase 9: deleted the …SERIAL_DEBUG…` blocks across `leonardo_rurp_shield.cpp`, `uno_rurp_shield.cpp` (×2 sites), `rurp_serial_utils.cpp` (×2), `include/rurp_serial_utils.h` and `include/rurp_shield.h`; `firestarter.cpp`'s `Phase 9: deleted the SERIAL_DEBUG bootstrap call`; and `eprom_params.cpp`'s `Unreferenced by src/ this phase (D-10) -- Phase 141 wires this table into configure_eprom` bookkeeping paragraph, which describes a state that has since changed. Where a tombstone carried one durable forward-looking fact, that fact was **kept and reworded** rather than lost — the `uno_rurp_shield.cpp` debug-channel block and `firestarter.cpp`'s `'{'-peek loop` note are the two instances.

### Named residual, measured rather than hidden

`survey_provenance.py`'s regex requires the token to sit **immediately after** a comment opener, so a token deeper inside a comment line is not a hit and no worklist entry anchors it. Measured with a token-anywhere scan restricted to comment lines:

| When | Mid-comment-only lines in `firestarter/{src,include}` |
|---|---|
| before this plan | **203** |
| after this plan | **152** |

51 went as a side-effect of §2's block-wide rule. Of the 152 survivors, 28 are in the exempt `eprom.cpp` and 7 in the exempt `eprom_params.h`, leaving **117** in files now at 0 *hits*. The largest concentrations are long structural file-header blocks whose section headings *are* decision IDs (`include/rurp_config_storage.h`'s `WHY EXACTLY TWO FUNCTIONS (D-06):`, 12 lines) and one file with **zero** survey hits at all (`include/rurp_hw_rev_utils.h`, 9 lines). Filed as **deferred item D5** with the reasoning: it is a second, uniform mechanical pass that should be decided once for both repos, and the host repo will carry the same population.

---

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — Bug] `test_config_schema_pinned.py` pins exact source LINE NUMBERS; the sweep broke it**

- **Found during:** Task 3, first run of the firmware gate suite (8 failed, one more than plan 06's 5 + this plan's expected 2).
- **Issue:** `test_the_seven_consumers_call_only_the_public_api` went RED with five named violations (`src/firestarter.cpp:38 does not call rurp_load_config(); observed line: '#endif'`, …). Cause: `_C14_CONSUMER_SITES` is a 9-tuple of `(path, exact 1-indexed line, function name)` asserted by `_consumer_census_violations`, and this sweep's deletions moved five of those lines. **`sweep-gate-dispositions.md` §B row 6 dispositioned this module as `control` — verified safe on the basis that "its declared-field extraction targets struct syntax, not comment text".** That is true of the struct legs; the row does not mention the second, line-pinned mechanism. A genuine unrecorded exposure, not a mis-read.
- **Fix:** re-pinned to the live call sites — `src/firestarter.cpp` 41→38, 119→115, 125→121; `src/hardware_operations.cpp` 107→106, 119→118; the other four sites are in files the sweep never touched and are unchanged. Re-derived by locating each call (`grep -nE '\brurp_(load|get|save)_config\s*\('`), never by relaxing the pin. The shift and its cause are recorded in the tuple's own comment, which is the file's established idiom — it already carried two earlier re-pins for exactly this class of cause (+1 from an added `#include`, +15 from a widened comment block, both recorded there). **Module back to 17/17**, and the pin's non-vacuity needs no separate demonstration: it *had just failed for real*.
- **Files modified:** `firestarter/tests/test_config_schema_pinned.py` (uncommitted, lands in plan 12's single firmware commit).
- **Scope note:** `firestarter/tests/*.py` is outside the sweep's globs (corpus baseline §7) and this edit is not a sweep — it is the repair of a pin whose subject legitimately changed, the same discipline Ruling B applies to a blob-sha sidecar. The existing `Phase 143 Plan 03` / `Phase 151 Plan 03` labels in that comment were **left intact** per D-03 (IDs are retained in test files) and D-04 (test files get the narrow treatment).
- **Blast-radius check:** a repo-wide grep for executable line-number pins over swept firmware paths finds this is the **only** one in either repo. `firestarter_app`'s two `src/firestarter.cpp:187-189` / `include/rurp_shield.h:25-31` references are **docstring prose**, not assertions — confirmed by the host modules running 88/88 against the swept content. Filed as **deferred item D6**, because §B's "control" verdict will mislead Phases 155–158, all of which shift lines.

**2. [Rule 3 — Blocking] The plan's task-1 diff-line-class criterion is unsatisfiable together with its own SWEEP-01 named-keep requirement**

- **Found during:** Task 1, enumerating the worklist.
- **Issue:** the criterion is `every added and removed diff line under src and include is a comment line or blank: the git diff -U0 filtered count == 0`. But **four** of the in-scope provenance hits sit on **code lines with trailing comments** — `dev_tools.cpp:108`, `dev_tools.cpp:154`, `memory.cpp:217`, and `eprom_params.cpp:58`. The last is SWEEP-01's *named* keep-example, which the plan's task 2 explicitly requires be swept and its sentence kept. Any edit to a trailing comment necessarily rewrites a line that does not start with `//`, so the criterion and the requirement cannot both hold. (Plan 06 hit the mirror image of this and chose to leave its `(D-16)` — but that token was **not a survey hit**, so leaving it cost nothing; these four **are** hits, and leaving them would fail the primary oracle.)
- **Fix:** all four edited, and the criterion replaced by two strictly stronger measurements rather than quietly reinterpreted: (a) comment-stripped text of all 32 modified files byte-identical to `FW_PRE_SHA` — **0 differences of 32**; (b) each of the four code prefixes before the comment opener byte-identical — **4 of 4**. The plan's own grep is still reported, at its literal value **8 of 1201**, with all eight lines printed and attributed. Nothing is claimed to be zero that is not.
- **Files modified:** none beyond the four sweeps themselves (verification method only).

**3. [Rule 2 — Missing critical] The three py32-only headers are covered by no compiled artifact**

- **Found during:** Task 3, reading the byte-identity result.
- **Issue:** `include/boards/py32f071_pinmap_guard.h`, `include/boards/py32f071_rurp_shield.h` and `include/rurp_pinmap_guard.h`'s py32 arm are not compiled by `uno`, `uno328pb` or `leonardo`, and this devcontainer cannot build the ARM target (FetchContent-only SDK). Reporting "all three targets byte-identical" without saying so would imply coverage that does not exist.
- **Fix:** stated as an explicit coverage caveat above, with the comment-stripped-equality measurement named as what actually covers those three files. No code change.

### Deliberate deviations

**4. No commit in `firestarter` — as instructed.** D-11 reserves that sub-repo's single commit for plan 12. 35 modified paths (32 under `src`/`include`, 2 goldens, 1 test module) sit in the working tree. Consequence, stated plainly: the porcelain-asserting legs and the two blob-sha gates stay red until plan 12 commits, and that is the mandated state.

**5. `.planning/v1.33/baseline-pre-sweep.md` read and NOT committed**, per plan 01 §7 and D-11. Still uncommitted on disk.

**6. `roadmap.update-plan-progress` deliberately not run.** v1.33's `ROADMAP.md` and `REQUIREMENTS.md` are hand-authored and the GSD verbs reformat whole files. Both were edited by surgical hand replacement with a uniqueness assertion on each `old` string, as plans 01–06 did.

**7. `src/proms/eeprom_28c.cpp` not touched.** Plan 06's swept content passes through this plan's working tree and its measurements unchanged; its blob is byte-identical to plan 06's (`11d4ed50…`, unchanged in `git diff --numstat`: still `353 399`).

---

## Method note — how the edits were applied

Plan 06's technique, reused: `(start_line, end_line, new_text)` triples with two pre-flight assertions — the ranges are disjoint and ascending, and **every line inside every range is a comment line or blank** — then replacement bottom-up so no earlier edit shifts a later range. **128 block replacements across 31 files.** No `old` string was ever retyped, so no whitespace mismatch could silently skip a block.

The four trailing-comment code lines could not go through that applier (its pre-flight would reject them, correctly), so they used a separate one-line helper that locates the comment opener, **asserts the code prefix is non-empty**, and rewrites only the comment — printing the old line, the new line and the preserved prefix for each. That is why the code-prefix identity table above is a measurement taken at edit time and re-verified afterwards against `FW_PRE_SHA`, rather than an assertion.

---

## Requirements

- **SWEEP-02 — ticked.** Fully discharged: `CAP-0N` exempt everywhere (counts unchanged, 6 / 1), the both-repos exemption test applied before stripping any token not on D-01's list, `src/firestarter.cpp:177-195` proven byte-identical by content search, and `test_cap03_ack_layout_parity.py` green **and** shown still able to fail (12/12 in the clone, both planted legs included). **Standing obligation this tick carries forward, stated so the tick is not read as wider than it is:** plans 09–11 sweep host source where `CAP-0N` appears in shipped code and 13 test modules, and must retain it. That is a restatement of the now-recorded rule, not an undischarged half.
- **SWEEP-01 / SWEEP-03 / SWEEP-05 / SWEEP-06 — left Pending.** Phase-wide; complete only at plan 12. This plan's partials: D-01 applied to 72 hits with the step-3 guard exercised on four named comments and all four surviving sentences quoted (SWEEP-01); requirement/decision IDs stripped from 31 shipped-source files, the shipped half of the asymmetry (SWEEP-03); the byte-identity pair measured on **all three** AVR targets, not just `uno` (SWEEP-05); the one blob-sha-pinned file Ruling B chose to sweep is swept and both its sidecars re-derived, with the four exemptions proven intact (SWEEP-06 — already ticked at plan 02 for the 8-path classification; this plan discharges its regeneration half).
- **SWEEP-07 — left Pending.** Plan 03 owns RED-before, plan 12 owns RED-after. This plan contributes the measurement that all 5 legs keep their semantics over the swept content (5/5 in the clone, anchoring leg against the real swept file).

## Issues Encountered

None beyond the three auto-fixed items above. No architectural decision was needed and no checkpoint was reached.

## Handoff Notes

- **Plan 08** starts from a firmware tree with **35** modified paths. Its `firestarter/test` sweep is a different group (`fw-test`, 216 hits) and does not overlap anything here; the two Ruling B exempted headers under `test/native/avr/_shared/` (`eprom_v131_expected.h` 4 hits, `sdp_expected.h` 3 hits) are **still exempt** and were verified byte-identical by this plan.
- **Plan 12** must expect exactly 7 red firmware legs before its commit: the 5 porcelain legs (unchanged from plan 06) and the 2 blob-sha gates. All 7 are proven green in a clean clone carrying the same bytes committed. The clone recipe is in this SUMMARY; `/tmp/gsd-154-07-fwclone` is a throwaway and can be deleted at any time. Plan 12 must **not** re-derive the sidecars again — they already carry the correct post-sweep hash `7817c142…`, and `git rev-parse HEAD:src/proms/eprom_params.cpp` will equal it the moment the commit lands, provided nothing further edits that file.
- **Plans 155–158** all shift line numbers in these files and will trip `test_config_schema_pinned.py::test_the_seven_consumers_call_only_the_public_api` the same way. Deferred item **D6** records it; the current pins are `firestarter.cpp` 38/115/121 and `hardware_operations.cpp` 106/118.
- **Phase 159** will remap `.planning/` citations into these 31 files. Composite diff for `src`+`include` in this plan: **557 insertions / 644 deletions over 32 files**, net −87 lines, spread across 128 replaced blocks rather than concentrated — so per-file constant offsets will *not* work here the way they partly did for `eeprom_28c.cpp`, and the range-shrinking path plan 05 built will carry most of the load. `src/firestarter.cpp` alone is 33/38 with the no-touch region shifted −5.
- **The `(D-09)` residual at old `src/firestarter.cpp:204`** is inside the contiguous comment block whose top half is a gate fixture. It is deliberately left, for the same reason plan 06 left `(D-16)`. Do not "finish the job" there without re-proving `_WIRE_LAYOUT_COMMENT`.

## User Setup Required

None.

---

## Self-Check: PASSED

Run after the docs commit, before handing back. Every claim re-verified against disk and git rather than trusted from this session's narrative.

| Check | Command | Result |
|---|---|---|
| This SUMMARY exists | `[ -f .planning/phases/154-…/154-07-SUMMARY.md ]` | FOUND |
| Swept pinned source exists | `[ -f firestarter/src/proms/eprom_params.cpp ]` | FOUND |
| Both sidecars exist | `[ -f …/eprom_params_citations.json ]`, `[ -f …/protocol_branch_inventory.json ]` | FOUND, FOUND |
| Repaired gate module exists | `[ -f firestarter/tests/test_config_schema_pinned.py ]` | FOUND |
| Docs commit exists | `git log --oneline -1 --format=%s` | `docs(154-07): shipped firmware sweep — 96→24 hits, 3 AVR targets byte-identical, both sidecars re-derived`. Checked by SUBJECT, not by SHA: this table lives inside the commit it describes, so amending it to add the table necessarily changes the SHA — a self-referential hash would be stale the moment it was written. Recorded rather than left dangling. |
| ROADMAP row ticked | `grep -c '^- \[x\] 154-07-PLAN.md'` | 1 |
| SWEEP-02 ticked + Complete | `grep -c '^- \[x\] \*\*SWEEP-02\*\*'` / `grep -c '\| SWEEP-02 \| Phase 154 \| Complete (154-07) \|'` | 1 / 1 |
| SWEEP-01/03/05 still Pending | `grep -cE '\| SWEEP-0[135] \| Phase 154 \| Pending \|'` | 3 — correct, phase-wide, plan 12 owns them |
| No commit in `firestarter` | `git -C firestarter log --oneline -1` | `8695ee5` = `FW_PRE_SHA`, unchanged (D-11) |
| No commit in `firestarter_app` | `git -C firestarter_app log --oneline -1` | `6bfa645` = `APP_PRE_SHA`, unchanged |
| Firmware working tree | `git -C firestarter status --short \| wc -l` | 35, **all `M`** — no untracked entries, no deletions |
| App working tree | `git -C firestarter_app status --short \| wc -l` | 13 (plan 03's 6 + 7 pre-existing untracked), untouched |
| Preservation branch intact | `git -C firestarter branch -v \| grep wip/v1.33` | `wip/v1.33-size-reduction-survey-preserved @ a6b46f8` present |
| `baseline-pre-sweep.md` still uncommitted | `git ls-files --error-unmatch …` | untracked — correct per D-11 |
| Forbidden git commands | reviewed every command run this session | none of `reset --hard`, `clean`, `checkout -- <path>`, `restore`, `stash`, force-push or branch deletion was run in any repo. The only clone (`/tmp/gsd-154-07-fwclone`) is a throwaway `--shared` clone whose one commit lives only in it; the parent's HEAD, branches and working tree are verified unchanged above |
