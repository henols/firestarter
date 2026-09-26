---
phase: 06-logging-infrastructure
plan: 04
subsystem: host

tags: [host, fw-guard, lockstep, pytest, lfw-05, lhost-04, dev-escape-hatch, refuse-before-accept]

# Dependency graph
requires:
  - 06-01 (catalog + codegen produced firestarter_app/firestarter/messages.py — host import surface)
  - 06-03 (rewrote serial_comm.py: byte-stream reader, FirmwareOutdatedError already exposed, pytest infra + fixtures in place)
provides:
  - host-side `major < 3` refuse guard in `SerialCommunicator._probe_port` with locked operator-facing wording
  - `FIRESTARTER_DEV_ALLOW_PRE_V12=1` environment-variable escape hatch (developer-only; documented for bench scripts during Phases 7-8)
  - explicit `except FirmwareOutdatedError: raise` clause in `FirmwareManager.check_current_firmware` (placed BEFORE the broad `except (ProgrammerNotFoundError, SerialError)`) — resolves the PATTERNS open question with **re-raise**
  - `firestarter_app/tests/test_fwguard.py` with 4 acceptance tests (refuse / accept / escape-hatch / malformed-version)
affects: [07-call-site-conversion, 08-call-site-conversion, 09-firmware-version-bump]

# Tech tracking
tech-stack:
  added: []   # no new deps; reuses pytest (Plan 03) + unittest.mock (stdlib)
  patterns:
    - "Refuse-before-accept: pre-v3 major-version guard fires BEFORE the existing v2.0.0 floor check (defence-in-depth retained)"
    - "Specific-before-broad except ordering: FirmwareOutdatedError re-raise sits ABOVE (ProgrammerNotFoundError, SerialError) catch so the inherited SerialError clause cannot swallow it"
    - "Autouse class fixture for env-var hermeticity: monkeypatch.delenv('FIRESTARTER_DEV_ALLOW_PRE_V12') at every test entry, so shell environment cannot taint the strict-path tests"
    - "patch.object stack + lambda __init__ short-circuit for hardware-free unit testing of _probe_port"

key-files:
  created:
    - firestarter_app/tests/test_fwguard.py
  modified:
    - firestarter_app/firestarter/serial_comm.py (added `import os`; inserted 21-line pre-v3 refuse-guard block in `_probe_port`)
    - firestarter_app/firestarter/firmware.py (added `FirmwareOutdatedError` to imports; inserted 2-line `except FirmwareOutdatedError: raise` clause in `check_current_firmware`)

key-decisions:
  - "PATTERNS open question resolved with **re-raise**, not swallow. The pre-v1.2 message is operator-actionable; surfacing it directly to the CLI gives the user the upgrade command without forcing them to scroll back through log output."
  - "Major-version threshold is `< 3` (not `<= 2`). The firmware bumps directly from 2.0.11 to 3.0.0 in Phase 9 (PROJECT.md lockstep constraint); no 2.1.x or 2.2.x intermediate exists, so `major < 3` cleanly captures all pre-v1.2 firmware."
  - "Malformed version string falls back to `major = 0`, NOT `major = 999`. T-06-17 (Repudiation): a tampered/garbage version cannot evade the refuse by producing an unparseable number. `0 < 3` ⇒ refuse fires."
  - "Existing `_is_version_sufficient(current_version, '2.0.0')` floor check **retained** as defence-in-depth — does not double-trip on v3+ firmware (sufficient ≥ 2.0.0 is True), and acts as a backup if the major-version parse ever silently regresses."
  - "Escape-hatch env-var name is intentionally verbose (`FIRESTARTER_DEV_ALLOW_PRE_V12`) — long enough to make accidental shell-export unlikely; project-prefixed so it never collides with another tool's variable. T-06-16 mitigation: rely on naming pragma rather than a security boundary."
  - "Test pattern `test_malformed_version_defaults_to_refuse` uses the version string `x.x.x` (not `NOT_A_VERSION`). The existing `re.search(r'FW:\\s*([\\d.x]+)', msg)` regex in `_probe_port` accepts `x` literally (carried over from the 2.0.x-pre-release era) but `int('x')` raises ValueError — exercising the guard's `try/except (ValueError, IndexError)` path."
  - "Autouse `_clear_escape_hatch` fixture delenvs the var at every test entry; per-test `monkeypatch.setenv(...)` then re-sets it for the one test that wants the bypass. Pytest auto-restores afterwards. Net effect: the suite passes whether or not the developer has the env var set in their shell."

