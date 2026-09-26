---
phase: 149
slug: firmware-page-size-seam-dual-repo-lockstep
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-19
---

# Phase 149 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `149-RESEARCH.md` §Validation Architecture (measured, not estimated).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Unity via PlatformIO (firmware native), pytest 9.1.1 + syrupy (host), pytest (firmware scripts) |
| **Config file** | `firestarter/platformio.ini` `[env:native]` (`:69-119`, `test_filter` 17 entries) · `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` (`addopts = "-ra -q"`) |
| **Quick run command** | `cd firestarter && pio test -e native -f native/avr/test_val_eeprom28c -f native/avr/test_read_timing` (**5.8 s**) |
| **Full suite command** | `cd firestarter && pio test -e native && pio test -e native_nodevtools` (141 cases / 17 suites each, both must agree) · `cd firestarter_app && python3 -m pytest tests/ -o addopts="" -q` (**218 s**, 1641 tests) · `cd firestarter && python3 -m pytest tests/ -q` (**10.7 s**, 314 tests) |
| **Estimated runtime** | ~6 s quick (native) · ~230 s full (host + firmware scripts) · cold `pio run` ×3 for the size gate |

**Traps that make a run dishonest** (all measured — see `149-RESEARCH.md`):

- `addopts` is `-ra -q`; a second `-q` hides the count line. Use `-o addopts=""` when counts matter.
- `test_flash_path_record_sync.py` asserts **whole-repo** git porcelain — commit before running the host suite.
- Devcontainer python is 3.12; app CI runs 3.9/3.11. A local green is not a CI green. Use `firestarter_app/tools/ci_parity.sh` (4 legs).
- Warning watermarks are **cold-only** figures (native 998 warm vs 1166 cold). A warm re-measure reads as headroom that does not exist.
- The record gate needs a **300 s** timeout — `STATE.md` carries a ~52k-char single line; a short timeout returns rc=124 and reads like a RED.

---

## Sampling Rate

- **After every task commit (firmware):** `pio test -e native -f native/avr/test_val_eeprom28c -f native/avr/test_read_timing` (5.8 s) + `python3 -m pytest tests/ -q` (10.7 s)
- **After every task commit (host):** targeted module run — `python3 -m pytest tests/test_wire_dict_equivalence.py tests/test_json_key_parity.py tests/test_page_size_invariants.py -o addopts="" -q`
- **After every task commit (meta):** `python3 .planning/phases/149-*/149-check-claims.py` (< 1 s)
- **After every plan wave (firmware):** `pio test -e native` **and** `pio test -e native_nodevtools` (compared, `envs_agree`) + `python3 -m pytest tests/ -q` + `pio run` for all three AVR envs
- **After every plan wave (host):** `python3 -m pytest tests/ -o addopts="" -q` + `ruff check firestarter/ tests/` + `ruff format --check firestarter/ tests/` + `python tools/check_mypy_watermark.py`
- **Before `/gsd-verify-work` (phase gate):** cold `pio run` ×3 · `check_size_baseline.py` default **and** `--policy merge05` · cold `check_build_warnings.py` · `tools/ci_parity.sh` (all 4 legs) · `python3 tools/diff_db.py` · the 149 claim gate — all green
- **Max feedback latency:** 6 s (native quick) / 20 s (firmware scripts) / 230 s (full host)

---

## Per-Task Verification Map

