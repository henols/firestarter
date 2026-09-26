---
created: 2026-08-30T00:00:00Z
title: Gate the fingerprint read-back on step failure (two full-device reads per passing run)
area: host app
files:
  - firestarter_app/firestarter/chip_test.py (:3100 collect_fingerprint gate; :3117 classify_fingerprint call)
  - firestarter_app/tests/test_chip_test*.py (fingerprint-presence assertions)
  - .planning/notes/dev-test-sequence-cost-model.md (measurement)
  - .planning/seeds/dev-test-adaptive-sequencing.md (rule R2)
resolves_phase: 177
---

## Problem

`_dispatch_multi_run` performs a full-region read-back to build a `Fingerprint`
on the final cycle of every `write` / `write-partial` / `verify` step. The gate at
[`chip_test.py:3100`](../../../firestarter_app/firestarter/chip_test.py#L3100) is:

```python
if collect_fingerprint and op in (OP_WRITE, OP_WRITE_PARTIAL, OP_VERIFY):
```

It consults op membership and the final-cycle flag. **It never consults
`outcomes`.** So it runs identically whether the step passed or failed.

A `Fingerprint` classifies a *mismatch distribution* — bit-clustering by high
address bit for address-line faults, `ff_ratio` for contact faults, scatter plus
non-repeatability for transport faults. On a run where write and verify both
passed, the mismatch set is empty by construction and the classification carries
no information.

**Measured cost** (sst27sf512, 65536 B, from the operator's own log): two
full-device reads at 7.40s and 7.59s, out of a modelled 121.8s default run —
**~12% of the run, on every passing run**, rising with device size. See
[`dev-test-sequence-cost-model.md`](../../notes/dev-test-sequence-cost-model.md).

## The one real objection, and why it does not block this

`classify_fingerprint`'s first bucket is `blank/contact`, and its own comment
([`chip_test.py:197-199`](../../../firestarter_app/firestarter/chip_test.py#L197-L199))
says it is checked *"regardless of whether there are zero mismatches (a perfect
verify)"* — it is a **false-PASS detector**, catching a write that reported OK
without the bus ever being driven. That is a genuine concern for the write step
and must not be lost.

It is already covered without the read-back: **the verify step immediately
follows the write in the same cycle**, streams the real pattern host→device, and
the firmware compares byte-for-byte
([`memory.cpp:377-396`](../../../firestarter/src/proms/memory.cpp#L377-L396)). A
near-all-`0xFF` device cannot produce a passing verify against a generated
pattern.

For the **verify** step's own read-back the objection is weaker still: verify has
just performed an independent on-device compare of the identical buffer.

## Proposed change

Gate on outcome as well as op:

```python
if collect_fingerprint and op in (...) and not all(outcomes):
```

- Passing run: zero read-backs.
- Failing run: byte-identical behaviour to today, including every
  `Fingerprint` field, every classification bucket and the `repeat_divergent`
  input at [`chip_test.py:3117`](../../../firestarter_app/firestarter/chip_test.py#L3117).

Failing runs also get *cheaper* than they look: `memory_verify_execute` returns
on the first mismatch, so the verify that triggers the read-back is the fast one.

## Load-bearing precondition — assert it, do not assume it

The false-PASS argument above depends on **every plan that emits a write also
emitting a verify behind it**. That holds for every plan `derive_plan` produces
today (checked across sst27sf512, w27c512, at28c256, m27c512, am27c020, w29c040).

It must become a **test**, not a comment: if a future plan shape ever emits a
write with no verify following it, that plan needs the unconditional read-back
restored. A structural assertion over `derive_plan` output across the DB is the
right shape — the same style as the existing SDP-arm sentinel
`test_shipped_ops_never_reach_sdp_arm`.

## Scope boundary

Do **not** touch `_dispatch_sdp_leg`. Its `_read_region` read-back **is** the
verdict, not decoration — the length gate and the degeneracy gate both need real
bytes, and the `write-inhibited` op's whole oracle is a read-back asymmetry.
That is stated explicitly in its own comment and must stay true.

## Existing tests to expect movement in

Any test asserting a `Fingerprint` is present on a **passing** write or verify
step now asserts the opposite. Those assertions encode the current unconditional
behaviour, not a requirement — but each one should be re-read before it is
flipped, in case it is standing in for something else.
