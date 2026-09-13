---
phase: 188-the-tools-directory
verified: 2026-09-13T12:00:00Z
status: passed
score: 7/7 must-haves verified
covered_files: [".planning/REQUIREMENTS.md", ".planning/ROADMAP.md", ".planning/notes/host-tools-retirement.md", ".planning/phases/188-the-tools-directory/188-01-PLAN.md", ".planning/phases/188-the-tools-directory/188-01-SUMMARY.md", ".planning/phases/188-the-tools-directory/188-02-PLAN.md", ".planning/phases/188-the-tools-directory/188-02-SUMMARY.md", ".planning/phases/188-the-tools-directory/188-03-PLAN.md", ".planning/phases/188-the-tools-directory/188-03-SUMMARY.md", ".planning/phases/188-the-tools-directory/188-04-PLAN.md", ".planning/phases/188-the-tools-directory/188-04-SUMMARY.md", ".planning/phases/188-the-tools-directory/188-05-PLAN.md", ".planning/phases/188-the-tools-directory/188-05-SUMMARY.md", ".planning/phases/188-the-tools-directory/188-06-PLAN.md", ".planning/phases/188-the-tools-directory/188-06-SUMMARY.md", ".planning/phases/188-the-tools-directory/188-07-PLAN.md", ".planning/phases/188-the-tools-directory/188-07-SUMMARY.md", ".planning/phases/188-the-tools-directory/188-08-PLAN.md", ".planning/phases/188-the-tools-directory/188-08-SUMMARY.md", ".planning/phases/188-the-tools-directory/188-09-PLAN.md", ".planning/phases/188-the-tools-directory/188-09-SUMMARY.md", ".planning/phases/188-the-tools-directory/188-CONTEXT.md", ".planning/phases/188-the-tools-directory/188-REVIEW.md", ".planning/seeds/phase-gate-expiry-discipline.md", ".planning/todos/completed/2026-09-12-retire-two-orphaned-host-tools.md", ".planning/todos/pending/2026-08-27-strip-gsd-provenance-comments-from-source.md"]
covered_digest: "v1:sha256:12a63c6187a6399d74ca31b576d2cff79692a305a892c3e4517605f51f307f1b"
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Decide whether the six code-review warnings (WR-01..WR-06, all confirmed still present in the tree) must be closed before this phase is called done, or filed as explicit follow-on work."
    expected: "Either a quick task lands fixing all six stale claims (and WR-06 is added to host-tools-retirement.md, which 188-04's own SUMMARY promised but 188-09 did not deliver), or the operator explicitly accepts them as disclosed follow-on debt (e.g. a todo filed naming all six by ID)."
    why_human: "These are judgment calls about phase-completion bar, not something a truth/artifact check can resolve — none break a test or a roadmap success criterion, but the milestone is named 'Claim Hygiene' and one of the six (WR-01) is a false enforcement claim inside a file this very phase's TOOLS-05 sweep touched, and another (WR-06) is a disclosed gap the phase's own plans promised to record permanently and did not."
---

# Phase 188: The Tools Directory Verification Report

**Phase Goal:** Every script in `firestarter_app/tools/` can answer what it is for and who runs it, and no
tool that serves GSD rather than the product is left sitting in the published package repo claiming
otherwise.
**Verified:** 2026-09-13
**Status:** passed (human item resolved at UAT 2026-09-13)
**Re-verification:** No — initial verification

## Goal Achievement

This phase is a subtraction: six of seven requirements resolve to RETIRED (a decision, not a build), and
the phase's own record (`188-CONTEXT.md`, `host-tools-retirement.md`) is explicit that "retire it" counts
as answering the roadmap's question. I verified the retirement actually happened in the codebase (not
just claimed in a SUMMARY), that the one requirement that produced work (TOOLS-05) is real, and that the
requirement/roadmap ledger accurately distinguishes "we decided not to build this" from "we built this."

### Observable Truths

