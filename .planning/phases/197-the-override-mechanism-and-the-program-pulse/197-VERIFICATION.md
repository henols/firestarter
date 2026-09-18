---
phase: 197-the-override-mechanism-and-the-program-pulse
verified: 2026-09-18T15:33:01Z
status: passed
score: 4/5 roadmap success criteria verified (1 decision-backed deferral, accepted); requirement traceability 8/10 Complete, 2 Pending (OVR-03, PULSE-04) — PULSE-01 was Pending at verification time and has since been marked Complete, see resolved_since_verification
covered_files:
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-01-PLAN.md
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-01-SUMMARY.md
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-02-PLAN.md
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-02-SUMMARY.md
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-03-PLAN.md
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-03-SUMMARY.md
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-04-PLAN.md
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-04-SUMMARY.md
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-05-PLAN.md
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-05-SUMMARY.md
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-06-PLAN.md
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-06-SUMMARY.md
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-07-PLAN.md
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-07-SUMMARY.md
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-08-PLAN.md
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-08-SUMMARY.md
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-REVIEW.md
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-REGEN-DIFF.md
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-PULSE-INVENTORY.md
  - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-GH70-ANSWER.md
  - .planning/REQUIREMENTS.md
  - firestarter_app/tools/build_db.py
  - firestarter_app/tools/datasheet_overrides.json
  - firestarter_app/tools/DECODE-NOTES.md
  - firestarter_app/tests/test_datasheet_overrides.py
  - firestarter_app/tests/test_build_db_constant_census.py
  - firestarter_app/tests/golden/build_db_part_specific_constants.json
  - firestarter_app/tests/test_build_db_pinout_fork.py
  - firestarter_app/tests/test_build_db_inclusion.py
  - firestarter_app/tests/test_wire_dict_equivalence.py
  - firestarter_app/tests/golden/wire_dict_expected_deltas_197.json
  - firestarter_app/tests/golden/chip_database_field_inventory.json
  - firestarter_app/tests/__snapshots__/test_characterization.ambr
  - firestarter_app/firestarter/data/chip_database.json
covered_digest: "v1:sha256:da6078e385e93c5160b0862f31807b20c2b3532b2d6be73a1820eb629ce515b7"
covered_digest_reanchored: "2026-09-18 — re-anchored by the orchestrator with `query verification fingerprint` after the close edits landed (999.72 filed, PULSE-01 marked Complete, overrides recorded). The verifier computed its digest at 15:33Z, before those edits, so it was already stale on arrival — the documented behaviour of this gate in this repo, not evidence of drift. No covered file changed content between the verifier reading it and this re-anchor except .planning/REQUIREMENTS.md, whose PULSE-01 edit is recorded above. Expect it to read stale again after phase.complete writes ROADMAP.md and REQUIREMENTS.md."
behavior_unverified: 0
overrides_applied: 3
status_changed_by: "orchestrator, on operator decision 2026-09-18 — the verifier's verdict was gaps_found (4/5 criteria). The operator was shown the four gaps and chose 'Mark complete, accept both'. Status set to passed so phase.complete would run. The verifier's original verdict, its evidence and the full gaps: block below are left UNEDITED — nothing was removed to make this pass."
overrides:
  - must_have: "gh#70 carries the answer and the version that holds it (ROADMAP SC5 / PULSE-04)."
    reason: "Accepted as a decision-backed carry-forward, not as achieved. The operator selected `hold` on 2026-09-18: the milestone branch has no upstream in either repo, so any version or commit the comment could cite does not exist for a reader to check. The draft is authored, content-verified and committed; gh#70 confirmed live as OPEN with 3 comments, none from this project. Closes at the v1.40 beta cut per the four steps in 197-GH70-ANSWER.md's 'Held-pending deferral' section. PULSE-04 remains Pending in REQUIREMENTS.md and is NOT claimed complete."
    accepted_by: "operator"
    accepted_at: "2026-09-18"
  - must_have: "OVR-03: the datasheet citation contract is enforced by the generator itself, not only by the test suite."
    reason: "Accepted as carried forward. The override file's shape satisfies OVR-03's literal text on all 9 entries, but WR-03 shows `_validate_datasheet_overrides_shape` does not check git-tracked status or reject a `..`-escaping path, so a standalone `python tools/build_db.py` would accept a citation the test suite would reject. OVR-03 remains Pending in REQUIREMENTS.md; its substantive route is the WR-03 hardening, which belongs with backlog 999.72 in the same mechanism. Separately, the verifier found OVR-03 was orphaned across plans — recorded in the orchestrator addendum below."
    accepted_by: "operator"
    accepted_at: "2026-09-18"
  - must_have: "The override mechanism is general across all six fields it advertises as overridable (CR-01)."
    reason: "Accepted with tracking, not disputed. The verifier's verdict is adopted verbatim: the mechanism is general for four of its six advertised fields and silently half-applied for `electrical.pin_count` and `electrical.size_bytes`. Dormant — all 9 shipped entries target the four safe fields. The verifier recorded 'no backlog entry ... as of this verification'; that was true when it began reading and stale by the time it wrote — backlog 999.72 was filed at efa71d21, 2026-09-18T15:28:10Z, mid-run. Operator chose file-only over patching so this phase's byte-identity proofs and verified state stay untouched."
    accepted_by: "operator"
    accepted_at: "2026-09-18"
