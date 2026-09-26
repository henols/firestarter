# Phase 123 Non-Regression Sweep — D-05 recorded evidence, wave 7

**Written:** 2026-07-31 (Plan 123-11)
**Firmware branch:** `v1.23-py32f071-integration` · **HEAD at this sweep:** `34bda8c9b473c3f19f7dd722d7ccadc2ae74fd77`
**Host branch:** `v1.23-py32f071-integration` · **HEAD at this sweep:** `ccbc401e16e2d2298f7376c3086164700bba0278`
**Both sub-repos forked off `beta`** — recorded fork points (123-01-SUMMARY.md, unchanged since):
`fork_point_firmware: 5c9160a34b665878b05403ab014b959926feb6bf`,
`fork_point_host: e7d3ee8c8a41cd20e9159ab43b5cd969603d773e`.
**Meta branch:** `gsd/v1.23-py32f071-integration` · **Meta HEAD before this plan's commits:** `a3f5b08e57bf1d3ca82d278c3b84a061a064cec3`.

**Re-execution pledge.** Every row below was executed in this session, against the trees as they now
stand — nothing is copied from any of the ten prior plans' SUMMARY files. Where a prior SUMMARY made a
claim (the AVR/native figures, the gate exit codes, the UNARMED lines, the fork-point SHA), this
document re-checked it against the live tree independently and says so. No disagreement was found
anywhere in this sweep — every figure below reproduces byte-exact against 123-01 through 123-10's
recorded numbers.

---

## 1. The claim, as precise statements

1. **The recorded baseline exists and is machine-readable.** `firestarter/scripts/baseline/size_baseline.json`
   (123-01) carries all six AVR flash/RAM figures and both native `{141,17}` pairs; every comparator this
   phase wrote (`check_size_baseline.py`, `check_build_warnings.py`) reads it via the
   `FIRESTARTER_SIZE_BASELINE` env seam rather than embedding numbers.
2. **The FW-absent proxy is split, and a present-repo-missing-target is a hard failure.**
   `tests/fw_presence.py` (123-07) keys presence on `../firestarter/.git`; `fw_path()` raises
   `MissingScanTargetError` — never a skip — when the sibling is present but a named path is not.
3. **The skip census fails on a firmware-absent reason while the marker exists.**
   `tests/test_skip_census.py` (123-09) asserts this and additionally fails on any skip reason absent
   from the committed `ALLOWED_SKIP_REASONS` allow-list, with no pinned total count (D-10).
4. **Four new checkers exist, three of them armed-on-arrival and correctly UNARMED today.**
   `check_size_baseline.py` and `check_build_warnings.py` are armed-on-arrival (every AVR/native env is
   always in scope); `check_cmake_manifest.py` and `check_orphan_provisional.py` are coarse-key-armed on
   `platform/py32f071/` (D-07) and both print `UNARMED:` today, re-confirmed this session (§4).
5. **Every checker introduced this milestone ships a committed planted fixture and a pytest proving the
   non-zero exit** — re-verified structurally by `firestarter/tests/test_checker_convention.py` (123-06),
   scoped to `firestarter/scripts/`, `FLOOR=4`/`FIXTURE_FLOOR=9`, both floors re-satisfied on this tree.
6. **No firmware production source, build config, workflow or native test suite was touched** — proven
   in this session by the cumulative `fork_point_firmware..HEAD` diff (§6), not by a working-tree
   comparison that would be blind to every wave already committed.

---

## 2. The BASE-01 baseline, as recorded and as re-verified

All figures below were produced by a **fresh clean rebuild in this session** (`pio run -t clean -e <env>`
then `pio run -e <env>` for the three AVR envs; `pio test -e <env>` for both native envs), not read from
a committed capture.

| Env | Flash used (recorded JSON) | Flash used (observed, this session) | RAM used (recorded) | RAM used (observed) |
|-----|----------:|----------:|---------:|---------:|
| uno | 23932 | **23932** | 1573 | **1573** |
| uno328pb | 23976 | **23976** | 1579 | **1579** |
| leonardo | 26072 | **26072** | 2014 | **2014** |

