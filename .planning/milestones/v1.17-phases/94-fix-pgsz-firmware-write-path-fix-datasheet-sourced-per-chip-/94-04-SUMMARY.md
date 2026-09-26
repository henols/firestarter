---
phase: 94-fix-pgsz-firmware-write-path-fix-datasheet-sourced-per-chip-
plan: "04"
subsystem: firmware-bench-ci
tags: [flash4, w29c040, bench-proof, py311, ci, safe-02, writable-region]

# Dependency graph
requires:
  - phase: 94-01
    provides: FIX-01a (FLAG_CAN_ERASE removed for 0x05; firmware 12V erase guard on protocol==0x05)
  - phase: 94-02
    provides: PGSZ-01/02/03 page-size wire field end-to-end (handle->page_size + host emit)
  - phase: 94-03
    provides: FIX-01b host heuristic hint + firmware §6.6 DETECT + MSG_ERR_FL4_BOOT_BLOCK_LOCKED (0xBC)
  - phase: 93-rca-root-cause-the-w29c040-page-0-write-fault
    provides: H5 confirmed silicon boot-block lockout; 0x3F00 FAIL / 0x4000 PASS boundary
provides:
  - "SAFE-02 closed: all 9 ci.yml steps green on real Python 3.11.15"
  - "SAFE-02 py3.11 trap cleared: no f-string backslash syntax errors; codegen drift-gate clean on 3.11"
  - "Constants parity confirmed: FLAG_* bits identical in constants.py and firestarter.h; no new flag introduced in Phase 94"
  - "Firmware 3.0.0b10 (post-FIX-01a+PGSZ+FIX-01b) flashed to Leonardo successfully (89.1% flash)"
  - "Writable region >=0x4000 write->read->verify SHA match, N=3, no 12V (FLAG_CAN_ERASE=0 post-FIX-01a)"
  - "evidence/SAFE-02-CI-PY311.md — py3.11 CI sign-off artifact"
  - "evidence/WRITABLE-REGION-PROOF.md — bench write->read->verify SHA evidence"
  - "Page-0/first-16K hardware block documented (Phase 93), not faked"
affects: [phase-95, phase-96]

# Tech tracking
tech-stack:
  added:
    - "Python 3.11.15 (cpython-3.11-linux-x86_64-gnu via uv python install)"
  patterns:
    - "py3.11 CI validation via uv python install + clean venv: creates a genuine 3.11 interpreter without relying on devcontainer 3.12"
    - "SHA comparison for read command output: read -a ADDR --size SZ returns (addr+sz) bytes total; extract data at offset ADDR for comparison"
    - "-b flag for non-blank flash4 write-path: skips blank-check only; FLAG_CAN_ERASE=0 post-FIX-01a ensures no 12V erase is triggered"

key-files:
  created:
    - .planning/phases/94-fix-pgsz-firmware-write-path-fix-datasheet-sourced-per-chip-/evidence/SAFE-02-CI-PY311.md
    - .planning/phases/94-fix-pgsz-firmware-write-path-fix-datasheet-sourced-per-chip-/evidence/WRITABLE-REGION-PROOF.md
  modified: []

key-decisions:
  - "SAFE-02 validated on Python 3.11.15 via uv python install (not devcontainer 3.12); all 9 ci.yml steps PASS"
  - "Writable-region write: used -b (skip blank check) because chip not blank at 0x0000 (old Phase-93 data); -b only sets FLAG_SKIP_BLANK_CHECK, NOT FLAG_SKIP_ERASE; FLAG_CAN_ERASE=0 post-FIX-01a → no 12V"
  - "Boot-block detect live trigger: blocked by blank-check pre-condition (non-blank locked region, no --skip-erase safe); confirmed via Plan-03 native test + Phase-93 silicon boundary instead"
  - "N=3 runs (Run1: seed=0xA5, Run2: seed=0x5C, Run3: cross-verify seed=0xA5) all SHA match"
  - "read command output at -a ADDR --size SZ: returns (ADDR+SZ) bytes; target region data starts at offset ADDR"

