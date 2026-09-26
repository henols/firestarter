---
phase: 82-electrically-rewritable-silicon-validation
plan: 01
subsystem: testing
tags: [eprom, bench, evidence, deterministic, rng, python, ruff]

# Dependency graph
requires:
  - phase: 81-2516-db-entry-non-destructive-read-sweep
    provides: EVIDENCE.{md,json} scaffold with 11 Phase 81 cells + SAFE-01/02/03 framing

provides:
  - Deterministic per-chip full-size image generator (tools/gen_test_image.py)
  - 12 pinning tests for the generator (size, determinism, distinct seeds, non-trivial content, CLI)
  - SAFE-02 gate recorded (663 tests + 0xA4 ack_data=False guard green, 2026-06-24)
  - EVIDENCE.json extended with 5 Phase 82 write columns + phase82 section; 11 Phase 81 cells preserved
  - EVIDENCE.md Phase 82 section with extended header row ready for bench write rows

affects:
  - 82-02-PLAN (the first bench task — depends on gen_test_image.py + EVIDENCE schema)
  - 82-03-PLAN (same)
  - 84-PLAN (EVIDENCE.json is the input to the decode-correctness audit)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Deterministic pseudo-random image: random.Random(seed).randint(0,255) for size_bytes iterations"
    - "Image storage convention: /tmp/firestarter_bench_p82/<chip>_img_{A,B}.bin (seed=1/2)"
    - "SHA-256 printed to stdout by CLI — becomes the EVIDENCE oracle value"

key-files:
  created:
    - firestarter_app/tools/gen_test_image.py
    - firestarter_app/tests/test_gen_test_image.py
  modified:
    - .planning/v1.15/bench/EVIDENCE.json
    - .planning/v1.15/bench/EVIDENCE.md

key-decisions:
  - "gen_test_image.py uses random.Random(seed) not /dev/urandom — seed recorded in EVIDENCE enables reproducible SHA oracle (D-03/D-04)"
  - "CLI writes file + prints SHA-256 to stdout; callers record sha256_image_A/B directly from that output"
  - "noqa: E402, I001 on the tools import in test file — tools/ is not a package, sys.path.insert is required before local import"
  - "Pre-existing ruff I001/UP031 errors in tools/audit_coverage_matrix.py + tools/catalog/ are out of scope (not introduced by this plan)"

patterns-established:
  - "A→B write proof: two write-cycle runs per chip (seed=1 then seed=2, no explicit erase between) — clean B SHA proves auto-erase"
  - "EVIDENCE.json evid_extension_columns extended across phases (read_count/blank_check_result + 5 Phase 82 write cols)"

requirements-completed: [EVID-02, EVID-03, DB-01]

# Metrics
duration: 20min
completed: 2026-06-24
---

# Phase 82 Plan 01: Image Generator + SAFE-02 Gate + EVIDENCE Phase 82 Extension Summary

**Deterministic full-size PRNG image generator (random.Random seed), 12 pinning tests, SAFE-02 green (663 tests + 0xA4 guard), and Phase 82 write-column schema added to EVIDENCE without dropping any Phase 81 row**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-06-24
- **Completed:** 2026-06-24
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Created `tools/gen_test_image.py` with `generate_image(size_bytes, seed) -> bytes` using `random.Random(seed)` for reproducibility; CLI prints SHA-256 for direct EVIDENCE recording
- 12 pinning tests: output length, determinism (two-call byte-identical + SHA match), distinct seeds (seed=1 vs seed=2 differ), non-trivial content (not all-0xFF/0x00), CLI smoke test
- SAFE-02 gate confirmed: 663 tests pass, 0xA4 guard `test_init_phase_data_frames_not_acked` PASS, new files ruff-clean
- EVIDENCE.json `evid_extension_columns` extended with `write_image_seed_A`, `sha256_image_A`, `write_image_seed_B`, `sha256_image_B`, `cr01_risk`; all 11 Phase 81 cells preserved (len==11 assertion green)
- EVIDENCE.md Phase 82 SAFE-02 subsection recorded; new "## Phase 82" section with extended table header ready for Plans 82-02/82-03 bench rows

## Task Commits

Submodule commits (firestarter_app on v1.15-bench-validation-of-operator-inventory):