Task IDs do not exist until `*-PLAN.md` files are written. The requirement→observable→command mapping below is
the **binding** contract; the executor fills `Task ID` / `Plan` / `Wave` / `Status` as plans land.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | C | 1 | PGSZ-01 | — | Only the 18 upstream-native `0x0D` rows gain `programming.page_size`; the 66 promoted rows and AT28C256 do not | unit (host) | `python3 -m pytest tests/test_page_size_invariants.py -o addopts="" -q` | ❌ W0 | ⬜ pending |
| TBD | C | 1 | PGSZ-01 | — | Every emitted `page_size` across all 746 rows is a power of two in range **and** provenance-corroborated (D-07) | unit (host) | same file | ❌ W0 | ⬜ pending |
| TBD | C | 1 | PGSZ-01 | — | Wire capture = golden **plus exactly the 18 named deltas**; golden still carries exactly 2 `page-size` records | unit (host) | `python3 -m pytest tests/test_wire_dict_equivalence.py -o addopts="" -q` | ✅ (modified + new fixture) | ⬜ pending |
| TBD | C | 1 | PGSZ-01 | — | Wire key union stays exactly 9 | unit (host) | `test_wire_key_union_is_exactly_nine_keys` | ✅ | ⬜ pending |
| TBD | C | 1 | PGSZ-01 | — | `diff_db` census invariant: exit 0, 744 changed, 0 unexplained, 0 new, 0 missing, buckets **686/56/2**, +18 `programming.page_size` compound secondaries | integration (host) | `python3 tools/diff_db.py; echo $?` | ✅ | ⬜ pending |
| TBD | D | 1 | PGSZ-01 | — | `"page-size":128` parsed off the wire into the handle field | unit (native) | `pio test -e native -f native/avr/test_read_timing` | ✅ (new case) | ⬜ pending |
| TBD | D | 1 | PGSZ-02 | — | Absent field ⇒ handle field 0 ⇒ 64 floor: **flush count 2** on a 128-byte geometry | unit (native) | `pio test -e native -f native/avr/test_val_eeprom28c` | ✅ (new case) | ⬜ pending |
| TBD | D | 1 | PGSZ-02 | — | Delivered 128 ⇒ **flush count 1** on the same geometry | unit (native) | same | ✅ (new case) | ⬜ pending |
| TBD | D | 1 | PGSZ-02 | — | Field resets to 0 between two commands on the **same** handle (D-05) | unit (native) | `pio test -e native -f native/avr/test_read_timing` | ✅ (new case) | ⬜ pending |
| TBD | D | 1 | PGSZ-02 | — | An unknown key before a known one does not desync the token walk (D-11) | unit (native) | same | ✅ (new case) | ⬜ pending |
| TBD | D | 1 | PGSZ-02 | — | Non-power-of-two / out-of-range ⇒ silent 64 fallback (flush count 2, no log) | unit (native) | `pio test -e native -f native/avr/test_val_eeprom28c` | ✅ (new case) | ⬜ pending |
| TBD | D | 1 | PGSZ-02 | — | The three pre-existing `test_fix06_*` cases are behaviourally byte-unchanged | regression (native) | same | ✅ | ⬜ pending |
| TBD | E | 2 | PGSZ-03 | — | `JSON_KEY_PAGE_SIZE` equals the PROGMEM key string in `src/json_parser.c` **and** that identifier appears in `key_parsers[]` | unit (host, scans fw) | `python3 -m pytest tests/test_json_key_parity.py -o addopts="" -q` | ❌ W0 | ⬜ pending |
| TBD | E | 2 | PGSZ-03 | — | All 3 `JSON_KEY_*` constants map two-way, with a named firmware-side exemption tuple | unit (host, scans fw) | same file | ❌ W0 | ⬜ pending |
| TBD | E | 2 | PGSZ-03 | — | `src/json_parser.c` is in the committed inventory and resolves | unit (host) | `python3 -m pytest tests/test_scan_paths_resolve.py -o addopts="" -q` | ✅ (one entry added) | ⬜ pending |
| TBD | E | 2 | PGSZ-03 | — | The gate SKIPS (not fails) with no firmware checkout, planted legs stay LIVE | integration (host) | `FIRESTARTER_FW_ROOT=$(mktemp -d) python3 -m pytest tests/ -rs -o addopts="" -q` | ✅ mechanism | ⬜ pending |
| TBD | E | 2 | PGSZ-03 | — | The gate goes RED on a planted undispatched / mismatched key | negative control (host) | `python3 -m pytest tests/test_json_key_parity.py -o addopts="" -q` (fixture legs) | ❌ W0 + fixtures | ⬜ pending |
| TBD | A | 0 | PGSZ-04 | — | Cold baseline captured at the v1.32 fork, **before** the first edit, all three envs | manual-then-recorded | `rm -rf .pio/build/<env> && pio run -e <env>` ×3, output committed | ❌ W0 (P-2) | ⬜ pending |
| TBD | F | 2 | PGSZ-04 | — | Post-change flash + RAM measured **cold**, all three envs; deltas stated | manual-then-recorded | same procedure, post-edit | ❌ | ⬜ pending |
| TBD | F | 2 | PGSZ-04 | — | Default byte-identity gate + `--policy merge05` both exit 0 against BASE-01 | integration (fw script) | `python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log uno=… --avr-log uno328pb=… --avr-log leonardo=…` (the flag is `--avr-log` / `--native-log`; **`--log` does not exist** on this script — it is the *warning* gate's flag) | ✅ | ⬜ pending |
| TBD | F | 2 | PGSZ-04 | — | The tripwire is still ARMED one byte past the **new** allowance | negative control (fw) | `python3 -m pytest tests/test_check_size_baseline.py -q` with re-planted fixtures | ✅ (4 legs + 2 fixtures modified) | ⬜ pending |
| TBD | F | 2 | PGSZ-04 | — | AVR warnings `== 0`; native `<= 1166` on both pinned envs, measured **cold** | integration (fw script) | `python3 scripts/check_build_warnings.py --rebuild …` | ✅ | ⬜ pending |
| TBD | F | 2 | PGSZ-04 | — | `native` / `native_nodevtools` still agree on `{cases, suites, all_passed}`; suites stays 17 | integration (fw) | `pio test -e native` + `pio test -e native_nodevtools`, compared | ✅ | ⬜ pending |
| TBD | B | 0 | PGSZ-05 | — | Every 149 artifact contains the literal phrase and zero forbidden claims | integration (meta) | `python3 .planning/phases/149-*/149-check-claims.py` | ❌ W0 | ⬜ pending |
| TBD | B | 0 | PGSZ-05 | — | Gate goes RED on a planted overclaim, GREEN after revert; both transcripts committed | negative control (meta) | same + `python3 -m pytest .planning/phases/149-*/test_check_claims_v132.py -q` | ❌ W0 + fixtures | ⬜ pending |
| TBD | B | 0 | PGSZ-05 | — | The surviving `proven` pattern still fires on an unqualified "proven" (X-2) | negative control (meta) | same fixture suite | ❌ W0 | ⬜ pending |
| TBD | C | 1 | PGSZ-05 | — | `0x0D` rows' `support_status` byte-unchanged; AT28C256's wire dict byte-unchanged | unit (host) | `python3 -m pytest tests/test_page_size_invariants.py -o addopts="" -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Fork `firestarter` off `origin/beta` + **cold** pre-edit capture, all three envs — **P-1/P-2, blocks every firmware plan**
- [ ] `.planning/phases/149-*/149-check-claims.py` + `test_check_claims_v132.py` + `fixtures/` — D-19, incl. the `\bproven\b` resolution (X-2)
- [ ] `firestarter_app/tests/test_page_size_invariants.py` — PGSZ-01 selection + D-07 exhaustive invariant + provenance + AT28C256 non-change + `extra_chips.json` back door
- [ ] `firestarter_app/tests/test_json_key_parity.py` — PGSZ-03 two-way parity (D-18)
- [ ] `firestarter_app/tests/fixtures/planted_json_parser_*.c` — the parity gate's RED legs (no `requires_fw`, so live in app CI)
- [ ] `firestarter_app/tests/golden/wire_dict_expected_deltas_149.json` — D-17's 18 deltas, generated from the golden
- [ ] Re-planted `firestarter/tests/fixtures/planted_size_baseline_policy_{leonardo_growth,uno_over_band}.log` — after the allowance `N` is known
- [ ] New cases in `test_read_timing_params.cpp` and `test_val_eeprom28c.cpp` — **extensions, not new files** (D-15: a new suite adds TUs and very likely warnings against a watermark with zero headroom)

*No framework install is needed: Unity, PlatformIO, pytest and syrupy are all present and green (P-4…P-7).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Cold flash/RAM capture, all three envs | PGSZ-04 | Requires a clean `.pio/build/<env>` and a real toolchain invocation; a warm build silently reuses objects and a warm warning count reads 998 vs the cold 1166 | `cd firestarter && rm -rf .pio/build/<env> && pio run -e <env>` for `uno`, `uno328pb`, `leonardo`; commit the transcripts |
| Wording review of `149-PAGE-SIZE.md`, the SUMMARYs and the changelog line | PGSZ-05 | The claim gate's own donor states it "cannot detect an implied overclaim, a misleading omission, a wrong tone, or a true statement placed where it misleads" (`146-check-claims.py:87-95`) | Human read of every 149 artifact after the gate is green; confirm no sentence implies silicon validation, `0x0D` graduation, or that gh#21/#32/#11/#12 is closed |
| MERGE-05 exemption justification + SHA attribution | PGSZ-04 | The *value* is mechanical; the *justification* is a judgement about whether the growth was necessary, which no gate can make | Review the new constant's docstring: it must name its own commit SHAs and state leonardo's remaining headroom as a number, with the v1.31 band breach named |

**Explicitly NOT verifiable in this phase (Evidence Ceiling, binding):** no criterion may be satisfied by silicon.
No AT28C part exists in operator inventory; `REQUIREMENTS.md` §Out of Scope excludes bench validation of the
page-size change. Criterion 1's "observed to deliver 128" is a **native flush-count** assertion on a host
compiler — it is not, and must not be described as, an observation on hardware.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 230s (full host suite; 6s for the native quick run)
- [ ] Every negative control was **seen** to fail before it was trusted (claim gate RED leg, parity planted legs, re-planted size fixtures)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
