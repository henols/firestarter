---
phase: 202-one-comparison-engine-on-the-host
reviewed: 2026-09-20T19:43:22Z
depth: standard
files_reviewed: 21
files_reviewed_list:
  - firestarter_app/firestarter/compare.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/chip_test.py
  - firestarter_app/pyproject.toml
  - firestarter_app/tests/test_compare.py
  - firestarter_app/tests/test_eprom_operations.py
  - firestarter_app/tests/test_cli_handlers.py
  - firestarter_app/tests/test_chip_test.py
  - firestarter_app/tests/fake_chip.py
  - firestarter_app/tests/fixtures/report_shapes.py
  - firestarter_app/tests/plan_corpus.py
  - firestarter_app/tests/test_chip_test_cycle.py
  - firestarter_app/tests/test_chip_test_sdp_leg.py
  - firestarter_app/tests/test_chip_test_timing.py
  - firestarter_app/tests/test_chip_test_uv_slot_write.py
  - firestarter_app/tests/test_dev_test_cmd.py
  - firestarter_app/tests/test_devtest_firmware_error_propagation.py
  - firestarter_app/tests/test_diagnostic_report.py
  - firestarter_app/tests/test_erase_blank_step_nonregression.py
  - firestarter_app/tests/test_write_response_budget.py
findings:
  critical: 1
  warning: 2
  info: 1
  total: 4
status: issues_found
---

# Phase 202: Code Review Report

**Reviewed:** 2026-09-20T19:43:22Z
**Depth:** standard
**Files Reviewed:** 21
**Status:** issues_found

## Summary

Phase 202 extracts a new streaming comparison engine (`compare.py`) and moves `verify`/`blank`
off the firmware's own verify/blank-check ordinals onto host-side reads through it. The engine
itself (`CompareAccumulator`, `classify_streamed`, the D-16 range cap, the D-08 abort/timeout
discrimination) is careful, well-reasoned work: I traced the coalescing, cap-boundary, and
bit-clustering arithmetic by hand across chunk boundaries, non-zero `addr_base`, and the
`full`/non-`full` split, and it holds up — including the subtle "cap bounds what is shown, never
what is counted" invariant, which is genuinely honored by the running counters. The test suite for
`compare.py` (`test_compare.py`) is unusually rigorous: an independent, hand-transcribed batch
reference is checked against the streamed path over a 12+ row corpus, an AST-based test pins the
import-purity invariant, and another AST-based test pins the equality-fast-path-before-per-offset
-loop shape so a performance regression fails loudly rather than silently.

The one real defect found is in the new CLI-tier region-refusal check
(`cli_handlers._region_refusal_exit_code`), shared by `verify` and `blank`: it fails to catch an
out-of-range `--address` on `blank` when `--size` is omitted, letting a malformed region reach the
wire and reporting the wrong exit code for it. This exact function has test coverage for the
`-a`+`-s` combination but never for `-a` alone, which is exactly the gap that slipped through.

## Critical Issues

### CR-01: `blank -a <address-past-chip-end>` (no `--size`) is not refused, sends a malformed region to the wire, and reports the wrong exit code

**File:** `firestarter_app/firestarter/cli_handlers.py:796-872` (`_region_refusal_exit_code`)

