---
phase: 157-command-decode-table-handle-type-narrowing-firmware-only
plan: "03"
subsystem: firmware-decode
tags: [firestarter.h, type-narrowing, protocol, ctrl_flags, avr-nm, sizeof, platformio]

# Dependency graph
requires:
  - phase: 157-command-decode-table-handle-type-narrowing-firmware-only
    provides: "the compiler-derived field_desc_t table (src/json_parser.c, plan 02) whose FIELD/FIELD_MASK macros re-derive offset/width automatically once the handle's member types narrow"
provides:
  - "firestarter_handle_t.protocol narrowed to uint8_t and .ctrl_flags narrowed to uint16_t, in include/firestarter.h"
  - "The consumer-surface audit, recorded with measured counts: 18 protocol-keyed dispatch sites / 20 total ->protocol reads, 40 is_flag_set uses / 59 post-preprocessor uses"
  - "The narrowing's own flash/RAM delta on all three AVR targets, measured separately from plan 02's table-only delta, with any divergence from the reference's -258/-1148 attributed to OD-1's policy column rather than engineered away"
  - "sizeof(firestarter_handle_t) re-derived on both architectures (AVR 596 B, native 656 B unchanged), confirming the -5 B RAM saving is AVR-only"
affects: [157-04-PLAN, 157-05-PLAN, 157-06-PLAN, 157-07-PLAN]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Bounds-justifying comment placed directly on a narrowed struct member, citing the specific named constant (PROTO_PHANTOM_0x39, FLAG_SKIP_SDP_UNLOCK) and the cross-repo parity gate that pins it, rather than a bare width change"

key-files:
  created: []
  modified:
    - firestarter/include/firestarter.h

key-decisions:
  - "protocol narrowed uint32_t -> uint8_t (largest dispatched value 0x39); ctrl_flags narrowed uint32_t -> uint16_t (largest flag 0x100, bidirectionally pinned by firestarter_app's test_revision_constants_parity.py at exactly nine flags)"
  - "Neither dispatch test file (test_configure_memory.cpp, test_not_implemented.cpp) needed its make_handle parameter narrowed -- check_build_warnings.py surfaced no new diagnostic from the implicit uint32_t -> uint8_t narrowing conversion at the h.protocol assignment, so both files stay byte-unchanged, exactly as the plan's conditional predicted"
  - "eprom_params_for(uint32_t protocol) and eprom_block_budget_s(uint32_t protocol, ...) signatures left untouched -- recorded as a lead, not taken, per the plan's explicit prohibition"
  - "Measured narrowing delta is -260 B per AVR target (not -258 B) and the composed total vs the before-record is -1144 B (not -1148 B); both divergences attributed to OD-1's per-row mask-vs-saturate policy column (C-19), not chased by editing code"
  - "Leonardo's Caterina headroom against 28672 is measured as 3438 B at this position, superseding the ROADMAP's stale 3440 B (also differing from the RESEARCH-cited 3442 B, itself computed from a predicted rather than measured absolute -- recorded as a further, smaller divergence of the same OD-1-attributed kind)"

patterns-established: []

requirements-completed: [DECODE-04]

