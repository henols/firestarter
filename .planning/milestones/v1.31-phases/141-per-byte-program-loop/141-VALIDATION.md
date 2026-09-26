---
phase: 141
slug: per-byte-program-loop
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-10
---

# Phase 141 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `141-RESEARCH.md` §"Validation Architecture" (lines 2095-2161).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Unity via PlatformIO `test_framework = unity` (+ ArduinoFake `^0.4.0` for mocks) for firmware behaviour; pytest 9.1.1 against `firestarter/tests/` for source-scan gates |
| **Config file** | `firestarter/platformio.ini` (six envs after this phase). `firestarter/tests/` has **no `conftest.py`** anywhere — a recorded house-rule, not an omission |
| **Quick run command** | `cd /workspaces/firestarter && python3 -m pytest tests/ -q -o addopts="" && pio test -e <sixth_env>` |
| **Full suite command** | `cd /workspaces/firestarter && pio test -e native && pio test -e native_nodevtools && pio test -e <sixth_env> && python3 -m pytest tests/ -q -o addopts="" && pio run` |
| **Estimated runtime** | ~11 s (pytest) + ~60-90 s (native envs) + ~90 s (three AVR builds) |

**Two environment traps that make a verify leg unrunnable if ignored:**

1. `pio` **crashes** with cwd `/workspaces` — the gitignored root `platformio.ini` carries two
   `[platformio]` sections, and `pio -d <dir>` does not work around it. Every leg must
   `cd /workspaces/firestarter && pio …`.
2. That `&&` must reach disk as two literal ampersands. This project has a recorded prior failure
   where a planner wrote `&amp;&amp;` into `<automated>` blocks, rendering 30/37 legs unrunnable while
   self-reporting `bash -n` PASS. **Verify the bytes on disk after writing plans.**
3. `node` is not on the bare `PATH`.
4. Always pass `-o addopts=""` — `addopts` is already `-ra -q`, and doubling `-q` suppresses the
   count line.

---

## Sampling Rate

- **After every task commit:** `cd /workspaces/firestarter && python3 -m pytest tests/ -q -o addopts=""` (~11 s) plus `pio test -e <sixth_env>`
- **After every plan wave:** the full suite command above, including `pio run` for all three AVR targets
- **Before `/gsd-verify-work`:** full suite green **except** the one expected RED below
- **Max feedback latency:** ~11 s (pytest leg), ~90 s (native leg)

**Phase gate — the exact green/red shape:**

| Check | Expected |
|-------|----------|
| `native` / `native_nodevtools` | green at **exactly 141 cases / 17 suites** each (pinned by live `size_baseline.json`) |
| `pytest tests/` | fully green, with the **re-derived** D-13 golden |
| `<sixth_env>` | green, run **by name** (in no CI leg of either repo) |
| `check_size_baseline.py --policy merge05` | green |
| `native_trace_v131` | **RED, and recorded as such** — the one expected non-green (D-10) |

The `native_trace_v131` RED must be named explicitly in the phase record so `/gsd-verify-work` does
not read it as a regression.

---

## Per-Task Verification Map

