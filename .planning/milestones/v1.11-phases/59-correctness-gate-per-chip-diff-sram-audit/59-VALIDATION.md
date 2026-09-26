---
phase: 59
slug: correctness-gate-per-chip-diff-sram-audit
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-09
---

# Phase 59 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + existing `firestarter_app` test suite |
| **Config file** | `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `cd firestarter_app && python tools/check_dispatch.py` (GATE-03, fast) |
| **Full suite command** | `cd firestarter_app && pytest --cov-fail-under=70` |
| **Estimated runtime** | ~10–30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd firestarter_app && python tools/check_dispatch.py` (confirms no dispatch regression)
- **After every plan wave:** Run `cd firestarter_app && pytest --cov-fail-under=70`
- **Before `/gsd-verify-work`:** All 4 phase success criteria green
- **Max feedback latency:** ~30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 59-01-* | 01 | 1 | GATE-02 | — | `diff_db.py` exits 0 — all 371 changed + 9 new chips explained by a cited root-cause rule; exits 1 on any unexplained diff | integration | `cd firestarter_app && python tools/diff_db.py` | ❌ W0 (new script) | ⬜ pending |
| 59-01-* | 01 | 1 | GATE-02 | — | unexplained-diff disposition surfaces the offending chip(s) | unit | `cd firestarter_app && pytest tests/test_diff_db.py -x` | ❌ W0 (optional — diff_db.py is itself the gate) | ⬜ pending |
| 59-0x-* | 0x | 1 | GATE-03/SC#2 | — | `check_dispatch.py` exits 0 across full 743-chip set incl. `DIP24_2816` | integration | `cd firestarter_app && python tools/check_dispatch.py` | ✅ exists | ⬜ pending |
| 59-0x-* | 0x | 1 | SC#4 | — | two consecutive `build_db.py` runs from pinned `infoic.xml` are byte-identical | integration | determinism harness (see Wave 0) | ❌ W0 (new harness) | ⬜ pending |
| 59-0x-* | 0x | 2 | GATE-04/SC#3 | — | SRAM blank-check / WP# / RTC behaviors documented in both layers; no silent safety dismissal | manual | human review of `59-SRAM-AUDIT.md` + shipped doc | ❌ W0 (new docs) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter_app/tools/diff_db.py` — re-runnable grouped-by-cause full-record diff (covers GATE-02)
- [ ] SC#4 determinism harness (small shell/Python: regen twice from pinned `infoic.xml`, byte-compare) — covers SC#4
- [ ] `firestarter_app/doc/sram-nvram-behavior.md` (or `sram.cpp` comment block) — covers GATE-04 shipped doc
- [ ] `.planning/phases/59-correctness-gate-per-chip-diff-sram-audit/59-SRAM-AUDIT.md` — covers GATE-04 planning audit artifact
- [ ] (optional) `firestarter_app/tests/test_diff_db.py` — unit stub for the unexplained-diff exit path

*Existing infrastructure covers SC#2 (`check_dispatch.py`) and the diff anchor (`chip_database.baseline.json` already committed in `f92873d`).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| SRAM/NVRAM behavioral truths (blank-check, WP#, RTC) documented and accurate | GATE-04 / SC#3 | Documentation correctness is a human-judgment exercise against datasheet behavior; `configure_sram` is a 2-line no-op so there is no code path to assert | Review `59-SRAM-AUDIT.md` + shipped doc cover all three truths; confirm escalation criterion ("only if a real safety issue") is honored |
| Grouped-by-cause diff rationales cite minipro source correctly | GATE-02 | Citation accuracy (permalink + pinned SHA `a8efaedc`) is verified against the recorded source, not asserted programmatically | Spot-check each root-cause group's citation resolves to the recorded minipro `database.c`/`.h` SHA |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
