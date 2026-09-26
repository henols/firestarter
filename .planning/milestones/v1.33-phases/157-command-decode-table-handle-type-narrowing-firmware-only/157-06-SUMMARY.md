---
phase: 157-command-decode-table-handle-type-narrowing-firmware-only
plan: "06"
subsystem: firmware-decode
tags: [configure_memory, switch-vs-if-chain, avr-gcc, dispatch, protocol, DECODE-07]

# Dependency graph
requires:
  - phase: 157-command-decode-table-handle-type-narrowing-firmware-only
    provides: "plan 03's narrowed handle->protocol (uint8_t), which changes the switched expression's width from 32 bits to 8 bits -- exactly the property this plan's measurement turns on"
provides:
  - "A first-party, three-target `switch`-vs-if-chain flash measurement taken at Phase 157's post-change position (uno/uno328pb/leonardo, all +18 B), superseding the survey's stale `uno` 25696/25678 pair"
  - "The dispatched value set enumerated from source: 17 distinct protocol values (13 named PROTO_* + 4 raw infeasibility-arm literals) spanning 0x05-0x39, density ~32%"
  - "The second rejection argument: firestarter/CLAUDE.md pins configure_memory's dispatch order as a source-of-truth contract, proven byte-unchanged since 1151dc4, so a switch conversion would require rewriting that document too"
  - "Proof that the branch-inventory golden (tests/golden/protocol_branch_inventory.json) is verified GREEN because this phase touches neither src/proms/eprom.cpp nor src/proms/memory.cpp -- distinct from Phase 156's re-derive-in-commit outcome"
  - "The consolidated DECODE-07 discharge section, raw material for 157-after-figures.md (plan 07)"
affects: [157-07-PLAN]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Throwaway detached git worktree (leaf dir literally 'firestarter') for measuring a rejected code-shape alternative without ever committing it, discarded with checkout+remove+prune and proven absent by blob-hash and rev-list-count equality"

key-files:
  created: []
  modified: []

key-decisions:
  - "The switch variant costs exactly +18 B flash on all three AVR targets at this position (uno 23108 vs 23090, uno328pb 23156 vs 23138, leonardo 25252 vs 25234), zero RAM delta -- the if-chain stays rejected, now for a freshly measured reason rather than a stale one"
  - "The fresh +18 B figure numerically matches the survey's stale +18 B claim, but this is stated as a coincidence of magnitude, not a confirmation of the same measurement: the survey's pair (uno 25696/25678) was taken on a 32-bit switched expression at a different tree position roughly 2.6 KB heavier; this plan's pair is taken on the now-8-bit switched expression at 785e644. Two different measurements landing on the same delta is recorded, not treated as validating the old absolutes"
  - "Both rejection arguments recorded: (1) the measured +18 B flash penalty on all three targets, (2) firestarter/CLAUDE.md pins configure_memory's if-chain dispatch order as a source-of-truth contract (Protocol Dispatch section, 7 numbered steps matching the file's structure), proven byte-unchanged since 1151dc4 -- a switch conversion would require rewriting that document too"
  - "Plan-authored path defect found and worked around (Rule 3): the plan's Task 2 action/verify text names 'firestarter_app/tests/test_protocol_branch_inventory.py', but that file lives at firestarter/tests/test_protocol_branch_inventory.py (the firmware repo's own tests/, run directly with system python3, not via pio test). Ran it from the correct location; test_dispatch_mirror.py and test_parse_gate_admission.py are correctly located in firestarter_app/tests/ as the plan states"

patterns-established: []

requirements-completed: []

