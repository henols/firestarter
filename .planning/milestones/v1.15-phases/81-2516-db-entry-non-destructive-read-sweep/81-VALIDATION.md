---
phase: 81
slug: 2516-db-entry-non-destructive-read-sweep
status: validated
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-23
validated: 2026-06-24
---

# Phase 81 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (firestarter_app) |
| **Config file** | firestarter_app/pyproject.toml |
| **Quick run command** | `cd firestarter_app && pytest tests/test_database_conversion.py -q` |
| **Full suite command** | `cd firestarter_app && pytest -q` |
| **Estimated runtime** | ~32 seconds (650 tests, per 2026-06-23 research run) |

---

## Sampling Rate

- **After every task commit:** Run the quick run command
- **After every plan wave:** Run the full suite command
- **Before `/gsd-verify-work`:** Full suite must be green (incl. the 0xA4 `test_init_phase_data_frames_not_acked` guard — SAFE-02)
- **Max feedback latency:** ~32 seconds

---

## Per-Task Verification Map

*Status audited 2026-06-24 against the live tree (commits 0cfc23b, e6e9870, 837321d on `v1.15-bench-validation-of-operator-inventory`). All automated commands re-run green; manual-only tasks confirmed operator-satisfied. See `81-VERIFICATION.md` (PASSED 5/5) for the goal-backward evidence.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 81-01-01 | 01 | 1 | DB-02, SAFE-03 | T-81-01 | FLAG_CAN_ERASE chain re-audited; W29C040/W29C020/W27C512 carry the flag, M27C512 does not; constant parity | unit | `cd firestarter_app && python3 -c "from firestarter.database import EpromDatabase; db=EpromDatabase(skip_local_override=True); print(all(db.convert_to_programmer(db.get_eprom(c))['flags']&0x02 for c in ('W29C040','W29C020','W27C512')) and db.convert_to_programmer(db.get_eprom('M27C512'))['flags']&0x02==0)"` | ✅ | ✅ COVERED |
| 81-01-02 | 01 | 1 | DB-02, SAFE-02 | T-81-01, T-81-02 | Flash/EEPROM pinning test green; 0xA4 guard green; full suite + ruff (CI target) green | unit | `cd firestarter_app && pytest tests/test_database_conversion.py::test_convert_w29c040_flash_eeprom_flag_can_erase tests/test_eprom_operations.py::test_init_phase_data_frames_not_acked -q && ruff check tests/test_database_conversion.py && ruff format --check tests/test_database_conversion.py && pytest -q` | ✅ | ✅ COVERED (651 passed) |
| 81-02-01 | 02 | 1 | GRAD-01, GRAD-02 | T-81-03, T-81-05 | 2516 user-override merged via name-key; decodes 0x0B/DIP24_2716/UV-EPROM/25000/2048; no FLAG_CAN_ERASE | integration | `cd firestarter_app && python3 -c "from firestarter.database import EpromDatabase; db=EpromDatabase(skip_local_override=False); e=db.get_eprom('2516'); assert e; print(db.convert_to_programmer(e)['flags']&0x02)"` | ✅ (`~/.firestarter/database.json`) | ✅ COVERED — env-dependent (user-override is home-dir, absent in CI; CI runs `skip_local_override=True`) |
| 81-02-02 | 02 | 1 | GRAD-02, EVID-01, EVID-02 | T-81-03, T-81-04 | SR-1 doc verifies 6 D-02 values + DIP24_2716 VPP=pin21; EVIDENCE.json 11 cells, locked columns, harness_version 81 | schema | `python3 -c "import json; d=json.load(open('.planning/v1.15/bench/EVIDENCE.json')); assert d['harness_version']=='81' and len(d['cells'])==11; print('ok')" && grep -q 'Operator sign-off' .planning/phases/81-2516-db-entry-non-destructive-read-sweep/81-2516-SAFETY-REVIEW.md && echo review-ok` | ✅ | ✅ COVERED |
| 81-02-03 | 02 | 1 | GRAD-02 | T-81-03, T-81-04 | Operator personally signs the 2516 safety review (blocking-human, never auto-approve) | human-check | manual — operator fills `**Operator sign-off:** [x] Approved` in 81-2516-SAFETY-REVIEW.md | n/a | ✅ SATISFIED — `[x] Approved — Henrik / 2026-06-23` |
| 81-03-01 | 03 | 2 | SWEEP-01, EVID-03, SAFE-01 | T-81-06, T-81-07, T-81-08 | 8 non-UV chips read (N>=3 byte-identical) + blank-check + negative control on Leonardo+Rev 2.0 | human-check | manual bench — operator records per-chip verdicts + wrong-file verify exit-nonzero into EVIDENCE | n/a | ✅ SATISFIED — 8/8 PASS (N=3); neg-control RC=1 on W27C512 |
| 81-03-02 | 03 | 2 | SWEEP-01, SWEEP-02, EVID-03, SAFE-01 | T-81-06, T-81-09 | 3 UV-EPROMs read (N>=3) + gating blank-state recorded; 2516 decode confirmed; no write | human-check | manual bench — operator records 3 UV BLANK/NOT-BLANK gating blank-states + 2516 info decode | n/a | ✅ SATISFIED — M27C512 BLANK / AM27C020 NOT-BLANK / 2516 ANOMALY (read-unstable, gates P83) |
| 81-03-03 | 03 | 2 | EVID-01 | T-81-06, T-81-09 | EVIDENCE.{md,json} finalized: 11 cells, no pending, UV gating blank-states, PASS rows non-vacuous (N>=3+SHA) | schema | `cd /workspaces && python3 -c "import json; d=json.load(open('.planning/v1.15/bench/EVIDENCE.json')); assert len(d['cells'])==11 and not [c for c in d['cells'] if c['verdict']=='pending']; print('ok')"` | ✅ | ✅ COVERED (11 cells, no pending) |

