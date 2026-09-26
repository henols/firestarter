---
phase: 52-lockstep-contract-round-trip-tests
plan: "01"
subsystem: test-infrastructure
tags: [golden-vectors, codegen, cobs, drift-gate, ci, lockstep]
dependency_graph:
  requires: []
  provides: [frame-vectors-catalog, codegen-vectors, frame_vectors.h, frame_vectors.py, ci-drift-gates]
  affects: [firestarter/include, firestarter/tools/catalog, firestarter_app/firestarter, firestarter_app/tools/catalog, ci-both-repos]
tech_stack:
  added: [frame-vectors.toml (TOML catalog), codegen_vectors.py (Python 3.11 codegen)]
  patterns: [LCAT-05 determinism contract, D-04/D-09 paired-commit vendoring, per-repo CI drift gate]
key_files:
  created:
    - firestarter/tools/catalog/frame-vectors.toml
    - firestarter/tools/catalog/codegen_vectors.py
    - firestarter/include/frame_vectors.h
    - firestarter_app/tools/catalog/frame-vectors.toml
    - firestarter_app/tools/catalog/codegen_vectors.py
    - firestarter_app/firestarter/frame_vectors.py
  modified:
    - firestarter/.github/workflows/build.yml
    - firestarter_app/.github/workflows/ci.yml
decisions:
  - "Separate codegen_vectors.py (not extending codegen.py) to avoid entangling [[messages]] validator with [[vectors]] schema (RESEARCH Open Q3 / Pitfall 6)"
  - "VECTOR_NAME_RE relaxed to VEC_[A-Z0-9][A-Z0-9_]* to accommodate VEC_512_* / VEC_1024_* corpus names"
metrics:
  duration: 25m
  completed: "2026-06-02"
  tasks: 3
  files: 8
---

# Phase 52 Plan 01: Golden Vector Catalog + Codegen + CI Drift Gates Summary

Authored the canonical golden-vector catalog (`frame-vectors.toml`) with the full D-05 corpus, implemented a deterministic separate codegen script (`codegen_vectors.py`), vendored both byte-identically into both sub-repos, generated the C++ PROGMEM header and Python module, and wired vector catalog validity + codegen drift-gate steps into both repos' CI.

## Tasks Completed

| Task | Name | Commit (fw) | Commit (app) | Files |
|------|------|-------------|--------------|-------|
| 1 | Author canonical frame-vectors.toml + codegen_vectors.py + generate frame_vectors.h | 16ea222 | — | 3 files (fw) |
| 2 | Vendor catalog + codegen byte-identically; generate frame_vectors.py | — | 57ebe17 | 3 files (app) |
| 3 | Add vector-catalog validity + codegen drift-gate steps to both CI | 8379c9c | dd75775 | 2 files (1 per repo) |

## Acceptance Criteria Verification

- `codegen_vectors.py --check` exits 0, prints "OK: catalog valid (12 vectors, version 1)." — PASS (both repos)
- Re-running cpp-vectors emit: `git diff --exit-code include/frame_vectors.h` clean — PASS
- Re-running python-vectors emit: `git diff --exit-code firestarter/frame_vectors.py` clean — PASS
- `include/frame_vectors.h` contains `FRAME_VECTORS`, `FRAME_VECTOR_COUNT`, row for VEC_RUN_254 — PASS
- Catalog contains all 12 D-05 vectors incl. VEC_RUN_253/254/255 — PASS
- VEC_JSON_STATE13 payload `{"state":13}`, frame_len=15, CRC8=0x19 — PASS (verified by codegen)
- No vector `frame_hex` includes a leading `#` (0x23) byte — PASS (Pitfall 2 avoided)
- Banner contains no timestamp/hostname; hex literals upper-case 2-digit — PASS (LCAT-05)
- `diff frame-vectors.toml` between repos: empty (byte-identical, D-09) — PASS
- `diff codegen_vectors.py` between repos: empty (byte-identical, D-09) — PASS
- `from firestarter.frame_vectors import FRAME_VECTORS` imports; VEC_RUN_254 present; every `.frame` ends in 0x00 — PASS
- Both CI workflows contain vector validity + drift-gate steps — PASS

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] VECTOR_NAME_RE relaxed to accept digit-starting suffixes**
- **Found during:** Task 1 — codegen --check rejected VEC_512_ALL_FF (first char after VEC_ is '5')
- **Issue:** Plan specified `VEC_[A-Z][A-Z0-9_]*` but D-05 corpus names VEC_512_ALL_FF / VEC_1024_ALL_FF / VEC_512_ALL_ZERO / VEC_1024_ALL_ZERO start with a digit after VEC_
- **Fix:** Relaxed to `VEC_[A-Z0-9][A-Z0-9_]*` — preserves the intent (VEC_ prefix + alphanumeric body) while accommodating the corpus names mandated by the plan itself
- **Files modified:** firestarter/tools/catalog/codegen_vectors.py (vendored copy in firestarter_app is byte-identical)
- **Commit:** 16ea222

## Known Stubs

None — all 12 vectors have hardcoded frozen byte literals. No placeholder or empty values flow to any output.

## Threat Flags

No new production network endpoints, auth paths, or trust-boundary schema changes introduced. This plan touches only test-infrastructure files (catalog, codegen, generated artifacts, CI steps). T-52-01 through T-52-SC are fully mitigated as documented in the plan's threat model.

## Self-Check: PASSED

Files created/exist:
- FOUND: firestarter/tools/catalog/frame-vectors.toml
- FOUND: firestarter/tools/catalog/codegen_vectors.py
- FOUND: firestarter/include/frame_vectors.h
- FOUND: firestarter_app/tools/catalog/frame-vectors.toml
- FOUND: firestarter_app/tools/catalog/codegen_vectors.py
- FOUND: firestarter_app/firestarter/frame_vectors.py

Commits exist:
- FOUND: 16ea222 (firestarter — Task 1)
- FOUND: 57ebe17 (firestarter_app — Task 2)
- FOUND: 8379c9c (firestarter — Task 3)
- FOUND: dd75775 (firestarter_app — Task 3)
