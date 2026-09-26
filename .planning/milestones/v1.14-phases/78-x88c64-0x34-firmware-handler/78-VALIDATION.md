---
phase: 78
slug: x88c64-0x34-firmware-handler
status: validated
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-22
validated: 2026-06-22
branch_executed: A (PCB-blocked deferral — zero code)
---

# Phase 78 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from 78-RESEARCH.md §"Validation Architecture". Two-branch phase:
> **Branch A (deferral, expected)** = documentation only, no code; **Branch B
> (handler-write, contingency)** = firmware + native tests, graduation still
> hardware-blocked (D-04).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Firmware native = Unity (PlatformIO `[env:native]`); Host = pytest |
| **Config file** | `firestarter/platformio.ini`; `firestarter_app/pyproject.toml` |
| **Quick run command** | `pio test -e native` (from `firestarter/`) / `pytest` (from `firestarter_app/`) |
| **Full suite command** | `pio test -e native && pio run -e leonardo` (firmware) + `pytest && ruff check --target-version py39` (host) |
| **Estimated runtime** | ~60–120 seconds (native suites + Leonardo build) |

---

## Sampling Rate

- **After every firmware task commit:** Run `pio test -e native` (all native suites)
- **After every host task commit:** Run `pytest` + `ruff check --target-version py39 --select I` (3.12-masks-CI trap)
- **Phase gate (Branch A — deferral):** No firmware changes; host tests green; `check_dispatch.py` green (no DB change).
- **Phase gate (Branch B — handler-write):** `pio test -e native` green + `pio run -e leonardo` ≤ ~90% flash + `pytest` green + `check_dispatch.py` green + `constants.py` ↔ `firestarter.h` parity green.
- **Before `/gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** ~120 seconds.

---

## Per-Task Verification Map

> Task IDs are illustrative until plans are finalized; the planner maps each task to one of these requirement rows.

**Branch executed: A (PCB-blocked deferral).** `A6 VERDICT: PCB-BLOCKED` (HIGH) was
recorded by Plan 01; Plan 02's [BLOCKING] gate read it and took the no-op defer path. **Zero
source code was written** (all 8 phase commits touch only `.planning/`). Consequently every
Branch B row is **N/A — deferral branch** (the handler, 0x34 dispatch arm, native test
suite, and `DIP24_X88C64` pinout were never created), not a MISSING automated-test gap.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 78-01-* | 01 | 1 | XIC-01 | T-78-03 | A6 verdict recorded with line-cited trace evidence; no speculative bit reuse | docs/trace | grep on `X88C64-FEASIBILITY.md` (verified in VERIFICATION 7/7) | ✅ | ✅ COVERED (doc-content; grep-verified) |
| 78-02-* (B) | 02 | 2 | XIC-02 | T-78-01 | 0x34 dispatch routes to `configure_x88c64`, BEFORE the `protocol != 0` guard | native dispatch | `pio test -e native -f "*test_dispatch*"` | ❌ never created | ⛔ N/A — deferral branch |
| 78-02-* (B) | 02 | 2 | XIC-02 | T-78-01 | configure phase sets NO VPP-enable bits; ALE/WR register order correct | native recording-stub | `pio test -e native -f "*test_val_x88c64*"` | ❌ never created | ⛔ N/A — deferral branch |
| 78-02-* (B) | 02 | 2 | XIC-03 | — | Leonardo flash ≤ ~90% | build measurement | `pio run -e leonardo` (read Flash % line) | ❌ no fw added | ⛔ N/A — deferral branch |
| SAFE-01 | 01,02 | — | SAFE-01 | T-78-01 | `chip_resolver.resolve_chip` host-guard NOT removed; X88C64P stays `protocol-not-implemented` | regression (existing) | `pytest -k "resolver or support_status"` + guard present at `chip_resolver.py:55` | ✅ | ✅ COVERED (existing suite) |
| SAFE-02 | 01,02 | — | SAFE-02 | T-78-01 | 0x34 stays non-dispatchable; no DB/dispatch regression | regression (existing) | `python tools/check_dispatch.py` (744 chips, 0 regressions) | ✅ | ✅ COVERED (existing suite) |
| SAFE-03 | 01,02 | — | SAFE-03 | — | `constants.py` ↔ `firestarter.h` flag/protocol parity untouched | regression (existing) | `pytest -k "parity or constants"` (5/5) | ✅ | ✅ COVERED (existing suite) |
| 78-XX (B) | — | — | XIC-04 | T-78-02 | N≥5 write+read-back SHA-match + negative control | Tier-3 bench | Manual — Leonardo + X88C64P + DIP24→DIP32 adapter | ❌ | ⬜ blocked (HW) — deferred FUT-01 |

*Status: ✅ COVERED · ⛔ N/A — deferral branch (Branch B not taken, no code) · ⬜ blocked (HW) = hardware-gated, deferred FUT-01*

---

## Wave 0 Requirements

**Branch A (deferral — expected landing):** None — no code files created; only `X88C64-FEASIBILITY.md` updated with the A6 verdict + future-unblock spec. Existing host/firmware infrastructure covers all provable behavior.

**Branch B (handler-write — contingency, only if A6 finds a free bit):**
- [ ] `firestarter/src/proms/eeprom_x88c64.cpp` — new file (configure + write functions)
- [ ] `firestarter/include/eeprom_x88c64.h` — new header
- [ ] `firestarter/test/native/avr/test_val_x88c64/test_val_x88c64.cpp` — new recording-stub test suite (model on `test_val_flash4`)
- [ ] `firestarter/test/native/avr/test_val_x88c64/host_stubs.cpp` — `#define HOST_STUBS_RECORD_BUS`
- [ ] `firestarter_app/firestarter/data/pinouts.json` — `DIP24_X88C64` entry (A7 planner decision = dedicated pinout, recommended)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| N≥5 write + read-back SHA-match + non-vacuous negative control | XIC-04 | No physical X88C64P chip and no DIP24→DIP32 adapter on hand (D-04) — graduation is hardware-blocked this phase regardless of the ALE verdict | DEFERRED to FUT-01: with Leonardo + X88C64P + adapter, run write→read-back→SHA-compare ≥5×; confirm a blank/wrong-data negative control fails; ASK which silkscreen shield rev is mounted; verify `r1 ≈ 270000` and `controller:` port identity first |