patterns-established:
  - "Refuse-before-accept guard pattern: a new failure check sits ABOVE an older floor check; both remain active. Useful when raising a hard error and the older check is informative but no longer authoritative."
  - "Specific-exception re-raise BEFORE inherited broad catch — applies any time a hierarchical exception (subclass inherits from caught parent) should not be swallowed by the parent's clause."
  - "Hermetic env-var testing via autouse delenv + per-test setenv — guarantees test outcome independent of shell context."

requirements-completed: [LFW-05, LHOST-04]

# Metrics
duration: ~6 min
completed: 2026-05-18
---

# Phase 6 Plan 04: Host Firmware-Version Refuse Guard Summary

**Wired the host-side `major < 3` refuse guard into `SerialCommunicator._probe_port` with the locked operator-facing wording, added the `FIRESTARTER_DEV_ALLOW_PRE_V12=1` escape hatch for bench scripts, and resolved the PATTERNS open question by adding an explicit `except FirmwareOutdatedError: raise` clause in `FirmwareManager.check_current_firmware` BEFORE the broad `(ProgrammerNotFoundError, SerialError)` catch. Four acceptance tests cover refuse / accept / escape-hatch / malformed-version paths and pass alongside Plan 03's 10 decoder tests (14 total).**

## Performance

- **Duration:** ~6 min (start `2026-05-18T~`, end `2026-05-18T~`)
- **Tasks:** 2/2 complete (each = submodule commit + meta-repo pointer-bump pair)
- **Files created:** 1 (`tests/test_fwguard.py`, 125 lines)
- **Files modified:** 2 (`serial_comm.py` +22 lines, `firmware.py` +3 lines)
- **Test result:** `pytest -q` → 14 passed in 0.25s (10 decoder + 4 fwguard)

## Accomplishments

- **Pre-v3 refuse guard in `_probe_port`** (`firestarter_app/firestarter/serial_comm.py`):
  - `import os` added at module top.
  - Inserted a 21-line block immediately after `current_version = match.group(1).strip()` and BEFORE the existing `_is_version_sufficient(current_version, "2.0.0")` floor check.
  - Logic:
    1. Parse `major = int(current_version.split(".")[0])` inside `try/except (ValueError, IndexError)` → falls back to `major = 0` on any parse error.
    2. If `major < 3` AND `os.environ.get("FIRESTARTER_DEV_ALLOW_PRE_V12") != "1"` → raise `FirmwareOutdatedError` with the locked message.
    3. Otherwise fall through to the existing v2.0.0 floor check (defence-in-depth retained).
  - Locked message body:
    > `Firmware version {current_version} is pre-v1.2 (text-format logging). This host expects v1.2+ firmware emitting ID-encoded log frames. Please upgrade the firmware to v3.0.0 or later using 'firestarter fw --install'. (No fallback to text-format protocol — the host and firmware must be upgraded together; see PROJECT.md "Constraints".)`
- **Explicit re-raise in `check_current_firmware`** (`firestarter_app/firestarter/firmware.py`):
  - `FirmwareOutdatedError` added to the import group from `firestarter.serial_comm`.
  - Inserted `except FirmwareOutdatedError: raise` clause BEFORE the broad `except (ProgrammerNotFoundError, SerialError)` clause. Source order verified: line 92 `except FirmwareOutdatedError:` precedes line 94 `except (ProgrammerNotFoundError, SerialError)`.
  - Since `FirmwareOutdatedError` inherits from `SerialError`, the broad catch WOULD have swallowed it; the new explicit clause makes the refuse error visible to the CLI surface.
- **Acceptance suite** (`firestarter_app/tests/test_fwguard.py`):
  - `class TestFirmwareVersionGuard` with autouse `_clear_escape_hatch(monkeypatch)` fixture that `delenv`s `FIRESTARTER_DEV_ALLOW_PRE_V12` at every test entry.
  - 4 test methods, each short-circuiting the serial connection via 5 stacked `patch.object` contexts (`expect_ack`, `send_json_command`, `consume_remaining_input`, `disconnect`, `__init__` → no-op lambda).
  - Tests:

| # | Test                                              | Path        | What it proves                                                                                                                |
| - | ------------------------------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------- |
| 1 | `test_refuse_pre_v3_firmware`                     | refuse      | `FW: 2.0.11, ...` → raises `FirmwareOutdatedError`; message contains `2.0.11`, `firestarter fw --install`, `v3.0.0 or later`. |
| 2 | `test_accept_v3_firmware`                         | accept      | `FW: 3.0.0, ...` → does NOT raise.                                                                                            |
| 3 | `test_dev_escape_hatch_env_var`                   | escape      | `FIRESTARTER_DEV_ALLOW_PRE_V12=1` + `FW: 2.0.11, ...` → does NOT raise (bypass).                                              |
| 4 | `test_malformed_version_defaults_to_refuse`       | malformed   | `FW: x.x.x, ...` → `int('x')` raises ValueError → `major=0` → refuse fires (T-06-17).                                         |

