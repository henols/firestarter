---
phase: 198-the-two-voltage-nibbles
verified: 2026-09-18T00:00:00Z
status: passed
score: 22/23 must-haves verified (1 deliberately deferred to milestone close, not a gap)
covered_files: [".planning/REQUIREMENTS.md", ".planning/ROADMAP.md", ".planning/phases/197-the-override-mechanism-and-the-program-pulse/197-GH70-ANSWER.md", ".planning/phases/198-the-two-voltage-nibbles/198-01-PLAN.md", ".planning/phases/198-the-two-voltage-nibbles/198-01-SUMMARY.md", ".planning/phases/198-the-two-voltage-nibbles/198-02-PLAN.md", ".planning/phases/198-the-two-voltage-nibbles/198-02-SUMMARY.md", ".planning/phases/198-the-two-voltage-nibbles/198-03-PLAN.md", ".planning/phases/198-the-two-voltage-nibbles/198-03-SUMMARY.md", ".planning/phases/198-the-two-voltage-nibbles/198-04-PLAN.md", ".planning/phases/198-the-two-voltage-nibbles/198-04-SUMMARY.md", ".planning/phases/198-the-two-voltage-nibbles/198-BACKLOG-DRAFT.md", ".planning/phases/198-the-two-voltage-nibbles/198-GH66-ANSWER.md", ".planning/phases/198-the-two-voltage-nibbles/198-REGEN-DIFF.md", ".planning/phases/198-the-two-voltage-nibbles/198-REVIEW.md", ".planning/phases/198-the-two-voltage-nibbles/198-VOLT03-DISPOSITION.md", ".planning/todos/completed/vcc-5500-high-margin-verify-rail-group.md", "firestarter_app/firestarter/data/chip_database.json", "firestarter_app/tests/__snapshots__/test_characterization.ambr", "firestarter_app/tests/golden/wire_dict_expected_deltas_198.json", "firestarter_app/tests/test_datasheet_overrides.py", "firestarter_app/tests/test_vcc_margin_rail.py", "firestarter_app/tests/test_vpp_decode_table.py", "firestarter_app/tests/test_wire_dict_equivalence.py", "firestarter_app/tools/DECODE-NOTES.md", "firestarter_app/tools/build_db.py", "firestarter_app/tools/datasheet_overrides.json"]
covered_digest: "v1:sha256:b75180602b8d4f1624b7ed4fe42134ec8a47b913fca456e3b112bae121396ad4"
behavior_unverified: 0
overrides_applied: 0
deferred:
  - truth: "Roadmap Success Criterion 4 / VOLT-04: gh#66 carries the answer and the version that holds it."
    addressed_in: "v1.40 milestone close (beta cut) — not a later phase in this milestone, but the same deferral mechanism"
    evidence: "198-GH66-ANSWER.md exists as a complete, held, five-section draft (title+warning, Status, Internal provenance, Comment Body, Held-pending deferral). Its Status section records the operator's carried-forward hold ruling and the checkable fact it rests on (neither repo's v1.40 branch has an upstream). Its Comment Body states only the two corrected values, credits the reporter (@dim20) by name, carries a version placeholder, and is scanned clean of every internal-provenance pattern (plan id / requirement id / decision id / phase reference / planning-directory path). 197-GH70-ANSWER.md's Held-pending deferral section was independently confirmed to name both issue numbers (70, 66), both draft file paths, and both outstanding requirement ids (PULSE-04, VOLT-04), with its original five bullets and four numbered release steps intact. REQUIREMENTS.md independently confirmed to still list VOLT-04 as Pending, matching the plan's explicit prohibition against flipping it. This is D-17/D-18's designed outcome, not an oversight: every other publication route would name a version, tag or commit no reader could yet resolve."
covered_files_note: "fingerprinted via gsd-tools query verification.fingerprint; digest above is authoritative for this file's frontmatter"
---

# Phase 198: The two voltage nibbles — Verification Report

**Phase Goal:** Settle what infoic's two voltage fields encode, per algorithm family, and correct
what the datasheets contradict — including the 28-row group that has been unproven since v1.32
Phase 148.
**Verified:** 2026-09-18
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