resolved_since_verification:
  - "PULSE-01 — the verifier's gap 3 was a real bookkeeping omission and is now FIXED, not overridden. 197-07-SUMMARY.md claimed `requirements-completed: [PULSE-01]` while REQUIREMENTS.md still read Pending. The substantive work was independently confirmed present by both the verifier and the orchestrator (tools/DECODE-NOTES.md section 8, 197-PULSE-INVENTORY.md), and 197-07 is the sole plan declaring PULSE-01, so no shared-ID gate applied. Marked Complete at 5fa1ecf7." 
gaps:
  - truth: "gh#70 carries the answer and the version that holds it (ROADMAP SC5 / PULSE-04)"
    status: failed
    reason: "Deliberately, explicitly deferred by an operator decision (`hold`, 2026-09-18) recorded in 197-08-SUMMARY.md and 197-GH70-ANSWER.md. Confirmed live: gh#70 is still OPEN with exactly 3 comments (checked via `gh issue view 70 --repo henols/firestarter`), none from this project — nothing has been posted. The stated reason is sound: the milestone branch has no upstream and resolves to no remote branch in either repo, so any version or commit the comment could cite does not exist yet for a reader to check. The verifier agrees this deferral is legitimate and not an execution failure, but it leaves ROADMAP success criterion 5 and requirement PULSE-04 genuinely unmet as of this verification."
    artifacts:
      - path: ".planning/phases/197-the-override-mechanism-and-the-program-pulse/197-GH70-ANSWER.md"
        issue: "Comment body fully drafted and content-verified, but Status is 'DRAFT — APPROVED, HELD PENDING THE BETA CUT. NOT POSTED.' PULSE-04 is correctly left Pending in REQUIREMENTS.md."
    missing:
      - "Post the '## Comment Body' section verbatim to gh#70 once a real published version exists (at the v1.40 beta cut), per the four steps in 197-GH70-ANSWER.md's 'Held-pending deferral' section, then mark PULSE-04 Complete."
      - "Alternatively, if the phase is to close now with this accepted as a known, decision-backed carry-forward, add a `overrides:` entry to this file's frontmatter recording that acceptance (see suggestion in the report body)."
  - truth: "OVR-03: every override entry's datasheet citation is both recorded AND enforced as resolvable/non-escaping by the generator itself, not only by the test suite"
    status: partial
    reason: "The override file's shape satisfies OVR-03's literal text — every one of the 9 shipped entries carries `datasheet`, `note`, and `{was, is}` per field, verified directly by reading tools/datasheet_overrides.json. But code review finding WR-01 (197-REVIEW.md, confirmed by direct read of build_db.py:410-422) shows `_validate_datasheet_overrides_shape` does not check that a cited path is git-tracked and does not reject a `..`-escaping path — that stronger contract is enforced only by a test (`test_every_datasheet_value_is_a_tracked_path_or_unsourced_with_note`), not by `python tools/build_db.py` run standalone, which is the documented regen command. REQUIREMENTS.md accurately reflects this as Pending; no plan's `requirements-completed` ever claims OVR-03 (197-01 and 197-02 are the only two plans that declare it, and both explicitly defer it)."
    artifacts:
      - path: "firestarter_app/tools/build_db.py"
        issue: "_validate_datasheet_overrides_shape (lines ~365-422) accepts any existing relative path as a valid, non-UNSOURCED datasheet citation without checking git-tracked status or rejecting path escape."
    missing:
      - "Move the git-tracked check and a `..`-segment rejection into _validate_datasheet_overrides_shape itself (WR-03's suggested fix), or explicitly accept the test-only enforcement as sufficient for OVR-03's closure and mark it Complete with that rationale recorded."
  - truth: "PULSE-01's finding is written down and the requirement is closed out in REQUIREMENTS.md"
    status: partial
    reason: "The substantive work is genuinely done and verified directly: tools/DECODE-NOTES.md section 8 exists with the confirmed decode rule, the MBM27C4001 positive proof, the 462/675 bulk-default falsification, the firmware wire-semantics argument, and the fail-closed empty-input note — all independently confirmed against the live file. 197-PULSE-INVENTORY.md exists with the reproducible query, the 297/215 census (independently reproduced by the orchestrator per this task's ground truth), and every one of the 12 Fujitsu rows disposed with a verdict. However, 197-07-SUMMARY.md claims `requirements-completed: [PULSE-01]` and states 'PULSE-01 is fully answered' in Next Phase Readiness, yet no commit in this phase's git history touches .planning/REQUIREMENTS.md for PULSE-01 (`git log --oneline -- .planning/REQUIREMENTS.md` shows no 197-07 commit), and REQUIREMENTS.md still shows `[ ] PULSE-01` / Pending. This is a bookkeeping omission, not a content gap: the SUMMARY over-claims relative to what was actually written to REQUIREMENTS.md."
    artifacts:
      - path: ".planning/REQUIREMENTS.md"
        issue: "PULSE-01 checkbox and traceability row still read Pending despite the underlying work (DECODE-NOTES.md §8, 197-PULSE-INVENTORY.md) being substantively complete and verified."
    missing:
      - "Check off PULSE-01 in REQUIREMENTS.md and change its traceability row to Complete, now that the substantive content has been independently verified."
  - truth: "The override mechanism is general across all six fields it advertises as overridable (electrical.size_bytes, electrical.pin_count, electrical.vpp_mv, electrical.vcc_mv, electrical.vdd_mv, programming.pulse_duration_us)"
    status: failed
    reason: "CONFIRMED by direct code read, matching 197-REVIEW.md's CR-01 (critical, unaddressed at time of this verification): `_OVERRIDABLE_DECODED_FIELDS` (build_db.py ~line 356) declares six overridable fields, but `apply_datasheet_override` runs at line ~687, AFTER `resolve_pinout_key` (line ~641, forks on raw `pin_count`/`mem_size`) and `classify()` (line ~668, also forks on raw `mem_size`) have already consumed the un-overridden values. An override targeting `electrical.pin_count` or `electrical.size_bytes` would silently write a corrected value into the emitted row while `pinout` and `programming.algorithm` stay computed from the stale, pre-override value — an internally inconsistent database row with no error and no test catching it. This is dormant today (all 9 shipped entries target vpp_mv/vcc_mv/vdd_mv/pulse_duration_us, which ARE genuinely general because nothing downstream of the override point consumes them before the override applies), but it means the phase's stated goal — 'a datasheet value can correct an infoic decode without a line of part-specific code' — is true for 4 of the 6 advertised fields and silently false/dangerous for the other 2. No backlog entry, fix, or explicit accepted-risk decision addresses this as of this verification; it is not mentioned in the three backlog entries (999.69/70/71) 197-07 filed."
    artifacts:
      - path: "firestarter_app/tools/build_db.py"
        issue: "Lines ~356-361 declare electrical.size_bytes and electrical.pin_count overridable; lines ~630-687 consume the raw (pre-override) values of both before apply_datasheet_override ever runs."
    missing:
      - "Either (a) split override application into a pre-classification pass for size_bytes/pin_count and a post-classification pass for the other four fields (197-REVIEW.md's option a), or (b) narrow _OVERRIDABLE_DECODED_FIELDS to the four fields the current call site can honor correctly and raise on an attempt to override the other two until (a) lands — and either way, file a backlog entry so the gap is tracked rather than left silent."
