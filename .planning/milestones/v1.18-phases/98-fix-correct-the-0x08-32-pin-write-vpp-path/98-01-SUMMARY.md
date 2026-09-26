---
phase: 98-fix-correct-the-0x08-32-pin-write-vpp-path
plan: 01
subsystem: database
tags: [pinout, chip-database, build_db, diff_db, DIP32, 0x08, AM27C020, RC-1, FIX-03]

requires:
  - phase: 97-pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program
    provides: "RC-1 root cause verdict: pin 31 modeled as address line A18 in DIP32_STD for all 0x08/32-pin chips; for ≤256K chips pin 31 is PGM (active-LOW), not A18"

provides:
  - "DIP32_27C020 scoped pinout in pinouts.json — pin 31 OFF the address bus (A18/line 22), VPP on pin 1, no static-high-pins (Q1 RESOLVED)"
  - "size-keyed resolve_pinout_key arm in build_db.py: proto_id==0x08 && mem_size<=262144 → DIP32_27C020"
  - "Regenerated chip_database.json: 88 chips (≤256K, proto 0x08, 32-pin) reassigned to DIP32_27C020"
  - "Updated chip_database.baseline.json with RC1_DIP32_27C020 cited rule; diff_db.py gate green"
  - "SAFE-02 host CI gate green (ruff check firestarter/+tests/, format, mypy, check_dispatch, diff_db)"
  - "Upstream contract for Plan 02: bus-config shape with pin 31 NOT an address line, ready for firmware PGM-assert"

affects:
  - 98-02-PLAN firmware PGM-assert branch
  - 99-bench-and-ledger
  - any future plan modifying the 0x08 32-pin dispatch path

tech-stack:
  added: []
  patterns:
    - "DIP32_27C020 scoped pinout variant — same structural model as DIP32_SST39SF040 precedent"
    - "size-keyed resolve_pinout_key arm: proto+size gate for class-scoped pinout assignment"
    - "RC1_DIP32_27C020 cited rule in diff_db.py — new rationale class for RC-1 pinout fix"

key-files:
  created: []
  modified:
    - "firestarter_app/firestarter/data/pinouts.json — DIP32_27C020 entry added"
    - "firestarter_app/tools/build_db.py — size-keyed arm in resolve_pinout_key; ruff format applied"
    - "firestarter_app/firestarter/data/chip_database.json — 88 chips reassigned via regen"
    - "firestarter_app/tools/baseline/chip_database.baseline.json — re-baselined with DIP32_27C020 (88 chips)"
    - "firestarter_app/tools/diff_db.py — RC1_DIP32_27C020 rationale + rule + classify_diff arm added"

key-decisions:
  - "Q1 RESOLVED (2026-06-30): static-high-pins RULED OUT as PGM vehicle — static_high_mask ORs HIGH into line 22 (CONTROL bit 6) with no inversion in RURP latch path; PGM program-active is VIL (LOW). DIP32_27C020 only takes pin 31 OFF the address bus; PGM=VIL assert is Plan 02's firmware branch"
  - "D-04 host-side alias guard: size gate (mem_size<=262144) structurally excludes 512K AM27C040 and 1M AM27C080 from DIP32_27C020; they stay DIP32_STD"
  - "Blast radius accepted as 88 chips (entire ≤256K 0x08 32-pin class, not just AMD); architectural correctness is class-wide (A18 = bit 18 = mask 0x40000 is unused at ≤256K)"
  - "LOW-7: re-baselined chip_database.baseline.json git diff is THE audited artifact; diff_db green by construction once baseline updated in same commit"
  - "py3.11 sign-off CI-PENDING: no python3.11 in devcontainer (3.12.13 used); ruff check + format gates scoped to firestarter/+tests/ per ci.yml (not tools/) — CI gate is structurally green"

requirements-completed: [FIX-03, SAFE-02]

duration: 45min
completed: 2026-06-30
---

# Phase 98 Plan 01: Add DIP32_27C020 Scoped Pinout + Size-Keyed DB Assignment + SAFE-02 Gate Summary

**DIP32_27C020 scoped pinout (pin 31 off address bus) assigned to 88 ≤256K 0x08/32-pin chips via size-keyed build_db.py arm; diff_db PASS; host CI gate green (ruff+mypy+check_dispatch); upstream bus-config contract for Plan 02 firmware PGM-assert delivered**

## HIGH-1 HEADLINE (verbatim — dominant expected outcome, NOT a footnote)

