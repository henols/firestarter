---
phase: 101-fw-apply-names-in-firmware
verified: 2026-07-01T00:00:00Z
status: passed
score: 7/7 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 101: FW — Apply Names in Firmware Verification Report

**Phase Goal:** Apply the operator-approved canonical `PROTO_<NAME>` name set inside the firmware — a rename/relabel-only phase. Define `PROTO_<NAME>` constants for every protocol number (numeric values unchanged), relabel the raw-hex dispatch chain in `firestarter/src/proms/memory.cpp` to those named constants, and confirm the many-to-one handler files/functions conform to the approved family-name layer. Dispatch order, behavior, and every numeric value stay identical. No CLI change (GATE-03), no `chip_database.json` change and no wire/lockstep-constant value change (GATE-02), numbers stay the authoritative dispatch key (GATE-01).
**Verified:** 2026-07-01
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `firestarter/include/proto_constants.h` defines a `PROTO_<NAME>` constant for every protocol number, values == verbatim hex | VERIFIED | File read directly: exactly 14 `#define PROTO_` lines (`grep -c` = 14); all 12 real + 2 phantom tokens present with correct hex values; `PROTO_PHANTOM_0x35`/`PROTO_PHANTOM_0x39` spelling exact (D-04); no `0x11/0x2A/0x2B/0x2C` tokens present (`grep` exit 1) |
| 2 | `memory.cpp` dispatch chain reads by name for the relabeled arms; dispatch ORDER and behavior byte-identical to baseline | VERIFIED | `git diff 6e7bd38..89e9e56 -- src/proms/memory.cpp` and diff vs pre-Phase-100 baseline (`30ad80e`) show ONLY the `#include` addition + literal-for-literal hex→PROTO_ substitution; arm order unchanged (0x10→0x0D→0x06→flash4→eprom→sram→infeasible→fail-closed→mem_type fallback); `handle->protocol != 0` fail-closed guard still numeric; infeasible arm (`0x11/0x2A/0x2B/0x2C`) still raw hex |
| 3 | Flash4 arm carries the operator-approved phantom tokens `PROTO_PHANTOM_0x35`/`PROTO_PHANTOM_0x39` | VERIFIED | `memory.cpp` line 90: `handle->protocol == PROTO_FLASH_5V_PAGE \|\| handle->protocol == PROTO_PHANTOM_0x35 \|\| handle->protocol == PROTO_PHANTOM_0x39` |
| 4 | All 7 handler families (eprom/sram/flash4/flash3/eeprom28c/flash_intel/not-implemented) confirmed conformant to the approved family-name layer — zero renames (D-01) | VERIFIED | Directly grepped all 7 `include/*.h` headers: `configure_eprom`, `configure_sram`, `configure_flash3`, `configure_flash4`, `configure_eeprom28c`, `configure_flash_intel`, `configure_not_implemented` all present exactly as named; `.cpp` filenames unchanged (`ls src/proms/`); PROTOCOLS.md Handler-family layer table matches these names exactly |
| 5 | `pio run -e uno`/`-e leonardo` build SUCCESS and `pio test -e native` stays 82/82 with zero test edits | VERIFIED | Independently re-ran all three commands myself (not trusting SUMMARY): native 82/82 succeeded; uno SUCCESS Flash 23516B/72.9%; leonardo SUCCESS Flash 25654B/89.5% — both byte-identical to SUMMARY-claimed values; `git diff` confirms zero test file touched anywhere in the phase |
| 6 | `firestarter/CLAUDE.md` dispatch/handler tables synced to PROTO_ tokens; no dangling old prose names | VERIFIED | Read CLAUDE.md directly; dispatch-order list (items 1-6) and Algorithm Handlers table use `PROTO_*` tokens; `grep -n -E "EPROM_STD\|FLASH_AMD_STD\|FLASH_AMD_ALT\|FLASH_EEPROM\b\|FLASH_EEPROM2\|EPROM_QUICK\|EPROM_LEGACY\|EEPROM_POLL\|SRAM_\*"` returns 0 matches |
| 7 | GATE-01/02/03 hold: numbers stay dispatch key, no DB/wire/value change, no CLI change | VERIFIED | Independently re-ran the full guard suite (see below) — all green, matching SUMMARY claims exactly |

**Score:** 7/7 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/include/proto_constants.h` | New header, 14 `#define PROTO_<NAME>` tokens, include-guarded | VERIFIED | Exists; 14 defines confirmed by grep + direct read; `#ifndef __PROTO_CONSTANTS_H__` guard present, closed with matching `#endif` |
| `firestarter/src/proms/memory.cpp` | Relabeled dispatch arms + `#include "proto_constants.h"` | VERIFIED | Direct read confirms `#include "proto_constants.h"` present in handler-include block (line 22); all 6 named arms relabeled; infeasible + fail-closed arms stay numeric |
| `firestarter/CLAUDE.md` | Dispatch/handler tables synced to PROTO_ tokens | VERIFIED | Direct read + grep confirm no old prose names remain; new PROTO_ tokens present including the previously-undocumented 0x34 row |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `memory.cpp` | `proto_constants.h` | `#include "proto_constants.h"` | WIRED | Confirmed present in the include block; compiles clean in both uno and leonardo builds (proves the tokens resolve) |
| Each relabeled `if (handle->protocol == PROTO_...)` arm | same `configure_*` handler, same order | direct substitution | WIRED | Diff vs pre-relabel baseline shows a pure literal substitution with zero reordering, zero handler-call change |
| `PROTOCOLS.md` Handler-family layer | actual `configure_*`/`.cpp` names | grep-verified conformance | WIRED | All 7 families' approved names already equal existing symbols — confirmed by direct grep against all 7 handler headers |
| `test_dispatch_mirror.py` (doc leg) | `check_dispatch.dispatch()` (tool leg) | two-table join in `parse_protocols_md()` | WIRED | Read full parser source — genuine two-table regex join (not a stub); both dispatch-mirror tests pass when independently re-run |