deferred: []
advisory: []
human_verification: []
---

# Phase 197: The override mechanism and the program pulse — Verification Report

**Phase Goal:** A datasheet value can correct an infoic decode without a line of part-specific code
in the generator, and the first correction proves it on the pulse width gh#70 measured.
**Verified:** 2026-09-18T15:33:01Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Summary

The core deliverable is real and works. I independently re-derived, rather than trusted, the
central claims: I ran the loader/applier/census test modules directly (27 + 9 = 36 tests, all
green), read `tools/build_db.py` line by line at every cited location, parsed
`tools/datasheet_overrides.json` directly (9 entries, sorted, 6 `UNSOURCED`, matching the given
ground truth exactly), confirmed the three vendored datasheets are git-tracked, confirmed zero
comment lines were added anywhere in the phase's Python diff against `70c92ce`, and confirmed via
`gh issue view 70` that gh#70 is still open with exactly 3 comments and nothing posted by this
project. All of that matches the phase's own claims.

But four things keep this from a clean pass, and none of them is invisible or deniable once you
read the code and the requirement ledger side by side rather than the SUMMARYs' own framing:

1. **PULSE-04 / ROADMAP success criterion 5 is genuinely unmet** — deliberately so, on a sound
   operator decision, but unmet nonetheless.
2. **OVR-03 is correctly tracked as Pending** — the shipped file structurally satisfies it, but the
   generator itself doesn't enforce the datasheet-provenance contract the phase actually built
   (only the test suite does — 197-REVIEW.md's WR-03).
3. **PULSE-01's underlying work is done and verified, but REQUIREMENTS.md was never updated** to
   reflect it, despite the plan's own SUMMARY claiming it was — a pure bookkeeping miss, not a
   content gap.
4. **The override mechanism is not actually general across the 6 fields it advertises.** Two of
   the six declared-overridable fields (`electrical.pin_count`, `electrical.size_bytes`) are
   consumed by `resolve_pinout_key`/`classify()` before the override ever applies. This is
   197-REVIEW.md's CR-01 — rated critical by the phase's own code review, confirmed here by direct
   code reading, and still unaddressed at the time of this verification.

## Goal Achievement — ROADMAP Success Criteria

| # | Success Criterion | Status | Evidence |
|---|---|---|---|
| 1 | An override entry changes a generated value, and deleting the entry restores the decoded one. | ✓ VERIFIED | `datasheet_overrides.json` parsed directly (9 entries). `197-02-SUMMARY.md`'s round-trip claim is structurally consistent with the code: `apply_datasheet_override` mutates a `_decoded_view` dict read back into the locals used by `chip_entry`; removing the file/entry leaves those locals at their raw decoded values. `197-REGEN-DIFF.md`'s "two zero-diff claims" section independently proves the mechanism is reversible for the six NMOS entries (byte-identical regen with the entries removed vs. present). |
| 2 | `build_db.py` contains no part-number literal after the three hardcodes move out, or every survivor is named with proof no alternative exists. | ✓ VERIFIED | Ran `tests/test_build_db_constant_census.py` directly: passes. Read `tests/golden/build_db_part_specific_constants.json` directly: exactly one survivor, `"DIP28"`, a pinout-family prefix (not a part number) with a substantive reason recorded. Matches the orchestrator's ground truth exactly. |
| 3 | The generator fails closed, with a legible message, on an unknown part, an unknown field, and a no-op override. | ✓ VERIFIED | Ran `tests/test_datasheet_overrides.py` directly: passes (27 tests total combined with the census module). `197-03`'s five fail-closed legs (unmatched key, duplicate target, unsorted file, type mismatch, no-op) are each backed by a named test per the SUMMARY, and the module is green against the live tree. |
| 4 | `MBM27C1000`'s `pulse_duration_us` lands inside 475–525 µs, and the full-database regeneration diff accounts for every other changed row. | ✓ VERIFIED | `tools/datasheet_overrides.json` shows `FUJITSU/MBM27C1000 → datasheets/MBM27C1000.pdf`. `197-REGEN-DIFF.md` read directly: 13/13 changed rows attributed either to a named decode rule or to a datasheet-citing override; 0 `support_status` changes; 746 in / 746 out. Matches the orchestrator's independently-measured ground truth exactly. |
| 5 | gh#70 carries the answer and the version that holds it. | ✗ FAILED (decision-backed, see below) | Confirmed live via `gh issue view 70 --repo henols/firestarter`: state OPEN, exactly 3 comments, none from this project. `197-GH70-ANSWER.md` is a fully-drafted, content-verified, but explicitly unposted draft. PULSE-04 is correctly left Pending in REQUIREMENTS.md. |

**Score:** 4/5 ROADMAP success criteria verified.

### On PULSE-04 / success criterion 5 specifically

The task asked me to assess this explicitly rather than fold it silently into a pass or a fail.

**My verdict: the deferral is legitimate.** The operator's `hold` decision (2026-09-18, recorded
verbatim in `197-08-SUMMARY.md` and `197-GH70-ANSWER.md`) rests on a fact I independently confirmed
rather than took on faith: the milestone branch has no upstream in either repository and
`git branch -r --contains` resolves nothing for the carrying commit, so naming a beta version or a
commit sha in the public comment would state something no reader could verify at the moment it
posted. Posting now would have manufactured a false claim to close a checkbox. The draft itself is
substantively complete and correctly scoped — it does not claim the reported failure is fixed, it
discloses the pinout finding (backlog 999.70) rather than withholding it, and it correctly routes
the VCC gap to Phase 200 — so the actual authoring work this requirement asks for is done. What
remains is a single external action (posting) gated on an event (the beta cut) outside this
phase's own scope.