**Issue:** Both `verify` and `blank`'s docstrings state the same contract: "Exits ... 2 on a
transport, hardware, setup, or region failure ... a region refusal -- a region running past the
chip's end -- is reported before the serial port ever opens." `_region_refusal_exit_code`
implements this by computing an effective `length` and refusing when `start + length > mem_size`.
But when no `--size` is given and there is no `input_file` (`blank`'s case), `length` is left as
`None` unconditionally:

```python
if explicit_size is not None:
    length: int | None = explicit_size
elif input_file is not None:
    ...
else:
    length = None  # blank's whole-chip default: nothing to bound here
```

This comment is only correct when `start == 0` (the true whole-chip case). When an operator
supplies `-a <addr>` without `-s`, the *effective* declared region is "the rest of the chip from
`addr` to `mem_size`" — a real, boundable length (`mem_size - addr`) — not "nothing to bound".
Because `length` stays `None`, the `mem_size` check is skipped entirely, and an out-of-range
`--address` sails straight through to `EpromOperator.check_eprom_blank`, which then computes
`region_length = cmd_data.get("memory-size", 0) - cmd_data.get("address", 0)` — a **negative**
number — and drives a `COMMAND_READ` whose wire `address` (32768 in the repro below) exceeds its
own wire `memory-size` (16384). This is exactly the malformed-region case the CLI tier exists to
prevent before the port opens; it is not prevented here.

Confirmed with a live simulation (see repro): the command actually sent to `find_and_connect` is
`{'memory-size': 16384, 'address': 32768, ...}`, and the eventual verdict is `1` ("not blank")
rather than the documented `2` (region refusal). The only reason this doesn't silently report a
false "blank" pass is `_drive_region_compare`'s unrelated `result.total > 0` guard (in
`eprom_operations.py`), which happens to also reject the resulting negative `result.total` — a
coincidental save, not a designed one. The exit code is still wrong (`1` instead of `2`), and a
malformed address is still sent to real firmware, with behaviour on actual hardware unverified by
this suite.

**Repro (verified against the current tree):**
```python
from firestarter.cli_handlers import _region_refusal_exit_code
_region_refusal_exit_code(
    eprom="X", eprom_data={"memory-size": 0x4000}, address="0x8000", size=None,
)
# -> None  (expected: 2, a refusal)
```
Driving `EpromOperator.check_eprom_blank("X", {"memory-size": 0x4000, ...}, address_str="0x8000")`
through a fake serial confirms the wire command carries `address=32768` against `memory-size=16384`
and returns verdict `1`.

**Missing test coverage:** `tests/test_cli_handlers.py::test_region_past_chip_end_is_refused_before_opening_the_port`
is the only test of this refusal path for `blank`, and it always supplies `-a` **and** `-s`
together (`["-a", "0x10000", "-s", "1"]`). The `-a`-alone case for `blank` — the actual gap — has
no test anywhere in the suite (confirmed by grep across `tests/`).

**Fix:** When no explicit `--size` is given but a non-zero `--address` is (the `blank` case),
default `length` to `mem_size - start` (when `mem_size` is known) instead of `None`, so the
existing `start + length > mem_size` check applies uniformly:

```python
if explicit_size is not None:
    length: int | None = explicit_size
elif input_file is not None:
    try:
        length = os.path.getsize(input_file)
    except OSError:
        length = None
else:
    mem_size_hint = eprom_data.get("memory-size")
    length = None if mem_size_hint is None else max(0, mem_size_hint - start)
```
Add a test that drives `blank -a <past-end-address>` with **no** `-s` and asserts exit code 2 and
that `find_and_connect`/`check_eprom_blank` are never called — the mirror image of the existing
`-a`+`-s` test.

## Warnings

### WR-01: Deliberate-abort vs. genuine-timeout discrimination has a hard-coded 3.0 s window with no test at its true failure boundary

**File:** `firestarter_app/firestarter/eprom_operations.py:98-107, 2290-2316` (`READ_ABORT_ACCEPTANCE_WINDOW_S`, `_drive_region_compare`)

**Issue:** The D-08 discrimination that tells a deliberate host-initiated read-stop apart from a
genuine hardware timeout relies on `(time.monotonic() - stopped_at) <= READ_ABORT_ACCEPTANCE_WINDOW_S`
using a fixed 3.0 s window. The reasoning documented for this constant (firmware's 1 s
`op_wait_for_ack` plus a few ms of transmission) is sound for the common case, but the window is a
real wall-clock budget that spans a Python call into `time.monotonic()`, GIL contention, OS
scheduling, and USB-serial driver latency on the host — none of which are bounded by the firmware's
own 1 s figure. If a real deliberate abort's `MSG_ERR_TIMEOUT` frame is delayed past 3.0 s under
host-side load (e.g. a busy CI runner, a slow USB-to-serial bridge, or simply many
`dev test`-style back-to-back operations queuing up scheduler time), `_drive_region_compare` will
misreport a genuine mismatch as exit code 2 (hardware failure) instead of exit code 1 (mismatch) —
the exact class of error this discrimination exists to prevent, just triggered from the opposite
direction the tests cover. `test_timeout_outside_the_acceptance_window_returns_two` only tests the
window firing *correctly* on an already-recorded genuine "arrived very late" case; there is no test
that exercises the window from just-inside-the-boundary to confirm the discrimination still
recognizes an abort at, say, 2.9 s under simulated host jitter. This is a design tradeoff, not
obviously wrong, but it is untested at its actual failure edge and the risk (a real mismatch being
reported as a false hardware error) is exactly the kind of finding the phase's own stated
invariants (`the abort seam ... whether the abort-vs-fault discrimination can misfire in either
direction`) asks to be surfaced.

