---
phase: 162-chip-11-part-dev-test-sweep-on-the-reference-rig
plan: 01
subsystem: bench, rig-tooling
tags: [bench, rig-tooling, host-only, wave-0, rig-pins, provenance, desk-records, no-hardware]

requires:
  - phase: 161-wrv-baseline-position-a3-b2
    provides: "A3/B2's measured Leonardo write/read anchors and rig-pins.json's two-entry chips map"
provides:
  - "rig-pins.json chips map extended to all eleven inventory parts, single source of truth"
  - "capture_provenance.py accepting all eleven --chip tokens, derived choices, no drift possible"
  - "FM1608 vcc_mv:3300 resolved as decorative/display-only, root cause filed as backlog"
  - "The measured per-part derive_plan NA map (id/erase/blank-check) for all ten sweep tokens + 2516"
  - "Pre-phase WRV EVIDENCE.jsonl snapshot and CLOSE-04 before-count for later diffing"
affects: [162-02, 162-03, 162-04, 162-05, 162-06, 162-07, 162-08, 162-09, 162-10]

tech-stack:
  added: []
  patterns:
    - "argparse choices= derived from a JSON config file at import time, never a duplicated literal"

key-files:
  created:
    - .planning/v1.34/bench/cells/CHIP/CHIPS-MAP-DERIVATION.md
    - .planning/v1.34/bench/cells/CHIP/FM1608-VCC.md
    - .planning/v1.34/bench/cells/CHIP/DERIVE-PLAN.json
    - .planning/v1.34/bench/cells/CHIP/PRE-PHASE.md
  modified:
    - .planning/v1.34/rig-pins.json
    - .planning/v1.34/tools/capture_provenance.py

key-decisions:
  - "PD-4 (RESEARCH R7 option A): extend rig-pins.json's chips map and derive _CHIP_CHOICES from it, never read the app DB live inside a rig tool"
  - "PD-9: --no-image-plan's help text widened to cover the chip-sweep case (writes the chip, no pre-computed image)"
  - "FM1608's vcc_mv:3300 classified as a pre-existing build_db.py decode gap (not v1.33-caused, not Phase 165's), filed as backlog"

requirements-completed: []

coverage:
  - id: D1
    description: "rig-pins.json's chips map covers all eleven inventory parts, derived from the v1.33 arm's own DB by script, cross-checked against RESEARCH R7 with zero disagreement"
    requirement: "CHIP-01"
    verification:
      - kind: unit
        ref: "python3 -c assertion script over rig-pins.json chips map shape/values (see 162-01-PLAN.md Task 1 verify block)"
        status: pass
    human_judgment: false
  - id: D2
    description: "capture_provenance.py accepts all eleven --chip tokens via a pins-derived choices list; unknown tokens still refused at exit 2"
    requirement: "CHIP-01"
    verification:
      - kind: unit
        ref: "capture_provenance.py --selftest (14 legs incl. 2 new) + shell loop over all nine new --chip tokens"
        status: pass
    human_judgment: false
  - id: D3
    description: "Per-part derive_plan NA map measured and committed (DERIVE-PLAN.json) so an NA is never mis-booked as a divergence at the bench"
    requirement: "CHIP-03"
    verification:
      - kind: unit
        ref: "python3 -c assertion over DERIVE-PLAN.json (11 tokens present, write-partial on UV parts)"
        status: pass
    human_judgment: false
  - id: D4
    description: "run_gates.sh still green at 12/12 selftests + 5/5 live gates, exit 0, after a load-bearing tool edit"
    verification:
      - kind: integration
        ref: "bash .planning/v1.34/tools/run_gates.sh; RC=$? (read directly, never piped)"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-08-28
status: complete
---

# Phase 162 Plan 01: Wave 0 rig-tooling and desk records Summary

