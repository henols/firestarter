---
phase: 81-2516-db-entry-non-destructive-read-sweep
plan: "02"
subsystem: user-database-override
tags: [2516, user-override, grad-01, grad-02, safety-review, evidence-scaffold, uv-eprom]
dependency_graph:
  requires: []
  provides: [2516-DB-ENTRY, 2516-SAFETY-SIGNOFF, EVIDENCE-SCAFFOLD, GRAD-01-FINDINGS]
  affects: [Plan-81-03-sweep, Phase-83-2516-write]
tech_stack:
  added: []
  patterns: [name-keyed-user-override-add-new, SR-1-safety-review, v1.13-matrix-extension]
key_files:
  created:
    - .planning/phases/81-2516-db-entry-non-destructive-read-sweep/81-2516-SAFETY-REVIEW.md
    - .planning/v1.15/bench/EVIDENCE.json
    - .planning/v1.15/bench/EVIDENCE.md
  modified:
    - ~/.firestarter/database.json (home dir — not under git)
decisions:
  - "GRAD-01: 2516 confirmed ABSENT from minipro infoic.xml — all 28 '2516' hits are 25160 SPI serial parts; hand-authored user-override required"
  - "GRAD-02: 2516 user-override authored via name-keyed add-new path under INTEL key (algorithm 0x0B, DIP24_2716, UV-EPROM, vpp_mv 25000, 2048 bytes, support_status supported); FLAG_CAN_ERASE NOT set (UV)"
  - "D-01 human gate: operator (Henrik) personally signed off on 81-2516-SAFETY-REVIEW.md 2026-06-23 — the sole compensating control for the bypassed check_dispatch.py/diff_db.py"
  - "EVID-01/02: EVIDENCE.{md,json} scaffolded extending the v1.13 matrix shape (harness_version=81, 11 pending chip rows, locked columns)"
metrics:
  completed: "2026-06-23"
  tasks_completed: 3
  files_modified: 4
---

# Phase 81 Plan 02: 2516 User-Override DB Entry + Safety Review + EVIDENCE Scaffold

**One-liner:** Hand-authored the irreplaceable Intel 2516 user-override DB entry (absent from minipro), captured a full SR-1 safety review verifying all 6 D-02 values against the TMS2516 datasheet, obtained the operator's blocking-human sign-off, and scaffolded the milestone EVIDENCE record with 11 pending chip rows.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Research 2516 (GRAD-01) + author user-override DB entry (GRAD-02) | `e6e9870` (folded into T2 commit; ~/.firestarter/database.json is home-dir, not git-tracked) | `~/.firestarter/database.json` |
| 2 | Author 81-2516-SAFETY-REVIEW.md + scaffold EVIDENCE.{md,json} (D-01/D-02, EVID-01/02) | `e6e9870` | `81-2516-SAFETY-REVIEW.md`, `.planning/v1.15/bench/EVIDENCE.{json,md}` |
| 3 | Operator personally signs off on the 2516 safety review (D-01 human gate, GRAD-02) | `<this commit>` | `81-2516-SAFETY-REVIEW.md` (sign-off line) |

## GRAD-01 Research Findings

- **The 2516 is ABSENT from minipro `infoic.xml`.** All 28 hits for "2516" are `25160` SPI serial EEPROM parts (e.g. AT25160) — NOT the parallel UV-EPROM. This confirms the 2516 must be a hand-authored user-override that bypasses `build_db.py` / `check_dispatch.py` / `diff_db.py`.
- **Datasheet class:** Intel/TI 2516 (TMS2516) — 24-pin NMOS UV-erasable PROM, 2K×8 = 2048 bytes, ~25V VPP, DIP24, 2716 read-compatible (VPP held at VCC=5V for read).

## GRAD-02: User-Override Entry

Authored under the `INTEL` manufacturer key using a `name: "2516"` key (with `part_number: "2516"`), routing through `EpromDatabase._merge_databases` add-new-item path (database.py:244–246). Values:

| Field | Value |
|-------|-------|
| algorithm | 11 (0x0B → `configure_eprom`) |
| pinout | DIP24_2716 (VPP=pin 21) |
| electrical.type | UV-EPROM |
| vpp_mv | 25000 (at the RURP_VPP_CEILING_MV ceiling, not over) |
| size_bytes | 2048 |
| support_status | supported |

**Live `firestarter info 2516` decode:** 0x0B / DIP24_2716 (VPP pin 21) / UV-EPROM / VPP 25.0V / 0x800 (2048) / "Can be erased: no". `convert_to_programmer` flags = `0x00` → **FLAG_CAN_ERASE NOT set** (correct for UV-EPROM, D-02 step 3).

## D-01 Human Gate — Operator Sign-off

The 2516 bypasses all automated DB safety gates, so the manual SR-1 review + operator sign-off is the SOLE compensating control before Phase 83 writes this irreplaceable chip.

**Operator sign-off: [x] Approved — Henrik / 2026-06-23.**

All 6 D-02 values verified PASS against the TMS2516 datasheet (the highest-risk field, VPP, confirmed at 25000 not 12000 — Pitfall 8; VPP routes to pin 21). Overall SR-1 result: **PASS**.

## EVID-01/02: EVIDENCE Scaffold

`.planning/v1.15/bench/EVIDENCE.{json,md}` created extending the v1.13 validation-matrix shape:
- `harness_version = "81"`, 11 chip cells seeded `verdict: "pending"`.
- Locked columns present per cell: chip, family, board, shield, blank_state, op, sha256, verdict, anomalies (+ EVID-extension fields read_count, blank_check_result).
- 11 chips: W27C512, W27E512, SST27SF512, W27E040, SST39SF040, W29C020, W29C040, FM1608, ST M27C512, AM27C020, 2516.
- No new dependency / harness (EVID-02): reuses the existing matrix shape and `firestarter` CLI.

This scaffold is the structure Plan 81-03's bench sweep populates.

## Deviations from Plan

- Task 1's deliverable (`~/.firestarter/database.json`) is a home-directory file outside any git repo, so it carries no commit of its own; per orchestrator guidance the atomic commit `e6e9870` covers Task 2's tracked `.planning/` artifacts. The override file itself was authored and verified live.

## Threat Surface Scan

The 2516 override bypasses `check_dispatch.py`/`diff_db.py` (T-81-04). Mitigation in place: the SR-1 review + blocking operator sign-off (D-01). Highest-risk field `vpp_mv` verified = 25000 (T-81-03). No package installs (T-81-SC accepted).

## Known Stubs

The 11 EVIDENCE chip rows are intentionally `pending` — populated by Plan 81-03's bench sweep.

## Self-Check: PASSED

- `~/.firestarter/database.json` 2516 entry merged via name-keyed path, decodes 0x0B/DIP24_2716/UV-EPROM/25000/2048: CONFIRMED (live `firestarter info 2516`)
- FLAG_CAN_ERASE NOT set on 2516 (flags 0x00): CONFIRMED
- `81-2516-SAFETY-REVIEW.md` exists with 6 D-02 items PASS, vpp-pin 21 line, info transcript, operator sign-off filled: CONFIRMED
- `EVIDENCE.json` harness_version=81, 11 cells, locked columns: CONFIRMED
- Operator (Henrik) sign-off recorded 2026-06-23: CONFIRMED
