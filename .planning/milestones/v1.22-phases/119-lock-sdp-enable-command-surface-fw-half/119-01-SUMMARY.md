---
phase: 119-lock-sdp-enable-command-surface-fw-half
plan: 01
subsystem: firmware-protocol-catalog
tags: [catalog, codegen, messages-toml, sdp, at28c]

# Dependency graph
requires:
  - phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half
    provides: the four-id catalog precedent (0x5E/0x5F/0x86/0x87), the D-03 three-repo codegen ritual, and the 32-char naming ceiling finding
provides:
  - Three new INFO-band catalog ids (0x60, 0x61, 0x62) synced byte-identically into both sub-repos, ready for Plan 119-04 (lock/unlock ops) and Plan 119-08 (page-load tracker) to emit
affects: [119-04, 119-06, 119-07, 119-08, 119-10]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Same D-03 three-repo codegen ritual as Phase 118: canonical tools/catalog/messages.toml -> sync_to_subrepos.sh -> regenerated include/messages.h + firestarter/messages.py, proven via three-way cmp + --check + git diff --exit-code"

key-files:
  created: []
  modified:
    - tools/catalog/messages.toml (meta + both sub-repo vendored copies, byte-identical)
    - firestarter/include/messages.h (regenerated, codegen output only)
    - firestarter_app/firestarter/messages.py (regenerated, codegen output only)

key-decisions:
  - "0x61's format string carries both of D-12's mandatory clauses in one line: 'SDP lock sequence emitted in %lu us; protection state is not readable'"
  - "0x62 (MSG_INFO_PAGE_LOAD_WORST_US) is a measurement-only id with no runtime budget compare, preserving 118 D-10's declination; its TOML comment frames gh#11 as a conflation bug per Phase 117's finding, reusing eeprom_28c.cpp's existing citation wording rather than inventing new framing"
  - "No new unlock id (0x5E/0x5F reused per D-13), no new ERROR id (0xA5 reused for D-06's refusal), no new WARN id (0x87 reused by the lock's budget check) -- catalog additions are exactly the three ids this plan owns"
  - "messages.h carries only #define numeric constants, no PROGMEM string table on the firmware side -- so three new unreferenced ids cost exactly 0 bytes of flash this plan; format strings live only in the host's messages.py. Flash figures are therefore byte-identical to the phase base (1880054), not merely close to it"

requirements-completed: []

coverage:
  - id: D1
    description: "Three new INFO catalog ids (MSG_INFO_SDP_LOCK 0x60, MSG_INFO_SDP_LOCK_DONE_US 0x61, MSG_INFO_PAGE_LOAD_WORST_US 0x62) added to the canonical messages.toml, each severity INFO, wire_format id_frame, names <=32 chars"
    verification:
      - kind: unit
        ref: "grep -c 'MSG_INFO_SDP_LOCK\"|MSG_INFO_SDP_LOCK_DONE_US\"|MSG_INFO_PAGE_LOAD_WORST_US\"' tools/catalog/messages.toml -> 3"
        status: pass
    human_judgment: false
  - id: D2
    description: "Three-repo codegen ritual run (sync_to_subrepos.sh); meta/firmware/host messages.toml byte-identical; both generated artifacts (messages.h, messages.py) drift-free under codegen.py --check + git diff --exit-code"
    verification:
      - kind: unit
        ref: "cmp tools/catalog/messages.toml firestarter/tools/catalog/messages.toml && cmp tools/catalog/messages.toml firestarter_app/tools/catalog/messages.toml"
        status: pass
      - kind: unit
        ref: "python3 tools/catalog/codegen.py --check (both sub-repos) + git diff --exit-code on both generated artifacts"
        status: pass
    human_judgment: false
  - id: D3
    description: "Firmware still builds on all three AVR envs (uno, uno328pb, leonardo) with the regenerated header; host gates (pytest suite, check_no_log_in_sdp_window.py, check_dispatch.py, ruff) remain at measured baseline"
    verification:
      - kind: unit
        ref: "pio run (firestarter) -- 3 succeeded in 00:00:03.859"
        status: pass
      - kind: unit
        ref: "pytest tests/test_sdp_table_parity.py tests/test_check_no_log_in_sdp_window.py tests/test_sdp_bus_config_drift.py tests/test_revision_constants_parity.py -q -- 21 passed"
        status: pass
    human_judgment: false

