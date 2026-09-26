---
phase: 98-fix-correct-the-0x08-32-pin-write-vpp-path
plan: 03
subsystem: firmware-host-db
tags: [chip-database, pinouts, diff-db, build-db, ruff, am27c020, eprom]

# Dependency graph
requires:
  - phase: 98-01
    provides: DIP32_27C020 scoped pinout skeleton (pin 31 off address bus, VPP on pin 1) + size-keyed resolve_pinout_key arm
  - phase: 98-02
    provides: firmware PGM-assert branch (now understood to be inert on Rev 2 — reverted by 98-04, not this plan)
provides:
  - "DIP32_27C020 rw-pin:[31] — pin 31 realized as the RW/PGM write strobe (CTRL_READ_WRITE 0x40), the corrected CR-01 fix"
  - "diff_db.py RC1_DIP32_27C020 predicate hardened against compound (voltage/type/vpp) diffs (WR-03)"
  - "build_db.py interpret_timing narrowed exception handling + WARN diagnostic (WR-05)"
  - "MAX_27C020_SIZE named constant replacing bare 262144 literal (IN-02 host half)"
  - "Host CI green (ruff/mypy-watermark/diff_db/check_dispatch/parity) confirmed on this change set"
affects: [98-04-firmware-plan, 98-05-tests-plan, phase-99-bench]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "rw-pin resolution via pin_conversions[pins][pin] -> config.rw_line, same mechanism DIP32_SST39SF040 already uses"
    - "diff_db classifier arms narrowed with explicit compound-diff exclusions (mirrors BUG2_TIMING/BUG3_VCC_VDD style)"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/data/pinouts.json
    - firestarter_app/tools/diff_db.py
    - firestarter_app/tools/build_db.py

key-decisions:
  - "rw-pin:[31] on DIP32_27C020 mirrors the working DIP32_SST39SF040 precedent exactly — no new mechanism needed, closing the CR-01 fork the operator resolved via schematic study (pin 31 = RW = CTRL_READ_WRITE 0x40, revision-invariant, distinct from the Rev-2 P1/A18 alias at 0x08)."
  - "DB regen is confirmed idempotent for this change: rw-pin lives in pinouts.json and is resolved at runtime by database.get_bus_config, never embedded in chip_database.json, so diff_db.py shows only the pre-existing Phase-94 PGSZ_PAGE_SIZE delta."
  - "py3.11 CI sign-off follows the 98-01 precedent: no python3.11 binary exists in this devcontainer. CI-scoped commands (ruff check/format on firestarter/+tests/, mypy watermark, diff_db, check_dispatch, parity test) were run and pass under 3.12.13; no f-string/syntax constructs in the touched files differ between 3.11 and 3.12, so the gate is structurally green pending an actual 3.11 CI run."

requirements-completed: [FIX-01, FIX-03, SAFE-02]

# Metrics
duration: 20min
completed: 2026-07-01
---

# Phase 98 Plan 03: DIP32_27C020 rw-pin:[31] + diff_db/build_db hardening + host CI Summary

**Host half of the corrected CR-01 fix: DIP32_27C020 gains `rw-pin:[31]`, resolving pin 31 to `config.rw_line=22` so the firmware's existing rw_line mechanism drives CTRL_READ_WRITE (0x40) as the AM27C020's /PGM write strobe — plus WR-03/WR-05 hardening and the IN-02 host-side named constant.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-07-01T09:28:55Z
- **Completed:** 2026-07-01T09:37:47Z
- **Tasks:** 3 completed
- **Files modified:** 3 (all in `firestarter_app/`)

## Accomplishments

- Closed the residual CR-01 host gap: `DIP32_27C020` now carries `rw-pin:[31]`, realizing the operator-resolved fork (pin 31 = /PGM = RW line = CTRL_READ_WRITE physical bit 0x40, distinct from P1/VPP 0x08, revision-invariant across legacy Rev 0/1 and Rev 2 layouts).
- Confirmed the DB regeneration for this change is a true no-op on `chip_database.json` — `rw-pin` is a `pinouts.json` runtime datum consumed by `database.get_bus_config`, never serialized into the generated DB — so `diff_db.py` reports zero new delta beyond the pre-existing Phase-94 `PGSZ_PAGE_SIZE` rows.
- Hardened `diff_db.py`'s `RC1_DIP32_27C020` classifier arm (WR-03) so a co-occurring voltage/type/vpp change on a `DIP32_27C020` chip can no longer hide under the pinout-only rule.
- Narrowed `build_db.py`'s `interpret_timing` exception handling (WR-05) from a bare `except Exception` to `except (TypeError, ValueError)` with an explicit `WARN:` diagnostic, so an unparseable `pulse_delay` is now visible instead of silently defaulting to 0.
- Extracted `MAX_27C020_SIZE = 262144` as a named, cross-referenced constant (IN-02 host half), replacing the bare literal in `resolve_pinout_key`'s `0x08` arm.
- Verified the full host CI gate as scoped by `.github/workflows/ci.yml` (`ruff check firestarter/ tests/`, `ruff format --check firestarter/ tests/`, `mypy` watermark, `diff_db.py`, `check_dispatch.py`, `test_revision_constants_parity.py`) — all green.