1. **Task 1: Deterministic image generator + pinning test** — `9bc8914` (feat) — tools/gen_test_image.py + tests/test_gen_test_image.py
2. **Task 1 fix: noqa I001** — `646afae` (fix) — tests/test_gen_test_image.py ruff noqa for sys.path+import pattern

Meta-repo commit (EVIDENCE files on gsd/v1.15-bench-validation-of-operator-inventory):

3. **Task 2: SAFE-02 gate + EVIDENCE Phase 82 column extension** — `4be7566` (feat) — .planning/v1.15/bench/EVIDENCE.{json,md}

## Files Created/Modified

- `/workspaces/firestarter_app/tools/gen_test_image.py` — Deterministic image generator; `generate_image(size_bytes, seed)` + CLI entry point printing SHA-256
- `/workspaces/firestarter_app/tests/test_gen_test_image.py` — 12 pinning tests (size, determinism, distinct seeds, non-trivial, CLI smoke)
- `/workspaces/.planning/v1.15/bench/EVIDENCE.json` — Added 5 Phase 82 evid_extension_columns + phase82 section documenting op values, verdict taxonomy, CR-01 pre-attribution
- `/workspaces/.planning/v1.15/bench/EVIDENCE.md` — Added Phase 82 SAFE-02 gate subsection + "## Phase 82 — Rewritable A→B Write Validation" section with extended table header

## Decisions Made

- Used `random.Random(seed).randint(0, 255)` per element rather than `random.Random(seed).getrandbits(8 * size_bytes)` for straightforward correctness; output is pure Python, no numpy dependency (EVID-02 zero new deps)
- Added `noqa: E402, I001` on the `from gen_test_image import` line in the test — tools/ is not a package, the sys.path.insert before the import is the correct pattern for test access without installing
- Recorded SAFE-02 with 663 tests (651 pre-existing + 12 new) — confirms no regressions from Task 1

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] ruff I001 import-sort error in test file**
- **Found during:** Task 2 SAFE-02 gate run (`ruff check .`)
- **Issue:** `from gen_test_image import` after `sys.path.insert` triggered I001 (import block un-sorted)
- **Fix:** Added `noqa: E402, I001` to the post-path-mutation import line
- **Files modified:** `tests/test_gen_test_image.py`
- **Verification:** `ruff check tests/test_gen_test_image.py` exits 0
- **Committed in:** `646afae` (firestarter_app submodule)

---

**Total deviations:** 1 auto-fixed (Rule 1 — ruff import-sort in new test file)
**Impact on plan:** Minor; fix necessary for ruff-clean compliance. No scope creep.

## Issues Encountered

- Pre-existing ruff errors in `tools/audit_coverage_matrix.py` and `tools/catalog/codegen*.py` (I001/UP031) — not introduced by this plan, out of scope per scope boundary rule. Logged to deferred-items.

## Known Stubs

None — no data stubs introduced. The EVIDENCE Phase 82 table intentionally has an empty body (placeholder row "(bench rows appended by Plans 82-02 / 82-03)") which is correct: it is the scaffold, not a data stub. Plans 82-02/03 will fill it with real bench results.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns beyond `/tmp/firestarter_bench_p82/` temp storage, or schema changes at trust boundaries.

## Next Phase Readiness

- `tools/gen_test_image.py` is ready for Plans 82-02/82-03 to invoke: `python tools/gen_test_image.py <size_bytes> <seed> <output_path>`
- EVIDENCE schema is ready to receive write rows (5 new extension columns declared)
- SAFE-02 is green and recorded — bench sessions can start immediately

---
## Self-Check: PASSED

- FOUND: firestarter_app/tools/gen_test_image.py
- FOUND: firestarter_app/tests/test_gen_test_image.py
- FOUND: .planning/v1.15/bench/EVIDENCE.json
- FOUND: .planning/v1.15/bench/EVIDENCE.md
- FOUND: .planning/phases/82-electrically-rewritable-silicon-validation/82-01-SUMMARY.md
- VERIFIED: submodule commit 9bc8914 (feat: generator + test)
- VERIFIED: submodule commit 646afae (fix: noqa)
- VERIFIED: meta-repo commit 4be7566 (feat: EVIDENCE extension)

---
*Phase: 82-electrically-rewritable-silicon-validation*
*Completed: 2026-06-24*
