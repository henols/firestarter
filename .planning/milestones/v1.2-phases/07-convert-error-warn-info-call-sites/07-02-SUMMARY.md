---
phase: 07-convert-error-warn-info-call-sites
plan: 02
subsystem: catalog

tags: [catalog, codegen, toml, error-messages, gap-fix, wave-1]

# Dependency graph
requires:
  - 07-01 (LOG_ERROR_ID_*/LOG_WARN_ID_* macro families in logging_id.h)
provides:
  - MSG_ERR_VPP_HIGH (0xB8) in canonical catalog + both generated artifacts
  - MSG_ERR_CHIP_ID_MISMATCH (0xB9) in canonical catalog + both generated artifacts
  - MSG_ERR_MEM_SIZE_TOO_SMALL (0xBA) in canonical catalog + both generated artifacts
  - All three Phase 6 catalog gaps closed, unblocking Plans 03/04/06/12 conversion
affects:
  - 07-03 (eprom.cpp conversion — unblocked)
  - 07-04 (flash_intel.cpp conversion — unblocked)
  - 07-06 (eeprom_28c.cpp conversion — unblocked)
  - 07-12 (flash_type_3.cpp conversion — unblocked)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "D-03 one-commit-per-gap protocol: separate chore(catalog): commits for each new ID across both sub-repos"
    - "Codegen idempotence confirmed: two consecutive runs produce byte-identical output (LCAT-05)"
    - "Vendor sync byte-identity: canonical .toml == firestarter/tools/catalog/messages.toml == firestarter_app/tools/catalog/messages.toml"

key-files:
  created: []
  modified:
    - .planning/catalog/messages.toml
    - firestarter/include/messages.h
    - firestarter/src/messages.c
    - firestarter/tools/catalog/messages.toml
    - firestarter_app/firestarter/messages.py
    - firestarter_app/tools/catalog/messages.toml

key-decisions:
  - "Error variants mirror WARN counterparts exactly — same format string, same param shape, only id + name + severity differ (per plan interfaces block)"
  - "Each gap landed as a separate chore(catalog): commit in each affected repo (D-03 protocol), yielding 3 meta-repo commits + 3 firestarter commits + 3 firestarter_app commits = 9 chore commits total plus 3 dep bump commits (12 commits for this plan)"

# Metrics
duration: ~5 min
completed: 2026-05-18
---

# Phase 7 Plan 02: Catalog Gap Fix (0xB8/0xB9/0xBA) Summary

**Three ERROR-severity catalog entries added (0xB8..0xBA) mirroring their WARN counterparts' format strings and param shapes — all Phase 6 gaps closed, codegen drift gate green, decoder regression suite passing.**

## Performance

- **Duration:** ~5 min
- **Tasks:** 3/3 complete
- **Files modified:** 6 (1 canonical + 2 generated + 3 vendored)

## Accomplishments

- `MSG_ERR_VPP_HIGH` (0xB8): ERROR-severity mirror of `MSG_WARN_VPP_HIGH` (0x82). Format `"VPP is high: %u.%uV > %u.%uV"`, params `[u16, u16, u16, u16]` (8 wire bytes). Unblocks `proms/eprom.cpp` and `proms/flash_intel.cpp` VPP-high populate sites.
- `MSG_ERR_CHIP_ID_MISMATCH` (0xB9): ERROR-severity mirror of `MSG_WARN_CHIP_ID_MISMATCH` (0x83). Format `"Chip ID %#04x dont match expected ID %#04x"`, params `[u16, u16]` (4 wire bytes). Unblocks chip-id mismatch populate sites in multiple PROM modules.
- `MSG_ERR_MEM_SIZE_TOO_SMALL` (0xBA): ERROR-severity mirror of `MSG_WARN_MEM_SIZE_TOO_SMALL` (0x84). Format `"mem_size %lu too small for chip-id check"`, params `[{u32, render="dec"}]` (4 wire bytes). Unblocks mem-size guard populate site.
- All three entries appended to the ERROR section (0xA0..0xDF) immediately after the existing last entry `MSG_ERR_OP_TIMEOUT` (0xB7) and before the `# DATA` section header.
- Codegen idempotence verified: two consecutive runs to `/tmp` files produce byte-identical output (confirmed with `diff`).
- Vendor sync verified: `diff .planning/catalog/messages.toml firestarter/tools/catalog/messages.toml` and `…/firestarter_app/tools/catalog/messages.toml` both return empty.
- Host decoder regression suite (`tests/test_decoder.py`, 12 tests) passes after all three additions.
- Pre-existing dirty files (`firestarter/include/rurp_register_utils.h`, `firestarter_app/firestarter/config.py`, `firestarter_app/firestarter/main.py`) left untouched throughout.

