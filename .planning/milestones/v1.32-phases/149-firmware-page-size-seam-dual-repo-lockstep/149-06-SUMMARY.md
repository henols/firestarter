---
phase: 149-firmware-page-size-seam-dual-repo-lockstep
plan: 06
subsystem: firmware-build-infra
tags: [platformio, avr, merge-05, size-gate, budget-exemption, cold-measurement]

# Dependency graph
requires:
  - phase: 149-04
    provides: "the page-size wire seam landed in firestarter (58c6a3c, 9c65f0f, 28bf089) whose cold flash/RAM cost this plan measures and funds"
  - phase: 149-05
    provides: "the cross-repo JSON-key parity gate, landed before this plan's cold capture so the measured cost reflects the phase's full firmware surface"
provides:
  - "cold post-change flash/RAM/warning measurement for uno, uno328pb, leonardo, with all four deltas per env (vs plan 01's pre-edit capture and vs BASE-01)"
  - "MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES=210 (flash) and MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES=2 (RAM), both SHA-attributed to this phase's own firmware commits, funding the measured seam cost without touching MERGE05_UNO_CLASS_FLASH_BAND (64), MERGE05_DEFECT_FIX_EXEMPTION_BYTES (96) or BASE-01"
  - "_merge05_flash_allowance as a 5-tuple (band, defect_exemption, seam_exemption, allowance, band_label) and a new _merge05_ram_allowance(env) resolver, so every PASS/FAIL message prints the full decomposition"
  - "five repaired test legs plus one new BASE-01-not-re-anchored leg (14/14 passing) and three re-planted fixtures observed to fire one byte past the new allowances"
  - "leonardo's remaining MERGE-05 flash headroom stated as a number: exactly 0 bytes after this exemption"
  - "the post-change section of 149-PAGE-SIZE.md and 149-SIZE-TRANSCRIPTS.md's RED/GREEN/re-armed-tripwire transcripts"
affects: [149-07, 149-08]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "MERGE-05 allowance decomposition as a 5-tuple, never a summed value: band + defect-fix exemption + page-size-seam exemption returned separately so every message shows which phase funded which byte"
    - "RAM exemption mirrors the flash exemption's shape: a single-reader resolver (_merge05_ram_allowance) and a named, SHA-attributed constant, the first time the RAM clause has admitted anything beyond exact equality"
    - "Comment-block literal hygiene: a constant's own identifier must not appear inside a SIBLING constant's docstring/comment prose, or the block-extraction regex used by this plan's own acceptance script (and any future one reusing the pattern) miscounts readers"

key-files:
  created:
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-SIZE-TRANSCRIPTS.md
  modified:
    - firestarter/scripts/check_size_baseline.py
    - firestarter/tests/test_check_size_baseline.py
    - firestarter/tests/fixtures/planted_size_baseline_policy_leonardo_growth.log
    - firestarter/tests/fixtures/planted_size_baseline_policy_uno_over_band.log
    - firestarter/tests/fixtures/planted_size_baseline_policy_ram_moved.log
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-PAGE-SIZE.md

key-decisions:
  - "Measured N=210 B flash and M=2 B RAM cold, uniform on all three AVR targets, before authoring either constant -- the exemption's value could not be pre-authored (D-12/D-13)"
  - "Funded the growth with two NEW, separately-named, SHA-attributed exemptions rather than folding into MERGE05_DEFECT_FIX_EXEMPTION_BYTES, re-anchoring BASE-01, or widening either band -- all three alternatives named and rejected in each constant's own comment block"
  - "RAM clause changed from exact-equality to a named, bounded tolerance (the first time in this gate's history) because Phase 149's own uint16_t page_size field moved RAM by a measured +2 B on all three targets -- funded with its own constant, never folded into the flash exemption's SCOPE: flash only boundary"
  - "Leonardo's post-exemption MERGE-05 headroom is exactly 0 bytes -- the exemption funds precisely what was measured, with zero spare margin; the next firmware phase adding even one byte to leonardo will need its own exemption or must shrink something else first"

patterns-established:
  - "A constant's SHA attribution must name commits distinct from any sibling exemption's SHAs, so a reader can tell which phase's growth funded which number without cross-referencing history"

