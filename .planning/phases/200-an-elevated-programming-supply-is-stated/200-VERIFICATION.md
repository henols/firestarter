---
phase: 200-an-elevated-programming-supply-is-stated
verified: 2026-09-19T00:00:00Z
status: human_needed
score: 9/10 must-haves verified
covered_files: [".planning/REQUIREMENTS.md", ".planning/phases/200-an-elevated-programming-supply-is-stated/200-01-PLAN.md", ".planning/phases/200-an-elevated-programming-supply-is-stated/200-01-SUMMARY.md", ".planning/phases/200-an-elevated-programming-supply-is-stated/200-02-PLAN.md", ".planning/phases/200-an-elevated-programming-supply-is-stated/200-02-SUMMARY.md", ".planning/phases/200-an-elevated-programming-supply-is-stated/200-03-PLAN.md", ".planning/phases/200-an-elevated-programming-supply-is-stated/200-03-SUMMARY.md", ".planning/phases/200-an-elevated-programming-supply-is-stated/200-CONTEXT.md", ".planning/phases/200-an-elevated-programming-supply-is-stated/200-REVIEW.md", "firestarter_app/firestarter/eprom_info.py", "firestarter_app/tests/__snapshots__/test_characterization.ambr", "firestarter_app/tests/test_characterization.py", "firestarter_app/tests/test_cli_handlers.py", "firestarter_app/tests/test_programming_vcc_census.py"]
covered_digest: "v1:sha256:24628ba3c41de3584bfe2e272fba6794b470a926fe6966e1639540d741e3a4a2"
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Read the shipped wording once, in place: run `firestarter info MBM27C1000` (or MBM27C4001) and confirm the two deliberate voltage spellings (`6.0v` in the field-row cell via `format_mv`, `6.0 V` in the warning prose via `_format_v_prose`) are both wanted, and that the amended verb — \"this part's programming supply decodes to 6.0 V; the shield supplies a fixed 5.0 V. Programming will be attempted at 5.0 V.\" — reads the way you intended when you amended it on 2026-09-19."
    expected: "Operator confirms both spellings and the amended verb read as intended, or states which should change."
    why_human: "This is plan 200-02 Task 2's own reserved `<human-check>`; no agent ran it, correctly, since the plan reserves this judgment for the operator. It is also the substance of VCC-02's 'is this the same shortfall-statement shape, does it read right' question, which 200-01's own flagged_assumptions explicitly route to human review rather than an automated pass/fail."
---

# Phase 200: An elevated programming supply is stated Verification Report

