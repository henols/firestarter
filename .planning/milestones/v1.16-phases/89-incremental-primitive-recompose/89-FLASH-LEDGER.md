# Phase 89 Flash Ledger — PRIM-06 Deliverable

**Phase:** 89-incremental-primitive-recompose
**Generated:** 2026-06-26
**Baseline ref:** `firestarter/.flash-baseline-87.txt` = 25654 B (89.5%)

---

## Step Ledger: P7 → P4 → P3 → P5

| Step | Primitive | Pre (B) | Post (B) | Delta (B) | Flash % | Disposition |
|------|-----------|---------|----------|-----------|---------|-------------|
| Baseline (Phase 88 close) | — | — | 25654 | — | 89.5% | Reference (firestarter@e6cce3e) |
| P7 (89-01) | SDP / const-table dedup (PRIM-02) | 25654 | 25654 | 0 | 89.5% | **Committed** — firestarter@0052c42 |
| P4 (89-02) | chip_id_report (PRIM-03) | 25654 | 25490 | −164 | 88.9% | **Committed** — firestarter@a10871d |
| P3 (89-03) | vpp_check_window (PRIM-04) | 25490 | 25088 | −402 | 87.5% | **Committed** — firestarter@a52fd0a |
| P5 (89-04) | poll_readback (PRIM-05) | 25088 | 25090 | +2 | 87.5% | **Committed** — firestarter@abbbb5c |
| CR-01 fix (post-phase) | chip_id_report caller-keyed `force_warning` + WR-02 tests | 25090 | 25136 | +46 | 87.7% | **Committed** — firestarter@a296195 |

**Phase HEAD is firestarter@a296195 (post CR-01 fix), not abbbb5c.** The code-review gate found CR-01 (eprom CHECK_CHIP_ID mismatch silently downgraded ERROR→WARNING under `--force`); the fix restored unconditional ERROR via an explicit `force_warning` keying argument and added 3 WR-02 mismatch-fork tests. It costs +46 B; the phase-cumulative result remains a net decrease (−518 B).

**D-02 deferral (operator-accepted 2026-06-26):** ROADMAP SC#4 lists a third `poll_readback` site — the verify-readback half of `eprom_write_execute` (`verify_and_update_mask`). It was intentionally NOT routed through `poll_readback`: it is a different algorithm (whole-buffer bitmask, returns a count, no timeout frame / no error MSG), so sharing the single-address poll kernel would change behavior. Deferred by design; see 89-04-SUMMARY.md.

---

## Final flash (PRIM-06)

| Metric | Value |
|--------|-------|
| Baseline (Phase 88) | 25654 B — 89.5% of 28672 B |
| Final (Phase 89 HEAD: firestarter@a296195, incl. CR-01 fix) | **25136 B — 87.7% of 28672 B** |
| Phase-cumulative delta | **−518 B** |
| D-01 net-decrease assertion | **PASS** — 25136 < 25654 |

**Build evidence:**

```
Flash: [========= ]  87.7% (used 25136 bytes from 28672 bytes)
========================= [SUCCESS]
```

(Measured: `cd firestarter && pio run -e leonardo`, 2026-06-26, HEAD = a296195. Pre-CR-01-fix snapshot at abbbb5c was 25090 B / 87.5% / −564 B.)

---

## Per-Primitive Disposition

| Primitive | Code | Files | Saved | Gate | D-02? |
|-----------|------|-------|-------|------|-------|
| P7 — SDP const-table dedup | PRIM-02 | flash_utils.h, eeprom_28c.cpp | 0 B (warm-up / dedup only) | D-01 PASS (0 B ≤ +16 B) | No |
| P4 — chip_id_report | PRIM-03 | primitives.h (new), primitives.cpp (new), flash_utils.cpp, eprom.cpp, eeprom_28c.cpp, flash_intel.cpp | −164 B | D-01 PASS | No |
| P3 — vpp_check_window | PRIM-04 | primitives.h, primitives.cpp, eprom.cpp, flash_intel.cpp | −402 B (biggest single saving) | D-01 PASS | No |
| P5 — poll_readback | PRIM-05 | primitives.h, primitives.cpp, eeprom_28c.cpp, flash_type_4.cpp | +2 B (call overhead; loop body too small for AVR cross-TU dedup) | D-01 PASS (+2 B ≤ +16 B) | No |