**`rig-pins.json`'s chips map extended to eleven parts and `capture_provenance.py`'s `--chip` gate derived from it, unblocking provenance capture for nine of ten sweep parts that argparse previously rejected at exit 2 before the pins file was ever read; four desk-provable answers (FM1608 VCC, the per-part NA map, the WRV pre-phase snapshot, and the CLOSE-04 issue count) committed before any part is seated.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-08-28T15:26:00Z (approx)
- **Completed:** 2026-08-28T16:11:26Z
- **Tasks:** 3/3 completed
- **Files modified:** 2 modified, 5 created

## Accomplishments

- `rig-pins.json`'s `chips` map extended from 2 to 11 entries, every value derived from the
  v1.33 arm's own `EpromDatabase` by a scratch script (never hand-typed), cross-checked against
  RESEARCH R7's independently-measured table with **zero disagreement**. The two frozen entries
  (`w27c512`, `w29c020`) kept every existing field byte-unchanged and gained only a `chip_token`.
- `capture_provenance.py`'s `_CHIP_CHOICES` is now `sorted(_load_pins_chips_or_die(_DEFAULT_PINS))`
  — a derivation over the pins file's own `chips` map, computed at import time, that fails loudly
  (never an empty-list fallback) on an unreadable/unparseable pins file. All nine new `--chip`
  tokens are now accepted by argparse; an unknown token is still refused at exit 2, by name.
- `--no-image-plan`'s help text widened (PD-9) to name the chip-sweep case explicitly: a position
  that *does* write the chip but has no pre-computed `IMAGE-PLAN.json` row to resolve.
- Two new `--selftest` legs added: a positive drift check (`set(_CHIP_CHOICES)` equals the pins
  file's `chips` key set, 11 members) and a negative named-refusal check (an unknown chip token is
  rejected and the rejection names the token).
- FM1608's `vcc_mv: 3300` resolved from source: the field is display-only, never reaches the wire
  dict, no VCC setter exists anywhere in firmware, and the value is byte-identical on both arms
  (never a v1.33 finding). Root cause: `build_db.py`'s `_PHASE84_RELABEL` (`:613`) sets FM1608's
  `_etype` to `"FRAM"` before the SRAM-class vcc→vdd correction (`:745`) can key on it, so the
  correction silently never fires for the one chip the relabel touches. Classified as a
  pre-existing decode gap, filed as a backlog item — not fixed here (`chip_database.json` is
  generated, never hand-edited).
- `derive_plan()` run against the v1.33 arm's own database/engine for all eleven tokens, persisted
  as `DERIVE-PLAN.json` — the authoritative per-part NA map every bench plan's divergence table
  keys on.
- Pre-phase `EVIDENCE.jsonl` snapshot and the CLOSE-04 "before" issue count captured as pasted
  command output, plus the A3/B2 Leonardo anchors, the ~2 hour machine-time budget, and PD-14's
  four stall ceilings with their arithmetic, all recorded in `PRE-PHASE.md`.
- `run_gates.sh` reconfirmed green after the tool edit: **12/12 selftests, 5/5 live gates, exit 0**
  (read directly, never through a pipe).

## Task Commits

1. **Task 1: Extend rig-pins.json's chips map to the eleven-part inventory, derived by script** - `0c04361b` (feat)
2. **Task 2: Derive capture_provenance.py's _CHIP_CHOICES from the pins map and widen --no-image-plan** - `a4ce6072` (feat)
3. **Task 3: Commit the desk-provable answers and the pre-phase snapshots, and re-confirm the gate** - `56349c10` (docs)

**Plan metadata:** committed via this SUMMARY + STATE.md update (docs commit follows)

## Files Created/Modified