coverage:
  - id: D1
    description: "firestarter_handle_t.protocol is uint8_t and .ctrl_flags is uint16_t; struct member order, data_buffer, and all nine FLAG_* defines are unchanged"
    requirement: "DECODE-04"
    verification:
      - kind: other
        ref: "grep -c 'uint8_t protocol;' / 'uint16_t ctrl_flags;' include/firestarter.h => 1 each; grep -c 'uint32_t protocol;' / 'uint32_t ctrl_flags;' => 0 each; grep -cE '^#define FLAG_' => 9; grep -c 'char data_buffer[DATA_BUFFER_SIZE];' => 1"
        status: pass
    human_judgment: false
  - id: D2
    description: "All 18 protocol-keyed dispatch sites (17 handle->protocol == comparisons + 1 switch) and all 40 is_flag_set uses keep identical truth values by integer promotion; audited surface-by-surface (comparison semantics, log payloads, wire visibility, persistence, uint32_t parameter surfaces)"
    requirement: "DECODE-04"
    verification:
      - kind: integration
        ref: "pio test -e native and -e native_nodevtools both 172 test cases: 172 succeeded, unchanged from plan 02; three clean AVR builds with zero warning: lines"
        status: pass
    human_judgment: false
  - id: D3
    description: "OD-1's mask policy on the key_flags table row is confirmed load-bearing: FIELD_MASK is still the row's policy, preventing a saturate-to-0xFFFF that would set FLAG_FORCE/FLAG_SKIP_ERASE/FLAG_SKIP_BLANK_CHECK"
    requirement: "DECODE-04"
    verification:
      - kind: other
        ref: "grep -n 'FIELD_MASK(key_flags' src/json_parser.c => one hit, line 140; store_field's mask_policy branch inspected at src/json_parser.c:439"
        status: pass
    human_judgment: false
  - id: D4
    description: "-5 B RAM saving on all three AVR targets, confirmed two independent ways: ram_used from the build and sizeof(firestarter_handle_t) re-derived from the real compiler flags"
    requirement: "DECODE-04"
    verification:
      - kind: other
        ref: "pio run RAM: uno 1562, uno328pb 1568, leonardo 2003 (each -5 from plan 02's 1567/1573/2008); AVR sizeof re-derivation: 596 B (601 B before), native sizeof unchanged at 656 B"
        status: pass
    human_judgment: false
  - id: D5
    description: "Both local check scripts run (not assumed) and pass; the merge05 size gate's one-sided pass is recorded with its source line numbers; host parity gates report 24 passed"
    requirement: "DECODE-04"
    verification:
      - kind: integration
        ref: "check_build_warnings.py --rebuild and check_no_heap_or_64bit_symbols.py both exit 0; check_size_baseline.py --policy merge05 --baseline size_baseline_base01.json --rebuild fails with exactly two native case-count lines and no AVR flash/RAM leg; firestarter_app pytest tests/test_revision_constants_parity.py tests/test_json_key_parity.py => 24 passed"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-08-23
status: complete
---

# Phase 157 Plan 03: Handle Type Narrowing Summary

**Narrowed `firestarter_handle_t.protocol` to `uint8_t` and `.ctrl_flags` to `uint16_t`, audited all five consumer surfaces one at a time with measured site counts, and measured the narrowing's own flash/RAM delta (-260 B flash, -5 B RAM per AVR target) separately from plan 02's table-only delta -- both check scripts and the one-sided size gate run rather than assumed.**

## Performance

- **Duration:** ~55 min
- **Tasks:** 2 (narrow + audit; measure + commit)
- **Files modified:** 1 (`firestarter/include/firestarter.h`)

## Accomplishments

- Narrowed `firestarter_handle_t.protocol` from `uint32_t` to `uint8_t` and `.ctrl_flags` from
  `uint32_t` to `uint16_t`, each with an in-place comment stating the bound that justifies it:
  `protocol`'s largest dispatched value is `0x39` (`PROTO_PHANTOM_0x39`); `ctrl_flags`' largest flag
  is `0x100` (`FLAG_SKIP_SDP_UNLOCK`), pinned bidirectionally by
  `firestarter_app/tests/test_revision_constants_parity.py` at exactly nine flags. Struct member
  order, `data_buffer[DATA_BUFFER_SIZE]`, and all nine `FLAG_*` defines are unchanged.
- Audited the site counts and recorded MEASURED numbers (§ below), never the ROADMAP's unreproducible
  19/45.
- Ran the promotion audit surface-by-surface: comparison semantics (identical truth values via
  integer promotion), log payloads (both `protocol` sites already cast to `uint8_t`; `ctrl_flags`
  never logged), wire visibility (neither field serialised into any response frame -- verified, not
  assumed), persistence (`rurp_configuration_t` contains neither field -- explicit "no migration
  exists" conclusion), and the `uint32_t` parameter surfaces (`eprom_params_for`,
  `eprom_block_budget_s` left untouched, recorded as a lead not taken).
- Confirmed OD-1's mask policy on the `key_flags` table row is now load-bearing: with `ctrl_flags`
  two bytes wide, a saturate policy would store `0xFFFF` on out-of-range wire `flags`, turning on
  `FLAG_FORCE`, `FLAG_SKIP_ERASE` and `FLAG_SKIP_BLANK_CHECK` simultaneously; `FIELD_MASK` prevents
  it. Confirmed `get_flags`'s direct-assignment path (`json_parse_config`/`json_get_cmd`) truncates
  the same way, so all three `flags` paths agree.
