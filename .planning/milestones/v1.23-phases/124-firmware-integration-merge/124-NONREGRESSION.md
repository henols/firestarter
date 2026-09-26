# Phase 124 Non-Regression Sweep — D-16 recorded evidence, closing plan (124-12)

**Written:** 2026-07-31 (Plan 124-12)
**Firmware branch:** `v1.23-py32f071-integration` · **HEAD at this sweep:** `a145081b59d94530583b9ce365db03ff567d0c2c`
**Host branch:** `v1.23-py32f071-integration` · **HEAD at this sweep:** `ccbc401e16e2d2298f7376c3086164700bba0278`
**Both sub-repos forked off `beta`** — recorded fork points (`123-01-SUMMARY.md`, unchanged since):
`fork_point_firmware: 5c9160a34b665878b05403ab014b959926feb6bf`,
`fork_point_host: e7d3ee8c8a41cd20e9159ab43b5cd969603d773e`.
**Meta branch:** `gsd/v1.23-py32f071-integration` · **Meta HEAD before this plan's commits:** `02dcb89fd25c16dac43528e1a708fe858a1aac14`.

**Re-execution pledge.** Every row below was executed in **this session** (Task 1 of Plan 124-12), against
the trees exactly as they now stand — nothing is copied from any of this phase's eleven prior plans'
SUMMARY files. Where a prior SUMMARY made a claim (a gate's exit code, a figure, a PASS line), this
document re-checked it against the live tree independently and says so. No disagreement was found in this
sweep — every figure below reproduces byte-exact against the recorded figures in 124-01 through 124-11,
**with one exception**: `check_landing_range.py`'s commit-scanned count is now **38** (not the 22 recorded by
124-04), because eight further code-bearing plans (124-05 through 124-10) landed commits into the same
`<fork>..HEAD` range after 124-04's own measurement — the range checker scans forward from a fixed
historical fork point, so its scanned-count grows with every subsequent commit by design. The **violations**
figure (0) does not change, and is the load-bearing invariant.

---

## 1. The claim, as precise statements

1. **The PY32F071 port exists on the integration branch as one atomic landing.** `check_landing_range.py`
   exits 0 with 0 violations over the full `<fork>..HEAD` range, re-run in this session against the current
   HEAD (38 commits now in range, not 124-04's 22 — see the re-execution pledge above for why the count
   grows).
2. **The ARM target configures and builds.** Evidenced exclusively by CI run `30634186514`, re-queried
   read-only in this session (not transcribed from 124-11-SUMMARY.md), at head SHA
   `a145081b59d94530583b9ce365db03ff567d0c2c` — string-equal to the live firmware HEAD re-derived in this
   same session.
3. **The provisional pin map cannot energise a PROM**, and the `#error` guard is restructured to be provably
   able to fire — re-confirmed in this session by the native refusal suite (10/10) and the three-armed
   `g++ -E` fire-proof (6 passed).
4. **MERGE-05's AVR band and MERGE-06's native counts both hold** — re-measured in this session with fresh
   clean AVR builds and cold `pio test` runs on all three native envs, not read from a captured log.
5. **All nine cross-repo source-scanning gates ran — never skipped — and passed**, re-executed in this
   session from `/workspaces/firestarter_app` with the merged `/workspaces/firestarter` sibling, and the
   full host suite reports 0 skipped under `-rs`.
6. **No firmware production source outside this phase's own declared surface was touched** — proven in this
   session by the cumulative `fork_point_firmware..HEAD` range diff (§6), enumerating what moved rather than
   proving a wrong path untouched.

---

## 2. The baseline, as recorded and as re-verified

All figures below were produced by a **fresh clean rebuild in this session** (`pio run -t clean -e <env>`
then `pio run -e <env>` for the three AVR envs; `rm -rf .pio/build/<env>` then a single uninterrupted
`pio test -e <env>` for all three native envs), not read from a committed capture.

| Env | Flash used (124-10 recorded) | Flash used (observed, this session) | RAM used (recorded) | RAM used (observed) |
|-----|----------:|----------:|---------:|---------:|
| uno | 23954 | **23954** | 1573 | **1573** |
| uno328pb | 24004 | **24004** | 1579 | **1579** |
| leonardo | 26016 | **26016** | 2014 | **2014** |

| Env | Cases (recorded) | Cases (observed) | Suites (recorded) | Suites (observed) | Result |
|-----|------:|------:|------:|------:|---|
| native | 141 | **141** | 17 | **17** | 141 succeeded, all 17 PASSED |
| native_nodevtools | 141 | **141** | 17 | **17** | 141 succeeded, all 17 PASSED |
| native_pinmap_provisional | 10 | **10** | 1 | **1** | 10 succeeded, all PASSED |

**Every AVR figure reproduces byte-exact against every code-bearing plan since the landing (124-04, 05, 06,
08, 09, 10)** — five intervening code-bearing plans moved zero AVR bytes, confirmed once more in this
session.

All three fresh AVR builds: **0 warnings of any kind** (`check_build_warnings.py --log`: `macro_redefinition=0
(== 0)` for uno/uno328pb/leonardo, exit 0 each) — matching the recorded figures exactly.

Native cold warning counts, measured against this session's own fresh cold `pio test` output (never a warm
re-use): **native 1166, native_nodevtools 1166, native_pinmap_provisional 138** — all three `== watermark`,
exit 0, matching Plan 124-10's re-baselined watermarks exactly. `size_baseline_base01.json`'s blob SHA
re-confirmed **unchanged** at `b940c91655600a57ad7ef67cba723943af929daf` (MERGE-05's frozen reference point);
the live `size_baseline.json`'s blob SHA is `9cc5204bb437735d77523e62512c1d2cadfc668f` (Plan 124-10's
re-baseline, distinct from the frozen file by design).

