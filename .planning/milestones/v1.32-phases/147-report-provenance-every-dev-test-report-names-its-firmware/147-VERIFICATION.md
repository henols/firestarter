---
phase: 147-report-provenance-every-dev-test-report-names-its-firmware
verified: 2026-08-18T20:51:49Z
status: passed
score: 5/5 truths verified (0 present, behavior-unverified)
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "REQUIREMENTS.md and its Traceability table reflect PROV-05 and PROV-06 as complete, matching the ROADMAP flip table's explicit assignment of both flips to plan 147-06"
    status: resolved
    reason: >
      Plan 147-06's frontmatter (`requirements: [PROV-05, PROV-06]`) and its SUMMARY.md
      (`requirements-completed: [PROV-05, PROV-06]`) both claim these two requirements are complete,
      and the underlying code/tests genuinely satisfy them (verified independently below). But no
      commit in the phase — including the final `cda1eda3 docs(phase-147): update tracking after
      wave 4` commit, whose own diff touches only ROADMAP.md's plan checkbox and STATE.md — ticked
      PROV-05/PROV-06's checkboxes in REQUIREMENTS.md or updated its Traceability table. Both
      requirements still read `[ ]` (unchecked) in the requirements list (lines 66, 73) and
      "Pending" in the Traceability table (lines 236-237) as of HEAD. This is the execute-plan.md
      `update_requirements` step under-firing on the last plan of the phase — the same failure mode
      as `reference_executors_prematurely_mark_requirements_complete.md`/`reference_state_writers
      _underwrite_state_md.md`, but in the opposite direction (under-marking instead of
      over-marking). Functionally the phase goal IS achieved (see Observable Truths below); this is
      a bookkeeping gap in the authoritative requirements-tracking file, not a code gap.
    artifacts:
      - path: ".planning/REQUIREMENTS.md"
        issue: "PROV-05 (line 66) and PROV-06 (line 73) checkboxes are `[ ]`; Traceability table rows (lines 236-237) read \"Pending\" despite both requirements being satisfied by verified code and tests"
    resolved_by: "9c5805d9 docs(phase-147): tick PROV-05/PROV-06 and sync v1.32 coverage table"
    resolution: >
      Closed by the orchestrator immediately after this verification, as a bookkeeping-only fix with
      no code change. Root cause was the orchestrator's own continuation-agent dispatch prompt, which
      instructed the agent not to write STATE.md/ROADMAP.md; the agent over-applied that to
      REQUIREMENTS.md and skipped execute-plan.md's `update_requirements` step entirely.
      `requirements.mark-complete PROV-05 PROV-06` produced a surgical 4-line diff (no _normalizeMd
      blast radius). The secondary ROADMAP coverage-table desync was fixed in the same commit by hand
      edit, syncing all six PROV rows.
    originally_missing:
      - "Tick PROV-05 and PROV-06 to `[x]` in REQUIREMENTS.md's PROV section"
      - "Update the Traceability table rows for PROV-05 and PROV-06 to \"Complete\""
      - "(Secondary, non-blocking) ROADMAP.md's own Traceability table at lines 321-326 still shows ALL of PROV-01…06 as \"Pending\" — it was never kept in sync with REQUIREMENTS.md even for PROV-01…04, which REQUIREMENTS.md already marks Complete. Worth a follow-up fix, but REQUIREMENTS.md is the authoritative file this verification is scoped against."
---

# Phase 147: Report Provenance — every `dev test` report names its firmware — Verification Report

**Phase Goal:** A `dev test` report identifies the firmware and board that produced it, so any
community report — this milestone's own included — can be attributed to a firmware version before
any write-path claim is made about it.