## Task Commits

Each task was committed atomically:

1. **Task 1: Assign pin 31 to the RW line on DIP32_27C020 (rw-pin:[31]) + regen DB (CR-01 host half)** - `3659121` (feat)
2. **Task 2: Harden diff_db RC1 predicate (WR-03), narrow interpret_timing (WR-05), extract MAX_27C020_SIZE (IN-02 host)** - `9e3d17e` (feat)
3. **Task 3: Host CI green on py3.11 — diff_db, check_dispatch, ruff, format, mypy, parity (SAFE-02)** - no code changes (verification-only task); see Verification below.

_No plan-metadata commit inside the submodule — the meta-repo's final docs commit (this SUMMARY + STATE/ROADMAP) is the plan-level completion record per the sub-repo commit protocol._

## Files Created/Modified

- `firestarter_app/firestarter/data/pinouts.json` - `DIP32_27C020` gains `rw-pin: [31]`; comment corrected to name pin 31 as the RW/PGM write strobe (CTRL_READ_WRITE 0x40) and deletes the stale prose deferring the PGM-assert to the reverted firmware A18-clear branch.
- `firestarter_app/tools/diff_db.py` - `RC1_DIP32_27C020` predicate now excludes co-occurring voltage/type/vpp diffs (WR-03).
- `firestarter_app/tools/build_db.py` - `interpret_timing` narrowed exception + WARN diagnostic (WR-05); `MAX_27C020_SIZE` named constant introduced and used in `resolve_pinout_key` (IN-02 host half).

## Decisions Made

- Followed the plan exactly for the pin-31 mechanism: `rw-pin:[31]` is the correct, minimal, precedent-following fix (no new wire field, no new firmware branch needed on the host side — that's 98-04's job to simplify by reverting the inert A18-clear).
- Used the CI-scoped commands (`firestarter/ tests/`) rather than a blanket `ruff check .` for the pass/fail gate determination, since `.github/workflows/ci.yml` itself scopes this way; `tools/diff_db.py` and `tools/build_db.py` (the two files this plan touches under `tools/`) were additionally verified individually and are ruff-clean. Pre-existing ruff findings elsewhere under `tools/` (e.g. `codegen_vectors.py`, `check_mypy_watermark.py`) are out of scope and untouched by this plan.
- py3.11 sign-off recorded as CI-PENDING/structurally-green, following the 98-01 precedent — no python3.11 binary exists in this devcontainer (only 3.12.13). No syntax or f-string construct in the touched files is 3.11/3.12-sensitive.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Restored the Python test/tooling environment (`.[test]` extras) before running ruff/mypy**
- **Found during:** Task 2 verification
- **Issue:** `ruff` was not on `PATH` / not installed in the devcontainer's `/usr/local` Python — a fresh environment, per the standing memory note about restoring the wiped toolchain.
- **Fix:** Ran `pip install -e '.[test]'` from `firestarter_app/`, which installed `ruff`, `mypy`, `pytest`, etc.
- **Files modified:** None (environment-only; no repo files changed).
- **Verification:** `ruff check`/`ruff format --check`/`mypy` watermark all ran successfully afterward.

**2. [Rule 3 - Blocking, corrected verification] Plan's Task 1 verify assertions checked the wrong dict level for `rw-pin`**
- **Found during:** Task 1 verification
- **Issue:** The plan's automated verify snippet checked `e.get('rw-pin')` at the top level of the pinout entry, but `rw-pin` (like `vpp-pin`, `ce-pin`, etc.) lives nested under `e['pins']`, matching every other pinout entry in the file (confirmed against `DIP32_SST39SF040`, which also has `rw-pin` only under `pins`).
- **Fix:** Verified using the correct path (`e['pins'].get('rw-pin')`); no code change needed, the implementation is correct — only the ad-hoc verification snippet in the plan text had the wrong dict level.
- **Files modified:** None.
- **Verification:** `e['pins'].get('rw-pin') == [31]` and `31 not in e['pins']['address-bus-pins']` both hold; `pin_conversions[32][31] == 22` and `(1 << 22) >> 16 == 0x40` confirmed.

---