duration: ~10min
completed: 2026-07-28
status: complete
---

# Phase 119 Plan 01: Three New SDP-Lock + Page-Load Catalog IDs Summary

**Three-repo codegen ritual adds `MSG_INFO_SDP_LOCK` (0x60), `MSG_INFO_SDP_LOCK_DONE_US` (0x61, carrying D-12's dual honesty clause), and `MSG_INFO_PAGE_LOAD_WORST_US` (0x62) with zero flash cost and zero behavior change.**

## Performance

- **Duration:** ~10 min
- **Completed:** 2026-07-28T18:41Z
- **Tasks:** 2/2
- **Files modified:** 6 (3 repos x 2 files each, `codegen.py` unchanged in both sub-repos)

## Accomplishments

- Added three new `[[messages]]` blocks to the canonical `tools/catalog/messages.toml` immediately after the existing `MSG_INFO_SDP_UNLOCK_DONE_US` (0x5F) block, mirroring Phase 118's field order and column alignment
- Ran `bash tools/catalog/sync_to_subrepos.sh` — copied `messages.toml`/`codegen.py` into both sub-repos, confirmed cross-sub-repo byte-identity, regenerated `firestarter/include/messages.h` and `firestarter_app/firestarter/messages.py`
- Proved three-way byte-identity of `messages.toml` (meta vs firmware vs host) via `cmp`, both `codegen.py --check` gates, and `git diff --exit-code` on both regenerated artifacts (no drift after re-running the generator against the staged files)
- Confirmed `MSG_INFO_SDP_UNLOCK`, `MSG_INFO_SDP_UNLOCK_DONE_US`, and `MSG_ERR_NOT_SUPPORTED` unchanged in both generated artifacts; new names each <=32 chars (17/25/27) so `messages.h`'s generated column layout did not reflow
- Firmware builds SUCCESS on all three AVR envs with the regenerated header. Flash/RAM figures are **byte-identical to the phase base** (`1880054`) because `messages.h` carries only numeric `#define`s, no PROGMEM string table — three unreferenced ids cost 0 bytes this plan:
  - Leonardo: 25680/28672 flash, 1998/2560 RAM (unchanged)
  - Uno: 23542/32256 flash, 1559/2048 RAM (unchanged)
  - uno328pb: 23592/32384 flash, 1563/2048 RAM (unchanged)
- Host lint validated: `ruff check` and `ruff format --check` pass in `firestarter_app`; `pyproject.toml` pins `target-version = "py39"` for ruff, so the check is against the CI target even though the devcontainer interpreter itself is 3.12
- Host gates re-run at measured baseline, none regressed:
  - `pytest tests/test_sdp_table_parity.py tests/test_check_no_log_in_sdp_window.py tests/test_sdp_bus_config_drift.py tests/test_revision_constants_parity.py -q` — 21 passed
  - `python3 tools/check_no_log_in_sdp_window.py` — `PASS:` line naming emitter lines 222-238 and completion-poll lines 272-285, exit 0
  - `python3 tools/check_dispatch.py` — exit 0 (746 scanned, 0 regressions)
  - Two known-RED modules (`tests/test_audit_coverage_matrix.py`, `tests/test_no_programmer_found_*`) were NOT run/chased — pre-existing, named in CONTEXT and confirmed not this plan's damage

## Task Commits

Each task was committed atomically, following the plan's explicit three-commit repo mechanics (one per sub-repo, plus one meta commit for the gitlinks + SUMMARY) rather than a strict one-task-one-commit split, per the plan's own "Repo and commit mechanics" section:

1. **Task 1 (meta catalog edit) + Task 2 (ritual/proof)** — landed as:
   - `firestarter@36a85ad` — `feat(119-01): add SDP lock report pair and page-load worst-interval catalog ids`
   - `firestarter_app@2821907` — `feat(119-01): add SDP lock report pair and page-load worst-interval catalog ids`
   - meta (this commit, following this SUMMARY) — `docs(119-01): sync catalog to both sub-repos (LOCK-02 catalog portion)`

## Files Created/Modified

- `tools/catalog/messages.toml` (meta) — three new `[[messages]]` blocks, INFO band, ids 0x60/0x61/0x62
- `firestarter/tools/catalog/messages.toml` — synced vendored copy, byte-identical to meta
- `firestarter/include/messages.h` — regenerated, three new `#define`s added, no reflow
- `firestarter_app/tools/catalog/messages.toml` — synced vendored copy, byte-identical to meta
- `firestarter_app/firestarter/messages.py` — regenerated, three new entries in the id table + name constants

## Decisions Made

- 0x61's format string satisfies D-12 as a single line: "SDP lock sequence emitted in %lu us; protection state is not readable" — both the emitted-clause and the not-readable-clause are present, matching the acceptance criterion literally.
- Entry 3's TOML comment reuses `eeprom_28c.cpp`'s existing gh#11 citation wording ("completion/data-landed CONFLATION bug ... not a sampling-rate or timing-budget bug") rather than inventing new framing, per the read_first instruction.
- `catalog-sync-check.yml` remains expected-red for this plan (it pins both sub-repos at `ref: main`) — this is recorded as known-and-expected exactly as `118-NONREGRESSION.md` framed it, not chased or "fixed".

## Deviations from Plan

None - plan executed exactly as written. Both tasks' acceptance criteria were met without any Rule 1-4 auto-fixes.

## Issues Encountered

None. Pre-existing untracked/modified files in `firestarter_app` (`.gitignore` local edit, `.coverage`, `.planning/config.json`, `SECURITY.md`, `doc/lockable-proms.md`, `write_test_port.sh`) predate this session (timestamps ~7h before this plan's execution window) and are unrelated to the catalog ritual — left untouched, out of scope per the scope boundary rule, and excluded from the sub-repo commit via individual `git add`.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None. No new call sites emit these ids yet — that is this plan's explicit, intentional scope (Plans 119-04 and 119-08 wire the emitters). No UI or data-rendering path is affected.

## Requirement Status

**LOCK-02 remains OPEN.** This plan lands only the catalog portion (the standalone lock's report surface, D-12/D-13). The requirement spans this plan plus 119-04 (commands/ops/wiring), 119-06 (report-shape proof), and 119-07 (dispatch proofs, which closes it). `REQUIREMENTS.md` was not touched — zero requirement rows changed.

## Next Phase Readiness

- The three new ids exist byte-identically in all three repos and are ready for Plan 119-04's `eeprom28c_sdp_lock_execute` (via the shared bracket helper) and Plan 119-08's `eeprom28c_write_execute` page-load tracker to emit.
- Flash headroom for LOCK-06's later arithmetic starts from the unchanged phase base: Leonardo 25680/28672 (2992 B free), Uno 23542/32256, uno328pb 23592/32384 — this plan spent 0 B.
- No blockers for Plan 119-02.

---
*Phase: 119-lock-sdp-enable-command-surface-fw-half*
*Completed: 2026-07-28*

## Self-Check: PASSED

- FOUND: `.planning/phases/119-lock-sdp-enable-command-surface-fw-half/119-01-SUMMARY.md`
- FOUND: `5bf07da` (meta commit)
- FOUND: `36a85ad` (firestarter commit)
- FOUND: `2821907` (firestarter_app commit)