**Verified:** 2026-08-18T20:51:49Z
**Status:** passed (all code/behavioral truths verified; the one documentation-tracking gap was closed by `9c5805d9` immediately after this report was written)
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth (ROADMAP Success Criterion) | Status | Evidence |
|---|---|---|---|
| 1 | A `dev test` report's `fw_board_identity` carries the real firmware/board identity (not an unconditional `null`), captured without opening a connection outside the orchestrator, with `EpromOperator.comm` still transient per-operation (SAFE-02 intact) | ✓ VERIFIED | `firestarter/hardware.py:151` `read_programmer_identity()` harvests `comm.firmware_identity` inside the existing `find_and_connect → expect_ack → disconnect` handshake (one connection). `cli_handlers.py:2501-2504` feeds it into `AutoCapture` by field name. Unit oracle `tests/test_hardware.py::test_read_programmer_identity_opens_one_connection_and_disconnects_once` passed live (re-run). `python3 tools/check_devtest_orchestrator.py` → PASS (0 VPP-set, 0 raw-wire-dict, 0 --force, 0 broad-except). |
| 2 | The recorded firmware string preserves its prerelease suffix — `3.0.0b19` is distinguishable from `3.0.0b11` | ✓ VERIFIED | `_scrub_identity()` is a printable-ASCII pass-through (no truncation of the suffix); `comm.firmware_identity` is the raw, untruncated string per `serial_comm.py:412`, distinct from the separate `[\d.x]+`-truncated local at `serial_comm.py:866` (ring-fenced, confirmed byte-identical: `git diff --stat` against `serial_comm.py` from pre-phase baseline is empty). `test_two_identities_differing_only_in_suffix_land_as_different_values` and `test_prerelease_suffix_survives_into_the_report` re-run live, both pass. |
| 3 | A report written by an earlier schema version, carrying `fw_board_identity: null`, still parses without error against the bumped schema | ✓ VERIFIED | `firestarter/diagnostic_report.py:55` `SCHEMA_VERSION = "1.4"`. `tools/test_parse_devtest_issue.py::test_legacy_null_identity_body_still_parses_and_groups` (frozen `schema_version: "1.2"`, `fw_board_identity: null` fixture) re-run live, passes. Both `[dev test]` parsers accept `schema_version` by presence only (no ordering logic added — confirmed by reading `render_diff`/parser source, no schema-comparison code present). |
| 4 | When the identity is null/unobtainable, both the human-readable report surface AND the `[dev test]` issue parser show an explicit unknown marker — never a blank, never bare `None` | ✓ VERIFIED | `diagnostic_report.py`'s `_identity_cell()` routes both `fw_board_identity`/`hw_revision` rows through `NOT_REPORTED = "not reported"` in `render()` only (AST-confirmed confined to `{_identity_cell, render}`, never `to_dict()`). `tools/parse_devtest_issue.py`'s `render_diff()` and the devtest-triage skill script's `cmd_show()` both carry their own `NOT_REPORTED`/`_NOT_ATTRIBUTABLE` (`NOT_ATTRIBUTABLE`) literals. Live re-execution of the skill script against both the null- and populated-identity fixtures (see Behavioral Spot-Checks) reproduces byte-identical output to what SUMMARY 147-06 claims, including `firmware not reported -- NOT attributable to a firmware version -- ask the reporter for a fresh dev test run on a current host build` for the null case and `firmware 3.0.0b19:leonardo` for the populated case. `python3 tools/check_diagnostic_report_claims.py` → PASS (167 literals scanned, 0 forbidden matches). |
| 5 | A triager reading a parsed `[dev test]` issue can attribute the report to a firmware version without asking the reporter | ✓ VERIFIED (via completed human checkpoint, not deferred) | Plan 147-06 Task 3 was a **blocking** `checkpoint:human-verify` (not an end-of-phase-deferred item) that already executed during the phase, with a genuine human verdict recorded in 147-06-SUMMARY.md: "Part A — APPROVED" and "Part B — APPROVED" (attribution answerable from the populated render, explicitly refused from the null render), with auto-mode independently confirmed inactive for the run. This verifier re-ran all four render commands (skill `show` × 2 fixtures, app `parse_devtest_issue.py` × 2 fixtures) live and confirmed the outputs match the SUMMARY's transcript exactly — the human verdict rests on real, reproducible evidence, not a hallucinated transcript. |