That said, "legitimate" is not the same as "already satisfied." ROADMAP success criterion 5 and
requirement PULSE-04 are both still literally unmet, and per this verifier's decision rules a
failed roadmap-contract truth routes the phase to `gaps_found` unless it is formally accepted as an
override. I have not applied an override myself — that requires a human decision recorded in this
file's frontmatter (see the suggested override block below) — but I recommend the project accept
one rather than block phase closure on an external event this phase correctly identified it cannot
manufacture.

**This looks intentional and well-evidenced. To accept this deviation, add to this file's
frontmatter:**

```yaml
overrides:
  - must_have: "gh#70 carries the answer and the version that holds it."
    reason: "Draft fully authored and content-verified (197-GH70-ANSWER.md); posting is gated on the v1.40 beta cut producing a real, resolvable version string. Posting earlier would have named a version or commit no reader could verify. Operator explicitly selected `hold` on 2026-09-18 with the reasoning recorded verbatim in 197-08-SUMMARY.md."
    accepted_by: "<human>"
    accepted_at: "<ISO timestamp>"
```

## The Override Mechanism's Generality — CR-01 Assessed

The task asked for a plain verdict on whether the mechanism is genuinely general or general only
for the four fully-hoisted fields. **Verdict: general only for four of the six fields it
advertises.**