Task IDs are assigned by the planner; the requirement→leg mapping below is fixed and every task
must inherit the leg for the requirement it claims.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD-at-plan | TBD | TBD | LOOP-01 | — | fixed pulse width, verify per pulse, per-byte count | unit (native) | `cd /workspaces/firestarter && pio test -e <sixth_env> -f "*<suite>*"` | ❌ W0 | ⬜ pending |
| TBD-at-plan | TBD | TBD | LOOP-02 | — | four named constructs absent from the write path | gate (source scan) + D-13 inventory shrinkage | `cd /workspaces/firestarter && python3 -m pytest tests/test_protocol_branch_inventory.py -q -o addopts=""` | ⚠️ D-13 gate exists; **LOOP-02 absence assertion does NOT** → W0 | ⬜ pending |
| TBD-at-plan | TBD | TBD | LOOP-03 | — | overprogram duration + clamp + 32-bit overflow safety (pure fn per D-08) | unit (native) | `cd /workspaces/firestarter && pio test -e <sixth_env> -f "*<suite>*"` | ❌ W0 | ⬜ pending |
| TBD-at-plan | TBD | TBD | LOOP-04 | T-141-V5 | `0x0B` energy cap: exactly 100/50/250 pulses at 500/1000/200 µs, no overprogram | unit (native) | `cd /workspaces/firestarter && pio test -e <sixth_env> -f "*<suite>*"` | ❌ W0 | ⬜ pending |
| TBD-at-plan | TBD | TBD | LOOP-05 | T-141-HV | abort + route disable + `(address, pulses)` reported; scoped to `_main`'s own CONTROL strobes | unit (native) | `cd /workspaces/firestarter && pio test -e <sixth_env> -f "*<suite>*"` | ❌ W0 | ⬜ pending |
| TBD-at-plan | TBD | TBD | LOOP-06 | — | `0xFF` and already-matching bytes emit **zero** pulses | unit (native) | `cd /workspaces/firestarter && pio test -e <sixth_env> -f "*<suite>*"` | ❌ W0 | ⬜ pending |
| TBD-at-plan | TBD | TBD | LOOP-07 | T-141-TRUNC | **global**: no recorded `delayMicroseconds` argument > 16383 | unit (native, `HOST_STUBS_RECORD_TIMING`) **+** source-scan gate for both sites | `cd /workspaces/firestarter && pio test -e <sixth_env> -f "*<suite>*"` | ❌ W0 | ⬜ pending |
| TBD-at-plan | TBD | TBD | LOOP-08 | T-141-HV | route asserted once per block, present in every per-byte CONTROL write, survives A16 crossing on `pins >= 32` | unit (native, strobe recorder) | `cd /workspaces/firestarter && pio test -e <sixth_env> -f "*<suite>*"` | ❌ W0 | ⬜ pending |
| TBD-at-plan | TBD | TBD | — (regression) | — | shipped table values unchanged | existing | `cd /workspaces/firestarter && python3 -m pytest tests/test_eprom_params_citations.py -q -o addopts=""` | ✅ | ⬜ pending |
| TBD-at-plan | TBD | TBD | — (regression) | — | frozen fixture untouched | existing | `cd /workspaces/firestarter && python3 -m pytest tests/test_golden_trace_identity_eprom_v131.py -q -o addopts=""` | ✅ | ⬜ pending |
| TBD-at-plan | TBD | TBD | — (regression) | — | no new `src/` TU left unmanifested | existing | `cd /workspaces/firestarter && python3 -m pytest tests/test_check_cmake_manifest.py -q -o addopts=""` | ✅ | ⬜ pending |
| TBD-at-plan | TBD | TBD | — (budget) | — | flash/RAM inside MERGE-05's band | existing checker | `cd /workspaces/firestarter && python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log uno=<log> --avr-log uno328pb=<log> --avr-log leonardo=<log>` | ✅ | ⬜ pending |
| TBD-at-plan | TBD | TBD | — (budget) | — | native warning watermark held | existing checker | `cd /workspaces/firestarter && python3 scripts/check_build_warnings.py …` — **never with the sixth env name** | ✅ | ⬜ pending |
| TBD-at-plan | TBD | TBD | — (tri-repo) | — | catalog synced + regenerated in both sub-repos | script + diff | `bash /workspaces/tools/catalog/sync_to_subrepos.sh` then `git -C /workspaces/firestarter diff --stat -- include/messages.h tools/catalog/messages.toml` | ✅ script | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**Measured flash budget (this branch, not the drifted `beta` tip):** 42 B (`uno`) / 36 B
(`uno328pb`) / 56 B (`leonardo`); RAM delta must be **exactly 0**. Binding constraint is
`uno328pb` at 36 B. F-138-02's 8 B / 2 B figure is an `origin/beta`-tip measurement and does
**not** apply — non-ancestry verified with `git merge-base --is-ancestor 6fab4ea HEAD` → NO.

---

## Wave 0 Requirements

- [ ] `test/native/avr/<new_suite>/<new_suite>.cpp` — covers LOOP-01, LOOP-03, LOOP-04, LOOP-05, LOOP-06, LOOP-07, LOOP-08
- [ ] `test/native/avr/<new_suite>/host_stubs.cpp` — `HOST_STUBS_REAL_REGISTER_UTILS` + `HOST_STUBS_RECORD_TIMING` + `HOST_STUBS_CUSTOM_READ_DATA_BUFFER`, plus a `converge_after` read-back model and `reset_register_cache`
- [ ] `platformio.ini` — the **sixth** `[env:native_*_v131]` with its HARD CONSTRAINT comment block, copied from `[env:native_params_v131]`. Names only its own suite in `test_filter`; never in `default_envs`; never passed to `check_size_baseline.py` (unknown env → uncaught `KeyError`, exit 1) or `check_build_warnings.py` (exit 2)
- [ ] **A LOOP-02 absence assertion** — the D-13 inventory proves the *shape* moved, not that the four named constructs are gone. A source-scan gate (`NUMBER_OF_RETRIES`, `program_mismatched_bytes`, `verify_and_update_mask`, the growth expression, all absent from `src/proms/eprom.cpp`) closes LOOP-02's own wording. Follow `test_protocol_branch_inventory.py`'s standalone-module conventions: live re-parse, non-vacuity guard, fail-closed on a missing target, no `pytest.skip`
- [ ] **A LOOP-07 source-scan leg** — the native test proves no *executed* path exceeds the ceiling; a grep-class gate asserting both former sites now call the helper closes the "global" wording
- [ ] Re-derived `tests/golden/protocol_branch_inventory.json` **and** the edited `:446` literal — the golden alone is insufficient: `test_protocol_branch_inventory.py:446` hard-codes `protocol_lines == [71, 145, 218]` in the **test module**, and no re-derivation script exists (`_extract_predicates` lives only inside the test module)
- [ ] The committed new-trace artifact (via `-D EPROM_V131_TRACE_DUMP`, binary run directly)
- **Framework install:** none — every dependency is already resolved

---

## Manual-Only Verifications

*None.* Bench proof on real silicon is BENCH-01…03, **Phase 145**, and is explicitly not a
Phase 141 verification.

---

## D-15 Discipline (applies to every new leg)

Plant the violation, watch it go RED **for the reason it was planted**, capture the transcript,
then fix **the locator rather than the assertion**. Phase 140 recorded 12 planted-RED runs across
three gates; match that standard.

Two recorded traps for planted-RED work in this repo:

- A pre-authored gate leg can be **unreachable** — RED proves nothing until the leg is seen to
  pass for the right reason.
- An "empty git diff" / byte-identical criterion breaks on later `#if` guards. Scope such criteria
  to *assertions-unchanged*, or name blob SHAs.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 90s
- [ ] Every `<automated>` block's `&&` verified as two literal ampersands **on disk**
- [ ] `native_trace_v131` RED named explicitly in the phase record (expected, not a regression)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