**Score:** 5/5 ROADMAP success criteria verified. 0 behavior-unverified.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter_app/firestarter/hardware.py` | `ProgrammerIdentity` NamedTuple, `_scrub_identity`, `read_programmer_identity` | ✓ VERIFIED | All three present (lines 38, 50, 151); read via `Read`/`grep`, logic matches SUMMARY claims exactly, including the D-04 independent-failure-path structure and D-07 scrub semantics |
| `firestarter_app/firestarter/cli_handlers.py` | `dev_test` handler feeds `AutoCapture` from a real captured identity by field name | ✓ VERIFIED | `cli_handlers.py:2501-2504`: `identity = app.hardware_manager.read_programmer_identity()` → `AutoCapture(..., fw_board_identity=identity.fw_board_identity, ...)` |
| `firestarter_app/firestarter/diagnostic_report.py` | `SCHEMA_VERSION` 1.4, `NOT_REPORTED`, `_identity_cell`, both identity rows routed through it | ✓ VERIFIED | `SCHEMA_VERSION = "1.4"` (line 55), `NOT_REPORTED = "not reported"` (line 103), `_identity_cell()` (line 375), applied to both rows (lines 568-569) |
| `firestarter_app/tools/parse_devtest_issue.py` | `NOT_REPORTED`, `_NOT_ATTRIBUTABLE`, two new labelled rows in `render_diff` | ✓ VERIFIED | Lines 205, 217, 223-271: labelled `host_version`/`fw_board_identity` rows, not-attributable clause folded in on absence, no `hw_revision` row (D-15, confirmed 0 hits for `hw_revision` in the file) |
| `.claude/skills/devtest-triage/scripts/devtest_issues.py` | Own `NOT_REPORTED`/`NOT_ATTRIBUTABLE` literals plus a firmware line in `cmd_show` | ✓ VERIFIED | Lines 54, 63-64, 386-390; tracked in git (`git ls-files .claude/skills/devtest-triage` lists it); live execution reproduces the documented render |
| `.claude/skills/devtest-triage/SKILL.md` | Regenerated §2 transcript matching real script output | ✓ VERIFIED | The fenced transcript at SKILL.md lines ~66-91 is byte-identical to a fresh live run of `show --body-file` against the null-identity fixture (confirmed by direct comparison in this session) |
| Two committed fixture bodies (populated + null identity) | Make the render verifiable offline/hermetically | ✓ VERIFIED | `.claude/skills/devtest-triage/fixtures/dev-test-at28c256-{null,populated}-identity.md`, both tracked, both re-run live in this session with matching output |
| `.gitignore` un-ignore of `.claude/skills/` | Precondition for tracking the skill files | ✓ VERIFIED | `.gitignore` lines 4-8 confirm `!.claude/skills/` un-ignore; `git ls-files .claude/skills` lists exactly the devtest-triage files (plus `find-skills` stays untracked, as designed) |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `comm.firmware_identity` (`serial_comm.py:412`) | `ProgrammerIdentity.fw_board_identity` | harvested inside `read_programmer_identity`'s existing `try`, before `expect_ack()` | ✓ WIRED | Confirmed by direct code read; D-04 ordering (harvest before ack, so an ack failure doesn't discard identity) is present at `hardware.py:184-185` |
| `ProgrammerIdentity` | `AutoCapture(fw_board_identity=...)` | `cli_handlers.py`'s `dev_test` handler, named-field access | ✓ WIRED | `cli_handlers.py:2501-2504` |
| `AutoCapture.fw_board_identity` | saved report JSON `auto_capture.fw_board_identity` | `to_dict()`/`to_json_block()` pass the field through untouched (never through `_identity_cell`, D-10) | ✓ WIRED | AST scan (from 147-03 SUMMARY, independently spot-checked by reading `diagnostic_report.py:532-563`) confirms `_identity_cell`/`NOT_REPORTED` referenced only by `{_identity_cell, render}` |
| `firestarter.diagnostic_report.NOT_REPORTED` | `tools.parse_devtest_issue.NOT_REPORTED` | value-parity, not import (D-11 — stdlib-only module contract forbids the import) | ✓ WIRED | Live cross-import in this session: both equal `"not reported"` |
| Both app-side `NOT_REPORTED` literals | `.claude/skills/devtest-triage/scripts/devtest_issues.py`'s own `NOT_REPORTED` | value-parity, human-checkpoint-verified (no automated cross-repo test, by design — RESEARCH P-6) | ✓ WIRED | Live three-way import in this session (app repo `firestarter.diagnostic_report`, `tools.parse_devtest_issue`, and the skill script loaded by file path) — all three equal `"not reported"` |
| `render_diff()` / skill `cmd_show()` | rendered `[dev test]` triage output | labelled `fw_board_identity` row present, not-attributable clause on absence | ✓ WIRED | Live execution of both parsers against both fixtures in this session reproduces exactly the labelled rows described |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Skill `show`, null-identity fixture, names the firmware line + refusal | `python3 .claude/skills/devtest-triage/scripts/devtest_issues.py show --body-file .../dev-test-at28c256-null-identity.md ...` | `firmware    not reported -- NOT attributable to a firmware version -- ask the reporter for a fresh dev test run on a current host build`, exit 0 | ✓ PASS |
| Skill `show`, populated-identity fixture, names the real firmware | same, populated fixture | `firmware    3.0.0b19:leonardo`, exit 0 | ✓ PASS |
| App parser, null-identity fixture | `python3 tools/parse_devtest_issue.py --body-file .../null-identity.md ...` | `fw_board_identity:       not reported -- NOT attributable...`, exit 0 | ✓ PASS |
| Three-way marker parity (live cross-import) | direct Python import of all three `NOT_REPORTED` literals | all three equal `'not reported'` | ✓ PASS |
| `check_devtest_orchestrator.py` (SAFE-02 gate) | `python3 tools/check_devtest_orchestrator.py` | `PASS: ... 0 VPP-set, 0 raw-wire-dict, 0 --force, 0 broad-except` | ✓ PASS |
| `check_diagnostic_report_claims.py` (forbidden-phrase gate) | `python3 tools/check_diagnostic_report_claims.py` | `PASS: ... 167 string literals checked, zero forbidden matches` | ✓ PASS |
| Targeted unit tests re-run live (not just trusted from SUMMARY) | `pytest tests/test_hardware.py tests/test_dev_test_cmd.py tests/test_diagnostic_report.py tests/test_parse_devtest_issue.py -o addopts="" -q` | `151 passed` | ✓ PASS |
| `ruff check`/`ruff format --check` on all 4 touched app files | `ruff check ...`; `ruff format --check ...` | "All checks passed!"; "4 files already formatted" | ✓ PASS |
| Debt-marker scan (TBD/FIXME/XXX/TODO/HACK/PLACEHOLDER) on all touched files | `grep -nE ...` | 0 hits in any of the 5 modified/created source files this phase owns | ✓ PASS |

*(Full-suite `1616 passed, 1 warning` was already run once by the orchestrator per the task's context; this verifier additionally ran a scoped 151-test re-run of exactly the 4 files this phase touches to confirm the count independently without re-running the whole ~280s suite a second time.)*

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| PROV-01 | 147-02 (handler oracle), 147-04 (unit oracle) | Report records real firmware/board identity | ✓ SATISFIED (code); ✗ REQUIREMENTS.md checkbox correctly `[x]`, Traceability "Complete" | Matches flip table; no gap |
| PROV-02 | 147-02, 147-04 | Capture respects SAFE-02, no extraneous connection | ✓ SATISFIED (code); REQUIREMENTS.md `[x]`, "Complete" | Matches flip table; no gap |
| PROV-03 | 147-02 | Prerelease suffix preserved | ✓ SATISFIED (code); REQUIREMENTS.md `[x]`, "Complete" | Matches flip table; no gap |
| PROV-04 | 147-03 (advances), 147-05 (completes) | Schema bump + backward-compatible parse | ✓ SATISFIED (code); REQUIREMENTS.md `[x]`, "Complete" | Matches flip table; no gap |
| PROV-05 | 147-03 (advances), 147-04 (advances), 147-06 (completes) | Explicit unknown marker, never bare `None` | ✓ SATISFIED (code, verified live); ✗ REQUIREMENTS.md checkbox still `[ ]`, Traceability still "Pending" | **Gap** — see frontmatter `gaps` |
| PROV-06 | 147-05 (advances), 147-06 (completes) | Issue parser surfaces identity, attribution possible | ✓ SATISFIED (code + completed human checkpoint, verified live); ✗ REQUIREMENTS.md checkbox still `[ ]`, Traceability still "Pending" | **Gap** — see frontmatter `gaps` |

**Orphaned requirements:** None. The six plans' frontmatter `requirements:` arrays union to exactly `{PROV-01..06}`, matching REQUIREMENTS.md's Phase 147 mapping with no extra or missing IDs.

**Flip-table conformance:** Verified exact match against ROADMAP.md's explicit table — `147-01→none`, `147-02→PROV-03`, `147-03→none`, `147-04→PROV-01,PROV-02`, `147-05→PROV-04`, `147-06→PROV-05,PROV-06`. No plan ticked a requirement outside its permitted set.

### Anti-Patterns Found

None. Scanned all files this phase created/modified (`hardware.py`, `cli_handlers.py`, `diagnostic_report.py`, `parse_devtest_issue.py`, `devtest_issues.py`, plus their test files) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`/empty-implementation patterns — zero hits. `ruff check`/`ruff format --check` clean. `bash tools/ci_parity.sh` legs 1-3 exit 0 per SUMMARY (leg 4's exit-2 is documented pre-existing devcontainer behavior, not phase-caused — reconfirmed unrelated to this phase's files).