| Env | Cases (recorded) | Cases (observed) | Suites (recorded) | Suites (observed) | Result |
|-----|------:|------:|------:|------:|---|
| native | 141 | **141** | 17 | **17** | 141 succeeded, all 17 PASSED |
| native_nodevtools | 141 | **141** | 17 | **17** | 141 succeeded, all 17 PASSED |

**ROADMAP cross-check result:** five of the six AVR figures (uno flash/RAM, leonardo flash/RAM, uno328pb
flash) reproduce byte-exact against `ROADMAP.md`'s Phase 123 Success Criteria wording. **uno328pb RAM
(1579 B used)** is supplied for the first time by this milestone — no prior milestone ever recorded it —
and this session's fresh measurement confirms 123-01's first-ever recording of that figure exactly.

All three fresh AVR builds: **0 warnings of any kind**, confirmed via `grep -cE 'warning:'` on each
freshly captured build log this session — same result as 123-01's original measurement.

Both native envs' warning counts, measured against this session's own fresh `pio test` output (not the
truncated `captured_test_native_summary.log`): **360** total warnings each, all macro-redefinition
shaped (`grep -cE 'warning: *"[^"]+" +redefined'` also returns 360 on both) — matching the recorded
watermark exactly, in agreement with 123-01/123-03/123-06/123-09's prior measurements.

---

## 3. The gate table — command, expected, observed

Every command below was re-executed in this session against the trees as they now stand.
**MERGE-07 gate** = the nine cross-repo source-scanning gates (C-8's smaller population, presented as
eleven table rows because three gates contribute both a checker invocation row and a paired-pytest row).
**D-11 inventory** = the seven proxy-carrying host modules' larger, superset cross-repo scan-path
population (`tests/scan_paths.py`), which additionally covers `test_gen_validation_header.py` — a module
absent from the MERGE-07 eleven-row table.

### Firmware repo (`/workspaces/firestarter`)

| # | Command | Expected | Observed |
|---|---|---|---|
| F1 | `python3 -m pytest tests/ -q` | 48 passed, 0 skipped | **48 passed**, 0 skipped |
| F2 | `pio test -e native` | 141/141, 17 suites, all PASSED | **141/141 succeeded**, 17 suites, all PASSED |
| F3 | `pio test -e native_nodevtools` | 141/141, 17 suites, all PASSED | **141/141 succeeded**, 17 suites, all PASSED — agrees exactly with F2 (MERGE-06 satisfiable, §6) |
| F4a | `check_size_baseline.py --avr-log uno=...` | exit 0 | **exit 0** — `PASS: uno(flash=23932/32256,ram=1573/2048)` |
| F4b | `check_size_baseline.py --avr-log uno328pb=...` | exit 0 | **exit 0** — `PASS: uno328pb(flash=23976/32384,ram=1579/2048)` |
| F4c | `check_size_baseline.py --avr-log leonardo=...` | exit 0 | **exit 0** — `PASS: leonardo(flash=26072/28672,ram=2014/2560)` |
| F5a | `check_build_warnings.py --log uno=...` | exit 0, macro_redefinition==0 | **exit 0** — `PASS: uno: macro_redefinition=0 (== 0)` |
| F5b | `check_build_warnings.py --log uno328pb=...` | exit 0 | **exit 0** — `PASS: uno328pb: macro_redefinition=0 (== 0)` |
| F5c | `check_build_warnings.py --log leonardo=...` | exit 0 | **exit 0** — `PASS: leonardo: macro_redefinition=0 (== 0)` |
| F6a | `check_size_baseline.py --native-log native=...` | exit 0, cases=141/suites=17 | **exit 0** — `PASS: native(cases=141,suites=17)` |
| F6b | `check_size_baseline.py --native-log native_nodevtools=...` | exit 0 | **exit 0** — `PASS: native_nodevtools(cases=141,suites=17)` |
| F7a | `check_build_warnings.py --log native=...` | exit 0, total==360 | **exit 0** — `PASS: native: total warnings=360 (== watermark 360)` |
| F7b | `check_build_warnings.py --log native_nodevtools=...` | exit 0 | **exit 0** — `PASS: native_nodevtools: total warnings=360 (== watermark 360)` |
| F8 | `check_cmake_manifest.py` | `UNARMED:`, exit 0 | **exit 0** — see §4 for verbatim line |
| F9 | `check_orphan_provisional.py` | `UNARMED:`, exit 0 | **exit 0** — see §4 for verbatim line |