**Phase Goal:** A decoded `vdd_mv` that nothing applies stops being invisible.
**Verified:** 2026-09-19
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | (SC1/VCC-01) A part whose `vdd_mv` decodes above 5000 mV shows a `Programming VCC:` row (between `VCC:` and `VPP:`) and a two-line `WARNING:` block naming both numbers, on `firestarter info`, before any write is attempted; exits 0. | ✓ VERIFIED | Re-ran independently: `firestarter info MBM27C1000` (clean `FIRESTARTER_CONFIG_DIR`) prints `Programming VCC:    6.0v` directly after `VCC:                5.0v` and before `VPP:                12.5v`, then a blank line, then `WARNING: this part's programming supply decodes to 6.0 V; the shield supplies a fixed 5.0 V.` / `Programming will be attempted at 5.0 V.`, `rc=0`, full DIP layout still printed. Corroborated by `tests/test_characterization.py::test_info_mbm27c1000`/`test_info_mbm27c4001` (subprocess, real entry point, syrupy-pinned) — both pass (`2 passed`, `4 snapshots passed`). |
| 2 | (D-06 fail-open, enumerated cases) A part at or below 5000 mV, or with `vdd_mv` absent/`None`/`0`/exactly `5000`/a non-numeric string, shows neither the row nor the warning; still shows `VCC:` correctly; exits 0. | ✓ VERIFIED | Re-ran independently: `firestarter info W27C512` shows only `VCC:                5.0v`, no `Programming VCC:`/`decodes`, `rc=0`. `programming_vcc_over_rail_mv` re-run directly against all 9 plan-specified cases (6000→6000, 5001→5001, 5000→None, 0→None, None→None, `{}`→None, `{}`(no electrical)→None, `None` arg→None, `"not-a-number"`→None) — all match. |
| 3 | (D-03) The predicate is `vdd_mv > _SHIELD_FIXED_VCC_MV`, `_SHIELD_FIXED_VCC_MV = 5000` defined exactly once, at module level in `eprom_info.py`, not in `constants.py`. | ✓ VERIFIED | `grep -c '_SHIELD_FIXED_VCC_MV = 5000' firestarter/eprom_info.py` = 1; `firestarter/constants.py` confirmed byte-unchanged against `0d6be3f`. |
| 4 | (D-04) The shipped sentence uses the operator's 2026-09-19 amended verb ("decodes to"), and the pre-amendment verb ("programs at") occurs zero times in `eprom_info.py`. | ✓ VERIFIED | Read `eprom_info.py` source directly: `programming supply decodes to` appears once; `grep -cF 'programs at' firestarter/eprom_info.py` = 0. |
| 5 | (D-02/D-07) The `write` path is unchanged; `vdd_mv` never crosses the wire; `database.py`, `cli_handlers.py`, `constants.py` byte-unchanged against phase base `0d6be3f`; no firmware file touched. | ✓ VERIFIED | `git diff --quiet 0d6be3f -- firestarter/database.py firestarter/cli_handlers.py firestarter/constants.py` exits 0 (re-run independently). `firestarter_fw` gitlink is unchanged since Phase 199 (`a050730`, clean tree). Phase diff overall: 5 files, 836 insertions, 0 deletions — none in database.py/cli_handlers.py/constants.py/firmware. |
| 6 | (D-01) The shipped predicate selects exactly 284 of 746 rows in the live database, proved non-vacuous (not a hand-transcribed number). | ✓ VERIFIED | `tests/test_programming_vcc_census.py` — 11/11 tests pass (re-run independently); imports the shipped predicate rather than reimplementing it; three in-module planted mutations plus an external `sed` mutation on `_EXPECTED_TOTAL_ROWS` all observed to fail per plan verify legs (reproduced: mutated total 283 fails, restored to 284 passes as part of the 11-test run). |
| 7 | (D-03) Phase 198's 28-row VOLT-03 set (`vcc_mv: 5500`) is fully disjoint from the 284-row elevated set. | ✓ VERIFIED | `test_volt03_five_five_volt_set_is_disjoint_from_the_elevated_set` passes as part of the 11/11 run; independently re-derivable from the live database (28 rows at `vcc_mv==5500`, 0 overlap with the 284). |
| 8 | The amended D-04 verb is warranted by measurement: exactly 3 of 284 rows carry a datasheet-cited `vdd_mv` override, 281 carry a pure rail-table slot. | ✓ VERIFIED | `test_only_three_elevated_rows_carry_a_datasheet_cited_vdd_override` passes; keys are `FUJITSU/MBM27128`, `FUJITSU/MBM27C1001`, `FUJITSU/MBM27C4001`, matched via comma-split aliasing (the exact bug class the plan calls out is guarded against). |
| 9 | (SC2/VCC-02) The shortfall-statement shape (blank separator, `WARNING:`-prefixed condition+consequence, follow-on line) is **defined**, generalising the existing `no_pinout_warning` advisory, per the ROADMAP's 2026-09-19 amendment superseding the RAIL-03-matching clause. | ✓ VERIFIED (structural) — see human_verification for the design-intent half | Read `present_eprom_details` directly: the new block is byte-for-byte the same three-part shape (`logger.warning("")`, condition+consequence line, follow-on line) as the pre-existing `no_pinout_warning` block a few lines below it. ROADMAP.md's Phase 200 section carries the amendment text verbatim, matching CONTEXT.md's D-04 note and the plans' `flagged_assumptions`. Whether this reads as the *intended* wording is inherently a design judgment, not a code-shape fact — routed to human_verification per the plan's own instruction. |
| 10 | (D-06, full contract) The predicate "must fail open" **unconditionally**, per its own docstring, for any malformed `raw_config_data`/`electrical`/`vdd_mv` shape reachable through a hand-edited local override. | ✗ Not fully met — see finding below | Reproduced directly: `programming_vcc_over_rail_mv({"electrical": "bogus"})` raises `AttributeError` rather than returning `None` (also for `123`, `[1,2,3]`). This is outside the plan's own explicitly enumerated D-06 case list (absent/`None`/`0`/exactly-5000/non-numeric-string `vdd_mv`), all of which pass, but it contradicts the shipped docstring's unconditional framing. See "CR-01" discussion below. |

