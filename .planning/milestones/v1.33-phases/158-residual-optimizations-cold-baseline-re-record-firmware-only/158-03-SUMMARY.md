---
phase: 158-residual-optimizations-cold-baseline-re-record-firmware-only
plan: "03"
subsystem: firmware
tags: [flash-5v-page, udivmodsi4, avr-objdump, coverage-gap, land-06, decline]

# Dependency graph
requires:
  - phase: 158-01
    provides: "158-before-figures.md — pre-phase cold ledger, superseded for this plan's own position by 158-02's post-LAND-05 cold figures"
  - phase: 158-02
    provides: "jsmntok_t narrowed to 6 B; post-LAND-05 cold AVR figures (uno 22952/1434, uno328pb 23000/1440, leonardo 25098/1875) — the position this plan measures against"
provides:
  - "LAND-06 decline record: measured mask cost at this phase's own position (+22/+24/+22 B flash, 0 B RAM), the two __udivmodsi4 call sites witnessed present/removed by symbol-range disassembly on all three ELFs, the image-wide call-site count proving no linkage saving"
  - "Enumerated zero-behavioural-coverage finding over test_val_5v_page's 14 registered cases, correcting F-6's 'the one case' framing to the two cases that actually execute the write path"
  - "The declined-alternative oracle shape and its native case-count cost, and the four-fact disconnection paragraph separating this criterion from the w27c512-write-slow-3x work and from algorithm 13's validating mask resolver"
