---
phase: 151-protection-readability-lock-status
plan: 07
subsystem: docs+host-tests
tags: [data-06, protect-flags, infoic-field-dictionary, doc-db-invariant]
dependency-graph:
  requires: [151-01]
  provides: [DATA-06 documented-once advisory statement, protect flags doc/DB invariant test]
  affects: [firestarter_app/doc/infoic-field-dictionary.md, firestarter_app/doc/package-details.md, firestarter_app/doc/protocol-flags.md]
tech-stack:
  added: [firestarter_app/tests/test_protect_flags_doc_measurements.py]
  patterns: [doc-figures-parsed-and-compared-to-recomputed-db, ast+tokenize-source-scan-for-runtime-consumer]
key-files:
  created:
    - firestarter_app/tests/test_protect_flags_doc_measurements.py
  modified:
    - firestarter_app/doc/infoic-field-dictionary.md
    - firestarter_app/doc/package-details.md
    - firestarter_app/doc/protocol-flags.md
    - .planning/todos/completed/decode-infoic-flags-bits-14-15-protect-metadata.md (moved from pending/)
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/STATE.md
decisions:
  - "Leg 4 generalized to an ast+tokenize structural scan (comment-or-docstring vs. executable code) rather than the plan's literal 'exactly one allowed file' check, because same-phase Plan 151-06 had already landed a second prose-only file by execution time."
metrics:
  duration: ~30min
  completed: 2026-08-20
status: complete
---

# Phase 151 Plan 07: DATA-06 — `protect_on_after` / `protect_off_before` documented once Summary

One authoritative section in `doc/infoic-field-dictionary.md` states both flags-bit-14/15 fields' measured distributions, the algorithm-13 promotion split, and the enumerated absence of any runtime consumer — proven equal to the committed `chip_database.json` by a new Python test, since a markdown-only commit fires no host CI.

## What Was Built

**Task 1 — the authoritative section (`firestarter_app/doc/infoic-field-dictionary.md`).** Added `### protect_off_before / protect_on_after (flags bits 14/15) — DECODE CONFIRMED; NO RUNTIME CONSUMER`, covering both sibling fields in one place:
- What the bits are: bit 14 `MP_OFF_PROTECT_BEFORE` (unprotect before write, gates minipro `-u`), bit 15 `MP_PROTECT_AFTER` (re-protect after write, gates minipro `-P`) — stated explicitly as a **capability, not a policy**.
- The measurement: `protect_on_after` true on 70 of 746 (674 false, 2 absent), algorithm 5 → 27 of 27 (constant), algorithm 13 → 43. `protect_off_before` true on 148 of 746 (596 false, 2 absent), algorithm 5 → 27 of 27, 6 → 77 of 190, 13 → 43 of 84, 52 → 1 of 1. 744 of 746 rows carry both keys; the two exceptions (`TEXAS INSTRUMENTS` `2516`/`2532`) raise `KeyError` on a direct index.
- The promotion split: algorithm 13's 84 rows are 18 upstream-native + 66 promoted; `protect_on_after`/`protect_off_before` are both true on 18 of 18 native and 25 of 66 promoted (18+25=43) — stated instead of the bare, misleading "43 of 84".
- The enumerated absence of a runtime consumer (Backlog 999.28), citing `tests/test_sdp_db_invariant.py::test_sdp_partition_matches_infoic_derived_field_element_wise` by full node id.
- The algorithm-6 correlation (77 of 190) framed as suggestive and explicitly non-derivable, restating the `W29C020C`/`W29EE011` flag-identity negative result.
- A four-item non-claims list.

Also corrected the stale `page_size` entry's "Not currently stored in `chip_database.json`" sentence with a dated, measured correction (20 rows carry `page_size`, 744 carry `infoic_page_size_raw`).

**Task 2 — one-line pointers.** `doc/package-details.md` and `doc/protocol-flags.md` each gained exactly one line pointing at the new section, sharing a 312-character verbatim substring (well over the required 40), restating no figure.

**Task 3 — `tests/test_protect_flags_doc_measurements.py` (10 legs) + folded todo.** Parses the doc's own stated figures via pre-compiled regex and compares them to a fresh recomputation against the committed `chip_database.json`; proves the `.get(...)` discipline is justified (direct index raises on the two exception rows); proves the 18/18+25/66 promotion split and the algorithm-6 sentence; proves no executable code under `firestarter_app/firestarter/` reads either field via an `ast`+`tokenize` source scan; proves "documented once" (one heading, one pointer per file, no restated figures); guards `sdp_capability.py` untouched; and proves the comparison machinery itself is non-vacuous via a synthetic moved-chip control.

Moved `.planning/todos/pending/decode-infoic-flags-bits-14-15-protect-metadata.md` to `completed/` (git mv) with a dated resolution block answering its own Cross-check note.

**DATA-06 flipped** — checkbox and traceability row in `REQUIREMENTS.md` and `ROADMAP.md`, exclusively (LOCK-01…04 untouched).

## Observed Failure/Fixture Messages (per plan `<output>` spec)

**Leg 1, temporarily altering `protect_on_after`'s headline figure from 70 to 71:**
```
AssertionError: doc states protect_on_after true=71 of 746, false=674; measured true=70 of 746, false=674.
assert (71, 746, 674) == (70, 746, 674)
```
The doc was restored immediately after (verified via `git diff --stat` returning empty for that file before the real commit).

