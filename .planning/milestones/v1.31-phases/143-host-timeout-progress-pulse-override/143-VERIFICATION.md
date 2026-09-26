---
phase: 143-host-timeout-progress-pulse-override
verified: 2026-08-13T10:00:00Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
---

# Phase 143: Host Timeout, Progress & Pulse Override Verification Report

**Phase Goal:** A host-initiated write survives the new, longer worst-case block times without lying to
the user about progress or failure, and a tester can override the database pulse for a single run.
**Verified:** 2026-08-13T10:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth (ROADMAP Success Criterion) | Status | Evidence |
|---|---|---|---|
| 1 | A write whose block takes longer than the previous 10 s `DEFAULT_RESPONSE_TIMEOUT` completes without the host raising a serial timeout | VERIFIED | `firestarter_app/firestarter/eprom_operations.py` `EpromOperator._write_block_timeout()` (line ~444) returns the firmware-advertised `write_block_budget_s` verbatim, clamped `[1, WRITE_BUDGET_MAX_S]`, else `WRITE_BLOCK_TIMEOUT_FALLBACK_S = 120.0`. `write_eprom` passes `response_timeout=self._write_block_timeout()` into `_run_state_machine` (line ~1923), which forwards it to `_main_phase_send_data`'s `timeout` used in `self.comm.get_response(timeout)`. Confirmed by direct code read (not just SUMMARY claim) and by re-running `tests/test_write_response_budget.py` (6/6 pass) independently. Firmware side: `eprom_block_budget_s()` (`firestarter/src/proms/eprom_budget.cpp`) computes the padded budget and `firestarter/src/firestarter.cpp`'s `init_programmer_framed` packs it onto `MSG_OK_READY` at the computed offset `4 + _vlen`; host decodes it in `serial_comm.py`'s CAP-03 arm at the computed `ver_end` (confirmed by direct grep/read). `verify_eprom` (line ~2010) omits `response_timeout`, confirming non-write paths keep the 10 s default (D-12) — read directly, not merely asserted. |
| 2 | The user sees ongoing progress during a long write instead of a silent stall | VERIFIED | Firmware: `firestarter/src/proms/eprom.cpp` emits a time-gated `MSG_DATA_PROGRESS` (0xE0) inside `eprom_internal_write_execute_body`'s per-byte loop, guarded `#ifndef SERIAL_ON_IO` (confirmed by direct grep: lines 326-401). Host: `eprom_operations.py`'s `_main_phase_send_data` has a `DATA` arm (confirmed by direct read, lines ~810-838) that calls `_apply_write_progress` and never acks, positioning the bar at `absolute - start_addr` and latching `firmware_drives_bar` so the chunk-handoff `update()` cannot rewind. Scope is explicitly `leonardo`/native only — compiled out on `uno`/`uno328pb` via the same `#ifndef SERIAL_ON_IO` guard, mechanically pinned by `tests/test_progress_emission_is_leonardo_only.py` (10 legs, independently re-run this session: 10 passed). This narrower-than-literal scope is a documented, deliberate mitigation (BF-2) for a real hazard (Uno's 4-slot deferred-log buffer would silently drop a subsequent `MSG_ERR_MAX_PULSES` frame) — not a gap. No bench/hardware claim of real bar motion is made anywhere in the record; that is explicitly deferred to Phase 145. |
| 3 | A byte that fails at `max_pulses` on the firmware side surfaces to the user as a program failure naming the address, not as a transport-level error | VERIFIED | Two-part fix, both independently confirmed: (a) HOST-01's timeout fix (above) stops the 10 s transport timeout from firing before the firmware's `MSG_ERR_MAX_PULSES`/`MSG_ERR_ENERGY_CAP` frame can arrive; (b) `eprom_operations.py`'s `_budget_failure_hint_message` (confirmed present at line 218, keyed on `_BUDGET_FAILURE_IDS = (0xBD, 0xBE, 0xAE)`) composes a disposition hint into the `ERROR` branch alongside `_boot_block_hint_message`, and `_raise_for_error_response` raises `EpromOperationError` (not the `0xBB` `ProtocolNotImplementedError` fork) carrying the address. Independently re-ran `tests/test_budget_failure_render.py` (4/4 pass) confirming the exact-type assertion (`type(exc) is EpromOperationError`) and the address-naming behavior. |
| 4 | `firestarter write --pulse-us N` overrides the database-supplied pulse for that run using the existing wire field, with no new command or wire field introduced | VERIFIED | `firestarter_app/firestarter/cli_handlers.py` has exactly one `--pulse-us` option (`click.IntRange(1, 65535)`, `default=None`) on `write` only (confirmed by grep: `write --help` on the real installed CLI shows the option and its TRAP #7 docstring). `write_eprom`'s `pulse_us` parameter rebinds `eprom_data_dict` to a shallow copy and sets `["pulse-delay"] = pulse_us` (confirmed by direct read, lines 1869-1894) — the existing wire key, no new key. Grep of `cli_handlers.py`/`serial_comm.py`/`messages.py`/`constants.py` confirms no new wire field or command was added. Independently re-ran `tests/test_pulse_us_override.py` (10/10 pass). |
| 5 | Supplying `--pulse-us` outside `1..65535` is refused with an actionable message before any serial byte is sent | VERIFIED | Live-tested directly against the real installed CLI (not merely asserted from a SUMMARY): `firestarter write DUMMYCHIP dummy.bin --pulse-us 0` → exit 2, `"0 is not in the range 1<=x<=65535"`; `--pulse-us 65536` → exit 2, actionable range message; `--pulse-us abc` → exit 2, `"'abc' is not a valid integer range"`. No serial-port error appears in any case (Click's `IntRange` refuses at parse time, before `write()`'s body — and therefore before `find_and_connect` — ever runs). `tests/test_pulse_us_override.py::test_refusal_opens_no_port` independently re-run and passing. |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter/include/eprom_budget.h`, `firestarter/src/proms/eprom_budget.cpp` | BF-3-corrected budget arithmetic, new unpinned TU | VERIFIED | Read in full; ceil pulse count, UNCAPPED zero-cap guard, overprogram term delegated to shipped `eprom_overprogram_us`, divide-before-multiply seconds conversion, ×2+2 padding — all present exactly as specified, no `Arduino.h`/`avr/pgmspace.h`. |
| `firestarter/src/firestarter.cpp` (`init_programmer_framed`) | CAP-02 ported + CAP-03 appended in one pack block | VERIFIED | `_ready[4+32+2]` buffer, budget written at computed `4 + _vlen` offset, `LOG_OK_ID_BYTES` emits `(4 + _vlen + 2)` bytes, `eprom_block_budget_s()` called (not restated). |
| `firestarter/src/proms/eprom.cpp` | Time-gated `MSG_DATA_PROGRESS` emission, `#ifndef SERIAL_ON_IO`-guarded | VERIFIED | Confirmed at lines 322-401; both the emit and its `last_emit_ms` state variable are independently guarded. |
| `firestarter/tests/test_ack_layout_source_contract_v143.py` | 10-leg source-contract gate pinning ack layout | VERIFIED | File exists (28442 bytes); independently re-run: 10 passed. |
| `firestarter/tests/test_progress_emission_is_leonardo_only.py` | 10-leg source-contract gate pinning progress emission scope | VERIFIED | File exists (39248 bytes); independently re-run: 10 passed. |
| `firestarter_app/firestarter/serial_comm.py` | CAP-03 decode arm, `WRITE_BUDGET_MAX_S`, `write_block_budget_s` | VERIFIED | Confirmed via grep: constant, class-level + `__init__` attribute, decode arm at computed `ver_end`, all present. Ring-fence (`_read_and_parse_lines`) untouched (git history shows only 143-02's targeted commit). |
| `firestarter_app/firestarter/eprom_operations.py` | `_write_block_timeout`, `_apply_write_progress`, `_budget_failure_hint_message`, `pulse_us` param | VERIFIED | All four present and wired (see Observable Truths 1-4 evidence above); read directly, function bodies match documented behavior. |
| `firestarter_app/firestarter/cli_handlers.py` | `--pulse-us` option on `write` only | VERIFIED | Confirmed via grep and live `write --help` / live CLI invocation. |
| `firestarter_app/tests/{test_write_response_budget,test_write_progress,test_pulse_us_override,test_budget_failure_render}.py` | New host test modules | VERIFIED | All four files exist; independently re-run together with `test_hw_revision_gate.py`/`test_fwguard.py`: 58 passed. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `write_eprom` | `_write_block_timeout()` | `response_timeout=self._write_block_timeout()` kwarg into `_run_state_machine` → `_main_phase_send_data` | WIRED | Confirmed by direct code read at the call site (line ~1923) and by the docstring/comment explaining exactly why it must be read inside the `with` block. |
| `_main_phase_send_data` DATA branch | `_apply_write_progress` | direct call, latching `firmware_drives_bar` | WIRED | Confirmed by direct code read (lines ~810-838); never acks, never routes through `_handle_progress_response`. |
| `_main_phase_send_data` ERROR branch | `_budget_failure_hint_message` | composed via `" -- "` join alongside `_boot_block_hint_message` | WIRED | Confirmed by direct code read; both hints computed unconditionally and joined in a loop. |
| CLI `--pulse-us` | `write_eprom(pulse_us=...)` | `pulse_us=pulse_us or 0` | WIRED | Confirmed by grep at `cli_handlers.py:797`. |
| `write_eprom`'s `pulse_us` | wire frame | `eprom_data_dict["pulse-delay"] = pulse_us` on a shallow copy | WIRED | Confirmed by direct read (lines 1869-1894); existing wire key, no new key added. |
| Firmware `eprom_block_budget_s()` | `MSG_OK_READY` ack | called at the pack site in `init_programmer_framed` | WIRED | Confirmed by direct read of `firestarter.cpp` line ~204. |
| Host CAP-03 decode | `write_block_budget_s` attribute | `struct.unpack(">H", params_bytes[ver_end:ver_end+2])` at computed offset, clamped | WIRED | Confirmed by grep of `serial_comm.py`; matches firmware's byte layout exactly (both sides independently pinned; no standing cross-repo parity gate yet — correctly handed off to Phase 144/TEST-07, not claimed here). |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| `--pulse-us 0` refused at parse time | `firestarter write DUMMYCHIP dummy.bin --pulse-us 0` | Exit 2, `"0 is not in the range 1<=x<=65535"`, no port-related error | PASS |
| `--pulse-us 65536` refused at parse time | `firestarter write DUMMYCHIP dummy.bin --pulse-us 65536` | Exit 2, actionable range message | PASS |
| `--pulse-us abc` refused at parse time | `firestarter write DUMMYCHIP dummy.bin --pulse-us abc` | Exit 2, `"'abc' is not a valid integer range"` | PASS |
| `write --help` shows `--pulse-us` and TRAP #7 docstring | `firestarter write --help` | Option and full HOST-04/05 docstring paragraph present | PASS |
| `verify_eprom` omits `response_timeout` (D-12 negative proof) | direct source read | No `response_timeout` kwarg passed; defaults to `DEFAULT_RESPONSE_TIMEOUT=10` | PASS |
| New host test modules pass standalone | `pytest tests/test_write_response_budget.py tests/test_write_progress.py tests/test_pulse_us_override.py tests/test_budget_failure_render.py tests/test_hw_revision_gate.py tests/test_fwguard.py` | 58 passed | PASS |
| New firmware gate modules pass standalone | `pytest tests/test_ack_layout_source_contract_v143.py tests/test_progress_emission_is_leonardo_only.py` | 20 passed | PASS |
| Full host suite (independent re-run, not copied from orchestrator) | `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` | 1578 passed, 30 snapshots passed | PASS |

### Probe Execution

Not applicable — this phase declares no `scripts/*/tests/probe-*.sh` probes; verification uses pytest/PlatformIO test suites and direct CLI invocation instead (all executed above, not merely narrated).

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| HOST-01 | 143-01, 143-02, 143-03, 143-04 | Write survives a block exceeding the old 10 s timeout | SATISFIED | Firmware budget arithmetic + wire advertisement + host decode + host timeout threading, all independently confirmed present and wired. |
| HOST-02 | 143-05, 143-06, 143-08 | User sees ongoing progress during a long write | SATISFIED | Firmware emission (leonardo/native only, by design) + host render, both confirmed; non-claim (leonardo-only, EPROM-path-only) explicitly and correctly stated in `firestarter/CLAUDE.md` and the phase record, not hidden. |
| HOST-03 | 143-04, 143-09 | `max_pulses` failure surfaces as a named program failure, not a transport error | SATISFIED | Both halves (timeout fix + render/hint) confirmed present and wired; correctly documented as split across two plans, neither alone sufficient. |
| HOST-04 | 143-04, 143-07 | `--pulse-us N` overrides DB pulse via existing wire field | SATISFIED | Transport half (143-04) + CLI half (143-07) both confirmed present and wired; correctly documented as split. |
| HOST-05 | 143-07 | Out-of-range `--pulse-us` refused with actionable message before any serial byte | SATISFIED | Live-tested directly against the installed CLI; confirmed exit 2, actionable messages, no port opened. |

All five requirement IDs declared across the phase's plans (via `143-HOST-RECORD.md`'s evidence table, since plans 143-01..09 deliberately carry `requirements: []` by design, centralizing the flip in 143-10) are accounted for in `REQUIREMENTS.md`. Cross-referenced: `REQUIREMENTS.md` maps exactly these five IDs to Phase 143 (grep confirms no orphaned Phase-143 requirement exists beyond HOST-01..05). All five are marked `[x]` / `Complete` in both the checkbox list and the coverage table, confirmed by direct read.

### Anti-Patterns Found

None. Scanned all newly-created and newly-modified files in both repos for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` and placeholder-return patterns (`return null`, empty `{}`/`[]` stubs, `console.log`-only bodies) — zero matches. The extensive self-documented "non-claims" throughout `143-HOST-RECORD.md` and `firestarter/CLAUDE.md` (leonardo-only progress delivery, no bench evidence, "not faster, not more reliable") are honest scope disclosures, not code smells, and are consistent with what the actual code does.

### Human Verification Required

None. All five ROADMAP success criteria are independently verifiable in software (call-argument oracles, byte-layout oracles, source-contract gates, and — for HOST-04/HOST-05 — direct live CLI invocation against the real installed package). The phase record is explicit and correct that real bar motion on physical hardware and per-pulse-overhead measurement are Phase 145's responsibility, not this phase's — that is a documented scope boundary, not an unverified claim this phase makes about itself.

### Gaps Summary

No gaps found. Every ROADMAP success criterion resolves to VERIFIED against direct codebase evidence (not SUMMARY narration): file contents were read in full for the arithmetic, the ack pack block, the progress emission, the host timeout threading, the progress render, the budget-failure hint, and the CLI option; the new test files were independently re-executed (not copied from the SUMMARYs) and passed; and HOST-04/HOST-05 were additionally confirmed by directly invoking the real installed `firestarter write` CLI with out-of-range and non-integer `--pulse-us` values, observing exit code 2 and actionable messages with no serial-port interaction.

Three deliberate, well-documented deviations were checked against the record and found to be intentional, disclosed engineering decisions rather than gaps:
- **HOST-02's progress delivery is leonardo/native-only** (BF-2, D-06 second dimension) — a documented mitigation for a real Uno-class buffer-overflow hazard that would otherwise regress HOST-03. Stated plainly in `firestarter/CLAUDE.md` and `143-HOST-RECORD.md`, not hidden.
- **No bench/hardware evidence exists or is claimed** — explicitly deferred to Phase 145, named as such throughout.
- **`check_size_baseline.py` and `native_trace_v131` remain RED**, both with fully attributed, previously operator-accepted reasons (MERGE-05/OD-2 drift, D-24) — re-measured this session and confirmed unchanged, not newly introduced by this phase.

REQUIREMENTS.md correctly shows all five `HOST-*` requirements as `Complete`; ROADMAP.md's requirement-coverage table still shows `Pending` for Phase 143, which is expected and correct at this point in the workflow (the `phase.complete` step writes it after verification, not before) — this is not a gap.

---

_Verified: 2026-08-13T10:00:00Z_
_Verifier: Claude (gsd-verifier)_
