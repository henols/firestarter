---
phase: 120-host-cli-surface-wire-emission-capability-refusal
verified: 2026-07-29T00:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 120: HOST — CLI surface, wire emission, capability refusal — Verification Report

**Phase Goal:** The lock/unlock capability becomes reachable from the CLI, correctly wired to the new firmware commands — and the host never emits a flag or command that current firmware would silently ignore or misinterpret.
**Verified:** 2026-07-29
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `firestarter dev sdp <chip> enable\|disable` exists, gated behind the v1.21 destructiveness confirm (or `-y`), and hard-fails on an absent chip before opening a serial port | ✓ VERIFIED | `cli_handlers.py:2024-2142` implements `dev sdp` with Gate 1 (`app.db.get_eprom(eprom)` absent-chip hard-fail, raises before any operator/serial call) → Gate 2 (capability) → Gate 3 (support-status) → Gate 4 (consent: on-TTY `Confirm.ask`, `-y` bypass, off-TTY-without-`-y` refuses). Independently ran `pytest tests/test_dev_sdp_cmd.py -v`: `test_gate_order_absent_chip_refuses_before_confirm_and_before_serial` and `test_no_port_opened_on_any_refusal_with_a_real_operator` assert `mock_confirm.ask.assert_not_called()` **and** `mock_find_and_connect.assert_not_called()` — the latter test uses a **real** `EpromOperator` with only the transport patched, so this is a genuine transport-level proof, not merely a mocked-operator proof. All 12 tests in `test_sdp_capability.py` and the `dev_sdp`-specific legs in `test_dev_sdp_cmd.py` pass. |
| 2 | `write --skip-sdp-unlock` emits `FLAG_SKIP_SDP_UNLOCK` on the wire, and a constants-parity test proves firmware and host agree on the flag's bit value, the new `CMD_*` values, and their `COMMAND_NAMES` entries | ✓ VERIFIED | `constants.py:72-73,90-91,121` defines `COMMAND_SDP_UNLOCK=9`, `COMMAND_SDP_LOCK=10`, `FLAG_SKIP_SDP_UNLOCK=0x100` with `COMMAND_NAMES` entries; `firestarter/include/firestarter.h` (firmware repo) has identical `#define CMD_SDP_UNLOCK 9` / `CMD_SDP_LOCK 10` / `FLAG_SKIP_SDP_UNLOCK 0x100`, confirmed by direct grep. `build_flags()` in `eprom_operations.py:173-211` ORs in the bit. `tests/test_write_skip_sdp_unlock.py` asserts the **emitted `flags` value at the transport seam** (`SerialCommunicator.find_and_connect`'s `command_dict`), not merely `build_flags`'s return value. Ran `pytest tests/test_revision_constants_parity.py -v`: all 13 tests pass, including 4 planted-violation legs (`test_planted_value_drift_is_detected`, `test_planted_host_missing_define_is_detected`, `test_planted_firmware_missing_flag_is_detected`, `test_missing_command_names_entry_is_detected`) whose bodies I read and confirmed assert the gate actually raises `AssertionError` with the expected message — non-vacuous — plus a fail-closed test that points at a nonexistent path and asserts an `AssertionError` ("firmware header not found") rather than a silent pass. |
| 3 | Issuing an SDP command against a `0x0D` chip in the non-SDP subset (2 FRAM parts, or pre-SDP `2804`/`2816`/`2817` class) is refused in-host before any serial byte is sent, with zero `chip_database.json` changes | ✓ VERIFIED | `sdp_capability.py` implements a static 43-ALLOW/41-REFUSE fail-closed allow-list, name-keyed (reads `db.get_eprom()`'s `name`/`protocol-id`, never a `resolve_chip` dict — confirmed by `test_predicate_is_name_keyed_and_a_programmer_dict_is_rejected`). `test_all_dip24_2816_parts_are_refused`, `test_both_fram_parts_are_refused_with_the_fram_reason`, `test_host04_named_pre_sdp_class_is_refused`, `test_all_nine_adapter_required_parts_are_refused_by_capability`, and `test_local_override_0x0d_entry_is_refused_at_runtime` all pass (ran directly). `dev sdp`'s Gate 2 calls this predicate before Gate 4/serial. Ran `git log --oneline -- firestarter/data/chip_database.json` — no commit since 362bfa0 (Phase 98), confirming zero DB changes across this phase; `git diff --stat 9ead17f..HEAD -- firestarter/data/chip_database.json` is empty. |
| 4 | The reported SDP outcome never states a fabricated lock/unlock boolean — when state can't be confirmed, the report says so in words | ✓ VERIFIED | Read `dev_sdp`'s success-message code directly: `"SDP {mode} sequence for {chip} was emitted. The resulting protection state cannot be read back on this chip family, so this is not a claim about the chip's actual state."` — no boolean, explicit uncertainty in words. `test_no_fabricated_lock_state_boolean_in_the_report` asserts the phrase composition (`"was emitted"`, `"cannot be read back"`, `"not a claim about the chip's actual state"`) rather than a brittle forbidden-word blacklist. `sdp_lock`/`sdp_unlock` docstrings in `eprom_operations.py:1754-1759,1802-1807` state the same honesty floor. Ran the test — passes. |
| 5 | This phase's flags and commands are not emitted, and this phase does not land, ahead of Phase 119's firmware landing | ✓ VERIFIED | `git -C /workspaces/firestarter status --porcelain` is empty and `git -C /workspaces/firestarter rev-parse --short HEAD` is `0048b3d` (Phase 119's own final commit — confirmed directly, matching the NONREGRESSION doc's claim). The firmware repo already carries `CMD_SDP_UNLOCK`/`CMD_SDP_LOCK`/`FLAG_SKIP_SDP_UNLOCK`/`MSG_WARN_SDP_UNLOCK_SKIPPED` (confirmed by grep against `firestarter/include/firestarter.h` and `messages.h`) — these predate Phase 120's host commits structurally (Phase 120 built its parity gate and CLI surface against symbols that already existed in the firmware tree it never touched). |

**Score:** 5/5 truths verified.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/sdp_capability.py` | Derived 43/41 allow-set + pure predicate | ✓ VERIFIED | Exists, substantive (no stubs), imports only `typing` (confirmed by `test_sdp_capability_module_imports_nothing_but_stdlib_typing`), wired into both `dev_sdp` and `write` handlers |
| `firestarter_app/tests/test_sdp_capability.py` | 12-leg gate | ✓ VERIFIED | 12 tests, all pass independently |
| `firestarter_app/firestarter/constants.py` | New `CMD_*`/`FLAG_*` + `COMMAND_NAMES` | ✓ VERIFIED | Confirmed present, matches firmware header byte-for-byte on value |
| `firestarter_app/firestarter/serial_comm.py` | INFO-band promotion + `seen_message_ids` | ✓ VERIFIED | `_log_rurp_feedback` promotes `INFO` type to `logging.INFO`; `seen_message_ids: set[int]` populated in `_decode_id_frame` seam (line 133, 321) |
| `firestarter_app/firestarter/eprom_operations.py` | `sdp_unlock`/`sdp_lock`, keyword-only `skip_sdp_unlock`, D-15 ack check | ✓ VERIFIED | All present and wired; D-15 check reads `self.comm.seen_message_ids` inside the `_operation_context` block, scoped via `eprom_data_dict.get("algorithm") == SDP_PROTOCOL_ID` |
| `firestarter_app/firestarter/cli_handlers.py` | `dev sdp` command, `--skip-sdp-unlock` on `write`, D-04 auto-set | ✓ VERIFIED | Both present at the documented line ranges, gate ordering matches design |
| `firestarter_app/tests/test_revision_constants_parity.py` + 3 fixtures | Two-way header-parsing parity gate | ✓ VERIFIED | 13 tests pass; 3 fixture files exist at `tests/fixtures/planted_constants_{value_drift,fw_missing,host_missing}.h`; each drives a real `AssertionError` through the actual gate function, not a parallel reimplementation |
| `firestarter_app/tests/test_dev_sdp_cmd.py`, `tests/test_write_skip_sdp_unlock.py` | CLI-surface + wire-emission tests | ✓ VERIFIED | Both files exist, all tests pass, assertions use mock-call proofs (`assert_not_called()`) and transport-level flag capture, not exit-code-only checks |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `dev_sdp` handler | `sdp_capability()` | direct call, Gate 2, before Gate 4/serial | ✓ WIRED | Confirmed by reading `cli_handlers.py:2066-2068` |
| `write` handler | `sdp_capability()` | D-04 auto-set decision | ✓ WIRED | Confirmed at `cli_handlers.py:566-576` |
| `build_flags()` | wire `flags` int | `FLAG_SKIP_SDP_UNLOCK` bit OR | ✓ WIRED | Confirmed at `eprom_operations.py:208-209`, and proven at the transport seam by `test_write_skip_sdp_unlock.py` |
| `write_eprom` | `seen_message_ids` | D-15 post-hoc ack check | ✓ WIRED | Confirmed at `eprom_operations.py:1655`; both positive and negative legs pass using a fake serial stream (`test_missing_sdp_ack_fails_the_write_loudly`, `test_sdp_ack_honoured_produces_no_complaint`, `test_ack_check_does_not_run_when_the_flag_was_not_set`) |
| `constants.py` | `firestarter.h` (firmware) | two-way header-parsing parity gate | ✓ WIRED | Gate reads the actual firmware header file at a resolved path; fails closed on missing path; verified with 4 planted-violation legs, each independently reproduced as passing |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| HOST-01 | 120-06, 120-08 | `dev sdp` CLI surface + gate order | ✓ SATISFIED | Code + tests confirmed directly |
| HOST-02 | 120-06, 120-09 | `write --skip-sdp-unlock` wire emission | ✓ SATISFIED | Code + transport-level test confirmed |
| HOST-03 | 120-02, 120-07 | Constants parity, `COMMAND_NAMES` | ✓ SATISFIED | Rebuilt real gate, 13 tests, 4 planted-violation legs all independently verified non-vacuous |
| HOST-04 | 120-01, 120-04, 120-05, 120-09 | Pre-wire capability refusal, zero DB change | ✓ SATISFIED | 43/41 partition, zero DB diff confirmed by git log/diff |
| HOST-05 | 120-03, 120-08 | Honest report, no fabricated boolean | ✓ SATISFIED | Message text read directly, matches claim |
| HOST-06 | 120-10 | Sequencing invariant upheld in practice | ✓ SATISFIED (see caveat below) | D-15 ack-based detection proven behaviorally; D-14 command-mapping proven only via mocked operator (see Anti-Patterns/Known-Findings) |

No orphaned requirements: `REQUIREMENTS.md` maps exactly HOST-01..06 to Phase 120, and all six appear in at least one plan's frontmatter `requirements:` list (120-01 through 120-12).

### Anti-Patterns Found

None. Scanned `sdp_capability.py`, `constants.py`, `serial_comm.py`, `eprom_operations.py`, `cli_handlers.py`, and all four new/extended test files for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` — zero hits across the phase's changed surface.

### Known, Already-Recorded Finding (carried forward, not a new gap)

**D-14's `MSG_ERR_UNKNOWN_CMD` → firmware-too-old mapping is real code, unit-proven only via a mocked operator; its production wire path is dead.** I independently traced this rather than trusting `120-NONREGRESSION.md`'s claim: `dev_sdp`'s `except EpromOperationError as e: if e.error_code == MSG_ERR_UNKNOWN_CMD: raise FirmwareOutdatedError(...)` wraps a call to `sdp_lock`/`sdp_unlock`, both of which delegate to `self._run_state_machine(op_name)` (`eprom_operations.py:1729,1777`). `_run_state_machine` (`eprom_operations.py:420-458`) has its own `except EpromOperationError as e: ... return False, str(e)` — which catches and swallows the exact exception `dev_sdp`'s handler is written to catch, **before** it can propagate up to `dev_sdp`. In production, an unknown-command response therefore surfaces only as a generic `logger.error("Programmer error during ...")` line and a bare `sys.exit(1)`, never the friendly "upgrade with `firestarter fw --install`" message. This does not fabricate a boolean, does not silently succeed, and does not break the fail-closed/refuse-before-serial guarantees — it is a UX-quality gap in the D-14 friendly-messaging layer, not a safety defect. This finding was already surfaced by the phase's own Plan 120-08/120-10 work and recorded in `120-NONREGRESSION.md`; it does not undermine any of the 5 roadmap success criteria (criterion 4's "never fabricated boolean" holds regardless, since `ok=False` in this path and no success message is printed). Recorded here as a WARNING-level, non-blocking observation — no new information, cross-checked against the actual code rather than accepted on the document's word.

