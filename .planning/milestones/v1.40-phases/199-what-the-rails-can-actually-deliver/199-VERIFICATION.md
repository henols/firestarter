---
phase: 199-what-the-rails-can-actually-deliver
verified: 2026-09-19T00:00:00Z
status: passed
score: 3/5 roadmap success criteria fully verified; 1 accepted-carried-forward override (RAIL-03); 1 deliberate deferral (RAIL-05, same pattern as PULSE-04/VOLT-04)
covered_files: [".planning/REQUIREMENTS.md", ".planning/ROADMAP.md", ".planning/phases/197-the-override-mechanism-and-the-program-pulse/197-GH70-ANSWER.md", ".planning/phases/199-what-the-rails-can-actually-deliver/199-01-PLAN.md", ".planning/phases/199-what-the-rails-can-actually-deliver/199-01-SUMMARY.md", ".planning/phases/199-what-the-rails-can-actually-deliver/199-02-PLAN.md", ".planning/phases/199-what-the-rails-can-actually-deliver/199-02-SUMMARY.md", ".planning/phases/199-what-the-rails-can-actually-deliver/199-03-FIRMWARE-NOTES.md", ".planning/phases/199-what-the-rails-can-actually-deliver/199-03-PLAN.md", ".planning/phases/199-what-the-rails-can-actually-deliver/199-03-SUMMARY.md", ".planning/phases/199-what-the-rails-can-actually-deliver/199-04-PLAN.md", ".planning/phases/199-what-the-rails-can-actually-deliver/199-04-SUMMARY.md", ".planning/phases/199-what-the-rails-can-actually-deliver/199-05-PLAN.md", ".planning/phases/199-what-the-rails-can-actually-deliver/199-05-SUMMARY.md", ".planning/phases/199-what-the-rails-can-actually-deliver/199-BENCH-RECORD.md", ".planning/phases/199-what-the-rails-can-actually-deliver/199-CONTEXT.md", ".planning/phases/199-what-the-rails-can-actually-deliver/199-GH71-ANSWER.md", ".planning/phases/199-what-the-rails-can-actually-deliver/199-REGEN-DIFF.md", "firestarter_app/firestarter/data/chip_database.json", "firestarter_app/tests/__snapshots__/test_characterization.ambr", "firestarter_app/tests/golden/wire_dict_expected_deltas_199.json", "firestarter_app/tests/test_vpp_rail_classification.py", "firestarter_app/tests/test_wire_dict_equivalence.py", "firestarter_app/tools/DECODE-NOTES.md", "firestarter_app/tools/datasheet_overrides.json", "firestarter_fw/include/eprom.h", "firestarter_fw/include/rurp_pinout.h", "firestarter_fw/platformio.ini", "firestarter_fw/src/proms/eprom.cpp", "firestarter_fw/test/native/avr/test_hv_route_ceiling/host_stubs.cpp", "firestarter_fw/test/native/avr/test_hv_route_ceiling/test_hv_route_ceiling.cpp", "firestarter_fw/tests/golden/protocol_branch_inventory.json"]
covered_digest: "v1:sha256:8c591b2ab85b27ae09c3248ac77374f111b3ba039e6ed643cc32e2ace311285a"
behavior_unverified: 0
overrides_applied: 1
overrides:
  - must_have: "RAIL-03 / Roadmap SC3: a part asking more than the shield can deliver produces a warning naming both voltages, on the path the operator actually uses, and the operation still proceeds."
    reason: "Accepted as carried forward, adjudicated by the 199-05 executor and independently confirmed by this verification. The only operator-facing shortfall signal is the pre-existing, untouched `MSG_WARN_VPP_LOW` in `eprom_check_vpp`. It has the right shape (names both voltages, never refuses) but is measurably insufficient on two independently-confirmed grounds: (1) its 5% trigger window is narrower than the bench-measured +7.59%/+7.95% ADC-vs-meter discrepancy, so for 9 of the 10 rescued rows (required 18000 mV) the check stays silent even though the socket is genuinely short — reproduced arithmetically in this verification (17100 threshold vs 18700 ADC reading, both from the bench record); (2) the warning names the live ADC reading, not the deliverable-maximum figure RAIL-03 asks it to name. RAIL-03 is correctly left Pending in REQUIREMENTS.md (not silently marked Complete), the gap is named in DECODE-NOTES § 10 (\"The shortfall warning gap\"), and the reasoning is recorded in 199-05-SUMMARY.md. This verifier concurs with the adjudication: the routing fix (RAIL-04) removes the shortfall entirely for the ten drop-resistor rows, which is a strictly better outcome than a warning, but is not the same claim RAIL-03 makes, so RAIL-03 is honestly unmet rather than satisfied by proxy."
    accepted_by: "199-05 executor adjudication, confirmed sound by verifier"
    accepted_at: "2026-09-19"