coverage:
  - id: D1
    description: "The switch alternative is built once in a throwaway detached worktree (leaf directory named exactly 'firestarter'), measured on all three AVR targets at this phase's post-change position, and discarded -- src/proms/memory.cpp in the committed tree is proven byte-identical to its blob at 1151dc4 both before and after"
    requirement: "DECODE-07"
    verification:
      - kind: other
        ref: "git hash-object src/proms/memory.cpp == git show 1151dc4:src/proms/memory.cpp | git hash-object --stdin (matched); grep -c 'switch (handle->protocol)' src/proms/memory.cpp => 0; git worktree list before/after identical; git rev-list --count HEAD == 852 both before and after; /tmp/157-sw-probe/firestarter does not exist"
        status: pass
    human_judgment: false
  - id: D2
    description: "Fresh three-target switch/if-chain/delta measurement recorded with verbatim pio run commands, plus a behavioural-equivalence check (pio test -e native, 184/184) proving the variant is a valid comparator"
    requirement: "DECODE-07"
    verification:
      - kind: other
        ref: "pio run -e uno -e uno328pb -e leonardo in the probe tree: uno 23108/1562, uno328pb 23156/1568, leonardo 25252/2003, zero warning: lines on a cold rebuild; pio test -e native in the probe tree: 184 test cases: 184 succeeded"
        status: pass
    human_judgment: false
  - id: D3
    description: "The survey's stale uno 25696/25678 pair is recorded with its provenance and marked SUPERSEDED as absolutes, alongside -- never in place of -- the fresh pair"
    requirement: "DECODE-07"
    verification:
      - kind: other
        ref: "See 'The stale survey pair' section below; provenance named as .planning/notes/firmware-size-reduction-survey.md, C-10 cited"
        status: pass
    human_judgment: false
  - id: D4
    description: "The second rejection argument (CLAUDE.md's dispatch-order contract) is recorded, and the branch-inventory golden plus both neighbouring host scanning gates are proven green for their stated reasons without the golden being touched"
    requirement: "DECODE-07"
    verification:
      - kind: other
        ref: "git diff --name-only 1151dc4 HEAD -- CLAUDE.md => empty; git hash-object src/proms/eprom.cpp matches golden's blob_shas entry; python3 -m pytest tests/test_protocol_branch_inventory.py (run from /workspaces/firestarter) => 7 passed; python3 -m pytest tests/test_dispatch_mirror.py tests/test_parse_gate_admission.py (from /workspaces/firestarter_app) => 9 passed"
        status: pass
    human_judgment: false

duration: 30min
completed: 2026-08-23
status: complete
---

# Phase 157 Plan 06: DECODE-07 Switch-Alternative Measurement Summary

**Built the rejected `configure_memory` switch alternative once in a throwaway detached worktree, measured a uniform +18 B flash penalty on all three AVR targets at Phase 157's post-narrowing position, confirmed behavioural equivalence (184/184 native), and discarded the variant -- leaving `src/proms/memory.cpp` and `firestarter/CLAUDE.md` byte-unchanged since `1151dc4`.**

## Performance

