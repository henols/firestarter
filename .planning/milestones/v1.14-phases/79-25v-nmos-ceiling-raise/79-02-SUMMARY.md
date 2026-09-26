---
phase: 79-25v-nmos-ceiling-raise
plan: 02
subsystem: database
tags: [nmos, vpp, 25v, ceiling, build-db, check-dispatch, db-regen, chip-resolver, best-effort-graduation]

requires:
  - phase: 79-01
    provides: "NMOS-01 gate evidence (rail-corrected: VPE = 22.4V DMM / 23.9V fw at MAX pot, ~90% of 25V; the ~15-19V was VPP not VPE) — proceeded under the CONTEXT D-07 operator override (best-effort graduation, no hardware change ever)"
provides:
  - "RURP_VPP_CEILING_MV raised 22000->25000 (build_db.py) and _FAMILY_VPP_INVARIANTS['configure_eprom'] (0,22000)->(0,25000) (check_dispatch.py), in one commit"
  - "chip_database.json regenerated: 4 NMOS chips (INTEL M2716,M2716M; INTEL 2732,2732A,M2732,M2732A; SGS-THOMSON ETC2716,M2716; ST ETC2716,M2716) graduated vpp-exceeds-max -> supported, algorithm 0->11 (0x0B), vpp_mv=25000, no unsupported_reason"
  - "Zero vpp-exceeds-max chips remain in the DB; M2732A (21V) standalone entries untouched"
  - "check_dispatch.py exits 0 (734 supported / 10 non-dispatchable / 0 violations); FUT-02 (>25V fail-closed) preserved by the strict-greater compare"
  - "Test suite re-anchored off the now-empty vpp-exceeds-max category + 3 new non-vacuous tests; full suite green (cov 77.79%); ruff clean at py39"
  - "REQUIREMENTS.md FUT-03 corrected to the D-07 manual-potentiometer + best-effort framing"
affects:
  - "79-03 (demoted to informational best-effort bench validation — chips stay supported even if a write does not SHA-match, per D-07)"

tech-stack:
  added: []
  patterns:
    - "Best-effort graduation: graduate a chip to supported even when the rail under-drives, leaning on the firmware's under-voltage warn-and-proceed (over-voltage still blocked) — the user opts in (CONTEXT D-07)"
    - "Two-constant ceiling lockstep (build_db.py + check_dispatch.py) raised in the same commit to keep the CI invariant semantically consistent"
    - "Golden-fixture regeneration as a sanctioned downstream effect of a DB regen (tests/golden/v1.3-COVERAGE-MATRIX.md)"

key-files:
  created:
    - ".planning/phases/79-25v-nmos-ceiling-raise/79-02-SUMMARY.md"
    - ".planning/phases/79-25v-nmos-ceiling-raise/deferred-items.md"
  modified:
    - "firestarter_app/tools/build_db.py (RURP_VPP_CEILING_MV 22000->25000)"
    - "firestarter_app/tools/check_dispatch.py (_FAMILY_VPP_INVARIANTS configure_eprom (0,22000)->(0,25000))"
    - "firestarter_app/firestarter/data/chip_database.json (regenerated; 4 NMOS chips graduated)"
    - "firestarter_app/tests/test_build_db_inclusion.py"
    - "firestarter_app/tests/test_chip_resolver.py"
    - "firestarter_app/tests/test_cli_handlers.py"
    - "firestarter_app/tests/test_check_dispatch_invariants.py"
    - "firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md (regenerated — 4 chips 0x00->0x0B)"
    - ".planning/REQUIREMENTS.md (FUT-03 corrected)"

key-decisions:
  - "Proceeded with graduation despite the 79-01 gate being below the strict ≥25V bar (VPE = 22.4V DMM / 23.9V fw, ~90% of 25V; the ~15-19V was VPP not VPE), under the explicit CONTEXT D-07 operator override (best-effort graduation, no hardware change ever; the original CLEARED-gate clause was superseded)"
  - "Graduation is software-only via the build_db.py ceiling raise + DB regen; the host guard in chip_resolver.resolve_chip self-cleared from the regenerated support_status (no guard edit)"
  - "Re-anchored every vpp-exceeds-max test exemplar off M2716/M2732 (category now empty) to X88C64P (protocol-not-implemented) and AT28C04 (adapter-required)"
  - "Regenerated tests/golden/v1.3-COVERAGE-MATRIX.md — the only change is 4 chips moving algorithm 0x00->0x0B, a legitimate consequence of the graduation"

patterns-established:
  - "Best-effort graduation under operator override: the firmware over-voltage block stays the damage boundary; under-voltage is a warn-and-proceed (harmless); the SHA-match becomes informational"
  - "Non-vacuous ceiling tests: a positive control (vpp_mv=25000 passes the new range) + a negative control (vpp_mv=25001 still fails — FUT-02) instead of re-asserting the old 12000 fixture"

requirements-completed: [NMOS-02]

duration: ~25min
completed: 2026-06-23
---

# Phase 79 Plan 02: 25V NMOS Ceiling Raise (NMOS-02) Summary

