---
phase: 159-citation-remap-milestone-close
plan: "03"
subsystem: infra
tags: [citation-remap, checkpoint, human-review, jsonl, ledger]

requires:
  - phase: 159-citation-remap-milestone-close
    provides: "159-02 exception ledger (515 pending records), review packet, corpus overlay (2 pending authorizations)"
provides:
  - "Complete decision for all 515 pending stable record IDs in 159-remap-exceptions.jsonl -- disposition, chosen endpoint(s)/text(s), rationale, evidence per ID"
  - "Both corpus-overlay authorizations settled: auth-cobs-relocation -> authorize_include, auth-state-md-dirty -> preserve_unstaged"
  - "Named real-diff shrink case satisfying ROADMAP criterion 3 (range citation shrink, both endpoints verbatim)"
  - "Three named blockers for Plan 159-04 (engine-coverage gap, defective historical-anchor candidate set, missing RETIRED disposition/Outcome)"
affects: [159-04, 159-05, 159-06]

tech-stack:
  added: []
  patterns:
    - "Mechanized, fail-closed triage: verbatim byte-exact oracle first, then diff-provenance (explicit non-verbatim flag), then target-identity de-duplication, then individual full-file search -- never approximate, never guess, retire rather than invent"

key-files:
  created: []
  modified: []

key-decisions:
  - "Research/plan floor counts (5 known_post154_non_survivor, 105 ordinary_original_non_survivor, 110 review floor) are honored as FLOORS; the measured ledger (515 pending, 4 classifications, 3 review_kinds) is authoritative, per this plan's own critical-phase constraint."
  - "candidate_evidence.retarget_new_line/text for hand_choice_re_deletion rows is the STALE Phase-154-era anchor location, not a current-tree suggestion -- verified by direct git show at both the Phase-154 anchor and the live final tree; true current locations independently re-derived by full-file text search."
  - "The verbatim mechanical-pass oracle excludes punctuation-only/whitespace-only recorded text (the brace floor) from claiming a MATCH; diff-provenance records making no match claim at all keep a low_information_target flag instead of being excluded, since an honest low-precision decision is preferable to leaving the record undecided."
  - "Duplicate citations sharing an identical recorded (target_line, target_line_end) share an identical remapped endpoint even when _associate()'s record<->span ATTRIBUTION is ambiguous -- attribution ambiguity does not propagate into endpoint ambiguity."
  - "149 records were retired as citation_absent_from_citing_document, distinct from every sweep-provenance retire cause: the citing planning document was hand-edited after Phase 154 and no longer contains any citation to the recorded target at all. Phase 159 remaps citations that exist; it does not resurrect ones a later edit deleted."

requirements-completed: [REMAP-01, REMAP-02, REMAP-03, REMAP-04, REMAP-05]

duration: not reliably measurable (multi-round interactive checkpoint with operator; no wall-clock instrumentation)
completed: 2026-08-24
status: complete
---

# Phase 159 Plan 03: Citation Remap Review Checkpoint Summary

**Every one of the 515 pending stable record IDs in `159-remap-exceptions.jsonl`, and both pending `159-corpus-overlay.json` authorizations, now carry a complete, evidence-backed decision -- reached through a mechanized, fail-closed triage (verbatim byte-exact match, then diff-provenance with an explicit non-verbatim flag, then duplicate-target-identity resolution, then individual full-file search) with zero fabricated endpoints and zero mutation of the corpus, ledger, or any citing document.**

## Performance