---

## Wave 0 Requirements

- *Existing infrastructure (pytest, ruff, mypy) covers all software phase requirements — no Wave 0 framework install needed.*
- *Hardware bench requirements (SWEEP-01/02, EVID-*) are manual-only — see below.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| 11-chip non-destructive read + blank-check on Leonardo + Rev 2.0 | SWEEP-01, SWEEP-02, EVID-01/02/03 | Requires physical chips + bench hardware (operator-executed) | Read + blank-check each chip; N≥3 byte-identical reads + negative control; record EVIDENCE row |
| 2516 user-override safety review sign-off | GRAD-02 | Human gate — operator personally approves the hand-authored override before bench | Operator signs `81-2516-SAFETY-REVIEW.md` checklist (D-01) |
| `firestarter info 2516` correct decode | GRAD-02 | Requires the user-override entry installed in `~/.firestarter/database.json` | Run `firestarter info 2516`, confirm 0x0B / DIP24_2716 / UV-EPROM / 25000mV / 2048 bytes |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references *(no Wave 0 needed — existing pytest/ruff infra)*
- [x] No watch-mode flags
- [x] Feedback latency < 32s *(full suite ~31s, 651 tests)*
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-06-24 — all 5 automated tasks re-run COVERED green (FLAG_CAN_ERASE chain `True`; pinning test + 0xA4 guard pass; full suite **651 passed** incl. the `test_list` snapshot; 2516 decode `flags&0x02=0`; EVIDENCE schema 11 cells / no pending; SAFETY-REVIEW sign-off present). All 3 manual-only bench/human tasks operator-satisfied (sign-off `[x] Henrik 2026-06-23`; 11-chip sweep recorded; UV blank-states gating Phase 83). Zero MISSING gaps → no auditor spawn required.

---

## Validation Audit 2026-06-24

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

**Notes:**
- This was a **State A** re-audit of a stale planner draft (all rows were `⬜ pending`). Every automated command was re-executed against the live tree and confirmed green; statuses promoted to ✅ COVERED / ✅ SATISFIED accordingly.
- **SC#4 coverage strengthened post-execution:** the planner draft's 81-01-02 "full suite green" command (`pytest -q`) initially failed (1 failed / 650 passed) because the 2516 user-override leaked into the `test_list` characterization snapshot. Resolved by the `FIRESTARTER_CONFIG_DIR` test seam in `firestarter/config.py` (commit 837321d) — the subprocess golden tests now run against an empty temp config dir, mirroring `EpromDatabase(skip_local_override=True)` at the process boundary. Full suite is now **651 passed** with the override installed. See `81-VERIFICATION.md` `resolved_gaps`.
- **Known coverage limitation (by design, not a gap):** 81-02-01's 2516 integration check depends on `~/.firestarter/database.json` (a home-dir user-override, intentionally not git/CI-tracked per GRAD-02). It runs green on the operator's machine but is not a repeatable CI test; CI exercises the DB path via `skip_local_override=True`. The 2516's correctness is additionally pinned by the operator-signed SR-1 safety review (human gate) — the sole compensating control for the bypassed `check_dispatch.py`/`diff_db.py`.