## Verification Commands

```bash
# Locked wording present
cd firestarter_app
grep -n "FIRESTARTER_DEV_ALLOW_PRE_V12" firestarter/serial_comm.py        # => 2 hits
grep -n "pre-v1.2 (text-format logging)" firestarter/serial_comm.py       # => 1 hit
grep -n "v3.0.0 or later" firestarter/serial_comm.py                      # => 1 hit
grep -n "firestarter fw --install" firestarter/serial_comm.py             # => multiple (locked phrase + legacy v2.0.0 catch)
grep -n "major < 3" firestarter/serial_comm.py                            # => 1 hit
grep -n "^import os" firestarter/serial_comm.py                           # => line 10

# v2.0.0 floor check retained (defence-in-depth)
grep -c '_is_version_sufficient' firestarter/serial_comm.py               # => 2 (method def + use site)

# Explicit re-raise in firmware.py BEFORE broad catch
grep -n "except " firestarter/firmware.py | head -3
# 92:        except FirmwareOutdatedError:
# 94:        except (ProgrammerNotFoundError, SerialError) as e:

# Inheritance preserved
python3 -c "from firestarter.serial_comm import FirmwareOutdatedError, SerialError; assert issubclass(FirmwareOutdatedError, SerialError); print('OK')"
# => OK

# All 4 fwguard tests pass
pytest tests/test_fwguard.py -v                                           # => 4 passed
# All 14 tests pass (10 decoder + 4 fwguard)
pytest tests/ -v                                                          # => 14 passed in 0.25s

# Developer-shell sanity: parent env var set does NOT taint the strict-path tests
FIRESTARTER_DEV_ALLOW_PRE_V12=1 pytest tests/test_fwguard.py -v           # => 4 passed (autouse delenv works)

# Test-method names present
grep -cE 'def test_(refuse_pre_v3_firmware|accept_v3_firmware|dev_escape_hatch_env_var|malformed_version_defaults_to_refuse)' tests/test_fwguard.py
# => 4
```

All pass.

## Task Commits

Each task = submodule commit + meta-repo pointer bump.

### Task 1 — Insert refuse guard + escape hatch + explicit re-raise

1. **firestarter_app:** `8ed7036` (feat) — `serial_comm.py` adds `import os` + 21-line pre-v3 refuse guard (with locked wording + escape hatch + ValueError fallback). `firmware.py` adds `FirmwareOutdatedError` to imports and inserts `except FirmwareOutdatedError: raise` BEFORE the broad catch.
2. **meta-repo:** `6d20c38` (chore) — bump firestarter_app pointer.

### Task 2 — pytest acceptance suite for LFW-05 + LHOST-04 (4 paths)

3. **firestarter_app:** `08f906d` (test) — `tests/test_fwguard.py` (125 lines, 4 tests + autouse env-var-cleanup fixture).
4. **meta-repo:** `ceaae4b` (chore) — bump firestarter_app pointer.

**Plan metadata commit** (this SUMMARY.md + STATE.md + ROADMAP.md + REQUIREMENTS.md): added at end-of-plan via final commit below.

## Files Created / Modified

### firestarter_app submodule — created

- `tests/test_fwguard.py` — `class TestFirmwareVersionGuard` with 4 tests + autouse env-var-cleanup fixture; 125 lines.

### firestarter_app submodule — modified

- `firestarter/serial_comm.py` — 22 insertions:
  - Line 10: `import os` (new).
  - Lines 647-666 (inside `_probe_port`): 21-line guard block — comment header explaining the Phase 6 / Phase 9 lockstep, the major-version parse with `try/except (ValueError, IndexError)` fallback to 0, the env-var-aware refuse `if`, and the multi-line `FirmwareOutdatedError(...)` raise with the locked wording.
  - No other changes to the file. Plan 03's `_read_and_parse_lines`, `_decode_id_frame`, `LogMessage`, `MAGIC_PREAMBLE`, `_CRC8_CCITT_TABLE`, `_decode_param` untouched.