- **Duration:** not reliably measurable (see frontmatter)
- **Tasks:** 1 completed (the plan's single blocking checkpoint)
- **Files modified:** 1 (this SUMMARY.md -- the only file this plan is permitted to write)

## Disposition Tally

515 pending records + 2 pending overlay authorizations, fully decided:

| Disposition | Count | Description |
|---|---|---|
| `historical_anchor_corrected` | 4 | Historical anchor corrected (evidence-defect fix, verbatim both ends) |
| `hand_choice_retargeted_verbatim` | 16 | Phase-154 hand-choice re-targeted, verbatim full-file match |
| `mechanical_oracle_pass` | 1 | Mechanical oracle pass (engine clamp, byte-exact match, non-trivial text) |
| `verbatim_unique_fullfile` | 9 | Verbatim, unique full-file text match (engine clamp guessed wrong coordinate) |
| `range_shrunk_verbatim_endpoints` | 26 | Range shrunk, both endpoints verbatim-verified (ROADMAP criterion 3) |
| `diff_provenance_reworded` | 269 | Diff-provenance only (Phase-154 sweep reworded the cited text; verbatim oracle did not apply) |
| `duplicate_citation_shared_endpoint` | 18 | Duplicate citation, attribution ambiguous but endpoint shared/invariant |
| `retired` | 172 | Retired -- no rewrite target (see retire_cause) |
| **Total** | **515** | |

Of the 269 `diff_provenance_reworded` records, **129** total records across the whole decision set (not only diff-provenance) carry `low_information_target: true` -- the live text at the chosen endpoint (start or end) is punctuation-only or whitespace-only. These are honest, diff-evidenced decisions, not verbatim-match claims; the flag lets a future reader filter them without re-deriving the distinction.

### Retired -- breakdown by cause (172 total)

| retire_cause | Count | Meaning |
|---|---|---|
| `citation_absent_from_citing_document` | 149 | Citation absent from citing document (living-document hand-edit deleted it; NOT sweep provenance) |
| `could_not_be_relocated` | 12 | Could not be relocated (no unique/valid successor found by any mechanical method) |
| `target_file_never_resolved` | 9 | Target file never resolved (manifest-build-time basename resolution failure) |
| `moved_with_semantic_change` | 1 | Moved across files with a semantic change (remap must not follow meaning) |
| `ambiguous_generic_text` | 1 | Ambiguous generic text (no semantic payload to disambiguate) |
| **Total** | **172** | |

## Overlap auth-cobs-relocation

- **current_path:** `.planning/v1.33/v1.9-COBS-DECISION.md`
- **original path:** `.planning/v1.9-COBS-DECISION.md` (deleted, tracked)
- **reviewed pre-apply SHA-256:** `4216e5f54bd83101698637454336b790eafaccd64843284744557863e2780ac1` (both preapply and expected_postapply -- bytes unchanged, pure relocation)
- **git_state:** `1 .D N... 100644 100644 000000 5e29993f... .planning/v1.9-COBS-DECISION.md` / `? .planning/v1.33/v1.9-COBS-DECISION.md`
- **topology_action:** relocated (deleted old path, added untracked new path)
- **decision:** `authorize_include`
- **staging strategy:** include this specific relocation (delete of the old tracked path, add of the new untracked path) in the Phase-159 production commit, so that any citation retargeting to `.planning/v1.33/v1.9-COBS-DECISION.md` lands against a committed file rather than an untracked one.
- **scope of authorization:** this one relocation only. No other untracked or modified path is authorized by this decision.
- **rationale:** Operator decision. Per PLAN.md, `preserve_unstaged` is not valid for a relocation (only for a `citation_only_blob`); the only remaining options were `authorize_include` or `stop`. Bytes are unchanged (preapply == expected_postapply), so inclusion carries no content risk -- only a topology change.

## Overlap auth-state-md-dirty

- **current_path:** `.planning/STATE.md`
- **reviewed pre-apply SHA-256:** `e866ab7ad7840e69931b4af62709c33ce9e5a69537c6c5abd24eda14bba8d71f`
- **git_state:** `1 .M N... 100644 100644 100644 b118a339... .planning/STATE.md`
- **topology_action:** modified in place (this phase's own execution bookkeeping)
- **decision:** `preserve_unstaged`
- **staging strategy:** `citation_only_blob` -- if `STATE.md` contains any citation Plan 159-04/05 would otherwise rewrite, only the citation-span hunks may be staged via index-object surgery; STATE.md's own bookkeeping edits must never enter the Phase-159 commit.
- **scope of authorization:** STATE.md only; no other file.
- **rationale:** Not a free choice -- settled by `159-06-PLAN.md:143` ("Do not stage STATE") and `159-06-PLAN.md:146` (asserts `sha256(.planning/STATE.md)` equals the preserved dirty hash). STATE.md must stay byte-identical for the remainder of the phase.

## Named Real-Diff Shrink Case (ROADMAP criterion 3)

**Requirement:** "a range citation has BOTH endpoints mapped, and a range spanning a deleted block is SHRUNK, not translated," proven on a real case from this milestone's own diff, not only on Phase-154's synthetic fixtures.

**Case:** `eprom_operations.cpp`, 13-member duplicate class (`orig-3884437ce9f0bccb`, `orig-64123a6b28cdbe09`, and 11 `late-*` records), citing `.planning/REQUIREMENTS.md:52` and 12 other planning locations, disposition `range_shrunk_verbatim_endpoints`.

- **Old range** (pre-sweep `8695ee52c27a4bee4387c5c489afd5f3d7275e8a`): **lines 57-67** (11 lines)
  - start text: `// LOCK-01/LOCK-02: standalone entry points for CMD_SDP_UNLOCK / CMD_SDP_LOCK`
  - end text: `// load-bearing (mirrors eprom_erase/eprom_blank_check above).`
- **New range** (live final tree): **lines 57-63** (7 lines) -- shrunk by 4 lines, NOT translated
  - start text (verbatim, unchanged): `// LOCK-01/LOCK-02: standalone entry points for CMD_SDP_UNLOCK / CMD_SDP_LOCK`
  - end text (verbatim, new terminus): `// no SDP analogue; D-06's op-layer NULL-main guard (Plan 119-07) is what`
- **What was deleted:** the comment's closing justification sentence ("...refuses these commands on a protocol whose handler set no main. Each body is exactly op_execute_simple_operation's single-step shape; op_execute_simple_operation returns true when FINISHED, so the `!` inversion here is load-bearing...") was removed, alongside a real code change: `eprom_sdp_unlock`/`eprom_sdp_lock` changed `return !op_execute_simple_operation(handle);` to `return op_execute_simple_operation(handle);` (the `!` inversion dropped).
- **Method:** both endpoints were verbatim-verified directly against both git blobs (`git show 8695ee52:src/eprom_operations.cpp` and the live working tree), not merely trusted from the engine's own clamp -- though in this case the engine's clamp (`resolve_with_review`'s natural `RETARGET` outcome) independently agreed with the manual verification.

## Method Note -- Class-B Blank-Line Self-Catch

While locating shrunk-range end boundaries (the `range_shrunk_verbatim_endpoints` disposition), the first implementation of the backward verbatim search matched blank lines and bare `{`/`}`/`,`/`;` characters as if they were real evidence -- e.g. it initially claimed three `json_parser.c` classes all "ended" at line 78 purely because that line happened to be blank in both the old and new text. This was caught before being reported and fixed by excluding content-free lines (blank, or stripped to one of `{`, `}`, `,`, `;`) from counting as valid backward-search evidence, mirroring the same floor applied to the mechanical verbatim-match oracle (the "brace floor"). All `range_shrunk_verbatim_endpoints` decisions in this SUMMARY reflect the corrected, content-bearing-only search. This is recorded here so the endpoint floor is auditable rather than silently assumed.

## Finding -- 149 Citations Deleted by Hand-Editing (not sweep provenance)

149 manifest citations (disposition `retired`, cause `citation_absent_from_citing_document`) were deleted from their citing documents by ordinary hand-editing of `.planning/` files between the Phase-154 sweep and now -- not by the Phase-154 comment sweep itself. The clearest example: `orig-02fd18603dd6a4b4` recorded a citation to `memory.cpp:337` at `.planning/PROJECT.md:495`; that line today reads "remainder are not in v1.30's scope and will present again at close." -- entirely different prose, no citation of any kind. This is a real, measured fact about `.planning/` hygiene: living documents (`PROJECT.md`, `ROADMAP.md`, `REQUIREMENTS.md`, `baseline-pre-sweep.md`, etc.) continue to be hand-edited after a sweep captures a citation manifest, and citations embedded in prose that later gets rewritten or trimmed do not survive that edit. This is out of scope for Phase 159 to prevent going forward, but the volume (149 out of 515, ~29% of the pending set) is large enough to be worth surfacing as a standalone measurement, not folded into the sweep-provenance findings.

## Blockers for Plan 159-04

### 1. Engine-coverage gap -- 21 approvals will be inert without an additive fix

Only 494 of the original 515 pending rows are reachable by `remap_citations.py`'s live `needs_review` reporting path. The other 21 -- 17 of the 18 original `hand_choice_re_deletion` rows (all `retarget: true`) plus all 4 `historical_anchor` rows -- are intercepted **before** the exceptions ledger is ever consulted:

- `retarget: true` rows hit the unconditional `FLAGGED_RETARGET` short-circuit in `remap_document`'s inner loop (`~line 1013`: "is flagged retarget in the manifest -- hand-chosen target, left exactly as written (D-08)") regardless of ledger status.
- The 4 `historical_anchor` rows hit the "no line map exists; skipped" branch (`~line 1032-1038`) before `decide()` is ever called, because their (file, source_sha) pair never produced a `LineMap`.

**Precondition on Plan 159-04's contract:** "apply these decisions mechanically by stable ID" does not currently hold for these 21 IDs (the 16 `hand_choice_retargeted_verbatim` + 2 `retired` Class-2 records already resolved by ID, plus the 4 `historical_anchor_corrected` records in this SUMMARY are all in this set). Plan 159-04 must add a code path that consults the reviewed ledger for `retarget: true` rows and for rows whose `LineMap` never resolved, before those approvals can take effect. Until then, approving them (as this SUMMARY does) is necessary but not sufficient.

### 2. `prepare_citation_remap.py`'s `anchor_record()` never offers the pre-sweep SHA as a candidate

All 4 `historical_anchor` records offered exactly the same defective 2-candidate set (`2ad5b322`, `2ccda8d43` -- both post-Phase-154 commits) for a citation whose recorded line (`61`) exists in **neither** candidate (`eprom_params.cpp` is only 58 lines at both). The correct anchor (pre-sweep `8695ee52`, where line 61 reads the pre-sweep text verbatim) was never offered. `anchor_record()` needs a third candidate tier -- the root's pre-sweep SHA -- before this class of finding can resolve without a manual bypass like the one applied here (`chosen_current_start`/`text` supplied directly, `chosen_source_sha` left unset).

### 3. No terminal `RETIRED` disposition/Outcome exists in the ledger or engine

172 records in this SUMMARY are disposed `retired` (5 distinct causes: `citation_absent_from_citing_document`, `could_not_be_relocated`, `target_file_never_resolved`, `moved_with_semantic_change`, `ambiguous_generic_text`), but neither `159-remap-exceptions.jsonl`'s schema nor `remap_citations.py`'s `Outcome` set has a representation for "a human decided this citation has no rewrite target and should not be touched." **Minimal additive design proposed (not implemented -- 159-04 owns it):**

- Ledger: add `status: "retired"` (alongside the existing `needs_review`/`reviewed`) plus a required `retire_cause` field constrained to a known enum (at minimum the 5 causes named above, extensible).
- Engine: add a terminal `RETIRED` `Outcome` that `resolve_with_review` returns whenever `entry.get("status") == "retired"`; `remap_document` must treat `RETIRED` as an explicit no-op/no-rewrite -- never entering `violations`, never entering `open_ids["needs_review"]`, and never blocking `--apply`.
- The `retire_cause` must be surfaced in `--report-json` (e.g. `retired_by_cause: {cause: count}`) so a future reader can distinguish sweep-provenance retirements from living-document-drift retirements from manifest-resolution-failure retirements without re-deriving this SUMMARY.

## Decisions

One `## Decision <record_id>` per pending stable record ID, grouped by disposition. Each class opens with a shared preamble (the common evidence/method); every individual entry still carries its own chosen endpoint(s), text(s), and rationale, per the plan's requirement that repeated semantic decisions may be reviewed together only if every stable record ID retains an individual decision.

### Class: `historical_anchor_corrected` (4 records)

#### Decision late-1dab9164ab57c0b4

- review_kind: `historical_anchor` | classification: `ambiguous_historical_anchor`
- disposition: `historical_anchor_corrected`
- chosen endpoint: start=57
- chosen text: `/* Fail closed: a null pointer with zero hardware side effects, never &EPROM_PARAMS[0]. */`
- rationale: Recorded target eprom_params.cpp:61 is unreadable at both offered candidate SHAs (2ad5b322, 2ccda8d43 -- both blobs are only 58 lines). The correct historical anchor is pre-sweep 8695ee52, never offered as a candidate by prepare_citation_remap.py's anchor_record() (logged as a Blocker for 159-04). At 8695ee52, line 61 reads 'return NULL; /* D-05: fail closed, zero hardware side effects -- never &EPROM_PARAMS[0] */' -- the Phase-154 sweep reflowed this exact sentence (dropping the D-05 label) to current final-tree line 57, independently corroborated by 154-VERIFICATION.md naming eprom_params.cpp:61 among its five keep-reflowed spot-checks.
- evidence: git show 8695ee52:src/proms/eprom_params.cpp (line 61) and live firestarter/src/proms/eprom_params.cpp (line 57); 154-VERIFICATION.md:30/32

#### Decision late-82ea6775d37bf8d7

- review_kind: `historical_anchor` | classification: `ambiguous_historical_anchor`
- disposition: `historical_anchor_corrected`
- chosen endpoint: start=57
- chosen text: `/* Fail closed: a null pointer with zero hardware side effects, never &EPROM_PARAMS[0]. */`
- rationale: Recorded target eprom_params.cpp:61 is unreadable at both offered candidate SHAs (2ad5b322, 2ccda8d43 -- both blobs are only 58 lines). The correct historical anchor is pre-sweep 8695ee52, never offered as a candidate by prepare_citation_remap.py's anchor_record() (logged as a Blocker for 159-04). At 8695ee52, line 61 reads 'return NULL; /* D-05: fail closed, zero hardware side effects -- never &EPROM_PARAMS[0] */' -- the Phase-154 sweep reflowed this exact sentence (dropping the D-05 label) to current final-tree line 57, independently corroborated by 154-VERIFICATION.md naming eprom_params.cpp:61 among its five keep-reflowed spot-checks.
- evidence: git show 8695ee52:src/proms/eprom_params.cpp (line 61) and live firestarter/src/proms/eprom_params.cpp (line 57); 154-VERIFICATION.md:30/32

#### Decision late-936b7d3f18742a33

- review_kind: `historical_anchor` | classification: `ambiguous_historical_anchor`
- disposition: `historical_anchor_corrected`
- chosen endpoint: start=57
- chosen text: `/* Fail closed: a null pointer with zero hardware side effects, never &EPROM_PARAMS[0]. */`
- rationale: Recorded target eprom_params.cpp:61 is unreadable at both offered candidate SHAs (2ad5b322, 2ccda8d43 -- both blobs are only 58 lines). The correct historical anchor is pre-sweep 8695ee52, never offered as a candidate by prepare_citation_remap.py's anchor_record() (logged as a Blocker for 159-04). At 8695ee52, line 61 reads 'return NULL; /* D-05: fail closed, zero hardware side effects -- never &EPROM_PARAMS[0] */' -- the Phase-154 sweep reflowed this exact sentence (dropping the D-05 label) to current final-tree line 57, independently corroborated by 154-VERIFICATION.md naming eprom_params.cpp:61 among its five keep-reflowed spot-checks.
- evidence: git show 8695ee52:src/proms/eprom_params.cpp (line 61) and live firestarter/src/proms/eprom_params.cpp (line 57); 154-VERIFICATION.md:30/32

#### Decision late-eb8e1eb7d526c0ca

- review_kind: `historical_anchor` | classification: `ambiguous_historical_anchor`
- disposition: `historical_anchor_corrected`
- chosen endpoint: start=57
- chosen text: `/* Fail closed: a null pointer with zero hardware side effects, never &EPROM_PARAMS[0]. */`
- rationale: Recorded target eprom_params.cpp:61 is unreadable at both offered candidate SHAs (2ad5b322, 2ccda8d43 -- both blobs are only 58 lines). The correct historical anchor is pre-sweep 8695ee52, never offered as a candidate by prepare_citation_remap.py's anchor_record() (logged as a Blocker for 159-04). At 8695ee52, line 61 reads 'return NULL; /* D-05: fail closed, zero hardware side effects -- never &EPROM_PARAMS[0] */' -- the Phase-154 sweep reflowed this exact sentence (dropping the D-05 label) to current final-tree line 57, independently corroborated by 154-VERIFICATION.md naming eprom_params.cpp:61 among its five keep-reflowed spot-checks.
- evidence: git show 8695ee52:src/proms/eprom_params.cpp (line 61) and live firestarter/src/proms/eprom_params.cpp (line 57); 154-VERIFICATION.md:30/32

### Class: `hand_choice_retargeted_verbatim` (16 records)

#### Decision orig-0eb49bddb82f80bd

- review_kind: `hand_choice_re_deletion` | classification: `known_post154_non_survivor`
- disposition: `hand_choice_retargeted_verbatim`
- chosen endpoint: start=97
- chosen text: `uint8_t flash_util_read_in_id_mode(firestarter_handle_t* handle, uint32_t address) {`
- rationale: candidate_evidence.retarget_new_line/text in the ledger is a verbatim echo of the original Phase-154 hand choice (valid at anchor 2ad5b322), not a current-tree suggestion -- independently re-located by exact text search in the live final tree.
- evidence: live grep -n confirms this exact text at line 97

#### Decision orig-1e6ee3305909e56a

- review_kind: `hand_choice_re_deletion` | classification: `known_post154_non_survivor`
- disposition: `hand_choice_retargeted_verbatim`
- chosen endpoint: start=67
- chosen text: `const char key_pulse_delay[] PROGMEM = "pulse-delay";`
- rationale: candidate_evidence.retarget_new_line/text in the ledger is a verbatim echo of the original Phase-154 hand choice (valid at anchor 2ad5b322), not a current-tree suggestion -- independently re-located by exact text search in the live final tree.
- evidence: live grep -n confirms this exact text at firestarter/src/json_parser.c:67

#### Decision orig-214cda407793d3db

- review_kind: `hand_choice_re_deletion` | classification: `known_post154_non_survivor`
- disposition: `hand_choice_retargeted_verbatim`
- chosen endpoint: start=67
- chosen text: `const char key_pulse_delay[] PROGMEM = "pulse-delay";`
- rationale: candidate_evidence.retarget_new_line/text in the ledger is a verbatim echo of the original Phase-154 hand choice (valid at anchor 2ad5b322), not a current-tree suggestion -- independently re-located by exact text search in the live final tree.
- evidence: live grep -n confirms this exact text at firestarter/src/json_parser.c:67

#### Decision orig-29f50ca7f611e0fc

- review_kind: `hand_choice_re_deletion` | classification: `known_post154_non_survivor`
- disposition: `hand_choice_retargeted_verbatim`
- chosen endpoint: start=133
- chosen text: `static const field_desc_t key_parsers[] PROGMEM = {`
- rationale: candidate_evidence.retarget_new_line/text in the ledger is a verbatim echo of the original Phase-154 hand choice (valid at anchor 2ad5b322), not a current-tree suggestion -- independently re-located by exact text search in the live final tree. NOTE (operator ruling): the symbol key_parsers survives; only the element type name changed (key_parser_t -> field_desc_t). Phase 159 remaps LINE NUMBERS, not prose -- if citing prose quotes the old type name, that prose is independently stale and out of scope for this phase. No citing document was edited.
- evidence: live grep -n confirms this exact text at firestarter/src/json_parser.c:133

#### Decision orig-303acb1f4af0883e

- review_kind: `hand_choice_re_deletion` | classification: `known_post154_non_survivor`
- disposition: `hand_choice_retargeted_verbatim`
- chosen endpoint: start=91
- chosen text: `typedef struct {`
- rationale: candidate_evidence.retarget_new_line/text in the ledger is a verbatim echo of the original Phase-154 hand choice (valid at anchor 2ad5b322), not a current-tree suggestion -- independently re-located by exact text search in the live final tree.
- evidence: live grep -n confirms this exact text at firestarter/src/json_parser.c:91

#### Decision orig-40632f5a559925b0

- review_kind: `hand_choice_re_deletion` | classification: `known_post154_non_survivor`
- disposition: `hand_choice_retargeted_verbatim`
- chosen endpoint: start=67
- chosen text: `const char key_pulse_delay[] PROGMEM = "pulse-delay";`
- rationale: candidate_evidence.retarget_new_line/text in the ledger is a verbatim echo of the original Phase-154 hand choice (valid at anchor 2ad5b322), not a current-tree suggestion -- independently re-located by exact text search in the live final tree.
- evidence: live grep -n confirms this exact text at firestarter/src/json_parser.c:67

#### Decision orig-4cbc623d02cc680e

- review_kind: `hand_choice_re_deletion` | classification: `known_post154_non_survivor`
- disposition: `hand_choice_retargeted_verbatim`
- chosen endpoint: start=67
- chosen text: `const char key_pulse_delay[] PROGMEM = "pulse-delay";`
- rationale: candidate_evidence.retarget_new_line/text in the ledger is a verbatim echo of the original Phase-154 hand choice (valid at anchor 2ad5b322), not a current-tree suggestion -- independently re-located by exact text search in the live final tree.
- evidence: live grep -n confirms this exact text at firestarter/src/json_parser.c:67

#### Decision orig-6325169ed64d49d8

- review_kind: `hand_choice_re_deletion` | classification: `known_post154_non_survivor`
- disposition: `hand_choice_retargeted_verbatim`
- chosen endpoint: start=67
- chosen text: `const char key_pulse_delay[] PROGMEM = "pulse-delay";`
- rationale: candidate_evidence.retarget_new_line/text in the ledger is a verbatim echo of the original Phase-154 hand choice (valid at anchor 2ad5b322), not a current-tree suggestion -- independently re-located by exact text search in the live final tree.
- evidence: live grep -n confirms this exact text at firestarter/src/json_parser.c:67

#### Decision orig-7542217df234e7e0

- review_kind: `hand_choice_re_deletion` | classification: `known_post154_non_survivor`
- disposition: `hand_choice_retargeted_verbatim`
- chosen endpoint: start=67
- chosen text: `const char key_pulse_delay[] PROGMEM = "pulse-delay";`
- rationale: candidate_evidence.retarget_new_line/text in the ledger is a verbatim echo of the original Phase-154 hand choice (valid at anchor 2ad5b322), not a current-tree suggestion -- independently re-located by exact text search in the live final tree.
- evidence: live grep -n confirms this exact text at firestarter/src/json_parser.c:67

#### Decision orig-a7ffdf6434491d29

- review_kind: `hand_choice_re_deletion` | classification: `known_post154_non_survivor`
- disposition: `hand_choice_retargeted_verbatim`
- chosen endpoint: start=67
- chosen text: `const char key_pulse_delay[] PROGMEM = "pulse-delay";`
- rationale: candidate_evidence.retarget_new_line/text in the ledger is a verbatim echo of the original Phase-154 hand choice (valid at anchor 2ad5b322), not a current-tree suggestion -- independently re-located by exact text search in the live final tree.
- evidence: live grep -n confirms this exact text at firestarter/src/json_parser.c:67

#### Decision orig-a92b85b282f633b1

- review_kind: `hand_choice_re_deletion` | classification: `known_post154_non_survivor`
- disposition: `hand_choice_retargeted_verbatim`
- chosen endpoint: start=60
- chosen text: `#define READ_TIMING_MAX_US 1000UL   /* T-44-01 sane max (~1ms); caps both knobs */`
- rationale: candidate_evidence.retarget_new_line/text in the ledger is a verbatim echo of the original Phase-154 hand choice (valid at anchor 2ad5b322), not a current-tree suggestion -- independently re-located by exact text search in the live final tree.
- evidence: live grep -n confirms this exact text at firestarter/src/json_parser.c:60

#### Decision orig-abcc91d3aed1883a

- review_kind: `hand_choice_re_deletion` | classification: `known_post154_non_survivor`
- disposition: `hand_choice_retargeted_verbatim`
- chosen endpoint: start=91
- chosen text: `typedef struct {`
- rationale: candidate_evidence.retarget_new_line/text in the ledger is a verbatim echo of the original Phase-154 hand choice (valid at anchor 2ad5b322), not a current-tree suggestion -- independently re-located by exact text search in the live final tree.
- evidence: live grep -n confirms this exact text at firestarter/src/json_parser.c:91

#### Decision orig-cf5a087e6b8c4eab

- review_kind: `hand_choice_re_deletion` | classification: `known_post154_non_survivor`
- disposition: `hand_choice_retargeted_verbatim`
- chosen endpoint: start=91
- chosen text: `typedef struct {`
- rationale: candidate_evidence.retarget_new_line/text in the ledger is a verbatim echo of the original Phase-154 hand choice (valid at anchor 2ad5b322), not a current-tree suggestion -- independently re-located by exact text search in the live final tree.
- evidence: live grep -n confirms this exact text at firestarter/src/json_parser.c:91

#### Decision orig-d584cfda9de9543a

- review_kind: `hand_choice_re_deletion` | classification: `known_post154_non_survivor`
- disposition: `hand_choice_retargeted_verbatim`
- chosen endpoint: start=133
- chosen text: `static const field_desc_t key_parsers[] PROGMEM = {`
- rationale: candidate_evidence.retarget_new_line/text in the ledger is a verbatim echo of the original Phase-154 hand choice (valid at anchor 2ad5b322), not a current-tree suggestion -- independently re-located by exact text search in the live final tree. NOTE (operator ruling): the symbol key_parsers survives; only the element type name changed (key_parser_t -> field_desc_t). Phase 159 remaps LINE NUMBERS, not prose -- if citing prose quotes the old type name, that prose is independently stale and out of scope for this phase. No citing document was edited.
- evidence: live grep -n confirms this exact text at firestarter/src/json_parser.c:133

#### Decision orig-e1d266b1f531c966

- review_kind: `hand_choice_re_deletion` | classification: `known_post154_non_survivor`
- disposition: `hand_choice_retargeted_verbatim`
- chosen endpoint: start=67
- chosen text: `const char key_pulse_delay[] PROGMEM = "pulse-delay";`
- rationale: candidate_evidence.retarget_new_line/text in the ledger is a verbatim echo of the original Phase-154 hand choice (valid at anchor 2ad5b322), not a current-tree suggestion -- independently re-located by exact text search in the live final tree.
- evidence: live grep -n confirms this exact text at firestarter/src/json_parser.c:67

#### Decision orig-e50a58e645c133ee

- review_kind: `hand_choice_re_deletion` | classification: `known_post154_non_survivor`
- disposition: `hand_choice_retargeted_verbatim`
- chosen endpoint: start=67
- chosen text: `const char key_pulse_delay[] PROGMEM = "pulse-delay";`
- rationale: candidate_evidence.retarget_new_line/text in the ledger is a verbatim echo of the original Phase-154 hand choice (valid at anchor 2ad5b322), not a current-tree suggestion -- independently re-located by exact text search in the live final tree.
- evidence: live grep -n confirms this exact text at firestarter/src/json_parser.c:67

### Class: `mechanical_oracle_pass` (1 records)

#### Decision late-f6b577d1070b08d1

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `mechanical_oracle_pass`
- chosen endpoint: start=565, end=586
- chosen text: `def test_clean_native_both_envs_pass():` .. ``
- rationale: Engine's own LineMap-computed clamp, verified byte-exact against the recorded manifest source_text[/_end] -- the strict mechanical oracle passing outright.
- evidence: engine clamp at firestarter/tests/test_check_size_baseline.py:565, verbatim match

### Class: `verbatim_unique_fullfile` (9 records)

#### Decision late-05328595afcb9f23

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `verbatim_unique_fullfile`
- chosen endpoint: start=47
- chosen text: ` * an absurd JSON value cannot pass an unbounded value to delayMicroseconds()`
- rationale: Engine's difflib clamp guessed the wrong coordinate, but a full-file exact-text search finds this record's recorded text exactly once elsewhere in the same target file -- unambiguous.
- evidence: full-file grep of firestarter/src/json_parser.c for the recorded source_text: exactly 1 hit

#### Decision late-1811de672eb79f6c

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `verbatim_unique_fullfile`
- chosen endpoint: start=47
- chosen text: ` * an absurd JSON value cannot pass an unbounded value to delayMicroseconds()`
- rationale: Engine's difflib clamp guessed the wrong coordinate, but a full-file exact-text search finds this record's recorded text exactly once elsewhere in the same target file -- unambiguous.
- evidence: full-file grep of firestarter/src/json_parser.c for the recorded source_text: exactly 1 hit

#### Decision late-2036867d4785cfd6

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `verbatim_unique_fullfile`
- chosen endpoint: start=60
- chosen text: `#define READ_TIMING_MAX_US 1000UL   /* T-44-01 sane max (~1ms); caps both knobs */`
- rationale: Engine's difflib clamp guessed the wrong coordinate, but a full-file exact-text search finds this record's recorded text exactly once elsewhere in the same target file -- unambiguous.
- evidence: full-file grep of firestarter/src/json_parser.c for the recorded source_text: exactly 1 hit

#### Decision late-52fbdd2c7d2b97fa

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `verbatim_unique_fullfile`
- chosen endpoint: start=60
- chosen text: `#define READ_TIMING_MAX_US 1000UL   /* T-44-01 sane max (~1ms); caps both knobs */`
- rationale: Engine's difflib clamp guessed the wrong coordinate, but a full-file exact-text search finds this record's recorded text exactly once elsewhere in the same target file -- unambiguous.
- evidence: full-file grep of firestarter/src/json_parser.c for the recorded source_text: exactly 1 hit

#### Decision late-b4978cb85d0b6c4a

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `verbatim_unique_fullfile`
- chosen endpoint: start=44
- chosen text: ` * Read-timing sweep knobs.`
- rationale: Full-file verbatim search (content-bearing text only) found exactly one occurrence of the recorded source_text[/_end] in the live target file, independent of the engine's own (non-viable) clamp.
- evidence: firestarter/src/json_parser.c: exactly 1 content-bearing verbatim hit

#### Decision late-db7274529d9e2cbe

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `verbatim_unique_fullfile`
- chosen endpoint: start=47
- chosen text: ` * an absurd JSON value cannot pass an unbounded value to delayMicroseconds()`
- rationale: Engine's difflib clamp guessed the wrong coordinate, but a full-file exact-text search finds this record's recorded text exactly once elsewhere in the same target file -- unambiguous.
- evidence: full-file grep of firestarter/src/json_parser.c for the recorded source_text: exactly 1 hit

#### Decision late-eba06b3387d9c52a

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `verbatim_unique_fullfile`
- chosen endpoint: start=47
- chosen text: ` * an absurd JSON value cannot pass an unbounded value to delayMicroseconds()`
- rationale: Engine's difflib clamp guessed the wrong coordinate, but a full-file exact-text search finds this record's recorded text exactly once elsewhere in the same target file -- unambiguous.
- evidence: full-file grep of firestarter/src/json_parser.c for the recorded source_text: exactly 1 hit

#### Decision late-fc1ecacd45ab5311

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `verbatim_unique_fullfile`
- chosen endpoint: start=60
- chosen text: `#define READ_TIMING_MAX_US 1000UL   /* T-44-01 sane max (~1ms); caps both knobs */`
- rationale: Engine's difflib clamp guessed the wrong coordinate, but a full-file exact-text search finds this record's recorded text exactly once elsewhere in the same target file -- unambiguous.
- evidence: full-file grep of firestarter/src/json_parser.c for the recorded source_text: exactly 1 hit

#### Decision orig-02ff8e53f66c0819

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `verbatim_unique_fullfile`
- chosen endpoint: start=47
- chosen text: ` * an absurd JSON value cannot pass an unbounded value to delayMicroseconds()`
- rationale: Engine's difflib clamp guessed the wrong coordinate, but a full-file exact-text search finds this record's recorded text exactly once elsewhere in the same target file -- unambiguous.
- evidence: full-file grep of firestarter/src/json_parser.c for the recorded source_text: exactly 1 hit

### Class: `range_shrunk_verbatim_endpoints` (26 records)

#### Decision late-05852a7bfa0dafe4

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=149, end=152
- chosen text: `CHECKER_GLOB = "check_*.py"` .. `# future checker addition must raise these in the same commit.`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 125-130 -> new range 149-152. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/tests/test_checker_convention.py: start and end independently verbatim-verified against sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 and the live tree

#### Decision late-0a79406e72e05a43

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=57, end=63
- chosen text: `// LOCK-01/LOCK-02: standalone entry points for CMD_SDP_UNLOCK / CMD_SDP_LOCK` .. `// no SDP analogue; D-06's op-layer NULL-main guard (Plan 119-07) is what`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 57-67 -> new range 57-63. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/eprom_operations.cpp: start and end independently verbatim-verified against sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a and the live tree

#### Decision late-1b7c9909a7221204

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=39, end=44
- chosen text: `    if (vpp_mv > (uint32_t)handle->vpp_mv + 500) {` .. `    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 39-77 -> new range 39-44. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/proms/flash_intel.cpp: start and end independently verbatim-verified against sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 and the live tree

#### Decision late-37f7847209cea9d4

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=73, end=92
- chosen text: `/* Per-chip page-write size delivered by the host.` .. `    PGM_P key;`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 62-76 -> new range 73-92. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/json_parser.c: start and end independently verbatim-verified against sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 and the live tree

#### Decision late-3c2eef4dad98c503

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=57, end=63
- chosen text: `// LOCK-01/LOCK-02: standalone entry points for CMD_SDP_UNLOCK / CMD_SDP_LOCK` .. `// no SDP analogue; D-06's op-layer NULL-main guard (Plan 119-07) is what`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 57-67 -> new range 57-63. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/eprom_operations.cpp: start and end independently verbatim-verified against sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a and the live tree

#### Decision late-40f875363f45c2b7

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=57, end=63
- chosen text: `// LOCK-01/LOCK-02: standalone entry points for CMD_SDP_UNLOCK / CMD_SDP_LOCK` .. `// no SDP analogue; D-06's op-layer NULL-main guard (Plan 119-07) is what`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 57-67 -> new range 57-63. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/eprom_operations.cpp: start and end independently verbatim-verified against sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a and the live tree

#### Decision late-4cc3be08c5e35ea9

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=57, end=63
- chosen text: `// LOCK-01/LOCK-02: standalone entry points for CMD_SDP_UNLOCK / CMD_SDP_LOCK` .. `// no SDP analogue; D-06's op-layer NULL-main guard (Plan 119-07) is what`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 57-67 -> new range 57-63. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/eprom_operations.cpp: start and end independently verbatim-verified against sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a and the live tree

#### Decision late-50af2a05f23392d0

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=57, end=63
- chosen text: `// LOCK-01/LOCK-02: standalone entry points for CMD_SDP_UNLOCK / CMD_SDP_LOCK` .. `// no SDP analogue; D-06's op-layer NULL-main guard (Plan 119-07) is what`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 57-67 -> new range 57-63. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/eprom_operations.cpp: start and end independently verbatim-verified against sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a and the live tree

#### Decision late-80da39f38d7c3fc1

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=57, end=63
- chosen text: `// LOCK-01/LOCK-02: standalone entry points for CMD_SDP_UNLOCK / CMD_SDP_LOCK` .. `// no SDP analogue; D-06's op-layer NULL-main guard (Plan 119-07) is what`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 57-67 -> new range 57-63. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/eprom_operations.cpp: start and end independently verbatim-verified against sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a and the live tree

#### Decision late-993b40b75b29de13

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=1833, end=1839
- chosen text: `/* Case 30 -- ERASE-01 / 152-CONTEXT.md D-07. Built from` .. ` * stream. `mem_util_blank_check` is the ONLY setter of`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 1770-1778 -> new range 1833-1839. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp: start and end independently verbatim-verified against sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 and the live tree

#### Decision late-abf44e25bdf34960

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=57, end=63
- chosen text: `// LOCK-01/LOCK-02: standalone entry points for CMD_SDP_UNLOCK / CMD_SDP_LOCK` .. `// no SDP analogue; D-06's op-layer NULL-main guard (Plan 119-07) is what`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 57-67 -> new range 57-63. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/eprom_operations.cpp: start and end independently verbatim-verified against sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a and the live tree

#### Decision late-abff4b496dff3bea

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=713, end=718
- chosen text: `    if (vpp_mv > (uint32_t)handle->vpp_mv + 500) {` .. `    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 713-743 -> new range 713-718. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/proms/eprom.cpp: start and end independently verbatim-verified against sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 and the live tree

#### Decision late-ac9c3bc172704bc4

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=26, end=44
- chosen text: `static void flash_intel_check_vpp(firestarter_handle_t* handle) {` .. `    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 26-70 -> new range 26-44. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/proms/flash_intel.cpp: start and end independently verbatim-verified against sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 and the live tree

#### Decision late-b2ae675ff8d780e8

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=316, end=318
- chosen text: `/* Case (ERASE-02): with FLAG_SKIP_BLANK_CHECK and FLAG_CAN_ERASE both clear,` .. ` * pointer (not by function name, so this exercises what configure_memory`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 317-325 -> new range 316-318. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp: start and end independently verbatim-verified against sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 and the live tree

#### Decision late-b8b74b30eb85dc2c

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=57, end=63
- chosen text: `// LOCK-01/LOCK-02: standalone entry points for CMD_SDP_UNLOCK / CMD_SDP_LOCK` .. `// no SDP analogue; D-06's op-layer NULL-main guard (Plan 119-07) is what`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 57-67 -> new range 57-63. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/eprom_operations.cpp: start and end independently verbatim-verified against sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a and the live tree

#### Decision late-cda981ae60cc6b1c

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=57, end=63
- chosen text: `// LOCK-01/LOCK-02: standalone entry points for CMD_SDP_UNLOCK / CMD_SDP_LOCK` .. `// no SDP analogue; D-06's op-layer NULL-main guard (Plan 119-07) is what`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 57-67 -> new range 57-63. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/eprom_operations.cpp: start and end independently verbatim-verified against sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a and the live tree

#### Decision late-d2fb0e44f1fc2bca

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=57, end=63
- chosen text: `// LOCK-01/LOCK-02: standalone entry points for CMD_SDP_UNLOCK / CMD_SDP_LOCK` .. `// no SDP analogue; D-06's op-layer NULL-main guard (Plan 119-07) is what`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 57-67 -> new range 57-63. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/eprom_operations.cpp: start and end independently verbatim-verified against sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a and the live tree

#### Decision late-dfa012d6edb605fc

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=57, end=63
- chosen text: `// LOCK-01/LOCK-02: standalone entry points for CMD_SDP_UNLOCK / CMD_SDP_LOCK` .. `// no SDP analogue; D-06's op-layer NULL-main guard (Plan 119-07) is what`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 57-67 -> new range 57-63. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/eprom_operations.cpp: start and end independently verbatim-verified against sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a and the live tree

#### Decision orig-1e41f358b54a202f

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=34, end=38
- chosen text: `bool eprom_erase(firestarter_handle_t* handle) {` .. `        return true;`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 34-40 -> new range 34-38. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/eprom_operations.cpp: start and end independently verbatim-verified against sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a and the live tree

#### Decision orig-3884437ce9f0bccb

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=57, end=63
- chosen text: `// LOCK-01/LOCK-02: standalone entry points for CMD_SDP_UNLOCK / CMD_SDP_LOCK` .. `// no SDP analogue; D-06's op-layer NULL-main guard (Plan 119-07) is what`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 57-67 -> new range 57-63. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/eprom_operations.cpp: start and end independently verbatim-verified against sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a and the live tree

#### Decision orig-43a1ba4b6ccc36d6

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=66, end=92
- chosen text: `const char key_pin_count[] PROGMEM = "pin-count";` .. `    PGM_P key;`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 55-130 -> new range 66-92. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/json_parser.c: start and end independently verbatim-verified against sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a and the live tree

#### Decision orig-64123a6b28cdbe09

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=57, end=63
- chosen text: `// LOCK-01/LOCK-02: standalone entry points for CMD_SDP_UNLOCK / CMD_SDP_LOCK` .. `// no SDP analogue; D-06's op-layer NULL-main guard (Plan 119-07) is what`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 57-67 -> new range 57-63. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/eprom_operations.cpp: start and end independently verbatim-verified against sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a and the live tree

#### Decision orig-8d0488859ab43a87

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=67, end=92
- chosen text: `const char key_pulse_delay[] PROGMEM = "pulse-delay";` .. `    PGM_P key;`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 56-75 -> new range 67-92. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/json_parser.c: start and end independently verbatim-verified against sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a and the live tree

#### Decision orig-e59e36ce963979d8

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=466, end=497
- chosen text: `        strncmp_P(json + tok->start, s, tok->end - tok->start) == 0) {` .. `bool get_flags(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 279-298 -> new range 466-497. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/json_parser.c: start and end independently verbatim-verified against sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a and the live tree

#### Decision orig-e8e9ce3e3bd6ade9

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=34, end=38
- chosen text: `bool eprom_erase(firestarter_handle_t* handle) {` .. `        return true;`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 34-40 -> new range 34-38. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/eprom_operations.cpp: start and end independently verbatim-verified against sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a and the live tree

#### Decision orig-f175c072762d8822

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `range_shrunk_verbatim_endpoints`
- chosen endpoint: start=34, end=38
- chosen text: `bool eprom_erase(firestarter_handle_t* handle) {` .. `        return true;`
- rationale: ROADMAP criterion 3: a range citation has both endpoints mapped; a range spanning a deleted block is SHRUNK, not translated. Old range 34-40 -> new range 34-38. Start located by unique full-file text match; end located by backward verbatim search from the old range's end, excluding blank/punctuation-only lines as valid evidence (self-caught during Round 3).
- evidence: firestarter/src/eprom_operations.cpp: start and end independently verbatim-verified against sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a and the live tree

### Class: `diff_provenance_reworded` (269 records)

#### Decision late-018734abcc8db9b1

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=58
- chosen text: ` */`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/operation_utils.cpp, hunk: @@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)'

#### Decision late-0301630e552fcf43

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=170
- chosen text: `        # one write block. The firmware ALREADY pads this figure -- only it`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/serial_comm.py, hunk: @@ -167,18 +167,18 @@ class SerialCommunicator:
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -167,18 +167,18 @@ class SerialCommunicator:'

#### Decision late-0526bf23fea3c930

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=265
- chosen text: `// Read addresses are derived from mem_size: AT28C256 = 0x7FC0/0x7FC1,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eeprom_28c.cpp, hunk: @@ -262,5 +262,5 @@ void configure_eeprom28c(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -262,5 +262,5 @@ void configure_eeprom28c(firestarter_handle_t* handle) {'

#### Decision late-06808d9f9b08bb49

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=351
- chosen text: `    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp, hunk: @@ -337,8 +338,15 @@ void test_5v_page_write_init_no_blank_check_with_flag_clear_erase02(void) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -337,8 +338,15 @@ void test_5v_page_write_init_no_blank_check_with_flag_clear_erase02(void) {'

#### Decision late-06ed834d4151842f

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=73
- chosen text: ` */`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/include/operation_utils.h, hunk: @@ -70,5 +70,5 @@ static inline bool is_operation_waiting_for_data(const firestarter_handle_t* han
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -70,5 +70,5 @@ static inline bool is_operation_waiting_for_data(const firestarter_handle_t* han'

#### Decision late-09144bf22008d90b

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1469
- chosen text: ` * for the callback parameter is safe: the NULL-main guard at`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp, hunk: @@ -1409,5 +1466,5 @@ void test_case23_standalone_unlock_matches_auto_unlock_stream(void) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -1409,5 +1466,5 @@ void test_case23_standalone_unlock_matches_auto_unlock_stream(void) {'

#### Decision late-09a64d32c9b69832

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=502
- chosen text: `        handle->address = 0;`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/memory.cpp, hunk: @@ -404,18 +497,12 @@ void uint32_to_bytes(char* buffer, int pos, uint32_t value) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -404,18 +497,12 @@ void uint32_to_bytes(char* buffer, int pos, uint32_t value) {'

#### Decision late-09f55a8a69f9aad2

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=44
- chosen text: `    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/flash_intel.cpp, hunk: @@ -38,44 +38,10 @@ static void flash_intel_check_vpp(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -38,44 +38,10 @@ static void flash_intel_check_vpp(firestarter_handle_t* handle) {'

#### Decision late-0a4731d81c1f2cc2

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=73
- chosen text: ` */`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/include/operation_utils.h, hunk: @@ -70,5 +70,5 @@ static inline bool is_operation_waiting_for_data(const firestarter_handle_t* han
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -70,5 +70,5 @@ static inline bool is_operation_waiting_for_data(const firestarter_handle_t* han'

#### Decision late-0a4809e3e59f6afb

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=81
- chosen text: `# section header the doc's own text calls "§3".`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/tests/test_py32_packaging.py, hunk: @@ -78,9 +78,9 @@ _FLASH_METHOD_DEF = "def flash_method("
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -78,9 +78,9 @@ _FLASH_METHOD_DEF = "def flash_method("'

#### Decision late-0af1e28818f27c14

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=351, end=339
- chosen text: `    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,` .. `        "left a multi-call INIT loop pending");`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp, hunk: @@ -337,8 +338,15 @@ void test_5v_page_write_init_no_blank_check_with_flag_clear_erase02(void) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -337,8 +338,15 @@ void test_5v_page_write_init_no_blank_check_with_flag_clear_erase02(void) {'

#### Decision late-0cafddedc056e120

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=489
- chosen text: ``
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/memory.cpp, hunk: @@ -391,7 +459,32 @@ uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -391,7 +459,32 @@ uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t'

#### Decision late-0cffafc1a99b1cdf

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=488
- chosen text: `    _ELECTRICAL_TYPE_LABEL = {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/ic_layout.py, hunk: @@ -482,11 +479,11 @@ class EpromSpecBuilder:
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -482,11 +479,11 @@ class EpromSpecBuilder:'

#### Decision late-0d07c096868adff5

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=100
- chosen text: `        return None`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/tools/parse_devtest_issue.py, hunk: @@ -97,5 +97,5 @@ def _extract_fenced_report(body: str | None) -> dict[str, Any] | None:
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -97,5 +97,5 @@ def _extract_fenced_report(body: str | None) -> dict[str, Any] | None:'

#### Decision late-0fb2574f86a57389

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=75
- chosen text: `# mismatched board cannot wedge the host -- it is not a defense against an`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/serial_comm.py, hunk: @@ -72,5 +72,5 @@ DEFAULT_RESPONSE_TIMEOUT = 10  # seconds for waiting for a specific response
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -72,5 +72,5 @@ DEFAULT_RESPONSE_TIMEOUT = 10  # seconds for waiting for a specific response'

#### Decision late-1050346ee048a62e

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1024
- chosen text: `# argparse-form mutex/validator tests that imported `create_firmware_args``
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/tests/test_firmware_install.py, hunk: @@ -1021,5 +1021,5 @@ class TestMagicDefault:
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -1021,5 +1021,5 @@ class TestMagicDefault:'

#### Decision late-122f28ce5f04d84c

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=265
- chosen text: `// Read addresses are derived from mem_size: AT28C256 = 0x7FC0/0x7FC1,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eeprom_28c.cpp, hunk: @@ -262,5 +262,5 @@ void configure_eeprom28c(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -262,5 +262,5 @@ void configure_eeprom28c(firestarter_handle_t* handle) {'

#### Decision late-148c414f2cf9e1c6

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=265
- chosen text: `// Read addresses are derived from mem_size: AT28C256 = 0x7FC0/0x7FC1,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eeprom_28c.cpp, hunk: @@ -262,5 +262,5 @@ void configure_eeprom28c(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -262,5 +262,5 @@ void configure_eeprom28c(firestarter_handle_t* handle) {'

#### Decision late-15946f9d7ab4f065

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=56, end=58
- chosen text: `"""` .. `from __future__ import annotations`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/tests/meta_presence.py, hunk: @@ -46,10 +46,12 @@ process's environment -- never an in-process monkeypatch, never a direct
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header="@@ -46,10 +46,12 @@ process's environment -- never an in-process monkeypatch, never a direct"

#### Decision late-16ed104a84a4e4ca

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=292
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eeprom_28c.cpp, hunk: @@ -289,20 +289,5 @@ static void eeprom28c_check_chip_id(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -289,20 +289,5 @@ static void eeprom28c_check_chip_id(firestarter_handle_t* handle) {'

#### Decision late-17f677cd83bfcb62

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=265
- chosen text: `// Read addresses are derived from mem_size: AT28C256 = 0x7FC0/0x7FC1,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eeprom_28c.cpp, hunk: @@ -262,5 +262,5 @@ void configure_eeprom28c(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -262,5 +262,5 @@ void configure_eeprom28c(firestarter_handle_t* handle) {'

#### Decision late-19f4bda3b38de373

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=351
- chosen text: `    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp, hunk: @@ -337,8 +338,15 @@ void test_5v_page_write_init_no_blank_check_with_flag_clear_erase02(void) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -337,8 +338,15 @@ void test_5v_page_write_init_no_blank_check_with_flag_clear_erase02(void) {'

#### Decision late-1a9d88d4ffa1c7df

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=58
- chosen text: ` */`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/operation_utils.cpp, hunk: @@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)'

#### Decision late-1c88f1b5ed8d4da0

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=233
- chosen text: `# flash-map figure and pyusb floor must not be able to disagree with the`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/tests/test_py32_packaging.py, hunk: @@ -230,5 +230,5 @@ def test_d17_gate_fails_closed_on_a_planted_file_lacking_the_record(
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -230,5 +230,5 @@ def test_d17_gate_fails_closed_on_a_planted_file_lacking_the_record('

#### Decision late-1cc027b72421a869

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=58
- chosen text: ` */`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/operation_utils.cpp, hunk: @@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)'

#### Decision late-1eb970f8169d1d32

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=44
- chosen text: `    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/flash_intel.cpp, hunk: @@ -38,44 +38,10 @@ static void flash_intel_check_vpp(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -38,44 +38,10 @@ static void flash_intel_check_vpp(firestarter_handle_t* handle) {'

#### Decision late-200d033a8148022e

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=283
- chosen text: `# ---------------------------------------------------------------------------`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/chip_test.py, hunk: @@ -280,5 +280,5 @@ def classify_fingerprint(
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -280,5 +280,5 @@ def classify_fingerprint('

#### Decision late-205aad7fd24710fe

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=314
- chosen text: ``
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/tools/build_db.py, hunk: @@ -311,5 +311,5 @@ def resolve_pinout_key(
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -311,5 +311,5 @@ def resolve_pinout_key('

#### Decision late-21f92de4a6340843

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=489
- chosen text: ``
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/memory.cpp, hunk: @@ -391,7 +459,32 @@ uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -391,7 +459,32 @@ uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t'

#### Decision late-2571d9edcab5fafd

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=107
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/flash_utils.cpp, hunk: @@ -103,17 +104,4 @@ uint8_t flash_util_read_in_id_mode(firestarter_handle_t* handle, uint32_t addres
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -103,17 +104,4 @@ uint8_t flash_util_read_in_id_mode(firestarter_handle_t* handle, uint32_t addres'

#### Decision late-274c85ca4e7cfcab

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=58
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/eprom_params.cpp, hunk: @@ -59,4 +55,4 @@ const eprom_params_t* eprom_params_for(uint32_t protocol) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -59,4 +55,4 @@ const eprom_params_t* eprom_params_for(uint32_t protocol) {'

#### Decision late-2968bcc62f3a9e49

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=58
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/eprom_params.cpp, hunk: @@ -59,4 +55,4 @@ const eprom_params_t* eprom_params_for(uint32_t protocol) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -59,4 +55,4 @@ const eprom_params_t* eprom_params_for(uint32_t protocol) {'

#### Decision late-2969c623b7340e56

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=318
- chosen text: `                token_idx += 2; // Skip key and simple value`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/json_parser.c, hunk: @@ -126,6 +315,5 @@ int json_parse(const char* json, jsmntok_t* tokens, int token_count, firestarter
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -126,6 +315,5 @@ int json_parse(const char* json, jsmntok_t* tokens, int token_count, firestarter'

#### Decision late-2f948571484c34ca

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=108
- chosen text: `    rurp_set_programmer_mode();`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/dev_tools.cpp, hunk: @@ -105,5 +105,5 @@ bool dt_set_registers(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -105,5 +105,5 @@ bool dt_set_registers(firestarter_handle_t* handle) {'

#### Decision late-3019564423a5362e

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=56, end=58
- chosen text: `"""` .. `from __future__ import annotations`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/tests/meta_presence.py, hunk: @@ -46,10 +46,12 @@ process's environment -- never an in-process monkeypatch, never a direct
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header="@@ -46,10 +46,12 @@ process's environment -- never an in-process monkeypatch, never a direct"

#### Decision late-31872b9fd314835e

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=288
- chosen text: ``
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/tools/build_db.py, hunk: @@ -285,5 +285,5 @@ def resolve_pinout_key(
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -285,5 +285,5 @@ def resolve_pinout_key('

#### Decision late-334008af0c7511f3

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=240, end=236
- chosen text: `static firestarter_handle_t make_write_init_handle_blank_check_enabled(void) {` .. ` * conditional's guard would have been satisfied. mem_size is a small 2048 --`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp, hunk: @@ -235,8 +235,7 @@ static firestarter_handle_t make_write_handle_with_data(void) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -235,8 +235,7 @@ static firestarter_handle_t make_write_handle_with_data(void) {'

#### Decision late-335c9e533614538b

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=122, end=64
- chosen text: `}` .. `    // Vin_mV = (voltage_adc_reading * 1100 * (R1 + R2)) / (bandgap_adc_reading * R2)`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/boards/rurp_common.cpp, hunk: @@ -62,11 +62,62 @@ uint16_t rurp_read_voltage_mv() {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -62,11 +62,62 @@ uint16_t rurp_read_voltage_mv() {'

#### Decision late-33c6e50d9db8849c

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1215
- chosen text: `# write_eprom, both ack directions plus the flag-not-set case, and the`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/tests/test_eprom_operations.py, hunk: @@ -1212,5 +1212,5 @@ class TestSdpOperationsWireShape:
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -1212,5 +1212,5 @@ class TestSdpOperationsWireShape:'

#### Decision late-3656c94d8524d325

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=173
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/operation_utils.cpp, hunk: @@ -162,5 +170,5 @@ bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -162,5 +170,5 @@ bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle'

#### Decision late-3bce1da55233bce8

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=718
- chosen text: `    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eprom.cpp, hunk: @@ -712,44 +712,10 @@ void eprom_check_vpp(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -712,44 +712,10 @@ void eprom_check_vpp(firestarter_handle_t* handle) {'

#### Decision late-3bf547b143bf9c2e

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=217
- chosen text: `            break;`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/memory.cpp, hunk: @@ -210,5 +214,5 @@ rurp_register_t mem_util_calculate_top_address_register(firestarter_handle_t* ha
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -210,5 +214,5 @@ rurp_register_t mem_util_calculate_top_address_register(firestarter_handle_t* ha'

#### Decision late-3d6536717c7270d1

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=103
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/flash_5v_page.cpp, hunk: @@ -99,7 +98,7 @@ void flash_5v_page_write_init(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -99,7 +98,7 @@ void flash_5v_page_write_init(firestarter_handle_t* handle) {'

#### Decision late-3dd4df9cfddc1ed4

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=58
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/eprom_params.cpp, hunk: @@ -59,4 +55,4 @@ const eprom_params_t* eprom_params_for(uint32_t protocol) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -59,4 +55,4 @@ const eprom_params_t* eprom_params_for(uint32_t protocol) {'

#### Decision late-3e81f0eeb5cceb95

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1487
- chosen text: `    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp, hunk: @@ -1422,10 +1479,10 @@ void test_case24_null_main_refusal_emits_not_supported_and_error_response(void)
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -1422,10 +1479,10 @@ void test_case24_null_main_refusal_emits_not_supported_and_error_response(void)'

#### Decision late-3eee31e1fb4b15e6

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=265
- chosen text: `// Read addresses are derived from mem_size: AT28C256 = 0x7FC0/0x7FC1,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eeprom_28c.cpp, hunk: @@ -262,5 +262,5 @@ void configure_eeprom28c(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -262,5 +262,5 @@ void configure_eeprom28c(firestarter_handle_t* handle) {'

#### Decision late-40a48d843d46d655

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=489, end=460
- chosen text: `` .. ``
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/memory.cpp, hunk: @@ -391,7 +459,32 @@ uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -391,7 +459,32 @@ uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t'

#### Decision late-445b8963fbd66302

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=489
- chosen text: ``
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/memory.cpp, hunk: @@ -391,7 +459,32 @@ uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -391,7 +459,32 @@ uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t'

#### Decision late-454a4b365a9ae2bf

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=46
- chosen text: `    }`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/flash_intel.cpp, hunk: @@ -38,44 +38,10 @@ static void flash_intel_check_vpp(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -38,44 +38,10 @@ static void flash_intel_check_vpp(firestarter_handle_t* handle) {'

#### Decision late-482d75a7b755c20c

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=81
- chosen text: `# short, distinctive fragment of the hypothetical warning this project`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/tests/test_write_skip_erase_0x0d.py, hunk: @@ -78,5 +78,5 @@ _SKIP_ERASE_WARNING = "has nothing to skip on this chip's protocol"
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -78,5 +78,5 @@ _SKIP_ERASE_WARNING = "has nothing to skip on this chip\'s protocol"'

#### Decision late-4a78f952b8e3cabd

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=720
- chosen text: `    }`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eprom.cpp, hunk: @@ -712,44 +712,10 @@ void eprom_check_vpp(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -712,44 +712,10 @@ void eprom_check_vpp(firestarter_handle_t* handle) {'

#### Decision late-4adf90acb999a078

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=581, end=620
- chosen text: `        #` .. `        # this bit (`serial_comm.py`'s `_log_command_details`) is DEBUG-only`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/database.py, hunk: @@ -568,69 +568,60 @@ class EpromDatabase:
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -568,69 +568,60 @@ class EpromDatabase:'

#### Decision late-4d40b8dc53924b4c

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164, end=275
- chosen text: `};` .. `    handle->bus_config.rw_line = 0xFF;`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision late-4e5c21d51dd82e1d

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=718
- chosen text: `    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eprom.cpp, hunk: @@ -712,44 +712,10 @@ void eprom_check_vpp(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -712,44 +712,10 @@ void eprom_check_vpp(firestarter_handle_t* handle) {'

#### Decision late-4e8529dba9905060

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=166, end=159
- chosen text: `    // RESPONSE_CODE_ERROR instead of the RESPONSE_CODE_OK loop() set: the` .. `    //`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/operation_utils.cpp, hunk: @@ -152,8 +158,10 @@ bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -152,8 +158,10 @@ bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle'

#### Decision late-4ec0de527aedfc80

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=58
- chosen text: ` */`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/operation_utils.cpp, hunk: @@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)'

#### Decision late-4ef352ae85d3f63f

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1469
- chosen text: ` * for the callback parameter is safe: the NULL-main guard at`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp, hunk: @@ -1409,5 +1466,5 @@ void test_case23_standalone_unlock_matches_auto_unlock_stream(void) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -1409,5 +1466,5 @@ void test_case23_standalone_unlock_matches_auto_unlock_stream(void) {'

#### Decision late-50375a5b7ca13a97

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=482
- chosen text: `        # _decode_id_frame MSG_OK_READY ack override in serial_comm.py, not`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/eprom_operations.py, hunk: @@ -479,8 +479,8 @@ class EpromOperator:
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -479,8 +479,8 @@ class EpromOperator:'

#### Decision late-50628884a934fe3a

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=56, end=58
- chosen text: `"""` .. `from __future__ import annotations`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/tests/meta_presence.py, hunk: @@ -46,10 +46,12 @@ process's environment -- never an in-process monkeypatch, never a direct
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header="@@ -46,10 +46,12 @@ process's environment -- never an in-process monkeypatch, never a direct"

#### Decision late-50e361e80bd6b197

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=64, end=64
- chosen text: `    // Vin_mV = (voltage_adc_reading * 1100 * (R1 + R2)) / (bandgap_adc_reading * R2)` .. `    // Vin_mV = (voltage_adc_reading * 1100 * (R1 + R2)) / (bandgap_adc_reading * R2)`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/boards/rurp_common.cpp, hunk: @@ -62,11 +62,62 @@ uint16_t rurp_read_voltage_mv() {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -62,11 +62,62 @@ uint16_t rurp_read_voltage_mv() {'

#### Decision late-51598ca48f2c8acc

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=312
- chosen text: `# shipped database (all 84 qualify -- electrical-type is EEPROM or`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/chip_test.py, hunk: @@ -306,8 +306,8 @@ _PROTOCOL_FLASH4 = 0x05
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -306,8 +306,8 @@ _PROTOCOL_FLASH4 = 0x05'

#### Decision late-51c35641fae5a02c

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=605
- chosen text: `        #`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/database.py, hunk: @@ -568,69 +568,60 @@ class EpromDatabase:
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -568,69 +568,60 @@ class EpromDatabase:'

#### Decision late-53ae75314eedd63f

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=107
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/flash_utils.cpp, hunk: @@ -103,17 +104,4 @@ uint8_t flash_util_read_in_id_mode(firestarter_handle_t* handle, uint32_t addres
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -103,17 +104,4 @@ uint8_t flash_util_read_in_id_mode(firestarter_handle_t* handle, uint32_t addres'

#### Decision late-561d0f1505f9c135

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=240
- chosen text: `static firestarter_handle_t make_write_init_handle_blank_check_enabled(void) {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp, hunk: @@ -235,8 +235,7 @@ static firestarter_handle_t make_write_handle_with_data(void) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -235,8 +235,7 @@ static firestarter_handle_t make_write_handle_with_data(void) {'

#### Decision late-572e5849738042e5

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=58
- chosen text: ` */`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/operation_utils.cpp, hunk: @@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)'

#### Decision late-5846fa4c41212803

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1487
- chosen text: `    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp, hunk: @@ -1422,10 +1479,10 @@ void test_case24_null_main_refusal_emits_not_supported_and_error_response(void)
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -1422,10 +1479,10 @@ void test_case24_null_main_refusal_emits_not_supported_and_error_response(void)'

#### Decision late-5ad8de708331fabf

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=626
- chosen text: `        simple_flags = 0`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/database.py, hunk: @@ -568,69 +568,60 @@ class EpromDatabase:
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -568,69 +568,60 @@ class EpromDatabase:'

#### Decision late-5babb29b661839d2

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=44
- chosen text: `    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/flash_intel.cpp, hunk: @@ -38,44 +38,10 @@ static void flash_intel_check_vpp(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -38,44 +38,10 @@ static void flash_intel_check_vpp(firestarter_handle_t* handle) {'

#### Decision late-5e381555204eaaa5

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1487
- chosen text: `    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp, hunk: @@ -1422,10 +1479,10 @@ void test_case24_null_main_refusal_emits_not_supported_and_error_response(void)
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -1422,10 +1479,10 @@ void test_case24_null_main_refusal_emits_not_supported_and_error_response(void)'

#### Decision late-5ef7d2125f382d29

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=265
- chosen text: `// Read addresses are derived from mem_size: AT28C256 = 0x7FC0/0x7FC1,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eeprom_28c.cpp, hunk: @@ -262,5 +262,5 @@ void configure_eeprom28c(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -262,5 +262,5 @@ void configure_eeprom28c(firestarter_handle_t* handle) {'

#### Decision late-6173b447b5af6b81

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=488
- chosen text: `    _ELECTRICAL_TYPE_LABEL = {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/ic_layout.py, hunk: @@ -482,11 +479,11 @@ class EpromSpecBuilder:
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -482,11 +479,11 @@ class EpromSpecBuilder:'

#### Decision late-62cb2e4ed1f73b18

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=73
- chosen text: ` */`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/include/operation_utils.h, hunk: @@ -70,5 +70,5 @@ static inline bool is_operation_waiting_for_data(const firestarter_handle_t* han
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -70,5 +70,5 @@ static inline bool is_operation_waiting_for_data(const firestarter_handle_t* han'

#### Decision late-6594218deb9d4c30

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=58
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/eprom_params.cpp, hunk: @@ -59,4 +55,4 @@ const eprom_params_t* eprom_params_for(uint32_t protocol) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -59,4 +55,4 @@ const eprom_params_t* eprom_params_for(uint32_t protocol) {'

#### Decision late-687156c215905b96

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=572, end=620
- chosen text: `        # fragile synthetic `info-flags & 0x10` round-trip injected by _map_data.` .. `        # this bit (`serial_comm.py`'s `_log_command_details`) is DEBUG-only`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/database.py, hunk: @@ -568,69 +568,60 @@ class EpromDatabase:
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -568,69 +568,60 @@ class EpromDatabase:'

#### Decision late-68723a1c0958e99d

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=545
- chosen text: `        # invokes sys.exit(...) at the end of every command, so we catch the`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/tests/test_consistency_check.py, hunk: @@ -542,5 +542,5 @@ class TestDispatchChain:
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -542,5 +542,5 @@ class TestDispatchChain:'

#### Decision late-6a57d215d82990da

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=502
- chosen text: `        handle->address = 0;`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/memory.cpp, hunk: @@ -404,18 +497,12 @@ void uint32_to_bytes(char* buffer, int pos, uint32_t value) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -404,18 +497,12 @@ void uint32_to_bytes(char* buffer, int pos, uint32_t value) {'

#### Decision late-6b3d7659a40bb2df

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=450
- chosen text: `    # silkscreen-string rendering.`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/tests/test_decoder.py, hunk: @@ -447,5 +447,5 @@ class TestIdFrameDecoder:
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -447,5 +447,5 @@ class TestIdFrameDecoder:'

#### Decision late-6e09296439e88e06

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=217
- chosen text: `            break;`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/memory.cpp, hunk: @@ -210,5 +214,5 @@ rurp_register_t mem_util_calculate_top_address_register(firestarter_handle_t* ha
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -210,5 +214,5 @@ rurp_register_t mem_util_calculate_top_address_register(firestarter_handle_t* ha'

#### Decision late-6e301584fb145f89

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=229
- chosen text: `# Proves that the FM1608 SRAM→FRAM relabel (fm-fram-full) and the SST39SF040`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/tests/test_database_conversion.py, hunk: @@ -226,5 +226,5 @@ def test_search_chip_id_returns_list(db: EpromDatabase) -> None:
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -226,5 +226,5 @@ def test_search_chip_id_returns_list(db: EpromDatabase) -> None:'

#### Decision late-70023abe3c43e54b

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=436, end=439
- chosen text: `# `'write_scope="none": ... omitted (D-01)'` shape the shipped write/verify/` .. `# reason it does not own.`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/chip_test.py, hunk: @@ -433,5 +433,5 @@ _SDP_LEG_STEP_ORDER: tuple[str, ...] = (
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -433,5 +433,5 @@ _SDP_LEG_STEP_ORDER: tuple[str, ...] = ('

#### Decision late-732ab91ab6b75b0d

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=126
- chosen text: `_STABLE_RELEASE_UNO328PB = {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/tests/test_firmware_install.py, hunk: @@ -119,9 +119,9 @@ _STABLE_RELEASE_LEONARDO = {
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -119,9 +119,9 @@ _STABLE_RELEASE_LEONARDO = {'

#### Decision late-73396580b16bd2e3

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=292, end=290
- chosen text: `}` .. `    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_A9_ENABLE, 0);`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eeprom_28c.cpp, hunk: @@ -289,20 +289,5 @@ static void eeprom28c_check_chip_id(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -289,20 +289,5 @@ static void eeprom28c_check_chip_id(firestarter_handle_t* handle) {'

#### Decision late-746200e335a3be8e

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1582, end=1590
- chosen text: `    int calls = 0;` .. `        "Case 25 (ERASE-03, mechanism-corrected/intent-satisfied -- never as failed): "`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp, hunk: @@ -1522,18 +1579,24 @@ void test_case25_cmd_erase_on_0x0d_dispatches_and_succeeds_erase03(void) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -1522,18 +1579,24 @@ void test_case25_cmd_erase_on_0x0d_dispatches_and_succeeds_erase03(void) {'

#### Decision late-751f17af05126881

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=151
- chosen text: `        # via the MSG_OK_READY operation-setup ack (2-byte big-endian u16 param).`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/serial_comm.py, hunk: @@ -148,9 +148,9 @@ class SerialCommunicator:
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -148,9 +148,9 @@ class SerialCommunicator:'

#### Decision late-75cdb24cd800200a

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=282
- chosen text: `     * single file-scope global with no per-command memset, and page-size is`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -90,14 +279,13 @@ int json_parse(const char* json, jsmntok_t* tokens, int token_count, firestarter
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -90,14 +279,13 @@ int json_parse(const char* json, jsmntok_t* tokens, int token_count, firestarter'

#### Decision late-763343ca42bac2c7

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=416
- chosen text: `                        # appended AFTER CAP-02's variable-length identity`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/serial_comm.py, hunk: @@ -413,5 +413,5 @@ class SerialCommunicator:
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -413,5 +413,5 @@ class SerialCommunicator:'

#### Decision late-795ca971c98be072

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=106
- chosen text: `void rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count) {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/boards/uno_rurp_shield.cpp, hunk: @@ -104,12 +101,7 @@ void rurp_set_programmer_mode() {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -104,12 +101,7 @@ void rurp_set_programmer_mode() {'

#### Decision late-7a75c35cefbffa5e

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1862
- chosen text: `    sdp_assert_stream_equals(SDP_FIXED_DIP28_28C256, SDP_FIXED_DIP28_28C256_LEN,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp, hunk: @@ -1786,8 +1849,15 @@ void test_case30_write_init_no_blank_check_with_flag_clear_erase01(void) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -1786,8 +1849,15 @@ void test_case30_write_init_no_blank_check_with_flag_clear_erase01(void) {'

#### Decision late-7ac4731da4b9c9b3

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=65, end=63
- chosen text: `bool eprom_sdp_unlock(firestarter_handle_t* handle) {` .. `// no SDP analogue; D-06's op-layer NULL-main guard (Plan 119-07) is what`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/eprom_operations.cpp, hunk: @@ -62,14 +62,11 @@ bool eprom_blank_check(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -62,14 +62,11 @@ bool eprom_blank_check(firestarter_handle_t* handle) {'

#### Decision late-7b83d6627e605f57

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=253
- chosen text: ``
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/tools/build_db.py, hunk: @@ -250,5 +250,5 @@ def resolve_pinout_key(
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -250,5 +250,5 @@ def resolve_pinout_key('

#### Decision late-7bfcba5a61690440

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=108
- chosen text: `    rurp_set_programmer_mode();`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/dev_tools.cpp, hunk: @@ -105,5 +105,5 @@ bool dt_set_registers(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -105,5 +105,5 @@ bool dt_set_registers(firestarter_handle_t* handle) {'

#### Decision late-7c48b00864559caf

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1582, end=1590
- chosen text: `    int calls = 0;` .. `        "Case 25 (ERASE-03, mechanism-corrected/intent-satisfied -- never as failed): "`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp, hunk: @@ -1522,18 +1579,24 @@ void test_case25_cmd_erase_on_0x0d_dispatches_and_succeeds_erase03(void) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -1522,18 +1579,24 @@ void test_case25_cmd_erase_on_0x0d_dispatches_and_succeeds_erase03(void) {'

#### Decision late-7d15cd4fb0b3ccd3

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1469
- chosen text: ` * for the callback parameter is safe: the NULL-main guard at`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp, hunk: @@ -1409,5 +1466,5 @@ void test_case23_standalone_unlock_matches_auto_unlock_stream(void) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -1409,5 +1466,5 @@ void test_case23_standalone_unlock_matches_auto_unlock_stream(void) {'

#### Decision late-7e7304d7781bc7f8

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=502, end=500
- chosen text: `        handle->address = 0;` .. `        set_operation_in_progress(handle);`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/memory.cpp, hunk: @@ -404,18 +497,12 @@ void uint32_to_bytes(char* buffer, int pos, uint32_t value) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -404,18 +497,12 @@ void uint32_to_bytes(char* buffer, int pos, uint32_t value) {'

#### Decision late-7fc06f8a5ea94e5c

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=265
- chosen text: `// Read addresses are derived from mem_size: AT28C256 = 0x7FC0/0x7FC1,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eeprom_28c.cpp, hunk: @@ -262,5 +262,5 @@ void configure_eeprom28c(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -262,5 +262,5 @@ void configure_eeprom28c(firestarter_handle_t* handle) {'

#### Decision late-8084c07e01dfe6bf

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/json_parser.c, hunk: @@ -294,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -294,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision late-8323909ebe817692

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1487
- chosen text: `    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp, hunk: @@ -1422,10 +1479,10 @@ void test_case24_null_main_refusal_emits_not_supported_and_error_response(void)
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -1422,10 +1479,10 @@ void test_case24_null_main_refusal_emits_not_supported_and_error_response(void)'

#### Decision late-84b8645e15e8eaff

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1590
- chosen text: `        "Case 25 (ERASE-03, mechanism-corrected/intent-satisfied -- never as failed): "`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp, hunk: @@ -1522,18 +1579,24 @@ void test_case25_cmd_erase_on_0x0d_dispatches_and_succeeds_erase03(void) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -1522,18 +1579,24 @@ void test_case25_cmd_erase_on_0x0d_dispatches_and_succeeds_erase03(void) {'

#### Decision late-8766471aad490f91

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=776
- chosen text: `    unexplained: list = []`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/tools/diff_db.py, hunk: @@ -773,5 +773,5 @@ def main():
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -773,5 +773,5 @@ def main():'

#### Decision late-87a68667bacf578a

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=58
- chosen text: ` */`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/operation_utils.cpp, hunk: @@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)'

#### Decision late-87ee6ee9c179c22f

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=718
- chosen text: `    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eprom.cpp, hunk: @@ -712,44 +712,10 @@ void eprom_check_vpp(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -712,44 +712,10 @@ void eprom_check_vpp(firestarter_handle_t* handle) {'

#### Decision late-8a0a8ef6b1695266

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=58
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/eprom_params.cpp, hunk: @@ -59,4 +55,4 @@ const eprom_params_t* eprom_params_for(uint32_t protocol) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -59,4 +55,4 @@ const eprom_params_t* eprom_params_for(uint32_t protocol) {'

#### Decision late-8c1e65c3703a0832

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=265
- chosen text: `// Read addresses are derived from mem_size: AT28C256 = 0x7FC0/0x7FC1,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eeprom_28c.cpp, hunk: @@ -262,5 +262,5 @@ void configure_eeprom28c(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -262,5 +262,5 @@ void configure_eeprom28c(firestarter_handle_t* handle) {'

#### Decision late-8d04bdf0789c9f1e

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164, end=275
- chosen text: `};` .. `    handle->bus_config.rw_line = 0xFF;`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision late-8e0ef5e92a1b76c0

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=103
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/flash_5v_page.cpp, hunk: @@ -99,7 +98,7 @@ void flash_5v_page_write_init(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -99,7 +98,7 @@ void flash_5v_page_write_init(firestarter_handle_t* handle) {'

#### Decision late-8edeb551959019c3

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=73
- chosen text: ` */`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/include/operation_utils.h, hunk: @@ -70,5 +70,5 @@ static inline bool is_operation_waiting_for_data(const firestarter_handle_t* han
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -70,5 +70,5 @@ static inline bool is_operation_waiting_for_data(const firestarter_handle_t* han'

#### Decision late-903fc7b7450d6985

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1487
- chosen text: `    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp, hunk: @@ -1422,10 +1479,10 @@ void test_case24_null_main_refusal_emits_not_supported_and_error_response(void)
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -1422,10 +1479,10 @@ void test_case24_null_main_refusal_emits_not_supported_and_error_response(void)'

#### Decision late-91c58d706cd4c0ae

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=581, end=620
- chosen text: `        #` .. `        # this bit (`serial_comm.py`'s `_log_command_details`) is DEBUG-only`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/database.py, hunk: @@ -568,69 +568,60 @@ class EpromDatabase:
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -568,69 +568,60 @@ class EpromDatabase:'

#### Decision late-9216696a4394548e

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1487
- chosen text: `    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp, hunk: @@ -1422,10 +1479,10 @@ void test_case24_null_main_refusal_emits_not_supported_and_error_response(void)
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -1422,10 +1479,10 @@ void test_case24_null_main_refusal_emits_not_supported_and_error_response(void)'

#### Decision late-935dfe8d317ce10c

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=44
- chosen text: `    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/flash_intel.cpp, hunk: @@ -38,44 +38,10 @@ static void flash_intel_check_vpp(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -38,44 +38,10 @@ static void flash_intel_check_vpp(firestarter_handle_t* handle) {'

#### Decision late-968afee7cd20439c

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=68
- chosen text: `# write-time budget decoded by _decode_id_frame's CAP-03 arm below. DERIVED,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/serial_comm.py, hunk: @@ -65,5 +65,5 @@ rurp_logger = logging.getLogger("RURP")
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -65,5 +65,5 @@ rurp_logger = logging.getLogger("RURP")'

#### Decision late-98e04c11a6e306b2

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=283
- chosen text: `# ---------------------------------------------------------------------------`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/chip_test.py, hunk: @@ -280,5 +280,5 @@ def classify_fingerprint(
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -280,5 +280,5 @@ def classify_fingerprint('

#### Decision late-9d8eae31a3f39114

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=85
- chosen text: ` */`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/include/operation_utils.h, hunk: @@ -82,5 +82,5 @@ bool op_execute_simple_operation(firestarter_handle_t* handle);
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -82,5 +82,5 @@ bool op_execute_simple_operation(firestarter_handle_t* handle);'

#### Decision late-9dc3c967ab8f9503

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503, end=503
- chosen text: `}` .. `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/json_parser.c, hunk: @@ -294,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -294,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision late-9dcd70601b1efd10

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1862, end=1850
- chosen text: `    sdp_assert_stream_equals(SDP_FIXED_DIP28_28C256, SDP_FIXED_DIP28_28C256_LEN,` .. `        "pre-write blank check still ran and left a multi-call INIT loop pending");`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp, hunk: @@ -1786,8 +1849,15 @@ void test_case30_write_init_no_blank_check_with_flag_clear_erase01(void) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -1786,8 +1849,15 @@ void test_case30_write_init_no_blank_check_with_flag_clear_erase01(void) {'

#### Decision late-9e80abd1a0d79749

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=73
- chosen text: ` */`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/include/operation_utils.h, hunk: @@ -70,5 +70,5 @@ static inline bool is_operation_waiting_for_data(const firestarter_handle_t* han
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -70,5 +70,5 @@ static inline bool is_operation_waiting_for_data(const firestarter_handle_t* han'

#### Decision late-9f65725852a7811d

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=282
- chosen text: `     * single file-scope global with no per-command memset, and page-size is`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -90,14 +279,13 @@ int json_parse(const char* json, jsmntok_t* tokens, int token_count, firestarter
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -90,14 +279,13 @@ int json_parse(const char* json, jsmntok_t* tokens, int token_count, firestarter'

#### Decision late-a279fa54e16deaa0

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=502
- chosen text: `        handle->address = 0;`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/memory.cpp, hunk: @@ -404,18 +497,12 @@ void uint32_to_bytes(char* buffer, int pos, uint32_t value) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -404,18 +497,12 @@ void uint32_to_bytes(char* buffer, int pos, uint32_t value) {'

#### Decision late-a343ac95a4f2fb9e

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=572, end=620
- chosen text: `        # fragile synthetic `info-flags & 0x10` round-trip injected by _map_data.` .. `        # this bit (`serial_comm.py`'s `_log_command_details`) is DEBUG-only`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/database.py, hunk: @@ -568,69 +568,60 @@ class EpromDatabase:
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -568,69 +568,60 @@ class EpromDatabase:'

#### Decision late-a44dd4ea099cd205

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=240
- chosen text: `static firestarter_handle_t make_write_init_handle_blank_check_enabled(void) {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp, hunk: @@ -235,8 +235,7 @@ static firestarter_handle_t make_write_handle_with_data(void) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -235,8 +235,7 @@ static firestarter_handle_t make_write_handle_with_data(void) {'

#### Decision late-a52f723ee2f7cf16

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164, end=275
- chosen text: `};` .. `    handle->bus_config.rw_line = 0xFF;`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision late-a56f21d2e54240d6

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=292
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eeprom_28c.cpp, hunk: @@ -289,20 +289,5 @@ static void eeprom28c_check_chip_id(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -289,20 +289,5 @@ static void eeprom28c_check_chip_id(firestarter_handle_t* handle) {'

#### Decision late-a75926068c602b29

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=58
- chosen text: ` */`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/operation_utils.cpp, hunk: @@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)'

#### Decision late-aa3d8b00b0636370

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=718
- chosen text: `    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eprom.cpp, hunk: @@ -712,44 +712,10 @@ void eprom_check_vpp(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -712,44 +712,10 @@ void eprom_check_vpp(firestarter_handle_t* handle) {'

#### Decision late-aabdd0cb088259bc

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=73
- chosen text: ` */`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/include/operation_utils.h, hunk: @@ -70,5 +70,5 @@ static inline bool is_operation_waiting_for_data(const firestarter_handle_t* han
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -70,5 +70,5 @@ static inline bool is_operation_waiting_for_data(const firestarter_handle_t* han'

#### Decision late-ab760da145549df5

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=720
- chosen text: `    }`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eprom.cpp, hunk: @@ -712,44 +712,10 @@ void eprom_check_vpp(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -712,44 +712,10 @@ void eprom_check_vpp(firestarter_handle_t* handle) {'

#### Decision late-abc2538caa1762ec

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=47
- chosen text: `                         * neither firestarter.h nor eprom.h/eprom_params.h/`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp, hunk: @@ -41,8 +41,8 @@ extern "C" {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -41,8 +41,8 @@ extern "C" {'

#### Decision late-aee68617d7feb69c

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=312
- chosen text: `# shipped database (all 84 qualify -- electrical-type is EEPROM or`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/chip_test.py, hunk: @@ -306,8 +306,8 @@ _PROTOCOL_FLASH4 = 0x05
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -306,8 +306,8 @@ _PROTOCOL_FLASH4 = 0x05'

#### Decision late-b0c41b3614b87444

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=58
- chosen text: ` */`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/operation_utils.cpp, hunk: @@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)'

#### Decision late-b27c39a109708b2a

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=106
- chosen text: `void rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count) {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/boards/uno_rurp_shield.cpp, hunk: @@ -104,12 +101,7 @@ void rurp_set_programmer_mode() {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -104,12 +101,7 @@ void rurp_set_programmer_mode() {'

#### Decision late-b38668d53ab91e4a

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=283
- chosen text: `# ---------------------------------------------------------------------------`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/chip_test.py, hunk: @@ -280,5 +280,5 @@ def classify_fingerprint(
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -280,5 +280,5 @@ def classify_fingerprint('

#### Decision late-b4317a4044c0ff8b

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1862
- chosen text: `    sdp_assert_stream_equals(SDP_FIXED_DIP28_28C256, SDP_FIXED_DIP28_28C256_LEN,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp, hunk: @@ -1786,8 +1849,15 @@ void test_case30_write_init_no_blank_check_with_flag_clear_erase01(void) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -1786,8 +1849,15 @@ void test_case30_write_init_no_blank_check_with_flag_clear_erase01(void) {'

#### Decision late-b4b0debcc57c9f7d

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=502, end=500
- chosen text: `        handle->address = 0;` .. `        set_operation_in_progress(handle);`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/memory.cpp, hunk: @@ -404,18 +497,12 @@ void uint32_to_bytes(char* buffer, int pos, uint32_t value) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -404,18 +497,12 @@ void uint32_to_bytes(char* buffer, int pos, uint32_t value) {'

#### Decision late-b5f21dacda85b229

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=231
- chosen text: ``
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/include/firestarter.h, hunk: @@ -224,5 +229,4 @@ typedef struct firestarter_handle {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -224,5 +229,4 @@ typedef struct firestarter_handle {'

#### Decision late-b6b17cde9e1c7aaa

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=502
- chosen text: `        handle->address = 0;`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/memory.cpp, hunk: @@ -404,18 +497,12 @@ void uint32_to_bytes(char* buffer, int pos, uint32_t value) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -404,18 +497,12 @@ void uint32_to_bytes(char* buffer, int pos, uint32_t value) {'

#### Decision late-b751c6638e72c5f6

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164
- chosen text: `};`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision late-b9c53c911b2f876b

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=436, end=439
- chosen text: `# `'write_scope="none": ... omitted (D-01)'` shape the shipped write/verify/` .. `# reason it does not own.`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/chip_test.py, hunk: @@ -433,5 +433,5 @@ _SDP_LEG_STEP_ORDER: tuple[str, ...] = (
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -433,5 +433,5 @@ _SDP_LEG_STEP_ORDER: tuple[str, ...] = ('

#### Decision late-baea020f08c35050

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=292
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eeprom_28c.cpp, hunk: @@ -289,20 +289,5 @@ static void eeprom28c_check_chip_id(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -289,20 +289,5 @@ static void eeprom28c_check_chip_id(firestarter_handle_t* handle) {'

#### Decision late-bc84a5c2568761f7

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=489, end=460
- chosen text: `` .. ``
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/memory.cpp, hunk: @@ -391,7 +459,32 @@ uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -391,7 +459,32 @@ uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t'

#### Decision late-c14563e7741f8ffb

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1862, end=1850
- chosen text: `    sdp_assert_stream_equals(SDP_FIXED_DIP28_28C256, SDP_FIXED_DIP28_28C256_LEN,` .. `        "pre-write blank check still ran and left a multi-call INIT loop pending");`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp, hunk: @@ -1786,8 +1849,15 @@ void test_case30_write_init_no_blank_check_with_flag_clear_erase01(void) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -1786,8 +1849,15 @@ void test_case30_write_init_no_blank_check_with_flag_clear_erase01(void) {'

#### Decision late-c2f44fad38f8c821

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/json_parser.c, hunk: @@ -294,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -294,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision late-c30fa27a172baa45

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=605
- chosen text: `        #`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/firestarter/database.py, hunk: @@ -568,69 +568,60 @@ class EpromDatabase:
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -568,69 +568,60 @@ class EpromDatabase:'

#### Decision late-c43c68107d5198b9

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=154
- chosen text: `    rurp_set_programmer_mode();`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/dev_tools.cpp, hunk: @@ -151,5 +151,5 @@ bool dt_set_address(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -151,5 +151,5 @@ bool dt_set_address(firestarter_handle_t* handle) {'

#### Decision late-c5109ba6e9201c71

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=211
- chosen text: `    uint8_t pins;`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/include/firestarter.h, hunk: @@ -207,5 +207,6 @@ typedef struct firestarter_handle {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -207,5 +207,6 @@ typedef struct firestarter_handle {'

#### Decision late-c57962620da326d3

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=154
- chosen text: `    rurp_set_programmer_mode();`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/dev_tools.cpp, hunk: @@ -151,5 +151,5 @@ bool dt_set_address(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -151,5 +151,5 @@ bool dt_set_address(firestarter_handle_t* handle) {'

#### Decision late-c6b0468e286bbb34

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1487
- chosen text: `    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp, hunk: @@ -1422,10 +1479,10 @@ void test_case24_null_main_refusal_emits_not_supported_and_error_response(void)
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -1422,10 +1479,10 @@ void test_case24_null_main_refusal_emits_not_supported_and_error_response(void)'

#### Decision late-c80e8bb0f471220f

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=173
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/operation_utils.cpp, hunk: @@ -162,5 +170,5 @@ bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -162,5 +170,5 @@ bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle'

#### Decision late-ca80b552ca926ff6

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164, end=275
- chosen text: `};` .. `    handle->bus_config.rw_line = 0xFF;`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision late-cab7ff14b502dc4d

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=44
- chosen text: `                             * eprom_block_budget_s -- BF-3-corrected budget arithmetic. */`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp, hunk: @@ -41,8 +41,8 @@ extern "C" {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -41,8 +41,8 @@ extern "C" {'

#### Decision late-cc58470d044c9052

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164, end=275
- chosen text: `};` .. `    handle->bus_config.rw_line = 0xFF;`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision late-d02faeddd6d53b53

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=718
- chosen text: `    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eprom.cpp, hunk: @@ -712,44 +712,10 @@ void eprom_check_vpp(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -712,44 +712,10 @@ void eprom_check_vpp(firestarter_handle_t* handle) {'

#### Decision late-d09c27844256506f

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/json_parser.c, hunk: @@ -294,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -294,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision late-d1337c62b74db4db

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=593, end=586
- chosen text: `    for env_name, fixture in (` .. ``
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/tests/test_check_size_baseline.py, hunk: @@ -561,35 +564,31 @@ def test_clean_avr_all_three_envs_pass():
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -561,35 +564,31 @@ def test_clean_avr_all_three_envs_pass():'

#### Decision late-d156cf281306afec

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=44
- chosen text: `    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/flash_intel.cpp, hunk: @@ -38,44 +38,10 @@ static void flash_intel_check_vpp(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -38,44 +38,10 @@ static void flash_intel_check_vpp(firestarter_handle_t* handle) {'

#### Decision late-d2577a81544d8cea

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=318
- chosen text: `                token_idx += 2; // Skip key and simple value`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/json_parser.c, hunk: @@ -126,6 +315,5 @@ int json_parse(const char* json, jsmntok_t* tokens, int token_count, firestarter
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -126,6 +315,5 @@ int json_parse(const char* json, jsmntok_t* tokens, int token_count, firestarter'

#### Decision late-d5993e2cf2179a25

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=58
- chosen text: ` */`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/operation_utils.cpp, hunk: @@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)'

#### Decision late-d5dce2e912dc2cbd

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/json_parser.c, hunk: @@ -294,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -294,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision late-d684c09e391cc63f

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=318
- chosen text: `                token_idx += 2; // Skip key and simple value`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/json_parser.c, hunk: @@ -126,6 +315,5 @@ int json_parse(const char* json, jsmntok_t* tokens, int token_count, firestarter
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -126,6 +315,5 @@ int json_parse(const char* json, jsmntok_t* tokens, int token_count, firestarter'

#### Decision late-d99720f86a3e0c67

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=265
- chosen text: `// Read addresses are derived from mem_size: AT28C256 = 0x7FC0/0x7FC1,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eeprom_28c.cpp, hunk: @@ -262,5 +262,5 @@ void configure_eeprom28c(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -262,5 +262,5 @@ void configure_eeprom28c(firestarter_handle_t* handle) {'

#### Decision late-dd6aa9b6b6cf1dcf

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=593, end=586
- chosen text: `    for env_name, fixture in (` .. ``
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/tests/test_check_size_baseline.py, hunk: @@ -561,35 +564,31 @@ def test_clean_avr_all_three_envs_pass():
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -561,35 +564,31 @@ def test_clean_avr_all_three_envs_pass():'

#### Decision late-de17c8e50b7a5b82

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=58
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/eprom_params.cpp, hunk: @@ -59,4 +55,4 @@ const eprom_params_t* eprom_params_for(uint32_t protocol) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -59,4 +55,4 @@ const eprom_params_t* eprom_params_for(uint32_t protocol) {'

#### Decision late-df6d0764b3f1ba0a

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=65, end=63
- chosen text: `bool eprom_sdp_unlock(firestarter_handle_t* handle) {` .. `// no SDP analogue; D-06's op-layer NULL-main guard (Plan 119-07) is what`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/eprom_operations.cpp, hunk: @@ -62,14 +62,11 @@ bool eprom_blank_check(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -62,14 +62,11 @@ bool eprom_blank_check(firestarter_handle_t* handle) {'

#### Decision late-e0c1b33533097f5b

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=58
- chosen text: ` */`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/operation_utils.cpp, hunk: @@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)'

#### Decision late-e0df256d46e172e0

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=351, end=339
- chosen text: `    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,` .. `        "left a multi-call INIT loop pending");`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp, hunk: @@ -337,8 +338,15 @@ void test_5v_page_write_init_no_blank_check_with_flag_clear_erase02(void) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -337,8 +338,15 @@ void test_5v_page_write_init_no_blank_check_with_flag_clear_erase02(void) {'

#### Decision late-e1e1f37fd3f42ae2

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=65, end=63
- chosen text: `bool eprom_sdp_unlock(firestarter_handle_t* handle) {` .. `// no SDP analogue; D-06's op-layer NULL-main guard (Plan 119-07) is what`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/eprom_operations.cpp, hunk: @@ -62,14 +62,11 @@ bool eprom_blank_check(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -62,14 +62,11 @@ bool eprom_blank_check(firestarter_handle_t* handle) {'

#### Decision late-e65cc0300ebbf4c9

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=46
- chosen text: `    }`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/flash_intel.cpp, hunk: @@ -38,44 +38,10 @@ static void flash_intel_check_vpp(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -38,44 +38,10 @@ static void flash_intel_check_vpp(firestarter_handle_t* handle) {'

#### Decision late-ea21e3c1875463c9

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164
- chosen text: `};`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision late-ebd430bed1cba11a

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=409
- chosen text: `#     so it matches the FIRST except clause (Python matches the first`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/tests/test_chip_test_sdp_leg.py, hunk: @@ -406,5 +406,5 @@ def _derive_precedence_row(exc):
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -406,5 +406,5 @@ def _derive_precedence_row(exc):'

#### Decision late-eda9e234c0666c8d

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=292
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eeprom_28c.cpp, hunk: @@ -289,20 +289,5 @@ static void eeprom28c_check_chip_id(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -289,20 +289,5 @@ static void eeprom28c_check_chip_id(firestarter_handle_t* handle) {'

#### Decision late-f06de9ab04f510b0

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=141
- chosen text: ``
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a -> live firestarter_app/tests/test_parse_gate_admission.py, hunk: @@ -98,9 +109,34 @@ _DEFAULT_UNKNOWN_CMD_RE = re.compile(
- diff evidence: sha_pair=['6bfa6453d1bac232eb81ab35fa7f14b50b0b291a', '<live working tree>'], hunk_header='@@ -98,9 +109,34 @@ _DEFAULT_UNKNOWN_CMD_RE = re.compile('

#### Decision late-f485b22a3b474d51

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=489, end=460
- chosen text: `` .. ``
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/memory.cpp, hunk: @@ -391,7 +459,32 @@ uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -391,7 +459,32 @@ uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t'

#### Decision late-f4a05ad2995feb74

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1582, end=1590
- chosen text: `    int calls = 0;` .. `        "Case 25 (ERASE-03, mechanism-corrected/intent-satisfied -- never as failed): "`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp, hunk: @@ -1522,18 +1579,24 @@ void test_case25_cmd_erase_on_0x0d_dispatches_and_succeeds_erase03(void) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -1522,18 +1579,24 @@ void test_case25_cmd_erase_on_0x0d_dispatches_and_succeeds_erase03(void) {'

#### Decision late-f5ad8b5a3fe2867c

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=58
- chosen text: ` */`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/operation_utils.cpp, hunk: @@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)'

#### Decision late-f8e06f303ac4f674

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=56, end=58
- chosen text: `"""` .. `from __future__ import annotations`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/tests/meta_presence.py, hunk: @@ -46,10 +46,12 @@ process's environment -- never an in-process monkeypatch, never a direct
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header="@@ -46,10 +46,12 @@ process's environment -- never an in-process monkeypatch, never a direct"

#### Decision late-fbcd5632f0aa46ef

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=265
- chosen text: `// Read addresses are derived from mem_size: AT28C256 = 0x7FC0/0x7FC1,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/proms/eeprom_28c.cpp, hunk: @@ -262,5 +262,5 @@ void configure_eeprom28c(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -262,5 +262,5 @@ void configure_eeprom28c(firestarter_handle_t* handle) {'

#### Decision late-ff145de30dafcfea

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=58
- chosen text: ` */`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 2ad5b322a37ba4a88afd09cc946f5c4114e51483 -> live firestarter/src/operation_utils.cpp, hunk: @@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)
- diff evidence: sha_pair=['2ad5b322a37ba4a88afd09cc946f5c4114e51483', '<live working tree>'], hunk_header='@@ -55,5 +55,5 @@ static inline bool _single_step_operation_callback(firestarter_handle_t* handle)'

#### Decision orig-01f1790b47980f9a

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164
- chosen text: `};`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision orig-03724044e2fa9b54

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-06c92ba6faf32077

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164, end=97
- chosen text: `};` .. ``
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision orig-0990f8a617d5792e

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-0e14b6f55b82c778

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=107, end=105
- chosen text: `}` .. `    uint16_t chip_id = flash_util_get_chip_id(handle);`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/flash_utils.cpp, hunk: @@ -103,17 +104,4 @@ uint8_t flash_util_read_in_id_mode(firestarter_handle_t* handle, uint32_t addres
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -103,17 +104,4 @@ uint8_t flash_util_read_in_id_mode(firestarter_handle_t* handle, uint32_t addres'

#### Decision orig-0e3bcf2eb9f3f99d

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-0e6113b5284755ca

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=173
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/operation_utils.cpp, hunk: @@ -162,5 +170,5 @@ bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -162,5 +170,5 @@ bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle'

#### Decision orig-0e7c1b8111d216c2

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=211
- chosen text: `    uint8_t pins;`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/include/firestarter.h, hunk: @@ -207,5 +207,6 @@ typedef struct firestarter_handle {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -207,5 +207,6 @@ typedef struct firestarter_handle {'

#### Decision orig-1329d6ba520d7a7e

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=292
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/eeprom_28c.cpp, hunk: @@ -301,25 +289,10 @@ static void eeprom28c_check_chip_id(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -301,25 +289,10 @@ static void eeprom28c_check_chip_id(firestarter_handle_t* handle) {'

#### Decision orig-18cb3c3088cd8b2c

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=103, end=105
- chosen text: `` .. `    uint16_t chip_id = flash_util_get_chip_id(handle);`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/flash_utils.cpp, hunk: @@ -103,17 +104,4 @@ uint8_t flash_util_read_in_id_mode(firestarter_handle_t* handle, uint32_t addres
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -103,17 +104,4 @@ uint8_t flash_util_read_in_id_mode(firestarter_handle_t* handle, uint32_t addres'

#### Decision orig-195e0e51da2376fa

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=97
- chosen text: ``
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision orig-1bba33baf699f4c1

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164
- chosen text: `};`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision orig-21a70dc9dbfce8ee

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164
- chosen text: `};`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision orig-2267e39064cb1790

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-238fd334ea41f3f8

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=107
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/flash_utils.cpp, hunk: @@ -103,17 +104,4 @@ uint8_t flash_util_read_in_id_mode(firestarter_handle_t* handle, uint32_t addres
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -103,17 +104,4 @@ uint8_t flash_util_read_in_id_mode(firestarter_handle_t* handle, uint32_t addres'

#### Decision orig-23a79f1e85498166

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=351
- chosen text: `    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp, hunk: @@ -337,8 +338,15 @@ void test_5v_page_write_init_no_blank_check_with_flag_clear_erase02(void) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -337,8 +338,15 @@ void test_5v_page_write_init_no_blank_check_with_flag_clear_erase02(void) {'

#### Decision orig-23cb647ef4ab83ac

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164
- chosen text: `};`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision orig-24aee1289cde3b55

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=107
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/flash_utils.cpp, hunk: @@ -103,17 +104,4 @@ uint8_t flash_util_read_in_id_mode(firestarter_handle_t* handle, uint32_t addres
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -103,17 +104,4 @@ uint8_t flash_util_read_in_id_mode(firestarter_handle_t* handle, uint32_t addres'

#### Decision orig-24d51257c90a95ee

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164
- chosen text: `};`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision orig-2534f9bfaa7bf2b7

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=107
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/flash_utils.cpp, hunk: @@ -103,17 +104,4 @@ uint8_t flash_util_read_in_id_mode(firestarter_handle_t* handle, uint32_t addres
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -103,17 +104,4 @@ uint8_t flash_util_read_in_id_mode(firestarter_handle_t* handle, uint32_t addres'

#### Decision orig-28f315215cb1605d

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164
- chosen text: `};`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision orig-318f399604c5c0cd

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164
- chosen text: `};`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision orig-32131e802f81e734

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503, end=497
- chosen text: `}` .. `bool get_flags(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-34f94bd587489d50

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=459, end=497
- chosen text: `        }` .. `bool get_flags(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-356bb8f7e365fe96

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-37ddacc3ed610f9f

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-3dd728837b6cb5ce

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=87
- chosen text: `        }`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/operation_utils.cpp, hunk: @@ -68,17 +68,23 @@ bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -68,17 +68,23 @@ bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle'

#### Decision orig-3f41e8468ba22cfa

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164
- chosen text: `};`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision orig-436c0d3356f5cd71

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-48a4b22c61687ba3

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-4920d562e764ba42

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164
- chosen text: `};`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision orig-52fed2082e348e7b

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164
- chosen text: `};`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision orig-54b4a7a0238f076c

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=173, end=176
- chosen text: `}` .. ` * @brief Executes a provided function with standard operation wrappers.`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/operation_utils.cpp, hunk: @@ -162,5 +170,5 @@ bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -162,5 +170,5 @@ bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle'

#### Decision orig-54cfc6f6c6e8440b

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded/live text is punctuation-only ('}'); a byte-exact match on a brace carries no discriminating power, so it is not trusted as a verbatim pass even though it is technically byte-identical
- rationale: Engine clamp lands on a bare '}' -- punctuation-only, excluded from the strict verbatim-match mechanical-pass floor per operator ruling, but the diff-computed clamp itself is a legitimate successor-line claim (not a match claim). Settled as diff-provenance with an explicit low-information flag rather than left undecided.
- evidence: engine clamp at firestarter/src/json_parser.c:503

#### Decision orig-55acea0659334089

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=41
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/eprom_operations.cpp, hunk: @@ -38,5 +38,5 @@ bool eprom_erase(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -38,5 +38,5 @@ bool eprom_erase(firestarter_handle_t* handle) {'

#### Decision orig-5af025295c8b59da

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=718
- chosen text: `    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/eprom.cpp, hunk: @@ -712,44 +712,10 @@ void eprom_check_vpp(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -712,44 +712,10 @@ void eprom_check_vpp(firestarter_handle_t* handle) {'

#### Decision orig-5c9c45d5b58025b6

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503, end=497
- chosen text: `}` .. `bool get_flags(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-5d799ba67002500d

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503, end=497
- chosen text: `}` .. `bool get_flags(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-5e9e8e1ee555583e

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-5f90801b66ccfc7c

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=20
- chosen text: ``
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -16,14 +18,4 @@ int parse_bus_config(const char* json, jsmntok_t* tokens, int token_count, fires
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -16,14 +18,4 @@ int parse_bus_config(const char* json, jsmntok_t* tokens, int token_count, fires'

#### Decision orig-605a03dc4d6d8859

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=33, end=39
- chosen text: `` .. `    }`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/eprom_operations.cpp, hunk: @@ -29,5 +29,5 @@ bool eprom_write(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -29,5 +29,5 @@ bool eprom_write(firestarter_handle_t* handle) {'

#### Decision orig-61c5d7e55e5ec3ab

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164
- chosen text: `};`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision orig-61ea900a6404c341

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-6529e5a21b08122c

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164
- chosen text: `};`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision orig-6617f48e28ba5a76

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-6ae4640f44ee8d7a

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503, end=497
- chosen text: `}` .. `bool get_flags(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-6b3c234aac74970d

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-6b98d6885c052ae4

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=489, end=558
- chosen text: `` .. `        LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, handle->address, handle->mem_size);`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/memory.cpp, hunk: @@ -387,7 +459,32 @@ uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -387,7 +459,32 @@ uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t'

#### Decision orig-707203e5cf97d1ab

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=393, end=460
- chosen text: `}` .. ``
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/memory.cpp, hunk: @@ -387,7 +459,32 @@ uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -387,7 +459,32 @@ uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t'

#### Decision orig-72e8e26c65d66bf8

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=50
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/eprom_operations.cpp, hunk: @@ -47,10 +47,10 @@ bool eprom_check_chip_id(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -47,10 +47,10 @@ bool eprom_check_chip_id(firestarter_handle_t* handle) {'

#### Decision orig-75593e92a1639406

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-77a4d18a31cde3c5

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=50
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/eprom_operations.cpp, hunk: @@ -47,10 +47,10 @@ bool eprom_check_chip_id(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -47,10 +47,10 @@ bool eprom_check_chip_id(firestarter_handle_t* handle) {'

#### Decision orig-7a196971330452e5

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-7d15c04e933ff1cd

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=20, end=19
- chosen text: `` .. `bool get_flags(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -16,14 +18,4 @@ int parse_bus_config(const char* json, jsmntok_t* tokens, int token_count, fires
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -16,14 +18,4 @@ int parse_bus_config(const char* json, jsmntok_t* tokens, int token_count, fires'

#### Decision orig-8251c72b3dcaafb2

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=240
- chosen text: `static firestarter_handle_t make_write_init_handle_blank_check_enabled(void) {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp, hunk: @@ -235,8 +235,7 @@ static firestarter_handle_t make_write_handle_with_data(void) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -235,8 +235,7 @@ static firestarter_handle_t make_write_handle_with_data(void) {'

#### Decision orig-83ae4c50d94cfcb3

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=33, end=39
- chosen text: `` .. `    }`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/eprom_operations.cpp, hunk: @@ -29,5 +29,5 @@ bool eprom_write(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -29,5 +29,5 @@ bool eprom_write(firestarter_handle_t* handle) {'

#### Decision orig-877d5eaaff75f54b

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=41
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/eprom_operations.cpp, hunk: @@ -38,5 +38,5 @@ bool eprom_erase(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -38,5 +38,5 @@ bool eprom_erase(firestarter_handle_t* handle) {'

#### Decision orig-89dbe10103e8fe03

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-8d61cadc57286de3

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=50
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/eprom_operations.cpp, hunk: @@ -47,10 +47,10 @@ bool eprom_check_chip_id(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -47,10 +47,10 @@ bool eprom_check_chip_id(firestarter_handle_t* handle) {'

#### Decision orig-936d5d2a561a945c

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164
- chosen text: `};`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision orig-94404d7c4192c15e

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164, end=271
- chosen text: `};` .. ``
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision orig-9a35bfe98d27ddd1

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=459, end=497
- chosen text: `        }` .. `bool get_flags(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-9af454dbb23f0497

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-9d5a1cb1e386a2f3

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-9e468f7303d1d2d4

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-9f4df61fe0341ef3

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=393, end=460
- chosen text: `}` .. ``
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/memory.cpp, hunk: @@ -387,7 +459,32 @@ uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -387,7 +459,32 @@ uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t'

#### Decision orig-a0a2b85ac1dfb6ad

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-a2e0400134936499

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=240
- chosen text: `static firestarter_handle_t make_write_init_handle_blank_check_enabled(void) {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp, hunk: @@ -235,8 +235,7 @@ static firestarter_handle_t make_write_handle_with_data(void) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -235,8 +235,7 @@ static firestarter_handle_t make_write_handle_with_data(void) {'

#### Decision orig-a34394bfffa95d1f

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=173
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/operation_utils.cpp, hunk: @@ -162,5 +170,5 @@ bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -162,5 +170,5 @@ bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle'

#### Decision orig-a68cfc4d488053dc

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=33, end=39
- chosen text: `` .. `    }`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/eprom_operations.cpp, hunk: @@ -29,5 +29,5 @@ bool eprom_write(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -29,5 +29,5 @@ bool eprom_write(firestarter_handle_t* handle) {'

#### Decision orig-b534082821baa81a

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-b83e840ffd07a1bd

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164, end=274
- chosen text: `};` .. `    handle->ctrl_flags = 0;`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision orig-b8ba976e7fae347d

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=20, end=21
- chosen text: `` .. `bool get_rw_pin(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -16,14 +18,4 @@ int parse_bus_config(const char* json, jsmntok_t* tokens, int token_count, fires
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -16,14 +18,4 @@ int parse_bus_config(const char* json, jsmntok_t* tokens, int token_count, fires'

#### Decision orig-bdd4d8997ad8dc3a

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=173, end=176
- chosen text: `}` .. ` * @brief Executes a provided function with standard operation wrappers.`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/operation_utils.cpp, hunk: @@ -162,5 +170,5 @@ bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -162,5 +170,5 @@ bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle'

#### Decision orig-bf16557c03f65a2b

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=292
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/eeprom_28c.cpp, hunk: @@ -301,25 +289,10 @@ static void eeprom28c_check_chip_id(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -301,25 +289,10 @@ static void eeprom28c_check_chip_id(firestarter_handle_t* handle) {'

#### Decision orig-bf331365b374def5

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=41
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/eprom_operations.cpp, hunk: @@ -38,5 +38,5 @@ bool eprom_erase(firestarter_handle_t* handle) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -38,5 +38,5 @@ bool eprom_erase(firestarter_handle_t* handle) {'

#### Decision orig-bfff4008f7c27d73

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-c851367c5fa2b9db

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-cbff8f283fa6d76f

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=107
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/proms/flash_utils.cpp, hunk: @@ -103,17 +104,4 @@ uint8_t flash_util_read_in_id_mode(firestarter_handle_t* handle, uint32_t addres
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -103,17 +104,4 @@ uint8_t flash_util_read_in_id_mode(firestarter_handle_t* handle, uint32_t addres'

#### Decision orig-ce10bd34592d5c4d

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503, end=497
- chosen text: `}` .. `bool get_flags(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-d002af63b8af49c3

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-d115fcc7ed3c6097

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=240
- chosen text: `static firestarter_handle_t make_write_init_handle_blank_check_enabled(void) {`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp, hunk: @@ -235,8 +235,7 @@ static firestarter_handle_t make_write_handle_with_data(void) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -235,8 +235,7 @@ static firestarter_handle_t make_write_handle_with_data(void) {'

#### Decision orig-d97348280e84506b

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503, end=497
- chosen text: `}` .. `bool get_flags(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-daf2ce68089477c0

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-dd4983a59a7f2b5f

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded/live text is punctuation-only ('}'); a byte-exact match on a brace carries no discriminating power, so it is not trusted as a verbatim pass even though it is technically byte-identical
- rationale: Engine clamp lands on a bare '}' -- punctuation-only, excluded from the strict verbatim-match mechanical-pass floor per operator ruling, but the diff-computed clamp itself is a legitimate successor-line claim (not a match claim). Settled as diff-provenance with an explicit low-information flag rather than left undecided.
- evidence: engine clamp at firestarter/src/json_parser.c:503

#### Decision orig-f0a2e3789c51a1eb

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=223
- chosen text: `    uint16_t chip_id;`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/include/firestarter.h, hunk: @@ -215,5 +216,9 @@ typedef struct firestarter_handle {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -215,5 +216,9 @@ typedef struct firestarter_handle {'

#### Decision orig-f2c91d236d0eb8d9

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=1862
- chosen text: `    sdp_assert_stream_equals(SDP_FIXED_DIP28_28C256, SDP_FIXED_DIP28_28C256_LEN,`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp, hunk: @@ -1786,8 +1849,15 @@ void test_case30_write_init_no_blank_check_with_flag_clear_erase01(void) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -1786,8 +1849,15 @@ void test_case30_write_init_no_blank_check_with_flag_clear_erase01(void) {'

#### Decision orig-f345b8a0a10d7fee

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-f59b07c498db3220

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503
- chosen text: `}`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-f9168ac07bb6b6a3

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=164, end=274
- chosen text: `};` .. `    handle->ctrl_flags = 0;`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

#### Decision orig-fb73c296c93c80da

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=166
- chosen text: `    // RESPONSE_CODE_ERROR instead of the RESPONSE_CODE_OK loop() set: the`
- low_information_target: `false`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/operation_utils.cpp, hunk: @@ -152,8 +158,10 @@ bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -152,8 +158,10 @@ bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle'

#### Decision orig-fbfe06a409d3f273

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=503, end=497
- chosen text: `}` .. `bool get_flags(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {`
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -295,34 +482,23 @@ static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {'

#### Decision orig-fc62d67a32a2a96e

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `diff_provenance_reworded`
- chosen endpoint: start=97
- chosen text: ``
- low_information_target: `true`
- verbatim_oracle_applied: `false` -- recorded source_text[/_end] does not equal live text at the clamp; sweep reworded the content
- rationale: Recorded text does not match live text at the clamp byte-for-byte; the cited line was REWORDED by the Phase-154 comment sweep (D-01), not merely moved. The engine's diff-derived LineMap clamp is the sole basis for this endpoint, per operator ruling (accept diff-provenance, mechanized).
- evidence: sha 8695ee52c27a4bee4387c5c489afd5f3d7275e8a -> live firestarter/src/json_parser.c, hunk: @@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";
- diff evidence: sha_pair=['8695ee52c27a4bee4387c5c489afd5f3d7275e8a', '<live working tree>'], hunk_header='@@ -66,19 +77,197 @@ const char key_read_strobe[]   PROGMEM = "read-strobe-us";'

### Class: `duplicate_citation_shared_endpoint` (18 records)

#### Decision late-18500dc530a26637

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `duplicate_citation_shared_endpoint`
- chosen endpoint: start=453
- chosen text: `        assert _git_porcelain(FW_ROOT) == "", (`
- duplicate_set: late-18500dc530a26637
- rationale: 1-way duplicate: all members share the identical recorded target identity (firestarter_app/tests/test_json_key_parity.py:453). _associate()'s group-cardinality check could not attribute each member to a specific surviving span (record<->span ATTRIBUTION is ambiguous), but the endpoint is attribution-invariant: the LineMap maps that one recorded target to one successor line regardless of which member 'owns' which span. Duplicate set: late-18500dc530a26637
- evidence: LineMap(firestarter_app/tests/test_json_key_parity.py, sha=6bfa6453d1bac232eb81ab35fa7f14b50b0b291a).span/point(453,None) resolves cleanly

#### Decision late-1ddd41155172d5b4

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `duplicate_citation_shared_endpoint`
- chosen endpoint: start=1275
- chosen text: `    assert _git_porcelain(_REPO_ROOT) == "", (`
- duplicate_set: late-1ddd41155172d5b4
- rationale: 1-way duplicate: all members share the identical recorded target identity (firestarter/tests/test_trace_segment_exhaustiveness_v131.py:1275). _associate()'s group-cardinality check could not attribute each member to a specific surviving span (record<->span ATTRIBUTION is ambiguous), but the endpoint is attribution-invariant: the LineMap maps that one recorded target to one successor line regardless of which member 'owns' which span. Duplicate set: late-1ddd41155172d5b4
- evidence: LineMap(firestarter/tests/test_trace_segment_exhaustiveness_v131.py, sha=8695ee52c27a4bee4387c5c489afd5f3d7275e8a).span/point(1275,None) resolves cleanly

#### Decision late-2e7fad9449b6a0ce

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `duplicate_citation_shared_endpoint`
- chosen endpoint: start=103
- chosen text: `}`
- duplicate_set: orig-2ee932140f8546c0, late-2e7fad9449b6a0ce, late-da96a21e85c4c8c0
- rationale: 3-way duplicate: all members share the identical recorded target identity (firestarter/src/proms/flash_5v_page.cpp:101). _associate()'s group-cardinality check could not attribute each member to a specific surviving span (record<->span ATTRIBUTION is ambiguous), but the endpoint is attribution-invariant: the LineMap maps that one recorded target to one successor line regardless of which member 'owns' which span. Duplicate set: orig-2ee932140f8546c0, late-2e7fad9449b6a0ce, late-da96a21e85c4c8c0
- evidence: LineMap(firestarter/src/proms/flash_5v_page.cpp, sha=8695ee52c27a4bee4387c5c489afd5f3d7275e8a).span/point(101,None) resolves cleanly

#### Decision late-3eca6122f460f077

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `duplicate_citation_shared_endpoint`
- chosen endpoint: start=177, end=195
- chosen text: `    // CAP-02 is being PORTED here, not invented: it shipped on origin/beta` .. `    // CAP-03 (HOST-01) is emitted for EVERY command, not just CMD_WRITE --`
- duplicate_set: orig-4bfe86cc4c907832, late-3eca6122f460f077
- rationale: 2-way duplicate: all members share the identical recorded target identity (firestarter/src/firestarter.cpp:182-200). _associate()'s group-cardinality check could not attribute each member to a specific surviving span (record<->span ATTRIBUTION is ambiguous), but the endpoint is attribution-invariant: the LineMap maps that one recorded target to one successor line regardless of which member 'owns' which span. Duplicate set: orig-4bfe86cc4c907832, late-3eca6122f460f077
- evidence: LineMap(firestarter/src/firestarter.cpp, sha=8695ee52c27a4bee4387c5c489afd5f3d7275e8a).span/point(182,200) resolves cleanly

#### Decision late-527ef40d87200f5b

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `duplicate_citation_shared_endpoint`
- chosen endpoint: start=491
- chosen text: `        assert _git_porcelain(FW_ROOT) == "", (`
- duplicate_set: late-527ef40d87200f5b
- rationale: 1-way duplicate: all members share the identical recorded target identity (firestarter_app/tests/test_json_key_parity.py:491). _associate()'s group-cardinality check could not attribute each member to a specific surviving span (record<->span ATTRIBUTION is ambiguous), but the endpoint is attribution-invariant: the LineMap maps that one recorded target to one successor line regardless of which member 'owns' which span. Duplicate set: late-527ef40d87200f5b
- evidence: LineMap(firestarter_app/tests/test_json_key_parity.py, sha=6bfa6453d1bac232eb81ab35fa7f14b50b0b291a).span/point(491,None) resolves cleanly

#### Decision late-63d1cb2351bb02c7

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `duplicate_citation_shared_endpoint`
- chosen endpoint: start=753
- chosen text: `    assert _git_porcelain(_REPO_ROOT) == "", (`
- duplicate_set: late-63d1cb2351bb02c7
- rationale: 1-way duplicate: all members share the identical recorded target identity (firestarter/tests/test_requirement_case_mapping_v131.py:753). _associate()'s group-cardinality check could not attribute each member to a specific surviving span (record<->span ATTRIBUTION is ambiguous), but the endpoint is attribution-invariant: the LineMap maps that one recorded target to one successor line regardless of which member 'owns' which span. Duplicate set: late-63d1cb2351bb02c7
- evidence: LineMap(firestarter/tests/test_requirement_case_mapping_v131.py, sha=8695ee52c27a4bee4387c5c489afd5f3d7275e8a).span/point(753,None) resolves cleanly

#### Decision late-73163a8965878a89

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `duplicate_citation_shared_endpoint`
- chosen endpoint: start=802
- chosen text: `    assert _git_porcelain(_REPO_ROOT) == "", (`
- duplicate_set: late-73163a8965878a89
- rationale: 1-way duplicate: all members share the identical recorded target identity (firestarter/tests/test_requirement_case_mapping_v131.py:802). _associate()'s group-cardinality check could not attribute each member to a specific surviving span (record<->span ATTRIBUTION is ambiguous), but the endpoint is attribution-invariant: the LineMap maps that one recorded target to one successor line regardless of which member 'owns' which span. Duplicate set: late-73163a8965878a89
- evidence: LineMap(firestarter/tests/test_requirement_case_mapping_v131.py, sha=8695ee52c27a4bee4387c5c489afd5f3d7275e8a).span/point(802,None) resolves cleanly

#### Decision late-7bd688b0f0c1873d

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `duplicate_citation_shared_endpoint`
- chosen endpoint: start=391
- chosen text: `        assert _git_porcelain(FW_ROOT) == "", (`
- duplicate_set: orig-13aa962c63cb6004, late-7bd688b0f0c1873d
- rationale: 2-way duplicate: all members share the identical recorded target identity (firestarter_app/tests/test_py32_flash_map_host.py:391). _associate()'s group-cardinality check could not attribute each member to a specific surviving span (record<->span ATTRIBUTION is ambiguous), but the endpoint is attribution-invariant: the LineMap maps that one recorded target to one successor line regardless of which member 'owns' which span. Duplicate set: orig-13aa962c63cb6004, late-7bd688b0f0c1873d
- evidence: LineMap(firestarter_app/tests/test_py32_flash_map_host.py, sha=6bfa6453d1bac232eb81ab35fa7f14b50b0b291a).span/point(391,None) resolves cleanly

#### Decision late-8c1a734043d1dca8

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `duplicate_citation_shared_endpoint`
- chosen endpoint: start=1144
- chosen text: `    assert _git_porcelain(_REPO_ROOT) == "", (`
- duplicate_set: late-8c1a734043d1dca8
- rationale: 1-way duplicate: all members share the identical recorded target identity (firestarter/tests/test_trace_segment_exhaustiveness_v131.py:1144). _associate()'s group-cardinality check could not attribute each member to a specific surviving span (record<->span ATTRIBUTION is ambiguous), but the endpoint is attribution-invariant: the LineMap maps that one recorded target to one successor line regardless of which member 'owns' which span. Duplicate set: late-8c1a734043d1dca8
- evidence: LineMap(firestarter/tests/test_trace_segment_exhaustiveness_v131.py, sha=8695ee52c27a4bee4387c5c489afd5f3d7275e8a).span/point(1144,None) resolves cleanly

#### Decision late-9a97677b6693d073

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `duplicate_citation_shared_endpoint`
- chosen endpoint: start=786
- chosen text: `        assert _git_porcelain(FW_ROOT) == "", (`
- duplicate_set: late-9a97677b6693d073
- rationale: 1-way duplicate: all members share the identical recorded target identity (firestarter_app/tests/test_cap03_ack_layout_parity.py:786). _associate()'s group-cardinality check could not attribute each member to a specific surviving span (record<->span ATTRIBUTION is ambiguous), but the endpoint is attribution-invariant: the LineMap maps that one recorded target to one successor line regardless of which member 'owns' which span. Duplicate set: late-9a97677b6693d073
- evidence: LineMap(firestarter_app/tests/test_cap03_ack_layout_parity.py, sha=6bfa6453d1bac232eb81ab35fa7f14b50b0b291a).span/point(786,None) resolves cleanly

#### Decision late-c936dd853af41730

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `duplicate_citation_shared_endpoint`
- chosen endpoint: start=323
- chosen text: `        assert _git_porcelain(FW_ROOT) == "", (`
- duplicate_set: orig-99337c160a67c186, late-c936dd853af41730
- rationale: 2-way duplicate: all members share the identical recorded target identity (firestarter_app/tests/test_py32_asset_name_host.py:323). _associate()'s group-cardinality check could not attribute each member to a specific surviving span (record<->span ATTRIBUTION is ambiguous), but the endpoint is attribution-invariant: the LineMap maps that one recorded target to one successor line regardless of which member 'owns' which span. Duplicate set: orig-99337c160a67c186, late-c936dd853af41730
- evidence: LineMap(firestarter_app/tests/test_py32_asset_name_host.py, sha=6bfa6453d1bac232eb81ab35fa7f14b50b0b291a).span/point(323,None) resolves cleanly

#### Decision late-da96a21e85c4c8c0

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `duplicate_citation_shared_endpoint`
- chosen endpoint: start=103
- chosen text: `}`
- duplicate_set: orig-2ee932140f8546c0, late-2e7fad9449b6a0ce, late-da96a21e85c4c8c0
- rationale: 3-way duplicate: all members share the identical recorded target identity (firestarter/src/proms/flash_5v_page.cpp:101). _associate()'s group-cardinality check could not attribute each member to a specific surviving span (record<->span ATTRIBUTION is ambiguous), but the endpoint is attribution-invariant: the LineMap maps that one recorded target to one successor line regardless of which member 'owns' which span. Duplicate set: orig-2ee932140f8546c0, late-2e7fad9449b6a0ce, late-da96a21e85c4c8c0
- evidence: LineMap(firestarter/src/proms/flash_5v_page.cpp, sha=8695ee52c27a4bee4387c5c489afd5f3d7275e8a).span/point(101,None) resolves cleanly

#### Decision late-df9fb450527ec517

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `duplicate_citation_shared_endpoint`
- chosen endpoint: start=1247
- chosen text: `        assert _git_porcelain(_FW_REPO_ROOT) == "", (`
- duplicate_set: late-df9fb450527ec517
- rationale: 1-way duplicate: all members share the identical recorded target identity (firestarter/tests/test_flash_path_record_sync.py:1247). _associate()'s group-cardinality check could not attribute each member to a specific surviving span (record<->span ATTRIBUTION is ambiguous), but the endpoint is attribution-invariant: the LineMap maps that one recorded target to one successor line regardless of which member 'owns' which span. Duplicate set: late-df9fb450527ec517
- evidence: LineMap(firestarter/tests/test_flash_path_record_sync.py, sha=8695ee52c27a4bee4387c5c489afd5f3d7275e8a).span/point(1247,None) resolves cleanly

#### Decision late-e236155371d97ee6

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `duplicate_citation_shared_endpoint`
- chosen endpoint: start=746
- chosen text: `        assert _git_porcelain(FW_ROOT) == "", (`
- duplicate_set: late-e236155371d97ee6
- rationale: 1-way duplicate: all members share the identical recorded target identity (firestarter_app/tests/test_cap03_ack_layout_parity.py:746). _associate()'s group-cardinality check could not attribute each member to a specific surviving span (record<->span ATTRIBUTION is ambiguous), but the endpoint is attribution-invariant: the LineMap maps that one recorded target to one successor line regardless of which member 'owns' which span. Duplicate set: late-e236155371d97ee6
- evidence: LineMap(firestarter_app/tests/test_cap03_ack_layout_parity.py, sha=6bfa6453d1bac232eb81ab35fa7f14b50b0b291a).span/point(746,None) resolves cleanly

#### Decision orig-13aa962c63cb6004

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `duplicate_citation_shared_endpoint`
- chosen endpoint: start=391
- chosen text: `        assert _git_porcelain(FW_ROOT) == "", (`
- duplicate_set: orig-13aa962c63cb6004, late-7bd688b0f0c1873d
- rationale: 2-way duplicate: all members share the identical recorded target identity (firestarter_app/tests/test_py32_flash_map_host.py:391). _associate()'s group-cardinality check could not attribute each member to a specific surviving span (record<->span ATTRIBUTION is ambiguous), but the endpoint is attribution-invariant: the LineMap maps that one recorded target to one successor line regardless of which member 'owns' which span. Duplicate set: orig-13aa962c63cb6004, late-7bd688b0f0c1873d
- evidence: LineMap(firestarter_app/tests/test_py32_flash_map_host.py, sha=6bfa6453d1bac232eb81ab35fa7f14b50b0b291a).span/point(391,None) resolves cleanly

#### Decision orig-2ee932140f8546c0

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `duplicate_citation_shared_endpoint`
- chosen endpoint: start=103
- chosen text: `}`
- duplicate_set: orig-2ee932140f8546c0, late-2e7fad9449b6a0ce, late-da96a21e85c4c8c0
- rationale: 3-way duplicate: all members share the identical recorded target identity (firestarter/src/proms/flash_5v_page.cpp:101). _associate()'s group-cardinality check could not attribute each member to a specific surviving span (record<->span ATTRIBUTION is ambiguous), but the endpoint is attribution-invariant: the LineMap maps that one recorded target to one successor line regardless of which member 'owns' which span. Duplicate set: orig-2ee932140f8546c0, late-2e7fad9449b6a0ce, late-da96a21e85c4c8c0
- evidence: LineMap(firestarter/src/proms/flash_5v_page.cpp, sha=8695ee52c27a4bee4387c5c489afd5f3d7275e8a).span/point(101,None) resolves cleanly

#### Decision orig-4bfe86cc4c907832

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `duplicate_citation_shared_endpoint`
- chosen endpoint: start=177, end=195
- chosen text: `    // CAP-02 is being PORTED here, not invented: it shipped on origin/beta` .. `    // CAP-03 (HOST-01) is emitted for EVERY command, not just CMD_WRITE --`
- duplicate_set: orig-4bfe86cc4c907832, late-3eca6122f460f077
- rationale: 2-way duplicate: all members share the identical recorded target identity (firestarter/src/firestarter.cpp:182-200). _associate()'s group-cardinality check could not attribute each member to a specific surviving span (record<->span ATTRIBUTION is ambiguous), but the endpoint is attribution-invariant: the LineMap maps that one recorded target to one successor line regardless of which member 'owns' which span. Duplicate set: orig-4bfe86cc4c907832, late-3eca6122f460f077
- evidence: LineMap(firestarter/src/firestarter.cpp, sha=8695ee52c27a4bee4387c5c489afd5f3d7275e8a).span/point(182,200) resolves cleanly

#### Decision orig-99337c160a67c186

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `duplicate_citation_shared_endpoint`
- chosen endpoint: start=323
- chosen text: `        assert _git_porcelain(FW_ROOT) == "", (`
- duplicate_set: orig-99337c160a67c186, late-c936dd853af41730
- rationale: 2-way duplicate: all members share the identical recorded target identity (firestarter_app/tests/test_py32_asset_name_host.py:323). _associate()'s group-cardinality check could not attribute each member to a specific surviving span (record<->span ATTRIBUTION is ambiguous), but the endpoint is attribution-invariant: the LineMap maps that one recorded target to one successor line regardless of which member 'owns' which span. Duplicate set: orig-99337c160a67c186, late-c936dd853af41730
- evidence: LineMap(firestarter_app/tests/test_py32_asset_name_host.py, sha=6bfa6453d1bac232eb81ab35fa7f14b50b0b291a).span/point(323,None) resolves cleanly

### Class: `retired` (172 records)

#### Decision late-2ae7c8f79fa48ec7

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `retired` | retire_cause: `could_not_be_relocated`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: The engine's own LineMap produced no viable clamp for this record at all. A full-file verbatim search (content-bearing occurrences only) found: target file missing or recorded text is not content-bearing. No unique candidate exists; not guessed.
- evidence: firestarter/src/json_parser.c: target file missing or recorded text is not content-bearing

#### Decision late-30d48f3f6499e662

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `retired` | retire_cause: `could_not_be_relocated`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: The engine's own LineMap produced no viable clamp for this record at all. A full-file verbatim search (content-bearing occurrences only) found: target file missing or recorded text is not content-bearing. No unique candidate exists; not guessed.
- evidence: firestarter/src/json_parser.c: target file missing or recorded text is not content-bearing

#### Decision late-39cefbd683226d5f

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `retired` | retire_cause: `could_not_be_relocated`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: The engine's own LineMap produced no viable clamp for this record at all. A full-file verbatim search (content-bearing occurrences only) found: target file missing or recorded text is not content-bearing. No unique candidate exists; not guessed.
- evidence: firestarter/src/json_parser.c: target file missing or recorded text is not content-bearing

#### Decision late-3b1cfd854122e223

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `retired` | retire_cause: `could_not_be_relocated`
- chosen endpoint: none (retired)
- chosen text: n/a
- duplicate_set: orig-6b0a4a84647fcf20, late-3b1cfd854122e223
- rationale: Duplicate-target group at firestarter/src/proms/eeprom_28c.cpp:199-201 -- LineMap span inverted (end<start) -- self-contradictory, does not resolve. Per operator ruling, a non-resolving successor is retired, not guessed.
- evidence: LineMap attempt: start=201 end=191 (LineMap span inverted (end<start) -- self-contradictory, does not resolve)

#### Decision late-66063d466e4ee138

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `retired` | retire_cause: `could_not_be_relocated`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: The engine's own LineMap produced no viable clamp for this record at all. A full-file verbatim search (content-bearing occurrences only) found: 0 start match(es). No unique candidate exists; not guessed.
- evidence: firestarter/src/json_parser.c: 0 start match(es)

#### Decision late-7dea267cef181135

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `retired` | retire_cause: `could_not_be_relocated`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: The engine's own LineMap produced no viable clamp for this record at all. A full-file verbatim search (content-bearing occurrences only) found: 1 start match(es), 0 end match(es). No unique candidate exists; not guessed.
- evidence: firestarter/src/proms/memory.cpp: 1 start match(es), 0 end match(es)

#### Decision late-a7d18d052a75b66f

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `retired` | retire_cause: `could_not_be_relocated`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: The engine's own LineMap produced no viable clamp for this record at all. A full-file verbatim search (content-bearing occurrences only) found: 0 start match(es). No unique candidate exists; not guessed.
- evidence: firestarter/src/json_parser.c: 0 start match(es)

#### Decision late-c321587ef86ca98a

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `retired` | retire_cause: `could_not_be_relocated`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: The engine's own LineMap produced no viable clamp for this record at all. A full-file verbatim search (content-bearing occurrences only) found: target file missing or recorded text is not content-bearing. No unique candidate exists; not guessed.
- evidence: firestarter/src/json_parser.c: target file missing or recorded text is not content-bearing

#### Decision late-e264ef9317ac2c1a

- review_kind: `composite_diff_non_survivor` | classification: `supplemental_non_survivor`
- disposition: `retired` | retire_cause: `could_not_be_relocated`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: The engine's own LineMap produced no viable clamp for this record at all. A full-file verbatim search (content-bearing occurrences only) found: target file missing or recorded text is not content-bearing. No unique candidate exists; not guessed.
- evidence: firestarter/src/json_parser.c: target file missing or recorded text is not content-bearing

#### Decision orig-02fd18603dd6a4b4

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:495 no longer contains any citation to memory.cpp at all (recorded target_line=337). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:495 for memory.cpp (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-02ffb5d8aa1c514e

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:941 no longer contains any citation to firestarter/submit.py at all (recorded target_line=73). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:941 for firestarter/submit.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-030541e3be6fc527

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:889 no longer contains any citation to eeprom_28c.cpp at all (recorded target_line=126). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:889 for eeprom_28c.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-03338ebbaf7d2ea3

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3552 no longer contains any citation to ../firestarter/include/rurp_shield.h at all (recorded target_line=46). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3552 for ../firestarter/include/rurp_shield.h (anchor_L) found 0 surviving spans (recorded N=2 vs current M=0)

#### Decision orig-0547917d944d8e6f

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:539 no longer contains any citation to eprom.cpp at all (recorded target_line=114). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:539 for eprom.cpp (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-0af3bb61c28bb3da

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:942 no longer contains any citation to cli_handlers.py at all (recorded target_line=576). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:942 for cli_handlers.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-0f7a7fa660b93a52

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3795 no longer contains any citation to cli_handlers.py at all (recorded target_line=797). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3795 for cli_handlers.py (colon_list) found 0 surviving spans (recorded N=2 vs current M=0)

#### Decision orig-11c4fc265f62a012

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:757 no longer contains any citation to database.py at all (recorded target_line=638). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:757 for database.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-1339cadce8817e2b

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:326 no longer contains any citation to check_size_baseline.py at all (recorded target_line=697). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:326 for check_size_baseline.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-1365b21ef5230820

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3515 no longer contains any citation to cli_handlers.py at all (recorded target_line=1355). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3515 for cli_handlers.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-13c028617f848ee7

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/todos/pending/phase-44-read-timing-knobs-missing-json-parse-reset.md:21 no longer contains any citation to firestarter/src/firestarter.cpp at all (recorded target_line=33). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/todos/pending/phase-44-read-timing-knobs-missing-json-parse-reset.md:21 for firestarter/src/firestarter.cpp (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-13fb229ed04e724e

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:939 no longer contains any citation to chip_test.py at all (recorded target_line=273). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:939 for chip_test.py (colon_range) found 0 surviving spans (recorded N=2 vs current M=0)

#### Decision orig-14dce94ecddd12e5

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3795 no longer contains any citation to cli_handlers.py at all (recorded target_line=810). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3795 for cli_handlers.py (colon_list) found 0 surviving spans (recorded N=2 vs current M=0)

#### Decision orig-1596fbc0b3129a69

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/todos/pending/phase-44-read-timing-knobs-missing-json-parse-reset.md:28 no longer contains any citation to firestarter/src/json_parser.c at all (recorded target_line=83). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/todos/pending/phase-44-read-timing-knobs-missing-json-parse-reset.md:28 for firestarter/src/json_parser.c (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-161cf32929e80d3d

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3578 no longer contains any citation to ../firestarter/src/operation_utils.cpp at all (recorded target_line=281). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3578 for ../firestarter/src/operation_utils.cpp (anchor_L) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-16489ffb29a4b99f

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3573 no longer contains any citation to firestarter/src/operation_utils.cpp at all (recorded target_line=271). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3573 for firestarter/src/operation_utils.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-1786d7f6bf6eafa5

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:509 no longer contains any citation to eprom.cpp at all (recorded target_line=20). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:509 for eprom.cpp (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-19a7630006e364f7

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `target_file_never_resolved`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: This record's target_file_cited was never resolved to a real path at manifest-build time (resolution_reason='basename matches no candidate') -- there is no file to compute a LineMap successor against. Not a sweep-provenance or drift issue; a manifest-time resolution failure.
- evidence: manifest record: resolution='unresolved', target_file_cited='test_flash_path_record_sync.py'

#### Decision orig-2205db8b9b6487e7

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:1114 no longer contains any citation to firestarter/include/eprom_budget.h at all (recorded target_line=28). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:1114 for firestarter/include/eprom_budget.h (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-2359b3616e033324

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:941 no longer contains any citation to tests/test_submit.py at all (recorded target_line=237). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:941 for tests/test_submit.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-2454de30d54876b6

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:929 no longer contains any citation to test_sdp_harness.cpp at all (recorded target_line=291). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:929 for test_sdp_harness.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-27c952ef95ae51a9

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:887 no longer contains any citation to firestarter/include/eprom_budget.h at all (recorded target_line=28). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:887 for firestarter/include/eprom_budget.h (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-281aad54cc4caaf9

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `could_not_be_relocated`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: The engine's own LineMap produced no viable clamp for this record at all. A full-file verbatim search (content-bearing occurrences only) found: target file missing or recorded text is not content-bearing. No unique candidate exists; not guessed.
- evidence: firestarter/src/json_parser.c: target file missing or recorded text is not content-bearing

#### Decision orig-28355c791c4de41f

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4211 no longer contains any citation to cli_handlers.py at all (recorded target_line=2456). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4211 for cli_handlers.py (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-2da90d89f293df5e

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:938 no longer contains any citation to cli_handlers.py at all (recorded target_line=1831). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:938 for cli_handlers.py (colon_range) found 0 surviving spans (recorded N=3 vs current M=0)

#### Decision orig-2db85c4e00c0759c

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:756 no longer contains any citation to firestarter_app/firestarter/ic_layout.py at all (recorded target_line=582). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:756 for firestarter_app/firestarter/ic_layout.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-2dcbd2ed46f022b5

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:941 no longer contains any citation to tests/test_submit.py at all (recorded target_line=301). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:941 for tests/test_submit.py (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-2e0fb3d6ffee661e

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/STATE.md:2096 no longer contains any citation to eprom.cpp at all (recorded target_line=274). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/STATE.md:2096 for eprom.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-2ff5efa3e66babf0

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/STATE.md:2150 no longer contains any citation to eprom.cpp at all (recorded target_line=217). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/STATE.md:2150 for eprom.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-30a4ee7747382c3c

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:489 no longer contains any citation to firestarter/src/json_parser.c at all (recorded target_line=279). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:489 for firestarter/src/json_parser.c (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-34a722710e676b7b

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4266 no longer contains any citation to firestarter/src/proms/eprom.cpp at all (recorded target_line=100). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4266 for firestarter/src/proms/eprom.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-39e4c40eb4242bf3

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:1114 no longer contains any citation to firestarter/src/proms/eprom_params.cpp at all (recorded target_line=50). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:1114 for firestarter/src/proms/eprom_params.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-3a30daf3993abd23

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:584 no longer contains any citation to eprom_params.cpp at all (recorded target_line=52). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:584 for eprom_params.cpp (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-3a4f13190fa626a6

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `target_file_never_resolved`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: This record's target_file_cited was never resolved to a real path at manifest-build time (resolution_reason='basename matches no candidate') -- there is no file to compute a LineMap successor against. Not a sweep-provenance or drift issue; a manifest-time resolution failure.
- evidence: manifest record: resolution='unresolved', target_file_cited='test_cap03_ack_layout_parity.py'

#### Decision orig-3bae46d352c56609

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4209 no longer contains any citation to cli_handlers.py at all (recorded target_line=2333). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4209 for cli_handlers.py (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-3cbf75644ace1bdc

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4209 no longer contains any citation to chip_test.py at all (recorded target_line=170). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4209 for chip_test.py (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-3e075edd33f7c9da

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4215 no longer contains any citation to chip_test.py at all (recorded target_line=2751). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4215 for chip_test.py (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-3fb3e84a44224486

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:1643 no longer contains any citation to build_db.py at all (recorded target_line=714). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:1643 for build_db.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-3fc46c2ab01eb0f5

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:938 no longer contains any citation to cli_handlers.py at all (recorded target_line=1760). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:938 for cli_handlers.py (colon_range) found 0 surviving spans (recorded N=3 vs current M=0)

#### Decision orig-417c312869b60922

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4267 no longer contains any citation to firestarter_app/firestarter/database.py at all (recorded target_line=594). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4267 for firestarter_app/firestarter/database.py (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-43bde19b52b2b673

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:740 no longer contains any citation to constants.py at all (recorded target_line=72). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:740 for constants.py (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-4697e11e9d20d944

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3937 no longer contains any citation to cli_handlers.py at all (recorded target_line=2098). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3937 for cli_handlers.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-48022cd6a884f0bd

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/STATE.md:573 no longer contains any citation to src/database.c at all (recorded target_line=39). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/STATE.md:573 for src/database.c (anchor_L_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-487a67392cd4be46

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:1637 no longer contains any citation to include/flash_utils.h at all (recorded target_line=48). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:1637 for include/flash_utils.h (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-4951d27fe65f908e

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3792 no longer contains any citation to eprom_operations.py at all (recorded target_line=1428). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3792 for eprom_operations.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-4a4946464944f797

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:938 no longer contains any citation to cli_handlers.py at all (recorded target_line=1811). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:938 for cli_handlers.py (colon_range) found 0 surviving spans (recorded N=3 vs current M=0)

#### Decision orig-4af2c58e50ea3172

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:939 no longer contains any citation to diagnostic_report.py at all (recorded target_line=177). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:939 for diagnostic_report.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-4b2bd5742798e0cf

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3804 no longer contains any citation to cli_handlers.py at all (recorded target_line=1355). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3804 for cli_handlers.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-4c1b3ae1967d63ae

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3947 no longer contains any citation to eprom_operations.py at all (recorded target_line=301). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3947 for eprom_operations.py (colon_list) found 0 surviving spans (recorded N=2 vs current M=0)

#### Decision orig-4ec3cd7bf1b21757

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3519 no longer contains any citation to ../firestarter/src/proms/eprom_params.cpp at all (recorded target_line=50). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3519 for ../firestarter/src/proms/eprom_params.cpp (anchor_L_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-53d6fc060eb38206

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:739 no longer contains any citation to eprom_operations.py at all (recorded target_line=1736). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:739 for eprom_operations.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-547693c438cb9780

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/todos/pending/phase-44-read-timing-knobs-missing-json-parse-reset.md:55 no longer contains any citation to firestarter/src/json_parser.c at all (recorded target_line=83). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/todos/pending/phase-44-read-timing-knobs-missing-json-parse-reset.md:55 for firestarter/src/json_parser.c (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-55952db2378d4074

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4209 no longer contains any citation to chip_test.py at all (recorded target_line=1285). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4209 for chip_test.py (colon_single) found 0 surviving spans (recorded N=2 vs current M=0)

#### Decision orig-5c0591a107c66f86

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:510 no longer contains any citation to eprom.cpp at all (recorded target_line=177). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:510 for eprom.cpp (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-5d8cfb001e46d74b

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `target_file_never_resolved`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: This record's target_file_cited was never resolved to a real path at manifest-build time (resolution_reason='basename matches no candidate') -- there is no file to compute a LineMap successor against. Not a sweep-provenance or drift issue; a manifest-time resolution failure.
- evidence: manifest record: resolution='unresolved', target_file_cited='test_requirement_case_mapping_v131.py'

#### Decision orig-5d9374bd8a11e90c

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/STATE.md:2096 no longer contains any citation to memory.cpp at all (recorded target_line=249). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/STATE.md:2096 for memory.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-5e8b8522a318d55e

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4321 no longer contains any citation to ../firestarter_app/tools/check_dispatch.py at all (recorded target_line=79). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4321 for ../firestarter_app/tools/check_dispatch.py (anchor_L_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-60d5d5be4c834825

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:887 no longer contains any citation to firestarter/src/proms/eprom_params.cpp at all (recorded target_line=50). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:887 for firestarter/src/proms/eprom_params.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-61f4ce9fc9b7d78b

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `target_file_never_resolved`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: This record's target_file_cited was never resolved to a real path at manifest-build time (resolution_reason='basename matches no candidate') -- there is no file to compute a LineMap successor against. Not a sweep-provenance or drift issue; a manifest-time resolution failure.
- evidence: manifest record: resolution='unresolved', target_file_cited='test_json_key_parity.py'

#### Decision orig-64a9d6696e899d91

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3519 no longer contains any citation to eprom_params.cpp at all (recorded target_line=50). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3519 for eprom_params.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-671118d76cdd4b15

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4221 no longer contains any citation to devtest-triage/scripts/devtest_issues.py at all (recorded target_line=393). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4221 for devtest-triage/scripts/devtest_issues.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-67cb6e179e05cdd9

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `target_file_never_resolved`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: This record's target_file_cited was never resolved to a real path at manifest-build time (resolution_reason='basename matches no candidate') -- there is no file to compute a LineMap successor against. Not a sweep-provenance or drift issue; a manifest-time resolution failure.
- evidence: manifest record: resolution='unresolved', target_file_cited='test_trace_segment_exhaustiveness_v131.py'

#### Decision orig-69a482da17c4d0cc

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4233 no longer contains any citation to serial_comm.py at all (recorded target_line=520). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4233 for serial_comm.py (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-6aed293321e15b11

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:1497 no longer contains any citation to database.py at all (recorded target_line=591). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:1497 for database.py (colon_single) found 0 surviving spans (recorded N=2 vs current M=0)

#### Decision orig-6b0a4a84647fcf20

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `could_not_be_relocated`
- chosen endpoint: none (retired)
- chosen text: n/a
- duplicate_set: orig-6b0a4a84647fcf20, late-3b1cfd854122e223
- rationale: Duplicate-target group at firestarter/src/proms/eeprom_28c.cpp:199-201 -- LineMap span inverted (end<start) -- self-contradictory, does not resolve. Per operator ruling, a non-resolving successor is retired, not guessed.
- evidence: LineMap attempt: start=201 end=191 (LineMap span inverted (end<start) -- self-contradictory, does not resolve)

#### Decision orig-6b5dc208c7085484

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3552 no longer contains any citation to firestarter/include/rurp_shield.h at all (recorded target_line=46). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3552 for firestarter/include/rurp_shield.h (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-6bdb4e5879b81eaa

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4120 no longer contains any citation to ../firestarter/src/proms/eprom_params.cpp at all (recorded target_line=50). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4120 for ../firestarter/src/proms/eprom_params.cpp (anchor_L) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-6d2359051315bee1

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:653 no longer contains any citation to cli_handlers.py at all (recorded target_line=2098). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:653 for cli_handlers.py (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-6db7b85b05ee0275

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3649 no longer contains any citation to eprom_params.cpp at all (recorded target_line=50). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3649 for eprom_params.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-6e5ca068f97bbb39

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:732 no longer contains any citation to cli_handlers.py at all (recorded target_line=1961). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:732 for cli_handlers.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-70322ca4bedb7012

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:887 no longer contains any citation to firestarter/src/proms/eprom.cpp at all (recorded target_line=430). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:887 for firestarter/src/proms/eprom.cpp (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-708879dd9ff6d0ab

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:283 no longer contains any citation to logging_id.h at all (recorded target_line=105). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:283 for logging_id.h (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-71602cc0ee5fcf4f

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/STATE.md:2027 no longer contains any citation to eprom_operations.py at all (recorded target_line=301). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/STATE.md:2027 for eprom_operations.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-728f06132a85ee34

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `target_file_never_resolved`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: This record's target_file_cited was never resolved to a real path at manifest-build time (resolution_reason='basename matches no candidate') -- there is no file to compute a LineMap successor against. Not a sweep-provenance or drift issue; a manifest-time resolution failure.
- evidence: manifest record: resolution='unresolved', target_file_cited='test_cap03_ack_layout_parity.py'

#### Decision orig-733c204fcd9e50cf

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:552 no longer contains any citation to firestarter_app/firestarter/serial_comm.py at all (recorded target_line=66). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:552 for firestarter_app/firestarter/serial_comm.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-74592d5effd071e4

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3947 no longer contains any citation to eprom_operations.py at all (recorded target_line=377). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3947 for eprom_operations.py (colon_list) found 0 surviving spans (recorded N=2 vs current M=0)

#### Decision orig-7483ce8414244343

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/STATE.md:1683 no longer contains any citation to eprom_info.py at all (recorded target_line=69). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/STATE.md:1683 for eprom_info.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-76082f5e9118d92d

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:574 no longer contains any citation to cli_handlers.py at all (recorded target_line=110). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:574 for cli_handlers.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-776b2418db8f2f95

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:939 no longer contains any citation to submit.py at all (recorded target_line=169). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:939 for submit.py (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-7943b6f16fe9acab

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4221 no longer contains any citation to tests/test_parse_devtest_issue.py at all (recorded target_line=138). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4221 for tests/test_parse_devtest_issue.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-7965f9a60b32a218

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:284 no longer contains any citation to eprom_operations.cpp at all (recorded target_line=57). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:284 for eprom_operations.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-7b2145b9745dbe08

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:465 no longer contains any citation to build_db.py at all (recorded target_line=807). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:465 for build_db.py (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-7bd29dbff15f416c

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:1617 no longer contains any citation to memory.cpp at all (recorded target_line=163). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:1617 for memory.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-7e3c49bd4cf8d74e

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3895 no longer contains any citation to eprom.cpp at all (recorded target_line=177). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3895 for eprom.cpp (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-7ff537545021d349

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3578 no longer contains any citation to firestarter/src/operation_utils.cpp at all (recorded target_line=281). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3578 for firestarter/src/operation_utils.cpp (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-81fa1ed552ff89f4

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:415 no longer contains any citation to serial_comm.py at all (recorded target_line=866). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:415 for serial_comm.py (colon_single) found 0 surviving spans (recorded N=2 vs current M=0)

#### Decision orig-82822c05b40b8130

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4267 no longer contains any citation to ../firestarter_app/firestarter/database.py at all (recorded target_line=594). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4267 for ../firestarter_app/firestarter/database.py (anchor_L_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-82dc7d38692dcdfb

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:478 no longer contains any citation to t48.c at all (recorded target_line=250). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:478 for t48.c (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-885aa03b34c1b10e

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4209 no longer contains any citation to chip_test.py at all (recorded target_line=568). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4209 for chip_test.py (colon_single) found 0 surviving spans (recorded N=2 vs current M=0)

#### Decision orig-8915041d09d8321c

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:900 no longer contains any citation to constants.py at all (recorded target_line=107). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:900 for constants.py (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-8b420335d005f182

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3552 no longer contains any citation to ../firestarter/include/rurp_shield.h at all (recorded target_line=49). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3552 for ../firestarter/include/rurp_shield.h (anchor_L) found 0 surviving spans (recorded N=2 vs current M=0)

#### Decision orig-8b727b937e8d2321

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:574 no longer contains any citation to include/eprom_params.h at all (recorded target_line=51). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:574 for include/eprom_params.h (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-8e600525cf57c328

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/STATE.md:1058 no longer contains any citation to 123/check_permitted_claims.py at all (recorded target_line=74). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/STATE.md:1058 for 123/check_permitted_claims.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-8e844d1fc0648f2f

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:1607 no longer contains any citation to check_size_baseline.py at all (recorded target_line=697). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:1607 for check_size_baseline.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-90b46b91416ad9e6

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/STATE.md:2096 no longer contains any citation to eprom.cpp at all (recorded target_line=283). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/STATE.md:2096 for eprom.cpp (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-920d7e12f69be9c4

- review_kind: `hand_choice_re_deletion` | classification: `known_post154_non_survivor`
- disposition: `retired` | retire_cause: `moved_with_semantic_change`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: LOG_ERROR_ID_BYTES(MSG_ERR_CHIP_ID_MISMATCH, _b, 4) is absent from eeprom_28c.cpp entirely. It moved to memory.cpp:301 AND was refactored into LOG_ID_BYTES(warn_only ? MSG_WARN_CHIP_ID_MISMATCH : MSG_ERR_CHIP_ID_MISMATCH, _b, 4) -- a genuine warn/err branch was added. A line-number remap must not follow a citation across files into changed semantics; that is inventing meaning. Successor named for a human to follow: memory.cpp:301. Do not retarget.
- evidence: grep -rn LOG_ERROR_ID_BYTES / MSG_ERR_CHIP_ID_MISMATCH across firestarter/src,include; found only at memory.cpp:301 in refactored form

#### Decision orig-925143e840922fdf

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/STATE.md:1645 no longer contains any citation to primitives.cpp at all (recorded target_line=121). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/STATE.md:1645 for primitives.cpp (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-96367b8178a33ceb

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:573 no longer contains any citation to firestarter/src/proms/eprom_params.cpp at all (recorded target_line=49). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:573 for firestarter/src/proms/eprom_params.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-988a3c8eddad9165

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3547 no longer contains any citation to ../firestarter/src/rurp_config_utils.cpp at all (recorded target_line=32). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3547 for ../firestarter/src/rurp_config_utils.cpp (anchor_L_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-9b6c353989d3e73a

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3547 no longer contains any citation to firestarter/src/rurp_config_utils.cpp at all (recorded target_line=32). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3547 for firestarter/src/rurp_config_utils.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-9ba16238e2fe15ed

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4215 no longer contains any citation to diagnostic_report.py at all (recorded target_line=1015). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4215 for diagnostic_report.py (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-9bb3f950fe153c47

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4266 no longer contains any citation to ../firestarter/src/proms/eprom.cpp at all (recorded target_line=100). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4266 for ../firestarter/src/proms/eprom.cpp (anchor_L_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-a021b2884f18be6f

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:1497 no longer contains any citation to database.py at all (recorded target_line=638). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:1497 for database.py (colon_single) found 0 surviving spans (recorded N=2 vs current M=0)

#### Decision orig-a56f81108e4c34b7

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/STATE.md:1818 no longer contains any citation to eprom_operations.py at all (recorded target_line=301). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/STATE.md:1818 for eprom_operations.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-a64f22e26b0a0211

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/STATE.md:2102 no longer contains any citation to eprom.cpp at all (recorded target_line=283). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/STATE.md:2102 for eprom.cpp (anchor_L) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-a75222a1653c4b74

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:741 no longer contains any citation to eprom_operations.py at all (recorded target_line=301). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:741 for eprom_operations.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-a7a4010b929742d1

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:543 no longer contains any citation to memory.cpp at all (recorded target_line=163). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:543 for memory.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-aa43d5d04c724668

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3658 no longer contains any citation to eprom_params.h at all (recorded target_line=53). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3658 for eprom_params.h (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-aae59710b0bcff21

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4317 no longer contains any citation to ../firestarter_app/tools/build_db.py at all (recorded target_line=117). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4317 for ../firestarter_app/tools/build_db.py (anchor_L) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-adf02f58d694ea98

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `target_file_never_resolved`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: This record's target_file_cited was never resolved to a real path at manifest-build time (resolution_reason='basename matches no candidate') -- there is no file to compute a LineMap successor against. Not a sweep-provenance or drift issue; a manifest-time resolution failure.
- evidence: manifest record: resolution='unresolved', target_file_cited='test_json_key_parity.py'

#### Decision orig-aeb70c4e164832c2

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:484 no longer contains any citation to eprom.cpp at all (recorded target_line=70). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:484 for eprom.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-af2f601e2fbb4743

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4424 no longer contains any citation to test_chip_resolver.py at all (recorded target_line=43). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4424 for test_chip_resolver.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-b099847c1daee762

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:465 no longer contains any citation to database.c at all (recorded target_line=130). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:465 for database.c (anchor_L_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-b0b8c1d95ea2e62e

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:1637 no longer contains any citation to eeprom_28c.cpp at all (recorded target_line=126). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:1637 for eeprom_28c.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-b39bbb040f05a6ea

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3649 no longer contains any citation to ../firestarter/src/proms/eprom_params.cpp at all (recorded target_line=50). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3649 for ../firestarter/src/proms/eprom_params.cpp (anchor_L_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-b47b8c37ec14a0e0

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:1037 no longer contains any citation to database.c at all (recorded target_line=1918). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:1037 for database.c (anchor_L) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-b7450ce5d5ba372b

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/STATE.md:2023 no longer contains any citation to cli_handlers.py at all (recorded target_line=653). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/STATE.md:2023 for cli_handlers.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-b9867ceff64661bc

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4120 no longer contains any citation to eprom_params.cpp at all (recorded target_line=50). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4120 for eprom_params.cpp (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-ba82010f7d8baa3b

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4317 no longer contains any citation to firestarter_app/tools/build_db.py at all (recorded target_line=117). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4317 for firestarter_app/tools/build_db.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-bae3c87a33ddd99a

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:757 no longer contains any citation to firestarter_app/firestarter/database.py at all (recorded target_line=591). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:757 for firestarter_app/firestarter/database.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-c0511d18c401861d

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:554 no longer contains any citation to memory.cpp at all (recorded target_line=307). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:554 for memory.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-c39d025c1cd6b8d2

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:96 no longer contains any citation to check_size_baseline.py at all (recorded target_line=697). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:96 for check_size_baseline.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-c3c41f1f389d5054

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:497 no longer contains any citation to firestarter/src/proms/eprom.cpp at all (recorded target_line=90). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:497 for firestarter/src/proms/eprom.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-c5c5b0317ea9a678

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:198 no longer contains any citation to cli_handlers.py at all (recorded target_line=2503). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:198 for cli_handlers.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-c7f978dc27efdb8d

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:494 no longer contains any citation to firestarter/src/proms/memory.cpp at all (recorded target_line=238). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:494 for firestarter/src/proms/memory.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-c94f4694f65a18bc

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3547 no longer contains any citation to firestarter/include/rurp_shield.h at all (recorded target_line=49). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3547 for firestarter/include/rurp_shield.h (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-cb8f4e1ec93a81a7

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3947 no longer contains any citation to constants.py at all (recorded target_line=72). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3947 for constants.py (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-cbd43093acbfbb22

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4211 no longer contains any citation to diagnostic_report.py at all (recorded target_line=942). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4211 for diagnostic_report.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-cc4ff29b3ce7a84b

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:369 no longer contains any citation to cli_handlers.py at all (recorded target_line=2503). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:369 for cli_handlers.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-cd04ff03b43f9463

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/STATE.md:1063 no longer contains any citation to usb_cdc.c at all (recorded target_line=20). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/STATE.md:1063 for usb_cdc.c (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-cf757de5d4499cbb

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:1637 no longer contains any citation to firestarter/src/proms/eeprom_28c.cpp at all (recorded target_line=105). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:1637 for firestarter/src/proms/eeprom_28c.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-cfce640ae7175364

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:498 no longer contains any citation to eprom_params.cpp at all (recorded target_line=50). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:498 for eprom_params.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-cfcfe2f8e355295e

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:541 no longer contains any citation to rurp_shield.h at all (recorded target_line=114). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:541 for rurp_shield.h (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-d1393de5880c270f

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4221 no longer contains any citation to devtest-rootcause/scripts/seed_debug_session.py at all (recorded target_line=280). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4221 for devtest-rootcause/scripts/seed_debug_session.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-d14cccc7db2af06b

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:888 no longer contains any citation to firestarter/src/proms/eeprom_28c.cpp at all (recorded target_line=105). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:888 for firestarter/src/proms/eeprom_28c.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-d1c2c0243c3d26ea

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/STATE.md:2318 no longer contains any citation to flash_5v_page.cpp at all (recorded target_line=88). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/STATE.md:2318 for flash_5v_page.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-d228bb8776ee589c

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:490 no longer contains any citation to firestarter/include/firestarter.h at all (recorded target_line=197). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:490 for firestarter/include/firestarter.h (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-daa814caebd78965

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4219 no longer contains any citation to diagnostic_report.py at all (recorded target_line=316). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4219 for diagnostic_report.py (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-dad06f601a230c14

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4209 no longer contains any citation to diagnostic_report.py at all (recorded target_line=967). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4209 for diagnostic_report.py (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-dc10752ee12f8d44

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:1034 no longer contains any citation to test_protocol_branch_inventory.py at all (recorded target_line=446). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:1034 for test_protocol_branch_inventory.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-dfcd5c2b23ddd62e

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `target_file_never_resolved`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: This record's target_file_cited was never resolved to a real path at manifest-build time (resolution_reason='basename matches no candidate') -- there is no file to compute a LineMap successor against. Not a sweep-provenance or drift issue; a manifest-time resolution failure.
- evidence: manifest record: resolution='unresolved', target_file_cited='test_trace_segment_exhaustiveness_v131.py'

#### Decision orig-e0e5447195d1c695

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:574 no longer contains any citation to eprom_info.py at all (recorded target_line=269). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:574 for eprom_info.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-e176f13047cfe8bf

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3573 no longer contains any citation to ../firestarter/src/operation_utils.cpp at all (recorded target_line=271). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3573 for ../firestarter/src/operation_utils.cpp (anchor_L_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-e40ffee6d36740a1

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:755 no longer contains any citation to cli_handlers.py at all (recorded target_line=856). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:755 for cli_handlers.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-e4ee4ae59082ca87

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `target_file_never_resolved`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: This record's target_file_cited was never resolved to a real path at manifest-build time (resolution_reason='basename matches no candidate') -- there is no file to compute a LineMap successor against. Not a sweep-provenance or drift issue; a manifest-time resolution failure.
- evidence: manifest record: resolution='unresolved', target_file_cited='test_requirement_case_mapping_v131.py'

#### Decision orig-e6334031c7cba97f

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:415 no longer contains any citation to serial_comm.py at all (recorded target_line=412). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:415 for serial_comm.py (colon_single) found 0 surviving spans (recorded N=2 vs current M=0)

#### Decision orig-e68994f61d69c8a6

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:939 no longer contains any citation to chip_test.py at all (recorded target_line=319). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:939 for chip_test.py (colon_range) found 0 surviving spans (recorded N=2 vs current M=0)

#### Decision orig-ec2c8af61b397fdd

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/STATE.md:2254 no longer contains any citation to 139-check-claims.py at all (recorded target_line=98). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/STATE.md:2254 for 139-check-claims.py (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-f026c20210d896ad

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3547 no longer contains any citation to ../firestarter/include/rurp_shield.h at all (recorded target_line=49). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3547 for ../firestarter/include/rurp_shield.h (anchor_L) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-f4459e335eb6ebed

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:888 no longer contains any citation to flash_utils.cpp at all (recorded target_line=61). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:888 for flash_utils.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-f4c06bfa246aad7d

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:4321 no longer contains any citation to firestarter_app/tools/check_dispatch.py at all (recorded target_line=79). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:4321 for firestarter_app/tools/check_dispatch.py (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-f5f12372c946b80b

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:942 no longer contains any citation to chip_test.py at all (recorded target_line=737). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:942 for chip_test.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-f62f91e614bef2f9

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:940 no longer contains any citation to chip_test.py at all (recorded target_line=505). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:940 for chip_test.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-f6f051271eeaf21c

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:576 no longer contains any citation to eprom_params.cpp at all (recorded target_line=41). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:576 for eprom_params.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-f8cd579666c1489d

- review_kind: `hand_choice_re_deletion` | classification: `known_post154_non_survivor`
- disposition: `retired` | retire_cause: `ambiguous_generic_text`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Bare '} else {' has two candidate occurrences in eeprom_28c.cpp (lines 277, 585); the anchor context (301-336, preceding a LOG_ERROR_ID_BYTES call) is too generic to disambiguate. The citation carries no semantic payload worth guessing at.
- evidence: grep -n '} else {' firestarter/src/proms/eeprom_28c.cpp -> 2 matches

#### Decision orig-f974424a5a69f1f2

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:752 no longer contains any citation to firestarter/src/proms/eeprom_28c.cpp at all (recorded target_line=547). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:752 for firestarter/src/proms/eeprom_28c.cpp (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-f9746ea89ae5cc44

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:876 no longer contains any citation to include/flash_utils.h at all (recorded target_line=48). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:876 for include/flash_utils.h (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-f9ac554bbb8524cf

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:465 no longer contains any citation to build_db.py at all (recorded target_line=193). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:465 for build_db.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-fac3bbfe4dd29dae

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `could_not_be_relocated`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: The engine's own LineMap produced no viable clamp for this record at all. A full-file verbatim search (content-bearing occurrences only) found: target file missing or recorded text is not content-bearing. No unique candidate exists; not guessed.
- evidence: firestarter/src/json_parser.c: target file missing or recorded text is not content-bearing

#### Decision orig-fb1166d5a2f78c61

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:3795 no longer contains any citation to diagnostic_report.py at all (recorded target_line=336). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:3795 for diagnostic_report.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-fba3f8eb0cde660b

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:753 no longer contains any citation to firestarter_app/firestarter/database.py at all (recorded target_line=638). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:753 for firestarter_app/firestarter/database.py (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-fd5c2f1e95d0f545

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/ROADMAP.md:1114 no longer contains any citation to firestarter/src/proms/eprom.cpp at all (recorded target_line=430). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/ROADMAP.md:1114 for firestarter/src/proms/eprom.cpp (colon_single) found 0 surviving spans (recorded N=1 vs current M=0)

#### Decision orig-fe3ed192763c1141

- review_kind: `composite_diff_non_survivor` | classification: `ordinary_original_non_survivor`
- disposition: `retired` | retire_cause: `citation_absent_from_citing_document`
- chosen endpoint: none (retired)
- chosen text: n/a
- rationale: Living-document drift: .planning/PROJECT.md:888 no longer contains any citation to memory.cpp at all (recorded target_line=259). The line was hand-rewritten between the Phase-154 sweep and now (not a sweep-provenance reword). Phase 159 remaps citations that exist; it does not resurrect ones a later hand-edit deleted.
- evidence: regex re-scan of .planning/PROJECT.md:888 for memory.cpp (colon_range) found 0 surviving spans (recorded N=1 vs current M=0)

## Deviations from Plan

### Auto-fixed / operator-ruled issues

**1. [Rule 4-adjacent, operator-ruled] `sweep-outcome-record.md` §4 misread, corrected before use**
- **Found during:** Round 2 planning for the composite non-survivor residue
- **Issue:** I initially proposed cross-referencing `sweep-outcome-record.md` §4 to resolve reworded citations, believing it was a survivor-attribution table. The coordinator corrected this: §4 is "Per-group residual, fully attributed -- 198 of 198," an accounting of regex hits deliberately left alone (D-02-exempt lines, retained test IDs, Ruling-B-exempt files), not a location map.
- **Fix:** Abandoned the cross-reference plan entirely; used the engine's own diff-computed `LineMap` clamp as the sole successor for reworded citations (`diff_provenance_reworded`), exactly as ruled.
- **Committed in:** this SUMMARY only (no code change; a planning-path correction).

**2. [Rule 1 - self-caught bug] Blank-line/punctuation false matches in the range-shrink end-boundary search**
- See "Method Note -- Class-B Blank-Line Self-Catch" above. Fixed before being reported; all `range_shrunk_verbatim_endpoints` decisions reflect the corrected search.

**3. [Rule 1 - bug] Ruling B's initial duplicate-target grouping conflated resolved and never-resolved records**
- **Found during:** implementing operator Ruling B (duplicate citations sharing a target identity)
- **Issue:** 9 of the 29 "ambiguous duplicate" records had `target_file_resolved: null` (`resolution: "unresolved", resolution_reason: "basename matches no candidate"`) at manifest-build time -- they were never resolvable to a real file, and their apparent "duplicate" target-line match with a genuinely-resolved sibling record was coincidental (both carried the same historic line number, but only one had a file to map it against).
- **Fix:** Split the 29 into 9 `target_file_never_resolved` (retired immediately, no `LineMap` possible) and 20 genuinely-resolved records, then applied Ruling B's `LineMap`-successor approach only to the resolved set (grouped into 14 true target-identity groups). One of those 14 groups (`eeprom_28c.cpp` 199-201, 2 records) produced a self-contradictory inverted span (`start=201 > end=191`) and was retired as `could_not_be_relocated` rather than accepted at face value.
- **Verification:** All 20 resolved-set records now have `resolved: true` with a sane (non-inverted) `LineMap` successor except the 2 retired for the inversion; totals reconcile to exactly 29.

No other deviations. All prior-round findings (engine-coverage gap, defective historical-anchor candidate set) are recorded as Blockers above, not fixed here, per this plan's no-file-mutation constraint.

## Issues Encountered

- The plan's own prose (`review_kind` values `semantic_target`/`planning_location`) does not match the measured ledger's actual `review_kind` values (`composite_diff_non_survivor`, `hand_choice_re_deletion`, `historical_anchor`). Per this plan's own critical-phase constraint, the ledger was treated as authoritative throughout; this SUMMARY uses the ledger's real field values, not the plan's prose terms.
- `git status --porcelain`'s `firestarter_app` line changed from `?? firestarter_app` (fully untracked) at session start to `M firestarter_app` mid-session. Investigated and confirmed unrelated to this plan's work: the gitlink SHA (`38f0d839...`) is stable and matches the superproject's recorded HEAD; the `M` is solely from pre-existing untracked files inside the submodule (`SECURITY.md`, `datasheets/*.pdf`, `write_test_port.sh`, `.planning/config.json`), none of which intersect any citation target or overlay authorization in this phase. No action taken.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- All 515 pending records and both overlay authorizations are decided and durably recorded above. Plan 159-04 can transcribe every `chosen_current_start`/`chosen_current_end`/`chosen_current_text[_end]` (or `retired`/`retire_cause`) into `159-remap-exceptions.jsonl` by stable record ID.
- Plan 159-04 must first close the three Blockers above (engine-coverage gap for 21 IDs, `anchor_record()`'s missing pre-sweep candidate, and the missing `RETIRED` disposition/`Outcome`) before "apply these decisions mechanically by stable ID" is fully true for every decided record in this SUMMARY.
- `.planning/v1.33/CITATIONS-STALE.md` remains present, as required until Plan 159-06's close gate.
- No manifest, ledger file, corpus byte, source file, or marker was modified by this checkpoint -- only this SUMMARY.md was created.

---
*Phase: 159-citation-remap-milestone-close*
*Completed: 2026-08-24*