---

## 3. The gate table — command, expected, observed

Every command below was re-executed in this session against the trees as they now stand.
**MERGE-07 gate** = the nine cross-repo source-scanning gates (presented as eleven table rows, same row IDs
as `123-NONREGRESSION.md`, because three gates contribute both a checker invocation row and a paired-pytest
row — reproduced here so the two documents are comparable side by side).

### Firmware repo (`/workspaces/firestarter`)

| # | Command | Expected | Observed |
|---|---|---|---|
| F1 | `python3 -m pytest tests/ -q` | passed, 0 skipped — supersedes 123's 48 | **72 passed**, 0 skipped, 0 failed |
| F2 | `pio test -e native` (cold) | 141/141, 17 suites, all PASSED | **141/141 succeeded**, 17 suites, all PASSED |
| F3 | `pio test -e native_nodevtools` (cold) | 141/141, 17 suites, all PASSED | **141/141 succeeded**, 17 suites, all PASSED — agrees exactly with F2 |
| F3b | `pio test -e native_pinmap_provisional` (cold, new since 123) | 10/10, 1 suite, all PASSED | **10/10 succeeded**, 1 suite, all PASSED |
| F4a | `check_size_baseline.py --avr-log uno=...` (default vs LIVE baseline) | exit 0 | **exit 0** — `PASS: uno(flash=23954/32256,ram=1573/2048)` |
| F4b | `check_size_baseline.py --avr-log uno328pb=...` | exit 0 | **exit 0** — `PASS: uno328pb(flash=24004/32384,ram=1579/2048)` |
| F4c | `check_size_baseline.py --avr-log leonardo=...` | exit 0 | **exit 0** — `PASS: leonardo(flash=26016/28672,ram=2014/2560)` |
| F4d (MERGE-05) | `check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json` (all 3 AVR logs, vs FROZEN BASE-01) | exit 0, deltas -56/+22/+28 | **exit 0** — `PASS: uno(flash=23954/32256[+22<=64],ram=1573/2048[=]), uno328pb(flash=24004/32384[+28<=64],ram=1579/2048[=]), leonardo(flash=26016/28672[-56<=0],ram=2014/2560[=])` |
| F5a | `check_build_warnings.py --log uno=...` | exit 0, macro_redefinition==0 | **exit 0** — `PASS: uno: macro_redefinition=0 (== 0)` |
| F5b | `check_build_warnings.py --log uno328pb=...` | exit 0 | **exit 0** — `PASS: uno328pb: macro_redefinition=0 (== 0)` |
| F5c | `check_build_warnings.py --log leonardo=...` | exit 0 | **exit 0** — `PASS: leonardo: macro_redefinition=0 (== 0)` |
| F6a (MERGE-06) | `check_size_baseline.py --native-log native=... --native-log native_nodevtools=...` | exit 0, cases=141/suites=17 both | **exit 0** — `PASS: native(cases=141,suites=17), native_nodevtools(cases=141,suites=17)` |
| F7a | `check_build_warnings.py --log native=... (cold)` | exit 0, total==1166 | **exit 0** — `PASS: native: total warnings=1166 (== watermark 1166)` |
| F7b | `check_build_warnings.py --log native_nodevtools=... (cold)` | exit 0 | **exit 0** — `PASS: native_nodevtools: total warnings=1166 (== watermark 1166)` |
| F7c | `check_build_warnings.py --log native_pinmap_provisional=... (cold)` | exit 0 | **exit 0** — `PASS: native_pinmap_provisional: total warnings=138 (== watermark 138)` |
| F8 (MERGE-02 textual half) | `check_cmake_manifest.py` | `PASS:`, exit 0 — inversion of 123's `UNARMED:` | **exit 0** — see §4 for verbatim line |
| F9 (MERGE-04 consumer half) | `check_orphan_provisional.py` | `PASS:`, exit 0 — inversion of 123's `UNARMED:` | **exit 0** — see §4 for verbatim line |
| F10 (MERGE-01) | `check_landing_range.py` | exit 0, 0 violations | **exit 0** — `PASS: 38 commit(s) scanned in 5c9160a34b665878b05403ab014b959926feb6bf..HEAD, 17 carrying a portability marker, 0 violations` |
| F11 (MERGE-06 per-array) | `pytest tests/test_golden_trace_identity.py -q` | passed | **6 passed**, 0 failed |
| F12 (MERGE-04 fire-proof) | `pytest tests/test_pinmap_guard_fires.py -q` | passed | **6 passed**, 0 failed |

**MERGE-01 ancestry re-check (re-run this session, not transcribed):** `git merge-base --is-ancestor
780a3fb HEAD` → exit **1** (non-ancestor — squash, not merge); `git merge-base --is-ancestor ad47c3b HEAD` →
exit **1** (D-07 exclusion holds); the four `780a3fb` identifiers (`pgm_read_ptr`, `strncpy_P`, `strncmp_P`,
`sprintf_P`) all present by content in `include/rurp_platform_compat.h` (grep-confirmed, lines 47-48/59-60/71-72/75-76).

**F13 (MERGE-03), re-read this session — both the local file AND the pushed ref, not transcribed from Plan
124-05/124-11:** `.github/workflows/py32f071.yml`'s `on:` block, read directly from the working tree, carries
`push: branches: [beta]` verbatim (no `paths:` filter on that arm). `git fetch origin
v1.23-py32f071-integration` then `git show origin/v1.23-py32f071-integration:.github/workflows/py32f071.yml`
— the **pushed remote ref**, fetched fresh in this session — shows the identical `push: branches: [beta]`
block, byte-for-byte matching the local file. Both `pull_request` (unchanged `paths:` filter) and
`workflow_dispatch` arms remain present and untouched in both copies.