- `firestarter/firmware.py` — 3 insertions:
  - Line 24: added `FirmwareOutdatedError` to the import group from `firestarter.serial_comm`.
  - Lines 92-93: `except FirmwareOutdatedError: raise   # Phase 6 (LHOST-04): surface lockstep refuse to operator (do NOT swallow)`.
  - No other changes.

## Decisions Made

1. **PATTERNS open question resolved with re-raise, not swallow.** The pre-v1.2 message includes the exact remedy (`firestarter fw --install`); surfacing it directly to the operator at the CLI is more useful than letting `check_current_firmware` return `(None, None, None)` with the error visible only in DEBUG logs.
2. **Major-version threshold is `< 3`** (not `<= 2`). The firmware bumps directly from v2.0.11 to v3.0.0 in Phase 9 per the PROJECT.md lockstep constraint — no intermediate version exists.
3. **Malformed version → `major = 0`**, NOT `major = 999`. T-06-17 disposition: a tampered version cannot evade the refuse by producing an unparseable number.
4. **`_is_version_sufficient('2.0.0')` retained** as defence-in-depth. Does not double-trip on v3+ (≥2.0.0 is True). Acts as a fallback if the major-version parse ever silently regresses.
5. **Escape-hatch env-var name intentionally verbose** (`FIRESTARTER_DEV_ALLOW_PRE_V12`) — project-prefixed, descriptive, long enough that accidental shell-export is unlikely. Naming pragma, not a security boundary.
6. **Test uses `x.x.x` as malformed-version probe**, not arbitrary garbage. The existing `re.search(r"FW:\s*([\d.x]+)", msg)` regex accepts `x` literally (carried over from `2.0.x` pre-release tags) but `int('x')` raises ValueError — cleanly exercising the guard's parse-error fallback.
7. **Autouse `_clear_escape_hatch` fixture for hermeticity.** `monkeypatch.delenv` at every test entry guarantees the strict-path tests (1, 2, 4) cannot be tainted by a developer's shell-exported var. Test 3 then `monkeypatch.setenv`s the var for the one test that needs the bypass.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Patched-`__init__` left `self.connection` unset → `_probe_port`'s `disconnect` failover crashed with `AttributeError`**

- **Found during:** Task 2, first run of `pytest tests/test_fwguard.py`. Tests 1 and 4 failed at `_probe_port`'s `except FirmwareOutdatedError`-block site:
  ```
  firestarter/serial_comm.py:704: in _probe_port
      communicator.disconnect()
  firestarter/serial_comm.py:540: in disconnect
      if self.is_connected():
  firestarter/serial_comm.py:202: in is_connected
      return self.connection is not None and self.connection.is_open
  AttributeError: 'SerialCommunicator' object has no attribute 'connection'
  ```
- **Issue:** Patching `__init__` to a no-op `lambda self, port, **k: None` means the instance never gets `self.connection = serial.Serial(...)`. When the guard raises `FirmwareOutdatedError`, `_probe_port`'s exception handler calls `communicator.disconnect()`, which calls `is_connected()`, which reads `self.connection` — undefined.
- **Fix:** Add `patch.object(SerialCommunicator, "disconnect", return_value=None)` to the patch stack in ALL four tests (refuse + accept + escape-hatch + malformed). The accept-path test already had it (the PATTERNS recipe at lines 808-820 omits it, but the live `_probe_port` path calls `disconnect()` on both the FirmwareOutdatedError exit AND the success-info-save exit, so all 4 tests need it).
- **Files modified:** `firestarter_app/tests/test_fwguard.py` only (inline fix during Task 2; no separate commit — the fix landed as part of the initial test-file commit).
- **Verification:** `pytest tests/test_fwguard.py -v` → 4 passed.
- **Committed in:** `08f906d` (Task 2 submodule commit, contains the corrected version).

### No other deviations

The plan's specified guard logic, locked wording, exception-clause ordering, and test surface were implemented exactly per PLAN.md, PATTERNS.md, and the RESEARCH-derived wording.

## Authentication Gates

None. The plan is fully autonomous host-side infrastructure; no external service, no hardware, no auth flow.

## Issues Encountered

- One blocking issue: the `__init__` short-circuit + `_probe_port`'s defensive `disconnect()` interaction (documented as deviation 1 above). Fixed inline before the first test commit.
- Pre-existing dirty `firestarter_app` files (`firestarter/config.py`, `firestarter/main.py`) were left untouched per orchestrator instruction. Verified via `git status` after each commit: those two files remain `M` (unstaged) throughout; neither of the two task commits touched them.

## PATTERNS Open Question Resolution

