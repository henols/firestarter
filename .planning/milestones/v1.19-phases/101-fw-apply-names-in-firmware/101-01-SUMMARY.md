---
phase: 101-fw-apply-names-in-firmware
plan: 01
subsystem: firmware
tags: [firmware, dispatch, protocol-naming, arduino, platformio, c-constants]

# Dependency graph
requires:
  - phase: 100-name-canonical-protocol-name-set-operator-approval
    provides: operator-approved 14-token canonical PROTO_<NAME> map + phantom identifier spelling (PROTOCOLS.md @ 6e7bd38)
provides:
  - firestarter/include/proto_constants.h (14 PROTO_<NAME> #define tokens, values == verbatim hex)
  - memory.cpp dispatch chain relabeled to named constants (byte-identical order/behavior)
affects: [102-host-apply-names-in-cli, 103-docs-reconcile-protocols-md]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "New firmware constant header follows firestarter.h include-guard + #define-block idiom exactly"
    - "Pure relabel: #define tokens substituted 1:1 for raw hex in dispatch comparisons, zero behavior change"

key-files:
  created:
    - firestarter/include/proto_constants.h
  modified:
    - firestarter/src/proms/memory.cpp

key-decisions:
  - "Kept the operator-approved phantom identifier spelling PROTO_PHANTOM_0x35 / PROTO_PHANTOM_0x39 verbatim (D-04) — did not normalize to _35/_39"
  - "Left the 0x11/0x2A/0x2B/0x2C infeasible dispatch arm as raw hex — no approved tokens exist for that bucket (D-04)"
  - "Left the generic `handle->protocol != 0` fail-closed guard numeric (never named) — preserves the BLOCKER-2 / 12V-VPP mitigation invariant"

patterns-established:
  - "PROTO_<NAME> constant home is firestarter/include/proto_constants.h, firmware-only (not mirrored to host constants.py per Phase 100 D-02)"

requirements-completed: [FW-01, FW-02]

coverage:
  - id: D1
    description: "firestarter/include/proto_constants.h defines all 14 operator-approved PROTO_<NAME> tokens with values identical to the verbatim hex map"
    requirement: FW-01
    verification:
      - kind: unit
        ref: "grep -c '^#define PROTO_' firestarter/include/proto_constants.h == 14"
        status: pass
      - kind: unit
        ref: "pio run -e uno (Uno build SUCCESS, compiles PROTO_PHANTOM_0x35/_0x39 identifiers)"
        status: pass
    human_judgment: false
  - id: D2
    description: "memory.cpp dispatch chain relabeled to named PROTO_ constants with dispatch order and behavior byte-identical to the raw-hex baseline"
    requirement: FW-02
    verification:
      - kind: unit
        ref: "pio test -e native -f \"*test_dispatch*\" (18/18 cases, test_configure_memory.cpp unchanged)"
        status: pass
      - kind: unit
        ref: "pio test -e native (82/82 native cases, full suite)"
        status: pass
    human_judgment: false

duration: 15min
completed: 2026-07-01
status: complete
---

# Phase 101 Plan 01: FW — Apply Names in Firmware Summary

**Defined the 14-token `PROTO_<NAME>` constant header and relabeled the `memory.cpp` dispatch chain in place — numeric values, dispatch order, and behavior all byte-identical to the raw-hex baseline.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-07-01T16:15:14Z
- **Completed:** 2026-07-01T16:24:41Z
- **Tasks:** 2
- **Files modified:** 2 (1 created, 1 modified) — both inside the `firestarter` submodule

## Accomplishments
- Created `firestarter/include/proto_constants.h` with exactly 14 `#define PROTO_<NAME>` tokens, values verbatim from Phase 100's operator-approved map (`firestarter/doc/PROTOCOLS.md` @ `6e7bd38`) — the label IS the number.
- Relabeled all six named dispatch arms in `memory.cpp:configure_memory()` from raw hex to `PROTO_` tokens, preserving exact arm order and first-match semantics.
- Flash4 arm (`0x05 || 0x35 || 0x39`) now reads `PROTO_FLASH_5V_PAGE || PROTO_PHANTOM_0x35 || PROTO_PHANTOM_0x39` — operator-approved honest phantom spelling preserved exactly.
- Infeasible arm (`0x11/0x2A/0x2B/0x2C`) and the `protocol != 0` fail-closed guard (12V-VPP / BLOCKER-2 mitigation) left as raw numeric literals per D-04 — never named.
- `pio run -e uno` SUCCESS, Flash 23516 B / 72.9% — byte-identical to the pre-relabel baseline.
- `pio test -e native` 82/82 green (18/18 dispatch cases specifically), zero test file edits.

## Task Commits

Each task was committed atomically inside the `firestarter` submodule (branch `v1.19-protocol-naming-labels`):

1. **Task 1: Create firestarter/include/proto_constants.h with the 14 PROTO_ tokens (FW-01)** - `6925b5b` (feat)
2. **Task 2: Relabel the memory.cpp dispatch chain to named constants, preserving order (FW-02)** - `81b6993` (feat)

**Plan metadata:** committed in the meta repo (this SUMMARY.md + STATE.md/ROADMAP.md left untouched — orchestrator-owned per plan directive)

## Files Created/Modified
- `firestarter/include/proto_constants.h` - New header; 14 `#define PROTO_<NAME> 0x<hex>` tokens + honest phantom-token comments, `__PROTO_CONSTANTS_H__` include guard in the `firestarter.h` idiom
- `firestarter/src/proms/memory.cpp` - Added `#include "proto_constants.h"` to the handler-include block; relabeled 6 dispatch `if` arms from raw hex to named `PROTO_` constants in place

## Decisions Made
- Kept `PROTO_PHANTOM_0x35` / `PROTO_PHANTOM_0x39` exactly as operator-approved (Phase 100 D-04) — did not "fix" to `_35`/`_39`.
- Left `0x11/0x2A/0x2B/0x2C` infeasible arm as raw hex — no approved tokens exist for that bucket; introducing tokens here would be unapproved naming.
- Left the generic `handle->protocol != 0` fail-closed guard as the numeric literal `0` — never named, per the BLOCKER-2 / 12V-VPP-hazard mitigation invariant.
- Did not mirror `PROTO_` tokens into host `constants.py` — firmware-only per Phase 100/101 D-02 (host has zero protocol constants; wire carries the integer `algorithm` field, not the token name).

## Deviations from Plan

None - plan executed exactly as written. Both tasks matched their acceptance criteria on first attempt with no auto-fixes required.

## Issues Encountered

None. `firestarter/platformio.ini` had a pre-existing unstaged whitespace-only diff (trailing space removed from a comment line) unrelated to this plan's scope — left unstaged/uncommitted, out of scope for these tasks.

## User Setup Required

None - no external service configuration required. This is a firmware-only, dual-repo-lockstep-exempt change (Phase 100/101 D-02: `PROTO_` tokens are firmware-internal, not mirrored to `constants.py`; no wire-crossing value changed).

## Next Phase Readiness

- `firestarter/include/proto_constants.h` is available as the constant home for any future firmware work referencing protocol names.
- `memory.cpp` dispatch chain now legible by name while remaining numerically and behaviorally identical — ready for Phase 102 (host display names) and Phase 103 (docs reconciliation) to build on without any firmware re-work.
- No blockers. Guard machinery (native suite, `pio run -e uno`) all green; host-side guards (`check_dispatch.py`, `diff_db.py`, constants-parity, dispatch-mirror) were untouched by this plan and remain the phase-level gate's responsibility (Wave 0 / gate-verification tasks per 101-CONTEXT.md D-03).

---
*Phase: 101-fw-apply-names-in-firmware*
*Completed: 2026-07-01*

## Self-Check: PASSED

- FOUND: firestarter/include/proto_constants.h
- FOUND: .planning/phases/101-fw-apply-names-in-firmware/101-01-SUMMARY.md
- FOUND: firestarter commit 6925b5b (Task 1)
- FOUND: firestarter commit 81b6993 (Task 2)
- FOUND: meta commit b184102 (SUMMARY.md)
