---
phase: 103
slug: docs-reconcile-prose-divergence-record
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-07-01
---

# Phase 103 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> **Docs-only phase:** ships no new executable behavior. Requirements map to *verification
> commands* (existing gates + grep integrity checks over `firestarter/doc/PROTOCOLS.md`),
> not new unit tests. No new test files, no framework install (RESEARCH.md §Validation Architecture).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (host, `firestarter_app/tests/`) + PlatformIO Unity native (`firestarter/test/native/`) — both pre-existing; plus `grep` doc-integrity checks |
| **Config file** | existing `firestarter_app/` pytest config; `firestarter/platformio.ini` `[env:native]` — none installed this phase |
| **Quick run command** | `cd firestarter_app && python -m pytest tests/test_dispatch_mirror.py -q` |
| **Full suite command** | `cd firestarter_app && python -m pytest tests/ -q` ; `cd firestarter && pio test -e native` |
| **Estimated runtime** | ~30 seconds (host pytest + diff_db + grep); `pio test -e native` ~60–90 s when the native env is available |

---

## Sampling Rate

- **After every task commit:** targeted `grep` integrity checks on the edited section (anchors + D-02 retentions) — the per-task `<verify><automated>` blocks in 103-01.
- **After every plan wave:** Wave 1 (103-01) = doc-integrity grep set; Wave 2 (103-02) = full GATE-01/02/03 command set.
- **Before `/gsd-verify-work`:** full GATE-01/02/03 set green (or CI-PENDING for absent-tool legs) + all 8 anchors resolve.
- **Max feedback latency:** ~30 seconds (grep + host pytest); firmware native leg deferred-to-CI when `pio` absent.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 103-01-01 | 01 | 1 | DOC-01 | — | Anchors resolve; no false-STALE (slugger em-dash→`--`, en-dash→`-`, proven vs current anchors) | doc integrity (grep + python slug) | `grep -c '^### 1\.[0-9]* — 0x[0-9A-Fa-f]* PROTO_' doc/PROTOCOLS.md` == 12; python golden-anchor re-derive greps every `](#…)` fragment | ✅ existing | ⬜ pending |
| 103-01-02 | 01 | 1 | DOC-01 | — | 9 INV rows name PROTO_ token beside hex; SAFE-02 planned-test-name column strings byte-identical | doc integrity (grep -F) | per-INV `grep -E "^\| INV-0N \| .*PROTO_"`; `grep -F 'test_inv0*…'` retention; prose-purge greps | ✅ existing | ⬜ pending |
| 103-01-03 | 01 | 1 | DOC-02 | — | Divergence callout present (3 D-04 facts); §0 tables untouched (broadened L22–57 changed-line guard) | doc integrity (grep + git diff) | callout + NAME-F1 + ASCII + `_PROTOCOL_DISPLAY_NAME` + Phase-102 greps; `git diff --unified=0` §0-row guard | ✅ existing | ⬜ pending |
| 103-02-01 | 02 | 2 | GATE-01, GATE-02, GATE-03 | — | Dispatch behavior / DB identity / CLI grammar unchanged; absent-tool legs recorded CI-PENDING, never over-claimed PASS | existing gate + no-op | `pytest tests/test_dispatch_mirror.py -q`; `python tools/diff_db.py`; `pytest -k parity -q`; `pio test -e native` (CI-PENDING if absent); `git -C firestarter_app status --porcelain` | ✅ existing | ⬜ pending |
| 103-02-02 | 02 | 2 | GATE-01, GATE-02, GATE-03 | — | Milestone-CLOSED write gated on no-FAIL Task-1 verdicts | doc integrity (grep) | `! grep -qiE 'GATE-0[123].*FAIL' 103-VERIFICATION.md`; STATE/MILESTONES close markers | ✅ existing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements.*

- Docs-only phase: no new test file, no `conftest.py`, no framework install.
- GATE-01/02/03 are exercised by pre-existing tooling: `firestarter_app/tests/test_dispatch_mirror.py`, `firestarter_app/tools/check_dispatch.py`, `firestarter_app/tools/diff_db.py`, the constants-parity pytest selection (`-k parity`), and `firestarter/` `pio test -e native` (all [VERIFIED present] in RESEARCH.md §Existing Tooling / §Code Examples).
- DOC-01/DOC-02 are exercised by `grep` integrity checks (anchor resolution + D-02 retention strings) — no infrastructure to install.

---

## Manual-Only Verifications

*All phase behaviors have automated verification.*

- Every DOC-01/DOC-02 check is a deterministic `grep` / `git diff` command.
- Every GATE-01/02/03 check is an existing automated gate command.
- The only non-executed legs are `pio test -e native` and py3.11-scoped pytest **when those tools are absent in-session** — these are recorded `CI-PENDING` (deferred-to-CI, Phase-98 precedent), not manual verifications; CI runs them automatically.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies (all 5 tasks have automated verify; Wave 0 = existing infra)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (none — existing infra covers all requirements)
- [x] No watch-mode flags
- [x] Feedback latency < 30s (grep + host pytest)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-07-01
