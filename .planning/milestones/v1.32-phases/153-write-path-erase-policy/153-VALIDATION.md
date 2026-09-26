---
phase: 153
slug: write-path-erase-policy
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-21
---

# Phase 153 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `153-RESEARCH.md` §"Validation Architecture".
> **Dual-repo phase** — two frameworks, two sampling regimes.
> **No AT28C part is required or permitted as a validation dependency** (ERASE-09). Every requirement
> below is provable in software; the ones that are *only* provable in software are marked so.

---

## Test Infrastructure

| Property | Host (`firestarter_app/`) | Firmware (`firestarter/`) |
|----------|---------------------------|---------------------------|
| **Framework** | pytest (`pyproject.toml:105-107`, `addopts = "-ra -q"`) | PlatformIO + Unity (`pio test`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` | `platformio.ini` — `[env:native]` at `:97`, `test_filter` allowlist at `:130-151` (17 suites) |
| **Quick run command** | `pytest tests/<module>.py -o addopts="" -q` | `pio test -e native -f native/avr/<suite>` |
| **Full suite command** | `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` | `pio test -e native` **then** `pio test -e native_nodevtools` (both must agree) |
| **Install** | `pip install -e '.[test]'` — **never `.[dev]`** | toolchain already present |
| **Estimated runtime** | ~90 s full host suite | ~60 s native; +~3 min per cold AVR build |

**Static / cross-repo gates**

| Gate | Command |
|------|---------|
| Host lint | `ruff check firestarter/ tests/` · `ruff format --check firestarter/ tests/` |
| Host types | `python tools/check_mypy_watermark.py` (watermark 35, current 33) |
| Dispatch (GATE-03) | `python tools/check_dispatch.py` · `pytest tests/test_check_dispatch_invariants.py` |
| SDP log window | `python tools/check_no_log_in_sdp_window.py` |
| Cross-repo parity | `pytest tests/test_sdp_table_parity.py tests/test_dispatch_mirror.py` |
| Size — byte identity | `python scripts/check_size_baseline.py --avr-log <env>=<log>` |
| Size — MERGE-05 band | `python scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log <env>=<log>` (**always name BASE-01 explicitly**) |
| Build warnings | `python scripts/check_build_warnings.py` |

**Traps that invalidate a green run:**

- `addopts` already carries `-q` — doubling it hides the count line. Use `-o addopts=""` when you need a count.
- Devcontainer python is **3.12**; app CI is **3.11 only**. A pass here is not a pass there.
- The default-mode size gate checks native **case counts**, not just bytes — a new native case changes it.
- **Neither repo's CI runs the size gate**, and the devcontainer's sibling layout hides cross-repo failures.
- Native trace stubs record **no time** — they cannot prove the 20 ms `tEC` wait. That assertion must be structural, not temporal.
- `check_no_log_in_sdp_window.py` **fails closed** on a `write_init` refactor.

---

## Sampling Rate

- **After every task commit (firmware):** `pio test -e native -f native/avr/<touched suite>` (< 30 s).
- **After every task commit (host):** `pytest tests/<touched file> -o addopts="" -q` (< 30 s).
- **After every wave (firmware):** `pio test -e native` **and** `pio test -e native_nodevtools` (must agree), plus `pio run -e leonardo` for an early flash/RAM read on any wave that lands firmware bytes.
- **After every wave (host):** `ruff check` + `ruff format --check` + `check_mypy_watermark.py` + `pytest tests/ --cov=firestarter --cov-fail-under=70`.
- **Phase gate:** all of the above, plus `check_dispatch.py`, `check_no_log_in_sdp_window.py`, three **cold** AVR builds, **both** `check_size_baseline.py` modes, and `check_build_warnings.py`.
- **Max feedback latency:** 90 s host / 60 s firmware-native.

---

## Per-Requirement Verification Map

Task IDs are assigned at planning time; this map is the requirement-level contract each task must inherit.

| Req | Behavior to prove | Test Type | Automated Command | File Exists | Status |
|-----|-------------------|-----------|-------------------|-------------|--------|
| ERASE-01 | No `mem_util_blank_check` call remains in `eeprom28c_write_init`; write-INIT is single-shot | source-scan + unit | `grep -c 'mem_util_blank_check' firestarter/src/proms/eeprom_28c.cpp` → **1** (the `CMD_BLANK_CHECK` arm only); native case driving `CMD_WRITE` init with `FLAG_SKIP_BLANK_CHECK` **clear**, asserting zero read strobes before the SDP stream | ❌ W2 (new case in `test_eeprom28c_sdp`) | ⬜ pending |
| ERASE-01 | The `0x0D` write stream is otherwise unchanged | golden/stream | `pio test -e native -f native/avr/test_eeprom28c_sdp` — Cases 1–5 (`*_stream_matches_fixed`) green **unmodified** | ✅ `test_eeprom28c_sdp.cpp:1708-1712` | ⬜ pending |
| ERASE-02 | Sibling **located** then removed; `0x05` write path otherwise intact | source-scan + unit | `grep -n 'FLAG_SKIP_BLANK_CHECK' firestarter/src/proms/flash_5v_page.cpp` → **0 hits**; `pio test -e native -f native/avr/test_val_5v_page` | ✅ suite exists; ❌ new negative case W2 | ⬜ pending |
| ERASE-03 (fw) | `CMD_ERASE` on `0x0D` sets a non-NULL main | unit | `pio test -e native -f native/avr/test_dispatch` — group 4 **inverted** to `TEST_ASSERT_NOT_NULL` | ✅ `test_configure_memory.cpp:310` (**must invert**) | ⬜ pending |
| ERASE-03 (fw) | End-to-end: `CMD_ERASE` dispatches, emits the six-write stream, returns `RESPONSE_CODE_OK`, emits **no** `MSG_ERR_NOT_SUPPORTED` | unit/stream | `pio test -e native -f native/avr/test_eeprom28c_sdp` — Case 25 **inverted** + new stream-equality case | ✅ `:1390` (**must invert**) | ⬜ pending |
| ERASE-03 (fw) | The `CMD_ERASE` arm asserts **no** VPP | unit | new case in `test_val_eeprom28c.cpp` modelled on `test_eeprom28c_blank_check_configure_no_vpp` (`:399`) | ❌ W2 | ⬜ pending |
| ERASE-03 (host) | All 84 algorithm-13 rows carry `FLAG_CAN_ERASE`; algorithm-5 rows still do **not**; UV-EPROM still does not | unit | `pytest tests/test_database_conversion.py -o addopts="" -q` — `:98-117` **inverted**; `:120-131` (W29C040, algo 5) and `:89-95` (M27C512 UV) unchanged as negative controls | ✅ (one inversion, two controls green) | ⬜ pending |
| ERASE-03 (host) | Exhaustive: **exactly 84** rows gain the flag, 0 non-13 rows change | unit | new leg iterating all 746 DB rows, modelled on `tests/test_page_size_invariants.py` leg 6 | ❌ W3 | ⬜ pending |
| ERASE-04 | The emitted sequence equals AN 0544B's six pairs, in order | unit/stream | native stream-equality case asserting the six `(address, byte)` writes | ❌ W2 | ⬜ pending |
| ERASE-04 | The erase stream **diverges** from SDP-disable at exactly the terminal byte (`0x10` vs `0x20`) | unit/stream | new case modelled verbatim on `test_case18/19_..._diverges_at_exact_index` (`:1082-1124`) — assert an **exact** divergence index, **never `!= -1`** | ❌ W2 (Case 19 is the template) | ⬜ pending |
| ERASE-04 | **No** VPP/VPE control-register write anywhere in the erase path | source-scan (negative) | brace-match `eeprom28c_erase_execute`; assert 0 occurrences of `CTRL_VPE`, `CTRL_VPP_REGULATOR_ENABLE`, `firestarter_set_control_register` | ❌ W2 — **this is the primary GATE-03 control** | ⬜ pending |
| ERASE-04 | `check_dispatch.py` unweakened, unexempted, un-re-baselined | source + behaviour | `git diff --quiet -- tools/check_dispatch.py` at phase end **and** `python tools/check_dispatch.py` exit 0 **and** `pytest tests/test_check_dispatch_invariants.py` green | ✅ all three exist | ⬜ pending |
| ERASE-05 | `blank` still reaches `mem_util_blank_check` and still reports not-blank correctly | unit | `pytest tests/test_characterization.py tests/test_eprom_operations.py -k blank -o addopts="" -q`; firmware: `pio test -e native -f native/avr/test_val_eeprom28c` case at `:399` **unchanged** | ✅ both exist — **non-regression, no new work** | ⬜ pending |
| ERASE-06 | `info`'s row and the wire flag agree for an algorithm-13 chip | unit | new leg asserting `build_specifications(...)["can_erase_str"].startswith("yes")` **and** `convert_to_programmer(...)["flags"] & FLAG_CAN_ERASE` for the same chip — one assert pair, both directions | ❌ W3 (`tests/test_ic_layout.py`) | ⬜ pending |
| ERASE-07 | The comment no longer asserts the two false claims | source-scan | `grep -c 'has no erase operation at' firestarter_app/firestarter/database.py` → **0**; `grep -c 'never reads FLAG_CAN_ERASE' …` → **0**; algorithm-5 rationale still present | ❌ W3 (grep criteria sufficient) | ⬜ pending |
| ERASE-08 | Constants lockstep | source-scan | parity check of `FLAG_CAN_ERASE` / `FLAG_SKIP_ERASE` / `FLAG_SKIP_BLANK_CHECK` / `CMD_ERASE` / `CMD_BLANK_CHECK` between `firestarter/include/firestarter.h` and `firestarter_app/firestarter/constants.py`; `pytest tests/test_revision_constants_parity.py` | ✅ exists | ⬜ pending |
| ERASE-08 | Cold flash/RAM on all three AVR targets vs the pre-change baseline | measurement | per target: `rm -rf .pio/build/<env> && pio run -e <env> 2>&1 \| tee <log>`, then `check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log <env>=<log>` | ✅ script exists | ⬜ pending |
| ERASE-08 | Native case/suite counts recorded and agreeing | measurement | `pio test -e native` + `pio test -e native_nodevtools`, then `check_size_baseline.py --native-log native=<log> --native-log native_nodevtools=<log>` | ✅ | ⬜ pending |
| ERASE-08 | Tripwire still armed above the new `v153` allowance | unit | `pytest tests/test_check_size_baseline.py -o addopts="" -q` with a **new `*_v153*` fixture family**, each fixture re-derived from `allowance+1` and **observed** to fail | ✅ suite exists; ❌ new family W4 | ⬜ pending |
| ERASE-09 | No `support_status` write, no graduation | source + gate | `python tools/check_no_community_support_status_write.py`; `python tools/check_diagnostic_report_claims.py`; `git diff -- firestarter/data/chip_database.json` empty | ✅ all exist | ⬜ pending |
| ERASE-09 | The phrase "software-proven and unvalidated on silicon" appears in the phase's own record | source-scan | `grep -rc 'software-proven and unvalidated on silicon' .planning/phases/153-*/` ≥ 1 | ❌ W5 (artifact) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] **Decision record** naming the erase mechanism (inline / `PROGMEM` / `.data`+exemption) with the measured 30 B RAM figure cited. This is a *precondition* to writing code — choosing wrong is a MERGE-05 blocker, not a note. **Operator has locked: RAM-neutral inline form + a named `v153` flash exemption.**
- [ ] Pre-change **cold** baseline logs in `firestarter/scripts/baseline/` for `uno`, `uno328pb`, `leonardo`. Leonardo reproduced during research (27500 / 2016, byte-identical to the committed baseline); `uno` and `uno328pb` **not yet**.
- [ ] Pre-change host suite count + coverage figure, captured once with `-o addopts=""`.
- [ ] Settle the SDP-disable-prefix question (Open Question 1) before the erase body is written — a phantom erase reporting OK is the exact failure class Phase 121 D-12 fought.

Framework install: **none needed.** Both frameworks are present and green.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The erase actually erases a physical AT28C part | — | **Deliberately out of scope.** ERASE-09 forbids requiring an AT28C part, and no ERASE requirement asserts the `0x0D` write path is proven. | Not performed. The phase ships **software-proven and unvalidated on silicon**. |

**Software-only by construction** (no silicon can be cited as evidence for these, and none is needed): ERASE-01, ERASE-02, ERASE-04 (sequence identity + the negative VPP scan), ERASE-05, ERASE-07, ERASE-08, ERASE-09.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all ❌ MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 90 s
- [ ] Every `!= -1` style divergence assertion replaced by an exact index
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