### Host repo (`/workspaces/firestarter_app`) — the MERGE-07 nine-gate / eleven-row set

| # | Command | Expected | Observed |
|---|---|---|---|
| H1 | `python3 tools/check_no_log_in_sdp_window.py` | PASS, exit 0 | **PASS** — resolved `.../firestarter/src/proms/eeprom_28c.cpp`, emitter lines 298-314, poll lines 348-361 |
| H2 | `pytest tests/test_check_no_log_in_sdp_window.py` | passed | **7 passed** |
| H3 | `pytest tests/test_sdp_table_parity.py` | passed | **5 passed** |
| H4a | `python3 tools/check_is_memory_cmd_no_ifdef.py` | PASS, exit 0 | **PASS** — no preprocessor conditional, exactly 8 commands |
| H4b | `pytest tests/test_check_is_memory_cmd_no_ifdef.py` | passed | **6 passed** |
| H5 | `python3 tools/gen_sdp_bus_config.py` (idempotence) | firmware tree unchanged from its own pre-run baseline | **PASS** — `git -C firestarter status --porcelain` was **empty before and empty after** (the pre-existing dirt this session recorded is zero for `firestarter`, so the idempotence baseline is the empty string, not the non-empty `?? firestarter/` baseline `122-NONREGRESSION.md` recorded for a different phase) |
| H6 | `pytest tests/test_sdp_bus_config_drift.py` | passed | **4 passed** |
| H7 | `pytest tests/test_revision_constants_parity.py` | passed | **13 passed** |
| H8 | `pytest tests/test_dispatch_mirror.py` | passed | **2 passed** |
| H9a | `python3 tools/check_dispatch.py` | PASS, exit 0 | **PASS** — 746 chips scanned; 736 supported; 10 confirmed non-dispatchable; 0 non_supported_dispatchable; 0 regressions; 0 consistency violations |
| H9b | `python3 tools/check_devtest_orchestrator.py` | PASS, exit 0 | **PASS** — scanned `chip_test.py`, `cli_handlers.py`, `submit.py`; 0 VPP-set, 0 raw-wire-dict, 0 `--force` |

All eleven rows PASS — none accepted on a prior plan's claim alone.

### Host repo — this phase's own gates (BASE-02/03/07/08, D-09/D-11/D-15/D-16)

| # | Command | Expected | Observed |
|---|---|---|---|
| H10 | 7 proxy modules, `-rs` | 49 passed, 0 skipped | **49 passed**, 0 skipped |
| H11 | `pytest tests/test_fw_presence.py tests/test_scan_paths_resolve.py tests/test_skip_census.py` | passed | **16 passed** |
| H12 | `python3 tools/check_no_exists_proxy.py` | PASS, exit 0, 78 files scanned | **PASS** — `scanned 78 file(s)...`, exit 0 |
| H13 | `python3 -m pytest tests/` | 1158 passed, 0 skipped | **1158 passed**, 0 skipped (confirmed via `-rs`: zero SKIPPED lines) |
| H14 | `ruff check firestarter/ tests/` | clean | **All checks passed!** |
| H15 | `ruff format --check firestarter/ tests/` | clean | **104 files already formatted** |
| H16 | `python tools/check_mypy_watermark.py` | below watermark | **1 error (watermark 35)** — 34 below, unchanged |

### Meta repo

| # | Command | Expected | Observed |
|---|---|---|---|
| M1 | `python3 -m pytest test_check_permitted_claims.py` | 10 passed | **10 passed** |
| M2 | `python3 check_permitted_claims.py` (no args) | exit 0, `UNARMED:` | **exit 0** — see §4 |
| M3 (courtesy) | claim-scan over this file | exit 0 | run after this file was written — see §7 |

---

## 4. What is UNARMED today and what arms it

```
UNARMED: /workspaces/firestarter/platform/py32f071 absent -- this gate arms itself the moment Phase 124 lands the py32f071 port (no manual flip needed; a rename inside the port cannot disarm it either).
```

Identical verbatim line from both `check_cmake_manifest.py` and `check_orphan_provisional.py`, both
exit 0, re-confirmed this session. **Arms:** `platform/py32f071/` appearing on disk (Phase 124). No
manual arm-flip constant exists in either script; a rename *inside* the port cannot disarm either gate,
only deleting the whole directory could, and that would report `UNARMED:` honestly rather than silently.