**F14 (MERGE-08's three named defects), re-verified this session against the live tree:**
1. **Flash-latency constant** — `platform/py32f071/src/main.cpp:76` reads `HAL_RCC_ClockConfig(&clocks,
   FLASH_LATENCY_1)` (confirmed via grep, not `FLASH_ACR_LATENCY_1`), with a `static_assert` at line 74
   guarding against regression. The ARM CI Build step (ARM1, `conclusion=success`) is the only mechanical
   proof the `static_assert` and the corrected constant compile — had the assertion's condition been false
   the Build step would have failed with a `static_assert` diagnostic; it did not.
2. **Orphaned `write_checksums.cmake`** — `test -f platform/py32f071/cmake/write_checksums.cmake` confirms
   **deleted**; `git grep -n write_checksums -- .` in both `firestarter` and `firestarter_app` re-run this
   session, both exit **1** (zero consumers, re-proven against the live tree, not the research record).
3. **`DEV_TOOLS`-off on ARM made an explicit commented decision** — `platform/py32f071/CMakeLists.txt:33`
   carries the `PY32_EXCLUDED: src/dev_tools.cpp -- no ARM dev-tools TU; DEV_TOOLS resolves to 0 by the
   shared default (MERGE-08, D-02)` comment; lines 104-105 carry a second explicit comment on the same
   decision beside `target_compile_definitions`; `include/firestarter.h:40-42` carries the shared
   `#ifndef DEV_TOOLS / #define DEV_TOOLS 0 / #endif` default all four targets resolve through. The ARM CI
   Build step's success is the mechanical confirmation this compiles correctly with no `DEV_TOOLS` define
   supplied.

### Host repo (`/workspaces/firestarter_app`) — the MERGE-07 nine-gate / eleven-row set

| # | Command | Expected | Observed |
|---|---|---|---|
| H1 | `python3 tools/check_no_log_in_sdp_window.py` | PASS, exit 0 | **PASS** — resolved `.../firestarter/src/proms/eeprom_28c.cpp`, emitter lines 298-314, poll lines 348-361 |
| H2 | `pytest tests/test_check_no_log_in_sdp_window.py` | passed | **7 passed** |
| H3 | `pytest tests/test_sdp_table_parity.py` | passed | **5 passed** |
| H4a | `python3 tools/check_is_memory_cmd_no_ifdef.py` | PASS, exit 0 | **PASS** — no preprocessor conditional, exactly 8 commands, predicate body lines 133-147 (shifted from 123's 109-123 by Plan 124-06's D-02 conversion; body itself unchanged) |
| H4b | `pytest tests/test_check_is_memory_cmd_no_ifdef.py` | passed | **6 passed** |
| H5 | `python3 tools/gen_sdp_bus_config.py` (idempotence) | firmware tree unchanged from its own pre-run baseline | **PASS** — `git -C firestarter status --porcelain` was **empty before and empty after** this session's run (the pre-existing dirt for `firestarter` is zero, matching 123-NONREGRESSION's own finding for this row) |
| H6 | `pytest tests/test_sdp_bus_config_drift.py` | passed | **4 passed** |
| H7 | `pytest tests/test_revision_constants_parity.py` | passed | **13 passed** — matches 123's recorded count exactly, confirming the D-02 preprocessor restructure did not regress this gate |
| H8 | `pytest tests/test_dispatch_mirror.py` | passed | **2 passed** |
| H9a | `python3 tools/check_dispatch.py` | PASS, exit 0 | **PASS** — 746 chips scanned; 736 supported; 10 confirmed non-dispatchable; 0 non_supported_dispatchable; 0 regressions; 0 consistency violations |
| H9b | `python3 tools/check_devtest_orchestrator.py` | PASS, exit 0 | **PASS** — scanned `chip_test.py`, `cli_handlers.py`, `submit.py`; 0 VPP-set, 0 raw-wire-dict, 0 `--force` |

**All eleven rows PASS — none accepted on a prior plan's claim alone; all re-run in this session.**

### Host repo — hygiene and full-suite rows

| # | Command | Expected | Observed |
|---|---|---|---|
| H10 | 7 proxy modules, `-rs` | passed, 0 skipped | **38 passed**, 0 skipped |
| H11 | `pytest tests/test_fw_presence.py tests/test_scan_paths_resolve.py tests/test_skip_census.py` | passed | **16 passed** |
| H12 | `python3 tools/check_no_exists_proxy.py` | PASS, exit 0, 78 files scanned | **PASS** — `scanned 78 file(s)...`, exit 0 |
| H13 | `python3 -m pytest tests/` | passed, 0 skipped — compared against 123's 1158 | **1158 passed**, 0 failed, 0 skipped (confirmed via `-rs`: zero `SKIPPED`/`skip` lines anywhere in the captured output; dot-count independently verified at 1158 across 17 progress-report lines) — **byte-identical to Phase 123's recorded 1158**, confirming the D-02 preprocessor restructure (124-06) and every other host-visible change this phase made left the host suite's collected-test count unchanged |
| H14 | `ruff check firestarter/ tests/` | clean | **All checks passed!** |
| H15 | `ruff format --check firestarter/ tests/` | clean | **104 files already formatted** |
| H16 | `python tools/check_mypy_watermark.py` | below watermark | **1 error (watermark 35)** — 34 below, unchanged from Phase 123 |

### ARM row (re-queried read-only in this session, per D-16's re-execution pledge)

