---
phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
plan: "11"
subsystem: host-app
tags: [python, comment-sweep, narrow-treatment, id-retention, ast-invariance, false-positive-abstention, gate-retarget, blocker-resolved]

requires:
  - phase: 154-02
    provides: "survey_provenance.py as the worklist authority and hit oracle (`--group app-tests`), the app-tests per-file hit table (131 hits / 46 files at plan-02 time), the `CORPUS DEFINITION` exclusion that explains why scan_paths.py reads zero, and D-02's CAP-0N exemption"
  - phase: 154-03
    provides: "The 5 SWEEP-07 planted-violation legs (4 RED-on-plant, 1 deliberate fail-open) living in test_sdp_table_parity.py and test_dispatch_mirror.py -- the reason this plan is wave 4 -- plus their recorded before-results and the four planted fixtures left untouched here"
  - phase: 154-08
    provides: "The narrow-treatment precedent for a test group: the three permitted operations, the ID-first-vs-narrative-prefix-first eligibility rule, the named-abstention pattern, and the D-04-exempt trailing-comment-on-code-line reporting convention"
  - phase: 154-09
    provides: "The AST-dump + comment-free-token-stream digest oracle and its non-vacuity control set; the three comment-sensitive host gate exposures; and blocker D7, which this plan resolves"
  - phase: 154-10
    provides: "The corrected verify leg (a trailing inline comment on a code line cannot pass a `every diff line starts with #` grep) and the clean-clone technique for the D-11 porcelain reds"
provides:
  - "The app-tests group swept under D-04's NARROW treatment only: 139 -> 84 provenance hits, all 84 residuals attributed by name (8 plan-03 fixtures untouched by mandate, 6 D-02-exempt CAP-0, 5 survey false positives, 9 named abstentions, 56 retained requirement/decision IDs of which 8 were newly exposed at line-start by the sweep itself)"
  - "D-04's named keep-in-full case discharged by a MEASURED ZERO rather than a judgment call: tests/scan_paths.py carries zero regex hits, so `git diff --quiet` on it exits 0 and PATTERNS.md's suggested reword is deliberately NOT performed"
  - "D-03 retention proven mechanically: `grep -roE 'D-[0-9]+' tests | wc -l` = 1536 before the first edit and 1536 after the last"
  - "BLOCKER D7 RESOLVED: test_parse_gate_admission.py's leg 2 retargeted off the literal `\"Phase 151\"` provenance pin onto a four-phrase conjunction over the CLAIM the comment block records, with the retarget proven STRICTLY STRONGER than the pin it replaced and proven RED against two planted violations"
  - "The full 1976-leg host suite runs 1976 passed / 0 failed / 0 skipped in a clean clone carrying both repos' swept blobs -- the D7 failure that was the ONE genuine red in plan 09's 1975-leg run is gone, and the arithmetic against that baseline closes exactly"
  - "Plan 03's five SWEEP-07 legs re-proven 4-RED / 1-GREEN against the swept text, with test_sdp_table_parity.py at 8 passed and test_dispatch_mirror.py at 4 passed -- identical to plan 03's recorded post-addition totals"
  - "A C/C++ analogue of the host code-invariance oracle for the three swept fixtures: comment-stripped, whitespace-normalised sha256, proven non-vacuous against three controls (a naive offset-preserving stripper FAILS here because shortening a comment changes the space run it leaves behind)"
affects: [154-12]

tech-stack:
  added: []
  patterns:
    - "Retargeting a gate that pins provenance: move the pin from the LABEL to the CLAIM, as a CONJUNCTION of durable phrases, then prove the conjunction is strictly stronger than the single literal by planting a comment that satisfies the OLD pin and records nothing. `\"Phase 151\" in text` passed against `// Phase 151 touched this block.`; the four-phrase conjunction reports all four missing."
    - "A comment-stripping invariance oracle for C/C++ MUST normalise whitespace, not preserve offsets. The offset-preserving stripper this repo already uses (`_strip_comments`, which replaces a comment span with same-shape whitespace) is correct for POSITION arithmetic and wrong for a DIGEST: shortening a comment changes the number of spaces it leaves behind, so all three fixtures reported FAIL on the first attempt. Collapsing every whitespace run to a single space makes comment length unable to leak into the hash -- re-proven non-vacuous against a comment-only edit (MATCH), a one-character code edit (DIFFER) and an added code line (DIFFER)."
    - "A plan-authored `git diff -- <group-dir>` verify leg is confounded by an EARLIER plan's uncommitted edits in the same pathspec. `git diff -U0 -- tests` here reports 346 non-comment lines and 18 docstring lines -- every one of them plan 03's 442-insertion diff, not this plan's. The leg must be scoped to the files THIS plan edited (25 explicit paths), where it reports 4 and 0. This is the D-11 single-commit rule's cost: a shared pathspec is not a per-plan boundary."
    - "Stripping a narrative prefix moves a line between measured populations rather than out of them. 55 of the 63 swept lines stopped being survey hits; 8 remained hits because a retained ID was exposed at line-start (plan 08's measured effect, reproduced); and 20 of the 55 still carry a token further into the line, so the mid-comment (D5/D8) population inside the swept files ROSE 155 -> 175. Every number is reported with its cause."

