---
phase: 86-variant-decode-correct-db-regen
verified: 2026-06-25T00:00:00Z
status: passed
score: 6/6 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: none
  previous_score: n/a
---

# Phase 86: infoic.xml Variant-Field Decode + Correct DB Regen — Verification Report

**Phase Goal:** Decode the `infoic.xml` `variant` field in full (low byte already used for pinout family; crack the previously-undecoded high byte, grounded in minipro source / committed datasheets); rewrite `build_db.py` to classify `electrical.type`/`algorithm`/`pinout` from principled variant-driven decode and DELETE the hand-maintained Rule 1/2/3 override stack; regenerate `chip_database.json`. Host-only. Plus VAR-05: ship 2516 + 2532 first-class via a curated non-upstream supplement passing the same gates, 2516 staying SAFE-04 UNVERIFIED.

**Verified:** 2026-06-25
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
| - | ----- | ------ | -------- |
| 1 | `variant` decoded in full (low + high byte), grounded in minipro source, honest gaps documented | ✓ VERIFIED | `tools/DECODE-NOTES.md` (260 lines): §1 low byte = pinout discriminator; §2 high byte = T56/T76 `algo_number` cited to `minipro database.c#L1918 @ a8efaedc236c...` (full 40-char SHA), full high-byte census table (§2.2), the two collision cells (0x41 FM1608/AT28C64, 0x31 X88C64 — §2.3) proving the high byte is NOT a classifier; honest-gap section present (4 "gap" hits) |
| 2 | `build_db.py` derives type/algorithm/pinout from principled decode; Rule 1/2/3 (incl. WARNING-5) override blocks REMOVED | ✓ VERIFIED | `grep -nvE '^\s*#'` for `Rule 1:|Rule 2 WARNING-5|Rule 3:` in active code returns NOTHING; only doc-comments documenting what `classify()` subsumes remain. Single `classify(type, proto, pm_idx, flags, pinout, mem_size)` (build_db.py L283-368) is the sole classifier, called once at L595 after `resolve_pinout_key`. No Pass-1/Pass-2 `_etype=` override blocks remain. |
| 3 | Regenerated DB resolves FM1608→0x28 + X88C64→EEPROM via general decode; every diff row explained by cited rule; both baselines re-pinned | ✓ VERIFIED | FM1608: algorithm 40 (0x28) / FRAM / DIP28_JEDEC_SRAM_8K (via classify arm 1). X88C64P: electrical.type EEPROM / algo 52 (0x34) / protocol-not-implemented (via classify arm 4b — no special-case). `python tools/diff_db.py` → IDENTITY diff (0 changed, 0 new, 0 missing, exit 0) against re-pinned baseline. `chip_database.baseline.json` byte-identical to generated DB (`diff -q` → IDENTICAL). `dispatch_baseline.json` re-pinned (746 chips, provenance cites Phase 86 / Plan 86-03 / VAR-05 / SHA a8efaedc). |
| 4 | `check_dispatch.py` exits 0 violations on regenerated DB | ✓ VERIFIED | `python tools/check_dispatch.py` → "746 chips scanned; 736 supported; 10 non-dispatchable; 0 non_supported_dispatchable; 0 dispatch regressions; 0 consistency violations" exit 0. The structural 12V-on-no-VPP-pin guard is GREEN with WARNING-5 deleted (D-08 backstop proven). |
| 5 | 11 EVIDENCE chips wire-stable (or flagged); host tooling green (py3.11) | ✓ VERIFIED | `tests/test_variant_decode_evidence_stability.py` PASSES (10 upstream-decoded EVIDENCE chips' algorithm/vpp_mv/pinout match OLD baseline; W27C512 stays 0x07/EEPROM/12000mV; 0 chips moved → no re-bench flag). Full suite: 686 passed, 77.69% coverage (>70 floor). ruff check + ruff format --check clean (CI scope `firestarter/ tests/`). mypy watermark OK (35=35). messages.py/codec.py untouched (no codegen-drift). |
| 6 | 2516 + 2532 ship via curated non-upstream supplement merged post-decode; pass gates; 2516 stays SAFE-04 UNVERIFIED | ✓ VERIFIED | `tools/extra_chips.json` (2 records, each `source: "non-upstream-supplement"` + `datasheet` cite). build_db.py merges post-decode (loop ends L729, merge L754, json.dump L764) — NOT routed through classify(). 2516: algo 0x0B(11)/UV-EPROM/DIP24_2716/25000mV/`verification_status: UNVERIFIED` (v1.15 wire values verbatim — SAFE-04). 2532: DIP24_2532 (non-JEDEC, vpp-pin 21)/UNVERIFIED. Both pass check_dispatch (0 violations) + diff_db EXTRA_CHIPS_SUPPLEMENT rule. `test_extra_chips_supplement.py` green. |

**Score:** 6/6 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `tools/DECODE-NOTES.md` | VAR-01 full variant decode dict, census, pinned SHA, honest gaps, X88C64 rationale | ✓ VERIFIED | 260 lines; both bytes; `database.c#L1918`×3, `algo_number`×8, SHA a8efaedc full; census + collision cells; §4 X88C64 0x34→EEPROM; 2516/2532 cross-ref to 86-04 |
| `tools/build_db.py` | single `classify()` replacing Rule 1/2/3; post-decode supplement merge | ✓ VERIFIED | classify() L283; sole call L595; no active Rule blocks; MINIPRO_XML_URL pinned to SHA (regen byte-identical); supplement merge L732-754 |
| `firestarter/data/chip_database.json` | regenerated correct DB (746 chips) | ✓ VERIFIED | 746 chips; regenerates byte-identically from build_db.py; git-clean |
| `tools/diff_db.py` | VARIANT_DECODE + EXTRA_CHIPS_SUPPLEMENT labels; exit 0 | ✓ VERIFIED | IDENTITY diff vs re-pinned baseline, exit 0 |
| `tools/extra_chips.json` | provenance-cited 2516+2532 supplement | ✓ VERIFIED | 2 records, source marker + datasheet cite + provenance + verification_note each |
| `firestarter/data/pinouts.json` | DIP24_2532 non-JEDEC pinout | ✓ VERIFIED | DIP24_2532 present, vpp-pin [21], 12 addr pins (4KB), non-JEDEC vs DIP24_2732 |
| `tools/baseline/chip_database.baseline.json` | re-pinned to correct DB (incl. supplement) | ✓ VERIFIED | byte-identical to generated DB; contains 2516+2532 |
| `tools/baseline/dispatch_baseline.json` | re-pinned w/ Phase-86 provenance | ✓ VERIFIED | 746 chips; note cites Phase 86 / Plan 86-03 / VAR-05 / SHA a8efaedc |
| `tests/test_build_db_inclusion.py` | FM1608 + X88C64 assertions | ✓ VERIFIED | collected + green |
| `tests/test_variant_decode_evidence_stability.py` | D-09 EVIDENCE wire-stability | ✓ VERIFIED | green; 0 chips moved |
| `tests/test_extra_chips_supplement.py` | VAR-05 supplement assertions | ✓ VERIFIED | green |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| DB regenerates reproducibly | `python tools/build_db.py` + `diff -q` | 746 chips; byte-identical to committed DB; SHA-pinned fetch | ✓ PASS |
| diff_db identity gate | `python tools/diff_db.py` | PASS: 0 changed, 0 new, 0 missing, exit 0 | ✓ PASS |
| dispatch safety gate | `python tools/check_dispatch.py` | 0 dispatch regressions; 0 consistency violations, exit 0 | ✓ PASS |
| oracle tests | `pytest test_build_db_inclusion test_variant_decode_evidence_stability test_extra_chips_supplement test_diff_db_gate` | 34 passed | ✓ PASS |
| full suite + coverage | `pytest tests/ --cov-fail-under=70` | 686 passed, 77.69% | ✓ PASS |
| lint (CI py3.11 scope) | `ruff check` + `ruff format --check firestarter/ tests/` | clean | ✓ PASS |
| mypy watermark | `python tools/check_mypy_watermark.py` | 35=35 watermark, OK | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
| ----------- | ----------- | ------ | -------- |
| VAR-01 | 86-01 | ✓ SATISFIED | DECODE-NOTES.md documents the variant field in full (low + high byte = algo_number) with minipro database.c#L1918 grounding and a pinned 40-char SHA + honest gaps. **NOTE: REQUIREMENTS.md still marks this "In Progress"** — the doc deliverable is in fact complete; traceability table is stale (see Findings). |
| VAR-02 | 86-02 | ✓ SATISFIED | Rule 1/2/3 deleted from active code; single classify() is sole classifier |
| VAR-03 | 86-02, 86-04, 86-03 | ✓ SATISFIED | FM1608→0x28, X88C64→EEPROM via general decode; diff_db identity exit 0; both baselines re-pinned |
| VAR-04 | 86-02, 86-03 | ✓ SATISFIED | check_dispatch 0 violations; EVIDENCE-11 wire-stable (0 moved); py3.11 toolchain green |
| VAR-05 | 86-04 | ✓ SATISFIED | extra_chips.json 2516+2532 merged post-decode; pass check_dispatch + diff_db; 2516 UNVERIFIED |
| SAFE-04 | 86-03, 86-04 | ✓ SATISFIED | No write path / host guard touched; 2516 UNVERIFIED + wire values verbatim from v1.15 |
| SAFE-03 (cross-cutting, homed Phase 86 recurring) | supporting | ✓ SUPPORTING | diff_db every-row-explained (now identity) + check_dispatch 0 every-phase posture established |
| SAFE-06 (cross-cutting, homed Phase 87) | supporting | ✓ SUPPORTING | host-only; py3.11 CI scope validated; messages.py never touched |

No orphaned requirements — all VAR/SAFE IDs mapped to plan frontmatter are accounted for.

### Anti-Patterns Found

| File | Pattern | Severity | Impact |
| ---- | ------- | -------- | ------ |
| (none) | no TBD/FIXME/XXX debt markers in any phase-modified file | — | none |

The `variant-decode-diff.txt` transcript shows "72 changed / 2 new" — this is the **pre-re-pin review artifact** (the captured diff vs the OLD baseline that Plan 86-03 reviewed before re-pinning), NOT a live gate failure. The live `diff_db.py` run is IDENTITY (0 changed). Correct by design.

### Human Verification Required

None. All six success criteria are verifiable in the codebase and were independently re-run green by the verifier. The D-09 EVIDENCE wire-stability gate was satisfied software-side (0 chips moved → no Leonardo/Rev2.0 re-bench flag was raised, so no hardware verification is gated within this phase). 2516 stays UNVERIFIED by design (its write graduation is FUT-03, out of scope).

### Gaps Summary

No gaps. The phase goal is achieved in the codebase:
- The variant field is decoded in full and documented with minipro grounding + a pinned SHA.
- The Rule 1/2/3 override stack is genuinely deleted from active code; `classify()` is the sole principled classifier.
- FM1608 (0x28/FRAM) and X88C64 (EEPROM/0x34) fall out of the general decode with no special-case.
- The regenerated DB is reproducible, the diff_db gate is IDENTITY (exit 0), check_dispatch is 0 violations, and both baselines are re-pinned with correct provenance.
- 2516 + 2532 ship first-class via the post-decode non-upstream supplement, pass all gates, and 2516 retains its SAFE-04 UNVERIFIED status with wire values unmoved.
- Host-only scope honored (no firmware, no host guards, no messages.py/codec.py touched); full py3.11 toolchain green.

**Minor documentation observation (non-blocking):** REQUIREMENTS.md traceability still lists VAR-01 as "In Progress (... classifier application is 86-02)". The classifier application (86-02) is complete and the VAR-01 *documentation* deliverable (DECODE-NOTES.md) is fully present and substantive. The "In Progress" label is stale — VAR-01 is functionally Complete. This is a planning-doc bookkeeping lag, not a codebase gap; it does not block the phase goal. Recommend flipping VAR-01 to Complete in REQUIREMENTS.md.

---

_Verified: 2026-06-25_
_Verifier: Claude (gsd-verifier)_