**Leg 7, fixture setup and mismatch-naming (synthetic moved-chip non-vacuity control):**
- Fixture setup assertions (both passed silently, so no `Fixture setup error: ...` was actually raised — they exist as guards, not as observed failures): `allow_before == ["SYNTHETIC_MFR/MOVED_CHIP"]` and `refuse_before == ["SYNTHETIC_MFR/CONTROL_CHIP"]`.
- The mismatch-naming assertion **was** observed to raise, with message:
```
'before' and 'after' protect_on_after partitions disagree. Only in 'before': ['SYNTHETIC_MFR/MOVED_CHIP']. Only in 'after': [].
```
Confirmed it names `MOVED_CHIP` and not `CONTROL_CHIP`.

## Shared Pointer Substring (Task 2)

```
**Note on bits 14/15:** the row above documents minipro's *bit* semantics only; what the emitted `protect_off_before` / `protect_on_after` database fields mean at runtime, and their measured distributions, is [documented once in `infoic-field-dictionary.md`](infoic-field-dictionary.md#protect-flags-bits-14-15).
```
(312 characters, present verbatim in both `package-details.md` and `protocol-flags.md`.)

## Known-Bugs Summary Table Conclusion

No row is owed in `## Summary: build_db.py Known Bugs vs Correct Semantics`. The decode of bits 14/15 (`flags & 0x4000` / `flags & 0x8000`) is correct and matches the `MP_*` constants exactly — this is a documentation gap this plan closes, not a decode defect (`BUG-N`).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 — stale plan premise] Leg 4's "exactly one allowed file" assumption no longer held**
- **Found during:** Task 3, leg 4 (source scan for a runtime consumer)
- **Issue:** The plan's action text assumed the only in-package prose occurrence of either field name was `sdp_capability.py:74`. By the time this plan executed, same-phase Plan 151-06 (wave 1) had already landed `firestarter/protection_readability.py`, which added two more occurrences: a provenance comment at `:163` and a docstring note at `:238` (the latter explicitly stating that no branch in that module reads either field). A literal "exactly one allowed file" check would therefore fail on arrival through no fault of the current DB or code.
- **Fix:** Implemented leg 4 structurally instead of via a hardcoded file allowlist: it parses every `.py` file under `firestarter_app/firestarter/` with `ast` + `tokenize`, computes which line numbers are comment or docstring text, and fails naming any occurrence of either field name that falls outside that prose set (i.e. any occurrence that would be executable code). This proves the actual D-16 invariant ("no runtime consumer") regardless of how many prose-only files exist, and does not need updating every time a comment moves or a new prose mention is added elsewhere.
- **Files modified:** `firestarter_app/tests/test_protect_flags_doc_measurements.py`
- **Commit:** `63ca353` (firestarter_app)

**2. [Rule 3 — stale plan premise] `page_size` grep-count acceptance criterion's stale "before" count**
- **Found during:** Task 1, verifying the `page_size` stale-sentence correction
- **Issue:** The plan's acceptance criteria assumed `grep -c 'Not currently stored in .chip_database.json.'` measured `2` before this task's edit (dropping to `1` after, leaving only the `chip_info` entry's identical sentence). Measured directly: the count was actually `3` before this task (the `page_size`, `chip_info`, **and** `blank_value` entries all carry the identical sentence) and is `2` after — the `blank_value` entry's stale-looking sentence was not named in this plan's action text (which explicitly says "Change nothing else in the `page_size` entry" and does not authorize touching `chip_info` or `blank_value`), so it was left untouched.
- **Fix:** No fix applied — this is an observation about the plan's stale premise, not a defect in the executed work. Only the `page_size` entry was corrected, per the plan's explicit scope. The `chip_info` and `blank_value` entries' claims were not independently re-measured against the DB in this plan and remain as-is; a future plan revisiting `infoic-field-dictionary.md`'s other "Not currently stored" claims should re-measure them before editing.
- **Files modified:** none (documentation-only observation)
- **Commit:** N/A

## Verification Results

- `pytest tests/test_protect_flags_doc_measurements.py -x -o addopts=""` — **10 passed** (plan required ≥7).
- `pytest tests/test_check_sdp_capability.py tests/test_sdp_db_invariant.py tests/test_b15_page_size_corroboration.py -o addopts="-ra"` — **22 passed**, no regressions.
- `git status --porcelain firestarter/sdp_capability.py tools/check_sdp_capability_invariants.py` — empty. No new `tools/check_*.py`.
- `grep -c 'Not currently stored in .chip_database.json.' doc/infoic-field-dictionary.md` — `2` (see Deviation 2 above for why this is 2, not the plan's assumed 1).
- `ruff check` / `ruff format --check` on the new test file — clean.
- `python3 tools/check_mypy_watermark.py` — 35 errors, at the watermark (unchanged), none in the new file.
- Both pointer files carry exactly one anchored pointer line each, sharing a 312-character verbatim substring — no measurement restated in either.
- The todo is under `completed/`, moved with `git mv`, with its dated resolution block answering its own Cross-check note.

## Self-Check: PASSED

- FOUND: `firestarter_app/doc/infoic-field-dictionary.md` (new section present)
- FOUND: `firestarter_app/doc/package-details.md` (pointer present)
- FOUND: `firestarter_app/doc/protocol-flags.md` (pointer present)
- FOUND: `firestarter_app/tests/test_protect_flags_doc_measurements.py`
- FOUND: `.planning/todos/completed/decode-infoic-flags-bits-14-15-protect-metadata.md`
- MISSING (expected — moved): `.planning/todos/pending/decode-infoic-flags-bits-14-15-protect-metadata.md`
- Commits verified present in `firestarter_app` log: `7527fdb`, `f6cac45`, `63ca353`
- Commits verified present in meta log: `05dd610a` (todo fold), `a7c1600d` (gitlink bump), `18368ea4` (DATA-06 flip in REQUIREMENTS.md), `01314c4c` (ROADMAP.md flip)
