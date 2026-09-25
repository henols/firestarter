---
created: 2026-09-24
source: .planning/milestones/v1.41-phases/207.1-address-v1-41-tech-debt/207.1-REVIEW.md § WR-02 (pre-existing since Phase 206; filed at the v1.41 milestone close)
resolves_phase:
severity: major
area: host app
---

# A lease drain failure leaves the dead link leased

`EpromOperator._setup_operation`'s leased branch calls `self.comm.consume_remaining_input()`
(`firestarter_app/firestarter/eprom_operations.py:695`) **before** the `try:` whose
`except SerialError` calls `_disconnect_programmer()` (`:696-706`).

`consume_remaining_input` reaches `_read_and_parse_lines`, which raises `SerialError` on any
`serial.SerialException` (`serial_comm.py:456-461`). A USB unplug or a stalled port produces that
exception. pyserial does not close the port on a read exception, so `is_connected()` stays True.
Every later leased step takes the same branch, drains the dead link again and fails the same way.
The rest of the `dev test` plan becomes SKIPPED instead of connecting again from cold.

This contradicts D-06 as `lease()` documents it, and T-206-12 in `206-SECURITY.md`: both state that
a `SerialError` "disconnects the link and the next operation cold-connects". The v1.41 re-audit's
integration checker reproduced it on the live tree. No test covers it, because
`test_session_lease.py`'s `_FakeComm.consume_remaining_input` never raises.

**Blast radius.** SESS-01 and the `dev test` flow, on a mid-run unplug only. No wrong verdict is
produced; the later steps are SKIPPED rather than run.

## Fix

Move the drain inside the existing handler:

```python
try:
    self.comm.consume_remaining_input()
    setup_ok = self.comm.setup_command(command_dict, self.config)
except SerialError:
    self._disconnect_programmer()
    raise
```

Add a `test_session_lease.py` leg in which `consume_remaining_input` raises `SerialError`. Assert
that `operator.comm is None` afterwards and that the next leased operation calls
`find_and_connect`.
