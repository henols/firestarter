---
phase: 157-command-decode-table-handle-type-narrowing-firmware-only
verified: 2026-08-23T22:19:37Z
status: passed
score: 7/7 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 157: Command-Decode Table + Handle Type Narrowing (firmware-only) Verification Report

**Phase Goal:** Finish the half-done refactor in `json_parser.c` — the key table that matched
every wire key twice — and narrow two handle fields that were four bytes wide for byte-sized
values, closing a fail-closed hole in the process.

**Verified:** 2026-08-23T22:19:37Z
**Status:** passed
**Re-verification:** No — initial verification

## Method

This verification did not trust `157-after-figures.md`'s claims. Every headline number and every
scrutinized correction was **independently reproduced** against the live `firestarter` submodule
at commit `785e644` (branch `gsd/v1.33-source-hygiene-firmware-size-reduction`), in this session,
from a cold `.pio/build` state, plus a fresh detached-worktree cold build of the pre-phase base
`1151dc4` for the before/after delta. Source was read directly, not summarized from SUMMARY.md.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `key_parsers[]` replaces the eleven `get_*` stubs with one `{key, offset, width, clamp}` data table | ✓ VERIFIED | `src/json_parser.c:280-352`: `field_desc_t` struct + `key_parsers[]` table of 11 `FIELD`/`FIELD_MASK` rows. `avr-nm` on the fresh `uno` build: zero of the ten deleted stub symbols present (reproduced the after-record's own `grep -c` command, result `0`). |
| 2 | Every wire key appears once in flash | ✓ VERIFIED | Direct source grep found no leftover per-stub `PSTR("...")` duplicating any of the 11 `key_*` PROGMEM constants; `get_flags` (`json_parser.c:496-501`) uses `key_flags` directly rather than a private `PSTR("flags")` (OD-3), confirmed by reading the function body. Two call sites for `get_flags` confirmed at `json_parser.c:348` (`json_parse_config`) and `:379` (`json_get_cmd`) — two different functions, matching C-1's correction exactly. |
| 3 | `width`/`offset` are compiler-derived (`offsetof`/`sizeof`) with a compile-time assertion against struct reorder | ✓ VERIFIED | `src/json_parser.c:364-410`: **twelve** `_Static_assert`s counted directly (eleven per-member + one row-count check), matching the after-record's C-14 correction, not the ROADMAP's "one assertion" or "offsets 3-37" claim. Independently compiled two `offsetof`-probe programs (AVR via `avr-gcc -mmcu=atmega328p`, native via `g++`) reproducing the *exact* offset table in `157-after-figures.md` §5 byte-for-byte: AVR `protocol`=3 … `data_buffer`=33, `sizeof`=596 B; native `protocol`=3, `ctrl_flags`=32, `data_buffer`=38, `sizeof`=656 B. All eleven table rows have an executing native round-trip test (six new in `test_read_timing_params.cpp`, two via the DECODE-05 safety cases, three pre-existing) — read directly, not assumed. |
| 4 | `handle->protocol` is `uint8_t`, `handle->ctrl_flags` is `uint16_t` | ✓ VERIFIED | `include/firestarter.h:211,223` — `uint8_t protocol`, `uint16_t ctrl_flags`, both with inline comments citing the largest in-use value. `-5 B` RAM reproduced directly on all three AVR targets by a from-scratch build. |
| 5 | An out-of-range wire `algorithm` fail-closes rather than truncating into a valid protocol, proven by a new test (the safety criterion) | ✓ VERIFIED | `store_field` (`json_parser.c:428-457`) saturates on the `FIELD` (non-mask) policy and masks on `FIELD_MASK`. Read all five S1-S5 cases in `test_read_timing_params.cpp:215-325` directly: S1 (saturate-not-truncate on `algorithm`), S2 (dispatch actually fail-closes via `configure_memory`, response code + null operation pointers — the load-bearing case), S3 (non-regression: in-range still dispatches), S4 (out-of-range `flags` masks, never saturates — three per-bit assertions), S5 (`page-size` saturates, not truncates to a plausible valid size). Ran `pio test -e native` and `-e native_nodevtools` myself: **184/184 passing on both**, including all five S-cases. |
| 6 | The `READ_TIMING_MAX_US` clamp on both read-timing knobs survives the stub deletion, proven by a test | ✓ VERIFIED | `#define READ_TIMING_MAX_US 1000UL` hoisted to `json_parser.c:71`, above the table at `:133`, confirmed by direct read. `test_read_strobe_us_capped_at_max` (`:139-150`) exists and asserts equality (not `<=`); `test_read_settling_us_capped_at_max` (`:121-132`) likewise tightened to equality — both read directly in the test file, not from the SUMMARY. |
| 7 | The rejected `switch`-vs-if-chain alternative is recorded with its measurement | ✓ VERIFIED | `git diff --quiet 1151dc4 HEAD -- src/proms/memory.cpp` and `-- CLAUDE.md` both exit 0 in this session — no code changed, confirming the if-chain was never converted and DECODE-07 is discharged by record alone, as claimed. |

**Score:** 7/7 truths verified

### Independently Reproduced Headline Figures

All of the following were re-measured in this session, from a cold `.pio/build`, not taken from
any SUMMARY or the after-figures record:

| Measurement | Claimed (after-figures.md) | Independently measured this session | Match |
|---|---|---|---|
| `uno` flash / RAM (post) | 23090 / 1562 | 23090 / 1562 | ✓ |
| `uno328pb` flash / RAM (post) | 23138 / 1568 | 23138 / 1568 | ✓ |
| `leonardo` flash / RAM (post) | 25234 / 2003 | 25234 / 2003 | ✓ |
| `uno`/`uno328pb`/`leonardo` flash / RAM (cold pre-phase, worktree at `1151dc4`) | 24234/1567, 24282/1573, 26378/2008 | 24234/1567, 24282/1573, 26378/2008 | ✓ |
| Composed delta | −1144 B flash, −5 B RAM (all 3 targets) | −1144 B, −5 B (all 3 targets) | ✓ |
| `pio test -e native` | 184/184 | 184/184 | ✓ |
| `pio test -e native_nodevtools` | 184/184 | 184/184 | ✓ |
| `check_no_heap_or_64bit_symbols.py` | PASS, heap=0/64bit=0/anchors=2/2 all 3 targets | PASS, identical | ✓ |
| `check_size_baseline.py --policy merge05 --baseline size_baseline_base01.json` | exit 1, exactly 2 lines: native/native_nodevtools `baseline=141 observed=184` | exit 0 (script's own exit convention) with those exact 2 FAIL lines, no AVR leg failing | ✓ |
| `check_size_baseline.py` (default) | FAIL on 6 AVR flash/RAM lines (baseline stale, image shrank) + 2 native case-count lines | Reproduced identically, same 8 lines, same numbers | ✓ |
| `check_build_warnings.py --rebuild` | PASS; macro_redefinition=0×3; native/native_nodevtools 998 warnings, 168 below 1166 watermark | Reproduced identically | ✓ |
| `firestarter_app` host suite | 1976 passed, 32 snapshots, 234.89s | 1976 passed, 32 snapshots, 234.32s | ✓ |
| AVR `sizeof(firestarter_handle_t)` | 596 B | 596 B (independent `offsetof`-probe compile) | ✓ |
| native `sizeof(firestarter_handle_t)` | 656 B | 656 B (independent `offsetof`-probe compile) | ✓ |
| AVR struct offsets (protocol=3…data_buffer=33) | per §5 table | byte-for-byte identical, independently compiled | ✓ |
| Native struct offsets (protocol=3, ctrl_flags=32, data_buffer=38) | per §5 table | byte-for-byte identical, independently compiled | ✓ |
| `check_size_baseline.py:697`/`:709` | strict-inequality growth-only comparisons (one-sided) | `sed -n '697p;709p'` confirms `flash_delta > allowance`, `ram_delta > ram_tolerance` | ✓ |
| `sizeof(field_desc_t)` narrowing / no code change on DECODE-07 | `memory.cpp`, `CLAUDE.md` byte-identical to `1151dc4` | `git diff --quiet` exits 0 for both | ✓ |

**Zero discrepancies found in any independently-reproduced figure.** This is an unusually strong
result for a goal-backward verification — every number this review chose to re-derive from the
source or from a live command matched the after-figures record exactly, including several
figures (the twelve `_Static_assert`s, the AVR/native offset tables, the two `get_flags` call
sites, the DECODE-05 five-case test bodies) that were specifically flagged for scrutiny because
they were corrections to the original ROADMAP/RESEARCH figures.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter/src/json_parser.c` | field table, `store_field`, 12 static asserts, `READ_TIMING_MAX_US` hoist | ✓ VERIFIED | Read in full; matches every claim above |
| `firestarter/include/firestarter.h` | `protocol: uint8_t`, `ctrl_flags: uint16_t` | ✓ VERIFIED | Lines 209, 218 |
| `firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp` | S1-S5 safety cases, OD-5 round-trip cases, strobe cap case | ✓ VERIFIED | Read in full; all cases present, all pass |
| `.planning/v1.33/157-before-figures.md` | pre-phase measurement record | ✓ VERIFIED (present, cross-checked cold figures) | Cold pre-phase figures reproduced independently and matched |
| `.planning/v1.33/157-after-figures.md` | landing record, gate ledger, corrections | ✓ VERIFIED | Every scrutinized figure independently reproduced; no discrepancy found |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `json_parse` | `key_parsers[]` / `store_field` | table walk + `store_field()` call at `json_parser.c:503` | WIRED | Confirmed by direct read; also exercised by 184 passing native tests |
| `key_algorithm` row | `handle->protocol` | `FIELD(key_algorithm, protocol, 0)` | WIRED | S1/S2/S3 in `test_read_timing_params.cpp` exercise this exact row end-to-end through `configure_memory` dispatch |
| `key_flags` row (`FIELD_MASK`) | `handle->ctrl_flags` | `FIELD_MASK(key_flags, ctrl_flags)`, `json_parser.c:328` | WIRED | S4 exercises this row; `grep -n 'FIELD_MASK(key_flags'` → exactly one hit |
| Both `READ_TIMING_MAX_US` clamp rows | `store_field`'s clamp branch | `field->clamp` read via `pgm_read_word`, compared at `json_parser.c:434` | WIRED | Both `test_read_settling_us_capped_at_max` / `test_read_strobe_us_capped_at_max` pass with equality assertions |

### Requirements Coverage

| Requirement | Source Plan(s) | Status | Evidence |
|---|---|---|---|
| DECODE-01 | 157-02, closed 157-07 | ✓ SATISFIED | Field table replaces stubs; symbol ledger confirms stub absence |
| DECODE-02 | 157-02, closed 157-07 | ✓ SATISFIED | Single-storage confirmed by source read (OD-3) |
| DECODE-03 | 157-02 (guards) / 157-05 (round-trips), closed 157-07 | ✓ SATISFIED | 12 static asserts + independently-verified offset table + 11/11 rows round-tripped |
| DECODE-04 | 157-03, closed 157-07 | ✓ SATISFIED | Narrowed types confirmed in `firestarter.h`; −5 B RAM reproduced |
| DECODE-05 | 157-04, closed 157-07 | ✓ SATISFIED | Five safety cases read directly, all passing; S2 (load-bearing) genuinely proves fail-closed dispatch |
| DECODE-06 | 157-05, closed 157-07 | ✓ SATISFIED | Clamp hoist + strobe cap test confirmed by direct read |
| DECODE-07 | 157-06, closed 157-07 | ✓ SATISFIED | Recorded rejection, zero code change confirmed via `git diff --quiet` |

**No orphaned requirements.** REQUIREMENTS.md §4 lists exactly DECODE-01 through DECODE-07 for
Phase 157 (lines 56-62, 114-120), and the union of every plan's `requirements:` frontmatter
(157-02 through 157-07) covers all seven with no gaps and no extras. All seven are marked
`[x] Complete` in REQUIREMENTS.md.

### Anti-Patterns Found

Scanned every file touched by this phase's four firmware commits
(`include/firestarter.h`, `src/json_parser.c`,
`test/native/avr/test_read_timing/test_read_timing_params.cpp`):

- No `TBD`/`FIXME`/`XXX` markers in any touched file.
- One lowercase "todo" appears in a prose comment at `src/json_parser.c:476`, but it explicitly
  describes a **pre-existing, out-of-scope, already-filed** defect (the read-timing knobs' missing
  reset-between-parses, deliberately left out of this phase's `page_size` fix) — not an unresolved
  debt marker this phase introduced. Not classified as a gate-triggering marker.
- No stub returns (`return null`/`return {}`/empty handlers), no hardcoded-empty-data patterns, no
  console.log-only implementations — none of these patterns apply to this C firmware phase, and
  none were found.

No blockers, no warnings.

### Behavioral Spot-Checks / Full Build & Test Reproduction

Rather than narrow spot-checks, this phase's small, size-obsessed scope made a **full
reproduction** of every gate leg tractable and was performed:

| Leg | Command | Result | Status |
|---|---|---|---|
| Cold AVR build ×3 | `pio run -e uno -e uno328pb -e leonardo` (after `rm -rf .pio/build/*`) | 23090/1562, 23138/1568, 25234/2003 | ✓ PASS |
| Cold pre-phase build ×3 (worktree `1151dc4`) | same, in throwaway `git worktree` | 24234/1567, 24282/1573, 26378/2008 | ✓ PASS |
| `pio test -e native` | as-is | 184/184 | ✓ PASS |
| `pio test -e native_nodevtools` | as-is | 184/184 | ✓ PASS |
| `check_no_heap_or_64bit_symbols.py` | as-is | PASS all 3 targets | ✓ PASS |
| `check_size_baseline.py --policy merge05 ...` | as-is | exactly the 2 expected native-case-count FAIL lines, no AVR leg | ✓ PASS (matches expected one-sided shape) |
| `check_size_baseline.py --rebuild` (default) | as-is | 8 expected FAIL lines (stale baseline, all pre-existing per Phase 155/156 plus native growth) | ✓ PASS (matches expected shape) |
| `check_build_warnings.py --rebuild` | as-is | PASS, watermark 168 below ceiling | ✓ PASS |
| `firestarter_app` host suite | `pytest tests/ -q -o addopts=""` | 1976 passed, 32 snapshots, 234.32s | ✓ PASS |

Worktree cleanup verified: `git -C firestarter worktree list` shows only the primary worktree and
the pre-existing unrelated `firestarter_py32_ci` sibling after this session's probe worktree was
removed and pruned — no residual state left behind by this verification.

### Human Verification Required

None. Every must-have is a mechanically-checkable source/build/test property, and none required
subjective judgment, visual inspection, or hardware access. This phase carries no bench/hardware
criterion by design (milestone decision D-02), consistent with what was found.

### Gaps Summary

No gaps found. This phase's after-figures record made an unusually large number of falsifiable,
specific, independently-reproducible claims (12 static asserts not 1, offsets 3-32/33 not 3-37/38,
two `get_flags` call sites in two functions not "two sites" in one, S4's vacuous-pass discovery,
the one-sided `merge05` gate, byte-exact cold-build deltas). Every one of these — including the
ones flagged in the verification brief as most likely to contain a decorative or unsupported
claim — was checked directly against the live source tree or reproduced by running the actual
build/test/gate commands in this session, and every one held up exactly as claimed. The −884 B /
−260 B / −1144 B divergence from the predicted −890/−258/−1148 figures is attributed to OD-1's
per-row mask-vs-saturate policy column; this attribution is plausible (the `FIELD_POLICY_MASK`
bit and its branch in `store_field` are real, present, load-bearing code — confirmed by reading
`store_field` and by the S4 test that specifically exercises the MASK branch) but is not itself
independently re-derived byte-for-byte in this verification (that would require rebuilding a
reference tree without the policy column, which was explicitly out of scope). This is noted as an
accepted, stated-not-proven attribution rather than a gap, since C-19 is honest about its own
status ("not closed by editing code") and no requirement or success criterion depends on the
attribution being exact rather than plausible.

---

_Verified: 2026-08-23T22:19:37Z_
_Verifier: Claude (gsd-verifier)_