I read `firestarter_app/tools/build_db.py` directly rather than relying on the review's line
citations:

- `_OVERRIDABLE_DECODED_FIELDS` (~line 356) lists six dotted paths: `electrical.size_bytes`,
  `electrical.pin_count`, `electrical.vpp_mv`, `electrical.vcc_mv`, `electrical.vdd_mv`,
  `programming.pulse_duration_us`.
- `resolve_pinout_key(pin_count, variant, flags, ..., mem_size=mem_size)` runs at ~line 641, and
  `classify(type_int, proto_id, pm_idx, flags, pinout_key, mem_size)` runs at ~line 668 — both
  consuming the **raw**, pre-override `pin_count`/`mem_size`.
- `_decoded_view` is built at ~line 672 (after both of the above) and `apply_datasheet_override` is
  called at ~line 687. Only after that does `mem_size`/`pin_count` get read back from the
  (possibly-overridden) view — but `pinout_key` and `proto_id` were already fixed using the
  un-overridden values three lines earlier.

Concretely: an override entry targeting `electrical.pin_count` or `electrical.size_bytes` would
change the emitted `electrical.pin_count`/`electrical.size_bytes` field, while `pinout` and
`programming.algorithm` stay whatever `resolve_pinout_key`/`classify` computed from the original,
uncorrected value — an internally inconsistent row, shipped with no error and no test catching it.
The four fields that ARE genuinely general (`vpp_mv`, `vcc_mv`, `vdd_mv`, `pulse_duration_us`) are
general precisely because nothing between the raw decode and the override point consumes them —
they are read for the first time downstream of the override.

This is exactly what `197-REVIEW.md` calls CR-01 and rates critical. It remains **unaddressed**:
no backlog entry references it (999.69/70/71, filed by `197-07`, are about the 100 µs inventory,
the MBM27C1000 pinout swap, and the six UNSOURCED VPP entries respectively — none is this), no code
change follows it, and no accepted-risk decision is recorded anywhere in the phase's artifacts.

It is dormant today: all 9 shipped override entries target the four safe fields. But Phase 198
("The two voltage nibbles") and Phase 199 ("RAIL") are the next consumers of this exact mechanism,
and if either ever needs to correct a decoded `pin_count` or `size_bytes` (for example, a part
whose infoic-decoded package size is wrong), this defect activates silently. I recommend either
fixing the ordering per the review's option (a), narrowing `_OVERRIDABLE_DECODED_FIELDS` to the
four safe fields per option (b) as an immediate low-risk mitigation, or filing this explicitly to
the backlog so it isn't lost before Phase 198 starts.