key-files:
  created: []
  modified:
    - firestarter_app/tests/** (25 files swept, UNCOMMITTED -- D-11)
    - firestarter_app/tests/test_parse_gate_admission.py (the D7 retarget, UNCOMMITTED -- D-11)
    - .planning/phases/154-.../deferred-items.md
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
    - .planning/STATE.md

key-decisions:
  - "`tests/scan_paths.py` is kept in full by NOT EDITING IT AT ALL, and the reason recorded is a measurement: it carries ZERO survey regex hits, because the regex requires the token adjacent to a comment opener and every one of its `D-11`/`A-7`/`C-8`/`BASE-02`/`Phase 123 Plan 08` labels sits inside the module docstring, which sweep-corpus-baseline.md's CORPUS DEFINITION places outside the corpus. 154-PATTERNS.md's suggested reword of that file is therefore deliberately NOT performed -- performing it would silently expand the corpus into docstrings on the strength of a suggestion, not a measurement. The name-collision statement (one `..` from `tools/` lands in the app's own Python package, two reach the sibling firmware repo) is intact and unaltered; `git diff --quiet -- tests/scan_paths.py` exits 0."
  - "The D7 retarget pins the CLAIM, as a conjunction of four durable phrases (`CMD_LOCK_STATUS (16)`, `CMD_READ_VPP (11)`, `this is a CHOICE`, `DBG_* diagnostic`), not the phase label. Restoring `Phase 151` to the firmware source was rejected outright: it would mean shipping a phase label in swept firmware source, defeating the phase. The conjunction was proven STRICTLY STRONGER than the literal it replaced, not merely different -- against a planted `// Phase 151 touched this block.` the OLD pin passes vacuously and the NEW pin reports all four phrases missing."
  - "`test_dispatch_mirror.py` is left COMPLETELY UNEDITED by this plan. Its single hit (line 58, `# Phase 100 restructured the bucket table: ...`) describes the table as it exists (present tense throughout: `column 3 is now`, `the doc leg is now a two-table join`), so it is not a tombstone -- but `Phase 100` is the grammatical SUBJECT of the sentence, not a narrative prefix, and stripping it leaves `# restructured the bucket table:` with no subject. Rewording is forbidden by D-04. Named abstention, and it has the incidental benefit that the module hosting two of the five SWEEP-07 legs receives zero edits from this plan."
  - "The abstention criterion is stated as a rule rather than applied case by case: STRIP when the residue after removing the line-initial token is grammatical, ABSTAIN when it is not. Five of the nine abstentions are mid-sentence continuations where the enclosing grammar spans a line boundary and removal leaves a dangling verb, comma or unclosed parenthesis; two are lines whose token IS the grammatical subject; two are the `test_chip_test.py:580/583` block, abstained TOGETHER because :583 cannot be stripped and half-editing prose whose subject is a phase-to-phase inversion would be worse than leaving it."
  - "Requirement and decision IDs are RETAINED throughout, the deliberate opposite of plans 06/07/09/10's shipped-source rule, and the retention is proven by a count rather than asserted: 1536 `D-NN`-shaped occurrences under `tests` before the first edit and 1536 after the last, across 63 line rewrites in 25 files. Eight swept lines REMAIN survey hits precisely because the strip exposed the retained ID at line-start -- correctly reattributed to D-03 retention rather than to an unstripped prefix."
  - "Five survey false positives are left in place, unreworded, extending plan 09's precedent from two classes to three: `Plan` matching the DOMAIN TYPE `Plan.is_uv` / `Plan.steps` (3 lines -- `Plan` is the dataclass `derive_plan()` returns), `Plan` matching the English word `Planted-violation` (1 line), and `Req` matching the English word `Required` (1 line). Rewriting correct domain vocabulary or correct English to dodge a regex would be a worse outcome than a documented non-zero residual."
  - "The full 1976-leg host suite WAS run, against the plan's own instruction to defer it. The plan's reason for deferring (9-ish porcelain-asserting modules go red against the D-11-mandated uncommitted state) is real and reproduced -- 11 failures in the real tree, every one of them the trailing `assert _git_porcelain(FW_ROOT) == \"\"` line -- but the orchestrator assigned the D7 blocker to this plan, and D7 is only demonstrably fixed by observing the suite. Run in a clean clone carrying both repos' swept blobs committed, per plans 06-10's technique, it reports 1976 passed / 0 failed."
  - "Docstrings were NOT swept, and what was found there is recorded rather than acted on. Within the 25 swept files, token occurrences on non-comment lines went 721 -> 719, and both of those two are the `# Phase 153:` trailing comments on the two `assert counts...` code lines that the diff-class enumeration names explicitly (code prefixes proven byte-identical). Every docstring occurrence is unchanged, proven structurally by the AST digest rather than by grep."

patterns-established:
  - "Every zero and every residual carries its denominator: 84 of 139 residual with all 84 classified into five named buckets that sum exactly; 4 non-comment diff lines of 63 total edits, both pairs prefix-proven; 0 docstring diff lines; 22 of 22 AST+token digests identical and 3 of 3 C-fixture digests identical, each oracle proven non-vacuous FIRST; 1536 -> 1536 `D-NN` occurrences."
  - "A plan-authored verify leg is re-derived, not trusted, when an earlier plan's uncommitted work shares its pathspec -- and the confounded number (346) is reported beside the scoped one (4) so a reader can see why the leg was changed."

requirements-completed: [SWEEP-04]

coverage:
  - id: D1
    description: "The app-tests group is swept under D-04's narrow treatment only, with requirement/decision IDs retained per D-03 and every residual hit attributed by name"
    requirement: "SWEEP-04"
    verification:
      - kind: integration
        ref: "`survey_provenance.py --group app-tests --file-table`: 139 hits / 48 files -> 84 hits / 40 files. Full residual attribution table below; the five buckets sum to exactly 84. Set-diff of the pre and post hit lists: 55 file:line positions ceased to be hits, 0 new positions became hits."
        status: pass
      - kind: integration
        ref: "`grep -roE 'D-[0-9]+' tests | wc -l` = 1536 before the first edit and 1536 after the last -- unchanged across 63 line rewrites in 25 files."
        status: pass
    human_judgment: true
    rationale: "Whether each comment was correctly classified tombstone / label-only / narrative-prefix / abstain has no covering oracle in this group -- D-04 says so explicitly. The reviewable artifact is `git -C firestarter_app diff -- <the 25 paths>`, and every abstention, every false positive and every whole-comment deletion is listed by file and line below."
  - id: D2
    description: "D-04's named keep-in-full case is kept in full, with the measured reason recorded rather than the judgment skipped"
    requirement: "SWEEP-04"
    verification:
      - kind: integration
        ref: "`git -C firestarter_app diff --quiet -- tests/scan_paths.py` exits 0. Cause measured, not assumed: the file carries 0 of the group's 139 hits (it does not appear in either the pre- or post-sweep `--file-table` output), because all its labels sit in the 362-line module docstring."
        status: pass
  - id: D3
    description: "No executable-code change and no docstring change in any swept file, proven structurally"
    requirement: "SWEEP-04"
    verification:
      - kind: integration
        ref: "AST + comment-free-token digests vs APP_PRE_SHA 6bfa6453 over the 22 swept `.py` files: 22 of 22 identical on BOTH digests, 0 differ. Oracle re-proven non-vacuous against 4 controls (comment-only MATCH; code / docstring / string-literal-with-`#` each DIFFER)."
        status: pass
      - kind: integration
        ref: "Comment-stripped, whitespace-normalised sha256 over the 3 swept `.c`/`.cpp` fixtures: 3 of 3 identical. Proven non-vacuous against 3 controls (comment-only MATCH; one-character code edit DIFFER; added code line DIFFER). The first attempt, with an offset-preserving stripper, reported 3 FAIL -- recorded below as an oracle defect found and fixed."
        status: pass
      - kind: integration
        ref: "Scoped diff-class leg over this plan's 25 paths: non-comment/blank diff lines = 4 (2 pairs, both trailing-comment-on-code, both code prefixes proven byte-identical); docstring diff lines = 0; `--numstat` insertions == deletions for every one of the 25 files (63/63 overall), so insertions never exceed deletions."
        status: pass
  - id: D4
    description: "Plan 03's five SWEEP-07 legs keep their 4-RED / 1-GREEN semantics after the modules hosting them are swept"
    requirement: "SWEEP-07"
    verification:
      - kind: integration
        ref: "Clean clone: `pytest tests/test_sdp_table_parity.py tests/test_dispatch_mirror.py` -> 12 passed (8 + 4, exactly plan 03's recorded post-addition totals). `-k \"planted or anchored\"` -> 5 passed. The fail-open leg `test_planted_comment_only_hex_is_NOT_detected` PASSES with no raises-wrapper, verbose-confirmed."
        status: pass
      - kind: integration
        ref: "Real D-11-dirty tree: 5 failed / 7 passed, and every one of the 5 tracebacks fails on the trailing `assert _git_porcelain(FW_ROOT) == \"\"` line with `' M include/b...a_pinned.py' == ''` -- every substantive detection assertion above it already passed. Identical to plans 06-10's recorded benign class."
        status: pass
  - id: D5
    description: "Blocker D7 is resolved: the host gate no longer pins a provenance label, its assertion strength is increased rather than preserved, and the retarget is proven non-vacuous"
    verification:
      - kind: integration
        ref: "`test_parse_gate_admission.py` -> 5 passed (was 3 passed / 1 failed). Leg 2 renamed `test_diagnostic_range_unchanged_with_phase_151_comment` -> `test_diagnostic_range_unchanged_with_stated_choice_comment`; the constant `_PHASE_151_LOOKBACK_CHARS` -> `_STATED_CHOICE_LOOKBACK_CHARS`; the pin is now `_missing_stated_choice_phrases()` over a four-phrase conjunction, all four verified present in the 1200-char lookback window of the SWEPT firmware source."
        status: pass
      - kind: integration
        ref: "Planted violation 1 (throwaway `git clone --shared` of the swept firmware tree; deliberateness sentence + `DBG_*` consequence deleted, BOTH ordinals kept): leg 2 goes RED with `missing ['this is a CHOICE', 'DBG_* diagnostic']`. Planted violation 2 (whole block replaced by `// Phase 151 touched this block.`): the OLD pin passes VACUOUSLY, the NEW pin reports all four missing -- the strictly-stronger proof. Clone file restored byte-identical, clone deleted, real firmware repo still at exactly 93 modified paths."
        status: pass
      - kind: integration
        ref: "Added leg 5 (`test_non_vacuity_control_reports_absent_stated_choice`), mirroring this module's own leg-4 idiom: feeds the SAME helper a synthetic comment block with the claim removed and asserts exactly `['this is a CHOICE', 'DBG_* diagnostic']` missing, then asserts the positive direction on the same helper so the control cannot pass by always reporting absence."
        status: pass
  - id: D6
    description: "The full host suite is measured against plan 09's 1975-leg baseline and the D7 failure is proven gone"
    verification:
      - kind: integration
        ref: "Clean clone carrying BOTH repos' swept blobs committed (fw 797bb93, app 4344b76, both porcelains empty, all 26 touched app blob hashes verified equal to the working tree, both sibling symlinks present plus a `.planning` symlink): **1976 passed / 0 failed / 0 skipped**. Real D-11-dirty tree: **1965 passed / 11 failed = 1976**, all 11 the porcelain class. Arithmetic against plan 09 closes exactly: 1963 passed + 1 (D7 fixed) + 1 (leg 5 added) = 1965; 12 failed - 1 (D7) = 11; 1975 + 1 = 1976. `test_diagnostic_range_unchanged_with_phase_151_comment` appears in neither failure list -- it no longer exists."
        status: pass
      - kind: integration
        ref: "Per-module targeted gates, recorded per module rather than as an aggregate -- 27 modules, 27 green (table below). `ruff check` (0.16.4) clean over all 23 edited `.py` files."
        status: pass
  - id: D7
    description: "The uno byte-identity oracle is unchanged -- a cheap positive proof nothing was written into the firmware repo"
    requirement: "SWEEP-05"
    verification:
      - kind: integration
        ref: "`cd /workspaces/firestarter && rm -rf .pio/build/uno && pio run -e uno` -> `.elf` sha256 `1cfa946f486e041ce5264fc75742ee11e2b437041eaee178ab4d164cbb31ecca`, `.hex` sha256 `be6e4ac80a70e251e2c263beb4109f9f7f9852a034b1064a5dbc8dbbcf05c095`, Flash 26026, RAM 1575 -- all four matching plans 01/06/07/08/09 character for character."
        status: pass

metrics:
  duration: ~115min
  completed: 2026-08-23
  tasks: 3
  files_changed: 26

status: complete
---

# Phase 154 Plan 11: `firestarter_app/tests` Narrow Sweep + the D7 Gate Retarget Summary

**Swept the last group, `firestarter_app/tests`, from 139 provenance hits to 84 under D-04's narrow treatment only — 63 line edits across 25 files, every one of the 84 residuals attributed by name, requirement/decision IDs proven retained by an unchanged 1536-occurrence count, `scan_paths.py` untouched with a MEASURED ZERO as the reason rather than a judgment call, and `test_dispatch_mirror.py` left completely unedited on a named abstention — and resolved blocker D7 by retargeting `test_parse_gate_admission.py`'s leg 2 off the literal string `"Phase 151"` onto a four-phrase conjunction over the claim the comment actually records, proven STRICTLY STRONGER than the pin it replaced against a planted comment that satisfies the old pin vacuously. The 1975-leg suite's ONE genuine failure is gone: a clean clone carrying both repos' swept blobs runs 1976 passed / 0 failed / 0 skipped.**

---

## 1. The primary oracle: hit count, before and after

```bash
cd /workspaces && python3 .planning/v1.33/tools/survey_provenance.py \
  /workspaces/firestarter /workspaces/firestarter_app --group app-tests --file-table
```

| Group | Candidate files | Files with hits | Hits |
|---|---|---|---|
| app-tests **before this plan** | 153 | 48 | **139** |
| app-tests **after** | 153 | 40 | **84** |

### Reconciling 139 against every recorded figure — nothing silently adopted

| Source | app-tests hits | Cause of the delta |
|---|---|---|
| `154-CONTEXT.md` D-04 | **115** | `.py` files only |
| `sweep-corpus-baseline.md` §"Per-group table" (plan 02) | **131** | 115 + the **16** hits in the 9 pre-existing `tests/fixtures/planted_*.c/.cpp/.h` files that plan 02's §"Reconciliation" already enumerates one-for-one |
| **This session, at plan start** | **139** | 131 + **8**, being 4 hits each in `planted_sdp_comment_brace.cpp` and `planted_sdp_comment_misanchor.cpp` — two of the four fixtures **plan 03** created and this plan is forbidden to touch. Candidate files 149 → 153 is the same four fixtures. |

Every delta closes to the hit and to the file.

### Per file, measured (the corrected `file_hits` key, not the integer `files` count)

| File | Before | After |
|---|---|---|
| `conftest.py` | 8 | 2 |
| `fixtures/planted_cap03_literal_index.cpp` | 2 | 2 |
| `fixtures/planted_cap03_truncated_length.cpp` | 2 | 2 |
| `fixtures/planted_constants_fw_missing.h` | 1 | 1 |
| `fixtures/planted_constants_host_missing.h` | 1 | 1 |
| `fixtures/planted_constants_value_drift.h` | 1 | 1 |
| `fixtures/planted_ifdef_in_predicate.h` | 1 | 1 |
| `fixtures/planted_json_parser_key_string_drift.c` | 4 | 0 |
| `fixtures/planted_json_parser_undispatched_key.c` | 3 | 0 |
| `fixtures/planted_log_in_window.cpp` | 1 | 0 |
| `fixtures/planted_sdp_comment_brace.cpp` (plan 03) | 4 | 4 |
| `fixtures/planted_sdp_comment_misanchor.cpp` (plan 03) | 4 | 4 |
| `test_budget_failure_render.py` | 1 | 1 |
| `test_build_db_inclusion.py` | 2 | 2 |
| `test_characterization.py` | 2 | 1 |
| `test_chip_resolver.py` | 2 | 0 |
| `test_chip_test.py` | 12 | 9 |
| `test_chip_test_cycle.py` | 1 | 1 |
| `test_chip_test_sdp_leg.py` | 6 | 6 |
| `test_cli_handlers.py` | 1 | 0 |
| `test_consistency_check.py` | 3 | 1 |
| `test_database_conversion.py` | 1 | 1 |
| `test_decoder.py` | 2 | 2 |
| `test_dev_test_cmd.py` | 7 | 7 |
| `test_diagnostic_report.py` | 1 | 1 |
| `test_dispatch_mirror.py` | 1 | 1 |
| `test_eprom_operations.py` | 8 | 2 |
| `test_firmware_install.py` | 6 | 2 |
| `test_frame_vectors.py` | 1 | 0 |
| `test_ic_layout.py` | 4 | 1 |
| `test_parse_devtest_issue.py` | 1 | 1 |
| `test_protocol_not_implemented_production_path.py` | 1 | 1 |
| `test_pulse_us_override.py` | 2 | 1 |
| `test_py32_asset_name_host.py` | 1 | 1 |
| `test_py32_flash_map_host.py` | 1 | 1 |
| `test_py32_packaging.py` | 5 | 4 |
| `test_py32_pyusb_absent.py` | 1 | 1 |
| `test_revision_constants_parity.py` | 3 | 1 |
| `test_sdp_db_invariant.py` | 1 | 1 |
| `test_sdp_honesty.py` | 1 | 0 |
| `test_serial_comm.py` | 4 | 1 |
| `test_skip_census.py` | 1 | 1 |
| `test_submit.py` | 13 | 6 |
| `test_update_version.py` | 4 | 4 |
| `test_val_wire_5v_page.py` | 1 | 0 |
| `test_variant_decode_evidence_stability.py` | 1 | 1 |
| `test_wire_dict_equivalence.py` | 3 | 1 |
| `test_write_skip_erase_0x0d.py` | 2 | 1 |
| **TOTAL** | **139** | **84** |

`tests/scan_paths.py` appears in **neither** column — that is the measurement §3 rests on.

### D-04's 331 test-file hits, closed across both plans

| Group | Plan | Pre-sweep | Post-sweep |
|---|---|---|---|
| `fw-test` (`firestarter/test/native`) | 08 | 216 | 61 |
| `app-tests` (`firestarter_app/tests`) | **11** | **115** (`.py` only) / **131** (plan 02's whole group) / **139** (at plan start, incl. plan 03's fixtures) | **84** |

D-04's own figure was `216 + 115 = 331`; the tool's group figure is `216 + 131 = 347`; at this plan's start the app half was `139`. All three are stated rather than one being adopted.

---

## 2. Residual attribution — all 84, in five buckets that sum exactly

| Bucket | Count | Basis |
|---|---|---|
| a. Plan 03's fixtures, untouched by mandate | **8** | `planted_sdp_comment_brace.cpp` 40/46/79/86, `planted_sdp_comment_misanchor.cpp` 47/53/86/93 — all four also ID-first, so ineligible regardless |
| b. D-02-exempt `CAP-0` lines | **6** | `conftest.py` 224/229; `planted_cap03_literal_index.cpp:53`; `planted_cap03_truncated_length.cpp:50`; `test_protocol_not_implemented_production_path.py:274`; `test_serial_comm.py:464` |
| c. Survey false positives, left unreworded | **5** | §5 |
| d. Named abstentions | **9** | §4 |
| e. Retained requirement/decision IDs at line-start (D-03) | **56** | of which **8** are newly at line-start because this sweep stripped the prefix in front of them |
| **TOTAL** | **84** | |

`8 + 6 + 5 + 9 + 56 = 84`, exactly.

### The 8 retained IDs the sweep itself exposed

Plan 08's measured effect, reproduced on the host side: stripping a narrative prefix routinely exposes a *new* line-start hit, correctly reattributed to D-03 retention rather than to an unstripped prefix.

| File:line | After the strip |
|---|---|
| `test_chip_test_sdp_leg.py:409` | `#     D-08 names -- it is a SUBCLASS of EpromOperationError,` |
| `test_database_conversion.py:229` | `# D-40 label-only CAN_ERASE pinning assertions` |
| `test_decoder.py:450` | `    # D-03 / WR-01 close: MSG_INFO_HW + MSG_INFO_PHYSICAL_HW` |
| `test_eprom_operations.py:1215` | `# D-15 / HOST-06: the 0x86 ack requirement inside` |
| `test_firmware_install.py:126` | `# D-01 landed).` |
| `test_py32_packaging.py:81` | `# D-15: the install doc's non-vacuity anchor -- the same` |
| `test_py32_packaging.py:233` | `# D-15, D-13: doc-vs-constant parity gate. The install doc's` |
| `test_write_skip_erase_0x0d.py:81` | `# D-153-05 / RESEARCH Pitfall 5 guard literal (leg 7 below): a` |

### D-03 retention, measured rather than asserted

```bash
grep -roE 'D-[0-9]+' tests | wc -l
# 1536 before the first edit; 1536 after the last
```

63 comment lines were rewritten across 25 files, many of them the line an ID sits on or beside. Not one occurrence was lost.

---

## 3. `scan_paths.py` — kept in full by making no edit at all

```bash
git -C firestarter_app diff --quiet -- tests/scan_paths.py   # exits 0
```

D-04 names this file's module docstring as the keep-in-full case, and `154-PATTERNS.md` §`firestarter_app/tests/scan_paths.py` suggests a reword. **The reword is deliberately not performed.** The reason is a measurement, not a judgment:

- The file carries **zero** of the group's 139 hits. It appears in neither the pre- nor the post-sweep `--file-table`.
- The cause is the corpus definition, not luck: `survey_provenance.py`'s regex requires the provenance token **immediately after** a comment opener, and every one of this file's `D-11` / `A-7` / `C-8` / `BASE-02` / `Phase 123 Plan 08` labels sits inside its 362-line **module docstring** — which `sweep-corpus-baseline.md`'s `CORPUS DEFINITION` section places outside the corpus, citing this exact file as its canonical example, with its measured size and cause.
- "Keep in full" is therefore satisfied by leaving it alone. Rewording it on PATTERNS.md's suggestion would silently expand the corpus into docstrings on the strength of a suggestion rather than a measurement — the T-154-45 threat the plan's own register names.

The name-collision statement is **intact and unaltered**, quoted from the untouched file — it is the sentence the remap tool's path handling was checked against:

> one `..` from `tools/` lands in the app's own Python package (`firestarter_app/firestarter`), two `..` reach the sibling firmware repo (`/workspaces/firestarter`).

Plan 03's four fixtures are likewise untouched:

```bash
git -C firestarter_app diff --quiet -- \
  tests/fixtures/planted_sdp_comment_misanchor.cpp tests/fixtures/planted_sdp_comment_brace.cpp \
  tests/fixtures/planted_dispatch_comment_only_hex.cpp tests/fixtures/planted_dispatch_missing_hex.cpp
# exits 0
```

---

## 4. The three permitted operations, measured by kind — and the 9 abstentions

| Operation | Count | Note |
|---|---|---|
| **Tombstone deletion** (comment describing absent code) | **0** | A measured absence, same as plan 08's finding for `fw-test`. Two candidates were read and rejected: `test_firmware_install.py:1024` and `:1255` describe tests **deliberately deleted** on the argparse→Click swap — they are deletion *records*, the reason something is absent, not comments describing code that should be there. Prefix stripped, body kept. |
| **Label-only-comment deletion** | **0** | No comment in this group reduces to connective punctuation after removing its tokens. `test_submit.py`'s seven `# Task N: ...` section headers all carry real content after the label (`sanitize_dict -- one test per leak vector`), so they are prefix strips, not deletions. |
| **Narrative-prefix stripping (sentence/fragment kept as written)** | **63** | The whole of this plan's edit set |
| **Abstention (recorded, not forced)** | **9** | Below |

**Eligibility rule, inherited verbatim from plan 08:** a hit is eligible for prefix stripping only when the first token after the comment opener is `Phase` / `Plan` / `Task` / `PNNN` / `NNN-CONTEXT`. A hit whose first token is a retained ID gets **zero** operations. Measured split of the 139: **76** prefix-eligible, **55** ID-first or CAP-0, **8** plan-03 fixtures.

**Abstention criterion, stated as a rule rather than decided case by case:** strip when the residue after removing the line-initial token is grammatical; abstain when it is not. Rewording to repair grammar is forbidden by D-04, so an ungrammatical residue is an abstention by construction.

### The 9 abstentions, quoted with their reason

**1-2. `test_chip_test.py:580` and `:583`** — abstained *together*, as one block.

```
580|     # Phase 109 (D-01, SAFE-01) INVERTS the Phase-108 annotate-only
581|     # contract: write_scope="none" must structurally OMIT write/erase from
582|     # the executable steps list; write_scope="full" keeps them exactly as
583|     # Phase 108 produced them (121-05 D-02: the kwarg is now the
```

`:583`'s `Phase 108` is the subject of a clause opened on `:582` ("keeps them exactly as **Phase 108** produced them"); removing it yields "keeps them exactly as produced them". `:580` alone *is* strippable, but this block's entire subject is the phase-to-phase inversion — half-editing it would leave `Phase-108` and `Phase 108` in place while deleting `Phase 109`, which reads as damage rather than hygiene.

**3. `test_chip_test.py:2160`** — the parenthetical opens on the previous line.

```
2159| # OP_WRITE_PARTIAL through the production run_plan path (D-06/D-07, Phase 121
2160| # Plan 06, Task 3) -- RESEARCH Pitfall 4: every region proof here drives
```

Removing `Plan 06, Task 3)` leaves `:2159`'s `(` unclosed. `Phase 121` on `:2159` is mid-line and not itself a hit, so repairing both lines would be a cross-line reflow, which D-04 forbids.

**4. `test_diagnostic_report.py:340`** — identical shape.

```
339| # Partial-vs-full-write fingerprint differentiation (D-06/D-08, Phase 121
340| # Plan 07). This is D-06/D-08's proof, not merely its argument: the GRAD-01
```

**5. `test_dispatch_mirror.py:63`** — the token is the grammatical **subject**, and the comment is judged **not** a tombstone.

```
58| # Phase 100 restructured the bucket table: the `.cpp` filename moved OUT of
```

The plan asked for this judgment explicitly. The block describes the table **as it exists** — `column 3 is now the frozen datasheets/ slug`, `the doc leg is now a two-table join` — so it is not a tombstone. But `Phase 100` is the sentence's subject, not a prefix: stripping it yields `# restructured the bucket table:` with nothing performing the restructuring. **This plan therefore makes zero edits to `test_dispatch_mirror.py`**, which is the module hosting two of the five SWEEP-07 legs.

**6. `test_ic_layout.py:165`** — the token is a predicate complement.

```
164| # Neither test asserts on description_points bullet text (D-03 — bullets are
165| # Phase-103-owned; prose reconciliation is out of scope here).
```

"bullets are **Phase-103-owned**"; removing it leaves "bullets are ;".

**7. `test_parse_devtest_issue.py:308`** — possessive mid-phrase.

```
307| # AGREEING (D-03, GRAD-01) -- dedup_fingerprint grouping, distinct from
308| # Phase-108's per-run N>=2
```

Removing it leaves `# 's per-run N>=2`.

**8. `test_sdp_db_invariant.py:188`** — dangling comma.

```
187| # What it is: the ALLOW half of the `0x0D` SDP partition, snapshotted
188| # Phase 131 plan 131-03, measured 43 of 84. Prior value: none, first
```

Removing it leaves "snapshotted , measured 43 of 84".

**9. `test_wire_dict_equivalence.py:222`** — possessive mid-phrase, and the label is content.

```
221| # golden to make a failure disappear breaks this assertion, keeping
222| # Phase 148's own central claim ("this migration changed nothing on the
```

Removing it leaves "keeping own central claim". The label is also load-bearing here: the golden sidecars this block guards are literally named `wire_dict_expected_deltas_149.json` / `_153.json`, so "Phase 148's own central claim" names a specific, still-live artifact.

### Two cross-line-boundary cases judged STRIPPABLE, reported for review

The abstention criterion cut both ways, so the two cases it admitted are named rather than folded into the bulk count:

```diff
79| # snapshots were pinned WITHOUT any override, so a local override (e.g. the
-80| # Phase 81 2516 user-override entry) would leak a spurious row into `list`/`info`
+80| # 2516 user-override entry) would leak a spurious row into `list`/`info`
```
→ "(e.g. the **2516 user-override entry**)" — grammatical and, if anything, clearer.

```diff
123| # (both at 3.0.0). Asset order [uno, uno328pb, leonardo] follows Phase 21
124| # D-08 section-order discipline (matches platformio.ini default_envs order
-125| # Phase 22 D-01 landed).
+125| # D-01 landed).
```
→ "(matches platformio.ini default_envs order **D-01 landed**)" — a relative clause with an elided "that", grammatical, and it exposes the retained `D-01`.

### The 2 D-04-exempt trailing-comment-on-code-line edits, reported literally

Per plan 08's convention, these are **not** laundered into "every changed line is a comment":

```diff
-    assert counts.m_applicable == 10, counts  # Phase 153: erase joined M (9 -> 10)
+    assert counts.m_applicable == 10, counts  # erase joined M (9 -> 10)
-    assert counts.n_ran == 6, counts  # Phase 153: erase joined N (5 -> 6)
+    assert counts.n_ran == 6, counts  # erase joined N (5 -> 6)
```

Code prefixes proven byte-identical against `APP_PRE_SHA` by an explicit per-line check:

```
line 2990: code prefix identical = True   prefix='    assert counts.m_applicable == 10, counts  '
line 2991: code prefix identical = True   prefix='    assert counts.n_ran == 6, counts  '
```

Denominator: **4 of 4** filtered `git diff -U0` lines across the 25 paths (2 pairs). Nothing else in this plan's diff is anything but a whole comment line or blank.

### Pre-existing fixtures swept — the header names the gate, so only the prefix goes

The plan asked that a fixture header naming the gate and the seam be treated as substantive. Measured, that is exactly what happened: of the 9 pre-existing `planted_*` fixtures carrying 16 hits, the **7** whose hits are `D-NN` / `CAP-0` file-header lines (`planted_cap03_*`, `planted_constants_*`, `planted_ifdef_in_predicate.h`) got **zero** edits — those lines are ID-first — and only the 3 with `Phase N --` prefixes were touched:

```diff
-/* Phase 44 -- host-tunable read-timing knobs (D-04 sweep params) */
+/* host-tunable read-timing knobs (D-04 sweep params) */
-/* Phase 149 -- per-chip page-write size delivered by the host (PGSZ-01/PGSZ-02).
+/* per-chip page-write size delivered by the host (PGSZ-01/PGSZ-02).
- * Phase 118 Plan 01 (D-06) redefined the checker's scanned window from the
+ * (D-06) redefined the checker's scanned window from the
```

Every `PLANTED VIOLATION` / `DELIBERATELY-VIOLATING` sentence, and every gate name and seam name, survives untouched. Before editing, both fixture gates were checked for a blob-sha pin over the fixture: `test_json_key_parity.py`'s `hash-object` calls all target `FW_ROOT` paths, and `test_check_no_log_in_sdp_window.py` pins no hash — so no fixture in this plan's scope is sha-pinned.

---

## 5. The 5 survey false positives, left deliberately unreworded

Plan 09 named two classes; this group extends it to three.

| File:line | Text | Class |
|---|---|---|
| `test_chip_test.py:351` | `# Plan.is_uv / Step.write_region -- carried fields, defaulted (D-02)` | `Plan` matching the **domain type** — `Plan` is the dataclass `derive_plan()` returns |
| `test_chip_test.py:961` | `# Plan.is_uv wiring proof, through derive_plan (D-02, 121-05 Task 3 leg 3)` | same |
| `test_chip_test_sdp_leg.py:270` | `# Plan.steps (D-01, SAFE-01), so this literal covers only {id, read,` | same |
| `test_revision_constants_parity.py:714` | `# Planted-violation and fail-closed legs (Phase 120 Plan 07, Task 3).` | `Plan` matching the English word **`Planted`** — a new class, not previously recorded |
| `test_py32_pyusb_absent.py:167` | `# Required even in the pyusb-absent devcontainer, and load-bearing in the` | `Req` matching **`Required`** — plan 09's `firmware.py:840` class |

Rewriting correct domain vocabulary (`Plan.is_uv` is the attribute the test asserts on) or correct English to dodge a regex would be a worse outcome than a documented non-zero residual. `test_revision_constants_parity.py:714` also carries a mid-line `Phase 120 Plan 07, Task 3` — the D5/D8 deferred class, left in place with the rest of it.

---

## 6. Code invariance — two oracles, both proven non-vacuous first

### 6a. The 22 swept `.py` files: AST + comment-free token digests vs `APP_PRE_SHA`

Plan 09's oracle, reused. Non-vacuity re-proven before trusting it, against `test_submit.py`'s pre-sweep text:

| Control | Required | Measured |
|---|---|---|
| Comment-only edit (`# Task 1: sanitize_dict` → `# sanitize_dict`, plus a trailing blank line) | MATCH | **MATCH** |
| Code edit (`import submit` → `import submit as submit`) | DIFFER | **DIFFER** |
| Docstring edit (3 chars inserted into the module docstring) | DIFFER | **DIFFER** |
| String literal containing a `#` (`y = "# Phase 9"` appended) | DIFFER | **DIFFER** |

Result: **22 of 22 identical on BOTH digests, 0 differ.**

```
OK   tests/conftest.py                          ast=5ee1d9af86d8/5ee1d9af86d8  tok=8f61a9783f86/8f61a9783f86
OK   tests/test_characterization.py             ast=c3739eea7546/c3739eea7546  tok=4f7301ffff40/4f7301ffff40
OK   tests/test_chip_resolver.py                ast=62eefdd07cf1/62eefdd07cf1  tok=c584306a2945/c584306a2945
OK   tests/test_chip_test.py                    ast=2a665be540f8/2a665be540f8  tok=713ec3c68fae/713ec3c68fae
OK   tests/test_chip_test_sdp_leg.py            ast=e0bcaacd0c85/e0bcaacd0c85  tok=aff89df9bca7/aff89df9bca7
OK   tests/test_cli_handlers.py                 ast=3ccd5b55adc3/3ccd5b55adc3  tok=7d9146264462/7d9146264462
OK   tests/test_consistency_check.py            ast=2021f24645c7/2021f24645c7  tok=c7c96dfd19cb/c7c96dfd19cb
OK   tests/test_database_conversion.py          ast=5bd6ebc2c03d/5bd6ebc2c03d  tok=16a8e68c167f/16a8e68c167f
OK   tests/test_decoder.py                      ast=a42baaa06e60/a42baaa06e60  tok=5ca36f352402/5ca36f352402
OK   tests/test_eprom_operations.py             ast=ae8a2e2d8fce/ae8a2e2d8fce  tok=22a41ceadba5/22a41ceadba5
OK   tests/test_firmware_install.py             ast=33c77367b75d/33c77367b75d  tok=ede37c61d4bf/ede37c61d4bf
OK   tests/test_frame_vectors.py                ast=4f22c7030c9a/4f22c7030c9a  tok=05a45132183d/05a45132183d
OK   tests/test_ic_layout.py                    ast=8ee90a09970a/8ee90a09970a  tok=047c2903d65e/047c2903d65e
OK   tests/test_pulse_us_override.py            ast=c56939e31d8c/c56939e31d8c  tok=a5518b4eab24/a5518b4eab24
OK   tests/test_py32_packaging.py               ast=9343ea2d55be/9343ea2d55be  tok=585394cfa8e6/585394cfa8e6
OK   tests/test_revision_constants_parity.py    ast=4dd591a3f46f/4dd591a3f46f  tok=108d3ae43fc8/108d3ae43fc8
OK   tests/test_sdp_honesty.py                  ast=2b71c60ba74f/2b71c60ba74f  tok=0f09eb764a2a/0f09eb764a2a
OK   tests/test_serial_comm.py                  ast=60aec39ef7ac/60aec39ef7ac  tok=b0211fb55aa8/b0211fb55aa8
OK   tests/test_submit.py                       ast=ca4429c0f4d9/ca4429c0f4d9  tok=521c90912e61/521c90912e61
OK   tests/test_val_wire_5v_page.py             ast=2f978ed36c1a/2f978ed36c1a  tok=02bfa364938f/02bfa364938f
OK   tests/test_wire_dict_equivalence.py        ast=c6e8c538a71a/c6e8c538a71a  tok=1d425d4604e6/1d425d4604e6
OK   tests/test_write_skip_erase_0x0d.py        ast=7e8875755585/7e8875755585  tok=da39ee4c2e0b/da39ee4c2e0b
```

**`tests/test_parse_gate_admission.py` is EXCLUDED from this oracle, and the exclusion is stated rather than hidden:** it is the D7 retarget, a deliberate and recorded change to executable test code (a renamed function, a renamed constant, a new helper, a rewritten assertion and one added leg). Running the invariance oracle over it would necessarily report FAIL, and reporting that as a failure would misdescribe an assigned task as damage. Its correctness is established instead by §7's planted-violation ceremony and by the suite.

### 6b. The 3 swept C/C++ fixtures — and an oracle defect found and fixed

The `.py` oracle does not apply to `.c`/`.cpp`. First attempt used this repo's existing `_strip_comments` idiom (replace a comment span with **same-shape** whitespace, so byte offsets still line up) and reported **3 FAIL**. That is a defect in the oracle, not the sweep: shortening a comment changes the number of spaces the stripper leaves behind, so the digest moves even though no code did. Recorded because the wrong version looks right.

Corrected oracle: strip comments **and collapse every whitespace run to a single space**, so comment length cannot leak into the hash. Non-vacuity proven first, against `planted_json_parser_key_string_drift.c`'s pre-sweep text:

| Control | Required | Measured |
|---|---|---|
| Comment-only edit | MATCH | **MATCH** (`ccd0d736df6b`) |
| One-character code edit (`"page_size"` → `"pageXsize"`) | DIFFER | **DIFFER** (`f79bb2411f97`) |
| Added code line | DIFFER | **DIFFER** (`f1293bbb1b40`) |

Result: **3 of 3 identical.**

```
OK   tests/fixtures/planted_json_parser_key_string_drift.c   code-only sha=ccd0d736df6b/ccd0d736df6b
OK   tests/fixtures/planted_json_parser_undispatched_key.c   code-only sha=f73289c1c63f/f73289c1c63f
OK   tests/fixtures/planted_log_in_window.cpp                code-only sha=245750f85ed9/245750f85ed9
```

### 6c. The diff-class leg — and why the plan's own version had to be re-scoped

The plan's automated leg is `git diff -U0 -- tests | ... | grep -vc '^[+-]\s*(#|//|\*|/\*|$)'` must equal **0**. Run as written it reports **346**, with **18** docstring lines. **None of that is this plan's work** — it is plan 03's 442-insertion / 2-deletion diff to `test_dispatch_mirror.py` and `test_sdp_table_parity.py`, sitting uncommitted in the same pathspec because D-11 reserves the app repo's single commit for plan 12. A shared pathspec is not a per-plan boundary.

Re-scoped to this plan's 25 swept paths:

```bash
git diff -U0 -- <the 25 paths> | grep -E '^[+-]' | grep -vE '^[+-]{3}' \
  | grep -vcE '^[+-][[:space:]]*(#|//|\*|/\*|$)'
# 4      (the 2 trailing-comment-on-code pairs of §4, both prefixes proven identical)
… | grep -cE '^[+-][[:space:]]*"""'
# 0      docstring diff lines
```

`--numstat` over the 25 paths: **insertions == deletions for every single file** (63 / 63 overall), so the narrow-treatment proxy "insertions do not exceed deletions" holds with zero exceptions and zero files needing a named reason.

### 6d. Docstrings and mid-comment tokens — measured and left, not silently swept

Within the 25 swept files (D7 file excluded):

| Population | Before | After | Disposition |
|---|---|---|---|
| Comment lines carrying a D-01 token **not adjacent** to the opener (the D5/D8 class) | 155 | **175** | Left in place. It **rose** by 20, and the cause is mechanical: 20 of the 55 lines that stopped being hits still carry a token further into the line, so stripping the prefix moved them from the hit population into this one. Not a regression — a reclassification, reported with its cause. |
| Token occurrences on **non-comment** lines (docstrings, string literals, trailing comments on code) | 721 | **719** | The −2 is exactly the two `# Phase 153:` trailing comments of §4. Every docstring occurrence is unchanged, proven structurally by the AST digest (docstrings are `ast.Constant` nodes), not by grep. |

Across the whole tracked `tests` tree the same two populations read 373 → 392 and 2016 → 2013; the extra −3 is the D7 file's deliberate retarget.

---

## 7. Blocker D7 — resolved by retargeting the pin onto the claim

**Orchestrator-assigned task, beyond this plan's written scope.** Plan 09 filed D7 as a BLOCKER for plan 12: `test_parse_gate_admission.py::test_diagnostic_range_unchanged_with_phase_151_comment` asserted the **literal string** `"Phase 151"` inside a 1200-character lookback window above the diagnostic-range guard in `firestarter/src/firestarter.cpp`, and plan 07's sweep correctly deleted that label. Measured: `git show 8695ee52:src/firestarter.cpp | grep -c 'Phase 151'` = **3**; on the swept tree, **0**. It was the ONE genuine failure in plan 09's whole 1975-leg run.

**Restoring the label was rejected outright** — it would mean shipping a phase label in swept firmware source, defeating the phase this plan is part of.

### What the gate actually guards

Its own docstring says: the comment block preceding the diagnostic-range test must record "the no-`DBG_*`-output consequence as a stated choice (DESIGN.md §7), not a silent, undocumented gap." The `"Phase 151"` literal was only an *anchor* for that recording. The recording itself survived plan 07's sweep intact:

```c
    // CMD_LOCK_STATUS (16) is numerically greater than CMD_READ_VPP (11), so
    // it falls outside this range by construction -- this is a CHOICE
    // recorded here, not a discovery made on the bench.
    // `dev lock-status` therefore emits none of the three DBG_* diagnostic
    // lines below.
```

### The retarget

| Before | After |
|---|---|
| `assert "Phase 151" in preceding_text` | `assert not _missing_stated_choice_phrases(preceding_text)` |
| `_PHASE_151_LOOKBACK_CHARS = 1200` | `_STATED_CHOICE_LOOKBACK_CHARS = 1200` |
| `test_diagnostic_range_unchanged_with_phase_151_comment` | `test_diagnostic_range_unchanged_with_stated_choice_comment` |
| — | `_STATED_CHOICE_PHRASES` + the shared helper, and a new **leg 5** non-vacuity control |

```python
_STATED_CHOICE_PHRASES = (
    "CMD_LOCK_STATUS (16)",
    "CMD_READ_VPP (11)",
    "this is a CHOICE",
    "DBG_* diagnostic",
)
```

**ALL FOUR** must be present — the conjunction is what makes it a claim-level pin: two wire ordinals, the word CHOICE, and the named consequence. All four verified present in the 1200-char lookback window of the **swept** source; `"Phase 151"` verified absent from it. None of the four is provenance, so no future sweep can break it the way this one broke the label pin.

The module docstring's taxonomy entry 2 was rewritten to describe what the leg now does, including why — a docstring that still promised a `"Phase 151"` sentence would misdescribe the leg for the next reader.

### The retarget is STRICTLY STRONGER, proven — not merely different

The ceremony is plan 03's V12 pattern, run against a throwaway `git clone --shared` of the firmware repo carrying plan 07's swept working tree (the real repo was never written to — confirmed still at exactly 93 modified paths afterwards; clone deleted).

| Run | Old pin (`"Phase 151"`) | New pin (conjunction) |
|---|---|---|
| Un-planted swept clone (baseline) | RED — this is D7 | **GREEN** |
| **Plant 1** — deliberateness sentence + `DBG_*` consequence deleted, **both ordinals kept** | (n/a) | **RED**: `missing ['this is a CHOICE', 'DBG_* diagnostic']` |
| **Plant 2** — whole block replaced by `// Phase 151 touched this block.` | **GREEN — vacuous pass** | **RED**: all four phrases missing |

Plant 2 is the strength proof: a comment that records *nothing* about the choice satisfied the old pin completely. The observed RED message from plant 1, verbatim:

```
E  AssertionError: the comment block preceding the diagnostic-range test no longer
   records DESIGN.md §7's stated choice -- missing ['this is a CHOICE', 'DBG_* diagnostic'].
   Command 16 emitting no DBG_* diagnostic output is a CHOICE and must be recorded there,
   not left to be rediscovered.
```

Clone source file restored byte-identical after each plant (`diff -q` empty), module back to 5 passed.

### Leg 5 — the committed checkable negative

A live planted-violation run proves the retarget today; it does not survive as a committed control. So leg 5 was added, mirroring this module's **own** leg-4 idiom exactly (synthetic in-memory string fed to the shared helper — this module deliberately cannot `monkeypatch.setenv` `FIRESTARTER_FW_ROOT`, since `fw_presence.py` binds `FW_ROOT` at import time, correction C-15). It:

1. asserts its own fixture sanity first, with distinct `Fixture setup error: ...` messages, so a broken control is distinguishable from a passing check;
2. asserts `_missing_stated_choice_phrases()` returns **exactly** `["this is a CHOICE", "DBG_* diagnostic"]` against a block that keeps both ordinals and drops the claim;
3. asserts the **positive** direction on the same helper, so the control cannot pass by reporting absence unconditionally.

`pytest tests/test_parse_gate_admission.py -o addopts="" -q` → **5 passed** (was 3 passed / 1 failed). `ruff check` clean.

---

## 8. Suite and gate measurements

### The five SWEEP-07 legs, leg by leg, against the swept text

Real (D-11-dirty) tree — `5 failed / 7 passed`, and every one of the 5 tracebacks fails on the **trailing** porcelain line:

```
>  assert _git_porcelain(FW_ROOT) == "", (
E  AssertionError: the sibling firmware repo is not clean after this planted-violation run …
E  assert ' M include/b...a_pinned.py\n' == ''
```

Every substantive assertion above it had already passed. Identical to the benign class plans 06-10 each documented. Clean clone (both repos' swept blobs committed, both sibling symlinks present):

| Leg | Selector | Plan 03's recorded before-result | Now |
|---|---|---|---|
| `test_planted_comment_misanchor_is_detected` | `-k planted_comment_misanchor` | PASS (asserts RED occurred) | **PASS** |
| `test_planted_comment_brace_break_is_detected` | `-k planted_comment_brace` | PASS (asserts RED occurred) | **PASS** |
| `test_extracted_slice_is_anchored_on_the_real_declaration` | `-k anchored` | PASS | **PASS** |
| `test_planted_missing_hex_is_detected` | `-k planted_missing_hex` | PASS (asserts RED occurred) | **PASS** |
| `test_planted_comment_only_hex_is_NOT_detected` | `-k planted_comment_only` | PASS, **no raises-wrapper** | **PASS**, no raises-wrapper (verbose-confirmed) |

Module totals match plan 03 exactly: `test_sdp_table_parity.py` **8 passed**, `test_dispatch_mirror.py` **4 passed**, combined **12 passed**, `-k "planted or anchored"` **5 passed**.

### Per-module targeted gates — recorded per module, not as an aggregate

| Module | Result | | Module | Result |
|---|---|---|---|---|
| `test_characterization.py` | 36 passed | | `test_revision_constants_parity.py` | 14 passed |
| `test_chip_resolver.py` | 12 passed | | `test_sdp_honesty.py` | 9 passed |
| `test_chip_test.py` | 149 passed | | `test_serial_comm.py` | 44 passed |
| `test_chip_test_sdp_leg.py` | 82 passed | | `test_submit.py` | 102 passed |
| `test_cli_handlers.py` | 66 passed | | `test_val_wire_5v_page.py` | 14 passed |
| `test_consistency_check.py` | 9 passed | | `test_wire_dict_equivalence.py` | 7 passed |
| `test_database_conversion.py` | 20 passed | | `test_write_skip_erase_0x0d.py` | 7 passed |
| `test_decoder.py` | 37 passed | | `test_sdp_table_parity.py` | 8 passed |
| `test_eprom_operations.py` | 43 passed | | `test_dispatch_mirror.py` | 4 passed |
| `test_firmware_install.py` | 46 passed | | `test_json_key_parity.py` (fixture gate) | 10 passed |
| `test_frame_vectors.py` | 13 passed | | `test_check_no_log_in_sdp_window.py` (fixture gate) | 7 passed |
| `test_ic_layout.py` | 13 passed | | `test_parse_gate_admission.py` (D7) | 5 passed |
| `test_pulse_us_override.py` | 10 passed | | `test_skip_census.py` | 5 passed |
| `test_py32_packaging.py` | 12 passed | | | |

**27 modules, 27 green.** `conftest.py` has no module of its own — it is exercised by the entire suite. `ruff check` (0.16.4, line-length 88, select E/F/I/UP) over all 23 edited `.py` files: **All checks passed.**

### The full host suite — run despite the plan's deferral, and why

The plan instructed that the full suite be deferred to plan 12's phase gate, on the ground that the porcelain-asserting modules go red against the D-11-mandated uncommitted state. **That reason is real and was reproduced**: research's F7 names 9 such modules (deferred item D2 measured 7 by grep), and against the real dirty tree **11 legs fail, every one of them the trailing `assert _git_porcelain(FW_ROOT) == ""`** — 5 in `test_sdp_table_parity.py`/`test_dispatch_mirror.py`, 2 in `test_cap03_ack_layout_parity.py`, 2 in `test_json_key_parity.py`, 1 each in `test_py32_asset_name_host.py` and `test_py32_flash_map_host.py`. Plan 12's ordering is therefore a **requirement**, not a preference: run before both commits land, the suite reports 11 sweep-dirt failures that would mask a real one.

But the orchestrator assigned D7 to this plan, and D7 is only *demonstrably* fixed by observing the suite. So the suite was run in a clean clone, per plans 06-10's technique — both repos `git clone --shared --no-hardlinks`, working-tree diffs and untracked files overlaid, committed onto a throwaway branch (fw `797bb93`, app `4344b76`), both porcelains empty, all 26 touched app blob hashes verified equal to the working tree, and both sibling symlinks created (plan 09's caveat: the technique manufactures 6 topology failures without them).

| Run | Result |
|---|---|
| Clean clone, both repos' swept blobs committed | **1976 passed / 0 failed / 0 skipped** |
| Real D-11-dirty tree | **1965 passed / 11 failed = 1976** |

Arithmetic against plan 09's baseline closes exactly:

- Total: `1975 + 1` (leg 5 added) `= 1976` ✓
- Dirty-tree passed: `1963 + 1` (D7 fixed) `+ 1` (leg 5) `= 1965` ✓
- Dirty-tree failed: `12 − 1` (D7) `= 11` ✓
- **`test_diagnostic_range_unchanged_with_phase_151_comment` appears in neither failure list — it no longer exists, and its replacement passes.**

One improvement on plan 09's clone run worth recording: it reported **3 skips** (meta-repo-artifact skips for `.planning/` JSON files absent from the clone). Symlinking `/workspaces/.planning` into the scratch root removed them, so those 3 legs **ran and passed** rather than skipping — hence 1976/0/0 rather than 1973/0/3.

### `uno` byte-identity cross-check

```bash
cd /workspaces/firestarter && rm -rf .pio/build/uno && pio run -e uno
```

| Artifact | Measured | Plans 01/06/07/08/09 |
|---|---|---|
| `.elf` sha256 | `1cfa946f486e041ce5264fc75742ee11e2b437041eaee178ab4d164cbb31ecca` | identical |
| `.hex` sha256 | `be6e4ac80a70e251e2c263beb4109f9f7f9852a034b1064a5dbc8dbbcf05c095` | identical |
| Flash | 26026 | identical |
| RAM | 1575 | identical |

Expected — this plan touched zero firmware files — but a cheap positive proof that neither the sweep nor the D7 planted-violation ceremony wrote into the firmware repo. (Artifacts are `.pio/build/uno/firestarter_uno.{elf,hex}`, not `firmware.{elf,hex}`; and `pio` crashes if cwd is `/workspaces`, per deferred item D1.)

---

## 9. Gate-safety checks run BEFORE editing

Hard boundary #2 says a gate may pin comment text via `inspect.getsource()` or a raw read, and plan 09 broke this once. Checked before touching anything in `tests`:

| Check | Result |
|---|---|
| Modules under `tests/` that read a **test module's** source text | 2 found. `test_dfu_opcode_anchors.py` reads `test_py32_dfu.py` (0 hits, not edited). `test_skip_census.py` reads **itself** — its `test_no_pinned_skip_count` is a *negative* check over its own source, and its only hit is ID-first, so it was not edited; a deletion-only sweep cannot add a match anyway. |
| `test_lockable_proms_doc_claims.py`'s whole-tree `rglob("*.py")` scan | Searches for a forbidden phrase. This plan only removes text, so it cannot introduce an offender. Module green in the suite. |
| Blob-sha pins over any fixture this plan swept | None. `test_json_key_parity.py`'s `hash-object` calls all target `FW_ROOT`; `test_check_no_log_in_sdp_window.py` pins no hash. |
| `serial_comm.py:455-581` host no-touch region (plan 09) | Untouched — that is a **package** file, outside this plan's scope entirely. `test_serial_comm.py` (the test module, edited here) is not the pinned source; `test_read_and_parse_lines_ringfence_unchanged` digests `inspect.getsource(SerialCommunicator._read_and_parse_lines)`. Module 44/44. |
| Exact-line-number pins over `tests/` (the D6 class) | None found in the app repo. D6's `_C14_CONSUMER_SITES` census is firmware-repo-side. All 63 edits preserve line counts exactly (insertions == deletions per file), so a line-shifting pin could not have been tripped regardless. |

Every edit was applied by an exact-old-line-match script (bottom-up per file, the house technique) that **refuses to run** on any mismatch — it caught one wrong indent guess in `test_consistency_check.py:545` and aborted with the actual line before anything was written.

---

## 10. Deviations from Plan

### Orchestrator-assigned task beyond the plan's written scope

**Task 3 (the D7 retarget) is not in `154-11-PLAN.md`.** It was assigned by the execute-phase orchestrator, which correctly identified that plan 09 named plan 11's file as the place D7 must be fixed and that plan 12's phase gate cannot run until it is. Recorded here explicitly so it does not read as unexplained drift. It is the only change in this plan to executable code, and it is excluded from §6a's invariance oracle with that exclusion stated.

### Auto-fixed issues

**1. [Rule 3 - Blocking] The plan's Task-1 automated verify leg measures plan 03's diff, not this plan's**
- **Found during:** Task 1 verification.
- **Issue:** `git -C firestarter_app diff -U0 -- tests | … | grep -vc …` must equal 0. It reports **346** (and 18 docstring lines), all of it plan 03's uncommitted 442-insertion diff to two modules in the same pathspec. The leg as written can never pass in this wave and measures the wrong plan.
- **Fix:** re-scoped to this plan's 25 explicit paths, where it reports **4** (the two documented trailing-comment-on-code pairs) and **0** docstring lines. Both the confounded number and the scoped one are reported so a reader can see why. Same class as plan 10's corrected leg.
- **Files modified:** none (verification only).

**2. [Rule 1 - Bug] The first C/C++ invariance oracle reported 3 false FAILs**
- **Found during:** Task 1 verification.
- **Issue:** reusing this repo's offset-preserving `_strip_comments` idiom for a *digest* is wrong — it replaces a comment span with same-shape whitespace, so shortening a comment changes the space run left behind and the hash moves even though no code did. All 3 fixtures reported FAIL.
- **Fix:** collapse every whitespace run to a single space after stripping, so comment length cannot leak into the hash; re-proven non-vacuous against 3 controls before being trusted. 3 of 3 then identical.
- **Files modified:** none (verification only).

### Deliberate deviations (process, not plan content)

- **The full host suite WAS run**, against the plan's instruction to defer it — see §8 for the reasoning and for the deferral's own justification, which is reproduced and confirmed rather than dismissed.
- **`154-PATTERNS.md`'s suggested reword of `scan_paths.py` was deliberately NOT performed** — see §3.
- **No commit in either sub-repo.** D-11 reserves exactly one commit per sub-repo for plan 12. `firestarter_app` now carries exactly **56** modified tracked paths — plan 03's 2 + plan 09's 20 + plan 10's 8 + this plan's 26, with **no overlap** (this plan edited neither `test_dispatch_mirror.py` nor `test_sdp_table_parity.py`) — plus its 7 pre-existing untracked files and plan 03's 4 fixtures. `firestarter` still carries exactly **93** modified paths, unchanged by this plan.

---

## 11. Issues Encountered

None beyond the two auto-fixed oracle defects in §10. `wip/v1.33-size-reduction-survey-preserved` @ `a6b46f8` untouched. No `git clean`, `git stash`, `reset --hard`, force-push or branch deletion at any point; the two throwaway clones were created outside both repos and deleted after use.

---

## 12. What plan 12 needs from this

1. **D7 is resolved.** The phase gate is unblocked. Plan 12 should expect **1976** legs (not 1975 — leg 5 was added) and, after both commits land, **1976 passed / 0 failed**. The 11 porcelain reds are the sweep's own dirt and will clear on commit; plan 12 must not run the gate before committing.
2. **SWEEP-04 is discharged** and ticked here — this was the second and last test group. **SWEEP-03 is phase-wide and left Pending** for plan 12, as is SWEEP-01/02.
3. **The app repo's commit must include `tests/test_parse_gate_admission.py`.** It is not a sweep file; it is the D7 fix, and the phase gate depends on it.
4. **Deferred item D7 has been marked RESOLVED** in `deferred-items.md`, with the retarget and its proofs recorded there in brief.
5. Deferred items **D2** (the porcelain-module count) and **D8** (mid-comment / docstring populations) both gain host-test-side numbers from §6d: 155 → 175 mid-comment lines and 721 → 719 non-comment-line occurrences within the swept files. Neither is swept; both are recorded, matching plans 07/09/10's call.

---

## 13. User Setup Required

None.

---

## Self-Check: PASSED

- `.planning/phases/154-.../154-11-SUMMARY.md` — FOUND (this file).
- `survey_provenance.py --group app-tests` re-run at write time: **84 hits / 40 files** — matches every figure quoted above.
- `git -C firestarter_app diff --quiet -- tests/scan_paths.py` → exit 0 — re-confirmed.
- `git -C firestarter_app diff --quiet -- tests/fixtures/planted_sdp_comment_{misanchor,brace}.cpp tests/fixtures/planted_dispatch_{comment_only_hex,missing_hex}.cpp` → exit 0 — re-confirmed.
- `grep -roE 'D-[0-9]+' tests | wc -l` → **1536** — re-confirmed equal to the pre-task count.
- `pytest tests/test_parse_gate_admission.py` → **5 passed** — re-confirmed.
- No commit exists in either sub-repo from this plan (`git -C firestarter_app log --oneline -1` unchanged at `6bfa645`; `git -C firestarter log --oneline -1` unchanged at `8695ee5`) — D-11 honoured.