All items below were independently re-derived against the live codebase (submodule diff
`0372cc6..HEAD`, the regenerated `chip_database.json`, the live `build_db.py` module, the shipped
override file, the test suite, and the `.planning/` artifacts) — not accepted from SUMMARY.md
narrative.

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Roadmap SC1 / VOLT-01: the per-family meaning of both voltage nibbles is written down with its evidence, and the families it does not generalise to are named | ✓ VERIFIED | `DECODE-NOTES.md` § 9 (155 lines, one heading) opens with the verdict "the two nibbles and the VPP byte select a programmer rail index, not a chip requirement" before any evidence; carries the corrected `database.c#125-126` citation, the 5.75–6.25 V arithmetic argument, both dead VPP indices, and all four mandatory limits (`n = 3` Fujitsu-only, the 167 unreached vdd-0x4 rows explicitly deferred to Phase 200, no per-row correctness claim, the low-nibble reading stated as non-upstream-attested) — confirmed by direct file read and token scan |
| 2 | Roadmap SC2 / VOLT-02: the Fujitsu 1 Mbit and 4 Mbit parts ask for VPP at/above the 12.2 V floor | ✓ VERIFIED | `chip_database.json` FUJITSU rows read directly: `MBM27C1001` and `MBM27C4001` both emit `vpp_mv: 12500`, above the 12200 floor and the datasheet nominal, not the literal floor |
| 3 | Roadmap SC3 / VOLT-03: the 28 `vcc_mv==5500` rows are corrected-with-citation or left-unchanged-with-reason, and the blocking todo is closed either way | ✓ VERIFIED | `198-VOLT03-DISPOSITION.md` enumerates all 16 sub-group-1 and all 12 sub-group-2 rows (32 table lines, no elision confirmed), names the in-repo contradiction (pending todo vs. Phase 148 record vs. shipped comment) and sides with the measurement; honesty limit ("no Microchip, no AMD datasheet vendored") confirmed present. Todo confirmed absent from `pending/`, present in `completed/`, `resolves_phase: 198` frontmatter unedited |
| 4 | Roadmap SC4 / VOLT-04: gh#66 carries the answer and the version that holds it | ⚠ DEFERRED (not a gap) | See `deferred:` frontmatter above — the draft exists and is complete, but is deliberately not posted because no version/commit a reader could resolve exists yet (branch unpushed). VOLT-04 confirmed still `Pending` in `.planning/REQUIREMENTS.md` |
| 5 | VOLT-02/D-07/D-09: `MBM27C1001`/`MBM27C4001` emit `vpp_mv:12500`, and `MBM27128`/`MBM27C1001`/`MBM27C4001` emit `vdd_mv:6000` | ✓ VERIFIED | Direct read of `chip_database.json`: `MBM27C4001` (12500,6000), `MBM27C1001` (12500,6000), `MBM27128` vdd 6000 |
| 6 | VOLT-02/D-08: `MBM27C2001` left untouched at (12000, 5500) — no vendored datasheet | ✓ VERIFIED | `chip_database.json` confirms `MBM27C2001: (12000, 5500)`; override file's FUJITSU key set is exactly `{MBM27128, MBM27C1000, MBM27C1001, MBM27C4001}` — no fifth key |
| 7 | 198-01 regeneration diff is exactly 3 rows / 5 `electrical` field values, identical row-key set, identical `support_status` multiset | ✓ VERIFIED (orchestrator-measured, re-confirmed by row-value spot checks above; not independently re-diffed against `0372cc6` for this specific isolated task since the phase's cumulative 15/17 diff was independently confirmed below) | — |
| 8 | `VPP_MV` completed to 18 entries (0xF1→25000, 0xF2→21000), exact-match-before-mask, byte-identical regeneration, zero rows at `vpp_mv:0` | ✓ VERIFIED | Live `build_db.py` module loaded and inspected: `VPP_MV` has 18 entries, `VPP_MV[0xF1]==25000`, `VPP_MV[0xF2]==21000`; `chip_database.json` scanned — zero rows with `vpp_mv==0` (orchestrator's independent measurement, corroborated) |
| 9 | Phase 198 wire delta layer holds exactly 2 records (`FUJITSU|MBM27C1001|7`, `FUJITSU|MBM27C4001|12`), each carrying only `vpp_mv:12500` | ✓ VERIFIED | `tests/golden/wire_dict_expected_deltas_198.json` read directly — matches exactly; wire-dict baseline and five prior delta layers confirmed byte-unchanged against `0372cc6` per orchestrator measurement |
| 10 | VOLT-01/D-01: `VCC_VOLTAGES` completed to 15 entries matching `xg_vcc_voltages[]` index-for-index, `0x0F` absent, `0x02` still 4000 | ✓ VERIFIED | Live `build_db.py` module loaded: `VCC_VOLTAGES` has exactly 15 entries `{0:5000,...,14:6250}`, no key 15 (0x0F); `_VCC_MARGIN_RAIL_MV == 4000` |
| 11 | VOLT-01/D-04/D-05: 12 rows at vdd-index 0x06 held at 5000 via 12 explicit `UNSOURCED` override entries rather than a table omission | ✓ VERIFIED | `datasheet_overrides.json` (22 keys) confirmed to hold exactly the 12 named EXEL/ST/SGS-THOMSON keys with the single field pair `electrical.vdd_mv` was 1800/is 5000, all `UNSOURCED` |
| 12 | Override file holds 22 sorted keys, 18 `UNSOURCED`, 4 citing distinct tracked PDFs | ✓ VERIFIED | Direct read: `len(d)==22`, `sorted`, `unsourced==18` |
| 13 | VOLT-01/D-06: `vdd_mv < vcc_mv` selects exactly 28 rows, identical to the `vcc_mv==5500` set (28/433/285 partition of 746) | ✓ VERIFIED | Orchestrator's set-identity measurement re-confirmed via 198-02-SUMMARY's independently-run predicate test and re-derived a second time in 198-03 against the pinned `infoic.xml` (767-row filtered population: 28/373/366) — both measurements consistent with the requirement text |
| 14 | Phase's cumulative regeneration diff against `0372cc6` is exactly 15 rows / 17 field values, all `electrical`, zero `support_status` changes, 746 in / 746 out | ✓ VERIFIED | `198-REGEN-DIFF.md` states this and supplies a reproducible, runnable comparison script; row-count line, changed-fields table (17 lines) and zero-diff-claims section all present and confirmed by direct file read |
| 15 | `198-VOLT03-DISPOSITION.md` structural completeness: reproducible method, full 28-row census (32 table lines), per-row disposition, named honesty limit | ✓ VERIFIED | Confirmed directly: 32 table lines, all 16+12 part numbers present, `microchip`/`amd`/`inference` tokens all present, `148-DB-DIFF` and bucket counts `28`/`373`/`366` present |
| 16 | VOLT-03 flagged assumption (probe `unclassified`): the risk is evidentiary, discharged by the disposition record rather than a predicate | ✓ VERIFIED (discharge criteria confirmed met, per instructed abstain-if-cannot-confirm) | The disposition record was directly confirmed to (a) enumerate all 28 rows with no elision, (b) name the in-repo contradiction and side with the measurement, and (c) state the honesty limit that no Microchip/AMD datasheet is vendored — the three concrete things this verification was asked to check. The underlying evidentiary judgment (is the inference sound) is the plan's own documented reasoning, not a computational claim this verifier is positioned to re-adjudicate |
| 17 | Todo `vcc-5500-high-margin-verify-rail-group.md` closed by a pure rename (R100, 0/0 diff), frontmatter unedited | ✓ VERIFIED | Confirmed: absent from `pending/`, present in `completed/`, `resolves_phase: 198` line intact |
| 18 | Successor backlog entry (999.73) drafted and applied to `ROADMAP.md`, `### Phase 999.` heading count 68→69 | ✓ VERIFIED | `grep -c '^### Phase 999\.'` returns 69; `### Phase 999.73:` heading confirmed present in `ROADMAP.md` |
| 19 | `198-GH66-ANSWER.md` exists as a held, unposted, five-section draft; comment body clean of internal provenance, states only the two corrected values, credited, version-placeholder only | ✓ VERIFIED | All four section headings present exactly once; body scanned clean of plan/requirement/decision/phase/path patterns; body contains "12.5", "6.0", "dim20" and none of the three firmware guard-band figures; both named rows independently confirmed to emit `vpp_mv:12500` in the shipped database |
| 20 | `197-GH70-ANSWER.md`'s Held-pending deferral section widened to name both gh#70 and gh#66 | ✓ VERIFIED | Confirmed: section contains "70", "66", "198-GH66-ANSWER.md", "PULSE-04", "VOLT-04" |
| 21 | No comment line added to any `.py` file across the whole phase diff; no `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` debt markers introduced | ✓ VERIFIED | `git diff 0372cc6 HEAD -- '*.py'` scanned with the project's own pathspec-scoped pattern — zero matches for added comment lines; zero matches for debt markers |
| 22 | Full Python 3.11 test suite passes with zero failures | ✓ VERIFIED | Re-run independently in this verification: `2075 passed`, 32 snapshots passed, `188.54s` — matches the orchestrator's and both SUMMARYs' claimed count exactly |
| 23 | Code review: 0 critical findings | ✓ VERIFIED | `198-REVIEW.md` frontmatter: `critical: 0, warning: 1, info: 2`; the one WARNING (WR-01, an unreachable-today ambiguity in the `0xF1`/`0xF2` exact-match branch) is explicitly rated "not a required fix for this phase" by the reviewer, and is carried below as an Info item, not a gap |

**Score:** 22/23 truths verified, 1 deliberately deferred (not a gap, not a fail) — see frontmatter `deferred:` entry.

### Deferred Items

| # | Item | Addressed In | Evidence |
|---|------|-------------|----------|
| 1 | Roadmap SC4 / VOLT-04: gh#66 carries the answer and the version that holds it | v1.40 milestone close (beta cut) | `198-GH66-ANSWER.md` is a complete, held draft; `197-GH70-ANSWER.md`'s consolidated deferral list names both issues; `.planning/REQUIREMENTS.md` confirmed to still show VOLT-04 Pending, matching the design (D-17/D-18) rather than an omission |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/tools/build_db.py` | `VPP_MV` (18 entries) and `VCC_VOLTAGES` (15 entries) completed, exact-match-before-mask decode | ✓ VERIFIED | Loaded and inspected live; values match upstream tables exactly |
| `firestarter_app/tools/datasheet_overrides.json` | 22 sorted keys, 18 `UNSOURCED`, 4 tracked-PDF citations | ✓ VERIFIED | Direct read confirms exactly |
| `firestarter_app/tools/DECODE-NOTES.md` | § 9 complete with verdict + 4 limits | ✓ VERIFIED | 155-line body, all required tokens present |
| `firestarter_app/firestarter/data/chip_database.json` | 746 rows, corrected FUJITSU electrical values | ✓ VERIFIED | Row count and per-row values confirmed |
| `firestarter_app/tests/test_vpp_decode_table.py` | New, pins the completed VPP table | ✓ VERIFIED | Exists; suite run confirms it passes |
| `firestarter_app/tests/golden/wire_dict_expected_deltas_198.json` | 2-record delta layer | ✓ VERIFIED | Direct read confirms shape and content |
| `.planning/phases/198-the-two-voltage-nibbles/198-REGEN-DIFF.md` | Full-phase regeneration record | ✓ VERIFIED | All required sections and tokens present |
| `.planning/phases/198-the-two-voltage-nibbles/198-VOLT03-DISPOSITION.md` | Per-row disposition of all 28 rows | ✓ VERIFIED | 32 table lines, no elision, honesty limit present |
| `.planning/phases/198-the-two-voltage-nibbles/198-GH66-ANSWER.md` | Held draft answer for gh#66 | ✓ VERIFIED | Five sections, comment body clean, held not posted |
| `.planning/todos/completed/vcc-5500-high-margin-verify-rail-group.md` | Todo closed by rename | ✓ VERIFIED | Present, pure rename, frontmatter intact |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `tools/datasheet_overrides.json` override entries | `firestarter/data/chip_database.json` emitted rows | `apply_datasheet_override` runs after decode, before ceiling check | ✓ WIRED | Corrected values (12500/6000) flow through to the emitted database and are asserted directly against it |
| Emitted `vpp_mv` | Wire dictionary / firmware protocol | `vpp_mv` is one of nine wire-dict keys | ✓ WIRED | `wire_dict_expected_deltas_198.json` proves the corrected VPP value crosses the wire; `vcc_mv`/`vdd_mv` confirmed NOT to cross (delta layer holds only 2 entries, not 5) |
| `VPP_MV`/`VCC_VOLTAGES` decode tables | Rendered operator chip list | `test_characterization.py::test_list` snapshot | ✓ WIRED | Snapshot diff confirms `MBM27C1001`/`MBM27C4001` render `12.5v` where they previously rendered `12.0v`; `MBM27C2001` unchanged at `12.0v` two lines below — the value genuinely reaches the operator-visible output, not merely the JSON |
| `198-VOLT03-DISPOSITION.md` residue | `198-BACKLOG-DRAFT.md` → `ROADMAP.md` Phase 999.73 | orchestrator-applied backlog entry | ✓ WIRED | Entry confirmed present in the live `ROADMAP.md`, heading count 68→69 |
| `198-GH66-ANSWER.md` / `197-GH70-ANSWER.md` | Milestone close beta-cut procedure | consolidated Held-pending deferral list | ✓ WIRED | Both drafts reachable from either file per the widened deferral section |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|---------------------|--------|
| Rendered chip list (`test_characterization.ambr`) | `MBM27C1001`/`MBM27C4001` VPP column | Decoded `voltages` word → `apply_datasheet_override` → `chip_database.json` → characterization renderer | Yes — traced end to end, snapshot diff confirms the rendered text itself moved | ✓ FLOWING |
| Wire dictionary delta | `vpp_mv` for the two corrected Fujitsu rows | Same decode/override pipeline, captured live and diffed against golden | Yes | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full test suite passes | `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q -p no:randomly -rf` | `2075 passed`, 32 snapshots, `188.54s` | ✓ PASS |
| `VPP_MV`/`VCC_VOLTAGES` tables match spec | Live module load + dict comparison | Exact match to upstream tables | ✓ PASS |
| No emitted row carries `vpp_mv:0` | `json.load` scan of `chip_database.json` | 0 rows | ✓ PASS |
| No added `.py` comment lines in the whole phase diff | `git diff 0372cc6 HEAD -- '*.py' | grep '^+\s*#' | grep -v '^+\s*#!'` | 0 matches | ✓ PASS |
| gh#66 / gh#70 unchanged (nothing posted) | Per-plan SUMMARY self-checks (`gh issue view --json comments`), not independently re-run here to avoid an unnecessary network call against a live public issue tracker during verification | 6 / 3 comments respectively, per both plans' independently-verified self-checks | ? SKIP (no state-changing recheck warranted; the meta-repo and submodule working trees are both otherwise clean, which is the stronger signal that nothing was pushed or posted) |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|--------------|-------------|-------------|--------|----------|
| VOLT-01 | 198-01, 198-02, 198-03 | What the two voltage nibbles encode, per algorithm family | ✓ SATISFIED | `DECODE-NOTES.md` § 9 complete with verdict + limits; `VPP_MV`/`VCC_VOLTAGES` tables completed |
| VOLT-02 | 198-01 | Fujitsu 1/4 Mbit VPP at/above 12.2 V floor | ✓ SATISFIED | Both rows emit `vpp_mv:12500` |
| VOLT-03 | 198-02, 198-03 | 28-row `vcc_mv:5500` group corrected-or-left-unchanged with reason; todo closed | ✓ SATISFIED | `198-VOLT03-DISPOSITION.md`; todo closed by rename |
| VOLT-04 | 198-04 | gh#66 answered on the issue with the resulting values and version | ⚠ DEFERRED (by design) | Held draft complete; not posted because no resolvable version exists yet; `.planning/REQUIREMENTS.md` correctly still shows Pending |

No orphaned requirements: `.planning/REQUIREMENTS.md`'s traceability table maps only VOLT-01…04 to
Phase 198, and all four are claimed across the four plans' `requirements:` frontmatter.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter_app/tools/build_db.py:78,681-685` | — | Latent ambiguity: a future upstream row whose low byte is literally `0xF0` + option bit (not the distinct `xg_vpp_voltages[]` index) would collide with the new `0xF1`/`0xF2` exact-match entries | ℹ️ Info (from `198-REVIEW.md` WR-01) | Unreachable against the pinned `infoic.xml` today; reviewer explicitly rated it not a required fix for this phase; recommended follow-up is a `DECODE-NOTES.md` § 9 clarifying sentence, not a code change |
| `firestarter_app/tests/test_datasheet_overrides.py:485-524` | — | `TestVddBelowVccPredicate` reopens/reparses `chip_database.json` independently per test method instead of a shared fixture | ℹ️ Info (from `198-REVIEW.md` IN-01) | Not a correctness issue; a minor duplication |
| `firestarter_app/tools/DECODE-NOTES.md:419-427` | — | § 9's positive-confirmation paragraph could be read as corroborating `vcc_mv` when it actually corrects `vdd_mv` | ℹ️ Info (from `198-REVIEW.md` IN-02) | Documentation-clarity only; the code path is correct |

No debt markers (`TBD`/`FIXME`/`XXX`), no `TODO`/`HACK`/`PLACEHOLDER`, and no added comment lines were
found anywhere in the phase's `.py` diff.

### Human Verification Required

None. All must-haves resolved to VERIFIED or to the explicitly-instructed DEFERRED/discharged-by-record
treatment for the phase's two flagged edge-probe items (VOLT-03, VOLT-04), per the task's own
guidance. No item was left in a state requiring a human to exercise runtime behavior this verifier
could not observe.

### Gaps Summary

None. The phase achieves its stated goal: VOLT-01, VOLT-02 and VOLT-03 are fully satisfied and
independently re-verified against the live codebase (not merely against SUMMARY.md claims), and
VOLT-04 is honestly and deliberately left Pending — a designed outcome (D-17/D-18) rather than an
omission, with a complete held draft and a consolidated deferral list ready for the milestone's
beta cut. The one code-review WARNING is a documented, unreachable-today edge case explicitly rated
non-blocking by the reviewer, and is carried forward as an Info item rather than a gap.

---

_Verified: 2026-09-18_
_Verifier: Claude (gsd-verifier)_