### Evidence Ceiling Compliance (binding, PROJECT.md §Current Milestone: v1.32)

Checked all touched files and both rendered outputs for any claim that `0x0D` is proven, any `support_status` change, or language closing gh#21/#32/#11/#12: none found. The not-attributable clause in both parsers/the skill script reads exactly as designed — "ask the reporter for a fresh dev test run" — never a write-path claim. The ceiling holds.

### Gaps Summary

The phase's actual deliverable — code and tests that make every future `dev test` report attributable
to a firmware version, on both the human-readable console surface and both `[dev test]` triage
surfaces (app parser + devtest-triage skill) — is genuinely built, tested, and live-reproducible; all
5 ROADMAP success criteria are VERIFIED against real code execution, not SUMMARY narrative.

The one gap is a **documentation-tracking defect**, not a functional one: `.planning/REQUIREMENTS.md`
never had PROV-05/PROV-06 ticked despite plan 147-06 (the plan the ROADMAP's own flip table assigns
both flips to) completing, and despite its own SUMMARY.md and STATE.md both narrating "PROV-05 +
PROV-06 complete." This should be a one-commit fix (tick two checkboxes + two Traceability rows) with
zero code risk, but it must land before the phase can be considered fully closed per this project's
own bookkeeping contract — a REQUIREMENTS.md checkbox is the single source of truth other phases
(150, which depends on 147) will check.

---

*Verified: 2026-08-18T20:51:49Z*
*Verifier: Claude (gsd-verifier)*