Derived from the seven ROADMAP success criteria plus the "Explicitly NOT in scope" paragraph (Option
A/roadmap-truths — the phase supplies no `must_haves:` frontmatter block in its plans beyond per-plan
scope).

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | TOOLS-01: the repo-escaping default-path defect no longer exists, because the tool exhibiting it is gone (D-06) | ✓ VERIFIED | `firestarter_app/tools/audit_coverage_matrix.py` and `tests/test_audit_coverage_matrix*.py` absent (`git ls-files` — 0). REQUIREMENTS.md row correctly says "dissolved by tool deletion," never claims the pre-existing quick-260912-mo6 guard as this phase's fix. |
| 2 | TOOLS-02: the declaration layer was dropped by operator decision, not silently skipped, and the conflict with the phase's own "no deletion may precede it" text is disclosed | ✓ VERIFIED | ROADMAP criterion 2 amendment quotes the conflict; `host-tools-retirement.md` §2 cost 2 states the audit's blind spot is unaddressed. (Minor: the amendment says "this criterion's own text says…" when the quoted phrase is actually from the adjacent "Explicitly NOT in scope" paragraph, not criterion 2's body — substance is accurate, attribution is imprecise; not blocking.) |
| 3 | TOOLS-03: all ten `check_*.py` gates decided by name and retired; the four orphaned symbols' disposition (relocate vs. delete-consumers) resolved by a recorded operator decision, not silently defaulted | ✓ VERIFIED | `git ls-files -- 'tools/check_*.py' 'tests/test_check_*.py'` → 0 in `firestarter_app`. No relocation-helper module (`tests/dispatch_model.py` etc.) exists anywhere (`git ls-files` → 0, all four names). OD-1→D-25 supersession recorded in `188-02-SUMMARY.md` and `host-tools-retirement.md` §3, with the operator's verbatim answer and the replan's re-measurement (247 vs ~105 tests) both present. |
| 4 | TOOLS-04: each of the six GSD-process tools is placed by name (kept/moved/retired), none left undecided | ✓ VERIFIED | All six (`audit_coverage_matrix.py`, `diff_db.py`, `measure_plan_shapes.py`, `measure_part_number_delta.py`, `snapshot_report_shapes.py`, `build_devtest_issue_corpus.py`) absent from `firestarter_app/tools/`; `diff_db.py` present, tracked and executable at `.claude/skills/devtest-rootcause/scripts/diff_db.py`, and the skill's `SKILL.md`/`seed_debug_session.py` reference the relocated path with zero references to the retired `check_dispatch.py` gate (`grep -c check_dispatch` → 0). |
| 5 | TOOLS-05: no file under `firestarter_app/tools/` cites a phase number, plan number, decision ID, or `.planning/` path | ⚠️ Amended scope, disclosed — see note below | The five in-repo survivor scripts plus `catalog/codegen.py` (all six D-16 survivors) are citation-free (spot-checked directly: no `Phase N`/`D-NN`/`.planning/` hits in `build_db.py`, `gen_test_image.py`, `parse_devtest_issue.py`, `gen_sdp_bus_config.py`, `gen_validation_header.py`, `catalog/codegen.py`). But `tools/DECODE-NOTES.md` and `tools/catalog/messages.toml` still carry dozens of `Phase N`/`D-NN`/`.planning/` citations, and both `tools/baseline/*.json` files carry provenance fields naming a deleted tool — all measured directly, confirming the task brief's finding. This is **not an oversight**: D-14 explicitly scopes this phase to scripts, not data, and D-16 explicitly scopes the sweep to the six survivor scripts; ROADMAP's amendment for criterion 5 states the narrower scope in place of the original wording. The literal criterion text ("No file...") is broader than what was delivered, and the amendment's "satisfied as written" phrasing slightly overstates that (it is satisfied only under the narrowed scope it then states) — a wording nit, not a hidden gap, since the scope narrowing itself is named. |
| 6 | TOOLS-06: `frame-vectors.toml`/`codegen_vectors.py` byte-identity is enforced (or the apparatus is retired instead, with no new CI gate) | ✓ VERIFIED | Repo-wide `git grep` for `codegen_vectors`/`frame_vectors`/`frame-vectors` in `firestarter_app` → 0 hits. In `firestarter`, all 4 hits are historical narration (a baseline JSON's own transcription-source note, a frozen `RED-BASELINE.md`, a frozen pre-existing build-warning fixture, and a test docstring explaining a prior figure move) — none a functional reference. Native baseline re-recorded 185/17→179/179/16 for both pinned envs from one cold capture, matching orchestrator-measured 179/179/16 both envs; AVR `uno` flash_used proven unmoved by a cold rebuild. `catalog/codegen.py` hashes identically (`70583765…`) across all three repos with zero citations, confirming D-17's sync-then-strip requirement. |
| 7 | TOOLS-07: `audit_coverage_matrix.py --check` exits 0, or the staleness is recorded as a decision with cause | ✓ VERIFIED | Tool deleted (D-06); its last measured behaviour before deletion (exit 1, zero bytes on stdout/stderr) is recorded in `host-tools-retirement.md` §6, matching CONTEXT.md's pre-phase measurement exactly. |
| 8 | "Explicitly NOT in scope" paragraph: no tool is deleted on reference-count evidence alone; `derive_sdp_partition.py` in particular stays protected from that specific evidence class | ✓ VERIFIED (disclosed deviation) | `derive_sdp_partition.py` was deleted, but ROADMAP's amendment states plainly it was deleted "on the operator's judgment about its value, not on the reference-count evidence this paragraph forbids" — the distinction is named, not elided, and matches `host-tools-retirement.md` §1/§2 cost 4 and `188-05-SUMMARY.md`'s own framing (D-15). |

**Score:** 7/7 roadmap success-criteria truths verified (criterion 5's scope-narrowing is disclosed, not a
failure; the "Explicitly NOT in scope" paragraph and the two criteria-1/2 attribution nits are recorded as
notes, not failures).

### Requirements Coverage

| Requirement | Disposition (REQUIREMENTS.md) | Cause recorded? | Verified in codebase? |
|---|---|---|---|
| TOOLS-01 | RETIRED | Yes — tool deleted, defect dissolved (188-05) | Yes — `audit_coverage_matrix.py` absent |
| TOOLS-02 | RETIRED | Yes — D-12, declaration layer dropped, blind spot carried forward (188-09) | Yes — no declaration convention exists; disclosed in verdict note |
| TOOLS-03 | Satisfied by family retirement | Yes — D-01 (all 10 gates), D-25 (90 consuming tests deleted, 0 collateral) (188-02/03/04) | Yes — 0 `check_*.py`/`test_check_*.py` files; D-25 replan documented and measured |
| TOOLS-04 | RETIRED | Yes — D-05/D-22, disposition tension stated explicitly (188-01/02/05) | Yes — 5 deleted, 1 relocated and working |
| TOOLS-05 | Complete | Yes — hand sweep with positive control (188-07/08) | Yes — six survivors clean; see truth 5 note on scope |
| TOOLS-06 | RETIRED | Yes — D-08, nothing left to sync (188-05/06) | Yes — apparatus gone both sides, baseline re-recorded |
| TOOLS-07 | RETIRED | Yes — D-06, last behaviour recorded (188-05) | Yes — recorded exit 1 / zero bytes matches CONTEXT.md |

No orphaned requirements: `REQUIREMENTS.md`'s traceability table maps exactly TOOLS-01…07 to Phase 188,
matching the phase's own declared requirement list with no extra or missing IDs.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter_app/tools/` (6 scripts) | `build_db.py`, `catalog/codegen.py`, `gen_sdp_bus_config.py`, `gen_test_image.py`, `gen_validation_header.py`, `parse_devtest_issue.py` | ✓ VERIFIED | `ls tools/*.py` + `catalog/codegen.py` matches exactly; no `check_*.py`, no GSD-process tool, no CI mirror, no frame-vector file remains |
| `.claude/skills/devtest-rootcause/scripts/diff_db.py` | skill-owned relocated copy | ✓ VERIFIED | Present, tracked, executable, resolves inputs from any cwd (188-01's own byte-identical-stdout proof) |
| `.planning/notes/host-tools-retirement.md` | D-23 verdict note | ✓ VERIFIED | Present, 259 lines, names every retired item, all 8 disclosed costs, the OD-1→D-25 supersession, deleted CLAUDE.md prose verbatim, the TOOLS-04 tension. Does **not** name the CLAUDE.md "Tooling gate (v1.8)" mypy-overstatement (WR-06) despite 188-04's own SUMMARY flagging it twice as "for 188-09's verdict note" — see Anti-Patterns below |
| `.planning/REQUIREMENTS.md` §TOOLS | 7 rows amended per D-22 | ✓ VERIFIED | Exact match to D-22's expected end state, only TOOLS-05 checkbox flipped |
| `.planning/ROADMAP.md` §Phase 188 | all 7 criteria + not-in-scope paragraph amended | ✓ VERIFIED | 8 `AMENDED by Phase 188` markers present, plan checklist 9/9 |
| `firestarter/scripts/baseline/size_baseline.json` | native envs re-recorded, AVR untouched | ✓ VERIFIED | 179/179/16 both envs; AVR `uno` flash_used unchanged by cold rebuild |

### Key Link Verification

| From | To | Via | Status |
|---|---|---|---|
| `.claude/skills/devtest-rootcause/SKILL.md` | relocated `diff_db.py` | path references, `check_dispatch.py` mentions dropped | ✓ WIRED |
| `tools/catalog/sync_to_subrepos.sh` | `firestarter`/`firestarter_app` `catalog/codegen.py` | sync run, byte-identity confirmed post-sync | ✓ WIRED |
| `ci.yml` (host) | surviving catalog/ruff/pytest steps | mypy + vector steps removed, catalog steps untouched | ✓ WIRED |
| `build.yml`/`beta-build.yml` (firmware) | native envs | vector CI steps removed in the same commit as their target files | ✓ WIRED |

### Anti-Patterns Found (from `188-REVIEW.md`, independently re-confirmed in the live tree)

| File | Issue | Severity | Confirmed live? |
|---|---|---|---|
| `firestarter_app/tools/parse_devtest_issue.py:212-215` (WR-01) | Comment claims a deleted test "is the only enforcement" of a forbidden-pattern property; there is now zero enforcement | Warning | Yes |
| `firestarter_app/tests/test_sdp_db_invariant.py:161-166` (WR-02) | Docstring cites a deleted gate (`check_sdp_capability_invariants.py`) as covering a widening signal it no longer does | Warning | Yes |
| `firestarter_app/tests/test_numeric_schema_source_scan.py:215,235` (WR-03) | Docstring/assertion say "tests 1 and 2" after test 2 was deleted; module docstring was corrected, function docstring/message were not | Warning | Yes |
| `firestarter_app/tests/test_build_db_inclusion.py:9-11` (WR-04) | Module docstring still claims an SC#3 dispatch-safety invariant "enforced by Plan 04" whose enforcing test was deleted this phase | Warning | Yes |
| `firestarter/.github/workflows/beta-build.yml:107-109` (WR-05) | Comment references "the vector gates above," which this phase deleted; the sibling `build.yml` has a self-contained comment at the same point | Warning | Yes |
| `firestarter_app/CLAUDE.md:127` (WR-06) | "Tooling gate (v1.8)" line still claims mypy is CI-enforced; the mypy CI step was deleted in 188-04. Disclosed twice in 188-04's SUMMARY as a gap "for 188-09's verdict note" — the verdict note does not mention it | Warning | Yes |
| `firestarter_app/tools/baseline/dispatch_baseline.json` (IN-01) | Fully orphaned data file (zero consumers, generator deleted) | Info | Yes |

None of the above is a `TBD`/`FIXME`/`XXX` debt marker, so the hard debt-marker gate does not fire. None
breaks a test or a build (both full suites and both native envs are green, confirmed by the
orchestrator's pre-run measurements and independently re-derived: `check_*.py` count 0, gate/tool file
counts 0, hash match on `codegen.py`, baseline JSON figures 179/179/16). All seven are genuine, verified
findings — six of them (all but IN-01) are stale claims of enforcement or relationship that this phase's
own deletions falsified, which is precisely the defect class this milestone ("Claim Hygiene") targets,
even though none falls inside any of the seven roadmap success criteria's literal text (TOOLS-05's own
scope is GSD-identifier citations, not general enforcement-claim accuracy, and the other four requirements
are about deciding a tool's fate, not about the accuracy of surviving prose elsewhere in the tree).

**My call:** these are WARNING-severity, not BLOCKER. They do not falsify any of the phase's seven
success criteria, do not leave any requirement's disposition inaccurate, and do not break a build or test.
But WR-06 is a distinct case from the other five: it was explicitly disclosed by 188-04's own SUMMARY as
an item "for 188-09's verdict note," and 188-09 — the very plan whose job was to write that note — did not
carry it forward. That is an incomplete execution of this phase's own documented intent, not merely an
out-of-scope residual. I am escalating the disposition of all six (fix now vs. file follow-on work) to
the human verification item above, rather than silently deciding for the operator or silently passing it.

### Behavioral Spot-Checks / Probe Execution

Not run independently — the orchestrator's pre-verification measurements (host pytest 3.11: 2129 passed,
0 failed; firmware pytest: 360 passed; `pio test -e native`/`native_nodevtools`: 179/179 each; three
`codegen.py` copies hash-identical with zero citations) were re-derived in part during this verification
(hash/citation/file-count checks above) and found consistent. No probe scripts (`scripts/*/tests/probe-*.sh`)
apply to this phase.

### Human Verification Required

1. **Test:** Decide the disposition of the six code-review warnings (WR-01 through WR-06).
   **Expected:** Either a quick task closes all six (rewording the five stale claims, and adding WR-06's
   mypy-CI-overstatement gap to `host-tools-retirement.md` as 188-04's own SUMMARY said would happen), or
   the operator explicitly accepts them as disclosed follow-on debt (e.g., a new todo naming all six by
   review ID, so they are not silently lost the way WR-06 nearly was).
   **Why human:** None of the six breaks a test or falsifies a roadmap success criterion, so this is a
   judgment call about the phase's completion bar under a milestone literally named "Claim Hygiene" — not
   something a truth/artifact/link check can resolve on its own.

### Gaps Summary

No must-have truth, artifact, or key link failed. The phase's subtraction-heavy goal is achieved and
verified directly against the codebase, not merely against the plans' own SUMMARYs: `tools/` holds exactly
the six declared survivors, every retired gate/tool/CI-mirror/apparatus fragment is actually gone (not
just claimed gone), the requirement ledger and ROADMAP accurately distinguish RETIRED from Complete with
cause recorded for each, and the two measured-not-met acceptance criteria from 188-04/188-06 were
genuinely resolved (render_shape mentions settled by 188-05; the 20-vs-21-line fixture discrepancy was a
plan miscount, correctly resolved to the natural, honest 20-line capture). The one open item is not a
failure but an unresolved disposition question: six code-review warnings, all confirmed live in the tree,
representing stale enforcement/relationship claims this phase's own deletions created — normal residue for
a phase of this size, but one of them (WR-06) is specifically a case where this phase's own documented
intent (get every disclosed gap into the verdict note) was not fully carried out. Routed to human decision
rather than silently passed or silently blocked.

---

## UAT Resolution (2026-09-13)

The single human-verification item was resolved at `/gsd-verify-work 188`. The operator chose the
second branch: **all six warnings accepted as disclosed follow-on debt**, rather than expanding
Phase 188 beyond its nine plans. The todo required by that branch is filed at
`.planning/todos/pending/2026-09-13-close-six-stale-claims-wr01-wr06.md`, naming all six by ID with
measured locations, and carrying WR-06's second obligation (the `host-tools-retirement.md` entry
188-04 promised and 188-09 did not deliver) as an explicit done-when condition. All six were
re-measured present in the tree at UAT time, and every retired enforcer they name was confirmed
deleted. `188-UAT.md` records the outcome; status is `complete`, 1/1 passed, 0 issues.

## Correction: `covered_digest` was computed before its own covered files settled

The `covered_digest` originally in this report's frontmatter (`v1:sha256:ee22edc0…`) matched neither
the covered files at the verification commit `070f6b46` nor at HEAD, so `verification.status`
returned `stale` unconditionally.

**It was not fabricated.** Sweeping historical revisions of the covered files shows `ee22edc0…` is
exactly the digest of the declared 26 files with `.planning/ROADMAP.md` at revision `cccfb7aa` — an
honest computation, taken before this phase's own close amendments rewrote ROADMAP.md and before the
report was committed. The digest was therefore already stale at the moment it landed.

This is a **systemic write-ordering issue, not a one-off**: the same reconstruction explains
`183` (ROADMAP at `dc309bf8`), `184` (ROADMAP at `25304374`) and `187` (REQUIREMENTS at `aa17f0a3`).
Five of v1.37's seven phases committed a digest that could never verify, because the fingerprint is
taken before the close sequence's own ROADMAP/REQUIREMENTS edits. `186` is unexplained by a
single-file sweep and may involve more than one covered file moving.

The frontmatter now carries `v1:sha256:12a63c61…`, emitted by
`gsd-tools query verification fingerprint` against the current tree — which includes the ROADMAP
`**Plans:**` repair made during this phase's transition. Detection power is unchanged: any later
edit to a covered file still trips the gate. An earlier note in this file called the original value
fabricated; that was wrong and is retracted here.

---

_Verified: 2026-09-13_
_Verifier: Claude (gsd-verifier)_
_UAT-resolved and digest-corrected: 2026-09-13_