requirements-completed: []  # PGSZ-04 spans multiple plans; per this phase's planner_decisions, plan 08 alone flips PGSZ-0N checkboxes after the whole-phase gate is green

coverage:
  - id: D1
    description: "Post-change flash and RAM measured cold for uno, uno328pb, leonardo, with all four deltas (vs pre-edit, vs BASE-01) recorded per env"
    requirement: "PGSZ-04"
    verification:
      - kind: unit
        ref: "149-postchange-cold-{uno,uno328pb,leonardo}.log -- cold rm -rf + pio run transcripts, N=210/M=2 derived and recorded"
        status: pass
    human_judgment: false
  - id: D2
    description: "The page-size-seam growth is funded by two new, separately-named, SHA-attributed MERGE-05 exemptions; the existing band/exemption constants and BASE-01 stay byte-unchanged; the tripwire is re-armed and observed to fire one byte past the new allowance"
    requirement: "PGSZ-04"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_check_size_baseline.py -- 14/14 passed (5 repaired legs + 1 new base01-not-re-anchored leg)"
        status: pass
      - kind: other
        ref: "python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json (real cold logs) -> EXIT=0; three re-planted fixtures each -> EXIT=1"
        status: pass
    human_judgment: false
  - id: D3
    description: "The operator judged the measured growth (+210 B flash / +2 B RAM for one wire key, one handle field, one reset, a mask resolver and one changed flush test) proportionate to what shipped, and authorized the exemption's justification"
    verification: []
    human_judgment: true
    rationale: "Whether the growth was necessary is a judgement no gate can make (149-VALIDATION.md); this is also the second consecutive milestone MERGE-05 has admitted growth by exemption, so a human check on the mechanism itself was required by the plan's own blocking checkpoint."

# Metrics
duration: ~35min
completed: 2026-08-19
status: complete
---

# Phase 149 Plan 06: Firmware Page-Size Seam — Cold Measurement and MERGE-05 Funding Summary

**Cold-measured the page-size seam's real flash (+210 B) and RAM (+2 B) cost on all three AVR targets, then funded it with two new named, SHA-attributed MERGE-05 exemptions — leaving leonardo's post-exemption headroom at exactly 0 bytes — after seeing the gate genuinely fail, then pass, then still fail one byte past the new floor.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-08-19
- **Tasks:** 3/3 completed (Task 3 is the operator checkpoint; approved)
- **Files modified:** 6 (5 in `firestarter`, 1 in meta — plus one new meta file, `149-SIZE-TRANSCRIPTS.md`)

## Accomplishments

- **Cold post-change measurement, all three AVR targets.** `rm -rf .pio/build/<env>` + one uninterrupted `pio run -e <env>` each, identical procedure to plan 01's pre-edit capture: uno 25130/1575, uno328pb 25180/1581, leonardo 27212/2016 (flash/RAM). Zero `warning:` lines in all three logs; `flash_total`/`ram_total` unchanged on all three (32256/2048, 32384/2048, 28672/2560).
- **The numbers plan 07 needs, exact and cold — transcribed here so it never has to re-derive anything warm:**

  | env | flash_used | flash_total | ram_used | ram_total |
  |---|---|---|---|---|
  | uno | 25130 | 32256 | 1575 | 2048 |
  | uno328pb | 25180 | 32384 | 1581 | 2048 |
  | leonardo | 27212 | 28672 | 2016 | 2560 |

  Source logs: `149-postchange-cold-{uno,uno328pb,leonardo}.log`, all `[SUCCESS]`.
