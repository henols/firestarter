---
phase: 119
slug: lock-sdp-enable-command-surface-fw-half
status: approved
nyquist_compliant: true
wave_0_complete: false
created: 2026-07-28
approved: 2026-07-28
---

> **Status note.** `nyquist_compliant: true` records that the *plan set* satisfies this contract — all 11 plans carry automated `<verify>` commands on every task, and every requirement below has a named oracle. `wave_0_complete` stays `false` because the Wave 0 artifacts (the `test_cmd_admission` suite, `[env:native_nodevtools]`, the `SDP_FIXED_LOCK_*` goldens, the new host gate) are *created during execution* by plans 119-02, 119-03 and 119-05 — it flips to `true` when those land.

# Phase 119 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `119-RESEARCH.md` § Validation Architecture. Baseline measured 2026-07-28 at firmware HEAD `1880054`.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Unity via PlatformIO (`test_framework = unity`, `firestarter/platformio.ini:70`) + pytest (host) |
| **Config file** | `firestarter/platformio.ini` — `[env:native]`, plus NEW `[env:native_nodevtools]` (Wave 0) |
| **Quick run command** | `pio test -e native -f "*test_eeprom28c_sdp*" -f "*test_sdp_harness*"` |
| **Full suite command** | `pio test -e native && pio test -e native_nodevtools && pio run` (firmware); `python3 -m pytest -q` + gate scripts (host) |
| **Estimated runtime** | ~2 s quick; ~60 s full firmware + host |

**Measured baseline (2026-07-28, firmware `1880054`):**