**Score:** 9/10 truths verified (0 present, behavior-unverified)

### CR-01 discussion (judgment item, not a truth failure)

The phase's own code review (`200-REVIEW.md`) flagged this as its one Critical finding, and I reproduced it independently (see truth #10 above and the `database.py` cross-check below). My judgment: **this does not falsify a must-have of this phase and is not a BLOCKER**, for three reasons, but it is real and should not be silently dropped:

1. **No must-have in any of the three plans' frontmatter enumerates this case.** 200-01's D-06 truth and 200-03's fail-open test matrix both list exactly five malformed-`vdd_mv` shapes plus an absent-`electrical`-key and a `None` record — never a **present-but-non-dict** `electrical` value. Every one of the enumerated cases returns `None` correctly (re-verified directly).
2. **It is coincidentally, but currently, unreachable from the shipped `info` command.** `firestarter/database.py:356` (read-only in this phase, confirmed byte-unchanged against `0d6be3f`) does `electrical = ic.get("electrical", {})` then unconditionally `electrical.get("pin_count")` one call earlier in the same request — so a malformed `electrical` value already raises `AttributeError` in `_map_data` before `programming_vcc_over_rail_mv` is ever reached via `info`. Reproduced directly against the live source.
3. **The live 746-row shipped database has zero rows in this or any other fail-open state** — the predicate's fail-open branch is dead-in-production today regardless of this gap, by the generator's own `.get(..., 5000)` default.