## Requirements Coverage

| Requirement | Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| OVR-01 | 197-02 | Single override file beside `tools/extra_chips.json`, generator applies on top of infoic decode | ✓ SATISFIED | `tools/datasheet_overrides.json` exists, loader/applier tested and run directly. REQUIREMENTS.md: Complete. |
| OVR-02 | 197-03 | An entry holds only fields that differ; a no-op field is not an entry | ✓ SATISFIED | `test_mbm27c4001_noop_entry_raises` and the no-op fail-closed leg verified via test run. REQUIREMENTS.md: Complete. |
| OVR-03 | 197-01, 197-02 (both defer it; no later plan ever claims it) | Every entry names its datasheet and the decoded value it replaces, readable without running the generator | ⚠ PARTIAL | Shipped file structurally satisfies the literal text. WR-03 (confirmed by direct code read) shows the stronger git-tracked/no-escape contract is test-only, not loader-enforced. Correctly Pending in REQUIREMENTS.md — but genuinely orphaned: no plan's `requirements-completed` ever claims it. |
| OVR-04 | 197-03 | Fails closed on unknown part, unknown field, no-op override | ✓ SATISFIED | 5 fail-closed legs, all test-verified directly. REQUIREMENTS.md: Complete. |
| OVR-05 | 197-03, 197-04 | Three hardcodes move into the override file with unchanged generated output | ✓ SATISFIED | `NMOS_TRUE_VPP_MV`, `_AT28C_DIP24_NAMES`, `_ETYPE_RELABEL` all confirmed absent from live `build_db.py`; byte-identical regeneration claims consistent with `197-REGEN-DIFF.md`'s zero-diff sections. REQUIREMENTS.md: Complete. |
| OVR-06 | 197-01, 197-05 | Any surviving part-specific constant is named with proof no alternative exists | ✓ SATISFIED | Golden census file read directly: one survivor (`DIP28`), reasoned. REQUIREMENTS.md: Complete. |
| PULSE-01 | 197-07 | What `pulse_delay` encodes is established per algorithm family, written down | ⚠ PARTIAL (content done, tracking not) | `tools/DECODE-NOTES.md` §8 read directly and matches every must-have (positive proof, bulk-default falsification, wire semantics, fail-closed empty input). `197-PULSE-INVENTORY.md` read directly and is substantively complete. But REQUIREMENTS.md was never updated — still `[ ]` Pending — despite `197-07-SUMMARY.md`'s `requirements-completed: [PULSE-01]` claim. No commit in `git log -- .planning/REQUIREMENTS.md` touches PULSE-01. |
| PULSE-02 | 197-02, 197-05 | MBM27C1000 pulse inside 475–525 µs window | ✓ SATISFIED | 500 µs confirmed directly in the shipped override file and REGEN-DIFF. REQUIREMENTS.md: Complete. |
| PULSE-03 | 197-05, 197-06 | Regeneration diff measured across all 746 rows, every changed row explained | ✓ SATISFIED | `197-REGEN-DIFF.md` and the wire-dict 197 delta layer both read directly; full suite run confirmed green on the wire-dict test module. REQUIREMENTS.md: Complete. |
| PULSE-04 | 197-08 | gh#70 answered with resulting values and the version | ✗ NOT SATISFIED (decision-backed) | Confirmed live: issue still open, 3 comments, nothing posted. Correctly Pending in REQUIREMENTS.md. See dedicated section above. |

No orphaned requirements: all 10 IDs the phase declares (OVR-01..06, PULSE-01..04) appear in the
ROADMAP phase header and are accounted for above; the traceability table in REQUIREMENTS.md lists
exactly these 10 against Phase 197.

## Code Review Findings Carried Into This Verification (197-REVIEW.md)

