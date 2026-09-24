---
phase: 203-the-write-guard-moves-up-a-layer
reviewed: 2026-09-21T14:12:39Z
depth: standard
files_reviewed: 10
files_reviewed_list:
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/compare.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/firestarter/exceptions.py
  - firestarter_app/firestarter/write_blank_guard.py
  - firestarter_app/tests/__snapshots__/test_characterization.ambr
  - firestarter_app/tests/fake_chip.py
  - firestarter_app/tests/test_write_blank_guard.py
  - firestarter_app/tests/test_write_blank_guard_pinning.py
  - firestarter_app/tests/test_write_verify.py
findings:
  critical: 1
  warning: 2
  info: 1
  total: 4
status: issues_found
---

# Phase 203: Code Review Report

**Reviewed:** 2026-09-21T14:12:39Z
**Depth:** standard
**Files Reviewed:** 10 (submodule range `a0855b9..HEAD` on `v1.41-verification-to-host`, per the phase's scope note)
**Status:** issues_found

## Summary

Phase 203 moves the pre-write blank check to the host (`write_blank_guard.py`) and adds `write
--verify`'s widened 0/1/2 exit-code contract (`cli_handlers.write`, `EpromOperator.write_eprom` /
`verify_eprom` / `_run_write_blank_guard`). The predicate module itself (`write_blank_guard.py`) is
correct and tightly pinned: `GUARDED_PROTOCOL_IDS` matches the required `{0x06,0x07,0x08,0x0B,0x10}`
exactly, `is_guarded_protocol`/`requires_blank_check` fail closed on absent/`None` evidence as
required, the module reads only `algorithm`/`flags` (verified both by reading and by the file's own
AST-walking test), both keys are genuinely present on every `resolve_chip()` wire dict, and
`refusal_text` carries no remedy clause. The address arithmetic that turns a `CompareResult`'s
region-relative `first_offset` back into an absolute address for the refusal message
(`region_start + first_offset`) is correct. Cross-checking the guarded/exempt protocol-id sets
against `tools/build_db.py`'s `KNOWN_PROTOCOLS` shows no coverage gap: every protocol id that can
actually reach `resolve_chip()` is classified by one of the two sets, or refused earlier as
unsupported.

The exit-code contract in `cli_handlers.write` is close to sound but has one real inaccuracy (a
"the write did not complete" line printed for an invocation where the write actually did land), and
the guard's core safety property — that the region proven blank is the region that gets written —
is not actually enforced by the implementation, because the guard's read and the write itself are
two independent serial connections with no port-identity pinning between them.

## Critical Issues

### CR-01: The blank-guard's read and the write it gates can silently target different boards

**File:** `firestarter_app/firestarter/eprom_operations.py:2158-2200` (`_run_write_blank_guard`'s own
`_operation_context` call) and `firestarter_app/firestarter/eprom_operations.py:2322-2329`
(`write_eprom`'s own, separate `_operation_context` call for `COMMAND_WRITE`)

**Issue:** `write_blank_guard.py`'s own module docstring states this guard "is the whole safety net
after Phase 205 removes the firmware's own write-init pre-flight," and its fail-closed design is
built entirely around the premise that proving a *region* blank is sufficient grounds to write that
region. That premise silently assumes the region it just read and the region it is about to write
are on the *same physical chip*. Nothing in the implementation enforces that.

`_run_write_blank_guard` opens its own `_operation_context(..., COMMAND_READ, ...)`, which calls
`SerialCommunicator.find_and_connect(command_dict, self.config, ...)` with no `restrict_to_port`
override, does its read, and disconnects (`_operation_context`'s `finally` always calls
`_disconnect_programmer()`). `write_eprom` then opens a **second, independent**
`_operation_context(..., COMMAND_WRITE, ...)`, which calls `find_and_connect` again from scratch.

`find_and_connect`'s own docstring (`serial_comm.py:983-993`) states that port selection is
restricted to one candidate *only* when the operator typed `-p` on this invocation
(`config_manager.is_transient("port") is True`); absent that, port discovery walks
`_list_potential_ports()` and connects to whichever candidate answers first. `_list_potential_ports`
itself documents (`serial_comm.py:663-668`) that when a preferred port fails to answer, "probing
continued and the caller was handed a DIFFERENT board's identity" — the exact failure mode this
finding is about, already known to occur for a *different* caller (`fw --install`) but left
unaddressed here.

Consequence: in any environment with more than one RURP-compatible board enumerable by
`serial.tools.list_ports.comports()` (a bench/test setup — this project's own memory notes describe
per-task port-identity churn: "ttyACM* numbers shuffle across replug" — is exactly such an
environment), the guard can prove board A's target region blank, disconnect (which also toggles DTR
and resets the connected MCU), reconnect, and land on board B for the actual write — writing over
whatever board B's chip already contains, with zero verification that board B's region was ever
blank. The `-b`/`--no-blank-check` and `-p <port>` combination is the only way an operator can pin
this today, and nothing in `write_eprom`, `write()`, or `write_blank_guard.py` requires or even
warns about it.

