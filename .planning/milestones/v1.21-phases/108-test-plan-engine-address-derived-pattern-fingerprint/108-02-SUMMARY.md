---
phase: 108-test-plan-engine-address-derived-pattern-fingerprint
plan: 02
subsystem: testing
tags: [python, address-derived-pattern, fingerprint-classifier, xor-fold, chip-validation]

# Dependency graph
requires:
  - phase: 108-01
    provides: EpromOperationError.error_code seam (RPT-03/D-07) threaded through _raise_for_error_response
provides:
  - "address_fold_byte(addr) -> int: XOR-fold of A0..A31 into one expected byte (D-01)"
  - "generate_pattern(start, length) -> bytes: region-parameterized address-derived pattern (D-02)"
  - "prepass_images(length) -> (bytes, bytes): cheap all-0x00/all-0xFF sanity images"
  - "_diff_offsets(expected, actual): shared byte-diff-offset primitive mirroring consistency_check_eprom (D-04)"
  - "classify_fingerprint(expected, actual, *, repeat_divergent=None, addr_base=0) -> Fingerprint: 4-bucket classifier (D-03)"
  - "Fingerprint dataclass (total, bad, bad_pct, classification, evidence)"
  - "four locked outcome labels: blank/contact, address-line, transport, indeterminate"
affects: [108-03-derive_plan, 108-04-run_plan, 110-diagnostic-report]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pure compute module (no serial I/O, no VPP, no wire dict) unit-tested with hand-built byte arrays"
    - "Reuse-not-reimplement: divergence math copied verbatim from consistency_check_eprom rather than imported, keeping chip_test.py import-light"
    - "Locked classification order with an honest indeterminate fallback -- never coerce an ambiguous signal into a confident label"

key-files:
  created:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_chip_test.py
  modified: []

key-decisions:
  - "Restricted address-line candidate bits to 8 <= k < (cmp_len-1).bit_length() -- bits at or above the compared region's size never toggle within [0, cmp_len) and would spuriously score 100% clustering (always-clear), producing a false address-line verdict on scattered data."
  - "blank/contact check runs on ff_ratio over actual bytes regardless of bad-mismatch count, so a near-all-0xFF read-back is caught even when every byte differs from the expected pattern (contact fault, not just a partial one)."
  - "Threshold constants (_FF_RATIO_THRESHOLD=0.98, _BIT_CLUSTER_THRESHOLD=0.9) declared as module-level tunables per D-04 (direction locked, exact numbers Claude's discretion / bench-tunable later)."

patterns-established:
  - "Region-parameterized pure pattern generator: generate_pattern(start, length) derives every byte from its ABSOLUTE address, so the same function serves a full-chip pattern or Phase 109's UV small-region write cap with no code change."

requirements-completed: [PATT-01, PATT-02]

coverage:
  - id: D1
    description: "Address-derived XOR-fold pattern generator (address_fold_byte, generate_pattern) is region-parameterized on absolute address, exposing stuck/shorted/aliased address lines"
    requirement: "PATT-01"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py::test_address_fold_byte_zero"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py::test_address_fold_byte_high_bit_folds"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py::test_generate_pattern_region_parameterized"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py::test_generate_pattern_high_base_differs"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py::test_prepass_images"
        status: pass
    human_judgment: false
  - id: D2
    description: "Four-bucket byte-mismatch fingerprint classifier (classify_fingerprint) reusing the shared divergence primitive, with an honest indeterminate fallback that never coerces an ambiguous distribution"
    requirement: "PATT-02"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py::test_fp_blank_near_all_ff"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py::test_fp_address_line_bit_a8"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py::test_fp_address_line_absolute_addr_base"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py::test_fp_transport_scattered_repeatable"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py::test_fp_indeterminate_ambiguous"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py::test_fingerprint_evidence_fields"
        status: pass
    human_judgment: false
  - id: D3
    description: "Shared byte-diff-offset helper (_diff_offsets) mirrors consistency_check_eprom's divergence math verbatim -- no parallel implementation (D-04)"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py::test_diff_offsets_equal_arrays"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py::test_diff_offsets_known_positions"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py::test_diff_offsets_unequal_length"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-07-02
status: complete
---

# Phase 108 Plan 02: Address-Derived Pattern + Fingerprint Classifier Summary

**Greenfield `chip_test.py` module: XOR-fold address-derived pattern generator (region-parameterized) plus a four-bucket byte-mismatch fingerprint classifier that reuses `consistency_check_eprom`'s divergence math and never over-confidently coerces an ambiguous distribution into a false diagnosis.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-07-02T17:46:48Z
- **Completed:** 2026-07-02T17:56:22Z
- **Tasks:** 3
- **Files modified:** 2 (both new)