| ID | Severity | Status at verification | My independent check |
|---|---|---|---|
| CR-01 | Critical | Unaddressed | Confirmed by direct code read (see dedicated section above). Real, dormant, undermines the phase goal's generality claim for 2 of 6 advertised fields. |
| WR-01 | Warning | Unaddressed | Not independently re-verified beyond the review's own text; plausible from the code structure (`written_by` is a per-call-scoped dict). Dormant — no shipped alias collision exists today. |
| WR-02 | Warning | Unaddressed | Confirmed by direct code read: line ~708 unconditionally recomputes `_d_pulse` from raw `pulse_delay` when the VPP ceiling fires, discarding any override-corrected value. Dormant — no shipped row combines an overridden pulse with a ceiling-triggering VPP today. |
| WR-03 | Warning | Unaddressed | Confirmed by direct code read: `_validate_datasheet_overrides_shape` does not check git-tracked status or reject `..`-escaping paths; that check exists only in `tests/test_datasheet_overrides.py`. This is the substantive reason OVR-03 correctly remains Pending. |
| WR-04 | Warning | Unaddressed | Confirmed by direct read of `tools/datasheet_overrides.json`: all six `UNSOURCED` notes end "No [vendor] datasheet ... is vendored ... Closed by: [vendor]'s own ... datasheet, vendored and git-tracked under datasheets/." — the second sentence reads as a present-tense claim immediately following a sentence stating the opposite. Cosmetic but real; a careless reader could misread an UNSOURCED entry as already datasheet-confirmed. |

None of these four warnings, nor CR-01, is fixed in a diff since the review was written
(2026-09-18, same day as this verification) — the review is the last artifact produced before this
verification ran, and nothing in the phase's commit history postdates it.

## Anti-Pattern Scan

- **Debt markers (TBD/FIXME/XXX):** zero, checked directly against the full phase diff
  (`git diff 70c92ce` across `tools/build_db.py`, `tools/datasheet_overrides.json`,
  `tools/DECODE-NOTES.md`, and all five touched test modules).