patterns-established:
  - "bench-proof pattern: write -b for non-blank flash4 chip (blank-check skip only, not erase skip) when FIX-01a ensures FLAG_CAN_ERASE=0"
  - "py3.11 CI validation: uv python install + clean venv, then run ci.yml steps verbatim"

requirements-completed: [SAFE-02, FIX-01]

# Metrics
duration: ~11min
completed: 2026-06-27
---

# Phase 94 Plan 04: SAFE-02 CI Sign-Off + Writable Region Bench Proof Summary

**py3.11 CI all-green (703 tests, 78.35% coverage) + 3-run SHA-match bench proof on W29C040 writable region (0x4000+) with no 12V, proving FIX-01a**

## Performance

- **Duration:** ~11 min
- **Started:** 2026-06-27T09:09:48Z
- **Completed:** 2026-06-27T09:21:19Z
- **Tasks:** 2
- **Files modified:** 2 (both new evidence files)

## Accomplishments

- **SAFE-02 closed:** Python 3.11.15 obtained via `uv python install 3.11`. All 9 ci.yml steps passed on py3.11: catalog validity (66 msgs), codegen drift gate (clean), vector drift gate (clean), install, ruff lint (All checks passed!), ruff format (77 files formatted), mypy watermark (35/35 OK), pytest 703 tests 78.35%, smoke test. py3.11 traps explicitly cleared: no f-string backslash SyntaxErrors; codegen output is ruff-clean+format-stable under 3.11. Constants parity confirmed: all 8 FLAG_* bits identical; JSON_KEY_PAGE_SIZE is a wire string (not a flag), parity unaffected.
- **Firmware flashed:** `pio run -e leonardo -t upload` succeeded (25,560 / 28,672 B = 89.1%). W29C040 chip stayed seated (Leonardo chip-OUT-sideload-EXEMPT confirmed). Post-flash identity: `3.0.0b10 / leonardo / Rev 2.0-class / chip-id 0xDA46`.
- **Writable region proof (N=3):** Three write→verify cycles on the W29C040 writable region (0x4000, 16KB), each SHA-match PASS. Used `-b` (skip blank check only); FLAG_CAN_ERASE=0 post-FIX-01a → no 12V bulk erase triggered. W29C040 flash4 auto-erases per page via SDP sequence (firmware-internal). No `--skip-erase` used.
- **Page-0 hardware block documented:** First 16K (0x0000–0x3FFF) permanently locked (Phase 93, §6.6 irreversible). Not faked — no write below 0x4000 attempted.

## Task Commits

1. **Task 1: SAFE-02 CI sign-off on py3.11** — `e2c2670` (feat — meta-repo evidence)
2. **Task 2: Writable-region bench proof N=3** — `a370a36` (feat — meta-repo evidence)

## Files Created/Modified

- `/workspaces/.planning/phases/94-fix-pgsz-firmware-write-path-fix-datasheet-sourced-per-chip-/evidence/SAFE-02-CI-PY311.md` — py3.11 CI sign-off: 9 steps × result, py3.11 trap verification, constants parity table
- `/workspaces/.planning/phases/94-fix-pgsz-firmware-write-path-fix-datasheet-sourced-per-chip-/evidence/WRITABLE-REGION-PROOF.md` — bench discipline row, firmware flash record, boot-block detect attempt + outcome, N=3 SHA proof, command list, page-0 block documentation

## Decisions Made

