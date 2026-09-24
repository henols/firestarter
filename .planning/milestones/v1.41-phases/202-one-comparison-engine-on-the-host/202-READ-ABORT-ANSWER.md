# Phase 202 Success Criterion 5 — Answer: Aborting a Read In Flight

**Filed against:** `.planning/ROADMAP.md`'s "Known open mechanic" paragraph (v1.41 milestone
section) and the deferred requirement **CMP-F1**.

**Answered:** 2026-09-20, by phase 202 plan 04.

## The question, as the roadmap posed it

There is no abort message for a read in flight. The read path is ack-driven — the firmware sends
one chip-byte chunk, waits for the host's ack, then sends the next — so the host's only lever is to
stop acking. The roadmap's premise, until this plan, was that the firmware's END phase had to run
normally for the port to be left in a clean, reusable state. If that premise were true, "break at
first mismatch" would only ever save *output* (fewer bytes to look at, fewer report lines), because
the host would still have to drain the whole read to reach the END phase honestly. The question
success criterion 5 asks is whether the saving can be made *temporal* instead — whether the host can
actually stop the programmer sending more bytes, on a 512 KiB part, without leaving the port wedged
for the next command.

## The answer

**Yes, affirmatively, and it works inside the existing protocol with no firmware change.** A
mid-stream stop already produces a clean port, because the firmware's own error-path teardown — not
its END-phase happy path — is what actually resets programmer state, and that teardown runs
identically whether the read finished normally or died mid-flight.

## The mechanism

Three firmware facts, all read as evidence for this phase and none of them modified by it:

1. **Every chunk is acked before the next one is sent.** `_process_outgoing_data`
   (`firestarter_fw/src/eprom_operations.cpp:157-179`) calls `op_wait_for_ack(handle)` once per
   chunk it sends. If the host never sends that ack, the firmware does not — cannot — send the next
   chunk. This is the lever: the host controls the read's continuation entirely through the ack.

2. **The ack wait has a bounded, precisely known timeout.** `op_wait_for_ack`
   (`firestarter_fw/src/operation_utils.cpp:94-108`) accepts `OP_MSG_ACK`, fails immediately on
   `OP_MSG_ERROR`, and otherwise polls every 10 ms until a 1000 ms deadline, at which point it emits
   `MSG_ERR_TIMEOUT` (`0xA8`) and returns `false`. Withholding the ack therefore costs the host
   *exactly* up to one second, not an indefinite hang, and the resulting condition on the wire is a
   completely ordinary firmware error frame — nothing new has to be taught to either side of the
   protocol.

3. **The dispatch loop's own completion routine runs on that error path, not just the happy one.**
   When `_process_outgoing_data` returns `false`, `eprom_read` propagates `finished` and the main
   `loop()` (`firestarter_fw/src/firestarter.cpp:208-217, 260-347`) calls `command_done()`. That
   routine disables the chip, zeroes the control register and both address registers, sets the
   command back to `CMD_IDLE`, and restores communication mode — **the exact same teardown a normal
   END phase leaves behind.** It does not check how the MAIN phase ended; it runs unconditionally
   once the dispatch loop decides the command is finished, whether that decision came from a clean
   completion or from the ack-wait timeout.

The host-side half of this (implemented in this plan, `firestarter_app/firestarter/eprom_operations.py`):

- `_main_phase_read_data` gained an additive `abort_predicate: Callable[[], bool] | None = None`
  keyword. When present and it returns true, the read loop stops sending acks but keeps consuming
  responses from the port — it does not raise and does not break — until the firmware's own
  `MSG_ERR_TIMEOUT` frame (or, on the last chunk, a normal `MAIN` completion that beat the timeout)
  arrives. Raising out of the callback instead would have unwound the loop without ever reading that
  terminating frame, leaving unconsumed bytes on the port — precisely the wedged-port failure mode
  the roadmap's premise worried about, and precisely what this design avoids.
- `verify_eprom`'s default (non-`--full`) path passes `accumulator.has_mismatch` as that predicate,
  so the read stops the instant the first mismatching byte is fed to the comparison engine.

## The correction

