---
phase: 80
slug: at28c04-16-adapter-graduation
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-22
---

# Phase 80 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution. Host-only graduation (mirrors Phase 77); the only hardware gates are the physical adapter build (ADPT-01) and the Leonardo write+read-back proof (ADPT-03), both `autonomous: false`.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (firestarter_app) |
| **Config file** | `firestarter_app/pyproject.toml` (`.[test]`) |
| **Quick run command** | `cd firestarter_app && python3 -m pytest tests/test_chip_resolver.py tests/test_build_db_inclusion.py -v` |
| **Full suite command** | `cd firestarter_app && python3 -m pytest --cov --cov-fail-under=70 && python3 tools/check_dispatch.py` |
| **Estimated runtime** | ~30–60 seconds |

---

## Sampling Rate

- **After every task commit:** `cd firestarter_app && ruff check --target-version py39 . && ruff format --check --target-version py39 . && python3 -m pytest tests/test_chip_resolver.py tests/test_build_db_inclusion.py -v`
- **After every plan wave:** `cd firestarter_app && python3 -m pytest --cov --cov-fail-under=70 && python3 tools/check_dispatch.py`
- **Before `/gsd-verify-work`:** Full suite green AND bench proof (ADPT-03) on record
- **Max feedback latency:** ~60 seconds (software); hardware gates are operator-paced

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 80-01-xx | 01 | 1 | ADPT-01 | T-80-WIRE | DMM continuity confirms /WE chip-pin-21 → socket-pin-30 reroute BEFORE any chip inserted | manual/bench | N/A (operator DMM) | ❌ W0 | ⬜ pending |
| 80-02-xx | 02 | 2 | ADPT-02 | — | Graduation tests RED before edit (positive resolve + DB supported assertions) | unit | `pytest tests/test_chip_resolver.py tests/test_build_db_inclusion.py -v` | ❌ W0 | ⬜ pending |
| 80-03-xx | 03 | 2 | ADPT-02, SAFE-01/02/03 | T-80-DISPATCH | Named arm removed + DB regen; resolve_chip self-heals; check_dispatch green; 5 broken tests fixed in same wave | unit+integration | `pytest --cov --cov-fail-under=70 && python3 tools/check_dispatch.py` | ❌ W0 | ⬜ pending |
| 80-04-xx | 04 | 3 | ADPT-03, SAFE-01 | T-80-BENCH | Leonardo write+independent read-back SHA-match + non-vacuous negative control; guard removal proven as FINAL step | manual/bench | N/A (operator bench) | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky. Task IDs finalized by the planner.*

---

## Wave 0 Requirements

- [ ] `tests/test_chip_resolver.py` — add `test_resolve_chip_at28c16_supported_resolves` + `test_resolve_chip_at28c04_supported_resolves` (positive post-graduation); invert `test_resolve_chip_adapter_required_raises_not_implemented`
- [ ] `tests/test_build_db_inclusion.py` — update `TestAdapterRequired24Pin` (remove/invert AT28C assertions; add `test_at28c16_is_supported`); remove the two `TestUnsupportedReasonStrings` adapter-doc tests that break post-graduation
- [ ] `tests/test_cli_handlers.py` — update `test_info_adapter_required_shows_status` + `test_read_adapter_required_status_refusal` (re-target to a chip that stays non-supported, or assert the new supported behavior)
- [ ] No framework install needed — pytest infrastructure already present

*The named-arm DELETE + DB regen + all 5 test updates land in the SAME wave so the suite never goes red across a wave boundary (Phase 77 / Phase 79 discipline).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| DIP24→DIP32 adapter built + DMM continuity | ADPT-01 | Physical hardware build; no software proxy | Build per `firestarter/doc/AT28C04-ADAPTER.md`; DMM continuity-check every mapped pin, especially /WE chip-pin-21 → socket-pin-30 against `DIP32_28C512_EEPROM`, BEFORE inserting any chip |
| Leonardo write + independent read-back SHA-match + negative control | ADPT-03 | Requires real chip + adapter + trustworthy oracle board | On Leonardo (NOT uno328pb, NOT Rev 0), adapter seated: `firestarter -p <port> write <CHIP> src.bin` → `read <CHIP> rb.bin` → `sha256sum src.bin rb.bin` (must match); `verify <CHIP> wrong.bin` must exit non-zero; record live R1/R2 + silkscreen rev |

*VPP-free (0x0D, 5V-only): a mis-wire degrades to non-function, NOT chip damage — lowest hazard class in v1.14.*

---

## Open Validation Notes (for the planner to reconcile)

- **check_dispatch.py `configure_eeprom28c` invariant:** the research summary says the SAFE-02 gate passes **without modification** (configure_eeprom28c is excluded from `_DB_CHECKED_VPP_INVARIANTS = frozenset({"configure_flash_intel"})`), while the research §Critical mentions updating a `(0, 6000)`→`(0, 13000)` family invariant. The planner MUST resolve this by reading `check_dispatch.py:78-93` directly and deciding whether any invariant edit is actually required — and if so, land it in the same commit as the named-arm removal (semantic sync, Phase 79 T-79-CEIL discipline). Default expectation: no edit needed; confirm.
- **Chip availability:** AT28C16/AT28C04 on the bench is UNCONFIRMED — ASK the operator at Plan 01. If no chip and/or no adapter, the phase DEFERS CLEANLY (chips stay honestly `adapter-required`); only Plan 04 is hardware-blocked.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify (software plans 02/03) or are explicitly hardware-gated manual (plans 01/04, `autonomous: false`)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify (the two hardware gates bracket the software wave)
- [x] Wave 0 covers all MISSING references (test updates enumerated above)
- [x] No watch-mode flags
- [x] Feedback latency < 60s (software)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-06-22