This is not a hypothetical: `write_cycle_eprom`/`consistency_check_eprom` already use the identical
multi-connect-per-invocation pattern for non-safety-critical reasons (a test-file comment calls it
"D-17's reality that every operation opens (and, on completion, closes) its own port"), so the
pattern is established elsewhere in this codebase — but this phase is the first time that pattern is
asked to carry a "read this region, then trust that reading enough to allow an irreversible physical
write" guarantee across the reconnect boundary.

**Fix:** Have `write_eprom` resolve the port once (e.g. via the guard's own successful connect, or
by an explicit discovery step before either connect) and force both the guard's `_operation_context`
and the write's `_operation_context` to use `restrict_to_port=True` against that same resolved port
name — so a change in port availability, enumeration order, or board identity between the two
connects surfaces as a connect failure (guard verdict 2 / write attempt verdict 2), never as a
silent write to an unverified board:

```python
# write_eprom, after the guard's own connect has resolved a port:
resolved_port = self.comm.port_name  # captured before the guard's context tears down
...
with self._operation_context(
    eprom_name, eprom_data_dict, COMMAND_WRITE, operation_flags,
    address_str, region_length=region_length,
    # new: force the same physical port the guard just proved blank
    preferred_port=resolved_port, restrict_to_port=True,
) as (cmd_data, buf_size, op_name):
    ...
```

## Warnings

### WR-01: `write --verify`'s "did not complete" line is printed for a write that actually landed

**File:** `firestarter_app/firestarter/eprom_operations.py:2373-2391` (verdict recorded before the
`--skip-sdp-unlock` ack check) and `firestarter_app/firestarter/cli_handlers.py:918-948` (Arm 4)