| Gate | Baseline |
|------|----------|
| `pio test -e native` | 112/112, 16/16 suites |
| `pio test -e native_nodevtools` | 112/112 (proven this session with zero test-code changes) |
| `pio run` (uno, uno328pb, leonardo) | 3/3 SUCCESS |
| Leonardo flash | 25680 / 28672 B → **2992 B free** (supersedes LOCK-06's stale 3348 B) |
| `-D DEV_TOOLS` cost | 1292 B Leonardo flash |
| Host pytest (4 relevant modules) | 21/21 |
| `tools/check_no_log_in_sdp_window.py` | PASS (exit 0) |
| `tools/check_dispatch.py` | exit 0 |

---

## Sampling Rate

- **After every task commit:** `pio test -e native -f "*test_eeprom28c_sdp*" -f "*test_sdp_harness*"` (~2 s) **plus** `python3 tools/check_no_log_in_sdp_window.py` (~0.2 s). The second is non-negotiable on any `eeprom_28c.cpp` touch — it is the cross-repo gate that fails closed while the firmware suite stays green.
- **After every plan wave:** `pio test -e native` AND `pio test -e native_nodevtools` AND `pio run` (all three envs) AND the full host gate set (pytest + `check_no_log_in_sdp_window.py` + `check_dispatch.py` + the new D-04 gate). Phase 118 proved that re-running every gate at every wave is what produced zero host-CI surprises.
- **Before `/gsd-verify-work`:** everything above green, plus `119-MEASUREMENT.md` and `119-NONREGRESSION.md` complete with provenance.
- **Max feedback latency:** ~2 s per task; ~60 s per wave.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| *(filled by the executor as tasks land — the requirement→oracle map below is the contract)* | | | | | | | | | |

### Requirement → oracle contract (from RESEARCH.md)

| Req | Behaviour to observe | Test type | Automated command | Exists? |
|-----|----------------------|-----------|-------------------|---------|
| LOCK-01 | Lock emits exactly the 3-load `AA·55·A0` stream on each of 4 pinouts, then `delay(t_WC)`, no data write after | firmware unit (golden trace) | `pio test -e native -f "*test_eeprom28c_sdp*"` | ❌ new cases + `SDP_FIXED_LOCK_*` goldens |
| LOCK-01 | Lock stream diverges from unlock at an exact index, and from `FLASH_ERASE` at an exact index | firmware unit (negative) | same | ❌ new |
| LOCK-02 | `configure_eeprom28c` sets a main for cmd 9 and cmd 10, leaves `init`/`end` NULL | firmware unit (dispatch) | `pio test -e native -f "*test_dispatch*"` | ❌ new cases |
| LOCK-02 | Standalone op is single-step — 4 ACKs, no `#` frame, no `DONE` | firmware unit **under F-F option (a)**; else reasoned from `CMD_ERASE` precedent | `pio test -e native` | ⚠ gated on Open Question 1 |
| LOCK-03 | `is_memory_cmd(c)` identical for every `c ∈ [0,255]` in BOTH build configurations | firmware unit (truth table, run in 2 envs) | `pio test -e native -f "*test_cmd_admission*"` AND `pio test -e native_nodevtools -f "*test_cmd_admission*"` | ❌ new suite |
| LOCK-03 | Predicate body contains no `#ifdef DEV_TOOLS`, enumerates exactly the 8 expected commands | host source-scan gate | `python3 tools/check_is_memory_cmd_no_ifdef.py` | ❌ new gate |
| LOCK-03 | …and that gate can actually fail | host pytest + planted fixture | `python3 -m pytest tests/test_check_is_memory_cmd_no_ifdef.py` | ❌ new |
| LOCK-03 | Whole native suite passes with `DEV_TOOLS` absent | firmware full suite | `pio test -e native_nodevtools` | ✅ demonstrated 112/112 |
| LOCK-04 | Lock/unlock on a non-`0x0D` protocol refused with `MSG_ERR_NOT_SUPPORTED`, never silently accepted | firmware unit **under F-F option (a)** | `pio test -e native` | ⚠ gated on Open Question 1 |
| LOCK-04 | `CMD_READ`/`CMD_WRITE`/`CMD_VERIFY` never NULL-main for any protocol reaching a handler | firmware unit (positive invariant) | `pio test -e native -f "*test_dispatch*"` | ❌ new — cheap, high value |
| LOCK-05 | `EEPROM_SDP_ENABLE` == `FLASH_ENABLE_WRITE_PROTECTION` == `FLASH_ENABLE_WRITE` byte-for-byte AND all three distinct objects | firmware unit | `pio test -e native -f "*test_sdp_harness*"` | ⚠ two-way leg exists (`test_sdp_harness.cpp:291-310`); third leg + distinctness ❌ |
| LOCK-05 | Lock stream terminates after exactly 3 command writes — no trailing data write | firmware unit (stream length) | same | ❌ new |
| LOCK-06 | Measured flash delta on all three envs, within the 2992 B Leonardo headroom | flash-size measurement | `pio run -e uno -e uno328pb -e leonardo` diffed against a `git worktree` at the phase base | ✅ base measured; delta pending |
| DEVTEST-01 (fw half) | `CMD_ERASE` on `0x0D` is refused, not silently OK | firmware unit **under F-F option (a)** | `pio test -e native` | ⚠ gated on Open Question 1 |
| D-08 sweep | `0x05/0x06/0x07/0x08/0x0B/0x10`/SRAM bus streams stay byte-identical | firmware unit + per-array golden byte-identity | `pio test -e native` (all 16 suites) | ✅ suites exist; per-array identity record ❌ |
| D-12 | Lock reports OK AND the message text says the state is unreadable | firmware unit (frame-id + catalog format) | `pio test -e native -f "*test_eeprom28c_sdp*"`; `codegen.py --check` | ❌ new |
| D-14 | Lock's `t_BLC` budget WARN fires when over budget AND does not fire at default elapsed | firmware unit (paired positive + anti-hollow control) | `pio test -e native -f "*test_eeprom28c_sdp*"` | ❌ new; requires the micros-mock upgrade |
| D-14 | Budget WARN never writes `response_code` | firmware unit | same | ✅ pattern exists |
| D-16 | Worst-case per-byte page-load interval, reported once per write | **bench measurement, 3 boards** | `firestarter write <chip> -b --force` per port | ❌ **hardware** |
| Catalog ritual | meta ↔ firmware ↔ host byte-identical; both generated artifacts drift-free | three-way `cmp` + two `--check` gates | `tools/catalog/sync_to_subrepos.sh`; `codegen.py --check` in each sub-repo | ✅ tooling exists |
| GATE-03 | Host lint against the CI Python targets | host lint | `ruff check` / `ruff format --check` under py3.9/3.11 (**not** 3.12) | ✅ |

---

## Wave 0 Requirements

- [ ] `firestarter/test/native/avr/test_cmd_admission/` — the `is_memory_cmd()` truth table over every cmd value (LOCK-03). Needs `test_*.cpp`, a `host_stubs.cpp` including `_shared/host_stubs_common.inc`, an `avr/pgmspace.h` shim if any header pulls PROGMEM, **plus a `test_filter` line and a matching `-I` line in BOTH native envs**.
- [ ] `firestarter/platformio.ini` — `[env:native_nodevtools]` with its own full `test_filter` + `-I` list and explicit `-D MONITOR_SPEED=250000 -D HARDWARE_REVISION`.
- [ ] `firestarter/.github/workflows/build.yml` — a `pio test -e native_nodevtools` step.
- [ ] `firestarter/test/native/avr/_shared/sdp_expected.h` — `SDP_FIXED_LOCK_{DIP28_28C256, DIP28_28C64, DIP24_2816, DIP32_28C512_EEPROM}` (4 goldens, dump-authored). **The whole-file blob SHA must change (D-10)** — 117/118's identity shorthand no longer applies; use per-array byte-identity instead.
- [ ] `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` — upgrade the `micros()` mock from a 2-slot parity alternator to a scripted queue, then **re-verify cases 11 and 12**.
- [ ] `firestarter_app/tools/check_is_memory_cmd_no_ifdef.py` + `tests/test_check_is_memory_cmd_no_ifdef.py` + `tests/fixtures/planted_ifdef_in_predicate.h` — the D-04 gate, its paired pytest, and its planted-violation fixture.
- [ ] `firestarter_app/tools/check_no_log_in_sdp_window.py` — append the new emit anchor; repair `tests/test_check_no_log_in_sdp_window.py` and `tests/fixtures/planted_log_in_window.cpp`. **This gate fails closed if D-14's shared bracket helper moves the emit call out of `eeprom28c_write_init`** — the exact cross-repo pattern that bit Phase 117 four times.
- [ ] `.planning/phases/119-…/119-MEASUREMENT.md` and `119-NONREGRESSION.md` — mirror `118-MEASUREMENT.md` §1/§6 and `118-NONREGRESSION.md` §4.
- [x] **BLOCKING decision — PLACED:** Open Question 1 — F-F option (a) (widen `[env:native]` `build_src_filter` with `+<operation_utils.cpp>`, verifying all 16 suites for ArduinoFake aborts) vs option (b) (`static inline` helper in `operation_utils.h`). Determines whether LOCK-04's and DEVTEST-01's proofs are tests or prose. **Planned as Task 1 of `119-07-PLAN.md`** — a bounded spike-then-commit with an explicit fallback to (b), ahead of every dependent proof.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Worst-case per-byte page-load interval, reported once per write | D-16 | Timing under real silicon load; the native `micros()` mock cannot produce true bus timing | `firestarter write <chip> -b --force` on each of the 3 attached boards (`/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0`); confirm `controller:` identity per port first |
| Per-board flash figures cross-checked against a real board | D-18 / LOCK-06 | The `pio run` build is CI-able; the *board identity* line is not | Attach each board, confirm `controller:` identity, record alongside the build figures |
| The lock operation's own hardware duration | D-17 | **Unreachable until Phase 120's `dev sdp` CLI exists** — no host command can issue a standalone lock in this phase | Deferred to Phase 120 by design; do not attempt |

> ⚠ Hardware verifications are **flagged, never rubber-stamped**. Bench work in this milestone is Leonardo-class; a hardware step that cannot be run must be recorded as skipped-with-reason.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies — verified by gsd-plan-checker across all 11 plans
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references — every ❌/⚠ row above is owned by a named plan
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [x] Open Question 1 (F-F option a/b) placed as `119-07` Task 1, ahead of every dependent proof
- [x] `nyquist_compliant: true` set in frontmatter
- [ ] `wave_0_complete: true` — flips when 119-02 / 119-03 / 119-05 land during execution

**Approval:** approved 2026-07-28 (plan-checker: VERIFICATION PASSED, 0 blockers)