The roadmap assumed the END phase itself had to run for the port to come back clean. It does not:
`command_done()` is the actual teardown, it lives in the dispatch loop rather than the END-phase
code path, and it runs identically on the error branch. The distinction matters because it is what
makes the abort safe to use routinely rather than only as a diagnostic curiosity — every aborted
read leaves the programmer in exactly the state a completed one would.

## The consequence

The default's saving is **temporal, not merely diagnostic.** On a 512 KiB part, draining a full read
after the first mismatch costs tens of seconds at 250000 baud; stopping in flight instead costs at
most the firmware's one-second ack-wait timeout, once, per aborted verify. This is precisely the
distinction success criterion 5 asks phase 202 to settle rather than leave assumed: "break at first
mismatch" is a genuine performance feature of the default `verify` path, not just a shorter report.

## The cost

Up to one second of firmware timeout per abort — the ack-wait's own deadline, unavoidable because
the deliberate stop and this cost are the same mechanism. No firmware change is required to pay it;
no new command, no new response type, no new field is added to the wire protocol.

## The discrimination this plan implements, and why it is needed

The deliberate stop and a genuine hardware timeout are **wire-identical**: both produce exactly the
same `MSG_ERR_TIMEOUT` (`0xA8`) error frame, because the host manufactures its abort by triggering
the firmware's ordinary timeout path rather than by sending anything new. Without a way to tell them
apart, a mismatching chip whose read then legitimately failed for an unrelated reason could be
misreported as a clean-looking abort, or — the more dangerous direction — this host's own deliberate
stop could be misreported as exit-2 hardware trouble on every single default-mode mismatch, which
would make the abort unusable in practice.

`verify_eprom` therefore accepts an error frame as its own doing only when **all four** of the
following hold, checked immediately after the state-machine drive returns failure:

1. **Intent** — the default (non-`--full`) path actually requested an abort for this call
   (`self._read_abort_intended`, set fresh before every drive so a stale value from a previous call
   can never leak in).
2. **A stop was actually recorded** — `self._read_abort_stopped_at` is not `None`, i.e. the read
   loop's `abort_predicate` genuinely fired at least once during this run.
3. **The error id matches exactly** — `self.last_firmware_error_code == MSG_ERR_TIMEOUT` (`0xA8`).
   Any other firmware error id is a different, real fault and is never accepted as this host's own
   abort, however recently a stop was recorded.
4. **The timing is plausible** — the elapsed time since the recorded stop is within
   `READ_ABORT_ACCEPTANCE_WINDOW_S` (3.0 seconds, derived as roughly three times the firmware's own
   1-second/10 ms-polled ack wait plus wire transit at 250000 baud). A timeout arriving long after a
   stop was recorded is not this stop's consequence.

If any one of the four conditions fails, the run is treated as a genuine fault and takes the
pre-existing exit-2 path unchanged. Only when all four hold is the compare finalised with
`aborted=True` and allowed to proceed to its ordinary mismatch verdict (exit 1). Three of the four
conditions are individually proven by negative tests in
`firestarter_app/tests/test_eprom_operations.py` — a non-timeout error id, a timeout with no abort
requested (the `--full` path), and a timeout whose recorded stop timestamp predates the acceptance
window — each independently forcing the exit-2 path despite superficially resembling an abort.

## Implication for CMP-F1

CMP-F1 (the future requirement filed against this open mechanic) assumed a protocol-level abort —
new wire behaviour — would be needed to make the stop clean. That assumption no longer holds: the
ack-withholding mechanism above already achieves a clean stop with zero firmware changes, at the
cost of up to one second of firmware timeout per abort. The genuinely cheaper remaining improvement
is the deferred idea recorded in `202-CONTEXT.md`'s `<deferred>` section: teaching the firmware's
`op_wait_for_ack` to treat an in-flight `"DONE"` message as a clean stop instead of waiting out the
full timeout — `op_get_message` already parses `"DONE"` into `OP_MSG_DONE`
(`firestarter_fw/src/operation_utils.cpp:131-139`); only `op_wait_for_ack`'s handling of that case
needs to change. That is a one-line firmware change, best made in phase 204, which is already
dual-repo and bench-gated — bringing it forward into this app-only, bench-no phase would have put
firmware work where none belongs. It removes the up-to-one-second cost and the wire-identical-error
ambiguity this plan's discrimination exists to resolve, but it is an optimisation of an already-working
mechanism, not a prerequisite for it.