**Raised the host VPP ceiling 22000→25000 in lockstep (build_db.py + check_dispatch.py), regenerated chip_database.json so the 4 NMOS UV-EPROMs (INTEL M2716, INTEL 2732/2732A/M2732/M2732A, SGS-THOMSON ETC2716, ST ETC2716) graduate from `vpp-exceeds-max` to `supported` (algorithm 0x0B, vpp_mv=25000) as a BEST-EFFORT graduation under the CONTEXT D-07 operator override — no hardware change, ever.**

## Best-Effort Graduation Framing (CONTEXT D-07 — important)

This plan is NOT a "≥25V proven" graduation. At MAX potentiometer the **VPE** (direct 0x0B) rail — the one these chips program on — measures **22.4V** (operator DMM) / 23.9V (fw `firestarter vpe`), ~90% of the rated 25V but still below it (the ~15–19V figure earlier attributed to VPE was actually VPP / 18.7V fw `firestarter vpp`). The operator authorized graduating the 4 NMOS chips anyway, with **no hardware change ever** (D-07 supersedes D-05/D-06). The chips now **resolve and attempt a write** on the existing 0x0B / direct-VPE firmware path, where `eprom_check_vpp` **warns-and-proceeds on under-voltage** (over-voltage stays blocked as the damage boundary). At ~22.4V the write is best-effort — it may or may not fully verify, and an under-driven write cannot damage the chip; the user opts in. Plan 79-03 is therefore informational best-effort bench validation: chips stay `supported` even if a write does not SHA-match. The original plan GATE (which required a CLEARED ≥25V verdict) was explicitly overridden — this is the sole reason this plan ran below the ≥25V bar.

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-06-23
- **Tasks:** 3
- **Files modified:** 9 (3 source/DB, 5 test, 1 requirements) across the firestarter_app submodule + meta-repo

## Accomplishments

- `RURP_VPP_CEILING_MV` 22000→25000 (build_db.py) and `_FAMILY_VPP_INVARIANTS["configure_eprom"]` (0,22000)→(0,25000) (check_dispatch.py) raised in the **same commit**.
- DB regenerated: the 4 NMOS chips graduate to `support_status=supported`, `programming.algorithm=11` (0x0B EPROM_LEGACY), `vpp_mv=25000`, no `unsupported_reason`. The host guard in `chip_resolver.resolve_chip` self-cleared from the regenerated DB (no guard edit).
- **Zero** `vpp-exceeds-max` chips remain in the packaged DB; M2732A (21V) standalone entries untouched at `vpp_mv=21000 / supported`.
- `check_dispatch.py` exits 0 (744 scanned / 734 supported / 10 non-dispatchable / 0 violations). FUT-02 preserved: the strict-greater compare keeps any future >25V chip fail-closed (proven by a new negative-control test).
- 7 vpp-exceeds-max-exemplar tests re-anchored to X88C64P / AT28C04; 3 new non-vacuous tests added; full suite green (cov 77.79%); ruff clean at py39.
- REQUIREMENTS.md FUT-03 corrected from the PCB-feedback-resistor framing to the D-07 manual-potentiometer + best-effort framing.

## Task Commits

Submodule (`firestarter_app` @ `v1.14-feasible-gap-implementation`):

1. **Task 1: Raise the ceiling (both constants) + DB regen + safety gate** — `1498786` (feat)
2. **Task 2: Update vpp-exceeds-max-exemplar tests + add non-vacuous positive tests** — `26cc62d` (test)

Meta-repo (`/workspaces` @ `gsd/v1.14-feasible-gap-implementation`):

3. **Task 3: Correct REQUIREMENTS.md FUT-03 root-cause text** — committed with plan metadata below.

**Plan metadata commit (meta-repo):** see final docs commit (SUMMARY + REQUIREMENTS + STATE + ROADMAP).