- `.planning/v1.34/rig-pins.json` — `chips` map 2→11 entries, `chip_token` on all eleven, new `chips_note`
- `.planning/v1.34/tools/capture_provenance.py` — `_CHIP_CHOICES` derived from pins; widened `--no-image-plan` help; two new `--selftest` legs
- `.planning/v1.34/bench/cells/CHIP/CHIPS-MAP-DERIVATION.md` — the derivation command, verbatim output, eleven-row table, R7 cross-check, SGS-THOMSON and `0x28`/`0x40` naming traps
- `.planning/v1.34/bench/cells/CHIP/FM1608-VCC.md` — the three-command VCC resolution, root cause, byte-0 defect non-interaction, structural NAs
- `.planning/v1.34/bench/cells/CHIP/DERIVE-PLAN.json` — machine-measured `derive_plan` output for all eleven tokens
- `.planning/v1.34/bench/cells/CHIP/PRE-PHASE.md` — WRV snapshot, CLOSE-04 count, anchors, budget, ceilings, `run_gates.sh` result

## Decisions Made

- **The eleven-row `chips` table as landed, with the RESEARCH R7 cross-check:** PASS, zero
  disagreement. All nine derived values (`size_bytes`, `pin_count`, `package`, `vpp_mv`,
  `algorithm`) matched R7's table exactly:

  | key | chip_token | size_bytes | pin_count | package | vpp_mv | algorithm |
  |---|---|---|---|---|---|---|
  | `w27c512` (frozen) | `W27C512` | 65536 | 28 | DIP28 | 12000 | 7 |
  | `w27e512` | `W27E512` | 65536 | 28 | DIP28 | 12000 | 7 |
  | `sst27sf512` | `SST27SF512` | 65536 | 28 | DIP28 | 12000 | 7 |
  | `fm1608` | `FM1608` | 8192 | 28 | DIP28 | 12000 | 40 |
  | `w27e040` | `W27E040` | 524288 | 32 | DIP32 | 12000 | 8 |
  | `sst39sf040` | `SST39SF040` | 524288 | 32 | DIP32 | 12000 | 6 |
  | `w29c040` | `W29C040` | 524288 | 32 | DIP32 | 12000 | 5 |
  | `w29c020` (frozen) | `W29C020` | 262144 | 32 | DIP32 | 12000 | 5 |
  | `am27c020` | `AM27C020` | 262144 | 32 | DIP32 | **13000** | 8 |
  | `m27c512` | `M27C512` | 65536 | 28 | DIP28 | **13000** | 7 |
  | `2516` (named absence) | `2516` | 2048 | 24 | DIP24 | 25000 | 11 |

  `m27c512` resolves to vendor **SGS-THOMSON**, recorded separately from the roadmap's human label
  "ST M27C512" per v1.15 Phase 83's convention. FM1608's family formats as `0x28` (40 decimal),
  which will look like a divergence against v1.15's `0x40 (SRAM_STD/FRAM)` label but is not (a
  known, already-retired NAME-04 conflation) — recorded once in `CHIPS-MAP-DERIVATION.md`.

- **The exact `_CHIP_CHOICES` derivation line and the `--pins`-override precedence:**
  ```python
  _CHIP_CHOICES = sorted(_load_pins_chips_or_die(_DEFAULT_PINS))
  ```
  Computed at import time against `_DEFAULT_PINS` specifically. A `--pins` override is a
  **runtime** path; the argparse `choices=` gate is fixed when `build_argparser()` constructs the
  parser object, so **the default pins file wins for the argparse gate regardless of a later
  `--pins` override**. The runtime `pins["chips"][args.chip]` index (with its existing
  `except KeyError` named refusal) is unchanged, so a `--pins` override that omits a chip token
  still fails by name, not by index error. An unreadable/unparseable `_DEFAULT_PINS` raises
  `RuntimeError` with a named reason — it never falls back to an empty choices list.

- **The two new selftest leg names:**
  - `positive: _CHIP_CHOICES equals rig-pins.json's chips key set, has 11 members`
  - `negative: --chip 'notachip' (absent from pins map) is refused by name`

