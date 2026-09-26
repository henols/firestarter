---
phase: 76
slug: spec-only-gaps-adapter-required-x88c64
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-18
---

# Phase 76 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> Phase 76 is spec/classification-only (no new programmable chip, no firmware handler).
> Validation = software-gate greenness + spec-doc completeness, NOT hardware round-trips
> (which are explicitly deferred to a future adapter-graduation milestone).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (existing firestarter_app suite) |
| **Config file** | `firestarter_app/pyproject.toml` (pre-existing) |
| **Quick run command** | `cd firestarter_app && pytest tests/test_build_db_inclusion.py -v` |
| **Full suite command** | `cd firestarter_app && pytest --cov-fail-under=70` |
| **Estimated runtime** | ~30 seconds (unit) |

---

## Sampling Rate

- **After every task commit:** `cd firestarter_app && pytest tests/test_build_db_inclusion.py -v && python tools/diff_db.py && python tools/check_dispatch.py`
- **After every plan wave:** `cd firestarter_app && pytest --cov-fail-under=70`
- **Before `/gsd-verify-work`:** Full suite green + `diff_db.py` PASS + `check_dispatch.py` PASS (744 chips, 0 violations)
- **Max feedback latency:** ~30 seconds

---

## Per-Task Verification Map

| Req | Behavior | Threat Ref | Test Type | Automated Command | File Exists | Status |
|-----|----------|------------|-----------|-------------------|-------------|--------|
| GAP-01 | AT28C04/AT28C16 routed to `adapter-required` via the named `resolve_pinout_key` arm (name-keyed, not proto_id-keyed) | — | unit | `pytest tests/test_build_db_inclusion.py::TestAdapterRequired24Pin -v` | ✅ extend | ⬜ pending |
| GAP-01 | All adapter-required chips' reason string carries the named-arm wording | — | unit | `pytest tests/test_build_db_inclusion.py::TestUnsupportedReasonStrings -v` | ✅ extend | ⬜ pending |
| GAP-01 | DIP24→DIP32 adapter spec doc exists in BOTH layers (firestarter/doc/ + meta .planning/) and is lockstep-consistent | — | doc/source | `test -f firestarter/doc/<adapter-spec>.md && test -f .planning/<adapter-spec>.md` | ❌ W0 | ⬜ pending |
| GAP-02 | X88C64P `unsupported_reason` reworded — datasheet-accurate (parallel DIP24, feasible-candidate, handler not implemented); regression guard that it no longer says "serial-parallel hybrid" | — | unit | `pytest tests/test_build_db_inclusion.py::TestUnsupportedReasonStrings -v` | ✅ extend | ⬜ pending |
| GAP-02 | X88C64P `support_status` stays `protocol-not-implemented` (no graduation) | — | unit | `pytest tests/test_build_db_inclusion.py::TestProtocolNotImplementedInclusion -v` | ✅ | ⬜ pending |
| GAP-02 | X88C64 feasibility verdict + protocol spec written down (datasheet-sourced) | — | doc | `test -f .planning/<x88c64-feasibility>.md` | ❌ W0 | ⬜ pending |
| GAP-01+02 | diff_db gate green — reason-string delta classified as `RULE_PHASE66`, no support_status/dispatch delta | — | gate | `cd firestarter_app && python tools/diff_db.py` | ✅ gate | ⬜ pending |
| GAP-01+02 | check_dispatch gate green (744 chips, 0 violations); no chip newly `supported` | — | gate | `cd firestarter_app && python tools/check_dispatch.py` | ✅ gate | ⬜ pending |
| GAP-01+02 | Full suite above coverage floor | — | regression | `cd firestarter_app && pytest --cov-fail-under=70` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Extend `tests/test_build_db_inclusion.py::TestAdapterRequired24Pin` to assert the AT28C04/AT28C16 reason string contains the named-arm wording (existing test only checks the `adapter required:` prefix + presence).
- [ ] Add a regression test asserting the new X88C64P reason string does NOT contain "serial-parallel hybrid" (guards against re-introducing the datasheet-wrong description).

*All remaining infrastructure is pre-existing — build_db.py / diff_db.py / check_dispatch.py run locally.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Adapter spec pin-table is electrically correct (DIP24→DIP32 reroute, esp. /WE chip-pin-21 → socket-pin-30 against `DIP32_28C512_EEPROM`) | GAP-01 | Cannot be auto-verified without a physical adapter + golden round-trip (explicitly deferred) | Reviewer cross-checks the spec pin table against `pinouts.json` `DIP24_2816` ↔ `DIP32_28C512_EEPROM` bus roles before sign-off |
| X88C64 feasibility verdict is datasheet-accurate (multiplexed ALE bus; NO STORE/RECALL — that's the X2210/X2212 family) | GAP-02 | Datasheet-judgement, not test-assertable | Reviewer confirms the verdict matches the sourced datasheet and reconciles the ROADMAP "STORE/RECALL" wording with the corrected finding |

---

## Validation Sign-Off

- [ ] All tasks have an `<automated>` verify or a Wave 0 dependency (doc deliverables verified by file-exists + reviewer check)
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
