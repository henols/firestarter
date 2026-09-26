---
phase: 89
slug: incremental-primitive-recompose
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-26
---

# Phase 89 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Detail source: `89-RESEARCH.md` → ## Validation Architecture.
> **For this refactor, the validation IS the existing Phase-88 oracle.** No new test
> infrastructure is built (SAFE-05). Every extraction step (P7→P4→P3→P5) reruns these
> exact green gates; a golden-trace diff is the review trigger (D-04), not auto-regression.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (firmware)** | Unity + ArduinoFake (`fakeit`), PlatformIO `[env:native]` (pio 6.1.19) |
| **Framework (host gates)** | python `tools/check_dispatch.py` + `tools/diff_db.py` (validate against CI py3.11, not the 3.12 devcontainer) |
| **Config file** | `firestarter/platformio.ini` `[env:native]` — **no change this phase** |
| **Quick run command** | `cd firestarter && pio test -e native -f "*test_val_<family>*"` |
| **Full suite command** | `cd firestarter && pio test -e native` |
| **Flash measure** | `cd firestarter && pio run -e leonardo` (parse `Flash: … used N bytes`); baseline `.flash-baseline-87.txt` = **25654 B** (89.5%) |
| **Host gates** | `cd firestarter_app && python tools/check_dispatch.py && python tools/diff_db.py` (both exit 0) |
| **Estimated runtime** | ~full native suite + leonardo build + 2 host gates, low single-digit minutes |

---

## Sampling Rate

- **Per task / extraction commit:** the narrow family suite(s) for that primitive + `pio run -e leonardo` delta (D-01 `≤+16B` per step) + INV grep.
- **Per primitive merge (commit kept):** full `pio test -e native` + both host gates (exit 0) + flash delta logged.
- **Phase gate (before `/gsd-verify-work`):** full `pio test -e native` green, `check_dispatch.py`/`diff_db.py` exit 0, `git -C firestarter_app diff --quiet` exit 0, final flash `< 25654 B`, achieved final flash % reported (PRIM-06).
- **Max feedback latency:** one extraction step (single atomic commit) — gates run between every primitive (D-02 abort-that-primitive-and-continue).

---

## Per-Phase Requirement → Test Map

> Per-task IDs are populated by the planner (plans do not yet exist at scaffold time).
> This map is the requirement-level oracle each task inherits.

| Req ID | Behavior (must stay TRUE) | Test Type | Automated Command | File Exists |
|--------|---------------------------|-----------|-------------------|-------------|
| PRIM-02 (P7) | eeprom28c SDP + flash write traces unchanged after dedup | golden trace | `pio test -e native -f "*test_val_eeprom28c*" -f "*test_val_flash4*" -f "*test_val_flash3*"` | ✅ |
| PRIM-03 (P4) | chip-id compare/report unchanged for eprom, flash_intel, eeprom28c, flash4 (flash3 has NO P4 site — D-03) | golden trace | `pio test -e native -f "*test_val_eprom*" -f "*test_val_flash_intel*" -f "*test_val_eeprom28c*" -f "*test_val_flash4*"` | ✅ |
| PRIM-04 (P3) | VPP window-check unchanged for eprom (0x07/08/0B) + flash_intel; INV-01/03 bit guards green; regulator routing stays handler-local | golden trace + INV asserts | `pio test -e native -f "*test_val_eprom*" -f "*test_val_flash_intel*"` | ✅ |
| PRIM-05 (P5) | eeprom28c + flash4 poll + eprom verify-readback unchanged; outer retry/page/erase loops untouched | golden trace | `pio test -e native -f "*test_val_eeprom28c*" -f "*test_val_flash4*" -f "*test_val_eprom*"` | ✅ |
| PRIM-06 | flash net-non-increase per step + final % recorded | build measure | `pio run -e leonardo` + Phase 87-04 `DELTA≤16` delta script | ✅ |
| SAFE-01 | protocol-keyed (`handle->protocol`); WARNING-5 guards (`novpp_in_eprom`/`eeprom28c_in_eprom`) preserved | dispatch + INV | `pio test -e native -f "*test_dispatch*"` + `check_dispatch.py` | ✅ |
| SAFE-02 | INV-01..09 survive each step, greppable ≥3 files | INV asserts + grep | full `pio test -e native` + `grep -rn INV-NN doc/ src/ test/` (×9) | ✅ |
| SAFE-03 | dispatch 0 violations, DB diff empty vs Phase-86-repinned 746-chip baseline | host gates | `check_dispatch.py` (exit 0) + `diff_db.py` (exit 0) | ✅ |

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| _populated during planning_ | — | — | PRIM-02..06 / SAFE-01..03 | T-89 (see Threats) | regulator routing + over-voltage check byte-identical | golden trace / build | per req map above | ✅ existing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- **None — existing test infrastructure covers all phase requirements.** The Phase-88 golden traces, INV-01..09 assertions, the `test_dispatch` mirror, and the two host gates are all present and green at HEAD (verified live this session: 34/34 in `test_val_eprom`+`test_dispatch`; `pio run -e leonardo` SUCCESS at 25654 B).
- The ONLY new artifact is the primitive source itself: `firestarter/src/proms/primitives.cpp` + `firestarter/include/primitives.h` (D-03). No new test file is required for a zero-diff extraction; a re-bless (D-04) edits an existing `.inc`, not a new file.

---

## Threat References (electrical-safety surface, see RESEARCH.md ## Security Domain)

| Ref | Pattern | Mitigation that MUST survive each step |
|-----|---------|----------------------------------------|
| T-89-01 | 12V/25V VPP regulator enabled on a 5V part | `check_dispatch.py` SRAM-never-reaches-eprom guard + protocol-keyed routing (D-06); P3 must not move regulator routing out of the handlers |
| T-89-02 | Over-voltage past the VPP window | `vpp_mv > set+500` HIGH check (`eprom.cpp:282`, `flash_intel.cpp:65`) — D-08; P3 extracts the *compare* but FORCE/ERROR semantics + threshold stay byte-identical |
| T-89-03 | Host bypassing the support-status guard | `chip_resolver.resolve_chip` (`chip_resolver.py:55`) never bypassed; no host change this phase (SAFE-06) |

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Achieved final flash % at phase close | PRIM-06 | Reported figure, derived from `pio run -e leonardo` | Record final `Flash: … N bytes` and % vs 25654 B baseline in phase SUMMARY |
| Re-bless decision (if any trace diffs) | D-04 | Human-gated audit checkpoint — confirm diff is benign register reorder before regenerating expected array | Inspect diff, document benign rationale in commit message |

*All automated behaviors have golden-trace / build / host-gate coverage; these two are review/reporting steps, not test gaps.*

---

## Validation Sign-Off

- [x] All tasks map to an existing golden-trace / INV / host-gate / flash-measure command (no Wave 0 needed)
- [x] Sampling continuity: gates run between every primitive extraction (D-02)
- [x] Wave 0 covers all MISSING references — N/A (none missing)
- [x] No watch-mode flags
- [x] Feedback latency = one atomic extraction commit
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-06-26 (gsd-plan-checker confirmed all 12 dimensions pass; validation body substantively correct)