- **Seam cost measured, not predicted:** `N = 210` B flash (BASE-01 delta of +306 minus the already-admitted 96 B Phase 145 exemption), `M = 2` B RAM — both uniform on all three AVR targets, matching the predicted RAM cost of the single `uint16_t page_size` field.
- **The gate SEEN to fail before any exemption existed:** `--policy merge05` against BASE-01 on the real cold logs exited 1, naming `allowance of 96 B` on leonardo and a `ram_used` delta on every env. Transcript: `149-SIZE-TRANSCRIPTS.md` §"RED".
- **Two new named, SHA-attributed exemptions added** to `firestarter/scripts/check_size_baseline.py`: `MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES = 210` (flash, attributed to commits `58c6a3c`/`28bf089`) and `MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES = 2` (RAM, attributed to `58c6a3c`) — the first time the RAM clause has admitted anything beyond exact equality. `MERGE05_UNO_CLASS_FLASH_BAND` stays exactly 64, `MERGE05_DEFECT_FIX_EXEMPTION_BYTES` stays exactly 96, `scripts/baseline/size_baseline_base01.json` is byte-unchanged (`git diff --quiet` verified).
- **`_merge05_flash_allowance` is now a 5-tuple** `(band, defect_exemption, seam_exemption, allowance, band_label)`, never a summed 4-tuple; both call sites (the FAIL arm and `main()`'s PASS-line builder) print the full three-term decomposition, e.g. `band 0 B + defect-fix exemption 96 B + page-size-seam exemption 210 B`. A new `_merge05_ram_allowance(env)` resolver is the sole reader of the RAM constant, mirroring the flash resolver's single-consumer shape.
- **The gate SEEN to pass after the exemptions landed:** the identical command against the identical cold logs exits 0, e.g. `leonardo(flash=27212/28672[+306<=306=band0+exempt96+seam210],ram=2016/2560[+2<=2=seam2])`. Transcript: `149-SIZE-TRANSCRIPTS.md` §"GREEN".
- **Five broken legs repaired, one new leg added** (14/14 passing in `test_check_size_baseline.py`): `test_policy_merge05_admits_the_documented_defect_fix` (re-derived to the new 306 B leonardo allowance, `delta=+307`), `test_policy_merge05_fires_on_uno_class_over_band` (`delta=+371`, `allowance of 370 B`), `test_policy_merge05_fires_on_leonardo_growth` (`delta=+307`), `test_policy_merge05_fires_on_ram_move` (`delta=+3`, `ram allowance of 2 B`), `test_policy_merge05_permits_the_measured_landing_deltas` (docstring updated; its own zero-delta arithmetic needed no change — zero sits inside any non-negative allowance), and the new `test_base01_is_not_re_anchored_by_the_new_exemption` (asserts BASE-01's figures and both flash band literals byte-unchanged, as a leg rather than only prose).
- **All three planted fixtures re-derived to exactly one byte past the NEW allowance and each independently observed to fire (exit 1):** `planted_size_baseline_policy_leonardo_growth.log` (Flash 26906+0+96+210+1=27213), `..._uno_over_band.log` (Flash 24824+64+96+210+1=25195), `..._ram_moved.log` (RAM 1573+2+1=1576). Confirmed both via the full test suite and via direct standalone gate invocations against each fixture.
- **A comment-hygiene self-catch during authoring:** an early draft of the RAM exemption's comment named `MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES` inside prose in four other locations (module docstring, the flash constant's own `SCOPE:` clause, and both function docstrings); the plan's own acceptance script asserts the identifier appears in exactly 2 places (its definition and its sole read site), so all four prose mentions were reworded to describe the constant without repeating its literal name before committing. Same defect shape plan 04 hit twice with `AT28C_PAGE_SIZE_FALLBACK`.
- **Post-commit whole-repo suites, run in the order the plan requires (commit, then run):** `python3 -m pytest tests/ -o addopts="" -q` (firmware repo) → **315 passed** (314 pre-existing + 1 new `test_base01_is_not_re_anchored_by_the_new_exemption` leg). `pio test -e native` and `-e native_nodevtools` → both **151/151 cases, 17 suites**, agreeing — unmoved from plan 04's landing, zero new native cases added by this plan.
- **Cold warnings, nothing lowered:** `check_build_warnings.py --rebuild`, run after removing all three native build directories by hand, reports AVR macro-redefinition 0/0/0 (the `== 0` rule) and both pinned native watermarks (`native`, `native_nodevtools`) holding at exactly **1166**, measured cold.
- **`149-PAGE-SIZE.md`'s post-change section is complete**: the cold three-env table with all four deltas, `N`/`M` stated explicitly, v1.31's MERGE-05 band breach named (leonardo's pre-existing headroom was already exactly 0 B before this phase, from Phase 145's fully-consumed 96 B exemption), leonardo's remaining post-exemption headroom stated as **exactly 0 bytes** (its physical free flash, a separate number, is 1460 B), the two new constants' SHA attribution and rejected alternatives, and the literal `software-proven and unvalidated on silicon`.
- **`149-check-claims.py` exits 0** over the completed artifact.
- **Operator checkpoint approved.** The operator reviewed the exemption's comment blocks (SHA attribution, three rejected alternatives each, `SCOPE:` clauses, negative-control test names), the post-change section of `149-PAGE-SIZE.md`, the side-by-side pre/post cold logs, and the re-armed tripwire's independent firing on all three fixtures, and judged the measured +210 B flash / +2 B RAM growth proportionate to the shipped seam (one wire key, one handle field, one reset, one mask resolver, one changed flush test). The `uint8_t` log2-exponent narrowing alternative was presented and explicitly declined in favor of the measured `uint16_t` field. Response: **"approved"**. No narrowing, no escalation requested.

## Leonardo's headroom, stated plainly for plan 07/08

**Leonardo's remaining MERGE-05 flash headroom after this exemption is exactly 0 bytes** — the post-change cold flash delta against BASE-01 (+306 B) equals the new effective allowance (0 band + 96 defect-fix + 210 seam = 306) exactly. This exemption funds the seam's measured cost with **zero spare margin**. **The next firmware phase that adds even a single byte of flash growth to leonardo will need its own new exemption (or to shrink something else first)** — this is not a one-time headroom grant, it is the same "funds exactly what was measured" shape the Phase 145 exemption already established. Leonardo's raw **physical** free flash — a separate, unrelated number, not gated by MERGE-05 — is `28672 - 27212 = 1460` bytes.

## Task Commits

Each task committed atomically, split across the two repos per `commits_land_in`:

1. **Task 1: Cold-measure flash, RAM and warnings post-change, see the MERGE-05 gate FAIL** — `7aa6e8c6` (docs, meta): three cold post-change transcripts, the RED gate transcript in `149-SIZE-TRANSCRIPTS.md`.
2. **Task 2: Add the named exemption(s), repair the five broken legs, re-plant the fixtures, re-arm the tripwire** — `581cff6` (feat, `firestarter`): the two new exemption constants, the 5-tuple resolver, the RAM resolver, five repaired legs plus one new leg, three re-planted fixtures. `f6497c0a` (docs, meta): the GREEN/tripwire transcripts and the post-change section of `149-PAGE-SIZE.md`.
3. **Task 3: Operator authorizes the MERGE-05 exemption and its justification** — checkpoint, no code change; approval recorded above. (No commit — this task is a review gate over Task 2's already-committed artifact.)

**Plan metadata:** committed after this SUMMARY (STATE.md / ROADMAP.md update, meta).

## Files Created/Modified

- `firestarter/scripts/check_size_baseline.py` — `MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES` (210), `MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES` (2), `_merge05_flash_allowance` widened to a 5-tuple, new `_merge05_ram_allowance`, `compare_avr_policy_merge05`'s RAM clause changed from exact-equality to a bounded tolerance, both PASS/FAIL message builders extended to three flash terms, module docstring worked examples re-derived
- `firestarter/tests/test_check_size_baseline.py` — five legs repaired, one new leg (`test_base01_is_not_re_anchored_by_the_new_exemption`) added, stale 96 B/160 B literals removed, derivation-history docstring prose updated
- `firestarter/tests/fixtures/planted_size_baseline_policy_leonardo_growth.log` — Flash `used` raised to 27213
- `firestarter/tests/fixtures/planted_size_baseline_policy_uno_over_band.log` — Flash `used` raised to 25195
- `firestarter/tests/fixtures/planted_size_baseline_policy_ram_moved.log` — RAM `used` raised to 1576
- `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-{uno,uno328pb,leonardo}.log` — new, cold post-change `pio run` transcripts
- `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-SIZE-TRANSCRIPTS.md` — new, RED/GREEN/re-armed-tripwire/post-commit-suite transcripts
- `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-PAGE-SIZE.md` — post-change section completed (plan 06's placeholder)

## Decisions Made

1. **Measured before authoring.** `N` and `M` were cold-measured in Task 1, before either constant existed, per the plan's binding precondition — the exemption's value could not have been pre-authored.
2. **Two exemptions, not one, not folded together.** Flash and RAM growth were funded by two SEPARATE named constants (`MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES`, `MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES`), each with its own `SCOPE:` boundary, so a flash change can never launder a RAM cost or vice versa.
3. **RAM clause weakened only exactly as much as measured.** Before this phase, `ram_used` required exact equality; it now requires "within the named exemption", which for uno/uno328pb/leonardo is uniformly 2 B — still strictly zero-tolerance for any RAM change this exemption does not cover.
4. **`uint16_t` field width retained**, per Claude's Discretion in `149-CONTEXT.md` — a narrower `uint8_t` log2-exponent form was considered and rejected (in the RAM exemption's own comment) because the RAM clause's tolerance was zero either way, so a narrower field only changes the constant's size, not whether an exemption is needed. The operator, at the checkpoint, independently confirmed this same conclusion.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] RAM exemption's own identifier leaked into sibling comment/docstring prose, breaking its own single-reader invariant**
- **Found during:** Task 2, running the plan's own acceptance script (the "exactly one reader" assertion for `MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES`)
- **Issue:** An early draft named the RAM constant's literal identifier in four places outside its own definition and read site: the module docstring, the flash exemption's own `SCOPE: flash only` clause, `_merge05_ram_allowance`'s docstring, and `compare_avr_policy_merge05`'s docstring. The acceptance check (`len(re.findall(...)) == 2`) correctly rejected this as a non-single-reader.
- **Fix:** Reworded all four locations to describe the RAM constant ("this module's own separate RAM-tolerance constant", "this module's single RAM-tolerance constant, defined immediately after the flash one") without repeating its literal name.
- **Files modified:** `firestarter/scripts/check_size_baseline.py`
- **Verification:** Re-ran the exact regex count from the plan's own acceptance script; got the expected 2 occurrences (definition + return statement).
- **Committed in:** `581cff6` (never committed in its broken state — caught pre-commit)

**2. [Rule 1 - Bug] The `software-proven and unvalidated on silicon` phrase was split across a comment-line wrap, breaking the block-extraction regex's substring match**
- **Found during:** Task 2, running the plan's own acceptance script (the required-phrase check on the flash exemption's comment block)
- **Issue:** The phrase wrapped as `...is software-proven and unvalidated on\n# silicon...`, so the literal substring `"software-proven and unvalidated on silicon"` did not appear contiguously once the `\n# ` line-wrap character sequence sat inside it.
- **Fix:** Reflowed the comment so the full phrase sits on one un-wrapped line.
- **Files modified:** `firestarter/scripts/check_size_baseline.py`
- **Verification:** Re-ran the acceptance script; the phrase assertion passed.
- **Committed in:** `581cff6` (never committed in its broken state — caught pre-commit)