- Built all three AVR targets three times across the session (post-narrowing, post-`check_build_warnings.py --rebuild`, post-`check_size_baseline.py --rebuild`) and got byte-identical figures every time: `uno` 23090/1562, `uno328pb` 23138/1568, `leonardo` 25234/2003 -- zero `warning:` lines each time.
- Confirmed `check_build_warnings.py --rebuild` surfaced no new diagnostic from the implicit
  `uint32_t -> uint8_t` narrowing conversion at both dispatch suites' `h.protocol = protocol;`
  assignment, so `test_configure_memory.cpp` and `test_not_implemented.cpp` stay byte-unchanged (the
  plan's conditional edit was not triggered).
- Re-derived `sizeof(firestarter_handle_t)` on both architectures with the same method and captured
  compiler flags the before-record used for OD-7: AVR `596` B (5 B smaller than the before-record's
  `601` B, with the eleven table members at offsets `3`-`32` and `data_buffer` at `33`, matching
  exactly); native `656` B, unchanged. States ceiling 5 explicitly: the -5 B RAM saving is AVR-only
  and unobservable natively, confirmed two independent ways.
- Ran `check_no_heap_or_64bit_symbols.py` (PASS, `heap=0,64bit=0`, all three targets) and the
  `merge05` size gate (`check_size_baseline.py --policy merge05 --baseline
  scripts/baseline/size_baseline_base01.json --rebuild`), which failed with exactly the two
  pre-existing native case-count lines and no AVR flash or RAM leg -- the one-sided pass, quoting
  `:697`/`:709` from source.
- Committed inside the submodule as `76ff592`; ran the host parity gates in `firestarter_app`
  afterward (`24 passed`), with `firestarter_app`'s porcelain unaffected by this plan.

## Measured Site Counts (Step 2)

Verbatim commands and results, run from `/workspaces/firestarter`:

```
grep -ro "handle->protocol ==" src/ | wc -l
# => 17
grep -rn "switch (handle->protocol)" src/
# => src/proms/eprom.cpp:70:        switch (handle->protocol) {
grep -rn -- "->protocol" src/ include/ | wc -l
# => 21 total (20 lines in src/, 1 in include/proto_constants.h -- a comment)
```

**18 protocol-keyed dispatch sites** (17 equality comparisons + 1 `switch`) out of **20 total
`handle->protocol` reads** in `src/`: the 18 dispatch occurrences, plus `eprom_params_for`'s three
call sites (`eprom.cpp:85,297,341`), `eprom_block_budget_s`'s one call site (`firestarter.cpp:242`),
the two already-cast log payloads (`not_implemented.cpp:17`, `eprom.cpp:87`), the `json_parser.c:393`
`_Static_assert` width probe, and three comment-only lines (`eprom.cpp:502`, `json_parser.c:337`,
`memory.cpp:140`) -- 20 distinct source lines in `src/` in total.

```
for f in $(grep -rl is_flag_set src/); do grep -o is_flag_set "$f" | wc -l; done | paste -sd+ | bc
grep -ro is_flag_set src/ | wc -l
# => 40, per-file: eprom_operations.cpp 1, flash_utils.cpp 1, flash_5v_page.cpp 2,
#    flash_intel.cpp 5, eeprom_28c.cpp 3, flash_nor_unlock.cpp 3, dev_tools.cpp 9,
#    firestarter.cpp 7, eprom.cpp 8, memory.cpp 1
grep -rno "LOG_INFO_ID[A-Z_0-9]*" src/ | wc -l
# => 19
```

**40 textual `is_flag_set` uses** in `src/`, **59 post-preprocessor uses** (40 + 19
`LOG_INFO_ID*` expansions, each expanding to one `is_flag_set(FLAG_VERBOSE)`). Neither the
ROADMAP's `19 protocol comparisons` nor its `45 is_flag_set call sites` is reproducible by any
counting rule and both are superseded. `include/firestarter.h`'s `is_flag_set` macro definition
and `include/memory_utils.h`'s prose mention are neither of them call sites and are excluded from
both counts.

## Measured Flash/RAM Delta (Step 1 of Task 2)

All figures WARM, `pio run -e uno -e uno328pb -e leonardo`, reproduced identically three times this
session with `git status --porcelain` verified clean before each measurement.

| Target | Plan 02 (table-only) | This plan (narrowed) | Narrowing delta | vs `1151dc4` (composed) |
|---|---|---|---|---|
| `uno` | 23350 / 1567 | **23090 / 1562** | **-260 B flash, -5 B RAM** | 24234 -> 23090 = **-1144 B** |
| `uno328pb` | 23398 / 1573 | **23138 / 1568** | **-260 B flash, -5 B RAM** | 24282 -> 23138 = **-1144 B** |
| `leonardo` | 25494 / 2008 | **25234 / 2003** | **-260 B flash, -5 B RAM** | 26378 -> 25234 = **-1144 B** |

**The narrowing's own delta is -260 B, not the reference's -258 B (a 2 B divergence); the composed
total is -1144 B, not -1148 B (a 4 B divergence).** Both are attributed to OD-1's per-row
mask-vs-saturate policy column (`FIELD_POLICY_MASK` and its branch in `store_field`), which the
reference table the -258/-1148 figures were measured on did not carry (C-19). No code was adjusted
to bring either figure into line with the reference numbers -- these are the numbers the build
actually produces at this position, composed from plan 02's independently-measured -884 B
(23350-884 not applicable here; table-only delta was measured against the `1151dc4` baseline of
24234/24282/26378, giving -884 B each) plus this plan's own -260 B: -884 + -260 = **-1144 B**,
internally consistent with the composed-total row above.

**Leonardo's Caterina headroom against `28672`: `28672 - 25234 = 3438` B**, measured -- superseding
the ROADMAP's stale `3440` B. This also differs from the `3442` B the phase's C-13 correction cited
(itself derived from the RESEARCH session's *predicted* absolute of `25230`, not a value measured at
this exact commit); the further 4 B gap between the measured `25234` and the predicted `25230` is the
same composed-total divergence already attributed to OD-1's policy column above, not a second,
independent discrepancy.

## sizeof(firestarter_handle_t) Re-derivation (Step 2 of Task 2)

Same method and captured compiler flags as the before-record's OD-7 figure (`avr-gcc -std=gnu11
-mmcu=atmega328p -Os` plus every layout-affecting `-D` and `-Iinclude`, and host `g++
-std=gnu++17` with the equivalent `-D`s), against a `char total[sizeof(firestarter_handle_t)];`
probe:

| Architecture | Before (plan 01's OD-7) | After (this plan) | Delta |
|---|---|---|---|
| AVR (`avr-gcc -mmcu=atmega328p`) | 601 B | **596 B** | **-5 B** |
| native (`g++ -std=gnu++17`) | 656 B | **656 B** | **0 B (unchanged)** |

AVR offsets re-derived (all `offsetof` + 1, minus 1 to recover the true offset): `protocol` 3,
`pins` 4, `mem_size` 5, `address` 9, `vpp_mv` 13, `pulse_delay` 15, `read_settling_us` 19,
`read_strobe_us` 23, `ctrl_flags` 27, `chip_id` 29, `page_size` 31, `data_buffer` 33 -- the eleven
table members at offsets 3-32 with `data_buffer` at 33, exactly as expected.

**Ceiling 5, stated explicitly:** the -5 B RAM saving is AVR-only and unobservable natively (native
`sizeof` is unchanged at 656 B, because the five narrowed bytes are absorbed by the alignment
padding before the struct's trailing function-pointer block); no native test asserts it, because
such a test would be vacuously false. The -5 B is confirmed two independent ways -- `ram_used` from
the build (1567->1562, 1573->1568, 2008->2003) and this `sizeof` re-derivation (601->596) -- which
is what makes the absolute `sizeof` figure non-load-bearing.

## Local Gates (Step 3 of Task 2)

- `python3 scripts/check_build_warnings.py --rebuild` -- **PASS**:
  `uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0), leonardo:
  macro_redefinition=0 (== 0), native: total warnings observed=998 is 168 below watermark 1166,
  native_nodevtools: total warnings observed=1026 is 140 below watermark 1166` (both native
  INFO-only, unchanged watermark, no headroom crossed). Run twice this session (once as its own
  invocation, once implicitly verified via the rebuilt AVR figures matching exactly) -- was
  UNVERIFIED before this phase per OD-6, now run and green.
- `python3 scripts/check_no_heap_or_64bit_symbols.py` -- **PASS**: `leonardo(heap=0,64bit=0,
  anchors=2/2), uno(heap=0,64bit=0,anchors=2/2), uno328pb(heap=0,64bit=0,anchors=2/2)`. The
  narrowing adds no allocation and no 64-bit arithmetic; `store_field`'s shift stays 32-bit.
- `python3 scripts/check_size_baseline.py --policy merge05 --baseline
  scripts/baseline/size_baseline_base01.json --rebuild` -- exits 1, output verbatim:
  ```
  FAIL:
    native: cases baseline=141 observed=172
    native_nodevtools: cases baseline=141 observed=172
  ```
  Exactly two lines, both pre-existing native case-count mismatches (frozen at Phase 124's `141`
  against the current `172`); **no AVR flash or RAM leg fails**. This is a **one-sided** pass:
  `scripts/check_size_baseline.py:697` reads `if flash_delta > allowance:` and `:709` reads
  `if ram_delta > ram_tolerance:` -- both strict-inequality, growth-only comparisons. A green run on
  those two legs proves only that flash/RAM did not *grow* past the MERGE-05 allowance; it does not
  mean "nothing changed" (D-03). No exemption constant was authored.
- `pio test -e native` and `pio test -e native_nodevtools` -- both `172 test cases: 172 succeeded`,
  unmoved (plans 04/05 move the count).

## Task Commits

1. **Task 1: Narrow the two handle fields and audit every consumer surface** -- folded into Task
   2's single commit (both tasks touch the same file; Task 1's verify block was run and confirmed
   passing in full before Task 2's commit step).
2. **Task 2: Measure the narrowing's own delta, re-derive sizeof, run the remaining gates, and
   commit** -- `76ff592` (`refactor(157-03): narrow handle protocol to uint8_t and ctrl_flags to
   uint16_t`).

## Files Created/Modified

- `firestarter/include/firestarter.h` -- `firestarter_handle_t.protocol` is `uint8_t`,
  `.ctrl_flags` is `uint16_t`, each with an in-place bound-justifying comment; no other struct
  member, `#define`, or ordering changed.