| # | Command | Expected | Observed |
|---|---|---|---|
| ARM1 | `gh run view 30634186514 --repo henols/firestarter --json databaseId,headSha,headBranch,event,status,conclusion,jobs` | conclusion=success, headSha matches live firmware HEAD | **Re-queried this session**: `databaseId=30634186514`, `headSha=a145081b59d94530583b9ce365db03ff567d0c2c`, `headBranch=v1.23-py32f071-integration`, `event=workflow_dispatch`, `status=completed`, `conclusion=success`. Job `build` (id `91167522497`): step 5 `Configure` conclusion=**success**; step 6 `Build` conclusion=**success**; step 7 `Upload failed build diagnostics` conclusion=**skipped** (corroborating — only runs on failure); step 8 `Report size` conclusion=**success**. |
| ARM2 | head SHA vs live firmware HEAD | string-equal | `git -C /workspaces/firestarter rev-parse HEAD` = `a145081b59d94530583b9ce365db03ff567d0c2c` — **string-equal** to `ARM1`'s re-queried `headSha`, re-derived independently in this session (not assumed from Plan 124-11's own comparison). |

### Meta repo

| # | Command | Expected | Observed |
|---|---|---|---|
| M1 | `python3 -m pytest test_check_permitted_claims.py` (in `123-.../`) | passed | **10 passed** |
| M2 | `python3 check_permitted_claims.py` (no args) | exit 0, `UNARMED:` | **exit 0** — `UNARMED: none of the 4 named v1.23 closing artifacts for Phase 130 exist yet ...` (Phase 130 has not started; expected) |
| M3 (courtesy) | claim-scan over this file | exit 0 | run after this file was written — see §7 |

---

## 4. What armed, and what it fired on (inverted from 123's "what is UNARMED")

Phase 123 recorded two gates as coarse-key-armed but `UNARMED:` on the pre-landing tree. Phase 124 landed
the trigger (`platform/py32f071/`) — both gates are now **armed and green**, and this section records what
they fired on before Phase 124's own plans closed each violation.

```
check_cmake_manifest.py, first armed run (124-04, before 124-05's fix): FAIL: 9 violation(s)
  -- the flash_type_3.cpp/flash_type_4.cpp rename-damage pair (v1.19 Phase 104 renamed the real files;
     the py32 branch's manifest still named the old ones), plus 7 present-but-uncovered source paths.
  Closed by: Plan 124-05 (rename fix + D-15's five-line PY32_EXCLUDED allow-list).
  Re-confirmed this session: PASS, 23 enforced source(s) resolved, 14 PY32_SDK_SOURCES exempt, 5
  allow-listed omissions named.

check_orphan_provisional.py, first armed run (124-04, before 124-08's fix): FAIL: 1 violation(s)
  -- RURP_PY32F071_PINMAP_PROVISIONAL: zero consumers outside its own definition.
  Closed by: Plan 124-08 (the platform-neutral RURP_PINMAP_PROVISIONAL flag + bridging block, giving both
  macros real consumers).
  Re-confirmed this session: PASS: RURP_PINMAP_PROVISIONAL (3 consumer(s)), RURP_PY32F071_PINMAP_PROVISIONAL
  (1 consumer(s)).

Two Phase-123 pytests EXPIRED at this landing (both asserted startswith("UNARMED:")):
  tests/test_check_cmake_manifest.py::test_unarmed_on_the_real_tree_with_no_seam_override
    -- inverted by Plan 124-05 to test_armed_and_passing_on_the_real_tree.
  tests/test_check_orphan_provisional.py::test_unarmed_on_the_real_tree_with_no_seam_override
    -- inverted by Plan 124-08 to test_armed_and_passing_on_the_real_tree.
  Both re-confirmed passing in this session's F1 run (72 passed, 0 failed).

The native build-warning watermark also fired, unpredicted by 123-NONREGRESSION: the pre-landing tree's
recorded 360 was a WARM-cache figure (BASE-01's own measurement procedure never cleaned the build directory
between environments); the identical pre-landing tree measures 456 cold. The landed tree's cold count is
1166 (both pinned envs) -- Plan 124-10 corrected the record in place (meta.warm_vs_cold_correction) rather
than silently replacing it, and re-baselined the watermark to each env's COLD figure so a warm local re-run
stays green (INFO, not FAIL) while a cold CI run is the one that must match exactly.
```

---

## 5. Known and explained conditions — never silent

1. **Neither firmware AVR workflow fires on `v1.23-py32f071-integration`.** `build.yml` triggers on
   `push: branches: [main]` only; `beta-build.yml` on `beta` only. `py32f071.yml` now ALSO fires on
   `push: branches: [beta]` (MERGE-03, Plan 124-05) — but the working branch is neither `main` nor `beta`,
   so every *local* firmware result in §3 remains a local run. The ARM row is the one exception: it is CI
   evidence, obtained via an explicit one-time `workflow_dispatch` behind an operator gate (Plan 124-11,
   D-08/D-09), not via any branch-push trigger.
2. **Host `ci.yml` performs a single checkout with no firmware sibling** — unchanged from Phase 123; D-05's
   local-evidence choice for the host-repo cross-repo gates still stands, unrevisited by this phase.
3. **`check_landing_range.py`'s scanned-commit count grows with every subsequent plan's commits, by design.**
   124-01 measured 14 pre-landing / 16 post-01; 124-04 measured 21 pre-landing / 22 post-landing; this
   session measures 38. The **violations** figure (0, always) is the invariant MERGE-01 requires; the
   **scanned** figure is a moving measurement of "how far the range has grown since the fixed fork point",
   not a target to hold constant.
4. **The native `native_pinmap_provisional` env's cold/warm ratio is qualitatively different from the two
   pinned envs' (Plan 124-10's finding, re-confirmed this session)**: `native`/`native_nodevtools` cold 1166
   → warm 998 (partial drop); `native_pinmap_provisional` cold 138 → warm 0 (complete drop, because it
   compiles only 1 suite and its warm re-run's Unity-runner regeneration happens not to touch any
   redefinition-prone shim). Recorded honestly, not normalized to match the other two envs.