```
UNARMED: none of the 4 named v1.23 closing artifacts for Phase 130 exist yet (130-LEDGER.md, 130-DECISION.md, 130-RELEASE-NOTES-fw.md, 130-RELEASE-NOTES-app.md) -- the close has not started, so the claim gate has nothing to scan yet. This is expected before Phase 130 runs.
```

`check_permitted_claims.py`'s D-15 all-or-nothing arming — **arms:** any one of the four named
`130-*.md` artifacts appearing (Phase 130). No manual arm-flip exists here either.

---

## 5. Known and explained conditions — never silent

1. **Neither firmware workflow fires on the `v1.23-py32f071-integration` branch.** `build.yml` triggers
   on `push: branches: [main]` only; `beta-build.yml` on `beta` only (RESEARCH C-4). Neither is this
   milestone's working branch, so every firmware result in §3 is a **local run**, not continuous CI
   coverage. These checkers become CI-live only when this branch merges toward `beta` in Phase 130.
   Everything in this document is **local evidence** per D-05, not CI coverage.
2. **Host `ci.yml` performs a single checkout with no firmware sibling.** That absence of a cross-repo
   checkout is exactly why D-05 chose local evidence over a CI leg for MERGE-07/BASE-08 — a CI leg run
   today would score against `beta`, the wrong tree, since the matching firmware commit lives on an
   unpushed milestone branch. The standalone-CI skip fix (`81fa53c`, `beta`-only, carried forward per
   STATE.md) remains honest under this reading.
3. **The 360 native macro-redefinition warnings on each native env** — 8 macros (`PSTR`, `memcpy_P`,
   `pgm_read_byte`, `pgm_read_dword`, `pgm_read_ptr`, `pgm_read_word`, `strcpy_P`, `strlen_P`) × 45
   translation units each, from each suite's own `avr/pgmspace.h` shim being redefined by ArduinoFake's.
   Measured **pre-existing** on `beta` at the recorded fork point `5c9160a3...`, before any v1.23 work —
   **not a regression** and not damage. The zero-tolerance rule (`== 0`) is scoped to the three AVR envs,
   where the count is genuinely zero; the native envs carry a watermark (`<= 360`) so any *new* warning
   fails. RESEARCH's Option B (deduplicating the shims across 17 suite directories) was considered and
   rejected as a breach of this phase's no-firmware-code-moves boundary.