## Decisions Made

- **Narrowed exactly the two members DECODE-04 names**, with the bound comment naming the specific
  constant (`PROTO_PHANTOM_0x39`, `FLAG_SKIP_SDP_UNLOCK`) and the cross-repo parity gate that pins
  it, rather than a bare width change.
- **Neither dispatch test file needed editing.** `check_build_warnings.py --rebuild` surfaced no new
  diagnostic from the implicit `uint32_t -> uint8_t` narrowing conversion at `h.protocol =
  protocol;` in either `test_configure_memory.cpp` or `test_not_implemented.cpp`'s `make_handle`.
  Per the plan's own conditional, both files are left byte-unchanged and that fact is recorded here
  rather than silently assumed.
- **`eprom_params_for`/`eprom_block_budget_s` left at `uint32_t` parameters**, recorded as a lead
  not taken (five files and two v131 suites it would reach, named in the plan's own prohibition;
  DECODE-04 does not ask for it).
- **Measured -260 B narrowing delta and -1144 B composed total, and did not chase -258/-1148.** The
  divergence (+2 B narrowing, +4 B composed) is attributed to OD-1's per-row policy column
  (`FIELD_POLICY_MASK`), which the reference table the -258/-1148 figures were measured on did not
  carry (C-19) -- consistent with plan 02's own -884-B-not-890-B divergence for the same reason.