---

## Final Gate Results

### Frozen-World Gates

| Gate | Result | Detail |
|------|--------|--------|
| `pio test -e native` (full suite) | **PASS** | 105/105 tests green (14 suites; +3 WR-02 mismatch-fork tests from CR-01 fix) |
| `check_dispatch.py` | **PASS** | Exit 0; 746 chips scanned, 736 supported, 0 dispatch regressions, 0 consistency violations |
| `diff_db.py` | **PASS** | Exit 0; 0 changed / 0 new / 0 missing (identity diff) |
| `git -C firestarter_app diff --quiet` (source) | **PASS** | Only change = pre-existing `.gitignore` annotation (`consistency*`); not a source/tool/test file, predates Phase 89, not caused by any Phase 89 extraction. Source gate clean (SAFE-06). |
| D-01 net-decrease (final < 25654 B) | **PASS** | 25090 B < 25654 B (−564 B) |

### INV Greppability (SAFE-02)

Each INV-id greps `firestarter/doc/ firestarter/src/ firestarter/test/`:

| INV | Files | Result |
|-----|-------|--------|
| INV-01 | 9 | PASS ≥ 3 |
| INV-02 | 3 | PASS ≥ 3 |
| INV-03 | 6 | PASS ≥ 3 |
| INV-04 | 4 | PASS ≥ 3 |
| INV-05 | 3 | PASS ≥ 3 |
| INV-06 | 3 | PASS ≥ 3 |
| INV-07 | 3 | PASS ≥ 3 |
| INV-08 | 3 | PASS ≥ 3 |
| INV-09 | 5 | PASS ≥ 3 |

All 9 INV ids ≥ 3 files.

### SAFE-04 Safety-Posture Verification

| Check | Location | Result |
|-------|----------|--------|
| Over-voltage HIGH check `vpp_mv > (uint32_t)handle->vpp_mv + 500` | `firestarter/src/proms/primitives.cpp:98` (inside `vpp_check_window`) | **PRESENT + UNMODIFIED** — threshold + FORCE/ERROR semantics byte-identical (moved from handlers to shared primitive in P3; behavior unchanged, now in one place) |
| `chip_resolver.resolve_chip` host guard | `firestarter_app/firestarter/chip_resolver.py:16` | **PRESENT + UNCHANGED** — `git -C firestarter_app diff --quiet` confirms no host source edit (SAFE-06) |
| 2516 UNVERIFIED status | `firestarter_app/firestarter/data/chip_database.json` | **UNVERIFIED** — `verification_status=UNVERIFIED, support_status=supported`; no write-graduation this phase (SAFE-04 / D-08) |

---

## Summary

Phase 89 closes PRIM-06 with a **−518 B net decrease** (89.5% → 87.7%) across 4 committed primitives plus the post-phase CR-01 fix. All four extractions (P7/P4/P3/P5) achieved zero-diff golden traces. The +2 B P5 cost is the expected call-overhead for a small loop body on an AVR architecture that does not inline across translation units; the +46 B CR-01 fix restores a behavior the golden traces could not catch and adds 3 regression-guard tests. Both are well within scope; the phase-cumulative result is a strong net-decrease.

One D-02 deferral (operator-accepted 2026-06-26): ROADMAP SC#4's third `poll_readback` site (`eprom_write_execute` verify) is a different algorithm and was intentionally not shared — see 89-04-SUMMARY.md.

Frozen-world contract: `check_dispatch.py` 0 violations, `diff_db.py` identity diff, all 9 INV ids ≥ 3 files, host source untouched. Electrical safety posture (SAFE-04/D-08) intact.

**Phase 89: COMPLETE.**