The pre-existing `test_audit_coverage_matrix.py::test_golden_file_matches` failure was reproduced independently in this verification (`186034` vs `184631` bytes) and confirmed to be the documented stale-golden condition, unrelated to Phase 120's diff.

### Human Verification Required

None. All five roadmap success criteria are resolved by direct code inspection plus independently re-run automated tests (not merely re-reading SUMMARY/NONREGRESSION claims). No visual, real-time, or hardware-dependent behavior is asserted by this phase — it explicitly adds no bench work (no AT28C part on the bench), and the Validation Ceiling in REQUIREMENTS.md/120-VALIDATION.md correctly scopes the phase's claims to software-provable facts only.

### Gaps Summary

No gaps. All 5 ROADMAP success criteria verified directly against source and independently re-executed tests (not SUMMARY claims):
- `firestarter/sdp_capability.py`, `constants.py`, `serial_comm.py`, `eprom_operations.py`, `cli_handlers.py` all read as described, with no stub/placeholder/debt-marker patterns.
- `firestarter_app` full test suite reproduced 1050 passed / 1 pre-existing failed (matching the documented, out-of-scope stale-golden condition).
- Targeted suites (`test_sdp_capability.py`, `test_dev_sdp_cmd.py`, `test_write_skip_sdp_unlock.py`, `test_revision_constants_parity.py`, plus the D-15 legs in `test_eprom_operations.py`) all independently re-run and passed, and the planted-violation/fail-closed legs were read and confirmed to assert real failures, not vacuous conditions.
- Firmware submodule confirmed untouched (`git status --porcelain` empty, HEAD `0048b3d`), and `chip_database.json` confirmed byte-unchanged since before this phase.
- One already-known, already-documented UX-quality finding (D-14's dead production path) was independently re-traced and confirmed accurate; it does not undermine any success criterion and is not a new gap.

---

_Verified: 2026-07-29_
_Verifier: Claude (gsd-verifier)_