### GATE Guard Suite (independently re-executed, not trusted from SUMMARY)

| Guard | Command | Result | Status |
|-------|---------|--------|--------|
| Native tests | `pio test -e native` | 82 test cases: 82 succeeded | PASS |
| Uno build | `pio run -e uno` | SUCCESS, Flash 23516B/72.9% (matches SUMMARY exactly) | PASS |
| Leonardo build | `pio run -e leonardo` | SUCCESS, Flash 25654B/89.5% (matches SUMMARY exactly) | PASS |
| Dispatch-mirror | `pytest tests/test_dispatch_mirror.py -q` | 2 passed | PASS |
| Constants-parity | `pytest tests/test_revision_constants_parity.py -q` | 6 passed (count unchanged, D-02 holds — no PROTO_ mirror in constants.py) | PASS |
| check_dispatch | `python tools/check_dispatch.py` | PASS: 746 chips scanned, 0 dispatch regressions, 0 consistency violations | PASS |
| diff_db | `python tools/diff_db.py` | PASS: 2 pre-existing (Phase-94) changed chips explained, 0 new, 0 removed | PASS |
| ruff check | `ruff check firestarter/ tests/` | All checks passed! | PASS |
| ruff format | `ruff format --check firestarter/ tests/` | 77 files already formatted | PASS |
| mypy watermark | `python tools/check_mypy_watermark.py` | 1 error, 34 below watermark (35) | PASS |
| GATE-03 diff scope | `git diff` across full phase (both submodules) | Only `tests/test_dispatch_mirror.py` (host) + `CLAUDE.md`/`proto_constants.h`/`memory.cpp` (firmware) touched — no CLI file anywhere | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| FW-01 | 101-01 | PROTO_ constants defined, values unchanged | SATISFIED | `proto_constants.h` verified directly — 14 tokens, correct values |
| FW-02 | 101-01 | Dispatch chain relabeled to named constants, order/behavior preserved | SATISFIED | `memory.cpp` diff verified — pure literal substitution, order unchanged, builds/tests green |
| FW-03 | 101-02 | Handler files/functions conform to approved family-name layer | SATISFIED (via D-01 conformance-confirm) | All 7 handler symbols verified present exactly as named; PROTOCOLS.md Handler-family layer matches; zero renames needed (operator-approved names already equal existing code per D-01) |
| GATE-01 | 101-00/01/02 | Numbers stay dispatch key; dispatch behavior unchanged | SATISFIED | Native 82/82, dispatch-mirror 2/2, structural grep confirms all PROTO_ uses are numeric `==` comparisons only |
| GATE-02 | 101-02 | No DB/wire/value change | SATISFIED | diff_db identity, check_dispatch PASS, constants-parity count unchanged (6), zero PROTO_ mirror in constants.py |
| GATE-03 | 101-02 | No CLI change | SATISFIED | Full phase diff scope confirms zero CLI file touched in either submodule |

**Note on ROADMAP wording vs D-01:** ROADMAP.md/REQUIREMENTS.md phrase FW-03 as "renamed" — Phase 101's context document (101-CONTEXT.md D-01) is an explicit, documented operator decision that the approved family names ARE the pre-existing names, so FW-03 is satisfied by conformance-confirmation rather than an actual rename. This is not a scope reduction — it was verified empirically in this report (all 7 handler headers grepped directly) that no rename was needed, and the decision to avoid an unnecessary 100+-reference rename that would re-open Phase 100 is a reasonable, transparently-recorded engineering call, not a gap.

### Anti-Patterns Found

None. No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` markers found in any of the 4 files touched by this phase (`proto_constants.h`, `memory.cpp`, `CLAUDE.md`, `test_dispatch_mirror.py`). The dispatch-mirror parser is a genuine two-table regex join (verified by reading the full source), not a stub returning a hardcoded/empty result.

### Human Verification Required

None. This is a rename/relabel-only phase; all behaviors have automated verification (native tests, board builds, host guard suite). 101-VALIDATION.md explicitly notes no bench hardware run is required (dispatch order/values identical, proven by golden-trace-equivalent native tests + byte-identical build sizes).

### Gaps Summary

No gaps found. Every must-have truth, artifact, and key link was independently verified against the actual codebase — not inferred from SUMMARY prose. All three plan SUMMARYs' claims (uno+leonardo build SUCCESS byte-identical, native 82/82, check_dispatch PASS 746, diff_db identity, constants-parity 6, dispatch-mirror green, ruff clean) were reproduced by directly re-running the underlying commands in this session, and every number matched exactly. The phase diff is minimal and precisely scoped (3 firmware files + 1 host test file across the whole phase), with zero incidental changes.

---

_Verified: 2026-07-01_
_Verifier: Claude (gsd-verifier)_