4. **`check_uno_ram.sh` was deleted, and it was already red.** Its `RAM_FLOOR=545` bytes is above the
   measured **475 B** free on Uno (2048 − 1573 used = 475), so the script would fail if run today; it was
   referenced by no workflow in either sub-repo (123-02's cross-repo grep). Its parse and its three-way
   exit taxonomy survive in `check_size_baseline.py`, which is strictly stronger — flash as well as RAM,
   three AVR envs rather than one, both native envs, and a recorded measurement rather than a
   hand-maintained floor.
5. **The D-14 pio-framing gap is closed** by `captured_native_warnings_excerpt.log`
   (`test_parser_survives_pio_test_framing`, 123-03) — the parser is proven against genuine `pio test`
   framing surrounding 8 real macro-redefinition diagnostics. **Residual limitation, stated honestly:**
   that capture is a partial excerpt (8 of the real 360 warnings, one per macro), not a full untruncated
   360-warning `pio test` log; `planted_build_warnings_native_excess.log` fills the volume-realism gap
   structurally but with synthetic content. The gap is closed for parser-survives-framing, not for
   volume-realism-from-one-real-log — 123-03-SUMMARY.md records this distinction and it still holds.
6. **The three pre-existing non-conforming host checkers** (`check_dispatch.py`,
   `check_sdp_capability_invariants.py`, `check_mypy_watermark.py`) are deliberately out of BASE-08's
   meta-test scope, which is `firestarter/scripts/` only (123-06's D-06 home choice). `check_mypy_watermark.py`'s
   missing test is a genuine gap, recorded here rather than blessed.
7. **Named pre-existing working-tree dirt.** `firestarter_app`: `M .gitignore`; untracked `.coverage`,
   `.planning/config.json`, `SECURITY.md`, `write_test_port.sh` — matches the dirt named in this plan's
   own dispatch prompt exactly, unchanged by any command run in this sweep. `firestarter`: clean
   (`git status --porcelain` empty). Meta: `firestarter_app` gitlink shows a `-dirty` suffix, which is
   the git plumbing's own reflection of the sub-repo's pre-existing untracked/modified state above, not
   a new gitlink pointer change — the gitlink's target commit (`ccbc401e...`) is unchanged.

---

## 6. The phase-wide no-firmware-code-moves proof

```
$ FORK=$(grep -oE '^fork_point_firmware: [0-9a-f]{40}$' 123-01-SUMMARY.md | cut -d' ' -f2)
$ echo "$FORK"
5c9160a34b665878b05403ab014b959926feb6bf
$ test -n "$FORK"; echo $?
0
$ git -C /workspaces/firestarter merge-base --is-ancestor "$FORK" HEAD; echo $?
0
$ git -C /workspaces/firestarter diff --stat "$FORK"..HEAD -- src include platformio.ini .github test
(empty)
$ git -C /workspaces/firestarter status --porcelain -- src include platformio.ini .github test
(empty)
```

This is the cumulative `<fork_point_firmware>..HEAD` range — covering every commit waves 1 through 7
made (123-01 through this plan's own upcoming commits) — not a working-tree comparison, which at phase
end would compare only the working tree against a HEAD that already contains all six prior waves and is
structurally incapable of seeing what those waves changed. `$FORK` is read from 123-01-SUMMARY.md's
`fork_point_firmware` field, asserted non-empty, and asserted an ancestor of HEAD before the diff runs.

**Anti-regression guard on the claim mechanism itself:**

```
$ grep -rlE -e 'diff --stat +--[^a-zA-Z-]' -e 'diff --stat +--$' \
    /workspaces/.planning/phases/123-non-regression-baselines-gate-hardening/ --include='*-PLAN.md' | wc -l
0
```

Observed integer: **0**. The vacuous ref-less `--stat` shape (the exact defect a plan-checker flagged as
a BLOCKER earlier in this phase) does not occur anywhere across the phase's own `*-PLAN.md` set, so it
cannot silently return by a later edit.

**Hand-off to Phase 124 (affirmative, per D-04):** both native envs agree at **141** cases / **17**
suites on this session's fresh measurement — **MERGE-06 is satisfiable exactly as worded and no
amendment should be requested.** D-04's feared live-divergence risk did not materialise. The
`PY32_EXCLUDED: <path> -- <reason>` comment format is committed (123-04) and Phase 124 populates it —
quoted verbatim from `check_cmake_manifest.py`'s own contract:

```cmake
# PY32_EXCLUDED: <path> -- <reason>
```

`check_cmake_manifest.py` will report exactly the `flash_type_3.cpp` / `flash_type_4.cpp` pair as
violations the moment `platform/py32f071/CMakeLists.txt` lands unchanged — MERGE-02's precise first
firing, since v1.19 Phase 104 renamed those two files to `flash_nor_unlock.cpp`/`flash_5v_page.cpp` and
the py32 branch's manifest still names the old filenames. `check_orphan_provisional.py` will fire on
`RURP_PY32F071_PINMAP_PROVISIONAL` (defined with exactly one repo-wide hit — its own definition, per
123-05-SUMMARY.md's restatement), which is the mechanism forcing MERGE-04 to actually wire the
provisional-pinmap refusal rather than leave it decorative.

---

## 7. The validation ceiling

Quoted verbatim from `.planning/REQUIREMENTS.md`:

> **No PY32F071 PCB exists.** Nothing in this milestone has ever run on this silicon, and nothing in it can.
>
> **Permitted claims:** the target builds clean; the native and host suites pass at their recorded case
> *and* suite counts; the DFU sequence is exercised against device descriptors and mocks; host-side
> timing and sizes are measured where a tool exists to measure them.
>
**Forbidden claim — cited by location, not reproduced verbatim (`.planning/REQUIREMENTS.md:14`):** the
eight-phrase forbidden list names an unqualified firmware-operates-on-silicon claim, an unqualified
end-to-end-install claim, three unqualified validation-adjective claims, a closed-loop-VPP claim, and a
pin-map-correctness claim. **Deliberate note on why this document does not reproduce that list's exact
wording:** doing so would itself trip this section's own claim-scanner below — the scanner matches each
phrase's shape regardless of quotation or negation context, by design (its own module docstring warns an
honestly-negated phrasing still trips the pattern). That is the gate working as intended, not a defect to
route around by weakening the pattern set; `REQUIREMENTS.md:14` remains the citable source of the
forbidden list's literal text.

**Line-by-line confirmation that nothing in this document asserts a forbidden claim.** Every result
above has a software artifact as its subject — a git blob/ref identity, a `pio run` size report, a
pytest exit code, a checker's own PASS/FAIL/UNARMED line, a source-read confirmation — never a silicon
observation. No PY32F071 hardware exists to observe. This entire document is measured figures only,
never rounded or paraphrased: **48**, **49**, **141**, **17**, **1158**, **360**, all six AVR flash/RAM
pairs, all cited exactly as observed.

**A green claim-scan is the mechanizable half only.** Running `check_permitted_claims.py` against this
file (courtesy check, since it is not one of the scanner's four default Phase 130 targets) proves no
*named forbidden phrase* co-occurs with a `py32`-shaped token within its 3-line proximity window — it
cannot and does not certify that every sentence in this document is honest by some broader human
judgment. The mechanizable half is the phrase-and-proximity check; the human-judgment half is reading
this document end to end, which this plan's own authorship is that reading.

---

## 8. Deliberately not taken

- **No firmware source moved, merged, cherry-picked or renamed.** §6's cumulative diff proves it across
  every commit this phase made, not merely this plan's own edits.
- **No `platformio.ini` edit.** The stale `[env:native_nodevtools]` "16-entry list" comments (three
  occurrences; the real list is 17 entries) stay unfixed — a deferred idea, not a defect this phase
  claims to have fixed.
- **No workflow edit.** `build.yml`, `beta-build.yml`, and host `ci.yml` are untouched by this phase.
- **No cross-repo CI leg added.** D-05's local-evidence choice stands; see §5.1-5.2.
- **No push, no `gh` invocation, no release, no tag, no gitlink bump.** This plan pushes nothing,
  publishes nothing, and comments nowhere public — Phase 130 owns every outward-facing action.
- **No baseline, watermark, floor, or allow-list was adjusted to make a row green.** Every row in §3
  passed as originally specified against the tree as found; no row required lowering a bar.

---

## Sweep Summary

| Gate | Result |
|---|---|
| Firmware pytest | **48 passed**, 0 skipped |
| Native `native` | **141/141**, 17 suites, all PASSED |
| Native `native_nodevtools` | **141/141**, 17 suites, all PASSED — agrees with `native` (MERGE-06 satisfiable) |
| AVR fresh builds × 2 gates each | all 3 envs match baseline byte-exact; both gates exit 0 for all 3 |
| Native fresh test-runs × 2 gates each | both envs; both gates exit 0 |
| Coarse-key gates (CMake, orphan-provisional) | both `UNARMED:`, exit 0, verbatim identical |
| No-firmware-code-moves cumulative diff | empty, `$FORK` ancestor-confirmed |
| Ref-less `--stat` guard over phase's own plans | **0** occurrences |
| Host 7 proxy modules | **49 passed**, 0 skipped |
| Host 11-row cross-repo gate table | all 11 PASS |
| Host skip census + scan-path resolve + fw-presence | **16 passed** |
| `check_no_exists_proxy.py` | PASS, 78 files scanned |
| Host full suite | **1158 passed**, 0 skipped |
| Host ruff / ruff-format / mypy-watermark | all green (1 error, 34 below watermark, unchanged) |
| Meta claim-gate self-test | **10 passed** |
| Meta claim-gate default run | `UNARMED:`, exit 0 |
| All three repos' branch state | firmware + host on `v1.23-py32f071-integration`; meta on `gsd/v1.23-py32f071-integration` |

**Phase 123's entire verification surface is green, re-executed against the tree exactly as it stands
at the end of this phase — local evidence, not CI coverage, per D-05.** This plan ticks BASE-01 through
BASE-08 in `.planning/REQUIREMENTS.md`, citing the specific row above that justifies each (see
`123-11-SUMMARY.md`).