**3. [Rule 1 - Bug] Second call site's tuple-unpack used a parenthesized/backslash-continued form the acceptance script's call-site regex could not match**
- **Found during:** Task 2, running the plan's own acceptance script (the "exactly 2 call sites" check)
- **Issue:** Two intermediate drafts of `main()`'s PASS-line builder wrapped the 5-name unpack across a line continuation (`= (\n    _merge05_flash_allowance(env)\n)` and then `= \` backslash-continuation) — both broke the `re.findall(r'=\s*_merge05_flash_allowance\(', s)` pattern because `\s*` does not match a literal `(` or `\` character sitting between the `=` and the function name.
- **Fix:** Rewrote the call site as a single unwrapped line, matching call site 1's shape exactly.
- **Files modified:** `firestarter/scripts/check_size_baseline.py`
- **Verification:** Re-ran the acceptance script; both call sites counted correctly, both unpacking 5 names.
- **Committed in:** `581cff6` (never committed in its broken state — caught pre-commit)

---

**Total deviations:** 3 auto-fixed (all Rule 1 — self-introduced formatting/naming collisions with this plan's own acceptance gates, each caught by re-running the plan's own verification script before the responsible commit, the same defect shape plan 04 hit with `AT28C_PAGE_SIZE_FALLBACK`).
**Impact on plan:** No scope creep. All three fixes are wording/formatting corrections to this plan's own new comments and code; none touches a measured figure, a test assertion's substance, or a `PGSZ-0N` requirement checkbox.

## Issues Encountered

None beyond the three self-caught deviations above — all cold builds, all pytest runs, and both native suites passed on first execution after each fix.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

Plan 07 (baseline update) can proceed: the cold post-change figures table above (uno 25130/32256/1575/2048, uno328pb 25180/32384/1581/2048, leonardo 27212/28672/2016/2560) is ready to transcribe directly into `scripts/baseline/size_baseline.json` without any warm-to-cold re-derivation. This plan did not touch that file. Plan 07 should also carry forward: leonardo's post-exemption MERGE-05 headroom is exactly 0 bytes (no spare margin — any future leonardo flash growth needs its own exemption), and the native case/suite counts (315 firmware pytest, 151/151 × 2 native envs, 17 suites) are unmoved from plan 04's landing since this plan added zero native cases. Plan 08 can proceed once plan 07 lands: no `PGSZ-0N` requirement checkbox or traceability row was touched by this plan — plan 08 alone flips all five.

## Self-Check: PASSED

- FOUND: `/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-uno.log`
- FOUND: `/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-uno328pb.log`
- FOUND: `/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-leonardo.log`
- FOUND: `/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-SIZE-TRANSCRIPTS.md`
- FOUND: `/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-PAGE-SIZE.md` (post-change section present, no `*(filled by plan 06)*` placeholder remaining)
- FOUND: `/workspaces/firestarter/scripts/check_size_baseline.py` (`MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES = 210`, `MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES = 2`, 5-tuple resolver, `_merge05_ram_allowance`)
- FOUND: `/workspaces/firestarter/tests/test_check_size_baseline.py` (14 test functions, including `test_base01_is_not_re_anchored_by_the_new_exemption`)
- FOUND: `/workspaces/firestarter/tests/fixtures/planted_size_baseline_policy_leonardo_growth.log` (Flash 27213)
- FOUND: `/workspaces/firestarter/tests/fixtures/planted_size_baseline_policy_uno_over_band.log` (Flash 25195)
- FOUND: `/workspaces/firestarter/tests/fixtures/planted_size_baseline_policy_ram_moved.log` (RAM 1576)
- FOUND commit: `7aa6e8c6` (meta)
- FOUND commit: `581cff6` (firestarter)
- FOUND commit: `f6497c0a` (meta)
- CONFIRMED: `python3 -m pytest tests/test_check_size_baseline.py -o addopts="" -q` in `firestarter` — 14 passed
- CONFIRMED: `python3 -m pytest tests/ -o addopts="" -q` in `firestarter` — 315 passed
- CONFIRMED: `pio test -e native` — 151/151 cases, 17 suites
- CONFIRMED: `pio test -e native_nodevtools` — 151/151 cases, 17 suites (envs agree)
- CONFIRMED: `python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json` against the real cold logs — EXIT=0
- CONFIRMED: direct gate runs against all three re-planted fixtures — EXIT=1 each
- CONFIRMED: `git -C /workspaces/firestarter diff --quiet scripts/baseline/size_baseline_base01.json` — unchanged
- CONFIRMED: `git -C /workspaces/firestarter diff --quiet scripts/baseline/size_baseline.json` — unchanged (plan 07's file)
- CONFIRMED: `git -C /workspaces/firestarter diff --quiet src include` — unchanged (this plan measures, does not edit firmware)
- CONFIRMED: `python3 /workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-check-claims.py` — EXIT=0
- CONFIRMED: no `PGSZ-0N` checkbox or traceability row touched in `REQUIREMENTS.md` or `ROADMAP.md`
- CONFIRMED: meta `M firestarter` / `M firestarter_app` gitlinks not staged by this plan

---
*Phase: 149-firmware-page-size-seam-dual-repo-lockstep*
*Completed: 2026-08-19*
