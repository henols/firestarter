---
title: dev test / dev write-cycle verify connects are not port-pinned
kind: defect
created: 2026-09-21
source_phase: 203
resolves_phase: null
severity: medium
---

Phase 203's CR-01 fix (`0fc6c77`, firestarter_app) pins the guard read, the write, and
`firestarter write --verify`'s read-back to one resolved port for the invocation.

`chip_test.py`'s own `verify_eprom` calls, used by `dev test` and `dev write-cycle`, do NOT pass
`preferred_port`, so they still re-run discovery and can land on a different board than the write
they are verifying. They inherit guard+write pinning for free (that is internal to `write_eprom`),
so the unpinned leg is the verify connect only.

Lower severity than CR-01 because `dev test` is a validation command, not an operator write path,
and a wrong-board verify reports a false mismatch rather than causing an irreversible write.

Fix: thread `preferred_port=<the write's resolved port>` into `chip_test.py`'s `verify_eprom`
calls, the same way `cli_handlers.write` does via `last_write_port`.

Deliberately out of scope for 203 — that phase's authorised fix was CR-01 on the
`firestarter write` path.
