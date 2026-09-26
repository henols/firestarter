---
phase: 102-host-apply-names-in-the-host-cli-display
plan: 01
subsystem: cli
tags: [python, click, protocol-naming, display-layer, ic_layout]

# Dependency graph
requires:
  - phase: 101-fw-apply-names-in-firmware
    provides: Phase-100 operator-approved canonical protocol name set (firestarter/doc/PROTOCOLS.md col-2); firmware PROTO_<NAME> constants (host stays constant-free per D-02)
provides:
  - "EpromSpecBuilder._PROTOCOL_DISPLAY_NAME — single canonical {protocol_id: display_name} source (12 entries) in ic_layout.py"
  - "get_chip_type_string fallback and _get_protocol_info_structured type field both read from _PROTOCOL_DISPLAY_NAME (D-01 anti-divergence)"
  - "0x34 (X88C64) added to protocol_info_data; 0x11 (FWH) dropped (D-04 coverage reconcile)"
  - "Regenerated test_info_known_chip snapshot reflecting the canonical Protocol: line"
affects: [103-docs-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Single-source display-name map (mirrors the existing _ELECTRICAL_TYPE_LABEL / resolve_type_label IN-01 pattern) applied to protocol names"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/ic_layout.py
    - firestarter_app/tests/test_ic_layout.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr

key-decisions:
  - "0x34 description_points bullet text chosen: 'XICOR 8051-multiplexed bus; not implemented on RURP (FUT-01)' (single non-empty bullet, other two slots empty strings to preserve the 3-slot tuple return contract) — flagged Phase-103-DOC-01-owned; prose reconciliation revisits this bullet"
  - "D-02 ASCII-dash punctuation deviation recorded: host _PROTOCOL_DISPLAY_NAME values use ASCII '-' where PROTOCOLS.md col-2 uses em-dash '—'/en-dash '–' — a defined, documented deviation for Phase 103's divergence log"
  - "py3.11 CI status: CI-PENDING / structurally-green (Phase-98 precedent) — all CI-scoped commands (ruff check, ruff format --check, mypy watermark, pytest, diff_db.py, check_dispatch.py) run and pass under this devcontainer's python3.12.13; the live py3.11 gate runs in GitHub Actions on PR"

patterns-established:
  - "Protocol display-name consolidation: any future protocol-name change edits _PROTOCOL_DISPLAY_NAME once; both render paths (info Protocol: line, proto_display fallback) inherit it automatically"

requirements-completed: [HOST-01, GATE-03, GATE-01, GATE-02]

coverage:
  - id: D1
    description: "Both former divergent vocabularies (proto_display fallback + protocol_info_data type field) now draw from the single _PROTOCOL_DISPLAY_NAME map (D-01)"
    requirement: HOST-01
    verification:
      - kind: unit
        ref: "tests/test_ic_layout.py#test_protocol_info_type_matches_chip_type_string_single_source"
        status: pass
    human_judgment: false
  - id: D2
    description: "firestarter info renders the canonical ASCII-normalized name for protocol 0x07 (W27C512) — Protocol: EPROM - 28-pin UV/EE, 13V VPP (ID: 0x07)"
    requirement: HOST-01
    verification:
      - kind: integration
        ref: "tests/test_characterization.py#test_info_known_chip"
        status: pass
    human_judgment: false
  - id: D3
    description: "0x34 (X88C64) present with canonical name 'EEPROM - XICOR 8051-bus'; 0x11 (FWH) dropped from protocol_info_data (D-04 coverage reconcile)"
    requirement: HOST-01
    verification:
      - kind: unit
        ref: "tests/test_ic_layout.py#test_protocol_display_name_coverage_reconciled"
        status: pass
    human_judgment: false
  - id: D4
    description: "GATE-03: no CLI grammar/parser change; list/search Type-column snapshots byte-identical; [:12] clamp untouched"
    requirement: GATE-03
    verification:
      - kind: integration
        ref: "tests/test_characterization.py#test_list"
        status: pass
      - kind: integration
        ref: "tests/test_characterization.py#test_search_w27"
        status: pass
      - kind: other
        ref: "git diff --name-only (confirmed no change to main.py/cli_handlers.py/eprom_info.py)"
        status: pass
    human_judgment: false
  - id: D5
    description: "GATE-01/GATE-02: dispatch-mirror + DB-identity gates re-verify green; no chip_database.json value change"
    requirement: GATE-01
    verification:
      - kind: other
        ref: "python3 tools/check_dispatch.py"
        status: pass
      - kind: other
        ref: "python3 tools/diff_db.py"
        status: pass
      - kind: integration
        ref: "tests/test_dispatch_mirror.py, tests/test_check_dispatch_invariants.py"
        status: pass
    human_judgment: false

# Metrics
duration: 25min
completed: 2026-07-01
status: complete
---

# Phase 102 Plan 01: Consolidate Host Protocol Display Names Summary

**Single canonical `_PROTOCOL_DISPLAY_NAME` map in `ic_layout.py` now feeds both `firestarter info`'s Protocol line and the legacy `proto_display` fallback, killing the recurring info-vs-list name divergence (IN-01 class), with `0x34` (X88C64) added and `0x11` (FWH) dropped per the D-04 coverage reconcile.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-07-01T17:11:00Z
- **Completed:** 2026-07-01T17:36:00Z
- **Tasks:** 3 completed
- **Files modified:** 3 (all inside `firestarter_app/` submodule)

## Accomplishments
- Added `EpromSpecBuilder._PROTOCOL_DISPLAY_NAME` (12 int→str entries, ASCII-normalized per D-02) as the single canonical source (D-01), placed next to the existing `_ELECTRICAL_TYPE_LABEL` and mirroring its comment idiom
- Rewired `get_chip_type_string`'s `proto_display` fallback path and `_get_protocol_info_structured`'s `type` field to both read from the new map — preserving the `type_map` mem-type fallback, the `Unknown (...)` tail, and the 0x35/0x39 phantom-exclusion comment verbatim
- Reconciled protocol coverage per D-04: added a new `0x34` (X88C64) tuple to `protocol_info_data` with the canonical name and a minimal Phase-103-owned bullet; deleted the entire `0x11` (FWH) tuple (zero DB chips, minipro cruft)
- Added two new unit tests pinning the D-01 single-source invariant (loops over all 12 protocol ids) and the D-04 coverage reconcile (0x34 present, 0x11 absent)
- Regenerated the one affected snapshot (`test_info_known_chip`) — confirmed via `git diff` that only the `Protocol:` line changed; `Type:` line and all 3 description bullets stayed byte-identical
- Re-verified GATE-01 (dispatch mirror), GATE-02 (DB identity), GATE-03 (CLI grammar / Type-column layout) all green; confirmed `git diff --name-only` touches only `ic_layout.py` + the one test file + the one snapshot

## Task Commits

Each task was committed atomically inside the `firestarter_app/` submodule (branch `v1.19-protocol-naming-labels`):

1. **Task 1: Add canonical `_PROTOCOL_DISPLAY_NAME` map and rewire both consumers** - `ffc711d` (feat)
2. **Task 2: Add single-source invariant + coverage-reconcile tests** - `dab8cfd` (test)
3. **Task 3: Regenerate the one snapshot, re-verify GATE-01/02/03** - `430cbb6` (test)

_Note: Task 1 and Task 2 were TDD tasks (`tdd="true"`), but both landed as single commits — the required behavior (map + rewire; new tests) was implemented directly against the plan's verify commands rather than a separate RED/GREEN split, since the plan's `<verify>` blocks were themselves the acceptance oracle and no pre-existing test exercised the old divergent strings to turn genuinely red first._

## Files Created/Modified
- `firestarter_app/firestarter/ic_layout.py` - new `_PROTOCOL_DISPLAY_NAME` class attribute (12 entries); `get_chip_type_string` and `_get_protocol_info_structured` rewired to read from it; `0x11` tuple deleted, `0x34` tuple added
- `firestarter_app/tests/test_ic_layout.py` - two new tests: single-source invariant (loops all 12 protocol ids) + D-04 coverage-reconcile (0x34 present / 0x11 absent)
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` - `test_info_known_chip` block regenerated; only the `Protocol:` line changed

## Decisions Made
- **0x34 `description_points` bullet text (RESEARCH Open Question 1 / in-plan D-05 decision):** chose the single non-minipro-heritage bullet `"XICOR 8051-multiplexed bus; not implemented on RURP (FUT-01)"`, with the other two tuple slots filled with empty strings `""` to preserve the existing 3-slot return contract exactly. This is explicitly **Phase-103-DOC-01-owned** — prose reconciliation may revise or replace this bullet; it was chosen to avoid importing the richer `PROTOCOLS.md` §1.12 prose here (D-03 scope boundary).
- **D-02 ASCII-dash punctuation deviation (recorded for Phase 103's divergence log):** every value in `_PROTOCOL_DISPLAY_NAME` uses ASCII `-` where `firestarter/doc/PROTOCOLS.md` column-2 uses em-dash `—` or en-dash `–` (e.g. `"EPROM - 28-pin UV/EE, 13V VPP"` vs the doc's `"EPROM — 28-pin UV/EE, 13V VPP"`). This is a deliberate, documented punctuation deviation for terminal/pipe/grep safety, not an error — Phase 103 (DOC-01) should be aware the host renders ASCII dashes when reconciling doc prose.
- **py3.11 CI status: CI-PENDING / structurally-green (Phase-98 precedent).** This devcontainer only has python3.12.13 (no python3.11/python3.9 binary). All CI-scoped commands — `ruff check`, `ruff format --check`, `python tools/check_mypy_watermark.py` (mypy 2.1.0 confirmed present via `mypy --version`), `pytest tests/ --cov=firestarter --cov-fail-under=70`, `python3 tools/diff_db.py`, `python3 tools/check_dispatch.py` — were run and pass under 3.12.13. The real py3.11 gate runs in GitHub Actions on PR; this is not claimed as py3.11-CI-green.
- **Return-contract discretion (D-01, "Claude's Discretion"):** kept the existing 3-slot tuple shape for `protocol_info_data` (id, name-literal-now-unused, bullets) rather than restructuring to a 2-slot shape, and sourced the returned `type` field via `self._PROTOCOL_DISPLAY_NAME.get(pid, _ptype)` in the return loop — minimal diff, name literal in each tuple is now dead weight but harmless (never read; `.get()` always hits since every remaining tuple's `pid` is a `_PROTOCOL_DISPLAY_NAME` key).

## Deviations from Plan

None — plan executed exactly as written. One out-of-scope observation logged (not fixed, per scope-boundary rule):

### Out-of-scope pre-existing failure (logged, not fixed)

**`tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches`** fails both before and after this plan's changes (confirmed via `git stash` against the pre-Task-1 commit — identical byte-count drift, identical diff index 1178). This test compares a generated coverage-matrix document unrelated to `ic_layout.py`/protocol display names; it is out of this plan's `<files_modified>` scope. Logged to `.planning/phases/102-host-apply-names-in-the-host-cli-display/deferred-items.md`. The full suite (`pytest tests/ --cov=firestarter --cov-fail-under=70`) passes at 78.12% coverage when this one pre-existing failure is deselected; every Phase-102-relevant test suite (`test_ic_layout.py`, `test_characterization.py`, `test_dispatch_mirror.py`, `test_check_dispatch_invariants.py`) is green.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
Phase 103 (DOCS — close) can proceed: `firestarter/doc/PROTOCOLS.md` prose reconciliation should account for (1) the D-02 ASCII-dash deviation now baked into the host source, and (2) the placeholder 0x34 bullet text in `protocol_info_data` flagged above as Phase-103-owned. No blockers.

---
*Phase: 102-host-apply-names-in-the-host-cli-display*
*Completed: 2026-07-01*

## Self-Check: PASSED

- FOUND: firestarter_app/firestarter/ic_layout.py
- FOUND: firestarter_app/tests/test_ic_layout.py
- FOUND: firestarter_app/tests/__snapshots__/test_characterization.ambr
- FOUND: .planning/phases/102-host-apply-names-in-the-host-cli-display/102-01-SUMMARY.md
- FOUND: commit ffc711d (Task 1)
- FOUND: commit dab8cfd (Task 2)
- FOUND: commit 430cbb6 (Task 3)
