---
phase: 74
slug: per-family-correctness-fixes-flash-gated
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-18
---

# Phase 74 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Unity (PlatformIO `[env:native]`) for firmware + pytest for host |
| **Config file** | `firestarter/platformio.ini` `[env:native]`; `firestarter_app/pyproject.toml` |
| **Quick run command** | `cd firestarter && pio test -e native` (~20s) / `cd firestarter_app && python3 tools/check_dispatch.py && python3 tools/diff_db.py` |
| **Full suite command** | `cd firestarter && pio run -e leonardo && pio test -e native` ; `cd firestarter_app && pytest --cov-fail-under=70` |
| **Estimated runtime** | ~60 seconds (native + leonardo build + host gates) |

---

## Sampling Rate

- **After every task commit:** Run `pio test -e native` (firmware tasks) or `python3 tools/check_dispatch.py && python3 tools/diff_db.py` (host tasks)
- **After every plan wave:** Run `pio run -e leonardo && pio test -e native && pytest --cov-fail-under=70`
- **Before `/gsd-verify-work`:** Full suite green + Tier-3 W29C040 re-bench PASS + Leonardo flash-% recorded (must stay under ~88% ceiling — research warns budget is already 88.9%; the FIX-02 additions need an actual measurement)
- **Max feedback latency:** ~60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 74-FIX01 | TBD | 1 | FIX-01 | — | N/A (no code change) | Tier-3 evidence (existing) | `grep 'VAL-06' firestarter_app/val-results/sram/val06-perbyte-verdict.txt` | ✅ | ⬜ pending |
| 74-FIX02A | TBD | 1 | FIX-02 | — | dispatch only; no VPP | Tier-1 native dispatch | `cd firestarter && pio test -e native -f "*test_dispatch*"` | ✅ (extend `test_configure_memory.cpp`) | ⬜ pending |
| 74-FIX02B-sdp | TBD | 1 | FIX-02 | T-74-VPP | SDP unlock sent; VPP regulator bit NEVER set | Tier-1 recording-stub | `cd firestarter && pio test -e native -f "*test_val_flash4*"` | ✅ (extend `test_val_flash4.cpp`) | ⬜ pending |
| 74-FIX02B-vpp | TBD | 1 | FIX-02 | T-74-VPP | `flash4_write_execute` asserts NO `CTRL_VPP_REGULATOR_ENABLE` | Tier-1 VPP-bit assertion | `cd firestarter && pio test -e native -f "*test_val_flash4*"` | ✅ (extend `test_val_flash4.cpp`) | ⬜ pending |
| 74-FIX02B-bench | TBD | 2 | FIX-02 | T-74-VPP | W29C040 write+read-back == source SHA on Leonardo | Tier-3 HIL bench | `firestarter -p /dev/ttyACM0 dev validate-family flash4 --board leonardo --chip W29C040 --source val-results/flash4/w29c040-source.bin --output-dir val-results/flash4` | ✅ (source bin on disk) | ⬜ pending |
| 74-FIX03 | TBD | 1 | FIX-03 | — | doc reconciliation only | Static/doc assertion | `grep -n '0x39\|0x35' firestarter/CLAUDE.md firestarter/src/proms/memory.cpp firestarter_app/firestarter/database.py firestarter_app/firestarter/ic_layout.py` | ✅ | ⬜ pending |
| 74-REGRESSION | TBD | * | all | — | no family regresses | All tiers | `python3 firestarter_app/tools/check_dispatch.py && python3 firestarter_app/tools/diff_db.py && cd firestarter && pio test -e native` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — add `test_flash4_check_chip_id_*` (FIX-02A RED→GREEN); file already exists, extend it
- [ ] `firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp` — add operation-phase SDP recording test + operation-phase VPP-bit assertion (FIX-02B RED→GREEN); file already exists, extend it
- [ ] No new test files or framework install needed — both extend existing native suites

*Existing infrastructure covers all phase requirements; only test cases are added.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| W29C040 chip-OUT VPP multimeter dry-run before any seated write | FIX-02 (T-74-VPP) | Requires physical multimeter on the socket VPP pin; cannot be asserted in software | With chip OUT, run the flash4 write path and confirm socket VPP pin stays at ~5V (never 12V+) before seating the W29C040; operator-only |
| Tier-3 W29C040 write+read-back on Leonardo | FIX-02 | Requires real silicon + Leonardo + working shield; standing bench precondition (R1≈270000, retry-on-timeout, Leonardo-only, verify `controller:` identity) | Run the `dev validate-family flash4` command above; verify readback SHA == source SHA, retry_count recorded |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies (Tier-3 bench + VPP multimeter are documented manual-only)
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