- **Duration:** ~30 min
- **Tasks:** 2 (build/measure/discard the switch variant; record the second rejection argument + prove golden gates green)
- **Files modified:** 0 in `firestarter` (this plan's contract). 1 in the meta repo (this SUMMARY.md).

## Accomplishments

- Enumerated `configure_memory`'s dispatched value set directly from `src/proms/memory.cpp` (`:99-142`) and `include/proto_constants.h`: **17 distinct protocol values** reach a non-generic arm -- 13 named `PROTO_*` constants (`0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39`) plus 4 raw-hex named-infeasibility literals (`0x11, 0x2A, 0x2B, 0x2C`), spanning `0x05` to `0x39` (a range of 53 values) for a density of **17/53 ≈ 32%**. Confirmed 17 `handle->protocol ==` comparisons (`grep -ro`), matching plan 03's own count exactly.
- Recorded the if-chain's own baseline at this position, `pio run -e uno -e uno328pb -e leonardo` on the committed tree: `uno` 23090/1562, `uno328pb` 23138/1568, `leonardo` 25234/2003 -- **exactly** plan 05's post-change figures, confirming the comparison is against a non-moving baseline.
- Built the probe worktree (`git worktree add --detach /tmp/157-sw-probe/firestarter HEAD`, leaf directory exactly `firestarter`), converted `configure_memory`'s seven if-arms into a single `switch (handle->protocol)` with one `case` label per dispatched value (grouped identically to the if-chain's groupings, same handler calls, same fail-closed `default`), and measured all three targets, twice (once warm, once after a targeted `pio run -t clean`): `uno` **23108**/1562, `uno328pb` **23156**/1568, `leonardo` **25252**/2003 -- zero `warning:` lines on the cold rebuild, byte-identical across both runs.
- **The delta is +18 B flash on all three targets, 0 B RAM delta, at this phase's post-narrowing (uint8_t) position.** The `switch` alternative is worse everywhere measured, matching the survey's `+18 B` claim in magnitude even though it was measured on a different tree position and a different-width switched expression -- recorded as a coincidence of magnitude, not evidence that the stale absolutes were still correct.
- Ran `pio test -e native` in the probe tree as the required behavioural-equivalence sanity check: **184 test cases: 184 succeeded**, matching the committed tree's own native count exactly -- the variant is a valid comparator, not a shortcut that happened to compile.
- Discarded the probe: `git checkout -- .` (porcelain empty), `git worktree remove --force` + `git worktree prune`. Confirmed `git worktree list` in `/workspaces/firestarter` matches its pre-probe output (only the pre-existing `firestarter_py32_ci` sibling), `git branch --list` gained nothing, `git rev-list --count HEAD` is `852` both before and after, `/tmp/157-sw-probe/firestarter` no longer exists, and `git hash-object src/proms/memory.cpp` equals the blob hash of that file at `1151dc4` -- the if-chain is byte-unchanged and the `switch` form exists in no commit anywhere (`grep -c 'switch (handle->protocol)' src/proms/memory.cpp` => `0`).
- Checked all four of `firestarter/CLAUDE.md` §Protocol Dispatch's claims against the (unchanged) source and confirmed each still true: dispatch is solely on `handle->protocol` with no secondary axis; the protocol-prefix chain covers every `KNOWN_PROTOCOLS` entry; there is no legacy-integer fallback axis; an unrecognized value (including `0`) fail-closes to `configure_not_implemented()`. `git diff --name-only 1151dc4 HEAD -- CLAUDE.md` is empty -- the document needed no edit, which is the second rejection argument's point.
- Proved the branch-inventory golden (`tests/golden/protocol_branch_inventory.json`) is **verified GREEN**, not re-derived: `git hash-object src/proms/eprom.cpp` (`9124a46d...`) matches `meta.blob_shas['src/proms/eprom.cpp']` exactly, and `python3 -m pytest tests/test_protocol_branch_inventory.py` (run from `/workspaces/firestarter`, its actual location -- see Deviations) passes 7/7. This phase touches neither `src/proms/eprom.cpp` nor `src/proms/memory.cpp`, so the gate that was Phase 156's main red is simply not this phase's business -- explicitly distinguished from Phase 156's "re-derived inside the same commit" outcome, which this plan does not perform.
- Confirmed the two neighbouring host scanning gates are unaffected for their own stated reasons: `test_dispatch_mirror.py` (from `/workspaces/firestarter_app`) scans `firestarter/doc/PROTOCOLS.md` and `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp`, never `memory.cpp`; `test_parse_gate_admission.py` scans `src/firestarter.cpp`, which this phase does not touch. Both pass: `9 passed` combined.

## The fresh three-target measurement

Verbatim commands, run in the probe worktree at `/tmp/157-sw-probe/firestarter` (detached at `785e644`):

```bash
pio run -e uno -e uno328pb -e leonardo
```