- **Added comment lines in `.py` files:** zero, checked directly with a Python-based line scan of
  the full `git diff 70c92ce -- '*.py'` (not the shell `grep`, which mis-tokenized on this
  environment's `ugrep`-backed `grep`). This matches CLAUDE.md's hard no-comments rule and the
  phase's own repeated self-checks.
- **Placeholder / stub returns:** none found in the reviewed files; `apply_datasheet_override` and
  `load_datasheet_overrides` are substantive, not stubs.
- **`firestarter_fw` untouched:** confirmed — `git log --since="2026-09-18"` in that submodule shows
  no commits; branch is on `v1.40-program-parameter-fidelity` at the same tip as the fork point,
  satisfying the phase's host-only prohibition.

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Loader/applier fail-closed legs + shipped-file contract | `pytest tests/test_datasheet_overrides.py -o addopts="" -q` | 18 passed | ✓ PASS |
| OVR-06 constant census (frozen golden, non-vacuity controls) | `pytest tests/test_build_db_constant_census.py -o addopts="" -q` | 9 passed | ✓ PASS |
| Wire-dict equivalence, all five layers incl. the 197 delta | `pytest tests/test_wire_dict_equivalence.py -o addopts="" -q` | 9 passed | ✓ PASS |
| Shipped override file shape | `python3 -c "json.load(...)"` on `tools/datasheet_overrides.json` | 9 entries, sorted, 6 UNSOURCED | ✓ PASS — matches given ground truth exactly |
| Three vendored datasheets git-tracked | `git ls-files --error-unmatch` × 3 | all tracked | ✓ PASS |
| gh#70 state | `gh issue view 70 --repo henols/firestarter --json state,comments` | OPEN, 3 comments, none from this project | ✓ PASS — confirms nothing was posted |
| No `.py` comment lines added anywhere in the phase | Python line-scan of `git diff 70c92ce -- '*.py'` | 0 matches | ✓ PASS |

Full-suite result not independently re-run in full here (per the "run the full suite at most once"
constraint); the orchestrator's reported `2065 passed, 0 failed, 32 snapshots` is accepted as given
ground truth, and the two test modules most load-bearing for this phase's own new behavior
(`test_datasheet_overrides.py`, `test_wire_dict_equivalence.py`) were re-run here directly and both
pass.

## Human Verification Required

None. Every remaining gap in this report is either independently confirmed via code reading and
direct test execution (OVR-03, PULSE-01 tracking, CR-01) or already carries an explicit, recorded
operator decision (PULSE-04). What remains is a project decision — accept the PULSE-04 deferral
formally via an override, fix or accept CR-01, correct the PULSE-01 tracking omission, and decide
OVR-03's disposition — not a behavior only a human can observe.

## Gaps Summary

Four items keep this phase from a clean pass, none of them hidden by the SUMMARYs (in fact,
`197-07-SUMMARY.md` and `197-08-SUMMARY.md` both name their own gaps candidly) but none of them
resolved either:

1. **PULSE-04 / SC5** — decision-backed, legitimate, but literally unmet. Needs either the beta-cut
   posting or a formal override to close the phase honestly.
2. **OVR-03** — correctly Pending; the stronger provenance contract this phase built is enforced
   only by tests, not by the generator itself (WR-03).
3. **PULSE-01 tracking** — the actual work is done and verified; REQUIREMENTS.md simply was never
   updated to say so. A one-line fix.
4. **CR-01** — the override mechanism is general for 4 of the 6 fields it advertises; the other 2
   would silently corrupt a row if ever used. Dormant today, unaddressed, and directly relevant to
   how literally the phase's own goal statement should be read going into Phase 198.

---

_Verified: 2026-09-18T15:33:01Z_
_Verifier: Claude (gsd-verifier)_

---

## Orchestrator addendum — 2026-09-18

Written after the verifier returned. It corrects one gap that went stale mid-run and records the
disposition of the two requirements left Pending, so neither reads as an oversight later.

### Gap 2 (CR-01 "unaddressed") is STALE — a backlog entry exists

The verifier reported CR-01 as having "no backlog entry, no fix, no accepted-risk note". That was
true when it began reading and false by the time it wrote. **Backlog entry `999.72` was filed at
`efa71d21`, 2026-09-18T15:28:10Z**, while the verifier was still running.

The *finding* stands exactly as the verifier states it, and the orchestrator confirmed it
independently against the live source before filing: `apply_datasheet_override` lands at
`build_db.py:687`, after `resolve_pinout_key` (`:642`) and `classify` (`:670`) have consumed raw
`pin_count` and `mem_size`, while both fields are declared overridable at `:357-358`.

**The verifier's verdict on the goal question is accepted and is the right framing: the mechanism
is general for four of its six advertised fields** — `vpp_mv`, `vcc_mv`, `vdd_mv` and
`pulse_duration_us` — and half-applied for `pin_count` and `size_bytes`. Operator decision
2026-09-18 was to file rather than patch, leaving this phase's byte-identity proofs and verified
state untouched. `999.72` carries both remediation routes and names the proofs a real fix must
re-run.

### OVR-03 stays Pending — two independent reasons, both deliberate

1. **Substantive (WR-03).** The git-tracked-path / no-`..`-escape contract is enforced only by
   `tests/test_datasheet_overrides.py::TestShippedOverrideFileContract`, not by `build_db.py`
   itself. A standalone `python tools/build_db.py` — the documented regeneration command — would
   accept an override citing an uncommitted or out-of-repo file. OVR-03 asks that every entry name
   its datasheet; today the generator does not enforce that on its own.
2. **Bookkeeping (verifier's finding, confirmed).** OVR-03 is declared in the frontmatter of
   `197-01` and `197-02` only. `197-01` deferred it to "later plans"; `197-02` deferred it to
   `197-03`; and `197-03`'s frontmatter is `[OVR-02, OVR-04, OVR-05]` — it never declares OVR-03.
   The requirement was deferred forward until nothing was left holding it.

   **`197-02-SUMMARY.md` asserts that "OVR-03 also appears in … 197-03's frontmatter". It does
   not.** Verified by reading the frontmatter directly. This is the same false-citation class this
   phase produced twice before (a SUMMARY reporting three deleted comments against an actual 18,
   and a proposed ROADMAP anchor matching two phases). Treat a SUMMARY's claim about another
   plan's frontmatter as a claim to check.

Leaving OVR-03 Pending is therefore correct on the merits, independently of the orphaning. The
substantive route to closing it is the WR-03 hardening recorded in `197-REVIEW.md`, which belongs
with `999.72` — both are gaps in the same mechanism.

### PULSE-01 was a genuine bookkeeping miss and is now fixed

`197-07-SUMMARY.md:54` claimed `requirements-completed: [PULSE-01]` but REQUIREMENTS.md was never
updated. The underlying work was verified present by both the verifier and the orchestrator
(`tools/DECODE-NOTES.md` § 8 and `197-PULSE-INVENTORY.md`), and `197-07` is the sole plan declaring
PULSE-01, so no shared-ID gate applied. Marked Complete by hand.

### PULSE-04 stays Pending by operator decision

The operator chose `hold` on the gh#70 answer: it is a committed draft and nothing was posted.
The verifier independently confirmed gh#70 is OPEN with 3 comments, none from this project. It
closes when the comment posts at the v1.40 beta cut, per `197-GH70-ANSWER.md` § "Held-pending
deferral". This leaves ROADMAP success criterion 5 literally unmet — deliberately.

### Final requirement tally

8 of 10 Complete. OVR-03 and PULSE-04 Pending, both by decision rather than omission.