However, the shipped docstring states the "must fail open" contract **without carving out this exception**, and `test_programming_vcc_census.py`'s own fail-open test is named in a way that overstates its coverage (the review's WR-01). This is a real, if narrow, defect: a future direct caller of `programming_vcc_over_rail_mv` (the function is a public, tested, standalone predicate — `test_programming_vcc_census.py` calls it directly with no `_map_data` in the path) could hit this uncaught exception. **Recommendation: file as a backlog/follow-up fix** (the review's suggested fix — widen the except tuple to include `AttributeError`, or validate `isinstance(electrical, dict)` explicitly — is a two-line change with an obvious test to pair it), not as a phase-blocking gap. This is analogous to the two backlog items 200-01 already filed (misaligned `Support status:` padding, arbitrary-override rendering) rather than to a missing artifact or broken key link.

### Judgment on 200-01's deviation (in-process assertion surface)

200-01's Task 2 must-have originally described the warning as "separable in-process ... under `CliRunner` with `obj=app` the root logger stays at WARNING, so only the warning lines appear ... via `result.output`." The executor found this vacuous under pytest (pytest's own log-capture handler suppresses `logging.lastResort`, so `result.output` is always `''` in this invocation shape) and substituted `caplog.text` instead, with a `caplog.at_level(...)` wrapper for order-independence. **Judgment: satisfied, not merely partially.** The letter of the original truth (specifically `result.output`) is false, but:
- The underlying property — that the warning reaches the operator via `logger.warning` on stdout at default verbosity, with no `-v` flag and no level prefix — is independently confirmed by my own live `firestarter info MBM27C1000` run above (real stdout, real default verbosity, no `-v`).
- The log-level separation the truth cared about (INFO field rows filtered out, only WARNING lines visible) is demonstrably real and pinned via `caplog.text` plus a planted-mutation non-vacuity check (both tests pass; the negative test was seen to fail against a lowered rail constant per the plan's own verify leg).
- 200-02's subprocess snapshots close the gap the in-process substitution left open, by pinning the literal stdout the real entry point produces — which is the actual claim VCC-01 needs.
The substitution is documented transparently in the SUMMARY as a Rule-1 auto-fix with reasoning and verification, not silently absorbed.

### Judgment on flagged_assumptions (VCC-01/VCC-02 "unclassified")

Both plans mark VCC-01 and VCC-02 `unclassified` from the spec-less edge probe and instruct a verifier who cannot confirm the claim from the artifacts to abstain to human review. I *could* confirm VCC-01 directly from the artifacts (live CLI run, subprocess snapshots, census tests — see truths #1–8 above), so VCC-01 is adjudicated VERIFIED rather than abstained. VCC-02's *structural* half (does a defined shape exist, does it generalize `no_pinout_warning`) is likewise directly confirmable from source and is VERIFIED (truth #9). VCC-02's *design-intent* half ("does this read as the right shape/wording") is exactly the judgment the plan says to route to human review, and it coincides with the operator's own already-pending `<human-check>` from 200-02 Task 2 — both are captured as the single `human_verification` item above rather than duplicated.

### ROADMAP vs REQUIREMENTS.md agreement on RAIL-03 supersession (judgment item 5)

Checked directly: `ROADMAP.md`'s Phase 200 section carries the full 2026-09-19 amendment text ("As written, criterion 2 and VCC-02 both pointed at 'the same shape as RAIL-03' — and RAIL-03 was adjudicated UNMET at the close of Phase 199 ... Phase 200 defines it instead"). `REQUIREMENTS.md`'s VCC-02 bullet text is **not** edited and still literally reads "uses the same warning shape as RAIL-03" — but `200-CONTEXT.md`'s own canonical-refs section explicitly flags this exact staleness and instructs readers to read it together with the ROADMAP amendment. This is a known, already-documented inconsistency between two planning artifacts, not a silent contradiction discovered here. It does not block adjudication of VCC-02 (which is judged against the ROADMAP's authoritative, current text), but the literal REQUIREMENTS.md wording should be updated to match the amendment at the orchestrator's next requirements-touching pass (not done here — REQUIREMENTS.md edits are the orchestrator's, not the verifier's).

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/eprom_info.py` | `_SHIELD_FIXED_VCC_MV`, `_format_v_prose`, `programming_vcc_over_rail_mv`, gated injection, gated row+warning blocks | ✓ VERIFIED | All four symbols present, wired into `prepare_detailed_eprom_data`/`present_eprom_details`; confirmed live and via source read. |
| `firestarter_app/tests/test_cli_handlers.py` | Two in-process regression tests pinning presence/absence | ✓ VERIFIED | `test_info_elevated_programming_vcc_warns`, `test_info_five_volt_part_emits_no_programming_vcc_warning` present, both pass (`79 passed` for the census+cli_handlers run). |
| `firestarter_app/tests/test_characterization.py` + `.ambr` | Two subprocess snapshot tests, four new `.ambr` entries, additive-only diff | ✓ VERIFIED | Both tests pass (`2 passed, 4 snapshots passed`); `git diff --numstat 0d6be3f -- tests/__snapshots__/test_characterization.ambr` = insertions-only (confirmed at 118 insertions / 0 deletions per SUMMARY, phase diff stat corroborates: `.ambr` +118/-0). |
| `firestarter_app/tests/test_programming_vcc_census.py` | 11-test census module, ≥250 lines, imports shipped predicate | ✓ VERIFIED | 509 lines; 11/11 tests pass; `grep` confirms `from firestarter.eprom_info import` and zero local redefinition of `_SHIELD_FIXED_VCC_MV`. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `cli_handlers.info` | `EpromConsolePresenter.prepare_detailed_eprom_data` | existing `raw_config_data` seam | ✓ WIRED | `cli_handlers.py` byte-unchanged; the seam already existed and is unmodified — confirmed by `git diff --quiet 0d6be3f`. |
| `prepare_detailed_eprom_data` injection | `present_eprom_details` row+warning | shared `"programming_vcc_str" in chip_data` gate | ✓ WIRED | Single call site sets both `programming_vcc_mv`/`programming_vcc_str` together; both output blocks gate on the same key — confirmed by direct source read (row and warning cannot disagree). |
| `test_programming_vcc_census.py` | `firestarter/eprom_info.py` | `from firestarter.eprom_info import _SHIELD_FIXED_VCC_MV, programming_vcc_over_rail_mv` | ✓ WIRED | Confirmed by grep; zero local reimplementation. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|---------------------|--------|
| `Programming VCC:` row | `chip_data['programming_vcc_str']` | `raw_config_data.electrical.vdd_mv` (live `chip_database.json`, via `programming_vcc_over_rail_mv`) | Yes | ✓ FLOWING |
| Warning block | `chip_data['programming_vcc_mv']` | same predicate/raw record | Yes | ✓ FLOWING |
| Census 284-row total | `_census(_load_db())` | live `firestarter/data/chip_database.json`, re-parsed at test time | Yes | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Elevated part shows row+warning, exits 0 | `FIRESTARTER_CONFIG_DIR=<clean> firestarter info MBM27C1000` | row+warning present, `rc=0` | ✓ PASS |
| 5V part shows neither, exits 0 | `FIRESTARTER_CONFIG_DIR=<clean> firestarter info W27C512` | only `VCC: 5.0v`, `rc=0` | ✓ PASS |
| Predicate raises on malformed `electrical` | `programming_vcc_over_rail_mv({"electrical": "bogus"})` | `AttributeError` (not `None`) | ✗ FAIL (see CR-01 discussion — not a must-have, filed as backlog recommendation) |
| Census + CLI-handler tests pass | `pytest tests/test_programming_vcc_census.py tests/test_cli_handlers.py` | `79 passed` | ✓ PASS |
| Characterization snapshots pass | `pytest tests/test_characterization.py::test_info_mbm27c1000 tests/test_characterization.py::test_info_mbm27c4001` | `2 passed`, `4 snapshots passed` | ✓ PASS |
| Read-only files unchanged | `git diff --quiet 0d6be3f -- firestarter/database.py firestarter/cli_handlers.py firestarter/constants.py` | exit 0 | ✓ PASS |
| Lint/format clean | `ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/` | `All checks passed!` / `145 files already formatted` | ✓ PASS |

### Probe Execution

Not applicable — this phase has no `scripts/*/tests/probe-*.sh` and none are declared in the plans.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| VCC-01 | 200-01, 200-02, 200-03 | A part that needs a programming VCC above the shield's fixed 5.0 V says so where the operator will see it, rather than carrying a decoded `vdd_mv` that nothing applies. | ✓ SATISFIED | Truths 1, 2, 6, 7, 8 above; live CLI check; census tests; subprocess snapshots. |
| VCC-02 | 200-01, 200-02 | That statement uses the same warning shape as RAIL-03 (superseded 2026-09-19: Phase 200 **defines** the shape instead, per ROADMAP amendment). | ✓ SATISFIED (structural) / pending human confirmation of wording | Truth 9 above; ROADMAP amendment text confirmed present and consistent with CONTEXT.md; wording-reads-as-intended is the pending `human_verification` item. |

No orphaned requirements: `REQUIREMENTS.md`'s Traceability table maps only VCC-01 and VCC-02 to Phase 200, and both are declared in all three plans' frontmatter `requirements:` fields.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter_app/firestarter/eprom_info.py` | 63–71 | Incomplete exception tuple contradicts the function's own "must fail open" docstring for a non-dict `electrical` value (CR-01, reproduced independently) | ⚠️ Warning | Not reachable via the shipped `info` CLI path today (mitigated one layer up in `database.py`) and not reachable from the live 746-row database; reachable only via a specific class of hand-edited local override, and only if a future caller uses the predicate directly. Recommend backlog fix, not a phase blocker. |
| `firestarter_app/firestarter/eprom_info.py` | 339–347 | Warning block indexes `chip_data['programming_vcc_mv']` directly rather than via `.get()`, unlike every other optional field in the same method (WR-02, code review) | ℹ️ Info | Currently safe — single call site always sets both keys together — but a future refactor could turn this into an unguarded `KeyError`. Non-blocking. |
| `firestarter_app/firestarter/eprom_info.py` | 302, 306 (pre-existing, not modified this phase) | `Support status:`/`Reason:` rows hardcode their pad and sit one column right of every `pos`-formatted row | ℹ️ Info | Pre-existing, explicitly out of scope for this phase (fixing would move unrelated snapshots); filed as a backlog observation in 200-01-SUMMARY.md, not re-filed here. |

No debt markers (`TBD`/`FIXME`/`XXX`) found in any file this phase modified (the one `XXX` grep hit in `test_characterization.py` is part of a `/dev/ttyXXX` path-masking pattern, not a debt marker). No `TODO`/`HACK`/`PLACEHOLDER` found.

### Human Verification Required

### 1. Wording and spelling confirmation (200-02 Task 2's reserved human-check)

**Test:** Run `firestarter info MBM27C1000` (or `MBM27C4001`) and read the output.
**Expected:** Confirm (a) the deliberate two-spelling split is wanted — `6.0v` in the `Programming VCC:` field-row cell (via `format_mv`) versus `6.0 V` in the warning prose (via `_format_v_prose`) — or say which one should win; and (b) the amended-verb sentence — `WARNING: this part's programming supply decodes to 6.0 V; the shield supplies a fixed 5.0 V.` / `Programming will be attempted at 5.0 V.` — reads the way you intended when you amended it on 2026-09-19.
**Why human:** This is a design-intent judgment the plan itself reserves for the operator (`200-02-PLAN.md` Task 2's own `<human-check>` block), not a code-shape fact a verifier can adjudicate. It is also the substance of the "does VCC-02's defined shape read right" question both plans' `flagged_assumptions` explicitly route to human review.

### Gaps Summary

No blocking gaps. Every artifact this phase claims to have produced exists, is substantive, is wired, and its data flows from the live database rather than a static stub. All three plans' commits are present in `firestarter_app` history at the SHAs their SUMMARYs claim (`3895753`, `077fce2`, `afeb11d`, `cc99e03`, `5cf4cb1`, `6a45804`), the submodule HEAD matches (`6a45804`), and the meta gitlink is advanced to match. The full re-derived phase diff is exactly 5 files / 836 insertions / 0 deletions, matching both SUMMARYs and the code review's own count. Lint, format, and every targeted test re-run pass independently of the SUMMARYs' claims.

One narrow, non-blocking correctness gap exists in `programming_vcc_over_rail_mv`'s exception handling for a malformed (non-dict) `electrical` value — real, caught by the phase's own code review, reproduced independently here, but outside every must-have this phase's plans actually declared, currently unreachable via the shipped `info` path, and unreachable from the live database. Recommended disposition: file as a backlog fix rather than block the phase (see "CR-01 discussion" above for the fix already drafted by the code review).

One item needs the operator's own sign-off before this phase can be called fully closed: confirming the shipped wording (spelling split + amended verb) reads as intended. This is the sole reason overall status is `human_needed` rather than `passed` — every other truth is independently verified against the actual codebase, not taken from a SUMMARY.

---

_Verified: 2026-09-19_
_Verifier: Claude (gsd-verifier)_