_Note: the firestarter_app gitlink is intentionally NOT bumped in the meta-repo (stays pinned until the operator's beta cut). `git status` showing firestarter_app as "modified (new commits)" is the expected, correct state._

## Files Created/Modified

- `firestarter_app/tools/build_db.py` — `RURP_VPP_CEILING_MV = 25000`
- `firestarter_app/tools/check_dispatch.py` — `configure_eprom` invariant `(0, 25000)` with Phase-79 comment
- `firestarter_app/firestarter/data/chip_database.json` — regenerated (4 NMOS chips graduated)
- `firestarter_app/tests/test_build_db_inclusion.py` — `test_nmos_vpp_exceeds_max`→`test_nmos_graduated_to_supported`; new `test_zero_vpp_exceeds_max_chips_remain`; reason test re-anchored to a synthetic >25V invariant
- `firestarter_app/tests/test_chip_resolver.py` — M2716 refusal tests re-anchored to X88C64P; new positive `test_resolve_chip_nmos_graduated_resolves`
- `firestarter_app/tests/test_cli_handlers.py` — 3 M2716 vpp-exceeds-max exemplars re-anchored to AT28C04; `test_info_vpp_exceeds_max_no_crash`→`test_info_nmos_25v_no_crash`
- `firestarter_app/tests/test_check_dispatch_invariants.py` — new `test_configure_eprom_with_25v_vpp_is_not_a_violation` (positive control) + `test_configure_eprom_above_25v_is_a_violation` (FUT-02 negative control); updated the 12000 test's comment to "25000"
- `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` — regenerated (4 chips 0x00→0x0B)
- `.planning/REQUIREMENTS.md` — FUT-03 corrected
- `.planning/phases/79-25v-nmos-ceiling-raise/deferred-items.md` — logged pre-existing ruff debt (out of scope)

## Decisions Made

- Proceeded under the CONTEXT D-07 operator override despite the 79-01 NOT-CLEARED gate (best-effort graduation, no hardware change ever). The plan's amended GATE clause and D-07 authorize this; 79-01-SUMMARY.md still records NOT CLEARED, which is expected.
- Re-anchored the now-empty `vpp-exceeds-max` test category to X88C64P (protocol-not-implemented) and AT28C04 (adapter-required) — distinct from the already-existing X88C64P/AT28C16 sibling tests to avoid exact duplicates.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Regenerated tests/golden/v1.3-COVERAGE-MATRIX.md golden fixture**
- **Found during:** Task 2 (full-suite run)
- **Issue:** `tests/test_audit_coverage_matrix.py::test_golden_file_matches` is a byte-identity gate against a golden coverage matrix derived from chip_database.json. Task 1's DB regen legitimately changed the matrix (4 chips moved algorithm 0x00→0x0B; the 0x00 row dropped to 0, the 0x0B row rose 26→30). The test explicitly says: "if this is a legitimate change, regenerate the golden file alongside the matrix commit."
- **Fix:** Regenerated `tests/golden/v1.3-COVERAGE-MATRIX.md` via `generate_matrix(output=golden, ledger_path=/workspaces/.planning/v1.3-defect-coverage-ids.json)` (the same ledger the test seeds from), producing a byte-identical fixture. Verified the only diff is the 4 NMOS chips' 0x00→0x0B move — no other drift. The meta-repo ledger was NOT modified.
- **Files modified:** firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md
- **Verification:** `pytest tests/test_audit_coverage_matrix.py` green; full suite green.
- **Committed in:** `26cc62d` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking).
**Impact on plan:** The golden regeneration is a sanctioned, expected downstream effect of the DB graduation — not scope creep. No code behavior changed beyond the planned ceiling raise.

## Issues Encountered

- Pre-existing ruff errors/format issues in 4 unrelated firestarter_app files (`tools/catalog/codegen.py`, `tools/catalog/codegen_vectors.py`, `.github/scripts/update_version.py`, `tools/check_mypy_watermark.py`). Confirmed pre-existing by stashing the 79-02 changes — present on the clean tree at HEAD, NOT introduced here. The files I edited are all ruff-clean + format-clean at `--target-version py39`. Logged in `deferred-items.md`; out of scope per the SCOPE BOUNDARY rule.

## Known Stubs

None — no placeholder/empty-value stubs introduced. The graduation is data-driven (DB regen) and the chips resolve to real wire dicts (vpp_mv=25000, algorithm=11). The "best-effort" nature is a firmware-rail property (under-voltage warn-and-proceed), not a code stub.

## Threat Model Disposition

- **T-79-CEIL** (over-broad graduation): mitigated — strict-greater compare keeps >25V fail-closed (new negative-control test `test_configure_eprom_above_25v_is_a_violation`); diff confirmed ONLY the 4 intended entries changed; M2732A untouched.
- **T-79-GATE** (stale/desynced invariant): mitigated — both constants raised in the same commit; check_dispatch.py run AFTER regen exits 0 / 0 violations.
- **T-79-HANDEDIT** (hand-edited DB/guard): mitigated — graduation driven only by `python3 tools/build_db.py`; host guard self-cleared; no hand-edit of support_status or the guard.
- **T-79-VACUOUS** (false test confidence): mitigated — `test_zero_vpp_exceeds_max_chips_remain`, `test_resolve_chip_nmos_graduated_resolves`, and `test_configure_eprom_with_25v_vpp_is_not_a_violation` all fail on the pre-edit state; not re-asserts of the 12000 fixture.
- **T-79-SC** (supply-chain): accept — no new packages installed.

## Next Phase Readiness

- NMOS-02 complete: ceiling raised, DB regenerated, 4 NMOS chips supported at vpp_mv=25000 / 0x0B, zero vpp-exceeds-max chips, M2732A untouched, FUT-02 preserved, suite green, FUT-03 corrected.
- 79-03 is now informational best-effort bench validation (per D-07): chips stay `supported` regardless of bench SHA-match. Resume when an NMOS chip is on hand on Leonardo; no revert on a failed bench write.
- The firestarter_app gitlink stays pinned until the operator's beta cut.

## Self-Check: PASSED

- Files verified present: 79-02-SUMMARY.md, deferred-items.md, build_db.py, check_dispatch.py, chip_database.json.
- Submodule commits verified present: `1498786` (Task 1), `26cc62d` (Task 2).

---
*Phase: 79-25v-nmos-ceiling-raise*
*Completed: 2026-06-23*