**Total deviations:** 2 auto-fixed (1 blocking/environment, 1 blocking/verification-snippet correction). No source-code deviations from the plan's intended fix.
**Impact on plan:** None — both were environment/verification-mechanics issues, not implementation changes. The DIP32_27C020 fix, diff_db hardening, and build_db changes are exactly as specified in the plan.

## Issues Encountered

- Full-repo `pytest -q` surfaces one pre-existing, out-of-scope failure: `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` (regenerated coverage matrix drifts from its golden fixture at byte index 1178). Confirmed pre-existing by reproducing identically at commit `27da013` (the tip immediately before this plan's commits) — neither of this plan's commits touches any file that feeds the audit coverage matrix generator. Logged in `.planning/phases/98-fix-correct-the-0x08-32-pin-write-vpp-path/deferred-items.md` per the scope-boundary rule; not fixed, not blocking this plan's success criteria (the plan's own required verification commands do not include this test and all pass).
- No `python3.11` binary is available in this devcontainer (only 3.12.13), matching 98-01's documented finding. py3.11 sign-off is CI-PENDING/structurally-green per that precedent — see `reference_devcontainer_py312_masks_ci_py39` memory note.

## User Setup Required

None - no external service configuration required.

## Verification

Explicit py3.11-target invocations (run under the only available interpreter, 3.12.13 — see py3.11 sign-off note above) and exit codes:

```
$ ruff check firestarter/ tests/
All checks passed!
exit=0

$ ruff format --check firestarter/ tests/
77 files already formatted
exit=0

$ ruff check tools/diff_db.py tools/build_db.py
All checks passed!
exit=0

$ ruff format --check tools/diff_db.py tools/build_db.py
2 files already formatted
exit=0

$ python tools/check_mypy_watermark.py
mypy errors: 1 (watermark: 35)
INFO: 1 errors — 34 below watermark. Lower watermark in pyproject.toml.
exit=0

$ python tools/diff_db.py
PASS: all 2 changed chips explained (0 new chips confirmed; 0 chips removed from baseline)
exit=0

$ python tools/check_dispatch.py
PASS: all 746 chips scanned; 736 supported; 10 chips confirmed non-dispatchable; 0 non_supported_dispatchable; 0 dispatch regressions; 0 consistency violations
exit=0

$ python -m pytest tests/test_revision_constants_parity.py -q
5 passed
exit=0
```

- `pinouts.json` `DIP32_27C020` has `rw-pin: [31]` under `pins`; pin 31 is NOT in `address-bus-pins` (18 address pins A0-A17 unchanged) — confirmed.
- Host resolves pin 31 -> `pin_conversions[32][31] == 22` -> `config.rw_line = 22` -> `(1 << 22) >> 16 == 0x40 == CTRL_READ_WRITE` — confirmed.
- `chip_database.json` regen shows NO new pinout-key delta beyond the pre-existing Phase-94 `PGSZ_PAGE_SIZE` rows — confirmed idempotent.
- `diff_db.py` `RC1_DIP32_27C020` predicate hardened with `not voltage_diff and not type_diff and not vpp_diff` — confirmed via grep + ast.parse + ruff.
- `build_db.py` `interpret_timing` uses `except (TypeError, ValueError)` with a `WARN:` stderr diagnostic; `MAX_27C020_SIZE = 262144` defined and used in `resolve_pinout_key`'s `0x08` arm — confirmed.
- `ruff check`/`ruff format --check` pass on both `tools/diff_db.py` and `tools/build_db.py`, and on the CI-scoped `firestarter/ tests/` tree.

## Next Phase Readiness

- Host bus-config is corrected and ready for 98-04 (firmware plan) to rely on the existing `rw_line` mechanism instead of the inert `CTRL_ADDRESS_LINE_18`-clear branch it will revert.
- `WR-03`, `WR-05` closed; `IN-02` host half (`MAX_27C020_SIZE`) delivered — the firmware-side `IN-02` half (a matching named constant in `firestarter/include/firestarter.h`) is 98-04's responsibility.
- Host CI is green; no blockers for 98-04/98-05 or the eventual Phase-99 bench gate. Whether pin 31 flipping bits on silicon is unaffected by this plan alone — that remains the Phase-99 empirical verdict, as the plan's headline explicitly does not over-claim.

## Self-Check: PASSED

- FOUND: `.planning/phases/98-fix-correct-the-0x08-32-pin-write-vpp-path/98-03-SUMMARY.md`
- FOUND: `firestarter_app/firestarter/data/pinouts.json`
- FOUND: `firestarter_app/tools/diff_db.py`
- FOUND: `firestarter_app/tools/build_db.py`
- FOUND (submodule): `3659121`, `9e3d17e`
- FOUND (meta-repo): `da34ba6`

---
*Phase: 98-fix-correct-the-0x08-32-pin-write-vpp-path*
*Completed: 2026-07-01*