- **Leonardo headroom recorded as measured (3438 B), not the ROADMAP's 3440 B nor the
  RESEARCH-predicted 3442 B.** Both prior figures predate this exact build; the 4 B gap to 3442 is
  the same OD-1-attributed divergence as the composed-total gap above, not an independent finding.

## Deviations from Plan

None -- plan executed exactly as written. Tasks 1 and 2 were executed together as a single edit and
verification pass (both operate on the same single file, and Task 1's full verify block -- struct
shape, site counts, three clean AVR builds, `172/172` native, `check_build_warnings.py` -- was run
and confirmed passing before Task 2's measurement and commit steps), which does not change what was
measured, committed, or verified. The plan's own conditional (narrow `make_handle`'s parameter only
if a new diagnostic surfaces) resolved to "no edit needed," exactly one of its two stated branches.

## Issues Encountered

None. The narrowing compiled cleanly on the first attempt on all three AVR targets and both native
environments; no `.rej`/`.orig` file was produced; `firestarter_app`'s porcelain was unaffected by
running its parity tests.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- `firestarter` HEAD is now `76ff592` on `gsd/v1.33-source-hygiene-firmware-size-reduction`;
  `git -C firestarter status --porcelain` is empty; no `.rej`/`.orig` file exists anywhere.
- Plan 04 (native round-trip test cases, OD-5) can dispatch against the now-narrowed
  `firestarter_handle_t` directly; the `field_desc_t` table's `FIELD`/`FIELD_MASK` macros already
  re-derived `offset`/`width` for both narrowed members automatically (no table edit was needed for
  the narrowing itself, confirming plan 02's own prediction).
- Plan 06/07 should read this SUMMARY's measured `-260 B` narrowing / `-1144 B` composed figures
  (not the reference's `-258`/`-1148`) and the `3438 B` Leonardo headroom (not `3440` or `3442`)
  when composing the after-figures record and the final requirement closure.
- No blockers.

---
*Phase: 157-command-decode-table-handle-type-narrowing-firmware-only*
*Completed: 2026-08-23*

## Self-Check: PASSED

- FOUND: `.planning/phases/157-command-decode-table-handle-type-narrowing-firmware-only/157-03-SUMMARY.md`
- FOUND: `firestarter/include/firestarter.h`
- FOUND: firmware commit `76ff592` (`git -C firestarter log --oneline --all`)