- **FM1608 `vcc_mv` verdict, one sentence with its strongest citation:** the field is
  decorative/display-only — `convert_to_programmer()` (`firestarter/database.py`) never includes
  `vcc_mv` or `vdd_mv` in the wire dict sent to the programmer, verified live: wire keys =
  `['algorithm', 'bus-config', 'chip-id', 'flags', 'memory-size', 'pin-count', 'pulse-delay',
  'vpp_mv']`.

- **The per-part NA map, one table** (full detail in `DERIVE-PLAN.json`):

  | Part | `id` | `blank-check` | `erase` | write op | write region |
  |---|---|---|---|---|---|
  | W27C512 | ✔ | ✔ | ✔ | `write` | `(0, 65536)` |
  | W27E512 | ✔ | ✔ | ✔ | `write` | `(0, 65536)` |
  | SST27SF512 | ✔ | ✔ | ✔ | `write` | `(0, 65536)` |
  | FM1608 | **NA** | **NA** | **NA** | `write` | `(0, 8192)` |
  | SST39SF040 | ✔ | ✔ | ✔ | `write` | `(0, 524288)` |
  | W27E040 | ✔ | ✔ | ✔ | `write` | `(0, 524288)` |
  | W29C040 | ✔ | **NA** | **NA** | `write` | `(16384, 491520)` |
  | W29C020 | ✔ | **NA** | **NA** | `write` | `(16384, 229376)` |
  | AM27C020 | ✔ | ✔ | **NA** | `write-partial` | `(261888, 256)` |
  | M27C512 | ✔ | ✔ | **NA** | `write-partial` | `(65280, 256)` |
  | 2516 (not seated) | **NA** | ✔ | **NA** | `write-partial` | `(1792, 256)` |

  All six SDP legs are `supported=False` on all eleven — the SDP exit floor can never fire in this
  phase.

- **Pre-phase `EVIDENCE.jsonl` snapshot figures:** `position_count_expected = 20`,
  `non-bringup rows = 12`.

- **CLOSE-04 "before" count, verbatim:** `issue count: 37` (`gh issue list --repo
  henols/firestarter_prom --state all --limit 1000 --json number`, authenticated, ran
  successfully).

- **Measured `run_gates.sh` counts and exit code:** `tool self-tests run: 12 / 12`, 5/5 live gates
  (independently counted via `grep -c "live gate PASS:"`), `ALL GATES PASSED`, `RC=0`.

## Deviations from Plan

None — plan executed exactly as written. All eleven values derived matched RESEARCH R7's
independently-measured table exactly; no disagreement was found that would have required stopping
and reporting.

## Known Stubs

None. No UI or data-flow stubs — this plan is bench tooling and desk records only.

## Threat Flags

None. No new network endpoints, auth paths, or trust-boundary schema changes were introduced
beyond what the plan's own `<threat_model>` already covers (T-162-01 through T-162-05, T-162-SC).

## Issues Encountered

None requiring deviation. The `capture_provenance.py --selftest` run prints two pre-existing
`FAIL:` lines to stderr from `patch_readback_fields`/`patch_image_plan_fields`'s own intentional
negative-path output (testing that those functions correctly refuse when no prior record exists);
this is inherited selftest behavior unrelated to Task 2's edits, and the tool's own `report()`
harness correctly evaluates both as `PASS:` (`ok_overall` stayed `True`, exit 0).

## Next Steps

Plan 162-02 and later bench plans (162-05 through 162-10) can now invoke `capture_provenance.py`
against any of the eleven inventory parts, key their per-step divergence lookups on
`DERIVE-PLAN.json`'s NA map (and on both `write`/`write-partial`), and cite `FM1608-VCC.md` inline
wherever FM1608's `vcc_mv` or byte-0 write behavior comes up, per the Folded Todos instruction.

## Self-Check: PASSED

All seven created/modified files verified present on disk; all four task/summary commit hashes
(`0c04361b`, `a4ce6072`, `56349c10`, `08866a28`) verified present in `git log --oneline --all`.