**Fix:** Either document the window as a known, accepted false-hardware-error risk under host load
(so a future debugger doesn't waste time chasing a "verify reports hardware error but the chip is
actually just mismatching" report as a hardware bug), or make the window configurable/env-driven
for constrained CI environments, and add a test that simulates the window firing just inside its
boundary under an injected delay to confirm the discrimination still resolves to "aborted".

### WR-02: `check_eprom_blank`'s SRAM/FRAM refusal (exit 2) and a genuine transport failure (also exit 2) are indistinguishable from a real hardware failure inside `_dispatch_step`'s blank-check dispatch, but this is pre-existing, undocumented as a *new* risk

**File:** `firestarter_app/firestarter/chip_test.py:2591-2619`

**Issue:** `_dispatch_step`'s `OP_BLANK_CHECK` arm does
`is_ok = operator.check_eprom_blank(name, eprom_data) == 0`, folding both verdict `1` (not blank)
and verdict `2` (refusal, including a genuine transport/hardware failure now that
`check_eprom_blank` composes `COMMAND_READ` and can fail for reasons unrelated to SRAM/FRAM
detection) into the same "not ok" branch, which then becomes `VERDICT_BAD` for any non-UV-prewrite
chip. The code comment acknowledges this is deliberate scope-narrowing ("the real migration to the
3-way (0/1/2) verdict is phase 206's job"), and the SRAM/FRAM refusal case specifically is proven
unreachable via this path (`derive_plan` marks that step `supported=False` before dispatch ever
happens). However, a *different* verdict-2 cause — a genuine transport/hardware failure during the
blank-check's read — is not proven unreachable, and folding a hardware fault into `VERDICT_BAD`
("chip is not blank") rather than a distinct hardware-failure verdict could mislead a `dev test`
report reader into believing the chip itself is at fault when the actual cause was a dropped
connection. Flagging because this fold-in silently changed shape in this phase: pre-202-05,
`check_eprom_blank` could only return bool (verdict-2 didn't exist as a concept), so "not ok" was
unambiguous; post-202-05, a value that used to be structurally impossible (a refusal on this
specific code path) is possible in principle for other reasons and is being silently absorbed.

**Fix:** No change required for this phase's stated scope (explicitly deferred to phase 206 per
the code's own comment), but worth a one-line addition to that comment naming the specific residual
risk (a genuine transport failure during `dev test`'s blank-check step reads as `VERDICT_BAD`, not
a distinct hardware-verdict), so a future reader doesn't have to re-derive it.

## Info

### IN-01: `CompareAccumulator.feed()`'s post-offset-computation empty check is dead code

**File:** `firestarter_app/firestarter/compare.py:241-244`

**Issue:**
```python
offs = [o for o in range(chunk_len) if expected[o] != actual[o]]
if not offs:
    self._close_open_range()
    return
```
This branch is reached only after the preceding Tier-2 fast path (`if expected == actual: ...
return`) has already confirmed `expected != actual` for this chunk. Since `feed()`'s docstring
guarantees `len(expected) == len(actual) == chunk_len`, byte-sequence inequality over equal-length
sequences always means at least one index differs, so `offs` can never be empty at this point. The
branch is unreachable in practice. Harmless (defensive code that costs nothing at runtime and
protects a documented invariant others could unknowingly relax), but worth noting since one of this
module's own stated design principles is to keep the divergence math to exactly one path with no
redundant computation.

**Fix:** Either remove the dead branch, or add a comment noting it is deliberately-kept defensive
redundancy in case a future caller violates the equal-length contract.

---

_Reviewed: 2026-09-20T19:43:22Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
