---
phase: 114
slug: disposition-no-auto-graduate-lock-graduation-ladder-inbox-re
status: planned
nyquist_compliant: true
wave_0_complete: true
created: 2026-07-03
---

# Phase 114 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (firestarter_app) |
| **Config file** | `firestarter_app/pyproject.toml` |
| **Quick run command** | `cd firestarter_app && python -m pytest tests/ -q -x` |
| **Full suite command** | `cd firestarter_app && python -m pytest tests/` |
| **Estimated runtime** | ~seconds (unit-only; no bench) |

---

## Sampling Rate

- **After every task commit:** Run `cd firestarter_app && python -m pytest tests/ -q -x`
- **After every plan wave:** Run `cd firestarter_app && python -m pytest tests/`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 114-01-01 | 01 | 1 | GRAD-01 | T-114-01/02 | build_db_diff derives report-side ladder_state (BAD→community-fail, all-OK→community-reported, marginal/none→""); community-confirmed never auto-emitted; single-source to_dict | unit | `cd firestarter_app && python -m pytest tests/test_diagnostic_report.py -q` | ❌ created in-plan | ⬜ pending |
| 114-01-02 | 01 | 1 | GRAD-01 | T-114-01 | Taxonomy doc: 4 states, auto-tag derivation, N≥2-via-dedup_fingerprint, manual build_db.py promotion (no code writes state) | presence+content | `test -f firestarter_app/doc/community-validation.md && grep -q community-confirmed firestarter_app/doc/community-validation.md && grep -q dedup_fingerprint firestarter_app/doc/community-validation.md` | ❌ created in-plan | ⬜ pending |
| 114-02-01 | 02 | 1 | INBOX-01, GRAD-01 | T-114-03/04/05 | Stdlib parser detects `[dev test]`+`schema_version`, surfaces DB-diff, counts matching dedup_fingerprints (D-03); fail-soft; no eval/exec/shell; no support_status write | smoke+static | `cd firestarter_app && python tools/parse_devtest_issue.py --help && ! grep -nE "eval\(|exec\(|shell=True" tools/parse_devtest_issue.py` | ❌ created in-plan | ⬜ pending |
| 114-02-02 | 02 | 1 | INBOX-01, GRAD-01 | T-114-03/05 | detect / db_diff / N-agreeing (2 match + 1 differ → count 2) / malformed-oversized-missing negative path, all bench-free (no gh) | unit (saved-JSON fixtures) | `cd firestarter_app && python -m pytest tests/test_parse_devtest_issue.py -q` | ❌ created in-plan | ⬜ pending |
| 114-03-01 | 03 | 2 | DISP-01 | T-114-06/07/08 | AST checker scans diagnostic_report.py + parse_devtest_issue.py for support_status writes; fail-closed empty scan; PASS names files; no eprom_info.py false-positive | subprocess/AST | `cd firestarter_app && python tools/check_no_community_support_status_write.py; test $? -eq 0` | ❌ created in-plan | ⬜ pending |
| 114-03-02 | 03 | 2 | DISP-01 | T-114-06/07 | Anti-hollow paired test: clean-baseline exit 0 + PASS names both targets; planted violation → non-zero FAIL; seam-isolation clean fixture exit 0 | unit (subprocess) | `cd firestarter_app && python -m pytest tests/test_check_no_community_support_status_write.py -q` | ❌ created in-plan | ⬜ pending |

*Wave-0 note: every code-producing task creates its own test/fixture within the same plan (task-level `tdd` or a paired test task), so no separate Wave-0 scaffolding plan is required — the RESEARCH "Wave 0 gaps" test files are the deliverables of Plans 01–03.*
*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Test scaffolding is folded into the implementation plans (no standalone Wave-0 plan):
- [x] GRAD-01 ladder tests — created in Plan 01 Task 1 (extends `tests/test_diagnostic_report.py`)
- [x] INBOX-01 parser tests + saved-JSON fixtures — created in Plan 02 Task 2 (`tests/test_parse_devtest_issue.py`)
- [x] DISP-01 anti-hollow paired test + planted fixtures — created in Plan 03 Task 2 (`tests/test_check_no_community_support_status_write.py`)
- [x] Reuse existing seams: `EpromDatabase(skip_local_override=True)` + mock operator; SAFE-03 anti-hollow planted-fixture pattern (`tests/test_check_devtest_orchestrator.py`); real `DiagnosticReport.to_json_block()` output as the parser fixture shape

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | — | — |

*All Phase 114 behaviors are host-Python + tooling — fully automated (no bench required).*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify (every task has an automated command)
- [x] Wave 0 covers all MISSING references (test files created within Plans 01–03)
- [x] No watch-mode flags
- [x] Feedback latency < 60s (unit-only, no bench)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** planner-approved 2026-07-03