**Under RC-1, the addr-0 register state is byte-unchanged by this host-pinout change — pin 31 is already at VIL at addr 0 (A18=0), so taking it off the address bus does not alter the addr-0 signal. If Phase 99 still shows 0 bits at addr 0, that is CONSISTENT WITH the analysis, not a new bug. This plan delivers the architecturally-correct pinout (pin 31 not an address line); it is NOT claimed to flip bits on silicon — Phase 99 is the sole empirical gate.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-06-30T14:15:00Z
- **Completed:** 2026-06-30T15:00:00Z
- **Tasks:** 3
- **Files modified:** 5 (in firestarter_app submodule)

## Q1 RESOLVED — Polarity (load-bearing for this plan)

Static-high-pins is RULED OUT as the PGM vehicle. Evidence chain (verified against live firmware):
- `static_high_mask` ORs a `1` (HIGH) into `reorg_address` at `memory.cpp:402` (set-only, never clears)
- Bit 22 of `reorg_address` → CONTROL register bit 6 via `mem_util_calculate_top_address_register` (`memory.cpp:184-185`)
- `rurp_write_to_register(CONTROL_REGISTER, ...)` → `rurp_internal_write_to_register` (`rurp_register_utils.h:63-89`) → `rurp_write_data_buffer(data)` maps each bit straight to a port pin with NO inversion (`leonardo_rurp_shield.cpp:80-99`)
- A `1` bit = physical HIGH at pin 31; AM27C020.pdf: PGM program-active = VIL (LOW)

**Conclusion:** `static-high-pins:[31]` drives pin 31 HIGH, not the PGM=VIL program-active level needed. This plan's only job for pin 31 is "take it off the address bus." The program-active PGM=VIL hold-LOW is Plan 02's firmware branch.

## Accomplishments

1. **DIP32_27C020 pinout added** (`pinouts.json`): pin 31 removed from `address-bus-pins` (no longer drives bus line 22/A18); `vpp-pin:[1]` retained per AM27C020.pdf; no `static-high-pins` entry (Q1 ruled it out); verbose comment cites AM27C020.pdf, ≤256K scope (D-02/D-04), Q1 polarity verdict, and Plan 02 PGM-assert handoff. `DIP32_STD` and `DIP32_SST39SF040` byte-unchanged.

2. **Size-keyed resolve_pinout_key arm** (`build_db.py`): `proto_id == 0x08 and mem_size <= 262144` → `DIP32_27C020`; all other 0x08/32-pin chips (512K AM27C040, 1M AM27C080) stay `DIP32_STD`. Inline comment cites D-02/D-04 and Assumption A4 (`mem_size <= 262144` ⟺ A18 = bit 18 = mask `0x40000` unused). DB regenerated via `build_db.py` (never hand-edited per CLAUDE.md). Re-baseline with `RC1_DIP32_27C020` cited rule added to `diff_db.py`.

3. **SAFE-02 host CI gate**: `ruff check firestarter/ tests/` PASS; `ruff format --check firestarter/ tests/` PASS (77 files); mypy watermark: 1 error / 35 watermark; `check_dispatch.py` PASS (0 VPP violations, 746 chips scanned); `diff_db.py` PASS.

## Task Commits

1. **Task 1: DIP32_27C020 scoped pinout** — `38b55d5` (feat)
2. **Task 2: size-keyed arm + DB regen + re-baseline** — `362bfa0` (feat)
3. **Task 3: SAFE-02 gate (ruff format)** — `27da013` (chore)

## MED-4a: Blast Radius — DIP32_27C020 Reassigned Chips (88 total)

**Exact count: 88 chips. Upper-bound assertion: ≤100 (verified in Task 2 verify step).**

All 88 chips have `electrical.size_bytes <= 262144` (size gate confirmed). No 512K/1M chip changed pinout.

**Size distribution:**
- 64K (65536): 1 chip — `SST37VF512`
- 128K (131072): 52 chips (27C010-class)
- 256K (262144): 36 chips (27C020-class, including AM27C020)

**Per-chip pin-31-role note:**
- **AMD AM27C020, AMD AM27LV020/B** — confirmed PGM per AM27C020.pdf (this is the target chip)
- **All 27C010-class (128K) and 27C020-class (256K) chips** — unverified-but-structurally-safe: A18 = bit 18 = mask 0x40000 is never an active address line at ≤256K (confirmed by Assumption A4); pin 31 is never a real A18 line at this size. The size gate makes this safe regardless of individual datasheet verification status.
- **SST37VF512 (64K, proto 0x08)** — unverified-but-structurally-safe by the same A4 argument. Note: SST37SF/VF family names suggest flash-style devices, but they are on proto 0x08 (EPROM_QUICK) in the DB. Pin 31 is never A18 at 64K.