| Target | `switch` (probe) | if-chain (committed, plan 05's figure) | Delta | RAM (both) |
|---|---|---|---|---|
| `uno` | **23108** | 23090 | **+18 B** | 1562 (unchanged) |
| `uno328pb` | **23156** | 23138 | **+18 B** | 1568 (unchanged) |
| `leonardo` | **25252** | 25234 | **+18 B** | 2003 (unchanged) |

Behavioural-equivalence check, same probe tree: `pio test -e native` => **184 test cases: 184 succeeded** (identical to the committed tree's own count -- the variant changes no observable behaviour). A cold rebuild (`pio run -t clean` then `pio run`) reproduced the exact same three flash/RAM pairs with **zero `warning:` lines**, so the figures are not a stale-cache artifact.

**What the measurement supports and no further:** the `switch` alternative is uniformly worse by +18 B on all three AVR targets measured, at this exact tree position, on avr-gcc 7.3.0 at `-Os` (C-22). It does not support a general claim about `switch` versus if-chain dispatch in the abstract, and a different compiler version or optimisation level could plausibly decide differently -- this is a single-configuration measurement, stated as such.

## The stale survey pair, with provenance -- recorded beside, never in place of, the fresh pair

The DECODE-07 criterion (`.planning/REQUIREMENTS.md` §DECODE-07) and the ROADMAP cite `uno` **25696** (switch) vs **25678** (if-chain), a **+18 B** claim, sourced from `.planning/notes/firmware-size-reduction-survey.md`. Those absolutes predate Phases 155 and 156 and the flash-ceiling quick task: `157-before-figures.md` records current `uno` at **24234** before Phase 157 even begins, and this plan's own committed-tree if-chain figure is **23090** -- the survey's absolutes are stale by roughly **1.4 to 2.6 KB** (C-10) and are **SUPERSEDED as absolutes**. They are recorded here, named with their provenance, precisely so a later reader sees both pairs and cannot mistake either for the current measurement:

| | Survey (stale, `.planning/notes/firmware-size-reduction-survey.md`) | This plan (fresh, at `785e644`) |
|---|---|---|
| `uno` switch | 25696 | 23108 |
| `uno` if-chain | 25678 | 23090 |
| delta | +18 B | +18 B |

**The magnitude coincides; the absolutes do not.** The survey's pair was measured on a `switch (handle->protocol)` where `protocol` was still `uint32_t` (pre-narrowing) at a tree position roughly 2.5 KB heavier overall. This plan's pair is measured on the now-`uint8_t` `protocol` (plan 03's narrowing) at Phase 157's near-final position. Two measurements landing on the identical delta despite a materially different switched-expression width and a different absolute baseline is reported as a coincidence of magnitude, not as validating the survey's stale absolutes, and not as proof that narrowing the switched expression left gcc's decision unaffected in general (C-22 again: one compiler, one optimisation level, one dispatched value set, at one tree position each time).

## The dispatched value set, from source

Enumerated from `src/proms/memory.cpp:99-142` and `include/proto_constants.h`:

| Group | Values | Handler |
|---|---|---|
| 1 | `PROTO_FLASH_INTEL` (0x10) | `configure_flash_intel` |
| 2 | `PROTO_EEPROM_PARALLEL` (0x0D) | `configure_eeprom28c` |
| 3 | `PROTO_FLASH_NOR_UNLOCK` (0x06) | `configure_flash_nor_unlock` |
| 4 | `PROTO_FLASH_5V_PAGE` (0x05), `PROTO_PHANTOM_0x35` (0x35), `PROTO_PHANTOM_0x39` (0x39) | `configure_flash_5v_page` |
| 5 | `PROTO_EPROM_28PIN` (0x07), `PROTO_EPROM_32PIN` (0x08), `PROTO_EPROM_24PIN` (0x0B) | `configure_eprom` |
| 6 | `PROTO_SRAM_32PIN` (0x0E), `PROTO_SRAM_24PIN` (0x27), `PROTO_SRAM_28PIN` (0x28), `PROTO_SRAM_32PIN_NVRAM` (0x29) | `configure_sram` |
| 7 | `0x11, 0x2A, 0x2B, 0x2C` (named infeasibility arms, no approved `PROTO_*` token) | `configure_not_implemented` |
| default | everything else, including `0` | `configure_not_implemented` |

**17 distinct values, range `0x05`-`0x39` (span 53), density ≈ 32%.** This is the property gcc's jump-table-versus-comparison-chain decision turns on -- and it is exactly why a pre-narrowing figure (measured when the switched expression was 32 bits wide) cannot answer this plan's question at 8 bits wide. The measurement in this plan is taken on the actual 8-bit switched expression.

## DECODE-07 discharge material -- for plan 07's `157-after-figures.md`

1. **Fresh three-target measurement:** `switch` +18 B flash on `uno` (23108 vs 23090), `uno328pb` (23156 vs 23138), `leonardo` (25252 vs 25234); 0 B RAM delta on all three; behavioural equivalence confirmed by `pio test -e native` (184/184). Commands: `pio run -e uno -e uno328pb -e leonardo` in a detached probe worktree at `785e644`.
2. **Survey's original pair, superseded:** `uno` 25696 (switch) / 25678 (if-chain), sourced from `.planning/notes/firmware-size-reduction-survey.md`, stale by 1.4-2.6 KB against `157-before-figures.md`'s `24234` and this plan's `23090`.
3. **Dispatched value set:** 17 distinct protocol values, range `0x05`-`0x39`, density ≈32% (table above).
4. **Rejection argument 1 (measured):** the `switch` form costs +18 B on every AVR target measured, at this position, with no compensating benefit.
5. **Rejection argument 2 (documentation contract):** `firestarter/CLAUDE.md` §Protocol Dispatch pins `configure_memory`'s if-chain dispatch order as a source-of-truth contract, verified still true against the (unchanged) source; converting to a `switch` would require rewriting that section too. `firestarter/CLAUDE.md` is proven byte-unchanged since `1151dc4` (`git diff --name-only` empty).
6. **C-22 ceiling:** single-configuration measurement -- one compiler (avr-gcc 7.3.0), one optimisation level (`-Os`), one dispatched value set, at one tree position (`785e644`). Not a general claim about `switch` versus if-chain.
7. **Discharge statement:** DECODE-07 is discharged by this record, not by any code change. `src/proms/memory.cpp` is byte-identical to its blob at `1151dc4` (both before and after this plan); the `switch` form exists in no commit anywhere.

## Golden and gate verification (Task 2)

- `tests/golden/protocol_branch_inventory.json`: `git hash-object src/proms/eprom.cpp` (`9124a46d45de764b8579b54f524b868b6b7ae0ef`) matches `meta.blob_shas['src/proms/eprom.cpp']` exactly. `python3 -m pytest tests/test_protocol_branch_inventory.py` (run from `/workspaces/firestarter`) => **7 passed**. **This is a "verified green" outcome, not Phase 156's "re-derived inside the same commit" outcome** -- Phase 157 touches neither `src/proms/eprom.cpp` nor `src/proms/memory.cpp`, so the gate that was Phase 156's main red is simply not this phase's business. The golden file itself is untouched (`git status --porcelain tests/golden/protocol_branch_inventory.json` empty).
- `tests/test_dispatch_mirror.py` + `tests/test_parse_gate_admission.py` (from `/workspaces/firestarter_app`) => **9 passed**. `test_dispatch_mirror.py` scans `firestarter/doc/PROTOCOLS.md` and the native `test_configure_memory.cpp` firmware test file, never `memory.cpp` -- DECODE-07's if-chain is not its business. `test_parse_gate_admission.py` scans `src/firestarter.cpp`, which this phase does not touch.

## Task Commits

None. `files_modified: []` per this plan's frontmatter -- no tracked file in `firestarter` was edited by either task, and the plan's contract is a record-only SUMMARY. The single commit this plan produces is the meta-repo docs commit (SUMMARY.md + STATE.md + ROADMAP.md), captured separately below.

## Files Created/Modified

- None in `firestarter` (contract honored: `git -C firestarter status --porcelain` is empty and HEAD is unchanged at `785e644` throughout this plan).
- `.planning/phases/157-command-decode-table-handle-type-narrowing-firmware-only/157-06-SUMMARY.md` (this file), plus STATE.md / ROADMAP.md updates in the meta repo.

## Decisions Made

- **Measured, did not assume, the delta's sign.** The direction was genuinely unknown going in (a 32-bit-to-8-bit narrowing of the switched expression can plausibly flip gcc's jump-table-vs-comparison-chain choice); the measurement resolved it as +18 B worse, matching the survey's stated magnitude coincidentally, at a materially different absolute position and switched-expression width.
- **Ran the branch-inventory gate from its actual location** (`firestarter/tests/test_protocol_branch_inventory.py`, invoked with system `python3 -m pytest` directly from `/workspaces/firestarter`) rather than the plan's literally-stated `firestarter_app/tests/test_protocol_branch_inventory.py`, which does not exist -- a plan-authoring path defect (Rule 3, blocking but mechanical: the file was simply misattributed to the sibling repo). `test_dispatch_mirror.py` and `test_parse_gate_admission.py` are correctly located in `firestarter_app/tests/` as the plan states and were run from there unchanged.
- **Did not restate the survey's `25696`/`25678` as current.** Both pairs are recorded side by side with the survey's file named as provenance and explicitly marked superseded as absolutes.
- **Did not flip DECODE-07 to Complete in `REQUIREMENTS.md`.** Per the plan's own requirements ledger note, plan 07 owns that flip for all seven DECODE requirements at phase close; this SUMMARY supplies the raw evidence.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Corrected the branch-inventory gate's repo location**
- **Found during:** Task 2, Step 2 (proving the branch-inventory golden is GREEN)
- **Issue:** The plan's action text and verify block both instruct running `cd /workspaces/firestarter_app && python3 -m pytest tests/test_protocol_branch_inventory.py ...`, but no such file exists under `firestarter_app/tests/`. The file actually lives at `firestarter/tests/test_protocol_branch_inventory.py` -- the firmware repo's own top-level `tests/` directory (distinct from `test/native/...`, the PlatformIO Unity suite tree), runnable directly with system `python3 -m pytest`.
- **Fix:** Ran the gate from its actual location (`cd /workspaces/firestarter && python3 -m pytest tests/test_protocol_branch_inventory.py -q -o addopts=""`), confirmed 7 passed. `test_dispatch_mirror.py` and `test_parse_gate_admission.py`, which the plan also names under `firestarter_app/tests/`, were confirmed present there and run from the correct location unchanged.
- **Files modified:** None -- this is a verification-command correction, not a source change.
- **Verification:** `python3 -m pytest tests/test_protocol_branch_inventory.py -q -o addopts=""` (from `/workspaces/firestarter`) => `7 passed`; `python3 -m pytest tests/test_dispatch_mirror.py tests/test_parse_gate_admission.py -q -o addopts=""` (from `/workspaces/firestarter_app`) => `9 passed`.
- **Committed in:** N/A -- no source commit; recorded here per this plan's own record-only contract.

---

**Total deviations:** 1 auto-fixed (1 blocking, plan-path correction).
**Impact on plan:** Purely a verification-command correction; does not affect any measurement, the golden's byte-hash proof, or the conclusion. No scope creep.

## Issues Encountered

None beyond the plan-path deviation above. The probe worktree built cleanly on the first attempt on all three targets, both warm and after a cold clean, with identical figures both times and zero build warnings.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- `firestarter` HEAD remains `785e644` on `gsd/v1.33-source-hygiene-firmware-size-reduction`; `git -C firestarter status --porcelain` is empty; `git -C firestarter worktree list` shows only the pre-existing `firestarter_py32_ci` sibling; no `.rej`/`.orig` file exists anywhere; `git rev-list --count HEAD` is `852`, unchanged from task start.
- Plan 07 (phase closeout) can transcribe the "DECODE-07 discharge material" section above directly into `.planning/v1.33/157-after-figures.md` and flip DECODE-07 (and the phase's other six DECODE requirements) to Complete in `REQUIREMENTS.md`.
- No blockers.

---
*Phase: 157-command-decode-table-handle-type-narrowing-firmware-only*
*Completed: 2026-08-23*

## Self-Check: PASSED

- FOUND: `.planning/phases/157-command-decode-table-handle-type-narrowing-firmware-only/157-06-SUMMARY.md`
- FOUND: meta commit `e0cc5e90` (`git log --oneline --all`)
- FOUND: `firestarter` HEAD unchanged at `785e644`, `git -C firestarter status --porcelain` empty