deferred:
  - truth: "Roadmap SC5 / RAIL-05: gh#71 carries the answer."
    addressed_in: "v1.40 milestone close (beta cut) — the same deferral mechanism already used for PULSE-04 (gh#70) and VOLT-04 (gh#66) in Phases 197/198"
    evidence: "199-GH71-ANSWER.md exists as a complete, approved, held five-section draft (title+warning, Status, Internal provenance, Comment Body, Held-pending deferral). Its Comment Body credits @dim20, states the 18V->21V correction, explains the automatic VPE-as-VPP routing in plain language, discloses the ADC-vs-meter reasoning, names both release channels as not-yet-shipped, and states plainly that the part is not confirmed to program and that the issue stays open. Scanned clean of every internal-provenance pattern (RAIL-0x, D-NN, phase/plan ids, .planning/ paths). Verified live via `gh issue view 71`: OPEN, 3 comments (dim20 2026-09-12, henols 2026-09-16 x2), matching the draft's own stated comment-state exactly. `197-GH70-ANSWER.md` \"Held-pending deferral\" independently confirmed to name gh#71, 199-GH71-ANSWER.md, and RAIL-05 as the third entry on the one consolidated list, with a comment-state line that correctly does NOT reuse the sibling issues' false \"no comment from this project\" clause (gh#71 has two maintainer comments, gh#70/gh#66 apparently do not). REQUIREMENTS.md independently confirmed to still list RAIL-05 as Pending. Nothing was pushed or posted in any of the three repositories: `git branch -r --contains HEAD` returns empty in all three; firestarter_fw and firestarter_app HEAD are both well ahead of, and disjoint from, their own `origin/beta`."
covered_files_note: "fingerprinted via gsd-tools query verification.fingerprint; digest above is authoritative for this file's frontmatter"
---

# Phase 199: What the rails can actually deliver — Verification Report

**Phase Goal:** Replace a theoretical ceiling with a measured one, decide the VPE routing question,
and make the shield say what it cannot do instead of offering it — establish by measurement what the
RURP shield's high-voltage rails deliver at the socket, route the one rail that might reach the
stranded parts, make the classification testable, and answer gh#71 without claiming more than was
measured.

**Verified:** 2026-09-19
**Status:** passed
**Re-verification:** No — initial verification

**Design note carried into this verification.** This phase reversed its own design mid-flight (D-21,
2026-09-19, operator ruling): the VPE-routing decision moved from a planned host-side Python policy
module (`firestarter/vpp_rail_gate.py`) to firmware, inside `eprom_hv_route_mask`. The reverted host
module was built, then fully reverted (`firestarter_app@4dc1913`, `f21d9a4`, both undone) and does
**not** exist in the codebase today — confirmed by `git ls-files` (no match) and `git status`
(no match, tracked or untracked). Its absence is correct, not a gap. Every truth below was checked
against the **final** design (D-21/D-22/D-23), not the original plan text.

## Goal Achievement

### Observable Truths