The PATTERNS document called out an open question on `firmware.py:check_current_firmware`'s handling of `FirmwareOutdatedError` (lines 508 and 512 of `06-PATTERNS.md`):

> "either keep swallow + log, or add `except FirmwareOutdatedError: raise` BEFORE the broad catch. RESEARCH.md §"Host FW-Version Refuse Guard" implies surfacing; planner picks."

**Resolution: re-raise.** Rationale:

- The pre-v1.2 message is fully operator-actionable (it names the version seen and the exact install command). Surfacing it directly to the CLI gives the user immediate visibility; swallowing it would leave them with a generic `(None, None, None)` return and the error visible only in DEBUG-level logs.
- The broad `(ProgrammerNotFoundError, SerialError)` catch is now scoped to its true purpose: transport-layer failures (port unavailable, write error, etc.), which the user cannot fix from a CLI error message but CAN diagnose from the logged context.
- Source order verified: line 92 `except FirmwareOutdatedError:` precedes line 94 `except (ProgrammerNotFoundError, SerialError)`. Specific-before-broad — Python evaluates them top-down, so the explicit clause wins even though `FirmwareOutdatedError` inherits from `SerialError`.

## Phases 7-8 Bench-Script Pragma

The `FIRESTARTER_DEV_ALLOW_PRE_V12=1` env var is the documented escape hatch for bench scripts during Phases 7-8 while firmware still reports `2.0.11`:

```bash
# Bench-script preamble during Phase 7-8 wave
export FIRESTARTER_DEV_ALLOW_PRE_V12=1
./firestarter_test.sh <EPROM>   # or any firestarter-CLI invocation
```

After Phase 9 (firmware bumps to v3.0.0), the bench scripts unset the var and the guard becomes a no-op for production users (who will be on v3+ by definition since they shipped through Phase 9).

The env var is intentionally **not** documented in user-facing CLI `--help` output or README — only here in the plan's SUMMARY and in the inline comment block at `serial_comm.py:647-650`. Operator-facing surface remains "upgrade the firmware to v3.0.0 or later".

## User Setup Required

None. Bench operators who want to keep using their existing v2.0.11 firmware between Phase 6 and Phase 9 set the env var as documented above.

## Next Plan Readiness

**Plan 06-05 (CI drift gate)** is unblocked. The CI workflow can invoke:
```bash
cd firestarter_app && pip install -e .[dev] && pytest -q
```
and expect 14 tests passing (10 from Plan 03, 4 from this plan). Any future regression in either decoder or fw-guard surface will fail CI visibly.

**Phase 9 (firmware version bump)** has the host side fully wired and tested. The moment firmware emits `OK: FW: 3.0.0, HW: Rev2, Cmd: 0x0d`, the guard transitions silently from "refuse" to "accept" — no further host change required.

## Self-Check: PASSED

Files exist:

- `firestarter_app/firestarter/serial_comm.py` (`import os`, `FIRESTARTER_DEV_ALLOW_PRE_V12`, locked wording, `major < 3`, retained `_is_version_sufficient`) — FOUND.
- `firestarter_app/firestarter/firmware.py` (`FirmwareOutdatedError` import, `except FirmwareOutdatedError: raise` BEFORE broad catch) — FOUND.
- `firestarter_app/tests/test_fwguard.py` (4 test methods, autouse delenv fixture, monkeypatch.setenv for escape-hatch test) — FOUND.
- `.planning/phases/06-logging-infrastructure/06-04-SUMMARY.md` (this file) — FOUND.

Commits (all on `feature/phase-10-static-pins`):

- firestarter_app `8ed7036` (feat 06-04) — FOUND (Task 1)
- firestarter_app `08f906d` (test 06-04) — FOUND (Task 2)
- meta-repo `6d20c38` (chore 06-04 pointer bump task 1) — FOUND
- meta-repo `ceaae4b` (chore 06-04 pointer bump task 2) — FOUND

Behavioural verification:

- `cd firestarter_app && pytest tests/ -v` → `14 passed in 0.25s` (10 decoder + 4 fwguard)
- `cd firestarter_app && pytest tests/test_fwguard.py -v` → `4 passed in 0.03s`
- `FIRESTARTER_DEV_ALLOW_PRE_V12=1 pytest tests/test_fwguard.py -v` → `4 passed` (autouse delenv hermeticity confirmed)
- `python3 -c "from firestarter.serial_comm import FirmwareOutdatedError, SerialError; assert issubclass(FirmwareOutdatedError, SerialError)"` → exits 0

---
*Phase: 06-logging-infrastructure*
*Completed: 2026-05-18*
