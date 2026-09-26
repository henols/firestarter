---
phase: 155-dead-weight-removal-the-heap-allocator-and-the-64-bit-runtim
verified: 2026-08-23T11:33:16Z
status: passed
score: 6/6 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 155: Dead-Weight Removal — the heap allocator and the 64-bit runtime Verification Report

**Phase Goal:** Delete two whole libraries from the image that one call site each was dragging in — with the allocator's removal also closing a latent unchecked-allocation dereference.
**Verified:** 2026-08-23T11:33:16Z
**Status:** passed
**Re-verification:** No — initial verification

All verification in this report was produced by re-running the mechanical checks myself
against the live `firestarter` tree (HEAD `adf1a31`), not by reading SUMMARY.md claims. Every
figure below was independently reproduced this session.

## Goal Achievement

### Observable Truths (ROADMAP.md's six Success Criteria — the contract)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Image contains no `malloc`/`free`/`realloc`/`calloc`/`__brkval` symbol on any of the three AVR images | ✓ VERIFIED | `python3 scripts/check_no_heap_or_64bit_symbols.py` → `PASS: leonardo(heap=0,64bit=0,anchors=2/2), uno(heap=0,64bit=0,anchors=2/2), uno328pb(heap=0,64bit=0,anchors=2/2)`, exit 0, reproduced independently this session. Cross-checked directly with `avr-nm --print-size --size-sort -C` + grep on all three ELFs: 0 matches for the 9-symbol heap set on each. `mem_util_blank_check`'s saved address is a file-scope `static uint32_t blank_check_saved_address` (`src/proms/memory.cpp:507`), not a `malloc`'d struct. |
| 2 | Unchecked dereference closed, recorded as a latent defect (not incidental cleanup) | ✓ VERIFIED | `src/proms/memory.cpp:507-525` — direct read/write of `blank_check_saved_address`, no allocation, no unchecked deref. `.planning/v1.33/155-after-figures.md` §7 quotes the original defect verbatim with line numbers and states "recorded here as a latent defect closed... not as incidental cleanup," matching DEAD-02's own instruction. |
| 3 | Image contains no 64-bit runtime helper (all eleven symbols, not just the eight DEAD-03 names) on any of the three images | ✓ VERIFIED | Same script/gate run above: `64bit=0` on all three ELFs. Independently confirmed with a direct `avr-nm` grep over all eleven symbol names (`__muldi3`, `__muldi3_6`, `__umulsidi3`, `__umulsidi3_helper`, `__umoddi3`, `__udivdi3`, `__udivdi3_umoddi3`, `__udivmod64`, `__ashrdi3`, `__lshrdi3`, `__adddi3`) — 0 matches on `uno`, `uno328pb`, `leonardo`. `rurp_read_voltage_mv`'s body is now pure 32-bit arithmetic (`src/boards/rurp_common.cpp`, no `uint64_t` anywhere in the function). |
| 4 | 32-bit voltage reformulation proven equivalent by a committed oracle over a stated grid, both overflow guards exercised | ✓ VERIFIED | `firestarter/tests/test_voltage_reformulation_oracle.py`, 15/15 passing (re-run this session). Confirmed non-vacuity of the guard-boundary tests: `test_guard_a_boundary_pair` and `test_guard_b_boundary_pair` use dedicated, plan-time-computed `(r1, r2)` pairs straddling the exact boundary — the nominal grid (R2 39k-47k) only reaches `k` ≤ 8715, three orders of magnitude below the 4194303 guard, so these dedicated cases are the only thing that exercises either guard. Both zero sentinels (`r2==0`, `bg==0`) tested. Shipped guard constant confirmed `k > 4194303UL` (`src/boards/rurp_common.cpp:117`), not the rejected `4000000UL`. |
| 5 | Coverage ceiling stated, not implied; no phase artifact implies native/bench coverage | ✓ VERIFIED | `python3 .planning/v1.33/tools/check_dead05_phrasing.py` → exit 0, `PASS: 22 file(s) scanned, 75 in-scope paragraph(s) found (floor 6)`, 0 forbidden-phrasing violations, all four required-positive targets confirmed carrying the mandated phrasing verbatim. Corpus has exactly three named exclusions (`155-RESEARCH.md`, `155-PATTERNS.md`, `155-VALIDATION.md` — negative-half only); all six `155-*-SUMMARY.md` files remain in-corpus and un-exempted (confirmed by reading `NAMED_EXCLUSIONS` in the checker source and the corpus doc's explicit statement "no SUMMARY.md" is exempt). Mandated wording present verbatim in the shipped `rurp_common.cpp` comment. Named residual risk (avr-gcc miscompiling the 32-bit multiply/divide) stated as unmitigated, not covered. |
| 6 | Both native suites updated together, behaviour still pinned by surviving assertion, rejected alternative recorded with cost | ✓ VERIFIED | `include/firestarter.h` no longer declares `progress_data`. Both `test_val_5v_page.cpp` and `test_eeprom28c_sdp.cpp` no longer assert `h.progress_data == NULL`; both carry the corrected "unconditionally adjacent statements in the same then-branch" wording (not the false "same statement" claim) in three comment blocks total. `pio test -e native` and `-e native_nodevtools` both reproduced at **172/172, 17 suites** this session. |

**Score:** 6/6 truths verified (0 present-but-behavior-unverified)

### Measured Deltas — independently reproduced (not transcribed)

| Target | Flash before (155-before-figures.md) | Flash after (measured this session) | Δ | RAM before | RAM after | Δ |
|---|---|---|---|---|---|---|
| `uno` | 26026 | **24660** | **−1366** | 1575 | **1567** | **−8** |
| `uno328pb` | 26074 | **24708** | **−1366** | 1581 | **1573** | **−8** |
| `leonardo` | 28170 | **26804** | **−1366** | 2016 | **2008** | **−8** |

Matches the phase's claimed −1366 B / −8 B on all three targets exactly, from a cold-independent `pio run` this session — not copied from any SUMMARY. This is 2 B more reduction than the ROADMAP header's `−1364 B`; that gap is deliberately explained (not a defect): the shipped guard is `k > 4194303UL`, confirmed present verbatim in `src/boards/rurp_common.cpp:117`, and the correction to −1366 B is recorded in both `155-after-figures.md` §3 and the ROADMAP/REQUIREMENTS text.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `.planning/v1.33/155-before-figures.md` | Authoritative pre-change record | ✓ VERIFIED | Present, 414 lines, all figures cross-checked against a live re-measurement this session and matched exactly. |
| `.planning/v1.33/155-after-figures.md` | Authoritative post-change landing record | ✓ VERIFIED | Present, 592 lines, all eight phase-gate legs recorded with figures; every claim in it was independently re-run this session and reproduced. |
| `firestarter/scripts/check_no_heap_or_64bit_symbols.py` | Link-time DEAD-01/03 gate | ✓ VERIFIED | Present, runs, exits 0 on the current tree with `heap=0, 64bit=0, anchors=2/2` on all three ELFs. |
| `firestarter/tests/test_check_no_heap_or_64bit_symbols.py` | Paired anti-hollow pytest | ✓ VERIFIED | 10/10 passing this session, including `test_planted_prechange_listing_exits_one_and_names_the_symbols` (RED direction) and `test_real_postchange_listing_exits_zero` (GREEN direction on a real committed post-change listing). |
| `firestarter/tests/fixtures/planted_no_heap_or_64bit_symbols_prechange_uno/avr-nm-uno.txt` | Real pre-change listing (RED control) | ✓ VERIFIED | Present, drives the RED-direction test above. |
| `firestarter/tests/fixtures/clean_no_heap_or_64bit_symbols_postchange_uno/avr-nm-uno.txt` | Real post-change listing (GREEN control) | ✓ VERIFIED | Present, drives the GREEN-direction test above, replacing the synthetic derivation. |
| `.planning/v1.33/tools/check_dead05_phrasing.py` | DEAD-05 phrasing gate | ✓ VERIFIED | Present, runs, exits 0 over the real 22-file corpus this session. |
| `.planning/v1.33/155-dead05-phrasing-corpus.md` | Corpus contract | ✓ VERIFIED | Present, names exactly three exclusions with reasons, `PARAGRAPH_FLOOR=6`. |
| `firestarter/tests/test_voltage_reformulation_oracle.py` | DEAD-04 oracle | ✓ VERIFIED | Present, 15/15 passing this session, including dedicated guard-boundary and sentinel legs and a source-contract scan binding the model to the shipped C. |
| `firestarter/src/boards/rurp_common.cpp` | 32-bit reformulation + mandated comment | ✓ VERIFIED | Shipped guard `k > 4194303UL`; mandated coverage-ceiling phrasing present verbatim; no `uint64_t` in the function. |
| `firestarter/src/proms/memory.cpp` | Heap removal | ✓ VERIFIED | File-scope static replaces the allocation; no `malloc`/`free`/unchecked deref remain. |
| `firestarter/include/firestarter.h` | `progress_data` member removed | ✓ VERIFIED | Grep confirms zero references to `progress_data` anywhere in the file. |
| `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp`, `test_eeprom28c_sdp.cpp` | Updated assertions + comments | ✓ VERIFIED | Both files updated, both suites build and pass, "same statement" corrected to "unconditionally adjacent statements" in all three affected blocks, no stale `progress_data` reference remains. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `scripts/check_no_heap_or_64bit_symbols.py` | `size_baseline.json`'s `avr_targets` keys | reads target names, never hardcodes three | ✓ WIRED | Gate ran successfully against all three configured targets (`uno`, `uno328pb`, `leonardo`) by name. |
| `test_check_no_heap_or_64bit_symbols.py` | the two committed fixtures | RED/GREEN pairing | ✓ WIRED | Both fixture-driven legs pass, proving the gate discriminates in both directions. |
| `test_voltage_reformulation_oracle.py` | `rurp_common.cpp` | comment-stripped source-contract scan | ✓ WIRED | `test_shipped_c_matches_the_transcribed_formula`, `test_model_constants_appear_verbatim_in_the_shipped_body`, `test_no_sixty_four_bit_type_remains_in_the_function_body` all pass — the Python model is bound to the actual shipped text, not an independent copy. |
| `check_dead05_phrasing.py` | the 22-file corpus (incl. all six `155-*-SUMMARY.md` files) | glob + paragraph scan | ✓ WIRED | Confirmed SUMMARY files are scanned (per-file paragraph counts shown in the tool's own output) and not exempted. |
| `include/firestarter.h`'s member removal | both native test suites | compiler-forced (build breaks without matching edit) | ✓ WIRED | Both suites build and pass at 172/172 combined; this is compile-time proof the edits landed together, not merely claimed. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Symbol gate reaches exit 0 on the shipped tree | `python3 scripts/check_no_heap_or_64bit_symbols.py` | `PASS: ... heap=0,64bit=0,anchors=2/2` for all three targets, exit 0 | ✓ PASS |
| `avr-nm` independently confirms zero heap/64-bit symbols | direct `avr-nm` + grep on all three ELFs | 0/0/0 matches, both symbol sets, all three targets | ✓ PASS |
| Native suite `native` | `pio test -e native` | 172 test cases, 172 succeeded, 17 suites | ✓ PASS |
| Native suite `native_nodevtools` | `pio test -e native_nodevtools` | 172 test cases, 172 succeeded, 17 suites | ✓ PASS |
| Host pytest suite | `python3 -m pytest tests/ -q -o addopts=""` | 348 passed, 0 failed | ✓ PASS |
| DEAD-04 oracle | `python3 -m pytest tests/test_voltage_reformulation_oracle.py -v -o addopts=""` | 15/15 passed | ✓ PASS |
| DEAD-01/03 anti-hollow gate pytest | `python3 -m pytest tests/test_check_no_heap_or_64bit_symbols.py -v` | 10/10 passed (RED + GREEN directions both proven) | ✓ PASS |
| DEAD-05 phrasing gate | `python3 .planning/v1.33/tools/check_dead05_phrasing.py` | exit 0, 22 files, 75 in-scope paragraphs, 0 violations | ✓ PASS |
| `pio run` all three targets | `pio run -e {uno,uno328pb,leonardo}` | −1366 B flash / −8 B RAM on all three, matching the claimed total exactly | ✓ PASS |
| checker convention floors | `python3 -m pytest tests/test_checker_convention.py -q` | 7/7 passed against `FLOOR=7`, `FIXTURE_FLOOR=16` | ✓ PASS |

### Probe Execution

Step 7c: SKIPPED — no `scripts/*/tests/probe-*.sh` files exist in either repo, and no PLAN/SUMMARY for this phase declares a probe.

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| DEAD-01 | 155-01, 155-02, 155-05, 155-06 | No malloc/free/realloc/calloc/__brkval symbol; sole caller closed | ✓ SATISFIED | Symbol gate exit 0, `avr-nm` cross-check, static replacing allocation |
| DEAD-02 | 155-01, 155-05, 155-06 | Unchecked dereference closed, recorded as latent defect | ✓ SATISFIED | `memory.cpp` diff, defect quoted with line numbers in after-figures §7 |
| DEAD-03 | 155-01, 155-02, 155-04, 155-06 | No 64-bit runtime helper (all 11 symbols); function body shrunk | ✓ SATISFIED | Symbol gate + direct `avr-nm` grep over all 11 names, 0 matches |
| DEAD-04 | 155-04, 155-06 | 32-bit reformulation proven equivalent by committed oracle | ✓ SATISFIED | 15/15 oracle tests passing, dedicated non-vacuous guard-boundary cases |
| DEAD-05 | 155-03, 155-04, 155-06 | Coverage ceiling stated, not implied | ✓ SATISFIED | Phrasing gate exit 0 over real corpus, mandated wording present verbatim |
| DEAD-06 | 155-05, 155-06 | Native suites updated, behaviour pinned, alternative recorded | ✓ SATISFIED | 172/172 both native legs, corrected comment wording confirmed by grep |

**Orphan check:** `grep -n "Phase 155" .planning/REQUIREMENTS.md` returns only the DEAD-01..06 block and its traceability-table rows — no additional requirement ID maps to Phase 155 that isn't claimed by a plan. No orphaned requirements.

### Anti-Patterns Found

None. Scanned all nine files modified by this phase (`include/firestarter.h`, `scripts/check_no_heap_or_64bit_symbols.py`, `src/boards/rurp_common.cpp`, `src/proms/memory.cpp`, both native test files, `tests/test_check_no_heap_or_64bit_symbols.py`, `tests/test_checker_convention.py`, `tests/test_voltage_reformulation_oracle.py`) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`/"not yet implemented"/"coming soon" — zero matches across all files.

**Hollow-gate scrutiny (explicit focus of this verification):** The symbol gate is proven from three directions, not one: (1) a real, committed pre-change listing produces exit 1 (`test_planted_prechange_listing_exits_one_and_names_the_symbols`); (2) a real, committed post-change listing produces exit 0 (`test_real_postchange_listing_exits_zero`); (3) `155-after-figures.md` §13 documents a throwaway-worktree planted post-change negative — the first attempt (a naive unused-malloc+immediate-free) was silently eliminated by the compiler and produced a false PASS, and the executor caught this and corrected the planted negative to mirror the pre-change store/read-back shape, which the compiler cannot elide (confirmed: flash grew 24660→25292, the gate then correctly reported FAIL naming all seven symbols). This self-correction is recorded, not hidden, and I could not independently re-run the throwaway-worktree leg (its whole premise is a non-persistent worktree that was removed), but the documented before/after flash numbers and the compiler-elision failure mode described are internally consistent and match this project's own stated standard for what makes a gate non-hollow.

### Scope Fence

`git -C firestarter diff --name-only 2ad5b322a37ba4a88afd09cc946f5c4114e51483..HEAD` lists exactly 13 files, all within the phase's declared scope: `include/firestarter.h`, `scripts/check_no_heap_or_64bit_symbols.py`, `src/boards/rurp_common.cpp`, `src/proms/memory.cpp`, both native test files, both new fixture directories (4 files), `tests/test_check_no_heap_or_64bit_symbols.py`, `tests/test_checker_convention.py`, `tests/test_voltage_reformulation_oracle.py`. None of `include/memory_utils.h`, `src/json_parser.c`, `src/proms/eprom.cpp`, `src/proms/flash_intel.cpp`, `src/proms/flash_utils.cpp`, `src/proms/eeprom_28c.cpp`, or `include/messages.h` appear — confirmed by direct listing, not by trusting the SUMMARY. `firestarter_app` was not touched by this phase (the meta repo's `M firestarter_app` is pre-existing Phase 154 drift, confirmed operator-gated and unrelated).

`scripts/baseline/size_baseline.json` confirmed byte-unchanged (`git diff --quiet` exits 0) — not re-anchored, as required (LAND-01/Phase 158 owns that).

### Carry-Forward Item (recorded, not a gap)

Phase 153 (`5bfae80`) added `check_erase_no_vpp.py` without bumping `FLOOR`/`FIXTURE_FLOOR`; the tree now ships 8 checkers/30 fixtures against a floor of 7/16 (raised from 6/15 by this phase). The `>=` assertion in `test_checker_convention.py` passes regardless. This phase explicitly declined to close that pre-existing gap and named it a Phase 158 item — confirmed present in `155-02-SUMMARY.md` and reproduced structurally in `tests/test_checker_convention.py` (`FLOOR = 7`, comment naming the drift). Not counted as a gap of this phase.

### Informational Note (not a gap)

`155-VALIDATION.md` frontmatter still reads `status: draft`, `nyquist_compliant: false`, and its "Validation Sign-Off" checklist items are unchecked with "Approval: pending" — this is stale bookkeeping left over from before execution; the actual evidence (all eight phase-gate legs, both gate directions, the phrasing gate) is fully recorded and independently reproduced in `155-after-figures.md` and by this verification. This does not block phase goal achievement but is worth a follow-up edit to `155-VALIDATION.md` for internal consistency.

### Human Verification Required

None. All six ROADMAP success criteria and all six DEAD-01..06 requirements are mechanically verifiable and were independently re-run this session with matching results.

### Gaps Summary

No gaps. All six ROADMAP success criteria hold, independently reproduced against the live tree rather than trusted from SUMMARY.md. The measured −1366 B flash / −8 B RAM delta was reproduced exactly on all three targets from a fresh build. The headline symbol-absence gate exits 0 with zero heap and zero 64-bit-runtime symbols on all three ELFs, confirmed both via the shipped script and via direct `avr-nm` queries. The gate is proven in both directions (a real pre-change negative and a real post-change positive), plus a documented (if not independently re-runnable) throwaway-worktree planted negative whose first, compiler-eliminable attempt was caught and corrected — exactly the hollow-gate failure mode this project's standard exists to catch. DEAD-04's oracle exercises both overflow guards with dedicated, non-vacuous boundary cases that the nominal grid cannot reach. DEAD-05's phrasing gate runs clean over the real 22-file corpus with exactly three named exclusions and the SUMMARY file class intentionally not exempted. The scope fence held: no phase-155 diff touches any of the files reserved for Phases 156-158. `size_baseline.json` is byte-unchanged. The five public corrections (OQ-1 through OQ-4, C-5) are documented in both `155-after-figures.md` and the hand-edited ROADMAP/REQUIREMENTS text, and the −1364/−1366 discrepancy is the deliberate, explained OQ-1 correction, not a defect. The only non-blocking finding is stale `155-VALIDATION.md` frontmatter/sign-off bookkeeping, noted above for a documentation touch-up.

---

_Verified: 2026-08-23T11:33:16Z_
_Verifier: Claude (gsd-verifier)_