**Full reassigned part-number list:**
`27C010`, `27C010,27C010A`, `27C020`, `27CX010` (×3), `A27020`, `AM27C010`, `AM27C020`, `AM27H010,AM27HB010`, `AM27LV010`, `AM27LV020,AM27LV020B`, `AT27BV010,AT27LV010,AT27LV010A`, `AT27BV020,AT27LV020,AT27LV020A`, `AT27C010,AT27C010L`, `AT27C020`, `CAT27010`, `CY27C010,CY27H010`, `CY27C020`, `DPV27C101`, `EN27C010`, `FM27C010`, `HN27C101AG,HN27C101AP,HN27C101AFP,HN27C101ATT,HN27C101G,HN27C101P`, `HN27C301AG,HN27C301AP,HN27C301AFP`, `HN27C301G`, `HT27C010`, `HT27C020`, `HT27LC010`, `HT27LC020`, `ICE27C010,ICE27LC010`, `ICE27C020,ICE27LC020`, `IS27C010,IS27HC010`, `IS27C020,IS27HC020`, `IS27LV010`, `IS27LV020`, `LG28C010`, `LG28C020`, `M23C1001`, `M23C2001`, `M27C1000`, `M27C1001,M27V101` (×2), `M27C2001,M27V201,M27W201` (×2), `M5M27C101K`, `M8720`, `MBM27C1000P,MBM27C1000`, `MBM27C1001`, `MBM27C2000P,MBM27C2000`, `MBM27C2001`, `MSM27C1000`, `MSM27C2000`, `MSM27C201`, `MX26C1000`, `MX26C2000`, `MX27C1000`, `MX27C1000A`, `MX27C2000`, `MX27C2000A`, `MX27L1000`, `MX27L2000`, `NM27C010` (×2), `NM27C020` (×2), `NM27LC010,NM27P010,NMC27C010`, `NM27LV010`, `NM27LV020`, `NM27P020`, `PT28C010`, `PT28C020`, `SMJ27C010A`, `SST27SF010`, `SST27SF020`, `SST27VF010`, `SST27VF020`, `SST37VF010`, `SST37VF020`, `SST37VF512`, `TMS27C010`, `TMS27C010A,TMS27PC010A`, `TMS27C020,TMS27PC020`, `UPD27C1001A`, `UPD27C2001`, `W27C01,W27C010,W27E01,W27E010,W27L01,W27L010`, `W27C02,W27C020,W27E02,W27E020,W27L02`, `WS27C010F`, `WS27C010L`

## LOW-7: Baseline as Audited Artifact

The re-baselined `chip_database.baseline.json` git diff (in commit `362bfa0`) is THE audited review artifact. `diff_db.py` is green by construction once the baseline is updated in the same commit that introduces the DB change. The baseline diff shows exactly 88 chips changing from `"pinout": "DIP32_STD"` to `"pinout": "DIP32_27C020"` — this is the reviewable scoping evidence, not the diff_db exit code.

## D-04 Host-Side Guard Verification

- AM27C040 (524288 bytes, 512K) — pinout: DIP32_STD (UNCHANGED)
- AM27C080 (1048576 bytes, 1M) — pinout: DIP32_STD (UNCHANGED)
- Zero 512K/1M chips appear in the reassigned list

## Files Created/Modified

- `firestarter_app/firestarter/data/pinouts.json` — DIP32_27C020 entry added (10 new lines)
- `firestarter_app/tools/build_db.py` — size-keyed arm in resolve_pinout_key; ruff format applied
- `firestarter_app/firestarter/data/chip_database.json` — 88 chips reassigned via regen (never hand-edited)
- `firestarter_app/tools/baseline/chip_database.baseline.json` — re-baselined (88 chips updated to DIP32_27C020)
- `firestarter_app/tools/diff_db.py` — RC1_DIP32_27C020 rationale + _RULE_FIELD_PATHS + _classify_diff arm

## SAFE-02 Gate Details

