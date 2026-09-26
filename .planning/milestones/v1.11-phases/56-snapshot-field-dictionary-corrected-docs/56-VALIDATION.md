---
phase: 56
slug: snapshot-field-dictionary-corrected-docs
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-08
---

# Phase 56 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> **Phase character:** This phase produces only `.md` and `.json` artifacts — no Python code changes. Validation is therefore (a) shell smoke checks that the new/rewritten files exist and assert their corrected content, plus (b) a regression gate that the existing test suite stays green unmodified.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | `firestarter_app/pytest.ini` (uses pytest discovery) |
| **Quick run command** | `cd firestarter_app && python -m pytest tests/ -x -q` |
| **Full suite command** | `cd firestarter_app && python -m pytest tests/ --cov-fail-under=70` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run the task's inline shell smoke check (file-exists / content-grep)
- **After every plan wave:** Run `cd firestarter_app && python -m pytest tests/ -x -q`
- **Before `/gsd-verify-work`:** Full suite must be green (`--cov-fail-under=70`)
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| (baseline) | snapshot | 1 | GATE-01 | — | N/A | smoke | `test -f firestarter_app/tools/baseline/chip_database.baseline.json` | ❌ W0 (new) | ⬜ pending |
| (dictionary) | dictionary | 2 | DEC-01 | — | N/A | smoke | `test -f firestarter_app/doc/infoic-field-dictionary.md` | ❌ W0 (new) | ⬜ pending |
| (dictionary) | dictionary | 2 | DEC-03/04/05 | — | N/A | manual-review | Review dictionary semantics against §D-11 in 56-RESEARCH.md | N/A | ⬜ pending |
| (doc DOC-01) | docs | 3 | DOC-01 | — | N/A | smoke | `grep -q "UNKNOWN" firestarter_app/doc/package-details.md` | ✅ existing | ⬜ pending |
| (doc DOC-02) | docs | 3 | DOC-02 | — | N/A | smoke | `grep -qE "MP_ERASE_MASK\|can_erase" firestarter_app/doc/protocol-flags.md` | ✅ existing | ⬜ pending |
| (doc DOC-03) | docs | 3 | DOC-03 | — | N/A | smoke | `grep -qE "IC2_ALG\|[Pp]hantom" firestarter_app/doc/protocol-id.md` | ✅ existing | ⬜ pending |
| (regression) | docs | 3 | CI gate | — | Existing suite unaffected by docs/json | regression | `cd firestarter_app && python -m pytest tests/ --cov-fail-under=70` | ✅ existing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*No test-file gaps — Phase 56 has no new Python code to unit-test.* New-file existence is asserted with inline shell smoke checks in the plan tasks (no separate test file needed). The existing 734-chip characterization suite, WARNING-5 regression, and check_dispatch tests cover the regression gate as-is.

- [ ] (none — existing infrastructure covers all phase requirements)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Dictionary states correct decode semantics for BUG-1..4 (code unchanged this phase) | DEC-03, DEC-04, DEC-05 | Content correctness against minipro source is a review judgment, not a runnable assertion | Compare each in-scope attribute entry against §D-11 / Field Dictionary in 56-RESEARCH.md; confirm CONFIRMED/INFERRED/UNKNOWN markers and citation permalinks resolve |
| Citation permalinks resolve to the pinned minipro commit | DEC-01 | External URL resolution | Spot-check 2–3 `gitlab.com/.../blob/a8efaedc.../src/database.{c,h}#L…` links land on the cited symbol |

---

## Validation Sign-Off

- [ ] All tasks have an `<automated>` smoke/regression check or a documented manual-review entry
- [ ] Sampling continuity: no 3 consecutive tasks without an automated verify
- [ ] Wave 0 covers all MISSING references (none required)
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