## Commit Log

### firestarter submodule (feature/phase-10-static-pins)

| Hash | Subject |
|------|---------|
| 3436080 | chore(catalog): add MSG_ERR_VPP_HIGH 0xB8 (Phase 6 gap fix, see Phase 7) |
| 905a1a9 | chore(catalog): add MSG_ERR_CHIP_ID_MISMATCH 0xB9 (Phase 6 gap fix, see Phase 7) |
| 10eca4f | chore(catalog): add MSG_ERR_MEM_SIZE_TOO_SMALL 0xBA (Phase 6 gap fix, see Phase 7) |

### firestarter_app submodule (feature/phase-10-static-pins)

| Hash | Subject |
|------|---------|
| f512fac | chore(catalog): add MSG_ERR_VPP_HIGH 0xB8 (Phase 6 gap fix, see Phase 7) |
| d9dcdb7 | chore(catalog): add MSG_ERR_CHIP_ID_MISMATCH 0xB9 (Phase 6 gap fix, see Phase 7) |
| 08f0f41 | chore(catalog): add MSG_ERR_MEM_SIZE_TOO_SMALL 0xBA (Phase 6 gap fix, see Phase 7) |

### meta-repo superproject (feature/phase-10-static-pins)

| Hash | Subject |
|------|---------|
| 5ff2212 | chore(catalog): add MSG_ERR_VPP_HIGH 0xB8 (Phase 6 gap fix, see Phase 7) |
| a135847 | deps(07-02): bump firestarter + firestarter_app after MSG_ERR_VPP_HIGH 0xB8 |
| f3592d4 | chore(catalog): add MSG_ERR_CHIP_ID_MISMATCH 0xB9 (Phase 6 gap fix, see Phase 7) |
| f66d798 | deps(07-02): bump firestarter + firestarter_app after MSG_ERR_CHIP_ID_MISMATCH 0xB9 |
| 6dad4b0 | chore(catalog): add MSG_ERR_MEM_SIZE_TOO_SMALL 0xBA (Phase 6 gap fix, see Phase 7) |
| c195ef3 | deps(07-02): bump firestarter + firestarter_app after MSG_ERR_MEM_SIZE_TOO_SMALL 0xBA |

## Final State: Catalog Entry Count

| Severity | Count | Note |
|----------|-------|------|
| OK | 6 | unchanged |
| INIT/MAIN/END/INFO/WARN | 34 | unchanged |
| ERROR | 27 | was 24; +3 new IDs (0xB8..0xBA) |
| DATA | 3 | unchanged |
| **Total** | **71** | was 68 |

## Deviations from Plan

None — plan executed exactly as written. The three entries were appended in ID order (0xB8 → 0xB9 → 0xBA), each with a separate codegen + sync + submodule-commit cycle per D-03 protocol.

## Known Stubs

None. All three new entries are fully defined catalog entries with concrete format strings and param shapes; no placeholder values introduced.

## Threat Flags

None. No new network endpoints, auth paths, or file access patterns introduced. The catalog additions are purely internal message-ID allocations with no runtime security surface.

## Self-Check: PASSED

- `.planning/catalog/messages.toml` exists with MSG_ERR_VPP_HIGH, MSG_ERR_CHIP_ID_MISMATCH, MSG_ERR_MEM_SIZE_TOO_SMALL: CONFIRMED
- `firestarter/include/messages.h` contains 0xB8, 0xB9, 0xBA: CONFIRMED (grep -c returns 3)
- `firestarter_app/firestarter/messages.py` contains all three names: CONFIRMED (grep -c returns 6, counting both ID constant and CATALOG entry)
- Codegen drift: zero diff between two consecutive runs: CONFIRMED
- Vendor .toml byte-identity: CONFIRMED (diff returns empty for both sub-repos)
- Decoder tests (12/12 pass): CONFIRMED
- Pre-existing dirty files untouched: CONFIRMED (rurp_register_utils.h, config.py, main.py still dirty, not staged)
- All 12 plan commits exist in git log: CONFIRMED