5. **The predicate `is_memory_cmd`'s reported line range has moved twice since Phase 123** (109-123 →
   113-127 predicted by RESEARCH → 133-147 actual, per Plan 124-06's own documented finding) because
   Plan 124-06's D-02 conversion inserted 24 lines of comment+code above it in the same file. The predicate's
   own content (8 named commands, zero conditionals, `static inline`) is unchanged; only its position moved.
6. **Named pre-existing working-tree dirt, unchanged by this entire phase.** `firestarter_app`:
   `M .gitignore`; untracked `.coverage`, `.planning/config.json`, `SECURITY.md`, `write_test_port.sh` —
   matches the dirt named in this plan's own dispatch prompt exactly, re-confirmed via `git status
   --porcelain` at the end of this session's sweep. `firestarter`: clean (`git status --porcelain` empty),
   re-confirmed at the end of this session after 15 separate build/test invocations wrote only into the
   gitignored `.pio/build/` tree.
7. **The three pre-existing non-conforming host checkers** (`check_dispatch.py`,
   `check_sdp_capability_invariants.py`, `check_mypy_watermark.py`) remain deliberately out of BASE-08's
   meta-test scope (`firestarter/scripts/` only) — unchanged from Phase 123, not revisited by this phase.

---

## 6. The phase-wide range proof — what moved, and what did not

Phase 123's §6 proved nothing moved. Phase 124 moved firmware code **by design** (the entire point of the
phase is landing a new port) — this section's job is the opposite: **enumerate what moved, and show that
everything outside that enumerated set did not.**

```
$ FORK=5c9160a34b665878b05403ab014b959926feb6bf   # read from 123-01-SUMMARY.md, asserted non-empty
$ test -n "$FORK"; echo $?
0
$ git -C /workspaces/firestarter merge-base --is-ancestor "$FORK" HEAD; echo $?
0
$ git -C /workspaces/firestarter rev-list --count "$FORK"..HEAD
38
```

`$FORK` is read from `123-01-SUMMARY.md`'s `fork_point_firmware` field, asserted non-empty, and asserted an
ancestor of HEAD **before** any diff runs — the same discipline `123-NONREGRESSION.md` §6 established.

**What moved** (`git diff --stat "$FORK"..HEAD`, this session): 92 files changed, 9720 insertions(+), 95
deletions(-). The paths, by category:
- `platform/py32f071/` (15 files, the landed port stack) + its CMakeLists.txt edits (rename fix, D-15
  allow-list, `DEV_TOOLS`/`RURP_PY32F071_PINMAP_CONFIGURED` compile definitions).
- `include/boards/py32f071_rurp_shield.h`, `include/boards/py32f071_pinmap_guard.h` (new), `include/rurp_platform.h`,
  `include/rurp_platform_compat.h`, `include/avr/pgmspace.h` — the landed portability layer plus Plan 124-09's
  hoisted guard fragment.
- `include/rurp_serial_utils.h`, `include/rurp_shield.h` — the landing's 2-file modified half (unchanged
  since 124-04).
- `include/firestarter.h`, `include/dev_tools.h`, `src/dev_tools.cpp`, `src/firestarter.cpp` — Plan 124-06's
  D-02 `DEV_TOOLS` value-semantics conversion.
- `include/rurp_pinmap_guard.h` (new), `src/proms/memory.cpp` — Plan 124-08's MERGE-04 refusal.
- `.github/workflows/py32f071.yml` — landed + MERGE-03's `push:` trigger (124-05).
- `scripts/`, `tests/`, `test/native/avr/test_pinmap_provisional/`, `test/native/avr/_shared/`,
  `platformio.ini` — this phase's own checkers, pytests, fixtures, and the third native env.

**What did NOT move** (asserted, not path-scoped-`git diff`-assumed):
```
$ git -C /workspaces/firestarter diff --stat "$FORK"..HEAD -- \
    src/boards/uno_rurp_shield.cpp src/boards/leonardo_rurp_shield.cpp src/boards/rurp_common.cpp \
    src/json_parser.c src/proms/ | grep -v memory.cpp