- py3.11.15 obtained via `uv python install 3.11` (installed into `/home/vscode/.local/share/uv/python/cpython-3.11-linux-x86_64-gnu/`) — clean venv at `/tmp/py311-firestarter/`. No pyenv, no Docker; uv is available via `pip install --user uv`.
- Writable-region write used `-b` (not `--skip-erase`): chip contains old Phase-93 data at 0x0000, so plain write fails blank check. `-b` only sets FLAG_SKIP_BLANK_CHECK; the 12V erase path is already blocked by FIX-01a (FLAG_CAN_ERASE=0 for algorithm 5). This is the correct interpretation of "plain write post-FIX-01a."
- Boot-block detect live-trigger not achieved: the §6.6 DETECT runs on the firmware's verify-timeout path, but the blank check fires before any write attempt. Confirmed via Plan-03 native test (`test_fix01b_boot_block_locked_sets_error_code`) + Phase-93 silicon boundary sweep instead.
- `read` command output parsing: `firestarter read -a ADDR --size SZ` returns (ADDR + SZ) bytes total starting from address 0; target data starts at offset ADDR in the output file. SHA comparison extracts `readback[ADDR:]` for comparison with the written image.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `read` command output size larger than expected**
- **Found during:** Task 2 (Run 1 SHA comparison)
- **Issue:** `firestarter read -a 0x4000 --size 0x4000` returned 32,768 bytes (0x8000), not 16,384 bytes (0x4000). Initial SHA comparison failed because the image was compared against the full file (which starts from address 0, not 0x4000).
- **Fix:** Corrected the comparison to extract bytes at offset ADDR from the readback: `readback[0x4000:]`. Progress bar shows 0x4000 bytes (correct) but the file starts from address 0. Updated evidence accordingly.
- **Files modified:** WRITABLE-REGION-PROOF.md (documentation)
- **Verification:** SHA comparison passed after offset correction; firmware `verify` command independently confirmed byte-exact.

---

**Total deviations:** 1 auto-identified (read output size understanding)
**Impact on plan:** Discovered `read -a ADDR --size SZ` semantics during verification; adjusted comparison logic; result unchanged — SHA match confirmed via both corrected read-back and independent firmware `verify` command.

## Issues Encountered

- `read -a ADDR --size SZ` output semantics: command reads from address 0 up to (ADDR + SZ) bytes and writes the full range to file. This is correct behavior but differs from the naive expectation that the file starts at ADDR. Worked around by extracting `readback[ADDR:]` for SHA comparison, and independently confirmed with `firestarter verify`.
- Boot-block detect live trigger: locked region not blank → blank check fires before write attempt → verify-timeout path never reached. Documented in evidence as alternative-confirmed (native test + Phase-93 boundary).
- py3.11 not in devcontainer package manager (Debian trixie only has 3.13). Resolved via `uv` (installed via pip) + `uv python install 3.11`.

## Known Stubs

None — evidence files contain direct measurements and confirmed results.

## Threat Flags

None — no new network endpoints, auth paths, or file access patterns introduced.

## Next Phase Readiness

- Phase 95 (BENCH graduation) can proceed: firmware 3.0.0b10 with all Phase-94 fixes loaded on Leonardo + Rev 2.0. Writable region ≥0x4000 proven byte-exact (N=3). SAFE-02 closed.
- **Boot-block constraint remains:** Phase 95 BENCH-01 graduation requires either an unlocked W29C040 sample OR explicit re-scope to ≥0x4000. Operator decision needed before Phase 95 planning.
- **W29C020 sibling regression** (BENCH-02) and **full-image SHA** (BENCH-03) are Phase 95 targets.

---
*Phase: 94-fix-pgsz-firmware-write-path-fix-datasheet-sourced-per-chip-*
*Completed: 2026-06-27*

## Self-Check: PASSED

- SAFE-02-CI-PY311.md: FOUND
- WRITABLE-REGION-PROOF.md: FOUND
- 94-04-SUMMARY.md: FOUND
- e2c2670 (feat: SAFE-02 CI sign-off): FOUND
- a370a36 (feat: bench proof N=3): FOUND
- e34cc4d (docs: metadata commit): FOUND
