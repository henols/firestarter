---
phase: 98-fix-correct-the-0x08-32-pin-write-vpp-path
verified: 2026-07-01T12:00:00Z
status: passed
score: 4/4 must-haves verified
overrides_applied: 0
---

# Phase 98: FIX — Correct the 0x08 32-Pin Write/VPP Path Verification Report

**Phase Goal:** The firmware/host `0x08` 32-pin write/VPP path is corrected per the Phase 97 root cause so the AM27C020 program pulse actually asserts the correct signals — without regressing the passing `0x07`/`0x0B` EPROM paths or breaking any other DIP32 chip user; v1.16 golden register traces stay green; the fix is covered by native tests including a failure-case/mismatch test; any wire-crossing datum is delivered dual-repo lockstep; host CI is green on py3.11. **Explicitly no-bench** — Phase 99 (Leonardo + Rev 2.0) is the sole empirical silicon gate.

**Verified:** 2026-07-01
**Status:** passed
**Re-verification:** No — initial verification

## Adversarial Starting Point

This phase has a documented history of a real, review-caught defect: the original 98-01/02 fix (pinout redirect + firmware clear of logical `CTRL_ADDRESS_LINE_18`) was flagged by `98-REVIEW.md` (CR-01) as a **physical no-op on Rev 2.x hardware** — the exact bench hardware the operator uses — because that logical bit OR-aliases onto the same physical output as `CTRL_VPP_P1_ENABLE` (0x08), which is held HIGH throughout the program pulse. The phase was HELD, the operator did schematic study, and gap-closure plans 98-03/04/05 claim a corrected fix using a different, non-aliased control bit (`CTRL_READ_WRITE`, 0x40, via the existing `rw_line` mechanism). This verification independently re-derived and spot-checked the bit arithmetic and control-flow rather than trusting the SUMMARY narrative, given the project's own history of a first attempt that looked complete but was physically inert.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The corrected (non-aliased) CR-01 mechanism is what's actually live in the firmware, and the reverted 98-02 mechanism is gone | ✓ VERIFIED | `memory.cpp` `memory_set_data` no longer contains any `ctrl & ~CTRL_ADDRESS_LINE_18` clear (grep-confirmed, zero matches). It relies on the pre-existing `mem_util_remap_address_bus(handle, address, WRITE_FLAG)` (`WRITE_FLAG=0`, `include/memory_utils.h:14`) which ORs `read_write << config.rw_line` into the address. `config.rw_line` resolves from `pinouts.json`'s new `DIP32_27C020.pins.rw-pin:[31]` via `pin_conversions[32][31] == 22` (`database.py:141`, independently confirmed) → bit 22 of the reorganized address → `(address>>16) & CTRL_READ_WRITE` in `mem_util_calculate_top_address_register` (`memory.cpp:195`) → `CTRL_READ_WRITE = 0x40` (`rurp_pinout.h:82/94`), a bit distinct from the aliased `0x08` bit (`CTRL_VPP_P1_ENABLE`/`CTRL_ADDRESS_LINE_18_REV2`, `rurp_pinout.h:121/128`). Independently traced `rurp_hw_rev_utils.h` and confirmed `CTRL_READ_WRITE` (0x40) is revision-invariant: it survives both the Rev-2 passthrough mask (line 23) and the Rev-0/1 raw `ctrl_reg = data` passthrough (line 30). This is the same `rw-pin` mechanism already used and presumably working for `DIP32_SST39SF040` (confirmed `rw-pin:[31]` present there too) — not a novel, unexercised code path. |
| 2 | FIX-01 — 0x08 write path corrected, scoped to ≤256K, not breaking 27C040/SST39SF040 | ✓ VERIFIED | `DIP32_27C020` pinout confirmed assigned to exactly 88 chips in `chip_database.json`, all via `resolve_pinout_key`'s `proto_id==0x08 and mem_size<=MAX_27C020_SIZE` gate (`build_db.py:303`); AM27C020 itself confirmed in DB with `pinout: DIP32_27C020`, `algorithm: 8`, `size_bytes: 262144`. 27C040 (524288B) and SST39SF040 stay off `DIP32_27C020` (size-gated out; SST39SF040 already had its own dedicated pinout). Firmware mechanism is structurally inert (rw_line=0xFF disabled) for every pinout except the two that assign `rw-pin` — confirmed via `RC-98B` native test (512K/A18-user case, `rw_line=0xFF`, exactly 5 CONTROL writes, unaffected by the mechanism) which we ran and it passed. |
| 3 | FIX-02 — golden traces stay byte-identical for 0x07/0x0B/chip-id; native tests cover the corrected path incl. a failure-case/mismatch test | ✓ VERIFIED | Ran `pio test -e native` independently: **119/119 PASSED** (matches SUMMARY claim exactly). `git diff --stat` across the full phase span (pre-98-01 baseline `362bfa0` → final `35706c2`) on all four golden `.inc` files (`0x07`, `0x0B`, `chip-id`, `0x08`) is empty — byte-identical, independently confirmed. The mismatch/failure-case test requirement (v1.16 P89 CR-01 lesson) is satisfied by `test_wr01_rev2_pin31_pgm_low_with_vpp_concurrent`, read in full: it explicitly encodes the OLD 98-02 register value and asserts it would FAIL the LOW-assertion (a genuine RED-state comparison against the corrected value), not just a green assertion on the new mechanism. |
| 4 | FIX-03 + SAFE-02 — dual-repo lockstep and host CI green on the py3.11-scoped command set | ✓ VERIFIED | Independently ran and confirmed: `ruff check firestarter/ tests/` (pass), `ruff format --check firestarter/ tests/` (77 files formatted), `ruff check tools/build_db.py tools/diff_db.py tools/check_dispatch.py` (pass), `python tools/check_mypy_watermark.py` (1 error / 35 watermark — under threshold), `python tools/diff_db.py` (PASS, only the pre-existing Phase-94 PGSZ rows), `python tools/check_dispatch.py` (PASS, 746 scanned, 0 regressions, 0 consistency violations), `pytest tests/test_revision_constants_parity.py` (6 passed, including the new `test_max_27c020_size_parity`). `firestarter.h` `#define MAX_27C020_SIZE 262144` and `constants.py` `MAX_27C020_SIZE = 262144` confirmed present and cross-referenced. No `python3.11` binary exists in this devcontainer (independently confirmed absent) — the "CI-PENDING/structurally-green" framing in the SUMMARYs is honest, not a fabricated claim; commands were genuinely run under 3.12.13 and no 3.11/3.12-sensitive construct exists in the touched files. `primitives.cpp`/`eprom.cpp` `git diff --stat` across the whole phase is empty (SAFE-02 electrical-safety files untouched, independently confirmed); `chip_resolver.py` likewise untouched. |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/data/pinouts.json` (`DIP32_27C020`) | Scoped pinout with pin 31 off address bus, `rw-pin:[31]` | ✓ VERIFIED | Confirmed via direct JSON parse; `rw-pin: [31]`, pin 31 absent from `address-bus-pins` (18 lines, A0-A17). |
| `firestarter_app/tools/build_db.py` (`resolve_pinout_key`) | Size-keyed arm routing 0x08 ≤256K to `DIP32_27C020` | ✓ VERIFIED | `proto_id == 0x08 and mem_size <= MAX_27C020_SIZE` confirmed at line 303; imports named constant, no bare literal. |
| `firestarter_app/tools/diff_db.py` (`RC1_DIP32_27C020`) | Hardened classifier excluding compound voltage/type/vpp diffs (WR-03) | ✓ VERIFIED | Predicate confirmed to include `not voltage_diff and not type_diff and not vpp_diff` in addition to the original exclusions. |
| `firestarter/src/proms/memory.cpp` (`memory_set_data`) | Corrected mechanism (rw_line/CTRL_READ_WRITE), old A18-clear removed | ✓ VERIFIED | Read in full; old clear absent (grep-confirmed); new comment block accurately documents the corrected, revision-invariant mechanism. |
| `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp` | WR-01 revision-parametrized physical-remap tests + reconciled RC-98A/B/C | ✓ VERIFIED | Both WR-01 tests present, run, and pass; replica functions verified line-for-line against the real `rurp_hw_rev_utils.h`; RC-98B assertion confirmed `TEST_ASSERT_EQUAL(5, ...)` (exact, not `<=`). |
| `firestarter/include/firestarter.h` + `firestarter_app/firestarter/constants.py` | `MAX_27C020_SIZE` named constant, both sides | ✓ VERIFIED | Both present, both `262144`, cross-referenced comments, parity test passes. |
| `firestarter_app/tests/test_revision_constants_parity.py` (`test_max_27c020_size_parity`) | Cross-repo parity assertion | ✓ VERIFIED | Present, follows the file's established pattern, passes. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `pinouts.json` `DIP32_27C020.pins.rw-pin` | `database.py` `pin_conversions[32][31]` | `get_bus_config`'s rw-pin resolution loop | WIRED | Confirmed: pin 31 → bus line 22 → `config.rw_line = 22`. |
| `config.rw_line` (host wire value 22) | `CTRL_READ_WRITE` (firmware physical bit 0x40) | `mem_util_remap_address_bus` → `mem_util_calculate_top_address_register` | WIRED | Confirmed via direct arithmetic: bit 22 of the reorganized address, right-shifted 16, masked against `CTRL_READ_WRITE`, lands exactly on 0x40. |
| `CTRL_READ_WRITE` (0x40) | Physical pin 31 on Rev 2.x | `rurp_map_ctrl_reg_for_hardware_revision` passthrough mask | WIRED | Confirmed in `rurp_hw_rev_utils.h:23` — `CTRL_READ_WRITE` is in the Rev-2 passthrough mask, unaffected by the `CTRL_ADDRESS_LINE_18_REV2`/`CTRL_VPP_P1_ENABLE_REV2` 0x08 alias at lines 25-26. |
| `CTRL_READ_WRITE` (0x40) | Physical pin 31 on Rev 0/1 | Legacy `ctrl_reg = data` raw passthrough | WIRED | Confirmed `rurp_hw_rev_utils.h:30` copies `data` verbatim; 0x40 survives unchanged. |
| `AM27C020` DB entry | `DIP32_27C020` pinout | `chip_database.json` regen | WIRED | Confirmed by direct JSON inspection: `"pinout": "DIP32_27C020"`, `"algorithm": 8`, `"size_bytes": 262144`. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Native test suite green | `pio test -e native` (run independently, not from SUMMARY) | 119 test cases: 119 succeeded | ✓ PASS |
| WR-01 revision-parametrized tests present and passing | `pio test -e native -f "*test_val_eprom*" -v` | Both `test_wr01_rev2_pin31_pgm_low_with_vpp_concurrent` and `test_wr01_rev01_pin31_pgm_low_legacy` PASS | ✓ PASS |
| Golden traces byte-identical across the whole phase | `git diff --stat 362bfa0 35706c2 -- <4 golden .inc files>` | empty diff | ✓ PASS |
| Firmware compiles clean on both targets | `pio run -e uno` / `pio run -e leonardo` | SUCCESS, RAM/Flash usage matches SUMMARY exactly (Uno 73.1%/77.8%, Leonardo 89.7%/79.4%) | ✓ PASS |
| Host CI gate (ruff/format/mypy/diff_db/check_dispatch/parity) | see commands in Truth #4 | all pass, matching SUMMARY claims | ✓ PASS |
| Pre-existing out-of-scope failure genuinely pre-existing | `git diff 27da013 HEAD --stat -- tests/test_audit_coverage_matrix.py` | empty diff (file untouched by any 98-0x commit); failure reproduces at HEAD | ✓ PASS (confirms non-regression, not a phase defect) |

Full `pio test -e native` and the host CI command set were each run once; no full-suite command was repeated or filtered per-truth.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| FIX-01 | 98-03, 98-04 | 0x08 write path corrected per RCA, scoped, non-breaking | ✓ SATISFIED | Corrected `rw_line`/`CTRL_READ_WRITE` mechanism live; old inert mechanism removed; DIP32_27C020 scope confirmed (88 chips, size-gated). |
| FIX-02 | 98-01, 98-02 (reverted), 98-04, 98-05 | Golden traces green; native tests incl. mismatch test | ✓ SATISFIED | 119/119 native tests pass (independently run); golden traces byte-identical across the whole phase span; genuine RED/GREEN mismatch test present (WR-01). |
| FIX-03 | 98-01, 98-03 | Dual-repo lockstep for wire-crossing data | ✓ SATISFIED | `MAX_27C020_SIZE` present on both sides with a passing parity test; `diff_db.py`/`check_dispatch.py` both green with the corrected classifier hardening (WR-03). |
| SAFE-02 | 98-03, 98-04, 98-05 | Host CI green on py3.11-scoped commands; primitives/eprom untouched | ✓ SATISFIED | All CI-scoped commands independently re-run and green; `primitives.cpp`/`eprom.cpp`/`chip_resolver.py` confirmed untouched across the entire phase (`git diff --stat` empty). py3.11 binary genuinely absent from this devcontainer (independently confirmed) — CI-pending framing is honest, not fabricated. |

No orphaned requirements found for Phase 98 in REQUIREMENTS.md.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | No TBD/FIXME/XXX/TODO/HACK/PLACEHOLDER found in any file touched by 98-01 through 98-05 | — | None |

No debt markers found. The 98-REVIEW.md CR-01 finding (the one real blocker surfaced during this phase's lifecycle) has been independently confirmed closed by the corrected mechanism, not merely asserted closed.

### Minor / Non-Blocking Observations

1. **ROADMAP.md top-level phase checkbox bookkeeping lag.** `.planning/ROADMAP.md` line 240 (`- [ ] **Phase 98: FIX** ...`) still shows the phase-level summary checkbox unchecked, even though every individual plan checkbox under the "Phase Details" section (98-01 through 98-05, lines 288/292/296-298) is `[x]`, and STATE.md / REQUIREMENTS.md's traceability table both mark FIX-01/02/03/SAFE-02 as Complete. This is a cosmetic doc-sync gap (STATE.md itself calls out the REQUIREMENTS.md traceability line update as "a phase-close bookkeeping task"), not a functional gap — does not affect the FIX-01/02/03/SAFE-02 status. Recommend fixing the top-level ROADMAP checkbox at phase close.
2. **Blast radius of 88 chips reassigned to `DIP32_27C020` with only AM27C020 datasheet-verified.** Flagged by the pre-gap-closure cross-AI plan review (`98-REVIEWS.md`) as a MEDIUM risk — the size-keyed `resolve_pinout_key` arm reassigns every ≤256K 0x08/32-pin chip in the DB (confirmed 88 via direct count), not just AM27C020, without per-chip pin-31-role verification. This is accepted as-designed (D-02/D-04, "architectural correctness is class-wide" per STATE.md decisions) and is explicitly a Phase-99/future-bench residual, not a Phase-98 must-have — noted here for visibility, not as a gap.

### Human Verification Required

None. This phase is explicitly native/host-CI-only by ROADMAP design ("No bench required for this phase"); the actual silicon behavior (does pin 31 physically reach VIL and does the program pulse flip bits on the seated AM27C020) is Phase 99's sole empirical gate, not a Phase 98 deliverable. All Phase-98 must-haves are mechanically/statically verifiable and were independently re-derived above.

### Gaps Summary

No gaps found. All four Phase 98 success criteria (FIX-01, FIX-02, FIX-03, SAFE-02) are independently verified against the codebase — not merely asserted by SUMMARY.md. The critical finding from this phase's own code review (CR-01: the original fix was a physical no-op on Rev 2.x) has been independently traced end-to-end and confirmed corrected: the new mechanism uses `CTRL_READ_WRITE` (0x40), a control bit proven revision-invariant and structurally distinct from the aliased `CTRL_VPP_P1_ENABLE`/`CTRL_ADDRESS_LINE_18_REV2` (0x08) bit that defeated the original attempt. The native test suite (119/119, independently executed), the four golden traces (byte-identical across the full phase span, independently diffed), and the host CI gate (independently re-run) all corroborate the SUMMARY claims rather than merely repeating them.

---

*Verified: 2026-07-01*
*Verifier: Claude (gsd-verifier)*