affects: ["158-06 (after-figures, transcribes this plan's decline record verbatim)", "158-07 (ROADMAP/REQUIREMENTS scope correction, cites this plan's own +22/+24/+22 figures rather than the research's)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Throwaway detached git worktree at HEAD, mask applied only inside it, torn down and pruned before task end, tracked tree proven byte-unchanged before and after (OD-2's isolation mechanism)"
    - "Symbol-range avr-objdump disassembly (avr-nm --print-size address+size, then avr-objdump --start-address/--stop-address) as the only valid witness for an inlined helper's instruction content — source reading is insufficient once gcc inlines both call-site helpers"

key-files:
  created: []
  modified: []

key-decisions:
  - "OD-2 executed (decline confirmed, not merely re-stated): the mask's cost was re-measured at this plan's own final position (post-158-02, HEAD 8e126f2) inside a throwaway worktree, rather than quoting 158-RESEARCH.md's F-6 figures, which were measured at a different tree position (pre-LAND-05, 785e644)."
  - "Correction to F-6's enumeration: TWO registered cases execute flash_5v_page_write_execute (test_5v_page_write_execute_emits_sdp AND test_5v_page_write_execute_no_vpp), not the single case F-6 named -- both drive the identical 4-byte handle from make_write_handle_with_data(), so the coverage gap conclusion is unchanged but the case count backing it is corrected here."

requirements-completed: [LAND-06]

# Coverage metadata
coverage:
  - id: D1
    description: "LAND-06 declined with a first-party measurement: mask cost re-measured cold on both sides at this phase's own position (+22/+24/+22 B flash, 0 B RAM on uno/uno328pb/leonardo), agreeing with REQUIREMENTS LAND-06's flat +22 B on uno and leonardo, 2 B low on uno328pb (same disagreement F-6/C-3 already named)"
    requirement: "LAND-06"
    verification:
      - kind: other
        ref: "avr-nm --print-size + avr-objdump --start-address/--stop-address over flash_5v_page_write_execute on uno/uno328pb/leonardo ELFs, before and after the mask, inside a throwaway worktree at /tmp/gsd-158-mask/firestarter (torn down)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Zero behavioural native coverage of the algorithm-5 boundary predicates established by enumerating all 14 registered test_val_5v_page cases; the two that execute the write path drive a 4-byte write against a 256-byte page size, which reaches neither predicate's non-trivial branch"
    requirement: "LAND-06"
    verification:
      - kind: unit
        ref: "pio test -e native -f \"*test_val_5v_page*\" -- 14 test cases: 14 succeeded"
        status: pass
    human_judgment: false

# Metrics
duration: ~35min
completed: 2026-08-24
status: complete
---

# Phase 158 Plan 03: LAND-06 decline record — measured mask cost, witnessed divisions, enumerated coverage gap Summary

**LAND-06 discharged as a recorded decline: the mask's flash cost re-measured cold at this phase's own final position (+22/+24/+22 B, 0 B RAM), the two `__udivmodsi4` calls inside `flash_5v_page_write_execute` witnessed present and removed by symbol-range disassembly on all three AVR images, the image-wide call-site count proving the helper stays linked either way, and the boundary path's zero behavioural coverage established by enumerating all 14 registered cases — with `src/proms/flash_5v_page.cpp` byte-unchanged and no commit created.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-08-24
- **Tasks:** 2 (both executed; neither produces a commit, per plan)
- **Files modified:** 0 (measure-and-record plan; the mask existed only inside a throwaway worktree, removed before task end)

## Accomplishments

### Task 1 — the measured decline, at this phase's own position

**Anchors.** `FW_SHA` = `8e126f2f743ed4209c8aab6dd7f0266f979a6080` (HEAD at plan start, plan 02's last commit). `git status --porcelain` empty before and after. Pre-probe `git worktree list`: `/workspaces/firestarter` (`8e126f2`) + `/workspaces/firestarter_py32_ci` (`ad47c3b`) — matched exactly after teardown.

**STEP 1 — baseline cold figures, in the probe location** (`git worktree add --detach /tmp/gsd-158-mask/firestarter 8e126f2`, `rm -rf .pio/build/<env>` + one `pio run -e <env>` per target, zero `warning:` lines each):

| Env | Flash (COLD) | RAM (COLD) | Cross-check vs plan 02's cold figures |
|---|---|---|---|
| `uno` | 22952 B | 1434 B | **Agrees exactly** (158-02-SUMMARY.md: 22952/1434) |
| `uno328pb` | 23000 B | 1440 B | **Agrees exactly** (158-02-SUMMARY.md: 23000/1440) |
| `leonardo` | 25098 B | 1875 B | **Agrees exactly** (158-02-SUMMARY.md: 25098/1875) |

The worktree probe reproduces plan 02's cold position exactly, which is what makes the mask delta below a like-for-like number measured in one location.

**STEP 2 — the two divisions, witnessed in the linked image, before the mask:**

`avr-nm --print-size` on the `uno` ELF: `flash_5v_page_write_execute` at address `0x2d68`, size `0x1d4` = **468 B**. `avr-objdump -d --start-address=0x2d68 --stop-address=0x2f3c`:

```
2e44: call 0x57f6 ; <__udivmodsi4>
2e64: call 0x2bde ; <flash_util_byte_flipping>
2e8a: call 0x57f6 ; <__udivmodsi4>
2ef4: call 0xece  ; <rurp_log_id>
```

Exactly **2** `__udivmodsi4` calls inside the symbol range, both in the loop body. `flash_5v_page_page_size` and `flash_5v_page_wait_for_page_write` are both fully inlined (no symbols of their own — confirmed by their absence from `avr-nm`'s output), which is why the image, not the C source, is the only valid witness.

Repeated on `uno328pb` (address `0x2df8`, size `0x1d4` = 468 B) and `leonardo` (address `0x327a`, size `0x1d4` = 468 B): **identical shape** on all three — same 2 calls inside the range, same 468 B function size.

**Image-wide `__udivmodsi4` count and helper size, before the mask:** `__udivmodsi4` itself is `0x44` = **68 B** on all three ELFs. Image-wide call-site count is **11** on `uno`, `uno328pb`, and `leonardo`. A surviving caller (source-level, since the release build carries no debug line info for `avr-addr2line` to resolve inlined call sites): `src/proms/eprom_budget.cpp:109` — `uint32_t rem = per_byte_us % 1000000UL;` inside `eprom_block_budget_s`.

**STEP 3 — the mask side, in the same location.** Applied inside the worktree only: hoisted `const uint32_t page_mask = page_size - 1;` immediately above the per-byte loop (no validating resolver — see Decisions below for why one would be dead code on algorithm 5), and rewrote both boundary predicates from `% page_size` to `& page_mask`. Cold rebuild, all three targets, zero warnings each:

| Env | Flash (mask) | RAM (mask) | Δ Flash | Δ RAM |
|---|---|---|---|---|
| `uno` | 22974 B | 1434 B | **+22 B** | **0** |
| `uno328pb` | 23024 B | 1440 B | **+24 B** | **0** |
| `leonardo` | 25120 B | 1875 B | **+22 B** | **0** |

Post-mask, `flash_5v_page_write_execute` on `uno`: address unchanged (`0x2d68`), size grown `0x1d4 → 0x1ea` = **468 B → 490 B**. Symbol-range disassembly over the new range: **0** `__udivmodsi4` calls. Image-wide count: **9** (dropped by exactly 2 from 11, still non-zero) — confirming the helper stays linked and there is **no linkage saving**.

**STEP 4 — the deltas against the criterion's own figure.** `+22 / +24 / +22 B` flash, `0 B` RAM on every target. **This agrees with REQUIREMENTS LAND-06's flat `+22 B (measured)` on `uno` and `leonardo`, and is 2 B low on `uno328pb`** (`+24 B` observed vs `+22 B` claimed) — the identical disagreement already opened as C-3 in `158-before-figures.md` and in `158-RESEARCH.md` F-6, now independently reproduced at this plan's own, later tree position (post-jsmntok_t-narrowing) rather than quoted from either source. The two measurements agreeing across two different tree positions is itself informative: the mask's cost is attributable entirely to `flash_5v_page.cpp` and is unaffected by the unrelated `jsmntok_t` narrowing landed in between.

**STEP 5 — teardown, proven.** `git worktree remove --force /tmp/gsd-158-mask/firestarter`, `git worktree prune`, `rm -rf /tmp/gsd-158-mask`. Verified: `/tmp/gsd-158-mask` absent; `git worktree list` matches its pre-probe output exactly (2 entries, same SHAs); `git status --porcelain` empty; `git diff HEAD --name-only -- src/proms/flash_5v_page.cpp` empty (0 files); `HEAD` still `8e126f2f743ed4209c8aab6dd7f0266f979a6080`. No commit created anywhere, including inside the worktree. The plan's own automated verify block (a fresh cold `uno` build in the tracked, unmasked tree) was also run and passed: 2 `__udivmodsi4` calls in range, 11 image-wide, `% page_size` still present in the tracked file, tree clean throughout.

**Source assertion satisfied:** the mask probe touched only the two boundary-predicate lines and added only the one `const uint32_t page_mask` local — no validating resolver was introduced. A resolver would be dead code on algorithm 5 because `flash_5v_page_page_size(mem_size)` derives the page size internally from three literal returns (64/128/256, each provably a power of two by inspection), unlike algorithm 13's `eeprom28c_page_mask`, whose input arrives from the host wire (`handle->page_size`) and could in principle be anything.

### Task 2 — the enumerated coverage gap and the decline's reasoning

**STEP 1 — enumeration, not characterisation.** `test/native/avr/test_val_5v_page/test_val_5v_page.cpp` registers **14** cases (`grep -c RUN_TEST` = 14, all named at `:506-529`). Read case-by-case:

| # | Case | Executes `flash_5v_page_write_execute`? |
|---|---|---|
| 1 | `test_5v_page_0x05_read_configure_no_vpp` | No — `configure_memory` only (dispatch phase) |
| 2 | `test_5v_page_0x05_write_configure_no_vpp` | No — dispatch phase only |
| 3 | `test_5v_page_0x35_read_configure_no_vpp` | No — dispatch phase only |
| 4 | `test_5v_page_0x35_write_configure_no_vpp` | No — dispatch phase only |
| 5 | `test_5v_page_0x39_read_configure_no_vpp` | No — dispatch phase only |
| 6 | `test_5v_page_0x39_write_configure_no_vpp` | No — dispatch phase only |
| 7 | `test_5v_page_write_execute_emits_sdp` | **Yes** — calls `h.firestarter_operation_main(&h)` |
| 8 | `test_5v_page_write_execute_no_vpp` | **Yes** — calls `h.firestarter_operation_main(&h)` |
| 9 | `test_5v_page_write_init_no_blank_check_with_flag_clear_erase02` | No — calls `firestarter_operation_init`, never `_main` |
| 10 | `test_5v_page_lock_status_dispatch` | No — `configure_memory` only |
| 11 | `test_5v_page_lock_status_pinned_sequence` | No — no handle call at all, constant-literal checks |
| 12 | `test_5v_page_lock_status_no_vpp` | No — calls `flash_5v_page_read_protection_execute` |
| 13 | `test_5v_page_lock_status_raw_byte_fidelity` | No — calls `flash_5v_page_read_protection_execute` |
| 14 | `test_5v_page_lock_status_mode_bracketing` | No — calls `flash_5v_page_read_protection_execute` |

**Correction to 158-RESEARCH.md F-6:** F-6 (`:517`) names only `test_5v_page_write_execute_emits_sdp` as the write-path-executing case. Reading the file this session shows **two** cases execute the write path — `test_5v_page_write_execute_emits_sdp` (Test 1, the SDP-signature assertion) and `test_5v_page_write_execute_no_vpp` (Test 2, the VPP-safety assertion) — both built from the identical `make_write_handle_with_data()` helper (`:213-228`): `mem_size = 524288` (512 KB), `address = 0`, `data_size = 4`. The coverage-gap conclusion is unchanged by this correction (both cases drive the same 4 bytes), but the case count backing it is now accurate.

`flash_5v_page_page_size(524288)`: `524288 > 65536` and `524288 > 262144`, so `page_size = 256` (the third literal return). A 4-byte write starting at address 0 against a 256-byte page:

- `is_page_start = (address % page_size) == 0` (or, post-mask, `& page_mask`): true only at `i=0` (`address=0`), where it is **confounded** with `is_first_byte` (also true) via the `||` — the predicate's own value cannot be independently observed there. For `i=1,2,3` (`address=1,2,3`), trivially false (far short of 256).
- `reached_page_end = ((address+1) % page_size) == 0`: for the last byte (`i=3`, `address=3`), `(4) % 256 = 4 ≠ 0` — **never true**. The wait is triggered only via `is_last_byte`, never via crossing the 256-byte boundary.

**Enumerated conclusion:** no case in the tree exercises either boundary predicate's non-trivial (true, boundary-crossing) behaviour. A botched mask edit — e.g., using `page_size` instead of `page_size - 1` for the mask, or an off-by-one in either predicate — would be caught by no leg in this suite.

**The one existing safety assertion, confirmed green and untouched:** `test_5v_page_write_execute_no_vpp` (case 8) pins that `flash_5v_page_write_execute` emits no `CTRL_VPP_REGULATOR_ENABLE` / `CTRL_VPP_P1_ENABLE` bit during the operation phase. It remains green throughout this plan's measurement (confirmed by the `pio test` run below) and is the only existing coverage over this function beyond dispatch wiring — but it asserts VPP-safety, not boundary correctness, so it provides no defence against a botched mask edit either.

**Suite run, confirming all 14 cases green:** `pio test -e native -f "*test_val_5v_page*"` → `14 test cases: 14 succeeded`. `test/native/avr/test_val_5v_page/` byte-unchanged against HEAD throughout.

**STEP 2 — the declined alternative and its cost.** The oracle that would make a taken mask honest (from `158-RESEARCH.md` F-6, re-stated and not re-derived here since D-02 forbids any bench addition and this oracle is source-level counting, not timing): a counting variant of the existing `recording_contains_sdp_signature` predicate, driven by a handle with `mem_size = 32768` (→ `page_size = 64`), `address = 0`, `data_size = 128` — spanning exactly two pages — asserting **exactly 2** SDP `FLASH_ENABLE_WRITE` signatures (page starts at byte 0 and byte 64) and **exactly 2** page-end poll windows (at byte 63 and byte 127), proven RED against a deliberately wrong mask (e.g. `page_size` instead of `page_size - 1`) before being trusted. Adding it moves the native case count from **184 to 185 or 186** (one case for a combined start+end count, or two for separate start-count and end-count legs), which feeds directly into LAND-01's `native_envs` figures and both `captured_test_native*_summary.log` fixtures — meaning it would have had to land **before** plan 04's re-record, not after. This alternative was available and is **declined here**, not omitted: naming its cost is what makes the decline a decision.

**STEP 3 — the runtime half, stated honestly.** D-02 forbids a bench criterion for this milestone; only silicon could measure the runtime win a mask would buy (fewer AVR division-subroutine calls per byte). Native trace stubs record no time — `delay()` and `delayMicroseconds()` are unstubbed in `test/native/avr/_shared/host_stubs_common.inc` — so a native trace diff can attest register-write sequence only, never duration. **The runtime half is therefore unquantified by construction, not by omission.** This SUMMARY contains no numeric runtime estimate, no percentage speedup, and no "likely faster" framing anywhere.

**STEP 4 — the disconnection paragraph, verbatim for plan 06:**

> This change is scoped to the **algorithm-5 flash-page write path only** — `configure_flash_5v_page` (`src/proms/flash_5v_page.cpp:41`), reached from `configure_memory`'s dispatch for protocols `PROTO_FLASH_5V_PAGE` (`0x05`), `PROTO_PHANTOM_0x35`, and `PROTO_PHANTOM_0x39` (confirmed both from the suite's own `test_5v_page_0x05/0x35/0x39_*` cases, `:506-515`, and from `firestarter/CLAUDE.md`'s protocol dispatch table). It is **not** connected to the w27c512-write-slow-3x work, which rewrote `eprom_write_execute` in `src/proms/eprom.cpp` — a different file, a different handler, a different protocol family (the `0x07`/`0x08`/`0x0B` UV-EPROM family), and a per-byte high-voltage (VPE) settle-time problem rather than a division-cost problem. The two share no code and no cause. REQUIREMENTS.md's "Out of Scope" section separately rules `eprom_write_execute` untouchable for this milestone ("Restructuring `eprom_write_execute`... Lead closed during scoping"). Separately, algorithm 13's masked page-end predicate in `src/proms/eeprom_28c.cpp:628-636,752` is a **different problem, kept distinct on purpose**: its page size (`handle->page_size`) arrives from the host wire and could be anything, so it needs the validating resolver it has (`eeprom28c_page_mask`, rejecting non-powers-of-two and falling back to a conservative floor); algorithm 5's page size is derived internally by `flash_5v_page_page_size` from three literal returns that are provably powers of two, so a bare mask suffices there and a validator would be dead code. `src/proms/eeprom_28c.cpp:21` already labels `flash_5v_page_page_size()` a "READ-ONLY ANALOG, byte-frozen, NOT adopted here" — the non-adoption runs in both directions.

**STEP 5 — the decline record assembled for plan 06** (all eight items, each with its evidence):

1. Measured per-target flash cost: `+22 / +24 / +22 B` (`uno` / `uno328pb` / `leonardo`), via cold `pio run` before/after the mask inside the throwaway worktree.
2. RAM cost: `0 B` on all three targets (identical `pio run` output).
3. Two witnessed division sites: `avr-nm --print-size` + symbol-range `avr-objdump -d --start-address=... --stop-address=...` over `flash_5v_page_write_execute` — 2 calls before, 0 after, on all three ELFs, identical shape.
4. Image-wide call-site count: **11 → 9** (dropped by exactly 2, still non-zero); helper size **68 B** unchanged; surviving user named — `src/proms/eprom_budget.cpp:109`.
5. Enumerated coverage gap: 14 registered cases, 2 execute the write path (both via the identical 4-byte handle), neither boundary predicate's non-trivial branch is reached by either.
6. Declined alternative: a two-window counting oracle over a 2-page (128-byte) write against a 64-byte page size, RED-first against a deliberately wrong mask, costing 1-2 native cases (`184 → 185/186`) and requiring sequencing before plan 04.
7. Runtime half: unquantified by construction under D-02; trace-stub time limitation named; no estimate anywhere in this record.
8. Disconnection paragraph: verbatim above, all four facts present.

**Tree state confirmed clean at end of Task 2:** `git status --porcelain` empty; `git diff HEAD --name-only` over `src/proms/flash_5v_page.cpp`, `src/proms/eeprom_28c.cpp`, `src/proms/eprom.cpp`, and `test/native/avr/test_val_5v_page/` = 0 files; HEAD still `8e126f2` (plan 02's last commit, subject `test(158-02): pin the jsmn token layout as a region-scoped source contract`); no commit created by this plan.

## The honest coverage ceilings — stated, not implied

All twelve, restated per this phase's own convention (every plan, every SUMMARY, both phase records):

1. `check_size_baseline.py`, `check_build_warnings.py` and `check_no_heap_or_64bit_symbols.py` are invoked by NO CI workflow — every size gate this phase leans on is a **local-run obligation**.
2. But the checker IS executed in CI by its own paired pytest — `build.yml:161` `pytest tests/ -v`, ungated, on `push: branches: ['**','!beta']`. LAND-04's honest statement has **two clauses**.
3. The ARM half of LAND-05 is unverified locally unless plan 02's toolchain install succeeded (it did — both pre- and post-narrowing `py32f071` builds passed).
4. LAND-06's runtime half is unmeasurable in this milestone (D-02) — the decline this plan records rests on a size measurement plus a coverage gap, never on a runtime number.
5. The algorithm-5 page-boundary path has ZERO behavioural native coverage — this plan proves that by enumeration of all 14 registered cases, not by restating the claim (and corrects F-6's case count from one to two in the process).
6. `sizeof(jsmntok_t)` cannot be asserted in a native test — AVR gives 6 B, the host gives 12 B (not touched by this plan).
7. The native suite is load-flaky (D-04) — this plan ran `pio test -e native -f "*test_val_5v_page*"` once and it passed 14/14; no re-run was needed since no failure occurred.
8. A `/tmp` worktree run of `pytest tests/` silently skips 32 cross-repo legs — not exercised by this plan (no pytest run was needed; only `pio run`/`pio test` and `avr-nm`/`avr-objdump`).
9. `lib/jsmn/src/jsmn.h` carries a dead duplicate implementation — untouched by this plan.
10. LAND-07's conclusion is a budget argument, not an impossibility argument — untouched by this plan.
11. Every `file:LINE` citation this phase writes will be newly stale; Phase 159 remaps them exactly once (D-01, D-05). This SUMMARY's own citations (e.g. `eprom_budget.cpp:109`) are subject to the same rule.
12. The `firestarter` gitlink in the meta repo is drifted — pre-existing since Phase 154, operator-gated, not touched by this plan.

## Task Commits

**None.** Per this plan's own prohibitions ("Must NOT create any commit in either repository"), Task 1 and Task 2 are measure-and-record tasks with `files_modified: []` — no tracked file in `firestarter` or `firestarter_app` was edited, and the mask existed only inside a throwaway detached worktree that was removed and pruned before the task ended. The evidence and reasoning captured in this SUMMARY are handed to plan 06, which alone writes `.planning/v1.33/158-after-figures.md`.

**Plan metadata commit:** made in the meta repo only, covering this SUMMARY.md, STATE.md, and ROADMAP.md's plan-progress row (not its criteria prose, which stays untouched per the phase-wide constraint that plan 07 alone edits ROADMAP.md/REQUIREMENTS.md content).

## Files Created/Modified

None in `firestarter` or `firestarter_app`. `src/proms/flash_5v_page.cpp` is byte-unchanged against `HEAD` (`8e126f2f743ed4209c8aab6dd7f0266f979a6080`) — confirmed by `git diff HEAD --name-only` returning empty both after Task 1's teardown and after Task 2's enumeration.

## Decisions Made

- **OD-2 executed (LAND-06 DECLINED), confirmed rather than merely re-stated:** this plan's own cold, first-party measurement at this phase's own final position reproduces the criterion's `+22/+24/+22 B` flash / `0 B` RAM figures, and the enumerated coverage gap over all 14 registered `test_val_5v_page` cases is the stated reason for the decline, alongside the runtime half being unquantified by construction under D-02.
- **The declined alternative (taking the mask with a boundary test) is recorded with its own cost** — 1-2 native cases, sequencing before plan 04 — rather than left unstated, per the plan's own requirement that a decline name what it turned down.
- **F-6's case-count claim corrected:** two registered cases execute `flash_5v_page_write_execute`, not one; both use the identical 4-byte handle, so the coverage-gap conclusion is unaffected, but the record must not understate the case count that was actually read.

## Deviations from Plan

None — plan executed exactly as written. The correction to F-6's case count (Task 2, Step 1) is not a deviation from this plan's own instructions: the plan's `read_first` directs reading the whole suite file and enumerating every case as observed this session, which is exactly what surfaced the second write-path-executing case that the research document had not named.

## Issues Encountered

None. Both cold-build passes (baseline and mask side) completed with zero `warning:` lines on all three targets in one attempt each. The native suite passed 14/14 on the first run, so no D-04 re-run was needed. `avr-addr2line` returned no debug-line information for the release build's inlined call sites (expected — release builds strip line tables); the surviving `__udivmodsi4` call site was instead named from source (`src/proms/eprom_budget.cpp:109`), matching `158-RESEARCH.md` F-6's own citation.

## User Setup Required

None — no external service configuration required. No packages were installed (zero npm/pip/cargo/apt invocations this plan).

## Next Phase Readiness

- Plan 06 (`158-after-figures.md`) can transcribe this plan's eight-item decline record verbatim: measured cost (`+22/+24/+22 B` flash, `0 B` RAM), the witnessed division sites (2 → 0, both symbol-range confirmed on all three ELFs), the image-wide call-site count (`11 → 9`, helper stays linked, surviving user at `eprom_budget.cpp:109`), the enumerated coverage gap (2 of 14 cases execute the write path, neither reaches a boundary), the declined alternative's cost (1-2 native cases, must precede plan 04), the runtime half as unquantified by construction, and the four-fact disconnection paragraph.
- Plan 07 (ROADMAP/REQUIREMENTS scope correction) can cite this plan's own `+22/+24/+22 B` figures — re-measured at this phase's own position rather than the research's pre-LAND-05 position — as the number that backs LAND-06's decline, with the 2 B disagreement on `uno328pb` named (C-3, already opened in `158-before-figures.md`).
- `src/proms/flash_5v_page.cpp` remains on the modulo form; no `test_val_5v_page` case was added; the native case count stays at 184, undisturbed by this plan, so LAND-01's `native_envs` figures (plan 04's responsibility) are unaffected by anything in this plan.
- No blockers.

---
*Phase: 158-residual-optimizations-cold-baseline-re-record-firmware-only*
*Completed: 2026-08-24*

## Self-Check: PASSED

- FOUND: .planning/phases/158-residual-optimizations-cold-baseline-re-record-firmware-only/158-03-SUMMARY.md
- FOUND: firestarter/src/proms/flash_5v_page.cpp (confirmed byte-unchanged against HEAD via `git diff HEAD --name-only` returning empty)
- FOUND: firestarter HEAD unchanged at `8e126f2f743ed4209c8aab6dd7f0266f979a6080` (plan 02's last commit, `test(158-02): pin the jsmn token layout as a region-scoped source contract`)
- CONFIRMED: no commit created by this plan in `firestarter` (git log shows only plan 02's and plan 157-05's commits, nothing new)
- CONFIRMED: `git -C /workspaces/firestarter status --porcelain` empty; no worktree left behind (`/tmp/gsd-158-mask` absent; `git worktree list` matches pre-probe)