*The SC#4 graduation flip (`support_status`→`supported` + `resolve_chip` host-guard removal) is NOT performed this phase per D-04/D-05.*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or are explicitly hardware-gated/deferral-branch — XIC-01 grep-verified; SAFE-01/02/03 covered by existing suites; XIC-02/03 N/A (Branch B not taken); XIC-04 hardware-gated (FUT-01)
- [x] Sampling continuity: no 3 consecutive code tasks without automated verify (Branch B) — N/A, zero code tasks executed
- [x] Wave 0 covers all MISSING references (Branch B) — N/A on Branch A; no code files created (Wave 0 had no requirements on the deferral branch)
- [x] No watch-mode flags
- [x] Feedback latency < 120s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-06-22 — Nyquist-compliant by deferral exemption (no code → no automatable behavior beyond SAFE regression invariants, which existing suites cover).

---

## Validation Audit 2026-06-22

| Metric | Count |
|--------|-------|
| Automated-test gaps found | 0 |
| Resolved (tests generated) | 0 |
| Escalated to manual-only | 0 |
| Pre-existing automated coverage (SAFE-01/02/03) | 3 |
| Doc-content grep-verified (XIC-01) | 1 |
| N/A — Branch B not taken (XIC-02/03) | 2 (3 rows) |
| Hardware-gated manual, deferred FUT-01 (XIC-04) | 1 |

**Auditor:** not spawned — no source code was written this phase (Branch A / PCB-blocked
deferral; all 8 commits touch only `.planning/`), so there is no implementation to generate
tests against. All provable behavior is already covered: SAFE regression invariants by the
existing `check_dispatch.py` + parity pytest suites (both green in VERIFICATION 7/7), the A6
verdict by grep on `X88C64-FEASIBILITY.md`. XIC-02/XIC-03 are vacuously N/A on the deferral
branch; XIC-04 graduation is legitimately hardware-blocked and tracked under FUT-01.
No test files generated; no `gsd-nyquist-auditor` invocation required.