- `ruff check firestarter/ tests/`: PASS (CI scope per ci.yml)
- `ruff format --check firestarter/ tests/`: PASS (77 files)
- `ruff check tools/build_db.py tools/diff_db.py`: PASS (modified files)
- `python tools/check_mypy_watermark.py`: 1 error / 35 watermark — OK
- `python tools/check_dispatch.py`: PASS (746 chips, 0 VPP violations, 0 dispatch regressions)
- `python tools/diff_db.py`: PASS (2 pre-existing PGSZ_PAGE_SIZE changes; 0 unexplained)
- **Pre-existing ruff I001 errors** in `tools/audit_coverage_matrix.py` and `tools/catalog/codegen*.py` — these are NOT in CI scope (`ci.yml` runs `ruff check firestarter/ tests/` only). Not caused by this plan's changes; deferred per scope boundary rule.
- **Python interpreter: 3.12.13** (`/usr/local/bin/python3`). **py3.11 sign-off: CI-PENDING** — no python3.11 binary in devcontainer. CI gate structurally green since `ruff check firestarter/ tests/` + mypy run cleanly under 3.12 with no f-string backslash or syntax differences in the modified files (pure config/JSON/tool changes, no new f-strings).

## Decisions Made

- Q1 RESOLVED: static-high-pins RULED OUT (static_high_mask drives HIGH; PGM=VIL); PGM-assert deferred to Plan 02 firmware branch
- D-03 honored: no new wire field needed (Q2 RESOLVED — existing protocol/pins/mem_size/bus_config fields suffice for Plan 02's firmware gate)
- Blast radius accepted as 88 (entire ≤256K class); not narrowed to AMD only — architectural correctness is class-wide

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] diff_db.py SRAM_PINOUT rule misclassified the 88 pinout changes**
- **Found during:** Task 2 (re-baselining)
- **Issue:** The existing SRAM_PINOUT rule matched all 88 `pinout` changes (since it triggers on any `pinout_diff && !algo_diff && !timing_diff`), attributing them to the Phase-58 SRAM re-derivation — the wrong cited rule and wrong rationale.
- **Fix:** Added `RC1_DIP32_27C020` rule to `_RATIONALES`, `_RULE_FIELD_PATHS`, and `_classify_diff` (before SRAM_PINOUT, scoped by `cu_chip.get("pinout") == "DIP32_27C020"`); updated priority-order comment. diff_db now correctly attributes the 88 chips to Phase 98 RC-1 fix.
- **Files modified:** `tools/diff_db.py`
- **Committed in:** `362bfa0` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — diff_db misclassification)
**Impact on plan:** Fix necessary for correct audit attribution. No scope creep.

## Issues Encountered

- `ruff check .` (dot-scope) shows 4 pre-existing I001/UP031 errors in `tools/` files not touched by this plan. CI scope is `firestarter/ tests/` per `ci.yml` — CI gate is green. Pre-existing errors deferred per scope boundary.

## Next Phase Readiness

- **Plan 02 (firmware PGM-assert)**: bus-config contract delivered — pin 31 is NO LONGER an address line in the wire bus-config for 0x08 ≤256K chips. The firmware branch can now gate on `handle->protocol == 0x08 && handle->pins == 32 && handle->mem_size <= 262144` and deliberately drive pin 31's bus line to PGM=VIL (hold LOW) across the CE pulse.
- **Plan 02 must** use the size gate (`mem_size <= 262144`) for D-04 alias safety — `CTRL_VPP_P1_ENABLE_REV2 == CTRL_ADDRESS_LINE_18_REV2 == 0x08` on Rev 2.0 (`rurp_pinout.h:121,127`); driving this bit on a 512K AM27C040 corrupts A18.
- **Phase 99 (bench)**: this plan does not claim to flip bits on silicon. Phase 99 is the sole empirical gate.

## Self-Check: PASSED

- firestarter_app/firestarter/data/pinouts.json: FOUND
- firestarter_app/tools/build_db.py: FOUND
- firestarter_app/firestarter/data/chip_database.json: FOUND
- firestarter_app/tools/baseline/chip_database.baseline.json: FOUND
- firestarter_app/tools/diff_db.py: FOUND
- .planning/phases/98-fix.../98-01-SUMMARY.md: FOUND
- Commit 38b55d5 (Task 1 — DIP32_27C020 pinout): FOUND
- Commit 362bfa0 (Task 2 — size-keyed arm + regen + re-baseline): FOUND
- Commit 27da013 (Task 3 — ruff format / SAFE-02 gate): FOUND

---

*Phase: 98-fix-correct-the-0x08-32-pin-write-vpp-path*
*Completed: 2026-06-30*