All items were independently re-derived against the live codebase (both submodules' actual HEAD,
live `chip_database.json`, live firmware source, a live-run native test suite, a live-run Python test
suite in a correctly-provisioned 3.11 environment, and a live `gh issue view` call) — not accepted
from SUMMARY.md narrative.

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Roadmap SC1 / RAIL-01: a recorded deliverable maximum per rail per shield revision, method named, ADC-derived figure carrying its known error | ✓ VERIFIED | `199-BENCH-RECORD.md` records `DELIVERABLE_MAX_DROP_PATH_MV=17380` and `DELIVERABLE_MAX_DIRECT_VPE_MV=22140`, both operator-meter readings at socket pin 1, Rev 2.0 (silkscreen, operator statement, explicitly not inferred from `hw_revision`), socket empty, pot at max and untouched between readings. Paired ADC readings (`18700`, `23900`) yield +7.59%/+7.95% error figures, both falling inside the project's independently-measured 6.8–8.3% ADC figure (999.38), stated as corroborating not replacing it. `DECODE-NOTES.md` § 10 restates all of this with the same numbers. The "per shield revision" clause is honestly scoped: Rev 2.2 and modified Rev 0 are explicitly named unmeasured, not assumed — confirmed present in both the bench record's "Limits" section and § 10's own limits list, which is the condition 199-05-PLAN.md's own flagged assumption says the tick depends on. |
| 2 | Roadmap SC2 / RAIL-02: the 30 rows at 18V+ are classified against whichever ceiling stands, reproducible from the recorded numbers | ✓ VERIFIED | Independently re-derived directly from the live `firestarter_app/firestarter/data/chip_database.json`: exactly 30 rows with `vpp_mv >= 18000`, voltage histogram `{18000: 21, 21000: 3, 25000: 6}`, path split by `programming.algorithm`: algo 7 (drop-resistor) = 10 rows (9 @ 18000 + 1 @ 21000, `MBM27128`), algo 11/0x0B (direct-VPE) = 20 rows (12 @ 18000 + 2 @ 21000 + 6 @ 25000), all 30 `support_status: supported`. This exactly matches `tests/test_vpp_rail_classification.py`'s asserted census (re-run live: 9/9 pass) and `DECODE-NOTES.md` § 10's table. **The stale "all ten at 18000" claim from `199-CONTEXT.md:396` and `199-04-PLAN.md` was NOT propagated into any deliverable** — the actual test, the actual DECODE-NOTES table, and the actual regeneration diff all correctly show 9+1, confirmed by direct re-derivation, not by trusting the SUMMARY's claim that it was corrected. |
| 3 | RAIL-02 / D-01 / D-02: `RURP_VPP_CEILING_MV=25000` stays, comparison stays strict, no `support_status` moved, no second generator constant added | ✓ VERIFIED | Independently re-derived the regeneration diff against `f155364` (pre-phase baseline): 746 rows in, 746 rows out, identical key set, exactly one changed tuple `(('FUJITSU','MBM27128'), 'electrical.vpp_mv', 18000, 21000)`. Matches `199-REGEN-DIFF.md`'s claim exactly, re-run independently rather than trusted. |
| 4 | Roadmap SC4 / RAIL-04: the VPE routing question is decided and recorded, including a decision not to route it where applicable | ✓ VERIFIED | `eprom_hv_route_mask` (`firestarter_fw/src/proms/eprom.cpp:246-261`) read directly: checks `FLAG_VPE_AS_VPP` first (manual override wins, no table read), then an unresolved protocol (`row == NULL`) fails closed to the drop path (a decision NOT to route), then an already-direct-VPE row (`VPP_PATH_DIRECT_VPE`) returns the undropped rail, then the new comparison `handle->vpp_mv > RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV` (17380, defined in `rurp_pinout.h:120`) routes the undropped rail only when the drop path genuinely cannot reach the requirement. |
| 5 | RAIL-04 / D-22: routing is decided on path capability, reads no ADC voltage, and the decision is proven rather than merely asserted | ✓ VERIFIED (behavioral, not just presence) | Ran the actual native test suite live: `pio test -e native -f "*test_hv_route_ceiling*"` — all 15 cases PASSED, including the boundary triple derived from the macro itself (not a hardcoded copy), both drop-resistor protocols (0x07, 0x08), the direct-VPE protocol (0x0B) unaffected, two fail-safes (unresolved protocol at max representable voltage, zero required voltage), the manual-override-wins case, a non-vacuity proof that the voltage-read counter is live (0→1 on a direct call), and the two D-22 falsifiability cases reproducing the reversal's own two-row table (18000 mV: ADC check would stay silent while the path rule routes; 21000 mV: ADC check would fire but catches only this one row). Every routing case asserts a **zero** voltage-read count. |
| 6 | RAIL-03 / D-23: `eprom_check_vpp` is byte-unchanged; routing decoupled from future ADC calibration | ✓ VERIFIED | `git diff 7eed3af..a050730 -- src/proms/eprom.cpp` shows zero lines changed inside `eprom_check_vpp` itself — every diff line is confined to `eprom_hv_route_mask`'s doc comment and its one new guard clause. |
| 7 | D-12 reversed: the firmware's own stale routing documentation was corrected in place, not left standing | ✓ VERIFIED | Direct diff read: `eprom.cpp`'s resolution-order comment corrected (steps 1 and 3 reworded, a new step 4 added) and `eprom.h`'s declaration comment corrected to say the route no longer comes from the `vpp_path` column alone. `DECODE-NOTES.md` § 10 states this as a posture change, correctly, not as a stale sentence left standing. |
| 8 | RAIL-04 / RAIL-02: no CI/build regression from the firmware change | ✓ VERIFIED | Ran `pio run -e leonardo` live: SUCCESS, flash 23816/32768 B — exact match to the SUMMARY's claimed final figure. Ran `pytest tests/` in `firestarter_fw` live: 17 failed / 284 passed — exact match to the claimed pre-existing baseline (all 17 are the documented `test_flash_path_record_sync.py` meta-repo-presence skips, unrelated to this phase). |
| 9 | Phase-wide: no regression in `firestarter_app`'s test suite | ✓ VERIFIED | Ran the full `pytest tests/` suite live in a correctly-provisioned Python 3.11 venv (the devcontainer default 3.12 lacks `syrupy` and produces false collection errors — a known environment trap, not a phase defect): 2085 passed, 32 snapshots passed, 0 failed. Matches 199-04/199-05's claimed counts exactly. `test_vpp_rail_classification.py` and `test_wire_dict_equivalence.py` independently re-run: both fully green. |
| 10 | Three-way figure equality (bench record ↔ `rurp_pinout.h` ↔ DECODE-NOTES § 10) | ✓ VERIFIED | All three independently read: bench record's `DELIVERABLE_MAX_DROP_PATH_MV = 17380`; `rurp_pinout.h:120` `#define RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV 17380`; DECODE-NOTES § 10's fenced constant block `RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV = 17380`. All three identical. |
| 11 | Bench record does not silently contradict itself; the retraction reads as a retraction | ✓ VERIFIED | § "Consequence for this phase" explicitly labels its own superseded paragraph "**Superseded by the measurement, 2026-09-19**" before quoting it, then states plainly "Both windows were subsequently measured" and gives the final figures. Not a silent overwrite; a visible, dated retraction with the old claim kept and marked wrong. |
| 12 | Nothing overclaims (DECODE-NOTES § 10, gh#71 draft) | ✓ VERIFIED | § 10 states plainly "Nothing was written to any of the thirty parts in this work. No claim is made that any of them now programs." The D-06 pin-21 approximation is stated explicitly, with an explicit refusal to license any inference about the six 25000 mV rows. The gh#71 draft's Comment Body states "It does not mean this specific chip is confirmed to program" and names both release channels as "Neither has shipped yet" — no version, tag, or commit that does not exist is named. |
| 13 | Nothing was pushed or posted in any of the three repositories | ✓ VERIFIED | `git branch -r --contains HEAD` returns empty for `firestarter_fw`, `firestarter_app`, and the meta repo. `gh issue view 71` confirms OPEN, 3 comments, last dated 2026-09-16 — unchanged from the bench record's and the draft's stated state. |
| 14 | Roadmap SC3 / RAIL-03: a shortfall warning naming both voltages, proceeding rather than refusing or silently attempting | ⚠ UNMET, ACCEPTED AS CARRIED FORWARD (override applied) | See `overrides:` frontmatter entry. Independently reproduced the arithmetic behind the adjudication: at 18000 mV required, the 5% threshold is 17100 mV, the ADC reads 18700 mV (from the bench record), so the existing `MSG_WARN_VPP_LOW` check stays silent for 9 of the 10 rescued rows even though the socket is genuinely 620 mV short. This verifier concurs with the 199-05 adjudication that RAIL-03 is genuinely unmet, correctly disclosed (Pending in REQUIREMENTS.md, named as a limit in DECODE-NOTES § 10 "The shortfall warning gap"), and not silently claimed complete anywhere. |
| 15 | Roadmap SC5 / RAIL-05: gh#71 carries the answer | ⚠ DEFERRED (not a gap) | See `deferred:` frontmatter entry. Same held-pending-beta-cut pattern already used for PULSE-04 (gh#70) and VOLT-04 (gh#66) in Phases 197/198, verified sound in those phases and reproduced identically and correctly here. |

**Score:** 13/15 truths fully VERIFIED, 1 accepted override (RAIL-03, genuinely unmet, correctly disclosed), 1 deliberate deferral (RAIL-05, same as established sibling pattern). No truth FAILED outright; no artifact missing or stub; no key link unwired.

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| RAIL-01 | 199-02 | Deliverable maximum per rail, per shield revision, at the socket, method named | ✓ SATISFIED | Bench record + DECODE-NOTES § 10, independently re-derived |
| RAIL-02 | 199-01, 199-04, 199-05 | Ceiling classification, reproducible | ✓ SATISFIED | Regeneration diff + classification test, both independently re-run |
| RAIL-03 | 199-03, 199-05 | Shortfall warning naming both voltages, non-silent | ⚠ ADJUDICATED UNMET, accepted carried-forward | 199-05-SUMMARY.md "RAIL-03: why it stays Pending"; REQUIREMENTS.md correctly Pending |
| RAIL-04 | 199-03, 199-05 | VPE routing decision, made and recorded | ✓ SATISFIED | Firmware change + 15-case native suite, independently re-run and passing |
| RAIL-05 | 199-05 | gh#71 answered | ⚠ DEFERRED to milestone close | Draft approved and held; gh#71 confirmed unchanged live |

No orphaned requirements: `.planning/REQUIREMENTS.md`'s traceability table lists exactly RAIL-01 through RAIL-05 under Phase 199, and every one is declared by at least one of the five plans' `requirements:` frontmatter. REQUIREMENTS.md accurately reflects 3 Complete / 2 Pending — it was not prematurely flipped, and it was not left stale either.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter_fw/include/rurp_pinout.h` | `RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV` constant, zero pre-existing lines touched | ✓ VERIFIED | Present at line 120, value 17380; diff shows insertion-only |
| `firestarter_fw/src/proms/eprom.cpp` | `eprom_hv_route_mask` gains the ceiling comparison; `eprom_check_vpp` untouched | ✓ VERIFIED | Read directly; diffed against pre-phase commit |
| `firestarter_fw/include/eprom.h` | Declaration comment corrected | ✓ VERIFIED | Read directly |
| `firestarter_fw/test/native/avr/test_hv_route_ceiling/*.cpp` | 15-case native suite, registered in both native envs | ✓ VERIFIED, WIRED, and RUN | `platformio.ini` lists it in both `native`/`native_nodevtools` `test_filter`; live run: 15/15 pass |
| `firestarter_app/tools/DECODE-NOTES.md` § 10 | Full record per must_haves list | ✓ VERIFIED | Read in full; every claimed element present |
| `firestarter_app/tools/datasheet_overrides.json` | `FUJITSU/MBM27128` gains `electrical.vpp_mv` 18000→21000 | ✓ VERIFIED | Read directly, datasheet-cited |
| `firestarter_app/firestarter/data/chip_database.json` | Regenerated, exactly one field changed | ✓ VERIFIED | Independently re-diffed against pre-phase baseline |
| `firestarter_app/tests/test_vpp_rail_classification.py` | 9-case census test, exact equalities, 3-way non-vacuity | ✓ VERIFIED and RUN | Live run: 9/9 pass |
| `.planning/phases/199-what-the-rails-can-actually-deliver/199-GH71-ANSWER.md` | 5-section held draft | ✓ VERIFIED | Full structure present, comment body clean of internal identifiers |
| `firestarter/vpp_rail_gate.py` (the reverted module) | Must NOT exist | ✓ CONFIRMED ABSENT | `git ls-files` and `git status` (tracked + untracked) both show no match; only stale, gitignored `__pycache__` artifacts remain |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `eprom_hv_route_mask` | `eprom_check_vpp` | shared call, same routed mask feeds the acceptance window | ✓ WIRED | `eprom_check_vpp` calls `eprom_hv_route_mask(handle)` before reading; confirmed by direct read, unchanged by this phase |
| `chip_database.json`'s live census | `test_vpp_rail_classification.py` | live-database read, no hand-kept list | ✓ WIRED and FLOWING | Test's own `_census()` helper reads the installed package's data; independently re-derived the same 30-row/9+1/12+2+6 result from the raw JSON without going through the test |
| Bench record's `17380` | `rurp_pinout.h`'s constant | manually transcribed once, cross-checked | ✓ VERIFIED EQUAL | Three-way check (bench record, header, DECODE-NOTES) all read `17380` |
| `199-GH71-ANSWER.md` | gh#71 | not yet posted, by design | ✓ CORRECTLY NOT WIRED | `gh issue view 71` confirms no new comment; branch has no upstream in any of the three repos |

### Behavioral Spot-Checks / Test Runs

| Behavior | Command | Result | Status |
|---|---|---|---|
| New firmware routing suite | `pio test -e native -f "*test_hv_route_ceiling*"` | 15/15 PASSED | ✓ PASS |
| Firmware build budget | `pio run -e leonardo` | SUCCESS, 23816/32768 B | ✓ PASS |
| Firmware Python suite baseline | `pytest tests/` (firestarter_fw) | 17 failed / 284 passed | ✓ PASS (matches documented pre-existing baseline) |
| App classification census | `pytest tests/test_vpp_rail_classification.py` | 9/9 PASSED | ✓ PASS |
| App wire-dict equivalence | `pytest tests/test_wire_dict_equivalence.py` | 11/11 PASSED | ✓ PASS |
| Full app suite (Python 3.11, correctly provisioned) | `pytest tests/` (firestarter_app) | 2085 passed, 32 snapshots, 0 failed | ✓ PASS |
| gh#71 live state | `gh issue view 71 --repo henols/firestarter` | OPEN, 3 comments, last 2026-09-16 | ✓ PASS (matches claimed state exactly) |
| Nothing pushed | `git branch -r --contains HEAD` (all 3 repos) | empty in all three | ✓ PASS |
| Reverted host module absence | `git ls-files \| grep vpp_rail_gate` (firestarter_app) | no match | ✓ PASS |
| Independent database re-derivation | ad hoc Python script over live `chip_database.json` | 30 rows, 9+1/12+2+6 split, all `supported` | ✓ PASS |
| Independent regeneration diff | ad hoc Python script vs. `git show f155364:...` | 746→746, exactly one field changed | ✓ PASS |

### Anti-Patterns Found

None. Scanned every file this phase touched or created (`rurp_pinout.h`, `eprom.cpp`, `eprom.h`,
`test_hv_route_ceiling.cpp`, `host_stubs.cpp`, `DECODE-NOTES.md`, `test_vpp_rail_classification.py`,
`datasheet_overrides.json`) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` — zero matches. The
no-comments-in-source rule that governed most of this phase's design decisions was removed
mid-milestone (meta `41a34c6a`, 2026-09-19); the new test files correctly carry ordinary license
headers, consistent with the rule's removal, and this is not treated as a defect.

### Human Verification Required

None. Every claim in this phase is either a code-level fact (verified by direct read and live test
execution), a database fact (verified by independent re-derivation from the raw JSON), or an
externally-checkable fact (gh#71's live state, git branch/upstream state) — all confirmed live in
this verification rather than accepted from SUMMARY.md narrative.

### Gaps Summary

**No blocking gaps.** Three roadmap success criteria (RAIL-01, RAIL-02, RAIL-04) are fully and
independently verified, including live execution of the new native test suite (15/15), the new
Python census test (9/9), the full `firestarter_app` suite (2085/2085), and a firmware build
(within flash budget). Two items are not literally "true" today by the roadmap's exact wording:

- **RAIL-03** (SC3) is genuinely unmet. The routing fix eliminates the underlying shortfall for the
  ten drop-resistor rows, which is a better outcome in practice, but it is not the warning RAIL-03
  asks for, and the existing `MSG_WARN_VPP_LOW` cannot reliably see the shortfall its trigger window
  is narrower than. This was adjudicated by the phase's own last plan, disclosed honestly (Pending
  in REQUIREMENTS.md, named as a limit in the shipped documentation), and is accepted here as a
  carried-forward, correctly-disclosed limitation rather than a silently-missed requirement. This
  verifier independently confirmed the arithmetic behind the adjudication and concurs with it.
- **RAIL-05** (SC5) is not literally answered — nothing has been posted to gh#71. This follows the
  same held-pending-a-beta-cut pattern this project already used, and this verification already
  confirmed sound, for gh#70 (PULSE-04) and gh#66 (VOLT-04) in the two preceding phases. The draft is
  complete, approved, accurate, and does not overclaim; only the posting act — gated on artifacts
  that do not yet exist (a beta cut with real, asset-bearing releases) — remains.

Both items are transparently recorded in `.planning/REQUIREMENTS.md` as Pending (not misrepresented
as Complete anywhere), both are named explicitly in this phase's own SUMMARY and DECODE-NOTES
artifacts, and both follow an established, previously-verified pattern in this exact project rather
than being a novel or hidden shortfall. Given that, and given every other truth in this phase was
independently reproduced against the live codebase rather than accepted from a summary, this
verification reaches **passed**.

---

_Verified: 2026-09-19_
_Verifier: Claude (gsd-verifier)_