## Accomplishments
- `address_fold_byte(addr)` / `generate_pattern(start, length)` / `prepass_images(length)` — a region-parameterized, address-derived write/verify pattern where every address line (A0..A31) contributes to the expected byte via XOR-fold, so stuck/shorted/aliased address lines are exposed instead of hidden (unlike a fixed pattern).
- `_diff_offsets(expected, actual)` — the single shared byte-diff-offset primitive, mirroring `consistency_check_eprom`'s exact divergence math (`eprom_operations.py:842-863`) verbatim, consumed by the classifier with zero parallel implementation.
- `classify_fingerprint(expected, actual, *, repeat_divergent=None, addr_base=0) -> Fingerprint` — a four-bucket classifier in locked order (blank/contact → address-line → transport → indeterminate), naming the suspected address line by absolute address (`addr_base + offset`) and carrying the raw evidence (`ff_ratio`, per-bit clustering scores, `repeat_divergent`, `first_offset`) so Phase 110's report can show why.
- 14 new unit tests, all passing, covering PATT-01/02 with hand-built byte arrays — no serial I/O, no hardware.

## Task Commits

Each task was committed atomically inside the `firestarter_app/` submodule (branch `v1.21-community-chip-validation-command`):

1. **Task 1: Address-derived pattern generator + pre-pass images** - `20fe3e2` (test)
2. **Task 2: Shared byte-diff-offset helper (reuse consistency divergence math)** - `6acf424` (test)
3. **Task 3: Four-bucket fingerprint classifier + Fingerprint record + tests** - `b3b3bb3` (feat)

**Plan metadata:** (this SUMMARY commit, meta repo)

_Note: all three tasks were TDD-flagged; since the module was authored as one coherent unit, each task's commit contains the incremental slice of `chip_test.py` + `test_chip_test.py` that task's `<verify>`/`<acceptance_criteria>` block exercises (verified independently before each commit by running that task's exact test selector against the file state at that point in history)._

## Files Created/Modified
- `firestarter_app/firestarter/chip_test.py` - new module: `address_fold_byte`, `generate_pattern`, `prepass_images`, `_diff_offsets`, `FP_*` label constants, `Fingerprint` dataclass, `classify_fingerprint`
- `firestarter_app/tests/test_chip_test.py` - new test file: 14 tests covering pattern generation, the shared diff helper, and all four fingerprint buckets

## Decisions Made
- Restricted address-line candidate bits to `8 <= k < (cmp_len-1).bit_length()`. Bits at or above the compared region's size never toggle within `[0, cmp_len)`, so including them would spuriously score 100% clustering on the always-clear polarity — this surfaced while designing the `transport`/`indeterminate` test fixtures (a naive `8..log2(total)` inclusive range produced a false `address-line` verdict on scattered data whenever `total` was a power of two).
- The `blank/contact` check evaluates `ff_ratio` over `actual` bytes independent of the mismatch count, so a near-all-0xFF read-back is caught even in the degenerate case where every compared byte differs from the expected pattern (a genuine contact fault, not a partial one).
- Threshold constants (`_FF_RATIO_THRESHOLD = 0.98`, `_BIT_CLUSTER_THRESHOLD = 0.9`) are declared as module-level tunables directly above the classifier per D-04 — direction is locked, exact numbers are Claude's discretion and bench-tunable later; a wrong number only produces more `indeterminate`, never a false confident label.

## Deviations from Plan

None - plan executed exactly as written. No architectural changes, no missing-critical-functionality gaps, no blocking issues beyond the internal test-fixture bit-range refinement documented above (which is design-time test correctness, not a deviation from the plan's specified behavior).

## Issues Encountered

One pre-existing, out-of-scope test failure was observed when running the full `firestarter_app` suite: `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` fails on a clean checkout with none of this plan's changes applied (confirmed via `git stash`). This is the golden-fixture drift already tracked in STATE.md (surfaced at Phase 106-01, unrelated to `chip_test.py`/`chip_resolver.py`/dispatch). Not touched — out of this plan's scope per the scope-boundary rule.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `chip_test.py` now has its pure compute layer (address-derived pattern + fingerprint classifier) ready for Plans 108-03 (`derive_plan`) and 108-04 (`run_plan`) to extend with the orchestration engine in the same module, same submodule branch.
- The `Fingerprint.evidence` dict shape (`ff_ratio`, `bit_clustering`, `repeat_divergent`, `first_offset`, `suspected_line`/`cluster_score` when address-line) is stable and ready for Phase 110's diagnostic report to consume.
- No blockers.

---
*Phase: 108-test-plan-engine-address-derived-pattern-fingerprint*
*Completed: 2026-07-02*

## Self-Check: PASSED

- FOUND: firestarter_app/firestarter/chip_test.py
- FOUND: firestarter_app/tests/test_chip_test.py
- FOUND: .planning/phases/108-test-plan-engine-address-derived-pattern-fingerprint/108-02-SUMMARY.md
- FOUND (firestarter_app submodule): 20fe3e2, 6acf424, b3b3bb3
- FOUND (meta repo): 9b91938