(empty -- only src/proms/memory.cpp appears in the src/proms/ scope, and it is grep-excluded above)
```
The AVR-specific board implementations, the shared JSON parser, and every `src/proms/*.cpp` file except the
one this phase's own MERGE-04 plan (124-08) deliberately edited are untouched across the full 38-commit
range — confirmed by a real diff over an asserted-ancestor range, never a vacuous path-scoped diff standing
in for "untouched."

**Anti-regression guard on the claim mechanism itself** (per the precedent in `123-NONREGRESSION.md` §6):
```
$ grep -rlE -e 'diff --stat +--[^a-zA-Z-]' -e 'diff --stat +--$' \
    /workspaces/.planning/phases/124-firmware-integration-merge/ --include='*-PLAN.md' | wc -l
0
```
Observed integer: **0**. The vacuous ref-less `--stat` shape does not occur anywhere across this phase's own
`*-PLAN.md` set.

**MERGE-01's ancestry proof, re-run this session (not transcribed from 124-04):**
```
$ git -C /workspaces/firestarter merge-base --is-ancestor 780a3fb HEAD; echo $?
1
$ git -C /workspaces/firestarter merge-base --is-ancestor ad47c3b HEAD; echo $?
1
```
Both non-ancestors — the squash landing (D-05) holds, and D-07's exclusion of
`feature/py32f071-release-assets` still holds, re-confirmed independently in this session.

---

## 7. The validation ceiling

Quoted verbatim from `.planning/REQUIREMENTS.md`:

> **No PY32F071 PCB exists.** Nothing in this milestone has ever run on this silicon, and nothing in it can.
>
> **Permitted claims:** the target builds clean; the native and host suites pass at their recorded case
> *and* suite counts; the DFU sequence is exercised against device descriptors and mocks; host-side timing
> and sizes are measured where a tool exists to measure them.

**Forbidden claim — cited by location, not reproduced verbatim (`.planning/REQUIREMENTS.md:14`):** the
eight-phrase forbidden list names an unqualified firmware-operates-on-silicon claim, an unqualified
end-to-end-install claim, three unqualified validation-adjective claims, a closed-loop-VPP claim, and a
pin-map-correctness claim. This document does not reproduce that list's exact wording, for the identical
reason `123-NONREGRESSION.md` §7 gives: the claim scanner matches a phrase's shape regardless of quotation
or negation context, by design, so reproducing the list would itself trip the scanner run against this file
in §M3/§9 below.

**Line-by-line confirmation that nothing in this document asserts a forbidden claim.** Every result above
has a software artifact as its subject — a git blob/ref identity, a `pio run`/`pio test` size or count
report, a pytest exit code, a checker's own PASS/FAIL line, a CI run's reported `conclusion` and per-step
outcome read from its own log text, a source-read confirmation — never a silicon observation. No PY32F071
hardware exists to observe. The ARM row (§3, §M) states only that the target **configures and builds**,
cited by run URL and head SHA, per MERGE-02's own permitted wording — nothing about the firmware running,
an install working, or the pin map being correct is claimed anywhere in this document.

**A green claim-scan is the mechanizable half only.** Running `check_permitted_claims.py` against this file
(§9 below) proves no *named forbidden phrase* co-occurs with a `py32`-shaped token within its proximity
window — it cannot and does not certify that every sentence here is honest by some broader human judgment.
The mechanizable half is the phrase-and-proximity check; the human-judgment half is this plan's own
authorship reading the document end to end before committing it.

---

## 8. The two Phase-123 claims this phase deliberately violates — reasoned exceptions, not silent drops

`123-NONREGRESSION.md` §8 made two blanket claims. Phase 124 is, **by its own requirements**, the phase that
breaks both of them. Rather than silently reusing Phase 123's shape and inheriting a claim this phase cannot
support, both are restated below as **explicit, reasoned exceptions** — what changed, why the requirement
licensed it, and what preserves the prior record intact.

### Exception 1 — a baseline and two watermarks WERE adjusted

Phase 123's §8 stated: *"No baseline, watermark, floor, or allow-list was adjusted to make a row green.
Every row in §3 passed as originally specified against the tree as found; no row required lowering a bar."*
**This is false of Phase 124, by design, and is not carried forward unqualified.**

- **`scripts/baseline/size_baseline_base01.json`** (Plan 124-02) is the **frozen** BASE-01 baseline —
  byte-identical to Phase 123's recorded truth, blob SHA `b940c91655600a57ad7ef67cba723943af929daf`,
  re-confirmed unchanged in this session (§2). MERGE-05's `--policy merge05` band assertion runs
  **exclusively against this frozen file** — so **no bar was lowered to make MERGE-05 green**. The
  ±64 B / must-not-grow band was always the requirement's own wording (`REQUIREMENTS.md` MERGE-05: *"Leonardo
  flash does not grow; Uno-class flash growth is ≤ 64 B and recorded"*); the previous gate
  (`check_size_baseline.py`'s pre-124 default mode) simply did not implement a band at all — it was strict
  equality only, which is why W-1 (Plan 124-02) had to add the band comparator as new code, not adjust an
  existing threshold. This distinction — implementing an unimplemented requirement clause versus loosening
  an existing bar — is the reasoning that licenses this exception.
- **`scripts/baseline/size_baseline.json`** (the LIVE, non-frozen baseline) **was re-baselined** by Plan
  124-10 to the post-landing tree's own measured figures (uno 23954/1573, uno328pb 24004/1579, leonardo
  26016/2014) — a deliberate re-baseline, not an accident, because the requirement is that flash/RAM be
  **recorded** against the new tree (MERGE-05's third clause), and BASE-01's pre-landing figures are no
  longer what the post-landing tree should be judged against in *default* mode. The frozen file (above)
  remains the fixed reference point default mode is compared against being wrong for; the live file is the
  one legitimately allowed to move.
- **The native warning watermark was RAISED**, from BASE-01's recorded 360 to the landed tree's cold-measured
  1166 (both pinned envs) — with the **warm-versus-cold correction to the prior record** written into the
  JSON itself (`meta.warm_vs_cold_correction`, Plan 124-10): BASE-01's own 360 was a warm-cache artifact of
  its own measurement procedure never having cleaned the build directory between runs; the *identical*
  pre-landing tree, measured cold in this phase, is **456** — not 360. So even Phase 123's own recorded
  figure was, itself, a warm measurement mislabeled as a clean-build figure. Phase 124's watermark move is
  therefore two things at once: a genuine increase attributable to the real landed code (456 → 1166 cold),
  and a correction of a measurement-methodology error inherited from Phase 123, both stated with their exact
  numbers rather than blended into one delta.

**Numbers, for the record:** BASE-01 recorded 360 (warm, mislabeled clean) → same pre-landing tree measured
456 cold (Plan 124-04's correction) → landed tree measured 1166 cold, both pinned envs (Plan 124-04/124-10) →
watermark set to 1166 (Plan 124-10, re-confirmed 1166 in this session, §2/§3). FLOOR (BASE-08's checker-count
meta-test) was raised 4→5 (Plan 124-01, the fifth checker, `check_landing_range.py`) and FIXTURE_FLOOR 9→10
in the same commit. A `PY32_EXCLUDED` allow-list (five lines, D-15) was added to `check_cmake_manifest.py`'s
own enforcement scope by Plan 124-05 — this is the mechanism the checker's own docstring always prescribed
for deliberate omissions, not a new leniency invented to pass a red gate; the checker was written by Phase
123 with this exact allow-list shape already specified, unused, because nothing was yet excluded.

### Exception 2 — a push and `gh` invocations DID occur

Phase 123's §8 stated: *"No push, no `gh` invocation, no release, no tag, no gitlink bump."* **This is false
of Phase 124.**

- **Plan 124-11** pushed the firmware **milestone branch** `v1.23-py32f071-integration` to `origin` — **not**
  `beta`, **not** `main`. No tag, no release, no gitlink bump, and no public comment was made by that push or
  by any command in this phase.
- The push's safety argument was **re-proven, not merely asserted**, by reading all three firmware workflow
  `on:` blocks directly from the tree before the push: `build.yml` fires only on `push: branches: [main]`;
  `beta-build.yml` only on `push: branches: [beta]`; `py32f071.yml` fires on `pull_request`,
  `workflow_dispatch`, and (as of Plan 124-05's MERGE-03 addition) `push: branches: [beta]` — none of the
  three names `v1.23-py32f071-integration`, so pushing that branch triggers **zero** CI on its own; the ARM
  build evidence was obtained only via an explicit, separately-authorized `workflow_dispatch` (D-08).
- That `workflow_dispatch` **sat behind a structural operator gate the chain could not wave through** (D-09):
  Plan 124-11's own task list contained no task capable of executing the push or the dispatch — Task 2 was
  the operator's own action, outside the executing agent's task set entirely, and the agent's Task 3
  independently re-derived every claimed fact via read-only `gh run view`/`git fetch` rather than trusting a
  relayed transcription of what the operator had done (124-11-SUMMARY.md's own recorded decision).
- `gh` **read-only** invocations occurred repeatedly across Plans 124-11 and this closing plan (124-12) to
  query the resulting CI run — `gh run view ...`, never `gh workflow run` (write) and never `gh release`/`gh
  pr` of any kind, in either plan.

**What still holds, re-asserted honestly, unchanged from Phase 123:**
- **No cross-repo CI leg was added.** Host `ci.yml` still performs a single checkout with no firmware
  sibling — D-05's local-evidence choice for the *host-repo* cross-repo gates is unrevisited by this phase.
- **No release was cut, and `beta` was not pushed.** The only push target was the firmware milestone branch;
  `origin/beta` was read (`git fetch origin beta` equivalent checks in Plan 124-04/124-11) but never written
  to.
- **Phase 130 still owns every remaining outward-facing action** — the tag, the release, the gitlink bump,
  and any public comment, per the milestone's own phase boundary (`124-CONTEXT.md` "Explicitly NOT in this
  phase").

---

## 9. Meta claim-scan over this document

```
$ cd /workspaces && python3 .planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py \
    .planning/phases/124-firmware-integration-merge/124-NONREGRESSION.md
```
**Exit code:** 0
**Output (verbatim):** `PASS: scanned ../124-firmware-integration-merge/124-NONREGRESSION.md; 1 file(s)
carry the required silicon caveat (this PASS is the mechanizable half of the honesty criterion only -- see
the module docstring's explicit non-claim)` — this is the scan run explicitly against this finished file, in
addition to the default-target run recorded at M2 in §3, which does not include this file among its four
default Phase-130 targets.

---

## 10. MERGE-01..MERGE-08 Requirement Tick Citations (per-clause)

Every requirement below is ticked only against a row this session re-executed (§3/§4/§6 above); no
requirement is ticked on the strength of a plan having merely run. Multi-clause requirements are justified
clause by clause.

- **MERGE-01** (3 clauses) — **TICKED.**
  1. Atomic landing: the squashed commit `e2c422d` (Plan 124-04), tree-proven equal to a true merge's tree.
  2. Includes `780a3fb`: its four contributed identifiers present by content in
     `include/rurp_platform_compat.h` (re-grepped §6); `780a3fb` itself confirmed a non-ancestor of HEAD this
     session (exit 1, §6) — content-inclusion via squash, not a citable ancestor commit, exactly as D-05
     records.
  3. No commit with the portability half present sans the py32 stack: **F10** — `check_landing_range.py`,
     re-run this session, `PASS: 38 commit(s) scanned ... 0 violations`, exit 0.
  Previously ticked by Plan 124-01 before the real landing existed (premature per the recorded incident
  class) — re-justified here from F10/§6, genuinely true now.

- **MERGE-02** (2 clauses, +1 ROADMAP clause) — **TICKED.**
  1. Manifest names the renamed files: **F8** — `check_cmake_manifest.py` PASS, exit 0, naming both
     `flash_nor_unlock.cpp`/`flash_5v_page.cpp` as resolved sources (§4 verbatim PASS line).
  2. ARM target reaches a successful CMake configure: **ARM1** — CI run `30634186514`, step 5 `Configure`
     `conclusion=success`, re-queried read-only this session.
  3. (ROADMAP) Successful build, cited by run URL + SHA: **ARM1** step 6 `Build` `conclusion=success`;
     **ARM2** — head SHA `a145081b59d94530583b9ce365db03ff567d0c2c` string-equal to the live firmware HEAD,
     re-derived independently this session.

- **MERGE-03** — **TICKED.** **F13** — `py32f071.yml`'s `on:` block read directly this session, both from
  the local working tree AND from the fetched `origin/v1.23-py32f071-integration` ref, shows
  `push: branches: [beta]` present in both, byte-identical.

- **MERGE-04** (2 clauses) — **TICKED.**
  1. Refusal of every PROM-energising operation: **F3b** — `pio test -e native_pinmap_provisional` (cold),
     10/10 succeeded (8 per-command refusal cases + 2 negative controls), re-run this session.
  2. Guard restructured, `#error` provably able to fire: **F12** — `pytest tests/test_pinmap_guard_fires.py`,
     6 passed (three discriminating arms: unset/`=1`/`=0`), re-run this session. **F9** — `PASS:` from
     `check_orphan_provisional.py` confirms both provisional macros have real consumers (the refusal is
     wired, not decorative).

- **MERGE-05** (3 clauses) — **TICKED.**
  1. Leonardo flash does not grow: **F4d** — `-56<=0` satisfied.
  2. Uno-class flash growth ≤ 64 B, recorded: **F4d** — uno `+22<=64`, uno328pb `+28<=64`.
  3. Flash and RAM recorded for all three AVR targets against BASE-01: **F4d**'s full PASS line names all
     six figures against the **frozen** `size_baseline_base01.json` (blob SHA re-confirmed unchanged this
     session, §2).
  Previously ticked by Plan 124-02 before the real landing existed — re-justified here from F4d (this
  session's own re-run against the actual landed, post-124-10 tree), genuinely true now.

- **MERGE-06** (2 clauses) — **TICKED.**
  1. Case and suite counts on both pinned envs: **F2**/**F3** — 141/17 both, all PASSED, re-run cold this
     session; **F6a** — `check_size_baseline.py --native-log` PASS for both, exit 0.
  2. Per-array golden-trace identity: **F11** — `pytest tests/test_golden_trace_identity.py`, 6 passed, this
     session.
  Previously ticked by Plan 124-03 before the real landing existed — re-justified here from F2/F3/F6a/F11
  (all re-run against the real landed tree this session), genuinely true now.