**Issue:** `write_eprom` deliberately records `last_write_attempt_verdict` from the state machine's
own `is_ok` **before** the `--skip-sdp-unlock` ack-verification block runs (comment: "before the
`--skip-sdp-unlock` ack block below, which flips `is_ok` to `False` AFTER a run that already
succeeded on the wire"). When the ack (`MSG_WARN_SDP_UNLOCK_SKIPPED`) is absent, `is_ok` is flipped
to `False`, but `last_write_attempt_verdict` stays `0` (write completed on the wire) — this exact
state is pinned by
`tests/test_write_verify.py::test_last_write_attempt_verdict_zero_when_skip_sdp_unlock_ack_check_fails`.

Back in `cli_handlers.write`, `ok=False` with `guard_verdict` not 1/2 and `attempt_verdict==0` (not
2) falls through to Arm 4's default case, which prints:

```
_WRITE_VERIFY_VERDICT_NO_WRITE = "Write to {eprom}: did not complete -- nothing was verified."
```

This line is factually wrong for this specific state: the write *did* complete on the wire (data was
physically programmed into the chip); only the host's own audit check for the `--skip-sdp-unlock`
acknowledgement failed. Exit code 1 ("host decided") is the right exit code for this case, but the
printed line claims nothing landed, when in fact something did. An operator reading only this line
(without `-v`/debug logs) could be misled into believing the chip is untouched and, for instance,
attempt a blind retry rather than investigating the SDP-unlock/firmware-version issue the earlier
`logger.error(...)` line (also printed, at INFO/ERROR level, not necessarily visible at default
verbosity in all invocations) already explains.

**Fix:** Either special-case this state (e.g. a fifth verdict line reserved for "landed, but the
skip-sdp-unlock request could not be confirmed"), or reclassify `last_write_attempt_verdict` to a
distinct value in the SDP-ack-failure branch so arm selection in `cli_handlers.write` can route to
a line that does not claim "did not complete":

```python
# eprom_operations.py, inside the --skip-sdp-unlock ack check:
if MSG_WARN_SDP_UNLOCK_SKIPPED not in self.comm.seen_message_ids:
    logger.error(...)
    is_ok = False
    self.last_write_attempt_verdict = 1  # still "host decided", but callers
    # that want to special-case "landed but unaudited" can check this against
    # a new sentinel instead of overloading arm 4's default.
```

### WR-02: `_run_write_blank_guard` can print a fabricated (non-observed) refusal value

**File:** `firestarter_app/firestarter/eprom_operations.py:2184-2196`

**Issue:** `_run_write_blank_guard` only special-cases `verdict == 1 and captured` when logging the
refusal; when that condition holds, it reads `result.first_offset`/`result.first_actual`, defaulting
each to `0` when `None`. `_drive_region_compare`'s final classification
(`result.total > 0 and result.bad == 0 and result.compared == result.total` → 0, else → 1) means
`verdict == 1` is reachable even when `result.bad == 0` — specifically when the read completes
successfully (`is_ok=True`, so never entering the abort-discrimination branch) but delivers fewer
bytes than the declared region (`compared < total`, e.g. a firmware short-read that still reaches
`MAIN` cleanly). In that state, `result.first_offset`/`result.first_actual` are both `None` (no
mismatch was ever found), so the refusal logs `refusal_text(eprom_name, region_start + 0, 0)` —
`"Refusing write to X: not blank at 0x<region_start>, v: 0x00."` — a specific address and byte value
that were never actually observed to be non-blank. The refusal itself is correctly fail-closed (an
incomplete compare must never be treated as a pass), but the diagnostic text asserts a false,
fabricated fact about the chip's contents, which could misdirect debugging.

**Fix:** Distinguish "refused because a mismatch was found" from "refused because the compare never
reached a decidable state" and use a different message for the latter (e.g. reuse the existing
short-read/incomplete-compare wording pattern rather than `refusal_text`, which is documented as
carrying "the first non-blank address and the byte value read there" — a claim that should only be
made when a byte was actually read and found non-blank).

## Info

### IN-01: A page-aligned negative flash4 address bypasses the clearer negative-address message

**File:** `firestarter_app/firestarter/eprom_operations.py:2267-2276` and
`firestarter_app/firestarter/page_size_gate.py:162-177`

**Issue:** `write_eprom` (and `cli_handlers.write`) call `require_page_alignment` before
`require_non_negative_address`. `require_page_alignment` computes `start = parse_address(address_str)
or 0` and checks `start % page_size != 0` — for a protocol-0x05 (flash4) chip with a negative,
page-size-aligned address (e.g. `-256` with `page_size=128`, since `-256 % 128 == 0` in Python),
alignment passes silently and control reaches `require_non_negative_address` afterward, which still
correctly raises `NegativeStartAddressError`. For a negative, *mis*aligned address on the same
protocol, `require_page_alignment` raises `PageAlignmentError` first, with a message that says
nothing about the address being negative — a less specific, more confusing message than the one
`require_non_negative_address` would have produced. Since `GUARDED_PROTOCOL_IDS` never includes
0x05 (flash4 is a named exemption), this has no safety impact — it is purely a message-clarity
ordering nit affecting one already-narrow input (a malformed CLI argument on protocol 0x05 only).

**Fix:** Optional: call `require_non_negative_address` before `require_page_alignment` in both
`write_eprom` and `cli_handlers.write`, so the more specific, more actionable message always wins
for a negative address regardless of protocol or page alignment.

---

_Reviewed: 2026-09-21T14:12:39Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