- **MERGE-07** — **TICKED.** All eleven MERGE-07 rows (**H1**–**H9b**) PASS, re-run this session from
  `/workspaces/firestarter_app` (literal directory name) with the merged `/workspaces/firestarter` sibling.
  **H13** — full host suite, 1158 passed, 0 failed, **0 skipped** under `-rs` (zero `SKIPPED` lines found by
  direct grep of the captured output) — no gate skipped, satisfying the requirement's "shown to run — not
  skip" wording literally.

- **MERGE-08** (3 named defects) — **TICKED.** **F14**, re-verified this session against the live tree:
  1. Flash-latency constant corrected (`FLASH_LATENCY_1`, not the ACR mask), with the `static_assert` guard
     compiling cleanly per ARM1's `Build=success`.
  2. `write_checksums.cmake` deleted, zero-consumer status re-proven via `git grep` in both repos this
     session (both exit 1).
  3. `DEV_TOOLS`-off on ARM is an explicit commented decision (`CMakeLists.txt:33,104-105`,
     `firestarter.h:40-42`), re-read this session.

**No requirement was left unticked.** All eight clauses/sub-clauses across all eight requirements are
satisfied by a row this session re-executed.

---

## Sweep Summary

| Gate | Result |
|---|---|
| Firmware pytest | **72 passed**, 0 failed, 0 skipped |
| Native `native` (cold) | **141/141**, 17 suites, all PASSED |
| Native `native_nodevtools` (cold) | **141/141**, 17 suites, all PASSED |
| Native `native_pinmap_provisional` (cold) | **10/10**, 1 suite, all PASSED |
| AVR fresh clean builds × 2 gates each | all 3 envs byte-identical to the 124-04 landing figures; default mode + `--policy merge05` both exit 0 |
| Native fresh cold test-runs × 2 gates each | all 3 envs; both `--native-log`/`--log` gates exit 0 |
| `check_cmake_manifest.py` | **PASS**, exit 0 (armed, inverted from Phase 123's `UNARMED:`) |
| `check_orphan_provisional.py` | **PASS**, exit 0 (armed, inverted from Phase 123's `UNARMED:`) |
| `check_landing_range.py` (MERGE-01) | **PASS**, 38 scanned, 0 violations |
| `test_golden_trace_identity.py` (MERGE-06 per-array) | **6 passed** |
| `test_pinmap_guard_fires.py` (MERGE-04 fire-proof) | **6 passed** |
| No-firmware-code-moves-outside-scope cumulative diff | enumerated (§6), scope-confirmed, `$FORK` ancestor-confirmed |
| Ref-less `--stat` guard over phase's own plans | **0** occurrences |
| Host 11-row MERGE-07 cross-repo gate table | all 11 PASS |
| Host 7 proxy modules | **38 passed**, 0 skipped |
| Host skip census + scan-path resolve + fw-presence | **16 passed** |
| `check_no_exists_proxy.py` | PASS, 78 files scanned |
| Host full suite | **1158 passed**, 0 failed, 0 skipped — byte-identical to Phase 123's recorded 1158 |
| Host ruff / ruff-format / mypy-watermark | all green (1 error, 34 below watermark, unchanged) |
| Meta claim-gate self-test | **10 passed** |
| Meta claim-gate default run | `UNARMED:`, exit 0 |
| Meta claim-gate run against this file | **exit 0** |
| ARM CI run `30634186514` | conclusion=success; Configure=success; Build=success; head SHA string-equal to live firmware HEAD |
| All three repos' branch state | firmware + host on `v1.23-py32f071-integration` (firmware HEAD `a145081b`); meta on `gsd/v1.23-py32f071-integration` |

**This phase's entire verification surface is green, re-executed against the tree exactly as it stands at
the end of the phase — local evidence for every gate except the ARM row (a CI run, read-only re-queried),
per D-05 (still standing) and D-16 (this document's own mandate).** This plan ticks the MERGE-01..MERGE-08
requirements it can justify in `.planning/REQUIREMENTS.md`, each citing the specific row above.
